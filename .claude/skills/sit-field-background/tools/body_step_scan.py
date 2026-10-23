#!/usr/bin/env python3
"""体内 clean 画像の『段差』検査（報告用）。床の輪郭を多角形に近似し、短い水平/垂直の辺(8〜150px)の前後で
輪郭が逆向きに約90度ずつ曲がる Z 形の食い違い（= 帯の端の平らな切り口などが作る段差）を数える。
斜めの帯・丸い折れ点・丸い末端・T字の合流は Z 形にならない。端点が模型の縁(天面の外周)に触れる辺は除く（縁から入る帯の側面で、縁の切り口と接するだけの辺）。

実行: uv run --with opencv-python-headless --with numpy --with pillow python3 -I body_step_scan.py [clean画像のディレクトリ]
"""
import math
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

MX0, MY0, MX1, MY1 = 138, 138, 1782, 942
FLOOR = (232, 201, 168)


def scan(path):
    a = np.array(Image.open(path).convert("RGB"))
    m = (a == np.array(FLOOR)).all(axis=2)[MY0:MY1, MX0:MX1].astype(np.uint8) * 255
    m = np.pad(m, 6)  # 縁で切れた床が閉じた輪郭になるよう外周に余白（床を縁の外へ伸ばさず、縁の辺は後で除く）
    cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    out = []
    for c in cs:
        poly = cv2.approxPolyDP(c, 2.0, True)[:, 0, :].astype(float) - 6
        n = len(poly)
        for i in range(n):
            p0, p1, p2, p3 = poly[(i - 1) % n], poly[i], poly[(i + 1) % n], poly[(i + 2) % n]
            e = p2 - p1
            L = math.hypot(*e)
            if not (8 <= L <= 150):
                continue
            ang = math.degrees(math.atan2(e[1], e[0])) % 180
            if min(ang, abs(ang - 90), abs(ang - 180)) > 2.0:
                continue
            if any(min(q[0], MX1 - MX0 - 1 - q[0], q[1], MY1 - MY0 - 1 - q[1]) <= 2 for q in (p1, p2)):
                continue
            def turn(u, v):
                return math.degrees(math.atan2(u[0] * v[1] - u[1] * v[0], u[0] * v[0] + u[1] * v[1]))
            t1, t2 = turn(p1 - p0, e), turn(e, p3 - p2)
            if t1 * t2 < 0 and abs(t1) >= 60 and abs(t2) >= 60:
                out.append((round(p1[0] + MX0), round(p1[1] + MY0), round(p2[0] + MX0), round(p2[1] + MY0), round(L)))
    return out


def main():
    if len(sys.argv) > 1 and sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        return
    d = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[4] / "verification/body-layout/clean"
    files = sorted(d.glob("BDY-*.png")) if d.is_dir() else []
    if not files:
        print(f"ERROR: {d} に BDY-*.png が無い（ディレクトリが不在・空・0件）", file=sys.stderr)
        sys.exit(1)
    tot = 0
    for f in files:
        r = scan(f)
        tot += len(r)
        print(f"{f.stem}: 段差 {len(r)} 件" + ("  " + "; ".join(f"({a},{b})-({c},{e}) {l}px" for a, b, c, e, l in r) if r else ""))
    print(f"合計 {tot} 件")


if __name__ == "__main__":
    main()
