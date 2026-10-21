# M203 prompt contract — 2026-10-21

- Target: M203 城の護衛敵: インフレ
- Stage: contract/prompt
- Status: independent prompt and raw-image reviews passed; adoption pending
- Grid class: `2x1` (`docs/monsters.md` §3-7)
- Candidate: `exec-8338ce18-40be-4880-a211-7a9ddce5112c.png` (1536×1024 RGBA)

## Canonical source rows

- `docs/monsters.md` M203: inflation, represented by price tags/numbers and pressure on daily life.
- `docs/monsters.md` §3-7: `M203〜M204 | 2x1 | 圧迫する値札群・横長のニュース画面`.
- `docs/dungeon-enemies.md` M203: ordinary castle-only guardian. Its attack grows in strength as used; high gold reward is not a visual requirement.
- `docs/assets-policy.md`: enemies and objects use photorealistic generated images as isolated transparent cutouts.

## Prompt

Create one isolated ordinary RPG enemy battle sprite for M203 “inflation”, logical gridClass 2x1, on a transparent landscape canvas 1536×1024 px. Photorealistic generated-object style, as if photographed in a studio: a horizontally spread, threatening mass of oversized price tags and mechanical numeral tiles, visibly bending and buckling inward beneath a dense heavy dark pressure band. Make the abstract numeral tiles suggest numbers without showing any readable amount or currency. Price tags should be the unmistakable core motif; oppressive weight and everyday cost pressure should be conveyed by compression and warped shapes. No people, hands, brands, real products, real shop, readable writing, money symbols, coins, floor, scenery, contact/cast shadow, frame, or separate props. Camera exactly 45 degrees from camera-front toward +x; show the fronts and right edges of the tags and number tiles. Entire silhouette with some margin, no part cut off. Transparent background. High-quality photorealistic fantasy RPG enemy cutout, strong clear silhouette and practical material detail.

Tool setting: `transparent_background: true`.

## Independent prompt review

- Reviewer: `/root/enemy_input_audit` (2026-10-21)
- Verdict: `pass`.
- The prompt covers price tags, numeral shapes, and pressure; it does not turn the high-gold reward into an image requirement. Review requested abstract numerals without readable amount/currency, exact front-to-+x camera wording, and no shadows or frame; all are included above.

## Independent raw-image review

- Reviewer: `/root/m130_prompt_review` (2026-10-21)
- Verdict: `pass`.
- The 1536×1024 RGBA image has transparent exterior and a complete horizontal silhouette. Price tags, abstract number-like tiles, and crushing weight read clearly; no readable amount, currency, text, people, or scenery appears. The photorealistic materials and oblique front/right planes match the contract.
