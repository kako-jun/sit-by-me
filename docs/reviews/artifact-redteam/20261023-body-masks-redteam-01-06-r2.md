# 体内 BDY-01〜06 マスク red-team 第2回（修正後の版・独立検査）

- reviewer: Claude（Sonnet 5.5、独立 red-team サブエージェント。マスクの作成者でも前回 red-team の担当でもない）
- 日付: 2026-10-23 / ステージ宣言: `mask/adoption`（版 = ブランチ body-maps-baseline-20261022、HEAD 2baff2fce8a0。マスク・links/register は**未追跡（`??`）でコミット無し**。作業ツリーの現物を検査）
- 前回報告: `docs/reviews/artifact-redteam/20261023-body-masks-redteam-01-06.md`（major F-01 BDY-01 南出口の喉、F-02 BDY-02 西、F-03 BDY-03 北）。本書はその修正確認と退行検査。作成者の自己評価は使わず、原画素・マスク画素から再計測した（rect は links.json の値を座標の物差しとして使用）。
- 前提: 2値のみ（white=通れる床 / black=それ以外）。壁の帯・面取り・影・地形・土台縁・装飾は black。遷移範囲値・runtime 扱い・床と縁の隙間の扱いは TBD（#142）。

## 1. 検査した版（sha256）

マスク（`assets/images/fields/masks/`、mask と traversal-edit は各組で同一）
| ファイル | sha256 |
|---|---|
| BDY-01-mask / traversal-edit | e6c61e33e5c5d089403113149c2b97abdfc3b6e60fda86d31a4b04bf12bcf456 |
| BDY-01-mask-overlay | 4494547cc04ed139a9b0a280c5a2641afdf497c5552b6f9799df4558c6df9ff0 |
| BDY-02-mask / traversal-edit | b5ecc245788466bbb26ff22fcd4719388a48cc393880663361384fe1cce9ed67 |
| BDY-02-mask-overlay | 2b0e6ce7c5f1491f2656c7b0b4d218351a99135f01e16b7e8a897144ed875a92 |
| BDY-03-mask / traversal-edit | 57028f4448e13b7dada0a4ad2a15a85e04da8463e43f19ad5561de3ac433d954 |
| BDY-03-mask-overlay | 50d2d192c65523f1f473dd009555eef663ca3a7a382c138fde583d2309e4b1cc |
| BDY-04-mask / traversal-edit | 22bad1523b23a19fbb95d73d0755f20ad3b4019978bdd551e6544be5c2df7aea |
| BDY-04-mask-overlay | 502e88ca0d884e10542f64da20a8bcdcf5a7676f7f4fd22853268d03b64e6f2c |
| BDY-05-mask / traversal-edit | 761a435439f41faf013a5b49a3ced26d581c1fffe748809e175c36044b987c33 |
| BDY-05-mask-overlay | fc3e28ba1ab837a5bf3911994dce5505006361f716134d53d16bbf22e9c125de |
| BDY-06-mask / traversal-edit | 6152710b37ebfd40dcced76270bfcfb6018491eb28479b56381823f26140b8f8 |
| BDY-06-mask-overlay | 29b18285c03c7f54c7f80005fdfae8e44105ed19564294093857eac9212784c3 |

採用画像（`assets/images/fields/reference/`、前回と同一ハッシュ = 画像は未変更）
| ファイル | sha256 |
|---|---|
| body-mouth-bdy01-adopted.webp | 5331efc4c98cb024aa854e0fd8c235179e0adfbf907ad97511e57c1245409441 |
| body-upper-torso-bdy02-adopted.webp | 21b1bf75cc2742de8c9904f3d588639fb5647bb4fa1544c1fe78008ddd93e06b |
| body-lower-torso-bdy03-adopted.webp | 22724fc3a41f13e91a9a0bcaacb0f771d3d2ed9b69863d8e722a96f036f520dc |
| body-brain-maze-bdy04-adopted.webp | 4f441b8cca1106f665c1670decd51008adf8b80e6f5ae485563eff61ae0f3982 |
| body-left-arm-1-bdy05-adopted.webp | e735fd28fd1d99b8935db4f0eb392447870b0c39e014e2465f452a5c5404f317 |
| body-left-arm-2-bdy06-adopted.webp | 612a4e1a899b896ced85799afa34f5cb5962394816f59b1ac312cc8390ab5272 |

