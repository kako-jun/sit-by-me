# M149 prompt contract — 2026-10-21

- Target: M149 石油ストーブ
- Stage: contract/prompt
- Status: independent prompt review passed; generation eligible
- Reference: `assets/images/enemies/M149.webp` (old oil heater form, burner grille, body, tank, and carrying handle; do not copy the right-facing side view or external fire-like glow)
- Grid class: `1x1` (`docs/monsters.md` §3-7 and `docs/dungeon-enemies.md`)

## Prompt

Use case: photorealistic-natural. Asset type: isolated battle sprite for Sit by Me enemy M149. These are verbatim canonical source rows for metadata only; do not render words or location elements:

`| M149 | 石油ストーブ | 火事の原因（火） | 寺町 sento（銭湯。中3の火事に向けて慣れさせる）（kako-jun 承認 2026-10-15、docs/enemy-allocation.md §1.1） | 火 | 未定 | 未定 | 生成済み: assets/images/enemies/M149.webp（採否待ち。右向き・透過・火災は描かない） | 同上 |`

`| M149 | 石油ストーブ（1x1） | A: sento＝暖房の火。B: 中3の火事に向けて慣れさせる（EA 1.1、L 3-3）。属性=火 | — （火） | 雑魚 | 未定 | 絵あり | ◎ | 未定 | 可（拠点。再訪できる。MT 7.2） |`

Create one isolated photorealistic battle sprite of a single old oil heater, using the supplied M149 image only to preserve the heater identity, burner grille, cylindrical body, fuel tank, and carrying handle. Replace the right-facing side view: orient the heater's front burner at exactly 45° yaw from camera-front (0°) toward screen-right (+x), showing the burner grille face and the right side of the body and tank; do not show an edge-on 90° profile. A subdued amber heating-element glow may appear behind the protective grille, but show no flame outside the heater, fire, smoke, or burning room. Logical occupancy `gridClass 1x1`; use a 1024×1024 square canvas. Keep the entire heater and handle inside the canvas with at least 32 px clear margin from all edges. Genuine transparent background. No room, wall, fuel can, person, floor, contact shadow, base, outline, text, logo, or extra object.

Tool setting: `transparent_background: true`.

## Independent prompt review

- Reviewer: `/root/enemy_input_audit` (independent; 2026-10-21)
- Verdict: `pass` for contract/prompt stage.
- Evidence: both canonical rows declare `1x1`; the reference supports the heater body, grille, tank, and handle. The 45° burner-front direction toward +x asks for the grille face and housing depth. The optional internal amber element glow is distinct from flame; fire, smoke, and room fire remain forbidden.
