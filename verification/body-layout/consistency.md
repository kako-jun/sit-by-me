# 体内 BDY-01..17 配置モック 整合表（自動生成）

画像 1920x1080 / 模型の天面 1644x804（余白: 机90px + 土台の縁の帯48px=foamboard28+corrugated断面20）/ 主路幅 230px（模型幅比 0.14、『キャラクター3人が横に並べる幅』の仮置き。数値はTBD）

**手足は斜めに伸びる道**（kako-jun 確定。原文: 胴体を真ん中として頭は上方向に、両手は右上、左上方向に、足は右下、左下方向に、一本道の通路としてかけばいい）。通路は模型の縁まで届く（画像端ではない）。遷移位置は辺上の範囲（図の着色帯、奥行60px。斜めの帯は縁との交わり区間）。BDY-02 は広間（壁で縁取った横長の楕円の床）から首が1本北へ伸び、上で頭（真北）と口（右上へ斜め→北辺に垂直）に分かれる形（kako-jun 決定 #142『首は A案』。旧版は首が見えない床の塊だったため作り直し）。

辺は body.svg の方位から導いた**提案**（原文に辺の指定は無い）。形は body_layout.py の SPECS。保留4枚（BDY-04/15/16/17）は入口の辺と位置が確定、内部は『仮案』（脳=迷路・胃=分岐なしJ字の1袋・心臓=2x2の4部屋の環・肺=5部屋。部屋名は注記のみ・絵には描かない）。

**BDY-17（肺）は2案を併記**（kako-jun 指示 2026-10-22『肺は左右の中心に上から入るように、通路をキャラ１人分の幅で左から上にぐるっとまわしては』。解釈が2通り）: 仮案A=外周を回る環（既定。BDY-17.png）／仮案B=渦巻き（BDY-17-B.png）。入口は北辺の左右中心（x=画像中心）の1本、通路幅はキャラ1人分=主路幅の1/3（約77px）、右3葉・左2葉の丸い5部屋。入口の帯の幅（1人幅か3人幅か）は原文に無く**要確認**。BDY-02 側の肺の出口は東辺から南辺へ移した（東辺は左腕のみ・西辺は右腕のみ。南辺は肺・下半身・心臓の3本）。**左右は身体の本人から見る**（kako-jun 決定 #142 2026-10-22『本人は仰向け、それを正面から見ている。画面左側は右手』）: 西辺=右腕・東辺=左腕・左足=画面右下・右足=画面左下。**心臓・肺の左右は確定**: 心臓は本人の左側=画面右（南辺 x≈1239–1469）、肺=画面左（x≈450–680）。

**BDY-15（胃）は kako-jun 指摘『なぜ胃が2つに分岐したようになってるのだ？人間はそうなのか？』で作り直し**: 旧図は胃底を横へ伸びる行き止まりの枝にして『噴門→胃底(枝)と胃体→幽門』と分岐させていた(区分の名前から枝を作った誤り)。新図は分岐なしJ字の1つの袋: 入口(西・噴門)のすぐ上の丸いドーム=胃底(袋の一部)→袋の本体=胃体(最大幅460px=入口230pxの2倍)→右へ曲がって細く(幽門130px)→丸く閉じた行き止まり。曲がり2・T字0・行き止まり1・入口1本。部屋名は注記のみ。形は SAC15(中心線の制御点＋半径の掃引)。

## 機械検査