links / register（`docs/production/body-masks/`）
| ファイル | sha256 |
|---|---|
| BDY-01-links / -register | 6a79e4abac17a62a3ee7f3a6087c1dece064b0b2be8cd9dad56d2d7ae71cb2ec / d8a5cc6881a062dce38d6a3ee1948b5f111f17f327da7befd8afc7ddbf8e6101 |
| BDY-02-links / -register | f1c0e7c95e51d265212a106c55baa0aa565901297942ba0d01f85ae7d4713013 / 8b32a5dcf7a5ee6643f50e69e3c91e9ba73ad339a7ff6f3099e50f371b4a8df0 |
| BDY-03-links / -register | 5a742a406fcc4c088e55fd7501187831f2c890e26afd14c87a1d7dcdb50a97fa / cf03dab363cdf56ed3a1a9b808fbc035ac2b42bf70edd8a8eca52df7b7423f47 |
| BDY-04-links / -register | 9c83f6ecfb921b819e82e646f1849545566742ba0792d4f3c9f5dfc29f520f07 / 0e6ab0dddb12e04293a3b8724ed638ef4ec3cfb064927a30cb2fbeff3fab48b7 |
| BDY-05-links / -register | da438d2d593884b0b1c6ae2b5c891453644d6361674773db8becaef918acf0ec / 03ed38584100dca7efa189587e0dc2626df33c0b99aa30088d67d0a0c717bd79 |
| BDY-06-links / -register | 5de0c722cd0e30c4873d6cd639e6294b9e62efffb96e2459788716180466b500 / 60493cb5ae69e293184fc24b5a4e11ee488c21d0d6b8eb22ae6768ed1b574b83 |

## 2. 前回 major の修正確認（原画素）

| 前回 | 結果 | 証拠 |
|---|---|---|
| F-01 BDY-01 南の喉 | **解消**。white が床を通って模型前縁まで届く | 前回 10,216px の床色 black 成分は消え、残りは左下の三角 x845-871,y807-837 = 504px のみ（下記 N-1/m-3）。白は y=839 まで（rect y1=800 の 39px 先）。縦プロファイル x=1000: y≤837 床色（RGB≈243,215,183）→ y840-847 前縁の暗い切断面（RGB≈164,128,91）→ y≥849 机（木目）。**白は前縁の切断面の手前で止まり、机には出ていない**（white 最下行 839 = 前縁リップの直上）。クロップ `c01_S.png`。壁の隙間（コルゲート帯の切れ目）を通る床と foamboard 帯（床と同色）が一続きで、帯を跳び越えた飛び地ではなく連続成分（white 連結成分 1）。 |
| F-02 BDY-02 西 | **解消** | white は x=130 から（床端 x≈128、実質 2〜3px 内側）。前回の床色 black 成分 2,844px は消滅。西縁の左にはコルゲート壁が連続し（black が正）、床がその壁に接している。上端の細い欠け y372-381 は壁影（dE 13〜53、床色ではない）で black が正。クロップ `c02_W.png`。 |
| F-03 BDY-03 北 | **解消** | white は y=116（床端 y≈115）から。喉 x747-922 は y=124 以降で連続 1 区間。前回の 1,682px の床色 black 成分は消滅。クロップ `c03_N.png`。 |

## 3. 退行検査（全6枚）

方法: PIL / numpy / scipy / skimage。検査スクリプトはスクラッチ（§7）。

