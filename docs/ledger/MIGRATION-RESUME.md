# 台帳全体移行の再開メモ（2026-10-26・WIP）

**移行は未完了。レビュー・全検証を終えるまで、このWIPをmainへ入れない。画像生成・生成画像の閲覧は停止を継続する。**

## 2026-10-27のチェックポイント（最新main `d469045` 取込み後）

- 論理イベント/移動の端には物理的な壁側を要求しないよう修正。未決値と相手端の必須条件を保持し、戸口・開口・抽象通路の不正値は引き続き拒否する。TRM-03を含む6MAP・6回帰アンカーのプロンプト反映検査はPASS。
- 4 rendererは `LEDGER_ROOT` を尊重し、テストfixture実行で実際のSVGを書き換えない。BG005は没の履歴と削除直前SHAを保持し、現行パスは空。INDEX・配置・生成物の整合を修正した。
- 指定Ruby検証5本、build/index/views check、content/domain検証はPASS。凍結Issueスナップショットの出典構造・引用照合はPASS（決定74件、照合70件・引用104個・例外4件）。これは発言の意味確認完了を示さない。
- テスト（全suite）は独立再レビュー時点で402件・既存失敗9件（いずれもこの移行の回帰ではない）。その9件は原因を調べて解消した（旧IDスキャンの対象外に台帳の引用・制作ログ・BGMスロットを明記、体内の左右は#142の「本人から見る」に合わせたテスト修正）。最新の件数は #156 のコメントを参照。
- 独立レビューで指摘された5件（敵サイズ決定の欠落、S008の素材共有、人物形態のgate、queryのID重複、Issue命題の必須出典FK）は**修正済み**で、回帰テストがある。人物形態の許可値は `語彙.yaml`（グループ `人物形態.年齢`・`人物形態.衣装`・`人物形態.車椅子`・組み合わせ規則 `人物形態.規則`）が正本で、`verify_content_ledger.py` が全行を検査する。
- 他PCのmain `d469045`（#160〜#164・#172）は**取り込み済み**（履歴上の親も持つ）。新規画像327点・既存画像102点の差し替え・JSONメタデータ7件は台帳に反映した。移行後の差し替えは `素材更新.yaml` のSHA連鎖（素材移行SHA→現物SHA）で追跡し、`verify_asset_layout.py` と `tests/test_asset_migration.py` が連鎖を辿って受理する（連鎖を壊すと落ちる。`verify_ledger.rb` も、移行SHAと現物SHAが違うのに素材更新の行がない素材と、出典commit の実在・新SHA＝出典blob・移行行のない path の連鎖起点を検出する）。ae90c04以前のmain由来の41件も連鎖に登録し、削除済みの S005 は素材移行で墓標（delete）にした。**限界**: 素材移行に行のない12パスは、連鎖の起点が git 履歴上のどれかの blob と一致することしか確かめられず、途中の素材更新行の欠落は検出できない（移行行のあるパスは移行SHA→現物SHAで欠落を検出する）。出典の照合には git の全履歴が要る（shallow clone では `git fetch --unshallow` を案内して失敗する）。
- `scripts/verify_map_id_renumber.py` の旧IDスキャンは、台帳の引用表（Issue出典・Issue命題・Issue点検）では原文の旧IDだけ残し旧slugは検査する。除外は語句・トークン単位だけで、行全体の除外はしない。新IDを併記した旧IDの言及や別体系の語（決定ラベル・生成ラウンドの略号）は、その語句だけを取り除いて検査する（同じ行の別の旧IDは検出する）。`docs/production/` と制作スキルでは、「P-」直後と「出口」に続く方位列の1桁 [NESW]（出口の方位略号）、および 生成ラウンド略号の直後が LOG_ROUND_TOKEN の語（報告・測定・round・の・で 等）のトークンだけを見逃し、それ以外の旧MAP IDは検出する。**限界**: 生成ラウンド略号の直後が「の」「で」等だと、生成ラウンドか旧MAP IDかを区別できず見逃す（旧MAPの1桁IDを指す「…の」でも通る）。出口の方位列に、旧MAP IDと同形の1桁が並んでも見逃す。
- 候補画像・付随JSON・`output/battle-sword-previews`・`sit-battle-effect` のエージェント定義は `ファイル配置.yaml` に用途限定の規則を追加。画像用JSONは `素材メタデータ.yaml`／`素材メタデータ値.yaml` から `scripts/asset_metadata.py` が生成し、`build_ledger.py` と `verify_ledger.rb` が検査する（数値は元の表記を保持）。

## 保存先と統合済み範囲

- 作業ブランチ: `ledger-master-complete-20261024`。このファイルを含むWIPコミットが中断点。
- PR #158・#159・#157はsquashでmainへ統合済み。`4a44a80` でmain `ae90c04` まで同期済み。その後のmain `d469045`（#160〜#164・#172）も取り込み済み。
- PR #138は未統合。最終的な台帳移行・関連ブランチの固有変更をまとめ、独立レビュー・検証後に統合する予定だった。古いPRタイトル/本文は最終内容に合わせて更新する。
- 別の作業のPR #160〜#164・#172はmainへ統合済み。最新mainを再確認し、素材の追加・差し替えと正本を照合する。既存worktreeの変更を上書き・削除しない。
- ブランチ・worktreeは削除していない。主作業コピーにある未コミット変更やsample資料も、このWIPの外なので触らない。

