"""Phase A: body volume and event contracts, independent of full atlas creation."""
import json
import unittest

import test_map_topology as topology_tests


BODY = {f"F{n:02}" for n in range(19, 27)} | {f"F{n:02}" for n in range(74, 83)}
BODY_PAIRS = {
    frozenset(pair) for pair in (
        ("F19", "F74"), ("F74", "F76"), ("F74", "F24"),
        ("F74", "F77"), ("F77", "F20"), ("F74", "F78"), ("F78", "F21"),
        ("F76", "F79"), ("F79", "F80"), ("F80", "F22"),
        ("F76", "F81"), ("F81", "F82"), ("F82", "F23"),
        ("F76", "F25"), ("F74", "F26"), ("F74", "F75"))
}


class BodyTopologyTests(unittest.TestCase):
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

    def test_all_130_maps_have_one_area_membership(self):
        members = [ident for area in self.registry()["areas"] for ident in area["maps"]]
        self.assertEqual(set(members), topology_tests.EXPECTED_IDS)
        self.assertEqual(len(members), len(set(members)))

    def test_body_spokes_declare_two_torso_two_arm_three_leg_maps(self):
        self.assertEqual(self.registry()["body_spokes"], {
            "upper_torso": "F74", "lower_torso": "F76", "head": "F24",
            "left_arm": ["F77", "F20"], "right_arm": ["F78", "F21"],
            "left_leg": ["F79", "F80", "F22"], "right_leg": ["F81", "F82", "F23"],
            "rooms": ["F25", "F26", "F75"]})

    def test_torso_must_be_vertical_with_lower_below_upper(self):
        layout = next(area for area in self.registry()["areas"] if area["id"] == "body")["layout"]
        self.assertEqual(layout["F74"][0], layout["F76"][0])
        self.assertLess(layout["F74"][1], layout["F76"][1])

    def test_head_and_each_limb_chain_have_approved_direction(self):
        layout = next(area for area in self.registry()["areas"] if area["id"] == "body")["layout"]
        self.assertLess(layout["F24"][1], layout["F74"][1])
        for chain, sign_x, sign_y in ((["F74", "F77", "F20"], -1, -1),
                                      (["F74", "F78", "F21"], 1, -1),
                                      (["F76", "F79", "F80", "F22"], -1, 1),
                                      (["F76", "F81", "F82", "F23"], 1, 1)):
            for a, b in zip(chain, chain[1:]):
                self.assertGreater((layout[b][0] - layout[a][0]) * sign_x, 0)
                self.assertGreater((layout[b][1] - layout[a][1]) * sign_y, 0)

    def test_missing_membership_rejected(self):
        self.mutate_registry(lambda data: data["areas"][0]["maps"].pop())
        self.reject()

    def test_duplicate_membership_rejected(self):
        self.mutate_registry(lambda data: data["areas"][1]["maps"].append(data["areas"][0]["maps"][0]))
        self.reject()

    def test_unknown_membership_rejected(self):
        self.mutate_registry(lambda data: data["areas"][0]["maps"].append("F99"))
        self.reject()

    def test_single_torso_spoke_contract_rejected(self):
        self.mutate_registry(lambda data: data["body_spokes"].update(lower_torso="F74"))
        self.reject()

    def test_short_arm_spoke_contract_rejected(self):
        self.mutate_registry(lambda data: data["body_spokes"].update(left_arm=["F20"]))
        self.reject()

    def test_short_leg_spoke_contract_rejected(self):
        self.mutate_registry(lambda data: data["body_spokes"].update(right_leg=["F81", "F23"]))
        self.reject()

    def test_swapped_arm_and_leg_coordinates_rejected(self):
        def mutate(data):
            area = next(a for a in data["areas"] if a["id"] == "body")
            area["layout"]["F20"], area["layout"]["F22"] = area["layout"]["F22"], area["layout"]["F20"]
        self.mutate_registry(mutate)
        self.reject()

    def test_head_below_torso_coordinates_rejected(self):
        def mutate(data):
            area = next(a for a in data["areas"] if a["id"] == "body")
            area["layout"]["F24"][1] = area["layout"]["F74"][1] + 100
        self.mutate_registry(mutate)
        self.reject()

    def test_exact_two_torso_two_arm_three_leg_volume(self):
        pairs = []
        for row in self.connection_rows():
            cells = [cell.strip() for cell in row.split("|")]
            a, b = [endpoint.split(".")[0] for endpoint in cells[1:3]]
            if a in BODY and b in BODY:
                self.assertEqual(cells[3], "door")
                pairs.append(frozenset((a, b)))
        self.assertEqual(set(pairs), BODY_PAIRS)
        self.assertEqual(len(pairs), len(BODY_PAIRS))

    def test_kindergarten_body_event_is_directed_not_walking(self):
        rows = [row for row in self.connection_rows() if "event-kiss" in row]
        self.assertEqual(len(rows), 1)
        cells = [cell.strip() for cell in rows[0].split("|")]
        self.assertEqual(cells[1:4], ["E01.event-kiss", "F19.event-mouth", "event"])

    def test_body_mouth_must_connect_to_upper_torso(self):
        self.remove_pair("F19", "F74")
        self.reject()

    def test_body_lung_must_be_registered_and_connected(self):
        self.remove_pair("F74", "F75")
        self.reject()

    def test_lower_torso_cannot_be_skipped(self):
        self.remove_pair("F74", "F76")
        self.append_connection("| F74.door-passage-shortcut | F79.door-passage-shortcut | door | 下半身を省略 |")
        self.reject()

    def test_arm_cannot_be_shortened_to_one_map(self):
        self.remove_pair("F74", "F77")
        self.remove_pair("F77", "F20")
        self.append_connection("| F74.door-passage-shortcut | F20.door-passage-shortcut | door | 腕1MAPへ短縮 |")
        self.reject()

    def test_leg_cannot_be_shortened_to_two_maps(self):
        self.remove_pair("F79", "F80")
        self.remove_pair("F80", "F22")
        self.append_connection("| F79.door-passage-shortcut | F22.door-passage-shortcut | door | 脚2MAPへ短縮 |")
        self.reject()

    def test_body_cannot_have_extra_arm_to_leg_chain(self):
        self.append_connection("| F20.door-passage-leg | F22.door-passage-arm | door | 手足の鎖を再導入 |")
        self.reject()

    def test_limb_terminal_cannot_lead_to_organ_room(self):
        self.append_connection("| F21.door-passage-stomach | F25.door-passage-arm | door | 腕から胃へ通り抜け |")
        self.reject()

    def test_body_event_cannot_originate_at_hospital(self):
        self.topology("E01.event-kiss", "E20.event-kiss")
        self.reject()

    def test_body_event_cannot_originate_overseas(self):
        self.topology("E01.event-kiss", "F30.event-kiss")
        self.reject()

    def test_body_event_cannot_be_reversed(self):
        row = self.pair_row("E01", "F19")
        cells = row.split("|")
        cells[1], cells[2] = cells[2], cells[1]
        self.topology(row, "|".join(cells))
        self.reject()

    def test_body_event_cannot_be_persistent_walking_door(self):
        row = self.pair_row("E01", "F19")
        changed = row.replace(".event-kiss", ".door-kiss").replace(".event-mouth", ".door-mouth")
        self.topology(row, changed.replace("| event |", "| door |"))
        self.reject()

    def test_body_terminal_arms_and_legs_have_degree_one(self):
        degree = {node: 0 for node in BODY}
        for row in self.connection_rows():
            a, b = [cell.strip().split(".")[0] for cell in row.split("|")[1:3]]
            if a in BODY and b in BODY:
                degree[a] += 1
                degree[b] += 1
        self.assertEqual({node: degree[node] for node in ("F20", "F21", "F22", "F23")},
                         {"F20": 1, "F21": 1, "F22": 1, "F23": 1})


if __name__ == "__main__":
    unittest.main()
