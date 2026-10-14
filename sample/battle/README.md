# 戦闘画面サンプル素材

すべて画像生成で作った仮置き素材（実写ではない）。実写素材に差し替える予定。

`enemy-dragon.png` は、緑背景で生成した段ボールのドラゴンをクロマキーで透過したもの（長辺640px）。味方は `assets/characters/poses/` の確定ポーズを使う。

## お遊戯会の舞台での表示確認（stage-b / stage-c）

`stage-b.json` / `stage-c.json` は、4人の戦闘ポーズ（ready）と段ボールのドラゴンを、舞台の背景（`backgrounds/stage-{b,c}.png`）で並べる name-name 戦闘サンプル用の設定。リポジトリのルートを CORS 付きで配信し、`battle-sample.html?config=<配信URL>/sample/battle/stage-c.json` で開く。
