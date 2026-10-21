# M133 actual generation-prompt re-review — 2026-10-21

- Reviewer: Codex, delegated independent reviewer (not the prompt author)
- Target: M133 毒キノコ
- Stage: `contract/prompt`
- Verdict: **pass for the exact second-call prompt text; actual transparency tool argument verified**
- Canonical base: `64bb973967e41475ef55678e9ce7d10dd413dc4a`
- Reference inspected, species/color only: `assets/images/enemies/M133.webp`, 640×466 WebP; SHA-256 `2984bd3d1899eb90999c6579962dacaa7a164aa7f1b2ea0781e78ab7e1be9fbe`
- This review supersedes neither the earlier full-prompt audit nor the requirement to review each distinct prompt revision.

## Canonical sources inspected

- `.claude/skills/sit-artifact-redteam/SKILL.md`, prompt-stage method and findings/disposition rules
- `.claude/skills/sit-enemy-sprite/SKILL.md`, §§12, 14–22, 24–47
- `docs/content-registry.md`, enemy index and prompt assembly rules
- `docs/monsters.md:132,224,278,319` (M133 identity, grid, image record, placement summary)
- `docs/dungeon-enemies.md:122,285` (encounter detail and placement provenance)
- `docs/art-direction.md:83` (poisonous mushroom fear category)
- `docs/assets-policy.md:3–5,13` (photorealistic subject and isolated transparent enemy asset)
- Actual pixels of `assets/images/enemies/M133.webp`
- Exact second-call prompt supplied by the author after identifying the prompt mismatch

## Exact prompt reviewed

> Recreate the poisonous mushroom enemy M133 as a photorealistic isolated transparent battle sprite, using the attached existing image only as species and color reference. Preserve exactly four mushrooms: one dominant red cap with three smaller mushrooms around it, pale stems, white cap flecks, and visible airborne spores. Keep the whole group and spores fully inside a compact centered 1x1 composition. Mushrooms have no face, eyes, limbs, or anthropomorphic body; head and torso orientation do not apply. Map location is context only and must not appear. Genuine transparent background. No soil, moss, ground, vegetation, roots, wood, forest, scenery, shadow, poison cloud, colored effects, text, logo, watermark, border, or outline.

The generation-call record confirms that the second call used `transparent_background: true`. This is a separate imagegen tool argument; it is not part of the prompt text quoted above.

## Checks performed

| Check | Evidence | Result |
|---|---|---|
| Identity and exact count/composition | `docs/monsters.md:132` identifies poisonous mushroom M133. The reference has four visible mushrooms: one dominant red cap and three smaller caps around it, with pale stems/white flecks. The prompt expressly sets four and the same relative arrangement. | Pass |
| Spores | Master row `docs/monsters.md:132` says spores impair vision/judgment and records “胞子つき”; encounter row `docs/dungeon-enemies.md:122` also identifies spores. Prompt includes visible airborne spores, no poison cloud or colored effects. | Pass |
| Grid | `docs/monsters.md:224` declares M133 `1x1`; encounter row `docs/dungeon-enemies.md:122` also labels it `1x1`. Prompt specifies compact centered `1x1` composition without inferring pixel dimensions. | Pass |
| No invented attribute/effects/environment | Attribute and weakness/resistance are `未定` in the master row. The prompt adds no element or attack effect. It says map location is context only and forbids environment, soil/moss/vegetation/wood/forest and scenery. | Pass |
| Orientation N/A | Mushrooms have no face, eyes, limbs, or anthropomorphic body in the prompt. Enemy-sprite skill §22 says not to invent head/torso orientation for targets with none. | Pass; N/A justified |
| Art and transparency contract | Photorealistic-natural rendering is consistent with `docs/assets-policy.md:3–5`. Prompt asks for an isolated transparent sprite and excludes scenery, text/logo, border, outline, base/ground and shadow. The author verified that the actual second imagegen call passed `transparent_background: true`. | Pass |

## Disposition

No blocker, major, or minor wording defect was found in this exact prompt text. The earlier prompt audit covered a longer revision; this re-review is recorded separately because the generated candidate used this shorter text. The actual second-call tool argument was verified as `transparent_background: true`. This is not an image pass or adoption decision; the raw candidate is judged independently.
