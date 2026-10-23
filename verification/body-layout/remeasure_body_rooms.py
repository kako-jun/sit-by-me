#!/usr/bin/env python3
"""BDY-04（迷路）・BDY-15（胃のJ字の1袋）・BDY-16（心臓の4部屋）・BDY-17（肺・案Aの外周の環）の onepass 送信文（prompts/BDY-xx-prompt-send.txt）に書いた
座標・半径・通路の列挙・数（通路の本数・行き止まり・T字・曲がり）を、clean 割付図の画素から『別コード』で再測定して突き合わせる
（remeasure_body_diag.py・remeasure_bdy02.py と同じ方式）。
build_body_prompt.py（床の連続区間・最大内接円の探索・格子の走査）とは別の方法を使う:
  - 迷路: 送信文の『横の連なり・縦の連なり』だけから通路の中心線の集合を作り、『中心線からの距離 <= 38.5px』で床を描き直して clean の床と比べる
    （輪郭から2px以内の差は丸め）。接続・木・数（通路・曲がり・T字・行き止まり）も送信文の列挙から数え直し、本文の数と照合。壁の厚みは地形の距離変換で測る。
  - 胃: 距離変換（scipy EDT）で制御点の半径、列ごとの床の区間は np.diff で、先端・最下点は床画素の極値で測る。
  - 心臓・肺: 部屋は境界画素への円の最小二乗当てはめ（代数的当てはめ）、環の通路は行/列の床の区間（np.diff）、島は地形の連結成分（ndimage.label）の外接枠。
種にするのは送信文の本文の数値（正規表現で読む）。body_layout.py の値は読まない。

実行: uv run --with pillow --with numpy --with scipy python3 -I verification/body-layout/remeasure_body_rooms.py [BDY-04 ...]
終了コード: 0=全件一致、1=不一致あり
"""
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

REPO = Path(__file__).resolve().parents[2]
FLOOR, TERR = (232, 201, 168), (170, 130, 110)
IDS = ["BDY-04", "BDY-15", "BDY-16", "BDY-17"]
bad = []


def check(name, ok, msg):
    print(f"{'OK ' if ok else 'NG '} {name}: {msg}")
    if not ok:
        bad.append(name)


def load(mid):
    a = np.asarray(Image.open(REPO / f"verification/body-layout/clean/{mid}.png").convert("RGB"))
    return (a == FLOOR).all(2), (a == TERR).all(2)


def p4_of(mid):
    send = (REPO / f"verification/body-layout/prompts/{mid}-prompt-send.txt").read_text(encoding="utf-8")
    body = send.split("=== WHAT TO DRAW", 1)[1]
    p4 = re.search(r"\nP4\. .*?(?=\nP5\. )", body, re.S).group(0)
    p3 = re.search(r"\nP3\. .*?(?=\nP4\. )", body, re.S).group(0)
    p10 = re.search(r"\nP10\. .*?(?=\nP11\. )", body, re.S).group(0)
    return p3, p4, p10


def spans(v):
    """真偽列の True の連続区間 (始, 終)。np.diff で数える（ビルダーの runs_of とは別の書き方）。"""
    d = np.diff(np.r_[0, v.astype(np.int8), 0])
    return list(zip(np.nonzero(d == 1)[0].tolist(), (np.nonzero(d == -1)[0] - 1).tolist()))


def dist_to_segments(shape, segs):
    """各画素から、線分の集合への最短距離（全画素）。線分は (x0,y0,x1,y1)。"""
    yy, xx = np.mgrid[0:shape[0], 0:shape[1]].astype(np.float32)
    best = np.full(shape, 1e9, np.float32)
    for x0, y0, x1, y1 in segs:
        dx, dy = x1 - x0, y1 - y0
        L2 = dx * dx + dy * dy
        t = np.clip(((xx - x0) * dx + (yy - y0) * dy) / (L2 if L2 else 1), 0, 1)
        d = np.hypot(xx - (x0 + t * dx), yy - (y0 + t * dy))
        best = np.minimum(best, d)
    return best


