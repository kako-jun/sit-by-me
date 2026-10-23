#!/usr/bin/env python3
"""体内 BDY-xx の採用画像と配置モック（清書図）の位置合わせ・床の切り出し・位相検査（試作）。画像生成はしない。

実行:
  uv run --with pillow --with numpy --with scipy --with opencv-python-headless python3 -I body_register.py \
      BDY-04 assets/images/fields/reference/body-brain-maze-bdy04-adopted.webp --out DIR \
      [--npc "kiosk:0.30,0.50;guard:0.9,0.1"] [--clean PATH] [--json-out PATH]

処理:
  (a) 採用画像から模型の天面の矩形（check_body_image.measure_layers）と床色・床を抽出
  (b) モック(1920x1080)の天面 1644x804 を画像の天面へ合わせる初期変換（拡大＋平行移動）→ 床の境界の chamfer 照合で精密化。
      自由度の候補 T(平行移動) / S(+等方拡大) / SR(+回転) / A(+縦横比) を全部試し、最小の自由度で十分なものを採る
  (c) 変換パラメータ・残差・信頼度・重ね画像を出す
  (d) 位置合わせ後のモックを種に、画像の色で床を切り出す（床の二値マスク、画像と同寸）。モックとの差を報告
  (e) 位相検査: 連結成分・縁に届く出口・スライス断面の区間数・（BDY-04）迷路格子の辺／行き止まり／T字・（脚の通路）折れ点
  (f) NPC・イベント位置を模型比率(u,v)で与えると、画像座標へ写して床の上の最寄りへ寄せる（寄せ距離を返す）

出力: <out>/<MAP>-register.json, -overlay.png, -floor-cut.png(0/255), -diff.png(緑=両方・赤=モックのみ・青=画像のみ),
      -topology.png, -npc.png（NPC指定時）
"""
import argparse
import importlib.util
import json
import math
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
from scipy.optimize import minimize

HERE = Path(__file__).resolve().parent


def _load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ck = _load("check_body_image")
REPO = ck.REPO
MOCK_RECT = (138, 138, 1782, 942)   # 模型の天面（body_layout.py の MX0..MY1）
MOCK_W, MOCK_H = 1920, 1080


# ------------------------------------------------------------ 変換
class Xf:
    """モック px -> 画像 px。x' = A (x - c) + c' ... を 2x3 行列で持つ。"""

    def __init__(self, M):
        self.M = np.asarray(M, float)             # 2x3
        A = np.vstack([self.M, [0, 0, 1]])
        self.Minv = np.linalg.inv(A)[:2]

    def pts(self, p):
        p = np.asarray(p, float).reshape(-1, 2)
        return p @ self.M[:, :2].T + self.M[:, 2]

    def inv_pts(self, p):
        p = np.asarray(p, float).reshape(-1, 2)
        return p @ self.Minv[:, :2].T + self.Minv[:, 2]

    def decompose(self):
        a, b, c, d = self.M[0, 0], self.M[0, 1], self.M[1, 0], self.M[1, 1]
        sx = math.hypot(a, c)
        rot = math.degrees(math.atan2(c, a))
        sy = (a * d - b * c) / sx
        return dict(scale_x=round(sx, 5), scale_y=round(sy, 5), rot_deg=round(rot, 4),
                    tx=round(float(self.M[0, 2]), 2), ty=round(float(self.M[1, 2]), 2))


def make_xf(rect_img, p, model):
    """rect 合わせの初期変換に、パラメータ p（モデルごと）で補正を足した Xf。
    p = [dx, dy, dlogs, drot_deg, dlog_aniso]。補正は天面の中心まわり。"""
    x0, y0, x1, y1 = rect_img
    mx0, my0, mx1, my1 = MOCK_RECT
    sx0, sy0 = (x1 - x0) / (mx1 - mx0), (y1 - y0) / (my1 - my0)
    dx, dy, dls, dr, dla = p
    s = math.exp(dls)
    ax = math.exp(dla / 2)
    ay = math.exp(-dla / 2)
    th = math.radians(dr)
    cth, sth = math.cos(th), math.sin(th)
    mc = np.array([(mx0 + mx1) / 2, (my0 + my1) / 2])
    ic = np.array([(x0 + x1) / 2, (y0 + y1) / 2])
    S0 = np.diag([sx0, sy0])
    R = np.array([[cth, -sth], [sth, cth]]) * s @ np.diag([ax, ay])
    A = R @ S0
    t = ic + np.array([dx, dy]) - A @ mc
    return Xf(np.hstack([A, t[:, None]]))


MODELS = {          # 自由度ごとの使うパラメータ index
    "T": [0, 1],
    "S": [0, 1, 2],
    "SR": [0, 1, 2, 3],
    "A": [0, 1, 2, 3, 4],
}


# ------------------------------------------------------------ 画像側の抽出
def extract_rect(a, s, exp_rect_scaled):
    """画像の天面 rect（4層測定 = check_body_image.measure_layers）。辺ごとに判定する:
    その辺の層（縁取り foam・波形 corr）が読め、かつ期待から 60px(×倍率) 以内なら測定値を採り、
    読めない・外れる辺だけ期待値へフォールバックして理由を side_reasons に残す（全辺まとめての切り替えはしない）。"""
    H, W = a.shape[:2]
    layers = ck.measure_layers(a, s)
    exp_edge = dict(N=exp_rect_scaled[1], W=exp_rect_scaled[0], E=W - exp_rect_scaled[2], S=H - exp_rect_scaled[3])
    edge = {sd: layers[sd]["edge"] for sd in "NESW"}
    side_ok, side_reasons, used = {}, {}, {}
    for sd in "NESW":
        lay_ok = layers[sd]["foam"] >= 0.3 * ck.BAND_FOAM * s and layers[sd]["corr"] >= 0.3 * ck.BAND_CORR * s
        dev_sd = abs(edge[sd] - exp_edge[sd])
        side_ok[sd] = bool(lay_ok and dev_sd <= 60 * s)
        if side_ok[sd]:
            used[sd] = edge[sd]
        else:
            used[sd] = exp_edge[sd]
            side_reasons[sd] = (f"層が読めない(foam={layers[sd]['foam']}px, corr={layers[sd]['corr']}px, 机={layers[sd]['desk']}px)" if not lay_ok
                                else f"期待から{dev_sd}px ずれ") + f" → 期待値 {exp_edge[sd]}px を使用"
    layers_ok = all(layers[sd]["foam"] >= 0.3 * ck.BAND_FOAM * s and layers[sd]["corr"] >= 0.3 * ck.BAND_CORR * s for sd in "NESW")
    rect_meas = (edge["W"], edge["N"], W - edge["E"], H - edge["S"])
    dev = max(abs(edge[sd] - exp_edge[sd]) for sd in "NESW")
    rect_ok = all(side_ok.values())
    rect = (used["W"], used["N"], W - used["E"], H - used["S"])
    # 位置合わせと GrabCut の範囲（rect_seg）は従来どおり全辺まとめて（4辺とも測れた時だけ測定値）。辺ごとに混ぜた rect を位置合わせに使うと
    # 変換が歪む画像があるため（BDY-03 で壁際の床が約760px 外れた）。links・出口の検出・喉の延長は辺ごとの rect を使う。
    rect_seg = rect_meas if (layers_ok and dev <= 60 * s) else exp_rect_scaled
    return dict(layers=layers, layers_ok=layers_ok, rect_meas=rect_meas, rect_exp=exp_rect_scaled, rect_ok=rect_ok,
                edge_dev_px=int(dev), side_ok=side_ok, side_reasons=side_reasons, rect=tuple(int(v) for v in rect),
                rect_seg=tuple(int(v) for v in rect_seg),
                desk_depth={sd: int(layers[sd]["desk"]) for sd in "NESW"})


def warp_mask(m, xf, W, H):
    return cv2.warpAffine(m.astype(np.uint8), xf.M.astype(np.float64), (W, H), flags=cv2.INTER_NEAREST) > 0


