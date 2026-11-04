"""アプリストア刀一覧用の派生画像の切り出し試作（sit-by-me #26、決定 SIT.appstore-weapon-list-image-is-derived-from-masters）。

刀マスター（assets/images/weapons/masters/*.png）から機械的に派生画像を作る。採用版が決まるまで画像はリポに入れない。
variant = 向き(diag/horiz) x にじみ(keep/cut/tight)。出力は --out の下に variant ごとのディレクトリと contact sheet。

usage: uv run --with pillow --with numpy python3 -I scripts/derive_blade_appstore.py --out DIR
"""
import argparse
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

REPO = Path(__file__).resolve().parents[1]
MASTERS = REPO / 'assets/images/weapons/masters'
PAD = 8
CANVAS = {'diag': (384, 256), 'horiz': (512, 128)}  # 向きごとの統一キャンバス（contain で収める）
CORE_ALPHA = 128  # 向きの推定・にじみ除去の「刀の実体」しきい値


def axis_angle_deg(alpha):
    """alpha>=CORE_ALPHA の画素の主成分軸の角度（度、画像座標 y 下向き、x 軸から）。"""
    ys, xs = np.nonzero(alpha >= CORE_ALPHA)
    pts = np.stack([xs - xs.mean(), ys - ys.mean()])
    w, v = np.linalg.eigh(np.cov(pts))
    vx, vy = v[:, 1]
    if vx < 0:
        vx, vy = -vx, -vy
    return math.degrees(math.atan2(vy, vx))


def apply_glow(im, mode):
    a = np.array(im.getchannel('A')).astype(np.float32)
    if mode == 'keep':
        pass
    elif mode == 'cut':  # 半透明（にじみ）を落とし、実体だけ不透明にする
        a = np.where(a >= 200, 255, 0)
    elif mode == 'tight':  # 縁を絞る: 下側を持ち上げて切り、1px 収縮
        a = np.clip((a - 96) / (224 - 96), 0, 1) * 255
        a = np.array(Image.fromarray(a.astype(np.uint8)).filter(ImageFilter.MinFilter(3))).astype(np.float32)
    else:
        raise ValueError(mode)
    out = im.copy()
    out.putalpha(Image.fromarray(a.astype(np.uint8)))
    return out


def trim(im, thr=8):
    box = im.getchannel('A').point(lambda v: 255 if v > thr else 0).getbbox()
    return im.crop(box)


def make(im, orient, glow):
    im = im.convert('RGBA')
    if orient == 'horiz':
        ang = axis_angle_deg(np.array(im.getchannel('A')))
        im = im.rotate(ang, resample=Image.BICUBIC, expand=True)  # 反時計回りに ang 度 = 軸を水平へ
    im = trim(apply_glow(im, glow))
    cw, ch = CANVAS[orient]
    s = min((cw - 2 * PAD) / im.width, (ch - 2 * PAD) / im.height)
    im = im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))), Image.LANCZOS)
    canvas = Image.new('RGBA', (cw, ch), (0, 0, 0, 0))
    canvas.alpha_composite(im, ((cw - im.width) // 2, (ch - im.height) // 2))
    return canvas


def checker(w, h, c=16):
    bg = Image.new('RGB', (w, h), (58, 58, 62))
    d = ImageDraw.Draw(bg)
    for y in range(0, h, c):
        for x in range(0, w, c):
            if (x // c + y // c) % 2:
                d.rectangle([x, y, x + c - 1, y + c - 1], fill=(78, 78, 84))
    return bg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    out = Path(ap.parse_args().out)
    variants = [(o, g) for o in ('diag', 'horiz') for g in ('keep', 'cut', 'tight')]
    files = sorted(MASTERS.glob('*.png'))
    cell_w, cell_h, label_w = 260, 136, 230
    sheet = Image.new('RGB', (label_w + cell_w * len(variants), 24 + cell_h * len(files)), (20, 20, 22))
    d = ImageDraw.Draw(sheet)
    for j, (o, g) in enumerate(variants):
        d.text((label_w + j * cell_w + 6, 6), f'{o}-{g}', fill=(230, 230, 230))
    for i, f in enumerate(files):
        src = Image.open(f)
        d.text((6, 24 + i * cell_h + 6), f.name.replace('-reference', '').replace('.png', ''), fill=(230, 230, 230))
        for j, (o, g) in enumerate(variants):
            res = make(src, o, g)
            vd = out / f'{o}-{g}'
            vd.mkdir(parents=True, exist_ok=True)
            res.save(vd / f.name.replace('.png', '.webp').replace('-reference', ''), lossless=True)
            sc = min((cell_w - 4) / res.width, (cell_h - 4) / res.height)
            th = res.resize((round(res.width * sc), round(res.height * sc)), Image.LANCZOS)
            cell = checker(cell_w, cell_h)
            cell.paste(th, ((cell_w - th.width) // 2, (cell_h - th.height) // 2), th)
            sheet.paste(cell, (label_w + j * cell_w, 24 + i * cell_h))
    sheet.save(out / 'contact-sheet.png')
    print(out / 'contact-sheet.png', sheet.size)


if __name__ == '__main__':
    main()
