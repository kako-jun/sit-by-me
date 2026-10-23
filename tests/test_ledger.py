"""台帳（docs/ledger）・INDEX・ファイル配置表の検証が、壊れた fixture で実際に失敗することを確認する。

root は環境変数 LEDGER_ROOT で差し替える（verify_index_reachable.rb・ledger_index.py・ledger_yaml.rb・ledger_io.py 共通の方針）。
実行: uv run python3 -m unittest tests.test_ledger  （または discover -s tests）
"""
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / ".claude/skills/sit-field-background/tools"
sys.path.insert(0, str(TOOLS))
import ledger_io  # noqa: E402  (テストでは表のテキスト生成 dumps だけを使う)

RUBY = next((p for p in ("/opt/homebrew/opt/ruby/bin/ruby", shutil.which("ruby")) if p and os.path.exists(p)), "ruby")
LAYOUT_COLS = ledger_io.SCHEMA["ファイル配置"]


def rule(id, pattern, reach="リンク", entry="", reason="", kind="ドキュメント", use="テスト用"):
    row = dict.fromkeys(LAYOUT_COLS, "")
    row.update({"配置ID": id, "パターン": pattern, "種別": kind, "用途": use, "到達": reach, "入口": entry, "許可リスト理由": reason})
    return row


BASE_RULES = [
    rule("index", r"docs/INDEX\.md"),
    rule("docs-top", r"docs/(?!INDEX\.md)[^/]+\.md"),
    rule("ledger-master", r"docs/ledger/[^/]+\.yaml", kind="台帳マスター"),
    rule("bulk", r"docs/bulk/(?!README\.md).+", reach="許可", entry="docs/bulk/README.md", reason="機械出力の置き場。README が説明する"),
    rule("bulk-readme", r"docs/bulk/README\.md"),
]

INDEX_TEXT = """# INDEX

- [a](a.md)
- [bulk](bulk/README.md)

<!-- GENERATED:BEGIN ledger-views -->
<!-- GENERATED:END ledger-views -->
"""


def env_for(root):
    return {**os.environ, "LEDGER_ROOT": str(root)}


class Fixture(unittest.TestCase):
    """最小の root を tmp に作る。docs/INDEX.md → a.md、許可リストの docs/bulk（README が入口）。"""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.write("docs/INDEX.md", INDEX_TEXT)
        self.write("docs/a.md", "# a\n")
        self.write("docs/bulk/README.md", "# bulk\n")
        self.write("docs/bulk/out-1.json", "{}\n")
        self.set_rules(BASE_RULES)
        self.build_index()

    def write(self, rel, text):
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
        return p

    def set_rules(self, rules):
        self.write("docs/ledger/ファイル配置.yaml", ledger_io.dumps("ファイル配置", rules))

    def build_index(self):
        r = self.run_py("build")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def run_py(self, cmd):
        return subprocess.run([sys.executable, str(TOOLS / "ledger_index.py"), cmd], env=env_for(self.root),
                              capture_output=True, text=True, cwd=ROOT)

    def reachable(self):
        return subprocess.run([RUBY, str(ROOT / "scripts/verify_index_reachable.rb")], env=env_for(self.root),
                              capture_output=True, text=True)

    def assertFails(self, result, *needles):
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        for n in needles:
            self.assertIn(n, result.stderr)


