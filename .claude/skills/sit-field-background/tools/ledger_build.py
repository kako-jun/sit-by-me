"""台帳（docs/ledger/*.csv）→ 派生物（plan・decor-pools・connections の JSON）を決定論で生成する唯一の導出器。

派生 JSON は手で編集しない（先頭の `_provenance` に入力ハッシュ・再生成コマンドを持つ）。
  uv run python3 ledger_build.py build            # 派生 JSON を再生成し、生成物.csv のハッシュを更新
  uv run python3 ledger_build.py check            # 再生成して手編集・古さを検出（書かない）
  uv run python3 ledger_build.py template area|map ID   # 必須キーの雛形行（空欄=未決として検出される）を出す
"""
import json
import os
import re
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ledger_flat as F  # noqa: E402
import ledger_io as L  # noqa: E402

OBL = os.path.join(L.REPO, "docs", "production", "oblique-mocks")
PLAN_KEYS = {"floors": "床", "walls": "壁", "boxes": "家具", "paths": "経路", "tree_zones": "樹木帯", "annotations": "注記"}
KIND_TO_KEY = {v: k for k, v in PLAN_KEYS.items()}
EDGE_TO_KEY = {"戸口": "doors", "開口": "openings", "縁": "markers"}


def tables():
    return {t: L.read(t) for t in L.SCHEMA}


def num(s):
    return json.loads(s) if s not in ("", None) else None


def ref_text(T, ref):
    """決定IDの要点（決定文の複写ではなく、台帳から展開した文）。"""
    for d in T["決定"]:
        if d["決定ID"] == ref:
            return d["決定の要点"]
    raise KeyError(f"決定 {ref} が決定表に無い")


PART_RE = re.compile(r"\{部位:([^}]+)\}")


def expand_look(T, s):
    if not s:
        return s
    parts = {p["部位ID"]: p for p in T["建物部位"]}

    def sub(m):
        return parts[m.group(1)]["見た目"]
    return PART_RE.sub(sub, s)


def element_dict(T, r):
    d = json.loads(r["属性JSON"]) if r["属性JSON"] else {}
    if r["種別"] != "注記":
        d["id"] = r["要素ID"]
    if r["名称"]:
        d["label"] = r["名称"]
    look = expand_look(T, r["見た目"])
    if not look and r["決定参照"]:
        look = ref_text(T, L.split_list(r["決定参照"])[0])
    if look:
        d["look"] = look
    return d


def with_refs(T, text, refs):
    ids = L.split_list(refs)
    for i in ids:
        ref_text(T, i)  # 存在確認
    return text + (f"（決定 {', '.join(ids)}）" if ids else "")


def edge_dict(T, r):
    d = json.loads(r["属性JSON"]) if r["属性JSON"] else {}
    d["id"] = r["端ID"]
    if r["壁"]:
        d["wall"] = r["壁"]
    if r["壁側"]:
        d["wall_side"] = L.en(L.SIDE, r["壁側"])
    if r["面"]:
        d["face"] = L.en(L.SIDE, r["面"])
    if r["中心"] != "":
        d["center"] = num(r["中心"])
    if r["沿い範囲"]:
        d["along_ref"] = json.loads(r["沿い範囲"])
    if r["相手端"]:
        d["partner"] = r["相手端"]
    if r["幅クラス"]:
        d["width_class"] = L.en(L.WIDTH, r["幅クラス"])
    if r["状態"]:
        d["status"] = L.en(L.STATUS, r["状態"])
    if r["通路"] == "開放":
        d["passage"] = True
    if r["備考"]:
        d["note"] = with_refs(T, r["備考"], r["決定参照"])
    return d


