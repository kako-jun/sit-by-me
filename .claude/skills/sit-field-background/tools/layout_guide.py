"""Draw a plain geometry guide from current YAML MAP geometry or explicit rectangles.

The historical trm02/trm04/trm05 aliases select MAP IDs; their old fixed dimensions
are superseded by docs/ledger. This tool never runs image generation.

  uv run python3 layout_guide.py --map TRM-04 --out guide.png
  uv run python3 layout_guide.py --rects '0,0,100,100' --out guide.png
"""
import argparse
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ledger_build as LB  # noqa: E402
import oblique_mock as M  # noqa: E402


def map_polygons(map_id):
    """Read current canonical geometry without writing derived files."""
    plan = LB.build_plan(LB.tables(), map_id)
    floors = [M.floor_img_poly(floor) for floor in plan.get("floors", [])]
    walls = [M.rect_poly(wall["rect"]) for wall in plan.get("walls", [])]
    return floors + walls


def draw(polygons, width=M.W, height=M.H_IMG):
    image = Image.new("RGB", (width, height), "white")
    pen = ImageDraw.Draw(image)
    for polygon in polygons:
        pen.polygon(polygon, fill=(232, 232, 232), outline=(120, 120, 120), width=3)
    return image


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--map")
    source.add_argument("--preset", choices=("trm02", "trm04", "trm05"))
    source.add_argument("--rects")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    if args.rects:
        polygons = []
        for item in args.rects.split(";"):
            coords = tuple(float(value) for value in item.split(","))
            if len(coords) != 4 or coords[2] <= coords[0] or coords[3] <= coords[1]:
                parser.error("each rectangle must be x0,y0,x1,y1 with positive width and height")
            x0, y0, x1, y1 = coords
            polygons.append([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])
    else:
        map_id = args.map or "TRM-" + args.preset[-2:]
        polygons = map_polygons(map_id)
    draw(polygons).save(args.out)
    print(f"wrote {args.out}; {len(polygons)} polygons")


if __name__ == "__main__":
    main()