def floor_model(a, mk, xf, rect, s, fcol_est):
    """床の色モデル。チェッカーの床色推定（画像だけ）と、モック床の芯（初期変換で写し、通路幅の0.25だけ内側）の中央値を比べ、
    食い違えば（BDY-07 のように床より地形のクリーム系が広い画像）芯の色を採る。分布（共分散）は芯の画素から取る。"""
    H, W = a.shape[:2]
    wf = warp_mask(mk["floor"], xf, W, H)
    dt = ndi.distance_transform_edt(wf)
    dmax = np.percentile(dt[wf], 90) if wf.any() else 0
    core = dt >= min(0.3 * dmax, 40 * s)
    pix = a[core]
    if len(pix) < 500:
        return dict(fcol=fcol_est, source="estimate(core too small)", core_px=int(core.sum()), cov=None)
    med = np.median(pix, axis=0)
    src = "estimate"
    f = fcol_est
    if np.abs(med - fcol_est).sum() > 40:
        f = med
        src = "mock-core(estimate differed by %d)" % int(np.abs(med - fcol_est).sum())
    pix2 = pix[np.abs(pix - f).sum(-1) < 120]
    cov = np.cov(pix2.T) + np.eye(3) * 36.0 if len(pix2) > 200 else np.eye(3) * 400.0
    return dict(fcol=np.asarray(f, float), source=src, core_px=int(core.sum()), cov=cov, median_core=[int(v) for v in med])


def color_floor(a, fm, rect, s, thr=3.2):
    """床色モデル（平均+共分散）のマハラノビス距離で床らしさを測り、開閉→最大連結成分。"""
    H, W = a.shape[:2]
    x0, y0, x1, y1 = rect
    ic = np.linalg.inv(fm["cov"]) if fm["cov"] is not None else np.eye(3) / 400.0
    dv = (a - fm["fcol"]).reshape(-1, 3)
    md = np.sqrt(np.maximum(np.einsum("ij,jk,ik->i", dv, ic, dv), 0)).reshape(H, W)
    m = md < thr
    r, b = a[..., 0], a[..., 2]
    m &= (r - b > 30)
    inr = np.zeros((H, W), bool); inr[max(y0 - 3, 0):y1 + 3, max(x0 - 3, 0):x1 + 3] = True
    m &= inr
    m = ndi.median_filter(m.astype(np.uint8), size=5) > 0
    m = ndi.binary_opening(m, iterations=2)
    return ck.largest(m), md


def boundary(mask):
    return mask & ~ndi.binary_erosion(mask, iterations=1)


def mock_arrays(clean):
    eq = lambda c: ck.eq(clean, c)
    return dict(floor=eq(ck.CL_FLOOR), terrain=eq(ck.CL_TERRAIN), wall=eq(ck.CL_WALL), band=eq(ck.CL_BAND), desk=eq(ck.CL_DESK))


# ------------------------------------------------------------ 位置合わせ
def edge_endpoints(mask, rect, s, minlen_scale=20):
    """天面の縁に接する床の区間の両端（辺ごと）。戻り {side: [(x,y), ...]}（mask の座標系）。"""
    out = {}
    depth = max(4, int(round(4 * s)))
    for sd in "NESW":
        pts = []
        for a_, b_ in side_runs(mask, rect, sd, depth, max(8, int(round(minlen_scale * s)))):
            for v in (a_, b_):
                pts.append({"N": (v, rect[1]), "S": (v, rect[3] - 1), "W": (rect[0], v), "E": (rect[2] - 1, v)}[sd])
        out[sd] = pts
    return out


def register(img_floor, rect_img, mk, s, allowed=("T", "S")):
    """初期変換（天面 rect 合わせ）と、4つの自由度モデルでの chamfer 精密化。
    コスト = 床境界の chamfer（上位70%の平均、最大20px）+ 0.5 x 縁に届く床区間の両端の位置ずれ（最大30px）。
    後者が無いと、斜めの帯（脚・腕）が帯の向きに滑って合う（開口問題）。
    採る自由度は既定で T（平行移動）か S（+拡大 ±2%）まで。回転・縦横比（SR/A）は表に診断値として出すが、allowed に入れない限り採らない
    （真上から撮った画像で回転は物理的に無く、斜めの帯が1本しかない MAP では回転が『傾きの描き分け』を吸収して誤った一致になる）。"""
    H, W = img_floor.shape
    # 画像側: 床の境界までの距離（天面の縁そのものは人工の境界なので除く）
    bimg = boundary(img_floor)
    r = int(round(3 * s)) + 1
    x0, y0, x1, y1 = rect_img
    edge_zone = np.ones_like(bimg)
    edge_zone[y0 + r:y1 - r, x0 + r:x1 - r] = False
    bimg &= ~edge_zone
    dt = ndi.distance_transform_edt(~bimg)
    # モック側の境界点: 床と地形の境界。天面の縁・広間の壁との境界は除く
    mf = mk["floor"]
    bm = boundary(mf)
    near_wall = ndi.binary_dilation(mk["wall"], iterations=4)
    mx0, my0, mx1, my1 = MOCK_RECT
    inner = np.zeros_like(bm)
    inner[my0 + 3:my1 - 3, mx0 + 3:mx1 - 3] = True
    bm &= inner & ~near_wall
    ys, xs = np.nonzero(bm)
    pts = np.c_[xs, ys][::3].astype(float)
    cap = 20.0 * s
    mock_ep = edge_endpoints(mk["floor"], MOCK_RECT, 1.0)
    img_ep = edge_endpoints(img_floor, rect_img, s)
    ep_list = [(sd, np.array(p, float)) for sd in "NESW" for p in mock_ep[sd]]
    ep_img = {sd: np.array(img_ep[sd], float).reshape(-1, 2) for sd in "NESW"}

    def cost(p, model_idx, init_rect, full=False):
        q = np.zeros(5)
        q[model_idx] = p
        xf = make_xf(init_rect, q, None)
        t = xf.pts(pts)
        d = ndi.map_coordinates(dt, [t[:, 1], t[:, 0]], order=1, mode="nearest")
        d = np.minimum(d, cap)
        ds = np.sort(d)
        k = int(len(ds) * 0.7)
        c = ds[:k].mean()
        if ep_list:
            tp = xf.pts(np.array([p for _, p in ep_list]))
            e = []
            for (sd, _), q in zip(ep_list, tp):
                cand = ep_img[sd]
                e.append(min(np.hypot(*(cand - q).T).min() if len(cand) else 30 * s, 30 * s))
            c = c + 0.5 * float(np.mean(e))
        return (c, d) if full else c

    # 縮尺は天面の rect が決める物理量なので自由度を ±2%・回転 ±1度・縦横比 ±2% に縛る（縛らないと、通路の幅の描き分けを拡大縮小で吸収してしまう）
    scale = np.array([4 * s, 4 * s, 0.01, 0.4, 0.01])
    bounds_all = np.array([[-40 * s, 40 * s], [-40 * s, 40 * s], [-0.02, 0.02], [-2.5, 2.5], [-0.02, 0.02]])
    cand_rects = {"measured": rect_img}
    results = {}
    base_c, base_d = cost(np.zeros(0), [], rect_img, full=True)
    results["init"] = dict(params=[0.0] * 5, cost=float(base_c), d=base_d)
    for name, idx in MODELS.items():
        best = None
        for rn, rr in cand_rects.items():
            x0_ = np.zeros(len(idx))
            f = lambda z: cost(z * scale[idx], idx, rr)
            bnds = [(bounds_all[i][0] / scale[i], bounds_all[i][1] / scale[i]) for i in idx]
            # 多段（Powell は局所解に弱いので、平行移動の粗い格子を先に当てる）
            seeds = [np.zeros(len(idx))]
            for gx in (-12, -6, 6, 12):
                for gy in (-12, -6, 6, 12):
                    z = np.zeros(len(idx)); z[0] = gx * s / scale[0]; z[1] = gy * s / scale[1]
                    seeds.append(z)
            seeds.sort(key=lambda z: f(z))
            for z0 in seeds[:3]:
                rs = minimize(f, z0, method="Powell", bounds=bnds, options=dict(xtol=1e-3, ftol=1e-5, maxiter=2000))
                if best is None or rs.fun < best[0]:
                    best = (float(rs.fun), rs.x * scale[idx], rn)
        q = np.zeros(5); q[idx] = best[1]
        c, d = cost(best[1], idx, rect_img, full=True)
        results[name] = dict(params=[float(v) for v in q], cost=float(c), d=d)
    # 最小の自由度: 最良 cost に 0.4px 以内まで迫る最小モデル
    order = [n for n in ["T", "S", "SR", "A"] if n in allowed]
    best_c = min(results[n]["cost"] for n in order)
    chosen = next(n for n in order if results[n]["cost"] <= best_c + 0.4 * s)
    # init より悪化するなら init
    if results[chosen]["cost"] > results["init"]["cost"]:
        chosen = "init"
    return results, chosen, pts, bm


def residual_stats(d, s):
    inl = d < 12 * s
    return dict(points=int(len(d)), inlier_frac=round(float(inl.mean()), 4),
                inlier_mean_px=round(float(d[inl].mean()), 2) if inl.any() else None,
                inlier_max_px=round(float(d[inl].max()), 2) if inl.any() else None,
                all_mean_px=round(float(d.mean()), 2), p90_px=round(float(np.percentile(d, 90)), 2))


