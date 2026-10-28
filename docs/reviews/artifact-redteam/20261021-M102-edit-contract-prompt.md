# M102 edit/re-render contract review — 2026-10-21

- Reviewer: Codex, independent artifact red-team reviewer
- Target: M102 大型ドリル
- Stage: `contract/prompt` only; no image edit or generation performed
- Canonical source commit: `64bb973967e41475ef55678e9ce7d10dd413dc4a`
- Prompt reviewed: `/tmp/sit-m102-edit-prompt.txt` (exact text below)
- Supplied edit reference inspected: `［ローカルパス省略］/exec-ab073035-0e2c-4753-a355-04d5729352f8.png`, 1536×1024 RGBA, SHA-256 `919614838e67158aef77594bea093cf7d6a8d89156143d0603405acb6fa46922`; reference-only for yellow drill identity, rear machinery, arm/hoses and helical bit. Its profile-like projection, second visible track, oversized crop, glow/background and alpha residue are explicitly rejected.
- Canonical image inspected: `assets/images/enemies/M102.webp`, 640×271 WebP, SHA-256 `710c7902be52ae82b197aed6c5b1658ff033515f37e6890af851b1a0eb2ba467`.
- Prior reports: `20261021-M102-retry-contract-prompt.md` (pass); `20261021-M102-raw-image-ab073035.md` (blockers: missing drill front plane, second visible track, oversized image/margins, edge alpha).

## Sources checked

- `docs/monsters.md:101`: M102 is an unmanned large drill in the heavy machinery family; attribute, weakness and role remain TBD. `どろだらけ` is its dedicated technique but effects/damage remain unresolved and the attribute/weakness must not change.
- `docs/monsters.md:208`: current logical grid is `2x1`; `:256` records the old footprint as reference.
- `docs/dungeon-enemies.md:200`: encounter row independently sets `2x1`; the construction-city and soil-learning details are context only.
- `docs/art-direction.md:73`: M102 is a heavy machinery enemy.
- `docs/assets-policy.md:5,13`: photorealistic-style isolated enemy image, transparent background, no outline, pedestal or contact shadow.
- `docs/content-registry.md:5–11,20`: appearance and mechanics must be grounded in the canonical row and source pixels; do not turn TBDs into facts.
- `.claude/skills/sit-enemy-sprite/SKILL.md:18–22,24–38,40–44`: camera-front 0°, true image-right profile 90°, target 45°; absent head/eyes/torso are N/A; `gridClass` is logical occupancy; actual tool call must request transparency.
- The canonical and supplied candidate images were inspected. Both support a yellow drilling machine, rear machinery body, articulated arm/hoses, helical steel bit, and one visible near-side crawler track. The candidate's second track is an image-side visible feature that the prompt explicitly excludes; it does not require the machine to have only one physical track. The prompt distinguishes the visible near-side track from the far-side track hidden behind the machine and near track.

## Review checklist and evidence

| Check | Evidence | Result |
|---|---|---|
| Identity / part preservation | The named yellow machine body, rear body, hydraulic hoses/arm, and helical bit are supported by both source images. No new structural component is introduced; one visible near-side track matches the canonical image's visible track. | Pass |
| Unsupported claims / TBDs | Attribute, weakness, role and technique effect are not promoted into appearance. Location and dirt skill are context-only; scenery, attack, magic and effects are excluded. | Pass |
| Exact yaw and drill-end plane | Defines front 0°, right profile 90°, exact forward yaw 45° toward image-right. It positively requires the near-side body/track plane and an oval front aspect of the outer helical flight while retaining visible side flutes, and rejects both pure profile and head-on. At 45° the drill axis can show a foreshortened oval flight end with the helical side simultaneously visible; these requirements are mutually compatible. | Pass |
| One visible crawler track | The near-side track is explicitly required; the far-side track is explicitly occluded behind body/near track. This controls visibility without claiming the actual machine has only one track. The near track/body plane and drill's frontal oval remain visible from the specified 45° view. | Pass |
| `gridClass` | Prompt declares logical `2x1`, matching `docs/dungeon-enemies.md:200` and `docs/monsters.md:208`. | Pass |
| Canvas / object fit | Inclusive box x=307…1228 is 922 px (60% width); y=205…818 is 614 px (60% height), centered with 20% margins on each side. The reference machine silhouette is horizontally elongated; it can uniformly fit this box with room around the bit/body while preserving the 2x1 logical occupancy. All required parts and every nonzero-alpha pixel share the same box, so no contradictory scale rule exists. | Pass |
| Alpha/background correction | Full alpha=0 outside the machine except direct neutral antialiasing; radial glow, halo, edge residue and background are prohibited. This directly addresses the prior alpha/background failure without requiring any mechanical component to be removed. | Pass |
| Framing and exclusions | Drill, rear body, arm, hoses and one visible track must be complete and inside the box. No ground, road, scenery, person, text or effects. | Pass |
| Actual transparency argument | Text specifies `transparent_background=true`; generation must pass the actual boolean tool argument `transparent_background: true`. | Pass at contract stage; invocation check pending |

