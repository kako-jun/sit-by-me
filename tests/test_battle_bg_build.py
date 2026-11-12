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
        # 書き割り（物ではない）は安全矩形に重なってよい
        self.assertTrue(any(i["kind"] == "backdrop" and not i["object"] for i in self.L["items"]))
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

    def test_floor_mask_excludes_sky_green_white_and_black(self):
        import numpy as np
        px = np.zeros((60, 240, 3), dtype=int)
        px[:, 0:60] = (130, 75, 40)    # 床の板
        px[:, 60:120] = (90, 150, 220)  # 青空
        px[:, 120:180] = (40, 100, 50)  # 緑の緞帳
        px[:, 180:240] = (20, 20, 20)   # 黒（床でも物でもない）
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
        px[:, 50:60] = (60, 35, 20)    # 濃い茶（物ではない）
        m = B.object_mask(px)
        self.assertFalse(m[:, 0:10].any())
        self.assertTrue(m[:, 10:50].all())
        hl = np.zeros((4, 4, 3), dtype=int)
        hl[:] = (209, 122, 63)  # 木の橙色のハイライト（物ではない）
        self.assertFalse(B.object_mask(hl).any())
        gold = np.zeros((4, 4, 3), dtype=int)
        gold[:] = (222, 172, 44)  # 金の房（物）
        self.assertTrue(B.object_mask(gold).all())
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




class FloorGeometry(unittest.TestCase):
    def setUp(self):
        _, self.L = B.load("BG011")

    def test_every_frame_corner_is_inside_the_floor_quad(self):
        self.assertEqual([p for p in B.pre_check(self.L) if "床の四角形" in p], [])

    def test_old_floor_with_right_edge_inside_ally4_corner_is_rejected(self):
        L = copy.deepcopy(self.L)
        L["floor"]["back_right"] = [1560, 0]
        L["floor"]["front_right"] = [1672, 840]  # y=483 で x≈1624 < 味方4枠の右端 1656
        probs = [p for p in B.pre_check(L) if "床の四角形" in p]
        self.assertTrue(any("ally4" in p and "右上" in p for p in probs))

    def test_point_in_quad(self):
        quad = [(0, 0), (10, 0), (10, 10), (0, 10)]
        self.assertTrue(B.point_in_quad((5, 5), quad))
        self.assertTrue(B.point_in_quad((10, 10), quad))  # 辺上・角は内側
        self.assertFalse(B.point_in_quad((10.5, 5), quad))


class ZoomRatio(unittest.TestCase):
    def test_every_candidate_crop_passes_zoom_ratio_check(self):
        _, L = B.load("BG011")
        W, H = L["canvas"]
        import numpy as np
        integ = B.Integral(np.ones((H, W), dtype=bool))
        for k in range(100, 400):
            sc = k / 100
            c = B._candidate(integ, L, sc, 0, 0, B.Integral(np.zeros((H, W), dtype=bool)))
            if c is None:
                continue
            w, h = c["crop"][2], c["crop"][3]
            self.assertTrue(B.crop_ratio_ok(w, h, W, H), (sc, w, h))

    def test_ratio_check_rejects_wrong_aspect(self):
        self.assertFalse(B.crop_ratio_ok(700, 448, 1672, 941))
        self.assertTrue(B.crop_ratio_ok(796, 448, 1672, 941))


class Survivors(unittest.TestCase):
    def test_zoomed_check_floor_threshold_94_fails_96_passes(self):
        import json, io, contextlib
        _, L = B.load("BG011")
        for band, expect in ((19, 1), (12, 0)):  # 枠の上端に黒（物でも床でもない）の帯。19px→床94.1%（NG）、12px→96.3%（合格）
            im = Image.new("RGB", (1672, 941), (120, 70, 38))
            x, y, w, h = next(r["box"] for r in L["safe_rects"] if r["id"] == "ally2")
            ImageDraw.Draw(im).rectangle([x, y, x + w - 1, y + band - 1], fill=(20, 20, 20))
            with tempfile.TemporaryDirectory() as t:
                p = Path(t) / "x.png"
                im.save(p)
                a = B.argparse.Namespace(bg_id="BG011", image=str(p), out=t, zoomed=True)
                with contextlib.redirect_stdout(io.StringIO()):
                    rc = B.cmd_check(a)
                self.assertEqual(rc, expect, band)

    def test_zoom_uses_lanczos_not_nearest(self):
        import numpy as np
        with tempfile.TemporaryDirectory() as t:
            rng = np.random.default_rng(1)
            src = Path(t) / "s.png"
            Image.fromarray(rng.integers(0, 255, (941, 1672, 3), dtype="uint8")).save(src)
            a = B.argparse.Namespace(bg_id="BG011", image=str(src), crop="400,300,796,448", out=str(Path(t) / "sub" / "o.png"))
            import io, contextlib
            with contextlib.redirect_stdout(io.StringIO()):
                B.cmd_zoom(a)  # 出力先の親ディレクトリも作る
            out = np.asarray(Image.open(a.out), dtype=int)
            im = Image.open(src).convert("RGB").crop((400, 300, 1196, 748))
            lan = np.asarray(im.resize((1672, 941), Image.LANCZOS), dtype=int)
            near = np.asarray(im.resize((1672, 941), Image.NEAREST), dtype=int)
            self.assertTrue((out == lan).all())
            self.assertFalse((out == near).all())




