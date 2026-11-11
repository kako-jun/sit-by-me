<!-- 生成物。台帳が正本。編集しない。 暫定: 背景・マスク・座標・数値 -->
# play/（name-name の /play が読む md）

**生成物。台帳が正本。編集しない。** `uv run python3 scripts/build_ledger.py build` で作り直す。
name-name の worker が `scriptsDir=play` として `play/` 直下とサブディレクトリ1段（`events/`）の md を読む。
背景・マスク・座標・数値は暫定（台帳の「暫定」列）。台帳の状態は blocked のまま。

| 生成ファイル | 正本 |
|---|---|
| [script.md](script.md)（入口） | 台帳 docs/ledger/イベント/opening_battle.yaml の出現位置 |
| [data.md](data.md) | 敵.yaml・人物.yaml・イベント台帳の敵（数値は暫定） |
| [events/opening_battle.md](events/opening_battle.md) | [opening_battle.yaml](../docs/ledger/イベント/opening_battle.yaml) |
| [events/evacuation_after_play.md](events/evacuation_after_play.md) | [evacuation_after_play.yaml](../docs/ledger/イベント/evacuation_after_play.yaml) |
| [events/play_cancelled_promise.md](events/play_cancelled_promise.md) | [play_cancelled_promise.yaml](../docs/ledger/イベント/play_cancelled_promise.yaml) |

人物の形態の目録（歩行絵・戦闘ポーズの一覧）: `assets/field/sit-character-forms.json`（素材のファイル名から生成）。

