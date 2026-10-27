"""Masked edit paste-back with a numeric check (used for v9->v11 of the main hall, the exterior v7, TRM-02 v3).

An imagegen edit may repaint the WHOLE picture even when only a masked region should change. Paste back only the masked region
into the canonical image (feathered edge) and verify numerically how many pixels outside the mask changed. The paste-back is a
post-edit step: record it in the adoption record, and verify the authenticity of the imagegen output separately.

Usage:
  uv run --with pillow --with numpy python3 -I .claude/skills/sit-field-background/tools/pasteback.py \
      --base canonical.png --raw edited-raw.png --rects "x0,y0,x1,y1;..." [--mask mask.png] --out result.png [--feather 3]
  The masked region is given by rectangles (inner area to take from the raw output) or by a mask image (white = editable).
Prints: raw vs base outside the mask (how much the model changed outside), final vs base outside the mask (should be ~0), total changed.
"""
import argparse
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--base', required=True)
    ap.add_argument('--raw', required=True)
    source = ap.add_mutually_exclusive_group(required=True)
    source.add_argument('--rects')
    source.add_argument('--mask')
    ap.add_argument('--out', required=True)
    ap.add_argument('--feather', type=float, default=3.0)
    a = ap.parse_args()
    if a.feather < 0:
        ap.error('--feather must be nonnegative')
    B = Image.open(a.base).convert('RGB')
    R = Image.open(a.raw).convert('RGB')
    if B.size != R.size:
        ap.error(f'size mismatch: {B.size} != {R.size}')
    if a.mask:
        mask_image = Image.open(a.mask).convert('L')
        if mask_image.size != B.size:
            ap.error(f'mask size mismatch: {mask_image.size} != {B.size}')
        m = np.array(mask_image) > 0
        alpha_src = Image.fromarray((m * 255).astype('uint8'))
    else:
        alpha_src = Image.new('L', B.size, 0)
        dr = ImageDraw.Draw(alpha_src)
        for s in a.rects.split(';'):
            rect = tuple(int(v) for v in s.split(','))
            if len(rect) != 4 or not (0 <= rect[0] < rect[2] < B.width and 0 <= rect[1] < rect[3] < B.height):
                ap.error('rectangles must be nonempty and inside the image')
            dr.rectangle(rect, fill=255)
        m = np.array(alpha_src) > 0
    out = ~m
    A = np.array(B).astype(int)
    Rr = np.array(R).astype(int)
    d = np.abs(A - Rr).max(axis=2)
    print('raw vs base outside mask: differing', int((d[out] > 0).sum()), 'of', int(out.sum()), 'mean', round(float(d[out].mean()), 2) if out.any() else 0, 'max', int(d[out].max()) if out.any() else 0, '>8:', int((d[out] > 8).sum()))
    alpha = alpha_src.filter(ImageFilter.GaussianBlur(a.feather))
    # Feather inward: pixels outside the explicitly allowed mask retain the base exactly.
    alpha_array = np.array(alpha)
    alpha_array[~m] = 0
    alpha = Image.fromarray(alpha_array)
    res = Image.composite(R, B, alpha)
    res.save(a.out)
    dd = np.abs(np.array(res).astype(int) - A).max(axis=2)
    print('final vs base outside mask: differing', int((dd[out] > 0).sum()), '; total changed', int((dd > 0).sum()))


if __name__ == "__main__":
    main()
