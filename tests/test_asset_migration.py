"""Independent post-migration checks; no images are generated or rewritten."""
import functools
import hashlib
import http.server
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest
from urllib.parse import urljoin, urlsplit
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs/production/20261018-asset-migration.json"
PNG = b"\x89PNG\r\n\x1a\n"


def strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from strings(item)


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


class AssetMigrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(MANIFEST.read_text())
        cls.rows = cls.manifest["entries"]

    def test_manifest_covers_original_assets_once(self):
        original = subprocess.check_output(
            ["git", "ls-tree", "-r", "--name-only", self.manifest["base_commit"],
             "assets", "sample"], cwd=ROOT, text=True).splitlines()
        old = [row["old"] for row in self.rows]
        self.assertEqual(len(old), len(set(old)), "duplicate source in manifest")
        self.assertEqual(set(original), set(old))
        targets = [row["new"] for row in self.rows if row["action"] == "move"]
        self.assertEqual(len(targets), len(set(targets)), "destination collision")

    def test_move_bytes_and_deletion_tombstones(self):
        for row in self.rows:
            with self.subTest(old=row["old"]):
                self.assertFalse((ROOT / row["old"]).exists())
                self.assertRegex(row["sha256"], r"^[0-9a-f]{64}$")
                self.assertTrue(row.get("source_commit", self.manifest["base_commit"]))
                self.assertTrue(row["reason"])
                if row["action"] == "move":
                    target = ROOT / row["new"]
                    self.assertTrue(target.is_file())
                    if target.suffix == ".png":
                        self.assertEqual(hashlib.sha256(target.read_bytes()).hexdigest(), row["sha256"])
                else:
                    self.assertEqual(row["action"], "delete")
                    self.assertIsNone(row["new"])

    def test_character_identity_and_every_suffix_preserved(self):
        ids = {"otton": "C001", "nam": "C002", "shah": "C003", "peiko": "C004"}
        seen = set()
        for row in self.rows:
            old = Path(row["old"])
            if not row["old"].startswith("assets/characters/") or old.suffix != ".png":
                continue
            name, suffix = old.name.split("-", 1)
            ident = ids[name]
            seen.add(ident)
            expected = f"assets/images/characters/{ident}/{old.parent.name}/{ident}-{suffix}"
            self.assertEqual(row["new"], expected)
        self.assertEqual(seen, set(ids.values()))

    def test_no_fabricated_summon_or_live_sample_assets(self):
        before = [r for r in self.rows if r["old"].startswith("assets/summons/") and r["action"] == "move"]
        actual = list((ROOT / "assets/images/summons").rglob("*.png"))
        self.assertEqual({r["new"] for r in before}, {p.relative_to(ROOT).as_posix() for p in actual})
        self.assertFalse((ROOT / "assets/images/summons/S008.png").exists())
        self.assertFalse(any((ROOT / "sample").rglob("*.png")))
        for config in (ROOT / "verification").rglob("*.json"):
            for value in strings(json.loads(config.read_text())):
                if urlsplit(value).path.endswith(".png"):
                    self.assertNotIn("sample/", value, str(config))

    def test_actual_http_configs_and_image_resolution(self):
        handler = functools.partial(QuietHandler, directory=str(ROOT))
        server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
        worker = threading.Thread(target=server.serve_forever, daemon=True)
        worker.start()
        origin = f"http://127.0.0.1:{server.server_port}/"
        try:
            fetched = set()
            for relative in ["verification/battles/stage-b.json", "verification/fields/teramachi-diorama-wheelchair.field.json"]:
                config_url = urljoin(origin, relative)
                with urlopen(config_url) as response:
                    self.assertEqual(response.status, 200)
                    config = json.load(response)
                for value in strings(config):
                    parsed = urlsplit(value)
                    if not parsed.path.endswith(".png"):
                        continue
                    # A localhost URL retains its root path, not its stale port.
                    url = urljoin(origin, parsed.path.lstrip("/")) if parsed.hostname in {"localhost", "127.0.0.1"} else urljoin(config_url, value)
                    self.assertEqual(urlsplit(url).netloc, urlsplit(origin).netloc)
                    with urlopen(url) as response:
                        self.assertEqual(response.status, 200)
                        self.assertEqual(response.read()[:8], PNG, url)
                    fetched.add(urlsplit(url).path)
            self.assertIn("/assets/images/enemies/M001.png", fetched)
            self.assertIn("/assets/images/battle-backgrounds/BG005.png", fetched)
            self.assertTrue(any("/masks/" in path for path in fetched))
            self.assertTrue(any("/fields/legacy/" in path for path in fetched))
        finally:
            server.shutdown()
            server.server_close()
            worker.join()


class VerifierFailureTests(unittest.TestCase):
    def fixture(self, root):
        (root / "docs/production").mkdir(parents=True)
        target = "assets/images/enemies/M001.png"
        (root / target).parent.mkdir(parents=True)
        (root / target).write_bytes(PNG + b"fixture")
        return dict(old="assets/enemies/dragon.png", new=target, action="move",
                    reason="fixture", sha256=hashlib.sha256(PNG + b"fixture").hexdigest())

    def run_verifier(self, root, rows):
        (root / "docs/production/20261018-asset-migration.json").write_text(json.dumps(dict(entries=rows)))
        return subprocess.run([sys.executable, str(ROOT / "scripts/verify_asset_layout.py"),
                               "--root", str(root)], capture_output=True, text=True)

    def test_valid_fixture_repeat_safe_and_missing_asset_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            row = self.fixture(root)
            for _ in range(2):
                self.assertEqual(self.run_verifier(root, [row]).returncode, 0)
            (root / row["new"]).unlink()
            result = self.run_verifier(root, [row])
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Missing migrated asset", result.stderr)

    def test_duplicate_destination_and_source_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            row = self.fixture(root)
            result = self.run_verifier(root, [row, dict(row, old="assets/enemies/other.png")])
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Duplicate manifest destination", result.stderr)
            result = self.run_verifier(root, [row, dict(row, new="assets/images/enemies/M002.png")])
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Duplicate manifest source", result.stderr)
            self.assertEqual((root / row["new"]).read_bytes(), PNG + b"fixture")

    def test_url_forms_and_known_missing_versus_live_dangling(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            row = self.fixture(root)
            config = root / "verification/battles/test.json"
            config.parent.mkdir(parents=True)
            paths = ["../../assets/images/enemies/M001.png",
                     "/assets/images/enemies/M001.png",
                     "http://localhost:8765/assets/images/enemies/M001.png"]
            config.write_text(json.dumps(dict(sprite=paths)))
            (root / "docs/reviews").mkdir()
            (root / "docs/reviews/history.md").write_text("Deleted sample/failed.png; S008 image never existed.")
            self.assertEqual(self.run_verifier(root, [row]).returncode, 0)
            config.write_text(json.dumps(dict(sprite="../../assets/images/summons/S008.png")))
            result = self.run_verifier(root, [row])
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Dangling reference", result.stderr)
            self.assertFalse((root / "assets/images/summons/S008.png").exists())


if __name__ == "__main__":
    unittest.main()
