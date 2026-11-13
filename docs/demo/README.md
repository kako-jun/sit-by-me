# 早期デモ（全部入りサンプル）の仕様の入口

kako-jun に見せる「最初に遊べる範囲」の全部入りサンプルについて、**ここが仕様の入口（正本の地図）**。この文書は決定や数字を持たない。決定は台帳、進捗は Issue、中身は各領域の正本にあり、ここは**どこを見ればよいかのリンクと、守る原則**だけを書く（多重管理しない）。

- 親 Issue: [#276](https://github.com/kako-jun/sit-by-me/issues/276)（子 Issue の一覧と進行はそこ。進捗の数字はこの文書に書かない）
- 決定の登録: [決定.yaml](../ledger/決定.yaml) の `DEMO.*`（人が読むビューは [決定](../ledger-views/決定.md)）

## 目的

「ゲームらしく、最初のイベント戦闘や幼稚園での自動イベント、自由なマップ散策、エンカウント、メニューを開いてアイテムを使ってレベル上げ、という当たり前の RPG らしいことができる」状態を、kako-jun の手元で触って確かめられるようにする（原点は [#238](https://github.com/kako-jun/sit-by-me/issues/238) 本文、name-name [#1084](https://github.com/kako-jun/name-name/issues/1084)）。**完了の判定は kako-jun の手元の実機操作**で、テストが通ったことや Issue を閉じたことではない。

## 範囲

- **香林坊（E004〜E007）は含めない**。まずはマップを歩くところから。店（name-name #1085）も今回は不要。決定 `DEMO.sample-excludes-korinbo`。
- 範囲を決めた順序・失効した案（本編の寺町から10MAPを切り出す案）は決定 `DEMO.sample-map-independent-of-main` の備考にある。

## 原則

1. **サンプルのマップは、本編の寺町とは別の独立したマップ**。本編の MAP ID・接続・台帳（[MAP.yaml](../ledger/MAP.yaml)・[接続.yaml](../ledger/接続.yaml)）は借りない・変えない。**寺町に似せるのは背景素材だけ**（採用済みの寺町の画像を背景に流用する）。決定 `DEMO.sample-map-independent-of-main`。
2. **行き止まりを作らない**。サンプルの接続は、使える出口がすべてどこかにつながり、全マップが1つにつながる。台帳の検証（[verify_domain_ledger.py](../../scripts/verify_domain_ledger.py)）が落とす。
3. **マップ以外は実際のゲームと同じ**。デモ専用の仕組み・UI・設定キーを作らず、実際のゲームの状態（セーブ）をロードして見せる。違ってよいのはマップ（場面・背景・マスク・リンク・出会いの敵の組み合わせ・NPC の配置）だけ。決定 `DEMO.real-game-save-only-map-differs`。
4. **架空の内容を作らない**。魔法・状態異常・敵・味方・装備・魔石は sit-by-me に実在するもの（台帳・docs に定義があるもの）だけ。実在するなら、ゲームを普通に進めていては手に入らない時期に持たせてよい。台帳に数値が無いものは暫定の数値と明記して置く。決定 `DEMO.real-game-save-only-map-differs`。
5. **決定は先に台帳へ**。会話や Issue の逐語は、決定表に登録してから参照する（[INDEX](../INDEX.md) の運用）。台帳を直すとき、本文を別の文書に複製しない。

## サンプル専用のエンカウント

寺町の道路（サンプルの道路3枚）にだけ、**サンプル専用のスイッチ**で通常エンカウントを入れる。本編の決定（[systems.md](../systems.md) の「スマホ購入前の寺町では通常のエンカウントはない」）は書き換えない。決定 `DEMO.sample-road-encounter-switch`。どの敵を出すかは**未決**（台帳に未登録）。

## サンプルのマップ

- 台帳: [サンプルMAP.yaml](../ledger/サンプルMAP.yaml)（1行=1マップ。流用元の本編 MAP、戦闘背景、エンカウントの有無、起動するイベント）と [サンプル接続.yaml](../ledger/サンプル接続.yaml)（マップどうしの接続。出口は流用元 MAP の端ID）。現在は**案で、kako-jun の承認待ち**（[#250](https://github.com/kako-jun/sit-by-me/issues/250) の「接続図を作り承認を得てから実装」）。
- 背景の画像・出口の画像上の位置は、本編の採用画像と [oblique-mocks](../production/oblique-mocks/connections.md) の mask.json が正本で、サンプルの台帳には座標を複製しない。
- 歩行マスクの用意（07・08・15 は webp 化されていない）、play/ への生成、出口を踏んで場面を移る機構は**実装タスク**で、この文書の対象外。

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

## 経緯（失効した指示。参照だけ）

デモの作り方の指示は何度か変わった。現在有効なのは上の原則（決定 `DEMO.*`）で、過去の次の指示は**上書き済み**。

- 専用マップを作らず本編の途中をセーブで再開する（name-name [#1020](https://github.com/kako-jun/name-name/issues/1020)）→ マップだけは別でよい、に修正（name-name [#1051](https://github.com/kako-jun/name-name/issues/1051)）。
- 名前に「サンプル」が付くものは不要（name-name [#1066](https://github.com/kako-jun/name-name/issues/1066)。寺町のサンプル設定 `teramachi.sample.json` を削除）→ サンプル専用のマップは作る、に上書き（決定 `DEMO.sample-map-independent-of-main`）。`teramachi.sample.json` と「寺町フィールド遭遇サンプル」（[#65](https://github.com/kako-jun/sit-by-me/issues/65)・決定表の古い記述）は現存しない。後継は実際のゲームをロードする `/play/sit-by-me` とこの文書のサンプルマップ。
- 「デバッグ用の特殊マップを1つだけ作って使い回す」（#1051、name-name [#1063](https://github.com/kako-jun/name-name/issues/1063) は未着手）とサンプル専用マップが同一物かは**未決**。
