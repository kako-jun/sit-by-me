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
from urllib.error import HTTPError
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / ".claude/skills/sit-field-background/tools"))
import asset_chain
import ledger_io
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
        # 移行後の差し替えは素材更新のSHA連鎖で追跡する（移行時SHAは履歴として固定）
        cls.chains = asset_chain.index(ledger_io.read("素材更新"))

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
                        actual = hashlib.sha256(target.read_bytes()).hexdigest()
                        self.assertTrue(asset_chain.reaches(self.chains, row["new"], row["sha256"], actual),
                                        f"{row['new']}: 移行SHAから現物SHAへの素材更新の連鎖がない")
                else:
                    self.assertEqual(row["action"], "delete")
                    self.assertIsNone(row["new"])

    def test_every_chain_starts_at_migration_sha_and_ends_at_live_bytes(self):
        migrated = {r["new"]: r["sha256"] for r in self.rows if r["action"] == "move"}
        for path, steps in self.chains.items():
            with self.subTest(path=path):
                head = [old for old in steps if old not in steps.values()]
                self.assertEqual(len(head), 1)
                if path in migrated:
                    self.assertEqual(head[0], migrated[path])
                end = asset_chain.walk(steps, head[0])[-1]
                self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), end)

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
        live = {p.relative_to(ROOT).as_posix() for p in actual}
        migrated = {r["new"] for r in before}
        # 移行した召喚獣画像は現存する。移行後に追加された画像は素材台帳に載っていなければならない
        self.assertLessEqual(migrated, live)
        registered = {r["パス"] for r in ledger_io.read("素材")}
        self.assertEqual(live - migrated - registered, set())
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
                    body = response.read()
                    self.assertEqual((body[:4], body[8:12]), (b"RIFF", b"WEBP"), relative)
                fetched.add(relative)
            # BG005 was explicitly retired after the original migration. Its
            # tombstone remains auditable, while the live HTTP path is gone.
            retired = "assets/images/battle-backgrounds/BG005.webp"
            tombstone = [row for row in self.rows if row.get("pruned_path") == retired]
            self.assertEqual(len(tombstone), 1)
            self.assertEqual((tombstone[0]["action"], tombstone[0]["new"]), ("delete", None))
            with self.assertRaises(HTTPError) as response:
                urlopen(urljoin(origin, retired))
            self.assertEqual(response.exception.code, 404)
            legacy = sorted((ROOT / "assets/images/fields/legacy").glob("*.webp"))
            self.assertTrue(legacy)
            with urlopen(urljoin(origin, legacy[0].relative_to(ROOT).as_posix())) as response:
                body = response.read()
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

    def chain_fixture(self, root, row, steps):
        ledger = root / "docs/ledger"
        ledger.mkdir(parents=True, exist_ok=True)
        rows = [dict.fromkeys(ledger_io.SCHEMA["素材更新"], "") | {
            "更新ID": f"AUP-{n:03d}", "素材ID": "A-1", "パス": row["new"], "旧sha256": old, "新sha256": new,
            "出典commit": "abcdef0", "出典パス": row["new"], "根拠": "fixture"} for n, (old, new) in enumerate(steps, 1)]
        (ledger / "素材更新.yaml").write_text(ledger_io.dumps("素材更新", rows), encoding="utf-8")

    def test_update_chain_accepts_replaced_bytes_and_mutations_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            row = self.fixture(root)
            migrated = row["sha256"]
            (root / row["new"]).write_bytes(PNG + b"replaced-twice")
            final = hashlib.sha256(PNG + b"replaced-twice").hexdigest()
            middle = hashlib.sha256(PNG + b"replaced-once").hexdigest()
            # 連鎖なし: 差し替えは検出される
            self.assertNotEqual(self.run_verifier(root, [row]).returncode, 0)
            # 移行SHA -> 中間 -> 現物 の連鎖があれば受理される
            self.chain_fixture(root, row, [(migrated, middle), (middle, final)])
            self.assertEqual(self.run_verifier(root, [row]).returncode, 0)
            # 変異: 連鎖の途切れ・起点違い・終点違いはどれも落ちる
            other = hashlib.sha256(b"unrelated").hexdigest()
            for label, steps in {"途切れ": [(migrated, middle), (other, final)],
                                 "起点違い": [(other, middle), (middle, final)],
                                 "終点違い": [(migrated, middle), (middle, other)],
                                 "分岐": [(migrated, middle), (migrated, final)]}.items():
                with self.subTest(mutation=label):
                    self.chain_fixture(root, row, steps)
                    result = self.run_verifier(root, [row])
                    self.assertNotEqual(result.returncode, 0, label)

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


