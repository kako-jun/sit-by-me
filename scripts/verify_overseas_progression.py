"""Executable design contract, deliberately separate from the game's runtime."""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ALLOWED_EVENTS = ["defeat_left", "defeat_right", "reveal_and_cooperate", "finish_cooperation", "enter_third", "collect_chest", "descend_5_to_4", "descend_4_to_3", "descend_3_to_2", "descend_2_to_1", "reach_exit", "defeat_s005", "actual_exit", "timeout"]
PHASES = ["exploring", "bridge", "cooperation", "escaping", "exit_battle", "escaped", "failed"]


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def step(contract, state, event):
    matches = [t for t in contract["transitions"]
               if t["event"] == event and t["from"] == state["phase"] and all(state.get(k) == v for k, v in t["requires"].items())]
    if len(matches) > 1:
        raise RuntimeError(f"ambiguous event {event}")
    if not matches:
        return None
    return {**state, **matches[0]["set"], "phase": matches[0]["to"]}


def fail(msg):
    raise RuntimeError(msg)


def verify(c):
    if c.get("kind") != "design-contract-not-game-runtime":
        fail("not a design contract")
    bosses = c.get("bosses") or {}
    if not (bosses.get("left") == {"id": "M015", "map": "OVS-09", "only": "magic"} and bosses.get("right") == {"id": "M016", "map": "OVS-14", "only": "ability"}):
        fail("left magic / right ability required")
    if not (c.get("family_id") == "M003" and c.get("bridge_battle") == "ordinary_enemies_only"):
        fail("third dragon encounter prohibited")
    if c.get("deadline") != "authorities_arrive_and_arrest_shah":
        fail("deadline must be authorities, not explosion")
    if not (c.get("save_during_timer") is False and c.get("third_tower_preentry") is False and c.get("s005_timer_continues") is True and c.get("failure") == "restore_last_pre_timer_save_and_chests"):
        fail("timer/save/reset policy changed")
    if c.get("tower_paths") != {"left": ["OVS-05", "OVS-06", "OVS-07", "OVS-08", "OVS-09"], "right": ["OVS-10", "OVS-11", "OVS-12", "OVS-13", "OVS-14"], "escape": ["OVS-16", "OVS-17", "OVS-18", "OVS-19", "OVS-20"]}:
        fail("five floor paths changed")
    if c.get("floor_area_class") != {i: "comparable_full_floor" for v in c["tower_paths"].values() for i in v}:
        fail("each of 15 floors must be comparable full-floor area")
    initial = c["initial"]
    if initial != {"phase": "exploring", "left_defeated": False, "right_defeated": False, "timer_running": False, "third_unlocked": False, "third_entered": False, "floor": 5, "s005_defeated": False, "exited": False, "four_party": False, "timer_starts": 0, "timer_id": "escape"}:
        fail("invalid initial state")
    if not all(t["event"] in ALLOWED_EVENTS and sorted(t.keys()) == ["event", "from", "requires", "set", "to"] and isinstance(t["requires"], dict) and isinstance(t["set"], dict)
               and not (set(t["requires"]) | set(t["set"])) - set(initial) for t in c["transitions"]):
        fail("unknown event")
    states = [initial]
    seen = set()
    reachable_events = []
    while states:
        state = states.pop(0)
        key = json.dumps(dict(sorted(state.items())), separators=(",", ":"))
        if key in seen:
            continue
        seen.add(key)
        phase = state["phase"]
        if phase not in PHASES:
            fail("invalid phase")
        if phase in ("bridge", "cooperation", "escaping", "exit_battle", "escaped") and not (state["left_defeated"] and state["right_defeated"]):
            fail("early bridge/reunion")
        if state["timer_running"] != (phase in ("escaping", "exit_battle")):
            fail("timer phase mismatch")
        if not (state["timer_id"] == "escape" and state["timer_starts"] == (1 if phase in ("escaping", "exit_battle", "escaped", "failed") else 0)):
            fail("single escape timer must start exactly once")
        if state["third_unlocked"] != (phase in ("escaping", "exit_battle", "escaped", "failed")):
            fail("third tower unlocked before cooperation ends")
        if state["third_entered"] and not state["third_unlocked"]:
            fail("third entered early")
        if phase == "escaped" and not (state["s005_defeated"] and state["exited"] and state["floor"] == 1 and state["third_entered"]):
            fail("S005 exit must finish timer")
        for event in ALLOWED_EVENTS:
            nxt = step(c, state, event)
            if not nxt:
                continue
            m = re.fullmatch(r"descend_(\d)_to_(\d)", event)
            if event in ("defeat_left", "defeat_right"):
                legal = phase == "exploring" and not state[event.replace("defeat_", "", 1) + "_defeated"]
            elif event == "reveal_and_cooperate":
                legal = phase == "bridge"
            elif event == "finish_cooperation":
                legal = phase == "cooperation"
            elif event == "enter_third":
                legal = phase == "escaping" and state["third_unlocked"]
            elif event == "collect_chest":
                legal = phase == "escaping" and state["third_entered"]
            elif m:
                legal = phase == "escaping" and state["third_entered"] and state["floor"] == int(m.group(1)) and int(m.group(2)) == int(m.group(1)) - 1 and nxt["floor"] == int(m.group(2))
            elif event == "reach_exit":
                legal = phase == "escaping" and state["third_entered"] and state["floor"] == 1
            elif event == "defeat_s005":
                legal = phase == "exit_battle" and not state["s005_defeated"] and nxt["s005_defeated"] and nxt["timer_running"]
            elif event == "actual_exit":
                legal = phase == "exit_battle" and state["s005_defeated"] and nxt["exited"]
            elif event == "timeout":
                legal = phase in ("escaping", "exit_battle")
            else:
                legal = False
            if not legal:
                fail(f"illegal event {event} during {phase}")
            reachable_events.append(event)
            states.append(nxt)
        if len(seen) > 200:
            fail("unbounded contract")
    if set(ALLOWED_EVENTS) - set(reachable_events):
        fail("missing reachable event")
    for order in (["defeat_left", "defeat_right"], ["defeat_right", "defeat_left"]):
        state = initial
        route = order + ["reveal_and_cooperate", "finish_cooperation", "enter_third", "collect_chest", "descend_5_to_4", "descend_4_to_3", "descend_3_to_2", "descend_2_to_1", "reach_exit", "defeat_s005", "actual_exit"]
        for event in route:
            state = step(c, state, event)
            if state is None:
                fail(f"blocked required route {event}")
        if state["phase"] != "escaped":
            fail("escape incomplete")
    return True


if __name__ == "__main__":
    try:
        path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "docs/topology/overseas-progression.json")
        verify(load(path))
        print("PASS: overseas design progression, both boss orders, third-tower gate, continuous timer and S005 exit")
    except Exception as e:
        print(f"FAIL: overseas progression: {e}", file=sys.stderr)
        sys.exit(1)
