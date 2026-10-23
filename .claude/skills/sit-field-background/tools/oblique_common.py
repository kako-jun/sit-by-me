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
    return d


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
