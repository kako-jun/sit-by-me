# S006 第1形態 contract/prompt review（2026-10-21）

## 現行判定: 修正版 pass

Issue #141 コメント [6311998804](https://github.com/kako-jun/sit-by-me/issues/141#issuecomment-6311998804) の修正版を、前回からの実質的な変更として再審査した。第1形態に未決のオレンジ系照明を加えていた前回のmajorは解消されている。現行promptは第1形態の記録済み契約に適合し、prompt段階では生成へ進める。これは画像候補の品質・透過・採用を認める判定ではない。

## 修正版の照合

- 第1形態は「夜空に浮かぶ暗いが美しい積乱雲だけ」で、金箔風の抽象雲は第2〜4形態だけ（`docs/monsters.md:88`; `docs/art-direction.md:130`; `.claude/skills/sit-summon-sprite/SKILL.md:22`; Issue #141 コメント 6311971898, 6311998804）。修正版は雲のみとし、金箔風意匠を明示的に除外する。
- 対象ID・ファイル名・`gridClass 2x3` はコメント 6311971898 に明記され、台帳の契約と一致（`docs/monsters.md:249`）。スキルは `gridClass` を占有セルと定義し、px寸法を指定しない（`.claude/skills/sit-summon-sprite/SKILL.md:22`）。
- 修正版からオレンジ系の色・照明指定がなくなった。オレンジ系はM001に響く雷竜の色として定義される（Issue #78; `docs/decisions.md:265`; `docs/monsters.md:88,250-251`）ため、第1形態の雲に適用しない修正は妥当。
- `photorealistic`、透明背景、単体、枠・台座・接地影なしは共通方針と一致（`docs/assets-policy.md:5,13`; `.claude/skills/sit-summon-sprite/SKILL.md:20,26,28`）。夜空に浮かぶ積乱雲という核指定は、S006台帳の第1段階に一致（`docs/monsters.md:88`; `docs/art-direction.md:130`）。
- 月・星・雨・可視の雷・雲核・氷・閃光・竜・動物・ドクロ・金箔風雲・文字・枠・台座・接地影を排除する条件は、雲だけという段階契約と矛盾しない。story.mdの後段で定義される雲核・雷竜の造形（`docs/story.md:168-169`）を第1段階へ混入していない。
- 召喚獣の入力は記録済みのID、台帳、grid、透明条件などに限り、台帳にない造形を補わない（`docs/content-registry.md:31-37`; `.claude/skills/sit-summon-sprite/SKILL.md:14-16`）。修正版で追加された夜間照明と雲の陰影は、既指定の夜の積乱雲を描くための一般的な光・陰影の表現で、未決の色や物体を追加しない。

### 修正版の確認事項

- Findings: なし。
- 45°面チェック: 雲だけで顔・頭部・胴体がないためN/A（`.claude/skills/sit-summon-sprite/SKILL.md:20`）。
- 生成後に確認する事項: 実寸、alpha、透明余白、外接矩形、画面内で切れて見えないこと、台帳原文との一致。prompt記載だけで透過は証明できない（`.claude/skills/sit-summon-sprite/SKILL.md:26,28`）。

## 前回判定の履歴

## 初回判定（修正前コメント 6311971898）

**major — prompt review only。生成前に、雲の色・光の表現を決定して具体化する必要がある。**

## 対象・独立性

- 対象: S006 第1形態 `assets/images/summons/S006-cloud.webp`、gridClass `2x3`
- レビュー段階: `contract/prompt`。画像候補はまだなく、画像品質・透過・採用可否は未審査。
- レビュー対象prompt: [Issue #141 のコメント 6311971898](https://github.com/kako-jun/sit-by-me/issues/141#issuecomment-6311971898) に記載された「第1形態・生成前プロンプト案」。同コメント内の対象メタデータも確認。
- 参照した正本: [content-registry.md](../../content-registry.md)、[monsters.md §S006・サイズ区分](../../monsters.md)、[story.md](../../story.md)、[art-direction.md](../../art-direction.md)、[assets-policy.md](../../assets-policy.md)、[召喚獣スプライトskill](../../../.claude/skills/sit-summon-sprite/SKILL.md)、[red-team skill](../../../.claude/skills/sit-artifact-redteam/SKILL.md)、[Issue #78](https://github.com/kako-jun/sit-by-me/issues/78)。

## 根拠確認

- S006 は召喚獣の正本台帳に属する（`docs/content-registry.md:21,31-37`）。
- 第1形態は「夜空に浮かぶ暗いが美しい積乱雲だけ」、第2〜4形態だけが金箔風の抽象雲を伴う（`docs/monsters.md:88`; `docs/art-direction.md:130`; Issue #141 コメント 6311971898）。prompt は第1形態に金箔風の雲を明示的に禁止しており、修正後のユーザー指示と一致する。
- 第1形態は `2x3`（`docs/monsters.md:249`、Issue #141 コメントの対象メタデータ）。
- 召喚獣の戦闘マスターは実写風、透過背景の単体素材で、枠線・台座・接地影なし（`docs/assets-policy.md:5,13`）。prompt はこれらの条件を含める。
- 物語上の終盤の雷竜は雲核・帯状雲・氷・閃光・雷をまとい、雲と雷に浮くドクロの顔を持つ（`docs/story.md:168-169`）。ただし第1形態を雲だけとする新しい段階分けはIssue #141 の明示決定であり、後段の物語記述を第1形態へ持ち込まない。
- 竜の形・色をM001に響かせ、雷はオレンジ系スプライト色にする決定はIssue #78 と `docs/decisions.md:265` にある。これらは第1形態の雲の縁をオレンジブラウンで照らすことまでは指定していない。

## Findings

### Major — 雲の縁の色と照明が台帳にない

prompt は「restrained warm orange-brown light along a few cloud edges」と指定するが、台帳は第1形態を「暗いが美しい積乱雲だけ」とし、オレンジ系を明示しているのは雷竜・スプライト雷の決定である。色コード、照らす縁の数、または第1形態にもオレンジ色を適用する根拠は記録されていない（`docs/monsters.md:88`; `docs/art-direction.md:130`; Issue #78; `docs/decisions.md:265`）。召喚獣skillは入力に色コードと個数を含め、台帳にない姿を補わないよう求める（`.claude/skills/sit-summon-sprite/SKILL.md:14-16`）。

「dark」「beautiful」「ominous」「restrained」も再現可能な色・明度条件に変換されていない。red-team skill は変換不能な曖昧語をmajorとする（`.claude/skills/sit-artifact-redteam/SKILL.md:14-16`）。第1形態の雲にオレンジ色を含めるか、色・照明条件を先に確定し、promptの形容を指定可能な条件へ置き換えること。

## Passした条件 / 後段で未審査の条件

- 第1形態が雲のみであること、夜空に浮かぶ積乱雲であること、金箔風の抽象雲を含めないこと、背景・地平線・月・星・雨・雷・雲核・氷・閃光・竜・動物・ドクロ・文字・枠・台座・接地影を除外することは、記録済み契約と矛盾しない。
- 透過背景と余白を要求しているが、透過・実寸・外接矩形・余白の実ピクセル検査は生成後に行う。
- 45度面の確認は、雲だけで顔・頭部・胴体を持たない形態なので現段階ではN/A。生成物に顔などを足した場合は再審査が必要。
- 絵の見栄え、実写風の達成度、グリッド内での見切れ、アルファ、寸法、M001とのピクセル比較は候補未生成のため未審査。

## 処置

作者側で第1形態の色・照明を決定し、改訂した完全promptで新しいcontract/prompt reviewを受けること。現時点では生成・採用適格とは判定しない。
