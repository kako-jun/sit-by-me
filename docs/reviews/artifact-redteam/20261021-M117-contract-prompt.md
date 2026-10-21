# M117 prompt contract review — 2026-10-21

- Reviewer: Codex independent reviewer (`enemy_input_audit`)
- Target: M117 怪人・ひとさらい風の絵本キャラ
- Stage: contract/prompt; no image generated
- Source revision: `84bbbdd80da95ecf2b88c7181a7374590aeeed9f`
- Sources inspected: `.claude/skills/sit-enemy-sprite/SKILL.md` lines 16–36, 42–46; `docs/content-registry.md`; `docs/monsters.md` lines 116, 196, 221, 346–348; `docs/dungeon-enemies.md` §5.2, lines 430–437; `docs/art-direction.md` lines 81, 94, 96–97; `docs/assets-policy.md` lines 3–5, 13.

## Exact proposed prompt reviewed

> Create one original M117 enemy sprite on a transparent 1024×1024 px canvas. Depict one nonhuman bogey creature as a character from a fictional picture book, evoking the source concept ‘怪人・ひとさらい風の絵本キャラ’ without depicting a real human, child, victim, kidnapping scene, or kidnapping prop. The creature has a visible head and torso. Set both head and torso yaw to exactly 45° from camera-front toward the creature’s right; show both the front plane and right-side plane of each. Set both eyes’ gaze vectors to +x (toward the player). Use a single standing creature and show its full silhouette. No clothing, accessories, text, logo, scene, floor, base, cast shadow, frame, border, or other figures. gridClass 1x1. Use the project’s realistic generated-object treatment. Do not add an encounter location, combat ability, element, or story detail.

## Checks

- **Identity and nonhuman depiction:** M117 is a “怪人・ひとさらい風の絵本キャラ” classified as fear media (`docs/monsters.md:116`; `docs/art-direction.md:81`). Treating this as a fictional, nonhuman picture-book bogey is a safe interpretation. It also follows the explicit rule not to make humans enemies (`docs/art-direction.md:94`). Excluding real people, children, victims, and an abduction scene/props prevents changing the image into a human or depicting an event. Pass.
- **Anatomy/orientation:** The source's `怪人` / `絵本キャラ` supports a character-like creature, while the 45° requirement is a shared enemy-sprite rule for any depicted head and torso (`sit-enemy-sprite/SKILL.md:18–22`). However, the proposed direction “toward the creature’s right” is ambiguous between anatomical right and canvas/screen right. The skill defines the rightward direction as screen `+x` and 45° from camera-front (`lines 20–22`). Major finding.
- **Eyes:** Neither the M117 row nor the art-direction entry specifies eyes or their number. “Both eyes” commits to exactly two visible eyes, which is an unsupported design choice. The shared rule only directs the gaze of eyes that are present; it does not require adding eyes (`sit-enemy-sprite/SKILL.md:22`). Major finding; use a conditional gaze clause for any visible pupils, or omit the gaze requirement if the character is eyeless.
- **Grid and canvas:** M117 is `1x1` (`docs/monsters.md:221`). The prompt correctly declares `gridClass 1x1` and separately states a 1024×1024 px canvas, consistent with the skill's separation of logical occupancy from pixel dimensions (`SKILL.md:24–36`). Pass.
- **Style and isolation:** `docs/assets-policy.md:5` requires realistic generated imagery for enemies, and line 13 requires a transparent, isolated sprite with no frame, base, or contact shadow. The prompt references the project treatment and excludes those elements. Pass.
- **Encounter placement and TBDs:** M117 remains unassigned in `docs/dungeon-enemies.md` §5.2 (`lines 430–437`); `docs/monsters.md:348` also lists M117 among unplaced enemies. The prompt correctly does not assign or depict a location. Unspecified element, abilities, weakness, and role details do not need to appear in the sprite. No image-relevant TBD independently blocks it.

## Findings and disposition

