"""戦闘背景の送信文・割付図の生成と検査（.claude/skills/sit-battle-background/tools/battle_bg_build.py）の検査。

実行: uv run --with pillow --with numpy python3 -m unittest tests.test_battle_bg_build
"""
import copy
import sys
import tempfile
import unittest
from pathlib import Path

REAL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REAL / ".claude/skills/sit-battle-background/tools"))
import battle_bg_build as B  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402


class Build(unittest.TestCase):
    def setUp(self):
        _, self.L = B.load("BG011")

    def test_ledger_layout_passes_pre_check(self):
        self.assertEqual(B.pre_check(self.L), [])

    def test_object_on_safe_rect_is_rejected(self):
        L = copy.deepcopy(self.L)
        castle = next(i for i in L["items"] if i["kind"] == "castle")
        castle["box"] = [270, 110, 250, 235]  # take4 の城: 敵の枠に被る
        self.assertTrue(any("enemy" in p for p in B.pre_check(L)))

    def test_non_object_may_overlap_safe_rect(self):
        # 書き割り・前面は安全矩形に重なってよい（物ではない）
        self.assertTrue(any(i["kind"] == "front_board" and not i["object"] for i in self.L["items"]))
        self.assertEqual(B.pre_check(self.L), [])

    def test_back_edge_must_rise_to_the_right(self):
        L = copy.deepcopy(self.L)
        L["floor"]["back_right"] = [1560, 290]
        self.assertTrue(any("上がり" in p for p in B.pre_check(L)))

    def test_prompt_lists_every_object_range_and_no_forbidden_words(self):
        text = B.build_prompt(self.L)
        for it in self.L["items"]:
            if it["object"]:
                self.assertIn(it["名"], text)
        for bad in ("テープ", "糊", "ノリ"):
            self.assertNotIn(bad, text)

    def test_layout_image_size(self):
        self.assertEqual(B.layout_image(self.L).size, tuple(self.L["canvas"]))

    def test_check_flags_castle_in_enemy_rect(self):
        im = Image.new("RGB", tuple(self.L["canvas"]), (90, 60, 40))
        d = ImageDraw.Draw(im)
        d.polygon([(300, 250), (330, 150), (360, 250)], fill=(200, 60, 40))  # 敵の枠の中に赤い屋根
        with tempfile.TemporaryDirectory() as t:
            p = Path(t) / "x.png"
            im.save(p)
            a = B.argparse.Namespace(bg_id="BG011", image=str(p), out=t)
            self.assertEqual(B.cmd_check(a), 1)

    def test_check_passes_castle_in_box(self):
        im = Image.new("RGB", tuple(self.L["canvas"]), (90, 60, 40))
        d = ImageDraw.Draw(im)
        for x in (740, 790, 840):
            d.polygon([(x, 230), (x + 20, 140), (x + 40, 230)], fill=(200, 60, 40))
        with tempfile.TemporaryDirectory() as t:
            p = Path(t) / "x.png"
            im.save(p)
            a = B.argparse.Namespace(bg_id="BG011", image=str(p), out=t)
            self.assertEqual(B.cmd_check(a), 0)


if __name__ == "__main__":
    unittest.main()
