# MAP個別仕様

`map-asset-registry.md` の全行に対応する、生成前の個別仕様帳。全MAPは北上固定で、道路だけの絵は禁止する。`TBD` が残るものは `blocked`。この文書は一枚ごとの仕様を埋め続ける正本である。

## 寺町（河岸段丘）

| MAP | 時期 | 一言特徴 | 不変条件／接続 | 暫定固定 |
|---|---|---|---|---|
| E01 kindergarten | 幼稚園前半〜終幕 | 本堂の裏で雪遊びをする私立幼稚園の園庭（屋外） | 段丘上。bottom→E05.top（正門）、door-west→E11.door-kindergarten（境内の右隣の通用門） | F02は同じ幼稚園の屋内。E01↔F02の直結doorは未契約のため描かない |
| E02 connector | 全時期 | 用水と寺門が交わる斜め道 | 左端←E10.right（住居裏の勝手口の細道から。旧E01接続は#51で廃止）、右→E03（東）、北→N2 | 画面内で北東へ曲がる（旧「E01から入って」はTBD）。犀川へ向かう出口はtop |
| E03 hinomi-bend | 全時期 | 火の見櫓を曲がる見通しの悪い角 | E02西↔E04東、南→E10 | 細道は画面内で終えず、E10.right→E02.leftへ戻る（#51） |
| E04 wide-road | 全時期 | 消雪パイプと寺の長塀の広い道 | E03西↔E05東、北の山門→E11 | 山門は中央より北寄り |
| E05 well-merge | 全時期 | 井戸と用水が合流するS字 | E04西↔E06東、top←E01.bottom | 水路と井戸の縁は黒マスク。E01の正門が真上に付く（#51） |
| E06 sento | 全時期 | 湯気の煙突が立つ銭湯前 | E05西↔E07南 | 時期差は営業灯だけ、地形不変 |
| E07 barrier-free-ramp | 事故後 | 犀川側の団地へ下る雪囲いスロープ | E06北→E08南、蛇行する車椅子主路 | 途中の急段差なし |
| E08 danchi-court | 事故後〜壮年 | 犀川側の県営住宅の中庭 | E07北↔E09東、棟入口→F03 | 団地内はドア遷移 |
| E09 old-slope-foot | 立てる時期 | 石段の下の古い坂道 | E08西↔E13北、車椅子不可 | 事故後は入口を閉鎖 |
| E10 narrow-lane | 全時期 | 寺の勝手口へ入る土塀の細道 | E03.bottomから入り、E10.right→E02.leftへ戻るループの一部。住居の裏の道 | 宝箱枝の扱い・E12への勝手口の扉はTBD（要確認） |
| E11 temple-grounds | 全時期 | 親鸞像のある浄土真宗の境内（屋外） | bottom→E04、door-main→F01、door-kindergarten→E01.door-west | #60/#51。本堂中心・境内から見て左（西）住居・右（東）幼稚園の同じ建物群。E01は境内の右隣。住居／遊戯室への屋外doorなし |
| E12 residence | 全時期 | 庫裏の台所と幼馴染の部屋（屋内） | door-hall→中央F01のdoor-west。F02直結なし | #60/#51。本堂の西（左）。台所は火事イベントの場所 |
| E13 slope-top | 立てる時期〜中学生 | 段丘上の分岐、学校側へ向く眺め | E09南↔N10東、車椅子主路はN10側 | 石段と学校坂を混同しない |

## 香林坊〜武蔵ヶ辻

