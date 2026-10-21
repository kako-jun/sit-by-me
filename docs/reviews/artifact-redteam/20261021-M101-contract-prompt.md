# M101 contract/prompt review — 2026-10-21

- Reviewer: Codex, delegated independent reviewer (not the prompt author)
- Target: M101 ロードローラー
- Stage: `contract/prompt`
- Verdict: **pass for this exact prompt revision**
- Canonical base: `64bb973967e41475ef55678e9ce7d10dd413dc4a`
- Reference image: none supplied or requested by the prompt; no prior profile/outline image was used as a generation reference.
- No image was generated.

## Canonical sources inspected

- `.claude/skills/sit-artifact-redteam/SKILL.md`, prompt-stage method and disposition criteria
- `.claude/skills/sit-enemy-sprite/SKILL.md`, §§12, 14–22, 24–47
- `docs/content-registry.md`, enemy type index and prompt assembly rules
- `docs/monsters.md:100` (M101 master row), `:207` (current `2x1`), `:255` (old-image footprint explicitly marked legacy)
- `docs/dungeon-enemies.md:88` (M101 encounter row), `:274` (placement rationale), `:401` (rare high-gold rationale)
- `docs/art-direction.md:3–5,71–74` (winter setting; road roller in the heavy-machinery fear category)
- `docs/assets-policy.md:3–5,13` (photorealistic generated objects/enemies; transparent enemy master without outline/base/shadow)
- Complete prompt from `/tmp/sit-m101-prompt.txt`

## Complete prompt reviewed

> Use case: photorealistic-natural
>
> Asset type: single enemy battle master sprite for a Final Fantasy-inspired side-view RPG
>
> Primary request: Recreate M101 ロードローラー as one isolated transparent sprite. Canonical enemy record: "M101 | ロードローラー | 圧倒的な機械・物 | 雪国の道路（フィールド・章は未定）。寺町 wide-road（広い道路）（一任による決定 2026-10-15、docs/dungeon-enemies.md が正本） | 未定 | 未定 | 未定 | assets/images/enemies/M101.webp（右向き・透過・運転者なし。2026-10-14 採用） | #12。技: どろだらけ（土のラーニング元。2026-10-15 kako-jun 決定。敵の専用 [特技]。効果・ダメージは未決。属性欄・弱点は変えない）". Encounter row: "M101 | ロードローラー（2x1。EA は大型扱い） | A: wide-road＝主道路（EA 1.1、L「雪国の道路」）。C: 土の元（EA 2.2、LS 68 の最早）。H: 高額ゴールド（めったに出ない。案を採用。§4.4） | どろだらけ | 雑魚 | 未定 | 絵あり | ◎ | 高額ゴールド（レア） | 可（拠点。再訪できる。MT 7.2）". Location, ability, and reward are contextual data only. Do not depict a map, road, environment, mud attack, magic, currency, or effects.
>
> Subject: One old yellow road roller machine with a broad cylindrical steel front drum, rear rubber tire, operator cabin, exhaust stack, and visible construction-machine frame. The cabin is empty; no driver or person. The machine has no head or eyes; head/eye orientation is N/A.
>
> Orientation: Vehicle heading yaw exactly 45 degrees toward image-right. The front cylindrical drum is the leading end and sits on image-right. Show the drum's curved rolling surface and one circular end face, plus the near side of the yellow body and cabin; do not show a flat 90-degree side profile or a head-on view. Preserve recognizable road-roller proportions.
>
> Style: Photorealistic natural machinery, worn yellow paint and aged steel with subtle traces of snow on the upper surfaces. No stylized outline, glow, rim light, or chromatic aberration.
>
> Composition: One complete machine, centered within logical gridClass 2x1. Keep all machine parts inside the central 80% of the canvas, with at least 10% transparent margin on all four sides. Ensure drum, tire, cabin, and exhaust are not cropped.
>
> Lighting: Neutral white lighting with even color and no colored edge cast.
>
> Constraints: Set transparent_background=true in the image-generation tool. Genuine alpha transparency outside the machine. Do not use an input image. No text, letters, logos, watermark, outline, fringe, halo, border, pedestal, ground plane, road, scenery, contact shadow, snow scene, driver, person, weapon, mud, magic, or additional objects. Do not crop or touch any canvas edge with opaque or partially transparent pixels.

## Checks performed

| Check | Evidence | Result |
|---|---|---|
| Identity and component description | `docs/monsters.md:100` and `docs/dungeon-enemies.md:88` identify one road roller. The specified drum, tire, cabin, exhaust and machinery frame are structural components of a road roller, not separate props. The prompt does not add a driver or other person. | Pass |
| `2x1` grid | `docs/monsters.md:207` sets M101 to `2x1`; encounter row `docs/dungeon-enemies.md:88` also says `2x1`. Prompt declares logical `gridClass 2x1` and defines pixel margins separately. | Pass |
| Heading/orientation and framing | Prompt specifies `45°` vehicle yaw toward image-right, puts the leading drum on image-right, names both the drum's curved surface and circular end face plus the machine's near side, and excludes both side profile and head-on view. It gives a central-80% composition and numeric 10% margins. The object has no head or eyes, so head/eye orientation is correctly N/A; vehicle heading is a separate, explicit property. | Pass |
| No old profile/outline reuse | Prompt explicitly says not to use an input image; it therefore cannot inherit the old image's profile or edge artifacts. The old 1x1 measurement is clearly legacy in `docs/monsters.md:255`; the current size contract is `2x1` in `:207`. | Pass |
| Source facts, TBDs, and unpictured mechanics | The source rows leave element, weakness/resistance and other combat details unresolved. The mud ability is recorded as the machine's skill, with effect/damage unspecified; the encounter reward is high gold. Prompt includes these only as contextual data and explicitly forbids depicting mud, magic, currency, attack effects, or environment. It does not invent an attribute or a mechanic. | Pass |
| Snow detail and setting | `docs/monsters.md:100` places M101 on a “snow-country road,” `docs/dungeon-enemies.md:88` cites L’s “snow-country roads,” and `docs/art-direction.md:3–5` establishes a winter-only snowy setting. Subtle snow traces on the machinery are consistent with that setting while the prompt excludes a snow scene/background. | Pass |
| No duplicated map depiction | The location and learning/reward rows are quoted for traceability, then explicitly made context-only. The prompt prohibits map, road and scene depiction and adds no route geometry or map detail to the sprite. | Pass |
| Art, alpha and negative constraints | Photorealistic machinery follows `docs/assets-policy.md:3–5`; isolated transparency without outline/base/contact shadow follows §13 and enemy-sprite skill §§22, 42. Prompt expressly requires the actual `transparent_background=true` tool argument and excludes text/logo, edge effects, scenery, ground, shadow, people and extra objects. | Pass for contract stage |

## Disposition

No blocker, major, or minor finding remains for this exact prompt. This pass permits author-side consideration of generation only; it does not generate or adopt an image. At generation, set the actual imagegen argument `transparent_background: true`. A raw-image review must verify the 45° front-right perspective, front drum on image-right, 10% margins, transparency, and prohibited additions.
