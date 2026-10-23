#!/usr/bin/env python3
"""BDY-01・03・05〜14 のonepass送信文（prompts/BDY-xx-prompt-send.txt）に書いた斜めの帯の角度・辺との交点・折れ点・合流点・丸い端を、
clean 割付図の画素から『別コード』で再測定して突き合わせる（BDY-02 の remeasure_bdy02.py と同じ方式）。
build_body_prompt.py（帯に直角な床の連続区間の中点列を直線に当てる）とは別の方法を使う:
  scipy.ndimage の距離変換（EDT）で帯の芯（EDT が通路幅/2 前後の細い画素列）を取り、主成分分析で直線に当てる。
種にするのは body_layout.py の折れ線だけ（本文の値は読まない）。本文は正規表現で数値を読んで照合する。

実行: uv run --with pillow --with numpy --with scipy python3 -I verification/body-layout/remeasure_body_diag.py [BDY-09 ...]
終了コード: 0=全件一致、1=不一致あり
"""
import importlib.util
import math
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

REPO = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("body_layout", REPO / ".claude/skills/sit-field-background/tools/body_layout.py")
bl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bl)
FLOOR = (232, 201, 168)
IDS = ["BDY-01", "BDY-03", "BDY-05", "BDY-06", "BDY-07", "BDY-08", "BDY-09", "BDY-10", "BDY-11", "BDY-12", "BDY-13", "BDY-14"]
bad = []


def check(name, ok, msg):
    print(f"{'OK ' if ok else 'NG '} {name}: {msg}")
    if not ok:
        bad.append(name)


def core_line(edt, p0, p1, lw):
    """p0→p1 の種の線の近く（12px以内）にある、EDT が lw/2 前後の芯の画素に直線を当てる。戻り値 (点, 向き, 本数)。"""
    ys, xs = np.nonzero((edt >= lw / 2 - 1.5) & (edt <= lw / 2 + 2.5))
    P = np.c_[xs, ys].astype(float)
    a, b = np.array(p0, float), np.array(p1, float)
    d = (b - a) / np.linalg.norm(b - a)
    n = np.array([-d[1], d[0]])
    rel = P - a
    dist = np.abs(rel @ n)
    t = rel @ d
    L = np.linalg.norm(b - a)
    sel = (dist <= 12) & (t >= 0) & (t <= L)
    # 辺の近くは EDT が欠けるので、模型の縁から lw/2 以上離れた芯だけ使う
    X0, Y0, X1, Y1 = bl.MX0, bl.MY0, bl.MX1, bl.MY1
    sel &= (P[:, 0] > X0 + lw / 2) & (P[:, 0] < X1 - lw / 2) & (P[:, 1] > Y0 + lw / 2) & (P[:, 1] < Y1 - lw / 2)
    Q = P[sel]
    if len(Q) < 20:
        return None
    mu = Q.mean(0)
    u, s, vt = np.linalg.svd(Q - mu)
    dd = vt[0] if vt[0] @ d > 0 else -vt[0]
    return mu, dd, len(Q)


def inter(l1, l2):
    A = np.array([l1[1], -l2[1]]).T
    s = np.linalg.solve(A, l2[0] - l1[0])
    return l1[0] + l1[1] * s[0]


for mid in (sys.argv[1:] or IDS):
    send = (REPO / f"verification/body-layout/prompts/{mid}-prompt-send.txt").read_text(encoding="utf-8")
    body = send.split("=== WHAT TO DRAW", 1)[1].split("P5. ", 1)[0]
    im = np.asarray(Image.open(REPO / f"verification/body-layout/clean/{mid}.png").convert("RGB"))
    fl = (im == FLOOR).all(2)
    edt = ndi.distance_transform_edt(fl)
    rows, ev, nodes, svg_edges, portals = bl.build_model()
    lw = int(round(bl.DEFAULT_MAIN_WIDTH_RATIO * bl.MW))
    quoted_angles = [float(x) for x in re.findall(r"at about ([0-9.]+) degrees (?:above|below) horizontal", body)]
    quoted_pts = [(int(a), int(b)) for a, b in re.findall(r"\((\d+), (\d+)\) \(in 1672x941", body)]
    lines = []
    for kind, pts, isp in bl.resolve_paths(mid, portals):
        for a, b in zip(pts, pts[1:]):
            ln = core_line(edt, a, b, lw)
            if ln is None:
                # 短い区間（BDY-03 の垂直な帯など）は芯が少ない。EDT の条件を緩めずに NG とする
                check(f"{mid} 区間", False, f"{a}→{b} の芯の画素が足りない")
                continue
            ang = math.degrees(math.atan2(abs(ln[1][1]), abs(ln[1][0])))
            lines.append((ln, ang))
    for ln, ang in lines:
        if ang > 89.0:
            continue  # 垂直は本文に角度を書かない（'straight down' と x 範囲）
        ok = any(abs(ang - q) <= 0.8 for q in quoted_angles)
        check(f"{mid} 角度", ok, f"芯の実測 {ang:.2f}度 / 本文 {quoted_angles}（許容±0.8）")
    # 本文の点: 辺との交点 / 折れ点・合流点（直線どうしの交点）/ 末端の丸い端（直線上）
    X0, Y0, X1, Y1 = bl.MX0, bl.MY0, bl.MX1, bl.MY1
    cands = []
    for ln, _ in lines:
        mu, d = ln[0], ln[1]
        for s, v in (("x", X0), ("x", X1), ("y", Y0), ("y", Y1)):
            if abs(d[0 if s == "x" else 1]) > 1e-6:
                tt = (v - mu[0 if s == "x" else 1]) / d[0 if s == "x" else 1]
                cands.append(mu + d * tt)
    for i in range(len(lines)):
        for j in range(i + 1, len(lines)):
            try:
                cands.append(inter(lines[i][0], lines[j][0]))
            except np.linalg.LinAlgError:
                pass
    for q in quoted_pts:
        qq = np.array(q, float)
        if any(np.linalg.norm(qq - c) <= 6 for c in cands):
            check(f"{mid} 点 {q}", True, "縁との交点または折れ点・合流点に一致（6px以内）")
            continue
        # 末端の丸い端: 直線上（4px以内）で、中心は床・最奥はその先が床でない
        on = [abs((qq - ln[0][0]) @ np.array([-ln[0][1][1], ln[0][1][0]])) for ln in lines]
        qx, qy = int(qq[0]), int(qq[1])
        if not fl[qy, qx]:  # 2本の間の地形のくさびの先端: 点は地形で、真上と真下の近く（30px以内）に床がある
            ok = bool(fl[qy - 30:qy, qx].any() and fl[qy + 1:qy + 31, qx].any())
            check(f"{mid} 点 {q}", ok, "くさびの先端: 点は地形で、上下の近くに床がある" if ok else "床でも先端でもない")
            continue
        ok = bool(on) and min(on) <= 4
        check(f"{mid} 点 {q}", ok, f"末端の丸い端の点: 直線からの距離 {min(on) if on else float('nan'):.1f}px、床={bool(fl[int(qq[1]), int(qq[0])])}")
print("全件一致" if not bad else f"不一致 {len(bad)} 件: {bad}")
sys.exit(1 if bad else 0)
