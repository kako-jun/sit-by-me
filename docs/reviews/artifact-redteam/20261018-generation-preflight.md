# Generation preflight independent review — 2026-10-18

Reviewer: Codex independent reviewer (`preflight_review`), not an author of the reviewed skills, contracts, prompts, images, or masks. Stage: `contract/prompt` and read-only forward tests. Initial disposition: **changes required; no image generation or adoption approved**. Image organization under #68 is being edited concurrently; temporary filename changes are outside this initial review.

## Final recheck after author corrections

Disposition: **pass for the reviewed skill/document workflow changes only**. Both initial findings below are resolved: `docs/content-registry.md:9`, `docs/map-asset-registry.md:25,29` and `docs/map-topology.md:71` now distinguish independent input-contract eligibility from final image/mask adoption; `sit-battle-background/SKILL.md:20` now scopes theatre materials to theatre and derives outdoor materials from its MAP. No unresolved must-fix finding remains in this change scope.

The production bundle's source rows were compared again after #68 path changes and still match their canonical files verbatim. Its lines 108–111 now scope the exterior reference to order/containment and explicitly permit one 1920×1080 prompt request followed by actual-file measurement; no unsupported API guarantee is required. The next executable authoring action is to assemble the complete outgoing common-exterior prompt and current reference pixels/roles, perform its independent input review, then generate one reference if that review passes. The current BLOCKED label must not be read as permission to skip that review. This turn prioritizes #68 organization and does not execute generation.

Earlier measured old-file paths and findings below are historical evidence from the initial review; #68's migration manifest maps or tombstones them. No new image quality, MAP ready, mask completeness, runtime adoption, or all-sixteen cutover pass is asserted. The separate [asset organization review](20261018-asset-organization.md) covers the completed relocation and deletion checks.

## Independent expectations and sources

Read #51 and #60 titles, complete bodies and all comments directly with `gh issue view`, before assessing author conclusions. #51 requires all E01–E13/F01–F03 rebuilt, exactly 1920×1080, old candidates/masks/passes excluded, and all sixteen accepted before a single runtime cutover. #60 requires F01 central, E12 east, F02 west, internal-only travel through F01, no residence/playroom direct transition, and no new exterior entrance from E11 to those interiors. The October 18 plan permits preparing and reviewing a common exterior reference before individual interiors and masks.

Canonical records read directly: `docs/content-registry.md`, `docs/map-asset-registry.md`, `docs/map-specifications.md`, `docs/map-topology.md`, `docs/map-contract-checklist.md`, `docs/teramachi-rebuild-candidates.md`, `docs/map-reference-research.md`, `docs/art-direction.md`, `docs/assets-policy.md`, `docs/production/20261018-teramachi-preflight.md`; all seven changed `sit-*` image/mask/review skills. Read `sit-artifact-redteam` and `skill-creator` instructions completely. Compared changed files to HEAD. The source-table rows copied into the production bundle were checked programmatically against their stated source files: all copied rows matched exactly at this review snapshot.

## Actionable findings

1. **Major — generation/adoption state contradiction remains in canonical entry points.** `docs/content-registry.md:9` prohibits generation unless `ready`; `docs/map-asset-registry.md:25` requires masks/reviews before considering `ready`, while line 29 allows generation only for `ready`. `docs/map-topology.md:71` also requires ready before image generation. These contradict the newly explicit phase distinction in `sit-field-background/SKILL.md:28`, and retain the first-generation circular dependency. Corrective destination: align those canonical generation gates with reviewed prompt/contract eligibility and final adoption readiness. Do not fix this by marking an ungenerated MAP ready. Disposition: unresolved at initial review; independent recheck required.

2. **Major — outdoor battle generation still inherits compulsory theatre materials.** `sit-battle-background/SKILL.md:20` requires stage floor, scenery and curtain materials without a theatre-only condition, whereas line 44 prohibits stage flooring/scenery/curtains outdoors. A realistic outdoor generation cannot satisfy both clauses. Corrective destination: scope theatre construction declarations to theatre, select outdoor construction materials from its actual field contract/reference, and retain measured material evidence requirements. Disposition: handed to skill author; independent recheck required.

## Forward tests and concrete results

### A. Resume rebuilding, repair deficient skills first, record the Issue before work

