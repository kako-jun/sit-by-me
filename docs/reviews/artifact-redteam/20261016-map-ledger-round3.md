# MAP台帳・トポロジー敵対レビュー（第3周・修正後）

> 当時のパス・判定を保持した履歴です。現行配置・削除／復元元は [#68素材対応表](../../production/asset-layout.md) を参照。

- 日付: 2026-10-16
- レビュアー: 独立 red-team reviewer（台帳・個別仕様の作成者とは別）
- 対象: `content-registry.md`、`map-asset-registry.md`、`map-contract-checklist.md`、`map-specifications.md`、`map-topology.md` v2、`map-reference-research.md`、`scripts/verify_map_ledger.rb`
- 結論: **pass（台帳の保留判定と修正対象の整合性）**。これは背景画像やwalk maskの採用承認ではない。

## 検査したことと根拠

| 検査 | 結果 | 根拠 |
|---|---|---|
| ID・台帳横断 | pass | 検証器が `contracts=104`、`assets=104`、`specs=104` を報告 |
| 参考根拠 | pass | 33 Refが宣言され、104契約行の全Refが解決する |
| 接続正本 | pass | v2には104 MAPすべてが登場し、同一画像辺の再利用は0、edgeは反対辺同士 |
| 修正した方位矛盾 | pass | F07、F09→E25→F10→E23、F41〜F60の入力方位がv2と一致 |
| 状態遷移 | pass | `legacy-needs-review` 33件、`blocked` 71件、`ready` 0件。TBDを残すMAPをreadyにしていない |
| maskの表現 | pass（保留） | E01〜E33は`mask未記録`、N1〜N12/F01〜F60は`mask未作成`。完了マスク0件を完了扱いしていない |

## 残る生成ブロッカー（意図的・具体的）

1. 全104 MAPに具体的TBDが残り、walk maskも未完了である。従って、どれも生成・採用に進めない。
2. `E31` は既存画像の海が上側で、正本の「能登の海は下側」と矛盾する。既存画像は採用禁止であり、回転ではなく再構図版を用意するまで保留する。

## 判定の範囲

今回のpassは「生成保留の根拠が104行に記録され、既知の接続矛盾を放置していない」ことへの判定である。各画像を `ready` または採用済みに変えるには、実画像・編集用mask・runtime mask・foreground mask・再度の画像単位red-teamを別途行う。
