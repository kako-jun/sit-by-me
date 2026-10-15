---
name: sit-field-mask
description: Create, edit, validate, and review Sit by Me field traversal masks and foreground occlusion layers. Use after a field background is accepted or when its accessibility, exits, or foreground display changes; do not use to generate the background itself.
---

# Sit by Me Field Masks

Treat a field mask as a first-class MAP asset, not as a finishing step. Its source must be a specific MAP row whose topology and image contract are `ready` or an approved `legacy` image under review. Read the target MAP specification, topology, relevant era/event conditions, and the accepted background before painting.

## Three traversal classes

The editable traversal source is a full-size RGB PNG with **flat fills only**—no baked contour or antialiased border. It is designed for direct Photoshop painting with the Pencil tool or Fill tool.

| Edit colour | Runtime class | Meaning |
|---|---|---|
| `#000000` black | `blocked` | Nobody may enter: water, wall, building, drop, deep snow, road edge, map base, or unsafe obstacle. |
| `#FF9D00` orange | `assist` | A standing character can pass; a wheelchair user cannot until the story’s companion-assist condition unlocks it. Use for stairs, narrow/rough paths, and safely assistable rubble only. |
| `#FFFFFF` white | `universal` | Everybody, including an unassisted wheelchair user, may pass. Must have adequate width, turning space, and no step/obstacle. |

Do not use colour to mean a merely cosmetic difference. A required main route must be `universal` whenever the MAP contract says it is a wheelchair route. A dead-end reward branch never changes a required route’s class. Per-era variations are separate named source masks; never overwrite an earlier era’s mask.

## Foreground occlusion

Keep foreground display independent of traversal:

- `*-foreground-edit.png` is a full-size, solid-colour RGB edit map: black `#000000` = no cover; cyan `#00FFFF` = render the matching foreground cutout in front of the player.
- `*-foreground.png` is the transparent RGBA artwork actually drawn in front. It contains only the foreground objects, never a coloured guide or contour.
- A foreground tree, rail, wall edge, or roof may cover the player visually while the ground beneath remains `universal`; it must not silently turn the route into `blocked`.

## Workflow

1. Derive every traversable exit and forbidden edge from the MAP’s connection contract. Record edge ranges and traversal class in its JSON source.
2. Start edit maps as flat colours at exactly the background resolution. Do not draw outlines into these edit files.
3. Generate runtime masks and a separate review preview with the repository’s mask tool. The preview may tint classes and draw contours; it is disposable and is never the Photoshop source or runtime mask.
4. Inspect at 100% and against the background: all mandatory paths reach their correct image edge; prohibited edges do not; black hazards cannot be crossed; orange is limited to assistable terrain; white has wheelchair clearance; cyan occlusion does not hide an exit or create an invisible collision.
5. Save the source JSON, traversal edit map, runtime outputs, foreground edit map, and foreground PNG together under `sample/field/masks/` (or the adopted asset’s mask directory). Update the MAP ledger with all paths and the relevant era/assist condition.
6. Send the result to `sit-artifact-redteam` before marking it `ready`.

## Generator contract

`sample/field/masks/make_masks.py` treats the two edit PNGs as canonical; JSON
holds background, size, links, and other metadata. It accepts legacy `walkable`
as `traversal.universal`, so an existing MAP remains valid without conversion.
Optional `traversal.universal`, `traversal.assist`, `traversal.blocked`, and
`foreground` polygon arrays are initial templates only. The generator writes:

- `*-traversal-edit.png`: the flat RGB Photoshop traversal source.
- `*-wheelchair-mask.png`: white only; `*-standing-mask.png` and
  `*-assist-mask.png`: white plus orange. `*-mask.png` remains a compatible
  alias for the wheelchair output.
- `*-foreground-edit.png`: flat black/cyan Photoshop source, and
  `*-foreground-mask.png`: its runtime alpha mask. The separately authored
  `*-foreground.png` remains the transparent foreground artwork.
- `*-mask-overlay.png`: tinted, contoured review preview only.

The first run creates the two edit PNGs from JSON. Later runs read those PNGs,
so Photoshop changes survive; pass `--refresh-edit` only when deliberately
replacing them from the JSON polygons.

## Hard stops

- Missing background, missing reciprocal edge, missing era/assist condition, or a map without an approved connection contract: keep the mask `blocked`.
- Never use a yellow/coloured outline as editable geometry. It is review-only.
- Never make stairs, deep snow, water, rubble, or foreground-only cover white merely to connect the route.
