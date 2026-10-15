"""フィールド用の編集マップ・実行時マスク・確認用プレビューを生成する。

使い方: uv run --with pillow python3 sample/field/masks/make_masks.py [--refresh-edit] [名前...]

JSON はリンク・背景・サイズなどのメタデータで、実際の編集の正本はPNGである。
初回のPNGを下書きする必要がある時だけ、旧形式の ``walkable`` または任意の
``traversal`` / ``foreground`` ポリゴンを読める（``walkable`` は全員通行として扱う）。
下書き用の新形式は次の通り。

{
  "image": "background.png", "size": [width, height],
  "traversal": {
    "universal": [[[x, y], ...]],
    "assist": [[[x, y], ...]],
    "blocked": [[[x, y], ...]
  },
  "foreground": [[[x, y], ...]],
  "links": [{"edge": "left", "range": [start, end], "class": "universal"}]
}

``universal`` は全員、``assist`` は立っている時期または相方の補助解禁後だけ、
``blocked`` は誰も通れない。foreground は移動とは独立した前景被さり領域である。
編集用PNGは塗りだけで輪郭を焼き込まず、輪郭は *-mask-overlay.png の確認用だけに描く。
初回はJSONから編集用PNGを作る。以後はそのPNGを読み込んで実行時マスクとレビューを
更新するため、Photoshopでの編集は失われない。JSONから作り直す時だけ --refresh-edit を使う。
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
FIELD = HERE.parent
NAMES = ["overview", "wide-road", "narrow-lane", "connector"]

BLACK = (0, 0, 0)
ORANGE = (255, 157, 0)
WHITE = (255, 255, 255)
CYAN = (0, 255, 255)


def polygons(spec, name):
    """Return a class's polygons, accepting the original walkable-only schema."""
    traversal = spec.get("traversal")
    if traversal is None:
        if name == "universal":
            return spec.get("walkable", [])
        if name == "blocked":
            return spec.get("blocked", [])
        return []
    return traversal.get(name, [])


def paint(image, polys, fill):
    draw = ImageDraw.Draw(image)
    for poly in polys:
        draw.polygon([tuple(point) for point in poly], fill=fill)


def traversal_edit_map(spec, size):
    """Make the Photoshop source: flat RGB fills, deliberately without outlines."""
    edit = Image.new("RGB", size, BLACK)
    paint(edit, polygons(spec, "universal"), WHITE)
    paint(edit, polygons(spec, "assist"), ORANGE)
    paint(edit, polygons(spec, "blocked"), BLACK)
    return edit


def binary_mask(edit, include_assist):
    mask = Image.new("L", edit.size, 0)
    src = edit.load()
    dst = mask.load()
    accepted = {WHITE}
    if include_assist:
        accepted.add(ORANGE)
    for y in range(edit.height):
        for x in range(edit.width):
            if src[x, y] in accepted:
                dst[x, y] = 255
    return mask


def exact_colour_mask(image, colour):
    mask = Image.new("L", image.size, 0)
    source = image.load()
    target = mask.load()
    for y in range(image.height):
        for x in range(image.width):
            if source[x, y] == colour:
                target[x, y] = 255
    return mask


def load_or_create_edit(path, create, size, colours, refresh):
    if not path.exists() or refresh:
        edit = create()
        edit.save(path)
        return edit
    edit = Image.open(path).convert("RGB")
    if edit.size != size:
        raise ValueError(f"{path.name}: size {edit.size} != JSON size {size}")
    unexpected = set(edit.getdata()) - colours
    if unexpected:
        raise ValueError(f"{path.name}: unsupported edit colour {next(iter(unexpected))}")
    return edit


def foreground_edit_map(spec, size):
    edit = Image.new("RGB", size, BLACK)
    paint(edit, spec.get("foreground", []), CYAN)
    return edit


def foreground_mask(edit):
    return exact_colour_mask(edit, CYAN)


def review_preview(bg, traversal, foreground):
    """Make a disposable review image; contours never enter an editable source."""
    preview = bg.convert("RGBA")
    tint = Image.new("RGBA", bg.size, (0, 0, 0, 0))
    for source, colour, alpha in ((traversal, WHITE, (0, 220, 90, 100)),
                                  (traversal, ORANGE, (255, 157, 0, 110)),
                                  (traversal, BLACK, (255, 45, 45, 55)),
                                  (foreground, CYAN, (0, 255, 255, 100))):
        tint.paste(alpha, mask=exact_colour_mask(source, colour))
    preview = Image.alpha_composite(preview, tint).convert("RGB")
    outline = ImageDraw.Draw(preview)
    labels = Image.new("L", bg.size, 0)
    labels.paste(85, mask=exact_colour_mask(traversal, WHITE))
    labels.paste(170, mask=exact_colour_mask(traversal, ORANGE))
    labels.paste(255, mask=exact_colour_mask(foreground, CYAN))
    labels = labels.load()
    for y in range(1, bg.height - 1):
        for x in range(1, bg.width - 1):
            if labels[x, y] and (labels[x, y] != labels[x - 1, y] or labels[x, y] != labels[x + 1, y]
                                 or labels[x, y] != labels[x, y - 1] or labels[x, y] != labels[x, y + 1]):
                outline.point((x, y), fill=(255, 255, 0))
    return preview


def build(name, refresh_edit=False):
    spec = json.loads((HERE / f"{name}.json").read_text(encoding="utf-8"))
    size = tuple(spec["size"])
    bg = Image.open(FIELD / spec["image"]).convert("RGB")
    if bg.size != size:
        raise ValueError(f"{name}: image size {bg.size} != JSON size {size}")

    edit = load_or_create_edit(
        HERE / f"{name}-traversal-edit.png",
        lambda: traversal_edit_map(spec, size), size, {BLACK, ORANGE, WHITE}, refresh_edit,
    )
    foreground = load_or_create_edit(
        HERE / f"{name}-foreground-edit.png",
        lambda: foreground_edit_map(spec, size), size, {BLACK, CYAN}, refresh_edit,
    )
    wheelchair = binary_mask(edit, include_assist=False)
    assisted = binary_mask(edit, include_assist=True)
    occlusion = foreground_mask(foreground)

    wheelchair.save(HERE / f"{name}-wheelchair-mask.png")
    assisted.save(HERE / f"{name}-standing-mask.png")
    assisted.save(HERE / f"{name}-assist-mask.png")
    occlusion.save(HERE / f"{name}-foreground-mask.png")
    # Compatibility with the old consumer: it was the wheelchair/universal mask.
    wheelchair.save(HERE / f"{name}-mask.png")
    review_preview(bg, edit, foreground).save(HERE / f"{name}-mask-overlay.png")
    print(name, "ok", "(legacy schema)" if "traversal" not in spec else "")


if __name__ == "__main__":
    args = sys.argv[1:]
    refresh = "--refresh-edit" in args
    names = [arg for arg in args if arg != "--refresh-edit"] or NAMES
    for mask_name in names:
        build(mask_name, refresh)
