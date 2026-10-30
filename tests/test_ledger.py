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


class LedgerViewsTests(Fixture):
    """ledger_views.py: build で生成し、手編集・台帳変更・欠落・手書きファイルの混入を check が検出する。"""

    def views(self, cmd):
        return subprocess.run([sys.executable, str(TOOLS / "ledger_views.py"), cmd], env=env_for(self.root), capture_output=True, text=True, cwd=ROOT)

    def setUp(self):
        super().setUp()
        self.write("docs/ledger/語彙.yaml", ledger_io.dumps("語彙", [{"語彙ID": "V1", "グループ": "g", "値": "v", "英語断片": "", "説明": ""}]))
        self.write("docs/ledger/決定.yaml", ledger_io.dumps("決定", [dict.fromkeys(ledger_io.SCHEMA["決定"], "") | {"決定ID": "T.one", "日付": "2026-10-24", "対象種別": "MAP", "対象ID": "TRM-02", "決定の要点": "テストの決定", "逐語": "「テスト」\n二行目", "状態": "有効", "プロンプト出力": "必須"}]))
        r = self.views("build")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_fresh_views_pass_and_contain_the_ledger(self):
        r = self.views("check")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        text = (self.root / "docs/ledger-views/決定.md").read_text(encoding="utf-8")
        self.assertIn("T.one", text)
        self.assertIn("> 「テスト」", text)
        self.assertIn("> 二行目", text)

    def test_hand_edit_fails(self):
        p = self.root / "docs/ledger-views/決定.md"
        p.write_text(p.read_text(encoding="utf-8") + "\n手で足した行\n", encoding="utf-8")
        r = self.views("check")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("決定.md が台帳と一致しない", r.stdout)

    def test_stale_after_ledger_change_fails_until_rebuilt(self):
        self.write("docs/ledger/決定.yaml", ledger_io.dumps("決定", [dict.fromkeys(ledger_io.SCHEMA["決定"], "") | {"決定ID": "T.two", "日付": "2026-10-24", "対象種別": "MAP", "対象ID": "TRM-02", "決定の要点": "別の決定", "状態": "有効"}]))
        r = self.views("check")
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual(self.views("build").returncode, 0)
        self.assertEqual(self.views("check").returncode, 0)
        self.assertIn("T.two", (self.root / "docs/ledger-views/決定.md").read_text(encoding="utf-8"))

    def test_missing_view_fails(self):
        (self.root / "docs/ledger-views/接続.md").unlink()
        r = self.views("check")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("接続.md が無い", r.stdout)

    def test_handwritten_file_in_views_dir_fails(self):
        self.write("docs/ledger-views/メモ.md", "# 手書き\n")
        r = self.views("check")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("生成ビューではない", r.stdout)


class VerifyLedgerIntegrationTests(unittest.TestCase):
    """実リポの台帳をコピーして verify_ledger.rb が新表の違反と古い INDEX を検出するか（他の検査の結果とは独立に、該当メッセージの有無を見る）。"""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.base = Path(cls.tmp.name)
        for name in ("scripts", ".claude/skills/sit-field-background/tools", ".claude/skills/sit-battle-background/tools"):
            shutil.copytree(ROOT / name, cls.base / name, ignore=shutil.ignore_patterns("__pycache__"))
        for name in ("docs/ledger", "docs/topology"):
            shutil.copytree(ROOT / name, cls.base / name, ignore=shutil.ignore_patterns("handoff"))
        shutil.copy(ROOT / "docs/INDEX.md", cls.base / "docs/INDEX.md")
        shutil.copytree(ROOT / "docs/ledger-views", cls.base / "docs/ledger-views")
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


    # ---- docs/ledger-views/*.md（台帳からの生成ビュー）の鮮度
    def test_fresh_views_are_not_reported(self):
        self.assertNotIn("生成ビューが古い、または検査できない: FAIL: docs/ledger-views", self.verify().stderr)
        self.assertNotIn("ledger-views/ の生成ビューが古い", self.verify().stderr)

    def test_hand_edited_view_is_reported_by_verify_ledger(self):
        p = self.work / "docs/ledger-views/MAP.md"
        p.write_text(p.read_text(encoding="utf-8").replace("MAP 一覧", "MAP 一覧（手編集）", 1), encoding="utf-8")
        self.assertIn("ledger-views/ の生成ビューが古い", self.verify().stderr)

    def test_ledger_change_without_regenerating_views_is_reported(self):
        def mut(rows):
            rows[0]["決定の要点"] += "（追記）"
        self.edit_table("決定", mut)
        self.assertIn("ledger-views/ の生成ビューが古い", self.verify().stderr)

    # ---- 描画定数・プロンプト文面（コードの直書きを台帳へ移した表。コードとの対応を verify_ledger.rb が見る）
    def edit_table(self, table, fn):
        p = self.work / f"docs/ledger/{table}.yaml"
        rows = ledger_io.parse(table, p.read_text(encoding="utf-8"))
        fn(rows)
        p.write_text(ledger_io.dumps(table, rows), encoding="utf-8")

    def code_text_errors(self):
        return [ln for ln in self.verify().stderr.splitlines() if ln.startswith("FAIL") and ("プロンプト文面" in ln or "描画定数" in ln or "台帳ID" in ln)]

    def test_clean_code_texts_have_no_errors(self):
        self.assertEqual(self.code_text_errors(), [])

    def test_code_reference_without_row_is_reported(self):
        self.edit_table("プロンプト文面", lambda rows: rows.remove(next(r for r in rows if r["文面ID"] == "PR.role")))
        self.assertIn("コードが参照する台帳ID 'PR.role'", self.verify().stderr)

    def test_row_without_code_reference_is_reported(self):
        def add(rows):
            r = dict(rows[0]); r["文面ID"] = "PR.dead-row"; r["文面"] = "誰も使わない"; r["変数"] = ""
            rows.append(r)
        self.edit_table("プロンプト文面", add)
        self.assertIn("台帳ID PR.dead-row がどのコード", self.verify().stderr)

    def test_variable_column_mismatch_is_reported(self):
        def mut(rows):
            next(r for r in rows if r["文面ID"] == "PR.partition")["文面"] += "{extra}"
        self.edit_table("プロンプト文面", mut)
        self.assertIn("プロンプト文面 PR.partition: 変数列", self.verify().stderr)

    def test_empty_constant_value_is_reported(self):
        def mut(rows):
            next(r for r in rows if r["定数ID"] == "view.char")["値"] = ""
        self.edit_table("描画定数", mut)
        self.assertIn("描画定数 view.char: 値が空", self.verify().stderr)

    def test_oblique_text_stops_on_unknown_id_and_on_wrong_variables(self):
        def run(code):
            return subprocess.run([sys.executable, "-c", "import sys; sys.path.insert(0, %r); import oblique_text as X; %s" % (str(self.work / ".claude/skills/sit-field-background/tools"), code)],
                                  env={**os.environ, "LEDGER_ROOT": str(self.work)}, capture_output=True, text=True, cwd=self.work)
        r = run("X.text('PR.no-such-id')")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("が台帳", r.stderr)
        r = run("X.text('PR.partition')")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("変数が合わない", r.stderr)
        r = run("print(X.text('PR.partition', id='W1'))")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("W1: 仕切り", r.stdout)


