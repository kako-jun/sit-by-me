# 体内 BDY-01〜06 マスク red-team（mask/adoption・独立検査）

- reviewer: Claude（Sonnet 5.5、独立 red-team サブエージェント。対象の画像・マスク・位置合わせツールの作成者ではない）
- 日付: 2026-10-23 / ステージ宣言: `mask/adoption`（版 = 作業ブランチ body-maps-baseline-20261022、HEAD 2baff2f。採用画像は HEAD でコミット済み・未変更、マスク一式（`assets/images/fields/masks/`）は **未追跡（`??`）でコミット無し**。検査したのは作業ツリーの現物）
- 前提（#142 最新コメント）: 2値のみ（white=通れる=床 / black=それ以外）。壁の帯・面取り・影・地形・土台縁・机・装飾は black。遷移範囲値・runtime 扱い・床と縁の隙間の扱いは TBD。
- 方針: 作成者の register.json の判定・`docs/production/20261022-body-mocks-and-registration.md` の結論は信用せず、原画素から再計測した。ただし rect（模型の天面矩形）は links.json の値を「作成者の定義」として座標の物差しに使い、その妥当性も検査した。

## 1. 検査した版（sha256）

マスク（`assets/images/fields/masks/`）
| ファイル | sha256 |
|---|---|
| BDY-01-mask / traversal-edit | bb18ce549f59b0ed3549568bf647ca2ee20ca4cf60f58f33e6fed7b0ad62b2f7（2ファイル同一） |
| BDY-01-mask-overlay | 5c15d08d53da8a6d9704a745f2ce8ef6a39c4967a12467bd1e14d5d4280d3953 |
| BDY-02-mask / traversal-edit | 3e7a0507c6b220d6afcbbc1bd979836d2e1dd2baeba2148a943b923524a30eb9 |
| BDY-02-mask-overlay | e0f27237f6ecb500be745adef2f61f8738c8ac5131d661977e98c00553de339e |
| BDY-03-mask / traversal-edit | b42d61cac0ef9b8477e1714ecf8b24e3dfe5740ea033193be39c5df811e4ef27 |
| BDY-03-mask-overlay | ede69069157daa58bcf3ed25db24c830a330c1e6c3ab9cc5a4f63d2662694bf1 |
| BDY-04-mask / traversal-edit | b94b886a173c9106c3f517d0e86f6fc81a32a85abaccce294bf94ffb609d8a9c |
| BDY-04-mask-overlay | b21b437369f45e761244d50c42867c0aa6f72be8d29ccd2f6ec861627fc3bca3 |
| BDY-05-mask / traversal-edit | 3f09f507b8f48c7fee6eaf8e6ddd48ff7803397678de72582bf95a08df161a5f |
| BDY-05-mask-overlay | a42a5da3cd093b0baefc29bd53ef2b0e4762b95ba2f890217946e62d269cc5a7 |
| BDY-06-mask / traversal-edit | 86da3864deef8a431c8d3b40e8dc78eeba39c23521757df07c730bf2b18b8091 |
| BDY-06-mask-overlay | 5e1f2643a16cbfea0eb62c7726e92b8b4b47c878b8a106242a00dcf7003d9191 |

採用画像（`assets/images/fields/reference/`）
| ファイル | sha256 |
|---|---|
| body-mouth-bdy01-adopted.webp | 5331efc4c98cb024aa854e0fd8c235179e0adfbf907ad97511e57c1245409441 |
| body-upper-torso-bdy02-adopted.webp | 21b1bf75cc2742de8c9904f3d588639fb5647bb4fa1544c1fe78008ddd93e06b |
| body-lower-torso-bdy03-adopted.webp | 22724fc3a41f13e91a9a0bcaacb0f771d3d2ed9b69863d8e722a96f036f520dc |
| body-brain-maze-bdy04-adopted.webp | 4f441b8cca1106f665c1670decd51008adf8b80e6f5ae485563eff61ae0f3982 |
| body-left-arm-1-bdy05-adopted.webp | e735fd28fd1d99b8935db4f0eb392447870b0c39e014e2465f452a5c5404f317 |
| body-left-arm-2-bdy06-adopted.webp | 612a4e1a899b896ced85799afa34f5cb5962394816f59b1ac312cc8390ab5272 |

