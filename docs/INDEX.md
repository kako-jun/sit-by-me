# Sit by Me ドキュメント入口（INDEX）

> **移行WIPの再開入口**: [MIGRATION-RESUME](ledger/MIGRATION-RESUME.md)（2026-10-26。全体移行・最終レビュー・全検証は未完了）。

リポ内の全ドキュメント・台帳・ツール・スキルへの入口。**ここからのリンクの連鎖で辿れないファイルは孤立としてエラー**になる（`ruby scripts/verify_index_reachable.rb`。置き場所の規則は台帳の [ファイル配置.yaml](ledger/ファイル配置.yaml)）。新しいファイルを足したら、このページか、ここから辿れるページにリンクを張る。

> **運用（絶対）**: 台帳（`docs/ledger/*.yaml`）が情報の唯一のマスター。①決定は先に台帳の `決定.yaml` へ書き、Issue は決定IDを参照するだけ（Issue にだけ書かない）。②必須キー（`必須キー.yaml`）が欠けたMAPはプロンプトを作れない。表に収まらない決まりは各表の `特徴(自由記述)` へそのまま書く。③画像生成は台帳整理の完了と kako-jun の再開指示があるまでしない（現在は停止中）。④生成画像は Claude は見ない（kako-jun が見る）。⑤プロンプトの文面・寸法はコードに直書きせず台帳の `プロンプト文面`・`描画定数` を直す。手順は [フィールド背景のスキル](../.claude/skills/sit-field-background/SKILL.md)。

- Issue との対応は [Issue 対応表](issue-map.md)（docs の決定・候補 ↔ Issue 番号）。Issue 対応表からもここへ戻れる。
- 台帳の方針（Issue #156）: 日本語キーの YAML（`docs/ledger/<表名>.yaml`）が情報の唯一のマスター。派生 JSON は台帳から導出する。
- 保存点: [移行再開メモ](ledger/MIGRATION-RESUME.md)、[関連ブランチの捕捉監査](ledger/branch-integration.md)（[パス別証拠](ledger/branch-integration-paths.json)）。監査は捕捉時点の履歴で、ゲーム情報の正本ではない。

## 台帳（マスター）

表の一覧・行数・列は下の生成ビューを見る。関連:
- 引き継ぎ（一時。第1段階の完了時に台帳へ吸収して削除）: [HANDOFF](ledger/handoff/HANDOFF.md)
- 検証: `ruby scripts/verify_ledger.rb`（スキーマ・外部キー・鮮度）、`ruby scripts/audit_issue_decisions.rb`（Issue の決定候補と決定表の突合。結果は台帳の Issue点検.yaml）、`ruby scripts/verify_prompt_reflects_ledger.rb`（台帳の決定・採用要素・自由記述・窓列がプロンプトに漏れなく出るか。必須キー未決のMAP〔現状は TRM-06〜17〕は『ゲートで停止』としてプロンプト反映検査の対象外。未決が解消してゲートが開いたMAPは自動で対象に入る）、`ruby scripts/verify_index_reachable.rb`（INDEX 到達性）
- ツール: [tools/README](../.claude/skills/sit-field-background/tools/README.md)
- 素材の付随表: [素材共有](ledger/素材共有.yaml)（所有者以外の利用関係）、[素材更新](ledger/素材更新.yaml)（素材移行SHAから現物SHAへのSHA連鎖。検査ロジックは [asset_chain.py](../scripts/asset_chain.py)）、[素材メタデータ](ledger/素材メタデータ.yaml)・[素材メタデータ値](ledger/素材メタデータ値.yaml)（画像用JSONの安全化済み正本。[asset_metadata.py](../scripts/asset_metadata.py) の `build|check` で導出・検査）
- 全派生物の再生成・鮮度検査: [build_ledger.py](../scripts/build_ledger.py) の `build|check`。MAPの元資料表は [map_source_views.py](../scripts/map_source_views.py) と [文書ビュー.yaml](ledger/文書ビュー.yaml) が管理する。
- 領域台帳の検査: [verify_domain_ledger.py](../scripts/verify_domain_ledger.py)、[verify_content_ledger.py](../scripts/verify_content_ledger.py)。`--require-reviewed` はIssueの意味点検が全件終わるまで失敗する。[移行の閉鎖条件](ledger/migration-closure.md) を形式移行の合格と区別する。
- 敵・人物・BGM・刀の全列ビュー: [コンテンツ](ledger/views/content.md)（[content_ledger_views.py](../scripts/content_ledger_views.py)）。生成入力は [content_ledger.py](../scripts/content_ledger.py) の `query KIND ID --gate`。
- 領域台帳の回帰検証: [content](../tests/test_content_ledger.py)、[domain](../tests/test_domain_ledger.py)、[Issue provenance](../tests/test_issue_provenance.py)、[typed paths](../tests/test_ledger_typed.py)。
- 共通fixture: [ledger_test_support.py](../tests/ledger_test_support.py)。PR #157に含まれる制作履歴: [C001歩行セット](production/20261024-c001-field-walk.md)（記載のマージ待ちは当時の状態）。
- Issueの凍結出典からの再生成: [build_issue_provenance.py](../scripts/build_issue_provenance.py)（`build|check --from-json SNAPSHOT`）。原文と安全化本文のハッシュを区別し、自動抽出を本人の決定と誤認しない。
- 移行用の一回限りのツール（再実行禁止）: [MAP移行](../.claude/skills/sit-field-background/tools/ledger_map_migrate_once.py)、[体内移行](../.claude/skills/sit-field-background/tools/ledger_body_migrate_once.py)、[コンテンツ移行](../scripts/content_ledger_migrate_once.py)。現行の体内入力は [body_geometry.py](../.claude/skills/sit-field-background/tools/body_geometry.py) がYAMLから読む。
- 人が読むビュー（台帳から生成。手編集禁止。`ledger_views.py build|check`）: [MAP 一覧](ledger-views/MAP.md)、[建物](ledger-views/建物.md)、[決定](ledger-views/決定.md)、[未決](ledger-views/未決.md)、[採用要素](ledger-views/採用要素.md)、[接続](ledger-views/接続.md)

## 企画・仕様

