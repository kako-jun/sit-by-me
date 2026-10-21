# M142 prompt contract — 2026-10-21

- Target: M142 落ちてきそうなシャンデリア
- Stage: contract/prompt
- Status: pass for prompt stage; generation eligible
- Independent review: pass, `/root/enemy_input_audit`, 2026-10-21; source details, grid, angle, complete-chain framing and exclusions verified
- Reference: `assets/images/enemies/M142.webp` (chandelier identity/material only; do not copy old crop or side-on view)
- Grid class: `1x2` (docs/monsters.md §3-7; stale dungeon-enemies row corrected to match)

## Prompt

Use case: photorealistic-natural. Asset type: isolated battle sprite for Sit by Me enemy M142. The following are verbatim canonical source rows for metadata only; do not render words or location/environment elements:

`| M142 | 落ちてきそうなシャンデリア | 崩壊・落下 | サニーランド屋内（旧円形ホール配置は失効、詳細再配置TBD） | 未定 | 未定 | 未定 | 生成済み: assets/images/enemies/M142.webp（採用: kako-jun 2026-10-14。右寄り斜め・透過・鎖は上端で切断） | #12 |`

`| M142 | 落ちてきそうなシャンデリア（1x2） | A: 入口・宿泊棟など屋内へ再配分TBD（旧円形ホール配置は失効）。G に近い（落下の恐怖。環境敵とは記録されていない） | — | 雑魚 | 未定 | 絵あり | ○（固定） | 高額ゴールド（案） | 未定 |`

Create one isolated photorealistic battle sprite of one ornate hanging chandelier, using `assets/images/enemies/M142.webp` only to preserve its tiered metal arms, candle-shaped bulbs, hanging crystal drops, and central hub. Replace the old crop and near-side profile: show the central hub's front face and right rim in a 45° view from camera-front (0°) toward screen-right (+x). Include the full central hub, all arms and drops, and the complete hanging chain above it; nothing may touch or cross the canvas edge. Center the complete object, with at least 32 px between every visible pixel and each edge. Logical occupancy `gridClass 1x2`; use a 1024×1536 portrait canvas. Genuine transparent background. No room, ceiling, hook, floor, ground/contact shadow, base, outline, text, logo, or extra object.

Tool setting: `transparent_background: true`.
