# M129 retry3 contract/prompt review — 2026-10-21

- Reviewer: Codex, independent artifact red-team reviewer
- Target: M129 ゴンズイ
- Stage: `contract/prompt`; no image generated
- Canonical source commit: `64bb973967e41475ef55678e9ce7d10dd413dc4a`
- Prompt reviewed: `/tmp/sit-m129-retry3-prompt.txt` (verbatim below)
- Reference inspected: `assets/images/enemies/M129.webp` (640×433 WebP), identity/group/color/anatomy reference only; prompt expressly rejects copying pose, crop and effects.

## Source checks

- `docs/monsters.md` §3-1 M129 row (line 128): five-member group; attribute Water, approved 2026-10-21; weakness TBD; role notes group and poison spines; current image is pending adoption.
- `docs/monsters.md` §4 M129 size row (line 223): `2x1`, with rationale “5匹のゴンズイの群れを横に並べる” (arrange the shoal horizontally).
- `docs/dungeon-enemies.md` M129 encounter row (line 146): `ゴンズイ（2x1）`, beach and shoal/poison-spine provenance, Water element, regular enemy, school/spines pattern.
- `.claude/skills/sit-enemy-sprite/SKILL.md`: exactly 45° yaw from camera-front 0° to true-right profile 90°; show frontal and right-side planes for applicable heads and torsos; record logical gridClass; require the actual tool transparency setting.
- `docs/art-direction.md` §敵素材 (lines 94–95): isolated transparent enemy sprite, facing +x, no text/logos, no stand/ground shadow.
- `docs/assets-policy.md` §敵・召喚獣: transparent cutout and no acrylic treatment.
- `docs/content-registry.md` §§共通運用・プロンプト組み立て規約: use source facts only; no extra element/effect.

## Checklist and finding

| Check | Evidence | Result |
|---|---|---|
| Count and species | Exactly five gonzui, no other fish; source image shows a five-fish shoal. | Pass |
| Intrinsic Water / toxin source | Explicit Water element is metadata only; no water/environment or toxin cloud is depicted. Natural dorsal spines are retained and separate poison effects are excluded, consistent with the source role. | Pass |
| Shape/reference scope | Slender brown striped bodies, pale lateral stripes, whiskers, fins and natural dorsal spines are tied to the inspected image. Its old side profile/crop/effects are explicitly rejected. | Pass |
| Every-fish orientation | For every fish, head and body yaw are set to 45° from defined 0°/90° baselines; snout points camera-front and image-right, both eyes/front snout/near flank must be visible; one-eye side profiles are expressly rejected. | Pass |
| Grid/canvas/crop | 1536×1024 canvas; all five complete with all appendages inside; `gridClass 2x1` matches register. | Pass |
| Layout | Prompt asks for a “staggered formation,” while the M129 size rationale explicitly says to arrange the five-member shoal horizontally. A staggered formation does not guarantee a horizontal shoal or constrain vertical stacking. | **Major** |
| Map/background/tool alpha | Water/beach/map/effects/background are prohibited. Genuine transparent background and `transparent_background=true` are requested; actual generation call must also set the tool argument to `true`. | Pass, conditional on tool argument |

## Exact prompt reviewed

```text
Create one new raw PNG candidate for M129 ゴンズイ; do not alter the canonical image.
Canonical row: "M129 | ゴンズイ | 水辺の生物 | 水辺（章は未定）。内灘 uchinada-beach（一任による決定 2026-10-15、docs/dungeon-enemies.md が正本） | 水（魚。kako-jun 2026-10-21） | 未定 | 未定（群れと毒棘） | 生成済み: assets/images/enemies/M129.webp（採否待ち。5匹の群れ・右向き・透過） | #12". Encounter row: "M129 | ゴンズイ（2x1） | A: beach＝砂浜・波打ち際（EA 1.4）。E: 群れと毒棘 | — （水） | 雑魚 | 群れ・毒棘（L 記述） | 絵あり（採否待ち） | ◎ | 未定 | 未定". Water is the recorded game element; do not depict water, beach, map or effects. Weakness is unspecified; add none.
Use assets/images/enemies/M129.webp only as reference for species and group identity; do not copy its pose, crop or effects. Exactly five complete gonzui fish, no other fish. Keep the slender brown bodies, pale lateral stripes, whiskers, fins and natural dorsal spines shown in the reference. Make a coordinated shoal in a staggered formation; distinguish all five heads and bodies.
For every fish, define head and body yaw with camera-front = 0° and true image-right side profile = 90°; target exactly 45° toward image-right. Make each snout point toward the camera and image-right at once. Show both eyes on every fish head, the frontal face of each snout, and the near flank of each body. This visible evidence is required; do not use one-eye-only side profiles. Use a 1536×1024 landscape canvas. All five bodies, heads, tails, fins, whiskers and spines are complete and inside it; no part is cropped by the image boundary. Logical gridClass 2x1.
Photorealistic natural fish. Neutral white lighting. Isolated transparent background, set transparent_background=true. Use natural antialiased edges only, no colored outline, fringe, glow, halo, shadow or scenery. No text, logo, watermark, border, pedestal, ground, water, waves, beach, toxin cloud, poison effect or extra objects.
```