# ------------------------------------------------------------ 床の切り出し
# モック床の境界に沿う「画像のみ床」の細い縁取りを壁の帯（面取りの上面など）として捨てる処理の幅。旧は 7px(x倍率) = 幅<約14px を捨てており、
# 模型の縁際・壁際の本物の床（BDY-09 W の x129〜140、BDY-16 右・下の壁際 9〜10px、BDY-01 右上の丸い先端 7〜12px）まで削っていた。
# 壁の面取りの上面は 3〜4px 幅（BDY-04）なので、捨てるのは幅<約7px（3px x倍率）に絞る。BODY_SLIVER_K=7 で旧挙動、0 で無効。
import os
SLIVER_K_PX = float(os.environ.get("BODY_SLIVER_K", "3"))
DROP_THIN_SLIVER = SLIVER_K_PX > 0
def strict_floor_by_color(a, seed, s, thr=5.0, core_px=22, erode_px=1):
    """最終マスクの床は『床色基準』。GrabCut の結果(seed)は種の補助に留め、seed の芯（縁から core_px 以上内側）の色（中央値＋共分散）に
    近い画素だけを床とする。壁の足元の定義: 床（クリーム）の領域だけが床で、壁の帯（段ボール・毛糸）・面取りの斜面・影・地形・土台縁・机は床に入れない。
    手順: ① 芯の色からのマハラノビス距離 < thr ② median(5) と opening ③ 芯と連結する成分だけ残す ④ 小さな穴（床の汚れ）だけ埋める
    ⑤ 壁側へ erode_px(x倍率) 侵食（面取りのにじみ・影の端の半端な画素を blocked 側へ）。"""
    H, W = seed.shape
    dt = ndi.distance_transform_edt(seed)
    core = dt >= max(6, core_px * s)
    if core.sum() < 800:
        core = dt >= max(4, 0.5 * dt.max())
    pix = a[core]
    med = np.median(pix, axis=0)
    pix2 = pix[np.abs(pix - med).sum(-1) < 150]
    cov = np.cov(pix2.T) + np.eye(3) * 25.0
    ic = np.linalg.inv(cov)
    dv = (a - med).reshape(-1, 3)
    md = np.sqrt(np.maximum(np.einsum("ij,jk,ik->i", dv, ic, dv), 0)).reshape(H, W)
    close = md < thr
    close = ndi.median_filter(close.astype(np.uint8), size=5) > 0
    m = seed & close
    k = max(1, int(round(2 * s)))
    m = ndi.binary_opening(m, structure=np.ones((3, 3), bool), iterations=k)
    lab, n = ndi.label(m)
    if n:
        ov = ndi.sum(core, lab, range(1, n + 1))
        keep = np.zeros(n + 1, bool); keep[1:] = ov > 0
        m = keep[lab]
    holes = ndi.binary_fill_holes(m) & ~m
    hl, hn = ndi.label(holes)
    if hn:
        hs = ndi.sum(holes, hl, range(1, hn + 1))
        small = np.zeros(hn + 1, bool); small[1:] = hs < 600 * s * s
        m = m | small[hl]
    if erode_px:
        m = ndi.binary_erosion(m, iterations=max(1, int(round(erode_px * s))))
    lab, n = ndi.label(m)          # 飾りの切れ端（床色の小片）は床としない
    if n:
        sz = ndi.sum(m, lab, range(1, n + 1))
        keep = np.zeros(n + 1, bool); keep[1:] = sz >= 1500 * s * s
        m = keep[lab]
    return m, dict(color_floor_core_median=[int(v) for v in med], color_floor_thr=thr, color_floor_erode_px=erode_px,
                   color_strict_removed_from_grabcut_px=int((seed & ~m).sum())), md


def cut_floor(a, fm, wf, wt, ww, rect, s, iters=5):
    """位置合わせ済みモック(wf=床, wt=地形, ww=壁)を種に GrabCut で床を切り出す。
    種: 確実な床 = モック床を 18px(x倍率) 侵食 / 確実な地形 = 天面の外 / 床らしい = モック床の縁 / 地形らしい = それ以外の天面内。
    （モック地形を『確実』にしないのは、画像のほうが床が広い所＝構造差を拾えるようにするため。）
    後処理: ① 壁の帯（細い段ボール帯・面取りの明るい面）は blocked 側として、モック床の境界に沿う『画像のみ床』の細い縁取り（幅<約14px）を除く
            ② 床色の細かい飾り（ボタン・毛糸・粘土玉）は、モック床の芯と連結しない成分を捨てる。"""
    H, W = a.shape[:2]
    x0, y0, x1, y1 = rect
    inrect = np.zeros((H, W), bool); inrect[y0:y1, x0:x1] = True
    k_deep = max(3, int(round(18 * s)))
    deep = ndi.binary_erosion(wf, iterations=k_deep)
    m = np.full((H, W), cv2.GC_BGD, np.uint8)
    m[inrect] = cv2.GC_PR_BGD
    m[wf & inrect] = cv2.GC_PR_FGD
    m[deep & inrect] = cv2.GC_FGD
    # 色が床モデルから遠すぎる所は『床らしい』にしない（モック床が実画像の床と食い違う時、誤った芯が色モデルを汚さないため）
    ic = np.linalg.inv(fm["cov"]) if fm["cov"] is not None else np.eye(3) / 400.0
    dv = (a - fm["fcol"]).reshape(-1, 3)
    md = np.sqrt(np.maximum(np.einsum("ij,jk,ik->i", dv, ic, dv), 0)).reshape(H, W)
    m[(m == cv2.GC_PR_FGD) & (md > 7)] = cv2.GC_PR_BGD
    m[(m == cv2.GC_FGD) & (md > 9)] = cv2.GC_PR_FGD
    bgr = np.ascontiguousarray(a[..., ::-1].astype(np.uint8))
    bgdm, fgdm = np.zeros((1, 65)), np.zeros((1, 65))
    cv2.grabCut(bgr, m, None, bgdm, fgdm, iters, cv2.GC_INIT_WITH_MASK)
    gc = ((m == cv2.GC_FGD) | (m == cv2.GC_PR_FGD)) & inrect
    fin = ndi.binary_opening(gc, structure=np.ones((3, 3), bool), iterations=max(1, int(round(2 * s))))
    wf_core = ndi.binary_erosion(wf, iterations=max(2, int(round(5 * s))))
    lab, n = ndi.label(fin)
    if n:
        ov = ndi.sum(wf_core, lab, range(1, n + 1))
        keep = np.zeros(n + 1, bool)
        keep[1:] = ov > 0
        isolated = int(((~keep[1:]) & (ndi.sum(np.ones_like(lab), lab, range(1, n + 1)) > 600 * s * s)).sum())
        fin = keep[lab]
    else:
        isolated = 0
    k = max(2, int(round(SLIVER_K_PX * s)))
    only_img = fin & ~wf
    thick = ndi.binary_opening(only_img, structure=np.ones((2 * k + 1, 2 * k + 1), bool))
    thin = only_img & ~thick
    fin_raw = fin
    if DROP_THIN_SLIVER:
        fin = fin & ~thin
    fin_gc = fin
    fin, cinfo2, md_floor = strict_floor_by_color(a, fin, s)
    return fin, md_floor, dict(**cinfo2, grabcut_iters=iters, grabcut_after_sliver_px=int(fin_gc.sum()), seed_deep_px=int(deep.sum()), grabcut_floor_px=int(gc.sum()), isolated_floorlike_components_dropped=isolated,
                     wall_bevel_sliver_removed_px=int(thin.sum()), cut_before_sliver_px=int(fin_raw.sum()))


def _to_out_up(arr, sd):
    """辺 sd の『外向き』が配列の上方向（行が減る向き）になるように、配列を変換する（N: そのまま / S: 上下反転 / W: 転置 / E: 転置+上下反転）。"""
    return {"N": lambda m: m, "S": lambda m: m[::-1], "W": lambda m: m.T, "E": lambda m: m.T[::-1]}[sd](arr)


def _from_out_up(arr, sd):
    return {"N": lambda m: m, "S": lambda m: m[::-1], "W": lambda m: m.T, "E": lambda m: m[::-1].T}[sd](arr)


