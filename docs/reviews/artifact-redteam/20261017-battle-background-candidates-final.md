# Battle background candidates final — independent red-team review

- Date: 2026-10-17
- Reviewer: independent red-team reviewer (not the candidate, prompt, or prior-review author)
- Scope: pixel review of the two unadopted PNG candidates only. No candidate, prompt, canonical record, Issue, or adoption state was changed.
- Targets:
  - `sample/battle/backgrounds/teramachi-outdoor-diorama-1920x1080-candidate.png`
  - `sample/battle/backgrounds/stage-e-1920x1080-candidate.png`
- Canonical sources inspected: `.claude/skills/sit-artifact-redteam/SKILL.md`, `.claude/skills/sit-world/SKILL.md`, `.claude/skills/sit-stage-background/SKILL.md`, `docs/art-direction.md`, `docs/roadmap.md`, `docs/assets-policy.md`, sit-by-me Issue #9, `sample/battle/stage-b.json`, and `docs/reviews/artifact-redteam/20261017-battle-background-candidates-v2.md`.
- Raw-artifact inspection: both target files were opened with `view_image` at original size.

## Shared technical and lifecycle checks

| Check | Result | Evidence |
| --- | --- | --- |
| Exact source dimensions | **Pass** | `sips` reports exactly 1920×1080 for both candidates (16:9). This resolves the 1672×941 export major recorded in the v2 review. |
| Does not overwrite an adopted asset | **Pass** | Both files have distinct candidate paths, are untracked, and have distinct SHA-256 values: Teramachi `20f513e5…6af21`; stage `a11343fc…b64a9`; adopted `stage-b.png` `b4baae7e…a33f`. `stage-b.json` still points to `backgrounds/stage-b.png`. |
| People, readable text, logos, watermark | **Pass** | Neither original-size image contains any visible person, readable text, logo, or watermark. |
| Required background ledger / provenance / lifecycle | **Blocker** | Issue #9 requires each battle background to have an ID, area, exact source dimensions, prompt, references, output, and adoption state in a battle-background ledger. No row or source prompt/reference/adoption state for either new output was found; the prior review's lifecycle blocker therefore remains unresolved. |
| Live Battle sample verification | **Minor** | The pixels provide the prescribed physical space, but no evidence shows the candidates in the required live sample modes. The roadmap and stage-background skill still require an actual battle overlay before adoption. |

## `teramachi-outdoor-diorama-1920x1080-candidate.png`

| Check | Result | Evidence |
| --- | --- | --- |
| Handmade Teramachi winter diorama | **Pass** | The shallow near-top-down scene visibly uses a paper/sandpaper-like black road, torn seams, glossy handmade water, cotton snow, miniature trees, tile roofs, and a white temple wall. It reads as a tabletop model rather than a photograph. |
| Temple element confined to upper 10% | **Pass** | Roofs, wall, watercourse, snow, and trees occupy only the narrow top band (roughly the top 9–10%); they do not intrude into the battle surface. |
| Ground at about 90% or more | **Pass** | The dark road begins directly below the upper band and fills roughly 90–91% of the frame. |
| Oblique repeated parallel lines | **Pass** | Five long, similarly angled torn/wet road seams form repeated lower-left-to-upper-right depth cues. |
| Battle and UI space | **Pass (pixel-only)** | The upper set band is clear of the broad road; left/right lanes and the lower command/message region remain unobstructed. This does not substitute for the outstanding live readability test. |

**Visual-composition disposition: pass.**

## `stage-e-1920x1080-candidate.png`

| Check | Result | Evidence |
| --- | --- | --- |
| Green curtain in upper approximately 10% | **Pass** | A dark-green pleated curtain forms the upper band; its lower edge and the low scenery base lie at roughly 10–12% of image height. |
| Rough child-made cardboard scenery | **Pass** | The blue snow-mountain flats and castle have irregular cut edges, separate panels, visible seams, simple hand-painted snow, and exposed cardboard-like construction. |
| Floor at about 90% | **Pass** | The unobstructed wooden stage floor occupies about 88–90% of the frame; the small variation is due to the deliberately low cardboard flats. It satisfies the intended ground-dominant composition. |
| Oblique repeated floorboards | **Pass** | Many repeated board seams run diagonally from lower-left toward upper-right across the open floor. |
| Battle and UI space | **Pass (pixel-only)** | All props stay in the narrow top band; the enemy/party lanes and lower command/message area are open wood floor. This does not substitute for the outstanding live readability test. |

**Visual-composition disposition: pass.**

## Findings and final disposition

1. **Blocker — both assets lack the Issue #9 battle-background ledger and provenance.** Corrective destination: create one non-ready ledger row per output with its ID, area, exact dimensions, prompt, reference(s), output path, adoption state, and a link to this review. Do not infer or reconstruct the missing prompt/reference from this review.
2. **Minor — live battle readability remains unverified.** Corrective destination: the same rows' verification evidence; use the actual Battle sample to check the required display modes before any adoption decision.

Both revised images pass the requested original-pixel, 1920×1080, no-people/text, non-overwrite, composition, and space checks. They are nevertheless **not eligible for adoption: blocker** until the independent lifecycle record is supplied. A new independent red-team pass is required after that material correction; this reviewer does not adopt either candidate.