- 企画・物語: [企画メモ](concept.md)、[物語](story.md)、[年代別まとめ](timeline.md)、[アートディレクション](art-direction.md)
- ゲーム: [ゲームシステム](systems.md)、[ロードマップ](roadmap.md)、[決定ログ](decisions.md)、[素材の方針](assets-policy.md)、[戦闘演出の台帳](battle-effects-registry.md)、[フィールド感情表現の台帳](field-emotion-registry.md)
- 戦闘・成長: [FF 戦闘ルール調査](ff-battle-rules.md)、[刃（刀）候補](blades.md)、[アビリティ候補](ability-candidates.md)、[ラーニング時期配置](learning-schedule.md)、[ボスのギミック](boss-gimmicks.md)
- 敵: [モンスター台帳](monsters.md)、[ダンジョン別の敵](dungeon-enemies.md)、[敵の割り当て案](enemy-allocation.md)
- 台帳（md）: [コンテンツ台帳の目次](content-registry.md)、[シナリオ台帳](scenario-registry.md)、[フィールド画像台帳](map-asset-registry.md)
- BGM: [BGMスロット表](bgm-registry.md)、[新世界より録音調査](bgm-sources-research.md)、[Suno 試験手順](bgm-suno-trial.md)、データ [bgm-phrases.csv](bgm-phrases.csv)・[bgm-sources.csv](bgm-sources.csv)

## MAP・フィールド背景

- MAP: [トポロジー計画](map-topology.md)、[MAP個別仕様](map-specifications.md)、[生成契約チェックリスト](map-contract-checklist.md)、[参考画像調査](map-reference-research.md)、[寺町再構築候補](teramachi-rebuild-candidates.md)
- 接続図: [全MAP接続図](topology/README.md)。データ: [map-ids.json](topology/map-ids.json)、[areas.json](topology/areas.json)、[overseas-progression.json](topology/overseas-progression.json)
- 制作記録: [素材ID配置](production/asset-layout.md)、[移行 manifest](production/20261018-asset-migration.json)、[MAP改名対応表](production/20261019-map-id-renumber.json)、[寺町の制作前入力](production/20261018-teramachi-preflight.md)
  - 体内: [BDY-02 採用](production/20261022-bdy02-adoption.md)、[体内MAP採用（共通）](production/20261022-body-maps-adoption.md)、[モック保存設計と位置合わせ](production/20261022-body-mocks-and-registration.md)、[体内の整合表](../verification/body-layout/consistency.md)、[体内の全接続](../verification/body-layout/connections.md)
  - 寺町（斜め視点）: [TRM-04 採用](production/20261023-trm04-adoption.md)、[斜めマスクの入力・結果](production/oblique-masks/README.md)、[斜めモックの接続一覧](production/oblique-mocks/connections.md)
- リポ概要: [README](../README.md)
- 刀候補の確認用プレビュー: [battle-sword-previews](../output/battle-sword-previews/README.md)
- 画像正本: [assets/images/](../assets/images/)（[ブランド素材の説明](../assets/images/brand/README.md)）（配置規則は [ファイル配置.yaml](ledger/ファイル配置.yaml) の `asset-*`）
- 検証記録: [敵画像の透過監査](../verification/transparency-audit-20261022/audit-notes.md)、[キャラ素材の切り出し](../verification/characters/tools/README.md)
- 独立レビュー（red-team）の日付記録: [reviews/artifact-redteam/](reviews/artifact-redteam/)

## スクリプト・テスト

- scripts: [asset_chain.py](../scripts/asset_chain.py), [asset_metadata.py](../scripts/asset_metadata.py), [audit_issue_decisions.rb](../scripts/audit_issue_decisions.rb), [build_map_prompt.rb](../scripts/build_map_prompt.rb), [fetch_bgm_sources.py](../scripts/fetch_bgm_sources.py), [ledger_required_keys.rb](../scripts/ledger_required_keys.rb), [ledger_yaml.rb](../scripts/ledger_yaml.rb), [make_logo.py](../scripts/make_logo.py), [map_graph.rb](../scripts/map_graph.rb), [md_table.rb](../scripts/md_table.rb), [render_body_topology.rb](../scripts/render_body_topology.rb), [render_late_topology.rb](../scripts/render_late_topology.rb), [render_map_atlas.rb](../scripts/render_map_atlas.rb), [render_sunnyland_topology.rb](../scripts/render_sunnyland_topology.rb), [svg_to_png.py](../scripts/svg_to_png.py), [verify_asset_layout.py](../scripts/verify_asset_layout.py), [verify_ledger.rb](../scripts/verify_ledger.rb), [verify_index_reachable.rb](../scripts/verify_index_reachable.rb), [verify_prompt_reflects_ledger.rb](../scripts/verify_prompt_reflects_ledger.rb), [verify_map_atlas.rb](../scripts/verify_map_atlas.rb), [verify_map_id_renumber.py](../scripts/verify_map_id_renumber.py), [verify_map_ledger.rb](../scripts/verify_map_ledger.rb), [verify_overseas_progression.rb](../scripts/verify_overseas_progression.rb)
- tests: [test_asset_metadata.py](../tests/test_asset_metadata.py), [test_asset_migration.py](../tests/test_asset_migration.py), [test_body_topology.py](../tests/test_body_topology.py), [test_ledger.py](../tests/test_ledger.py), [test_map_atlas.py](../tests/test_map_atlas.py), [test_map_id_renumber.py](../tests/test_map_id_renumber.py), [test_map_topology.py](../tests/test_map_topology.py), [test_overseas_progression.py](../tests/test_overseas_progression.py)

## スキルとツール

- 回収した制作ツール: [layout_guide.py](../.claude/skills/sit-field-background/tools/layout_guide.py)、[oblique_town.py](../.claude/skills/sit-field-background/tools/oblique_town.py)、[pasteback.py](../.claude/skills/sit-field-background/tools/pasteback.py)、[battle_base.py](../.claude/skills/sit-battle-background/tools/battle_base.py)。[マップ上の敵立ち絵](../.claude/skills/sit-map-enemy-sprite/SKILL.md)。

