# M025 ribbon prompt / contract review

- **Reviewed stage:** contract/prompt only. This review does not assess a generated image, alpha, crop, or adoption.
- **Reviewer:** independent reviewer; not the author of the M025 specification, prompt, or prior review.
- **Date:** 2026-10-22.
- **Target:** M025 ヘルナルキッソス.
- **Source baseline:** repository `HEAD` `209ae1733cc6dcede7b3330ff8c8be1ba0a0b2428`; canonical ledger files were also checked in the working tree at review time. No image candidate or pixel reference was supplied.
- **Canonical sources inspected:** `docs/content-registry.md` (enemy M register and prompt assembly rules); `docs/monsters.md` M025; `docs/dungeon-enemies.md` M025 and §6; `docs/art-direction.md` enemy orientation and asset rules; `docs/assets-policy.md` generated-image and enemy-master policy; `.claude/skills/sit-enemy-sprite/SKILL.md`; `.claude/skills/sit-artifact-redteam/SKILL.md`.

## Complete prompt reviewed

> Asset type: enemy battle master candidate M025; gridClass 2x2. Primary request: One isolated single-stem hellish narcissus flower enemy inspired by FFV Halicarnassus. Its single flower head has exactly six distinct outer petals around exactly one central trumpet-shaped corona, as in Narcissus pseudonarcissus; show exactly one flower head, on exactly one stem, and no other flowers. Show the flower head in a 45° yaw (camera front 0°, exact right profile 90°), oriented to the right, with the trumpet opening and its right side visible. Tie exactly one cute bow around the middle of the stem; its two thin ribbon tails visibly stream toward image-left (−x). Add no face, human head or torso, eyes, roots, or leaves. Photorealistic generated enemy consistent with assets-policy. Transparent background. No environment, no text/logo, no base, no outline, no ground shadow, no attack effects. Single subject. Magic/learning/spell name are behavior and must not be pictured or written in the image.

## Contract checks

| Check | Evidence | Result |
|---|---|---|
| ID, role, grid, and placement | M025 is a Kanazawa Garden boss-rush candidate and a 2x2 midboss candidate in `docs/monsters.md` and `docs/dungeon-enemies.md`; prompt declares M025 and `gridClass 2x2`. | Pass |
| Subject count and flower structure | M025 row specifies one narcissus-shaped flower, one stem, six outer petals, one trumpet-shaped corona, and no roots or leaves. Prompt specifies exactly one head, one stem, six distinct petals, one corona, no additional flowers, roots, or leaves. | Pass |
| Orientation | M025 row specifies a 45° right-facing flower head using camera front 0° and exact right profile 90°. Prompt uses the same angles and explicitly shows the trumpet opening and right side. As a flower, it has no humanoid head or torso; humanoid head/torso checks are N/A under the enemy-sprite skill. | Pass |
| Ribbon | M025 row specifies one cute bow at the middle of the stem and two thin tails flowing toward image-left (−x). Prompt specifies one bow, the stem middle, two thin tails, and −x flow. | Pass |
| Image policy and behavior | Photorealistic generated enemy, transparent isolated subject, and no environment, text/logo, base, outline, ground shadow, or attack effects comply with `assets-policy.md` and the enemy-sprite skill. The prompt correctly excludes magic, learning, and the spell name from the picture. | Pass |
| Unresolved image-affecting TBDs / contradictions | Spell effects, attributes, and targets remain TBD in M025, but the prompt explicitly excludes behavior/effects and does not depict them. No conflict with the M025 row or shared enemy policy found. | Pass at prompt stage |

## Findings and disposition

No prompt/contract finding blocks generation. **Pass for the contract/prompt stage only.** This does not adopt an image. After generation, record the actual canvas dimensions and alpha bounds, inspect the pixels and orientation, then obtain an independent raw-image review before adoption.
