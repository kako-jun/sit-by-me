"""#191: 戸口なし・外周の南北端に壁なしの屋外MAPで、斜めツールが空列 max() で落ちない回帰テスト。

小さな合成 plan だけで検証する（生成済み plan・台帳の MAP 行に依存しない）。
実行: uv run --with pytest --with numpy --with opencv-python-headless --with pillow python3 -m pytest tests/test_oblique_empty_edges.py
"""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".claude/skills/sit-field-background/tools"))
import oblique_build as B  # noqa: E402
import oblique_text as X  # noqa: E402
import oblique_topology as T  # noqa: E402

POOL = {"trees": {"total": [8, 12], "pine": {"count": [6, 8]}, "deadtree": {"count": [2, 4]}}}


def wall(wid, rect, h=40):
    return {"id": wid, "rect": rect, "h": h, "kind": "fence", "label": wid}


def plan(walls):
    return {"walls": walls, "floors": [], "doors": [], "windows": [], "boxes": []}


def top_head(hb, hf):
    """PR.coord.top の文頭（高さを述べる括弧の終わりまで）。座標は別なので高さの部分だけ比べる。"""
    head = X.text("PR.coord.top", hb=hb, hf=hf, pts="")
    return head[:head.index("）") + 1]


class ObliqueEmptyEdges(unittest.TestCase):
    def test_width_text_without_doors_returns_ledger_text(self):
        # 戸口なしの屋外MAP（出入りは端マーカーだけ）。空列 max() で落ちず台帳文を返す
        self.assertEqual(T.width_text([]), X.text("TP.width-none"))

    def coord(self, walls):
        return "\n".join(B.coord_section(plan(walls), POOL))

    def test_no_horizontal_wall_on_north_or_south_edge_uses_zero_height(self):
        # 縦長の壁だけ（外周の北端・南端に接する横長の壁なし）: hb=hf=0 で節が出る
        out = self.coord([wall("w-l", [0, 0, 20, 1000]), wall("w-r", [980, 0, 1000, 1000])])
        self.assertIn(top_head(0, 0), out)

    def test_north_wall_only_keeps_hb_and_defaults_hf_to_zero(self):
        # 北端にだけ横長の壁（南端なし）: hf の default=0 を縛る
        out = self.coord([wall("w-n", [0, 0, 1000, 20], h=40), wall("w-l", [0, 20, 20, 1000])])
        self.assertIn(top_head(40, 0), out)

    def test_south_wall_only_keeps_hf_and_defaults_hb_to_zero(self):
        # 南端にだけ横長の壁（北端なし）: hb の default=0 を縛る
        out = self.coord([wall("w-s", [0, 980, 1000, 1000], h=40), wall("w-l", [0, 0, 20, 980])])
        self.assertIn(top_head(0, 40), out)


if __name__ == "__main__":
    unittest.main()
