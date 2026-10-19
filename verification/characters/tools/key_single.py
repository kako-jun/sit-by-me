"""1体だけの画像を透過にし、タイトに切り抜く（グリッドで作れなかったコマの差し替え用）。
usage: key_single.py src.png out.webp alpha|green|magenta [flip]"""
import sys, os
import numpy as np
from PIL import Image
from scipy import ndimage

src, dst, key = sys.argv[1:4]
flip = len(sys.argv) > 4 and sys.argv[4] == 'flip'
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import keying
out, alpha = keying.load(src, key)
th = 0.02 if key == 'alpha' else 0.08
# 小さなノイズのかたまりを消す
fg = alpha > th
lab, n = ndimage.label(fg)
areas = ndimage.sum(fg, lab, range(1, n + 1))
alpha = alpha * np.isin(lab, [i + 1 for i, v in enumerate(areas) if v >= 40])
ys, xs = np.where(alpha > th)
rgba = np.dstack([out, alpha * 255]).clip(0, 255).astype(np.uint8)
im = Image.fromarray(rgba[ys.min():ys.max() + 1, xs.min():xs.max() + 1])
if flip:
    im = im.transpose(Image.FLIP_LEFT_RIGHT)
im.save(dst, 'WEBP', quality=85)
print('ok', dst, im.size)
