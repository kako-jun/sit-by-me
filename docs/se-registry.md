# 仮SE

Issue #67。SFC時代のRPGを思わせる短い電子音を、既存曲を使わず波形合成した試作。全件仮で、実際の操作中の音量・音色は試聴して調整する。勝利・入手ジングルはBGM側の範囲。

| ID | 用途 | 音の形 | 状態 |
|---|---|---|---|
| cursor | カーソル移動 | 高い短音 | 仮 |
| confirm | 決定 | 上昇音 | 仮 |
| cancel | 戻る | 下降音 | 仮 |
| error | 操作不可 | 低い短音 | 仮 |
| encounter | エンカウント開始 | 急降下 | 仮 |
| mosaic | モザイク遷移 | 短いノイズ | 仮 |
| attack | 攻撃 | 鋭いノイズ | 仮 |
| damage | 被弾 | 低い下降音 | 仮 |
| heal | 回復 | 上昇音 | 仮 |

パラメータは `assets/se/params/<ID>.json`、音声は `assets/sounds/se/<ID>.ogg`。`uv run python3 scripts/se_synth.py` で全件を再生成する（ffmpeg と libvorbis が必要）。種はノイズの再現に使用する。戦闘や操作への自動接続は name-name 側の再生口が必要で、現時点では未接続。

`assets/sounds/se/manifest.json` は name-name の仮SE再生経路（#1198）用の割当。配線には name-name 側の変更が必要であり、素材の追加だけでは鳴らない。
