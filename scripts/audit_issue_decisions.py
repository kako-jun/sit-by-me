#!/usr/bin/env python3
"""sit-by-me の Issue（本文・コメント）から『kako-jun の決定』と読める候補を列挙し、決定表（docs/ledger/決定.yaml）と突合して
docs/ledger/Issue点検.yaml（分類つき）の過不足を検査・更新する。誤検出より漏れ検出を優先する（迷ったら『未反映(要取込み)』）。

  uv run python3 scripts/audit_issue_decisions.py                       # gh で全 Issue/コメントを取得 → 候補を分類 → Issue点検.yaml と突合（未点検があれば exit 1）
  uv run python3 scripts/audit_issue_decisions.py --from-json F         # 事前取得した JSON を使う（オフライン・テスト用）
  uv run python3 scripts/audit_issue_decisions.py --fetch F             # gh の取得結果を F に保存して終わる（--from-json 用）
  uv run python3 scripts/audit_issue_decisions.py --write               # Issue点検.yaml を更新（【手動】と書いた行の分類は保つ）
  uv run python3 scripts/audit_issue_decisions.py --list 未反映(要取込み)  # 分類ごとの一覧
  uv run python3 scripts/audit_issue_decisions.py --check-quotes [--from-json F]  # 決定.逐語の各引用が 出典URL（; 区切り複数）のコメント本文に実在するか検査（違反があれば exit 1）
  uv run python3 scripts/audit_issue_decisions.py --check-sources [--from-json F] # 全実Issueの出典・ハッシュ・命題リンクを検査
  uv run python3 scripts/audit_issue_decisions.py --check-sources --require-reviewed # 全命題の意味判定完了も要求（未判定があれば exit 1）
  LEDGER_ROOT=/path/to/root ...                               # root 差し替え（テスト用）

候補のヒューリスティック（tools/README.md にも同文）:
  投稿者での絞り込みはしない（Claude が kako-jun のアカウントで投稿するため全コメントが『本人投稿』）。次のいずれかを候補にする:
  見出し  行頭 # の見出しに 決定|確定|承認|合意|指示|発言|指摘|判定|回答|方針|訂正 を含む
  逐語    本文に『逐語』の語がある
  引用    kako-jun|本人|ユーザー|発言|原文|指示|回答|承認 を含む行に 「…」『…』の引用がある
  言及    kako-jun の直後（12字以内）に 指示|決定|承認|OK|まかせ|よい|判断 がある
分類（上から順に最初に当たったもの。決まらなければ 未反映(要取込み)）:
  対象外            プルリクエスト（本文・会話）
  決定表に反映済み   コメントURLが 決定.出典URL にある、または 逐語に抽出した引用（10字以上）が全て 決定.逐語/決定の要点 に含まれる
  決定でない         先頭の見出しが 結果|これからやること|実施記録|進捗|完了|再開|棚卸し 等の作業記録で、逐語の引用が1つも無い
  未反映(要取込み)   上のどれでもない（逐語ありの発言だけが決定表へ取り込む根拠になる。備考に逐語あり/なしを書く）
"""
import hashlib
import json
import os
import re
import subprocess
import sys

import ledger_yaml as LY

# Ruby の \s \d は ASCII のみ。同じ挙動にそろえる
A = re.ASCII
WS = " \t\r\n\f\v"


def strip(s):
    return s.strip(WS + "\0")


def lines_nl(text):
    return re.findall(r"[^\n]*\n|[^\n]+", text)


def ws_strip_all(s):
    return re.sub(r"\s+", "", s, flags=A)


