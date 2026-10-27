"""Generation inputs follow canonical YAML and keep proposals/unknowns explicit."""
import json

from tests.ledger_test_support import YamlFixture, row


class ContentQueryTests(YamlFixture):
    def setUp(self):
        super().setUp()
        self.write_table("敵", [row("敵", 敵ID="M008", 名称="大きな敵", 遭遇状態="記録あり")])
        self.write_table("敵サイズ", [row("敵サイズ", サイズ行ID="SZ-001", 敵ID="M008", グリッド種別="2x2")])
        self.write_table("召喚獣", [row("召喚獣", 召喚獣ID="S001", 名称="召喚獣")])
        self.write_table("人物", [row("人物", 人物ID="C001", 呼称="主人公")])
        self.write_table("人物形態", [row("人物形態", 形態ID="FORM-002", 人物ID="C001",
                                         マスターパス="assets/C001-adult.webp"),
                                      row("人物形態", 形態ID="FORM-001", 人物ID="C001",
                                          マスターパス="assets/C001-adult-wheelchair.webp")])
        self.write_table("素材", [row("素材", 素材ID="A-001", 所有者ID="C001", 状態="現存（採否未照合）", パス="assets/C001-adult.webp"),
                                row("素材", 素材ID="A-002", 所有者ID="C001", 状態="採用", パス="assets/C001-adult-wheelchair.webp")])

    def query(self, kind="enemy", ident="M008", *arguments):
        return self.cli("content_ledger.py", "query", kind, ident, "--gate", "--json", *arguments)

    def test_valid_enemy_identity_and_grid_pass(self):
        result = self.query()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["サイズ"][0]["グリッド種別"], "2x2")

    def test_unknown_or_wrong_kind_id_stops(self):
        for kind, ident in (("enemy", "M999"), ("enemy", "S001"), ("character", "M008")):
            with self.subTest(kind=kind, ident=ident):
                self.assert_rejected(self.query(kind, ident), ident)

    def test_invalid_grid_stops(self):
        self.mutate("敵サイズ", lambda values: values[0].update(グリッド種別="garbage-grid"))
        self.assert_rejected(self.query(), "グリッド")

    def test_unresolved_encounter_stops(self):
        self.mutate("敵", lambda values: values[0].update(遭遇状態="未決(要確認)"))
        self.assert_rejected(self.query(), "遭遇状態")

    def test_nonencounter_and_draft_enemy_stop(self):
        for status in ("非遭遇", "ID案・未決"):
            with self.subTest(status=status):
                self.mutate("敵", lambda values: values[0].update(遭遇状態=status))
                self.assert_rejected(self.query())

    def test_missing_grid_and_identity_stop(self):
        self.write_table("敵サイズ", [])
        self.assert_rejected(self.query(), "グリッド")

    def test_missing_character_name_stops(self):
        self.mutate("人物", lambda values: values[0].update(呼称=""))
        self.assert_rejected(self.query("character", "C001", "--form", "FORM-002"), "呼称")

    def test_multiple_sizes_require_selection(self):
        self.mutate("敵サイズ", lambda values: values.append(row("敵サイズ", サイズ行ID="SZ-002", 敵ID="M008", グリッド種別="1x1")))
        self.assert_rejected(self.query(), "--size-row")
        self.assertEqual(self.query("enemy", "M008", "--size-row", "SZ-002").returncode, 0)

    def test_summon_uses_selected_size(self):
        self.mutate("敵サイズ", lambda values: values.append(row("敵サイズ", サイズ行ID="SZ-002", 敵ID="S001", グリッド種別="1x1")))
        result = self.query("summon", "S001", "--size-row", "SZ-002")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["サイズ"][0]["敵ID"], "S001")

    def test_foreign_or_absent_size_stops(self):
        self.assert_rejected(self.query("enemy", "M008", "--size-row", "SZ-999"), "SZ-999")

    def test_character_form_excludes_prefix_sharing_wheelchair_asset(self):
        result = self.query("character", "C001", "--form", "FORM-002")
        self.assertEqual(result.returncode, 0, result.stderr)
        facts = json.loads(result.stdout)
        self.assertEqual(facts["採用素材"], [])
        self.assertEqual([asset["パス"] for asset in facts["採否未照合・参考素材"]], ["assets/C001-adult.webp"])
        self.assertNotIn("wheelchair", result.stdout)

    def test_absent_and_unselected_character_forms_stop(self):
        self.assert_rejected(self.query("character", "C001"), "--form")
        self.assert_rejected(self.query("character", "C001", "--form", "FORM-999"), "FORM-999")

    def test_image_specific_unknown_remains_a_gate(self):
        self.write_table("未決", [row("未決", 未決ID="U-001", 対象テーブル="敵サイズ", 対象ID="SZ-001", キー="形態", 内容="未確認", 状態="未決")])
        self.assert_rejected(self.query(), "U-001")

    def test_gameplay_placement_unknown_does_not_block_sprite(self):
        self.write_table("敵配置", [row("敵配置", 配置ID="PLACE-001", 敵ID="M008", 対象MAP="未決(要確認)")])
        self.write_table("未決", [row("未決", 未決ID="U-001", 対象テーブル="敵配置", 対象ID="PLACE-001", キー="対象MAP", 内容="未確認", 状態="未決")])
        result = self.query()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("未決(要確認)", result.stdout)

    def test_fresh_yaml_decisions_and_long_features_reach_prompt(self):
        sentence = "長い特徴と配色の指定。" * 25 + "最後の必須文。\nパイプ | も残す。"
        self.mutate("敵", lambda values: values[0].update({"特徴(自由記述)": sentence}))
        decisions = [row("決定", 決定ID="D-global", 対象種別="全体", 対象ID="sit-by-me", 状態="有効", 決定の要点="共通の固有文"),
                     row("決定", 決定ID="D-enemy", 対象種別="敵", 対象ID="M008", 状態="有効", 決定の要点="敵の固有文"),
                     row("決定", 決定ID="D-other", 対象種別="敵", 対象ID="M999", 状態="有効", 決定の要点="他の敵"),
                     row("決定", 決定ID="D-retired", 対象種別="敵", 対象ID="M008", 状態="撤回", 決定の要点="撤回された文")]
        self.write_table("決定", decisions)
        result = self.cli("content_ledger.py", "query", "enemy", "M008", "--gate")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(sentence, result.stdout)
        for text in ("共通の固有文", "敵の固有文"):
            self.assertIn(text, result.stdout)
        for text in ("他の敵", "撤回された文"):
            self.assertNotIn(text, result.stdout)

    def test_form_and_material_decisions_follow_selected_form(self):
        self.write_table("決定", [row("決定", 決定ID="D-form", 対象種別="人物形態", 対象ID="FORM-002", 状態="有効", 決定の要点="立位だけ"),
                                row("決定", 決定ID="D-asset", 対象種別="素材", 対象ID="A-001", 状態="有効", 決定の要点="選択素材だけ"),
                                row("決定", 決定ID="D-wheel", 対象種別="人物形態", 対象ID="FORM-001", 状態="有効", 決定の要点="車椅子だけ")])
        result = self.query("character", "C001", "--form", "FORM-002")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual({d["決定ID"] for d in json.loads(result.stdout)["決定"]}, {"D-form", "D-asset"})

    def test_candidate_pattern_stays_labelled_as_proposal(self):
        self.write_table("戦闘パターン案", [row("戦闘パターン案", パターンID="P001", 対象ID="M008", 案="試験案", 採用状態="候補・要確認")])
        result = self.cli("content_ledger.py", "query", "enemy", "M008", "--gate")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("候補/未決。採用済みの決定として使わない", result.stdout)

    def test_public_query_rejects_unknown_yaml_column(self):
        path = self.ledger / "敵.yaml"
        path.write_text(path.read_text() + '  "未知列": "value"\n')
        self.assert_rejected(self.query(), "敵", "未知列")

    def test_public_query_rejects_duplicate_yaml_key(self):
        path = self.ledger / "敵.yaml"
        path.write_text(path.read_text() + '  "名称": "別名"\n')
        self.assert_rejected(self.query(), "敵", "名称")

    def test_public_query_rejects_unquoted_scalar(self):
        for scalar in ("no", "2026-10-24", "001"):
            with self.subTest(scalar=scalar):
                path = self.ledger / "敵.yaml"
                text = path.read_text()
                path.write_text(text.replace('"名称": "大きな敵"', '"名称": ' + scalar))
                self.assert_rejected(self.query(), "敵", "5行目", "引用符")
                path.write_text(text)

    def test_public_query_rejects_nested_yaml_value(self):
        path = self.ledger / "敵.yaml"
        path.write_text(path.read_text().replace('"名称": "大きな敵"', '"名称": {"nested": "value"}'))
        self.assert_rejected(self.query(), "敵", "5行目", "入れ子")

    def test_legacy_markdown_cannot_override_yaml(self):
        (self.root / "docs/monsters.md").write_text("# Old\nM008 obsolete name")
        result = self.query()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("obsolete", result.stdout)
