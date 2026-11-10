<!-- 生成物: docs/ledger/イベント/opening_battle.yaml が正本。仮稿・ゲームへ接続しない。未決: 中断条件（3ターンは仮）、技の具体、シャーの台詞の採否、敵味方IDの名前対応、遷移先と接続 -->

## opening_battle: お遊戯会の劇戦闘（仮稿）

[戦闘 opening_battle]
名前: お遊戯会の劇
敵: M001
にげる: 不可
固定: 結果=中断 上限ターン=3
台詞: 条件=ターン>=2 話者=シャー 文=もうちょっとや！
中断時: 次=evacuation_after_play
[/戦闘]

[イベント opening_battle]
[戦闘: opening_battle]
[/イベント]