def fit_circle(x, y):
    A = np.c_[2 * x, 2 * y, np.ones(len(x))]
    b = x * x + y * y
    cx, cy, c = np.linalg.lstsq(A, b, rcond=None)[0]
    return cx, cy, float(np.sqrt(c + cx * cx + cy * cy))


def room_circle(fl, cx, cy, r, win=6):
    """境界画素（床と地形の境）のうち、期待円の近く（半径方向 ±win px）にあるものへ円を当てる。"""
    edge = fl & ~ndi.binary_erosion(fl, structure=np.ones((3, 3)))
    ys, xs = np.nonzero(edge)
    d = np.hypot(xs - cx, ys - cy)
    sel = np.abs(d - r) < win
    cx2, cy2, r2 = fit_circle(xs[sel].astype(float), ys[sel].astype(float))
    for _ in range(4):  # 外れ（通路が部屋に接する所）を捨てて当て直す
        d = np.hypot(xs - cx2, ys - cy2)
        sel = np.abs(d - r2) < 1.5
        cx2, cy2, r2 = fit_circle(xs[sel].astype(float), ys[sel].astype(float))
    return cx2, cy2, r2, int(sel.sum())


def maze(mid):
    fl, terr = load(mid)
    p3, p4, _ = p4_of(mid)
    lw = int(re.search(r"Every corridor is exactly (\d+) px wide", p4).group(1))
    pitch = int(re.search(r"neighbouring grid cells are (\d+) px apart", p4).group(1))
    x0, y0 = map(int, re.search(r"x = (\d+) \+ \d+ c and y = (\d+) \+", p4).groups())
    C, R = map(int, re.search(r"grid of (\d+) columns by (\d+) rows", p4).groups())
    X = lambda c: x0 + c * pitch
    Y = lambda r: y0 + r * pitch
    hsec = p4.split("Horizontal runs", 1)[1].split("Vertical runs", 1)[0]
    vsec = p4.split("Vertical runs", 1)[1].split("Each run is", 1)[0]
    segs, links = [], set()
    for m_ in re.finditer(r"row (\d+) \(y (\d+)\): (.*)", hsec):
        r, y = int(m_.group(1)), int(m_.group(2))
        assert y == Y(r)
        for a, b in re.findall(r"x (\d+) to (\d+)", m_.group(3)):
            ca, cb = (int(a) - x0) // pitch, (int(b) - x0) // pitch
            segs.append((int(a), y, int(b), y))
            for c in range(ca, cb):
                links.add(((c, r), (c + 1, r)))
    for m_ in re.finditer(r"column (\d+) \(x (\d+)\): (.*)", vsec):
        c, x = int(m_.group(1)), int(m_.group(2))
        assert x == X(c)
        for a, b in re.findall(r"y (\d+) to (\d+)", m_.group(3)):
            ra, rb = (int(a) - y0) // pitch, (int(b) - y0) // pitch
            segs.append((x, int(a), x, int(b)))
            for r in range(ra, rb):
                links.add(((c, r), (c, r + 1)))
    ex0, ex1 = map(int, re.search(r"entrance band comes in from the south edge at x (\d+) to (\d+)", p4).groups())
    root = tuple(map(int, re.search(r"cell in column (\d+), row (\d+)", p4).groups()))
    segs.append((X(root[0]), Y(root[1]), X(root[0]), 942))
    # 1. 列挙から床を描き直して clean と比べる（輪郭から2px超離れた不一致が0）
    dist = dist_to_segments(fl.shape, segs)
    rec = dist <= lw / 2
    box = np.zeros_like(fl)
    box[138:942, 138:1782] = True
    edge = (fl ^ ndi.binary_erosion(fl)) | (fl ^ ndi.binary_dilation(fl))
    band = ndi.binary_dilation(edge, iterations=2)
    resid = int(((rec ^ fl) & box & ~band).sum())
    check(f"{mid} 通路の列挙", resid <= 20, f"本文の連なりから描き直した床と clean の床の、輪郭から2px超離れた不一致 {resid} 画素（0に近いほど列挙が全通路を過不足なく覆う）")
    # 2. 接続の数え直し
    adj = {}
    for a, b in links:
        adj.setdefault(a, set()).add(b)
        adj.setdefault(b, set()).add(a)
    nlink = int(re.search(r"joined by (\d+) corridor links", p4).group(1))
    check(f"{mid} 通路の本数", len(links) == nlink == C * R - 1 and len(adj) == C * R, f"列挙から {len(links)} 本・セル {len(adj)}（本文 {nlink}・格子 {C * R}）。木（本数=セル数-1）")
    seen, st = {root}, [root]
    while st:
        c = st.pop()
        for n in adj[c]:
            if n not in seen:
                seen.add(n)
                st.append(n)
    check(f"{mid} 連結・ループなし", len(seen) == C * R, f"入口のセルから全{len(seen)}セルへ到達（木なのでループなし）")
    deg = {c: len(adj[c]) + (1 if c == root else 0) for c in adj}
    dead = sorted([(X(c), Y(r)) for (c, r), d in deg.items() if d == 1], key=lambda p: (p[1], p[0]))
    tj = sorted([(X(c), Y(r)) for (c, r), d in deg.items() if d >= 3], key=lambda p: (p[1], p[0]))
    corners = 0
    for (c, r), d in deg.items():
        if d == 2:
            nn = [(n[0] - c, n[1] - r) for n in adj[(c, r)]] + ([(0, 1)] if (c, r) == root else [])
            if nn[0][0] + nn[1][0] != 0 or nn[0][1] + nn[1][1] != 0:
                corners += 1
    q_dead = [tuple(map(int, t)) for t in re.findall(r"\((\d+), (\d+)\)", p4.split("dead ends, each", 1)[1].split("There is no crossing", 1)[0].split("at the cell centres", 1)[1])]
    q_tj = [tuple(map(int, t)) for t in re.findall(r"\((\d+), (\d+)\)", p4.split("T-junctions", 1)[1].split("dead ends, each", 1)[0])]
    q_corner = int(re.search(r"(\d+) bends", p4).group(1))
    check(f"{mid} 行き止まり", dead == sorted(q_dead, key=lambda p: (p[1], p[0])) and len(dead) == int(re.search(r"(\d+) dead ends", p4).group(1)), f"{len(dead)}か所 {dead}")
    check(f"{mid} T字", tj == sorted(q_tj, key=lambda p: (p[1], p[0])), f"{len(tj)}か所 {tj}")
    check(f"{mid} 曲がり", corners == q_corner, f"列挙から {corners}（本文 {q_corner}）")
    # 3. 行き止まりが丸い閉じた端（先の床が無く、中心から先 lw/2 まで床・その先は地形）
    ok = True
    for (x, y) in dead:
        ch = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        nb = [(dx, dy) for dx, dy in ch if (X((x - x0) // pitch + dx), Y((y - y0) // pitch + dy)) in [] or True]
        # 先端: どちらの向きに床が続くかは列挙から。繋がる向きの反対へ lw/2 の所が床の縁
        c, r = (x - x0) // pitch, (y - y0) // pitch
        n = next(iter(adj[(c, r)]))
        dx, dy = c - n[0], r - n[1]
        fx, fy = x + dx * (lw // 2 - 2), y + dy * (lw // 2 - 2)
        gx, gy = x + dx * (lw // 2 + 4), y + dy * (lw // 2 + 4)
        if not (fl[fy, fx] and not fl[gy, gx]):
            ok = False
    check(f"{mid} 行き止まりの丸い端", ok, f"{len(dead)}か所とも、中心から先 {lw // 2 - 2}px は床・{lw // 2 + 4}px 先は地形")
    # 4. 壁の厚み: 接続しない隣セルの間の地形の距離変換の山
    et = ndi.distance_transform_edt(terr)
    gaps = []
    for c in range(C):
        for r in range(R):
            for dc, dr in ((1, 0), (0, 1)):
                n = (c + dc, r + dr)
                if n[0] < C and n[1] < R and ((c, r), n) not in links:
                    mx, my = (X(c) + X(n[0])) // 2, (Y(r) + Y(n[1])) // 2
                    gaps.append(float(et[my - 4:my + 5, mx - 4:mx + 5].max()) * 2)
    q_gap = int(re.search(r"wall of terrain at least (\d+) px thick", p4).group(1))
    check(f"{mid} 壁の厚み", abs(min(gaps) - q_gap) <= 3, f"接続しない隣セルの間の壁の厚み 距離変換の山×2 の最小 {min(gaps):.1f}px（本文 {q_gap}）")
    # 5. 入口と外周の枠
    row = spans(fl[940, :])
    ok_ent = len(row) == 1 and abs(row[0][0] - ex0) <= 1 and abs(row[0][1] - ex1) <= 1
    check(f"{mid} 入口", ok_ent, f"南辺（縁の内側2px）の床区間 {row}（本文 x{ex0}-{ex1}）")
    left = min(np.nonzero(fl[:, 138:300].any(0))[0]) + 138 - 138
    check(f"{mid} 外周の枠", abs(left - 63) <= 2, f"模型の縁から最も外側の通路の縁まで {left}px（本文 about 63）")
    _red(mid, terr, p4_of(mid)[2], 15)  # 赤紙 約30px の半径


def _red(mid, terr, p10, rad):
    seg = p10.split("centred at about:", 1)[1].split("(six in total)", 1)[0]  # 迷路は 1672 併記なし（2026-10-22 の字数削減）。座標だけを拾う
    seg = re.sub(r"\(in 1672x941: \(\d+, \d+\)\)", "", seg)
    pts = [tuple(map(int, t)) for t in re.findall(r"\((\d+), (\d+)\)", seg)]
    # 赤紙の中心: 全て地形の上で、周囲 rad px（紙の半径）が地形
    ok = len(pts) == 6 and all(terr[y - rad:y + rad + 1, x - rad:x + rad + 1].all() for x, y in pts)
    check(f"{mid} 赤紙6枚", ok, f"本文の中心 {len(pts)}個。周囲{rad}pxの正方形が全て地形: " + ", ".join("OK" if terr[y - rad:y + rad + 1, x - rad:x + rad + 1].all() else f"NG{(x, y)}" for x, y in pts))
    # 床の縁・仕切りからの距離（赤紙の半分＋仕切り＋毛糸の余白）: 迷路36px以上・他50px以上（床の画素までの距離変換）
    fl_, _t = load(mid)
    need = 36 if mid == "BDY-04" else 50
    ef = ndi.distance_transform_edt(~fl_)
    dd = [float(ef[y, x]) for x, y in pts]
    check(f"{mid} 赤紙と床の距離", len(dd) == 6 and min(dd) >= need, f"床までの距離 " + ", ".join(f"{v:.0f}" for v in dd) + f"（最小 {min(dd):.0f}px。必要 {need}px以上）")


def sac(mid):
    fl, terr = load(mid)
    p3, p4, p10 = p4_of(mid)
    edt = ndi.distance_transform_edt(fl)
    ctl = re.findall(r"\((\d+), (\d+)\) with a half-width of about (\d+) px", p4)
    for x, y, r in ctl:
        x, y, r = int(x), int(y), int(r)
        # 制御点の位置そのものでの床の距離変換 = 床の外までの距離。本文の半径と±3px
        check(f"{mid} 半幅 ({x},{y})", abs(float(edt[y, x]) - r) <= 3.5, f"距離変換 {edt[y, x]:.1f}px（本文 {r}）")
    prof = re.findall(r"x (\d+) \(in 1672x941: \d+\): y (\d+) to (\d+) \(in 1672x941", p4)
    okp = True
    for x, a, b in prof:
        x, a, b = int(x), int(a), int(b)
        s = spans(fl[:, x])
        if not (len(s) == 1 and s[0] == (a, b)):
            okp = False
            print(f"   x={x}: 本文 {a}-{b} / 実測 {s}")
    check(f"{mid} 列ごとの床の区間", okp and len(prof) >= 20, f"{len(prof)}列を np.diff で再測定")
    ys, xs = np.nonzero(fl)
    tip = tuple(map(int, re.search(r"whose farthest point is at about \((\d+), (\d+)\)", p4).groups()))
    check(f"{mid} 先端", abs(int(xs.max()) - tip[0]) <= 3 and abs(float(ys[xs == xs.max()].mean()) - tip[1]) <= 3, f"最右の床画素 ({xs.max()}, {ys[xs == xs.max()].mean():.0f})（本文 {tip}）")
    low = tuple(map(int, re.search(r"whose lowest point is at about \((\d+), (\d+)\)", p4).groups()))
    check(f"{mid} 最下点", abs(int(ys.max()) - low[1]) <= 3 and abs(float(xs[ys == ys.max()].mean()) - low[0]) <= 12, f"最下の床画素 ({xs[ys == ys.max()].mean():.0f}, {ys.max()})（本文 {low}・最下の点は平らなので x は ±12）")
    ent = tuple(map(int, re.search(r"entrance band is \d+ px wide \(y (\d+) to (\d+) at the west edge", p4).groups()))
    s = spans(fl[:, 140])
    check(f"{mid} 入口", len(s) == 1 and s[0] == ent, f"西辺（縁の内側2px）の床区間 {s}（本文 y{ent[0]}-{ent[1]}）")
    lab, n = ndi.label(fl)
    check(f"{mid} 床は1つの袋", n == 1, f"床の連結成分 {n}")
    _red(mid, terr, p10, 22)


def rooms(mid):
    fl, terr = load(mid)
    p3, p4, p10 = p4_of(mid)
    pts = [(int(a), int(b)) for a, b in re.findall(r"\((\d+), (\d+)\) \(in 1672x941", p4)]
    if mid == "BDY-16":
        rs = int(re.search(r"round floor of radius (\d+) px", p4).group(1))
        cs = [tuple(map(int, t)) for t in re.findall(r"(?:centred at|room at) \((\d+), (\d+)\)", p4)]
        cs = cs[:4]
        rr = [rs] * 4
    else:
        rs1 = int(re.search(r"Three smaller rooms of radius (\d+) px", p4).group(1))
        rs2 = int(re.search(r"two larger rooms of radius (\d+) px", p4).group(1))
        sec = p4.split("THE FIVE ROOMS", 1)[1].split("THE ENTRANCE", 1)[0]
        cs = [tuple(map(int, t)) for t in re.findall(r"\((\d+), (\d+)\) \(in 1672x941", sec)]
        rr = [rs1] * 3 + [rs2] * 2
    for (cx, cy), r in zip(cs, rr):
        x2, y2, r2, n = room_circle(fl, cx, cy, r)
        check(f"{mid} 部屋 ({cx},{cy})", abs(x2 - cx) <= 2.5 and abs(y2 - cy) <= 2.5 and abs(r2 - r) <= 2.5, f"円当てはめ 中心({x2:.1f},{y2:.1f}) 半径{r2:.1f}（本文 ({cx},{cy}) {r}。境界{n}画素）")
    if mid == "BDY-16":
        sp = lambda pat: tuple(map(int, re.search(pat, p4).groups()))
        top = sp(r"top passage between the two upper rooms runs along y (\d+) to (\d+)")
        bot = sp(r"bottom passage between the two lower rooms along y (\d+) to (\d+)")
        lef = sp(r"left passage between the two left rooms along x (\d+) to (\d+)")
        rig = sp(r"right passage between the two right rooms along x (\d+) to (\d+)")
        isl = tuple(map(int, re.search(r"x (\d+) to (\d+) and y (\d+) to (\d+) \(\d+ x \d+ px", p4).groups()))
        xm, ym = (cs[0][0] + cs[2][0]) // 2, (cs[0][1] + cs[1][1]) // 2
        got = dict(top=spans(fl[:, xm])[0], bot=spans(fl[:, xm])[-1], lef=[s for s in spans(fl[ym, :]) if s[0] < xm][0], rig=[s for s in spans(fl[ym, :]) if s[0] > xm][0])
        # 通路の区間: 列/行を走査して、本文の区間を含む1区間
        sx_ = spans(fl[:, xm])
        sy_ = spans(fl[ym, :])
        ok = (top in sx_ and bot in sx_ and lef in sy_ and rig in sy_)
        check(f"{mid} 環の通路", ok, f"列 x={xm} の床の区間 {sx_}・行 y={ym} の床の区間 {sy_}（本文 上{top}・下{bot}・左{lef}・右{rig}）")
        lab, n = ndi.label(terr)
        sizes = ndi.sum(terr, lab, range(1, n + 1))
        k = int(np.argsort(sizes)[0]) + 1  # 小さい方が島
        ys, xs = np.nonzero(lab == k)
        bb = (int(xs.min()), int(xs.max()), int(ys.min()), int(ys.max()))
        check(f"{mid} 島", bb == isl, f"地形の連結成分（小）の外接枠 x{bb[0]}-{bb[1]} y{bb[2]}-{bb[3]}（本文 {isl}）")
        e0, e1 = tuple(map(int, re.search(r"entrance band \(x (\d+) to (\d+)", p4).groups()))
        s = spans(fl[140, :])
        check(f"{mid} 入口", s == [(e0, e1)], f"北辺（縁の内側2px）の床区間 {s}（本文 x{e0}-{e1}）")
    else:
        sp = lambda pat: tuple(map(int, re.search(pat, p4).groups()))
        ring = re.search(r"along y (\d+) \(top; floor y (\d+) to (\d+)\), y (\d+) \(bottom; floor y (\d+) to (\d+)\), x (\d+) \(left; floor x (\d+) to (\d+)\) and x (\d+) \(right; floor x (\d+) to (\d+)\)", p4).groups()
        yt, t0, t1, yb, b0, b1, xl, l0, l1, xr, r0, r1 = map(int, ring)
        xm = (xl + 960) // 2 + 50
        got = [spans(fl[:, xm]), spans(fl[:, 960]), spans(fl[(cs[0][1] + cs[1][1]) // 2, :]), spans(fl[(cs[3][1] + cs[4][1]) // 2, :])]
        ok = (t0, t1) in got[0] and (b0, b1) in got[1] and (l0, l1) in got[2] and (r0, r1) in got[3]
        check(f"{mid} 環の通路", ok, f"上{(t0, t1)}・下{(b0, b1)}・左{(l0, l1)}・右{(r0, r1)}（行/列の np.diff の区間と照合。幅{t1 - t0 + 1}px）")
        isl = tuple(map(int, re.search(r"spanning x (\d+) to (\d+) and y (\d+) to (\d+)", p4).groups()))
        lab, n = ndi.label(terr)
        sizes = ndi.sum(terr, lab, range(1, n + 1))
        k = int(np.argsort(sizes)[0]) + 1
        ys, xs = np.nonzero(lab == k)
        bb = (int(xs.min()), int(xs.max()), int(ys.min()), int(ys.max()))
        check(f"{mid} 島", bb == isl, f"地形の連結成分（小）の外接枠 x{bb[0]}-{bb[1]} y{bb[2]}-{bb[3]}（本文 {isl}）")
        e0, e1 = tuple(map(int, re.search(r"entrance band \(x (\d+) to (\d+),", p4).groups()))
        s = spans(fl[140, :])
        check(f"{mid} 入口", s == [(e0, e1)], f"北辺（縁の内側2px）の床区間 {s}（本文 x{e0}-{e1}）")
        # T字: 入口の真下で環の上辺に合流（上辺の中心線上が床で、入口の x の列は y=yt まで連続）
        col = spans(fl[:, 960])
        check(f"{mid} T字", any(a <= 140 and b >= yt + 30 for a, b in col), f"入口の列 x960 の床区間 {col[:2]}（北辺から環の上辺 y{yt} を越える）")
    _red(mid, terr, p10, 22)


for mid in (sys.argv[1:] or IDS):
    {"BDY-04": maze, "BDY-15": sac, "BDY-16": rooms, "BDY-17": rooms}[mid](mid)
print("全件一致" if not bad else f"不一致 {len(bad)} 件: {bad}")
sys.exit(1 if bad else 0)
