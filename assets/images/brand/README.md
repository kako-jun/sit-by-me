# ロゴ（暫定の文字ロゴ）

- 「SIT BY ME」を縦長の大文字フォントで書いた**仮置き**のロゴ（2行: `SIT BY` / `ME`）。のちに正式なロゴへ差し替える予定（#68）。FF5ロゴそのものの模倣はしない（フォントの雰囲気のみ）。
- `logo.svg` が正本、`logo.png`（幅1600px、透過）は SVG からの派生。WebP化はしない。
- フォント: Noto Serif Display ExtraCondensed Black（SIL Open Font License 1.1）。出所: Noto Project Authors、https://github.com/notofonts/latin-greek-cyrillic （ローカルは Arch `noto-fonts`、`/usr/share/fonts/noto/NotoSerifDisplay-ExtraCondensedBlack.ttf`）。文字は輪郭化済みで、SVGはフォント非依存。
- 配色: 金のグラデーション（#f6ecc8→#d9bd73→#9c7a34）＋暗褐色の縁（#2a1f0c）。ダークテーマの背景で読める。
- 再生成:
  1. `uv run --with fonttools python3 -I scripts/make_logo.py /usr/share/fonts/noto/NotoSerifDisplay-ExtraCondensedBlack.ttf assets/images/brand/logo.svg two`（1行版は末尾を `one`）
  2. `uv run --with resvg-py --with pillow python3 -I scripts/svg_to_png.py assets/images/brand/logo.svg assets/images/brand/logo.png 1600`
- 旧ロゴ下絵（能登の口、BRAND001・002）は不採用で削除済み。
