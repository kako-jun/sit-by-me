"""Exercise the real ledger CLI against isolated, semantically mutated inputs."""
import hashlib
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]


class MapTopologyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in ("docs", "scripts"):
            shutil.copytree(ROOT / name, self.root / name)
        # Legacy image existence is part of the CLI contract; copy tiny fixtures
        # rather than the production image collection.
        for image in (ROOT / "assets/images/fields/legacy").glob("*.png"):
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
        result = subprocess.run(["ruby", "scripts/render_late_topology.rb"],
                                cwd=self.root, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def remove_connection(self, prefix):
        path = self.root / "docs/map-topology.md"
        source = path.read_text()
        row = next(line for line in source.splitlines() if line.startswith(prefix))
        path.write_text(source.replace(row + "\n", "", 1))

    def diagram(self):
        return self.root / "docs/topology/late-dungeons.svg"

    def test_current_104_contracts_pass_without_mutating_inputs(self):
        paths = sorted((self.root / "docs").rglob("*"))
        before = {p: hashlib.sha256(p.read_bytes()).digest() for p in paths if p.is_file()}
        results = [self.cli(), self.cli()]
        for result in results:
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("contracts=104", result.stdout)
        self.assertEqual(results[0].stdout, results[1].stdout)
        self.assertEqual(before, {p: hashlib.sha256(p.read_bytes()).digest() for p in before})

    def test_103_contracts_rejected(self):
        path = self.root / "docs/map-contract-checklist.md"
        rows = path.read_text().splitlines(keepends=True)
        path.write_text("".join(row for row in rows if not row.startswith("| F60 |")))
        self.reject("104")

    def test_105_contracts_rejected(self):
        path = self.root / "docs/map-contract-checklist.md"
        source = path.read_text()
        row = next(line for line in source.splitlines() if line.startswith("| F60 |"))
        path.write_text(source + "\n" + row + "\n")
        self.reject("104")

    def test_duplicate_and_missing_contract_at_104_rows_rejected(self):
        self.edit("map-contract-checklist.md", "| F60 |", "| F59 |")
        self.reject("重複", "F59")

    def test_unknown_contract_at_104_rows_rejected(self):
        self.edit("map-contract-checklist.md", "| F60 |", "| F61 |")
        self.reject("F60")

    def test_edge_must_use_opposite_sides(self):
        self.topology("| E01.right | E02.left | edge |", "| E01.right | E02.right | edge |")
        self.reject("反対辺")

    def test_unknown_edge_side_rejected(self):
        self.topology("| E01.right | E02.left | edge |", "| E01.up | E02.down | edge |")
        self.reject()

    def test_missing_edge_side_rejected(self):
        self.topology("| E01.right | E02.left | edge |", "| E01. | E02.left | edge |")
        self.reject()

    def test_reused_edge_endpoint_rejected(self):
        self.append_connection("| E01.right | E10.left | edge | 同一端の再利用 |")
        self.reject("E01.right")

    def test_unknown_map_endpoint_rejected(self):
        self.topology("| E01.right | E02.left | edge |", "| E99.right | E02.left | edge |")
        self.reject("E99")

    def test_missing_door_identifier_rejected(self):
        self.topology("| E01.door-north | E11.door-kindergarten | door |",
                      "| E01. | E11.door-kindergarten | door |")
        self.reject()

    def test_reused_door_endpoint_rejected(self):
        self.append_connection("| E01.door-north | E10.door-extra | door | 扉端の再利用 |")
        self.reject("E01.door-north")

    def test_unknown_connection_kind_rejected(self):
        self.topology("| E01.right | E02.left | edge |", "| E01.right | E02.left | teleport |")
        self.reject()

    def test_blank_connection_kind_rejected(self):
        self.topology("| E01.right | E02.left | edge |", "| E01.right | E02.left |  |")
        self.reject()

    def test_mountain_shortcut_rejected(self):
        self.append_connection("| N8.door-shortcut | F06.door-shortcut | door | 禁止の登山近道 |")
        self.reject()

    def test_mountain_branch_rejected(self):
        self.append_connection("| F04.door-branch | E10.door-mountain | door | 禁止の登山枝 |")
        self.reject()

    def test_missing_mountain_segment_rejected(self):
        self.remove_connection("| E22.top | F04.bottom |")
        self.reject()

    def test_garden_three_cycles_rejected(self):
        self.remove_connection("| F43.right | F44.left |")
        self.render()
        self.reject("兼六園", "3", "4")

    def test_garden_five_cycles_accepted(self):
        self.append_connection("| F41.door-extra | F44.door-extra | door | 境界検証用の仮接続 |")
        self.render()
        result = self.cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("garden=5", result.stdout)

    def test_castle_two_cycles_rejected(self):
        self.remove_connection("| F53.door-south | F54.door-north |")
        self.render()
        self.reject("金沢城", "2", "3")

    def test_castle_four_cycles_accepted(self):
        self.append_connection("| F54.door-extra | F58.door-extra | door | 境界検証用の仮接続 |")
        self.render()
        result = self.cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("castle=4", result.stdout)

    def test_towers_zero_cycles_rejected(self):
        self.remove_connection("| F33.door-landing | F37.door-left |")
        self.render()
        self.reject("双塔", "0", "1")

    def test_towers_two_cycles_accepted(self):
        self.append_connection("| F32.door-extra | F35.door-extra | door | 境界検証用の仮接続 |")
        self.render()
        result = self.cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("towers=2", result.stdout)

    def test_left_tower_route_cannot_be_replaced_by_cross_link(self):
        self.remove_connection("| F31.door-up | F32.door-down |")
        self.append_connection("| F31.door-cross | F35.door-cross | door | 閉路数だけでは発見できない左塔経路欠落 |")
        self.render()
        self.reject("双塔", "F31", "F32")

    def test_right_tower_route_cannot_be_replaced_by_cross_link(self):
        self.remove_connection("| F34.door-up | F35.door-down |")
        self.append_connection("| F34.door-cross | F32.door-cross | door | 閉路数だけでは発見できない右塔経路欠落 |")
        self.render()
        self.reject("双塔", "F34", "F35")

    def test_sunny_pending_rows_not_playable_connections(self):
        result = self.cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("pending=6", result.stdout)
        self.assertIn("garden=4 castle=3 towers=1", result.stdout)
        self.topology("| F07.door | F08.door | pending |", "| F07.door | F08.door | door |")
        self.reject("サニーランド")

    def test_pending_requires_utf8_reason(self):
        path = self.root / "docs/map-topology.md"
        source = path.read_text()
        row = next(line for line in source.splitlines() if line.startswith("| F07.door | F08.door | pending |"))
        self.topology(row, "| F07.door | F08.door | pending |  |")
        self.reject("保留理由")

    def test_diagram_missing_edge_rejected(self):
        tree = ET.parse(self.diagram())
        parent = next(node for node in tree.iter() if any(child.get("data-from") for child in node))
        parent.remove(next(child for child in parent if child.get("data-from")))
        tree.write(self.diagram(), encoding="utf-8")
        self.reject("接続図", "辺集合")

    def test_diagram_extra_edge_rejected(self):
        tree = ET.parse(self.diagram())
        ET.SubElement(tree.getroot(), "path", {"data-from": "F41", "data-to": "F44", "class": "edge"})
        tree.write(self.diagram(), encoding="utf-8")
        self.reject("接続図", "辺集合")

    def test_diagram_pending_solid_edge_rejected(self):
        tree = ET.parse(self.diagram())
        ET.SubElement(tree.getroot(), "path", {"data-from": "F07", "data-to": "F08", "class": "edge"})
        tree.write(self.diagram(), encoding="utf-8")
        self.reject("接続図", "辺集合")

    def test_diagram_missing_map_rejected(self):
        tree = ET.parse(self.diagram())
        node = next(node for node in tree.iter() if node.get("data-map") == "F41")
        node.attrib.pop("data-map")
        tree.write(self.diagram(), encoding="utf-8")
        self.reject("接続図", "MAP集合")

    def test_diagram_extra_map_rejected(self):
        tree = ET.parse(self.diagram())
        ET.SubElement(tree.getroot(), "circle", {"data-map": "F07"})
        tree.write(self.diagram(), encoding="utf-8")
        self.reject("接続図", "MAP集合")


if __name__ == "__main__":
    unittest.main()
