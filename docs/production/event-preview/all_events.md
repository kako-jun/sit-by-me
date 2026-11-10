<!-- 生成物: イベント台帳の通読用仮稿。手編集しない。 -->
# シナリオ通読用の仮稿

全121イベント。台帳から生成した人間のレビュー用であり、ゲーム実行用ではありません。
時代・表示順による仮の時系列です。会話、演出、設定上未決の展開は全て仮稿です。

## ERA-01 / お遊戯会の劇戦闘

ID: `opening_battle` ／ 状態: blocked ／ [正本](../../ledger/イベント/opening_battle.yaml) ／ [個別md](events/opening_battle.md)

目的: 4人の想像上の強さを操作し、地震による劇の中断を体験する（目的は案）。

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

## ERA-01 / 地震と避難

ID: `evacuation_after_play` ／ 状態: blocked ／ [正本](../../ledger/イベント/evacuation_after_play.yaml) ／ [個別md](events/evacuation_after_play.md)

目的: 地震で劇が中断され運動場へ避難する

[イベント evacuation_after_play]
> ゆれが おさまった。

**園長先生**:
みんな、そとへ。

**相方**:
みんな、いる？

**シャー**:
おるで。ペー子は？

**ペー子**:
ここにいます。

**主人公**:
行こう。
[/イベント]

## ERA-01 / 中止になった劇と約束

ID: `play_cancelled_promise` ／ 状態: blocked ／ [正本](../../ledger/イベント/play_cancelled_promise.yaml) ／ [個別md](events/play_cancelled_promise.md)

目的: 劇の中止から4人の約束までを描く

[イベント play_cancelled_promise]
**相方**:
もう、おしまいだって。

**相方**:
いっぱい れんしゅうしたのに。

> 相方は、泣きながらうつむいた。

**主人公**:
うまかったよ。みんな。

**相方**:
でも、さいごまでやりたかった。

**主人公**:
うん。やりたかった。

**シャー**:
ドラゴン、こわがっとったで。

**ペー子**:
またできます。かくりつは100%です。

**主人公**:
ぱーせんとって、なに？

**ペー子**:
ぜったい、ということです。

**相方**:
……ぜったい？

**ペー子**:
はい。きっと。

**シャー**:
さいきん、じしん多いな。

**主人公**:
もう、ゆれないかな。

**相方**:
……ねえ。また四人で遊ぼうよ。

**相方**:
卯辰山に ゆうえんちがあるんだって。

**主人公**:
山の上に？

**相方**:
うん。のりものがあるって。

**主人公**:
行こうよ。四人で。

**シャー**:
おれは、親が……。

**シャー**:
いや、うん。行こう。

**ペー子**:
やくそくですね。
[/イベント]

## ERA-01 / シャーの虫図鑑

ID: `kindergarten_insect_book` ／ 状態: blocked・仮稿 ／ [正本](../../ledger/イベント/kindergarten_insect_book.yaml) ／ [個別md](events/kindergarten_insect_book.md)

目的: シャーの虫好きと、ほかの子との反応の違いを描く

[イベント kindergarten_insect_book]
**シャー**:
なあ、見てみ！

**相方**:
うわっ、虫！？

**シャー**:
図鑑やって。こっちは蝶やで。

**ペー子**:
きれいな色ですね。

**シャー**:
せやろ！　羽が青いやつもおるんや。

**主人公**:
そんなに知ってるのか。

**シャー**:
まだまだおるで。ほら！
[/イベント]

## ERA-01 / 四人のビー玉

ID: `kindergarten_marble` ／ 状態: blocked ／ [正本](../../ledger/イベント/kindergarten_marble.yaml) ／ [個別md](events/kindergarten_marble.md)

目的: 四人で分けたビー玉を印象に残す

[イベント kindergarten_marble]
> 色のちがうビー玉が、四つ。

**相方**:
ひとつずつね。

**シャー**:
ちっちゃいな。

**ペー子**:
なくさないでください。

**主人公**:
みんな、おそろいだ。

**相方**:
うん。ずっと持ってよう。
[/イベント]

## ERA-01 / 香林坊へ

ID: `depart_korinbo` ／ 状態: blocked ／ [正本](../../ledger/イベント/depart_korinbo.yaml) ／ [個別md](events/depart_korinbo.md)

目的: 別れた後に大人と香林坊へ移動する

[イベント depart_korinbo]
**相方**:
またね！

**シャー**:
ほな、またな。

**ペー子**:
また明日。

**大人**:
さあ、行こうか。

**主人公**:
うん。

> 大きな手を見上げた。
[/イベント]

## ERA-01 / 売り場で刀とスマホ

ID: `korinbo_toy_shop` ／ 状態: blocked ／ [正本](../../ledger/イベント/korinbo_toy_shop.yaml) ／ [個別md](events/korinbo_toy_shop.md)

目的: スマホと最初の刀の選択に繋げる

[イベント korinbo_toy_shop]
**相方**:
あっ、来てたんだ！

**主人公**:
みんなも買いに来たの？

**シャー**:
そうや。さっき、そこで会うた。

**店員**:
スマホはこちらです。

**店員**:
刀は、一人一本。好きなのを選んでね。

**主人公**:
どれにしよう。

**相方**:
わたし、これ！

**店員**:
刀があれば、わざを使えるよ。

**シャー**:
ほな、ためしてみよか。
[/イベント]

## ERA-01 / お子様ランチ

ID: `korinbo_lunch` ／ 状態: blocked ／ [正本](../../ledger/イベント/korinbo_lunch.yaml) ／ [個別md](events/korinbo_lunch.md)

目的: 四人の日常と食事の時間を描く

[イベント korinbo_lunch]
**相方**:
旗が立ってる！

**シャー**:
最後に食べるんや。

**主人公**:
旗は食べないよ。

**シャー**:
わかっとるわ！

**ペー子**:
ゼリーは最後にします。

**相方**:
じゃあ、よーいどん。

**主人公**:
何のきょうそう？
[/イベント]

## ERA-01 / 帰り道の冒険

ID: `korinbo_return_route` ／ 状態: blocked ／ [正本](../../ledger/イベント/korinbo_return_route.yaml) ／ [個別md](events/korinbo_return_route.md)

目的: スマホを買った後に寺町への探索を始める

[イベント korinbo_return_route]
**相方**:
帰り道、こっち行ってみよう。

**主人公**:
知らない道だよ。

**シャー**:
スマホも刀もあるやろ。

**ペー子**:
みんなで行きましょう。

**主人公**:
よし、行こう。
[/イベント]

## ERA-01 / カッペボーイとの初戦

ID: `cappaboy_first_encounter` ／ 状態: blocked・仮稿 ／ [正本](../../ledger/イベント/cappaboy_first_encounter.yaml) ／ [個別md](events/cappaboy_first_encounter.md)

目的: 敵として現れるカッペボーイの負けず嫌いと、仲間に加わりたい気持ちを隠す姿を見せる

[戦闘 cappaboy_first_battle]
名前: カッペボーイ
敵: M031
台詞: 条件=開始 話者=カッペボーイ 文=かかってこい！
[/戦闘]

[イベント cappaboy_first_encounter]
> 道の先に、段ボールのお面が見えた。

**カッペボーイ**:
待て！　ここは通さねえべ！

**相方**:
だれ！？

**カッペボーイ**:
オラに勝ったら通してやるべ！

**シャー**:
なんやそれ。いくで！

[戦闘: cappaboy_first_battle]

**カッペボーイ**:
……きょうはこのくらいにしとくべ！

**主人公**:
次も勝つからな。

**カッペボーイ**:
つぎはオラが勝つべ！
[/イベント]

## ERA-01 / 銭湯で会う

ID: `bathhouse_first_meeting` ／ 状態: blocked ／ [正本](../../ledger/イベント/bathhouse_first_meeting.yaml) ／ [個別md](events/bathhouse_first_meeting.md)

目的: 日常の中で相手を異性として意識する

[イベント bathhouse_first_meeting]
> 別の日。湯の音がする。向こうは湯気で見えない。

**相方**:
あれ？　ここにいたの？

**主人公**:
えっ。なんで？

**相方**:
銭湯のおふろが、こわれたんだって。

**主人公**:
……そうなんだ。

**相方**:
ようちえんでも、おふろでも会うね。

**主人公**:
う、うん。
[/イベント]

## ERA-02 / 奥能登鉄道の車内

ID: `noto_train` ／ 状態: blocked ／ [正本](../../ledger/イベント/noto_train.yaml) ／ [個別md](events/noto_train.md)

目的: 能登旅行の期待を描く

[イベント noto_train]
**ペー子**:
もうすぐ海が見えます。

**相方**:
どっち？　どっち？

**シャー**:
まだ山ばっかりやで。

**主人公**:
あ、あそこ！

**ペー子**:
あれが能登の海です。

**相方**:
大きい！
[/イベント]

## ERA-02 / 能登に到着

ID: `noto_arrival` ／ 状態: blocked ／ [正本](../../ledger/イベント/noto_arrival.yaml) ／ [個別md](events/noto_arrival.md)

目的: 親の招待と旅行先への到着

[イベント noto_arrival]
**ペー子の親**:
よう来たね。おいで。

**ペー子**:
こちらです。

**シャー**:
駅、ちっちゃいな。

**相方**:
海も近いね！

**主人公**:
はやく行こう。
[/イベント]

## ERA-02 / 釣りへの誘い

ID: `noto_fishing_invitation` ／ 状態: blocked ／ [正本](../../ledger/イベント/noto_fishing_invitation.yaml) ／ [個別md](events/noto_fishing_invitation.md)

目的: ペー子が能登を見せたい気持ちを描く

[イベント noto_fishing_invitation]
**ペー子**:
海で釣りをしませんか。

**主人公**:
こんなに寒いのに？

**ペー子**:
冬は大きな魚も釣れます。

**相方**:
行こう！　大きいやつ！

**シャー**:
大きさなら負けへんで。

**ペー子**:
能登の海を見てほしいんです。
[/イベント]

## ERA-02 / 冬の釣り場

ID: `noto_fishing` ／ 状態: blocked ／ [正本](../../ledger/イベント/noto_fishing.yaml) ／ [個別md](events/noto_fishing.md)

