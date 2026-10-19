# MAP生成契約チェックリスト

2026-10-18: サニーランドは口述と創作の円環接続へ更新。旧pending6接続は削除済み。

`map-asset-registry.md` の130行を、生成可能にするまで追跡する行単位チェックリスト。接続の正本は `map-topology.md` の「MAP相互接続台帳 v2」、画面主役と主路は `map-specifications.md`、マスク形式は `sit-field-mask` である。全行は `blocked` または `legacy-needs-review` で始める。`TBD` が空でない限り `ready` にしない。台帳整合の独立再監査は [第3周レビュー](reviews/artifact-redteam/20261016-map-ledger-round3.md) を参照。

**注記**: ステータス名 `recreate-required-1920x1080` は名前は1920×1080だが1672×941（16:9）も許容する（改名は別件）。

**2026-10-18 / #51**: E01–E13/F01–F03は全て `recreate-required-1920x1080`、生成契約は `blocked`。以下の旧画像パスは参照専用で、旧mask・旧passは新候補の採用根拠にならない。現行再作成状態は [候補台帳](teramachi-rebuild-candidates.md)、建物群の生成前入力は [制作前確認](production/20261018-teramachi-preflight.md) を参照する。

| ID | 状態 | Ref | mask / 出力 | 具体的TBD |
|---|---|---|---|---|
| E01 | recreate-required-1920x1080 | R006,R011 | `assets/images/fields/legacy/E01.png`; mask未記録 | 園庭の既存画像におけるE05(bottom)/E11(door-west)の実端、幼稚園期のtraversalを採寸する。E02との接続は#51で廃止 |
| E02 | recreate-required-1920x1080 | R006,R011 | `assets/images/fields/legacy/E02.png`; mask未記録 | E01/E03/N2の三端と用水のblocked域を実画像から記録する |
| E03 | recreate-required-1920x1080 | R006,R011 | `assets/images/fields/legacy/E03.png`; mask未記録 | E02/E04/E10端、火の見櫓周囲のblocked域を記録する |
| E04 | recreate-required-1920x1080 | R006,R011 | `assets/images/fields/legacy/E04.png`; mask未記録 | E03/E05/E11端と山門のforeground域を記録する |
| E05 | recreate-required-1920x1080 | R006,R011 | `assets/images/fields/legacy/E05.png`; mask未記録 | 用水・井戸のblocked域とE04/E06端、top側のE01正門(#51)を記録する |
| E06 | recreate-required-1920x1080 | R006,R011 | `assets/images/fields/legacy/E06.png`; mask未記録 | E05/E07端、銭湯煙突・雪山のforeground/blockedを記録する |
| E07 | recreate-required-1920x1080 | R006,R011 | `assets/images/fields/legacy/E07.png`; mask未記録 | E06/E08を結ぶuniversalスロープの幅・折返しを記録する |
| E08 | recreate-required-1920x1080 | R006,R011 | `assets/images/fields/legacy/E08.png`; mask未記録 | E07/E09端、F03ドア、団地棟のforegroundを記録する |
| E09 | recreate-required-1920x1080 | R006,R011,R025 | 1254×1254のv6候補・maskは参照専用。新規出力は1920×1080（返せない場合は16:9の1672×941）、prompt・参照画像・mask・red-teamを新たに記録する | v6のleft→top石段・assist-only設計を参照し、16:9版を再生成する |
| E10 | recreate-required-1920x1080 | R006,R011 | `assets/images/fields/legacy/E10.png`; mask未記録 | E03.top入口とE02.leftへのright出口以外を禁止辺とする（#51ループ化。E12への勝手口の扉はTBD） |
| E11 | recreate-required-1920x1080 | R006,R011,R024 | 旧境内画像は参照専用。新背景・mask未作成 | #60の屋外境内。E04端、E01.door-west通用門（境内の右＝東側）、F01正面扉、池・墓地のblocked域を記録。E12/F02屋外doorなし。共通外観参照未通過 |
| E12 | recreate-required-1920x1080 | R006,R011,R021,R024 | 旧庫裏画像は参照専用。新背景・mask未作成 | #60/#51の西（本堂から見て左）の屋内住居。F01.door-west↔door-hallのみ。内部廊下の扉位置、幅・段差・回転域、火事時遮断範囲がTBD。F02直結なし |
| E13 | recreate-required-1920x1080 | R006,R011 | `assets/images/fields/legacy/E13.png`; mask未記録 | E09石段とN10車椅子坂の端・通行クラスを記録する |
| E14 | legacy-needs-review | R005,R011 | `assets/images/fields/legacy/E14.png`; mask未記録 | N1/N11/N9端、百貨店door（相手はF83.door-street）、封鎖期のN9遷移を記録する |
| E15 | legacy-needs-review | R005 | `assets/images/fields/legacy/E15.png`; mask未記録 | 3階（kako-jun 2026-10-19）。door-elevator（階選択遷移。全階から行き先を選ぶ。4階は条件つき）、売場通路のuniversal幅を記録する。E15（3階・玩具売場）は2階F85と無関係（決定 2026-10-19） |
| E16 | legacy-needs-review | R005 | `assets/images/fields/legacy/E16.png`; mask未記録 | 5階（kako-jun決定 2026-10-19、#87。実在の大和は8階レストラン街）。door-elevator（階選択遷移。4階は条件つき）、再訪時の同一導線を記録する |
| E17 | legacy-needs-review | R013,R011 | `assets/images/fields/legacy/E17.png`; mask未記録 | E19/N1端、E18door、格子・側溝のblocked域を記録する |
| E18 | legacy-needs-review | R013 | `assets/images/fields/legacy/E18.png`; mask未記録 | E17door、座敷の段差・車椅子可否を決める |
| E19 | legacy-needs-review | R011,R013 | `assets/images/fields/legacy/E19.png`; mask未記録 | N2/E17端、駐車場枝の画面内終端を記録する |
| E20 | legacy-needs-review | R011 | `assets/images/fields/legacy/E20.png`; mask未記録 | N9端、車寄せのuniversal幅と入口foregroundを記録する |
| E21 | legacy-needs-review | R011 | `assets/images/fields/legacy/E21.png`; mask未記録 | N11端、能登／内灘乗車door、広場の禁止辺を記録する |
| E22 | legacy-needs-review | R007,R008 | `assets/images/fields/legacy/E22.png`; mask未記録 | N8/F04端、折返し主路と廃遊具のblocked域を記録する |
| E23 | legacy-needs-review | R007 | `assets/images/fields/legacy/E23.png`; mask未記録 | 小さな屋外空間・巨大シャチホコ。水族館出口→屋外動物園。ラッコ館・海底洞窟の入口出口。M008戦は屋外、噴水と断定しない。 door-aquarium→E24.door-outdoor、door-zoo→F10.door-hub、door-otter-in→F64.door-entry、door-otter-out→F64.door-exit、door-cave-in→F65.door-entry、door-cave-out→F65.door-exit。旧画像は参照専用。pixel/mask/幅TBD |
| E24 | legacy-needs-review | R007 | `assets/images/fields/legacy/E24.png`; mask未記録 | 格子状水槽の地下水族館。出口付近にピラルク巨大水槽。壁際にサメ標本・クジラの陰茎標本。展示格子と通行交点は別。 door-corridor→F09.door-aquarium、door-outdoor→E23.door-aquarium。旧画像は参照専用。pixel/mask/幅TBD |
| E25 | legacy-needs-review | R007 | `assets/images/fields/legacy/E25.png`; mask未記録 | 下り渡り廊下途中・右側のゲームセンター。右は下降時の進行基準。F08前半への割当はゲーム配置。 door-corridor→F08.door-arcade-right。旧画像は参照専用。pixel/mask/幅TBD |
| E26 | legacy-needs-review | R014,R015 | `assets/images/fields/legacy/E26.png`; mask未記録 | N3端、駅出口と線路端のblocked域を記録する |
| E27 | legacy-needs-review | R015 | `assets/images/fields/legacy/E27.png`; mask未記録 | F11端、海側blocked帯と締まった砂のuniversal帯を記録する |
| E28 | legacy-needs-review | R004 | `assets/images/fields/legacy/E28.png`; mask未記録 | E21/E29door、車内通路とドア回転域を記録する |
| E29 | legacy-needs-review | R004 | `assets/images/fields/legacy/E29.png`; mask未記録 | N5端、終端線路のblocked域に加え、右辺→F84.left（茂みの小径。道路ではない。暫定入口、入口MAPは要確認）を記録する |
| E30 | legacy-needs-review | R004 | `assets/images/fields/legacy/E30.png`; mask未記録 | N7/E31端、家door、海側blocked域を記録する |
| E31 | legacy-needs-review | R004 | `assets/images/fields/legacy/E31.png`; mask未記録・採用禁止 | 既存画像は海が上側で、既定の「能登の海は下側」に違反する。回転での救済はしない。E30端・桟橋終端・海/テトラblocked域を満たす再構図版が必要 |
| E32 | legacy-needs-review | R016 | `assets/images/fields/legacy/E32.png`; mask未記録 | 被災前の廃校（#89で被災前へ移動）。F84.right→E32.left、崩落棟blocked域を記録する。画像は据え置き |
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
| F01 | recreate-required-1920x1080 | R021,R024 | 旧本堂画像は参照専用。新背景・mask未作成 | #60の中央屋内本堂。E11南、E12西、F02東の扉位置、畳・仏具と主路、段差・幅・回転域を記録する |
| F02 | recreate-required-1920x1080 | R021,R024 | 旧遊戯室画像は参照専用。新背景・mask未作成 | #60/#51の東（右）の屋内幼稚園。F01.door-east↔F02.door-west（本堂側＝西から入る）の扉位置・廊下長、舞台袖・椅子・主路の分離、段差・幅・回転域を記録する。E12直結なし |
| F03 | recreate-required-1920x1080 | R021,R024 | 未生成・mask未作成 | 県営住宅室内の玄関段差・回転域・E08doorを創作寸法で決める |
| F04 | blocked | R007,R008,R021,R027 | 未生成・mask未作成 | E22/F05端、東屋脇の枝なし蛇行主路の安全幅を決める |
| F05 | blocked | R007,R008,R021,R027 | 未生成・mask未作成 | F04/F06端、崩落石垣を避けるassist主路の幅を決める |
| F06 | blocked | R007,R008,R021,R027 | 未生成・mask未作成 | F05/F07端、山頂戦闘域と展望柵のblocked域を決める |
| F07 | blocked | R027 | 未生成・mask未作成 | 八角形エントランス1階・受付。door-corridor→F08.door-entry、door-stairs→F61.door-stairs、bottom→F06.top。八角形ホールの一辺から1階へ。受付横に階段と長い廊下への一辺。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| F08 | blocked | R027 | 未生成・mask未作成 | 雪の森に囲まれた下り渡り廊下・前半。door-entry→F07.door-corridor、door-next→F09.door-prev、door-arcade-right→E25.door-corridor。全2MAPの下り廊下、雪の森。途中の下降時右へゲームセンター（前半割当はゲーム配置）。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| F09 | blocked | R027 | 未生成・mask未作成 | 雪の森に囲まれた下り渡り廊下・後半。door-prev→F08.door-next、door-aquarium→E24.door-corridor。長い下り廊下後半から地下水族館へ。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| F10 | blocked | R027 | 未生成・mask未作成 | 狭い格子状の昭和の屋外動物園。door-hub→E23.door-zoo、door-stairs→F63.door-zoo。格子状の狭い劣悪な昭和の屋外檻。動物種・交点の通行はTBD。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| F11 | blocked | R014,R015,R021 | 未生成・mask未作成 | N3/E27端、砂丘頂の柵・深砂・海側のblocked域を決める |
| F12 | blocked | R016,R028,R029 | 未生成・mask未作成 | F13/F18端、E29と同一地形の被災後差分を決める |
| F13 | blocked | R016,R028,R029 | 未生成・mask未作成 | F12/F14端、仮設板路のassist可否と地割れblocked域を決める |
| F14 | blocked | R016,R028,R029 | 未生成・mask未作成 | F13/F15端、倒木・神社枝封鎖の範囲を決める |
| F15 | blocked | R016,R028,R029 | 未生成・mask未作成 | F14/F16端、地割れをまたぐ主路の安全表現を決める |
| F16 | blocked | R016,R028,R029 | 未生成・mask未作成 | F15/F17端、実家door封鎖と生活路の範囲を決める |
| F17 | blocked | R016,R028,R029 | 未生成・mask未作成 | F16端、釣り場先端を終端にする柵と海のblocked域を決める |
| F18 | blocked | R016,R028,R029 | 未生成・mask未作成 | F12.right端、廃校の校庭に建つ仮設住宅の生活路・集会所doorを決める。E32への接続は廃止（被災後の廃校は潰れて入れない）。入口は被災前E29.right→F84.leftの被災後版（F12.right） |
| F19 | blocked | R018 | 未生成・mask未作成 | 口・体内入口。door-passage-torso→F74.door-passage-mouth。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |
| F20 | blocked | R018 | 未生成・mask未作成 | 左手通路2・末端。door-passage-base→F77.door-passage-tip。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |
| F21 | blocked | R018 | 未生成・mask未作成 | 右手通路2・末端。door-passage-base→F78.door-passage-tip。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |
| F22 | blocked | R018 | 未生成・mask未作成 | 左足通路3・末端。door-passage-base→F80.door-passage-tip。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |
| F23 | blocked | R018 | 未生成・mask未作成 | 右足通路3・末端。door-passage-base→F82.door-passage-tip。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |
| F24 | blocked | R018 | 未生成・mask未作成 | 頭・脳の迷路通路。door-passage-torso→F74.door-passage-head。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |
| F25 | blocked | R018 | 未生成・mask未作成 | 胃・分岐室。door-passage-torso→F76.door-passage-stomach。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |
| F26 | blocked | R018 | 未生成・mask未作成 | 心臓・分岐室。door-passage-torso→F74.door-passage-heart。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |
| F27 | blocked | R019,R033 | 未生成・mask未作成 | 到着口/F28端、凍結滑走路を通行不能にする空港導線を確定する |
| F28 | blocked | R019,R033 | 未生成・mask未作成 | F27/F29端、凍った泉の画面内終端と乾燥寒冷地資料を確定する |
| F29 | blocked | R019,R033 | 未生成・mask未作成 | F28/F30端、凍結穴・風食岩のblocked域を確定する |
| F30 | blocked | R019 | 未生成・mask未作成 | 攻略双塔の共通基壇。door-left→F31.door-base、door-right→F34.door-base、bottom→F29.top。左右塔は5階建て、雑多な増改築・無駄道・袋小路。左右対称・同一階平面反復を避ける。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| F31 | blocked | R019 | 未生成・mask未作成 | 左塔1階・雑居入口。door-base→F30.door-left、door-up→F66.door-down。左右塔は5階建て、雑多な増改築・無駄道・袋小路。左右対称・同一階平面反復を避ける。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| F32 | blocked | R019 | 未生成・mask未作成 | 左塔3階・配管と混在用途。door-down→F66.door-up、door-up→F67.door-down。左右塔は5階建て、雑多な増改築・無駄道・袋小路。左右対称・同一階平面反復を避ける。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| F33 | blocked | R019 | 未生成・mask未作成 | 左塔5階・M015魔法のみ有効。door-down→F67.door-up、door-bridge→F37.door-left。左右塔は5階建て、雑多な増改築・無駄道・袋小路。左右対称・同一階平面反復を避ける。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| F34 | blocked | R019 | 未生成・mask未作成 | 右塔1階・雑居入口。door-base→F30.door-right、door-up→F68.door-down。左右塔は5階建て、雑多な増改築・無駄道・袋小路。左右対称・同一階平面反復を避ける。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| F35 | blocked | R019 | 未生成・mask未作成 | 右塔3階・増改築の交差路。door-down→F68.door-up、door-up→F69.door-down。左右塔は5階建て、雑多な増改築・無駄道・袋小路。左右対称・同一階平面反復を避ける。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| F36 | blocked | R019 | 未生成・mask未作成 | 右塔5階・M016アビリティのみ有効。door-down→F69.door-up、door-bridge→F37.door-right。左右塔は5階建て、雑多な増改築・無駄道・袋小路。左右対称・同一階平面反復を避ける。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| F37 | blocked | R019 | 未生成・mask未作成 | 塔間空中通路・シャー判明と雑魚共闘。door-left→F33.door-bridge、door-right→F36.door-bridge、door-third→F70.door-bridge。左右塔は5階建て、雑多な増改築・無駄道・袋小路。左右対称・同一階平面反復を避ける。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| F38 | blocked | R019 | 未生成・mask未作成 | 脱出第3塔1階・出口直前S005戦。door-up→F73.door-down。5階建て第3塔の下降。各階は攻略塔同程度の面積。宝箱取捨選択、タイマー継続。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
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

## 2026-10-18追加ID（番号は既存MAPを移動しない）

| ID | 状態 | Ref | mask / 出力 | 具体的TBD |
|---|---|---|---|---|
| F61 | blocked | R027 | 未生成・mask未作成 | 八角形エントランス2階・全方向の窓。door-hotel→F62.door-entry、door-stairs→F07.door-stairs。2階は全方向の窓。一辺から和室宿泊棟、階段で1階。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| F62 | blocked | R027 | 未生成・mask未作成 | 廃墟の和室が並ぶ宿泊棟。door-far-end→F63.door-hotel、door-entry→F61.door-hotel。廃墟の和室が並ぶ。入口2階側と屋外階段側の両端。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| F63 | blocked | R027 | 未生成・mask未作成 | 動物園から宿泊棟端への屋外階段。door-zoo→F10.door-stairs、door-hotel→F62.door-far-end。ユーザー創作の動物園→宿泊棟端の屋外階段。assist方法TBD。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| F64 | blocked | R027 | 未生成・mask未作成 | ラッコ館・入口と出口のある任意探索。door-entry→E23.door-otter-in、door-exit→E23.door-otter-out。入口・出口別。宝箱目当ての任意通り抜け。同じ屋外E23へ戻すのはゲーム配置。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| F65 | blocked | R027 | 未生成・mask未作成 | 低予算昭和の海底探検洞窟・任意探索。door-entry→E23.door-cave-in、door-exit→E23.door-cave-out。低予算昭和の海底探検の作り物。ダイオウイカ・難破船・ニンゲン。入口出口別、任意宝箱。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| F66 | blocked | R019 | 未生成・mask未作成 | 左塔2階・迷路状の増築。door-down→F31.door-up、door-up→F32.door-down。左右塔は5階建て、雑多な増改築・無駄道・袋小路。左右対称・同一階平面反復を避ける。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| F67 | blocked | R019 | 未生成・mask未作成 | 左塔4階・無駄道と袋小路。door-down→F32.door-up、door-up→F33.door-down。左右塔は5階建て、雑多な増改築・無駄道・袋小路。左右対称・同一階平面反復を避ける。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| F68 | blocked | R019 | 未生成・mask未作成 | 右塔2階・混在用途の迷路。door-down→F34.door-up、door-up→F35.door-down。左右塔は5階建て、雑多な増改築・無駄道・袋小路。左右対称・同一階平面反復を避ける。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| F69 | blocked | R019 | 未生成・mask未作成 | 右塔4階・無駄道と袋小路。door-down→F35.door-up、door-up→F36.door-down。左右塔は5階建て、雑多な増改築・無駄道・袋小路。左右対称・同一階平面反復を避ける。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| F70 | blocked | R019 | 未生成・mask未作成 | 脱出第3塔5階・宝箱と下り階段。door-bridge→F37.door-third、door-down→F71.door-up。5階建て第3塔の下降。各階は攻略塔同程度の面積。宝箱取捨選択、タイマー継続。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| F71 | blocked | R019 | 未生成・mask未作成 | 脱出第3塔4階・宝箱と下り階段。door-up→F70.door-down、door-down→F72.door-up。5階建て第3塔の下降。各階は攻略塔同程度の面積。宝箱取捨選択、タイマー継続。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| F72 | blocked | R019 | 未生成・mask未作成 | 脱出第3塔3階・宝箱と下り階段。door-up→F71.door-down、door-down→F73.door-up。5階建て第3塔の下降。各階は攻略塔同程度の面積。宝箱取捨選択、タイマー継続。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| F73 | blocked | R019 | 未生成・mask未作成 | 脱出第3塔2階・宝箱と下り階段。door-up→F72.door-down、door-down→F38.door-up。5階建て第3塔の下降。各階は攻略塔同程度の面積。宝箱取捨選択、タイマー継続。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |

## #74追加ID（胴体・肺）

| ID | 状態 | Ref | mask / 出力 | 具体的TBD |
|---|---|---|---|---|
| F74 | blocked | R018 | 未生成・mask未作成 | 上半身・胴体上段。door-passage-mouth→F19.door-passage-torso、door-passage-lower→F76.door-passage-upper、door-passage-head→F24.door-passage-torso、door-passage-left-arm→F77.door-passage-torso、door-passage-right-arm→F78.door-passage-torso、door-passage-heart→F26.door-passage-torso、door-passage-lung→F75.door-passage-torso。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |
| F75 | blocked | R018 | 未生成・mask未作成 | 肺・分岐室。door-passage-torso→F74.door-passage-lung。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |

## #74追加ボリューム（上半身・下半身／手2／足3）

| ID | 状態 | Ref | mask / 出力 | 具体的TBD |
|---|---|---|---|---|
| F76 | blocked | R018 | 未生成・mask未作成 | 下半身・胴体下段。door-passage-upper→F74.door-passage-lower、door-passage-left-leg→F79.door-passage-torso、door-passage-right-leg→F81.door-passage-torso、door-passage-stomach→F25.door-passage-torso。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |
| F77 | blocked | R018 | 未生成・mask未作成 | 左手通路1・付け根側。door-passage-torso→F74.door-passage-left-arm、door-passage-tip→F20.door-passage-base。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |
| F78 | blocked | R018 | 未生成・mask未作成 | 右手通路1・付け根側。door-passage-torso→F74.door-passage-right-arm、door-passage-tip→F21.door-passage-base。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |
| F79 | blocked | R018 | 未生成・mask未作成 | 左足通路1・付け根側。door-passage-torso→F76.door-passage-left-leg、door-passage-middle→F80.door-passage-base。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |
| F80 | blocked | R018 | 未生成・mask未作成 | 左足通路2・中間。door-passage-base→F79.door-passage-middle、door-passage-tip→F22.door-passage-base。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |
| F81 | blocked | R018 | 未生成・mask未作成 | 右足通路1・付け根側。door-passage-torso→F76.door-passage-right-leg、door-passage-middle→F82.door-passage-base。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |
| F82 | blocked | R018 | 未生成・mask未作成 | 右足通路2・中間。door-passage-base→F81.door-passage-middle、door-passage-tip→F23.door-passage-base。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |

## #87/#89追加ID（番号は既存MAPを移動しない）

| ID | 状態 | Ref | mask / 出力 | 具体的TBD |
|---|---|---|---|---|
| F83 | blocked | R005 | 未生成・mask未作成 | デパート1階（入口階）。時計のある吹き抜け（アトリオ参照。出所 https://github.com/kako-jun/sit-by-me/issues/87#issuecomment-6258778050）。実在店に似せないジオラマ、大和4階の時計サロンとは別。door-street→E14.door、door-elevator（階選択遷移。扉に入るとウィンドウで階を選び、選んだ階の扉前に着く。箱は全階を結びMAPを持たない。決定 2026-10-19）。TBD: 売場の中身、1階での出来事。画像生成blocked。 |
| F85 | blocked | R005 | 未生成・mask未作成 | デパート2階（隠し階。https://github.com/kako-jun/sit-by-me/issues/87 2026-10-19の決定）。実在店に似せないジオラマ。door-elevator（階選択遷移）。四角い吹き抜けの廊下だけ（売場は無い。決定 2026-10-19）。歩行域=廊下の環のみ、吹き抜け部分はblocked（歩行マスク契約）。描画=中央の吹き抜けから下の1階が見える（侵入不可）。見える1階=F83(同じ場所を2階から見下ろす視点で描く)。契約: F83の背景を作るときはF85の吹き抜け越しの絵と整合させる(F83の吹き抜け・時計・床の見た目が共通の参照)。決定: 2階は最初から解放（解放条件なし。2026-10-19）。E15（3階・玩具売場）とF85は無関係（決定）。TBD: 吹き抜け縁の落下しない前提、隠し階への行き方（ボタン等）。画像生成blocked。 |
| F86 | blocked | R005 | 未生成・mask未作成 | デパート4階（隠し階・条件つき。最終章で兼六園へ向かう途中にデパートに寄り道すると、階選択で4階も選べるようになる(決定 2026-10-19)。兼六園への道のどのMAP・イベントで寄り道できるかは要確認。強い何かが手に入る。https://github.com/kako-jun/sit-by-me/issues/87 2026-10-19の決定）。実在店に似せないジオラマ。door-elevator（階選択遷移。選択肢に出る条件はシナリオ側）。TBD: 売場の中身、強い何かの中身、寄り道できるMAP・イベント、行き方（ボタン等）。画像生成blocked。 |
| F84 | blocked | R016 | 未生成・mask未作成 | 廃校の校庭（被災前）。left←E29.right（茂みの小径の暫定入口）、right→E32.left。TBD: 入口MAP（E29は暫定）、茂みの見せ方、校庭の見た目、勝手口等の扉、校庭↔E32の辺はright↔leftで選択済み（理由はmap-topology.md）。 |
