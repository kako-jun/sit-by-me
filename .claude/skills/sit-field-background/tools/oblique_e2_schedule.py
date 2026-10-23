#!/usr/bin/env python3
"""E2 の生成スケジューラ: 依存グラフ（dependency-graph.json）と各MAPの確定状態から『今起動できるMAP』を出す。

依存関係で直列か並列かを決める（同じ建物・扉・家具・場所を複数枚で描くなら先に確定→参考画像として次へ。共有しないなら並列）。
確定＝manifest.json の adoption.canonical（正本パス）が存在する（`oblique_build.py --adopt IMG --take N --canonical PATH`）。

使い方（リポ直下で。`uv run python3 -I`）:
  oblique_e2_schedule.py list                 全MAPの依存・確定・起動可否
  oblique_e2_schedule.py check MAP            親が全て確定済みか（未確定なら理由を出して終了コード1）
  oblique_e2_schedule.py refs MAP             確定済みの親の正本画像を `PARENT=path` で列挙（参考画像）
  oblique_e2_schedule.py graph                グラフの検証（循環・存在しないID・自己参照・plan との不一致）
  oblique_e2_schedule.py launch [--dry-run]   起動可能で未確定のMAPを並列にバックグラウンド起動（oblique_e2_run.sh MAP 4）
"""
import json, os, re, subprocess, sys
from pathlib import Path

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


def cmd_list(maps):
    print(f"{'MAP':12} {'depends_on':28} {'確定':4} {'起動可':6} 備考")
    for k in maps:
        deps, miss = status(maps, k)
        ok = not miss
        note = ("親が未確定: " + ",".join(miss)) if miss else ("plan なし（別ブランチ）" if not has_plan(k) else "")
        print(f"{k:12} {','.join(deps) or '-':28} {'済' if confirmed(k) else '-':4} {'可' if ok and not confirmed(k) and has_plan(k) else '-':6} {note}")


def cmd_check(maps, mid):
    if mid not in maps:
        sys.exit(f"ERROR: {mid} がグラフに無い")
    errs = validate(maps)
    if errs:
        sys.exit("ERROR: 依存グラフが不正:\n  " + "\n  ".join(errs))
    deps, miss = status(maps, mid)
    if miss:
        print(f"ERROR: {mid} は起動できない。親が未確定: {', '.join(miss)}（依存: {', '.join(deps)}）。先に親を確定（採用→--adopt --canonical）してから", file=sys.stderr)
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
        deps, miss = status(maps, k)
        if miss or confirmed(k) or not has_plan(k):
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
