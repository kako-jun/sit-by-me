"""Independent full-atlas checks and real CLI mutation fixtures for Issue 74."""
import hashlib
import json
import subprocess
import unittest
import xml.etree.ElementTree as ET

import test_map_topology as topology_tests


class MapAtlasTests(unittest.TestCase):
    setUp = topology_tests.MapTopologyTests.setUp
    cli = topology_tests.MapTopologyTests.cli
    reject = topology_tests.MapTopologyTests.reject
    edit = topology_tests.MapTopologyTests.edit
    topology = topology_tests.MapTopologyTests.topology
    append_connection = topology_tests.MapTopologyTests.append_connection
    connection_rows = topology_tests.MapTopologyTests.connection_rows
    pair_row = topology_tests.MapTopologyTests.pair_row
    remove_connection = topology_tests.MapTopologyTests.remove_connection
    remove_pair = topology_tests.MapTopologyTests.remove_pair

    def registry(self):
        return json.loads((self.root / "docs/topology/areas.json").read_text())

    def mutate_registry(self, mutate):
        path = self.root / "docs/topology/areas.json"
        data = json.loads(path.read_text())
        mutate(data)
        path.write_text(json.dumps(data, ensure_ascii=False))

    def render(self):
        result = subprocess.run(["ruby", "scripts/render_map_atlas.rb"], cwd=self.root,
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def diagram(self, filename="atlas.svg"):
        return self.root / "docs/topology" / filename

    def mutate_svg(self, filename, mutate):
        path = self.diagram(filename)
        tree = ET.parse(path)
        mutate(tree)
        tree.write(path, encoding="utf-8")

    def edge_elements(self, tree):
        return [node for node in tree.iter() if node.get("data-edge-id")]

    def canonical_edges(self):
        edges = []
        for row in self.connection_rows():
            cells = [cell.strip() for cell in row.split("|")]
            source, target, kind = cells[1:4]
            if kind != "pending":
                edges.append((f"{source}>{target}:{kind}", source, target, kind))
        return edges

    def area_owners(self):
        return {ident: area["id"] for area in self.registry()["areas"] for ident in area["maps"]}

    def edge_ids(self, tree):
        return [node.get("data-edge-id") for node in self.edge_elements(tree)]

    def test_atlas_all_canonical_edges_preserve_kind_and_both_ports(self):
        tree = ET.parse(self.diagram())
        actual = {node.get("data-edge-id"): node for node in self.edge_elements(tree)}
        expected = self.canonical_edges()
        self.assertEqual(sorted(self.edge_ids(tree)), sorted(edge[0] for edge in expected))
        for edge_id, source, target, kind in expected:
            with self.subTest(edge=edge_id):
                node = actual[edge_id]
                source_map, source_port = source.split(".", 1)
                target_map, target_port = target.split(".", 1)
                self.assertEqual(node.get("data-from"), source_map)
                self.assertEqual(node.get("data-to"), target_map)
                self.assertEqual(node.get("data-from-port"), source_port)
                self.assertEqual(node.get("data-to-port"), target_port)
                self.assertEqual(node.get("data-kind"), kind)

    def test_overview_has_exactly_all_cross_area_edges(self):
        owners = self.area_owners()
        expected = [edge_id for edge_id, source, target, _ in self.canonical_edges()
                    if owners[source.split(".")[0]] != owners[target.split(".")[0]]]
        tree = ET.parse(self.diagram("overview.svg"))
        self.assertEqual(sorted(self.edge_ids(tree)), sorted(expected))
        actual_areas = [node.get("data-area") for node in tree.iter() if node.get("data-area")]
        self.assertEqual(sorted(actual_areas), sorted(area["id"] for area in self.registry()["areas"]))
        visible = {"".join(node.itertext()) for node in tree.iter()
                   if node.tag.rsplit("}", 1)[-1] == "text"}
        for area in self.registry()["areas"]:
            self.assertIn(area["name"], visible)

    def test_area_views_owned_union_and_cross_references_are_exact(self):
        owners = self.area_owners()
        all_owned = []
        for area in self.registry()["areas"]:
            with self.subTest(area=area["id"]):
                tree = ET.parse(self.diagram(f"areas/{area['id']}.svg"))
                owned = [node.get("data-map") for node in tree.iter() if node.get("data-map")]
                self.assertEqual(sorted(owned), sorted(area["maps"]))
                labels = ["".join(node.itertext()).strip() for node in tree.iter()
                          if node.tag.rsplit("}", 1)[-1] == "text" and node.get("class") == "id"]
                self.assertEqual(sorted(labels), sorted(area["maps"]))
                all_owned.extend(owned)
                expected_edges, remote = [], set()
                for edge_id, source, target, _ in self.canonical_edges():
                    a, b = source.split(".")[0], target.split(".")[0]
                    if area["id"] in (owners[a], owners[b]):
                        expected_edges.append(edge_id)
                        remote.update(node for node in (a, b) if owners[node] != area["id"])
                self.assertEqual(sorted(self.edge_ids(tree)), sorted(expected_edges))
                references = [node.get("data-reference-map") for node in tree.iter() if node.get("data-reference-map")]
                self.assertEqual(sorted(references), sorted(remote))
        self.assertEqual(sorted(all_owned), sorted(topology_tests.EXPECTED_IDS))

    def test_all_registered_maps_have_exactly_one_area(self):
        areas = self.registry()["areas"]
        members = [ident for area in areas for ident in area["maps"]]
        self.assertEqual(set(members), topology_tests.EXPECTED_IDS)
        self.assertEqual(len(members), len(set(members)))
        self.assertEqual(len({area["id"] for area in areas}), len(areas))

    def test_missing_area_membership_rejected(self):
        self.mutate_registry(lambda data: data["areas"][0]["maps"].pop())
        self.reject()

    def test_duplicate_area_membership_rejected(self):
        self.mutate_registry(lambda data: data["areas"][1]["maps"].append(data["areas"][0]["maps"][0]))
        self.reject()

    def test_unknown_area_member_rejected(self):
        self.mutate_registry(lambda data: data["areas"][0]["maps"].append("KRB-99"))
        self.reject()

    def test_duplicate_area_identifier_rejected(self):
        self.mutate_registry(lambda data: data["areas"][1].update(id=data["areas"][0]["id"]))
        self.reject()

    def test_atlas_has_all_registered_distinct_owned_visible_nodes(self):
        tree = ET.parse(self.diagram())
        owned = [node.get("data-map") for node in tree.iter() if node.get("data-map")]
        self.assertEqual(set(owned), topology_tests.EXPECTED_IDS)
        self.assertEqual(len(owned), len(topology_tests.EXPECTED_IDS))
        labels = ["".join(node.itertext()).strip() for node in tree.iter()
                  if node.tag.rsplit("}", 1)[-1] == "text" and node.get("class") == "id"]
        self.assertEqual(sorted(labels), sorted(topology_tests.EXPECTED_IDS))

    def test_atlas_missing_node_rejected(self):
        self.mutate_svg("atlas.svg", lambda tree: next(n for n in tree.iter()
                        if n.get("data-map") == "BDY-02").attrib.pop("data-map"))
        self.reject()

    def test_atlas_blank_visible_id_cannot_hide_behind_metadata(self):
        def mutate(tree):
            node = next(n for n in tree.iter() if n.get("class") == "id" and n.text == "BDY-02")
            node.text = ""
        self.mutate_svg("atlas.svg", mutate)
        self.reject()

    def test_directed_event_and_flight_have_visible_arrowheads(self):
        tree = ET.parse(self.diagram())
        directed = [node for node in self.edge_elements(tree) if node.get("data-kind") in {"event", "oneway"}]
        self.assertEqual(len(directed), 2)
        for node in directed:
            self.assertIn("url(#", node.get("marker-end", ""))
            self.assertIsNone(node.get("marker-start"))

    def test_body_event_arrow_cannot_be_removed(self):
        def mutate(tree):
            node = next(n for n in self.edge_elements(tree) if n.get("data-kind") == "event")
            node.attrib.pop("marker-end")
        self.mutate_svg("atlas.svg", mutate)
        self.reject()

    def test_oneway_flight_arrow_cannot_be_reversed(self):
        def mutate(tree):
            node = next(n for n in self.edge_elements(tree) if n.get("data-kind") == "oneway")
            node.set("marker-start", node.attrib.pop("marker-end"))
        self.mutate_svg("atlas.svg", mutate)
        self.reject()

    def test_atlas_duplicate_owned_node_rejected(self):
        self.mutate_svg("atlas.svg", lambda tree: ET.SubElement(tree.getroot(), "circle", {"data-map": "BDY-02"}))
        self.reject()

    def test_atlas_missing_edge_rejected(self):
        def mutate(tree):
            node = self.edge_elements(tree)[0]
            next(parent for parent in tree.iter() if node in list(parent)).remove(node)
        self.mutate_svg("atlas.svg", mutate)
        self.reject()

    def test_atlas_edge_remote_port_corruption_rejected(self):
        self.mutate_svg("atlas.svg", lambda tree: self.edge_elements(tree)[0].set("data-to-port", "door-invented"))
        self.reject()

    def test_atlas_edge_kind_corruption_rejected(self):
        self.mutate_svg("atlas.svg", lambda tree: self.edge_elements(tree)[0].set("data-kind", "teleport"))
        self.reject()

    def test_parallel_otter_doors_keep_distinct_edge_ids(self):
        tree = ET.parse(self.diagram())
        edges = [node for node in self.edge_elements(tree)
                 if {node.get("data-from"), node.get("data-to")} == {"SNL-06", "SNL-07"}]
        self.assertEqual(len(edges), 2)
        self.assertEqual(len({node.get("data-edge-id") for node in edges}), 2)

    def test_parallel_otter_door_cannot_be_merged(self):
        def mutate(tree):
            node = next(node for node in self.edge_elements(tree)
                        if {node.get("data-from"), node.get("data-to")} == {"SNL-06", "SNL-07"})
            next(parent for parent in tree.iter() if node in list(parent)).remove(node)
        self.mutate_svg("atlas.svg", mutate)
        self.reject()

    def test_overview_missing_cross_area_edge_rejected(self):
        def mutate(tree):
            node = self.edge_elements(tree)[0]
            next(parent for parent in tree.iter() if node in list(parent)).remove(node)
        self.mutate_svg("overview.svg", mutate)
        self.reject()

    def test_area_owned_map_cannot_be_dropped(self):
        def mutate(tree):
            next(n for n in tree.iter() if n.get("data-map") == "BDY-02").attrib.pop("data-map")
        self.mutate_svg("areas/body.svg", mutate)
        self.reject()

    def test_area_incident_cross_connection_cannot_be_dropped(self):
        def mutate(tree):
            node = next(n for n in self.edge_elements(tree) if n.get("data-kind") == "event")
            next(parent for parent in tree.iter() if node in list(parent)).remove(node)
        self.mutate_svg("areas/body.svg", mutate)
        self.reject()

    def test_area_remote_reference_cannot_point_to_hospital(self):
        def mutate(tree):
            node = next(n for n in tree.iter() if n.get("data-reference-map") == "TRM-03")
            node.set("data-reference-map", "KRB-13")
        self.mutate_svg("areas/body.svg", mutate)
        self.reject()

    def test_body_entry_must_start_at_kindergarten_even_after_render(self):
        self.topology("TRM-03.event-kiss", "KRB-13.event-kiss")
        self.render()
        self.reject()

    def test_body_entry_must_not_start_overseas_even_after_render(self):
        self.topology("TRM-03.event-kiss", "OVS-04.event-kiss")
        self.render()
        self.reject()

    def test_body_event_must_not_be_walking_door_even_after_render(self):
        row = self.pair_row("TRM-03", "BDY-01")
        self.topology(row, row.replace(".event-kiss", ".door-kiss")
                      .replace(".event-mouth", ".door-mouth").replace("| event |", "| door |"))
        self.render()
        self.reject()

    def test_body_event_reversal_rejected_even_after_render(self):
        row = self.pair_row("TRM-03", "BDY-01")
        cells = row.split("|")
        cells[1], cells[2] = cells[2], cells[1]
        self.topology(row, "|".join(cells))
        self.render()
        self.reject()

    def test_old_hand_to_leg_chain_rejected_even_after_render(self):
        self.remove_pair("BDY-10", "BDY-11")
        self.append_connection("| BDY-06.door-passage-leg | BDY-11.door-passage-hand | door | 旧手足の鎖を再導入 |")
        self.render()
        self.reject()

    def test_nonterminal_limb_rejected_even_after_render(self):
        self.append_connection("| BDY-06.door-passage-extra | BDY-15.door-passage-extra | door | 腕から胃へ通り抜け |")
        self.render()
        self.reject()

    def test_body_missing_lung_rejected_even_after_render(self):
        self.remove_pair("BDY-02", "BDY-17")
        self.render()
        self.reject()

    def test_body_head_below_torso_rejected_even_after_render(self):
        def mutate(data):
            area = next(a for a in data["areas"] if "BDY-02" in a["maps"])
            area["layout"]["BDY-04"][1] = area["layout"]["BDY-02"][1] + 100
        self.mutate_registry(mutate)
        self.render()
        self.reject()

    def test_body_swapped_arm_leg_coordinates_rejected_even_after_render(self):
        def mutate(data):
            area = next(a for a in data["areas"] if "BDY-02" in a["maps"])
            area["layout"]["BDY-06"], area["layout"]["BDY-11"] = area["layout"]["BDY-11"], area["layout"]["BDY-06"]
        self.mutate_registry(mutate)
        self.render()
        self.reject()

    def test_atlas_renderer_is_deterministic_and_does_not_change_sources(self):
        sources = [self.root / "docs/map-topology.md", self.root / "docs/topology/areas.json"]
        before = {path: hashlib.sha256(path.read_bytes()).digest() for path in sources}
        self.render()
        outputs = [self.diagram(), self.diagram("overview.svg")]
        outputs += sorted((self.root / "docs/topology/areas").glob("*.svg"))
        first = {path: path.read_bytes() for path in outputs}
        self.render()
        self.assertEqual(first, {path: path.read_bytes() for path in outputs})
        self.assertEqual(before, {path: hashlib.sha256(path.read_bytes()).digest() for path in sources})


if __name__ == "__main__":
    unittest.main()
