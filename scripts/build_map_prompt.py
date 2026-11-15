"""台帳 + sit-diorama の規約からフィールド生成プロンプトを組む。
生成そのものは行わない。ready かつ TBD 空欄でない限り、プロンプトを
出力しないため、未決事項を画像生成でごまかせない。

legacy・非正本（docs/content-registry.md）。md の表は見出し行の列名で読む（md_table.py。列の位置に依存しない）。
台帳（docs/ledger/MAP.yaml）に行がある MAP（寺町）は md を読まず、台帳の状態・未決で停止する（プロンプトは
oblique_build.py が台帳ゲートつきで作る）。
"""
import os
import re
import sys

import ledger_yaml as LY
import md_table as MdTable

ROOT = LY.ROOT  # LEDGER_ROOT で md の読み先も差し替える（ledger_yaml.py と同じ環境変数）


def read_doc(name):
    with open(os.path.join(ROOT, "docs", name), encoding="utf-8") as f:
        return f.read()


def table_row(document, first, id_, *names):
    """先頭列（ID／MAP）がこの MAP の行。複数の表にまたがって探す"""
    for r in MdTable.rows(document, first, *names):
        parts = (r[first] or "").split()
        if parts and parts[0] == id_:
            return r
    return None


def abort(message):
    sys.stderr.write(message if message.endswith("\n") else message + "\n")
    sys.exit(1)


SPEC_ROUTE_COLUMNS = ["不変条件／接続", "方位・主路・通行条件", "接続"]
SPEC_FIXED_COLUMNS = ["暫定固定", "不変条件／TBD"]

id_ = (sys.argv[1] if len(sys.argv) > 1 else "").upper()
if not re.fullmatch(r"[A-Z]{3}-\d{2}", id_):
    abort("usage: uv run python3 scripts/build_map_prompt.py MAP_ID")

ledger_row = next((r for r in LY.read("MAP") if r["MAP_ID"] == id_ and r["状態"] != "廃止"), None)
if ledger_row:
    open_items = [u for u in LY.read("未決") if u["状態"] == "未決" and (u["対象ID"] == id_ or u["対象ID"].startswith(f"{id_}."))]
    items = "none" if not open_items else ", ".join(f"{u['未決ID']} {u['キー']}" for u in open_items)
    abort(f"""{id_}: prompt generation is blocked here. This MAP is managed by the ledger (docs/ledger/MAP.yaml), not by the legacy md tables.
ledger status: {ledger_row['状態']} / adoption: {ledger_row['採用状態']}
unresolved (docs/ledger/未決.yaml): {items}
Build the prompt with oblique_build.py (ledger-gated): see .claude/skills/sit-field-background/tools/README.md
""")

checklist = read_doc("map-contract-checklist.md")
specifications = read_doc("map-specifications.md")
topology = read_doc("map-topology.md")
contract = table_row(checklist, "ID", id_, "状態", "Ref", "mask / 出力", "具体的TBD")
specification = table_row(specifications, "MAP", id_, "時期", "一言特徴")
if not contract:
    abort(f"{id_}: contract row is missing")
if not specification:
    abort(f"{id_}: specification row is missing")

status, refs, mask, tbd = contract["状態"], contract["Ref"], contract["mask / 出力"], contract["具体的TBD"]
if not (status == "ready" and not tbd):
    abort(f"""{id_}: prompt generation is blocked.
status: {status}
refs: {refs}
mask/output: {mask}
unresolved TBD: {tbd}
""")


def s(v):
    return "" if v is None else v


era, feature = specification["時期"], specification["一言特徴"]
route = MdTable.pick(specification, *SPEC_ROUTE_COLUMNS)
fixed = MdTable.pick(specification, *SPEC_FIXED_COLUMNS)

section_start = topology.find("#### MAP相互接続台帳 v2")
section_end = topology.find("#### 寺町の地形不変条件", section_start)
edges = [r for r in MdTable.section_rows(topology[section_start:section_end], "From", "To", "種別", "主路・状態") if s(r["From"]).startswith(f"{id_}.")]
connections = [" / ".join(s(x) for x in (r["From"], r["To"], r["種別"])) for r in edges]
if not connections:
    abort(f"{id_}: ready but has no topology entry")

print(f"""FIELD BACKGROUND CONTRACT — {id_}
Subject / unique landmark: {s(feature)}
Era and story phase: {s(era)}
Required route: {s(route)}
Fixed constraints: {s(fixed)}
Canonical exits: {'; '.join(connections)}
References: {s(refs)}

Contemporary K Prefecture, Japan, winter; handmade tabletop diorama, almost top-down 80–85 degree view, shallow depth, cardboard base and surrounding room visible. Use cotton snow, cardboard/paper-clay buildings, black paper or sandpaper roads, cellophane/resin water, rough cut edges, glue traces and restrained everyday snow-country grime only. No people, no text, no logos, no sky or distant perspective. Draw every canonical exit as a broad unobstructed route to the correct image edge; all other edges are closed. Keep treasure branches internal and separate from the required route. Do not place water, fences, walls, deep snow, stairs, rubble, or foreground objects across the required wheelchair route. For mountains or significant slopes, use a gentle serpentine or hairpin route rather than a straight climb.""")
