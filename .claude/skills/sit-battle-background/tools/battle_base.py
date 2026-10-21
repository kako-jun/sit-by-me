"""Common geometry tool for ALL battle backgrounds of Sit by Me (kako-jun 2026-10-21: "the guide is almost the same for every battle background, so reuse it").

A battle background is a small tabletop diorama of the battlefield only, seen from high above and slightly turned, in a PARALLEL
(oblique, "cabinet drawing") projection. This tool draws a flat coloured BASE image that carries the geometry; imagegen then repaints
it as a handmade miniature by image EDIT (see SKILL.md). Mirroring/flipping to fix the direction is forbidden.

FIXED geometry (the same for every area; only the preset below changes the contents):
  image 1672x941; orthographic projection; depression THETA = 65 deg; yaw PSI = 2 deg
  f = (sin PSI cos THETA, cos PSI cos THETA, -sin THETA);  r = f x zhat normalised;  u = r x f
  world: a = along the backdrop (right), b = depth (away from the camera), z = up
  every line across the stage (foot line of the backdrop, plank seams / tile rows, front cardboard edge) has the SAME screen slope
  u_a / r_a = tan PSI sin THETA = 0.03165 px/px (rising to the right; about 52.9 px across the width)
  foot line of the backdrop: left y = 166 (0.176 H), right y = 113 (0.120 H)  -> the wall band is about 12..18 % of the height
  front cardboard edge: leaves the frame at the bottom left (enters at x = 727) and is seen along the right part only
  floor share about 85 % of the picture; vertical objects stay vertical on the screen.

Variable per preset: the contents of the band (painted backdrop / wall and roof / tree line), curtains yes/no, the floor material
(planks or tiles) and its colours.

Usage:
  uv run --with pillow --with numpy python3 -I .claude/skills/sit-battle-background/tools/battle_base.py --preset geki --out out/base.png
  ... --guide --out guide-battle.png     (the plain grey guide: no colour, no text, no arrows)
  ... --measure                          (prints the slopes of every line across the stage and the band / floor shares)
"""
import argparse
import math
import random
from PIL import Image, ImageDraw

W, H = 1672, 941
THETA, PSI = math.radians(65.0), math.radians(2.0)
f = (math.sin(PSI) * math.cos(THETA), math.cos(PSI) * math.cos(THETA), -math.sin(THETA))
r = (math.cos(PSI), -math.sin(PSI), 0.0)
u = (r[1] * f[2] - r[2] * f[1], r[2] * f[0] - r[0] * f[2], r[0] * f[1] - r[1] * f[0])
slope = u[0] / r[0]
BASE_LEFT = 166.0       # foot line of the backdrop at the left edge
FRONT = 963.0           # front cardboard edge at the left edge (leaves the frame at the bottom left)
ROW = 28.0              # screen px between plank / tile rows
A0, A1 = -300.0, W + 300.0

def _proj(a, b, z=0.0):
    return (r[0] * a + r[1] * b + r[2] * z, u[0] * a + u[1] * b + u[2] * z)
_sx0, _sy0 = _proj(0.0, 0.0)
X0, Y0 = -_sx0, BASE_LEFT + _sy0

def S(a, b, z=0.0):
    x, y = _proj(a, b, z)
    return (X0 + x, Y0 - y)

def foot_y(x):
    return BASE_LEFT - slope * x

# ---------------------------------------------------------------- presets
PRESETS = {
    # opening play fight: kindergarten stage (green curtains, painted snowy mountains and castle, brown plank floor)
    'geki': dict(floor='planks', floor_bg=(92, 58, 36),
                 shades=[(98, 62, 38), (104, 66, 40), (92, 58, 36), (110, 72, 44), (100, 64, 42), (94, 60, 38)],
                 seam=(60, 38, 24), end=(66, 42, 26), seed=5, plank_len=(560.0, 820.0),
                 band='painted', curtains=True, sky=(196, 222, 244)),
    # Teramachi outdoor: stone paving, plaster wall with a tile roof behind, snowy trees (simple silhouettes, no curtains)
    'teramachi': dict(floor='tiles', floor_bg=(120, 120, 124),
                      shades=[(124, 124, 128), (112, 112, 118), (132, 132, 136), (118, 120, 126)],
                      seam=(80, 80, 86), end=(90, 90, 96), seed=7, plank_len=(150.0, 260.0),
                      band='wall', curtains=False, sky=(200, 214, 230)),
    # snowy grove: snow-white ground with faint tiles, a row of conifers behind
    'grove': dict(floor='tiles', floor_bg=(236, 240, 246),
                  shades=[(240, 243, 248), (232, 237, 244), (244, 246, 250)],
                  seam=(205, 212, 224), end=(212, 218, 228), seed=9, plank_len=(220.0, 360.0),
                  band='trees', curtains=False, sky=(206, 222, 240)),
}

