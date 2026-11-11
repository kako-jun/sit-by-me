#!/usr/bin/env python3
"""イベント台帳（docs/ledger/イベント/*.yaml）から、name-name の一枚絵フィールドで動く md を生成する（#250 第一歩）。

正本は台帳。出力（play/ 配下）は何度も書き換わる派生物で、手で編集しない。
scripts/preview_event.py はレビュー用の別物で、ここからは使わない。
build_ledger.py の `build` / `check` から呼ばれる。単体でも `uv run python3 scripts/field_md.py check`（鮮度・孤児・上書き防止の検査）が使える。

第一歩の範囲は E001〜E003（opening_battle / evacuation_after_play / play_cancelled_promise）だけ。
TBD が残る台帳（状態=blocked）からも骨組みは作れるが、blocked は解除しない。

台帳の列（イベント台帳は既存の語に合わせる。許容値は下の定数で厳密に判定し、typo は FAIL にする）:
  背景画像・歩行マスク（assets/images からの相対）・出現位置（x,y）・発火条件（空 または 場面開始・1回）・
  行き先（そのイベント末尾に [場面移動:] を足す先のイベントID）・暫定（注記の正本。生成物の先頭コメントに出る）。
"""
import argparse
import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
EVENTS = ROOT / "docs/ledger/イベント"
OUT = ROOT / "play"
# name-name の worker は scriptsDir 直下 + サブディレクトリ1段だけを列挙する。
# play/ を scriptsDir にすれば、play/script.md（入口）・play/data.md・play/events/*.md が全部拾われる。
FORMS = ROOT / "assets/field/sit-character-forms.json"
TRIGGER_AUTO_ONCE = "場面開始・1回"  # 発火条件の許容値（空欄は「別イベントから起動」でトリガーなし）
ENTRY_EVENT = "opening_battle"
FIELD_EVENTS = ("opening_battle", "evacuation_after_play", "play_cancelled_promise")
PARTY = ("C001", "C002", "C003", "C004")
MONSTER_SPRITE = "enemies/{id}.webp"
FORM = "elementary"  # 歩行絵・戦闘ポーズが全員揃う時期。ERA-01 は幼稚園期なので暫定
FORMS_GENERATED_KEY = "_generated"  # 目録 JSON の生成物の印（name-name は未知キーを読まない）
MARKER = "<!-- 生成物。台帳が正本。編集しない。"  # 先頭の固定部分。続けて暫定の注記と -->
ID_RE = re.compile(r"[a-zA-Z0-9_-]+\Z")
# 数値は仮値。敵.yaml の M001「HP は極めて高い（数値は未決）」と矛盾しないよう、仮の大きな値を置いただけ。
PROVISIONAL_HP = {"monster": 9999, "party": 100}


def _load(path):
    record = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(record, dict) or record.get("イベントID") != path.stem or not ID_RE.fullmatch(path.stem):
        raise SystemExit(f"{path.name}: イベントIDとファイル名が一致しません")
    return record


def _table(name):
    return yaml.safe_load((ROOT / "docs/ledger" / f"{name}.yaml").read_text(encoding="utf-8"))


def _text(record, key):
    value = record.get(key)
    return str(value).strip() if value is not None else ""


def _position(record, key="出現位置"):
    match = re.fullmatch(r"(\d+),(\d+)", _text(record, key))
    if not match:
        raise SystemExit(f"{record['イベントID']}: {key} は x,y の形で書く: {_text(record, key)!r}")
    return f"@{match.group(1)},{match.group(2)}"


def _head(note):
    return f"{MARKER}{(' 暫定: ' + note) if note else ''} -->"


def _scene_title(record):
    return _text(record, "名称").replace("\n", " ") or record["イベントID"]


def _frontmatter(title, extra=()):
    return "\n".join(["---", "engine: name-name", f"title: {title}", *extra, "---"])


def _script(record, records):
    """台帳の脚本。「行き先」があれば、イベント末尾に [場面移動:] を足す（到着位置は行き先の出現位置）。"""
    script = record["脚本"].rstrip()
    target = _text(record, "行き先")
    if not target:
        return script
    if target not in records or not _text(records[target], "出現位置"):
        raise SystemExit(f"{record['イベントID']}: 行き先 {target} の台帳に出現位置がありません")
    lines = script.split("\n")
    closing = [i for i, line in enumerate(lines) if line == "[/イベント]"]
    if not closing:
        raise SystemExit(f"{record['イベントID']}: [/イベント] が無く、場面移動を足せません")
    lines.insert(closing[-1], f"[場面移動: {target} {_position(records[target])}]")
    return "\n".join(lines)


