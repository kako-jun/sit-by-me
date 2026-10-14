"""usage: uv run --with resvg-py --with pillow python3 -I scripts/svg_to_png.py in.svg out.png [width] [bg-hex-for-preview]"""
import sys, resvg_py, io
from PIL import Image
svg, out = sys.argv[1], sys.argv[2]
w = int(sys.argv[3]) if len(sys.argv) > 3 else 1600
b = resvg_py.svg_to_bytes(svg_path=svg, width=w)
im = Image.open(io.BytesIO(bytes(b))).convert("RGBA")
if len(sys.argv) > 4:
    bg = Image.new("RGBA", im.size, sys.argv[4]); bg.alpha_composite(im); im = bg
im.save(out); print(im.size, im.mode)
