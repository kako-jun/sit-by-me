# フィールド画像台帳

## 運用

背景は**1画像1行**で管理する。生成前に各行へ、**一言特徴（この一枚は何の場所か）**、時期・景色（時代／場所／天候／生活の汚れ）・必須接続・禁止辺・通行不能物・車椅子の通行条件・任意枝の有無・**TBD**を埋める。対象画像が描く内容に関わるTBDがあれば生成を `blocked` とする。生成前の入力契約審査と、画像・mask・links・実機確認後の採用readyを別の段階として記録する。

全画像の共通条件は、現代の K県、冬、手作りジオラマ、真上寄り、人物・文字なし。昭和から残る建物や設備は存在してよいが、時代設定を昭和に戻さない。汚れは雪国の日常（融雪水、砂、泥、塩の白残り、黒ずんだ木、錆）であり、廃墟でない場所を廃墟化しない。

寺町では、[map-topology.md の「寺町の地形不変条件」](map-topology.md) が最優先である。河岸段丘の犀川側＝県営住宅、そこへは石段（立てる時期のみ）と車椅子用スロープ（生活経路）が別にある。段丘の反対側＝小学校で、長い通学坂は車椅子で通れる。この関係を壊すMAPは `blocked` とする。

`ready` は全項目が記入済みかつ TBD=なし、`legacy` は既存画像で再生成・差し替えを禁止、`blocked` は個別契約またはTBDが残っている状態である。寺町は2026-10-16の方針により、旧legacyを一枚も採用せず、E01–E13/F01–F03の新候補16枚を揃えて監査後に**一括**でruntimeへ差し替える。混在運用はしない。**「ただの道」「つなぎ」だけは一言特徴にならない**。道なら、交差点・橋・用水・寺の裏門・雪囲い・市場の角・坂の眺めなど、そこでしか成立しない主役を必ず持たせる。

## 130行共通の画像契約

全MAP行は、本文の略表に加えて次の契約を持つ。接続は `map-topology.md` の「MAP相互接続台帳 v2」、主役・時期・主路は `map-specifications.md` の同じID、参考は `map-reference-research.md` の同じIDまたは明示した共通Refを参照する。これらのどれかが無い行は `blocked` とする。

| 必須欄 | 記録方法 |
|---|---|
| 状態・採否・出力 | `blocked` / `legacy-needs-review` / `ready`、背景・prompt・adoptionのパス |
| 必須接続・禁止辺 | v2にある辺だけが必須。そこに無い外周辺は道路を出さない禁止辺 |
| 通行不能物 | 水・建物・塀・柵・深雪・急段差・画面土台。MAP固有物は個別仕様に追記 |
| 車椅子・任意枝 | `universal` / `assist` / `blocked` を `sit-field-mask` の編集PNGに記録。宝箱枝は必須接続と別で画面内終端 |
| 景色・汚れ | 現代K県・冬・手作りジオラマを継承。屋外は融雪水、砂、泥、塩、黒ずみ、錆からMAPの地形に合うものだけ選ぶ。廃墟・被災後以外を荒廃させない |
| 参考・TBD | Ref IDと、未解決なら「どの場所／何の資料／どの判定を得るか」を具体的に書く。`参照待ち`だけは無効 |
| mask・red-team | 生成後にtraversal/foreground edit・runtime・review各パスと敵対レビュー記録を追加し、最終採用 `ready` を検討。未生成であることだけを入力契約審査の妨げにしない |

`legacy` は採用済みを意味しない。実パス・参考・マスク・red-teamが未記録のlegacyは `legacy-needs-review` として扱い、生成根拠にも接続根拠にも使わない。 採用状態はファイルの置き場でなくこの台帳のstatusで管理する（生成物は正本パスへ直接上書きし、使うならコミット・使わないならgitでリバート。[素材配置台帳](production/asset-layout.md)）。

## 個別契約（対象画像の入力契約を独立審査してから生成する）

N1〜N12 の詳細な接続契約は [map-specifications.md](map-specifications.md) と [map-topology.md](map-topology.md) にある。N4 は欠番である。ここでの `blocked` はトポロジー未決を意味しない。画像ごとの現地参照・既存画像端・歩行マスクを照合するまで生成を保留する状態である。

