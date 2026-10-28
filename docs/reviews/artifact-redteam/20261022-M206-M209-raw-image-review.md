# M206 / M209 raw-image independent review — 2026-10-22

- Stage: generated PNG candidates only; human adoption remains pending. No prompt, specification, candidate, or canonical image was changed by this review.
- Basis: `.claude/skills/sit-enemy-sprite/SKILL.md`, `docs/monsters.md` M206/M209 and §3-7, `docs/art-direction.md` line 94, `docs/assets-policy.md`, the two complete 2026-10-22 prompts, and both initial/revised prompt-contract review reports. I inspected the source PNGs at original resolution, their white-background diagnostic composites, and the adopted `M206.webp` identity reference.
- Both prompts passed the revised *pre-generation* review. The findings below concern the generated pixels and do not change that prompt verdict.

## Measurement method and provenance

`file` reports 1024×1536, 8-bit RGBA PNG for each candidate. ImageMagick `-alpha extract` measured alpha extrema and corners; `-threshold 0 -trim` measured the exact `alpha > 0` bounding box. To distinguish the figure from scattered low-alpha background marks, `-threshold 50% -connected-components 8` measured the largest connected component of pixels with alpha above 50%. This second box is a silhouette estimate, not a replacement for the exact alpha-positive box. The source PNGs were not modified; white composites existed only under `/tmp` for inspection.

| Candidate | SHA-256 of PNG | Alpha zero pixels | Alpha range | Four corner alpha | Exact `alpha > 0` bbox | Main `alpha > 50%` component |
|---|---|---:|---|---|---|---|
| M206 `exec-5b7f8edf-9bc0-4fbb-bc7a-1bf8c4ea2d19.png` | `993b823d61709090cfa4d7dac6f2b2ee66ac160d87a3ed5bdc1b6d0c088964f1` | 1,155,920 / 1,572,864 | 0–254 / 255 | 0, 0, 0, 0 | `1010×1520+0+0` | `955×1346+51+86` |
| M209 `exec-076d1aea-a11f-42a8-92e6-42cd02902231.png` | `2367370575271c245e332e1cb0423b544eb99da68b72e8e71c58e40a7f4ce1f6` | 1,073,184 / 1,572,864 | 0–254 / 255 | 0, 0, 0, 0 | `1016×1491+0+0` | `986×1213+26+32` |

Full source paths:

- M206: `［ローカルパス省略］/exec-5b7f8edf-9bc0-4fbb-bc7a-1bf8c4ea2d19.png`
- M209: `［ローカルパス省略］/exec-076d1aea-a11f-42a8-92e6-42cd02902231.png`

Prompt SHA-256: M206 `fc5515fd772aa0ff161522b89356f09ea7fbb588a4c747d90f3364b25d40ac3f`; M209 `e1655579c6a0e257b7a3890f107e9018c4a6118d476feb8e6928d492cf9031e2`. The read-only adopted M206 reference `assets/images/enemies/M206.webp` has SHA-256 `8a625c3456ef5f2df7d37afc8f810fe906bc8c2e92a1831061bee6fb4e9df263`.

## M206 — running ninja puppet

**Verdict: MAJOR; hold adoption of this candidate.**

| Check | Severity | Pixel evidence |
|---|---|---|
| Source identity and material | Pass | Same blank angular mask, tied head pieces, dark carved wood plates, ball joints, and articulated hands/feet as the adopted reference. It reads as a crafted display puppet, not a living person. No cloth, skin, weapon, writing, logo, acrylic base, or ground shadow is visible. |
| Running arm strike | Pass | Torso leans forward; the rightward arm ends in a closed fist thrust toward `+x`, while the opposite fist is drawn back. One leg reaches forward and the other extends behind in an airborne running stride. Head, hands, and both feet are complete rather than visibly cropped. |
| Head and torso direction | Pass, with measurement limit | The mask and torso show frontal and side facets, and the action goes toward `+x`; neither reads as a pure 90° right profile. A 2D render does not establish the exact 45° yaw numerically. |
| Grid and canvas | Pass | The PNG is 1024×1536 and the tall action silhouette is consistent with the logical `1x2` class. Pixel aspect ratio is not the grid definition. |
| 48 px silhouette margin | **Major** | The main alpha-above-50% component occupies x=51–1005 and y=86–1431. Its right margin is only **18 px** (48 required), at the forward fist. The silhouette is visually complete but too close to that edge. The exact `alpha > 0` box reaches the top and left edges because of background marks. |
| Transparent isolation | **Major** | Alpha zero exists, and all corners are zero, so RGBA transparency is real. On white, many scattered dark flecks remain outside the puppet across the frame, including near the upper-left, middle-right, and lower half. They are source pixels with positive alpha, not a viewer checkerboard. The exact alpha-positive box begins at `(0,0)` and leaves only 14 px at right and 16 px at bottom. This is not a clean isolated enemy cutout. |

## M209 — airborne kunoichi puppet

**Verdict: MAJOR; hold adoption of this candidate.**

| Check | Severity | Pixel evidence |
|---|---|---|
| Source identity and material | Pass | The blank carved wooden mask, exposed hands, ball joints at neck/arms/hips/knees, and hard wooden foot pieces make it read as an articulated object rather than a person. The blue fabric is over the puppet; no human skin, eyes, real face, weapon, writing, logo, acrylic base, or contact shadow is visible. |
| Distinctive color and action | Pass | Woven light water-blue garment dominates, with dark-blue trim; it is plainly different from M206's dark bare wood. The rightward leg is extended in a flying kick, the other leg is folded beneath, and the arms counterbalance. Neither foot touches a floor; no floor is depicted. The head, both hands, feet, and fabric ends appear complete. |
| Head and torso direction | Pass, with measurement limit | The wooden mask has a frontal plate and angled side contour; the chest/shoulders show front and side surfaces, and the kick points toward `+x`. It is not an unambiguous true right profile. The exact 45° yaw cannot be measured reliably from this single projection. |
| Grid and canvas | Pass | 1024×1536 portrait canvas and tall airborne figure are consistent with logical `gridClass 1x2`. The kick makes a broad figure within that portrait canvas, which the grid rule permits. |
| 48 px silhouette margin | **Major** | The main alpha-above-50% component occupies x=26–1011 and y=32–1244: **26 px left, 12 px right, 32 px top**. The left hand, rightward hand/foot, and top fabric violate the 48 px prompt margin. No obvious part is actually cut off. |
| Transparent isolation | **Major** | Alpha zero and four transparent corners are present. White compositing still reveals isolated dark specks beyond the puppet, including around the top, right, and below the rear foot. The exact `alpha > 0` box starts at `(0,0)` and extends to x=1015 and y=1490 because of these positive-alpha marks. The background is not a clean isolated cutout. |

## Review conclusion

The intended enemy designs and attack poses are readable in both candidates. The PNGs fail their explicit 48 px framing requirement, and positive-alpha stray marks remain around both figures. These are output defects, so the revised prompt approvals cannot be treated as image approval. Keep both generated candidates available for human comparison; leave `assets/images/enemies/M206.webp`, any M209 canonical path, and adoption/`ready` state unchanged until kako-jun decides.
