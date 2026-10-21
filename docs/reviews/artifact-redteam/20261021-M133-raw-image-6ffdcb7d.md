# M133 raw-image review — 2026-10-21

- Reviewer: Codex, delegated independent reviewer (not the prompt author)
- Target: M133 毒キノコ
- Stage: `raw-image`
- Verdict: **blocker; do not adopt this candidate**
- Canonical base: `64bb973967e41475ef55678e9ce7d10dd413dc4a`
- Exact prompt revision reviewed: `docs/reviews/artifact-redteam/20261021-M133-contract-prompt-actual.md` (short second-call text; this report does not claim the candidate used the earlier longer prompt)
- Candidate inspected in place: `/home/kako-jun/.codex/generated_images/01a15ccc-868c-7f60-8889-229de4286e8f/exec-6ffdcb7d-5665-4b01-ac7e-9ceb517bbe89.png`
- Candidate SHA-256: `e44329ea38102f334bd37ced2fec2b76ca5e36430c8beb239098c463b389ff9b`
- No edit, conversion, adoption, deletion, or move was performed.

## Exact generation prompt reviewed

> Recreate the poisonous mushroom enemy M133 as a photorealistic isolated transparent battle sprite, using the attached existing image only as species and color reference. Preserve exactly four mushrooms: one dominant red cap with three smaller mushrooms around it, pale stems, white cap flecks, and visible airborne spores. Keep the whole group and spores fully inside a compact centered 1x1 composition. Mushrooms have no face, eyes, limbs, or anthropomorphic body; head and torso orientation do not apply. Map location is context only and must not appear. Genuine transparent background. No soil, moss, ground, vegetation, roots, wood, forest, scenery, shadow, poison cloud, colored effects, text, logo, watermark, border, or outline.

## Measurements and pixel evidence

- PNG, 1254×1254 px, sRGBA
- Alpha minimum 0; maximum 1
- Alpha-positive bounding box: `1254x1237+0+17`; the raw bbox touches the canvas edges because of stray/edge pixels
- Top-left, top-right and bottom-left corner alpha are 0. Bottom-right corner `(1253,1253)` is beige (`srgba(217,189,149,0.321569)`), an isolated partial-alpha pixel outside the visible mushroom group.
- The author verified that the actual second imagegen call used `transparent_background: true`. The file itself also has substantial transparent pixels and genuine alpha.

## Checks

| Check | Evidence | Result |
|---|---|---|
| Exact mushroom count and arrangement | Full-resolution view shows four and only four mushroom forms: one dominant red cap at upper center/right, with three smaller mushrooms at mid-left, lower-left, and lower-right. Pale stems and white cap flecks are present. Floating particles have no stems/caps and do not create extra mushrooms. | Pass |
| Spores | Numerous separate pale airborne particles surround the group, matching “visible airborne spores.” No broad cloud is visible. | Pass; particles are prominent, but their requested count/size is unspecified |
| 1x1 and framing | A compact centered group is used for logical `1x1`; the canvas itself is square, but logical occupancy is from source `docs/monsters.md:224` and `docs/dungeon-enemies.md:122`, not inferred from aspect ratio. All four mushrooms and visible particles appear inside the frame; no cap or stem is visibly cut. | Pass, with edge residue below |
| Transparency | The generation call used `transparent_background: true`; alpha minimum is 0 and transparent canvas pixels are present, but one 1/3-opacity beige pixel remains in the bottom-right canvas corner. | Pass for genuine alpha; minor contamination |
| Prohibited scenery, shadow, text, bases, effects | No soil, moss, ground plane, vegetation, roots, wood, forest, scenery, contact shadow, text/logo/watermark, border, or pedestal is visible. No separate toxin cloud or elemental effect is present. | Pass |
| Visual edge artifact | A conspicuous bright yellow/green/red fringe traces the mushroom and spore silhouettes in many locations. It reads as an outline/contour artifact, although the exact prompt explicitly bans any outline and colored effects. The isolated colored corner pixel is consistent with residual fringe/noise. | **Blocker** |
| Crop and canvas edge | Main mushroom silhouettes and spores are visible within canvas margins on inspection. The alpha-positive bbox nevertheless touches the frame due to edge artifacts; the tiny bottom-right pixel is not a mushroom or spore. Edge contact alone is not a failure, but the fringe must be removed. | Pass for visible crop; artifact blocker above |

## Findings and disposition

1. **Blocker — prohibited colored contour/outline artifact.** Bright multicolor fringe surrounds the caps, stems and many airborne particles, directly contradicting “No ... colored effects ... or outline.” Correct by producing a new candidate with clean transparent cutout edges and no contour effect, then require a new raw review.
2. **Minor — isolated alpha residue.** The bottom-right corner contains a beige partial-alpha pixel at `(1253,1253)`. Correct in a new candidate so all four corners are alpha 0.

This candidate is **not eligible for adoption** because of the colored outline artifact. The exact prompt and verified tool argument are recorded separately above. Human adoption remains pending. Candidate was left untouched.