def extend_exit_throats(cut, md, rect, s, exit_sides, desk_depth, side_measured, passes=((5.0, 50, 45), (10.0, 0, 20)), out_px=60, a_out_px=4):
    """出口の喉: 出口（縁に届く床の区間）で、床色（床の芯の色からのマハラノビス距離 md < 閾値）が連続する所まで white にする。
    - 対象は仕様で出口のある辺だけ（出口以外の辺の white は 0 のまま）。
    - passes = (md の閾値, 出口の区間の左右へ許す幅 px, 縁から内側へ見る深さ px) を順に。1回目は床色（md<5。喉は床が斜めに広がるので左右へ50px）、
      2回目は出口の縁際だけ、影で暗くなった床（md<10。波形の帯の足元の影。区間の左右6px・縁から20px以内）まで。
      壁の帯・面取り・毛糸は md が桁違いに大きいのでここでも入らない。
    - A（縁の内側・縁ぎわ）: 床色の画素のうち既存の white と連結するもの（縁の外へは a_out_px まで）を足す。
    - B（縁の外側＝波形の帯の切れ目。1回目の md<5 のときだけ、かつその辺の rect が測定値のときだけ）: 列（辺に直交する線）ごとに、white の外端から
      外向きへ床色が途切れず続く所まで伸ばす。途切れず続く線だけなので、帯（床色でない）に塞がれた所や、帯の向こうの台紙の縁取り（床と同色）へは回り込まない。
      出口の幅は床の幅（切れ目の幅）に従う。rect が測れていない辺（期待値）は、縁の位置自体が不明で面取り・縁取りの床色の帯（BDY-05 W の x102〜125 など）を
      床と取り違えるので B をしない。
    - 模型の外へは出さない: B の先端が机の始まり（measure_layers の desk 深さ + 4px）に届く辺（床と台紙の縁取りが同色で区別できない）は、縁（rect）で止める。
    戻り (新しい cut, 出口ごとの情報)"""
    H, W = cut.shape
    x0, y0, x1, y1 = rect
    depth = max(10, int(round(30 * s)))
    pw_min = max(8, int(round(0.3 * 77 * s)))
    out_cut = cut.copy()
    info = []
    outp = int(round(out_px * s))
    runs_by_side = {sd: side_runs(cut, rect, sd, depth, pw_min) for sd in exit_sides}   # 出口の区間は最初の cut で決める
    edge_row = {"N": y0, "S": H - y1, "W": x0, "E": W - x1}     # 変換後の座標での、縁の最初の内側の行
    for pass_i, (thr, pad_px, in_px) in enumerate(passes):
        pad, inp = int(round(pad_px * s)), int(round(in_px * s))
        cand_all = ndi.median_filter((md < thr).astype(np.uint8), size=3) > 0
        for sd in exit_sides:
            if pass_i > 0 and not side_measured.get(sd):
                continue        # 影で暗い床まで広げる2回目は、縁（rect）を測れた辺だけ（測れていない辺は面取り・縁取りの帯を床と取り違える）
            cu = _to_out_up(out_cut, sd).copy()
            cd = _to_out_up(cand_all, sd)
            Hh, Ww = cu.shape
            e = edge_row[sd]
            for (a0, b0) in runs_by_side[sd]:
                la, lb = max(a0 - pad, 0), min(b0 + pad + 1, Ww)
                # A: 縁の内側（縁の外へは2pxまで）で、既存の white と連結する床色
                r0, r1 = max(e - (a_out_px if pass_i == 0 else 0), 0), min(e + inp, Hh)       # 影で暗い床(2回目 md<10)は縁の内側だけ（縁の外へ非床色を延ばさない）
                zone = np.zeros_like(cu); zone[r0:r1, la:lb] = True
                lab, n = ndi.label((cd & zone) | (cu & zone))
                newA = np.zeros_like(cu)
                if n:
                    seeds = np.unique(lab[cu & zone])
                    keep = np.zeros(n + 1, bool); keep[seeds[seeds > 0]] = True
                    newA = keep[lab] & ~cu
                cur = cu | newA
                # B: 縁の外側。列ごとに、white の外端から外向きに床色が続く所まで
                newB = np.zeros_like(cu)
                top_lim = max(e - outp, 0)
                for x in (range(la, lb) if (pass_i == 0 and side_measured.get(sd)) else ()):
                    col = cur[top_lim:r1, x]
                    if not col.any():
                        continue
                    r = top_lim + int(np.argmax(col))       # 最も外側の white の行
                    rr = r - 1
                    while rr >= top_lim and cd[rr, x]:
                        newB[rr, x] = True
                        rr -= 1
                # 切れ目の幅が出口の幅の2割（最小約20px）に満たない細い連なり（帯にかかったテープ・帯の欠けた隙間の床色）は、床の喉ではないので足さない
                lat = max(int(round(20 * s)), int(round(0.2 * (b0 - a0 + 1))))
                newB = ndi.binary_opening(newB, structure=np.ones((1, lat), bool))
                # 幅が約5px未満の突起（床色の偶然の連なり）は足さない
                new = newA | newB
                op = ndi.binary_opening(new | cu, structure=np.ones((3, 3), bool), iterations=2)
                new &= op
                lab2, n2 = ndi.label(new | cu)
                sd2 = np.unique(lab2[cu]); k2 = np.zeros(n2 + 1, bool); k2[sd2[sd2 > 0]] = True
                new &= k2[lab2]
                outer = np.zeros_like(cu); outer[:e] = True
                new_out = new & outer
                clipped = False
                if new_out.any():
                    tip = int(np.nonzero(new_out)[0].min())      # 変換後は外向き=上。行番号 = 画像の外縁からの距離
                    if desk_depth.get(sd, 0) > 0 and tip <= desk_depth[sd] + 4:
                        new &= ~outer
                        clipped = True
                        new_out = np.zeros_like(new_out)
                cu |= new
                info.append(dict(side=sd, run=[int(a0), int(b0)], md_thr=thr, added_px=int(new.sum()), added_beyond_edge_px=int(new_out.sum()),
                                 clipped_at_edge_because_floor_color_reaches_desk=clipped))
            out_cut = _from_out_up(cu, sd)
    return out_cut, info


def finalize_cut(cut, md, rect, s, a, base, exit_sides, nonfloor_md=5.0, hole_md=10.0, hole_max_px=100, nonfloor_md2=12.0):
    """喉の延長のあとの仕上げ（床色の定義に揃える）。戻り (cut, 情報)
    (0) 床の定義（床の芯の色＝延長前の white の芯の色。共分散も延長前の white から取った md2）が nonfloor_md2（12。検査の閾値 15 に余裕を持たせる）を超える white 画素を除く
        （延長の md<10 の許容が、影ではなく帯・壁の色〔例 RGB(167,123,81)〕まで拾った分と、縁際に残る帯・壁の色の点を落とす）
    (1') 出口の縁ぎわ（縁から内外12px）の幅5px未満の突起は開閉で落とす（足さない）
    (1) 模型の縁（rect）の外に出た white は、床の芯の色（md < nonfloor_md）の画素だけ残す（テープ・縁取り・帯の色は除く）。残りの white と連結しなくなった切れ端も除く
    (2) white に囲まれた小さな穴（<= hole_max_px×s²。縁の外にかかる穴は除く）は、穴の画素の md の中央値が hole_md 未満かつ md2 の最大が nonfloor_md2 以下（穴の全画素が床色）のときだけ埋める。床色でない穴（本物の島・飾り）は残す"""
    out = cut.copy()
    x0, y0, x1, y1 = rect
    H, W = cut.shape
    core = ndi.binary_erosion(base, iterations=max(6, int(round(22 * s))))
    if core.sum() < 800:
        core = base
    pix = a[core].astype(float)
    med = np.median(pix, axis=0)
    pix2 = pix[np.abs(pix - med).sum(-1) < 150]
    ic = np.linalg.inv(np.cov(pix2.T) + np.eye(3) * 25.0)
    dv = (a - med).reshape(-1, 3).astype(float)
    md2 = np.sqrt(np.maximum(np.einsum("ij,jk,ik->i", dv, ic, dv), 0)).reshape(H, W)
    far = out & (md2 > nonfloor_md2)
    out &= ~far
    outside = np.ones(cut.shape, bool); outside[y0:y1, x0:x1] = False
    bad = out & outside & (md >= nonfloor_md)
    out &= ~bad
    lab, n = ndi.label(out)
    dropped_islands = 0
    if n > 1:
        sz = ndi.sum(out, lab, range(1, n + 1))
        keep = np.zeros(n + 1, bool); keep[1 + int(np.argmax(sz))] = True
        dropped_islands = int(out.sum() - keep[lab].sum())
        out = keep[lab]
    # 出口の縁ぎわ（縁から内外 12px）の、幅 5px 未満の突起・ぎざぎざを開閉で落とす（出口の幅は100px以上。足すことはしない）
    strip = np.zeros(cut.shape, bool)
    for sd in exit_sides:
        if sd == "N":
            strip[max(y0 - 12, 0):y0 + 12, :] = True
        elif sd == "S":
            strip[y1 - 12:y1 + 12, :] = True
        elif sd == "W":
            strip[:, max(x0 - 12, 0):x0 + 12] = True
        else:
            strip[:, x1 - 12:x1 + 12] = True
    op = ndi.binary_opening(out, structure=np.ones((5, 5), bool))
    spur = out & strip & ~op
    out &= ~spur
    lab, n = ndi.label(out)
    if n > 1:
        sz = ndi.sum(out, lab, range(1, n + 1))
        keep = np.zeros(n + 1, bool); keep[1 + int(np.argmax(sz))] = True
        out = keep[lab]
    holes = ndi.binary_fill_holes(out) & ~out
    hl, hn = ndi.label(holes)
    filled, kept = [], []
    for i in range(1, hn + 1):
        hm = hl == i
        area = int(hm.sum())
        mmd = float(np.median(md[hm]))
        mmd2 = float(md2[hm].max())
        if area <= hole_max_px * s * s and mmd < hole_md and mmd2 <= nonfloor_md2 and not (hm & outside).any():
            out |= hm
            ys, xs = np.nonzero(hm)
            filled.append(dict(area_px=area, centroid=[int(xs.mean()), int(ys.mean())], md_median=round(mmd, 2), md2_max=round(mmd2, 2)))
        else:
            kept.append(area)
    return out, dict(edge_spur_removed_px=int(spur.sum()), nonfloor_md2_removed_px=int(far.sum()), nonfloor_md2_removed_from_pre_throat_white_px=int((far & base).sum()), nonfloor_removed_beyond_rect_px=int(bad.sum()), disconnected_dropped_px=dropped_islands, holes_filled=filled, holes_kept_area_px=kept,
                     rule="縁の外の white は md<%.0f のみ / 小さな穴は床色（md中央値<%.0f）のときだけ埋める" % (nonfloor_md, hole_md))


