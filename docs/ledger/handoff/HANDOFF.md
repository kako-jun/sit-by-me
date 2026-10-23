# 【最優先の決定（2026-10-23 セッション終了間際）: 台帳の形式は CSV でなく YAML】

kako-jun「csvが本当にいいのか？yamlとかのほうが管理しやすいのではないのか」「JSONもyamlのほうがいいのではないのか」→ 提案「人が編集するものは YAML、機械が作る派生物は JSON のまま」に「よい」。

- 理由: 決定の逐語・自由記述（複数行の文章）、建物の窓列・部位・時期差分（入れ子）、コメントが CSV では扱いにくい。YAML は複数行ブロック・入れ子・コメントが自然で、1エンティティ1ファイルにすると差分が読みやすく kako-jun も直接編集しやすい。
- **マスター（人が書く）= YAML**（全テーブル。接続・敵配置などの単純な行の列も YAML のリスト）。`map-ids.json`・`areas.json`・`dependency-graph.json` など人が編集している JSON も YAML のマスターへ合流。
- **派生物（機械が作る）= JSON のまま**（plan・decor-pools・connections・manifest。ファイル先頭のメタデータに入力ハッシュ・生成日時・再生成コマンド。既存の斜めツール(Python)・検証(Ruby)・テスト・ゲーム実行側が JSON を読むため）。
- **人が読む一覧 = 台帳（YAML）からの md ビュー**。
- 実装済みの24表（CSV・364行）は `ledger_io.py` のスキーマを使って YAML へ自動変換する小さなスクリプトを作る（WIP の今が最も安い時期）。**第0段階（INDEX・配置表・到達性検証）を始める前に変換する**。検証は YAML スキーマ（必須キー定義を含む）＋外部キー存在検査。以下の本文中の「CSV」は「YAML」に読み替える（`docs/ledger/*.csv` → `docs/ledger/**/*.yaml`）。

# 台帳DB化 引き継ぎ（WIP。2026-10-23 セッション終了時点）

この置き場は一時的。第1段階の完了時に内容を台帳へ吸収してこの `handoff/` ごと削除する（INDEX の到達性検証では許可リスト『handoff（第1段階完了時に台帳へ吸収して削除）』）。

## 目的・目標
Issue #156（https://github.com/kako-jun/sit-by-me/issues/156）が正本。要点: 日本語ヘッダの CSV（`docs/ledger/*.csv`）を**情報の唯一のマスター**にし、エリア・MAP・建物・接続・要素・窓・決定・採用要素…を別表にして ID で関連づけ、重複をなくし、スキルが台帳から**一意にプロンプトを作る**（再現性）。Issue は台帳に書くまでの仮。kako-jun の指示の逐語は #156 本文。設計の承認は「まかせる」（#144 コメント）。

## 承認済み設計の要点
- マスター=CSV（UTF-8・LF・日本語列名・IDは既存英数字維持）。md は表にできる部分だけ生成ビュー。
- JSON（plan・decor-pools・connections・dependency-graph）は台帳から導出する派生物。`_provenance`（入力ハッシュ・生成日時・コマンド）を持ち、`生成物.csv` に登録して鮮度検査。
- 必須キー（`必須キー.csv`）: 欠落=エラー、語彙外=エラー、『未決(要確認)』は `未決.csv` に載せる。必須キーが揃わないMAPは `oblique_build.py` が起動しない。
- 各表に任意の `特徴(自由記述)` 欄。プロンプトの FEATURES 節にそのまま入る。
- 決定は status に関係なく必ずプロンプトに入る（旧 ledger_gate は廃止）。採用要素（継承要素）は参考画像とプロンプトの両方で次の絵へ。
- 屋内と外観は建物表の同じ行から導出（渡り廊下棟は TRM-04 採用画像に一致: 閉じた壁・南壁に連窓3・板張り・低い瓦屋根）。
- 段階: 第0=INDEX・ファイル配置、第1=寺町（TRM-02〜17）、第2=体内・全MAP、第3=敵・素材・人物。

