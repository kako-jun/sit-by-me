# M136 prompt contract — 2026-10-21

- Target: M136 金網
- Stage: contract/prompt
- Status: pass for prompt stage; generation eligible
- Independent review: pass, `/root/m130_prompt_review`, 2026-10-21; source rows, panel angle, 2x1 grid and exclusions verified
- Reference: `assets/images/enemies/M136.webp` (identity, mesh material, and post reference only; do not copy edge-cropped wire shape)
- Grid class: `2x1` (docs/monsters.md §3-7)

## Prompt

Use case: photorealistic-natural. Asset type: isolated battle sprite for Sit by Me enemy M136. The following are verbatim canonical source rows for metadata only; do not render words or map/location elements:

`| M136 | 金網 | 毒と尖り（尖ったもの） | 卯辰山 utatsuyama-sunnyland（一任による決定 2026-10-15、docs/dungeon-enemies.md が正本） | 未定 | 未定 | 未定 | 生成済み: assets/images/enemies/M136.webp（採否待ち。右へ切れた針金が伸びる・透過） | #12 |`

`| M136 | 金網（2x1） | A: utatsuyama-sunnyland＝廃遊園地の跡の柵（EA 1.3） | — | 雑魚 | 未定 | 絵あり | ○ | 未定 | 未定 |`

Create one isolated photorealistic battle sprite of a weathered chain-link fence section based on `assets/images/enemies/M136.webp`, preserving the recognizable diamond mesh and rusted metal wire while replacing its flat side view. The fence panel's face is yawed exactly 45° from camera-front (0°) toward screen-right (+x), not edge-on at 90°; show the mesh face and the panel's right edge thickness. Include one upright support post at the image-left end. Several broken wire ends extend toward +x from the image-right edge, but remain fully inside the canvas. Center the complete fence fragment with at least 32 px between every visible wire/post pixel and each canvas edge. Logical occupancy `gridClass 2x1`; use a 1536×1024 landscape canvas. Genuine transparent background. No ground, amusement-park scenery, people, sign, shadow, base, outline, text, logo, or extra object.

Tool setting: `transparent_background: true`.
