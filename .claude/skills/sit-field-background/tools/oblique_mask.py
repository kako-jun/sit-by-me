"""斜め視点の床マスク・出口・NPC。oblique_register.py の出力（行列）を使う。画像を生成しない。

出力（--out DIR）:
  <MAP>-oblique-traversal-edit.png  画像と同寸のフラット塗り（sit-field-mask の edit PNG 形式）
                                    white=床 / black=blocked / orange #FF9D00=assist（既定0画素）
  <MAP>-oblique-mask.png            white のみ（車椅子でも通れる）
  <MAP>-oblique-mask-overlay.png    確認用の重ね画像（使い捨て。緑=white・赤=blocked・橙=assist）
  <MAP>-oblique-result.json         判定・数値の詳細
--masks-dir を付けると、edit・mask を可逆WebP、overlay を非可逆WebP(q85)で
<MAP>-{traversal-edit,mask,mask-overlay}.webp として書く（体内 BDY-NN と同じ名前の型）。

方針（kako-jun 決定 #144）:
  * 床は Lab のマハラノビス距離（床の芯の色から）。RGB は使わない。
  * 家具は「床色でない連結成分」を閉じて穴埋めし膨張して black。凸包は使わない。
  * blocked は入力JSONの多角形で手動追加（舞台など）。assist は入力JSONの assist 多角形だけ。
  * 出口は設計書が正本。位置が設計書に無い（status=TBD）出口は検査せず TBD と出す。絵から読まない。
    位置が決まったものは範囲が床マスクの縁（white と非white の境）に接することを検査する。
  * NPC は平面座標(u,v)→絵へ射影→床マスク上で縁から12px以上内側の最寄り点へ寄せ、寄せ距離を返す。
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # python3 -I は script dir を足さない

import cv2
import numpy as np
from scipy import ndimage as ndi
from scipy.spatial import cKDTree

from oblique_common import (SCHEMA_RESULT, apply_h, jdump, load_input, poly_mask, read_image,
                            room_homography, sha256_file, table, uv_to_img)

ORANGE = (255, 157, 0)  # RGB
EDGE_CLEAR_PX = 12


def room_floor(im, room, blocked_mask, fl):
    """部屋1つ分の床（white 候補）。戻り値: (white, info)。"""
    H, W = im.shape[:2]
    quad = poly_mask(im.shape, room["quad"])
    lab = cv2.cvtColor(im, cv2.COLOR_BGR2LAB).astype(np.float32)
    core_ok = ndi.binary_erosion(quad, iterations=int(fl.get("core_erode", 25))) & ~blocked_mask
    hs = fl.get("core_hsv")
    if hs:
        hv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV).astype(np.int32)
        core_ok &= ((hv[..., 0] >= hs["h"][0]) & (hv[..., 0] <= hs["h"][1]) & (hv[..., 1] >= hs["s_min"])
                    & (hv[..., 2] >= hs["v"][0]) & (hv[..., 2] <= hs["v"][1]))
    pix = lab[core_ok]
    if len(pix) < 500:
        sys.exit(f"room {room['id']}: 床の芯の画素が少なすぎる({len(pix)})。core_hsv か quad を見直す")
    med = np.median(pix, axis=0)
    pix2 = pix[np.abs(pix - med).sum(-1) < 60]
    cov = np.cov(pix2.T) + np.eye(3) * float(fl.get("reg", 2.0))
    ic = np.linalg.inv(cov)
    dv = (lab - med).reshape(-1, 3)
    md = np.sqrt(np.maximum(np.einsum("ij,jk,ik->i", dv, ic, dv), 0)).reshape(H, W)
    thr = float(fl.get("thr", 5.0))
    close = ndi.median_filter((md < thr).astype(np.uint8), size=5) > 0
    m = close & quad & ~blocked_mask
    m = ndi.binary_opening(m, np.ones((3, 3), bool), iterations=2)
    lb, n = ndi.label(m)
    ov = ndi.sum(core_ok, lb, range(1, n + 1))
    keep = np.zeros(n + 1, bool); keep[1:] = ov > 0; m = keep[lb]
    holes = ndi.binary_fill_holes(m) & ~m
    hl, hn = ndi.label(holes)
    hsz = ndi.sum(holes, hl, range(1, hn + 1))
    small = np.zeros(hn + 1, bool); small[1:] = hsz < int(fl.get("hole_fill_max", 300)); m |= small[hl]
    m = ndi.binary_erosion(m, iterations=1)
    lb, n = ndi.label(m)
    sz = ndi.sum(m, lb, range(1, n + 1))
    keep = np.zeros(n + 1, bool); keep[1:] = sz >= int(fl.get("min_component", 1500)); floor = keep[lb]
    # 家具: 床でない連結成分を閉じて穴埋め→膨張（凸包は使わない）
    nonfloor = ndi.binary_opening(quad & ~floor & ~blocked_mask, np.ones((3, 3), bool))
    nl, nn = ndi.label(nonfloor)
    furn = np.zeros((H, W), bool); comps = []
    cl = int(fl.get("furniture_close", 15))
    for i in range(1, nn + 1):
        c = nl == i
        if c.sum() < 250:
            continue
        ys, xs = np.nonzero(c)
        if c.sum() < 600 and (np.ptp(ys) < 8 or np.ptp(xs) < 8):
            continue
        furn |= ndi.binary_fill_holes(ndi.binary_closing(c, np.ones((cl, cl), bool), border_value=0))
        comps.append({"px": int(c.sum()), "center": [int(xs.mean()), int(ys.mean())]})
    k = int(fl.get("furniture_dilate", 7))
    furn = cv2.dilate(furn.astype(np.uint8), np.ones((k, k), np.uint8)).astype(bool)
    white = ndi.binary_opening(floor & ~furn & ~blocked_mask, np.ones((9, 9), bool))
    lb, n = ndi.label(white)
    if n == 0:
        sys.exit(f"room {room['id']}: 床が1画素も残らない")
    sz = ndi.sum(white, lb, range(1, n + 1))
    white = lb == 1 + int(np.argmax(sz))
    info = {"room": room["id"], "floor_core_lab": [int(v) for v in med], "thr": thr, "quad_px": int(quad.sum()),
            "white_px": int(white.sum()), "white_share_of_quad": round(float(white.sum() / quad.sum()), 3),
            "md_gt15_white_px": int((md[white] > 15).sum()), "furniture_components": len(comps)}
    return white, info


def boundary_of(white):
    """white の縁（4近傍に非whiteがある white 画素）。"""
    er = ndi.binary_erosion(white, structure=ndi.generate_binary_structure(2, 1), border_value=0)
    return white & ~er


def exit_poly(room, pos):
    if "image_polygon" in pos:
        return np.array(pos["image_polygon"], np.float64)
    u0, u1, v0, v1 = pos["plan_box"]
    return np.array([uv_to_img(room, u0, v0), uv_to_img(room, u1, v0), uv_to_img(room, u1, v1), uv_to_img(room, u0, v1)])


def edge_adjacent(room, pos, edge, tol=0.1):
    if "plan_box" in pos:
        u0, u1, v0, v1 = pos["plan_box"]
        return {"west": u0 <= tol, "east": u1 >= 1 - tol, "north": v0 <= tol, "south": v1 >= 1 - tol}[edge]
    return None


def check_exit(im, room, white, bnd, e, pos, dt):
    poly = exit_poly(room, pos)
    pm = poly_mask(im.shape, poly)
    adj = edge_adjacent(room, pos, e["edge"])
    n_edge = int((pm & bnd).sum()); n_white = int((pm & white).sum())
    far = float(dt[pm].max()) if pm.any() else 0.0  # 範囲内で床の縁から最も遠い点（床の奥へ入り込みすぎの目安）
    return {"polygon": np.round(poly, 1).tolist(), "range_px": int(pm.sum()), "white_px": n_white,
            "floor_edge_px": n_edge, "touches_floor_edge": bool(n_edge > 0),
            "edge_adjacent_in_plan": adj, "max_depth_into_floor_px": round(far, 1),
            "pass": bool(n_edge > 0 and n_white > 0 and adj is not False)}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", help="入力JSON（sit-oblique-input/1）")
    ap.add_argument("--image", required=True, help="採用画像（oblique_register.py と同じ）")
    ap.add_argument("--reg", required=True, help="oblique_register.py の出力ディレクトリ（行列の整合を検査）")
    ap.add_argument("--out", required=True, help="出力ディレクトリ")
    ap.add_argument("--masks-dir", help="可逆WebP等を書く先（例 assets/images/fields/masks）。省略時は書かない")
    a = ap.parse_args()
    d = load_input(a.input)
    mid = d["map_id"]
    im = read_image(a.image)
    H_, W_ = im.shape[:2]
    exp = d.get("image", {}).get("expected_size")
    if exp and [W_, H_] != exp:
        sys.exit(f"画像寸法 {W_}x{H_} が期待 {exp} と違う")
    from json import load
    reg = load(open(os.path.join(a.reg, f"{mid}-oblique-register.json"), encoding="utf-8"))
    if reg["input_sha256"] != sha256_file(a.input) or reg["image"]["sha256"] != sha256_file(a.image):
        sys.exit("register.json が今の入力JSON・画像と食い違う。oblique_register.py をやり直す")
    rooms = {r["id"]: r for r in d["rooms"]}
    fl = d.get("floor", {})
    # blocked / assist 多角形
    blk_all = np.zeros((H_, W_), bool); blk_by_room = {r: np.zeros((H_, W_), bool) for r in rooms}
    for b in d.get("blocked", []):
        m = poly_mask(im.shape, b["polygon"])
        if b.get("room") in rooms:
            blk_by_room[b["room"]] |= m
        else:
            blk_all |= m
    asi = np.zeros((H_, W_), bool)
    for s in d.get("assist", []):
        asi |= poly_mask(im.shape, s["polygon"])
    white = np.zeros((H_, W_), bool); infos = []
    for rid, room in rooms.items():
        wm, info = room_floor(im, room, blk_all | blk_by_room[rid], fl)
        white |= wm; infos.append(info)
    manual_blk = blk_all.copy()
    for m in blk_by_room.values():
        manual_blk |= m
    white &= ~manual_blk
    orange = asi & white           # assist は指定多角形の中の床だけ。指定が無ければ0画素
    white_only = white & ~orange
    lb, n_cc = ndi.label(white | orange)
    bnd = boundary_of(white | orange)
    dt = ndi.distance_transform_edt(white | orange)
    # 出力画像
    edit = np.zeros((H_, W_, 3), np.uint8)
    edit[white_only] = (255, 255, 255); edit[orange] = ORANGE
    edit_bgr = edit[..., ::-1].copy()
    mask = np.zeros((H_, W_, 3), np.uint8); mask[white_only] = 255
    os.makedirs(a.out, exist_ok=True)
    p_edit = os.path.join(a.out, f"{mid}-oblique-traversal-edit.png"); cv2.imwrite(p_edit, edit_bgr)
    p_mask = os.path.join(a.out, f"{mid}-oblique-mask.png"); cv2.imwrite(p_mask, mask)
    # 判定
    chk = []
    res = {"schema": SCHEMA_RESULT, "map_id": mid, "image": {"sha256": sha256_file(a.image), "size": [W_, H_]},
           "input_sha256": sha256_file(a.input), "register_sha256": sha256_file(os.path.join(a.reg, f"{mid}-oblique-register.json")),
           "floor": infos, "counts_px": {"white": int(white_only.sum()), "assist_orange": int(orange.sum()),
           "blocked_manual": int(manual_blk.sum()), "white_components": int(n_cc)}}
    chk.append(("床 white", f"{int(white_only.sum())}px / 連結{n_cc}", "PASS" if n_cc == 1 else "FAIL"))
    chk.append(("床 md>15 の白", f"{sum(i['md_gt15_white_px'] for i in infos)}px", "PASS" if all(i['md_gt15_white_px'] == 0 for i in infos) else "FAIL"))
    chk.append(("assist(橙)", f"{int(orange.sum())}px", "既定0" if not orange.any() else "指定領域のみ"))
    mb = []
    for b in d.get("blocked", []):
        m = poly_mask(im.shape, b["polygon"])
        leak = int((m & (white | orange)).sum())
        mb.append({"id": b["id"], "room": b.get("room"), "reason": b.get("reason"), "leak_white_px": leak, "pass": leak == 0})
        chk.append((f"blocked {b['id']}", f"white漏れ{leak}px", "PASS" if leak == 0 else "FAIL"))
    res["blocked"] = mb
    # 出口
    ex_out = []
    for e in d.get("exits", []):
        room = rooms[e["room"]]
        pos = e.get("position", {"status": "TBD"})
        ent = {"id": e["id"], "room": e["room"], "edge": e["edge"], "partner": e.get("partner"),
               "design_source": e.get("design_source"), "position_status": pos.get("status", "fixed")}
        if pos.get("status") == "TBD":
            ent["check"] = None
            ent["note"] = "設計書に位置が無い（TBD）。絵から読まない。候補は candidates"
            chk.append((f"出口 {e['id']}", "位置TBD（設計書）", "TBD"))
        else:
            ent["check"] = check_exit(im, room, white | orange, bnd, e, pos, dt)
            c = ent["check"]
            chk.append((f"出口 {e['id']}", f"縁px{c['floor_edge_px']} white{c['white_px']}", "PASS" if c["pass"] else "FAIL"))
        ent["candidates"] = []
        for c in e.get("candidates", []):
            cc = check_exit(im, room, white | orange, bnd, e, c, dt)
            ent["candidates"].append({"id": c["id"], "note": c.get("note"), **cc})
            chk.append((f"  候補 {c['id']}", f"縁px{cc['floor_edge_px']} white{cc['white_px']}", "候補:" + ("縁に接する" if cc["pass"] else "接しない")))
        ex_out.append(ent)
    res["exits"] = ex_out
    # NPC
    ys, xs = np.nonzero(dt >= EDGE_CLEAR_PX)
    tree = cKDTree(np.c_[xs, ys]) if len(xs) else None
    npc_out = []
    for nconf in d.get("npcs", []):
        room = rooms[nconf["room"]]
        u, v = nconf["uv"]
        px, py = uv_to_img(room, u, v)
        ix, iy = int(round(px)), int(round(py))
        d0 = float(dt[iy, ix]) if 0 <= iy < H_ and 0 <= ix < W_ else -1.0
        if d0 >= EDGE_CLEAR_PX:
            sx, sy, sd = ix, iy, 0.0
        else:
            sd, j = tree.query([px, py]); sx, sy = int(xs[j]), int(ys[j]); sd = float(sd)
        Hm = np.array(reg["rooms"][[r["id"] for r in reg["rooms"]].index(nconf["room"])]["H_img_to_plan"])
        pp = apply_h(Hm, [[sx, sy]])[0]; pw, ph = reg["rooms"][[r["id"] for r in reg["rooms"]].index(nconf["room"])]["plan_size"]
        clr = float(dt[sy, sx])
        npc_out.append({"id": nconf["id"], "room": nconf["room"], "uv": [u, v], "img_projected": [round(px, 1), round(py, 1)],
                        "clearance_before_px": round(d0, 1), "snapped_img": [sx, sy], "snap_dist_px": round(sd, 1),
                        "edge_clearance_px": round(clr, 1), "snapped_uv": [round(pp[0] / pw, 3), round(pp[1] / ph, 3)],
                        "pass": bool(clr >= EDGE_CLEAR_PX and white_only[sy, sx])})
        chk.append((f"NPC {nconf['id']}", f"寄せ{sd:.1f}px 縁から{clr:.1f}px", "PASS" if npc_out[-1]["pass"] else "FAIL"))
    res["npcs"] = npc_out
    res["verdict"] = {"all_pass": all(c[2] in ("PASS", "既定0", "指定領域のみ", "TBD") or c[2].startswith("候補") for c in chk)}
    # overlay
    o = im.copy().astype(np.float32)
    def tint(m, bgr, k=0.45):
        o[m] = (1 - k) * o[m] + k * np.array(bgr, np.float32)
    anyquad = np.zeros((H_, W_), bool)
    for r in rooms.values():
        anyquad |= poly_mask(im.shape, r["quad"])
    tint(white_only, (0, 255, 0)); tint(orange, (0, 157, 255), 0.6)
    tint(anyquad & ~(white | orange) & ~manual_blk, (0, 0, 255), 0.4); tint(manual_blk & anyquad, (255, 0, 0), 0.45)
    o = o.astype(np.uint8)
    for rid, room in rooms.items():
        for i in range(11):
            cv2.line(o, tuple(int(x) for x in uv_to_img(room, i / 10, 0)), tuple(int(x) for x in uv_to_img(room, i / 10, 1)), (0, 255, 255), 1)
        for j in range(7):
            cv2.line(o, tuple(int(x) for x in uv_to_img(room, 0, j / 6)), tuple(int(x) for x in uv_to_img(room, 1, j / 6)), (0, 255, 255), 1)
        cv2.polylines(o, [np.int32(room["quad"])], True, (255, 255, 255), 2)
    for e in ex_out:
        for c in e["candidates"]:
            cv2.polylines(o, [np.int32(np.round(c["polygon"]))], True, (255, 255, 0), 2)
            cv2.putText(o, c["id"], tuple(int(v) for v in np.array(c["polygon"])[0] + [8, -6]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
        if e["check"]:
            cv2.polylines(o, [np.int32(np.round(e["check"]["polygon"]))], True, (255, 0, 255), 3)
    for n_ in npc_out:
        cv2.circle(o, tuple(n_["snapped_img"]), 9, (255, 0, 255), -1)
        cv2.circle(o, tuple(int(v) for v in n_["img_projected"]), 6, (0, 255, 255), 2)
        cv2.putText(o, n_["id"], (n_["snapped_img"][0] + 12, n_["snapped_img"][1]), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 2)
    p_ov = os.path.join(a.out, f"{mid}-oblique-mask-overlay.png"); cv2.imwrite(p_ov, o)
    res["outputs"] = {"traversal_edit_sha256": sha256_file(p_edit), "mask_sha256": sha256_file(p_mask)}
    if a.masks_dir:
        from PIL import Image
        os.makedirs(a.masks_dir, exist_ok=True)
        Image.open(p_edit).convert("RGB").save(os.path.join(a.masks_dir, f"{mid}-traversal-edit.webp"), lossless=True)
        Image.open(p_mask).convert("RGB").save(os.path.join(a.masks_dir, f"{mid}-mask.webp"), lossless=True)
        Image.open(p_ov).convert("RGB").save(os.path.join(a.masks_dir, f"{mid}-mask-overlay.webp"), quality=85)
    rp = os.path.join(a.out, f"{mid}-oblique-result.json"); jdump(res, rp)
    print(f"{mid} mask: " + ("ALL PASS" if res["verdict"]["all_pass"] else "FAIL あり"))
    print(table([tuple(c) for c in chk], ("検査", "値", "判定")))
    print(f"詳細: {rp}")
    if not res["verdict"]["all_pass"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
