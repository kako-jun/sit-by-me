#!/usr/bin/env python3
"""体内 BDY-xx の生成画像を、期待幾何（清書図）と実測で突き合わせる共通チェッカー。画像生成はしない。

実行:
  uv run --with pillow --with numpy --with scipy python3 -I check_body_image.py BDY-03 generated.png \
      [--edit-source v2.png] [--out DIR] [--expect-red 6] [--json]

期待幾何: verification/body-layout/clean/BDY-xx.png（body_layout.py --clean の出力。色定義は body_layout.py から読む）。
入力画像は 1920x1080 または 1672x941（倍率 = 幅/1920 を自動判定）。

床色は画像から推定（固定値なし）。床IoUは body_floor_overlay.py と共通定義。色は「床・地形の地色」と「装飾の色域」を別項目で測る。赤紙は模型の中の枚数と模型の外の赤を別項目で測る。
判定は幾何・色の機械実測のみ。美観・グロの判断はしない（人間／レビュー担当が見る）。
色の絶対値でなく構造で測る: 机・縁取り・波形の4層（外周から内側へ）、通路は縁取りの内側に接する床の区間、広間の壁は床の途切れ方位。
"""
import argparse
import ast
import json
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
LAYOUT_PY = HERE / "body_layout.py"
OK_SIZES = {(1920, 1080), (1672, 941)}

# 床の目安色（BDY-02 の旧採用画像（現在は新版に差し替え）で較正: 約 237,197,163）
FLOOR_REF = np.array([233.0, 196.0, 164.0])

# 期待（body_layout.py と同じ値。読めたら上書きする）
DESK_M, BAND = 90, 48
PASSAGE_POS_TOL = 25   # px (1920基準)
PASSAGE_W_TOL = 0.10   # 幅 ±10%
ROPE_PAD = 7       # 床の縁取り(麻縄・段ボール)の半幅(1920基準 px)。実測の床幅は縄の内側までなので両側に足して比較
PROBE_IN = 40          # 縁から内側のプローブ距離 (1920基準)
WALL_T = 22

ORDER = {"PASS": 0, "WARN": 1, "FAIL": 2}


def load_layout_consts():
    """body_layout.py の定数を import せず ast で読む（実行副作用を避ける）。"""
    consts = {}
    try:
        tree = ast.parse(LAYOUT_PY.read_text(encoding="utf-8"))
        for n in tree.body:
            if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name):
                try:
                    consts[n.targets[0].id] = ast.literal_eval(n.value)
                except Exception:
                    pass
            elif (isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Tuple)
                  and isinstance(n.value, ast.Tuple)):   # BAND_FOAM, BAND_CORR = 28, 20
                try:
                    for tg, vl in zip(n.targets[0].elts, n.value.elts):
                        consts[tg.id] = ast.literal_eval(vl)
                except Exception:
                    pass
    except Exception:
        pass
    return consts


C = load_layout_consts()
CL_FLOOR = tuple(C.get("FLOOR", (232, 201, 168)))
CL_TERRAIN = tuple(C.get("CLEAN_TERRAIN", (170, 130, 110)))
CL_DESK = tuple(C.get("CLEAN_DESK", (118, 120, 126)))
CL_BAND = tuple(C.get("CLEAN_BAND", (150, 110, 62)))
CL_WALL = tuple(C.get("CLEAN_WALL", (92, 104, 128)))
DESK_M = C.get("DESK_M", DESK_M)
WALL_T = C.get("WALL_T", WALL_T)
BAND_FOAM = C.get("BAND_FOAM", 28)   # 土台縁の外側 cream の foamboard 帯
BAND_CORR = C.get("BAND_CORR", 20)   # その内側の corrugated（波形段ボール）帯
BAND = BAND_FOAM + BAND_CORR


class Rep:
    def __init__(self):
        self.items = []   # (key, title, status, detail, data)
        self.data = {}

    def add(self, key, title, status, detail, data=None):
        self.items.append(dict(key=key, title=title, status=status, detail=detail, data=data or {}))

    def overall(self):
        return max((i["status"] for i in self.items), key=lambda s: ORDER[s], default="PASS")


def eq(img, col, tol=0):
    return (np.abs(img.astype(int) - np.array(col)).max(-1) <= tol)


def largest(mask):
    lab, n = ndi.label(mask)
    if n == 0:
        return mask
    sz = ndi.sum(mask, lab, range(1, n + 1))
    return lab == (np.argmax(sz) + 1)


def hsv(a):
    a = a.astype(float)
    mx, mn = a.max(-1), a.min(-1)
    v = mx
    s = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1), 0)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    d = np.maximum(mx - mn, 1e-6)
    h = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) * 60
    return h, s, v


def runs_1d(m):
    """True の連続区間 [(a,b)]"""
    out, st = [], None
    for i, v in enumerate(m):
        if v and st is None:
            st = i
        if not v and st is not None:
            out.append((st, i - 1)); st = None
    if st is not None:
        out.append((st, len(m) - 1))
    return out


def side_view(m, side):
    """side の外縁が上端になるよう回転した配列（scan は行0→内側）。"""
    return {"N": m, "S": m[::-1], "W": m.T, "E": m.T[::-1]}[side]


def side_pt(side, along, depth, W, H):
    """side_view 座標 (along, depth) -> 画像 (x,y)"""
    return {"N": (along, depth), "S": (along, H - 1 - depth), "W": (depth, along), "E": (W - 1 - depth, along)}[side]


def first_run(col, minlen):
    """col(bool 配列)で最初に minlen 連続 True となる開始位置。無ければ len。"""
    run = 0
    for i, v in enumerate(col):
        run = run + 1 if v else 0
        if run >= minlen:
            return i - minlen + 1
    return len(col)


