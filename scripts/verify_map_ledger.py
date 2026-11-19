"""MAP生成台帳の構造検査。YAMLから生成した互換ビューを読み、生成可能性を
"見た目の印象" ではなく 登録された全行・参照・接続端の不変条件で検査する。
表は見出し行の列名で読む（md_table.py。列の位置に依存しない）。台帳（docs/ledger）に行がある寺町のMAPは、
契約チェックリストの状態列を『台帳』とし、状態・未決・既定は台帳（verify_ledger.py）が検査する。
"""
import json
import math
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict

import ledger_yaml as LY
import md_table as MdTable
import verify_map_atlas as MapAtlasVerification
import verify_overseas_progression as OverseasProgression

ROOT = LY.ROOT  # LEDGER_ROOT で md の読み先も差し替える（ledger_yaml.py と同じ環境変数）
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, ".."))


def read(name):
    with open(os.path.join(ROOT, "docs", name), encoding="utf-8") as f:
        return f.read()


def fail(message):
    msg = f"FAIL: {message}"
    sys.stderr.write(msg if msg.endswith("\n") else msg + "\n")
    sys.exit(1)


def lines_keep(out):
    return out.splitlines(keepends=True)


def run_merged(cmd, env_extra):
    r = subprocess.run(cmd, env={**os.environ, **env_extra}, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8")
    return r.stdout, r.returncode == 0


view_builder = os.path.join(HERE, "map_source_views.py")
if os.path.isfile(view_builder):
    out, ok = run_merged(["uv", "run", "--project", REPO, "python3", view_builder, "check"], {"LEDGER_ROOT": ROOT})
    if not ok:
        fail(f"MAP生成ビューが台帳と一致しない: {' / '.join(lines_keep(out)[:3])}")

MAP_ID_PATTERN = "(?:" + "|".join(json.loads(read("topology/map-ids.json"))["areas"].keys()) + r")-\d{2}"


def ids():
    register = json.loads(read("topology/map-ids.json"))
    retired = list(register.get("retired", {}).keys())
    result = [f"{code}-{n:02d}" for code, count in register["areas"].items() for n in range(1, count + 1)]
    result = [i for i in result if i not in retired]
    if not (len(result) == register["expected_count"] and len(set(result)) == len(result)):
        fail("ID登録件数不一致")
    return result


def rsplit_comma(s):
    parts = s.split(",")
    while parts and parts[-1] == "":
        parts.pop()
    return parts


def uniq(xs):
    return list(dict.fromkeys(xs))


expected = ids()
checklist = read("map-contract-checklist.md")
specifications = read("map-specifications.md")
references = read("map-reference-research.md")
topology = read("map-topology.md")
assets = read("map-asset-registry.md")

contract_rows = [[r["ID"], r["状態"], r["Ref"], r["mask / 出力"], r["具体的TBD"]]
                 for r in MdTable.rows(checklist, "ID", "状態", "Ref", "mask / 出力", "具体的TBD")
                 if re.fullmatch(MAP_ID_PATTERN, r["ID"] or "")]

contract_ids = [r[0] for r in contract_rows]
if len(contract_ids) != len(expected):
    fail(f"契約行が登録件数ではない: {len(contract_ids)}")
if len(set(contract_ids)) != len(expected):
    fail(f"契約ID重複: {', '.join(k for k in uniq(contract_ids) if contract_ids.count(k) > 1)}")
if [i for i in expected if i not in contract_ids]:
    fail(f"契約ID不足: {', '.join(i for i in expected if i not in contract_ids)}")
if [i for i in contract_ids if i not in expected]:
    fail(f"未知の契約ID: {', '.join(i for i in contract_ids if i not in expected)}")

valid_status = ["blocked", "legacy-needs-review", "ready", "recreate-required-1920x1080", "台帳"]
# 台帳に行がある（廃止でない）MAP。旧 status（blocked／recreate-required…）は寺町だけ廃止し、状態列は『台帳』にする
ledger_maps = [r["MAP_ID"] for r in LY.read("MAP") if r["状態"] != "廃止"]
for id_, status, refs, mask, tbd in contract_rows:
    if status not in valid_status:
        fail(f"{id_}: 不正な状態 {status}")
    if status == "台帳" and id_ not in ledger_maps:
        fail(f"{id_}: 状態が『台帳』なのに台帳（docs/ledger/MAP.yaml）に行が無い")
    # The compatibility view preserves historical status. Current generation
    # readiness comes from required YAML keys, not the former Markdown status.
    if not refs:
        fail(f"{id_}: Refがない")
    if not mask:
        fail(f"{id_}: mask/output欄がない")
    if not tbd:
        fail(f"{id_}: 具体的TBDがない")
    if status == "ready":
        fail(f"{id_}: TBDありなのにready")
    if status != "legacy-needs-review":
        continue
    m = re.search(r"`([^`]+\.webp)`", mask)
    if not m:
        fail(f"{id_}: legacy画像パスがない")
    relative_image = m.group(1)
    if not os.path.isfile(os.path.join(ROOT, relative_image)):
        fail(f"{id_}: legacy画像がない {relative_image}")

reference_ids = uniq(re.findall(r"^\| (R\d{3}) \|", references, re.M))
for id_, _, refs, _, _ in contract_rows:
    for ref in rsplit_comma(refs):
        if ref not in reference_ids:
            fail(f"{id_}: 未登録Ref {ref}")

# 個別仕様の表は節ごとに見出しの名前が少し違う（接続／不変条件／接続／方位・主路・通行条件）。名前の候補から読む
SPEC_ROUTE_COLUMNS = ["不変条件／接続", "方位・主路・通行条件", "接続"]
spec_rows = [[r["MAP"].split()[0], r] for r in MdTable.rows(specifications, "MAP", "時期", "一言特徴")
             if re.match(MAP_ID_PATTERN + r"(?:\s|\Z)", r["MAP"] or "")]
spec_ids = uniq(s[0] for s in spec_rows)
if [i for i in expected if i not in spec_ids]:
    fail(f"個別仕様にないID: {', '.join(i for i in expected if i not in spec_ids)}")
for id_, r in spec_rows:
    if not len(r["cells"]) >= sum(1 for k in r if k != "cells"):
        fail(f"{id_}: 個別仕様の欄不足")
    if not r["一言特徴"]:
        fail(f"{id_}: 一言特徴がない")
    route = MdTable.pick(r, *SPEC_ROUTE_COLUMNS)
    if not route:
        fail(f"{id_}: 接続・通行条件がない")

asset_ids = uniq(re.findall(r"^\| (" + MAP_ID_PATTERN + r") \|", assets, re.M))
if [i for i in expected if i not in asset_ids]:
    fail(f"画像台帳にないID: {', '.join(i for i in expected if i not in asset_ids)}")

start = topology.find("#### MAP相互接続台帳 v2")
finish = topology.find("#### 寺町の地形不変条件", start) if start >= 0 else -1
if start < 0 or finish < 0:
    fail("v2接続台帳の範囲を取得できない")
topology_rows = []
for r in MdTable.section_rows(topology[start:finish], "From", "To", "種別", "主路・状態"):
    vals = [r["From"], r["To"], r["種別"], r["主路・状態"]]
    if not (len(r["cells"]) == 4 and all(v is not None for v in vals)):
        fail(f"v2接続行の欄不足: {' | '.join(r['cells'])}")
    topology_rows.append(vals)
if not topology_rows:
    fail("v2接続台帳が空")


def head(endpoint):
    return endpoint.split(".")[0]


def side(endpoint):
    p = endpoint.split(".", 1)
    return p[1] if len(p) > 1 else None


edge_ends = defaultdict(list)
door_ends = defaultdict(list)
active = []
pending = []
opposite = {"top": "bottom", "bottom": "top", "left": "right", "right": "left"}
for index, (from_, to, kind, reason) in enumerate(topology_rows):
    if kind not in ("edge", "door", "event", "oneway", "pending"):
        fail(f"v2 row {index + 1}: 未知・未設定の種別 {json.dumps(kind, ensure_ascii=False)}")
    for endpoint in (from_, to):
        if head(endpoint) not in expected:
            fail(f"v2 row {index + 1}: 未知MAP {head(endpoint)}")
    from_side = side(from_)
    to_side = side(to)
    if kind == "pending":
        if not reason:
            fail(f"v2 row {index + 1}: 保留理由がない")
        pending.append([from_, to])
        continue
    if head(from_) == head(to):
        fail(f"v2 row {index + 1}: 自己接続 {from_} -> {to}")
    if kind == "edge":
        if not (from_side in opposite and opposite[from_side] == to_side):
            fail(f"v2 row {index + 1}: 不正・反対辺でない {from_} -> {to}")
        for endpoint in (from_, to):
            edge_ends[endpoint].append(index + 1)
    elif kind == "event":
        if not all(re.search(r"\.event-[A-Za-z0-9_-]+\Z", p) for p in (from_, to)):
            fail("物語イベントの端名が不正")
    else:
        for endpoint in (from_, to):
            if not re.search(r"\.door(?:-[A-Za-z0-9_-]+)?\Z", endpoint):
                fail(f"v2 row {index + 1}: 扉IDがない {endpoint}")
            door_ends[endpoint].append(index + 1)
    active.append([head(from_), head(to), kind])
topology_ids = uniq(i for f, t, _, _ in topology_rows for i in (head(f), head(t)))
# デパートのエレベーターは接続台帳の外の別枠表（階選択遷移）。MAPを持たず、各階MAPが door-elevator を1つ持つ。
elevator_start = topology.find("#### 階選択遷移")
if not (elevator_start >= 0 and elevator_start < start):
    fail("階選択遷移の表がない")
elevator_rows = []
for r in MdTable.section_rows(topology[elevator_start:start], "階", "MAP", "エレベーター扉", "選べる行き先", "出現・解放"):
    vals = [r["階"], r["MAP"], r["エレベーター扉"], r["選べる行き先"], r["出現・解放"]]
    if not (len(r["cells"]) == 5 and all(v is not None for v in vals)):
        fail(f"階選択遷移行の欄不足: {' | '.join(r['cells'])}")
    elevator_rows.append(vals)
if [r[:2] for r in elevator_rows] != [["1階", "KRB-02"], ["2階", "KRB-03"], ["3階", "KRB-04"], ["4階", "KRB-05"], ["5階", "KRB-06"]]:
    fail(f"階選択遷移の階とMAPが不正: {json.dumps([r[:2] for r in elevator_rows], ensure_ascii=False)}")
for r in elevator_rows:
    if r[2] != f"{r[1]}.door-elevator":
        fail(f"エレベーター扉IDが不正 {r[1]}")
elevator_ids = [r[1] for r in elevator_rows]
if any(e.endswith(".door-elevator") for f, t, _, _ in topology_rows for e in (f, t)):
    fail("階選択遷移の扉が接続台帳にも載っている（二重管理）")
if not all(i in expected for i in elevator_ids):
    fail("エレベーターのMAPが独立して追加されている")
missing = [i for i in expected if i not in topology_ids and i not in elevator_ids]
if missing:
    fail(f"v2接続台帳にないMAP: {', '.join(missing)}")
reused = {k: v for k, v in edge_ends.items() if len(v) > 1}
if reused:
    fail(f"同一画像辺の二重使用: {', '.join(f'{k}({",".join(map(str, v))})' for k, v in reused.items())}")
reused_doors = {k: v for k, v in door_ends.items() if len(v) > 1}
if reused_doors:
    fail(f"同一扉端の二重使用: {', '.join(reused_doors.keys())}")

if pending:
    fail("旧サニーランドpendingは廃止")
entry = [r for r in topology_rows if r[2] == "event"]
if [[a, b, k] for a, b, k, _ in entry] != [["TRM-03.event-kiss", "BDY-01.event-mouth", "event"]]:
    fail("体内イベントは園庭（境内TRM-03の右の区画）から口BDY-01への一方向のみ")
flights = [r for r in topology_rows if r[2] == "oneway"]
if [[a, b, k] for a, b, k, _ in flights] != [["APT-02.door-gate", "OVS-01.door-arrival", "oneway"]]:
    fail("一方向の海外渡航が不正")
membership = json.loads(read("topology/areas.json"))
area_ids = [a["id"] for a in membership["areas"]]
if len(set(area_ids)) != len(area_ids):
    fail("エリアID重複")
members = [m for a in membership["areas"] for m in a["maps"]]
if sorted(members) != sorted(expected):
    fail("エリア所属が全MAP一意網羅でない")
for a in membership["areas"]:
    if sorted(a["layout"].keys()) != sorted(a["maps"]):
        fail(f"エリア配置のMAP不一致 {a['id']}")
    if not all(isinstance(xy, list) and len(xy) == 2 and all(isinstance(n, (int, float)) and not isinstance(n, bool) and math.isfinite(n) for n in xy) for xy in a["layout"].values()):
        fail(f"エリア配置座標が不正 {a['id']}")


def each_cons(xs, n=2):
    return [xs[i:i + n] for i in range(len(xs) - n + 1)]


body_paths = [["BDY-01", "BDY-02"], ["BDY-02", "BDY-03"], ["BDY-02", "BDY-04"], ["BDY-02", "BDY-05", "BDY-06"], ["BDY-02", "BDY-07", "BDY-08"], ["BDY-03", "BDY-09", "BDY-10", "BDY-11"], ["BDY-03", "BDY-12", "BDY-13", "BDY-14"], ["BDY-03", "BDY-15"], ["BDY-02", "BDY-16"], ["BDY-02", "BDY-17"]]
body = next((a for a in membership["areas"] if a["id"] == "body"), None)
if not (body and sorted(body["maps"]) == sorted(uniq(i for p in body_paths for i in p))):
    fail("体内17MAPの所属不一致")
body_pairs = sorted(sorted(c) for path in body_paths for c in each_cons(path))
body_active = [e for e in active if e[0] in body["maps"] and e[1] in body["maps"]]
if not (sorted(sorted([a, b]) for a, b, _ in body_active) == body_pairs and all(k == "door" for _, _, k in body_active)):
    fail("体内の上半身/下半身・手2枚・足3枚の一本道接続が不一致")
body_external = [e for e in active if (e[0] in body["maps"]) != (e[1] in body["maps"])]
if body_external != [["TRM-03", "BDY-01", "event"]]:
    fail("園庭以外からの体内入口／逆方向出口がある")
coords = body["layout"]
ux, uy = coords["BDY-02"]
lx, ly = coords["BDY-03"]
if not (ux == lx and uy < ly):
    fail("胴体は上半身と下半身の縦2MAP")
if not (coords["BDY-04"][0] == ux and coords["BDY-04"][1] < uy):
    fail("頭は胴体の上")
for i, path in enumerate([["BDY-02", "BDY-05", "BDY-06"], ["BDY-02", "BDY-07", "BDY-08"], ["BDY-03", "BDY-09", "BDY-10", "BDY-11"], ["BDY-03", "BDY-12", "BDY-13", "BDY-14"]]):
    base_x, base_y = coords[path[0]]
    direction_x = 1 if i % 2 == 0 else -1
    direction_y = -1 if i < 2 else 1
    if not (all((coords[j][0] - base_x) * direction_x > 0 for j in path[1:]) and all((coords[b][1] - coords[a][1]) * direction_y > 0 for a, b in each_cons(path))):
        fail("手は左右斜め上・足は左右斜め下の連続通路")
expected_spokes = {"upper_torso": "BDY-02", "lower_torso": "BDY-03", "head": "BDY-04", "left_arm": ["BDY-05", "BDY-06"], "right_arm": ["BDY-07", "BDY-08"], "left_leg": ["BDY-09", "BDY-10", "BDY-11"], "right_leg": ["BDY-12", "BDY-13", "BDY-14"], "rooms": ["BDY-15", "BDY-16", "BDY-17"]}
if membership.get("body_spokes") != expected_spokes:
    fail("体内方向・枚数契約不一致")
sunny = ["SNL-01", "SNL-02", "SNL-04", "SNL-05", "SNL-06", "SNL-09", "SNL-10", "SNL-11", "SNL-12", "SNL-03", "SNL-07", "SNL-08"]
sunny_ring = ["SNL-01", "SNL-02", "SNL-04", "SNL-05", "SNL-06", "SNL-09", "SNL-10", "SNL-11", "SNL-12", "SNL-01"]
for a, b in each_cons(sunny_ring):
    if not any(sorted([x, y]) == sorted([a, b]) for x, y, _ in active):
        fail(f"サニーランド円環がない {a} -> {b}")
for id_ in ("SNL-07", "SNL-08"):
    routes = [e for e in active if sorted([e[0], e[1]]) == sorted(["SNL-06", id_])]
    if len(routes) != 2:
        fail(f"任意施設の入口出口がない {id_}")
    if any((a == id_ or b == id_) and "SNL-06" not in (a, b) for a, b, _ in active):
        fail(f"任意施設に未承認出口 {id_}")
if not any(sorted([a, b]) == ["SNL-02", "SNL-03"] for a, b, _ in active):
    fail("ゲームセンター分岐がない")
sunny_expected = [sorted(c) for c in each_cons(sunny_ring)] + [["SNL-02", "SNL-03"]] + [sorted(["SNL-06", i]) for i in ("SNL-07", "SNL-08") for _ in range(2)]
sunny_actual = [sorted([a, b]) for a, b, _ in active if a in sunny and b in sunny]
if sorted(sunny_actual) != sorted(sunny_expected):
    fail("サニーランド接続集合不一致")


def graph_check(name, nodes, active, minimum):
    edges = [e for e in active if e[0] in nodes and e[1] in nodes]
    pairs = [sorted([a, b]) for a, b, _ in edges]
    if len({tuple(p) for p in pairs}) != len(pairs):
        fail(f"{name}: MAP間接続が重複")
    visited = []
    queue = [nodes[0]]
    while queue:
        node = queue.pop(0)
        if node in visited:
            continue
        visited.append(node)
        for a, b, _ in edges:
            if a == node and b not in visited:
                queue.append(b)
            if b == node and a not in visited:
                queue.append(a)
    if sorted(visited) != sorted(nodes):
        fail(f"{name}: 到達不能MAP {', '.join(n for n in nodes if n not in visited)}")
    cycles = len(edges) - len(nodes) + 1
    if cycles < minimum:
        fail(f"{name}: 独立閉路{cycles}は最低{minimum}未満")
    return cycles


garden = [f"GRD-{n:02d}" for n in range(1, 11)]
castle = [f"CST-{n:02d}" for n in range(1, 11)]
towers = [f"OVS-{n:02d}" for n in range(4, 21)]
garden_cycles = graph_check("兼六園", garden, active, 4)
castle_cycles = graph_check("金沢城", castle, active, 3)
tower_cycles = graph_check("双塔", towers, active, 1)
third = ["OVS-16", "OVS-17", "OVS-18", "OVS-19", "OVS-20"]
third_pairs = [sorted(c) for c in each_cons(third)]
for a, b, _ in active:
    if a in third and b in third:
        if sorted([a, b]) not in third_pairs:
            fail("第3塔の階飛ばし接続")
    elif (a in third) != (b in third):
        if sorted([a, b]) != ["OVS-15", "OVS-16"]:
            fail("第3塔の事前進入を許す未承認接続")
for route in (["OVS-04", "OVS-05", "OVS-06", "OVS-07", "OVS-08", "OVS-09", "OVS-15"], ["OVS-04", "OVS-10", "OVS-11", "OVS-12", "OVS-13", "OVS-14", "OVS-15"], ["OVS-15", "OVS-16", "OVS-17", "OVS-18", "OVS-19", "OVS-20"]):
    for a, b in each_cons(route):
        if not any(kind == "door" and sorted([x, y]) == sorted([a, b]) for x, y, kind in active):
            fail(f"双塔: 階層経路がない {a} -> {b}")
mountain = ["UTS-01", "UTS-02", "UTS-03", "UTS-04", "UTS-05"]
mountain_pairs = [sorted(c) for c in each_cons(mountain)]
actual_mountain = [sorted([a, b]) for a, b, _ in active if a in mountain and b in mountain]
if sorted(actual_mountain) != sorted(mountain_pairs):
    fail("卯辰山: 一本道の接続不一致・近道あり")
allowed_entrances = [sorted(["KRB-11", "UTS-01"]), sorted(["UTS-05", "SNL-01"])]
for a, b, _ in active:
    if (a in mountain) == (b in mountain):
        continue
    if sorted([a, b]) not in allowed_entrances:
        fail(f"卯辰山: 分岐禁止 {a} -> {b}")

for filename, panels in (("late-dungeons.svg", [garden, castle, towers, mountain]), ("sunnyland.svg", [sunny])):
    diagram_path = os.path.join(ROOT, "docs/topology", filename)
    if not os.path.isfile(diagram_path):
        fail("接続図がない")
    try:
        diagram = ET.parse(diagram_path).getroot()
    except ET.ParseError as e:
        fail(f"接続図のXML不正: {e}")
    expected_nodes = sorted(n for p in panels for n in p)
    actual_nodes = sorted(n.attrib["data-map"] for n in diagram.iter() if "data-map" in n.attrib)
    if actual_nodes != expected_nodes:
        fail("接続図のMAP集合が正本と不一致")
    expected_paths = sorted([*sorted([a, b]), kind] for a, b, kind in active if a in expected_nodes and b in expected_nodes)
    actual_paths = sorted([*sorted([p.attrib.get("data-from", ""), p.attrib.get("data-to", "")]), p.attrib.get("class", "")]
                          for p in diagram.iter() if "data-from" in p.attrib or "data-to" in p.attrib)
    if actual_paths != expected_paths:
        fail("接続図の有効辺集合が正本と不一致（欠落・余分・保留の実線化）")
try:
    OverseasProgression.verify(OverseasProgression.load(os.path.join(ROOT, "docs/topology/overseas-progression.json")))
except Exception as e:
    fail(f"海外状態契約: {e}")

try:
    MapAtlasVerification.verify(ROOT)
except Exception as e:
    fail(f"全MAP図: {e}")

# 隣り合う屋外MAPのつなぎ目で、道の縁の境界の種類が両側で一致する（決定 SIT.road-edge-solid-boundary、Issue #191）。未決以外の食い違いはFAIL。
# 接続の構造（ID登録・反対辺・端の再利用など）を先に全部通してから見る。壊れた接続でここが先に落ちると、構造の診断が『つなぎ目の食い違い』に隠れる（#316）
seam_checker = os.path.join(HERE, "verify_seam_boundaries.py")
if os.path.isfile(seam_checker):
    out, ok = run_merged(["uv", "run", "--with", "numpy", "--with", "scipy", "--with", "opencv-python-headless", "--with", "pillow", "python3", seam_checker], {"LEDGER_ROOT": ROOT})
    if not ok:
        fail(f"つなぎ目の境界の種類が隣のMAPと食い違う: {' / '.join([l for l in lines_keep(out) if 'FAIL' in l][:3])}")

print(f"PASS: MAP contracts={len(contract_ids)}, assets={len(asset_ids)}, specs={len(spec_ids)}, refs={len(reference_ids)}, topology MAPs={len(topology_ids)}, topology rows={len(topology_rows)}, pending={len(pending)}, cycles garden={garden_cycles} castle={castle_cycles} towers={tower_cycles}, full atlas={len(contract_ids)} MAPs/{len(topology_rows)} connections/{len(membership['areas'])} areas, overview and all area diagrams verified")
