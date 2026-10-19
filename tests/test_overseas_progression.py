"""Independent tests of the executable DESIGN contract, not a game runtime."""
import copy
import itertools
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = "docs/topology/overseas-progression.json"
SCRIPT = "scripts/verify_overseas_progression.rb"


class OverseasProgressionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in ("docs", "scripts"):
            shutil.copytree(ROOT / name, self.root / name)
        self.path = self.root / CONTRACT
        self.contract = json.loads(self.path.read_text())

    def cli(self):
        return subprocess.run(["ruby", SCRIPT], cwd=self.root,
                              text=True, capture_output=True)

    def reject(self, mutate):
        mutated = copy.deepcopy(self.contract)
        mutate(mutated)
        self.path.write_text(json.dumps(mutated, ensure_ascii=False))
        result = self.cli()
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("FAIL:", result.stderr)

    def run_events(self, events):
        return self.run_routes([events])[0]

    def run_routes(self, routes):
        # Call the production design evaluator. No test-side transition engine.
        code = """
c = OverseasProgression.load(ARGV[0])
traces = JSON.parse(STDIN.read).map do |events|
  state = c.fetch('initial'); trace = []
  events.each do |event|
    before = Marshal.load(Marshal.dump(state))
    candidate = OverseasProgression.step(c, state, event)
    raise 'input mutated' unless before == state
    state = candidate if candidate
    trace << {'event'=>event, 'accepted'=>!candidate.nil?, 'state'=>state}
  end
  trace
end
puts JSON.generate(traces)
"""
        result = subprocess.run(["ruby", "-r", str(self.root / SCRIPT), "-e", code,
                                 str(self.path)], cwd=self.root, input=json.dumps(routes),
                                text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def transition(self, contract, event, phase=None):
        return next(t for t in contract["transitions"] if t["event"] == event
                    and (phase is None or t["from"] == phase))

    def escaping_events(self):
        return ["defeat_left", "defeat_right", "reveal_and_cooperate", "finish_cooperation"]

    def test_valid_design_cli(self):
        result = self.cli()
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_both_boss_orders_unlock_only_after_cooperation(self):
        for order in itertools.permutations(["defeat_left", "defeat_right"]):
            with self.subTest(order=order):
                trace = self.run_events(list(order) + ["reveal_and_cooperate", "finish_cooperation"])
                for item in trace[:3]:
                    self.assertTrue(item["accepted"])
                    self.assertFalse(item["state"]["timer_running"])
                    self.assertFalse(item["state"]["third_unlocked"])
                self.assertEqual(trace[0]["state"]["phase"], "exploring")
                self.assertEqual(trace[1]["state"]["phase"], "bridge")
                self.assertEqual(trace[2]["state"]["phase"], "cooperation")
                self.assertTrue(trace[3]["state"]["timer_running"])
                self.assertTrue(trace[3]["state"]["third_unlocked"])

    def test_both_orders_and_all_five_floor_chest_choices_allow_escape(self):
        routes = []
        for order in itertools.permutations(["defeat_left", "defeat_right"]):
            for choices in itertools.product([False, True], repeat=5):
                events = list(order) + ["reveal_and_cooperate", "finish_cooperation", "enter_third"]
                for floor, collect in zip(range(5, 0, -1), choices):
                    if collect:
                        events.append("collect_chest")
                    if floor > 1:
                        events.append(f"descend_{floor}_to_{floor-1}")
                routes.append(events + ["reach_exit", "defeat_s005", "actual_exit"])
        traces = self.run_routes(routes)
        self.assertEqual(len(traces), 64)
        for trace in traces:
            with self.subTest(events=[item["event"] for item in trace]):
                self.assertTrue(all(item["accepted"] for item in trace))
                self.assertEqual(trace[-1]["state"]["phase"], "escaped")
                self.assertEqual(trace[-1]["state"]["timer_starts"], 1)
                self.assertTrue(all(item["state"]["timer_running"] for item in trace[3:-1]))

    def test_zero_or_one_boss_cannot_reveal_or_enter_or_collect(self):
        for prefix in ([], ["defeat_left"], ["defeat_right"]):
            with self.subTest(prefix=prefix):
                trace = self.run_events(prefix + ["reveal_and_cooperate", "enter_third", "collect_chest"])
                self.assertTrue(all(not item["accepted"] for item in trace[-3:]))
                self.assertFalse(trace[-1]["state"]["timer_running"])
                self.assertFalse(trace[-1]["state"]["third_entered"])

    def test_duplicate_boss_event_not_second_credit(self):
        for boss in ("defeat_left", "defeat_right"):
            trace = self.run_events([boss, boss, "reveal_and_cooperate"])
            self.assertFalse(trace[1]["accepted"])
            self.assertFalse(trace[2]["accepted"])
            self.assertEqual(trace[-1]["state"]["phase"], "exploring")

    def test_third_tower_and_chests_blocked_before_cooperation_ends(self):
        trace = self.run_events(["defeat_left", "defeat_right", "enter_third",
                                 "reveal_and_cooperate", "enter_third", "collect_chest"])
        for index in (2, 4, 5):
            self.assertFalse(trace[index]["accepted"])
        self.assertFalse(trace[-1]["state"]["third_entered"])

    def test_repeat_cooperation_cannot_restart_timer(self):
        trace = self.run_events(self.escaping_events() + ["finish_cooperation"])
        self.assertFalse(trace[-1]["accepted"])
        self.assertEqual(trace[-1]["state"], trace[-2]["state"])

    def test_five_floor_descent_and_optional_chests_keep_timer_running(self):
        events = self.escaping_events() + ["enter_third", "collect_chest"]
        for upper in range(5, 1, -1):
            events.extend([f"descend_{upper}_to_{upper-1}", "collect_chest"])
        events.append("reach_exit")
        trace = self.run_events(events)
        self.assertTrue(all(item["accepted"] for item in trace))
        self.assertTrue(all(item["state"]["timer_running"] for item in trace[3:]))
        self.assertEqual([item["state"]["floor"] for item in trace
                          if item["event"].startswith("descend_")], [4, 3, 2, 1])
        self.assertEqual(trace[-1]["state"]["phase"], "exit_battle")

    def test_s005_defeat_keeps_same_timer_until_actual_exit(self):
        events = self.escaping_events() + ["enter_third"]
        events += [f"descend_{n}_to_{n-1}" for n in range(5, 1, -1)]
        trace = self.run_events(events + ["reach_exit", "defeat_s005", "actual_exit"])
        self.assertTrue(all(item["accepted"] for item in trace))
        won, escaped = trace[-2:]
        self.assertTrue(won["state"]["s005_defeated"])
        self.assertFalse(won["state"]["exited"])
        self.assertTrue(won["state"]["timer_running"])
        self.assertTrue(escaped["state"]["exited"])
        self.assertFalse(escaped["state"]["timer_running"])
        for item in trace[3:]:
            self.assertEqual(item["state"]["timer_id"], "escape")
            self.assertEqual(item["state"]["timer_starts"], 1)

    def test_actual_exit_cannot_bypass_s005(self):
        events = self.escaping_events() + ["enter_third"]
        events += [f"descend_{n}_to_{n-1}" for n in range(5, 1, -1)]
        trace = self.run_events(events + ["reach_exit", "actual_exit"])
        self.assertFalse(trace[-1]["accepted"])
        self.assertTrue(trace[-1]["state"]["timer_running"])

    def test_timeout_after_s005_victory_before_exit_still_fails(self):
        events = self.escaping_events() + ["enter_third"]
        events += [f"descend_{n}_to_{n-1}" for n in range(5, 1, -1)]
        trace = self.run_events(events + ["reach_exit", "defeat_s005", "timeout"])
        self.assertTrue(trace[-1]["accepted"])
        self.assertEqual(trace[-1]["state"]["phase"], "failed")
        self.assertFalse(trace[-1]["state"]["exited"])

    def test_descent_requires_entering_third_tower(self):
        trace = self.run_events(self.escaping_events() + ["descend_5_to_4", "collect_chest", "reach_exit"])
        self.assertTrue(all(not item["accepted"] for item in trace[-3:]))

    def test_descent_cannot_skip_a_floor(self):
        trace = self.run_events(self.escaping_events() + ["enter_third", "descend_3_to_2", "reach_exit"])
        self.assertTrue(all(not item["accepted"] for item in trace[-2:]))

    def test_timeout_from_descent_or_s005_battle(self):
        base = self.escaping_events() + ["enter_third"]
        battle = [f"descend_{n}_to_{n-1}" for n in range(5, 1, -1)] + ["reach_exit"]
        for suffix in ([], battle):
            trace = self.run_events(base + suffix + ["timeout"])
            self.assertTrue(trace[-1]["accepted"])
            self.assertEqual(trace[-1]["state"]["phase"], "failed")
            self.assertFalse(trace[-1]["state"]["exited"])

    def test_second_boss_cannot_start_timer(self):
        self.reject(lambda c: next(t for t in c["transitions"]
                    if t["event"] == "defeat_right" and t["to"] == "bridge")["set"].update(timer_running=True))

    def test_reveal_cannot_start_timer(self):
        self.reject(lambda c: self.transition(c, "reveal_and_cooperate")["set"].update(timer_running=True))

    def test_cooperation_must_start_timer(self):
        self.reject(lambda c: self.transition(c, "finish_cooperation")["set"].update(timer_running=False))

    def test_third_tower_must_not_unlock_early(self):
        self.reject(lambda c: self.transition(c, "reveal_and_cooperate")["set"].update(third_unlocked=True))

    def test_s005_battle_cannot_pause_timer(self):
        self.reject(lambda c: self.transition(c, "reach_exit")["set"].update(timer_running=False))

    def test_s005_victory_cannot_stop_timer(self):
        self.reject(lambda c: self.transition(c, "defeat_s005")["set"].update(timer_running=False))

    def test_s005_battle_cannot_reset_start_count(self):
        self.reject(lambda c: self.transition(c, "reach_exit")["set"].update(timer_starts=2))

    def test_s005_battle_cannot_use_another_clock(self):
        self.reject(lambda c: self.transition(c, "reach_exit")["set"].update(timer_id="new-battle-clock"))

    def test_actual_exit_requires_s005_victory(self):
        self.reject(lambda c: self.transition(c, "actual_exit")["requires"].pop("s005_defeated"))

    def test_early_chest_collection_transition_rejected(self):
        def mutate(c):
            t = copy.deepcopy(self.transition(c, "collect_chest"))
            t.update({"from": "exploring", "to": "exploring", "requires": {}, "set": {}})
            c["transitions"].append(t)
        self.reject(mutate)

    def test_early_third_entry_transition_rejected(self):
        def mutate(c):
            t = copy.deepcopy(self.transition(c, "enter_third"))
            t.update({"from": "exploring", "to": "exploring", "requires": {}, "set": {"third_entered": True}})
            c["transitions"].append(t)
        self.reject(mutate)

    def test_repeated_cooperation_restart_transition_rejected(self):
        def mutate(c):
            t = copy.deepcopy(self.transition(c, "finish_cooperation"))
            t.update({"from": "escaping", "requires": {"timer_running": True}})
            c["transitions"].append(t)
        self.reject(mutate)

    def test_ambiguous_duplicate_transition_rejected(self):
        self.reject(lambda c: c["transitions"].append(copy.deepcopy(c["transitions"][0])))

    def test_prison_key_is_not_a_progression_requirement(self):
        self.reject(lambda c: self.transition(c, "finish_cooperation")["requires"].update(prison_key=True))

    def test_defeat_all_enemies_is_not_an_escape_requirement(self):
        self.reject(lambda c: self.transition(c, "enter_third")["requires"].update(all_enemies_defeated=True))

    def test_explosion_deadline_rejected(self):
        self.reject(lambda c: c.update(deadline="building_explodes"))

    def test_bridge_third_dragon_boss_rejected(self):
        self.reject(lambda c: c.update(bridge_battle="M003_dragon"))

    def test_wrong_left_attack_type_rejected(self):
        self.reject(lambda c: c["bosses"]["left"].update(only="physical"))

    def test_right_boss_not_on_fifth_floor_rejected(self):
        self.reject(lambda c: c["bosses"]["right"].update(map="OVS-13"))

    def test_four_floors_rejected(self):
        self.reject(lambda c: c["tower_paths"]["escape"].pop())

    def test_six_floors_rejected(self):
        self.reject(lambda c: c["tower_paths"]["escape"].append("OVS-04"))

    def test_duplicate_floor_rejected(self):
        self.reject(lambda c: c["tower_paths"]["left"].__setitem__(1, "OVS-05"))

    def test_third_tower_cannot_be_reduced_to_narrow_shaft(self):
        self.reject(lambda c: c["floor_area_class"].update({"OVS-18": "narrow_stair_shaft"}))

    def test_all_fifteen_floors_have_comparable_area_contract(self):
        expected = {"OVS-05", "OVS-06", "OVS-07", "OVS-08", "OVS-09", "OVS-10", "OVS-11", "OVS-12",
                    "OVS-13", "OVS-14", "OVS-16", "OVS-17", "OVS-18", "OVS-19", "OVS-20"}
        self.assertEqual(set(self.contract["floor_area_class"]), expected)
        self.assertEqual(set(self.contract["floor_area_class"].values()), {"comparable_full_floor"})

    def test_missing_transition_conditions_rejected(self):
        self.reject(lambda c: self.transition(c, "enter_third").pop("requires"))

    def test_save_during_timer_rejected(self):
        self.reject(lambda c: c.update(save_during_timer=True))

    def test_failure_must_restore_pre_timer_save_and_chests(self):
        self.reject(lambda c: c.update(failure="keep_chests_and_restart_here"))


if __name__ == "__main__":
    unittest.main()