def window_dict(T, r, walls):
    d = json.loads(r["属性JSON"]) if r["属性JSON"] else {}
    if r["種別"] == "窓なし":
        d.update({"wall": r["壁"], "status": L.en(L.STATUS, r["状態"]), "reason": with_refs(T, r["備考"], r["決定参照"])})
        return d
    d["id"] = r["窓ID"]
    d["wall"] = r["壁"]
    d["wall_side"] = L.en(L.SIDE, r["壁側"])
    d["status"] = L.en(L.STATUS, r["状態"])
    if r["沿い範囲"]:
        d["along_ref"] = json.loads(r["沿い範囲"])
    if r["備考"]:
        d["note"] = with_refs(T, r["備考"], r["決定参照"])
    if r["建物窓列ID"] and r["中心"] == "":
        row = next(x for x in T["建物窓列"] if x["窓列ID"] == r["建物窓列ID"])
        lo, hi = d["along_ref"]
        ln, n = hi - lo, int(r["連番"])
        wall_h = next(w for w in walls if w["id"] == r["壁"])["h"]
        d["center"] = round(lo + (float(row["先頭比"]) + (n - 1) * float(row["間隔比"])) * ln)
        d["width"] = round(float(row["幅比"]) * ln)
        d["kind"] = L.en(L.WKIND, row["窓種別"])
        d["sill"] = round(float(row["窓台比"]) * wall_h)
        d["height"] = round(float(row["高さ比"]) * wall_h)
    else:
        d["center"] = num(r["中心"])
        d["width"] = num(r["幅"])
        d["kind"] = L.en(L.WKIND, r["種別"])
        d["sill"] = num(r["窓台"])
        d["height"] = num(r["高さ"])
    return d


def collect(T, map_id, era):
    """MAP_ID・適用時期（''=基準 / 'kids' など）の plan 部品を dict で返す。"""
    out = {}
    for r in T["要素"]:
        if r["MAP_ID"] == map_id and r["適用時期"] == era:
            out.setdefault(KIND_TO_KEY[r["種別"]], []).append(element_dict(T, r))
    for r in T["端"]:
        if r["MAP_ID"] == map_id and r["適用時期"] == era:
            out.setdefault(EDGE_TO_KEY[r["種別"]], []).append(edge_dict(T, r))
    return out


def build_plan(T, map_id):
    m = next(x for x in T["MAP"] if x["MAP_ID"] == map_id)
    p = {"schema": "sit-oblique-plan/1", "map_id": map_id, "name": m["名称"], "subtitle": m["字幕"], "source": m["寸法根拠"]}
    base = collect(T, map_id, "")
    p.update(base)
    walls = p.get("walls", [])
    wins = [r for r in T["窓"] if r["MAP_ID"] == map_id and r["適用時期"] == ""]
    for r in wins:
        d = window_dict(T, r, walls)
        key = "no_window_walls" if r["種別"] == "窓なし" else "windows"
        p.setdefault(key, []).append(d)
    p["assumptions"] = [with_refs(T, x["内容"], x["決定参照"]) for x in T["既定値"] if x["MAP_ID"] == map_id and x["適用時期"] == ""]
    if m["装飾プールID"] and not m["装飾プールID"].startswith("未決"):
        p["decor_pool"] = m["装飾プールID"]
    p["depends_on"] = [x for x in L.split_list(m["依存MAP"]) if x not in ("なし", "該当なし")]
    eras = []
    for r in T["時期差分"]:
        if r["MAP_ID"] == map_id and r["時期"] not in eras:
            eras.append(r["時期"])
    if eras:
        p["variants"] = {}
    for era in eras:
        v = {}
        rm = []
        for r in T["時期差分"]:
            if r["MAP_ID"] != map_id or r["時期"] != era:
                continue
            if r["項目"] == "名称":
                v["name"] = r["値"]
            elif r["項目"] == "字幕":
                v["subtitle"] = r["値"]
            elif r["項目"] == "削除":
                rm.append(r["値"])
            elif r["項目"] == "依存":
                v["depends_on"] = L.split_list(r["値"])
        if rm:
            v["remove"] = rm
        add = collect(T, map_id, era)
        wins_v = [window_dict(T, r, walls) for r in T["窓"] if r["MAP_ID"] == map_id and r["適用時期"] == era]
        if wins_v:
            add["windows"] = wins_v
        if add:
            v["add"] = add
        ass = [with_refs(T, x["内容"], x["決定参照"]) for x in T["既定値"] if x["MAP_ID"] == map_id and x["適用時期"] == era]
        if ass:
            v["assumptions"] = ass
        p["variants"][era] = v
    return p