| MAP | 時期 | 一言特徴 | 不変条件／接続 | 暫定固定 |
|---|---|---|---|---|
| E14 korinbo | 幼稚園・壮年 | 地下入口のある繁華街交差点 | N1南、N11北、N9東への分岐。百貨店door→F83.door-street | 犀川北岸の結節点 |
| E15 toy-floor | 幼稚園 | ブラウン管デモ台のあるおもちゃ売場（3階） | door-korinbo↔F83.door-toys、door-restaurant↔E16.door、door-2f↔F85.door-upper（隠し階の枝）、door-4f→F86.door-lower（条件つき）。玩具売場 | 購入イベントE005。3階はkako-jun決定（2026-10-19）。階移動はエレベーター（1つの箱が全階を結び、階選択はUI側）。TBD: 旧「おもちゃ売場」と2階F85の関係 |
| F83 | 幼稚園・壮年 | デパート1階（入口階）。時計のある吹き抜け（アトリオ参照） | door-street→E14.door、door-toys↔E15.door-korinbo、door-restaurant↔E16.door-lobby、door-2f↔F85.door-lower | 売場は香林坊アトリオの、からくり時計（アトリオクロック）のある吹き抜けを参考にする（kako-jun 2026-10-19、出所 https://github.com/kako-jun/sit-by-me/issues/87#issuecomment-6258778050）。実在店に似せないジオラマ（art-direction.md の既存方針）。香林坊大和4階の時計サロンとは別でアトリオクロックと無関係、ワープ先レストラン（大和8階）とも別の建物。TBD（要確認）: 1階の売場の中身、階の移動はエレベーターだけ（決定 2026-10-19）。エレベーターは1つの箱が全階を結び、階選択はUI側（箱は独立MAPにしない）。扉に入るとウィンドウで行き先の階を選び、選んだ階の扉前に着く（#87追加決定 2026-10-19）。台帳の扉の組はその代表経路（map-topology.md §3.2）。TBD（要確認）: 2階の解放条件。1階での出来事の有無。画像生成blocked。 |
| F85 | 幼稚園・壮年 | デパート2階（隠し階） | door-lower↔F83.door-2f、door-upper↔E15.door-2f（1階・3階から行ける枝。通らなくても本筋は成立） | 隠し階（#87の決定 2026-10-19）。階移動はエレベーターだけ（1つの箱が全階を結び、階選択はUI側）。売場の中身は未決定（創作しない）。TBD（要確認）: 2階の解放条件（最初から使えるのか別条件か）、2階の売場の中身、隠し階への行き方（エレベーターのボタン等）、E15旧「おもちゃ売場」との関係。実在店に似せないジオラマ。画像生成blocked。 |
| F86 | 壮年（ラスボス付近） | デパート4階（隠し階・条件つき） | door-lower↔E15.door-4f、door-upper↔E16.door-4f（どちらも条件つき。解放条件はシナリオ側。階選択はUI側のエレベーター） | 最初は無く、ラスボス付近でデパートに立ち寄ると行けるようになり強い何かが手に入る（#87の決定 2026-10-19）。売場の中身・「強い何か」の中身は未決定（創作しない）。TBD（要確認）: 4階の見た目、強い何か、行き方（ボタン等）、未解放の間のE15→E16。実在店に似せないジオラマ。画像生成blocked。 |
| E16 restaurant | 幼稚園・壮年 | 高層階のお子様ランチのレストラン（5階。実在の大和は8階レストラン街） | door↔E15.door-restaurant、door-lobby↔F83.door-restaurant、door-4f↔F86.door-upper（条件つき） | 再訪時の差分。5階はkako-jun決定（2026-10-19、#87。実在は8階だがゲーム内は5階）。序盤のワープ先は2階・4階を通らず1階／3階から直接来られる |
| E17 chaya-lane | 幼稚園・壮年 | 犀川手前の暗い格子の茶屋道 | E19南、N1北、茶室E18のドア | にし茶屋街は犀川南岸 |
| E18 tearoom | 幼稚園以降 | 雪明かりの弁柄色の茶室 | chaya-laneのドア | イベント用途 |
| E19 convenience | 幼稚園 | 除雪雪山のある無名コンビニ | N2南から受け、E17北へ抜ける | 犀川南岸の寺町帰路 |
| E20 hospital | 壮年 | スロープと車寄せのある私立病院 | N9西から東〜南東へ入る | 小立野側、車椅子の車寄せ |
| N1 | 幼稚園 | 融雪水の犀川鉄橋 | E17南岸→E14北岸を南北に渡る | 橋上に枝なし |
| N2 | 幼稚園 | 用水と黒瓦を見上げる寺町坂 | E02南→E19北、北上しつつ蛇行して段丘へ | 車椅子主坂 |
| N9 | 壮年 | 松と石垣で二手に分かれる広坂 | E14西→F41北、E20東のT字 | 封鎖は切替柵 |
| N11 | 幼稚園〜再訪 | バス屋根と市場アーケードの十字 | E14南→E21北／N8東 | 浅野川橋はN8内 |

## 寺町の屋内（追加3枚）

| MAP | 時期 | 一言特徴 | 方位・主路・通行条件 | 暫定固定 |
|---|---|---|---|---|
| F01 | 全時期 | 仏具の鈍い金と畳が対照になる本堂（屋内） | door-south→E11、door-west→E12.door-hall、door-east→F02.door-west。参拝域は端へ出ない | #60。中央の屋内分岐。住居・幼稚園へ外に出ず移動 |
| F02 | 幼稚園期・火事後 | 舞台幕と小さな椅子が残る遊戯室（屋内） | door-west→F01.door-east（本堂側＝西から入る）。扉位置・廊下長はTBD。舞台袖は画面内終端。E12直結なし | #60/#51。本堂の東（右）。劇の自動イベント用。E01と同じ幼稚園で、園庭直結は未契約 |
| F03 | 事故後〜壮年 | 車椅子の回転余地がある県営住宅の団地室 | E08棟入口からドア遷移。玄関→居間→窓際で、段差なし。 | 犀川側・段丘下の生活空間。 |

