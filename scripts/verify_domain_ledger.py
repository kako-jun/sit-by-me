#!/usr/bin/env python3
"""Validate normalized MAP/content/Issue tables without interpreting proposals as decisions."""
import hashlib
import re
import argparse
import json
import os
from pathlib import Path

from content_ledger import rows, L
import ledger_flat as F
import asset_chain

# 制作規約より前にある素材の付随表も、汎用の主キー検査（空・重複）の対象にする
ASSET_SIDE_TABLES = ("素材共有", "素材更新", "素材メタデータ", "素材メタデータ値", "素材移行")


def check(require_reviewed=False, from_json=None):
    names = list(L.SCHEMA)[list(L.SCHEMA).index("制作規約"):]
    data = {name: rows(name) for name in names}
    data.update({name: rows(name) for name in ("エリア", "MAP", "決定", "未決", "素材") + ASSET_SIDE_TABLES})
    errors = []

    def need(ok, message):
        if not ok:
            errors.append(message)

    def ids(table, key=None):
        return {r[key or L.SCHEMA[table][0]] for r in data[table]}

    compound = {"体内幾何": ("MAP_ID", "変種", "経路"), "素材メタデータ値": ("メタデータID", "JSONポインタ")}
    for table in [*ASSET_SIDE_TABLES, *names]:
        keys = compound.get(table, (L.SCHEMA[table][0],))
        seen = set()
        for row in data[table]:
            key = tuple(row[k] for k in keys)
            # JSONポインタの空文字はルート要素を表す正規の値
            need(bool(key[0]) if table == "素材メタデータ値" else all(key), f"{table}: 空の主キー {key}")
            need(key not in seen, f"{table}: 主キー重複 {key}")
            seen.add(key)

    shared_pairs = set()
    for row in data["素材共有"]:
        pair = (row["利用者ID"], row["素材ID"])
        need(pair not in shared_pairs, f"素材共有: 関係重複 {pair}")
        shared_pairs.add(pair)
        need(pair[0] in ids("敵") | ids("召喚獣") | ids("人物"), f"素材共有.利用者ID: {pair[0]} が敵・召喚獣・人物にない")
        need(pair[1] in ids("素材"), f"素材共有.素材ID: {pair[1]} が素材にない")

    errors.extend(asset_chain.validate(data["素材更新"], data["素材"], data["素材移行"]))
    meta_ids = ids("素材メタデータ")
    for row in data["素材メタデータ値"]:
        need(row["メタデータID"] in meta_ids, f"素材メタデータ値: {row['メタデータID']} が素材メタデータにない")

    def fk(table, column, target, key=None, allow=(), many=False):
        parents = ids(target, key)
        for row in data[table]:
            values = row[column].split(";") if many else [row[column]]
            for value in values:
                need(not value or value in parents or value in allow,
                     f"{table}.{column}: {value} が {target} にない")

    unknown = ("未決(要確認)",)
    for table in ("図配置", "MAP仕様", "MAP契約", "体内幾何"):
        fk(table, "MAP_ID", "MAP", allow=("GLOBAL",) if table == "体内幾何" else ())
    fk("図配置", "エリアID", "エリア")
    map_area = {r["MAP_ID"]: r["エリアID"] for r in data["MAP"]}
    for row in data["図配置"]:
        need(map_area.get(row["MAP_ID"]) == row["エリアID"], f"図配置: エリア不一致 {row['配置ID']}")
        for key in ("順番", "X", "Y"):
            need(bool(re.fullmatch(r"-?\d+", row[key])), f"図配置: {row['配置ID']}.{key} は整数でない")
    for column in ("起点MAP", "到着MAP"):
        fk("特殊遷移", column, "MAP", allow=unknown, many=True)
    for table, column, target in (
        ("敵配置", "敵ID", "敵"), ("敵配置", "召喚獣ID", "召喚獣"),
        ("敵配置", "ダンジョンID", "ダンジョン"), ("敵配置", "対象MAP", "MAP"),
        ("兼六園再登場", "敵ID", "敵"), ("兼六園再登場", "MAP_ID", "MAP"),
        ("兼六園再登場", "元ダンジョンID", "ダンジョン"),
        ("敵戦利品", "敵ID", "敵"), ("BGM回想編曲", "元スロットID", "BGMスロット"),
        ("BGM旧スロット対応", "現行スロットID", "BGMスロット"),
        ("BGMフレーズ", "元録音ID", "BGM録音"),
        ("人物形態", "人物ID", "人物"), ("刀配分案", "人物ID", "人物"),
        ("刀配分案", "刀候補ID", "刀候補"), ("刀能力配分案", "人物ID", "人物"),
        ("刀能力配分案", "刀候補ID", "刀候補"), ("刀能力配分案", "能力候補ID", "能力候補"),
        ("ジョブ候補", "人物ID", "人物"),
        ("Issue命題", "決定ID", "決定"), ("Issue命題", "未決ID", "未決"),
    ):
        fk(table, column, target, key="録音ID" if column == "元録音ID" else None, allow=unknown, many=True)
    for row in data["Issue命題"]:
        source_id = row["出典ID"].strip()
        need(bool(source_id) and source_id not in unknown and source_id in ids("Issue出典"),
             f"Issue命題.出典ID: {row['命題ID']} の出典 {source_id or '(空欄)'} が必須または未登録")
    enemy_ids = ids("敵") | ids("召喚獣")
    for row in data["敵サイズ"]:
        need(row["敵ID"] in enemy_ids, f"敵サイズ: 未登録ID {row['敵ID']}")
    for row in data["敵配置"]:
        need(bool(row["敵ID"]) != bool(row["召喚獣ID"]), f"敵配置: 敵/召喚獣の一方だけ指定 {row['配置ID']}")
    for row in data["戦闘パターン案"]:
        need(set(re.findall(r"G\d{3}", row["ギミックID"])) <= ids("ボスギミック"), f"戦闘パターン案: 未登録ギミック {row['パターンID']}")
    for table in ("エリア構造", "海外進行", "体内幾何"):
        groups = {}
        for row in data[table]:
            group = (row["MAP_ID"], row["変種"]) if table == "体内幾何" else "all"
            groups.setdefault(group, []).append((row["経路"], row["値"], row["型"]))
        for key, values in groups.items():
            try:
                F.unflatten(values)
            except (ValueError, TypeError, KeyError, IndexError) as exc:
                errors.append(f"{table} {key}: {exc}")

    urls = set()
    sources = {r["出典ID"]: r for r in data["Issue出典"]}
    for row in sources.values():
        ident = row["出典ID"]
        need(row["URL"] not in urls, f"Issue出典: URL重複 {ident}")
        urls.add(row["URL"])
        need(bool(re.fullmatch(r"https://github.com/kako-jun/sit-by-me/issues/" + re.escape(row["Issue番号"]) + r"(?:#issuecomment-\d+)?", row["URL"])), f"Issue出典: URL/番号不一致 {ident}")
        for field in ("本文SHA256", "安全化SHA256"):
            need(bool(re.fullmatch(r"[0-9a-f]{64}", row[field])), f"Issue出典: SHA256形式 {ident}.{field}")
        need(hashlib.sha256(row["本文"].encode()).hexdigest() == row["安全化SHA256"], f"Issue出典: 本文ハッシュ不一致 {ident}")
        need(row["種別"] in ("本文", "コメント"), f"Issue出典: 種別不明 {ident}")
        need(row["点検状態"] in ("確認済み", "自動抽出・要確認"), f"Issue出典: 点検状態不明 {ident}")
    covered = set()
    for row in data["Issue命題"]:
        ident = row["命題ID"]
        covered.add(row["出典ID"])
        need(row["分類"] in ("決定反映", "未決反映", "既存台帳参照", "提案", "作業記録", "撤回・訂正", "対象外", "要確認"), f"Issue命題: 分類不明 {ident}")
        need(row["帰属"] in ("本人引用（Issue内）", "本人決定との記録（逐語なし）", "司令塔既定", "話者未確定"), f"Issue命題: 帰属不明 {ident}")
        need(row["分類"] != "決定反映" or bool(row["決定ID"]), f"Issue命題: 決定IDなし {ident}")
        need(row["分類"] != "未決反映" or bool(row["未決ID"]), f"Issue命題: 未決IDなし {ident}")
        need(row["分類"] != "既存台帳参照" or bool(row["参照先"]), f"Issue命題: 参照先なし {ident}")
        if row["原文抜粋"] and row["出典ID"] in sources:
            need(row["原文抜粋"] in sources[row["出典ID"]]["本文"], f"Issue命題: 抜粋が出典にない {ident}")
        if row["出典ID"] in sources and sources[row["出典ID"]]["点検状態"] == "確認済み":
            need(row["分類"] != "要確認", f"Issue出典: 確認済みだが未分類の命題が残る {ident}")
    need(set(sources) <= covered, "Issue命題: 命題がない出典がある")
    pairs = [(r["録音ID"], r["楽章"]) for r in data["BGM録音"]]
    need(len(pairs) == len(set(pairs)), "BGM録音: 録音ID/楽章の組が重複")
    snapshot = from_json or os.environ.get("LEDGER_ISSUE_SNAPSHOT")
    if snapshot:
        from build_issue_provenance import source_records, digest
        expected = {r["id"]: r for r in source_records(json.loads(Path(snapshot).read_text()))}
        need(set(expected) == set(sources), "Issue出典: snapshotの全文・コメント集合と一致しない")
        for ident in set(expected) & set(sources):
            need(digest(expected[ident]["body"]) == sources[ident]["本文SHA256"], f"Issue出典: snapshotから本文変更 {ident}")
    pending = sum(r["点検状態"] != "確認済み" for r in sources.values())
    if require_reviewed:
        need(not pending, f"Issue出典: 意味点検未完了 {pending}件")
        need(not any(r["分類"] == "要確認" for r in data["Issue命題"]), "Issue命題: 要確認が残る")
    if errors:
        raise SystemExit("\n".join("FAIL: " + e for e in errors))
    print(f"PASS: {len(names)} normalized tables; Issue sources={len(sources)}, semantic review pending={pending}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-reviewed", action="store_true", help="fail until every Issue source has been semantically reviewed")
    parser.add_argument("--from-json", type=Path, help="frozen Issues API snapshot for complete source/hash coverage")
    args = parser.parse_args()
    check(args.require_reviewed, args.from_json)
