"""斜め視点ツール（oblique_register.py / oblique_mask.py）の共通部品。画像を生成しない。

入力JSONの形（schema `sit-oblique-input/1`）は ../tools/README.md と
docs/production/oblique-masks/TRM-02-input.json を参照。
"""
import hashlib
import json
import sys

import cv2
import numpy as np

SCHEMA_INPUT = "sit-oblique-input/1"
SCHEMA_REGISTER = "sit-oblique-register/1"
SCHEMA_RESULT = "sit-oblique-result/1"
EDGES = ("north", "south", "west", "east")


def sha256_file(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def load_input(path):
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    if d.get("schema") != SCHEMA_INPUT:
        sys.exit(f"入力JSONの schema が {SCHEMA_INPUT} ではない: {d.get('schema')}")
    ids = [r["id"] for r in d["rooms"]]
    if len(set(ids)) != len(ids):
        sys.exit("rooms の id が重複している")
    for r in d["rooms"]:
        q = r["quad"]
        if len(q) != 4:
            sys.exit(f"room {r['id']}: quad は4点（左上・右上・右下・左下の順）")
    resolve_aspects(d)
    return d


def resolve_aspects(d):
    """plan_aspect.source が `from_room:<id>` または `from_room:<id>*<ratio>` の部屋の縦横比を、別の部屋の行列から決める。

    元の部屋の行列（その部屋の縦横比で作る）へこの部屋の quad を外挿して投影し、平面上の
    幅（上下の辺の平均）÷奥行き（左右の辺の平均）× ratio を w_over_h に入れる。
    同じ高さの床が壁などで分かれていて、別々の quad で取った部屋に使う。元の部屋の縦横比は
    循環検証・独立検証のどちらかを引き継ぐ（独立検証には数えない）。元は from_room ではない部屋のみ。
    """
    rooms = {r["id"]: r for r in d["rooms"]}
    for r in d["rooms"]:
        pa = r.get("plan_aspect", {})
        src = pa.get("source", "")
        if not src.startswith("from_room:"):
            continue
        ref, _, ratio = src[len("from_room:"):].partition("*")
        ratio = float(ratio) if ratio else 1.0
        if ref not in rooms or rooms[ref].get("plan_aspect", {}).get("source", "").startswith("from_room:"):
            sys.exit(f"room {r['id']}: from_room:{ref} は存在しないか、それ自体が from_room")
        H, _, _, _ = room_homography(rooms[ref])
        q = apply_h(H, r["quad"])
        w = (np.hypot(*(q[1] - q[0])) + np.hypot(*(q[2] - q[3]))) / 2
        h = (np.hypot(*(q[3] - q[0])) + np.hypot(*(q[2] - q[1]))) / 2
        pa["w_over_h"] = round(float(w / h * ratio), 3)
        pa["derived_from"] = {"room": ref, "ratio": ratio, "plan_w": round(float(w), 1), "plan_h": round(float(h), 1)}


def geom_polygon(rooms, g):
    """bridge / carve の形 → 画像上の多角形（点列）。

    g のキー（どれか1つ）:
      plan_uv_polygon  [[u,v],...]  room の平面座標(0..1。範囲外も可＝行列の外挿)
      plan_px_polygon  [[x,y],...]  room の平面図の画素
      image_polygon    [[x,y],...]  画像の画素（最後の手段）
      line_uv          {"from":[u,v],"to":[u,v],"width_plan_px":N}  線＋幅（平面図の画素）
    """
    room = rooms[g["room"]] if g.get("room") in rooms else None
    if "image_polygon" in g:
        return np.array(g["image_polygon"], np.float64)
    if room is None:
        sys.exit(f"{g.get('id')}: room が必要（image_polygon 以外）")
    _, Hi, pw, ph = room_homography(room)
    if "plan_uv_polygon" in g:
        P = np.array([[u * pw, v * ph] for u, v in g["plan_uv_polygon"]], np.float64)
    elif "plan_px_polygon" in g:
        P = np.array(g["plan_px_polygon"], np.float64)
    elif "line_uv" in g:
        l = g["line_uv"]
        a = np.array([l["from"][0] * pw, l["from"][1] * ph]); b = np.array([l["to"][0] * pw, l["to"][1] * ph])
        t = b - a; n = np.array([-t[1], t[0]]) / (np.hypot(*t) or 1.0) * float(l["width_plan_px"]) / 2
        P = np.array([a + n, b + n, b - n, a - n])
    else:
        sys.exit(f"{g.get('id')}: plan_uv_polygon / plan_px_polygon / image_polygon / line_uv のどれかが要る")
    return apply_h(Hi, P)


def plan_size(room):
    """平面図の画素寸法。plan_aspect.w_over_h と plan_width から決める（決定的に丸める）。"""
    w = int(room.get("plan_width", 1600))
    a = float(room["plan_aspect"]["w_over_h"])
    return w, int(round(w / a))


def room_homography(room):
    """画像 → 平面図（0..PW, 0..PH）。quad の順は 左上・右上・右下・左下。"""
    pw, ph = plan_size(room)
    src = np.float32(room["quad"])
    dst = np.float32([[0, 0], [pw, 0], [pw, ph], [0, ph]])
    H = cv2.getPerspectiveTransform(src, dst)
    return H, np.linalg.inv(H), pw, ph


def apply_h(H, pts):
    p = np.asarray(pts, np.float64).reshape(-1, 2)
    q = np.c_[p, np.ones(len(p))] @ H.T
    return q[:, :2] / q[:, 2:3]


def uv_to_img(room, u, v):
    """平面座標 (u,v)=0..1 → 絵の画素。"""
    _, Hi, pw, ph = room_homography(room)
    return apply_h(Hi, [[u * pw, v * ph]])[0]


def img_to_uv(room, x, y):
    H, _, pw, ph = room_homography(room)
    p = apply_h(H, [[x, y]])[0]
    return p[0] / pw, p[1] / ph


def read_image(path):
    im = cv2.imread(path, cv2.IMREAD_COLOR)
    if im is None:
        sys.exit(f"画像を読めない: {path}")
    return im


def poly_mask(shape, polygon):
    m = np.zeros(shape[:2], np.uint8)
    cv2.fillPoly(m, [np.int32(np.round(polygon))], 1)
    return m.astype(bool)


def jdump(obj, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=1, ensure_ascii=False, sort_keys=False)
        f.write("\n")


def table(rows, header):
    """要点の表（等幅）。rows は文字列タプルのリスト。"""
    cols = list(zip(*([header] + rows)))
    wid = [max(len(str(c)) + sum(1 for ch in str(c) if ord(ch) > 255) for c in col) for col in cols]
    def fmt(r):
        return "  ".join(
            str(c) + " " * (w - len(str(c)) - sum(1 for ch in str(c) if ord(ch) > 255)) for c, w in zip(r, wid)
        ).rstrip()
    out = [fmt(header), fmt(["-" * w for w in wid])]
    out += [fmt(r) for r in rows]
    return "\n".join(out)