class LegacyMdReaderTests(unittest.TestCase):
    """旧 md を読む scripts は見出し行の列名で読む（md_table.rb）。列の並び替えで壊れず、台帳管理のMAPは台帳で止まる。"""

    CHECKLIST = """| ID | 状態 | Ref | mask / 出力 | 具体的TBD |
|---|---|---|---|---|
| KRB-01 | ready | R005 | x.webp | |
"""
    CHECKLIST_REORDERED = """| ID | 具体的TBD | mask / 出力 | Ref | 状態 |
|---|---|---|---|---|
| KRB-01 | | x.webp | R005 | ready |
"""
    SPEC = """| MAP | 時期 | 一言特徴 | 方位・主路・通行条件 | 暫定固定 |
|---|---|---|---|---|
| KRB-01 | 幼稚園 | 交差点 | 南へ | 固定A |
"""
    SPEC_REORDERED = """| MAP | 暫定固定 | 方位・主路・通行条件 | 一言特徴 | 時期 |
|---|---|---|---|---|
| KRB-01 | 固定A | 南へ | 交差点 | 幼稚園 |
"""
    TOPO = """#### MAP相互接続台帳 v2

| From | To | 種別 | 主路・状態 |
|---|---|---|---|
| KRB-01.top | KRB-11.bottom | edge | 北へ |

注記の地の文（表が途中で分かれても続きの行として読む）

| KRB-01.right | KRB-12.left | edge | 東へ |

#### 寺町の地形不変条件
"""
    TOPO_REORDERED = TOPO.replace("| From | To | 種別 | 主路・状態 |", "| From | To | 主路・状態 | 種別 |").replace("| edge | 北へ |", "| 北へ | edge |").replace("| edge | 東へ |", "| 東へ | edge |")

    def run_ruby(self, root, *args):
        return subprocess.run([RUBY, str(root / "scripts/build_map_prompt.rb"), *args], capture_output=True, text=True)

    def make_root(self, checklist, spec, topo):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        (root / "scripts").mkdir()
        (root / "docs/ledger").mkdir(parents=True)
        for f in ("build_map_prompt.rb", "md_table.rb", "ledger_yaml.rb"):
            shutil.copy(ROOT / "scripts" / f, root / "scripts" / f)
        # ledger_yaml.rb は表定義(SCHEMA)を ledger_io.py schema から読む
        tools = root / ".claude/skills/sit-field-background/tools"
        tools.mkdir(parents=True)
        shutil.copy(ROOT / ".claude/skills/sit-field-background/tools/ledger_io.py", tools / "ledger_io.py")
        for name in ("pyproject.toml", "uv.lock"):
            shutil.copy(ROOT / name, root / name)
        (root / "docs/map-contract-checklist.md").write_text(checklist, encoding="utf-8")
        (root / "docs/map-specifications.md").write_text(spec, encoding="utf-8")
        (root / "docs/map-topology.md").write_text(topo, encoding="utf-8")
        return root

    def test_prompt_is_the_same_when_columns_are_reordered(self):
        a = self.run_ruby(self.make_root(self.CHECKLIST, self.SPEC, self.TOPO), "KRB-01")
        b = self.run_ruby(self.make_root(self.CHECKLIST_REORDERED, self.SPEC_REORDERED, self.TOPO_REORDERED), "KRB-01")
        self.assertEqual(a.returncode, 0, a.stderr)
        self.assertIn("Subject / unique landmark: 交差点", a.stdout)
        self.assertIn("KRB-01.top / KRB-11.bottom / edge; KRB-01.right / KRB-12.left / edge", a.stdout)
        self.assertEqual(a.stdout, b.stdout)

    def test_ledger_root_redirects_where_the_md_files_are_read_from(self):
        # スクリプトを複製せず本物の scripts/ を使い、LEDGER_ROOT だけで md の読み先（docs/*.md）を差し替える
        root = self.make_root(self.CHECKLIST, self.SPEC, self.TOPO)
        r = subprocess.run([RUBY, str(ROOT / "scripts/build_map_prompt.rb"), "KRB-01"], env=env_for(root), capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("Subject / unique landmark: 交差点", r.stdout)  # fixture の md の内容（本物の docs には無い）

    def test_verify_map_ledger_reads_md_from_ledger_root(self):
        root = self.make_root(self.CHECKLIST, self.SPEC, self.TOPO)
        # The public verifier checks YAML-derived document views first. Give
        # that check a valid empty registry, then require the missing topology
        # registry diagnostic to name this isolated root.
        (root / "docs/ledger/文書ビュー.yaml").write_text(ledger_io.dumps("文書ビュー", []), encoding="utf-8")
        r = subprocess.run([RUBY, str(ROOT / "scripts/verify_map_ledger.rb")], env=env_for(root), capture_output=True, text=True)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn(str(root), r.stderr)  # fixture に無い docs/topology/map-ids.json を fixture の root から読もうとして失敗する（本物の docs を読まない）

    def test_blocked_status_still_blocks(self):
        root = self.make_root(self.CHECKLIST.replace("ready", "blocked"), self.SPEC, self.TOPO)
        r = self.run_ruby(root, "KRB-01")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("prompt generation is blocked", r.stderr)

    def test_ledger_managed_map_stops_on_the_ledger_not_the_md(self):
        root = self.make_root(self.CHECKLIST, self.SPEC, self.TOPO)
        shutil.copy(ROOT / "docs/ledger/MAP.yaml", root / "docs/ledger/MAP.yaml")
        shutil.copy(ROOT / "docs/ledger/未決.yaml", root / "docs/ledger/未決.yaml")
        r = self.run_ruby(root, "TRM-04")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("managed by the ledger", r.stderr)
        self.assertIn("U-042", r.stderr)  # TRM-04.dais の未決

    def test_verify_map_ledger_requires_ledger_status_for_ledger_maps(self):
        text = (ROOT / "docs/map-contract-checklist.md").read_text(encoding="utf-8")
        self.assertIn("| TRM-04 | 台帳 |", text)
        for needle in ("| TRM-02 | 台帳 |", "| TRM-03 | 台帳 |", "| TRM-05 | 台帳 |"):
            self.assertIn(needle, text)
        self.assertNotIn("recreate-required-1920x1080 |", "\n".join(l for l in text.splitlines() if l.startswith("| TRM-")))


class OperationRulesPresentTests(unittest.TestCase):
    """運用（決定は先に台帳・必須キーと自由記述・画像生成の停止・生成画像は見ない）が入口の3文書から消えていないこと。"""

    NEEDLES = ("決定IDを参照するだけ", "必須キー", "特徴(自由記述)", "再開指示", "Claude は見ない", "プロンプト文面")

    def test_rules_are_stated_in_skill_readme_and_index(self):
        for rel in (".claude/skills/sit-field-background/SKILL.md", ".claude/skills/sit-field-background/tools/README.md", "docs/INDEX.md"):
            text = (ROOT / rel).read_text(encoding="utf-8")
            for n in self.NEEDLES:
                self.assertIn(n, text, f"{rel} に運用の記述『{n}』が無い")


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
        # 現行の台帳は寺町 TRM-06〜17 の未決を既定(要確認)で解消済み（#191）なので、ゲート停止は 0 で TRM-06〜17 も検査対象に入る
        r = self.verify()
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertIn("PASS", r.stdout)
        self.assertNotIn("ゲートで停止（対象外）", r.stdout)
        self.assertIn("ゲート停止 0", r.stdout)
        self.assertIn("TRM-06", r.stdout.split("検査したMAP")[1].splitlines()[0])
        # 必須キーを未決に戻した MAP はゲートで止まり、対象外として報告される
        self.edit_row("MAP", "MAP_ID", "TRM-06", **{"壁材": "未決(要確認)"})
        r = self.verify()
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
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
        self.edit_row("MAP", "MAP_ID", "TRM-06", **{"壁材": "未決(要確認)"})
        r = self.verify("--maps", "TRM-06,TRM-05")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("ゲートで停止（対象外）: TRM-06", r.stdout)
        self.assertIn("検査したMAP（1）: TRM-05", r.stdout)


    # ---- 時期差分MAPは基準MAPの確定画像を参照に含める（#193）
    BASE_LINE = "- 基準MAP TRM-05 の確定画像は、このMAP（{era}）と同じ部屋・同じ建物の別時期。"

    def probe(self):
        r = subprocess.run(self.probe_cmd(), shell=True, env={**os.environ, "LEDGER_ROOT": str(self.work)}, capture_output=True, text=True, cwd=self.work)
        self.assertEqual(r.returncode, 0, r.stderr)
        return {rec["map_id"]: rec["prompt"] for rec in json.loads(r.stdout)}

    def adopt_base(self):
        """合成の採用状態: 素材表に TRM-05 の採用済み背景画像の行を足す（実ファイルは作らない・実台帳は変えない）。"""
        rows = self.rows("素材")
        rows.append(dict.fromkeys(ledger_io.SCHEMA["素材"], "") | {"素材ID": "A-TEST-193", "所有者ID": "TRM-05", "種別": "背景(屋内)", "状態": "採用",
                                                              "パス": "assets/images/fields/reference/synthetic-trm05-adopted.webp", "sha256": "ab" * 32})
        self.save("素材", rows)

    def build_variant(self, era):
        out = Path(self.scratch.name) / f"out-{era}"
        cmd = self.probe_cmd().replace("oblique_prompt_probe.py", "oblique_build.py")
        plan = shlex.quote(str(self.work / "docs/production/oblique-mocks/TRM-05-plan.json"))
        r = subprocess.run(f"{cmd} {plan} --variant {era} --out {shlex.quote(str(out))}", shell=True, env={**os.environ, "LEDGER_ROOT": str(self.work)}, capture_output=True, text=True, cwd=self.work)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        key = f"TRM-05-{era}"
        man = json.loads((out / key / "manifest.json").read_text(encoding="utf-8"))
        return man["stages"]["prompt"], (out / key / f"{key}-edit-prompt.txt").read_text(encoding="utf-8")

    def test_era_variants_blocked_until_base_is_adopted(self):
        for era in ("kids", "fire"):
            prompt = self.probe()[f"TRM-05-{era}"]
            self.assertIn("- TRM-05: 未確定（依存MAPが採用されるまで", prompt)
            self.assertIn(self.BASE_LINE.format(era=era), prompt)
            stage, text = self.build_variant(era)
            self.assertEqual(stage["status"], "blocked")
            self.assertIn("TRM-05", stage["unadopted_dependencies"])
            self.assertEqual(stage["blocked_base"], "TRM-05")
            self.assertIn("# BLOCKED（基準の採用待ち）", text)

    def test_era_variants_carry_base_image_after_adoption(self):
        self.adopt_base()
        for era in ("kids", "fire"):
            prompt = self.probe()[f"TRM-05-{era}"]
            self.assertIn("- TRM-05: assets/images/fields/reference/synthetic-trm05-adopted.webp（sha256 abababababab）", prompt)
            self.assertNotIn("TRM-05: 未確定", prompt)
            self.assertIn(self.BASE_LINE.format(era=era), prompt)
            self.assertIn("- TRM-04: assets/images/fields/reference/", prompt)  # 採用要素の元MAP（本堂）の参照は落とさない
            stage, text = self.build_variant(era)
            self.assertEqual(stage["status"], "ok")
            self.assertEqual(stage["unadopted_dependencies"], [])
            self.assertNotIn("blocked_base", stage)
            self.assertNotIn("# BLOCKED", text)
        self.assertEqual(self.verify().returncode, 0)  # 採用後も検証は PASS

    def test_e2_schedule_check_refuses_blocked_prompt_even_if_base_is_canonical(self):
        # --adopt --canonical だけ（素材表は未採用）でも親は『確定』になるが、プロンプト段が blocked のままなら起動を拒否する（#193）
        ob = self.work / "docs/production/oblique-mocks"
        (ob / "TRM-05").mkdir()
        (ob / "TRM-05/manifest.json").write_text(json.dumps({"adoption": {"canonical": "docs/ledger/未決.yaml"}}), encoding="utf-8")
        (ob / "TRM-05-kids").mkdir()
        mf = ob / "TRM-05-kids/manifest.json"

        def check():
            cmd = f"{shlex.quote(sys.executable)} -I {shlex.quote(str(self.work / '.claude/skills/sit-field-background/tools/oblique_e2_schedule.py'))} check TRM-05-kids"
            return subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=self.work)

        mf.write_text(json.dumps({"stages": {"prompt": {"status": "blocked", "unadopted_dependencies": ["TRM-05"]}}}), encoding="utf-8")
        r = check()
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("プロンプトが blocked", r.stderr)
        mf.write_text(json.dumps({"stages": {"prompt": {"status": "ok"}}}), encoding="utf-8")
        r = check()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def _sched(self, *args):
        tool = self.work / ".claude/skills/sit-field-background/tools/oblique_e2_schedule.py"
        return subprocess.run([sys.executable, "-I", str(tool), *args], capture_output=True, text=True, cwd=self.work)

    def test_e2_schedule_list_and_launch_exclude_blocked_prompt(self):
        # 基準だけ canonical・素材表は未採用（プロンプト段 blocked）。check と同じ判定を list／launch も使う。
        # 使わないと list が『起動可』と出し launch が起動して、run.sh が check で落ちる（エラーは e2-launch.log にしか出ない）（#193）
        ob = self.work / "docs/production/oblique-mocks"
        (ob / "TRM-05").mkdir()
        (ob / "TRM-05/manifest.json").write_text(json.dumps({"adoption": {"canonical": "docs/ledger/未決.yaml"}}), encoding="utf-8")
        (ob / "TRM-05-kids").mkdir()
        mf = ob / "TRM-05-kids/manifest.json"
        mf.write_text(json.dumps({"stages": {"prompt": {"status": "blocked", "unadopted_dependencies": ["TRM-05"]}}}), encoding="utf-8")

        def kids_row(out):
            return next(l for l in out.splitlines() if l.startswith("TRM-05-kids "))

        r = self._sched("list")
        self.assertEqual(r.returncode, 0, r.stderr)
        row = kids_row(r.stdout)
        self.assertIn("プロンプトが blocked（再生成が必要", row)
        self.assertNotIn(" 可 ", row)
        r = self._sched("launch", "--dry-run")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn("[dry-run] TRM-05-kids", r.stdout)
        self.assertIn("スキップ TRM-05-kids", r.stdout)
        self.assertIn("プロンプトが blocked", r.stdout)
        # blocked でなければ起動可・launch の対象になる
        mf.write_text(json.dumps({"stages": {"prompt": {"status": "ok"}}}), encoding="utf-8")
        self.assertIn(" 可 ", kids_row(self._sched("list").stdout))
        r = self._sched("launch", "--dry-run")
        self.assertIn("[dry-run] TRM-05-kids", r.stdout)
        self.assertNotIn("スキップ TRM-05-kids", r.stdout)

    def test_base_map_itself_is_not_blocked_by_itself(self):
        self.assertNotIn("基準MAP TRM-05 の確定画像は", self.probe()["TRM-05"])

    def test_era_variant_without_base_dependency_in_ledger_is_detected(self):
        self.delete_rows("時期差分", lambda r: r["MAP_ID"] == "TRM-05" and r["時期"] == "kids" and r["項目"] == "依存")
        self.assertDetects("TRM-05-kids", "依存に基準MAP TRM-05 が無い")

    def test_era_variant_plan_dropping_base_reference_is_detected(self):
        plan = self.work / "docs/production/oblique-mocks/TRM-05-plan.json"
        doc = json.loads(plan.read_text(encoding="utf-8"))
        doc["variants"]["fire"]["depends_on"] = []
        plan.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
        self.assertDetects("TRM-05-fire", "基準MAP TRM-05 が REFERENCE IMAGES に現れない")

    def test_base_reference_usage_sentence_removed_from_ledger_is_detected(self):
        # 文面行が台帳から消えると、プロンプトを導出するツール側が止まる（検査 (vi) の tpl.nil? 分岐の手前）。特定のメッセージで検出されること
        self.delete_rows("プロンプト文面", lambda r: r["文面ID"] == "PR.reference.base-era")
        self.assertDetects("PR.reference.base-era")

    def test_base_reference_usage_sentence_missing_from_prompt_is_detected_by_check_vi(self):
        # 台帳には文面があるのにプロンプトへ入らない（生成側の脱落）。検査 (vi) の『使い方の文が REFERENCE IMAGES 節に現れない』分岐を直接通す
        q = self.work / ".claude/skills/sit-field-background/tools/ledger_query.py"
        text = q.read_text(encoding="utf-8")
        line = "        L_.append(X.base_era_reference(base, map_id[len(base) + 1:]))\n"
        self.assertIn(line, text)
        q.write_text(text.replace(line, "        pass\n"), encoding="utf-8")
        self.assertDetects("基準参照の使い方の文（プロンプト文面.PR.reference.base-era）が REFERENCE IMAGES 節に現れない")


