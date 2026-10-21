# M144 prompt contract — 2026-10-21

- Target: M144 破れた障子
- Stage: contract/prompt
- Status: independent prompt review passed; candidate adopted by kako-jun on 2026-10-21
- Reference: `assets/images/enemies/M144.webp` (shoji frame, lattice, torn paper, and rightward paper strips; do not copy the old side-on view)
- Grid class: `1x2` (`docs/monsters.md` §3-7; `docs/dungeon-enemies.md` size corrected to match)

## Prompt

Use case: photorealistic-natural. Asset type: isolated battle sprite for Sit by Me enemy M144. The following are verbatim canonical source rows for metadata only; do not render words or location elements:

`| M144 | 破れた障子 | 崩壊・落下 | 香林坊 chaya-lane（茶屋街）（kako-jun 承認 2026-10-15、docs/enemy-allocation.md §1.2） | 未定 | 未定 | 未定 | 生成済み: assets/images/enemies/M144.webp（採否待ち。右へ紙片がなびく・透過） | #12、#14 |`

`| M144 | 破れた障子（1x2） | A: chaya-lane＝暗い木の格子・提灯（L 固定、MT 7.3）。H: **救済＝無属性ダメージ魔法のラーニング元（案）。序盤の最弱クラスの敵。kako-jun 2026-10-15。learning-schedule.md §1b** | **（案）無属性ダメージ魔法「おにぱんち」**（採用方向） | 雑魚 | 未定 | 絵あり（採否待ち） | ○（固定） | 未定 | 未定（ワープ先は香林坊のレストラン。DC 60 行。到達は可） |`

Create one isolated photorealistic battle sprite of one complete torn shoji panel. Use the supplied M144 image only to preserve the dark wooden lattice frame, translucent paper, tears, and strips trailing toward screen-right; do not copy its side-on camera. Orient the shoji plane exactly 45° yaw from camera-front (0°) toward screen-right (+x), not edge-on at 90°; show both the paper plane and the frame's right edge thickness. Torn paper strips stream from openings toward +x, with every tip visible inside the canvas and at least 32 px clearance from all canvas edges. Logical occupancy `gridClass 1x2`; use a 1024×1536 portrait canvas. Genuine transparent background. No room, wall, lantern, ceiling, floor, rubble, person, contact shadow, base, outline, text, logo, or extra object. The “暗い木の格子・提灯” field description is location context; do not add a lantern to the enemy sprite.

Tool setting: `transparent_background: true`.

## Independent prompt review

- Reviewer: `/root/enemy_input_audit` (independent; 2026-10-21)
- Verdict: `pass` for contract/prompt stage.
- Evidence: canonical monster and encounter rows both declare `1x2`; the prompt retains the row text verbatim. Reference and encounter context support the dark lattice, torn shoji paper, and strips trailing right. The lantern is location context and is explicitly excluded as a separate sprite object. The 45° plane angle, front plane/right edge, canvas pixels, transparency, margins, and exclusions are concrete.
