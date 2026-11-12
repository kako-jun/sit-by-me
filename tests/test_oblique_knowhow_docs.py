"""道路系のノウハウが作成スキル（pitfalls.md）とレビュー側（sit-artifact-redteam）に残っていることを縛る（消えたら落ちる）。"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
PIT = (ROOT / ".claude/skills/sit-field-background/pitfalls.md").read_text()
RED = (ROOT / ".claude/skills/sit-artifact-redteam/SKILL.md").read_text()

MAKE = ["SIT.no-power-lines", "SIT.shosetsu-hole-only", "SIT.scenery-door-not-enterable", "EXTRA_REFS", "TRM.canal-continuity", "SIT.base-edge-decor-random",
        "#e4ded2", "pink_whole", "size_exact", "リサイズで通さない", "oblique_e2_schedule.py stale", "--relativize", "スキルに無い手順で作らない", "同時2件"]
REVIEW = ["派生物の古さ", "台帳の単一正本", "変異テスト", "目視適合表", "リサイズ", "絶対パス", "スキル外の手順"]


class KnowHow(unittest.TestCase):
    def test_creation_skill_has_road_knowhow(self):
        i = PIT.index("## H. 道路系（oblique）")
        sec = PIT[i:]
        for k in MAKE:
            self.assertIn(k, sec, k)

    def test_review_skill_has_road_viewpoints(self):
        i = RED.index("## 道路系（oblique）の追加観点")
        sec = RED[i:]
        for k in REVIEW:
            self.assertIn(k, sec, k)


if __name__ == "__main__":
    unittest.main()
