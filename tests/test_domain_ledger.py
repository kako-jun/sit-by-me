"""Normalized families share FK/PK/type checks, independent of full asset data."""
from ledger_test_support import YamlFixture, row


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
