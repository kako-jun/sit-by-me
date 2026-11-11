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
        for name in ("敵", "人物", "魔法"):
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
                path.write_text(original.replace('"出現位置": "400,512"', f'"出現位置": "{bad}"'), encoding="utf-8")
                with self.assertRaises(SystemExit) as cm:
                    field_md.outputs()
                self.assertIn("出現位置", str(cm.exception))
                path.write_text(original, encoding="utf-8")

    def test_destination_without_position(self):
        path = self.event_path("play_cancelled_promise")
        path.write_text(path.read_text(encoding="utf-8").replace('"出現位置": "400,512"\n', ""), encoding="utf-8")
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
        self.edit_event("play_cancelled_promise", '"歩行マスク": "fields/legacy/masks/TRM-08-mask.webp"', '"歩行マスク": ""')
        with self.assertRaises(SystemExit) as cm:
            field_md.outputs()
        self.assertIn("歩行マスク", str(cm.exception))

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
        self.assertEqual(lines[-2:], ["[場面移動: play_cancelled_promise @400,512]", "[/イベント]"])
        self.assertNotIn("[トリガー", "\n".join(lines))  # 背景を持たない（E001 の結果から呼ぶ）

    def test_e003(self):
        text = self.out("play/events/play_cancelled_promise.md")
        self.assertIn("[トリガー auto scene=play_cancelled_promise once=true]", text)
        self.assertIn("[プレイヤー @400,512]", text)

    def test_script_entry(self):
        self.assertIn("[フィールド: opening_battle @700,480]", self.out("play/script.md"))

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
        self.assertEqual(doc, {
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


class ResumeSaves(FieldMdCase):
    def test_three_saves_generated_and_checked(self):
        rels = [r for _, _, r, _, _ in field_md.outputs() if r.endswith(".save.json")]
        self.assertEqual(sorted(rels), [f"play/saves/{n}.save.json" for n in ("opening_battle_fight", "playground_walk", "playroom_walk")])
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

    def test_save_has_required_rpg_keys(self):
        import json

        rpg = json.loads(self.out("play/saves/opening_battle_fight.save.json"))["rpg"]
        self.assertEqual(rpg["version"], 1)
        self.assertEqual(rpg["equipment"], {})
        self.assertEqual([p["id"] for p in rpg["party"]], ["C001", "C002", "C003", "C004"])
        self.assertEqual(rpg["battle"]["enemies"][0]["id"], "M001")


if __name__ == "__main__":
    unittest.main()
