# M104 contract/prompt review — 2026-10-21

- Reviewer: Codex, delegated independent reviewer (not the prompt author)
- Target: M104 乱暴な自転車
- Stage: `contract/prompt`
- Verdict: **pass for this exact prompt revision**
- Canonical base: `64bb973967e41475ef55678e9ce7d10dd413dc4a`
- Reference inspected, reference-only for bicycle identity, wear/color and parts: `assets/images/enemies/M104.webp`, 640×418 WebP with alpha; SHA-256 `5a18c6801cde0341238beff09b216a60a4c368a2a767c45df03bd82cb8841285`
- No image was generated.

## Canonical sources inspected

- `.claude/skills/sit-artifact-redteam/SKILL.md`, enemy prompt-review criteria and findings/disposition requirements
- `.claude/skills/sit-enemy-sprite/SKILL.md`, §§12, 14–22, 24–47
- `docs/content-registry.md`, enemy index and prompt assembly rules
- `docs/monsters.md:103` (M104 source row), `:209` (current grid class), `:258` (legacy image footprint)
- `docs/dungeon-enemies.md:90` (encounter source row), `:275` (allocation rationale)
- `docs/art-direction.md:70–75` and §“イマジナリー敵” (traffic and noise fear category)
- `docs/assets-policy.md:3–5,13` (photorealistic generated enemies; transparent isolated enemy master without outline/base/shadow)
- Actual pixels of `assets/images/enemies/M104.webp`
- Complete prompt from `/tmp/sit-m104-prompt.txt`

## Complete prompt reviewed

> Use case: photorealistic-natural
>
> Asset type: single enemy battle master sprite for a Final Fantasy-inspired side-view RPG
>
> Primary request: Recreate M104 乱暴な自転車 as an isolated transparent sprite. Canonical enemy record: "M104 | 乱暴な自転車 | 交通と騒音 | 寺町 hinomi-bend（弧の道）（一任による決定 2026-10-15、docs/dungeon-enemies.md が正本） | 未定 | 未定 | 未定 | 生成済み: assets/images/enemies/M104.webp（採否待ち。右向き（前輪が右）・透過・無人） | #12、art-direction.md". Encounter source row: "M104 | 乱暴な自転車（2x1） | A: hinomi-bend＝見通しの悪い曲がり角（EA 1.1）。H: 救済＝無属性ダメージ魔法のラーニング元（案。寺町の弱い敵。learning-schedule.md §1b） | （案）無属性ダメージ魔法 | 雑魚 | 未定 | 絵あり | △ | 未定 | 可（拠点。再訪できる。MT 7.2）". The location and learning-role information provide context only; do not depict a map, scene, magic, or effects.
>
> Input image: Image 1 is the existing M104 bicycle sprite. Use it only to preserve bicycle identity, worn blue frame, rusty metal, and general recognizable parts. Do not copy the exact side-on view.
>
> Subject: One unoccupied, old, battered blue city bicycle with rusty metal parts, two complete wheels, handlebars, saddle, pedals, chain, and frame. No rider or person. It is an inanimate object, so head, torso, and eye orientation are N/A.
>
> Orientation: Bicycle longitudinal direction is yaw 45 degrees toward image-right, with the front wheel on the image-right side. Show both the near side of the bicycle and the forward-facing aspects of the handlebar/front assembly; avoid a flat 90-degree side profile and avoid a straight-on head-on view. The visible wheel rims and frame must read as a coherent bicycle in perspective.
>
> Style/medium: Photorealistic natural object rendering with visible worn blue paint and rust, suitable for a transparent battle sprite.
>
> Composition/framing: One bicycle only, fully visible, centered in a logical 2x1 battle-grid footprint. Keep both tires and every bicycle part inside the canvas with clear margins. No rider.
>
> Lighting/mood: Neutral readable lighting that separates the wheel spokes, frame, handlebars, and saddle.
>
> Constraints: Genuine transparent background (tool parameter transparent_background=true). No text, letters, logos, watermark, border, graphic outline, pedestal, ground plane, road, scenery, contact shadow, motion streaks, sound waves, magic, elemental effects, or additional objects. Do not crop any part of the bicycle.

**Generation tool setting:** as the prompt notes, the imagegen call must actually set `transparent_background: true`; this text alone does not set the tool argument.

## Checks performed

| Check | Evidence | Result |
|---|---|---|
| Source identity and appearance grounding | `docs/monsters.md:103` identifies an unoccupied, right-facing bicycle. The reference visibly shows a blue worn/rusted bicycle, complete bicycle parts and no rider; prompt uses it for identity/color/parts and expressly rejects its flat side-on pose. | Pass |
| 2x1 grid | `docs/monsters.md:209` sets M104 to `2x1`; encounter row `docs/dungeon-enemies.md:90` also labels it `2x1`. Prompt specifies a logical `2x1` footprint and does not infer output pixel dimensions or aspect ratio. | Pass |
| Orientation and framing | Prompt says yaw `45°` toward image-right, front wheel on image-right, both near-side and forward-facing handlebar/front-assembly aspects visible, rejects both a `90°` side profile and straight-on head-on view, and asks for coherent perspective. This supplies a numeric intermediate target and two explicit endpoints; it does not inherit the reference's profile. | Pass |
| Object anatomy N/A | Bicycle is an inanimate object, so head/torso/eye anatomy and those anatomical orientation checks are N/A under sprite skill §22. Prompt correctly specifies bicycle-axis orientation separately instead of inventing a head or face. | Pass |
| Map and learning provenance | Monster row gives hinomi-bend; encounter row elaborates a blind corner and proposed learning role. Prompt repeats only those source facts as context, explicitly bans map/scene, magic/effects and does not add map geometry or a second map description. | Pass |
| Unspecified attributes and role | Master source leaves attribute, weakness/resistance and special behavior unspecified; encounter's magic-learning relation is marked a proposal. Prompt treats learning-role data as context only and depicts no magic or effects. | Pass |
| Style and negative constraints | `docs/assets-policy.md:3–5` calls for photorealistic generated subjects and §13 requires a transparent isolated enemy master without outline/base/contact shadow. Prompt matches object rendering and excludes text/logo, border/outline, pedestal/ground/road/scenery, shadow, motion/sound effects, magic and extra objects. | Pass for contract stage |

## Disposition

No blocker, major, or minor finding remains for this exact prompt. This is a `contract/prompt` pass only; it neither generates nor adopts an image. At generation time, actually set the imagegen argument `transparent_background: true`. A raw-image review must separately verify the perspective, both complete wheels and parts, alpha, framing, and prohibited additions.
