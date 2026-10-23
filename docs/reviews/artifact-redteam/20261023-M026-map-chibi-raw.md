# M026 map chibi raw-image review

- Date: 2026-10-23
- Reviewer: `/root/sprite_prompt_review` (independent)
- Stage: `raw-image`
- Target: M026 メモドンコリロ, Kenrokuen boss-rush candidate
- Sources: `docs/monsters.md` M026 row; `docs/dungeon-enemies.md` §6; `assets/images/enemies/M026.webp`; prompt and generation plan in Sit by Me Issue #152 comments `6356628588` and `6356641607`
- Worktree state: reviewed uncommitted raw artifact; no commit hash

## Artifact

`~/.codex/generated_images/01a1665b-0d55-76a1-a2cb-e8e9b515c6b6/exec-eeec4c62-7577-46a2-9f15-875dfd217285.png`

SHA-256: `933744f40cca726930d59c1fcf3b0f5cdd5297980427972c6d888a564e4f3be8`

1312×1199 PNG RGBA; alpha minimum 0. All four corner pixels have alpha 0. Alpha-positive bbox is `1282×1160`, offset `(0,39)` due detached one-level-alpha pixels. Reviewer measured the main silhouette at threshold >1/255 as approximately `878×991` at `(220,87)`, leaving about 220 px left, 213 px right, 87 px top, and 121 px bottom. The subject is not cropped.

## Checks and findings

- **Identity: pass.** One large red-orange eye, rounded charcoal body, rounded flame-like hair tufts, and four short rounded support feet are present. Fine blood vessels, detailed fingers, and horror treatment are removed.
- **Style and pose: pass.** Low-proportion and cute, with visible color and volume; not a shadow or flat icon. Upright and mostly frontal. A slight 3/4 deviation is acceptable per kako-jun's instruction on 2026-10-23 and differs substantially from the crouched diagonal battle pose.
- **Spoiler reduction: pass for the requested transformation.** Core identity cues remain, but anatomy and surface details are simplified. The exact final in-game spoiler/readability judgement remains for kako-jun.
- **Transparency: minor edge noise.** Corners pass strict alpha=0. Isolated alpha=1/255 pixels remain at left edge `x=0, y=781–786` and bottom edge `y=1198` (30 pixels). They are outside the main silhouette.
- **Small-display legibility: pending.** The exact MAP ID and rendered pixel size are not assigned. At source size the eye, four feet, and broad hair masses remain separable; final downscale check is deferred until a display size is specified.

## Disposition

Raw-image review passes with the minor detached-edge-pixel note. The PNG remains an unadopted candidate outside the repository. This review does not set the asset to `ready` or establish its exact MAP placement.
