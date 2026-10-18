# Battle background candidates v2 — independent red-team review

- Date: 2026-10-17
- Reviewer: independent red-team reviewer (not the candidate, prompt, or prior-review author)
- Scope: pixel review of the two unadopted PNG candidates only. This review does not generate, edit, adopt, delete, stage, or otherwise alter either candidate.
- Targets:
  - `sample/battle/backgrounds/teramachi-outdoor-diorama-candidate.png`
  - `sample/battle/backgrounds/stage-e-candidate.png`
- Canonical sources inspected: `.claude/skills/sit-artifact-redteam/SKILL.md`, `.claude/skills/sit-world/SKILL.md`, `.claude/skills/sit-stage-background/SKILL.md`, `docs/art-direction.md`, `docs/roadmap.md`, `docs/assets-policy.md`, sit-by-me Issue #9, `sample/battle/stage-b.json`, and the previous independent review `docs/reviews/artifact-redteam/20261017-battle-background-candidates.md`.
- Raw artifact inspection: both target files were opened with `view_image` at original size. No source prompt, reference, battle-background ledger row/ID, or adoption state was found for either target in the inspected canonical records.

## Shared lifecycle and technical checks

| Check | `teramachi-outdoor-diorama-candidate.png` | `stage-e-candidate.png` |
| --- | --- | --- |
| Asset record, provenance, and lifecycle | **Blocker.** Issue #9 requires a per-area battle-background record (ID, area, 1920×1080/16:9 source dimensions, prompt, reference, output, adoption state). No corresponding record, prompt, reference, or state exists. The file is untracked. | **Blocker.** Same missing required record and provenance; the file is untracked. |
| Exact source dimensions / 16:9 | **Major.** 1672×941: it is not the Issue #9 1920×1080 contract and not exact 16:9 (`1672×9 = 15048`, `941×16 = 15056`). | **Major.** Same 1672×941 non-exact ratio/non-1920×1080 source. |
| Does not overwrite the adopted stage background | **Pass.** Its SHA-256 is `a7e9ad5f…a864`, distinct from tracked `stage-b.png` (`b4baae7e…a33f`); it has its own candidate filename. | **Pass.** Its SHA-256 is `fc3a426c…5d75`, distinct from `stage-b.png`; it has its own candidate filename. |
| People, readable text, logo, watermark | **Pass.** No person, readable text, logo, or watermark is visible in the pixels. | **Pass.** No person, readable text, logo, or watermark is visible in the pixels. |

The missing Issue #9 record is an adoption **blocker**, not permission for this reviewer to recreate provenance. The 1672×941 export is a separate **major** with an evident author-side correction; it must be checked again after an exact 1920×1080 export or other documented exact-ratio source is supplied.

## `teramachi-outdoor-diorama-candidate.png`

| Check | Result | Evidence |
| --- | --- | --- |
| Handmade Teramachi diorama, not a photograph | **Pass.** The exposed cardboard base and torn/cut edges, corrugated lower edge, black paper/sandpaper-like road panels, cotton-like snow, miniature trees, white wall, tiled roof, watercourse, and hand-built bridge make the requested near-top-down tabletop construction unmistakable. |
| Teramachi and winter/snow-country read | **Pass.** Temple wall and gate, tiled roofs, watercourse, snow, slush, and miniature vegetation provide a specific winter temple-town scene rather than a generic road. |
| Issue #9 high boundary / ground majority | **Major.** The far wall/road boundary is approximately 22–24% from the top, leaving roughly 76–78% as road/ground. It is high and ground-dominant, but materially short of Issue #9's approximate 90%-ground target. |
| Issue #9 oblique, repeated parallel depth cues | **Pass.** Multiple long seams between the large dark road panels run diagonally across the image in closely parallel bands; the shallow overhead construction reads as the specified oblique/cabinet-like ground treatment. |
| Battle lanes and command/message-window margin | **Minor.** The broad road gives physical room for enemy-left, party-right, and lower UI. However, the heavy black ground, wet/slushy texture, seams, and debris make acrylic-sprite contrast unproven. Issue #9 and the roadmap still require an actual sample-page overlay in none/acrylic and front/side modes. |

