# M150 prompt contract — 2026-10-21

- Target: M150 ライター
- Stage: contract/prompt
- Status: independent prompt review passed; generation eligible
- Reference: `assets/images/enemies/M150.webp` (upright red lighter body, metal top and ignition parts, flame at upper-right; replace the right-facing profile)
- Grid class: `1x2` (`docs/monsters.md` §3-7; stale `docs/dungeon-enemies.md` size reconciled to match)

## Prompt

Use case: photorealistic-natural. Asset type: isolated battle sprite for Sit by Me enemy M150. These are verbatim canonical source rows for metadata only; do not render words or location elements:

`| M150 | ライター | 火事の原因（火） | 寺町 sento（銭湯。中3の火事に向けて慣れさせる）（kako-jun 承認 2026-10-15、docs/enemy-allocation.md §1.1） | 火 | 未定 | 未定 | 生成済み: assets/images/enemies/M150.webp（採否待ち。炎が右上へ・透過・無人・ロゴなし） | 同上 |`

`| M150 | ライター（1x2） | 同上（A・B。属性=火） | — （火） | 雑魚 | 未定 | 絵あり | ◎ | 未定 | 可（拠点。再訪できる。MT 7.2） |`

Create one isolated photorealistic battle sprite of one upright red metal lighter with a silver ignition top, using the supplied M150 image only to preserve the red casing, ignition parts, and flame identity; replace its right-facing side profile. Orient the broad casing face exactly 45° yaw from camera-front (0°) toward screen-right (+x), showing both that front plane and the casing's right-side thickness. Keep the top button and ignition wheel visible. A single active orange-yellow flame emerges from the nozzle and points diagonally to the upper-right; keep the whole flame tip inside the canvas. Logical occupancy `gridClass 1x2`; use a 1024×1536 portrait canvas. Keep the complete lighter and flame at least 32 px inside every canvas edge. Genuine transparent background. No hand, person, room, fire scene, smoke, fuel can, contact shadow, base, outline, text, logo, or extra object.

Tool setting: `transparent_background: true`.

## Independent prompt review

- Reviewer: `/root/enemy_input_audit` (independent; 2026-10-21)
- Verdict: `pass` for contract/prompt stage.
- Evidence: canonical `1x2` class and right-up lighter flame match the source rows and existing image. The 45° broad-face yaw toward +x shows the casing front and right thickness. Fire-scene prohibition does not forbid the lighter's own flame; room fire and smoke remain excluded.
