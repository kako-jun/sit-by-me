# MAP生成契約チェックリスト

2026-10-18: サニーランドは口述と創作の円環接続へ更新。旧pending6接続は削除済み。

`map-asset-registry.md` の130行を、生成可能にするまで追跡する行単位チェックリスト。接続の正本は `map-topology.md` の「MAP相互接続台帳 v2」、画面主役と主路は `map-specifications.md`、マスク形式は `sit-field-mask` である。全行は `blocked` または `legacy-needs-review` で始める。`TBD` が空でない限り `ready` にしない。台帳整合の独立再監査は [第3周レビュー](reviews/artifact-redteam/20261016-map-ledger-round3.md) を参照。

**注記**: ステータス名 `recreate-required-1920x1080` は名前は1920×1080だが1672×941または1672×940（16:9）も許容する（改名は別件）。

**2026-10-18 / #51**: TRM-01〜TRM-16は全て `recreate-required-1920x1080`、生成契約は `blocked`。以下の旧画像パスは参照専用で、旧mask・旧passは新候補の採用根拠にならない。現行再作成状態は [候補台帳](teramachi-rebuild-candidates.md)、建物群の生成前入力は [制作前確認](production/20261018-teramachi-preflight.md) を参照する。

| ID | 状態 | Ref | mask / 出力 | 具体的TBD |
|---|---|---|---|---|
| TRM-01 | recreate-required-1920x1080 | R006,R011 | `assets/images/fields/legacy/TRM-01.webp`; mask未記録 | 園庭の既存画像におけるTRM-08(bottom)/TRM-03(door-west)の実端、幼稚園期のtraversalを採寸する。TRM-16との接続は#51で廃止 【決定 kako-jun 2026-10-21、#51】「園庭は寺の正面の空間（境内）の右側半分に作るべき」。未決（kako-jun に要確認）: TRM-01 を TRM-03 に統合するのか、TRM-01 は園庭を表す別の絵として残すのか。通用門 TRM-03.door-kindergarten↔TRM-01.door-west・正門 TRM-01.bottom→TRM-08.top・TRM-01.event-kiss→BDY-01・MAP数130・接続136への影響は未決。台帳の既存接続はこの決定では書き換えていない。決定（kako-jun 2026-10-21、v3を見て『かなりいい』）:「右側の幼稚園のほうが大きな建物であるべき」「住居と違って掃き出し窓があるべき」「右端の門もなんのためにあるのかわからん」。TRM-03 の絵では幼稚園棟を住居棟より大きく（wider and deeper）し、幼稚園の南面に床まで届く引き違いのガラス窓（掃き出し窓。扉ではない）を並べる（住居は腰高窓のみ。枚数は仮）。通用門はこの絵に描かない。通用門の接続の扱いは TRM-01 統合の未決と一緒に要確認。決定（kako-jun 2026-10-21、#51）:「本堂を通らなくても左右の建物にも入口は必要だろ」。住居・幼稚園それぞれに、本堂を通らず外（南面）から入る玄関を付ける。【未決・衝突注記】『TRM-03から住居・遊戯室への屋外doorを新設しない』『屋外doorなし』（map-topology §6・遷移表・接続表、checklist、preflight）と衝突するが、既存の接続・記述は書き換えていない。候補・影響は Issue #51 のコメント参照（要確認）。決定（kako-jun 2026-10-21、#51）:「渡り廊下がながすぎる」。TRM-03 の絵では廊下棟を明確に短くする（建物との比で表現。数値は採用画像で確定。廊下の長さTBDは「短くする（比で表現）、数値は採用画像で確定」）。決定（kako-jun 2026-10-21、#51）:「段差はこれでいいのでは。車椅子生活になるとは思ってなかったのだし、最初からスロープだったら不自然。車椅子の子ができたと分かったあとに、この画像を渡してスロープがついた別マップに差し替えたほうがストーリー的に自然」。TRM-03（立位期）は v5 の外観を採用（本堂前の2段の石段を許容。参照用の採用外観で、mask・links・red-team未通過のためruntime未切替。詳細 docs/production/20261021-trm03-standing-exterior-adoption.md）。「段差を主路にせず／扉前に回転余地／車椅子通路」は車椅子期の別マップ（この外観を参照にスロープ付きで差し替える。新ID・MAP数・接続・差し替え時点は未決、要確認）に適用する。決定（kako-jun 2026-10-21、#51、『楽しそうな園庭がきえてしまっているぞ』）: 園庭は楽しそうにする。具体物は遊具（滑り台・ブランコ・半円アーチ型の遊具・斑点のある動物型の遊具）と雪遊びの物（雪だるま・そり・雪山・足跡。原文『雪遊びをする私立幼稚園の園庭』からの導出）で、数は複数、右半分の中の一箇所に固定しない。 |
| TRM-16 | recreate-required-1920x1080 | R006,R011 | `assets/images/fields/legacy/TRM-16.webp`; mask未記録 | TRM-01/TRM-15/TRM-17の三端と用水のblocked域を実画像から記録する |
| TRM-15 | recreate-required-1920x1080 | R006,R011 | `assets/images/fields/legacy/TRM-15.webp`; mask未記録 | TRM-16/TRM-07/TRM-06端、火の見櫓周囲のblocked域を記録する |
| TRM-07 | recreate-required-1920x1080 | R006,R011 | `assets/images/fields/legacy/TRM-07.webp`; mask未記録 | TRM-15/TRM-08/TRM-03端と山門のforeground域を記録する |
| TRM-08 | recreate-required-1920x1080 | R006,R011 | `assets/images/fields/legacy/TRM-08.webp`; mask未記録 | 用水・井戸のblocked域とTRM-07/TRM-09端、top側のTRM-01正門(#51)を記録する |
| TRM-09 | recreate-required-1920x1080 | R006,R011 | `assets/images/fields/legacy/TRM-09.webp`; mask未記録 | TRM-08/TRM-10端、銭湯煙突・雪山のforeground/blockedを記録する |
| TRM-10 | recreate-required-1920x1080 | R006,R011 | `assets/images/fields/legacy/TRM-10.webp`; mask未記録 | TRM-09/TRM-11を結ぶuniversalスロープの幅・折返しを記録する |
| TRM-11 | recreate-required-1920x1080 | R006,R011 | `assets/images/fields/legacy/TRM-11.webp`; mask未記録 | TRM-10/TRM-13端、TRM-12ドア、団地棟のforegroundを記録する |
| TRM-13 | recreate-required-1920x1080 | R006,R011,R025 | 1254×1254のv6候補・maskは参照専用。新規出力は1920×1080（返せない場合は16:9の1672×941または1672×940）、prompt・参照画像・mask・red-teamを新たに記録する | v6のleft→top石段・assist-only設計を参照し、16:9版を再生成する |
| TRM-06 | recreate-required-1920x1080 | R006,R011 | `assets/images/fields/legacy/TRM-06.webp`; mask未記録 | TRM-15.top入口とTRM-16.leftへのright出口以外を禁止辺とする（#51ループ化。TRM-05への勝手口の扉はTBD） |
| TRM-03 | recreate-required-1920x1080 | R006,R011,R024 | 旧境内画像は参照専用。新背景・mask未作成 | #60の屋外境内。TRM-07端、TRM-01.door-west通用門（境内の右＝東側）、TRM-04正面扉、墓地のblocked域・像・鐘楼を、採用した外観画像で確定して記録（決定 kako-jun 2026-10-21、#51: 池なし（お金持ちの寺ではない）／像と墓地は必須／鐘楼あり（演出に使える）。墓地は住居側（境内の左＝西側）。園庭側（右＝東）には置かない（kako-jun 2026-10-21、#51）。像（親鸞。笠と杖の小さな石像。蓮如には変えない）は中心の石畳の通路の脇に置き、通路の方を向く。向き（左右のどちら側か）は指定しない（kako-jun 2026-10-21、#51）。決定（kako-jun 2026-10-21、#51）「園庭は寺の正面の空間（境内）の右側半分に作るべき」。TRM-03 の絵は左半分＝住居側（墓地・像など）、右半分＝幼稚園の園庭。未決（kako-jun に要確認）: TRM-01 を TRM-03 に統合するのか、TRM-01 は園庭を表す別の絵として残すのか。通用門 TRM-03.door-kindergarten↔TRM-01.door-west・正門 TRM-01.bottom→TRM-08.top・TRM-01.event-kiss→BDY-01・MAP数130・接続136への影響は未決。台帳の既存接続はこの決定では書き換えていない。決定（kako-jun 2026-10-21、v3を見て『かなりいい』）:「右側の幼稚園のほうが大きな建物であるべき」「住居と違って掃き出し窓があるべき」「右端の門もなんのためにあるのかわからん」。TRM-03 の絵では幼稚園棟を住居棟より大きく（wider and deeper）し、幼稚園の南面に床まで届く引き違いのガラス窓（掃き出し窓。扉ではない）を並べる（住居は腰高窓のみ。枚数は仮）。通用門はこの絵に描かない。通用門の接続の扱いは TRM-01 統合の未決と一緒に要確認。決定（kako-jun 2026-10-21、#51）:「本堂を通らなくても左右の建物にも入口は必要だろ」。住居・幼稚園それぞれに、本堂を通らず外（南面）から入る玄関を付ける。【未決・衝突注記】『TRM-03から住居・遊戯室への屋外doorを新設しない』『屋外doorなし』（map-topology §6・遷移表・接続表、checklist、preflight）と衝突するが、既存の接続・記述は書き換えていない。候補・影響は Issue #51 のコメント参照（要確認）。決定（kako-jun 2026-10-21、#51）:「渡り廊下がながすぎる」。TRM-03 の絵では廊下棟を明確に短くする（建物との比で表現。数値は採用画像で確定。廊下の長さTBDは「短くする（比で表現）、数値は採用画像で確定」）。決定（kako-jun 2026-10-21、#51）:「段差はこれでいいのでは。車椅子生活になるとは思ってなかったのだし、最初からスロープだったら不自然。車椅子の子ができたと分かったあとに、この画像を渡してスロープがついた別マップに差し替えたほうがストーリー的に自然」。TRM-03（立位期）は v5 の外観を採用（本堂前の2段の石段を許容。参照用の採用外観で、mask・links・red-team未通過のためruntime未切替。詳細 docs/production/20261021-trm03-standing-exterior-adoption.md）。「段差を主路にせず／扉前に回転余地／車椅子通路」は車椅子期の別マップ（この外観を参照にスロープ付きで差し替える。新ID・MAP数・接続・差し替え時点は未決、要確認）に適用する。決定（kako-jun 2026-10-21、#51、『楽しそうな園庭がきえてしまっているぞ』）: 園庭は楽しそうにする。具体物は遊具（滑り台・ブランコ・半円アーチ型の遊具・斑点のある動物型の遊具）と雪遊びの物（雪だるま・そり・雪山・足跡。原文『雪遊びをする私立幼稚園の園庭』からの導出）で、数は複数、右半分の中の一箇所に固定しない。決定（kako-jun 2026-10-21、#51）: 木は描く（「木は描かせない」は撤回）。種類は葉を落とした枯木と雪をかぶった常緑樹の2つで、配置は境内の各所（一箇所に固定しない）。単調さを避けるため雪面は起伏・土の露出・足跡・石畳の汚れで変化をつける。池は置かない）。TRM-05/TRM-02屋外doorなし。共通外観参照は通過済み（順序・包含関係の確認用）だがTRM-03最終背景は未生成 |
| TRM-05 | recreate-required-1920x1080 | R006,R011,R021,R024 | 旧庫裏画像は参照専用。新背景・mask未作成 | #60/#51の西（本堂から見て左）の屋内住居。TRM-04.door-west↔door-hallのみ。内部廊下の扉位置、幅・段差・回転域、火事時遮断範囲がTBD。TRM-02直結なし 【決定 kako-jun 2026-10-21『住居部分は幼馴染の個室もあるだろう。そこに化石が置かれる。燃えるのは台所とその部屋とかだ。幼稚園のトイレは住居と兼用でもいい』: 記録上の読み = (1) TRM-05 に幼馴染の個室がある (2) その個室に化石が置かれる（story.md 95行・decisions.md 89行『台所の火が化石に引火』『幼馴染の部屋の化石』と整合、矛盾なし） (3) 火事で燃えるのは台所とその部屋（『とか』は他にも燃える場所があり得る意味。範囲は発明しない。『火事時の遮断範囲TBD』は『台所と幼馴染の個室を含む』まで進んだ。残りはTBD） (4) 幼稚園のトイレは住居と兼用でもよい（許容であり必須ではない。TRM-02にトイレを必須としない。置き場所TBD）。化石の形・大きさは原文に無くTBD（story.md は『2人で川でとった化石・割っていない・中身不明』まで）。接続・MAP数は未変更】 【決定 kako-jun 2026-10-21『住居も板張りでいいが、畳でなく細長いロールござを展開とかにしてもいい』: TRM-05（住居）の床は畳にせず、板張り、または細長いロールのござを広げた床（どちらかは画像で確定。「とか」は他の表現もあり得る意味で、範囲は発明しない）。これで畳を使う部屋は無くなった（TRM-04=板張り、TRM-02=板張りかリノリウム、TRM-05=板張りかロールござ）。畳の語・畳の原文は書き換えていない（要整合）。接続は書き換えていない】 【決定 kako-jun 2026-10-21（#51）:「寝室が1つなのは変だろ。2人暮らしだぞ。ただ、幼稚園までは父と同じ寝室で小学校からは寝室を無理やり1つ増やすなど、変化をつけるのもいい。どうせ燃えた後のマップも必要だし。ほか、化石の形がおかしい。アンモナイトじゃない。把握しろ」。記録上の読み: (1) 住居は父（園長先生）と幼馴染の2人暮らし。中3（火事前）の基準状態は寝室2つ（父の寝室・幼馴染の個室）。 (2) 幼稚園期は父と同じ寝室（1つ）、小学校から寝室を無理やり1つ増やす＝同じ間取りに間仕切りを足す案。「変化をつけるのもいい」は許容であって必須ではない。 (3) 燃えた後のマップも必要（台所とその部屋が燃えた状態。火事前／火事後は別画像。時期別は新ID・MAP数130・接続への影響が未決で、接続・MAP数は書き換えていない）。 (4) 化石の形（原文: decisions.md 43・86・89行、story.md 292行、art-direction.md 115行、monsters.md S004）: 幼馴染と2人で川（手取川）でとった化石。割っていない・中身不明。火の召喚獣（虎）の由来。おそらくサーベルタイガー、白山火山帯から手取川で流れてきた欠片かもしれない。推測で断定しない。アンモナイトは水の召喚獣 S001 の形でありこの化石ではない。画像では「ゴツゴツした茶色と黒の混ざった石。割っていない・中身は見えない・拳ほどの大きさ。渦巻きにしない」（2026-10-21 kako-jun「化石はゴツゴツした茶色と黒に混ざったものにしろ」で、先の「川の丸い石・滑らか・灰色」から更新）】 【決定 kako-jun 2026-10-21（#51）:「住居の下の扉は左にずらして机のある部屋に入れるべきだ。あと寝室側にいくための道が梁?が邪魔でみえない」。記録上の読み: (1) 南面の玄関の扉は、板の間（机のある部屋）に入る位置＝建物の中央より左に寄せる（採用外観の「中央よりやや東」から変更）。 (2) 板の間から各寝室へ入る出入口が見えること（仕切りの壁・柱・梁で隠さない）。 【食い違い・未決】採用外観（TRM-03、住居棟の南面の玄関扉は中央よりやや東）と食い違う。外観の画像編集で扉を左へ移すか、食い違いを許容するかは kako-jun に要確認（画像編集は別担当が実施中）。台帳の接続は書き換えていない。台帳（map-specifications 等）に玄関扉の位置の既存記述は見つからなかった（位置は外観画像で確定、という記述のみ）】 【決定 kako-jun 2026-10-21（#51）:「台所の設備が古すぎる。昭和にしろ」。記録上の読み: TRM-05 の台所の設備を昭和らしいものにする。具体例（ガスコンロ・タイル張りかステンレスの流し・ホーロー鍋・ガラス戸の食器棚・小さな冷蔵庫）は担当（コーディネーター）の例示で、kako-jun の指定ではない（kako-jun が別の物を挙げたらそちらを優先）。範囲: この決定は台所設備に限る。世界の時代は現代のままで、共通条件「昭和から残る建物や設備は存在してよいが、時代設定を昭和に戻さない」は維持する（台所の設備が昭和らしい＝昭和から残る設備、という整合）】 【決定 kako-jun 2026-10-21（#51）:「左に移せ。別画像にしろ。柱2本の意味がわからん。ないほうがいい」。記録上の読み（直前の質問への回答）: (1) 採用外観（TRM-03）の住居棟の玄関扉を左へ移す（建物の左から約1/4〜1/3、食卓のある板の間の前。元の位置は腰高窓）。外観の画像編集で対応し、採用外観を差し替える（編集版 ref-trm03-standing-v6。保存は編集完了後に別途指示）。 (2) 時期別の間取りは別画像: 幼稚園期=父と同じ寝室1つ／小学校以降=寝室を無理やり1つ増やす／中3火事前=寝室2つ（現基準）／火事後=台所とその部屋が燃えた状態。新ID・MAP数130→増加・接続（各状態に張るのか同一ID置換か）・差し替えの時点は未決（接続・MAP数は書き換えていない）。 (3) 寝室の出入口の柱（木の棒）と敷居の台座は不要＝仕切りの壁が途切れただけの素直な開口（柱なし）。東壁の開口（柱2本・まぐさ・敷居の帯）は言及がないので変更しない。『柱の意味が分からない』が東壁の開口にも当てはまるかは要確認】 |
| TRM-14 | recreate-required-1920x1080 | R006,R011 | `assets/images/fields/legacy/TRM-14.webp`; mask未記録 | TRM-13石段とSCH-01車椅子坂の端・通行クラスを記録する |
| KRB-01 | legacy-needs-review | R005,R011 | `assets/images/fields/legacy/KRB-01.webp`; mask未記録 | KRB-07/KRB-11/KRB-12端、百貨店door（相手はKRB-02.door-street）、封鎖期のKRB-12遷移を記録する |
| KRB-04 | legacy-needs-review | R005 | `assets/images/fields/legacy/KRB-04.webp`; mask未記録 | 3階（kako-jun 2026-10-19）。door-elevator（階選択遷移。全階から行き先を選ぶ。4階は条件つき）、売場通路のuniversal幅を記録する。KRB-04（3階・玩具売場）は2階KRB-03と無関係（決定 2026-10-19） |
| KRB-06 | legacy-needs-review | R005 | `assets/images/fields/legacy/KRB-06.webp`; mask未記録 | 5階（kako-jun決定 2026-10-19、#87。実在の大和は8階レストラン街）。door-elevator（階選択遷移。4階は条件つき）、再訪時の同一導線を記録する |
| KRB-08 | legacy-needs-review | R013,R011 | `assets/images/fields/legacy/KRB-08.webp`; mask未記録 | KRB-10/KRB-07端、KRB-09door、格子・側溝のblocked域を記録する |
| KRB-09 | legacy-needs-review | R013 | `assets/images/fields/legacy/KRB-09.webp`; mask未記録 | KRB-08door、座敷の段差・車椅子可否を決める |
| KRB-10 | legacy-needs-review | R011,R013 | `assets/images/fields/legacy/KRB-10.webp`; mask未記録 | TRM-17/KRB-08端、駐車場枝の画面内終端を記録する |
| KRB-13 | legacy-needs-review | R011 | `assets/images/fields/legacy/KRB-13.webp`; mask未記録 | KRB-12端、車寄せのuniversal幅と入口foregroundを記録する |
| STN-01 | legacy-needs-review | R011 | `assets/images/fields/legacy/STN-01.webp`; mask未記録 | KRB-11端、能登／内灘乗車door、広場の禁止辺を記録する |
| UTS-02 | legacy-needs-review | R007,R008 | `assets/images/fields/legacy/UTS-02.webp`; mask未記録 | UTS-01/UTS-03端、折返し主路と廃遊具のblocked域を記録する |
| SNL-06 | legacy-needs-review | R007 | `assets/images/fields/legacy/SNL-06.webp`; mask未記録 | 小さな屋外空間・巨大シャチホコ。水族館出口→屋外動物園。ラッコ館・海底洞窟の入口出口。M008戦は屋外、噴水と断定しない。 door-aquarium→SNL-05.door-outdoor、door-zoo→SNL-09.door-hub、door-otter-in→SNL-07.door-entry、door-otter-out→SNL-07.door-exit、door-cave-in→SNL-08.door-entry、door-cave-out→SNL-08.door-exit。旧画像は参照専用。pixel/mask/幅TBD |
| SNL-05 | legacy-needs-review | R007 | `assets/images/fields/legacy/SNL-05.webp`; mask未記録 | 格子状水槽の地下水族館。出口付近にピラルク巨大水槽。壁際にサメ標本・クジラの陰茎標本。展示格子と通行交点は別。 door-corridor→SNL-04.door-aquarium、door-outdoor→SNL-06.door-aquarium。旧画像は参照専用。pixel/mask/幅TBD |
| SNL-03 | legacy-needs-review | R007 | `assets/images/fields/legacy/SNL-03.webp`; mask未記録 | 下り渡り廊下途中・右側のゲームセンター。右は下降時の進行基準。SNL-02前半への割当はゲーム配置。 door-corridor→SNL-02.door-arcade-right。旧画像は参照専用。pixel/mask/幅TBD |
| UCH-02 | legacy-needs-review | R014,R015 | `assets/images/fields/legacy/UCH-02.webp`; mask未記録 | UCH-03端、駅出口と線路端のblocked域を記録する |
| UCH-05 | legacy-needs-review | R015 | `assets/images/fields/legacy/UCH-05.webp`; mask未記録 | UCH-04端、海側blocked帯と締まった砂のuniversal帯を記録する |
| NTR-01 | legacy-needs-review | R004 | `assets/images/fields/legacy/NTR-01.webp`; mask未記録 | STN-01/NTB-01door、車内通路とドア回転域を記録する |
| NTB-01 | legacy-needs-review | R004 | `assets/images/fields/legacy/NTB-01.webp`; mask未記録 | NTB-02端、終端線路のblocked域に加え、右辺→NTB-07.left（茂みの小径。道路ではない。暫定入口、入口MAPは要確認）を記録する |
| NTB-05 | legacy-needs-review | R004 | `assets/images/fields/legacy/NTB-05.webp`; mask未記録 | NTB-04/NTB-06端、家door、海側blocked域を記録する |
| NTB-06 | legacy-needs-review | R004 | `assets/images/fields/legacy/NTB-06.webp`; mask未記録・採用禁止 | 既存画像は海が上側で、既定の「能登の海は下側」に違反する。回転での救済はしない。NTB-05端・桟橋終端・海/テトラblocked域を満たす再構図版が必要 |
| NTB-08 | legacy-needs-review | R016 | `assets/images/fields/legacy/NTB-08.webp`; mask未記録 | 被災前の廃校（#89で被災前へ移動）。NTB-07.right→NTB-08.left、崩落棟blocked域を記録する。画像は据え置き |
| SCH-02 | legacy-needs-review | R006,R011 | `assets/images/fields/legacy/SCH-02.webp`; mask未記録 | SCH-01端、校門と校庭外周柵のblocked域を記録する |
| KRB-07 | blocked | R001,R002,R011 | 未生成・mask未作成 | KRB-08/KRB-01端、南北橋の型・欄干外blocked域をR001/R002と照合する |
| TRM-17 | blocked | R006,R011,R021,R024,R025 | 未生成・mask未作成 | TRM-16/KRB-10端、蛇行するuniversal坂と用水のblocked域を実景参照で確定する |
| UCH-03 | blocked | R003,R014,R015 | 未生成・mask未作成 | UCH-02/UCH-04端、砂丘木道の幅・防砂柵・深砂blocked域を確定する |
| NTB-02 | blocked | R004,R028 | 未生成・mask未作成 | NTB-01/NTB-03端、海を下に置く蛇行坂の集落尺度を能登沿岸資料で補う |
| NTB-03 | blocked | R004,R028 | 未生成・mask未作成 | NTB-02/NTB-04端、尾根・小祠・畑の資料と神社枝の終端を確定する |
| NTB-04 | blocked | R004,R028 | 未生成・mask未作成 | NTB-03/NTB-05端、下り坂の勾配と海側blocked域を沿岸資料で補う |
| UTS-01 | blocked | R007,R008,R010,R021,R026,R027 | 未生成・mask未作成 | KRB-11/UTS-02端、橋を含む東岸坂・石段assist域を実景資料で確定する |
| KRB-12 | blocked | R011,R023 | 未生成・mask未作成 | KRB-01/GRD-01/KRB-13端、封鎖柵の開閉差分と松・石垣の資料を追加する |
| SCH-01 | blocked | R006,R011,R021,R023,R024,R025 | 未生成・mask未作成 | TRM-14/SCH-02端、車椅子の連続坂・手すり・除雪帯の寸法根拠を追加する |
| KRB-11 | blocked | R005,R010,R011,R023,R026 | 未生成・mask未作成 | KRB-01/STN-01/UTS-01端、交差点の3出口と横断部の段差なし範囲を確定する |
| UCH-01 | blocked | R009,R021,R022 | 未生成・mask未作成 | STN-01/UCH-02door、車椅子回転域と半自動扉のゲーム上寸法を確定する |
| TRM-04 | recreate-required-1920x1080 | R021,R024 | 旧本堂画像は参照専用。新背景・mask未作成 | #60の中央屋内本堂。TRM-03南、TRM-05西、TRM-02東の扉位置、畳・仏具と主路、段差・幅・回転域を記録する 【決定 kako-jun 2026-10-21『畳がすごく不自然だ。苦手なら板張りにしろ。寺の本堂は普通の和室じゃないので、札とかが壁にあったりする。浄土真宗の寺の写真を調べろ』: 本堂の床は畳でなく板張りにする（畳の表現が不自然なため）。本堂は普通の和室ではなく壁に札などがある（具体は浄土真宗の本堂の調査後に追記）。本行の「畳」は書き換えていない（要整合）】 【決定 kako-jun 2026-10-21（調査反映、#51）: 本堂の壁の札は、確認できた2つ（外陣の向かって右の白壁の墨書の木の芳名板、矢来の上部に貼る紙の名簿＝過去帳・志納者一覧）だけにする。額・柱の対句・門徒札・貼り紙は根拠なしで入れない。床は板張り。区画は外陣→矢来→一段高い内陣、左右に余間。本尊は金色の阿弥陀如来立像（既定、要確認）。本行の「畳」は書き換えていない（要整合）】 【決定 kako-jun 2026-10-21『幼稚園に向かう渡り廊下には子どもらしい飾りを貼ればいい。描いた絵とかね』: 幼稚園に向かう渡り廊下（TRM-04 の東の廊下）の壁に子どもの描いた絵などの飾りを貼る（「とか」は他の子どもらしい飾りもあり得る意味で、範囲は発明しない）。接続・廊下長は書き換えていない】 【変更 2026-10-21（kako-jun 未確認）: 本堂の芳名板の位置は、調査（妙寂寺。外陣の向かって右の白壁）から意図的にずらし、西廊下の北壁（端から端まで）にする。見下ろしで外陣の東壁は細い帯になり読めないため。寺側=西廊下に芳名板、幼稚園側=東廊下に子どもの絵】 【決定 kako-jun 2026-10-21『渡り廊下の端の扉の向きが違うのでは』『左右に向けてあるべきだ』: 渡り廊下の外端の扉は左右（西/東）に向ける。西端は左向き、東端は右向き。接続は書き換えていない】 【決定 kako-jun 2026-10-21（#51）『よいが、仏壇前の柵や注意書きはいらない。参考写真は観光用のかもね。実際は個人の寺にはないものだ』: 矢来（仏壇前の柵）と名簿・注意書きは描かない（調査の参考写真は観光寺院由来で個人の町寺にはない）。余間の掛軸など他の観光寺院由来かもしれない要素は要確認】 【採用 kako-jun 2026-10-21（#51）: TRM-04 の絵は v11 を採用（`assets/images/fields/reference/teramachi-main-hall-interior-adopted.webp`、sha256 `837d3a10…6042`）。mask・links・red-team未通過のためruntime未切替、status変更なし。本行の「畳」は書き換えていない（要整合）】 |
| TRM-02 | recreate-required-1920x1080 | R021,R024 | 旧遊戯室画像は参照専用。新背景・mask未作成 | #60/#51の東（右）の屋内幼稚園。TRM-04.door-east↔TRM-02.door-west（本堂側＝西から入る）の扉位置・廊下長、舞台袖・椅子・主路の分離、段差・幅・回転域を記録する。TRM-05直結なし 【決定 kako-jun 2026-10-21『渡り廊下がながすぎる』: 廊下棟は短くする（建物との比で表現）。数値は採用画像で確定。本行の接続は書き換えていない】 【決定 kako-jun 2026-10-21『住居部分は幼馴染の個室もあるだろう。そこに化石が置かれる。燃えるのは台所とその部屋とかだ。幼稚園のトイレは住居と兼用でもいい』: 記録上の読み = (1) TRM-05 に幼馴染の個室がある (2) その個室に化石が置かれる（story.md 95行・decisions.md 89行『台所の火が化石に引火』『幼馴染の部屋の化石』と整合、矛盾なし） (3) 火事で燃えるのは台所とその部屋（『とか』は他にも燃える場所があり得る意味。範囲は発明しない。『火事時の遮断範囲TBD』は『台所と幼馴染の個室を含む』まで進んだ。残りはTBD） (4) 幼稚園のトイレは住居と兼用でもよい（許容であり必須ではない。TRM-02にトイレを必須としない。置き場所TBD）。化石の形・大きさは原文に無くTBD（story.md は『2人で川でとった化石・割っていない・中身不明』まで）。接続・MAP数は未変更】 【決定 kako-jun 2026-10-21: 原文のメッセージは「畳が苦手なら幼稚園も板やりのにうむ床にしろ」。「板張りかリノリウム」と読んだ（記録上の読み）。TRM-02（幼稚園の遊戯室）の床は畳にせず、板張りまたはリノリウム（どちらかは画像で確定）。舞台幕と小さな椅子の原文は維持。TRM-05（住居）の床は別決定待ち（畳か板か未決、浄土真宗の本堂の調査後）。接続は書き換えていない】 【決定 kako-jun 2026-10-21『幼稚園に向かう渡り廊下には子どもらしい飾りを貼ればいい。描いた絵とかね』: 幼稚園に向かう渡り廊下（TRM-04 の東の廊下）の壁に子どもの描いた絵などの飾りを貼る（「とか」は他の子どもらしい飾りもあり得る意味で、範囲は発明しない）。接続・廊下長は書き換えていない】 |
| TRM-12 | recreate-required-1920x1080 | R021,R024 | 未生成・mask未作成 | 県営住宅室内の玄関段差・回転域・TRM-11doorを創作寸法で決める |
| UTS-03 | blocked | R007,R008,R021,R027 | 未生成・mask未作成 | UTS-02/UTS-04端、東屋脇の枝なし蛇行主路の安全幅を決める |
| UTS-04 | blocked | R007,R008,R021,R027 | 未生成・mask未作成 | UTS-03/UTS-05端、崩落石垣を避けるassist主路の幅を決める |
| UTS-05 | blocked | R007,R008,R021,R027 | 未生成・mask未作成 | UTS-04/SNL-01端、山頂戦闘域と展望柵のblocked域を決める |
| SNL-01 | blocked | R027 | 未生成・mask未作成 | 八角形エントランス1階・受付。door-corridor→SNL-02.door-entry、door-stairs→SNL-12.door-stairs、bottom→UTS-05.top。八角形ホールの一辺から1階へ。受付横に階段と長い廊下への一辺。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| SNL-02 | blocked | R027 | 未生成・mask未作成 | 雪の森に囲まれた下り渡り廊下・前半。door-entry→SNL-01.door-corridor、door-next→SNL-04.door-prev、door-arcade-right→SNL-03.door-corridor。全2MAPの下り廊下、雪の森。途中の下降時右へゲームセンター（前半割当はゲーム配置）。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| SNL-04 | blocked | R027 | 未生成・mask未作成 | 雪の森に囲まれた下り渡り廊下・後半。door-prev→SNL-02.door-next、door-aquarium→SNL-05.door-corridor。長い下り廊下後半から地下水族館へ。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| SNL-09 | blocked | R027 | 未生成・mask未作成 | 狭い格子状の昭和の屋外動物園。door-hub→SNL-06.door-zoo、door-stairs→SNL-10.door-zoo。格子状の狭い劣悪な昭和の屋外檻。動物種・交点の通行はTBD。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| UCH-04 | blocked | R014,R015,R021 | 未生成・mask未作成 | UCH-03/UCH-05端、砂丘頂の柵・深砂・海側のblocked域を決める |
| NTA-01 | blocked | R016,R028,R029 | 未生成・mask未作成 | NTA-02/NTA-07端、NTB-01と同一地形の被災後差分を決める |
| NTA-02 | blocked | R016,R028,R029 | 未生成・mask未作成 | NTA-01/NTA-03端、仮設板路のassist可否と地割れblocked域を決める |
| NTA-03 | blocked | R016,R028,R029 | 未生成・mask未作成 | NTA-02/NTA-04端、倒木・神社枝封鎖の範囲を決める |
| NTA-04 | blocked | R016,R028,R029 | 未生成・mask未作成 | NTA-03/NTA-05端、地割れをまたぐ主路の安全表現を決める |
| NTA-05 | blocked | R016,R028,R029 | 未生成・mask未作成 | NTA-04/NTA-06端、実家door封鎖と生活路の範囲を決める |
| NTA-06 | blocked | R016,R028,R029 | 未生成・mask未作成 | NTA-05端、釣り場先端を終端にする柵と海のblocked域を決める |
| NTA-07 | blocked | R016,R028,R029 | 未生成・mask未作成 | NTA-01.right端、廃校の校庭に建つ仮設住宅の生活路・集会所doorを決める。NTB-08への接続は廃止（被災後の廃校は潰れて入れない）。入口は被災前NTB-01.right→NTB-07.leftの被災後版（NTA-01.right） |
| BDY-01 | blocked | R018 | 未生成・mask未作成 | 口・体内入口。door-passage-torso→BDY-02.door-passage-mouth。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |
| BDY-06 | blocked | R018 | 未生成・mask未作成 | 左手通路2・末端。door-passage-base→BDY-05.door-passage-tip。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |
| BDY-08 | blocked | R018 | 未生成・mask未作成 | 右手通路2・末端。door-passage-base→BDY-07.door-passage-tip。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |
| BDY-11 | blocked | R018 | 未生成・mask未作成 | 左足通路3・末端。door-passage-base→BDY-10.door-passage-tip。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |
| BDY-14 | blocked | R018 | 未生成・mask未作成 | 右足通路3・末端。door-passage-base→BDY-13.door-passage-tip。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |
| BDY-04 | blocked | R018 | 未生成・mask未作成 | 頭・脳の迷路通路。door-passage-torso→BDY-02.door-passage-head。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |
| BDY-15 | blocked | R018 | 未生成・mask未作成 | 胃・分岐室。door-passage-torso→BDY-03.door-passage-stomach。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |
| BDY-16 | blocked | R018 | 未生成・mask未作成 | 心臓・分岐室。door-passage-torso→BDY-02.door-passage-heart。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |
| OVS-01 | blocked | R019,R033 | 未生成・mask未作成 | 到着口/OVS-02端、凍結滑走路を通行不能にする空港導線を確定する |
| OVS-02 | blocked | R019,R033 | 未生成・mask未作成 | OVS-01/OVS-03端、凍った泉の画面内終端と乾燥寒冷地資料を確定する |
| OVS-03 | blocked | R019,R033 | 未生成・mask未作成 | OVS-02/OVS-04端、凍結穴・風食岩のblocked域を確定する |
| OVS-04 | blocked | R019 | 未生成・mask未作成 | 攻略双塔の共通基壇。door-left→OVS-05.door-base、door-right→OVS-10.door-base、bottom→OVS-03.top。左右塔は5階建て、雑多な増改築・無駄道・袋小路。左右対称・同一階平面反復を避ける。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| OVS-05 | blocked | R019 | 未生成・mask未作成 | 左塔1階・雑居入口。door-base→OVS-04.door-left、door-up→OVS-06.door-down。左右塔は5階建て、雑多な増改築・無駄道・袋小路。左右対称・同一階平面反復を避ける。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| OVS-07 | blocked | R019 | 未生成・mask未作成 | 左塔3階・配管と混在用途。door-down→OVS-06.door-up、door-up→OVS-08.door-down。左右塔は5階建て、雑多な増改築・無駄道・袋小路。左右対称・同一階平面反復を避ける。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| OVS-09 | blocked | R019 | 未生成・mask未作成 | 左塔5階・M015魔法のみ有効。door-down→OVS-08.door-up、door-bridge→OVS-15.door-left。左右塔は5階建て、雑多な増改築・無駄道・袋小路。左右対称・同一階平面反復を避ける。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| OVS-10 | blocked | R019 | 未生成・mask未作成 | 右塔1階・雑居入口。door-base→OVS-04.door-right、door-up→OVS-11.door-down。左右塔は5階建て、雑多な増改築・無駄道・袋小路。左右対称・同一階平面反復を避ける。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| OVS-12 | blocked | R019 | 未生成・mask未作成 | 右塔3階・増改築の交差路。door-down→OVS-11.door-up、door-up→OVS-13.door-down。左右塔は5階建て、雑多な増改築・無駄道・袋小路。左右対称・同一階平面反復を避ける。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| OVS-14 | blocked | R019 | 未生成・mask未作成 | 右塔5階・M016アビリティのみ有効。door-down→OVS-13.door-up、door-bridge→OVS-15.door-right。左右塔は5階建て、雑多な増改築・無駄道・袋小路。左右対称・同一階平面反復を避ける。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| OVS-15 | blocked | R019 | 未生成・mask未作成 | 塔間空中通路・シャー判明と雑魚共闘。door-left→OVS-09.door-bridge、door-right→OVS-14.door-bridge、door-third→OVS-16.door-bridge。左右塔は5階建て、雑多な増改築・無駄道・袋小路。左右対称・同一階平面反復を避ける。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| OVS-20 | blocked | R019 | 未生成・mask未作成 | 脱出第3塔1階・出口直前S005戦。door-up→OVS-19.door-down。5階建て第3塔の下降。各階は攻略塔同程度の面積。宝箱取捨選択、タイマー継続。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| APT-01 | blocked | R020,R021,R022,R032 | 未生成・mask未作成 | ワープ広場/APT-02door、駐機場blocked域を確定する |
| APT-02 | blocked | R020,R021,R022,R032 | 未生成・mask未作成 | APT-01/OVS-01door、一方通行の保安・搭乗導線を確定する |
| GRD-01 | blocked | R012,R030,R034,R035 | 未生成・mask未作成 | 真弓坂側の南西入口。top→GRD-03.bottom、right→GRD-02.left、bottom→KRB-12.top。池／堀・高低差、各出口の位置・幅、assistと閉鎖域、城攻略目標と解錠条件を個別確定する（#45） |
| GRD-02 | blocked | R012,R030,R034,R035 | 未生成・mask未作成 | 時雨亭・長谷池。left→GRD-01.right、top→GRD-04.bottom、right→GRD-09.left。池／堀・高低差、各出口の位置・幅、assistと閉鎖域、城攻略目標と解錠条件を個別確定する（#45） |
| GRD-03 | blocked | R012,R014,R030,R034,R035 | 未生成・mask未作成 | 瓢池・夕顔亭・翠滝下段。bottom→GRD-01.top、right→GRD-04.left、top→GRD-10.bottom。池／堀・高低差、各出口の位置・幅、assistと閉鎖域、城攻略目標と解錠条件を個別確定する（#45） |
| GRD-04 | blocked | R012,R013,R030,R034,R035 | 未生成・mask未作成 | 霞ヶ池西岸・栄螺山。bottom→GRD-02.top、left→GRD-03.right、top→GRD-05.bottom。池／堀・高低差、各出口の位置・幅、assistと閉鎖域、城攻略目標と解錠条件を個別確定する（#45） |
| GRD-05 | blocked | R012,R004,R030,R034,R035 | 未生成・mask未作成 | 霞ヶ池北岸・ことじ灯籠。bottom→GRD-04.top、right→GRD-06.left、left→GRD-10.right。池／堀・高低差、各出口の位置・幅、assistと閉鎖域、城攻略目標と解錠条件を個別確定する（#45） |
| GRD-06 | blocked | R012,R007,R030,R034,R035 | 未生成・mask未作成 | 霞ヶ池東岸・唐崎松。left→GRD-05.right、bottom→GRD-07.top。池／堀・高低差、各出口の位置・幅、assistと閉鎖域、城攻略目標と解錠条件を個別確定する（#45） |
| GRD-07 | blocked | R012,R030,R034,R035 | 未生成・mask未作成 | 曲水・根上松。top→GRD-06.bottom、bottom→GRD-08.top、left→GRD-09.right。池／堀・高低差、各出口の位置・幅、assistと閉鎖域、城攻略目標と解錠条件を個別確定する（#45） |
| GRD-08 | blocked | R012,R030,R034,R035 | 未生成・mask未作成 | 山崎山・花見橋側。top→GRD-07.bottom、bottom→GRD-09.top。池／堀・高低差、各出口の位置・幅、assistと閉鎖域、城攻略目標と解錠条件を個別確定する（#45） |
| GRD-09 | blocked | R012,R030,R034,R035 | 未生成・mask未作成 | 梅林側の南周回路。left→GRD-02.right、right→GRD-07.left、top→GRD-08.bottom。池／堀・高低差、各出口の位置・幅、assistと閉鎖域、城攻略目標と解錠条件を個別確定する（#45） |
| GRD-10 | blocked | R012,R017,R030,R031,R034,R035 | 未生成・mask未作成 | 桂坂口・石川橋。bottom→GRD-03.top、right→GRD-05.left、top→CST-01.bottom。池／堀・高低差、各出口の位置・幅、assistと閉鎖域、城攻略目標と解錠条件を個別確定する（#45） |
| CST-01 | blocked | R017,R031,R034,R035 | 未生成・mask未作成 | 石川門の枡形。left→CST-02.right、bottom→GRD-10.top。池／堀・高低差、各出口の位置・幅、assistと閉鎖域、城攻略目標と解錠条件を個別確定する（#45） |
| CST-02 | blocked | R017,R031,R034,R035 | 未生成・mask未作成 | 三の丸。right→CST-01.left、top→CST-03.bottom、left→CST-04.right、bottom→CST-08.top。池／堀・高低差、各出口の位置・幅、assistと閉鎖域、城攻略目標と解錠条件を個別確定する（#45） |
| CST-03 | blocked | R017,R031,R034,R035 | 未生成・mask未作成 | 菱櫓・五十間長屋。bottom→CST-02.top、door-west→CST-05.door-hishi、door-south→CST-04.door-north。池／堀・高低差、各出口の位置・幅、assistと閉鎖域、城攻略目標と解錠条件を個別確定する（#45） |
| CST-04 | blocked | R017,R031,R034,R035 | 未生成・mask未作成 | 橋爪門・橋爪門続櫓。right→CST-02.left、left→CST-05.right、door-north→CST-03.door-south。池／堀・高低差、各出口の位置・幅、assistと閉鎖域、城攻略目標と解錠条件を個別確定する（#45） |
| CST-05 | blocked | R017,R031,R034,R035 | 未生成・mask未作成 | 二の丸。door-hishi→CST-03.door-west、right→CST-04.left、left→CST-06.right、bottom→CST-07.top。池／堀・高低差、各出口の位置・幅、assistと閉鎖域、城攻略目標と解錠条件を個別確定する（#45） |
| CST-06 | blocked | R017,R031,R034,R035 | 未生成・mask未作成 | 低地の玉泉院丸庭園。right→CST-05.left。池／堀・高低差、各出口の位置・幅、assistと閉鎖域、城攻略目標と解錠条件を個別確定する（#45） |
| CST-07 | blocked | R017,R031,R034,R035 | 未生成・mask未作成 | 極楽橋・本丸附段・三十間長屋側。top→CST-05.bottom、right→CST-09.left。3攻略目標完了後にCST-09本丸入口を解錠。池／堀・高低差、各出口の位置・幅、assistと閉鎖域、城攻略目標と解錠条件を個別確定する（#45） |
| CST-08 | blocked | R017,R031,R034,R035 | 未生成・mask未作成 | 鶴の丸・東の丸側。top→CST-02.bottom、left→CST-09.right。3攻略目標完了後にCST-09本丸入口を解錠。池／堀・高低差、各出口の位置・幅、assistと閉鎖域、城攻略目標と解錠条件を個別確定する（#45） |
| CST-09 | blocked | R017,R031,R034,R035 | 未生成・mask未作成 | 高い本丸。left→CST-07.right、right→CST-08.left、door-tower→CST-10.door-base。池／堀・高低差、各出口の位置・幅、assistと閉鎖域、城攻略目標と解錠条件を個別確定する（#45） |
| CST-10 | blocked | R017,R031,R034,R035 | 未生成・mask未作成 | 本丸内のイマジナリー天守上層。door-base→CST-09.door-tower。池／堀・高低差、各出口の位置・幅、assistと閉鎖域、城攻略目標と解錠条件を個別確定する（#45） |

## 2026-10-18追加ID

| ID | 状態 | Ref | mask / 出力 | 具体的TBD |
|---|---|---|---|---|
| SNL-12 | blocked | R027 | 未生成・mask未作成 | 八角形エントランス2階・全方向の窓。door-hotel→SNL-11.door-entry、door-stairs→SNL-01.door-stairs。2階は全方向の窓。一辺から和室宿泊棟、階段で1階。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| SNL-11 | blocked | R027 | 未生成・mask未作成 | 廃墟の和室が並ぶ宿泊棟。door-far-end→SNL-10.door-hotel、door-entry→SNL-12.door-hotel。廃墟の和室が並ぶ。入口2階側と屋外階段側の両端。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| SNL-10 | blocked | R027 | 未生成・mask未作成 | 動物園から宿泊棟端への屋外階段。door-zoo→SNL-09.door-stairs、door-hotel→SNL-11.door-far-end。ユーザー創作の動物園→宿泊棟端の屋外階段。assist方法TBD。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| SNL-07 | blocked | R027 | 未生成・mask未作成 | ラッコ館・入口と出口のある任意探索。door-entry→SNL-06.door-otter-in、door-exit→SNL-06.door-otter-out。入口・出口別。宝箱目当ての任意通り抜け。同じ屋外SNL-06へ戻すのはゲーム配置。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| SNL-08 | blocked | R027 | 未生成・mask未作成 | 低予算昭和の海底探検洞窟・任意探索。door-entry→SNL-06.door-cave-in、door-exit→SNL-06.door-cave-out。低予算昭和の海底探検の作り物。ダイオウイカ・難破船・ニンゲン。入口出口別、任意宝箱。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| OVS-06 | blocked | R019 | 未生成・mask未作成 | 左塔2階・迷路状の増築。door-down→OVS-05.door-up、door-up→OVS-07.door-down。左右塔は5階建て、雑多な増改築・無駄道・袋小路。左右対称・同一階平面反復を避ける。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| OVS-08 | blocked | R019 | 未生成・mask未作成 | 左塔4階・無駄道と袋小路。door-down→OVS-07.door-up、door-up→OVS-09.door-down。左右塔は5階建て、雑多な増改築・無駄道・袋小路。左右対称・同一階平面反復を避ける。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| OVS-11 | blocked | R019 | 未生成・mask未作成 | 右塔2階・混在用途の迷路。door-down→OVS-10.door-up、door-up→OVS-12.door-down。左右塔は5階建て、雑多な増改築・無駄道・袋小路。左右対称・同一階平面反復を避ける。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| OVS-13 | blocked | R019 | 未生成・mask未作成 | 右塔4階・無駄道と袋小路。door-down→OVS-12.door-up、door-up→OVS-14.door-down。左右塔は5階建て、雑多な増改築・無駄道・袋小路。左右対称・同一階平面反復を避ける。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| OVS-16 | blocked | R019 | 未生成・mask未作成 | 脱出第3塔5階・宝箱と下り階段。door-bridge→OVS-15.door-third、door-down→OVS-17.door-up。5階建て第3塔の下降。各階は攻略塔同程度の面積。宝箱取捨選択、タイマー継続。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| OVS-17 | blocked | R019 | 未生成・mask未作成 | 脱出第3塔4階・宝箱と下り階段。door-up→OVS-16.door-down、door-down→OVS-18.door-up。5階建て第3塔の下降。各階は攻略塔同程度の面積。宝箱取捨選択、タイマー継続。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| OVS-18 | blocked | R019 | 未生成・mask未作成 | 脱出第3塔3階・宝箱と下り階段。door-up→OVS-17.door-down、door-down→OVS-19.door-up。5階建て第3塔の下降。各階は攻略塔同程度の面積。宝箱取捨選択、タイマー継続。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| OVS-19 | blocked | R019 | 未生成・mask未作成 | 脱出第3塔2階・宝箱と下り階段。door-up→OVS-18.door-down、door-down→OVS-20.door-up。5階建て第3塔の下降。各階は攻略塔同程度の面積。宝箱取捨選択、タイマー継続。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |

## #74追加ID（胴体・肺）

| ID | 状態 | Ref | mask / 出力 | 具体的TBD |
|---|---|---|---|---|
| BDY-02 | blocked | R018 | 未生成・mask未作成 | 上半身・胴体上段。door-passage-mouth→BDY-01.door-passage-torso、door-passage-lower→BDY-03.door-passage-upper、door-passage-head→BDY-04.door-passage-torso、door-passage-left-arm→BDY-05.door-passage-torso、door-passage-right-arm→BDY-07.door-passage-torso、door-passage-heart→BDY-16.door-passage-torso、door-passage-lung→BDY-17.door-passage-torso。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |
| BDY-17 | blocked | R018 | 未生成・mask未作成 | 肺・分岐室。door-passage-torso→BDY-02.door-passage-lung。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |

## #74追加ボリューム（上半身・下半身／手2／足3）

| ID | 状態 | Ref | mask / 出力 | 具体的TBD |
|---|---|---|---|---|
| BDY-03 | blocked | R018 | 未生成・mask未作成 | 下半身・胴体下段。door-passage-upper→BDY-02.door-passage-lower、door-passage-left-leg→BDY-09.door-passage-torso、door-passage-right-leg→BDY-12.door-passage-torso、door-passage-stomach→BDY-15.door-passage-torso。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |
| BDY-05 | blocked | R018 | 未生成・mask未作成 | 左手通路1・付け根側。door-passage-torso→BDY-02.door-passage-left-arm、door-passage-tip→BDY-06.door-passage-base。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |
| BDY-07 | blocked | R018 | 未生成・mask未作成 | 右手通路1・付け根側。door-passage-torso→BDY-02.door-passage-right-arm、door-passage-tip→BDY-08.door-passage-base。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |
| BDY-09 | blocked | R018 | 未生成・mask未作成 | 左足通路1・付け根側。door-passage-torso→BDY-03.door-passage-left-leg、door-passage-middle→BDY-10.door-passage-base。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |
| BDY-10 | blocked | R018 | 未生成・mask未作成 | 左足通路2・中間。door-passage-base→BDY-09.door-passage-middle、door-passage-tip→BDY-11.door-passage-base。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |
| BDY-12 | blocked | R018 | 未生成・mask未作成 | 右足通路1・付け根側。door-passage-torso→BDY-03.door-passage-right-leg、door-passage-middle→BDY-13.door-passage-base。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |
| BDY-13 | blocked | R018 | 未生成・mask未作成 | 右足通路2・中間。door-passage-base→BDY-12.door-passage-middle、door-passage-tip→BDY-14.door-passage-base。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |

## #87/#89追加ID

| ID | 状態 | Ref | mask / 出力 | 具体的TBD |
|---|---|---|---|---|
| KRB-02 | blocked | R005 | 未生成・mask未作成 | デパート1階（入口階）。時計のある吹き抜け（アトリオ参照。出所 https://github.com/kako-jun/sit-by-me/issues/87#issuecomment-6258778050）。実在店に似せないジオラマ、大和4階の時計サロンとは別。door-street→KRB-01.door、door-elevator（階選択遷移。扉に入るとウィンドウで階を選び、選んだ階の扉前に着く。箱は全階を結びMAPを持たない。決定 2026-10-19）。TBD: 売場の中身、1階での出来事。画像生成blocked。 |
| KRB-03 | blocked | R005 | 未生成・mask未作成 | デパート2階（隠し階。https://github.com/kako-jun/sit-by-me/issues/87 2026-10-19の決定）。実在店に似せないジオラマ。door-elevator（階選択遷移）。四角い吹き抜けの廊下だけ（売場は無い。決定 2026-10-19）。歩行域=廊下の環のみ、吹き抜け部分はblocked（歩行マスク契約）。描画=中央の吹き抜けから下の1階が見える（侵入不可）。見える1階=KRB-02(同じ場所を2階から見下ろす視点で描く)。契約: KRB-02の背景を作るときはKRB-03の吹き抜け越しの絵と整合させる(KRB-02の吹き抜け・時計・床の見た目が共通の参照)。決定: 2階は最初から解放（解放条件なし。2026-10-19）。KRB-04（3階・玩具売場）とKRB-03は無関係（決定）。吹き抜けの縁では落下しない（吹き抜けは歩行不可のblockedで、落下の仕組みは無い。kako-jun決定 2026-10-19、#87）。隠し階の行き方は決定済み: エレベーターの扉→階選択ウィンドウ（B案）。画像生成blocked。 |
| KRB-05 | blocked | R005 | 未生成・mask未作成 | デパート4階（隠し階・条件つき。最終章で兼六園へ向かう途中にデパートに寄り道すると、階選択で4階も選べるようになる(決定 2026-10-19)。最終章の兼六園への道（茶屋街→香林坊→広坂→兼六園）の途中の、香林坊のデパートに入ると階選択に4階が出る。専用イベントなし（デパートに入ること自体が条件。kako-jun決定 2026-10-19、#87）。強い何か=ものまね（FF5/6の隠しアビリティに相当。kako-jun決定 2026-10-19、#87）。魔法扱い（パーティ共通の共有ライブラリ。全員が使える）。4階の敵は「鏡」=映った自分たち自身（パーティの姿）で、ボス扱い。兼六園の最終救済には出ない（これまでのボスは兼六園でも雑魚敵として出さない）ので、ものまねはここでしか覚えられない。鏡の技「ものまね」を食らった味方が戦闘終了時に自動でラーニング（既存規則）。ものまねの効果=直前の味方の行動を、ノーコスト（MP・AP等の消費なし）で真似る。敵の行動は真似ない（回数・対象の選び方などの細部は未決）。要確認(#87): 鏡の敵の新規ID・映り込みの流用方法（鏡像・色味・何人映るか。味方の映り込みを流用できるならしたい。実現可否と作り方は要確認）・戦闘仕様。https://github.com/kako-jun/sit-by-me/issues/87 2026-10-19の決定）。実在店に似せないジオラマ。door-elevator（階選択遷移。選択肢に出る条件はシナリオ側）。TBD: 鏡の敵のID・映り込みの流用方法・戦闘仕様（#87）。行き方は決定済み: エレベーターの扉→階選択ウィンドウ（B案）。4階は最終章の兼六園途中の寄り道で選択肢に出る。画像生成blocked。 |
| NTB-07 | blocked | R016 | 未生成・mask未作成 | 廃校の校庭（被災前）。left←NTB-01.right（茂みの小径の暫定入口）、right→NTB-08.left。TBD: 入口MAP（NTB-01は暫定）、茂みの見せ方、校庭の見た目、勝手口等の扉、校庭↔NTB-08の辺はright↔leftで選択済み（理由はmap-topology.md）。 |
