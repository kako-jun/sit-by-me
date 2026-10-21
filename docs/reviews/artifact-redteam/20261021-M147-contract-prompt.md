# M147 prompt contract — 2026-10-21

- Target: M147 扇風機・換気扇の羽根
- Stage: contract/prompt
- Status: independent prompt review passed; generation eligible
- Reference: `assets/images/enemies/M147.webp` (aged metal fan head, circular guard, three blades, central hub, and support details; replace the old right-facing side presentation)
- Grid class: `1x1` (`docs/monsters.md` §3-7 and `docs/dungeon-enemies.md`)

## Prompt

Use case: photorealistic-natural. Asset type: isolated battle sprite for Sit by Me enemy M147. These are verbatim canonical source rows for metadata only; do not render words or map elements:

`| M147 | 扇風機・換気扇の羽根 | 回転する刃（風） | 寺町 sento（銭湯）（一任による決定 2026-10-15、docs/dungeon-enemies.md が正本） | 風 | 未定 | 未定 | 生成済み: assets/images/enemies/M147.webp（採否待ち。右向き・透過） | 同上 |`

`| M147 | 扇風機・換気扇の羽根（1x1） | A: sento＝銭湯の換気（EA 1.1）。C 準ずる: 風の元（属性=風。LS 67 の最早＝幼稚園前半） | — （風） | 雑魚 | 未定 | 絵あり | ◎ | 未定 | 可（拠点。再訪できる。MT 7.2） |`

Create one isolated photorealistic battle sprite of an aged metal fan head: one circular wire guard, a central hub, and exactly three blades, using the supplied M147 image only for this fan identity and visible parts. Replace the old right-facing side view. Orient the circular fan plane exactly 45° from camera-front (0°) toward screen-right (+x), not edge-on at 90°; show the blades' front surfaces, the hub face, and the right-side depth of the guard and housing. Make the rotating blades distinct from the guard wires. The fan is an inanimate object with no head, torso, or eyes. Logical occupancy `gridClass 1x1`; use a 1024×1024 square canvas. Keep the full guard, housing, and all visible fan parts inside the canvas with at least 32 px clear margin from every edge. Genuine transparent background. No room, wall, bathroom fixtures, person, blood, airflow lines, floor, contact shadow, display base, outline, text, logo, or extra object.

Tool setting: `transparent_background: true`.

## Independent prompt review

- Reviewer: `/root/enemy_input_audit` (independent; 2026-10-21)
- Verdict: `pass` for contract/prompt stage.
- Evidence: both canonical rows declare `1x1`; the reference supports an aged metal fan head, wire guard, three blades, hub, and housing. The 45° disk/hub-axis direction is a concrete physical camera view. Sento ventilation is placement context and is excluded from the isolated sprite. No unresolved visual TBD blocks generation.