目的: 主人公が離れた場所で大物に引かれて落水

[イベント noto_fishing]
**相方**:
釣れた？

**主人公**:
まだ。あっちでもやってみる。

**シャー**:
負けへんからな！

> 糸が、ぐいと引かれた。

**主人公**:
来た！　大きい！

> 竿がぐいと引かれ、体ごと海へ引っ張られた。

**主人公**:
あっ……！
[/イベント]

## ERA-02 / 水の召喚獣

ID: `noto_water_battle` ／ 状態: blocked ／ [正本](../../ledger/イベント/noto_water_battle.yaml) ／ [個別md](events/noto_water_battle.md)

目的: 落水した主人公の負け戦と相手の参戦

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

## ERA-02 / 搬送中の声

ID: `noto_rescue_voice` ／ 状態: blocked ／ [正本](../../ledger/イベント/noto_rescue_voice.yaml) ／ [個別md](events/noto_rescue_voice.md)

目的: 暗転中の搬送を声だけで示す

[イベント noto_rescue_voice]
> 声が、遠くに聞こえる。

**大人**:
こっちだ。急いで。

**大人**:
もうすぐ着くからね。

**相方**:
……ごめんね。

> 声が、聞こえなくなった。
[/イベント]

## ERA-02 / 車椅子で帰る

ID: `first_wheelchair` ／ 状態: blocked ／ [正本](../../ledger/イベント/first_wheelchair.yaml) ／ [個別md](events/first_wheelchair.md)

目的: 生活への戻り始めと友人たちとの距離を描く

[イベント first_wheelchair]
**シャー**:
おかえり。

**ペー子**:
待っていました。

**主人公**:
みんな、来てたのか。

**相方**:
帰ろう。一緒に。

**主人公**:
……先に行ってていいよ。

**シャー**:
なんでや。帰る道、おんなじやろ。

**主人公**:
そっか。
[/イベント]

## ERA-02 / 団地への坂

ID: `return_home_slope` ／ 状態: blocked ／ [正本](../../ledger/イベント/return_home_slope.yaml) ／ [個別md](events/return_home_slope.md)

目的: 車椅子になった後の帰り道を描く

[イベント return_home_slope]
**主人公**:
ここ、階段だった。

**相方**:
ゆるい坂もあるよ。

**主人公**:
遠回りだな。

**相方**:
うん。いっしょに行こう。

**主人公**:
……うん。
[/イベント]

## ERA-02 / 帰ってきた部屋

ID: `noto_hospital_waking` ／ 状態: blocked ／ [正本](../../ledger/イベント/noto_hospital_waking.yaml) ／ [個別md](events/noto_hospital_waking.md)

目的: 退院後、自分の部屋へ戻る

[イベント noto_hospital_waking]
> 時が過ぎ、家に戻った。

**主人公**:
……帰ってきた。

**相方**:
うん。また明日、会おうね。

**主人公**:
そっか。
[/イベント]

## ERA-02 / 帰ってから

ID: `hospital_missing_leg` ／ 状態: blocked ／ [正本](../../ledger/イベント/hospital_missing_leg.yaml) ／ [個別md](events/hospital_missing_leg.md)

目的: 退院後、二人がこれからの不安を言葉にする

[イベント hospital_missing_leg]
**主人公**:
この足じゃ、もう走れないのかな。

**相方**:
……どうだろう。

**主人公**:
前みたいに、みんなと。

**相方**:
……わからない。

**主人公**:
あの山も、行けない？

**相方**:
今は、わからない。

**主人公**:
そっか。

**相方**:
でも、また会いに来るよ。

**主人公**:
……うん。
[/イベント]

## ERA-03 / 廃遊園地への誘い

ID: `sunnyland_invitation` ／ 状態: blocked ／ [正本](../../ledger/イベント/sunnyland_invitation.yaml) ／ [個別md](events/sunnyland_invitation.md)

目的: 閉じた遊園地への探検を持ちかける

[イベント sunnyland_invitation]
**相方**:
卯辰山、行かない？

**主人公**:
もう遊園地じゃないだろ。

**相方**:
探検ならできるよ。

**主人公**:
無理だよ、この足で。

**相方**:
じゃあ、わたしが押す。

**主人公**:
……そこまで言うなら。
[/イベント]

## ERA-03 / 卯辰山の道

ID: `utatsuyama_ascent` ／ 状態: blocked ／ [正本](../../ledger/イベント/utatsuyama_ascent.yaml) ／ [個別md](events/utatsuyama_ascent.md)

目的: 山を進む中で遊園地を目指す

[イベント utatsuyama_ascent]
**主人公**:
坂、まだ続くな。

**相方**:
休みながら行こう。

**主人公**:
道、わかる？

**相方**:
たぶん、こっち。

**主人公**:
たぶんかよ。

**相方**:
足あと、あるでしょ。

**主人公**:
……それ、さっきの足あとだ。
[/イベント]

## ERA-03 / 凍った森との戦い

ID: `ice_summon_battle` ／ 状態: blocked ／ [正本](../../ledger/イベント/ice_summon_battle.yaml) ／ [個別md](events/ice_summon_battle.md)

目的: 氷の召喚獣との戦いを描く

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

## ERA-03 / 氷の召喚獣

ID: `ice_summon_after` ／ 状態: blocked ／ [正本](../../ledger/イベント/ice_summon_after.yaml) ／ [個別md](events/ice_summon_after.md)

目的: 戦いを越えて先へ進む

[イベント ice_summon_after]
**主人公**:
静かになった。

> 冷たい光が、手もとに残った。

**主人公**:
これ、さっきの……？

**相方**:
氷の力、かな。

**相方**:
ほら、あそこ。門が見える。

**主人公**:
……ほんとだ。

**相方**:
行こう。
[/イベント]

## ERA-03 / 崩れた入口

ID: `sunnyland_broken_entrance` ／ 状態: blocked ／ [正本](../../ledger/イベント/sunnyland_broken_entrance.yaml) ／ [個別md](events/sunnyland_broken_entrance.md)

目的: 車椅子では入りにくい入口を相方と越える

[イベント sunnyland_broken_entrance]
**主人公**:
入口、くずれてる。

> 車輪が、石の手前で止まった。

**相方**:
ここから入れるかな。

**主人公**:
ここまで来たのに。

**相方**:
押すよ。ゆっくり行こう。

**主人公**:
……頼む。
[/イベント]

## ERA-03 / シャチホコの前

ID: `sunnyland_statue` ／ 状態: blocked ／ [正本](../../ledger/イベント/sunnyland_statue.yaml) ／ [個別md](events/sunnyland_statue.md)

目的: 迷惑をかける不安と、相方の受け止めを描く

[イベント sunnyland_statue]
**主人公**:
また、止まったな。

**相方**:
急がなくていいよ。

**主人公**:
やっぱり、来なきゃよかった。

**相方**:
どうして？

**主人公**:
みんなのめいわくになる。

**主人公**:
だから、来たくなかったんだ！

**相方**:
めいわくだなんて、思ってないよ。

**主人公**:
でも、何度も止まった。

**相方**:
止まってもいいじゃない。

**相方**:
わたしが来たかったんだよ。

**相方**:
いっしょに来てくれて、うれしい。

**主人公**:
……ごめん。

> 白いシャチホコを見上げた。

**主人公**:
あれ……動いた？
[/イベント]

## ERA-03 / 白いシャチホコ

ID: `shachihoko_battle` ／ 状態: blocked ／ [正本](../../ledger/イベント/shachihoko_battle.yaml) ／ [個別md](events/shachihoko_battle.md)

目的: 主人公の不安が像に重なる戦闘

[戦闘 shachihoko_battle]
名前: 白いシャチホコ
敵: M008
台詞: 条件=開始 話者=主人公 文=さっきまで、石だった。
台詞: 条件=開始 話者=相方 文=こわくないよ。一緒だよ。
勝利時: 次=sunnyland_after_battle
[/戦闘]

[イベント shachihoko_battle]
[戦闘: shachihoko_battle]
[/イベント]

## ERA-03 / 遊園地の帰り

ID: `sunnyland_after_battle` ／ 状態: blocked ／ [正本](../../ledger/イベント/sunnyland_after_battle.yaml) ／ [個別md](events/sunnyland_after_battle.md)

目的: 我慢しなくてよいと感じる小さな前進

[イベント sunnyland_after_battle]
**主人公**:
……やっぱり、石だ。

**相方**:
うん。大きいね。

**主人公**:
また来ても、いいかな。

**相方**:
もちろん！

**主人公**:
じゃあ、今度はあっちも見よう。
[/イベント]

## ERA-03 / カッペボーイとの再戦

ID: `cappaboy_sunnyland_rematch` ／ 状態: blocked・仮稿 ／ [正本](../../ledger/イベント/cappaboy_sunnyland_rematch.yaml) ／ [個別md](events/cappaboy_sunnyland_rematch.md)

目的: 再会への喜びを強がりで隠すカッペボーイとの関係を育てる

[戦闘 cappaboy_sunnyland_battle]
名前: カッペボーイ
敵: M031
台詞: 条件=開始 話者=カッペボーイ 文=こんどこそ勝つべ！
[/戦闘]

[イベント cappaboy_sunnyland_rematch]
**カッペボーイ**:
みつけたべ！

**相方**:
あっ、また会えたね！

**カッペボーイ**:
会いに来たんじゃねえ！
この前の勝負の続きだべ！

**主人公**:
まだ勝負、終わってなかったのか。

**カッペボーイ**:
オラが勝つまで終わらねえ！

[戦闘: cappaboy_sunnyland_battle]

**カッペボーイ**:
……また負けたべ。

**相方**:
次も一緒に遊ぼうよ！

**カッペボーイ**:
遊びじゃねえ！　勝負だべ！

**主人公**:
はいはい。じゃあ、またな。

**カッペボーイ**:
……またな！
[/イベント]

## ERA-04 / 校庭へ行く前

ID: `schoolyard_before_parting` ／ 状態: blocked・仮稿 ／ [正本](../../ledger/イベント/schoolyard_before_parting.yaml) ／ [個別md](events/schoolyard_before_parting.md)

目的: 相手の善意、シャーの拒み、主人公の嫉妬と自己嫌悪を決裂の前に置く

