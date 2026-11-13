---
engine: name-name
title: 共通定義
hidden: true
---
<!-- 生成物。台帳が正本。編集しない。 暫定: 数値は台帳 opening_battle の暫定を参照（HP・ATK・DEF・AGI と魔法の効果は仮値）。魔法は台帳 魔法.yaml の MAG-07・MAG-08 だけ。サンプル専用・暫定: M101・M104・M148 の HP・ATK・DEF・AGI・EXP・GOLD も仮値（M001 の仮値とは別。数値の正本は #237）。味方 C001〜C004 の経験値表・成長も暫定値（生存者への等分で3〜4戦で Lv2） -->

## data: 共通定義

[人物の形態 目録=field/sit-character-forms.json 素材=characters]
[歩行絵 主人公 人物=C001 形態=elementary]
[操作画像 手=ui/hand-cursor-v1.webp 選択マーク=ui/select-mark-cone-v1.webp]
[通貨名: 円]
[メニュー: item, magic, equip, appstore, magicite, job, status, save, config]

[モンスター M001]
名前: 段ボールのドラゴン
HP: 9999
ATK: 10
DEF: 0
AGI: 5
スプライト: enemies/M001.webp
[/モンスター]

[モンスター M101]
名前: ロードローラー
HP: 90
ATK: 14
DEF: 0
AGI: 3
EXP: 12
GOLD: 30
サイズ: 2x1
スプライト: enemies/M101.webp
[/モンスター]

[モンスター M104]
名前: 乱暴な自転車
HP: 50
ATK: 10
DEF: 0
AGI: 9
EXP: 8
GOLD: 15
サイズ: 2x1
スプライト: enemies/M104.webp
[/モンスター]

[モンスター M148]
名前: 凍った水たまり
HP: 70
ATK: 8
DEF: 0
AGI: 5
EXP: 10
GOLD: 20
サイズ: 2x1
スプライト: enemies/M148.webp
[/モンスター]

[呪文 MAG-07]
名前: おにぱんち
MP: 0
対象: 敵単体
効果: damage 40..60
[/呪文]

[呪文 MAG-08]
名前: いたいのいたいのとんでいけ
MP: 0
対象: 味方単体
効果: heal 40..60
[/呪文]

[パーティ C001]
名前: オットン
HP: 100
MP: 0
ATK: 20
DEF: 5
AGI: 10
習得: Lv1 MAG-07
習得: Lv1 MAG-08
経験値表: 8, 20, 40, 80
成長: hp+10, atk+2, def+1, agi+1
人物: C001
形態: elementary
[/パーティ]

[パーティ C002]
名前: ナム
HP: 100
MP: 0
ATK: 20
DEF: 5
AGI: 10
習得: Lv1 MAG-07
習得: Lv1 MAG-08
経験値表: 8, 20, 40, 80
成長: hp+10, atk+2, def+1, agi+1
人物: C002
形態: elementary
[/パーティ]

[パーティ C003]
名前: シャー
HP: 100
MP: 0
ATK: 20
DEF: 5
AGI: 10
習得: Lv1 MAG-07
習得: Lv1 MAG-08
経験値表: 8, 20, 40, 80
成長: hp+10, atk+2, def+1, agi+1
人物: C003
形態: elementary
[/パーティ]

[パーティ C004]
名前: ペー子
HP: 100
MP: 0
ATK: 20
DEF: 5
AGI: 10
習得: Lv1 MAG-07
習得: Lv1 MAG-08
経験値表: 8, 20, 40, 80
成長: hp+10, atk+2, def+1, agi+1
人物: C004
形態: elementary
[/パーティ]