- スキル手順書: [フィールド背景](../.claude/skills/sit-field-background/SKILL.md)（[gates](../.claude/skills/sit-field-background/gates.md)、[pitfalls](../.claude/skills/sit-field-background/pitfalls.md)、[issue-template](../.claude/skills/sit-field-background/issue-template.md)、[体内の付録](../.claude/skills/sit-field-background/body-appendix.md)、[エージェント定義](../.claude/skills/sit-field-background/agents/openai.yaml)）、[フィールドマスク](../.claude/skills/sit-field-mask/SKILL.md)、[red-team](../.claude/skills/sit-artifact-redteam/SKILL.md)、[戦闘背景](../.claude/skills/sit-battle-background/SKILL.md)、[キャラ](../.claude/skills/sit-character-sprite/SKILL.md)、[敵](../.claude/skills/sit-enemy-sprite/SKILL.md)、[召喚獣](../.claude/skills/sit-summon-sprite/SKILL.md)、[戦闘演出](../.claude/skills/sit-battle-effect/SKILL.md)（[エージェント定義](../.claude/skills/sit-battle-effect/agents/openai.yaml)）
- フィールド背景のツール（一覧と使い方は [tools/README](../.claude/skills/sit-field-background/tools/README.md)）: [body_floor_overlay.py](../.claude/skills/sit-field-background/tools/body_floor_overlay.py), [body_geometry_json.py](../.claude/skills/sit-field-background/tools/body_geometry_json.py), [body_layout.py](../.claude/skills/sit-field-background/tools/body_layout.py), [body_mask_export.py](../.claude/skills/sit-field-background/tools/body_mask_export.py), [body_register.py](../.claude/skills/sit-field-background/tools/body_register.py), [body_sheet.py](../.claude/skills/sit-field-background/tools/body_sheet.py), [body_step_scan.py](../.claude/skills/sit-field-background/tools/body_step_scan.py), [build_body_prompt.py](../.claude/skills/sit-field-background/tools/build_body_prompt.py), [check_body_image.py](../.claude/skills/sit-field-background/tools/check_body_image.py), [ledger_build.py](../.claude/skills/sit-field-background/tools/ledger_build.py), [ledger_csv_to_yaml_once.py](../.claude/skills/sit-field-background/tools/ledger_csv_to_yaml_once.py), [ledger_flat.py](../.claude/skills/sit-field-background/tools/ledger_flat.py), [ledger_index.py](../.claude/skills/sit-field-background/tools/ledger_index.py), [ledger_views.py](../.claude/skills/sit-field-background/tools/ledger_views.py), [ledger_io.py](../.claude/skills/sit-field-background/tools/ledger_io.py), [ledger_migrate_once.py](../.claude/skills/sit-field-background/tools/ledger_migrate_once.py), [ledger_query.py](../.claude/skills/sit-field-background/tools/ledger_query.py), [ledger_write_rows.py](../.claude/skills/sit-field-background/tools/ledger_write_rows.py), [oblique_build.py](../.claude/skills/sit-field-background/tools/oblique_build.py), [oblique_common.py](../.claude/skills/sit-field-background/tools/oblique_common.py), [oblique_e2_measure.py](../.claude/skills/sit-field-background/tools/oblique_e2_measure.py), [oblique_e2_schedule.py](../.claude/skills/sit-field-background/tools/oblique_e2_schedule.py), [oblique_mask.py](../.claude/skills/sit-field-background/tools/oblique_mask.py), [oblique_mock.py](../.claude/skills/sit-field-background/tools/oblique_mock.py), [oblique_prompt_probe.py](../.claude/skills/sit-field-background/tools/oblique_prompt_probe.py), [oblique_text.py](../.claude/skills/sit-field-background/tools/oblique_text.py), [oblique_register.py](../.claude/skills/sit-field-background/tools/oblique_register.py), [oblique_topology.py](../.claude/skills/sit-field-background/tools/oblique_topology.py), [oblique_e2_run.sh](../.claude/skills/sit-field-background/tools/oblique_e2_run.sh)

## 台帳の生成ビュー

<!-- GENERATED:BEGIN ledger-views -->

> **生成ビュー（手編集禁止）**。生成元: `docs/ledger/*.yaml`（表の定義は `.claude/skills/sit-field-background/tools/ledger_io.py` の `SCHEMA`・`TABLE_DOC`）。
> 再生成: `uv run python3 .claude/skills/sit-field-background/tools/ledger_index.py build`（リポ直下で実行）。鮮度検査: `uv run python3 .claude/skills/sit-field-background/tools/ledger_index.py check`（`ruby scripts/verify_ledger.rb` に含まれる）。台帳を変えたら再生成して同じコミットに入れる。

### 台帳の表