class E2RunMarkerTests(unittest.TestCase):
    """oblique_e2_run.sh が imagegen に渡さない末尾（DRAFT/BLOCKED）の始まりを sed で探す行マーカーが、
    台帳が出す全 edit-prompt の行に一致すること。元バグ（『台帳ゲート』と書いて一致せず削除が空振りした）を検出できなかったための回帰テスト（#193）。"""

    def test_run_script_marker_matches_every_edit_prompt(self):
        import re
        script = (ROOT / ".claude/skills/sit-field-background/tools/oblique_e2_run.sh").read_text(encoding="utf-8")
        m = re.search(r"^LEDGER_MARKER_RE='([^']+)'$", script, re.M)
        self.assertIsNotNone(m, "run.sh に LEDGER_MARKER_RE の定義が無い")
        self.assertIn('sed "/$LEDGER_MARKER_RE/,\\$d"', script, "run.sh が LEDGER_MARKER_RE で削除していない")
        marker = re.compile(m.group(1))
        prompts = sorted((ROOT / "docs/production/oblique-mocks").glob("*/*-edit-prompt.txt"))
        self.assertTrue(prompts)
        for p in prompts:
            lines = p.read_text(encoding="utf-8").splitlines()
            self.assertTrue(any(marker.search(l) for l in lines), f"{p.name}: run.sh の削除マーカー {m.group(1)!r} に一致する行が無い")


class IssueAuditBase(unittest.TestCase):
    """audit_issue_decisions.rb のテスト共通土台。audit_issue_decisions.rb: Issue の決定候補を決定表と突合して分類し、Issue点検.yaml の過不足を検出する（--from-json でオフライン）。"""

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


class IssueAuditTests(IssueAuditBase):
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


