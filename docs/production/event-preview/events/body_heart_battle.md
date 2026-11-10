<!-- 生成物: docs/ledger/イベント/body_heart_battle.yaml が正本。仮稿・ゲームへ接続しない。未決: HP0後の復活条件・火の演出・台詞・接続は仮稿。player ID要照合 -->

## body_heart_battle: 心臓の水の召喚獣（仮稿）

[戦闘 body_heart_battle]
名前: 心臓の水の召喚獣
敵: S001
復活: 条件=倒れた[player] 対象=player HP=1 文=はなさない！
台詞: 条件=開始 話者=主人公 文=今度は逃げない！
台詞: 条件=ターン>=2 話者=火の召喚獣 文=立て！
[/戦闘]

[イベント body_heart_battle]
[戦闘: body_heart_battle]
[/イベント]
