#!/usr/bin/env python3
"""BDY-02 の送信文（docs/production/20261022-bdy02-adoption-prompts/BDY-02-stage1-prompt-send.txt。採用記録）に書いた座標・角度を、clean 割付図の画素から『別コード』で再測定して突き合わせる。
build_body_prompt.py（numpy の隣接シフト・列の追跡・代数的楕円当て）とは別の方法を使う:
  scipy.ndimage でラベル付け・膨張、scipy.optimize で楕円の幾何当て、行ごとの境界の走査で斜めの縁を当てる。

実行: uv run --with pillow --with numpy --with scipy python3 -I verification/body-layout/remeasure_bdy02.py [送信文のパス]
  送信文の既定は採用記録の BDY-02-stage1-prompt-send.txt。作り直し版は verification/body-layout/prompts/BDY-02-prompt-send.txt を渡す（新プールの onepass。構造の文と数値の書式は同じ）。
終了コード: 0=全件一致、1=不一致あり
"""
import math
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from scipy.optimize import least_squares

REPO = Path(__file__).resolve().parents[2]
SEND_PATH = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else REPO / "docs/production/20261022-bdy02-adoption-prompts/BDY-02-stage1-prompt-send.txt"
SEND = SEND_PATH.read_text(encoding="utf-8")
print(f"送信文: {SEND_PATH}")
im = np.asarray(Image.open(REPO / "verification/body-layout/clean/BDY-02.png").convert("RGB")).astype(int)
FLOOR, WALL, TERR = (232, 201, 168), (92, 104, 128), (170, 130, 110)
fl = (im == FLOOR).all(2)
wall = (im == WALL).all(2)
terr = (im == TERR).all(2)
bad = []


def check(name, measured, written, tol):
    ok = abs(measured - written) <= tol
    print(f"{'OK ' if ok else 'NG '} {name}: 実測 {measured:.2f} / 送信文 {written} (許容±{tol})")
    if not ok:
        bad.append(name)


def num(pattern, group=1, cast=float):
    m = re.search(pattern, SEND)
    if not m:
        print(f"NG  送信文に {pattern!r} が無い")
        bad.append(pattern)
        return None
    return cast(m.group(group))


# ---- 辺の床区間（模型の縁の行/列を scipy.ndimage.label で数える）
MX0, MY0, MX1, MY1 = 138, 138, 1782, 942


def segs(line):
    lab, n = ndi.label(line)
    return [(int(np.nonzero(lab == i)[0].min()), int(np.nonzero(lab == i)[0].max())) for i in range(1, n + 1)]


edge = {"N": segs(fl[MY0, :]), "S": segs(fl[MY1 - 1, :]), "W": segs(fl[:, MX0]), "E": segs(fl[:, MX1 - 1])}
print("辺の床区間:", edge)
want = {"N": [(845, 1075), (1239, 1469)], "S": [(450, 680), (845, 1075), (1239, 1469)], "W": [(425, 655)], "E": [(248, 477)]}
for s, w in want.items():
    for (a, b), (c, d) in zip(edge[s], w):
        check(f"{s}辺 区間始点", a, c, 2)
        check(f"{s}辺 区間終点", b, d, 2)
    if len(edge[s]) != len(w):
        print(f"NG  {s}辺の本数 {len(edge[s])} != {len(w)}"); bad.append(s)
for pat, nm in ((r"head passage at x (\d+) to (\d+)", "北 頭"), (r"mouth passage at x (\d+) to (\d+)", "北 口"),
                (r"lung passage at x (\d+) to (\d+)", "南 肺"), (r"lower-body passage at x (\d+) to (\d+)", "南 下半身"),
                (r"heart passage at x (\d+) to (\d+)", "南 心臓"), (r"right-arm passage \(the person's own right arm\) at y (\d+) to (\d+)", "西 右腕"),
                (r"left-arm passage \(the person's own left arm\) at y (\d+) to (\d+)", "東 左腕")):
    a, b = num(pat, 1, int), num(pat, 2, int)
    side = {"北": "N", "南": "S", "西": "W", "東": "E"}[nm[0]]
    ok = any(abs(a - s0) <= 2 and abs(b - s1) <= 2 for s0, s1 in edge[side])
    print(f"{'OK ' if ok else 'NG '} 送信文の {nm}: {a}–{b} が辺の床区間に存在")
    if not ok:
        bad.append(nm)