class LedgerCopyBase(unittest.TestCase):
    """実リポの台帳・scripts・tools をコピーした root を作り、壊した台帳で検査が実際に失敗することを見る共通土台。
    画像生成はしない。コピーは小さい（台帳 約1MB・scripts・tools・派生 JSON）。"""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.base = Path(cls.tmp.name)
        for name in ("scripts", ".claude/skills/sit-field-background/tools"):
            shutil.copytree(ROOT / name, cls.base / name, ignore=shutil.ignore_patterns("__pycache__"))
        for name in ("docs/ledger", "docs/topology"):
            shutil.copytree(ROOT / name, cls.base / name, ignore=shutil.ignore_patterns("handoff"))
        shutil.copy(ROOT / "docs/INDEX.md", cls.base / "docs/INDEX.md")
        shutil.copytree(ROOT / "docs/ledger-views", cls.base / "docs/ledger-views")
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

    def env(self, **extra):
        return {**os.environ, "LEDGER_ROOT": str(self.work), **extra}

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

    def replace_text(self, table, old, new, count=1):
        p = self.work / f"docs/ledger/{table}.yaml"
        text = p.read_text(encoding="utf-8")
        self.assertIn(old, text)
        p.write_text(text.replace(old, new, count), encoding="utf-8")

    def replace_in_row(self, table, anchor, old, new):
        """anchor（行の先頭キー付近の文字列）より後ろで最初に現れる old を new にする。dumps が拒む壊れた YAML を作るため生テキストで直す。"""
        p = self.work / f"docs/ledger/{table}.yaml"
        text = p.read_text(encoding="utf-8")
        i = text.index(anchor)
        j = text.index(old, i)
        p.write_text(text[:j] + new + text[j + len(old):], encoding="utf-8")

    def verify_ledger(self):
        return subprocess.run([RUBY, str(self.work / "scripts/verify_ledger.rb")], env=self.env(LEDGER_SKIP_REGEN="1"), capture_output=True, text=True, cwd=self.work)

    def probe_cmd(self):
        probe = shlex.quote(str(self.work / ".claude/skills/sit-field-background/tools/oblique_prompt_probe.py"))
        try:
            import cv2, numpy, PIL  # noqa: F401, E401
            return f"{shlex.quote(sys.executable)} {probe}"
        except ImportError:
            return f"uv run --project {shlex.quote(str(self.work))} --with numpy --with opencv-python-headless --with pillow python3 {probe}"

    def verify_prompt(self, *args):
        return subprocess.run([RUBY, str(self.work / "scripts/verify_prompt_reflects_ledger.rb"), *args], env=self.env(LEDGER_PROBE_CMD=self.probe_cmd()),
                              capture_output=True, text=True, cwd=self.work)

    def py(self, script, *args):
        return subprocess.run([sys.executable, str(self.work / ".claude/skills/sit-field-background/tools" / script), *args], env=self.env(),
                              capture_output=True, text=True, cwd=self.work)

    def assertFailsWith(self, r, *needles):
        self.assertNotEqual(r.returncode, 0, "壊したのに成功した\n" + r.stdout)
        for n in needles:
            self.assertIn(n, r.stderr + r.stdout)


class MissingKeysGateTests(LedgerCopyBase):
    """ledger_query.missing_keys は、Ruby の検査器が例外で落ちたときに『欠落なし』と読んでゲートを開けてはならない（閉じる側）。"""

    def missing(self, map_id):
        code = "import ledger_query as Q, sys; r = Q.missing_keys(sys.argv[1]); print('MISSING:' + repr(r))"
        return subprocess.run([sys.executable, "-c", code, map_id], env=self.env(PYTHONPATH=str(self.work / ".claude/skills/sit-field-background/tools")),
                              capture_output=True, text=True, cwd=self.work)

    def test_gated_map_reports_missing_keys(self):
        self.edit_row("MAP", "MAP_ID", "TRM-06", **{"壁材": "未決(要確認)"})
        r = self.missing("TRM-06")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("MISSING:[", r.stdout)
        self.assertNotIn("MISSING:[]", r.stdout)

    def test_ruby_exception_stops_instead_of_opening_the_gate(self):
        # Corrupt a table the mandatory-key checker actually consumes. An
        # unrelated decision table is no longer read by this scoped checker.
        self.replace_text("MAP", '"MAP_ID": "TRM-02"', '"MAP_ID": TRM-02')
        r = self.missing("TRM-05")
        self.assertNotEqual(r.returncode, 0, r.stdout)
        self.assertIn("異常終了", r.stderr)
        self.assertNotIn("MISSING:[]", r.stdout)


class RubyCrashGateTests(LedgerCopyBase):
    """台帳の内容と無関係に必須キー検査器(Ruby)が落ちた場合でも、生成ゲート・プロンプト導出が『欠落なし』として進まない。"""

    def crash_checker(self):
        p = self.work / "scripts/ledger_required_keys.rb"
        p.write_text('raise "boom（テスト用の異常終了）"\n' + p.read_text(encoding="utf-8"), encoding="utf-8")

    def test_missing_keys_stops_when_the_checker_crashes(self):
        self.crash_checker()
        code = "import ledger_query as Q; print(Q.missing_keys('TRM-05'))"
        r = subprocess.run([sys.executable, "-c", code], env=self.env(PYTHONPATH=str(self.work / ".claude/skills/sit-field-background/tools")), capture_output=True, text=True, cwd=self.work)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("異常終了", r.stderr)
        self.assertNotEqual(r.stdout.strip(), "[]")

    def test_prompt_probe_produces_nothing_when_the_checker_crashes(self):
        self.crash_checker()
        probe = self.work / ".claude/skills/sit-field-background/tools/oblique_prompt_probe.py"
        try:
            import cv2, numpy, PIL  # noqa: F401, E401
            cmd = [sys.executable, str(probe)]
        except ImportError:
            cmd = ["uv", "run", "--project", str(self.work), "--with", "numpy", "--with", "opencv-python-headless", "--with", "pillow", "python3", str(probe)]
        r = subprocess.run(cmd, env=self.env(), capture_output=True, text=True, cwd=self.work)
        self.assertNotEqual(r.returncode, 0)
        self.assertNotIn('"gated": []', r.stdout)  # ゲートが開いたことにして導出した記録を出さない


class PromptNegationClauseTests(LedgerCopyBase):
    """禁止語の免除は『同じ節（。、区切り）にある否定』だけ。同じ行の別の節の否定で、禁止語（畳）を見逃してはならない。"""

    def rebuild(self):
        r = self.py("ledger_build.py", "build")
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_forbidden_word_beside_a_negation_in_another_clause_is_detected(self):
        self.edit_row("要素", "要素ID", "bed-n", **{"見た目": "い草色の畳敷き（寝室）。ピンクは残さない、壁は描かない。"})
        self.rebuild()
        r = self.verify_prompt()
        self.assertFailsWith(r, "TRM-05", "畳")

    # ---- 再レビュー（中-2）: 回帰アンカーの免除は『決定の要点の節と完全一致』か『決定参照つき展開文』だけ
    def emptied_forbidden_words(self, word):
        rows = self.rows("決定")
        hit = [r for r in rows if r["禁止語"] == word]
        self.assertTrue(hit)
        for r in hit:
            r["禁止語"] = ""
        self.save("決定", rows)

    def test_anchor_detects_one_word_clause_even_when_the_word_is_in_a_decision_text(self):
        # 禁止語を台帳から空にされても、回帰アンカーは固定の期待で畳の漏れを検出する（1語の節が決定の要点の部分文字列でも免除しない）
        self.emptied_forbidden_words("畳")
        self.edit_row("要素", "要素ID", "bed-n", **{"見た目": "床は板張り、畳、ござを敷く。"})
        self.rebuild()
        self.assertFailsWith(self.verify_prompt(), "回帰アンカー tatami", "畳")

    def test_anchor_detects_ammonite_in_a_list_even_with_the_forbidden_word_emptied(self):
        self.emptied_forbidden_words("アンモナイト")
        self.edit_row("要素", "要素ID", "bed-n", **{"見た目": "棚に巻貝、アンモナイト、貝殻を並べる。"})
        self.rebuild()
        self.assertFailsWith(self.verify_prompt(), "回帰アンカー fossil-stone", "アンモナイト")

    def test_anchor_still_exempts_a_decision_referenced_expansion(self):
        self.edit_row("要素", "要素ID", "bed-n", **{"見た目": "畳を描かない。畳を使わない。（決定 TRM.no-tatami）"})
        self.rebuild()
        r = self.verify_prompt()
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_anchor_does_not_exempt_a_reference_to_a_nonexistent_decision(self):
        self.edit_row("要素", "要素ID", "bed-n", **{"見た目": "畳を使う部屋がある。（決定 TRM.no-such-decision）"})
        self.rebuild()
        self.assertFailsWith(self.verify_prompt(), "回帰アンカー tatami")

    # ---- 軽微 b: 名詞だけの節の直後が否定なら同じ否定の列挙とみなす（述語を持つ節は別）
    def test_bare_noun_enumerated_under_a_following_negation_is_not_a_leak(self):
        self.edit_row("要素", "要素ID", "hall-floor", **{"見た目": "濃い茶色の板張り。矢来、名簿は描かない。"})
        self.rebuild()
        r = self.verify_prompt()
        self.assertNotIn("矢来", r.stderr)

    def test_forbidden_word_with_its_own_predicate_before_a_negation_is_still_a_leak(self):
        self.edit_row("要素", "要素ID", "hall-floor", **{"見た目": "濃い茶色の板張り。矢来を置く、名簿は描かない。"})
        self.rebuild()
        self.assertFailsWith(self.verify_prompt(), "矢来")