## 卯辰山・サニーランド

**現行指定**: 八角形入口1階・2階、雪の森の長い下り渡り廊下2MAP、地下水族館、シャチホコ屋外空間、昭和の屋外動物園、創作の屋外階段、和室宿泊棟が双方向円環。ラッコ館・洞窟は任意の入口出口付き探索。

山は「東岸へ渡る→北へ上る→西へ折返す→再び北東へ上る」の蛇行を固定し、分岐・宝箱脇道・近道を置かない。全て事故後も同行者が押せる幅の緩勾配を主路として残す。

| MAP | 時期 | 一言特徴 | 方位・主路・通行条件 | 暫定固定 |
|---|---|---|---|---|
| N8 | 小学生前半 | 浅野川橋の先で杉林へ折れる寺門の登り口 | N11の東から入り、東へ橋を渡り、北へ折れる。`left→top`。橋はこのMAP内、石段は脇。 | 浅野川横断を独立MAPにしない。 |
| E22 | 小学生前半 | 廃遊具の脇を二度折り返す山腹道 | N8から南で受け、左カーブ→右カーブで北へ抜ける。 | 山道1枚目。 |
| F04 | 小学生前半 | 雪をかぶった展望東屋を回り込む尾根道 | E22の南から入り、東へ緩く振れて北へ戻る。東屋は道沿いの景観で、枝は作らない。 | 山道2枚目。 |
| F05 | 小学生前半 | 崩れた石垣を避けるヘアピン坂 | F04南→西への折返し→北。崩落側は柵で黒マスク、主坂は幅を保つ。 | 山道3枚目。 |
| F06 | 小学生前半 | 氷の召喚獣と対峙する風穴のある山頂広場 | F05南から入り、北端からF07へ。展望柵は主路外、枝なし。 | 屋外山ダンジョンの終点。 |
| F07 | 小学生前半 | 八角形エントランス1階・受付 | door-corridor→F08.door-entry、door-stairs→F61.door-stairs、bottom→F06.top | 八角形ホールの一辺から1階へ。受付横に階段と長い廊下への一辺。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| F08 | 小学生前半 | 雪の森に囲まれた下り渡り廊下・前半 | door-entry→F07.door-corridor、door-next→F09.door-prev、door-arcade-right→E25.door-corridor | 全2MAPの下り廊下、雪の森。途中の下降時右へゲームセンター（前半割当はゲーム配置）。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| F09 | 小学生前半 | 雪の森に囲まれた下り渡り廊下・後半 | door-prev→F08.door-next、door-aquarium→E24.door-corridor | 長い下り廊下後半から地下水族館へ。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| F10 | 小学生前半 | 狭い格子状の昭和の屋外動物園 | door-hub→E23.door-zoo、door-stairs→F63.door-zoo | 格子状の狭い劣悪な昭和の屋外檻。動物種・交点の通行はTBD。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| E23 | 小学生前半 | 小さな屋外空間・巨大シャチホコ | door-aquarium→E24.door-outdoor、door-zoo→F10.door-hub、door-otter-in→F64.door-entry、door-otter-out→F64.door-exit、door-cave-in→F65.door-entry、door-cave-out→F65.door-exit | 水族館出口→屋外動物園。ラッコ館・海底洞窟の入口出口。M008戦は屋外、噴水と断定しない。 pixel/mask/幅TBD |
| E24 | 小学生前半 | 格子状水槽の地下水族館 | door-corridor→F09.door-aquarium、door-outdoor→E23.door-aquarium | 出口付近にピラルク巨大水槽。壁際にサメ標本・クジラの陰茎標本。展示格子と通行交点は別。 pixel/mask/幅TBD |
| E25 | 小学生前半 | 下り渡り廊下途中・右側のゲームセンター | door-corridor→F08.door-arcade-right | 右は下降時の進行基準。F08前半への割当はゲーム配置。 pixel/mask/幅TBD |

## 内灘・浅野川線

