"""#191: 戸口なし・外周南端に壁なしの屋外MAPで、斜めツールが空列 max() で落ちない回帰テスト。

実行: uv run --with pytest --with numpy --with opencv-python-headless --with pillow python3 -m pytest tests/test_oblique_empty_edges.py
"""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".claude/skills/sit-field-background/tools"))
import oblique_build as B  # noqa: E402
import oblique_mock as M  # noqa: E402
import oblique_text as X  # noqa: E402
import oblique_topology as T  # noqa: E402

MOCKS = ROOT / "docs/production/oblique-mocks"


class ObliqueEmptyEdges(unittest.TestCase):
    def test_width_text_without_doors_returns_ledger_text(self):
        # TRM-07 は戸口なしの屋外MAP（端マーカーのみ）。空列 max() で落ちず台帳文を返す
        self.assertEqual(M.load_plan(str(MOCKS / "TRM-07-plan.json"))["doors"], [])
        self.assertEqual(T.width_text([]), X.text("TP.width-none"))

    def test_coord_section_without_south_edge_wall_uses_zero_height(self):
        # TRM-11 は外周南端に接する横長の壁が無い。内観分岐（building 無し）に通し、手前壁の高さ0で節が出る
        p = M.load_plan(str(MOCKS / "TRM-11-plan.json"))
        ws = p["walls"]
        y0, y1 = min(w["rect"][1] for w in ws), max(w["rect"][3] for w in ws)
        self.assertFalse([w for w in ws if M.is_h(w) and w["rect"][3] == y1])
        for w in ws:
            if w.get("kind") == "building":
                w["kind"] = "fence"
        hb = max(w["h"] for w in ws if M.is_h(w) and w["rect"][1] == y0)
        head = X.text("PR.coord.top", hb=hb, hf=0, pts="")
        head = head[:head.index("）") + 1]
        out = "\n".join(B.coord_section(p, B.load_decor(p)))
        self.assertIn(head, out)


if __name__ == "__main__":
    unittest.main()
