# M135 prompt contract — 2026-10-21

- Target: M135 割れたガラス
- Stage: contract/prompt
- Status: pass for prompt stage; generation eligible
- Independent review: pass, `/root/m130_prompt_review`, 2026-10-21; source rows, cluster identity, direction, 1x1 grid and constraints verified
- Reference: `assets/images/enemies/M135.webp` (legacy broken-glass identity/material reference only)
- Grid class: `1x1` (docs/monsters.md §3-7, M130–M135 group)

## Prompt

Use case: photorealistic-natural. Asset type: isolated battle sprite for Sit by Me enemy M135. The following are verbatim canonical source rows for metadata only; do not render words or map/location elements:

`| M135 | 割れたガラス | 毒と尖り（尖ったもの） | 能登 NTB-04 下り坂（被災後）（一任による決定 2026-10-15、docs/dungeon-enemies.md が正本） | 未定 | 未定 | 未定 | assets/images/enemies/M135.webp（採用: kako-jun 2026-10-14） | #12 |`

`| M135 | 割れたガラス（1x1） | A: NTB-04 下り坂の被災した町（EA 1.5） | — | 雑魚 | 未定 | 絵あり | ○ | 未定 | 可（青年編の始まりのレベル上げの場。MT 7.2） |`

Create one isolated photorealistic battle sprite depicting broken glass only, using `assets/images/enemies/M135.webp` as an identity reference for the interlocked mass of sharp translucent shards with reflective facets. Preserve the cluster identity without imposing a shard count. Point the longest shard toward screen-right (+x) and show visible front and right facet planes; do not show the cluster edge-on. Keep the full cluster centered, with every tip at least 32 px inside the canvas. Logical occupancy `gridClass 1x1`; use a square 1024×1024 canvas. Genuine transparent background. No bottle, window frame, floor, rubble, blood, person, hand, ground/contact shadow, base, outline, text, logo, or extra object.

Tool setting: `transparent_background: true`.