| MAP | 時期 | 一言特徴 | 方位・主路・通行条件 | 暫定固定 |
|---|---|---|---|---|
| E21 | 幼稚園〜終幕 | 鼓門の下に雪が弧を描く金沢駅前 | N11南から北へ入り、鉄道乗場は屋内遷移。左右の広場は画面内で終える。 | 能登・内灘への発着、ワープ到達可。 |
| N12 | 中学生後半 | 結露窓と赤い座席が続く浅野川線車内 | 乗車ドア→横長通路→降車ドア。両端に回転余地、座席は通路外。 | 金沢駅とE26をつなぐ乗車遷移。 |
| E26 | 中学生後半 | 風を受ける小駅と留置線 | 駅出口から東へN3。北は線路終端で歩道にしない。 | 海へ向かう起点。 |
| N3 | 中学生後半 | クロマツ防砂林を蛇行して登る木道 | E26西から入り、右→左のS字で北へF11。深砂は黒マスク。 | 車椅子木道。 |
| F11 | 中学生後半 | 海を見下ろす砂丘頂の風車柵 | N3南から北へ上がり、東へ緩く折れてE27南へ下る。頂上枝は画面内で終える。 | 海は画面上。 |
| E27 | 中学生後半 | 風紋と波打ち際が上側に広がる砂浜 | F11から下側へ入り、上の海は通行不能。横長の締まった砂の帯が主路。 | 風の召喚獣の場。 |

## 小学校への坂

| MAP | 時期 | 一言特徴 | 方位・主路・通行条件 | 暫定固定 |
|---|---|---|---|---|
| N10 | 中学生前半 | 雪の手すりに沿って二度曲がる校門前の長坂 | E13の東出口から入り、東へ出た後に南へ蛇行してE33北の校門へ。石段は置かず、連続した緩勾配と除雪帯を確保。 | 寺町段丘の学校側、車椅子主路。 |

## 能登（被災前・被災後）

同一地点の前後版は、方位・出入口・高低を必ず一致させる。被災後だけ道を増やして地理を変えない。海は常に画面下側。

| MAP | 時期 | 一言特徴 | 方位・主路・通行条件 | 暫定固定 |
|---|---|---|---|---|
| E28 | 幼稚園後半 | 雪で曇る窓と木製座席ののと鉄道車内 | 金沢側ドア→横通路→蛸島側ドア。 | 蛸島へ到着。 |
| E29 | 幼稚園後半 | 車止めの先で線路が終わる蛸島駅 | 駅出口の北側からN5へ。線路北端は終点、東へ道路を出さない。東の茂みの小径（道路ではない）が被災前の廃校の校庭F84へ入る暫定入口（#89。入口MAPと茂みの見せ方は要確認）。 | 鉄道の終点。 |
| N5 | 幼稚園後半 | 海を背に蛇行して上がる漁村坂 | E29北から入り、左→右へ折返しN6南へ。 | 海から離れる上り。 |
| N6 | 幼稚園後半 | 小祠と畑を抱える尾根の横道 | N5南から入り東のN7へ横断。神社枝は画面内終了。 | 海は下端に遠く見える。 |
| N7 | 幼稚園後半 | 船揚げ場の屋根へ蛇行して降りる急坂 | N6西から入り、二度曲がり南のE30へ下る。 | 低地への下り。 |
| E30 | 幼稚園後半 | 黒瓦の実家と海岸道のT字 | N7北から受け、南のE31桟橋へ。西は家の玄関ドア。| 家・海岸の結節。 |
| E31 | 幼稚園後半 | テトラポッド脇へ伸びる短い桟橋 | E30北から入り南の先端で終了。海・テトラは通行不可。 | 事故イベント地点。 |
| F12 | 中学生後半 | 傾いた標識と土砂が残る被災後蛸島駅 | E29と同じ駅出口・線路終端。東の仮設導線からF18へ（被災前はE29東の茂みの小径から廃校の校庭F84へ、#89）。 | E29の被災後版。 |
| F13 | 中学生後半 | 崩れた擁壁を迂回する被災後の上り坂 | N5と同じ南入・北出、折返し位置も同じ。仮設板路が主路。 | N5の被災後版。 |
| F14 | 中学生後半 | 青いシートと折れた杉の尾根 | N6と同じ西入・東出。神社枝は封鎖。 | N6の被災後版。 |
| F15 | 中学生後半 | 地割れを跨ぐ仮設板の下り坂 | N7と同じ北西入・南出。地割れは主路外。 | N7の被災後版。 |
| F16 | 中学生後半 | 壁の欠けた実家と傾いた物干し | E30と同じ北入・南出。家ドアは崩壊で封鎖。 | E30の被災後版。 |
| F17 | 中学生後半 | 壊れた防潮柵の先に残る釣り場 | E31と同じ北入・南終端。先端は立入禁止。 | E31の被災後版。 |
| F18 | 中学生後半 | 給水車と小さな集会所の仮設住宅（廃校の校庭に建つ） | F12東の生活動線から入るL字。集会所ドア以外は行き止まり。被災後の廃校は潰れて入れず、E32への接続は廃止。 | 被災後の安全拠点。潰れた廃校の校庭に作る（#89、kako-jun 2026-10-19）。F84の被災後版。被災前のE29.right→F84.left（茂みの小径）の被災後版がF12東の仮設導線→F18。 |
| E32 | 幼稚園後半 | 窓が抜けた廃校の雪深い中庭（被災前の廃校） | left←F84.right（校庭から地続き）。校舎入口→中庭→体育館ドアの短い主路、崩落棟は封鎖。 | 被災前の廃校（もともと廃墟）。被災後は潰れて入れないためMAPなし（#89、https://github.com/kako-jun/sit-by-me/issues/89#issuecomment-6258788080）。ID据え置き、時期ラベルを被災前へ変更。画像E32.pngは据え置き。 |
| E33 | 中学生前半 | 楕円トラックと鉄棒が雪に埋もれる小学校校庭 | N10北から校門へ入り、校舎・体育館はドア遷移。外周柵は閉鎖。 | 段丘の反対側、車椅子可。 |