### Findings and disposition

- **Blocker — missing battle-background record/provenance.** Corrective destination: a new Issue #9 battle-background ledger row for this output, initially `blocked`/`needs-review`, containing the source prompt, reference(s), output path, dimensions, area, adoption state, and a link to this review. Do not reconstruct those fields from this review.
- **Major — ground share is below the approximately-90% composition target.** Corrective destination: that non-ready row and the authoring brief; move the far boundary materially upward while retaining the shallow handmade-diorama treatment and diagonal ground bands. A materially recomposed image requires a fresh independent review.
- **Major — source dimensions are not the contract.** Corrective destination: the authoring/export record; supply and re-review an exact 1920×1080 asset.
- **Minor — live sprite/UI readability has not been demonstrated.** Corrective destination: the row's verification evidence; test the required Battle sample modes after the above corrections.

**Final disposition: blocker.** Not eligible for adoption.

## `stage-e-candidate.png`

| Check | Result | Evidence |
| --- | --- | --- |
| Stage-specific upper band: green curtain at about the top 10% | **Pass.** Dark green pleated curtain occupies the upper strip to about 10% of the image; no competing scenery reaches into the battle floor. |
| Child-made cardboard scenery | **Pass.** The snow mountains and castle are visibly separate, roughly cut and hand-painted cardboard flats with uneven painted snow, simple shapes, and exposed cardboard edges; they read as real kindergarten-play props, not a polished fantasy landscape. |
| Issue #9 high boundary / ground majority | **Pass.** The curtain/scenery-to-floor boundary is at about 10–11% from the top. The uncluttered wooden floor occupies roughly 89–90% of the image, matching the issue's intended ground-dominant framing. |
| Issue #9 oblique, repeated parallel depth cues | **Pass.** Numerous wood-floor board seams run diagonally in repeated, near-parallel bands across the battle surface. |
| Enemy-left, party-right, and lower UI margin | **Pass.** Props remain in the narrow top band. The central/lower wooden floor, including both side battle lanes and the bottom command/message area, is clear of foreground set pieces. |
| Live display verification | **Minor.** The pixels leave the specified space, but no actual Battle sample evidence establishes readability with none/acrylic and front/side modes as Issue #9 and the roadmap require. |

### Findings and disposition

- **Blocker — missing battle-background record/provenance.** Corrective destination: a new Issue #9 battle-background ledger row with the required fields and this review link; keep it `blocked`/`needs-review`. The reviewer must not infer the missing prompt or reference.
- **Major — source dimensions are not the contract.** Corrective destination: the authoring/export record; supply and re-review an exact 1920×1080 asset.
- **Minor — live sprite/UI readability has not been demonstrated.** Corrective destination: the row's verification evidence; verify the issue-mandated live sample modes after the record and export are corrected.

**Final disposition: blocker.** The image passes the specified visual-composition and stage-art checks, but is not eligible for adoption until the independent lifecycle blocker and exact-export major are resolved; then it needs a new red-team pass.

## Result summary

| Candidate | Pass | Blocker | Major | Minor | Final disposition |
| --- | --- | --- | --- | --- | --- |
| `teramachi-outdoor-diorama-candidate.png` | non-overwrite; no people/text; handmade diorama; Teramachi/winter read; diagonal ground bands | missing Issue #9 record/provenance | ground share about 76–78%, below approximate 90%; 1672×941 export | live overlay/readability unproven | **blocker** |
| `stage-e-candidate.png` | non-overwrite; no people/text; top ~10% green curtain; rough child cardboard flats; high boundary/ground share; diagonal floorboards; clear battle/UI lanes | missing Issue #9 record/provenance | 1672×941 export | live overlay/readability unproven | **blocker** |

Neither candidate is ready or adopted. This reviewer made no candidate or canonical-record correction; a material correction requires a new independent red-team review.