| ID | 画像 | 状態 | 一言特徴 | 時期 | 必須接続 | TBD |
|---|---|---|---|---|
| N1 | `kanazawa-saigawa-bridge` | blocked | 雪と融雪水を抱えた犀川の鉄橋 | 幼稚園前半 | 茶屋街南岸 → 犀川橋 → 香林坊北岸 | 橋の実在形状・既存E14/E17端を参照してマスク照合 |
| N2 | `teramachi-entry-slope` | blocked | 用水と黒瓦を見上げる寺町の坂 | 幼稚園前半 | コンビニ北 → 寺町connector南 | 既存E02/E19端を参照してマスク照合 |
| N3 | `uchinada-pine-dune-path` | blocked | 風に鳴るクロマツ防砂林の木道 | 中学生後半 | 内灘駅 → 砂丘頂 → 砂浜 | 実在木道の幅・既存E26/E27端を参照してマスク照合 |
| N5 | `noto-uphill` | blocked | 海を背にして上がる雪混じりの漁村坂 | 幼稚園後半 | 低地 → 尾根 | 被災前後の同一端をマスク照合 |
| N6 | `noto-ridge` | blocked | 海を下に見下ろす小さな神社の尾根 | 幼稚園後半 | N5 → N7 | 被災前後の同一端をマスク照合 |
| N7 | `noto-downhill` | blocked | 船揚げ場の屋根へ降りる急な集落坂 | 幼稚園後半 | 尾根 → 実家低地 | 被災前後の同一端をマスク照合 |
| N8 | `utatsuyama-trailhead-slope` | blocked | 浅野川東岸の寺門と杉林の登り口 | 小学生前半 | 武蔵ヶ辻 → 浅野川橋 → 山中腹 | 東岸橋・既存E22端を参照してマスク照合 |
| N9 | `hirosaka-slope` | blocked | 松と石垣の間で二手に分かれる広坂 | 壮年編 | 香林坊 → 兼六園／病院側 | 封鎖用柵の差分・既存E14/E20端を照合 |
| N10 | `teramachi-school-slope` | blocked | 雪の手すりを伝う校門前の長い坂 | 中学生前半 | slope-top → 校門 | 既存E13/E33の校門位置をマスク照合 |
| N11 | `musashigatsuji-crossing` | blocked | バス屋根と市場アーケードが交わる武蔵ヶ辻 | 幼稚園前半〜再訪 | 香林坊 → 金沢駅／浅野川橋側 | 既存E14/E21・N8端をマスク照合 |
| N12 | `asanogawa-line-interior` | blocked | 結露した窓と赤い座席の浅野川線車内 | 中学生後半 | 金沢駅乗車 → 車内通路 → 内灘駅降車 | 実車扉幅と車椅子回転域を参照してマスク照合 |

## 既存画像（再生成禁止・個別契約を逆算して追記する対象）