class IndexReachabilityTests(Fixture):
    def test_clean_fixture_passes(self):
        r = self.reachable()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("PASS", r.stdout)

    def test_orphan_file_fails(self):
        self.write("docs/orphan.md", "# nobody links me\n")
        self.assertFails(self.reachable(), "孤立ファイル", "docs/orphan.md")

    def test_file_reachable_only_through_a_chain_passes(self):
        self.write("docs/b.md", "# b\n[c](c.md)\n")
        self.write("docs/c.md", "# c\n")
        self.write("docs/a.md", "# a\n[b](b.md)\n")
        self.assertEqual(self.reachable().returncode, 0)

    def test_broken_link_fails(self):
        self.write("docs/a.md", "# a\n[gone](missing.md)\n")
        self.assertFails(self.reachable(), "壊れたリンク", "missing.md")

    def test_link_inside_code_is_ignored(self):
        self.write("docs/a.md", "# a\n`[x](nothing.md)`\n```\n[y](nothing2.md)\n```\n")
        self.assertEqual(self.reachable().returncode, 0)

    def test_file_without_layout_rule_fails(self):
        self.write("tools/new.py", "print(1)\n")
        self.assertFails(self.reachable(), "配置規則に無いファイル", "tools/new.py")

    def test_file_matching_two_rules_fails(self):
        self.set_rules(BASE_RULES + [rule("dup", r"docs/a\.md")])
        self.assertFails(self.reachable(), "複数の配置規則に一致", "docs/a.md")

    def test_allowlist_without_reason_fails(self):
        rules = [dict(r, **{"許可リスト理由": ""}) if r["配置ID"] == "bulk" else r for r in BASE_RULES]
        self.set_rules(rules)
        self.assertFails(self.reachable(), "許可リスト理由")

    def test_allowlist_entrance_not_linked_fails(self):
        self.write("docs/INDEX.md", INDEX_TEXT.replace("- [bulk](bulk/README.md)\n", ""))
        self.build_index()
        self.assertFails(self.reachable(), "入口", "辿れない")

    def test_allowlist_entrance_missing_fails(self):
        (self.root / "docs/bulk/README.md").unlink()
        self.assertFails(self.reachable())

    def test_allowlisted_files_need_no_individual_link(self):
        self.write("docs/bulk/out-2.json", "{}\n")
        self.assertEqual(self.reachable().returncode, 0)

    def dir_entrance_rules(self):
        return BASE_RULES + [rule("dirent", r"docs/dirent/.+", reach="許可", entry="docs/dirent", reason="ディレクトリ単位で入る記録")]

    def test_allowlist_directory_entrance_unlinked_fails(self):
        self.write("docs/dirent/x.md", "# x\n")
        self.set_rules(self.dir_entrance_rules())
        self.build_index()
        self.assertFails(self.reachable(), "入口ディレクトリ", "辿れない")

    def test_allowlist_directory_entrance_linked_passes(self):
        self.write("docs/dirent/x.md", "# x\n")
        self.write("docs/a.md", "# a\n[dir](dirent/)\n")
        self.set_rules(self.dir_entrance_rules())
        self.build_index()
        self.assertEqual(self.reachable().returncode, 0, self.reachable().stderr)

    def test_link_pointing_outside_root_fails(self):
        self.write("docs/a.md", "# a\n[x](../../outside.md)\n")
        self.assertFails(self.reachable(), "壊れたリンク")

    def test_real_repo_has_no_orphans(self):
        r = subprocess.run([RUBY, str(ROOT / "scripts/verify_index_reachable.rb")], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)


class GeneratedViewFreshnessTests(Fixture):
    def test_fresh_view_passes(self):
        r = self.run_py("check")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_hand_edited_view_fails(self):
        p = self.root / "docs/INDEX.md"
        p.write_text(p.read_text(encoding="utf-8").replace("ファイル配置規則", "ファイル配置規則（手編集）"), encoding="utf-8")
        r = self.run_py("check")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("古い", r.stdout)

    def test_ledger_change_makes_view_stale(self):
        self.write("docs/ledger/語彙.yaml", ledger_io.dumps("語彙", [
            {"語彙ID": "V1", "グループ": "g", "値": "v", "英語断片": "", "説明": ""}]))
        r = self.run_py("check")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("古い", r.stdout)
        self.build_index()
        self.assertEqual(self.run_py("check").returncode, 0)

    def test_missing_markers_fails(self):
        self.write("docs/INDEX.md", "# INDEX\n[a](a.md)\n")
        r = self.run_py("check")
        self.assertNotEqual(r.returncode, 0)