[イベント schoolyard_before_parting]
**相手**:
シャー、最近ずっと一人でしょ。
今日は一緒に帰ろうよ！

**シャー**:
ええって。用事あるし。

**相手**:
用事が終わるまで待つから！

**シャー**:
……待たんでええ。

> シャーは先に歩いていく。

**主人公**:
あいつのこと、そんなに気になるのか。

**相手**:
だって、放っておけないよ。
四人とも、大事なんだから。

**主人公**:
そうか。

> 相手が、シャーの背中を見ている。

**主人公**:
（何を言ってるんだ。心配してるだけだろ）

**相手**:
ねえ。昔みたいに、あそこで話さない？
[/イベント]

## ERA-04 / 校庭の決裂

ID: `schoolyard_parting` ／ 状態: blocked・仮稿 ／ [正本](../../ledger/イベント/schoolyard_parting.yaml) ／ [個別md](events/schoolyard_parting.md)

目的: シャーの突き放しと主人公の気づきを描く

[イベント schoolyard_parting]
> 校庭の隅で、ペー子が足を止める。三人からは見えない。

**相手**:
ここで話そう。
昔は、なんでも話したでしょ。

**シャー**:
昔はな。

**相手**:
困ってることがあるなら、
一緒に考えるよ。

**シャー**:
同情もやめてや。

**主人公**:
何かできないか。

**シャー**:
おまえには親、いてるやん。
オレには心のつながった親はおらん。

**主人公**:
……何もできない。

**シャー**:
せんでええ。忘れてくれ。

**相手**:
そんなことできないよ。
シャーのこと、大事だもん。

**シャー**:
大事？　好きなん？

**相手**:
……友達として、好きだよ。

**シャー**:
ほんなら、オレが見せて言うたら
胸、見せてくれるん？

> 平手の音がする。

**相手**:
どうして、そんなこと……。

**シャー**:
……うざいんだよ。

> 相手は涙をぬぐう。

**主人公**:
シャー、おまえ……。

**シャー**:
もう、ほっといてや。

**主人公**:
（わざと嫌われた。……何も言えなかった）
[/イベント]

## ERA-04 / 能登の地震

ID: `noto_earthquake_waiting` ／ 状態: blocked・仮稿 ／ [正本](../../ledger/イベント/noto_earthquake_waiting.yaml) ／ [個別md](events/noto_earthquake_waiting.md)

目的: 何の予兆もなく地震が起き、現地へ行けないことを描く

[イベント noto_earthquake_waiting]
> 突然、地面が揺れる。

> 揺れが収まる。スマホに能登の地震を知らせる画面が出た。

**相手**:
能登……ペー子は？

> 主人公は電話をかける。

**主人公**:
つながらない。

**相手**:
行こう。今すぐ。

**主人公**:
今行ったら、邪魔になる。

**相手**:
……待つしかないの？

**主人公**:
連絡を待とう。
[/イベント]

## ERA-04 / ペー子の帰還

ID: `peko_returns_after_quake` ／ 状態: blocked・仮稿 ／ [正本](../../ledger/イベント/peko_returns_after_quake.yaml) ／ [個別md](events/peko_returns_after_quake.md)

目的: 両親と家を失ったペー子を迎える

[イベント peko_returns_after_quake]
**ペー子**:
ただいま。

**相手**:
……おかえり。

**主人公**:
連絡、待ってた。

**ペー子**:
片づけも、お葬式も済んだの。

**ペー子**:
親が死ぬところを見たわ。

**ペー子**:
医者なのに、先に死んじゃうなんて。
笑っちゃうよね。

> 誰も笑わない。

**相手**:
ペー子……。

**主人公**:
……行けなくて、ごめん。

**ペー子**:
ううん。来なくてよかった。

**主人公**:
何もできなかった。

**ペー子**:
……二人とも、元気でよかった。
[/イベント]

## ERA-04 / 砂浜の手前

ID: `uchinada_at_sand` ／ 状態: blocked・仮稿 ／ [正本](../../ledger/イベント/uchinada_at_sand.yaml) ／ [個別md](events/uchinada_at_sand.md)

目的: 相手が自分の意思で車椅子を押す

[イベント uchinada_at_sand]
**相手**:
ペー子、先に海で待ってるって。

> 二人は、砂浜の手前まで来た。

**相手**:
押すよ。

> いつもなら、ここで頼んでいた。

**主人公**:
いい。自分で行く。

**相手**:
いやだ。私が押したいの。

**相手**:
そうしないと、
進めない気がする。

**主人公**:
押したら嫌いになるよ。

**相手**:
なれば？

> 車椅子が、砂を踏む。
[/イベント]

## ERA-04 / 海辺での別れ

ID: `uchinada_say_goodbye` ／ 状態: blocked・仮稿 ／ [正本](../../ledger/イベント/uchinada_say_goodbye.yaml) ／ [個別md](events/uchinada_say_goodbye.md)

目的: シャー不在の理由とペー子の決意

[イベント uchinada_say_goodbye]
**ペー子**:
さけばない？

**相手**:
……シャーの家、空っぽだった。

**相手**:
遠くの少年院にいるって。
だから、今日は来られなくて。

**ペー子**:
……そう。

**相手**:
私たちが、もっと早く
何かできていたら。

**ペー子**:
あなたは、もう十分です。

**主人公**:
ペー子は、これからどうする？

**ペー子**:
東京の親戚のところへ行きます。

**相手**:
また、会えるよね。

**ペー子**:
もちろん。

**ペー子**:
……どうしてこうなっちゃったんだろうね。

**主人公**:
わからない。

**ペー子**:
私は運命と戦う。

**相手**:
だったら私も。

> 波の音が、声をのみこむ。

**ペー子**:
あああああっ！
[/イベント]

## ERA-04 / 風の召喚獣

ID: `uchinada_wind_battle` ／ 状態: blocked・仮稿 ／ [正本](../../ledger/イベント/uchinada_wind_battle.yaml) ／ [個別md](events/uchinada_wind_battle.md)

目的: 叫びの後に風と戦う

[戦闘 uchinada_wind_battle]
名前: 風の召喚獣
敵: S003
台詞: 条件=開始 話者=主人公 文=この風……！
台詞: 条件=ターン>=2 話者=相手 文=負けないよ！
[/戦闘]

[イベント uchinada_wind_battle]
[戦闘: uchinada_wind_battle]
[/イベント]

## ERA-04 / 金沢駅の見送り

ID: `kanazawa_station_farewell` ／ 状態: blocked・仮稿 ／ [正本](../../ledger/イベント/kanazawa_station_farewell.yaml) ／ [個別md](events/kanazawa_station_farewell.md)

目的: ペー子を東京へ見送る

[イベント kanazawa_station_farewell]
**相手**:
着いたら、連絡して。

**ペー子**:
はい。忘れません。

**主人公**:
また会おう。

**ペー子**:
ええ。また。

> 列車の扉が閉まる。
[/イベント]

## ERA-05 / 寺の火事

ID: `temple_mochi_fire` ／ 状態: blocked・仮稿 ／ [正本](../../ledger/イベント/temple_mochi_fire.yaml) ／ [個別md](events/temple_mochi_fire.md)

目的: 進路の会話から、突然の事故へ移る

[イベント temple_mochi_fire]
**園長**:
大きくなったねえ。

**主人公**:
進路、まだ決まってません。

**相手**:
私も。父さんを一人にできないし。

> 棚に、川で一緒に拾った化石がある。

**主人公**:
まだ持ってたんだな。

**相手**:
もちろん！　割るのは、もったいないもん。

**相手**:
おもち焼いてくるね。

> しばらくしても、戻ってこない。

**園長**:
……遅いね。

> 台所から煙が上がる。

**主人公**:
待ってろ。今行く！

> 台所に、倒れた相手がいる。

**主人公**:
おい、返事をしろ！

> 火は部屋へ燃え広がり、棚の化石を包む。
[/イベント]

## ERA-05 / 火の召喚獣

ID: `temple_fire_summon` ／ 状態: blocked・仮稿 ／ [正本](../../ledger/イベント/temple_fire_summon.yaml) ／ [個別md](events/temple_fire_summon.md)

目的: 化石から現れた火を制し、火事から脱出する

[戦闘 temple_fire_summon]
名前: 火の召喚獣
敵: S004
台詞: 条件=開始 話者=主人公 文=火を止めないと！
台詞: 条件=ターン>=2 話者=主人公 文=ここは通せ！
[/戦闘]

[イベント temple_fire_summon]
[戦闘: temple_fire_summon]
[/イベント]

## ERA-05 / 火が消えたあと

ID: `temple_fire_extinguished` ／ 状態: blocked・仮稿 ／ [正本](../../ledger/イベント/temple_fire_extinguished.yaml) ／ [個別md](events/temple_fire_extinguished.md)

目的: 火の召喚獣を鎮め、避難と爆発を描く

[イベント temple_fire_extinguished]
**火の召喚獣**:
……あのときの子か。

**主人公**:
おまえ、化石の中にいたのか？

**火の召喚獣**:
話はあとだ。外へ出ろ！

> 一同が外へ逃れる。大きな音が響き、火が消える。
> 幼稚園は半壊している。
> 火の召喚獣が、外にいる主人公たちへ合流する。
[/イベント]

## ERA-05 / 火事のあと

ID: `fire_escape_wheelchair` ／ 状態: blocked・仮稿 ／ [正本](../../ledger/イベント/fire_escape_wheelchair.yaml) ／ [個別md](events/fire_escape_wheelchair.md)

目的: 冷えていく相手を車椅子に乗せ、体内へ入る

[イベント fire_escape_wheelchair]
> 主人公は車椅子を降り、相手を座らせる。

**主人公**:
ここなら、少しは楽だろ。

**園長**:
救急車を呼んだ。道で待っている。

> 園長が走り去る。

**主人公**:
冷たい……。さっきまで話してたのに。

**火の召喚獣**:
中から冷えてる。おれが入る。

**主人公**:
どうやって？

**火の召喚獣**:
キスをしろ。

**主人公**:
……ごめんなさい。

> 主人公は相手に唇を重ねる。
> 火の召喚獣の姿が、二人のあいだに消える。
[/イベント]

## ERA-05 / 体内への入口

