"""BDY-02 の広間半径の実測。清書版 clean/BDY-02.png から、ハブ中心の床円（広間）の半径と壁の縁取りを画素で確認し、
body_layout.py の計算値と一致するか見る。実行: uv run --with pillow --with numpy python3 verification/body-layout/measure_hall_radius.py"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / ".claude/skills/sit-field-background/tools"))
import body_layout as B

im = np.array(Image.open(Path(__file__).parent / "clean/BDY-02.png").convert("RGB"))
rows, ev, nodes, svg_edges, portals = B.build_model()
lw = int(round(B.DEFAULT_MAIN_WIDTH_RATIO * B.MW))
(cx, cy), r = B.hall_radius("BDY-02", B.corridors("BDY-02", portals["BDY-02"]), lw)
floor = np.all(im == B.FLOOR, axis=2)
ys, xs = np.mgrid[0:im.shape[0], 0:im.shape[1]]
inside = (xs - cx) ** 2 + (ys - cy) ** 2 <= r * r
print("centre", (cx, cy), "radius(計算)", r, "wall thickness", B.WALL_T)
print("床円がすべて床:", bool(floor[inside].all()))
ring = ((xs - cx) ** 2 + (ys - cy) ** 2 <= (r + B.WALL_T) ** 2) & ~inside
print("壁の縁取り(clean壁色)の画素数:", int((np.all(im == B.CLEAN_WALL, axis=2) & ring).sum()))
