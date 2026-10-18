# Stage H miniature-curtain candidate — independent red-team review

- Date: 2026-10-17
- Reviewer: independent red-team reviewer (not the candidate, prompt, or prior-review author)
- Scope: original-pixel review of one unadopted battle-background candidate. No asset, prompt, ledger, Issue, or adoption state was changed.
- Target: `sample/battle/backgrounds/stage-h-miniature-curtain-1920x1080-candidate.png`
- Canonical sources inspected: `.claude/skills/sit-artifact-redteam/SKILL.md`, `.claude/skills/sit-stage-background/SKILL.md`, `.claude/skills/sit-world/SKILL.md`, `docs/art-direction.md`, `docs/assets-policy.md`, `docs/roadmap.md`, `sample/battle/stage-b.json`, and the original-pixel reference images `sample/battle/backgrounds/bg-a.png` and `sample/battle/backgrounds/stage-b.png`.
- Raw-artifact inspection: opened at original size with `view_image`; `sips` reports a non-alpha PNG at exactly 1920×1080. SHA-256: `eef17d5d533349ecc6192133c9b78d3cceb41b033c86a193afdf1b92fe298793`.

## Checks

| Check | Result | Evidence |
| --- | --- | --- |
| Exact 16:9 source dimensions | **Pass** | `sips` reports 1920×1080. |
| Candidate does not overwrite the adopted background | **Pass** | It has a distinct candidate path. Its hash differs from adopted `stage-b.png` (`b4baae7e…a33f`), and `stage-b.json` still resolves to `backgrounds/stage-b.png`. |
| Reference camera language (`bg-a`, `stage-b`) | **Pass** | The floor recedes from a shallow, normal battle-stage viewpoint: the backdrop remains high in frame and the viewer sees the floor surface, without the straight-down field-map composition. Board seams run from lower-left toward upper-right, matching the requested modest repeated oblique depth cue. |
| Main and side curtains | **Pass** | A deep-green pleated curtain spans the rear/upper stage and is visibly parted at both far sides, forming two open side panels. The curtains are unambiguous and do not carry text or branding. |
| Child-made stage scenery | **Pass** | The snow mountains, trees, and castle are visibly painted, irregular cardboard cut-outs with exposed edges, joints, and taped bases—not a polished fantasy landscape. |
| Clear party, enemy, and lower UI floor | **Pass (pixel-only)** | The centre/lower floor is free of props. No object blocks the normal left/right battle lanes or lower command/message region. Live Battle compositing remains unverified. |
| Humans, readable text, logos, watermarks | **Pass** | None are visible in the original pixels. |
| Clearly tabletop / miniature-scale construction rather than a full-size stage photograph | **Major** | The image is still dominated by a full-size-looking varnished wooden theatre floor and life-size velvet curtains. The cut-outs are handmade, but their scale is not established by miniature construction cues such as a visible tabletop edge, corrugated/paper floor, model-scale curtain, or deliberately small material grain. It can read as a photograph of a real kindergarten stage fitted with cardboard flats—the failure that prompted this regeneration—rather than the required miniature itself. |

## Findings and disposition

1. **Major — miniature identity is not reliable.** The prompt requires clearly visible handmade **miniature** materials, while this candidate's life-size stage floor and velvet curtains retain a real-stage reading. **Corrective destination:** regenerate as a shallow-oblique photograph of a small tabletop theatre model: preserve this `bg-a`/`stage-b` camera geometry and the green main/side curtains, but make the floor, curtain, and scenery visibly model-scale handmade materials. Keep all lanes and UI floor open. Do not adopt this candidate as the miniature-stage replacement.
2. **Blocker — lifecycle/provenance record is absent.** The existing battle-background reviews require an Issue #9 row containing ID, area, exact dimensions, source prompt, reference(s), output path, adoption state, and review link. None was available for this output. **Corrective destination:** Issue #9 battle-background ledger as `blocked` or `needs-review`; do not reconstruct prompt/reference fields from this review.
3. **Minor — live Battle display has not been demonstrated.** Pixel inspection cannot prove acrylic sprites, enemy, and UI retain contrast in their actual placement. **Corrective destination:** verification evidence on the same non-ready Issue #9 ledger row after the visual correction.

**Visual-composition disposition: major revision required.** The candidate correctly fixes the requested shallow oblique reference view, curtains, diagonal floor cues, and clear battle space, but does not reliably read as a miniature rather than a photographed real stage. It is **not eligible for adoption: blocker** due to missing provenance, and it also needs visual regeneration before a fresh independent review. This review does not adopt it.
