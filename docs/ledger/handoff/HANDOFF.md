# 現行台帳との照合（2026-10-26・WIP）

表（docs/ledger/）67枚。決定472（有効464・訂正済み8）、`未決.yaml` に1941件、`ファイル配置.yaml`（55規則）。これは格納行数の実測であり、意味点検や移行の完了件数ではない。U-050を含む未決を維持し、Issue出典1988件・命題3020件の意味点検は未完了（要確認42件、見出しによる自動分類432件と規則による機械仕分け825件は節ごとの精読が未了）。

現在の件数・列・配置規則は [INDEXの生成ビュー](../../INDEX.md#台帳の生成ビュー) でも確認する。この節の実測と以下の歴史的スナップショットを混同しない。

以下は第1段階時点の引き継ぎ履歴。本文の旧件数・未着手・マージ待ちは当時の状態を示す。現行の保存点と次手は [移行再開メモ](../MIGRATION-RESUME.md)、削除ゲートは [移行の合流点検](../migration-closure.md) を参照する。固有情報の照合が残るため、この履歴はまだ削除しない。

# 【最優先の決定（2026-10-23 セッション終了間際）: 台帳の形式は CSV でなく YAML】

kako-jun「csvが本当にいいのか？yamlとかのほうが管理しやすいのではないのか」「JSONもyamlのほうがいいのではないのか」→ 提案「人が編集するものは YAML、機械が作る派生物は JSON のまま」に「よい」。

- 理由: 決定の逐語・自由記述（複数行の文章）、建物の窓列・部位・時期差分（入れ子）、コメントが CSV では扱いにくい。YAML は複数行ブロック・入れ子・コメントが自然で、1エンティティ1ファイルにすると差分が読みやすく kako-jun も直接編集しやすい。
- **マスター（人が書く）= YAML**（全テーブル。接続・敵配置などの単純な行の列も YAML のリスト）。`map-ids.json`・`areas.json`・`dependency-graph.json` など人が編集している JSON も YAML のマスターへ合流。
- **派生物（機械が作る）= JSON のまま**（plan・decor-pools・connections・manifest。ファイル先頭のメタデータに入力ハッシュ・生成日時・再生成コマンド。既存の斜めツール(Python)・検証(Ruby)・テスト・ゲーム実行側が JSON を読むため）。
- **人が読む一覧 = 台帳（YAML）からの md ビュー**。
- 当時実装済みだった24表（CSV・364行。変換時点の数値）は `ledger_io.py` のスキーマを使って YAML へ自動変換する小さなスクリプトを作る（WIP の今が最も安い時期）。**第0段階（INDEX・配置表・到達性検証）を始める前に変換する**。→ **2026-10-24 変換済み**（下記「実施済み」）。検証は YAML スキーマ（必須キー定義を含む）＋外部キー存在検査。以下の本文中の「CSV」は「YAML」に読み替える（`docs/ledger/*.csv` → `docs/ledger/**/*.yaml`）。

**実施済み（2026-10-24）**: 当時の24表764行（変換時点の数値）を `docs/ledger/<表名>.yaml`（表ごと1ファイル・行のリスト・日本語キー・全スカラー引用つき文字列・先頭に表の説明コメント）へ無損失変換し、CSV は削除。
- 変換器 `.claude/skills/sit-field-background/tools/ledger_csv_to_yaml_once.py`（一度きり。`--verify-only` で コミット 40bf95d の CSV と突合の再検査ができる）。
- Python: `ledger_io.py` の `read`/`write` は据え置き、内部を YAML に差し替え（PyYAML はリポ直下 `pyproject.toml` で依存宣言。`uv run python3` で自動導入）。
- Ruby: `scripts/ledger_csv.rb` → `scripts/ledger_yaml.rb`（標準 `yaml`。全値を文字列へ正規化）。Ruby は Homebrew の 4.x が要る（macOS 標準の 2.6 は `verify_ledger.rb` の構文で動かない: `PATH=/opt/homebrew/opt/ruby/bin:$PATH`）。
- 以降の本文中の `*.csv`・「CSV」は YAML に読み替え済み（歴史的記述を除く）。他の記録文書（ledger-db-design.md・local-orphans.md・curation-scripts/）は当時のままで、読むときは同様に読み替える。


# 【第1段階の進捗（2026-10-24）】
- (a)(b)(c) 実施済み（prompt反映検査・Issue点検・TRM-06〜17取込み）。**(d)(e)(f)(h)(i) 実施済み**:
  - (d) 斜めツールの直書き定数・文面 → 新表 `描画定数.yaml`・`プロンプト文面.yaml`（`oblique_text.py` が読む。`verify_ledger.rb` がコードと台帳の対応を検査）。出力は変更前後でバイト一致。コード内に残したもの（色・乱数・検査の閾値・診断メッセージ・表の見出し・FONT）と理由は `tools/README.md`。
  - (e) 旧mdは見出し行の列名で読む（`scripts/md_table.rb`）: build_map_prompt.rb・verify_map_ledger.rb・map_graph.rb・render_map_atlas.rb。**第2段階で置換済み**: render_sunnyland_topology.rb（サニーランドのMAP仕様は列名で確認し、接続は台帳参照）。未対応: render_body_topology.rb・render_late_topology.rb。
  - (f) 畳の記述を TRM.no-tatami と整合、確定済みの戸口の位置・幅のTBDを台帳参照に、TRM-05 寝室方針の3表重複を決定ID参照に、`teramachi-rebuild-candidates.md` を参照のみに、寺町の legacy status を『台帳』に（verify_map_ledger が強制）。
  - (h) 運用を SKILL.md・tools/README・INDEX 冒頭に明記。(i) `docs/ledger-views/*.md`（`ledger_views.py build|check`。verify_ledger.rb が検査）。
- 残り: (g) 測定器、(j) 既定値の統合、Issue点検の未反映（要取込み）378 件の仕分け（見出し『決定』の38件優先）、建物表の入れ子化、独立レビュー（opus）→PR。第2段階（体内・全MAP）。

# 【handoff/ の削除手順（第2段階以降で実施。ここには手順だけ書く。削除そのものはまだしない）】
`docs/ledger/handoff/` の各ファイルの行き先（吸収してから `git rm`。1コミットずつ、`ledger_index.py build`・`ruby scripts/verify_index_reachable.rb` を通す）:
1. `ledger-db-design.md`（設計の背景・採用理由。残す価値がある）→ `git mv` で `docs/ledger/DESIGN.md`（台帳の設計文書）へ。中の『CSV』は YAML に読み替えて冒頭に一文注記する。`ファイル配置.yaml` に `docs/ledger/DESIGN.md`（到達=リンク）の規則を足し、`docs/INDEX.md` の台帳の節にリンクを張る。
2. `existing-test-failures-52.txt`（既存テスト失敗の基準線）→ `git mv` で `tests/known-failures-baseline.txt` へ。`ファイル配置.yaml` に規則を足し、`tests/` の README か INDEX から参照する（基準線は main と同じ集合の失敗一覧。減ったら更新）。
3. `decisions-59.jsonl`（決定の初期取り込み用データ）→ **第1段階の再レビュー対応で `git rm` 済み**。59件の決定IDは全て `決定.yaml` にあり、逐語は一致（TRM-05.mask-values の1件だけ、実在する発言の引用に訂正済み）、決定の要点は3件（TRM-03.corridor・TRM-05.door-back・TRM.open-passage）が決定表のほうが新しい。吸収するものは残っていない。
4. `curation-scripts/`（移行時の一度きりのデータ作成スクリプト。再実行すると手修正が消える）→ `git rm -r`。履歴は git に残る。
5. `HANDOFF.md`・`ledger-audit.md`・`local-orphans.md` → 内容は台帳（Issue点検・決定・未決・ファイル配置）・tools/README・SKILL.md・INDEX に吸収済みなので `git rm`（`ledger-audit.md`・`local-orphans.md` は当時の調査記録。必要な事実が台帳に載っていることを確認してから消す）。
6. 最後に `ファイル配置.yaml` の `ledger-handoff` 規則を削除し、`docs/INDEX.md` の『引き継ぎ』リンクを外して `uv run python3 .claude/skills/sit-field-background/tools/ledger_index.py build`、`tests/test_ledger.py` の `ignore_patterns("handoff")`（fixture のコピー除外）を外す。`verify_ledger.rb`・`verify_index_reachable.rb`・`uv run python3 -m unittest tests.test_ledger` を通してコミット。

# 【マージ手順（PR を main に入れるとき）】
- **squash マージし、マージ後にこのブランチ（ledger-master-phase1-20261023）を削除する**。ブランチの旧コミットには、公開リポに載せない絶対パス（ローカルのホーム配下）や codex のセッション ID が残っている（現行ツリーからは除去済みで `NoLocalPathsTests` が検査するが、履歴は書き換えない）。squash なら main の履歴にはそれらが入らない。通常マージ・rebase マージはしない。
- `--check-quotes` が保証するのは『出典コメントに転記された文との一致』までで、元の発言そのものとの一致は保証しない（`tools/README.md` の『逐語の出典の実在検査』）。

# 台帳DB化 引き継ぎ（WIP。2026-10-23 セッション終了時点）

## 第2段階進捗（2026-10-24・PR #158 未マージのため別ブランチ）
- サニーランド（SNL-01〜12）を取り込み済み。MAP 12・端 29・接続 15（うち境界接続 SNL-01.bottom↔UTS-05.top）・要素 21・窓 1・既定値 0。未決は U-051〜U-261（+211）。出典に具体値がない項目は未決として登録し、既定値の創作なし。renderer は台帳接続参照へ変更し、生成SVGは前後同一。
- UTS-05 MAP・端は今回の対象外だが、map-topology.md v2 にある境界接続は `外部=はい` として登録。崩落の具体形状・条件付き通行の同行者assist mechanicsは未決。
- 契約チェックリストのSNL-01〜12状態列は「台帳」。旧状態はMAP備考、SNL-03/05/06のlegacy画像パスはMAP備考と map-asset-registry.md に保持。
- 未決の詳細は `docs/ledger/未決.yaml` が正本。検証結果・PRは Issue #156 を参照。体内・後半は未着手。

この置き場は一時的。第2段階以降に、上の『handoff/ の削除手順』で内容を台帳へ吸収してこの `handoff/` ごと削除する（INDEX の到達性検証では許可リスト『handoff（第2段階以降に、HANDOFF.md の削除手順で台帳へ吸収してから削除）』）。

## 目的・目標
Issue #156（https://github.com/kako-jun/sit-by-me/issues/156）が正本。要点: 日本語キーの YAML（`docs/ledger/<表名>.yaml`）を**情報の唯一のマスター**にし、エリア・MAP・建物・接続・要素・窓・決定・採用要素…を別表にして ID で関連づけ、重複をなくし、スキルが台帳から**一意にプロンプトを作る**（再現性）。Issue は台帳に書くまでの仮。kako-jun の指示の逐語は #156 本文。設計の承認は「まかせる」（#144 コメント）。

## 承認済み設計の要点
- マスター=YAML（UTF-8・LF・日本語キー・IDは既存英数字維持）。md は表にできる部分だけ生成ビュー。
- JSON（plan・decor-pools・connections・dependency-graph）は台帳から導出する派生物。`_provenance`（入力ハッシュ・生成日時・コマンド）を持ち、`生成物.yaml` に登録して鮮度検査。
- 必須キー（`必須キー.yaml`）: 欠落=エラー、語彙外=エラー、『未決(要確認)』は `未決.yaml` に載せる。必須キーが揃わないMAPは `oblique_build.py` が起動しない。
- 各表に任意の `特徴(自由記述)` 欄。プロンプトの FEATURES 節にそのまま入る。
- 決定は status に関係なく必ずプロンプトに入る（旧 ledger_gate は廃止）。採用要素（継承要素）は参考画像とプロンプトの両方で次の絵へ。
- 屋内と外観は建物表の同じ行から導出（渡り廊下棟は TRM-04 採用画像に一致: 閉じた壁・南壁に連窓3・板張り・低い瓦屋根）。
- 段階: 第0=INDEX・ファイル配置、第1=寺町（TRM-02〜17）、第2=体内・全MAP、第3=敵・素材・人物。

## どこまで済んだか（このブランチの実装）
- 表（docs/ledger/）28枚（第1段階完了時点の歴史的スナップショット、実測 2026-10-24）: エリア15行・MAP17行（寺町）・建物5・建物部位20・建物窓列5・建物関係4・建物時期差分4・端43・接続22・接続図設定223・要素283・窓31・時期差分16・既定値89・エリア固定22・装飾プール80・語彙117・決定68（有効65・訂正済み3）・採用要素6・素材36・生成物・必須キー62・未決50・キー別名・ファイル配置40規則・Issue点検・描画定数・プロンプト文面。
- ツール（.claude/skills/sit-field-background/tools/）: `ledger_io.py`（表定義 SCHEMA）・`ledger_flat.py`・`ledger_build.py`（導出器: plan/decor/connections/dependency-graph。`build`/`check`/`template`）・`ledger_query.py`（MAP→プロンプト台帳節）・`ledger_migrate_once.py`（一度きりの移行。再実行禁止）。`oblique_build.py` は必須キーゲート＋台帳節をプロンプトに入れる版（PROMPT_VERSION /5）。
- 検証（scripts/）: `ledger_yaml.rb`・`ledger_required_keys.rb`・`verify_ledger.rb`（外部キー・一意・循環・必須キー・語彙・別名・決定整合・建物窓列・生成物鮮度・自由記述警告）。`verify_ledger.rb` は PASS（28表・決定68・MAP17・警告1＝Issue点検の未反映通知）。`verify_map_ledger.rb`・`verify_map_atlas.rb` は PASS（旧 md は併存）。
- 意図的な修正（移行後のJSON差分）: 畳の語の除去、化石の石（決定表から展開）、-fire の勝手口 prompt（西壁→北壁）、TRM-03 の渡り廊下棟（roof-passage を取り消し→建物行から導出・連窓6を追加）、TRM-04 廊下窓の状態（既定→確定）、決定文の写し→決定参照。移行そのものは plan/decor/connections/dependency-graph とも無損失（`curation-scripts/compare_json_roundtrip.py`）。
- main（TRM-01 統合・TRM-08.top 閉鎖）を merge 済み。atlas は 129MAP/137接続。
- 生成: 寺町4 plan（TRM-02〜05＋-kids・-fire）のモック・マスク・プロンプトを再生成済み（画像生成はしていない）。TRM-05-fire のプロンプトに決定68件のうち該当分・継承要素・参考画像・自由記述が入ることを確認。

## 未着手・未了（次にやる順序）
1. **WIP の検証を通す**: `ruby scripts/verify_ledger.rb`（PASS）、`ruby scripts/verify_map_ledger.rb`、`ruby scripts/verify_map_atlas.rb`、`uv run python3 -m unittest discover -s tests`（既存の失敗52件から増えないこと。一覧 `existing-test-failures-52.txt`。main と同じ集合）。TRM-04 の採用記録 `manifest.adoption.plan_sha256` は plan 再生成で古くなる: 幾何不変（clean.png の sha 同一）を確認してから rebaseline を記録する。
2. ~~第0段階~~ **実施済み（2026-10-24）**: `docs/INDEX.md`（表一覧・派生物・配置規則は `ledger_index.py` が台帳から生成するビュー。`check` を `verify_ledger.rb` が実行）・`docs/ledger/ファイル配置.yaml`（40規則。asset-layout.md と verify_asset_layout.py の画像ID規則を合流。verification/・body-*・oblique-* を含む。許可リストは『許可リスト理由』列、handoff は『第1段階完了時に台帳へ吸収して削除』）・`scripts/verify_index_reachable.rb`（配置規則漏れ/複数一致・孤立・壊れたリンク・許可リストの入口を検査）・`tests/test_ledger.py`（fixture で失敗することを確認）。docs/issue-map.md ⇔ INDEX は相互リンク。**handoff/ の削除は上の『handoff/ の削除手順』（第2段階以降）で行い、最後に『ファイル配置.yaml』の `ledger-handoff` 行を同時に削除し、INDEX の HANDOFF リンクも外す**。
3. 第1段階の残り: (a) `verify_prompt_reflects_ledger.rb`（決定ID・必須語・継承要素・自由記述がプロンプトに現れるか。漏れ=畳・化石の石・勝手口・火事版の上半分・渡り廊下の窓列を検出するテスト）と `tests/test_ledger.py`（壊れた fixture で失敗すること。`LEDGER_ROOT` で root を差し替え可）。(b) `audit_issue_decisions.rb`（Issue コメントの決定候補と決定表の差分。`Issue点検.csv` で分類）。(c) ~~TRM-06〜17~~ **実施済み（2026-10-24。`curation-scripts/import_trm06_17*.py`。新列 MAP.設計意図・plan追加JSON／接続.属性JSON、接続図『寺町全体』、要素種別『閉鎖辺』、MAP状態『モック作成済み(承認待ち)』）**: teramachi-rest ブランチ（teramachi-rest-mocks-20261023。読むだけ）の plan 12個・connections-teramachi.json・teramachi-assumptions.md・oblique-masks/README.md の 2026-10-23 の決定を MAP・接続・決定・未決へ取込み。(d) コード内定数の台帳化: oblique_mock.py の幅クラス/視点/マステ座標、oblique_build.py・oblique_topology.py（L382）の直書き文。(e) `build_map_prompt.rb`・`verify_map_ledger.rb` の旧 md 列位置依存を YAML 参照へ。(f) 旧 md 突合: 畳（specifications:46・contract-checklist:57・topology:290）、TBD の勝手口・戸口幅、TRM-05 寝室方針の3表重複、`teramachi-rebuild-candidates.md` を参照のみに、legacy status は寺町だけ廃止。(g) 測定器: 火事版の上半分（火の色の領域が上半分に限られるか）・採用要素（みかん等）の存在確認を参考表示に。(h) SKILL.md・tools/README・docs 冒頭に運用（決定は先に台帳・必須キーと自由記述）。(i) `md ビュー` の生成と鮮度検査。(j) 既定値 `TRM-05.door-back` の旧 assumptions 2件（a08/a09）は a04 に統合済み。
4. 独立レビュー（sonnet 以下。コードレビューは opus 可だが上限は現行メイン以下）→ PR → マージ。第2段階以降は #156 のチェックリスト。

## 実行コマンド
- INDEX の生成ビュー再生成/検査: `uv run python3 .claude/skills/sit-field-background/tools/ledger_index.py build|check`（台帳・配置表を変えたら build して同じコミットに入れる）
- 到達性・配置規則の検査: `ruby scripts/verify_index_reachable.rb`（`LEDGER_ROOT` で root 差し替え）
- 台帳関連のテスト: `uv run python3 -m unittest tests.test_ledger`
- 台帳の検証: `ruby scripts/verify_ledger.rb`
- 派生JSONの再生成/検査: `cd .claude/skills/sit-field-background/tools && uv run python3 ledger_build.py build|check`
- 必須キーの雛形: `uv run python3 ledger_build.py template area|map ID`
- MAPの必須キー欠落: `ruby scripts/ledger_required_keys.rb TRM-05`
- プロンプトの台帳節: `uv run python3 ledger_query.py TRM-05-fire`
- 一括ビルド: `cd docs/production/oblique-mocks && uv run --with numpy --with opencv-python-headless --with pillow python3 -I ../../../.claude/skills/sit-field-background/tools/oblique_build.py --all connections.json`
- Python は必ず `uv run python3`（素の python3 は壊れている）。Ruby は Homebrew 4.x（標準 yaml）。

## 既知の問題
- 既存テストの失敗52件は main と同じ集合（`existing-test-failures-52.txt`。test_asset_migration 43・test_map_id_renumber 8 ほか）。台帳と無関係。
- 決定の逐語の出典URLは、引用ごとに実在するコメントを `;` 区切りで指す（独立レビュー後に修正。`ruby scripts/audit_issue_decisions.rb --check-quotes [--from-json F]` が検査）。旧『会話（Issue #144 に記録）』の3件は #156 本文を出典にした。TRM-04.mask-confirmed は決定表から外し未決 U-050 へ移した（石の敷居・須弥壇の段・本堂の正面扉などは kako-jun の発言ではなく、司令塔の既定として #144 コメント 6355539302 に記録されている。kako-jun の確認待ち。端 TRM-04.door-south・TRM-03.door-main の位置は既定(要確認)）。
- `TRM-05.mikan` の素材IDは空（採用画像の確定後に紐付け）。当時の未決集計は261件（第1段階完了時50件＋サニーランド211件）。現行の未決件数は冒頭の照合節・INDEXの生成ビューを参照する。U-050も未決のまま維持する。
- 接続: `TRM-05.door-back⇄TRM-06.door-house` は接続.yaml にあり、topology v2（map-topology.md）にも 2026-10-24 に追加済み（atlas は 129MAP/137接続）。
- curation-scripts/ はこのセッションの台帳データ作成スクリプト（記録用。再実行すると手修正が消える）。

## 注意
- **画像生成は停止中**。再開は台帳整理の完了＋kako-jun の指示後。生成画像は Claude は見ない（kako-jun が見る）。
- Issue にだけ書かない: 決定は先に `決定.yaml`、Issue は決定IDを参照。
- worktree/ブランチ: 本作業 `sit-by-me-wt-ledger-master`（ローカルの作業ツリー）（ledger-master-phase1-20261023）。他: `sit-by-me-wt-oblique`（oblique-mask-tools-20261023。別担当）、`sit-by-me-wt-teramachi-rest`（teramachi-rest-mocks-20261023。読むだけ）、`sit-by-me`（本体）。git stash 禁止。コミットに Co-Authored-By を付けない。
