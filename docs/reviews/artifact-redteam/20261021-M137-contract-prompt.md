# M137 prompt contract — 2026-10-21

- Target: M137 有刺鉄線
- Stage: contract/prompt
- Status: pass for prompt stage; generation eligible
- Independent review: pass, `/root/enemy_input_audit`, 2026-10-21; source rows, coil/strand identity, angle, 2x1 grid and exclusions verified
- Reference: `assets/images/enemies/M137.webp` (barbed-wire identity and coil/strand direction only; do not copy its side-on composition)
- Grid class: `2x1` (docs/monsters.md §3-7)

## Prompt

Use case: photorealistic-natural. Asset type: isolated battle sprite for Sit by Me enemy M137. The following are verbatim canonical source rows for metadata only; do not render words or map/location elements:

`| M137 | 有刺鉄線 | 毒と尖り（尖ったもの） | 海外 荒れ地A・B（一任による決定 2026-10-15、docs/dungeon-enemies.md が正本） | 未定 | 未定 | 未定 | 生成済み: assets/images/enemies/M137.webp（採否待ち。右へ線が伸びる・透過） | #12 |`

`| M137 | 有刺鉄線（2x1） | A: 荒れ地 A・B の立入禁止の境界（EA 1.7 の案。記録に固有の理由は無い） | — | 雑魚 | 未定 | 絵あり（採否待ち） | △ | 未定 | 不可（海外は一方通行。MT 3.9） |`

Create one isolated photorealistic battle sprite of barbed wire, using `assets/images/enemies/M137.webp` only to preserve the identity of sharp barbs on rusted twisted wire. Show a loosely wound coil at image-left with one strand extending toward screen-right (+x), matching the existing rightward line while replacing the side-on view. Set the visible face of the coil at exactly 45° yaw from camera-front (0°) toward screen-right (+x), not edge-on at 90°; show both the coil opening/inner loops and the wire's side thickness. Keep all wire, barbs and coil fully inside the canvas with at least 32 px clearance from every edge. Logical occupancy `gridClass 2x1`; use a 1536×1024 landscape canvas. Genuine transparent background. No wood post, fence, scenery, ground/contact shadow, base, outline, text, logo, people, or extra objects.

Tool setting: `transparent_background: true`.