## 体内

幼稚園児が想像する現実離れした架空人体の抽象概念。肌色寄りでよく、写実的な臓器・解剖図にしない。口から上半身・下半身へ入り、頭は上、手は左右斜め上各2MAP、足は左右斜め下各3MAPの一本道。脳は迷路、胃・心臓・肺は単純な分岐室。既存の心臓への発火条件を保持し、空間上の枝だけから全枝任意・即座の心臓到達を確定しない。攻略条件・迷路・maskはTBD。

| MAP | 時期 | 一言特徴 | 方位・主路・通行条件 | 暫定固定 |
|---|---|---|---|---|
| F19 | 中3 | 口・体内入口 | door-passage-torso→F74.door-passage-mouth | 上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |
| F20 | 中3 | 左手通路2・末端 | door-passage-base→F77.door-passage-tip | 上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |
| F21 | 中3 | 右手通路2・末端 | door-passage-base→F78.door-passage-tip | 上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |
| F22 | 中3 | 左足通路3・末端 | door-passage-base→F80.door-passage-tip | 上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |
| F23 | 中3 | 右足通路3・末端 | door-passage-base→F82.door-passage-tip | 上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |
| F24 | 中3 | 頭・脳の迷路通路 | door-passage-torso→F74.door-passage-head | 上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |
| F25 | 中3 | 胃・分岐室 | door-passage-torso→F76.door-passage-stomach | 上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |
| F26 | 中3 | 心臓・分岐室 | door-passage-torso→F74.door-passage-heart | 上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |

## K空港・海外

K空港だけがワープ到達点。そこから飛行機で海外へ出た後は日本へ戻れない。海外も冬であり、黄土色の砂漠・熱帯・青空は使わない。乾いた氷、霜、灰褐色、錆赤、青白い長い影を共通基調にする。

| MAP | 時期 | 一言特徴 | 方位・主路・通行条件 | 暫定固定 |
|---|---|---|---|---|
| F39 | 青年前半 | 雪囲いの送迎車線と低い管制塔のK空港外 | ワープ到着広場→東のF40入口。駐機場は通行不能。 | 日本側の唯一のワープ空港。 |
| F40 | 青年前半 | 白い蛍光灯の下で搭乗口へ折れる空港内 | F39からドア、北へ保安検査、東の搭乗ゲートで海外へ遷移。 | 帰路なし。 |
| F27 | 青年後半 | 凍結した滑走路と赤錆の到着ターミナル | 飛行機から西側到着口、東の荒れ地バス停へ。滑走路は通行不能。 | 海外ダンジョン起点。 |
| F28 | 青年後半 | 遠い都市影へ伸びる霜の一本道 | F27西から入り東へ。道は緩く北へ湾曲し、脇の凍った泉で画面内終端。 | 荒れ地A。 |
| F29 | 青年後半 | 風食岩と凍った塩原を回る二重カーブ | F28西から入り、左→右へ蛇行して北東の都市外縁へ。凍結穴は主路外。 | 荒れ地B。 |
| F30 | 青年後半 | 攻略双塔の共通基壇 | door-left→F31.door-base、door-right→F34.door-base、bottom→F29.top | 左右塔は5階建て、雑多な増改築・無駄道・袋小路。左右対称・同一階平面反復を避ける。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| F31 | 青年後半 | 左塔1階・雑居入口 | door-base→F30.door-left、door-up→F66.door-down | 左右塔は5階建て、雑多な増改築・無駄道・袋小路。左右対称・同一階平面反復を避ける。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| F32 | 青年後半 | 左塔3階・配管と混在用途 | door-down→F66.door-up、door-up→F67.door-down | 左右塔は5階建て、雑多な増改築・無駄道・袋小路。左右対称・同一階平面反復を避ける。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| F33 | 青年後半 | 左塔5階・M015魔法のみ有効 | door-down→F67.door-up、door-bridge→F37.door-left | 左右塔は5階建て、雑多な増改築・無駄道・袋小路。左右対称・同一階平面反復を避ける。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| F34 | 青年後半 | 右塔1階・雑居入口 | door-base→F30.door-right、door-up→F68.door-down | 左右塔は5階建て、雑多な増改築・無駄道・袋小路。左右対称・同一階平面反復を避ける。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| F35 | 青年後半 | 右塔3階・増改築の交差路 | door-down→F68.door-up、door-up→F69.door-down | 左右塔は5階建て、雑多な増改築・無駄道・袋小路。左右対称・同一階平面反復を避ける。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| F36 | 青年後半 | 右塔5階・M016アビリティのみ有効 | door-down→F69.door-up、door-bridge→F37.door-right | 左右塔は5階建て、雑多な増改築・無駄道・袋小路。左右対称・同一階平面反復を避ける。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| F37 | 青年後半 | 塔間空中通路・シャー判明と雑魚共闘 | door-left→F33.door-bridge、door-right→F36.door-bridge、door-third→F70.door-bridge | 左右塔は5階建て、雑多な増改築・無駄道・袋小路。左右対称・同一階平面反復を避ける。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| F38 | 青年後半 | 脱出第3塔1階・出口直前S005戦 | door-up→F73.door-down | 5階建て第3塔の下降。各階は攻略塔同程度の面積。宝箱取捨選択、タイマー継続。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |

## 兼六園（最終ダンジョン前半）

兼六園は実在の池・築山・高低差・園路を保ち、8地区の遭遇レイヤーを重ねる自由回遊網。夕方から城の夜へ。接続はv2、地形根拠は調査記録。

| MAP | 時期 | 一言特徴 | 方位・主路・通行条件 | 暫定固定 |
|---|---|---|---|---|
| F41 | 壮年 | 真弓坂側の南西入口 | top→F43.bottom、right→F42.left、bottom→N9.top | 実景地形を維持。池・急段差blocked、通行幅・mask TBD（#45） |
| F42 | 壮年 | 時雨亭・長谷池 | left→F41.right、top→F44.bottom、right→F49.left | 実景地形を維持。池・急段差blocked、通行幅・mask TBD（#45） |
| F43 | 壮年 | 瓢池・夕顔亭・翠滝下段 | bottom→F41.top、right→F44.left、top→F50.bottom | 実景地形を維持。池・急段差blocked、通行幅・mask TBD（#45） |
| F44 | 壮年 | 霞ヶ池西岸・栄螺山 | bottom→F42.top、left→F43.right、top→F45.bottom | 実景地形を維持。池・急段差blocked、通行幅・mask TBD（#45） |
| F45 | 壮年 | 霞ヶ池北岸・ことじ灯籠 | bottom→F44.top、right→F46.left、left→F50.right | 実景地形を維持。池・急段差blocked、通行幅・mask TBD（#45） |
| F46 | 壮年 | 霞ヶ池東岸・唐崎松 | left→F45.right、bottom→F47.top | 実景地形を維持。池・急段差blocked、通行幅・mask TBD（#45） |
| F47 | 壮年 | 曲水・根上松 | top→F46.bottom、bottom→F48.top、left→F49.right | 実景地形を維持。池・急段差blocked、通行幅・mask TBD（#45） |
| F48 | 壮年 | 山崎山・花見橋側 | top→F47.bottom、bottom→F49.top | 実景地形を維持。池・急段差blocked、通行幅・mask TBD（#45） |
| F49 | 壮年 | 梅林側の南周回路 | left→F42.right、right→F47.left、top→F48.bottom | 実景地形を維持。池・急段差blocked、通行幅・mask TBD（#45） |
| F50 | 壮年 | 桂坂口・石川橋 | bottom→F43.top、right→F45.left、top→F51.bottom | 実景地形を維持。池・急段差blocked、通行幅・mask TBD（#45） |

## 金沢城（最終ダンジョン後半）

石川橋はF50北端から城へ。三の丸の西に二の丸、その南の高い本丸。3攻略目標は任意順、最終夜の天守は本丸内の架空上層。