# ---- 広間: 壁（外縁=地形に接する境界）を最小二乗の幾何当てで楕円に
ring = ndi.binary_dilation(terr, iterations=1) & wall
oy, ox = np.nonzero(ring)
# 内縁: 壁を1画素ずつ侵食し、床に接する画素のうち外縁の楕円の内側 12–30px のものだけ
inner = ndi.binary_dilation(fl, iterations=1) & wall
iy, ix = np.nonzero(inner)


def ell_res(p, x, y):
    cx, cy, a, b = p
    return (np.hypot((x - cx) / a, (y - cy) / b) - 1) * min(a, b)


po = least_squares(ell_res, [960, 700, 320, 225], args=(ox, oy), loss="soft_l1").x
rho = np.hypot((ix - po[0]) / po[2], (iy - po[1]) / po[3])
sel = (rho < 1 - 12 / min(po[2], po[3])) & (rho > 1 - 34 / min(po[2], po[3]))
pi = least_squares(ell_res, [960, 700, 300, 205], args=(ix[sel], iy[sel]), loss="soft_l1").x
print(f"広間 外縁 {po.round(1)} 内縁 {pi.round(1)}")
cx, cy = num(r"centred at \((\d+), (\d+)\)", 1, int), num(r"centred at \((\d+), (\d+)\)", 2, int)
hr, vr = num(r"horizontal radius (\d+) px", 1, int), num(r"vertical radius (\d+) px", 1, int)
wt = num(r"low paper-clay WALL, (\d+) px thick", 1, int)
check("広間 中心x", (pi[0] + po[0]) / 2, cx, 3)
check("広間 中心y", (pi[1] + po[1]) / 2, cy, 3)
check("広間 横半径", pi[2], hr, 3)
check("広間 縦半径", pi[3], vr, 3)
check("壁厚(横)", po[2] - pi[2], wt, 2.5)
check("壁厚(縦)", po[3] - pi[3], wt, 2.5)

# ---- 壁の弧: ラベル付けで数え、方位を測る
lab, n = ndi.label(wall)
arcs = []
for i in range(1, n + 1):
    ys, xs = np.nonzero(lab == i)
    if len(xs) < 200:
        continue
    b = np.degrees(np.arctan2(xs - cx, -(ys - cy))) % 360
    if b.max() - b.min() > 180:  # 北をまたぐ場合
        b = np.where(b > 180, b - 360, b)
    arcs.append((b.min() % 360, b.max() % 360 if b.max() >= 0 else b.max() + 360, int(xs.min()), int(xs.max()), int(ys.min()), int(ys.max())))
arcs.sort()
nar = num(r"The wall is visible in (\d+) arcs only", 1, int)
check("壁の弧の数", len(arcs), nar, 0)
written = re.findall(r"arc: bearing (\d+) to (\d+) degrees \(x (\d+) to (\d+), y (\d+) to (\d+);", SEND)
for a, w in zip(arcs, sorted((tuple(map(int, t)) for t in written))):
    for k, nm in enumerate(("方位始", "方位終", "x0", "x1", "y0", "y1")):
        check(f"弧 {nm}", a[k], w[k], 2 if k < 2 else 3)
# 外周に地形が出ない（壁の中間の楕円を1度刻みで）
cnt_t = 0
for t in range(360):
    r = math.radians(t)
    x = round(cx + (hr + wt / 2) * math.sin(r)); y = round(cy - (vr + wt / 2) * math.cos(r))
    cnt_t += int(terr[y, x])
check("広間の外周で地形に当たる点（0なら外周は壁か通路の床だけ）", cnt_t, 0, 0)

# ---- 首（1本）: 行ごとの走査で、x=960 を含む床の連続区間の幅を全行で見る
ny0, ny1 = int(num(r"branch point, about \(\d+, (\d+)\)", 1, int)) + 100, cy - vr - 5
runs = []
for y in range(ny0, ny1):
    lab_r, n_r = ndi.label(fl[y, MX0:MX1])
    k = lab_r[960 - MX0]
    xs = np.nonzero(lab_r == k)[0] + MX0
    runs.append((xs.min(), xs.max(), n_r))
widths = {(a, b) for a, b, _ in runs}
print(f"首の行({len(runs)}行)の区間の種類: {sorted(widths)}")
check("首の幅(行ごとに一定か: 種類数)", len(widths), 1, 0)
nw = num(r"ONE single neck band (\d+) px wide", 1, int)
check("首の幅", list(widths)[0][1] - list(widths)[0][0], nw, 2)

