"""MAP ID付け替え対応表の検査(scripts/verify_map_id_renumber.py)を実リポと変異コピーで確認する。"""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
TABLE = "docs/production/20261019-map-id-renumber.json"


class MapIdRenumberTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in ("docs", "scripts", ".claude"):
            shutil.copytree(ROOT / name, self.root / name)

    def run_cli(self):
        return subprocess.run([sys.executable, "scripts/verify_map_id_renumber.py", "--root", str(self.root)],
                              cwd=self.root, capture_output=True, text=True)

    def mutate(self, name, change):
        path = self.root / name
        data = json.loads(path.read_text(encoding="utf-8"))
        change(data)
        path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    def reject(self, diagnostic):
        result = self.run_cli()
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn(diagnostic, result.stderr)

    def test_real_repository_passes_with_130_one_to_one(self):
        result = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        table = json.loads((ROOT / TABLE).read_text(encoding="utf-8"))["maps"]
        self.assertEqual(len(table), 130)
        self.assertEqual(len({m["old_id"] for m in table}), 130)
        self.assertEqual(len({m["new_id"] for m in table}), 130)

    def test_duplicate_new_id_rejected(self):
        self.mutate(TABLE, lambda d: d["maps"][1].update(new_id=d["maps"][0]["new_id"]))
        self.reject("duplicate new ID")

    def test_missing_entry_rejected(self):
        self.mutate(TABLE, lambda d: d["maps"].pop())
        self.reject("expected 130")

    def test_sequence_gap_rejected(self):
        def gap(d):
            last = next(m for m in d["maps"] if m["new_id"] == "CST-10")
            last["new_id"] = "CST-11"
        self.mutate(TABLE, gap)
        self.reject("gap")

    def test_area_membership_mismatch_rejected(self):
        def move(d):
            first, second = d["areas"][0], d["areas"][1]
            second["maps"].append(first["maps"].pop())
        self.mutate("docs/topology/areas.json", move)
        self.reject("areas.json")

    def test_map_ids_count_mismatch_rejected(self):
        self.mutate("docs/topology/map-ids.json", lambda d: d["areas"].update(TRM=16))
        self.reject("map-ids.json")

    def test_unregistered_new_style_id_in_docs_rejected(self):
        path = self.root / "docs/map-topology.md"
        path.write_text(path.read_text(encoding="utf-8") + "\nTRM-99\n", encoding="utf-8")
        self.reject("unregistered new-style ID TRM-99")

    def test_leftover_old_id_in_map_doc_rejected(self):
        path = self.root / "docs/map-specifications.md"
        path.write_text(path.read_text(encoding="utf-8") + "\n| E14 | 残骸 |\n", encoding="utf-8")
        self.reject("old ID E14 remains")


    def append(self, name, text):
        path = self.root / name
        path.write_text(path.read_text(encoding="utf-8") + text, encoding="utf-8")

    def test_event_id_column_replaced_by_map_id_rejected(self):
        path = self.root / "docs/scenario-registry.md"
        source = path.read_text(encoding="utf-8")
        self.assertIn("| E005 |", source)
        path.write_text(source.replace("| E005 |", "| TRM-08 |", 1), encoding="utf-8")
        self.reject("event ID column")

    def test_map_id_right_after_event_word_rejected(self):
        path = self.root / "docs/map-specifications.md"
        source = path.read_text(encoding="utf-8")
        self.assertIn("購入イベントE005", source)
        path.write_text(source.replace("購入イベントE005", "購入イベントTRM-08", 1), encoding="utf-8")
        self.reject("event/BGM word")

    def test_map_id_in_bgm_table_rejected(self):
        self.append("docs/bgm-registry.md", "\n| TRM-01 | 楽しい |\n")
        self.reject("BGM table")

    def test_leftover_old_id_in_event_registry_rejected(self):
        self.append("docs/scenario-registry.md", "\nMAP:N8/サニーランド入口\n")
        self.reject("old ID N8 remains")

    def test_leftover_old_id_followed_by_letters_rejected(self):
        self.append("docs/map-contract-checklist.md", "\n| 残骸 | E18door |\n")
        self.reject("old ID E18 remains")

    def test_three_digit_event_ids_are_not_old_ids(self):
        self.append("docs/scenario-registry.md", "\n| E031 | ERA-09 | 自動 |\n")
        result = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
