"""生成直後の寸法検査（1672×941でない画像は採用手順に進めない。TRM-06・10 が 1671×941 で採用手順の寸法検査に落ちた件、#191）。"""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".claude/skills/sit-field-background/tools"))
import oblique_e2_measure as EM  # noqa: E402


class SizeGate(unittest.TestCase):
    def test_wrong_size_take_is_reported(self):
        res = [{"take": "1", "orig_size": [1671, 941]}, {"take": "2", "orig_size": [1672, 941]}]
        bad = EM.size_problems(res, (1672, 941))
        self.assertEqual(len(bad), 1)
        self.assertIn("take1", bad[0])
        self.assertIn("1671x941", bad[0])

    def test_exact_size_has_no_problem(self):
        self.assertEqual(EM.size_problems([{"take": "1", "orig_size": [1672, 941]}], (1672, 941)), [])

    def test_gate_and_message_are_wired(self):
        s = (ROOT / ".claude/skills/sit-field-background/tools/oblique_e2_measure.py").read_text()
        self.assertIn('"size_exact": not r["resized_for_measure"]', s)
        self.assertIn("再生成が必要", s)
        self.assertIn("bad = size_problems(res, size)", s)  # 呼び出し行（def には一致させない）
        self.assertIn("sys.exit(3)", s)  # 寸法NGは終了コード3
        run = (ROOT / ".claude/skills/sit-field-background/tools/oblique_e2_run.sh").read_text()
        self.assertIn("MRC=$?", run)
        self.assertLess(run.index('if [ "$MRC" -ne 0 ]'), run.index("== 全テイク"))  # 寸法NGでは『全テイク』表示に進まない


if __name__ == "__main__":
    unittest.main()
