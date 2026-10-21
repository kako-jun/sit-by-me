# M145 prompt contract — 2026-10-21

- Target: M145 割れた酒瓶（割れたビール瓶）
- Stage: contract/prompt
- Status: independent prompt review passed; generation eligible
- Reference: `assets/images/enemies/M145.webp` (brown beer-bottle identity, horizontal placement, broken mouth; do not copy its exact side-on framing)
- Grid class: `2x1` (`docs/monsters.md` §3-7 and `docs/dungeon-enemies.md`)

## Prompt

Use case: photorealistic-natural. Asset type: isolated battle sprite for Sit by Me enemy M145. These are verbatim canonical source rows for metadata only; do not render words, labels, or location elements:

`| M145 | 割れた酒瓶（割れたビール瓶） | 崩壊・落下 | 寺町 sento（銭湯）（kako-jun 承認 2026-10-15、docs/enemy-allocation.md §1.1） | 未定 | 未定 | 未定 | 生成済み: assets/images/enemies/M145.webp（口が割れた茶色いビール瓶・右向き・透過。2026-10-14生成、同日 kako-jun が採用） | #12 |`

`| M145 | 割れた酒瓶（2x1） | A: sento（L 3-3 固定）。F: 2x1 | — | 雑魚 | 未定 | 絵あり | ◎ | 未定 | 可（拠点。再訪できる。MT 7.2） |`

Create one isolated photorealistic battle sprite of a single brown amber beer bottle lying horizontally, with the bottle body complete and its neck broken into a jagged opening at the screen-right (+x) end. Use the supplied M145 image only to preserve bottle identity, brown glass, horizontal placement, and broken mouth; replace its side-on camera. Turn the bottle's long axis exactly 45° from camera-front (0°) toward screen-right (+x), so its broken mouth points diagonally right and toward the camera; show the oval opening and both the front glass surface and rightward depth of the neck, never a 90° flat profile. Keep the full bottle and every jagged edge inside the canvas with at least 32 px clear margin from each edge. Logical occupancy `gridClass 2x1`; use a 1536×1024 landscape canvas. Genuine transparent background. No label, text, logo, hand, person, extra shards, floor, room, contact shadow, base, outline, or other object.

Tool setting: `transparent_background: true`.

## Independent prompt review

- Reviewer: `/root/enemy_input_audit` (independent; 2026-10-21)
- Verdict: `pass` for contract/prompt stage.
- Evidence: canonical monster and encounter rows both declare `2x1`; `1536×1024` is the separate canvas size. The reference supports the brown amber bottle, horizontal position, and broken mouth at +x. The prompt's 45° bottle axis, visible opening and neck depth are concrete physical orientation instructions. Unresolved mechanics-only TBDs do not affect this image.
