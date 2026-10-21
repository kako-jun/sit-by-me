# M128 prompt contract — 2026-10-21

- Target: M128 タコ
- Stage: contract/prompt
- Status: pass for prompt stage; generation eligible
- Canonical reference: `assets/images/enemies/M128.webp` if present; otherwise use records only
- Grid class: `2x2` (docs/monsters.md §3-7: giant squid and octopus grouping)
- Independent review: pass, `/root/m130_prompt_review`, 2026-10-21; verbatim source rows, grid agreement and complete constraints verified

## Prompt

Use case: photorealistic-natural. Asset type: isolated battle sprite for Sit by Me enemy M128. The following are verbatim canonical source rows for metadata only; do not render words or map/location elements:

`| M128 | タコ | 水辺の生物 | 水辺（章は未定）。能登 実家 v2（被災前。水のラーニング元なので被災後の能登の海辺でも出て再戦できる）（一任による決定 2026-10-15、docs/dungeon-enemies.md が正本） | 水（海の生物。kako-jun 2026-10-21） | 未定 | 通常敵（吸い付き・からみつき・多腕のトリッキーな戦い） | 仕様のみ | #12 |`

`| M128 | タコ（2x2） | A: 実家 v2＝海岸の集落・漁具（EA 1.5）。D: 吸い付き・からみつき・多腕（L 記述） | — （水） | 雑魚 | 吸い付き・からみつき（L 記述） | 仕様のみ | ◎ | 未定 | 可（能登は青年編の始まりで青年前半に戻れる。被災前→被災後でも海の敵は出る。2026-10-15 の一任による決定） |`

Make one photorealistic game battle sprite of one octopus, showing the complete body and exactly eight distinct arms with visible suction cups. Body and mantle yaw exactly 45° from camera-front (0°) toward screen-right (+x), not the 90° true-right profile; show both front and right planes. Pose the arms curled and extended in multiple directions to suggest grasping and wrapping; keep arm tips separated so each of eight arms can be counted. Center the complete creature; keep the nontransparent subject at least 32 pixels from every canvas edge. Logical occupancy gridClass 2x2; use square 1024×1024 canvas. Isolated transparent background with genuine alpha. Do not render habitat, settlement, fishing gear, water, rocks, floor, contact shadow, base, outline, text, logo, extra creatures, or unsupported effects.

Tool setting: `transparent_background: true`.