- 寸法: mask・traversal-edit・mask-overlay・採用画像の全 24 ファイルが 1672×941。**合格**
- 値: mask の一意値は全6枚 {0,255}、R=G=B（mode RGB）。**合格**
- traversal-edit = mask: 全6組でバイト一致・配列一致。**合格**
- 可逆: 全 mask の WebP チャンクが `VP8L`。**合格**（書き出し前の配列との一致は元が無く未検証）
- 白の連結成分: 全6枚で 1、black の連結成分（4近傍）も 1（白内の穴 0、白の島 0）。white px = 91,819 / 497,318 / 424,974 / 445,335 / 109,363 / 105,878。**合格**
- 装飾/壁の帯/面取り/影の白混入（白で Lab dE>15 の床芯中央値比）: 01=48px、02=169px、03=3px、04=53px、05=16px、06=12px。座標を見るとすべて境界 1〜数px の縁フリンジ（01: x874-895,y777-797 の 10px と x1125-1155,y778-808 の 27px ほか／02: 20 クラスタ、最大 27px、N/S 縁沿い／04: 入口 x797-875,y799-822 の 53px／05・06: 斜め縁沿い 1〜6px）。島・面としての混入は **0**。dE>10 でも 150〜1,497px（床の緩い陰影）で面の誤混入なし。**合格**
- 禁止辺（出口でない辺で縁から 4px 以内〜外 8px に白）: 01 N/E/W、03 S、04 N/E/W、05 E/S、06 N/E/W すべて 0。BDY-03 S は最寄りの白が縁から 9px（E 出口の下端 y=801 と rect y1=810）で 4px 以内に該当せず。白の外接矩形は画像縁から最小 101px で画像外縁には触れない。**合格**
- 出口の個数と辺: 01 = S×1、02 = N×2・E×1・S×3・W×1（計7）、03 = N×1・E×2・W×1、04 = S×1、05 = N×1・W×1、06 = S×1。links.json の 16 出口と一致（`(id,partner)` 16/16 が `docs/map-topology.md` の台帳行に存在）。**合格**
- 接続表: 反対辺 01 S↔02 N、02 S↔03 N、02 N（head）↔04 S、02 E↔05 W、05 N↔06 S は維持。台帳（map-topology.md）は未更新分を除き変更なし。**合格**
- links.json と mask の実測の一致（出口ごとに端の極値と区間を再計測。§4 表）: 隙間・はみ出し量は全16出口で ±1px で一致。区間 a/b は 2 件が不一致（m-1, m-2）。
- BDY-04 の迷路（作成者の格子 JSON の 78 中心を register の行列で画像へ写し、その上で独立再導出）: 78 中心の 7×7 窓が全 white（78/78）。隣接ペア 137 のうち通路 = 中点まで全 white の 77 本（曖昧 0）で作成者の 77 辺と**完全一致**。次数 1 = 12（行き止まり 11 + 入口セル (6,5)）、次数 3（T 字）= 10、次数 2 の曲がり 37 + 入口セルの直角 1 = 38、閉路 0（black 1 成分・白に穴 0）、連結 78/78。壁で隔てられた 60 ペアの中点に white は 0（壁が連続して通路が貫通・連結していない）。入口は S 辺 x803-869 の 1 本のみ。スケルトン独立計測: 成分 1、端点 13（12 + 入口の延長端）。**合格**

### 出口ごとの links.json と mask 実測（rect 基準。+ = 内側、− = 辺の先）
| 出口 | links 隙間/はみ出し | mask 実測 | links 区間 a-b | 辺付近の mask 区間 |
|---|---|---|---|---|
| 01 S | 0 / 40 | −39（y=839） | 877-1155 | y=800 で 876-1134（b が 21px 差） |
| 02 N head | 0 / 1 | −1 | 744-923 | y=133 で 744-921 |
| 02 N mouth | 0 / 2 | −2 | 1020-1260 | y=129 で 1078-1255（a が 58px 差） |
| 02 E | 0 / 4 | −3 | 232-407 | x=1542 で 239-406、x=1532 で 232-406 |
| 02 S lung/lower/heart | 0 / 4 | −3 | 408-587／743-925／1082-1265 | 408-586／746-924／1082-1265 |
| 02 W | 0 / 7 | −7（x=130） | 378-561 | x=137 で 378-560 |
| 03 N | 0 / 4 | −4 | 747-922 | y=124 で 747-922 |
| 03 E stomach/left-leg | 0 / 1・3 | 0・−2 | 138-330／601-801 | x=1548 で 144-325／610-801 |
| 03 W | 0 / 4 | −4 | 598-797 | x=130 で 604-797 |
| 04 S | 0 / 2 | −1 | 803-869 | 803-869 |
| 05 N | 6 / 0 | +6 | 518-849 | y=130 で 529-849 |
| 05 W | 8 / 0 | +8 | 381-582 | x≈131〜150 で 379-582 |
| 06 S | 0 / 6 | −5 | 569-890 | y=813 で 567-860 |

## 4. 新たに白にした画素の妥当性（座標検査）

- BDY-01 S（rect の外に 9,277px、x872-1133,y801-839）: foamboard 帯（床と同色）の中だが、帯は壁の隙間の床とつながった連続面で、y=839 が前縁リップ（y840 以降は暗い切断面・y849 以降は机の木目）の直上。**土台縁の内側**（白は机にも切断面にも出ない）。遷移範囲を「辺上」で判定する場合は、辺 = rect 縁 y=800 でなく実際の前縁 y≈839 のどちらかを kako-jun が決める必要がある（M-1）。白は帯の幅いっぱいまで広がり、左端 x872-876・右端 x1133 は垂直・斜めで床の延長線に沿っているが、左下の床色の三角 504px（x845-871,y807-837）が black のまま残り、境界が帯の途中で垂直に切れる（m-3）。
- BDY-02 W/S/N（rect 外 3,107px、最大 7px）: すべて壁の足元から先端までの床の延長（W は壁に接する x=130、S は壁の上面 y≤805、N は y≥127）。帯の跳び越えなし。
- BDY-03 N（y116〜、rect 外 4px）・E/W（rect 外 2〜4px）: 床端に沿う。crop `c03_N.png`, `c03_E2.png`。
- BDY-04 S（rect 外 14px）、BDY-06 S（rect 外 1,170px、最大 5px、壁の上面まで）: 壁の手前で止まり、コルゲート壁・テープは black（`c06_S.png`）。
- いずれも色の dE<8 の床で、装飾・毛糸・ボタン・粘土玉・赤紙・テープの白混入は 0。

