"""ポリゴンJSONから歩行マスクと確認用の重ね画像を生成する。
使い方: uv run --with pillow python3 sample/field/masks/make_masks.py [名前...]
"""
import json, sys
from pathlib import Path
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
FIELD = HERE.parent
NAMES = ["overview", "wide-road", "narrow-lane", "connector"]

def build(name):
    spec = json.loads((HERE / f"{name}.json").read_text(encoding="utf-8"))
    bg = Image.open(FIELD / spec["image"]).convert("RGB")
    size = tuple(spec["size"])
    assert bg.size == size, (bg.size, size)
    mask = Image.new("L", size, 0)
    d = ImageDraw.Draw(mask)
    for poly in spec["walkable"]:
        d.polygon([tuple(p) for p in poly], fill=255)
    mask.save(HERE / f"{name}-mask.png")
    green = Image.new("RGB", size, (0, 255, 0))
    tint = Image.composite(green, bg, mask.point(lambda v: 110 if v else 0))
    od = ImageDraw.Draw(tint)
    for poly in spec["walkable"]:
        od.line([tuple(p) for p in poly] + [tuple(poly[0])], fill=(255, 255, 0), width=2)
    tint.save(HERE / f"{name}-mask-overlay.png")
    print(name, "ok")

for n in (sys.argv[1:] or NAMES):
    build(n)
