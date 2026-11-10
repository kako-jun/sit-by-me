<!-- 生成物: docs/ledger/イベント/noto_water_battle.yaml が正本。仮稿・ゲームへ接続しない。未決: HP条件・10ターンでのHP調整・戦闘台詞・敵味方ID・戦後接続は仮 -->

## noto_water_battle: 水の召喚獣（仮稿）

[戦闘 noto_water_battle]
名前: 海の中
敵: S001
味方: hero
にげる: 不可
下限: 対象=hero HP=1 条件=!参戦[partner]
下限: 対象=敵全員 HP=1
台詞: 条件=開始 話者=主人公 文=つめたい……！
強制: 条件=ターン>=10 対象=hero HP=1
参戦: 条件=HP[hero]<=1 対象=partner 文=おさななじみが とびこんだ！
台詞: 条件=参戦[partner] 話者=相方 文=はなさない！
終了: 条件=参戦[partner] 結果=敗北
敗北時: 次=noto_rescue_voice
[/戦闘]

[イベント noto_water_battle]
[戦闘: noto_water_battle]
[/イベント]
