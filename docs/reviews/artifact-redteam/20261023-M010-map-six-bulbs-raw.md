# M010 six-bulb map sprite raw-image review

- Date: 2026-10-23
- Reviewer: `/root/sprite_prompt_review` (independent)
- Stage: `raw-image`
- Target: M010 オミクロン株, stomach shield-role boss
- Sources: `docs/monsters.md` M010 row; `docs/dungeon-enemies.md` M010 assignment; `assets/images/enemies/M010.webp`; exact prompt and generation record in Issue #152 comments `6356739111`, `6356749625`, and `6356770656`
- Worktree state: reviewed uncommitted raw artifact; no commit hash

## Artifact

`~/.codex/generated_images/01a1665b-0d55-76a1-a2cb-e8e9b515c6b6/exec-91e8f0f3-65ac-4b51-92ac-af5c8b9ddc7c.png`

SHA-256: `1d07829c05b2ef9388d494352f660846ab8a1a1fe037cb96468e3b6d2e14fe18`

1536×1024 PNG source RGBA; alpha minimum 0; all four corner pixels have alpha 0. Alpha-positive bbox is `1487×996`, offset `(0,0)`; reviewer confirmed a clear visible transparent margin and intact silhouette. Apparent aura is transparent outside the subject and between the spokes; only a narrow red edge tint is contiguous with the creature.

## Checks and findings

- **Identity: pass.** Broad flattened pale core with three large openings and six distinct radial red protrusions, each ending in one separate red bulb.
- **Low-resolution simplification: pass.** All six bulbs and three openings are countable. No bulb clusters, fine web, extra face, limbs, or props.
- **Pose/composition: pass.** New frontal symmetric map composition, not the battle camera or pose.
- **Transparency: pass.** RGBA, alpha minimum 0, four transparent corners, complete silhouette within visible margins.
- **Minor style note.** Soft gradients and subtle texture remain; image is considerably simpler than the battle source.
- **Actual-scale check: pending.** No MAP display size is assigned yet.

## Disposition

Raw-image review passes with no blocker or major finding. kako-jun approved the candidate 2026-10-23. Canonical field asset: `assets/images/enemies/M010-field.webp`; MAP placement remains unassigned.
