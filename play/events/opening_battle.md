---
engine: name-name
title: お遊戯会の劇戦闘
hidden: true
---
<!-- 生成物。台帳が正本。編集しない。 暫定: 背景は採用済み TRM-02 遊戯室（正本 fields/reference/teramachi-kindergarten-playroom-trm02-adopted.webp）を worker の配信上限（1MiB）に収めるため WebP 再圧縮した複製（fields/play/）。マスクは TRM-02-mask.webp（採用画像と同寸 1672x941）。出現位置は歩ける白画素の仮の点。味方の形態は elementary を流用（幼稚園期の歩行絵が無い）。敵・味方の数値（HP・ATK・DEF・AGI）と魔法の効果（MAG-07 おにぱんち=damage 40..60、MAG-08 いたいのいたいのとんでいけ=heal 40..60、MP 0）は data.md の仮値。劇戦闘への最強級の固定付与は具体が未決なので書かない -->

## opening_battle: お遊戯会の劇戦闘

[フィールドマップ 背景=fields/play/teramachi-playroom-trm02-play.webp マスク=fields/masks/TRM-02-mask.webp 戦闘背景=fields/play/bg011.webp]
[プレイヤー @700,480]
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