## 5. Findings

分類: blocker / major / minor / note。**blocker 0・major 0（前回の F-01〜03 は解消）**。

| ID | 分類 | MAP | 内容・証拠 | 修正先 |
|---|---|---|---|---|
| F-04（維持） | major | BDY-02 | 契約「首は広間から1本、上で頭（北）と口（北東）に分岐」と画像の食い違い。y=129 の white は x812-849・1078-1255、y=133 は x744-921・1073-1258、y=159 は x748-921・1007-1258。首の狭まりは無く、頭と口は斜めの壁片（くさび、x≈925〜1090,y≈117〜175）を挟んで広間の上端に並ぶ 2 つの開口。mask は画像の床を忠実に写しており mask の欠陥ではない（`c02_N.png`）。**kako-jun の承認待ち** | `docs/map-topology.md` BDY-02 作画契約・`docs/map-specifications.md` BDY-02 行。契約を実形に合わせるか採用を再判断。mask は変更不要 |
| M-1 | minor | BDY-01 | 出口の辺の定義が出口間で不揃い。BDY-01 S だけ白が rect 縁 y=800 を 39px 越え前縁リップ y=839 に届く（links の `white_beyond_edge_px`=40、`edge_line_px`=800）。他の出口は rect から最大 7px。壁の隙間で床が前縁に達する画像なので物理的には正しいが、遷移範囲を辺上で判定する TBD が決まる際、BDY-01 S の辺の位置（800 / 839）を明記する必要がある | `map-asset-registry.md` BDY-01 行・遷移範囲 TBD に「S の辺 = 前縁 y≈839」等を記録 |
| m-1 | minor | BDY-01 | links.json の S 区間 b=1155 は mask の辺（y=800）での右端 1134 と 21px 差。区間が斜め縁の最大値になっている | `BDY-01-links.json` を辺の実測（876-1134）へ再生成 |
| m-2 | minor | BDY-02 | links.json の N mouth の a=1020 は mask の辺（y=129）での左端 1078 と 58px 差（y=159 で 1007）。区間が壁片の先端でなく内側の最大値を取っている | `BDY-02-links.json` を辺の実測（1078-1255）へ再生成 |
| m-3 | minor | BDY-01 | 左下の床色の三角 x845-871,y807-837（504px）が black のまま、白の左縁が垂直に切れる（`c01_S.png`）。右側の斜め縁は床に沿う。連続性・連結には影響せず | BDY-01 mask の左縁を斜めの床端に合わせる（任意） |
| m-4 | minor | BDY-03/02 | 床色の black 残り: BDY-03 NE x1394-1512,y147-188 = 483px、SE x1456-1512,y768-789 = 280px（壁際 10〜12px の帯）、BDY-02 x654-688,y463-484 = 214px。前回 F-05/F-09 の残余。出口外で到達に影響しない | 任意（次の mask 更新時） |
| m-5 | minor | BDY-04 | 通路幅が仕様「約77px」（1920基準）より細い（前回 F-06）。今回も台帳の注記を確認できず（register.json の `passage_width_px`=77 は幾何、mask は 52〜66px） | `map-specifications.md` 124 行・`map-asset-registry.md` 116 行に「mask 実幅 約56px（影を除く床）」を注記 |
| m-6 | minor | BDY-01 | `BDY-01.event-mouth` の到着位置・向き・範囲が TBD（links `range=null`、前回 F-07）。mask から検査不能 | `map-asset-registry.md` BDY-01 行に TBD 明記 |
| N-1 | note | BDY-05 | 残った隙間は妥当。N 6px（white は y=126 から、rect y0=120）・W 8px（white は x=128〜131 から、rect x0=120）。N は床の上に粘土の枠が走り、W は縁の foamboard/粘土の壁（x≈110〜128）が床との間に常にあり、black が正（`c05_N.png`, `c05_W.png`）。床は壁に接して出口の辺まで届いている | 隙間の扱いは TBD（#142）に従う |
| N-2 | note | BDY-04 | 壁の面取り上面（y237-240、y551-553 ほかの 3〜4px 帯、床色で black）は定義どおり（前回 F-10） | 記録のみ |
| N-3 | note | 全体 | mask・links・register は未追跡でコミット無し（前回 F-12）。台帳文言（「mask未作成」）の更新は本書の対象外（前回 F-11）。コミット後に hash を追記すること | — |