## Disposition

**Major; keep non-ready and do not generate from this version.** Replace “staggered formation” with a concrete horizontal shoal arrangement that matches the M129 `2x1` rationale (for example, five distinguishable fish arranged left-to-right in one horizontal group, with only limited vertical staggering that does not make the group read as a vertical stack). Keep all-five 45° evidence and 1536×1024 framing unchanged. Set actual tool argument `transparent_background: true` during generation. No asset was changed by this review.

## Re-review of revised prompt — 2026-10-21

Revised prompt reviewed: `/tmp/sit-m129-retry3-prompt.txt` as currently present at re-review. The author replaced “staggered formation” with “all five fish in one shallow horizontal shoal extending left-to-right, as a 2x1 battle formation.” This now directly matches the M129 size rationale at `docs/monsters.md` §4, line 223. The prompt retains exactly five gonzui, metadata-only Water, reference-grounded markings and fins, every fish's defined 45° yaw and required visible face/near-flank evidence, 1536×1024 landscape canvas, full uncropped subjects, 2x1, and no map/background/water/effects. The imagegen tool argument still must be set to `transparent_background: true` at generation.

**Revised disposition: PASS for `contract/prompt` stage only.** The earlier major layout finding is retained as historical context and superseded by this pass for the current revision. Raw-image review remains required for actual five-fish count, each fish's orientation, alpha, cropping and exclusions. No image was generated or changed by this review.

### Exact revised prompt

```text
Create one new raw PNG candidate for M129 ゴンズイ; do not alter the canonical image.
Canonical row: "M129 | ゴンズイ | 水辺の生物 | 水辺（章は未定）。内灘 uchinada-beach（一任による決定 2026-10-15、docs/dungeon-enemies.md が正本） | 水（魚。kako-jun 2026-10-21） | 未定 | 未定（群れと毒棘） | 生成済み: assets/images/enemies/M129.webp（採否待ち。5匹の群れ・右向き・透過） | #12". Encounter row: "M129 | ゴンズイ（2x1） | A: beach＝砂浜・波打ち際（EA 1.4）。E: 群れと毒棘 | — （水） | 雑魚 | 群れ・毒棘（L 記述） | 絵あり（採否待ち） | ◎ | 未定 | 未定". Water is the recorded game element; do not depict water, beach, map or effects. Weakness is unspecified; add none.
Use assets/images/enemies/M129.webp only as reference for species and group identity; do not copy its pose, crop or effects. Exactly five complete gonzui fish, no other fish. Keep the slender brown bodies, pale lateral stripes, whiskers, fins and natural dorsal spines shown in the reference. Arrange all five fish in one shallow horizontal shoal extending left-to-right, as a 2x1 battle formation; distinguish all five heads and bodies.
For every fish, define head and body yaw with camera-front = 0° and true image-right side profile = 90°; target exactly 45° toward image-right. Make each snout point toward the camera and image-right at once. Show both eyes on every fish head, the frontal face of each snout, and the near flank of each body. This visible evidence is required; do not use one-eye-only side profiles. Use a 1536×1024 landscape canvas. All five bodies, heads, tails, fins, whiskers and spines are complete and inside it; no part is cropped by the image boundary. Logical gridClass 2x1.
Photorealistic natural fish. Neutral white lighting. Isolated transparent background, set transparent_background=true. Use natural antialiased edges only, no colored outline, fringe, glow, halo, shadow or scenery. No text, logo, watermark, border, pedestal, ground, water, waves, beach, toxin cloud, poison effect or extra objects.
```
