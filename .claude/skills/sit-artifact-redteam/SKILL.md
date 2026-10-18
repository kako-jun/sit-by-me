---
name: sit-artifact-redteam
description: Independently red-team Sit by Me planning, prompts, generated images, and walk masks before adoption. Use after an authoring pass or before changing an asset to ready; do not use to generate assets.
---

# Sit by Me Artifact Red Team

Find evidence that a proposed or generated artifact is wrong before it is adopted. This is an **independent** review: the reviewer must not be the author of the target specification, prompt, image, mask, or prior review, and must receive the raw artifact and canonical records rather than the author's conclusion.

## 一意解釈監査（このスキルの全行より優先）

レビューで `少し`、`やや`、`広い`、`狭い`、`近い`、`遠い`、`自然`、`十分`、`明瞭`、`目立つ`、`適切`、`雰囲気`、`おおよそ`、`〜風`、`斜め`だけ、`奥行き`だけを根拠にしてはならない。各判定には原文ファイル行、参照画像パス、画面座標、ピクセル数、個数、色コード、または定義済み方角を添える。生成入力に変換不能な曖昧語が残っている場合は `major` とする。台帳にない道・水路・直線・直交・格子・等間隔の追加は `blocker` とする。

## ミニチュア材料監査

ミニチュア背景をレビューするとき、「模型に見える」は判定語として使わない。生成入力の材料・工作道具・加工法を原文で読み、原寸画像で各項目を一つずつ確認する。`foamboard`、段ボール断面、`paper clay` の刻み、綿雪、紙・紙やすりの地面、セロファン水、スポンジ木、マスキングテープ、PVA接着剤、ポスターカラーの筆跡のうち、生成入力で指定されたものが三つ未満しか確認できない候補は `major` とする。実景写真・実物素材・CG均一面しか確認できない場合は `blocker` とする。

## Inputs and canonical sources

For a MAP review, first read:

- `docs/content-registry.md`
- target row in `docs/map-asset-registry.md`
- target row in `docs/map-specifications.md`
- applicable graph in `docs/map-topology.md`
- `docs/map-reference-research.md`
- `docs/art-direction.md`, `docs/assets-policy.md`, and `.claude/skills/sit-field-background/SKILL.md`

For an enemy review, read `.claude/skills/sit-enemy-sprite/SKILL.md`, the target `M` row, its source prompt, and the actual RGBA candidate. Record the declared `gridClass`, canvas px, transparent-pixel bounding rectangle, and whether head and torso each show the front plane and right plane. A 90° right-profile head or torso, a gridClass outside `1x1`/`2x1`/`1x2`/`2x2`, or an outside-rectangle measure outside 92–96% is a `blocker`.

For a summon review, substitute `.claude/skills/sit-summon-sprite/SKILL.md` and the target `S` row. For magic, ability, job, event, or scenario review, use the corresponding type register from `content-registry.md`. Read the actual candidate and its source prompt/mask when they exist; never infer success from a filename.

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