| MAP | 時期 | 一言特徴 | 方位・主路・通行条件 | 暫定固定 |
|---|---|---|---|---|
| F51 | 壮年 | 石川門の枡形 | left→F52.right、bottom→F50.top | 高低差を維持。攻略／門開閉・assist・mask TBD（#45） |
| F52 | 壮年 | 三の丸 | right→F51.left、top→F53.bottom、left→F54.right、bottom→F58.top | 高低差を維持。攻略／門開閉・assist・mask TBD（#45） |
| F53 | 壮年 | 菱櫓・五十間長屋 | bottom→F52.top、door-west→F55.door-hishi、door-south→F54.door-north | 高低差を維持。攻略／門開閉・assist・mask TBD（#45） |
| F54 | 壮年 | 橋爪門・橋爪門続櫓 | right→F52.left、left→F55.right、door-north→F53.door-south | 高低差を維持。攻略／門開閉・assist・mask TBD（#45） |
| F55 | 壮年 | 二の丸 | door-hishi→F53.door-west、right→F54.left、left→F56.right、bottom→F57.top | 高低差を維持。攻略／門開閉・assist・mask TBD（#45） |
| F56 | 壮年 | 低地の玉泉院丸庭園 | right→F55.left | 高低差を維持。攻略／門開閉・assist・mask TBD（#45） |
| F57 | 壮年 | 極楽橋・本丸附段・三十間長屋側 | top→F55.bottom、right→F59.left | 3攻略目標完了後にF59本丸入口を解錠。高低差を維持。攻略／門開閉・assist・mask TBD（#45） |
| F58 | 壮年 | 鶴の丸・東の丸側 | top→F52.bottom、left→F59.right | 3攻略目標完了後にF59本丸入口を解錠。高低差を維持。攻略／門開閉・assist・mask TBD（#45） |
| F59 | 壮年 | 高い本丸 | left→F57.right、right→F58.left、door-tower→F60.door-base | 高低差を維持。攻略／門開閉・assist・mask TBD（#45） |
| F60 | 壮年 | 本丸内のイマジナリー天守上層 | door-base→F59.door-tower | 高低差を維持。攻略／門開閉・assist・mask TBD（#45） |

## 2026-10-18追加ID（番号は既存MAPを移動しない）

| MAP | 時期 | 一言特徴 | 接続 | 不変条件／TBD |
|---|---|---|---|---|
| F61 | 小学生前半 | 八角形エントランス2階・全方向の窓 | door-hotel→F62.door-entry、door-stairs→F07.door-stairs | 2階は全方向の窓。一辺から和室宿泊棟、階段で1階。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| F62 | 小学生前半 | 廃墟の和室が並ぶ宿泊棟 | door-far-end→F63.door-hotel、door-entry→F61.door-hotel | 廃墟の和室が並ぶ。入口2階側と屋外階段側の両端。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| F63 | 小学生前半 | 動物園から宿泊棟端への屋外階段 | door-zoo→F10.door-stairs、door-hotel→F62.door-far-end | ユーザー創作の動物園→宿泊棟端の屋外階段。assist方法TBD。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| F64 | 小学生前半 | ラッコ館・入口と出口のある任意探索 | door-entry→E23.door-otter-in、door-exit→E23.door-otter-out | 入口・出口別。宝箱目当ての任意通り抜け。同じ屋外E23へ戻すのはゲーム配置。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| F65 | 小学生前半 | 低予算昭和の海底探検洞窟・任意探索 | door-entry→E23.door-cave-in、door-exit→E23.door-cave-out | 低予算昭和の海底探検の作り物。ダイオウイカ・難破船・ニンゲン。入口出口別、任意宝箱。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| F66 | 青年後半 | 左塔2階・迷路状の増築 | door-down→F31.door-up、door-up→F32.door-down | 左右塔は5階建て、雑多な増改築・無駄道・袋小路。左右対称・同一階平面反復を避ける。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| F67 | 青年後半 | 左塔4階・無駄道と袋小路 | door-down→F32.door-up、door-up→F33.door-down | 左右塔は5階建て、雑多な増改築・無駄道・袋小路。左右対称・同一階平面反復を避ける。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| F68 | 青年後半 | 右塔2階・混在用途の迷路 | door-down→F34.door-up、door-up→F35.door-down | 左右塔は5階建て、雑多な増改築・無駄道・袋小路。左右対称・同一階平面反復を避ける。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| F69 | 青年後半 | 右塔4階・無駄道と袋小路 | door-down→F35.door-up、door-up→F36.door-down | 左右塔は5階建て、雑多な増改築・無駄道・袋小路。左右対称・同一階平面反復を避ける。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| F70 | 青年後半 | 脱出第3塔5階・宝箱と下り階段 | door-bridge→F37.door-third、door-down→F71.door-up | 5階建て第3塔の下降。各階は攻略塔同程度の面積。宝箱取捨選択、タイマー継続。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| F71 | 青年後半 | 脱出第3塔4階・宝箱と下り階段 | door-up→F70.door-down、door-down→F72.door-up | 5階建て第3塔の下降。各階は攻略塔同程度の面積。宝箱取捨選択、タイマー継続。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| F72 | 青年後半 | 脱出第3塔3階・宝箱と下り階段 | door-up→F71.door-down、door-down→F73.door-up | 5階建て第3塔の下降。各階は攻略塔同程度の面積。宝箱取捨選択、タイマー継続。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |
| F73 | 青年後半 | 脱出第3塔2階・宝箱と下り階段 | door-up→F72.door-down、door-down→F38.door-up | 5階建て第3塔の下降。各階は攻略塔同程度の面積。宝箱取捨選択、タイマー継続。 幅・pixel/mask・階内経路TBD、画像生成blocked。 |

