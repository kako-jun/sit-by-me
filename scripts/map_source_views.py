#!/usr/bin/env python3
"""Build/check the original MAP-document table shapes from normalized YAML.

Only GENERATED MAP-SOURCE blocks are replaced. Surrounding prose and tables
outside those blocks remain historical explanation or reference research.
"""
import argparse
import json
import re

from content_ledger import ROOT, L, rows

BEGIN = "<!-- GENERATED:BEGIN MAP-SOURCE "
BLOCK = re.compile(r"<!-- GENERATED:BEGIN MAP-SOURCE ([^ ]+) -->\n.*?<!-- GENERATED:END MAP-SOURCE \1 -->", re.S)


def cell(value):
    return value.replace("|", "\\|").replace("\r", "").replace("\n", "<br>")


def source_values(table, row, header):
    if table == "MAP仕様":
        fields = {"MAP": "原文ID表記", "時期": "時期", "一言特徴": "一言特徴",
                  "不変条件／接続": "経路・通行", "方位・主路・通行条件": "経路・通行", "接続": "経路・通行",
                  "暫定固定": "暫定固定", "不変条件／TBD": "暫定固定"}
    elif table == "MAP契約":
        fields = {"ID": "MAP_ID", "状態": "旧状態", "Ref": "参照ID", "mask / 出力": "mask・出力",
                  "具体的TBD": "具体的TBD", "画像": "画像識別子", "管理名": "画像識別子",
                  "TBD": "具体的TBD", "未決のため必要な個別契約": "具体的TBD", "契約": "具体的TBD",
                  "必須接続": "通行・接続", "地区": "素材状態"}
        # Source registry had a display description and era in separate cells.
        # The one-time migration recorded them together in the feature column.
        feature = row[L.FREE]
        if "／時期: " in feature:
            description, era = feature.rsplit("／時期: ", 1)
        else:
            description, era = feature, ""
        extra = {"一言特徴": description, "時期": era}
    elif table == "接続":
        fields = {"From": "端A", "To": "端B", "種別": "種別", "主路・状態": "出典注記", "型": "種別", "注記": "出典注記"}
    elif table == "特殊遷移":
        fields = {"階": "階", "MAP": "起点MAP", "エレベーター扉": "起点端", "選べる行き先": "行先表示", "出現・解放": "条件"}
    else:
        raise ValueError(f"Unsupported source view table {table}")
    result = []
    for column in header:
        if table == "MAP契約" and column in extra:
            result.append(extra[column])
        elif column in fields:
            result.append(row[fields[column]] or (row.get("MAP_ID", "") if column == "MAP" else ""))
        else:
            raise ValueError(f"{table}: unmapped source column {column}")
    return result


def render(view, data):
    header = json.loads(view["ヘッダーJSON"])
    table = view["元の表"]
    values = data[table]
    if table == "接続":
        lookup = {f"{r['端A']}>{r['端B']}": r for r in values}
    else:
        lookup = {r[L.SCHEMA[table][0]]: r for r in values}
    output = [f"{BEGIN}{view['ビューID']} -->",
              f"> YAML生成ビュー（手編集禁止）。正本: `docs/ledger/{table}.yaml`。再生成: `uv run python3 scripts/build_ledger.py build`。", "",
              "| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    for ident in L.split_list(view["行参照"]):
        if ident not in lookup:
            raise ValueError(f"{view['ビューID']}: source row {ident} missing")
        output.append("| " + " | ".join(cell(v) for v in source_values(table, lookup[ident], header)) + " |")
    output.append(f"<!-- GENERATED:END MAP-SOURCE {view['ビューID']} -->")
    return "\n".join(output)


def run(action):
    views = rows("文書ビュー")
    data = {name: rows(name) for name in {v["元の表"] for v in views}}
    by_path = {}
    for view in views:
        by_path.setdefault(view["パス"], {})[view["ビューID"]] = view
    for relative, records in by_path.items():
        path = ROOT / relative
        text = path.read_text(encoding="utf-8")
        found = set()
        def replace(match):
            ident = match.group(1)
            if ident not in records or ident in found:
                raise ValueError(f"{relative}: unknown/duplicate view marker {ident}")
            found.add(ident)
            return render(records[ident], data)
        expected = BLOCK.sub(replace, text)
        if found != set(records):
            raise ValueError(f"{relative}: missing view markers {sorted(set(records)-found)}")
        if action == "build":
            path.write_text(expected, encoding="utf-8")
        elif text != expected:
            raise SystemExit(f"FAIL: {relative} tables differ from YAML")
    print(f"PASS: {len(views)} MAP source-table views ({len(by_path)} documents)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("build", "check"))
    run(parser.parse_args().action)
