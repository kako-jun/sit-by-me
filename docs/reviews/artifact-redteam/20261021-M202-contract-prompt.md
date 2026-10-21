# M202 prompt contract — 2026-10-21

- Target: M202 城の護衛敵: 白黒の怖い侍
- Stage: contract/prompt
- Status: independent prompt and raw-image review passed; adoption pending
- Grid class: `1x2` (`docs/monsters.md` §3-7)
- Candidate: `exec-5c2aa26a-fd04-40f6-b78e-846872f39b12.png` (1024×1536 RGBA)

## Canonical source rows

- `docs/monsters.md` M202: a scary samurai, an ordinary castle guardian, distinct from midboss M014.
- `docs/monsters.md` §3-7: `M202 | 1x2 | 白黒の怖い侍`.
- `docs/art-direction.md` enemy shelf: old black-and-white period-film image, dry grain, strong shadows.
- The project policy in `docs/assets-policy.md` requires photorealistic generated images for enemies and objects.

## Prompt

Create one isolated ordinary enemy battle sprite for M202, logical gridClass 1x2, on a portrait 1024×1536 px transparent canvas. It is a frightening samurai image as if emerging from an old black-and-white period-film frame: an empty kabuto helmet and torso armor shell, standing upright by itself, with no wearer, no flesh, no human body, no face, and no weapon. The visual should read immediately as a scary samurai through the helmet crest silhouette and layered armor plates, but use no real clan insignia, real historical person, recognizable film character, flag, or readable text. Strict monochrome black, white, and gray; strong dramatic shadows across the armor; dry visible film grain, slightly worn old-film texture. Camera at exactly 45 degrees from camera-front toward the object's right (+x), showing front and right-facing side planes. No eyes or gaze. Keep the entire armor shell inside the canvas with some margin. Isolated enemy cutout only: no floor, scenery, smoke, shadow plane, frame, or lettering. Photorealistic generated image, with readable detail at battle-sprite scale.

Tool setting: `transparent_background: true`.

## Independent review

- Prompt reviewer: `/root/enemy_input_audit` (2026-10-21), pass. An empty armor shell is source-faithful, avoids making a person into an enemy, and matches the period-film description. The reviewer confirmed the portrait canvas and `1x2` grid are compatible.
- Raw reviewer: `/root/m130_prompt_review` (2026-10-21), pass. The 1024×1536 RGBA has full alpha transparency; armor is fully framed. Helmet opening, chest front, and right shoulder planes show the required three-quarter front-right view. The image remains a candidate pending kako-jun's adoption decision.
