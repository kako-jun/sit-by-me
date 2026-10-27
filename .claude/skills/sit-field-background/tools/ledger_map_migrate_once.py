"""旧MAP資料の行を日本語YAML台帳へ一度だけ移す。

既存行を上書きしない。旧表の列名と行番号を記録し、推測できない造形・
寸法・材質は未決(要確認)と対応する未決行にする。画像は読まない。
移行後に再実行しない（旧資料は生成ビューになる）。
"""
import json
import re
from pathlib import Path

import ledger_io as L

ROOT = Path(L.REPO)
UNKNOWN = "未決(要確認)"
MAP_ID = re.compile(r"^[A-Z]{3}-\d{2}$")
ENDPOINT = re.compile(r"^[A-Z]{3}-\d{2}\.[^ |]+$")


def md_rows(path):
    """名前付き Markdown 表の行を、見出しと行番号付きで返す。"""
    section = ""
    header = None
    result = []
    for lineno, line in enumerate((ROOT / path).read_text(encoding="utf-8").splitlines(), 1):
        if line.startswith("#"):
            section = line.lstrip("# ")
            header = None
        if not line.startswith("|"):
            continue
        cells = [c.strip().replace("\\|", "|") for c in line.strip().strip("|").split("|")]
        if cells and cells[0] in ("MAP", "ID", "From"):
            header = cells
            continue
        if not header or len(cells) != len(header) or cells[0].startswith("---"):
            continue
        result.append((section, lineno, dict(zip(header, cells))))
    return result


def key(a, b, kind):
    return tuple(sorted((a, b))) + (kind,)


