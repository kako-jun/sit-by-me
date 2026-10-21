# M208 prompt contract — 2026-10-21

- Target: M208 城の雑魚: 怨霊
- Stage: contract/prompt
- Status: independent prompt and raw-image reviews passed; adoption pending
- Grid class: `2x2` (`docs/monsters.md` §3-7)
- Candidate: `exec-1be1da1e-7c85-4520-b091-6b537ecb656f.png` (1254×1254 RGBA)

## Canonical source rows

- `docs/monsters.md` M208: vengeful spirit, ordinary castle-only enemy (#140).
- `docs/monsters.md` §3-7: `M208 | 2x2 | 周囲へ広がる怨霊`.
- `docs/dungeon-enemies.md` #140 identifies the three new castle enemies as Japanese-style castle enemies.
- `docs/art-direction.md` §94: humans are not enemies.
- `docs/assets-policy.md`: photorealistic enemy/object art as an isolated transparent cutout.

## Prompt

Create one isolated ordinary RPG battle enemy M208 “vengeful spirit”, logical gridClass 2x2, on a transparent square 1254×1254 px canvas. Depict a broad, spreading photorealistic supernatural smoke phenomenon, clearly nonhuman and without anatomy: a dense dark translucent vapor mass with torn blank pale paper-like strips caught along its edges and one empty dark aperture in the center. The aperture is only a hollow gap, not a face or mask. No head, torso, limbs, eyes, human figure, body, clothing, actual mask, religious or funerary symbol, recognizable culture, text, frame, or real object. The form should read as a frightening ghostly presence through its unnatural widening smoke silhouette and empty center. Keep it self-contained as one enemy, with no floor, scenery, external cast/contact shadow, or extra props. Entire silhouette fully inside canvas with visible transparent margin. Transparent isolated cutout; photorealistic generated-object style. As this is a headless radial smoke phenomenon, orientation and gaze are not applicable.

Tool setting: `transparent_background: true`.

## Independent reviews

- Prompt reviewer: `/root/enemy_input_audit` (2026-10-21), pass. A broad translucent smoke phenomenon fits the ghost enemy and 2x2; blank strips and a hollow gap remain non-anatomical; no forced face or orientation is needed.
- Raw reviewer: `/root/m130_prompt_review` (2026-10-21), pass. The 1254×1254 RGBA image has alpha transparency and a complete frame; it reads as one spreading nonhuman smoke mass with pale wisps, without a distinct head, face, or person.
