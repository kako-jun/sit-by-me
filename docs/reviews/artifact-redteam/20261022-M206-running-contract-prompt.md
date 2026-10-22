# M206 running attack update — 2026-10-22

- Target: M206 城の雑魚: 忍者
- Stage: contract/prompt
- Status: prompt contract passed independent review; image candidate has major framing/transparency findings; awaiting user adoption decision
- Grid class: `1x2` (`docs/monsters.md` §3-7)
- Read-only reference: `assets/images/enemies/M206.webp` (current adopted source `exec-cf3ba92a-2acf-407f-90e0-8be7a1ab3243.png`, 1024×1536)
- Output role: one separate, unadopted candidate under generated_images; the canonical image remains untouched until user approval.

## Canonical source rows

- `docs/monsters.md` M206: castle-only ordinary ninja enemy (#140); its current adopted image is recorded in the M206 row.
- `docs/monsters.md` §3-7: `M206 | 1x2 | 走り込みながら腕の打撃を繰り出す忍者人形（#140。縦長）`.
- `docs/art-direction.md` §94: do not make humans enemies; mannequins and dolls remain display objects/toys.
- `docs/assets-policy.md`: enemy battle masters are photorealistic generated images on transparent backgrounds, without acrylic treatment, base, or contact shadow.

## Complete prompt

Use case: product-mockup
Asset type: Sit by Me ordinary RPG battle enemy master sprite, M206, logical gridClass `1x2`.
Primary request: Create a separate, unadopted candidate for M206 by changing the pose of the referenced ninja mannequin to show a dynamic running attack. Treat Image 1 as a read-only visual reference. Do not modify or overwrite the source or canonical `assets/images/enemies/M206.webp`. Keep the same frightening carved black wooden articulated display puppet, blank carved mask, jointed wood construction, and angular carved wood plates. It must remain visibly a wooden object, not a living person.
Input image: Image 1 is a read-only edit reference for identity and material: `assets/images/enemies/M206.webp`, current adopted 1024×1536 transparent M206.
Scene/backdrop: isolated transparent cutout, no scene.
Subject: one full-body black wooden ninja mannequin, logical gridClass `1x2`, on a 1024×1536 px portrait canvas. Show a running lunge toward +x: torso pitched 25° forward from vertical; front foot reaches toward +x, rear foot pushes off behind; one wooden fist thrusts toward +x in a straight punch and the other arm is pulled back for balance. Keep all limbs attached and visible.
Style/medium: photorealistic generated-object studio image, matching the existing carved black wood material and details.
Composition/framing: preserve the edit target’s 45° yaw for both head and torso, measured from camera-front 0° toward +x; show each front plane and right plane. Keep the complete silhouette, including both feet and head details, at least 48 px inside every canvas edge.
Lighting/mood: subdued studio lighting that reveals the black carved wood and joints.
Materials/textures: dark carved wood throughout; visible articulated wooden joints; no fabric clothing.
Constraints: change only the pose in a separate candidate; preserve the existing character identity and wood design. Never write to the reference file or canonical path. Transparent background requested with tool setting `transparent_background: true`.
Avoid: standing or upright pose; running without an attack; clothing; living human, skin, realistic anatomy, or real person; real ninja weapons; extra objects; motion trails; floor; background; contact shadow; border; text; logo; watermark; acrylic stand.

## Tool setting

`transparent_background: true`