# ---------- 実測 ----------
def estimate_floor_color(a, rect=None):
    """床色を画像から推定する: 模型の天面 rect の中で『クリーム系（r-b>40, g-b>=22, r-g 12..60）』の画素を粗い色ビンに分け、
    上位ビンそれぞれを種に（和絶対差<45 の画素の開閉後）最大連結成分を求め、最も大きい成分の中央値を床色とする。
    戻り値 (色, 推定できたか, 最大連結成分の画素数)。固定の床色は使わない（BDY-07 の 224,188,148 のように MAP/生成ごとに違う）。"""
    H_, W_ = a.shape[:2]
    reg = np.zeros((H_, W_), bool)
    if rect is None:
        reg[:] = True
    else:
        reg[max(rect[1], 0):rect[3], max(rect[0], 0):rect[2]] = True
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    cand = reg & (r - b > 40) & (g - b >= 22) & (r - g >= 12) & (r - g <= 60) & (r >= 190) & (g >= 150)
    if cand.sum() < 1000:
        return FLOOR_REF.copy(), False, 0
    q = (a // 12)[cand]
    keys, cnt = np.unique(q[:, 0] * 10000 + q[:, 1] * 100 + q[:, 2], return_counts=True)
    best = None
    for k in keys[np.argsort(-cnt)[:6]]:
        seed = np.array([k // 10000, (k // 100) % 100, k % 100]) * 12 + 6
        m = (np.abs(a - seed).sum(-1) < 45) & reg
        m = ndi.binary_opening(m, iterations=2)
        lab, n = ndi.label(m)
        if n == 0:
            continue
        sz = ndi.sum(m, lab, range(1, n + 1))
        i = int(np.argmax(sz))
        if best is None or sz[i] > best[0]:
            best = (float(sz[i]), lab == (i + 1))
    if best is None or best[0] < 1000:
        return FLOOR_REF.copy(), False, 0
    return np.median(a[best[1]], axis=0), True, int(best[0])


def floor_iou_ov(a, fcol, exp_floor, exp_rect, s):
    """床IoU の定義（body_floor_overlay.py と共通）: 期待の天面 rect を 14px(×倍率) 内側に縮めた範囲で、
    実測床 = 床色との和絶対差<45 の画素の開閉2回→最大連結成分、期待床 = 清書図の床、IoU = 交差/和（補正・膨張なし）。"""
    H_, W_ = a.shape[:2]
    m = int(round(14 * s))
    x0, y0, x1, y1 = exp_rect
    rr = np.zeros((H_, W_), bool)
    rr[y0 + m:y1 - m, x0 + m:x1 - m] = True
    fl = (np.abs(a - fcol).sum(-1) < 45) & rr
    fl = ndi.binary_opening(fl, iterations=2)
    fl = largest(fl)
    e = exp_floor & rr
    inter, uni = int((fl & e).sum()), int((fl | e).sum())
    return (inter / uni if uni else 0.0), fl, e


def surface_mask(a, fcol):
    """模型の天面（床・地形・赤紙）らしい画素。土台の板（クリーム）・段ボール・机は含まない。"""
    h, s, v = hsv(a)
    r, b = a[..., 0].astype(float), a[..., 2].astype(float)
    floorish = (np.linalg.norm(a - fcol, axis=-1) < 28) & (r - b > 60)
    tape = (v > 200) & (h > 33) & (h < 58)
    terrainish = (s > 0.34) & (v > 105) & ~tape
    m = (floorish & ~tape) | terrainish
    return ndi.median_filter(m.astype(np.uint8), size=5) > 0


def side_img(a, side):
    """side_view の RGB 版（外縁が上端になる向きに回転）。"""
    return {"N": a, "S": a[::-1], "W": a.transpose(1, 0, 2), "E": a.transpose(1, 0, 2)[::-1]}[side]


def _first_run_rows(flag, start, minlen, gap, max_skip):
    """flag(行ごとの bool)で start から max_skip 行以内に始まる True の連続区間 [a,b)。
    途中 gap 行までの途切れは許す。無ければ (start,start)。"""
    n = len(flag)
    a = start
    lim = min(n, start + max_skip + 1)
    while a < lim and not flag[a]:
        a += 1
    if a >= lim:
        return start, start
    b, miss = a, 0
    while b < n and (flag[b] or miss < gap):
        miss = 0 if flag[b] else miss + 1
        b += 1
    b -= miss
    return (a, b) if b - a >= minlen else (start, start)


def measure_layers(a, s):
    """4辺それぞれで、画像の外周から内側へ「机(木目の茶) → 縁取り(cream の foamboard) → 波形(corrugated) → 天面」の
    4層の境界を構造で測る。色の絶対値でなく、各層の“行ごとの画素割合”の並びで決める。
      机     : 彩度の高い木目色（s>0.55）の画素が過半の行が外縁から続く
      縁取り : 明るい cream（v>185, 彩度0.12-0.45, 色相20-55°）が過半の行
      波形   : 強い輝度勾配（縞）の画素が一定割合ある行（平らな天面・床は勾配が無い）
    走査は辺の中央80%（通路で天面が縁取りに触れる所もあるが、層の行割合は多数決で決まる）。
    返り値 {side: dict(desk, foam, corr, edge, rows)} すべて px（実画像）。"""
    h, sa, v = hsv(a)
    lum = a.mean(-1)
    gy, gx = np.gradient(lum)
    grad = np.hypot(gx, gy) > 22
    wood = (sa > 0.55) & (v < 235) & (h > 8) & (h < 42)
    cream = (v > 185) & (sa > 0.12) & (sa < 0.45) & (h > 20) & (h < 55)
    res = {}
    for sd in "NESW":
        w_, c_, g_ = side_view(wood, sd), side_view(cream, sd), side_view(grad, sd)
        n = w_.shape[1]
        lo, hi = int(n * 0.10), int(n * 0.90)
        depth = int(min(w_.shape[0] * 0.3, 260 * s))
        wf = w_[:depth, lo:hi].mean(1)
        cf = c_[:depth, lo:hi].mean(1)
        gf = ndi.uniform_filter1d(g_[:depth, lo:hi].mean(1), 3)
        # 机: 外縁から続く wood 過半の行（4行連続で崩れたら終わり）
        d0 = 0
        while d0 < depth and wf[d0:d0 + 4].max() >= 0.5:
            d0 += 1
        # 縁取り: 机の終わりの影(<=16s行)を飛ばして cream 過半の行が続く区間
        fa, fb = _first_run_rows(cf >= 0.55, d0, max(3, int(4 * s)), 3, int(16 * s) + 2)
        # 波形: 縁取りの終わり直後から勾配の縞が続く区間
        ca, cb = _first_run_rows(gf >= 0.25, fb, max(3, int(4 * s)), 3, int(6 * s) + 2) if fb > fa else (fb, fb)
        edge = cb if cb > ca else fb
        res[sd] = dict(desk=int(d0), foam=int(fb - fa), foam_at=int(fa), corr=int(cb - ca), corr_at=int(ca), edge=int(edge),
                       wood_frac0=round(float(wf[:max(int(6 * s), 2)].mean()), 2))
    return res


def floor_mask_of(a, fcol, rect=None):
    h, s, v = hsv(a)
    r, b = a[..., 0].astype(float), a[..., 2].astype(float)
    m = (np.linalg.norm(a - fcol, axis=-1) < 28) & (r - b > 52)
    m = ndi.median_filter(m.astype(np.uint8), size=5) > 0
    m = ndi.binary_opening(m, iterations=2)
    if rect is not None:
        x0, y0, x1, y1 = rect
        k = np.zeros_like(m); k[y0:y1, x0:x1] = True
        m &= k
    return largest(m)


def red_comps(a, s, rect=None):
    r, g, b = a[..., 0].astype(int), a[..., 1].astype(int), a[..., 2].astype(int)
    m = (r > 150) & (g < 90) & (b < 100) & (r - g > 90)
    m = ndi.binary_opening(m, iterations=2)
    lab, n = ndi.label(m)
    out = []
    for i in range(1, n + 1):
        area = int((lab == i).sum())
        if area < 300 * s * s:
            continue
        cy, cx = ndi.center_of_mass(lab == i)
        out.append(dict(x=int(cx), y=int(cy), area=area, label=i))
    return out, lab


def probe_runs(fm, side, off, W, H):
    """side の辺から off px 内側の直線上で床の連続区間。戻り: [(a,b)] along 座標。"""
    v = side_view(fm, side)
    off = int(min(max(off, 0), v.shape[0] - 1))
    return runs_1d(v[off, :])


def circle_fit(xs, ys):
    A = np.c_[2 * xs, 2 * ys, np.ones_like(xs)]
    bb = xs ** 2 + ys ** 2
    sol = np.linalg.lstsq(A, bb, rcond=None)[0]
    cx, cy = sol[0], sol[1]
    r = math.sqrt(max(sol[2] + cx * cx + cy * cy, 0))
    return cx, cy, r


def ang_intervals(angs, bin_deg=2, min_pts=6, gap_deg=8):
    """北から時計回り(deg)の点群 -> 連続区間 [(a,b)]（小ギャップは結合）。"""
    hist = np.bincount((np.asarray(angs) // bin_deg).astype(int) % (360 // bin_deg), minlength=360 // bin_deg)
    on = hist >= max(1, min_pts // 3)
    idx = np.flatnonzero(on) * bin_deg
    if len(idx) == 0:
        return []
    out, st, pv = [], idx[0], idx[0]
    for x in idx[1:]:
        if x - pv > gap_deg:
            out.append((int(st), int(pv + bin_deg))); st = x
        pv = x
    out.append((int(st), int(pv + bin_deg)))
    if len(out) > 1 and out[0][0] == 0 and out[-1][1] >= 360 - bin_deg:
        out[0] = (out[-1][0] - 360, out[0][1]); out.pop()
    return [(a % 360, b % 360 if b % 360 else 360) if False else (a, b) for a, b in out]


def clock_angle(dx, dy):
    return (np.degrees(np.arctan2(dx, -dy)) + 360) % 360


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("map_id", help="例: BDY-03")
    ap.add_argument("image", help="生成画像 (1920x1080 または 1672x941)")
    ap.add_argument("--edit-source", help="編集元画像（床IoU・赤紙ずれを比較）")
    ap.add_argument("--out", help="重ね画像の出力パス（既定: 画像と同じ場所の <stem>-check.png）")
    ap.add_argument("--expect-red", type=int, default=6, help="赤い折り紙の期待枚数（既定6）")
    ap.add_argument("--clean", help="期待幾何の清書PNG（既定: verification/body-layout/clean/<MAP>.png）")
    ap.add_argument("--json", action="store_true", help="JSON のみ標準出力")
    ap.add_argument("--json-out", help="JSON をファイルにも書く")
    args = ap.parse_args()

    rep = Rep()
    clean_path = Path(args.clean) if args.clean else REPO / "verification/body-layout/clean" / f"{args.map_id}.png"
    if not clean_path.exists():
        sys.exit(f"期待幾何が無い: {clean_path}")
    gimg = Image.open(args.image).convert("RGB")
    W, H = gimg.size
    s = W / 1920.0
    a = np.asarray(gimg).astype(int)
    clean = np.asarray(Image.open(clean_path).convert("RGB")).astype(int)
    if clean.shape[:2] != (1080, 1920):
        sys.exit("清書図が 1920x1080 でない")

    # ---- 1. サイズ ----
    if (W, H) in OK_SIZES:
        rep.add("size", "実寸", "PASS", f"{W}x{H}（倍率 {s:.4f}）")
    elif abs(W / H - 16 / 9) < 0.01:
        rep.add("size", "実寸", "WARN", f"{W}x{H} は想定外サイズだが16:9（倍率 {s:.4f} で続行）")
    else:
        rep.add("size", "実寸", "FAIL", f"{W}x{H}: 許容は 1920x1080 / 1672x941")
    out_img = Image.new("RGB", (W, H))

    # 期待幾何（清書図を生成画像サイズへ）
    exp_img = np.asarray(Image.fromarray(clean.astype("uint8")).resize((W, H), Image.NEAREST)).astype(int)
    exp_floor = eq(exp_img, CL_FLOOR)
    exp_wall = eq(exp_img, CL_WALL)
    exp_desk = eq(exp_img, CL_DESK)
    ys, xs = np.where(~exp_desk)
    exp_desk_m = dict(N=int(ys.min()), S=int(H - 1 - ys.max()), W=int(xs.min()), E=int(W - 1 - xs.max()))
    ys, xs = np.where(exp_floor | eq(exp_img, CL_TERRAIN) | exp_wall)
    exp_rect = (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)
    exp_band = dict(N=exp_rect[1] - exp_desk_m["N"], S=H - exp_rect[3] - exp_desk_m["S"],
                    W=exp_rect[0] - exp_desk_m["W"], E=W - exp_rect[2] - exp_desk_m["E"])

    # ---- 実測の下ごしらえ ----
    _m14 = int(round(14 * s))
    fcol, calibrated, fcol_px = estimate_floor_color(a, (exp_rect[0] + _m14, exp_rect[1] + _m14, exp_rect[2] - _m14, exp_rect[3] - _m14))
    layers = measure_layers(a, s)
    layers_ok = all(layers[sd]["foam"] >= 0.3 * BAND_FOAM * s and layers[sd]["corr"] >= 0.3 * BAND_CORR * s for sd in "NESW")
    if layers_ok:
        edge_px = {sd: layers[sd]["edge"] for sd in "NESW"}
    else:   # 層が読めない画像は、期待の縁位置で以後の項目（床・通路・赤紙）を続行する
        edge_px = {sd: exp_desk_m[sd] + exp_band[sd] for sd in "NESW"}
    rect = (edge_px["W"], edge_px["N"], W - edge_px["E"], H - edge_px["S"])
    fm = floor_mask_of(a, fcol, rect=(max(rect[0] - int(4 * s), 0), max(rect[1] - int(4 * s), 0),
                                      min(rect[2] + int(4 * s), W), min(rect[3] + int(4 * s), H)))
    rep.data["floor_color"] = [int(x) for x in fcol]
    rep.data["model_rect_measured"] = list(rect)
    rep.data["model_rect_expected"] = list(exp_rect)

    # ---- 2. 床 IoU ----
    # 定義は body_floor_overlay.py と共通（floor_iou_ov）: 床色は画像から推定したクリーム系の最大連結クラスタ（固定値でない）、
    # 天面 rect を14px内側に縮め、膨張・縁取り補正なし。通路の幅・位置は別項目（passages）で測る。
    iou, fl_ov, e_ov = floor_iou_ov(a, fcol, exp_floor, exp_rect, s)
    st = "PASS" if iou >= 0.75 else "WARN" if iou >= 0.60 else "FAIL"
    note = "" if calibrated else "（床色の推定に失敗、既定色を使用）"
    rep.add("floor_iou", "床（最大連結）と期待床の IoU", st,
            f"IoU {iou:.3f}（床色 {tuple(int(x) for x in fcol)} は画像から推定（最大連結クラスタ{fcol_px}px）、実測床 {int(fl_ov.sum())}px / 期待 {int(e_ov.sum())}px / 共通 {int((fl_ov & e_ov).sum())}px）{note}。"
            " PASS>=0.75 WARN>=0.60（body_floor_overlay.py と同じ定義）", dict(iou=float(iou), floor_color=[int(x) for x in fcol]))

    # ---- 4. 机・土台縁（4層を外周から内側へ構造で測る）----
    # 期待の層厚: 机=清書図の各辺の机余白、縁取り(foamboard)=BAND_FOAM、波形(corrugated)=BAND_CORR（いずれも ×倍率）。
    # 判定は「期待に対する比」: 机・縁取り・波形のいずれも 比<0.30 で FAIL（その層が見えない）、<0.60 か上限超で WARN。
    lines, st4, bad4 = [], "PASS", []
    exp_foam, exp_corr = BAND_FOAM * s, BAND_CORR * s
    SPEC = (("机", "desk", None, 0.30, 0.60, 1.8), ("縁取り(foam)", "foam", exp_foam, 0.30, 0.60, 2.2),
            ("波形(corrugated)", "corr", exp_corr, 0.30, 0.60, 2.5))
    for sd in "NESW":
        L = layers[sd]
        lines.append(f"{sd}: 机 {L['desk']}px(期待{exp_desk_m[sd]}) / 縁取り {L['foam']}px(期待{exp_foam:.0f}) / 波形 {L['corr']}px(期待{exp_corr:.0f}) / 天面の始まり {L['edge']}px(期待{exp_desk_m[sd] + exp_band[sd]})")
        for nm, key, ex, lo_f, warn_f, hi_f in SPEC:
            ex = exp_desk_m[sd] if ex is None else ex
            ratio = L[key] / max(ex, 1)
            if ratio < lo_f:
                st4 = "FAIL"; bad4.append(f"{sd}辺の{nm}が見えない({L[key]}px、期待{ex:.0f}の{ratio * 100:.0f}%<30%)")
            elif ratio < warn_f or ratio > hi_f:
                if st4 == "PASS":
                    st4 = "WARN"
                bad4.append(f"{sd}辺の{nm}が期待からずれる({L[key]}px、期待{ex:.0f}の{ratio * 100:.0f}%)")
    rep.add("margins", "机の余白と土台縁の帯(4辺・4層)", st4,
            " ／ ".join(bad4) if bad4 else "4辺とも 机→縁取り→波形→天面 の4層が期待の範囲",
            dict(layers=layers, expected=dict(desk=exp_desk_m, foam=exp_foam, corr=exp_corr), lines=lines))

    # ---- 3. 通路 ----
    pas_lines, st3, bad3 = [], "PASS", []
    _fl = ndi.binary_opening((np.linalg.norm(a - fcol, axis=-1) < 32) & (a[..., 0] - a[..., 2] > 50), iterations=1)
    fm_loose_all = {sd: side_view(_fl, sd) for sd in "NESW"}
    pdata = {}
    edge_med = edge_px
    for sd in "NESW":
        # 縁に接する区間: 天面の始まり(波形の内側)から +14〜+30px(×倍率)の帯で床が6割以上の列を連結（期待も同じ帯で測る）。
        # 辺の along 方向は模型の内側だけ（角で隣の辺の縁取りを拾わない）。幅 60px(×倍率) 未満の細い区間は縄・段ボールの縁として捨てる。
        PS, PE, MINW = int(14 * s), int(30 * s), 60 * s
        def strip_runs(mask2d, e0, r):
            v_ = side_view(mask2d, sd)
            f_ = v_[min(e0 + PS, v_.shape[0] - 1):min(e0 + PE, v_.shape[0]), :].mean(0) >= 0.6
            lo_, hi_ = (r[0], r[2]) if sd in "NS" else (r[1], r[3])
            f_[:max(lo_, 0)] = False; f_[hi_:] = False
            return [(x, y) for x, y in runs_1d(f_) if y - x > MINW]
        e0 = exp_desk_m[sd] + exp_band[sd]
        eruns = strip_runs(exp_floor, e0, exp_rect)
        o0 = int(edge_med[sd])
        oruns = strip_runs(_fl, o0, rect)
        oruns = [(x - ROPE_PAD * s, y + ROPE_PAD * s) for x, y in oruns]
        pdata[sd] = dict(expected=[(int(x), int(y)) for x, y in eruns], observed=[(int(x), int(y)) for x, y in oruns])
        # 貪欲マッチ（中心が近い順）
        used, pairs = set(), []
        for (ea, eb) in eruns:
            ec = (ea + eb) / 2
            best = None
            for k, (oa, ob) in enumerate(oruns):
                if k in used:
                    continue
                dd = abs((oa + ob) / 2 - ec)
                if best is None or dd < best[0]:
                    best = (dd, k)
            if best is not None and best[0] <= 120 * s:
                used.add(best[1]); pairs.append(((ea, eb), oruns[best[1]]))
            else:
                pairs.append(((ea, eb), None))
        extra = [oruns[k] for k in range(len(oruns)) if k not in used]
        if len(oruns) != len(eruns):
            st3 = "FAIL"; bad3.append(f"{sd}辺: 通路 期待{len(eruns)}本/実測{len(oruns)}本")
        for (ea, eb), o in pairs:
            ec, ew = (ea + eb) / 2, eb - ea + 1
            if o is None:
                pas_lines.append(f"{sd}: 期待 中心{ec:.0f} 幅{ew} -> 実測なし")
                continue
            oc, ow = (o[0] + o[1]) / 2, o[1] - o[0] + 1
            dpos, dw = oc - ec, ow / ew - 1
            ok = abs(dpos) <= PASSAGE_POS_TOL * s and abs(dw) <= PASSAGE_W_TOL
            pas_lines.append(f"{sd}: 期待 中心{ec:.0f} 幅{ew} / 実測 中心{oc:.0f} 幅{ow:.0f} (位置{dpos:+.0f}px 幅{dw * 100:+.0f}%) {'OK' if ok else 'NG'}")
            if not ok:
                if st3 == "PASS":
                    st3 = "WARN"
                bad3.append(f"{sd}辺 期待中心{ec:.0f}: 位置{dpos:+.0f}px/幅{dw * 100:+.0f}%")
        for o in extra:
            pas_lines.append(f"{sd}: 余分な床区間 中心{(o[0] + o[1]) / 2:.0f} 幅{o[1] - o[0] + 1}")
        # 縁に届くか（実測区間の中心から外縁側へ床が続くか）
        for (oa, ob) in oruns:
            c = int((oa + ob) // 2)
            v = side_view(fm, sd)
            dpt = int(edge_med[sd] + PROBE_IN * s)
            seg = fm_loose_all[sd][int(edge_med[sd] + 14 * s):dpt + 1, c]
            if seg.size and seg.mean() < 0.9:
                st3 = "FAIL"; bad3.append(f"{sd}辺 中心{c}: 縁まで床が連続しない")
    # 床が模型の外（机の上）: 机の層(画像の外周〜縁取りの始まり)に床色の塊が出ていないか。縁取りの foamboard は床と同系色なので数えない
    desk_zone = np.zeros((H, W), bool)
    dz = int(0.9 * min(layers[sd]["desk"] for sd in "NESW")) if layers_ok else int(0.9 * min(exp_desk_m.values()))
    desk_zone[:dz, :] = True; desk_zone[H - dz:, :] = True; desk_zone[:, :dz] = True; desk_zone[:, W - dz:] = True
    on_desk_mask = ndi.binary_opening((np.linalg.norm(a - fcol, axis=-1) < 20) & (a[..., 0] - a[..., 2] > 58), iterations=2) & desk_zone
    on_desk = int(on_desk_mask.sum())
    out_cnt = on_desk
    if out_cnt > 400 * s * s:
        if st3 == "PASS":
            st3 = "WARN"
        bad3.append(f"床色が机の上（画像の外周）に{out_cnt}px はみ出す")
    rep.add("passages", "模型の縁に届く通路（本数・位置・幅）", st3,
            " ／ ".join(bad3) if bad3 else "全通路が期待位置±25px・幅±10%(倍率済)",
            dict(sides=pdata, lines=pas_lines, floor_outside_px=out_cnt, floor_on_desk_px=on_desk))

    # ---- 5. 赤紙（模型の中の枚数・位置）と 5b. 模型の外の赤 ----
    comps, rlab = red_comps(a, s)
    reds, outs, bad5, st5 = [], [], [], "PASS"
    fm_filled = ndi.binary_dilation(fm, iterations=1)
    for c in comps:
        reg = rlab == c["label"]
        rim = ndi.binary_dilation(reg, iterations=max(int(8 * s), 3)) & ~reg
        rim_floor = float((fm_filled & rim).sum() / max(rim.sum(), 1))
        in_rect = rect[0] <= c["x"] < rect[2] and rect[1] <= c["y"] < rect[3]
        on_floor = bool(fm[c["y"], c["x"]]) or rim_floor > 0.15
        e_cls = "floor" if exp_floor[c["y"], c["x"]] else "terrain" if eq(exp_img, CL_TERRAIN)[c["y"], c["x"]] else "other"
        d = dict(x=c["x"], y=c["y"], area=c["area"], rim_floor=round(rim_floor, 3), in_model=in_rect,
                 expected_class=e_cls, on_floor=on_floor)
        if not in_rect:
            outs.append(d)
            continue
        reds.append(d)
        if on_floor:
            st5 = "FAIL"; bad5.append(f"({c['x']},{c['y']}) が床の上/床に接する(縁の床率{rim_floor:.0%})")
    if len(reds) != args.expect_red:
        st5 = "FAIL"; bad5.append(f"模型の中の枚数 期待{args.expect_red}/実測{len(reds)}")
    rep.add("red", "赤い折り紙（模型の中の枚数・位置・面積）", st5,
            " ／ ".join(bad5) if bad5 else f"模型の中に{len(reds)}枚、全て地形の上",
            dict(count=len(reds), comps=reds))
    st5b = "FAIL" if outs else "PASS"
    rep.add("red_outside", "模型の外の赤（縁・机・床の外）", st5b,
            (f"模型の外に赤が{len(outs)}個: " + ", ".join(f"({d['x']},{d['y']})" for d in outs)) if outs else "模型の外に赤なし（全体の赤 "
            f"{len(comps)} 個 = 模型の中 {len(reds)} + 外 0）", dict(count=len(outs), comps=outs, total=len(comps)))

    # ---- 6. 広間 ----
    # 壁の色（青灰とは限らない: 段ボール茶・毛糸に塗り直されうる）に頼らず、「広間の外周で床の連続が途切れるか」を
    # 床マスクだけで測る。広間の中心から3°刻みで外へ歩き、床が6px続けて途切れた半径(r_end)を、期待(清書図)と実測で比べる。
    #   期待の壁の弧 = 期待の r_end が 1.25×床半径 未満の方位（壁・地形に床が阻まれる）。通路の方位は r_end が長く伸びる。
    # 壁の色で見た弧（青灰など）は参考値として data に残す。判定は床の途切れ方位だけで行う。
    hall = None
    if exp_wall.any():
        ey, ex = np.where(exp_wall)
        ecx, ecy, eR = circle_fit(ex.astype(float), ey.astype(float))
        rr = np.hypot(ex - ecx, ey - ecy)
        e_floor_r = float(np.percentile(rr, 1))
        e_ang = ang_intervals(clock_angle(ex - ecx, ey - ecy))

        def end_profile(mask):
            rmax = int(e_floor_r * 2)
            res_ = []
            for ang in range(0, 360, 3):
                th = math.radians(ang)
                miss, r_end = 0, rmax
                for r_ in range(rmax):
                    x_, y_ = int(round(ecx + r_ * math.sin(th))), int(round(ecy - r_ * math.cos(th)))
                    if not (0 <= x_ < W and 0 <= y_ < H):
                        r_end = r_; break
                    if mask[y_, x_]:
                        miss = 0
                    else:
                        miss += 1
                        if miss >= 6:
                            r_end = r_ - miss + 1; break
                res_.append(r_end)
            return np.array(res_, float)
        E_end = end_profile(exp_floor)
        O_end = np.minimum(end_profile(_fl) + ROPE_PAD * s, e_floor_r * 2)   # 縁取りの縄の分だけ足す
        tol = 0.2 * e_floor_r
        wallish = E_end < 1.25 * e_floor_r
        agree = np.abs(E_end - O_end) <= tol
        a_wall = float(agree[wallish].mean()) if wallish.any() else 1.0
        extra_open = int(((O_end < 1.25 * e_floor_r) & ~wallish).sum())
        a_all = float(agree.mean())
        bad_deg = [int(d) for d, ok in zip(range(0, 360, 3), agree) if not ok and wallish[d // 3]]
        st6 = "PASS" if a_wall >= 0.85 and extra_open <= 10 else "FAIL" if a_wall < 0.5 else "WARN"
        msg = [f"期待の壁の方位 {int(wallish.sum()) * 3}° のうち床の途切れが期待どおりの割合 {a_wall * 100:.0f}%（PASS>=85% WARN>=50%）",
               f"全方位の一致 {a_all * 100:.0f}%", f"期待に無い途切れ {extra_open * 3}°（>30°で WARN）"]
        if bad_deg:
            msg.append("不一致の壁方位(北から時計回り) " + ", ".join(f"{x}°" for x in bad_deg[:12]))
        hall = dict(expected=dict(center=[round(ecx), round(ecy)], floor_r=round(e_floor_r), arcs=e_ang),
                    floor_end=dict(agree_on_wall=a_wall, agree_all=a_all, extra_open_deg=extra_open * 3,
                                   expected_wall_deg=int(wallish.sum()) * 3))
        # 参考: 床でも地形でもない「壁色」の弧（青灰・毛糸など。茶に塗り直されると取れない）
        yy, xx = np.mgrid[0:H, 0:W]
        r_o = np.hypot(xx - ecx, yy - ecy)
        ring_h = (r_o > e_floor_r * 0.80) & (r_o < e_floor_r + WALL_T * s * 2.2)
        hh, ss, vv = hsv(a)
        cand = ring_h & (np.linalg.norm(a - fcol, axis=-1) > 30) & ~((ss > 0.40) & (vv < 200) & (hh < 30)) & ~((a[..., 0] > 150) & (a[..., 1] < 90))
        cand = ndi.binary_opening(cand, iterations=2)
        lab, n = ndi.label(cand)
        keep = np.zeros_like(cand)
        for i in range(1, n + 1):
            if (lab == i).sum() >= 150 * s * s:
                keep |= lab == i
        oy, ox = np.where(keep)
        color_arcs = ang_intervals(clock_angle(ox - ecx, oy - ecy), min_pts=6) if len(ox) >= 100 else []
        hall["observed_color_arcs"] = color_arcs
        rep.add("hall", "広間（壁の弧: 床の途切れ方位）", st6,
                "。".join(msg) + f"。参考: 壁色の弧 {', '.join(f'{x}-{y}°' for x, y in color_arcs) or '検出なし(茶に塗り直された壁は取れない。目視要確認)'}"
                f" / 期待 {', '.join(f'{x}-{y}°' for x, y in e_ang)}（北から時計回り）。期待中心({ecx:.0f},{ecy:.0f}) 床半径{e_floor_r:.0f}", hall)
    else:
        rep.add("hall", "広間", "PASS", "この MAP に広間なし（清書に壁色なし）")

    # ---- 7. 汚れ・編集元 ----
    ff = ndi.binary_fill_holes(fm)
    inner = ndi.binary_erosion(ff, iterations=max(int(6 * s), 3))
    off = (np.linalg.norm(a - fcol, axis=-1) > 42) & inner
    # 赤紙・壁の弧が床内にあれば床外の穴として fill 済みなので inner に含まれる→除外
    rr_mask = ndi.binary_dilation(rlab > 0, iterations=3)
    inner_ex = inner & ~rr_mask & ~(exp_wall if False else np.zeros_like(inner))
    off = (np.linalg.norm(a - fcol, axis=-1) > 42) & inner_ex
    # 弧（壁）の画素は汚れではない: ホールを埋めた分のうち床マスクの穴は広間の弧
    arc_hole = ff & ~fm
    arc_hole = ndi.binary_dilation(arc_hole, iterations=4) if arc_hole.any() else arc_hole
    off_net = off & ~(ndi.binary_opening(arc_hole & ~fm, iterations=1) if False else np.zeros_like(off))
    frac = float(off_net.sum() / max(inner_ex.sum(), 1))
    st7 = "PASS" if frac < 0.02 else "WARN" if frac < 0.06 else "FAIL"
    d7 = dict(off_frac=frac, inner_px=int(inner_ex.sum()))
    msg7 = f"床内部（縁から6px内側）で床色から外れる画素 {frac * 100:.2f}%（PASS<2% WARN<6%）"
    if args.edit_source:
        src = np.asarray(Image.open(args.edit_source).convert("RGB")).astype(int)
        if src.shape != a.shape:
            src = np.asarray(Image.fromarray(src.astype("uint8")).resize((W, H), Image.LANCZOS)).astype(int)
        scol, _, _ = estimate_floor_color(src, (exp_rect[0] + _m14, exp_rect[1] + _m14, exp_rect[2] - _m14, exp_rect[3] - _m14))
        sl = measure_layers(src, s)
        srect = tuple(rect) if not all(sl[sd]["foam"] >= 0.3 * BAND_FOAM * s for sd in "NESW") else \
            (sl["W"]["edge"], sl["N"]["edge"], W - sl["E"]["edge"], H - sl["S"]["edge"])
        sfm = floor_mask_of(src, scol, rect=srect)
        i2 = float((fm & sfm).sum() / max((fm | sfm).sum(), 1))
        sc, _ = red_comps(src, s)
        shifts = []
        for c in comps:
            if sc:
                dd = min(math.hypot(c["x"] - o["x"], c["y"] - o["y"]) for o in sc)
                shifts.append(dd)
        mxs = max(shifts) if shifts else None
        st_e = "PASS" if i2 >= 0.97 and (mxs is None or mxs <= 15 * s) else "WARN" if i2 >= 0.93 and (mxs is None or mxs <= 40 * s) else "FAIL"
        d7.update(edit_floor_iou=float(i2), red_shift_max=mxs, red_count_src=len(sc), red_count_out=len(comps))
        msg7 += f"。編集元との床IoU {i2:.3f}、赤紙 {len(sc)}→{len(comps)}枚、最大ずれ {mxs if mxs is None else round(mxs, 1)}px"
        if ORDER[st_e] > ORDER[st7]:
            st7 = st_e
    rep.add("stain", "床の汚れ（と編集元との差）", st7, msg7, d7)

    # ---- 8. 色の逸脱（床・地形の地色）と 8b. 装飾の色域 ----
    # 8: 床と地形の『地色』だけを対象にする。床領域の極端色（緑・青・強赤）の比率と、地形領域の色の中央値（色相・彩度）で測る。
    #    装飾（ビーズ・フェルト・毛糸）の高彩度は中央値に響かないので、ここでは誤検出しない。
    # 8b: 装飾の色域: 地形面積に対する『肌色・薄桃・クリーム・茶系・象牙色の範囲外（緑・青・紫・黄・オレンジ）』の画素比率。赤は折り紙として除外。
    inside = np.zeros((H, W), bool)
    inside[rect[1]:rect[3], rect[0]:rect[2]] = True
    hh, ss, vv = hsv(a)
    redzone = ndi.binary_dilation(rlab > 0, iterations=4)
    floor_zone = ndi.binary_dilation(ndi.binary_fill_holes(fm), iterations=max(int(8 * s), 3)) & inside
    terr_zone = inside & ~floor_zone
    blue = (a[..., 2] > a[..., 0] + 12) & (ss > 0.18)
    green = (a[..., 1] > a[..., 0] + 6) & (a[..., 1] > a[..., 2] + 10) & (ss > 0.2)
    strong_red = (ss > 0.62) & (a[..., 0] > 170) & ((hh < 8) | (hh > 350))
    ext_floor = floor_zone & ~redzone & (blue | green | strong_red)
    fz = int(floor_zone.sum())
    frac_floor = float(ext_floor.sum() / max(fz, 1))
    tm = terr_zone & ~redzone & (vv > 60)
    tn = int(tm.sum())
    hm = float(np.median(hh[tm])) if tn else float("nan")
    sm_ = float(np.median(ss[tm])) if tn else float("nan")
    tcol = np.median(a[tm], axis=0).astype(int).tolist() if tn else None
    bad8 = []
    st8 = "PASS"
    if frac_floor >= 0.05:
        st8 = "FAIL"; bad8.append(f"床領域に緑・青・強赤が{frac_floor * 100:.1f}%")
    elif frac_floor >= 0.01:
        st8 = "WARN"; bad8.append(f"床領域に緑・青・強赤が{frac_floor * 100:.1f}%")
    if not tn:
        if st8 == "PASS":
            st8 = "WARN"
        bad8.append("判定不能（地形の地色が測れない。全面ベタ画像など）")
    elif not (0 <= hm <= 50 or hm >= 340):
        st8 = "FAIL"; bad8.append(f"地形の地色の色相{hm:.0f}°が肌・桃・茶の範囲（340-50°）外")
    elif sm_ < 0.10 or sm_ > 0.80:
        if st8 == "PASS":
            st8 = "WARN"
        bad8.append(f"地形の地色の彩度{sm_:.2f}が 0.10-0.80 外")
    rep.add("colors", "色の逸脱（床と地形の地色）", st8,
            "。".join(bad8) if bad8 else f"床領域の極端色 {frac_floor * 100:.2f}%、地形の地色 {tcol}（色相中央 {hm:.0f}°・彩度中央 {sm_:.2f}）は範囲内（装飾は 装飾の色域 で別に測る）",
            dict(floor_extreme_frac=frac_floor, terrain_median_rgb=tcol, terrain_hue_median=hm, terrain_sat_median=sm_))
    # 装飾の色域
    gam_green = (hh >= 75) & (hh < 170) & (ss > 0.20) & (vv > 60)
    gam_blue = (hh >= 170) & (hh < 255) & (ss > 0.18) & (vv > 60)
    gam_purple = (hh >= 255) & (hh < 335) & (ss > 0.20) & (vv > 60)
    gam_yellow = (hh >= 48) & (hh < 75) & (ss > 0.35) & (vv > 120)
    gam_orange = (hh >= 18) & (hh < 48) & (ss > 0.78) & (vv > 180)
    gcls = {"緑": gam_green, "青": gam_blue, "紫": gam_purple, "黄": gam_yellow, "橙": gam_orange}
    tz = terr_zone & ~redzone
    tz_n = int(tz.sum())
    cnts = {k: int((v_ & tz).sum()) for k, v_ in gcls.items()}
    out_n = int(sum(cnts.values()))
    frac_g = out_n / max(tz_n, 1)
    st8b = "PASS" if frac_g <= 0.02 else "WARN" if frac_g <= 0.05 else "FAIL"
    rep.add("deco_gamut", "装飾の色域（肌色・薄桃・クリーム・茶系・象牙色の外）", st8b,
            f"地形面積 {tz_n}px のうち色域外 {out_n}px = {frac_g * 100:.2f}%（" + "・".join(f"{k}{v_}" for k, v_ in cnts.items()) +
            "。赤は折り紙として除外）。PASS<=2% WARN<=5% FAIL>5%", dict(frac=frac_g, counts=cnts, terrain_px=tz_n))
    gam_any = tz & (gam_green | gam_blue | gam_purple | gam_yellow | gam_orange)   # 重ね画像用

    # ---- 重ね画像 ----
    ov = Image.fromarray(a.astype("uint8")).convert("RGBA")
    layer = np.zeros((H, W, 4), np.uint8)
    layer[fm] = (40, 220, 90, 90)
    edge_exp = exp_floor & ~ndi.binary_erosion(exp_floor, iterations=2)
    layer[edge_exp] = (255, 0, 255, 255)
    layer[off_net] = (255, 255, 0, 255)
    layer[gam_any] = (0, 60, 255, 200)
    ov = Image.alpha_composite(ov, Image.fromarray(layer))
    dr = ImageDraw.Draw(ov)
    dr.rectangle(rect, outline=(0, 255, 255, 255), width=2)
    dr.rectangle(exp_rect, outline=(255, 128, 0, 255), width=1)
    for sd in "NESW":
        for (x0, x1), col in [(r_, (0, 255, 0, 255)) for r_ in pdata[sd]["observed"]] + [(r_, (255, 0, 255, 255)) for r_ in pdata[sd]["expected"]]:
            if sd in "NS":
                y = edge_med[sd] + PROBE_IN * s if sd == "N" else H - 1 - edge_med[sd] - PROBE_IN * s
                dr.line([(x0, y), (x1, y)], fill=col, width=3)
            else:
                x = edge_med[sd] + PROBE_IN * s if sd == "W" else W - 1 - edge_med[sd] - PROBE_IN * s
                dr.line([(x, x0), (x, x1)], fill=col, width=3)
    for d in reds:
        dr.ellipse([d["x"] - 18, d["y"] - 18, d["x"] + 18, d["y"] + 18], outline=(255, 255, 255, 255), width=3)
    if exp_wall.any():
        dr.ellipse([ecx - e_floor_r, ecy - e_floor_r, ecx + e_floor_r, ecy + e_floor_r], outline=(0, 160, 255, 255), width=2)
        if keep.any():
            km = keep & ~ndi.binary_erosion(keep, iterations=1)
            arr = np.asarray(ov).copy(); arr[km] = (0, 160, 255, 255); ov = Image.fromarray(arr)
    outp = Path(args.out) if args.out else Path(args.image).with_name(Path(args.image).stem + "-check.png")
    outp.parent.mkdir(parents=True, exist_ok=True)
    ov.convert("RGB").save(outp)

    result = dict(map=args.map_id, image=str(args.image), size=[W, H], scale=round(s, 4), overall=rep.overall(),
                  overlay=str(outp), note="美観・グロの判断はしない（人間/レビュー担当が見る）。幾何・色の機械実測のみ。",
                  items=rep.items, measured=rep.data)
    if args.json_out:
        Path(args.json_out).write_text(json.dumps(result, ensure_ascii=False, indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o)), encoding="utf-8")
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o)))
        return
    print(f"== {args.map_id} {args.image}  {W}x{H} (x{s:.3f}) ==")
    for it in rep.items:
        print(f"[{it['status']}] {it['title']}: {it['detail']}")
        for ln in it["data"].get("lines", []) or []:
            print(f"      {ln}")
    print(f"総合: {rep.overall()}   重ね画像: {outp}")
    print("※ 美観・グロの判断はしない。幾何・色の機械実測のみ（緑=実測床 / 紫線=期待床の縁 / 水=実測模型rect / 橙=期待rect / 黄=床の汚れ / 濃青=装飾の色域外 / 水の円=広間期待円と弧）。")


if __name__ == "__main__":
    main()
