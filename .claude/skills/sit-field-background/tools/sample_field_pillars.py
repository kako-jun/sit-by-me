"""サンプル専用マップ SMP-01（時の最果て）の柱の裏を歩けるようにする: 歩行マスクと前面レイヤーを plan から決定論で作る（Issue #286）。

画像生成 AI は使わない。入力は plan（docs/production/sample-field/SMP-01-plan.json）と採用背景（台帳 素材.yaml の A-1362）だけ。

- 歩行マスク（白=歩ける・黒=不可。RGB・可逆 WebP・1672x941）: 足場の円盤の内側から、柱と光の柱の「足元の矩形」だけを黒にする。
  旧版は柱の見た目の覆い（高さぶんの箱のシルエット）まで黒にしていたので、柱の裏（奥側）を歩けなかった。
- 前面レイヤー（透過 WebP・背景と同寸。name-name の `前面=`、#866）: 主人公より手前に重ねる絵。柱ごとに
  『柱の箱のシルエット（左右・上へ余白 MARGIN px）のうち、足元の矩形の奥の辺（画像の y）より上』だけを採用背景から切り抜く。
  人物が柱の裏にいるとき（足元が奥の辺より上）は、体が柱に隠れて柱が手前に見える。足元の矩形は歩行不可なので、柱の足元は通れない。
  限界: 前面レイヤーは1枚の静止画で、人物との前後を毎フレーム比べない。足元の矩形の脇（柱の見た目の幅の内側）に立つ人物の頭が、
  足元が奥の辺より下で約38px 以内のとき柱の上部に隠れる。光の柱は足場の奥の縁に立ち、その裏に歩ける床が無いので前面には出さない。
  追従: name-name Issue #1190（前面をレイヤーごとの切れ目線で奥行きソートする）。

使い方（リポのルートで。画像だけ書く。台帳の素材行の sha256 は build_ledger.py の検査が見る）:
  uv run --with numpy --with opencv-python-headless --with pillow python3 -I .claude/skills/sit-field-background/tools/sample_field_pillars.py build
"""
import argparse
import copy
import os
import sys

import cv2
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import oblique_mock as M  # noqa: E402

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))
PLAN = os.path.join(REPO, "docs", "production", "sample-field", "SMP-01-plan.json")
BACKGROUND = os.path.join(REPO, "assets", "images", "fields", "reference", "sample-field-smp01-adopted.webp")
MASK_OUT = os.path.join(REPO, "assets", "images", "fields", "masks", "SMP-01-mask.webp")
FOREGROUND_OUT = os.path.join(REPO, "assets", "images", "fields", "foreground", "SMP-01-foreground.webp")
PREVIEW_OUT = os.path.join(REPO, "docs", "production", "sample-field", "SMP-01-foreground-preview.png")
MARGIN = 6  # 採用画像の柱の笠は plan の箱より左右・上に数px はみ出す。余白は必要最小限（広いと柱の脇の床・空まで前面に写り、脇に立つ人物の端をつぶす）
FOOT_EXT = 12  # 柱の台座（円形の土台）は plan の足元の矩形の手前の辺より画像で約12px 下まである。その分まで足元の矩形を広げて、台座の手前縁に立てないようにする（柱のみ）


def _fill(arr, pts, v):
    cv2.fillPoly(arr, [np.round(np.array(pts)).astype(np.int32)], v)


def foot_blocked(p):
    """柱（kind=column）と光の柱（kind=light）の足元の矩形（z=0 の画像上の四角形）。"""
    out = []
    for b in p["boxes"]:
        if b.get("blocked") and b["kind"] in ("column", "light"):
            poly = M.rect_poly(b["rect"])
            if b["kind"] == "column":  # 手前の辺（頂点 2・3）を台座の下端まで下げる
                poly = [poly[0], poly[1], (poly[2][0], poly[2][1] + FOOT_EXT), (poly[3][0], poly[3][1] + FOOT_EXT)]
            out.append((b, poly))
    return out


def derive_mask(p):
    q = copy.deepcopy(p)
    for b in q["boxes"]:
        if b["kind"] in ("column", "light"):
            b["blocked"] = False  # 箱のシルエット全体を黒にしない（足元の矩形だけ後で黒にする）
    m, _, _, _, _ = M.derive_mask(q)
    for _, poly in foot_blocked(p):
        _fill(m, poly, 0)
    return m


def derive_foreground_alpha(p):
    """柱ごとの『箱のシルエット＋余白のうち、足元の矩形の奥の辺より上』の不透明度（0/255）。"""
    alpha = np.zeros((M.H_IMG, M.W), np.uint8)
    cuts = {}
    for b, _ in foot_blocked(p):
        if b["kind"] != "column":
            continue
        x0, y0, x1, y1 = b["rect"]
        cut = int(round(M.proj((x0 + x1) / 2, y0)[1]))  # 足元の矩形の奥の辺の画像 y
        sil = np.zeros((M.H_IMG, M.W), np.uint8)
        for pts, _, _ in M.box_polys(b["rect"], b["h"], b["color"]):
            _fill(sil, pts, 255)
        sil = cv2.dilate(sil, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * MARGIN + 1, 2 * MARGIN + 1)))
        sil[cut:, :] = 0
        alpha = np.maximum(alpha, sil)
        cuts[b["id"]] = cut
    return alpha, cuts


def build():
    p = M.load_plan(PLAN)
    m = derive_mask(p)
    os.makedirs(os.path.dirname(MASK_OUT), exist_ok=True)
    Image.fromarray(np.stack([m, m, m], -1)).save(MASK_OUT, lossless=True)
    alpha, cuts = derive_foreground_alpha(p)
    bg = np.array(Image.open(BACKGROUND).convert("RGB"))
    if bg.shape[:2] != (M.H_IMG, M.W):
        sys.exit(f"背景の寸法が {M.W}x{M.H_IMG} ではない: {bg.shape}")
    rgba = np.dstack([bg * (alpha[..., None] > 0), alpha]).astype(np.uint8)
    os.makedirs(os.path.dirname(FOREGROUND_OUT), exist_ok=True)
    Image.fromarray(rgba, "RGBA").save(FOREGROUND_OUT, lossless=True, exact=True)
    # 目視用: 背景を暗くし、前面レイヤーの不透明部分だけ明るく、歩けない足元の矩形を赤で重ねる（リポの派生物。画像ビューアで見せる）
    prev = (bg * 0.35).astype(np.float32)
    a = alpha > 0
    prev[a] = bg[a]
    red = np.zeros_like(m)
    for _, poly in foot_blocked(p):
        _fill(red, poly, 255)
    prev[red > 0] = prev[red > 0] * 0.4 + np.array([255, 40, 40]) * 0.6
    Image.fromarray(np.clip(prev, 0, 255).astype(np.uint8)).save(PREVIEW_OUT)
    print("mask", MASK_OUT, "白:", int((m > 0).sum()))
    print("foreground", FOREGROUND_OUT, "不透明:", int(a.sum()), "奥の辺の y:", cuts)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("action", choices=("build",))
    ap.parse_args()
    build()
