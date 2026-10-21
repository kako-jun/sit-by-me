# M102 retry contract/prompt review — 2026-10-21

- Reviewer: Codex, independent artifact red-team reviewer
- Target: M102 大型ドリル
- Stage: `contract/prompt` only; no image generated
- Canonical source commit: `64bb973967e41475ef55678e9ce7d10dd413dc4a`
- Prompt reviewed: `/tmp/sit-m102-retry-prompt.txt` (exact text below)
- Visual reference inspected: `assets/images/enemies/M102.webp` (640×271 WebP; SHA-256 `710c7902be52ae82b197aed6c5b1658ff033515f37e6890af851b1a0eb2ba467`), explicitly identity/mechanical-components reference only
- Prior contract with major findings: `docs/reviews/artifact-redteam/20261021-M102-contract-prompt.md`

## Sources checked

- `docs/content-registry.md` lines 5–11, 20: prompt must follow canonical enemy row and common policies, avoid unsupported facts, and preserve relevant source details.
- `docs/monsters.md` line 101: M102 is 大型ドリル in family 圧倒的な機械・物, at the overseas dense vertical city; attribute, weakness/resistance and role are `未定`. The current adopted image is the unmanned, transparent M102 asset. The distinct 土 technique is `どろだらけ`; its effect/damage are unresolved and attribute/weakness must not change.
- `docs/dungeon-enemies.md` line 200: M102 is a regular enemy with logical `2x1` class. It cites construction-town placement and 土-learning provenance as encounter context.
- `docs/assets-policy.md` lines 5 and 13: photorealistic-style isolated enemy sprite; transparent background without outline, base, or contact shadow.
- `.claude/skills/sit-enemy-sprite/SKILL.md` lines 18–22, 24–38, 40–44: angle baseline is camera front 0°, true right profile 90°, desired yaw 45°; no-head/eyes/torso N/A for this machine; gridClass is logical and independent of pixel frame; imagegen must actually request transparency.
- Reference pixels: the existing M102 image depicts a yellow industrial drilling rig with a large helical bit, articulated support structure and hoses, and one visible near-side continuous crawler track. It is almost side-on. The prompt confines reference use to identity and listed components, rejects the old pose/framing/edges/background/shadow, and does not require a second visible crawler track.

## Review checklist and evidence

| Check | Evidence | Result |
|---|---|---|
| Identity and reference scope | The named large yellow tracked drill form and visible components (body, near-side track, support arm/hoses, helical bit) are present in the inspected source image. Prompt explicitly restricts reference to identity/components and rejects its side pose, framing, edge treatment, background and shadow. | Pass |
| Count / gridClass | Exactly one machine; `gridClass 2x1` is explicit and matches `docs/dungeon-enemies.md:200`. | Pass |
| Source facts / TBDs | Canonical row is quoted verbatim. Attributes and weakness remain `未定`; `どろだらけ` is context-only and the prompt prohibits attack/effect/magic depiction. | Pass |
| Angle | Defines object yaw from camera-facing front 0° to true image-right side profile 90°, sets exactly 45° toward image-right, and positively specifies bit front face + helical flutes with near-side track/body. Prohibits both side-on and head-on results. Matches skill lines 20–22. | Pass |
| Inanimate anatomy | Correctly says no head, eyes, or humanoid torso and sets those checks N/A, without adding anatomy. The machine forward-axis yaw still has a separate explicit requirement. | Pass |
| Scale / frame compatibility | 3:2 landscape; silhouette width 55–65%, height 45–65%, centered, with ≥17.5% margins on all sides. The 65% maxima leave exactly 17.5% at each opposing edge, so the bounds are compatible. These are pixel-frame composition bounds; `2x1` remains logical occupancy. | Pass |
| Environment / prohibited additions | Location/skill are context only; prompt excludes map/city, ground, road, scenery, shadow, people, weapons, attack, effects and extra objects. | Pass |
| Transparency | Prompt explicitly says `transparent_background=true` and requires actual alpha. This is the correct tool-setting instruction; the eventual imagegen invocation must pass boolean `transparent_background: true`. | Pass at contract stage; invocation check pending |

## Exact prompt reviewed

```text
Use case: photorealistic-natural
Asset type: isolated enemy battle master sprite for a Final Fantasy-inspired side-view RPG
Primary request: Recreate M102 大型ドリル as one isolated transparent sprite. Canonical record: "M102 | 大型ドリル | 圧倒的な機械・物 | 海外 密集垂直都市（青年後半）（kako-jun 承認 2026-10-15、docs/enemy-allocation.md §1.7） | 未定 | 未定 | 未定 | 生成済み: assets/images/enemies/M102.webp（採用: kako-jun 2026-10-14。右向き・透過・無人） | #12。技: どろだらけ（土のラーニング元。2026-10-15 kako-jun 決定。敵の専用 [特技]。効果・ダメージは未決。属性欄・弱点は変えない）". Encounter record: "M102 | 大型ドリル（2x1） | A: 建設の街（EA 1.7、L 固定）。C: 土の元。F: 2x1 | どろだらけ | 雑魚 | 未定 | 絵あり | ◎（固定） | 未定 | 不可（同上）". Location and skill are context only; depict no map, city, attack, magic, or effect.
Reference: Use existing `assets/images/enemies/M102.webp` only to identify its large yellow tracked drill form and visible components (yellow machinery body, near-side crawler track, hydraulic support arm and large helical steel bit). Do not copy its flat side-on pose, framing, outline/fringe, background, or contact shadow. Do not add a second visible crawler track if the reference perspective does not show it.
Subject: Exactly one unoccupied industrial tracked drilling machine with yellow machinery body, one visible near-side continuous steel crawler track, hydraulic hoses/support arm, and a large helical steel drill bit. No operator or person. It has no head, eyes, or humanoid torso; those checks are N/A.
Orientation definition: Define object yaw with camera-facing front = 0°, true image-right side profile = 90°. Target machine yaw is exactly 45° between those endpoints, facing toward image-right. The drill-bit end leads on image-right. Show the circular front face and helical flutes of the bit together with the near-side crawler track and machinery body. Avoid the old flat side pose and a straight-on head-on view.
Appearance: Photorealistic natural heavy machinery with worn yellow paint, aged steel, and visible hydraulic details. No stylized outline, glow, rim light, chromatic aberration, or colored edge treatment.
Canvas and scale: 3:2 landscape transparent canvas. The complete machine silhouette occupies 55–65% of canvas width and 45–65% of canvas height, centered in both axes. Leave at least 17.5% transparent margin on every side. Keep the drill bit, rear chassis, visible crawler track, hoses and arm inside the canvas. Logical gridClass is 2x1; pixel dimensions do not determine grid occupancy.
Lighting: Neutral white light without colored cast around the silhouette.
Constraints: Set `transparent_background=true`. Preserve alpha transparency outside the machine. No text, letters, logos, watermark, border, outline, fringe, halo, ground plane, road, scenery, contact shadow, driver, person, weapon, dirt/mud attack, magic, or extra objects. No nonzero-alpha pixel may touch the canvas edge.
```

## Disposition

**Pass for this exact prompt at `contract/prompt` stage.** The prior findings are resolved: the reference has a declared identity-only role, visible parts are grounded in its pixels, two-track overclaim is removed, the angle baseline is complete, and size/margins fit. The transparency instruction is present; verify the actual imagegen call uses `transparent_background: true`. This does not generate or adopt an image. Raw-image review remains required.
