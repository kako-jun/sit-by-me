#!/usr/bin/env python3
"""体内 BDY-xx の body_register.py の出力から、2値マスク・レビュー用重ね画像・出口候補JSONを書き出す簡易ツール。

体内など小学校以降のMAPは通れる/通れないの2値だけ（kako-jun 決定 #142）。white=床（通れる）、black=それ以外。assist（#FF9D00）は使わない。
make_masks.py（削除済み）の legacy 形式（フラット塗り・画像と同寸 RGB の *-traversal-edit、*-mask）と互換。standing = wheelchair = 同一の mask。

実行（register を先に OUT/BDY-xx-register.json, -floor-cut.png へ出しておく）:
  uv run --with pillow --with numpy --with scipy python3 -I body_mask_export.py --reg REGDIR \
      --masks assets/images/fields/masks --notes-dir docs/production/body-masks [--maps BDY-01,BDY-02]

出力:
  <masks>/BDY-xx-traversal-edit.webp  可逆WebP、RGB、白/黒のみ（Photoshop の編集元）
  <masks>/BDY-xx-mask.webp           同一画素（standing = wheelchair）
  <masks>/BDY-xx-mask-overlay.webp   レビュー用（床=緑・輪郭=黄・出口の枠）。使い捨て
  <notes-dir>/BDY-xx-links.json      出口候補の範囲（模型の天面の矩形の辺上、比率0..1と画像px）。範囲値とランタイム扱いは TBD（kako-jun 2026-10-22）
  <notes-dir>/BDY-xx-register.json   body_register.py の出力（床の差・位相・信頼度）に、採用判断（画像の床を正とした）を足した写し
  <notes-dir>/export-report.json     17枚の一覧と、接続の辺の反対検査
  承認の事実（red-team 済み・kako-jun の逸脱承認の日付と内容）は、コードに書かず <notes-dir>/approvals.json（--approvals で変更可）から読む。
  無ければ register に承認の記述を書かない。接続検査に problems があれば exit 1、--maps や入力ファイルの不備は exit 2。
"""
import argparse
import glob
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi

REPO = Path(__file__).resolve().parents[4]
MAPS = [f"BDY-{i:02d}" for i in range(1, 18)]
OPP = {"N": "S", "S": "N", "E": "W", "W": "E"}
ADOPT = {"BDY-01": "body-mouth-bdy01", "BDY-02": "body-upper-torso-bdy02", "BDY-03": "body-lower-torso-bdy03", "BDY-04": "body-brain-maze-bdy04",
         "BDY-05": "body-left-arm-1-bdy05", "BDY-06": "body-left-arm-2-bdy06", "BDY-07": "body-right-arm-1-bdy07", "BDY-08": "body-right-arm-2-bdy08",
         "BDY-09": "body-left-leg-1-bdy09", "BDY-10": "body-left-leg-2-bdy10", "BDY-11": "body-left-leg-3-bdy11", "BDY-12": "body-right-leg-1-bdy12",
         "BDY-13": "body-right-leg-2-bdy13", "BDY-14": "body-right-leg-3-bdy14", "BDY-15": "body-stomach-bdy15", "BDY-16": "body-heart-bdy16",
         "BDY-17": "body-lungs-bdy17"}
MOCK_RECT = (138, 138, 1782, 942)

# 信頼度が HIGH でない MAP の判断（レビュー後に埋める。画像の床を正とした記録）
NOTES = {
    "BDY-04": "MID。床の差のモックのみ約17%は、画像の通路が壁際の影の帯（約8〜10px）ぶん細いこと。迷路の格子は辺・行き止まり・T字・曲がり・成分とも仕様と一致。床=クリーム色の領域だけ、影は black（画像の床を正）",
    "BDY-05": "MID。モックのみ約18%は、画像の帯が壁の帯・面取りのぶんモックより細いこと。出口 N1/W1 は一致。画像の床を正",
    "BDY-07": "LOW（inlier 0.19）。理由: 画像の帯がモックより広く傾きも違い、床の境界が12px以内に重ならない。位置合わせは T のまま。マスクは位置合わせでなく採用画像の床の見え（床色の芯 233,205,171）で切り出しており、画像の廊下に沿っている。画像の床を正とし、モックは更新しない（差分として記録）。出口 N1/E1 は一致、中心はモックから -23/+43px",
    "BDY-09": "MID。壁の外側の明るい面取り斜面は床色基準で black に戻した（旧: 画像のみ床19% → 現: 構造差0、細い境界差のみ）。出口 S1/W1 一致、折れ点1（仕様1）",
    "BDY-15": "LOW（inlier 0.44）。理由: J字の袋の形（胃体の膨らみ）が画像の方が細く、モック境界の12px以内に入る点が半分に満たない。部屋の検査は4室中3室（胃体の内接円 約97px < 期待200px×0.75 = 画像の胃体が痩せている）。連結成分1・出口 W1・穴0 は仕様どおり。画像の床を正とし、モックは更新しない",
    "BDY-16": "LOW（inlier 0.46）。理由: 4部屋をつなぐ上下の帯と中央の島の縁が、画像のほうが細く／位置が違う（モックのみの構造差 帯2か所）。部屋4/4・環の穴1・出口 N1・連結成分1 は仕様どおり。画像の床を正とし、モックは更新しない",
}


