#!/usr/bin/env python3
"""Build/check a navigable Markdown index for non-MAP content YAML tables."""

from __future__ import annotations

import argparse
import os
import re
from pathlib import Path
from content_ledger import ROOT, rows, L

OUTPUT = ROOT / "docs/ledger/views/content.md"
TABLES = [
    ("敵と戦闘", [
        ("敵", "敵ID", "名称", "遭遇状態"), ("召喚獣", "召喚獣ID", "名称", "敵として戦うか"),
        ("敵サイズ", "サイズ行ID", "敵ID", "グリッド種別"), ("ダンジョン", "ダンジョンID", "名称", "時期"),
        ("敵配置", "配置ID", "敵ID", "採用状態"), ("兼六園再登場", "再登場ID", "敵ID", "状態"),
        ("ボスギミック", "ギミックID", "内容", "採用状態"),
        ("戦闘パターン案", "パターンID", "対象ID", "採用状態"),
        ("敵戦利品", "敵ID", "ドロップ", "根拠")]),
    ("BGM", [
        ("BGMスロット", "スロットID", "抽象名", "状態"),
        ("BGM回想編曲", "編曲ID", "回想場面", "状態"),
        ("BGM旧スロット対応", "対応ID", "旧スロットID", "扱い"),
        ("BGM録音", "録音行ID", "録音ID", "ランク"),
        ("BGMフレーズ", "フレーズ行ID", "主題ID", "要耳確認")]),
    ("人物と素材", [
        ("人物", "人物ID", "呼称", "役割"), ("人物形態", "形態ID", "人物ID", "状態"),
        ("素材", "素材ID", "所有者ID", "状態"), ("素材移行", "旧パス", "新パス", "操作"),
        ("素材移行設定", "設定ID", "値", "説明")]),
    ("刀・能力・ジョブ", [
        ("刀候補", "刀候補ID", "刀名", "状態"), ("刀配分案", "配分ID", "人物ID", "状態"),
        ("能力候補", "能力ID", "候補", "状態"),
        ("刀能力配分案", "配分ID", "人物ID", "状態"),
        ("ジョブ候補", "候補ID", "役割", "状態"), ("魔法", "魔法ID", "魔法名", "状態")]),
]


def cell(value: str) -> str:
    def link(match):
        label, target = match.groups()
        if re.match(r"[a-z]+:|#|/", target):
            return match.group(0)
        source = ROOT / "docs" / target.split("#", 1)[0]
        if not source.exists() and (ROOT / target.split("#", 1)[0]).exists():
            source = ROOT / target.split("#", 1)[0]
        relative = Path(os.path.relpath(source, OUTPUT.parent)).as_posix()
        anchor = "#" + target.split("#", 1)[1] if "#" in target else ""
        if not source.exists():
            # A historical branch may cite an absent review. Preserve its label
            # and source path as text instead of presenting a broken live link.
            return f"{label}（出典記載: `{target}`）"
        return f"[{label}]({relative}{anchor})"
    value = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link, value)
    return value.replace("\n", "<br>").replace("|", "&#124;")


def render() -> str:
    lines = [
        "# コンテンツ台帳の検索ビュー", "", "[ドキュメント入口](../../INDEX.md)", "",
        "このファイルは YAML 正本から生成する。変更は各表の YAML に記録し、",
        "uv run python3 scripts/content_ledger_views.py build で更新する。",
        "敵・人物・召喚獣の生成入力は content_ledger.py query KIND ID --gate を使う。",
    ]
    for heading, tables in TABLES:
        lines.extend(("", f"## {heading}"))
        for table, key, label, state in tables:
            record_rows = rows(table)
            columns = L.SCHEMA[table]
            lines.extend(("", f"### {table} ({len(record_rows)}件)", "",
                          f"正本: [{table}.yaml](../{table}.yaml)", "",
                          "| " + " | ".join(columns) + " |", "|" + " --- |" * len(columns)))
            for row in record_rows:
                lines.append("| " + " | ".join(cell(row.get(k, "")) for k in columns) + " |")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("build", "check"))
    args = parser.parse_args()
    output = render()
    if args.action == "build":
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(output, encoding="utf-8")
        print(f"built {OUTPUT.relative_to(ROOT)}")
    elif not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != output:
        raise SystemExit(f"{OUTPUT.relative_to(ROOT)} is stale")
    else:
        print(f"PASS: {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
