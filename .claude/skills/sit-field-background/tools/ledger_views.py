"""人が読む md ビュー（docs/ledger-views/*.md）を台帳（docs/ledger/*.yaml）から生成・鮮度検査する。

  uv run python3 ledger_views.py build   # docs/ledger-views/*.md を書き直す（余計な .md は消さずエラーにする）
  uv run python3 ledger_views.py check   # 台帳から再生成した内容と一致しなければ exit 1（verify_ledger.rb が実行）

ビューは MAP・建物・決定・未決・採用要素・接続の6つ。手編集禁止（直すのは台帳。編集しても check が失敗する）。
root は環境変数 LEDGER_ROOT で差し替えられる（テスト用）。
"""
import os
import sys

import ledger_io as L

VIEWS = os.path.join(L.REPO, "docs", "ledger-views")
CMD = "uv run python3 .claude/skills/sit-field-background/tools/ledger_views.py"


def cell(s):
    return (s or "").replace("|", "\\|").replace("\r", "").replace("\n", "<br>")


def table(header, rows):
    out = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    out += ["| " + " | ".join(cell(c) for c in r) + " |" for r in rows]
    return out


def head(title, table_names, note=""):
    srcs = "・".join(f"`{t}.yaml`" for t in table_names)
    lines = [f"# {title}", "",
             f"> **生成ビュー（手編集禁止）**。生成元: {srcs}（`docs/ledger/`）。直すのは台帳。再生成: `{CMD} build`（リポ直下）。鮮度検査: `{CMD} check`（`ruby scripts/verify_ledger.rb` に含まれる）。"]
    if note:
        lines.append(f"> {note}")
    return lines + [""]


def quote(text):
    return ["> " + ln if ln else ">" for ln in (text or "").split("\n")]


def view_map():
    maps, ends, open_items = L.read("MAP"), L.read("端"), L.read("未決")
    areas = {a["エリアID"]: a["名称"] for a in L.read("エリア")}
    out = head("MAP 一覧", ["MAP", "端", "未決", "エリア"])
    out += ["MAP 1行=画像1枚（時期違いは同一IDの差し替え）。状態・採用状態・未決は台帳の値そのまま。", ""]
    by_area = {}
    for m in maps:
        by_area.setdefault(m["エリアID"], []).append(m)
    for aid, ms in by_area.items():
        out += [f"## {areas.get(aid, aid)}（{aid}）", ""]
        rows = []
        for m in ms:
            n_open = sum(1 for u in open_items if u["状態"] == "未決" and (u["対象ID"] == m["MAP_ID"] or u["対象ID"].startswith(m["MAP_ID"] + ".")))
            rows.append([m["MAP_ID"], m["名称"], m["時期"], m["屋内外"], m["状態"], m["採用状態"], m["一言特徴"], m["建物ID"], m["依存MAP"], str(n_open)])
        out += table(["MAP", "名称", "時期", "屋内外", "状態", "採用状態", "一言特徴", "建物", "依存MAP", "未決"], rows) + [""]
    out += ["## 端（出入口）", ""]
    rows = [[e["端ID"], e["MAP_ID"], e["適用時期"], e["種別"], e["壁側"], e["幅クラス"], e["状態"], e["相手端"], e["備考"]] for e in ends]
    out += table(["端", "MAP", "適用時期", "種別", "壁側", "幅", "状態", "相手端", "備考"], rows) + [""]
    return "\n".join(out)


def view_building():
    blds, parts, wins = L.read("建物"), L.read("建物部位"), L.read("建物窓列")
    rels, eras = L.read("建物関係"), L.read("建物時期差分")
    out = head("建物", ["建物", "建物部位", "建物窓列", "建物関係", "建物時期差分"], "屋内と外観は同じ建物の行から導出する。")
    for b in blds:
        bid = b["建物ID"]
        out += [f"## {b['名称']}（{bid}）", ""]
        out += table(["項目", "内容"], [[k, b[k]] for k in ("種別", "外形", "屋根", "外壁", "窓列", "扉", "材質", "関係", "状態", "備考", L.FREE) if b.get(k)]) + [""]
        ps = [p for p in parts if p["建物ID"] == bid]
        if ps:
            out += ["### 部位", ""] + table(["部位", "種別", "方角", "状態", "材質", "見た目", "決定"], [[p["部位ID"], p["部位種別"], p["方角"], p["状態"], p["材質"], p["見た目"], p["決定参照"]] for p in ps]) + [""]
        ws = [w for w in wins if w["建物ID"] == bid]
        if ws:
            out += ["### 窓列", ""] + table(["窓列", "部位", "個数", "先頭比", "間隔比", "幅比", "窓台比", "高さ比", "窓種別", "理由", "決定"], [[w["窓列ID"], w["部位ID"], w["個数"], w["先頭比"], w["間隔比"], w["幅比"], w["窓台比"], w["高さ比"], w["窓種別"], w["理由"], w["決定参照"]] for w in ws]) + [""]
        es = [e for e in eras if e["建物ID"] == bid]
        if es:
            out += ["### 時期差分", ""] + table(["時期", "部位", "差分", "内容", "決定"], [[e["時期"], e["部位ID"], e["差分"], e["内容"], e["決定参照"]] for e in es]) + [""]
    rs = rels
    if rs:
        out += ["## 建物どうしの関係", ""] + table(["通番", "建物A", "建物B", "関係", "方角", "接続端", "決定"], [[r["通番"], r["建物A"], r["建物B"], r["関係"], r["方角"], r["接続端ID"], r["決定参照"]] for r in rs]) + [""]
    return "\n".join(out)


