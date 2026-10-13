#!/usr/bin/env python3
"""戦闘画面サンプル素材の加工。
実行: uv run --with pillow --with numpy --with scipy python3 -I prepare_assets.py \
        --sheet SHEET.png --dragon DRAGON.png --bg BG.png --out OUTDIR
"""
import argparse, shutil
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage as ndi

MAX_H = 480      # 味方の最大高さ（4人共通の縮小率で適用）
DRAGON_LONG = 640


def blur_alpha(a, r):
    im = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8))
    return np.asarray(im.filter(ImageFilter.GaussianBlur(r)), dtype=np.float32) / 255


def cut_gray(rgb, tol=22):
    """外周から連結した灰色背景を抜く。戻り値: RGBA(float配列)"""
    h, w, _ = rgb.shape
    f = rgb.astype(np.float32)
    border = np.concatenate([f[0], f[-1], f[:, 0], f[:, -1]])
    bg = np.median(border, axis=0)
    # 背景は緩やかなグラデの可能性があるので、局所背景色を大きなメディアン風に近似: 単色距離+彩度
    dist = np.abs(f - bg).max(axis=2)
    sat = f.max(axis=2) - f.min(axis=2)
    lum = f.mean(axis=2)
    # 背景色に近い色 + 無彩色の暗めの灰色（足元の影）。外周連結のものだけ抜く
    shadow = ndi.binary_opening((sat < 10) & (lum > 135) & (lum <= bg.mean() - tol), iterations=2)
    bgish = (dist < tol) | shadow
    lab, _ = ndi.label(bgish)
    border_labels = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    bgmask = np.isin(lab, list(border_labels))
    fg = ~bgmask
    # 小さな孤立ノイズ除去
    lab2, n = ndi.label(fg)
    sizes = ndi.sum(fg, lab2, range(1, n + 1))
    keep = np.zeros(n + 1, bool)
    keep[1:] = sizes > 500
    fg = keep[lab2]
    core = ndi.binary_erosion(fg, iterations=2)
    alpha = blur_alpha(ndi.binary_erosion(fg, iterations=1).astype(np.float32), 1.0)
    # defringe: コア外の色は最近傍コア色で置換
    _, (iy, ix) = ndi.distance_transform_edt(~core, return_indices=True)
    col = f[iy, ix]
    col[core] = f[core]
    out = np.dstack([col, alpha * 255]).clip(0, 255).astype(np.uint8)
    return out, fg


def split_people(fg, expect=4):
    cols = fg.any(axis=0)
    lab, n = ndi.label(cols)
    # 近接(隙間<20px)を結合
    segs = [(np.where(lab == i)[0][0], np.where(lab == i)[0][-1]) for i in range(1, n + 1)]
    merged = []
    for s in segs:
        if merged and s[0] - merged[-1][1] < 20:
            merged[-1] = (merged[-1][0], s[1])
        else:
            merged.append(s)
    return merged


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet", required=True)
    ap.add_argument("--dragon", required=True)
    ap.add_argument("--bg", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)

    # --- 味方 ---
    sheet = np.asarray(Image.open(a.sheet).convert("RGB"))
    H = sheet.shape[0]
    full_rgba, full_fg = cut_gray(sheet)
    # 行を自動検出（行方向の投影で最初のかたまり＝一番上の行）
    rows = full_fg.any(axis=1)
    rl, rn = ndi.label(rows)
    if rn < 1:
        raise SystemExit("行が見つからない")
    ry = np.where(rl == 1)[0]
    rgba, fg = full_rgba[: ry[-1] + 6], full_fg[: ry[-1] + 6]
    # 上段のみ：行の境界を跨ぐ成分が無いよう、下端付近を確認
    segs = split_people(fg)
    if len(segs) != 4:
        raise SystemExit(f"人物が4つ見つからない: {segs}")
    crops = []
    for x0, x1 in segs:
        sub = fg[:, x0:x1 + 1]
        ys = np.where(sub.any(axis=1))[0]
        pad = 3
        y0, y1 = max(ys[0] - pad, 0), min(ys[-1] + pad, rgba.shape[0] - 1)
        crops.append(Image.fromarray(rgba[y0:y1 + 1, max(x0 - pad, 0):x1 + 1 + pad], "RGBA"))
    scale = min(MAX_H / max(c.height for c in crops), 1.0)
    for name, c in zip("abcd", crops):
        im = c.resize((round(c.width * scale), round(c.height * scale)), Image.LANCZOS)
        bb = im.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox()
        im = im.crop(bb)
        p = out / f"party-{name}.png"
        im.save(p)
        print(p, im.size)
    print("scale", scale)

    # --- ドラゴン ---
    d = Image.open(a.dragon).convert("RGB")
    f = np.asarray(d).astype(np.float32)
    R, G, B = f[..., 0], f[..., 1], f[..., 2]
    gain = G - np.maximum(R, B)
    alpha = 1 - np.clip((gain - 40) / 120, 0, 1)
    # 外周から連結していない緑ゲイン領域（本体内）は抜かない → 外周連結のみ透過
    bgish = gain > 40
    lab, _ = ndi.label(bgish)
    bl = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    ext = ndi.binary_dilation(np.isin(lab, list(bl)), iterations=3)
    alpha = np.where(ext, alpha, 1.0)
    # spill 除去
    lim = (R + B) / 2
    G2 = np.where(G > lim, lim + (G - lim) * 0.0, G)
    rgb = np.dstack([R, G2, B])
    # 半透明境界の色は不透明側へ寄せる（ハロ防止）
    solid = alpha > 0.98
    solid = ndi.binary_erosion(solid, iterations=1)
    _, (iy, ix) = ndi.distance_transform_edt(~solid, return_indices=True)
    near = rgb[iy, ix]
    edge = (alpha < 0.98) & (alpha > 0)
    rgb = np.where(edge[..., None], near, rgb)
    alpha = blur_alpha(ndi.binary_erosion(alpha > 0.5, iterations=1).astype(np.float32) * 0 + alpha, 0.6)
    im = Image.fromarray(np.dstack([rgb, alpha * 255]).clip(0, 255).astype(np.uint8), "RGBA")
    im = im.crop(im.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox())
    s = min(DRAGON_LONG / max(im.size), 1.0)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    p = out / "enemy-dragon.png"
    im.save(p)
    print(p, im.size)

    # --- 背景 ---
    shutil.copyfile(a.bg, out / "background.png")


if __name__ == "__main__":
    main()
