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
            a = B.argparse.Namespace(bg_id="BG011", image=str(p), out=t, zoomed=False)
            self.assertEqual(B.cmd_check(a), 1)

    def test_check_passes_castle_in_box(self):
        im = B.layout_image(self.L)
        d = ImageDraw.Draw(im)
        for x in (740, 790, 840):
            d.polygon([(x, 85), (x + 20, 5), (x + 40, 85)], fill=(200, 60, 40))
        with tempfile.TemporaryDirectory() as t:
            p = Path(t) / "x.png"
            im.save(p)
            a = B.argparse.Namespace(bg_id="BG011", image=str(p), out=t, zoomed=False)
            self.assertEqual(B.cmd_check(a), 0)




def _png(L, painter):
    im = Image.new("RGB", tuple(L["canvas"]), (90, 60, 40))
    painter(ImageDraw.Draw(im))
    return im


class Mutants(unittest.TestCase):
    """検査の閾値・分岐を変えると落ちること（変異テスト）。"""

    def setUp(self):
        _, self.L = B.load("BG011")
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def run_check(self, im, L=None):
        p = Path(self.tmp.name) / "x.png"
        im.save(p)
        orig = B.load
        if L is not None:
            B.load = lambda bg: (None, L)
        try:
            a = B.argparse.Namespace(bg_id="BG011", image=str(p), out=self.tmp.name, zoomed=False)
            import io, contextlib
            with contextlib.redirect_stdout(io.StringIO()):
                rc = B.cmd_check(a)
            import json
            return rc, json.loads((Path(self.tmp.name) / "report.json").read_text(encoding="utf-8"))
        finally:
            B.load = orig

    def roofs(self, d, xs=(740, 790, 840), top=140):
        for x in xs:
            d.polygon([(x, top + 90), (x + 20, top), (x + 40, top + 90)], fill=(200, 60, 40))

    def test_roof_just_outside_castle_box_tolerance_fails(self):  # M6
        # 枠 x715〜905 の右へ 40px はみ出す（許容30）屋根
        rc, rep = self.run_check(_png(self.L, lambda d: self.roofs(d, xs=(900, 950, 1000))))
        self.assertTrue(any("城の枠" in p for p in rep["problems"]))

    def test_wrong_size_fails(self):  # M7
        rc, rep = self.run_check(Image.new("RGB", (1920, 1080), (90, 60, 40)))
        self.assertFalse(rep["size_ok"])
        self.assertEqual(rc, 1)

    def test_few_red_pixels_means_castle_not_detected(self):  # M8
        def small(d):
            d.rectangle([760, 150, 770, 160], fill=(200, 60, 40))  # 121画素 < 200
        rc, rep = self.run_check(_png(self.L, small))
        self.assertIsNone(rep["castle_roof"])
        self.assertTrue(any("検出できない" in p for p in rep["problems"]))

    def test_empty_layout_stops(self):  # M9
        orig = B.LIO.read
        B.LIO.read = lambda t: [{"背景ID": "BG011", "配置": " "}]
        try:
            with self.assertRaises(SystemExit):
                B.load("BG011")
        finally:
            B.LIO.read = orig

    def test_missing_stage_ref_stops_build(self):
        a = B.argparse.Namespace(bg_id="BG011", stage_ref="/nonexistent/stage.png", out=self.tmp.name)
        with self.assertRaises(SystemExit):
            B.cmd_build(a)


class Boundaries(unittest.TestCase):
    def setUp(self):
        _, self.L = B.load("BG011")

    def rise_problem(self, rise):
        L = copy.deepcopy(self.L)
        L["floor"]["back_right"] = [1560, L["floor"]["back_left"][1] - rise]
        return any("上がり" in p for p in B.pre_check(L))

    def test_rise_35_passes_34_fails(self):
        self.assertFalse(self.rise_problem(35))
        self.assertTrue(self.rise_problem(34))

    def test_touching_edges_are_not_overlap(self):
        self.assertEqual(B.overlap([0, 0, 10, 10], [10, 0, 10, 10]), 0)
        self.assertEqual(B.overlap([0, 0, 10, 10], [0, 10, 10, 10]), 0)
        self.assertGreater(B.overlap([0, 0, 10, 10], [9, 0, 10, 10]), 0)

    def test_item_flush_against_safe_rect_passes(self):
        L = copy.deepcopy(self.L)
        castle = next(i for i in L["items"] if i["kind"] == "castle")
        castle["box"] = [708, 135, 190, 120]  # 敵の枠の右端(708)にちょうど接する
        self.assertFalse(any("enemy" in p for p in B.pre_check(L) if "castle" in p))

    def test_item_outside_frame_is_rejected(self):
        L = copy.deepcopy(self.L)
        castle = next(i for i in L["items"] if i["kind"] == "castle")
        castle["cutoff"] = False
        castle["box"] = [1600, 135, 190, 110]
        self.assertTrue(any("はみ出す" in p for p in B.pre_check(L)))
        castle["box"] = [715, 135, 190, 110 + 900]
        self.assertTrue(any("はみ出す" in p for p in B.pre_check(L)))


