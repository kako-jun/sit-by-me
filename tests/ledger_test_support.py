"""Small offline YAML fixtures shared by the migration regression tests."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / ".claude/skills/sit-field-background/tools"
sys.path.insert(0, str(TOOLS))
import ledger_io as L


def row(table, **values):
    result = dict.fromkeys(L.SCHEMA[table], "")
    result.update(values)
    return result


def environment(root):
    return {**os.environ, "LEDGER_ROOT": str(root), "BODY_DOCS_ROOT": str(root),
            "PATH": "/opt/homebrew/opt/ruby/bin:" + os.environ.get("PATH", "")}


class YamlFixture(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.ledger = self.root / "docs/ledger"
        self.ledger.mkdir(parents=True)
        for table in L.SCHEMA:
            self.write_table(table, [])

    def write_table(self, table, values):
        (self.ledger / (table + ".yaml")).write_text(L.dumps(table, values), encoding="utf-8")

    def read_table(self, table):
        return L.parse(table, (self.ledger / (table + ".yaml")).read_text(encoding="utf-8"))

    def mutate(self, table, change):
        values = self.read_table(table)
        change(values)
        self.write_table(table, values)

    def cli(self, script, *arguments):
        return subprocess.run(["uv", "run", "python3", str(ROOT / "scripts" / script), *arguments],
                              cwd=ROOT, env=environment(self.root), capture_output=True, text=True)

    def assert_rejected(self, result, *diagnostics):
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        for diagnostic in diagnostics:
            self.assertIn(diagnostic, result.stdout + result.stderr)
