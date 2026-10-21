# S006 第2形態 raw-image review

- Reviewer: independent red-team reviewer (not the specification, prompt, image, or prior-review author)
- Stage: `raw-image`
- Target: S006 第2形態 `S006-awakening.webp` 候補（未採用PNG）
- Disposition: **pass** for this raw-image stage. This does not adopt the candidate or verify WebP conversion/runtime behavior.

## Artifact inspected

- Candidate: `/home/kako-jun/.codex/generated_images/01a15d7a-cc03-7c12-b781-c681f515408c/exec-a7817c61-9f47-42e7-87ee-ef5fa318b008.png`
- SHA-256: `05afc78b2c8344de617ab8b86d3cfa7152cf1be3196766b064c9501e18c19d94`
- Dimensions/mode: 1536×1024, RGBA sRGB.
- Alpha: min=0, max=254/255 (0.996078). Corner alpha values: TL=0, TR=0, BL=0, BR=1/255. `alpha > 0` bbox is the full 1536×1024 canvas because of sparse edge pixels. On each outermost edge, every nonzero alpha value is at most 1/255; counts are top=17, bottom=77, left=87, right=1 pixels. These edge traces are not visibly clipping the cloud or gold motifs at original size and, under the user's explicit tolerance, do not block this review.
- Generation inputs: complete prompt in Issue #141 comment [6312135944](https://github.com/kako-jun/sit-by-me/issues/141#issuecomment-6312135944); reference image and `referenced_image_paths` / `transparent_background: true` recorded in [6312163197](https://github.com/kako-jun/sit-by-me/issues/141#issuecomment-6312163197); candidate measurements in [6312237622](https://github.com/kako-jun/sit-by-me/issues/141#issuecomment-6312237622).
- Reference actually inspected: `assets/images/summons/S006-cloud.webp` (1536×1024 RGBA). It depicts a single gray nighttime cumulonimbus mass with layered cloud structure and broad crown; the prompt limits its use to carrying forward some of that mass/silhouette.

## Canonical sources inspected

- `.claude/skills/sit-artifact-redteam/SKILL.md`
- `.claude/skills/sit-summon-sprite/SKILL.md`
- `docs/content-registry.md` summon workflow, lines 21 and 33–37
- `docs/monsters.md` S006 row (line 88) and grid rows (249–255)
- `docs/story.md` thunder summon role and M004→M005 sequence (lines 93–95)
- `docs/art-direction.md` S006 four-stage description (line 130)
- `docs/assets-policy.md` summon master treatment (lines 5, 13)
- Issue #141, especially the updated stage-two decision and complete prompt/tool input comments listed above
- Issue #78: M005/S006 are “竜” echoing M001 in shape and orange color; M003 remains a separate “龍” line

## Checks and evidence

- **Subject / transition from stage one — pass.** The candidate retains a large mass of layered gray cloud. The visible opening is a single large, roughly circular void with an uneven cloud edge and a deep star-filled cosmic interior; it does not read as a clean geometric portal with a visible enclosing wall or bottom. Gray remains the dominant cloud color while yellow/gold first appears around the opening and in the new decorative motifs. Orange is not the dominant color.
- **Stage-two-only exclusions — pass.** No dragon/animal silhouette, skull, or dragon-shaped lightning is visible. Those belong to later stages. The dark interior remains a cosmic expanse; it is not shaped into a face.
- **Gold-leaf-like abstract clouds — pass.** Abstract, curling gold forms surround and follow the storm as a decorative motif. The stage-one reference itself has no such motifs; they are newly introduced here as required for stages two through four.
- **Transparency / framing — pass with recorded edge trace.** The file is RGBA, the minimum alpha is zero, and three corners are fully transparent; the fourth contains one alpha value of 1/255. All nonzero alpha pixels on the four canvas edges are at most 1/255. At original size these sparse traces are barely visible and do not look like a backdrop panel or clipped subject. The sprite remains legible and fully visible. The display preview's dark/gold appearance was not used as transparency evidence; alpha was measured from the file.
- **Summon treatment — pass.** No border, base/stand, or ground shadow is visible. No face or eyes are present, so the 45-degree face-plane check is not applicable.
- **Declared grid — pass.** `docs/monsters.md` declares S006 stage two as `2x3` (lines 249–250). As the summon skill specifies, this is a combat-cell class, not a pixel aspect-ratio requirement; the 1536×1024 canvas is recorded only.
- **Lifecycle — pending.** Candidate is not adopted. This review permits the authoring workflow to present it for the user's visual adoption decision. WebP conversion, alpha equivalence, and runtime verification are later checks.

## Findings

No blocker, major, or minor discrepancy found for this exact raw image against the current stage-two contract. Edge contact is recorded above; measured edge alpha is at most 1/255 and is not visibly consequential at original size. The candidate remains unadopted pending the user's decision.
