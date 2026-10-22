# M206 / M209 revised prompt-contract review — 2026-10-22

- Reviewer: independent raw-source and prompt review (`/root/m130_prompt_review`)
- Stage: pre-generation contract review; no image generated
- Scope: revised complete prompts in `20261022-M206-running-contract-prompt.md` and `20261022-M209-airborne-contract-prompt.md`.
- Sources checked: `docs/monsters.md` M206/M209 and §3-7; `docs/dungeon-enemies.md` M209; `docs/art-direction.md` lines 94–95; `docs/assets-policy.md` lines 3–5, 11–13; `.claude/skills/sit-enemy-sprite/SKILL.md` lines 16–46; prior findings in `20261022-M206-M209-contract-review.md`.
- No prompt/spec/source/asset was edited; no image was generated.

## Summary of prior blockers

The earlier report blocked M206 because the adopted source was described as an edit target without explicit protection and separate output, and blocked both prompts because `stylized-concept` conflicted with photorealistic asset policy. In the revised prompts:

- M206 calls `assets/images/enemies/M206.webp` a **read-only** identity/material reference, explicitly forbids modifying or overwriting it, and requires a **separate, unadopted** candidate. This resolves the source-protection/output-role blocker.
- Both prompts replace `stylized-concept` with `product-mockup` and explicitly specify photorealistic generated-object studio rendering. This resolves the photorealistic-style ambiguity. The phrase “product-mockup” is a mildly unusual use-case label for action poses, but it does not override the detailed pose and asset-style instructions and is not blocking.

## M206 — running ninja mannequin

**Verdict: PASS.**

| Check | Verdict | Evidence |
|---|---|---|
| Source alignment | Pass | `docs/monsters.md` §3-7 row M206 says `1x2` and `走り込みながら腕の打撃を繰り出す忍者人形`. Prompt specifies a wooden articulated ninja display puppet, running lunge, and arm strike/punch. Castle-only ordinary enemy identity remains. |
| Adopted image protection | Pass | Prompt says Image 1 is “a read-only visual reference,” calls for a “separate, unadopted candidate,” and explicitly says not to modify/overwrite the source or canonical path. This directly fixes the previous blocker. |
| Grid/canvas/margins | Pass | `gridClass 1x2`; canvas exactly `1024×1536`; full silhouette and both feet/head details at least 48 px from each edge. `1x2` is a logical footprint, correctly distinguished from the pixel canvas by the skill. |
| Pose and angle | Pass | Lunge toward `+x`; torso pitch 25° from vertical; forward and trailing legs explicitly differentiated; one fist punches while the other arm balances. Head and torso yaw each exactly 45° from camera-front 0° toward +x, with front and right planes shown. Pitch and yaw are independent constraints, not contradictory. |
| Identity/material and exclusions | Pass | Existing black carved articulated wooden puppet, blank carved mask, joints, and angular wooden plates are preserved. No clothing, human skin/anatomy, person, weapons, scene, floor, shadow, or stand. This follows `docs/art-direction.md` line 95: humans are not enemies; mannequins/dolls remain display objects/toys. |
| Style/transparency | Pass | `product-mockup` is paired with explicit photorealistic generated-object studio style. Transparent cutout and actual tool setting `transparent_background: true` are stated; enemy asset policy exclusions (border/base/contact shadow) are present. |

## M209 — airborne kunoichi mannequin

**Verdict: PASS.**

| Check | Verdict | Evidence |
|---|---|---|
| Source alignment | Pass | `docs/monsters.md` §3-7 row M209 says `1x2` and `水色の忍装束の人形が空中から蹴りかかるくのいち`. `docs/dungeon-enemies.md` M209 distinguishes it from M206 with a light-blue ninja outfit and airborne kick. Prompt retains those distinguishing traits. |
| Reference role | Pass | M206 is limited to wood-construction/rendering reference; its black palette, standing pose, and silhouette are explicitly excluded. No adopted M209 image is implied. |
| Grid/canvas/margins | Pass | `gridClass 1x2`; canvas exactly `1024×1536`; complete hands, feet, and garment ends at least 48 px from every edge. This is feasible for the specified portrait canvas and dynamic pose. |
| Pose and angle | Pass | Torso pitch 25° forward; leading leg extends in a flying kick toward +x, trailing leg folds beneath, arms counterbalance, and no ground contact. Head/torso yaw each exactly 45° from camera-front 0° toward +x, with front and right planes visible. These pitch/yaw and limb instructions are compatible. |
| Puppet/person distinction | Pass | Prompt specifies one articulated wooden puppet, visible carved wood hands and joints, blank wooden mask/no eyes, and exposed wood at mask/joints; it explicitly excludes living human, skin, realistic face, and real person. This follows `docs/art-direction.md` line 95 and assets policy. |
| Color/material/style | Pass | Water-blue outfit matches canonical `水色`; explicit `#78D7E6` and dark trim `#234A68` make the blue distinction from M206 concrete. Trim is a small operational garment detail and does not change the source identity. Photorealistic object/studio rendering is explicit after replacing the ambiguous `stylized-concept` label. |
| Transparency/exclusions | Pass | Transparent cutout plus actual tool setting `transparent_background: true`; no scene, floor, shadow, border, text, logo, watermark, or acrylic stand. |

## Final result

**PASS for M206 and PASS for M209.** The previous blockers are resolved: M206’s adopted source is explicitly read-only with separate candidate output, and both prompts now specify the photorealistic style required by `assets-policy.md`. Grid classes, canvas dimensions, margins, poses, yaw reference frame, source traits, and transparency settings are concrete and mutually compatible. M206.webp remains untouched; generation remains pending the parent workflow.
