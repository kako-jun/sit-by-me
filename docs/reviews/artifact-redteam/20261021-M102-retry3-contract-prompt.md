# M102 retry3 contract/prompt review — 2026-10-21

- Reviewer: Codex, independent artifact red-team reviewer
- Target: M102 大型ドリル
- Stage: `contract/prompt`; no image generated
- Canonical source commit: `64bb973967e41475ef55678e9ce7d10dd413dc4a`
- Prompt reviewed: `/tmp/sit-m102-retry3-prompt.txt` (verbatim below)
- Image 1 inspected: prior edited M102 candidate `/home/kako-jun/.codex/generated_images/01a15ccc-868c-7f60-8889-229de4286e8f/exec-93cc91ed-9428-41e2-931f-c82a07a002de.png`, 1536×1024; identity/parts reference only. Its radial background, near-profile pose, oversized composition and second visible track are explicitly rejected.
- Canonical image inspected: `assets/images/enemies/M102.webp`, 640×271 WebP.

## Source checks

- `docs/monsters.md` M102 row (line 101): large drill; attribute, weakness and role unspecified; unmanned, right-facing and transparent; dedicated `どろだらけ` technique is context only and its effect/damage are unresolved.
- `docs/monsters.md` §4 M102–M103 (line 208): logical `2x1`.
- `docs/dungeon-enemies.md` M102 encounter row (line 200): `大型ドリル（2x1）`, construction-city location and earth-learning context; regular enemy; no additional visual fact.
- `docs/art-direction.md` §「圧倒的な機械・物」 and §「敵素材」: isolated machine enemy, +x-facing; no driver/person, text or logos.
- `docs/assets-policy.md` §「敵・召喚獣」: transparent isolated cutout, no acrylic frame, pedestal or contact shadow.
- `.claude/skills/sit-enemy-sprite/SKILL.md` orientation/grid/output sections: exact 45° from camera-front 0° to true-right profile 90°; logical grid class must match the row; use transparency in the actual imagegen setting; head/torso checks are N/A for this machine.
- `docs/content-registry.md` §§「共通の運用」「プロンプト組み立て規約」: no inferred location, skill effect or other TBD completion.

The canonical sprite visibly supports a yellow mining/drilling machine, continuous crawler track, rear chassis, hoses/supporting structure, and a helical drill. The supplied candidate adds source-supported machine identity/visible construction cues but also has traits expressly excluded by this prompt. No extra environmental or gameplay detail is imported.

## Checklist

| Check | Evidence | Result |
|---|---|---|
| Subject and source-bounded details | One unmanned yellow tracked mining drill; chassis, articulated support structure, helical bit. Both inspected images support the industrial drill identity and machinery silhouette; rejected candidate-specific background/pose/second track are named and disallowed. | Pass |
| Orientation and bit projection | Defines camera-front=0°, true-right profile=90°, target 45° toward +x. Requires the oval forward face and side flutes simultaneously plus near-side machine plane. These are compatible at the requested three-quarter view. | Pass |
| Track visibility | Exactly one visible continuous near-side track is required; the far-side track is occluded, not deleted from the machine. This resolves the previous candidate's extra visible track without claiming the real vehicle is single-track. | Pass |
| TBD/context | Location, dirt technique and its unsettled effect stay metadata-only; no magic, attack, attribute or weakness is added. | Pass |
| Grid/framing | `gridClass 2x1` matches both canonical registries. Fixed 1536×1024 landscape canvas and fully-inside/no-crop instruction are compatible; no arbitrary coordinate box is imposed. | Pass |
| Transparency and exclusions | Genuine alpha, no background/radial glow/outline/fringe/shadow; actual tool transparency setting is explicitly required. Road, soil, text, person and extra machinery are prohibited. | Pass at contract stage; invocation check pending |

## Exact prompt reviewed

```text
Create a fresh raw PNG candidate for M102 大型ドリル, using Image 1 only for the yellow mining drill identity and machine-part appearance. Do not preserve its background; do not alter the canonical asset.
Canonical row: "M102 | 大型ドリル | 圧倒的な機械・物 | 海外 密集垂直都市（青年後半）（kako-jun 承認 2026-10-15、docs/enemy-allocation.md §1.7） | 未定 | 未定 | 未定 | 生成済み: assets/images/enemies/M102.webp（採用: kako-jun 2026-10-14。右向き・透過・無人） | #12。技: どろだらけ（土のラーニング元。2026-10-15 kako-jun 決定。敵の専用 [特技]。効果・ダメージは未決。属性欄・弱点は変えない）". Encounter row: "M102 | 大型ドリル（2x1） | A: 建設の街（EA 1.7、L 固定）。C: 土の元。F: 2x1 | どろだらけ | 雑魚 | 未定 | 絵あり | ◎（固定） | 未定 | 不可（同上）". Location and skill are context only; do not depict them. No elemental effects.
Exactly one complete unoccupied yellow tracked mining drill. Include one near-side continuous crawler track only, a yellow industrial chassis, articulated support arms and a large forward helical drill bit. Face the drill toward image-right and toward the camera at 45° between camera-front=0° and true-right profile=90°. Show an oval frontal face of the helical bit and its side flutes simultaneously, plus the near-side body plane. The near-side track is clearly visible under the chassis; do not reveal a second far-side track. Use a 1536×1024 landscape canvas. All machine components are complete and inside it; no part is cropped by the image boundary. No operator or person. Logical gridClass 2x1.
Photorealistic natural industrial machine, yellow paint with realistic wear, neutral clear light. Isolated object on genuine transparent background, set transparent_background=true. Draw only the machine silhouette with clean antialiased edges; outside it is fully transparent, with no radial glow, halo, matte, outline, fringe or shadow. No text, logos, road, soil, ground, scenery, additional machinery, attack, magic or effect.
```

## Disposition

**Pass for this exact prompt at `contract/prompt` stage only.** The prompt gives measurable canvas dimensions, fixes the 45° bit/body orientation and single visible near-side track, and excludes the known background and candidate-specific failures. At generation, set the actual imagegen argument `transparent_background: true`. A new raw-image review must still measure alpha and check the bit planes, track count, crop and exclusions. No image was generated or modified by this review.
