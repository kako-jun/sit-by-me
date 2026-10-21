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
from urllib.parse import urljoin
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs/production/20261018-asset-migration.json"
PNG = b"\x89PNG\r\n\x1a\n"


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
                    if target.suffix in {".png", ".webp"}:
                        self.assertEqual(hashlib.sha256(target.read_bytes()).hexdigest(), row["sha256"])
                else:
                    self.assertEqual(row["action"], "delete")
                    self.assertIsNone(row["new"])

    def test_character_identity_and_every_suffix_preserved(self):
        ids = {"otton": "C001", "nam": "C002", "shah": "C003", "peiko": "C004"}
        seen = set()
        for row in self.rows:
            old = Path(row["old"])
            if not row["old"].startswith("assets/characters/") or old.suffix != ".png" or row["action"] != "move":
                continue
            name, suffix = old.name.split("-", 1)
            ident = ids[name]
            seen.add(ident)
            expected = f"assets/images/characters/{ident}/{old.parent.name}/{ident}-{suffix.removesuffix('.png')}.webp"
            self.assertEqual(row["new"], expected)
        self.assertEqual(seen, set(ids.values()))

    def test_no_fabricated_summon_or_live_sample_assets(self):
        before = [r for r in self.rows if r["old"].startswith("assets/summons/") and r["action"] == "move"]
        actual = list((ROOT / "assets/images/summons").rglob("*.webp"))
        self.assertEqual({r["new"] for r in before}, {p.relative_to(ROOT).as_posix() for p in actual})
        self.assertFalse((ROOT / "assets/images/summons/S008.webp").exists())
        self.assertFalse(any((ROOT / "sample").rglob("*.png")))

    def test_pruned_paths_stay_deleted(self):
        pruned = [r for r in self.rows if r.get("pruned_path")]
        self.assertTrue(pruned)
        for row in pruned:
            self.assertEqual(row["action"], "delete")
            self.assertFalse((ROOT / row["pruned_path"]).exists(), row["pruned_path"])
        for relative in ["assets/images/enemies/raw", "assets/images/summons/raw", "verification/battles",
                         "verification/fields", "assets/images/fields/verification"]:
            self.assertFalse((ROOT / relative).exists(), relative)
        self.assertEqual(list((ROOT / "assets/images/characters").glob("*/raw")), [])

    def test_actual_http_image_resolution(self):
        handler = functools.partial(QuietHandler, directory=str(ROOT))
        server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
        worker = threading.Thread(target=server.serve_forever, daemon=True)
        worker.start()
        origin = f"http://127.0.0.1:{server.server_port}/"
        try:
            fetched = set()
            for relative in ["assets/images/enemies/M001.webp",
                             "assets/images/battle-backgrounds/BG001.webp"]:
                with urlopen(urljoin(origin, relative)) as response:
                    self.assertEqual(response.status, 200)
                    body = response.read(12)
                    self.assertEqual((body[:4], body[8:12]), (b"RIFF", b"WEBP"), relative)
                fetched.add(relative)
            legacy = sorted((ROOT / "assets/images/fields/legacy").glob("*.webp"))
            self.assertTrue(legacy)
            with urlopen(urljoin(origin, legacy[0].relative_to(ROOT).as_posix())) as response:
                body = response.read(12)
                self.assertEqual((body[:4], body[8:12]), (b"RIFF", b"WEBP"))
        finally:
            server.shutdown()
            server.server_close()
            worker.join()


class VerifierFailureTests(unittest.TestCase):
    def fixture(self, root):
        (root / "docs/production").mkdir(parents=True)
        target = "assets/images/enemies/M001.webp"
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
            result = self.run_verifier(root, [row, dict(row, new="assets/images/enemies/M002.webp")])
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Duplicate manifest source", result.stderr)
            self.assertEqual((root / row["new"]).read_bytes(), PNG + b"fixture")

    def test_nested_finder_metadata_is_ignored_without_removal(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            row = self.fixture(root)
            metadata = root / "sample/field/nested/.DS_Store"
            metadata.parent.mkdir(parents=True)
            metadata.write_bytes(b"existing-user-finder-metadata")
            result = self.run_verifier(root, [row])
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(metadata.read_bytes(), b"existing-user-finder-metadata")

    def test_field_legacy_requires_map_id_webp(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            row = self.fixture(root)
            for ok in ["assets/images/fields/legacy/TRM-01.webp",
                       "assets/images/fields/legacy/KRB-06-v1.webp",
                       "assets/images/fields/legacy/masks/TRM-16-bottom__TRM-15-top.webp"]:
                path = root / ok
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b"RIFFxxxxWEBPok")
            self.assertEqual(self.run_verifier(root, [row]).returncode, 0)
            for bad in ["assets/images/fields/legacy/E01.webp",
                        "assets/images/fields/legacy/TRM-01.png",
                        "assets/images/fields/legacy/masks/TRM-01-mask.png",
                        "assets/images/fields/legacy/XXX-01.webp"]:
                with self.subTest(bad=bad):
                    path = root / bad
                    path.write_bytes(b"RIFFxxxxWEBPbad")
                    result = self.run_verifier(root, [row])
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("Non-ID image", result.stderr)
                    path.unlink()

    def test_field_reference_webp_allowed_only_under_reference_dir(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            row = self.fixture(root)
            ok = root / "assets/images/fields/reference/teramachi-common-exterior-reference.webp"
            ok.parent.mkdir(parents=True)
            ok.write_bytes(b"RIFFxxxxWEBPreference")
            self.assertEqual(self.run_verifier(root, [row]).returncode, 0)
            for bad in ["assets/images/fields/unknown.webp",
                        "assets/images/fields/reference/nested/x.webp",
                        "assets/images/fields/reference/Bad_Name.webp",
                        "assets/images/enemies/Bad.webp"]:
                with self.subTest(bad=bad):
                    path = root / bad
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(b"RIFFxxxxWEBPbad")
                    result = self.run_verifier(root, [row])
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("Non-ID image", result.stderr)
                    path.unlink()

    def test_sample_images_including_hidden_files_still_fail(self):
        for filename in ["old.PNG", ".hidden.png"]:
            with self.subTest(filename=filename), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                row = self.fixture(root)
                asset = root / "sample/field/nested" / filename
                asset.parent.mkdir(parents=True)
                asset.write_bytes(PNG + b"old-asset")
                result = self.run_verifier(root, [row])
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("sample still contains files", result.stderr)
                self.assertEqual(asset.read_bytes(), PNG + b"old-asset")


if __name__ == "__main__":
    unittest.main()
