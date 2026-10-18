# 戦闘画面サンプル素材

画像生成による戦闘検証設定。素材の状態とIDは [素材配置台帳](../../docs/production/asset-layout.md) を参照する。

敵は `assets/images/enemies/M001.png`（旧長辺640px、品質再承認ではない）。味方は `assets/images/characters/C001`〜`C004` の `poses/ready.png` を使う。

## お遊戯会の舞台での表示確認（stage-b / stage-c）

`stage-b.json` / `stage-c.json` は4人とM001をBG005／BG006で並べるname-name検証設定。リポジトリrootをCORS付きで配信し、`battle-sample.html?config=<配信URL>/verification/battles/stage-c.json` で開く。JSON内の画像は設定URLを基準とする相対パスで読む。
