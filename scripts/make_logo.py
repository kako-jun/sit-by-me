"""SIT BY ME の仮置き文字ロゴ(brand/logo.svg)を作る。文字は輪郭化(パス化)するのでSVGはフォント非依存。
フォント: Noto Serif Display ExtraCondensed Black (SIL OFL 1.1)。
usage: uv run --with fonttools python3 -I scripts/make_logo.py <font.ttf> <out.svg> [two|one]
  one = 1行 "SIT BY ME" / two = 2行 "SIT BY" + "ME"
"""
import sys
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen

font_path, out = sys.argv[1], sys.argv[2]
mode = sys.argv[3] if len(sys.argv) > 3 else "two"
f = TTFont(font_path)
gs, cmap, hmtx = f.getGlyphSet(), f.getBestCmap(), f["hmtx"]
TRACK = 60  # 字間(font units)
PAD = 80

def line(text, x0, y0):
    """text を baseline y0(下向き座標)へ配置した path d と (幅, 高さ) を返す"""
    pen = SVGPathPen(gs); x = x0
    for ch in text:
        if ch == " ":
            x += hmtx[cmap[32]][0] * 1.4; continue
        g = cmap[ord(ch)]
        gs[g].draw(TransformPen(pen, (1, 0, 0, -1, x, y0)))
        x += hmtx[g][0] + TRACK
    return pen.getCommands(), x - TRACK - x0

cap = f["OS/2"].sCapHeight
lines = ["SIT BY ME"] if mode == "one" else ["SIT BY", "ME"]
LH = cap * 1.25
ds, widths = [], []
for i, t in enumerate(lines):
    d, w = line(t, 0, cap + i * LH); ds.append(d); widths.append(w)
W = max(widths); H = cap + (len(lines) - 1) * LH
# 2行目は中央寄せ
if mode == "two":
    d2, w2 = line(lines[1], (W - widths[1]) / 2, cap + LH); ds[1] = d2
vw, vh = W + PAD * 2, H + PAD * 2
paths = "\n".join(f'    <path d="{d}"/>' for d in ds)
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {vw:.0f} {vh:.0f}" width="{vw:.0f}" height="{vh:.0f}">
  <title>SIT BY ME (provisional text logo)</title>
  <defs>
    <linearGradient id="g" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#f6ecc8"/>
      <stop offset="0.55" stop-color="#d9bd73"/>
      <stop offset="1" stop-color="#9c7a34"/>
    </linearGradient>
  </defs>
  <g transform="translate({PAD} {PAD})" fill="url(#g)" stroke="#2a1f0c" stroke-width="14" stroke-linejoin="round" paint-order="stroke fill">
{paths}
  </g>
</svg>
'''
open(out, "w").write(svg)
print(out, vw, vh)
