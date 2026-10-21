# M146 prompt contract — 2026-10-21

- Target: M146 プロペラ
- Stage: contract/prompt
- Status: independent prompt review passed; generation eligible
- Reference: `assets/images/enemies/M146.webp` (three-blade propeller and central hub only; do not copy its near-profile hub presentation)
- Grid class: `1x1` (`docs/monsters.md` §3-7 and `docs/dungeon-enemies.md`)

## Prompt

Use case: photorealistic-natural. Asset type: isolated battle sprite for Sit by Me enemy M146. These are verbatim canonical source rows for metadata only; do not render words or map elements:

`| M146 | プロペラ | 回転する刃（風） | 内灘 uchinada-station・UCH-03 松林道（kako-jun 承認 2026-10-15、docs/enemy-allocation.md §1.4） | 風 | 未定 | 未定 | 生成済み: assets/images/enemies/M146.webp（採否待ち。三枚羽根・透過） | art-direction.md、#26 |`

`| M146 | プロペラ（1x1） | A: 電車基地・松林道、体が切断されそうな恐怖（AD 85 行）。属性=風（記録あり） | — （風） | 雑魚 | 未定 | 絵あり（採否待ち） | ○ | 未定 | 未定 |`

Create one isolated photorealistic battle sprite of one complete three-blade metal propeller with a central cylindrical hub. Use the supplied M146 image only to preserve the three-blade propeller identity and hub; replace its near-profile presentation. Turn the propeller disk exactly 45° from camera-front (0°) toward screen-right (+x), with the hub axis pointing diagonally right and toward the camera; show the front face of the hub and its right-side depth. Show exactly three distinct blades, all fully visible, with no blade overlapping the hub in a way that hides its attachment. The propeller is a mechanical object and has no head, torso, or eyes. Logical occupancy `gridClass 1x1`; use a 1024×1024 square canvas. Keep the full hub and blade tips within the canvas with at least 32 px clear margin from all edges. Genuine transparent background. No airplane, vehicle, person, blood, airflow streaks, floor, room, contact shadow, base, outline, text, logo, or extra object.

Tool setting: `transparent_background: true`.

## Independent prompt review

- Reviewer: `/root/enemy_input_audit` (independent; 2026-10-21)
- Verdict: `pass` for contract/prompt stage.
- Evidence: canonical rows and reference support `1x1`, the exact three-blade count, and central hub. The 45° orientation is defined by rotating the propeller disk normal/hub axis toward +x, with both hub face and depth visible. Material and mechanical identity come from the reference; no plane, vehicle, location scenery, or unresolved appearance detail is introduced.
