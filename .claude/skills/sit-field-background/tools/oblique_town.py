"""寺町全体の接続図一覧（白黒ワイヤー・FF攻略本風）。全MAPをノードにし、戸口・端の接続（door/edge）・寺町外の端点・円環・閉じた辺・体内入口イベントを載せる。

oblique_topology.py（幼稚園一式 TRM-02〜05 用の接続図）とは独立。あちらと connections.json は変更しない。
平面スペック（*-plan.json）と connections-teramachi.json（sit-oblique-town/1）から機械的に生成する。手描きしない。画像生成なし。

  uv run --with numpy --with opencv-python-headless --with pillow python3 -I oblique_town.py \
      docs/production/oblique-mocks/connections-teramachi.json --out docs/production/oblique-mocks \
      [--check-only] [--build]
出力（--out）: teramachi-connection-diagram.png（白黒の接続図）・teramachi-overview.png（カラーのレビュー用モック一覧）・
              teramachi-connections.md（接続表・マップ一覧・検査結果）・teramachi-assumptions.md（既定（要確認）の一覧）
検査（問題が1つでもあれば exit 1）: 端・戸口の相互参照（partner が互いに一致）・辺（反対側）・位置（辺上の座標）・幅の一致・
  全接続が宣言されていること・台帳（map-topology の接続行）との突合・屋外MAPの四辺が『接続』か『閉鎖』で埋まっていること・円環。
--build を付けると own_plans（今回作る屋外MAP）の個別ビルド（validate→mock→wire→mask→occlusion→prompt）も走らせる。
"""
import argparse
import json
import os
import re
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import oblique_mock as M  # noqa: E402
import oblique_topology as T  # noqa: E402
import oblique_text as X  # noqa: E402
import ledger_io as LIO  # noqa: E402

K = "#000000"
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))
OPP = {"north": "south", "south": "north", "west": "east", "east": "west"}
JA = {"north": "北", "south": "南", "west": "西", "east": "東"}
POS_TOL = X.const_num("town.position-tolerance")  # 辺上の座標の許容差（平面単位）
FRAC_TOL = X.const_num("town.fraction-tolerance")


def load_town(conn_path):
    with open(conn_path, encoding="utf-8") as f:
        C = json.load(f)
    if C.get("schema") != "sit-oblique-town/1":
        sys.exit("schema が sit-oblique-town/1 ではない")
    base = os.path.dirname(os.path.abspath(conn_path))
    plans = {}
    for fn in C["plans"]:
        p = M.load_plan(os.path.join(base, fn))
        plans[p["map_id"]] = p
    return C, base, plans


def index_ports(plans):
    """id -> (map, dict, kind)。kind=door|marker。"""
    ports = {}
    for mid, p in plans.items():
        for d in p["doors"]:
            ports[d["id"]] = (mid, d, "door")
        for m in p["markers"]:
            ports[m["id"]] = (mid, m, "marker")
    return ports


def read_ledger():
    """Read current YAML connections, excluding retired MAPs."""
    retired = {r["MAP_ID"] for r in LIO.read("MAP") if r["状態"] == "廃止"}
    rows = set()
    for row in LIO.read("接続"):
        ends = (row["端A"], row["端B"])
        if not any(end.startswith("TRM-") for end in ends):
            continue
        if any(end.split(".", 1)[0] in retired for end in ends):
            continue
        rows.add((frozenset(ends), row["種別"]))
    return rows, None


