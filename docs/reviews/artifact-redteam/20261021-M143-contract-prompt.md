# M143 prompt contract — 2026-10-21

- Target: M143 割れた窓
- Stage: contract/prompt
- Status: independent prompt review passed; candidate generated and adopted by kako-jun on 2026-10-21
- Reference: `assets/images/enemies/M143.webp` (broken-window identity, old wooden frame, glass-shard direction only; do not copy side-on framing)
- Grid class: `1x2` (docs/monsters.md §3-7; stale dungeon-enemies row corrected to match)

## Prompt

Use case: photorealistic-natural. Asset type: isolated battle sprite for Sit by Me enemy M143. The following are verbatim canonical source rows for metadata only; do not render words or map/location elements:

`| M143 | 割れた窓 | 崩壊・落下 | サニーランド屋内（旧円形ホール配置は失効、詳細再配置TBD） | 未定 | 未定 | 未定 | 生成済み: assets/images/enemies/M143.webp（採用: kako-jun 2026-10-14。右へ破片が突き出す・透過） | #12 |`

`| M143 | 割れた窓（1x2） | A: 廃墟の屋内。割れたガラス・錆（MT 7.2、EA 1.3） | — | 雑魚 | 未定 | 絵あり | ○ | 未定 | 未定 |`

Create one isolated photorealistic battle sprite of a single broken window panel, using `assets/images/enemies/M143.webp` only to preserve its old wooden frame, fractured glass, and rightward shards. Replace the old side-on camera: orient the window plane at exactly 45° yaw from camera-front (0°) toward screen-right (+x), not edge-on at 90°; show both the glass plane and the frame's right edge thickness. Keep several sharp glass fragments projecting from the opening toward +x, fully inside the canvas. Show the complete window frame and all visible shard tips, with at least 32 px clearance from every edge. Logical occupancy `gridClass 1x2`; use a 1024×1536 portrait canvas. Genuine transparent background. No wall, room, ceiling, floor, rubble, person, blood, contact shadow, base, outline, text, logo, or extra object.

Tool setting: `transparent_background: true`.

## Independent prompt review

- Reviewer: `/root/enemy_input_audit` (independent; 2026-10-21)
- Verdict: `pass` for contract/prompt stage.
- Evidence: canonical M143 and dungeon rows both declare `1x2`; the portrait pixel canvas is specified separately. The reference supports the wooden frame, fractured glass, and right-projecting shards; the dungeon row supports rust. The 45° plane yaw is an explicit orientation for this inanimate window, and the prompt excludes scene context and extra objects.