def rect_note(reg):
    im = reg["image_measure"]
    return dict(method="check_body_image.measure_layers（机→縁取り→波形→天面の4層の構造測定）を辺ごとに判定。層が読め期待から60px以内の辺は測定値、それ以外の辺は期待値へフォールバック",
                rect_used=im["rect_used"], side_measured_ok=im["side_measured_ok"], side_fallback_reasons=im["side_fallback_reasons"],
                rect_used_for_registration=im["rect_used_for_registration"])


def load_approvals(path):
    """承認の事実の読み込み元。無ければ空（承認は書かない）。形式は docs/production/body-masks/approvals.json 参照"""
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        die(f"approvals を読めない: {path}: {e}")


def approval_text(appr, mid):
    d = (appr.get("deviations") or {}).get(mid)
    return d["text"] if d and d.get("text") else ""


def runtime_status(appr):
    parts = []
    rt = appr.get("red_team") or {}
    if rt.get("done"):
        parts.append("red-team 済み")
    devs = appr.get("deviations") or {}
    if devs:
        dates = sorted({d["date"] for d in devs.values() if d.get("date")})
        who = sorted({d["approver"] for d in devs.values() if d.get("approver")})
        if who and dates:
            parts.append(f"{'・'.join(who)} の逸脱承認済み {dates[-1]}")
    return "ready ではない（遷移の範囲値・ランタイムの扱いが TBD" + ("。" + "・".join(parts) if parts else "") + "）"


def die(msg, code=2):
    print("ERROR: " + msg, file=sys.stderr)
    sys.exit(code)


def note_for(mid, reg, appr=None):
    im = reg["image_measure"]
    fb = im["side_fallback_reasons"]
    parts = [NOTES.get(mid) or "", "【rect の測定】" + ("4辺とも測定値。" if not fb else "辺 " + "".join(sorted(fb)) + " は期待値のフォールバック（測定できなかった。直せない理由: 縁の層〔縁取り・波形〕が画像に読めず、期待値より良い根拠が画像に無い）。内訳: " + "; ".join(f"{k}={v}" for k, v in fb.items()) + "。"),
             "【床色基準の統一・喉】" + THROAT_NOTE]
    th = reg["floor_cut"]["info"].get("exit_throat_extension")
    if th:
        parts.append(f"喉の延長で足した床 {th['added_px']}px（出口のある辺 {''.join(th['sides'])}）。")
    parts.append(EXTRA.get(mid, "").replace("{APPROVAL}", approval_text(appr or {}, mid)).strip())
    return " ".join(p for p in parts if p)


THROAT_NOTE = ("床=床の芯の色からのマハラノビス距離 md<5 が続く所まで white。壁の帯・面取り・影・地形・毛糸は black（影の帯を床の内側へ削り込まない）。"
               "出口の喉は、縁の内側で床色が続く所まで、縁の外側は波形の帯の切れ目を床色が途切れず通る列だけ white（出口の幅=切れ目の幅、模型の外の机へは出さない。"
               "床色が机まで続く辺は縁で止める）。縁際の影で暗い床は測定済みの辺の出口だけ、縁の内側・出口の区間の幅の中に限り md<10 まで許す（縁の外・区間の外へは延ばさない）。"
               "縁の外の white は床の芯の色（md<5）のみ（テープ・縁取り・帯の色は除く）。white に囲まれた床色の小さな穴は埋める。壁の面取り上面（幅<約7px）の捨て処理は幅を絞った（旧は約14px）。"
               "禁止辺の検査: 出口でない辺で、縁から内側4px以内と縁の外側に white が無いこと。出口の範囲（links）は縁から内側4pxの帯の white の連続区間")

