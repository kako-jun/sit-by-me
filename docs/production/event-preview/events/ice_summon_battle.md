<!-- 生成物: docs/ledger/イベント/ice_summon_battle.yaml が正本。仮稿・ゲームへ接続しない。未決: 発火条件・パーティID・台詞・敵HP・入手処理は仮 -->

## ice_summon_battle: 凍った森との戦い（仮稿）

[戦闘 ice_summon_battle]
名前: 凍った森
敵: S002
台詞: 条件=開始 話者=主人公 文=木が、動いてる？
台詞: 条件=開始 話者=相方 文=下がって！
勝利時: 次=ice_summon_after
[/戦闘]

[イベント ice_summon_battle]
[戦闘: ice_summon_battle]
[/イベント]
