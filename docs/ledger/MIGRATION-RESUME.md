# 台帳全体移行の再開メモ（2026-10-26・WIP）

**移行は未完了。レビュー・全検証を終えるまで、このWIPをmainへ入れない。画像生成・生成画像の閲覧は停止を継続する。**

## 保存先と統合済み範囲

- 作業ブランチ: `ledger-master-complete-20261024`。このファイルを含むWIPコミットが中断点。
- PR #158・#159・#157はsquashでmainへ統合済み。ローカル作業は旧HEAD `0f58bc1` を基点にしており、最新mainの文章変更はまだ正式にmergeしていない。
- PR #138は未統合。最終的な台帳移行・関連ブランチの固有変更をまとめ、独立レビュー・検証後に統合する予定だった。古いPRタイトル/本文は最終内容に合わせて更新する。
- 別の作業でPR #160〜#164が追加されている。再開時に最新のPR・mainを確認すること。既存worktreeの変更を上書き・削除しない。
- ブランチ・worktreeは削除していない。主作業コピーにある未コミット変更やsample資料も、このWIPの外なので触らない。

## 中断時の実ファイル件数（意味や検証の完了件数ではない）

| 表 | 行数 |
|---|---:|
| MAP | 130（廃止TRM-01を含む。現役129） |
| エリア / 接続 | 15 / 137 |
| 敵 / 召喚獣 / 人物 | 96 / 8 / 5 |
| 素材 | 723 |
| 決定 / 未決 | 74 / 1823 |
| Issue出典 / Issue命題 | 1189 / 1868 |

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
3. 未移管の非MAP表・旧正本consumer・validator/gate・型付きpath・生成ビュー鮮度を点検する。追加テスト54件と既存topology fixtureの追従は最終確認前。
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
ruby scripts/verify_map_atlas.rb
uv run python3 .claude/skills/sit-field-background/tools/ledger_build.py check
uv run python3 .claude/skills/sit-field-background/tools/ledger_index.py check
uv run python3 .claude/skills/sit-field-background/tools/ledger_views.py check
ruby scripts/audit_issue_decisions.rb --check-quotes
uv run python3 -m unittest tests.test_ledger
uv run python3 -m unittest discover -s tests
```

全suiteの並列runnerは完成確認前。以前の一時runnerにはcwd/PYTHONPATH/Ruby PATHの誤りがあったため、そのまま流用しない。handoff削除・既存基準線移動も未完了なので、実ファイルとテストの参照先を確認する。
