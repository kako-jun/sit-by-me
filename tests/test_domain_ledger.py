"""Normalized families share FK/PK/type checks, independent of full asset data."""
import json
import subprocess

from tests.ledger_test_support import ROOT, L, YamlFixture, environment, row


class DomainLedgerTests(YamlFixture):
    def verify(self, *args):
        return self.cli("verify_domain_ledger.py", *args)

    def test_empty_minimal_fixture_is_structurally_valid(self):
        result = self.verify()
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_new_families_reject_duplicate_primary_keys(self):
        for table in ("制作規約", "MAP仕様", "MAP契約", "敵", "召喚獣", "人物", "人物形態", "刀候補", "能力候補", "BGMスロット", "Issue出典"):
            with self.subTest(table=table):
                key = __import__('ledger_io').SCHEMA[table][0]
                item = row(table, **{key: "DUPLICATE"})
                self.write_table(table, [item, item.copy()])
                self.assert_rejected(self.verify(), table, "重複")
                self.write_table(table, [])

    def test_map_variant_path_is_a_composite_key(self):
        values = [row("体内幾何", 幾何ID="G1", MAP_ID="GLOBAL", 変種="A", 経路="x", 型="数", 値="1"),
                  row("体内幾何", 幾何ID="G2", MAP_ID="GLOBAL", 変種="B", 経路="x", 型="数", 値="2")]
        self.write_table("体内幾何", values)
        result = self.verify()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.mutate("体内幾何", lambda rows: rows[1].update(変種="A"))
        self.assert_rejected(self.verify(), "体内幾何", "重複")

    def test_recording_id_and_movement_must_be_unique(self):
        self.write_table("BGM録音", [row("BGM録音", 録音行ID="REC1", 録音ID="rec", 楽章="1"),
                                    row("BGM録音", 録音行ID="REC2", 録音ID="rec", 楽章="1")])
        self.assert_rejected(self.verify(), "BGM録音", "重複")

    def test_foreign_keys_reject_missing_targets(self):
        cases = [("敵サイズ", "敵ID", "M999"), ("敵配置", "敵ID", "M999"),
                 ("敵配置", "召喚獣ID", "S999"), ("敵配置", "ダンジョンID", "D999"),
                 ("MAP仕様", "MAP_ID", "MAP999"), ("MAP契約", "MAP_ID", "GLOBAL"),
                 ("人物形態", "人物ID", "C999"), ("刀配分案", "刀候補ID", "B999"),
                 ("刀能力配分案", "能力候補ID", "A999"),
                 ("BGMフレーズ", "元録音ID", "REC999"),
                 ("Issue命題", "出典ID", "SOURCE999"), ("Issue命題", "決定ID", "DECISION999"),
                 ("Issue命題", "未決ID", "U-999")]
        for table, key, value in cases:
            with self.subTest(table=table, key=key):
                ident = __import__('ledger_io').SCHEMA[table][0]
                self.write_table(table, [row(table, **{ident: "fixture", key: value})])
                self.assert_rejected(self.verify(), table, value)
                self.write_table(table, [])

    def test_placement_requires_exactly_one_enemy_or_summon(self):
        self.write_table("敵", [row("敵", 敵ID="M001")])
        self.write_table("召喚獣", [row("召喚獣", 召喚獣ID="S001")])
        for enemy, summon in (("", ""), ("M001", "S001")):
            with self.subTest(enemy=enemy, summon=summon):
                self.write_table("敵配置", [row("敵配置", 配置ID="PLACE", 敵ID=enemy, 召喚獣ID=summon)])
                self.assert_rejected(self.verify(), "一方だけ")

    def test_yaml_typed_path_mutation_reaches_verifier(self):
        self.write_table("エリア構造", [row("エリア構造", 経路="list[2]", 型="数", 値="1")])
        self.assert_rejected(self.verify(), "エリア構造", "添字")

    def test_issue_reflected_claim_requires_its_typed_link(self):
        for classification, key in (("決定反映", "決定ID"), ("未決反映", "未決ID"), ("既存台帳参照", "参照先")):
            with self.subTest(classification=classification):
                self.write_table("Issue命題", [row("Issue命題", 命題ID="CLAIM", 分類=classification, 帰属="話者未確定")])
                self.assert_rejected(self.verify(), key)


