"""台帳 → name-name の一枚絵フィールド md の生成（scripts/field_md.py, #250）の検査。

実リポの play/ を汚さないよう、必要な台帳・play/・目録・素材のファイル名だけを一時ディレクトリへ写し、
field_md のモジュール変数（ROOT/EVENTS/OUT/FORMS）を差し替えて実行する。
実行: uv run python3 -m unittest tests.test_field_md
"""
import contextlib
import io
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

REAL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REAL / "scripts"))
import field_md  # noqa: E402
import resume_saves  # noqa: E402

EVENT_IDS = field_md.FIELD_EVENTS


class FieldMdCase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        ledger = self.tmp / "docs/ledger"
        (ledger / "イベント").mkdir(parents=True)
        for ident in EVENT_IDS:
            shutil.copy(REAL / "docs/ledger/イベント" / f"{ident}.yaml", ledger / "イベント")
        for name in ("敵", "人物", "魔法", "サンプルMAP", "素材", "戦闘背景"):
            shutil.copy(REAL / "docs/ledger" / f"{name}.yaml", ledger)
        shutil.copytree(REAL / "docs/ledger/再開点", ledger / "再開点")
        shutil.copytree(REAL / "play", self.tmp / "play")
        shutil.copytree(REAL / "assets/field", self.tmp / "assets/field")
        # 目録の生成は素材のファイル名しか見ないので、空ファイルで足りる
        for cid in field_md.PARTY:
            for sub in ("poses", "walk"):
                src = REAL / "assets/images/characters" / cid / sub
                dst = self.tmp / "assets/images/characters" / cid / sub
                dst.mkdir(parents=True, exist_ok=True)
                for f in src.glob("*.webp"):
                    (dst / f.name).touch()
        # サンプル場面が引く画像は実在だけを見るので、空ファイルで足りる（実寸・画素は SampleField.test_spawn_is_walkable_in_real_mask が実物で見る）
        for rel in ("fields/reference/teramachi-grounds-exterior-trm03-adopted.webp", "fields/masks/TRM-03-exterior-mask.webp",
                    "fields/play/bg012.webp", *[f"enemies/{m}.webp" for m in field_md.SAMPLE_ENEMY_STATS]):
            path = self.tmp / "assets/images" / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.touch()
        # 感情吹き出しの宣言は素材の実在だけを見るので、空ファイルで足りる
        emo = self.tmp / "assets/images/effects/field-emotion"
        emo.mkdir(parents=True)
        for name in field_md.EMOTIONS.values():
            (emo / f"field-emotion-{name}.png").touch()
        saved = {k: getattr(field_md, k) for k in ("ROOT", "EVENTS", "OUT", "FORMS")}
        self.addCleanup(lambda: [setattr(field_md, k, v) for k, v in saved.items()])
        saved_rs = {k: getattr(resume_saves, k) for k in ("ROOT", "DIR")}
        self.addCleanup(lambda: [setattr(resume_saves, k, v) for k, v in saved_rs.items()])
        resume_saves.ROOT = self.tmp
        resume_saves.DIR = self.tmp / "docs/ledger/再開点"
        field_md.ROOT = self.tmp
        field_md.EVENTS = self.tmp / "docs/ledger/イベント"
        field_md.OUT = self.tmp / "play"
        field_md.FORMS = self.tmp / "assets/field/sit-character-forms.json"

    def event_path(self, ident):
        return self.tmp / "docs/ledger/イベント" / f"{ident}.yaml"

    def edit_event(self, ident, old, new):
        path = self.event_path(ident)
        text = path.read_text(encoding="utf-8")
        self.assertIn(old, text)
        path.write_text(text.replace(old, new, 1), encoding="utf-8")

    def out(self, relative):
        return dict((r, o) for _, _, r, _, o in field_md.outputs())[relative].decode("utf-8")

    def run_check(self):
        with contextlib.redirect_stdout(io.StringIO()):
            field_md.check()


class Determinism(FieldMdCase):
    def test_outputs_twice_identical(self):
        self.assertEqual(field_md.outputs(), field_md.outputs())

    def test_baseline_check_passes(self):
        # 以降の失敗系テストが「元から壊れていた」のではないことの前提
        self.run_check()