## 6. MAP別判定表（mask ステージ限定の意見。台帳 status は変更しない）

遷移範囲値・runtime 扱い・床と縁の隙間の扱い（TBD）が未決のため、台帳を `ready` にするのは**この red-team 単独ではまだ不可**。mask としての可否は次のとおり。

| MAP | mask 判定 | 条件 |
|---|---|---|
| BDY-01 | **可**（mask のみ、TBD 解消後） | M-1（辺 y=800/839 の定義）の記録が条件。m-1・m-3 は任意、m-6 は台帳 TBD 明記 |
| BDY-02 | **条件付き可** | F-04（契約と画像の食い違い）を kako-jun が承認・文言を直すことが条件。mask は変更不要。m-2（links の a）を直すと良い |
| BDY-03 | **可**（mask のみ、TBD 解消後） | m-4 は任意 |
| BDY-04 | **可**（mask のみ、TBD 解消後） | m-5（幅の注記）。迷路は独立再導出で仕様一致 |
| BDY-05 | **可**（mask のみ、TBD 解消後） | 隙間 N 6px・W 8px は壁の実在で妥当。TBD に従う |
| BDY-06 | **可**（mask のみ、TBD 解消後） | S 縁の細い欠けは前回より解消（床色 black 成分なし） |

## 7. 使ったコマンド・クロップ

作業ディレクトリ: `/tmp/claude-1001/-home-kako-jun-repos-private-freeza/aa5acb76-b5dd-4655-b198-ef71c171c671/scratchpad/r2/`（`uv run --with pillow --with numpy --with scipy --with scikit-image python3 -I <script>`）

- sha256: `sha256sum assets/images/fields/masks/BDY-0[1-6]-* assets/images/fields/reference/body-*-bdy0[1-6]-adopted.webp docs/production/body-masks/BDY-0[1-6]-*.json`
- `a1.py`（寸法・値・同一・VP8L・連結・床色 dE・床色 black 成分）、`a2.py`（4辺の走査・dE>15 白のクラスタ・rect 外の白）、`forb.py`（禁止辺）、`links.py`（links と mask の突合）、`prof.py`（BDY-01 S の縦プロファイル）、`maze.py`（BDY-04 の再導出）、`crop.py`（左=原画素・右=mask 境界の赤線）
- クロップ（`r2/` 下）: `c01_S.png`（F-01 確認・前縁）、`c02_W.png`（F-02）、`c03_N.png`（F-03）、`c02_N.png`（F-04・頭と口）、`c02_S.png`、`c06_S.png`、`c05_N.png`、`c05_W.png`（N-1）、`c03_E2.png`、`c03_E1.png`、`c03_W.png`、`c04_S.png`、`c01_RT.png`

## 8. 検査しなかったこと

- runtime の遷移判定（範囲値・TBD）、実機の歩行確認、BDY-07〜17。
- 書き出し前の mask 配列との可逆一致（元が手元に無い）。
- 台帳 docs の文言更新（前回 F-11）。

## 9. 総括

前回の major 3 件（BDY-01 南・BDY-02 西・BDY-03 北の喉で床が white に届かない）は原画素で解消を確認した。白は床と同色の foamboard 帯の中を通って BDY-01 の前縁リップ（y=839）で止まり、机へ出ていない（土台縁の内側）。前回合格の項目（寸法・{0,255}・同一・可逆・白連結成分 1・装飾の混入なし・禁止辺・出口の個数と辺・台帳 16/16・BDY-04 迷路 78/77/11/10/38/0）に退行はない。blocker・major なし（F-04 の契約と画像の食い違いは前回どおり kako-jun の承認待ちで維持）。残りは minor（links の区間 2 件、辺の定義 M-1、BDY-01 左下の三角、幅の注記、event-mouth TBD）で、台帳を ready にするには遷移範囲の TBD 解消と F-04 の決着が先。

【追記 2026-10-23】本書の F-04（BDY-02 の首: 契約『首は1本・上で頭と口に分岐』と採用画像〔旧版。北辺の床が首の狭まりのない1つの広い塊〕の食い違い）は kako-jun が承認済みの逸脱として採用した。マスクは変更不要（画像が正）。あわせて、BDY-13 の寸法 1672x940（F-01、13-17 の報告）も kako-jun が例外承認した。
