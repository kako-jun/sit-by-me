#!/usr/bin/env python3
"""E2 測定: クリーンモック編集元の imagegen 生成物が、モックの幾何をどれだけ保つか（決定論・画像認識なし）。

使い方（リポ直下で）:
  uv run --with numpy --with opencv-python-headless --with pillow python3 -I \
    .claude/skills/sit-field-background/tools/oblique_e2_measure.py MAP [--round e2] [--takes 4] [--files a.png b.png ...]

入力: docs/production/oblique-mocks/<MAP>/<MAP>-clean.png（編集元）、<MAP>-plan.json、<round>/take1..N.png
出力（<round>/）: metrics.json, metrics.md, overlay-takeN.png（モックの輪郭=赤を生成画像に重ねたもの）
測るもの:
  (a) モックの輪郭（Canny）に対する生成画像の輪郭の一致: recall@6px・Chamfer（モック→生成）・ずらし基準（+30,+20px）との差
  (b) 領域ごと（戸口・窓・家具・舞台）の輪郭帯が、生成画像の輪郭の上に乗る位置ずれ（±40px 探索の最良 dx,dy）
      ＋ 戸口のピンク残り・窓ガラス内の白/緑の割合・床の模様量
  (c) テイク間: 輪郭のペアごとの Chamfer・領域ずれの標準偏差
  (d) 本物確認: sha256 が codex generated_images の新規ファイルと一致するか・色数・ログ中の偽造ツール使用
  (e) 装飾量と層構造（--ref に元の採用画像を渡したとき。git:REV:PATH 可）: 領域（壁・床・家具・作業机・台座の前縁・建物の外）ごとの
      エッジ密度・色エントロピーの対元画像比、層の平均色（Lab ΔE）と層の分離、建物の外の木（常緑樹・枯木の塊）・草の量と四辺への分布、白いのっぺり面の割合
合否基準は GATES / DECOR_GATES（先に決めた値）。画像の内容は人が見る項目（HUMAN_ITEMS）として別掲する。
"""
import argparse, glob, hashlib, itertools, json, os, re, sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import oblique_mock as om  # noqa: E402

GATES = {
    "edge_recall_room_min": 0.60,      # モック輪郭の 6px 以内に生成輪郭がある割合（室内）
    "edge_margin_min": 0.15,           # 上の値 − ずらし基準での値（偶然一致でない証拠）
    "chamfer_room_max_px": 6.0,        # モック輪郭→最寄り生成輪郭の平均距離（室内）
    "region_shift_max_px": 8,          # 領域の輪郭帯が最良になる平行移動の |dx|,|dy|
    "region_ok_ratio_min": 0.70,       # 自己照合（モック自身）で 0.87（椅子の小箱が隣と取り違えられる）       # 上を満たす領域の割合
    "door_pink_residual_max": 0.02,    # 戸口パネル内のピンク残り
    "window_white_green_max": 0.05,    # 窓ガラス内の 白（空・雪）/緑（木）の割合
    "aspect_tol": 0.005,
}
# 装飾量・層構造のゲート（E2 round2 の生成前に決定。元の採用画像=ref に対する比）
DECOR_GATES = {
    "density_ratio_min": 0.60,         # 領域のエッジ密度・色エントロピーが ref の 60% 以上（モックは単色で≈0）
    "layer_color_dE_max": 30.0,        # 層（作業机・台座の前縁・建物の外・室内の床）の平均色が ref から Lab ΔE76 で 30 以内
    "layer_sep_ratio_min": 0.60,       # 作業机と建物の外の色差が ref の 60% 以上（層が混ざらない）
    "outside_flat_white_max": 0.15,    # 建物の外で「明るく平坦な白」（白い素地）の割合の上限
    "outside_tree_blobs_min": 6,       # 建物の外の木（常緑樹・枯木）の塊の数
    "outside_tree_sides_min": 3,       # 木が奥・手前・左・右のうち何辺にあるか
    "outside_evergreen_ratio_min": 0.30, "outside_branch_ratio_min": 0.30, "outside_grass_ratio_min": 0.20,
}
ROUND2_IF_PASS_LT = 2  # 合格テイクがこの数未満なら追加ラウンド

