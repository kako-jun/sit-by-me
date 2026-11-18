"""event-preview の鮮度検査（preview_event.py check）が、台帳のずれ・手編集・孤児 md を実際に検出する。"""
from pathlib import Path
import shutil
import sys
import contextlib
import io
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import preview_event as P  # noqa: E402


class PreviewFreshness(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        self.sources = root / "ledger"
        self.preview = root / "preview"
        shutil.copytree(P.SOURCES, self.sources)
        shutil.copytree(P.PREVIEW, self.preview)
        for name, value in (("SOURCES", self.sources), ("PREVIEW", self.preview),
                            ("EVENTS", self.preview / "events"), ("INDEX", self.preview / "README.md"),
                            ("BOOK", self.preview / "all_events.md"), ("ROOT", root)):
            patcher = mock.patch.object(P, name, value)
            patcher.start()
            self.addCleanup(patcher.stop)

    def test_committed_preview_is_fresh(self):
        with contextlib.redirect_stdout(io.StringIO()):
            P.check()

    def test_ledger_change_without_regeneration_fails(self):
        path = self.sources / "opening_battle.yaml"
        text = path.read_text(encoding="utf-8")
        self.assertIn("M001@C1", text)
        path.write_text(text.replace("M001@C1", "M002@C1"), encoding="utf-8")
        with self.assertRaises(SystemExit) as ctx:
            P.check()
        self.assertIn("opening_battle.md", str(ctx.exception))

    def test_edited_preview_fails(self):
        path = self.preview / "all_events.md"
        path.write_text(path.read_text(encoding="utf-8") + "\n手編集\n", encoding="utf-8")
        with self.assertRaises(SystemExit):
            P.check()

    def test_crlf_drift_fails(self):
        path = self.preview / "all_events.md"
        path.write_bytes(path.read_bytes().replace(b"\n", b"\r\n"))
        with self.assertRaises(SystemExit):
            P.check()

    def test_orphan_event_md_fails(self):
        (self.preview / "events" / "removed.md").write_text("x", encoding="utf-8")
        with self.assertRaises(SystemExit) as ctx:
            P.check()
        self.assertIn("手で消して", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