- OK C1 map-topology.md の door 16行 == body.svg の door 16本 (16 vs 16)
- OK C2 全接続で両端の辺が反対 (16/16)
- OK C3 各MAPの描画通路 == 接続表のport集合 (MAP数=17)
- OK C4 BDY-01..17 を全て生成 (17)
- OK C5 BDY-02 の通路は7本のみ (7)
- OK C6 同一辺の通路帯（斜めは縁との交わり区間）が重ならない (主路幅230px)
- OK C8 手足・口・下半身の枝の道は斜め（水平・垂直から15度以上）。区間16本 (最小/最大(水平からの度) 17.5/62.0)
- OK C14 太ももの折れ点=1（関節は膝の1つ・区間2本）・折れ角（進行方向の変化）30〜45度以内（内角135度以上の鈍角・2区間とも同じ側へ進む）・道の長さ >= 旧直線 (BDY-09: 折れ点1・区間2・折れ角（進行方向の変化）35.1度・内角144.9度・中心線919px・旧直線830px（入口0.35→出口0.392）の1.11倍; BDY-12: 折れ点1・区間2・折れ角（進行方向の変化）35.1度・内角144.9度・中心線919px・旧直線830px（入口0.35→出口0.392）の1.11倍)
- OK C9 丸い末端・合流点の円が模型の天面に収まる (問題なし)
- OK P1 BDY-04 部屋数0・曲がり38・T字分岐10・行き止まり11 (実測 部屋0・曲がり38・T字10・行き止まり11)
- OK P2 BDY-04 入口は1本だけ（接続表のport数） (port頂点1)
- OK P3 BDY-04 道幅77px（キャラ1人分=主路幅1/3）で全通路に適用、部屋の直径は道幅より大きい (道幅77px 全通路一定)
- OK P4 BDY-04 床が模型の天面に収まり、入口以外の縁に20px以上の余白を残す (問題なし)
- OK P5 BDY-04 関連しない通路・部屋どうしの壁(隙間)が20px以上 (最小の隙間 43px)
- OK P1 BDY-15 部屋数4・曲がり2・T字分岐0・行き止まり1 (実測 部屋4・曲がり2・T字0・行き止まり1)
- OK P2 BDY-15 入口は1本だけ（接続表のport数） (port頂点1)
- OK P3 BDY-15 道幅: 入口230px・袋の最大幅464px(入口の1.8〜2.1倍)・先端(幽門)130px(115〜150)・最小幅130px>=キャラ1人分77px (最小130・最大464・先端130)
- OK P4 BDY-15 袋が模型の天面に収まり、入口以外の縁に15px以上の余白（床の最小 x=0, y=15, 右端 1455, 下端 780） (縁に出る床 0画素)
- OK P5 BDY-15 床が一連結（1つの袋・離れた島なし） (床 64369 / 連結 64369（3px間引き）)
- OK P1 BDY-16 部屋数4・曲がり3・T字分岐1・行き止まり0 (実測 部屋4・曲がり3・T字1・行き止まり0)
- OK P2 BDY-16 入口は1本だけ（接続表のport数） (port頂点1)
- OK P3 BDY-16 道幅230px（3人並び=主路幅）で全通路に適用、部屋の直径は道幅より大きい (道幅230px 全通路一定)
- OK P4 BDY-16 床が模型の天面に収まり、入口以外の縁に20px以上の余白を残す (問題なし)
- OK P5 BDY-16 関連しない通路・部屋どうしの壁(隙間)が20px以上 (最小の隙間 194px)
- OK P1 BDY-17案A 部屋数5・曲がり4・T字分岐1・行き止まり0 (実測 部屋5・曲がり4・T字1・行き止まり0)
- OK P2 BDY-17案A 入口は1本だけ（接続表のport数） (port頂点1)
- OK P3 BDY-17案A 道幅77px（キャラ1人分=主路幅1/3）で全通路に適用、部屋の直径は道幅より大きい (道幅77px 全通路一定)
- OK P4 BDY-17案A 床が模型の天面に収まり、入口以外の縁に20px以上の余白を残す (問題なし)
- OK P5 BDY-17案A 関連しない通路・部屋どうしの壁(隙間)が20px以上 (最小の隙間 165px)
- OK P1 BDY-17案B 部屋数5・曲がり7・T字分岐0・行き止まり1 (実測 部屋5・曲がり7・T字0・行き止まり1)
- OK P2 BDY-17案B 入口は1本だけ（接続表のport数） (port頂点1)
- OK P3 BDY-17案B 道幅77px（キャラ1人分=主路幅1/3）で全通路に適用、部屋の直径は道幅より大きい (道幅77px 全通路一定)
- OK P4 BDY-17案B 床が模型の天面に収まり、入口以外の縁に20px以上の余白を残す (問題なし)
- OK P5 BDY-17案B 関連しない通路・部屋どうしの壁(隙間)が20px以上 (最小の隙間 63px)
- OK P7 BDY-04 迷路の複雑さ: 曲がり>=20・T字>=8・行き止まり>=10（seed=433、入口から最奥まで 65区間） (曲がり38・T字10・行き止まり11・道は木構造(ループなし): 辺数77=セル数78-1)
- OK P6 BDY-17案A 入口は北辺の左右中心(x=画像中心960)の1本 (辺N x=960.0)
- OK P6 BDY-17案B 入口は北辺の左右中心(x=画像中心960)の1本 (辺N x=960.0)
- OK C2b 各MAPの図の辺・port集合 == 接続表+body.svg 由来の辺 (BDY-02 以外の全port一致)
- OK C10 BDY-02 の7本の辺と隣接MAPの入口が矛盾しない（全て反対辺） (7/7 (mouth:N, lower:S, head:N, left-arm:E, right-arm:W, heart:S, lung:S))
- OK C11 BDY-02 首は1本: 分岐点より下(y=450..472, 23行)で x=960 を通る北向きの道が1本・幅230px (23行すべて一致)
- OK C12 BDY-02 分岐: 分岐点が広間の壁と北辺の間・北辺の床は頭と口の2本・頭=真北・口=右上へ斜め(水平から15度以上) (J=y350(壁の上端y473、北辺y138)、北辺の床2本[(845, 1075), (1239, 1469)]、口の斜めは水平から17.6度)
- OK C13 BDY-02 広間の壁（壁色）が見える弧の数（参考。帯が接する所以外に壁が残る） (4か所)
- OK P8 BDY-04 迷路の画素検査: 全77区間の通路幅が77px一定・壁の最小厚>=38.5px・床も地形も一連結（通路どうしが接触せずループなし） (通路幅 78〜78px、壁の最小厚 42px、地形の成分1・床の成分1、入口から最奥まで 65区間・中心線の長さ 7902px、曲がり38・T字10・行き止まり11、seed=433)
- OK C7 描画画素: 模型の縁の床帯位置・幅が仕様と一致、他の辺に漏れ無し、模型の外(土台の縁・机・画像端)に床なし、縁に届く、広間は床に収まる (問題なし)