EXTRA = {
    "BDY-01": "南の出口の white は縁（rect y=800）を約40px 越えて前縁（y=839）まで届く。辺の定義は y=800（rect）と y=839（前縁）の両方を links.json に記録し、遷移範囲の確定時にどちらを採るか決める（TBD）。",
    "BDY-04": "通路幅は画像の描画による差（画像で約56px。仕様 約77px→画像倍率で約66px）。マスクは画像に従う。",
    "BDY-17": "通路幅は画像の描画による差（記載 77px(1920基準)/約67px(画像倍率)に対し、画像で横の帯 48〜52px・縦の帯 63〜64px）。マスクは画像に従う。",
    "BDY-15": "入口（W）の白は、画像で見えている床より約19〜22px細い（上端の影帯を black にする定義のため）。画像の描画による差でマスクは画像に従う。入口の幅は決定の再確認事項。",
    "BDY-02": "契約『首は1本・上で頭と口に分岐』と採用画像（旧版。北辺の床が首の狭まりのない1つの広い塊）が食い違う。{APPROVAL}契約の首1本・分岐は画像では広い床の塊として現れる。マスクは画像の床に従う（変更不要。画像が正）。",
    "BDY-13": "画像・マスクとも 1672x940（寸法ゲートは 1672x941。比率差0.1%）。{APPROVAL}",
}


def edge_axis(sd):
    return "x" if sd in "NS" else "y"


def assign_exits(geom_exits, reg, xf_M):
    """モックの出口（辺ごと）を、画像で検出した床の区間（その辺の縁に届く）へ、中心が近い順に1対1で割り当てる。"""
    rect = reg["image_measure"]["rect_used"]
    exits = reg["topology"]["exits"]
    M = np.array(xf_M, float)
    out = []
    used = {sd: set() for sd in "NESW"}
    # 辺ごとに、モックの出口を画像へ写した中心と、検出区間の中心を近い順に
    for sd in "NESW":
        ge = [e for e in geom_exits if e["side"] == sd]
        runs = [pr["image"] for pr in exits[sd]["pairs"]]
        cands = []
        for gi, e in enumerate(ge):
            r = e["range"]
            if edge_axis(sd) == "x":
                ys = MOCK_RECT[1] if sd == "N" else MOCK_RECT[3]
                p = np.array([[r["a_px"], ys], [r["b_px"], ys]])
            else:
                xs = MOCK_RECT[0] if sd == "W" else MOCK_RECT[2]
                p = np.array([[xs, r["a_px"]], [xs, r["b_px"]]])
            q = p @ M[:, :2].T + M[:, 2]
            k = 0 if edge_axis(sd) == "x" else 1
            ma, mb = sorted([float(q[0][k]), float(q[1][k])])
            for ri, run in enumerate(runs):
                cands.append((abs((ma + mb) / 2 - (run[0] + run[1]) / 2), gi, ri, (ma, mb)))
        cands.sort()
        got = {}
        for d, gi, ri, mr in cands:
            if gi in got or ri in used[sd] or d > 320:
                continue
            got[gi] = (ri, mr, d); used[sd].add(ri)
        for gi, e in enumerate(ge):
            if gi in got:
                ri, mr, d = got[gi]
                out.append((e, sd, runs[ri], mr, d))
            else:
                r = e["range"]
                out.append((e, sd, None, None, None))
    return out, {sd: [runs for runs in [exits[sd]["pairs"]]] for sd in "NESW"}, rect


def gap_to_edge(cut, sd, rect, a, b):
    """出口区間の床が、天面の矩形の縁から何px内側で始まるか（縁と床の間の blocked の帯＝段ボール帯下の影など。0なら縁に接する）。"""
    x0, y0, x1, y1 = rect
    if sd == "N":
        v = cut[y0:y0 + 80, a:b + 1].any(1)
    elif sd == "S":
        v = cut[y1 - 80:y1, a:b + 1].any(1)[::-1]
    elif sd == "W":
        v = cut[a:b + 1, x0:x0 + 80].any(0)
    else:
        v = cut[a:b + 1, x1 - 80:x1].any(0)[::-1]
    return int(np.argmax(v)) if v.any() else None


