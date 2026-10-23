"""平面図スペック（*-plan.json）と接続リスト（connections.json）から、接続図・個別ワイヤー図・接続表・全MAP一覧を機械的に作る。手描きしない。

白背景・黒線のワイヤーフレーム（昔の攻略本のマップ接続図の流儀）。各MAPは oblique_mock の斜め射影の小さな平面図。
出力（--out）: connection-diagram.png・wire-<MAP>.png（個別）・overview.png（カラーのレビュー用モック一覧）・connections.md

  uv run --with numpy --with opencv-python-headless --with pillow python3 -I oblique_topology.py \
      docs/production/oblique-mocks/connections.json --out docs/production/oblique-mocks
"""
import argparse
import json
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import oblique_mock as M

K = "#000000"


def fnt(n):
    return M.font(n)


def content_bbox(p):
    xs, ys = [], []
    for key, tag, polys, meta in M.build_items(p, "wire"):
        for pts, _, _ in polys:
            for x, y in pts:
                xs.append(x); ys.append(y)
    return min(xs), min(ys), max(xs), max(ys)


def text_box(d, xy, t, f, fg=K, bg="#ffffff", pad=5, outline=K, anchor="mm"):
    lines = t.split("\n")
    bbs = [d.textbbox((0, 0), s, font=f) for s in lines]
    lh = max(b[3] - b[1] for b in bbs) + 6
    tw = max(b[2] - b[0] for b in bbs)
    th = lh * len(lines)
    x, y = xy
    if anchor == "mm":
        x0, y0 = x - tw / 2, y - th / 2
    else:  # lt
        x0, y0 = x, y
    if bg:
        d.rectangle([x0 - pad, y0 - pad, x0 + tw + pad, y0 + th + pad], fill=bg, outline=outline, width=2 if outline else 0)
    for i, s in enumerate(lines):
        d.text((x0, y0 + i * lh - bbs[i][1] + 2), s, font=f, fill=fg)
    return (x0 - pad, y0 - pad, x0 + tw + pad, y0 + th + pad)


def door_info(p, door):
    """位置の文言と、位置の比（along_ref に対する 0..1）を返す。"""
    w = M.wall_by_id(p, door["wall"])
    a, b = door["along_ref"]
    frac = (door["center"] - a) / (b - a)
    side = {"north": "北", "south": "南", "west": "西", "east": "東"}[door["wall_side"]]
    if door["wall_side"] in ("west", "east"):
        pos = f"{side}壁 v={frac:.2f}（{'上下の中央より下寄り' if frac > 0.5 else '上寄り'}）"
    else:
        pos = f"{side}壁 u={frac:.2f}（{'中央' if abs(frac - 0.5) < 0.03 else ('中央より左寄り' if frac < 0.5 else '右寄り')}）"
    if M.is_h(w):
        a1 = M.proj(door["center"] - M.DOOR_W / 2, w["rect"][3])
        b1 = M.proj(door["center"] + M.DOOR_W / 2, w["rect"][3])
        px = f"見かけ幅{abs(b1[0] - a1[0]):.0f}px"
    else:
        px = "側壁（縦）"
    return pos, frac, f"幅{M.DOOR_W}単位=キャラ2人分（{px}）"


def compass(d, x, y, f):
    d.line([(x, y + 60), (x, y - 20)], fill=K, width=5)
    d.polygon([(x, y - 40), (x - 14, y - 14), (x + 14, y - 14)], fill=K)
    d.text((x - 12, y + 66), "北", font=f, fill=K)


def render_cell(p, width):
    """ワイヤー画像を内容の範囲で切り出して width に拡縮。戻り (Image, transform(pt)->pt, anchors)。"""
    img, anchors = M.render(p, "wire", labels=False, ss=2)
    x0, y0, x1, y1 = content_bbox(p)
    mg = 40
    box = (int(max(0, x0 - mg)), int(max(0, y0 - mg)), int(min(M.W, x1 + mg)), int(min(M.H_IMG, y1 + mg)))
    crop = img.crop(box)
    sc = width / crop.width
    crop = crop.resize((width, int(crop.height * sc)), Image.LANCZOS)
    tf = lambda pt: ((pt[0] - box[0]) * sc, (pt[1] - box[1]) * sc)
    return crop, tf, {k: tf(v) for k, v in anchors.items()}, sc