## BDY-04 迷路の生成規則（kako-jun 指示 #142 2026-10-22『脳もキャラ１人分の幅でもっと複雑にして』）

- 通路幅 77px（=主路幅230pxの1/3、BDY-17 の mlw と同じ扱い）。入口は南辺中央の1本のまま（BDY-02 の頭の出口から）、出口なし。
- 格子 13列x6行・ピッチ120px（隣り合う通路の壁 = 120-77 = 43px >= 通路幅の半分）、左上セル中心=模型の天面の(102,102)、縁から通路の縁まで 64px の余白。
- 生成: 入口の真上のセル（列6・行5）から Python `random.Random(seed)` で深さ優先の全域木（未訪問の隣セルを `rnd.choice`、袋小路で戻る）。全78セルを1回ずつ通る木＝ループなし（正解の道は1つ）。
- seed 選択: seed 0..599 のうち 曲がり>=20・T字>=8・行き止まり>=10 を満たし、入口から最も遠い行き止まりまでの道が最長のもの = **seed 433**（決定的）。
- 結果: 曲がり38・T字10・行き止まり11・入口から最奥まで65区間（中心線 7902px）・壁の最小厚 42px・通路幅 78〜78px。行き止まりは丸い閉じた端、折れ点も丸い。

## 段差検査（全17枚+17-B の clean 画素。body_step_scan.py）

18枚すべて 段差 0 件（床の輪郭の短い水平/垂直の辺で前後が逆向きに約90度曲がる Z 形の食い違いなし。縁に触れる辺は除く）。

## 全接続の両端の辺（出る辺 / 入る辺）

| 出る側 | 出る辺 | 入る側 | 入る辺 | 反対か |
|---|---|---|---|---|
| BDY-01.door-passage-torso | S | BDY-02.door-passage-mouth | N | OK |
| BDY-02.door-passage-lower | S | BDY-03.door-passage-upper | N | OK |
| BDY-02.door-passage-head | N | BDY-04.door-passage-torso | S | OK |
| BDY-02.door-passage-left-arm | E | BDY-05.door-passage-torso | W | OK |
| BDY-05.door-passage-tip | N | BDY-06.door-passage-base | S | OK |
| BDY-02.door-passage-right-arm | W | BDY-07.door-passage-torso | E | OK |
| BDY-07.door-passage-tip | N | BDY-08.door-passage-base | S | OK |
| BDY-03.door-passage-left-leg | E | BDY-09.door-passage-torso | W | OK |
| BDY-09.door-passage-middle | S | BDY-10.door-passage-base | N | OK |
| BDY-10.door-passage-tip | S | BDY-11.door-passage-base | N | OK |
| BDY-03.door-passage-right-leg | W | BDY-12.door-passage-torso | E | OK |
| BDY-12.door-passage-middle | S | BDY-13.door-passage-base | N | OK |
| BDY-13.door-passage-tip | S | BDY-14.door-passage-base | N | OK |
| BDY-03.door-passage-stomach | E | BDY-15.door-passage-torso | W | OK |
| BDY-02.door-passage-heart | S | BDY-16.door-passage-torso | N | OK |
| BDY-02.door-passage-lung | S | BDY-17.door-passage-torso | N | OK |