class Orphans(FieldMdCase):
    def test_orphan_md_and_other_extension_stop_preflight(self):
        for name in ("events/ghost.md", "notes.txt", "events/sub/deep.png"):
            with self.subTest(name=name):
                path = self.tmp / "play" / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("x", encoding="utf-8")
                with self.assertRaises(SystemExit) as cm:
                    field_md.preflight(field_md.outputs())
                self.assertIn(name, str(cm.exception))
                path.unlink()
        field_md.preflight(field_md.outputs())  # 消せば通る


class OverwriteGuard(FieldMdCase):
    def test_md_without_marker_is_refused(self):
        (self.tmp / "play/data.md").write_text("手書きのメモ\n", encoding="utf-8")
        with self.assertRaises(SystemExit) as cm:
            field_md.preflight(field_md.outputs())
        self.assertIn("play/data.md", str(cm.exception))

    def test_forms_json_without_generated_key_is_refused(self):
        field_md.FORMS.write_text(json.dumps({"characters": {}}), encoding="utf-8")
        with self.assertRaises(SystemExit) as cm:
            field_md.preflight(field_md.outputs())
        self.assertIn("sit-character-forms.json", str(cm.exception))

    def test_forms_json_with_generated_key_is_accepted(self):
        field_md.preflight(field_md.outputs())


class CheckFailure(FieldMdCase):
    def test_one_char_edit_in_each_play_md_fails_check(self):
        for path in sorted((self.tmp / "play").rglob("*.md")):
            with self.subTest(path=path.name):
                original = path.read_text(encoding="utf-8")
                path.write_text(original + "x", encoding="utf-8")
                with self.assertRaises(SystemExit) as cm:
                    self.run_check()
                self.assertIn("stale", str(cm.exception))
                path.write_text(original, encoding="utf-8")
        self.run_check()

    def test_edited_forms_json_fails_check(self):
        field_md.FORMS.write_text(field_md.FORMS.read_text(encoding="utf-8") + " ", encoding="utf-8")
        with self.assertRaises(SystemExit):
            self.run_check()

    def test_ledger_change_makes_check_fail(self):
        self.edit_event("opening_battle", '"名称": "お遊戯会の劇戦闘"', '"名称": "別名"')
        with self.assertRaises(SystemExit):
            self.run_check()

    # build_ledger.py check は台帳全体（ほかの派生物・生成物登録）も見るため、ここでは同じ outputs/preflight を
    # 共有する範囲（field_md.check）で検査する。フル実行は別途。


