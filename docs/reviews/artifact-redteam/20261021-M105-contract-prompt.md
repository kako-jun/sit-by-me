# M105 contract/prompt review — 2026-10-21

- Reviewer: Codex, independent artifact red-team reviewer
- Target: M105 乱暴な車
- Stage: `contract/prompt`; no image generated
- Canonical source commit: `64bb973967e41475ef55678e9ce7d10dd413dc4a`
- Prompt reviewed: `/tmp/sit-m105-prompt.txt` (verbatim below)
- Existing source image: none identified; M105 canonical row says `仕様のみ`. No reference image is supplied or needed for this prompt.

## Source checks

- `docs/monsters.md` §3-1, M105 row (line 104): M105 is an aggressive car in the “traffic and noise” class; attribute, weakness/resistance, skill and sprite are unspecified; it explicitly says no driver.
- `docs/monsters.md` §4 (lines 193–224): M105 is assigned `2x1`, with the paired row describing the group as unoccupied car and loud motorcycle.
- `docs/dungeon-enemies.md` M105 row (line 108): Kōrinbō crossroads provenance, regular enemy, current image status “仕様のみ”; no visual appearance specifics beyond the car identity and its no-driver requirement.
- `.claude/skills/sit-enemy-sprite/SKILL.md`: 45° is defined from camera-front 0° to true-right profile 90°; vehicles without head/torso use N/A for those anatomy checks; record `gridClass`, request actual tool transparency, omit outline/base/contact shadow.
- `docs/art-direction.md` §交通と騒音 (lines 72–75) and §敵素材 (lines 94–95): the car is a traffic/noise enemy, driverless, isolated, facing +x, with no logo/text.
- `docs/assets-policy.md` §敵・召喚獣: transparent isolated asset, no acrylic frame, pedestal or contact shadow.
- `docs/content-registry.md` §§共通運用・プロンプト組み立て規約: unspecified fields must not be filled with invented attributes or effects.

## Checklist and findings

| Check | Evidence | Result |
|---|---|---|
| Identity/count/occupant | One car; no driver or people. This matches M105 source and art direction. | Pass |
| Vehicle anatomy | Four wheels, body, windows, doors, grille and headlights are ordinary car anatomy consistent with the source category. | Pass |
| Map provenance | Kōrinbō/crossroads is labeled context only; road, signage, restaurant and scenery are excluded. | Pass |
| Attribute/TBD | Prompt explicitly excludes any attribute, weakness/resistance or skill additions; no elemental/status effect is added. | Pass |
| Orientation | Camera-front 0°, true-right profile 90°, target yaw 45°, front pointing +x and toward camera, front and image-facing side planes specified. The subject has no head/torso, so those anatomy-plane checks are N/A. | Pass |
| Logical grid | Explicit `gridClass 2x1`, consistent with the canonical size table. | Pass |
| Alpha and exclusions | Genuine transparency and `transparent_background=true` are specified; prompt excludes text, logo, background, ground, effects, outline, fringe, shadow, base and extra subjects. The actual generation call must pass the imagegen tool argument `transparent_background: true`. | Pass, conditional on tool argument |
| Canvas/scale contract | No pixel canvas dimensions or measurable complete-silhouette bound are specified. The skill's unique-interpretation gate requires canvas px dimensions in generation input; `full vehicle visible within canvas` alone leaves the target canvas unspecified. | **Major** |
| Unsupported pose wording | “Forward-leaning” could request an invented pitch/tilt separate from the specified 45° yaw. The threatening presentation is already achieved by the specified perspective and the source name does not establish that the car is physically tilted. | **Major** |

## Exact prompt reviewed

