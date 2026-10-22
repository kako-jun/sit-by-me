#!/usr/bin/env python3
"""体内 BDY-01..17（+ BDY-17 仮案B）の一覧画像 contact-sheet.png を作る。

各 MAP の割付図（body_layout.py の出力 BDY-xx.png。通常版）を体の配置（頭=上・手=左右上・足=左右下・胴=中央）に並べ、
接続線を『出る辺の位置 → 入る辺の位置』で結ぶ（body_layout.py の接続モデルと同じ辺・位置。線は図の下を通り、辺の出入口の点で止まる）。
BDY-17 は仮案A（外周の環）と仮案B（渦巻き）を並べ、BDY-02 の肺からどちらへも線を引く。

実行（先に body_layout.py で BDY-xx.png を作っておく）:
  uv run --with pillow --with numpy python3 -I body_sheet.py [--src DIR] [--out contact-sheet.png]
  既定の src/out は verification/body-layout/ 。
"""
import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
import body_layout as b  # noqa: E402

# (列, 行): 体の配置。BDY-02 の南辺（肺=左寄り・下半身・心臓=右寄り。確定）から出る3本は row4 の 17・03・16 の北辺へ入る。
POS = {"BDY-04": (2, 0),
       "BDY-08": (0, 1), "BDY-06": (4, 1),
       "BDY-07": (1, 2), "BDY-01": (2, 2), "BDY-05": (3, 2),
       "BDY-02": (2, 3),
       "BDY-17-B": (0, 4), "BDY-17": (1, 4), "BDY-03": (2, 4), "BDY-16": (3, 4),
       "BDY-15": (3, 5),
       "BDY-12": (1, 6), "BDY-09": (3, 6),
       "BDY-13": (0, 7), "BDY-10": (4, 7),
       "BDY-14": (0, 8), "BDY-11": (4, 8)}
TW, TH, G, M, TOP = 740, 416, 80, 50, 110
COLS, ROWS = 5, 9
PALETTE = [(230, 110, 110), (110, 170, 235), (120, 205, 120), (240, 180, 70), (185, 130, 225), (70, 205, 205), (235, 125, 175), (200, 200, 110)]
LABEL = {"BDY-17": "【仮案A 外周の環】", "BDY-17-B": "【仮案B 渦巻き】"}
PROV = ("BDY-04", "BDY-15", "BDY-16")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=str(b.REPO / "verification/body-layout"))
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    src = Path(a.src)
    out = Path(a.out) if a.out else src / "contact-sheet.png"
    Wd = M * 2 + COLS * TW + (COLS - 1) * G
    Ht = TOP + M + ROWS * TH + (ROWS - 1) * G
    im = Image.new("RGB", (Wd, Ht), (24, 24, 30))
    d = ImageDraw.Draw(im)
    F = lambda s: ImageFont.truetype(b.FONT, s, index=0)
    d.text((Wd / 2, 36), "体内 BDY-01..17 割付図 一覧（左右は身体の本人から見る=画面左が右手。BDY-17 は仮案A/B 併記）", font=F(48), fill=(240, 240, 240), anchor="mm")
    d.text((Wd / 2, 84), "色付きの線=接続（出る辺の位置→入る辺の位置、点=模型の縁の出入口）。線は図の下を通る。【仮案】=保留4枚の内部の形", font=F(30), fill=(200, 200, 210), anchor="mm")
    org = lambda m: (M + POS[m][0] * (TW + G), TOP + POS[m][1] * (TH + G))
    rows_, ev, nodes, sv, portals = b.build_model()
    sc = TW / b.W

    def port_xy(m, p):
        """tile 境界上の出入口の点と外向きの単位ベクトル。"""
        dd = portals[m][p]
        ex, ey = b.edge_point(dd["side"], dd["slot"])
        ox, oy = org(m)
        s = dd["side"]
        if s == "N": return (ox + ex * sc, oy), (0, -1)
        if s == "S": return (ox + ex * sc, oy + TH), (0, 1)
        if s == "W": return (ox, oy + ey * sc), (-1, 0)
        return (ox + TW, oy + ey * sc), (1, 0)

    def key17(m, variant):  # 接続表上の BDY-17 は仮案A/Bの両方の tile に引く
        return "BDY-17-B" if (m == "BDY-17" and variant == "B") else m

    conns = []
    for ra, rap, rb_, rbp in [(r[0], r[1], r[2], r[3]) for r in rows_]:
        a_, b_ = (ra, rb_)
        # body_layout.build_model と同じ親子の向き（BDY-01 の行は BDY-02 側が出る）
        if (ra, rb_) in b.PARENT_OVERRIDE:
            ra, rap, rb_, rbp = rb_, rbp, ra, rap
        conns.append((ra, rap, rb_, rbp, "A"))
        if rb_ == "BDY-17":
            conns.append((ra, rap, rb_, rbp, "B"))
    for i, (ra, rap, rb_, rbp, var) in enumerate(conns):
        col = PALETTE[i % len(PALETTE)]
        lane = (i % 5 - 2) * 8
        ta, tb = ra, key17(rb_, var)
        (x0, y0), n0 = port_xy(ra, rap)
        (x1, y1), n1 = port_xy(rb_, rbp)
        if tb != rb_:
            x1 += org(tb)[0] - org(rb_)[0]; y1 += org(tb)[1] - org(rb_)[1]
        L = 30 + abs(lane) // 2
        p0 = (x0 + n0[0] * L, y0 + n0[1] * L)
        p1 = (x1 + n1[0] * L, y1 + n1[1] * L)
        if n0[1]:   # 出る辺が N/S: 縦へ出て、タイル間の横の隙間で横移動
            ym = y0 + n0[1] * (G / 2 + lane)
            pts = [(x0, y0), (x0, ym), (x1, ym), (x1, y1)] if n1[1] else [(x0, y0), p0, p1, (x1, y1)]
        else:       # E/W: 横へ出て、列の隙間で縦移動
            xm = x0 + n0[0] * (G / 2 + lane)
            pts = [(x0, y0), (xm, y0), (xm, y1), (x1, y1)] if n1[0] else [(x0, y0), p0, p1, (x1, y1)]
        d.line(pts, fill=col, width=8, joint="curve")
        for (x, y) in ((x0, y0), (x1, y1)):
            d.ellipse([x - 9, y - 9, x + 9, y + 9], fill=col, outline=(20, 20, 20), width=2)
    for m in POS:
        x, y = org(m)
        t = Image.open(src / f"{m}.png").convert("RGB").resize((TW, TH), Image.LANCZOS)
        im.paste(t, (x, y))
        d.rectangle([x - 1, y - 1, x + TW, y + TH], outline=(200, 200, 200), width=2)
        base = m.replace("-B", "")
        tag = "  " + LABEL[m] if m in LABEL else "  【仮案】" if base in PROV else ""
        txt = f"{m}  {b.NAMES[base]}{tag}"
        f = F(32)
        w = d.textlength(txt, font=f)
        d.rectangle([x + 8, y + 6, x + 8 + w + 20, y + 6 + 46], fill=(24, 24, 30))
        d.text((x + 18, y + 29), txt, font=f, fill=(250, 250, 250), anchor="lm")
    im.save(out)
    print(out, im.size)


if __name__ == "__main__":
    main()
