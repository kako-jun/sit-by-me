# M102 background-extraction edit contract review — 2026-10-21

- Reviewer: Codex, independent artifact red-team reviewer
- Target: M102 大型ドリル
- Stage: `contract/prompt` only; no edit or generation performed
- Canonical source commit: `64bb973967e41475ef55678e9ce7d10dd413dc4a`
- Prompt reviewed: `/tmp/sit-m102-bg-prompt.txt` (exact text below)
- Image 1 inspected and identified as the blocked edit candidate: `［ローカルパス省略］/exec-93cc91ed-9428-41e2-931f-c82a07a002de.png`, 1536×1024 RGBA, SHA-256 `ce7d1174cea24b4a2833c0667ad4082b4d3f9671eb3e643a18319433850919db`; visible radial brown/gray backdrop is the only targeted change. The machine already has the requested oblique pose and visible components.
- Canonical M102 source: `assets/images/enemies/M102.webp` (adopted); this prompt edits the separate blocked candidate and forbids changing the canonical file.
- Previous reviews: `20261021-M102-edit-contract-prompt.md` (pass); `20261021-M102-raw-image-93cc91ed.md` (blocker: radial background/alpha and box overflow).

## Sources checked

- `docs/monsters.md:101`: M102 is an unmanned large drill; attribute, weakness and role are TBD; `どろだらけ` effect is unresolved and must not change attribute/weakness.
- `docs/monsters.md:208` and `docs/dungeon-enemies.md:200`: canonical logical grid is `2x1`.
- `docs/dungeon-enemies.md:200`: location and soil-learning provenance are context only, not image appearance.
- `docs/art-direction.md:73`: M102 is in the heavy machinery enemy family.
- `docs/assets-policy.md:5,13`: photorealistic-style isolated enemy master with transparent background, no outline, base or contact shadow.
- `docs/content-registry.md:5–11,20`: preserve canonical facts and do not invent unknown appearance/mechanics.
- `.claude/skills/sit-enemy-sprite/SKILL.md:18–22,24–38,40–44`: inanimate orientation anatomy N/A; logical grid differs from pixel dimensions; the actual tool invocation must request transparency.
- The supplied candidate was inspected directly. It has a yellow drill machine, one visible near-side track, forward-facing oval helical bit and side flutes, complete parts, and no person. Its composition/scale/pose are already the desired ones for this particular background-removal pass; a separate review records the broad background glow and bounds failures.

## Review checklist and evidence

| Check | Evidence | Result |
|---|---|---|
| Scope limited to background | Prompt opens with “only for background transparency,” then explicitly requires machine pixels, camera, pose, scale and framing unchanged. It names the radial field as the target and explicitly bans crop/redraw. No unrelated appearance changes are requested. | Pass |
| Identity and canonical facts | M102 identity and canonical record are quoted; technique, location and unknowns are contextual only. It does not add attribute, attack, effect or new machine part. | Pass |
| Pose and part inventory | Prompt identifies the candidate's correct front-right 45° view, one visible near-side continuous track, oval helical-bit front and flutes, complete parts and no person; it explicitly freezes these. `gridClass 2x1` matches canonical rows. | Pass |
| Background alpha requirements | Radial brown/gray background is to be removed; outside the actual machine silhouette must become alpha 0, with clean antialiasing and no glow, halo, matte, outline, fringe, shadow or other background pixels. This directly addresses the prior candidate failure. | Pass |
| Canvas/framing | Image 1 is the 1536×1024 candidate; prompt expressly preserves its framing, scale and machine pixels while requesting only alpha/background extraction. It does not request an alternate canvas, crop, enlargement or pose change. | Pass |
| Tool transparency | `transparent_background=true` is explicitly requested. The actual image tool call must set boolean `transparent_background: true`. | Pass at contract stage; invocation check pending |

## Exact prompt reviewed

```text
Edit Image 1 only for background transparency. Produce a new raw PNG candidate; do not alter the canonical asset.
Target: M102 大型ドリル. Canonical row: "M102 | 大型ドリル | 圧倒的な機械・物 | 海外 密集垂直都市（青年後半）（kako-jun 承認 2026-10-15、docs/enemy-allocation.md §1.7） | 未定 | 未定 | 未定 | 生成済み: assets/images/enemies/M102.webp（採用: kako-jun 2026-10-14。右向き・透過・無人） | #12。技: どろだらけ（土のラーニング元。2026-10-15 kako-jun 決定。敵の専用 [特技]。効果・ダメージは未決。属性欄・弱点は変えない）". Encounter row: "M102 | 大型ドリル（2x1） | A: 建設の街（EA 1.7、L 固定）。C: 土の元。F: 2x1 | どろだらけ | 雑魚 | 未定 | 絵あり | ◎（固定） | 未定 | 不可（同上）". Location and skill are context only; do not depict them.
Image 1 is the edit target. It already has the correct yellow drilling machine identity, one visible near-side continuous track, front-right oblique yaw 45° (camera front 0°, image-right side profile 90°), visible oval forward face of the helical drill and side flutes, full parts, and no person. Preserve the machine pixels, camera, pose, scale, and framing unchanged.
Change only the background: remove the radial brown/gray field around the machine and make every pixel outside its silhouette fully transparent (alpha 0). Keep a clean natural antialiased silhouette with no glow, halo, matte, outline, fringe, shadow or other background pixels. Do not crop or redraw any part of the machine. Logical gridClass is 2x1.
Set `transparent_background=true`. No added or removed machine parts, no text, logo, road, ground, scene, attack, magic or additional objects.
```

## Disposition

**Pass for this exact background-extraction prompt at `contract/prompt` stage.** It is tightly limited to removing the failed radial backdrop and changing its alpha while preserving the candidate's already accepted pose, scale, framing and part pixels. Its canonical identity/grid are consistent; no unrelated change or unsupported visual detail is requested. This narrow pass does not resolve the prior raw candidate's scale/coordinate-box failure; that remains pending and must be checked again after the edit. At execution, pass Image 1 as the actual edit reference and set boolean `transparent_background: true`. This review does not edit or generate an image; a new raw-image review remains required.
