---
name: sit-artifact-redteam
description: Independently red-team Sit by Me planning, prompts, generated images, and walk masks before adoption. Use after an authoring pass or before changing an asset to ready; do not use to generate assets.
---

# Sit by Me Artifact Red Team

**画像の保存形式（#68決定、2026-10-19）**: imagegenの出力（PNG）→切り出し→**WebP（非可逆・品質85・アルファ保持）**にして正本パスへ保存する（`magick in.png -quality 85 out.webp`、または `verification/characters/tools/key_*.py` が直接WebPで出す）。PNGは残さない（name-name のTUIは WebP のみデコードできる）。実寸（不変）・アルファ（`magick in.png -alpha extract` と変換後WebPの同コマンドを `compare -metric AE` で比べAE=0）の検査はWebPで行う。寸法ゲートの基準（1920×1080等）は変えない。

失敗の来歴（完全prompt・参照・実寸/検査結果・判定理由）はIssueまたはレビュー文書に記録し、失敗画像はリバート／削除する（バイナリを別置き場に保存しない）。

Find evidence that a proposed or generated artifact is wrong before it is adopted. This is an **independent** review: the reviewer must not be the author of the target specification, prompt, image, mask, or prior review, and must receive the raw artifact and canonical records rather than the author's conclusion.

## 一意解釈監査（このスキルの全行より優先）

レビューで `少し`、`やや`、`広い`、`狭い`、`近い`、`遠い`、`自然`、`十分`、`明瞭`、`目立つ`、`適切`、`雰囲気`、`おおよそ`、`〜風`、`斜め`だけ、`奥行き`だけを根拠にしてはならない。各判定には原文ファイル行、参照画像パス、画面座標、ピクセル数、個数、色コード、または定義済み方角を添える。生成入力に変換不能な曖昧語が残っている場合は `major` とする。台帳にない道・水路・直線・直交・格子・等間隔の追加は `blocker` とする。

## ミニチュア材料監査

ミニチュア背景をレビューするとき、「模型に見える」は判定語として使わない。生成入力の材料・工作道具・加工法を原文で読み、原寸画像で各項目を一つずつ確認する。`foamboard`、段ボール断面、`paper clay` の刻み、綿雪、紙・紙やすりの地面、セロファン水、スポンジ木、マスキングテープ、PVA接着剤、ポスターカラーの筆跡のうち、生成入力で指定されたものが三つ未満しか確認できない候補は `major` とする。実景写真・実物素材・CG均一面しか確認できない場合は `blocker` とする。

## Inputs and canonical sources

Use the #68 migration ledger for actual paths: `assets/images/{enemies,summons,characters,fields,battle-backgrounds}/`. Match canonical M/S/C/BG IDs and MAP IDs (area code + sequence, e.g. TRM-01) and distinguish reference and legacy roles (pre-processing originals/raw are not kept). There is no candidate folder or version suffix: new generations overwrite the canonical path (committed if kept, reverted via git if not). Adoption is the ledger status, never the file location; a file at a canonical path proves neither adoption nor a passed review. Review the exact committed version (commit hash). Historical reviews retain old paths; follow the relocation/deletion ledger and source commit rather than treating tombstones as live inputs.

For a MAP review, first read:

- `docs/content-registry.md`
- target row in `docs/map-asset-registry.md`
- target row in `docs/map-specifications.md`
- applicable graph in `docs/map-topology.md`
- `docs/map-reference-research.md`
- `docs/art-direction.md`, `docs/assets-policy.md`, and `.claude/skills/sit-field-background/SKILL.md`

For an enemy review, read `.claude/skills/sit-enemy-sprite/SKILL.md`, the target `M` row, its source prompt, and the actual RGBA candidate. Record the declared `gridClass`, canvas px, transparent-pixel bounding rectangle, and whether head and torso each show the front plane and right plane. A 90° right-profile head or torso, or a gridClass not declared in the target row is a `blocker`. Canvas dimensions and edge contact are recorded for human review, not automatic failures.

For a summon review, substitute `.claude/skills/sit-summon-sprite/SKILL.md` and the target `S` row. For magic, ability, job, event, or scenario review, use the corresponding type register from `content-registry.md`. Read the actual candidate and its source prompt/mask when they exist; never infer success from a filename.

