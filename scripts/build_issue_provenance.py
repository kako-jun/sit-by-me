#!/usr/bin/env python3
"""Build a provenance ledger from a frozen GitHub Issues API snapshot.

The extraction is deliberately conservative. A heading is not proof that the
speaker was kako-jun, and an existing decision's source URL does not make the
rest of that source a decision. All unreviewed sections remain explicit.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import os
from pathlib import Path

import yaml


ROOT = Path(os.environ.get("LEDGER_ROOT", Path(__file__).resolve().parents[1]))
LEDGER = ROOT / "docs" / "ledger"
SOURCE_COLUMNS = [
    "出典ID", "Issue番号", "種別", "URL", "投稿日", "本文SHA256",
    "安全化SHA256", "本文", "点検状態", "備考",
]
CLAIM_COLUMNS = [
    "命題ID", "出典ID", "位置", "要点", "原文抜粋", "帰属", "分類",
    "決定ID", "未決ID", "参照先", "備考",
]
HEADING = re.compile(r"(?m)^#{1,6}\s+[^\n]+")
LOCAL_PATH = re.compile(r"(?<![\w])/(?:Users|home)/[^\s`'\"<>、。，；;）)]+")
HOME_PATH = re.compile(r"(?<![\w])~/[^\s`'\"<>、。，；;）)]+")
WINDOWS_USER_PATH = re.compile(r"(?i)\b[A-Z]:[\\/](?:Users|Documents and Settings)[\\/][^\s`'\"<>、。，；;）)]+")
TEMP_PATH = re.compile(r"(?<![\w])/tmp/[^\s`'\"<>、。，；;）)]+")
PRIVATE_APP_PATH = re.compile(r"~?/\.(?:codex|claude)(?:/[^\s`'\"<>、。，；;）)]+)?")
SESSION_UUID = re.compile(r"(?i)\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b")
PRIVATE_REPO = re.compile(r"freeza(?=[/ ]|の|側|`|\b)", re.I)
TOKEN = re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{20,}\b")
QUOTE = re.compile(r"[「『]([^」』]{2,500})[」』]")
WORKLOG = re.compile(r"結果|これからやること|実施|進捗|完了|レビュー|検証|テスト|着手|作業")
PROPOSAL = re.compile(r"候補|提案|比較|選択肢|仕様案|アイデア|検討")
DECISION = re.compile(r"決定|確定|指示|回答|承認|合意|方針|訂正|撤回|逐語")


class QuotedDumper(yaml.SafeDumper):
    pass


def represent_string(dumper: yaml.SafeDumper, value: str):
    style = "|" if "\n" in value else '"'
    return dumper.represent_scalar("tag:yaml.org,2002:str", value, style=style)


QuotedDumper.add_representer(str, represent_string)


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def safe_text(body: str) -> tuple[str, dict[str, int]]:
    counts: dict[str, int] = {}
    for label, pattern in [
        ("ローカルパス", LOCAL_PATH),
        ("ホーム相対パス", HOME_PATH),
        ("Windowsユーザーパス", WINDOWS_USER_PATH),
        ("一時パス", TEMP_PATH),
        ("私用アプリパス", PRIVATE_APP_PATH),
        ("セッションID", SESSION_UUID),
        ("トークン", TOKEN),
        ("私的リポジトリ", PRIVATE_REPO),
    ]:
        body, count = pattern.subn(f"［{label}省略］", body)
        if count:
            counts[label] = count
    return body, counts


def source_records(data: dict) -> list[dict]:
    issues = {str(issue["number"]): issue for issue in data["issues"]}
    result = []
    for issue in data["issues"]:
        if issue.get("pull_request"):
            continue
        number = str(issue["number"])
        result.append({
            "id": f"ISSUE-{number}-BODY", "number": number, "kind": "本文",
            "url": issue["html_url"], "date": issue["created_at"],
            "body": issue.get("body") or "",
        })
    for comment in data["comments"]:
        number = comment["issue_url"].rstrip("/").rsplit("/", 1)[-1]
        issue = issues.get(number)
        if issue is None:
            raise ValueError(f"Comment {comment.get('id')} refers to absent Issue {number}; snapshot is incomplete")
        if issue.get("pull_request"):
            continue
        result.append({
            "id": f"ISSUE-{number}-C{comment['id']}", "number": number,
            "kind": "コメント", "url": comment["html_url"],
            "date": comment["created_at"], "body": comment.get("body") or "",
        })
    return sorted(result, key=lambda item: (int(item["number"]), item["date"], item["id"]))


def sections(body: str) -> list[tuple[int, int, str, str]]:
    """Keep every character in exactly one section, including preamble text."""
    heads = list(HEADING.finditer(body))
    starts = [0] + [match.start() for match in heads if match.start() != 0]
    starts = sorted(set(starts))
    spans = []
    for i, start in enumerate(starts):
        end = starts[i + 1] if i + 1 < len(starts) else len(body)
        text = body[start:end]
        if not text.strip() and body:
            continue
        line = body.count("\n", 0, start) + 1
        line_end = body.count("\n", 0, end) + (0 if not text or text.endswith("\n") else 1)
        title = text.strip().splitlines()[0] if text.strip() else "（空の本文）"
        spans.append((line, max(line, line_end), title, text))
    return spans or [(1, 1, "（空の本文）", "")]


def section_class(title: str, text: str) -> str:
    headline = title.lstrip("# ").strip()
    if DECISION.search(headline) or "逐語" in text:
        return "要確認"
    if "kako-jun" in text and QUOTE.search(text):
        return "要確認"
    if PROPOSAL.search(headline):
        return "提案"
    if WORKLOG.search(headline):
        return "作業記録"
    if not text.strip():
        return "対象外"
    return "要確認"


def excerpt_for(decision: dict, body: str) -> tuple[str, bool]:
    for match in QUOTE.finditer(decision.get("逐語", "")):
        quoted = match.group(0)
        if quoted in body:
            return quoted, True
        # A past editor may have changed the bracket style while retaining words.
        if match.group(1) in body:
            return match.group(1), True
    return "", False


def build(data: dict, decisions: list[dict]) -> tuple[list[dict], list[dict]]:
    originals = source_records(data)
    by_url = {record["url"]: record for record in originals}
    decision_sources: dict[str, list[dict]] = {}
    for decision in decisions:
        for url in decision.get("出典URL", "").split(";"):
            url = url.strip()
            if url:
                decision_sources.setdefault(url, []).append(decision)
    sources, claims = [], []
    for source in originals:
        body = source["body"]
        safe, redactions = safe_text(body)
        note = "GitHub API原文のSHA256を保持。本文は安全化済み。節の意味分類は自動抽出で再点検が必要。"
        if redactions:
            note += " 安全化: " + ", ".join(f"{key}{value}件" for key, value in redactions.items()) + "。"
        sources.append(dict(zip(SOURCE_COLUMNS, [
            source["id"], source["number"], source["kind"], source["url"],
            source["date"], digest(body), digest(safe), safe,
            "自動抽出・要確認", note,
        ])))
        for decision in decision_sources.get(source["url"], []):
            quote, found = excerpt_for(decision, body)
            clean_quote, quote_redaction = safe_text(quote)
            exact = found and not quote_redaction
            claims.append(dict(zip(CLAIM_COLUMNS, [
                f"{source['id']}.D.{decision['決定ID']}", source["id"],
                "既存決定の出典URL", decision["決定の要点"], clean_quote if exact else "",
                "本人引用（Issue内）" if exact else "話者未確定",
                "決定反映", decision["決定ID"], "", "",
                "既存決定への対応。" + ("出典本文内に引用を照合。" if exact else "この行単独で逐語を照合できない。決定表全体の逐語検査を参照。"),
            ])))
        for index, (first, last, title, section) in enumerate(sections(body), 1):
            safe_section, section_redactions = safe_text(section)
            classification = section_class(title, section)
            safe_title, title_redactions = safe_text(title)
            summary = re.sub(r"\s+", " ", safe_title.lstrip("# ").strip())[:180]
            if not summary:
                summary = "（空の本文）"
            excerpt = safe_section.strip()[:400]
            if section_redactions or title_redactions:
                excerpt = ""  # A redacted excerpt must never masquerade as an exact quote.
            claims.append(dict(zip(CLAIM_COLUMNS, [
                f"{source['id']}.S{index:03d}", source["id"],
                f"行{first}-{last}", summary, excerpt,
                "話者未確定", classification, "", "", "",
                "見出し単位の自動抽出。複数命題の分割・時系列・帰属は要確認。"
                if classification == "要確認" else
                "見出しによる暫定分類。出典全文と他の節に決定がないことを保証しない。",
            ])))
    return sources, claims


def dump_table(name: str, rows: list[dict], columns: list[str]) -> str:
    header = f"# 表: {name} — Issue全件の安全化した出典と命題単位の点検。\n"
    header += "# 列: " + " / ".join(columns) + "\n"
    header += "# 全スカラーは文字列。元本文のSHA256と安全化本文のSHA256を混同しない。\n"
    return header + yaml.dump(rows, Dumper=QuotedDumper, allow_unicode=True, sort_keys=False, width=120)


def keep_reviewed_rows(sources: list[dict], claims: list[dict]) -> tuple[list[dict], list[dict]]:
    """Keep manual semantic review only while its source body hash is unchanged."""
    source_path = LEDGER / "Issue出典.yaml"
    claim_path = LEDGER / "Issue命題.yaml"
    if not source_path.exists() or not claim_path.exists():
        return sources, claims
    old_sources = {row["出典ID"]: row for row in yaml.safe_load(source_path.read_text(encoding="utf-8")) or []}
    old_claims = {row["命題ID"]: row for row in yaml.safe_load(claim_path.read_text(encoding="utf-8")) or []}
    current = {row["出典ID"]: row for row in sources}
    for index, row in enumerate(sources):
        old = old_sources.get(row["出典ID"])
        if old and old["本文SHA256"] == row["本文SHA256"] and old["点検状態"] == "確認済み":
            row["点検状態"] = "確認済み"
            row["備考"] = old["備考"]
    for index, row in enumerate(claims):
        old = old_claims.get(row["命題ID"])
        source = current.get(row["出典ID"])
        old_source = old_sources.get(row["出典ID"])
        if (old and source and old_source and old_source["本文SHA256"] == source["本文SHA256"]
                and "【手動】" in old["備考"]):
            claims[index] = old
    generated_ids = {row["命題ID"] for row in claims}
    for old in old_claims.values():
        source = current.get(old["出典ID"])
        old_source = old_sources.get(old["出典ID"])
        if (old["命題ID"] not in generated_ids and source and old_source
                and old_source["本文SHA256"] == source["本文SHA256"]
                and "【手動】" in old["備考"]):
            claims.append(old)
    return sources, claims


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["build", "check"])
    parser.add_argument("--from-json", required=True, type=Path)
    args = parser.parse_args()
    data = json.loads(args.from_json.read_text(encoding="utf-8"))
    decisions = yaml.safe_load((LEDGER / "決定.yaml").read_text(encoding="utf-8"))
    sources, claims = build(data, decisions)
    sources, claims = keep_reviewed_rows(sources, claims)
    for name, rows, columns in [
        ("Issue出典", sources, SOURCE_COLUMNS),
        ("Issue命題", claims, CLAIM_COLUMNS),
    ]:
        path = LEDGER / f"{name}.yaml"
        output = dump_table(name, rows, columns)
        if args.mode == "build":
            path.write_text(output, encoding="utf-8")
        elif not path.exists() or path.read_text(encoding="utf-8") != output:
            print(f"FAIL: {path} does not match the frozen snapshot")
            return 1
    print(f"{args.mode}: Issue出典 {len(sources)}件・Issue命題 {len(claims)}件")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
