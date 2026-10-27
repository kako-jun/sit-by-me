#!/usr/bin/env python3
"""Check normalized content relationships, asset provenance, and derived manifest."""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from pathlib import Path

from content_ledger import ROOT, MANIFEST, manifest_payload, rows, shape_vocabulary_errors

EXPECTED = {
    "敵": 86, "召喚獣": 8, "敵サイズ": 63, "ダンジョン": 12,
    "敵配置": 70, "兼六園再登場": 44, "ボスギミック": 28,
    "戦闘パターン案": 21, "敵戦利品": 6, "BGMスロット": 26,
    "BGM回想編曲": 4, "BGM旧スロット対応": 54, "BGM録音": 64,
    "BGMフレーズ": 15, "人物": 4, "人物形態": 30,
    "素材移行": 712, "素材移行設定": 8, "刀候補": 31,
    "刀配分案": 20, "能力候補": 38, "刀能力配分案": 20,
    "ジョブ候補": 4, "魔法": 8,
}


def check() -> None:
    data = {name: rows(name) for name in EXPECTED}
    def ids(name: str, key: str) -> set[str]:
        values = [row[key] for row in data[name]]
        assert len(values) == len(set(values)), f"{name}: duplicate {key}"
        return set(values)

    enemy = ids("敵", "敵ID")
    summon = ids("召喚獣", "召喚獣ID")
    dungeon = ids("ダンジョン", "ダンジョンID")
    boss = ids("ボスギミック", "ギミックID")
    slot = ids("BGMスロット", "スロットID")
    person = ids("人物", "人物ID")
    blade = ids("刀候補", "刀候補ID")
    ability = ids("能力候補", "能力ID")
    maps = {row["MAP_ID"] for row in rows("MAP")}
    for name, key in (("敵サイズ", "サイズ行ID"), ("敵配置", "配置ID"),
                      ("兼六園再登場", "再登場ID"), ("戦闘パターン案", "パターンID"),
                      ("BGM回想編曲", "編曲ID"), ("BGM旧スロット対応", "対応ID"),
                      ("BGM録音", "録音行ID"), ("BGMフレーズ", "フレーズ行ID"),
                      ("人物形態", "形態ID"), ("刀配分案", "配分ID"),
                      ("刀能力配分案", "配分ID"), ("ジョブ候補", "候補ID"),
                      ("魔法", "魔法ID"), ("素材移行", "旧パス")):
        ids(name, key)
    for row in data["敵サイズ"]:
        assert row["敵ID"] in enemy | summon, row
    for row in data["敵配置"]:
        assert bool(row["敵ID"]) != bool(row["召喚獣ID"]), row
        assert not row["敵ID"] or row["敵ID"] in enemy, row
        assert not row["召喚獣ID"] or row["召喚獣ID"] in summon, row
        assert row["ダンジョンID"] in dungeon, row
        assert row["対象MAP"] == "未決(要確認)" or row["対象MAP"] in maps, row
        assert row["採用状態"] == "採用/案混在（原文参照）", row
    for row in data["兼六園再登場"]:
        assert row["敵ID"] in enemy, row
        assert row["MAP_ID"] == "未決(要確認)" or row["MAP_ID"] in maps, row
        assert row["元ダンジョンID"] == "未決(要確認)" or row["元ダンジョンID"] in dungeon, row
    assert sum(int(r["種数換算"]) for r in data["兼六園再登場"]) == 49
    assert len({r["グループID"] for r in data["兼六園再登場"]}) == 8
    for row in data["戦闘パターン案"]:
        assert set(re.findall(r"G\d{3}", row["ギミックID"])) <= boss, row
    for row in data["敵戦利品"]:
        assert row["敵ID"] in enemy, row
    for row in data["BGM回想編曲"]:
        assert row["元スロットID"] in slot, row
    for row in data["BGM旧スロット対応"]:
        if row["現行スロットID"]:
            assert row["現行スロットID"] in slot, row
    rec = {(r["録音ID"], r["楽章"]) for r in data["BGM録音"]}
    assert len(rec) == 64
    rec_ids = {r["録音ID"] for r in data["BGM録音"]}
    for row in data["BGMフレーズ"]:
        recording = row["録音ID"].split("(")[0]
        assert recording in rec_ids, row
    vocabulary = rows("語彙")
    for row in data["人物形態"]:
        assert row["人物ID"] in person, row
        shape_errors = shape_vocabulary_errors(row, vocabulary)
        assert not shape_errors, shape_errors
        assert (ROOT / row["マスターパス"]).is_file(), row
    for name in ("刀配分案", "刀能力配分案"):
        for row in data[name]:
            assert row["人物ID"] in person, row
            assert row["刀候補ID"] in blade, row
            if name == "刀能力配分案":
                assert not row["能力候補ID"] or row["能力候補ID"] in ability, row
                if not row["能力候補ID"]:
                    assert "案" in row["状態"] and (re.search(r"A\d{2}", row["型"]) or "候補" in row["型"]), row
    for row in data["ジョブ候補"]:
        assert not row["人物ID"] or row["人物ID"] in person, row

    assets = rows("素材")
    asset_ids = [r["素材ID"] for r in assets]
    assert len(asset_ids) == len(set(asset_ids)), "duplicate 素材ID"
    present = [r for r in assets if r["パス"]]
    absent = [r for r in assets if not r["パス"]]
    paths = [r["パス"] for r in present]
    assert len(paths) == len(set(paths)), "duplicate asset path"
    image_paths = {p.relative_to(ROOT).as_posix() for p in (ROOT / "assets/images").rglob("*") if p.suffix in {".webp", ".png", ".svg"}}
    assert set(paths) == image_paths, f"asset paths differ: ledger={len(paths)}, disk={len(image_paths)}"
    for row in present:
        assert hashlib.sha256((ROOT / row["パス"]).read_bytes()).hexdigest() == row["sha256"], row["パス"]
    restored = [r for r in present if r["パス"].startswith("assets/images/weapons/masters/")]
    assert len(restored) == 20
    assert all(r["状態"] == "現存（採否未照合）" and r["来歴"].startswith("旧枝 ddb1c98:") for r in restored)
    for filename in ("敵", "召喚獣", "敵配置"):
        assert not re.search(r"exec-[0-9a-f]{8}-[0-9a-f-]{27,}\.png",
                             (ROOT / "docs/ledger" / f"{filename}.yaml").read_text())
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert manifest == manifest_payload(), "derived asset manifest differs from YAML"
    actions = Counter(r["操作"] for r in data["素材移行"])
    assert actions == {"move": 431, "delete": 281}, actions
    assert sum(bool(r["剪定パス"]) for r in data["素材移行"]) == 134
    print(f"PASS: {len(EXPECTED)} content tables; {len(assets)} assets ({len(present)} present, {len(restored)} restored weapon records); {len(data['素材移行'])} migration entries")


if __name__ == "__main__":
    check()