def check(C, plans, ports, ledger_rows):
    """(problems, notes, rows)。rows は接続表の行。"""
    problems, notes, rows = [], [], []
    virtual = C.get("virtual_ports", {})
    ext_ports = {pid: ex for ex in C["externals"] for pid in ex["ports"]}
    declared = set()
    for e in C["edges"]:
        a, b = e["a"], e["b"]
        declared.update((a, b))
        for end, ident in (("a", a), ("b", b)):
            if ident not in ports and ident not in virtual and ident not in ext_ports:
                problems.append(f"{ident} がスペック・仮想端点・外部ノードのどれにも無い（接続 {a}⇄{b}）")
        info = {}
        for end, ident in (("a", a), ("b", b)):
            if ident in ports:
                mid, dd, kind = ports[ident]
                if kind == "marker":
                    info[end] = {"map": mid, "kind": kind, "side": dd["edge"], "at": dd["at"], "w": M.marker_w(dd), "partner": dd.get("partner"), "status": dd.get("status", ""),
                                 "text": f"{JA[dd['edge']]}端 {dd['at']}", "frac": None}
                else:
                    pos, frac, wtxt = T.door_info(plans[mid], dd)
                    info[end] = {"map": mid, "kind": kind, "side": dd["wall_side"], "at": dd["center"], "w": M.door_w(dd), "partner": dd.get("partner"), "status": dd.get("status", ""),
                                 "text": pos, "frac": frac, "wc": dd.get("width_class", "2people")}
            elif ident in virtual:
                v = virtual[ident]
                info[end] = {"map": v["map"], "kind": "virtual", "side": "", "at": None, "w": None, "partner": None, "status": v.get("status", ""), "text": v.get("note", "仮想端点（イベント）"), "frac": None}
            else:
                ex = ext_ports.get(ident, {})
                info[end] = {"map": None, "kind": "external", "side": "", "at": None, "w": None, "partner": None, "status": "", "text": ex.get("note", "（寺町の外・別MAP）"), "frac": None}
        # partner 相互参照
        for end, other in (("a", b), ("b", a)):
            i = info[end]
            if i["kind"] in ("marker", "door"):
                if i["partner"] != other:
                    problems.append(f"{e['a'] if end == 'a' else e['b']} の partner が {i['partner']}（接続リストの相手 {other} と不一致）")
        verdict = "（外部ノード・整合検査なし）"
        ia, ib = info["a"], info["b"]
        if ia["kind"] == "marker" and ib["kind"] == "marker":
            sides_ok = ib["side"] == OPP[ia["side"]]
            pos_ok = abs(ia["at"] - ib["at"]) <= POS_TOL
            w_ok = ia["w"] == ib["w"]
            verdict = ("OK" if sides_ok and pos_ok and w_ok else "NG") + f"（辺{'反対側' if sides_ok else '不整合'}・位置差{abs(ia['at'] - ib['at']):.0f}単位・幅{'一致' if w_ok else f'不一致 {ia['w']}≠{ib['w']}'}）"
        elif ia["kind"] == "door" and ib["kind"] == "door":
            exp = e.get("expect", "same")
            if exp == "skip":
                verdict = "要確認（向き・位置は台帳に無く既定。検査対象外）"
            else:
                sides_ok = (ib["side"] == OPP[ia["side"]]) if exp == "opposite" else (ia["side"] == ib["side"])
                pos_ok = abs(ia["frac"] - ib["frac"]) <= FRAC_TOL
                w_ok = ia["wc"] == ib["wc"]
                verdict = ("OK" if sides_ok and pos_ok and w_ok else "NG") + f"（辺{'一致' if sides_ok else '不整合'}・位置差{abs(ia['frac'] - ib['frac']):.2f}・幅{'一致' if w_ok else '不一致'}）"
        elif {ia["kind"], ib["kind"]} & {"marker", "door"} and not ({ia["kind"], ib["kind"]} & {"virtual"}):
            pass
        if verdict.startswith("NG"):
            problems.append(f"{a}⇄{b}: {verdict}")
        rows.append((e, info, verdict))
    # 全接続が宣言されているか
    for ident, (mid, dd, kind) in ports.items():
        if dd.get("partner") and ident not in declared:
            problems.append(f"{ident} は partner があるのに connections-teramachi.json の接続に無い")
    # 台帳との突合
    if ledger_rows is not None:
        mine = {(frozenset((e["a"], e["b"])), e["kind"]) for e in C["edges"]}
        for r_ in sorted(ledger_rows - mine, key=lambda x: sorted(x[0])):
            problems.append(f"台帳（docs/ledger/接続.yaml）にあるが接続図に無い: {' ⇄ '.join(sorted(r_[0]))}（{r_[1]}）")
        for r_ in sorted(mine - ledger_rows, key=lambda x: sorted(x[0])):
            problems.append(f"接続図にあるが台帳（docs/ledger/接続.yaml）に無い（正本台帳または派生元を確認）: {' ⇄ '.join(sorted(r_[0]))}（{r_[1]}）")
        notes.append(f"台帳突合: 現行YAML台帳の寺町接続行（廃止MAPを除く）{len(ledger_rows)} 行、接続図の接続 {len(mine)} 本")
    # 四辺の被覆（屋外MAP）
    for mid, p in plans.items():
        if p.get("indoor") or "closed_edges" not in p:
            continue
        opened = {m["edge"] for m in p["markers"]}
        closed = {c["edge"] for c in p["closed_edges"]}
        for ed in ("north", "south", "west", "east"):
            if ed in opened and ed in closed:
                problems.append(f"{mid}: {JA[ed]}辺が接続と閉鎖の両方にある")
            if ed not in opened and ed not in closed:
                problems.append(f"{mid}: {JA[ed]}辺が接続にも閉鎖にも書かれていない")
    # 円環
    for ring in C.get("rings", []):
        ok = True
        for a_map, b_map in zip(ring["maps"], ring["maps"][1:] + ring["maps"][:1]):
            if not any({ports[e["a"]][0], ports[e["b"]][0]} == {a_map, b_map} for e in C["edges"] if e["a"] in ports and e["b"] in ports):
                ok = False
                problems.append(f"円環 {ring['name']}: {a_map}→{b_map} の接続が無い")
        if ok:
            notes.append(f"円環 {ring['name']}: " + " → ".join(ring["maps"] + ring["maps"][:1]) + " が接続図で辿れる")
    return problems, notes, rows