## Review method

Declare the reviewed stage first: `contract/prompt`, `raw-image`, or `mask/adoption`. A pass is limited to that stage and exact artifact version. Before any paid generation, review the **complete outgoing prompt** and actual reference pixels against the verbatim source bundle, including incoming and outgoing edges and peer records. Missing images/masks do not fail a prompt review; unresolved geometry or architecture does. A raw-image pass permits mask authoring, never adoption. Mask/adoption requires the reviewed new image and its matching outputs. Do not inherit old passes after a new generation or material prompt correction.

For #51, measure each raw file independently: target 1920×1080, or 16:9 1672×941 or 1672×940 when the image tool cannot return 1920×1080 (shared exterior reference: dimensions not gated); any other size fails and is never rescaled. A filename or copied review claim is not evidence. Every old candidate and old mask is reference-only. Record each reference's role and forbidden traits after viewing it: a wrong separate-building, outside-passage, or cutaway image cannot be an architecture reference merely because the prompt says to ignore its geometry. The shared roof/exterior reference must pass before interiors; it has no traversal-mask requirement.

For miniature materials, cite original-size pixel coordinates for at least three specified material/construction cues. A list of materials in the prompt is not image evidence. Check actual paper/cotton/cut edges against the declared processing method; do not call photoreal asphalt, tiles, velvet, or uniform CG a pass because the composition is small.

1. Construct a checklist from the register **before** looking at the author's self-assessment. Check ID coverage, lifecycle/status, era, location, one-line role, inter-record references, and every explicit `TBD`.
2. Test topology in both directions against the canonical connection table: reciprocal map/door ID, declared edge, era/class, and north-up bearing. Do not invent matching road width, pixel position, or angle across two images as an additional criterion. Flag a geographic contradiction even when legacy images appear to fit.
3. For a field image, inspect the actual pixels and mask for: all required exits, no path on forbidden edges, no blocked required route, wheelchair width/turning, separate optional dead ends, no accidental people/text, shallow top-down handmade-diorama construction, specified weather/season/period/grime, landmark uniqueness, and reference consistency.
3a. **Exterior reference of a building group (required):** check that the constituent buildings visibly connect as a required, continuous group via the specified roofed corridors; that no detached separate building has crept in; and never pass on a prohibition-only basis (e.g. "it is not a forbidden passage" is not a pass). The connection must be positively visible in the pixels. Concrete criteria: roofed corridor wings touch the left and right walls of the main hall; the wing roofs continue without a break into the main-hall, residence and kindergarten roofs; both ends of each wing abut walls, and no ground gap or snowfield passes between roof and roof; there is no direct corridor between residence and kindergarten. An open-air outer corridor fails; a roofed and walled corridor wing is mandatory.
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

Write a dated review under `docs/reviews/artifact-redteam/` and link it from the relevant registry row. A review must name the reviewer, target ID, canonical sources inspected, reviewed artifact paths with commit hash (failed images are reverted, so record prompt/measurements/verdict instead of keeping binaries), each check and evidence, findings, and final disposition. If no issue is found, explicitly list the checks performed; a bare “looks good” is invalid.

## Independence gate

Do not repair the candidate while reviewing it. Hand blockers back to the authoring workflow, then require a **new** red-team pass after a material correction. The reviewer may propose a correction, but may not mark its own correction `ready` or `pass`.

## Stop conditions

- Any unresolved TBD, missing source, missing reciprocal edge, or missing mask blocks adoption/`ready`. At earlier stages, require only the artifacts appropriate to that stage; explicitly list later-stage checks as pending rather than claiming they passed.
- An image may remain a `legacy` record, but it cannot be used as proof that a contradictory topology is correct.
- Do not generate replacements, revert or delete images, or change public/issue state in this skill unless separately directed.

共通（#68運用）: 合格済みの正本を上書きする前に、現行がコミット済みか確認する。不合格テイクをコミット済みにしてしまった場合は `git revert <commit>`、または `git checkout <旧commit> -- <path>` で戻す。
