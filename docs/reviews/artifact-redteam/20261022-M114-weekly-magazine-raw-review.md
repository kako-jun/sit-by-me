# M114 weekly-magazine raw-image review — 2026-10-22

- Reviewer: independent raw-image reviewer (`/root/m114_raw_review`)
- Target: M114 18禁の成人向け週刊誌（目隠しされた表紙）
- Stage: raw-image
- Source: `docs/monsters.md:116,224`; `docs/dungeon-enemies.md` M114 entry; `docs/reviews/artifact-redteam/20261022-M114-weekly-magazine-contract-prompt.md`; `.claude/skills/sit-enemy-sprite/SKILL.md`; `.claude/skills/sit-artifact-redteam/SKILL.md`
- Candidate: `/home/kako-jun/.codex/generated_images/01a15ccc-868c-7f60-8889-229de4286e8f/exec-fa7c7b39-3307-4c5a-ac00-c298fb6c0b24.png`
- Candidate remains unadopted; this review does not make an adoption decision.

## Measurements

- `file` reports PNG RGBA, `1024×1536` px. The prompt declares `gridClass 1x2`, consistent with `docs/monsters.md`'s M114–M116 decision.
- Alpha channel range is `0–254`; all four corner alpha samples are `0`. Alpha is real, not merely an RGBA label.
- Strict alpha-positive bounding rectangle: `1010×1489` at `(0,47)`; faint positive-alpha residue reaches the left canvas edge. At `alpha ≥ 1%`, bbox is `880×1360` at `(82,90)`, leaving margins of 82 px left, 62 px right, 90 px top, and 86 px bottom. The visible book itself is not cropped.
- Sampled background points `(20,700)`, `(512,40)`, `(1000,700)`, `(512,80)` all have alpha `0`.

## Checks and findings

- **Book silhouette — Major.** The object is immediately recognizable as a closed book with a front cover, thick page block, and prominent bound spine. It does not read as a thin Japanese weekly magazine; its substantial rounded hardcover construction repeats the book-like silhouette the user found insufficiently distinctive in the earlier cloth-wrapped book. The requested cover treatment is present, but the physical format weakens the magazine identity.
- **Color and cover layout — Pass.** The front uses fuchsia/pink halftone dots, red, yellow, cream, near-black borders, burst shapes, stacked blank headline panels, and a circular warning-like badge. These cues evoke a Japanese pulp weekly-cover layout and give M114 stronger character than a plain wrapped book. No legible headline, number, or recognizable magazine logo is present.
- **18+ erotic signal — Major.** The cover illustration is a clearly adult, fully clothed pin-up with a red satin garment, exposed shoulders/cleavage, lipstick, perfume, and roses. It is suggestive without nudity, exposed nipples/genitals, or sexual activity. However, the lower-right circular badge contains a stylized face/heart-like emblem rather than an unambiguous 18+ age-restriction mark, and the art could still read as a generic vintage glamour or cosmetics cover. The requested adult-magazine identity is therefore not immediate enough.
- **Blindfold and cover art — Pass.** One dark-red cloth band crosses the illustrated woman's eyes. The woman is printed cover art, not an additional scene entity.
- **Isolation and alpha edge — Major for cleanup.** The four corners and sampled exterior points are transparent, and the main book has clear margins. However, alpha-positive residue extends to x=0, whereas the ≥1% bbox starts at x=82; inspect/remove the faint left-edge fringe during any later authoring pass. No floor, shelf, or separate prop is visible.
- **Anatomy/orientation — N/A.** The target is a book with printed illustration; no enemy head/torso yaw or gaze applies.

## Disposition

**Major — raw-image candidate needs a material revision before it can satisfy the requested identity.** Keep the loud Japanese weekly-cover palette/layout, the non-explicit adult pin-up, and the eye-covering band. Rework the physical object to read as a thin periodical/magazine rather than a thick hardcover book, make the age-restricted adult-magazine signal unmistakable through non-readable visual cues, and eliminate the faint left-edge alpha fringe. This is a raw-image quality finding only; adoption remains for the user to decide.
