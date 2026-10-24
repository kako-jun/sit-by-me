"""寺町 TRM-06〜17 の台帳取込み（一度きり。再実行すると手修正が消える。記録用）。
入力: teramachi-rest-mocks-20261023 ブランチの TRM-06〜17-plan.json・connections-teramachi.json（git show で取り出したもの。引数1=置き場）。
"""
import json
import os
import re
import sys

TOOLS = "<repo>/.claude/skills/sit-field-background/tools"
sys.path.insert(0, TOOLS)
import ledger_flat as F  # noqa: E402
import ledger_io as L  # noqa: E402

SRC = sys.argv[1]
NOW = "2026-10-24"
MAPS = [f"TRM-{n:02d}" for n in range(6, 18)]
plans = {m: json.load(open(os.path.join(SRC, f"{m}-plan.json"))) for m in MAPS}
town = json.load(open(os.path.join(SRC, "connections-teramachi.json")))

T = {t: L.read(t) for t in L.SCHEMA}


def blank(table):
    return {c: "" for c in L.SCHEMA[table]}


def jd(o):
    return json.dumps(o, ensure_ascii=False)


# ---- 決定参照（既存の決定に対応する既定の文だけ）
def refs_for(mid, text):
    r = []
    if "TRM-06.door-house" in text and "決定済み" in text:
        r.append("TRM-05.door-back")
    if mid == "TRM-08" and text.startswith("上端は塀・壁で閉じる"):
        r.append("TRM-08.top-closed")
    if "円環" in text and "#51" in text or (mid == "TRM-16" and "円環（16→15→06→16）" in text):
        r.append("TRM-06.loop")
    return ";".join(r)


# ---- MAP
state_new = "モック作成済み(承認待ち)"
for m in T["MAP"]:
    mid = m["MAP_ID"]
    if mid not in plans:
        continue
    p = plans[mid]
    m["名称"] = p["name"]
    m["字幕"] = p["subtitle"]
    m["寸法根拠"] = p["source"]
    m["設計意図"] = p["design"]
    extra = {k: v for k, v in p.items() if k not in ("schema", "map_id", "name", "subtitle", "source", "design", "floors", "walls", "doors", "openings", "markers", "boxes",
                                                      "closed_edges", "assumptions", "windows", "paths", "tree_zones", "annotations")}
    m["plan追加JSON"] = L.jdump(extra) if extra else ""
    m["状態"] = state_new
    m["描画方式"] = "斜めモック"
    m["建物ID"] = "該当なし"
    m["表現する部位"] = "該当なし"
    m["備考"] = "plan（平面スペック）を台帳へ取込み済み（2026-10-24）。モック画像・マスク・オクルージョンは別ブランチ teramachi-rest-mocks-20261023 にあり本ブランチ未取込。全体レビュー承認前。画像生成は承認後"

# ---- 要素
for mid in MAPS:
    p = plans[mid]
    for key in ("floors", "walls", "boxes"):
        for e in p.get(key, []):
            e = dict(e)
            r = blank("要素")
            r.update({"MAP_ID": mid, "要素ID": e.pop("id"), "種別": L.EKIND[key]})
            lab = e.pop("label", None)
            if lab:
                r["名称"] = lab
            elif lab == "":
                e["label"] = ""
            if "look" in e:
                assert e["look"], (mid, r["要素ID"])
                r["見た目"] = e.pop("look")
            r["属性JSON"] = L.jdump(e)
            T["要素"].append(r)
    for ce in p.get("closed_edges", []):
        r = blank("要素")
        r.update({"MAP_ID": mid, "要素ID": f"closed-{ce['edge']}", "種別": "閉鎖辺", "属性JSON": L.jdump(ce)})
        if mid == "TRM-08" and ce["edge"] == "north":
            assert ce.get("decided")
            r["決定参照"] = "TRM-08.top-closed"
        T["要素"].append(r)

# ---- 端
SIDE = L.SIDE


def edge_row(mid, e, kind):
    e = dict(e)
    r = blank("端")
    r.update({"端ID": e.pop("id"), "MAP_ID": mid, "種別": kind})
    if kind == "縁":
        attr = {k: e.pop(k) for k in ("at", "edge", "label", "width") if k in e}
        r["属性JSON"] = L.jdump(attr)
    else:
        r["壁"] = e.pop("wall")
        r["壁側"] = SIDE[e.pop("wall_side")]
        if "face" in e:
            r["面"] = SIDE[e.pop("face")]
        r["中心"] = json.dumps(e.pop("center"))
        r["沿い範囲"] = json.dumps(e.pop("along_ref"))
        r["幅クラス"] = L.WIDTH[e.pop("width_class")]
        if e.pop("passage", False):
            r["通路"] = "開放"
    r["相手端"] = e.pop("partner", "")
    r["状態"] = L.STATUS[e.pop("status")]
    r["備考"] = e.pop("note", "")
    assert not e, (mid, r["端ID"], e)
    if r["端ID"] == "TRM-06.door-house":
        r["決定参照"] = "TRM-05.door-back"
    return r


for mid in MAPS:
    p = plans[mid]
    for key, kind in (("doors", "戸口"), ("openings", "開口"), ("markers", "縁")):
        for e in p.get(key, []):
            T["端"].append(edge_row(mid, e, kind))

