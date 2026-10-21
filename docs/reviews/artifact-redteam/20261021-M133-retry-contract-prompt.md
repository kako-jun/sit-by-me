# M133 retry contract/prompt review — 2026-10-21

- Reviewer: Codex, delegated independent reviewer (not the prompt author)
- Target: M133 毒キノコ
- Stage: `contract/prompt`
- Verdict: **pass for this exact retry prompt**
- Canonical base: `64bb973967e41475ef55678e9ce7d10dd413dc4a`
- Reference inspected, limited to species/cap appearance/group identity: `assets/images/enemies/M133.webp`, 640×466 WebP; SHA-256 `2984bd3d1899eb90999c6579962dacaa7a164aa7f1b2ea0781e78ab7e1be9fbe`
- No image was generated.

## Canonical sources inspected

- `.claude/skills/sit-artifact-redteam/SKILL.md`, prompt-stage and enemy-review criteria
- `.claude/skills/sit-enemy-sprite/SKILL.md`, §§12, 14–22, 24–47
- `docs/content-registry.md`, enemy type index and prompt assembly rules
- `docs/monsters.md:132,224,278,319` (identity, grid, old image record and location summary)
- `docs/dungeon-enemies.md:122,285` (encounter row and placement provenance)
- `docs/art-direction.md:83` (toxic mushroom fear category)
- `docs/assets-policy.md:3–5,13` (photorealistic generated enemy art; transparent standalone enemy sprite without outline/base/shadow)
- Actual pixels of `assets/images/enemies/M133.webp`
- Complete retry prompt from `/tmp/sit-m133-retry-prompt.txt`

## Complete prompt reviewed

> Use case: photorealistic-natural
>
> Asset type: single enemy battle master sprite for a Final Fantasy-inspired side-view RPG
>
> Primary request: Recreate M133 poisonous mushroom as one isolated transparent sprite. Canonical row: "M133 | 毒キノコ | 毒と尖り | 湿った林・古い木壁・山の遊園地跡。卯辰山 utatsuyama-sunnyland（一任による決定 2026-10-15、docs/dungeon-enemies.md が正本） | 未定 | 未定 | 未定（胞子で視界や判断を乱す） | 生成済み: assets/images/enemies/M133.webp（採否待ち。透過・胞子つき） | #12". Encounter row: "M133 | 毒キノコ（1x1） | A: 台帳の候補地「湿った林・古い木壁・山の遊園地跡」（L 3-3・4）。E: 胞子で視界や判断を乱す（状態異常の担い手） | — | 雑魚 | 胞子（L 記述） | 絵あり | ◎ | 未定 | 未定". Locations and encounter information are context only. Do not depict any map or environment.
>
> Reference image: Use the existing M133 sprite only for mushroom species, cap color and texture, and exact group identity. Recreate exactly four mushrooms: one dominant large red cap with three smaller red-capped mushrooms around it; each has a pale stem and white cap flecks. Include separate pale airborne spore particles. Do not copy the reference soil, moss, wood, base, or scenery.
>
> Subject: Exactly four natural non-anthropomorphic mushrooms and separate airborne spores. No faces, eyes, limbs, or humanoid anatomy. Head, torso, and eye orientation are N/A.
>
> Style: Photorealistic natural mushroom surfaces and lighting. No illustration contour, glow, rim light, chromatic aberration, or colored edge treatment.
>
> Composition: A centered compact group for logical gridClass 1x1. Keep the complete silhouette of all four mushrooms and every visible spore within the central 80% of the canvas, leaving a transparent margin at least 10% of canvas width on the left and right and 10% of canvas height at the top and bottom. Arrange one dominant mushroom behind the three smaller mushrooms; keep each of the three smaller mushrooms separately identifiable. Do not overlap spores with the canvas boundary.
>
> Lighting: Neutral white light with no colored cast and no backlight around object edges.
>
> Constraints: Set transparent_background=true in the image-generation tool. The canvas background must be fully transparent outside the mushroom and spore silhouettes. No soil, moss, grass, roots, wood, forest, scenery, ground plane, contact shadow, pedestal, poison cloud, colored toxin effect, outline, fringe, halo, border, text, letters, logo, watermark, or additional mushroom. Do not crop or touch any canvas edge with opaque or partially transparent pixels.

## Checks performed

| Check | Evidence | Result |
|---|---|---|
| Species and exact count/arrangement | `docs/monsters.md:132` identifies M133 as poisonous mushroom. The actual reference contains one dominant red cap and three smaller red-capped mushrooms with pale stems and white flecks; prompt defines exactly that four-mushroom arrangement and separately identifies spores. | Pass |
| Spores and attribute discipline | Master row `docs/monsters.md:132` states spores impair vision/judgment and marks other combat details/attributes TBD; encounter row `docs/dungeon-enemies.md:122` identifies spores. Prompt includes only separate pale spores; it does not infer an elemental attribute, toxin cloud or elemental effect. | Pass |
| Grid class | `docs/monsters.md:224` sets M133 as `1x1`, and `docs/dungeon-enemies.md:122` independently labels it `1x1`. Prompt declares logical `gridClass 1x1` and separately defines clear canvas margins without treating pixel aspect as grid occupancy. | Pass |
| Provenance and environment | Rows cite candidate wet grove/old wooden wall/amusement-park ruin locations. Prompt explicitly makes these context only, forbids maps/environment, and excludes soil, moss, wood, vegetation and scenery. It does not add any environment details. | Pass |
| Anatomy orientation N/A | Fungus is non-anthropomorphic; prompt excludes face/eyes/limbs/humanoid anatomy and explicitly marks head/torso/eye orientation N/A, consistent with enemy-sprite skill §22. | Pass |
| Framing and clean edge requirement | The 10% margins on each side align with central 80% placement. The additional ban on touching any edge is consistent with the stated clear-margin intent. | Pass |
| Transparency, style, and artifact exclusions | Prompt explicitly requires the actual imagegen `transparent_background=true` setting, photorealistic surfaces, fully transparent outside silhouettes, and no outline/fringe/halo/chromatic aberration/colored edge treatment. This directly addresses the visible fringe blocker in the prior raw candidate. It also excludes ground/base/shadow/text and toxin/element effects consistent with assets policy. | Pass |

## Disposition

No blocker, major, or minor finding remains for this retry prompt. This pass covers the contract stage only and does not generate or adopt an image. The next generation must use the actual `transparent_background: true` tool argument. A new raw-image review must verify count, spore readability, edge margins, alpha, and the clean silhouette before human adoption consideration.
