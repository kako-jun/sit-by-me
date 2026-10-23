"""斜め視点マップの一括ビルド（Make 風）。平面スペック1つ → 全決定論の成果物。途中から再開できる。

段階（上から順。入力 hash が前回と同じ段はスキップ、変わった段以降だけ再実行）:
  validate  平面スペックのスキーマ・整合の検査（欠落・戸口の相手不一致・幅不足・戸口前の障害物・到達不能）
  mock      クリーン版（imagegen 編集元・ラベルなし）とレビュー版（ラベル付き）
  wire      個別の白黒ワイヤー図（昔の攻略本流）
  mask      歩行マスク（床=白・blocked=黒・戸口=出口範囲）
  occlusion 手前オクルージョンマスク（壁・背の高い家具がキャラを隠す領域。深度つき）
  prompt    imagegen 編集用プロンプトを機械生成（台帳 ready でなければ blocked と記録。生成そのものはしない）
  --- 承認ゲート（全MAPのモック・接続図を kako-jun がレビュー）---
  adopt     （手動）採用画像を記録: --adopt IMAGE [--take N]
  verify    （手動）採用記録の鮮度検査（モック/プロンプトが変わっていないか・寸法）
画像認識や LLM を使うのは承認後の imagegen だけ。ここまでは全部スクリプト。

使い方:
  uv run --with numpy --with opencv-python-headless --with pillow python3 -I oblique_build.py PLAN.json [--variant kids] [--from STAGE] [--force]
  uv run ... oblique_build.py --all docs/production/oblique-mocks/connections.json   # 全MAP＋接続図・一覧・接続表
  uv run ... oblique_build.py --status docs/production/oblique-mocks/connections.json
  uv run ... oblique_build.py PLAN.json --adopt path/to/adopted.png --take 3
出力: <out>/<MAP>/ に成果物と manifest.json（各段の入力 hash・出力 sha256。台帳の行へのリンク）。
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import oblique_mock as M  # noqa: E402
import oblique_topology as T  # noqa: E402
from PIL import Image  # noqa: E402

STAGES = ["validate", "mock", "wire", "mask", "occlusion", "prompt"]
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
ID_RE = re.compile(r"^[A-Z]{3}-\d{2}\.[A-Za-z0-9-]+$")
PROMPT_VERSION = "oblique-edit-prompt/3"
DECOR_FILE = os.path.join(REPO, "docs", "production", "oblique-mocks", "decor-pools.json")
DECOR_LAYER_KEYS = ("desk", "slab_edge", "outside", "building")
DECOR_REQUIRED = ("geometry_fixed", "fill_rule", "layers", "surfaces", "kinds", "allow", "forbid")


def load_decor(p):
    """plan の decor_pool が指す装飾プール（sit-oblique-decor/1）を返す。無ければ None。"""
    pid = p.get("decor_pool")
    if not pid:
        return None
    with open(DECOR_FILE, encoding="utf-8") as f:
        doc = json.load(f)
    return doc["pools"].get(pid) if doc.get("schema") == "sit-oblique-decor/1" else None


def box_look(b, pool):
    return b.get("look") or ((pool or {}).get("kinds", {}).get(b.get("kind", "")) or "")


def validate_decor(p, E, Wn):
    pid = p.get("decor_pool")
    if not pid:
        Wn.append("decor_pool 未指定: edit-prompt に見た目（look）と許す/禁じる装飾が出ない（簡素な絵になりやすい。E2 round1 の失敗）")
        return
    try:
        with open(DECOR_FILE, encoding="utf-8") as f:
            doc = json.load(f)
    except Exception as ex:  # noqa: BLE001
        E.append(f"decor-pools.json を読めない: {ex}"); return
    if doc.get("schema") != "sit-oblique-decor/1":
        E.append("decor-pools.json の schema が sit-oblique-decor/1 でない"); return
    pool = doc.get("pools", {}).get(pid)
    if pool is None:
        E.append(f"decor_pool {pid} が decor-pools.json に無い"); return
    for k in DECOR_REQUIRED:
        if not pool.get(k):
            E.append(f"decor_pool {pid}: {k} が必要")
    for lk in DECOR_LAYER_KEYS:
        ly = (pool.get("layers") or {}).get(lk)
        if not (isinstance(ly, dict) and ly.get("look") and ly.get("fixed")):
            E.append(f"decor_pool {pid}: layers.{lk} に look と fixed が必要")
    for sk in ("wall", "floor", "door", "window"):
        if not (pool.get("surfaces") or {}).get(sk):
            E.append(f"decor_pool {pid}: surfaces.{sk} が必要")
    for b in p["boxes"]:
        if not box_look(b, pool):
            E.append(f"boxes {b['id']}: look（または pool.kinds に載る kind）が必要")



def sha_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha_file(path):
    with open(path, "rb") as f:
        return sha_bytes(f.read())


def src_sha(*names):
    return sha_bytes(b"".join(open(os.path.join(HERE, n), "rb").read() for n in names))


# ---------------------------------------------------------------- 検査

def plan_free_grid(p, cell=2):
    """平面（土台 1600x1270 単位）で歩ける所の格子。床（no_step=踏ませない床は除く）＋戸口・開口の通り道、から壁・blocked の箱を引く。"""
    import numpy as np
    import cv2
    gw, gh = M.BASE_W // cell, M.BASE_D // cell
    g = np.zeros((gh, gw), np.uint8)

    def fill(rc, v):
        x0, y0, x1, y1 = [int(round(c / cell)) for c in rc]
        g[max(0, y0):max(0, y1), max(0, x0):max(0, x1)] = v
    for f in p["floors"]:
        if f.get("walkable", True) and not f.get("no_step"):
            fill(f["rect"], 255)
    for f in p["floors"]:
        if f.get("no_step"):
            fill(f["rect"], 0)
    for w in p["walls"]:
        fill(w["rect"], 0)
    for bx in p["boxes"]:
        if bx.get("blocked"):
            fill(bx["rect"], 0)
    for o in p["openings"]:
        w = M.wall_by_id(p, o["wall"]); r = w["rect"]; a, b_ = M.span(o)
        fill([a, r[1], b_, r[3]] if M.is_h(w) else [r[0], a, r[2], b_], 255)
    for d in p["doors"]:
        w = M.wall_by_id(p, d["wall"]); r = w["rect"]; a, b_ = M.span(d)
        fill([a, r[1], b_, r[3]] if M.is_h(w) else [r[0], a, r[2], b_], 255)
    return g


def endpoint(p, ident):
    """戸口・開口の通り道の入口の平面点（歩く側へ少し入った所）。"""
    for d in p["doors"] + p["openings"]:
        if d["id"] == ident:
            w = M.wall_by_id(p, d["wall"]); r = w["rect"]
            face = d.get("face", "east")
            if M.is_h(w):
                return (d["center"], (r[1] - 100) if face == "north" else (r[3] + 100))
            return ((r[0] - 100) if face == "west" else (r[2] + 100), d["center"])
    return None


def check_paths(p):
    """paths[]: 戸口⇄開口の通り道に、戸口幅（キャラ2人分）の通路を確保できるか。no_step の床・blocked の箱の上は通らない。"""
    import numpy as np
    import cv2
    E = []
    if not p.get("paths"):
        return E
    cell = 2
    g = plan_free_grid(p, cell)
    for pa in p["paths"]:
        half = (pa.get("min_width", M.DOOR_W) / 2 - 2) / cell
        k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (int(2 * half) + 1, int(2 * half) + 1))
        er = cv2.erode(g, k)
        a, b_ = endpoint(p, pa["from"]), endpoint(p, pa["to"])
        if a is None or b_ is None:
            E.append(f"paths {pa.get('id')}: from/to の戸口・開口が無い"); continue
        sa = (int(a[0] / cell), int(a[1] / cell)); sb = (int(b_[0] / cell), int(b_[1] / cell))
        n, lab = cv2.connectedComponents((er > 0).astype(np.uint8))
        la, lb = lab[sa[1], sa[0]], lab[sb[1], sb[0]]
        if la == 0 or lb == 0 or la != lb:
            E.append(f"paths {pa.get('id')}: {pa['from']} から {pa['to']} へ幅{pa.get('min_width', M.DOOR_W)}（キャラ2人分）の通路が取れない（布団・長持・家具が通路に乗っている、または狭い）")
    return E

def validate_plan(p):
    """(errors, warnings)。errors があれば後段へ進まない。"""
    E, Wn = [], []
    for k in ("map_id", "name"):
        if not p.get(k):
            E.append(f"必須項目 {k} が無い")
    ids = {}

    def reg(kind, e):
        if "id" not in e:
            E.append(f"{kind} に id が無い: {e}")
            return
        if e["id"] in ids:
            E.append(f"id 重複: {e['id']}")
        ids[e["id"]] = kind

    def rect_ok(kind, e):
        r = e.get("rect")
        if not (isinstance(r, list) and len(r) == 4 and all(isinstance(v, (int, float)) for v in r)):
            E.append(f"{kind} {e.get('id')}: rect は [x0,y0,x1,y1]"); return False
        if r[2] <= r[0] or r[3] <= r[1]:
            E.append(f"{kind} {e['id']}: rect の大きさが0以下 {r}"); return False
        if r[0] < 0 or r[1] < 0 or r[2] > M.BASE_W or r[3] > M.BASE_D:
            E.append(f"{kind} {e['id']}: 土台（{M.BASE_W}x{M.BASE_D}）の外に出ている {r}")
        return True

    for kind in ("floors", "walls", "boxes"):
        for e in p[kind]:
            reg(kind, e)
            if rect_ok(kind, e):
                if kind in ("walls", "boxes") and e.get("h", 0) <= 0:
                    E.append(f"{kind} {e['id']}: h（高さ）が必要")
                if kind != "walls" and kind != "floors" and "color" not in e:
                    E.append(f"boxes {e['id']}: color が必要")
                if kind == "floors" and "color" not in e:
                    E.append(f"floors {e['id']}: color が必要")
    walls = {w["id"]: w for w in p["walls"] if "rect" in w and "id" in w}
    seen_span = {}
    for kind in ("doors", "openings"):
        for d in p[kind]:
            reg(kind, d)
            did = d.get("id", "?")
            if d.get("wall") not in walls:
                E.append(f"{kind} {did}: wall {d.get('wall')} が無い"); continue
            w = walls[d["wall"]]
            r = w["rect"]
            if d.get("wall_side") not in M.__dict__.get("_SIDES", ("north", "south", "west", "east")):
                E.append(f"{kind} {did}: wall_side が north/south/west/east でない")
            if kind == "doors" and d.get("face") not in ("north", "south", "west", "east"):
                E.append(f"doors {did}: face（歩く側）が必要")
            if not isinstance(d.get("center"), (int, float)):
                E.append(f"{kind} {did}: center が必要"); continue
            if not (isinstance(d.get("along_ref"), list) and len(d["along_ref"]) == 2 and d["along_ref"][1] > d["along_ref"][0]):
                E.append(f"{kind} {did}: along_ref [a,b] が必要（位置の比の基準）")
            lo, hi = (r[0], r[2]) if M.is_h(w) else (r[1], r[3])
            a, b = M.span(d)
            if d.get("width_class", "2people") not in M.WIDTH_CLASSES:
                E.append(f"{kind} {did}: width_class は {list(M.WIDTH_CLASSES)}")
            if kind == "doors" and "width_class" not in d:
                E.append(f"doors {did}: width_class（2people|1person）が必要")
            if a < lo or b > hi:
                E.append(f"{kind} {did}: 戸口の幅（{d.get('width_class','2people')}={M.door_w(d):.0f}）が壁の長さに収まらない（壁 {lo}〜{hi}、戸口 {a:.0f}〜{b:.0f}）")
            if kind == "doors":
                if M.DOOR_H > w["h"]:
                    E.append(f"doors {did}: 戸口の高さ{M.DOOR_H}（キャラ2人分）が壁の高さ{w['h']}を超える")
                pr = d.get("partner")
                if not pr or not ID_RE.match(pr):
                    E.append(f"doors {did}: partner（相手の door ID。MAP-ID.name の形）が必要")
                if not ID_RE.match(did):
                    E.append(f"doors {did}: id は MAP-ID.name の形")
            seen_span.setdefault(d["wall"], []).append((a, b, did))
    for wid, spans in seen_span.items():
        spans.sort()
        for (a1, b1, i1), (a2, b2, i2) in zip(spans[:-1], spans[1:]):
            if a2 < b1:
                E.append(f"壁 {wid}: {i1} と {i2} の戸口・開口が重なる")
    for m in p["markers"]:
        reg("markers", m)
        if m.get("edge") not in ("north", "south", "west", "east"):
            E.append(f"markers {m.get('id')}: edge が不正")
        if not m.get("partner") or not ID_RE.match(m["partner"]):
            E.append(f"markers {m.get('id')}: partner が必要")
    # 窓
    for wn in p["windows"]:
        reg("windows", wn)
        wid = wn.get("id", "?")
        if wn.get("wall") not in walls:
            E.append(f"windows {wid}: wall {wn.get('wall')} が無い"); continue
        w = walls[wn["wall"]]; r = w["rect"]
        if wn.get("kind") not in M.WINDOW_KINDS:
            E.append(f"windows {wid}: kind は {list(M.WINDOW_KINDS)} のどれか（掃き出し=floor・腰高=waist）"); continue
        if wn.get("status") not in ("fixed", "default"):
            E.append(f"windows {wid}: status は fixed|default")
        for k in ("center", "width", "sill", "height"):
            if not isinstance(wn.get(k), (int, float)):
                E.append(f"windows {wid}: {k} が必要")
        if not isinstance(wn.get("center"), (int, float)) or not isinstance(wn.get("width"), (int, float)) or not isinstance(wn.get("sill"), (int, float)) or not isinstance(wn.get("height"), (int, float)):
            continue
        if wn["kind"] == "floor" and wn["sill"] != 0:
            E.append(f"windows {wid}: 掃き出し窓は sill=0（床まで届く）")
        if wn["kind"] == "waist" and wn["sill"] <= 0:
            E.append(f"windows {wid}: 腰高窓は sill>0")
        lo, hi = (r[0], r[2]) if M.is_h(w) else (r[1], r[3])
        a, b = wn["center"] - wn["width"] / 2, wn["center"] + wn["width"] / 2
        if a < lo or b > hi:
            E.append(f"windows {wid}: 壁の長さに収まらない（壁 {lo}〜{hi}、窓 {a:.0f}〜{b:.0f}）")
        if wn["sill"] + wn["height"] > w["h"]:
            E.append(f"windows {wid}: 窓の上端 {wn['sill'] + wn['height']} が壁の高さ {w['h']} を超える")
        for d in p["doors"] + p["openings"]:
            if d.get("wall") == wn["wall"]:
                da, db = M.span(d)
                top = M.DOOR_H if d in p["doors"] else w["h"]
                if a < db and b > da and wn["sill"] < top:
                    E.append(f"windows {wid}: 戸口・開口 {d['id']} と重なる")
        for o in p["windows"]:
            if o is not wn and o.get("wall") == wn["wall"] and isinstance(o.get("center"), (int, float)):
                oa, ob = o["center"] - o["width"] / 2, o["center"] + o["width"] / 2
                if a < ob and b > oa:
                    E.append(f"windows {wid}: 窓 {o['id']} と重なる")
        face = r[3] if M.is_h(w) else M.visible_face_x(w)
        for bx in p["boxes"]:
            q = bx["rect"]
            if M.is_h(w):
                adj = abs(q[1] - face) <= 2 and q[0] < b and q[2] > a
            else:
                adj = (abs(q[0] - face) <= 2 or abs(q[2] - face) <= 2) and q[1] < b and q[3] > a
            if adj and bx["h"] > wn["sill"]:
                E.append(f"windows {wid}: 家具 {bx['id']} が窓の前をふさぐ")
    for w in p["walls"]:
        n = sum(1 for x in p["windows"] if x.get("wall") == w["id"])
        if w.get("window_count", 0) != n:
            E.append(f"壁 {w['id']}: window_count={w.get('window_count', 0)} と windows[] の実数 {n} が不一致")
    for nw in p.get("no_window_walls", []):
        if nw.get("wall") not in walls:
            E.append(f"no_window_walls: wall {nw.get('wall')} が無い")
        elif any(x.get("wall") == nw["wall"] for x in p["windows"]):
            E.append(f"no_window_walls: 壁 {nw['wall']} は窓なしと確定しているのに windows[] がある")
    E += check_paths(p)
    # 戸口の前（歩く側）を blocked の箱が塞いでいないか
    for d in p["doors"]:
        if d.get("wall") not in walls or d.get("face") not in ("north", "south", "west", "east"):
            continue
        w = walls[d["wall"]]; r = w["rect"]; a, b = M.span(d)
        pad = 80
        if M.is_h(w):
            zone = [a, r[1] - pad, b, r[1]] if d["face"] == "north" else [a, r[3], b, r[3] + pad]
        else:
            zone = [r[0] - pad, a, r[0], b] if d["face"] == "west" else [r[2], a, r[2] + pad, b]
        for bx in p["boxes"]:
            if bx.get("blocked"):
                q = bx["rect"]
                if q[0] < zone[2] and q[2] > zone[0] and q[1] < zone[3] and q[3] > zone[1]:
                    E.append(f"doors {d['id']}: 戸口の前（{pad}単位）を箱 {bx['id']} が塞いでいる")
    if not E:
        # 到達性: 全出口が同じ白成分
        try:
            _, _, exits, n, comps = M.derive_mask(p)
            if exits:
                common = set(comps[exits[0]["id"]])
                for e in exits[1:]:
                    common &= set(comps[e["id"]])
                if not common:
                    E.append(f"出口どうしが歩行マスク上でつながらない: { {k: v for k, v in comps.items()} }")
                for e in exits:
                    if not comps[e["id"]]:
                        E.append(f"出口 {e['id']} が歩行マスクの白に重ならない")
        except Exception as ex:  # noqa: BLE001
            E.append(f"マスク導出に失敗: {ex}")
    for a_ in p.get("assumptions", []):
        Wn.append(a_)
    for d in p["doors"] + p["openings"]:
        if d.get("status") == "default":
            Wn.append(f"既定（要確認）: {d['id']}")
    validate_decor(p, E, Wn)
    return E, Wn


# ---------------------------------------------------------------- プロンプト
def build_prompt(p, key):
    """imagegen 編集用プロンプト（決定論）。モック=編集元1枚。原文束は台帳（build_map_prompt.rb）に依存するので別セクション。"""
    pool = load_decor(p)
    if pool:
        L = [f"# {PROMPT_VERSION} {key}", "",
             "ROLE: 添付のモック画像（色付きの箱で作った間取りの斜め見下ろし図）を編集して、手作りミニチュア（段ボールの台座・綿の雪・紙粘土の木・木目の床の工作）の一枚絵に仕上げる。モックは**位置と大きさを正確にするための型**で、見た目の完成形ではない。",
             f"GEOMETRY（固定。ここだけが『足さない・消さない・ずらさない』）: {pool['geometry_fixed']}",
             f"FILL（装飾。簡素にしない）: {pool['fill_rule']}",
             "DOORS: 濃いピンクの四角は戸口。その位置・幅・高さのまま、木の板戸または開口として描く（高さはキャラ2人分。幅は戸口ごとに下記）。ピンクの色は残さない。",
             "NO TEXT: 画像に文字・数字・矢印・ラベルを入れない。人物は入れない。", "",
             "LAYERS（外から内へ。層の境界の位置・形はモックのまま。質感と装飾で埋める）:"]
        for k in DECOR_LAYER_KEYS:
            ly = pool["layers"][k]
            L.append(f"- {ly.get('label', k)}: {ly['look']} 固定: {ly['fixed']}")
        L += ["", "SURFACES（建物の面）:"] + [f"- {k}: {v}" for k, v in pool["surfaces"].items()]
        for w in p["walls"]:
            if w.get("look"):
                L.append(f"- 壁 {w['id']}: {w['look']}")
        L += ["", "OBJECTS (色付きの箱 → 実物。位置・大きさ・高さは箱のまま。見た目で十分に作り込む):"]
        for b in p["boxes"]:
            L.append(f"- {b['id']}（{b.get('label') or '箱'}）: 高さ{b['h']}。{'登れない・通れない物' if b.get('blocked') else '歩ける物'}。見た目: {box_look(b, pool)}" + (f"。{b['prompt']}" if b.get("prompt") else ""))
    else:
        L = [f"# {PROMPT_VERSION} {key}", "",
             "ROLE: 添付のモック画像（色付きの箱で作った間取りの斜め見下ろし図）を編集して、手作りミニチュア（段ボールの土台・雪・木の質感）の一枚絵に仕上げる。",
             "GEOMETRY (必ず保つ): 画像の寸法・視点・土台の台形・壁の位置と高さ・箱の位置と大きさ・戸口の位置と大きさを一切動かさない。足さない・消さない・ずらさない。",
             "DOORS: 濃いピンクの四角は戸口。その位置・幅・高さのまま、木の扉または開口として描く（高さはキャラ2人分。幅は戸口ごとに下記）。ピンクの色は残さない。",
             "NO TEXT: 画像に文字・矢印・ラベルを入れない。人物は入れない。", "",
             "OBJECTS (色付きの箱 → 実物。位置・大きさは箱のまま):"]
        for b in p["boxes"]:
            L.append(f"- {b['id']}（{b.get('label') or '箱'}）: 高さ{b['h']}。{'登れない・通れない物' if b.get('blocked') else '歩ける物'}" + (f"。{b['prompt']}" if b.get("prompt") else ""))
    for w in p["walls"]:
        if w.get("kind") == "partition":
            L.append(f"- {w['id']}: 仕切り（壁より低い。壁と区別できる別素材で描く）。開口は箱の切れ目のまま")
    ops = [d for d in p["openings"]] + [d for d in p["doors"] if d.get("passage")]
    rps = [w for w in p["walls"] if w.get("kind") == "roof-passage"]
    if ops or rps:
        L += ["", "OPEN PASSAGES（左右・横方向に行き来する開口。壁に見せない）:"]
        for o in ops:
            L.append(f"- {o['id']}（{o['wall']}・中心{o['center']}・幅{M.door_w(o) if 'width_class' in o or o in p['doors'] else M.DOOR_W:.0f}）: 開口の上に梁・鴨居・垂れ壁・壁を描かない。奥まで見通せる開放した通路")
        for w in rps:
            L.append(f"- {w['id']}（{w.get('label') or '渡り廊下'}）: 屋根を柱で支えるだけの開放した通路（壁・窓・格子・戸を描かない）。屋根の下を左右へ奥まで見通せる。床は木の板張り（確定・茶色の板）。石の床にしない")
    if p["doors"]:
        WN = {"1person": "キャラ1人分（細い裏口）", "1.5people": "キャラ1.5人分", "2people": "キャラ2人分"}
        L += ["", "DOOR WIDTHS:"] + [f"- {d['id']}: 幅{WN[d.get('width_class', '2people')]}（{M.door_w(d):.0f}平面単位）・{d['wall_side']}壁" for d in p["doors"]]
    if p["windows"]:
        L += ["", "WINDOWS（個数・位置・種別を固定。ずらさない・増減しない・扉にしない。ガラス越しに見えるのは室内の床で、窓の中に雪や木・外の景色を描かない）:"]
        for w in p["walls"]:
            ws = sorted([x for x in p["windows"] if x["wall"] == w["id"]], key=lambda x: x["center"])
            if not ws:
                continue
            ax = "left to right" if M.is_h(w) else "back to front"
            kinds = {M.WINDOW_KINDS[x["kind"]] for x in ws}
            lo, hi = ws[0].get("along_ref", [0, 1])
            pos = ", ".join(f"#{i+1} at {(x['center']-lo)/(hi-lo):.2f}" for i, x in enumerate(ws))
            L.append(f"- 壁 {w['id']}（{w.get('label') or w.get('kind','wall')}）: {len(ws)}枚の{'・'.join(sorted(kinds))}。{ax}: {pos}（壁沿いの比）。窓台高さ{ws[0]['sill']}・高さ{ws[0]['height']}・幅{ws[0]['width']}（平面単位）")
    for nw in p.get("no_window_walls", []):
        L.append(f"- 壁 {nw['wall']}: 窓は描かない（0枚・確定: {nw.get('reason','')}）。壁に窓・格子窓・採光窓を足さない")
    L += ["", "FLOORS:"] + [f"- {f['id']}（{f.get('label') or ''}）{'歩ける' if f.get('walkable', True) else '歩けない'}" + (f"。見た目: {f['look']}" if f.get("look") else "") for f in p["floors"]]
    if pool:
        L += ["", "ALLOWED DECORATION（許す。積極的に使って面を埋める）:"] + [f"- {a}" for a in pool["allow"]]
        L += ["", "FORBIDDEN（禁じる。これだけは守る）:"] + [f"- {a}" for a in pool["forbid"]]
    L += ["", f"ASSUMPTIONS（既定・要確認）:"] + [f"- {a}" for a in p.get("assumptions", [])]
    return "\n".join(L) + "\n"


def ledger_gate(map_id):
    """台帳（build_map_prompt.rb）が ready か。戻り (ready, text)。"""
    base = re.sub(r"-(kids|fire|burnt|wc)$", "", map_id)
    script = os.path.join(REPO, "scripts", "build_map_prompt.rb")
    if not os.path.exists(script):
        return False, "scripts/build_map_prompt.rb が無い"
    try:
        r = subprocess.run(["ruby", script, base], capture_output=True, text=True, timeout=60)
        return r.returncode == 0 and "blocked" not in r.stdout[:200], (r.stdout + r.stderr).strip()
    except Exception as ex:  # noqa: BLE001
        return False, f"ruby 実行失敗: {ex}"


# ---------------------------------------------------------------- manifest
def load_manifest(path):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {"schema": "sit-oblique-manifest/1", "stages": {}}


def save_manifest(path, m):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(m, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")


def build_one(plan_path, outroot, variant=None, from_stage=None, force=False, log=print):
    p = M.load_plan(plan_path, variant)
    key = p["map_id"]
    out = os.path.join(outroot, key)
    os.makedirs(out, exist_ok=True)
    mpath = os.path.join(out, "manifest.json")
    man = load_manifest(mpath)
    plan_sha = sha_file(plan_path) + (f"+{variant}" if variant else "")
    tool_mock = src_sha("oblique_mock.py")
    tool_topo = src_sha("oblique_mock.py", "oblique_topology.py")
    man.update({"map_id": key, "plan": os.path.relpath(plan_path, REPO), "plan_sha256": plan_sha,
                "ledger": {"registry": "docs/map-asset-registry.md", "checklist": "docs/map-contract-checklist.md",
                           "row_id": re.sub(r"-(kids|fire|burnt|wc)$", "", key), "era_suffix": variant}})
    inputs = {"validate": sha_bytes((plan_sha + tool_mock + src_sha("oblique_build.py")).encode()),
              "mock": sha_bytes((plan_sha + tool_mock).encode()), "wire": sha_bytes((plan_sha + tool_topo).encode()),
              "mask": sha_bytes((plan_sha + tool_mock).encode()), "occlusion": sha_bytes((plan_sha + tool_mock).encode()),
              "prompt": sha_bytes((plan_sha + PROMPT_VERSION + tool_mock + (sha_file(DECOR_FILE) if os.path.exists(DECOR_FILE) else "")).encode())}
    dirty = bool(force)
    errors = []
    for st in STAGES:
        if from_stage == st:
            dirty = True
        rec = man["stages"].get(st, {})
        fresh = (rec.get("input_sha") == inputs[st] and all(os.path.exists(os.path.join(out, o)) and sha_file(os.path.join(out, o)) == h for o, h in rec.get("outputs", {}).items()) and rec.get("status") in ("ok", "blocked"))
        if fresh and not dirty:
            log(f"[{key}] {st}: skip（入力 hash 同じ）")
            if st == "validate" and rec.get("status") == "ok":
                pass
            continue
        dirty = True  # 以降は再実行
        if st == "validate":
            errs, warns = validate_plan(p)
            man["stages"][st] = {"input_sha": inputs[st], "status": "error" if errs else "ok", "outputs": {}, "errors": errs, "warnings": warns}
            log(f"[{key}] validate: {'ERROR ' + str(len(errs)) if errs else 'ok'}（警告・既定要確認 {len(warns)}）")
            for e in errs:
                log("   ERROR: " + e)
            if errs:
                errors = errs
                save_manifest(mpath, man)
                return man, errs
            continue
        files, extra = [], {}
        if st == "mock":
            files = M.write_mock(p, out)
        elif st == "wire":
            fn = f"wire-{key}.png"
            T.wire_single(p, os.path.join(out, fn), None)
            files = [fn]
        elif st == "mask":
            files, doc = M.write_mask(p, out)
            extra = {"white_components": doc["white_components"], "exit_components": doc["exit_components"]}
        elif st == "occlusion":
            files = M.write_occlusion(p, out)
        elif st == "prompt":
            text = build_prompt(p, key)
            fn = f"{key}-edit-prompt.txt"
            ready, gate_text = ledger_gate(key)
            with open(os.path.join(out, fn), "w", encoding="utf-8") as f:
                f.write(text)
                f.write("\n# ---- 台帳ゲート（scripts/build_map_prompt.rb）----\n")
                f.write(("READY\n" if ready else "BLOCKED（原文束は未取得。台帳の TBD を埋めて ready にしてから）\n") + gate_text + "\n")
            files = [fn]
            extra = {"ledger_ready": ready}
        man["stages"][st] = {"input_sha": inputs[st], "status": "ok" if st != "prompt" or extra.get("ledger_ready") else "blocked",
                             "outputs": {fn: sha_file(os.path.join(out, fn)) for fn in files}, **extra}
        log(f"[{key}] {st}: 実行 → {', '.join(files)}")
    save_manifest(mpath, man)
    return man, errors


def adopt(plan_path, outroot, image, take, variant=None):
    p = M.load_plan(plan_path, variant)
    key = p["map_id"]
    out = os.path.join(outroot, key)
    mpath = os.path.join(out, "manifest.json")
    man = load_manifest(mpath)
    im = Image.open(image)
    if im.size != (M.W, M.H_IMG):
        sys.exit(f"採用画像の寸法が {M.W}x{M.H_IMG} でない: {im.size}（リサイズで通さない。例外は kako-jun の承認＋記録）")
    pr = man["stages"].get("prompt", {})
    mk = man["stages"].get("mock", {})
    if not pr or not mk:
        sys.exit("先に prompt・mock 段を実行する")
    man["adoption"] = {"image": os.path.relpath(image, REPO) if os.path.abspath(image).startswith(REPO) else image, "image_sha256": sha_file(image),
                       "size": list(im.size), "take": take, "prompt_sha256": next(iter(pr["outputs"].values())), "mock_clean_sha256": mk["outputs"].get(f"{key}-clean.png"),
                       "plan_sha256": man["plan_sha256"]}
    save_manifest(mpath, man)
    print(f"[{key}] adopt 記録: take {take} sha256 {man['adoption']['image_sha256'][:12]}…")


def verify(man, key):
    a = man.get("adoption")
    if not a:
        return "未採用"
    cur_plan = man.get("plan_sha256")
    return "採用済み・最新" if a["plan_sha256"] == cur_plan else "採用後にスペックが変わった（再生成が要る）"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("target", help="PLAN.json、または --all/--status 時は connections.json")
    ap.add_argument("--variant")
    ap.add_argument("--out", help="出力ルート（既定: スペックと同じディレクトリ）")
    ap.add_argument("--from", dest="from_stage", choices=STAGES)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--adopt")
    ap.add_argument("--take", type=int, default=1)
    a = ap.parse_args()
    if a.all or a.status:
        base = os.path.dirname(os.path.abspath(a.target))
        out = a.out or base
        with open(a.target, encoding="utf-8") as f:
            C = json.load(f)
        jobs = []
        for fn in C["plans"]:
            pp = os.path.join(base, fn)
            jobs.append((pp, None))
            with open(pp, encoding="utf-8") as f:
                for v in json.load(f).get("variants", {}):
                    jobs.append((pp, v))
        if a.status:
            for pp, v in jobs:
                p = M.load_plan(pp, v)
                mp = os.path.join(out, p["map_id"], "manifest.json")
                man = load_manifest(mp)
                st = {k: man["stages"].get(k, {}).get("status", "-") for k in STAGES}
                print(p["map_id"], st, verify(man, p["map_id"]))
            return
        bad = 0
        for pp, v in jobs:
            _, errs = build_one(pp, out, v, a.from_stage, a.force)
            bad += bool(errs)
        # 接続図（全MAP横断）。入力 hash で skip
        cm = os.path.join(out, "connection-manifest.json")
        h = sha_bytes((sha_file(a.target) + "".join(sha_file(os.path.join(base, fn)) for fn in C["plans"]) + src_sha("oblique_mock.py", "oblique_topology.py")).encode())
        cur = load_manifest(cm)
        outs = ["connection-diagram.png", "overview.png", "connections.md", "windows.md"]
        if not a.force and cur.get("input_sha") == h and all(os.path.exists(os.path.join(out, o)) for o in outs) and not a.from_stage:
            print("[connections] diagram: skip（入力 hash 同じ）")
        else:
            probs = T.build(a.target, out)
            cur = {"schema": "sit-oblique-manifest/1", "input_sha": h, "problems": probs, "outputs": {o: sha_file(os.path.join(out, o)) for o in outs}}
            save_manifest(cm, cur)
            print("[connections] diagram: 実行 → " + ", ".join(outs), "| 問題:", probs or "なし")
            bad += bool(probs)
        sys.exit(1 if bad else 0)
    out = a.out or os.path.dirname(os.path.abspath(a.target))
    if a.adopt:
        adopt(a.target, out, a.adopt, a.take, a.variant)
        return
    _, errs = build_one(a.target, out, a.variant, a.from_stage, a.force)
    sys.exit(1 if errs else 0)


if __name__ == "__main__":
    main()