class SchemaAndSyntaxTests(LedgerCopyBase):
    """列名の綴り間違い・未定義列、未引用スカラー、重複キーは、読み手が黙って受け入れず verify_ledger / ledger_build check で失敗する。"""

    ANCHOR = '"端ID": "TRM-05.door-outside"'

    def test_misspelled_column_is_reported_by_verify_ledger(self):
        self.replace_in_row("端", self.ANCHOR, '"決定参照"', '"決定参考"')
        r = self.verify_ledger()
        self.assertFailsWith(r, "表定義に無い列", "決定参考")

    def test_misspelled_column_is_reported_by_ledger_build_check(self):
        self.replace_in_row("端", self.ANCHOR, '"決定参照"', '"決定参考"')
        r = self.py("ledger_build.py", "check")
        self.assertFailsWith(r, "決定参考")

    def test_ruby_reader_itself_rejects_a_misspelled_column(self):
        # 軽微 a: verify_ledger を経由しない Ruby の読み手（LedgerYaml.read）も列を照合する。黙って空欄扱いにしない
        self.replace_in_row("端", self.ANCHOR, '"決定参照"', '"決定参考"')
        r = subprocess.run([RUBY, "-e", "require './scripts/ledger_yaml'; LedgerYaml.read('端')"], env=self.env(), capture_output=True, text=True, cwd=self.work)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("表定義", r.stderr)
        self.assertIn("決定参考", r.stderr)

    def test_unquoted_scalar_is_rejected_by_ruby_and_python(self):
        self.replace_in_row("端", self.ANCHOR, '"中心": "', '"中心": 841 #"')
        self.assertFailsWith(self.verify_ledger(), "引用符のないスカラー")
        self.assertFailsWith(self.py("ledger_build.py", "check"), "引用符のないスカラー")

    def test_unquoted_date_is_rejected(self):
        self.replace_text("決定", '"日付": "2026-10-21"', '"日付": 2026-10-21')
        self.assertFailsWith(self.verify_ledger(), "引用符のないスカラー")
        self.assertFailsWith(self.py("ledger_build.py", "check"), "引用符のないスカラー")

    def test_duplicate_key_is_rejected_by_ruby_and_python(self):
        self.replace_in_row("端", self.ANCHOR, '  "MAP_ID": "TRM-05"\n', '  "MAP_ID": "TRM-05"\n  "MAP_ID": "TRM-02"\n')
        self.assertFailsWith(self.verify_ledger(), "重複")
        self.assertFailsWith(self.py("ledger_build.py", "check"), "重複")


class RequiredKeysDefinitionTests(LedgerCopyBase):
    """必須キー表の壊れ方（未知の対象テーブル・行の削除・必須度の誤り・条件の列名の綴り間違い）で、検査が黙って無効にならない。"""

    def required(self, map_id="TRM-05"):
        return subprocess.run([RUBY, str(self.work / "scripts/ledger_required_keys.rb"), map_id], env=self.env(), capture_output=True, text=True, cwd=self.work)

    def test_clean_map_passes_the_gate(self):
        self.assertEqual(self.required().returncode, 0)

    def test_unknown_target_table_is_an_error_not_silently_ignored(self):
        self.edit_row("必須キー", "キー", "外形", **{"対象テーブル": "建物X"})
        r = self.required()
        self.assertEqual(r.returncode, 1)
        self.assertIn("対象テーブル『建物X』は検査未対応", r.stdout)
        self.assertFailsWith(self.verify_ledger(), "対象テーブル『建物X』は検査未対応")

    def test_deleting_an_anchor_row_stops_the_gate(self):
        self.delete_rows("必須キー", lambda r: r["対象テーブル"] == "MAP" and r["キー"] == "床材")
        r = self.required()
        self.assertEqual(r.returncode, 1)
        self.assertIn("最低限の行『MAP.床材』が無い", r.stdout)
        self.assertFailsWith(self.verify_ledger(), "最低限の行『MAP.床材』")

    def test_deleting_an_area_anchor_row_stops_the_gate(self):
        self.delete_rows("必須キー", lambda r: r["対象テーブル"] == "エリア" and r["キー"] == "木の種類")
        self.assertIn("最低限の行『エリア.木の種類』が無い", self.required().stdout)

    def test_unknown_required_degree_is_an_error(self):
        self.edit_row("必須キー", "キー", "床材", **{"必須度": "任意"})
        self.assertIn("必須度『任意』", self.required().stdout)

    def test_condition_column_typo_is_reported_by_verify_ledger(self):
        self.edit_row("必須キー", "キー", "屋内外", **{"対象テーブル": "MAP", "条件": "描画方法=斜めモック"})
        self.assertFailsWith(self.verify_ledger(), "条件『描画方法=斜めモック』の列『描画方法』が表定義に無い")


class FreeTextAllTablesTests(LedgerCopyBase):
    """特徴(自由記述)の欄がある全表（エリア・建物関係・建物時期差分・接続・素材 を含む）の記述が、プロンプトの FEATURES 節に出て、
    出なくなったら verify_prompt_reflects_ledger.rb が検出する。"""

    CASES = [
        # (表, キー列, キー値, 検査するMAP, 目印)
        ("エリア", "エリアID", "teramachi", "TRM-05", "エリア目印"),
        ("建物関係", "通番", "2", "TRM-05", "建物関係目印"),
        ("建物時期差分", "時期", "fire", "TRM-05-fire", "建物時期差分目印"),
        ("接続", "端A", "TRM-05.door-outside", "TRM-05", "接続目印"),
        ("素材", "素材ID", "A-001", "TRM-04", "素材目印"),
    ]

    def query(self, map_id):
        return self.py("ledger_query.py", map_id).stdout

    def test_each_table_free_text_reaches_the_features_section(self):
        for table, key, val, map_id, mark in self.CASES:
            with self.subTest(table=table):
                self.edit_row(table, key, val, **{"特徴(自由記述)": mark})
                self.assertIn(mark, self.query(map_id))

    def test_verify_prompt_detects_a_table_whose_free_text_is_dropped(self):
        tools = self.work / ".claude/skills/sit-field-background/tools/ledger_query.py"
        for table, key, val, map_id, mark in self.CASES:
            with self.subTest(table=table):
                self.edit_row(table, key, val, **{"特徴(自由記述)": mark})
        text = tools.read_text(encoding="utf-8")
        i, j = text.index("        for r in self.T[\"建物関係\"]:"), text.index("        for r in self.T[\"要素\"]:")
        k, l = text.index("        for r in self.T[\"接続\"]:"), text.index("        for a in self.inherits(map_id):\n            if a[L.FREE]")
        # 建物関係・建物時期差分・接続・素材の導出を壊した状態
        tools.write_text(text[:i] + text[j:k] + text[l:], encoding="utf-8")
        r = self.verify_prompt()
        self.assertFailsWith(r, "建物関係 2", "建物時期差分 BLD-TRM-jukyo/fire", "接続 TRM-05.door-outside", "素材 A-001")

    def test_verify_prompt_detects_a_dropped_area_free_text(self):
        self.edit_row("エリア", "エリアID", "teramachi", **{"特徴(自由記述)": "エリア目印"})
        tools = self.work / ".claude/skills/sit-field-background/tools/ledger_query.py"
        text = tools.read_text(encoding="utf-8")
        old = "        if ar and ar[L.FREE]:\n"
        self.assertIn(old, text)
        tools.write_text(text.replace(old, "        if False:\n"), encoding="utf-8")
        self.assertFailsWith(self.verify_prompt(), "エリア teramachi")

    def test_new_free_text_table_without_derivation_is_reported(self):
        # 自由記述の欄を持つ表が増えたのに導出・検査の対象に足されていない状態
        p = self.work / ".claude/skills/sit-field-background/tools/ledger_io.py"
        text = p.read_text(encoding="utf-8")
        old = '"未決": ["未決ID", "対象テーブル", "対象ID", "キー", "内容", "状態", "解決決定ID"]'
        self.assertIn(old, text)
        p.write_text(text.replace(old, old[:-1] + ', FREE]'), encoding="utf-8")
        self.assertFailsWith(self.verify_ledger(), "表 未決 に特徴(自由記述)の欄がある")


