"""Exercise the real ledger CLI against isolated, semantically mutated inputs."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
_REGISTER = json.loads((ROOT / "docs/topology/map-ids.json").read_text())
EXPECTED_IDS = {f"{code}-{n:02}"
                for code, count in _REGISTER["areas"].items()
                for n in range(1, count + 1)} - set(_REGISTER.get("retired", {}))


class MapTopologyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in ("docs", "scripts"):
            shutil.copytree(ROOT / name, self.root / name)
        # Legacy image existence is part of the CLI contract; copy tiny fixtures
        # rather than the production image collection.
        for image in (ROOT / "assets/images/fields/legacy").glob("*.webp"):
            target = self.root / image.relative_to(ROOT)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(b"fixture")

    def cli(self):
        return subprocess.run(["ruby", "scripts/verify_map_ledger.rb"],
                              cwd=self.root, capture_output=True, text=True)

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
        self.edit("map-topology.md", before, after)

    def append_connection(self, line):
        self.topology("#### 寺町の地形不変条件", line + "\n\n#### 寺町の地形不変条件")

    def render(self):
        for script in ("render_late_topology.rb", "render_sunnyland_topology.rb", "render_map_atlas.rb"):
            result = subprocess.run(["ruby", "scripts/" + script],
                                    cwd=self.root, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)

    def remove_connection(self, prefix):
        path = self.root / "docs/map-topology.md"
        source = path.read_text()
        row = next(line for line in source.splitlines() if line.startswith(prefix))
        path.write_text(source.replace(row + "\n", "", 1))

    def connection_rows(self):
        source = (self.root / "docs/map-topology.md").read_text()
        table = source.split("#### MAP相互接続台帳 v2", 1)[1].split("#### 寺町の地形不変条件", 1)[0]
        return [line for line in table.splitlines() if line.startswith("| ")
                and "." in line.split("|")[1]]

    def pair_row(self, a, b):
        return next(row for row in self.connection_rows()
                    if {cell.strip().split(".")[0] for cell in row.split("|")[1:3]} == {a, b})

    def remove_pair(self, a, b):
        self.remove_connection(self.pair_row(a, b))

    def diagram(self):
        return self.root / "docs/topology/late-dungeons.svg"

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
        path = self.root / "docs/map-contract-checklist.md"
        rows = path.read_text().splitlines(keepends=True)
        path.write_text("".join(row for row in rows if not row.startswith("| CST-10 |")))
        self.reject()

    def test_one_extra_contract_rejected(self):
        path = self.root / "docs/map-contract-checklist.md"
        source = path.read_text()
        row = next(line for line in source.splitlines() if line.startswith("| CST-10 |"))
        path.write_text(source + "\n" + row + "\n")
        self.reject()

    def test_duplicate_and_missing_contract_at_expected_count_rejected(self):
        self.edit("map-contract-checklist.md", "| CST-10 |", "| CST-09 |")
        self.reject("重複", "CST-09")

    def test_unknown_contract_at_expected_count_rejected(self):
        self.edit("map-contract-checklist.md", "| CST-10 |", "| KRB-99 |")
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
        self.reject("欄不足")

    def test_missing_door_identifier_rejected(self):
        self.topology("| TRM-04.door-west | TRM-05.door-hall | door |",
                      "| TRM-04. | TRM-05.door-hall | door |")
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
        self.render()
        self.reject()

    def test_sunny_hotel_ring_route_is_required(self):
        self.remove_pair("SNL-12", "SNL-11")
        self.render()
        self.reject()

    def test_pending_requires_utf8_reason(self):
        self.append_connection("| TRM-03.door-future | TRM-06.door-future | pending |  |")
        self.reject("保留理由")

    def test_optional_otter_has_two_distinct_ports(self):
        self.remove_pair("SNL-06", "SNL-07")
        self.render()
        self.reject()

    def test_optional_cave_has_two_distinct_ports(self):
        self.remove_pair("SNL-06", "SNL-08")
        self.render()
        self.reject()

    def test_optional_otter_three_doors_rejected(self):
        self.append_connection("| SNL-06.door-extra | SNL-07.door-extra | door | 任意館の余分な扉 |")
        self.render()
        self.reject()

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