class InputValidation(FieldMdCase):
    def test_position_not_x_y(self):
        for bad in ("700", "700;480", "a,b", "", "700, 480"):
            with self.subTest(bad=bad):
                path = self.event_path("play_cancelled_promise")
                original = path.read_text(encoding="utf-8")
                path.write_text(original.replace('"出現位置": "1330,480"', f'"出現位置": "{bad}"'), encoding="utf-8")
                with self.assertRaises(SystemExit) as cm:
                    field_md.outputs()
                self.assertIn("出現位置", str(cm.exception))
                path.write_text(original, encoding="utf-8")

    def test_destination_without_position(self):
        path = self.event_path("play_cancelled_promise")
        path.write_text(path.read_text(encoding="utf-8").replace('"出現位置": "1330,480"\n', ""), encoding="utf-8")
        with self.assertRaises(SystemExit) as cm:
            field_md.outputs()
        self.assertIn("出現位置", str(cm.exception))

    def test_destination_unknown_event(self):
        self.edit_event("evacuation_after_play", '"行き先": "play_cancelled_promise"', '"行き先": "no_such_event"')
        with self.assertRaises(SystemExit):
            field_md.outputs()

    def test_destination_without_closing_tag(self):
        self.edit_event("evacuation_after_play", "[/イベント]", "[/end]")
        with self.assertRaises(SystemExit) as cm:
            field_md.outputs()
        self.assertIn("[/イベント]", str(cm.exception))

    def test_trigger_must_be_empty_or_allowed(self):
        for bad in ("毎回", "場面開始・1回 ", "場面開始・毎回", "auto"):
            with self.subTest(bad=bad):
                path = self.event_path("play_cancelled_promise")
                original = path.read_text(encoding="utf-8")
                path.write_text(original.replace('"発火条件": "場面開始・1回"', f'"発火条件": "{bad}"'), encoding="utf-8")
                # 末尾空白だけは strip で許容される
                if bad.strip() == field_md.TRIGGER_AUTO_ONCE:
                    field_md.outputs()
                else:
                    with self.assertRaises(SystemExit) as cm:
                        field_md.outputs()
                    self.assertIn("発火条件", str(cm.exception))
                path.write_text(original, encoding="utf-8")

    def test_empty_trigger_has_no_trigger_line(self):
        self.edit_event("play_cancelled_promise", '"発火条件": "場面開始・1回"', '"発火条件": ""')
        self.assertNotIn("[トリガー", self.out("play/events/play_cancelled_promise.md"))

    def test_background_without_mask(self):
        self.edit_event("play_cancelled_promise", '"歩行マスク": "fields/masks/TRM-03-exterior-mask.webp"', '"歩行マスク": ""')
        with self.assertRaises(SystemExit) as cm:
            field_md.outputs()
        self.assertIn("歩行マスク", str(cm.exception))

    def test_empty_battle_background_is_not_emitted(self):
        self.edit_event("opening_battle", '"戦闘背景": "fields/play/bg011.webp"', '"戦闘背景": ""')
        self.assertNotIn("戦闘背景=", self.out("play/events/opening_battle.md"))

    def test_battle_background_is_emitted_on_field_map_line(self):
        # BG011 は暫定採用済みで、台帳の opening_battle に配信用複製が入っている
        self.assertIn(
            "マスク=fields/masks/TRM-02-mask.webp 戦闘背景=fields/play/bg011.webp]",
            self.out("play/events/opening_battle.md"),
        )

    def test_battle_background_with_space_or_bracket(self):
        for bad in ("a b.webp", "a].webp"):
            self.edit_event("opening_battle", '"戦闘背景": "fields/play/bg011.webp"', f'"戦闘背景": "{bad}"')
            with self.assertRaises(SystemExit) as cm:
                field_md.outputs()
            self.assertIn("戦闘背景", str(cm.exception))
            self.edit_event("opening_battle", f'"戦闘背景": "{bad}"', '"戦闘背景": "fields/play/bg011.webp"')

    def test_event_id_must_match_filename(self):
        self.edit_event("opening_battle", '"イベントID": "opening_battle"', '"イベントID": "other"')
        with self.assertRaises(SystemExit):
            field_md.outputs()


class Notation(FieldMdCase):
    def test_e001(self):
        text = self.out("play/events/opening_battle.md")
        self.assertIn("[トリガー auto scene=opening_battle once=true]", text)
        self.assertIn("中断時: 次=evacuation_after_play", text)
        self.assertIn("[プレイヤー @700,480]", text)

    def test_e002_scene_move_just_before_closing(self):
        lines = self.out("play/events/evacuation_after_play.md").rstrip("\n").split("\n")
        self.assertEqual(lines[-2:], ["[場面移動: play_cancelled_promise @1330,480]", "[/イベント]"])
        self.assertNotIn("[トリガー", "\n".join(lines))  # 背景を持たない（E001 の結果から呼ぶ）

    def test_e003(self):
        text = self.out("play/events/play_cancelled_promise.md")
        self.assertIn("[トリガー auto scene=play_cancelled_promise once=true]", text)
        self.assertIn("[プレイヤー @1330,480]", text)

    def test_script_entry(self):
        self.assertIn("[フィールド: opening_battle @700,480]", self.out("play/script.md"))

    def test_command_label_is_magic_not_incantation(self):
        # 戦闘コマンドは わざ・まほう・どうぐ・にげる（docs/systems.md）。name-name の既定「じゅもん」を上書きする
        self.assertIn("battle_command_labels: spell=まほう\n", self.out("play/script.md"))

    def test_readme_save_key_is_project_scoped(self):
        # /play/sit-by-me は name-name-save-<docKey=プロジェクト名>-<slot> を読む（field.html だけ field）
        readme = self.out("play/README.md")
        self.assertIn("name-name-save-sit-by-me-0", readme)
        self.assertNotIn("name-name-save-field-", readme)

    def test_every_event_md_is_hidden_with_marker(self):
        for ident in EVENT_IDS:
            text = self.out(f"play/events/{ident}.md")
            self.assertIn("hidden: true", text)
            self.assertIn(field_md.MARKER, text)


