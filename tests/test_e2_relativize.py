"""e2 の測定・ログから、この PC の絶対パス（worktree 名・ホーム）を消す（git に入れない）。"""
from pathlib import Path
import os
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / ".claude/skills/sit-field-background/tools"
sys.path.insert(0, str(TOOLS))
import oblique_e2_measure as EM  # noqa: E402

SRC = (TOOLS / "oblique_e2_measure.py").read_text()
RUN = (TOOLS / "oblique_e2_run.sh").read_text()


class Relativize(unittest.TestCase):
    def test_repo_and_home_paths_are_removed(self):
        root = "/home/someone/repos/x-r07"
        home = os.path.expanduser("~")
        t = f'"{root}/docs/a/take1.png" "{home}/.codex/generated_images/y.png" workdir: {root}'
        r = EM.relativize(t, root)
        self.assertIn('"docs/a/take1.png"', r)
        self.assertIn("~/.codex/generated_images/y.png", r)
        self.assertTrue(r.endswith("workdir: ."), r)  # 末尾スラッシュなしの root も消える
        self.assertNotIn("x-r07", r)

    def test_tilde_form_of_root_is_removed(self):
        home = os.path.expanduser("~")
        root = home + "/repos/private/x-r07"
        r = EM.relativize("workdir: ~/repos/private/x-r07\n~/repos/private/x-r07/docs/a.png", root)
        self.assertEqual(r, "workdir: .\ndocs/a.png")

    def test_prefix_only_paths_are_not_replaced(self):
        root = "/home/someone/repos/x-r07"
        home = os.path.expanduser("~")
        t = f"{root}2/a {home}2/b {root}-old/c"
        self.assertEqual(EM.relativize(t, root), t)

    def test_write_paths_and_run_sh_use_relativize(self):
        self.assertIn('(out / "metrics.json").write_text(relativize(json.dumps(summary', SRC)
        self.assertIn('(out / "metrics.md").write_text(relativize("\\n".join(L)', SRC)
        self.assertIn("--relativize-files", RUN)
        self.assertNotIn('sed -i "s|', RUN)

    def test_relativize_files_cli(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "log.txt"
            f.write_text(f"workdir: {ROOT}\n{ROOT}/docs/x.png\n")
            subprocess.run(["uv", "run", "--with", "numpy", "--with", "opencv-python-headless", "--with", "pillow", "python3", str(TOOLS / "oblique_e2_measure.py"), "--relativize-files", str(f)],
                           cwd=ROOT, check=True, capture_output=True, timeout=120)
            self.assertEqual(f.read_text(), "workdir: .\ndocs/x.png\n")

    def test_tracked_e2_outputs_have_no_absolute_path(self):
        files = subprocess.run(["git", "ls-files", "docs/production/oblique-mocks"], cwd=ROOT, capture_output=True, text=True).stdout.split()
        bad = []
        for f in files:
            if f.endswith(("metrics.json", "metrics.md", "codex-take1.log.txt")):
                t = (ROOT / f).read_text()
                if str(ROOT) in t or "/home/" in t:
                    bad.append(f)
        self.assertEqual(bad, [])


if __name__ == "__main__":
    unittest.main()