| 表 | 行数 | 説明 | 列 |
|---|---|---|---|
| [エリア](ledger/エリア.yaml) | 15 | エリア（区域）の台帳。1行=1エリア。 | エリアID / 区域コード / 名称 / 目標枚数 / 台帳段階 / 机の天面の材質 / 台座の素材 / 木の種類 / 外周の装飾方針 / 備考 / 特徴(自由記述) |
| [MAP](ledger/MAP.yaml) | 130 | MAP（1枚の背景）の台帳。1行=1MAP。設計意図=plan の design。plan追加JSON=plan の最上位に足す追加キー(例 indoor)。 | MAP_ID / エリアID / 名称 / 字幕 / 時期 / 屋内外 / 状態 / 建物ID / 表現する部位 / 一言特徴 / 描画方式 / 装飾プールID / 依存MAP / 依存の確度 / 依存の根拠 / 床材 / 壁材 / 窓 / 扉の意匠 / 工作の材質 / 時期差分 / 採用状態 / 寸法根拠 / 備考 / 設計意図 / plan追加JSON / 特徴(自由記述) |
| [建物](ledger/建物.yaml) | 5 | 建物の台帳。屋内と外観は同じ建物行から導出する。 | 建物ID / 名称 / エリアID / 種別 / 外形 / 屋根 / 外壁 / 窓列 / 扉 / 材質 / 関係 / 状態 / 備考 / 特徴(自由記述) |
| [建物部位](ledger/建物部位.yaml) | 20 | 建物の部位（壁・屋根・扉など）。 | 部位ID / 建物ID / 部位種別 / 方角 / 状態 / 材質 / 見た目 / 決定参照 / 特徴(自由記述) |
| [建物窓列](ledger/建物窓列.yaml) | 5 | 建物の壁ごとの窓列。 | 窓列ID / 建物ID / 部位ID / 個数 / 先頭比 / 間隔比 / 幅比 / 窓台比 / 高さ比 / 窓種別 / 理由 / 決定参照 / 特徴(自由記述) |
| [建物関係](ledger/建物関係.yaml) | 4 | 建物どうしの関係（渡り廊下で接続など）。 | 通番 / 建物A / 建物B / 関係 / 方角 / 接続端ID / 決定参照 / 特徴(自由記述) |
| [建物時期差分](ledger/建物時期差分.yaml) | 4 | 建物の時期ごとの差分。 | 建物ID / 時期 / 部位ID / 差分 / 内容 / 決定参照 / 特徴(自由記述) |
| [端](ledger/端.yaml) | 277 | MAP の端（戸口・開口・縁）。 | 端ID / MAP_ID / 適用時期 / 種別 / 壁 / 壁側 / 面 / 中心 / 沿い範囲 / 相手端 / 幅クラス / 状態 / 通路 / 建物部位ID / 備考 / 決定参照 / 属性JSON / 特徴(自由記述) |
| [接続](ledger/接続.yaml) | 137 | 端と端の接続。図は ; 区切りで複数の接続図に属せる。属性JSON は {図ID: {辺の出力キー: 値(null=その図では出さない)}} で図ごとの上書きを持つ。 | 端A / 端B / 種別 / 期待 / ラベル / 方角A / 方角B / 外部 / 無効時期 / 図 / 主路・状態 / 出典注記 / 決定参照 / 属性JSON / 特徴(自由記述) |
| [接続図設定](ledger/接続図設定.yaml) | 223 | 接続図の描画設定（図ID×項目）。 | 図ID / 項目 / 値 / 型 / 決定参照 |
| [要素](ledger/要素.yaml) | 304 | MAP 内の要素（家具・物・樹木など）。 | MAP_ID / 適用時期 / 要素ID / 種別 / 名称 / 建物部位ID / 見た目 / 決定参照 / 属性JSON / 特徴(自由記述) |
| [窓](ledger/窓.yaml) | 32 | MAP の壁の窓。 | 窓ID / MAP_ID / 適用時期 / 壁 / 壁側 / 中心 / 幅 / 種別 / 窓台 / 高さ / 状態 / 沿い範囲 / 建物窓列ID / 連番 / 備考 / 決定参照 / 属性JSON / 特徴(自由記述) |
| [時期差分](ledger/時期差分.yaml) | 16 | MAP の時期ごとの差分。 | MAP_ID / 時期 / 項目 / 値 / 決定参照 |
| [既定値](ledger/既定値.yaml) | 89 | 仮置きの既定値（要確認）。 | 既定ID / MAP_ID / 適用時期 / 内容 / 決定参照 |
| [エリア固定](ledger/エリア固定.yaml) | 22 | エリア単位で固定する指定（机の天面・木の種類・台座など）。 | エリアID / 項目 / 値 / 型 / 決定参照 |
| [装飾プール](ledger/装飾プール.yaml) | 80 | 装飾プールの設定。 | プールID / 項目 / 値 / 型 / 決定参照 |
| [語彙](ledger/語彙.yaml) | 132 | 許す・禁じる語彙と英語プロンプト断片。 | 語彙ID / グループ / 値 / 英語断片 / 説明 |
| [決定](ledger/決定.yaml) | 584 | kako-jun の決定（逐語・出典つき）。status に関係なくプロンプトへ入る。 | 決定ID / 日付 / 対象種別 / 対象ID / 対象名 / 決定の要点 / 逐語 / 出典 / 出典URL / 状態 / 置換先 / プロンプト出力 / 必須語 / 禁止語 / 対象MAP / 備考 / 特徴(自由記述) |
| [採用要素](ledger/採用要素.yaml) | 6 | 採用画像から次の絵へ継承する要素。 | 採用要素ID / 素材ID / 元MAP / 要素 / 内容 / 継承先MAP / 継承方法 / 状態 / 確認語 / 決定参照 / 特徴(自由記述) |
| [素材](ledger/素材.yaml) | 1055 | 素材（画像・マスクなど。没も行で保持）。 | 素材ID / 所有者ID / 種別 / パス / 状態 / 日付 / 来歴 / sha256 / 特徴(自由記述) |
| [素材共有](ledger/素材共有.yaml) | 3 | 所有者以外の人物・敵・召喚獣が同一素材を利用する明示的な関係。素材行を複製せず、出典を保持する。 | 共有ID / 利用者ID / 素材ID / 根拠 |
| [素材更新](ledger/素材更新.yaml) | 143 | 元の素材移行SHAを保持したまま後続の上流更新を記録するSHA連鎖。出典commitと出典パスを必須とする。 | 更新ID / 素材ID / パス / 旧sha256 / 新sha256 / 出典commit / 出典パス / 根拠 |
| [素材メタデータ](ledger/素材メタデータ.yaml) | 7 | 上流の画像用JSONを安全化してYAML正本に変換した出典とハッシュ。原文の秘匿値は保持しない。 | メタデータID / パス / 所有者ID / 原文sha256 / 安全化sha256 / 出典commit / 安全化方針 |
| [素材メタデータ値](ledger/素材メタデータ値.yaml) | 704 | 画像用JSONをJSONポインタ・型・値へ分解したYAML正本。JSONは再構築して生成する。 | メタデータID / JSONポインタ / 型 / 値 |
| [生成物](ledger/生成物.yaml) | 26 | 派生物（JSON）の登録と鮮度検査用ハッシュ。 | 生成物ID / 種別 / パス / 元の表 / 入力ハッシュ / 生成日時 / 再生成コマンド / 備考 |
| [必須キー](ledger/必須キー.yaml) | 142 | 対象テーブルごとの必須キー定義。 | 対象テーブル / キー / 必須度 / 条件 / 語彙グループ / 説明 |
| [未決](ledger/未決.yaml) | 1960 | 未決（要確認）の一覧。 | 未決ID / 対象テーブル / 対象ID / キー / 内容 / 状態 / 解決決定ID |
| [キー別名](ledger/キー別名.yaml) | 20 | 列名・キー名の別名と正規名。 | 正規名 / 別名 / 対象テーブル / 説明 |
| [Issue点検](ledger/Issue点検.yaml) | 525 | Issue の決定候補と決定表の突合結果（audit_issue_decisions.rb が更新。分類=決定表に反映済み／未反映(要取込み)／決定でない／対象外）。 | Issue番号 / コメントURL / 候補の要約 / 分類 / 決定ID / 備考 |
| [ファイル配置](ledger/ファイル配置.yaml) | 54 | リポ内のファイルの置き場所規則（パターン・種別・用途・所有表/生成元・許可リスト理由）。asset-layout.md と verify_asset_layout.py の規則を合流した正本。 | 配置ID / パターン / 種別 / 用途 / 所有表 / 生成元 / 到達 / 入口 / 許可リスト理由 / 検査 / 備考 |
| [描画定数](ledger/描画定数.yaml) | 28 | 斜めツール（oblique_mock.py・oblique_topology.py）の寸法・視点・幅クラス・窓種別・台座の飾りの位置。コードはここを読む。 | 定数ID / グループ / 値 / 単位 / 説明 / コード内の名前 |
| [プロンプト文面](ledger/プロンプト文面.yaml) | 144 | imagegen 用プロンプト・接続表・窓一覧・接続図に出る文面（{名前}=変数の差し込み口）。コードは oblique_text.text で読み、文面を直接持たない。 | 文面ID / 区分 / 文面 / 変数 / 使用箇所 / 備考 |
| [制作規約](ledger/制作規約.yaml) | 8 | 制作規約の台帳。元資料の提案と確定状態を区別して保持する。 | 規約ID / 対象種別 / 対象ID / 区分 / 内容 / 確度 / 根拠 |
| [図配置](ledger/図配置.yaml) | 129 | MAPの接続模式図上の順序と座標。地理的な実距離ではない。 | 配置ID / エリアID / MAP_ID / 順番 / X / Y / 図ラベル / 備考 |
| [エリア構造](ledger/エリア構造.yaml) | 16 | area JSON の体内部位分類など、模式図座標では表せない構造値。経路・型・値で保持する。 | 経路 / 型 / 値 / 根拠 |
| [MAP仕様](ledger/MAP仕様.yaml) | 132 | MAPごとの個別仕様。原表の各行を名前付き列として保持し、MAP行へ重複転記しない。 | 仕様ID / MAP_ID / 原文ID表記 / 節 / 時期 / 一言特徴 / 経路・通行 / 暫定固定 / 原文列名 / 根拠 / 決定参照 / 特徴(自由記述) |
| [文書ビュー](ledger/文書ビュー.yaml) | 29 | 文書ビューの台帳。元資料の提案と確定状態を区別して保持する。 | ビューID / パス / 元の表 / ヘッダーJSON / 行参照 / 根拠 |
| [MAP契約](ledger/MAP契約.yaml) | 258 | 旧MAP仕様・契約表の移行先。参考、旧状態、既存素材、通行条件、未決の出典を保持する。 | 契約ID / MAP_ID / 資料区分 / 参照ID / 旧状態 / 画像識別子 / mask・出力 / 具体的TBD / 通行・接続 / 素材状態 / 根拠 / 特徴(自由記述) |
| [特殊遷移](ledger/特殊遷移.yaml) | 5 | 歩行接続ではない階選択やワープの遷移。未決の端点を推測しない。 | 遷移ID / 種別 / 階 / 起点MAP / 起点端 / 到着MAP / 行先表示 / 条件 / 状態 / 根拠 / 特徴(自由記述) |
| [体内幾何](ledger/体内幾何.yaml) | 419 | 体内の幾何入力。MAP・変種・経路ごとの型付き値を保ち、モック生成コードはこれを読む。 | 幾何ID / MAP_ID / 変種 / 経路 / 型 / 値 / 確度 / 根拠 / 特徴(自由記述) |
| [海外進行](ledger/海外進行.yaml) | 165 | 海外三塔の設計状態機械。経路ごとの型付き値からJSONを導出する。 | 経路 / 型 / 値 / 根拠 |
| [敵](ledger/敵.yaml) | 96 | 敵の台帳。元資料の提案と確定状態を区別して保持する。 | 敵ID / 名称 / 分類 / 登場設定 / 属性 / 弱点・耐性 / 役割 / 遭遇状態 / 画像状態 / 根拠 / 特徴(自由記述) |
| [召喚獣](ledger/召喚獣.yaml) | 8 | 召喚獣の台帳。元資料の提案と確定状態を区別して保持する。 | 召喚獣ID / 名称 / 登場・取得 / 属性 / 敵として戦うか / 画像状態 / 根拠 / 特徴(自由記述) |
| [敵サイズ](ledger/敵サイズ.yaml) | 73 | 敵サイズの台帳。元資料の提案と確定状態を区別して保持する。 | サイズ行ID / 敵ID / 形態 / グリッド種別 / 根拠 |
| [ダンジョン](ledger/ダンジョン.yaml) | 12 | ダンジョンの台帳。元資料の提案と確定状態を区別して保持する。 | ダンジョンID / 名称 / 含む地区・MAP / 時期 / 分ける理由 / 目標種数 / 備考 |
| [敵配置](ledger/敵配置.yaml) | 70 | 敵配置の台帳。元資料の提案と確定状態を区別して保持する。 | 配置ID / 敵ID / 召喚獣ID / ダンジョンID / 対象MAP / 時期 / 名前・サイズ / 理由 / ラーニング / 役割 / 個性パターン案 / 画像状態 / 評価 / 報酬の個性 / 再戦可否 / 採用状態 / 出典 / 特徴(自由記述) |
| [兼六園再登場](ledger/兼六園再登場.yaml) | 44 | 兼六園再登場の台帳。元資料の提案と確定状態を区別して保持する。 | 再登場ID / グループID / MAP_ID / 元ダンジョンID / 敵ID / 種数換算 / 理由 / 状態 |
| [ボスギミック](ledger/ボスギミック.yaml) | 28 | ボスギミックの台帳。元資料の提案と確定状態を区別して保持する。 | ギミックID / 内容 / 出典 / 実現可否 / 使う予定 / 採用状態 / 特徴(自由記述) |
| [戦闘パターン案](ledger/戦闘パターン案.yaml) | 21 | 戦闘パターン案の台帳。元資料の提案と確定状態を区別して保持する。 | パターンID / 対象ID / 案 / 根拠 / ギミックID / 実現可否 / 採用状態 |
| [敵戦利品](ledger/敵戦利品.yaml) | 6 | 敵戦利品の台帳。元資料の提案と確定状態を区別して保持する。 | 敵ID / ドロップ / ぬすむ通常 / ぬすむレア / 根拠 |
| [BGMスロット](ledger/BGMスロット.yaml) | 26 | BGMスロットの台帳。元資料の提案と確定状態を区別して保持する。 | スロットID / 抽象名 / 場面 / 気分 / Largo / 系統 / 長さ / 兼用先 / 状態 / 根拠 |
| [BGM回想編曲](ledger/BGM回想編曲.yaml) | 4 | BGM回想編曲の台帳。元資料の提案と確定状態を区別して保持する。 | 編曲ID / 元スロットID / 回想場面 / 編曲案 / 気分 / Largo / 系統 / 状態 |
| [BGM旧スロット対応](ledger/BGM旧スロット対応.yaml) | 54 | BGM旧スロット対応の台帳。元資料の提案と確定状態を区別して保持する。 | 対応ID / 旧スロットID / 旧抽象名 / 現行スロットID / 扱い / 理由 |
| [BGM録音](ledger/BGM録音.yaml) | 64 | BGM録音の台帳。元資料の提案と確定状態を区別して保持する。 | 録音行ID / 録音ID / 録音名 / 演奏者 / 録音年 / 楽章 / ファイルパス / ランク / ライセンス表記(原文) / 出典URL / クレジット文言 / ffprobeで実測した長さ(秒) / 形式 / 備考 |
| [BGMフレーズ](ledger/BGMフレーズ.yaml) | 15 | BGMフレーズの台帳。元資料の提案と確定状態を区別して保持する。 | フレーズ行ID / 主題ID / 楽章 / 主題名 / 録音ID / 元録音ID / 開始秒 / 終了秒 / 気分(悲/楽/緊) / 割当スロット候補 / 出力ファイル / 要耳確認 |
| [人物](ledger/人物.yaml) | 5 | 人物の台帳。元資料の提案と確定状態を区別して保持する。 | 人物ID / 呼称 / 旧接頭辞 / 牌 / 人物の芯 / 見た目の核 / 役割 / 根拠 / 特徴(自由記述) |
| [人物形態](ledger/人物形態.yaml) | 31 | 人物形態の台帳。元資料の提案と確定状態を区別して保持する。 | 形態ID / 人物ID / 年齢 / 衣装 / 車椅子 / マスターパス / 状態 / 根拠 |
| [素材移行](ledger/素材移行.yaml) | 712 | 旧素材の移動・削除・剪定先を監査可能な行で保持し、manifest JSONを導出する。 | 旧パス / 新パス / 操作 / 理由 / sha256 / 剪定パス |
| [素材移行設定](ledger/素材移行設定.yaml) | 8 | 素材移行設定の台帳。元資料の提案と確定状態を区別して保持する。 | 設定ID / 値 / 説明 |
| [刀候補](ledger/刀候補.yaml) | 31 | 刀候補の台帳。元資料の提案と確定状態を区別して保持する。 | 刀候補ID / 刀名 / 種別 / 作者 / 時代 / 指定 / 所蔵 / 特徴 / 逸話 / 個性の素 / 確度 / 注 / 出典 / 状態 |
| [刀配分案](ledger/刀配分案.yaml) | 20 | 刀配分案の台帳。元資料の提案と確定状態を区別して保持する。 | 配分ID / 人物ID / 枠 / 刀候補ID / 理由 / 状態 |
| [能力候補](ledger/能力候補.yaml) | 38 | 能力候補の台帳。元資料の提案と確定状態を区別して保持する。 | 能力ID / 候補 / 型・参照元 / 重荷 / 素質 / 時代 / 定番 / ジョブ重なり / cmd / MG / 状態 / 根拠 |
| [刀能力配分案](ledger/刀能力配分案.yaml) | 20 | 刀能力配分案の台帳。元資料の提案と確定状態を区別して保持する。 | 配分ID / 人物ID / 刀候補ID / 能力候補ID / 型 / 根拠 / 状態 |
| [ジョブ候補](ledger/ジョブ候補.yaml) | 4 | ジョブ候補の台帳。元資料の提案と確定状態を区別して保持する。 | 候補ID / 役割 / 人物ID / 履歴 / 候補プール / 根拠 / 状態 |
| [魔法](ledger/魔法.yaml) | 8 | 魔法の台帳。元資料の提案と確定状態を区別して保持する。 | 魔法ID / 属性 / 魔法名 / 効果 / 根拠 / 状態 |
| [Issue出典](ledger/Issue出典.yaml) | 2065 | 全Issue本文・コメントの安全化済み出典。原文SHA256と安全化SHA256を区別する。 | 出典ID / Issue番号 / 種別 / URL / 投稿日 / 本文SHA256 / 安全化SHA256 / 本文 / 点検状態 / 備考 |
| [Issue命題](ledger/Issue命題.yaml) | 3234 | Issue中の命題を分類し、決定・未決・既存台帳へ関連づける。 | 命題ID / 出典ID / 位置 / 要点 / 原文抜粋 / 帰属 / 分類 / 決定ID / 未決ID / 参照先 / 備考 |

