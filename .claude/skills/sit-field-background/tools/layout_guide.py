"""Layout guide (a flat grey block diagram) for field-map interiors and other map images.

Why: written proportions are not kept by the image model (Teramachi corridor length, residence size). A plain grey diagram of the
outline, passed as a REFERENCE image (and, when strictness is needed, a coloured base used as the EDIT source), fixes proportions.
The diagram carries no style: grey rectangles and thin lines only, NO text, NO arrows (so nothing leaks into the picture).
The prompt must say: "copy its rectangles' proportions, position and size relative to the image frame exactly; do not draw its grey
faces or lines in the picture".

Presets (all 1672x941, south edge at y = 780, same scale: the hall's south face = 640 px = 1):
  trm04  main hall 640x600 with a west corridor 340x200 (0.53) and an east corridor 250x200 (0.39)
  trm05  residence 520x510 (0.81 of the hall's width, about 0.31 of the image width, nearly square)
  trm02  kindergarten 690x480 (1.08 of the hall's width, about 0.41 of the image width)
Custom:  --rects "x0,y0,x1,y1;x0,y0,x1,y1" --out guide.png

Usage:
  uv run --with pillow python3 -I .claude/skills/sit-field-background/tools/layout_guide.py --preset trm05 --out out/layout-trm05.png
Every rectangle is printed with its size relative to the image width (check against the exterior measurements).
"""
import argparse
from PIL import Image, ImageDraw

W, H = 1672, 941
SOUTH = 780

def centered(w, d):
    x0 = (W - w) // 2
    return [(x0, SOUTH - d, x0 + w, SOUTH)]

def trm04():
    hall_w, west_w, east_w = 640, 340, 250
    x0 = (W - (west_w + hall_w + east_w)) // 2
    hall = (x0 + west_w, SOUTH - 600, x0 + west_w + hall_w, SOUTH)
    return [(x0, SOUTH - 200, x0 + west_w, SOUTH), hall, (hall[2], SOUTH - 200, hall[2] + east_w, SOUTH)]

PRESETS = {'trm04': trm04, 'trm05': lambda: centered(520, 510), 'trm02': lambda: centered(690, 480)}

def draw(rects, w=W, h=H):
    im = Image.new('RGB', (w, h), 'white')
    d = ImageDraw.Draw(im)
    for rc in rects:
        d.rectangle(rc, fill=(232, 232, 232), outline=(120, 120, 120), width=3)
    return im

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--preset', choices=sorted(PRESETS))
    ap.add_argument('--rects')
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    if a.rects:
        rects = [tuple(int(v) for v in s.split(',')) for s in a.rects.split(';')]
    else:
        rects = PRESETS[a.preset or 'trm05']()
    draw(rects).save(a.out)
    for x0, y0, x1, y1 in rects:
        print('rect', (x0, y0, x1, y1), 'size %dx%d' % (x1 - x0, y1 - y0), 'width/frame %.3f' % ((x1 - x0) / W), 'vs hall 640: %.3f' % ((x1 - x0) / 640))