class StatusVocabularyTests(LedgerCopyBase):
    """決定・採用要素・素材の『状態』は語彙で検査する。語彙外（有効化 など）の値が、黙ってプロンプトから消える状態を許さない。"""

    def vocab_errors(self):
        # 最小 fixture には docs 全体が無いので、ファイル配置の入口などの別の失敗は混ざる。語彙の失敗だけを見る
        return [ln for ln in self.verify_ledger().stderr.splitlines() if "語彙（" in ln]

    def test_clean_ledger_has_no_vocabulary_errors(self):
        self.assertEqual(self.vocab_errors(), [])

    def test_decision_state_outside_vocabulary_is_reported(self):
        self.edit_row("決定", "決定ID", "TRM.no-tatami", **{"状態": "有効化"})
        self.assertFailsWith(self.verify_ledger(), "『状態』の値『有効化』が語彙（決定状態）に無い")

    def test_adopted_element_state_outside_vocabulary_is_reported(self):
        self.edit_row("採用要素", "採用要素ID", "TRM-04.door-design", **{"状態": "有効化"})
        self.assertFailsWith(self.verify_ledger(), "『状態』の値『有効化』が語彙（採用要素状態）に無い")

    def test_adopted_element_state_with_annotation_is_allowed(self):
        self.edit_row("採用要素", "採用要素ID", "TRM-04.door-design", **{"状態": "記録（確定待ち）"})
        self.assertEqual(self.vocab_errors(), [])

    def test_material_state_outside_vocabulary_is_reported(self):
        self.edit_row("素材", "素材ID", "A-001", **{"状態": "採用済み"})
        self.assertFailsWith(self.verify_ledger(), "『状態』の値『採用済み』が語彙（素材状態）に無い")


class ConnectionEndpointExistsTests(LedgerCopyBase):
    """接続が、端表に行があるMAPの存在しない端を指していたら失敗する（仮想端点・端表にまだ行が無いMAPは対象外）。"""

    def end_errors(self):
        return [ln for ln in self.verify_ledger().stderr.splitlines() if "存在しない端を指す接続" in ln]

    def test_clean_ledger_has_no_dangling_connection(self):
        self.assertEqual(self.end_errors(), [])

    def test_connection_to_a_nonexistent_edge_is_reported(self):
        self.edit_row("接続", "端A", "TRM-05.door-hall", **{"端A": "TRM-05.door-hall-typo"})
        self.assertTrue(any("TRM-05.door-hall-typo" in ln for ln in self.end_errors()), self.verify_ledger().stderr)

    def test_virtual_port_of_the_connection_diagram_is_allowed(self):
        self.assertFalse(any("event-kiss" in ln for ln in self.end_errors()))


class SourceQuoteTests(IssueAuditBase):
    """audit_issue_decisions.rb --check-quotes: 決定.逐語の各引用が、出典URL（; 区切り複数）のどれかのコメント本文に実在する。
    コメントは --from-json のキャッシュ JSON から読む（オフライン）。"""

    def setUp(self):
        super().setUp()
        self.data = {"issues": [{"number": 7, "html_url": f"{self.URL}/7", "body": "Issue本文「本文にだけある発言です、ここ」", "created_at": "2026-10-01T00:00:00Z"}],
                     "comments": [self.comment(201, 7, "## 決定\n逐語: 「机の材質など、必ず指定が必要なものは強制する」"),
                                  self.comment(202, 7, "## 別の決定\n逐語: 「化石はゴツゴツした茶色と黒の石にしろ」（入れ子の『閉鎖』は **強調** 付き）"),
                                  self.comment(203, 7, "## 何もない\nただの作業記録")]}

    def decision(self, did, verbatim, urls):
        dec = dict.fromkeys(ledger_io.SCHEMA["決定"], "")
        return dict(dec, **{"決定ID": did, "決定の要点": "要点", "逐語": verbatim, "出典": "Issue #7", "出典URL": ";".join(urls), "状態": "有効"})

    def check(self, *decisions):
        self.write_table("決定", list(decisions))
        return self.audit("--check-quotes")

    def u(self, cid):
        return f"{self.URL}/7#issuecomment-{cid}"

    def test_quote_present_in_the_cited_comment_passes(self):
        r = self.check(self.decision("D.ok", "「机の材質など、必ず指定が必要なものは強制する」", [self.u(201)]))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("PASS", r.stdout)

    def test_url_pointing_at_a_comment_without_the_quote_fails_and_names_the_real_one(self):
        r = self.check(self.decision("D.wrong", "「机の材質など、必ず指定が必要なものは強制する」", [self.u(203)]))
        self.assertEqual(r.returncode, 1)
        self.assertIn("決定 D.wrong", r.stderr)
        self.assertIn("issuecomment-201", r.stderr)  # 実在するコメントの候補を示す

    def test_altered_word_in_the_verbatim_fails(self):
        r = self.check(self.decision("D.alt", "「机の材質とか、必ず指定が必要なものは強制する」", [self.u(201)]))
        self.assertEqual(r.returncode, 1)
        self.assertIn("どのコメントにも無い", r.stderr)

    def test_each_quote_may_live_in_a_different_comment_of_the_url_list(self):
        v = "「机の材質など、必ず指定が必要なものは強制する」（2026-10-23）「化石はゴツゴツした茶色と黒の石にしろ」"
        self.assertEqual(self.check(self.decision("D.two", v, [self.u(201), self.u(202)])).returncode, 0)
        r = self.check(self.decision("D.one", v, [self.u(201)]))  # 2つ目の引用を含むコメントが URL に無い
        self.assertEqual(r.returncode, 1)
        self.assertIn("化石はゴツゴツ", r.stderr)

    def test_nested_brackets_and_emphasis_are_normalised(self):
        v = "「入れ子の『閉鎖』は 強調 付き」"
        self.assertEqual(self.check(self.decision("D.nest", "「化石はゴツゴツした茶色と黒の石にしろ」" + v, [self.u(202)])).returncode, 0)

    def test_issue_body_url_is_accepted_as_a_source(self):
        r = self.check(self.decision("D.body", "「本文にだけある発言です、ここ」", [f"{self.URL}/7"]))
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_missing_url_and_non_issue_url_fail(self):
        r = self.check(self.decision("D.nourl", "「机の材質など、必ず指定が必要なものは強制する」", []))
        self.assertEqual(r.returncode, 1)
        self.assertIn("出典URLが無い", r.stderr)
        r = self.check(self.decision("D.blob", "「机の材質など、必ず指定が必要なものは強制する」", ["https://github.com/kako-jun/sit-by-me/blob/main/README.md"]))
        self.assertEqual(r.returncode, 1)
        self.assertIn("Issue のコメント", r.stderr)

    # ---- 再レビュー指摘（中-1）: 偽の逐語を通さない
    def test_short_quote_needs_an_exact_bracketed_match(self):
        self.data["comments"] += [self.comment(204, 7, "## 回答\nkako-jun「A,A」"), self.comment(205, 7, "## 別\nxA,Ay の話")]
        self.assertEqual(self.check(self.decision("D.short", "「A,A」（2問への回答）", [self.u(204)])).returncode, 0)
        r = self.check(self.decision("D.fakeshort", "「B,B」（2問への回答）", [self.u(204)]))  # A,A → B,B の改変
        self.assertEqual(r.returncode, 1)
        self.assertIn("B,B", r.stderr)
        r = self.check(self.decision("D.loose", "「A,A」", [self.u(205)]))  # 括弧なしの部分一致では通さない
        self.assertEqual(r.returncode, 1)

    def test_outer_double_corner_brackets_are_checked_as_quotes(self):
        r = self.check(self.decision("D.corner", "『机の材質など、必ず指定が必要なものは強制する』", [self.u(201)]))
        self.assertEqual(r.returncode, 0, r.stderr)
        r = self.check(self.decision("D.fakecorner", "『人間の三人ぶんくらいの幅の扉にしろ』", [self.u(201)]))
        self.assertEqual(r.returncode, 1)
        self.assertIn("三人ぶん", r.stderr)

    def test_decision_without_checkable_quote_fails_unless_explicitly_marked(self):
        r = self.check(self.decision("D.stripped", "机の材質など、必ず指定が必要なものは強制する", [self.u(201)]))  # 引用符を外した偽の文
        self.assertEqual(r.returncode, 1)
        self.assertIn("D.stripped", r.stderr)
        r = self.check(self.decision("D.fakeplain", "人間の三人ぶんくらいの幅の扉にしろ", [self.u(201)]))
        self.assertEqual(r.returncode, 1)
        r = self.check(self.decision("D.marked", "（逐語の引用なし: Issue記録の決定文）扉の幅は2人分", [self.u(201)]))
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_pass_message_reports_the_actual_scope_and_the_exceptions(self):
        r = self.check(self.decision("D.a", "「机の材質など、必ず指定が必要なものは強制する」「化石はゴツゴツした茶色と黒の石にしろ」", [self.u(201), self.u(202)]),
                       self.decision("D.b", "（逐語の引用なし: Issue記録の決定文）扉の幅は2人分", [self.u(201)]))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("決定2件中、照合1件・引用2個・例外1件", r.stdout)
        self.assertIn("D.b", r.stdout)

    def test_real_ledger_decisions_all_have_issue_source_urls(self):
        # 実リポの決定表: 出典が Issue のものは全て Issue のコメント/本文の URL（; 区切り）で、出典の Issue 番号と一致する（verify_ledger.rb が検査）
        rows = ledger_io.parse("決定", (ROOT / "docs/ledger/決定.yaml").read_text(encoding="utf-8"))
        for d in rows:
            if d["出典"].startswith("Issue"):
                urls = [u for u in d["出典URL"].split(";") if u]
                self.assertTrue(urls, d["決定ID"])
                nums = sorted({n for n in __import__("re").findall(r"#(\d+)", d["出典"])})
                self.assertEqual(nums, sorted({__import__("re").search(r"/issues/(\d+)", u).group(1) for u in urls}), d["決定ID"])


