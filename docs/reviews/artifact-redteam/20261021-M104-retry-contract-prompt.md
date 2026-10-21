# M104 retry contract/prompt review — 2026-10-21

- Reviewer: Codex, independent artifact red-team reviewer
- Target: M104 乱暴な自転車
- Stage: `contract/prompt` only; no image generated
- Canonical source commit: `64bb973967e41475ef55678e9ce7d10dd413dc4a`
- Prompt reviewed: `/tmp/sit-m104-retry-prompt.txt` (exact text below)
- Visual reference inspected: `assets/images/enemies/M104.webp` (640×418 WebP; SHA-256 `5a18c6801cde0341238beff09b216a60a4c368a2a767c45df03bd82cb8841285`), declared bicycle/component identity reference only
- Prior reviews: contract pass `20261021-M104-contract-prompt.md`; raw candidate blocker `20261021-M104-raw-image-ccbf1a25.md` (side-profile appearance, fringe, insufficient margin)

## Sources checked

- `docs/content-registry.md` lines 5–11 and 20: use canonical enemy rows and avoid unsupported facts; preserve source constraints and TBD values.
- `docs/monsters.md` line 103: M104 is 乱暴な自転車, family 交通と騒音, placed at Teramachi hinomi-bend, with attribute/weakness/role unresolved; its existing image record says right-facing with the front wheel on the right, transparent, unmanned, and pending adoption.
- `docs/dungeon-enemies.md` line 90: M104 is `2x1`; its location is the blind curve, with an unfinalized learning-source proposal. Its role is regular enemy; other identity/pattern details remain unresolved.
- `docs/dungeon-enemies.md` lines 275 and 419: the blind curve is described as a sudden-appearance/road-corner fear; the record explicitly says not to invent a stronger distinct reason without a source.
- `docs/art-direction.md` lines 71–74: M104 belongs to the “交通と騒音” category; that row says the driver is not depicted.
- `docs/assets-policy.md` lines 5 and 13: photorealistic-style enemy, isolated transparent master without outline, base, or contact shadow.
- `.claude/skills/sit-enemy-sprite/SKILL.md` lines 18–22, 24–38, 40–44: explicit camera-front 0° / true-right profile 90° yaw convention; 45° target; absent head/torso/eyes are N/A; gridClass is logical occupancy; transparency must be requested in the actual image tool call.
- Reference pixels: the existing image shows one worn blue city bicycle with two wheels, frame, handlebar, saddle, pedals and chain; it has no rider. It is nearly side-on with strong outline/color fringe and little margin. The prompt excludes its pose, crop, fringe, background and shadow.

## Review checklist and evidence

| Check | Evidence | Result |
|---|---|---|
| Identity and count | Exactly one old blue bicycle; all named parts match the canonical image's visible construction. No rider, person or anthropomorphic features are added. | Pass |
| Reference scope | The old image is restricted to bicycle identity/components; its profile, crop, outline/fringe, background and contact shadow are explicitly rejected. | Pass |
| Canonical uncertainty | Attribute, weakness, role and proposed learning detail are not promoted to fixed appearance. Location/learning are context-only; prompt excludes map, scenery, magic and effects. | Pass |
| Angle and facing | Explicitly defines camera-facing front 0°, true image-right side profile 90°, and exact 45° between them. It further requires front wheel on image-right and both near-side and forward-facing assembly planes. This resolves the prior side-profile risk and matches the skill. | Pass |
| `gridClass 2x1` | Prompt declares the logical class and separates it from pixel dimensions; encounter row line 90 agrees. | Pass |
| Scale and margins | 3:2 canvas; width 55–65%, height 45–65%, centered; 17.5% minimum transparent margin on all sides. The 65% maxima leave exactly 17.5% on both opposing sides, so bounds are compatible. | Pass |
| Negative constraints | Prohibits map/road/scene, contact shadow, sound/motion effects, magic, text, outline/fringe, person/rider and extra objects; no nonzero alpha at edges. These are consistent with an isolated master. | Pass |
| Transparency | Prompt explicitly requires `transparent_background=true` and genuine alpha. At generation, the actual tool call must set boolean `transparent_background: true`; this review verifies the contract text, not a future invocation. | Pass at contract stage; invocation check pending |

## Exact prompt reviewed

```text
Use case: photorealistic-natural
Asset type: isolated enemy battle master sprite for a Final Fantasy-inspired side-view RPG
Primary request: Recreate M104 乱暴な自転車 as one isolated transparent sprite. Canonical row: "M104 | 乱暴な自転車 | 交通と騒音 | 寺町 hinomi-bend（弧の道）（一任による決定 2026-10-15、docs/dungeon-enemies.md が正本） | 未定 | 未定 | 未定 | 生成済み: assets/images/enemies/M104.webp（採否待ち。右向き（前輪が右）・透過・無人） | #12、art-direction.md". Encounter row: "M104 | 乱暴な自転車（2x1） | A: hinomi-bend＝見通しの悪い曲がり角（EA 1.1）。H: 救済＝無属性ダメージ魔法のラーニング元（案。寺町の弱い敵。learning-schedule.md §1b） | （案）無属性ダメージ魔法 | 雑魚 | 未定 | 絵あり | △ | 未定 | 可（拠点。再訪できる。MT 7.2）". Location and learning role are context only; depict no map, scene, magic, or effect.
Reference: Use existing `assets/images/enemies/M104.webp` only to identify one old blue city bicycle and its visible components: two wheels, frame, handlebar, saddle, pedals, chain. Do not copy its flat side profile, crop, outline/fringe, background, or contact shadow. No person is present in the canonical record; do not add a rider.
Subject: Exactly one unoccupied worn blue bicycle with some aged/rusty metal, two complete wheels, handlebar, saddle, pedals, chain, and frame. No rider, person or anthropomorphic features; head/torso/eye checks are N/A.
Orientation definition: Define bicycle yaw with camera-facing front = 0°, true image-right side profile = 90°. Target bicycle yaw is exactly 45° between those endpoints, facing image-right. Place the front wheel on image-right. Show the near side of the frame and wheels and the forward-facing aspects of the handlebar and front-wheel assembly. Avoid a flat 90° side profile and a straight-on head-on view.
Appearance: Photorealistic natural bicycle surface, worn blue paint and aged metal. No stylized outline, glow, rim light, chromatic aberration or colored edge treatment.
Canvas and scale: 3:2 landscape transparent canvas. Bicycle silhouette occupies 55–65% of canvas width and 45–65% of canvas height, centered in both axes. Leave at least 17.5% transparent margin on every side. Keep both tires, handlebars, saddle and pedals inside the canvas. Logical gridClass is 2x1; pixel dimensions do not determine grid occupancy.
Lighting: Neutral white light without colored cast around the silhouette.
Constraints: Set `transparent_background=true`. Genuine alpha transparency outside the bicycle. No text, letters, logos, watermark, border, outline, fringe, halo, pedestal, ground plane, road, scenery, contact shadow, motion streaks, sound waves, magic, effects, rider, person, or additional objects. No nonzero-alpha pixel may touch the canvas edge.
```

## Disposition

**Pass for this exact prompt at `contract/prompt` stage.** The revised angle explicitly requests front/right planes at exact 45°, includes the current `2x1` grid, uses the old image only for supported identity and visible parts, supplies feasible scale/margin bounds, excludes riders/effects, and requires the transparency argument. At generation, confirm the actual call sets `transparent_background: true`. This review does not generate or adopt an image; raw-image review remains required.