ID: `body_mouth_entry` ／ 状態: blocked・仮稿 ／ [正本](../../ledger/イベント/body_mouth_entry.yaml) ／ [個別md](events/body_mouth_entry.md)

目的: 主人公と火の召喚獣が相手を助けに入る

[イベント body_mouth_entry]
**主人公**:
ここが……あいつの中？

**火の召喚獣**:
急ぐぞ。心臓が弱ってる。

**主人公**:
まっすぐ行けないのか。

**火の召喚獣**:
先に、冷えを追い払う。
[/イベント]

## ERA-05 / 右手の回想

ID: `body_right_hand_memory` ／ 状態: blocked・仮稿 ／ [正本](../../ledger/イベント/body_right_hand_memory.yaml) ／ [個別md](events/body_right_hand_memory.md)

目的: 握っていたもの

[イベント body_right_hand_memory]
> 手を強く握られる。

**同級生の声**:
痛い？　ごめん。

**相手の声**:
平気！　離さなくていいよ。

> 手が離れる。指の跡が残っている。

**主人公**:
……痛かったんじゃないか。
[/イベント]

## ERA-05 / 右手の中ボス

ID: `body_right_hand_battle` ／ 状態: blocked・仮稿 ／ [正本](../../ledger/イベント/body_right_hand_battle.yaml) ／ [個別md](events/body_right_hand_battle.md)

目的: 右手の障害を越える

[戦闘 body_right_hand_battle]
名前: 右手の中ボス
敵: unresolved_body_right_hand
台詞: 条件=開始 話者=主人公 文=その手を離せ！
台詞: 条件=ターン>=2 話者=火の召喚獣 文=まだ冷たいぞ！
[/戦闘]

[イベント body_right_hand_battle]
[戦闘: body_right_hand_battle]
[/イベント]

## ERA-05 / 右手の戦闘後

ID: `body_right_hand_after` ／ 状態: blocked・仮稿 ／ [正本](../../ledger/イベント/body_right_hand_after.yaml) ／ [個別md](events/body_right_hand_after.md)

目的: 部位の冷えが和らぐ

[イベント body_right_hand_after]
**火の召喚獣**:
冷たかった手が、少し戻った。

**主人公**:
痛くても、言えなかったんだな。

**火の召喚獣**:
まだ間に合う。行くぞ。
[/イベント]

## ERA-05 / 左手の回想

ID: `body_left_hand_memory` ／ 状態: blocked・仮稿 ／ [正本](../../ledger/イベント/body_left_hand_memory.yaml) ／ [個別md](events/body_left_hand_memory.md)

目的: 差し伸べた手

[イベント body_left_hand_memory]
**同級生の声**:
これも持ってくれる？

**相手の声**:
うん、任せて！

> 荷物が重なり、差し出す手がふさがる。

**主人公**:
助けてって、言えばいいのに。

**火の召喚獣**:
言えなかったんだろ。
[/イベント]

## ERA-05 / 左手の中ボス

ID: `body_left_hand_battle` ／ 状態: blocked・仮稿 ／ [正本](../../ledger/イベント/body_left_hand_battle.yaml) ／ [個別md](events/body_left_hand_battle.md)

目的: 左手の障害を越える

[戦闘 body_left_hand_battle]
名前: 左手の中ボス
敵: unresolved_body_left_hand
台詞: 条件=開始 話者=主人公 文=今度は手を貸す。
台詞: 条件=ターン>=2 話者=火の召喚獣 文=前を見ろ！
[/戦闘]

[イベント body_left_hand_battle]
[戦闘: body_left_hand_battle]
[/イベント]

## ERA-05 / 左手の戦闘後

ID: `body_left_hand_after` ／ 状態: blocked・仮稿 ／ [正本](../../ledger/イベント/body_left_hand_after.yaml) ／ [個別md](events/body_left_hand_after.md)

目的: 部位の冷えが和らぐ

[イベント body_left_hand_after]
**主人公**:
自分から、断れなかったのか。

**火の召喚獣**:
わかるのは、戻ってからだ。

**主人公**:
……そうだな。
[/イベント]

## ERA-05 / 右足の回想

ID: `body_right_leg_memory` ／ 状態: blocked・仮稿 ／ [正本](../../ledger/イベント/body_right_leg_memory.yaml) ／ [個別md](events/body_right_leg_memory.md)

目的: 歩幅と待つこと

[イベント body_right_leg_memory]
> みんなの足音が遠ざかる。

**同級生の声**:
早くしないと置いてくよ！

**相手の声**:
すぐ行く！　先に行ってて！

> 足音がひとつ、遅れて走り出す。

**主人公**:
あいつ、追いかけたのか。
[/イベント]

## ERA-05 / 右足の中ボス

ID: `body_right_leg_battle` ／ 状態: blocked・仮稿 ／ [正本](../../ledger/イベント/body_right_leg_battle.yaml) ／ [個別md](events/body_right_leg_battle.md)

目的: 右足の障害を越える

[戦闘 body_right_leg_battle]
名前: 右足の中ボス
敵: unresolved_body_right_leg
台詞: 条件=開始 話者=主人公 文=待ってろ。今行く。
台詞: 条件=ターン>=2 話者=火の召喚獣 文=足を止めるな！
[/戦闘]

[イベント body_right_leg_battle]
[戦闘: body_right_leg_battle]
[/イベント]

## ERA-05 / 右足の戦闘後

ID: `body_right_leg_after` ／ 状態: blocked・仮稿 ／ [正本](../../ledger/イベント/body_right_leg_after.yaml) ／ [個別md](events/body_right_leg_after.md)

目的: 部位の冷えが和らぐ

[イベント body_right_leg_after]
**主人公**:
置いていかれても、追いかけたんだな。

**火の召喚獣**:
今は止まるな。

**主人公**:
ああ。次へ行こう。
[/イベント]

## ERA-05 / 左足の回想

ID: `body_left_leg_memory` ／ 状態: blocked・仮稿 ／ [正本](../../ledger/イベント/body_left_leg_memory.yaml) ／ [個別md](events/body_left_leg_memory.md)

目的: 足踏みと我慢

[イベント body_left_leg_memory]
**同級生の声**:
もう一回、走れる？

**相手の声**:
大丈夫！　まだ走れるよ！

> 足が前へ出ない。

**主人公**:
もうやめろ。休めよ。

**火の召喚獣**:
声は届かない。思い出だ。
[/イベント]

## ERA-05 / 左足の中ボス

ID: `body_left_leg_battle` ／ 状態: blocked・仮稿 ／ [正本](../../ledger/イベント/body_left_leg_battle.yaml) ／ [個別md](events/body_left_leg_battle.md)

目的: 左足の障害を越える

[戦闘 body_left_leg_battle]
名前: 左足の中ボス
敵: unresolved_body_left_leg
台詞: 条件=開始 話者=主人公 文=もう無理しなくていい。
台詞: 条件=ターン>=2 話者=火の召喚獣 文=こっちは任せろ！
[/戦闘]

[イベント body_left_leg_battle]
[戦闘: body_left_leg_battle]
[/イベント]

## ERA-05 / 左足の戦闘後

ID: `body_left_leg_after` ／ 状態: blocked・仮稿 ／ [正本](../../ledger/イベント/body_left_leg_after.yaml) ／ [個別md](events/body_left_leg_after.md)

目的: 部位の冷えが和らぐ

[イベント body_left_leg_after]
**主人公**:
大丈夫って、ずっと言ってたな。

**火の召喚獣**:
体は、そう言っていない。

**主人公**:
早く温めよう。
[/イベント]

## ERA-05 / 頭の回想

ID: `body_head_memory` ／ 状態: blocked・仮稿 ／ [正本](../../ledger/イベント/body_head_memory.yaml) ／ [個別md](events/body_head_memory.md)

目的: 相手の表に出なかった思いに触れる

[イベント body_head_memory]
**相手の声**:
笑っていれば、平気だと思った。

**相手の声**:
誰にも言えなかった。

**主人公**:
……知らなかった。

**火の召喚獣**:
来る。ここの体が、おまえを拒んでる。
[/イベント]

## ERA-05 / 頭の中ボス

ID: `body_head_battle` ／ 状態: blocked・仮稿 ／ [正本](../../ledger/イベント/body_head_battle.yaml) ／ [個別md](events/body_head_battle.md)

目的: 体内の異物として免疫に迎え撃たれる

[戦闘 body_head_battle]
名前: 頭の中ボス
敵: M012
台詞: 条件=開始 話者=主人公 文=通してくれ！
台詞: 条件=ターン>=2 話者=火の召喚獣 文=ためらうな！
[/戦闘]

[イベント body_head_battle]
[戦闘: body_head_battle]
[/イベント]

## ERA-05 / 頭の戦闘後

ID: `body_head_after` ／ 状態: blocked・仮稿 ／ [正本](../../ledger/イベント/body_head_after.yaml) ／ [個別md](events/body_head_after.md)

目的: 相手の本心を知った主人公が進む

[イベント body_head_after]
**主人公**:
あいつも、苦しかったんだな。

**火の召喚獣**:
本人に聞け。帰ってからな。
[/イベント]

## ERA-05 / 胃の異物

ID: `body_stomach_entry` ／ 状態: blocked・仮稿 ／ [正本](../../ledger/イベント/body_stomach_entry.yaml) ／ [個別md](events/body_stomach_entry.md)

目的: 逃げる小さな影と、それを守る敵に遭遇する

[イベント body_stomach_entry]
**主人公**:
あれは……？

**火の召喚獣**:
小さいが、嫌な気配だ。

> 小さな影の前に、大きな影が立つ。

**主人公**:
守ってるのか。
[/イベント]

## ERA-05 / 胃の盾とエラー細胞

ID: `body_stomach_battle` ／ 状態: blocked・仮稿 ／ [正本](../../ledger/イベント/body_stomach_battle.yaml) ／ [個別md](events/body_stomach_battle.md)

目的: 盾役を越えるが、エラー細胞は逃れる

[戦闘 body_stomach_battle]
名前: 胃の盾とエラー細胞
敵: M010+M009
下限: 対象=M009 HP=1
逃走: 条件=倒れた[M010] 対象=M009 文=小さな影が逃げた！
台詞: 条件=開始 話者=主人公 文=後ろに何かいる！
台詞: 条件=ターン>=2 話者=火の召喚獣 文=逃がすな！
[/戦闘]

