# Stage F miniature candidate — independent red-team review

- Date: 2026-10-17
- Reviewer: independent red-team reviewer (not the candidate, prompt, or prior-review author)
- Scope: original-pixel review of one unadopted battle-background candidate. No candidate, ledger, status, Issue, or adoption state was edited.
- Target: `sample/battle/backgrounds/stage-f-miniature-1920x1080-candidate.png`
- Canonical sources inspected: `.claude/skills/sit-artifact-redteam/SKILL.md`, `.claude/skills/sit-stage-background/SKILL.md`, `.claude/skills/sit-world/SKILL.md`, `docs/art-direction.md`, `docs/assets-policy.md`, `docs/roadmap.md`, `sample/battle/stage-b.json`, and `docs/reviews/artifact-redteam/20261017-battle-background-candidates-final.md`.
- Raw-artifact inspection: opened at original size with `view_image`; `sips` reports 1920×1080 PNG.

## Checks

| Check | Result | Evidence |
| --- | --- | --- |
| Exact 16:9 source dimensions | **Pass** | `sips` reports 1920×1080. |
| Candidate does not overwrite the adopted background | **Pass** | The candidate has its own untracked path and SHA-256 `37404a42…bbafa7`; adopted `stage-b.png` is distinct (`b4baae7e…a33f`) and `stage-b.json` still points to `backgrounds/stage-b.png`. |
| Handmade tabletop miniature, not photographic stage | **Pass** | Corrugated-cardboard edges, torn/irregular cut-outs, visible tape, thick painted paper, and a low cardboard platform edge are direct, unmistakable construction evidence. It does not read as a real theatre photograph. |
| Required camera angle | **Pass** | The platform’s near corrugated edge is visible, floorboards recede toward the scenery, and the top scenery sits behind the stage plane. The camera is shallow and oblique from slightly above/side: neither head-on nor straight-down. |
| Upper narrow scenery band | **Pass** | A green paper curtain, crude cardboard snow-mountain flats, and a taped cardboard castle are confined to roughly the top 10–12% of the frame. The child-made construction is visible without becoming a fantasy landscape. |
| Ground-dominant battle surface | **Pass** | The open wooden miniature floor fills roughly 88–90% of the image. Its many repeated floorboard seams run lower-left to upper-right, producing the specified strong diagonal depth cue. |
| Battle and UI safe zones | **Pass (pixel-only)** | The left/centre/right battle lanes are free of props. The lower command/message region is open floor; the cardboard front lip is limited to the extreme lower edge and has no text or interactive-looking detail. Live Battle compositing remains unverified. |
| People, readable text, logos, watermark | **Pass** | None visible at original size. |

## Findings and disposition

1. **Blocker — lifecycle/provenance record remains absent.** The existing final battle-background review establishes that Issue #9 requires one record per battle background with ID, area, exact dimensions, source prompt, reference(s), output path, adoption state, and review link. No such record or original generation provenance was available for this new output. **Corrective destination:** the Issue #9 battle-background ledger, as a `blocked` or `needs-review` row; do not reconstruct prompt/reference fields from this review.
2. **Minor — live Battle display has not been demonstrated.** Pixel inspection verifies composition only. `sit-stage-background` and the roadmap require the real Battle sample overlay before adoption. **Corrective destination:** verification evidence on that same Issue #9 ledger row.

**Visual-composition disposition: pass.** The corrected asset satisfies the miniature-material, shallow-oblique-camera, upper-band, diagonal-floor, and open-battle-space requirements. It is **not eligible for adoption: blocker** until its provenance/lifecycle record exists; after that material correction, it needs a fresh independent red-team pass. This review does not adopt it.
