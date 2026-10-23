"""docs/INDEX.md の「台帳の生成ビュー」部分を台帳（docs/ledger/*.yaml）から生成・鮮度検査する。

  uv run python3 ledger_index.py build   # INDEX.md の生成ブロックを書き直す
  uv run python3 ledger_index.py check   # 生成ブロックが台帳から再生成した内容と一致しなければ exit 1（verify_ledger.rb が実行）

INDEX.md の `<!-- GENERATED:BEGIN ledger-views -->` と `<!-- GENERATED:END ledger-views -->` の間だけを扱う（それ以外は人が書く）。
root は環境変数 LEDGER_ROOT で差し替えられる（テスト用）。
"""
import os
import sys

import ledger_io as L

BEGIN = "<!-- GENERATED:BEGIN ledger-views -->"
END = "<!-- GENERATED:END ledger-views -->"
INDEX = os.path.join(L.REPO, "docs", "INDEX.md")
CMD = "uv run python3 .claude/skills/sit-field-background/tools/ledger_index.py"


def cell(s):
    return (s or "").replace("|", "\\|").replace("\n", " ")


def block():
    out = [BEGIN, "",
           "> **生成ビュー（手編集禁止）**。生成元: `docs/ledger/*.yaml`（表の定義は `.claude/skills/sit-field-background/tools/ledger_io.py` の `SCHEMA`・`TABLE_DOC`）。",
           f"> 再生成: `{CMD} build`（リポ直下で実行）。鮮度検査: `{CMD} check`（`ruby scripts/verify_ledger.rb` に含まれる）。台帳を変えたら再生成して同じコミットに入れる。",
           "", "### 台帳の表", "", "| 表 | 行数 | 説明 | 列 |", "|---|---|---|---|"]
    for t in L.SCHEMA:
        exists = os.path.exists(L.path(t))
        n = len(L.read(t)) if exists else 0
        link = f"[{t}](ledger/{t}.yaml)" if exists else f"{t}（ファイル無し）"
        out.append(f"| {link} | {n} | {cell(L.TABLE_DOC.get(t, ''))} | {cell(' / '.join(L.SCHEMA[t]))} |")
    out += ["", "### 台帳から導出した派生物（手編集禁止）", "", "| 生成物ID | 種別 | パス | 再生成コマンド |", "|---|---|---|---|"]
    for g in L.read("生成物"):
        p = g["パス"]
        out.append(f"| {cell(g['生成物ID'])} | {cell(g['種別'])} | [{cell(p)}]({p[5:] if p.startswith('docs/') else '../' + p}) | `{cell(g['再生成コマンド'])}` |")
    out += ["", "### ファイル配置規則", "",
            "置き場所の規則の正本は [ファイル配置.yaml](ledger/ファイル配置.yaml)。パターンは repo root からの相対パスに fullmatch する正規表現。到達=リンクのファイルは INDEX からのリンクの連鎖で辿れなければ孤立（`ruby scripts/verify_index_reachable.rb`）。",
            "", "| 配置ID | 種別 | 用途 | 到達 | 入口 |", "|---|---|---|---|---|"]
    for r in L.read("ファイル配置"):
        out.append(f"| {cell(r['配置ID'])} | {cell(r['種別'])} | {cell(r['用途'])} | {cell(r['到達'])} | {cell(r['入口'])} |")
    out += ["", END]
    return "\n".join(out)


def split(text):
    if BEGIN not in text or END not in text:
        raise SystemExit(f"FAIL: {INDEX} に生成ブロックの印（{BEGIN} … {END}）が無い")
    head, rest = text.split(BEGIN, 1)
    _, tail = rest.split(END, 1)
    return head, tail


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "check"
    with open(INDEX, encoding="utf-8", newline="") as f:
        text = f.read()
    head, tail = split(text)
    new = head + block() + tail
    if cmd == "build":
        if new != text:
            with open(INDEX, "w", encoding="utf-8", newline="") as f:
                f.write(new)
            print("INDEX.md の生成ブロックを更新した")
        else:
            print("INDEX.md の生成ブロックは最新")
    elif cmd == "check":
        if new != text:
            print(f"FAIL: docs/INDEX.md の生成ビューが台帳と一致しない（古い）。再生成: {CMD} build")
            sys.exit(1)
        print("PASS: INDEX.md の生成ビューは台帳と一致")
    else:
        raise SystemExit(f"使い方: {sys.argv[0]} build|check")


if __name__ == "__main__":
    main(sys.argv)