## 2. 読んだ正本

`.claude/skills/sit-artifact-redteam/SKILL.md`、`docs/map-topology.md`（118 行の v2 台帳 244〜261 行、686〜692 行）、`verification/body-layout/connections.md`、`docs/production/body-masks/BDY-0{1..6}-links.json`・`-register.json`・`export-report.json`、`docs/production/20261022-body-mocks-and-registration.md`（§4〜§8）、`docs/map-asset-registry.md`（111・112・116・176・183・184 行）、`docs/map-specifications.md`（115〜126・205・212〜213 行）、`docs/map-contract-checklist.md`（75・76・80・140・147・148 行）。

## 3. 検査項目と結果

### 項目1: 寸法・2値・同一・可逆（6枚すべて合格）
- 採用画像・mask・traversal-edit・mask-overlay の全 24 ファイルが 1672x941（PIL）。
- 各 mask のユニーク値は {0,255} の2種のみ。R=G=B（RGBequal True）。
- mask と traversal-edit は全6組でバイト一致（sha256 同一）、`np.array_equal` も True。
- mask の WebP チャンクは全て `VP8L`（可逆）。ただし「元（書き出し前の配列）と一致」はこちらに元が無いので **未検証**（VP8L と再読込の2値性までを確認）。
- white の連結成分は各 mask で 1 個（BDY-01 80,880px / 02 487,296 / 03 421,573 / 04 445,033 / 05 108,329 / 06 102,673）。孤立した white の島は 0。black の連結成分（4近傍）も各 1 個 = 壁が一枚で連続し、white の内部に black の孤島（穴）は無い。

### 項目2: 床と white の一致（床の欠け）
方法: mask の芯（30px 侵食）の Lab 中央値を床色とし、dE 距離で (a) white 内の非床、(b) black 側の床色連結成分を数えた。(a) は全6枚で dE>14 の white が 0px。(b) は下表（dE<8、3x3 opening、white から 4px 以内に接する成分）。この方式は作成者の色クラスタ方式と近い（同一基準で circular な面がある）ため、拡大クロップの目視（§6）で補った。
| MAP | white から接する床色の black 成分 |
|---|---|
| BDY-01 | S 出口の喉 x844-1128,y792-840 = 10,216px（F-01）。右上の丸い先端 x1161-1234,y433-497 = 808px（F-08） |
| BDY-02 | W x128-146,y382-559 = 2,844px（F-02）。S 縁 y801-806 の複数帯 計 約1,800px。N 島の周り x979-1077,y134-172 = 642px（影、定義どおり black） ほか |
| BDY-03 | N 喉 x747-922,y117-129 = 1,682px（F-03）。NE x1394-1539,y139-188 = 609px、SE x1456-1552,y768-801 = 535px（F-09） |
| BDY-04 | 壁の上面の細い帯（y237-240、y551-553、y342-344 等、3〜4px 幅）計 3,790px。壁の面取り上面で black が定義どおり（合格） |
| BDY-05 | 計 23px（無し） |
| BDY-06 | S 縁 x572-858,y795-819 = 1,915px（F-10） |

装飾（毛糸・ボタン・粘土玉・赤紙）の white への食い込み: 全6枚で dE>14 の white=0px、白の島=0。床と同色の装飾の white 側への混入は **なし**。BDY-03 の床色のテープ（x394-476,y318-401 ほか）は black 側で床と非接続。壁側への床の漏れ: なし。

