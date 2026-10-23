# フィールド画像台帳

## 運用

背景は**1画像1行**で管理する。生成前に各行へ、**一言特徴（この一枚は何の場所か）**、時期・景色（時代／場所／天候／生活の汚れ）・必須接続・禁止辺・通行不能物・車椅子の通行条件・任意枝の有無・**TBD**を埋める。対象画像が描く内容に関わるTBDがあれば生成を `blocked` とする。生成前の入力契約審査と、画像・mask・links・実機確認後の採用readyを別の段階として記録する。

全画像の共通条件は、現代の K県、冬、手作りジオラマ、真上寄り、人物・文字なし。昭和から残る建物や設備は存在してよいが、時代設定を昭和に戻さない。汚れは雪国の日常（融雪水、砂、泥、塩の白残り、黒ずんだ木、錆）であり、廃墟でない場所を廃墟化しない。

寺町では、[map-topology.md の「寺町の地形不変条件」](map-topology.md) が最優先である。河岸段丘の犀川側＝県営住宅、そこへは石段（立てる時期のみ）と車椅子用スロープ（生活経路）が別にある。段丘の反対側＝小学校で、長い通学坂は車椅子で通れる。この関係を壊すMAPは `blocked` とする。

`ready` は全項目が記入済みかつ TBD=なし、`legacy` は既存の旧画像で、採用・生成根拠にならない旧素材の記録（新運用では、新しい画像は正本パスへ上書き保存し、不採用は消す。寺町以外の現存legacy画像20件の旧画像は、上書きで置き換えるまで現存画像の記録として残り、置き換えた時点でstatusを更新する。**legacy statusの廃止可否は要確認、kako-jun判断待ち**）、`blocked` は個別契約またはTBDが残っている状態である。寺町は2026-10-16の方針により、旧legacyを一枚も採用せず、TRM-02〜TRM-16の新候補15枚（旧TRM-01は2026-10-23にTRM-03へ統合して廃止）を揃えて監査後に**一括**でruntimeへ差し替える。混在運用はしない。**「ただの道」「つなぎ」だけは一言特徴にならない**。道なら、交差点・橋・用水・寺の裏門・雪囲い・市場の角・坂の眺めなど、そこでしか成立しない主役を必ず持たせる。

## 129行共通の画像契約

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

新規つなぎの絵11枚の詳細な接続契約は [map-specifications.md](map-specifications.md) と [map-topology.md](map-topology.md) にある。旧IDとの対応は [対応表](production/20261019-map-id-renumber.json)。ここでの `blocked` はトポロジー未決を意味しない。画像ごとの現地参照・既存画像端・歩行マスクを照合するまで生成を保留する状態である。

| ID | 画像 | 状態 | 一言特徴 | 時期 | 必須接続 | TBD |
|---|---|---|---|---|
| KRB-07 | `kanazawa-saigawa-bridge` | blocked | 雪と融雪水を抱えた犀川の鉄橋 | 幼稚園前半 | 茶屋街南岸 → 犀川橋 → 香林坊北岸 | 橋の実在形状・既存KRB-01/KRB-08端を参照してマスク照合 |
| TRM-17 | `teramachi-entry-slope` | blocked | 用水と黒瓦を見上げる寺町の坂 | 幼稚園前半 | コンビニ北 → 寺町connector南 | 既存TRM-16/KRB-10端を参照してマスク照合 |
| UCH-03 | `uchinada-pine-dune-path` | blocked | 風に鳴るクロマツ防砂林の木道 | 中学生後半 | 内灘駅 → 砂丘頂 → 砂浜 | 実在木道の幅・既存UCH-02/UCH-05端を参照してマスク照合 |
| NTB-02 | `noto-uphill` | blocked | 海を背にして上がる雪混じりの漁村坂 | 幼稚園後半 | 低地 → 尾根 | 被災前後の同一端をマスク照合 |
| NTB-03 | `noto-ridge` | blocked | 海を下に見下ろす小さな神社の尾根 | 幼稚園後半 | NTB-02 → NTB-04 | 被災前後の同一端をマスク照合 |
| NTB-04 | `noto-downhill` | blocked | 船揚げ場の屋根へ降りる急な集落坂 | 幼稚園後半 | 尾根 → 実家低地 | 被災前後の同一端をマスク照合 |
| UTS-01 | `utatsuyama-trailhead-slope` | blocked | 浅野川東岸の寺門と杉林の登り口 | 小学生前半 | 武蔵ヶ辻 → 浅野川橋 → 山中腹 | 東岸橋・既存UTS-02端を参照してマスク照合 |
| KRB-12 | `hirosaka-slope` | blocked | 松と石垣の間で二手に分かれる広坂 | 壮年編 | 香林坊 → 兼六園／病院側 | 封鎖用柵の差分・既存KRB-01/KRB-13端を照合 |
| SCH-01 | `teramachi-school-slope` | blocked | 雪の手すりを伝う校門前の長い坂 | 中学生前半 | slope-top → 校門 | 既存TRM-14/SCH-02の校門位置をマスク照合 |
| KRB-11 | `musashigatsuji-crossing` | blocked | バス屋根と市場アーケードが交わる武蔵ヶ辻 | 幼稚園前半〜再訪 | 香林坊 → 金沢駅／浅野川橋側 | 既存KRB-01/STN-01・UTS-01端をマスク照合 |
| UCH-01 | `uchinada-line-interior` | blocked | 結露した窓と赤い座席の内灘線車内 | 中学生後半 | 金沢駅乗車 → 車内通路 → 内灘駅降車 | 実車扉幅と車椅子回転域を参照してマスク照合 |

