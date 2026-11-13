"""早期デモ専用の サンプルMAP・サンプル接続 の検査（scripts/verify_domain_ledger.py の check_sample_maps）。

本編の MAP・接続を借りず、流用元の出口を1回ずつつないで行き止まりを作らないことを、最小の fixture で確かめる。
"""
from tests.ledger_test_support import YamlFixture, row


class SampleMapLedgerTests(YamlFixture):
    def verify(self):
        return self.cli("verify_domain_ledger.py")

    def setUp(self):
        super().setUp()
        self.write_table("MAP", [row("MAP", MAP_ID="TRM-A", エリアID="a"), row("MAP", MAP_ID="TRM-B", エリアID="a")])
        self.write_table("端", [
            row("端", 端ID="TRM-A.east", MAP_ID="TRM-A", 種別="縁"),
            row("端", 端ID="TRM-A.hole", MAP_ID="TRM-A", 種別="開口"),
            row("端", 端ID="TRM-B.west", MAP_ID="TRM-B", 種別="縁"),
        ])
        self.write_table("素材", [
            row("素材", 素材ID="A-1", 所有者ID="TRM-A", 種別="背景(基準)", 状態="採用"),
            row("素材", 素材ID="A-2", 所有者ID="TRM-B", 種別="背景(基準)", 状態="採用"),
        ])
        self.write_table("エリア", [row("エリア", エリアID="a")])
        self.write_table("サンプルMAP", [
            row("サンプルMAP", サンプルID="SMP-01", 流用元MAP="TRM-A", エンカウント="なし", 状態="承認済み"),
            row("サンプルMAP", サンプルID="SMP-02", 流用元MAP="TRM-B", エンカウント="なし", 状態="承認済み"),
        ])
        self.write_table("サンプル接続", [
            row("サンプル接続", 通番="01", サンプルA="SMP-01", 出口A="TRM-A.east", サンプルB="SMP-02", 出口B="TRM-B.west"),
        ])

    def test_closed_pair_without_dead_end_passes(self):
        result = self.verify()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_unconnected_port_is_a_dead_end(self):
        self.write_table("サンプル接続", [])
        self.assert_rejected(self.verify(), "行き止まり", "TRM-A.east")

    def test_skipped_port_is_not_a_dead_end_but_cannot_also_be_used(self):
        self.write_table("サンプル接続", [])
        self.mutate("サンプルMAP", lambda rows: rows[0].update(使わない出口="TRM-A.east"))
        self.mutate("サンプルMAP", lambda rows: rows[1].update(使わない出口="TRM-B.west"))
        # 2つのサンプルMAP が孤立するので連結の検査で落ちるが、行き止まりでは落ちない
        result = self.verify()
        self.assert_rejected(result, "連結でない")
        self.assertNotIn("行き止まり", result.stdout + result.stderr)

    def test_port_used_twice_is_rejected(self):
        self.mutate("サンプル接続", lambda rows: rows.append(
            row("サンプル接続", 通番="02", サンプルA="SMP-01", 出口A="TRM-A.east", サンプルB="SMP-02", 出口B="TRM-B.west")))
        self.assert_rejected(self.verify(), "複数の接続に使われている")

    def test_port_of_another_map_is_rejected(self):
        self.mutate("サンプル接続", lambda rows: rows[0].update(出口A="TRM-B.west"))
        self.assert_rejected(self.verify(), "出口A", "流用元 TRM-A")

    def test_sample_id_cannot_collide_with_main_map(self):
        self.mutate("サンプルMAP", lambda rows: rows[0].update(サンプルID="TRM-A"))
        self.mutate("サンプル接続", lambda rows: rows[0].update(サンプルA="TRM-A"))
        self.assert_rejected(self.verify(), "本編の MAP ID と衝突")

    def test_source_without_adopted_background_is_rejected(self):
        self.mutate("素材", lambda rows: rows[0].update(状態="没"))
        self.assert_rejected(self.verify(), "採用済みの背景", "TRM-A")

    def test_disconnected_sample_maps_are_rejected(self):
        self.mutate("サンプルMAP", lambda rows: rows.append(
            row("サンプルMAP", サンプルID="SMP-03", 流用元MAP="TRM-B", エンカウント="なし", 使わない出口="TRM-B.west", 状態="承認済み")))
        self.assert_rejected(self.verify(), "SMP-03", "連結でない")

    def test_encounter_value_and_missing_event_are_rejected(self):
        self.mutate("サンプルMAP", lambda rows: rows[0].update(エンカウント="たまに"))
        self.assert_rejected(self.verify(), "あり/なし")
        self.mutate("サンプルMAP", lambda rows: rows[0].update(エンカウント="なし", 起動イベント="no_such_event"))
        self.assert_rejected(self.verify(), "no_such_event")

    def test_state_outside_vocabulary_is_rejected(self):
        self.mutate("サンプルMAP", lambda rows: rows[0].update(状態="たぶんOK"))
        self.assert_rejected(self.verify(), "サンプルMAP.状態", "SMP-01")

    def test_non_walkable_port_kind_is_rejected(self):
        self.mutate("サンプルMAP", lambda rows: rows[0].update(使わない出口="TRM-A.east"))
        self.mutate("サンプル接続", lambda rows: rows[0].update(出口A="TRM-A.hole"))
        self.assert_rejected(self.verify(), "歩いて出る出口", "TRM-A.hole")

    def test_connection_between_same_sample_map_is_rejected(self):
        self.mutate("サンプル接続", lambda rows: rows[0].update(サンプルB="SMP-01", 出口B="TRM-A.east"))
        self.assert_rejected(self.verify(), "同じサンプルMAP どうし")

    def test_skipped_port_of_another_map_is_rejected(self):
        self.mutate("サンプルMAP", lambda rows: rows[0].update(使わない出口="TRM-B.west"))
        self.assert_rejected(self.verify(), "使わない出口", "流用元 TRM-A")

    def test_port_with_disabled_period_warns_but_passes(self):
        self.write_table("接続", [row("接続", 端A="TRM-A.east", 端B="TRM-X.y", 無効時期='{"TRM-A-fire":"焼失"}')])
        result = self.verify()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("WARN", result.stdout)
        self.assertIn("無効時期", result.stdout)
        self.assertIn("TRM-A.east", result.stdout)

    def test_port_without_disabled_period_does_not_warn(self):
        self.write_table("接続", [row("接続", 端A="TRM-A.east", 端B="TRM-B.west")])
        self.assertNotIn("WARN", self.verify().stdout)
