"""素材メタデータ: YAML正本→JSONの生成・検査（数値表記の保持、私的パスの除去、集合の照合）。"""
import hashlib
import json

from tests.ledger_test_support import ROOT, L, YamlFixture, row
import sys

sys.path.insert(0, str(ROOT / "scripts"))
import asset_metadata as A

RAW = '{\n  "x": 0.70,\n  "path": "/home/someone/out.png",\n  "ok": "output/a.png",\n  "list": [1, 2.50, {}],\n  "empty": [],\n  "nothing": null\n}\n'


class MetadataFunctionTests(YamlFixture):
    def test_numbers_keep_their_original_notation_and_private_strings_are_redacted(self):
        node = A.sanitize(A.loads(RAW))
        text = A.output_bytes(node).decode()
        self.assertIn('"x": 0.70', text)
        self.assertIn("2.50", text)
        self.assertIn('"path": "redacted local provenance"', text)
        self.assertIn('"ok": "output/a.png"', text)
        rebuilt = A.reconstruct(list(A.flatten("AMETA-X", node)))
        self.assertEqual(A.output_bytes(rebuilt), A.output_bytes(node))

    def test_private_patterns_cover_unix_home_windows_and_run_ids(self):
        for value in ("/Users/a/b.png", "/home/a/b.png", "/tmp/x", "/private/var/x", "~/work/x.png", r"C:\Users\a\x.png",
                      "D:/work/x.png", r"\\server\share\x", "exec-0a1b2c3d-1111-2222-3333-444455556666.png"):
            with self.subTest(value=value):
                self.assertEqual(A.sanitize({"k": value})["k"], A.REDACTED)
        for value in ("output/battle-sword-previews/x.png", "swing-followthrough", "about 1.4-1.6 x height"):
            with self.subTest(value=value):
                self.assertEqual(A.sanitize({"k": value})["k"], value)


class MetadataLedgerTests(YamlFixture):
    PATH = "assets/images/weapons/C001/C001-blade-candidates.json"

    def setUp(self):
        super().setUp()
        # LEDGER_ROOT を fixture に向けて CLI を実行する
        node = A.sanitize(A.loads(RAW))
        payload = A.output_bytes(node)
        self.write_table("素材メタデータ", [row("素材メタデータ", メタデータID="AMETA-001", パス=self.PATH, 所有者ID="C001",
                                           原文sha256="0" * 64, 安全化sha256=hashlib.sha256(payload).hexdigest(),
                                           出典commit="abcdef0", 安全化方針="fixture")])
        self.write_table("素材メタデータ値", [row("素材メタデータ値", **leaf) for leaf in A.flatten("AMETA-001", node)])
        (self.root / self.PATH).parent.mkdir(parents=True)
        (self.root / self.PATH).write_bytes(payload)

    def check(self):
        return self.cli("asset_metadata.py", "check")

    def test_valid_fixture_passes_for_any_record_count(self):
        result = self.check()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("1 sanitized", result.stdout)

    def test_stale_json_unregistered_json_and_hash_drift_are_rejected(self):
        (self.root / self.PATH).write_text('{"edited": true}\n')
        self.assert_rejected(self.check(), "Stale metadata JSON")
        self.cli("asset_metadata.py", "build")
        self.assertEqual(self.check().returncode, 0)
        extra = self.root / "assets/images/effects/C009/C009-extra.json"
        extra.parent.mkdir(parents=True)
        extra.write_text("{}\n")
        self.assert_rejected(self.check(), "unregistered")
        extra.unlink()
        self.mutate("素材メタデータ", lambda rows: rows[0].update(安全化sha256="f" * 64))
        self.assert_rejected(self.check(), "Sanitized hash differs")

    def test_private_provenance_in_yaml_values_is_rejected(self):
        def leak(rows):
            rows[[r["JSONポインタ"] for r in rows].index("/path")]["値"] = json.dumps("/home/someone/out.png")
        self.mutate("素材メタデータ値", leak)
        self.assert_rejected(self.check(), "Private provenance")

    def git_commit(self):
        import subprocess
        run = lambda *a: subprocess.run(["git", "-C", str(self.root), *a], capture_output=True, text=True, check=True)
        run("init", "-q")
        run("-c", "user.name=t", "-c", "user.email=t@example.com", "commit", "-q", "--allow-empty", "-m", "x")
        return run("rev-parse", "HEAD").stdout.strip()

    def ingest(self, commit, path=None, owner="C001"):
        raw = self.root / "raw.json"
        raw.write_text(RAW)
        return self.cli("asset_metadata.py", "ingest", "--source", str(raw), "--path", path or self.PATH,
                        "--owner", owner, "--commit", commit)

    def test_ingest_validates_path_owner_and_commit(self):
        self.write_table("人物", [row("人物", 人物ID="C001")])
        commit = self.git_commit()
        self.assertEqual(self.ingest(commit).returncode, 0)
        self.assert_rejected(self.ingest(commit, path="docs/x.json"), "--path")
        self.assert_rejected(self.ingest(commit, path="assets/images/a/x.png"), "--path")
        self.assert_rejected(self.ingest(commit, path="assets/images/../x.json"), "--path")
        self.assert_rejected(self.ingest(commit, owner="C999"), "--owner")
        self.assert_rejected(self.ingest(commit, owner=""), "--owner")
        self.assert_rejected(self.ingest("abcdef1"), "git に存在しない")

    def test_ingest_reimports_raw_json_and_rebuilds_identically(self):
        self.write_table("人物", [row("人物", 人物ID="C001")])
        raw = self.root / "raw.json"
        raw.write_text(RAW.replace("0.70", "0.75"))
        result = self.cli("asset_metadata.py", "ingest", "--source", str(raw), "--path", self.PATH,
                          "--owner", "C001", "--commit", self.git_commit())
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("AMETA-001", result.stdout)
        self.assertEqual(len(self.read_table("素材メタデータ")), 1)
        self.assert_rejected(self.check(), "Stale metadata JSON")
        self.assertEqual(self.cli("asset_metadata.py", "build").returncode, 0)
        self.assertEqual(self.check().returncode, 0)
        self.assertIn('"x": 0.75', (self.root / self.PATH).read_text())
        self.assertNotIn("/home/someone", (self.root / self.PATH).read_text())

    def test_works_under_python_optimize(self):
        # assert に頼らない: -O でも不一致を検出する
        (self.root / self.PATH).write_text('{"edited": true}\n')
        import subprocess
        from tests.ledger_test_support import environment
        result = subprocess.run(["uv", "run", "python3", "-O", str(ROOT / "scripts/asset_metadata.py"), "check"],
                                cwd=ROOT, env=environment(self.root), capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
