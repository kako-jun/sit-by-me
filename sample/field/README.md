# フィールド背景の試作

> 2026-10-14: 寺町の4枚は試作用のサンプル（実写寄りの見た目）。本番の背景は、デフォルメされたジオラマ風で作る（docs/art-direction.md）。ジオラマ風の見た目の確認用の試作は `diorama-trial/`。

寺町の背景パック（Issue #11）。全景・広い道路・狭い道・接続画を、同じ光（冬の曇天の午後）・同じカメラ（約45°の高めの斜め見下ろし）・同じ反復物（寺の土塀と石垣、門、雪囲い、赤白スノーポール、消雪パイプと錆、除雪の雪山、用水、電柱）でそろえた。共通の説明文を1つにまとめ、カットの説明だけを変えて並列生成している（手順は `sit-world` スキル（背景パック））。人物・文字なし。

| ファイル | カット |
|---|---|
| `teramachi-overview.png` | 全景（広い道路から狭い道が分かれる） |
| `teramachi-wide-road.png` | 広い道路 |
| `teramachi-narrow-lane.png` | 寺の土塀にはさまれた狭い道と用水 |
| `teramachi-connector.png` | 狭い道と広い道路の角、用水の石橋 |

## 寺町の歩行サンプルに全ての敵を出す実験（Issue #31）

`teramachi-diorama-standing.field.json` / `teramachi-diorama-wheelchair.field.json` は、エンカウントのあるシーン（連絡路・日の見の曲がり・狭い道・広い道・井戸の合流・銭湯）で、生成済みの敵8体（スズメバチ・ロードローラー・釘・割れたガラス・ウニ・氷柱・割れたビール瓶・段ボールのドラゴン）を共通の16群から均等抽選で出す。

- **実験用であり正本ではない。** 能力値・出現率（1/8）・群の構成はすべて仮。台帳 `docs/monsters.md` の「出る場所」は変えていない。
- 戦闘は `side` ＋ `acrylic`。敵の絵は `assets/enemies/` と `sample/battle/enemy-dragon.png`。
- 群は単独・同種2〜4体・異種の混成（最大5体）を混ぜた16通り。

## ジオラマ風の試作（寺町以外・2026-10-14〜15）

`diorama-trial/` に、docs に仕様がある場所の背景を未採否で置いている（歩行マスクは未作成）。

| ファイル | 場所・個性 |
|---|---|
| `korinbo-crossroads-diorama.png` | 香林坊。店が連なる十字路と、地下へ下りる入口 |
| `korimon-station-plaza-diorama.png` | 金沢駅の鼓門前。左右対称の広い広場 |
| `utatsuyama-sunnyland-diorama.png` | 卯辰山のサニーランド跡。斜めのうねる山道と廃遊具（うねる山道は正解。kako-jun 2026-10-14） |
| `chaya-lane-diorama.png` | 茶屋街。用水沿いのL字の石畳 |

### -v2（採否待ち。再生成は kako-jun の指示があった場合だけ）

`utatsuyama-sunnyland-v2.png` は、卯辰山の道を広い帯にした別案だが、うねる道が正解のため参考扱い。`chaya-lane-v2.png`（桜らしい木を除いた版）と `korimon-station-plaza-v2.png`（鼓門を実物から離した版）は、元の版と並べて kako-jun が選ぶ。元の版（`-diorama.png`）はそのまま残している。

### 事実に沿った追加（2026-10-15）

- 卯辰山のサニーランドは屋内施設で観覧車はない（docs/art-direction.md）。既存の `utatsuyama-sunnyland-diorama.png`（屋外の山道と廃遊具）は事実と違うが、うねる山道の屋外シーンとして残す。事実に沿った屋内の廃墟は `utatsuyama-sunnyland-*-indoor-diorama.png` として追加する。
- 鼓門前は、現地調査の要点に沿った `korimon-station-plaza-v3-diorama.png` を追加（v1・v2 は採否待ちで残す）。
- 背景は「場所のイメージ」で、地理・街並みの再現ではない。

### 追加分の一覧（2026-10-15、すべて採否待ち）

| ファイル | 内容 |
|---|---|
| `convenience-store-diorama.png` | コンビニ前（実在チェーンに似ない黄土色。横の道路） |
| `temple-grounds-diorama.png` | 寺の境内（縦の参道、山門、本堂、鐘楼、地蔵） |
| `schoolyard-diorama.png` | 小学校の校庭（L字の校舎） |
| `hospital-exterior-diorama.png` | 私立病院の外観と駐車場（斜めの道） |
| `abandoned-school-diorama.png` | 廃校（T字の道、廃墟探検） |
| `uchinada-station-diorama.png` | 内灘駅（作り直し。kako-jun 指示で旧版 uchinada-dune-station・uchinada-station-v2 は破棄）。住宅地の端の終着駅、実物に寄せた小さな白い駅舎、直線と緩い曲線の線路、銀とオレンジ帯の電車、検車区、バス乗り場 |
| `korimon-station-plaza-v3-diorama.png` | 鼓門前。現地調査に沿った版（ガラスのドーム、緑青の屋根、雪吊り） |
| `utatsuyama-sunnyland-indoor-diorama.png` | サニーランド跡の屋内。円形のエントランスと白いシャチホコ |
| `utatsuyama-sunnyland-aquarium-indoor-diorama.png` | サニーランド跡の屋内。水族館の水槽跡と動物園の檻 |
| `utatsuyama-sunnyland-arcade-indoor-diorama.png` | サニーランド跡の屋内。ゲームセンターとござの和室 |
| `chaya-tearoom-diorama.png` | 茶屋街の茶室の座敷（八畳、床の間、炉、障子、縁側、雪の坪庭、水屋）。docs/art-direction.md の茶屋街の調査に沿う |