def build_decor(T):
    doc = {}
    rows = [(r["項目"], r["値"], r["型"]) for r in T["装飾プール"] if r["プールID"] == "_doc"]
    doc.update(F.unflatten(rows))
    doc["pools"] = {}
    pids = []
    for r in T["装飾プール"]:
        if r["プールID"] != "_doc" and r["プールID"] not in pids:
            pids.append(r["プールID"])
    for pid in pids:
        rows = []
        for r in T["装飾プール"]:
            if r["プールID"] != pid:
                continue
            v = r["値"]
            if r["決定参照"] and not v:
                v = f"{ref_text(T, r['決定参照'])}（決定 {r['決定参照']}）"
            rows.append((r["項目"], v, r["型"]))
        doc["pools"][pid] = F.unflatten(rows)
    doc["areas"] = {}
    aids = []
    for r in T["エリア固定"]:
        if r["エリアID"] not in aids:
            aids.append(r["エリアID"])
    for aid in aids:
        rows = []
        for r in T["エリア固定"]:
            if r["エリアID"] != aid:
                continue
            v = r["値"]
            if r["決定参照"] and not v:
                v = f"{ref_text(T, r['決定参照'])}（決定 {r['決定参照']}）"
            rows.append((r["項目"], v, r["型"]))
        doc["areas"][aid] = F.unflatten(rows)
    return doc


def build_connections(T, zu="幼稚園一式"):
    doc = F.unflatten([(r["項目"], r["値"], r["型"]) for r in T["接続図設定"] if r["図ID"] == zu])
    edges = []
    for r in T["接続"]:
        if r["図"] != zu:
            continue
        e = {"a": r["端A"], "b": r["端B"], "kind": r["種別"]}
        if r["期待"]:
            e["expect"] = r["期待"]
        if r["ラベル"]:
            e["label"] = r["ラベル"]
        if r["方角A"]:
            e["a_dir"] = L.en(L.SIDE, r["方角A"]) if r["方角A"] in L.SIDE.values() else r["方角A"]
        if r["方角B"]:
            e["b_dir"] = L.en(L.SIDE, r["方角B"]) if r["方角B"] in L.SIDE.values() else r["方角B"]
        if r["外部"] == "はい":
            e["external"] = True
        if r["無効時期"]:
            e["disabled_in"] = json.loads(r["無効時期"])
        edges.append(e)
    doc["edges"] = edges
    return doc


DEPSTATUS = {"fixed": "確定", "derived": "導出", "needs-confirmation": "要確認"}


def build_deps(T):
    doc = F.unflatten([(r["項目"], r["値"], r["型"]) for r in T["接続図設定"] if r["図ID"] == "依存グラフ"])
    maps = {}
    for m in T["MAP"]:
        if m["依存の確度"]:
            maps[m["MAP_ID"]] = {"depends_on": [x for x in L.split_list(m["依存MAP"]) if x not in ("なし", "該当なし")], "status": L.en(DEPSTATUS, m["依存の確度"]), "basis": m["依存の根拠"]}
    eras = {}
    for r in T["時期差分"]:
        e = eras.setdefault((r["MAP_ID"], r["時期"]), {})
        if r["項目"] == "依存":
            e["depends_on"] = L.split_list(r["値"])
        elif r["項目"] == "依存の確度":
            e["status"] = L.en(DEPSTATUS, r["値"])
        elif r["項目"] == "依存の根拠":
            e["basis"] = r["値"]
    for (mid, era), e in eras.items():
        if "depends_on" in e:
            maps[f"{mid}-{era}"] = {"depends_on": e["depends_on"], "status": e["status"], "basis": e["basis"]}
    doc["maps"] = maps
    return doc


