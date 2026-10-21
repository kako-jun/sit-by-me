# S006 第1形態 raw-image review

- Reviewer: independent red-team reviewer (not the specification, prompt, image, or prior-review author)
- Stage: `raw-image`
- Target: S006 第1形態 `S006-cloud.webp` 候補
- Disposition: **pass** for raw-image stage; author may save this human-approved candidate to the canonical path. This is not a WebP, adoption, or runtime verification.

## Artifact inspected

- Raw image: `/home/kako-jun/.codex/generated_images/01a15d7a-cc03-7c12-b781-c681f515408c/exec-f1ad40a1-0bf8-41ab-99d4-62367974f1fc.png`
- SHA-256: `b8b675f091d06a6d4f65d27fa626db97c9114156393f659d877f190557ee1477`
- Dimensions/mode: 1536×1024, RGBA, sRGB, 8-bit/channel
- Alpha: minimum 0, maximum 254/255; all four corner pixels are `srgba(0,0,0,0)`.
- Nonzero-alpha bounding rectangle: `(x=0, y=0, width=1536, height=1024)`. The recorded edge residue is at most alpha 1/255; the cloud silhouette itself is visibly inset from every edge and is not cut off. Edge contact is recorded for human review, not treated as automatic failure under the summon skill.
- Source prompt: Issue #141 comment [6311998804](https://github.com/kako-jun/sit-by-me/issues/141#issuecomment-6311998804); raw artifact metadata and human visual approval: #141 comment [6312060335](https://github.com/kako-jun/sit-by-me/issues/141#issuecomment-6312060335). The user subsequently specified the gray-to-yellow-to-orange progression; the visible first stage is gray.

## Canonical sources inspected

- `.claude/skills/sit-artifact-redteam/SKILL.md`
- `.claude/skills/sit-summon-sprite/SKILL.md`
- `docs/content-registry.md` (summon ID and prompt assembly rules)
- `docs/monsters.md` S006 row (line 88) and summon grid rows (lines 249–251)
- `docs/story.md` final battle sequence (cloud cores, then the cloud-entangled thunder dragon)
- `docs/art-direction.md` S006 four-stage description (line 130)
- `docs/assets-policy.md` summon-master transparency and no-base/no-outline/no-shadow rules
- Issue #141 body and comments, including the current stage-one prompt and stage-one-only exclusion for gold-leaf-like abstract clouds
- Issue #78: thunder dragon is a “竜” echoing M001 in shape/color; M003 is a separate “龍” motif

## Checks and evidence

- **Stage-one subject and palette — pass.** The image shows one large, layered gray cumulonimbus with a broad anvil crown, floating against transparent pixels. No yellow/orange lightning or other later-stage element is visible. This matches the current S006 row and art-direction stage-one text.
- **Stage-one exclusions — pass.** At original resolution, there is no gold-leaf-like abstract cloud motif, circular abyss/space opening, dragon or animal silhouette, skull, visible lightning, rain, moon, stars, landscape, horizon, text, frame, base, or ground shadow. The surrounding dark appearance in the viewer is not an opaque sky panel: all four actual corner alpha values are zero.
- **Full visibility — pass with edge note.** The complete cloud mass is visible with a narrow transparent margin; no part of its silhouette is clipped. The faint nonzero alpha residue along the outer canvas edges is at most 1/255, as recorded in #141. Human review of the displayed image also accepted this candidate.
- **Declared grid class — recorded.** S006 stage one is explicitly `2x3` in `docs/monsters.md`; this is a combat-cell class and does not impose a pixel aspect ratio. The 1536×1024 canvas is recorded, not judged against the grid ratio.
- **Transparent summon-master treatment — pass.** RGBA data has zero-alpha corners; there is no display border, stand/base, or ground shadow. No face or eye is present, so the 45-degree face-plane check is not applicable.
- **Lifecycle — pass at this stage.** User visual approval is recorded in #141 comment 6312060335. This independent pass permits author-side WebP conversion and canonical saving at `assets/images/summons/S006-cloud.webp`; it does not claim converted-file alpha equivalence, final registry adoption, or runtime verification.

## Findings

No blocking, major, or minor discrepancy found for this exact raw image and the current stage-one contract. The full-canvas nonzero-alpha bounding rectangle is noted above because of extremely faint edge pixels; it does not visually clip the cloud and is not an automatic rejection under the applicable skill.
