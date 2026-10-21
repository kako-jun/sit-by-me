# M139 prompt contract — 2026-10-21

- Target: M139 ウニ
- Stage: contract/prompt
- Status: pass for prompt stage; generation eligible
- Independent review: pass, `/root/enemy_input_audit`, 2026-10-21; N/A anatomical facing, camera elevation, grid and source facts verified
- Reference: `assets/images/enemies/M139.webp` (sea urchin body and spine identity only; do not copy its top-down/near-flat framing)
- Grid class: `1x1` (docs/monsters.md §3-7)

## Prompt

Use case: photorealistic-natural. Asset type: isolated battle sprite for Sit by Me enemy M139. The following are verbatim canonical source rows for metadata only; do not render words or map/location elements:

`| M139 | ウニ | 毒と尖り（尖ったもの） | 能登 釣り場（被災前。水のラーニング元なので被災後の能登の海辺でも出て再戦できる）（一任による決定 2026-10-15、docs/dungeon-enemies.md が正本） | 水（海の生物。kako-jun 2026-10-21） | 未定 | 未定 | assets/images/enemies/M139.webp（採用: kako-jun 2026-10-14） | #12 |`

`| M139 | ウニ（1x1） | A: 釣り場の岩・テトラ・磯（MT 7.3「能登＝岩・テトラ」）。E: 尖りと毒（AD 82 行）。事故の舞台 | — （水） | 雑魚 | 未定 | 絵あり | ◎ | 未定 | 可（能登は青年編の始まりで青年前半に戻れる。被災前→被災後でも海の敵は出る。2026-10-15 の一任による決定） |`

Create one isolated photorealistic battle sprite of a sea urchin, using `assets/images/enemies/M139.webp` only to preserve the dark spherical body and long sharp spines. Show the complete central body and all visible spine tips; arrange the spines radially outward from the body center, pointing in multiple directions, with front and rear spines overlapping. Set the camera elevation to exactly 45° above the horizontal and aim at the body center; show the rounded core and depth between front and rear spines, not a flat top-down view. A sea urchin has no head, torso, or eyes, so the enemy-facing yaw check is N/A; do not add a face. Keep the whole urchin centered, with every spine tip at least 32 px inside the canvas. Logical occupancy `gridClass 1x1`; use a square 1024×1024 canvas. Genuine transparent background. No water, rock, fishing gear, floor, contact shadow, base, outline, text, logo, or extra object.

Tool setting: `transparent_background: true`.
