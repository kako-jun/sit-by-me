---
engine: name-name
title: お遊戯会の劇戦闘
hidden: true
---
<!-- 生成物。台帳が正本。編集しない。 暫定: 背景・マスクは寺町の旧素材 TRM-07（山門の通り）を流用。本来の場所は幼稚園・遊戯室 TRM-02（採用画像は未生成）。出現位置は歩ける白画素の仮の点。味方の形態は elementary を流用（幼稚園期の歩行絵が無い）。敵・味方の数値（HP など）は data.md の仮値 -->

## opening_battle: お遊戯会の劇戦闘

[フィールドマップ 背景=fields/legacy/TRM-07.webp マスク=fields/legacy/masks/TRM-07-mask.webp]
[プレイヤー @768,512]
[トリガー auto scene=opening_battle once=true]

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