## 既存画像（個別契約を逆算して追記する対象）

旧TRM-01（園庭）の legacy 画像（`legacy/TRM-01.webp` とそのmask）は、2026-10-23にTRM-03へ統合して廃止したMAPの没素材として削除済み（kako-jun 決定、#51。履歴はgit）。台帳の行は持たない。

| ID | 画像 | 地区 | 状態 |
|---|---|---|---|
| TRM-16 | `assets/images/fields/legacy/TRM-16.webp` | 寺町 | retired-replacement-required |
| TRM-15 | `assets/images/fields/legacy/TRM-15.webp` | 寺町 | retired-replacement-required |
| TRM-07 | `assets/images/fields/legacy/TRM-07.webp` | 寺町 | retired-replacement-required |
| TRM-08 | `assets/images/fields/legacy/TRM-08.webp` | 寺町 | retired-replacement-required |
| TRM-09 | `assets/images/fields/legacy/TRM-09.webp` | 寺町 | retired-replacement-required |
| TRM-10 | `assets/images/fields/legacy/TRM-10.webp` | 寺町 | retired-replacement-required |
| TRM-11 | `assets/images/fields/legacy/TRM-11.webp` | 寺町 | retired-replacement-required |
| TRM-13 | `assets/images/fields/legacy/TRM-13.webp` | 寺町 | retired-replacement-required |
| TRM-06 | `assets/images/fields/legacy/TRM-06.webp` | 寺町 | retired-replacement-required |
| TRM-03 | `assets/images/fields/legacy/TRM-03.webp` | 寺町 | retired-replacement-required |
| TRM-05 | `assets/images/fields/legacy/TRM-05.webp` | 寺町 | retired-replacement-required |
| TRM-14 | `assets/images/fields/legacy/TRM-14.webp` | 寺町 | retired-replacement-required |
| KRB-01 | `assets/images/fields/legacy/KRB-01.webp` | 香林坊 | legacy |
| KRB-04 | `assets/images/fields/legacy/KRB-04.webp` | 香林坊 | legacy |
| KRB-06 | `assets/images/fields/legacy/KRB-06.webp` | 香林坊 | legacy |
| KRB-08 | `assets/images/fields/legacy/KRB-08.webp` | 茶屋街 | legacy |
| KRB-09 | `assets/images/fields/legacy/KRB-09.webp` | 茶屋街 | legacy |
| KRB-10 | `assets/images/fields/legacy/KRB-10.webp` | 戻り道 | legacy |
| KRB-13 | `assets/images/fields/legacy/KRB-13.webp` | 病院 | legacy |
| STN-01 | `assets/images/fields/legacy/STN-01.webp` | 金沢駅 | legacy |
| UTS-02 | `assets/images/fields/legacy/UTS-02.webp` | 卯辰山 | legacy |
| SNL-06 | `assets/images/fields/legacy/SNL-06.webp` | サニーランド | 小さな屋外空間・巨大シャチホコ。水族館出口→屋外動物園。ラッコ館・海底洞窟の入口出口。M008戦は屋外、噴水と断定しない。 door-aquarium→SNL-05.door-outdoor、door-zoo→SNL-09.door-hub、door-otter-in→SNL-07.door-entry、door-otter-out→SNL-07.door-exit、door-cave-in→SNL-08.door-entry、door-cave-out→SNL-08.door-exit。旧画像は参照専用。pixel/mask/幅TBD |
| SNL-05 | `assets/images/fields/legacy/SNL-05.webp` | サニーランド | 格子状水槽の地下水族館。出口付近にピラルク巨大水槽。壁際にサメ標本・クジラの陰茎標本。展示格子と通行交点は別。 door-corridor→SNL-04.door-aquarium、door-outdoor→SNL-06.door-aquarium。旧画像は参照専用。pixel/mask/幅TBD |
| SNL-03 | `assets/images/fields/legacy/SNL-03.webp` | サニーランド | 下り渡り廊下途中・右側のゲームセンター。右は下降時の進行基準。SNL-02前半への割当はゲーム配置。 door-corridor→SNL-02.door-arcade-right。旧画像は参照専用。pixel/mask/幅TBD |
| UCH-02 | `assets/images/fields/legacy/UCH-02.webp` | 内灘 | legacy |
| UCH-05 | `assets/images/fields/legacy/UCH-05.webp` | 内灘 | legacy |
| NTR-01 | `assets/images/fields/legacy/NTR-01.webp` | 奥能登（被災前） | legacy |
| NTB-01 | `assets/images/fields/legacy/NTB-01.webp` | 奥能登（被災前） | legacy |
| NTB-05 | `assets/images/fields/legacy/NTB-05.webp` | 奥能登（被災前） | legacy |
| NTB-06 | `assets/images/fields/legacy/NTB-06.webp` | 奥能登（被災前） | legacy |
| NTB-08 | `assets/images/fields/legacy/NTB-08.webp` | 奥能登（被災前） | legacy |
| SCH-02 | `assets/images/fields/legacy/SCH-02.webp` | 小学校 | legacy |

旧版・不採用候補（`-v2` 以外の旧版、寺町の地蔵版、蛸島以外の小木駅版、駅前 v1/v2、サニーランド v2）は参照専用であり、マップの契約対象に数えない。

## 個別仕様済みの将来枠（全て `blocked`：生成前の参照・マスク照合待ち）