### 台帳から導出した派生物（手編集禁止）

| 生成物ID | 種別 | パス | 再生成コマンド |
|---|---|---|---|
| G-map-ids | MAP ID登録JSON | [docs/topology/map-ids.json](topology/map-ids.json) | `uv run python3 .claude/skills/sit-field-background/tools/ledger_build.py build` |
| G-areas | MAP所属・模式図座標JSON | [docs/topology/areas.json](topology/areas.json) | `uv run python3 .claude/skills/sit-field-background/tools/ledger_build.py build` |
| G-overseas-progression | 海外三塔設計契約JSON | [docs/topology/overseas-progression.json](topology/overseas-progression.json) | `uv run python3 .claude/skills/sit-field-background/tools/ledger_build.py build` |
| G-TRM-02-plan | 斜めplan JSON | [docs/production/oblique-mocks/TRM-02-plan.json](production/oblique-mocks/TRM-02-plan.json) | `uv run python3 .claude/skills/sit-field-background/tools/ledger_build.py build` |
| G-TRM-03-plan | 斜めplan JSON | [docs/production/oblique-mocks/TRM-03-plan.json](production/oblique-mocks/TRM-03-plan.json) | `uv run python3 .claude/skills/sit-field-background/tools/ledger_build.py build` |
| G-TRM-04-plan | 斜めplan JSON | [docs/production/oblique-mocks/TRM-04-plan.json](production/oblique-mocks/TRM-04-plan.json) | `uv run python3 .claude/skills/sit-field-background/tools/ledger_build.py build` |
| G-TRM-05-plan | 斜めplan JSON | [docs/production/oblique-mocks/TRM-05-plan.json](production/oblique-mocks/TRM-05-plan.json) | `uv run python3 .claude/skills/sit-field-background/tools/ledger_build.py build` |
| G-TRM-06-plan | 斜めplan JSON | [docs/production/oblique-mocks/TRM-06-plan.json](production/oblique-mocks/TRM-06-plan.json) | `uv run python3 .claude/skills/sit-field-background/tools/ledger_build.py build` |
| G-TRM-07-plan | 斜めplan JSON | [docs/production/oblique-mocks/TRM-07-plan.json](production/oblique-mocks/TRM-07-plan.json) | `uv run python3 .claude/skills/sit-field-background/tools/ledger_build.py build` |
| G-TRM-08-plan | 斜めplan JSON | [docs/production/oblique-mocks/TRM-08-plan.json](production/oblique-mocks/TRM-08-plan.json) | `uv run python3 .claude/skills/sit-field-background/tools/ledger_build.py build` |
| G-TRM-09-plan | 斜めplan JSON | [docs/production/oblique-mocks/TRM-09-plan.json](production/oblique-mocks/TRM-09-plan.json) | `uv run python3 .claude/skills/sit-field-background/tools/ledger_build.py build` |
| G-TRM-10-plan | 斜めplan JSON | [docs/production/oblique-mocks/TRM-10-plan.json](production/oblique-mocks/TRM-10-plan.json) | `uv run python3 .claude/skills/sit-field-background/tools/ledger_build.py build` |
| G-TRM-11-plan | 斜めplan JSON | [docs/production/oblique-mocks/TRM-11-plan.json](production/oblique-mocks/TRM-11-plan.json) | `uv run python3 .claude/skills/sit-field-background/tools/ledger_build.py build` |
| G-TRM-12-plan | 斜めplan JSON | [docs/production/oblique-mocks/TRM-12-plan.json](production/oblique-mocks/TRM-12-plan.json) | `uv run python3 .claude/skills/sit-field-background/tools/ledger_build.py build` |
| G-TRM-13-plan | 斜めplan JSON | [docs/production/oblique-mocks/TRM-13-plan.json](production/oblique-mocks/TRM-13-plan.json) | `uv run python3 .claude/skills/sit-field-background/tools/ledger_build.py build` |
| G-TRM-14-plan | 斜めplan JSON | [docs/production/oblique-mocks/TRM-14-plan.json](production/oblique-mocks/TRM-14-plan.json) | `uv run python3 .claude/skills/sit-field-background/tools/ledger_build.py build` |
| G-TRM-15-plan | 斜めplan JSON | [docs/production/oblique-mocks/TRM-15-plan.json](production/oblique-mocks/TRM-15-plan.json) | `uv run python3 .claude/skills/sit-field-background/tools/ledger_build.py build` |
| G-TRM-16-plan | 斜めplan JSON | [docs/production/oblique-mocks/TRM-16-plan.json](production/oblique-mocks/TRM-16-plan.json) | `uv run python3 .claude/skills/sit-field-background/tools/ledger_build.py build` |
| G-TRM-17-plan | 斜めplan JSON | [docs/production/oblique-mocks/TRM-17-plan.json](production/oblique-mocks/TRM-17-plan.json) | `uv run python3 .claude/skills/sit-field-background/tools/ledger_build.py build` |
| G-decor-pools | 装飾プールJSON | [docs/production/oblique-mocks/decor-pools.json](production/oblique-mocks/decor-pools.json) | `uv run python3 .claude/skills/sit-field-background/tools/ledger_build.py build` |
| G-dependency-graph | 依存グラフJSON | [docs/production/oblique-mocks/dependency-graph.json](production/oblique-mocks/dependency-graph.json) | `uv run python3 .claude/skills/sit-field-background/tools/ledger_build.py build` |
| G-connections | 接続図JSON | [docs/production/oblique-mocks/connections.json](production/oblique-mocks/connections.json) | `uv run python3 .claude/skills/sit-field-background/tools/ledger_build.py build` |
| G-connections-teramachi | 接続図JSON | [docs/production/oblique-mocks/connections-teramachi.json](production/oblique-mocks/connections-teramachi.json) | `uv run python3 .claude/skills/sit-field-background/tools/ledger_build.py build` |
| G-asset-migration | 素材移行JSON | [docs/production/20261018-asset-migration.json](production/20261018-asset-migration.json) | `uv run python3 scripts/build_ledger.py build` |
| G-bgm-sources-csv | BGM CSVビュー | [docs/bgm-sources.csv](bgm-sources.csv) | `uv run python3 scripts/build_ledger.py build` |
| G-bgm-phrases-csv | BGM CSVビュー | [docs/bgm-phrases.csv](bgm-phrases.csv) | `uv run python3 scripts/build_ledger.py build` |

