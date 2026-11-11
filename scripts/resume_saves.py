#!/usr/bin/env python3
"""再開点の台帳（docs/ledger/再開点/*.yaml）から、name-name の `?resume=` で読むセーブ JSON を生成する（#250）。

正本は台帳。play/saves/*.save.json は派生物で、手で編集しない。決定的（時刻・環境に依らない）。
field_md.py の出力一覧に含まれ、build_ledger.py の build / check で登録・検査される。
セーブの形式の正本は name-name の frontend/src/game/rpgSave.ts（RpgSaveState）。
中身は実在するものだけ: 味方は台帳 人物.yaml の C001〜C004、敵は 敵.yaml の ID。所持品・装備は空。
"""
import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / "docs/ledger/再開点"
SAVED_AT = "2026-01-01T00:00:00.000Z"  # 固定（決定的出力のため。実際の保存時刻ではない）
PROVISIONAL = {"party_hp": 100, "monster_hp": 9999, "gold": 0}  # data.md の仮値と同じ
FACINGS = ("up", "down", "left", "right", "upLeft", "upRight", "downLeft", "downRight")
FIRE_AUTO = "場面開始を起こす"  # 再開直後の許容値（空欄=起こさない）。セーブの field.fireAuto（name-name #1155）
ID_RE = re.compile(r"[a-z0-9_]+\Z")


def _load(path):
    r = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(r, dict) or r.get("再開点ID") != path.stem or not ID_RE.fullmatch(path.stem):
        raise SystemExit(f"{path.name}: 再開点IDとファイル名が一致しません")
    return r


def save_of(record, people, enemies, scenes):
    """再開点 1 件 → SaveSlotData（dict）。台帳に無い人物・敵・場面は FAIL。"""
    ident = record["再開点ID"]
    if str(record["場面ID"]) not in scenes:
        raise SystemExit(f"{ident}: 場面ID {record['場面ID']} が play/ の場面にありません")
    m = re.fullmatch(r"(\d+),(\d+)", str(record["位置"]))
    if not m:
        raise SystemExit(f"{ident}: 位置は x,y の形で書く")
    if record["向き"] not in FACINGS:
        raise SystemExit(f"{ident}: 向き は {FACINGS} のどれか: {record['向き']!r}")
    party = [c.strip() for c in str(record["パーティ"]).split(",") if c.strip()]
    for cid in party:
        if cid not in people:
            raise SystemExit(f"{ident}: パーティ {cid} が人物台帳にありません")
    mons = [c.strip() for c in str(record.get("戦闘") or "").split(",") if c.strip()]
    for mid in mons:
        if mid not in enemies:
            raise SystemExit(f"{ident}: 戦闘 {mid} が敵台帳にありません")
    fire = str(record.get("再開直後") or "")
    if fire not in ("", FIRE_AUTO):
        raise SystemExit(f"{ident}: 再開直後 は {FIRE_AUTO!r} か空欄だけ: {fire!r}")
    if fire and mons:
        raise SystemExit(f"{ident}: 戦闘中のセーブには 再開直後 を付けない")
    rpg = {
        "version": 1,
        "party": [{"id": c, "hp": PROVISIONAL["party_hp"], "mp": 0} for c in party],
        "items": {},
        "equipment": {},
        "gold": PROVISIONAL["gold"],
        "field": {"sceneId": str(record["場面ID"]), "x": int(m[1]), "y": int(m[2]), "facing": record["向き"]},
    }
    if fire:
        rpg["field"]["fireAuto"] = True
    if mons:
        rpg["battle"] = {
            "enemies": [{"id": mid, "hp": PROVISIONAL["monster_hp"]} for mid in mons],
            "atb": {"partyGauge": ([1000, 600, 300, 0] + [0] * len(party))[: len(party)],
                    "enemyGauge": [0] * len(mons), "queue": [0]},
        }
    return {
        "slot": 0, "sceneId": None, "eventIndex": 0, "textIndex": 0, "flags": {},
        "backgroundPath": None, "isBlackout": False, "characters": [], "currentBgmPath": None,
        "savedAt": SAVED_AT, "sceneName": str(record["名称"]), "rpg": rpg,
    }


def outputs(scenes):
    """[(生成物ID, 種別, 相対パス, 元の表, bytes)]。scenes は play/ の場面ID の集合。"""
    people = {r["人物ID"] for r in yaml.safe_load((ROOT / "docs/ledger/人物.yaml").read_text(encoding="utf-8"))}
    enemies = {r["敵ID"] for r in yaml.safe_load((ROOT / "docs/ledger/敵.yaml").read_text(encoding="utf-8"))}
    items = []
    for path in sorted(DIR.glob("*.yaml")):
        rec = _load(path)
        text = json.dumps(save_of(rec, people, enemies, scenes), ensure_ascii=False, indent=2) + "\n"
        items.append((f"G-play-save-{path.stem}", "name-name 再開用セーブJSON", f"play/saves/{path.stem}.save.json",
                      f"再開点:{path.stem}|人物|敵", text.encode("utf-8")))
    return items
