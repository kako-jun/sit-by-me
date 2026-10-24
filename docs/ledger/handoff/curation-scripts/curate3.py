# -*- coding: utf-8 -*-
"""曲線3: 決定表"""
import json, re, sys
sys.path.insert(0, '<repo>/.claude/skills/sit-field-background/tools')
import ledger_io as L
S = '<scratchpad>/lm/'
D = [json.loads(l) for l in open(S + 'decisions.jsonl')]
drop = {"TRM-03.corridor", "TRM.open-passage", "TRM-03.standing"}
# 修正する決定の内容
FIX = {
 "TRM-03.corridor": dict(content="渡り廊下棟（conn-w/conn-e）の床は木の板張り（石敷きではない）。廊下棟は住居・幼稚園の屋根幅より短くする。造りは屋内の確定画像（TRM-04 採用）と同じ建物行から導出する（→TRM.building-shared）。", tags="floor, layout, must:木の板張り"),
 "TRM.open-passage": dict(content="本堂広間と廊下の境・住居の仕切りなど左右（横方向）に行き来する開口部は、梁・鴨居・垂れ壁・壁を描かず、奥まで見通せる通れる開口にする（TRM-04 広間⇄西・東廊下の境、TRM-05 の仕切り）。廊下棟そのもの（壁・屋根・窓列）は開口ではない（→TRM.building-shared）。", tags="door, wall, must:梁"),
}
FIXMAP = {"TRM-03.corridor": "TRM-03", "TRM.open-passage": "TRM-04, TRM-05"}
TARGET = {  # 対象種別, 対象ID
 "TRM-05.door-back": ("端", "TRM-05.door-back"), "TRM-05.door-back-west": ("端", "TRM-05.door-back"), "TRM-05.door-back-fire": ("端", "TRM-05.door-back"),
 "TRM-05.fossil": ("要素", "rock"), "TRM-05.stone-pos": ("要素", "rock"), "TRM-05.fossil-state": ("要素", "rock"),
 "TRM.hall-no-window": ("建物", "BLD-TRM-honden"), "TRM-03.corridor": ("建物", "BLD-TRM-corridor-w"), "TRM.open-passage": ("建物", "BLD-TRM-corridor-w"),
 "TRM-04.corridor-end-doors": ("建物", "BLD-TRM-corridor-w"), "TRM-04.east-corridor-art": ("建物", "BLD-TRM-corridor-e"),
 "TRM.entrances": ("接続", "TRM-03.door-residence"), "TRM-06.loop": ("接続", "TRM-15.bottom"), "TRM-08.top-closed": ("MAP", "TRM-08"),
 "TRM-03.kindergarten-bigger": ("建物", "BLD-TRM-youchien"), "TRM.windows-spec": ("エリア", "teramachi"),
}
MUST_FALLBACK = {"TRM-03.grounds-roles": "墓地", "TRM.left-right": "左", "TRM-03.standing": "石段", "TRM.era-variants": "同一ID", "TRM-04.floor": "板張り", "TRM-02.floor": "リノリウム"}
def expand(spec):
    out = []
    for tok in [t.strip() for t in spec.split(",")]:
        m = re.match(r"^TRM-(\d\d)\.\.TRM-(\d\d)$", tok)
        if m:
            out += [f"TRM-{n:02d}" for n in range(int(m.group(1)), int(m.group(2)) + 1)]
        else:
            out.append(tok)
    return out
