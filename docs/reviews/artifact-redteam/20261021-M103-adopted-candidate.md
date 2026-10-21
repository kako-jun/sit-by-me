# M103 adopted candidate review — 2026-10-21

- Candidate: `exec-d2e1c751-ef98-414b-872d-55f168debdd5.png`
- User decision: adopted by kako-jun on 2026-10-21.
- Prompt contract: pass. Target is one unmanned firearm, logical gridClass `2x1`, 1536×1024 px canvas; the firearm's body and barrel use a 45° oblique view, with front and right-side planes visible. The existing image was identity-only reference. No map scenery, person, or extra weapon was requested.
- Raw review: pass for contents, oblique orientation, alpha transparency, and framing.

## Raw checks

| Check | Result |
|---|---|
| Dimensions and channels | 1536×1024, RGBA |
| Alpha range | 0 to 0.996078 |
| Alpha-positive bounding box | 1513×983 at (11,9); faint anti-aliased edge pixels extend this box, while the >1% alpha silhouette is 1502×784 at (19,142) |
| Canvas perimeter | Four corners and all one-pixel edge strips have alpha 0 |
| Detached background samples | Alpha 0 at (10,500), (768,100), (768,900), (200,500), (1000,700), and (1500,500) |
| Subject | One firearm, no person/operator, no text/logo/extra object; muzzle opening and near-side/top planes visible; not a pure profile |
| Crop | Full firearm visible; silhouette margins approximately 19 px left and 15 px right |

The alpha-only difference between the PNG source and adopted WebP (`-quality 85`) is AE `0`.

The raw reviewer noted that the RGB channels contain a radial-looking color around the object, but those pixels are fully alpha-transparent. This record documents the user-adopted candidate and does not change encounter placement data.