class IssueAudit:
    REPO = "kako-jun/sit-by-me"
    CLASSES = ["決定表に反映済み", "未反映(要取込み)", "決定でない", "対象外"]
    HEAD_RE = re.compile(r"#{1,4}\s*.*(決定|確定|承認|合意|指示|発言|指摘|判定|回答|方針|訂正)", A)
    ATTR_RE = re.compile(r"kako-jun|本人|ユーザー|発言|原文|指示|回答|承認")
    MENTION_RE = re.compile(r"kako-jun.{0,12}(指示|決定|承認|OK|まかせ|よい|判断)")
    QUOTE_RE = re.compile(r"[「『](.{4,400}?)[」』]")
    WORKLOG_RE = re.compile(r"(?:#{1,4}\s*)?(?:\d{4}-\d{2}-\d{2}\s*)?(結果|これからやること|これから行う|実施記録|実施結果|進捗|完了|反映完了|再開|棚卸し|レビュー|実装)", A)
    MANUAL = "【手動】"
    SHORT_QUOTE = 4  # これ未満の引用は、部分一致だと別の文に紛れるので「」ごと完全一致で照合する
    NO_QUOTE_MARK = "（逐語の引用なし"  # 逐語欄にこの語を明記した決定だけが『引用0件』の例外

    def __init__(self, data, tables=None):
        self._issues = {i["number"]: i for i in data["issues"]}
        self._comments = data["comments"]
        self._t = tables if tables is not None else LY.load_all()
        self.quote_stats = None
        self._index_ledger()
        rows = [r for r in (self._classify(c) for c in self._candidates()) if r]
        self.rows = sorted(rows, key=lambda r: (int(r["Issue番号"] or 0), r["_at"]))

    @staticmethod
    def norm(s):
        return ws_strip_all(s if s is not None else "")

    @staticmethod
    def source_id(url):
        """出典URL -> コメントID（文字列）／Issue 本文（"issue-N"）／どちらでもなければ None"""
        m = re.search(r"/issues/(\d+)(?:#issuecomment-(\d+))?\Z", url, A)
        return (m.group(2) or f"issue-{m.group(1)}") if m else None

    @staticmethod
    def squash(s):
        s = ws_strip_all(s if s is not None else "")
        return s.replace("*", "").replace("`", "").replace("『", "「").replace("』", "」")

    @classmethod
    def verbatim_quotes(cls, text):
        """逐語欄から「…」『…』の引用を取り出す（最外側の括弧は 「」『』 のどちらでも引用。入れ子は外側の引用の一部）。"""
        out = []
        depth = 0
        buf = []
        for ch in text:
            if depth == 0:
                if ch in "「『":
                    depth = 1
                    buf = []
                continue
            if ch in "「『":
                depth += 1
                buf.append("「")
            elif ch in "」』":
                depth -= 1
                if depth == 0:
                    out.append("".join(buf))
                else:
                    buf.append("」")
            else:
                buf.append(ch)
        return [q for q in (cls.squash(q) for q in out) if q]

    def check_quotes(self):
        """決定表の各決定について、逐語の各引用が出典URL群のどれかのコメント（または Issue 本文）の本文に実在することを検査する。戻り値: エラー文のリスト。"""
        bodies = {}
        for i in self._issues.values():
            bodies[f"issue-{i['number']}"] = (self.squash(i["body"]), i["html_url"])
        for c in self._comments:
            bodies[str(c["id"])] = (self.squash(c["body"]), c["html_url"])
        errors = []
        self.quote_stats = {"decisions": len(self._t["決定"]), "checked": 0, "quotes": 0, "exceptions": []}
        for d in self._t["決定"]:
            id_ = d["決定ID"]
            qs = self.verbatim_quotes(d["逐語"])
            marked = self.NO_QUOTE_MARK in d["逐語"]
            urls = [u for u in (strip(u) for u in d["出典URL"].split(";")) if u]
            if d["出典"].startswith("docs/decisions.md") and marked:
                self.quote_stats["exceptions"].append(id_)
                continue
            if not urls:
                errors.append(f"決定 {id_}: 出典URLが無い")
                continue
            srcs = [(u, self.source_id(u)) for u in urls]
            for u, sid in srcs:
                if sid is None:
                    errors.append(f"決定 {id_}: 出典URL『{u}』が Issue のコメント（または本文）のURLでない")
            for u, sid in srcs:
                if sid and sid not in bodies:
                    errors.append(f"決定 {id_}: 出典URL『{u}』のコメントを取得結果に見つけられない")
            if not qs:
                if marked:
                    self.quote_stats["exceptions"].append(id_)
                else:
                    errors.append(f"決定 {id_}: 逐語に照合できる引用（「…」『…』）が無い（引用のない決定は逐語欄に『{self.NO_QUOTE_MARK}: 理由）』と明記する）")
                continue
            self.quote_stats["checked"] += 1
            self.quote_stats["quotes"] += len(qs)
            have = [bodies[sid] for _, sid in srcs if sid in bodies]
            for q in qs:
                needle = f"「{q}」" if len(q) < self.SHORT_QUOTE else q
                if any(needle in b for b, _ in have):
                    continue
                cands = [u for b, u in bodies.values() if needle in b][:3]
                errors.append(f"決定 {id_}: 逐語の引用「{q[:30]}」が出典URL群のどのコメントにも実在しない" + ("（どのコメントにも無い）" if not cands else f"（実在するコメント: {' '.join(cands)}）"))
        return errors

    # ---- 台帳側の参照
    def _index_ledger(self):
        self._by_url = {}
        for d in self._t["決定"]:
            for u in (strip(u) for u in d["出典URL"].split(";")):
                if u:
                    self._by_url.setdefault(self.source_id(u), []).append(d["決定ID"])
        self._ledger_text = [(self.norm(d["逐語"]), d["決定ID"]) for d in self._t["決定"]] + [(self.norm(d["決定の要点"]), d["決定ID"]) for d in self._t["決定"]]

    # ---- 候補の抽出
    def _reasons(self, text):
        r = []
        ls = lines_nl(text)
        if any(self.HEAD_RE.match(l) for l in ls):
            r.append("見出し")
        if "逐語" in text:
            r.append("逐語")
        if any(self.ATTR_RE.search(l) and self.QUOTE_RE.search(l) for l in ls):
            r.append("引用")
        if self.MENTION_RE.search(text):
            r.append("言及")
        return r

    def _candidates(self):
        out = []
        for i in self._issues.values():
            body = i.get("body") or ""
            rs = self._reasons(body)
            if rs:
                out.append({"number": i["number"], "url": i["html_url"], "id": f"issue-{i['number']}", "text": body, "at": i.get("created_at"), "reasons": rs, "kind": "本文", "pr": i.get("pull_request")})
        for c in self._comments:
            n = int(re.search(r"(\d+)\Z", c["issue_url"], A).group(1))
            body = c.get("body") or ""
            rs = self._reasons(body)
            if not rs:
                continue
            out.append({"number": n, "url": c["html_url"], "id": str(c["id"]), "text": body, "at": c.get("created_at"), "reasons": rs, "kind": "コメント", "pr": (self._issues.get(n) or {}).get("pull_request")})
        return out

    def _quotes(self, text):
        """逐語として扱う引用（逐語の語があれば本文全体、無ければ帰属表現のある行の引用）。10字以上のものだけを突合に使う"""
        ls = lines_nl(text)
        if "逐語" not in text:
            ls = [l for l in ls if self.ATTR_RE.search(l)]
        qs = [self.norm(q) for l in ls for q in self.QUOTE_RE.findall(l)]
        return list(dict.fromkeys(q for q in qs if len(q) >= 10))

    def _classify(self, c):
        text = c["text"]
        qs = self._quotes(text)
        ls = lines_nl(text)
        first = next((s for s in (strip(l) for l in ls) if s), "")
        head = strip(next((l for l in ls if self.HEAD_RE.match(l)), ""))
        summary = re.sub(r"\A#+\s*", "", head or first, flags=A)[:70]
        m = self.QUOTE_RE.search(text)
        if m:
            summary += f"／「{m.group(1)[:50]}」"
        ids = []
        note = f"検出: {'・'.join(c['reasons'])}（{c['kind']}）"
        hit = self._by_url.get(c["id"])
        if c["pr"] is not None:
            cls = "対象外"
            note += "。プルリクエストの会話"
        elif hit:
            cls = "決定表に反映済み"
            ids = hit
            note += "。決定.出典URL に一致"
        elif qs and all(any(q in t for t, _ in self._ledger_text) for q in qs):
            cls = "決定表に反映済み"
            ids = list(dict.fromkeys(i for q in qs for t, i in self._ledger_text if q in t))
            note += f"。逐語{len(qs)}件が決定表に含まれる"
        elif not qs and self.WORKLOG_RE.match(first) and "逐語" not in c["reasons"] and "引用" not in c["reasons"]:
            cls = "決定でない"
            note += "。作業記録（逐語の引用なし）"
        else:
            cls = "未反映(要取込み)"
            matched = sum(1 for q in qs if any(q in t for t, _ in self._ledger_text))
            note += "。逐語の引用なし（取込みの根拠にできない。要確認）" if not qs else f"。逐語あり{len(qs)}件（うち決定表に含まれる {matched}件）"
        return {"Issue番号": str(c["number"]), "コメントURL": c["url"], "候補の要約": re.sub(r"\s+", " ", summary, flags=A), "分類": cls,
                "決定ID": ";".join(ids), "備考": note, "_at": str(c["at"] if c["at"] is not None else "")}

    def counts(self):
        out = {}
        for r in self.rows:
            out[r["分類"]] = out.get(r["分類"], 0) + 1
        return out