def stub_dir(i, e, end):
    d = e.get("a_dir" if end == "a" else "b_dir")
    if d:
        return d
    return i["side"] or "south"


def draw_town(C, plans, ports, rows, out):
    CW, CH = C["canvas"]
    img = Image.new("RGB", (CW, CH), "#ffffff")
    d = ImageDraw.Draw(img)
    f_t, f_m, f_s, f_xs = T.fnt(56), T.fnt(34), T.fnt(26), T.fnt(22)
    d.text((60, 40), C["title"], font=f_t, fill=K)
    d.text((60, 116), "白黒ワイヤーフレーム（平面スペックから機械生成。画像生成なし）。黒丸と太線=接続（点線矢印=一方向のイベント）。灰=歩けない。斜線=水路。破線枠=寺町の外／寺町内の未図示端点。", font=f_s, fill=K)
    door_widths = "／".join(f"{name}={value:g}" for name, value in M.WIDTH_CLASSES.items())
    marker_widths = sorted({M.marker_w(marker) for plan in plans.values() for marker in plan["markers"]})
    d.text((60, 156), f"×=閉鎖（歩行マスク=黒）。図の上が北。戸口幅: {door_widths}。端の幅: " + "／".join(f"{width:g}" for width in marker_widths) + "（平面単位。台帳由来）。", font=f_s, fill=K)
    anchors, boxes, tfs = {}, {}, {}
    for mid, cfg in C["cells"].items():
        p = plans[mid]
        crop, tf, anc, sc = T.render_cell(p, cfg["width"])
        x0, y0 = cfg["pos"]
        img.paste(crop, (x0, y0))
        d.rectangle([x0, y0, x0 + crop.width, y0 + crop.height], outline=K, width=3)
        for k, v in anc.items():
            anchors[k] = (v[0] + x0, v[1] + y0)
        boxes[mid] = (x0, y0, x0 + crop.width, y0 + crop.height)
        tfs[mid] = (tf, x0, y0)
        info = C.get("maps_info", {}).get(mid, {})
        kind = info.get("kind", "")
        sub = p.get("subtitle", "")
        title = f"{mid}（{kind}）\n{p['name']}" if kind else f"{mid}\n{p['name']}"
        tp = cfg.get("title_pos", "overlay")  # overlay=セルの左上に重ねる／above=上／below=下
        if tp == "below" or cfg.get("title_below"):
            T.text_box(d, (x0, y0 + crop.height + 14), title.replace("\n", "  ") + ("\n" + sub if sub and len(sub) < 60 else ""), f_m, anchor="lt")
        elif tp == "above":
            T.text_box(d, (x0, y0 - 100), title.replace("\n", "  ") + ("\n" + sub if sub and len(sub) < 60 else ""), f_m, anchor="lt")
        else:
            T.text_box(d, (x0 + 10, y0 + 10), title, f_s, bg="#ffffff", pad=4, anchor="lt")
        # 閉鎖の辺
        for ce in p.get("closed_edges", []):
            ed = ce["edge"]
            cx, cy = (x0 + crop.width / 2, y0 + crop.height / 2)
            bar = {"north": [(x0 + 30, y0 - 3), (x0 + crop.width - 30, y0 - 3)], "south": [(x0 + 30, y0 + crop.height + 3), (x0 + crop.width - 30, y0 + crop.height + 3)],
                   "west": [(x0 - 3, y0 + 30), (x0 - 3, y0 + crop.height - 30)], "east": [(x0 + crop.width + 3, y0 + 30), (x0 + crop.width + 3, y0 + crop.height - 30)]}[ed]
            d.line(bar, fill=K, width=12)
            lab = "×閉鎖" + ("（決定済み）" if ce.get("decided") else "")
            pos = {"north": (cx, y0 - 22), "south": (cx, y0 + crop.height + 24), "west": (x0 - 52, cy), "east": (x0 + crop.width + 52, cy)}[ed]
            if ed in ("west", "east"):
                lab = "×\n閉鎖" + ("\n決定済" if ce.get("decided") else "")
            if cfg.get("title_below") and ed == "south":
                continue
            T.text_box(d, pos, lab, f_xs, pad=3, outline=None)
    # 仮想端点（TRM-03.event-kiss など）
    for vid, v in C.get("virtual_ports", {}).items():
        tf, x0, y0 = tfs[v["map"]]
        pt = tf(M.proj(*v["at"]))
        anchors[vid] = (pt[0] + x0, pt[1] + y0)
        d.ellipse([anchors[vid][0] - 14, anchors[vid][1] - 14, anchors[vid][0] + 14, anchors[vid][1] + 14], outline=K, width=5, fill="#ffffff")
        d.ellipse([anchors[vid][0] - 6, anchors[vid][1] - 6, anchors[vid][0] + 6, anchors[vid][1] + 6], fill=K)
    # 外部ノード
    for ex in C["externals"]:
        x, y, w, h = ex["box"]
        d.rounded_rectangle([x, y, x + w, y + h], radius=14, outline=None if ex.get("dashed") else K, width=4, fill="#ffffff")
        if ex.get("dashed"):
            for a_, b_ in (((x, y), (x + w, y)), ((x + w, y), (x + w, y + h)), ((x + w, y + h), (x, y + h)), ((x, y + h), (x, y))):
                M.dashed(d, a_, b_, K, 4, dash=16)
        d.text((x + 16, y + 14), ex["label"], font=f_s, fill=K)
        for pid, (side, fr) in ex["ports"].items():
            pt = {"top": (x + w * fr, y), "bottom": (x + w * fr, y + h), "left": (x, y + h * fr), "right": (x + w, y + h * fr)}[side]
            anchors[pid] = pt
            d.ellipse([pt[0] - 9, pt[1] - 9, pt[0] + 9, pt[1] + 9], fill=K)
    # 線
    tags = []
    for e, info, verdict in rows:
        a, b = e["a"], e["b"]
        pa, pb = anchors[a], anchors[b]
        da, db = stub_dir(info["a"], e, "a"), stub_dir(info["b"], e, "b")
        if e.get("via"):
            pts = [pa] + [tuple(v) for v in e["via"]] + [pb]
        else:
            pts = T.route(pa, da, pb, db, stub=e.get("stub", 70))
        T.poly_line(d, pts, 6, dashed_line=(e["kind"] == "event"))
        for q in (pa, pb):
            d.ellipse([q[0] - 10, q[1] - 10, q[0] + 10, q[1] + 10], fill=K)
        if e["kind"] == "event":
            q, q2 = pts[-2], pts[-1]
            vx, vy = q2[0] - q[0], q2[1] - q[1]
            n = max(1, (vx * vx + vy * vy) ** 0.5); ux, uy = vx / n, vy / n
            d.polygon([(q2[0], q2[1]), (q2[0] - ux * 30 - uy * 14, q2[1] - uy * 30 + ux * 14), (q2[0] - ux * 30 + uy * 14, q2[1] - uy * 30 - ux * 14)], fill=K)
        seg = max(zip(pts[:-1], pts[1:]), key=lambda s: (s[0][0] - s[1][0]) ** 2 + (s[0][1] - s[1][1]) ** 2)
        mx, my = (seg[0][0] + seg[1][0]) / 2, (seg[0][1] + seg[1][1]) / 2
        if e.get("label_at"):
            mx, my = e["label_at"]
        ws = []
        for end in ("a", "b"):
            i = info[end]
            if i["w"]:
                ws.append(i["w"])
        wl = f"\n幅{min(ws):.0f}単位" if ws else ""
        lab = e["label"] + wl
        if verdict.startswith("OK"):
            lab += "  整合OK"
        tags.append((mx, my, lab))
    for mx, my, lab in tags:
        T.text_box(d, (mx, my), lab, f_xs, bg="#ffffff", outline=K)
    # 端・戸口のタグ
    for ident, (mid, dd, kind) in ports.items():
        if ident not in anchors:
            continue
        ax, ay = anchors[ident]
        star = "*" if dd.get("status") == "default" else ""
        if kind == "door":
            pos = T.door_info(plans[mid], dd)[0].split("（")[0]
            t = f"{ident}{star}\n{pos}"
        else:
            t = f"{ident}{star}\n{JA[dd['edge']]}端{dd['at']}・幅{M.marker_w(dd):.0f}"
        e = next((e for e in C["edges"] if ident in (e["a"], e["b"])), None)
        side = dd.get("wall_side") or dd.get("edge")
        dr = (e.get("a_dir") if e and e["a"] == ident else e.get("b_dir")) if e else None
        dr = dr or side
        w_est = max(d.textbbox((0, 0), s_, font=f_xs)[2] for s_ in t.split("\n")) + 12
        h_est = len(t.split("\n")) * 33 + 8
        if dr == "east":
            x, y = ax - w_est - 18, ay - h_est - 14
        elif dr == "west":
            x, y = ax + 18, ay - h_est - 14
        elif dr == "south":
            x, y = ax + 22, ay - h_est - 30
            if x + w_est > CW - 20:
                x = ax - w_est - 22
        else:
            x, y = ax + 22, ay + 16
        T.text_box(d, (x, y), t, f_xs, bg="#ffffee", anchor="lt")
    for vid, v in C.get("virtual_ports", {}).items():
        ax, ay = anchors[vid]
        T.text_box(d, (ax + 20, ay + 14), f"{vid}\n{v.get('note', '')}", f_xs, bg="#ffffee", anchor="lt")
    T.compass(d, CW - 120, 110, f_m)
    # 凡例
    lx, ly = C["legend_at"]
    lines = ["凡例と読み方"]
    items = ["黒丸と太線=端・戸口どうしの接続。点線矢印=一方向のイベント", "二重丸=仮想の端点（イベントの起点）", "×閉鎖=その辺は塀・壁・家並みで通れない", "*（IDの後ろ）=台帳に位置が無く仮置きした端・戸口（既定・要確認）", "整合OK=相手MAPの端・戸口と 辺（反対側）・位置・幅 が一致"] + list(C.get("legend_notes", []))
    for it in items:
        chunks = _wrap(it, 34)
        lines += ["・" + chunks[0]] + ["　" + c_ for c_ in chunks[1:]]
    T.text_box(d, (lx, ly), "\n".join(lines), f_s, bg="#ffffff", anchor="lt")
    img.save(os.path.join(out, "teramachi-connection-diagram.png"))


