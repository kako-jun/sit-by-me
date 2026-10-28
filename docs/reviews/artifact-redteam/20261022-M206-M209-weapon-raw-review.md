# M206 / M209 weapon revisions: independent raw-image review — 2026-10-22

- Reviewer: `/root/m206_m209_weapon_raw_review` (independent raw-image review; no image generation or edits).
- Stage: `raw-image`. This review assesses only the two listed PNG files. It does not approve adoption.
- Repository state inspected at `57d9132c0eb3384c25792e918d295b1a900cf612` (working docs may have subsequent uncommitted edits).
- Sources inspected: `.claude/skills/sit-artifact-redteam/SKILL.md`; `.claude/skills/sit-enemy-sprite/SKILL.md`; `docs/monsters.md` M206/M209 and §3-7; `docs/dungeon-enemies.md` M206/M209; `docs/art-direction.md` §95; `docs/assets-policy.md`; complete prompts `20261022-M206-kunai-action-contract-prompt.md` and `20261022-M209-shuriken-airborne-contract-prompt.md`.
- Canonical classes: both `1x2` (logical grid, matching `docs/monsters.md` §3-7).

## M206 — running attack with kunai

- Reviewed raw candidate: `［ローカルパス省略］/exec-78833a1d-2d55-4c9d-aade-c756406ec920.png`
- SHA-256: `dd8dfdc7264da4974f04cb3560e509b95b6490966c3944ba847bd426717a1cee`
- Raster: `1024×1536`, RGBA (`srgba`). All four corner alpha samples are `0`; the outermost rows and columns sampled have alpha max `0`. Thus fully transparent canvas edges are present. At original display size, the main visible puppet/weapon span is approximately x=34–1012, y=160–1404; the kunai tip is close to the right edge but remains visible.
- Pose: strong low sprint, torso pitched forward, one leg extended back and the other driving forward; thrusting arm extends toward +x. This is visibly distinct from M209's aerial kick and much more forceful than an upright stance.
- Weapon: one clearly recognizable dark-steel kunai with triangular blade and ring pommel in the forward hand; no extra weapon visible.
- Orientation/material: mask and torso show front and right planes rather than a pure right profile. The subject reads as a jointed carved wooden mannequin, with visible ball joints and dark carved plates.
- Artifacts: no separate stray fleck or text/logo was visible. A soft brown-black vignette/glow is visible around the subject in the rendered preview, despite the prompt's no-glow/no-gradient requirement. Since the sampled outer canvas edges are transparent, this appears confined to the interior exterior pixels; it still weakens the isolated-cutout presentation and should be considered before adoption.
- Disposition: **candidate quality pass with a major transparency-presentation concern**. Pose, weapon, distinction, and puppet identity pass visual review; the visible interior vignette is the outstanding issue. Adoption decision remains with the user.

## M209 — airborne kunoichi with shuriken

- Reviewed raw candidate: `［ローカルパス省略］/exec-844e3d01-5594-46c8-baec-4bd8edfa5d8f.png`
- SHA-256: `091241448be7046913515ca346a1b3ba98e464f2fabc4c1a1256ea3df94f5632`
- Raster: `1024×1536`, RGBA (`srgba`). All four corner alpha samples are `0`; top and bottom edge alpha max are `0`. The first and last columns contain only very low alpha at their maxima (1/255 and 2/255 respectively). The main visible puppet/weapon span is approximately x=20–978, y=20–1320; no body part or shuriken appears cropped.
- Pose: clearly airborne, with torso inclined, a leading leg extended in a flying kick, trailing leg folded, and the opposite arm counterbalancing. It reads distinctly from M206's low sprint.
- Weapon: one clear four-point steel shuriken is held in the forward hand; no kunai or additional weapon visible.
- Outfit/material: light water-blue fabric with dark-blue trim is visually dominant; exposed wood mask, joints, hands and feet keep the subject legible as a constructed mannequin. Head and torso show front and right planes, not just a right profile.
- Artifacts: no separate stray fleck or text/logo was visible. A strong cyan-blue halo/vignette surrounds the figure and fills much of the transparent exterior in the preview, contrary to the prompt's no-halo/no-gradient and fully transparent exterior requirements. The very low alpha on side-edge pixels is also measurable as noted above.
- Disposition: **candidate quality pass with a major transparency-presentation concern**. The requested aerial action, blue outfit, weapon, and visual distinction pass; the halo/gradient is the outstanding issue. Adoption decision remains with the user.

## Summary

Both candidates satisfy the requested pose distinction and carry the correct single ninja weapon. Both are `1024×1536` and have transparent corners. The apparent vignette around M206 and pronounced cyan halo around M209 conflict with the prompts' isolated transparent-cutout requirements; M209 also has faint alpha at the extreme side columns. These findings concern the raw candidates only and do not change either canonical asset or any adoption status. Per the red-team skill, registry-row links to this report should be added by the authoring workflow after this independent review.