## どこまで済んだか（このブランチの実装）
- 表（docs/ledger/）24枚: エリア15・MAP17（寺町）・建物5・建物部位・建物窓列・建物関係・建物時期差分・端・接続・接続図設定・要素・窓・時期差分・既定値・エリア固定・装飾プール・語彙・決定67（有効+訂正済み）・採用要素6・素材・生成物・必須キー62・未決45・キー別名。
- ツール（.claude/skills/sit-field-background/tools/）: `ledger_io.py`（表定義 SCHEMA）・`ledger_flat.py`・`ledger_build.py`（導出器: plan/decor/connections/dependency-graph。`build`/`check`/`template`）・`ledger_query.py`（MAP→プロンプト台帳節）・`ledger_migrate_once.py`（一度きりの移行。再実行禁止）。`oblique_build.py` は必須キーゲート＋台帳節をプロンプトに入れる版（PROMPT_VERSION /5）。
- 検証（scripts/）: `ledger_csv.rb`・`ledger_required_keys.rb`・`verify_ledger.rb`（外部キー・一意・循環・必須キー・語彙・別名・決定整合・建物窓列・生成物鮮度・自由記述警告）。`verify_ledger.rb` は PASS（24表・決定67・警告0）。`verify_map_ledger.rb`・`verify_map_atlas.rb` は PASS（旧 md は併存）。
- 意図的な修正（移行後のJSON差分）: 畳の語の除去、化石の石（決定表から展開）、-fire の勝手口 prompt（西壁→北壁）、TRM-03 の渡り廊下棟（roof-passage を取り消し→建物行から導出・連窓6を追加）、TRM-04 廊下窓の状態（既定→確定）、決定文の写し→決定参照。移行そのものは plan/decor/connections/dependency-graph とも無損失（`curation-scripts/compare_json_roundtrip.py`）。
- main（TRM-01 統合・TRM-08.top 閉鎖）を merge 済み。atlas は 129MAP/136接続。
- 生成: 寺町4 plan（TRM-02〜05＋-kids・-fire）のモック・マスク・プロンプトを再生成済み（画像生成はしていない）。TRM-05-fire のプロンプトに決定67件のうち該当分・継承要素・参考画像・自由記述が入ることを確認。

## 未着手・未了（次にやる順序）
1. **WIP の検証を通す**: `ruby scripts/verify_ledger.rb`（PASS）、`ruby scripts/verify_map_ledger.rb`、`ruby scripts/verify_map_atlas.rb`、`uv run python3 -m unittest discover -s tests`（既存の失敗52件から増えないこと。一覧 `existing-test-failures-52.txt`。main と同じ集合）。TRM-04 の採用記録 `manifest.adoption.plan_sha256` は plan 再生成で古くなる: 幾何不変（clean.png の sha 同一）を確認してから rebaseline を記録する。
2. 第0段階: `docs/INDEX.md`（表は台帳からの生成ビュー）・`ファイル配置.csv`（asset-layout.md・verify_asset_layout.py と合流。verification/・weapons・body-*・oblique-* の規則）・`verify_index_reachable.rb`（孤立ファイルをエラー。許可リストに handoff を理由つきで）。docs/issue-map.md を INDEX の入口に。
3. 第1段階の残り: (a) `verify_prompt_reflects_ledger.rb`（決定ID・必須語・継承要素・自由記述がプロンプトに現れるか。漏れ=畳・化石の石・勝手口・火事版の上半分・渡り廊下の窓列を検出するテスト）と `tests/test_ledger.py`（壊れた fixture で失敗すること。`LEDGER_ROOT` で root を差し替え可）。(b) `audit_issue_decisions.rb`（Issue コメントの決定候補と決定表の差分。`Issue点検.csv` で分類）。(c) TRM-06〜17: teramachi-rest ブランチ（teramachi-rest-mocks-20261023。読むだけ）の plan 12個・connections-teramachi.json・teramachi-assumptions.md・oblique-masks/README.md の 2026-10-23 の決定を MAP・接続・決定・未決へ取込み。(d) コード内定数の台帳化: oblique_mock.py の幅クラス/視点/マステ座標、oblique_build.py・oblique_topology.py（L382）の直書き文。(e) `build_map_prompt.rb`・`verify_map_ledger.rb` の旧 md 列位置依存を CSV 参照へ。(f) 旧 md 突合: 畳（specifications:46・contract-checklist:57・topology:290）、TBD の勝手口・戸口幅、TRM-05 寝室方針の3表重複、`teramachi-rebuild-candidates.md` を参照のみに、legacy status は寺町だけ廃止。(g) 測定器: 火事版の上半分（火の色の領域が上半分に限られるか）・採用要素（みかん等）の存在確認を参考表示に。(h) SKILL.md・tools/README・docs 冒頭に運用（決定は先に台帳・必須キーと自由記述）。(i) `md ビュー` の生成と鮮度検査。(j) 既定値 `TRM-05.door-back` の旧 assumptions 2件（a08/a09）は a04 に統合済み。
4. 独立レビュー（sonnet 以下。コードレビューは opus 可だが上限は現行メイン以下）→ PR → マージ。第2段階以降は #156 のチェックリスト。

