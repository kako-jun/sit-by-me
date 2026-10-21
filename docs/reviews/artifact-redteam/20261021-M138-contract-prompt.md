# M138 contract/prompt review — 2026-10-21

- Reviewer: Codex, delegated independent reviewer (not the prompt author)
- Target: M138 氷柱
- Stage: `contract/prompt`
- Verdict: **pass for this exact prompt revision**
- Canonical base: `64bb973967e41475ef55678e9ce7d10dd413dc4a`, plus the current uncommitted M138 source rows
- Reference inspected, reference-only role: `assets/images/enemies/M138.webp`, 640×432 WebP with alpha; SHA-256 `177cc0aa28d4bad180ce82a866a079f947164d5b80aad6b930a5313f2921a78c`
- No image was generated.

## Canonical sources inspected

- `.claude/skills/sit-enemy-sprite/SKILL.md`, §§14–22, 24–46
- `.claude/skills/sit-artifact-redteam/SKILL.md`, enemy contract/prompt criteria and findings disposition
- `docs/content-registry.md`, enemy index and prompt assembly rules
- `docs/monsters.md`, M138 source row, §3-7 current grid declaration, §3-8 old-image footprint record
- `docs/dungeon-enemies.md`, M138 encounter row and allocation row
- `docs/learning-schedule.md`, M138 ice-learning row and current ice-attribute note
- `docs/art-direction.md`, icicle placement among pointed/poison hazards
- `docs/assets-policy.md`, realistic generated enemy art and transparent enemy-master rules
- Actual pixels of `assets/images/enemies/M138.webp`

## Complete prompt reviewed

> Use case: photorealistic-natural
>
> Asset type: single enemy battle master sprite for a Final Fantasy-inspired side-view RPG
>
> Primary request: Create one vertical icicle enemy. Canonical enemy record: "M138 | 氷柱 | 毒と尖り（尖ったもの） | 卯辰山 UTS-01 登り口（一任による決定 2026-10-15、docs/dungeon-enemies.md が正本） | 氷（kako-jun 2026-10-21） | 未定 | 未定 | assets/images/enemies/M138.webp（採用: kako-jun 2026-10-14） | #12". Encounter source row: "M138 | 氷柱（1x2） | A: 登り口の石段・杉木立の冬（EA 1.3）。山の中ボス S002（氷）の前触れ | — （氷） | 雑魚 | 未定 | 絵あり | ◎ | 未定 | 未定". The encounter row is placement context only; do not depict a map or scenery.
>
> Input image: Image 1 is the existing M138 image, used only as a reference for clear ice material, icy blue-white coloration, internal fractures, and realistic frozen texture. Do not copy its broad horizontal row of many icicles.
>
> Subject: Exactly one hanging icicle made of clear, cold ice. It is a non-living object with no head or torso.
>
> Style/medium: Photorealistic natural ice rendering, consistent with the enemy asset set.
>
> Composition/framing: One isolated vertical ice formation, logical gridClass 1x2. The upper end is broader and irregular; the single body tapers continuously to one sharp downward point. Show distinct front and side crystal facets so the form is visibly three-dimensional. Keep the entire ice formation inside the canvas.
>
> Lighting/mood: Cool neutral lighting with controlled highlights that reveal clear ice and internal fractures.
>
> Constraints: Genuine transparent background (tool parameter transparent_background=true). Head, torso, eyes, limbs, face, and 45-degree anatomical yaw are not applicable; do not anthropomorphize the icicle. No text, letters, logos, watermark, border, outline, pedestal, ground plane, floor, contact shadow, roof, eave, scenery, extra icicles, ice shards, snow, or elemental effects. Do not crop the object.

**Generation setting required by the skill:** pass `transparent_background: true` as the actual image-generation tool argument; the prompt's parenthetical text documents the setting but does not substitute for the tool argument.

## Checks performed

| Check | Evidence | Result |
|---|---|---|
| ID, identity, location and attribute | `docs/monsters.md:137` says M138 is an icicle enemy at UTS-01 with `氷（kako-jun 2026-10-21）`. `docs/dungeon-enemies.md:121` says it is an icicle preceding the ice summon S002; `docs/learning-schedule.md:158,219` also associates M138 with Ice. Prompt carries these facts without adding a new setting. | Pass |
| Map provenance only | Encounter row `docs/dungeon-enemies.md:121` mentions the winter stone steps and cedar grove. Prompt quotes this row as context only and explicitly forbids map/scenery depiction; it excludes roof/eave and scenery too. Allocation row `:290` identifies UTS-01 as placement rationale, not additional sprite content. | Pass |
| Exact count and shape | Source identity is one icicle; prompt specifies exactly one isolated vertical formation, one continuous body and one downward point, and forbids extra icicles/shards. The reference's many-icicle row is explicitly reference-only and excluded. | Pass |
| Grid class | `docs/monsters.md:226` declares M138 `1x2`; `docs/dungeon-enemies.md:121` independently labels it `1x2`. `docs/monsters.md:283` clearly marks the old image's `1x1` as legacy and current `1x2` as target. Prompt declares logical `gridClass 1x2`; no pixel ratio is inferred. | Pass |
| Ice attribute | Master row and learning/encounter rows agree on Ice (`氷`). Prompt's clear cold ice material and icy blue-white reference are consistent. | Pass |
| Orientation N/A | M138 is a nonliving icicle/object, and the prompt explicitly says it has no head or torso and forbids anthropomorphizing it. Sprite skill §22 allows head/torso/eye orientation checks to be N/A when those parts do not exist and says not to invent them. The prompt separately calls for crystal facets, not anatomical face planes. | Pass; N/A is justified |
| Three-dimensional form and art direction | Prompt asks for front and side crystal facets, not invented anatomy. `docs/assets-policy.md:5` calls for realistic generated images of objects/enemies; actual `M138.webp` visibly supplies clear ice, blue-white color and internal fracture cues for the reference role. | Pass |
| Transparency and negative constraints | Sprite skill §42 requires transparent tool setting and measured alpha after generation; prompt names `transparent_background=true` and has no contradictory backdrop. Assets policy §13 and sprite skill §22 exclude outline/base/contact shadow; prompt also excludes text/logo, ground/floor, roof/eave, scenery, extra icicles, snow and elemental effects. Actual tool argument must still be set as stated above. | Pass at contract stage |
| Unresolved TBD | Weakness/resistance/role are `未定` in source rows, but the image depicts only the icicle shape and material; no unresolved visual fact is required. The existing adopted image is a reference, and this prompt review does not change its adoption state. | Pass for prompt stage |

## Disposition

No blocker, major, or minor finding remains for this prompt. This pass applies only to the exact `contract/prompt` stage. If a candidate is generated, use the actual `transparent_background: true` tool argument, then inspect the raw file's alpha, alpha-positive bounding box, single-object count, full uncropped point, material and negative constraints. This review does not adopt a replacement or alter the current asset status.