class EndpointMandatoryGateTests(YamlFixture):
    """Logical travel keeps unknown records without inventing physical walls."""
    ENDPOINT = "TRM-03.event-kiss"

    @classmethod
    def setUpClass(cls):
        # Only the small tables used by the real mandatory-key CLI are needed;
        # never copy source snapshots, images, scripts or project environments.
        names = ("必須キー", "未決", "語彙", "エリア", "MAP", "建物", "端", "窓",
                 "時期差分", "建物時期差分", "接続", "特殊遷移", "装飾プール")
        cls.canonical = {name: L.parse(name, (ROOT / "docs/ledger" / (name + ".yaml")).read_text())
                         for name in names}
        selected = next(r for r in cls.canonical["MAP"] if r["MAP_ID"] == "TRM-03")
        ids = {"TRM-03", selected["エリアID"], *selected["建物ID"].split(";")}
        ids.update(r["端ID"] for r in cls.canonical["端"] if r["MAP_ID"] == "TRM-03")
        cls.canonical["未決"] = [r for r in cls.canonical["未決"] if r["対象ID"] in ids]

    def setUp(self):
        super().setUp()
        for table, values in self.canonical.items():
            self.write_table(table, values)
        self.unknowns = self.read_table("未決")
        self.assertTrue(any(r["対象ID"] == self.ENDPOINT and r["キー"] == "壁側"
                            and r["状態"] == "未決" for r in self.unknowns))

    def port(self, kind, wall="未決(要確認)", **values):
        def change(rows):
            selected = next(r for r in rows if r["端ID"] == self.ENDPOINT)
            selected.update({"種別": kind, "壁側": wall, "幅クラス": "1人分", **values})
        self.mutate("端", change)

    def gate(self):
        return subprocess.run(["ruby", str(ROOT / "scripts/ledger_required_keys.rb"), "TRM-03"],
                              cwd=ROOT, env=environment(self.root), capture_output=True, text=True)

    def reflect_empty_prompt(self, gate):
        path = self.root / "prompt.json"
        path.write_text(json.dumps([{"map_id": "TRM-03", "gated": gate.stdout.splitlines(), "prompt": ""}]))
        return subprocess.run(["ruby", str(ROOT / "scripts/verify_prompt_reflects_ledger.rb"),
                               "--from-json", str(path), "--maps", "TRM-03"],
                              cwd=ROOT, env=environment(self.root), capture_output=True, text=True)

    def test_logical_event_and_travel_keep_unknown_wall_without_gating(self):
        for kind in ("イベント", "移動"):
            with self.subTest(kind=kind):
                self.port(kind)
                result = self.gate()
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertEqual(result.stdout, "")
                self.assertEqual(self.read_table("未決"), self.unknowns)
                selected = next(r for r in self.read_table("端") if r["端ID"] == self.ENDPOINT)
                self.assertEqual(selected["壁側"], "未決(要確認)")

    def test_physical_wall_blank_unknown_and_invalid_vocabulary_still_gate(self):
        for kind in ("戸口", "開口", "抽象通路"):
            for wall in ("", "未決(要確認)", "garbage-wall"):
                with self.subTest(kind=kind, wall=wall):
                    self.port(kind, wall)
                    result = self.gate()
                    self.assert_rejected(result, self.ENDPOINT, "壁側")
                    if wall == "garbage-wall":
                        self.assertIn("語彙", result.stdout)

    def test_boundary_edge_does_not_require_a_wall_side(self):
        self.port("縁")
        result = self.gate()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_logical_event_and_travel_still_require_their_peer(self):
        for kind in ("イベント", "移動"):
            with self.subTest(kind=kind):
                self.port(kind, 相手端="")
                self.assert_rejected(self.gate(), self.ENDPOINT, "相手端")

    def test_physical_door_still_requires_width(self):
        self.port("戸口", "北", 幅クラス="未決(要確認)")
        self.write_table("未決", self.unknowns + [row("未決", 未決ID="U-fixture-width",
                          対象テーブル="端", 対象ID=self.ENDPOINT, キー="幅クラス", 内容="幅を確認する", 状態="未決")])
        self.assert_rejected(self.gate(), self.ENDPOINT, "幅クラス")

    def test_trm03_logical_event_reenters_both_real_regression_anchors(self):
        self.port("イベント")
        gate = self.gate()
        self.assertEqual(gate.returncode, 0, gate.stdout + gate.stderr)
        # An intentionally empty prompt must reach both TRM-03 anchors and fail
        # for missing content; it must never be silently skipped as gated.
        result = self.reflect_empty_prompt(gate)
        self.assert_rejected(result, "回帰アンカー tatami", "回帰アンカー corridor-windows")
        self.assertIn("検査したMAP（1）: TRM-03", result.stdout)
        self.assertNotIn("このMAPがゲートで止まっていて検査できない", result.stderr)

    def test_trm03_physical_unknown_does_not_exempt_regression_anchors(self):
        self.port("戸口")
        gate = self.gate()
        self.assert_rejected(gate, self.ENDPOINT, "壁側")
        result = self.reflect_empty_prompt(gate)
        self.assert_rejected(result, "回帰アンカー tatami", "回帰アンカー corridor-windows",
                             "このMAPがゲートで止まっていて検査できない")