HUMAN_ITEMS = [
    "窓の外に雪・木・空が描かれていないか（測定は窓ガラス内の白/緑の割合のみ。ガラス越しが室内の床に見えるかは目視）",
    "床の模様の質（板張りに見えるか・不自然な模様がないか。測定は輝度の標準偏差のみ）",
    "壁の見え方（厚み・材質・上端）と、戸口が木の扉/開口として自然か（ピンク残りは測定、造形は目視）",
    "家具が実物（棚・椅子・机・舞台）として読めるか。人物・文字・矢印が入っていないか（文字有無は未測定）",
    "段ボールの土台・雪・木の質感の様式（手作りミニチュアらしさ）",
]


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def load(p, size):
    im = Image.open(p).convert("RGB")
    resized = im.size != size
    if resized:
        im = im.resize(size, Image.LANCZOS)
    return np.array(im), resized


def edges_gen(rgb):
    g = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    g = cv2.GaussianBlur(g, (0, 0), 1.6)
    gx = cv2.Sobel(g, cv2.CV_32F, 1, 0)
    gy = cv2.Sobel(g, cv2.CV_32F, 0, 1)
    mag = np.hypot(gx, gy)
    hi = float(np.percentile(mag, 92))
    return cv2.Canny(g, hi * 0.4, hi * 0.9) > 0


def dist_to(e):
    return cv2.distanceTransform((~e).astype(np.uint8), cv2.DIST_L2, 3)


def poly_mask(polys, size):
    m = np.zeros((size[1], size[0]), np.uint8)
    for q in polys:
        cv2.fillPoly(m, [np.round(np.array(q)).astype(np.int32)], 1)
    return m > 0


def regions(plan, size):
    R = {}
    for d in plan["doors"]:
        _, panel, _ = om.door_geom(plan, d)
        R[("door", d["id"])] = poly_mask([panel], size)
    for i, w in enumerate(plan.get("windows", [])):
        R[("window", w.get("id", f"win{i}"))] = poly_mask([om.window_geom(plan, w)], size)
    for b in plan["boxes"]:
        polys = [q for q, _, _ in om.box_polys(b["rect"], b["h"], b["color"])]
        R[("box", b["id"])] = poly_mask(polys, size)
    floors = [poly_mask([om.rect_poly(f["rect"])], size) for f in plan["floors"]]
    fl = np.zeros_like(floors[0])
    for f in floors:
        fl |= f
    return R, fl


def band(mask, w=3):
    k = np.ones((2 * w + 1, 2 * w + 1), np.uint8)
    return (cv2.dilate(mask.astype(np.uint8), k) - cv2.erode(mask.astype(np.uint8), k)) > 0


def best_shift(bnd, dg, rng=40):
    ys, xs = np.nonzero(bnd)
    if len(ys) == 0:
        return None
    h, w = dg.shape
    sc = np.exp(-dg / 3.0)
    best = (-1, 0, 0)
    s0 = None
    for dy in range(-rng, rng + 1, 2):
        for dx in range(-rng, rng + 1, 2):
            yy, xx = ys + dy, xs + dx
            ok = (yy >= 0) & (yy < h) & (xx >= 0) & (xx < w)
            if ok.sum() < 0.8 * len(ys):
                continue
            v = float(sc[yy[ok], xx[ok]].mean())
            if dx == 0 and dy == 0:
                s0 = v
            if v > best[0] + 1e-9 or (abs(v - best[0]) < 1e-9 and abs(dx) + abs(dy) < abs(best[1]) + abs(best[2])):
                best = (v, dx, dy)
    return {"best_score": round(best[0], 3), "dx": best[1], "dy": best[2], "score_at_0": round(s0 or 0, 3)}


def glass_stats(rgb, mask):
    k = np.ones((9, 9), np.uint8)
    inner = cv2.erode(mask.astype(np.uint8), k) > 0
    if inner.sum() < 50:
        inner = mask
    px = rgb[inner].astype(np.float32)
    mx, mn = px.max(1), px.min(1)
    white = (mn > 215) & ((mx - mn) < 0.15 * mx + 1)
    green = (px[:, 1] > px[:, 0] + 15) & (px[:, 1] > px[:, 2] + 15)
    return {"mean_rgb": [round(float(v), 1) for v in px.mean(0)], "white": round(float(white.mean()), 3), "green": round(float(green.mean()), 3), "px": int(inner.sum())}


