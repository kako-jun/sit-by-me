"""#191: 屋外MAPの建物・塀・門の look 空欄ゲート（現実参照・境界の実体化。決定 SIT.real-reference-boundaries）。

実行: uv run --with pytest --with numpy --with opencv-python-headless --with pillow python3 -m pytest tests/test_oblique_outdoor_look_gate.py
"""
import glob
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".claude/skills/sit-field-background/tools"))
import oblique_build as B  # noqa: E402
import oblique_mock as M  # noqa: E402
import oblique_text as X  # noqa: E402

PLANS = sorted(glob.glob(str(ROOT / "docs/production/oblique-mocks/*-plan.json")))
OUTDOOR_POOL = {"outdoor": True}


def plan(walls=(), boxes=(), floors=()):
    return {"walls": list(walls), "boxes": list(boxes), "floors": list(floors)}


class OutdoorLookGate(unittest.TestCase):
    def test_empty_building_and_fence_look_is_error(self):
        p = plan(walls=[{"id": "house", "kind": "building", "look": ""}, {"id": "fence", "kind": "fence"}])
        errs, _ = B.outdoor_look_problems(p, OUTDOOR_POOL)
        self.assertEqual(len(errs), 2)

    def test_empty_gate_box_is_error_but_other_kind_is_not(self):
        p = plan(boxes=[{"id": "gate", "kind": "gate"}, {"id": "bell", "kind": "bell"}])
        errs, _ = B.outdoor_look_problems(p, OUTDOOR_POOL)
        self.assertEqual(len(errs), 1)
        self.assertIn("gate", errs[0])

    def test_filled_look_passes(self):
        p = plan(walls=[{"id": "w", "kind": "fence", "look": "古い土塀。瓦屋根つきで雪が載る"}])
        self.assertEqual(B.outdoor_look_problems(p, OUTDOOR_POOL), ([], []))

    def test_blocked_floor_plain_ground_warns(self):
        for look in ("", "雪に覆われた地面（歩けない部分）"):
            _, w = B.outdoor_look_problems(plan(floors=[{"id": "snow", "walkable": False, "look": look}]), OUTDOOR_POOL)
            self.assertEqual(len(w), 1, look)

    def test_blocked_floor_without_visual_reason_warns_and_with_reason_does_not(self):
        _, w = B.outdoor_look_problems(plan(floors=[{"id": "s", "walkable": False, "look": "なだらかな雪の庭"}]), OUTDOOR_POOL)
        self.assertEqual(len(w), 1)
        _, w = B.outdoor_look_problems(plan(floors=[{"id": "s", "walkable": False, "look": "一段高い庭。縁に低い石垣がある"}]), OUTDOOR_POOL)
        self.assertEqual(w, [])

    def test_validate_decor_applies_only_to_outdoor_pools(self):
        p = {"decor_pool": "teramachi-winter-exterior", "boxes": [], "walls": [{"id": "w", "kind": "building"}], "floors": []}
        E, W = [], []
        B.validate_decor(p, E, W)
        self.assertTrue(any("look が空欄" in e for e in E))
        p["decor_pool"] = "teramachi-winter"  # 屋内プールは対象外
        E, W = [], []
        B.validate_decor(p, E, W)
        self.assertFalse(any("look が空欄" in e for e in E))

    def test_approved_maps_are_not_gated(self):
        # 承認済み・採用済みの TRM-02〜05（屋内・外観 TRM-03）は新ゲートで落ちない
        for path in PLANS:
            pid = Path(path).name.split("-plan")[0]
            if pid not in ("TRM-02", "TRM-03", "TRM-04", "TRM-05", "TRM-12"):
                continue
            p = M.load_plan(path)
            pool = B.load_decor(p)
            errs = B.outdoor_look_problems(p, pool)[0] if pool and pool.get("outdoor") else []
            self.assertEqual(errs, [], pid)

    def test_unfilled_outdoor_maps_are_gated(self):
        # TRM-06〜17 のうち屋外は look 未記入のため止まる（調査結果を台帳に反映するまで意図どおり）
        gated = []
        for path in PLANS:
            p = M.load_plan(path)
            pool = B.load_decor(p)
            if pool and pool.get("outdoor") and B.outdoor_look_problems(p, pool)[0]:
                gated.append(p["map_id"])
        self.assertIn("TRM-08", gated)

    def test_reality_prompt_text_in_ledger(self):
        t = X.text("PR.reality")
        for w in ("位置の指定にすぎない", "色の違いだけ", "歩けなさそう", "古木"):
            self.assertIn(w, t)


if __name__ == "__main__":
    unittest.main()
