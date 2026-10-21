# M204 prompt contract — 2026-10-21

- Target: M204 城の護衛敵: 外国での戦争
- Stage: contract/prompt
- Status: original prompt review passed; edited candidate passed raw-image review
- Grid class: `2x1` (`docs/monsters.md` §3-7)
- Final candidate: `exec-fcfa091c-e53d-4f26-a068-787303bbf1e6.png` (1774×887 RGBA)
- Superseded first candidate: `exec-58589e26-24a3-4f75-8007-aed60e33fbb8.png` (background vignette and near-frontal angle failed raw review)

## Canonical source rows

- `docs/monsters.md` M204: foreign wars represented as a distant news screen, smoke, and alarms.
- `docs/dungeon-enemies.md` M204: ordinary castle-only guardian; do not make a country, military, citizen, or real weapon into an enemy.
- `docs/monsters.md` §3-7: 2x1 horizontal screen composition.
- `docs/assets-policy.md`: enemy/object sprites are photorealistic isolated transparent cutouts.

## Prompt

Create one isolated ordinary RPG battle sprite for M204 “foreign wars as distant news”, logical gridClass 2x1 on a transparent 1536×1024 landscape canvas. Photorealistic generated-object style. Depict one threatening horizontal old broadcast monitor fused into rolling dark smoke and a few generic alarm lights, as a single enemy. The monitor screen shows only blurred abstract smoke and indistinct generic ruined shapes with anonymous signal bands. Use an aged monochrome black-and-white broadcast look. Convey distant war through news, smoke, and alarms only. Do not depict any country, flag, map, military, soldier, citizen, person, uniform, real weapon, identifiable building, actual conflict, readable text, logo, or insignia. Camera exactly 45 degrees from camera-front toward +x, screen front and right side visible. Complete silhouette fully in frame with margin. No floor, battlefield, scenery, contact/cast shadow, frame around canvas, or extra props. Transparent cutout, photorealistic enemy image, strong readable silhouette.

Tool setting: `transparent_background: true`.

## Independent prompt review

- Reviewer: `/root/enemy_input_audit` (2026-10-21)
- Verdict: `pass`.
- The concept follows the distant news/smoke/alarm motif and excludes real actors and identifiable conflict. Reviewer requested aged monochrome broadcast styling and a clearly generic skyline; both are included.

## Edit prompt

Edit this M204 enemy sprite to meet its transparent cutout and viewing angle. Preserve the same anonymous old black-and-white news monitor, generic blurred distant smoke/ruin shapes, rolling smoke mass, and generic red alarm lights. Remove the entire dark vignette/background so the exterior is genuinely transparent; keep smoke only where it forms the enemy's compact silhouette and leave clear transparent margin around every edge. Rotate the monitor so it is unmistakably viewed exactly 45 degrees from camera-front toward +x, with the screen front and its right side casing clearly visible. Keep the news image abstract and anonymous, with no country, flag, map, soldier, citizen, person, uniform, real weapon, readable text, or identifiable building. Keep 2x1 landscape framing, complete uncut silhouette, photorealistic generated-object style. No background, floor, external cast/contact shadow, scene, border, or text. Preserve only the isolated enemy on transparency.

Tool setting: `transparent_background: true`; referenced first candidate above.

Edit prompt result: pass. Raw-image reviewer confirmed an RGBA cutout with transparent corners and a clear front/right monitor view. The first image was rejected for a nontransparent vignette and an insufficiently clear oblique view.