class FormsManifest(unittest.TestCase):
    LISTING = {
        "C001": {
            "poses": ["C001-elementary-idle.webp", "C001-elementary-character-idle.webp", "C001-elementary-slash.webp",
                      "C001-elementary-swing-windup.webp", "C001-elementary-bogus.webp", "readme.txt"],
            "walk": [f"C001-elementary-walk-{d}-{n}.webp"
                     for d in ("up", "down", "left", "right", "upleft", "upright", "downleft", "downright") for n in "123"],
        },
        "C002": {"poses": ["C002-kids-cast.webp"], "walk": ["C002-kids-walk-up-1.webp"]},
    }

    def test_snapshot(self):
        doc = json.loads(field_md.forms_manifest(self.LISTING))
        self.assertEqual(doc["_provenance"]["input_sha"], field_md.provenance_sha(doc))  # verify_ledger.rb が要求する印
        self.assertEqual(doc, {
            "_provenance": doc["_provenance"],
            field_md.FORMS_GENERATED_KEY: doc[field_md.FORMS_GENERATED_KEY],
            "characters": {
                "C001": {"plainBaked": True, "forms": {"elementary": {
                    "poses": {"plain": ["idle", "swing-windup", "slash"], "character": ["idle"]}, "walk": True}}},
                "C002": {"forms": {"kids": {"poses": {"plain": ["cast"]}, "walk": False}}},
            },
        })

    def test_text_format_and_purity(self):
        text = field_md.forms_manifest(self.LISTING)
        self.assertTrue(text.endswith("}\n"))
        self.assertIn('"character": ["idle"],\n            "plain": ["idle", "swing-windup", "slash"]\n', text)  # 短い配列は1行
        self.assertIn('"C002": {\n      "forms"', text)  # C001 以外に plainBaked は付かない
        self.assertEqual(text, field_md.forms_manifest(self.LISTING))
        self.assertIn(field_md.FORMS_GENERATED_KEY, text)


class StillBlocked(FieldMdCase):
    def test_ledger_status_is_blocked(self):
        for ident in EVENT_IDS:
            record = yaml.safe_load(self.event_path(ident).read_text(encoding="utf-8"))
            self.assertEqual(record["状態"], "blocked", ident)

    def test_outputs_carry_provisional_notes(self):
        for ident in EVENT_IDS:
            self.assertIn(" 暫定: ", self.out(f"play/events/{ident}.md"), ident)
        self.assertIn("暫定", self.out("play/script.md"))
        self.assertIn("暫定", self.out("play/data.md"))
        self.assertIn("blocked のまま", self.out("play/README.md"))