全行の一言特徴・方位・主路・通行条件は [map-specifications.md](map-specifications.md) に確定済み。下表の「未決のため必要な個別契約」は旧見出しであり、以降の各記述は参照・マスク照合項目として読む。

| ID | 画像 | 地区 | 未決のため必要な個別契約 |
|---|---|---|---|
| TRM-04 | `teramachi-main-hall-interior` | 寺町 | ドア接続・時期・室内通路 |
| TRM-02 | `teramachi-kindergarten-hall` | 寺町 | ドア接続・舞台と通路 |
| TRM-12 | `teramachi-danchi-interior` | 寺町 | ドア接続・車椅子動線 |
| UTS-03 | `utatsuyama-route-02` | 卯辰山 | 接続辺・中ボスまでの主経路 |
| UTS-04 | `utatsuyama-route-03` | 卯辰山 | 接続辺・中ボスまでの主経路 |
| UTS-05 | `utatsuyama-summon-clearing` | 卯辰山 | 接続辺・戦闘場の通行条件 |
| SNL-01 | `SNL-01` | サニーランド | 八角形エントランス1階・受付。八角形ホールの一辺から1階へ。受付横に階段と長い廊下への一辺。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| SNL-02 | `SNL-02` | サニーランド | 雪の森に囲まれた下り渡り廊下・前半。全2MAPの下り廊下、雪の森。途中の下降時右へゲームセンター（前半割当はゲーム配置）。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| SNL-04 | `SNL-04` | サニーランド | 雪の森に囲まれた下り渡り廊下・後半。長い下り廊下後半から地下水族館へ。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| SNL-09 | `SNL-09` | サニーランド | 狭い格子状の昭和の屋外動物園。格子状の狭い劣悪な昭和の屋外檻。動物種・交点の通行はTBD。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| UCH-04 | `uchinada-dune-summit` | 内灘 | UCH-03・砂浜との接続、車椅子経路 |
| NTA-01 | `noto-post-station` | 奥能登（被災後） | 被災前版との同一接続 |
| NTA-02 | `noto-post-uphill` | 奥能登（被災後） | NTB-02との同一接続 |
| NTA-03 | `noto-post-ridge` | 奥能登（被災後） | NTB-03との同一接続 |
| NTA-04 | `noto-post-downhill` | 奥能登（被災後） | NTB-04との同一接続 |
| NTA-05 | `noto-post-house` | 奥能登（被災後） | 実家版との同一接続 |
| NTA-06 | `noto-post-fishing-spot` | 奥能登（被災後） | 釣り場版との同一接続 |
| NTA-07 | `noto-temporary-housing` | 奥能登（被災後） | 接続辺・生活動線（入口はNTA-01.right。被災前NTB-01.right→NTB-07.leftの被災後版。#89） |
| BDY-01 | `BDY-01` | 抽象体内 | 口・体内入口。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・脳内迷路はTBD、mask作成済み（assets/images/fields/masks/BDY-01-mask.webp。2026-10-23）・第2回red-team済み（mask可。ready は遷移の範囲値・runtime扱いのTBD待ち。BDY-13 の寸法例外・BDY-02 の首の逸脱は kako-jun 承認済み 2026-10-23）・status は blocked 維持。 【BDY-01 基準状態の画像採用済み（reference。mask作成済み・links作成済み・第2回red-team済み（mask可。ready は遷移の範囲値・runtime扱いのTBD待ち。BDY-13 の寸法例外・BDY-02 の首の逸脱は kako-jun 承認済み 2026-10-23）・runtime切替なし。kako-jun 2026-10-22。`assets/images/fields/reference/body-mouth-bdy01-adopted.webp`、[採用記録](production/20261022-body-maps-adoption.md)）】 |
| BDY-06 | `BDY-06` | 抽象体内 | 左手通路2・末端。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・脳内迷路はTBD、mask作成済み（assets/images/fields/masks/BDY-06-mask.webp。2026-10-23）・第2回red-team済み（mask可。ready は遷移の範囲値・runtime扱いのTBD待ち。BDY-13 の寸法例外・BDY-02 の首の逸脱は kako-jun 承認済み 2026-10-23）・status は blocked 維持。 【BDY-06 基準状態の画像採用済み（reference。mask作成済み・links作成済み・第2回red-team済み（mask可。ready は遷移の範囲値・runtime扱いのTBD待ち。BDY-13 の寸法例外・BDY-02 の首の逸脱は kako-jun 承認済み 2026-10-23）・runtime切替なし。kako-jun 2026-10-22。`assets/images/fields/reference/body-left-arm-2-bdy06-adopted.webp`、[採用記録](production/20261022-body-maps-adoption.md)）】 |
| BDY-08 | `BDY-08` | 抽象体内 | 右手通路2・末端。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・脳内迷路はTBD、mask作成済み（assets/images/fields/masks/BDY-08-mask.webp。2026-10-23）・第2回red-team済み（mask可。ready は遷移の範囲値・runtime扱いのTBD待ち。BDY-13 の寸法例外・BDY-02 の首の逸脱は kako-jun 承認済み 2026-10-23）・status は blocked 維持。 【BDY-08 基準状態の画像採用済み（reference。mask作成済み・links作成済み・第2回red-team済み（mask可。ready は遷移の範囲値・runtime扱いのTBD待ち。BDY-13 の寸法例外・BDY-02 の首の逸脱は kako-jun 承認済み 2026-10-23）・runtime切替なし。kako-jun 2026-10-22。`assets/images/fields/reference/body-right-arm-2-bdy08-adopted.webp`、[採用記録](production/20261022-body-maps-adoption.md)）】 |
| BDY-11 | `BDY-11` | 抽象体内 | 左足通路3・末端。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・脳内迷路はTBD、mask作成済み（assets/images/fields/masks/BDY-11-mask.webp。2026-10-23）・第2回red-team済み（mask可。ready は遷移の範囲値・runtime扱いのTBD待ち。BDY-13 の寸法例外・BDY-02 の首の逸脱は kako-jun 承認済み 2026-10-23）・status は blocked 維持。 【BDY-11 基準状態の画像採用済み（reference。mask作成済み・links作成済み・第2回red-team済み（mask可。ready は遷移の範囲値・runtime扱いのTBD待ち。BDY-13 の寸法例外・BDY-02 の首の逸脱は kako-jun 承認済み 2026-10-23）・runtime切替なし。kako-jun 2026-10-22。`assets/images/fields/reference/body-left-leg-3-bdy11-adopted.webp`、[採用記録](production/20261022-body-maps-adoption.md)）】 |
| BDY-14 | `BDY-14` | 抽象体内 | 右足通路3・末端。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・脳内迷路はTBD、mask作成済み（assets/images/fields/masks/BDY-14-mask.webp。2026-10-23）・第2回red-team済み（mask可。ready は遷移の範囲値・runtime扱いのTBD待ち。BDY-13 の寸法例外・BDY-02 の首の逸脱は kako-jun 承認済み 2026-10-23）・status は blocked 維持。 【BDY-14 基準状態の画像採用済み（reference。mask作成済み・links作成済み・第2回red-team済み（mask可。ready は遷移の範囲値・runtime扱いのTBD待ち。BDY-13 の寸法例外・BDY-02 の首の逸脱は kako-jun 承認済み 2026-10-23）・runtime切替なし。kako-jun 2026-10-22。`assets/images/fields/reference/body-right-leg-3-bdy14-adopted.webp`、[採用記録](production/20261022-body-maps-adoption.md)）】 |
| BDY-04 | `BDY-04` | 抽象体内 | 頭・脳の迷路通路。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。迷路状の通路。通路幅はキャラクター1人分（約77px。模型の天面比0.047）、入口は南辺中央1本、行き止まりの迷路（出口なし）。形の詳細（座標・格子）は verification/body-layout の割付図が正本。pixel/maskはmask作成済み（assets/images/fields/masks/BDY-04-mask.webp。2026-10-23）・第2回red-team済み（mask可。ready は遷移の範囲値・runtime扱いのTBD待ち。BDY-13 の寸法例外・BDY-02 の首の逸脱は kako-jun 承認済み 2026-10-23）・status は blocked 維持。 【BDY-04 基準状態の画像採用済み（reference。mask作成済み・links作成済み・第2回red-team済み（mask可。ready は遷移の範囲値・runtime扱いのTBD待ち。BDY-13 の寸法例外・BDY-02 の首の逸脱は kako-jun 承認済み 2026-10-23）・runtime切替なし。kako-jun 2026-10-22。`assets/images/fields/reference/body-brain-maze-bdy04-adopted.webp`、[採用記録](production/20261022-body-maps-adoption.md)）】 |
| BDY-15 | `BDY-15` | 抽象体内 | 胃・分岐室。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。分岐なしJ字の1袋（入口は西辺230px→ドーム=胃底→胃体最大460px→幽門130pxで丸く閉じる）。形の詳細（座標・格子）は verification/body-layout の割付図が正本。pixel/maskはmask作成済み（assets/images/fields/masks/BDY-15-mask.webp。2026-10-23）・第2回red-team済み（mask可。ready は遷移の範囲値・runtime扱いのTBD待ち。BDY-13 の寸法例外・BDY-02 の首の逸脱は kako-jun 承認済み 2026-10-23）・status は blocked 維持。 【BDY-15 基準状態の画像採用済み（reference。mask作成済み・links作成済み・第2回red-team済み（mask可。ready は遷移の範囲値・runtime扱いのTBD待ち。BDY-13 の寸法例外・BDY-02 の首の逸脱は kako-jun 承認済み 2026-10-23）・runtime切替なし。kako-jun 2026-10-22。`assets/images/fields/reference/body-stomach-bdy15-adopted.webp`、[採用記録](production/20261022-body-maps-adoption.md)）】 |
| BDY-16 | `BDY-16` | 抽象体内 | 心臓・分岐室。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。丸い4部屋（右心房=画面左上・右心室=左下・左心房=右上・左心室=右下。左右は本人から見る）を四角い環の通路でつなぐ。入口は北辺。形の詳細（座標・格子）は verification/body-layout の割付図が正本。pixel/maskはmask作成済み（assets/images/fields/masks/BDY-16-mask.webp。2026-10-23）・第2回red-team済み（mask可。ready は遷移の範囲値・runtime扱いのTBD待ち。BDY-13 の寸法例外・BDY-02 の首の逸脱は kako-jun 承認済み 2026-10-23）・status は blocked 維持。 【BDY-16 基準状態の画像採用済み（reference。mask作成済み・links作成済み・第2回red-team済み（mask可。ready は遷移の範囲値・runtime扱いのTBD待ち。BDY-13 の寸法例外・BDY-02 の首の逸脱は kako-jun 承認済み 2026-10-23）・runtime切替なし。kako-jun 2026-10-22。`assets/images/fields/reference/body-heart-bdy16-adopted.webp`、[採用記録](production/20261022-body-maps-adoption.md)）】 |
| OVS-01 | `overseas-airport` | 海外 | 到着口・荒れ地への接続 |
| OVS-02 | `overseas-wasteland-a` | 海外 | 空港・荒れ地Bへの接続 |
| OVS-03 | `overseas-wasteland-b` | 海外 | 荒れ地A・都市への接続 |
| OVS-04 | `OVS-04` | 海外3塔 | 攻略双塔の共通基壇。左右塔は5階建て、雑多な増改築・無駄道・袋小路。左右対称・同一階平面反復を避ける。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| OVS-05 | `OVS-05` | 海外3塔 | 左塔1階・雑居入口。左右塔は5階建て、雑多な増改築・無駄道・袋小路。左右対称・同一階平面反復を避ける。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| OVS-07 | `OVS-07` | 海外3塔 | 左塔3階・配管と混在用途。左右塔は5階建て、雑多な増改築・無駄道・袋小路。左右対称・同一階平面反復を避ける。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| OVS-09 | `OVS-09` | 海外3塔 | 左塔5階・M015魔法のみ有効。左右塔は5階建て、雑多な増改築・無駄道・袋小路。左右対称・同一階平面反復を避ける。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| OVS-10 | `OVS-10` | 海外3塔 | 右塔1階・雑居入口。左右塔は5階建て、雑多な増改築・無駄道・袋小路。左右対称・同一階平面反復を避ける。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| OVS-12 | `OVS-12` | 海外3塔 | 右塔3階・増改築の交差路。左右塔は5階建て、雑多な増改築・無駄道・袋小路。左右対称・同一階平面反復を避ける。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| OVS-14 | `OVS-14` | 海外3塔 | 右塔5階・M016アビリティのみ有効。左右塔は5階建て、雑多な増改築・無駄道・袋小路。左右対称・同一階平面反復を避ける。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| OVS-15 | `OVS-15` | 海外3塔 | 塔間空中通路・シャー判明と雑魚共闘。左右塔は5階建て、雑多な増改築・無駄道・袋小路。左右対称・同一階平面反復を避ける。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| OVS-20 | `OVS-20` | 海外3塔 | 脱出第3塔1階・出口直前S005戦。5階建て第3塔の下降。各階は攻略塔同程度の面積。宝箱取捨選択、タイマー継続。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| APT-01 | `k-airport-exterior` | K空港 | 広場・搭乗口への接続 |
| APT-02 | `k-airport-interior` | K空港 | ドア接続・搭乗動線 |
| GRD-01 | `kenrokuen-1` | 兼六園 | 真弓坂側の南西入口・v2接続、幅／高低差／通行条件TBD（blocked） |
| GRD-02 | `kenrokuen-2` | 兼六園 | 時雨亭・長谷池・v2接続、幅／高低差／通行条件TBD（blocked） |
| GRD-03 | `kenrokuen-3` | 兼六園 | 瓢池・夕顔亭・翠滝下段・v2接続、幅／高低差／通行条件TBD（blocked） |
| GRD-04 | `kenrokuen-4` | 兼六園 | 霞ヶ池西岸・栄螺山・v2接続、幅／高低差／通行条件TBD（blocked） |
| GRD-05 | `kenrokuen-5` | 兼六園 | 霞ヶ池北岸・ことじ灯籠・v2接続、幅／高低差／通行条件TBD（blocked） |
| GRD-06 | `kenrokuen-6` | 兼六園 | 霞ヶ池東岸・唐崎松・v2接続、幅／高低差／通行条件TBD（blocked） |
| GRD-07 | `kenrokuen-7` | 兼六園 | 曲水・根上松・v2接続、幅／高低差／通行条件TBD（blocked） |
| GRD-08 | `kenrokuen-8` | 兼六園 | 山崎山・花見橋側・v2接続、幅／高低差／通行条件TBD（blocked） |
| GRD-09 | `kenrokuen-9` | 兼六園 | 梅林側の南周回路・v2接続、幅／高低差／通行条件TBD（blocked） |
| GRD-10 | `kenrokuen-10` | 兼六園 | 桂坂口・石川橋・v2接続、幅／高低差／通行条件TBD（blocked） |
| CST-01 | `castle-1` | 金沢城 | 石川門の枡形・v2接続、幅／高低差／通行条件TBD（blocked） |
| CST-02 | `castle-2` | 金沢城 | 三の丸・v2接続、幅／高低差／通行条件TBD（blocked） |
| CST-03 | `castle-3` | 金沢城 | 菱櫓・五十間長屋・v2接続、幅／高低差／通行条件TBD（blocked） |
| CST-04 | `castle-4` | 金沢城 | 橋爪門・橋爪門続櫓・v2接続、幅／高低差／通行条件TBD（blocked） |
| CST-05 | `castle-5` | 金沢城 | 二の丸・v2接続、幅／高低差／通行条件TBD（blocked） |
| CST-06 | `castle-6` | 金沢城 | 低地の玉泉院丸庭園・v2接続、幅／高低差／通行条件TBD（blocked） |
| CST-07 | `castle-7` | 金沢城 | 極楽橋・本丸附段・三十間長屋側・v2接続、幅／高低差／通行条件TBD（blocked） |
| CST-08 | `castle-8` | 金沢城 | 鶴の丸・東の丸側・v2接続、幅／高低差／通行条件TBD（blocked） |
| CST-09 | `castle-9` | 金沢城 | 高い本丸・v2接続、幅／高低差／通行条件TBD（blocked） |
| CST-10 | `castle-10` | 金沢城 | 本丸内のイマジナリー天守上層・v2接続、幅／高低差／通行条件TBD（blocked） |

