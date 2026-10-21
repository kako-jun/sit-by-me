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

ap = argparse.ArgumentParser()
ap.add_argument('--base', required=True)
ap.add_argument('--raw', required=True)
ap.add_argument('--rects')
ap.add_argument('--mask')
ap.add_argument('--out', required=True)
ap.add_argument('--feather', type=float, default=3.0)
a = ap.parse_args()
B = Image.open(a.base).convert('RGB')
R = Image.open(a.raw).convert('RGB')
assert B.size == R.size, ('size mismatch', B.size, R.size)
if a.mask:
    m = np.array(Image.open(a.mask).convert('L')) > 0
    alpha_src = Image.fromarray((m * 255).astype('uint8'))
else:
    alpha_src = Image.new('L', B.size, 0)
    dr = ImageDraw.Draw(alpha_src)
    for s in a.rects.split(';'):
        dr.rectangle(tuple(int(v) for v in s.split(',')), fill=255)
    m = np.array(alpha_src) > 0
out = ~m
A = np.array(B).astype(int)
Rr = np.array(R).astype(int)
d = np.abs(A - Rr).max(axis=2)
print('raw vs base outside mask: differing', int((d[out] > 0).sum()), 'of', int(out.sum()), 'mean', round(float(d[out].mean()), 2), 'max', int(d[out].max()), '>8:', int((d[out] > 8).sum()))
alpha = alpha_src.filter(ImageFilter.GaussianBlur(a.feather))
res = Image.composite(R, B, alpha)
res.save(a.out)
dd = np.abs(np.array(res).astype(int) - A).max(axis=2)
print('final vs base outside mask: differing', int((dd[out] > 0).sum()), '; total changed', int((dd > 0).sum()))
