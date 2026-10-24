# sit-by-me ローカル孤立情報の棚卸し(読み取り専用)

調査日 2026-10-23。対象: sit-by-me 本体(`<repo>`、branch body-maps-baseline-20261022、追跡1153ファイル、画像・レビューを除く文書/コード/JSON 486)と worktree 3つ(oblique 268 / teramachi-rest 355 / ledger-master 282 の本体に無い追加ファイル)、notes リポ、freeza セッションノート47本、memory。
凡例: 「確認」=ファイル/コマンドで確認、「推測」=未確認。
注意: 台帳(新形式)は ledger-master worktree の `docs/ledger/*.csv` 10表(MAP/端/接続/接続図設定/要素/窓/時期差分/既定値/エリア固定/装飾プール、計364行)が現状の全て。**決定表・採用要素表・未決表は ledger_io.py にスキーマだけあり、CSV はまだ無い**(確認: ledger_io.py L37-42、ls docs/ledger)。つまり「決定が台帳に降りていない」はほぼ全件が現状該当し、孤立の判定は「決定表が出来たとき移す先がある情報か」を基準にした。Issue 側は番号・本文を全件は突合していない(推測を含む)。

## 1. ファイル分類(件数)

本体 HEAD の非画像追跡ファイル 486 + worktree 追加分。

| 分類 | 内容 | 件数 | 主な場所 |
|---|---|---|---|
| A 台帳(新形式) | 日本語CSV | 10表(ledger-master のみ、未マージ) | ledger-master `docs/ledger/` |
| B 台帳の派生物(生成物) | plan/decor-pools/connections JSON、edit-prompt、mask/occlusion JSON、manifest。**生成物台帳への登録は無い**(生成物.csv は設計のみ) | 約190(TRM-02〜17 の plan 16、TRM-xx/ 配下 mask/occlusion/edit-prompt/manifest 各16〜、connections 3、decor-pools 1、dependency-graph 1) | oblique / teramachi-rest の `docs/production/oblique-mocks/` |
| C 旧形式の設計/台帳 md(移行元。新形式でも Issue でもない) | 台帳の実体が md 表。今回の「孤立」の主体。第1段階は寺町分だけCSV化、残りは未移行 | 約25 | `docs/*.md`(decisions 210KB, monsters 108KB, story 107KB, map-topology 94KB, dungeon-enemies, systems, map-specifications, map-contract-checklist, map-asset-registry, boss-gimmicks, enemy-allocation, ability-candidates, learning-schedule, blades, art-direction, assets-policy, content-registry, bgm-*.md/csv, scenario-registry, timeline, ff-battle-rules, roadmap, concept, issue-map, teramachi-rebuild-candidates, map-reference-research) |
| D 履歴記録(置き場として正当) | レビュー、採用記録、E2報告、没記録 | 約300 | `docs/reviews/artifact-redteam/`(md 200)、`docs/production/*adoption*.md`、`oblique-mocks/TRM-02/e2/*-report.md`・run-log、`verification/transparency-audit-20261022/`、`20261018-teramachi-preflight.md` |
| E 来歴/対応表(機械可読の台帳的JSON) | 素材移行 manifest 712件(274KB)、MAP ID 改番 130件、body-masks 36 JSON、body-mocks 17 JSON、verification/body-layout geometry 18・registration 5、oblique-masks の input/register/result JSON 14 | 約110 | `docs/production/`、`verification/body-layout/` |
| F コード/スキル | SKILL.md 9、tools 約20、scripts 14、tests 6 | 約60 | `.claude/skills/`、`scripts/`、`tests/` |
| G 画像・生成プロンプトの送信文 | `*-prompt-send.txt` 約60(BDY採用の来歴)、verification/body-layout/prompts 35 | 約95 | 同上 |
| H 孤立した情報を含むもの | 下の §2 | 約25ファイル | §2 |

## 2. 孤立した情報の一覧(台帳にも Issue にも無い、または台帳に降りていない)

優先度: 寺町=P1、他エリア=P2、敵=P3、素材=P4。

### 2.1 寺町(P1)

