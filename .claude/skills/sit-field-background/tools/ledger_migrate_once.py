"""一度きりの移行: 既存の plan.json・decor-pools.json・connections.json・md 台帳（寺町）→ docs/ledger/*.csv。

以降は CSV が正本。再実行すると手で足した行が消えるので、通常は実行しない（`--force` が要る）。
意図的な修正（畳・化石の石・勝手口・渡り廊下棟など）はここでは入れず、移行後に CSV を直す
（移行の忠実性を ledger_build.py の再生成と元 JSON の比較で先に証明するため）。
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ledger_flat as F  # noqa: E402
import ledger_io as L  # noqa: E402

OBL = os.path.join(L.REPO, "docs", "production", "oblique-mocks")
PLANS = ["TRM-05", "TRM-04", "TRM-02", "TRM-03"]


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def md_rows(name, prefix_re):
    out = {}
    with open(os.path.join(L.REPO, "docs", name), encoding="utf-8") as f:
        for line in f:
            if re.match(prefix_re, line):
                c = [x.strip() for x in line.strip().strip("|").split("|")]
                out[c[0].split()[0]] = c
    return out


def elements_rows(map_id, era, src, rows):
    for key, kind in L.EKIND.items():
        for i, e in enumerate(src.get(key, []), 1):
            e = dict(e)
            eid = e.pop("id") if "id" in e else f"{map_id}.{era or 'base'}.annotation{i}"
            r = {"MAP_ID": map_id, "適用時期": era, "要素ID": eid, "種別": kind}
            lab = e.get("label")
            if isinstance(lab, str) and lab:
                r["名称"] = e.pop("label")
            look = e.get("look")
            if isinstance(look, str) and look:
                r["見た目"] = e.pop("look")
            r["属性JSON"] = L.jdump(e) if e else ""
            rows["要素"].append(r)


def edge_rows(map_id, era, src, rows):
    for key, kind in L.EDGE_KIND.items():
        for e in src.get(key, []):
            e = dict(e)
            r = {"端ID": e.pop("id"), "MAP_ID": map_id, "適用時期": era, "種別": kind}
            if "wall" in e:
                r["壁"] = e.pop("wall")
            if "wall_side" in e:
                r["壁側"] = L.jp(L.SIDE, e.pop("wall_side"))
            if "face" in e:
                r["面"] = L.jp(L.SIDE, e.pop("face"))
            if "center" in e:
                r["中心"] = json.dumps(e.pop("center"))
            if "along_ref" in e:
                r["沿い範囲"] = json.dumps(e.pop("along_ref"))
            if "partner" in e:
                r["相手端"] = e.pop("partner")
            if "width_class" in e:
                r["幅クラス"] = L.jp(L.WIDTH, e.pop("width_class"))
            if "status" in e:
                r["状態"] = L.jp(L.STATUS, e.pop("status"))
            if e.pop("passage", False):
                r["通路"] = "開放"
            if "note" in e:
                r["備考"] = e.pop("note")
            r["属性JSON"] = L.jdump(e) if e else ""
            rows["端"].append(r)


def window_rows(map_id, era, src, rows):
    for e in src.get("windows", []):
        e = dict(e)
        r = {"窓ID": e.pop("id"), "MAP_ID": map_id, "適用時期": era, "壁": e.pop("wall"), "壁側": L.jp(L.SIDE, e.pop("wall_side")),
             "中心": json.dumps(e.pop("center")), "幅": json.dumps(e.pop("width")), "種別": L.jp(L.WKIND, e.pop("kind")),
             "窓台": json.dumps(e.pop("sill")), "高さ": json.dumps(e.pop("height")), "状態": L.jp(L.STATUS, e.pop("status"))}
        if "along_ref" in e:
            r["沿い範囲"] = json.dumps(e.pop("along_ref"))
        if "note" in e:
            r["備考"] = e.pop("note")
        r["属性JSON"] = L.jdump(e) if e else ""
        rows["窓"].append(r)
    for e in src.get("no_window_walls", []):
        e = dict(e)
        r = {"窓ID": f"{map_id}.nowin.{e['wall']}", "MAP_ID": map_id, "適用時期": era, "壁": e.pop("wall"), "種別": "窓なし",
             "状態": L.jp(L.STATUS, e.pop("status")), "備考": e.pop("reason")}
        r["属性JSON"] = L.jdump(e) if e else ""
        rows["窓"].append(r)


def main():
    if os.path.exists(L.path("MAP")) and "--force" not in sys.argv:
        sys.exit("docs/ledger/MAP.csv が既にある。移行は一度きり（上書きするなら --force）")
    rows = {t: [] for t in L.SCHEMA}
    spec = md_rows("map-specifications.md", r"^\| TRM-\d\d")
    # ---- plan
    plan_meta = {}
    for mid in PLANS:
        p = load(os.path.join(OBL, f"{mid}-plan.json"))
        plan_meta[mid] = p
        elements_rows(mid, "", p, rows)
        edge_rows(mid, "", p, rows)
        window_rows(mid, "", p, rows)
        for i, a in enumerate(p.get("assumptions", []), 1):
            rows["既定値"].append({"既定ID": f"{mid}.a{i:02d}", "MAP_ID": mid, "適用時期": "", "内容": a})
        for era, v in p.get("variants", {}).items():
            for k, item in (("名称", "name"), ("字幕", "subtitle")):
                if item in v:
                    rows["時期差分"].append({"MAP_ID": mid, "時期": era, "項目": k, "値": v[item]})
            for rid in v.get("remove", []):
                rows["時期差分"].append({"MAP_ID": mid, "時期": era, "項目": "削除", "値": rid})
            if "depends_on" in v:
                rows["時期差分"].append({"MAP_ID": mid, "時期": era, "項目": "依存", "値": ";".join(v["depends_on"])})
            add = v.get("add", {})
            elements_rows(mid, era, add, rows)
            edge_rows(mid, era, add, rows)
            window_rows(mid, era, add, rows)
            for i, a in enumerate(v.get("assumptions", []), 1):
                rows["既定値"].append({"既定ID": f"{mid}.{era}.a{i:02d}", "MAP_ID": mid, "適用時期": era, "内容": a})
            unknown = set(v) - {"name", "subtitle", "remove", "add", "assumptions", "depends_on"}
            assert not unknown, unknown
        unknown = set(p) - {"schema", "map_id", "name", "subtitle", "source", "assumptions", "decor_pool", "depends_on", "variants", "no_window_walls"} - set(L.EKIND) - set(L.EDGE_KIND) - {"windows"}
        assert not unknown, (mid, unknown)
    # ---- MAP（寺町 17 行）
    for n in range(1, 18):
        mid = f"TRM-{n:02d}"
        s = spec.get(mid, [mid, "", "", "", "", ""])
        p = plan_meta.get(mid)
        rows["MAP"].append({
            "MAP_ID": mid, "エリアID": "teramachi", "名称": p["name"] if p else "", "字幕": p.get("subtitle", "") if p else "",
            "時期": s[1], "一言特徴": s[2], "描画方式": "斜めモック" if p else "未設計",
            "装飾プールID": p.get("decor_pool", "") if p else "", "依存MAP": ";".join(p.get("depends_on", [])) if p else "",
            "寸法根拠": p.get("source", "") if p else ""})
    # ---- decor-pools
    doc = load(os.path.join(OBL, "decor-pools.json"))
    for k in ("schema", "note"):
        t = "文"
        rows["装飾プール"].append({"プールID": "_doc", "項目": k, "値": doc[k], "型": t})
    for pid, pool in doc["pools"].items():
        for path_, v, t in F.flatten(pool):
            rows["装飾プール"].append({"プールID": pid, "項目": path_, "値": v, "型": t})
    for aid, area in doc["areas"].items():
        for path_, v, t in F.flatten(area):
            rows["エリア固定"].append({"エリアID": aid, "項目": path_, "値": v, "型": t})
    # ---- connections
    conn = load(os.path.join(OBL, "connections.json"))
    for path_, v, t in F.flatten({k: v for k, v in conn.items() if k != "edges"}):
        rows["接続図設定"].append({"図ID": "幼稚園一式", "項目": path_, "値": v, "型": t})
    seen = set()
    for e in conn["edges"]:
        d = dict(e)
        r = {"端A": d.pop("a"), "端B": d.pop("b"), "種別": d.pop("kind"), "図": "幼稚園一式"}
        for k, col in (("expect", "期待"), ("label", "ラベル"), ("a_dir", "方角A"), ("b_dir", "方角B")):
            if k in d:
                r[col] = d.pop(k)
        if d.pop("external", False):
            r["外部"] = "はい"
        if "disabled_in" in d:
            r["無効時期"] = L.jdump(d.pop("disabled_in"))
        assert not d, d
        rows["接続"].append(r)
        seen.add(frozenset([r["端A"], r["端B"]]))
    # topology v2 の寺町行（connections.json に無いもの）
    with open(os.path.join(L.REPO, "docs", "map-topology.md"), encoding="utf-8") as f:
        t = f.read()
    a = t.index("#### MAP相互接続台帳 v2")
    b = t.index("#### 寺町の地形不変条件", a)
    for line in t[a:b].splitlines():
        if not line.startswith("| TRM-") and not re.match(r"^\| [A-Z]{3}-\d\d\.\S+ \| TRM-", line):
            continue
        c = [x.strip() for x in line.strip().strip("|").split("|")]
        if frozenset([c[0], c[1]]) in seen:
            continue
        seen.add(frozenset([c[0], c[1]]))
        rows["接続"].append({"端A": c[0], "端B": c[1], "種別": c[2], "主路・状態": c[3]})
    for tname, rs in rows.items():
        if rs:
            L.write(tname, rs)
    print({k: len(v) for k, v in rows.items() if v})


if __name__ == "__main__":
    main()
