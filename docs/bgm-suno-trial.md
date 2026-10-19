# BGM 用 Suno 試験手順書（新世界の主題フレーズ）

**状態: 試験用の手順案。** 目的は「Suno に新世界の旋律を読ませたとき、旋律がどこまで保たれるか」を人の耳で確かめること。スロットの割当や採用は決定ではない（正本は bgm-registry.md）。Suno 側の画面・メニュー名・上限は変わるので、以下の名称は**現行 UI で確認**してから使う。

## 1. 入力素材

置き場は `~/data/sit-bgm/suno-input/`（git 管理外。リポ内に音源を置かない）。一覧と位置は `docs/bgm-phrases.csv`。

| 主題ID | 主題 | 気分 | (a) 録音から切り出し | (b) 旋律だけ |
|---|---|---|---|---|
| m2_largo | 第2楽章 主旋律(イングリッシュホルン) | 悲 | clips/m2_largo_{stokowski1927,omega13a2026}.wav | midi/m2_largo.mid ・ m2_largo_mono.wav |
| m1a_horn | 第1楽章 第1主題(ホルン) | 楽 | clips/m1a_horn_*.wav | midi/m1a_horn.mid ・ m1a_horn_mono.wav |
| m1b_flute | 第1楽章 第2主題(フルート) | 楽 | clips/m1b_flute_*.wav | midi/m1b_flute.mid ・ m1b_flute_mono.wav |
| m3_scherzo | 第3楽章 Scherzo 主題 | 楽 | clips/m3_scherzo_*.wav | midi/m3_scherzo.mid ・ m3_scherzo_mono.wav |
| m4_finale | 第4楽章 冒頭主題(英雄) | 緊 | clips/m4_finale_*.wav | midi/m4_finale.mid ・ m4_finale_mono.wav |

- （ランクA/B/C/X の定義は bgm-sources-research.md の冒頭）`stokowski1927` = Stokowski 1927（ランクC・CC0はアップロード者の宣言のみ・米国で 2028-01-01 まで保護期間内の計算・モノラル電気録音。音は古い）。**現状のクリップ入力はこの1927年版。1925年版（ランクA）の同位置クリップは未作成。**`omega13a2026` = 打ち込み全曲（ランクB・CC BY 4.0。音がきれい。**公開・配布時はクレジット必須**）。
- (b) の MIDI は Mutopia の楽譜 MIDI（Sym9, CC BY-SA 3.0）を、打ち込み音源のピッチ追跡で検証・補正して作った単旋律。WAV は MIDI から合成した減衰する単音（sine+倍音）。MIDI は Suno に直接上げられない想定なので **WAV を上げる**。MIDI は DAW で楽器を変えて書き出す用。
- 位置は『候補』。**最終は人の耳**（要耳確認の列を見る）。

## 2. Suno での試し方（メニュー名は現行 UI で確認）

1. Suno の作成画面で、音声ファイルを読み込む機能を探す（「Upload Audio」「Add Audio」等の名前。無料枠で使えるか・長さ上限・商用可否のプラン条件は**現行の規約で確認**）。
2. 読み込んだ音声から曲を作る方式を選ぶ。名称は「Cover」「Extend」などで、時期により違う。試す順は次の2つ:
   - **Cover 系（旋律を保ったまま編成・曲調を変える）**: 旋律保持が目的なのでまずこちら。
   - **Extend 系（フレーズの続きを作る）**: ループ向きの展開や続きの旋律が出るかを見る。
3. スタイル欄にプロンプトを入れる。例（英語、短く具体的に）:
   - 悲（m2）: `progressive rock, melancholic, english horn lead melody kept intact, slow, warm analog synth pad, soft drums, 60 bpm`
   - 楽（m1a/m1b/m3）: `progressive rock, bright, playful, flute lead melody kept intact, steady groove, acoustic guitar and organ, mid tempo`
   - 緊（m4）: `progressive rock, heroic, tense, brass-like synth lead melody kept intact, driving drums, distorted guitar, fast`
   - 歌なしにしたいので、インスト指定（`instrumental` の項目があれば有効にする）。
4. 1設定につき複数テイク（2〜4）を生成し、採用は人間が選ぶ。

## 3. 試す順

1. **m2_largo**（最も旋律が知られていて保持の判定がしやすい）: (a) omega → (a) stokowski → (b) mono.wav の順。
2. **m4_finale**（E-F#-G-F#-E の動機。リズムが特徴的）。
3. **m1a_horn** → **m1b_flute** → **m3_scherzo**（速い音型は崩れやすい。後回し）。
4. 各主題とも (a) 2種と (b) 1種を同じプロンプトで比べる。(a) の2種は「きれいな打ち込み」と「古い録音」で出力が変わるかを見る。

## 4. 聞くポイント

- **旋律が保たれるか**: 冒頭の音の並び（例 m2: F-Ab-F-Eb-Db、m4: E-F#-G-F#-E、m1a: E-G-B-E-G-E-C-B-E）が追えるか。音程が変わった・リズムが崩れた・別メロディになったを区別して記録する。
- **編成**: 指定した編成（プログレ寄り）に変わったか。元の管弦楽の音色が残っていないか。
- **ループ向きか**: 終わりと始まりが繋がるか。無音・フェードアウトの有無。繋ぎやすい小節数か。
- **気分**: 悲/楽/緊の系統に合っているか（bgm-registry.md の凡例）。
- **既存曲への似方**: 原曲そのままに聞こえすぎないか／別の既存曲に似ていないか（bgm-registry.md 第7節の確認事項）。
- **位置の確認**: 切り出し区間が本当にその主題か（開始が早い・遅い、余計な音が混ざる）。ずれていたら bgm-phrases.csv の開始/終了秒を直す。

## 5. 結果の記録欄

テイクごとに1行。採否は人が決める。

| 日付 | 主題ID | 入力(a/b・録音ID) | モード(Cover/Extend 等・現行UIの名称) | プロンプト | 旋律保持(○△×) | 編成 | ループ向き(○△×) | 気分の合致 | メモ・採用候補 |
|---|---|---|---|---|---|---|---|---|---|
| | | | | | | | | | |
| | | | | | | | | | |
| | | | | | | | | | |

## 6. 注意

- 録音の権利確認は bgm-sources-research.md の通り（Stokowski1927 は CC0 宣言のみで、計算上、米国では 2028-01-01 まで保護期間内。公開・商用を見据えるなら、1925年版（ランクA、計算上 2026-01-01 から PD）で切り出し直すのが次手。弁護士確認は未了。omega13a2026 は CC BY 4.0 のためクレジット要）。
- (b) 経路(MIDI→単音WAV)は CC BY-SA 3.0 の継承が出力に及ぶか未整理。公開前に要確認。
- omega13a2026 (CC BY 4.0): 打ち込み(MuseSounds等のレンダリング)音声の再配布可否は未確認。Suno入力にして出力を商用配布する可否は未確定。
- 位置・音符は自動解析の候補。特に m3_scherzo（速い反復音）と m1b_flute（速い音型）は追跡の裏付けが薄く、MIDI の多くを楽譜で補っている。耳で確認すること。