class NoFrontEdge(unittest.TestCase):
    def setUp(self):
        _, self.L = B.load("BG011")

    def test_layout_has_no_front_items_and_floor_runs_off_the_bottom(self):
        self.assertFalse(any(i["kind"].startswith("front") for i in self.L["items"]))
        f = self.L["floor"]
        self.assertGreater(f["front_left"][1], self.L["canvas"][1])  # 前縁は画面の外
        self.assertGreater(f["front_right"][1], self.L["canvas"][1])

    def test_prompt_has_floor_line_direction_and_no_front_edge_words(self):
        text = B.build_prompt(self.L)
        self.assertIn("奥の縁と同じく右へ上がる向き", text)
        self.assertIn("手前でも水平にしない", text)
        for bad in ("前縁は", "前面の濃茶", "段ボールの断面", "床と前面", "板の前面", "前面は"):
            self.assertNotIn(bad, text)

    def test_windows_corners_must_be_inside_floor_quad(self):
        L = copy.deepcopy(self.L)
        L["floor"]["front_left"] = [0, 840]
        L["floor"]["front_right"] = [1800, 840]  # 水平な前縁を窓の位置に置くと窓の下側が床の外
        self.assertTrue(any(p.startswith("枠 status") or p.startswith("枠 cmd") for p in B.pre_check(L)))

    def test_check_zoomed_requires_floor_only_in_window_frames(self):
        import json, io, contextlib
        im = Image.new("RGB", (1672, 941), (120, 70, 38))
        x, y, w, h = next(r["box"] for r in self.L["safe_rects"] if r["id"] == "status")
        ImageDraw.Draw(im).rectangle([x + 100, y + 20, x + 160, y + 80], fill=(240, 240, 235))
        with tempfile.TemporaryDirectory() as t:
            p = Path(t) / "x.png"
            im.save(p)
            a = B.argparse.Namespace(bg_id="BG011", image=str(p), out=t, zoomed=True)
            with contextlib.redirect_stdout(io.StringIO()):
                rc = B.cmd_check(a)
            self.assertEqual(rc, 1)
            rep = json.loads((Path(t) / "report.json").read_text(encoding="utf-8"))
            self.assertTrue(any("status" in p for p in rep["problems"]))