def _floor(d, P):
    db = ROW / u[1]
    random.seed(P['seed'])
    rows = int((H + 60) / ROW) + 2
    lo, hi = P['plank_len']
    for k in range(rows):
        b0, b1 = -k * db, -(k + 1) * db
        a = A0 - random.uniform(0, 700 if P['floor'] == 'planks' else hi * 2)
        while a < A1:
            L = random.uniform(lo, hi)
            shade = random.choice(P['shades'])
            d.polygon([S(a, b0), S(a + L, b0), S(a + L, b1), S(a, b1)], fill=shade)
            d.line([S(a, b0), S(a, b1)], fill=P['end'], width=1)
            a += L
        d.line([S(A0, b1), S(A1, b1)], fill=P['seam'], width=1)

def _front_edge(d):
    d.polygon([(0, FRONT), (W, FRONT - slope * W), (W, H), (0, H)], fill=(196, 152, 98))
    for x in range(0, W, 9):                         # corrugation hint
        y0 = FRONT - slope * x
        d.line([(x, y0 + 14), (x, H)], fill=(176, 132, 82), width=1)
    d.line([(0, FRONT), (W, FRONT - slope * W)], fill=(70, 46, 28), width=3)

def _mountain(d, x0, x1, peak_x, h, col):
    d.polygon([(x0, foot_y(x0)), (peak_x, foot_y(peak_x) - h), (x1, foot_y(x1))], fill=col)

def _tree(d, cx, big=1.0):
    fy = foot_y(cx)
    d.polygon([(cx - 22 * big, fy - 6), (cx, fy - 62 * big), (cx + 22 * big, fy - 6)], fill=(36, 86, 52))
    d.polygon([(cx - 15 * big, fy - 30 * big), (cx, fy - 62 * big), (cx + 15 * big, fy - 30 * big)], fill=(246, 248, 250))

def _band_painted(d, P):
    d.polygon([(0, 0), (W, 0), (W, foot_y(W)), (0, foot_y(0))], fill=P['sky'])
    _mountain(d, 40, 520, 250, 80, (150, 170, 205)); _mountain(d, 380, 900, 640, 88, (235, 240, 248))
    _mountain(d, 820, 1300, 1060, 70, (160, 182, 214)); _mountain(d, 1180, 1640, 1420, 62, (238, 242, 250))
    d.polygon([(0, foot_y(0) - 10), (W, foot_y(W) - 10), (W, foot_y(W)), (0, foot_y(0))], fill=(248, 250, 253))
    SC, cx = 1.35, 900
    fy = foot_y(cx)
    d.rectangle([cx - 60 * SC, fy - 28 * SC, cx + 60 * SC, fy - 8 * SC], fill=(236, 226, 206))
    for tx, th in ((cx - 54 * SC, 42), (cx, 52), (cx + 54 * SC, 42)):
        d.rectangle([tx - 12 * SC, fy - th * SC, tx + 12 * SC, fy - 8 * SC], fill=(240, 230, 210))
        d.polygon([(tx - 15 * SC, fy - th * SC), (tx, fy - th * SC - 18 * SC), (tx + 15 * SC, fy - th * SC)], fill=(190, 52, 44))
    for tx in (210, 300, 1380, 1470):
        _tree(d, tx)

def _band_wall(d, P):
    d.polygon([(0, 0), (W, 0), (W, foot_y(W)), (0, foot_y(0))], fill=P['sky'])
    wallh, roofh = 62, 26                            # a plaster wall with a tile roof, standing on the foot line (upright edges)
    d.polygon([(0, foot_y(0) - wallh), (W, foot_y(W) - wallh), (W, foot_y(W)), (0, foot_y(0))], fill=(232, 224, 206))
    d.polygon([(0, foot_y(0) - wallh - roofh), (W, foot_y(W) - wallh - roofh), (W, foot_y(W) - wallh), (0, foot_y(0) - wallh)], fill=(96, 98, 106))
    d.polygon([(0, foot_y(0) - wallh - roofh - 8), (W, foot_y(W) - wallh - roofh - 8), (W, foot_y(W) - wallh - roofh), (0, foot_y(0) - wallh - roofh)], fill=(248, 250, 253))
    for tx in (260, 760, 1300):
        _tree(d, tx, 0.8)

