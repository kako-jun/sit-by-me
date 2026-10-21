# M129 contract/prompt re-review — 2026-10-21

- Reviewer: Codex, delegated independent reviewer (not the prompt author)
- Target: M129 ゴンズイ
- Stage: `contract/prompt`
- Verdict: **pass for this exact prompt revision**
- Canonical base: `64bb973967e41475ef55678e9ce7d10dd413dc4a`, plus the current uncommitted working-tree updates to the M129 records and legacy-footprint note
- Existing image inspected as reference only: `assets/images/enemies/M129.webp`, 640×433 WebP with alpha; SHA-256 `8f4259c43b69b46dc937d64037121a344b17070347fd63a0aadef5ff6b6d198f`
- No image was generated.

## Canonical sources inspected

- `.claude/skills/sit-enemy-sprite/SKILL.md`, §§14–22, 24–46
- `.claude/skills/sit-artifact-redteam/SKILL.md`, enemy prompt review method, findings and independence gates
- `docs/content-registry.md`, enemy index and prompt assembly rules
- `docs/monsters.md`, M129 source row, §3-7 grid declaration, and §3-8 old-image footprint table
- `docs/dungeon-enemies.md`, M129 encounter and allocation rows
- `docs/learning-schedule.md`, water source and unresolved-issues rows
- `docs/art-direction.md`, water-edge creatures
- `docs/assets-policy.md`, enemy image and cutout constraints
- Actual pixels of `assets/images/enemies/M129.webp`

## Complete prompt reviewed

> Use case: photorealistic-natural
>
> Asset type: single enemy battle master sprite for a Final Fantasy-inspired side-view RPG
>
> Primary request: Create exactly five gonzui (Japanese striped eel catfish) as one enemy group. Their source record is: "M129 | ゴンズイ | 水辺の生物 | 水辺（章は未定）。内灘 uchinada-beach（一任による決定 2026-10-15、docs/dungeon-enemies.md が正本） | 水（魚。kako-jun 2026-10-21） | 未定 | 未定（群れと毒棘） | 生成済み: assets/images/enemies/M129.webp（採否待ち。5匹の群れ・右向き・透過） | #12". Encounter source row: "M129 | ゴンズイ（2x1） | A: beach＝砂浜・波打ち際（EA 1.4）。E: 群れと毒棘 | — （水） | 雑魚 | 群れ・毒棘（L 記述） | 絵あり（採否待ち） | ◎ | 未定 | 未定". The map/encounter source is context only; do not depict a background or map.
>
> Input image: Image 1 is the existing M129 sprite, used only as reference for exact species identity, five-member shoal, dark brown backs, pale lateral stripes, whiskers, fins, natural fin spines, and realistic fish texture. Do not copy its exact pose or its true-right-facing profile.
>
> Subject: Exactly five gonzui fish, with visible whiskers, characteristic striped bodies, and natural dorsal/pectoral fin spines. No other species, objects, characters, bubbles, water, or scenery.
>
> Style/medium: Photorealistic animal rendering with realistic anatomy and texture, suitable for a transparent battle sprite.
>
> Composition/framing: A single compact but clearly countable horizontal shoal inside logical gridClass 2x1. Each fish's head and body yaw is exactly 45 degrees from camera-front (0 degrees) toward true right profile (90 degrees), showing both front plane and right-side plane; all fish face toward image-right. Do not show any fish in a 90-degree profile. Keep all five complete, including fins and whiskers, within the canvas.
>
> Lighting/mood: Neutral, clear lighting that makes anatomy and stripes readable.
>
> Constraints: Genuine transparent background (tool parameter transparent_background=true). No text, letters, logos, watermark, border, outline, pedestal, ground plane, floor, or contact shadow. Do not add separate poison needles, toxin droplets/cloud, or any elemental effects; preserve the fish's natural fin spines. Do not crop any fish.

## Checks performed

| Check | Evidence | Result |
|---|---|---|
| ID, family, placement, attribute, behavior and lifecycle | `docs/monsters.md` M129 row identifies M129, ゴンズイ, 水辺の生物, Uchinada beach, Water (fish; dated decision), weakness/resistance `未定`, and group/poison-spine behavior. Its image remains adoption-pending. Prompt reproduces this source row. | Pass |
| Encounter facts and map provenance | `docs/dungeon-enemies.md` M129 encounter row says beach, group and poison spines, water learning, and雑魚. Prompt quotes it, then explicitly marks the map/encounter source as context only and forbids background/map depiction. No shoreline, water, map, or other scenery is requested. | Pass |
| Water-element consistency | `docs/monsters.md` M129 attribute is `水（魚。kako-jun 2026-10-21）`; encounter row has `—（水）`; learning schedule §5-5 now points to `docs/monsters.md` for the attribute and records the water decision. The earlier attribute-undecided wording is gone. | Pass |
| Grid class | `docs/monsters.md` §3-7 declares M129 `2x1` for five horizontally arranged gonzui; `docs/dungeon-enemies.md` M129 row also says `2x1`. The §3-8 table now labels the old image footprint `旧1x1 → 現行2x1` and identifies §3-7 as canonical. `gridClass` is explicitly logical occupancy, not a pixel ratio. | Pass |
| Five-member shoal | The M129 source image descriptor states `5匹の群れ`; art direction states群れと毒棘. Prompt says exactly five and clearly countable. The actual old reference contains five individual striped fish. | Pass |
| Species and defining anatomy | `docs/art-direction.md` water-edge-creature line identifies the shoaling, poisonous-spined gonzui. Actual `assets/images/enemies/M129.webp` shows five dark brown striped catfish with whiskers and fins. Prompt preserves species, stripes, whiskers, and natural dorsal/pectoral fin spines while excluding separate toxin props/effects. | Pass |
| Facing convention | Enemy-sprite skill §18 defines camera-front `0°`, true-right profile `90°`, requires `45°` and both front/right face planes, and rejects 90° profile. Prompt applies exact yaw to each fish's head and body, requires both planes, points all fish toward image-right, and explicitly rejects profiles. It also forbids copying the old reference's true-right profile. | Pass |
| Realistic style | `docs/assets-policy.md` states enemy assets are realistic-style generated images. `photorealistic-natural` is followed by an explicit photorealistic animal-rendering instruction; no conflicting stylized rendering direction remains. | Pass |
| Transparency and excluded elements | Enemy-sprite skill §42 requires transparent background in both prompt and tool setting; prompt includes `transparent_background=true`. Assets policy and sprite skill §§22, 44 require an isolated enemy cutout and exclude text/logo/outline/base/contact shadow; prompt explicitly excludes these, plus ground/floor/water/scenery. | Pass |
| Remaining TBDs | Weakness/resistance and other undecided mechanics do not need to appear in the image. The prompt adds no unsupported mechanics or poison effects. | Pass for prompt stage |

## Earlier findings and disposition

The prior review identified three prompt/source concerns: an unresolved water-attribute conflict, absence of a transparent tool setting, and a prohibition that could suppress natural fin spines. All are resolved in the current source bundle and exact prompt above. The separate issue that §3-8 described M129 as `1x1` has been qualified as the old image footprint, with current `2x1` declared canonical in §3-7. No prior findings are erased; this report records their resolution for this revision.

This is a **contract/prompt-stage pass only**. It permits the authoring workflow to proceed with one generation attempt using `transparent_background=true`; it does not pass or adopt a generated image. After generation, inspect the actual image at original size for the 45° planes of all five fish, exact count, transparency, and excluded elements, and record measured canvas and alpha bounds. Keep adoption pending until the human adoption decision.