class BackEdge(unittest.TestCase):
    def setUp(self):
        _, self.L = B.load("BG011")

    def layout_with_rise(self, rise):
        L = copy.deepcopy(self.L)
        L["floor"]["back_right"] = [1560, L["floor"]["back_left"][1] - rise]
        return L

    def test_measured_rise_of_layout_image(self):
        import numpy as np
        L = self.L
        px = np.asarray(B.layout_image(L), dtype=int)
        rise = B.edge_rise(px, L["floor"])
        self.assertIsNotNone(rise)
        self.assertGreater(rise, 80)  # 割付図は 95px

    def test_small_rise_fails_check(self):
        # take6 のような約20px の上がり: 床の奥の縁を 20px 上がりにした割付図を検査に通す
        L = self.layout_with_rise(20)
        im = B.layout_image(L)
        m = Mutants("test_wrong_size_fails")
        m.setUp()
        rc, rep = m.run_check(im, L)
        m.tmp.cleanup()
        self.assertTrue(any("奥の縁の上がり" in p for p in rep["problems"]))




class Zoom(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.src = Path(self.tmp.name) / "src.png"
        Image.new("RGB", (1672, 941), (10, 20, 30)).save(self.src)

    def run_zoom(self, crop):
        a = B.argparse.Namespace(bg_id="BG011", image=str(self.src), crop=crop, out=str(Path(self.tmp.name) / "o.png"))
        import io, contextlib
        with contextlib.redirect_stdout(io.StringIO()):
            B.cmd_zoom(a)
        return a

    def test_zoom_outputs_canvas_size_and_report(self):
        import json
        a = self.run_zoom("400,362,796,448")
        self.assertEqual(Image.open(a.out).size, (1672, 941))
        rep = json.loads((Path(self.tmp.name) / "zoom-report.json").read_text(encoding="utf-8"))
        self.assertEqual(rep["crop"], [400, 362, 796, 448])
        self.assertAlmostEqual(rep["scale"], 2.1005, places=3)
        self.assertEqual(len(rep["source_sha256"]), 64)

    def test_zoom_keeps_source(self):
        import hashlib
        before = hashlib.sha256(self.src.read_bytes()).hexdigest()
        self.run_zoom("400,362,796,448")
        self.assertEqual(hashlib.sha256(self.src.read_bytes()).hexdigest(), before)

    def test_zoom_rejects_non_16_9(self):
        with self.assertRaises(SystemExit):
            self.run_zoom("400,362,700,448")

    def test_zoom_rejects_crop_outside_image(self):
        with self.assertRaises(SystemExit):
            self.run_zoom("1000,600,796,448")




class ZoomSearch(unittest.TestCase):
    def setUp(self):
        _, self.L = B.load("BG011")

    def test_integral_matches_mean(self):
        import numpy as np
        m = np.zeros((100, 200), dtype=bool)
        m[:, :100] = True
        self.assertAlmostEqual(B.Integral(m).frac([0, 0, 200, 100]), 0.5, places=6)
        self.assertAlmostEqual(B.Integral(m).frac([0, 0, 100, 100]), 1.0, places=6)
        self.assertAlmostEqual(B.Integral(m).frac([150, 0, 50, 100]), 0.0, places=6)

    def test_floor_mask_excludes_sky_green_white_and_dark_face(self):
        import numpy as np
        px = np.zeros((60, 240, 3), dtype=int)
        px[:, 0:60] = (130, 75, 40)    # 床の板
        px[:, 60:120] = (90, 150, 220)  # 青空
        px[:, 120:180] = (40, 100, 50)  # 緑の緞帳
        px[:, 180:240] = (60, 35, 20)   # 前面の濃い板
        m = B.floor_mask(px)
        self.assertTrue(m[:, 10:50].all())
        self.assertFalse(m[:, 70:110].any())
        self.assertFalse(m[:, 130:170].any())
        self.assertFalse(m[:, 190:230].any())

    def test_candidate_is_ok_only_when_every_frame_is_floor(self):
        import numpy as np
        mask = np.ones((941, 1672), dtype=bool)
        integ = B.Integral(mask)
        c = B._candidate(integ, self.L, 1.0, 0, 0)
        self.assertTrue(c["ok"])
        mask[300:420, 940:1100] = False  # 味方1枠の中に床でない物
        c = B._candidate(B.Integral(mask), self.L, 1.0, 0, 0)
        self.assertFalse(c["ok"])
        self.assertIsNone(B._candidate(integ, self.L, 1.0, 100, 0))  # 画像の外へはみ出す枠




class Cutoff(unittest.TestCase):
    def setUp(self):
        _, self.L = B.load("BG011")
        self.castle = next(i for i in self.L["items"] if i["kind"] == "castle")

    def test_cutoff_item_may_leave_the_frame_and_touch_log_band(self):
        self.assertTrue(self.castle.get("cutoff"))
        self.assertLess(self.castle["box"][1], 0)  # 画面の上へはみ出す
        self.assertEqual(B.pre_check(self.L), [])

    def test_non_cutoff_item_may_not_leave_the_frame(self):
        self.castle["cutoff"] = False
        self.assertTrue(any("はみ出す" in p for p in B.pre_check(self.L)))

    def test_cutoff_does_not_excuse_overlap_with_ally_frames(self):
        self.castle["box"] = [950, -40, 190, 200]  # 味方1枠(920,78)に入る
        self.assertTrue(any("ally1" in p for p in B.pre_check(self.L)))

    def test_cutoff_prompt_uses_cut_phrase(self):
        text = B.build_prompt(self.L)
        self.assertIn("画面の上端で見切れて描く", text)

    def test_floor_back_edge_clears_ally1_top(self):
        f = self.L["floor"]
        (x0, y0), (x1, y1) = f["back_left"], f["back_right"]
        y_at_920 = y0 + (y1 - y0) * (920 - x0) / (x1 - x0)
        self.assertLessEqual(y_at_920, 78)  # 奥の縁が味方1枠の上端より上
        self.assertLessEqual(y0, 184.5)  # 左は敵の枠の上端より上




class ObjectInFrames(unittest.TestCase):
    def setUp(self):
        _, self.L = B.load("BG011")

    def test_object_mask_detects_set_colours_not_floor(self):
        import numpy as np
        px = np.zeros((10, 60, 3), dtype=int)
        px[:, 0:10] = (130, 75, 40)    # 床の板
        px[:, 10:20] = (90, 150, 220)  # 青空
        px[:, 20:30] = (40, 100, 50)   # 緑の緞帳
        px[:, 30:40] = (240, 240, 235)  # 白い粘土
        px[:, 40:50] = (200, 60, 40)   # 赤い屋根
        px[:, 50:60] = (60, 35, 20)    # 前面の濃い板
        m = B.object_mask(px)
        self.assertFalse(m[:, 0:10].any())
        self.assertTrue(m[:, 10:50].all())
        self.assertFalse(m[:, 50:60].any())

    def test_candidate_rejected_when_set_object_enters_frame(self):
        import numpy as np
        floor = np.ones((941, 1672), dtype=bool)
        obj = np.zeros((941, 1672), dtype=bool)
        obj[78:120, 930:1000] = True  # 味方1枠(920,78)に城の塔
        c = B._candidate(B.Integral(floor), self.L, 1.0, 0, 0, B.Integral(obj))
        self.assertFalse(c["ok"])
        self.assertGreater(c["object_fraction"]["ally1"], B.OBJ_MAX)
        c = B._candidate(B.Integral(floor), self.L, 1.0, 0, 0, B.Integral(np.zeros_like(obj)))
        self.assertTrue(c["ok"])

    def test_check_zoomed_flags_object_in_frame(self):
        import json, io, contextlib
        im = Image.new("RGB", (1672, 941), (120, 70, 38))
        ImageDraw.Draw(im).rectangle([930, 80, 1000, 130], fill=(240, 240, 235))
        with tempfile.TemporaryDirectory() as t:
            p = Path(t) / "x.png"
            im.save(p)
            a = B.argparse.Namespace(bg_id="BG011", image=str(p), out=t, zoomed=True)
            with contextlib.redirect_stdout(io.StringIO()):
                rc = B.cmd_check(a)
            self.assertEqual(rc, 1)
            rep = json.loads((Path(t) / "report.json").read_text(encoding="utf-8"))
            self.assertTrue(any("舞台セットの物" in p for p in rep["problems"]))


if __name__ == "__main__":
    unittest.main()