def white_beyond_edge(cut, sd, rect, a, b):
    """出口区間の white が、模型の縁（rect）より外側（波形の帯の切れ目）へ何px 出ているか（0なら縁まで）。隙間の測り方は gap_to_edge と同じ最終マスクから。"""
    x0, y0, x1, y1 = rect
    H, W = cut.shape
    if sd == "N":
        v = cut[max(y0 - 80, 0):y0, a:b + 1].any(1)[::-1]
    elif sd == "S":
        v = cut[y1:min(y1 + 80, H), a:b + 1].any(1)
    elif sd == "W":
        v = cut[a:b + 1, max(x0 - 80, 0):x0].any(0)[::-1]
    else:
        v = cut[a:b + 1, x1:min(x1 + 80, W)].any(0)
    n = 0
    for f in v:
        if not f:
            break
        n += 1
    return n


def _line(cut, sd, rect, lo, hi):
    """辺 sd の縁から内側へ lo〜hi px（rect の内側。縁の最初の内側の行が 0）の帯で、辺に沿う座標ごとに white が1つでもあるか。戻り (vec, off)"""
    x0, y0, x1, y1 = rect
    if sd == "N":
        return cut[y0 + lo:y0 + hi, x0:x1].any(0), x0
    if sd == "S":
        return cut[y1 - hi:y1 - lo, x0:x1].any(0), x0
    if sd == "W":
        return cut[y0:y1, x0 + lo:x0 + hi].any(1), y0
    return cut[y0:y1, x1 - hi:x1 - lo].any(1), y0


def _runs(v, off, minlen):
    out, st = [], None
    for i, f in enumerate(list(v) + [False]):
        if f and st is None:
            st = i
        elif not f and st is not None:
            if i - st >= minlen:
                out.append((st + off, i - 1 + off))
            st = None
    return out


BAND_PX = 4      # 出口の範囲・禁止辺の検査は、縁（rect）から内側 4px の帯で測る（両者の定義を揃える）


def edge_band_run(cut, sd, rect, ref, band=BAND_PX, minlen=8):
    """出口の範囲 = 縁から内側 band px の帯にある white の連続区間のうち、ref（30px 帯で検出した区間）と最も重なるもの。無ければ None"""
    v, off = _line(cut, sd, rect, 0, band)
    best = None
    for a, b in _runs(v, off, minlen):
        ov = min(b, ref[1]) - max(a, ref[0])
        if ov > 0 and (best is None or ov > best[0]):
            best = (ov, a, b)
    return None if best is None else (best[1], best[2])


def front_edge(cut, sd, rect, a, b, n):
    """縁（rect）より外へ white が n px 出ている出口の、最も外の行（列）の座標と、そこでの white の区間（出口の範囲 a..b と重なるもの）"""
    x0, y0, x1, y1 = rect
    line = {"N": y0 - n, "S": y1 + n - 1, "W": x0 - n, "E": x1 + n - 1}[sd]
    if sd in "NS":
        v, off = cut[line, x0:x1], x0
    else:
        v, off = cut[y0:y1, line], y0
    rs = [r for r in _runs(v, off, 1) if min(r[1], b) - max(r[0], a) >= 0]
    return dict(line_px=int(line), range=None if not rs else dict(a_px=int(min(r[0] for r in rs)), b_px=int(max(r[1] for r in rs))))


def forbidden_edge_check(cut, rect, exit_sides, band=BAND_PX):
    """禁止辺の検査（統一定義）: 出口でない辺で、縁（rect）から内側 band px 以内と縁の外側に white が無いこと。辺ごとの white の画素数と合否"""
    x0, y0, x1, y1 = rect
    H, W = cut.shape
    res = {}
    for sd in "NESW":
        if sd in exit_sides:
            continue
        n_inner = int({"N": cut[y0:y0 + band, x0:x1], "S": cut[y1 - band:y1, x0:x1], "W": cut[y0:y1, x0:x0 + band], "E": cut[y0:y1, x1 - band:x1]}[sd].sum())
        n_out = int({"N": cut[:y0, :], "S": cut[y1:, :], "W": cut[:, :x0], "E": cut[:, x1:]}[sd].sum())
        res[sd] = {"white_px_inside_band": n_inner, "white_px_outside_edge": n_out, "ok": n_inner == 0 and n_out == 0}
    return dict(definition="出口でない辺で、縁（rect）から内側 %dpx 以内と縁の外側に white が無い" % band, sides=res, ok=all(v["ok"] for v in res.values()))