def _band_trees(d, P):
    d.polygon([(0, 0), (W, 0), (W, foot_y(W)), (0, foot_y(0))], fill=P['sky'])
    d.polygon([(0, foot_y(0) - 10), (W, foot_y(W) - 10), (W, foot_y(W)), (0, foot_y(0))], fill=(248, 250, 253))
    for tx in range(60, W, 120):
        _tree(d, tx, 1.0 + 0.25 * ((tx // 120) % 3 == 0))

def _curtains(d):
    for xa, xb, edge in ((0, 130, 130), (W - 130, W, W - 130)):
        d.polygon([(xa, 0), (xb, 0), (xb, foot_y(xb)), (xa, foot_y(xa))], fill=(30, 92, 58))
        for fx in range(xa + 10, xb, 22):
            d.line([(fx, 0), (fx, foot_y(fx))], fill=(22, 70, 44), width=2)
        d.line([(edge, 0), (edge, foot_y(edge))], fill=(214, 176, 70), width=4)
    VAL, TOPOFF = 16.0, 125.0
    d.polygon([(0, 0), (W, 0), (W, max(0.0, foot_y(W) - TOPOFF + VAL)), (0, foot_y(0) - TOPOFF + VAL)], fill=(30, 92, 58))
    d.line([(0, foot_y(0) - TOPOFF + VAL), (W, foot_y(W) - TOPOFF + VAL)], fill=(214, 176, 70), width=3)

BANDS = {'painted': _band_painted, 'wall': _band_wall, 'trees': _band_trees}

def render(preset):
    P = PRESETS[preset]
    im = Image.new('RGB', (W, H), P['floor_bg'])
    d = ImageDraw.Draw(im)
    _floor(d, P)
    _front_edge(d)
    BANDS[P['band']](d, P)
    if P['curtains']:
        _curtains(d)
    d.line([(0, foot_y(0)), (W, foot_y(W))], fill=(60, 40, 26), width=3)
    return im

def guide():
    """The plain grey guide: no colour, no text, no arrows. Same geometry as every preset."""
    im = Image.new('RGB', (W, H), 'white')
    d = ImageDraw.Draw(im)
    PANEL = 40.0
    def poly(a, b):
        return [(0, a), (W, a - slope * W), (W, b - slope * W), (0, b)]
    d.polygon([(0, 0), (W, 0), (W, BASE_LEFT - PANEL - slope * W), (0, BASE_LEFT - PANEL)], fill=(160, 160, 160))
    d.polygon(poly(BASE_LEFT - PANEL, BASE_LEFT), fill=(195, 195, 195))
    d.polygon(poly(BASE_LEFT, FRONT), fill=(236, 236, 236))
    d.polygon([(0, FRONT), (W, FRONT - slope * W), (W, H), (0, H)], fill=(205, 205, 205))
    for k in range(1, 9):
        y0 = BASE_LEFT + k * 100.0
        d.line([(0, y0), (W, y0 - slope * W)], fill=(150, 150, 150), width=2)
    for y0, wd in ((BASE_LEFT - PANEL, 2), (BASE_LEFT, 4), (FRONT, 3)):
        d.line([(0, y0), (W, y0 - slope * W)], fill=(100, 100, 100), width=wd)
    return im

def measure():
    print('projection u =', [round(v, 4) for v in u], ' analytic slope =', round(slope, 5), '  rise across the width =', round(slope * W, 1), 'px')
    for name, y0 in (('backdrop foot line', BASE_LEFT), ('front cardboard edge', FRONT)):
        y1 = y0 - slope * W
        print('%-22s left y=%.1f right y=%.1f slope=%.5f' % (name, y0, y1, (y0 - y1) / W))
    db = ROW / u[1]
    for k in (3, 8, 15, 25):
        y0 = S(A0, -(k + 1) * db)[1]; y1 = S(A1, -(k + 1) * db)[1]
        print('plank seam / tile row %2d  slope=%.5f' % (k, (y0 - y1) / (S(A1, 0)[0] - S(A0, 0)[0])))
    print('band (curtain+backdrop) height / image height: left %.3f right %.3f' % (foot_y(0) / H, foot_y(W) / H))
    print('floor share of the picture (mean): %.3f' % (1 - ((foot_y(0) + foot_y(W)) / 2) / H))
    xs = (FRONT - (H - 1)) / slope
    print('front cardboard edge: cut off by the frame at the bottom left; it enters the picture at x = %.0f px (y = %d) and is seen along the right part only; at the right end it is %.1f px above the bottom edge' % (xs, H - 1, H - (FRONT - slope * W)))

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--preset', default='geki', choices=sorted(PRESETS))
    ap.add_argument('--out')
    ap.add_argument('--guide', action='store_true')
    ap.add_argument('--measure', action='store_true')
    a = ap.parse_args()
    if a.measure:
        measure()
    if a.out:
        (guide() if a.guide else render(a.preset)).save(a.out)
