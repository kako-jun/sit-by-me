# M104 raw-image review — retry candidate

- Reviewer: Codex, independent artifact red-team reviewer
- Target: M104 乱暴な自転車
- Stage: `raw-image`
- Verdict: **blocker: near-profile orientation and scale/margins fail; edge alpha residue**
- Canonical source commit: `64bb973967e41475ef55678e9ce7d10dd413dc4a`
- Passed contract reviewed: `docs/reviews/artifact-redteam/20261021-M104-retry-contract-prompt.md`
- Candidate inspected in place: `/home/kako-jun/.codex/generated_images/01a15ccc-868c-7f60-8889-229de4286e8f/exec-fd5cec7e-f602-42cf-93ae-5c2ac99b0257.png`
- Candidate SHA-256: `707087a2af2c2e1ab5ae3fee554df1fb12a9d7cff0156854a745dc06a7b493e2`
- No edit, conversion, move, deletion, or adoption was performed.

## Measurements

- PNG RGBA, 1536×1024 px.
- Alpha range: min `0`, max `0.996078`.
- Corner alpha TL/TR/BL/BR: `0 / 0 / 0 / 0`.
- Alpha-positive bbox: `1511×1024+19+0`; tiny positive alpha reaches the top and bottom canvas edges.
- Core bbox at alpha ≥0.5%: `1195×925+185+58` (77.8% of canvas width, 90.3% of height). At ≥1% alpha, bbox is `1194×924+186+59`.
- At ≥0.5%, margins are 185 px left (12.0%), 156 px right (10.2%), 58 px top (5.7%), and 41 px bottom (4.0%). Contract requires 55–65% width, 45–65% height, and at least 17.5% margin on every side.
- The alpha-positive bounds touching top/bottom correspond to very low-alpha residue; despite transparent corners and numerous zero-alpha exterior samples, the edge prohibition is violated.

## Visual checks

| Check | Evidence | Result |
|---|---|---|
| Count and bicycle parts | Exactly one bicycle. Both complete wheels, frame, handlebar/grips, saddle, pedals and chain are visible. No major part is cropped. | Pass |
| Rider / person | No rider, person or human silhouette appears. The round metal part on the handlebar has no facial features and reads as a bicycle component, not a person. | Pass |
| Front wheel position | Front wheel is on image-right, as required. | Pass |
| Yaw / front and side planes | Both wheels are nearly full circular faces, and the frame is shown broadly side-on. The handlebar assembly does not provide a clear forward-facing plane. This reads as close to the prohibited 90° right profile, not the required 45° view from camera-front 0° to true-right profile 90°. | **Blocker** |
| Scale / margins | Core silhouette spans 77.8%×90.3%, exceeding both maximum scale bounds. Margins are 4.0–12.0%, below 17.5%. | **Blocker** |
| Transparency / background | Alpha=0 exists, all corners are alpha 0, and sampled outside-machine points are alpha 0. The dark radial field in the preview is not an opaque background in those samples; alpha mask follows the bicycle. However, alpha-positive pixels reach top/bottom edges. | **Blocker for edge residue** |
| Outline / fringe / effects | No separate stylized outline or clear chromatic fringe is visible on the actual bicycle silhouette. No ground plane, contact shadow, road, scenery, motion streaks, sound waves, magic or other effect appears in the alpha silhouette. | Pass |

## Findings and disposition

1. **Blocker — orientation:** bicycle wheels and frame remain nearly in a flat side profile; front wheel placement is correct, but the required 45° front/side view is not demonstrated.
2. **Blocker — scale and margins:** the core alpha bbox is substantially larger than contracted and leaves less than 17.5% margin on all sides.
3. **Blocker — edge alpha:** low-alpha pixels touch the top and bottom canvas edges despite the zero-alpha corners.

Do not adopt this candidate. The complete bicycle, front-wheel direction, absence of a rider, and lack of visible scene/effect pass. Candidate and canonical image remain untouched; a corrected raw candidate needs a new independent review.