def fetch_all():
    def fetch(path):
        p = subprocess.run(["gh", "api", "--paginate", "--slurp", path], capture_output=True, text=True)
        if p.returncode != 0:
            out = (p.stdout + p.stderr).splitlines()[-3:]
            sys.exit(f"gh api {path} に失敗: {''.join(l + chr(10) for l in out)}")
        flat = []
        for x in json.loads(p.stdout):
            flat.extend(x) if isinstance(x, list) else flat.append(x)
        return flat

    return {"issues": fetch(f"repos/{IssueAudit.REPO}/issues?state=all&per_page=100"),
            "comments": fetch(f"repos/{IssueAudit.REPO}/issues/comments?per_page=100")}


def write_table(rows, root):
    existing = LY.read("Issue点検")
    manual = {r["コメントURL"]: r for r in existing if IssueAudit.MANUAL in r["備考"]}
    merged = [manual.get(r["コメントURL"]) or {k: v for k, v in r.items() if not k.startswith("_")} for r in rows]
    tool = os.path.join(root, ".claude/skills/sit-field-background/tools/ledger_write_rows.py")
    p = subprocess.run(["uv", "run", "--project", root, "python3", tool, "Issue点検"], input=json.dumps(merged, ensure_ascii=False),
                       capture_output=True, text=True, env={**os.environ, "LEDGER_ROOT": root})
    if p.returncode != 0:
        sys.exit(f"Issue点検.yaml の書き込みに失敗: {p.stdout}{p.stderr}")
    return len(merged)


