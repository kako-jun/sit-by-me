#!/usr/bin/env python3
"""E2 の生成スケジューラ: 依存グラフ（dependency-graph.json）と各MAPの確定状態から『今起動できるMAP』を出す。

依存関係で直列か並列かを決める（同じ建物・扉・家具・場所を複数枚で描くなら先に確定→参考画像として次へ。共有しないなら並列）。
確定＝manifest.json の adoption.canonical（正本パス）が存在する（`oblique_build.py --adopt IMG --take N --canonical PATH`）。

使い方（リポ直下で。`uv run python3 -I`）:
  oblique_e2_schedule.py list                 全MAPの依存・確定・起動可否
  oblique_e2_schedule.py check MAP            親が全て確定済みか、かつ manifest が使えるか（validate エラー・プロンプトが blocked／失効／古いなら理由を全部出して終了コード1）。list／launch も同じ判定（blockers）を使う
  oblique_e2_schedule.py refs MAP             確定済みの親の正本画像を `PARENT=path` で列挙（参考画像）
  oblique_e2_schedule.py graph                グラフの検証（循環・存在しないID・自己参照・plan との不一致）
  oblique_e2_schedule.py launch [--dry-run]   起動可能（親が確定済みでプロンプトが blocked でない）で未確定のMAPを並列にバックグラウンド起動（oblique_e2_run.sh MAP 4）。blocked は理由を出して外す
"""
import json, os, re, subprocess, sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import oblique_freshness as FR  # noqa: E402

ROOT = Path(__file__).resolve().parents[4]
OB = ROOT / "docs/production/oblique-mocks"
GRAPH = OB / "dependency-graph.json"
ID_RE = re.compile(r"^[A-Z]{3}-\d{2}(-[a-z]+)?$")


def load():
    g = json.loads(GRAPH.read_text(encoding="utf-8"))
    return g["maps"]


def manifest_of(mid):
    p = OB / mid / "manifest.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def canonical_of(mid):
    a = manifest_of(mid).get("adoption") or {}
    c = a.get("canonical")
    return (ROOT / c) if c and (ROOT / c).exists() else None


def confirmed(mid):
    return canonical_of(mid) is not None


def has_plan(mid):
    base = re.sub(r"-(kids|fire|burnt|wc)$", "", mid)
    return (OB / f"{base}-plan.json").exists()


def validate(maps):
    errs = []
    for k, v in maps.items():
        if not ID_RE.match(k):
            errs.append(f"{k}: ID の形が不正")
        for d in v.get("depends_on", []):
            if d == k:
                errs.append(f"{k}: 自己参照")
            elif d not in maps:
                errs.append(f"{k}: depends_on の {d} がグラフに無い")
    state = {}

    def dfs(n, stack):
        state[n] = 1
        for d in maps.get(n, {}).get("depends_on", []):
            if d not in maps:
                continue
            if state.get(d) == 1:
                errs.append("循環: " + " -> ".join(stack + [n, d]))
            elif d not in state:
                dfs(d, stack + [n])
        state[n] = 2
    for k in maps:
        if k not in state:
            dfs(k, [])
    # plan の depends_on とグラフの一致
    for k in maps:
        base = re.sub(r"-(kids|fire|burnt|wc)$", "", k)
        pp = OB / f"{base}-plan.json"
        if not pp.exists():
            continue
        pl = json.loads(pp.read_text(encoding="utf-8"))
        want = (pl.get("variants", {}).get(k[len(base) + 1:], {}) if k != base else pl).get("depends_on")
        if want is None:
            errs.append(f"{k}: plan に depends_on が無い")
        elif sorted(want) != sorted(maps[k].get("depends_on", [])):
            errs.append(f"{k}: plan の depends_on {want} がグラフ {maps[k].get('depends_on')} と不一致")
    return errs


def status(maps, mid):
    deps = maps[mid].get("depends_on", [])
    miss = [d for d in deps if not confirmed(d)]
    return deps, miss


