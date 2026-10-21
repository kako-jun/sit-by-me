# M201 prompt contract — 2026-10-21

- Target: M201 異国への誤像
- Stage: contract/prompt
- Status: independent revised prompt review passed; final raw image review passed; adoption pending
- Grid class: `2x2` (`docs/monsters.md` §3-7)
- Final candidate: `exec-d7a63c76-b157-49c3-9705-83ade5e29da5.png` (1254×1254 RGBA)
- Initial candidate: `exec-995b8dde-0b3f-4066-95dd-bd910d39da5d.png` (superseded after raw review found a style conflict)

## Canonical source rows

`docs/monsters.md` M201: six uncanny motifs (hopping doll, rippling blade, wrapped doll, dark mound, strange interwoven ornament, mask), one enemy ID, fictional misconception; must not make an actual country, ethnicity, religion, craft, or funerary custom into an enemy.

`docs/monsters.md` §3-7: `M201 | 2x2 | 複数の誤像を一体として扱う敵`.

`docs/dungeon-enemies.md` §2.10: M201 is one ordinary enemy row representing six forms in the desert vertical city. Its placement is already recorded there; this image task does not add or alter encounter data.

## Prompt

Edit this exact enemy sprite to comply with the project's photorealistic generated-object style. Preserve its existing composition, 2x2 silhouette, six fictional motifs, camera position, materials, colors, and transparent cutout. Transform the current painterly illustration into a convincing photorealistic studio photograph of a fantastical practical creature-prop sculpture assembled from a carved wooden hopping doll, a separate wrapped wooden doll, an abstract rippling shard, a dark rough mound, a strange interwoven metal ornament, and a featureless mask. Keep the same creature identity and arrangement. Keep the view exactly 45 degrees from camera-front toward +x, with the front and right planes visible. Keep all forms obviously invented and nonhuman; do not introduce any real cultural costume, religious or national symbol, funerary object, real weapon, writing, floor, scenery, frame, or contact shadow. Preserve transparent background and the complete full silhouette inside the square canvas.

Tool setting: `transparent_background: true`; referenced image: initial M201 candidate above.

## Independent prompt review

- Reviewer: `/root/enemy_input_audit` (independent; 2026-10-21)
- Initial prompt verdict: `pass after prompt specification completed`; its image was blocked by raw review because painterly 2D art conflicted with `docs/assets-policy.md`.
- The edit prompt keeps the six motifs and composition, while correcting the style to the project's photorealistic generated-object policy. It retains the stated fictional/cultural exclusions.
- Image edit prompt review: pass; reviewer requested more precise camera wording, incorporated above.
- Image edit raw review: pass after one framing adjustment to restore margin around the right mound protrusion. The image remains a candidate until kako-jun's adoption decision.
- Pose caveat from raw review: the overall fused composite has an oblique front/right-plane view and no clear right-profile portrait, but the individual blank doll/mask forms face different directions, so their exact yaw cannot be independently measured. Retain this note for adoption review; do not regenerate solely for this ambiguity given the acrylic-stand presentation guidance.
