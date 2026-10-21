# M205 prompt contract — 2026-10-21

- Target: M205 城の護衛敵: 核兵器
- Stage: contract/prompt and raw image
- Status: source concept and final raw image passed; adoption pending
- Grid class: `2x2` (`docs/monsters.md` §3-7)
- Final candidate: `exec-9003a49c-9deb-4cbc-bd37-c8fb826f7dee.png` (1254×1254 RGBA)
- Superseded first image: `exec-aaf25573-f09d-4e9b-aabd-f6e1e868ae58.png` (flame/explosion appearance and clipped edges)

## Canonical source rows

- `docs/monsters.md` M205: white flash, alarm, pressure, and shadow. It is an ordinary castle-only guardian.
- `docs/monsters.md` §3-7: `M205 | 2x2 | 白い閃光・警報・圧力・影の複合体`.
- `docs/art-direction.md` §25: no country, military, citizen, or real weapon as an enemy.
- `docs/assets-policy.md`: photorealistic generated enemy art as an isolated transparent cutout.

## Initial prompt

Create one isolated ordinary RPG enemy battle sprite for M205, logical gridClass 2x2 on a square 1254×1254 px transparent canvas. This is the fear of nuclear weapons represented only by abstract effects: a compact overexposed white core behind a distorted translucent pressure-wave membrane, several generic alarm lamps, and a hard-edged dark shadow form contained within the sprite silhouette. Do not make an external cast or contact shadow. Photorealistic generated-object style; represent the membrane and alarm lamps as tangible but impossible studio-prop forms. Absolutely no bomb, missile, warhead, mushroom cloud, radiation symbol, country, military, civilian, human figure, building, landscape, writing, flag, or logo. The white flash, alarms, pressure and internal shadow are the entire concept. Camera azimuth exactly 45 degrees from camera-front toward +x, showing front and right planes of the membrane and alarm units; no head, torso, or gaze because this is an abstract phenomenon. Full 2x2 silhouette inside frame with generous margin; no floor, scenery, external shadows, border, or extra props. Transparent isolated cutout, clear readable fantasy RPG enemy, photorealistic materials.

Tool setting: `transparent_background: true`.

## Edit prompt

Edit this M205 battle sprite to match the abstract source motif and fix its crop. Preserve a square 2x2 enemy silhouette with generic alarm lamps and a distorted pressure-wave membrane, but scale the full composition uniformly to about 78% and center it with clear transparent margin on all four sides. Replace the orange flame/fireball/explosion appearance with a pure, overexposed white flash core and a cool pale translucent pressure wave; no fire, flames, explosion cloud, mushroom shape, or blast debris. Keep only a hard-edged dark shadow form contained inside the sprite silhouette. No people or person-shaped forms, no bomb, missile, weapon, country, military, civilian, buildings, landscape, radiation symbol, text, or flag. Photorealistic generated-object style, transparent isolated cutout, no floor, scenery, external shadow, frame, or extra objects.

Tool setting: `transparent_background: true`; referenced first image above.

## Independent review

- Prompt concept reviewer: `/root/enemy_input_audit` (2026-10-21), pass. The source motifs and exclusions were confirmed; reviewer noted that the edit request's “about 78%” and “clear margin” were imprecise and recommended an exact scale and pixel margin. The generated edit visibly provides margin; measured final alpha bounds are documented in the raw-image review. This wording issue is recorded and the prompt will use numeric bounds for subsequent edits.
- First raw reviewer: `/root/m130_prompt_review` (2026-10-21), blocker. Initial image read as an orange explosion and was clipped.
- Final raw reviewer: `/root/m130_prompt_review` (2026-10-21), pass. The 1254×1254 RGBA has an alpha bbox of 1059×1040 at +98,+113 (about 8% margin). White flash, alarms, pressure shell, and abstract shadows read clearly; no person, weapon, or literal fiery explosion is apparent.