# ---- 口の帯の斜め: 行ごとの走査（列の追跡とは別の方向）。下縁=行ごとの境界x、上縁も同様に行ごとの x で当てる
rows_lo, rows_up = [], []
for y in range(250, 420):
    lab_r, n_r = ndi.label(fl[y, 1080:1400])
    # 口の帯の床の連続区間のうち、y に応じた斜めの帯: 左端は首の東縁(1075)につながる区間
    k = lab_r[0] if lab_r[0] else 0
    if k:
        xs = np.nonzero(lab_r == k)[0] + 1080
        rows_lo.append((y, xs.max()))
for y in range(150, 190):
    lab_r, n_r = ndi.label(fl[y, 1076:1300])
    ks = [i for i in range(1, n_r + 1)]
    if ks:
        xs = np.nonzero(lab_r == ks[0])[0] + 1076
        rows_up.append((y, xs.min()))
# 下縁は 行 y ごとの右端 x（帯が斜めなので y が増えると x が減る）。傾き dy/dx の逆数から角度
ylo = np.array([r[0] for r in rows_lo if r[1] < 1385], float)
xlo = np.array([r[1] for r in rows_lo if r[1] < 1385], float)
yup = np.array([r[0] for r in rows_up], float)
xup = np.array([r[1] for r in rows_up], float)
a_lo = math.degrees(math.atan(abs(np.polyfit(xlo, ylo, 1)[0])))
a_up = math.degrees(math.atan(abs(np.polyfit(xup, yup, 1)[0])))
print(f"口の斜め 下縁{a_lo:.2f} 上縁{a_up:.2f}")
mang = num(r"at ([\d.]+) degrees above horizontal to about", 1, float)
check("口の斜めの角度(下縁)", a_lo, mang, 0.8)
check("口の斜めの角度(上縁)", a_up, mang, 0.8)
# 分岐点: 上縁・下縁の直線の中点が x=960 を通る y
ku, cu = np.polyfit(xup, yup, 1)
kl, cl = np.polyfit(xlo, ylo, 1)
jy = ((ku * 960 + cu) + (kl * 960 + cl)) / 2
check("分岐点 y（上縁と下縁の直線の中点が x=960 を通る高さ）", jy, num(r"branch point, about \(\d+, (\d+)\)", 1, int), 4)
# 首の東縁の開口 y 範囲
col = fl[:, 1077]
lab_c, _ = ndi.label(col[140:600])
k = lab_c[300 - 140]
ys = np.nonzero(lab_c == k)[0] + 140
check("開口 上端", ys.min(), num(r"opening of the mouth band spans y (\d+) to (\d+)", 1, int), 2)
check("開口 下端", ys.max(), num(r"opening of the mouth band spans y (\d+) to (\d+)", 2, int), 2)

# ---- 腕の斜め（行ごとの走査）
def arm_angle(y_rng, x_cols_fn, seed_fn):
    pts = []
    for y in y_rng:
        seg = fl[y, :]
        lab_r, n_r = ndi.label(seg)
        k = lab_r[seed_fn(y)]
        if not k:
            continue
        xs = np.nonzero(lab_r == k)[0]
        pts.append((y, xs.min(), xs.max()))
    return pts


# 右腕（西辺）: 下縁（床が終わる y）を列ごとに x 走査せず、行ごとに『帯の右端』ではなく、列ごとの下端を別法（ndimage.label の列ラベル）で
pts = []
for x in range(330, 470, 2):
    lab_c, _ = ndi.label(fl[:, x])
    k = lab_c[560]
    ys = np.nonzero(lab_c == k)[0]
    pts.append((x, ys.min(), ys.max()))
pa = np.array(pts, float)
ang_w = math.degrees(math.atan(abs(np.polyfit(pa[:, 0], pa[:, 2], 1)[0])))
check("右腕の斜め(下縁)", ang_w, num(r"sloping down and to the right at about ([\d.]+) degrees", 1, float), 0.8)
pts = []
for x in range(1350, 1600, 2):
    lab_c, _ = ndi.label(fl[:, x])
    k = lab_c[420]
    if not k:
        continue
    ys = np.nonzero(lab_c == k)[0]
    pts.append((x, ys.min(), ys.max()))