## #74追加ID（胴体・肺）

| MAP | 時期 | 一言特徴 | 接続 | 不変条件／TBD |
|---|---|---|---|---|
| F74 | 中3 | 上半身・胴体上段 | door-passage-mouth→F19.door-passage-torso、door-passage-lower→F76.door-passage-upper、door-passage-head→F24.door-passage-torso、door-passage-left-arm→F77.door-passage-torso、door-passage-right-arm→F78.door-passage-torso、door-passage-heart→F26.door-passage-torso、door-passage-lung→F75.door-passage-torso | 上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |
| F75 | 中3 | 肺・分岐室 | door-passage-torso→F74.door-passage-lung | 上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |

## #74追加ボリューム（上半身・下半身／手2／足3）

| MAP | 時期 | 一言特徴 | 接続 | 不変条件／TBD |
|---|---|---|---|---|
| F76 | 中3 | 下半身・胴体下段 | door-passage-upper→F74.door-passage-lower、door-passage-left-leg→F79.door-passage-torso、door-passage-right-leg→F81.door-passage-torso、door-passage-stomach→F25.door-passage-torso | 上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |
| F77 | 中3 | 左手通路1・付け根側 | door-passage-torso→F74.door-passage-left-arm、door-passage-tip→F20.door-passage-base | 上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |
| F78 | 中3 | 右手通路1・付け根側 | door-passage-torso→F74.door-passage-right-arm、door-passage-tip→F21.door-passage-base | 上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |
| F79 | 中3 | 左足通路1・付け根側 | door-passage-torso→F76.door-passage-left-leg、door-passage-middle→F80.door-passage-base | 上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |
| F80 | 中3 | 左足通路2・中間 | door-passage-base→F79.door-passage-middle、door-passage-tip→F22.door-passage-base | 上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |
| F81 | 中3 | 右足通路1・付け根側 | door-passage-torso→F76.door-passage-right-leg、door-passage-middle→F82.door-passage-base | 上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |
| F82 | 中3 | 右足通路2・中間 | door-passage-base→F81.door-passage-middle、door-passage-tip→F23.door-passage-base | 上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |

## #87/#89追加ID（番号は既存MAPを移動しない）

| MAP | 時期 | 一言特徴 | 接続 | 不変条件／TBD |
|---|---|---|---|---|
| F83 | 幼稚園・壮年 | デパート1階（入口階）。時計のある吹き抜け（アトリオ参照） | door-street→E14.door、door-toys↔E15.door-korinbo、door-restaurant↔E16.door-lobby、door-2f↔F85.door-lower | 詳細は香林坊〜武蔵ヶ辻の表のF83行を正とする（二重管理を避け、ここは索引のみ）。 |
| F85 | 幼稚園・壮年 | デパート2階（隠し階） | door-lower↔F83.door-2f、door-upper↔E15.door-2f（1階・3階から行ける枝。通らなくても本筋は成立） | 詳細は香林坊〜武蔵ヶ辻の表のF85行を正とする（二重管理を避け、ここは索引のみ）。 |
| F86 | 壮年（ラスボス付近） | デパート4階（隠し階・条件つき） | door-lower↔E15.door-4f、door-upper↔E16.door-4f（条件つき） | 詳細は香林坊〜武蔵ヶ辻の表のF86行を正とする（二重管理を避け、ここは索引のみ）。 |
| F84 | 幼稚園後半 | 廃校の校庭（被災前）。F18の被災前版（仮設住宅が建つ前） | left←E29.right（茂みの小径の暫定入口）、right→E32.left | 校庭側の見た目、勝手口等の扉（E10同様）、茂みの見せ方（画面端／獣道）、入口がE29でよいか（比較はmap-topology.md参照）、校庭↔E32は地続きの屋外としてF84.right↔E32.left（辺の選択理由はmap-topology.md）。画像生成blocked。 |