## Exact prompt reviewed

```text
Mode: reference-based re-render/edit of the supplied M102 candidate into a new raw PNG candidate. Do not alter the canonical asset.
Target: M102 大型ドリル. Canonical row: "M102 | 大型ドリル | 圧倒的な機械・物 | 海外 密集垂直都市（青年後半）（kako-jun 承認 2026-10-15、docs/enemy-allocation.md §1.7） | 未定 | 未定 | 未定 | 生成済み: assets/images/enemies/M102.webp（採用: kako-jun 2026-10-14。右向き・透過・無人） | #12。技: どろだらけ（土のラーニング元。2026-10-15 kako-jun 決定。敵の専用 [特技]。効果・ダメージは未決。属性欄・弱点は変えない）". Encounter row: "M102 | 大型ドリル（2x1） | A: 建設の街（EA 1.7、L 固定）。C: 土の元。F: 2x1 | どろだらけ | 雑魚 | 未定 | 絵あり | ◎（固定） | 未定 | 不可（同上）". Location and skill are context only; no map, city, attack, magic, or effects.
Image 1 is the previously generated blocked M102 candidate. Preserve its yellow industrial drilling machine identity, rear machinery body, hydraulic hoses/arm, and steel helical bit. Re-render the viewpoint and composition. Do not preserve the side-profile camera, second visible track, crop, background glow, or edge residue.
Subject: One unmanned machine. Show one continuous near-side crawler track only; the far-side crawler track must be fully hidden behind the machine body and near track. No person or operator. No head/eyes/humanoid torso; those checks are N/A.
Orientation definition: camera-facing front=0°, true image-right side profile=90°, target forward yaw=45° toward image-right. Drill bit is the leading end on image-right. Show both the machine's near-side body/track plane and the bit's front-facing plane. The helical bit's forward end must show a broad visible oval cross-section of its outer flight as it turns toward the camera, while its helical flutes remain visible along the side. Do not show only a thin pointed side silhouette of the drill tip. Avoid both a 90° side view and a straight-on front view.
Appearance: Photorealistic natural heavy machinery; worn yellow body and aged steel. No stylized outline, glow, rim light, chromatic aberration, color fringe, sticker edge, or drop shadow.
Canvas/grid: Output 1536×1024 landscape, logical gridClass `2x1`. Fit the entire drill, body, arm, hoses and single visible crawler track inside x=307…1228 and y=205…818 inclusive, centered in that box. No component may extend outside the box.
Tool/exclusions: Set `transparent_background=true`. Keep alpha exactly 0 on canvas outside the machine, with neutral antialiasing only directly along the silhouette. No radial backdrop/glow, halo, outline, fringe, ground plane, road, scenery, contact shadow, text, letters, logo, watermark, driver, person, weapon, mud attack, magic or extra object. Do not crop or add machine parts.
```

## Disposition

**Pass for this exact prompt at `contract/prompt` stage.** The single visible near-side track is a visibility/occlusion instruction consistent with the source-supported machine, not a claim of a one-track vehicle. Exact 45° yaw, visible oval helical-flight front plus side flutes, and near-side track plane can coexist. The prompt fixes the former yaw, extra-track, background/alpha and scale findings; the 60% centered box is feasible for this horizontal subject. At generation, use the supplied blocked candidate as the edit reference and pass actual `transparent_background: true`. No image generated or modified; raw-image review remains required.
