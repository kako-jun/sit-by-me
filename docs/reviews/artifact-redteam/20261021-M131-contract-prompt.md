# M131 contract/prompt review — 2026-10-21

- Reviewer: Codex, delegated independent reviewer (not the prompt author)
- Target: M131 スズメバチ
- Stage: `contract/prompt`
- Verdict: **pass for this exact prompt revision**
- Canonical base: `64bb973967e41475ef55678e9ce7d10dd413dc4a`
- Reference inspected, reference-only: `assets/images/enemies/M131.webp`, 640×636 WebP with alpha; SHA-256 `837d8dc7b952e2ed814c978c4c40cdf4d40045fe21b397e141a6c6f4343a58e5`
- No image was generated.

## Canonical sources inspected

- `.claude/skills/sit-artifact-redteam/SKILL.md`, enemy prompt-review criteria and finding/disposition requirements
- `.claude/skills/sit-enemy-sprite/SKILL.md`, §§12, 14–22, 24–47
- `docs/content-registry.md`, enemy index and prompt assembly rules
- `docs/monsters.md:130` (M131 source row), `:276` (M131 current grid declaration), `:327` (location-unspecified summary)
- `docs/dungeon-enemies.md:124` (M131 encounter row), `:284` and `:421` (allocation/provenance context)
- `docs/art-direction.md`, §“イマジナリー敵” / “毒と尖り” (hornet is listed as a fear-based living enemy)
- `docs/assets-policy.md:3–5,13` (photorealistic generated subjects; transparent isolated enemy master without outline/base/shadow)
- Actual pixels of `assets/images/enemies/M131.webp`
- Complete prompt from `/tmp/sit-m131-prompt.txt`

## Complete prompt reviewed

> Use case: photorealistic-natural
>
> Asset type: single enemy battle master sprite for a Final Fantasy-inspired side-view RPG
>
> Primary request: Create one realistic hornet enemy. Canonical enemy record: "M131 | スズメバチ | 生物 | 卯辰山 UTS-01 登り口（一任による決定 2026-10-15、docs/dungeon-enemies.md が正本） | 未定 | 未定 | 未定 | assets/images/enemies/M131.webp（imagegen 透過直生成を採用。長辺640。加工前の原本は残さない） | #12、#17". Encounter source row: "M131 | スズメバチ（1x1） | A: 登り口・杉木立（EA 1.3） | — | 雑魚 | 未定 | 絵あり | △ | 未定 | 未定". The encounter row is placement context only; do not depict a map or scenery. Its elemental attribute, weakness, resistance, battle role, and special attack are unspecified; do not invent any of them or add elemental effects.
>
> Input image: Image 1 is the existing M131 hornet sprite, used only as a reference for the hornet species, black-and-yellow pattern, wings, legs, and realistic anatomy. Do not copy its exact pose or its true-right-facing profile.
>
> Subject: Exactly one hornet, with six legs, two antennae, two pairs of translucent wings, segmented abdomen, and a natural stinger as part of its anatomy. No other insects or objects.
>
> Style/medium: Photorealistic animal rendering with realistic insect anatomy and texture, suitable for a transparent battle sprite.
>
> Composition/framing: One complete centered hornet, logical gridClass 1x1. Its head and thorax face 45 degrees from camera-front (0 degrees) toward true right profile (90 degrees), pointing toward image-right, with both compound eyes visible and both the front plane of the head and right-side plane of the thorax visible. Do not show a 90-degree profile. Keep antennae, wings, legs, and stinger inside the canvas.
>
> Lighting/mood: Neutral clear light that makes the black-and-yellow pattern and translucent wings readable.
>
> Constraints: Genuine transparent background (tool parameter transparent_background=true). No text, letters, logos, watermark, border, outline, pedestal, ground plane, floor, contact shadow, nest, tree, leaves, forest, extra insects, poison droplets/cloud, or elemental effects. Do not crop any part of the hornet.

**Tool setting required for generation:** actually pass `transparent_background: true` to imagegen; the prompt's parenthetical documents the requirement but does not itself set the tool parameter.

## Checks performed

| Check | Evidence | Result |
|---|---|---|
| Source identity and no invented attributes | `docs/monsters.md:130` identifies M131 as a hornet and leaves attribute, weakness/resistance, and skill unspecified. `docs/dungeon-enemies.md:124` likewise leaves battle role detail and skill unspecified. Prompt explicitly preserves these as unspecified, forbids inventing them, and bans elemental effects. | Pass |
| Anatomy and exact count | The named species is a hornet. Prompt calls for exactly one and lists its insect anatomy (six legs, two antennae, two wing pairs, segmented abdomen, natural stinger), and excludes other insects/objects. These are species anatomy, not a new attack or ability. The viewed reference shows the same black/yellow hornet identity, veined wings, legs, antennae, and stinger. | Pass |
| Logical grid class | `docs/monsters.md:276` declares M131 `1x1`; encounter row `docs/dungeon-enemies.md:124` also labels it `1x1`. Prompt declares logical `gridClass 1x1`, without implying pixel dimensions or aspect ratio. | Pass |
| Head and thorax orientation | Sprite skill §20 defines front as 0°, true-right profile as 90°, and requires both front and right-side planes. Prompt specifies 45° for head and thorax with those endpoints, explicitly asks for both head planes and the thorax right-side plane, and rejects a 90° profile. The existing reference visibly presents a right-facing, nearly profile pose; prompt correctly limits it to species/markings/anatomy and explicitly forbids copying that pose/profile. | Pass |
| Location/map provenance | Monster row names UTS-01; encounter row `docs/dungeon-enemies.md:124` gives the mountain entrance and cedar grove as placement context. Prompt labels that row context-only and explicitly forbids map/scenery; it does not turn the allocation rationale into depicted scenery. | Pass |
| TBD fields | Attribute, weakness, resistance, battle role, and special attack remain unspecified in source rows. Prompt says not to invent any of them and the only added details are visible species anatomy and reference-grounded appearance. No image-relevant unresolved decision is converted into a guessed feature. | Pass for prompt stage |
| Style, transparency, and negative constraints | Photorealistic animal rendering matches `docs/assets-policy.md:3–5`. Prompt requires genuine transparency and calls out `transparent_background=true`; it excludes text/logo, outlines, pedestal/base, floor/contact shadow, map/nature scenery, extra insects, and toxin/element effects, consistent with assets policy and sprite skill §§22, 42. The actual tool argument must still be set. | Pass for contract stage |

## Disposition

No blocker, major, or minor finding remains for this exact prompt. The pass covers only the `contract/prompt` stage and does not change the existing asset's adoption status. Before generation, use `transparent_background: true` as the actual tool argument. Any resulting candidate still needs an independent raw-image check for count, anatomy, 45° head and thorax planes, alpha, uncropped parts, and prohibited additions; adoption remains a separate human decision.
