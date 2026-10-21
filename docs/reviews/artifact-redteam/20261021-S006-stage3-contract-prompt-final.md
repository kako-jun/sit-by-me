# S006 第3形態 contract/prompt 最終独立レビュー

- 判定段階: `contract/prompt`
- 対象: S006 雷の召喚獣・第3形態（`gridClass 2x4`）
- レビュアー: Codex sub-agent（prompt・仕様・画像の作成者ではない独立レビュアー）
- 対象Issue: #141、最新版の完全prompt comment `6312379649`、追加条件 comment `6312377373`
- 結果: **pass**。この最新版のpromptと参照で生成へ進める。
- 範囲: 生成前契約のみ。生成画像、alpha、実寸・外接矩形、表示時の切れ、採用可否は未審査。

## 確認した正本・資料

- `docs/content-registry.md` §共通の運用・プロンプト組み立て規約
- `docs/monsters.md` S006行（88行）、召喚獣gridClass表のS006第1〜4形態（249〜251行）
- `docs/story.md` 雷召喚獣の出現・雲核の後の雷竜（93、165〜169行）
- `docs/art-direction.md` 竜と龍の区別（114行）、S006四段階仕様（130行）
- `docs/assets-policy.md` 生成画像方針、召喚獣マスターの透明背景・アクスタ装飾除外（5、13行）
- `.claude/skills/sit-summon-sprite/SKILL.md` 全文
- `.claude/skills/sit-artifact-redteam/SKILL.md` 全文
- #78: M001に似た「竜」、オレンジ系の上空放電、M003の生物的な「龍」と混同させないという確定
- #141のユーザー訂正 `6312377373` と、その訂正を取り込んだ完全prompt `6312379649`
- 実参照ピクセル: `assets/images/summons/S006-awakening.webp`（1536×1024 RGBA WebP、SHA-256 `3c840fddedfab4d79e8759017915ca8ba1fd8dc8aa9ba8eaf6b98a2bc8f58555`）、目視確認済み

## 監査結果

1. **ID・段階・グリッド** — S006第3形態として明示され、台帳で定義済みの `2x4` と一致する（`monsters.md:88,250`）。2x4は占有セルであり、promptはそこから未定義のpx比率を推測していない。
2. **段階遷移と参照画像** — 第2形態参照は灰色の積乱雲に、輪郭があやふやな円形の宇宙開口を持ち、金箔風の抽象雲も伴う。promptはその実画像を「灰色の雲の塊とあやふやな円形の深淵の気配を少し残す」用途に限定し、第2形態の要素を第3形態へ継承する台帳記述に一致する。別の旧候補を参照に混ぜていない。
3. **主役・稲妻の形** — 多方向へ激しく走る雷を主役にし、雲の輪郭を越えて複数方向へ遠く突出し、枝を雲から分離して見せる。加えて全枝を荒く不規則で鋭いジグザグ／角張った形とし、滑らかな曲線・丸い枝分かれを避ける。これはユーザーの直近指定（雲から飛び出す、よりジグザグで荒く尖る）と `art-direction.md:130` に直接対応する。
4. **龍顔の暗示** — 複数の龍顔を「なんとなく」連想させる一方、個数を固定せず、くっきりした個別の顔や完成した竜体を描かない。#141のユーザー指定および「龍」と「竜」を分ける#78の意図に反しない。
5. **色と残留要素** — 雲に灰色を残し、黄色を強く、雷にオレンジを出始めさせ、最終形態のオレンジの竜をまだ主役にしない。第2形態の円形開口も背後にわずかに残す。第3形態の台帳と一致する。
6. **金箔風雲** — 金箔風の日本画的抽象雲形を召喚獣の周囲に維持する。第3形態を含む第2〜第4形態にある共通意匠であり、第1形態だけに誤って適用していない。
7. **最終形態との区別** — ドクロ顔、完成した竜本体を明示的に除外する。オレンジ竜が主役となる第4形態（2x6）を先取りしない。
8. **出力・参照引数** — 対象ファイルを実参照 `assets/images/summons/S006-awakening.webp` として `referenced_image_paths` に渡し、tool-level `transparent_background: true` を指定する。単体スプライト、余白、背景・文字・枠・台座・接地影なしはassets-policyと召喚獣スキルに合う。召喚獣は実写風生成画像という全体方針にpromptの `photorealistic` が一致する。
9. **未指定の造形を足していないか** — 稲妻の色以外の細かな色コード、枝の本数、顔の数、角度、背景環境や解剖学的な竜の顔を固定していない。追加の場所・物語・構造も入れていない。

## 完全prompt（審査対象）

> Create one isolated, photorealistic battle-summon sprite on a transparent background. Use the reference image only to retain a trace of the gray cloud mass and the vague circular cosmic abyss from the previous form. Make violent lightning forks shooting in many directions the dominant new feature. The lightning must clearly break beyond the cloud silhouette and protrude far outside its edges in multiple directions; keep the projecting branches fully visible and separate from the cloud mass. Give every lightning branch a rough, irregular, sharply zigzagging shape with angular points; avoid smooth curves and rounded forks. Let some branching patterns vaguely suggest multiple dragon faces, without a fixed count, crisp individual faces, or complete dragon bodies. Keep a trace of the prior circular cosmic opening visible behind the branching lightning. Continue the color transition: gray remains in the cloud, yellow is strong, and orange begins to emerge in the lightning; do not make the final orange dragon the subject yet. Keep the Japanese-painting cloud forms resembling hammered gold leaf around the summon. One coherent isolated sprite; no skull face, no complete dragon body, no landscape, no horizon, no sky backdrop, no text, no frame, no base, no ground shadow. Keep the whole sprite visible with transparent margin.

## Findings

Blocker・major・minor はなし。最新版のみを判定し、前回の旧prompt passや旧raw候補の結果を引き継いでいない。第3形態候補ができた後は、新しいraw-image reviewが必要。
