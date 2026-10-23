"""斜め視点（寺町 TRM-02〜05 の採用画像）の位置合わせ: 床の4点 → 平面図のホモグラフィ（3×3）。

入力: 入力JSON（MAP ID・部屋ごとの床の4点・平面図の縦横比）と採用画像。
出力: DIR/<MAP>-oblique-register.json（行列・検証）、DIR/<MAP>-<room>-plan.png（平面図への逆射影）。
画像は生成しない。同じ入力なら同じ画素・同じJSON（乱数なし）。

検証の区別（出力の `independence` 欄）:
  circular     縦横比を既知の円（source=circle:<id>）から決めたとき、その円の真円度は定義上ほぼ0%
               になる循環検証。縦横比の証拠にならない。
  independent  縦横比を台帳・設計書の寸法（source=ledger）から決めたときの円の真円度。縦横比の独立検証。
  quad-only    床板・舞台前縁の水平／継ぎ目の垂直。縦横比には依らず、床の4点だけを検証する
               （縦横比の独立検証にはならない）。
複数の部屋（rooms）は部屋ごとに別のホモグラフィ。床の高さが違う帯は別の room として書く。
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # python3 -I は script dir を足さない

import cv2
import numpy as np
from scipy import ndimage as ndi

from oblique_common import (SCHEMA_REGISTER, apply_h, jdump, load_input, plan_size, read_image,
                            room_homography, sha256_file, table)

CIRCLE_TOL_PCT = 5.0
LINE_TOL_DEG = 1.0


def circle_check(room, c, H, Hi, pw, ph):
    """外形の点 → 平面図 → 外接矩形の縦横比と、面積モーメントの軸比。implied_aspect は真円になる縦横比。"""
    P = apply_h(H, c["outline"])
    poly = P.astype(np.float32).reshape(-1, 1, 2)
    bw = float(np.ptp(P[:, 0])); bh = float(np.ptp(P[:, 1]))
    # 輪郭の面積モーメント（多角形を平面図の画素に塗って二次モーメント）
    cnv = np.zeros((ph, pw), np.uint8)
    cv2.fillPoly(cnv, [np.int32(np.round(P))], 1)
    ys, xs = np.nonzero(cnv)
    ev = np.linalg.eigvalsh(np.cov(np.stack([xs, ys])))
    mom = float(np.sqrt(ev[1] / ev[0]))
    bbox = max(bw, bh) / min(bw, bh)
    # 真円になる縦横比: v 方向を s 倍すると真円 → s = bw/bh（外接矩形）。plan_h を s 倍 = aspect を 1/s 倍
    a0 = float(room["plan_aspect"]["w_over_h"])
    implied = a0 * bh / bw
    src = room["plan_aspect"].get("source", "")
    circ = src == f"circle:{c['id']}"
    return {
        "id": c["id"], "plan_bbox_wh": [round(bw, 1), round(bh, 1)],
        "err_pct_bbox": round((bbox - 1) * 100, 2), "err_pct_moments": round((mom - 1) * 100, 2),
        "implied_aspect_w_over_h": round(implied, 3),
        "independence": "circular" if circ else "independent",
        "pass": bool(abs(bbox - 1) * 100 <= CIRCLE_TOL_PCT) if not circ else None,
        "note": ("縦横比をこの円から決めたため循環検証（縦横比の証拠にならない）" if circ
                 else f"縦横比は台帳・設計書由来。円から逆算した縦横比は {implied:.3f}"),
    }


def line_check(ln, H):
    P = apply_h(H, ln["points"])
    k = np.polyfit(P[:, 0], P[:, 1], 1)
    ang = float(np.degrees(np.arctan(k[0])))
    res = float(np.std(P[:, 1] - np.polyval(k, P[:, 0])))
    kind = ln.get("kind", "horizontal")
    dev = ang if kind == "horizontal" else None
    if kind == "vertical":
        k2 = np.polyfit(P[:, 1], P[:, 0], 1)
        dev = float(np.degrees(np.arctan(k2[0])))
    return {"id": ln["id"], "kind": kind, "plan_dev_deg": round(dev, 2), "resid_px": round(res, 2),
            "n": len(P), "independence": "quad-only", "pass": bool(abs(dev) <= LINE_TOL_DEG)}


def floor_lines_auto(im, room, H, plan, pw, ph):
    """平面図上の長い水平線（床板）と短い垂直線（継ぎ目）の角度の中央値。家具の線は中央値で薄まる。"""
    quad = np.zeros(plan.shape[:2], np.uint8)
    valid = ndi.binary_erosion(np.ones((ph, pw), bool), iterations=25)
    gp = cv2.cvtColor(plan, cv2.COLOR_BGR2GRAY)
    lsd = cv2.createLineSegmentDetector(cv2.LSD_REFINE_STD)
    ls = lsd.detect(gp)[0]
    hs, vs = [], []
    if ls is not None:
        for l in ls.reshape(-1, 4):
            dx, dy = l[2] - l[0], l[3] - l[1]
            L = float(np.hypot(dx, dy)); an = float(np.degrees(np.arctan2(dy, dx)))
            mx, my = int((l[0] + l[2]) / 2), int((l[1] + l[3]) / 2)
            if not valid[min(max(my, 0), ph - 1), min(max(mx, 0), pw - 1)]:
                continue
            h = ((an + 90) % 180) - 90
            if L >= 80 and abs(h) < 12:
                hs.append(h)
            v = (an % 180) - 90
            if 14 <= L <= 70 and abs(v) < 20:
                vs.append(v)
    def st(a, gate=True):
        if not a:
            return None
        a = np.array(a); m = float(np.median(a))
        return {"n": len(a), "median_deg": round(m, 2), "mad_deg": round(float(np.median(np.abs(a - m))), 2),
                "independence": "quad-only", "pass": bool(abs(m) <= LINE_TOL_DEG) if gate else None}
    # 継ぎ目は短くノイズが大きい（E1 でも MAD 5度）ため参考値。判定には使わない
    return {"planks_horizontal": st(hs), "seams_vertical": st(vs, gate=False)}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", help="入力JSON（sit-oblique-input/1）")
    ap.add_argument("--image", required=True, help="採用画像（PNG/WebP。寸法は入力JSONの image.expected_size と一致）")
    ap.add_argument("--out", required=True, help="出力ディレクトリ（register.json と平面図PNG）")
    a = ap.parse_args()
    d = load_input(a.input)
    im = read_image(a.image)
    h, w = im.shape[:2]
    exp = d.get("image", {}).get("expected_size")
    if exp and [w, h] != exp:
        sys.exit(f"画像寸法 {w}x{h} が期待 {exp} と違う（拡縮して合わせない）")
    os.makedirs(a.out, exist_ok=True)
    rooms_out, rows = [], []
    for room in d["rooms"]:
        H, Hi, pw, ph = room_homography(room)
        plan = cv2.warpPerspective(im, H, (pw, ph), flags=cv2.INTER_CUBIC)
        pth = os.path.join(a.out, f"{d['map_id']}-{room['id']}-plan.png")
        cv2.imwrite(pth, plan)
        circles = [circle_check(room, c, H, Hi, pw, ph) for c in room.get("circles", [])]
        lines = [line_check(l, H) for l in room.get("lines", [])]
        auto = floor_lines_auto(im, room, H, plan, pw, ph) if room.get("floor_lines_auto", True) else {}
        indep = any(c["independence"] == "independent" for c in circles)
        rooms_out.append({
            "id": room["id"], "quad": room["quad"], "plan_size": [pw, ph],
            "plan_aspect": room["plan_aspect"], "H_img_to_plan": H.tolist(), "H_plan_to_img": Hi.tolist(),
            "plan_image": os.path.basename(pth), "circles": circles, "lines": lines, "floor_lines_auto": auto,
            "aspect_verified_independently": indep,
        })
        for c in circles:
            rows.append((room["id"], f"円 {c['id']}", f"{c['err_pct_bbox']:+.2f}%(矩形)/{c['err_pct_moments']:+.1f}%(モーメント)",
                         c["independence"], "-" if c["pass"] is None else ("PASS" if c["pass"] else "FAIL")))
        for l in lines:
            rows.append((room["id"], f"線 {l['id']}", f"{l['plan_dev_deg']:+.2f}deg 残差{l['resid_px']}px", l["independence"],
                         "PASS" if l["pass"] else "FAIL"))
        for k, v in auto.items():
            if v:
                rows.append((room["id"], f"自動 {k}", f"中央値{v['median_deg']:+.2f}deg MAD{v['mad_deg']} n={v['n']}",
                             v["independence"], "-" if v["pass"] is None else ("PASS" if v["pass"] else "FAIL")))
        if not indep:
            rows.append((room["id"], "縦横比", f"{room['plan_aspect']['w_over_h']}:1 source={room['plan_aspect'].get('source')}",
                         "-", "独立検証なし"))
    res = {"schema": SCHEMA_REGISTER, "map_id": d["map_id"],
           "image": {"path": os.path.basename(a.image), "sha256": sha256_file(a.image), "size": [w, h]},
           "input_sha256": sha256_file(a.input), "rooms": rooms_out}
    rp = os.path.join(a.out, f"{d['map_id']}-oblique-register.json")
    jdump(res, rp)
    print(f"{d['map_id']} register: 部屋{len(rooms_out)}")
    print(table([tuple(map(str, r)) for r in rows], ("room", "検査", "値", "区分", "判定")))
    print(f"詳細: {rp}")


if __name__ == "__main__":
    main()
