# sit-by-me 台帳DB化 設計案(日本語マスター → JSON派生 → プロンプト)

調査: worktree /home/kako-jun/repos/2026/sit-by-me-wt-oblique。読み取りのみ。リポ無変更。前段の調査 ledger-audit.md(D1〜D10 の重複・漏れ実例)は有効なので再掲しない。
「確認」=ファイル/コマンドで確認、「推測」=未確認。

## 0. 結論(先に)
- 決定の分散が漏れの原因。md の「決定ブロック」案(ledger-audit.md 案)は、決定を1箇所に寄せるが、外部キーで敵・MAP・接続・素材を結ぶ構造にはならない。目標(DBのテーブル)には**日本語列名のCSVを正規化テーブルとして持つ**のが最小の正解。
- マスター=日本語CSV(`docs/ledger/*.csv`)。人が読む md 設計書は「生成ビュー(読み取り専用)」へ段階的に移す。JSON(plan・decor-pools・connections・atlas・manifest)は**描画直前の派生物**として台帳に登録し、入力ハッシュで鮮度検査する。
- 最初にやるのは寺町(TRM-01〜17)だけ。既存 md 台帳は第1段階では**消さない**(重複は「生成ビュー化」まで保留)。

## 1. 現状の情報モデル(確認した事実)

### 1.1 規模
| 概念 | 実測 | 根拠 |
|---|---|---|
| エリア | 15(TRM17 KRB13 STN1 NTR1 NTB8 UTS5 SNL12 SCH2 NTA7 UCH5 BDY17 APT2 OVS20 GRD10 CST10) | docs/topology/map-ids.json、areas.json(areas 15、maps 合計 130。expected_count 130) |
| MAP | 130(依頼の129でなく130) | 同上。checklist/registry は各130行、specifications は133行(先頭表の行を含む=推測) |
| 接続 | MAP相互接続台帳v2 に138行(door 64、edge 72、event 1、oneway 1) | docs/map-topology.md L116以降の `\| MAP.端 \|` 行を集計 |
| 敵 | M 86(通常敵+中ボス等)、S(召喚獣)8 | docs/monsters.md の ID 列 |
| 敵の配置 | dungeon-enemies.md(表行256)、enemy-allocation.md(130)、monsters.md の「出る場所」列。三箇所で配置を持つ(後者2つは dungeon-enemies に整合させたと冒頭にある) | md表行数 grep |
| ボス | boss-gimmicks.md(表行58) | 同上 |
| BGM | bgm-phrases.csv、bgm-sources.csv(既にCSV)、bgm-registry.md(24KB) | ファイル確認 |
| 決定 | decisions.md 210KB・見出し/日付箇条 約340行、他に art-direction 52KB・story 107KB・systems 60KB・Issue コメント | wc/grep |
| 斜めモック計画 | oblique-mocks/TRM-02〜05-plan.json(4個、エリア=寺町のみ)、decor-pools.json(pools 2、areas)、connections.json(edges 7+)、windows.md、dependency-graph.json | ファイル確認 |