def diff_report(cut, wf, s, rect):
    both = cut & wf
    only_img = cut & ~wf
    only_mock = wf & ~cut
    # 細い境界のずれ（開閉で消える）と構造差を分ける
    k = max(3, int(round(7 * s)))
    se = np.ones((2 * k + 1, 2 * k + 1), bool)
    struct_img = ndi.binary_opening(only_img, structure=se)
    struct_mock = ndi.binary_opening(only_mock, structure=se)

    def comps(m, lim=6):
        lab, n = ndi.label(m)
        out = []
        for i in range(1, n + 1):
            ys, xs = np.nonzero(lab == i)
            if len(ys) < 300 * s * s:
                continue
            out.append(dict(area_px=int(len(ys)), bbox=[int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())],
                            centroid=[int(xs.mean()), int(ys.mean())]))
        out.sort(key=lambda c: -c["area_px"])
        return out[:lim]

    tot_mock = int(wf.sum())
    return dict(mock_floor_px=tot_mock, cut_floor_px=int(cut.sum()), both_px=int(both.sum()),
                iou=round(float(both.sum() / max((cut | wf).sum(), 1)), 4),
                only_image_px=int(only_img.sum()), only_mock_px=int(only_mock.sum()),
                only_image_pct_of_mock=round(100 * float(only_img.sum()) / max(tot_mock, 1), 2),
                only_mock_pct_of_mock=round(100 * float(only_mock.sum()) / max(tot_mock, 1), 2),
                structural_only_image_px=int(struct_img.sum()), structural_only_mock_px=int(struct_mock.sum()),
                structural_only_image=comps(struct_img), structural_only_mock=comps(struct_mock)), only_img, only_mock


def edge_bias(cut, wf, s):
    """モック床境界の点が、切り出した床の境界から何px ずれているかを、境界の向き（床から見て地形が N/S/E/W のどちら側か）別に
    符号付きで出す。+ = モックの床が画像の床より外へ張り出す（壁の面取り・影で床が欠ける側）、- = モックより画像の床が広い。"""
    sd = ndi.distance_transform_edt(~cut) - ndi.distance_transform_edt(cut)   # + = 画像の床の外
    g = cv2.GaussianBlur(wf.astype(np.float32), (0, 0), 3 * s)
    gy, gx = np.gradient(g)
    bm = boundary(wf)
    ys, xs = np.nonzero(bm)
    # 床の外向き法線 = -grad(床)
    nx, ny = -gx[ys, xs], -gy[ys, xs]
    out = {}
    names = {"S(下向きの縁)": (ny > 0) & (abs(ny) >= abs(nx)), "N(上向きの縁)": (ny < 0) & (abs(ny) >= abs(nx)),
             "E(右向きの縁)": (nx > 0) & (abs(nx) > abs(ny)), "W(左向きの縁)": (nx < 0) & (abs(nx) > abs(ny))}
    v = sd[ys, xs]
    for k, m in names.items():
        sel = m & (abs(v) < 25 * s)
        out[k] = dict(n=int(sel.sum()), mean_px=round(float(v[sel].mean()), 2) if sel.any() else None)
    return out


# ------------------------------------------------------------ 位相検査
def side_runs(mask, rect, side, depth, minlen):
    """天面の縁に接する床の区間。画像座標の (a,b)（辺に沿う座標）の列。"""
    x0, y0, x1, y1 = rect
    if side == "N":
        v = mask[y0:y0 + depth, x0:x1].any(0); off = x0
    elif side == "S":
        v = mask[y1 - depth:y1, x0:x1].any(0); off = x0
    elif side == "W":
        v = mask[y0:y1, x0:x0 + depth].any(1); off = y0
    else:
        v = mask[y0:y1, x1 - depth:x1].any(1); off = y0
    return [(a + off, b + off) for a, b in ck.runs_1d(v) if b - a + 1 >= minlen]


def slice_profile(mask, rect, n=10, minlen=6):
    """天面を縦横 n 分割した断面ごとの床の区間数。戻り {'h':[...], 'v':[...]}（h=水平線ごと, v=垂直線ごと）"""
    x0, y0, x1, y1 = rect
    h, v = [], []
    for i in range(1, n):
        y = int(y0 + (y1 - y0) * i / n)
        h.append(len([1 for a, b in ck.runs_1d(mask[y, x0:x1]) if b - a + 1 >= minlen]))
        x = int(x0 + (x1 - x0) * i / n)
        v.append(len([1 for a, b in ck.runs_1d(mask[y0:y1, x]) if b - a + 1 >= minlen]))
    return dict(h=h, v=v)


def exits_compare(cut, warped_mock, rect, s, geom, shift_px=0.0):
    """縁に届く床の区間（出口）を、画像（切り出した床）とモックで比べる。縁から depth（30px x 倍率。段ボール帯の下の影で床が縁から約10〜15px 離れる画像がある）以内に床があれば「届く」とみなす
    （縁と床の間に段ボールの細い帯が挟まる画像があるため）。モック側は変換の平行移動ぶん（shift_px）だけ深く見る。"""
    out = {}
    depth = max(10, int(round(30 * s)))
    pw = (geom or {}).get("passage_width_px", 77)
    minlen = max(8, int(round(0.3 * pw * s)))   # 通路幅の3割未満の区間は出口とみなさない（縁の毛糸・段ボールの切れ端）
    for sd in "NESW":
        ri = side_runs(cut, rect, sd, depth, minlen)
        rm = side_runs(warped_mock, rect, sd, max(10, int(round(16 * s))) + int(math.ceil(shift_px)) + 2, minlen)
        pairs = []
        used = set()
        for (a, b) in ri:
            best = None
            for j, (c, d_) in enumerate(rm):
                if j in used:
                    continue
                dc = abs((a + b) / 2 - (c + d_) / 2)
                if best is None or dc < best[0]:
                    best = (dc, j)
            if best:
                used.add(best[1])
                c, d_ = rm[best[1]]
                pairs.append(dict(image=[a, b], mock=[c, d_], center_shift_px=round((a + b) / 2 - (c + d_) / 2, 1),
                                  width_image=b - a + 1, width_mock=d_ - c + 1))
            else:
                pairs.append(dict(image=[a, b], mock=None))
        missing = [list(rm[j]) for j in range(len(rm)) if j not in used]
        exp_n = geom["topology_expect"]["exits_per_side"][sd] if geom else None
        out[sd] = dict(image_count=len(ri), mock_count=len(rm), spec_count=exp_n,
                       match=len(ri) == len(rm), pairs=pairs, mock_only=missing)
    return out


def components(cut, s):
    lab, n = ndi.label(cut)
    sizes = [int(v) for v in ndi.sum(cut, lab, range(1, n + 1))] if n else []
    sizes.sort(reverse=True)
    return dict(count=n, big_count=len([v for v in sizes if v > 1500 * s * s]), sizes_top=sizes[:6])