| ID | 画像 | 地区 | 状態 |
|---|---|---|---|
| E01 | `assets/images/fields/legacy/E01.png` | 寺町 | retired-replacement-required |
| E02 | `assets/images/fields/legacy/E02.png` | 寺町 | retired-replacement-required |
| E03 | `assets/images/fields/legacy/E03.png` | 寺町 | retired-replacement-required |
| E04 | `assets/images/fields/legacy/E04.png` | 寺町 | retired-replacement-required |
| E05 | `assets/images/fields/legacy/E05.png` | 寺町 | retired-replacement-required |
| E06 | `assets/images/fields/legacy/E06.png` | 寺町 | retired-replacement-required |
| E07 | `assets/images/fields/legacy/E07.png` | 寺町 | retired-replacement-required |
| E08 | `assets/images/fields/legacy/E08.png` | 寺町 | retired-replacement-required |
| E09 | `assets/images/fields/legacy/E09.png` | 寺町 | retired-replacement-required |
| E10 | `assets/images/fields/legacy/E10.png` | 寺町 | retired-replacement-required |
| E11 | `assets/images/fields/legacy/E11.png` | 寺町 | retired-replacement-required |
| E12 | `assets/images/fields/legacy/E12.png` | 寺町 | retired-replacement-required |
| E13 | `assets/images/fields/legacy/E13.png` | 寺町 | retired-replacement-required |
| E14 | `assets/images/fields/legacy/E14.png` | 香林坊 | legacy |
| E15 | `assets/images/fields/legacy/E15.png` | 香林坊 | legacy |
| E16 | `assets/images/fields/legacy/E16.png` | 香林坊 | legacy |
| E17 | `assets/images/fields/legacy/E17.png` | 茶屋街 | legacy |
| E18 | `assets/images/fields/legacy/E18.png` | 茶屋街 | legacy |
| E19 | `assets/images/fields/legacy/E19.png` | 戻り道 | legacy |
| E20 | `assets/images/fields/legacy/E20.png` | 病院 | legacy |
| E21 | `assets/images/fields/legacy/E21.png` | 金沢駅 | legacy |
| E22 | `assets/images/fields/legacy/E22.png` | 卯辰山 | legacy |
| E23 | `assets/images/fields/legacy/E23.png` | サニーランド | 小さな屋外空間・巨大シャチホコ。水族館出口→屋外動物園。ラッコ館・海底洞窟の入口出口。M008戦は屋外、噴水と断定しない。 door-aquarium→E24.door-outdoor、door-zoo→F10.door-hub、door-otter-in→F64.door-entry、door-otter-out→F64.door-exit、door-cave-in→F65.door-entry、door-cave-out→F65.door-exit。旧画像は参照専用。pixel/mask/幅TBD |
| E24 | `assets/images/fields/legacy/E24.png` | サニーランド | 格子状水槽の地下水族館。出口付近にピラルク巨大水槽。壁際にサメ標本・クジラの陰茎標本。展示格子と通行交点は別。 door-corridor→F09.door-aquarium、door-outdoor→E23.door-aquarium。旧画像は参照専用。pixel/mask/幅TBD |
| E25 | `assets/images/fields/legacy/E25.png` | サニーランド | 下り渡り廊下途中・右側のゲームセンター。右は下降時の進行基準。F08前半への割当はゲーム配置。 door-corridor→F08.door-arcade-right。旧画像は参照専用。pixel/mask/幅TBD |
| E26 | `assets/images/fields/legacy/E26.png` | 内灘 | legacy |
| E27 | `assets/images/fields/legacy/E27.png` | 内灘 | legacy |
| E28 | `assets/images/fields/legacy/E28.png` | 能登（被災前） | legacy |
| E29 | `assets/images/fields/legacy/E29.png` | 能登（被災前） | legacy |
| E30 | `assets/images/fields/legacy/E30.png` | 能登（被災前） | legacy |
| E31 | `assets/images/fields/legacy/E31.png` | 能登（被災前） | legacy |
| E32 | `assets/images/fields/legacy/E32.png` | 能登（被災前） | legacy |
| E33 | `assets/images/fields/legacy/E33.png` | 小学校 | legacy |

旧版・不採用候補（`-v2` 以外の旧版、寺町の地蔵版、蛸島以外の小木駅版、駅前 v1/v2、サニーランド v2）は参照専用であり、マップの契約対象に数えない。

## 個別仕様済みの将来枠（全て `blocked`：生成前の参照・マスク照合待ち）

全行の一言特徴・方位・主路・通行条件は [map-specifications.md](map-specifications.md) に確定済み。下表の「未決のため必要な個別契約」は旧見出しであり、以降の各記述は参照・マスク照合項目として読む。