## 2026-10-18追加ID

| ID | 管理名 | 地区 | 契約 |
|---|---|---|---|
| SNL-12 | `SNL-12` | サニーランド | 八角形エントランス2階・全方向の窓。2階は全方向の窓。一辺から和室宿泊棟、階段で1階。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| SNL-11 | `SNL-11` | サニーランド | 廃墟の和室が並ぶ宿泊棟。廃墟の和室が並ぶ。入口2階側と屋外階段側の両端。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| SNL-10 | `SNL-10` | サニーランド | 動物園から宿泊棟端への屋外階段。ユーザー創作の動物園→宿泊棟端の屋外階段。assist方法TBD。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| SNL-07 | `SNL-07` | サニーランド | ラッコ館・入口と出口のある任意探索。入口・出口別。宝箱目当ての任意通り抜け。同じ屋外SNL-06へ戻すのはゲーム配置。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| SNL-08 | `SNL-08` | サニーランド | 低予算昭和の海底探検洞窟・任意探索。低予算昭和の海底探検の作り物。ダイオウイカ・難破船・ニンゲン。入口出口別、任意宝箱。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| OVS-06 | `OVS-06` | 海外3塔 | 左塔2階・迷路状の増築。左右塔は5階建て、雑多な増改築・無駄道・袋小路。左右対称・同一階平面反復を避ける。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| OVS-08 | `OVS-08` | 海外3塔 | 左塔4階・無駄道と袋小路。左右塔は5階建て、雑多な増改築・無駄道・袋小路。左右対称・同一階平面反復を避ける。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| OVS-11 | `OVS-11` | 海外3塔 | 右塔2階・混在用途の迷路。左右塔は5階建て、雑多な増改築・無駄道・袋小路。左右対称・同一階平面反復を避ける。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| OVS-13 | `OVS-13` | 海外3塔 | 右塔4階・無駄道と袋小路。左右塔は5階建て、雑多な増改築・無駄道・袋小路。左右対称・同一階平面反復を避ける。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| OVS-16 | `OVS-16` | 海外3塔 | 脱出第3塔5階・宝箱と下り階段。5階建て第3塔の下降。各階は攻略塔同程度の面積。宝箱取捨選択、タイマー継続。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| OVS-17 | `OVS-17` | 海外3塔 | 脱出第3塔4階・宝箱と下り階段。5階建て第3塔の下降。各階は攻略塔同程度の面積。宝箱取捨選択、タイマー継続。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| OVS-18 | `OVS-18` | 海外3塔 | 脱出第3塔3階・宝箱と下り階段。5階建て第3塔の下降。各階は攻略塔同程度の面積。宝箱取捨選択、タイマー継続。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| OVS-19 | `OVS-19` | 海外3塔 | 脱出第3塔2階・宝箱と下り階段。5階建て第3塔の下降。各階は攻略塔同程度の面積。宝箱取捨選択、タイマー継続。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |

## #74追加ID（胴体・肺）

| ID | 管理名 | 地区 | 契約 |
|---|---|---|---|
| BDY-02 | `BDY-02` | 抽象体内 | 上半身・胴体上段。7経路は模型（ジオラマ）の縁の辺で隣MAPへ遷移し（遷移位置は辺上の範囲指定、範囲値TBD。土台の板と机は見えたまま）、方位は `docs/topology/body.svg` に従う（口=北東、頭=北、左腕=北東（東辺から出る）、右腕=北西（西辺から出る）、下半身=南、心臓=南東、肺=南西。**左右は身体の本人から見る（本人は仰向け、それを正面から見る構図なので、画面左が本人の右手・右足、画面右が本人の左手・左足。kako-jun 2026-10-22、#142）**。左足・左手は画面右、右足・右手は画面左。心臓は画面右（南東）、肺は画面左（南西）。南辺は 肺=左寄り・下半身=中央・心臓=右寄り）。口から胴体への首道は1本、頭道はそこから分岐。体外形・洞窟口は描かず、平面床と低い仕切りで道を作る。心臓・肺の部屋と胃は描かない（胃はBDY-03からBDY-15へ接続）。架空人体・非写実・肌色寄り・非グロ、主路幅はキャラクター3人分程度。体内材料は `art-direction.md`／`map-specifications.md` を参照。 【BDY-02 新版（首1本・左右は本人から見る）の基準状態の画像採用済み（reference。mask作成済み・links作成済み・第2回red-team済み（mask可。ready は遷移の範囲値・runtime扱いのTBD待ち。BDY-13 の寸法例外・BDY-02 の首の逸脱は kako-jun 承認済み 2026-10-23）・runtime切替なし。kako-jun 2026-10-22。`assets/images/fields/reference/body-upper-torso-bdy02-adopted.webp`、[採用記録](production/20261022-bdy02-adoption.md)）】 【BDY-02 承認済みの逸脱 2026-10-23】首の狭まりがない旧版画像を kako-jun が承認済みの逸脱として採用。契約の首1本・分岐は画像では広い床の塊として現れる（マスクは変更不要。画像が正）。 |
| BDY-17 | `BDY-17` | 抽象体内 | 肺・分岐室。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。丸い5部屋（右肺3葉=画面左・左肺2葉=画面右）を外周の環で結ぶ。入口は北辺中央、通路幅はキャラクター1人分、行き止まりなし。形の詳細（座標・格子）は verification/body-layout の割付図が正本。pixel/maskはmask作成済み（assets/images/fields/masks/BDY-17-mask.webp。2026-10-23）・第2回red-team済み（mask可。ready は遷移の範囲値・runtime扱いのTBD待ち。BDY-13 の寸法例外・BDY-02 の首の逸脱は kako-jun 承認済み 2026-10-23）・status は blocked 維持。 【BDY-17 基準状態の画像採用済み（reference。mask作成済み・links作成済み・第2回red-team済み（mask可。ready は遷移の範囲値・runtime扱いのTBD待ち。BDY-13 の寸法例外・BDY-02 の首の逸脱は kako-jun 承認済み 2026-10-23）・runtime切替なし。kako-jun 2026-10-22。`assets/images/fields/reference/body-lungs-bdy17-adopted.webp`、[採用記録](production/20261022-body-maps-adoption.md)）】 |

