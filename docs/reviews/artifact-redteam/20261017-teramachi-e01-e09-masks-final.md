# 寺町 E01 v3 / E09 v6 — 背景・歩行マスク独立最終レビュー

> 当時のパス・判定を保持した履歴です。現行配置・削除／復元元は [#68素材対応表](../../production/asset-layout.md) を参照。

- **レビュー日:** 2026-10-17
- **レビュー担当:** independent red-team（画像・mask・既存rawレビューの作者ではない）
- **対象:** `E01-teramachi-kindergarten-rebuild-v3-candidate.png` と
  `E09-teramachi-old-slope-foot-rebuild-v6-candidate.png`、および両候補専用の
  traversal / foreground edit・runtime mask 一式
- **結論:** **blocker — どちらも完了候補・採用候補にはまだできない。**
  E01 は自身の右端リンク記録と編集PNGが不一致で、E01 の両方の相手側を
  runtime mask で往復確認できない。E09 は候補自身の三値maskは正しいが、
  接続先の既存候補との範囲・採用状態を確定できず、候補台帳にも v6 の来歴がない。
  以下は再生成指示ではなく、mask authoring / candidate-record author に返す是正事項である。

## 読んだ正本・入力

- `docs/content-registry.md`
- `docs/map-asset-registry.md`（E01/E09 はともに `legacy`。mask/red-team/output の
  採用記録が揃わなければ ready にできないという共通契約を含む）
- `docs/map-specifications.md`（E01: right→E02 と有限の北通用門→E11、
  E09: left→E08、top→E13、車椅子不可）
- `docs/map-topology.md` の `MAP相互接続台帳 v2`
  （`E01.right ⇄ E02.left`、`E01.door-north ⇄ E11.door-kindergarten`、
  `E08.right ⇄ E09.left`、`E09.top ⇄ E13.bottom`）と寺町の段丘・屋内外遷移条件
- `docs/map-reference-research.md` の R011/R024/R025、`docs/art-direction.md`、
  `docs/assets-policy.md`、`.claude/skills/sit-diorama/SKILL.md`
- `.claude/skills/sit-field-mask/SKILL.md` と
  `.claude/skills/sit-artifact-redteam/SKILL.md`
- `docs/teramachi-rebuild-candidates.md` と
  `docs/reviews/artifact-redteam/20261017-teramachi-e01-e09-raw-candidates.md`
- 生画像:
  `sample/field/rebuild/E01-teramachi-kindergarten-rebuild-v3-candidate.png`、
  `sample/field/rebuild/E09-teramachi-old-slope-foot-rebuild-v6-candidate.png`
- 指定された各候補の `*.json`、`*-traversal-edit.png`、
  `*-foreground-edit.png`、全 runtime mask、`*-mask-overlay.png`
- 相手側として存在する E08/E13 の `rebuild-v2` JSON・編集mask一式。E02/E11 の
  対応する候補専用JSON/maskは存在しなかった。

## 共通の技術検査

| 検査 | E01 v3 | E09 v6 | 結果 |
|---|---|---|---|
| 背景・編集mask・runtime mask の寸法 | 全て 1920×1080 PNG | 全て 1920×1080 PNG | pass |
| 編集traversalの許可色 | black 1,776,455 px / white 297,145 px のみ | black 1,790,949 px / orange 282,651 px のみ | pass |
| foreground edit の許可色 | black 2,073,600 px のみ（cyan coverなし） | black 2,073,600 px のみ（cyan coverなし） | pass |
| runtime導出 | white→wheelchair/standing/assist、black→非通行、foreground alpha を実編集PNGから独立再計算し、全ファイルがビット一致 | orange→standing/assist、wheelchair と互換 `-mask` は全black、foreground alpha を含めビット一致 | pass |
| foreground 分離 | traversalにcyan等を混ぜず、前景なしを独立edit/runtimeで明示 | 同左 | pass |

`*-mask-overlay.png` は輪郭・着色を含む確認専用であり、編集用PNGには輪郭／中間色がないことも実画素で確認した。

## E01 kindergarten v3

### 実画像・接続・通行検査

| 項目 | 実証 | 結果 |
|---|---|---|
| 固有性・画風 | 雪の園庭、遊具、園舎、本堂背面／寺塀、土台と机面、綿雪・模型材料が読める。人物・可読文字・鳥居・地蔵・卒塔婆なし。 | pass |
| 禁止外周 | left/top/bottom は土台・雪・塀・建物で閉じ、外部へ出る通路を白にしていない。 | pass |
| `right → E02.left` 実画素 | 編集PNGの white は right edge の y=**460..675**（216 px）に連続。画像上もこの帯が右端の生活路へ対応する。 | **blocker** |
| `right → E02.left` 記録値 | JSON link は y=`[470,675]` と記録する一方、実編集PNGは上記 y=460..675。10 px の白い外部出口が未記録で、リンク範囲とcanonical edit sourceが一致しない。 | **blocker** |
| 北通用門 | white の短い枝はおおむね anchor `[675,315]` に届き、top edgeに出ず、right 外部路とは別の有限 door link として置かれている。 | pass（候補単体） |
| 車椅子幅・旋回 | main route は広い連続whiteで、遊具・園舎・塀・積雪はblack。門枝を含めwhiteに段差を混ぜていない。 | pass（画像内） |
| reciprocal | E02 専用JSON／maskが無く `E02.left` の実際の class・edge range を、E11 の `door-kindergarten` も同様に照合できない。名前は v2 台帳と一致するが、runtimeの往復証明にはならない。 | **blocker** |

### E01 の是正先

1. **`sample/field/masks/teramachi-e01-rebuild-v3.json` と同編集PNG**:
   right link range を編集PNGの実ピクセルに合わせるか、編集PNGを契約 `[470,675]` に合わせるかを一方に統一する。黒／白どちらを正とするかはauthorが背景上の安全幅を確認して決めること。
2. **E02/E11 の候補専用maskと各JSON**: `E02.left` と `E11.door-kindergarten` を作成し、edge/door名・class・condition・端の通行範囲を往復照合する。E01単体で `ready` にしないこと。
3. **`docs/teramachi-rebuild-candidates.md` のE01行**: v3画像、prompt全文、R011/R024/R025等の参照、mask群、今回のreview、adoption stateを記録する（現在は初回候補名だけ）。

## E09 old-slope-foot v6

### 実画像・接続・通行検査

| 項目 | 実証 | 結果 |
|---|---|---|
| 固有性・画風 | 雪を被った石段、石垣、寺塀、土台・机面があり、手作り模型として読める。人物・可読文字なし。車椅子スロープは描かれていない。 | pass |
| `left → E08.right` | orange は left edge y=535..750（216 px）に実画素で届き、石段下から踊り場へ連続。right/bottom はblack。 | pass（候補単体） |
| `top → E13.bottom` | orange は top edge x=875..1085（211 px）に実画素で届き、石段を経てleft入口へ連続。 | pass（候補単体） |
| assistのみ | universal/whiteは0 px。wheelchair-maskと互換 `-mask` は全black。standing/assist maskだけがorange主路を白として出力する。ゆえに単独車椅子が石段に入れない。 | pass |
| 禁止地形 | 石垣・塀・樹木・急段差・雪・土台はblackで、right/bottomに出口なし。 | pass |
| reciprocal edge naming | E08 JSON の `right → E09.left` と E13 JSON の `bottom → E09.top` は、双方とも `assist` として命名・classが一致する。 | pass（命名・class） |
| reciprocal edge range | E08は1254×1254のright y=590..760（13.6%高）、E09は1920×1080のleft y=535..750（20.0%高）。E13は1254×1254のbottom x=520..690（13.6%幅）、E09はtop x=875..1085（11.0%幅）。解像度／縦横比も違い、現行の候補群に「正規化して一致」とする記録・検査がないため、接続幅と位置の互換性を証明できない。 | **major** |
| 立位期／事故後 | E09側は `standing-or-companion-assist` を記録するが、E08/E13の既存maskが採用済みではなく、事故後にE09入口を閉じるゲーム状態を実際に一括確認できない。 | **major** |

### E09 の是正先

1. **E08/E09/E13 の各candidate mask契約**: 異解像度のedge rangeを、エンジンが利用する正規化座標または共通logical canvasで明示し、left/right と top/bottom の対応範囲を往復判定する。単に target 名が合うだけでは不十分。
2. **各候補の状態台帳**: E08/E13も未採用候補であることを保ったまま、立位期・介助解禁時・事故後閉鎖の条件を遷移側で検証できるよう記録する。E09のorangeを車椅子universalに変えてはならない。
3. **`docs/teramachi-rebuild-candidates.md` のE09行**: 旧 `rebuild-v3` / `blocked-regenerate` を、v6生画像・prompt・参照・mask一式・本review・adoption stateへ更新する。現状では存在しない v3候補を指しており、v6を採用根拠にできない。

## 横断的な採用ゲート

| 条件 | 状態 |
|---|---|
| raw画像レビュー | E01 v3 / E09 v6 は `20261017-teramachi-e01-e09-raw-candidates.md` で画像単体pass |
| 三値traversalとforegroundの作成・runtime導出 | 完了、上記の通り技術的にはpass |
| canonical candidate ledger のv3/v6来歴・prompt・Ref・mask・review・adoption state | 未記録 |
| E01の記録値と実edit edgeの一致 | 不一致 |
| 全相手MAPとの runtime reciprocal 検査 | E01は不能、E09はrange互換未証明 |

## 最終 disposition

**E01 v3: blocker。** 背景は再生成不要だが、right edgeのJSON/edit不一致、E02/E11の往復mask未作成、候補台帳の来歴欠落を解消し、新しい独立レビューが必要である。

**E09 v6: blocker。** 候補自身の画像・三値mask・assist限定は通過したが、E08/E13との実行時範囲互換、時期遷移、v6の候補台帳来歴が未解決である。これらを解消し、新しい独立レビューが必要である。

このレビューは採用を行わず、既存legacyを差し替えず、いずれの候補も `ready` としない。
