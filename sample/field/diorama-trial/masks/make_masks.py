"""ジオラマ版の歩行マスク生成。ポリゴンJSON（walkable=白、blocked=黒で上書き）→ 白黒PNGと確認用の重ね画像。
さらに teramachi-map.json のリンクが、マスクの端まで届いているかを検査する。
使い方: uv run --with pillow python3 sample/field/diorama-trial/masks/make_masks.py [名前...]
"""
import json, sys
from pathlib import Path
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
TRIAL = HERE.parent
NAMES = ["wide-road", "connector", "narrow-lane", "kindergarten", "sento", "slope-top"]

def build(name):
    spec = json.loads((HERE / f"{name}.json").read_text(encoding="utf-8"))
    bg = Image.open(TRIAL / spec["image"]).convert("RGB")
    size = tuple(spec["size"])
    assert bg.size == size, (bg.size, size)
    mask = Image.new("L", size, 0)
    d = ImageDraw.Draw(mask)
    for poly in spec["walkable"]:
        d.polygon([tuple(p) for p in poly], fill=255)
    for poly in spec.get("blocked", []):
        d.polygon([tuple(p) for p in poly], fill=0)
    mask.save(HERE / f"{name}-mask.png")
    green = Image.new("RGB", size, (0, 255, 0))
    tint = Image.composite(green, bg, mask.point(lambda v: 110 if v else 0))
    od = ImageDraw.Draw(tint)
    for poly in spec["walkable"]:
        od.line([tuple(p) for p in poly] + [tuple(poly[0])], fill=(255, 255, 0), width=2)
    for poly in spec.get("blocked", []):
        od.line([tuple(p) for p in poly] + [tuple(poly[0])], fill=(255, 0, 0), width=2)
    tint.save(HERE / f"{name}-mask-overlay.png")
    print(name, "ok")
    return mask

def edge_ok(mask, edge, rng):
    w, h = mask.size
    bad = 0
    for v in range(rng[0], rng[1] + 1):
        x, y = {"left": (1, v), "right": (w - 2, v), "top": (v, 1), "bottom": (v, h - 2)}[edge]
        if mask.getpixel((x, min(y, h - 1)) if edge in ("top", "bottom") else (x, v)) == 0:
            bad += 1
    return bad

def check_links(masks):
    mp = json.loads((HERE / "teramachi-map.json").read_text(encoding="utf-8"))
    for l in mp["links"]:
        m = masks[l["from"]]
        b = edge_ok(m, l["edge"], l["range"])
        msg = f'{l["from"]}.{l["edge"]}{l["range"]} -> {l["to"]}: 黒画素 {b}/{l["range"][1]-l["range"][0]+1}'
        if l["to"]:
            b2 = edge_ok(masks[l["to"]], l["toEdge"], l["toRange"])
            msg += f' / 相手 {b2}'
        print(msg)

if __name__ == "__main__":
    ms = {n: build(n) for n in (sys.argv[1:] or NAMES)}
    if not sys.argv[1:]:
        check_links(ms)
