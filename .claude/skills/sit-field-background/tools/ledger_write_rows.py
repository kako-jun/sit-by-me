"""標準入力の JSON（行の配列）を台帳の1表として書く（YAML の書き出しは Python の ledger_io だけが行う）。
  echo '[{...}]' | uv run python3 ledger_write_rows.py TABLE
audit_issue_decisions.rb --write が使う。root は LEDGER_ROOT で差し替え可。
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ledger_io as L  # noqa: E402

if __name__ == "__main__":
    table = sys.argv[1]
    if table not in L.SCHEMA:
        sys.exit(f"未定義の表: {table}")
    L.write(table, json.load(sys.stdin))