class AssetChainValidateTests(unittest.TestCase):
    PATH = "assets/images/enemies/M001.webp"
    A, B, C = ("a" * 64, "b" * 64, "c" * 64)

    def run_validate(self, updates, current=None, moved=None):
        assets = [{"素材ID": "A-1", "パス": self.PATH, "sha256": current or self.B}]
        migration = [{"操作": "move", "新パス": self.PATH, "sha256": moved or self.A}]
        rows = [{"更新ID": f"AUP-{n}", "素材ID": "A-1", "パス": self.PATH, "旧sha256": old, "新sha256": new,
                 "出典commit": "abcdef0", "出典パス": self.PATH} for n, (old, new) in enumerate(updates, 1)]
        return asset_chain.validate(rows, assets, migration)

    def test_valid_chain_passes(self):
        self.assertEqual(self.run_validate([(self.A, self.B)]), [])

    def test_missing_update_row_is_detected(self):
        errors = self.run_validate([], current=self.B, moved=self.A)
        self.assertTrue(any("連鎖がない" in e for e in errors), errors)
        self.assertEqual(self.run_validate([], current=self.A, moved=self.A), [])

    def test_reaches_requires_chain_end(self):
        chains = asset_chain.index([{"パス": "p", "旧sha256": self.A, "新sha256": self.B},
                                    {"パス": "p", "旧sha256": self.B, "新sha256": self.C}])
        self.assertTrue(asset_chain.reaches(chains, "p", self.A, self.C))
        self.assertFalse(asset_chain.reaches(chains, "p", self.A, self.B))
        self.assertFalse(asset_chain.reaches(chains, "p", self.A, self.A))
        self.assertTrue(asset_chain.reaches({}, "q", self.A, self.A))

    def test_sources_checked_against_git(self):
        def fake_git(blobs, commits, shallow=False):
            def git(*args):
                if args[:2] == ("cat-file", "-e"):
                    return (0 if args[2].split("^")[0] in commits else 1), b""
                if args[:2] == ("cat-file", "blob"):
                    ref, path = args[2].split(":", 1)
                    return (0, blobs[(ref, path)]) if (ref, path) in blobs else (128, b"")
                if args[0] == "rev-parse":
                    return 0, b"true\n" if shallow else b"false\n"
                assert args[:2] == ("log", "--follow"), args  # 改名をまたいで履歴を辿る
                return 0, b"h1\n"
            return git
        row = {"更新ID": "AUP-1", "パス": self.PATH, "旧sha256": hashlib.sha256(b"old").hexdigest(),
               "新sha256": hashlib.sha256(b"new").hexdigest(), "出典commit": "abcdef0", "出典パス": self.PATH}
        good = fake_git({("abcdef0", self.PATH): b"new", ("h1", self.PATH): b"old"}, {"abcdef0"})
        self.assertEqual(asset_chain.validate_sources([row], [], good), [])
        missing = fake_git({("abcdef0", self.PATH): b"new", ("h1", self.PATH): b"old"}, set())
        self.assertTrue(any("存在しない" in e for e in asset_chain.validate_sources([row], [], missing)))
        shallow = asset_chain.validate_sources([row], [], fake_git({}, set(), shallow=True))
        self.assertTrue(any("shallow" in e and "unshallow" in e for e in shallow), shallow)
        self.assertFalse(any("shallow" in e for e in asset_chain.validate_sources([row], [], missing)))
        wrong_new = fake_git({("abcdef0", self.PATH): b"other", ("h1", self.PATH): b"old"}, {"abcdef0"})
        self.assertTrue(any("blob と違う" in e for e in asset_chain.validate_sources([row], [], wrong_new)))
        orphan_start = fake_git({("abcdef0", self.PATH): b"new", ("h1", self.PATH): b"else"}, {"abcdef0"})
        self.assertTrue(any("起点" in e for e in asset_chain.validate_sources([row], [], orphan_start)))
        # 起点が移行行にあれば git 履歴の blob は要らない
        self.assertEqual(asset_chain.validate_sources([row], [{"操作": "move", "新パス": self.PATH}], orphan_start), [])


if __name__ == "__main__":
    unittest.main()
