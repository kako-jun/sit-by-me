"""#191: 石垣（retaining）の上面が屋根色だと瓦屋根の建物に描かれる／マーカーのピンクが画像に残る、の再発防止。"""
from pathlib import Path
import glob
import json
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".claude/skills/sit-field-background/tools"))
import oblique_build as B  # noqa: E402

OUTDOOR_POOL = {"outdoor": True}


class RetainingTop(unittest.TestCase):
    def test_roof_grey_top_is_error(self):
        p = {"walls": [{"id": "r", "kind": "retaining", "look": "石垣", "top_color": "#6c7077"}], "boxes": [], "floors": []}
        errs, _ = B.outdoor_look_problems(p, OUTDOOR_POOL)
        self.assertTrue(any("kind=retaining" in e and "屋根" in e for e in errs))

    def test_snow_top_passes(self):
        p = {"walls": [{"id": "r", "kind": "retaining", "look": "石垣", "top_color": "#e4ded2"}], "boxes": [], "floors": []}
        self.assertEqual([e for e in B.outdoor_look_problems(p, OUTDOOR_POOL)[0] if "retaining" in e], [])

    def test_all_plans_have_no_roof_grey_retaining(self):
        for pp in sorted(glob.glob(str(ROOT / "docs/production/oblique-mocks/*-plan.json"))):
            for w in json.load(open(pp)).get("walls", []):
                if w.get("kind") == "retaining":
                    self.assertNotEqual((w.get("top_color") or "").lower(), "#6c7077", pp)


class PinkGate(unittest.TestCase):
    def test_measure_has_whole_image_pink_gate(self):
        s = (ROOT / ".claude/skills/sit-field-background/tools/oblique_e2_measure.py").read_text()
        self.assertIn('"pink_whole_max"', s)
        self.assertIn('"pink_whole": r["pink_residual_whole_image"]', s)


if __name__ == "__main__":
    unittest.main()
