# M102 contract/prompt review — 2026-10-21

- Reviewer: Codex, independent artifact red-team reviewer
- Target: M102 大型ドリル
- Stage: `contract/prompt` only; no image generated
- Reviewed source commit: `64bb973967e41475ef55678e9ce7d10dd413dc4a`
- Prompt source: `/tmp/sit-m102-prompt.txt` (exact text reviewed below)
- Existing image reference inspected: `assets/images/enemies/M102.webp`, WebP 640×271, SHA-256 `710c7902be52ae82b197aed6c5b1658ff033515f37e6890af851b1a0eb2ba467`

## Canonical evidence

- `docs/content-registry.md` lines 5–11, 20, 30–36: generation must derive from the canonical target row, common asset policy and type skill; do not add unsupported appearance facts; unresolved TBD blocks only if it affects what the image depicts.
- `docs/monsters.md` line 101: M102 is “大型ドリル”, family “圧倒的な機械・物”, location “海外 密集垂直都市（青年後半）”; attribute, weakness/resistance and role are `未定`; current adopted image is `assets/images/enemies/M102.webp` and records right-facing, transparent, unmanned. The row separately records `どろだらけ` as the 土 learning-source special technique and explicitly says not to change the attribute or weakness fields.
- `docs/dungeon-enemies.md` line 200: M102 is a regular enemy with `gridClass 2x1`; encounter context lists the location as construction town (EA 1.7), learning role, and fixed 2x1 footprint.
- `docs/assets-policy.md` lines 5, 13: enemy sprites are photorealistic-style isolated transparent assets; no acrylic outline, base or contact shadow.
- `.claude/skills/sit-enemy-sprite/SKILL.md` lines 18–22, 24–38, 40–44: yaw convention is camera-front 0°, true right profile 90°, target 45°; inanimate objects have head/torso/eyes checks N/A; gridClass is logical occupancy; actual imagegen tool must request transparency; all row facts and prohibitions must be carried into the generation input.
- Old image inspection: the asset visibly depicts one unmanned, yellow, weathered tracked drilling machine, with a large front helical bit, articulated support/arm structure and hoses. Its visible orientation is close to a side view. This image can inform object identity only; it does not authorize copying its current profile pose.

## Checks and findings

| Check | Evidence | Result |
|---|---|---|
| ID / species identity / count | Prompt names M102, 大型ドリル, and requests one machine; source row identifies the same machine. | Pass |
| `gridClass` | Prompt says `2x1`; encounter row line 200 says 大型ドリル（2x1） and F: 2x1. | Pass |
| Element / weakness / technique | Prompt does not assign an element or weakness. It treats location, ability and learning information as context and bans depicting the mud attack/effects. This matches the row’s `未定` fields and the distinct 土 technique. | Pass |
| Map provenance only | Prompt explicitly says location, ability, and learning information are context only and prohibits map, road and environment. | Pass |
| Transparency / exclusions | Prompt requires the actual tool argument `transparent_background=true`, genuine alpha, and excludes text, marks, base, shadow, ground, road, scenery, people and effects. Skill requires the tool setting as well as visual alpha; the stated argument is the correct invocation requirement. | Pass at contract stage; invocation must actually use it |
| Style | “Photorealistic natural heavy machinery” matches assets-policy.md line 5. | Pass |
| Orientation | It says “exactly 45 degrees toward image-right,” but does not define the two reference endpoints. The skill defines the required measurable convention as camera-front = 0° and true-right profile = 90° (`SKILL.md` line 20). Without those endpoints, “45 degrees” can be interpreted as a 45° turn from several different starting axes. | **Major** |
| Source-image identity | Prompt explicitly says “No input image,” while the identity-specific machine details are visually established by the currently adopted M102 image. With no image supplied, generation has no visual source for the same model’s yellow body, drill/arm/track arrangement, or hose layout; the text list is an interpretation and cannot ensure the same asset identity. The existing image is already adopted, so a replacement needs an explicit reference role and pose override. | **Major** |
| Unsupported details / TBD | “two continuous steel crawler tracks” is more specific than the canonical row and the inspected side-view image visibly establishes only the near-side continuous track. Other construction details in the prompt also come from the old image rather than a separately cited canonical appearance specification. Attribute/weakness/role remain unassigned. | **Major** |
| Crop / margin | Central 80% and 10% transparent margin constraints are numerically consistent; all named machine parts are required inside those bounds. | Pass |

