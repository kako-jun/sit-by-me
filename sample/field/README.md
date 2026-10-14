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
| `uchinada-dune-station-diorama.png` | 内灘。砂丘と海、浅野川鉄道の小駅と朽ちた車両、横の道と踏切 |
| `korimon-station-plaza-diorama.png` | 金沢駅の鼓門前。左右対称の広い広場 |
| `utatsuyama-sunnyland-diorama.png` | 卯辰山のサニーランド跡。斜めのうねる山道と廃遊具（うねる山道は正解。kako-jun 2026-10-14） |
| `chaya-lane-diorama.png` | 茶屋街。用水沿いのL字の石畳 |

### -v2（採否待ち。再生成は kako-jun の指示があった場合だけ）

`utatsuyama-sunnyland-v2.png` は、卯辰山の道を広い帯にした別案だが、うねる道が正解のため参考扱い。`chaya-lane-v2.png`（桜らしい木を除いた版）と `korimon-station-plaza-v2.png`（鼓門を実物から離した版）は、元の版と並べて kako-jun が選ぶ。元の版（`-diorama.png`）はそのまま残している。
