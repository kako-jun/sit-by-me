# M133 contract/prompt review — 2026-10-21

- Reviewer: Codex, delegated independent reviewer (not the prompt author)
- Target: M133 毒キノコ
- Stage: `contract/prompt`
- Verdict: **pass for this exact prompt revision**
- Canonical base: `64bb973967e41475ef55678e9ce7d10dd413dc4a`
- Reference inspected, reference-only: `assets/images/enemies/M133.webp`, 640×466 WebP with alpha; SHA-256 `2984bd3d1899eb90999c6579962dacaa7a164aa7f1b2ea0781e78ab7e1be9fbe`
- No image was generated.

## Canonical sources inspected

- `.claude/skills/sit-artifact-redteam/SKILL.md`, enemy prompt review and disposition requirements
- `.claude/skills/sit-enemy-sprite/SKILL.md`, §§12, 14–22, 24–47
- `docs/content-registry.md`, enemy type index and prompt assembly rules
- `docs/monsters.md:132` (M133 source row), `:224` (M133 current 1x1 grid group), `:278` (image dimension record), `:319` (candidate location summary)
- `docs/dungeon-enemies.md:122` (encounter row), `:285` (allocation context)
- `docs/art-direction.md:83` (poison-and-pointed fear category includes poisonous mushrooms)
- `docs/assets-policy.md:3–5,13` (photorealistic generated enemy art; isolated transparent master without outline/base/shadow)
- Actual pixels of `assets/images/enemies/M133.webp`
- Complete prompt from `/tmp/sit-m133-prompt.txt`

## Complete prompt reviewed

> Use case: photorealistic-natural
>
> Asset type: single enemy battle master sprite for a Final Fantasy-inspired side-view RPG
>
> Primary request: Recreate the M133 poisonous mushroom enemy as an isolated transparent sprite. Canonical enemy record: "M133 | 毒キノコ | 毒と尖り | 湿った林・古い木壁・山の遊園地跡。卯辰山 utatsuyama-sunnyland（一任による決定 2026-10-15、docs/dungeon-enemies.md が正本） | 未定 | 未定 | 未定（胞子で視界や判断を乱す） | 生成済み: assets/images/enemies/M133.webp（採否待ち。透過・胞子つき） | #12". Encounter source row: "M133 | 毒キノコ（1x1） | A: 台帳の候補地「湿った林・古い木壁・山の遊園地跡」（L 3-3・4）。E: 胞子で視界や判断を乱す（状態異常の担い手） | — | 雑魚 | 胞子（L 記述） | 絵あり | ◎ | 未定 | 未定". The location is context only; do not depict a map or environment.
>
> Input image: Image 1 is the existing M133 sprite, used only as a reference for mushroom species and color/texture identity. Preserve its exact visible group count and arrangement: four mushrooms, one dominant red cap with three smaller mushrooms around it, pale stems, white cap flecks, and visible airborne spores. Do not copy its soil, moss, ground base, vegetation, or background.
>
> Subject: The same four-mushroom enemy group shown in the reference, with red caps, white flecks, pale stems, and airborne spores. No faces, eyes, limbs, or anthropomorphic body.
>
> Style/medium: Photorealistic natural mushroom rendering with realistic cap and stem texture, suitable for a transparent battle sprite.
>
> Composition/framing: A compact centered group within logical gridClass 1x1. Keep all four mushrooms and visible spores fully inside the canvas. Show cap and stem volume through visible surface curvature and internal shading; there is no head/torso orientation requirement because these are non-anthropomorphic fungi.
>
> Lighting/mood: Neutral clear lighting that makes the red caps, pale stems, and white flecks readable.
>
> Constraints: Genuine transparent background (tool parameter transparent_background=true). No text, letters, logos, watermark, border, outline, pedestal, ground plane, soil, moss, grass, roots, wood, forest, tree, scenery, contact shadow, poison cloud, colored toxin effect, or elemental effects. Do not crop the mushrooms or spores.

**Tool setting required for generation:** pass `transparent_background: true` as the actual image-generation tool argument. The parenthetical in the prompt records the requirement but does not itself set the argument.

## Checks performed

| Check | Evidence | Result |
|---|---|---|
| Count and arrangement | In the actual reference, four red-capped mushrooms are visible: one dominant cap near upper center/right, a medium mushroom behind-left, a smaller mushroom at lower-left, and a medium/small mushroom at lower-right. Prompt's “one dominant red cap with three smaller mushrooms around it” matches this layout and fixes the count at four. Floating spore particles are not counted as additional mushrooms. | Pass |
| Appearance and spore source | `docs/monsters.md:132` records “未定（胞子で視界や判断を乱す）” and “透過・胞子つき”; encounter row `docs/dungeon-enemies.md:122` also states the spores are the status-effect carrier. The reference visibly has pale cap flecks, pale stems and small airborne particles around the group. The prompt asks for visible spores while forbidding a separate poison cloud, colored toxin, and elemental effect; it does not invent a new attack visual. | Pass |
| Logical grid class | `docs/monsters.md:224` specifies `1x1` for M130–M135, including M133; encounter row `docs/dungeon-enemies.md:122` independently labels M133 `1x1`. Prompt uses logical `gridClass 1x1` and does not infer pixels/aspect ratio. | Pass |
| Attribute and other unknowns | The M133 master row leaves attribute, weakness/resistance, and broader details unspecified. Prompt includes those source TBDs unchanged and adds no elemental attribution/effects or toxin-cloud effect. “Poisonous mushroom” follows the canonical enemy name, while spores are explicitly documented. | Pass |
| Map provenance only | The source lists candidate placement among a wet grove, old wooden walls and the mountain amusement-park ruins. Prompt labels the encounter row as location context only and explicitly forbids depicting a map/environment; it also excludes soil, moss, grass, roots, wood, forest, tree and scenery. No placement setting is treated as required sprite content. | Pass |
| Anatomy/orientation N/A | The source calls M133 a fungus; prompt explicitly excludes faces, eyes, limbs and anthropomorphic form. Under enemy-sprite skill §22, when an enemy has no head/torso/eyes, those orientation checks are N/A and must not be invented. Cap/stem volume is a form/material instruction, not anatomical yaw. | Pass; N/A justified |
| Style and asset constraints | `docs/assets-policy.md:3–5` requires photorealistic generated enemy art; §13 requires isolated transparent enemy masters without outline/base/contact shadow. Prompt's mushroom material/style matches, asks for genuine transparency and prohibits text/logo, border, outline, ground, soil, moss, scenery, pedestal and contact shadow. The actual tool argument remains required at generation. | Pass for contract stage |

## Disposition

No blocker, major, or minor finding remains for this prompt. This is a `contract/prompt` pass only; it does not adopt or change the status of the existing image. At generation time, use the actual `transparent_background: true` tool argument. A later raw-image review must independently count the four mushrooms, verify spores and alpha, inspect crop/edge margins and prohibited scenery/effects, and retain adoption for human decision.