**Major; not yet pass for generation.** Replace “toward the creature’s right” with the skill-defined “toward screen-right (+x),” and avoid forcing exactly two eyes unless the canonical source is updated or this is explicitly approved as an appearance decision. For example: “Set the head and torso yaw to exactly 45° from camera-front (0°) toward screen-right (+x), showing the front and right-side planes of each. If eyes are visible, direct their gaze toward +x.” This review does not assign a location, modify a canonical record, generate an image, or approve adoption.

## Final contract re-review — 2026-10-21

### Exact revised prompt

> Create one original M117 enemy sprite on a transparent 1024×1024 px canvas. Depict one nonhuman bogey creature as a character from a fictional picture book, evoking the source concept ‘怪人・ひとさらい風の絵本キャラ’ without depicting a real human, child, victim, kidnapping scene, or kidnapping prop. The creature has a visible head and torso. Set both head and torso yaw to exactly 45° from camera-front toward screen-right (+x); show both the front plane and right-side plane of each. If eyes are present, direct their gaze toward screen-right (+x). Use one standing creature and show its full silhouette. No clothing, accessories, text, logo, scene, floor, base, cast shadow, frame, border, or other figures. gridClass 1x1. Use the project’s realistic generated-object treatment. Do not add an encounter location, combat ability, element, or story detail.

### Checks and disposition

- **Concept and safety:** Pass. `docs/monsters.md:116` and `docs/art-direction.md:81` define M117 as a fear-media picture-book character with a kidnapper-like bogey concept. “Nonhuman bogey creature” is a safe realization consistent with `docs/art-direction.md:94` (do not make humans enemies). The exclusions prevent depicting actual people, children, victims, or an abduction event/prop without displacing the source concept.
- **Anatomy and direction:** Pass. A character-like `怪人` can be represented with a head and torso; the exact 45° rule for those features comes from `.claude/skills/sit-enemy-sprite/SKILL.md:18–22`. The revised prompt now uses camera-front 0° and screen-right `+x`, so its yaw direction is unambiguous and displays the required front/right planes. The gaze is conditional and no longer invents a required eye count; any present eye gaze points `+x`, matching the skill.
- **Grid and canvas:** Pass. `gridClass 1x1` matches `docs/monsters.md:221`; 1024×1024 px is specified independently from logical occupancy, in line with the skill at lines 24–36.
- **Style and isolation:** Pass. `docs/assets-policy.md:5` defines the realistic generated-object treatment for enemy images; the prompt references it. Transparent isolation and exclusions of base, cast shadow, and frame comply with line 13 and the enemy sprite skill.
- **Placement and unresolved fields:** Pass. `docs/dungeon-enemies.md` §5.2 (`lines 430–437`) keeps M117 unassigned. The prompt adds no location. Unspecified element, abilities, weaknesses, and combat role are not depicted, so no image-relevant TBD blocks this prompt.

**Pass — contract/prompt stage only.** This verdict applies to the exact revised prompt above. No image was generated, no canonical record was edited, and this is not an adoption decision.

## Edit-contract review — 2026-10-21

### Exact prompt reviewed

> Edit reference image 1, the unadopted M117 candidate, preserving the same one nonhuman feathered bogey creature, its brown feather textures, color palette, body proportions, limbs, pose, scale, and full transparent cutout. Change only the yaw of the head and torso so each is exactly 45° from camera-front toward screen-right (+x). For BOTH head and torso, make the front-facing plane plainly visible and the right-side plane separately visible; the face must be a three-quarter view, never a side profile. If eyes are visible, aim their gaze toward +x. Retain the same hooked beak and single creature identity. Keep all original content exclusions: no human, child, victim, kidnapping scene/prop, clothing, text, logo, scene, floor, base, shadow, frame, border, or other figure. Transparent background. gridClass 1x1. Use the realistic generated-object treatment. Do not add location, ability, element, or story details.

- Reference image 1: `/home/kako-jun/.codex/generated_images/01a15ccc-868c-7f60-8889-229de4286e8f/exec-1722c419-5251-4ac6-8035-5c1a26cdcf06.png` (unadopted design/identity reference only; raw review `20261021-M117-raw-image-1722c419.md` found the head and torso angle noncompliant).

