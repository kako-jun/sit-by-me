# M133 background-extraction edit contract review — 2026-10-21

- Reviewer: Codex, independent artifact red-team reviewer
- Target: M133 毒キノコ
- Stage: `contract/prompt` only; no edit or generation performed
- Canonical source commit: `64bb973967e41475ef55678e9ce7d10dd413dc4a`
- Prompt reviewed: `/tmp/sit-m133-bg-prompt.txt` (exact text below)
- Image 1 inspected and identified as latest blocked edit candidate: `/home/kako-jun/.codex/generated_images/01a15ccc-868c-7f60-8889-229de4286e8f/exec-370149f0-bd62-4833-8ab3-d01fa5f3cb22.png`, 1536×1024 RGBA, SHA-256 `bd8af0add559c89ecdbf66b6d9f8e6fc0116135c4b166c63738e37c9c8e89174`; it shows the desired four mushroom forms/spores plus the unwanted radial field. The candidate's prior raw review is `20261021-M133-raw-image-370149f0.md`.

## Sources checked

- `docs/monsters.md:132`: M133 毒キノコ, attribute and weakness TBD, role detail says spores disturb vision/judgment; current canonical image is pending adoption and notes spores/transparency.
- `docs/dungeon-enemies.md:122`: M133 is a regular enemy with logical `1x1`; spores are the documented distinguishing feature; location is context only.
- `docs/art-direction.md:83`: poison mushroom belongs to the “毒と尖り” category.
- `docs/assets-policy.md:5,13`: isolated photorealistic-style enemy master, genuine transparency, no outline/base/contact shadow.
- `docs/content-registry.md:5–11,20`: derive from canonical facts and avoid unsupported additions or TBD inference.
- `.claude/skills/sit-enemy-sprite/SKILL.md:18–22,24–38,40–44`: no head/torso/eyes means orientation N/A; logical `gridClass` is separate from pixel canvas; request transparency in the actual image-tool argument.
- `assets/images/enemies/M133.webp` and Image 1 were inspected. Both depict exactly one dominant red cap with white flecks and three smaller red-capped mushrooms, four pale stems and separate pale airborne spores. The current candidate's brown/gray radial field is an unwanted background; no soil/moss/wood/forest is needed to identify the enemy.

## Review checklist and evidence

| Check | Evidence | Result |
|---|---|---|
| Exact forms and count | Prompt explicitly preserves the same four forms and their arrangement: one dominant cap and three smaller mushrooms, with red caps/white flecks, pale stems and separate spores. This matches both inspected images. | Pass |
| Spores and anatomy | Separate spores are preserved, consistent with the M133 source row; no poison cloud is requested. It explicitly excludes anatomy and sets orientation N/A, correct for non-anthropomorphic mushrooms. | Pass |
| Background-only scope | The sole change is removal of the brown/gray radial field, glow, halo, matte and other background pixels. It forbids resize, crop, move, redraw and added objects. | Pass |
| Transparency / edge handling | All pixels outside mushroom/spore silhouettes are alpha 0; natural antialiasing is retained directly at edges only. No outline, fringe, halo, shadow or backdrop remains. These statements together allow clean antialiased cutout edges while requiring transparent exterior. | Pass |
| `gridClass` and canvas | Logical `1x1` matches `docs/dungeon-enemies.md:122`; the prompt freezes Image 1's current scale/framing and prohibits resizing/cropping. Image 1 is 1536×1024; no new pixel canvas or box is requested because this operation is deliberately background-only. | Pass |
| Location and unsupported details | Location and encounter details are provenance/context only. No map/environment, poison cloud, colored effect, or unresolved attribute/weakness is introduced. | Pass |
| Tool argument | `transparent_background=true` is explicitly requested; actual execution must pass boolean `transparent_background: true`. | Pass at contract stage; invocation check pending |

## Exact prompt reviewed

```text
Edit Image 1 only for background transparency. Produce a new raw PNG candidate; do not alter the canonical asset.
Target: M133 毒キノコ. Canonical row: "M133 | 毒キノコ | 毒と尖り | 湿った林・古い木壁・山の遊園地跡。卯辰山 utatsuyama-sunnyland（一任による決定 2026-10-15、docs/dungeon-enemies.md が正本） | 未定 | 未定 | 未定（胞子で視界や判断を乱す） | 生成済み: assets/images/enemies/M133.webp（採否待ち。透過・胞子つき） | #12". Encounter row: "M133 | 毒キノコ（1x1） | A: 台帳の候補地「湿った林・古い木壁・山の遊園地跡」（L 3-3・4）。E: 胞子で視界や判断を乱す（状態異常の担い手） | — | 雑魚 | 胞子（L 記述） | 絵あり | ◎ | 未定 | 未定". Locations and encounter details are context only; show no map or scene.
Image 1 is the edit target. Preserve its exact four mushroom forms and arrangement, red caps with white flecks, pale stems, separate airborne spores, current scale and framing. The current brown/gray radial field is not part of the enemy and must be removed.
Change only the background: make every pixel outside the four mushroom and spore silhouettes alpha 0. Preserve natural antialiasing directly along the object edges. Remove all brown/gray background, glow, halo, matte, outline, fringe, shadow and backdrop. Keep all four mushrooms and all spores inside the canvas. Do not redraw, resize, crop, move, or add any object. Logical gridClass remains 1x1. No head, torso, eyes or limbs; orientation is N/A.
Set `transparent_background=true`. No soil, moss, grass, roots, wood, forest, scenery, ground, contact shadow, pedestal, poison cloud, colored effect, text, logo, watermark, border, or additional mushroom/object.
```

## Disposition

**Pass for this exact background-extraction prompt at `contract/prompt` stage.** It preserves the exact four forms, their relative arrangement and spores, changes only the background alpha, and prevents resize/crop or unrelated edits. The transparency argument is specified. This narrow pass does not resolve the latest candidate's previously measured scale/coordinate-box overflow; that remains pending and must be measured in a new raw review after the edit. No image was edited or generated.
