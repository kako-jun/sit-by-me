#!/usr/bin/env python3
"""Generate review-only name-name drafts from per-event YAML files."""
import argparse
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "docs/ledger/イベント"
PREVIEW = ROOT / "docs/production/event-preview"
EVENTS = PREVIEW / "events"
INDEX = PREVIEW / "README.md"
INDEX_MARKER = "<!-- 生成物: イベント台帳のレビュー用目次。手編集しない。 -->"
BOOK = PREVIEW / "all_events.md"
BOOK_MARKER = "<!-- 生成物: イベント台帳の通読用仮稿。手編集しない。 -->"
ID_RE = re.compile(r"[a-zA-Z0-9_-]+\Z")


def text_value(record, key, fallback="未記入"):
    value = record.get(key)
    return str(value).strip() if value is not None and str(value).strip() else fallback


def escaped(value):
    return value.replace("|", "\\|").replace("\n", " ").replace("\r", " ")


def load_record(path):
    record = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(record, dict):
        raise ValueError(f"{path.name}: 台帳は1件のYAMLマップである必要があります")
    event_id = record.get("イベントID")
    if not isinstance(event_id, str) or not ID_RE.fullmatch(event_id) or path.stem != event_id:
        raise ValueError(f"{path.name}: イベントIDとファイル名が一致しないか、IDが不正です")
    script = record.get("脚本")
    if not isinstance(script, str) or not script.strip():
        raise ValueError(f"{path.name}: 脚本がありません")
    if not re.search(r"(?m)^\[イベント [^\]\n]+\]$|^\[戦闘 [^\]\n]+\]$", script):
        raise ValueError(f"{path.name}: イベントまたは戦闘の宣言がありません")
    return record


def sort_key(record):
    era = text_value(record, "ERA", "")
    match = re.search(r"ERA-(\d+)", era)
    era_number = int(match.group(1)) if match else 999
    # An explicit ordering key is preferred. E references provide only a rough
    # fallback; name order within an E is not a claim about story chronology.
    explicit = text_value(record, "表示順", "")
    existing = text_value(record, "既存イベントID", "")
    event_match = re.search(r"E(\d+)", existing)
    event_number = int(event_match.group(1)) if event_match else 999
    explicit_number = int(explicit) if explicit.isdecimal() else 999999
    return (era_number, explicit_number, event_number, record["イベントID"])


def preview_marker(source):
    return f"<!-- 生成物: docs/ledger/イベント/{source.name} が正本。"


def render_event(source, record):
    pending = text_value(record, "未決", "未決事項の記載なし").replace("--", "—").replace("\n", " ")
    header = (f"{preview_marker(source)}仮稿・ゲームへ接続しない。"
              f"未決: {pending} -->\n\n")
    title = text_value(record, "名称", record["イベントID"]).replace("\n", " ")
    return f"{header}## {record['イベントID']}: {title}（仮稿）\n\n{record['脚本'].rstrip()}\n"


def render_index(records):
    rows = [
        INDEX_MARKER,
        "# イベント脚本レビュー用目次",
        "",
        f"イベント台帳 {len(records)} 件から生成。すべてレビュー用の仮稿で、ゲームへの接続や実行を保証しない。",
        "時代順、明示された表示順、既存 E 番号、ID の順に表示。表示順は仮の時系列であり、未指定分は各時代の後に仮置きする。",
        "[全イベントの通読版](all_events.md)",
        "",
        "| 時代 | 既存E | 場面 | 生成ファイル | 状態 | 正本 |",
        "|---|---|---|---|---|---|",
    ]
    for source, record in records:
        event_id = record["イベントID"]
        era = escaped(text_value(record, "ERA"))
        existing = escaped(text_value(record, "既存イベントID"))
        title = escaped(text_value(record, "名称", event_id))
        status = escaped(text_value(record, "状態"))
        rows.append(
            f"| {era} | {existing} | {title} | [{event_id}.md](events/{event_id}.md) "
            f"| {status} | [{source.name}](../../ledger/イベント/{source.name}) |"
        )
    return "\n".join(rows) + "\n"


def render_book(records):
    rows = [
        BOOK_MARKER,
        "# シナリオ通読用の仮稿",
        "",
        f"全{len(records)}イベント。台帳から生成した人間のレビュー用であり、ゲーム実行用ではありません。",
        "時代・表示順による仮の時系列です。会話、演出、設定上未決の展開は全て仮稿です。",
    ]
    for source, record in records:
        event_id = record["イベントID"]
        rows.extend([
            "",
            f"## {text_value(record, 'ERA')} / {text_value(record, '名称', event_id)}",
            "",
            f"ID: `{event_id}` ／ 状態: {text_value(record, '状態')} ／ "
            f"[正本](../../ledger/イベント/{source.name}) ／ [個別md](events/{event_id}.md)",
            "",
            f"目的: {text_value(record, '目的')}",
            "",
            record["脚本"].rstrip(),
        ])
    return "\n".join(rows) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    paths = sorted(SOURCES.glob("*.yaml"))
    if not paths:
        raise SystemExit("イベント台帳が見つかりません")
    try:
        records = [(path, load_record(path)) for path in paths]
    except (OSError, ValueError, yaml.YAMLError) as exc:
        raise SystemExit(str(exc)) from exc
    records.sort(key=lambda pair: sort_key(pair[1]))
    outputs = [(EVENTS / f"{record['イベントID']}.md", render_event(source, record), preview_marker(source))
               for source, record in records]
    outputs.append((INDEX, render_index(records), INDEX_MARKER))
    outputs.append((BOOK, render_book(records), BOOK_MARKER))
    # A removed or renamed source must not leave a misleading old preview.
    # Never delete the orphan automatically: it may contain hand edits.
    expected_events = {path for path, _, _ in outputs if path.parent == EVENTS}
    orphans = sorted(path for path in EVENTS.glob("*.md") if path not in expected_events)
    if orphans:
        names = ", ".join(str(path.relative_to(ROOT)) for path in orphans)
        raise SystemExit(f"対応する台帳のない md が残っているため生成しません: {names}")
    # Preflight all paths before writing anything: never overwrite a manual file.
    for path, _, marker in outputs:
        if path.exists() and not path.read_text(encoding="utf-8").startswith(marker):
            raise SystemExit(f"生成先が対応する生成物ではないため上書きしません: {path.relative_to(ROOT)}")
    EVENTS.mkdir(parents=True, exist_ok=True)
    for path, content, _ in outputs:
        path.write_text(content, encoding="utf-8")
    print(f"{len(records)}件のイベントと目次を生成: {PREVIEW.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