class DrawOffset(unittest.TestCase):
    def setUp(self):
        _, self.L = B.load("BG011")

    def test_offset_is_interpolated_between_measured_points_and_clamped(self):
        o = self.L["描画オフセット"]
        self.assertEqual(B.draw_offset(self.L, o["x_left"]), o["dy_left"])
        self.assertEqual(B.draw_offset(self.L, o["x_right"]), o["dy_right"])
        mid = B.draw_offset(self.L, (o["x_left"] + o["x_right"]) / 2)
        self.assertAlmostEqual(mid, (o["dy_left"] + o["dy_right"]) / 2)
        self.assertEqual(B.draw_offset(self.L, 0), o["dy_left"])      # 左の外は左の値
        self.assertEqual(B.draw_offset(self.L, 1672), o["dy_right"])  # 右の外は右の値

    def test_no_offset_leaves_layout_unchanged(self):
        L = copy.deepcopy(self.L)
        del L["描画オフセット"]
        C = B.corrected_layout(L)
        self.assertEqual(C["floor"]["back_left"], L["floor"]["back_left"])
        self.assertEqual(B.draw_offset(L, 500), 0.0)

    def test_corrected_layout_moves_edge_up_and_keeps_ledger_untouched(self):
        before = copy.deepcopy(self.L)
        C = B.corrected_layout(self.L)
        self.assertEqual(self.L, before)  # 台帳の値（狙い）は変えない
        o = self.L["描画オフセット"]
        self.assertLess(C["floor"]["back_left"][1], self.L["floor"]["back_left"][1])
        self.assertAlmostEqual(self.L["floor"]["back_left"][1] - C["floor"]["back_left"][1], B.draw_offset(self.L, self.L["floor"]["back_left"][0]), delta=1)
        self.assertAlmostEqual(self.L["floor"]["back_right"][1] - C["floor"]["back_right"][1], o["dy_right"], delta=1)
        # 前の2点（画面外の下）は動かさない
        self.assertEqual(C["floor"]["front_left"], self.L["floor"]["front_left"])

    def test_cutoff_items_keep_min_visible_and_backdrop_follows_edge(self):
        C = B.corrected_layout(self.L)
        mv = self.L["描画オフセット"]["min_visible"]
        for it in C["items"]:
            if it.get("cutoff") and it["kind"] != "backdrop":
                self.assertGreaterEqual(it["box"][1] + it["box"][3], mv)
        orig = next(i for i in self.L["items"] if i["kind"] == "backdrop")
        moved = next(i for i in C["items"] if i["kind"] == "backdrop")
        self.assertLess(moved["box"][1], orig["box"][1])

    def test_build_sends_corrected_but_checks_ledger_values(self):
        with tempfile.TemporaryDirectory() as t:
            ref = Path(t) / "r.png"
            Image.new("RGB", (10, 10)).save(ref)
            a = B.argparse.Namespace(bg_id="BG011", stage_ref=str(ref), out=t)
            import io, contextlib
            with contextlib.redirect_stdout(io.StringIO()):
                B.cmd_build(a)
            sent = (Path(t) / "send.txt").read_text(encoding="utf-8")
            self.assertIn("y=0〜40", sent)  # 城は min_visible=40 で残る（台帳の y1=90 ではない）
            self.assertEqual(Image.open(Path(t) / "layout.png").size, tuple(self.L["canvas"]))




import numpy as np  # noqa: E402


class RealColours(unittest.TestCase):
    """採用済み TRM-02 の実画像の色で、屋根・ランタンの検出と木のハイライトの除外を確かめる。"""

    def trm02(self):
        import numpy as np
        im = Image.open(REAL / "assets/images/fields/reference/teramachi-kindergarten-playroom-trm02-adopted.webp").convert("RGB")
        return np.asarray(im, dtype=int)

    def test_real_roof_colours_are_objects_and_wood_highlight_is_not(self):
        import numpy as np
        for rgb in ((225, 110, 59), (216, 88, 48), (200, 94, 55)):  # TRM-02 の屋根の実色
            px = np.array([[rgb]], dtype=int)
            self.assertTrue(B.red_roof_mask(px).all(), rgb)
            self.assertTrue(B.object_mask(px).all(), rgb)
        for rgb in ((209, 122, 63), (218, 179, 148), (130, 75, 40)):  # 木の橙ハイライト・淡い桃色・床
            self.assertFalse(B.object_mask(np.array([[rgb]], dtype=int)).any(), rgb)

    def test_real_lantern_brass_is_gold(self):
        import numpy as np
        self.assertTrue(B.gold_mask(np.array([[(207, 143, 74)]], dtype=int)).all())  # TRM-02 のランタンの真鍮の中央値
        self.assertFalse(B.gold_mask(np.array([[(209, 122, 63)]], dtype=int)).any())  # 木のハイライト（g/r≈0.58）

    def test_trm02_castle_roof_coverage_is_at_least_half(self):
        px = self.trm02()[200:290, 760:915]  # 城の屋根を含む範囲
        r, g, b = px[..., 0], px[..., 1], px[..., 2]
        roofish = (r > 150) & (r - g > 60) & (r - b > 80)  # 屋根らしい赤みの画素（基準）
        self.assertGreater(roofish.sum(), 500)
        self.assertGreater(B.red_roof_mask(px)[roofish].mean(), 0.5)  # 旧基準は9%だった

    def test_trm02_lantern_warm_pixels_are_partly_gold(self):
        px = self.trm02()[205:275, 603:630]
        r, b = px[..., 0], px[..., 2]
        warm = (r > 170) & (r - b > 80)
        self.assertGreater(B.gold_mask(px)[warm].mean(), 0.4)

    def test_synthetic_floor_with_highlights_has_few_false_positives(self):
        import numpy as np
        rng = np.random.default_rng(3)
        base = np.array([120, 70, 38])
        floor = np.clip(base + rng.integers(-25, 26, (200, 300, 3)), 0, 255)
        hl = rng.random((200, 300)) < 0.05  # 5% が橙ハイライト (g/r≈0.58)
        floor[hl] = (209, 122, 63)
        self.assertLess(B.object_mask(floor).mean(), 0.005)