def view_decisions():
    ds = L.read("決定")
    out = head("決定", ["決定"], "決定は先に台帳へ書く（Issue は決定IDを参照するだけ）。状態『訂正済み』は置換先を見る。")
    out += ["## 一覧", ""] + table(["決定", "日付", "対象", "状態", "決定の要点"], [[d["決定ID"], d["日付"], f"{d['対象種別']}:{d['対象ID']}", d["状態"], d["決定の要点"]] for d in ds]) + [""]
    out += ["## 逐語と出典", ""]
    for d in ds:
        out += [f"### {d['決定ID']}（{d['日付']}・{d['状態']}）", "", d["決定の要点"], ""]
        if d["逐語"]:
            out += quote(d["逐語"]) + [""]
        meta = [f"出典: {d['出典']}" + (f"（{d['出典URL']}）" if d["出典URL"] else ""), f"プロンプト出力: {d['プロンプト出力']}"]
        if d["置換先"]:
            meta.append(f"置換先: {d['置換先']}")
        if d["必須語"]:
            meta.append(f"必須語: {d['必須語']}")
        if d["禁止語"]:
            meta.append(f"禁止語: {d['禁止語']}")
        if d["対象MAP"]:
            meta.append(f"対象MAP: {d['対象MAP']}")
        out += ["- " + " ／ ".join(meta), ""]
        if d.get(L.FREE):
            out += [f"- 自由記述: {d[L.FREE]}", ""]
    return "\n".join(out)


def view_open():
    us = L.read("未決")
    out = head("未決（要確認）", ["未決"], "発明しない。決まったら決定表に書き、解決決定IDを入れて状態を『解決』にする。")
    for state in ("未決", None):
        sel = [u for u in us if (u["状態"] == "未決") == (state == "未決")]
        out += [f"## {'未決' if state else 'その他（解決済みほか）'}（{len(sel)}件）", ""]
        out += table(["未決", "対象", "キー", "内容", "状態", "解決決定"], [[u["未決ID"], f"{u['対象テーブル']}:{u['対象ID']}", u["キー"], u["内容"], u["状態"], u["解決決定ID"]] for u in sel]) + [""]
    return "\n".join(out)


def view_inherit():
    es = L.read("採用要素")
    out = head("採用要素（継承要素）", ["採用要素"], "採用画像から次の絵へ継承する要素。参考画像とプロンプトの両方で渡る。")
    out += table(["採用要素", "素材", "元MAP", "要素", "内容", "継承先MAP", "継承方法", "状態", "確認語", "決定"], [[e["採用要素ID"], e["素材ID"], e["元MAP"], e["要素"], e["内容"], e["継承先MAP"], e["継承方法"], e["状態"], e["確認語"], e["決定参照"]] for e in es]) + [""]
    return "\n".join(out)


def view_connections():
    cs = L.read("接続")
    ends = {e["端ID"]: e for e in L.read("端")}
    out = head("接続", ["接続", "端"], "端と端のつながり。期待=opposite は反対の辺どうし。図は所属する接続図。")

    def where(eid):
        e = ends.get(eid)
        return f"{eid}（{e['壁側']}）" if e and e["壁側"] else eid
    out += table(["端A", "端B", "種別", "期待", "ラベル", "外部", "無効時期", "図", "主路・状態", "決定"], [[where(c["端A"]), where(c["端B"]), c["種別"], c["期待"], c["ラベル"], c["外部"], c["無効時期"], c["図"], c["主路・状態"], c["決定参照"]] for c in cs]) + [""]
    return "\n".join(out)


FILES = {"MAP.md": view_map, "建物.md": view_building, "決定.md": view_decisions, "未決.md": view_open, "採用要素.md": view_inherit, "接続.md": view_connections}


def expected():
    return {name: fn().rstrip("\n") + "\n" for name, fn in FILES.items()}


def problems():
    exp = expected()
    bad = []
    for name, text in exp.items():
        p = os.path.join(VIEWS, name)
        if not os.path.isfile(p):
            bad.append(f"{name} が無い")
        elif open(p, encoding="utf-8", newline="").read() != text:
            bad.append(f"{name} が台帳と一致しない（古い、または手編集）")
    if os.path.isdir(VIEWS):
        for name in sorted(os.listdir(VIEWS)):
            if name not in exp:
                bad.append(f"{name} は生成ビューではない（docs/ledger-views/ に手書きのファイルを置かない）")
    return bad


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "check"
    if cmd == "build":
        os.makedirs(VIEWS, exist_ok=True)
        for name, text in expected().items():
            with open(os.path.join(VIEWS, name), "w", encoding="utf-8", newline="") as f:
                f.write(text)
        extra = [n for n in os.listdir(VIEWS) if n not in FILES]
        if extra:
            print(f"WARN: 生成ビューではないファイルがある: {extra}", file=sys.stderr)
        print(f"docs/ledger-views/ を更新した（{len(FILES)} ファイル）")
    elif cmd == "check":
        bad = problems()
        if bad:
            print(f"FAIL: docs/ledger-views/ が台帳と一致しない: {'; '.join(bad)}。再生成: {CMD} build")
            sys.exit(1)
        print("PASS: docs/ledger-views/ は台帳と一致")
    else:
        raise SystemExit(f"使い方: {sys.argv[0]} build|check")


if __name__ == "__main__":
    main(sys.argv)