### 項目3: 接続表との整合
- 出口の個数・辺（模型縁から 0〜30px 内側の white 区間を6枚全辺で走査、rt_exit.py）
  - BDY-01: S 1本（x885-1140）のみ。N/E/W は off0〜30 で white 0。
  - BDY-02: N 2本（x769-917 頭 / x1078-1256 口）、E 1本（y238-404）、S 3本（x409-583 肺 / x751-922 下半身 / x1084-1260 心臓）、W 1本（y383-554）。仕様どおり 7 本。
  - BDY-03: N 1本（x748-921）、W 1本（y605-795）、E 2本（y141-326 胃 / y608-794 左足）。S は off0〜20 で white 0（off30 の端は斜め帯の角）。
  - BDY-04: S 1本（x807-866）のみ。
  - BDY-05: N 1本（x530-848）、W 1本（y382-577）。E/S は white 0。
  - BDY-06: S 1本（x613-864 @off5）のみ。N/E/W は white 0。
  - 禁止辺の white: 全6枚で 0。
- ledger 整合: links.json の全16出口の `id`/`partner` が `docs/map-topology.md` 246〜261 行の v2 台帳（16 door 行）と一致（`(id,partner)` または逆順で台帳に存在、16/16）。辺の反対（connections.md）: 01 S↔02 N、02 S↔03 N、02 N（head）↔04 S、02 E↔05 W、05 N↔06 S は全て反対辺。
- 床と縁の隙間（links.json の `floor_gap_to_edge_px`、mask の最初の white 行/列で独立に確認）: 01 S 1（white 最下行 y=798、rect 800）、02 N head 4・mouth 1、02 E 1、02 S 1、02 W **10**（white 開始 x=147、rect x0=137）、03 N **10**（white 開始 y=130、rect 120）、03 E 1、03 W 4、04 S 1、05 N 7、05 W 9、06 S 1。ただし rect 自体が床の実端と合わない箇所がある（F-01・F-02・F-03）。
- BDY-01 の event-mouth: links.json の `events[0].range=null`、「到着位置・向きは原文に無い(TBD)」と記載。辺ではないので mask 側で検査不能。F-07 として TBD 記録。

### 項目4: 迷路・BDY-02・BDY-03
- BDY-04（独立に格子を再構成。作成者の幾何 JSON の格子中心 78 点を register の行列で画像へ写し、中心と中間線の white/black で通路グラフを再導出）:
  - 78 セル中心の 6px 窓は全て white（78/78）。通路 = 隣接セル間 9 点の線が全て white のもの 77 本、残りは中央が black（曖昧 0）。
  - グラフ: 連結成分 1、次数 3（T 字）10、次数 1 は 12 = 行き止まり 11 + 入口セル (6,5)、次数 2 の曲がり 37 + 入口セル(6,5)（隣は (7,5) で入口の南向きと直角 → 曲がり）= 38、閉路なし（78 点・77 辺・連結 = 木、black の連結成分が 1 個で一致）。仕様（曲がり38・T字10・行き止まり11・通路77）と一致。
  - 入口: S 辺に x807-866（幅 61px）の 1 本、他の辺は white 0。入口セル外の white は骨格から 60px 超が 1,616px・1 成分（= 入口の通路 y760-813）のみ。
  - 壁: black は 1 成分（外周と全内壁が連結）、通路が壁を貫通・分断する箇所なし。
  - 通路幅（skeleton 上の 2×距離変換）: 5/25/50/75/95 パーセンタイルが 52/54/56/58.5/65.8 px。F-06（77px 仕様との差）。
- BDY-02: 北辺 2・東 1・南 3・西 1（上記）。首の分岐の形: 行 y=150 は white が x749-921 と x1053-1257 の 2 区間、y=200 では x749-1260 の 1 区間（512px）、y=260 は x748-1235 と x1363-1539。すなわち頭と口は「首 1 本→分岐」でなく、島（x925-1080,y117-175 の壁）を挟んで広間の上端に並ぶ 2 つの開口。F-04。
- BDY-03: 4 出口（N・W・E×2）。V 字くさびの先端: E くさび先端 x1140-1215,y440-480 は white 28.3%、下のくさび頂点 x820-870,y555-600 は 18.4%、先端の細い地形部分は black（行 y=460 の white は x560-1145 で、先端 x>1146 は black）。くさび先端の細い地形は black で合格。

