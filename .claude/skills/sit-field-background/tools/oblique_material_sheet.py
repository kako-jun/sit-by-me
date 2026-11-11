"""素材見本シート（CRAFT MATERIAL SHEET）の決定的な作成。採用済みの手作りミニチュアの画像と、以前の良い絵（鉄道模型のジオラマの質感）から、
物の形が入らない『素材だけ』の局所クロップを切り出して並べる。oblique_e2_run.sh の参照画像（素材の質感・作り方の参考のみ）に常に付ける。

  uv run --with pillow python3 oblique_material_sheet.py crops   # CROPS の元画像から crops/*.webp（可逆）を切り出す（元画像が必要。git の履歴からも読む）
  uv run --with pillow python3 oblique_material_sheet.py build   # crops/*.webp から material-swatch-sheet.webp（可逆）を組む
  uv run --with pillow python3 oblique_material_sheet.py check   # 今のシートが crops から組み直した結果と画素まで一致するか

出力先: docs/production/oblique-mocks/material-swatch/（crops/ と material-swatch-sheet.webp。ファイル配置 oblique-mocks の下。元画像と切り出し枠の正本は本ファイルの CROPS）。
クロップは遊具・人物・文字が入らない位置にし、構図のコピーを防ぐため1枚 330x220 に縮小する。決定 SIT.miniature-materials-not-photoreal・Issue #191。
"""
import io
import os
import subprocess
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.environ.get("LEDGER_ROOT") or os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
OUTDIR = os.path.join(REPO, "docs", "production", "oblique-mocks", "material-swatch")
CROPDIR = os.path.join(OUTDIR, "crops")
SHEET = os.path.join(OUTDIR, "material-swatch-sheet.webp")
T3 = "assets/images/fields/reference/teramachi-grounds-exterior-trm03-adopted.webp"
T8 = "assets/images/fields/reference/teramachi-road-well-canal-trm08-adopted.webp"
OLD = "git:22dc9511:sample/field/diorama-trial/teramachi-wide-road-diorama.png"  # 2026-10-14 の以前の良い絵（鉄道模型のジオラマの質感）
W, H = 330, 220
COLS = 5
# (ファイル名, 元画像, 切り出し枠 x0,y0,x1,y1, 何の素材か)
CROPS = [
    ("01-cotton-snow-ground", T3, (1010, 640, 1230, 787), "綿の雪の地面"),
    ("02-clay-roof-tiles-snow", T3, (700, 40, 920, 187), "紙粘土の瓦と綿の雪"),
    ("03-plaster-wall-wood", T3, (1150, 170, 1370, 317), "紙粘土の漆喰壁と木の窓枠"),
    ("04-sponge-pine", T3, (1060, 690, 1280, 837), "スポンジと綿の松"),
    ("05-cut-stone-paving", T3, (745, 480, 965, 627), "石粉粘土の石畳"),
    ("06-cardboard-edge", T3, (760, 790, 980, 937), "段ボール断面の台座（テープ・糊の垂れの無い区間）"),
    ("07-clay-stone-base", T8, (150, 780, 370, 927), "石粉粘土の石積みと綿の雪"),
    ("08-black-paper-road", T8, (560, 300, 780, 447), "黒紙とサンドペーパーの道"),
    ("09-clipped-hedge-wall", T8, (610, 740, 830, 887), "紙粘土の石垣と刈り込みの生垣"),
    ("10-old-cotton-roof", OLD, (190, 690, 410, 837), "綿の屋根（以前の良い絵）"),
    ("11-old-railway-trees", OLD, (660, 40, 880, 187), "鉄道模型の木（以前の良い絵）"),
    ("12-old-bamboo-fence", OLD, (800, 860, 1020, 1007), "爪楊枝・割り箸の竹垣（以前の良い絵）"),
    ("13-old-white-pole", OLD, (820, 100, 1040, 247), "割り箸の白い柱（以前の良い絵）"),
    ("14-old-blue-resin", OLD, (620, 285, 840, 432), "青い透明樹脂の用水（以前の良い絵）"),
    ("15-old-black-road", OLD, (340, 535, 560, 682), "黒い画用紙の道（以前の良い絵）"),
]


def open_src(spec):
    if spec.startswith("git:"):
        _, rev, path = spec.split(":", 2)
        data = subprocess.run(["git", "show", f"{rev}:{path}"], cwd=REPO, check=True, capture_output=True).stdout
        return Image.open(io.BytesIO(data)).convert("RGB")
    return Image.open(os.path.join(REPO, spec)).convert("RGB")


def do_crops():
    os.makedirs(CROPDIR, exist_ok=True)
    cache = {}
    for name, src, box, _ in CROPS:
        im = cache.setdefault(src, open_src(src))
        im.crop(box).resize((W, H), Image.LANCZOS).save(os.path.join(CROPDIR, name + ".webp"), lossless=True)
        print("crop", name)


def assemble():
    rows = -(-len(CROPS) // COLS)
    sheet = Image.new("RGB", (W * COLS + 10 * (COLS + 1), H * rows + 10 * (rows + 1)), (60, 50, 45))
    for i, (name, *_rest) in enumerate(CROPS):
        c = Image.open(os.path.join(CROPDIR, name + ".webp")).convert("RGB")
        sheet.paste(c, (10 + (i % COLS) * (W + 10), 10 + (i // COLS) * (H + 10)))
    return sheet


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "build"
    if mode == "crops":
        do_crops()
    elif mode == "build":
        os.makedirs(OUTDIR, exist_ok=True)
        assemble().save(SHEET, lossless=True)
        print("wrote", SHEET)
    elif mode == "check":
        a = Image.open(SHEET).convert("RGB")
        b = assemble()
        if a.size != b.size or a.tobytes() != b.tobytes():
            sys.exit("FAIL: material-swatch-sheet.webp が crops から組み直した結果と違う（build を再実行）")
        print("PASS: 素材見本シートは crops と一致")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
