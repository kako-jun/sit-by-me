# 早期デモ（全部入りサンプル）の仕様の入口

kako-jun に見せる「最初に遊べる範囲」の全部入りサンプルについて、**ここが仕様の入口（正本の地図）**。この文書は決定や数字を持たない。決定は台帳、進捗は Issue、中身は各領域の正本にあり、ここは**どこを見ればよいかのリンクと、守る原則**だけを書く（多重管理しない）。

- 親 Issue: [#276](https://github.com/kako-jun/sit-by-me/issues/276)（子 Issue の一覧と進行はそこ。進捗の数字はこの文書に書かない）
- 決定の登録: [決定.yaml](../ledger/決定.yaml) の `DEMO.*`（人が読むビューは [決定](../ledger-views/決定.md)）

## 目的

「ゲームらしく、最初のイベント戦闘や幼稚園での自動イベント、自由なマップ散策、エンカウント、メニューを開いてアイテムを使ってレベル上げ、という当たり前の RPG らしいことができる」状態を、kako-jun の手元で触って確かめられるようにする（原点は [#238](https://github.com/kako-jun/sit-by-me/issues/238) 本文、name-name [#1084](https://github.com/kako-jun/name-name/issues/1084)）。**完了の判定は kako-jun の手元の実機操作**で、テストが通ったことや Issue を閉じたことではない。

## 範囲と原則（本文は決定にある。ここは見出しとリンクだけ）

- 範囲（香林坊を含めない）: 決定 `DEMO.sample-excludes-korinbo`
- 原則1 サンプルのマップは本編の寺町とは別の独立したもの: 決定 `DEMO.sample-map-independent-of-main`。背景はサンプル専用の「時の最果て」風の抽象空間（寺町の流用は取り下げ）: 決定 `DEMO.sample-bg-last-place`（Issue [#281](https://github.com/kako-jun/sit-by-me/issues/281)）
- 原則2 サンプルは1マップ（接続・マップ端の切り替えなし）: 決定 `DEMO.sample-single-map`、検査は [verify_domain_ledger.py](../../scripts/verify_domain_ledger.py)
- 原則3 マップ以外は実際のゲームと同じ（セーブをロードして見せる）: 決定 `DEMO.real-game-save-only-map-differs`
- 原則4 架空の内容を作らない: 同上
- サンプル専用のエンカウント: 決定 `DEMO.sample-road-encounter-switch`
- 決定は先に台帳へ: 決定 `DEMO.spec-single-canonical-doc` と [INDEX](../INDEX.md) の運用
- 失効した過去の指示の経緯: 決定 `DEMO.sample-map-independent-of-main` の備考

決定は [決定.yaml](../ledger/決定.yaml)（人が読むビューは [決定](../ledger-views/決定.md)）。

## サンプルのマップ

- **サンプルは1マップ**（決定 `DEMO.sample-single-map`）。マップ端の切り替え・複数マップ・接続表は作らない。
- 台帳: [サンプルMAP.yaml](../ledger/サンプルMAP.yaml)（SMP-01 の1行。流用元の本編 MAP、戦闘背景、エンカウントの有無、起動するイベント）。
- 背景はサンプル専用の「時の最果て」風マップ（暗い星空の虚空に浮かぶ円形の石の足場・数本の柱・淡い光源。決定 `DEMO.sample-bg-last-place`）。画像はモック承認後に生成する（現状は未生成で、`play/` は旧 TRM-03 流用の背景のまま）。モックと平面スペックは [sample-field/](../production/sample-field/SMP-01-plan.json)（台帳から導出する plan ではなく、サンプル専用。本編の台帳に行を足さない）。座標・画像は複製せず、素材ID/MAP ID で参照するだけ。
- E001〜E003 のつなぎ方（方針だけ）: 3つとも SMP-01 の同じマップの中で、場面ごとの [トリガー]（イベントの起動条件）で起動する。マップを渡り歩かない。E001 の戦闘の中断後に E002、続けて E003（運動場の約束）へ進み、背景・出現位置・行き先はイベント台帳（[イベント/](../ledger/イベント/)）が正本。E003 の末尾からサンプルの歩ける場面 `sample_field` へ `[場面移動:]` で移る（生成器 [field_md.py](../../scripts/field_md.py) が出す。台帳 サンプルMAP.yaml の起動イベントの最後が入り口）。
- 背景の画像・歩行マスクは、承認・採用後に素材.yaml へ登録する（それまでは [sample-field](../production/sample-field/SMP-01-plan.json) のモックが設計）。
- 歩ける場面 `sample_field`（歩行マスク・戦闘背景 BG013・サンプル専用のエンカウント）と再開点 `sample_field_walk` は field_md.py が play/ に生成する（サンプル専用・暫定。敵は M101・M104・M148 の仮の数値で、数値の正本は [#237](https://github.com/kako-jun/sit-by-me/issues/237)）。マップ端の切り替えは作らない。

## 見せ方（確認の仕方）

- 見せる場所は `/play/sit-by-me`（name-name）。入口は [play/README.md](../../play/README.md)（台帳から生成。再開手順はそこが正本）。
- 見せる前に、画面の見た目の決定を満たしていることを確認する。突き合わせの記録は [demo-look-list.md](../production/demo-look-list.md)（決定の一覧ではなく、満たしているかの記録。最新の状態は Issue と実機が真実）。
- 生成した画像・実機の画面の確認は kako-jun が手元で行う。

## 領域ごとの正本（リンクだけ）

| 領域 | 正本 |
|---|---|
| 決定（逐語・出典） | [決定.yaml](../ledger/決定.yaml) |
| 戦闘・エンカウント・メニュー・成長のルール | [systems.md](../systems.md)・[決定ログ](../decisions.md) |
| 画面の見た目の決定 | [demo-look-list.md](../production/demo-look-list.md)（出典は [field-ui-wireframe.md](../field-ui-wireframe.md) ほか） |
| イベントのセリフ・脚本 | 台帳（[イベント/](../ledger/イベント/)・[NPCセリフ.yaml](../ledger/NPCセリフ.yaml)・[NPC配置.yaml](../ledger/NPC配置.yaml)）。`play/` の md は台帳から生成するスナップショット（[#250](https://github.com/kako-jun/sit-by-me/issues/250)） |
| 敵・魔法・人物 | [敵.yaml](../ledger/敵.yaml)・[魔法.yaml](../ledger/魔法.yaml)・[人物.yaml](../ledger/人物.yaml) |
| 数値（能力値・経験値・価格） | 台帳に数値は無い。案は [#237](https://github.com/kako-jun/sit-by-me/issues/237)（暫定と明記する） |
| 戦闘背景 | [戦闘背景.yaml](../ledger/戦闘背景.yaml)（[#267](https://github.com/kako-jun/sit-by-me/issues/267)） |
| 寺町の画像（背景素材） | [素材.yaml](../ledger/素材.yaml)・[MAP.yaml](../ledger/MAP.yaml)（[#191](https://github.com/kako-jun/sit-by-me/issues/191)） |
| エンジン側（name-name）の足りない機能 | name-name [#1084](https://github.com/kako-jun/name-name/issues/1084) |
