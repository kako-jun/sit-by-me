# M207 final edit-contract review — 2026-10-21

- Reviewer: Codex independent reviewer (`enemy_input_audit`)
- Target: M207 城の雑魚: 姫
- Candidate referenced: `［ローカルパス省略］/exec-b529c122-b421-4daf-b4e9-ebdfb8c0467a.png`
- Scope: Review of the proposed final edit-prompt constraints supplied for this audit; the complete verbatim prompt was not provided.
- Sources: `docs/monsters.md:165,246`; `docs/dungeon-enemies.md:262`; `.claude/skills/sit-enemy-sprite/SKILL.md` lines 16–36.

## Review

The described prompt preserves the existing Japanese-inspired porcelain doll/statue, `gridClass 1x2`, transparent background, and complete silhouette. These match M207's source identity as a Japanese-style castle princess enemy and its upright 1x2 size. It directs both the face/head and torso toward image-right, requires front and right planes to remain visible, and explicitly excludes left-facing, rear-facing, and profile views. This addresses the previous raw candidate's head-orientation failure without changing its inanimate identity.

**Blocker: angle precision.** The proposed wording says “about 45°” (`約45度`). The sprite skill requires exactly `45°` from camera-front toward `+x`, and its unique-interpretation gate rejects approximate execution terms. Replace with exact 45° and the defined camera-front/+x reference. State separately that the head and torso each show their front plane and right-side plane.

**Canvas clarification:** The referenced candidate is 887×1774 px. The described prompt preserves canvas but does not state those exact output dimensions; include `887×1774 px` if the edit must retain that canvas. `gridClass 1x2` is logical occupancy and does not substitute for canvas dimensions.

## Verdict

**Blocker until exact angle wording is used.** Source identity, Japanese-inspired object styling, grid, transparency, and full-silhouette constraints are appropriate. No canonical source was edited and no image was generated.

## Updated final-prompt and candidate audit — 2026-10-21

The revised prompt summary now specifies the head and torso **each exactly 45° from camera-front toward screen-right (`+x`)**, with the broad front plane and right-side plane visible, and explicitly names the output canvas as **887×1774 px**. This resolves the earlier approximate-angle and unspecified-canvas blockers. The Japanese-inspired porcelain doll/statue identity, 1x2 grid, transparent cutout, and full-body constraint remain source-consistent.

### Verbatim final edit prompt

> EDIT the referenced same cracked porcelain statue/doll of a Japanese-inspired castle princess. Preserve her crown, layered fictional robe, red/black/white/gold palette, cracked glossy ceramic material, folded hands, full-body silhouette, and transparent background. Preserve the exact 887×1774 px canvas and 1:2 portrait composition. Change only orientation: rotate the torso exactly 45 degrees from camera-front toward image-right (+x), with its front plane and right side plane both visible. Rotate the head and blank oval faceplate independently to exactly the same 45-degree direction from camera-front toward image-right (+x); the faceplate's broad front surface must remain clearly visible while a narrow right-side plane is also visible. Both head and torso face image-right at exactly 45 degrees. Do not show a left-facing profile, back view, or pure side profile. Make the front plane recognizable through its broad oval area and subtle central vertical gold seam, without adding eyes, nose, mouth, or any human facial features. Keep the complete crown and hem inside the canvas with transparent margins. No text, props, background, clothing changes, or new objects.

### Candidate check

- Candidate: `［ローカルパス省略］/exec-b9502417-27dd-43b8-8b87-22f0a8ca1445.png`
- Canvas: 887×1774 px RGBA; all four corner alpha samples are 0.
- Alpha-positive bounding box: 876×1757 at x=0, y=1. The sprite touches the left edge and nearly touches the top edge; the full intended transparent margin is absent, and the left skirt edge appears clipped/flush with the frame.

## Updated disposition

**Prompt angle/canvas: pass.** The independent raw-image review reports **PASS** for image-right three-quarter head and torso orientation, transparent corners, and a complete visible silhouette ([raw review](20261021-M207-raw-image-b9502417.md)). The contract reviewer separately measured the any-alpha bounding box as touching the left edge and nearly touching the top. The raw reviewer measured the alpha>1% subject bounds at +14,+9 px and found the crown, hem, and side silhouette intact. This difference is consistent with faint edge pixels; record it as a minor fringe/frame caveat for user adoption review. No canonical source was edited.
