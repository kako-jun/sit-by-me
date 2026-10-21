# M206 prompt contract — 2026-10-21

- Target: M206 城の雑魚: 忍者
- Stage: contract/prompt
- Status: independent prompt and raw-image reviews passed; adoption pending
- Grid class: `1x2` (`docs/monsters.md` §3-7)
- Candidate: `exec-cf3ba92a-2acf-407f-90e0-8be7a1ab3243.png` (1024×1536 RGBA)

## Canonical source rows

- `docs/monsters.md` M206: ninja, an ordinary castle-only enemy (#140).
- `docs/monsters.md` §3-7: `M206 | 1x2 | 直立する忍者のイマジナリー`.
- `docs/art-direction.md` §94: humans are not enemies; objects such as mannequins remain objects.
- `docs/assets-policy.md`: enemies/objects use photorealistic transparent cutouts.

## Prompt

Create one isolated ordinary RPG battle enemy M206 “ninja”, logical gridClass 1x2, on a transparent portrait 1024×1536 px canvas. Depict a frightening carved black wooden ninja puppet, unmistakably an articulated display object and not a living person. It has a blank carved mask, upright narrow head-and-torso silhouette, articulated wooden joints, and simple dark carved wrap/armor-like plates. No skin, human anatomy, real human, realistic cloth costume, real ninja weapons, real historical person, clan emblem, national symbol, text, or recognizable real-world mark. This is a fictional image of a castle ninja, not an actual person. Photorealistic generated-object style as a studio-photographed carved prop. Camera on both the mask/head and torso: exactly 45 degrees from camera-front toward +x, with front and right planes visible. No eyes, so gaze is not applicable. Full silhouette with margin. Transparent isolated cutout only; no floor, background, contact shadow, border, or extra objects.

Tool setting: `transparent_background: true`.

## Independent prompt review

- Reviewer: `/root/enemy_input_audit` (2026-10-21)
- Verdict: `pass`.
- A carved articulated puppet keeps the ninja identity without making a person into an enemy. The reviewer confirmed that the M112 mannequin clothing constraint is specific to that entity, not a global no-clothing rule; this prompt uses carved prop plates and excludes real costume/weapons.
