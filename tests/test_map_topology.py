"""Exercise the real ledger CLI against isolated, semantically mutated inputs."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
import xml.etree.ElementTree as ET
from tests.ledger_test_support import L, environment
import ledger_flat as F
import ledger_build as B


ROOT = Path(__file__).resolve().parents[1]
_REGISTER = json.loads((ROOT / "docs/topology/map-ids.json").read_text())
EXPECTED_IDS = {f"{code}-{n:02}"
                for code, count in _REGISTER["areas"].items()
                for n in range(1, count + 1)} - set(_REGISTER.get("retired", {}))


class MapTopologyFixture(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in ("docs", "scripts"):
            shutil.copytree(ROOT / name, self.root / name,
                            ignore=shutil.ignore_patterns("handoff", "Issue出典.yaml", "Issue命題.yaml"))
        # Invoke production scripts with LEDGER_ROOT; this keeps uv on the one
        # existing project environment instead of creating fixture environments.
        self.sources_changed = False
        # Legacy image existence is part of the CLI contract; copy tiny fixtures
        # rather than the production image collection.
        for image in (ROOT / "assets/images/fields/legacy").glob("*.webp"):
            target = self.root / image.relative_to(ROOT)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(b"fixture")

    def cli(self):
        self.refresh_source_views()
        return subprocess.run(["ruby", str(ROOT / "scripts/verify_map_ledger.rb")],
                              cwd=self.root, env=environment(self.root), capture_output=True, text=True)

    def yaml_rows(self, table):
        return L.parse(table, (self.root / "docs/ledger" / (table + ".yaml")).read_text())

    def write_yaml(self, table, values):
        (self.root / "docs/ledger" / (table + ".yaml")).write_text(L.dumps(table, values))
        self.sources_changed = True

    def refresh_source_views(self):
        if not self.sources_changed:
            return
        result = subprocess.run(["uv", "run", "python3", str(ROOT / "scripts/map_source_views.py"), "build"],
                                cwd=ROOT, env=environment(self.root), capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.sources_changed = False

    def sync_connections(self, values):
        self.write_yaml("接続", values)
        views = self.yaml_rows("文書ビュー")
        for view in views:
            if view["元の表"] == "接続":
                view["行参照"] = ";".join(r["端A"] + ">" + r["端B"] for r in values)
        self.write_yaml("文書ビュー", views)

    def edit(self, name, before, after):
        path = self.root / "docs" / name
        source = path.read_text(encoding="utf-8")
        self.assertIn(before, source)
        path.write_text(source.replace(before, after, 1), encoding="utf-8")

    def reject(self, *diagnostics):
        result = self.cli()
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("FAIL:", result.stderr)
        for diagnostic in diagnostics:
            self.assertIn(diagnostic, result.stderr)

    def topology(self, before, after):
        values = self.yaml_rows("接続")
        for value in values:
            old = self.connection_line(value)
            if before not in old:
                continue
            changed = old.replace(before, after, 1)
            cells = [v.strip() for v in changed.strip().strip("|").split("|")]
            if len(cells) != 4:
                # A truncated legacy row corresponds to a missing canonical
                # kind/reason; change that fact, never corrupt a generated view.
                cells = cells[:2] + ["", ""]
            value.update(zip(("端A", "端B", "種別", "主路・状態"), cells))
            self.sync_connections(values)
            return
        values = self.yaml_rows("特殊遷移")
        columns = ("階", "起点MAP", "起点端", "行先表示", "条件")
        for value in values:
            old = "| " + " | ".join(value[k] for k in columns) + " |"
            if before in old:
                changed = old.replace(before, after, 1)
                cells = [v.strip() for v in changed.strip().strip("|").split("|")]
                self.assertEqual(len(cells), len(columns))
                value.update(zip(columns, cells))
                self.write_yaml("特殊遷移", values)
                return
        self.edit("map-topology.md", before, after)

    def append_connection(self, line):
        cells = [v.strip() for v in line.strip().strip("|").split("|")]
        value = dict.fromkeys(L.SCHEMA["接続"], "")
        value.update(zip(("端A", "端B", "種別", "主路・状態"), cells))
        self.sync_connections(self.yaml_rows("接続") + [value])

    def render(self):
        self.refresh_source_views()
        for script in ("render_late_topology.rb", "render_sunnyland_topology.rb", "render_map_atlas.rb"):
            result = subprocess.run(["ruby", str(ROOT / "scripts" / script)],
                                    cwd=self.root, env=environment(self.root), capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)

    def reject_sunny_contract(self, *diagnostics):
        # The renderer now reads canonical YAML and rejects invalid topology
        # itself. Also require the verifier to identify the broken domain fact,
        # so a stale diagram alone cannot make this mutation test pass.
        self.refresh_source_views()
        result = subprocess.run(["ruby", str(ROOT / "scripts/render_sunnyland_topology.rb")],
                                cwd=self.root, env=environment(self.root), capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("sunnyland connection ledger mismatch", result.stderr)
        self.reject(*diagnostics)

    def remove_connection(self, prefix):
        values = self.yaml_rows("接続")
        match = next(value for value in values if self.connection_line(value).startswith(prefix))
        values.remove(match)
        self.sync_connections(values)

    @staticmethod
    def connection_line(row):
        return "| " + " | ".join(row[k] for k in ("端A", "端B", "種別", "主路・状態")) + " |"

    def connection_rows(self):
        return [self.connection_line(row) for row in self.yaml_rows("接続")]

    def mutate_registry(self, mutate):
        """Change the canonical placement/structure inputs, then derive JSON."""
        values = json.loads((self.root / "docs/topology/areas.json").read_text())
        mutate(values)
        original = self.yaml_rows("図配置")
        areas = self.yaml_rows("エリア")
        self.assertEqual(len(areas), len(values["areas"]))
        for source, selected in zip(areas, values["areas"]):
            source.update(エリアID=selected["id"], 名称=selected["name"])
        self.write_yaml("エリア", areas)
        placements = []
        for area in values["areas"]:
            for index, ident in enumerate(area["maps"], 1):
                prior = next((r for r in original if r["MAP_ID"] == ident), dict.fromkeys(L.SCHEMA["図配置"], ""))
                item = prior.copy()
                xy = area["layout"].get(ident, [0, 0])
                item.update(配置ID=f"FIXTURE-{len(placements)}", エリアID=area["id"], MAP_ID=ident,
                            順番=str(index), X=str(xy[0]), Y=str(xy[1]))
                placements.append(item)
        self.write_yaml("図配置", placements)
        structure = {k: v for k, v in values.items() if k not in ("areas", "schema_version", "_provenance")}
        self.write_yaml("エリア構造", [dict(経路=p, 型=t, 値=v, 根拠="fixture") for p, v, t in F.flatten(structure)])
        tables = {name: self.yaml_rows(name) for name in ("エリア", "図配置", "エリア構造")}
        (self.root / "docs/topology/areas.json").write_text(json.dumps(B.build_areas(tables), ensure_ascii=False))

    def pair_row(self, a, b):
        return next(row for row in self.connection_rows()
                    if {cell.strip().split(".")[0] for cell in row.split("|")[1:3]} == {a, b})

    def remove_pair(self, a, b):
        self.remove_connection(self.pair_row(a, b))

    def diagram(self):
        return self.root / "docs/topology/late-dungeons.svg"


class MapTopologyTests(MapTopologyFixture):
    def test_current_expanded_contracts_pass_without_mutating_inputs(self):
        paths = sorted((self.root / "docs").rglob("*"))
        before = {p: hashlib.sha256(p.read_bytes()).digest() for p in paths if p.is_file()}
        results = [self.cli(), self.cli()]
        for result in results:
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn(f"contracts={len(EXPECTED_IDS)}", result.stdout)
        self.assertEqual(results[0].stdout, results[1].stdout)
        self.assertEqual(before, {p: hashlib.sha256(p.read_bytes()).digest() for p in before})

    def test_one_missing_contract_rejected(self):
        self.write_yaml("MAP契約", [r for r in self.yaml_rows("MAP契約") if r["契約ID"] != "CHECK-CST-10"])
        # Retain the descriptor's reference to the deleted source: a missing
        # canonical contract must fail before a stale document can hide it.
        result = subprocess.run(["uv", "run", "python3", str(ROOT / "scripts/map_source_views.py"), "check"],
                                cwd=ROOT, env=environment(self.root), capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("CHECK-CST-10", result.stderr)
        self.sources_changed = False
        self.reject()

    def test_one_extra_contract_rejected(self):
        values = self.yaml_rows("MAP契約")
        source = next(r for r in values if r["契約ID"] == "CHECK-CST-10")
        duplicate = source.copy()
        duplicate["契約ID"] = "CHECK-extra"
        self.write_yaml("MAP契約", values + [duplicate])
        views = self.yaml_rows("文書ビュー")
        view = next(v for v in views if "CHECK-CST-10" in v["行参照"])
        view["行参照"] += ";CHECK-extra"
        self.write_yaml("文書ビュー", views)
        self.reject()

    def test_duplicate_and_missing_contract_at_expected_count_rejected(self):
        values = self.yaml_rows("MAP契約")
        next(r for r in values if r["契約ID"] == "CHECK-CST-10")["MAP_ID"] = "CST-09"
        self.write_yaml("MAP契約", values)
        self.reject("重複", "CST-09")

    def test_unknown_contract_at_expected_count_rejected(self):
        values = self.yaml_rows("MAP契約")
        next(r for r in values if r["契約ID"] == "CHECK-CST-10")["MAP_ID"] = "KRB-99"
        self.write_yaml("MAP契約", values)
        self.reject("CST-10")

    def test_edge_must_use_opposite_sides(self):
        self.topology("| TRM-16.right | TRM-15.left | edge |", "| TRM-16.right | TRM-15.right | edge |")
        self.reject("反対辺")

    def test_unknown_edge_side_rejected(self):
        self.topology("| TRM-16.right | TRM-15.left | edge |", "| TRM-16.up | TRM-15.down | edge |")
        self.reject()

    def test_missing_edge_side_rejected(self):
        self.topology("| TRM-16.right | TRM-15.left | edge |", "| TRM-16. | TRM-15.left | edge |")
        self.reject()

    def test_missing_endpoint_separator_cannot_silently_drop_row(self):
        self.topology("| TRM-16.right | TRM-15.left | edge |", "| TRM-16 | TRM-15.left | edge |")
        self.reject()

    def test_reused_edge_endpoint_rejected(self):
        self.append_connection("| TRM-16.right | TRM-06.left | edge | 同一端の再利用 |")
        self.reject("TRM-16.right")

    def test_unknown_map_endpoint_rejected(self):
        self.topology("| TRM-16.right | TRM-15.left | edge |", "| E99.right | TRM-15.left | edge |")
        self.reject("E99")

    def test_unknown_source_id_cannot_silently_drop_row(self):
        self.topology("| TRM-16.right | TRM-15.left | edge |", "| UNKNOWN.right | TRM-15.left | edge |")
        self.reject("UNKNOWN")

    def test_malformed_row_without_kind_or_reason_rejected(self):
        self.topology("| TRM-16.right | TRM-15.left | edge |", "| TRM-16.right | TRM-15.left |")
        self.reject("種別")

    def test_missing_door_identifier_rejected(self):
        row = self.pair_row("TRM-04", "TRM-05")
        self.topology(row, row.replace("TRM-04.door-west", "TRM-04."))
        self.reject()

    def test_reused_door_endpoint_rejected(self):
        self.append_connection("| TRM-04.door-west | TRM-06.door-extra | door | 扉端の再利用 |")
        self.reject("TRM-04.door-west")

    def test_unknown_connection_kind_rejected(self):
        self.topology("| TRM-16.right | TRM-15.left | edge |", "| TRM-16.right | TRM-15.left | teleport |")
        self.reject()

    def test_blank_connection_kind_rejected(self):
        self.topology("| TRM-16.right | TRM-15.left | edge |", "| TRM-16.right | TRM-15.left |  |")
        self.reject()

    def test_mountain_shortcut_rejected(self):
        self.append_connection("| UTS-01.door-shortcut | UTS-05.door-shortcut | door | 禁止の登山近道 |")
        self.reject()

    def test_mountain_branch_rejected(self):
        self.append_connection("| UTS-03.door-branch | TRM-06.door-mountain | door | 禁止の登山枝 |")
        self.reject()

    def test_missing_mountain_segment_rejected(self):
        self.remove_connection("| UTS-02.top | UTS-03.bottom |")
        self.reject()

    def test_garden_three_cycles_rejected(self):
        self.remove_connection("| GRD-03.right | GRD-04.left |")
        self.render()
        self.reject("兼六園", "3", "4")

    def test_garden_five_cycles_accepted(self):
        self.append_connection("| GRD-01.door-extra | GRD-04.door-extra | door | 境界検証用の仮接続 |")
        self.render()
        result = self.cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("garden=5", result.stdout)

    def test_castle_two_cycles_rejected(self):
        self.remove_connection("| CST-03.door-south | CST-04.door-north |")
        self.render()
        self.reject("金沢城", "2", "3")

    def test_castle_four_cycles_accepted(self):
        self.append_connection("| CST-04.door-extra | CST-08.door-extra | door | 境界検証用の仮接続 |")
        self.render()
        result = self.cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("castle=4", result.stdout)

    def test_missing_left_tower_floor_connection_rejected(self):
        self.remove_pair("OVS-05", "OVS-06")
        self.render()
        self.reject()

    def test_third_tower_shortcut_bypass_rejected(self):
        self.append_connection("| OVS-04.door-extra | OVS-16.door-extra | door | 脱出塔への事前進入 |")
        self.render()
        self.reject()

    def test_external_third_tower_lower_floor_bypass_rejected(self):
        self.append_connection("| OVS-03.door-extra | OVS-17.door-extra | door | 荒野から脱出塔4階へ不正進入 |")
        self.render()
        self.reject()

    def test_bridge_cannot_skip_third_tower_upper_floor(self):
        self.append_connection("| OVS-15.door-extra | OVS-17.door-extra | door | 空中通路から脱出塔5階を省略 |")
        self.render()
        self.reject()

    def test_left_tower_route_cannot_be_replaced_by_cross_link(self):
        self.remove_pair("OVS-05", "OVS-06")
        self.append_connection("| OVS-05.door-cross | OVS-12.door-cross | door | 閉路数だけでは発見できない左塔経路欠落 |")
        self.render()
        self.reject()

    def test_right_tower_route_cannot_be_replaced_by_cross_link(self):
        self.remove_pair("OVS-10", "OVS-11")
        self.append_connection("| OVS-10.door-cross | OVS-07.door-cross | door | 閉路数だけでは発見できない右塔経路欠落 |")
        self.render()
        self.reject()

    def test_sunny_aquarium_ring_route_is_required(self):
        self.remove_pair("SNL-04", "SNL-05")
        self.reject_sunny_contract("サニーランド円環", "SNL-04", "SNL-05")

    def test_sunny_hotel_ring_route_is_required(self):
        self.remove_pair("SNL-12", "SNL-11")
        self.reject_sunny_contract("サニーランド円環", "SNL-11", "SNL-12")

    def test_pending_requires_utf8_reason(self):
        self.append_connection("| TRM-03.door-future | TRM-06.door-future | pending |  |")
        self.reject("保留理由")

    def test_optional_otter_has_two_distinct_ports(self):
        self.remove_pair("SNL-06", "SNL-07")
        self.reject_sunny_contract("任意施設の入口出口", "SNL-07")

    def test_optional_cave_has_two_distinct_ports(self):
        self.remove_pair("SNL-06", "SNL-08")
        self.reject_sunny_contract("任意施設の入口出口", "SNL-08")

    def test_optional_otter_three_doors_rejected(self):
        self.append_connection("| SNL-06.door-extra | SNL-07.door-extra | door | 任意館の余分な扉 |")
        self.reject_sunny_contract("任意施設の入口出口", "SNL-07")

    def test_expanded_id_set_is_exact(self):
        for name in ("map-contract-checklist.md", "map-asset-registry.md"):
            rows = (self.root / "docs" / name).read_text().splitlines()
            actual = {line.split("|")[1].strip() for line in rows if line.startswith("| ")
                      and line.split("|")[1].strip() in EXPECTED_IDS}
            self.assertEqual(actual, EXPECTED_IDS, name)

    def test_sunny_has_two_routes_without_optional_facilities(self):
        ring = {"SNL-01", "SNL-02", "SNL-04", "SNL-05", "SNL-06", "SNL-09", "SNL-10", "SNL-11", "SNL-12"}
        adjacency = {node: set() for node in ring}
        for row in self.connection_rows():
            a, b = [cell.strip().split(".")[0] for cell in row.split("|")[1:3]]
            if a in ring and b in ring:
                adjacency[a].add(b)
                adjacency[b].add(a)
        paths = []

        def walk(node, path):
            if node == "SNL-06":
                paths.append(path)
                return
            for other in adjacency[node] - set(path):
                walk(other, path + [other])

        walk("SNL-01", ["SNL-01"])
        expected = [["SNL-01", "SNL-02", "SNL-04", "SNL-05", "SNL-06"],
                    ["SNL-01", "SNL-12", "SNL-11", "SNL-10", "SNL-09", "SNL-06"]]
        self.assertEqual(sorted(paths), sorted(expected))
        self.assertFalse(set(paths[0][1:-1]) & set(paths[1][1:-1]))

    def test_optional_facilities_are_two_distinct_named_door_connections(self):
        for facility in ("SNL-07", "SNL-08"):
            with self.subTest(facility=facility):
                ports = []
                for row in self.connection_rows():
                    cells = [cell.strip() for cell in row.split("|")]
                    if {cell.split(".")[0] for cell in cells[1:3]} == {"SNL-06", facility}:
                        self.assertEqual(cells[3], "door")
                        ports.extend(cells[1:3])
                self.assertEqual(len(ports), 4)
                self.assertEqual(len(set(ports)), 4)

    def test_diagram_missing_edge_rejected(self):
        tree = ET.parse(self.diagram())
        parent = next(node for node in tree.iter() if any(child.get("data-from") for child in node))
        parent.remove(next(child for child in parent if child.get("data-from")))
        tree.write(self.diagram(), encoding="utf-8")
        self.reject("接続図", "辺集合")

    def test_diagram_extra_edge_rejected(self):
        tree = ET.parse(self.diagram())
        ET.SubElement(tree.getroot(), "path", {"data-from": "GRD-01", "data-to": "GRD-04", "class": "edge"})
        tree.write(self.diagram(), encoding="utf-8")
        self.reject("接続図", "辺集合")

    def test_diagram_pending_solid_edge_rejected(self):
        tree = ET.parse(self.diagram())
        ET.SubElement(tree.getroot(), "path", {"data-from": "SNL-01", "data-to": "SNL-08", "class": "edge"})
        tree.write(self.diagram(), encoding="utf-8")
        self.reject("接続図", "辺集合")

    def test_diagram_missing_map_rejected(self):
        tree = ET.parse(self.diagram())
        node = next(node for node in tree.iter() if node.get("data-map") == "GRD-01")
        node.attrib.pop("data-map")
        tree.write(self.diagram(), encoding="utf-8")
        self.reject("接続図", "MAP集合")

    def test_diagram_extra_map_rejected(self):
        tree = ET.parse(self.diagram())
        ET.SubElement(tree.getroot(), "circle", {"data-map": "KRB-99"})
        tree.write(self.diagram(), encoding="utf-8")
        self.reject("接続図", "MAP集合")


    def test_elevator_floor_select_table_is_separate_from_ledger(self):
        rows = self.connection_rows()
        self.assertFalse([r for r in rows if "door-elevator" in r])
        source = (self.root / "docs/map-topology.md").read_text(encoding="utf-8")
        for map_id in ("KRB-02", "KRB-03", "KRB-04", "KRB-05", "KRB-06"):
            self.assertIn(f"| {map_id}.door-elevator |", source)

    def test_elevator_door_in_ledger_rejected(self):
        self.append_connection("| KRB-02.door-elevator | KRB-04.door-elevator | door | 二重管理 |")
        self.reject("階選択遷移", "二重管理")

    def test_elevator_table_missing_floor_rejected(self):
        self.topology("| 4階 | KRB-05 | KRB-05.door-elevator |", "| 4階 | KRB-99 | KRB-99.door-elevator |")
        self.reject("階選択遷移")

    def test_elevator_door_id_must_match_map(self):
        self.topology("| KRB-04.door-elevator |", "| KRB-04.door-lift |")
        self.reject("エレベーター扉ID")


if __name__ == "__main__":
    unittest.main()