class VerifyLedgerIntegrationTests(unittest.TestCase):
    """実リポの台帳をコピーして verify_ledger.rb が新表の違反と古い INDEX を検出するか（他の検査の結果とは独立に、該当メッセージの有無を見る）。"""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.base = Path(cls.tmp.name)
        for name in ("scripts", ".claude/skills/sit-field-background/tools"):
            shutil.copytree(ROOT / name, cls.base / name, ignore=shutil.ignore_patterns("__pycache__"))
        for name in ("docs/ledger", "docs/topology"):
            shutil.copytree(ROOT / name, cls.base / name, ignore=shutil.ignore_patterns("handoff"))
        shutil.copy(ROOT / "docs/INDEX.md", cls.base / "docs/INDEX.md")
        for name in ("pyproject.toml", "uv.lock"):
            shutil.copy(ROOT / name, cls.base / name)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def setUp(self):
        self.scratch = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.scratch, True)
        self.work = self.scratch / "r"
        shutil.copytree(self.base, self.work, ignore=shutil.ignore_patterns(".venv"))

    def verify(self):
        env = {**os.environ, "LEDGER_ROOT": str(self.work), "LEDGER_SKIP_REGEN": "1"}
        return subprocess.run([RUBY, str(self.work / "scripts/verify_ledger.rb")], env=env, capture_output=True, text=True, cwd=self.work)

    def test_stale_index_is_reported(self):
        p = self.work / "docs/INDEX.md"
        p.write_text(p.read_text(encoding="utf-8").replace("### 台帳の表", "### 台帳の表（古い）"), encoding="utf-8")
        self.assertIn("生成ビューが古い", self.verify().stderr)

    def test_fresh_index_is_not_reported(self):
        self.assertNotIn("生成ビューが古い", self.verify().stderr)

    def test_layout_allow_without_reason_is_reported(self):
        p = self.work / "docs/ledger/ファイル配置.yaml"
        rows = ledger_io.parse("ファイル配置", p.read_text(encoding="utf-8"))
        for r in rows:
            if r["到達"] == "許可":
                r["許可リスト理由"] = ""
        p.write_text(ledger_io.dumps("ファイル配置", rows), encoding="utf-8")
        self.assertIn("許可リスト理由が要る", self.verify().stderr)

    def test_layout_unknown_owner_table_is_reported(self):
        p = self.work / "docs/ledger/ファイル配置.yaml"
        rows = ledger_io.parse("ファイル配置", p.read_text(encoding="utf-8"))
        rows[0]["所有表"] = "存在しない表"
        p.write_text(ledger_io.dumps("ファイル配置", rows), encoding="utf-8")
        self.assertIn("所有表='存在しない表'", self.verify().stderr)

    def test_generated_path_without_layout_rule_is_reported(self):
        p = self.work / "docs/ledger/生成物.yaml"
        rows = ledger_io.parse("生成物", p.read_text(encoding="utf-8"))
        rows[0]["パス"] = "nowhere/plan.json"
        p.write_text(ledger_io.dumps("生成物", rows), encoding="utf-8")
        self.assertIn("どの配置規則", self.verify().stderr)

    # ---- Issue点検.yaml（verify_ledger.rb の外部キー・語彙・整合）
    def mutate(self, **changes):
        p = self.work / "docs/ledger/Issue点検.yaml"
        rows = ledger_io.parse("Issue点検", p.read_text(encoding="utf-8"))
        rows[0].update(changes)
        p.write_text(ledger_io.dumps("Issue点検", rows), encoding="utf-8")

    def test_clean_issue_audit_has_no_issue_audit_errors(self):
        errs = [ln for ln in self.verify().stderr.splitlines() if ln.startswith("FAIL") and "Issue点検" in ln]
        self.assertEqual(errs, [])

    def test_unknown_decision_id_is_reported(self):
        self.mutate(**{"決定ID": "NO.SUCH.DECISION", "分類": "決定表に反映済み"})
        self.assertIn("外部キー Issue点検.決定ID='NO.SUCH.DECISION'", self.verify().stderr)

    def test_unknown_classification_is_reported(self):
        self.mutate(**{"分類": "たぶん決定"})
        self.assertIn("分類 'たぶん決定' が語彙", self.verify().stderr)

    def test_reflected_without_decision_id_is_reported(self):
        self.mutate(**{"分類": "決定表に反映済み", "決定ID": ""})
        self.assertIn("決定IDが空", self.verify().stderr)

    def test_issue_number_mismatching_url_is_reported(self):
        self.mutate(**{"Issue番号": "99999"})
        self.assertIn("Issue番号 '99999' が URL の Issue と違う", self.verify().stderr)


