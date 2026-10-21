# M101 retry contract/prompt review — 2026-10-21

- Reviewer: Codex, independent artifact red-team reviewer
- Target: M101 ロードローラー
- Stage: `contract/prompt` only; no image generated
- Reviewed source commit: `64bb973967e41475ef55678e9ce7d10dd413dc4a`
- Prompt: `/tmp/sit-m101-retry-prompt.txt` (exact text below)
- Existing source asset inspected: `assets/images/enemies/M101.webp` (640×393 WebP; previously adopted source, used for identity/context inspection only; prompt says no input image)
- Prior contract: `docs/reviews/artifact-redteam/20261021-M101-contract-prompt.md` (pass for an earlier, materially different prompt)
- Prior raw candidate review: `docs/reviews/artifact-redteam/20261021-M101-raw-image-481e4a05.md` (blocker: alpha bbox outside the central 80% / margins)

## Canonical evidence

- `docs/content-registry.md` lines 5–11, 20, 30–36: construct prompts from the target row and applicable policy/skill; do not invent unsupported facts; resolve image-affecting TBDs; review the complete prompt before generation.
- `docs/monsters.md` line 100: M101 is a road roller in the “圧倒的な機械・物” family, associated with snow-country roads and Teramachi `wide-road`; attribute, weakness/resistance, and other role details are not fixed. The adopted asset is a yellow-facing, transparent, unmanned M101 image. Its named 土 learning-source technique is `どろだらけ`; effect/damage is unresolved and must not redefine the enemy attribute/weakness.
- `docs/monsters.md` line 207 and `docs/dungeon-enemies.md` line 88: current logical grid is `2x1`; encounter row identifies M101 as a regular enemy, large-class, with rare high-gold reward. Reward and location are context, not objects to depict.
- `docs/art-direction.md` lines 3–5, 71–74: winter is the game-wide setting; road roller belongs to the heavy machinery fear category. `docs/assets-policy.md` lines 5, 13: photorealistic-style isolated enemy sprite; transparent background without outline, base, or contact shadow.
- `.claude/skills/sit-enemy-sprite/SKILL.md` lines 18–22: vehicle/body yaw must use camera-front = 0° and true-right profile = 90°, target 45°; inanimate objects with no head/eyes do not receive invented anatomy checks. Lines 24–38: gridClass is logical occupancy, independent of pixel ratio. Lines 40–44: actual tool must request transparency and canonical source data must be carried into generation.
- Source asset inspected at original size: `assets/images/enemies/M101.webp`, 640×393. It shows a single old yellow roller with one visible cylindrical steel drum at image-right, one visible large rear tire, empty cabin, exhaust stack, and snow on upper surfaces. The prompt's “no input image” avoids copying its profile pose and outline; it asks for conventional roller construction from its canonical identity and record.

## Checks and findings

| Check | Evidence | Result |
|---|---|---|
| Identity, count, components | Prompt requests exactly one unoccupied yellow road roller and names drum, rear tire, cabin, exhaust, and frame; this matches M101 identity and inspected adopted asset. It excludes people and additional objects. | Pass |
| `gridClass 2x1` | Prompt explicitly separates logical `2x1` occupancy from pixel dimensions; canonical rows agree. | Pass |
| Canonical TBD / ability / reward | It does not assign an attribute or weakness. Ability, effect and reward are contextual only, with depiction prohibited. | Pass |
| Snow detail | Small traces on the machine's upper surfaces are consistent with M101's snow-country road placement and the winter-only art direction; prompt prohibits a snow scene/background. | Pass |
| No map/background | It names location/reward/ability only as context and excludes road, scenery, snow scene, ground and contact shadow. | Pass |
| Transparency / exclusions | `transparent_background=true` is specified as a tool argument; alpha, no edge contact, no outline/fringe/halo, and no environment/people/effects are required. The actual generation call must pass this argument. | Pass at contract stage |
| Candidate scale and 2x1 fit | 3:2 landscape canvas; a centered complete machine occupying 65% or less in each axis can fit inside 17% transparent margins on both sides (the margins imply a 66% maximum). Logical 2x1 is explicitly not equated to pixel aspect ratio. | **Major: no lower bound or target scale** |
| Orientation | “yaw exactly 45 degrees toward image-right” gives a numeric angle but omits the required endpoints. The skill's convention is camera-front 0° and true-right profile 90°; “toward image-right” alone does not anchor the rotation. | **Major: angle is not self-contained** |

## Exact corrections required

1. Define the angle in the prompt: “Vehicle forward axis yaw is exactly 45° from camera-front (0°) toward true right profile (90°); image right is +x. Show the drum’s curved rolling surface and its circular end face together with the machine’s near side.”
2. Define a scale interval or target in addition to maximum margins. For example: “Centered machine alpha bounds occupy 60–65% of canvas width and 58–65% of canvas height; at least 17% of each canvas dimension remains transparent at both opposing edges.” This interval is compatible with a road roller silhouette near the inspected source's 1.53:1 ratio on a 3:2 canvas. (The present “no more than 65%” allows arbitrarily small output subjects.)
3. Continue to use `transparent_background: true` as the actual imagegen argument.

## Exact prompt reviewed

```text
Use case: photorealistic-natural
Asset type: isolated enemy battle master sprite
Primary request: Draw M101 ロードローラー, a single old yellow construction road roller, on a true transparent canvas. Canonical data: M101 is a road roller, classification "圧倒的な機械・物", in a snow-country road chapter at Teramachi wide-road; its attribute and weakness/resistance are TBD. It can use the named ability どろだらけ, but its effect is unresolved. The encounter record assigns `2x1`, calls it a large-class enemy, and records rare high gold. These location, reward, attribute, and ability details are context only; depict no setting, money, attack, magic, or effect.
Subject: Exactly one unoccupied yellow road roller with a front steel cylindrical drum, one rear rubber tire, cabin, exhaust stack, and construction frame. The cabin is empty. No person, driver, or human silhouette. The machine has no head or eyes, so head/eye orientation is N/A.
Orientation: Vehicle forward axis yaw exactly 45 degrees toward image-right. The front drum leads on image-right. Show its curved rolling surface and one circular end face; also show the near side of the yellow chassis and cabin. Avoid a flat 90-degree side view and avoid a head-on view.
Appearance: Photorealistic natural machinery with worn yellow paint, aged steel and only small traces of snow on the machine's upper surfaces. No stylized outline, glow, rim light, chromatic aberration, or colored edge treatment.
Canvas and scale: Use a 3:2 landscape transparent canvas. Center the complete machine. The visible machine including exhaust, tire and drum must occupy no more than 65% of canvas width and no more than 65% of canvas height. Leave at least 17% of canvas width empty on the left and right and 17% of canvas height empty at the top and bottom. All transparent margins must remain empty. This is a logical `2x1` enemy; the pixel dimensions do not define its grid occupancy.
Lighting: Neutral white light. Do not cast colored light onto the transparent perimeter.
Tool and exclusions: Set `transparent_background=true`. Do not use an input image. Preserve alpha transparency outside the machine. No text, letters, logos, watermark, border, outline, fringe, halo, pedestal, ground plane, road, scenery, contact shadow, snow scene, person, driver, weapon, dirt/mud attack, magic, or additional object. No part of the machine or nonzero-alpha pixel may touch the canvas edge.
```

## Disposition

**Major findings remain; do not generate from this prompt.** The 2x1 occupancy and full-machine margins can coexist, but the maximum-only scale leaves subject size unbounded below, and the 45° direction lacks the skill's explicit camera-front / true-right endpoints. Resolve those two fields and request a new contract review. No image was generated or modified.
