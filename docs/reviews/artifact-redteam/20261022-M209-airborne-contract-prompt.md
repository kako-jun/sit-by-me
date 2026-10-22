# M209 airborne attack — 2026-10-22

- Target: M209 城の雑魚: くのいち
- Stage: contract/prompt
- Status: prompt contract passed independent review; image candidate has major framing/transparency findings; awaiting user adoption decision; no adopted image exists
- Grid class: `1x2` (`docs/monsters.md` §3-7)
- Reference role: `assets/images/enemies/M206.webp` is a visual reference for the photorealistic carved wooden display-object construction only; do not copy M206's dark palette, standing pose, or silhouette.

## Canonical source rows

- `docs/monsters.md` M209: castle-only ordinary kunoichi enemy (#140); distinguish it from M206 with a light-blue ninja outfit and an airborne kicking attack.
- `docs/monsters.md` §3-7: `M209 | 1x2 | 水色の忍装束の人形が空中から蹴りかかるくのいち（#140。縦長の跳躍姿勢）`.
- `docs/art-direction.md` §94: do not make humans enemies; mannequins and dolls remain display objects/toys.
- `docs/assets-policy.md`: battle master enemies use photorealistic generated images isolated on transparent backgrounds, without acrylic treatment, base, or contact shadow.

## Complete prompt

Use case: product-mockup
Asset type: Sit by Me ordinary RPG battle enemy master sprite, M209, logical gridClass `1x2`.
Primary request: Create one distinct kunoichi enemy: an articulated wooden puppet in a light water-blue ninja outfit, attacking while airborne with a forward flying kick. It must read as a frightening imaginary display puppet, not a living human.
Input image: Image 1 is a material and rendering reference only: `assets/images/enemies/M206.webp`, the existing carved wooden M206 puppet. Do not copy its black palette, upright pose, or silhouette.
Scene/backdrop: isolated transparent cutout, no scene.
Subject: one full-body wooden kunoichi mannequin, logical gridClass `1x2`, on a 1024×1536 px portrait canvas. Wear a clearly visible light water-blue outfit, dominant garment color `#78D7E6`, with simple dark-blue trim `#234A68`. Attack from midair: torso angled forward 25° from vertical, the leading leg extends in a flying kick toward +x, the trailing leg folds beneath the body, one arm extends toward +x and the other is held back for balance. Show visible carved wooden hands and articulated wooden joints at neck, elbows, hips, and knees. Blank wooden mask with no visible eyes.
Style/medium: photorealistic generated-object studio image, visibly crafted wood joints and fabric clothing; consistent material realism with the reference while retaining the blue palette and airborne pose.
Composition/framing: exact 45° yaw for both head and torso, measured from camera-front 0° toward +x; show each front plane and right plane. Keep the complete silhouette, including both hands, feet, and any clothing ends, at least 48 px inside every canvas edge.
Lighting/mood: subdued studio lighting that preserves the light-blue color and reveals the carved joints.
Materials/textures: woven light water-blue fabric over a wooden articulated display mannequin; exposed wood at the blank mask and joint areas.
Constraints: one character only; no ground contact, since the pose is airborne. Transparent background requested with tool setting `transparent_background: true`.
Avoid: standing, walking, or grounded pose; black/dark overall outfit; human skin, living person, realistic human face, or identifiable real person; extra characters; weapons; floor; scenery; contact shadow; border; text; logo; watermark; acrylic stand.

## Tool setting

`transparent_background: true`
