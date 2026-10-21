# M133 retry 2 contract/prompt review — 2026-10-21

- Reviewer: Codex, independent artifact red-team reviewer
- Target: M133 毒キノコ
- Stage: `contract/prompt` only; no image generated
- Canonical source commit: `64bb973967e41475ef55678e9ce7d10dd413dc4a`
- Prompt reviewed: `/tmp/sit-m133-retry2-prompt.txt` (exact text below)
- Generation reference scope: no input image is attached or requested; the written appearance/count description matches the existing M133 image inspected by reviewer at `assets/images/enemies/M133.webp` (pending-adoption source, reference-only for this review). Prior candidate fringe/margin failures are not used as geometry sources.

## Sources checked

- `docs/content-registry.md` lines 5–11 and 20: enemy prompt must follow canonical row and policies, avoid unsupported facts, and resolve any image-affecting TBD before generation.
- `docs/monsters.md` line 132: M133 is 毒キノコ in the “毒と尖り” family, placed at the damp forest/old wooden wall/mountain amusement-park remains; attributes and weakness are TBD; role detail is “胞子で視界や判断を乱す”; current image is pending adoption and notes transparency/spores.
- `docs/dungeon-enemies.md` line 122: M133 is a regular enemy with logical grid `1x1`; spores are its documented distinguishing feature and location/map details are provenance/context.
- `docs/art-direction.md` line 83: poison mushroom belongs to the “毒と尖り” enemy family.
- `docs/assets-policy.md` lines 5 and 13: photorealistic-style isolated enemy image, transparent background, no outline/base/contact shadow.
- `.claude/skills/sit-enemy-sprite/SKILL.md` lines 18–22, 24–38, 40–44: orientation checks are N/A for subjects without head/torso/eyes; logical grid class is independent of pixel bounds; transparency must be requested in the actual image tool call.
- Existing M133 image inspected at original size: four mushrooms (one dominant large cap and three smaller caps), red caps with white flecks, pale stems, and light airborne spores. The prompt's text-only input preserves these source-identity facts while excluding the old soil/moss/wood setting, outline/fringe, shadow and crop.

## Review checklist and evidence

| Check | Evidence | Result |
|---|---|---|
| Exact count and arrangement | Prompt explicitly specifies exactly four mushrooms: one dominant large red cap with white flecks above/behind three smaller red-capped mushrooms, all with pale stems. This matches the inspected existing image; “no extra mushroom” reinforces count. | Pass |
| Spores / poison facts | Spores are canonical M133's distinguishing feature and role (“spores disturb vision/judgment”). Prompt keeps pale airborne spores, but excludes a poison cloud or colored toxin effect; this does not suppress the documented spores or invent an emitted attack. | Pass |
| Grid / frame | Canonical encounter row says `1x1`; prompt explicitly states logical `1x1`. A 1536×1024 canvas is stated separately, correctly treating gridClass as logical occupancy. | Pass |
| Coordinate box feasibility | Inclusive box x=307…1228 is 922 px wide; y=205…818 is 614 px high. This is a centered 60%×60% canvas region, leaving 307 px (20%) left/right and 205 px (20%) top/bottom. It fits the 1536×1024 canvas and gives the four caps/stems/spores explicit bounds. No competing scale or margin condition is present. | Pass |
| Centering and completeness | Whole group is centered; all four stems, all caps, and every visible spore must remain inside the explicit box. Three smaller mushrooms must be individually distinguishable. | Pass |
| Orientation N/A | Mushrooms are explicitly non-anthropomorphic with no eyes, face, limbs or humanoid form. Head/torso/eye yaw is correctly marked N/A under the enemy skill; it does not evade any relevant geometry check. | Pass |
| Source/environment and unsupported additions | Location and encounter records are explicitly context only; no map/place/scenery is depicted. Soil, moss, grass, roots, wood, forest, ground, contact shadow, pedestal, poison cloud, toxin effect and extra objects are prohibited. | Pass |
| Text-only reference | Prompt says no source image is attached and constructs from the exact written description. This avoids carrying forward the old asset's crop/outline/background while retaining its visible source identity in text. | Pass |
| Transparency / edge constraints | Prompt demands `transparent_background=true`, alpha=0 outside the mushroom/spore silhouettes except neutral edge antialiasing, and no nonzero-alpha pixel outside the coordinate box. This is explicit; the actual imagegen call must pass boolean `transparent_background: true`. | Pass at contract stage; invocation check pending |

## Exact prompt reviewed

```text
Use case: photorealistic-natural
Asset type: isolated enemy battle master sprite for a Final Fantasy-inspired side-view RPG
Primary request: Create a new sprite for M133 毒キノコ. Canonical record: "M133 | 毒キノコ | 毒と尖り | 湿った林・古い木壁・山の遊園地跡。卯辰山 utatsuyama-sunnyland（一任による決定 2026-10-15、docs/dungeon-enemies.md が正本） | 未定 | 未定 | 未定（胞子で視界や判断を乱す） | 生成済み: assets/images/enemies/M133.webp（採否待ち。透過・胞子つき） | #12". Encounter record: "M133 | 毒キノコ（1x1） | A: 台帳の候補地「湿った林・古い木壁・山の遊園地跡」（L 3-3・4）。E: 胞子で視界や判断を乱す（状態異常の担い手） | — | 雑魚 | 胞子（L 記述） | 絵あり | ◎ | 未定 | 未定". These location and encounter details are context only. Do not show map, place, scenery or battle environment.
Subject: Exactly four non-anthropomorphic mushrooms: one dominant large red cap with white flecks above/behind three smaller red-capped mushrooms; all have pale stems. Include loose pale airborne spores around the group. No eyes, face, limbs or humanoid form. Head/torso/eye orientation is N/A.
Rendering: Photorealistic natural mushrooms with realistic cap, gill and stem detail. No source image is attached; construct from the exact description above. No illustration contour, glow, rim light, chromatic aberration, color-fringe, sticker edge or drop shadow.
Grid/composition: Logical gridClass `1x1`. Use a 1536×1024 landscape transparent canvas. Center the complete four-mushroom group. Put every mushroom and every visible spore wholly inside pixel box x=307…1228 and y=205…818 inclusive. No mushroom, spore, glow or other nonzero-alpha pixel may extend outside that box. Keep the three smaller mushrooms individually distinguishable and all four stems visible.
Lighting: Neutral white light with no colored cast and no backlighting around edges.
Tool/output constraints: Set `transparent_background=true`. Actual canvas outside the mushroom and spore silhouettes must be alpha 0, with only neutral antialiasing directly on their edges. No soil, moss, grass, roots, wood, forest, scenery, ground, contact shadow, pedestal, poison cloud, colored toxin effect, text, letters, logo, watermark, border, outline, fringe, halo, extra mushroom or extra object. Do not crop any mushroom or spore.
```

## Disposition

**Pass for this exact prompt at `contract/prompt` stage.** Count/arrangement, spores, 1x1 grid, N/A orientation, exact canvas/coordinate box, no-environment/no-toxin constraints, text-only appearance grounding and transparency instruction are consistent and feasible. At generation, confirm the actual imagegen call passes `transparent_background: true`. This pass does not generate or adopt an image; a raw-image review remains required.
