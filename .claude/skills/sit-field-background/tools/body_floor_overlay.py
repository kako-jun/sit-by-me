#!/usr/bin/env python3
"""体内 BDY-xx の生成画像の『床』を期待床（清書図）と重ねて IoU を出し、重ね画像を書く。画像生成はしない。
旧 scratchpad の ov.py（床色固定・MAPごとに手書き）を、床色を画像から自動推定する版に整備したもの。
IoU の定義は check_body_image.py の floor_iou_ov と同一（このスクリプトはそれを呼ぶだけ）:
  床色 = 天面 rect 内のクリーム系画素の最大連結クラスタの中央値（固定値でない）
  実測床 = 床色との和絶対差<45 の画素の開閉2回→最大連結成分、天面 rect を14px内側に縮めた範囲
  期待床 = verification/body-layout/clean/<MAP>.png の床色（膨張・補正なし）
重ね画像の色: 緑=両方に床 / 赤=期待にあるが実測に無い / 青=実測にあるが期待に無い。

実行:
  uv run --with pillow --with numpy --with scipy python3 -I body_floor_overlay.py BDY-07 generated.png [--out overlay.png] [--clean path]
"""
import argparse
import importlib.util
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent


def load_checker():
    spec = importlib.util.spec_from_file_location("check_body_image", HERE / "check_body_image.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("map_id")
    ap.add_argument("image")
    ap.add_argument("--clean")
    ap.add_argument("--out")
    args = ap.parse_args()
    ck = load_checker()
    clean_path = Path(args.clean) if args.clean else ck.REPO / "verification/body-layout/clean" / f"{args.map_id}.png"
    if not clean_path.exists():
        sys.exit(f"期待幾何が無い: {clean_path}")
    img = Image.open(args.image).convert("RGB")
    W, H = img.size
    s = W / 1920.0
    a = np.asarray(img).astype(int)
    clean = Image.open(clean_path).convert("RGB").resize((W, H), Image.NEAREST)
    ca = np.asarray(clean).astype(int)
    exp_floor = ck.eq(ca, ck.CL_FLOOR)
    ys, xs = np.where(exp_floor | ck.eq(ca, ck.CL_TERRAIN) | ck.eq(ca, ck.CL_WALL))
    exp_rect = (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)
    m = int(round(14 * s))
    fcol, ok, npx = ck.estimate_floor_color(a, (exp_rect[0] + m, exp_rect[1] + m, exp_rect[2] - m, exp_rect[3] - m))
    iou, fl, e = ck.floor_iou_ov(a, fcol, exp_floor, exp_rect, s)
    print(f"{args.map_id} IoU {iou:.3f}  床色(推定{'OK' if ok else '失敗・既定色'}) {tuple(int(x) for x in fcol)}  "
          f"actual {int(fl.sum())} exp {int(e.sum())} both {int((fl & e).sum())} exp-only {int((e & ~fl).sum())} act-only {int((fl & ~e).sum())}")
    o = a.astype(float)
    for mk, cl in ((fl & e, (0, 200, 0)), (e & ~fl, (230, 0, 0)), (fl & ~e, (0, 80, 255))):
        o[mk] = o[mk] * 0.5 + np.array(cl) * 0.5
    out = Path(args.out) if args.out else Path(args.image).with_name(Path(args.image).stem + "-floor-overlay.png")
    out.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(o.astype(np.uint8)).save(out)
    print(f"重ね画像: {out}")


if __name__ == "__main__":
    main()