# ---- 窓
for mid in MAPS:
    for w in plans[mid].get("windows", []):
        w = dict(w)
        r = blank("窓")
        r.update({"窓ID": w.pop("id"), "MAP_ID": mid, "壁": w.pop("wall"), "壁側": SIDE[w.pop("wall_side")], "中心": json.dumps(w.pop("center")), "幅": json.dumps(w.pop("width")),
                  "種別": L.WKIND[w.pop("kind")], "窓台": json.dumps(w.pop("sill")), "高さ": json.dumps(w.pop("height")), "状態": L.STATUS[w.pop("status")],
                  "沿い範囲": json.dumps(w.pop("along_ref")), "備考": w.pop("note", "")})
        assert not w, w
        T["窓"].append(r)

# ---- 既定値
for mid in MAPS:
    for i, a in enumerate(plans[mid]["assumptions"], 1):
        r = blank("既定値")
        r.update({"既定ID": f"{mid}.a{i:02d}", "MAP_ID": mid, "内容": a, "決定参照": refs_for(mid, a)})
        T["既定値"].append(r)

# ---- 接続
def pair(a, b):
    return tuple(sorted((a, b)))


rows = {pair(r["端A"], r["端B"]): r for r in T["接続"]}


def edge_from_row(r, zu):
    e = {"a": r["端A"], "b": r["端B"], "kind": r["種別"]}
    if r["期待"]:
        e["expect"] = r["期待"]
    if r["ラベル"]:
        e["label"] = r["ラベル"]
    if r["方角A"]:
        e["a_dir"] = r["方角A"] if r["方角A"] not in SIDE.values() else L.en(SIDE, r["方角A"])
    if r["方角B"]:
        e["b_dir"] = r["方角B"] if r["方角B"] not in SIDE.values() else L.en(SIDE, r["方角B"])
    if r["外部"] == "はい":
        e["external"] = True
    if r["無効時期"]:
        e["disabled_in"] = json.loads(r["無効時期"])
    return e


used = set()
for te in town["edges"]:
    k = pair(te["a"], te["b"])
    r = rows[k]
    used.add(k)
    zs = L.split_list(r["図"])
    if "幼稚園一式" in zs:  # 共有行: 列は幼稚園の値のまま、寺町全体との差を上書きに持つ
        base = edge_from_row(r, "幼稚園一式")
        assert (base["a"], base["b"]) == (te["a"], te["b"]), k
        ov = {}
        for key in set(base) | set(te):
            if base.get(key) != te.get(key):
                ov[key] = te.get(key)  # None=その図では出さない
        r["図"] = "幼稚園一式;寺町全体"
        if ov:
            r["属性JSON"] = L.jdump({"寺町全体": ov})
    else:
        if (r["端A"], r["端B"]) != (te["a"], te["b"]):  # 向きを寺町全体の図に揃える
            r["端A"], r["端B"] = r["端B"], r["端A"]
            r["方角A"], r["方角B"] = r["方角B"], r["方角A"]
        assert r["方角A"] == "" and r["方角B"] == ""
        r["種別"] = te["kind"]
        r["期待"] = te.get("expect", "")
        r["ラベル"] = te.get("label", "")
        if "a_dir" in te:
            r["方角A"] = SIDE.get(te["a_dir"], te["a_dir"])
        if "b_dir" in te:
            r["方角B"] = SIDE.get(te["b_dir"], te["b_dir"])
        r["外部"] = "はい" if te.get("external") else ""
        r["無効時期"] = jd(te["disabled_in"]) if "disabled_in" in te else ""
        r["図"] = "寺町全体"
        ex = {k2: te[k2] for k2 in ("via", "label_at", "ledger", "note") if k2 in te}
        left = set(te) - {"a", "b", "kind", "expect", "label", "a_dir", "b_dir", "external", "disabled_in", "via", "label_at", "ledger", "note"}
        assert not left, left
        if ex:
            r["属性JSON"] = L.jdump({"寺町全体": ex})
assert used == set(rows), set(rows) - used

# ---- 接続図設定（寺町全体）
doc = {k: v for k, v in town.items() if k != "edges"}
# maps_info: 06〜17 は MAP 表（屋内外・設計意図）から導出するので行にしない
doc["maps_info"] = {k: v for k, v in doc["maps_info"].items() if k not in MAPS}
for mid in MAPS:
    mi = town["maps_info"][mid]
    mp = next(m for m in T["MAP"] if m["MAP_ID"] == mid)
    assert mi["kind"] == mp["屋内外"] and mi["design"] == mp["設計意図"], mid
for item, val, typ in F.flatten(doc):
    r = blank("接続図設定")
    r.update({"図ID": "寺町全体", "項目": item, "値": val, "型": typ})
    T["接続図設定"].append(r)

# ---- 語彙
mx = max(int(r["語彙ID"].split("-")[1]) for r in T["語彙"])
for grp, val, desc in (("要素種別", "閉鎖辺", "屋外MAPの閉鎖した辺（塀・壁・家並み・擁壁・雪の壁）と理由。plan の closed_edges"),
                       ("MAP状態", state_new, "平面スペック(plan)とモックは作ったが、全体レビューの承認前（画像生成は承認後）")):
    mx += 1
    T["語彙"].append({"語彙ID": f"V-{mx:03d}", "グループ": grp, "値": val, "英語断片": "", "説明": desc})

for t in ("MAP", "要素", "端", "窓", "既定値", "接続", "接続図設定", "語彙"):
    L.write(t, T[t])
print("done")
