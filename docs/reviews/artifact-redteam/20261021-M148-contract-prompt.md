# M148 prompt contract — 2026-10-21

- Target: M148 凍った水たまり
- Stage: contract/prompt
- Status: independent prompt review passed after user-directed ground and rounded-outline correction
- Reference: `assets/images/enemies/M148.webp` (thin horizontal ice-puddle silhouette, cloudy ice, cracks, bubbles, and frosted rim; do not copy former raised mound appearance)
- Grid class: `2x1` (`docs/monsters.md` §3-7 and `docs/dungeon-enemies.md`)

## Prompt

Use case: photorealistic-natural. Asset type: isolated battle sprite for Sit by Me enemy M148. These are verbatim canonical source rows for metadata only; do not render words or map elements:

`| M148 | 凍った水たまり | 凍った足元（氷） | 寺町 connector・well-merge（一任による決定 2026-10-15、docs/dungeon-enemies.md が正本） | 氷 | 未定 | 未定 | 生成済み: assets/images/enemies/M148.webp（採否待ち。ほぼ平面・白く曇った氷・ひびと気泡・縁に霜。旧版は盛り上がって凍った水たまりに見えにくく不要とされ削除。kako-jun 2026-10-15） | 同上 |`

`| M148 | 凍った水たまり（2x1） | A: connector・well-merge の雪の道・凍った用水、滑る・割れて落ちる恐怖（EA 1.1、AD 86）。C に準ずる: 属性=氷が記録にある最早の元（LS 66）。F: 2x1 | — （氷） | 雑魚 | 未定 | 絵あり | ◎ | 未定 | 可（拠点。再訪できる。MT 7.2） |`

Create one isolated photorealistic battle sprite of a single frozen puddle set into a small, irregular patch of snow-dusted ground, nearly flat with the ground. Use the supplied image only to preserve a broad shallow horizontal puddle silhouette and ice identity; avoid a raised mound. Give the puddle a naturally rounded, irregular outline with no sharp points, spikes, or protruding ice shards. The cloudy white-blue ice surface contains fine branching cracks, trapped round air bubbles, and a thin frost rim; the cold, slippery frozen surface carries the fear by itself. Show a continuous ground ring 60–100 px wide around the puddle on every side, so the ice clearly rests on ground; keep this small ground patch inside the sprite and let the outer edge meet transparent pixels. This patch is a visual part of the enemy sprite and must not form a path, road layout, watercourse, or map feature. Show the horizontal ice surface from a camera positioned exactly 45° above the ground plane, looking down toward the puddle. This is an inanimate ice formation with no head, torso, eyes, or biological facing; the 45° creature-facing yaw check is N/A; this numeric elevation defines only the surface view. Logical occupancy `gridClass 2x1`; use a 1536×1024 landscape canvas. Keep the complete ice and ground patch inside the canvas with at least 32 px clear margin on every side. Genuine transparent background. No channel, road markings, stones, people, footprints, contact shadow, base, outline, text, logo, or extra object.

Tool setting: `transparent_background: true`.

## Initial independent prompt review

- Reviewer: `/root/enemy_input_audit` (independent; 2026-10-21)
- Verdict: `major` on the initial version because “low oblique overhead view” mixed incompatible relative terms and did not define a camera elevation.
- Correction: replaced that phrase with an explicit camera elevation of 45° above the ground plane. Biological-facing yaw remains N/A for this inanimate puddle.

## Independent re-review

- Reviewer: `/root/enemy_input_audit` (independent; 2026-10-21)
- Verdict: `pass` for contract/prompt stage after the camera elevation correction.
- Evidence: camera elevation is unambiguously 45° above the ground plane and directed toward the puddle; biological yaw remains N/A. The shallow silhouette, cloudy ice, cracks, bubbles, frost rim, and `2x1` class match the canonical records. A minor grammar cleanup was applied without changing meaning.

## User-directed visual correction

- User feedback: surrounding ground is necessary for the object to read as a puddle; sharp points are unnecessary because the frozen state itself is frightening.
- Prompt changes: add a bounded snow-dusted ground ring around the ice; use a rounded irregular puddle outline; explicitly exclude sharp points, spikes, and shards. The ground is a cropped sprite detail without encounter placement or map-layout data.
- The earlier prompt review predates this material correction and does not carry over. Independent re-review is pending.

## Independent re-review after visual correction

- Reviewer: `/root/enemy_input_audit` (independent; 2026-10-21)
- Verdict: `pass` for contract/prompt stage.
- Evidence: snowy ground is supported by the canonical “雪の道・凍った用水” location rationale; its 60–100 px ring is a bounded sprite detail and excludes path/watercourse/map layouts. The rounded edge and lack of spikes/shards follow the user direction. Camera elevation is fixed at 45°, yaw is N/A, and `2x1` remains consistent.