### 項目5: 必須ルート・孤立
- 全6枚で white 連結成分が 1 個（孤立 white 島 0）。全出口と全行き止まり（BDY-04 の 11 袋小路を含む）が同一成分 = 入口から全 white に到達可能。必須ルートを black が塞いでいる箇所なし。
- 作成者の register.json の `holes` / `components` は 1 と一致。

### 項目6: 台帳（docs）
- 全6行が `status=blocked`（`map-contract-checklist.md` 75・76・80・140・147・148 行）。ready にしてよいか: **不可**（理由は §5）。
- 矛盾・古い記述:
  - checklist 75・76・80・147・148 行の列「未生成・mask未作成」は、マスク作成後は事実と食い違う（F-11）。
  - checklist 140 行（BDY-02）の「先行previewはユーザー却下…正本未保存・mask未作成。再生成前に配置モックが必要」は、採用済み画像（registry 176 行）と矛盾（F-11）。
  - registry 111・112・116・176・183・184、specifications 119・120・124・212・213 行に「pixel/maskはTBD（mask未作成）」の文言が残る（F-11）。
  - BDY-04 の仕様幅「約77px」（registry 116 / specifications 124）と mask の実通路幅（F-06）。
  - 作成者ドキュメント §6 は「出口の隙間: BDY-02 W 10px…」と記す。これは rect 基準の隙間で、実際の床端からは 20px の欠け（F-02）。

### 項目7: 沈黙された欠落
- links.json の出口 ID は全て台帳と一致（項目3）。`ratio` は `(a_px − rect原点)/rect寸法` と全16出口で 2e-3 以内に一致（`image_range.a_ratio/b_ratio` を再計算）。`width_px = b−a+1` も一致。座標系の混在なし（px=画像px、ratio=天面比 0〜1）。
- 画像サイズ: 1672x941 全一致（項目1）。BDY-13 は対象外。
- 作成者が自己申告していない問題: F-01・F-02・F-03・F-04・F-08・F-09・F-10（下記）。

## 4. Findings

分類: blocker / major / minor / note。blocker は 0。