def build_links(mid, geom, reg, adopted_path, img_size, cut):
    rect = reg["image_measure"]["rect_used"]
    x0, y0, x1, y1 = rect
    W_, H_ = x1 - x0, y1 - y0
    asg, _, _ = assign_exits(geom["exits"], reg, reg["registration"]["matrix_mock_to_image"])
    exits = []
    for e, sd, run, mr, d in asg:
        ax = edge_axis(sd)
        lo, span = (x0, W_) if ax == "x" else (y0, H_)
        edge_px = {"N": y0, "S": y1, "W": x0, "E": x1}[sd]
        item = dict(id=f"{mid}.{e['port']}", port=e["port"], side=sd, partner=e["partner"], along=ax,
                    mock_range_in_image=None if mr is None else dict(a_px=round(mr[0], 1), b_px=round(mr[1], 1)),
                    spec_slot_ratio=e["slot"], edge_line_px=int(edge_px))
        if run is None:
            item.update(detected=False, image_range=None, note="この辺の縁に届く床の区間が、モックの出口の近く（320px以内）に見つからない")
        else:
            ref = (int(run[0]), int(run[1]))
            er = edge_band_run(cut, sd, rect, ref)
            er30 = None if er else edge_band_run(cut, sd, rect, ref, band=30)
            a, b = er or er30 or ref          # 範囲 = 縁から内側4pxの帯の white の実測。帯に white が無い（床が縁に届かない）時だけ内側30pxの帯の white の連続区間
            item["range_definition"] = ("縁（rect）から内側 %dpx の帯の white の連続区間" % BAND_PX) if er else ("4px 帯に white が無い（床が縁に届かない）ため、縁から内側 30px の帯の white の連続区間" if er30 else "縁から内側 30px の帯にも見つからず、検出区間を採用")
            item.update(detected=True, image_range=dict(a_px=a, b_px=b, a_ratio=round((a - lo) / span, 4), b_ratio=round((b - lo) / span, 4),
                                                       width_px=b - a + 1, center_px=round((a + b) / 2, 1), center_ratio=round(((a + b) / 2 - lo) / span, 4)),
                        center_shift_vs_mock_px=round((a + b) / 2 - (mr[0] + mr[1]) / 2, 1),
                        floor_gap_to_edge_px=gap_to_edge(cut, sd, rect, a, b), white_beyond_edge_px=white_beyond_edge(cut, sd, rect, a, b))
            wb = item["white_beyond_edge_px"]
            if wb > 0:
                fe = front_edge(cut, sd, rect, a, b, wb)
                item["edge_definitions"] = dict(
                    rect_edge=dict(line_px=int(edge_px), range=dict(a_px=a, b_px=b)), front_edge=fe,
                    note="辺の定義は2つ: rect_edge（模型の天面の矩形の縁 %s=%d）と front_edge（white が実際に届く最も外の行 %s=%d、縁から %dpx 外）。遷移の範囲値の確定時に、どちらを辺として採るか決める（TBD）" % (
                        "y" if sd in "NS" else "x", edge_px, "y" if sd in "NS" else "x", fe["line_px"], wb))
        exits.append(item)
    extra = []
    for sd in "NESW":
        known = {(it["side"], tuple(it["image_range"].values())[:2]) for it in exits if it.get("image_range")}
        for pr in reg["topology"]["exits"][sd]["pairs"]:
            if (sd, tuple(pr["image"])) not in known:
                extra.append(dict(side=sd, image_range_px=pr["image"], note="仕様に無い出口（画像で縁に届く床の区間）"))
    events = [dict(id=f"{mid}.{ev['id']}", note=ev["note"], range=None, source="TRM-03.event-kiss → BDY-01.event-mouth（一方向の物語イベント）。位置・範囲は原文に無く TBD")
              for ev in geom.get("events", [])]
    return dict(schema="sit-body-exit-candidates/1", map=mid, status="出口候補の範囲（遷移の範囲値とランタイムの扱いは TBD、kako-jun 2026-10-22。ready ではない）",
                image=dict(path=str(adopted_path), size=list(img_size)), model_top_rect_image_px=dict(x0=x0, y0=y0, x1=x1, y1=y1, w=W_, h=H_),
                coordinate_note="a/b は辺に沿う区間（N/S は x、E/W は y）の画像px、ratio は天面の矩形に対する 0..1。区間は『床が模型の縁（波形の内側＝天面の矩形）に届く範囲』＝縁から内側4pxの帯の white の連続区間を、最終マスクから実測した値（出口でない辺の禁止検査も同じ4px帯）",
                exits=exits, unexpected_exits=extra, events=events)


