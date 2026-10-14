# ロゴ下絵（能登の口）

- `logo-noto-mouth-{a,b}.svg` が正本、`.png` は透過(1600px幅)。A=口を大きく、B=口＋広め。
- 輪郭: 国土数値情報 行政区域 N03-20230101 石川県（国土交通省）を Web メルカトルで描画。能登島のポリゴンのみ除外し、その位置にタイトル文字を置く。
- 目: ベクター（輪島付近の陸地内）。
- タイトル `SIT BY ME`: Cinzel Bold（SIL OFL 1.1、https://github.com/NDISCOVER/Cinzel 、`scripts/fonts/` に同梱）をアウトライン化し、1行（改行なし）で字幅を絞った縦長の大文字に変形（字幅比0.5、能登島の外接矩形の96%幅に収める）。SVG はフォント非依存。
- 再生成: `scripts/noto_logo_geo.py`（`--with shapely --with fonttools`）、PNG は `scripts/svg_to_png.py`。