[イベント body_stomach_battle]
[戦闘: body_stomach_battle]
[/イベント]

## ERA-05 / 胃の戦闘後

ID: `body_stomach_after` ／ 状態: blocked・仮稿 ／ [正本](../../ledger/イベント/body_stomach_after.yaml) ／ [個別md](events/body_stomach_after.md)

目的: 小さな影を逃したことを残す

[イベント body_stomach_after]
> 小さな影が、すき間へ消えた。

**主人公**:
逃げた……。

**火の召喚獣**:
追えない。今は心臓だ。
[/イベント]

## ERA-05 / 心臓へ

ID: `body_heart_entry` ／ 状態: blocked・仮稿 ／ [正本](../../ledger/イベント/body_heart_entry.yaml) ／ [個別md](events/body_heart_entry.md)

目的: 相手が守ってきた水への恐怖と向き合う

[イベント body_heart_entry]
> かすかな鼓動が聞こえる。

**主人公**:
……また、おまえか。

**火の召喚獣**:
知ってるのか。

**主人公**:
あの日、海にいた。

**主人公**:
あいつが、ずっと抱えてたのか。

> 冷たい水が、足元へ寄せる。

**主人公**:
あのとき、手を離さなかった。

**主人公**:
……今度は、こっちの番だ。
[/イベント]

## ERA-05 / 心臓の水の召喚獣

ID: `body_heart_battle` ／ 状態: blocked・仮稿 ／ [正本](../../ledger/イベント/body_heart_battle.yaml) ／ [個別md](events/body_heart_battle.md)

目的: HP0から復活して水に挑む

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

## ERA-05 / 救急車の前で

ID: `ambulance_after_body` ／ 状態: blocked・仮稿 ／ [正本](../../ledger/イベント/ambulance_after_body.yaml) ／ [個別md](events/ambulance_after_body.md)

目的: 相手が目覚め、二人が後で話す約束をする

[イベント ambulance_after_body]
> 救急車は、すでに来ていた。
> 相手が車椅子の上で目を開ける。

**相手**:
……あれ。どうして、ここに？

> 相手はストレッチャーに移される。
> 主人公は車椅子に戻る。園長が救急車に乗り込む。

**主人公**:
元気になって。伝えたいことがある。

**相手**:
わたしも！

> 扉が閉まり、救急車が走り去る。
> 車椅子は救急車に載せられず、主人公は見送る。
[/イベント]

## ERA-05 / 園庭への寄り道

ID: `kindergarten_evening_revisit` ／ 状態: blocked・仮稿 ／ [正本](../../ledger/イベント/kindergarten_evening_revisit.yaml) ／ [個別md](events/kindergarten_evening_revisit.md)

目的: 疎遠になった二人が、昔の距離を取り戻し始める

[イベント kindergarten_evening_revisit]
> 銭湯の帰り、二人は幼稚園の前で足を止める。
**相手**:
不法侵入だよ。

**主人公**:
OBだからいいの。知らなかった？

**相手**:
そんな決まり、あるわけないでしょ。

**相手**:
教室も見てく？

**主人公**:
……天井、こんなに低かったんだな。
[/イベント]

## ERA-05 / 能登の仕事

ID: `noto_recovery_work` ／ 状態: blocked・仮稿 ／ [正本](../../ledger/イベント/noto_recovery_work.yaml) ／ [個別md](events/noto_recovery_work.md)

目的: 青年になった主人公が復興に関わる

[イベント noto_recovery_work]
**主人公**:
ここなら、できる仕事がある。

**火の召喚獣**:
旅費のためか。

**主人公**:
ああ。それだけじゃない。

**火の召喚獣**:
……手伝うぞ。
[/イベント]

## ERA-05 / ペー子の帰郷

ID: `peko_reunion_message` ／ 状態: blocked・仮稿 ／ [正本](../../ledger/イベント/peko_reunion_message.yaml) ／ [個別md](events/peko_reunion_message.md)

目的: 久しぶりの再会とシャーからの短い連絡

[イベント peko_reunion_message]
> 主人公は能登から金沢に戻り、久しぶりに相手と会う。

**相手**:
おかえり。能登の仕事、どう？

**主人公**:
まだ途中だよ。

**ペー子**:
ただいま。

**主人公**:
……ペー子？

**ペー子**:
驚きました？
金沢の病院で研修することになったの。

> 久しぶりに見るペー子から、主人公は目をそらす。

**主人公**:
……変わったな。

**ペー子**:
あなたも。

**相手**:
帰ってくるなら言ってよ。

**ペー子**:
驚かせたかったから。

**ペー子**:
それと……シャーから連絡が来たの。

**主人公**:
シャーが？

**ペー子**:
海外にいるって。連れ去られて、
悪いことを手伝わされているみたい。

**主人公**:
なんでペー子に？

**ペー子**:
べ、別にいいでしょ！

**相手**:
どこにいるかわかる？

**ペー子**:
短い文だけ。間違いも多くて。
見える文字を送ったみたいだけど……。

**ペー子**:
あら。その子、誰？

**主人公**:
見えるのか？

**火の召喚獣**:
見えるなら話が早い。

**主人公**:
……見えるんだな。
[/イベント]

## ERA-05 / 渡航費とビー玉

ID: `marbles_and_fare` ／ 状態: blocked・仮稿 ／ [正本](../../ledger/イベント/marbles_and_fare.yaml) ／ [個別md](events/marbles_and_fare.md)

目的: 手がかりを考え、働いて渡航費を貯める

[イベント marbles_and_fare]
**ペー子**:
この文字を手がかりに、調べてみます。

**相手**:
建物から見える看板かもしれないね。

**主人公**:
シャーは、外を見られるところにいるのか。

**ペー子**:
それも、まだわかりません。

**相手**:
見つけよう。迎えに行きたい！

**主人公**:
場所がわかっても、遠いな。

**ペー子**:
私、お金ありません。貧乏なめないで。

**相手**:
うちも修繕中だよ。

**主人公**:
じゃあ、働こう。

**ペー子**:
その前にお願い。ビー玉を探して。

**相手**:
四人の？

**ペー子**:
ええ。それぞれ、荷物に入れて。
[/イベント]

## ERA-05 / K空港から出発

ID: `airport_departure` ／ 状態: blocked・仮稿 ／ [正本](../../ledger/イベント/airport_departure.yaml) ／ [個別md](events/airport_departure.md)

目的: 友人を迎えに海外へ向かう

[イベント airport_departure]
**相手**:
忘れ物、ない？

**主人公**:
ビー玉ならある。

**ペー子**:
私も。行きましょう。
[/イベント]

## ERA-05 / 海外の街へ

ID: `overseas_city_arrival` ／ 状態: blocked・仮稿 ／ [正本](../../ledger/イベント/overseas_city_arrival.yaml) ／ [個別md](events/overseas_city_arrival.md)

目的: 街の暮らしの中を通って塔に向かう

[イベント overseas_city_arrival]
> 窓の明かりが、細い路地を照らす。

**主人公**:
ここで暮らしてる人がいる。

**ペー子**:
ええ。探すのは、塔の中です。

**相手**:
シャーを連れて帰ろう。
[/イベント]

## ERA-05 / 左塔の中ボス

ID: `overseas_left_tower` ／ 状態: blocked・仮稿 ／ [正本](../../ledger/イベント/overseas_left_tower.yaml) ／ [個別md](events/overseas_left_tower.md)

目的: 魔法のみ有効の塔を突破する

[戦闘 overseas_left_tower]
名前: 左塔の中ボス
敵: M015
台詞: 条件=開始 話者=主人公 文=刃が通らない！
台詞: 条件=ターン>=2 話者=ペー子 文=魔法でいきます！
[/戦闘]

[イベント overseas_left_tower]
[戦闘: overseas_left_tower]
[/イベント]

## ERA-05 / 右塔の中ボス

ID: `overseas_right_tower` ／ 状態: blocked・仮稿 ／ [正本](../../ledger/イベント/overseas_right_tower.yaml) ／ [個別md](events/overseas_right_tower.md)

目的: アビリティのみ有効の塔を突破する

[戦闘 overseas_right_tower]
名前: 右塔の中ボス
敵: M016
台詞: 条件=開始 話者=相手 文=魔法が効かない！
台詞: 条件=ターン>=2 話者=主人公 文=刃なら、どうだ！
[/戦闘]

[イベント overseas_right_tower]
[戦闘: overseas_right_tower]
[/イベント]

## ERA-05 / 空中通路の再会

ID: `overseas_bridge_reunion` ／ 状態: blocked・仮稿 ／ [正本](../../ledger/イベント/overseas_bridge_reunion.yaml) ／ [個別md](events/overseas_bridge_reunion.md)

目的: 敵の中にシャーを見つける

[イベント overseas_bridge_reunion]
**相手**:
……シャー？

**シャー**:
なんで、おまえらがここに。

**ペー子**:
迎えに来ました。

**シャー**:
頼んでへん。

**主人公**:
わかってる。

**シャー**:
帰っても、オレは捕まる。
やったことは消えへん。

**相手**:
それでも、一緒に帰ろう。

**シャー**:
……勝手なやつらやな。

**主人公**:
話はあとだ。来るぞ！
[/イベント]

## ERA-05 / 空中通路の共闘

ID: `overseas_bridge_fight` ／ 状態: blocked・仮稿 ／ [正本](../../ledger/イベント/overseas_bridge_fight.yaml) ／ [個別md](events/overseas_bridge_fight.md)

目的: 四人で雑魚を退ける

[戦闘 overseas_bridge_fight]
名前: 空中通路の共闘
敵: unresolved_bridge_enemies
台詞: 条件=開始 話者=シャー 文=オレもやる！
台詞: 条件=ターン>=2 話者=相手 文=四人そろったね！
[/戦闘]

[イベント overseas_bridge_fight]
[戦闘: overseas_bridge_fight]
[/イベント]

## ERA-05 / ビー玉

ID: `overseas_marble_reveal` ／ 状態: blocked・仮稿 ／ [正本](../../ledger/イベント/overseas_marble_reveal.yaml) ／ [個別md](events/overseas_marble_reveal.md)

