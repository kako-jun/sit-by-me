# Battle background candidates — independent red-team review

- Date: 2026-10-17
- Reviewer: independent red-team reviewer (not the candidate, prompt, or prior-review author)
- Scope: unadopted raw PNG candidates only. This review neither generates, edits, adopts, nor deletes assets.
- Targets:
  - `sample/battle/backgrounds/teramachi-outdoor-candidate.png`
  - `sample/battle/backgrounds/stage-d-candidate.png`
- Canonical sources inspected: `.claude/skills/sit-artifact-redteam/SKILL.md`, `.claude/skills/sit-world/SKILL.md`, `.claude/skills/sit-stage-background/SKILL.md`, `docs/assets-policy.md`, `docs/art-direction.md`, `docs/roadmap.md`, sit-by-me Issue #9, `sample/battle/README.md`, and `sample/battle/stage-b.json`.
- Pixel inspection: both targets and the adopted comparison asset `sample/battle/backgrounds/stage-b.png` were opened at original size with `view_image`.

## Register and lifecycle gate — blocker for both

Issue #9 requires one battle-background record per area, with an ID such as `B001-teramachi-snow`, area, 1920×1080/16:9 source dimensions, prompt, reference, output, and adoption state. Neither target has a matching ID or ledger row, prompt, reference, or adoption state in the inspected canonical records. Both files are untracked candidates; `git ls-files` contains neither. The field-map registry cannot supply this record because it is a different asset class, and no battle-background registry exists.

**Disposition: blocker.** Before any adoption decision, create the Issue #9 battle-background ledger and add one non-ready row for each target with every required field, including this review link. Keep the rows `blocked`/`needs-review`; the missing authoring provenance must not be reconstructed by this reviewer.

## Shared technical checks

| Check | `teramachi-outdoor-candidate.png` | `stage-d-candidate.png` |
|---|---|---|
| Raw dimensions / 16:9 | 1672×941. This is not exact 16:9 (1672×9 = 15048; 941×16 = 15056) and is not the Issue #9 contract of 1920×1080. **Major.** | 1672×941, with the same non-exact ratio and non-1920×1080 source. **Major.** |
| Candidate does not overwrite an approved asset | **Pass.** It is untracked and has SHA-256 `008c9132…02231`, distinct from tracked approved `stage-b.png` (`b4baae7e…a33f`). | **Pass.** It is untracked and has SHA-256 `548e8e80…dfbc09`, distinct from tracked approved `stage-b.png`. |
| People / readable text / logos / watermark | **Pass.** No people, readable text, logo, or watermark found in the pixels. | **Pass.** No people, readable text, logo, or watermark found in the pixels. The painted backdrop contains no readable lettering. |

The dimensions issue is a **major**, not an independent adoption block: it has an obvious correction (an exact 1920×1080 export or a documented exact-ratio source) but must be verified again after correction. It does not remove either candidate's separate blocker.

## `teramachi-outdoor-candidate.png`

### Checks and evidence

| Check | Result | Evidence |
|---|---|---|
| Issue #9 composition: high horizon / ground dominates | Pass | The wall/road boundary sits around the upper fifth of the image; wet, snowy roadway occupies roughly four fifths. |
| Issue #9 composition: many diagonal, parallel depth cues | Major | Pavement seams and slush tracks provide some shallow diagonals, but they largely converge or run nearly horizontal. The image does not clearly read as the requested cabinet-like oblique projection with repeated diagonal parallels. |
| Character, enemy, and UI safety | Minor | The broad roadway leaves physical space for left enemy/right party placement and the lower UI; no large foreground prop occupies those zones. However, high-frequency wet asphalt, reflections, seams, and snow lumps reduce contrast behind acrylic sprites. A live battle overlay is still required by the roadmap before usability can be signed off. |
| Teramachi / winter specificity | Pass | Snow, long white plaster wall over stone base, tiled roofs, temple gate, water channel, and red-white snow poles directly communicate the required snow-country temple-town vocabulary. |
| Background visual language | Blocker | It reads as a photographic street scene. `assets-policy.md` and `art-direction.md` require backgrounds to visibly be handmade, deformed tabletop dioramas with material scale, shallow/top-down construction, and non-photographic texture. This candidate has photographic snow, asphalt, masonry, trees, and perspective. |

### Findings and disposition

- **Blocker — wrong required visual medium.** Corrective destination: the future Issue #9 ledger row for this candidate must remain `blocked`; return a replacement brief to the battle-background authoring workflow that requires a handmade tabletop-diorama rendering, shallow visual depth, and the same Teramachi landmarks. A new candidate requires a new red-team pass.
- **Major — diagonal-parallel construction is too weak.** Corrective destination: the same non-ready ledger row and its prompt/brief; specify repeated, clearly visible parallel oblique road/ground cues rather than a natural photographic perspective.
- **Minor — sprite contrast remains unproven.** Corrective destination: the row's verification field; test enemy-left/party-right plus the command/message windows in the live sample after the material and composition corrections.

**Final disposition: blocker.** It is not eligible for adoption.

## `stage-d-candidate.png`

### Checks and evidence

| Check | Result | Evidence |
|---|---|---|
| Stage contract: real kindergarten play stage | Pass | Green curtain, warm wooden stage, childlike hand-painted cardboard snow mountains/castle/trees, and wings with a ladder and boxes visibly form a real stage. The ladder/props are kept at the far right edge as allowed by `sit-stage-background`. |
| Issue #9 composition: high horizon / ground dominates | Blocker | The backdrop-to-floor boundary is around 57–61% down the image, so the floor is only about the lower 39–43%, not the approximately 90% ground-side composition required by Issue #9. |
| Issue #9 composition: diagonal, parallel depth cues | Pass | The floorboards create repeated diagonal perspective lines across the available floor. This does not cure the failed ground-area requirement. |
| Character, enemy, and UI safety | Pass | The central and lower floor is intentionally open. The enemy-left and party-right floor zones are unobstructed; the command/message-window region at the lower edge has no foreground stage prop. The right-side ladder and crates remain at the edge rather than occupying the battle lanes. |
| Readable text / people / logos / watermark | Pass | No people or readable text, logo, or watermark is visible. |

### Findings and disposition

- **Blocker — battle-wide Issue #9 composition is not met.** Corrective destination: the future Issue #9 ledger row for the stage candidate and its authoring brief. Do not treat the stage-specific skill's otherwise-satisfied safety requirements as an exemption from the Issue #9 high-horizon / approximately-90%-ground rule. A materially recomposed candidate needs a new red-team pass.

**Final disposition: blocker.** It is not eligible for adoption.

## Result summary

| Candidate | Pass | Blocker | Major | Minor | Final disposition |
|---|---:|---:|---:|---:|---|
| `teramachi-outdoor-candidate.png` | Teramachi read; high horizon/ground; no people/text; no overwrite | provenance/ledger missing; photographic instead of handmade diorama | non-exact ratio/dimensions; weak oblique parallel construction | live sprite-contrast evidence absent | **blocker** |
| `stage-d-candidate.png` | stage realism; diagonal floor cues; safety margins; no people/text; no overwrite | provenance/ledger missing; floor only about 40%, not Issue #9's ground-dominant composition | non-exact ratio/dimensions | none | **blocker** |

No candidate is marked ready, adopted, or pass. The common provenance blocker and each candidate-specific blocker must be resolved by the authoring workflow before a fresh independent review.