```text
Create one new raw PNG battle sprite candidate for M105 乱暴な車; do not alter any canonical asset.
Canonical row: "M105 | 乱暴な車 | 交通と騒音 | 香林坊 korinbo-crossroads（十字）（一任による決定 2026-10-15、docs/dungeon-enemies.md が正本） | 未定 | 未定 | 未定 | 仕様のみ（運転者は描かない） | 同上". Encounter row: "M105 | 乱暴な車 | A: korinbo-crossroads＝繁華街の交差点（EA 1.2） | — | 雑魚 | 未定 | 仕様のみ | ○ | 未定 | 未定（ワープ先は香林坊のレストラン。DC 60 行。到達は可）". Encounter/location are context only: depict no street, intersection, signage, or restaurant. Attribute, weakness, resistance and skills are unspecified; add none.
Exactly one unoccupied ordinary passenger car, with four wheels, body, windows, doors, grille and headlights. No driver or people. It should feel threatening through its forward-leaning 3/4 presentation alone; do not add damage, weapons, spikes, faces, or motion effects. Front points toward image-right and toward the camera at 45° between camera-front 0° and true-right side profile 90°. Clearly show the front face and the image-facing side plane; do not show a pure side profile. Logical gridClass 2x1.
Photorealistic natural object rendering, neutral clear light. Full vehicle visible within canvas. Genuine transparent background; set transparent_background=true. Natural antialiased silhouette only: no glow, halo, outline, fringe, shadow or background. No text, letters, logos, license plate text, watermark, pedestal, road, ground, scenery, traffic, additional vehicle or object.
```

## Disposition

**Historical disposition for first prompt version:** Major; it omitted pixel dimensions and used unsupported “forward-leaning” wording.

## Re-review of revised prompt — 2026-10-21

Revised prompt reviewed: `/tmp/sit-m105-prompt.txt` as currently present at re-review. The author removed “forward-leaning,” specifies a 1536×1024 canvas and requires the entire vehicle to remain uncropped. The 45° front/right view, single unoccupied car, 2x1 grid, map provenance-only treatment, TBD exclusions and transparent-background requirement remain. The car has no head/torso, so those anatomy-specific checks are N/A. No source image exists because M105 is still `仕様のみ`; the ordinary passenger-car body details are generic car anatomy, not additional named accessories or effects.

**Revised disposition: PASS for `contract/prompt` stage only.** The 1536×1024 canvas and fully-inside/no-crop instruction resolve the earlier canvas ambiguity; the unsupported pitch/tilt request is gone. At generation, use the actual imagegen argument `transparent_background: true`. Raw-image review must still inspect the 45° planes, full vehicle, alpha and prohibited elements. The earlier major finding is retained as history and superseded for this revision. No canonical asset was changed.

### Exact revised prompt

```text
Create one new raw PNG battle sprite candidate for M105 乱暴な車; do not alter any canonical asset.
Canonical row: "M105 | 乱暴な車 | 交通と騒音 | 香林坊 korinbo-crossroads（十字）（一任による決定 2026-10-15、docs/dungeon-enemies.md が正本） | 未定 | 未定 | 未定 | 仕様のみ（運転者は描かない） | 同上". Encounter row: "M105 | 乱暴な車 | A: korinbo-crossroads＝繁華街の交差点（EA 1.2） | — | 雑魚 | 未定 | 仕様のみ | ○ | 未定 | 未定（ワープ先は香林坊のレストラン。DC 60 行。到達は可）". Encounter/location are context only: depict no street, intersection, signage, or restaurant. Attribute, weakness, resistance and skills are unspecified; add none.
Exactly one unoccupied ordinary passenger car, with four wheels, body, windows, doors, grille and headlights. No driver or people. Do not add damage, weapons, spikes, faces, or motion effects. Front points toward image-right and toward the camera at 45° between camera-front 0° and true-right side profile 90°. Clearly show the front face and the image-facing side plane; do not show a pure side profile. Logical gridClass 2x1.
Photorealistic natural object rendering, neutral clear light. Use a 1536×1024 landscape canvas. Show the entire vehicle inside it; no part is cropped by the image boundary. Genuine transparent background; set transparent_background=true. Natural antialiased silhouette only: no glow, halo, outline, fringe, shadow or background. No text, letters, logos, license plate text, watermark, pedestal, road, ground, scenery, traffic, additional vehicle or object.
```
