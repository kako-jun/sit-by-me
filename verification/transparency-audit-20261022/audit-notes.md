# Enemy transparency audit — 2026-10-22

The green-background contact sheet covers all 33 enemy image files modified on 2026-10-22 in `assets/images/enemies/`. Each has an alpha channel with transparent pixels; the sheet composites those pixels over bright green.

- M208 was already the transparent onryo sprite in `HEAD`; no replacement was needed. Its dimensions are 1145×1374.
- M210 had an opaque checker background. It was replaced with the transparent red-paper variant `exec-09301265-498f-44e9-b21b-83aac9bd4715.png` (1024×1536).
- M033 has no canonical image file yet. An earlier transparent source `exec-32087d33-a421-4241-bbe6-3e5f4a6da286.png` remains, but it is an obsolete draft that appears to have an extra head. The latest two-head candidate `exec-04373558-828a-47da-8bea-50082977899b.png` has checkerboard baked in. The older image was not substituted because it does not match the accepted design.
