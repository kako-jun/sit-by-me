# M131 retry prompt contract review — 2026-10-21

- Reviewer: Codex, independent artifact red-team reviewer
- Target: M131 スズメバチ
- Stage: `contract/prompt`; no image generated
- Canonical source commit: `64bb973967e41475ef55678e9ce7d10dd413dc4a`
- Prompt reviewed: `/tmp/sit-m131-retry-prompt.txt` (verbatim below)
- Reference inspected: `assets/images/enemies/M131.webp` (640×636 WebP); reference is for identity, color pattern and natural anatomy only.

## Source checks

- `docs/monsters.md` §3-1, M131 row (line 130): M131 is a hornet; attribute, weakness/resistance and skill are unspecified; canonical asset policy says direct transparent imagegen and no retained pre-processing original.
- `docs/monsters.md` §4 size table (line 224): M130–M135 are 1x1; §3-8 (line 276) confirms M131 1x1.
- `docs/dungeon-enemies.md` row M131 (line 124): `スズメバチ（1x1）`, encounter context is the trailhead / cedar grove, enemy role is regular, and individual skill is TBD. The prompt correctly treats this as provenance only and bans scenery.
- `.claude/skills/sit-enemy-sprite/SKILL.md`: head and torso yaw must be exactly 45° from camera-front 0° toward true-right profile 90°, with both front and right-side planes visible; record `gridClass`; request transparency through the actual imagegen tool setting; no outline, base or contact shadow.
- `docs/art-direction.md` §「敵素材」: realistic-looking enemy asset, facing +x; no human; insect render should remain readable and not heighten disgust. The prompt's single insect, natural photorealism and exclusions fit this guidance.
- `docs/assets-policy.md` §「素材の方針」: enemy battle master is a transparent isolated asset, outside the acrylic-stand treatment.
- `docs/content-registry.md` §§「共通の運用」「プロンプト組み立て規約」: prompts derive from canonical rows, and unspecified attributes/effects must not be added.

## Checklist and finding

| Check | Evidence | Result |
|---|---|---|
| Identity, number and anatomy | Prompt specifies exactly one hornet, six legs, two antennae, two pairs of wings, segmented abdomen and stinger; the inspected reference supports a single black/yellow hornet and these anatomical traits. | Pass |
| Attribute/TBD handling | Prompt states attribute, weakness/resistance and skill are unspecified and forbids additions; no elemental or poison effect is introduced. | Pass |
| Map provenance | Encounter row is explicitly context only; prompt bans map scenery and named environmental objects. | Pass |
| Orientation | Defines 0°, 90°, target 45°, image-right, both compound eyes, and front/right planes for head and thorax; this is an unambiguous test matching the sprite skill. | Pass |
| Grid | Explicit `gridClass 1x1`, consistent with the M131 row and size table. | Pass |
| Alpha and excluded art | Genuine transparent background and `transparent_background=true` are explicitly required; outline, glow, fringe, shadow, text, logo, environment and extra insects are prohibited. The generation call must actually pass the `transparent_background: true` tool argument; prompt text alone is not evidence that the argument was set. | Pass, conditional on actual tool argument |
| Canvas and safe bounds | Prompt provides no pixel canvas dimensions or numeric silhouette bounds. “Clear transparent space” does not define a reproducible margin or pixel region, so completeness/edge clearance cannot be mechanically interpreted from the contract. | **Major** |

## Exact prompt reviewed

```text
Create one new transparent raw PNG candidate for M131 スズメバチ; do not alter the canonical asset.
Canonical row: "M131 | スズメバチ | 生物 | 卯辰山 UTS-01 登り口（一任による決定 2026-10-15、docs/dungeon-enemies.md が正本） | 未定 | 未定 | 未定 | assets/images/enemies/M131.webp（imagegen 透過直生成を採用。長辺640。加工前の原本は残さない） | #12、#17". Encounter row: "M131 | スズメバチ（1x1） | A: 登り口・杉木立（EA 1.3） | — | 雑魚 | 未定 | 絵あり | △ | 未定 | 未定". The row is placement context only; depict no map or scenery. Attribute, weakness, resistance and skill are unspecified; add none.
Use Image 1 only as a reference for hornet identity, black/yellow pattern and natural anatomy. Do not copy its pose/profile. Exactly one complete hornet with six legs, two antennae, two pairs of translucent wings, segmented abdomen and natural stinger. Camera-facing head and thorax yaw are 45° between camera-front 0° and true-right profile 90°, pointed image-right. Show both compound eyes and the front and right-side planes of the head and thorax; not a profile. Keep every antenna tip, wing tip, leg and stinger visibly inside the canvas with clear transparent space around the complete silhouette. Do not let any part touch or cross the canvas edge.
Photorealistic natural insect rendering under neutral light. Genuine transparent background; set transparent_background=true. Edges are natural antialiasing only: no colored outline, rim glow, fringe, halo or shadow. No text, logos, watermark, border, pedestal, ground, contact shadow, nest, tree, leaves, forest, extra insects, poison droplets/cloud or elemental effect. Logical gridClass 1x1.
```

## Disposition

**Historical disposition for the first revision:** Major; do not generate from that version. It lacked pixel canvas dimensions and said only “clear transparent space.”

## Re-review of revised prompt — 2026-10-21

Revised prompt reviewed: `/tmp/sit-m131-retry-prompt.txt` as currently present at re-review. The author added a 1536×1024 landscape canvas and replaced the vague margin wording with a complete-insect/no-crop requirement. The prompt still explicitly requires exactly one hornet, six legs, two antennae, two pairs of wings, segmented abdomen and stinger; it retains the defined 45° head/thorax yaw, both compound eyes and both face planes; it keeps 1x1 and all source/TBD/environment exclusions. This resolves the missing canvas and edge-cropping ambiguity at contract stage. The requested tool setting is explicit; actual use must still be verified in the generation call.

**Revised disposition: PASS for `contract/prompt` stage only.** At generation, set the actual imagegen argument `transparent_background: true`. Raw-image review must still verify that the complete insect is visible, actual alpha is present, and the prescribed head/thorax planes are rendered. The earlier major finding above is retained as history and is superseded by this pass for the revised prompt.