目的: シャーが持ち続けたビー玉を見せる

[イベント overseas_marble_reveal]
> 遠くで、近づく音がする。

**シャー**:
連中が来る。早よ出な。

**ペー子**:
覚えていますか。これ。

**シャー**:
……ビー玉。

**相手**:
言われたとおり、探してきたよ。

**主人公**:
こっちにもある。

**相手**:
みんなで、ずっと持ってようって。

> シャーがポケットを探る。
> 手の中に、小さなビー玉がある。

**シャー**:
それだけは、持ってた。

> シャーは手の中のビー玉を見つめ、泣く。

**シャー**:
なんで捨てへんかったんやろな。

**ペー子**:
なくさないでって、言いましたよね。

> シャーはビー玉を握る。

**シャー**:
……オレ、正気にもどったわ。
[/イベント]

## ERA-05 / 第三塔を下る

ID: `overseas_tower_escape` ／ 状態: blocked・仮稿 ／ [正本](../../ledger/イベント/overseas_tower_escape.yaml) ／ [個別md](events/overseas_tower_escape.md)

目的: 当局の到着前に脱出する

[イベント overseas_tower_escape]
**ペー子**:
時間がありません。下へ！

**シャー**:
ここを出るんや。急げ！

**主人公**:
置いていかない。全員で行く。
[/イベント]

## ERA-05 / 土の召喚獣

ID: `overseas_earth_summon` ／ 状態: blocked・仮稿 ／ [正本](../../ledger/イベント/overseas_earth_summon.yaml) ／ [個別md](events/overseas_earth_summon.md)

目的: 脱出直前の召喚獣を突破する

[戦闘 overseas_earth_summon]
名前: 土の召喚獣
敵: S005
台詞: 条件=開始 話者=主人公 文=出口はそこだ！
台詞: 条件=ターン>=2 話者=シャー 文=道をあけろ！
[/戦闘]

[イベント overseas_earth_summon]
[戦闘: overseas_earth_summon]
[/イベント]

## ERA-05 / 海外からの脱出

ID: `overseas_exit` ／ 状態: blocked・仮稿 ／ [正本](../../ledger/イベント/overseas_exit.yaml) ／ [個別md](events/overseas_exit.md)

目的: 四人で塔の外へ出る

[イベント overseas_exit]
**相手**:
外だ！

**ペー子**:
全員いますね？

**シャー**:
……ああ。

**主人公**:
帰ろう。
[/イベント]

## ERA-06 / 帰国後のプロポーズ

ID: `proposal_after_rescue` ／ 状態: blocked ／ [正本](../../ledger/イベント/proposal_after_rescue.yaml) ／ [個別md](events/proposal_after_rescue.md)

目的: 日常を取り戻した二人が、これからを選ぶ。

[イベント proposal_after_rescue]
**相手**:
帰ってきたね。
**主人公**:
ああ。みんなでな。
**相手**:
まだ、夢みたい。
**主人公**:
離れてる間、考えてた。
どこに帰りたいのか。
**相手**:
どこだった？
**主人公**:
おまえの隣だ。
Let me sit by you.
**相手**:
うん。ずっと、隣にいて。
[/イベント]

## ERA-06 / 結婚と家族の始まり

ID: `wedding_and_family` ／ 状態: blocked ／ [正本](../../ledger/イベント/wedding_and_family.yaml) ／ [個別md](events/wedding_and_family.md)

目的: 友人たちに見守られ、新しい生活へ進む。

[イベント wedding_and_family]
**シャー**:
おめでとう。
泣いてへんからな。
**ペー子**:
まだ何も言ってませんよ。
**相手**:
ありがとう。二人とも。
**主人公**:
これからも、頼む。
**シャー**:
そっちこそや。
[/イベント]

## ERA-07 / 家族の朝

ID: `family_morning` ／ 状態: blocked ／ [正本](../../ledger/イベント/family_morning.yaml) ／ [個別md](events/family_morning.md)

目的: 親になった二人と子供たちの暮らしを描く。

[イベント family_morning]
**ハク**:
早く行こうよ！
**ハツ**:
もう、じゅんびできた！
**相手**:
靴が、左右逆だよ。
**ハツ**:
あっ。
**主人公**:
慌てるな。まだ朝だ。
**相手**:
昔、あなたも急いでたよ。
**主人公**:
……覚えてたのか。
[/イベント]

## ERA-07 / 子供たちの小冒険

ID: `family_imaginary_adventure` ／ 状態: blocked ／ [正本](../../ledger/イベント/family_imaginary_adventure.yaml) ／ [個別md](events/family_imaginary_adventure.md)

目的: 子供たちの想像に親が付き合う。

[イベント family_imaginary_adventure]
**ハク**:
そこ、気をつけて！
敵がいる！
**ハツ**:
おおきいのが来るよ！
**主人公**:
見えた。大きいな。
**ハツ**:
でしょ！
**相手**:
あなたにも見えるんだ。
**主人公**:
ああ。任せておけ。
**ハク**:
みんな、いくよ！
[/イベント]

## ERA-07 / 小冒険の帰り道

ID: `family_adventure_after` ／ 状態: blocked ／ [正本](../../ledger/イベント/family_adventure_after.yaml) ／ [個別md](events/family_adventure_after.md)

目的: 親子の冒険の余韻を見せる。

[イベント family_adventure_after]
**ハツ**:
勝った！
**ハク**:
次はもっと強いのが出るよ。
**主人公**:
それは困るな。
**相手**:
もう疲れたの？
**主人公**:
いや。
次も、ついていく。
[/イベント]

## ERA-07 / 地震と延期された検診

ID: `m8_checkup_postponed` ／ 状態: blocked ／ [正本](../../ledger/イベント/m8_checkup_postponed.yaml) ／ [個別md](events/m8_checkup_postponed.md)

目的: 突然の地震と、検診の延期を示す。

[イベント m8_checkup_postponed]
> 地震が起きた。
**主人公**:
みんな、いるか！
**相手**:
いるよ。二人とも、ここ。
**ハク**:
こわかった……。
**相手**:
大丈夫。ここにいるよ。
> 病院から、検診の延期が伝えられた。
**主人公**:
落ち着いたら、行こう。
**相手**:
うん。そうしよう。
[/イベント]

## ERA-07 / 香林坊のレストラン

ID: `family_korinbo_lunch` ／ 状態: blocked ／ [正本](../../ledger/イベント/family_korinbo_lunch.yaml) ／ [個別md](events/family_korinbo_lunch.md)

目的: 子供時代の場所を親として訪ねる。

[イベント family_korinbo_lunch]
**ハク**:
旗が立ってる！
**ハツ**:
こっちにもある！
**相手**:
ここ、覚えてる？
**主人公**:
ああ。昔も食べた。
**相手**:
あのときは、旗が宝物だった。
**主人公**:
今もそうみたいだな。
[/イベント]

## ERA-07 / 三人目の知らせ

ID: `hospital_third_child` ／ 状態: blocked ／ [正本](../../ledger/イベント/hospital_third_child.yaml) ／ [個別md](events/hospital_third_child.md)

目的: 喜びの直後に診察室へ向かう。

[イベント hospital_third_child]
**相手**:
三人目が、できたよ。
**主人公**:
本当か？
**相手**:
うん。
**主人公**:
ハクたち、喜ぶな。
**相手**:
きっとね。
> ペー子が主人公を診察室に呼ぶ。
[/イベント]

## ERA-07 / 病院での告知

ID: `hospital_diagnosis` ／ 状態: blocked ／ [正本](../../ledger/イベント/hospital_diagnosis.yaml) ／ [個別md](events/hospital_diagnosis.md)

目的: 告知を受け、相手が一人で受け止めた時間を知る。

[イベント hospital_diagnosis]
**ペー子**:
病気が見つかりました。
**主人公**:
……治せるんだろう？
**ペー子**:
今の段階では、難しいです。
**主人公**:
本当に、助からないのか？
**ペー子**:
……はい。
> 景色から色が消え、主人公の体が浮く。
**相手**:
この子を、産みたい。
**主人公**:
……一人で、聞いたのか。
**相手**:
うん。怖かった。
でも、決めたの。
**主人公**:
……そうか。
**相手**:
これからは、一緒にいて。
**主人公**:
ああ。ずっと一緒だ。
**主人公**:
すごいな、おまえは。
> 二人が抱き合い、画面が暗くなる。
[/イベント]

## ERA-07 / 暗転後の歩み

ID: `family_memory_montage` ／ 状態: blocked ／ [正本](../../ledger/イベント/family_memory_montage.yaml) ／ [個別md](events/family_memory_montage.md)

目的: 子供と歩く画面に二人の記憶が重なる。

[イベント family_memory_montage]
> 子供たちと歩く。画面の端に、過ぎた日々が流れる。
**相手**:
あっ……！
> 銭湯の湯気。幼い二人。
**相手**:
行こう！
> 雪の坂。並んだ影。
**主人公**:
隣にいてくれ。
> 手が重なる。
> 足音だけが続く。
[/イベント]

## ERA-08 / 別れの儀式

ID: `family_funeral` ／ 状態: blocked ／ [正本](../../ledger/イベント/family_funeral.yaml) ／ [個別md](events/family_funeral.md)

目的: 日本の葬送の場を丁寧に描き、残された人を示す。

[イベント family_funeral]
> 人々が静かに手を合わせる。
**シャー**:
なんで、あいつやねん。
**主人公**:
……わからない。
**シャー**:
俺やったら、よかったのに。
**主人公**:
そんなこと、言うな。
**ペー子**:
私たちも、そばにいます。
**主人公**:
ああ。頼む。
[/イベント]

## ERA-08 / 内灘の叫び

ID: `uchinada_silent_cry` ／ 状態: blocked ／ [正本](../../ledger/イベント/uchinada_silent_cry.yaml) ／ [個別md](events/uchinada_silent_cry.md)

目的: 叫んだ内容を明かさず、子供たちのもとへ戻る。

[イベント uchinada_silent_cry]
> 冬の海。主人公の叫びを、波の音がさらう。
> ハクは赤ん坊のチュンを抱いて待っている。
**ハク**:
チュン、眠ったよ。
**ハク**:
……もういいの？
**主人公**:
もう少し、ここにいよう。
> 三人は波を見ている。
[/イベント]

