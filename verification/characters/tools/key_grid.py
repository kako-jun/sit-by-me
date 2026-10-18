"""3x3 のポーズグリッドを透過にし、重心のコマへ振り分けて切り出す（枠をはみ出した刃・手足・光も切らない）。
usage: key_grid.py grid.png outdir name alpha|green|magenta [flip_idx,...]
alpha は透過のまま生成したグリッド（既定の方式）、green/magenta はクロマキー背景（keying.py）"""
import sys, os
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import keying

src, outdir, name, key = sys.argv[1:5]
flips = set(int(x) for x in sys.argv[5].split(',')) if len(sys.argv) > 5 and sys.argv[5] else set()
NAMES = ['idle', 'ready', 'step', 'slash', 'hurt', 'down', 'cast', 'special', 'victory']
out, alpha = keying.load(src, key)
H, W = alpha.shape
cells = keying.split(alpha, lambda cy, cx: int(min(2, cx // (W / 3)) + 3 * min(2, cy // (H / 3))))
rgba = np.dstack([out, alpha * 255]).clip(0, 255).astype(np.uint8)
os.makedirs(outdir, exist_ok=True)
for i, nm in enumerate(NAMES):
    m = cells.get(i)
    if m is None or not m.any():
        sys.exit(f'EMPTY {nm}')
    ys, xs = np.where(m)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    sub = rgba[y0:y1, x0:x1].copy()
    sub[..., 3] = np.where(m[y0:y1, x0:x1], sub[..., 3], 0)
    im = Image.fromarray(sub, 'RGBA')
    if i in flips:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    im.save(f'{outdir}/{name}-{nm}.png')
print('ok', name)
