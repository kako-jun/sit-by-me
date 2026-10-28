# M101 edit/re-render contract review — 2026-10-21

- Reviewer: Codex, independent artifact red-team reviewer
- Target: M101 ロードローラー
- Stage: `contract/prompt` only; no image edit or generation performed
- Canonical source commit: `64bb973967e41475ef55678e9ce7d10dd413dc4a`
- Prompt reviewed: `/tmp/sit-m101-edit-prompt.txt` (exact text below)
- Supplied edit reference inspected: `［ローカルパス省略］/exec-e63460aa-374d-41a0-8e7f-a234a1ffa7b8.png`, 1536×1024 RGBA, SHA-256 `571afcaaed12f481c442c7f825d64e3a9920981588ebb26cc89682f0bee021a4`; its road-roller identity, parts, view, paint and machine-top snow are reference-only. Its oversized composition, glow/background and alpha residue are explicitly rejected.
- Canonical image inspected: `assets/images/enemies/M101.webp`, 640×393 WebP; SHA-256 `4ad83ad1fdcf0db8400c332d97fc28964ea69e13dc571b66f3387341273ad6b6`.
- Prior reviews: `20261021-M101-retry2-contract-prompt.md` (pass); `20261021-M101-raw-image-e63460aa.md` (blocker: oversized, margins insufficient, alpha reaches left/bottom edges).

## Sources checked

- `docs/monsters.md:100`: M101 is ロードローラー; location and material context; attribute/weakness TBD; adopted canonical image is right-facing, transparent and unmanned. Its dedicated `どろだらけ` ability has unresolved effects and must not change the attribute or weakness.
- `docs/monsters.md:207`: M101 current logical `gridClass` is `2x1`; `:255` labels the legacy 1x1 image footprint as historical.
- `docs/dungeon-enemies.md:88`: encounter row independently confirms `2x1`; location, 土 learning provenance and rare high-gold reward are not visual instructions.
- `docs/art-direction.md:3–5,71–74`: winter is the setting vocabulary; M101 belongs to heavy machinery; drivers are not depicted.
- `docs/assets-policy.md:5,13`: photorealistic-style isolated enemy master; transparent background, no outline, pedestal or contact shadow.
- `docs/content-registry.md:5–11,20`: derive the image prompt from canonical rows and relevant policies; do not invent image facts or turn unresolved fields into claims.
- `.claude/skills/sit-enemy-sprite/SKILL.md:18–22,24–38,40–44`: yaw convention is front 0°, true image-right profile 90°, target 45°; head/eyes are N/A for this inanimate machine; `gridClass` is logical occupancy; actual tool call must request transparency.
- The supplied retry2 pixels visibly show one yellow road roller with steel front drum, rear tire, empty cabin, exhaust, frame, snow on upper machine surfaces and the forward drum's curved surface/end face. Its 45° front-right presentation was accepted in the prior raw review; its scale, radial glow/background and low-level alpha residue failed. The edit prompt keeps the accepted view and named parts while explicitly removing those failed traits.

## Review checklist and evidence

