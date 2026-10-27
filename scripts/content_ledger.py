#!/usr/bin/env python3
"""Query non-MAP YAML masters and build the historical asset migration JSON.

`query KIND ID --gate` emits the deterministic facts to put in a generation
prompt. It fails when an identity, encounter status, or required grid size is
unresolved. The query never promotes candidate proposals to decisions.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / ".claude/skills/sit-field-background/tools"))
import ledger_io as L

ROOT = Path(os.environ.get("LEDGER_ROOT", L.REPO))
LEDGER = ROOT / "docs/ledger"
MANIFEST = ROOT / "docs/production/20261018-asset-migration.json"
CSV_VIEWS = {
    "sources": ("BGM録音", ROOT / "docs/bgm-sources.csv"),
    "phrases": ("BGMフレーズ", ROOT / "docs/bgm-phrases.csv"),
}
CSV_FIELDS = {
    "sources": ["id", "録音名", "演奏者", "録音年", "楽章", "ファイルパス", "ランク",
                "ライセンス表記(原文)", "出典URL", "クレジット文言",
                "ffprobeで実測した長さ(秒)", "形式", "備考"],
    "phrases": ["主題ID", "楽章", "主題名", "録音ID", "開始秒", "終了秒",
                "気分(悲/楽/緊)", "割当スロット候補",
                "出力ファイル(~/data/sit-bgm/suno-input/ 配下)", "要耳確認"],
}


def rows(table: str) -> list[dict[str, str]]:
    path = LEDGER / f"{table}.yaml"
    return L.parse(table, path.read_text(encoding="utf-8"))


def candidate(value: str) -> bool:
    return any(word in value for word in ("案", "未決", "未定", "未照合", "TBD", "候補", "要確認"))


def shape_vocabulary_errors(shape: dict, vocabulary: list) -> list:
    """人物形態1行を語彙（人物形態.年齢/衣装/車椅子/規則）に照らした誤り。語彙が無ければ全値が語彙外になる。"""
    errors = []
    for field in ("年齢", "衣装", "車椅子"):
        allowed = {r["値"] for r in vocabulary if r["グループ"] == f"人物形態.{field}"}
        value = shape.get(field, "").strip()
        if not value or candidate(value) or value not in allowed:
            errors.append(f"{shape['形態ID']}.{field}が未確定または語彙外: {value or '(空欄)'}")
    for rule in (r["値"] for r in vocabulary if r["グループ"] == "人物形態.規則"):
        try:
            when, then = (dict(part.split("=", 1) for part in side.split(";")) for side in rule.split(":", 1))
        except ValueError:
            errors.append(f"人物形態.規則 の書式エラー（「列=値;列=値:列=値」の形で書く）: {rule!r}")
            continue
        if all(shape.get(k) == v for k, v in when.items()) and any(shape.get(k) != v for k, v in then.items()):
            errors.append(f"{shape['形態ID']}: 規則 {rule} に反する")
    return errors


def refs(value: str) -> list[str]:
    return list(dict.fromkeys(re.findall(r"(?:M|S|C)\d{3}|(?:G|P)\d{3}", value)))


def applicable_decisions(kind: str, ident: str, related: set[tuple[str, str]] | None = None) -> list[dict[str, str]]:
    target_names = {
        "enemy": {"敵", "モンスター"},
        "summon": {"召喚獣"},
        "character": {"人物", "キャラクター", "登場人物"},
    }[kind]
    targets = {(name, ident) for name in target_names} | (related or set())
    result = []
    for row in rows("決定"):
        if row.get("状態") != "有効":
            continue
        if (row.get("対象種別"), row.get("対象ID")) in targets or row.get("対象種別") in {"全体", "共通"}:
            result.append(row)
    return result


def matching_assets(ident: str) -> list[dict[str, str]]:
    shared_ids = {r["素材ID"] for r in rows("素材共有") if r["利用者ID"] == ident}
    return [r for r in rows("素材")
            if r.get("パス") and (r.get("所有者ID") == ident or r["素材ID"] in shared_ids)]


def query(kind: str, ident: str, gate: bool = False, form: str = "", size_row: str = "") -> dict:
    spec = {
        "enemy": ("敵", "敵ID"),
        "summon": ("召喚獣", "召喚獣ID"),
        "character": ("人物", "人物ID"),
    }
    table, key = spec[kind]
    entities = [row for row in rows(table) if row[key] == ident]
    if not entities:
        raise ValueError(f"{table} {ident} is absent")
    entity = entities[0]
    assets = matching_assets(ident)
    result = {"種別": table, "ID": ident, "本体": entity,
              "採用素材": [r for r in assets if r["状態"] == "採用"],
              "採否未照合・参考素材": [r for r in assets if r["状態"] != "採用"],
              "未解決": []}
    if len(entities) > 1:
        result["未解決"].append(f"{table}.{key}={ident} の主キーが重複 ({len(entities)}行)")
    for field in ("名称",) if kind != "character" else ("呼称",):
        if not entity.get(field) or candidate(entity[field]):
            result["未解決"].append(f"{field}が未確定")
    if kind in {"enemy", "summon"}:
        all_sizes = rows("敵サイズ")
        result["サイズ"] = [r for r in all_sizes if r["敵ID"] == ident]
        if size_row:
            result["サイズ"] = [r for r in result["サイズ"] if r["サイズ行ID"] == size_row]
            if not result["サイズ"]:
                result["未解決"].append(f"指定サイズ行 {size_row} は {ident} に存在しない")
        elif len(result["サイズ"]) > 1:
            result["未解決"].append("複数のサイズ行から対象形態を選ぶ必要がある（--size-row）")
        for key_id in {r["サイズ行ID"] for r in result["サイズ"]}:
            if sum(r["サイズ行ID"] == key_id for r in all_sizes) > 1:
                result["未解決"].append(f"敵サイズ.サイズ行ID={key_id} の主キーが重複")
        result["配置"] = [r for r in rows("敵配置") if r.get("敵ID") == ident or r.get("召喚獣ID") == ident]
        result["戦闘パターン案"] = [r for r in rows("戦闘パターン案") if ident in refs(r.get("対象ID", ""))]
        used = {ref for r in result["戦闘パターン案"] for ref in re.findall(r"G\d{3}", r.get("ギミックID", ""))}
        result["ボスギミック"] = [r for r in rows("ボスギミック") if r["ギミックID"] in used or ident in refs(r.get("使う予定", ""))]
        if kind == "enemy":
            result["戦利品"] = [r for r in rows("敵戦利品") if r["敵ID"] == ident]
        if kind == "enemy" and entity["遭遇状態"] == "非遭遇":
            result["未解決"].append("非遭遇ID: 戦闘敵として生成しない")
        if not result["サイズ"] or all(candidate(r.get("グリッド種別", "")) or not r.get("グリッド種別") for r in result["サイズ"]):
            result["未解決"].append("戦闘グリッド種別が未確定")
        if kind == "enemy" and entity["遭遇状態"] == "ID案・未決":
            result["未解決"].append("敵IDは案・未決")
        if kind == "enemy" and entity["遭遇状態"] not in {"記録あり", "非遭遇", "ID案・未決"}:
            result["未解決"].append("遭遇状態が未確定または語彙外")
        allowed_grids = {r["値"] for r in rows("語彙") if r["グループ"] == "敵グリッド種別"}
        # The domain has four named battle-grid sizes. A missing vocabulary
        # table entry must not permit an arbitrary string through the gate.
        allowed_grids |= {"1x1", "1x2", "2x1", "2x2", "2x3", "2x4", "2x6", "4x1"}
        for r in result["サイズ"]:
            grid = r["グリッド種別"].replace("**", "").split("（", 1)[0]
            if grid not in allowed_grids:
                result["未解決"].append(f"戦闘グリッド種別が語彙外: {r['グリッド種別']}")
    else:
        all_forms = rows("人物形態")
        result["形態"] = [r for r in all_forms if r["人物ID"] == ident]
        if form:
            result["形態"] = [r for r in result["形態"] if r["形態ID"] == form]
            if not result["形態"]:
                result["未解決"].append(f"指定形態 {form} は {ident} に存在しない")
            else:
                master = result["形態"][0]["マスターパス"]
                result["採用素材"] = [r for r in result["採用素材"] if r["パス"] == master]
                result["採否未照合・参考素材"] = [r for r in result["採否未照合・参考素材"] if r["パス"] == master]
        elif len(result["形態"]) > 1:
            result["未解決"].append("複数の人物形態から対象を選ぶ必要がある（--form）")
        if not result["形態"]:
            result["未解決"].append("人物マスター形態が未登録")
        for key_id in {r["形態ID"] for r in result["形態"]}:
            if sum(r["形態ID"] == key_id for r in all_forms) > 1:
                result["未解決"].append(f"人物形態.形態ID={key_id} の主キーが重複")
        # 許可値・組み合わせ規則は台帳の語彙（グループ「人物形態.<列>」「人物形態.規則」）が正本
        for shape in result["形態"]:
            result["未解決"].extend(shape_vocabulary_errors(shape, rows("語彙")))
    related = {("素材", r["素材ID"]) for label in ("採用素材", "採否未照合・参考素材") for r in result[label]}
    related |= {("人物形態", r["形態ID"]) for r in result.get("形態", [])}
    related |= {("敵サイズ", r["サイズ行ID"]) for r in result.get("サイズ", [])}
    result["決定"] = applicable_decisions(kind, ident, related)
    targets = {(table, ident)} | related
    targets |= {("敵サイズ", r["サイズ行ID"]) for r in result.get("サイズ", [])}
    # Exact MAP placement is intentionally irrelevant to creating a sprite;
    # unresolved identity, form, and size facts must stop generation.
    result["未決行"] = [r for r in rows("未決") if r["状態"] == "未決"
                       and (r["対象テーブル"], r["対象ID"]) in targets]
    result["未解決"].extend(f"{r['未決ID']}: {r['キー']} {r['内容']}" for r in result["未決行"])
    if gate and result["未解決"]:
        raise ValueError(f"{table} {ident}: " + "; ".join(result["未解決"]))
    return result


def format_prompt(facts: dict) -> str:
    lines = [f"# {facts['種別']} {facts['ID']} — 台帳から導出した生成入力", "\n## 本体"]
    for key, value in facts["本体"].items():
        if value:
            lines.append(f"- {key}: {value}")
    for label in ("サイズ", "配置", "形態", "採用素材", "採否未照合・参考素材", "戦利品", "決定", "戦闘パターン案", "ボスギミック"):
        values = facts.get(label, [])
        if not values:
            continue
        lines.append(f"\n## {label}")
        for value in values:
            status = value.get("状態", value.get("採用状態", ""))
            lines.append(f"- {json.dumps(value, ensure_ascii=False, sort_keys=True)}")
            if candidate(status):
                lines.append("  - 候補/未決。採用済みの決定として使わない。")
    if facts["未解決"]:
        lines.append("\n## 未解決ゲート")
        lines.extend(f"- {x}" for x in facts["未解決"])
    return "\n".join(lines) + "\n"


def manifest_payload() -> dict:
    settings = {r["設定ID"]: r["値"] for r in rows("素材移行設定")}
    entries = []
    for row in rows("素材移行"):
        item = {"old": row["旧パス"], "new": row["新パス"] or None,
                "action": row["操作"], "reason": row["理由"], "sha256": row["sha256"]}
        if row.get("剪定パス"):
            item["pruned_path"] = row["剪定パス"]
        entries.append(item)
    pruned = {key[7:]: (int(value) if key.endswith("count") or key.endswith("issue") else value)
              for key, value in settings.items() if key.startswith("pruned.")}
    payload = {"issue": int(settings["issue"]), "base_commit": settings["base_commit"],
               "prompt_provenance": settings["prompt_provenance"], "entries": entries, "pruned": pruned}
    return payload


def manifest_bytes() -> bytes:
    # Preserve existing consumer shape and indentation; the provenance metadata
    # for generated outputs is stored in 生成物.yaml, not injected into entries.
    return (json.dumps(manifest_payload(), ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def bgm_csv_bytes(view: str) -> bytes:
    table, _ = CSV_VIEWS[view]
    record_rows = rows(table)
    fieldnames = CSV_FIELDS[view]
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fieldnames, lineterminator="\r\n")
    writer.writeheader()
    for row in record_rows:
        projected = {}
        for field in fieldnames:
            source_key = ("録音ID" if view == "sources" and field == "id" else
                          "出力ファイル" if field.startswith("出力ファイル(") else field)
            projected[field] = row[source_key]
        writer.writerow(projected)
    return output.getvalue().encode("utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    q = sub.add_parser("query")
    q.add_argument("kind", choices=("enemy", "summon", "character"))
    q.add_argument("id")
    q.add_argument("--gate", action="store_true")
    q.add_argument("--json", action="store_true")
    q.add_argument("--form", default="", help="人物形態.形態ID (例 FORM-001)")
    q.add_argument("--size-row", default="", help="敵サイズ.サイズ行ID (例 SZ-059)")
    m = sub.add_parser("manifest")
    m.add_argument("action", choices=("build", "check"))
    c = sub.add_parser("bgm-csv")
    c.add_argument("action", choices=("build", "check"))
    args = parser.parse_args()
    if args.command == "query":
        value = query(args.kind, args.id, args.gate, args.form, args.size_row)
        print(json.dumps(value, ensure_ascii=False, indent=2) if args.json else format_prompt(value), end="")
        return
    if args.command == "bgm-csv":
        for view, (_, path) in CSV_VIEWS.items():
            output = bgm_csv_bytes(view)
            if args.action == "build":
                path.write_bytes(output)
            elif path.read_bytes() != output:
                raise SystemExit(f"{path.relative_to(ROOT)} is stale against its BGM YAML master")
        print("BGM CSV views match YAML masters" if args.action == "check" else "built BGM CSV views")
        return
    output = manifest_bytes()
    if args.action == "build":
        MANIFEST.write_bytes(output)
        print(f"built {MANIFEST.relative_to(ROOT)}: {len(rows('素材移行'))} entries")
    elif MANIFEST.read_bytes() != output:
        raise SystemExit("asset migration JSON is stale against 素材移行.yaml")
    else:
        print("asset migration JSON matches 素材移行.yaml")


if __name__ == "__main__":
    main()
