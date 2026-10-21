# M130 contract/prompt review — 2026-10-21

- Reviewer: Codex, delegated independent reviewer (not the prompt author)
- Target: M130 フグ
- Stage: `contract/prompt`
- Verdict: **major — do not generate until the noted metadata conflict is made explicit**
- Canonical review base: `64bb973967e41475ef55678e9ce7d10dd413dc4a`
- Prompt under review: complete revised prompt supplied for this review on 2026-10-21; reproduced below.
- Reference inspected: `assets/images/enemies/M130.webp` (640×535 WebP with alpha, at the canonical review base)
- No image was generated and no candidate was created.

## Sources inspected

- `.claude/skills/sit-enemy-sprite/SKILL.md`, especially §§14–22, 24–46
- `.claude/skills/sit-artifact-redteam/SKILL.md`, enemy prompt review method and findings disposition
- `docs/content-registry.md`, enemy index and prompt assembly rules
- `docs/monsters.md`, M130 row and grid table
- `docs/dungeon-enemies.md`, M130 encounter row and allocation row
- `docs/art-direction.md`, § water-edge creatures
- `docs/assets-policy.md`, generated art and enemy-master rules
- Actual pixels in `assets/images/enemies/M130.webp`

## Exact prompt reviewed

> Source facts (metadata only; do not render any text): M130; フグ; 水辺の生物; 水辺（章は未定）。サニーランド sunnyland-aquarium-indoor（一任による決定 2026-10-15、docs/dungeon-enemies.md が正本）; 属性=未定; 弱点・耐性=未定; 未定（膨らみと毒）; 絵=膨らんだ姿・右向き・透過; `M130 | フグ（1x1） | A: aquarium＝廃水族館の水槽（EA 1.3）。E: 膨らみと毒。属性=水系（LS 65。台帳に水属性の記録は無い） | — （水） | 雑魚 | 膨らみと毒（L 記述）`. Create one isolated, photorealistic game battle sprite of the same inflated pufferfish shown in the reference image. Preserve its existing pufferfish identity, color pattern, body shape, and spine arrangement; do not add objects or features. Rotate the fish's body to exactly 45° yaw from the camera front toward screen-right (+x): camera-front is 0°, true right profile is 90°. Show both the front plane and right side plane of the face; do not produce a 90° side profile. The fish's snout points diagonally toward screen-right. One fish only, full body visible, centered, no cropping. Logical occupancy gridClass 1x1. Transparent background with genuine alpha. No text, logo, outline, acrylic base, or ground/contact shadow. Highest quality, square 1024x1024 target.

The author also specified `transparent_background: true` as the image-generation tool setting.

## Checks and evidence

| Check | Evidence | Result |
|---|---|---|
| ID, family, location, appearance/role, spell and status facts included without inventing content | `docs/monsters.md:129`; `docs/dungeon-enemies.md:136,283`; prompt labels its source bundle metadata-only and includes both source rows | Pass, subject to conflict finding below |
| Grid class | M130 is `1x1` in `docs/monsters.md:224` and `docs/dungeon-enemies.md:136`; prompt says `gridClass 1x1` | Pass |
| Orientation | Sprite skill §18 defines front `0°`, true right `90°`, requires `45°`, both face planes and rejects a 90° profile. Prompt gives these exact directions and explicitly requires both planes | Pass |
| Orientation against reference pixels | `M130.webp` shows an inflated fish with its face and body near true-right profile; it is useful for identity and colors, not as the target pose | Pass; target override is stated clearly |
| Identity and source visual facts | `docs/art-direction.md:82` says pufferfish, swelling and poison. Actual reference visibly has a cream underside, tan/brown spotted upper body, pale long spines, translucent fins and a large eye. Prompt retains identity, color pattern, body shape and spine arrangement without requiring new details | Pass |
| Appearance style | `docs/assets-policy.md:5` calls for photorealistic-style generated images for enemies | Pass |
| Transparency and enemy treatment | `docs/assets-policy.md:13`; sprite skill §42. Prompt requests genuine alpha and omits outline/base/contact shadow; author specified tool transparency setting | Pass |
| Background, text and object additions | Prompt asks for one isolated fish, no text or added objects/features; no unsupported aquarium environment or poison effect is requested | Pass |
| Canvas vs grid semantics | Sprite skill §36 states grid class is logical occupancy and does not specify pixel dimensions. Prompt separately identifies `1x1` and a square 1024×1024 target | Pass |

## Major finding

**The metadata block presents an unresolved attribute contradiction without identifying it as a contradiction.** `docs/monsters.md:129` has the attribute field `未定`. The included verbatim `docs/dungeon-enemies.md:136` row says `属性=水系` while also stating `台帳に水属性の記録は無い`; its spell field is `—（水）`. The prompt first states `属性=未定`, then repeats the water-system claim as though both were settled facts. Although the block says metadata-only, it does not tell the model or reviewer which entry is authoritative or that no attribute-based visual effect may be inferred. The artifact has no water depiction requirement, so this is readily resolvable without changing canonical records.

**Exact correction:** replace the attribute metadata clauses with an explicit conflict transcription, for example: `属性欄の記録差（描画に使わない）: docs/monsters.md = 未定; docs/dungeon-enemies.md = 水系（同じ行に「台帳に水属性の記録は無い」と注記）; 属性や水の効果を画像へ追加しない。` Preserve the quoted dungeon row as source evidence if desired, but label its attribute/spell fields as unresolved metadata and keep them out of visual instructions. Then submit the corrected complete prompt for a new independent contract review.

The old image descriptor `絵=膨らんだ姿・右向き・透過` also describes the legacy image. Its “右向き” could be read as the requested target pose; add `既存画像の旧記述であり、今回の向き指定ではない` to make the history/target distinction explicit. The later 45° clause already specifies the intended pose, so this is a minor clarity fix and not a separate major finding.

## Disposition

Keep M130 non-ready and do not generate from this prompt revision. The orientation, `1x1` grid class, realistic style, alpha request (including tool setting), and no-base/no-shadow constraints pass. Re-review after explicitly labeling the conflicting attribute metadata and the legacy right-facing descriptor.
