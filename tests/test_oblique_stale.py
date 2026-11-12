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
            self.assertEqual(S.stale_maps(maps), ["TRM-X"])  # 既知の例外 variant は数えない
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