| Check | Evidence | Result |
|---|---|---|
| Identity and part preservation | Prompt keeps one yellow roller and names the front drum, near side/front planes, cabin, rear tire, exhaust and frame, all visible in the candidate. “Do not alter the machine's part inventory” preserves the complete same machine without adding components. | Pass |
| Source-supported appearance | Yellow road roller, worn paint, steel drum, tire, cabin, exhaust and frame are present in M101 imagery; light snow on top surfaces is visible in the reference and fits the winter road setting. No driver is added. | Pass |
| Unknown effects / map provenance | Ability/reward/location are explicitly context only and banned from depiction. Attribute/weakness remain unresolved in source and are not asserted in prompt. | Pass |
| Orientation | Defines camera-front 0°, true image-right profile 90°, target yaw 45°. Preserves the already-reviewed oblique view with front drum leading at image-right and positively describes curved drum surface plus circular end together with near cabin/chassis. | Pass |
| `gridClass` | Logical `2x1` is explicit and agrees with `docs/monsters.md:207` and `docs/dungeon-enemies.md:88`. | Pass |
| Fixed frame / scale fit | Inclusive x=307…1228 is 922 px (60.0% of 1536); y=205…818 is 614 px (60.0% of 1024). Centered margins are 20% on each horizontal side and each vertical side. The prior machine silhouette's core bbox ratio is about 1.49; the target box ratio is about 1.50, so a uniform downscale can fit the complete silhouette. The prompt constrains every part and all nonzero alpha to that same box, making object and transparency bounds consistent. | Pass |
| Removal of prior alpha/background defects | Prompt requires alpha exactly 0 across the remainder of the canvas with only direct edge antialiasing, excludes dark/radial backdrop, glow, halo and fringe, and bounds all nonzero-alpha pixels. These are the exact prior failure modes and can be removed without changing the machine parts or its accepted camera view. | Pass |
| Crop and exclusions | Exhaust, cabin, tire and drum are explicitly required fully visible. Road, scenery, shadow, text, logo, driver, mud, magic and extra objects are prohibited, consistent with the isolated asset policy and canonical unknowns. | Pass |
| Tool transparency | Prompt states `transparent_background=true`; actual invocation must set boolean `transparent_background: true`. | Pass at contract stage; invocation check pending |

## Exact prompt reviewed

```text
Mode: reference-based re-render/edit of the supplied M101 candidate; create a new raw PNG candidate, do not alter the canonical asset.
Target: M101 ロードローラー. Canonical record: "M101 | ロードローラー | 圧倒的な機械・物 | 雪国の道路（フィールド・章は未定）。寺町 wide-road（広い道路）（一任による決定 2026-10-15、docs/dungeon-enemies.md が正本） | 未定 | 未定 | 未定 | assets/images/enemies/M101.webp（右向き・透過・運転者なし。2026-10-14 採用） | #12。技: どろだらけ（土のラーニング元。2026-10-15 kako-jun 決定。敵の専用 [特技]。効果・ダメージは未決。属性欄・弱点は変えない）". Encounter row: "M101 | ロードローラー（2x1。EA は大型扱い） | A: wide-road＝主道路（EA 1.1、L「雪国の道路」）。C: 土の元（EA 2.2、LS 68 の最早）。H: 高額ゴールド（めったに出ない。案を採用。§4.4） | どろだらけ | 雑魚 | 未定 | 絵あり | ◎ | 高額ゴールド（レア） | 可（拠点。再訪できる。MT 7.2）". Location, ability and reward are context only; do not draw scenery, currency, attack, magic or effects.
Image 1 is the previously generated blocked M101 candidate. Preserve its correct yellow road-roller identity, front drum on image-right, near side and front end planes, cabin, rear tire, exhaust, frame, worn paint, and light snow on the machine. It already has the correct 45° front-right view and no driver. Recompose the same complete machine at smaller scale. Do not retain any background/glow or edge residue.
Orientation: camera-facing front=0°, true image-right profile=90°, target machine yaw=45°. Preserve the current front-right oblique view, with the front steel drum leading on image-right and its curved rolling surface plus circular end visible.
Canvas and grid: Output 1536×1024 landscape with logical gridClass `2x1`. Place the whole machine inside x=307…1228 and y=205…818 inclusive. Scale it down and center it inside that box. All machine parts and all nonzero-alpha pixels must remain in the box. Keep the full exhaust, cabin, tire and drum visible.
Tool and exclusions: Set `transparent_background=true`. Keep alpha exactly 0 over the rest of the canvas; neutral antialiasing is allowed only directly against the machine edge. No dark/radial backdrop, glow, halo, outline, fringe, shadow, ground plane, road, scenery, text, letters, logo, watermark, driver, person, currency, mud, magic or extra object. Do not crop or alter the machine's part inventory.
```

## Disposition

**Pass for this exact prompt at `contract/prompt` stage.** It preserves the source-supported machine and the already-reviewed front-right 45° view while directly fixing the retry2 size, out-of-bounds alpha and glow/background failures. Its fixed coordinate box and alpha requirement are compatible and leave 20% margins on all sides. At execution, use the supplied retry2 candidate as reference and set actual `transparent_background: true`. No image was generated or modified; raw-image review remains required.
