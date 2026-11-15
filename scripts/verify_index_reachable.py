#!/usr/bin/env python3
"""docs/INDEX.md から（markdown リンクの連鎖で）到達できないファイル（孤立）と壊れたリンクをエラーにする。

  uv run python3 scripts/verify_index_reachable.py              # エラーがあれば exit 1
  LEDGER_ROOT=/path/to/root uv run python3 scripts/verify_index_reachable.py   # root を差し替え（テスト用）

規則の正本は台帳の docs/ledger/ファイル配置.yaml:
  - リポ内の全ファイルが、ちょうど1つの配置規則（パターン）に一致すること（一致なし・複数一致はエラー）
  - 到達=リンク の規則に一致するファイルは INDEX から辿れること（孤立=エラー）
  - 到達=許可 の規則は許可リスト。許可リスト理由が必須で、入口（ファイルまたはディレクトリ）が INDEX から辿れること
  - 辿ったページ（到達=リンクの md）の相対リンクが実在すること（壊れたリンク=エラー）
"""
import os
import re
import subprocess
import sys

import ledger_yaml as LY

INDEX = "docs/INDEX.md"
IGNORED = [".git", "__pycache__", ".DS_Store", ".venv", "node_modules", ".pytest_cache"]
MAP_ID = r"(?:TRM|KRB|STN|NTR|NTB|UTS|SNL|SCH|NTA|UCH|BDY|APT|OVS|GRD|CST)-\d{2}"
REACH = ["リンク", "許可"]
WS = " \t\n\v\f\r\0"

LINK_RE = re.compile(r'!?\[(?:[^\]\\]|\\.)*\]\(\s*<?([^)\s>]+)>?(?:\s+"[^"]*")?\s*\)', re.ASCII)
REF_RE = re.compile(r"^\s*\[[^\]]+\]:\s*<?(\S+?)>?\s*$", re.ASCII | re.M)


def blank(s):
    return not s.strip(WS)


def split_rb(s, sep):
    """Ruby の String#split（末尾の空要素を落とす）"""
    parts = s.split(sep)
    while parts and parts[-1] == "":
        parts.pop()
    return parts


