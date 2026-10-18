# 寺町再構築 v2 候補・独立red-team再監査

> 当時のパス・判定を保持した履歴です。現行配置・削除／復元元は [#68素材対応表](../../production/asset-layout.md) を参照。

- 日付: 2026-10-16
- レビュアー: 独立 red-team reviewer（v2候補・prompt・mask・作者自己評価の作者ではない）
- 対象: `sample/field/rebuild/*-rebuild-v2-candidate.png` の10件（E04/E06/E07/E08/E09/E11/E12/E13/F01/F03）
- 正本: `content-registry.md`、`map-asset-registry.md`、`map-specifications.md`、`map-topology.md` v2、`map-reference-research.md`、`art-direction.md`、`assets-policy.md`、`sit-diorama`、`sit-artifact-redteam`
- 結論: **画像契約を満たしてmask工程へ進められる候補は E04/E06/E07/E08/E13/F01/F03 の7件。E09は接続方位違反、E11は必須の親鸞像欠落、E12は庫裏の台所・幼馴染の部屋を満たさず、現状態ではmask工程に進めない。全10件はmask/links不在のため、いずれも採用は不可。**

作者の自己評価や前版の判定を参照せず、v2の実PNGを原寸で目視してから正本と照合した。人物、読める文字、余計な屋外edgeはこの10件では検出しなかった。

## 共通 blocker（採用停止。ただし画像適合とは別）

全10件に `traversal-edit`、runtime traversal、foreground edit/runtime、edge/door `links`、候補ごとのprompt・Ref・adoption stateがない。従ってこのレビューの `mask工程` 判定は「画像上で主路と禁止辺を描き分けられる見込み」のみであり、通行可能・車椅子可・屋内外往復を証明したものではない。各MAPに次を記録するまで `blocked`/`needs-review` を維持する。

1. `sample/field/masks/` の輪郭なし三値編集PNG、runtime mask、foreground edit/runtime、JSON `links`。
2. 各候補の prompt、参照Ref、出力パス、非採用/採用状態、当レビューへのリンク。
3. E11↔F01、F01↔E12、E12↔F02、E08↔F03のdoor ID・進行方向・150cm相当の回転域を両側で一致させた往復確認。

## ID別判定

| ID | raw | 実画素で確認した required / forbidden | 無段差・模型性・固有景色 | 画像契約／mask工程 | corrective destination |
|---|---|---|---|---|---|
| E04 | `sample/field/rebuild/E04-teramachi-wide-road-rebuild-v2-candidate.png` | left/rightの消雪道路は両端へ到達し、top中央の山門路も上端へ到達する。bottomは雪庭・土台で閉じる。 | 消雪パイプ、長塀、融雪水、綿雪と段ボール土台が直接見える。主路は広く、山門の段差は主路扱いにしなければよい。 | **pass: mask工程可** | `E04.top ↔ E11.bottom`、left/rightをlinks化し、塀・雪庭・側溝をblackに記録する。 |
| E06 | `sample/field/rebuild/E06-teramachi-sento-rebuild-v2-candidate.png` | 左端の道路が銭湯前を通り、右下へ曲がってbottom edgeに到達する。top/rightの外周路はない。 | 湯気の煙突・銭湯が明瞭。綿雪、粗い紙工作の端、スノーポールがあり模型性を満たす。 | **pass: mask工程可** | `E06.left ↔ E07.top` をlinks化。建物・雪山・側溝はblack、路面の融雪水は通行クラスを明示する。 |
| E07 | `sample/field/rebuild/E07-teramachi-barrier-free-ramp-rebuild-v2-candidate.png` | top/bottomの幅ある蛇行路が両端まで連続し、left/rightは土台・建物で閉じる。 | 前版と違い綿雪、紙粘土石垣、段ボール枠、手作りの粗が見える。階段はなく、手すりつき蛇行は車椅子主路候補として十分に広く読める。 | **pass: mask工程可** | 全蛇行を連続white/assistにし、石垣・雪山をblackにする。曲線部の回転域とE06/E08のlinksをruntimeで検証する。 |
| E08 | `sample/field/rebuild/E08-teramachi-danchi-court-rebuild-v2-candidate.png` | top中央から中庭へ入る主路、right中部の石段口候補がある。left/bottomの外周路はない。 | 県営住宅、雪山、洗濯物、中庭で固有景色は明瞭。綿雪・段ボール枠で模型性も確認できる。石段を車椅子主路へ混ぜない必要がある。 | **pass: mask工程可** | `E07.top` を無段差、`E09.right` を立位期限定の別link、F03住戸扉をdoor linkとして三値maskに分離する。 |
| E09 | `sample/field/rebuild/E09-teramachi-old-slope-foot-rebuild-v2-candidate.png` | 必須は `E08.left → E13.top` だが、石段はbottom寄りからtopへ上る構図で、**left edgeの進入路が存在しない**。 | 模型性と車椅子不可の石段表現は良いが、接続違反を補えない。 | **blocker: mask工程不可** | `map-topology.md` を変えず、E08からのleft edgeを起点にtop edgeへ抜ける石段へ再構図する。立位期のみのorange/blackをmaskで示すのは修正後。 |
| E11 | `sample/field/rebuild/E11-temple-grounds-rebuild-v2-candidate.png` | bottom山門、中央本堂、leftの幼稚園通用門、rightの庫裏門が見え、外側の接続配置は読むことができる。 | 綿雪・手作り模型性は良い。しかし一言特徴である**親鸞像が画面内にない**。 | **major: mask工程保留** | 境内の歩行路を壊さず親鸞像を追加/再構図し、`door-kindergarten`/`door-main`/`door-residence`を各々links化する。E01/F01/E12との往復確認後に再レビュー。 |
| E12 | `sample/field/rebuild/E12-temple-residence-rebuild-v2-candidate.png` | 左の外扉、下の外扉、右の遊戯室扉らしき開口はあるが、F01東廊下・E11庫裏門・F02西扉を同定するID記録はない。 | 模型性は高い。一方、必須の**庫裏の台所と幼馴染の部屋が画面上で確認できない**。本堂風の仏間と広い廊下・遊戯室が主になっており、個別仕様に不適合。 | **blocker: mask工程不可** | E12を庫裏として再構図し、台所・幼馴染の部屋・F01渡り廊下・F02職員廊下の4要素を明示する。扉IDを決め、F01/F02と往復照合する。 |
| E13 | `sample/field/rebuild/E13-teramachi-slope-top-rebuild-v2-candidate.png` | bottom中央の石段とright中部の緩い道路候補があり、E09/N10の分岐に合う。left/topは土台・住宅・雪で閉じる。 | 段丘の高低差、石段、学校側へ抜ける蛇行路を分けて表現し、模型性もある。右主路は車椅子用としてmask幅の確認が必要。 | **pass: mask工程可** | bottomを立位期のみ、rightを車椅子主路として別linksにする。`E09.top ↔ E13.bottom` と `E13.right ↔ N10.left` を両側で照合する。 |
| F01 | `sample/field/rebuild/F01-temple-main-hall-rebuild-v2-candidate.png` | south中央の本堂扉とeast側渡り廊下が明瞭。画像端の偽の外部接続はない。 | 本堂の主役、冬の外側、畳廊下の連続は読める。中央通路は広いが、柱・法具周辺のwhite/blackと回転域をmaskで確認する必要がある。 | **pass: mask工程可** | `door-south`と`door-east`をlinks化し、E11.main/E12.hallとの向き・段差・回転域を相互に確認する。 |
| F03 | `sample/field/rebuild/F03-danchi-apartment-rebuild-v2-candidate.png` | bottom中央に住戸入口候補があり、不要な外周edgeはない。 | 玄関から中央の広い居室、手すりつき浴室・トイレが見え、車椅子生活を妨げない室内として読み取れる。小物・室内は模型断面として一貫する。 | **pass: mask工程可** | `E08.door ↔ F03.door`を一意なdoor linkにする。玄関・居室・水回りのwhite/assist/black、150cm相当の回転域を編集PNGで確認する。 |

## 再監査の境界

E04/E06/E07/E08/E13/F01/F03は、上記のmask・linksを作っても自動採用してはならない。E09/E11/E12は画像契約を直した新候補、残る7件はmask一式を添えた候補について、それぞれ別の独立red-teamで再確認する。