| ID | 分類 | MAP | 内容・証拠（座標・画素数） | 修正先 |
|---|---|---|---|---|
| F-01 | major | BDY-01 | S 出口の喉で床が white に入っていない。採用画像では床がコルゲート帯の切れ目（x≈843〜1131）を通って土台縁まで連続しているが、mask の white は y=798 で終わる（rect y1=800）。床色の black 成分 x844-1128,y792-840 = 10,216px（約40px 厚）。クロップ `crop_01_S_exit.png`。出口が模型の縁に届かず、遷移範囲の判定（辺上）に届かない恐れ。rect（波形の内側）が床の実端でなく定義が合っていない | `BDY-01-mask.webp`/`traversal-edit.webp` を再作成。出口の喉まで床を white に延ばす（延ばす範囲は縁か土台縁手前かを kako-jun と決め、TBD を registry 行に記入）。再 red-team |
| F-02 | major | BDY-02 | W 出口（右腕）で床の実端が mask より 20px 外側。画像の床は x≈127 から、mask の white は x=147 から。床色の black 成分 x128-146,y382-559 = 2,844px（上縁にも y372-381 の細い欠け）。作成者の隙間 10px は rect x0=137 基準で、rect 自体が床の実端（約127）より 10px 内側。クロップ `crop_02_W_strip.png` | BDY-02 mask 再作成。links.json `floor_gap_to_edge_px` と rect を実端基準へ再測定 |
| F-03 | major | BDY-03 | N 出口の喉で床が white に入っていない。床は y≈115 から、mask は y=130 から。床色の black 成分 x747-922,y117-129 = 1,682px。クロップ `crop_03_N_exit.png`。（床と縁の隙間 10px は作成者が自認するが、実際は床が存在するのに black） | BDY-03 mask 再作成（F-01 と同処置） |
| F-04 | major | BDY-02 | 契約「首は広間から1本、上で頭（北）と口（北東）に分岐」が採用画像・mask の形と合わない。y=200 の white は x749-1260 の 1 区間（512px）で首の狭まりが無く、頭と口の開口は島（x925-1080,y117-175）を挟んで広間の上端に並ぶだけ。mask は画像の床を忠実に写しており mask の欠陥ではなく画像・契約の食い違い（`map-topology.md` 690 行の BDY-02 作画契約、`connections.md`）。画像は kako-jun 採用済みだが台帳の文言と未整合 | 契約文言を画像の実形へ合わせるか、採用判断を kako-jun が再確認（`map-topology.md` 690 行・`map-specifications.md` BDY-02 行）。mask は変更不要 |
| F-05 | minor | BDY-02/03/06 ほか | 出口付近の床端の細い欠け: BDY-02 S 縁 y801-806（5〜6px 帯・複数、計約1,800px）、BDY-06 S x572-858,y795-819（1,915px、5〜8px 帯）、BDY-03 NE 609px・SE 535px（壁際の 10〜12px 帯、`crop_03_SE_tip.png`）、BDY-02 N 頭の喉の上端がギザ（y=135 で white が x769-791・812-879・896-902 のみ。y=150 で x749-921）。遷移範囲が縁の辺上で判定される前提では到達に影響しうる | 各 mask の喉付近を縁まで延ばす際に同時に直す（F-01〜03 と同じ処置） |
| F-06 | minor | BDY-04 | 通路幅が仕様より細い。mask の幅 5/50/95 パーセンタイル 52/56/65.8px、入口 61px。仕様「約77px」（1920基準。画像倍率 0.8613 で約66px）に対し中央値で約10px（約15%）細い。作成者は影の帯 8〜10px を black にしたためと説明。決定どおりの black で正しいが仕様値との差は台帳に未記録 | `map-specifications.md` 124 行・`map-asset-registry.md` 116 行に「mask 実幅 約56px（影を除いた床）」を注記 |
| F-07 | minor | BDY-01 | `BDY-01.event-mouth`（TRM-01 からの一方向イベント）の到着位置・向き・範囲が無い（links.json `range=null`、TBD）。mask からは検査不能 | `map-asset-registry.md` 111 行に TBD 明記 |
| F-08 | minor | BDY-01 | 右上の丸い先端 x1161-1234,y433-497 の曲線沿いで white の縁が床端より約 7〜12px 内側（808px）。`crop_01_RTend.png` | BDY-01 mask 再作成時に同時修正 |
| F-09 | note | BDY-03 | E くさび・下のくさび・島の先端の細い地形は black（合格）。SE 端の斜め帯の床端（x1456-1552,y768-801、535px）に壁際 10〜12px の欠け。F-05 に集約 | — |
| F-10 | note | BDY-04 | 壁の面取り上面（y237-240、y551-553、y342-344 の 3〜4px 帯、計3,790px）は床色で black。定義（面取りは black）どおりなので不具合ではないが、壁の上面と床の境界の判断は人の判断に依存する | 記録のみ |
| F-11 | minor | 台帳 | 6行とも mask 作成後の文言が未更新（「mask未作成」）。checklist 140 行 BDY-02 が採用済みと矛盾（「ユーザー却下・正本未保存」）。registry/specifications に「pixel/maskはTBD」が残存。status は blocked のまま | `map-contract-checklist.md` 75・76・80・140・147・148 行、`map-asset-registry.md` 111・112・116・176・183・184 行、`map-specifications.md` 119・120・124・212・213 行を、「mask 作成済み（未コミット）・red-team 結果・blocked 理由=遷移範囲TBD・F-01〜04」へ更新 |
| F-12 | note | 全体 | mask 6セットが未追跡でコミットが無い。「検査した版」を commit hash で固定できない（SKILL.md の要件）。可逆 WebP の「元との一致」も元配列が無く未検証 | コミット後に hash を本書へ追記 |

## 5. MAP別判定表

「ready 可」は mask ステージ限定の意見。台帳の status は変更しない。全6 MAP とも、遷移範囲値・runtime 扱い・床と縁の隙間の扱い（TBD）が未決のため **現時点で台帳を ready にしてはならない**（blocked 維持）。