## #74追加ボリューム（上半身・下半身／手2／足3）

| ID | 管理名 | 地区 | 契約 |
|---|---|---|---|
| BDY-03 | `BDY-03` | 抽象体内 | 下半身・胴体下段。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・脳内迷路はTBD、mask作成済み（assets/images/fields/masks/BDY-03-mask.webp。2026-10-23）・第2回red-team済み（mask可。ready は遷移の範囲値・runtime扱いのTBD待ち。BDY-13 の寸法例外・BDY-02 の首の逸脱は kako-jun 承認済み 2026-10-23）・status は blocked 維持。 【BDY-03 基準状態の画像採用済み（reference。mask作成済み・links作成済み・第2回red-team済み（mask可。ready は遷移の範囲値・runtime扱いのTBD待ち。BDY-13 の寸法例外・BDY-02 の首の逸脱は kako-jun 承認済み 2026-10-23）・runtime切替なし。kako-jun 2026-10-22。`assets/images/fields/reference/body-lower-torso-bdy03-adopted.webp`、[採用記録](production/20261022-body-maps-adoption.md)）】 |
| BDY-05 | `BDY-05` | 抽象体内 | 左手通路1・付け根側。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・脳内迷路はTBD、mask作成済み（assets/images/fields/masks/BDY-05-mask.webp。2026-10-23）・第2回red-team済み（mask可。ready は遷移の範囲値・runtime扱いのTBD待ち。BDY-13 の寸法例外・BDY-02 の首の逸脱は kako-jun 承認済み 2026-10-23）・status は blocked 維持。 【BDY-05 基準状態の画像採用済み（reference。mask作成済み・links作成済み・第2回red-team済み（mask可。ready は遷移の範囲値・runtime扱いのTBD待ち。BDY-13 の寸法例外・BDY-02 の首の逸脱は kako-jun 承認済み 2026-10-23）・runtime切替なし。kako-jun 2026-10-22。`assets/images/fields/reference/body-left-arm-1-bdy05-adopted.webp`、[採用記録](production/20261022-body-maps-adoption.md)）】 |
| BDY-07 | `BDY-07` | 抽象体内 | 右手通路1・付け根側。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・脳内迷路はTBD、mask作成済み（assets/images/fields/masks/BDY-07-mask.webp。2026-10-23）・第2回red-team済み（mask可。ready は遷移の範囲値・runtime扱いのTBD待ち。BDY-13 の寸法例外・BDY-02 の首の逸脱は kako-jun 承認済み 2026-10-23）・status は blocked 維持。 【BDY-07 基準状態の画像採用済み（reference。mask作成済み・links作成済み・第2回red-team済み（mask可。ready は遷移の範囲値・runtime扱いのTBD待ち。BDY-13 の寸法例外・BDY-02 の首の逸脱は kako-jun 承認済み 2026-10-23）・runtime切替なし。kako-jun 2026-10-22。`assets/images/fields/reference/body-right-arm-1-bdy07-adopted.webp`、[採用記録](production/20261022-body-maps-adoption.md)）】 |
| BDY-09 | `BDY-09` | 抽象体内 | 左足通路1・付け根側。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・脳内迷路はTBD、mask作成済み（assets/images/fields/masks/BDY-09-mask.webp。2026-10-23）・第2回red-team済み（mask可。ready は遷移の範囲値・runtime扱いのTBD待ち。BDY-13 の寸法例外・BDY-02 の首の逸脱は kako-jun 承認済み 2026-10-23）・status は blocked 維持。 【BDY-09 基準状態の画像採用済み（reference。mask作成済み・links作成済み・第2回red-team済み（mask可。ready は遷移の範囲値・runtime扱いのTBD待ち。BDY-13 の寸法例外・BDY-02 の首の逸脱は kako-jun 承認済み 2026-10-23）・runtime切替なし。kako-jun 2026-10-22。`assets/images/fields/reference/body-left-leg-1-bdy09-adopted.webp`、[採用記録](production/20261022-body-maps-adoption.md)）】 |
| BDY-10 | `BDY-10` | 抽象体内 | 左足通路2・中間。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・脳内迷路はTBD、mask作成済み（assets/images/fields/masks/BDY-10-mask.webp。2026-10-23）・第2回red-team済み（mask可。ready は遷移の範囲値・runtime扱いのTBD待ち。BDY-13 の寸法例外・BDY-02 の首の逸脱は kako-jun 承認済み 2026-10-23）・status は blocked 維持。 【BDY-10 基準状態の画像採用済み（reference。mask作成済み・links作成済み・第2回red-team済み（mask可。ready は遷移の範囲値・runtime扱いのTBD待ち。BDY-13 の寸法例外・BDY-02 の首の逸脱は kako-jun 承認済み 2026-10-23）・runtime切替なし。kako-jun 2026-10-22。`assets/images/fields/reference/body-left-leg-2-bdy10-adopted.webp`、[採用記録](production/20261022-body-maps-adoption.md)）】 |
| BDY-12 | `BDY-12` | 抽象体内 | 右足通路1・付け根側。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・脳内迷路はTBD、mask作成済み（assets/images/fields/masks/BDY-12-mask.webp。2026-10-23）・第2回red-team済み（mask可。ready は遷移の範囲値・runtime扱いのTBD待ち。BDY-13 の寸法例外・BDY-02 の首の逸脱は kako-jun 承認済み 2026-10-23）・status は blocked 維持。 【BDY-12 基準状態の画像採用済み（reference。mask作成済み・links作成済み・第2回red-team済み（mask可。ready は遷移の範囲値・runtime扱いのTBD待ち。BDY-13 の寸法例外・BDY-02 の首の逸脱は kako-jun 承認済み 2026-10-23）・runtime切替なし。kako-jun 2026-10-22。`assets/images/fields/reference/body-right-leg-1-bdy12-adopted.webp`、[採用記録](production/20261022-body-maps-adoption.md)）】 |
| BDY-13 | `BDY-13` | 抽象体内 | 右足通路2・中間。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・脳内迷路はTBD、mask作成済み（assets/images/fields/masks/BDY-13-mask.webp。2026-10-23）・第2回red-team済み（mask可。ready は遷移の範囲値・runtime扱いのTBD待ち。BDY-13 の寸法例外・BDY-02 の首の逸脱は kako-jun 承認済み 2026-10-23）・status は blocked 維持。 【BDY-13 基準状態の画像採用済み（reference。mask作成済み・links作成済み・第2回red-team済み（mask可。ready は遷移の範囲値・runtime扱いのTBD待ち。BDY-13 の寸法例外・BDY-02 の首の逸脱は kako-jun 承認済み 2026-10-23）・runtime切替なし。kako-jun 2026-10-22。`assets/images/fields/reference/body-right-leg-2-bdy13-adopted.webp`、[採用記録](production/20261022-body-maps-adoption.md)）】 【BDY-13 承認 2026-10-23】寸法 1672x940 は kako-jun が例外承認（寸法ゲートは 1672x941。比率差0.1%）。 |

