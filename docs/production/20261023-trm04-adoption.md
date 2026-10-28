# TRM-04 本堂（室内）基準状態の採用記録（2026-10-23、#144）

## 採用
- 採用: `docs/production/oblique-mocks/TRM-04/e2/take4.png`（E2 案1の4枚目）。**根拠: kako-jun「04は４枚目」（2026-10-23、4テイクを目視して選択）**。他の3テイク・追加1巡 `retry1` は没。
- 保存先（正本）: `assets/images/fields/reference/teramachi-main-hall-interior-trm04-adopted.webp`（WebP 品質85・実寸 1672×941・リサイズなし・333,634 bytes）、sha256 `46027605e2631821ab653cab27c147b8bb5eb5e3dff002130dbb90e634efa81d`。元 PNG（codex 出力、2,972,537 bytes）の sha256 `11d406356da181527143609e059e9c82b8eb8968c0c6a0b50282ba4e694779a1`（`［ホーム相対パス省略］/generated_images/` の本ラン生成物と一致を確認済み。偽造なし）。
- 生成: 2026-10-23 15:28〜15:32（JST）、`codex exec`（codex-cli 0.163.0・`$imagegen` 明示・品質 high・reasoning high）。`oblique_e2_run.sh TRM-04 4 e2`。
- 送信文（プロンプト全文）: [TRM-04-prompt-send.txt](20261023-trm04-adoption-prompts/TRM-04-prompt-send.txt)（sha256 `f01ef03e06741c3142912d8b0d5db3f406487b35be7a8d52e20c3c1120af9805`。edit-prompt v4＋参照・出力の節）。
- 参照画像（2枚。様式参照なし）: クリーンモック `docs/production/oblique-mocks/TRM-04/TRM-04-clean.png`（sha256 `aa3db6ff210b15538c9f026c53b0d00428d82a767783f8c6c18c346e34437822`、編集元）、素材見本 `verification/body-layout/BDY-material-swatch-corrugated-edge.png`（sha256 `764b7ae7f1aa0ff19bd8e79a8724fc8b975c4d5465440fb539f5566f52828b45`）。
- plan: `docs/production/oblique-mocks/TRM-04-plan.json`、manifest の `adoption` に記録（`oblique_build.py --adopt`）。decor_pool=teramachi-winter（エリア固定: 机・松＋枯木・台座を継承）。look は旧採用画像 v11（git fbe876a）を1回見て拾った。

## 測定値（参考。判定ではない）
recall@6px 0.839（ずらし基準 0.449）・Chamfer 3.67px・領域OK率 0.727・窓 6/6 が ±8px 内・戸口 1/3。装飾（参考）: 前縁・床の密度が元画像比 0.5 前後、松の緑量は基準 0.003 未満、外周の木の辺の判定は N・S 中心（本堂は廊下が全幅で左右の帯が狭い）。机はエリア固定から ΔE 7.6・板目は横。詳細 `docs/production/oblique-mocks/TRM-04/e2/metrics.md`・`e2-report.md`。

## マスク・オクルージョン（モック由来。採用画像から逆算していない）
`assets/images/fields/masks/TRM-04-{mask,traversal-edit,mask-overlay,foreground-edit,foreground-mask}.webp`（可逆WebP・1672×941）。`TRM-04-mask` は `TRM-04-mask.png`（モックから決定論で出した歩行マスク）、`foreground-*` は `TRM-04-occlusion*`（手前の壁・背の高い家具が隠す領域）。以前の採用画像（v11）から逆算した旧マスクは置き換えた。生成画像がモックの幾何を保つ限りマスクと絵は一致する前提で、位置合わせの red-team は未実施（台帳の status は変えない。ready 化は red-team・遷移のTBD解消後）。

## 没の記録（2026-10-23。kako-jun 判定）
- 没: TRM-04 の take1〜3 と `retry1`、TRM-02 の round1〜3（+round3-remeasure）、TRM-03 の e2・retry1、TRM-05 の e2・retry1、TRM-05-kids・TRM-05-fire の e2。
- 理由: **依存順を無視して並列生成したため**。本堂が決まると扉のデザインが決まり、住居を1つ作ってからでないと家具のデザインが一致しない。外観は内部が全部確定してから。生成画像は削除済み（測定 md/json・prompt・e2-report は経緯として残す）。
- 今後は直列（確定→その画像を参考画像として次へ）。依存関係で決める（通路的な独立マップは並列）。`.claude/skills/sit-field-background/SKILL.md` の「依存順の直列方式」参照。

## 補足: 開口描画の修正との関係（2026-10-23）
開口（passage の戸口・仕切りの開口）の描画を直した（壁の立体を開口の幅で切り抜き・緑の塗りと枠線）。TRM-04 のモック（clean・review・occlusion 系の PNG）は再生成で変わったが、**歩行マスク（TRM-04-mask.png）は不変**、採用画像と `assets/images/fields/masks/TRM-04-*.webp`（採用時に作成）・台帳は据え置き。採用時のモックの sha（manifest の adoption.mock_clean_sha256）と現行モックは異なる。