def pink_frac(rgb, mask):
    px = rgb[mask].astype(np.int32)
    pink = (px[:, 0] > 200) & (px[:, 1] < 130) & (px[:, 2] > 110) & (px[:, 0] - px[:, 1] > 100)
    return round(float(pink.mean()), 4) if len(px) else 0.0


# ---------------------------------------------------------------- 装飾量・層構造（元の採用画像との比）
def layer_masks(plan, size, R, floor, room):
    W, H = size
    tl, tr, br, bl = [tuple(map(float, q)) for q in om._DST]
    top = poly_mask([[tl, tr, br, bl]], size)
    front = poly_mask([[bl, br, (br[0], br[1] + om.SLAB), (bl[0], bl[1] + om.SLAB)]], size)
    k = lambda m, n: cv2.erode(m.astype(np.uint8), np.ones((n, n), np.uint8)) > 0  # noqa: E731
    boxes = np.zeros((H, W), bool)
    for (kind, _), m in R.items():
        if kind == "box":
            boxes |= m
    other = np.zeros((H, W), bool)
    for (kind, _), m in R.items():
        if kind in ("door", "window"):
            other |= m
    hull = cv2.dilate(room.astype(np.uint8), np.ones((11, 11), np.uint8)) > 0
    fcol = plan["floors"][0].get("color", "#8f6a43").lstrip("#")
    return {
        "desk": k(~(top | front), 9),
        "slab_front": k(front, 7),
        "outside": k(top & ~hull, 9),
        "floor": k(floor & ~boxes & ~other, 7),
        "wall": k(room & ~floor & ~boxes & ~other, 5),
        "objects": k(boxes, 5),
    }, hull


def region_stats(rgb, m, ge):
    px = rgb[m]
    q = (px >> 4).astype(np.int32)
    idx = q[:, 0] * 256 + q[:, 1] * 16 + q[:, 2]
    h = np.bincount(idx, minlength=4096).astype(np.float64)
    h = h[h > 0] / h.sum()
    ent = float(-(h * np.log2(h)).sum())
    lab = cv2.cvtColor((rgb.astype(np.float32) / 255.0), cv2.COLOR_RGB2LAB)[m].mean(0)
    return {"edge_density": round(float(ge[m].mean()), 4), "color_entropy": round(ent, 3), "lab": [round(float(v), 1) for v in lab], "px": int(m.sum())}


def outside_objects(rgb, m, hull_box):
    f = rgb.astype(np.int32)
    lum = (0.299 * f[..., 0] + 0.587 * f[..., 1] + 0.114 * f[..., 2])
    r, g, b = f[..., 0], f[..., 1], f[..., 2]
    green = (g > r + 6) & (g > b + 6) & (lum < 115) & m
    branch = (r > g + 8) & (g > b + 5) & (lum < 120) & (r < 150) & m
    grass = (g > b + 25) & (r > b + 20) & (lum > 70) & (lum < 190) & ~green & m
    tree = (green | branch).astype(np.uint8)
    tree = cv2.morphologyEx(tree, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
    n, lab, st, cen = cv2.connectedComponentsWithStats(tree)
    x0, y0, x1, y1 = hull_box
    sides, blobs = set(), 0
    for i in range(1, n):
        if st[i, cv2.CC_STAT_AREA] < 200:
            continue
        blobs += 1
        cx, cy = cen[i]
        if cy < y0: sides.add("N")
        elif cy > y1: sides.add("S")
        elif cx < x0: sides.add("W")
        elif cx > x1: sides.add("E")
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY).astype(np.float32)
    mean = cv2.blur(gray, (7, 7)); sq = cv2.blur(gray * gray, (7, 7))
    sd = np.sqrt(np.maximum(sq - mean * mean, 0))
    flat_white = (lum > 225) & (sd < 1.5) & m
    a = float(m.sum())
    return {"evergreen_frac": round(float(green.sum() / a), 4), "branch_frac": round(float(branch.sum() / a), 4), "grass_frac": round(float(grass.sum() / a), 4),
            "tree_blobs": blobs, "tree_sides": sorted(sides), "flat_white_frac": round(float(flat_white.sum() / a), 4)}


