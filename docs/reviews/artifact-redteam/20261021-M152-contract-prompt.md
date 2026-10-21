# M152 prompt contract — 2026-10-21

- Target: M152 砲弾の欠片
- Stage: contract/prompt
- Status: independent prompt review passed; generation eligible
- Reference: none; no existing M152 image
- Grid class: `1x1` (`docs/monsters.md` §3-7)

## Canonical source rows

`| M152 | 砲弾の欠片 | 回転する刃（風）に準ずる風のラーニング元（形の気配に留める） | 内灘 UCH-03 松林道（防砂林・砂丘）（kako-jun 承認 2026-10-15、docs/enemy-allocation.md §1.4） | 風（風のラーニング元「ざくざく」。kako-jun 承認 2026-10-15、docs/enemy-allocation.md §1.4） | 未定 | 未定 | 未定（生成していない。仕様のみ） | 形の気配に留め、実在の砲弾・兵器は再現しない（S003 の「砲弾の欠片の気配」と対応）。docs/enemy-allocation.md §1.4、art-direction.md |`

`| M152 | 砲弾の欠片 | A/B: 風の召喚獣 S003 の「砲弾の欠片の気配が混ざる殺意の強風」（L S003、AD 13 行）。内灘闘争の記憶（AD 12 行）。C 準ずる: 風の元（承認済み。L 固定） | — （風） | 雑魚 | 未定 | 仕様のみ | ◎（固定） | 未定 | 未定 |`

`| M152 | 1x1 | 砲弾の欠片の気配に留める通常敵 |`

## Prompt

Use case: photorealistic isolated battle sprite for Sit by Me enemy M152. Create exactly one dark gray weathered metal fragment with an irregular broken silhouette, broad broken face and visible thin edge, from a front view rotated 45° around the vertical axis toward screen-right (+x), so broad face and right edge are both visible. It should suggest a fragment of shrapnel but must not be recognizable as a real shell, unexploded ordnance, or specific weapon. Three narrow pale gray-blue streams of wind sweep around it toward screen-right; they remain secondary to the metal fragment. This is a wind-attribute battle sprite, not soil: no sand, soil, dune, bird, battlefield, explosion, weapon parts, fuse, writing, insignia, person, floor, contact shadow, frame, or extra objects. Logical occupancy gridClass 1x1. Square 1024×1024 canvas. Genuine transparent background.

Tool setting: `transparent_background: true`.

## Independent prompt review

- Reviewer: `/root/enemy_input_audit` (independent; 2026-10-21)
- Verdict: `pass`.
- Evidence: the fragment remains an abstract wind-learning enemy in `1x1`; it suggests shrapnel without depicting ammunition or a weapon. The three wind streams communicate the recorded wind attribute without adding sand or soil. The view states the 45° reference and visible planes, and the source's S003 relation is reflected without turning M152 into the summon.
- The dark-gray metal and three pale wind streams are visual choices, not facts claimed by the source rows; they do not conflict with canonical constraints.
