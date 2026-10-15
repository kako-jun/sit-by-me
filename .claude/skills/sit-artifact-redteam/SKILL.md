---
name: sit-artifact-redteam
description: Independently red-team Sit by Me planning, prompts, generated images, and walk masks before adoption. Use after an authoring pass or before changing an asset to ready; do not use to generate assets.
---

# Sit by Me Artifact Red Team

Find evidence that a proposed or generated artifact is wrong before it is adopted. This is an **independent** review: the reviewer must not be the author of the target specification, prompt, image, mask, or prior review, and must receive the raw artifact and canonical records rather than the author's conclusion.

## Inputs and canonical sources

For a MAP review, first read:

- `docs/content-registry.md`
- target row in `docs/map-asset-registry.md`
- target row in `docs/map-specifications.md`
- applicable graph in `docs/map-topology.md`
- `docs/map-reference-research.md`
- `docs/art-direction.md`, `docs/assets-policy.md`, and `.claude/skills/sit-diorama/SKILL.md`

For an enemy, magic, ability, job, event, or scenario review, replace the MAP sources with its corresponding type register from `content-registry.md`. Read the actual candidate and its source prompt/mask when they exist; never infer success from a filename.

## Review method

1. Construct a checklist from the register **before** looking at the author's self-assessment. Check ID coverage, lifecycle/status, era, location, one-line role, inter-record references, and every explicit `TBD`.
2. Test topology in both directions. For every claimed connection, confirm the reciprocal map, opposite edge, compatible road orientation, and geographic bearing. Flag an edge that conflicts with north-up geography even if two legacy images appear to fit.
3. For a field image, inspect the actual pixels and mask for: all required exits, no path on forbidden edges, no blocked required route, wheelchair width/turning, separate optional dead ends, no accidental people/text, shallow top-down handmade-diorama construction, specified weather/season/period/grime, landmark uniqueness, and reference consistency.
4. Search for silent omissions: a generic road with no landmark; a shared condition stated only at area level but absent from its MAP contract; a created image without a reference ID, output path, adoption state, or walk-mask result; a `ready` item with a remaining question.
5. Treat contradictions between documents as failures, not as permission to choose a convenient version. Historic/legacy notes cannot override the current canonical ledger.

## Findings and disposition

Classify each finding with evidence and an exact corrective destination:

| Result | Meaning | Required disposition |
|---|---|---|
| `blocker` | Would make generation, navigation, accessibility, story continuity, or adoption incorrect | Add a concrete TBD to the target registry row; set it `blocked` or `needs-review`; do not generate/adopt. |
| `major` | Contract is incomplete or conflicting but a safe correction is apparent | Record exact missing field and referenced document; keep non-ready. |
| `minor` | Clarity, naming, or traceability problem that cannot alter the artifact | Record it; do not silently rewrite canonical facts. |
| `pass` | Every required condition has direct evidence | Eligible for author-side resolution; never auto-adopt an image. |

Write a dated review under `docs/reviews/artifact-redteam/` and link it from the relevant registry row. A review must name the reviewer, target ID, canonical sources inspected, raw artifact paths, each check and evidence, findings, and final disposition. If no issue is found, explicitly list the checks performed; a bare “looks good” is invalid.

## Independence gate

Do not repair the candidate while reviewing it. Hand blockers back to the authoring workflow, then require a **new** red-team pass after a material correction. The reviewer may propose a correction, but may not mark its own correction `ready` or `pass`.

## Stop conditions

- Any unresolved TBD, missing source, missing reciprocal edge, or missing mask blocks `ready`.
- An image may remain a `legacy` record, but it cannot be used as proof that a contradictory topology is correct.
- Do not generate replacements, delete candidates, or change public/issue state in this skill unless separately directed.