### Checks and disposition

- **Reference role and invariants:** Pass. I viewed the named reference. It depicts one nonhuman feathered, brown, hooked-beak creature with limbs and a visible eye. Those retained traits are tied explicitly to the candidate as an identity/design reference; the prompt does not treat that image as evidence of correct orientation. The raw review separately records the current yaw failure, and this edit asks to correct it.
- **Yaw and visible planes:** Pass. Both head and torso are set to exactly 45° from camera-front toward screen-right (`+x`), with their front and right-side planes separately visible; the face must be three-quarter and not a profile. This is concrete and matches `.claude/skills/sit-enemy-sprite/SKILL.md:18–22`. Changing yaw necessarily changes their projected view, but does not require changing identity, body proportions, or limb pose in the creature's own frame; the stated invariants do not contradict the requested correction.
- **Gaze:** Pass. “If eyes are visible” avoids adding eyes; `+x` gaze matches the shared rule.
- **Source and exclusions:** Pass. M117 is the fictional kidnapper-like picture-book character (`docs/monsters.md:116`; `docs/art-direction.md:81`). Its nonhuman treatment follows `art-direction.md:94`; the prompt excludes real people, children, victims, and abduction scenes/props. Candidate-derived feathers, color, limbs, and beak are preserved as current design identity rather than introduced as newly inferred canon facts. No location, abilities, element, or story facts are added.
- **Grid, style, and placement:** Pass. `gridClass 1x1` matches `docs/monsters.md:221`. Realistic enemy treatment follows `docs/assets-policy.md:5`. No placement is added; M117 stays unassigned per `docs/dungeon-enemies.md` §5.2, lines 430–437.

**Pass — edit-contract stage only.** The prompt is concrete and its requested view change is compatible with its identity/pose invariants. The reference's orientation failure remains a reason to edit; this contract review is not evidence that a resulting image will pass, and it does not approve adoption. No image was edited or generated and no canonical record was changed.

## Second edit-contract review — 2026-10-21

Before this review I read both raw-image reports: `20261021-M117-raw-image-1722c419.md` and `20261021-M117-raw-image-88f92ea1.md`. Both candidates remain unadopted; the first report found head and torso yaw noncompliant, and the second found the head still near-profile while the torso showed more front/side planes but was not conclusively at 45°. I viewed the second image as a design/identity reference only.

### Exact prompt reviewed

> Edit reference image 1, the latest unadopted M117 candidate. Preserve the same single nonhuman feathered bogey creature, brown feather texture/color, body proportions, limbs, pose, scale, and transparent isolated presentation. Keep the torso yaw at exactly 45° from camera-front toward screen-right (+x), with the chest/front plane and right-side feathered plane both visibly separate. Turn the head further toward camera until its yaw is exactly 45° from camera-front toward screen-right (+x), clearly a three-quarter view: show the front-facing facial plane together with the right-side plane; show both eyes on the two sides of the beak, with their gaze toward +x; show the beak’s front surface and right contour. Do not show a side-profile head. Keep the full silhouette inside the canvas with clear transparent margin at top and bottom. Preserve the same creature; no humans, children, victims, kidnapping scene/props, clothing, text, logo, scene, floor, base, shadow, frame, border, or other figure. Transparent background. gridClass 1x1. Use realistic generated-object rendering. Do not add location, abilities, element, or story details.

### Checks and findings

