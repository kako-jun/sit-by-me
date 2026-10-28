# S006 第2形態 contract/prompt 独立レビュー

- Reviewer: Codex subagent `/root/s006_stage2_review` (independent of the S006 specification and prompt author)
- Target: S006 第2形態 `assets/images/summons/S006-awakening.webp`
- Review stage: `contract/prompt`
- Raw input: GitHub Issue #141 comment `6312109862`, retrieved 2026-10-21; complete text copied below.
- Candidate image: not generated at this stage.
- Verdict: **major — revise before generation**

## Raw prompt reviewed

> Create one isolated, photorealistic battle-summon sprite on a transparent background. Preserve the recognizable mass and layered silhouette of the previous gray nighttime cumulonimbus. In the cloud, form one large, roughly circular opening with an indistinct, soft, uneven boundary, like a deep abyss rather than a clean geometric portal. Inside the opening, make the universe appear to extend into depth: a dark cosmic expanse with stars and nebulae receding inward. Keep the cloud mostly gray, with muted yellow beginning to emerge in parts of the cloud and rim; do not make orange dominant yet. Around the storm cloud, include abstract Japanese-painting cloud forms that look like hammered gold leaf, following the cloud as a decorative motif. Keep all shapes inside one coherent isolated sprite. No dragon or animal silhouette, no skull, no dragon-shaped lightning, no landscape, no horizon, no sky backdrop, no moon, no text, no frame, no base, no ground shadow. Keep the whole sprite visible with transparent margin.

Issue metadata names the output path and gridClass as `2x3`; the comment does not list any reference image path or identify an image attached to the generation request.

## Contract declared from canonical records