## #87/#89追加ID

| ID | 管理名 | 地区 | 契約 |
|---|---|---|---|
| KRB-02 | `KRB-02` | 香林坊 | デパート1階（入口階）。時計のある吹き抜け（アトリオ参照、出所 https://github.com/kako-jun/sit-by-me/issues/87#issuecomment-6258778050）。実在店に似せないジオラマ。door-street→KRB-01.door、door-elevator（階選択遷移）。階移動はエレベーターだけ（扉に入るとウィンドウで階を選ぶ。箱は独立MAPにしない）・売場の中身TBD、画像生成blocked。 |
| KRB-03 | `KRB-03` | 香林坊 | デパート2階（隠し階。https://github.com/kako-jun/sit-by-me/issues/87 2026-10-19の決定）。四角い吹き抜けの廊下だけのフロア（売場は無い）。中央の吹き抜けから下の1階が見える描画（侵入不可）。見える1階=KRB-02(同じ場所を2階から見下ろす視点で描く)。契約: KRB-02の背景を作るときはKRB-03の吹き抜け越しの絵と整合させる(KRB-02の吹き抜け・時計・床の見た目が共通の参照)。歩行域=廊下の環のみ、吹き抜け部分はblocked。実在店に似せないジオラマ。door-elevator（階選択遷移）。行き方は決定済み（エレベーターの扉→階選択ウィンドウ、B案）。画像生成blocked。 |
| KRB-05 | `KRB-05` | 香林坊 | デパート4階（隠し階・条件つき。最終章で兼六園へ向かう途中にデパートに寄り道すると、階選択で4階も選べるようになる(決定 2026-10-19)。最終章の兼六園への道（茶屋街→香林坊→広坂→兼六園）の途中の、香林坊のデパートに入ると階選択に4階が出る。専用イベントなし（デパートに入ること自体が条件。kako-jun決定 2026-10-19、#87）。強い何か=ものまね（FF5/6の隠しアビリティに相当。kako-jun決定 2026-10-19、#87）。魔法扱い（パーティ共通の共有ライブラリ。全員が使える）。4階の敵は「鏡」=映った自分たち自身（パーティの姿）で、ボス扱い。兼六園の最終救済には出ない（これまでのボスは兼六園でも雑魚敵として出さない）ので、ものまねはここでしか覚えられない。鏡の技「ものまね」を食らった味方が戦闘終了時に自動でラーニング（既存規則）。ものまねの効果=直前の味方の行動を、ノーコスト（MP・AP等の消費なし）で真似る。敵の行動は真似ない（回数・対象の選び方などの細部は未決）。要確認(#87): 鏡の敵の新規ID・映り込みの流用方法（鏡像・色味・何人映るか。味方の映り込みを流用できるならしたい。実現可否と作り方は要確認）・戦闘仕様）。door-elevator（階選択遷移。条件つき）。行き方は決定済み（エレベーターの扉→階選択ウィンドウ、B案。4階は最終章の兼六園途中の寄り道で選択肢に出る）。画像生成blocked。 |
| NTB-07 | `NTB-07` | 奥能登（被災前） | 廃校の校庭（被災前）。NTA-07の被災前版。left←NTB-01.right（茂みの小径の暫定入口）、right→NTB-08.left。校庭の見た目・茂みの見せ方・勝手口TBD、画像生成blocked。 |