class SampleField(FieldMdCase):
    """全部入りサンプルの歩ける場面 sample_field（#276 / #250）。サンプル専用・暫定。"""

    def scene(self):
        return self.out("play/events/sample_field.md")

    def test_scene_output_and_provisional_head(self):
        text = self.scene()
        self.assertIn("サンプル専用・暫定", text.split("-->")[0])  # 先頭コメント
        self.assertIn(field_md.MARKER, text)
        self.assertIn("## sample_field: ", text)
        self.assertIn("戦闘背景=fields/play/bg012.webp", text)  # 台帳 戦闘背景.yaml の配信用複製
        self.assertIn("背景=fields/reference/teramachi-grounds-exterior-trm03-adopted.webp", text)  # 素材.yaml の採用済み TRM-03
        self.assertIn("マスク=fields/masks/TRM-03-exterior-mask.webp", text)
        self.assertNotIn("[トリガー", text)  # 歩くだけ。NPC・マップ端の切り替えも無い
        self.assertNotIn("[NPC", text)
        self.assertIn("サンプル専用・暫定", self.out("play/README.md"))

    def test_encounter_notation_shape(self):
        import re

        text = self.scene()
        self.assertEqual(len(re.findall(r"^\[エンカウント率: 1/[1-9][0-9]*\]$", text, re.M)), 1)
        groups = re.findall(r"^\[エンカウント群: ([^\]]+)\]$", text, re.M)
        self.assertEqual(len(groups), 1)
        # name-name の書式: カンマ区切りの群、+ 連結。id に空白・@ * : を含めない
        for group in groups[0].split(", "):
            for mid in group.split("+"):
                self.assertRegex(mid, r"^M[0-9]{3}$")
        # 率・群は [フィールドマップ] の直後（name-name の emit も直後）
        lines = text.splitlines()
        i = next(n for n, l in enumerate(lines) if l.startswith("[フィールドマップ"))
        self.assertTrue(lines[i + 1].startswith("[エンカウント率:") and lines[i + 2].startswith("[エンカウント群:"))

    def test_closed_references(self):
        import re

        data = self.out("play/data.md")
        groups = re.search(r"^\[エンカウント群: ([^\]]+)\]$", self.scene(), re.M)[1]
        defined = set(re.findall(r"^\[モンスター (\S+)\]$", data, re.M))
        enemies = {r["敵ID"] for r in yaml.safe_load((self.tmp / "docs/ledger/敵.yaml").read_text(encoding="utf-8"))}
        for mid in set(re.split(r"[,+ ]+", groups)):
            self.assertIn(mid, defined, mid)  # data.md の [モンスター] に定義がある
            self.assertIn(mid, enemies, mid)  # 台帳に実在する敵
            self.assertTrue((self.tmp / "assets/images/enemies" / f"{mid}.webp").is_file(), mid)
        for rel in re.findall(r"(?:背景|マスク|戦闘背景)=(\S+?)[\] ]", self.scene()):
            self.assertTrue((self.tmp / "assets/images" / rel).is_file(), rel)
        # 場面移動の行き先と再開点の場面ID は実在する
        self.assertIn("[場面移動: sample_field @", self.out("play/events/play_cancelled_promise.md"))
        save = json.loads(self.out("play/saves/sample_field_walk.save.json"))
        self.assertEqual(save["rpg"]["field"]["sceneId"], "sample_field")
        self.assertNotIn("battle", save["rpg"])

    def test_sample_enemy_values_are_provisional_and_distinct_from_m001(self):
        data = self.out("play/data.md")
        self.assertIn("サンプル専用・暫定", data.split("-->")[0])
        for mid, stats in field_md.SAMPLE_ENEMY_STATS.items():
            self.assertLess(stats[0], field_md.PROVISIONAL_HP["monster"])  # 9999 とは別。数ターンで終わる
            self.assertIn(f"[モンスター {mid}]", data)

    def test_e001_to_e003_unchanged_apart_from_sample_move(self):
        # 回帰: E001・E002 は台帳どおり（サンプル移動を足さない）。E003 は末尾に sample_field への移動が1行増えるだけ
        e1, e2 = self.out("play/events/opening_battle.md"), self.out("play/events/evacuation_after_play.md")
        self.assertNotIn("sample_field", e1)
        self.assertEqual(e2.count("[場面移動:"), 1)
        self.assertIn("[場面移動: play_cancelled_promise @1330,480]", e2)
        e3 = self.out("play/events/play_cancelled_promise.md")
        self.assertEqual(e3.count("[場面移動:"), 1)
        self.assertTrue(e3.rstrip().endswith("[場面移動: sample_field @1330,480]\n[/イベント]"))
        record = yaml.safe_load(self.event_path("play_cancelled_promise").read_text(encoding="utf-8"))
        self.assertEqual(e3.split("[イベント play_cancelled_promise]")[1].rsplit("[場面移動:", 1)[0].rstrip(), record["脚本"].split("[イベント play_cancelled_promise]")[1].replace("[/イベント]", "").rstrip())

    def test_freshness_orphan_overwrite(self):
        self.run_check()
        path = self.tmp / "play/events/sample_field.md"
        original = path.read_text(encoding="utf-8")
        path.write_text(original + "x", encoding="utf-8")
        with self.assertRaises(SystemExit) as cm:
            self.run_check()
        self.assertIn("stale", str(cm.exception))
        path.write_text("手書き\n", encoding="utf-8")
        with self.assertRaises(SystemExit) as cm:
            field_md.preflight(field_md.outputs())
        self.assertIn("sample_field.md", str(cm.exception))
        path.write_text(original, encoding="utf-8")
        orphan = self.tmp / "play/events/sample_field_old.md"
        orphan.write_text("x", encoding="utf-8")
        with self.assertRaises(SystemExit):
            field_md.preflight(field_md.outputs())

    def test_ledger_change_propagates(self):
        path = self.tmp / "docs/ledger/サンプルMAP.yaml"
        text = path.read_text(encoding="utf-8")
        path.write_text(text.replace('"エンカウント": "あり"', '"エンカウント": "なし"'), encoding="utf-8")
        scene = self.scene()
        self.assertNotIn("[エンカウント", scene)
        with self.assertRaises(SystemExit):
            self.run_check()  # 台帳を変えたら play/ は古い

    def test_bad_sample_map_fails(self):
        path = self.tmp / "docs/ledger/サンプルMAP.yaml"
        text = path.read_text(encoding="utf-8")
        for old, new in (('"戦闘背景": "BG012"', '"戦闘背景": "BG999"'), ('"流用元MAP": "TRM-03"', '"流用元MAP": "TRM-99"'),
                         ('opening_battle;evacuation_after_play;play_cancelled_promise', 'opening_battle;evacuation_after_play;no_such_event')):
            with self.subTest(old=old):
                path.write_text(text.replace(old, new), encoding="utf-8")
                with self.assertRaises(SystemExit):
                    field_md.outputs()
        path.write_text(text, encoding="utf-8")
        (self.tmp / "assets/images/fields/play/bg012.webp").unlink()
        with self.assertRaises(SystemExit):
            field_md.outputs()

    def test_spawn_is_walkable_in_real_mask(self):
        try:
            from PIL import Image
        except ImportError:
            self.skipTest("Pillow が無い（uv run --with pillow python3 -m unittest で実行すると検査される）")
        sample = field_md.sample_map({k: yaml.safe_load(self.event_path(k).read_text(encoding="utf-8")) for k in EVENT_IDS})
        x, y = map(int, sample["position"][1:].split(","))
        mask = Image.open(REAL / "assets/images" / sample["mask"]).convert("L")
        self.assertGreater(mask.getpixel((x, y)), 128)  # 白=歩行可