def stub_vec(direction):
    return {"north": (0, -1), "south": (0, 1), "west": (-1, 0), "east": (1, 0)}[direction]


def route(p1, d1, p2, d2, stub=60):
    s1 = (p1[0] + stub_vec(d1)[0] * stub, p1[1] + stub_vec(d1)[1] * stub)
    s2 = (p2[0] + stub_vec(d2)[0] * stub, p2[1] + stub_vec(d2)[1] * stub)
    h1, h2 = d1 in ("east", "west"), d2 in ("east", "west")
    if h1 and h2:
        mx = (s1[0] + s2[0]) / 2
        mid = [(mx, s1[1]), (mx, s2[1])]
    elif not h1 and not h2:
        my = (s1[1] + s2[1]) / 2
        mid = [(s1[0], my), (s2[0], my)]
    elif h1:
        mid = [(s2[0], s1[1])]
    else:
        mid = [(s1[0], s2[1])]
    return [p1, s1] + mid + [s2, p2]


def poly_line(d, pts, width, dashed_line=False):
    d.line(pts, fill="#ffffff", width=width + 12, joint="curve")
    if dashed_line:
        for a, b in zip(pts[:-1], pts[1:]):
            M.dashed(d, a, b, K, width, dash=22)
    else:
        d.line(pts, fill=K, width=width, joint="curve")


