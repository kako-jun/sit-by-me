# M130 contract/prompt re-review — 2026-10-21

- Reviewer: Codex, delegated independent reviewer (not the prompt author)
- Target: M130 フグ
- Stage: `contract/prompt`
- Verdict: **pass for this prompt revision; image generation is eligible after the authoring workflow records this exact prompt and uses the specified transparent tool setting**
- Canonical commit base: `64bb973967e41475ef55678e9ce7d10dd413dc4a`; the canonical rows below were also checked in the current working-tree revision, which is uncommitted at review time.
- Reference inspected: `assets/images/enemies/M130.webp` (640×535 WebP, alpha channel with alpha min 0 and max 1, at the canonical commit base). Its pose is legacy/reference-only.
- Prior report: [`20261021-M130-contract-prompt.md`](20261021-M130-contract-prompt.md) retains the initial `major` finding and its original prompt unchanged. The attribute conflict is resolved in the current canonical rows; this report supersedes that finding for the prompt below.
- No image was generated and no candidate was created.

## Canonical sources inspected

- `.claude/skills/sit-enemy-sprite/SKILL.md`, §§14–22, 24–46
- `.claude/skills/sit-artifact-redteam/SKILL.md`, enemy prompt review method, findings and independence gates
- `docs/content-registry.md`, enemy index and prompt assembly rules
- `docs/monsters.md`, M130 row and grid-class table
- `docs/dungeon-enemies.md`, M130 encounter row and M130 allocation row
- `docs/learning-schedule.md`, water-learning row
- `docs/art-direction.md`, water-edge creatures
- `docs/assets-policy.md`, generated art and enemy-master rules
- Actual pixels and file alpha in `assets/images/enemies/M130.webp`

Current source facts: `docs/monsters.md` M130 row identifies フグ / 水辺の生物, location サニーランド aquarium, attribute `水（魚。kako-jun 2026-10-21）`, weakness/resistance `未定`, and role text `未定（膨らみと毒）`; its image is adoption-pending. `docs/dungeon-enemies.md` M130 row specifies `フグ（1x1）`, aquarium, `膨らみと毒`, the learning entry `—（水）`, and雑魚. Its allocation row states the fish puffs up in the aquarium and is poisonous. `docs/learning-schedule.md` lists M130 among the 水 learning sources. The earlier attribute inconsistency is absent from the current source rows.

## Complete prompt reviewed

> Canonical source metadata only; do not render text or infer additional visual attributes from metadata: ID M130; name フグ; family 水辺の生物; appearance placement 水辺（章は未定）。サニーランド sunnyland-aquarium-indoor（一任による決定 2026-10-15、docs/dungeon-enemies.md が正本）; attribute 水（魚。kako-jun 2026-10-21）; weakness/resistance 未定; role 未定（膨らみと毒）; encounter role 雑魚; encounter location aquarium＝廃水族館の水槽（EA 1.3）; encounter feature 膨らみと毒; learning row —（水）; current asset `assets/images/enemies/M130.webp` is adoption-pending and its old descriptor “膨らんだ姿・右向き・透過” describes only that existing image, not this target pose. Create one isolated, photorealistic game battle sprite of the same inflated pufferfish in the reference image. Use the old image only for the fish's identity, visible color pattern, body shape, and spine arrangement; do not copy its near-true-right-profile pose, framing, or background. Add no objects or unsupported features. Set the fish's body yaw to exactly 45° from camera-front toward screen-right (+x), where camera-front is 0° and true right profile is 90°. Show both the front plane and the right-side plane of the fish's face; do not produce a 90° side profile. Point the snout diagonally toward screen-right. One fish only, full body visible, centered, no cropping. Logical occupancy `gridClass 1x1`. Transparent background with genuine alpha. No text, logo, outline, acrylic base, or ground/contact shadow. Square 1024×1024 target, highest quality.

Tool setting: `transparent_background: true`.

## Checks performed

| Check | Evidence | Result |
|---|---|---|
| Target ID, family, location, attribute, weakness/resistance status, behavior and learning source | `docs/monsters.md` M130 row; `docs/dungeon-enemies.md` M130 and allocation rows; `docs/learning-schedule.md` water row. Water attribute is now consistently recorded as fish-related; weakness/resistance remain explicitly undecided and are not depicted | Pass |
| Exact grid class | `docs/monsters.md` M130 range row declares `1x1`; `docs/dungeon-enemies.md` M130 row says `1x1`; prompt records `gridClass 1x1` | Pass |
| Direction convention | Enemy-sprite skill §18 defines camera-front `0°`, true right profile `90°`, required yaw `45°`, and both face planes. Prompt uses those exact definitions and explicitly excludes the old profile pose | Pass |
| Reference role and pixels | `assets/images/enemies/M130.webp` (640×535, alpha min 0/max 1) visibly depicts one inflated pufferfish with cream underside, tan/brown spotted upper body, pale long spines, translucent fins and a large eye. Its near-profile pose is explicitly excluded as target pose | Pass |
| Required design and art style | `docs/art-direction.md` water-edge creature line specifies a pufferfish with swelling and poison; `docs/assets-policy.md` requires realistic-style enemy images. Prompt retains identity and attributes without inventing a poison cloud, aquarium scenery, or other effect | Pass |
| Transparency and exclusions | Enemy-sprite skill §42 requires transparency both in prompt and tool setting; prompt and tool request alpha. `docs/assets-policy.md` enemy-master rule and sprite skill §22 prohibit outline, base and contact shadow; prompt excludes these, as well as text/logo | Pass |
| Output dimensions vs logical occupancy | Enemy-sprite skill §36 states `gridClass` is logical occupancy, not pixel dimensions. Prompt treats `1x1` and square 1024×1024 as separate requirements | Pass |
| Unresolved visual TBDs | Remaining weakness/resistance `未定` do not appear in the sprite. The visible fish identity and swollen form are resolved in canonical source facts | Pass for prompt stage; runtime mechanics are outside this review |

## Preserved historical finding

The initial report remains unchanged at [`20261021-M130-contract-prompt.md`](20261021-M130-contract-prompt.md). It correctly recorded a `major` because the then-current metadata simultaneously said `属性=未定` and `属性=水系` with an explicit caveat. The current canonical revision records `水（魚。kako-jun 2026-10-21）` in the M130 attribute field and removes the stale caveat from the dungeon row. This resolves the original conflict; it does not retroactively change the initial report's finding or reviewed prompt.

## Disposition and pending checks

This exact prompt passes the **contract/prompt** stage and is eligible for one generation attempt using `transparent_background: true`. This is not an image review or adoption: after generation, measure actual pixel dimensions and alpha, record the alpha-positive bounding box, and inspect the face's front and right-side planes at original size. Keep the image non-ready and adoption-pending until those checks and human adoption are complete.
