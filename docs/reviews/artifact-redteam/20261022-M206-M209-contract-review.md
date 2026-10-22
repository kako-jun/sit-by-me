# M206 / M209 prompt-contract review — 2026-10-22

- Reviewer: Codex independent reviewer (`enemy_input_audit`)
- Stage: pre-generation contract review; no image generated
- Sources: `docs/monsters.md:165,168,247,250`; `docs/dungeon-enemies.md:261,264`; `docs/art-direction.md:94`; `docs/assets-policy.md:3–5,13`; `.claude/skills/sit-enemy-sprite/SKILL.md:16–38`; complete prompts in `20261022-M206-running-contract-prompt.md` and `20261022-M209-airborne-contract-prompt.md`.

## M206 — running ninja puppet

**Verdict: Blocker pending two clarifications.**

The source row names a castle ninja, and §3-7 specifies a running ninja puppet delivering an arm strike in `gridClass 1x2`. The prompt's lunge, forward punch, articulated black wood puppet, no clothing/weapon, exact head and torso yaw at 45° from camera-front toward `+x`, visible front/right planes, 1024×1536 canvas, and 48 px all-side margin are consistent. Keeping it visibly an inanimate wooden display puppet satisfies the no-human-enemy rule. The photorealistic generated-object treatment, transparency, and no base/contact shadow follow assets policy.

1. **Existing adopted asset protection:** the prompt calls the adopted `assets/images/enemies/M206.webp` “the edit target” and says “Edit the provided M206 ... image.” The task requires that adopted asset remain untouched. Make Image 1 explicitly a read-only identity reference and require a separate unadopted candidate output; do not overwrite or modify the canonical file.
2. **Style label conflict:** `Use case: stylized-concept` is ambiguous beside the explicit photorealistic studio style and the required photorealistic rendering for enemy objects (`assets-policy.md:5`). Remove or replace that label with a photorealistic enemy-sprite use case so it cannot steer toward illustration.

## M209 — airborne kunoichi puppet

**Verdict: Blocker pending style-label clarification.**

The source requires a wooden-doll kunoichi in a light-blue ninja outfit, airborne and kicking, with `gridClass 1x2`; the prompt implements those traits and deliberately distinguishes it from M206's black, standing wooden puppet. The light-blue `#78D7E6` garment and dark-blue `#234A68` trim operationalize the source's 水色 instruction. A clothed wooden puppet is the canonical subject, not a human enemy; exposed wooden mask and joints, blank face/no eyes, and no human skin preserve that distinction. The flying kick toward `+x`, tucked leg, balancing arms, 25° torso pitch, exact 45° head/torso yaw from camera-front toward `+x`, visible front/right planes, 1024×1536 canvas, 48 px all-side margin, transparency, no ground contact, and no floor/shadow/frame are concrete and mutually compatible.

- **Style label conflict:** as for M206, `Use case: stylized-concept` conflicts ambiguously with the explicit photoreal studio-object rendering required by assets policy. Remove or replace it before generation. The rest of the prompt is source-consistent.

## Summary

The grid classes, portrait canvas dimensions, margins, poses, and 45° orientation requirements are explicit. M206 must be framed as a read-only reference edit that yields a separate candidate, preserving its adopted canonical file. Both prompts should remove the `stylized-concept` use-case label to make the mandatory photorealistic rendering unambiguous. No prompt/spec file or canonical asset was edited; no generation was performed.
