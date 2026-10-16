# 寺町最終修正版・独立red-team画像監査

- 日付: 2026-10-16
- レビュアー: 独立 red-team reviewer（候補画像・prompt・mask・作者自己評価の作者ではない）
- 対象: E09 v3、E11 v4、E12 v3の実PNG
- 正本: `docs/content-registry.md`、`docs/map-asset-registry.md`、`docs/map-specifications.md`、`docs/map-topology.md` v2、`docs/map-reference-research.md`、`docs/art-direction.md`、`docs/assets-policy.md`、`.claude/skills/sit-diorama/SKILL.md`、`.claude/skills/sit-artifact-redteam/SKILL.md`

## 結論

- **E09 v3: blocker。** 必須の `E08.left → E09.top` に対し、left edgeから石段へ入る連続路が実画像にない。topの出口候補はあるが、片側だけでは接続契約を満たさない。
- **E11 v4: pass（画像契約。mask工程可）。** bottom山門、left幼稚園通用門、right庫裏門、main hall、親鸞像候補を実画素で確認した。main hallまでの中央石畳には目視できる段差・階段がなく、無段差主路としてmaskで検証可能である。
- **E12 v3: pass（画像契約。mask工程可）。** 庫裏の台所、幼馴染の個室、別位置の3つの出入口候補を実画素で確認した。

`pass` は画像契約についてだけの判定であり、採用判定ではない。全3件に traversal edit/runtime、foreground edit/runtime、door/edge `links`、prompt・Ref・adoption state がないため、**全件採用不可**である。E11/E12はmaskと往復照合の前に`ready`へ移してはならない。

## 原画像の確認

| ID | raw path | required / forbidden の検査 | 景色・模型性・無段差／扉の検査 | 判定と次の作業 |
|---|---|---|---|---|
| E09 v3 | `sample/field/rebuild/E09-teramachi-old-slope-foot-rebuild-v3-candidate.png` | `E08.right ↔ E09.left`、`E09.top ↔ E13.bottom` が正本。石段は画面上端へ到達するが、下側の石段足元は雪・石垣で閉じ、**left画像端から石段へ達する歩行路がない**。left端は家屋・石垣・非連続の暗部であり、edgeとして使えない。 | 雪の古い石段、立位期限定、段丘の石垣、手作り模型の土台はよく表現される。車椅子不可の景観としては適切だが、接続方位違反を相殺しない。人物・読める文字なし。 | **blocker / mask工程不可。** `map-topology.md`を変えず、left edgeから石段下端へ入りtop edgeに抜ける構図へ再作成する。修正版でleft/top linksと事故後orange/blackを記録して再監査する。 |
| E11 v4 | `sample/field/rebuild/E11-temple-grounds-rebuild-v4-candidate.png` | bottomの山門路、leftの遊具側通用門、rightの庫裏側通路、topの本堂入口がそれぞれ識別でき、余計な外周道路はない。 | 右下庭園に僧形の石像があり、親鸞像として使える視覚的候補になっている。綿雪・紙工作の屋根・土台が見え、手作り模型性を満たす。本堂までの中央石畳は平面の連続路として読め、目視上の階段・段差で遮られていない。 | **pass / mask工程可。** `E04.bottom`、`door-kindergarten`、`door-main`、`door-residence`を別linksにし、main hall前の回転域をwhite/assistで確認する。E01/F01/E12側と双方向のID・向き・段差を照合してから再監査する。 |
| E12 v3 | `sample/field/rebuild/E12-temple-residence-rebuild-v3-candidate.png` | 左上・右上・左下の別出入口候補があり、外周edgeとしての道路はない。画像だけではそれぞれを`door-temple`/`door-hall`/`door-playroom`へ確定できないが、3扉を割り当てる余地はある。 | 上部にシンク・コンロ・冷蔵庫・作業台を備えた台所、中央下にベッド・机・玩具を備えた幼馴染の個室が明瞭。切断模型の構成が一貫し、文字・人物なし。開口からF01/F02へ行く経路の無段差・回転域はmaskで要検証。 | **pass / mask工程可。** 3扉を一意にID化してlinks化し、`F01.door-east ↔ E12.door-hall`、`E11.door-residence ↔ E12.door-temple`、`E12.door-playroom ↔ F02.door-west`を往復照合する。台所・個室の家具と壁をblackにし、回転域を含む主路を三値maskに記録する。 |

## 共通の採用 blocker

各候補には、以下が未作成または未記録である。

1. 輪郭なし `*-traversal-edit.png`、runtime traversal、foreground edit/runtime、JSON `links`。
2. candidateごとのprompt、参照Ref、出力パス、adoption state、台帳からのレビューリンク。
3. E11/F01/E12/F02の扉遷移と、E08/F03の住戸扉を往復する実地検証。

したがってE11/E12は「mask工程へ進める」までで、採用・`ready`化は禁じる。E09は画像の再修正後にのみmask工程へ進める。候補画像は本レビューでは変更していない。
