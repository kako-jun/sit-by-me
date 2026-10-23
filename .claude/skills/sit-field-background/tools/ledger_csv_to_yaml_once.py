"""一度きりの変換: docs/ledger/*.csv（24表）→ docs/ledger/<表名>.yaml。以降は YAML が正本。

- 表定義は ledger_io.SCHEMA。行の順序・全セルの文字列を保つ（空欄は ""、複数行は |- ブロック）。
- 書き出したあと YAML を読み戻し、変換前 CSV の全行・全セルと完全一致することを表ごとに検査して出力する。
  1つでも違えば非 0 で終了する。
- 検査に通ったあと CSV を消す（二重管理禁止）のは呼び出し側（git rm）。このスクリプトは CSV を消さない。
- 再実行すると YAML 側の手編集が CSV の内容で上書きされるので、変換後は実行しない（`--force` が要る）。

実行: uv run python3 .claude/skills/sit-field-background/tools/ledger_csv_to_yaml_once.py [--force]
"""
import csv
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ledger_io as L  # noqa: E402


CSV_REV = "40bf95d"  # CSV マスターが最後に存在したコミット


def read_csv(table, text=None):
    if text is None:
        with open(os.path.join(L.LEDGER, f"{table}.csv"), encoding="utf-8", newline="") as f:
            text = f.read()
    import io
    return list(csv.DictReader(io.StringIO(text, newline="")))


def csv_texts():
    """作業ツリーに CSV があればそれ、無ければ CSV_REV（CSV 最後のコミット）の CSV を使う（変換後の再検査用）。"""
    out = {}
    for t in L.SCHEMA:
        p = os.path.join(L.LEDGER, f"{t}.csv")
        if os.path.exists(p):
            with open(p, encoding="utf-8", newline="") as f:
                out[t] = f.read()
        else:
            r = subprocess.run(["git", "show", f"{CSV_REV}:docs/ledger/{t}.csv"], cwd=L.REPO, capture_output=True)
            if r.returncode == 0:
                out[t] = r.stdout.decode("utf-8")
    return out


def main():
    force = "--force" in sys.argv
    verify_only = "--verify-only" in sys.argv
    texts = csv_texts()
    if not verify_only and not force and any(os.path.exists(L.path(t)) for t in L.SCHEMA):
        sys.exit("YAML が既にある。変換は一度きり（上書きするなら --force、検査だけなら --verify-only）")
    bad = 0
    total_rows = total_cells = 0
    for t in L.SCHEMA:
        if t not in texts:
            print(f"SKIP {t}: CSV が無い")
            continue
        src = read_csv(t, texts[t])
        cols = L.SCHEMA[t]
        header = texts[t].split("\n", 1)[0].rstrip("\r")
        if header != ",".join(cols):
            print(f"NG   {t}: CSV ヘッダが SCHEMA と違う: {header}")
            bad += 1
            continue
        if not verify_only:
            L.write(t, [{c: (r.get(c) or "") for c in cols} for r in src])
        back = L.read(t)
        want = [{c: (r.get(c) or "") for c in cols} for r in src]
        cells = len(want) * len(cols)
        diffs = []
        if len(back) != len(want):
            diffs.append(f"行数 {len(want)} != {len(back)}")
        else:
            for i, (a, b) in enumerate(zip(want, back)):
                if list(b) != cols or a != b:
                    diffs.append(f"{i + 2}行目")
        if diffs:
            bad += 1
            print(f"NG   {t}: {diffs[:5]}")
        else:
            print(f"OK   {t}: 行 {len(want)} / セル {cells} 一致")
            total_rows += len(want)
            total_cells += cells
    print(f"SUMMARY: 表 {len(L.SCHEMA)} / 行 {total_rows} / セル {total_cells} / 不一致表 {bad}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