The concrete next authoring target is the **common exterior reference input**, not a replacement E11 background, interior, mask, or runtime cutover. The production bundle preserves #60 verbatim and has the five relevant MAP rows, incoming E04→E11 connection and reciprocal door records. The corrected v2 topology removes E12↔F02 and E11↔E12; E01↔E11 remains an outdoor garden/courtyard gate, not a new route into F02. F02's existing `door-west` ID does not prove its physical arrival bearing; that remains an explicitly deferred interior question. The original topology's old proposals are explicitly marked historic and cannot override current v2.

The draft input retains roof/exterior surfaces, forbids cutaways/external passages and contains named materials and processing methods. It explicitly excludes runtime link coordinates, interior corridor shape/width and masks from this overview's claims. Missing future runtime measurements **are not findings against this overview**.

Viewed the actual prior `sample/field/rebuild/teramachi-temple-compound-master-plan-v2-connected.png`: at 1254×1254, central hall interior is exposed around x450–770/y210–390; western playroom furniture around x100–390/y520–780 and eastern residence rooms around x930–1180/y300–510 are visible through removed roofs. This is a failed exterior architecture reference regardless of its “connected” filename. It cannot serve as the next architectural reference. A material-only reference must be explicitly assigned that role after its pixels are inspected; a prompt saying to ignore bad architecture cannot promote it into a valid architectural reference.

The outgoing draft is not yet executable as an approved generation: the production table explicitly leaves exterior-reference scope/shape treatment and actual tool size capability unresolved (`20261018-teramachi-preflight.md:108,111`), alongside finding 1. The available image generation tool schema has no explicit pixel-size argument; a 1920×1080 prompt is not a guarantee. **An API guarantee is not a prerequisite:** one explicitly requested 1920×1080 attempt followed by actual-file measurement and rejection of mismatches is a valid route. Correct the production statement so lack of a dedicated size parameter does not falsely make this route impossible; never resize a failed output into compliance. No paid generation was attempted. There is no need to ask again about already decided east/central/west placement. The latest user-directed #68 organization takes priority before the generation attempt.

### B. M001 transparency/extent rejection

Measured the actual `sample/battle/enemy-dragon.png` with Pillow, read-only: 640×564; converted RGBA alpha extrema 0–255; alpha>0 bbox `(0,0,640,564)`; width and height occupy 100% of canvas. This is **not an all-opaque image**, but it fails the current sprite canvas and 92–96% extent contract. Alpha=0 existence alone cannot pass it. The revised enemy gate explicitly requires measured dimensions, alpha=0 existence, alpha>0 bbox and per-plane visual verification, so this test correctly rejects adoption. A hypothetical RGBA image whose alpha is uniformly 255 also rejects because alpha=0 is absent. No candidate was changed or generated.

### C. E01 raw-image pass without masks

Measured actual `sample/field/rebuild/E01-teramachi-kindergarten-16x9-candidate.png`: 1672×941; opaque alpha 255. Its filename does not prove 1920×1080. It fails #51's raw dimension gate and cannot advance to masks or inherit an old pass.

For the explicitly counterfactual scenario of a **new exact-size E01 candidate with an independent raw-image pass and resolved connection/era contract**, `sit-field-mask` now permits mask authoring before final MAP ready; `sit-artifact-redteam` limits that pass to raw-image stage. Missing masks remain pending, final ready/adoption remains forbidden, and the sixteen-image batch cutover remains later. This is the correct phase-specific next step. Finding 1 prevents declaring the overall canonical workflow consistent yet.

## Checks passed at this phase

- The rebuilding candidate table excludes all sixteen current old candidates; old progress is historic rather than carried-forward acceptance.
- Current #60 topology is represented in specification, candidate table and checklist; no new direct residence/playroom link is permitted.
- Exact 1920×1080 actual-file inspection, independent complete-prompt review before paid generation, actual reference pixels/roles, independent raw-image review, then mask/links review are required by revised field/review skills.
- Transparent sprite checks no longer accept an RGBA format label as alpha evidence.
- Failure provenance may survive as prompt/reference/measurement/hash/reason plus recoverable Git source commit when user-authorized failed binaries are removed; permanent duplicate blobs are not required.
- Raw-image and prompt passes do not auto-adopt assets. No image quality pass is claimed by this paper/workflow review.

Pending: author corrections, renewed logic check, #68 completed path/runtime integrity review, actual supported-size route and complete outgoing prompt/reference review. The reviewer has not repaired author files, generated images, edited masks, adopted assets or written to Issues.