## 中断時の実ファイル件数（意味や検証の完了件数ではない）

| 表 | 行数 |
|---|---:|
| MAP | 130（廃止TRM-01を含む。現役129） |
| エリア / 接続 | 15 / 137 |
| 敵 / 召喚獣 / 人物 | 96 / 8 / 5 |
| 素材 | 1050 |
| 決定 / 未決 | 74 / 1834 |
| Issue出典 / Issue命題 | 1189 / 1868 |

（上表は中断時点の件数。2026-10-30 の最終取込み時点で Issue出典 2055 / Issue命題 3224 になり、その時点で `audit_issue_decisions.rb --check-sources` はPASSだった。以後に Issue へ増えたコメントは含まない。）

Issue出典は構造・ハッシュ・リンクの検査と、発言内容の意味確認を分けている。最後の報告では1182出典・1322命題が要確認。**全Issueの決定を意味確認済みとは言えない。** U-050は未決のまま維持する。

## 実装済みの主な部分

- 全MAP・接続、体内/海外の著者定義データ、敵/BGM/人物/素材/候補台帳をYAMLへ移行し、読み取り・導出器を追加中。
- 旧MAP資料の27表はYAML由来の生成ブロックへ置換。非MAP資料は、移管できた表と未移管の事実を照合中。
- `scripts/build_ledger.py` が生成物の共通入口。`content_ledger.py`、`verify_content_ledger.py`、`verify_domain_ledger.py`、`map_source_views.py`等を追加。
- 関連ブランチの多角形床・水面/階段・marker幅・台紙/貼戻しツールを、現行YAML参照と既存の開口/canonical処理を保持して統合中。
- 武器20点・体内側28点・main側歩行111点は既存Gitオブジェクトから取り込み済み。生成・閲覧はしていない。BG005は19ab92aの没指定に従って削除し、素材履歴の整合を対応中。
- ブランチ別の固有差分と除外理由は[branch-integration.md](branch-integration.md)と監査JSON、残る移管は[migration-closure.md](migration-closure.md)を参照。

## 次にやる順序

1. ブランチ・WIPコミット・最新main/PRを確認し、担当の重複編集を止める。`git stash`は禁止。
2. 下記の保存資料と独立レビュー設計を読む。利用上限で担当が止まったため、最終レビューは未完了。
3. 未移管の非MAP表・旧正本consumer・validator/gate・型付きpath・生成ビュー鮮度を点検する。追加61テストと既存topology fixtureのチェックポイントは下記のとおり。
4. 現在の全変更を保存した後で最新mainを取り込み、歩行素材の仕様文・skill・配置表などを両方保持する。古いmainや旧ブランチでYAML正本を巻き戻さない。
5. 生成・独立レビュー・指摘修正・指定検証一式を実行。既存失敗52件の基準線と実失敗集合を比較する。途中のPASS報告を最終結果に流用しない。
6. Issue #156に結果を記録し、最終内容のPRをレビュー可能にしてから、承認済みの統合方針に従う。未検証のままPR #138をmergeしない。

## 再開資料（ローカルcache）

Git共通ディレクトリの `resume-support/ledger-master-complete-20261024/session-20261026.tar.gz` に、凍結Issueスナップショット・独立レビュー設計・未移管表監査・初期比較基準を保存した。公開ファイルへ未加工のIssue原文やローカルパスをコピーしない。

```sh
task_cache="$(git rev-parse --git-common-dir)/resume-support/ledger-master-complete-20261024/session-20261026.tar.gz"
task_resume_dir=$(mktemp -d)
tar -xzf "$task_cache" -C "$task_resume_dir"
```

主な資料: `sit-ledger-review-design.md`、`sit-content-table-audit.json`、`sit-issue-audit-20261024-latest.json`、`sit-ledger-complete-baseline-20261024/`。cacheはGit追跡外なので別PCには自動転送されない。別PCでは元コミット/Issueから基準を再取得し、凍結時点と新規発言の差分を明記する。

## 実行規律と検証入口

Pythonは必ず `uv run python3`。RubyだけでなくPythonテストの子プロセスにもHomebrew RubyのPATHを継承させる。新規venv・大きな複製・画像生成/閲覧はしない。明示パスでstageし、AI署名をcommitへ付けない。

```sh
export PATH=/opt/homebrew/opt/ruby/bin:$PATH
ruby --version
uv run python3 scripts/build_ledger.py --help
ruby scripts/verify_ledger.rb
ruby scripts/verify_prompt_reflects_ledger.rb
ruby scripts/verify_index_reachable.rb
ruby scripts/verify_map_ledger.rb
uv run python3 scripts/verify_asset_layout.py
ruby scripts/verify_map_atlas.rb
uv run python3 .claude/skills/sit-field-background/tools/ledger_build.py check
uv run python3 .claude/skills/sit-field-background/tools/ledger_index.py check
uv run python3 .claude/skills/sit-field-background/tools/ledger_views.py check
ruby scripts/audit_issue_decisions.rb --check-quotes
uv run python3 -m unittest tests.test_ledger
uv run python3 -m unittest discover -s tests
```

全suiteの並列runnerは完成確認前。以前の一時runnerにはcwd/PYTHONPATH/Ruby PATHの誤りがあったため、そのまま流用しない。handoff削除・既存基準線移動も未完了なので、実ファイルとテストの参照先を確認する。