class DecisionSourceTests(LedgerCopyBase):
    """決定の出典URL（; 区切り複数）の形式検査（verify_ledger.rb）と、レビューで見つかった決定表の誤りの回帰。"""

    def source_errors(self):
        return [ln for ln in self.verify_ledger().stderr.splitlines() if ln.startswith("FAIL") and "決定" in ln and ("出典" in ln)]

    def test_clean_sources_pass(self):
        self.assertEqual(self.source_errors(), [])

    def test_multiple_urls_across_issues_are_accepted(self):
        self.edit_row("決定", "決定ID", "TRM.no-tatami", **{"出典": "Issue #51・#144", "出典URL": "https://github.com/kako-jun/sit-by-me/issues/144#issuecomment-6359895953;https://github.com/kako-jun/sit-by-me/issues/51#issuecomment-6306972440"})
        self.assertEqual(self.source_errors(), [])

    def test_issue_number_in_source_must_match_the_urls(self):
        self.edit_row("決定", "決定ID", "TRM.no-tatami", **{"出典": "Issue #144"})  # URL に #51 が増えたのに出典が #144 のまま
        self.edit_row("決定", "決定ID", "TRM.no-tatami", **{"出典URL": "https://github.com/kako-jun/sit-by-me/issues/144#issuecomment-6359895953;https://github.com/kako-jun/sit-by-me/issues/51#issuecomment-6306972440"})
        self.assertTrue(any("食い違う" in ln and "TRM.no-tatami" in ln for ln in self.source_errors()))

    def test_non_issue_url_for_an_issue_source_is_rejected(self):
        self.edit_row("決定", "決定ID", "TRM.no-tatami", **{"出典URL": "https://github.com/kako-jun/sit-by-me/blob/main/docs/README.md"})
        self.assertTrue(any("Issue のコメント" in ln and "TRM.no-tatami" in ln for ln in self.source_errors()))

    # ---- 実リポの決定表の回帰（レビュー指摘）
    def real(self, table):
        return ledger_io.parse(table, (ROOT / f"docs/ledger/{table}.yaml").read_text(encoding="utf-8"))

    def test_ledger_yaml_decision_exists_and_ledger_db_is_corrected(self):
        dec = {d["決定ID"]: d for d in self.real("決定")}
        y = dec["TRM.ledger-yaml"]
        self.assertEqual(y["状態"], "有効")
        self.assertIn("issuecomment-6360639772", y["出典URL"])
        self.assertIn("「csvが本当にいいのか？yamlとかのほうが管理しやすいのではないのか」", y["逐語"])
        db = dec["TRM.ledger-db"]
        self.assertEqual((db["状態"], db["置換先"]), ("訂正済み", "TRM.ledger-yaml"))

    def test_required_keys_verbatim_is_the_original_wording(self):
        d = next(d for d in self.real("決定") if d["決定ID"] == "TRM.required-keys")
        self.assertIn("机の材質など、", d["逐語"])
        self.assertNotIn("机の材質とか、", d["逐語"])

    def test_unconfirmed_mask_decision_is_an_open_item_not_a_decision(self):
        self.assertNotIn("TRM-04.mask-confirmed", [d["決定ID"] for d in self.real("決定")])
        self.assertTrue(any(u["対象ID"] == "TRM-04" and "歩行マスク・出口" in u["キー"] and u["状態"] == "未決" for u in self.real("未決")))

    def test_u050_and_main_door_record_the_commander_default_not_a_kako_jun_statement(self):
        # 再レビュー中-3: #144 comment 6355539302 に『司令塔の既定』として存在する。『Issue全コメントに該当なし』は誤り
        u = next(u for u in self.real("未決") if u["未決ID"] == "U-050")
        self.assertIn("6355539302", u["内容"])
        self.assertIn("司令塔", u["内容"])
        self.assertNotIn("該当なし", u["内容"])
        edges = {e["端ID"]: e for e in self.real("端")}
        for eid in ("TRM-04.door-south", "TRM-03.door-main"):
            self.assertEqual(edges[eid]["状態"], "既定(要確認)", eid)
            self.assertIn("U-050", edges[eid]["備考"], eid)
        self.assertNotIn("該当なし", (ROOT / "docs/ledger/handoff/HANDOFF.md").read_text(encoding="utf-8"))

    def test_review_followups_are_recorded_in_handoff_and_readme(self):
        handoff = (ROOT / "docs/ledger/handoff/HANDOFF.md").read_text(encoding="utf-8")
        readme = (ROOT / ".claude/skills/sit-field-background/tools/README.md").read_text(encoding="utf-8")
        self.assertIn("squash マージし、マージ後にこのブランチ", handoff)  # 軽微 e
        self.assertIn("元の発言そのものとの一致は保証しない", handoff)  # 軽微 f
        self.assertIn("元の発言そのものとの一致は保証しない", readme)
        self.assertIn("禁止語の節分割", readme)  # 軽微 b の既知の制約
        self.assertIn("decisions-59.jsonl", handoff)  # 軽微 c: 行き先
        self.assertFalse((ROOT / "docs/ledger/handoff/decisions-59.jsonl").exists())
        reason = next(r for r in self.real("ファイル配置") if r["配置ID"] == "ledger-handoff")["許可リスト理由"]
        self.assertIn("第2段階以降", reason)
        self.assertNotIn("第1段階完了時", reason)

    def test_decision_source_url_is_unconditionally_required(self):
        # 軽微 d: 形骸化した条件『出典!=会話（Issue #144 に記録）』を整理。全決定が Issue 出典なので意味は変わらない
        rk = next(r for r in self.real("必須キー") if r["対象テーブル"] == "決定" and r["キー"] == "出典URL")
        self.assertEqual((rk["必須度"], rk["条件"]), ("必須", ""))
        self.assertTrue(all(d["出典URL"] for d in self.real("決定")))

    def test_decision_notes_have_no_leading_whitespace(self):
        for d in self.real("決定"):
            self.assertEqual(d["備考"], d["備考"].lstrip(), d["決定ID"])

    def test_plan_input_hash_follows_the_referenced_decision_wording_only(self):
        code = ("import ledger_build as B; T = B.tables(); print(B.input_hash(B.input_rows(T, 'TRM-05')))")
        def h():
            return subprocess.run([sys.executable, "-c", code], env=self.env(PYTHONPATH=str(self.work / ".claude/skills/sit-field-background/tools")), capture_output=True, text=True, cwd=self.work).stdout.strip()
        base = h()
        self.assertTrue(base)
        self.edit_row("決定", "決定ID", "TRM-05.door-back", **{"出典URL": "https://github.com/kako-jun/sit-by-me/issues/144#issuecomment-6357220251"})
        self.assertEqual(h(), base)  # メタデータを直しても変わらない
        self.edit_row("決定", "決定ID", "TRM-05.door-back", **{"決定の要点": "別の要点"})
        self.assertNotEqual(h(), base)  # 参照された決定の要点を直すと変わる


class TemplateOutputTests(LedgerCopyBase):
    """ledger_build.py template は台帳と同じ YAML で出す（CSV でなく）。出力は台帳の表としてそのまま読める。"""

    def test_template_is_yaml_that_the_ledger_reader_accepts(self):
        for kind, table in (("map", "MAP"), ("area", "エリア")):
            r = self.py("ledger_build.py", "template", kind, "X-01")
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertNotIn(",", r.stdout.splitlines()[0])  # CSV のヘッダ行ではない
            rows = ledger_io.parse(table, r.stdout)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0][ledger_io.SCHEMA[table][0]], "X-01")
            self.assertEqual(set(rows[0]), set(ledger_io.SCHEMA[table]))

    def test_unknown_kind_is_an_error(self):
        self.assertNotEqual(self.py("ledger_build.py", "template", "building", "X-01").returncode, 0)