### 1.2 概念ごとの現状
| 概念 | 今の置き場所 | 構造化度 | 重複・食い違い |
|---|---|---|---|
| エリア | areas.json(id/name/maps/layout座標)、map-ids.json(区域コード→件数) | JSON(構造化済み) | areas.json と map-ids.json の件数が別管理(verify で突合済み) |
| MAP | checklist(状態・Ref・出力・TBD)/specifications(時期・特徴・主路・固定)/registry(画像1行)/candidates(寺町)の4表が同一MAP IDを行キーに持つ | md表。固定列位置で `\|` split(build_map_prompt.rb L36-48) | ledger-audit D1/D5/D8: 同文の丸写し |
| 接続 | map-topology.md v2 表(From/To/種別/主路)138行、connections.json(寺町4MAP分)、topology/overseas-progression.json、atlas/*.svg | md表+JSON+SVG | 戸口の位置・幅は topology/spec/checklist/candidates の4か所に自然文、plan.json に画素矩形(D8) |
| 敵 | monsters.md(ID・名前・分類・出る場所・属性・弱点・役割・絵の状態・根拠)、dungeon-enemies.md(ダンジョン別)、enemy-allocation.md | md表 | 「出る場所」が3か所 |
| ボス | boss-gimmicks.md、monsters.md(中ボス・ラスボス) | md | 未実測 |
| 時期 | map-specifications の「時期」列、timeline.md、-kids/-fire などの差分は ID suffix で checklist に記述 | 文章+suffix | 時期差分は台帳に列が無い(推測: 文章のみ) |
| 決定 | decisions.md、Issue(#51 #144 等)、SKILL.md「決定」節、decor-pools.json の note、plan.json の look/assumptions | 文章。**構造化ゼロ**(決定ID・対象・日付の列が無い) | D2〜D7、D9: 畳・化石・勝手口・木・窓・戸口幅が台帳md に降りていない |
| 素材 | map-asset-registry.md(画像パス・status・採用記録リンク)、oblique-mocks/<MAP>/manifest.json(sit-oblique-manifest/1、input_sha と出力sha)、body-masks/*.json(register/links 計約34個) | md表+JSON | registry は画像1行、manifest は生成ステージ単位。両者を結ぶ列が無い(manifest に `ledger.row_id` はあるが一方向。oblique_build.py L626) |
| キャラ | art-direction.md、assets-policy.md、decisions.md | 文章 | sit-character-sprite は先に3つの md を「原文のまま読む」前提 |
| プロンプト材料 | oblique_build.py build_prompt(L513)が plan+decor-pools+connections から合成。build_map_prompt.rb が checklist+spec+topology から合成(ready 以外は abort) | 2系統が独立 | D10: oblique の edit-prompt に台帳原文が1語も入らない |
| 採用記録/没記録 | docs/production/2026*.md、-prompts/、checklist のセル内【2026-10-23 E2 の生成物は全て没】 | 文章。セル内に没を混在 | 没が checklist のTBDセルに埋まる(TRM-03/05)。採用状態を機械で拾えない |
| 検証 | scripts/verify_map_ledger.rb(md表を正本のまま検査)、tests/ 6本(1495行)、verify_*.py | あり | md 表の列位置依存。決定→生成物到達の検証は無い |
| 材料語彙 | decor-pools.json(床材方針・禁止語)、sit-diorama 規約(build_map_prompt.rb の固定文) | JSON+Ruby直書き | 語彙が JSON とスクリプトに二重 |

SKILL が読むもの(確認): sit-enemy-sprite=content-registry/monsters/dungeon-enemies/art-direction/assets-policy を「原文のまま」読む(SKILL.md L12)。sit-battle-background=content-registry+対象MAP原文+art-direction+戦闘レイアウトJSON(L24)。sit-character-sprite=art-direction+assets-policy+decisions(L18)。sit-field-background=oblique_build.py 一式。つまり**各スキルは人が読む md を LLM に読ませて曖昧に拾う**のが標準で、`MAP_ID → プロンプト` の決定論的な合成は oblique_build.py(寺町4MAP)だけが持つ。

## 2. 正規化テーブル設計

### 2.1 原則
1. 1事実=1行・1セル。複数ファイルに同じ値を書かない。他テーブルからは**ID参照**。
2. マスターは日本語。列名・値(状態・種別・時期)も日本語。ID は既存の英数字(TRM-05、TRM-05.door-back、M012)を**変えない**(map-id-renumber 20261019 の資産、アセットパス、manifest がこの ID を使用)。
3. 人が読む md 設計書は後述の「ビュー」。決定の逐語・日付は decisions 表にだけ書く。
4. JSON は台帳に登録された派生物(§3)。

### 2.2 テーブル一覧(`docs/ledger/` に1表=1CSV)
| 表 | 主キー | 主な列(日本語) | 外部キー | 備考・初期の元データ |
|---|---|---|---|---|
| エリア.csv | エリアID(teramachi 等) | 区域コード(TRM)・名称・目標枚数・特徴・図の座標 | — | areas.json/map-ids.json を取り込み(15行) |
| MAP.csv | MAP_ID(TRM-05) | エリアID・名称・時期(幼稚園/火災後…)・屋内外・状態・一言特徴・必須ルート・MAP固定制約・描画方式(斜め/戦闘背景) | エリアID | specifications/checklist/registry の4表を分解(130行) |
| 接続.csv | 接続ID(通番)または 端A+端B | 端A(TRM-05.door-hall)・端B・種別(edge/door/event/oneway)・向きの期待(反対/同じ)・方角A・方角B・無効になる時期・扉の位置文・戸口幅クラス | 端A→端.csv、端B→端.csv | topology v2 の138行を取り込み |
| 端.csv(戸口) | 端ID(TRM-05.door-back) | MAP_ID・壁/辺・位置文(北壁左端)・幅クラス(1人分/1.5人分/2人分)・高さクラス | MAP_ID | 戸口の自然文と画素矩形の元。D8 を解消 |
| 時期差分.csv | MAP_ID+時期 | 差分の種別(置換/焼失/追加)・対象(要素ID)・内容・出力サフィックス(-kids/-fire) | MAP_ID | TRM-05 の -kids/-fire 方針(D1)を1か所に |
| 要素.csv(MAP内の家具・物) | 要素ID(TRM-05.fossil) | MAP_ID・種別(家具/窓/木/石)・名称・個数・材質・色・形・大きさクラス・禁止事項・状態(確定/未定) | MAP_ID | plan.json の boxes[].look を台帳へ。化石の石(D4)をここで |
| 窓.csv | 窓ID | MAP_ID・壁・個数・種別・時期・置かない理由 | MAP_ID | windows.md を取り込み(D7) |
| エリア固定.csv | エリアID+項目 | 項目(机/台座/木/床材方針/禁止語)・値・出典決定ID | エリアID、決定ID | decor-pools.json の areas を取り込み |
| 語彙.csv | 語彙ID | 種別(材料/禁止語/文体)・日本語・英語プロンプト断片・適用範囲(全体/エリア/MAP) | エリアID(任意) | build_map_prompt.rb 固定文と decor-pools の方針文を統合 |
| 決定.csv | 決定ID(D-0031 など連番) | 日付・対象種別(エリア/MAP/要素/接続/敵…)・対象ID・決定の要点(1文)・逐語・出典(Issue #番号/コメントURL/ファイル)・状態(有効/撤回)・置換先決定ID・プロンプトへの出力(必須語/禁止語/なし) | 対象ID(種別ごとに対応表) | **外部キーが多態**(対象種別+対象ID)。検証で存在確認 |
| 敵.csv | 敵ID(M012) | 名前・分類・属性・弱点耐性・役割・絵の状態・根拠・サイズ種別(gridClass) | — | monsters.md の主表(M 86 + S 8)。ドロップ/ぬすむ/gridClass の副表は列に統合 |
| 敵配置.csv | 配置ID | 敵ID・MAP_IDまたはダンジョンID・時期・種別(通常/ボス/イベント)・理由 | 敵ID、MAP_ID | dungeon-enemies/enemy-allocation/monsters の「出る場所」を1表に(推測: 三者の食い違いが先に出る) |
| ボス.csv | ボスID | 敵ID・ギミック・フェーズ・勝利条件・BGM | 敵ID、BGM | boss-gimmicks.md |
| 素材.csv | 素材ID(通番) | MAP_ID/敵IDなど所有者・種別(背景/マスク/遮蔽/立ち絵/BGM)・パス・状態(採用/候補/没/legacy)・日付・来歴(生成元prompt、採用記録へのリンク)・sha256 | 所有者ID | registry 130行 + manifest 出力 + 没記録を統合。**没はここで状態=没(行を消さない)** |
| 生成物.csv(派生物台帳) | 生成物ID | 種別(plan/decor/接続図/edit-prompt/atlas)・パス・元の表と行・入力ハッシュ・生成日時・再生成コマンド・鮮度 | 所有者ID | §3.3 |
| BGM.csv ほか | 既存 bgm-*.csv | — | MAP_ID(割当) | 既存CSVを列に MAP_ID を足して継続 |
| 参照資料.csv | R番号 | 題・出典・メモ | — | map-reference-research.md |

注: 敵・ボス・BGM は第2段階以降(§5)。第1段階はエリア/MAP/接続/端/時期差分/要素/窓/エリア固定/語彙/決定/素材/生成物(寺町分)。

### 2.3 md を生成ビューにする方針の是非
- 利点: 重複が構造的に消える(D1〜D10 の原因が「同文を手で複写」)。回帰テストは表の存在確認だけで済む。
- 欠点/リスク: map-topology.md(94KB)の §3.1〜§9 は経緯・設計思想の**散文**が多く、表に落ちない(確認: 冒頭に「履歴記録」注記あり L311)。decisions.md/story.md/art-direction.md は本質的に文章。monsters.md の「役割」「根拠」も文章セルが長い。
- 推奨: **表で表せる部分だけ**ビューにする。具体的にはMAP表(spec/checklist/registry)・topology v2 の接続表・monsters 主表・dungeon-enemies の配置表。散文(story・art-direction・decisions の物語/美術の決定、topology の経緯節)は md のまま残し、台帳CSVの決定IDから**リンクする**だけにする。ビューは `docs/views/*.md`(先頭に「自動生成・編集禁止」)に出し、人が読む md は当面ビュー+従来散文の併存。

### 2.4 形式の推奨(kako-jun が直接編集・git差分・外部キー)
候補比較:
| 形式 | 直接編集 | git差分 | 日本語 | 外部キー | 既存整合 | 評価 |
|---|---|---|---|---|---|---|
| CSV(UTF-8、日本語ヘッダ) | Excel/LibreOffice/テキストで可。Agasteer(md中心)では扱いにくい(推測) | 1行=1レコードで行単位差分 | ◎ | ID列で表現 | bgm-*.csv が既にある、noun-gender 等も CSV 運用 | **推奨** |
| TSV | 同上。セル内にカンマを書ける | 同上 | ◎ | 同上 | 既存と不整合 | 惜しい。長文セルに `"` やカンマが多いなら有力 |
| md表 | 今の運用。Agasteer で編集可 | 長い行で差分が読みにくい。列追加で固定列位置のパーサが壊れる(確認: build_map_prompt.rb は contract_cells[2..5]) | ◎ | 同上 | 現状 | 列が10を超える表には不向き。**ビューとして残す** |
| YAML/JSONL | テキスト編集 | ◎ | ○ | 参照可 | 無し | 逐語を含む決定は書きやすいが、一覧・並べ替え・突合が不便 |
| 1決定=1md(frontmatter) | ◎(長文に最適) | ◎ | ◎ | frontmatter | 無し | 決定だけの代替案。件数が千超になるなら有力(推測) |

**推奨: CSV(UTF-8 BOM なし、LF、日本語ヘッダ、1表1ファイル、行は主キー昇順で固定=差分を最小に)**。決定.csv の逐語セルが長い問題だけ、必要なら「逐語」を `docs/ledger/決定逐語/D-0031.md` に分けて CSV の `逐語` 列にパスを書く逃げ道を残す。

日本語テーブルの具体例(列と値は日本語、外部キーはID+名称の併記。名称は表示用で検証対象外):

`docs/ledger/決定.csv`
```
決定ID,日付,対象種別,対象ID,対象名,決定の要点,逐語,出典,状態,プロンプト出力,必須語,禁止語
D-0412,2026-10-21,要素,TRM-05.floor,住居の床,畳は描かない。床は板張り,"畳がすごく不自然だ…",Issue #51,有効,必須,板張り,畳
D-0431,2026-10-23,要素,TRM-05.fossil,化石の石,茶色と黒の混ざった石(割っていない・拳大・渦巻き模様なし),"…",Issue #144,有効,必須,茶色と黒,アンモナイト模様
D-0432,2026-10-23,端,TRM-05.door-back,勝手口,北壁左端・幅1人分・TRM-06.door-house へ通じる・-fireで焼失,"勝手口は上辺の左端だ",Issue #144,有効,必須,,
```
`docs/ledger/端.csv`
```
端ID,MAP_ID,MAP名,壁,位置,幅クラス,高さクラス,備考
TRM-05.door-back,TRM-05,住居,北,左端,1人分,2人分,見落としやすい細い扉
```
`docs/ledger/接続.csv`
```
端A,端B,種別,向きの期待,方角A,方角B,無効になる時期,ラベル
TRM-05.door-back,TRM-06.door-house,戸口,指定,西,北,火災後,勝手口↔裏の細道
```
`docs/ledger/生成物.csv`
```
生成物ID,種別,パス,元の表と行,入力ハッシュ,生成日時,再生成コマンド,鮮度
G-TRM-05-plan,斜め計画JSON,docs/production/oblique-mocks/TRM-05-plan.json,MAP:TRM-05|端:TRM-05.*|要素:TRM-05.*|窓:TRM-05.*|エリア固定:teramachi,ab12cd34,2026-10-23T10:00,ruby scripts/ledger_build.rb plan TRM-05,最新
```
外部キーは**ID(英数字)を正本**、隣の「名」列は人間のための日本語表示。エリアや要素を日本語名で参照すると改名で壊れる(推測: 既存でも map-id-renumber 事件)ので、日本語名は参照キーにしない。名称併記の整合は検証で警告にする。

## 3. 導出パイプライン(日本語マスター → JSON派生 → プロンプト)

### 3.1 流れ
```
docs/ledger/*.csv (日本語マスター。人が書く)
   │ scripts/ledger_build.rb  (新。唯一の導出器。純関数: 表→JSON)
   ▼
派生JSON(描画直前に生成。手編集禁止)
   ├ <MAP>-plan.json           (sit-oblique-plan/1。座標・寸法は MAP/端/要素/窓 表から)
   ├ decor-pools.json          (エリア固定+語彙+禁止語+決定から)
   ├ connections*.json         (接続+端から)
   ├ dependency-graph.json      (MAP.依存 列から)
   └ MAP別 prompt-input.json    (決定の必須語・禁止語・時期差分を束ねる)
   │ oblique_build.py (既存。入力を派生JSONにするだけ。ロジックは残す)
   ▼
モック → マスク → 遮蔽 → edit-prompt → 生成 → 採用(manifest.json に入力ハッシュ)
```
- 座標・寸法の画素矩形は台帳に書かない。台帳は「北壁左端・幅1人分」のクラス値までを持つ。クラス→画素の換算は oblique_build.py の既存ロジックに任せる(推測: plan.json の矩形は幾何計算結果。確認: edit-prompt の COORDINATES は「plan とモックの射影から機械的に出した値」)。
- 自由文 `look` は要素.csv の「材質・色・形」列から組み立てる(plan の look を直書きしない)。これで漏れの根が消える。

### 3.2 MAP_ID → プロンプトの決定論
`ledger_build.rb prompt <MAP_ID> [--時期 kids]`:
1. MAP行→エリア→エリア固定・語彙→要素/窓/端/接続→有効な決定(対象がこのMAPまたはその要素/端/エリア)→時期差分、の順に**JOINして固定順に並べる**(並びは主キー昇順)。
2. 決定の「必須語」「禁止語」を FILL/FORBID 節に必ず入れる(status に依存しない。D10 解消)。
3. 英語プロンプト断片は語彙.csv から。直書きは禁止。
4. 同じ表が同じ入力なら同じ prompt(テンプレートは `docs/ledger/テンプレート/` またはスクリプトのバージョンも入力に含める)。

他スキルも同じ型で拡張(推測=第2段階以降):
- sit-enemy-sprite: `ledger_build.rb prompt-enemy M012` → 敵.csv+語彙+サイズ種別+決定。content-registry/monsters.md を丸読みしない。
- sit-battle-background: MAP_ID + 敵配置.csv で出る敵のサイズ・位置を引く。
- sit-character-sprite: キャラ.csv(今は未表。第3段階)。

### 3.3 入力ハッシュと manifest の関係
- 派生JSONの `生成物.csv` の「入力ハッシュ」= 入力の行(元の表と行のセル値を正規化直列化)+ ledger_build.rb バージョン文字列の sha256。
- 既存の manifest.json(ステージ別 input_sha、oblique_build.py L638)は**生成物ごとの再現性**を担保し続ける。違いは、input_sha に「派生JSONのハッシュ」が入ること(派生JSONの内容は台帳由来なので、台帳が変われば自動的に再生成扱い)。manifest の `ledger.row_id`(L626)は MAP_ID のまま使い、`ledger.input_sha`(派生JSONの sha)を足す。
- JSON ファイル自体の先頭(`_provenance` キー)にも同じ情報を埋める: `{"source":["MAP:TRM-05","端:TRM-05.*"],"input_sha":"...","generated_at":"...","command":"ruby scripts/ledger_build.rb plan TRM-05","do_not_edit":true}`。台帳の成果物欄(生成物.csv)と二重に持つが、前者は機械が検証する印、後者は人間が辿る一覧。両方は ledger_build.rb が同時に書く(手で書かない)。

## 4. 整合性検証(`scripts/verify_ledger.rb` 新、既存 verify は残す)
| 検査 | 内容 | 失敗の例 |
|---|---|---|
| 外部キー | 全FK列のIDが参照先の主キーに存在(MAP.エリアID、接続.端A/端B→端、端.MAP_ID、決定.対象ID は対象種別ごとの表、素材.所有者、敵配置.敵ID/MAP_ID) | 存在しないMAP_ID |
| 一意性・孤児 | 主キー重複なし。MAPに端も接続も無い孤児、どの接続からも指されない端、どのMAPにも属さない要素 | |
| 接続の対称性 | 接続の方向(反対/同じ)に対する方角A・Bの整合、双方向の取りこぼし、循環(許容種別=ループは明示)。現 topology の「反対辺」規則を機械化 | |
| 決定の到達 | **有効な決定すべてについて**、派生 prompt-input.json と生成済み edit-prompt.txt に必須語が入っていること、禁止語が肯定形で入っていないこと(ledger-audit 案(e)の回帰テスト)。撤回された決定の語が残っていないこと | 「畳」「茶色と黒」「勝手口」の漏れを検出 |
| 派生物の鮮度 | 生成物.csv の各行について、入力行から再計算したハッシュ==記録ハッシュ==JSONの `_provenance.input_sha`。不一致=「古い」でエラー | 台帳を直したのにJSON未再生成 |
| 台帳に無いJSON | `docs/production/**` の `*.json`(allowlist: 画像メタ等は `.ledger-ignore`)が、生成物.csv にパスとして登録されていること | 手書き plan.json |
| 手編集検知 | 派生JSONを再生成して内容が一致すること(ビルド→diff) | JSON 手編集 |
| ビュー鮮度 | docs/views/*.md を再生成してgit diff 0 | ビューだけ手編集 |
| 命名・列スキーマ | 列名・必須列・状態列の語彙(確定/未定 など日本語の許可リスト) | 「確定」の誤字 |
| 既存 md との突合(移行期のみ) | CSV と旧 md 表の同一セルが一致 | 移行期の二重管理 |

テストは tests/test_ledger.py(新、既存 tests/*.py の流儀に合わせる)で、CSVにわざと壊れた行を入れた fixture で失敗することを確認する(推測: 現 tests は同様の fixture 方式。未確認)。

## 5. 移行計画(寺町から)

### 第1段階: 寺町の最小DB化(TRM-01〜17、MAP 17行)
1. `docs/ledger/` を作り、エリア(15行は一括、areas.json から)・MAP(寺町17行)・端・接続(寺町分)・時期差分・要素(TRM-02〜05 の plan から)・窓(windows.md)・エリア固定+語彙(decor-pools.json)・決定(Issue #51/#144 と SKILL.md 決定節から。畳、化石の石、勝手口、木=松と枯木、本堂に窓なし、戸口幅クラス、寝室方針)・素材(寺町分の registry+manifest)・生成物を取り込む。**取り込みは一度きりのスクリプト**(md/JSON→CSV)で、以降は CSV が正本。
2. `ledger_build.rb` が plan/decor-pools/connections を台帳から再生成し、既存の手書きJSONと**一致するか**を差分で確認してから置換(差分が出れば、それが現在の食い違い=人に報告して直す)。
3. oblique_build.py: 入力を派生JSONに切替(パスは同じ)。edit-prompt に決定の必須語・禁止語を status 非依存で追加。ledger_gate(L588)の「ready 以外は台帳原文を省略」を廃止。
4. verify_ledger.rb と tests を追加。CI は **未確認**(.github/workflows が無い=ls で無し)ので、ローカル+PR チェックリストに入れる(推測)。
5. スキル更新: sit-field-background SKILL.md の「決定を受けたらまず決定.csv に書く→verify→再生成」の順序を冒頭に。Issueは参照のみ(「決定D-0431」)。

置換/残置(第1段階):
| 既存 | 扱い |
|---|---|
| map-contract-checklist/specifications/registry/candidates の寺町行 | 残す(消さない)。ただし「MAP.csv が正本」と先頭に明記し、新規書き込みは禁止。移行期は突合検査で一致を保つ。畳(spec:46 等)は MAP.csv 作成時に直し、旧 md も同じ PR で追従 |
| map-topology.md v2 表(寺町行) | 同上。接続.csv が正本、md は後でビュー化 |
| plan.json・decor-pools.json・connections*.json・windows.md | **派生物に格下げ**。手編集禁止、生成物.csv に登録。windows.md は窓.csv のビューへ |
| manifest.json | 残す(生成物の再現性。ledger.input_sha を追加) |
| build_map_prompt.rb | 残すが入力を CSV に切替(md の `\|` split を廃止)。後に ledger_build.rb へ統合(推測) |
| verify_map_ledger.rb・tests/test_map_*.py | 第1段階は残す。新検査は別ファイルで追加 |
| decisions.md | 残す(物語・美術の散文)。MAP制作の決定は決定.csv が正本とし、decisions.md には重複して書かない |
| SKILL.md の「決定」節 | 寺町の決定は決定.csv に移し、スキルには参照とルールだけ残す |

壊れうる箇所: ①build_map_prompt.rb と verify_map_ledger.rb が md の列位置・見出し文字列に依存(確認: L36-48、`'#### MAP相互接続台帳 v2'`)。列追加や見出し変更は旧スクリプトを落とす → 旧md は列追加せず、新CSVに寄せる。②manifest の input_sha が変わり、既存ステージが全て再生成扱い(想定内)。③areas.json の layout 座標(atlas/SVG 用)の持ち場所: エリア.csv に入れるとセル内座標の可読性が落ちる=layout は別表「配置座標.csv」にするか JSON のまま派生扱いに(推測)。④同一ID(TRM-05-kids/-fire)の時期差分の扱い: 時期差分.csv で suffix を管理。⑤並行 worktree で CSV 末尾追記が衝突(行順固定+主キー昇順で緩和)。

### 第2段階: 敵・ボス・戦闘背景
敵.csv(M 86+S 8)、敵配置.csv、ボス.csv。三つの md の食い違い洗い出し結果は先に kako-jun に一覧報告(広範な監査は一覧→判断の運用)。sit-enemy-sprite/sit-battle-background を CSV 駆動に。monsters.md/dungeon-enemies.md の表はビュー化。

### 第3段階: 他エリア・BGM・キャラ・ビュー化
KRB・NTB 等のMAPを制作順に決定.csv/要素.csv へ(全130を遡及で埋めない=新規制作時に)。bgm-*.csv に MAP_ID 列、キャラ.csv。表のmdを docs/views/ に生成して旧 md を撤去。atlas/topology SVG(render_*.rb)の入力を CSV に。

## 6. kako-jun に決めてほしい点(3点・推奨つき)
1. **マスターの形式**: 日本語ヘッダの CSV(`docs/ledger/*.csv`、ID は英数字維持)を推奨。代案=md表(今の運用、編集は楽だが差分と列追加に弱い)、決定だけ1決定=1mdファイル。編集環境(Excel等かテキストか)を教えてほしい。
2. **md設計書の扱い**: 表で表せる部分(MAP表・接続表・敵主表)だけ**生成ビュー(編集禁止)**にし、散文(物語・美術・経緯)は md のまま残す。推奨=この折衷。全面ビュー化は散文が壊れるので非推奨。
3. **段階**: 第1段階は寺町17MAPのみ+決定.csv。旧 md の寺町行は消さず、突合検査で併存→一致確認後に「MAP.csv が正本」と明記。推奨=この順。(敵の移行は一覧報告後に第2段階。)

## 付録: 推測として扱った点
- CI が無い(ls .github/workflows でマッチなし。zsh の glob 失敗)=リポ全体の実態は未確認。
- tests/ の fixture 方式、Agasteer での CSV 編集性、三者敵配置の食い違い、spec 133行の内訳は未確認。
- 敵・ボス・BGM・キャラの記述は規模確認まで。内容の重複実測は未実施。

---

# 追補(必須要件 1〜4 への対応)

## 7. 建物(構造物)テーブル: 屋内と外観が同じ行から導出される

### 7.1 実例の確認(事実)
- TRM-03-plan.json(外観)の渡り廊下は `kind: "roof-passage"` が2箇所(L99, L133)。look は「柱と低い灰色の瓦屋根だけの開放した通路。床は木の板張り(確定)。壁・窓・格子・戸を描かない」。
- 同ファイルの assumptions(L354)に「渡り廊下は柱で支えるだけの開放通路に変更(kako-jun 2026-10-23『左右を行き来する開口部は壁に見えないように』)。旧の廊下棟の窓列(既定)は廃止」とある。つまり**この決定は plan.json の自由文 assumptions にだけ**あり、屋内側(TRM-04/05/02)と結ぶ列が無い。依頼文にある「#51 の決定『外観の廊下棟に窓列』『廊下の南壁に外観と同じ窓列』」と新決定の間で、どちらが有効かを表から判別できない。map-topology.md L142/L578/L587 は渡り廊下を「TRM-04.door-west↔TRM-05.door-hall」の接続の説明文にだけ書き、**建物としての行は無い**(確認: grep)。屋内の廊下の南壁の窓列が今どうなっているかは未確認。
- 構造的な原因: 渡り廊下という実体が、屋内3MAP・外観1MAP・topology 文・plan の look/assumptions の5箇所に別々に書かれる。同じ事実の「持ち主」が決まっていない。

### 7.2 建物系テーブル(追加)
| 表 | 主キー | 列(日本語) | 外部キー |
|---|---|---|---|
| 建物.csv | 建物ID(BLD-TRM-honden、BLD-TRM-corridor-w、BLD-TRM-corridor-e、BLD-TRM-jukyo、BLD-TRM-youchien) | 名称・エリアID・種別(棟/渡り廊下棟/門/塔)・平面寸法クラス(幅/奥行/高さ)・屋根(形・材・色)・外壁(材・色・壁の有無=閉/開放)・床材・階数・状態 | エリアID |
| 建物部位.csv | 部位ID(BLD-TRM-corridor-w.south-wall) | 建物ID・部位種別(壁/屋根/柱列/窓列/扉)・方角・材質・状態(閉/開放/なし)・備考 | 建物ID |
| 建物窓列.csv | 窓列ID | 建物ID・部位ID・個数・並び(等間隔/位置指定)・窓種別・時期・理由 | 建物ID、部位ID |
| 建物扉.csv | 扉ID(=端ID 共有) | 建物ID・部位ID・幅クラス・高さクラス・意匠(引き戸/板戸/開口)・時期差分 | 建物ID、端ID |
| 建物関係.csv | 通番 | 建物A・建物B・関係(隣接/渡り廊下で接続/内包)・方角・接続の端ID | 建物ID×2、端ID |
| 建物時期差分.csv | 建物ID+時期 | 時期(幼稚園/火災後)・部位ID・差分(焼失/改築/追加)・内容 | 建物ID、部位ID |
| MAP表の追加列 | — | `建物ID`(屋内MAPが属する棟)、`表現する部位`(屋内=内側、外観=外側) | 建物ID |

寺町の初期行(例。値は推測の叩き台で、既存決定からの転記時に埋める):
```
建物ID,名称,種別,外壁,屋根,床材,状態
BLD-TRM-corridor-w,西の渡り廊下(本堂-住居),渡り廊下棟,開放(柱のみ),低い灰色の瓦,木の板張り,有効
部位ID,建物ID,部位種別,方角,状態,備考
BLD-TRM-corridor-w.south-wall,BLD-TRM-corridor-w,壁,南,開放,決定D-0xxx(2026-10-23)で開放通路。窓列なし
建物関係:  BLD-TRM-honden , BLD-TRM-corridor-w , 渡り廊下で接続 , 西 , TRM-04.door-west
建物関係:  BLD-TRM-corridor-w , BLD-TRM-jukyo , 渡り廊下で接続 , 西 , TRM-05.door-hall
```
MAP との関係: TRM-04/TRM-05 は建物.csv の本堂棟/住居棟に属し、TRM-03 外観の「建物に見える範囲」は同じ建物行の外壁・屋根・窓列を描く。屋内の廊下的な部分(TRM-04.door-west の先)も建物 `BLD-TRM-corridor-w` を参照する。外観・屋内ともに「南壁=開放」という値が**1箇所**にしか無いので、片方だけ窓列を持つことは構造的に書けない(窓列は建物窓列.csv に1行だけ。開放と窓列が両立しない旨は検証で検出)。

### 7.3 食い違いうる事項と一意になる行(対応表)
| 食い違いうる事項 | 一意になるテーブルの1行 | 屋内・外観の導出元 |
|---|---|---|
| 渡り廊下の壁の有無・屋根 | 建物部位.csv `BLD-TRM-corridor-w.south-wall` | 屋内MAPの壁/外観の壁 |
| 窓列(個数・位置・種別) | 建物窓列.csv(窓列ID) | 屋内の窓(窓.csv は窓列IDを参照)/外観の窓 |
| 扉のデザイン・幅・高さ | 建物扉.csv(扉ID=端ID) | 屋内の戸口・外観の戸口・端.csv の位置 |
| 屋内の接続口と外観の戸口の位置・幅 | 端.csv の1行を屋内側・外観側の2つのMAPが参照(例 TRM-05.door-outside と TRM-03.door-residence は接続.csv の1行で結ばれ、幅クラスは建物扉.csv 側に1個) | |
| 床材(畳をやめる、板張り) | 建物.csv の床材(建物単位)+エリア固定.csv(エリア共通) | 屋内床/外観の渡り廊下床 |
| 家具(固定の机・コンロ等) | 要素.csv(MAP_ID所属)。屋外からも見える要素は `外観に見える` フラグで外観が参照 | |
| 時期別差分(-kids/-fire) | 建物時期差分.csv(建物+時期) | 屋内・外観の両方の時期別出力 |
| 屋根・外壁の材質・色 | 建物.csv | 外観/屋内の天井・壁面の質感 |
| 建物間の位置関係(本堂-渡り廊下-住居) | 建物関係.csv | topology 図/外観の配置/屋内の接続方角 |
| 木・石・池などの敷地の物 | 要素.csv(所属=外観MAP/エリア)+エリア固定.csv | |
| 決定そのもの(日付・逐語) | 決定.csv(対象=建物/部位/窓列/扉…) | すべて決定IDで参照 |
| 敵の出る場所 | 敵配置.csv | monsters/dungeon-enemies/enemy-allocation |

### 7.4 起きないことの説明(今回の渡り廊下ケース)
1. 決定を受けたら、まず `決定.csv` に1行(対象=BLD-TRM-corridor-w.south-wall、要点=開放通路、必須語/禁止語=「壁・窓・格子・戸を描かない」)。
2. その部位行の状態を `開放` に更新(同じ変更でないと verify が落ちる: 「有効な決定の対象と状態が不一致」)。
3. 屋内 TRM-04/05 の prompt-input と外観 TRM-03 の prompt-input は、**どちらも同じ部位行を JOIN して作る**。外観だけ開放、屋内だけ窓列、という状態は入力に出ない。
4. 旧決定(窓列あり)は決定.csv の状態=撤回、置換先=新決定。窓列行は建物窓列.csv から削除または状態=廃止。検証「撤回済み決定が対象に残っていない」「有効な部位に窓列と開放が同居しない」「建物窓列.csv に行があるのに部位状態が開放」で落ちる。
5. 屋内に窓列が必要という決定が残っていたら、決定.csv に「有効かつ矛盾する2決定」(同じ対象・同じ属性)があるので、検証が**決定間の矛盾**を検出(対象ID+属性が同じ有効決定が2行ならエラー)。→ 今回はどちらを採るかを kako-jun が決める必要があった問題を、書込み時点で露出させる。

## 8. 決定の入口を1つにする運用と Issue 点検
- 入口: 決定.csv。Issue/PR/スキルは「D-0431」と参照するだけ。スキルの冒頭に、決定を受けたら「①決定.csv ②対象表の更新 ③verify_ledger.rb ④ledger_build.rb 再生成 ⑤Issue に決定IDを書く」の順を明記。
- 検査の弱点: Issue にしかない決定。**点検スクリプト案** `scripts/audit_issue_decisions.rb`(推測。gh CLI 使用):
  1. 対象Issue(sit-by-me の MAP制作関連=issue-map.md に載る番号、または `--issues 51,144,...`)のコメントを `gh issue view --comments --json` で取得。
  2. 投稿者が kako-jun のコメントのうち、日付(2026-10-23 等)・「決定」「確定」「〜にする」「やめる」などの語を含むものを候補として抽出(ヒューリスティック=見落としあり、が弱点)。
  3. 決定.csv の「出典」列(Issue #N とコメントURL/ID)に含まれないコメントを**未記録候補**として列挙(`audit-issue-decisions.md` に出力。台帳には書かない)。
  4. 人(またはサブエージェント)が各候補を「決定→決定.csv に追加/決定ではない→`ignore-comments.csv`(コメントID,理由)に追加」と**必ず分類**。分類済みの数を確認し、未分類が0になるまで /impl のマージ前チェックにする。
  5. 逆向き: 決定.csv の出典のコメントが実在するか(リンク切れ)。
- 運用ルール: Issue に決定を書いた会話の最後に、その決定が決定.csv にあることを確認(スキルのチェックリスト)。これは機械化できないため点検スクリプトで事後にも拾う。「過去に伝えたことが Issue にしかない」状態の一括救出は、第1段階の最初に寺町関連 Issue(#51 #60 #144 ほか issue-map.md の寺町関連)に対して1回走らせ、未記録候補を全部分類して決定.csv に取り込む(これを第1段階の手順0とする)。

## 9. 画像生成の依存順と建物テーブル
- 依存順(確認: TRM-03-plan.json `depends_on: [TRM-04, TRM-05, TRM-02]`、checklist の「本堂 TRM-04 確定→住居→幼稚園→外観の直列」): 屋内確定 → 外観。
- 導出の入力:
  - 屋内 MAP の prompt-input = MAP行 + 所属建物行 + 部位/窓列/扉(内側面) + 要素 + 端/接続 + エリア固定 + 語彙 + 有効な決定 + 時期差分。
  - 外観 MAP(TRM-03)の prompt-input = MAP行 + **建物行(外壁/屋根/窓列/扉/材質/時期差分、外側面) + 建物関係(配置)** + 外観の要素(木・池・墓・遊具)+ エリア固定 + 語彙 + 有効な決定 + **確定済み屋内画像(素材.csv で状態=採用・MAP∈depends_on のもの)を参考画像として添付**。
  - 生成物.csv の入力ハッシュに「依存MAPの採用画像 sha256」も含める。→ 屋内を採り直すと、外観の生成物が自動的に「古い」と判定される。
  - 順序は MAP.csv の `依存MAP` 列(dependency-graph.json はここから派生)。未採用の依存MAPがあれば ledger_build.rb が外観 prompt の生成を拒否(今の「ready でなければ BLOCKED」の置換で、決定の漏れではなく**依存の未充足**だけを理由にする)。
- 参考画像は「建物行の事実を見た目で補う」位置づけ。建物行と参考画像が食い違ったら建物行が勝つ(prompt に明記。画像は幾何と質感の参考)。

## 10. 移行計画への反映(§5 第1段階の差分)
手順0: 寺町関連Issueの未記録決定の救出(§8)。手順0.5: 建物テーブルの作成(本堂棟・住居棟・幼稚園棟・渡り廊下棟(西・東)、寺町分で約5〜6行)。手順1以降は §5 に従う。検証に §7.4 の4項目(決定間の矛盾、撤回済み決定の残存、部位状態と窓列の不一致、依存MAP採用画像のハッシュ)を追加。
第1段階の kako-jun 決めてほしい点に追加(4点目): 渡り廊下の現行決定(開放通路か、窓列付きの廊下棟か)。屋内の廊下の現状が未確認のため、移行の手順0で食い違いとして報告する。