### ファイル配置規則

置き場所の規則の正本は [ファイル配置.yaml](ledger/ファイル配置.yaml)。パターンは repo root からの相対パスに fullmatch する正規表現。到達=リンクのファイルは INDEX からのリンクの連鎖で辿れなければ孤立（`ruby scripts/verify_index_reachable.rb`）。

| 配置ID | 種別 | 用途 | 到達 | 入口 |
|---|---|---|---|---|
| root-readme | ドキュメント | リポの入口（概要・ドキュメント一覧） | リンク |  |
| root-config | 設定 | Git 除外・Python 依存宣言（PyYAML）。ドキュメントではない | 許可 |  |
| docs-index | ドキュメント | 全ドキュメント・台帳・ツール・スキルへの入口（表一覧は台帳からの生成ビュー） | リンク |  |
| docs-top | ドキュメント | 企画・仕様・台帳（md）。docs 直下。INDEX から到達できること | リンク |  |
| docs-bgm-data | データ | BGM録音・フレーズ YAML から生成する互換 CSV（手編集禁止） | リンク |  |
| ledger-master | 台帳マスター | 日本語キー YAML。情報の唯一のマスター（人が編集する） | リンク |  |
| ledger-views | 台帳の生成ビュー | 人が読む md ビュー（MAP・建物・決定・未決・採用要素・接続）。台帳から生成する（手編集禁止） | リンク |  |
| ledger-handoff | 引き継ぎ（一時） | 台帳DB化の WIP 引き継ぎ資料・移行スクリプト・監査記録 | 許可 | docs/ledger/handoff/HANDOFF.md |
| topology-doc | ドキュメント | 全MAP接続図の説明 | リンク |  |
| topology-svg | 生成図 | 接続図（svg） | リンク |  |
| topology-json | データ | MAP ID登録・所属配置・海外進行の YAML 派生ビュー（手編集禁止） | リンク |  |
| production-doc | ドキュメント | 制作の記録・採用記録・素材ID配置 | リンク |  |
| production-json | データ | 素材移行 manifest は YAML 派生、MAP改名対応表は凍結記録 | リンク |  |
| production-prompts | プロンプト記録 | 採用時に送信したプロンプトの逐語記録 | 許可 | docs/production/20261022-bdy02-adoption.md;docs/production/20261022-body-maps-adoption.md;docs/production/20261023-trm04-adoption.md |
| body-masks | 機械出力 | 体内17MAPのマスク登録・links・承認記録 | 許可 | docs/production/20261022-body-maps-adoption.md |
| body-mocks | 機械出力 | 体内17MAPの割付モック・clean 画像・幾何 | 許可 | docs/production/20261022-body-mocks-and-registration.md |
| oblique-masks-doc | ドキュメント | 斜め視点マスクの入力・結果の説明 | リンク |  |
| oblique-masks-data | 機械出力 | 斜め視点マスクの入力JSON・register・結果 | 許可 | docs/production/oblique-masks/README.md |
| oblique-mocks | 派生物・機械出力 | 斜め視点の plan・decor-pools・connections・dependency-graph（台帳から導出する JSON）と、MAPごとのモック・マスク・生成テイクの測定結果 | 許可 | docs/production/oblique-mocks/connections.md |
| reviews | レビュー記録 | 独立レビュー（red-team）の日付つき記録 | 許可 | docs/reviews/artifact-redteam |
| verification-body-docs | 生成ドキュメント | 体内の整合表・全接続一覧（自動生成） | リンク |  |
| verification-body-data | 機械出力 | 体内17MAPの検証画像・割付図・幾何・送信文 | 許可 | verification/body-layout/consistency.md |
| verification-characters-doc | ドキュメント | キャラ素材の加工（切り出し）の手順 | リンク |  |
| verification-characters-tools | ツール | キャラ素材の切り出しスクリプト | 許可 | verification/characters/tools/README.md |
| verification-audit | 検証記録 | 敵画像の透過監査（2026-10-22） | 許可 | verification/transparency-audit-20261022/audit-notes.md |
| brand-readme | ドキュメント | ブランド素材の説明 | リンク |  |
| scripts | スクリプト | 検証・描画・生成のスクリプト | リンク |  |
| tests | テスト | unittest（uv run python3 -m unittest discover -s tests） | リンク |  |
| skills-doc | スキル | 制作スキルの手順書・ツール一覧 | リンク |  |
| skills-agent | スキル | スキルのエージェント定義 | リンク |  |
| skills-tools | ツール | フィールド背景の制作ツール（台帳 ledger_*.py・体内 body_*.py・斜め oblique_*.py） | リンク |  |
| asset-enemies | 画像正本 | 敵（monsters.md の ID。M006・M014 は同一IDの派生ポーズ・形態を -suffix で持つ） | 許可 | assets/images |
| asset-summons | 画像正本 | 召喚獣（S001・S003・S005・S006 は段階・形態を -suffix で持つ） | 許可 | assets/images |
| asset-characters | 画像正本 | 人物（C管理ID別） | 許可 | assets/images |
| asset-field-legacy | 画像正本 | MAP旧素材（現存のみ。新規生成先ではない） | 許可 | assets/images |
| asset-field-legacy-masks | 画像正本 | 旧接続の検証専用マスク（可逆WebP） | 許可 | assets/images |
| asset-field-reference | 画像正本 | 外観参照・採用基準状態（kebab-case・非可逆WebP品質85） | 許可 | assets/images |
| asset-field-masks | 画像正本 | 体内・寺町（斜め視点）のマスク（mask・edit は可逆、overlay は非可逆。runtime 切替前） | 許可 | assets/images |
| asset-battle-backgrounds | 画像正本 | 戦闘背景（現存はBG001。BG005は没・削除） | 許可 | assets/images |
| asset-brand | 画像正本 | ブランド（暫定の文字ロゴ。svg が正本・png は派生） | 許可 | assets/images |
| ledger-closure | 監査文書 | Issue #156 の元資料ごとの移行先と未解決ゲート | リンク |  |
| ledger-content-view | 台帳の生成ビュー | 非MAPコンテンツ24表の検索ビュー | リンク |  |
| asset-weapons | 画像正本 | 復元した旧刀マスター画像。採用・所有者は未決 | 許可 | assets/images |
| ledger-branch-audit | 監査文書 | 関連枝の捕捉時点のGit比較・除外理由。ゲーム情報の正本ではない。 | リンク |  |
| ledger-resume | 監査文書 | WIP再開条件と検証入口 | リンク |  |
| asset-effect-candidates | 画像候補 | 戦闘演出（詠唱・ヒット・ダメージ数字）の候補画像。採否は素材台帳の状態に従う | 許可 | assets/images |
| asset-effect-character | 画像候補 | 人物別の演出候補画像（魔法・移動・端末の光） | 許可 | assets/images |
| asset-field-emotion | 画像正本 | フィールドの人物に添える感情吹き出し（採用）。256x256 透過PNG | 許可 | assets/images |
| asset-shared-adopted | 画像正本 | 人物共通（フィールドの汎用モブNPCなど、特定の C 管理IDを持たない人物）の採用素材。透過切り抜き WebP | 許可 | assets/images |
| asset-shared-candidates | 画像候補 | 人物共通の外観候補（所有者は未決） | 許可 | assets/images |
| asset-weapon-candidates | 画像候補 | 人物別の刀（軌跡を含む）の候補画像 | 許可 | assets/images |
| asset-metadata-json | 画像用メタデータ | 候補画像の付随JSON。素材メタデータ表から生成する安全化済み出力 | 許可 | assets/images |
| output-sword-previews | プレビュー画像 | 刀候補20本と斬撃ポーズの重ね確認画像（採用判断の参考） | 許可 | output/battle-sword-previews/README.md |
| output-sword-previews-readme | プレビュー説明 | 刀プレビューの読み方 | リンク |  |

<!-- GENERATED:END ledger-views -->
