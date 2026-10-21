# M129 retry contract/prompt review — 2026-10-21

- Reviewer: Codex, independent artifact red-team reviewer
- Target: M129 ゴンズイ
- Stage: `contract/prompt` only; no image generated
- Canonical source commit: `64bb973967e41475ef55678e9ce7d10dd413dc4a`
- Prompt reviewed: `/tmp/sit-m129-retry-prompt.txt` (exact text below)
- Visual reference inspected: `assets/images/enemies/M129.webp` (640×433 WebP; SHA-256 `8f4259c43b69b46dc937d64037121a344b17070347fd63a0aadef5ff6b6d198f`), used as fish/group identity reference only; its pose, crop and edge artifacts are explicitly excluded
- Prior contract: `docs/reviews/artifact-redteam/20261021-M129-contract-prompt-recheck.md` (pass for prior prompt)
- Prior raw-image review: `docs/reviews/artifact-redteam/20261021-M129-raw-image-aea25d47.md` (blocker: side profile, cropped tail, color fringe)

## Sources checked

- `docs/content-registry.md` lines 5–11 and 20: derive from canonical row and applicable policy/skill; do not introduce unsupported appearance or mechanics.
- `docs/monsters.md` line 128: M129 is ゴンズイ, a waterside creature at 内灘 uchinada-beach; attribute is `水（魚。kako-jun 2026-10-21）`; weakness is TBD; role is `未定（群れと毒棘）`; the existing five-fish image is pending adoption.
- `docs/monsters.md` line 223: current logical grid is `2x1`, with five gonzui arranged horizontally.
- `docs/dungeon-enemies.md` line 146: M129 encounter row says `2x1`, beach/shoreline placement, group and venomous spines, Water, regular enemy.
- `docs/assets-policy.md` lines 5, 13: enemy is a photorealistic-style isolated sprite without outline/base/contact shadow.
- `.claude/skills/sit-enemy-sprite/SKILL.md` lines 18–22, 24–38, 40–44: exact yaw convention and 45° target; eye vector may be +x while body remains at 45°; logical gridClass does not define pixel size; actual image tool must request transparency.
- Existing image inspection: five slender dark-brown fish with pale lateral stripes, whiskers, fins and natural dorsal spines. Their pose is a near-90° side profile; some tails/spines and silhouette edges have crop/artifact issues. Prompt identifies the species and shoal only and excludes copying those defects.
- Species fact check: Kamogawa Sea World says gonzui is a saltwater fish and that they shoal, with venomous dorsal and pectoral fin spines ([Kamogawa Sea World, animal information](https://www.kamogawa-seaworld.jp/animal/movie/vol_154/), lines 99–101). Kyoto Prefecture's marine center similarly describes gonzui as a fish of the sea, striped brown juveniles, shoaling, and venomous dorsal/pectoral spines ([Kyoto Prefecture, “丹後の海の生き物（ゴンズイ）”](https://www.pref.kyoto.jp/kaiyo/gonzui.html), lines 69–72).

## Review checklist and findings

| Check | Evidence | Result |
|---|---|---|
| Exact fish count | Canonical row and image record say five; prompt explicitly says exactly five separate gonzui, each complete, and no other fish. The inspected reference visibly contains five. | Pass |
| Water element | Canonical monster row explicitly records Water as the intrinsic element; encounter row records `— （水）`. Prompt repeats Water without adding elemental visuals. | Pass |
| Species / habitat qualifier | Prompt calls the species “freshwater gonzui.” The canonical placement is a shoreline, and authoritative aquarium/government sources identify gonzui as a saltwater/sea fish. “Freshwater” is an unsupported and factually conflicting species detail. | **Major** |
| 2x1 grid | Prompt states logical `gridClass 2x1`; both monsters grid table line 223 and encounter row line 146 agree. | Pass |
| Angle per fish | It defines camera-front 0°, true-right profile 90°, and exactly 45° for each fish's head/body, all facing +x. It separately allows eye gaze +x and asks for the snout/front aspect and near flank. This is explicit and consistent with the skill. | Pass |
| Reference scope / identity | Reference is limited to the fish species and five-member group; pose, overlaps, crop, outline/fringe, background and shadow are excluded. Listed dark brown body, pale stripe, whiskers, fins and natural dorsal spines are visible in source image or canonical “群れと毒棘” description. | Pass |
| Toxin / unsupported additions | Prompt preserves natural pointed dorsal spines, bans added spikes, and excludes toxin clouds, poison effects and elemental effects. This fits the source’s venomous-spine description without inventing a toxin emission. | Pass |
| Location/background | Shoreline is explicitly provenance/context only; water, map, beach and scenery are prohibited. | Pass |
| Scale and margins | Group bounds are 55–75% canvas width and 45–65% height, centered; at 75% width, opposing 12.5% margins are exactly feasible; height leaves at least 17.5%. Tails, fins, whiskers and spines are included. | Pass |
| Transparency | Prompt explicitly requires `transparent_background=true` and genuine alpha. The actual generation call must pass boolean `transparent_background: true`; contract wording is correct, invocation remains to be checked when generated. | Pass at contract stage |

## Exact correction required

Replace `Photorealistic natural freshwater gonzui` with `Photorealistic natural gonzui` (or `Photorealistic natural marine gonzui`). Do not use “freshwater.” Keep the explicit no-water/no-shoreline-background constraint; the Water game element does not imply a depicted environment.

## Exact prompt reviewed

```text
Use case: photorealistic-natural
Asset type: isolated enemy battle master sprite for a Final Fantasy-inspired side-view RPG
Primary request: Recreate M129 ゴンズイ as one transparent battle sprite. Canonical row: "M129 | ゴンズイ | 水辺の生物 | 水辺（章は未定）。内灘 uchinada-beach（一任による決定 2026-10-15、docs/dungeon-enemies.md が正本） | 水（魚。kako-jun 2026-10-21） | 未定 | 未定（群れと毒棘） | 生成済み: assets/images/enemies/M129.webp（採否待ち。5匹の群れ・右向き・透過） | #12". Encounter row: "M129 | ゴンズイ（2x1） | A: beach＝砂浜・波打ち際（EA 1.4）。E: 群れと毒棘 | — （水） | 雑魚 | 群れ・毒棘（L 記述） | 絵あり（採否待ち） | ◎ | 未定 | 未定". The location and shoreline are context only; show no water, map, beach or scenery.
Reference: Use existing `assets/images/enemies/M129.webp` only to identify the fish species and five-fish group. Preserve five gonzui with slender brown bodies, pale lateral stripes, whiskers, fins and natural dorsal spines. Do not copy its profile pose, overlaps, edge crop, outline/fringe, background, or shadow. Water is the recorded element; do not add water effects or toxin clouds.
Subject: Exactly five separate gonzui fish swimming as a coordinated shoal. Each fish has a complete head, body, fins and tail in view. Do not add other fish.
Orientation definition for each fish: Define fish body yaw with camera-facing front = 0° and true image-right side profile = 90°. Each fish's head/body yaw is exactly 45° between these endpoints, facing toward image-right. Show each fish's snout/front-facing aspect together with its near flank; do not render any fish as a flat 90° side profile. The eyes follow the forward image-right direction; eye direction does not change head/body yaw.
Appearance: Photorealistic natural freshwater gonzui, brown body with pale side stripe, fine whiskers, fins and pointed dorsal spines. No anthropomorphic features, armor, added spikes, glow, stylized contour, rim light, chromatic aberration or colored edge treatment.
Canvas and scale: Landscape transparent canvas. Center all five complete fish as a compact logical gridClass 2x1 group. Shoal occupies 55–75% of canvas width and 45–65% of canvas height, centered in both axes. Leave at least 12.5% transparent margin on every side. Keep every tail, fin, whisker and spine within the canvas.
Lighting: Neutral white light without colored cast around the silhouettes.
Constraints: Set `transparent_background=true`. Preserve alpha transparency outside the fish. No text, letters, logos, watermark, border, outline, fringe, halo, pedestal, ground plane, water, waves, beach, scenery, contact shadow, toxin cloud, poison effect, or additional objects. No nonzero-alpha pixel may touch the canvas edge.
```

## Disposition

**Major finding remains; do not generate from this prompt.** Remove the unsupported/factually conflicting “freshwater” descriptor, then obtain a new prompt review. All requested count, Water element, 2x1 grid, per-fish 45° geometry, 12.5% minimum margins, no-environment/no-toxin-effects constraints, and transparency tool-setting instruction otherwise pass. This review neither generates nor adopts an image.