- S006 is the lightning summon in the adult-era first-run finale at Kanazawa Castle, enemy in the first run and strongest ally in the second (`docs/monsters.md:88`; `docs/story.md:93,95`).
- The four-form sequence is currently: stage 1 gray night cumulonimbus only; stage 2 an indistinct circular abyss-like hole in a cloud, universe inside, gray retained as yellow begins, with gold-leaf-like abstract clouds around it; stage 3 multidirectional lightning with a vague impression of multiple dragon faces; stage 4 skull-faced dragon with dragon-shaped lightning, the third form’s lightning retained. (`docs/monsters.md:88`, `docs/art-direction.md:130`; Issue #141 comments, especially `6311985956`, `6312028358`, and `6312109862`.)
- Stage 2 gridClass is `2x3`; stage 3 is `2x4`; stage 4 is `2x6` (`docs/monsters.md:249-251`; `.claude/skills/sit-summon-sprite/SKILL.md:22`).
- The gold-leaf-like abstract cloud motif applies only to stages 2–4. The earlier “all four” instruction was explicitly superseded in Issue #141 by comment `6311964346`.
- The style is a photorealistic generated battle image; summon masters are isolated on transparency without frame, base, or contact shadow (`docs/assets-policy.md:5,13`).
- The wider story describes the final lightning dragon retaining intertwined clouds, cloud cores, ice, flashes, and lightning, with a skull-like face (`docs/story.md:168-169`; `docs/art-direction.md:114`). This describes the final target, not additional stage-2 requirements.
- Issue #78 establishes a non-biological “竜” direction, orange relation to M001, and the distinction from biological M003 “龍”. Its earlier instruction not to remake S006 until explicitly instructed is superseded by the later user request and Issue #141; it does not block this review.

## Checks and findings

1. **Identity, role, stage, lifecycle, and grid — pass.** The target is S006 stage 2, the named output is distinct from the old `S006.webp`, and its `2x3` grid matches the stage-2 contract (`docs/monsters.md:88,249`; Issue #141 comment `6312109862`). The stage is not described as the final skull-faced dragon, consistent with `docs/story.md:169` and the current S006 row.
2. **Color and progression — pass with one reference limitation below.** Gray remains dominant and yellow begins; orange is explicitly held back. This matches the stage-2 and transition requirements in `docs/monsters.md:88`, `docs/art-direction.md:130`, and Issue #141 comment `6312028358`.
3. **Gold cloud motif — pass.** It is included in stage 2 as required by the updated scope (Issue #141 comment `6311964346`; `docs/monsters.md:88`; `.claude/skills/sit-summon-sprite/SKILL.md:22`). The earlier contradictory “all four forms” comment was corrected in the same issue and is not current contract.
4. **Isolated sprite and exclusions — pass.** Transparency, no scenery/backdrop, no frame/base/contact shadow, and no dragon/skull imagery align with `docs/assets-policy.md:5,13`, the stage-2 description at `docs/monsters.md:88`, and `.claude/skills/sit-summon-sprite/SKILL.md:20,26`.
5. **Prior-form continuity reference — major.** The prompt requires preserving the “recognizable mass and layered silhouette” of stage 1, and the user specified that each form retain something from the preceding form (Issue #141 comment `6312028358`). However, the outgoing prompt record names no reference image path, and the image request’s reference inputs are not recorded. The prior form exists at `assets/images/summons/S006-cloud.webp` (`docs/monsters.md:88`; workspace file observed, currently untracked), but without declaring/passing it as a reference the generator has no concrete silhouette to preserve. The summon skill requires recording reference image paths and supplying the actual reference pixels for prompt review (`.claude/skills/sit-summon-sprite/SKILL.md:16,26`; red-team instructions in `.claude/skills/sit-artifact-redteam/SKILL.md`, “Review method”). Add the exact reference path and confirm it is actually attached to the generation input, or replace the preservation claim with fully specified shape cues. Do not claim continuity has been checked until then.
6. **Cosmic details — minor unsupported elaboration.** “Stars and nebulae receding inward” is more specific than the user’s “宇宙が広がってるような敵” / current ledger’s “その内側に宇宙が広がる” (`docs/monsters.md:88`; Issue #141 comment `6311985956`). The broad cosmic interior is supported, but stars, nebulae, and their receding arrangement are not separately fixed by the source. To keep the prompt within recorded intent, either reduce this to a dark cosmic expanse extending inward or record those visual details as an accepted design choice before generation.

## Sources inspected

- `docs/content-registry.md:1-37` — registry roles and generation workflow; summon records point to `monsters.md` / `story.md`, art rules to assets policy and art direction.
- `docs/monsters.md:88,194-201,249-255` — S006 row and size contracts.
- `docs/story.md:93-96,164-170` — summon role, final encounter, cloud-to-dragon story continuity.
- `docs/art-direction.md:114,130` — thunder-dragon distinction and S006 four-stage art direction.
- `docs/assets-policy.md:3-14` — visual style and transparent isolated summon master requirements.
- `.claude/skills/sit-summon-sprite/SKILL.md:12-28` — source, reference, grid, transparency, and generation gates.
- `.claude/skills/sit-artifact-redteam/SKILL.md` — independence, input, prompt-review, evidence, and stop requirements.
- Issue #78 (current body) and Issue #141 comments `6311964346`, `6311985956`, `6312028358`, `6312109862`.

## Disposition

**Do not generate from this recorded request yet.** Resolve the missing prior-form reference input first. The optional cosmic detail should also be narrowed or explicitly decided. This review covers only contract/prompt; actual pixels, alpha, crop, and stage-to-stage visual continuity remain pending raw-image review.

## Independent recheck — 2026-10-21

- Reviewer: Codex subagent `/root/s006_stage2_recheck`, independent of the S006 specification, prompt, and prior review author.
- Target: S006 第2形態 `assets/images/summons/S006-awakening.webp`.
- Review stage: `contract/prompt` recheck of Issue #141 comment `6312135944`.
- Prior result retained: the earlier reviewed prompt remains **major** for missing reference pixels and **minor** for unsupported stars/nebulae details. This entry does not rewrite that historical finding.
- Current disposition: **major — generation input not yet evidenced**.

### Recheck evidence

1. **Corrected prompt text — pass.** Issue #141 comment `6312135944` now names `assets/images/summons/S006-cloud.webp` and limits its use to preserving the previous gray nighttime cumulonimbus mass and silhouette; it explicitly says not to copy the backdrop. The actual file exists in the workspace and is a 1536×1024 WebP with alpha. Its visible subject is the stage-1 gray cumulonimbus, so the stated silhouette-continuity role is appropriate. The prompt no longer adds stars or nebulae; “a cosmic expanse that appears to continue inward into depth” stays at the level of the recorded cosmic interior (`docs/monsters.md`, S006 row; Issue #141 comment `6311985956`).
2. **Current S006 contract — pass.** The S006 row requires stage 2 to retain the gray cloud and abyss-like circular opening while yellow begins, and to add gold-leaf-like abstract cloud forms. The grid table assigns stage 2 `2x3`; `.claude/skills/sit-summon-sprite/SKILL.md` explicitly lists S006's stage-specific exception and motif scope. The prompt matches these requirements and excludes stage-3/4 dragon features.
3. **Reference-pixel handoff — major remains.** Comment `6312135944` records a path and textual role, but does not evidence that the generation call actually receives the image pixels. The file's presence in the workspace is not itself an attached reference input. No generation call or request record was provided for this recheck, so I cannot confirm that `assets/images/summons/S006-cloud.webp` is passed through the tool's image-reference input. `.claude/skills/sit-summon-sprite/SKILL.md` requires the actual reference image path in generation/review inputs; `.claude/skills/sit-artifact-redteam/SKILL.md` requires the complete outgoing prompt and actual reference pixels to be reviewed before generation. Attach this exact file as an image reference in the outgoing generation request, and retain the request evidence, before treating the major as resolved.
4. **Other contract checks — pass at prompt stage.** `docs/content-registry.md` requires prompt construction from canonical records and no invented visual details. `docs/story.md` and `docs/art-direction.md` describe the cloud-to-dragon finale; stage 2 is not required to depict the final skull or dragon. `docs/assets-policy.md` and the summon skill require an isolated transparent sprite without a frame, base, or ground shadow; these are excluded. Issue #78's M001/orange final-dragon direction concerns later forms and does not contradict the gray-to-yellow stage-2 prompt. Its “do not remake until instructed” clause was superseded by the later explicit S006 creation request recorded in Issue #141.

### Sources inspected

- `docs/content-registry.md` (generation/source bundle rules).
- `docs/monsters.md` (S006 row and S006 stage grid rows).
- `docs/story.md` (M004→M005 and S006 finale continuity).
- `docs/art-direction.md` (S006 four-form visual contract and M001/M003 distinction).
- `docs/assets-policy.md` (isolated summon style and transparency restrictions).
- `.claude/skills/sit-summon-sprite/SKILL.md` and `.claude/skills/sit-artifact-redteam/SKILL.md`.
- Issue #78 (M001 relation, orange final dragon, and superseded hold instruction).
- Issue #141 comment `6312135944` and workspace reference pixels `assets/images/summons/S006-cloud.webp` (1536×1024 WebP with alpha; viewed for subject/role only).

### Disposition

The textual prompt correction resolves the unsupported cosmic-detail minor and makes the intended reference role clear. The earlier reference blocker is **not yet resolved**: the issue comment does not prove that the actual image pixels enter the outgoing generation request. Do not generate until that exact image is attached as a reference and the outgoing request can be reviewed. This is only a contract/prompt review; generated pixels, transparency, framing, and visual stage continuity remain pending.

## Independent recheck — 2026-10-21 (reference pixels and request parameters)

- Reviewer: Codex subagent `/root/s006_stage2_finalreview`, independent of the S006 specification, prompt, image, and earlier reviews.
- Target: S006 stage 2 `assets/images/summons/S006-awakening.webp`.
- Review stage: `contract/prompt` recheck of Issue #141 comments `6312135944` and `6312163197`.
- Earlier findings above are retained as historical results. This entry supersedes their disposition for the current text/reference handoff only.

### Current contract and prompt

Issue #141 comment `6312135944` supplies the full current prompt. It specifies a transparent, isolated stage-2 sprite; a roughly circular, indistinct abyss opening with a cosmic interior continuing inward; gray cloud with yellow beginning and orange not yet dominant; and the gold-leaf-like abstract cloud motif. It excludes dragon/animal silhouettes, skull, dragon-shaped lightning, scenery, frame, base, and ground shadow. Comment `6312163197` specifies the actual tool input `referenced_image_paths: ["［ローカルパス省略］"]` and limits its role to continuity of the cloud mass and silhouette.

I opened the actual reference image at original resolution. It is a 1536×1024 WebP showing a single dark gray cumulonimbus with a broad, layered upper crown and a deeper stacked cloud mass below. The upper cloud spreads laterally; the lower body gathers into dense rounded layers. The image corners have alpha 0 and the measured alpha range is 0–0.996078, so the dark areas visible in the viewer are not evidence of an opaque backdrop. This is an appropriate reference for the requested cloud-mass/silhouette continuity. The prompt explicitly forbids copying its backdrop, and the tool parameter passes this file as pixels rather than merely naming its path.

The current S006 row (`docs/monsters.md:88`) and art-direction row (`docs/art-direction.md:130`) support the stage-2 subject and color/motif transition. Stage-2 grid is `2x3` (`docs/monsters.md:249`; `.claude/skills/sit-summon-sprite/SKILL.md:22`). The gray-to-yellow direction, delayed orange, and gold motif match Issue #141. The prompt does not import the stage-3 multiple-face lightning or stage-4 skull dragon. Cosmic detail is limited to the approved inward-extending cosmic expanse, resolving the prior unsupported-stars/nebulae finding.

### Remaining finding

1. **Major — transparent-background tool setting is not specified.** The prompt says “on a transparent background,” but Issue #141 comment `6312163197` records only `referenced_image_paths`. The summon skill requires transparency to be requested in the tool setting as well (`.claude/skills/sit-summon-sprite/SKILL.md:26`); the image tool exposes `transparent_background`. Include `transparent_background: true` in the outgoing call. This is a generation-input requirement, not a demand for post-generation evidence.
2. **Non-blocking source wording drift.** `docs/monsters.md:249` still describes the second 2x3 form as “雲核と気象要素が集まり始める形態,” while the current S006 row at line 88 and art-direction at line 130 specify the abyss-like circular opening and inward cosmic expanse. The stage-2 prompt follows the detailed current row. The older grid-table gloss should be synchronized in product docs, but it does not make this prompt's subject indeterminate because the detailed S006 entry is explicit.

### Sources inspected

- Issue #141 comments `6312135944`, `6312163197` (current complete prompt and explicit image-reference argument).
- Actual `assets/images/summons/S006-cloud.webp`, opened at original resolution; `identify` reports 1536×1024 WebP with alpha; corner alpha 0, alpha min 0, max 0.996078.
- `docs/content-registry.md:5-11,32-41`; `docs/monsters.md:88,249-255`; `docs/story.md:93-95,165-169`; `docs/art-direction.md:114,130`; `docs/assets-policy.md:3-20`.
- `.claude/skills/sit-summon-sprite/SKILL.md:12-26`; `.claude/skills/sit-artifact-redteam/SKILL.md`.
- Issue #78 current body: M001 resemblance/orange direction and its hold instruction, superseded by the later explicit creation request in #141.

### Disposition

**Major — add `transparent_background: true` to the outgoing image generation call before generation.** The image reference is now explicit and appropriate, and the cosmic-detail concern is resolved. Once the tool setting is included, the contract/prompt review passes for the exact prompt and reference specified above. This review does not assess generated pixels, alpha, cropping, or visual continuity after generation.

## Independent final gate — 2026-10-21

- Reviewer: Codex subagent `/root/s006_stage2_finalgate`, independent of the S006 specification, prompt, image, and prior reviews.
- Target: S006 第2形態 `assets/images/summons/S006-awakening.webp`.
- Review stage: `contract/prompt` final check against Issue #141 comments `6312135944`, `6312163197`, and `6312196628`.
- Historical findings above remain as an audit trail. This entry checks their listed corrections against the current contract; it does not imply that an image-generation request has already run.

### Checks and evidence

1. **Current stage-2 subject and transition — pass.** The complete prompt in #141 comment `6312135944` specifies a gray nighttime cumulonimbus with one indistinct, roughly circular abyss opening and a cosmic expanse continuing inward; yellow begins while orange is not dominant. It includes the abstract Japanese-painting cloud forms resembling hammered gold leaf. Those terms agree with the current S006 row in `docs/monsters.md:88`, the S006 art-direction row `docs/art-direction.md:130`, and the user decisions recorded in #141 comments `6311964346`, `6311985956`, and `6312028358`. The prompt excludes dragon/animal silhouettes, skulls, and dragon-shaped lightning, preserving the later forms for stages 3 and 4.
2. **Grid and prior table wording — pass.** `docs/monsters.md:249` now describes S006 stages 1 and 2 as the gray cumulonimbus with the abyss-like circular opening and cosmic interior; stage 2 is included in the `2x3` row. The summon skill explicitly lists S006 stage 2 as `2x3` (`.claude/skills/sit-summon-sprite/SKILL.md:22`). No pixel canvas dimensions are inferred from that grid class.
3. **Reference subject and handoff — pass.** I inspected the actual `assets/images/summons/S006-cloud.webp` (1536×1024 WebP). Its subject is the adopted stage-1 dark gray, layered cumulonimbus with a broad upper mass. This is pertinent to the specified cloud-mass/silhouette continuity, and the prompt limits the image's role to that continuity while forbidding copying its backdrop. Issue #141 comment `6312163197` records the full absolute path under `referenced_image_paths`, so the reference is specified as actual image input, not prompt text alone. The existing measurements recorded in the preceding independent review report alpha range 0–0.996078 and transparent corners; no opacity/background conflict is evidenced.
4. **Transparent isolated-sprite requirements — pass for the planned request contract.** The prompt requires a transparent background and excludes landscape, horizon, sky backdrop, moon, text, frame, base, and ground shadow. Issue #141 comment `6312196628` explicitly adds `transparent_background: true` as a required image-generation API argument. Together with the reference-path argument in `6312163197`, the requested tool settings are complete. The summon skill requires transparency at the tool setting (`.claude/skills/sit-summon-sprite/SKILL.md:26`); `docs/assets-policy.md:13` requires a transparent isolated summon master without frame/base/contact shadow.
5. **Canonical source alignment — pass.** `docs/content-registry.md:5-11,32-41` requires the source ledger and skill bundle to govern prompt construction. `docs/story.md:93,167-169` places the cloud-to-dragon sequence at the finale; it does not require the final skull dragon in stage 2. `docs/art-direction.md:114,130` keeps the thunder “竜” distinct from biological M003 “龍” and supports the later orange/M001 relation. Issue #78's orange/M001 direction applies to the final dragon; its earlier hold on recreating S006 has been superseded by the later explicit creation request in #141. `docs/assets-policy.md` and both skills were checked for the isolated-sprite, reference, grid, transparency, and independent-review requirements.

### Current disposition

**Pass for contract/prompt; eligible to generate one stage-2 candidate with the recorded request settings.** The ready-to-send request must use `referenced_image_paths: ["［ローカルパス省略］"]` and `transparent_background: true`, as separately recorded in #141. No actual generation call was part of this review. Generated-pixel checks, alpha measurements, crop, and human adoption remain pending and require their own reviews.

### Sources inspected

- `docs/content-registry.md:5-11,32-41`; `docs/monsters.md:88,249-255`; `docs/story.md:93,167-169`; `docs/art-direction.md:114,130`; `docs/assets-policy.md:3-20`.
- `.claude/skills/sit-summon-sprite/SKILL.md:12-28`; `.claude/skills/sit-artifact-redteam/SKILL.md` (independence, source/pixel input, prompt-stage scope, and disposition rules).
- Issue #78 current body; Issue #141 comments `6311964346`, `6311985956`, `6312028358`, `6312135944`, `6312163197`, `6312196628`.
- Actual reference pixels `assets/images/summons/S006-cloud.webp`, inspected at original resolution; file metadata and prior recorded alpha measurements cited above.