## event（辺ではない）

| TRM-01.event-kiss | BDY-01.event-mouth | 一方向。到着位置・向きは原文に無い(TBD)。BDY-01 の図には印だけ |

## MAPごとの通路

| MAP | 辺 | port | 相手 | 辺上の位置(提案、模型の辺に対する比) |
|---|---|---|---|---|
| BDY-01 | S | door-passage-torso | BDY-02.door-passage-mouth | 0.600 |
| BDY-02 | N | door-passage-head | BDY-04.door-passage-torso | 0.500 |
| BDY-02 | N | door-passage-mouth | BDY-01.door-passage-torso | 0.740 |
| BDY-02 | E | door-passage-left-arm | BDY-05.door-passage-torso | 0.280 |
| BDY-02 | S | door-passage-lung | BDY-17.door-passage-torso | 0.260 |
| BDY-02 | S | door-passage-lower | BDY-03.door-passage-upper | 0.500 |
| BDY-02 | S | door-passage-heart | BDY-16.door-passage-torso | 0.740 |
| BDY-02 | W | door-passage-right-arm | BDY-07.door-passage-torso | 0.500 |
| BDY-03 | N | door-passage-upper | BDY-02.door-passage-lower | 0.500 |
| BDY-03 | E | door-passage-stomach | BDY-15.door-passage-torso | 0.162 |
| BDY-03 | E | door-passage-left-leg | BDY-09.door-passage-torso | 0.820 |
| BDY-03 | W | door-passage-right-leg | BDY-12.door-passage-torso | 0.820 |
| BDY-04 | S | door-passage-torso | BDY-02.door-passage-head | 0.500 |
| BDY-05 | N | door-passage-tip | BDY-06.door-passage-base | 0.392 |
| BDY-05 | W | door-passage-torso | BDY-02.door-passage-left-arm | 0.500 |
| BDY-06 | S | door-passage-base | BDY-05.door-passage-tip | 0.392 |
| BDY-07 | N | door-passage-tip | BDY-08.door-passage-base | 0.608 |
| BDY-07 | E | door-passage-torso | BDY-02.door-passage-right-arm | 0.500 |
| BDY-08 | S | door-passage-base | BDY-07.door-passage-tip | 0.608 |
| BDY-09 | S | door-passage-middle | BDY-10.door-passage-base | 0.407 |
| BDY-09 | W | door-passage-torso | BDY-03.door-passage-left-leg | 0.292 |
| BDY-10 | N | door-passage-base | BDY-09.door-passage-middle | 0.392 |
| BDY-10 | S | door-passage-tip | BDY-11.door-passage-base | 0.700 |
| BDY-11 | N | door-passage-base | BDY-10.door-passage-tip | 0.700 |
| BDY-12 | E | door-passage-torso | BDY-03.door-passage-right-leg | 0.292 |
| BDY-12 | S | door-passage-middle | BDY-13.door-passage-base | 0.593 |
| BDY-13 | N | door-passage-base | BDY-12.door-passage-middle | 0.608 |
| BDY-13 | S | door-passage-tip | BDY-14.door-passage-base | 0.300 |
| BDY-14 | N | door-passage-base | BDY-13.door-passage-tip | 0.300 |
| BDY-15 | W | door-passage-torso | BDY-03.door-passage-stomach | 0.162 |
| BDY-16 | N | door-passage-torso | BDY-02.door-passage-heart | 0.260 |
| BDY-17 | N | door-passage-torso | BDY-02.door-passage-lung | 0.500 |