# ---- 生成物の出力先
def targets(T):
    out = []
    for m in T["MAP"]:
        if m["描画方式"] == "斜めモック" and any(r["MAP_ID"] == m["MAP_ID"] for r in T["要素"]):
            out.append((f"G-{m['MAP_ID']}-plan", "斜めplan JSON", f"docs/production/oblique-mocks/{m['MAP_ID']}-plan.json",
                        f"MAP:{m['MAP_ID']}|要素|端|窓|既定値|時期差分|建物部位|建物窓列", lambda t, mid=m["MAP_ID"]: build_plan(t, mid),
                        lambda t, mid=m["MAP_ID"]: input_rows(t, mid)))
    out.append(("G-decor-pools", "装飾プールJSON", "docs/production/oblique-mocks/decor-pools.json", "装飾プール|エリア固定|決定", build_decor,
                lambda t: {"装飾プール": t["装飾プール"], "エリア固定": t["エリア固定"], "決定": [d for d in t["決定"] if any(r["決定参照"] == d["決定ID"] for r in t["装飾プール"] + t["エリア固定"])]}))
    out.append(("G-dependency-graph", "依存グラフJSON", "docs/production/oblique-mocks/dependency-graph.json", "MAP.依存MAP|時期差分|接続図設定", build_deps,
                lambda t: {"MAP": [(r["MAP_ID"], r["依存MAP"], r["依存の確度"], r["依存の根拠"]) for r in t["MAP"]], "時期差分": [r for r in t["時期差分"] if r["項目"].startswith("依存")],
                           "接続図設定": [r for r in t["接続図設定"] if r["図ID"] == "依存グラフ"]}))
    out.append(("G-connections", "接続図JSON", "docs/production/oblique-mocks/connections.json", "接続|接続図設定", build_connections,
                lambda t: {"接続": [r for r in t["接続"] if r["図"]], "接続図設定": t["接続図設定"]}))
    return out


def input_rows(T, mid):
    sel = {"MAP": [r for r in T["MAP"] if r["MAP_ID"] == mid]}
    for tb in ("要素", "端", "窓", "既定値", "時期差分"):
        sel[tb] = [r for r in T[tb] if r["MAP_ID"] == mid]
    sel["建物部位"] = T["建物部位"]
    sel["建物窓列"] = T["建物窓列"]
    return sel


def input_hash(sel):
    return L.sha(L.jdump(sel) + L.BUILDER_VERSION)


def provenance(gid, path_, source, ih, now):
    return {"source": source, "input_sha": ih, "generated_at": now, "command": "uv run python3 .claude/skills/sit-field-background/tools/ledger_build.py build",
            "ledger_id": gid, "do_not_edit": True}


def dump_json(doc):
    return json.dumps(doc, ensure_ascii=False, indent=1) + "\n"


def run(write):
    T = tables()
    now = datetime.now().strftime("%Y-%m-%dT%H:%M")
    old = {r["生成物ID"]: r for r in T["生成物"]}
    problems = []
    rows_out = []
    for gid, kind, path_, source, fn, inputs in targets(T):
        doc = fn(T)
        ih = input_hash(inputs(T))
        doc_p = dict(doc)
        prev_gen = old.get(gid, {}).get("生成日時") or now
        if old.get(gid, {}).get("入力ハッシュ") != ih:
            prev_gen = now
        doc_p["_provenance"] = provenance(gid, path_, source, ih, prev_gen)
        text = dump_json(doc_p)
        ap = os.path.join(L.REPO, path_)
        if write:
            with open(ap, "w", encoding="utf-8") as f:
                f.write(text)
        else:
            cur = open(ap, encoding="utf-8").read() if os.path.exists(ap) else ""
            if cur != text:
                problems.append(f"{path_}: 台帳から再生成した内容と一致しない（手編集または古い）")
        rows_out.append((gid, kind, path_, source, ih, prev_gen))
    if write:
        keep = [r for r in T["生成物"] if r["生成物ID"] not in {x[0] for x in rows_out}]
        new = [{"生成物ID": g, "種別": k, "パス": p_, "元の表": s, "入力ハッシュ": ih, "生成日時": gen,
                "再生成コマンド": "uv run python3 .claude/skills/sit-field-background/tools/ledger_build.py build", "備考": "台帳から導出（手編集禁止）"}
               for g, k, p_, s, ih, gen in rows_out]
        L.write("生成物", new + keep)
    return problems


def template(kind, ident):
    """必須キーの雛形（空欄の行）。空欄は verify で『未決』として検出される。"""
    cols = L.SCHEMA["エリア"] if kind == "area" else L.SCHEMA["MAP"]
    row = {c: "" for c in cols}
    row[cols[0]] = ident
    print(",".join(cols))
    print(",".join(row[c] for c in cols))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    if cmd == "build":
        run(True)
        print("再生成しました")
    elif cmd == "check":
        pr = run(False)
        for x in pr:
            print("FAIL:", x)
        sys.exit(1 if pr else 0)
    elif cmd == "template":
        template(sys.argv[2], sys.argv[3])
    else:
        sys.exit(__doc__)
