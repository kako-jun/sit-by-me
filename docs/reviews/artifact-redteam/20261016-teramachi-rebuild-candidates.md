# 寺町再構築候補・独立red-teamレビュー

> 当時のパス・判定を保持した履歴です。現行配置・削除／復元元は [#68素材対応表](../../production/asset-layout.md) を参照。

- 日付: 2026-10-16
- レビュアー: 独立 red-team reviewer（候補画像・プロンプト・mask・自己評価の作者ではない）
- 対象: `sample/field/rebuild/` の E01〜E13、F01〜F03（PNG 16件）
- 結論: **全16件 `blocker`、採用不可**。これは候補画像を棄却・削除する判定ではなく、採用前に必要な接続・mask・記録の欠落を止める判定である。

## 読んだ正本と実見した原画像

`docs/content-registry.md`、`docs/map-asset-registry.md`、`docs/map-specifications.md`、`docs/map-topology.md`（v2および寺町再構築時の屋外・屋内遷移不変条件）、`docs/map-reference-research.md`、`docs/art-direction.md`、`docs/assets-policy.md`、`.claude/skills/sit-diorama/SKILL.md`、`.claude/skills/sit-artifact-redteam/SKILL.md` を確認した。

各候補の実PNGを原寸で目視した。対象パスは、各行の `raw` 列に記す。人物・読める文字は全16件で見つからなかった（石像、遊具、空の案内板、宗教具は人物・文字として数えない）。

## 全候補に共通する blocker

1. **歩行・前景・リンクの記録がない。** `*-traversal-edit.png`、runtime traversal、foreground edit/runtime、画像端・扉の `links` が一件もない。したがって required edge が本当に到達可能か、車椅子主路が通れるか、扉を往復できるかを検証できない。`sit-field-mask` の三値編集PNGとJSONを各背景に作り、`map-asset-registry.md` の当該行へ全パスを記録すること。
2. **候補の生成根拠・採否が台帳にない。** 16 PNGは `rebuild/` にあるだけで、対象MAP行には prompt、使用Ref、出力パス、adoption state、今回レビューへのリンクがない。各MAPの候補台帳（または既存の個別行）にこれらを記録し、`legacy` をこの候補の採用済み表現に流用しないこと。
3. **全画像が未解消TBDを持つ非`ready` MAPである。** `content-registry.md` の規約どおり、画像候補を作ったこと自体は採用条件を満たさない。TBD解消、mask、相互接続、再レビューまで `blocked`/`needs-review` を維持すること。
4. **屋内外遷移を画像だけで確定できない。** E01/E11/E12/F01/F02 の扉IDは画面内の扉であり、写真上の見た目だけでは同じ扉・同じ向き・回転余地を証明できない。`map-topology.md` の4つの不変条件を `links` と三値traversalで往復照合すること。

## 画像単位の検査

「画像固有」は共通 blocker を除いた判定であり、`pass` でも採用可を意味しない。`required / forbidden` は MAP相互接続台帳v2に照合した。

| ID | raw | required / forbidden の目視 | 車椅子・内外整合・画風／景色 | 画像固有 | 最終 disposition と修正先 |
|---|---|---|---|---|---|
| E01 | `sample/field/rebuild/E01-teramachi-kindergarten-rebuild-candidate.png` | 右側の生活路と北東の通用門候補は見える。ただし右端へ到達する連続路が塀・雪で不明瞭で、E02.left のリンク幅を読めない。余計な外周路は目視上なし。 | 雪遊びの園庭と本堂裏の主役は明確。土台は見えるが、遊具周囲の主路・E11通用門の回転域は未証明。 | major | 共通 blocker により採用不可。右edgeと`door-north`をmask/linksで明記し、E11側と往復照合する。 |
| E02 | `sample/field/rebuild/E02-teramachi-connector-rebuild-candidate.png` | 左右の横道とtopへ向かう用水脇の道が見え、E01/E03/N2の三接続に整合する。bottomは屋根・土台で閉じている。 | 用水・寺門が一言特徴として明瞭、手作り土台も明瞭。濡れた生活路はあるがmaskなしでは幅・通行性を保証できない。 | pass | 共通 blocker により採用不可。3 edgeをlinks化し、用水・橋・石段を黒にしたmaskで再確認する。 |
| E03 | `sample/field/rebuild/E03-teramachi-hinomi-bend-rebuild-candidate.png` | 左右主路とbottom中央の細道が見え、E02/E04/E10の辺配置に概ね合う。topは壁・雪で閉じている。 | 火の見櫓が固有の主役。bottom枝がE10へ行く必須接続で、宝箱枝として画面内終端にしてはならない点をmaskで確認する必要がある。 | pass | 共通 blocker により採用不可。left/right/bottomをlinks化し、櫓台・石垣をblackにする。 |
| E04 | `sample/field/rebuild/E04-teramachi-wide-road-rebuild-candidate.png` | 左右の広い道は明瞭だが、topの山門へ至る石畳は**上画像端に到達せず**、E11.bottom へのedgeとして未成立に見える。 | 消雪パイプと長塀は明確で、冬の融雪水も表現される。 | blocker | 再構図または採用前の画像編集で、top edgeまで連続する幅ある通路を作る。`E04.top ↔ E11.bottom` をmask/linksで示してから再レビュー。 |
| E05 | `sample/field/rebuild/E05-teramachi-well-merge-rebuild-candidate.png` | 左右に続くS字の主路を確認し、top/bottomに外周道路はない。 | 井戸・用水が固有の主役。井戸縁・水路は転落域なのでblack mask必須。 | pass | 共通 blocker により採用不可。水際のblackと左右linksを作成する。 |
| E06 | `sample/field/rebuild/E06-teramachi-sento-rebuild-candidate.png` | 左から入る主路はあるが、E07.topへ出るべき**bottom edgeまで連続する通路が見えない**。画面下方は建物・塀で閉じる。 | 銭湯と煙突は明瞭、文字・人物なし。 | blocker | `E06.left ↔ E07.top` を保つようbottom edgeへ幅ある主路を再構図する。主路上の縁石・雪・水溜りをmaskで通行判定する。 |
| E07 | `sample/field/rebuild/E07-teramachi-barrier-free-ramp-rebuild-candidate.png` | top/bottomの出入口候補と蛇行は見えるが、画像は実景写真風で、土台・材料・室内机が見えない。 | 車椅子主路としては蛇行・手すりがある一方、融雪・凍結面と曲線部の有効幅・回転域は未証明。手作りジオラマ規約に不適合。 | blocker | 写真風でなく、綿雪・紙粘土石垣・段ボール土台の見える真上寄り模型として作り直す。全蛇行をwhite/assistで連続させ、急段差をblackにする。 |
| E08 | `sample/field/rebuild/E08-teramachi-danchi-court-rebuild-candidate.png` | topから中庭へ入る経路とrightへの石段側候補は見えるが、端到達区間は無記録。 | 県営住宅中庭・F03入口候補はある。しかし実景写真風で、手作り模型の材料・土台が見えない。E09は立位期のみ、F03の扉は車椅子でも回転可能である必要がある。 | blocker | ジオラマ規約を満たす候補に作り直し、E07/E09/F03の各linksを分けて記録する。石段はwhite/assist主路に混ぜない。 |
| E09 | `sample/field/rebuild/E09-teramachi-old-slope-foot-rebuild-candidate.png` | 必須は `E08.left → E13.top` だが、実画像は**bottom → top の石段**でありleft edgeの入路がない。黒い背景も地図端として扱えない。 | 石段・古い坂という主役は明瞭で、車椅子不可の条件自体は合う。 | blocker | E08から入るleft edgeとE13へ抜けるtop edgeを明示した石段に再構図する。事故後閉鎖用のorange/blackをmaskで表現し、white主路にしない。 |
| E10 | `sample/field/rebuild/E10-teramachi-narrow-lane-rebuild-candidate.png` | top中央から土塀路地へ入り、画面内の門で終わる。required `E03.bottom` の一方向枝と、他辺禁止に合う。 | 勝手口・土塀の主役は明瞭。宝箱枝なら門の先を通行可能にしない必要がある。 | pass | 共通 blocker により採用不可。top linkだけを記録し、門・井戸・塀はblack、終端は画面内で閉じるmaskにする。 |
| E11 | `sample/field/rebuild/E11-teramachi-temple-grounds-rebuild-candidate.png` | bottom山門、中央本堂、右の庫裏側通路、左の幼稚園側通路は候補として見える。ただし4扉のID・進行方向は画像から確定できない。 | 浄土真宗の「親鸞像」が必要だが、庭の像は宗派固有の親鸞像と識別できず、確認不能。雪の境内は明瞭だが実景写真寄り。 | major | 共通 blocker により採用不可。`E04.bottom`、`door-kindergarten`、`door-main`、`door-residence` を個別linksにし、E01/F01/E12と往復照合する。親鸞像の意匠根拠も候補台帳に記す。 |
| E12 | `sample/field/rebuild/E12-teramachi-residence-rebuild-candidate.png` | E11への外門らしい上側入口は見えるが、F01渡り廊下とF02職員廊下をどの室内扉に割り当てるか読めない。 | 台所・幼馴染の部屋は明瞭。火事イベントの台所が主役として読める一方、畳・通路の幅と車椅子回転域が未検証。 | blocker | `door-temple`、`door-hall`、`door-playroom` を一意な扉IDにしてlinks化する。F01東廊下/F02西扉と同じ方位・幅で往復させる。 |
| E13 | `sample/field/rebuild/E13-teramachi-slope-top-rebuild-candidate.png` | bottomの石段口とrightの緩い道候補が見え、E09/N10の二接続に概ね合う。 | 石段と車椅子主路を視覚的に分離し、階段の鎖もある。右側主路の連続幅・雪上の通行区分はmaskなしでは未証明。看板は文字が読めない。 | major | 共通 blocker により採用不可。bottomを立位期のみ、rightを車椅子主路として別links/traversalにし、N10.leftと照合する。 |
| F01 | `sample/field/rebuild/F01-temple-main-hall-rebuild-candidate.png` | southの大扉とeastの渡り廊下候補は見える。ただしE11/F01/E12それぞれの扉ID・向き・通行幅は画像単体では検証不能。 | 本堂の主役・冬の外景は明瞭。畳の中央・椅子列・柱により車椅子が回転・通過できる経路は不明。 | blocker | `door-south` と `door-east` のlinks、white/assist通路、回転域をmaskで示す。E11.main/E12.hallとの往復テスト後に再レビュー。 |
| F02 | `sample/field/rebuild/F02-kindergarten-playroom-rebuild-candidate.png` | westの開口は見えるが、`E12.door-playroom ↔ F02.door-west` の同一扉・進行方向を確定する記録がない。舞台袖は画面内で終わる。 | 遊戯室・舞台という主役は明瞭、文字・人物なし。床上の机・棚・舞台段差の通行区分が未記録。 | blocker | west扉をlinks化し、E12職員廊下と往復照合する。舞台段差と袖はblack、歩行床・回転域はwhite/assistで分離する。 |
| F03 | `sample/field/rebuild/F03-danchi-apartment-rebuild-candidate.png` | E08からの住戸扉候補はbottomにあるが、door ID・開口幅・往復位置が未記録。外周に不要なedge接続はない。 | 県営住宅室内・結露窓・冬の生活感は明瞭。入口、廊下、トイレ・浴室周りの車椅子通行/回転を画像だけで保証できない。 | blocker | `E08.door ↔ F03.door` をlinksで特定し、玄関・廊下・居室のwhite/assist/blackを編集PNGに記録する。 |

## 横断結論と再レビューの入口

画像としての冬・現代K県・雪国の融雪水／汚れ・固有ランドマークは、E04/E05/E06/E10/E13/F01/F02/F03で概ね直接確認できる。E07/E08は写真風という重大な画風逸脱があり、E04/E06/E09は画像端接続が正本と合わない。したがって、まずこれら5件を作者側で修正する。

その後、全16件について次を満たしたものだけを新規red-teamへ渡す。

1. candidateごとの prompt・Ref・出力・adoption state を台帳化する。
2. traversal edit/runtime、foreground edit/runtime、edge/door `links` を出す。
3. E01↔E11、E11↔F01、F01↔E12、E12↔F02を往復テストする。
4. E06/E07/E08/E09/E13の車椅子/石段の時代差を三値maskで証明する。

本レビューは候補を変更しておらず、修正後の画像・maskに対しては別の独立レビューが必要である。