def overlay(a, floor, links, rect):
    o = a.astype(float)
    m = floor
    o[~m] = o[~m] * 0.55
    o[m] = o[m] * 0.55 + np.array([0, 200, 0]) * 0.45
    b = m & ~ndi.binary_erosion(m)
    b = ndi.binary_dilation(b)
    o[b] = (255, 235, 0)
    im = Image.fromarray(np.clip(o, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(im)
    d.rectangle([rect[0], rect[1], rect[2] - 1, rect[3] - 1], outline=(255, 0, 255), width=2)
    for it in links["exits"]:
        r = it.get("image_range")
        if not r:
            continue
        sd = it["side"]; aa, bb = r["a_px"], r["b_px"]
        box = {"N": [aa, rect[1] - 8, bb, rect[1] + 10], "S": [aa, rect[3] - 10, bb, rect[3] + 8],
               "W": [rect[0] - 8, aa, rect[0] + 10, bb], "E": [rect[2] - 10, aa, rect[2] + 8, bb]}[sd]
        d.rectangle(box, outline=(0, 255, 255), width=4)
        d.text((box[0] + 4, box[1] + 12), it["port"].replace("door-passage-", ""), fill=(255, 255, 255))
    return im


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--reg", required=True, help="body_register.py の出力ディレクトリ")
    ap.add_argument("--masks", required=True)
    ap.add_argument("--notes-dir", required=True)
    ap.add_argument("--maps")
    ap.add_argument("--approvals", help="承認の事実を読む JSON（既定: <notes-dir>/approvals.json。無ければ承認は書かない）")
    args = ap.parse_args()
    maps = [m.strip() for m in args.maps.split(",") if m.strip()] if args.maps else MAPS
    bad_ids = [m for m in maps if m not in ADOPT]
    if not maps or bad_ids:
        die(f"--maps が不正（BDY-01〜BDY-17 のカンマ区切り）: {bad_ids or args.maps!r}")
    reg_dir, masks, notes = Path(args.reg), Path(args.masks), Path(args.notes_dir)
    if not reg_dir.is_dir():
        die(f"--reg がディレクトリでない: {reg_dir}")
    appr = load_approvals(Path(args.approvals) if args.approvals else notes / "approvals.json")
    for mid in maps:
        need = [reg_dir / f"{mid}-register.json", reg_dir / f"{mid}-floor-cut.png"]
        hits = glob.glob(str(REPO / "assets/images/fields/reference" / f"{ADOPT[mid]}-adopted.webp"))
        miss = [str(x) for x in need if not x.is_file()] + ([] if hits else [f"採用画像 {ADOPT[mid]}-adopted.webp"])
        gp = REPO / "verification/body-layout/geometry" / f"{mid}.json"
        if not gp.is_file():
            miss.append(str(gp))
        if miss:
            die(f"{mid}: 入力が無い: {', '.join(miss)}")
    masks.mkdir(parents=True, exist_ok=True); notes.mkdir(parents=True, exist_ok=True)
    report = {}
    all_links = {}
    for mid in maps:
        reg = json.loads((reg_dir / f"{mid}-register.json").read_text(encoding="utf-8"))
        cut = np.asarray(Image.open(reg_dir / f"{mid}-floor-cut.png").convert("L")) > 127
        adopted = Path(glob.glob(str(REPO / "assets/images/fields/reference" / f"{ADOPT[mid]}-adopted.webp"))[0])
        img = Image.open(adopted).convert("RGB")
        W, H = img.size
        assert cut.shape == (H, W), (mid, cut.shape, (W, H))
        geom = json.loads((REPO / "verification/body-layout/geometry" / f"{mid}.json").read_text(encoding="utf-8"))
        edit = np.where(cut[..., None], 255, 0).astype(np.uint8).repeat(3, axis=2)
        e_im = Image.fromarray(edit, "RGB")
        for suffix in ("traversal-edit", "mask"):
            e_im.save(masks / f"{mid}-{suffix}.webp", lossless=True, quality=100, method=6, exact=True)
        back = np.asarray(Image.open(masks / f"{mid}-traversal-edit.webp").convert("RGB"))
        assert back.shape == (H, W, 3) and np.array_equal(back, edit), f"{mid} lossless readback mismatch"
        assert set(np.unique(back).tolist()) <= {0, 255}
        links = build_links(mid, geom, reg, adopted.relative_to(REPO), (W, H), cut)
        fcheck = forbidden_edge_check(cut, reg["image_measure"]["rect_used"], {e["side"] for e in links["exits"]})
        links["forbidden_edge_check"] = fcheck
        overlay(np.asarray(img), cut, links, reg["image_measure"]["rect_used"]).save(masks / f"{mid}-mask-overlay.webp", quality=85)
        (notes / f"{mid}-links.json").write_text(json.dumps(links, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        reg["adoption"] = dict(
            floor_source="採用画像の床の見え（床色クラスタ基準の切り出し）を正とした。モックは位置合わせと位相検査の基準であり、床の正解ではない",
            mask_classes="2値（white=床=通れる / black=それ以外）。assist(#FF9D00) 不使用",
            wall_foot_definition="床（クリーム）の領域だけが white。壁の帯（段ボール・毛糸）・面取りの斜面・影・地形・土台縁・机は black",
            rect_measurement=rect_note(reg), lossless_readback_equals_floor_cut_array=True,
            rect_fallback_sides=sorted(k for k, v in reg["image_measure"]["side_measured_ok"].items() if not v),
            forbidden_edge_check=fcheck, note=note_for(mid, reg, appr), registration_confidence=reg["registration"]["confidence"], runtime_status=runtime_status(appr))
        (notes / f"{mid}-register.json").write_text(json.dumps(reg, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        all_links[mid] = links
        t = reg["topology"]; dr = reg["floor_diff_vs_mock"]; r = reg["registration"]
        report[mid] = dict(model=r["chosen_model"], transform=r["transform"], inlier=r["residual"]["inlier_frac"], mean_px=r["residual"]["inlier_mean_px"],
                           max_px=r["residual"]["inlier_max_px"], confidence=r["confidence"], iou=dr["iou"], only_image_pct=dr["only_image_pct_of_mock"],
                           only_mock_pct=dr["only_mock_pct_of_mock"], components=t["components"]["count"],
                           exits_match={sd: (t["exits"][sd]["image_count"], t["exits"][sd]["mock_count"], t["exits"][sd]["spec_count"]) for sd in "NESW"},
                           exits_detected=sum(1 for e in links["exits"] if e["detected"]), exits_spec=len(links["exits"]), unexpected=len(links["unexpected_exits"]),
                           bends=t.get("bends"), maze=t.get("maze_grid") and {k: t["maze_grid"][k] for k in ("passages", "mock_passages", "dead_ends", "t_junctions", "corners", "components", "loops")},
                           rooms=t.get("rooms") and {k: t["rooms"][k] for k in ("count_expected", "count_present")}, holes=(t.get("holes"), t.get("holes_spec")),
                           slice_mismatch=t["slice_profile_mismatch"], white_px=int(cut.sum()), forbidden_edge_ok=fcheck["ok"],
                           forbidden_edge_definition=fcheck["definition"])
    # 接続の辺の反対検査（相手 MAP の出口が両方とも検出済みの接続だけ）
    conn = []
    for mid, lk in all_links.items():
        for e in lk["exits"]:
            pm, pp = e["partner"].split(".", 1)
            if pm not in all_links or mid > pm:
                continue
            other = next((x for x in all_links[pm]["exits"] if x["port"] == pp), None)
            conn.append(dict(a=e["id"], a_side=e["side"], b=f"{pm}.{pp}", b_side=other and other["side"], opposite=bool(other) and OPP[e["side"]] == other["side"],
                             a_detected=e["detected"], b_detected=bool(other and other["detected"])))
    report["_connections"] = conn
    (notes / "export-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    bad = [c for c in conn if not c["opposite"] or not (c["a_detected"] and c["b_detected"])]
    print(f"maps={len(maps)} connections={len(conn)} problems={len(bad)}")
    for c in bad:
        print("  ", c)
    if bad:
        sys.exit(1)


if __name__ == "__main__":
    main()
