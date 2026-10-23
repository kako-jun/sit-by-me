# M010 low-resolution map sprite raw-image review

- Date: 2026-10-23
- Reviewer: `/root/sprite_prompt_review` (independent)
- Stage: `raw-image`
- Target: M010 オミクロン株, stomach shield-role boss
- Sources: `docs/monsters.md` M010 row; `docs/dungeon-enemies.md` M010 assignment; `assets/images/enemies/M010.webp`; exact prompt and generation record in Issue #152 comment `6356633562`
- Worktree state: reviewed uncommitted raw artifact; no commit hash

## Artifact

`~/.codex/generated_images/01a1665b-0d55-76a1-a2cb-e8e9b515c6b6/exec-b8c22cfb-dfed-45f9-8ecf-37af3204d75c.png`

SHA-256: `00c7f0d8a8973c38fc638caefe0cac00199f4cfc2816aba3a6503af8e161f262`

1312×1199 PNG RGBA; alpha minimum 0; all four corner pixels alpha 0. Alpha-positive bbox is `1300×1190`, offset `(0,0)` due stray flecks. The main subject is inset and not cropped; independent review estimated its >1% alpha bbox as `1102×1103` at `(111,48)`, leaving about 111 px left, 99 px right, 48 px top, and 48 px bottom.

## Checks and findings

- **Identity: pass.** Pale-gray porous viral core with rounded red protrusions; no face or limbs; distinct from M132's tendrils.
- **Low-resolution simplification: pass with caveat.** Six primary thick spokes are countable. Each endpoint remains a cluster of roughly 3–5 round lobes. The core has fewer, broader openings and bridges than the battle master, but still retains small pores, surface texture, and glossy highlights. Actual display-size legibility cannot be conclusively checked before map scale is assigned.
- **Pose/composition: pass.** Near-radial, frontal new map composition; no battle framing or effects.
- **Transparency: pass with minor note.** RGBA and all four corners transparent. Detached red flecks remain outside the subject (above the top cluster and near the sides). They do not crop the subject.

## Disposition

Raw-image review has no blocker or major finding. The candidate remains unadopted outside the repository. Map display size and exact MAP placement are not set by this review.
