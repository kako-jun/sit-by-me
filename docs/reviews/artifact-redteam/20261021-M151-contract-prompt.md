# M151 prompt contract — 2026-10-21

- Target: M151 古いたこ足配線
- Stage: contract/prompt
- Status: independent prompt review passed; generation eligible
- Reference: `assets/images/enemies/M151.webp` (aged ivory power strip, charred sockets, frayed cords and plugs; preserve identity, replace the old side-on view)
- Grid class: `2x1` (`docs/monsters.md` §3-7 and `docs/dungeon-enemies.md`)

## Prompt

Use case: photorealistic-natural. Asset type: isolated battle sprite for Sit by Me enemy M151.

Isolated photorealistic battle sprite for enemy M151: one old, yellowed-ivory power strip with visibly charred socket openings and several aged, frayed cords extending horizontally to screen-right, each ending in a worn plug, matching the supplied reference. Keep the complete strip-and-cord assembly recognizable and intact. Logical occupancy: gridClass 2x1. Show it in a horizontal, ground-resting pose, with the socket-face plane turned exactly 45° from camera-front toward screen-right (+x), so the socket face and right-side body thickness are both visible. Transparent background; landscape 1536×1024. No visible floor, room, wall, wall outlet, person, clothing, extra object, text, logo, sparks, lightning bolts, or flames. M151's enemy attribute is fire; lightning is only its learned かんでん ability, so show no lightning effects.

Tool setting: `transparent_background: true`.

## Independent prompt review

- Reviewer: `/root/enemy_input_audit` (independent; 2026-10-21)
- Verdict: `pass` after clarifying which plane faces the camera.
- Evidence: prompt matches the canonical `2x1`, old power-strip identity, charred sockets, and rightward cords. The dungeon record confirms fire is the enemy attribute and lightning is only its learned ability. It excludes visible fire, sparks, and lightning effects; no room or floor is added.
