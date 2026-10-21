# M101 retry 2 contract/prompt review — 2026-10-21

- Reviewer: Codex, independent artifact red-team reviewer
- Target: M101 ロードローラー
- Stage: `contract/prompt` only; no image generated
- Canonical source commit: `64bb973967e41475ef55678e9ce7d10dd413dc4a`
- Prompt reviewed: `/tmp/sit-m101-retry2-prompt.txt` (exact text below)
- Visual reference inspected: `assets/images/enemies/M101.webp` (640×393 WebP; SHA-256 `4ad83ad1fdcf0db8400c332d97fc28964ea69e13dc571b66f3387341273ad6b6`), explicitly identity/parts reference only
- Prior reviews: initial contract pass `20261021-M101-contract-prompt.md`; retry 1 major findings `20261021-M101-retry-contract-prompt.md`; raw candidate blocker `20261021-M101-raw-image-481e4a05.md`

## Sources checked

- `docs/content-registry.md` lines 5–11 and 20: prompt must follow canonical enemy row and common policies, not invent unsupported appearance or mechanics.
- `docs/monsters.md` line 100: M101 identity/family/location, TBD attributes and weakness, adopted image, unmanned cue, and `どろだらけ` technique with unresolved effects and explicit instruction not to change attribute/weakness.
- `docs/dungeon-enemies.md` line 88: M101 encounter class `2x1`, large-class treatment, Teramachi wide-road/learning provenance, rare high-gold reward.
- `docs/art-direction.md` lines 3–5 and 71–74: winter setting and heavy-machinery grouping.
- `docs/assets-policy.md` lines 5 and 13: photorealistic-style isolated enemy art, transparent background, no outline/base/contact shadow.
- `.claude/skills/sit-enemy-sprite/SKILL.md` lines 18–22, 24–38, 40–44: defined 0°/90° convention and 45° target; inanimate subject N/A for absent head/eyes; logical gridClass separate from pixel frame; tool must request transparency.
- Reference pixels: the old image shows one yellow road roller, front drum, rear tire, empty cabin, exhaust and frame with snow on upper surfaces in an approximately side-on pose. Prompt assigns it only type/parts identity, explicitly excluding pose, framing, edge treatment, background, and shadow.

## Review checklist and evidence

| Check | Evidence | Result |
|---|---|---|
| Source facts and identity | Exact monster and encounter records are quoted. Listed drum, rear tire, cabin, exhaust and frame match the inspected image's visible parts; the reference is restricted to identity/parts. No extra part is inferred. | Pass |
| Count / occupancy | “Exactly one” machine; logical `gridClass 2x1` matches both canonical records. The canvas ratio is explicitly not used to determine occupancy. | Pass |
| Attribute, weakness, technique, reward | `未定` values are preserved; `どろだらけ` and rare high-gold reward are context only; prompt bans depicting setting, currency, magic, attack and effect. | Pass |
| Angle | Defines camera-facing front = 0°, true image-right side profile = 90°, and exactly 45° between them, facing +x. Drum-leading direction and both curved surface/end face plus near side are specified. This matches skill lines 20–22. | Pass |
| Reference scope | Correctly uses `M101.webp` for machine type and named parts only and rejects the old side-on pose, framing, outline/fringe, background, contact shadow. | Pass |
| Scale / frame compatibility | 3:2 canvas. Silhouette width and height each 55–65%, centered; minimum 17.5% margins on all sides. At the 65% maximum, each remaining dimension has 35% total transparent margin, or 17.5% per side; therefore requested scale and margins are exactly compatible. A 2x1 logical class is independent of those pixel percentages. | Pass |
| Snow / appearance | Light snow on top surfaces is supported by M101's snow-country road placement, art-direction winter setting, and visible snow on the identity reference; a snow scene is explicitly forbidden. | Pass |
| Transparency and negatives | Prompt explicitly requires `transparent_background=true` and genuine outside alpha; bans text, logos, frame, outline/fringe/halo, base, ground, road, setting, shadow, people, attacks, effects, and extra objects. The actual generation call must pass the boolean tool argument `transparent_background: true`. | Pass at contract stage; invocation check pending |

## Exact prompt reviewed

```text
Use case: photorealistic-natural
Asset type: isolated enemy battle master sprite for a Final Fantasy-inspired side-view RPG
Primary request: Recreate M101 ロードローラー as one isolated transparent sprite. Canonical record: "M101 | ロードローラー | 圧倒的な機械・物 | 雪国の道路（フィールド・章は未定）。寺町 wide-road（広い道路）（一任による決定 2026-10-15、docs/dungeon-enemies.md が正本） | 未定 | 未定 | 未定 | assets/images/enemies/M101.webp（右向き・透過・運転者なし。2026-10-14 採用） | #12。技: どろだらけ（土のラーニング元。2026-10-15 kako-jun 決定。敵の専用 [特技]。効果・ダメージは未決。属性欄・弱点は変えない）". Encounter record: "M101 | ロードローラー（2x1。EA は大型扱い） | A: wide-road＝主道路（EA 1.1、L「雪国の道路」）。C: 土の元（EA 2.2、LS 68 の最早）。H: 高額ゴールド（めったに出ない。案を採用。§4.4） | どろだらけ | 雑魚 | 未定 | 絵あり | ◎ | 高額ゴールド（レア） | 可（拠点。再訪できる。MT 7.2）". Location, ability, and reward are context only; depict no setting, currency, magic, attack, or effect.
Reference: Use the existing `assets/images/enemies/M101.webp` only to identify the machine type and its parts (yellow road roller, front drum, rear tire, cabin, exhaust stack, frame). Do not copy its side-on pose, framing, outline/fringe, background, or contact shadow. No additional part may be inferred from the reference.
Subject: Exactly one old yellow road roller. Cabin is empty: no driver, person, or human silhouette. There is no head or eye; head/eye checks are N/A.
Orientation definition: Define object yaw with camera-facing front = 0°, true image-right side profile = 90°. Target machine yaw is exactly 45° between those endpoints, facing toward image-right. The front steel cylindrical drum is the leading end on image-right. Show its curved rolling surface and circular end face together with the near side of the yellow cabin and chassis. Do not show the old flat side pose or a straight-on front view.
Appearance: Photorealistic natural machinery, worn yellow paint, aged steel and light snow resting on top surfaces. No stylized outline, glow, rim light, chromatic aberration, or colored edge treatment.
Canvas and scale: 3:2 landscape transparent canvas. The full machine silhouette occupies 55–65% of canvas width and 55–65% of canvas height, centered in both axes. Leave at least 17.5% empty transparent margin on every side. Keep the drum, tire, cabin and exhaust fully inside the canvas. Logical gridClass is 2x1; canvas dimensions do not determine occupancy.
Lighting: Neutral white light without colored cast around the silhouette.
Constraints: Set `transparent_background=true`. Preserve actual alpha transparency outside the machine. No text, letters, logos, watermark, border, outline, fringe, halo, pedestal, ground plane, road, scenery, contact shadow, snow scene, driver, person, weapon, mud, magic, or extra objects. No nonzero-alpha pixel may touch the canvas edge.
```

## Disposition

**Pass for this exact prompt at `contract/prompt` stage.** Previous retry findings are resolved: angle endpoints are defined and scale now has a lower and upper bound compatible with the minimum margins. The tool instruction specifies transparency; confirm the actual invocation passes `transparent_background: true`. This review does not generate or adopt an image. Raw-image review remains required.
