# MAP生成契約チェックリスト

2026-10-18: サニーランドF07–F10/E23–E25の旧平面接続は失効。2階建てエントランス（入場階未確定）／地下水族館／屋外動物園の詳細接続を口述待ち。以下の旧TBDは再設計対象で、生成根拠にしない。

`map-asset-registry.md` の104行を、生成可能にするまで追跡する行単位チェックリスト。接続の正本は `map-topology.md` の「MAP相互接続台帳 v2」、画面主役と主路は `map-specifications.md`、マスク形式は `sit-field-mask` である。全行は `blocked` または `legacy-needs-review` で始める。`TBD` が空でない限り `ready` にしない。台帳整合の独立再監査は [第3周レビュー](reviews/artifact-redteam/20261016-map-ledger-round3.md) を参照。

**2026-10-18 / #51**: E01–E13/F01–F03は全て `recreate-required-1920x1080`、生成契約は `blocked`。以下の旧画像パスは参照専用で、旧mask・旧passは新候補の採用根拠にならない。現行再作成状態は [候補台帳](teramachi-rebuild-candidates.md)、建物群の生成前入力は [制作前確認](production/20261018-teramachi-preflight.md) を参照する。

| ID | 状態 | Ref | mask / 出力 | 具体的TBD |
|---|---|---|---|---|
| E01 | recreate-required-1920x1080 | R006,R011 | `assets/images/fields/legacy/E01.png`; mask未記録 | 園庭の既存画像におけるE02/E11の実端、幼稚園期のtraversalを採寸する |
| E02 | recreate-required-1920x1080 | R006,R011 | `assets/images/fields/legacy/E02.png`; mask未記録 | E01/E03/N2の三端と用水のblocked域を実画像から記録する |
| E03 | recreate-required-1920x1080 | R006,R011 | `assets/images/fields/legacy/E03.png`; mask未記録 | E02/E04/E10端、火の見櫓周囲のblocked域を記録する |
| E04 | recreate-required-1920x1080 | R006,R011 | `assets/images/fields/legacy/E04.png`; mask未記録 | E03/E05/E11端と山門のforeground域を記録する |
| E05 | recreate-required-1920x1080 | R006,R011 | `assets/images/fields/legacy/E05.png`; mask未記録 | 用水・井戸のblocked域とE04/E06端を記録する |
| E06 | recreate-required-1920x1080 | R006,R011 | `assets/images/fields/legacy/E06.png`; mask未記録 | E05/E07端、銭湯煙突・雪山のforeground/blockedを記録する |
| E07 | recreate-required-1920x1080 | R006,R011 | `assets/images/fields/legacy/E07.png`; mask未記録 | E06/E08を結ぶuniversalスロープの幅・折返しを記録する |
| E08 | recreate-required-1920x1080 | R006,R011 | `assets/images/fields/legacy/E08.png`; mask未記録 | E07/E09端、F03ドア、団地棟のforegroundを記録する |
| E09 | recreate-required-1920x1080 | R006,R011,R025 | 1254×1254のv6候補・maskは参照専用。新規出力は1920×1080、prompt・参照画像・mask・red-teamを新たに記録する | v6のleft→top石段・assist-only設計を参照し、16:9版を再生成する |
| E10 | recreate-required-1920x1080 | R006,R011 | `assets/images/fields/legacy/E10.png`; mask未記録 | E03からの入口以外を禁止辺とし、画面内終端を記録する |
| E11 | recreate-required-1920x1080 | R006,R011,R024 | 旧境内画像は参照専用。新背景・mask未作成 | #60の屋外境内。E04端、E01通用門、F01正面扉、池・墓地のblocked域を記録。E12/F02屋外doorなし。共通外観参照未通過 |
| E12 | recreate-required-1920x1080 | R006,R011,R021,R024 | 旧庫裏画像は参照専用。新背景・mask未作成 | #60の東の屋内住居。F01.door-east↔door-hallのみ。内部廊下の扉位置、幅・段差・回転域、火事時遮断範囲がTBD。F02直結なし |
| E13 | recreate-required-1920x1080 | R006,R011 | `assets/images/fields/legacy/E13.png`; mask未記録 | E09石段とN10車椅子坂の端・通行クラスを記録する |
| E14 | legacy-needs-review | R005,R011 | `assets/images/fields/legacy/E14.png`; mask未記録 | N1/N11/N9端、百貨店door、封鎖期のN9遷移を記録する |
| E15 | legacy-needs-review | R005 | `assets/images/fields/legacy/E15.png`; mask未記録 | door-korinbo→E14.door、door-restaurant→E16.door、売場通路のuniversal幅を記録する |
| E16 | legacy-needs-review | R005 | `assets/images/fields/legacy/E16.png`; mask未記録 | E15door、再訪時の同一導線を記録する |
| E17 | legacy-needs-review | R013,R011 | `assets/images/fields/legacy/E17.png`; mask未記録 | E19/N1端、E18door、格子・側溝のblocked域を記録する |
| E18 | legacy-needs-review | R013 | `assets/images/fields/legacy/E18.png`; mask未記録 | E17door、座敷の段差・車椅子可否を決める |
| E19 | legacy-needs-review | R011,R013 | `assets/images/fields/legacy/E19.png`; mask未記録 | N2/E17端、駐車場枝の画面内終端を記録する |
| E20 | legacy-needs-review | R011 | `assets/images/fields/legacy/E20.png`; mask未記録 | N9端、車寄せのuniversal幅と入口foregroundを記録する |
| E21 | legacy-needs-review | R011 | `assets/images/fields/legacy/E21.png`; mask未記録 | N11端、能登／内灘乗車door、広場の禁止辺を記録する |
| E22 | legacy-needs-review | R007,R008 | `assets/images/fields/legacy/E22.png`; mask未記録 | N8/F04端、折返し主路と廃遊具のblocked域を記録する |
| E23 | legacy-needs-review | R007 | `assets/images/fields/legacy/E23.png`; mask未記録 | 2階建てエントランス（入場階未確定）／約2MAP長の下り渡り廊下（雪の森）／途中の進行方向右にゲームセンター／地下水族館／屋外動物園。階差・各接続・シャチホコ戦の位置は口述待ち。旧平面接続は失効、blocked（#14） |
| E24 | legacy-needs-review | R007 | `assets/images/fields/legacy/E24.png`; mask未記録 | 2階建てエントランス（入場階未確定）／約2MAP長の下り渡り廊下（雪の森）／途中の進行方向右にゲームセンター／地下水族館／屋外動物園。階差・各接続・シャチホコ戦の位置は口述待ち。旧平面接続は失効、blocked（#14） |
| E25 | legacy-needs-review | R007 | `assets/images/fields/legacy/E25.png`; mask未記録 | 2階建てエントランス（入場階未確定）／約2MAP長の下り渡り廊下（雪の森）／途中の進行方向右にゲームセンター／地下水族館／屋外動物園。階差・各接続・シャチホコ戦の位置は口述待ち。旧平面接続は失効、blocked（#14） |
| E26 | legacy-needs-review | R014,R015 | `assets/images/fields/legacy/E26.png`; mask未記録 | N3端、駅出口と線路端のblocked域を記録する |
| E27 | legacy-needs-review | R015 | `assets/images/fields/legacy/E27.png`; mask未記録 | F11端、海側blocked帯と締まった砂のuniversal帯を記録する |
| E28 | legacy-needs-review | R004 | `assets/images/fields/legacy/E28.png`; mask未記録 | E21/E29door、車内通路とドア回転域を記録する |
| E29 | legacy-needs-review | R004 | `assets/images/fields/legacy/E29.png`; mask未記録 | N5端、終端線路のblocked域を記録する |
| E30 | legacy-needs-review | R004 | `assets/images/fields/legacy/E30.png`; mask未記録 | N7/E31端、家door、海側blocked域を記録する |
| E31 | legacy-needs-review | R004 | `assets/images/fields/legacy/E31.png`; mask未記録・採用禁止 | 既存画像は海が上側で、既定の「能登の海は下側」に違反する。回転での救済はしない。E30端・桟橋終端・海/テトラblocked域を満たす再構図版が必要 |
| E32 | legacy-needs-review | R016 | `assets/images/fields/legacy/E32.png`; mask未記録 | F18door、崩落棟blocked域と避難導線を記録する |
| E33 | legacy-needs-review | R006,R011 | `assets/images/fields/legacy/E33.png`; mask未記録 | N10端、校門と校庭外周柵のblocked域を記録する |
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
| F01 | recreate-required-1920x1080 | R021,R024 | 旧本堂画像は参照専用。新背景・mask未作成 | #60の中央屋内本堂。E11南、E12東、F02西の扉位置、畳・仏具と主路、段差・幅・回転域を記録する |
| F02 | recreate-required-1920x1080 | R021,R024 | 旧遊戯室画像は参照専用。新背景・mask未作成 | #60の西の屋内幼稚園。F01↔F02.door-westの到着方位と扉位置、舞台袖・椅子・主路の分離、段差・幅・回転域を記録する。E12直結なし |
| F03 | recreate-required-1920x1080 | R021,R024 | 未生成・mask未作成 | 県営住宅室内の玄関段差・回転域・E08doorを創作寸法で決める |
| F04 | blocked | R007,R008,R021,R027 | 未生成・mask未作成 | E22/F05端、東屋脇の枝なし蛇行主路の安全幅を決める |
| F05 | blocked | R007,R008,R021,R027 | 未生成・mask未作成 | F04/F06端、崩落石垣を避けるassist主路の幅を決める |
| F06 | blocked | R007,R008,R021,R027 | 未生成・mask未作成 | F05/F07端、山頂戦闘域と展望柵のblocked域を決める |
| F07 | blocked | R007,R008,R021,R027 | 未生成・mask未作成 | 2階建てエントランス（入場階未確定）／約2MAP長の下り渡り廊下（雪の森）／途中の進行方向右にゲームセンター／地下水族館／屋外動物園。階差・各接続・シャチホコ戦の位置は口述待ち。旧平面接続は失効、blocked（#14） |
| F08 | blocked | R021,R027 | 未生成・mask未作成 | 2階建てエントランス（入場階未確定）／約2MAP長の下り渡り廊下（雪の森）／途中の進行方向右にゲームセンター／地下水族館／屋外動物園。階差・各接続・シャチホコ戦の位置は口述待ち。旧平面接続は失効、blocked（#14） |
| F09 | blocked | R021,R027 | 未生成・mask未作成 | 2階建てエントランス（入場階未確定）／約2MAP長の下り渡り廊下（雪の森）／途中の進行方向右にゲームセンター／地下水族館／屋外動物園。階差・各接続・シャチホコ戦の位置は口述待ち。旧平面接続は失効、blocked（#14） |
| F10 | blocked | R021,R027 | 未生成・mask未作成 | 2階建てエントランス（入場階未確定）／約2MAP長の下り渡り廊下（雪の森）／途中の進行方向右にゲームセンター／地下水族館／屋外動物園。階差・各接続・シャチホコ戦の位置は口述待ち。旧平面接続は失効、blocked（#14） |
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
| F30 | blocked | R019 | 未生成・mask未作成 | 双塔共通の基壇・左右入口。door-left→F31.door-base、door-right→F34.door-base、bottom→F29.top。階差・主路幅、左右ボスとM003救出／S005脱出／時間制限の関係を確定する（#71） |
| F31 | blocked | R019 | 未生成・mask未作成 | 左塔下層。door-base→F30.door-left、door-up→F32.door-down。階差・主路幅、左右ボスとM003救出／S005脱出／時間制限の関係を確定する（#71） |
| F32 | blocked | R019 | 未生成・mask未作成 | 左塔中層。door-down→F31.door-up、door-up→F33.door-down。階差・主路幅、左右ボスとM003救出／S005脱出／時間制限の関係を確定する（#71） |
| F33 | blocked | R019 | 未生成・mask未作成 | 左塔上層・左ボス枠。door-down→F32.door-up、door-landing→F37.door-left。階差・主路幅、左右ボスとM003救出／S005脱出／時間制限の関係を確定する（#71） |
| F34 | blocked | R019 | 未生成・mask未作成 | 右塔下層。door-base→F30.door-right、door-up→F35.door-down。階差・主路幅、左右ボスとM003救出／S005脱出／時間制限の関係を確定する（#71） |
| F35 | blocked | R019 | 未生成・mask未作成 | 右塔中層。door-down→F34.door-up、door-up→F36.door-down。階差・主路幅、左右ボスとM003救出／S005脱出／時間制限の関係を確定する（#71） |
| F36 | blocked | R019 | 未生成・mask未作成 | 右塔上層・右ボス枠。door-down→F35.door-up、door-landing→F37.door-right。階差・主路幅、左右ボスとM003救出／S005脱出／時間制限の関係を確定する（#71） |
| F37 | blocked | R019 | 未生成・mask未作成 | 双塔の共通上層・救出配置候補。door-left→F33.door-landing、door-right→F36.door-landing、door-escape→F38.door-landing。階差・主路幅、左右ボスとM003救出／S005脱出／時間制限の関係を確定する（#71） |
| F38 | blocked | R019 | 未生成・mask未作成 | 脱出終点・S005戦配置候補。door-landing→F37.door-escape。階差・主路幅、左右ボスとM003救出／S005脱出／時間制限の関係を確定する（#71） |
| F39 | blocked | R020,R021,R022,R032 | 未生成・mask未作成 | ワープ広場/F40door、駐機場blocked域を確定する |
| F40 | blocked | R020,R021,R022,R032 | 未生成・mask未作成 | F39/F27door、一方通行の保安・搭乗導線を確定する |
| F41 | blocked | R012,R030,R034,R035 | 未生成・mask未作成 | 真弓坂側の南西入口。top→F43.bottom、right→F42.left、bottom→N9.top。池／堀・高低差、各出口の位置・幅、assistと閉鎖域、城攻略目標と解錠条件を個別確定する（#45） |
| F42 | blocked | R012,R030,R034,R035 | 未生成・mask未作成 | 時雨亭・長谷池。left→F41.right、top→F44.bottom、right→F49.left。池／堀・高低差、各出口の位置・幅、assistと閉鎖域、城攻略目標と解錠条件を個別確定する（#45） |
| F43 | blocked | R012,R014,R030,R034,R035 | 未生成・mask未作成 | 瓢池・夕顔亭・翠滝下段。bottom→F41.top、right→F44.left、top→F50.bottom。池／堀・高低差、各出口の位置・幅、assistと閉鎖域、城攻略目標と解錠条件を個別確定する（#45） |
| F44 | blocked | R012,R013,R030,R034,R035 | 未生成・mask未作成 | 霞ヶ池西岸・栄螺山。bottom→F42.top、left→F43.right、top→F45.bottom。池／堀・高低差、各出口の位置・幅、assistと閉鎖域、城攻略目標と解錠条件を個別確定する（#45） |
| F45 | blocked | R012,R004,R030,R034,R035 | 未生成・mask未作成 | 霞ヶ池北岸・ことじ灯籠。bottom→F44.top、right→F46.left、left→F50.right。池／堀・高低差、各出口の位置・幅、assistと閉鎖域、城攻略目標と解錠条件を個別確定する（#45） |
| F46 | blocked | R012,R007,R030,R034,R035 | 未生成・mask未作成 | 霞ヶ池東岸・唐崎松。left→F45.right、bottom→F47.top。池／堀・高低差、各出口の位置・幅、assistと閉鎖域、城攻略目標と解錠条件を個別確定する（#45） |
| F47 | blocked | R012,R030,R034,R035 | 未生成・mask未作成 | 曲水・根上松。top→F46.bottom、bottom→F48.top、left→F49.right。池／堀・高低差、各出口の位置・幅、assistと閉鎖域、城攻略目標と解錠条件を個別確定する（#45） |
| F48 | blocked | R012,R030,R034,R035 | 未生成・mask未作成 | 山崎山・花見橋側。top→F47.bottom、bottom→F49.top。池／堀・高低差、各出口の位置・幅、assistと閉鎖域、城攻略目標と解錠条件を個別確定する（#45） |
| F49 | blocked | R012,R030,R034,R035 | 未生成・mask未作成 | 梅林側の南周回路。left→F42.right、right→F47.left、top→F48.bottom。池／堀・高低差、各出口の位置・幅、assistと閉鎖域、城攻略目標と解錠条件を個別確定する（#45） |
| F50 | blocked | R012,R017,R030,R031,R034,R035 | 未生成・mask未作成 | 桂坂口・石川橋。bottom→F43.top、right→F45.left、top→F51.bottom。池／堀・高低差、各出口の位置・幅、assistと閉鎖域、城攻略目標と解錠条件を個別確定する（#45） |
| F51 | blocked | R017,R031,R034,R035 | 未生成・mask未作成 | 石川門の枡形。left→F52.right、bottom→F50.top。池／堀・高低差、各出口の位置・幅、assistと閉鎖域、城攻略目標と解錠条件を個別確定する（#45） |
| F52 | blocked | R017,R031,R034,R035 | 未生成・mask未作成 | 三の丸。right→F51.left、top→F53.bottom、left→F54.right、bottom→F58.top。池／堀・高低差、各出口の位置・幅、assistと閉鎖域、城攻略目標と解錠条件を個別確定する（#45） |
| F53 | blocked | R017,R031,R034,R035 | 未生成・mask未作成 | 菱櫓・五十間長屋。bottom→F52.top、door-west→F55.door-hishi、door-south→F54.door-north。池／堀・高低差、各出口の位置・幅、assistと閉鎖域、城攻略目標と解錠条件を個別確定する（#45） |
| F54 | blocked | R017,R031,R034,R035 | 未生成・mask未作成 | 橋爪門・橋爪門続櫓。right→F52.left、left→F55.right、door-north→F53.door-south。池／堀・高低差、各出口の位置・幅、assistと閉鎖域、城攻略目標と解錠条件を個別確定する（#45） |
| F55 | blocked | R017,R031,R034,R035 | 未生成・mask未作成 | 二の丸。door-hishi→F53.door-west、right→F54.left、left→F56.right、bottom→F57.top。池／堀・高低差、各出口の位置・幅、assistと閉鎖域、城攻略目標と解錠条件を個別確定する（#45） |
| F56 | blocked | R017,R031,R034,R035 | 未生成・mask未作成 | 低地の玉泉院丸庭園。right→F55.left。池／堀・高低差、各出口の位置・幅、assistと閉鎖域、城攻略目標と解錠条件を個別確定する（#45） |
| F57 | blocked | R017,R031,R034,R035 | 未生成・mask未作成 | 極楽橋・本丸附段・三十間長屋側。top→F55.bottom、right→F59.left。3攻略目標完了後にF59本丸入口を解錠。池／堀・高低差、各出口の位置・幅、assistと閉鎖域、城攻略目標と解錠条件を個別確定する（#45） |
| F58 | blocked | R017,R031,R034,R035 | 未生成・mask未作成 | 鶴の丸・東の丸側。top→F52.bottom、left→F59.right。3攻略目標完了後にF59本丸入口を解錠。池／堀・高低差、各出口の位置・幅、assistと閉鎖域、城攻略目標と解錠条件を個別確定する（#45） |
| F59 | blocked | R017,R031,R034,R035 | 未生成・mask未作成 | 高い本丸。left→F57.right、right→F58.left、door-tower→F60.door-base。池／堀・高低差、各出口の位置・幅、assistと閉鎖域、城攻略目標と解錠条件を個別確定する（#45） |
| F60 | blocked | R017,R031,R034,R035 | 未生成・mask未作成 | 本丸内のイマジナリー天守上層。door-base→F59.door-tower。池／堀・高低差、各出口の位置・幅、assistと閉鎖域、城攻略目標と解錠条件を個別確定する（#45） |
