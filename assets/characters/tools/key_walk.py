"""4行x3列のクロマキー歩きグリッドを透過にし、12コマを同じ大きさの枠へ足元そろえで切り出す。
usage: key_walk.py grid.png outdir name green|magenta ROWS
ROWS は上の行から順に向きを4つ、カンマ区切りで（例: down,right,left,up）。生成では2行目と3行目の向きが入れ替わることがあるので、顔を拡大して確かめて指定する。
出力: {name}-walk-{down,left,right,up}-{1,2,3}.png"""
import sys, os
import numpy as np
from PIL import Image
from scipy import ndimage

src, outdir, name, key, rows = sys.argv[1:6]
rows = rows.split(',')
a = np.asarray(Image.open(src).convert('RGB')).astype(float)
r, g, b = a[..., 0], a[..., 1], a[..., 2]
k = g - np.maximum(r, b) if key == 'green' else np.minimum(r, b) - g
alpha = 1 - np.clip((k - 40) / 80, 0, 1)
out = a.copy()
if key == 'green':
    out[..., 1] = np.minimum(g, np.maximum(r, b) + 10)
else:
    out[..., 0] = np.where(k > 0, np.minimum(r, g + 30), r)
    out[..., 2] = np.where(k > 0, np.minimum(b, g + 30), b)
H, W = alpha.shape
rgba = np.dstack([out, alpha * 255]).clip(0, 255).astype(np.uint8)

# 絵はセルの境界をまたぐことがあるので、画像全体でかたまりを見つけ、
# 重心のあるコマの最大のかたまりを体とし、残りの破片はいちばん近い体へ付ける（key_grid.py と同じ方式）
fg = alpha > 0.08
lab, n = ndimage.label(fg)
areas = ndimage.sum(fg, lab, range(1, n + 1))
cents = ndimage.center_of_mass(fg, lab, range(1, n + 1))
def cell_of(cy, cx):
    return (int(min(3, cy // (H / 4))), int(min(2, cx // (W / 3))))
body = {}
for li in range(1, n + 1):
    c = cell_of(*cents[li - 1])
    if areas[li - 1] >= 2000 and (c not in body or areas[li - 1] > areas[body[c] - 1]):
        body[c] = li
if len(body) != 12:
    sys.exit(f'found {len(body)} bodies, expected 12')
dist = {c: ndimage.distance_transform_edt(lab != li) for c, li in body.items()}
masks = {c: lab == li for c, li in body.items()}
for li in range(1, n + 1):
    if li in body.values() or areas[li - 1] < 40:
        continue
    m = lab == li
    ys, xs = np.where(m)
    y, x = ys[len(ys) // 2], xs[len(xs) // 2]
    c = min(body, key=lambda c: dist[c][y, x])
    if dist[c][y, x] < W / 6:
        masks[c] |= m
frames = {}
for c, m in masks.items():
    f = rgba.copy()
    f[..., 3] = np.where(m, f[..., 3], 0)
    ys, xs = np.where(f[..., 3] > 20)
    frames[c] = f[ys.min():ys.max() + 1, xs.min():xs.max() + 1]

# 全コマ共通の枠（最大幅・最大高さ）に、横は中央・縦は足元（下端）でそろえる
fw = max(f.shape[1] for f in frames.values())
fh = max(f.shape[0] for f in frames.values())
os.makedirs(outdir, exist_ok=True)
for (ri, ci), f in frames.items():
    canvas = Image.new('RGBA', (fw, fh), (0, 0, 0, 0))
    canvas.paste(Image.fromarray(f), ((fw - f.shape[1]) // 2, fh - f.shape[0]))
    canvas.save(os.path.join(outdir, f'{name}-walk-{rows[ri]}-{ci + 1}.png'))
print('ok', name, fw, fh)