def _wrap(it, n):
    toks = re.split(r"(?<=[。・、／])", it)
    out, cur = [], ""
    for tk in toks:
        while len(tk) > n:
            if cur:
                out.append(cur); cur = ""
            out.append(tk[:n]); tk = tk[n:]
        if len(cur) + len(tk) > n and cur:
            out.append(cur); cur = ""
        cur += tk
    if cur:
        out.append(cur)
    return out


def draw_overview(C, plans, out):
    order = C.get("overview_order") or list(plans)
    cols = 4
    tw, th = 836, 470
    rows_n = (len(order) + cols - 1) // cols
    ov = Image.new("RGB", (tw * cols + 10 * (cols + 1), th * rows_n + 10 * (rows_n + 1) + 70), "#2b2b2b")
    od = ImageDraw.Draw(ov)
    od.text((15, 14), "寺町 全マップのモック一覧（レビュー用・カラー・ラベル付き。TRM-02〜05 は幼稚園一式）", font=T.fnt(30), fill="#ffffff")
    for i, mid in enumerate(order):
        r, _ = M.render(plans[mid], "color", labels=True)
        r = r.resize((tw, th), Image.LANCZOS)
        ov.paste(r, (10 + (i % cols) * (tw + 10), 70 + (i // cols) * (th + 10)))
    ov.save(os.path.join(out, "teramachi-overview.png"))


def write_md(C, plans, ports, rows, problems, notes, out):
    L = ["# 寺町 全マップの接続表・マップ一覧（機械生成。`oblique_town.py`。手で直さない）", "",
         "YAML正本から導出した平面スペックと接続JSONから生成。画像生成なし。対象: " + "、".join(sorted(plans)), "",
         "![寺町全体の接続図](teramachi-connection-diagram.png)", "", "![全マップのモック一覧](teramachi-overview.png)", "",
         "## 検査結果", ""]
    L += [f"- 問題: {len(problems)} 件" + ("" if not problems else "（下記）")] + [f"  - {x}" for x in problems]
    L += [f"- {n}" for n in notes]
    L += ["", "## マップ一覧（対象マップの洗い出し）", "", "| MAP | 名前 | 屋内外 | 出入口（端・戸口） | 閉鎖の辺 | 設計記述（台帳） |", "|---|---|---|---|---|---|"]
    for mid, p in plans.items():
        info = C.get("maps_info", {}).get(mid, {})
        pts = []
        for d_ in p["doors"]:
            pts.append(f"`{d_['id'].split('.', 1)[1]}`→{d_.get('partner')}")
        for m_ in p["markers"]:
            pts.append(f"{JA[m_['edge']]} `{m_['id'].split('.', 1)[1]}`→{m_.get('partner')}")
        ce = "・".join(f"{JA[c['edge']]}" + ("（決定済み）" if c.get("decided") else "") for c in p.get("closed_edges", [])) or "-"
        L.append(f"| {mid} | {p['name']} | {info.get('kind', '')} | " + "<br>".join(pts) + f" | {ce} | {info.get('design', p.get('design', ''))} |")
    L += ["", "## 接続表（戸口・端の相互参照）", "", "寺町の外・別MAPへの端点は検査対象外（相手のスペックが無い）。辺は『反対側』、位置は辺上の座標の差が" + f"{POS_TOL}単位以内（戸口は壁沿いの比が{FRAC_TOL}以内）、幅は一致、partner は互いに一致で OK。", "",
          "| 端・戸口A | Aの位置 | 端・戸口B | Bの位置 | 幅 | 種別 | 整合 | 備考 |", "|---|---|---|---|---|---|---|---|"]
    for e, info, verdict in rows:
        ws = [i["w"] for i in info.values() if i["w"]]
        note = []
        for end in ("a", "b"):
            if info[end]["status"] == "default":
                note.append(f"{e[end]} は既定（要確認）")
        if e.get("note"):
            note.append(e["note"])
        if e.get("ledger", "v2") != "v2":
            note.append(f"移行前の出典分類: {e['ledger']}")
        for vk, vr in e.get("disabled_in", {}).items():
            note.append(f"{vk} では無効（{vr}）")
        L.append(f"| `{e['a']}` | {info['a']['text']} | `{e['b']}` | {info['b']['text']} | {('%d単位' % min(ws)) if ws else '-'} | {e['kind']} | {verdict} | {'・'.join(note) or '-'} |")
    L += ["", "## 閉鎖の辺", "", "| MAP | 辺 | 理由 |", "|---|---|---|"]
    for mid, p in plans.items():
        for c in p.get("closed_edges", []):
            L.append(f"| {mid} | {JA[c['edge']]} | {c['reason']} |")
    with open(os.path.join(out, "teramachi-connections.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")


def write_assumptions(C, plans, out):
    L = ["# 寺町の残りマップ: 要確認（既定）の一覧（機械生成。`oblique_town.py`。手で直さない）", "",
         "設計（台帳・kako-jun の決定）に無く、モックのために仮置きした寸法・位置・物の一覧。各 `docs/production/oblique-mocks/TRM-XX-plan.json` の `assumptions` から集約。正しい値が決まったら docs/ledger の正本を直し ledger_build.py build で再生成する。"
         "（TRM-02〜05 の既定は各 plan の assumptions・`windows.md` を参照。ここは対象外）", ""]
    total = 0
    body = []
    for mid in C.get("own_plans_order", []):
        p = plans[mid]
        items = [a for a in p.get("assumptions", [])]
        total += len(items)
        body += [f"## {mid} {p['name']}（{len(items)} 件）", ""] + [f"- {a}" for a in items] + [""]
    L += [f"合計 {total} 件（{len(C.get('own_plans_order', []))} マップ）。共通の既定（全マップに共通する仮置き）は次のとおり。", ""]
    L += [f"- {a}" for a in C.get("cross_assumptions", [])] + [""]
    L += body
    with open(os.path.join(out, "teramachi-assumptions.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    return total


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("connections")
    ap.add_argument("--out", required=True)
    ap.add_argument("--no-ledger", action="store_true")
    ap.add_argument("--check-only", action="store_true", help="接続の検査だけ実行し画像・Markdownを出力しない")
    ap.add_argument("--build", action="store_true", help="own_plans の個別ビルド（oblique_build.build_one）も実行")
    a = ap.parse_args()
    if not a.check_only:
        os.makedirs(a.out, exist_ok=True)
    C, base, plans = load_town(a.connections)
    ports = index_ports(plans)
    if a.build:
        import oblique_build as B
        for fn in C.get("own_plans", []):
            _, errs = B.build_one(os.path.join(base, fn), base)
            if errs:
                sys.exit(f"{fn}: validate エラー")
    ledger_rows = None
    if not a.no_ledger:
        ledger_rows, err = read_ledger()
        if err:
            print("台帳を読めない:", err)
    problems, notes, rows = check(C, plans, ports, ledger_rows)
    if a.check_only:
        for problem in problems:
            print(problem)
        print(f"connections: {len(rows)}; problems: {len(problems)}")
        sys.exit(1 if problems else 0)
    draw_town(C, plans, ports, rows, a.out)
    draw_overview(C, plans, a.out)
    write_md(C, plans, ports, rows, problems, notes, a.out)
    total = write_assumptions(C, plans, a.out)
    print("接続:", len(rows), "本 / 問題:", len(problems), "/ 既定（要確認）:", total, "件")
    for n in notes:
        print(" -", n)
    for p_ in problems:
        print(" !!", p_)
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