def blockers(maps, mid):
    """起動できない理由の一覧（空なら起動可）。list／check／launch が共有する唯一の判定（#193）。
    親が未確定、または manifest のプロンプトが使えない:
      - validate 段が error（plan が検証に通らない。前回のプロンプトは古い）
      - プロンプト段が blocked（台帳の素材表に基準/依存の採用行が無いまま生成した。--adopt --canonical は素材表に触れない）
      - プロンプト段が stale（validate エラーで失効）／無い／入力 hash が今の plan・台帳・ツールと合わない（古い）。
    鮮度は oblique_build と同じ導出（oblique_freshness）で今の hash を計算して比べる。"""
    _, miss = status(maps, mid)
    out = []
    if miss:
        out.append(f"親が未確定: {', '.join(miss)}")
    man = manifest_of(mid)
    stages = man.get("stages", {})
    va = stages.get("validate", {})
    if va.get("status") == "error":
        out.append(f"validate エラー（plan が検証に通らない。{len(va.get('errors', []))}件。oblique_build.py の出力を見て台帳を直し、再実行する）")
    pr = stages.get("prompt", {})
    if pr.get("status") == "blocked":
        un = ", ".join(pr.get("unadopted_dependencies", []))
        out.append(f"プロンプトが blocked（再生成が必要。台帳の素材表に未採用の依存: {un}）")
    elif pr.get("status") == "stale":
        out.append("プロンプトが失効（stale。validate エラーで無効にした。oblique_build.py を再実行）")
    elif has_plan(mid) and man:
        base = re.sub(r"-(kids|fire|burnt|wc)$", "", mid)
        variant = mid[len(base) + 1:] or None
        try:
            cur = FR.current_prompt_sha(mid, maps[mid].get("depends_on", []), str(OB / f"{base}-plan.json"), variant)
        except Exception as e:  # 台帳が読めない等は古い扱いにせず理由を出す
            out.append(f"プロンプトの鮮度を判定できない: {e}")
            cur = None
        if cur is not None and pr.get("input_sha") != cur:
            out.append("プロンプトが古い（入力 hash が今の plan・台帳・ツールと合わない。oblique_build.py を再実行）")
    return out


def cmd_list(maps):
    print(f"{'MAP':12} {'depends_on':28} {'確定':4} {'起動可':6} 備考")
    for k in maps:
        deps, _ = status(maps, k)
        bl = blockers(maps, k)
        note = "／".join(bl) if bl else ("plan なし（別ブランチ）" if not has_plan(k) else "")
        print(f"{k:12} {','.join(deps) or '-':28} {'済' if confirmed(k) else '-':4} {'可' if not bl and not confirmed(k) and has_plan(k) else '-':6} {note}")


def cmd_check(maps, mid):
    if mid not in maps:
        sys.exit(f"ERROR: {mid} がグラフに無い")
    errs = validate(maps)
    if errs:
        sys.exit("ERROR: 依存グラフが不正:\n  " + "\n  ".join(errs))
    deps, miss = status(maps, mid)
    bl = blockers(maps, mid)
    if bl:
        tail = "。親は先に確定（採用→--adopt --canonical）し、" if miss else "。"
        print(f"ERROR: {mid} は起動できない。{'／'.join(bl)}{tail}素材表に採用行を入れる・台帳を直すなどして oblique_build.py でプロンプトを再生成してから起動する（--adopt --canonical は素材表に触れない）", file=sys.stderr)
        sys.exit(1)
    print(f"OK: {mid} の親は全て確定済み（{', '.join(deps) or '依存なし'}）")


def cmd_refs(maps, mid):
    for d in maps[mid].get("depends_on", []):
        c = canonical_of(d)
        if c is None:
            sys.exit(f"ERROR: 親 {d} が未確定")
        print(f"{d}={c}")


def cmd_launch(maps, dry):
    errs = validate(maps)
    if errs:
        sys.exit("ERROR: 依存グラフが不正:\n  " + "\n  ".join(errs))
    run = ROOT / ".claude/skills/sit-field-background/tools/oblique_e2_run.sh"
    procs = []
    for k in maps:
        deps, _ = status(maps, k)
        bl = blockers(maps, k)
        if bl:
            if not confirmed(k) and has_plan(k):
                print(f"スキップ {k}: {'／'.join(bl)}")
            continue
        if confirmed(k) or not has_plan(k):
            continue
        print(("[dry-run] " if dry else "起動 ") + f"{k}（親: {', '.join(deps) or 'なし'}）")
        if not dry:
            log = OB / k / "e2-launch.log"
            (OB / k).mkdir(parents=True, exist_ok=True)
            procs.append((k, subprocess.Popen(["bash", str(run), k, "4"], cwd=str(ROOT), stdout=open(log, "w"), stderr=subprocess.STDOUT, start_new_session=True)))
    for k, pr in procs:
        print(f"  {k}: pid {pr.pid}（ログ {OB / k / 'e2-launch.log'}）")


def main():
    maps = load()
    a = sys.argv[1:]
    if not a:
        print(__doc__); return
    c = a[0]
    if c == "list":
        cmd_list(maps)
    elif c == "check":
        cmd_check(maps, a[1])
    elif c == "refs":
        cmd_refs(maps, a[1])
    elif c == "graph":
        errs = validate(maps)
        print("OK: 依存グラフは正しい" if not errs else "\n".join(errs)); sys.exit(1 if errs else 0)
    elif c == "launch":
        cmd_launch(maps, "--dry-run" in a)
    else:
        sys.exit("不明なコマンド: " + c)


if __name__ == "__main__":
    main()