def sha(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def check_source_coverage(data, require_reviewed=False):
    """Issue点検の候補ヒューリスティックとは独立した、全実Issueの出典網羅検査。PASS は出典の保存と構造的なリンクだけを意味する。"""
    issues = {str(i["number"]): i for i in data["issues"]}
    originals = [(i["html_url"], i.get("body") or "") for i in data["issues"] if not i.get("pull_request")]
    for comment in data["comments"]:
        number = comment["issue_url"].split("/")[-1]
        if issues.get(number) is None or issues[number].get("pull_request"):
            continue
        originals.append((comment["html_url"], comment.get("body") or ""))
    expected = dict(originals)
    sources = LY.read("Issue出典")
    claims = LY.read("Issue命題")
    decisions = {d["決定ID"]: d for d in LY.read("決定")}
    source_by_url = {s["URL"]: s for s in sources}
    source_by_id = {s["出典ID"]: s for s in sources}
    errors = []
    if len(source_by_url) != len(sources):
        errors.append("Issue出典.URL に重複あり")
    if len(source_by_id) != len(sources):
        errors.append("Issue出典.出典ID に重複あり")
    for url in expected:
        if url not in source_by_url:
            errors.append(f"Issue出典に無い: {url}")
    for url in source_by_url:
        if url not in expected:
            errors.append(f"取得結果に無いIssue出典: {url}")
    for url, body in expected.items():
        row = source_by_url.get(url)
        if row is None:
            continue
        if row["本文SHA256"] != sha(body):
            errors.append(f"Issue出典の原文SHA256が変化: {url}")
        if row["安全化SHA256"] != sha(row["本文"]):
            errors.append(f"Issue出典の安全化SHA256が不一致: {url}")
    claims_by_source = {}
    for claim in claims:
        claims_by_source.setdefault(claim["出典ID"], []).append(claim)
    for source in sources:
        if not claims_by_source.get(source["出典ID"]):
            errors.append(f"Issue出典に命題行が無い: {source['出典ID']}")
    for claim in claims:
        source = source_by_id.get(claim["出典ID"])
        if source is None:
            errors.append(f"Issue命題 {claim['命題ID']}: 出典IDが無い")
            continue
        excerpt = claim["原文抜粋"]
        if not (excerpt == "" or excerpt in source["本文"]):
            errors.append(f"Issue命題 {claim['命題ID']}: 安全化出典に抜粋が無い")
        if claim["分類"] != "決定反映":
            continue
        # 決定IDは ';' 区切りで複数指定できる。各IDを個別に検査する
        decision_ids = [d for d in (strip(d) for d in claim["決定ID"].split(";")) if d]
        if not decision_ids:
            errors.append(f"Issue命題 {claim['命題ID']}: 決定IDが無い（決定反映なのに決定IDが空）")
        for decision_id in decision_ids:
            decision = decisions.get(decision_id)
            if decision is None:
                errors.append(f"Issue命題 {claim['命題ID']}: 決定IDが無い（{decision_id}）")
            elif source["URL"] not in [strip(u) for u in decision["出典URL"].split(";")]:
                errors.append(f"Issue命題 {claim['命題ID']}: 決定の出典URLと一致しない（{decision_id}）")
    unresolved = sum(1 for c in claims if c["分類"] == "要確認")
    unreviewed_sources = sum(1 for s in sources if s["点検状態"] != "確認済み")
    if require_reviewed and (unresolved > 0 or unreviewed_sources > 0):
        errors.append(f"意味判定が未完了: 出典 {unreviewed_sources} 件・命題 {unresolved} 件")
    for e in errors[:30]:
        print(f"FAIL: {e}", file=sys.stderr)
    print(f"Issue出典の構造検査: 実Issue {len(expected)} 件、出典表 {len(sources)} 件、命題表 {len(claims)} 件、出典未点検 {unreviewed_sources} 件、命題要確認 {unresolved} 件")
    print("PASS: 全実Issueの出典保存・ハッシュ・命題リンクは一致（意味判定は別）" if not errors else f"FAIL: 出典保存・リンク {len(errors)} 件")
    return not errors


def main():
    argv = sys.argv[1:]
    root = LY.ROOT

    def arg(flag):
        return argv[argv.index(flag) + 1] if flag in argv and argv.index(flag) + 1 < len(argv) else None

    f = arg("--fetch")
    if f:
        with open(f, "w", encoding="utf-8") as fh:
            fh.write(json.dumps(fetch_all(), ensure_ascii=False, separators=(",", ":")))
        print(f"保存: {f}")
        return 0
    f = arg("--from-json")
    if f:
        with open(f, encoding="utf-8") as fh:
            data = json.load(fh)
    else:
        data = fetch_all()
    if "--check-sources" in argv:
        return 0 if check_source_coverage(data, require_reviewed="--require-reviewed" in argv) else 1
    audit = IssueAudit(data)
    if "--check-quotes" in argv:
        errors = audit.check_quotes()
        for e in errors:
            print(f"FAIL: {e}", file=sys.stderr)
        st = audit.quote_stats
        ex = st["exceptions"]
        print(f"PASS: 決定{st['decisions']}件中、照合{st['checked']}件・引用{st['quotes']}個・例外{len(ex)}件（逐語の引用なし明記: {' '.join(ex)}）。出典コメントの転記との一致までを保証する（元の発言との一致は保証しない）"
              if not errors else f"FAIL: 逐語の引用が出典に実在しない／照合できない {len(errors)} 件")
        return 0 if not errors else 1
    print(f"Issue {len(data['issues'])} 件・コメント {len(data['comments'])} 件を走査 → 候補 {len(audit.rows)} 件")
    counts = audit.counts()
    for c in IssueAudit.CLASSES:
        print("  %-18s %d" % (c, counts.get(c, 0)))
    cls = arg("--list")
    if cls:
        for r in audit.rows:
            if r["分類"] == cls:
                print(f"{r['Issue番号']}\t{r['コメントURL']}\t{r['候補の要約']}\t{r['備考']}")
    if "--write" in argv:
        print(f"Issue点検.yaml に {write_table(audit.rows, root)} 行を書いた")
        return 0
    table = {r["コメントURL"]: r for r in LY.read("Issue点検")}
    missing = [r for r in audit.rows if r["コメントURL"] not in table]
    urls = {r["コメントURL"] for r in audit.rows}
    stale = [k for k in table if k not in urls]
    diff = [r for r in audit.rows if r["コメントURL"] in table and table[r["コメントURL"]]["分類"] != r["分類"] and IssueAudit.MANUAL not in table[r["コメントURL"]]["備考"]]
    for r in missing[:20]:
        print(f"未点検の候補: Issue #{r['Issue番号']} {r['コメントURL']}（自動分類: {r['分類']}）{r['候補の要約']}", file=sys.stderr)
    for r in diff[:20]:
        print(f"分類が自動判定と違う: {r['コメントURL']}（表: {table[r['コメントURL']]['分類']} / 自動: {r['分類']}）", file=sys.stderr)
    if missing or diff:
        print(f"未点検の候補 {len(missing)} 件・自動判定と違う分類 {len(diff)} 件・表にあるが候補でなくなった行 {len(stale)} 件", file=sys.stderr)
    actual = {}
    for r in table.values():
        actual[r["分類"]] = actual.get(r["分類"], 0) + 1
    print("台帳の分類: " + "、".join(f"{n}={c}" for n, c in actual.items()))
    ok = not missing and not diff
    print("PASS: Issue点検.yaml は候補走査結果と一致（全Issueの意味判定は --check-sources で別途確認）" if ok else "FAIL: --write で更新するか、【手動】つきで分類を確定する")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
