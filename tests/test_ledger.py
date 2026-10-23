"""台帳（docs/ledger）・INDEX・ファイル配置表の検証が、壊れた fixture で実際に失敗することを確認する。

root は環境変数 LEDGER_ROOT で差し替える（verify_index_reachable.rb・ledger_index.py・ledger_yaml.rb・ledger_io.py 共通の方針）。
実行: uv run python3 -m unittest tests.test_ledger  （または discover -s tests）
"""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / ".claude/skills/sit-field-background/tools"
sys.path.insert(0, str(TOOLS))
import ledger_io  # noqa: E402  (テストでは表のテキスト生成 dumps だけを使う)

RUBY = next((p for p in ("/opt/homebrew/opt/ruby/bin/ruby", shutil.which("ruby")) if p and os.path.exists(p)), "ruby")
LAYOUT_COLS = ledger_io.SCHEMA["ファイル配置"]


def rule(id, pattern, reach="リンク", entry="", reason="", kind="ドキュメント", use="テスト用"):
    row = dict.fromkeys(LAYOUT_COLS, "")
    row.update({"配置ID": id, "パターン": pattern, "種別": kind, "用途": use, "到達": reach, "入口": entry, "許可リスト理由": reason})
    return row


BASE_RULES = [
    rule("index", r"docs/INDEX\.md"),
    rule("docs-top", r"docs/(?!INDEX\.md)[^/]+\.md"),
    rule("ledger-master", r"docs/ledger/[^/]+\.yaml", kind="台帳マスター"),
    rule("bulk", r"docs/bulk/(?!README\.md).+", reach="許可", entry="docs/bulk/README.md", reason="機械出力の置き場。README が説明する"),
    rule("bulk-readme", r"docs/bulk/README\.md"),
]

INDEX_TEXT = """# INDEX

- [a](a.md)
- [bulk](bulk/README.md)

<!-- GENERATED:BEGIN ledger-views -->
<!-- GENERATED:END ledger-views -->
"""


def env_for(root):
    return {**os.environ, "LEDGER_ROOT": str(root)}


class Fixture(unittest.TestCase):
    """最小の root を tmp に作る。docs/INDEX.md → a.md、許可リストの docs/bulk（README が入口）。"""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.write("docs/INDEX.md", INDEX_TEXT)
        self.write("docs/a.md", "# a\n")
        self.write("docs/bulk/README.md", "# bulk\n")
        self.write("docs/bulk/out-1.json", "{}\n")
        self.set_rules(BASE_RULES)
        self.build_index()

    def write(self, rel, text):
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
        return p

    def set_rules(self, rules):
        self.write("docs/ledger/ファイル配置.yaml", ledger_io.dumps("ファイル配置", rules))

    def build_index(self):
        r = self.run_py("build")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def run_py(self, cmd):
        return subprocess.run([sys.executable, str(TOOLS / "ledger_index.py"), cmd], env=env_for(self.root),
                              capture_output=True, text=True, cwd=ROOT)

    def reachable(self):
        return subprocess.run([RUBY, str(ROOT / "scripts/verify_index_reachable.rb")], env=env_for(self.root),
                              capture_output=True, text=True)

    def assertFails(self, result, *needles):
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        for n in needles:
            self.assertIn(n, result.stderr)


class IndexReachabilityTests(Fixture):
    def test_clean_fixture_passes(self):
        r = self.reachable()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("PASS", r.stdout)

    def test_orphan_file_fails(self):
        self.write("docs/orphan.md", "# nobody links me\n")
        self.assertFails(self.reachable(), "孤立ファイル", "docs/orphan.md")

    def test_file_reachable_only_through_a_chain_passes(self):
        self.write("docs/b.md", "# b\n[c](c.md)\n")
        self.write("docs/c.md", "# c\n")
        self.write("docs/a.md", "# a\n[b](b.md)\n")
        self.assertEqual(self.reachable().returncode, 0)

    def test_broken_link_fails(self):
        self.write("docs/a.md", "# a\n[gone](missing.md)\n")
        self.assertFails(self.reachable(), "壊れたリンク", "missing.md")

    def test_link_inside_code_is_ignored(self):
        self.write("docs/a.md", "# a\n`[x](nothing.md)`\n```\n[y](nothing2.md)\n```\n")
        self.assertEqual(self.reachable().returncode, 0)

    def test_file_without_layout_rule_fails(self):
        self.write("tools/new.py", "print(1)\n")
        self.assertFails(self.reachable(), "配置規則に無いファイル", "tools/new.py")

    def test_file_matching_two_rules_fails(self):
        self.set_rules(BASE_RULES + [rule("dup", r"docs/a\.md")])
        self.assertFails(self.reachable(), "複数の配置規則に一致", "docs/a.md")

    def test_allowlist_without_reason_fails(self):
        rules = [dict(r, **{"許可リスト理由": ""}) if r["配置ID"] == "bulk" else r for r in BASE_RULES]
        self.set_rules(rules)
        self.assertFails(self.reachable(), "許可リスト理由")

    def test_allowlist_entrance_not_linked_fails(self):
        self.write("docs/INDEX.md", INDEX_TEXT.replace("- [bulk](bulk/README.md)\n", ""))
        self.build_index()
        self.assertFails(self.reachable(), "入口", "辿れない")

    def test_allowlist_entrance_missing_fails(self):
        (self.root / "docs/bulk/README.md").unlink()
        self.assertFails(self.reachable())

    def test_allowlisted_files_need_no_individual_link(self):
        self.write("docs/bulk/out-2.json", "{}\n")
        self.assertEqual(self.reachable().returncode, 0)

    def dir_entrance_rules(self):
        return BASE_RULES + [rule("dirent", r"docs/dirent/.+", reach="許可", entry="docs/dirent", reason="ディレクトリ単位で入る記録")]

    def test_allowlist_directory_entrance_unlinked_fails(self):
        self.write("docs/dirent/x.md", "# x\n")
        self.set_rules(self.dir_entrance_rules())
        self.build_index()
        self.assertFails(self.reachable(), "入口ディレクトリ", "辿れない")

    def test_allowlist_directory_entrance_linked_passes(self):
        self.write("docs/dirent/x.md", "# x\n")
        self.write("docs/a.md", "# a\n[dir](dirent/)\n")
        self.set_rules(self.dir_entrance_rules())
        self.build_index()
        self.assertEqual(self.reachable().returncode, 0, self.reachable().stderr)

    def test_link_pointing_outside_root_fails(self):
        self.write("docs/a.md", "# a\n[x](../../outside.md)\n")
        self.assertFails(self.reachable(), "壊れたリンク")

    def test_real_repo_has_no_orphans(self):
        r = subprocess.run([RUBY, str(ROOT / "scripts/verify_index_reachable.rb")], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)


