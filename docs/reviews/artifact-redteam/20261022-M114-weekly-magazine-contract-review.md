# M114 weekly-magazine contract review — 2026-10-22

- Reviewer: independent prompt-contract review (`/root/m114_contract_review`)
- Target: `docs/reviews/artifact-redteam/20261022-M114-weekly-magazine-contract-prompt.md`
- Stage: before image generation
- Reviewed against: `docs/monsters.md` M114 and grid decision; `docs/dungeon-enemies.md` M114; `docs/art-direction.md` §§3, 5; `.claude/skills/sit-enemy-sprite/SKILL.md`
- Generation performed: no

## Verdict

**FAIL — do not generate from this prompt yet.** The size, object identity, transparent isolation, retained adopted source, and unassigned placement are consistent with the source. The proposed legible `18禁` badge conflicts with the sprite rule against readable text and creates a known left-right reversal problem. The user's direction supports an erotic adult-magazine visual treatment, but does not specifically require printing those characters in the image. Remove the legible badge and use non-readable graphic marks instead.

## Findings

1. **The core visual direction is supported.** M114 is an `18禁の成人向け週刊誌（目隠しされた表紙）`; `docs/art-direction.md` groups it as fear media. A saturated Japanese weekly-magazine cover palette, dense headline-like graphic blocks, halftones, starbursts, and suggestive non-explicit artwork of an unmistakably adult fictional model are consistent with the user's request and preserve the book as the sole enemy. Keeping the image on the cover as printed art, without showing magazine contents or a separate person in the scene, is sound.

2. **The literal `18禁` badge is a blocking conflict.** The sprite skill and `docs/art-direction.md` §5 prohibit readable text, logos, and side-dependent marks because the renderer may horizontally flip enemy sprites. A `18禁` badge is legible text and becomes reversed in that use. The user asked that the image be recognizable through color and Japanese weekly-magazine styling; they did not explicitly instruct that the characters `18禁` appear. This is therefore not an authorized exception. Preserve the red/white badge-like visual if useful, but replace its contents with abstract, unreadable graphic marks. Do not introduce other legible text or recognizable magazine branding.

3. **“Fully clothed glamorous pose” risks losing the requested adult-erotic distinction.** It may read as a fashion magazine. Keep the model unmistakably adult and use a clearly sensual, non-explicit cover-art treatment (for example, dramatic makeup, a revealing but opaque evening outfit, confident pose, and suggestive lighting), while excluding nudity, sexual activity, visible genitals, and explicit depiction. The prompt's prohibition on exposed underwear may remain, but should be reconciled with the desired erotic tone through styling and composition rather than reducing the art to ordinary fashion photography.

4. **Other contract checks pass.** M114 remains a closed upright book with the canonical blindfold band; `1x2` matches the ledger decision for books/DVD cases. `1024×1536`, transparent background, one isolated book with front and spine visible, preserving the adopted source pending approval, no fabricated placement, and anatomical yaw/gaze marked N/A are consistent. The prompt correctly leaves M114 unassigned and does not add a map location.

## Required edits before generation

- Remove the instruction to render legible `18禁` characters and the claim that this text is directly user-requested.
- Use a non-legible red/white age-warning-style graphic badge, with abstract marks only; keep all cover typography as unreadable graphic texture to survive horizontal reversal.
- Make the printed cover image more clearly adult and erotic through non-explicit styling, while preserving the existing content limits and single-book identity.
- Re-run prompt-contract review after updating the prompt. Do not generate from the current version.
