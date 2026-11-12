"""台帳の文面・plan を変えた後に派生物（<MAP>-edit-prompt.txt）が古いままなのを検出する（oblique_e2_schedule.py stale）。"""
import pathlib
import sys
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".claude/skills/sit-field-background/tools"))
import oblique_e2_schedule as S  # noqa: E402


class Stale(unittest.TestCase):
    def test_stale_map_is_detected_and_exits_1(self):
        maps = {"TRM-X": {"depends_on": []}, "TRM-05-kids": {"depends_on": []}}
        with mock.patch.object(S, "has_plan", return_value=True), \
                mock.patch.object(S, "blockers", return_value=["プロンプトが古い（入力 hash が今の plan・台帳・ツールと合わない。oblique_build.py を再実行）"]):
            self.assertEqual(S.stale_maps(maps), ["TRM-X", "TRM-05-kids"])  # 例外なし（variant も数える）
            with self.assertRaises(SystemExit) as cm:
                S.cmd_stale(maps)
            self.assertEqual(cm.exception.code, 1)

    def test_fresh_maps_exit_0(self):
        maps = {"TRM-X": {"depends_on": []}}
        with mock.patch.object(S, "has_plan", return_value=True), mock.patch.object(S, "blockers", return_value=[]):
            with self.assertRaises(SystemExit) as cm:
                S.cmd_stale(maps)
            self.assertEqual(cm.exception.code, 0)

    def test_repo_has_no_stale_prompt(self):
        self.assertEqual(S.stale_maps(S.load()), [], "台帳を変えたら oblique_build.py --all を実行する")


if __name__ == "__main__":
    unittest.main()


class VariantFreshness(unittest.TestCase):
    """variant（TRM-05-kids・fire）の古さ判定が build と同じ入力 hash になる（依存は plan から導く。依存グラフ JSON は variant の追加依存を持たない）。"""

    def test_plan_depends_on_matches_load_plan(self):
        import glob
        import json
        import oblique_freshness as FR
        import oblique_mock as M
        for pp in sorted(glob.glob(str(ROOT / "docs/production/oblique-mocks/*-plan.json"))):
            variants = [None] + list(json.load(open(pp)).get("variants", {}))
            for v in variants:
                self.assertEqual(FR.plan_depends_on(pp, v), M.load_plan(pp, v).get("depends_on", []), f"{pp} {v}")

    def test_variant_prompt_is_not_stale(self):
        maps = S.load()
        for mid in ("TRM-05-kids", "TRM-05-fire"):
            self.assertFalse(any("プロンプトが古い" in b for b in S.blockers(maps, mid)), mid)

    def test_no_known_stale_exception_left(self):
        self.assertFalse(hasattr(S, "KNOWN_STALE"))


class BuildAllTarget(unittest.TestCase):
    def test_town_config_with_virtual_ports_is_rejected_with_message(self):
        import subprocess
        r = subprocess.run([sys.executable, str(ROOT / ".claude/skills/sit-field-background/tools/oblique_build.py"), "--all",
                            str(ROOT / "docs/production/oblique-mocks/connections-teramachi.json")], capture_output=True, text=True, timeout=120)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("virtual_ports", r.stderr)
        self.assertIn("oblique_town.py", r.stderr)
        self.assertNotIn("KeyError", r.stderr)