rows = []
for d in D:
    i = d["id"]
    content = FIX.get(i, {}).get("content", d["content"])
    tags = FIX.get(i, {}).get("tags", d["tags"])
    maps = expand(FIXMAP.get(i, d["maps"]))
    tg = [t.strip() for t in tags.split(",")]
    must = [t[5:] for t in tg if t.startswith("must:")]
    forb = [t[7:] for t in tg if t.startswith("forbid:")]
    out = "なし" if "prompt:skip" in tg else "必須"
    if out == "必須" and not must and not forb:
        must = [MUST_FALLBACK.get(i) or d["content"][:6]]; print("fallback", i, must)
    if i.startswith("TRM.") and i not in TARGET:
        kind, tid = "エリア", "teramachi"
    elif i in TARGET:
        kind, tid = TARGET[i]
    else:
        kind, tid = "MAP", i.split(".")[0].split("-")[0] + "-" + i.split(".")[0].split("-")[1]
    status = d["status"]
    repl = ""
    m = re.match(r"訂正済み\(→(.+)\)", status)
    if m:
        status, repl = "訂正済み", m.group(1)
    cats = [t for t in tg if not t.startswith(("must:", "forbid:", "prompt:"))]
    rows.append({"決定ID": i, "日付": d["date"], "対象種別": kind, "対象ID": tid, "対象名": "", "決定の要点": content, "逐語": d["verbatim"],
                 "出典": f"Issue #{d['issue']}", "出典URL": d["url"] or "", "状態": status, "置換先": repl, "プロンプト出力": out,
                 "必須語": ";".join(must), "禁止語": ";".join(forb), "対象MAP": ";".join(maps), "備考": (d.get("note") or "") + (" 分類: " + ",".join(cats) if cats else ""), L.FREE: ""})
def add(id, date, issue, snip, kind, tid, verb, content, maps, out="必須", must="", forb="", status="有効", repl="", note="", cats=""):
    url = ""
    if issue:
        cm = [json.loads(l) for l in open(S + f"c{issue}.jsonl")]
        hit = [c for c in cm if snip in c["body"]]
        assert hit, (id, snip)
        url = hit[0]["url"]
    rows.append({"決定ID": id, "日付": date, "対象種別": kind, "対象ID": tid, "対象名": "", "決定の要点": content, "逐語": verb, "出典": f"Issue #{issue}" if issue else "会話（Issue #144 に記録）",
                 "出典URL": url, "状態": status, "置換先": repl, "プロンプト出力": out, "必須語": must, "禁止語": forb, "対象MAP": ";".join(expand(maps)), "備考": note + (" 分類: " + cats if cats else ""), L.FREE: ""})
add("TRM.building-shared", "2026-10-23", 144, "正規化台帳（DB的）の設計を承認", "建物", "BLD-TRM-corridor-w",
    "「まかせる」（設計案の④外観の渡り廊下棟は屋内の確定画像に合わせる、への回答。推奨どおり）。前提:「1つの建物の情報は共有する（屋内と外観の食い違いを構造的に起こさない）」",
    "1つの建物の情報（外形・屋根・壁・窓列・扉・材質・関係）は建物表の1行を正とし、屋内MAPと外観MAPの両方がそこから導出される。外観の渡り廊下棟は屋内の確定画像（TRM-04 採用）と一致させる: 閉じた壁（外端も閉）・南壁に腰高の連窓3つ・木の板張りの床・灰色の瓦の低い寄棟屋根。柱と屋根だけの開放通路にしない。",
    "TRM-02, TRM-03, TRM-04, TRM-05", must="連窓", forb="柱と屋根だけ", cats="layout, window, wall")
add("TRM-03.corridor-open", "2026-10-23", 144, "左右を行き来する開口部は壁に見えないように", "建物", "BLD-TRM-corridor-w",
    "「渡り廊下など左右を行き来する開口部はちゃんと見えるように梁を消すなど、壁に見えないようにしてね」（再掲）",
    "（誤読。取り消し）渡り廊下棟を柱と屋根だけの開放した通路にする。", "TRM-03", out="なし", status="訂正済み", repl="TRM.building-shared",
    note="kako-jun の指示は『開口部（戸口・仕切りの開口）を壁に見せない』で、廊下棟の壁をなくすことではなかった。屋内の確定画像（TRM-04 採用）は壁と窓列のある廊下。", cats="")
