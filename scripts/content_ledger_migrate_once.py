#!/usr/bin/env python3
"""One-time, source-preserving migration of non-MAP content into Japanese-key YAML.

The source Markdown and CSV files are historical input to this command. Never run it
over subsequently curated ledger rows. Use `content_ledger.py` to build views and the
asset migration JSON after the first import.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import re
from collections import Counter
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs"
LEDGER = DOC / "ledger"


def section(text: str, heading: str, next_heading: str | None = None) -> str:
    start = text.index(heading)
    tail = text[start + len(heading):]
    if next_heading:
        tail = tail[: tail.index(next_heading)]
    return tail


def tables(text: str) -> list[tuple[list[str], list[list[str]]]]:
    found = []
    lines = text.splitlines()
    pos = 0
    while pos < len(lines):
        if not lines[pos].startswith("|"):
            pos += 1
            continue
        block = []
        while pos < len(lines) and lines[pos].startswith("|"):
            block.append(lines[pos])
            pos += 1
        if len(block) < 2 or not re.fullmatch(r"[|:\- ]+", block[1]):
            continue
        head = cells(block[0])
        rows = [cells(line) for line in block[2:]]
        found.append((head, rows))
    return found


def cells(line: str) -> list[str]:
    # Source tables use literal pipes only as column delimiters. Escaped pipes in
    # inline code are handled before splitting, then restored.
    hold = "\u0000PIPE\u0000"
    line = line.replace("\\|", hold)
    return [value.strip().replace(hold, "|") for value in line.strip().strip("|").split("|")]


def first_table(text: str, expected: str) -> tuple[list[str], list[list[str]]]:
    for head, rows in tables(text):
        if head and head[0] == expected:
            return head, rows
    raise ValueError(f"table headed {expected!r} absent")


def markdown(path: str) -> str:
    return (DOC / path).read_text(encoding="utf-8")


def row_map(head: list[str], row: list[str], source: str) -> dict[str, str]:
    if source == "monsters.md" and row[0] == "M006" and len(row) == len(head) - 1:
        # The source row merged image adoption facts into 役割 and omitted the
        # separate 絵の状態 cell. Do not infer a second independent value.
        row = row[:-1] + ["", row[-1]]
    if len(head) != len(row):
        raise ValueError(f"{source}: {len(head)} columns but {len(row)} values: {row[:2]}")
    return dict(zip(head, row))


def write(table: str, rows: list[dict[str, str]]) -> None:
    path = LEDGER / f"{table}.yaml"
    if path.exists():
        if os.environ.get("SIT_CONTENT_MIGRATION_RESUME") == "1":
            print(f"{table}: already migrated; skipped")
            return
        raise FileExistsError(f"refusing to overwrite curated table: {path}")
    path.write_text(
        f"# 表: {table}。移行後はこの YAML が正本。全値は文字列。\n"
        + yaml.safe_dump(rows, allow_unicode=True, sort_keys=False, width=100000, default_style='"'),
        encoding="utf-8",
    )
    print(f"{table}: {len(rows)}")


def source_rows(doc: str, begin: str, end: str, expected: str) -> tuple[list[str], list[list[str]]]:
    return first_table(section(markdown(doc), begin, end), expected)


def monster_tables() -> None:
    text = markdown("monsters.md")
    enemy = []
    for start, end in [
        ("### 3-1.", "### 3-2."),
        ("### 3-3.", "### 3-4."),
        ("### 3-4.", "### 3-5."),
    ]:
        head, rows = first_table(section(text, start, end), "ID")
        for source in rows:
            m = re.match(r"M\d{3}", source[0])
            if not m:
                continue  # Unassigned IDs belong in 未決, not a fabricated M ID.
            r = row_map(head, source, "monsters.md")
            ident = m.group()
            enemy.append({
                "敵ID": ident,
                "名称": r["名前"],
                "分類": r["分類"],
                "登場設定": r["出る場所"],
                "属性": r["属性"],
                "弱点・耐性": r["弱点・耐性"],
                "役割": r["役割"],
                "遭遇状態": "非遭遇" if ident in {"M003", "M011"} else ("ID案・未決" if ident in {"M022", "M023"} else "記録あり"),
                "画像状態": r["絵の状態"],
                "根拠": r["根拠"],
                "特徴(自由記述)": "",
            })
    assert len(enemy) == 86, len(enemy)
    write("敵", enemy)

    head, rows = first_table(section(text, "### 3-2.", "### 3-3."), "ID")
    summons = []
    for source in rows:
        r = row_map(head, source, "monsters.md summons")
        summons.append({
            "召喚獣ID": r["ID"], "名称": r["名前"], "登場・取得": r["出る場所（取得・登場）"],
            "属性": r["属性"], "敵として戦うか": r["敵として戦うか"], "画像状態": r["絵の状態"],
            "根拠": r["根拠"], "特徴(自由記述)": "",
        })
    assert len(summons) == 8
    write("召喚獣", summons)

    head, rows = first_table(section(text, "### 3-7.", "### 3-8."), "ID")
    sizes = []
    for i, source in enumerate(rows, 1):
        r = row_map(head, source, "monsters.md sizes")
        m = re.match(r"[MS]\d{3}", r["ID"])
        if not m:
            continue
        sizes.append({"サイズ行ID": f"SZ-{i:03d}", "敵ID": m.group(),
                      "形態": r["ID"], "グリッド種別": r["gridClass"], "根拠": r["根拠"]})
    write("敵サイズ", sizes)

    head, rows = first_table(section(text, "### 3-6.", "### 3-7."), "ID")
    loot = []
    for source in rows:
        r = row_map(head, source, "monsters.md loot")
        if not re.fullmatch(r"M\d{3}", r["ID"]):
            continue
        loot.append({"敵ID": r["ID"], "ドロップ": r["ドロップ"],
                     "ぬすむ通常": r["ぬすむ（通常枠）"], "ぬすむレア": r["ぬすむ（レア枠）"],
                     "根拠": r["根拠"]})
    write("敵戦利品", loot)


def dungeon_tables() -> None:
    text = markdown("dungeon-enemies.md")
    head, rows = first_table(section(text, "## 1. ダンジョンの単位", "## 2. ダンジョン別の敵の表"), "単位")
    dungeons = []
    for i, source in enumerate(rows, 1):
        r = row_map(head, source, "dungeon-enemies.md dungeons")
        dungeons.append({"ダンジョンID": f"DNG-{i:02d}", "名称": r["単位"],
                         "含む地区・MAP": r["含む地区・マップ"], "時期": r["時期"],
                         "分ける理由": r["分ける理由"], "目標種数": "", "備考": ""})
    assert len(dungeons) == 12
    write("ダンジョン", dungeons)
    by_name = {d["名称"]: d["ダンジョンID"] for d in dungeons}

    placement_section = section(text, "## 2. ダンジョン別の敵の表", "## 3. 現状の重複")
    blocks = re.split(r"(?=^### 2\.\d+ )", placement_section, flags=re.M)
    placement = []
    for block in blocks:
        h = re.match(r"### 2\.\d+ ([^（\n]+)", block)
        if not h:
            continue
        name = h.group(1).strip()
        # Heading names differ slightly from §1; match the initial heading name
        # and preserve the original heading in 出典 for any ambiguous case.
        key = next((value for label, value in by_name.items() if name.startswith(label) or label.startswith(name)), "")
        if name == "能登・被災前":
            key = "DNG-06"
        elif name == "能登・被災後":
            key = "DNG-07"
        for head, rows in tables(block):
            if head[:2] != ["ID", "名前（サイズ）"]:
                continue
            for source in rows:
                r = row_map(head, source, "dungeon-enemies.md placements")
                ident = re.match(r"[MS]\d{3}", r["ID"])
                if not ident:
                    continue
                eid = ident.group()
                placement.append({
                    "配置ID": f"EP-{len(placement)+1:03d}",
                    "敵ID": eid if eid.startswith("M") else "", "召喚獣ID": eid if eid.startswith("S") else "",
                    "ダンジョンID": key, "対象MAP": "未決(要確認)", "時期": "",
                    "名前・サイズ": r["名前（サイズ）"], "理由": r["理由（根拠）"],
                    "ラーニング": r["ラーニング"], "役割": r["役割"],
                    "個性パターン案": r["個性パターン（候補）"], "画像状態": r["状態"],
                    "評価": r["評価"], "報酬の個性": r["報酬の個性"],
                    "再戦可否": r["再戦可否"], "採用状態": "採用/案混在（原文参照）",
                    "出典": f"docs/dungeon-enemies.md §2 {h.group(0)}", "特徴(自由記述)": "",
                })
    write("敵配置", placement)

    # §2.11 is a deliberate exception: every listed normal enemy recurs at a
    # specific garden group, and M201 represents six types rather than one.
    garden = section(text, "### 2.11 ", "### 2.12 ")
    group_rows = next(rows for head, rows in tables(garden) if head and head[0] == "グループ")
    map_rows = next(rows for head, rows in tables(garden) if head and head[0] == "地区グループ")
    map_by_group = {re.sub(r"グループ.*", "", r[0]).strip(): re.search(r"GRD-\d{2}", r[1]).group() for r in map_rows}
    revival = []
    for row in group_rows:
        group, origin, members = row
        label = re.sub(r"グループ.*", "", group).strip()
        map_id = map_by_group.get(label, "未決(要確認)")
        origin_sections = re.findall(r"§2\.(\d+)", origin)
        source_dungeon = f"DNG-{int(origin_sections[0]):02d}" if len(origin_sections) == 1 else "未決(要確認)"
        # Parenthetical notes after the list mention excluded bosses and future
        # replenishment candidates. They are not adopted recurrences.
        for eid in dict.fromkeys(re.findall(r"M\d{3}", members.split("（")[0])):
            revival.append({"再登場ID": f"RE-{len(revival)+1:03d}", "グループID": group,
                            "MAP_ID": map_id, "元ダンジョンID": source_dungeon, "敵ID": eid,
                            "種数換算": "6" if eid == "M201" else "1", "理由": members,
                            "状態": "採用済みの再登場規則"})
    write("兼六園再登場", revival)


def boss_tables() -> None:
    text = markdown("boss-gimmicks.md")
    head, rows = first_table(section(text, "## 1. ギミック一覧", "## 2. 召喚獣"), "ID")
    gimmicks = []
    for source in rows:
        r = row_map(head, source, "boss-gimmicks.md gimmicks")
        gimmicks.append({"ギミックID": r["ID"], "内容": r["ギミック"], "出典": r["出典"],
                         "実現可否": r["実現可否"], "使う予定": r["使う予定"],
                         "採用状態": "案・決定混在（原文参照）", "特徴(自由記述)": ""})
    assert len(gimmicks) == 28
    write("ボスギミック", gimmicks)
    head, rows = first_table(section(text, "## 5. 戦い方のパターン案", "### 5.0"), "ID")
    patterns = []
    for source in rows:
        r = row_map(head, source, "boss-gimmicks.md patterns")
        patterns.append({"パターンID": r["ID"], "対象ID": r["ボス"], "案": r["パターン案"],
                         "根拠": r["根拠（記録上のモチーフ）"], "ギミックID": r["ギミック"],
                         "実現可否": r["実現可否"], "採用状態": "案"})
    assert len(patterns) == 21
    write("戦闘パターン案", patterns)


def bgm_tables() -> None:
    text = markdown("bgm-registry.md")
    current = section(text, "## 5. スロット表", "## 6. 集計")
    slots, recalls = [], []
    for head, rows in tables(current):
        if head[0] == "ID" and "抽象名" in head:
            for source in rows:
                r = row_map(head, source, "bgm-registry.md slots")
                slots.append({"スロットID": r["ID"], "抽象名": r["抽象名"],
                              "場面": r.get("場面", r.get("使う地区", "")), "気分": r["気分"],
                              "Largo": r["Largo"], "系統": r["系統"], "長さ": r["長さ"],
                              "兼用先": r["兼用先"], "状態": "案", "根拠": "docs/bgm-registry.md §5"})
        elif head[:2] == ["ID", "元テーマ"]:
            for source in rows:
                r = row_map(head, source, "bgm-registry.md recalls")
                recalls.append({"編曲ID": r["ID"], "元スロットID": re.match(r"P\d{2}", r["元テーマ"]).group(),
                                "回想場面": r["回想の場面（出典）"], "編曲案": r["編曲の案（楽器・テンポ）"],
                                "気分": r["気分"], "Largo": r["Largo"], "系統": r["系統"], "状態": "案"})
    assert len(slots) == 26, len(slots)
    assert len(recalls) == 4
    write("BGMスロット", slots)
    write("BGM回想編曲", recalls)

    old = section(text, "### 2.2 旧54スロット案", "## 3. sit にあって")
    head, rows = first_table(old, "旧ID(抽象名)")
    mapping = []
    for source in rows:
        r = row_map(head, source, "bgm-registry.md old map")
        original = r["旧ID(抽象名)"]
        ids = []
        for a, b in re.findall(r"([A-Z]\d{2})〜([A-Z]\d{2})", original):
            if a[0] == b[0]:
                ids.extend(f"{a[0]}{n:02d}" for n in range(int(a[1:]), int(b[1:]) + 1))
        masked = re.sub(r"[A-Z]\d{2}〜[A-Z]\d{2}", "", original)
        ids.extend(re.findall(r"[A-Z]\d{2}", masked))
        dest = r["現行の行き先"]
        to = re.findall(r"[SBTV DPEX]\d{2}", dest.replace(" ", ""))
        for old_id in dict.fromkeys(ids):
            mapping.append({"対応ID": f"OLD-{len(mapping)+1:03d}", "旧スロットID": old_id,
                            "旧抽象名": original, "現行スロットID": to[0] if to and "削除" not in dest else "",
                            "扱い": "削除" if "削除" in dest else "兼用/編曲（原文参照）", "理由": dest})
    write("BGM旧スロット対応", mapping)

    with (DOC / "bgm-sources.csv").open(newline="", encoding="utf-8-sig") as file:
        sources = list(csv.DictReader(file))
    assert len(sources) == 64
    source_rows = []
    for i, r in enumerate(sources, 1):
        source_rows.append({"録音行ID": f"REC-{i:03d}", "録音ID": r["id"], "録音名": r["録音名"],
                            "演奏者": r["演奏者"], "録音年": r["録音年"], "楽章": r["楽章"],
                            "ファイルパス": r["ファイルパス"], "ランク": r["ランク"],
                            "ライセンス表記(原文)": r["ライセンス表記(原文)"], "出典URL": r["出典URL"],
                            "クレジット文言": r["クレジット文言"],
                            "ffprobeで実測した長さ(秒)": r["ffprobeで実測した長さ(秒)"],
                            "形式": r["形式"], "備考": r["備考"]})
    write("BGM録音", source_rows)
    with (DOC / "bgm-phrases.csv").open(newline="", encoding="utf-8-sig") as file:
        phrases = list(csv.DictReader(file))
    assert len(phrases) == 15
    phrase_rows = []
    for i, r in enumerate(phrases, 1):
        phrase_rows.append({"フレーズ行ID": f"PHR-{i:03d}", "主題ID": r["主題ID"],
                            "楽章": r["楽章"], "主題名": r["主題名"], "録音ID": r["録音ID"],
                            "開始秒": r["開始秒"], "終了秒": r["終了秒"],
                            "気分(悲/楽/緊)": r["気分(悲/楽/緊)"],
                            "割当スロット候補": r["割当スロット候補"],
                            "出力ファイル": r["出力ファイル(~/data/sit-bgm/suno-input/ 配下)"],
                            "要耳確認": r["要耳確認"]})
    write("BGMフレーズ", phrase_rows)


def people_tables() -> None:
    art = markdown("art-direction.md")
    head, rows = first_table(section(art, "## 4人の呼称と伏線", "## 人物素材"), "呼称")
    prefixes = {"オトン": ("C001", "otton"), "ナム": ("C002", "nam"),
                "シャー": ("C003", "shah"), "ペー子": ("C004", "peiko")}
    people = []
    for source in rows:
        r = row_map(head, source, "art-direction.md people")
        ident, prefix = prefixes[r["呼称"]]
        people.append({"人物ID": ident, "呼称": r["呼称"], "旧接頭辞": prefix,
                       "牌": r["牌"], "人物の芯": r["人物の芯"], "見た目の核": r["見た目の核"],
                       "役割": "主人公/相方は選択で入れ替わる" if ident in {"C001", "C002"} else "友達",
                       "根拠": "docs/art-direction.md; docs/assets-policy.md", "特徴(自由記述)": ""})
    write("人物", people)
    forms = []
    for path in sorted((ROOT / "assets/images/characters").glob("C*/masters/*.webp")):
        rel = path.relative_to(ROOT).as_posix()
        ident = path.parent.parent.name
        suffix = path.stem[len(ident) + 1:]
        tokens = suffix.split("-")
        age = tokens[0]
        forms.append({"形態ID": f"FORM-{len(forms)+1:03d}", "人物ID": ident,
                      "年齢": age, "衣装": "園服" if "uniform" in tokens else "通常",
                      "車椅子": "はい" if "wheelchair" in tokens else "いいえ",
                      "マスターパス": rel, "状態": "現存（採否は原文参照）",
                      "根拠": "docs/assets-policy.md; assets/images/characters"})
    assert len(forms) == 30
    write("人物形態", forms)


def asset_tables() -> None:
    manifest = json.loads((DOC / "production/20261018-asset-migration.json").read_text(encoding="utf-8"))
    assert len(manifest["entries"]) == 712
    rows = [{"旧パス": r["old"], "新パス": r["new"] or "", "操作": r["action"],
             "理由": r["reason"], "sha256": r["sha256"],
             "剪定パス": r.get("pruned_path", "")} for r in manifest["entries"]]
    write("素材移行", rows)
    settings = []
    for key in ("issue", "base_commit", "prompt_provenance"):
        settings.append({"設定ID": key, "値": str(manifest[key]), "説明": "移行manifestの元メタデータ"})
    for key, value in manifest["pruned"].items():
        settings.append({"設定ID": f"pruned.{key}", "値": str(value), "説明": "移行後の削除記録"})
    write("素材移行設定", settings)

    # Preserve existing curated 36 rows and register every current canonical
    # image. Binary presence is a fact; it does not imply visual adoption.
    path = LEDGER / "素材.yaml"
    existing = yaml.safe_load(path.read_text(encoding="utf-8"))
    prior = {r["パス"] for r in existing}
    rows = list(existing)
    for image in sorted((ROOT / "assets/images").rglob("*")):
        if image.suffix.lower() not in {".webp", ".png", ".svg"}:
            continue
        rel = image.relative_to(ROOT).as_posix()
        if rel in prior:
            continue
        parts = rel.split("/")
        domain = parts[2]
        owner = ""
        if domain == "characters":
            owner = parts[3]
        elif domain in {"enemies", "summons", "battle-backgrounds"}:
            owner = re.match(r"(?:M|S)\d{3}|BG\d{3}", image.name).group()
        elif domain == "fields":
            found = re.search(r"(?:TRM|KRB|STN|NTR|NTB|UTS|SNL|SCH|NTA|UCH|BDY|APT|OVS|GRD|CST)-\d{2}", image.name, re.I)
            owner = found.group().upper() if found else ""
        elif domain == "brand":
            owner = "BRAND"
        rows.append({"素材ID": f"A-{len(rows)+1:03d}", "所有者ID": owner,
                     "種別": domain, "パス": rel, "状態": "現存（採否未照合）", "日付": "",
                     "来歴": "現存ファイル登録。採用判定を追加しない。所有者が空なら未決。",
                     "sha256": hashlib.sha256(image.read_bytes()).hexdigest(), "特徴(自由記述)": ""})
    assert len({r["パス"] for r in rows if r["パス"]}) == sum(bool(r["パス"]) for r in rows)
    assert len(rows) == 564  # 559 current images and five existing no-path history rows.
    path.write_text("# 表: 素材 — 現存ファイルと採用来歴。\n" + yaml.safe_dump(rows, allow_unicode=True, sort_keys=False, width=100000, default_style='"'), encoding="utf-8")
    print(f"素材: {len(rows)}")


def weapon_tables() -> None:
    text = markdown("blades.md")
    source = section(text, "## 1. 時代別の候補一覧", "## 2. 個性の素")
    candidates = []
    for head, rows in tables(source):
        if head[0] != "刀名":
            continue
        for source_row in rows:
            r = row_map(head, source_row, "blades.md candidates")
            candidates.append({"刀候補ID": f"WREF-{len(candidates)+1:03d}", "刀名": r["刀名"],
                               "種別": r["種別"], "作者": r["作者"], "時代": r["時代"],
                               "指定": r["指定"], "所蔵": r["所蔵"], "特徴": r["特徴"],
                               "逸話": r["逸話（伝承は明記）"], "個性の素": r["個性の素"],
                               "確度": r["確度"], "注": r["注"],
                               "出典": "docs/blades.md §1（原文の出典一覧 §6）", "状態": "候補"})
    assert len(candidates) == 31
    write("刀候補", candidates)
    by_name = {r["刀名"].split("（")[0]: r["刀候補ID"] for r in candidates}
    allocation = section(text, "## 3. 割り当て案", "## 4. 採用に注意")
    parts = re.split(r"(?=^### (?:ペー子|オトン|ナム|シャー))", allocation, flags=re.M)
    person_id = {"ペー子": "C004", "オトン": "C001", "ナム": "C002", "シャー": "C003"}
    assignments = []
    for part in parts:
        m = re.match(r"### (ペー子|オトン|ナム|シャー)", part)
        if not m:
            continue
        person = person_id[m.group(1)]
        for match in re.finditer(r"^([1-5])\. ([^:]+): (.*)$", part, re.M):
            name, reason = match.group(2), match.group(3)
            key = next((ident for label, ident in by_name.items() if name.startswith(label) or label.startswith(name)), "")
            assignments.append({"配分ID": f"WA-{len(assignments)+1:03d}", "人物ID": person,
                                "枠": match.group(1), "刀候補ID": key, "理由": f"{name}: {reason}",
                                "状態": "案"})
    assert len(assignments) == 20
    write("刀配分案", assignments)


def ability_tables() -> None:
    text = markdown("ability-candidates.md")
    pool = section(text, "## 6. 候補プール", "## 7. ジョブ")
    abilities = []
    for head, rows in tables(pool):
        if not head or head[0] != "ID" or len(head) != 10:
            continue
        for source in rows:
            r = row_map(head, source, "ability-candidates.md ability")
            if not re.fullmatch(r"A\d{2}", r["ID"]):
                continue
            abilities.append({"能力ID": r["ID"], "候補": r.get("候補", r.get("候補（参照名で記述）", "")),
                              "型・参照元": r["型・参照元"], "重荷": r["重荷"], "素質": r["素質"],
                              "時代": r["時代"], "定番": r["定番"], "ジョブ重なり": r["ジョブ重なり"],
                              "cmd": r["cmd"], "MG": r["MG"], "状態": "候補（未採用）",
                              "根拠": "docs/ability-candidates.md §6"})
    assert len(abilities) == 36, len(abilities)
    for ident, name in (("A81", "算術型"), ("A82", "たべる型")):
        abilities.append({"能力ID": ident, "候補": name, "型・参照元": "§6-10の追加候補",
                          "重荷": "", "素質": "", "時代": "", "定番": "", "ジョブ重なり": "",
                          "cmd": "", "MG": "", "状態": "候補（未採用）", "根拠": "docs/ability-candidates.md §6-10"})
    write("能力候補", abilities)

    proposal = section(text, "**配分案（20 枠）", "**型の集計")
    head, rows = first_table(proposal, "人物（時代）")
    people = {"ペー子": "C004", "オトン": "C001", "ナム": "C002", "シャー": "C003"}
    current = ""
    allocations = []
    blade_rows = yaml.safe_load((LEDGER / "刀候補.yaml").read_text(encoding="utf-8"))
    for source in rows:
        r = row_map(head, source, "ability-candidates.md allocation")
        if r["人物（時代）"]:
            current = next((ident for label, ident in people.items() if label in r["人物（時代）"]), "")
        blade = r["刀（blades.md）"]
        blade_id = next((b["刀候補ID"] for b in blade_rows if blade.startswith(b["刀名"].split("（")[0]) or b["刀名"].startswith(blade)), "")
        ids = re.findall(r"A\d{2}", r["型・候補 ID（案）"])
        allocations.append({"配分ID": f"BA-{len(allocations)+1:03d}", "人物ID": current,
                            "刀候補ID": blade_id, "能力候補ID": ids[0] if len(ids) == 1 else "",
                            "型": r["型・候補 ID（案）"], "根拠": r["根拠"], "状態": "案（複数候補は未決）"})
    assert len(allocations) == 20
    write("刀能力配分案", allocations)

    jobs = section(text, "### 7-3.", "### 7-4.")
    head, rows = first_table(jobs, "人物")
    role_rows = []
    for i, source in enumerate(rows, 1):
        r = row_map(head, source, "ability-candidates.md jobs")
        actor = r["人物"]
        role_rows.append({"候補ID": f"JROLE-{i:02d}", "役割": actor,
                          "人物ID": "C003" if "シャー" in actor else ("C004" if "ペー子" in actor else ""),
                          "履歴": r["履歴（記録の事実と出典）"],
                          "候補プール": r["候補プール（現実の職業名・案）"],
                          "根拠": r["根拠（履歴との結びつき）"], "状態": "案（個別ジョブ未採用）"})
    assert len(role_rows) == 4
    write("ジョブ候補", role_rows)


def magic_table() -> None:
    text = markdown("learning-schedule.md")
    head, rows = first_table(section(text, "## 1. 魔法一覧", "取得と扱いの決定"), "属性")
    magic = []
    for i, source in enumerate(rows, 1):
        r = row_map(head, source, "learning-schedule.md magic")
        magic.append({"魔法ID": f"MAG-{i:02d}", "属性": r["属性"], "魔法名": r["魔法名（＝敵の技名）"],
                      "効果": r["効果"], "根拠": r["根拠"], "状態": "記録あり（詳細未決あり）"})
    assert len(magic) == 8
    write("魔法", magic)


def main() -> None:
    monster_tables()
    dungeon_tables()
    boss_tables()
    bgm_tables()
    people_tables()
    asset_tables()
    weapon_tables()
    ability_tables()
    magic_table()


if __name__ == "__main__":
    main()