class ResumeSaves(FieldMdCase):
    def test_three_saves_generated_and_checked(self):
        rels = [r for _, _, r, _, _ in field_md.outputs() if r.endswith(".save.json")]
        self.assertEqual(sorted(rels), [f"play/saves/{n}.save.json" for n in ("opening_battle_fight", "opening_battle_start", "play_cancelled_promise_start", "playground_walk", "playroom_walk", "sample_field_walk")])
        self.run_check()

    def test_unknown_person_or_scene_fails(self):
        path = self.tmp / "docs/ledger/再開点/playroom_walk.yaml"
        text = path.read_text(encoding="utf-8")
        path.write_text(text.replace("C004", "C999"), encoding="utf-8")
        with self.assertRaises(SystemExit):
            field_md.outputs()
        path.write_text(text.replace('"opening_battle"', '"no_such_scene"'), encoding="utf-8")
        with self.assertRaises(SystemExit):
            field_md.outputs()

    def test_fire_auto_only_on_start_points(self):
        import json

        for name, expected in (("opening_battle_start", True), ("playroom_walk", False)):
            field = json.loads(self.out(f"play/saves/{name}.save.json"))["rpg"]["field"]
            self.assertEqual(field.get("fireAuto", False), expected)

    def test_fire_auto_value_is_strict(self):
        path = self.tmp / "docs/ledger/再開点/opening_battle_start.yaml"
        path.write_text(path.read_text(encoding="utf-8").replace("場面開始を起こす", "起こす"), encoding="utf-8")
        with self.assertRaises(SystemExit):
            field_md.outputs()

    def test_save_has_required_rpg_keys(self):
        import json

        rpg = json.loads(self.out("play/saves/opening_battle_fight.save.json"))["rpg"]
        self.assertEqual(rpg["version"], 1)
        self.assertEqual(rpg["equipment"], {})
        self.assertEqual([p["id"] for p in rpg["party"]], ["C001", "C002", "C003", "C004"])
        self.assertEqual(rpg["battle"]["enemies"][0]["id"], "M001")


if __name__ == "__main__":
    unittest.main()
