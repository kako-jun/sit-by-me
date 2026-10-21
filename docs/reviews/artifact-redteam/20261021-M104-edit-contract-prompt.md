# M104 edit/re-render contract review — 2026-10-21

- Reviewer: Codex, independent artifact red-team reviewer
- Target: M104 乱暴な自転車
- Stage: `contract/prompt` only; no image edit or generation performed
- Canonical source commit: `64bb973967e41475ef55678e9ce7d10dd413dc4a`
- Prompt reviewed: `/tmp/sit-m104-edit-prompt.txt` (exact text below)
- Supplied edit reference inspected: `/home/kako-jun/.codex/generated_images/01a15ccc-868c-7f60-8889-229de4286e8f/exec-fd5cec7e-f602-42cf-93ae-5c2ac99b0257.png`, 1536×1024 RGBA, SHA-256 `707087a2af2c2e1ab5ae3fee554df1fb12a9d7cff0156854a745dc06a7b493e2`; its bicycle identity, blue paint and aged metal are reference-only. Its side-on projection, glow/background, edge residue, scale and framing are explicitly rejected.
- Canonical image inspected for M104 identity: `assets/images/enemies/M104.webp`, 640×418 RGBA/WebP, SHA-256 `5a18c6801cde0341238beff09b216a60a4c368a2a767c45df03bd82cb8841285`.
- Prior reviews: `20261021-M104-retry-contract-prompt.md` (pass); `20261021-M104-raw-image-fd5cec7e.md` (blockers: profile-like yaw, excessive size, insufficient margins and edge alpha).

## Sources checked

- `docs/monsters.md:103`: M104 is an unoccupied 乱暴な自転車; its current row specifies front wheel to image-right, transparency and no rider. Attribute, weakness and role remain TBD and are not turned into image details.
- `docs/monsters.md:209`: current logical `gridClass` is `2x1`; `:258` records the old 1x1 image footprint as historical only.
- `docs/dungeon-enemies.md:90`: M104 encounter row independently confirms `2x1`; location and proposed learning role are context, not depicted content.
- `docs/art-direction.md:74`: traffic/noise enemy category explicitly says not to depict a driver.
- `docs/assets-policy.md:5,13`: photorealistic-style isolated enemy image; enemy master has transparent background and no outline, pedestal or contact shadow.
- `docs/content-registry.md:5–11,20`: build prompts from canonical rows and relevant policy/skill; do not invent unsupported details or convert TBDs into facts.
- `.claude/skills/sit-enemy-sprite/SKILL.md:18–22,24–38,40–44`: camera-front 0° / true-right profile 90° / required 45° yaw; no head, torso or eyes means those checks are N/A; `gridClass` is logical occupancy independent of pixel dimensions; transparency must be requested in the actual image tool call.
- The previous raw candidate was inspected at original size. It depicts one worn blue bicycle with two wheels, frame, handlebar, saddle, pedals and chain. Its existing profile-like projection and glow/background are visibly present and directly excluded by this prompt.

## Review checklist and evidence

| Check | Evidence | Result |
|---|---|---|
| Subject identity and count | Prompt requests exactly one old blue bicycle and names the visible major parts supported by the supplied candidate and canonical asset. No person/rider or anthropomorphic traits are added. “Same specific bicycle identity” is limited to bicycle/part identity, blue paint and aged metal; it does not preserve the failed pose or background. | Pass |
| Unsupported details and TBDs | Worn blue paint and aged/rusty metal are visible in the reference. Handlebar, two wheels, frame, saddle, pedals and chain are visible. No attribute, weakness, attack, map scene or learning effect is asserted. | Pass |
| Exact camera angle | Prompt defines front = 0°, true image-right profile = 90°, and targets exactly 45° toward image-right. It positively requires near frame side plus forward-facing handlebar/front-wheel assembly. | Pass |
| Wheel projection / overlap | Both wheel planes are to be foreshortened, the front wheel on image-right and larger in perspective, and the front wheel partially overlapping the rear wheel. These are mutually compatible at the specified front-right camera direction: the nearer front assembly can project larger and overlap the farther rear assembly while the frame side remains visible. The requirements directly address the two prior profile-like candidates. | Pass |
| `gridClass` | Prompt explicitly declares logical `2x1`, matching both `docs/monsters.md:209` and `docs/dungeon-enemies.md:90`. | Pass |
| Canvas box / composition feasibility | 1536×1024 canvas; inclusive x=307…1228 gives 922 px (60.0% width), y=205…818 gives 614 px (60.0% height), centered with 20% margins on each opposing side. The bicycle can fit this 3:2 box while preserving horizontal orientation; gridClass remains a separate logical property. The same strict box applies to the full silhouette and its alpha, avoiding conflict between stated scale and margins. | Pass |
| Reference scope and exclusions | The supplied candidate is explicitly identity/color/material reference only. Its side view, crop, glow, alpha residue and background are rejected. Rider, map/road/environment, motion/sound/magic effects, outline/fringe/halo, ground and shadows are excluded. No unsupported bicycle component is required. | Pass |
| Transparency | Prompt requires `transparent_background=true`, actual alpha 0 outside the bicycle except direct neutral edge antialiasing, and no nonzero-alpha pixel beyond the box. At execution the actual imagegen tool argument must be boolean `transparent_background: true`; this review checks the contract, not a future invocation. | Pass at contract stage; invocation check pending |

