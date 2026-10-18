"""ジオラマ版の歩行マスク生成。ポリゴンJSON（walkable=白、blocked=黒で上書き）→ 白黒PNGと確認用の重ね画像。
マスクは2種類: 車椅子の時期（{名前}-mask.png）と立てる時期（{名前}-standing-mask.png）。
JSON の standing_only に書いたポリゴン（古い石段など）は、立てる時期だけ白で、車椅子の時期は黒。standing_only が無い絵は、立てる時期のマスクを作らない（車椅子と同じ）。
さらに teramachi-map.json のリンクが、マスクの端まで届いているかを検査する（requires: "standing" のリンクは立てる時期のマスクで検査）。
使い方: uv run --with pillow python3 verification/fields/legacy-masks/make_masks.py [名前...]
"""
import json, sys
from pathlib import Path
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
TRIAL = HERE.parent
NAMES = ["wide-road", "connector", "narrow-lane", "kindergarten", "sento", "slope-top",
         "hinomi-bend", "well-merge", "barrier-free-ramp", "danchi-court", "old-slope-foot"]

def draw_mask(spec, standing):
    size = tuple(spec["size"])
    mask = Image.new("L", size, 0)
    d = ImageDraw.Draw(mask)
    polys = list(spec["walkable"]) + (list(spec.get("standing_only", [])) if standing else [])
    for poly in polys:
        d.polygon([tuple(p) for p in poly], fill=255)
    for poly in spec.get("blocked", []):
        d.polygon([tuple(p) for p in poly], fill=0)
    return mask, polys

def overlay(bg, mask, spec, polys, path):
    green = Image.new("RGB", bg.size, (0, 255, 0))
    tint = Image.composite(green, bg, mask.point(lambda v: 110 if v else 0))
    od = ImageDraw.Draw(tint)
    for poly in polys:
        od.line([tuple(p) for p in poly] + [tuple(poly[0])], fill=(255, 255, 0), width=2)
    for poly in spec.get("blocked", []):
        od.line([tuple(p) for p in poly] + [tuple(poly[0])], fill=(255, 0, 0), width=2)
    tint.save(path)

def build(name):
    spec = json.loads((HERE / f"{name}.json").read_text(encoding="utf-8"))
    bg = Image.open(HERE / spec["image"]).convert("RGB")
    output = HERE / spec["output_prefix"]
    output.parent.mkdir(parents=True, exist_ok=True)
    assert bg.size == tuple(spec["size"]), (bg.size, spec["size"])
    mask, polys = draw_mask(spec, False)
    mask.save(output.parent / f"{output.name}-mask.png")
    overlay(bg, mask, spec, polys, output.parent / f"{output.name}-mask-overlay.png")
    out = {"wheelchair": mask}
    if spec.get("standing_only"):
        sm, sp = draw_mask(spec, True)
        sm.save(output.parent / f"{output.name}-standing-mask.png")
        overlay(bg, sm, spec, sp, output.parent / f"{output.name}-standing-mask-overlay.png")
        out["standing"] = sm
    else:
        out["standing"] = mask
    print(name, "ok", "(standing あり)" if spec.get("standing_only") else "")
    return out

def edge_ok(mask, edge, rng):
    w, h = mask.size
    bad = 0
    for v in range(rng[0], rng[1] + 1):
        x, y = {"left": (1, v), "right": (w - 2, v), "top": (v, 1), "bottom": (v, h - 2)}[edge]
        if mask.getpixel((x, y)) == 0:
            bad += 1
    return bad

def check_links(masks):
    mp = json.loads((HERE / "teramachi-map.json").read_text(encoding="utf-8"))
    for l in mp["links"]:
        variant = "standing" if l.get("requires") == "standing" else "wheelchair"
        b = edge_ok(masks[l["from"]][variant], l["edge"], l["range"])
        msg = f'{l["from"]}.{l["edge"]}{l["range"]} -> {l["to"]} [{variant}]: 黒画素 {b}/{l["range"][1]-l["range"][0]+1}'
        if l["to"]:
            b2 = edge_ok(masks[l["to"]][variant], l["toEdge"], l["toRange"])
            msg += f' / 相手 {b2}'
        print(msg)

if __name__ == "__main__":
    ms = {n: build(n) for n in (sys.argv[1:] or NAMES)}
    if not sys.argv[1:]:
        check_links(ms)