def decor_eval(rgb, ge, masks, hull_box, ref):
    d = {"regions": {k: region_stats(rgb, m, ge) for k, m in masks.items()}, "outside_objects": outside_objects(rgb, masks["outside"], hull_box)}
    G = DECOR_GATES
    g = {}
    for k, v in d["regions"].items():
        rv = ref["regions"][k]
        d["regions"][k]["edge_ratio_vs_ref"] = round(v["edge_density"] / max(rv["edge_density"], 1e-6), 2)
        d["regions"][k]["entropy_ratio_vs_ref"] = round(v["color_entropy"] / max(rv["color_entropy"], 1e-6), 2)
        g[f"density:{k}"] = d["regions"][k]["edge_ratio_vs_ref"] >= G["density_ratio_min"] and d["regions"][k]["entropy_ratio_vs_ref"] >= G["density_ratio_min"]
    dE = lambda a, b: float(np.linalg.norm(np.array(a) - np.array(b)))  # noqa: E731
    for k in ("desk", "slab_front", "outside", "floor"):
        d["regions"][k]["dE_vs_ref"] = round(dE(d["regions"][k]["lab"], ref["regions"][k]["lab"]), 1)
        g[f"layer_color:{k}"] = d["regions"][k]["dE_vs_ref"] <= G["layer_color_dE_max"]
    sep = dE(d["regions"]["desk"]["lab"], d["regions"]["outside"]["lab"])
    rsep = dE(ref["regions"]["desk"]["lab"], ref["regions"]["outside"]["lab"])
    d["layer_sep_desk_outside"] = round(sep, 1); d["layer_sep_ratio_vs_ref"] = round(sep / max(rsep, 1e-6), 2)
    g["layer_separation"] = d["layer_sep_ratio_vs_ref"] >= G["layer_sep_ratio_min"]
    o, ro = d["outside_objects"], ref["outside_objects"]
    g["outside_flat_white"] = o["flat_white_frac"] <= G["outside_flat_white_max"]
    g["outside_trees"] = o["tree_blobs"] >= G["outside_tree_blobs_min"] and len(o["tree_sides"]) >= G["outside_tree_sides_min"]
    g["outside_evergreen"] = o["evergreen_frac"] >= G["outside_evergreen_ratio_min"] * ro["evergreen_frac"]
    g["outside_branch"] = o["branch_frac"] >= G["outside_branch_ratio_min"] * ro["branch_frac"]
    g["outside_grass"] = o["grass_frac"] >= G["outside_grass_ratio_min"] * ro["grass_frac"]
    return d, g