## Exact prompt reviewed

```text
Mode: edit/reference-based re-render of the supplied candidate into a new raw PNG candidate. Keep the same specific bicycle identity and worn blue color, but change the camera projection and canvas composition described below. Do not edit the canonical asset.
Target: M104 乱暴な自転車. Canonical row: "M104 | 乱暴な自転車 | 交通と騒音 | 寺町 hinomi-bend（弧の道）（一任による決定 2026-10-15、docs/dungeon-enemies.md が正本） | 未定 | 未定 | 未定 | 生成済み: assets/images/enemies/M104.webp（採否待ち。右向き（前輪が右）・透過・無人） | #12、art-direction.md". Encounter record: "M104 | 乱暴な自転車（2x1） | A: hinomi-bend＝見通しの悪い曲がり角（EA 1.1）。H: 救済＝無属性ダメージ魔法のラーニング元（案。寺町の弱い敵。learning-schedule.md §1b） | （案）無属性ダメージ魔法 | 雑魚 | 未定 | 絵あり | △ | 未定 | 可（拠点。再訪できる。MT 7.2）". Location/learning role are context only; show no map, road, scene, magic or effect.
Image 1 is the previous M104 generated candidate. Use it to preserve bicycle part identity, worn blue frame, and old metal only. It is a blocked near-profile candidate. Re-render the bicycle from a different camera view; do not preserve its flat side projection, crop, radial glow, edge-alpha residue, or any background.
Subject: Exactly one old blue bicycle with two complete wheels, frame, handlebar, saddle, pedals and chain. No rider, person or anthropomorphic feature. Head/torso/eye orientation is N/A.
Exact camera definition: camera-facing bicycle front = yaw 0°; true image-right side profile = yaw 90°; required bicycle yaw = exactly 45° between them, facing image-right with the front wheel on image-right. Show both the bicycle's near frame side and the front-facing aspect of the handlebar/front-wheel assembly. Make the front wheel visibly foreshortened to an ellipse, and make the rear wheel also foreshortened; the two wheels must not appear as two full circular side-on faces. The front wheel is larger in perspective and partially overlaps the rear wheel. The snout/front of the head tube and handlebar assembly face image-right and toward the camera.
Appearance: Photorealistic natural object, worn blue paint and aged/rusty metal. No stylized outline, glow, rim light, chromatic aberration, color fringe, sticker edge or drop shadow.
Canvas: Output a 1536×1024 landscape transparent canvas. Keep the entire bicycle silhouette inside x=307…1228 and y=205…818 inclusive. Center it within that box. No nonzero-alpha pixel, part, or glow outside this box. This is logical gridClass `2x1`; pixel dimensions do not set grid occupancy.
Tool and exclusions: Set `transparent_background=true`. Preserve actual alpha=0 in the full area outside the bicycle, except neutral antialiasing directly along the silhouette. No text, letters, logos, watermark, outline, fringe, halo, pedestal, ground plane, road, scenery, contact shadow, motion streaks, sound waves, magic, effect, rider, person, or extra object. Do not crop any bicycle part.
```

## Disposition

**Pass for this exact prompt at `contract/prompt` stage.** The reference scope preserves source-supported bicycle identity and material while rejecting the old failed projection/artifacts. The defined 45° camera view, foreshortened/overlapping wheel constraints, front-wheel-right direction, 2x1 grid, fixed box, transparency and exclusions are compatible and address prior blockers without requiring unsupported parts. Before generation, pass the supplied candidate as the edit reference and set the actual imagegen argument `transparent_background: true`. Raw-image review is still required; this pass does not generate or adopt an image.
