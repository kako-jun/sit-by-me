"""4行x3列の歩きグリッドを透過にし、12コマを同じ大きさの枠へ足元そろえで切り出す。
usage: key_walk.py grid.png outdir name alpha|green|magenta ROWS
ROWS は上の行から順に向きを4つ、カンマ区切りで（例: down,right,left,up）。生成では2行目と3行目の向きが入れ替わることがあるので、顔を拡大して確かめて指定する。
出力: {name}-walk-{down,left,right,up}-{1,2,3}.png"""
import sys, os
import numpy as np
from PIL import Image

src, outdir, name, key, rows = sys.argv[1:6]
rows = rows.split(',')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import keying
out, alpha = keying.load(src, key)
H, W = alpha.shape
rgba = np.dstack([out, alpha * 255]).clip(0, 255).astype(np.uint8)

# 絵はセルの境界をまたぐので、コマの枠では切らず、重心のコマの体へ画素ごとに振り分ける（keying.split）
masks = keying.split(alpha, lambda cy, cx: (int(min(3, cy // (H / 4))), int(min(2, cx // (W / 3)))))
if len(masks) != 12:
    sys.exit(f'found {len(masks)} bodies, expected 12')
frames = {}
for c, m in masks.items():
    f = rgba.copy()
    f[..., 3] = np.where(m, f[..., 3], 0)
    ys, xs = np.where(m)
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