## ERA-08 / 園長先生と話す

ID: `temple_principal_after_loss` ／ 状態: blocked ／ [正本](../../ledger/イベント/temple_principal_after_loss.yaml) ／ [個別md](events/temple_principal_after_loss.md)

目的: 亡き相手の親と残された家族が向き合う。

[イベント temple_principal_after_loss]
**園長先生**:
寒かっただろう。
**主人公**:
海に行ってきました。
**園長先生**:
そうか。
**主人公**:
あいつは、強かった。
**園長先生**:
ああ。昔からな。
**主人公**:
子供たちと、生きていきます。
**園長先生**:
うん。一人で抱えるなよ。
[/イベント]

## ERA-08 / 隣にいた人

ID: `spouse_summon_reunion` ／ 状態: blocked・仮稿 ／ [正本](../../ledger/イベント/spouse_summon_reunion.yaml) ／ [個別md](events/spouse_summon_reunion.md)

目的: 喪失の後に配偶者の召喚獣と出会い、共に過ごした時間を子供たちにつなぐ。

[イベント spouse_summon_reunion]
> ふと、隣に気配がする。
**主人公**:
……おまえ、なのか？
**相手**:
うん。ここにいるよ。
**主人公**:
また、会えるのか。
**相手**:
あなたが呼んでくれたらね。
**主人公**:
子供たちに、伝えていこう。
**相手**:
二人で覚えたこと、全部ね。
**主人公**:
……ああ。
> 手を伸ばす。そこには、あたたかさが残った。
[/イベント]

## ERA-08 / 子供たちと進む

ID: `children_join_journey` ／ 状態: blocked ／ [正本](../../ledger/イベント/children_join_journey.yaml) ／ [個別md](events/children_join_journey.md)

目的: 父母の時間をつなぎ、子供たちと歩き出す。

[イベント children_join_journey]
> 季節が過ぎ、チュンも歩けるようになった。
**ハク**:
行こう。みんな待ってる。
**ハツ**:
行くよ。
**チュン**:
一緒に行く。
**主人公**:
よし。離れるなよ。
**ハク**:
そっちこそね。
**主人公**:
……ああ。
[/イベント]

## ERA-08 / 大地震と厳冬

ID: `m9_cold_after_quake` ／ 状態: blocked ／ [正本](../../ledger/イベント/m9_cold_after_quake.yaml) ／ [個別md](events/m9_cold_after_quake.md)

目的: 突然の地震のあと、寒さの中で人々を助ける。

[イベント m9_cold_after_quake]
> 地震が起きた。
**主人公**:
全員、無事か！
**ハク**:
うん。こっちは大丈夫！
**ハツ**:
電気がつかない。
**チュン**:
寒いよ……。
**主人公**:
あたたかい場所へ行くぞ。
**ハク**:
みんなも呼んでくる。
**主人公**:
一緒に行こう。
[/イベント]

## ERA-08 / 兼六園の再戦

ID: `garden_boss_return` ／ 状態: blocked ／ [正本](../../ledger/イベント/garden_boss_return.yaml) ／ [個別md](events/garden_boss_return.md)

目的: 懐かしい恐怖の像と、子供たちと共に向き合う。

[イベント garden_boss_return]
**ハツ**:
あれ、なに？
**主人公**:
昔、会ったことがある。
**ハク**:
強い？
**主人公**:
強かったぞ。
**チュン**:
どのくらい？
**主人公**:
……見ればわかる。
**ハツ**:
来るよ！
[/イベント]

## ERA-08 / 石川橋の中ボス

ID: `ishikawa_bridge_boss` ／ 状態: blocked ／ [正本](../../ledger/イベント/ishikawa_bridge_boss.yaml) ／ [個別md](events/ishikawa_bridge_boss.md)

目的: 城へ続く橋で強敵に向き合う。

[戦闘 ishikawa_bridge_boss]
名前: 石川橋の中ボス
敵: M013
台詞: 条件=開始 話者=主人公 文=橋を渡るぞ。
台詞: 条件=開始 話者=ハク 文=みんな、一緒に！
[/戦闘]

## ERA-08 / 城の三体

ID: `castle_three_wars` ／ 状態: blocked ／ [正本](../../ledger/イベント/castle_three_wars.yaml) ／ [個別md](events/castle_three_wars.md)

目的: 戦争の像を前に、子供たちと城を進む。

[戦闘 castle_three_wars]
名前: 城の三体
敵: M014*3
台詞: 条件=開始 話者=ハツ 文=三つもいる！
台詞: 条件=開始 話者=主人公 文=目をそらすな。
台詞: 条件=開始 話者=ハク 文=ここを通ろう。
[/戦闘]

## ERA-08 / 額縁の予言者

ID: `castle_prophet` ／ 状態: blocked ／ [正本](../../ledger/イベント/castle_prophet.yaml) ／ [個別md](events/castle_prophet.md)

目的: 予言に心を奪われず、先へ進む。

[イベント castle_prophet]
**予言者**:
終わりは、すでに見えている。
**ハク**:
本当に？
**主人公**:
聞く必要はない。
**チュン**:
じゃあ、行こう。
[/イベント]

## ERA-08 / 額縁の予言者との戦闘

ID: `castle_prophet_battle` ／ 状態: blocked ／ [正本](../../ledger/イベント/castle_prophet_battle.yaml) ／ [個別md](events/castle_prophet_battle.md)

目的: 場面と人物の反応を描く

[戦闘 castle_prophet_battle]
名前: 予言者
敵: M022+M023
台詞: 条件=開始 話者=予言者 文=終わりが来る。
台詞: 条件=開始 話者=ハク 文=それでも行くよ。
台詞: 条件=ターン>=2 話者=カッペボーイ 文=あぶねえ！
[/戦闘]

## ERA-08 / カッペボーイの別れ

ID: `cappaboy_sacrifice` ／ 状態: blocked・仮稿 ／ [正本](../../ledger/イベント/cappaboy_sacrifice.yaml) ／ [個別md](events/cappaboy_sacrifice.md)

目的: カッペボーイが子供たちを守り、友達になりたい気持ちを伝える

[イベント cappaboy_sacrifice]
> 攻撃が子供たちへ向かう。

**カッペボーイ**:
あぶねえ！

> カッペボーイが、子供たちをかばう。

**ハク**:
どうして……！

**カッペボーイ**:
オラも、仲間になりたかったんだべ。

**チュン**:
じゃあ、いっしょに帰ろう！

**カッペボーイ**:
友達になりたきゃ、すぐ声かけろ。

**カッペボーイ**:
オラみてえに、遅くなる前に。

> カッペボーイは動かなくなった。
[/イベント]

## ERA-08 / 天守の前

ID: `final_summit_family` ／ 状態: blocked ／ [正本](../../ledger/イベント/final_summit_family.yaml) ／ [個別md](events/final_summit_family.md)

目的: 空を覆う像を前に、家族が互いの意思を確かめる。

[イベント final_summit_family]
**ハツ**:
空が、動いてる。
**主人公**:
また、来たのか……。
**ハク**:
行くんだね。
**主人公**:
怖かったら、戻っていい。
**チュン**:
一緒に行くよ。
**ハツ**:
一緒に行く！
**ハク**:
みんなで帰ろう。
**主人公**:
……ああ。みんなでな。
[/イベント]

## ERA-08 / 日本海寒帯気団収束体

ID: `storm_convergence_battle` ／ 状態: blocked ／ [正本](../../ledger/イベント/storm_convergence_battle.yaml) ／ [個別md](events/storm_convergence_battle.md)

目的: 再生する雲核と向き合う。

[戦闘 storm_convergence_battle]
名前: 日本海寒帯気団収束体
敵: M004
台詞: 条件=開始 話者=主人公 文=まだ奪うつもりか！
台詞: 条件=開始 話者=ハク 文=雲が増えてる！
台詞: 条件=開始 話者=チュン 文=あそこ、光ってる！
[/戦闘]

## ERA-08 / 雷竜との決着

ID: `lightning_dragon_battle` ／ 状態: blocked ／ [正本](../../ledger/イベント/lightning_dragon_battle.yaml) ／ [個別md](events/lightning_dragon_battle.md)

目的: 雲の中の竜と向き合い、家族の時間をつなぐ。

[戦闘 lightning_dragon_battle]
名前: 雷竜
敵: M005
台詞: 条件=開始 話者=主人公 文=あのときの……竜？
台詞: 条件=開始 話者=ハク 文=負けない！
台詞: 条件=開始 話者=主人公 文=ああ。行くぞ！
[/戦闘]

## ERA-08 / 嵐の後

ID: `after_storm_home` ／ 状態: blocked ／ [正本](../../ledger/イベント/after_storm_home.yaml) ／ [個別md](events/after_storm_home.md)

目的: 戦いの後、家族が帰る。

[イベント after_storm_home]
> 雲の向こうに、光が差す。
**ハツ**:
終わった？
> 主人公は、空を見上げる。
**主人公**:
……静かになったな。
**チュン**:
おなか、すいた！
**ハク**:
みんなで帰ろう。
**主人公**:
ああ。飯にしよう。
[/イベント]

## ERA-08 / 最後の見送り

ID: `farewell_peko` ／ 状態: blocked ／ [正本](../../ledger/イベント/farewell_peko.yaml) ／ [個別md](events/farewell_peko.md)

目的: 寿命を迎える主人公をペー子が見送る。

[イベント farewell_peko]
**ペー子**:
みんな、来ていましたよ。
**主人公**:
そうか。
**ペー子**:
あなたの隣にいられて、よかった。
**主人公**:
ありがとう。
**ペー子**:
……おやすみなさい。
[/イベント]

## ERA-08 / 幼稚園での再会

ID: `kindergarten_reunion` ／ 状態: blocked ／ [正本](../../ledger/イベント/kindergarten_reunion.yaml) ／ [個別md](events/kindergarten_reunion.md)

目的: 初めて会った場所で、二人が隣に座る。

[イベント kindergarten_reunion]
> 幼稚園。小さな椅子が二つ。
**相手**:
ここ、あいてるよ。
**主人公**:
……座ってもいいか？
**相手**:
うん。
> 二人は、隣に座る。
[/イベント]