class RoadBackground(unittest.TestCase):
    """BG012（寺町の道路）: BG011 を継承し、地面は道路、文面・見本・描画オフセットは BG012 固有。"""

    def setUp(self):
        _, self.L = B.load("BG012")
        _, self.B11 = B.load("BG011")

    def test_inherits_safe_rects_and_floor_from_bg011(self):
        self.assertEqual(self.L["safe_rects"], self.B11["safe_rects"])
        self.assertEqual(self.L["floor"], self.B11["floor"])
        self.assertEqual(self.L["canvas"], self.B11["canvas"])

    def test_own_draw_offset_is_not_inherited(self):
        self.assertNotEqual(self.L["描画オフセット"], self.B11["描画オフセット"])
        self.assertGreater(self.L["描画オフセット"]["dy_left"], self.B11["描画オフセット"]["dy_left"])

    def test_pre_check_passes_and_prompt_is_a_snow_road_without_snow_melting_holes(self):
        self.assertEqual(B.pre_check(self.L), [])
        text = B.build_prompt(B.corrected_layout(self.L))
        self.assertIn("雪道", text)
        self.assertIn("足跡", text)
        for bad in ("舞台", "緞帳", "城", "消雪", "金属", "穴", "融雪"):  # kako-jun「雪道でいいのでは」: 穴・金属蓋は描かない
            self.assertNotIn(bad, text)

    def test_snow_ground_mask_counts_white_and_grey_snow_not_objects(self):
        import numpy as np
        px = np.zeros((4, 4, 3), dtype=int)
        for rgb in ((235, 238, 240), (150, 155, 165)):  # 綿の雪・雪の影
            px[:] = rgb
            self.assertTrue(B.floor_mask(px, "snow").all(), rgb)
            self.assertFalse(B.object_mask(px, "snow").any(), rgb)
        for rgb in ((225, 190, 120), (80, 80, 92), (90, 150, 220), (40, 100, 50)):  # 土塀・瓦・青・緑
            px[:] = rgb
            self.assertFalse(B.floor_mask(px, "snow").any(), rgb)
            self.assertTrue(B.object_mask(px, "snow").all(), rgb)

    def test_draw_offset_matches_the_measured_values(self):
        o = self.L["描画オフセット"]
        self.assertEqual((o["x_left"], o["dy_left"], o["x_right"], o["dy_right"]), (100, 260, 1500, 93))

    def test_wall_is_sloped_and_its_visible_height_is_clamped_in_the_prompt(self):
        C = B.corrected_layout(self.L)
        wall = next(i for i in C["items"] if i["kind"] == "wall")
        orig = next(i for i in self.L["items"] if i["kind"] == "wall")
        self.assertEqual(wall["box"][3], orig["box"][3])  # 下端の高さは変えず、全体を上へ寄せる（SLOPED）
        self.assertLess(wall["box"][1], orig["box"][1])
        self.assertIn("古い土塀（紙粘土のひび割れた面）と戸室石の基礎: x=120〜1560 の範囲に、画面の上端で見切れて描く。画面に見えるのは y=0〜40 の部分だけ。", B.build_prompt(C))

    def test_ref_sheet_is_built_from_ledger_spec(self):
        with tempfile.TemporaryDirectory() as t:
            a = B.argparse.Namespace(bg="BG012", out=str(Path(t) / "r.png"))
            import io, contextlib
            with contextlib.redirect_stdout(io.StringIO()):
                B.cmd_ref(a)
            spec = self.L["参照見本"]
            self.assertEqual(Image.open(a.out).size, (spec["sheet_w"], spec["tile_h"] * spec["rows"]))

    def test_check_without_castle_does_not_crash(self):
        import io, contextlib
        im = Image.new("RGB", (1672, 941), (235, 238, 240))  # 雪道
        with tempfile.TemporaryDirectory() as t:
            p = Path(t) / "x.png"
            im.save(p)
            a = B.argparse.Namespace(bg_id="BG012", image=str(p), out=t, zoomed=True)
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(B.cmd_check(a), 0)




class BlueThreshold(unittest.TestCase):
    def test_blue_object_boundary_is_r_plus_25(self):
        import numpy as np
        px = np.array([[(100, 100, 125), (100, 100, 126), (130, 120, 160)]], dtype=int)
        m = B.object_mask(px)
        self.assertFalse(m[0, 0])  # b=r+25 はまだ物でない（わずかに青い灰色のアスファルトなど）
        self.assertTrue(m[0, 1])   # b=r+26 は青（空）
        self.assertTrue(m[0, 2])


if __name__ == "__main__":
    unittest.main()
