"""docs/INDEX.md の生成ブロックが、配置規則（scripts・tests・skills-doc・skills-tools）に一致する実在ファイルを全部載せる（孤立ファイルを作らない）。"""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".claude/skills/sit-field-background/tools"))
import ledger_index as LI  # noqa: E402


class IndexListing(unittest.TestCase):
    def test_every_matching_file_is_linked_in_generated_block(self):
        block = LI.block()
        for rid, _title, files in LI.listed_files():
            self.assertTrue(files, rid)
            for f in files:
                self.assertIn(f"(../{f})", block, f)

    def test_new_test_files_are_listed(self):
        files = dict((rid, fs) for rid, _t, fs in LI.listed_files())
        self.assertIn("tests/test_index_file_listing.py", files["tests"])
        self.assertIn("scripts/verify_seam_boundaries.py", files["scripts"])

    def test_committed_index_is_up_to_date(self):
        text = (ROOT / "docs/INDEX.md").read_text()
        self.assertIn(LI.block(), text)


if __name__ == "__main__":
    unittest.main()
