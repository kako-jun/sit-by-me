# 戦闘画面サンプル素材

すべて画像生成で作った仮置き素材（実写ではない）。実写素材に差し替える予定。

| 出力 | 元ファイル | 加工 |
|---|---|---|
| party-a/b/c/d.png | cast-growth-sheet.png（成長シート1672x941）の一番上の行（幼稚園）左から男A・女B・男C・女D | 灰色背景を外周からのフラッドフィル＋足元の影除去で透過、defringe、tight bbox。4人共通の縮小率（今回は等倍） |
| enemy-dragon.png | cardboard-dragon.png（緑背景） | 緑ゲイン(G-max(R,B))でクロマキー、spill除去、tight bbox、長辺640px |
| background.png | street-bg.png（1672x941） | コピーのみ |

再生成:

```
uv run --with pillow --with numpy --with scipy python3 -I tools/prepare_assets.py \
  --sheet cast-growth-sheet.png --dragon cardboard-dragon.png --bg street-bg.png --out .
```
