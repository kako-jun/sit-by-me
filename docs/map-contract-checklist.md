# MAP生成契約チェックリスト

`map-asset-registry.md` の104行を、生成可能にするまで追跡する行単位チェックリスト。接続の正本は `map-topology.md` の「MAP相互接続台帳 v2」、画面主役と主路は `map-specifications.md`、マスク形式は `sit-field-mask` である。全行は `blocked` または `legacy-needs-review` で始める。`TBD` が空でない限り `ready` にしない。台帳整合の独立再監査は [第3周レビュー](reviews/artifact-redteam/20261016-map-ledger-round3.md) を参照。

| ID | 状態 | Ref | mask / 出力 | 具体的TBD |
|---|---|---|---|---|
| E01 | legacy-needs-review | R006,R011 | `diorama-trial/teramachi-kindergarten-diorama.png`; mask未記録 | 園庭の既存画像におけるE02/E11の実端、幼稚園期のtraversalを採寸する |
| E02 | legacy-needs-review | R006,R011 | `diorama-trial/teramachi-connector-shinshu-diorama.png`; mask未記録 | E01/E03/N2の三端と用水のblocked域を実画像から記録する |
| E03 | legacy-needs-review | R006,R011 | `diorama-trial/teramachi-hinomi-bend-shinshu-diorama.png`; mask未記録 | E02/E04/E10端、火の見櫓周囲のblocked域を記録する |
| E04 | legacy-needs-review | R006,R011 | `diorama-trial/teramachi-wide-road-diorama.png`; mask未記録 | E03/E05/E11端と山門のforeground域を記録する |
| E05 | legacy-needs-review | R006,R011 | `diorama-trial/teramachi-well-merge-diorama.png`; mask未記録 | 用水・井戸のblocked域とE04/E06端を記録する |
| E06 | legacy-needs-review | R006,R011 | `diorama-trial/teramachi-sento-diorama.png`; mask未記録 | E05/E07端、銭湯煙突・雪山のforeground/blockedを記録する |
| E07 | legacy-needs-review | R006,R011 | `diorama-trial/teramachi-barrier-free-ramp-diorama.png`; mask未記録 | E06/E08を結ぶuniversalスロープの幅・折返しを記録する |
| E08 | legacy-needs-review | R006,R011 | `diorama-trial/teramachi-danchi-court-diorama.png`; mask未記録 | E07/E09端、F03ドア、団地棟のforegroundを記録する |
| E09 | legacy-needs-review | R006,R011 | `diorama-trial/teramachi-old-slope-foot-diorama.png`; mask未記録 | 立位期onlyのassist石段とE08/E13端を記録する |
| E10 | legacy-needs-review | R006,R011 | `diorama-trial/teramachi-narrow-lane-diorama.png`; mask未記録 | E03からの入口以外を禁止辺とし、画面内終端を記録する |
| E11 | legacy-needs-review | R006,R011 | `diorama-trial/temple-grounds-shinshu-diorama.png`; mask未記録 | E04端、E01/F01/E12ドア、池・墓地のblocked域を記録する |
| E12 | legacy-needs-review | R006,R011 | `diorama-trial/temple-residence-interior-diorama.png`; mask未記録 | E11/F01/F02の各doorと火事時の遮断範囲を記録する |
| E13 | legacy-needs-review | R006,R011 | `diorama-trial/teramachi-slope-top-diorama.png`; mask未記録 | E09石段とN10車椅子坂の端・通行クラスを記録する |
| E14 | legacy-needs-review | R005,R011 | `diorama-trial/korinbo-crossroads-diorama.png`; mask未記録 | N1/N11/N9端、百貨店door、封鎖期のN9遷移を記録する |
| E15 | legacy-needs-review | R005 | `diorama-trial/korinbo-daiwa-toy-floor-diorama.png`; mask未記録 | E14/E16door、売場通路のuniversal幅を記録する |
| E16 | legacy-needs-review | R005 | `diorama-trial/korinbo-department-restaurant-diorama-v2.png`; mask未記録 | E15door、再訪時の同一導線を記録する |
| E17 | legacy-needs-review | R013,R011 | `diorama-trial/chaya-lane-diorama.png`; mask未記録 | E19/N1端、E18door、格子・側溝のblocked域を記録する |
| E18 | legacy-needs-review | R013 | `diorama-trial/chaya-tearoom-diorama.png`; mask未記録 | E17door、座敷の段差・車椅子可否を決める |
| E19 | legacy-needs-review | R011,R013 | `diorama-trial/convenience-store-diorama.png`; mask未記録 | N2/E17端、駐車場枝の画面内終端を記録する |
| E20 | legacy-needs-review | R011 | `diorama-trial/hospital-exterior-diorama.png`; mask未記録 | N9端、車寄せのuniversal幅と入口foregroundを記録する |
| E21 | legacy-needs-review | R011 | `diorama-trial/korimon-station-plaza-v3-diorama.png`; mask未記録 | N11端、能登／内灘乗車door、広場の禁止辺を記録する |
| E22 | legacy-needs-review | R007,R008 | `diorama-trial/utatsuyama-sunnyland-diorama.png`; mask未記録 | N8/F04端、折返し主路と廃遊具のblocked域を記録する |
| E23 | legacy-needs-review | R007 | `diorama-trial/utatsuyama-sunnyland-indoor-diorama.png`; mask未記録 | F10/E25door、噴水外周のuniversal環状路を記録する |
| E24 | legacy-needs-review | R007 | `diorama-trial/utatsuyama-sunnyland-aquarium-indoor-diorama.png`; mask未記録 | F08/F09door、水槽と破片のblocked域を記録する |
| E25 | legacy-needs-review | R007 | `diorama-trial/utatsuyama-sunnyland-arcade-indoor-diorama.png`; mask未記録 | F09/F10door、筐体間のuniversal幅を記録する |
| E26 | legacy-needs-review | R014,R015 | `diorama-trial/uchinada-station-diorama.png`; mask未記録 | N3端、駅出口と線路端のblocked域を記録する |
| E27 | legacy-needs-review | R015 | `diorama-trial/uchinada-beach-diorama.png`; mask未記録 | F11端、海側blocked帯と締まった砂のuniversal帯を記録する |
| E28 | legacy-needs-review | R004 | `diorama-trial/noto-railway-interior-v2-diorama.png`; mask未記録 | E21/E29door、車内通路とドア回転域を記録する |
| E29 | legacy-needs-review | R004 | `diorama-trial/noto-takojima-station-diorama.png`; mask未記録 | N5端、終端線路のblocked域を記録する |
| E30 | legacy-needs-review | R004 | `diorama-trial/noto-peko-house-seaside-v2-diorama.png`; mask未記録 | N7/E31端、家door、海側blocked域を記録する |
| E31 | legacy-needs-review | R004 | `diorama-trial/noto-tetrapod-fishing-spot-diorama.png`; mask未記録・採用禁止 | 既存画像は海が上側で、既定の「能登の海は下側」に違反する。回転での救済はしない。E30端・桟橋終端・海/テトラblocked域を満たす再構図版が必要 |
| E32 | legacy-needs-review | R016 | `diorama-trial/abandoned-school-diorama.png`; mask未記録 | F18door、崩落棟blocked域と避難導線を記録する |
| E33 | legacy-needs-review | R006,R011 | `diorama-trial/schoolyard-diorama.png`; mask未記録 | N10端、校門と校庭外周柵のblocked域を記録する |
| N1 | blocked | R001,R002,R011 | 未生成・mask未作成 | E17/E14端、南北橋の型・欄干外blocked域をR001/R002と照合する |
| N2 | blocked | R006,R011,R021,R024,R025 | 未生成・mask未作成 | E02/E19端、蛇行するuniversal坂と用水のblocked域を実景参照で確定する |
| N3 | blocked | R003,R014,R015 | 未生成・mask未作成 | E26/F11端、砂丘木道の幅・防砂柵・深砂blocked域を確定する |
| N5 | blocked | R004,R028 | 未生成・mask未作成 | E29/N6端、海を下に置く蛇行坂の集落尺度を能登沿岸資料で補う |
| N6 | blocked | R004,R028 | 未生成・mask未作成 | N5/N7端、尾根・小祠・畑の資料と神社枝の終端を確定する |
| N7 | blocked | R004,R028 | 未生成・mask未作成 | N6/E30端、下り坂の勾配と海側blocked域を沿岸資料で補う |
| N8 | blocked | R007,R008,R010,R021,R026,R027 | 未生成・mask未作成 | N11/E22端、橋を含む東岸坂・石段assist域を実景資料で確定する |
| N9 | blocked | R011,R023 | 未生成・mask未作成 | E14/F41/E20端、封鎖柵の開閉差分と松・石垣の資料を追加する |
| N10 | blocked | R006,R011,R021,R023,R024,R025 | 未生成・mask未作成 | E13/E33端、車椅子の連続坂・手すり・除雪帯の寸法根拠を追加する |
| N11 | blocked | R005,R010,R011,R023,R026 | 未生成・mask未作成 | E14/E21/N8端、交差点の3出口と横断部の段差なし範囲を確定する |
| N12 | blocked | R009,R021,R022 | 未生成・mask未作成 | E21/E26door、車椅子回転域と半自動扉のゲーム上寸法を確定する |
| F01 | blocked | R021,R024 | 未生成・mask未作成 | 本堂の畳・仏具・車椅子回転域を、特定寺院を模写しない創作寸法で決める |
| F02 | blocked | R021,R024 | 未生成・mask未作成 | 遊戯室の舞台袖・椅子・E12doorの安全な室内導線を決める |
| F03 | blocked | R021,R024 | 未生成・mask未作成 | 県営住宅室内の玄関段差・回転域・E08doorを創作寸法で決める |
| F04 | blocked | R007,R008,R021,R027 | 未生成・mask未作成 | E22/F05端、東屋周囲の迂回坂と展望枝の安全幅を決める |
| F05 | blocked | R007,R008,R021,R027 | 未生成・mask未作成 | F04/F06端、崩落石垣を避けるassist主路の幅を決める |
| F06 | blocked | R007,R008,R021,R027 | 未生成・mask未作成 | F05/F07端、山頂戦闘域と展望柵のblocked域を決める |
| F07 | blocked | R007,R008,R021,R027 | 未生成・mask未作成 | F06/F08door、瓦礫のassist迂回路と崩落入口の資料を追加する |
| F08 | blocked | R021,R027 | 未生成・mask未作成 | F07/E24door、割れ物を避ける館内universal通路を創作寸法で決める |
| F09 | blocked | R021,R027 | 未生成・mask未作成 | E24/E25door、階段でなく折返しスロープを使う根拠を創作寸法で決める |
| F10 | blocked | R021,R027 | 未生成・mask未作成 | E25/E23door、整備棚の行き止まりと主路の分離を決める |
| F11 | blocked | R014,R015,R021 | 未生成・mask未作成 | N3/E27端、砂丘頂の柵・深砂・海側のblocked域を決める |
| F12 | blocked | R016,R028,R029 | 未生成・mask未作成 | F13/F18端、E29と同一地形の被災後差分を決める |
| F13 | blocked | R016,R028,R029 | 未生成・mask未作成 | F12/F14端、仮設板路のassist可否と地割れblocked域を決める |
| F14 | blocked | R016,R028,R029 | 未生成・mask未作成 | F13/F15端、倒木・神社枝封鎖の範囲を決める |
| F15 | blocked | R016,R028,R029 | 未生成・mask未作成 | F14/F16端、地割れをまたぐ主路の安全表現を決める |
| F16 | blocked | R016,R028,R029 | 未生成・mask未作成 | F15/F17端、実家door封鎖と生活路の範囲を決める |
| F17 | blocked | R016,R028,R029 | 未生成・mask未作成 | F16端、釣り場先端を終端にする柵と海のblocked域を決める |
| F18 | blocked | R016,R028,R029 | 未生成・mask未作成 | F12/E32door、仮設住宅の生活路・集会所doorを決める |
| F19 | blocked | R018 | 未生成・mask未作成 | 抽象素材の口入口、F20/F21/F24の3枝、非写実安全表現を確定する |
| F20 | blocked | R018 | 未生成・mask未作成 | F19/F22端、左手枝を任意終端へする抽象地形を確定する |
| F21 | blocked | R018 | 未生成・mask未作成 | F19/F23端、右手枝を任意終端へする抽象地形を確定する |
| F22 | blocked | R018 | 未生成・mask未作成 | F20端、左脚枝の終端・戦闘域を確定する |
| F23 | blocked | R018 | 未生成・mask未作成 | F21端、右脚枝の終端・戦闘域を確定する |
| F24 | blocked | R018 | 未生成・mask未作成 | F19/F25/F26端、頭部室の外周主路・中ボス域を確定する |
| F25 | blocked | R018 | 未生成・mask未作成 | F24/F26端、胃への遠回り主路と安全な抽象素材を確定する |
| F26 | blocked | R018 | 未生成・mask未作成 | F24/F25端、心臓戦闘域・外周通路・終端を確定する |
| F27 | blocked | R019,R033 | 未生成・mask未作成 | 到着口/F28端、凍結滑走路を通行不能にする空港導線を確定する |
| F28 | blocked | R019,R033 | 未生成・mask未作成 | F27/F29端、凍った泉の画面内終端と乾燥寒冷地資料を確定する |
| F29 | blocked | R019,R033 | 未生成・mask未作成 | F28/F30端、凍結穴・風食岩のblocked域を確定する |
| F30 | blocked | R019 | 未生成・mask未作成 | F29/F31端、外門以外を壁で閉じる縦都市構造を確定する |
| F31 | blocked | R019 | 未生成・mask未作成 | F30/F32端、市場袋小路と主回廊を分離する構造を確定する |
| F32 | blocked | R019 | 未生成・mask未作成 | F31/F33端、排水路・渡り廊下の安全な幅を確定する |
| F33 | blocked | R019 | 未生成・mask未作成 | F32/F34端、補給枝の画面内終端を確定する |
| F34 | blocked | R019 | 未生成・mask未作成 | F33/F35端、エレベーター坑を避ける螺旋主路を確定する |
| F35 | blocked | R019 | 未生成・mask未作成 | F34/F36端、給水塔広場の宝箱枝を主路から分離する |
| F36 | blocked | R019 | 未生成・mask未作成 | F35/F37端、空中街路の落下辺・柵・foregroundを確定する |
| F37 | blocked | R019 | 未生成・mask未作成 | F36/F38端、発電機周囲のblocked域を確定する |
| F38 | blocked | R019 | 未生成・mask未作成 | F37端、時間制限脱出口・戦闘域・終端を確定する |
| F39 | blocked | R020,R021,R022,R032 | 未生成・mask未作成 | ワープ広場/F40door、駐機場blocked域を確定する |
| F40 | blocked | R020,R021,R022,R032 | 未生成・mask未作成 | F39/F27door、一方通行の保安・搭乗導線を確定する |
| F41 | blocked | R012,R030 | 未生成・mask未作成 | N9/F42端、雪吊り松・南口・外周閉鎖を確定する |
| F42 | blocked | R012,R030 | 未生成・mask未作成 | F41/F43端、細流と石橋のblocked域を確定する |
| F43 | blocked | R012,R014,R030 | 未生成・mask未作成 | F42/F44端、築山の主路・頂上枝・風紋の扱いを確定する |
| F44 | blocked | R012,R013,R030 | 未生成・mask未作成 | F43/F45端、曲水・茶屋景観を主路と分離する |
| F45 | blocked | R012,R004,R030 | 未生成・mask未作成 | F44/F46端、池・石組みのblocked域を確定する |
| F46 | blocked | R012,R007,R030 | 未生成・mask未作成 | F45/F47端、石段を脇にしたヘアピン主路を確定する |
| F47 | blocked | R012,R030 | 未生成・mask未作成 | F46/F48端、宝箱枝・風穴・雪柱のblocked域を確定する |
| F48 | blocked | R012,R030 | 未生成・mask未作成 | F47/F49端、曲水・石灯籠・foregroundを確定する |
| F49 | blocked | R012,R030 | 未生成・mask未作成 | F48/F50端、大池沿いの行き止まりと主路を確定する |
| F50 | blocked | R012,R017,R030,R031 | 未生成・mask未作成 | F49/F51端、石川橋をF50東端に含める構図を確定する |
| F51 | blocked | R017,R031 | 未生成・mask未作成 | F50/F52端、石川門・M013戦闘域・橋外blocked域を確定する |
| F52 | blocked | R017,R031 | 未生成・mask未作成 | F51/F53端、枡形の二度折れ主路を確定する |
| F53 | blocked | R017,R031 | 未生成・mask未作成 | F52/F54端、長屋と石垣の通行不能域を確定する |
| F54 | blocked | R017,R031 | 未生成・mask未作成 | F53/F55端、石段を脇に置くヘアピン坂を確定する |
| F55 | blocked | R017,R031 | 未生成・mask未作成 | F54/F56端、兵站蔵と宝箱枝を分離する |
| F56 | blocked | R017,R031 | 未生成・mask未作成 | F55/F57端、井戸周囲のblocked域を確定する |
| F57 | blocked | R017,R031 | 未生成・mask未作成 | F56/F58端、櫓回廊の外縁柵・foregroundを確定する |
| F58 | blocked | R017,R031 | 未生成・mask未作成 | F57/F59端、瓦礫を避ける折返し坂を確定する |
| F59 | blocked | R017,R031 | 未生成・mask未作成 | F58/F60端、ボスラッシュ戦闘域と中央空地を確定する |
| F60 | blocked | R017,R031 | 未生成・mask未作成 | F59端、最終戦の外周通路・北終端を確定する |