def provenance(path, out_dir, n):
    r = {"sha256": sha(path), "bytes": os.path.getsize(path)}
    im = Image.open(path)
    r["size"] = list(im.size); r["mode"] = im.mode
    a = np.array(im.convert("RGB")).reshape(-1, 3)
    r["unique_colors"] = int(len(np.unique(a[:: max(1, len(a) // 400000)], axis=0)))
    gi = Path.home() / ".codex" / "generated_images"
    before = out_dir / ".gi-before.txt"
    r["matches_codex_generated_image"] = None
    if gi.exists():
        old = set(before.read_text().split()) if before.exists() else set()
        cands = [p for p in gi.rglob("*") if p.is_file() and p.suffix.lower() in (".png", ".webp", ".jpg") and p.relative_to(gi).parts[0] not in old]
        hit = [str(p) for p in cands if p.stat().st_size == r["bytes"] and sha(p) == r["sha256"]]
        r["matches_codex_generated_image"] = hit[0] if hit else False
        r["new_generated_images_in_run"] = len(cands)
    log = out_dir / f"codex-take{n}.log"
    if not log.exists():
        log = out_dir / f"codex-take{n}.log.txt"  # 整形済み（先頭のみ）
    if log.exists():
        t = log.read_text(errors="replace")
        r["log_mentions_unavailable"] = "IMAGE_GEN_TOOL_UNAVAILABLE" in t
        r["log_fabrication_tool_calls"] = len(re.findall(r"\b(magick|convert|composite)\b .*\.png|from PIL|import numpy", t))
        r["log_mentions_image_gen"] = bool(re.search(r"image_gen|imagegen", t))
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("map_id")
    ap.add_argument("--round", default="e2")
    ap.add_argument("--takes", type=int, default=4)
    ap.add_argument("--files", nargs="*")
    ap.add_argument("--root", default=None)
    ap.add_argument("--ref", default=None, help="元の採用画像（装飾量・層の基準）。ファイル、または git:REV:PATH")
    a = ap.parse_args()
    root = Path(a.root or os.popen("git rev-parse --show-toplevel").read().strip())
    M = root / "docs/production/oblique-mocks"
    out = M / a.map_id / a.round
    mock_p = M / a.map_id / f"{a.map_id}-clean.png"
    plan = om.load_plan(str(M / f"{a.map_id}-plan.json"))
    mock = np.array(Image.open(mock_p).convert("RGB"))
    H, W = mock.shape[:2]
    size = (W, H)
    me = cv2.Canny(cv2.cvtColor(mock, cv2.COLOR_RGB2GRAY), 40, 120) > 0
    R, floor = regions(plan, size)
    room = np.zeros((H, W), bool)
    xs = [q for k, m in R.items() for q in [m]]
    wall_polys = []
    for w in plan["walls"]:
        wall_polys += [om.rect_poly(w["rect"]), om.rect_poly(w["rect"], w["h"])]
    room = cv2.dilate(poly_mask(wall_polys, size).astype(np.uint8), np.ones((31, 31), np.uint8)) > 0
    # 壁の外周を含む凸包でなく、床＋壁の凸包
    pts = np.round(np.array([p for q in wall_polys for p in q])).astype(np.int32)
    room = np.zeros((H, W), np.uint8)
    cv2.fillConvexPoly(room, cv2.convexHull(pts), 1)
    room = room > 0
    me_room = me & room
    ref = None
    if a.ref:
        if a.ref.startswith("git:"):
            import io, subprocess
            blob = subprocess.check_output(["git", "-C", str(root), "show", a.ref[4:]])
            refrgb = np.array(Image.open(io.BytesIO(blob)).convert("RGB").resize(size, Image.LANCZOS))
        else:
            refrgb = np.array(Image.open(a.ref).convert("RGB").resize(size, Image.LANCZOS))
        dmasks, _hull = layer_masks(plan, size, R, floor, room)
        ys_, xs2 = np.nonzero(room)
        hull_box = (int(xs2.min()), int(ys_.min()), int(xs2.max()), int(ys_.max()))
        ref = {"regions": {k: region_stats(refrgb, m, edges_gen(refrgb)) for k, m in dmasks.items()}, "outside_objects": outside_objects(refrgb, dmasks["outside"], hull_box), "edges": edges_gen(refrgb)}
    # 自己較正: モック自身の輪郭で同じ領域ずれ探索をし、自分自身でもずれる領域（隣の同形状と取り違える椅子・細い戸口など）は
    # 測定不能（unreliable）として領域ずれの合否から除く（生成画像のせいにしない）
    dmock = dist_to(edges_gen(mock))
    unreliable = set()
    for (kind, rid), m in R.items():
        s0 = best_shift(band(m) & (cv2.dilate(me.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0), dmock)
        if (not s0) or abs(s0["dx"]) > GATES["region_shift_max_px"] or abs(s0["dy"]) > GATES["region_shift_max_px"]:
            unreliable.add(f"{kind}:{rid}")
    files = a.files or [str(out / f"take{i}.png") for i in range(1, a.takes + 1)]
    files = [f for f in files if os.path.exists(f)]
    res, gens = [], []
    for f in files:
        n = re.findall(r"take(\d+)", f)
        n = n[-1] if n else "?"
        rgb, resized = load(f, size)
        im0 = Image.open(f)
        ge = edges_gen(rgb)
        dg = dist_to(ge)
        ys, xs_ = np.nonzero(me_room)
        d = dg[ys, xs_]
        recall = float((d <= 6).mean())
        sh = np.roll(np.roll(ge, 20, 0), 30, 1)
        recall_sh = float((dist_to(sh)[ys, xs_] <= 6).mean())
        r = {"take": n, "file": f, "resized_for_measure": resized, "orig_size": list(im0.size),
             "aspect_ok": abs(im0.size[0] / im0.size[1] - W / H) < GATES["aspect_tol"] * W / H}
        r["edge"] = {"recall6_room": round(recall, 3), "recall6_shifted_baseline": round(recall_sh, 3),
                     "margin": round(recall - recall_sh, 3), "chamfer_room_px": round(float(d.mean()), 2),
                     "recall6_full": round(float((dg[me] <= 6).mean()), 3), "gen_edge_density_room": round(float(ge[room].mean()), 4)}
        reg = {}
        for (kind, rid), m in R.items():
            # モックで実際に輪郭になっている所（壁に隠れた辺・同色の境は除く）だけを帯として使う
            s = best_shift(band(m) & (cv2.dilate(me.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0), dg)
            ent = {"shift": s}
            if kind == "window":
                ent["glass"] = glass_stats(rgb, m)
            if kind == "door":
                ent["pink_residual"] = pink_frac(rgb, m)
            reg[f"{kind}:{rid}"] = ent
        r["regions"] = reg
        fl = floor & ~np.any([m for (k, _), m in R.items() if k == "box"], axis=0)
        lum = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY).astype(np.float32)
        fm = cv2.erode(fl.astype(np.uint8), np.ones((15, 15), np.uint8)) > 0
        r["floor"] = {"lum_std": round(float(lum[fm].std()), 2), "mean_rgb": [round(float(v), 1) for v in rgb[fm].mean(0)],
                      "mock_mean_rgb": [round(float(v), 1) for v in mock[fm].mean(0)]}
        r["pink_residual_whole_image"] = pink_frac(rgb, np.ones((H, W), bool))
        r["provenance"] = provenance(f, out, n)
        # ゲート
        for k in reg:
            reg[k]["unreliable_self_check"] = k in unreliable
        shifts = [v["shift"] for k, v in reg.items() if v["shift"] and k not in unreliable]
        sx = [s["dx"] for s in shifts]; sy = [s["dy"] for s in shifts]
        r["global_shift_median_px"] = [float(np.median(sx)) if sx else None, float(np.median(sy)) if sy else None]
        ok = [abs(s["dx"]) <= GATES["region_shift_max_px"] and abs(s["dy"]) <= GATES["region_shift_max_px"] for s in shifts]
        r["region_ok_ratio"] = round(sum(ok) / max(1, len(ok)), 3)
        gl = [v["glass"] for v in reg.values() if "glass" in v]
        pk = [v["pink_residual"] for v in reg.values() if "pink_residual" in v]
        g = {
            "aspect": r["aspect_ok"],
            "edge_recall": r["edge"]["recall6_room"] >= GATES["edge_recall_room_min"],
            "edge_margin": r["edge"]["margin"] >= GATES["edge_margin_min"],
            "chamfer": r["edge"]["chamfer_room_px"] <= GATES["chamfer_room_max_px"],
            "regions": r["region_ok_ratio"] >= GATES["region_ok_ratio_min"],
            "door_pink": all(x <= GATES["door_pink_residual_max"] for x in pk),
            "window_content": all(x["white"] <= GATES["window_white_green_max"] and x["green"] <= GATES["window_white_green_max"] for x in gl),
            "genuine": bool(r["provenance"].get("matches_codex_generated_image")) and r["provenance"]["unique_colors"] > 5000 and r["provenance"].get("log_fabrication_tool_calls", 0) == 0,
        }
        r["gates"] = g
        r["pass"] = all(g.values())
        if ref:
            r["decor"], r["decor_gates"] = decor_eval(rgb, ge, dmasks, hull_box, ref)
            # 元画像の構図コピー検出: 生成輪郭が『モック』と『元画像』のどちらに近いか（室内。小さい方に寄っている）
            yy, xx = np.nonzero(ref["edges"] & room)
            r["decor"]["chamfer_to_ref_edges_px"] = round(float(dg[yy, xx].mean()), 2)
            r["decor"]["chamfer_to_mock_edges_px"] = r["edge"]["chamfer_room_px"]
            r["decor"]["composition_copy_suspect"] = r["decor"]["chamfer_to_ref_edges_px"] < r["decor"]["chamfer_to_mock_edges_px"]
            r["pass_decor"] = all(r["decor_gates"].values())
            r["pass_all"] = r["pass"] and r["pass_decor"]
        res.append(r)
        gens.append((n, rgb, ge, dg))
        ov = rgb.copy()
        ov[cv2.dilate(me.astype(np.uint8), np.ones((2, 2), np.uint8)) > 0] = (255, 0, 0)
        Image.fromarray(ov).save(out / f"overlay-take{n}.png")
    # テイク間
    inter = {}
    if len(gens) >= 2:
        pc = []
        for (na, _, ea, da), (nb, _, eb, db) in itertools.combinations(gens, 2):
            ya, xa = np.nonzero(ea & room)
            yb, xb = np.nonzero(eb & room)
            ca = float(0.5 * (db[ya, xa].mean() + da[yb, xb].mean()))
            pc.append({"pair": f"{na}-{nb}", "sym_chamfer_room_px": round(ca, 2)})
        inter["pairwise_chamfer"] = pc
        inter["mean_pairwise_chamfer_px"] = round(float(np.mean([p["sym_chamfer_room_px"] for p in pc])), 2)
        stack = np.stack([cv2.GaussianBlur(cv2.cvtColor(g[1], cv2.COLOR_RGB2GRAY), (0, 0), 4).astype(np.float32) for g in gens])
        inter["blurred_lum_pixel_std_room_mean"] = round(float(stack.std(0)[room].mean()), 2)
        keys = res[0]["regions"].keys()
        sd = {}
        for k in keys:
            dxs = [r["regions"][k]["shift"]["dx"] for r in res if r["regions"][k]["shift"]]
            dys = [r["regions"][k]["shift"]["dy"] for r in res if r["regions"][k]["shift"]]
            if dxs:
                sd[k] = {"dx_sd": round(float(np.std(dxs)), 1), "dy_sd": round(float(np.std(dys)), 1)}
        inter["region_shift_sd"] = sd
        inter["region_shift_sd_mean_px"] = round(float(np.mean([v["dx_sd"] + v["dy_sd"] for v in sd.values()]) / 2), 2) if sd else None
    summary = {"map": a.map_id, "round": a.round, "gates": GATES, "takes_measured": len(res), "unreliable_regions": sorted(unreliable),
               "takes_pass": [r["take"] for r in res if r["pass"]],
               "ref": a.ref, "ref_stats": {k: v for k, v in (ref or {}).items() if k != "edges"}, "takes_pass_decor": [r["take"] for r in res if r.get("pass_decor")], "takes_pass_all": [r["take"] for r in res if r.get("pass_all")],
               "decor_gates": DECOR_GATES if ref else None,
               "round2_needed": sum(r["pass"] for r in res) < ROUND2_IF_PASS_LT,
               "human_items": HUMAN_ITEMS, "takes": res, "inter_take": inter}
    (out / "metrics.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1))
    L = [f"# E2 測定 {a.map_id} {a.round}", "", "ゲート: " + json.dumps(GATES, ensure_ascii=False), ""]
    L += ["| take | PASS | recall6 | margin | chamfer | region_ok | 失敗ゲート | 本物 |", "|---|---|---|---|---|---|---|---|"]
    for r in res:
        bad = [k for k, v in r["gates"].items() if not v]
        L.append(f"| {r['take']} | {'PASS' if r['pass'] else 'FAIL'} | {r['edge']['recall6_room']} | {r['edge']['margin']} | {r['edge']['chamfer_room_px']} | {r['region_ok_ratio']} | {','.join(bad) or '-'} | {r['provenance'].get('matches_codex_generated_image') not in (None, False)} |")
    if ref:
        L += ["", "## 装飾量・層構造（元の採用画像=ref との比）", "", "DECOR_GATES: " + json.dumps(DECOR_GATES, ensure_ascii=False), "",
              "| take | PASS(装飾) | PASS(幾何+装飾) | 失敗ゲート | 層の分離比 | 外: 木の塊/辺 | 常緑/枝/草 (frac) | 平坦白 |", "|---|---|---|---|---|---|---|---|"]
        for r in res:
            bad = [k for k, v in r["decor_gates"].items() if not v]
            o = r["decor"]["outside_objects"]
            L.append(f"| {r['take']} | {'PASS' if r['pass_decor'] else 'FAIL'} | {'PASS' if r['pass_all'] else 'FAIL'} | {','.join(bad) or '-'} | {r['decor']['layer_sep_ratio_vs_ref']} | {o['tree_blobs']}/{''.join(o['tree_sides'])} | {o['evergreen_frac']}/{o['branch_frac']}/{o['grass_frac']} | {o['flat_white_frac']} |")
        ro = ref["outside_objects"]
        L.append(f"| ref | - | - | - | 1.0 | {ro['tree_blobs']}/{''.join(ro['tree_sides'])} | {ro['evergreen_frac']}/{ro['branch_frac']}/{ro['grass_frac']} | {ro['flat_white_frac']} |")
        L += ["", "領域ごとの エッジ密度比 / 色エントロピー比 / 平均色ΔE（対 ref）", "", "| region | " + " | ".join(f"take{r['take']}" for r in res) + " | ref(エッジ密度,エントロピー) |", "|---|" + "---|" * (len(res) + 1)]
        for k in ref["regions"]:
            L.append(f"| {k} | " + " | ".join(f"{r['decor']['regions'][k]['edge_ratio_vs_ref']} / {r['decor']['regions'][k]['entropy_ratio_vs_ref']}" + (f" / dE{r['decor']['regions'][k]['dE_vs_ref']}" if 'dE_vs_ref' in r['decor']['regions'][k] else "") for r in res) + f" | {ref['regions'][k]['edge_density']}, {ref['regions'][k]['color_entropy']} |")
    L += ["", "## 領域ごとの最良ずれ (dx,dy) px", "", "| region | " + " | ".join(f"take{r['take']}" for r in res) + " |", "|---|" + "---|" * len(res)]
    for k in (res[0]["regions"] if res else []):
        L.append(f"| {k}{' (測定不能)' if k in unreliable else ''} | " + " | ".join(f"({r['regions'][k]['shift']['dx']},{r['regions'][k]['shift']['dy']})" if r["regions"][k]["shift"] else "-" for r in res) + " |")
    L += ["", "## 窓ガラス内 white/green・戸口ピンク残り", ""]
    for r in res:
        parts = []
        for k, v in r["regions"].items():
            if "glass" in v:
                parts.append(f"{k} w{v['glass']['white']}/g{v['glass']['green']}")
            if "pink_residual" in v:
                parts.append(f"{k} pink{v['pink_residual']}")
        L.append(f"- take{r['take']}: " + "; ".join(parts) + f"; 床lum_std {r['floor']['lum_std']}; 全体ピンク残り {r['pink_residual_whole_image']}")
    L += ["", "## テイク間", "", "```", json.dumps(inter, ensure_ascii=False, indent=1)[:3000], "```", "",
          f"合格テイク（幾何）: {summary['takes_pass']} / 合格（装飾）: {summary['takes_pass_decor']} / 合格（幾何+装飾）: {summary['takes_pass_all']} / 追加ラウンド: {'要' if summary['round2_needed'] else '不要'}", "", "## kako-jun の目視確認項目", ""]
    L += [f"- {h}" for h in HUMAN_ITEMS]
    (out / "metrics.md").write_text("\n".join(L) + "\n")
    print("\n".join(L[:40 + 3 * len(res)]))
    print(f"wrote {out}/metrics.json, metrics.md, overlay-take*.png")


if __name__ == "__main__":
    main()