def holes_count(cut, rect, s):
    """床に囲まれた非床の島（環の中の島）の数。天面の外・縁に接する非床は数えない。"""
    x0, y0, x1, y1 = rect
    sub = np.zeros_like(cut); sub[y0:y1, x0:x1] = cut[y0:y1, x0:x1]
    inv = ~sub
    lab, n = ndi.label(inv)
    border = set(np.unique(np.r_[lab[0], lab[-1], lab[:, 0], lab[:, -1]]).tolist())
    cnt = 0
    for i in range(1, n + 1):
        if i in border:
            continue
        if (lab == i).sum() > 800 * s * s:
            cnt += 1
    # 縁に床が届く MAP では、天面の縁の外側が inv で外周と連結するので、縁で囲まれる島（模型内の島）は上の border に入らない
    return cnt


def rooms_check(cut, xf, geom, s):
    """モックの丸い部屋（中心・半径）を画像へ写し、その中心で床の内接円半径（距離変換）が半径の 0.75 倍以上あるかを見る。"""
    dt = ndi.distance_transform_edt(cut)
    sc = xf.decompose()["scale_x"]
    H, W = cut.shape
    rows = []
    for r in geom["rooms"]:
        c = xf.pts(r["center"]["px"])[0]
        x, y = int(round(c[0])), int(round(c[1]))
        v = float(dt[min(max(y, 0), H - 1), min(max(x, 0), W - 1)]) if 0 <= x < W and 0 <= y < H else 0.0
        # 中心付近(±40px)の最大値（部屋の中心がずれる場合）
        yy0, yy1, xx0, xx1 = max(y - 40, 0), min(y + 41, H), max(x - 40, 0), min(x + 41, W)
        vm = float(dt[yy0:yy1, xx0:xx1].max()) if yy1 > yy0 and xx1 > xx0 else 0.0
        exp_r = r["radius_px"] * sc
        rows.append(dict(name=r["name"], center_image_px=[round(float(c[0]), 1), round(float(c[1]), 1)], radius_expected_px=round(exp_r, 1),
                         inscribed_at_center_px=round(v, 1), inscribed_max_within_40px=round(vm, 1), present=bool(vm >= 0.75 * exp_r)))
    return dict(count_expected=len(rows), count_present=sum(1 for x in rows if x["present"]), rooms=rows)


def zhang_suen(img):
    """Zhang-Suen 細線化（0/1 配列、numpy のみ）。"""
    im = img.astype(np.uint8).copy()
    while True:
        changed = False
        for step in (0, 1):
            p = np.pad(im, 1)
            P2, P3, P4, P5 = p[:-2, 1:-1], p[:-2, 2:], p[1:-1, 2:], p[2:, 2:]
            P6, P7, P8, P9 = p[2:, 1:-1], p[2:, :-2], p[1:-1, :-2], p[:-2, :-2]
            nb = [P2, P3, P4, P5, P6, P7, P8, P9]
            B = sum(x.astype(int) for x in nb)
            seq = nb + [P2]
            A = sum(((seq[i] == 0) & (seq[i + 1] == 1)).astype(int) for i in range(8))
            if step == 0:
                c = (P2 * P4 * P6 == 0) & (P4 * P6 * P8 == 0)
            else:
                c = (P2 * P4 * P8 == 0) & (P2 * P6 * P8 == 0)
            rm = (im == 1) & (B >= 2) & (B <= 6) & (A == 1) & c
            if rm.any():
                im[rm] = 0
                changed = True
        if not changed:
            break
    return im.astype(bool)


def skeleton_path(mask, scale=0.5):
    """床マスク（1本の通路）の中心線。半分の解像度で細線化→端点から測地的に最遠の2点を結ぶ最長路。戻り: 画像座標の点列。"""
    sm = cv2.resize(mask.astype(np.uint8), None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA) > 0
    sk = zhang_suen(ndi.binary_closing(sm, iterations=1))
    ys, xs = np.nonzero(sk)
    if len(xs) < 5:
        return np.zeros((0, 2))
    idx = {(int(x), int(y)): i for i, (x, y) in enumerate(zip(xs, ys))}
    nbrs = [[] for _ in xs]
    for (x, y), i in idx.items():
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if (dx or dy) and (x + dx, y + dy) in idx:
                    nbrs[i].append(idx[(x + dx, y + dy)])

    def bfs(src):
        dist = {src: 0}; prev = {src: None}; q = [src]
        for u in q:
            for v in nbrs[u]:
                if v not in dist:
                    dist[v] = dist[u] + 1; prev[v] = u; q.append(v)
        far = max(dist, key=dist.get)
        return far, prev

    a0, _ = bfs(0)
    b0, prev = bfs(a0)
    path = []
    u = b0
    while u is not None:
        path.append((xs[u], ys[u])); u = prev[u]
    return np.array(path, float) / scale


def bend_count(path, width_px):
    """中心線の折れ点数: 近似多角形（許容 = 道幅の 0.08 倍）で、向きの変化 >= 12 度の頂点。戻り (数, 角度のリスト)。"""
    if len(path) < 10:
        return 0, []
    # 縁で切れた端はスケルトンが角へ曲がるので、端から道幅の1倍ぶんは見ない
    seg = np.r_[0, np.cumsum(np.hypot(*np.diff(path, axis=0).T))]
    keep = (seg >= width_px) & (seg <= seg[-1] - width_px)
    path = path[keep]
    if len(path) < 10:
        return 0, []
    eps = max(6.0, 0.08 * width_px)
    ap = cv2.approxPolyDP(path.astype(np.float32).reshape(-1, 1, 2), eps, False).reshape(-1, 2)
    angs = []
    for i in range(1, len(ap) - 1):
        v1, v2 = ap[i] - ap[i - 1], ap[i + 1] - ap[i]
        if np.hypot(*v1) < 0.6 * width_px or np.hypot(*v2) < 0.6 * width_px:
            continue
        t = math.degrees(math.atan2(v1[0] * v2[1] - v1[1] * v2[0], v1 @ v2))
        if abs(t) >= 12:
            angs.append(round(t, 1))
    return len(angs), angs


def maze_graph(maskimg, xf, geom, s):
    """BDY-04: モックの13x6格子を画像へ写し、セル・辺の開閉を床で判定。モックの木との差を辺単位で返す。"""
    mz = geom["maze"]
    cols, rows = mz["cols"], mz["rows"]
    pw = geom["passage_width_px"]
    cell = {(c, r): np.array(mz["cells"][f"{c},{r}"]["px"], float) for c in range(cols) for r in range(rows)}
    H, W = maskimg.shape

    def sample(p):
        x, y = int(round(p[0])), int(round(p[1]))
        return bool(maskimg[y, x]) if 0 <= x < W and 0 <= y < H else False

    def seg_frac(p, q):
        n = max(int(np.hypot(*(q - p)) / 4), 2)
        ts = np.linspace(0.18, 0.82, n)   # セル中心の円の部分は除く
        pts = xf.pts(np.array([p + (q - p) * t for t in ts]))
        return float(np.mean([sample(pt) for pt in pts]))

    open_cell = {k: float(np.mean([sample(xf.pts(v + np.array(o))[0]) for o in [(0, 0), (10, 0), (-10, 0), (0, 10), (0, -10)]])) for k, v in cell.items()}
    mock_edges = {tuple(sorted(map(tuple, e))) for e in mz["edges"]}
    img_edges = set()
    fr = {}
    for c in range(cols):
        for r in range(rows):
            for dc, dr in ((1, 0), (0, 1)):
                k2 = (c + dc, r + dr)
                if k2 in cell:
                    f = seg_frac(cell[(c, r)], cell[k2])
                    fr[((c, r), k2)] = f
                    if f >= 0.9:
                        img_edges.add(tuple(sorted([(c, r), k2])))
    missing = sorted(mock_edges - img_edges)
    extra = sorted(img_edges - mock_edges)
    adj = {}
    for a_, b_ in img_edges:
        adj.setdefault(a_, set()).add(b_); adj.setdefault(b_, set()).add(a_)
    root = tuple(mz["root_cell"])
    deg = {k: len(adj.get(k, ())) + (1 if k == root else 0) for k in cell}
    dead = sum(1 for v in deg.values() if v == 1)
    tj = sum(1 for v in deg.values() if v >= 3)
    corners = 0
    for k, n in adj.items():
        nn = list(n) + ([(k[0], k[1] + 1)] if k == root else [])
        if len(nn) == 2:
            a_, b_ = nn
            if (a_[0] - k[0], a_[1] - k[1]) != (k[0] - b_[0], k[1] - b_[1]):
                corners += 1
    # 連結・ループ
    seen, comp = set(), 0
    for k in cell:
        if k in seen or deg[k] == 0 and open_cell[k] < 0.5:
            continue
        comp += 1; st = [k]; seen.add(k)
        while st:
            u = st.pop()
            for v in adj.get(u, ()):
                if v not in seen:
                    seen.add(v); st.append(v)
    ambiguous = sorted([(list(k[0]), list(k[1]), round(v, 2)) for k, v in fr.items() if 0.6 <= v < 0.9])
    return dict(cells_open=int(sum(1 for v in open_cell.values() if v >= 0.5)), cells=len(cell),
                passages=len(img_edges), mock_passages=len(mock_edges), missing_vs_mock=[[list(a_), list(b_)] for a_, b_ in missing],
                extra_vs_mock=[[list(a_), list(b_)] for a_, b_ in extra], components=comp, loops=len(img_edges) - (len(adj) - comp) if adj else 0,
                dead_ends=dead, t_junctions=tj, corners=corners, ambiguous_edges=ambiguous[:8],
                spec=dict(passages=mz["edge_count"], dead_ends=geom["topology_expect"].get("dead_ends"),
                          t_junctions=geom["topology_expect"].get("t_junctions"), corners=geom["topology_expect"].get("corners")))


