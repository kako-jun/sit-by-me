# M114 prompt contract review — 2026-10-21

- Reviewer: Codex independent reviewer (`enemy_input_audit`)
- Target: M114 大人向けの本（目隠しされた表紙）
- Stage: contract/prompt; generation not reviewed or authorized by this review
- Prompt reviewed: exact proposed M114 prompt supplied for independent review on 2026-10-21
- Source revision: `84bbbdd80da95ecf2b88c7181a7374590aeeed9f`
- Sources: `.claude/skills/sit-enemy-sprite/SKILL.md`; `.claude/skills/sit-artifact-redteam/SKILL.md`; `docs/content-registry.md`; `docs/monsters.md` lines 113, 194–220, 346–348; `docs/dungeon-enemies.md` §5.2 (lines 430–437); `docs/art-direction.md` lines 81, 94, 96–97; `docs/assets-policy.md` lines 3–5, 13.

## Exact prompt reviewed

> Generate one isolated fantasy enemy master image for Sit by Me, ID M114, transparent background. Subject: one closed, upright adult-themed book, sized for gridClass 1x2 (logical vertical two-cell sprite). Use only the source concept ‘大人向けの本（目隠しされた表紙）’; make the defining read a dark cloth blindfold wrapped across the front cover, with a visible hardcover and cream page block. Keep all cover surfaces blank: no title, letters, logo, real person, or explicit imagery; do not expose or depict the contents. It should read as an eerie fantasy enemy through a slightly warped cover and tense wrapped cloth, while remaining clearly a book. Single object only, centered, whole silhouette visible, no scene, shelf, floor, base, cast shadow, frame, border, or extra props. Transparent background. Enemy objects use the project’s realistic generated-object treatment, not diorama treatment. No anatomic parts are present; head/torso yaw and eye gaze checks are N/A. Do not invent encounter location, combat abilities, element, or story details.

## Checks

- **ID and source concept:** M114 is a fear-media enemy, named “大人向けの本（目隠しされた表紙）”; its image note says not to depict explicit contents (`docs/monsters.md:113`). The prompt preserves a closed book with an obscured cover and explicitly excludes explicit imagery and contents. Pass.
- **Encounter placement:** M114 has no assigned dungeon placement. `docs/dungeon-enemies.md` §5.2 explicitly says it remains unassigned (`lines 430–437`), while `docs/monsters.md:348` lists it among enemies with undetermined locations. The prompt correctly adds no shelf, room, scene, or encounter location. Pass.
- **Grid:** `docs/monsters.md:220` assigns M114–M116 `1x2`, citing upright shelf-standing books/DVD cases. The prompt declares logical `gridClass 1x2` and an upright object. Pass.
- **Style and isolation:** `docs/assets-policy.md:5` requires realistic generated-object treatment for objects/enemies, not diorama treatment; line 13 requires isolated transparent enemy masters without frame, base, or contact shadow. The prompt complies.
- **Anatomy/orientation:** A book has no head, torso, or eyes; marking those checks N/A follows the enemy sprite skill. No 45° anatomical orientation claim is needed.
- **Image-relevant TBDs:** Attribute, abilities, weakness/resistance, and encounter location are unspecified, but none needs to appear in this isolated book image. No image-relevant unresolved TBD blocks generation.

## Findings

**Major — prompt adds unsupported visual specifics and leaves output canvas dimensions unspecified.** The canonical visual facts are the adult-oriented book and a blindfolded cover, with explicit contents omitted (`docs/monsters.md:113`; `docs/art-direction.md:81`). “Dark cloth,” “hardcover,” “cream page block,” “slightly warped cover,” and “tense wrapped cloth” choose material, color, construction, and supernatural appearance that the source does not establish; “slightly” and “tense” are also not concrete generation constraints under the sprite skill's unambiguous-input rule. Remove these additions or obtain a source decision. A neutral closed upright book with a blank cover visibly obscured by a blindfold is sufficient. The prompt should separately state the chosen pixel canvas dimensions; `gridClass` is logical occupancy and does not define pixel dimensions (`sit-enemy-sprite/SKILL.md`, “グリッド種別と出力枠”).

## Disposition

**Major; not yet pass for generation.** Correct the unsupported cover/material/warping details and add the chosen canvas px dimensions, then request a fresh prompt review. This review does not assign M114 a location or alter any canonical record. No image was generated or adopted.