class IndexReachability:
    def __init__(self, root=None):
        self.root = os.path.abspath(root or LY.ROOT)
        self.errors = []
        self.warnings = []

    def err(self, msg):
        self.errors.append(msg)

    def warn(self, msg):
        self.warnings.append(msg)

    def run(self):
        rules = self.load_rules()
        if rules is None:
            return self
        files = self.list_files()
        governing = self.classify(rules, files)
        reached_files, reached_dirs = self.walk(governing)
        self.check_orphans(governing, reached_files)
        self.check_allowlist(rules, governing, reached_files, reached_dirs)
        return self

    def load_rules(self):
        if not os.path.isfile(os.path.join(self.root, INDEX)):
            self.err(f"{INDEX} が無い（到達性の起点）")
            return None
        rows = LY.read("ファイル配置")
        if not rows:
            self.err("docs/ledger/ファイル配置.yaml が無い、または空")
            return None
        ids = [r["配置ID"] for r in rows]
        counts = {}
        for i in ids:
            counts[i] = counts.get(i, 0) + 1
        for i, n in counts.items():
            if n > 1:
                self.err(f"ファイル配置: 配置ID '{i}' が重複")
        for r in rows:
            id_ = r["配置ID"]
            try:
                r["_re"] = re.compile(r"(?:" + r["パターン"].replace("{MAP_ID}", MAP_ID) + r")", re.ASCII)
            except re.error as e:
                self.err(f"ファイル配置 {id_}: パターンが不正（{e}）")
            if r["到達"] not in REACH:
                self.err(f"ファイル配置 {id_}: 到達 '{r['到達']}' は {'/'.join(REACH)} のどちらでもない")
            if r["到達"] == "許可" and blank(r["許可リスト理由"]):
                self.err(f"ファイル配置 {id_}: 到達=許可 には許可リスト理由が要る")
            if r["到達"] == "リンク" and not (blank(r["許可リスト理由"]) and blank(r["入口"])):
                self.err(f"ファイル配置 {id_}: 到達=リンク に許可リスト理由・入口は書かない（許可にする）")
        return [r for r in rows if r["_re"]]

    def list_files(self):
        """リポ内のファイル（repo root からの相対パス、/ 区切り）。git リポならトラッキング対象＋未追跡（.gitignore 除く）、でなければ全走査。"""
        paths = None
        if os.path.exists(os.path.join(self.root, ".git")):
            r = subprocess.run(["git", "-C", self.root, "-c", "core.quotepath=off", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
                               capture_output=True)
            if r.returncode == 0:
                paths = split_rb(r.stdout.decode("utf-8", "surrogateescape"), "\0")
        if paths is None:
            paths = self.walk_fs()
        paths = [p for p in paths if not any(seg in IGNORED for seg in p.split("/"))]
        paths = [p for p in paths if os.path.isfile(os.path.join(self.root, p))]
        return sorted(set(paths))

    def walk_fs(self):
        out = []
        for d, dirs, fs in os.walk(self.root):
            for f in fs:
                out.append(os.path.relpath(os.path.join(d, f), self.root).replace(os.sep, "/"))
        return out

    def classify(self, rules, files):
        gov = {}
        for f in files:
            hit = [r for r in rules if r["_re"].fullmatch(f)]
            if not hit:
                self.err(f"配置規則に無いファイル: {f}（ファイル配置.yaml に規則を足す）")
            elif len(hit) > 1:
                self.err(f"複数の配置規則に一致: {f}（{', '.join(r['配置ID'] for r in hit)}）")
            else:
                gov[f] = hit[0]
        return gov

    def walk(self, governing):
        reached_files = {INDEX: True}
        reached_dirs = {}
        queue = [INDEX]
        while queue:
            page = queue.pop(0)
            for raw in self.links(page):
                target = self.resolve(page, raw)
                if target is None:
                    self.err(f"壊れたリンク（root の外）: {page} → {raw}")
                    continue
                full = os.path.join(self.root, target)
                if os.path.isdir(full):
                    reached_dirs[re.sub(r"/\Z", "", target)] = True
                elif os.path.isfile(full):
                    if target in reached_files:
                        continue
                    reached_files[target] = True
                    if target.endswith(".md") and governing.get(target) and governing[target]["到達"] == "リンク":
                        queue.append(target)
                else:
                    self.err(f"壊れたリンク: {page} → {raw}")
        return reached_files, reached_dirs

    def check_orphans(self, governing, reached_files):
        for f, r in governing.items():
            if r["到達"] != "リンク":
                continue
            if f not in reached_files:
                self.err(f"孤立ファイル（INDEX から辿れない）: {f}（規則 {r['配置ID']}。リンクを張る、または許可リストにする）")

    def check_allowlist(self, rules, governing, reached_files, reached_dirs):
        for r in [r for r in rules if r["到達"] == "許可"]:
            id_ = r["配置ID"]
            if not any(g is r for g in governing.values()):
                self.warn(f"許可リスト {id_}: 一致するファイルが無い（不要になった規則か）")
            for e in [x.strip(WS) for x in split_rb(r["入口"], ";") if x.strip(WS)]:
                e = re.sub(r"/\Z", "", e)
                full = os.path.join(self.root, e.lstrip("/")) if e.startswith("/") else os.path.join(self.root, e)
                if os.path.isdir(full):
                    if e not in reached_dirs:
                        self.err(f"許可リスト {id_}: 入口ディレクトリ {e} が INDEX から辿れない")
                elif os.path.isfile(full):
                    if e not in reached_files:
                        self.err(f"許可リスト {id_}: 入口 {e} が INDEX から辿れない")
                else:
                    self.err(f"許可リスト {id_}: 入口 {e} が実在しない")

    def links(self, page):
        """md 中のリンク先（コードブロック・インラインコード内は除く）"""
        with open(os.path.join(self.root, page), encoding="utf-8", newline="") as f:
            text = f.read()
        keep = []
        fenced = False
        for ln in re.findall(r"[^\n]*\n|[^\n]+", text):
            if ln.lstrip(WS).startswith(("```", "~~~")):
                fenced = not fenced
                continue
            if not fenced:
                keep.append(re.sub(r"`[^`\n]*`", "", ln))
        body = "".join(keep)
        found = LINK_RE.findall(body) + REF_RE.findall(body)
        return [t for t in found if t and not t.startswith("#") and not re.match(r"[a-z][a-z0-9+.\-]*:", t, re.I)]

    def resolve(self, page, raw):
        """ページからの相対リンクを root からの相対パスにする。root の外なら None"""
        t = raw.split("#", 1)[0].split("?", 1)[0]
        t = re.sub(rb"%[0-9A-Fa-f]{2}", lambda m: bytes([int(m.group()[1:], 16)]), t.encode("utf-8", "surrogateescape")).decode("utf-8", "surrogateescape")
        if not t:
            return page
        if t.startswith("/"):
            base = self.root + "/" + t.lstrip("/")
        else:
            base = os.path.normpath(os.path.join(os.path.dirname(os.path.join(self.root, page)), t))
        prefix = self.root + "/"
        if not (base == self.root or base.startswith(prefix)):
            return None
        return "" if base == self.root else base[len(prefix):]


def warn_line(msg):
    """Ruby の Kernel#warn と同じく、末尾が改行なら改行を足さない"""
    print(msg, file=sys.stderr, end="" if msg.endswith("\n") else "\n")


def main():
    v = IndexReachability().run()
    for w in v.warnings:
        warn_line(f"WARN: {w}")
    if not v.errors:
        print("PASS: INDEX から全ファイルが到達でき、孤立・壊れたリンク・配置規則漏れはない")
    else:
        for e in v.errors:
            warn_line(f"FAIL: {e}")
        print(f"FAIL: {len(v.errors)} errors", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
