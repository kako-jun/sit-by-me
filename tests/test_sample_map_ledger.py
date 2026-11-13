"""早期デモ専用の サンプルMAP（1マップ）の検査（scripts/verify_domain_ledger.py の check_sample_maps）。

本編の MAP を借りず、流用元の採用済み背景・歩行マスク・起動イベントの実在を最小の fixture で確かめる。
"""
from tests.ledger_test_support import YamlFixture, row


class SampleMapLedgerTests(YamlFixture):
    def verify(self):
        return self.cli("verify_domain_ledger.py")

    def setUp(self):
        super().setUp()
        self.write_table("MAP", [row("MAP", MAP_ID="TRM-A", エリアID="a")])
        self.write_table("素材", [
            row("素材", 素材ID="A-1", 所有者ID="TRM-A", 種別="背景(基準)", 状態="採用"),
            row("素材", 素材ID="A-2", 所有者ID="TRM-A", 種別="マスク", パス="docs/ledger/決定.yaml", 状態="参照専用"),
        ])
        self.write_table("エリア", [row("エリア", エリアID="a")])
        self.write_table("サンプルMAP", [
            row("サンプルMAP", サンプルID="SMP-01", 流用元MAP="TRM-A", エンカウント="なし", 状態="採用"),
        ])

    def test_single_sample_map_passes(self):
        result = self.verify()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_sample_id_cannot_collide_with_main_map(self):
        self.mutate("サンプルMAP", lambda rows: rows[0].update(サンプルID="TRM-A"))
        self.assert_rejected(self.verify(), "本編の MAP ID と衝突")

    def test_source_without_adopted_background_is_rejected(self):
        self.mutate("素材", lambda rows: rows[0].update(状態="没"))
        self.assert_rejected(self.verify(), "採用済みの背景", "TRM-A")

    def test_source_without_existing_walk_mask_is_rejected(self):
        self.mutate("素材", lambda rows: rows[1].update(パス="no/such/mask.webp"))
        self.assert_rejected(self.verify(), "歩行マスク", "TRM-A")

    def test_encounter_value_and_missing_event_are_rejected(self):
        self.mutate("サンプルMAP", lambda rows: rows[0].update(エンカウント="たまに"))
        self.assert_rejected(self.verify(), "あり/なし")
        self.mutate("サンプルMAP", lambda rows: rows[0].update(エンカウント="なし", 起動イベント="no_such_event"))
        self.assert_rejected(self.verify(), "no_such_event")

    def test_unknown_battle_background_is_rejected(self):
        self.mutate("サンプルMAP", lambda rows: rows[0].update(戦闘背景="BG999"))
        self.assert_rejected(self.verify(), "サンプルMAP.戦闘背景", "BG999")

    def test_state_outside_vocabulary_is_rejected(self):
        self.mutate("サンプルMAP", lambda rows: rows[0].update(状態="たぶんOK"))
        self.assert_rejected(self.verify(), "サンプルMAP.状態", "SMP-01")
