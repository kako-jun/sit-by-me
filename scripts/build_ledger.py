#!/usr/bin/env python3
"""Build/check all deterministic ledger derivatives with one command."""
import argparse
import subprocess
import sys
from datetime import datetime

from content_ledger import ROOT, L, CSV_VIEWS, manifest_bytes, bgm_csv_bytes

TOOLS = ".claude/skills/sit-field-background/tools"


def run(action):
    outputs = [("G-asset-migration", "素材移行JSON", "docs/production/20261018-asset-migration.json", "素材移行|素材移行設定", manifest_bytes())]
    outputs += [(f"G-bgm-{view}-csv", "BGM CSVビュー", str(path.relative_to(ROOT)), table, bgm_csv_bytes(view))
                for view, (table, path) in CSV_VIEWS.items()]
    existing = {r["生成物ID"]: r for r in L.read("生成物")}
    for ident, kind, relative, source, output in outputs:
        path = ROOT / relative
        sha = L.sha(output)
        if action == "check":
            if not path.is_file() or path.read_bytes() != output:
                raise SystemExit(f"FAIL: {relative} is stale")
            if existing.get(ident, {}).get("入力ハッシュ") != sha:
                raise SystemExit(f"FAIL: {ident} 生成物 registration is stale")
        else:
            path.write_bytes(output)
            old = existing.get(ident, {})
            existing[ident] = {"生成物ID": ident, "種別": kind, "パス": relative, "元の表": source,
                              "入力ハッシュ": sha, "生成日時": old.get("生成日時", "") if old.get("入力ハッシュ") == sha else datetime.now().strftime("%Y-%m-%dT%H:%M"),
                              "再生成コマンド": "uv run python3 scripts/build_ledger.py build",
                              "備考": "台帳から導出（手編集禁止）。既存consumerの形式を保持し、内容のSHA256を登録。"}
    if action == "build":
        L.write("生成物", list(existing.values()))
    commands = [f"{TOOLS}/ledger_build.py", "scripts/content_ledger_views.py", "scripts/map_source_views.py", f"{TOOLS}/ledger_views.py", f"{TOOLS}/ledger_index.py"]
    for script in commands:
        subprocess.run([sys.executable, str(ROOT / script), action], cwd=ROOT, check=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("build", "check"))
    run(parser.parse_args().action)
