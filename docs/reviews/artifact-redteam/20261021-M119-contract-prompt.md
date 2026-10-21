# M119 prompt contract review — 2026-10-21

- Reviewer: Codex independent reviewer (`enemy_input_audit`)
- Target: M119 指名手配風ポスター
- Stage: contract/prompt; no image generated
- Source revision: `84bbbdd80da95ecf2b88c7181a7374590aeeed9f`
- Sources: `.claude/skills/sit-enemy-sprite/SKILL.md` lines 16–36, 42–46; `docs/content-registry.md`; `docs/monsters.md` lines 118, 196, 222, 346–348; `docs/dungeon-enemies.md` §5.2, lines 430–437; `docs/art-direction.md` lines 81, 94, 96–97; `docs/assets-policy.md` lines 3–5, 13.

## Exact prompt reviewed

> Create one M119 enemy sprite on a transparent 1024×1536 px canvas. Depict one upright paper wanted-style poster as a single object, full rectangular silhouette visible. Show the poster face nearly frontal with its plane turned exactly 45° from camera-front toward screen-right (+x), so the front surface and narrow right paper edge are both visible. On the poster, use only a fictional nonhuman monster silhouette as a simple black ink pictogram; no realistic person, child, victim, face, identifiable person, name, event, or readable text. Use blank header/footer areas and a bold circular stamp shape to make the object read as a wanted-style notice without lettering. No scene, wall, pole, shelf, floor, base, cast shadow, frame outside the paper, or other object. gridClass 1x2. This is a paper object, not a living subject; head/torso/gaze checks are N/A because the printed pictogram has no anatomical detail. Use realistic generated-object treatment. Do not add a location, abilities, element, or story details.

## Checks

- **Source identity and anti-human constraint:** `docs/monsters.md:118` names M119 as a wanted-style poster and requires fictional imagery with no real person, name, or event; `docs/art-direction.md:94` prohibits human enemies and says wanted-style posters must use fictional graphics without real persons/names/events. A nonhuman fictional pictogram, with no human/victim/event depiction, follows both sources.
- **Poster layout details:** Blank header/footer areas and a circular stamp mark are not canonical requirements, but are reasonable graphic-layout choices for making a wanted-style notice recognizable while honoring the no-text/no-real-identity rules. They add no encounter or story fact. Clarify that the circular mark is a printed graphic on the poster, not an additional physical object. The `only ... monster silhouette` wording should refer to the only illustration; otherwise it could conflict with the separately requested stamp shape.
- **Orientation/N/A:** The poster's paper plane has a concrete 45° camera view, with front and narrow right edge visible; this is an object-facing instruction, not a biological yaw claim. However, a “monster silhouette” may depict a head, torso, or eyes. The prompt later declares anatomy/gaze N/A on the assumption that the pictogram has no anatomical detail, but does not actually constrain the silhouette to be non-anatomical. As written, its icon could have a head/torso/eyes, triggering the sprite skill's 45° anatomical orientation and +x gaze rules (`SKILL.md:18–22`). Major finding.
- **Grid/canvas:** `gridClass 1x2` matches M119–M120 (`docs/monsters.md:222`); the 1024×1536 px portrait canvas is independently specified, as required by the sprite skill (`lines 24–36`). Pass.
- **Style/isolation:** Realistic generated-object treatment is required for objects/enemies (`docs/assets-policy.md:5`); an isolated transparent paper sprite with no base, cast shadow, or outside frame follows line 13. Pass.
- **Placement/TBD:** M119 remains unassigned under `docs/dungeon-enemies.md` §5.2 (`lines 430–437`) and `docs/monsters.md:348`; prompt correctly invents no location. Unspecified abilities and element are not depicted. No image-relevant TBD blocks the poster itself.

## Findings and disposition

**Major; not yet pass for generation.** Make the printed emblem's non-anatomical nature explicit so N/A is guaranteed, or instead specify a 45° head/torso and +x eye gaze for any anatomical figure. Safest correction: call it an abstract, nonhuman monster glyph with no discernible head, torso, eyes, or biological anatomy, and clarify the circular stamp is a printed mark. The specified 45° poster plane, grid, canvas, anti-human safeguards, and unassigned location are otherwise consistent. No canonical record was edited and no image was generated.

## Revised prompt re-review — 2026-10-21

### Exact prompt reviewed

> Create one M119 enemy sprite on a transparent 1024×1536 px canvas. Depict one upright paper wanted-style poster as a single object, full rectangular silhouette visible. Show the poster face nearly frontal with its plane turned exactly 45° from camera-front toward screen-right (+x), so the front surface and narrow right paper edge are both visible. On the poster, the only illustration is a simple abstract black ink glyph whose overall silhouette suggests a fictional nonhuman monster but has no discernible head, torso, eyes, or biological anatomy. Use blank header/footer areas and a bold red circular stamp shape printed on the paper, with no lettering, to make the object read as a wanted-style notice. No realistic person, child, victim, identifiable person, name, event, readable text, or logo. No scene, wall, pole, shelf, floor, base, cast shadow, frame outside the paper, or other object. gridClass 1x2. This is a paper object with a non-anatomical glyph; head/torso/gaze checks are N/A. Use realistic generated-object treatment. Do not add a location, abilities, element, or story details.

### Verdict

**Pass.** The plane instruction gives an exact 45° yaw from camera-front toward +x and explicitly requires the poster face and narrow right edge to be visible. The pictogram is now clearly non-anatomical, so the skill's head/torso/eye checks are correctly N/A. M119 is a paper wanted-style poster with fictional imagery; no human, real identity, name, or event is introduced. Blank header/footer areas and a printed circular stamp are graphic layout details that make the canonical wanted-style notice legible without adding story or encounter facts. The red stamp color is a visual treatment of that printed mark, not a new enemy attribute. `gridClass 1x2` and 1024×1536 px portrait canvas are explicit and consistent. The prompt does not invent placement; M119 remains unassigned per dungeon ledger §5.2. No generation or canonical source edit was performed.