## ERA-09 / もう一度、劇へ

ID: `new_game_return` ／ 状態: blocked ／ [正本](../../ledger/イベント/new_game_return.yaml) ／ [個別md](events/new_game_return.md)

目的: 再会から二周目の冒頭へ戻る。

[イベント new_game_return]
**誰か**:
演劇が始まるよ。
**相手**:
行こう！
**主人公**:
ああ。
> 二人は駆け出す。
[/イベント]

## ERA-09 / アオスジアゲハ

ID: `butterfly_wings` ／ 状態: blocked ／ [正本](../../ledger/イベント/butterfly_wings.yaml) ／ [個別md](events/butterfly_wings.md)

目的: シャーの暮らしと偶然の小さな変化を描く。

[イベント butterfly_wings]
> 山椒の枝で、蝶が羽化する。
**シャー**:
お、出てきたか。
> 蝶が飛び立ち、羽ばたきが頬に触れる。
**シャー**:
元気でな。
[/イベント]

## ERA-09 / 友達の家族

ID: `second_friends_family` ／ 状態: blocked・仮稿 ／ [正本](../../ledger/イベント/second_friends_family.yaml) ／ [個別md](events/second_friends_family.md)

目的: シャーとペー子が家族となり、ホワの親であることを示す。

[イベント second_friends_family]
**シャー**:
ほら、ホワ。あいさつや。
**ホワ**:
はじめまして。
**ペー子**:
私たちの子です。
**相手**:
よろしくね、ホワ！
**主人公**:
……大きくなったな、シャー。
**シャー**:
何言うとる。お前もやろ。
> ホワが、二人の顔を見比べる。
**ホワ**:
ずっと友達なんだね。
**シャー**:
ああ。長い付き合いや。
[/イベント]

## ERA-09 / 二周目の検診

ID: `second_checkup` ／ 状態: blocked ／ [正本](../../ledger/イベント/second_checkup.yaml) ／ [個別md](events/second_checkup.md)

目的: 検診による早期発見と、これからの治療を示す。

[イベント second_checkup]
**相手**:
検診、受けてきたよ。
**主人公**:
どうだった？
**ペー子**:
早く見つかって、よかった。
**相手**:
治るんだね？
**ペー子**:
はい。治療を始めましょう。
**主人公**:
一緒に行く。
**相手**:
うん。お願い。
[/イベント]

## ERA-09 / 親世代の最後の冒険

ID: `parents_final_adventure` ／ 状態: blocked ／ [正本](../../ledger/イベント/parents_final_adventure.yaml) ／ [個別md](events/parents_final_adventure.md)

目的: 親子四人で一緒に冒険する時間を描く。

[イベント parents_final_adventure]
**ハク**:
先に行っていい？
**主人公**:
道は見えてるか？
**ハク**:
見えてるよ。
**相手**:
行っておいで。
**ハツ**:
待って、一緒に行く！
**主人公**:
気をつけろよ。
**相手**:
あなた、昔より心配性だね。
**主人公**:
おまえもだろ。
**相手**:
……そうかもね。
> 二人は、先を行く子供たちを見送る。
[/イベント]

## ERA-09 / 子供たちの旅立ち

ID: `children_depart` ／ 状態: blocked ／ [正本](../../ledger/イベント/children_depart.yaml) ／ [個別md](events/children_depart.md)

目的: 子供四人に旅を任せる。

[イベント children_depart]
**ハク**:
今度は、四人で行く。
**主人公**:
困ったら、戻ってこい。
**ホワ**:
困る前に考えます。
**相手**:
頼もしいね。
**チュン**:
行ってきます！
**主人公**:
……気をつけろ。
[/イベント]

## ERA-09 / シーサイドへの入口

ID: `seaside_secret_entrance` ／ 状態: blocked ／ [正本](../../ledger/イベント/seaside_secret_entrance.yaml) ／ [個別md](events/seaside_secret_entrance.md)

目的: ペー子だけが知る場所を子供たちに示す。

[イベント seaside_secret_entrance]
**ペー子**:
私しか知らない場所があるんです。
**ホワ**:
ペー子の秘密？
**ペー子**:
ええ。海が見える場所です。
**ハク**:
行ってみよう。
[/イベント]

## ERA-09 / シーサイドの海側

ID: `seaside_balcony` ／ 状態: blocked ／ [正本](../../ledger/イベント/seaside_balcony.yaml) ／ [個別md](events/seaside_balcony.md)

目的: 二階の海側から景色を見て、おまけの冒険を楽しむ。

[イベント seaside_balcony]
**ハツ**:
海が見える！
**ホワ**:
二階からだと、遠くまで見えるね。
**チュン**:
あっちにも道がある。
> 廊下の奥で、何かが動く。
**ハツ**:
……今、見た？
**ホワ**:
見た。どうする？
**ハク**:
一緒に確かめよう。
**チュン**:
うん！
[/イベント]

## ERA-09 / シーサイドの最強ボス

ID: `seaside_strongest_boss` ／ 状態: blocked ／ [正本](../../ledger/イベント/seaside_strongest_boss.yaml) ／ [個別md](events/seaside_strongest_boss.md)

目的: 得体の知れない強敵に、四人で立ち向かう。

[イベント seaside_strongest_boss]
**ハク**:
……さっきの、あれだ。
**チュン**:
おっきい……。
**ホワ**:
引き返す？
**ハツ**:
ここまで来たんだよ！
**ハク**:
無理はしない。四人で行こう。
[/イベント]

## ERA-09 / ハクの上京

ID: `haku_wants_tokyo` ／ 状態: blocked ／ [正本](../../ledger/イベント/haku_wants_tokyo.yaml) ／ [個別md](events/haku_wants_tokyo.md)

目的: 長子の進路をめぐり、親と子が衝突する。

[イベント haku_wants_tokyo]
**ハク**:
東京へ行きたい。
**主人公**:
遠すぎる。
向こうで地震が来たら？
**ハク**:
ここにいても、来るよ。
**相手**:
戦争の話も聞く。心配なんだ。
**ハク**:
地震も戦争も、怖いよ。
**ハク**:
でも、行きたい。
**チュン**:
ハクはずっと考えてたよ。
**ホワ**:
ちゃんと話を聞いて。
**主人公**:
……行くなら、超えていけ。
[/イベント]

## ERA-09 / 鼓門前の親との戦い

ID: `kanazawa_parents_battle` ／ 状態: blocked ／ [正本](../../ledger/イベント/kanazawa_parents_battle.yaml) ／ [個別md](events/kanazawa_parents_battle.md)

目的: 親の現実的な問いを受け止め、長子が意思を示す。

[戦闘 kanazawa_parents_battle]
名前: 顔の見えない巨人
敵: M006*2
台詞: 条件=開始 話者=主人公 文=金は、どうする？
台詞: 条件=開始 話者=ハク 文=働く。足りなきゃ考える。
台詞: 条件=ターン>=2 話者=相手 文=地震が来たら？
台詞: 条件=ターン>=2 話者=ハク 文=備える。怖くても行く。
台詞: 条件=ターン>=3 話者=主人公 文=帰れなくなったら？
台詞: 条件=ターン>=3 話者=ハク 文=それでも、行きたい。
[/戦闘]

## ERA-09 / 鼓門の召喚

ID: `tsuzumi_gate_summon` ／ 状態: blocked ／ [正本](../../ledger/イベント/tsuzumi_gate_summon.yaml) ／ [個別md](events/tsuzumi_gate_summon.md)

目的: 長子の召喚をきっかけに親子の衝突が解ける。

[イベント tsuzumi_gate_summon]
**ハク**:
お願い。道を開けて！
> 鼓門の像が現れ、二体の巨人を打つ。
> 9999の数字が、二つ並ぶ。
**相手**:
……聞こえたよ。あなたの気持ち。
**主人公**:
まだだ！
> 相手は水の召喚獣となり、火の主人公に水をかける。
**主人公**:
……冷たいな。
**相手**:
この子の足で、行かせよう。
**主人公**:
……ああ。
[/イベント]

## ERA-09 / 旅立ち直前

ID: `haku_family_sendoff` ／ 状態: blocked ／ [正本](../../ledger/イベント/haku_family_sendoff.yaml) ／ [個別md](events/haku_family_sendoff.md)

目的: 場面と人物の反応を描く

[イベント haku_family_sendoff]
**ハツ**:
向こう、遠いね。
**ハク**:
うん。でも、帰ってこられるよ。
**チュン**:
おみやげ、忘れないでね。
**ハク**:
覚えてたらね。
**ホワ**:
帰ってきたら、話を聞かせてくれよ。
**ハク**:
うん。待ってて。
[/イベント]

## ERA-09 / 金沢駅の見送り

ID: `kanazawa_platform_farewell` ／ 状態: blocked ／ [正本](../../ledger/イベント/kanazawa_platform_farewell.yaml) ／ [個別md](events/kanazawa_platform_farewell.md)

目的: 長子を見送り、ホワの秘密が明らかになる。

[イベント kanazawa_platform_farewell]
**相手**:
着いたら連絡してね。

> ハクはうなずく。

**主人公**:
元気でな。

**ハツ**:
おみやげ、忘れないでね。

**チュン**:
また帰ってきてね。

**ハク**:
うん。行ってきます。
[/イベント]

## ERA-09 / 新幹線の隣席

ID: `shinkansen_sit_by_me` ／ 状態: blocked ／ [正本](../../ledger/イベント/shinkansen_sit_by_me.yaml) ／ [個別md](events/shinkansen_sit_by_me.md)

目的: 二人が隣に座り、題名に着地する。

[イベント shinkansen_sit_by_me]
> 新幹線の扉が閉まり、列車が動き出す。

**ハク**:
……あれ、ホワ？

**ホワ**:
隣の席、とってあるよ。

**ハク**:
いつの間に！？

**ホワ**:
言ったら、止められるから。

> ホームの家族が、窓を見上げる。

**相手**:
……ホワも乗ってる！

**主人公**:
なんだって！？

> ホームの姿が、少しずつ遠ざかる。

**ハク**:
これから、どうするの？

**ホワ**:
着いてから考える。

> 二人は、隣に座る。
[/イベント]