class PromptReflectionTests(unittest.TestCase):
    """verify_prompt_reflects_ledger.rb が、過去に漏れた事例（畳・化石の石・-fire の勝手口・火事版の上半分・渡り廊下の窓列）や
    自由記述・継承要素の漏れを、壊した fixture で実際に検出するか。プロンプトは fixture 内のツールで導出する（画像生成はしない）。"""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.base = Path(cls.tmp.name)
        for name in ("scripts", ".claude/skills/sit-field-background/tools"):
            shutil.copytree(ROOT / name, cls.base / name, ignore=shutil.ignore_patterns("__pycache__"))
        for name in ("docs/ledger", "docs/topology"):
            shutil.copytree(ROOT / name, cls.base / name, ignore=shutil.ignore_patterns("handoff"))
        oblique = cls.base / "docs/production/oblique-mocks"
        oblique.mkdir(parents=True)
        for f in (ROOT / "docs/production/oblique-mocks").glob("*.json"):
            shutil.copy(f, oblique / f.name)
        for name in ("pyproject.toml", "uv.lock"):
            shutil.copy(ROOT / name, cls.base / name)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory()
        self.addCleanup(self.scratch.cleanup)
        self.work = Path(self.scratch.name) / "r"
        shutil.copytree(self.base, self.work)

    def rows(self, table):
        return ledger_io.parse(table, (self.work / f"docs/ledger/{table}.yaml").read_text(encoding="utf-8"))

    def save(self, table, rows):
        (self.work / f"docs/ledger/{table}.yaml").write_text(ledger_io.dumps(table, rows), encoding="utf-8")

    def edit_row(self, table, key, val, **changes):
        rows = self.rows(table)
        hit = [r for r in rows if r[key] == val]
        self.assertTrue(hit, f"{table}.{key}={val} が無い")
        hit[0].update(changes)
        self.save(table, rows)

    def delete_rows(self, table, pred):
        rows = self.rows(table)
        kept = [r for r in rows if not pred(r)]
        self.assertLess(len(kept), len(rows), "消す行が無かった")
        self.save(table, kept)

    def probe_cmd(self):
        probe = shlex.quote(str(self.work / ".claude/skills/sit-field-background/tools/oblique_prompt_probe.py"))
        try:  # 斜めツールは numpy / opencv / pillow が要る。無い環境（素の uv run）では uv に足させる
            import cv2, numpy, PIL  # noqa: F401, E401
            return f"{shlex.quote(sys.executable)} {probe}"
        except ImportError:
            return f"uv run --project {shlex.quote(str(self.work))} --with numpy --with opencv-python-headless --with pillow python3 {probe}"

    def verify(self, *args):
        env = {**os.environ, "LEDGER_ROOT": str(self.work), "LEDGER_PROBE_CMD": self.probe_cmd()}
        return subprocess.run([RUBY, str(self.work / "scripts/verify_prompt_reflects_ledger.rb"), *args], env=env, capture_output=True, text=True, cwd=self.work)

    def assertDetects(self, *needles):
        r = self.verify()
        self.assertNotEqual(r.returncode, 0, "壊したのに PASS した\n" + r.stdout)
        for n in needles:
            self.assertIn(n, r.stderr)

    def test_clean_ledger_passes_and_reports_gated_maps(self):
        r = self.verify()
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertIn("PASS", r.stdout)
        self.assertIn("ゲートで停止（対象外）: TRM-06", r.stdout)
        self.assertNotIn("検査したMAP（0）", r.stdout)

    # ---- 過去に漏れた4事例 + 渡り廊下の窓列
    def test_tatami_leaking_into_prompt_is_detected(self):
        self.edit_row("建物", "建物ID", "BLD-TRM-jukyo", **{"外壁": "畳敷きの外壁"})
        self.assertDetects("TRM.no-tatami", "禁止語『畳』")

    def test_tatami_decision_removed_is_detected(self):
        self.delete_rows("決定", lambda r: r["決定ID"] == "TRM.no-tatami")
        self.assertDetects("回帰アンカー tatami", "TRM.no-tatami")

    def test_fossil_decision_removed_is_detected(self):
        self.delete_rows("決定", lambda r: r["決定ID"] == "TRM-05.fossil")
        self.assertDetects("回帰アンカー fossil-stone", "TRM-05.fossil")

    def test_fossil_decision_no_longer_reaches_prompt_is_detected(self):
        self.edit_row("決定", "決定ID", "TRM-05.fossil", **{"プロンプト出力": "なし"})
        self.assertDetects("fossil-stone", "TRM-05.fossil")

    def test_fire_back_door_on_wrong_wall_is_detected(self):
        row = next(r for r in self.rows("決定") if r["決定ID"] == "TRM-05.door-back")
        self.edit_row("決定", "決定ID", "TRM-05.door-back", **{"決定の要点": row["決定の要点"].replace("北壁", "西壁")})
        self.assertDetects("door-back-fire", "西壁")

    def test_fire_upper_half_decision_removed_is_detected(self):
        self.delete_rows("決定", lambda r: r["決定ID"] == "TRM-05-fire.upper-half")
        self.assertDetects("回帰アンカー fire-upper-half", "TRM-05-fire.upper-half")

    def test_fire_upper_half_decision_with_dropped_wording_is_detected(self):
        self.edit_row("決定", "決定ID", "TRM-05-fire.upper-half", **{"決定の要点": "火事版は燃える。"})
        self.assertDetects("上半分だけ")

    def test_corridor_window_row_changed_is_detected(self):
        self.edit_row("建物窓列", "窓列ID", "BLD-TRM-corridor-w.south-wins", **{"先頭比": "0.6"})
        self.assertDetects("BLD-TRM-corridor-w.south-wins", "一致しない")

    def test_corridor_windows_missing_on_one_side_is_detected(self):
        self.delete_rows("窓", lambda r: r["MAP_ID"] == "TRM-03" and r["建物窓列ID"] == "BLD-TRM-corridor-w.south-wins")
        self.assertDetects("回帰アンカー corridor-windows", "TRM-03")

    # ---- 自由記述・継承要素・決定の逐語
    def test_free_text_on_window_must_reach_features(self):
        win = next(r for r in self.rows("窓") if r["MAP_ID"] == "TRM-05")
        self.edit_row("窓", "窓ID", win["窓ID"], **{"特徴(自由記述)": "窓枠に結露の水滴がある"})
        r = self.verify()
        self.assertEqual(r.returncode, 0, r.stderr)  # 導出側が FEATURES 節へそのまま入れている

    def test_free_text_missing_from_prompt_is_detected(self):
        # 導出器（ledger_query.free_texts の建物の行）を壊した状態を再現して、台帳の自由記述が FEATURES に出ない漏れを検出できるか
        self.edit_row("建物", "建物ID", "BLD-TRM-jukyo", **{"特徴(自由記述)": "屋根に鳩が一羽いる"})
        probe = self.work / ".claude/skills/sit-field-background/tools/ledger_query.py"
        text = probe.read_text(encoding="utf-8")
        self.assertIn('out.append((f"建物 {b[\'建物ID\']}", b[L.FREE]))', text)
        probe.write_text(text.replace('out.append((f"建物 {b[\'建物ID\']}", b[L.FREE]))', "pass"), encoding="utf-8")
        self.assertDetects("建物 BLD-TRM-jukyo", "特徴(自由記述)", "鳩")

    def test_inherited_element_without_reference_image_is_detected(self):
        plan = self.work / "docs/production/oblique-mocks/TRM-05-plan.json"
        doc = json.loads(plan.read_text(encoding="utf-8"))
        self.assertIn("TRM-04", doc["depends_on"])
        doc["depends_on"] = [d for d in doc["depends_on"] if d != "TRM-04"]
        plan.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
        self.assertDetects("採用要素 TRM-04.door-design", "REFERENCE IMAGES")

    def test_decision_wording_changed_in_prompt_is_detected(self):
        probe = self.work / ".claude/skills/sit-field-background/tools/ledger_query.py"
        text = probe.read_text(encoding="utf-8")
        old = "{d['決定の要点']}"
        self.assertIn(old, text)
        probe.write_text(text.replace(old, "{d['決定の要点'][:10]}", 1), encoding="utf-8")
        self.assertDetects("要点が DECISIONS 節に逐語で現れない")

    def test_gated_map_is_reported_not_checked(self):
        r = self.verify("--maps", "TRM-06,TRM-05")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("ゲートで停止（対象外）: TRM-06", r.stdout)
        self.assertIn("検査したMAP（1）: TRM-05", r.stdout)