def _scene_block(record, records):
    ident = record["イベントID"]
    lines = [f"## {ident}: {_scene_title(record)}", ""]
    if _text(record, "背景画像"):
        if not _text(record, "歩行マスク"):
            raise SystemExit(f"{ident}: 背景画像 があるのに 歩行マスク がありません")
        lines.append(f"[フィールドマップ 背景={_text(record, '背景画像')} マスク={_text(record, '歩行マスク')}]")
        lines.append(f"[プレイヤー {_position(record)}]")
        start = _text(record, "発火条件")
        if start not in ("", TRIGGER_AUTO_ONCE):
            raise SystemExit(f"{ident}: 発火条件 は {TRIGGER_AUTO_ONCE!r} か空欄だけ: {start!r}")
        if start == TRIGGER_AUTO_ONCE:
            lines.append(f"[トリガー auto scene={ident} once=true]")
        lines.append("")
    lines.append(_script(record, records))
    return "\n".join(lines)


def render_event(record, records):
    head = _frontmatter(_text(record, "名称") or record["イベントID"], ["hidden: true"])
    return f"{head}\n{_head(_text(record, '暫定').replace(chr(10), ' '))}\n\n{_scene_block(record, records)}\n"


def render_script(records):
    entry = records[ENTRY_EVENT]
    # 戦闘は FF5・6 式（DQ 式ではない。決定: docs/systems.md 7・14 行、kako-jun 2026-10-14）なので
    # battle_presentation: ff。窓は呪文・特技名と勝敗メッセージだけを1行で出し、踏み出し・のけぞり・ダメージ数字の演出になる。
    # 全場面共通の決定済みの値なので台帳の列にはしない。
    head = _frontmatter("Sit by Me", ["battle_layout: Side", "battle_presentation: ff"])
    body = [
        "## start: はじまり",
        "",
        f"[フィールド: {ENTRY_EVENT} {_position(entry)}]",
    ]
    note = "入口の座標は台帳 opening_battle の出現位置（暫定）"
    return f"{head}\n{_head(note)}\n\n" + "\n".join(body) + "\n"


def render_data(records):
    enemies = {r["敵ID"]: r for r in _table("敵")}
    people = {r["人物ID"]: r for r in _table("人物")}
    monster_ids = sorted({m for r in records.values() for m in re.split(r"[,;、\s]+", _text(r, "敵")) if m})
    head = _frontmatter("共通定義", ["hidden: true"])
    lines = [
        "## data: 共通定義",
        "",
        f"[人物の形態 目録={FORMS.relative_to(ROOT / 'assets')} 素材=characters]",
        f"[歩行絵 主人公 人物={PARTY[0]} 形態={FORM}]",
        "",
    ]
    for mid in monster_ids:
        enemy = enemies[mid]
        lines += [
            f"[モンスター {mid}]",
            f"名前: {enemy['名称']}",
            f"HP: {PROVISIONAL_HP['monster']}",
            f"スプライト: {MONSTER_SPRITE.format(id=mid)}",
            "[/モンスター]",
            "",
        ]
    for cid in PARTY:
        # 魔法・特技は台帳（魔法.yaml）に劇戦闘用の具体が無い（systems.md: 保留）ので書かない。
        lines += [
            f"[パーティ {cid}]",
            f"名前: {people[cid]['呼称']}",
            f"HP: {PROVISIONAL_HP['party']}",
            "MP: 0",
            f"人物: {cid}",
            f"形態: {FORM}",
            "[/パーティ]",
            "",
        ]
    note = "数値は台帳 opening_battle の暫定を参照（HP は仮値）。味方の魔法・特技は空"
    return f"{head}\n{_head(note)}\n\n" + "\n".join(lines).rstrip() + "\n"


def render_readme(records):
    rows = ["| 生成ファイル | 正本 |", "|---|---|", "| [script.md](script.md)（入口） | 台帳 docs/ledger/イベント/%s.yaml の出現位置 |" % ENTRY_EVENT,
            "| [data.md](data.md) | 敵.yaml・人物.yaml・イベント台帳の敵（数値は opening_battle の暫定列を参照） |"]
    for ident in FIELD_EVENTS:
        rows.append(f"| [events/{ident}.md](events/{ident}.md) | [{ident}.yaml](../docs/ledger/イベント/{ident}.yaml) |")
    return "\n".join([
        _head("各台帳の「暫定」列を参照"),
        "# play/（name-name の /play が読む md）",
        "",
        "**生成物。台帳が正本。編集しない。** `uv run python3 scripts/build_ledger.py build` で作り直す。",
        "name-name の worker が `scriptsDir=play` として `play/` 直下とサブディレクトリ1段（`events/`）の md を読む。",
        "暫定の項目と理由は各台帳の「暫定」列が正本（ここには複製しない）。台帳の状態は blocked のまま。",
        "",
        *rows,
        "",
        "人物の形態の目録（歩行絵・戦闘ポーズの一覧）: `assets/field/sit-character-forms.json`（素材のファイル名から生成）。",
        "",
    ]) + "\n"


