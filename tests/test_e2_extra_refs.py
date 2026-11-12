"""oblique_e2_run.sh の EXTRA_REFS（隣接MAPの継ぎ目参考）が、スキルの正規手順としてスクリプト・SKILL.md・README に揃っているかの静的検査。"""
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SK = ROOT / ".claude/skills/sit-field-background"


class ExtraRefs(unittest.TestCase):
    def test_script_handles_extra_refs_and_webp(self):
        s = (SK / "tools/oblique_e2_run.sh").read_text()
        self.assertIn("EXTRA_REFS", s)
        self.assertIn("隣接する $PID の絵（つなぎ目の参考のみ）", s)
        self.assertIn("*.webp) uv run", s.split("EXTRA_REFS=")[1])

    def test_documented_in_skill_and_readme(self):
        self.assertIn("EXTRA_REFS", (SK / "SKILL.md").read_text())
        self.assertIn("EXTRA_REFS", (SK / "tools/README.md").read_text())
        self.assertIn("test_e2_extra_refs.py", (SK / "SKILL.md").read_text())


if __name__ == "__main__":
    unittest.main()
