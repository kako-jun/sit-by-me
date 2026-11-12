"""#191: 石垣（retaining）の上面が屋根色だと瓦屋根の建物に描かれる／マーカーのピンクが画像に残る、の再発防止。"""
from pathlib import Path
import glob
import json
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".claude/skills/sit-field-background/tools"))
import oblique_build as B  # noqa: E402
import oblique_e2_measure as EM  # noqa: E402
import oblique_mock as M  # noqa: E402

OUTDOOR_POOL = {"outdoor": True}


def retaining_plan(top):
    w = {"id": "r", "kind": "retaining", "look": "石垣"}
    if top is not None:
        w["top_color"] = top
    return {"walls": [w], "boxes": [], "floors": []}


class RetainingTop(unittest.TestCase):
    def test_roof_grey_top_is_error_in_any_notation(self):
        for top in ("#6c7077", "#6C7077", " #6c7077 "):
            errs, _ = B.outdoor_look_problems(retaining_plan(top), OUTDOOR_POOL)
            self.assertTrue(any("kind=retaining" in e and "屋根" in e for e in errs), top)

    def test_norm_hex_expands_short_form(self):
        self.assertEqual(B._norm_hex("#ABC"), "#aabbcc")
        self.assertEqual(B._norm_hex("#6C7077"), "#6c7077")
        self.assertEqual(B._norm_hex(None), "")

    def test_snow_top_passes(self):
        errs, _ = B.outdoor_look_problems(retaining_plan("#e4ded2"), OUTDOOR_POOL)
        self.assertEqual([e for e in errs if "retaining" in e], [])

    def test_all_plans_have_no_roof_grey_retaining(self):
        for pp in sorted(glob.glob(str(ROOT / "docs/production/oblique-mocks/*-plan.json"))):
            for w in json.load(open(pp)).get("walls", []):
                if w.get("kind") == "retaining":
                    self.assertNotEqual(B._norm_hex(w.get("top_color")), "#6c7077", pp)

    def test_mock_default_top_of_retaining_is_snow_band(self):
        p = M.load_plan(str(ROOT / "docs/production/oblique-mocks/TRM-13-plan.json"))
        for w in p["walls"]:
            if w.get("kind") == "retaining":
                w.pop("top_color", None)
        tops = [polys for _k, tag, polys, meta in M.build_items(p, "color") if tag == "wall" and meta.get("kind") == "retaining"]
        self.assertTrue(tops)
        for polys in tops:
            self.assertEqual([c for _pts, c, part in polys if part == "top"], ["#e4ded2"])


class PinkGate(unittest.TestCase):
    def test_pink_whole_gate_value_and_wiring(self):
        self.assertLessEqual(EM.GATES["pink_whole_max"], 0.0001)
        s = (ROOT / ".claude/skills/sit-field-background/tools/oblique_e2_measure.py").read_text()
        self.assertIn('"pink_whole": r["pink_residual_whole_image"] <= GATES["pink_whole_max"]', s)


if __name__ == "__main__":
    unittest.main()