class GeneratedViewFreshnessTests(Fixture):
    def test_fresh_view_passes(self):
        r = self.run_py("check")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_hand_edited_view_fails(self):
        p = self.root / "docs/INDEX.md"
        p.write_text(p.read_text(encoding="utf-8").replace("ファイル配置規則", "ファイル配置規則（手編集）"), encoding="utf-8")
        r = self.run_py("check")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("古い", r.stdout)

    def test_ledger_change_makes_view_stale(self):
        self.write("docs/ledger/語彙.yaml", ledger_io.dumps("語彙", [
            {"語彙ID": "V1", "グループ": "g", "値": "v", "英語断片": "", "説明": ""}]))
        r = self.run_py("check")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("古い", r.stdout)
        self.build_index()
        self.assertEqual(self.run_py("check").returncode, 0)

    def test_missing_markers_fails(self):
        self.write("docs/INDEX.md", "# INDEX\n[a](a.md)\n")
        r = self.run_py("check")
        self.assertNotEqual(r.returncode, 0)


class VerifyLedgerIntegrationTests(unittest.TestCase):
    """実リポの台帳をコピーして verify_ledger.rb が新表の違反と古い INDEX を検出するか（他の検査の結果とは独立に、該当メッセージの有無を見る）。"""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.base = Path(cls.tmp.name)
        for name in ("scripts", ".claude/skills/sit-field-background/tools"):
            shutil.copytree(ROOT / name, cls.base / name, ignore=shutil.ignore_patterns("__pycache__"))
        for name in ("docs/ledger", "docs/topology"):
            shutil.copytree(ROOT / name, cls.base / name, ignore=shutil.ignore_patterns("handoff"))
        shutil.copy(ROOT / "docs/INDEX.md", cls.base / "docs/INDEX.md")
        for name in ("pyproject.toml", "uv.lock"):
            shutil.copy(ROOT / name, cls.base / name)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def setUp(self):
        self.scratch = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.scratch, True)
        self.work = self.scratch / "r"
        shutil.copytree(self.base, self.work, ignore=shutil.ignore_patterns(".venv"))

    def verify(self):
        env = {**os.environ, "LEDGER_ROOT": str(self.work), "LEDGER_SKIP_REGEN": "1"}
        return subprocess.run([RUBY, str(self.work / "scripts/verify_ledger.rb")], env=env, capture_output=True, text=True, cwd=self.work)

    def test_stale_index_is_reported(self):
        p = self.work / "docs/INDEX.md"
        p.write_text(p.read_text(encoding="utf-8").replace("### 台帳の表", "### 台帳の表（古い）"), encoding="utf-8")
        self.assertIn("生成ビューが古い", self.verify().stderr)

    def test_fresh_index_is_not_reported(self):
        self.assertNotIn("生成ビューが古い", self.verify().stderr)

    def test_layout_allow_without_reason_is_reported(self):
        p = self.work / "docs/ledger/ファイル配置.yaml"
        rows = ledger_io.parse("ファイル配置", p.read_text(encoding="utf-8"))
        for r in rows:
            if r["到達"] == "許可":
                r["許可リスト理由"] = ""
        p.write_text(ledger_io.dumps("ファイル配置", rows), encoding="utf-8")
        self.assertIn("許可リスト理由が要る", self.verify().stderr)

    def test_layout_unknown_owner_table_is_reported(self):
        p = self.work / "docs/ledger/ファイル配置.yaml"
        rows = ledger_io.parse("ファイル配置", p.read_text(encoding="utf-8"))
        rows[0]["所有表"] = "存在しない表"
        p.write_text(ledger_io.dumps("ファイル配置", rows), encoding="utf-8")
        self.assertIn("所有表='存在しない表'", self.verify().stderr)

    def test_generated_path_without_layout_rule_is_reported(self):
        p = self.work / "docs/ledger/生成物.yaml"
        rows = ledger_io.parse("生成物", p.read_text(encoding="utf-8"))
        rows[0]["パス"] = "nowhere/plan.json"
        p.write_text(ledger_io.dumps("生成物", rows), encoding="utf-8")
        self.assertIn("どの配置規則", self.verify().stderr)


if __name__ == "__main__":
    unittest.main()
