# M129 retry 2 contract/prompt review — 2026-10-21

- Reviewer: Codex, independent artifact red-team reviewer
- Target: M129 ゴンズイ
- Stage: `contract/prompt` only; no image generated
- Canonical source commit: `64bb973967e41475ef55678e9ce7d10dd413dc4a`
- Prompt reviewed: `/tmp/sit-m129-retry2-prompt.txt` (exact text below)
- Visual reference inspected: `assets/images/enemies/M129.webp` (640×433 WebP; SHA-256 `8f4259c43b69b46dc937d64037121a344b17070347fd63a0aadef5ff6b6d198f`), species/group identity reference only; old pose/crop/edge artifacts excluded
- Previous retry report preserved: `docs/reviews/artifact-redteam/20261021-M129-retry-contract-prompt.md` (major finding: false `freshwater` descriptor)

## Sources checked

- `docs/content-registry.md` lines 5–11, 20: derive the prompt from the canonical enemy row and policy/skill, preserve relevant source fields, and do not invent appearance or mechanics.
- `docs/monsters.md` line 128: M129 is ゴンズイ, at the Uchinatā shoreline; its intrinsic element is Water; weakness is TBD; role detail is `未定（群れと毒棘）`; current five-fish image remains pending adoption.
- `docs/monsters.md` line 223: current M129 logical occupancy is `2x1`, with five gonzui arranged horizontally.
- `docs/dungeon-enemies.md` line 146: encounter row states `2x1`, beach/shoreline provenance, group and venomous spines, Water, and regular-enemy role.
- `docs/assets-policy.md` lines 5, 13: photorealistic-style isolated enemy master; transparent background without outline, base, or contact shadow.
- `.claude/skills/sit-enemy-sprite/SKILL.md` lines 18–22, 24–38, 40–44: camera-front 0° / true-right profile 90° convention, 45° target, eye vector may independently point +x, logical gridClass is distinct from pixel aspect, and actual image tool must request transparency.
- Reference image at original size: five striped brown gonzui with pale lateral stripes, whiskers, fins, and natural dorsal spines. The prompt uses the image for species/group identity and excludes its near-profile pose, overlaps, crop, fringe, background, and shadow.
- Species verification remains as recorded in the previous report: Kamogawa Sea World and Kyoto Prefecture's marine center identify gonzui as marine/saltwater fish; the revised prompt no longer calls them freshwater.

## Review checklist and evidence

| Check | Evidence | Result |
|---|---|---|
| Exact count | Prompt requires exactly five separate gonzui, each complete, and no other fish. Canonical row and inspected reference both record/show five. | Pass |
| Water element | Canonical M129 row says `水（魚。kako-jun 2026-10-21）`; prompt states Water is the recorded game element but excludes water/elemental effects. No habitat/environment is implied by the game attribute. | Pass |
| Species detail / corrected habitat | `freshwater` has been removed. `gonzui` with brown body, pale stripe, whiskers, fins and spines matches the reference/canonical “群れと毒棘” descriptor. No false freshwater qualifier remains. | Pass |
| Grid class | Prompt declares logical `gridClass 2x1`; monster grid table line 223 and encounter row line 146 agree. | Pass |
| Per-fish orientation | For every fish, prompt defines camera-front = 0°, true image-right side profile = 90°, and exactly 45° toward image-right; each snout/front aspect and near flank must be visible. Eye gaze +x is explicitly separated from body yaw, consistent with skill lines 20–22. | Pass |
| Source-reference scope | Old asset is limited to species and five-member group identity; its side pose, overlap, crop and artifacts are prohibited. Appearance details are supported by inspected pixels/source row. | Pass |
| Poison/spines and additions | Natural dorsal spines are retained as anatomy; added spikes, toxin clouds and poison effects are excluded. No armor, anthropomorphic features or other fish are allowed. | Pass |
| Map/background | Beach/shoreline are context only; water, waves, beach, map and scenery are explicitly prohibited. | Pass |
| Composition / margins | Centered group occupies 55–75% width and 45–65% height, with ≥12.5% margins. At 75% width, centered opposing margins are exactly 12.5%; max height 65% leaves 17.5%. All fish parts must remain inside the frame. | Pass |
| Transparency | Prompt requires `transparent_background=true` and alpha outside the fish. At generation time, the actual tool call must pass boolean `transparent_background: true`; the contract instruction is explicit. | Pass at contract stage; invocation check pending |

## Exact prompt reviewed

```text
Use case: photorealistic-natural
Asset type: isolated enemy battle master sprite for a Final Fantasy-inspired side-view RPG
Primary request: Recreate M129 ゴンズイ as one transparent battle sprite. Canonical row: "M129 | ゴンズイ | 水辺の生物 | 水辺（章は未定）。内灘 uchinada-beach（一任による決定 2026-10-15、docs/dungeon-enemies.md が正本） | 水（魚。kako-jun 2026-10-21） | 未定 | 未定（群れと毒棘） | 生成済み: assets/images/enemies/M129.webp（採否待ち。5匹の群れ・右向き・透過） | #12". Encounter row: "M129 | ゴンズイ（2x1） | A: beach＝砂浜・波打ち際（EA 1.4）。E: 群れと毒棘 | — （水） | 雑魚 | 群れ・毒棘（L 記述） | 絵あり（採否待ち） | ◎ | 未定 | 未定". The location and shoreline are context only; show no water, map, beach or scenery.
Reference: Use existing `assets/images/enemies/M129.webp` only to identify the fish species and five-fish group. Preserve five gonzui with slender brown bodies, pale lateral stripes, whiskers, fins and natural dorsal spines. Do not copy its profile pose, overlaps, edge crop, outline/fringe, background, or shadow. Water is the recorded element; do not add water effects or toxin clouds.
Subject: Exactly five separate gonzui fish swimming as a coordinated shoal. Each fish has a complete head, body, fins and tail in view. Do not add other fish.
Orientation definition for each fish: Define fish body yaw with camera-facing front = 0° and true image-right side profile = 90°. Each fish's head/body yaw is exactly 45° between these endpoints, facing toward image-right. Show each fish's snout/front-facing aspect together with its near flank; do not render any fish as a flat 90° side profile. The eyes follow the forward image-right direction; eye direction does not change head/body yaw.
Appearance: Photorealistic natural gonzui, brown body with pale side stripe, fine whiskers, fins and pointed dorsal spines. No anthropomorphic features, armor, added spikes, glow, stylized contour, rim light, chromatic aberration or colored edge treatment.
Canvas and scale: Landscape transparent canvas. Center all five complete fish as a compact logical gridClass 2x1 group. Shoal occupies 55–75% of canvas width and 45–65% of canvas height, centered in both axes. Leave at least 12.5% transparent margin on every side. Keep every tail, fin, whisker and spine within the canvas.
Lighting: Neutral white light without colored cast around the silhouettes.
Constraints: Set `transparent_background=true`. Preserve alpha transparency outside the fish. No text, letters, logos, watermark, border, outline, fringe, halo, pedestal, ground plane, water, waves, beach, scenery, contact shadow, toxin cloud, poison effect, or additional objects. No nonzero-alpha pixel may touch the canvas edge.
```

## Disposition

**Pass for this exact prompt at `contract/prompt` stage.** The false freshwater detail has been removed; the five-member shoal, Water element, `2x1`, individual exact 45° yaw, 12.5% margins, background/effect restrictions, reference scope and transparency setting are all consistent with the sources and skill. Verify the eventual imagegen invocation passes `transparent_background: true`. This pass does not generate or adopt an image; raw-image review remains required.