class ConfirmedEdgeBasisTests(LedgerCopyBase):
    """端の状態が『確定』なら根拠の決定（決定参照）が要る。接続.yaml の円環・勝手口の記述が現状に合っている。"""

    def edge_errors(self):
        return [ln for ln in self.verify_ledger().stderr.splitlines() if "状態が『確定』なのに決定参照が無い" in ln]

    def test_confirmed_edges_all_have_a_decision_basis(self):
        self.assertEqual(self.edge_errors(), [])

    def test_confirmed_edge_without_decision_is_reported(self):
        self.edit_row("端", "端ID", "TRM-02.door-west", **{"決定参照": ""})
        errs = self.edge_errors()
        self.assertTrue(any("TRM-02.door-west" in ln for ln in errs), errs)

    def test_default_state_edge_does_not_need_a_decision(self):
        self.edit_row("端", "端ID", "TRM-02.door-west", **{"決定参照": "", "状態": "既定(要確認)"})
        self.assertEqual(self.edge_errors(), [])

    def test_loop_connections_cite_the_loop_decision_and_back_door_note_is_current(self):
        rows = {(r["端A"], r["端B"]): r for r in ledger_io.parse("接続", (ROOT / "docs/ledger/接続.yaml").read_text(encoding="utf-8"))}
        for key in (("TRM-15.bottom", "TRM-06.top"), ("TRM-06.right", "TRM-16.left")):
            self.assertIn("TRM-06.loop", rows[key]["決定参照"].split(";"))
        note = rows[("TRM-06.right", "TRM-16.left")]["主路・状態"]
        self.assertNotIn("台帳になくTBD", note)
        self.assertIn("TRM-05.door-back⇄TRM-06.door-house", note)


class GatedMapsScopeTests(LedgerCopyBase):
    """ゲートで止まる MAP（必須キー未決。現状は無し。TRM-06〜17 は #191 で解消）はプロンプト反映検査の対象外。未決が解消してゲートが開いた MAP は自動で対象に入る。
    対象外であることは INDEX と tools/README に明記されている。"""

    def test_gated_maps_are_skipped_and_reported(self):
        self.edit_row("MAP", "MAP_ID", "TRM-15", **{"壁材": "未決(要確認)"})
        r = self.verify_prompt()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("ゲートで停止（対象外）: TRM-15", r.stdout)
        self.assertNotIn("TRM-15", r.stdout.split("検査したMAP")[1])

    def test_a_map_whose_undecided_keys_are_resolved_enters_the_check_automatically(self):
        # 生成済みの TRM-02 に必須キーの未決を作ってゲートを閉じ（対象外になる）、解消して開ける（自動で対象に戻る）。
        # 屋外MAP（TRM-06〜17）も同じ（台帳の現状でゲートが開いて検査対象に入っている。test_clean_ledger_passes_and_reports_gated_maps）
        original = next(r for r in self.rows("MAP") if r["MAP_ID"] == "TRM-02")["壁材"]
        self.edit_row("MAP", "MAP_ID", "TRM-02", **{"壁材": "未決(要確認)"})
        closed = self.verify_prompt()
        self.assertIn("ゲートで停止（対象外）: TRM-02", closed.stdout)
        self.assertNotIn("TRM-02", closed.stdout.split("検査したMAP")[1].splitlines()[0])
        # 回帰アンカーの対象MAPがゲートで止まったら、検査できないこと自体をエラーにする（黙って素通りさせない）
        self.assertNotEqual(closed.returncode, 0)
        self.assertIn("このMAPがゲートで止まっていて検査できない", closed.stderr)
        self.edit_row("MAP", "MAP_ID", "TRM-02", **{"壁材": original})
        opened = self.verify_prompt()
        self.assertEqual(opened.returncode, 0, opened.stderr)
        self.assertNotIn("ゲートで停止（対象外）: TRM-02", opened.stdout)
        self.assertIn("TRM-02", opened.stdout.split("検査したMAP")[1])

    def test_scope_is_stated_in_index_and_tools_readme(self):
        for rel in (".claude/skills/sit-field-background/tools/README.md", "docs/INDEX.md"):
            text = (ROOT / rel).read_text(encoding="utf-8")
            self.assertIn("TRM-06〜17", text, rel)
            self.assertIn("プロンプト反映検査の対象外", text, rel)


class HandoffAndDocsFollowTests(unittest.TestCase):
    """引き継ぎ文書（HANDOFF.md）の数値が台帳の実測と一致し、矛盾せず、handoff/ の削除手順がある。tools/README の渡り廊下の説明が現行。"""

    HANDOFF = (ROOT / "docs/ledger/handoff/HANDOFF.md").read_text(encoding="utf-8")

    def rows(self, table):
        return ledger_io.parse(table, (ROOT / f"docs/ledger/{table}.yaml").read_text(encoding="utf-8"))

    def test_numbers_match_the_ledger(self):
        import re
        dec = self.rows("決定")
        valid = sum(1 for d in dec if d["状態"] == "有効")
        section = re.search(r"(?ms)^# 現行台帳との照合[^\n]*\n(.*?)(?=^# |\Z)", self.HANDOFF)
        self.assertIsNotNone(section, "現在値と歴史的スナップショットを区別する見出しが必要")
        current = section[1]
        m = re.search(r"決定(\d+)（有効(\d+)・訂正済み(\d+)）", current)
        self.assertEqual((int(m[1]), int(m[2]), int(m[3])), (len(dec), valid, len(dec) - valid))
        self.assertEqual(int(re.search(r"`未決.yaml` に(\d+)件", current)[1]), len(self.rows("未決")))
        self.assertEqual(int(re.search(r"ファイル配置.yaml`（(\d+)規則", current)[1]), len(self.rows("ファイル配置")))
        self.assertIn(f"表（docs/ledger/）{len(list((ROOT / 'docs/ledger').glob('*.yaml')))}枚", current)
        # Phase-one counts are evidence about that phase, never current totals.
        history = self.HANDOFF.split("## どこまで済んだか（このブランチの実装）", 1)[1].split("## ", 1)[0]
        for fact in ("歴史的スナップショット", "決定68（有効65・訂正済み3）", "MAP17行", "未決50"):
            self.assertIn(fact, history)

    def test_atlas_connection_count_is_consistent(self):
        import re
        counts = set(re.findall(r"129MAP/(\d+)接続", self.HANDOFF))
        self.assertEqual(counts, {"137"})  # 以前は 136 と 137 が同居していた

    def test_handoff_removal_procedure_is_written(self):
        for needle in ("handoff/ の削除手順", "git mv", "DESIGN.md", "known-failures-baseline.txt", "curation-scripts/", "ledger_index.py build"):
            self.assertIn(needle, self.HANDOFF)

    def test_tools_readme_corridor_matches_the_current_decisions(self):
        text = (ROOT / ".claude/skills/sit-field-background/tools/README.md").read_text(encoding="utf-8")
        self.assertNotIn("床＋四隅の柱＋屋根の板だけの開放した通路", text)
        self.assertIn("TRM-03.corridor-open は訂正済み", text)
        dec = {d["決定ID"]: d for d in self.rows("決定")}
        self.assertEqual((dec["TRM-03.corridor-open"]["状態"], dec["TRM-03.corridor-open"]["置換先"]), ("訂正済み", "TRM.building-shared"))

    def test_known_constraint_about_font_on_macos_is_stated(self):
        text = (ROOT / ".claude/skills/sit-field-background/tools/README.md").read_text(encoding="utf-8")
        self.assertIn("既知の制約", text)
        self.assertIn("macOS では mock 段", text)


class NoLocalPathsTests(unittest.TestCase):
    """公開リポに入るファイルへ、ローカルの絶対パス（/Users/kako-jun・/home/kako-jun）と codex のセッションIDを書かない。
    対象: 引き継ぎ（handoff/ と curation-scripts）・斜めモックの E2 記録（codex ログ・metrics.json・.gi 一覧）。汎用表記は <repo>・<home>・<session-id>。"""

    UUID = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"

    def files(self):
        out = [p for p in (ROOT / "docs/ledger/handoff").rglob("*") if p.is_file() and "__pycache__" not in p.parts]
        e2 = ROOT / "docs/production/oblique-mocks"
        out += [p for p in e2.rglob("*") if p.is_file() and "e2" in p.parts and (p.name.startswith("codex-take") or p.name == "metrics.json" or p.name.startswith(".gi-"))]
        return out

    def test_no_absolute_home_paths(self):
        import re
        bad = [str(p.relative_to(ROOT)) for p in self.files() if re.search(r"/(?:Users|home)/kako-jun", p.read_text(encoding="utf-8", errors="replace"))]
        self.assertEqual(bad, [])

    def test_no_codex_session_ids(self):
        import re
        pat = re.compile(r"(?:generated_images/|session id:\s*|exec-)" + self.UUID)
        bad = [str(p.relative_to(ROOT)) for p in self.files() if pat.search(p.read_text(encoding="utf-8", errors="replace"))]
        self.assertEqual(bad, [])

    def test_gi_listings_are_not_tracked(self):
        self.assertEqual([p for p in self.files() if p.name.startswith(".gi-")], [])
        self.assertIn(".gi-", (ROOT / ".gitignore").read_text(encoding="utf-8"))

    def test_metrics_json_is_still_valid_json(self):
        for p in (ROOT / "docs/production/oblique-mocks").rglob("metrics.json"):
            json.loads(p.read_text(encoding="utf-8"))