- **Design identity:** The reference visibly contains one nonhuman feathered creature, brown feather texture, a hooked beak, limbs, and one visible eye. Preserving these as reference-derived traits is appropriate for an identity-preserving edit. The prompt does not use either candidate as evidence of compliant yaw. Its concept remains consistent with M117 (`docs/monsters.md:116`; `docs/art-direction.md:81`) and the no-human-enemy rule (`art-direction.md:94`).
- **Both eyes:** Acceptable as a view instruction for this existing beaked, feathered creature: the requested three-quarter head angle can reveal the far-side eye that is hidden in the near-profile reference, and the prompt does not add eyes as a separate accessory. Both eyes' +x gaze matches the sprite skill's gaze rule (`SKILL.md:20–22`). The canonical M117 description does not independently prescribe eye count, so retain this only as an identity/view constraint tied to the existing design reference.
- **Yaw and planes:** Pass. Head and torso are each defined at exactly 45° from camera-front toward screen-right (+x). Separate front and right-side planes are specified for both; for the face, both eyes and the beak's front and right contour reinforce the requested three-quarter view. “No side-profile head” is consistent with, and reinforces, the 45° constraint. This is precise under `.claude/skills/sit-enemy-sprite/SKILL.md:18–22`.
- **Pose/proportions:** Pass. Maintaining anatomy, limbs, pose, and scale in the creature's local frame is compatible with changing yaw; the projected view is expected to change. No pixel-identical silhouette invariant is demanded.
- **Canvas and margin:** **Major.** The latest input candidate is `1254×1254` px per its raw-image report, but the edit prompt does not state the output canvas dimensions. `gridClass 1x1` does not define pixel size (`SKILL.md:24–36`). “Clear transparent margin” is qualitative and the previous reports document alpha envelopes reaching top and bottom edges. If this margin is a generation constraint, specify a numeric top/bottom margin; if not, remove the vague phrase and leave edge contact to raw review.
- **Other contract checks:** `gridClass 1x1` matches `docs/monsters.md:221`; style and transparent isolation follow `docs/assets-policy.md:5,13`. No location is added and M117 remains unassigned under `docs/dungeon-enemies.md` §5.2 (`lines 430–437`). Other TBD fields are not depicted.

### Disposition

**Major; not yet pass for edit generation.** Yaw, planes, and identity-preserving invariants are concrete and compatible; the second-eye request is acceptable only as a view of the existing beaked creature. Specify the output px canvas and either a numeric top/bottom margin or omit “clear transparent margin.” No image was edited or generated and no canonical record changed.

## Final edit-contract re-review — 2026-10-21

### Exact revised prompt

> Edit reference image 1, the latest unadopted M117 candidate. Preserve the same single nonhuman feathered bogey creature, brown feather texture/color, body proportions, limbs, pose, scale, and transparent isolated presentation. Output on a transparent 1254×1254 px canvas and keep the full silhouette uncut. Keep the torso yaw at exactly 45° from camera-front toward screen-right (+x), with the chest/front plane and right-side feathered plane both visibly separate. Turn the head further toward camera until its yaw is exactly 45° from camera-front toward screen-right (+x), clearly a three-quarter view: show the front-facing facial plane together with the right-side plane; show both eyes on the two sides of the beak, with their gaze toward +x; show the beak’s front surface and right contour. Do not show a side-profile head. Preserve the same creature; no humans, children, victims, kidnapping scene/props, clothing, text, logo, scene, floor, base, shadow, frame, border, or other figure. Transparent background. gridClass 1x1. Use realistic generated-object rendering. Do not add location, abilities, element, or story details.

### Checks and disposition

- **Reference/candidate role:** The latest unadopted candidate remains a design/identity reference only. Its raw-image report says the head still reads near-profile; the torso is closer to front-plus-side but not conclusively 45°. Neither prior raw report is used as evidence of orientation compliance.
- **Canvas and silhouette:** Pass. The prompt now specifies the reference's `1254×1254` px output canvas, distinct from `gridClass 1x1`, and says to keep the full silhouette uncut. The previous vague “clear transparent margin” condition is removed. Edge contact remains a raw-image observation, not an ambiguous prompt margin.
- **Head and torso geometry:** Pass. Each yaw is exactly 45° from camera-front toward screen-right (+x). For each, the front and right-side planes are explicitly required; the head additionally specifies both eyes on opposite sides of the beak and the beak's front surface/right contour, prohibiting a profile. This is operational under `.claude/skills/sit-enemy-sprite/SKILL.md:18–22`.
- **Both-eye view:** Pass. The existing reference is a feathered hooked-beak creature with one visible eye in a near-profile view. Requiring both eyes in the corrected three-quarter view is a view condition that reveals the far side of the same creature; it is not an added prop or a changed identity. Directing their gaze to +x matches the canonical orientation rule.
- **Preserved identity and source constraints:** Pass. Brown feathering, beak, limbs, proportions, pose, and scale are tied to the identity reference, not asserted as canonical traits. The nonhuman bogey interpretation remains consistent with `docs/monsters.md:116`, `docs/art-direction.md:81,94`. No human, victim, kidnapping scene/prop, setting, or new story fact is added. Realistic isolated treatment follows `docs/assets-policy.md:5,13`.
- **Grid and placement:** Pass. `1x1` matches `docs/monsters.md:221`; no location is added and M117 remains unassigned under `docs/dungeon-enemies.md` §5.2 (`lines 430–437`). Other TBD fields are not image-relevant.

