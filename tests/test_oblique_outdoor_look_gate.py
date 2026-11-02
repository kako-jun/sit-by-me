"""#191: 屋外MAPの建物・塀・門の look 空欄ゲート（現実参照・境界の実体化。決定 SIT.real-reference-boundaries）。

実行: uv run --with pytest --with numpy --with opencv-python-headless --with pillow python3 -m pytest tests/test_oblique_outdoor_look_gate.py
"""
import glob
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".claude/skills/sit-field-background/tools"))
import oblique_build as B  # noqa: E402
import oblique_mock as M  # noqa: E402
import oblique_text as X  # noqa: E402

PLANS = sorted(glob.glob(str(ROOT / "docs/production/oblique-mocks/*-plan.json")))
OUTDOOR_POOL = {"outdoor": True}


def plan(walls=(), boxes=(), floors=()):
    return {"walls": list(walls), "boxes": list(boxes), "floors": list(floors)}


def floor_warns(ws):
    return [w for w in ws if "歩けない面" in w]


class OutdoorLookGate(unittest.TestCase):
    def test_empty_building_and_fence_look_is_error(self):
        p = plan(walls=[{"id": "house", "kind": "building", "look": ""}, {"id": "fence", "kind": "fence"}])
        errs, _ = B.outdoor_look_problems(p, OUTDOOR_POOL)
        self.assertEqual(len(errs), 2)

    def test_empty_gate_box_is_error_but_other_kind_is_not(self):
        p = plan(boxes=[{"id": "gate", "kind": "gate"}, {"id": "bell", "kind": "bell"}])
        errs, _ = B.outdoor_look_problems(p, OUTDOOR_POOL)
        self.assertEqual(len(errs), 1)
        self.assertIn("gate", errs[0])

    def test_filled_look_passes(self):
        p = plan(walls=[{"id": "w", "kind": "fence", "look": "古い土塀。瓦屋根つきで雪が載る"}])
        self.assertEqual(B.outdoor_look_problems(p, OUTDOOR_POOL)[0], [])

    def test_blocked_floor_plain_ground_warns(self):
        for look in ("", "雪に覆われた地面（歩けない部分）"):
            _, w = B.outdoor_look_problems(plan(floors=[{"id": "snow", "walkable": False, "look": look}]), OUTDOOR_POOL)
            self.assertEqual(len(floor_warns(w)), 1, look)

    def test_blocked_floor_without_visual_reason_warns_and_with_reason_does_not(self):
        _, w = B.outdoor_look_problems(plan(floors=[{"id": "s", "walkable": False, "look": "なだらかな雪の庭"}]), OUTDOOR_POOL)
        self.assertEqual(len(floor_warns(w)), 1)
        _, w = B.outdoor_look_problems(plan(floors=[{"id": "s", "walkable": False, "look": "一段高い庭。縁に低い石垣がある"}]), OUTDOOR_POOL)
        self.assertEqual(floor_warns(w), [])

    def test_validate_decor_applies_only_to_outdoor_pools(self):
        p = {"decor_pool": "teramachi-winter-exterior", "boxes": [], "walls": [{"id": "w", "kind": "building", "rect": [0, 0, 100, 100], "h": 50}], "floors": []}
        E, W = [], []
        B.validate_decor(p, E, W)
        self.assertTrue(any("look が空欄" in e for e in E))
        p["decor_pool"] = "teramachi-winter"  # 屋内プールは対象外
        E, W = [], []
        B.validate_decor(p, E, W)
        self.assertFalse(any("look が空欄" in e for e in E))

    def test_approved_maps_are_not_gated(self):
        # look ゲートで落ちないこと（承認・採用の有無とは無関係）。TRM-02/04/05 は屋内でゲート対象外、TRM-03 は屋外だが look が埋まっているので通る
        # （通っても屋外の節〔REALITY・寺町の古木の文・SURFACES 注記〕はプロンプトに載る＝次回再生成で変わる。
        #  SCENERY DOORS・BOUNDARY・VARIATION は TRM-03 の plan にそのキーが無いので出ない）。
        # TRM-12 は『モック承認取り消し→再モック→今日承認』の経緯で、モック承認は最新だが屋内なのでゲート対象外
        for path in PLANS:
            pid = Path(path).name.split("-plan")[0]
            if pid not in ("TRM-02", "TRM-03", "TRM-04", "TRM-05", "TRM-12"):
                continue
            p = M.load_plan(path)
            pool = B.load_decor(p)
            errs = B.outdoor_look_problems(p, pool)[0] if pool and pool.get("outdoor") else []
            self.assertEqual(errs, [], pid)

    def test_unfilled_outdoor_maps_are_gated(self):
        # TRM-06〜17 のうち屋外は look 未記入のため止まる（調査結果を台帳に反映するまで意図どおり）
        gated = []
        for path in PLANS:
            p = M.load_plan(path)
            pool = B.load_decor(p)
            if pool and pool.get("outdoor") and B.outdoor_look_problems(p, pool)[0]:
                gated.append(p["map_id"])
        self.assertIn("TRM-08", gated)

    def test_reality_prompt_text_in_ledger(self):
        t = X.text("PR.reality")
        for w in ("位置の指定にすぎない", "色の違いだけ", "歩けなさそう"):
            self.assertIn(w, t)

    def test_boundaries_and_scenery_doors_need_look(self):
        p = plan(floors=[{"id": "r", "walkable": True}])
        p["boundaries"] = [{"id": "b", "rect": [0, 0, 10, 10], "look": ""}, {"id": "c", "look": "石垣"}]
        p["scenery_doors"] = [{"id": "d", "look": ""}]
        errs, warns = B.outdoor_look_problems(p, OUTDOOR_POOL)
        self.assertEqual(len(errs), 3)
        p2 = plan(floors=[{"id": "r", "walkable": True}])
        _, warns = B.outdoor_look_problems(p2, OUTDOOR_POOL)
        self.assertTrue(any("boundaries" in w for w in warns))
        self.assertTrue(any("variation" in w for w in warns))

    def test_forbid_skip_must_match_pool_forbid(self):
        # 検査は validate_decor の一般部分（屋内プールも対象）
        for pid, n_err in (("teramachi-winter-exterior", 2), ("teramachi-winter", 2)):
            p = M.load_plan(str(ROOT / "docs/production/oblique-mocks/TRM-03-plan.json"))
            p["decor_pool"] = pid
            p["forbid_skip"] = [{"match": "畳", "reason": "屋外"}, {"match": "存在しない", "reason": "x"}, {"match": "畳"}]
            E, W = [], []
            B.validate_decor(p, E, W)
            self.assertEqual(len([e for e in E if "forbid_skip" in e]), n_err, pid)

    def test_forbid_skip_multi_hit_warns(self):
        p = M.load_plan(str(ROOT / "docs/production/oblique-mocks/TRM-03-plan.json"))
        pool = B.load_decor(p)
        word = next(w for w in ("の", "を") if sum(1 for f in pool["forbid"] if w in f) > 1)
        p["forbid_skip"] = [{"match": word, "reason": "x"}]
        E, W = [], []
        B.validate_decor(p, E, W)
        self.assertTrue(any("forbid_skip" in w and "件に一致" in w for w in W))

    def test_tree_zones_area_is_in_pixels(self):
        p = M.load_plan(str(ROOT / "docs/production/oblique-mocks/TRM-03-plan.json"))
        pool = B.load_decor(p)
        # 小さい矩形なら警告が必ず出て、px² の面積（画素へ射影した外接矩形）が文中に出る
        p["tree_zones"] = [{"id": "z", "rect": [0, 0, 10, 10]}]
        bx0, by0, bx1, by1 = B._bbox([M.rect_poly([0, 0, 10, 10])])
        w = B.tree_room_warning(p, pool)
        self.assertIsNotNone(w)
        self.assertIn(f"{(bx1 - bx0) * (by1 - by0)}px²", w)

    def test_tree_zones_large_plan_rect_not_overestimated(self):
        # plan 単位の大きな矩形は画素へ射影して数える。画素の面積が十分なら警告なし（plan 単位の数値のまま数えて過大評価していないことの確認用の下限）
        p = M.load_plan(str(ROOT / "docs/production/oblique-mocks/TRM-03-plan.json"))
        pool = B.load_decor(p)
        p["tree_zones"] = [{"id": "z", "rect": [0, 0, 1600, 100]}]
        bx0, by0, bx1, by1 = B._bbox([M.rect_poly([0, 0, 1600, 100])])
        area = (bx1 - bx0) * (by1 - by0)
        need = pool["trees"]["total"][0] * B.X.const_num("tree.min-area-per-tree")
        w = B.tree_room_warning(p, pool)
        if area >= need:
            self.assertIsNone(w)
        else:
            self.assertIn(f"{area}px²", w)

    def test_tree_band_sizes_without_walls_is_empty(self):
        self.assertEqual(B.tree_band_sizes({"walls": []}), {})
        self.assertIsNone(B.tree_room_warning({"walls": []}, {"trees": {"total": [4, 6]}}))

    def test_scenery_heading_only_when_list_nonempty(self):
        p = M.load_plan(str(ROOT / "docs/production/oblique-mocks/TRM-03-plan.json"))
        p["scenery_doors"] = []
        self.assertNotIn("SCENERY DOORS", "\n".join(B.scenery_sections(p)))
        p["scenery_doors"] = [{"id": "sd", "wall": "x", "look": "閉じた板戸の門"}]
        t = "\n".join(B.scenery_sections(p))
        self.assertIn("SCENERY DOORS", t)
        self.assertNotIn("描いてよい", t)

    def test_tree_size_note_only_in_teramachi_outdoor_pool(self):
        self.assertNotIn("古木", X.text("PR.reality"))
        for mid, want in (("TRM-03", True), ("TRM-02", False)):
            p = M.load_plan(str(ROOT / f"docs/production/oblique-mocks/{mid}-plan.json"))
            self.assertEqual("飛び抜けて高い古木" in B.build_prompt(p, mid), want, mid)

    def test_unknown_plan_key_warns(self):
        p = M.load_plan(str(ROOT / "docs/production/oblique-mocks/TRM-03-plan.json"))
        p["boundries"] = []
        _, W = B.validate_plan(p)
        self.assertTrue(any("boundries" in w for w in W))

    def test_tree_band_zero_width_warns_for_trm08_but_not_trm03(self):
        for mid, expect in (("TRM-08", True), ("TRM-03", False)):
            p = M.load_plan(str(ROOT / f"docs/production/oblique-mocks/{mid}-plan.json"))
            self.assertEqual(bool(B.tree_room_warning(p, B.load_decor(p))), expect, mid)

    def test_outdoor_prompt_has_new_sections_and_forbid_skip(self):
        p = M.load_plan(str(ROOT / "docs/production/oblique-mocks/TRM-03-plan.json"))
        p["boundaries"] = [{"id": "b", "rect": [0, 0, 100, 40], "look": "土塀の根元の石積み"}]
        p["scenery_doors"] = [{"id": "sd", "wall": "x", "look": "閉じた板戸の門"}]
        p["variation"] = ["足跡"]
        p["forbid_skip"] = [{"match": "畳", "reason": "屋外"}]
        t = B.build_prompt(p, "TRM-03")
        for w in ("SCENERY DOORS", "BOUNDARY", "VARIATION", "土塀の根元の石積み", "閉じた板戸の門"):
            self.assertIn(w, t)
        self.assertNotIn("畳（い草", t)


if __name__ == "__main__":
    unittest.main()
