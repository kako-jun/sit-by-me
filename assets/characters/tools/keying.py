"""切り出しツール共通の透過処理。
key='alpha' : 透過のまま生成した RGBA をそのまま使う（既定の方式）
key='green' / 'magenta' : クロマキー背景を抜く（透過で返らなかったときの代替）
戻り値: (rgb float 配列, alpha 0..1 配列)"""
import numpy as np
from PIL import Image


def load(src, key):
    if key == 'alpha':
        a = np.asarray(Image.open(src).convert('RGBA')).astype(float)
        return a[..., :3], a[..., 3] / 255
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
    return out, alpha


def split(alpha, cell_of, min_body=2000):
    """画像全体を、コマごとの体へ振り分けたマスクにする（コマの枠では切らない）。
    体 = 濃い部分（alpha>0.5）のかたまりのうち、重心のあるコマで最大のもの。
    残りの見える画素（薄い光・にじみ・はみ出した刃や手足）は、画素ごとにいちばん近い体へ付ける。
    透過生成の光は薄く広がって隣のコマとつながるので、かたまり単位でなく画素単位で振り分ける。
    cell_of(cy, cx) -> コマの番号。戻り値: {コマ: bool マスク}"""
    from scipy import ndimage
    H, W = alpha.shape
    core = alpha > 0.5
    lab, n = ndimage.label(core)
    areas = ndimage.sum(core, lab, range(1, n + 1))
    cents = ndimage.center_of_mass(core, lab, range(1, n + 1))
    body = {}
    for li in range(1, n + 1):
        c = cell_of(*cents[li - 1])
        if areas[li - 1] >= min_body and (c not in body or areas[li - 1] > areas[body[c] - 1]):
            body[c] = li
    owner = np.zeros(alpha.shape, int)
    for i, li in enumerate(body.values(), 1):
        owner[lab == li] = i
    dist, (iy, ix) = ndimage.distance_transform_edt(owner == 0, return_indices=True)
    nearest = owner[iy, ix]
    visible = (alpha > 0.02) & (dist < W / 6)
    # 小さな孤立ノイズを消す
    vlab, vn = ndimage.label(visible)
    vareas = ndimage.sum(visible, vlab, range(1, vn + 1))
    visible &= np.isin(vlab, [i + 1 for i, v in enumerate(vareas) if v >= 40])
    # 足元（体の濃い部分の下端）より下に丸ごと離れて浮いている小さな塊（光の粒）は捨てる。
    # 付いたままだと切り抜きの下端が足でなくなり、台座から浮いて見える。
    # 足元の上からつながる光や、跳んだポーズの足の下を回る大きな光の帯は残す
    masks = {}
    for i, (c, li) in enumerate(body.items(), 1):
        m = visible & (nearest == i)
        bottom = np.where((lab == li).any(axis=1))[0].max()
        mlab, mn = ndimage.label(m, structure=np.ones((3, 3)))
        tops = ndimage.minimum(np.arange(H)[:, None] * np.ones((1, W), int), mlab, range(1, mn + 1))
        sizes = ndimage.sum(m, mlab, range(1, mn + 1))
        m &= np.isin(mlab, [j + 1 for j in range(mn) if tops[j] <= bottom + 4 or sizes[j] >= 300])
        masks[c] = m
    return masks