| # | ファイル(行) | 内容 | 種類 | 合流先 | 移し方 |
|---|---|---|---|---|---|
| T1 | teramachi-rest `oblique-mocks/TRM-06〜17-plan.json`(12個、各5〜7KB)と `connections-teramachi.json`(13KB、sit-oblique-town/1) | 寺町残り12MAPの平面設計(道の形・建物・塀・用水・橋・石段の位置/寸法、端の位置、閉鎖辺)。台帳の MAP.csv は TRM-06〜17 が空行(確認: MAP.csv 17行のうちTRM-01・06〜17は名称等が空)。**設計の唯一の置き場がplan JSON** | 設計 | MAP/端/接続/要素/窓/エリア固定 | ledger_migrate_once.py を TRM-06〜17 に拡張して台帳化。plan は派生物化 |
| T2 | teramachi-rest `oblique-mocks/teramachi-assumptions.md`(14KB、機械生成)の「58件の既定(要確認)」 | 仮置き寸法の一覧。道幅クラス(狭い道132/街路160/広い道260)、出入口2人分原則、閉鎖辺は黒、屋外に decor_pool を付けない方針、円環(16→15→06→16) | 数値/決定 | 既定値.csv(MAP_ID付き)+エリア固定(道幅クラス) | 台帳の既定値へ。md は生成ビュー |
| T3 | 同 teramachi-assumptions.md L5-6「TRM-08 上端は塀で閉じる。kako-jun 決定 2026-10-23(#51。旧TRM-01正門廃止)」、TRM-15/16 の円環、TRM-03.event-kiss の起点 | 接続の決定 | 決定 | 決定表+接続(閉鎖辺は接続側に『閉鎖』行が無い=辺の状態テーブル未設計) | 決定表へ。閉鎖辺は端.csv に種別「閉鎖」を足す案(推測) |
| T4 | oblique `oblique-mocks/windows.md`(7.4KB)、`dependency-notes.md`、`connections.md`(12.5KB)、`teramachi-connections.md`(12KB、生成) | 窓の根拠・MAP依存・接続表。windows.md は窓.csv に取り込み済み(確認: 窓.csv 25行)だが **md側は残り、台帳との同期検証が無い**。connections.md/dependency-notes.md は 接続.csv/MAP.csv の依存MAP列に対応(取込済み範囲は未突合=推測) | 設計 | 窓/接続/MAP | 突合してから md を生成ビュー化 |
| T5 | `oblique-masks/README.md`(7.5KB、worktree)の「TRM-04 の確定(kako-jun 2026-10-23)」「TRM-02 の出口」 | 石の敷居は通れる(bridge)、須弥壇の段は blocked、扉は本堂の壁、char_unit(体内1人幅77px→1672幅で67.1px)、各出口の位置 v=0.552〜0.968 | 決定/数値 | 決定表・端.csv・既定値 | 決定表へ移し README は手順だけに |
| T6 | `oblique-masks/TRM-0x-input.json` 5個、`*-oblique-result.json`、`TRM-05-openings-check.json`、`TRM-05-floorplan-candidates.webp` | 旧方式(採用画像からの逆算)の入力と結果。README に「旧方式の記録(検証用)」とあり正当な履歴だが、input.json に出口の `design_source`(台帳原文の引用)と TBD 候補が入っている | 履歴(一部設計) | 履歴のまま。design_source は決定表へ | 履歴として残し、決定表へ移した後に参照化 |
| T7 | `docs/teramachi-rebuild-candidates.md`(8.8KB) | 寺町再作成の候補台帳(没候補・旧legacy画像の概略構図の扱い)。oblique の assumptions が「旧legacy画像は参照専用」と引用 | 来歴/決定 | 素材.csv(状態=没/参照専用)+決定 | 移して参照化 |
| T8 | `docs/production/20261018-teramachi-preflight.md`(19.7KB) | 寺町16枚の事前確認。台帳に降りていない前提・順序・チェックを含む(推測。全文未精読) | 手順/決定 | 決定表 or 履歴 | 精読して判定 |
| T9 | map-contract-checklist.md の TRM-03/05 の TBD セル内【2026-10-23 E2 の生成物は全て没】(設計案の認定) | 没の記録がセル内に混在 | 来歴 | 素材.csv(状態=没) | 設計案 §2.2 のとおり |
| T10 | map-topology.md「MAP相互接続台帳 v2」の138行(接続表)・「寺町の地形不変条件」節 | 寺町外を含む接続の正本 | 設計 | 接続.csv(寺町分はledger-masterに23行。残りは第2段階) | 第2段階で全接続を取込、oblique_town.py の台帳突合(`--ledger-ref`)を台帳CSV参照に |

### 2.2 他エリア(P2)

| # | ファイル | 内容 | 種類 | 合流先 | 移し方 |
|---|---|---|---|---|---|
| E1 | `docs/map-specifications.md`(60KB)・`map-contract-checklist.md`(58KB)・`map-asset-registry.md`(45KB) | 130MAPのうち寺町17以外 113MAP の時期/特徴/主路/固定/状態/TBD/画像。**旧md表が唯一の正本** | 設計 | MAP.csv 他 | 第2段階で一括取込(build_map_prompt.rb は固定列位置依存=cells[2..5]) |
| E2 | 体内(BDY-01〜17): `.claude/skills/sit-field-background/tools/body_layout.py`(1299行)・`build_body_prompt.py`(2956行・BDY- 252回)・`docs/production/20261022-body-maps-adoption.md`/`decoration-plan.md`/`20261022-bdy02-adoption.md`/`body-mocks-and-registration.md`、`verification/body-layout/{consistency,connections}.md`・geometry 18・registration 5 | **体内の幾何決定がコードの定数に埋まっている**(§3 の B1〜B6)。採用の記録はmd、数値はgeometry JSON、決定の原文はIssue #142 コメントと body_layout.py のコメント | 設計/決定/数値 | MAP/端/要素/決定 | 体内17MAPを台帳化し body_layout.py は台帳読込に |
| E3 | `docs/topology/areas.json`・`map-ids.json`・`overseas-progression.json`・`areas/*.svg` 15・`atlas.svg` | エリア/MAP数/座標。既に JSON だが台帳(エリア.csv)は未作成。overseas-progression は進行条件の設計 | 設計 | エリア.csv 他 | 取込後、JSON/SVG は派生物化 |
| E4 | `docs/timeline.md`・`story.md`・`scenario-registry.md`・`systems.md` | 時期定義(幼稚園期/火災後…)。MAP の「時期」列の語彙の正本が散文(推測) | 語彙 | 語彙/時期表 | 時期語彙を表にし MAP.時期の FK に |
| E5 | `docs/bgm-registry.md`(24KB)+`bgm-phrases.csv`+`bgm-sources.csv` | 既に一部CSV。md との二重管理 | 来歴 | BGM.csv(+MAP_ID列) | CSVを正本、md をビュー |

### 2.3 敵・召喚獣・人物・武器(P3)

| # | ファイル | 内容 | 合流先 |
|---|---|---|---|
| M1 | `docs/monsters.md`(108KB)・`dungeon-enemies.md`(74KB)・`enemy-allocation.md`(36KB)・`boss-gimmicks.md`(45KB) | 敵86+召喚獣8。出る場所が3か所(設計案§1.2)。**絵の状態/採用が md 表** | 敵.csv/敵配置.csv/ボス.csv |
| M2 | `docs/content-registry.md`(5.6KB) | 戦闘/MAP ID の確定表。sit-enemy-sprite/battle-background が最初に読む | 台帳 INDEX の入口候補 |
| M3 | `docs/art-direction.md`(52KB)・`assets-policy.md`(7.5KB) | 画風・品質規約。sit-enemy/character/summon が「原文のまま」読む | 語彙/決定へ分解(散文は残す) |
| M4 | `docs/production/asset-layout.md` L27-47 | **C001〜C009 の人名prefix表**、`C009`採用記録、`M001`旧640px透過の扱い、Mxxx-field 16点正本化(2026-10-23)の記述。人物ID表の正本が Issue #95 でなく asset-layout.md 内 | キャラ.csv(第3段階)+素材.csv |
| M5 | `assets/images/weapons/masters/`(20枚)(session1153 `20261023-session1153-sit-by-me-weapon-masters.md`、Issue #147) | **武器マスター20枚は README・docs・スキル・asset-layout のどこからも言及されていない**(確認: grep で assets 外に0件)。来歴=Issue #147 とセッションノートだけ。ファイル名は `<刀名>-reference-v1.png`(PNG、asset-layout は非可逆WebP規約) | 素材.csv(武器)・asset-layout の配置表に追記 |
| M6 | `verification/transparency-audit-20261022/{audit-notes.md,alpha-report.txt}` | 透過監査(どの敵/人物の画像のalphaが不合格か、約今日の敵を緑背景で確認)。docs/ のどこからもリンクされない | 素材.csv の検査結果列。履歴として保存 |

### 2.4 素材(P4)

| # | ファイル | 内容 | 合流先 |
|---|---|---|---|
| S1 | `docs/production/20261018-asset-migration.json`(274KB、712件)・`20261019-map-id-renumber.json`(130MAP+aliases) | 旧→新パス、SHA-256、削除理由、pruned、prompt_provenance。**素材の来歴の唯一の機械可読台帳。素材.csv は未作成** | 素材.csv の初期データ。JSONは履歴として残し台帳から参照 |
| S2 | `docs/production/20261022-bdy02-adoption-prompts/*.txt`・`20261022-body-maps-adoption-prompts/*.txt`(計約35)、`verification/body-layout/prompts/*`(35) | 採用に使った送信プロンプト原文=来歴。どの md からも文字列で参照されていない(確認: §4) | 素材.csv の「来歴」列にパスを入れる |
| S3 | `assets/images/fields/reference/*.webp`(18)、asset-layout.md の「保存済み」行(sha256・byte数・解像度の長文) | 採用画像の寸法/sha/用途が asset-layout.md の散文に埋まる | 素材.csv(sha列) |
| S4 | `verification/characters/tools/README.md`+keying系 | 透過処理ツール(keying.py が正本)。人物/敵スキルが呼ぶ | 手順としてINDEXへ |
| S5 | `assets/images/brand/README.md` | ロゴ暫定の規定 | 決定へ(軽微) |

## 3. コード内の定数・語彙(台帳から導出すべきもの)

確認はすべて ledger-master worktree の tools/ または main の scripts/。

| # | 場所(行) | 値/語彙 | 台帳候補 |
|---|---|---|---|
| B1 | oblique_mock.py L25-27 `CHAR=66`、`WIDTH_CLASSES={2people:132, 1.5people:100, 1person:66}`、DOOR_H=2*CHAR | 戸口幅クラスの寸法(決定 2026-10-23「1.5人分=100」等) | 語彙(幅クラス)+エリア固定 |
| B2 | oblique_mock.py L34-37 `KV=0.74`、`SLAB=35`、`_DST=[[165,55],[1525,55],[1650,850],[22,850]]`、L290-291 `SLAB_TAPES`/`SLAB_GLUE`(マステ・糊の座標)、L542-543 `CHAR_PX=67`・`BODY_PX=100` | 斜め視点の測定値(session1152 で記録した 40〜45°/奥幅比0.81〜0.84/前面35px/出力1672×941/1キャラ=67px)。決定は視点系パラメータ=エリア横断 | 描画方式表(新)または既定値。session1152ノートの数値と食い違い無しか照合要 |
| B3 | oblique_build.py L40-58 `DECOR_FILE`、`DECOR_LAYER_KEYS`、`DECOR_REQUIRED`、`AREA_OVERRIDE_PLAN_KEYS` | スキーマ定数。台帳列と二重(ledger_io.py にも列定義) | ledger_io と一本化 |
| B4 | oblique_build.py L519-570 の build_prompt 直書き文: TREES 見出し「寺町の木=松＋枯木。常緑樹は松だけ」、OPEN PASSAGES「(#51 2026-10-21)」「床は木の板張り(確定)。石の床にしない」、DOOR WIDTHS の WN、「細い扉。見落としやすいので必ず描く」、ROLE 文(段ボールの台座・綿の雪…) | **決定が英日の文に埋まる**。松の決定は decor-pools.json にもあり二重。板張り・開口の文は decor-pool に無い | 決定表(プロンプト出力=必須語)+語彙(プロンプト断片) |
| B5 | oblique_topology.py L382「本堂に窓はいらない(kako-jun 決定 2026-10-23)」の直書き文、L23 `WCN` | 決定の文章がコード内 | 決定表 |
| B6 | oblique_e2_measure.py L40-56,346 | 測定基準の閾値(装飾量比・机の平均色(127,75,38)・松の緑量の絶対基準・畳判定「畳は描かない決定(#51)」)。基準変更の経緯(2026-10-23)は e2-report.md | 既定値/決定(測定基準)。履歴はe2-reportに |
| B7 | body_layout.py L40-100: `DEFAULT_MAIN_WIDTH_RATIO=0.14`(TBD の仮置き)、`LW17_DIV=3`、`ONE_PERSON_MAPS=("BDY-17","BDY-04")`、`BDY02_SLOTS`、`HUB`、`BDY02_HALL=((960,700),205)`、`BDY02_HALL_RX=300`、`BDY02_J`、`BDY02_K_Y`、`BDY02_ARMS`、`THIGH_ENTRY_SLOT=0.292`、`MW0,MH0=1644,804`、BDY-09 の膝35度など。コメントに kako-jun 決定の原文引用(#142 2026-10-22) | **体内17MAPの幾何決定そのもの**がPythonの定数。geometry JSON(verification/body-layout/geometry/)はその出力 | MAP/端/要素/時期差分+決定表 |
| B8 | build_body_prompt.py L48-69: `TARGETS`(17)、`ROOM_MAPS`、`ISSUE=142`、`SLIVER_NARROW=80`、`LABEL`(英語prompt用の部位名) | 対象リスト・部屋構造の分類・英語名 | MAP.描画方式/語彙 |
| B9 | check_body_image.py L26-78: `OK_SIZES={(1920,1080),(1672,941)}`、`FLOOR_REF=(233,196,164)`、`PASSAGE_POS_TOL=25`、`PASSAGE_W_TOL=0.10`、CL_*(模型色)、BAND_FOAM 28/BAND_CORR 20 | 検査の閾値と模型の素材色 | 既定値(検査基準)。tools に残す場合も1か所へ |
| B10 | body_register.py L46 `MOCK_RECT=(138,138,1782,942)`(body_layout の MX0..MY1 と一致する旨のコメント) | 二重定義 | 一本化 |
| B11 | scripts/build_map_prompt.rb L36-60: 固定列位置 `contract_cells[2..5]`、`#### MAP相互接続台帳 v2` 見出し文字列で節を切る、末尾の英語プロンプト固定文(「Contemporary K Prefecture, Japan, winter; handmade tabletop diorama, 80–85 degree view…」) | 旧md表の列位置依存+固定文(語彙) | 語彙+MAP表。第1段階で oblique 側は台帳に載り、本スクリプトは屋外の旧方式用に残る |
| B12 | oblique_build.py `ledger_gate`(L588〜)・manifest の `ledger.registry/checklist`(L626)がパス直書き | 旧 md を参照する配線 | 台帳CSV参照に差し替え |
| B13 | scripts/verify_map_ledger.rb | md表を正本として検査(列位置依存) | verify_ledger.rb へ |
| B14 | tests/ 6本(1495行) | asset-migration / map-id-renumber / topology / atlas / overseas / body_topology の fixture はJSON/mdの現行内容に依存。台帳化で追従が要る | 追従対象 |

## 4. 導線から孤立したファイル(機械的に出した結果)

方法: 非画像の追跡486ファイルについて、他の追跡ファイル本文に「パス全体」または(同名が1つだけなら)「basename」が1回も出ないものを孤立、とした。リンク解析は README.md から BFS(README→docs→…)と、README+全 SKILL.md を根にしたもの。本体 HEAD のみ(worktree の追加分は含めない)。スクリプトは scratchpad の `reach.py`・`bfs.py`。**制限**: 文字列一致のみ(パターン参照 `BDY-NN-*` は一致しない)=過検出あり。

- 直接の被参照ゼロ(README・台帳・スキル・他のファイルのどれにも名前が出ない): **164 / 486**
- README から辿れない: **249 / 486**(README が直接リンクするのは docs 8本のみ)
- README+SKILL.md から辿れない: **247 / 486**

内訳(README+SKILL.md から辿れない 247):
| ディレクトリ | 件数 | 備考 |
|---|---|---|
| docs/reviews/artifact-redteam | 90(過検出あり。レビュー200のうち) | 履歴だが索引が無い |
| docs/production/body-masks | 34 | `BDY-NN-{links,register}.json`(パターン参照のみ、body_register.py が出力) |
| verification/body-layout/prompts | 30 | プロンプト原文 |
| docs/production/20261022-body-maps-adoption-prompts | 17 | |
| docs/production/body-mocks | 17 | |
| verification/body-layout/geometry | 17 | |
| docs/topology/areas | 15 | SVG(atlas 生成物) |
| scripts | 9 | fetch_bgm_sources.py, map_graph.rb, render_*.rb 4, verify_map_atlas.rb, verify_map_id_renumber.py, verify_overseas_progression.rb |
| tests | 6 | 全て |
| verification/body-layout/registration | 5 | |
| docs/topology | 2 | `README.md`, `sunnyland.svg` |
| verification/transparency-audit-20261022 | 2 | |
| .claude/skills | 2〜3 | `sit-field-background/agents/openai.yaml`, `sit-field-background/tools/README.md`(SKILL.md から未リンク)、BFS 版 README のみでは `sit-character-sprite`・`sit-map-enemy-sprite` の SKILL.md も(スキルは自動注入なので問題小) |
| docs | 1 | `docs/issue-map.md`(README・SKILL・他docから未リンク。memory は「再開の入口」と書いている=最重要入口が孤立) |

特に致命的: 
1. `docs/issue-map.md`: memory で「再開時の入口」とされる、決定・候補と Issue 番号の対応表が、README からも他 docs からも辿れない。
2. `docs/topology/README.md`: エリア図の説明。同じく孤立。
3. 武器マスター20枚(`assets/images/weapons/masters/`)は assets 配下で唯一文書から一度も言及されない。
4. リポ直下に `CLAUDE.md` / `AGENTS.md` が**無い**(確認: ls)。エージェントの入口は README(8リンク)と各スキルの「原文のまま読む」リスト(sit-enemy-sprite/summon-sprite/battle-background/map-enemy-sprite)だけ。
5. `scripts/` 14本のうち README・台帳で説明があるのは `verify_asset_layout.py`(asset-layout.md)と `verify_map_ledger.rb` 等一部のみ。

## 5. フォルダ・ファイル配置の管理の現状

規定の所在:
- `docs/production/asset-layout.md`(73行、2026-10-18 #68 起点・2026-10-23 まで追記): 画像の正本配置表(敵/召喚獣/人物/MAP legacy/legacy mask/外観参照/体内マスク/戦闘背景/ブランド)、保存運用(候補置き場を作らない、raw を保管しない、非可逆WebP品質85)、C-ID 表、BG 表。L27-47 は長文の「保存済み」行が20本以上(sha256付き)で表としての構造が無い。
- `scripts/verify_asset_layout.py`(70行): 検証は **asset-migration.json の旧パス消失・新パス存在・ID形式**に限る(確認)。配置規則そのもの(例: `fields/` 以下のディレクトリ許可リスト)は検査しない(推測: 70行で全文確認していない)。
- `docs/production/20261019-map-id-renumber.json`+`scripts/verify_map_id_renumber.py`: MAP ID の正本。
- `docs/topology/map-ids.json`・`areas.json`: エリア別MAP数。

食い違い・規定の無いもの(確認):
1. asset-layout.md L7「`verification/` 配下の検証画像置き場は作らない」と L31「`verification/` は削除済み」に対し、**`verification/` は現存**(body-layout 約95ファイル、characters/tools、transparency-audit)。README も「切り出しツールは `verification/characters/tools/`」と書く。規定と実態の食い違い。
2. asset-layout.md に **`assets/images/weapons/masters/`・`docs/production/body-masks`・`body-mocks`・`oblique-masks`・`oblique-mocks`・`verification/body-layout/`・`docs/reviews/artifact-redteam/` の記述が無い**(確認: grep で weapons 0件、body-mocks/body-masks は md に0件)。
3. `fields/masks/` は asset-layout に体内17×3=51の規定のみ。斜め用マスク(`TRM-*-{traversal-edit,mask,mask-overlay}.webp`)の配置は `oblique-masks/README.md` に書かれ、規定が2か所に分かれる。
4. `fields/legacy/`(参照専用)と `fields/reference/`(外観参照)の意味は asset-layout の表にあるが、oblique 側の assumptions では「旧legacy画像は参照専用・採用根拠にしない」を別途繰り返す(重複)。`legacy/masks` は「検証専用・旧接続を変更しない」。
5. `docs/production/` 内に同種が複数形式で同居: `20261018-*`(日付prefix)、`oblique-*`(prefixなし)、`body-*`、`asset-layout.md`(prefixなし)。日付付き=一度きりの作業記録、prefixなし=継続運用と見えるが規約は書かれていない(推測)。
6. `assets/images/weapons/masters/*-reference-v1.png` は PNG(asset-layout の規約は WebP 品質85)。規約外(推測: 参照専用の扱い。未確認)。
7. `assets/images/characters/C009/`(未追跡)・`docs/reviews/artifact-redteam/20261023-C009-master-raw.md`(未追跡)が本体チェックアウトにあり(確認: git status)、asset-layout は既に C009 を記述(未コミットの M)。
8. e2/ の `.started`/`.finished`/`.gi-before.txt` 等の作業マーカー約100ファイルがコミット済み(oblique 側、確認: ls-files)。置き場の規定なし。

## 6. 台帳 INDEX に載せるべき入口の候補

**エージェントが最初に読む(全スキル共通)**
1. `docs/ledger/INDEX.md`(新設): 台帳の表一覧と FK、生成物(plan 等)の所在、各スキルの入口、配置規定へのリンク
2. `docs/issue-map.md`(決定・候補と Issue の対応。現在孤立)
3. `docs/content-registry.md`(戦闘/MAP ID 確定表)
4. 配置規定: `docs/production/asset-layout.md`(§5 の不足を補う)+`docs/topology/README.md`
5. `docs/decisions.md` の末尾(日付つき決定。決定表へ移すまでの暫定入口)
6. `docs/roadmap.md` 末尾「引き継ぎ」(memory 記載の再開点)

**スキルごと**
- sit-field-background(斜め): ledger 表 → `tools/README.md`(未リンク)・`gates.md`・`pitfalls.md`・`issue-template.md`・`oblique-masks/README.md`(旧方式)
- sit-field-background(体内): `body-appendix.md`・`verification/body-layout/{consistency,connections}.md`・geometry/index.json
- sit-field-mask: `oblique-masks/README.md` と SKILL「斜め視点のエリア」
- sit-enemy-sprite / sit-summon-sprite: content-registry・monsters(対象行)・dungeon-enemies・art-direction・assets-policy(+story の対象行)
- sit-map-enemy-sprite: monsters・dungeon-enemies(召喚獣行)
- sit-battle-background: content-registry・art-direction・戦闘レイアウトJSON(所在要確認=推測)・roadmap 劇背景決定
- sit-character-sprite: art-direction・assets-policy・decisions・asset-layout の C-ID 表
- sit-artifact-redteam: `docs/reviews/artifact-redteam/`(索引新設)

## 7. 決定がメモリ・ノート・セッションノートにだけある例

- memory `project-sit-body-left-right-from-the-person.md`(体内の左右は本人から見る): 本体 HEAD では `.claude/skills/sit-field-background/{body-appendix,pitfalls,issue-template}.md` と body_layout.py のコメントに既出だが、**docs/(map-topology・decisions)には無い**(確認: git grep)。台帳の方位語(左腕=北西 等)が画面左=左のまま、という注記が memory にあり、台帳の決定表には無い。→ 決定表へ。
- memory `project-sit-by-me-concept-and-plan.md`: 「人物は必ずイラスト調」「世界観は少し未来の日本(混血・移民)」「召喚獣は想像で曖昧に」「公開リポなので私的名・未処理の実写素材を書かない」。リポ docs に同旨がある可能性は高いが(推測)未突合。
- freeza セッションノート session1152: 「視点の測定値(40〜45°・側辺9〜11°・奥幅/手前幅0.81〜0.84・前面35px・机小物(マステ3〜5・糊3〜5)は手前固定・出力1672×941・1キャラ=67px)」は一部がコード定数(§3 B2)で、台帳の既定値.csv には `1672` が0件(確認)。寝室1(幼稚園期)/2(小学生〜)・舞台は登れない・内部仕切りは絵で壁と区別、は既定値.csv に既出。
- session1152「質問を減らす: 既定は司令塔が決めてモックに織り込み、まとめて見せる」「常設ゲート: 全モック提示→明示承認前は試験生成も禁止」: 運用規範。スキル(gates.md)に既出の可能性が高い(未突合)。memory `feedback-show-all-mocks-before-generating-images.md` にもある。決定表の対象外(プロセス)。
- 旧採用画像の元: 外観v7・住居v12=commit febf8a6、本堂v11=fbe876a、幼稚園v3=9652459(現ツリーに無い)。session1152 ノートと decor-pools.json の note(「git 9652459」)にだけある → 素材.csv の来歴列に(ledger-master の 装飾プール.csv にも9652459は含まれる=確認、febf8a6/fbe876a は未確認)。
- notes リポ: sit-by-me 専用の dev リーフ無し。`todo/freeza.md` L26 の sit-by-me 行に現況サマリ(M101〜M152採用47/47、M002/M006残、BG010→PR #138 判断、回答待ち #123 ほか)があるが、台帳(monsters.md 絵の状態)と二重。孤立ではなく「現況の写し」。
- freeza セッションノート sit 47本: 決定の記録として正当。台帳にまだ決定表が無いので、各ノートの「決定」節は決定表の初期データ候補(session1140 topology-decisions、1141、1149、1152 が特に)。

## 8. 合流の進め方(優先度順)

第0段階(今すぐ、台帳作業と衝突しない小さな整理)
- `docs/ledger/INDEX.md` と、リポ直下の入口(CLAUDE.md or README の「エージェント向け目次」)を作る。§6 の入口を載せ、`issue-map.md`・`topology/README.md`・`tools/README.md` へのリンクを足す。孤立ファイル(§4)は INDEX か各ディレクトリ README から全件辿れるようにする(特に reviews の索引、body-masks/prompts のディレクトリ README、scripts の一覧、tests)。
- asset-layout.md を§5の食い違いに合わせて整理(verification の現存を認める、weapons・body-*・oblique-* を配置表へ)。verify_asset_layout.py を配置規則の許可リスト検査に拡張(孤立ディレクトリを検出)。

第1段階(寺町、ledger-master で進行中の延長)
1. 決定表・採用要素表・未決表を実体化。初期データ = T3・T5・B4・B5 の決定(松、本堂に窓なし、開口は壁に見せない、板張り、勝手口1人幅、出入口2人分原則、外への戸口1.5人分、TRM-08 上端閉鎖、石の敷居 bridge、体内左右ルール)。
2. TRM-06〜17(T1・T2・T4)を台帳に取込み、plan/connections を派生物化。MAP.csv の空行を埋める。
3. 生成物.csv に B 区分の派生物を登録(allowlist なしの JSON を検出)。
4. B1・B2・B4・B5 を台帳/語彙から導出に(定数は台帳読込、決定文は必須語で出力)。

第2段階(体内・全エリア)
5. 体内17MAP(E2・B7〜B10)。body_layout.py の定数→台帳(MAP/端/要素)。geometry JSON は派生物に。
6. 全130MAP・接続138行(E1・E3・T10)。build_map_prompt.rb/verify_map_ledger.rb を台帳読込に。tests 追従(B14)。

第3段階(敵・素材・人物)
7. 敵・敵配置・ボス(M1)、素材.csv(S1〜S3 を初期データ、M5 武器マスターを登録)、キャラ(M4)。
8. md 設計書のうち表で表せる部分を生成ビュー化(`docs/views/`)。散文(story・art-direction・decisions の物語/美術の決定、map-topology の経緯節)は残し、決定IDからリンク。

履歴(D・E の記録系)は消さず、INDEX の「履歴」節に集約して台帳の来歴列から参照する。