| MAP | mask 判定 | 理由 |
|---|---|---|
| BDY-01 | 不可 | F-01（出口の喉 10,216px の床が black）、F-08、F-07（event-mouth TBD）。他（2値・同一・出口1本・禁止辺0・連結1）は合格 |
| BDY-02 | 不可 | F-02（W 床 20px 欠け 2,844px）、F-04（首の分岐が画像と契約で不一致）、F-05。出口 7 本・禁止辺 0・連結 1 は合格 |
| BDY-03 | 不可 | F-03（N 喉 1,682px の床が black）、F-05。出口 4 本・くさび先端 black・連結 1 は合格 |
| BDY-04 | 可（mask のみ。TBD 解消後） | 迷路 78 セル・77 通路・行き止まり11・T字10・曲がり38・閉路 0・連結 1、入口 S 1 本、壁 black 連続を独立再構成で確認。残りは F-06（幅の注記）・F-10（記録）のみ |
| BDY-05 | 可（mask のみ。TBD 解消後） | 出口 N・W の 2 本、禁止辺 0、床色の欠け 23px。隙間 N 7px・W 9px は TBD（隙間の扱い）に依存 |
| BDY-06 | 可（mask のみ。TBD 解消後・F-05 を直せばなお良い） | 出口 S 1 本、禁止辺 0。S 縁に 5〜8px 帯の欠け（1,915px）は minor |

総括: 6 枚とも 2 値・同一・可逆・連結 1・禁止辺 0・出口の個数と ID は合格で、blocker は無い。major は BDY-01・02・03 の「出口の喉まで床が white に届かない」（F-01〜03、床 10,216／2,844／1,682px）と、BDY-02 の首の形の契約不一致（F-04）。いずれも作成者の rect（波形の内側）が実際の床端より 10〜40px 内側にあることが共通の原因で、遷移範囲が縁の辺上で判定されるなら出口に届かない恐れがある。修正後に BDY-01〜03 は新しい red-team を受けること。BDY-04〜06 は mask として合格水準。status は blocked のまま（遷移範囲の TBD と F-11 の台帳更新が先）。

## 6. 使ったコマンド・クロップ

作業ディレクトリ: `/tmp/claude-1001/-home-kako-jun-repos-private-freeza/aa5acb76-b5dd-4655-b198-ef71c171c671/scratchpad/rt/`（実行は `uv run --with pillow --with numpy --with scipy --with scikit-image python3 -I <script>`）

- `rt_floor.py`: 床色（Lab 中央値）距離による white/black の突合、`rt_adj.py`: white に接する床色成分の列挙、`rt_exit.py`: 4辺の縁から 0〜30px 内側の white 区間・成分数、`rt_maze.py`: BDY-04 の 78 セルの再構成、`rt_misc.py`: BDY-02 首・BDY-03 くさび・BDY-04 通路幅、`crop.py`: 拡大クロップ。
- sha256: `sha256sum assets/images/fields/masks/BDY-0[1-6]-* assets/images/fields/reference/body-*-bdy0[1-6]-adopted.webp`
- 全体オーバーレイ（緑=white、赤線=境界）: `rt/ov01.png`〜`rt/ov06.png`
- 拡大クロップ（左=原画素、右=mask 境界）: `rt/crop_01_S_exit.png`（F-01）、`rt/crop_02_W_strip.png`（F-02）、`rt/crop_03_N_exit.png`（F-03）、`rt/crop_02_N_island.png`、`rt/crop_02_S_edge.png`、`rt/crop_01_RTend.png`（F-08）、`rt/crop_03_NE.png`、`rt/crop_03_SE_tip.png`（F-05/F-09）、`rt/crop_06_S_exit.png`（F-05）、`rt/crop_02_mid.png`
- dE 画像: `rt/dE01.png`〜`rt/dE05.png`

## 7. 検査しなかったこと（後ステージ）

- runtime の遷移判定（範囲値・TBD）、実機での歩行確認、車椅子区分（2値決定で不要）、BDY-07〜17。
- 「元の mask 配列との可逆一致」（元が手元に無い）。
- 作成者以外の第二の床境界の定義（本書は色距離と目視。壁の足元の最終判断は kako-jun）。