pa = np.array(pts, float)
ang_e = math.degrees(math.atan(abs(np.polyfit(pa[:, 0], pa[:, 2], 1)[0])))
check("左腕の斜め(下縁)", ang_e, num(r"sloping down and to the left at about ([\d.]+) degrees below horizontal into the hall of P4", 1, float), 0.8)

# ---- 追加（作り直し版の送信文で明記した折れ位置・肺と心臓の斜め）。別の方法: 列ごとの床の連続区間（ndimage.label）の下縁を直線に当て、帯の中心線は下縁から lw/2 だけ斜めに内側
LW = 230


def text_after(pat, group=1, cast=float):
    m_ = re.search(pat, SEND, re.S)
    if not m_:
        print(f"NG  送信文に {pat!r} が無い")
        bad.append(pat)
        return None
    return cast(m_.group(group))


def centre_shift(k):
    return (LW / 2) / math.cos(math.atan(abs(k)))


# 右腕・左腕の折れ位置（辺から水平に入る帯の中心線 y と斜めの中心線の交点）
pts_w = []
for x in range(330, 470, 2):
    lab_c, _ = ndi.label(fl[:, x])
    pts_w.append((x, np.nonzero(lab_c == lab_c[560])[0].max()))
kw, cw = np.polyfit(np.array(pts_w, float)[:, 0], np.array(pts_w, float)[:, 1], 1)
xr = (540 - (cw + 0.5 - centre_shift(kw))) / kw
tx = text_after(r"right-arm passage \(the person's own right arm\) at y.*?running straight to the right to about x (\d+)")
check("右腕の折れ位置 x", xr, tx, 6)
pts_e = []
for x in range(1350, 1600, 2):
    lab_c, _ = ndi.label(fl[:, x])
    k_ = lab_c[420]
    if k_:
        ys = np.nonzero(lab_c == k_)[0]
        pts_e.append((x, ys.max()))
ke, ce = np.polyfit(np.array(pts_e, float)[:, 0], np.array(pts_e, float)[:, 1], 1)
ye = (248 + 477) / 2
xl = (ye - (ce + 0.5 - centre_shift(ke))) / ke
tx = text_after(r"left-arm passage \(the person's own left arm\) at y.*?running straight to the left to about x (\d+)")
check("左腕の折れ位置 x", xl, tx, 6)


def lower_edge(xs, seed_y, y_hi=942):
    pts_ = []
    for x in xs:
        lab_c, _ = ndi.label(fl[:y_hi, x])
        k_ = lab_c[seed_y]
        if k_:
            pts_.append((x, np.nonzero(lab_c == k_)[0].max() + 0.5))
    pa_ = np.array(pts_, float)
    return np.polyfit(pa_[:, 0], pa_[:, 1], 1), len(pts_)


(kl_, cl_), n_l = lower_edge(range(692, 746), 840)
check("肺の斜め(下縁。列数)", n_l, 54, 3)
check("肺の斜め(下縁)", math.degrees(math.atan(abs(kl_))), text_after(r"lung passage at x.*?then sloping up and to the right at about ([\d.]+) degrees above horizontal"), 1.2)
yl = kl_ * 565 + cl_ - centre_shift(kl_)
check("肺の折れ位置 y", yl, text_after(r"lung passage at x.*?running straight up to about y (\d+)"), 6)
(kh_, ch_), n_h = lower_edge(range(1176, 1230), 840)
check("心臓の斜め(下縁。列数)", n_h, 54, 3)
check("心臓の斜め(下縁)", math.degrees(math.atan(abs(kh_))), text_after(r"heart passage at x.*?then sloping up and to the left at about ([\d.]+) degrees above horizontal"), 1.2)
yh = kh_ * 1354 + ch_ - centre_shift(kh_)
check("心臓の折れ位置 y", yh, text_after(r"heart passage at x.*?running straight up to about y (\d+)"), 6)
# 口の帯の折れ位置 y: 上縁・下縁の直線の中点が x=口の中心(1354) を通る高さ
ky_ = (((ku * 1354 + cu) + (kl * 1354 + cl)) / 2)
check("口の帯の折れ位置 y", ky_, text_after(r"mouth passage at x.*?running straight down to about y (\d+)"), 6)

print("\n全件一致" if not bad else f"\n不一致 {len(bad)} 件: {bad}")
sys.exit(1 if bad else 0)
