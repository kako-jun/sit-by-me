# M114 revised weekly-magazine contract review — 2026-10-22

- Reviewer: independent prompt-contract review (`/root/m114_contract_review`)
- Target: `docs/reviews/artifact-redteam/20261022-M114-weekly-magazine-contract-prompt.md`
- Stage: before image generation
- Compared with: M114 canonical row and grid decision in `docs/monsters.md`; M114 placement row in `docs/dungeon-enemies.md`; `docs/art-direction.md` fear-media and flip rules; `.claude/skills/sit-enemy-sprite/SKILL.md`
- Generation performed: no

## Verdict

**FAIL — subject matter is acceptable, but the current prompt still fails the sprite skill's unambiguous-prompt gate.** The prior text/flip blocker is resolved: the warning badge is nonverbal and the prompt forbids legible text, numbers, and logos. The adult pin-up treatment is non-explicit and consistent with the user's requested identity. Before generation, replace remaining subjective or underspecified execution terms with concrete visual values and placement instructions.

## Checks

- **User direction:** Pass. The fuchsia/red/yellow/cream/black weekly cover palette, dense graphic blocks, and adult pin-up illustration directly address the user's request. “Adult woman” plus opaque lingerie and no nudity/sexual activity/transparent fabric keeps the depiction adult and non-explicit. Printed art remains part of the sole book object, not a separate human enemy. The cloth blindfold remains on the cover model's eye area.
- **Text and horizontal flip:** Pass. The revised contract no longer asks for readable `18禁` or any text, number, or logo. An abstract red-and-white warning badge is not a directional mark and remains meaningful when flipped. Ensure graphic marks remain non-letter-like and do not accidentally generate readable glyphs.
- **Source and grid:** Pass. M114's canonical identity is an adult weekly magazine with a blindfolded cover. The `1x2` decision matches M114–M116. Keeping the adopted asset read-only until the user accepts the new candidate is correct.
- **Placement:** Pass. M114 is still unassigned in `docs/dungeon-enemies.md`; the prompt correctly adds no shelf, scene, or encounter location.
- **Orientation and isolation:** No anatomical yaw/gaze applies to a book, correctly marked N/A. The isolated transparent cutout, full-silhouette constraint, no base/shadow/scene, and single-book identity are appropriate.

## Blocking contract gaps

The sprite skill's unique-interpretation gate says not to generate while non-numeric or non-source-derived execution terms remain. This prompt still relies on terms including `3/4 view`, `clearly readable`, `vivid`, `dense`, `bold`, `sensual pin-up`, `tasteful`, `weekly-magazine-style`, and `photorealistic`. Some may be acceptable as broad style guidance individually, but here they do not specify a repeatable layout or pose. It also gives named colors but no hex values, and does not state which side the spine appears on or give a defined camera yaw; the reference image is called an orientation reference without spelling out the orientation to retain.

Before generation, specify at least:

- Exact color values (hex) for the cover's main background, accents, badge, and cloth band.
- A camera angle (for example, 45° from a front-on view) and whether the visible spine is on the image's left or right in the master; use the current reference for the chosen side.
- Approximate cover-region proportions/locations for the model, non-readable headline blocks, halftone/starburst shapes, and warning badge. All marks must remain nonverbal under a horizontal flip.
- Concrete non-explicit adult pin-up appearance and pose (opaque garment coverage, limb/torso position, and facial treatment) rather than “sensual/tasteful” alone.

The revised direction is materially sound and should be retained while making these final execution details concrete. No policy or source-content blocker remains beyond prompt precision. Do not generate from the current version; run one final contract check after these edits.