## Revision review — 2026-10-21

### Exact revised prompt reviewed

> Create one isolated M114 enemy sprite on a transparent 1024×1536 px canvas. Depict one closed, upright book, with its front cover visibly blindfolded by a single opaque band crossing the cover. Keep the cover blank, with no title, letters, logo, or illustration. Do not show or imply explicit contents. Show the book’s full silhouette. No shelf, scene, floor, base, cast shadow, frame, border, or other object. gridClass: 1x2. This is an object with no head, torso, or eyes; anatomy and gaze checks are N/A. Do not add a location, combat ability, element, or story detail.

### Findings

- **Blindfold band:** Pass. An opaque band across the front cover is a literal, low-inference realization of `目隠しされた表紙` in `docs/monsters.md:113` and `docs/art-direction.md:81`. The prompt no longer introduces an unsupported band material or color. “Crossing the cover” permits variation in exact band placement, but that does not change the defining feature or identify a conflicting object; no placement detail is required by the source.
- **Contents and other details:** Pass. Closed book, blank cover, no explicit contents, and no scene props follow `docs/monsters.md:113`. Nothing adds a location; M114 remains unassigned per `docs/dungeon-enemies.md` §5.2, lines 430–437.
- **Grid and output canvas:** Pass. `gridClass 1x2` matches `docs/monsters.md:220`; the explicitly specified 1024×1536 px canvas is independent technical output size, consistent with the sprite skill's separation of grid occupancy and pixel dimensions.
- **Anatomy checks:** Pass. A book has no head, torso, or eyes, so N/A is correct under the enemy sprite skill.
- **Major — omitted required visual style:** `docs/assets-policy.md:5` says objects and enemies use photorealistic generated imagery. The revised prompt does not specify that style (the previous proposal did). “Enemy sprite” does not make the rendering style unambiguous. Add a concise style clause such as “Photorealistic-natural object rendering.” No other unsupported additions or image-relevant TBDs remain.

### Revision disposition

**Major; not yet pass for generation** until the photorealistic-natural object treatment from `docs/assets-policy.md:5` is stated in the prompt. No generation occurred and no canonical record was changed.

## Final prompt review — 2026-10-21

### Exact prompt reviewed

> Create one isolated M114 enemy sprite on a transparent 1024×1536 px canvas. Depict one closed, upright book, with its front cover visibly blindfolded by a single opaque band crossing the cover. Keep the cover blank, with no title, letters, logo, or illustration. Do not show or imply explicit contents. Show the book’s full silhouette. No shelf, scene, floor, base, cast shadow, frame, border, or other object. gridClass: 1x2. This is an object with no head, torso, or eyes; anatomy and gaze checks are N/A. Use the realistic generated-object rendering specified in docs/assets-policy.md. Do not add a location, combat ability, element, or story detail.

### Checks and disposition

- **Source identity:** Pass. The target row defines M114 as an adult-oriented book with a blindfolded cover and explicitly says not to depict explicit contents (`docs/monsters.md:113`). A single opaque band across the visible front cover is a literal, minimal depiction of that concept; no color, material, or supernatural surface detail is added. Keeping the cover blank and contents hidden is consistent with the source.
- **Grid and dimensions:** Pass. `gridClass 1x2` matches `docs/monsters.md:220` (upright books/DVD cases); `1024×1536 px` is a separately specified canvas size, not inferred from gridClass. The sprite skill explicitly treats logical occupancy and pixel dimensions as distinct.
- **Encounter placement:** Pass. M114 remains unassigned under `docs/dungeon-enemies.md` §5.2 (`lines 430–437`), and the prompt adds no shelf, location, scene, or encounter detail.
- **Style and isolation:** Pass. The prompt explicitly delegates to the realistic generated-object treatment in `docs/assets-policy.md:5`. Its transparent isolated single-object composition and exclusions follow `docs/assets-policy.md:13` and `.claude/skills/sit-enemy-sprite/SKILL.md`.
- **Anatomy and gaze:** Pass. A book has no head, torso, or eyes; N/A is correct under the sprite skill.
- **TBDs:** M114's location, attribute, abilities, and weaknesses remain unresolved, but none is depicted or needed for this object sprite. No image-relevant TBD blocks the prompt.

**Pass — contract/prompt stage only.** The exact prompt is source-aligned and sufficiently concrete. This does not review a generated image or approve adoption. No image was generated and no canonical record was edited.