def main():
    areas_json = json.loads((ROOT / "docs/topology/areas.json").read_text(encoding="utf-8"))["areas"]
    active = {mid: a["id"] for a in areas_json for mid in a["maps"]}
    existing = L.read("MAP")
    missing = sorted(set(active) - {r["MAP_ID"] for r in existing})
    if len(missing) != 101 or len(existing) != 29:
        raise SystemExit(f"移行前の件数ではない: MAP={len(existing)}, 残={len(missing)}。再実行禁止")

    specs = {}
    spec_rows = []
    for section, line, r in md_rows("docs/map-specifications.md"):
        raw = r.get("MAP", "")
        mid = raw.split()[0] if raw else ""
        if mid not in active:
            continue
        spec_rows.append({
            "仕様ID": f"SPEC-{len(spec_rows)+1:03d}", "MAP_ID": mid, "節": section,
            "時期": r.get("時期", ""), "一言特徴": r.get("一言特徴", ""),
            "経路・通行": r.get("不変条件／接続") or r.get("方位・主路・通行条件") or r.get("接続", ""),
            "暫定固定": r.get("暫定固定") or r.get("不変条件／TBD", ""),
            "原文列名": ";".join(r.keys()), "根拠": f"docs/map-specifications.md:{line}",
            L.FREE: ""})
        specs.setdefault(mid, []).append(r)
    if set(specs) != set(active):
        raise SystemExit(f"個別仕様のID差: 不足={sorted(set(active)-set(specs))}, 余分={sorted(set(specs)-set(active))}")

    check = {}
    contract_rows = []
    for section, line, r in md_rows("docs/map-contract-checklist.md"):
        mid = r.get("ID", "")
        if mid not in active:
            continue
        if mid in check:
            raise SystemExit(f"契約表の重複 {mid}")
        check[mid] = r
        contract_rows.append({
            "契約ID": f"CHECK-{mid}", "MAP_ID": mid, "資料区分": "生成契約チェックリスト",
            "参照ID": r.get("Ref", ""), "旧状態": r.get("状態", ""),
            "画像識別子": "", "mask・出力": r.get("mask / 出力", ""),
            "具体的TBD": r.get("具体的TBD", ""), "通行・接続": "", "素材状態": "",
            "根拠": f"docs/map-contract-checklist.md:{line}", L.FREE: ""})
    if set(check) != set(active):
        raise SystemExit(f"契約表のID差: 不足={sorted(set(active)-set(check))}")

    asset = {}
    for section, line, r in md_rows("docs/map-asset-registry.md"):
        mid = r.get("ID", "")
        if mid not in active:
            continue
        asset.setdefault(mid, []).append(r)
        contract_rows.append({
            "契約ID": f"ASSET-{mid}-{len(asset[mid])}", "MAP_ID": mid,
            "資料区分": section, "参照ID": "", "旧状態": r.get("状態", ""),
            "画像識別子": r.get("画像") or r.get("管理名", ""), "mask・出力": "",
            "具体的TBD": r.get("TBD") or r.get("未決のため必要な個別契約") or r.get("契約", ""),
            "通行・接続": r.get("必須接続", ""), "素材状態": r.get("地区", ""),
            "根拠": f"docs/map-asset-registry.md:{line}", L.FREE: r.get("一言特徴", "") + (f"／時期: {r['時期']}" if r.get("時期") else "")})
    if set(asset) != set(active):
        raise SystemExit(f"画像台帳のID差: 不足={sorted(set(active)-set(asset))}")

    u = L.read("未決")
    next_u = max(int(r["未決ID"].split("-")[1]) for r in u) + 1
    pending = {(r["対象テーブル"], r["対象ID"], r["キー"]) for r in u}

    def undecided(table, ident, field, content):
        nonlocal next_u
        tup = (table, ident, field)
        if tup not in pending:
            u.append({"未決ID": f"U-{next_u:03d}", "対象テーブル": table,
                      "対象ID": ident, "キー": field, "内容": content,
                      "状態": "未決", "解決決定ID": ""})
            pending.add(tup)
            next_u += 1
        return UNKNOWN

    placements = []
    for a in areas_json:
        for seq, mid in enumerate(a["maps"], 1):
            xy = a["layout"][mid]
            placements.append({"配置ID": f"ATLAS-{mid}", "エリアID": a["id"],
                               "MAP_ID": mid, "順番": str(seq), "X": str(xy[0]), "Y": str(xy[1]), "備考": "模式図座標。実距離・確定形状ではない。"})
    area_rows = L.read("エリア")
    for a in area_rows:
        if a["台帳段階"] == "対象外":
            a["台帳段階"] = "対象"
            a["備考"] = "MAPの出典移行済み。幾何・材料の未決は未決表を参照。"
            for field in ("机の天面の材質", "台座の素材", "木の種類", "外周の装飾方針"):
                a[field] = undecided("エリア", a["エリアID"], field, "旧資料に確定値なし。制作前に確認する。")

    for mid in missing:
        s = specs[mid][0]
        times = list(dict.fromkeys(r.get("時期", "") for r in specs[mid] if r.get("時期")))
        row = {col: "" for col in L.SCHEMA["MAP"]}
        row.update({"MAP_ID": mid, "エリアID": active[mid],
                    "名称": s.get("一言特徴", ""), "時期": ";".join(times),
                    "一言特徴": s.get("一言特徴", ""),
                    "屋内外": undecided("MAP", mid, "屋内外", "個別仕様と画像契約を照合して屋内/屋外を確定する。"),
                    "状態": undecided("MAP", mid, "状態", "旧状態とモック/採用記録を照合して台帳状態を確定する。"),
                    "描画方式": undecided("MAP", mid, "描画方式", "斜め/体内など生成方式と必要な仕様を確認する。"),
                    "採用状態": undecided("MAP", mid, "採用状態", "旧画像は新方式の採用根拠にしない。参照画像の採用記録を照合する。"),
                    "表現する部位": "", "備考": "出典の詳細はMAP仕様・MAP契約・端・接続を参照。"})
        for field in ("床材", "壁材", "窓", "扉の意匠", "工作の材質", "時期差分", "装飾プールID", "依存MAP"):
            row[field] = undecided("MAP", mid, field, "旧資料に確定した個別値が無いか、複数記述の照合が必要。")
        existing.append(row)

    source = (ROOT / "docs/map-topology.md").read_text(encoding="utf-8")
    start = source.index("#### MAP相互接続台帳 v2")
    stop = source.index("#### 寺町の地形不変条件", start)
    old_edges = []
    for line in source[start:stop].splitlines():
        m = re.fullmatch(r"\| ([A-Z]{3}-\d{2}\.[^ |]+) \| ([A-Z]{3}-\d{2}\.[^ |]+) \| (edge|door|event|oneway) \| (.*) \|", line)
        if m:
            old_edges.append(m.groups())
    if len(old_edges) != 137:
        raise SystemExit(f"v2 接続が137行でない: {len(old_edges)}")
    old_yaml = L.read("接続")
    lookup = {key(r["端A"], r["端B"], r["種別"]): r for r in old_yaml}
    new_edges = []
    for a, b, kind, note in old_edges:
        k = key(a, b, kind)
        if k in lookup:
            r = lookup[k]
        else:
            r = {col: "" for col in L.SCHEMA["接続"]}
            r.update({"端A": a, "端B": b, "種別": kind,
                      "主路・状態": note,
                      "外部": "はい" if active[a.split(".")[0]] != active[b.split(".")[0]] else "",
                      "図": "全MAP"})
        new_edges.append(r)
    if len(new_edges) != 137 or len(lookup) != 37:
        raise SystemExit("接続の既存37行との対応が崩れた")

    ends = L.read("端")
    known_ends = {(r["端ID"], r["適用時期"]) for r in ends}
    for a, b, kind, note in old_edges:
        for ep, peer in ((a, b), (b, a)):
            ident = (ep, "")
            if ident in known_ends:
                continue
            mid, port = ep.split(".", 1)
            if port in ("top", "bottom", "left", "right"):
                kind_ja = "縁"
            elif kind == "event":
                kind_ja = "イベント"
            elif kind == "oneway":
                kind_ja = "移動"
            elif mid.startswith("BDY-"):
                kind_ja = "抽象通路"
            else:
                kind_ja = "戸口"
            row = {col: "" for col in L.SCHEMA["端"]}
            row.update({"端ID": ep, "MAP_ID": mid, "種別": kind_ja,
                        "相手端": peer, "状態": "接続定義済み",
                        "備考": "接続の存在と端IDのみv2で確定。位置・幅・具体形状は未決。"})
            if kind_ja == "戸口":
                row["幅クラス"] = undecided("端", ep, "幅クラス", "v2接続に戸口の幅の確定値なし。")
            if kind_ja not in ("縁", "イベント", "移動"):
                row["壁側"] = undecided("端", ep, "壁側", "v2接続に壁の方角の確定値なし。")
            ends.append(row)
            known_ends.add(ident)

    special = [
        {"遷移ID": f"ELEV-{mid}", "種別": "階選択", "起点MAP": mid,
         "到着MAP": "未決(要確認)" if mid == "KRB-05" else "KRB-02;KRB-03;KRB-04;KRB-05;KRB-06",
         "条件": "4階KRB-05は最終章・兼六園へ向かう途中の寄り道で選択可能。他階は通常選択。",
         "状態": "設計記録", "根拠": "docs/map-topology.md:104-115; docs/map-asset-registry.md:#87/#89追加ID", L.FREE: ""}
        for mid in ("KRB-02", "KRB-03", "KRB-04", "KRB-05", "KRB-06")
    ]
    # 階選択の到着先は共通集合。個別の起点からの線を接続表へ捏造しない。
    special[3]["到着MAP"] = "KRB-02;KRB-03;KRB-04;KRB-05;KRB-06"

    for table, rows in (("図配置", placements), ("MAP仕様", spec_rows), ("MAP契約", contract_rows),
                        ("エリア", area_rows), ("MAP", existing), ("端", ends),
                        ("接続", new_edges), ("特殊遷移", special), ("未決", u)):
        L.write(table, rows)
        print(table, len(rows))


if __name__ == "__main__":
    main()
