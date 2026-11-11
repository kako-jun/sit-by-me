<!-- 生成物。台帳が正本。編集しない。 暫定: 各台帳の「暫定」列を参照 -->
# play/（name-name の /play が読む md）

**生成物。台帳が正本。編集しない。** `uv run python3 scripts/build_ledger.py build` で作り直す。
name-name の worker が `scriptsDir=play` として `play/` 直下とサブディレクトリ1段（`events/`）の md を読む。
暫定の項目と理由は各台帳の「暫定」列が正本（ここには複製しない）。台帳の状態は blocked のまま。

| 生成ファイル | 正本 |
|---|---|
| [script.md](script.md)（入口） | 台帳 docs/ledger/イベント/opening_battle.yaml の出現位置 |
| [data.md](data.md) | 敵.yaml・人物.yaml・イベント台帳の敵（数値は opening_battle の暫定列を参照） |
| [events/opening_battle.md](events/opening_battle.md) | [opening_battle.yaml](../docs/ledger/イベント/opening_battle.yaml) |
| [events/evacuation_after_play.md](events/evacuation_after_play.md) | [evacuation_after_play.yaml](../docs/ledger/イベント/evacuation_after_play.yaml) |
| [events/play_cancelled_promise.md](events/play_cancelled_promise.md) | [play_cancelled_promise.yaml](../docs/ledger/イベント/play_cancelled_promise.yaml) |

## 途中の場面から始める（デモ・確認の手順）

オープニングを毎回通らない。**再開点を選んで `?resume=` で開く**（セーブ JSON は台帳 `docs/ledger/再開点/` から生成）。

1. `play/saves/<再開点ID>.save.json`（下の一覧）を選ぶ。
2. /play を開くのと同じオリジンのコンソールで `localStorage.setItem('name-name-save-field-0', <その JSON の中身>)`。
3. `/play/sit-by-me?resume=0` を開く。

| 再開点 | 内容 |
|---|---|
| [opening_battle_fight](saves/opening_battle_fight.save.json) | お遊戯会の劇戦闘の最中 |
| [opening_battle_start](saves/opening_battle_start.save.json) | お遊戯会の劇戦闘の開始から |
| [play_cancelled_promise_start](saves/play_cancelled_promise_start.save.json) | 劇の中止後の約束の会話から |
| [playground_walk](saves/playground_walk.save.json) | 運動場（劇の中止後の場面）を歩く |
| [playroom_walk](saves/playroom_walk.save.json) | 遊戯室（お遊戯会の場面）を歩く |

セーブからの再開直後は、既定では場面開始のトリガーを起こさない。`*_start` の再開点は `field.fireAuto: true`（name-name Issue #1155）で、その場面のイベント（劇戦闘・約束の会話）を再開直後に起こす。#1155 が入るまでは歩けるだけ（各再開点の暫定に書く）。

見た目の決定の一覧と、画面を見せてよい状態のチェックリスト: [demo-look-list.md](../docs/production/demo-look-list.md)

人物の形態の目録（歩行絵・戦闘ポーズの一覧）: `assets/field/sit-character-forms.json`（素材のファイル名から生成）。

