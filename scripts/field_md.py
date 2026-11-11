#!/usr/bin/env python3
"""イベント台帳（docs/ledger/イベント/*.yaml）から、name-name の一枚絵フィールドで動く md を生成する（#250 第一歩）。

正本は台帳。出力（play/ 配下）は何度も書き換わる派生物で、手で編集しない。
scripts/preview_event.py はレビュー用の別物で、ここからは使わない。
build_ledger.py の `build` / `check` から呼ばれる（直接は実行しない）。

第一歩の範囲は E001〜E003（opening_battle / evacuation_after_play / play_cancelled_promise）だけ。
TBD が残る台帳（状態=blocked）からも骨組みは作れるが、blocked は解除しない。
"""
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
ENTRY_EVENT = "opening_battle"
FIELD_EVENTS = ("opening_battle", "evacuation_after_play", "play_cancelled_promise")
PARTY = ("C001", "C002", "C003", "C004")
MONSTER_SPRITE = "enemies/{id}.webp"
FORM = "elementary"  # 歩行絵・戦闘ポーズが全員揃う時期。ERA-01 は幼稚園期なので暫定
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
    """台帳の脚本。「移動先」があれば、イベント末尾に [場面移動:] を足す（到着位置は移動先の出現位置）。"""
    script = record["脚本"].rstrip()
    target = _text(record, "移動先")
    if not target:
        return script
    if target not in records or not _text(records[target], "出現位置"):
        raise SystemExit(f"{record['イベントID']}: 移動先 {target} の台帳に出現位置がありません")
    lines = script.split("\n")
    closing = [i for i, line in enumerate(lines) if line == "[/イベント]"]
    if not closing:
        raise SystemExit(f"{record['イベントID']}: [/イベント] が無く、場面移動を足せません")
    lines.insert(closing[-1], f"[場面移動: {target} {_position(records[target])}]")
    return "\n".join(lines)


def _scene_block(record, records):
    ident = record["イベントID"]
    lines = [f"## {ident}: {_scene_title(record)}", ""]
    if _text(record, "背景"):
        lines.append(f"[フィールドマップ 背景={_text(record, '背景')} マスク={_text(record, 'マスク')}]")
        lines.append(f"[プレイヤー {_position(record)}]")
        start = _text(record, "開始方式")
        if start.startswith("場面開始"):
            once = " once=true" if "1回" in start else ""
            lines.append(f"[トリガー auto scene={ident}{once}]")
        lines.append("")
    lines.append(_script(record, records))
    return "\n".join(lines)


def render_event(record, records):
    head = _frontmatter(_text(record, "名称") or record["イベントID"], ["hidden: true"])
    return f"{head}\n{_head(_text(record, '暫定').replace(chr(10), ' '))}\n\n{_scene_block(record, records)}\n"


def render_script(records):
    entry = records[ENTRY_EVENT]
    head = _frontmatter("Sit by Me", ["battle_layout: Side"])
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
        "## data: 共通定義（HP・攻撃などの数値はすべて暫定。台帳の敵・味方の数値は未決）",
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
    note = "HP などの数値はすべて仮値。台帳 敵.yaml の M001「HP は極めて高い・数値は未決」と矛盾しない大きな仮値。味方の魔法・特技は台帳に劇戦闘用の具体が無いので空"
    return f"{head}\n{_head(note)}\n\n" + "\n".join(lines).rstrip() + "\n"


def render_readme(records):
    rows = ["| 生成ファイル | 正本 |", "|---|---|", "| [script.md](script.md)（入口） | 台帳 docs/ledger/イベント/%s.yaml の出現位置 |" % ENTRY_EVENT,
            "| [data.md](data.md) | 敵.yaml・人物.yaml・イベント台帳の敵（数値は暫定） |"]
    for ident in FIELD_EVENTS:
        rows.append(f"| [events/{ident}.md](events/{ident}.md) | [{ident}.yaml](../docs/ledger/イベント/{ident}.yaml) |")
    return "\n".join([
        _head("背景・マスク・座標・数値"),
        "# play/（name-name の /play が読む md）",
        "",
        "**生成物。台帳が正本。編集しない。** `uv run python3 scripts/build_ledger.py build` で作り直す。",
        "name-name の worker が `scriptsDir=play` として `play/` 直下とサブディレクトリ1段（`events/`）の md を読む。",
        "背景・マスク・座標・数値は暫定（台帳の「暫定」列）。台帳の状態は blocked のまま。",
        "",
        *rows,
        "",
        "人物の形態の目録（歩行絵・戦闘ポーズの一覧）: `assets/field/sit-character-forms.json`（素材のファイル名から生成）。",
        "",
    ]) + "\n"


def render_forms():
    """name-name の目録（frontend/scripts/gen_sit_character_forms.py と同じ形式。刀の項目は付けない）。"""
    poses_order = ["idle", "ready", "step", "swing-windup", "slash", "swing-followthrough", "cast", "special", "hurt", "down", "victory"]
    dirs = ["up", "down", "left", "right", "upleft", "upright", "downleft", "downright"]
    characters = {}
    for cid in PARTY:
        base = ROOT / "assets/images/characters" / cid
        forms = {}
        pose_re = re.compile(rf"^{cid}-(?P<form>.+?)(?P<char>-character)?-(?P<pose>swing-windup|swing-followthrough|[a-z]+)\.webp$")
        for f in sorted((base / "poses").glob(f"{cid}-*.webp")):
            m = pose_re.match(f.name)
            if not m or m["pose"] not in poses_order:
                continue
            entry = forms.setdefault(m["form"], {"poses": {}, "walk": False})
            entry["poses"].setdefault("character" if m["char"] else "plain", []).append(m["pose"])
        walk_re = re.compile(rf"^{cid}-(?P<form>.+)-walk-(?P<dir>[a-z]+)-(?P<n>[123])\.webp$")
        walk = {}
        for f in (base / "walk").glob(f"{cid}-*-walk-*.webp"):
            m = walk_re.match(f.name)
            if m:
                walk.setdefault(m["form"], set()).add((m["dir"], m["n"]))
        for form, got in walk.items():
            if len(got) == len(dirs) * 3:
                forms.setdefault(form, {"poses": {}, "walk": False})["walk"] = True
        for entry in forms.values():
            for variant in entry["poses"]:
                entry["poses"][variant].sort(key=poses_order.index)
        characters[cid] = {**({"plainBaked": True} if cid == "C001" else {}), "forms": dict(sorted(forms.items()))}
    doc = {"_generated": "scripts/field_md.py が assets/images/characters の素材から生成。手で編集しない（#250）", "characters": characters}
    text = json.dumps(doc, ensure_ascii=False, indent=2)
    text = re.sub(r"\[\s*((?:\"[a-z-]+\",?\s*)+)\]", lambda m: "[" + " ".join(m.group(1).split()).rstrip(",") + "]", text)
    return text + "\n"


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
    """孤児 md を黙って残さない・生成物でないファイルを上書きしない（消さない）。"""
    expected = {ROOT / relative for _, _, relative, _, _ in items}
    orphans = sorted(p for p in OUT.rglob("*.md") if p not in expected)
    if orphans:
        names = ", ".join(str(p.relative_to(ROOT)) for p in orphans)
        raise SystemExit(f"対応する台帳のない md が残っているため生成しません: {names}")
    for _, _, relative, _, _ in items:
        path = ROOT / relative
        if path.suffix == ".md" and path.exists() and MARKER not in path.read_text(encoding="utf-8"):
            raise SystemExit(f"生成先が生成物ではないため上書きしません: {relative}")