| ID | 画像 | 地区 | 未決のため必要な個別契約 |
|---|---|---|---|
| F01 | `teramachi-main-hall-interior` | 寺町 | ドア接続・時期・室内通路 |
| F02 | `teramachi-kindergarten-hall` | 寺町 | ドア接続・舞台と通路 |
| F03 | `teramachi-danchi-interior` | 寺町 | ドア接続・車椅子動線 |
| F04 | `utatsuyama-route-02` | 卯辰山 | 接続辺・中ボスまでの主経路 |
| F05 | `utatsuyama-route-03` | 卯辰山 | 接続辺・中ボスまでの主経路 |
| F06 | `utatsuyama-summon-clearing` | 卯辰山 | 接続辺・戦闘場の通行条件 |
| F07 | `F07` | サニーランド | 八角形エントランス1階・受付。八角形ホールの一辺から1階へ。受付横に階段と長い廊下への一辺。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| F08 | `F08` | サニーランド | 雪の森に囲まれた下り渡り廊下・前半。全2MAPの下り廊下、雪の森。途中の下降時右へゲームセンター（前半割当はゲーム配置）。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| F09 | `F09` | サニーランド | 雪の森に囲まれた下り渡り廊下・後半。長い下り廊下後半から地下水族館へ。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| F10 | `F10` | サニーランド | 狭い格子状の昭和の屋外動物園。格子状の狭い劣悪な昭和の屋外檻。動物種・交点の通行はTBD。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| F11 | `uchinada-dune-summit` | 内灘 | N3・砂浜との接続、車椅子経路 |
| F12 | `noto-post-station` | 能登（被災後） | 被災前版との同一接続 |
| F13 | `noto-post-uphill` | 能登（被災後） | N5との同一接続 |
| F14 | `noto-post-ridge` | 能登（被災後） | N6との同一接続 |
| F15 | `noto-post-downhill` | 能登（被災後） | N7との同一接続 |
| F16 | `noto-post-house` | 能登（被災後） | 実家版との同一接続 |
| F17 | `noto-post-fishing-spot` | 能登（被災後） | 釣り場版との同一接続 |
| F18 | `noto-temporary-housing` | 能登（被災後） | 接続辺・生活動線（入口はF12.right。被災前E29.right→F84.leftの被災後版。#89） |
| F19 | `F19` | 抽象体内 | 口・体内入口。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |
| F20 | `F20` | 抽象体内 | 左手通路2・末端。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |
| F21 | `F21` | 抽象体内 | 右手通路2・末端。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |
| F22 | `F22` | 抽象体内 | 左足通路3・末端。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |
| F23 | `F23` | 抽象体内 | 右足通路3・末端。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |
| F24 | `F24` | 抽象体内 | 頭・脳の迷路通路。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |
| F25 | `F25` | 抽象体内 | 胃・分岐室。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |
| F26 | `F26` | 抽象体内 | 心臓・分岐室。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |
| F27 | `overseas-airport` | 海外 | 到着口・荒れ地への接続 |
| F28 | `overseas-wasteland-a` | 海外 | 空港・荒れ地Bへの接続 |
| F29 | `overseas-wasteland-b` | 海外 | 荒れ地A・都市への接続 |
| F30 | `F30` | 海外3塔 | 攻略双塔の共通基壇。左右塔は5階建て、雑多な増改築・無駄道・袋小路。左右対称・同一階平面反復を避ける。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| F31 | `F31` | 海外3塔 | 左塔1階・雑居入口。左右塔は5階建て、雑多な増改築・無駄道・袋小路。左右対称・同一階平面反復を避ける。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| F32 | `F32` | 海外3塔 | 左塔3階・配管と混在用途。左右塔は5階建て、雑多な増改築・無駄道・袋小路。左右対称・同一階平面反復を避ける。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| F33 | `F33` | 海外3塔 | 左塔5階・M015魔法のみ有効。左右塔は5階建て、雑多な増改築・無駄道・袋小路。左右対称・同一階平面反復を避ける。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| F34 | `F34` | 海外3塔 | 右塔1階・雑居入口。左右塔は5階建て、雑多な増改築・無駄道・袋小路。左右対称・同一階平面反復を避ける。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| F35 | `F35` | 海外3塔 | 右塔3階・増改築の交差路。左右塔は5階建て、雑多な増改築・無駄道・袋小路。左右対称・同一階平面反復を避ける。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| F36 | `F36` | 海外3塔 | 右塔5階・M016アビリティのみ有効。左右塔は5階建て、雑多な増改築・無駄道・袋小路。左右対称・同一階平面反復を避ける。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| F37 | `F37` | 海外3塔 | 塔間空中通路・シャー判明と雑魚共闘。左右塔は5階建て、雑多な増改築・無駄道・袋小路。左右対称・同一階平面反復を避ける。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| F38 | `F38` | 海外3塔 | 脱出第3塔1階・出口直前S005戦。5階建て第3塔の下降。各階は攻略塔同程度の面積。宝箱取捨選択、タイマー継続。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| F39 | `k-airport-exterior` | K空港 | 広場・搭乗口への接続 |
| F40 | `k-airport-interior` | K空港 | ドア接続・搭乗動線 |
| F41 | `kenrokuen-1` | 兼六園 | 真弓坂側の南西入口・v2接続、幅／高低差／通行条件TBD（blocked） |
| F42 | `kenrokuen-2` | 兼六園 | 時雨亭・長谷池・v2接続、幅／高低差／通行条件TBD（blocked） |
| F43 | `kenrokuen-3` | 兼六園 | 瓢池・夕顔亭・翠滝下段・v2接続、幅／高低差／通行条件TBD（blocked） |
| F44 | `kenrokuen-4` | 兼六園 | 霞ヶ池西岸・栄螺山・v2接続、幅／高低差／通行条件TBD（blocked） |
| F45 | `kenrokuen-5` | 兼六園 | 霞ヶ池北岸・ことじ灯籠・v2接続、幅／高低差／通行条件TBD（blocked） |
| F46 | `kenrokuen-6` | 兼六園 | 霞ヶ池東岸・唐崎松・v2接続、幅／高低差／通行条件TBD（blocked） |
| F47 | `kenrokuen-7` | 兼六園 | 曲水・根上松・v2接続、幅／高低差／通行条件TBD（blocked） |
| F48 | `kenrokuen-8` | 兼六園 | 山崎山・花見橋側・v2接続、幅／高低差／通行条件TBD（blocked） |
| F49 | `kenrokuen-9` | 兼六園 | 梅林側の南周回路・v2接続、幅／高低差／通行条件TBD（blocked） |
| F50 | `kenrokuen-10` | 兼六園 | 桂坂口・石川橋・v2接続、幅／高低差／通行条件TBD（blocked） |
| F51 | `castle-1` | 金沢城 | 石川門の枡形・v2接続、幅／高低差／通行条件TBD（blocked） |
| F52 | `castle-2` | 金沢城 | 三の丸・v2接続、幅／高低差／通行条件TBD（blocked） |
| F53 | `castle-3` | 金沢城 | 菱櫓・五十間長屋・v2接続、幅／高低差／通行条件TBD（blocked） |
| F54 | `castle-4` | 金沢城 | 橋爪門・橋爪門続櫓・v2接続、幅／高低差／通行条件TBD（blocked） |
| F55 | `castle-5` | 金沢城 | 二の丸・v2接続、幅／高低差／通行条件TBD（blocked） |
| F56 | `castle-6` | 金沢城 | 低地の玉泉院丸庭園・v2接続、幅／高低差／通行条件TBD（blocked） |
| F57 | `castle-7` | 金沢城 | 極楽橋・本丸附段・三十間長屋側・v2接続、幅／高低差／通行条件TBD（blocked） |
| F58 | `castle-8` | 金沢城 | 鶴の丸・東の丸側・v2接続、幅／高低差／通行条件TBD（blocked） |
| F59 | `castle-9` | 金沢城 | 高い本丸・v2接続、幅／高低差／通行条件TBD（blocked） |
| F60 | `castle-10` | 金沢城 | 本丸内のイマジナリー天守上層・v2接続、幅／高低差／通行条件TBD（blocked） |