**Pass — edit-contract stage only.** The exact prompt is complete and operational for a single edit. This does not certify the resulting image or authorize adoption. No image was edited or generated and no canonical record was changed.

## Framing-only edit-contract review — 2026-10-21

### Exact prompt reviewed

> Edit reference image 1, the latest M117 candidate. Preserve the exact same nonhuman feathered bogey creature, appearance, facial features, both visible eyes and +x gaze, existing head and torso yaw/visible planes (the already reviewed 45° three-quarter orientation), brown palette, feather detail, body proportions, pose, limbs, and expression. Make no other changes. Uniformly scale the complete creature to 80% of its current height and center it on the transparent 1254×1254 px canvas. Keep the entire silhouette, including every crest feather and all talon tips, within the canvas, with no feature cut off. No new objects, clothing, text, background, floor, shadow, base, border, frame, people, or kidnapping props. gridClass 1x1. Use realistic generated-object rendering. Do not add location, ability, element, or story details.

- Reference image: `/home/kako-jun/.codex/generated_images/01a15ccc-868c-7f60-8889-229de4286e8f/exec-59acb47b-47bc-4e0e-89d0-a508e138ec52.png`, the latest unadopted M117 v3 candidate; use only as identity/orientation reference. Raw review: `20261021-M117-raw-image-59acb47b.md`.

### Checks and disposition

- **Reference state:** The v3 raw review passes head/torso 45° three-quarter orientation and gaze but blocks the candidate because the crest and talon endpoints meet or are cropped at the canvas edges. This prompt treats v3 as the already reviewed identity/orientation reference, not as proof that the framing passes.
- **Scale and placement:** Pass. The reference canvas is 1254×1254 px and its alpha/content envelope reaches top and bottom. Uniformly scaling the complete figure to 80% of its current height gives an approximately 1003 px figure height if the current full-height envelope is used; centering that on a 1254 px canvas leaves approximately 125 px above and below. This is a concrete, proportion-preserving correction to the recorded crop, and `gridClass 1x1` remains separate from canvas pixel size.
- **Cropped endpoints:** Pass with the explicit full-silhouette condition. The source image clips some terminal feather/talon detail, so the edit must complete the already-present crest and talon contours while reducing scale; the prompt names those exact existing features and requires no additions or other changes. This is a necessary completion of the same silhouette, not an unsupported new prop or story detail.
- **Orientation and identity:** Pass. Preserving the already reviewed 45° head/torso planes and +x eye gaze while applying a uniform scale does not alter yaw or identity. The prompt does not instruct any viewpoint/orientation change.
- **Source compatibility:** Pass. The existing creature design remains the reference-derived realization of M117's nonhuman picture-book bogey (`docs/monsters.md:116`; `docs/art-direction.md:81,94`). The prompt adds no location, element, combat ability, or story detail. Realistic isolated treatment follows `docs/assets-policy.md:5,13`; 1x1 matches `docs/monsters.md:221`; M117 remains unassigned under `docs/dungeon-enemies.md` §5.2 (`lines 430–437`).

**Pass — framing-only edit-contract stage.** The 80% scale, canvas, centering, and required full silhouette are concrete and compatible with the approved orientation. This does not certify the resulting image or authorize adoption. No image was edited or generated and no canonical record was changed.