def forms_manifest(listing):
    """目録（name-name の frontend/scripts/gen_sit_character_forms.py と同じ形式。刀の項目は付けない）を作る純関数。

    listing: {人物ID: {"poses": [poses/ のファイル名], "walk": [walk/ のファイル名]}}。ファイル名だけで決まる（時刻・環境に依らない）。
    """
    poses_order = ["idle", "ready", "step", "swing-windup", "slash", "swing-followthrough", "cast", "special", "hurt", "down", "victory"]
    dirs = ["up", "down", "left", "right", "upleft", "upright", "downleft", "downright"]
    characters = {}
    for cid in sorted(listing):
        forms = {}
        pose_re = re.compile(rf"^{cid}-(?P<form>.+?)(?P<char>-character)?-(?P<pose>swing-windup|swing-followthrough|[a-z]+)\.webp$")
        for name in sorted(listing[cid]["poses"]):
            m = pose_re.match(name)
            if not m or m["pose"] not in poses_order:
                continue
            entry = forms.setdefault(m["form"], {"poses": {}, "walk": False})
            entry["poses"].setdefault("character" if m["char"] else "plain", []).append(m["pose"])
        walk_re = re.compile(rf"^{cid}-(?P<form>.+)-walk-(?P<dir>[a-z]+)-(?P<n>[123])\.webp$")
        walk = {}
        for name in listing[cid]["walk"]:
            m = walk_re.match(name)
            if m:
                walk.setdefault(m["form"], set()).add((m["dir"], m["n"]))
        for form, got in walk.items():
            if len(got) == len(dirs) * 3:
                forms.setdefault(form, {"poses": {}, "walk": False})["walk"] = True
        for entry in forms.values():
            for variant in entry["poses"]:
                entry["poses"][variant].sort(key=poses_order.index)
        characters[cid] = {**({"plainBaked": True} if cid == "C001" else {}), "forms": dict(sorted(forms.items()))}
    doc = {FORMS_GENERATED_KEY: "scripts/field_md.py が assets/images/characters の素材から生成。手で編集しない（#250）", "characters": characters}
    text = json.dumps(doc, ensure_ascii=False, indent=2)
    text = re.sub(r"\[\s*((?:\"[a-z-]+\",?\s*)+)\]", lambda m: "[" + " ".join(m.group(1).split()).rstrip(",") + "]", text)
    return text + "\n"


def render_forms():
    listing = {}
    for cid in PARTY:
        base = ROOT / "assets/images/characters" / cid
        listing[cid] = {"poses": [f.name for f in (base / "poses").glob(f"{cid}-*.webp")],
                        "walk": [f.name for f in (base / "walk").glob(f"{cid}-*-walk-*.webp")]}
    return forms_manifest(listing)


def outputs():
    """[(生成物ID, 種別, 相対パス, 元の表, bytes)]。決定的（時刻・環境に依らない）。"""
    records = {ident: _load(EVENTS / f"{ident}.yaml") for ident in FIELD_EVENTS}
    source = "イベント台帳|敵|人物"
    items = [
        ("G-play-script", "name-name 入口md", "play/script.md", source, render_script(records)),
        ("G-play-data", "name-name 共通定義md", "play/data.md", source, render_data(records)),
        ("G-play-readme", "play/ の説明", "play/README.md", source, render_readme(records)),
    ]
    for ident in FIELD_EVENTS:
        items.append((f"G-play-event-{ident}", "name-name 場面md", f"play/events/{ident}.md", f"イベント台帳:{ident}", render_event(records[ident], records)))
    items.append(("G-play-character-forms", "人物の形態の目録JSON", "assets/field/sit-character-forms.json", "assets/images/characters", render_forms()))
    return [(a, b, c, d, e.encode("utf-8")) for a, b, c, d, e in items]


def preflight(items):
    """孤児（play/ 配下の全ファイル）を黙って残さない・生成物でないファイルを上書きしない（消さない）。

    play/ は name-name が読む md だけの置き場なので、台帳に対応しないファイルは拡張子を問わず孤児として止める
    （verify_asset_layout.py はファイル配置の規則外のファイルを見つけるだけで、孤児の削除漏れは見ない）。
    """
    expected = {ROOT / relative for _, _, relative, _, _ in items}
    orphans = sorted(p for p in OUT.rglob("*") if p.is_file() and p not in expected)
    if orphans:
        names = ", ".join(str(p.relative_to(ROOT)) for p in orphans)
        raise SystemExit(f"対応する台帳のないファイルが play/ に残っているため生成・検査を止めます: {names}")
    for _, _, relative, _, _ in items:
        path = ROOT / relative
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        marked = f'"{FORMS_GENERATED_KEY}"' in text if path.suffix == ".json" else MARKER in text
        if not marked:
            raise SystemExit(f"生成先が生成物ではないため上書きしません: {relative}")


def check():
    """鮮度（バイト一致）・孤児・上書き防止を検査する。build_ledger.py check は台帳登録のハッシュも見る。"""
    items = outputs()
    preflight(items)
    for _, _, relative, _, output in items:
        path = ROOT / relative
        if not path.is_file() or path.read_bytes() != output:
            raise SystemExit(f"FAIL: {relative} is stale")
    print(f"PASS: play/ の {len(items)} ファイルは台帳と一致")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("check",))
    parser.parse_args()
    check()
