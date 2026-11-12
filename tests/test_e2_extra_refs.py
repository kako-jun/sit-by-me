"""oblique_e2_run.sh の EXTRA_REFS（隣接MAPの継ぎ目参考）が、スキルの正規手順としてスクリプト・SKILL.md・README に揃っているかの検査。"""
import os
import pathlib
import re
import subprocess
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SK = ROOT / ".claude/skills/sit-field-background"
RUN = SK / "tools/oblique_e2_run.sh"


class ExtraRefs(unittest.TestCase):
    def test_script_handles_extra_refs_and_webp(self):
        s = RUN.read_text()
        self.assertIn("EXTRA_REFS", s)
        self.assertIn("隣接する $PID の絵（つなぎ目の参考のみ）", s)
        loop = re.search(r'for KV in "\$\{EXTRA_ARR.*?\n  REFS\+=', s, re.S)
        self.assertIsNotNone(loop, "EXTRA_REFS のループが見つからない")
        self.assertRegex(loop.group(0), r"\*\.webp\)")
        self.assertIn("存在しない", s)
        self.assertNotIn("$(printf", s)  # 単語分割・glob 展開に頼るループを使わない

    def test_documented_in_skill_and_readme(self):
        self.assertIn("EXTRA_REFS", (SK / "SKILL.md").read_text())
        self.assertIn("EXTRA_REFS", (SK / "tools/README.md").read_text())
        self.assertIn("test_e2_extra_refs.py", (SK / "SKILL.md").read_text())

    def test_missing_extra_ref_image_exits_with_error(self):
        # EXTRA_REFS の検査は何も作らないうちに行われる（リポを汚さない）。生成先ディレクトリが出来ていないことも確かめる
        out = ROOT / "docs/production/oblique-mocks/TRM-10/e2/_test_missing"
        self.assertFalse(out.exists())
        env = dict(os.environ, EXTRA_REFS="TRM-99=/nonexistent/x.png", DRY_RUN="1")
        r = subprocess.run(["bash", str(RUN), "TRM-10", "1", "e2/_test_missing"], cwd=ROOT, env=env, capture_output=True, text=True, timeout=120)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("存在しない", r.stderr)
        self.assertFalse(out.exists(), "検査失敗時に生成先を作ってはいけない")


if __name__ == "__main__":
    unittest.main()
