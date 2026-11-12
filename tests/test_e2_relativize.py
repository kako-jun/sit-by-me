"""e2 の測定・ログから、この PC の絶対パス（worktree 名・ホーム）を消す（git に入れない）。"""
from pathlib import Path
import os
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".claude/skills/sit-field-background/tools"))
import oblique_e2_measure as EM  # noqa: E402


class Relativize(unittest.TestCase):
    def test_repo_and_home_paths_are_removed(self):
        root = "/home/someone/repos/x-r07"
        home = os.path.expanduser("~")
        t = f'"{root}/docs/a/take1.png" "{home}/.codex/generated_images/y.png" workdir: {root}'
        r = EM.relativize(t, root)
        self.assertIn('"docs/a/take1.png"', r)
        self.assertIn("~/.codex/generated_images/y.png", r)
        self.assertNotIn("x-r07/", r)

    def test_tracked_e2_outputs_have_no_absolute_home_path(self):
        import subprocess
        files = subprocess.run(["git", "ls-files", "docs/production/oblique-mocks"], cwd=ROOT, capture_output=True, text=True).stdout.split()
        bad = [f for f in files if (f.endswith("metrics.json") or f.endswith("metrics.md") or f.endswith("codex-take1.log.txt")) and "/home/" in (ROOT / f).read_text()]
        self.assertEqual(bad, [])


if __name__ == "__main__":
    unittest.main()
