# M134 prompt contract — 2026-10-21

- Target: M134 釘
- Stage: contract/prompt
- Status: pass for prompt stage; generation eligible
- Independent review: pass, `/root/enemy_input_audit`, 2026-10-21; source rows, 1x1 grid, angle and exclusions verified
- Reference: `assets/images/enemies/M134.webp` (legacy identity/material reference only; do not copy its flat side view)
- Grid class: `1x1` (docs/monsters.md §3-7, M130–M135 group)

## Prompt

Use case: photorealistic-natural. Asset type: isolated battle sprite for Sit by Me enemy M134. The following are verbatim canonical source rows for metadata only; do not render words or map/location elements:

`| M134 | 釘 | 毒と尖り（尖ったもの） | 能登 NTB-02 上り坂（被災後）（一任による決定 2026-10-15、docs/dungeon-enemies.md が正本） | 未定 | 未定 | 未定 | assets/images/enemies/M134.webp（透過・長辺640。採用: kako-jun 2026-10-14） | #12 |`

`| M134 | 釘（1x1） | A: NTB-02 上り坂の被災後（EA 1.5） | — | 雑魚 | 未定 | 絵あり | △ | 未定 | 可（青年編の始まりのレベル上げの場。MT 7.2） |`

Create one isolated photorealistic battle sprite of a single old iron nail, using `assets/images/enemies/M134.webp` only to preserve the identity of a long iron nail with a broad flat head, pointed tip, and worn brown rust texture. Replace the side-on camera angle: the nail head's broad circular face plane is at 45° yaw from camera-front (0°) toward screen-right (+x), with both its front face and right edge visible. The shaft extends from image-left toward image-right (+x), so the nail head is at image-left and pointed tip at image-right; show the shaft's side surface. Keep the whole nail visible and centered, with its head and tip at least 32 px inside the canvas. Logical occupancy `gridClass 1x1`; use a square 1024×1024 canvas. Genuine transparent background. No person, hand, board, wall, road, rubble, blood, ground/contact shadow, base, outline, text, logo, or extra object.

Tool setting: `transparent_background: true`.
