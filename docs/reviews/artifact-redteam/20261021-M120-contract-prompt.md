# M120 prompt contract review — 2026-10-21

- Reviewer: Codex independent reviewer (`enemy_input_audit`)
- Target: M120 誘拐を思わせる標識
- Stage: contract/prompt; no image generated
- Sources: `.claude/skills/sit-enemy-sprite/SKILL.md` lines 16–36, 42–46; `docs/content-registry.md`; `docs/monsters.md` lines 119, 196, 222, 346–348; `docs/dungeon-enemies.md` §5.2, lines 430–437; `docs/art-direction.md` lines 94, 96–97; `docs/assets-policy.md` lines 3–5, 13.

## Exact prompt reviewed

> Create one M120 enemy sprite on a transparent 1024×1536 px canvas. Depict one upright Japanese-style warning road sign panel attached to a single post; show the complete sign and post as one object. The sign face is turned exactly 45° from camera-front toward screen-right (+x), with its front plane and narrow right edge both visible. On the panel, place one fictional abstract black pictogram: a curling shadow shape enclosing an empty oval, suggesting something has disappeared. Use no anatomical features in the pictogram. No person, child, victim, real event, real sign design, lettering, words, numbers, logos, or recognizable real-world symbols. No road, environment, floor, base, cast shadow, extra sign, frame, or prop. gridClass 1x2. The object and pictogram have no head, torso, or eyes; anatomy/gaze checks are N/A. Use realistic generated-object rendering. Do not add a location, abilities, element, or story details.

## Checks

- **Source identity / fictional sign:** `docs/monsters.md:119` names the enemy “a sign suggesting kidnapping” and says “same as above,” referring to M119's fictional-image restriction. `docs/art-direction.md:94` explicitly requires fictional imagery for such signs, with no real people, names, or events. The prompt excludes people, real events, lettering, and recognizable symbols, consistent with that rule.
- **Depiction specificity:** A shadow enclosing an empty oval is a plausible abstract visual shorthand for disappearance and avoids depicting a victim. However, the M120 concept is specifically kidnapping-suggestive, while this phrase only says “something has disappeared”; it may render as a generic missing-object or warning icon rather than convey the source concept. This needs a clearer but still fictional visual cue for being pulled away / abducted, without depicting a person or adding a narrative event. The phrase “Japanese-style warning road sign” also adds an unsupported national style and may pull the model toward a recognizable real sign design, despite the later exclusion. Recommend “fictional warning sign” without the national qualifier.
- **Orientation / N/A:** A sign panel is an inanimate object, so the anatomy/gaze N/A declaration is correct. Its face is specified at exactly 45° from camera-front toward +x and the front plane and narrow right edge are explicitly visible; the plane angle is concrete.
- **Grid / canvas:** `gridClass 1x2` matches M119–M120 (`docs/monsters.md:222`) and the 1024×1536 px canvas is separately specified. The single post is consistent with “立てる ... 標識” in the grid guidance and is part of the sign object.
- **Style / isolation:** Realistic generated-object treatment follows `docs/assets-policy.md:5`; transparent isolated presentation with no base, cast shadow, or outside frame follows line 13 and `docs/art-direction.md:96`.
- **Placement / TBD:** M120 is explicitly unassigned in dungeon ledger §5.2 (`docs/dungeon-enemies.md:430–437`; also `docs/monsters.md:348`). The prompt correctly adds no location. Abilities and element are not shown.

## Finding and disposition

**Major; clarify before generation.** Core size, object angle, fictional-only safeguard, isolation, and unassigned placement pass. The proposed icon may not communicate the kidnapping-suggestive source concept, and “Japanese-style” introduces avoidable national/style specificity. Use a generic fictional warning sign and refine the pictogram to visibly suggest an abstract pull-away/abduction motif while remaining non-anatomical and containing no person, victim, or real-world symbol. No canonical record was edited and no image was generated.

## Revised prompt re-review — 2026-10-21

### Exact prompt reviewed

> Create one M120 enemy sprite on a transparent 1024×1536 px canvas. Depict one upright fictional warning road sign panel attached to a single post; show the complete panel and post as one object. The sign face is turned exactly 45° from camera-front toward screen-right (+x), with its front plane and narrow right edge both visible. The panel’s single fictional pictogram shows a small empty oval being forcibly pulled sideways by hooked motion strokes into a dark spiral, leaving the oval’s original position empty. Keep the pictogram abstract and non-anatomical: no person, body part, child, victim, or realistic symbol. No lettering, words, numbers, logos, real event, or recognizable real-world road sign design. No road, environment, floor, base, cast shadow, extra sign, frame, or prop. gridClass 1x2. The sign and pictogram have no head, torso, or eyes; anatomy/gaze checks are N/A. Use realistic generated-object rendering. Do not add a location, abilities, element, or story details.

### Verdict

**Pass.** A single panel on a post reads as an upright warning sign and fits the grid guidance “立てる ... 標識.” The 45° plane angle toward +x and visibility of both front plane and narrow right edge are concrete. The oval displaced by hooked motion strokes into a spiral gives a clear forced-removal / abduction cue while remaining abstract, non-anatomical, and free of people, victims, or real-world symbols. The national style qualifier is removed, and the prompt explicitly excludes recognizable real-world road sign designs. No required color or material is specified by the canonical row, and neither is needed to identify the object or its pictogram. `gridClass 1x2` and 1024×1536 px canvas are explicit; isolated realistic-object rendering is consistent with `docs/assets-policy.md`. M120 remains unassigned under dungeon ledger §5.2; the prompt adds no placement. No generation or canonical edit was performed.

## Edit-contract re-review — 2026-10-21

### Exact prompt reviewed

> Edit reference image 1, the unadopted M120 candidate. Preserve the existing post, the exact black pictogram of the empty oval being pulled by hooked strokes into a spiral, the full isolated object, and the 45° +x view with front plane and right thickness visible. Change only the sign panel design: replace the standard yellow triangular warning panel and heavy black inset border with an unmistakably fictional, tall asymmetrical metal panel with one inward notch and uneven clipped corners, in muted charcoal-blue with a narrow pale-metal edge. Keep the symbol centered, with no text, numbers, logo, person, child, victim, or real-event imagery. Keep the entire panel and post silhouette inside the transparent 887×1774 px canvas. Do not add any setting, road, floor, base, shadow, frame, second sign, or props. gridClass 1x2. No head/torso/eyes; anatomy/gaze N/A. Use realistic generated-object rendering. Do not add location, abilities, element, or story details.

### Verdict

**Pass.** This edit directly addresses the raw review blocker: the standard yellow triangle and heavy black inset border are replaced with an explicitly fictional panel silhouette and muted color, while retaining the sign-on-post construction and the already passing pictogram. The requested one notch, clipped corners, charcoal-blue surface, and pale-metal edge sufficiently distinguish the panel from a conventional road-warning sign without adding people, text, or a real-world event. The exact canvas is 887×1774 px, matching the referenced candidate; the full-silhouette instruction prevents cropping. `gridClass 1x2` matches `docs/monsters.md:222`; the 45° +x view and visible front/right thickness are explicit. Transparency, no-human constraints, and realistic isolated-object treatment remain clear. M120 stays unassigned per `docs/dungeon-enemies.md` §5.2. Material/color choices are prompt-level visual means to resolve the previously observed conventional-sign resemblance; the canonical source does not mandate another color or material. No generation or canonical record edit was performed.