## Exact corrections required

1. Replace `No input image.` with the supplied old image `assets/images/enemies/M102.webp`, explicitly labeled **identity/mechanical-layout reference only**. Add: “Do not copy its side-profile pose; redesign the whole machine to the specified 45° view.”
2. Make the orientation self-contained: “Machine forward axis yaw is exactly 45° from camera-front (0°) toward true right profile (90°); image right is +x. Show the circular drill-bit front face and near side of the machine together.”
3. Remove the unsupported demand for “two continuous steel crawler tracks.” Ground other model-specific details as reference-derived, not canonical facts: say to preserve only the machine identity and visible mechanics from the attached reference, with no invented additional components. If a far-side track must be depicted, state it as an inferred hidden component and avoid requiring extra visible track detail.
4. Keep `transparent_background=true` as the actual `imagegen` tool argument at generation time, not merely text in the prompt.

## Exact prompt reviewed

```text
Use case: photorealistic-natural
Asset type: single enemy battle master sprite for a Final Fantasy-inspired side-view RPG
Primary request: Recreate M102 大型ドリル as one isolated transparent sprite. Canonical record: "M102 | 大型ドリル | 圧倒的な機械・物 | 海外 密集垂直都市（青年後半）（kako-jun 承認 2026-10-15、docs/enemy-allocation.md §1.7） | 未定 | 未定 | 未定 | 生成済み: assets/images/enemies/M102.webp（採用: kako-jun 2026-10-14。右向き・透過・無人） | #12。技: どろだらけ（土のラーニング元。2026-10-15 kako-jun 決定。敵の専用 [特技]。効果・ダメージは未決。属性欄・弱点は変えない）". Encounter row: "M102 | 大型ドリル（2x1） | A: 建設の街（EA 1.7、L 固定）。C: 土の元。F: 2x1 | どろだらけ | 雑魚 | 未定 | 絵あり | ◎（固定） | 未定 | 不可（同上）". Location, ability, and learning information are context only. Do not depict a map, road, environment, attack, magic, currency, or effect.
Subject: One massive unmanned tracked industrial drilling machine: old yellow machinery body, two continuous steel crawler tracks, articulated support arm, hydraulic hoses, and a large helical metal drill bit at the front. No operator or person. This machine has no head, eyes, or humanoid torso; those orientation checks are N/A.
Orientation: Machine's forward axis yaw exactly 45 degrees toward image-right. Drill-bit end is the leading end on image-right. Show the circular front face and helical flutes of the drill bit plus the near side of its tracked chassis, arm, and machinery body. Avoid a flat 90-degree side profile and avoid a head-on view.
Style: Photorealistic natural heavy machinery with worn yellow paint, aged steel, and realistic hydraulic details. No stylized outline, glow, rim light, or chromatic aberration.
Composition: One complete machine in logical gridClass 2x1, centered and fully visible. Keep entire drill bit, rear chassis, crawler tracks, hoses, and arm within the central 80% of canvas with at least 10% transparent margin on all four sides.
Lighting: Neutral white lighting; no colored edge cast.
Constraints: Set transparent_background=true in the image-generation tool. No input image. Genuine alpha transparency outside the machine. No text, letters, logos, watermark, border, outline, fringe, halo, ground plane, road, scenery, contact shadow, driver, person, weapon, dirt/mud attack, magic, or additional objects. No cropping or touching canvas edges with opaque or partially transparent pixels.
```

## Disposition

**Major findings remain; contract does not pass.** Do not generate from this prompt. Correct the angle baseline, provide the existing M102 image with a reference-only identity role and explicit pose override, and remove or qualify the track-count assertion. Re-review the corrected complete prompt before generation. This report does not change the adopted image or its status.