add("TRM-05-fire.upper-half", "2026-10-23", 144, "住居の火事版は上半分だけが燃える", "MAP", "TRM-05",
    "「住居の３パターンの絵も、火事で燃えるのは上半分と伝えてるのに３枚はそうなっていなかった。机の上のみかんがあるのはよかったが、そういう良い点を参考画像で伝えて連鎖させることでほかの絵にももれなく再現できるようにし続ける必要がある」",
    "火事版（TRM-05-fire）は上半分だけが燃える（火の範囲は北側 Y280〜640）。下半分は燃えない。4テイク中3枚が守らず没。生成後は火の色の領域が上半分に限られているかを決定論で測る（参考表示）。",
    "TRM-05-fire", must="上半分だけ", forb="下半分", cats="era, object")
add("TRM.inherit-elements", "2026-10-23", 144, "住居の火事版は上半分だけが燃える", "エリア", "teramachi",
    "（同上）「そういう良い点を参考画像で伝えて連鎖させることでほかの絵にももれなく再現できるようにし続ける必要がある」",
    "採用画像の良い点は『採用要素（継承要素）』として台帳に記録し、次の絵へ（a）確定画像を参考画像に付ける（b）プロンプトに「継承する要素」として明記、の両方で伝える。", "TRM-02..TRM-17", out="なし", cats="process")
add("TRM.ledger-db", "2026-10-23", 144, "正規化台帳（DB的）の設計を承認", "エリア", "teramachi",
    "「まかせる」（設計案 ledger-db-design.md の①形式=CSV／②表にできる部分だけ md を生成ビューにする／③寺町から段階移行／④外観の渡り廊下棟は屋内の確定画像に合わせる、いずれも推奨どおり）。前提:「DBのテーブルのように、エリア・マップ・マップ間の関連・敵・敵1匹ごとの情報が別ファイルで互いに関連し、重複がなく、スキルがそれらから一意にプロンプトを作る。再現性が高いのが狙い」「日本語の情報が元。描画直前のJSONは効率がよければ作り、それもドキュメントとして台帳から管理」",
    "台帳は日本語ヘッダのCSV（docs/ledger/*.csv）が唯一のマスター。plan・decor-pools・connections・dependency-graph は台帳から導出する派生物（入力ハッシュ・再生成コマンド付き、生成物表に登録して鮮度検査）。第1段階は寺町（TRM-02〜17）と建物表。敵・他エリアは第2段階。", "TRM-02..TRM-17", out="なし", cats="process")
add("TRM.required-keys", "2026-10-23", None, "", "エリア", "teramachi",
    "「接続とか工作の材質とか机の材質とか、マップごとエリアごとに必ず指定が必要なものとかは強制できるようにキーを統一するような考え方も入れろ」",
    "エリア・MAP・建物ごとに必須キーを定義し（必須キー表）、欠落・語彙外の値・別名をエラーにする。『指定なし』は空欄でなく明示値（窓なし・該当なし）で書き、空欄は未決として検出する。必須キーが揃わないMAPは生成を起動しない。", "TRM-02..TRM-17", out="なし", cats="process")
add("TRM.free-text", "2026-10-23", None, "", "エリア", "teramachi",
    "「それプラス特徴があれば自由作文できる部分も作ればいいのだ」",
    "各表に必須キーとは別の任意の自由記述欄『特徴(自由記述)』を持たせ、固有の特徴を日本語で自由に書ける。プロンプトの専用節にそのまま入れる。必須キー・禁止語と矛盾する記述、構造化できる内容（寸法・個数・材質）は検証で警告する。", "TRM-02..TRM-17", out="なし", cats="process")
add("TRM.index", "2026-10-23", None, "", "エリア", "teramachi",
    "「エージェントに対する目次みたいなものを作ってもいい。それを見てたどれるよう導線から孤立したものはなくせ。フォルダ、ファイル配置の管理とも合流しろ」",
    "docs/INDEX.md をエージェントの入口にする（表は台帳からの生成ビュー）。リポの追跡ファイルは INDEX から辿れること（孤立ファイルはエラー）。フォルダ・ファイル配置の規則は台帳のファイル配置表に統合する。", "TRM-02..TRM-17", out="なし", cats="process")
L.write("決定", rows)
print(len(rows), "decisions")
