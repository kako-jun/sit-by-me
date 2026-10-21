# M133 edit/re-render contract review — 2026-10-21

- Reviewer: Codex, independent artifact red-team reviewer
- Target: M133 毒キノコ
- Stage: `contract/prompt` only; no image edit or generation performed
- Canonical source commit: `64bb973967e41475ef55678e9ce7d10dd413dc4a`
- Prompt reviewed: `/tmp/sit-m133-edit-prompt.txt` (exact text below)
- Supplied edit reference inspected: `/home/kako-jun/.codex/generated_images/01a15ccc-868c-7f60-8889-229de4286e8f/exec-263b8baf-64cf-4149-8054-4224cbc454d7.png`, 1536×1024 RGBA, SHA-256 `af7b25b7cfec3201cbf7cdd833c69c0e27de11eb84824b229a68f5514691afd2`; its four mushroom forms, colors, pale stems and spores are reference-only. The radial glow, background pixels and failed framing are explicitly excluded.
- Canonical image inspected: `assets/images/enemies/M133.webp`, 640×466 WebP, SHA-256 `2984bd3d1899eb90999c6579962dacaa7a164aa7f1b2ea0781e78ab7e1be9fbe`; used to confirm the same four-mushroom/spore identity and prohibit environmental parts from the edit reference.
- Prior reports: `20261021-M133-retry2-contract-prompt.md` (pass); `20261021-M133-raw-image-263b8baf.md` (blocker: radial background/alpha outside box and subject vertical overflow).

## Sources checked

- `docs/monsters.md:132`: M133 is 毒キノコ in family 毒と尖り; attributes/weakness are TBD; role detail is spores disturbing vision/judgment; current canonical image is pending adoption and notes transparency/spores.
- `docs/dungeon-enemies.md:122`: M133 is a regular enemy with logical `1x1`; spores are the documented distinguishing feature; location is provenance/context.
- `docs/art-direction.md:83`: poison mushroom belongs to the poison/sharp-object family.
- `docs/assets-policy.md:5,13`: photorealistic-style isolated enemy image; transparent background, no outline, base or contact shadow.
- `docs/content-registry.md:5–11,20`: prompt must follow canonical records and policy, avoid unsupported facts, and keep TBDs unresolved.
- `.claude/skills/sit-enemy-sprite/SKILL.md:18–22,24–38,40–44`: orientation is N/A when no head/torso/eyes; `gridClass` is logical occupancy independent of pixel dimensions; actual tool call must request transparency.
- Both the blocked edit-reference candidate and canonical M133 image were inspected. Each shows exactly one dominant red cap with white flecks and three smaller red-capped mushrooms, pale stems and separate pale airborne spores. The edit prompt retains those features and composition, removes the radial glow and old background, and retains no ground/forest content.

## Review checklist and evidence

| Check | Evidence | Result |
|---|---|---|
| Exact subject count and arrangement | Prompt requires the same four visible mushrooms and relative arrangement: one dominant and three smaller, matching the inspected candidate and canonical image. All four stems and separate spores are explicitly preserved; no extra mushroom/object. | Pass |
| Appearance and spores | Red caps, white flecks, pale stems and pale airborne spores are visible in both images; spores also match canonical M133's documented feature. No cloud/toxin effect is added. | Pass |
| Background removal | The candidate's broad brown/gray radial glow and any background pixels are explicitly discarded; alpha=0 outside actual mushroom/spore silhouettes, with antialiasing limited to their direct edges. The unwanted visual field can be removed without changing the subject identity. | Pass |
| `gridClass` | Logical `1x1` is explicit and matches `docs/dungeon-enemies.md:122`; pixel canvas region does not infer grid occupancy. | Pass |
| Fixed frame feasibility | 1536×1024 canvas; inclusive x=307…1228 is 922 px wide (60%); y=205…818 is 614 px high (60%). It is a centered, feasible 60%×60% region. The four mushrooms and all spores can be uniformly recomposed within it; no conflicting subject-scale bound exists. | Pass |
| Orientation / anatomy | Explicitly non-anthropomorphic; no head, eyes, limbs or torso; yaw N/A is appropriate and matches the sprite skill. | Pass |
| Location and prohibited details | Location and encounter data are context only; no map or scene. Soil, moss, grass, roots, wood, forest, ground, shadow, pedestal, poison cloud and colored toxin effect are excluded. No TBD attribute/weakness is inferred. | Pass |
| Transparency argument | Prompt specifies `transparent_background=true` and genuine alpha. Actual imagegen invocation must pass boolean `transparent_background: true`. | Pass at contract stage; invocation check pending |

## Exact prompt reviewed

```text
Mode: image edit/re-render of Image 1 into a new raw PNG candidate; preserve the four-mushroom subject but correct framing and background. Do not modify the canonical asset.
Target: M133 毒キノコ. Canonical row: "M133 | 毒キノコ | 毒と尖り | 湿った林・古い木壁・山の遊園地跡。卯辰山 utatsuyama-sunnyland（一任による決定 2026-10-15、docs/dungeon-enemies.md が正本） | 未定 | 未定 | 未定（胞子で視界や判断を乱す） | 生成済み: assets/images/enemies/M133.webp（採否待ち。透過・胞子つき） | #12". Encounter row: "M133 | 毒キノコ（1x1） | A: 台帳の候補地「湿った林・古い木壁・山の遊園地跡」（L 3-3・4）。E: 胞子で視界や判断を乱す（状態異常の担い手） | — | 雑魚 | 胞子（L 記述） | 絵あり | ◎ | 未定 | 未定". Location/encounter are context only; show no map or scene.
Image 1 is the prior M133 candidate, which has the correct four mushroom forms, cap colors, pale stems and spores, but failed because its subject and glow extend beyond the required frame. Keep exactly the same four visible mushrooms and their relative arrangement; preserve red caps with white flecks, pale stems, and separate pale spores. Remove the entire brown/gray radial glow and any background pixels; do not preserve the failed framing.
Subject: Exactly four non-anthropomorphic mushrooms, one dominant large cap with three smaller mushrooms, all stems visible, plus separate spores. No face, eyes, limbs or humanoid body; orientation is N/A.
Rendering: Photorealistic natural mushroom cap, gill and stem detail. No outline, fringe, halo, glow, rim light, chromatic aberration, drop shadow or colored cast.
Canvas/grid: Output a 1536×1024 landscape transparent canvas for logical gridClass `1x1`. Recompose the whole group, including all spores, inside x=307…1228 and y=205…818 inclusive. Center it within that region. No mushroom, spore, glow or other nonzero-alpha pixel outside the box. Do not crop any of the four mushrooms or spores.
Tool and exclusions: Set `transparent_background=true`. Pixels outside the mushrooms/spores must have alpha exactly 0; neutral antialiasing only directly at their edges. No soil, moss, grass, roots, wood, forest, scenery, ground, contact shadow, pedestal, poison cloud, colored toxin effect, text, letters, logo, watermark, border, outline, fringe, halo, or additional mushroom/object.
```

## Disposition

**Pass for this exact prompt at `contract/prompt` stage.** The four mushrooms and spores are source-supported and explicitly retained; the failed glow/background and oversized framing are directly addressed. The fixed 60%×60% box is compatible with a centered 1x1 subject group, and genuine transparency is specified. At execution, use the supplied candidate as edit reference and set actual `transparent_background: true`. No image generated or modified; raw-image review remains required.