## 実行コマンド
- 台帳の検証: `ruby scripts/verify_ledger.rb`
- 派生JSONの再生成/検査: `cd .claude/skills/sit-field-background/tools && uv run python3 ledger_build.py build|check`
- 必須キーの雛形: `uv run python3 ledger_build.py template area|map ID`
- MAPの必須キー欠落: `ruby scripts/ledger_required_keys.rb TRM-05`
- プロンプトの台帳節: `uv run python3 ledger_query.py TRM-05-fire`
- 一括ビルド: `cd docs/production/oblique-mocks && uv run --with numpy --with opencv-python-headless --with pillow python3 -I ../../../.claude/skills/sit-field-background/tools/oblique_build.py --all connections.json`
- Python は必ず `uv run python3`（素の python3 は壊れている）。Ruby の csv gem は無い（`ledger_csv.rb` が自前）。

## 既知の問題
- 既存テストの失敗52件は main と同じ集合（`existing-test-failures-52.txt`。test_asset_migration 43・test_map_id_renumber 8 ほか）。台帳と無関係。
- 決定の `出典` が『会話（Issue #144 に記録）』の4件（TRM.required-keys・free-text・index ほか）は Issue コメントへの記録が未了（#156 本文に逐語あり）。
- `TRM-05.mikan` の素材IDは空（採用画像の確定後に紐付け）。`未決.csv` に45件（TRM-06〜17 の壁材・窓・時期差分・装飾プール、依存要確認ほか）。
- 接続: `TRM-05.door-back⇄TRM-06.door-house` は接続.csv に無い（topology v2 に行が無く、追加は atlas の件数に波及。第1段階の残りで topology と一緒に足す）。
- curation-scripts/ はこのセッションの台帳データ作成スクリプト（記録用。再実行すると手修正が消える）。

## 注意
- **画像生成は停止中**。再開は台帳整理の完了＋kako-jun の指示後。生成画像は Claude は見ない（kako-jun が見る）。
- Issue にだけ書かない: 決定は先に `決定.csv`、Issue は決定IDを参照。
- worktree/ブランチ: 本作業 `~/repos/2026/sit-by-me-wt-ledger-master`（ledger-master-phase1-20261023）。他: `sit-by-me-wt-oblique`（oblique-mask-tools-20261023。別担当）、`sit-by-me-wt-teramachi-rest`（teramachi-rest-mocks-20261023。読むだけ）、`sit-by-me`（本体）。git stash 禁止。コミットに Co-Authored-By を付けない。