def build(conn_path, out):
    with open(conn_path, encoding="utf-8") as f:
        C = json.load(f)
    base = os.path.dirname(os.path.abspath(conn_path))
    plans = {}
    for fn in C["plans"]:
        p = M.load_plan(os.path.join(base, fn))
        plans[p["map_id"]] = p
    # 接続の存在・相互参照を検査
    doors = {}
    for mid, p in plans.items():
        for dd in p["doors"]:
            doors[dd["id"]] = (mid, dd)
        for mk in p["markers"]:
            doors[mk["id"]] = (mid, mk)
    problems = []
    rows = []
    for e in C["edges"]:
        for end in ("a", "b"):
            ident = e[end]
            if ident not in doors and not e.get("external") and True:
                problems.append(f"{ident} がスペックに無い")
    declared = {x for e in C["edges"] for x in (e["a"], e["b"])}
    for ident, (mid, dd) in doors.items():
        pr = dd.get("partner")
        if pr and ident not in declared:
            problems.append(f"{ident} は partner があるのに connections.json の接続に無い")
        if pr and pr in doors and doors[pr][1].get("partner") != ident:
            problems.append(f"{ident} の相手 {pr} の partner が {doors[pr][1].get('partner')}（相互参照が不一致）")
    for e in C["edges"]:
        a, b = e["a"], e["b"]
        info = {}
        for end, ident in (("a", a), ("b", b)):
            if ident in doors:
                mid, dd = doors[ident]
                if "wall" in dd:
                    pos, frac, wtxt = door_info(plans[mid], dd)
                    info[end] = (pos, frac, wtxt, dd["wall_side"], dd.get("partner"), dd.get("status", ""))
                else:
                    info[end] = (f"土台の{ {'south':'南','east':'東','west':'西','north':'北'}[dd['edge']]}端 {dd['at']}", None, f"幅{M.DOOR_W}単位=キャラ2人分", dd["edge"], dd.get("partner"), dd.get("status", ""))
                if dd.get("partner") and dd["partner"] != (b if end == "a" else a):
                    problems.append(f"{ident} の partner {dd['partner']} が接続リストと不一致")
            else:
                ext = next((x for x in C["externals"] if ident in x["ports"]), {})
                info[end] = (ext.get("note", "（寺町の外・別MAP）"), None, "", "", None, "")
        verdict = "（外部ノード・整合検査なし）"
        if "a" in info and info["a"][1] is not None and info["b"][1] is not None:
            sa, sb = info["a"][3], info["b"][3]
            opp = {"west": "east", "east": "west", "south": "north", "north": "south"}
            sides_ok = (sb == opp[sa]) if e.get("expect") == "opposite" else (sa == sb)
            pos_ok = abs(info["a"][1] - info["b"][1]) <= 0.05
            verdict = ("OK" if sides_ok and pos_ok else "NG") + f"（辺{'一致' if sides_ok else '不整合'}・位置差{abs(info['a'][1]-info['b'][1]):.2f}）"
            if verdict.startswith("NG"):
                problems.append(f"{a}↔{b}: {verdict}")
        rows.append((e, info, verdict))

    # ---------------------------------------------------------------- 接続図
    CW, CH = C["canvas"]
    img = Image.new("RGB", (CW, CH), "#ffffff")
    d = ImageDraw.Draw(img)
    f_t, f_m, f_s, f_xs = fnt(46), fnt(30), fnt(24), fnt(21)
    d.text((60, 40), C["title"], font=f_t, fill=K)
    d.text((60, 108), "白黒ワイヤーフレーム（平面図から機械生成）。黒塗り=戸口（幅・高さともキャラ2人分）。灰=登れない。破線枠=仕切りの開口（既定・要確認）。", font=f_s, fill=K)
    anchors_abs, cell_boxes = {}, {}
    for mid, cfg in C["cells"].items():
        p = plans[mid]
        crop, tf, anc, sc = render_cell(p, cfg["width"])
        x0, y0 = cfg["pos"]
        img.paste(crop, (x0, y0))
        d.rectangle([x0, y0, x0 + crop.width, y0 + crop.height], outline=K, width=3)
        for k, v in anc.items():
            anchors_abs[k] = (v[0] + x0, v[1] + y0)
        cell_boxes[mid] = (x0, y0, x0 + crop.width, y0 + crop.height)
        ty = (y0 + crop.height + 14) if cfg.get("title_below") else (y0 - 92)
        text_box(d, (x0, ty), f"{mid}  {p['name']}\n{p.get('subtitle','')}", f_m, anchor="lt")
    for ex in C["externals"]:
        x, y, w, h = ex["box"]
        d.rounded_rectangle([x, y, x + w, y + h], radius=14, outline=None if ex.get("dashed") else K, width=4, fill="#ffffff")
        if ex.get("dashed"):
            for a_, b_ in (((x, y), (x + w, y)), ((x + w, y), (x + w, y + h)), ((x + w, y + h), (x, y + h)), ((x, y + h), (x, y))):
                M.dashed(d, a_, b_, K, 4, dash=16)
        d.text((x + 16, y + 14 if "\n" in ex["label"] else y + 38), ex["label"], font=f_s, fill=K)
        for pid, (side, fr) in ex["ports"].items():
            pt = {"top": (x + w * fr, y), "bottom": (x + w * fr, y + h), "left": (x, y + h * fr), "right": (x + w, y + h * fr)}[side]
            anchors_abs[pid] = pt
            d.ellipse([pt[0] - 9, pt[1] - 9, pt[0] + 9, pt[1] + 9], fill=K)
        text_box(d, (x + w - 10, y - 14), "寺町外の端点", f_xs, bg="#ffffff", outline=None, anchor="lt") if False else None
    # 線
    tags = []
    for e, info, verdict in rows:
        a, b = e["a"], e["b"]
        pa, pb = anchors_abs[a], anchors_abs[b]
        sidea = info["a"][3] if info["a"][3] else "south"
        sideb = info["b"][3] if info["b"][3] else "south"
        da = e.get("a_dir") or sidea
        db = e.get("b_dir") or {"west": "east", "east": "west"}.get(sideb, sideb)
        if "b_dir" not in e and e.get("expect") == "opposite":
            db = sideb
        pts = route(pa, da, pb, db, stub=70 if e["kind"] != "door" or not e.get("external") else 50)
        poly_line(d, pts, 6, dashed_line=(e["kind"] == "event"))
        for q in (pa, pb):
            d.ellipse([q[0] - 10, q[1] - 10, q[0] + 10, q[1] + 10], fill=K)
        if e["kind"] == "event":
            q, q2 = pts[-2], pts[-1]
            vx, vy = q2[0] - q[0], q2[1] - q[1]
            n = max(1, (vx * vx + vy * vy) ** 0.5); ux, uy = vx / n, vy / n
            d.polygon([(q2[0], q2[1]), (q2[0] - ux * 30 - uy * 14, q2[1] - uy * 30 + ux * 14), (q2[0] - ux * 30 + uy * 14, q2[1] - uy * 30 - ux * 14)], fill=K)
        # 線ラベル（中間の線分の中央）
        seg = max(zip(pts[:-1], pts[1:]), key=lambda s: (s[0][0] - s[1][0]) ** 2 + (s[0][1] - s[1][1]) ** 2)
        mx, my = (seg[0][0] + seg[1][0]) / 2, (seg[0][1] + seg[1][1]) / 2
        lab = e["label"] + ("\n幅=キャラ2人分" if e["kind"] == "door" else "")
        if verdict.startswith("OK"):
            lab += "  位置整合OK"
        tags.append((mx, my, lab))
    for mx, my, lab in tags:
        text_box(d, (mx, my), lab, f_xs, bg="#ffffff", outline=K)
    # 戸口 ID タグ（短く。幅などの詳細は connections.md・個別図）
    for ident, (mid, dd) in doors.items():
        if ident not in anchors_abs:
            continue
        ax, ay = anchors_abs[ident]
        if "wall" in dd:
            pos = door_info(plans[mid], dd)[0].split("（")[0]
        else:
            pos = dd["label"]
        t = f"{ident}\n{pos}" + ("\n*既定（要確認）" if dd.get("status") == "default" else "")
        e = next((e for e in C["edges"] if ident in (e["a"], e["b"])), None)
        side = dd.get("wall_side") or dd.get("edge")
        dr = (e.get("a_dir") if e and e["a"] == ident else e.get("b_dir")) if e else None
        dr = dr or side
        w_est = max(d.textbbox((0, 0), s_, font=f_xs)[2] for s_ in t.split("\n")) + 12
        h_est = len(t.split("\n")) * 33 + 8
        if dr == "east":
            x, y = ax + 16, ay - h_est - 26
        elif dr == "west":
            x, y = ax - w_est - 16, ay - h_est - 26
        elif dr == "south":
            x, y = ax + 22, ay + 14
            if x + w_est > CW - 20:
                x = ax - w_est - 22
        else:
            x, y = ax + 22, ay - h_est - 10
        text_box(d, (x, y), t, f_xs, bg="#ffffee", anchor="lt")
    compass(d, CW - 100, 90, f_m)
    # 凡例・接続一覧
    lx, ly = 60, 1290 + 0
    lines = ["凡例と読み方", "・黒い丸と太線=戸口どうしの接続（点線矢印=一方向のイベント）", "・戸口の幅=キャラ2人分（132単位。手前縁で約134px）", "・方角: 図の上が北。住居=西・本堂=中央・幼稚園=東", "・位置整合: 相手MAPの戸口との辺・位置（比）が一致=OK", "・*既定（要確認）=台帳に位置が無く仮置きした戸口"] + ["・" + t_ for n in C.get("legend_notes", []) for t_ in [x + "。" for x in n.split("。") if x]]
    text_box(d, (lx, ly), "\n".join(lines), f_s, bg="#ffffff", anchor="lt")
    y0 = 1750
    d.text((lx, y0), "接続一覧（詳細は connections.md）", font=f_m, fill=K)
    for i, (e, info, verdict) in enumerate(rows):
        d.text((lx, y0 + 50 + i * 34), f"{e['a']} ⇄ {e['b']}  {verdict}", font=f_xs, fill=K)
    img.save(os.path.join(out, "connection-diagram.png"))

    # ---------------------------------------------------------------- 一覧（カラー）
    order = ["TRM-05", "TRM-04", "TRM-02", "TRM-03"]
    tw, th = 836, 470
    ov = Image.new("RGB", (tw * 2 + 30, th * 2 + 30 + 70), "#2b2b2b")
    od = ImageDraw.Draw(ov)
    od.text((15, 14), "寺町 幼稚園一式のモック一覧（レビュー用・カラー・ラベル付き）", font=fnt(30), fill="#ffffff")
    for i, mid in enumerate(order):
        r, _ = M.render(plans[mid], "color", labels=True)
        r = r.resize((tw, th), Image.LANCZOS)
        ov.paste(r, (10 + (i % 2) * (tw + 10), 70 + (i // 2) * (th + 10)))
    ov.save(os.path.join(out, "overview.png"))

    # ---------------------------------------------------------------- 接続表 md
    L = ["# 寺町 幼稚園一式の接続表（機械生成。`oblique_topology.py`。手で直さない）", "",
         "平面図スペック（`*-plan.json`）と `connections.json` から生成。戸口の幅はすべてキャラ2人分（132平面単位。土台の手前縁で約134px。奥は遠近で縮む）。位置の比: 西・東壁の戸口は v（その部屋の奥行き方向。0=奥・1=手前）、南壁の戸口は u（幅方向。0=西・1=東）。", "",
         "![接続図](connection-diagram.png)", "",
         "| 戸口A | Aの位置 | 戸口B | Bの位置 | 幅 | 位置整合 | 備考 |", "|---|---|---|---|---|---|---|"]
    for e, info, verdict in rows:
        note = []
        for end in ("a", "b"):
            if info[end][5] == "default":
                note.append(f"{e[end]} は既定（要確認）")
        if e.get("external"):
            exn = next((x for x in C["externals"] if e["a"] in x["ports"] or e["b"] in x["ports"]), {})
            note.append(exn.get("kind_note", "寺町の外への端点"))
        L.append(f"| `{e['a']}` | {info['a'][0]} | `{e['b']}` | {info['b'][0]} | 2人分（{M.DOOR_W}単位） | {verdict} | {'・'.join(note) or '-'} |")
    L += ["", "## 戸口の一覧（スペック由来）", "", "| 戸口 | MAP | 辺 | 位置 | 相手 | 備考 |", "|---|---|---|---|---|---|"]
    for mid, p in plans.items():
        for dd in p["doors"]:
            pos, frac, wtxt = door_info(p, dd)
            L.append(f"| `{dd['id']}` | {mid} | {dd['wall_side']} | {pos} | `{dd.get('partner') or '-'}` | {dd.get('note','')} |")
        for mk in p["markers"]:
            L.append(f"| `{mk['id']}` | {mid} | {mk['edge']}端 | {mk['at']} | `{mk.get('partner') or '-'}` | {mk.get('label','')} {mk.get('note','')} |")
    L += ["", "## 既定（要確認）とした点（各スペックの assumptions）", ""]
    for mid, p in plans.items():
        for a_ in p.get("assumptions", []):
            L.append(f"- {mid}: {a_}")
    wl = ["# 窓の一覧（機械生成。`oblique_topology.py`。手で直さない）", "",
          "平面スペックの `windows[]` から生成。個数・位置・種別をすべて明示する。位置は壁沿いの中心座標（平面単位）と、壁の何割か（比。西→東・奥→手前）。"
          "種別: 掃き出し窓=床まで届く引き違い（扉ではない）／腰高窓。status: fixed=#51 等で既決／default=既定（要確認）。窓は見た目のみで、歩行マスク・オクルージョンには影響しない。", "",
          "## 壁ごとの個数", "", "| MAP | 壁 | 個数 | 種別 | status |", "|---|---|---|---|---|"]
    rowsw = []
    for mid, p in plans.items():
        for w in p["walls"]:
            ws = sorted([x for x in p["windows"] if x["wall"] == w["id"]], key=lambda x: x["center"])
            if not ws:
                continue
            ks = "・".join(sorted({M.WINDOW_KINDS[x["kind"]].split("（")[0] for x in ws}))
            sts = "・".join(sorted({x["status"] for x in ws}))
            wl.append(f"| {mid} | {w['id']}（{w.get('label') or w.get('kind','wall')}） | {len(ws)} | {ks} | {sts} |")
            for x in ws:
                lo, hi = x.get("along_ref") or ((w["rect"][0], w["rect"][2]) if M.is_h(w) else (w["rect"][1], w["rect"][3]))
                rowsw.append(f"| {mid} | {w['id']} | `{x['id']}` | {x['center']} | {(x['center']-lo)/(hi-lo):.2f} | {M.WINDOW_KINDS[x['kind']].split('（')[0]} | 窓台{x['sill']}・高さ{x['height']}・幅{x['width']} | {x['status']} | {x.get('note','')} |")
    wl += ["", "## 窓ごとの位置", "", "| MAP | 壁 | 窓ID | 中心（平面単位） | 比 | 種別 | 寸法 | status | 備考 |", "|---|---|---|---|---|---|---|---|---|"] + rowsw
    wl += ["", "窓の無い壁（window_count=0）: 本堂の広間・本堂棟（設計未指定のため置かない）ほか。"]
    with open(os.path.join(out, "windows.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(wl) + "\n")
    if problems:
        L += ["", "## 検査で出た問題", ""] + [f"- {x}" for x in problems]
    with open(os.path.join(out, "connections.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    return problems


def wire_single(p, path, plans):
    img, anchors = M.render(p, "wire", labels=False, ss=2)
    d = ImageDraw.Draw(img)
    f_t, f_s, f_xs = fnt(34), fnt(22), fnt(20)
    text_box(d, (20, 16), f"{p['map_id']}  {p['name']}   {p.get('subtitle','')}", f_t, anchor="lt")
    compass(d, M.W - 60, 90, fnt(26))
    # 箱・仕切りのラベル
    seen = set()
    for key, tag, polys, meta in M.build_items(p, "wire"):
        if tag == "box" and meta.get("label"):
            cx, cy = (sum(q[0] for q in polys[2][0]) / 4, sum(q[1] for q in polys[2][0]) / 4)
            text_box(d, (cx, cy), meta["label"], f_xs, pad=2, outline=None)
        elif tag == "floor" and meta.get("label") and meta["id"] not in seen:
            seen.add(meta["id"])
            cx, cy = M.proj(*meta["label_at"]) if meta.get("label_at") else (sum(q[0] for q in polys[0][0]) / 4, sum(q[1] for q in polys[0][0]) / 4)
            d.text((cx - 60, cy - 12), meta["label"], font=f_xs, fill="#666666")
        elif tag == "wall" and meta["id"] not in seen and meta.get("kind") in ("partition", "building"):
            seen.add(meta["id"])
            cx, cy = (sum(q[0] for q in polys[2][0]) / 4, sum(q[1] for q in polys[2][0]) / 4)
            text_box(d, (cx, cy), meta.get("label", ""), f_s, pad=3, outline=None)
    for dd in p["doors"]:
        ax, ay = anchors[dd["id"]]
        pos, frac, wtxt = door_info(p, dd)
        t = f"{dd['id']}\n{pos}\n{wtxt}\n相手: {dd.get('partner')}" + ("\n*既定（要確認）" if dd.get("status") == "default" else "")
        side = dd["wall_side"]
        w_est = max(d.textbbox((0, 0), s_, font=f_xs)[2] for s_ in t.split("\n")) + 12
        h_est = len(t.split("\n")) * 31 + 10
        x = ax + (-w_est - 50 if side == "west" else (50 if side == "east" else -w_est / 2))
        y = ay + 100 if side == "south" else ay - h_est - 20
        if side == "south":
            y = min(y, M.H_IMG - h_est - 70)
        x = max(10, min(x, M.W - w_est - 10))
        text_box(d, (x, y), t, f_xs, bg="#ffffee", anchor="lt")
        d.line([(ax, ay), (min(max(ax, x), x + w_est), y + (0 if side == "south" else h_est))], fill=K, width=2)
    for mk in p["markers"]:
        ax, ay = anchors[mk["id"]]
        text_box(d, (ax - 150, ay - 70), f"{mk['id']}\n{mk.get('label','')}\n相手: {mk.get('partner')}" + ("\n*既定（要確認）" if mk.get("status") == "default" else ""), f_xs, bg="#ffffee", anchor="lt")
    for o in p["openings"]:
        ax, ay = anchors[o["id"]]
        text_box(d, (ax - 60, ay - 14), "開口*要確認", f_xs, bg="#ffffff", pad=2)
    text_box(d, (20, M.H_IMG - 60), "白黒ワイヤー（平面図から機械生成）。黒塗り=戸口（幅・高さともキャラ2人分）／灰=登れない／破線=仕切りの開口（既定・要確認）", f_xs, anchor="lt", bg="#ffffff", outline=None)
    img.save(path)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("connections")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    probs = build(a.connections, a.out)
    print("problems:", probs)


if __name__ == "__main__":
    main()
