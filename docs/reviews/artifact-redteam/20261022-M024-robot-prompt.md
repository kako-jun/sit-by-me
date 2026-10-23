# M024 robot-clothing prompt review

- **Reviewed stage:** contract/prompt only. No generated image, transparency, cropping, or adoption is assessed here.
- **Reviewer:** independent reviewer, not the author of the M024 specification, prompt, image, or prior review.
- **Date:** 2026-10-22
- **Target:** M024 システマウェポン, `gridClass 2x2`.
- **Canonical source snapshot:** `209ae1733cc6dcede7b3330ff8cbe1ba0a0b2428` plus the current working-tree M024 row (the row is modified in this workspace).
- **Canonical sources inspected:** `docs/content-registry.md` (enemy register and generation bundle); `docs/monsters.md` M024; `docs/dungeon-enemies.md` §6; `docs/art-direction.md` enemy policy and M024 exception; `docs/assets-policy.md`; `.claude/skills/sit-enemy-sprite/SKILL.md`; `.claude/skills/sit-artifact-redteam/SKILL.md`.
- **Previously reviewed prompt:** `docs/reviews/artifact-redteam/20261022-M024-M025-prompt.md`. Its M024 prompt predates the robot-clothing correction and is not evidence for this review.
- **Reviewed prompt source:** complete outgoing prompt supplied with the review task; no candidate image was supplied.

## Contract checks

| Check | Evidence | Result |
|---|---|---|
| ID and grid | Prompt declares M024 and `gridClass 2x2`; current `docs/monsters.md` M024 row declares 2x2. The M024 entry in `docs/dungeon-enemies.md` §6 is a Kanazawa Garden boss-rush candidate. | Pass |
| Robot body and clothing | The M024 row specifies an adult-sized humanoid robot, mechanical exposed head/torso/limbs, no visible skin, and a plain dark-charcoal long-sleeved pullover with straight-cut trousers and no logos. The prompt specifies those same features; “entire exposed … mechanical” plus “show no skin” rules out a visible human body. | Pass |
| Orientation | Prompt defines 45° yaw with the skill's camera-front 0° / exact-right-profile 90° convention, requires both front and right-side planes for head and torso, and directs visible eyes toward +x. This matches the enemy-master direction in the skill and `art-direction.md`. | Pass |
| Systema portrayal | Prompt's relaxed breathing, looseness, posture, and movement direction matches the M024 row's non-rigid Systema pose. It explicitly says not to imply that Systema removes pain sensation, consistent with the M024 research note. | Pass |
| Human-enemy exception | M024 is the expressly recorded cyborg exception in `docs/art-direction.md`; the prompt specifies a robot and introduces no real person or identifiable human reference. | Pass |
| Render and isolation rules | Photorealistic generated enemy, transparent background, one subject, and no environment, text/logo, base, outline, ground shadow, or attack effect follow `docs/assets-policy.md`, `docs/art-direction.md`, and the enemy-sprite skill. | Pass |
| Image-affecting TBDs and contradictions | M024's battle capability, attack, and attribute are still TBD, but the prompt depicts none of them. The working M024 row frames the body, clothing, and pose as the visual candidate contract. No source conflict or unresolved image-affecting TBD was found. | Pass at prompt stage |

## Exact prompt reviewed

> Asset type: enemy battle master candidate M024; gridClass 2x2. Primary request: One adult-sized robot practicing Systema, dressed in a plain dark-charcoal long-sleeved pullover and straight-cut trousers, with no logos. Its entire exposed head, torso, arms, and legs are mechanical; show no skin. Full isolated figure oriented toward the party on the right. Pose communicates relaxed breathing, looseness, posture, and movement; no rigid/braced posture. Head and torso each have 45° yaw (camera front 0°, exact right profile 90°), with both front and right-side planes visible. Eyes, if visible, gaze +x. Photorealistic generated enemy consistent with assets-policy. Transparent background. No environment, no text/logo, no base, no outline, no ground shadow, no attack effects. One subject only. Do not imply Systema removes pain sensation.

## Findings and disposition

No contract/prompt findings. The revised M024 prompt passes this stage and is eligible for generation. This verdict applies only to the exact prompt above; it does not pass any generated image. After generation, measure the actual canvas and alpha bounds, inspect the 45° head and torso planes and edge contact, and complete an independent raw-image review before adoption.
