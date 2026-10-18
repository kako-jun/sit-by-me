# 寺町 E09 v6 マスク・独立 red-team レビュー

> 当時のパス・判定を保持した履歴です。現行配置・削除／復元元は [#68素材対応表](../../production/asset-layout.md) を参照。

- 日付: 2026-10-16
- レビュアー: 独立 red-team reviewer（候補・maskの作成者ではない）
- 対象: `E09 old-slope-foot` v6 の背景、JSON、traversal/foreground edit、runtime masks
- 正本: content／asset／specification／topology／reference registry、art-direction、assets policy、`sit-diorama`、`sit-field-mask`、`sit-artifact-redteam`

## pass: 素材とマスク契約

- `E08.right ↔ E09.left` と `E09.top ↔ E13.bottom` の4 linksは、すべて反対辺・`[590,690]`・`assist`・`standing-or-companion-assist` で一致する。
- E08.right、E09.left/top、E13.bottomは、standing／assist runtimeで各101pxが白。E09の二出口は単一連結成分である。
- E09 wheelchairと互換`-mask.png`は全黒、right/bottomも全黒。white（universal）は存在しない。
- `traversal-edit`は黒と橙だけの1254×1254 RGBで、runtime outputsはその編集PNGから一致して導出される。
- foreground edit/runtimeは全ゼロ。遮蔽のない透明RGBA foregroundも同梱し、通行判定との衝突はない。
- 生画像でも左の石畳→中央石段→上端が確認でき、人物・可読文字はない。冬の手作りジオラマとして読める。

## 採用前の境界

素材・マスクは **pass**。ただし現行`*.field.json`は旧`diorama-trial`の背景・mask・linksを参照しており、v6を実ゲームで使う変更はまだ行っていない。これは候補のlegacy差替え／runtime参照更新を採用判断として残すためである。従って本レビューは素材を自動採用しない。