# ------------------------------------------------------------ NPC
def snap_to_floor(pt, floor, clearance_px):
    """pt（画像 px）を、床の内側で縁から clearance 以上離れた最寄りの点へ寄せる。戻り (新しい点, 寄せ距離px, 元の位置が床か)。"""
    dt = ndi.distance_transform_edt(floor)
    ok = dt >= clearance_px
    if not ok.any():
        ok = floor
    d2, idx = ndi.distance_transform_edt(~ok, return_indices=True)
    x, y = int(round(pt[0])), int(round(pt[1]))
    H, W = floor.shape
    x = min(max(x, 0), W - 1); y = min(max(y, 0), H - 1)
    ny, nx = idx[0][y, x], idx[1][y, x]
    return (int(nx), int(ny)), float(d2[y, x]), bool(ok[y, x])


def parse_npc(text):
    out = []
    for item in (text or "").split(";"):
        item = item.strip()
        if not item:
            continue
        name, _, uv = item.partition(":")
        u, v = uv.split(",")
        out.append((name.strip(), float(u), float(v)))
    return out


# ------------------------------------------------------------ 描画
def tint(o, mask, col, alpha):
    o[mask] = o[mask] * (1 - alpha) + np.array(col) * alpha


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("map_id")
    ap.add_argument("image")
    ap.add_argument("--out", required=True, help="出力ディレクトリ")
    ap.add_argument("--clean")
    ap.add_argument("--geometry", help="幾何JSON（既定: verification/body-layout/geometry/<MAP>.json）")
    ap.add_argument("--npc", help='"名前:u,v;名前:u,v"（u,v は模型の天面の比 0..1）')
    ap.add_argument("--clearance", type=float, default=12.0, help="NPCを寄せる時の床の縁からの最小距離（1920基準px）")
    ap.add_argument("--allow-rotation", action="store_true", help="回転・縦横比のモデル(SR/A)も採用候補にする（既定は T/S のみ）")
    ap.add_argument("--json-out")
    args = ap.parse_args()
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    mid = args.map_id
    clean_path = Path(args.clean) if args.clean else REPO / "verification/body-layout/clean" / f"{mid}.png"
    gpath = Path(args.geometry) if args.geometry else REPO / "verification/body-layout/geometry" / f"{mid}.json"
    geom = json.loads(gpath.read_text(encoding="utf-8")) if gpath.exists() else None
    img = Image.open(args.image).convert("RGB")
    W, H = img.size
    s = W / 1920.0
    a = np.asarray(img).astype(int)
    clean = np.asarray(Image.open(clean_path).convert("RGB")).astype(int)
    mk = mock_arrays(clean)
    exp_rect_scaled = tuple(int(round(v * s)) for v in MOCK_RECT)
    res = dict(map=mid, image=str(args.image), size=[W, H], scale_vs_1920=round(s, 5))

    # (a) 画像: 天面 rect と床色モデル
    im = extract_rect(a, s, exp_rect_scaled)
    rect_links = im["rect"]            # 辺ごとの測定 rect（出口・links・喉の延長）
    rect = im["rect_seg"]              # 位置合わせ・切り出し用
    m14 = int(round(14 * s))
    fcol_est, fok, fpx = ck.estimate_floor_color(a, (exp_rect_scaled[0] + m14, exp_rect_scaled[1] + m14, exp_rect_scaled[2] - m14, exp_rect_scaled[3] - m14))
    xf0 = make_xf(rect, np.zeros(5), None)
    # (b) 位置合わせ（2パス: 初期変換で床色モデルを作る→照合→その変換で床色モデルを作り直す→照合）。切り出し(GrabCut)の結果は使わない（循環を避ける）
    fm = floor_model(a, mk, xf0, rect, s, fcol_est)
    img_floor, _md = color_floor(a, fm, rect, s)
    results, chosen, pts, bm = register(img_floor, rect, mk, s, allowed=(('T', 'S', 'SR', 'A') if args.allow_rotation else ('T', 'S')))
    xf1 = make_xf(rect, np.array(results[chosen]["params"]), None)
    fm = floor_model(a, mk, xf1, rect, s, fcol_est)
    img_floor, _md = color_floor(a, fm, rect, s)
    results, chosen, pts, bm = register(img_floor, rect, mk, s, allowed=(('T', 'S', 'SR', 'A') if args.allow_rotation else ('T', 'S')))
    res["image_measure"] = dict(rect_measured=list(map(int, im["rect_meas"])), rect_expected_scaled=list(exp_rect_scaled), rect_used=list(rect_links), rect_used_for_registration=list(rect),
                                layers_ok=bool(im["layers_ok"]), rect_ok=bool(im["rect_ok"]), edge_dev_px=im["edge_dev_px"],
                                side_measured_ok=im["side_ok"], side_fallback_reasons=im["side_reasons"], desk_depth_px=im["desk_depth"],
                                floor_color=[int(v) for v in fm["fcol"]], floor_color_source=fm["source"],
                                floor_color_checker_estimate=[int(v) for v in fcol_est], floor_color_estimated_ok=bool(fok),
                                floor_px_color_only=int(img_floor.sum()))
    tab = {}
    for n in ["init", "T", "S", "SR", "A"]:
        r_ = results[n]
        tab[n] = dict(params=dict(zip(["dx", "dy", "dlogs", "drot_deg", "dlog_aniso"], [round(v, 4) for v in r_["params"]])),
                      cost_px_incl_endpoint_term=round(r_["cost"], 2), **residual_stats(r_["d"], s))
    xf = make_xf(rect, np.array(results[chosen]["params"]), None)
    d_ch = results[chosen]["d"]
    st = residual_stats(d_ch, s)
    inl = st["inlier_frac"]
    conf = "HIGH" if inl >= 0.80 and (st["inlier_mean_px"] or 99) <= 4.0 * s else ("MID" if inl >= 0.5 else "LOW")
    res["registration"] = dict(chosen_model=chosen, models=tab, transform=xf.decompose(), matrix_mock_to_image=[[round(float(v), 6) for v in row] for row in xf.M],
                               residual=st, confidence=conf,
                               confidence_note="residual=モック床境界点→画像の床（色だけで抽出）の境界までの距離。inlier=12px(x倍率)以内の割合。HIGH: inlier>=0.80 かつ平均<=4px(x倍率) / MID: >=0.5 / LOW: それ未満")

    # 位置合わせ後のモック
    wf, wt, ww = (warp_mask(mk[k], xf, W, H) for k in ("floor", "terrain", "wall"))
    inr = np.zeros((H, W), bool); inr[rect[1]:rect[3], rect[0]:rect[2]] = True
    wf &= inr

    # (d) 床の切り出し（GrabCut）
    cut, md_floor, cinfo = cut_floor(a, fm, wf, wt, ww, rect, s)
    exit_sides = sorted({e["side"] for e in geom["exits"]}) if geom else list("NESW")
    before_ext = int(cut.sum())
    cut_pre_throat = cut.copy()
    np.save(out / f"{mid}-md-floor.npy", md_floor.astype(np.float16))   # 床の芯の色からのマハラノビス距離（検査・比較用）
    Image.fromarray((cut * 255).astype(np.uint8)).save(out / f"{mid}-floor-cut-pre-throat.png")
    cut, throat = extend_exit_throats(cut, md_floor, rect_links, s, exit_sides, im["desk_depth"], im["side_ok"])
    cut, fin_info = finalize_cut(cut, md_floor, rect_links, s, a, cut_pre_throat, exit_sides)
    rect = rect_links
    cinfo["exit_throat_extension"] = dict(sides=exit_sides, added_px=int(cut.sum()) - before_ext, exits=throat, finalize=fin_info)
    Image.fromarray((cut * 255).astype(np.uint8)).save(out / f"{mid}-floor-cut.png")
    res["floor_cut"] = dict(info=cinfo, color_only_px=int(img_floor.sum()))
    dr, only_img, only_mock = diff_report(cut, wf, s, rect)
    res["floor_diff_vs_mock"] = dr
    res["edge_bias_signed_px"] = edge_bias(cut, wf, s)

    # (e) 位相
    topo = {}
    topo["components"] = components(cut, s)
    topo["mock_components"] = components(wf, s)
    _tp = res["registration"]["transform"]
    _sh = max(abs(results[chosen]["params"][0]), abs(results[chosen]["params"][1]))
    topo["exits"] = exits_compare(cut, wf, rect, s, geom, shift_px=_sh)
    topo["slice_profile_image"] = slice_profile(cut, rect)
    topo["slice_profile_mock"] = slice_profile(wf, rect)
    sp_i, sp_m = topo["slice_profile_image"], topo["slice_profile_mock"]
    topo["slice_profile_mismatch"] = dict(h=[i + 1 for i, (p, q) in enumerate(zip(sp_i["h"], sp_m["h"])) if p != q],
                                          v=[i + 1 for i, (p, q) in enumerate(zip(sp_i["v"], sp_m["v"])) if p != q],
                                          note="断面 i/10 の位置（h=水平線のi/10の高さ, v=垂直線のi/10の幅）で床の区間数がモックと違う所")
    if mid == "BDY-04" and geom and "maze" in geom:
        topo["maze_grid"] = maze_graph(cut, xf, geom, s)
    if mid in ("BDY-01", "BDY-09", "BDY-12", "BDY-05", "BDY-07", "BDY-10", "BDY-13", "BDY-06", "BDY-08", "BDY-11", "BDY-14"):
        pw = (geom["passage_width_px"] if geom else 230) * s * xf.decompose()["scale_x"] / s
        pi_, pm_ = skeleton_path(cut), skeleton_path(wf)
        bi, ai = bend_count(pi_, pw)
        bm_, am_ = bend_count(pm_, pw)
        topo["bends"] = dict(image=bi, image_turn_deg=ai, mock=bm_, mock_turn_deg=am_, spec=(geom or {}).get("topology_expect", {}).get("bends"),
                             centerline_len_image_px=int(np.hypot(*np.diff(pi_, axis=0).T).sum()) if len(pi_) > 1 else 0,
                             centerline_len_mock_px=int(np.hypot(*np.diff(pm_, axis=0).T).sum()) if len(pm_) > 1 else 0)
        res["_skeleton"] = [pi_.tolist()[::6], pm_.tolist()[::6]]
    topo["holes"] = holes_count(cut, rect, s)
    topo["holes_spec"] = {"BDY-15": 0, "BDY-16": 1, "BDY-17": 1}.get(mid)
    if geom and geom.get("rooms"):
        topo["rooms"] = rooms_check(cut, xf, geom, s)
    res["topology"] = topo

    # (f) NPC
    npcs = parse_npc(args.npc)
    if npcs:
        x0, y0, x1, y1 = MOCK_RECT
        rows = []
        for name, u, v in npcs:
            mp = (x0 + u * (x1 - x0), y0 + v * (y1 - y0))
            ip = xf.pts(mp)[0]
            sp, dist, was_ok = snap_to_floor(ip, cut, args.clearance * s)
            rows.append(dict(name=name, ratio=[u, v], mock_px=[round(mp[0], 1), round(mp[1], 1)], image_px=[round(float(ip[0]), 1), round(float(ip[1]), 1)],
                             snapped_px=list(sp), snap_distance_px=round(dist, 1), already_on_floor=was_ok,
                             snapped_ratio=[round((sp[0] - rect[0]) / (rect[2] - rect[0]), 4), round((sp[1] - rect[1]) / (rect[3] - rect[1]), 4)]))
        res["npc"] = rows

    # 描画: 重ね画像
    base = a.astype(float)
    o = base.copy()
    tint(o, wf, (40, 90, 255), 0.38)
    bd = boundary(wf)
    bd = ndi.binary_dilation(bd, iterations=max(1, int(round(1.2 * s))))
    o[bd] = (255, 235, 0)
    cv2.rectangle(o, (rect[0], rect[1]), (rect[2] - 1, rect[3] - 1), (255, 0, 255), 2)
    Image.fromarray(np.clip(o, 0, 255).astype(np.uint8)).save(out / f"{mid}-overlay.png")
    # 差分
    o = base * 0.55
    tint(o, cut & wf, (0, 200, 0), 0.55)
    tint(o, wf & ~cut, (255, 0, 0), 0.6)
    tint(o, cut & ~wf, (0, 90, 255), 0.6)
    Image.fromarray(np.clip(o, 0, 255).astype(np.uint8)).save(out / f"{mid}-diff.png")
    # 位相図
    o = np.clip(base * 0.5, 0, 255)
    tint(o, cut, (255, 255, 255), 0.45)
    ti = Image.fromarray(o.astype(np.uint8)); dd = ImageDraw.Draw(ti)
    for sd in "NESW":
        for pr in topo["exits"][sd]["pairs"]:
            aa, bb = pr["image"]
            box = {"N": [aa, rect[1] - 8, bb, rect[1] + 10], "S": [aa, rect[3] - 10, bb, rect[3] + 8],
                   "W": [rect[0] - 8, aa, rect[0] + 10, bb], "E": [rect[2] - 10, aa, rect[2] + 8, bb]}[sd]
            dd.rectangle(box, outline=(0, 255, 120) if pr["mock"] else (255, 120, 0), width=4)
        for (aa, bb) in topo["exits"][sd]["mock_only"]:
            box = {"N": [aa, rect[1] - 8, bb, rect[1] + 10], "S": [aa, rect[3] - 10, bb, rect[3] + 8],
                   "W": [rect[0] - 8, aa, rect[0] + 10, bb], "E": [rect[2] - 10, aa, rect[2] + 8, bb]}[sd]
            dd.rectangle(box, outline=(255, 0, 0), width=4)
    if "_skeleton" in res:
        for pl, col in zip(res["_skeleton"], ((0, 255, 255), (255, 0, 255))):
            if len(pl) > 1:
                dd.line([tuple(p) for p in pl], fill=col, width=4)
    if "maze_grid" in topo:
        mz = geom["maze"]
        for k, v in mz["cells"].items():
            p = xf.pts(v["px"])[0]
            dd.ellipse([p[0] - 4, p[1] - 4, p[0] + 4, p[1] + 4], fill=(255, 220, 0))
        for e in topo["maze_grid"]["missing_vs_mock"] + topo["maze_grid"]["extra_vs_mock"]:
            pa = xf.pts(mz["cells"][f"{e[0][0]},{e[0][1]}"]["px"])[0]; pb = xf.pts(mz["cells"][f"{e[1][0]},{e[1][1]}"]["px"])[0]
            col = (255, 0, 0) if e in topo["maze_grid"]["missing_vs_mock"] else (0, 120, 255)
            dd.line([tuple(pa), tuple(pb)], fill=col, width=6)
    if npcs:
        for r_ in res["npc"]:
            p = r_["image_px"]; q = r_["snapped_px"]
            dd.line([tuple(p), tuple(q)], fill=(255, 255, 0), width=3)
            dd.ellipse([p[0] - 6, p[1] - 6, p[0] + 6, p[1] + 6], outline=(255, 0, 0), width=3)
            dd.ellipse([q[0] - 8, q[1] - 8, q[0] + 8, q[1] + 8], fill=(0, 255, 0))
            dd.text((q[0] + 10, q[1] - 6), r_["name"], fill=(255, 255, 255))
    ti.save(out / f"{mid}-topology.png")
    res.pop("_skeleton", None)
    js = json.dumps(res, ensure_ascii=False, indent=1)
    (out / f"{mid}-register.json").write_text(js + "\n", encoding="utf-8")
    if args.json_out:
        Path(args.json_out).write_text(js + "\n", encoding="utf-8")
    r = res["registration"]
    print(f"{mid} model={r['chosen_model']} conf={r['confidence']} inlier={r['residual']['inlier_frac']} mean={r['residual']['inlier_mean_px']}px max={r['residual']['inlier_max_px']}px "
          f"IoU={dr['iou']} only_img={dr['only_image_pct_of_mock']}% only_mock={dr['only_mock_pct_of_mock']}% comps={topo['components']['count']}")
    print("out:", out)


if __name__ == "__main__":
    main()