class IssueAuditTests(unittest.TestCase):
    """audit_issue_decisions.rb: Issue の決定候補を決定表と突合して分類し、Issue点検.yaml の過不足を検出する（--from-json でオフライン）。"""

    URL = "https://github.com/kako-jun/sit-by-me/issues"

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.base = Path(cls.tmp.name)
        for name in ("scripts", ".claude/skills/sit-field-background/tools"):
            shutil.copytree(ROOT / name, cls.base / name, ignore=shutil.ignore_patterns("__pycache__"))
        for name in ("pyproject.toml", "uv.lock"):
            shutil.copy(ROOT / name, cls.base / name)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory()
        self.addCleanup(self.scratch.cleanup)
        self.work = Path(self.scratch.name) / "r"
        shutil.copytree(self.base, self.work)
        (self.work / "docs/ledger").mkdir(parents=True)
        dec = dict.fromkeys(ledger_io.SCHEMA["決定"], "")
        d1 = dict(dec, **{"決定ID": "D.url", "決定の要点": "URLで反映", "出典URL": f"{self.URL}/7#issuecomment-111", "状態": "有効"})
        d2 = dict(dec, **{"決定ID": "D.quote", "決定の要点": "逐語で反映", "逐語": "「畳がすごく不自然だ。苦手なら板張りにしろ」", "状態": "有効"})
        self.write_table("決定", [d1, d2])
        self.data = {"issues": [
            {"number": 7, "html_url": f"{self.URL}/7", "body": "ただの説明", "created_at": "2026-10-01T00:00:00Z"},
            {"number": 8, "html_url": f"https://github.com/kako-jun/sit-by-me/pull/8", "body": "", "created_at": "2026-10-01T00:00:00Z", "pull_request": {}}],
            "comments": [
            self.comment(111, 7, "## kako-jun 決定\nOK"),
            self.comment(112, 7, "## 追加決定\nkako-jun「畳がすごく不自然だ。苦手なら板張りにしろ」"),
            self.comment(113, 7, "## 決定\n逐語: 「廊下の端の扉は外へ開く向きにしろ、内開きは不可」"),
            self.comment(114, 7, "## これからやること\nkako-jun 指示どおりに台帳を直す"),
            self.comment(115, 8, "## 決定 レビュー指摘\n直した"),
            self.comment(116, 7, "ふつうの雑談"),
            self.comment(117, 7, "## 決定\nkako-jun「畳がすごく不自然だ。苦手なら板張りにしろ」「窓は全部やめて壁だけにしろ、とにかく全部だ」"),
            self.comment(118, 7, "## これからやること\nkako-jun「板張りにしろ」を台帳へ")]}

    def comment(self, cid, num, body):
        return {"id": cid, "issue_url": f"https://api.github.com/repos/kako-jun/sit-by-me/issues/{num}", "html_url": f"{self.URL}/{num}#issuecomment-{cid}",
                "body": body, "created_at": f"2026-10-02T00:00:{cid % 60:02d}Z"}

    def write_table(self, table, rows):
        (self.work / f"docs/ledger/{table}.yaml").write_text(ledger_io.dumps(table, rows), encoding="utf-8")

    def audit(self, *args):
        j = self.work / "all.json"
        j.write_text(json.dumps(self.data, ensure_ascii=False), encoding="utf-8")
        return subprocess.run([RUBY, str(self.work / "scripts/audit_issue_decisions.rb"), "--from-json", str(j), *args],
                              env=env_for(self.work), capture_output=True, text=True, cwd=self.work)

    def table(self):
        return {r["コメントURL"].rsplit("-", 1)[-1]: r for r in ledger_io.parse("Issue点検", (self.work / "docs/ledger/Issue点検.yaml").read_text(encoding="utf-8"))}

    def test_classification(self):
        self.assertEqual(self.audit("--write").returncode, 0)
        t = self.table()
        self.assertEqual((t["111"]["分類"], t["111"]["決定ID"]), ("決定表に反映済み", "D.url"))
        self.assertEqual((t["112"]["分類"], t["112"]["決定ID"]), ("決定表に反映済み", "D.quote"))
        self.assertEqual(t["113"]["分類"], "未反映(要取込み)")
        self.assertIn("逐語あり", t["113"]["備考"])
        self.assertEqual(t["114"]["分類"], "決定でない")
        self.assertEqual(t["117"]["分類"], "未反映(要取込み)")  # 逐語の一部しか決定表に無い
        self.assertIn("うち決定表に含まれる 1件", t["117"]["備考"])
        self.assertEqual(t["118"]["分類"], "未反映(要取込み)")  # 作業記録の見出しでも kako-jun の引用があれば決定でないにしない
        self.assertEqual(t["115"]["分類"], "対象外")
        self.assertNotIn("116", t)  # 候補でない雑談
        self.assertNotIn("issue-7", t)

    def test_unlogged_candidate_without_quote_is_conservatively_unreflected(self):
        self.data["comments"].append(self.comment(120, 7, "## kako-jun 指示\n台帳に入れる前に確認する"))
        self.audit("--write")
        self.assertEqual(self.table()["120"]["分類"], "未反映(要取込み)")
        self.assertIn("逐語の引用なし", self.table()["120"]["備考"])

    def test_check_fails_for_candidate_missing_from_table_and_passes_after_write(self):
        r = self.audit()
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("未点検の候補", r.stderr)
        self.assertEqual(self.audit("--write").returncode, 0)
        self.assertEqual(self.audit().returncode, 0)
        self.data["comments"].append(self.comment(121, 7, "## kako-jun 決定\nあとから増えた決定"))
        r = self.audit()
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("issuecomment-121", r.stderr)

    def test_check_fails_when_classification_drifts_from_scan(self):
        self.audit("--write")
        rows = ledger_io.parse("Issue点検", (self.work / "docs/ledger/Issue点検.yaml").read_text(encoding="utf-8"))
        for row in rows:
            if row["コメントURL"].endswith("-113"):
                row["分類"] = "決定でない"  # 逐語つきの決定候補を黙って『決定でない』にした
        self.write_table("Issue点検", rows)
        r = self.audit()
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("分類が自動判定と違う", r.stderr)

    def test_manual_classification_is_kept_on_rewrite(self):
        self.audit("--write")
        rows = ledger_io.parse("Issue点検", (self.work / "docs/ledger/Issue点検.yaml").read_text(encoding="utf-8"))
        for row in rows:
            if row["コメントURL"].endswith("-113"):
                row["分類"] = "決定でない"
                row["備考"] = "【手動】確認の結果、方針ではなく実施メモだった"
        self.write_table("Issue点検", rows)
        self.assertEqual(self.audit().returncode, 0)
        self.audit("--write")
        self.assertEqual(self.table()["113"]["分類"], "決定でない")


if __name__ == "__main__":
    unittest.main()