## 2026-10-18追加ID（番号は既存MAPを移動しない）

| ID | 管理名 | 地区 | 契約 |
|---|---|---|---|
| F61 | `F61` | サニーランド | 八角形エントランス2階・全方向の窓。2階は全方向の窓。一辺から和室宿泊棟、階段で1階。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| F62 | `F62` | サニーランド | 廃墟の和室が並ぶ宿泊棟。廃墟の和室が並ぶ。入口2階側と屋外階段側の両端。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| F63 | `F63` | サニーランド | 動物園から宿泊棟端への屋外階段。ユーザー創作の動物園→宿泊棟端の屋外階段。assist方法TBD。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| F64 | `F64` | サニーランド | ラッコ館・入口と出口のある任意探索。入口・出口別。宝箱目当ての任意通り抜け。同じ屋外E23へ戻すのはゲーム配置。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| F65 | `F65` | サニーランド | 低予算昭和の海底探検洞窟・任意探索。低予算昭和の海底探検の作り物。ダイオウイカ・難破船・ニンゲン。入口出口別、任意宝箱。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| F66 | `F66` | 海外3塔 | 左塔2階・迷路状の増築。左右塔は5階建て、雑多な増改築・無駄道・袋小路。左右対称・同一階平面反復を避ける。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| F67 | `F67` | 海外3塔 | 左塔4階・無駄道と袋小路。左右塔は5階建て、雑多な増改築・無駄道・袋小路。左右対称・同一階平面反復を避ける。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| F68 | `F68` | 海外3塔 | 右塔2階・混在用途の迷路。左右塔は5階建て、雑多な増改築・無駄道・袋小路。左右対称・同一階平面反復を避ける。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| F69 | `F69` | 海外3塔 | 右塔4階・無駄道と袋小路。左右塔は5階建て、雑多な増改築・無駄道・袋小路。左右対称・同一階平面反復を避ける。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| F70 | `F70` | 海外3塔 | 脱出第3塔5階・宝箱と下り階段。5階建て第3塔の下降。各階は攻略塔同程度の面積。宝箱取捨選択、タイマー継続。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| F71 | `F71` | 海外3塔 | 脱出第3塔4階・宝箱と下り階段。5階建て第3塔の下降。各階は攻略塔同程度の面積。宝箱取捨選択、タイマー継続。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| F72 | `F72` | 海外3塔 | 脱出第3塔3階・宝箱と下り階段。5階建て第3塔の下降。各階は攻略塔同程度の面積。宝箱取捨選択、タイマー継続。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| F73 | `F73` | 海外3塔 | 脱出第3塔2階・宝箱と下り階段。5階建て第3塔の下降。各階は攻略塔同程度の面積。宝箱取捨選択、タイマー継続。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |

## #74追加ID（胴体・肺）

| ID | 管理名 | 地区 | 契約 |
|---|---|---|---|
| F74 | `F74` | 抽象体内 | 上半身・胴体上段。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |
| F75 | `F75` | 抽象体内 | 肺・分岐室。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |

## #74追加ボリューム（上半身・下半身／手2／足3）

| ID | 管理名 | 地区 | 契約 |
|---|---|---|---|
| F76 | `F76` | 抽象体内 | 下半身・胴体下段。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |
| F77 | `F77` | 抽象体内 | 左手通路1・付け根側。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |
| F78 | `F78` | 抽象体内 | 右手通路1・付け根側。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |
| F79 | `F79` | 抽象体内 | 左足通路1・付け根側。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |
| F80 | `F80` | 抽象体内 | 左足通路2・中間。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |
| F81 | `F81` | 抽象体内 | 右足通路1・付け根側。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |
| F82 | `F82` | 抽象体内 | 右足通路2・中間。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |

## #87/#89追加ID（番号は既存MAPを移動しない）

| ID | 管理名 | 地区 | 契約 |
|---|---|---|---|
| F83 | `F83` | 香林坊 | デパート1階（入口階）。時計のある吹き抜け（アトリオ参照、出所 https://github.com/kako-jun/sit-by-me/issues/87#issuecomment-6258778050）。実在店に似せないジオラマ。door-street→E14.door、door-toys↔E15.door-korinbo、door-restaurant↔E16.door-lobby、door-2f↔F85.door-lower。階移動はエレベーターだけ・エレベーターの箱構成と売場の中身TBD、画像生成blocked。 |
| F85 | `F85` | 香林坊 | デパート2階（隠し階。https://github.com/kako-jun/sit-by-me/issues/87 2026-10-19の決定）。実在店に似せないジオラマ。door-lower↔F83.door-2f、door-upper↔E15.door-2f（1・3階からの枝）。売場の中身・行き方TBD、画像生成blocked。 |
| F86 | `F86` | 香林坊 | デパート4階（隠し階・条件つき。ラスボス付近で解放。強い何かが手に入る）。door-lower↔E15.door-4f、door-upper↔E16.door-4f。売場の中身・強い何かの中身・行き方TBD、画像生成blocked。 |
| F84 | `F84` | 能登（被災前） | 廃校の校庭（被災前）。F18の被災前版。left←E29.right（茂みの小径の暫定入口）、right→E32.left。校庭の見た目・茂みの見せ方・勝手口TBD、画像生成blocked。 |
