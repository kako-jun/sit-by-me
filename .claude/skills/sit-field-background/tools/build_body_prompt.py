#!/usr/bin/env python3
"""体内 BDY-01・03・05〜14 の生成用 prompt を、原文行と割付図の画素実測から機械生成する共通ビルダー（装飾込み1回生成 = onepass）。

画像は生成しない。出力は MAP ごとに2ファイル:
  DIR/BDY-xx-prompt.md        来歴・警告・原文束（逐語）・参照一覧・wrapper・本文P1〜・照合表・実測・検査項目
  DIR/BDY-xx-prompt-send.txt  送信文（wrapper + 本文。本文は SOURCE TEXT=原文束（逐語。BDY-04・15・16・17 だけは最後に置く）→ WHAT TO DRAW（構造＋装飾を1回で）→ REFERENCE（2枚: clean 割付図＋材料見本。様式参照画像は使わない）。
                              原文束以外の自作文に内部メモ・TBD・仮案を入れない。Issue は題名・本文と最新の決定コメントの決定部分のみ）

実行（-I で動く。リポのどこからでも）:
  uv run --with pillow --with numpy python3 -I .claude/skills/sit-field-background/tools/build_body_prompt.py BDY-09 --out verification/body-layout/prompts
  ... build_body_prompt.py --all --out verification/body-layout/prompts      # 15枚（BDY-01・03〜08・10〜17。採用済みの BDY-02・09 は含めない）
  ... build_body_prompt.py BDY-02 --force-redo --out verification/body-layout/prompts   # 作り直し（BDY-02・BDY-09 だけ）
  ... build_body_prompt.py --verify-send verification/body-layout/prompts/BDY-09-prompt-send.txt

経緯: 2段階生成（簡素な段階1→装飾の段階2）は廃止（kako-jun 指示 2026-10-22）。装飾込みの1回生成で幾何が崩れたのは様式参照画像が原因という仮説で、
様式参照なし（参照2枚）の構造 prompt に装飾の指示を本文で足した onepass を既定にした。

正本（このコードは読むだけ。原文を要約・補完しない）:
  docs/*.md の対象行（逐語。`[ファイル:行]` の見出し + その行そのまま。--verify-bundle で行番号どおりに再照合できる）
  Issue #142（gh issue view 142。本文とコメント全件を逐語）
  verification/body-layout/clean/BDY-xx.png（割付図の清書版。辺・位置・幅・曲がり・区画数はこの画素から測る）
  body_layout.py（通路の折れ線＝曲がりの位置の元。画素で裏取りし、食い違えば停止する）

形: stub（末端の丸い閉じた端）/ through（辺から辺の斜めの1本）/ knee（折れ点1つ・鈍角35度。BDY-09,12）/ junction（BDY-03 の4本合流）。
BDY-02（広間・首・分岐。専用の本文 build_prompt_hall）と BDY-09 は採用済み（旧プールの装飾）。既定は拒否（採用済み保護）。
作り直しは明示オプション `--force-redo`（kako-jun 2026-10-22『つくりなおせ』。Issue #142）で、新プールの onepass を BDY-02-prompt.* / BDY-09-prompt.* に書く（--all には含めない）。
BDY-04（脳の迷路）・BDY-15（胃のJ字の1袋）・BDY-16（心臓の4部屋）・BDY-17（肺・案Aの外周の環）は、kako-jun が形を決めモック承認済み（Issue #142）。
部屋・迷路の専用の本文（build_prompt_rooms）で作る（clean 画素の実測。迷路は13x6格子の全通路を列挙し、P4 の先頭にステンシル宣言・ランドマークを置く）。送信文の順は wrapper → WHAT TO DRAW → REFERENCE → SOURCE TEXT（この4枚だけ原文束が最後）。別コードの再測定: verification/body-layout/remeasure_body_rooms.py。
"""
import argparse
import math
import hashlib
import random
import importlib.util
import json
import re
import subprocess
import sys
from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]

TARGETS = ["BDY-01", "BDY-02", "BDY-03", "BDY-04", "BDY-05", "BDY-06", "BDY-07", "BDY-08", "BDY-09", "BDY-10", "BDY-11", "BDY-12",
           "BDY-13", "BDY-14", "BDY-15", "BDY-16", "BDY-17"]
ROOM_MAPS = ("BDY-04", "BDY-15", "BDY-16", "BDY-17")  # 部屋・迷路の構造（kako-jun が脳=迷路・胃=J字の1袋・心臓=4部屋・肺=案Aの環を決定・モック承認済み。2026-10-22）
ON_HOLD = {}  # 保留（原文未確定）で拒否するMAP。今は無し（旧: BDY-04/15/16/17。上の決定で解除）
ISSUE = 142
CUT_MARK = re.compile(r" 【BDY-\d+ ")  # docs の採用済みMAP行（BDY-02・BDY-09 など）の末尾の来歴注記。送信しない（それ以前を逐語で送る）

CLEAN_DIR = REPO / "verification/body-layout/clean"
SWATCH = REPO / "verification/body-layout/BDY-material-swatch-corrugated-edge.png"
DOCS = {k: REPO / v for k, v in {
    "registry": "docs/map-asset-registry.md", "spec": "docs/map-specifications.md", "topology": "docs/map-topology.md",
    "checklist": "docs/map-contract-checklist.md", "art": "docs/art-direction.md",
    "research": "docs/map-reference-research.md", "decisions": "docs/decisions.md"}.items()}

# ---- 割付図の色（body_layout.py --clean と同じ値）----
C_DESK, C_BAND, C_TERRAIN, C_FLOOR, C_WALL = (118, 120, 126), (150, 110, 62), (170, 130, 110), (232, 201, 168), (92, 104, 128)
W, H = 1920, 1080
SLIVER_NARROW = 80  # 細い帯と見なす幅(px)。通路幅230pxより十分細いもの
EDGE_DEPTH = 2  # 縁の床区間を測る深さ(px)。BDY-02 以外
W2, H2 = 1672, 941  # 1920x1080 が返らないときの許容寸法（×0.871）

LABEL = {  # 台帳の一言特徴（registry/spec の逐語から取れるものはそちらが正本。ここは英語prompt用の名前）
    "BDY-01": "the mouth (口・体内入口), the entrance of the imaginary human body",
    "BDY-02": "the upper torso (上半身・胴体上段)",
    "BDY-03": "the lower torso (下半身・胴体下段) of the imaginary human body",
    "BDY-05": "the left arm, first passage, root side (左手通路1・付け根側)",
    "BDY-06": "the left arm, second passage, tip end (左手通路2・末端)",
    "BDY-07": "the right arm, first passage, root side (右手通路1・付け根側)",
    "BDY-08": "the right arm, second passage, tip end (右手通路2・末端)",
    "BDY-09": "the left leg, first passage, root side (左足通路1・付け根側)",
    "BDY-10": "the left leg, second passage, middle (左足通路2)",
    "BDY-11": "the left leg, third passage, tip end (左足通路3・末端)",
    "BDY-12": "the right leg, first passage, root side (右足通路1・付け根側)",
    "BDY-13": "the right leg, second passage, middle (右足通路2)",
    "BDY-14": "the right leg, third passage, tip end (右足通路3・末端)",
    "BDY-04": "a maze of narrow one-person-wide passages",
    "BDY-15": "one single J-shaped pouch",
    "BDY-16": "four round rooms joined in a square ring",
    "BDY-17": "five round rooms joined in a ring with one entrance",
}
ROLE = {  # (MAP, port) -> 通路の役割（英語。相手MAP名は出さず役割で呼ぶ）
    ("BDY-01", "door-passage-torso"): "the neck passage (leading on toward the torso)",
    ("BDY-03", "door-passage-upper"): "the upper-body passage (leading back up to the upper torso)",
    ("BDY-03", "door-passage-left-leg"): "the left-leg passage",
    ("BDY-03", "door-passage-right-leg"): "the right-leg passage",
    ("BDY-03", "door-passage-stomach"): "the side-chamber passage (leading on toward a side chamber)",
    ("BDY-05", "door-passage-torso"): "the torso-side passage (leading back toward the upper torso)",
    ("BDY-05", "door-passage-tip"): "the arm-tip passage (leading on toward the hand end)",
    ("BDY-06", "door-passage-base"): "the arm-root passage (leading back toward the root of the arm)",
    ("BDY-07", "door-passage-torso"): "the torso-side passage (leading back toward the upper torso)",
    ("BDY-07", "door-passage-tip"): "the arm-tip passage (leading on toward the hand end)",
    ("BDY-08", "door-passage-base"): "the arm-root passage (leading back toward the root of the arm)",
    ("BDY-09", "door-passage-torso"): "the torso-side passage (leading back toward the lower torso)",
    ("BDY-09", "door-passage-middle"): "the passage leading on down the leg",
    ("BDY-10", "door-passage-base"): "the leg-root passage (leading back up the leg)",
    ("BDY-10", "door-passage-tip"): "the passage leading on down the leg toward the foot",
    ("BDY-11", "door-passage-base"): "the leg-root passage (leading back up the leg)",
    ("BDY-12", "door-passage-torso"): "the torso-side passage (leading back toward the lower torso)",
    ("BDY-12", "door-passage-middle"): "the passage leading on down the leg",
    ("BDY-13", "door-passage-base"): "the leg-root passage (leading back up the leg)",
    ("BDY-13", "door-passage-tip"): "the passage leading on down the leg toward the foot",
    ("BDY-14", "door-passage-base"): "the leg-root passage (leading back up the leg)",
}
ROLE.update({
    ("BDY-02", "door-passage-head"): "the head passage",
    ("BDY-02", "door-passage-mouth"): "the mouth passage",
    ("BDY-02", "door-passage-left-arm"): "the left-arm passage (the person's own left arm)",
    ("BDY-02", "door-passage-right-arm"): "the right-arm passage (the person's own right arm)",
    ("BDY-02", "door-passage-lung"): "the lung passage",
    ("BDY-02", "door-passage-heart"): "the heart passage",
    ("BDY-02", "door-passage-lower"): "the lower-body passage",
    ("BDY-04", "door-passage-torso"): "the entrance passage (leading back down toward the upper torso)",
    ("BDY-15", "door-passage-torso"): "the entrance passage (leading back toward the lower torso)",
    ("BDY-16", "door-passage-torso"): "the entrance passage (leading back toward the upper torso)",
    ("BDY-17", "door-passage-torso"): "the entrance passage (leading back toward the upper torso)",
})
SIDE_EN = {"N": "North edge (top", "S": "South edge (bottom", "W": "West edge (left", "E": "East edge (right"}
NUM_EN = {1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five"}
NUM_en = {k: v.lower() for k, v in NUM_EN.items()}


def die(msg, code=2):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


# ---------------------------------------------------------------- body_layout の読み込み（-I でも動くよう importlib）
def load_layout():
    spec = importlib.util.spec_from_file_location("body_layout", HERE / "body_layout.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------- 原文束（逐語。行番号つき）
class Bundle:
    """`[ファイル:行]` の見出し + その行そのまま、の並び。--verify-bundle で再照合できる。"""

    def __init__(self):
        self.parts = []  # (kind, ...)
        self.lines = {}  # key -> list[str]
        self.seen = set()

    def note(self, text):
        self.parts.append(("note", text))

    def line(self, key, n):
        if (key, n) in self.seen:
            return
        self.seen.add((key, n))
        t = self.lines[key][n - 1]
        if CUT_MARK.search(t):  # 来歴注記は送信しない（前半だけを逐語で送る）
            t = CUT_MARK.split(t)[0]
        self.parts.append(("line", key, n, t))

    def text(self):
        out = []
        for p in self.parts:
            if p[0] == "note":
                out.append(p[1])
            elif p[0] == "line":
                out.append(f"[{DOCS[p[1]].relative_to(REPO)}:{p[2]}]\n{p[3]}")
            else:
                out.append(p[1])
        return "\n".join(out) + "\n"


def run_gh(args):
    r = subprocess.run(["gh", "issue", "view", str(ISSUE)] + args, capture_output=True, text=True, cwd=REPO)
    if r.returncode != 0:
        die(f"gh issue view {ISSUE} {' '.join(args)} が失敗: {r.stderr.strip()[:200]}")
    return r.stdout


def find_line(lines, startswith, after=0):
    hits = [i + 1 for i, l in enumerate(lines) if i + 1 > after and l.startswith(startswith)]
    if not hits:
        die(f"原文行が見つからない: {startswith!r}")
    return hits[0]


def next_nonempty(lines, n, count):
    out, i = [], n
    while len(out) < count and i < len(lines):
        i += 1
        if lines[i - 1].strip():
            out.append(i)
    return out


def table_header(lines, n):
    """表の行 n の直前の見出し行（`| ID |` / `| MAP |`）とその下の区切り行の行番号。"""
    for i in range(n - 1, 0, -1):
        if re.match(r"^\|\s*(ID|MAP)\s*\|", lines[i - 1]):
            return [i, i + 1]
    die(f"表見出しが見つからない: 行{n}")


def row_of(lines, mid, label):
    hits = [i + 1 for i, l in enumerate(lines) if re.match(rf"^\|\s*{mid}\s*\|", l)]
    if len(hits) != 1:
        die(f"{label}: {mid} の行が {len(hits)} 件（1件でなければ停止）")
    return hits[0]


def neighbours(topo_lines, mid):
    pat = re.compile(r"^\|\s*(\S+)\s*\|\s*(\S+)\s*\|\s*(door|event|oneway|pending)\s*\|")
    rows, nb = [], []
    for i, l in enumerate(topo_lines):
        m = pat.match(l)
        if not m:
            continue
        a, b = m.group(1), m.group(2)
        if a.startswith(mid + ".") or b.startswith(mid + "."):
            rows.append((i + 1, a, b, m.group(3)))
            for x in (a, b):
                if x.startswith("BDY-") and not x.startswith(mid + "."):
                    nb.append(x.split(".")[0])
    return rows, sorted(set(nb))


# BDY-02 の原文束に入れる Issue #142 の決定行（コメントの見出し行 -> そのコメント内で逐語に抜粋する行の前方一致）。時系列順。
# 入れない行: 旧形（7本が丸い広間に接する・旧い辺割付）、台座の語を含む行、作業メモ（これからやること）、他MAPの影響の列挙。
BDY02_PICKS = [
    ("## kako-jun 決定（2026-10-22「推奨で」）", ["BDY-02 の以下を", "1. 口の辺 = 北辺", "5. 赤い折り紙"]),
    ("## kako-jun 決定（2026-10-22、BDY-02 v1 を見て）", ["1. 「模型の縁まででいい"]),
    ("## kako-jun 決定（2026-10-22）: 首は A案", ["「A」— 首は BDY-02 の内部で1本"]),
    ("## kako-jun 決定（2026-10-22）: 左右は身体の本人から見る", ["「左右の考え方は", "- 左右は**本人から見た**左右"]),
    ("## kako-jun 決定（2026-10-22、モック一覧と接続表を見て）", ["「心臓は自然にすればいい", "1. 心臓:", "3. 首:"]),
]


# BDY-04（脳の迷路）・15（胃）・16（心臓）・17（肺）の原文束に入れる Issue #142 の決定行（BDY02_PICKS と同じ書式）。時系列順。
# 入れない行: 『花・雲』『台座』など人体と無関係なモチーフ・台座の語を含む行、破棄された旧モック（胃を分岐にした旧承認）、作業メモ（これからやること）、
# 他MAPの影響の列挙、承認時点のハッシュ表。決定コメントの『現行の櫛型より複雑に』は旧モックとの比較だが、決定（1人幅・もっと複雑に）の行として逐語で入れる。
_H_0734 = "## kako-jun 決定・指摘（2026-10-22、モック一覧を見て）"
_H_0808A = "## kako-jun 指示（2026-10-22、モック一覧を見て）: 肺"
_H_0808B = "## kako-jun 指示（2026-10-22、モック一覧を見て・続き）"
_H_0818 = "## kako-jun 決定（2026-10-22）: 左右は身体の本人から見る"
_H_0833 = "## kako-jun 決定（2026-10-22、モック一覧と接続表を見て）"
_H_1126 = "## kako-jun 承認（2026-10-22）: BDY-15（胃）の作り直しモック"
_LR = [_H_0818, ["「左右の考え方は", "- 左右は**本人から見た**左右", "- 部屋名（右心房＝画面左"]]
ROOM_PICKS = {
    "BDY-04": [(_H_0734, ["4. **脳・心臓・肺など**"])],  # 『…現行の櫛型（曲がり4・T字4・行き止まり5）より複雑にする』の決定行は送らない（旧モックとの比較で、迷路の形の根拠でない。1人幅77pxは [注記] が担う）
    "BDY-15": [(_H_0734, ["4. **脳・心臓・肺など**"]), (_H_1126, ["「よい」— 胃を"])],
    "BDY-16": [(_H_0734, ["4. **脳・心臓・肺など**"]), tuple(_LR), (_H_0833, ["「心臓は自然にすればいい", "1. 心臓:"])],
    "BDY-17": [(_H_0734, ["4. **脳・心臓・肺など**"]), (_H_0808A, ["「肺は左右の中心に上から入るように", "→ BDY-17 の入口は北辺"]), tuple(_LR),
               (_H_0833, ["「心臓は自然にすればいい", "2. 肺（BDY-17）:"])],
}


def bdy02_issue_decisions(comments, picks=None, note_for="BDY-02"):
    """BDY-02（picks 指定で他MAP）に関わる決定行を、各コメントから原文のまま抜粋する。見つからなければ停止。戻り値=(逐語の本文, 見出し注記)。"""
    out = []
    for head, prefixes in (BDY02_PICKS if picks is None else picks):
        cs = [c["body"] for c in comments if c["body"].split("\n")[0] == head]
        if len(cs) != 1:
            die(f"Issue #{ISSUE} に決定コメント {head!r} が {len(cs)} 件（1件でなければ停止）")
        lines = cs[0].split("\n")
        got = [head]
        for pf in prefixes:
            hit = [l for l in lines if l.startswith(pf)]
            if len(hit) != 1:
                die(f"決定コメント {head!r} に行 {pf!r} が {len(hit)} 件（1件でなければ停止）")
            got.append(hit[0])
        out.append("\n".join(got))
    return "\n\n".join(out), (f"[Issue #{ISSUE} 決定コメント（時系列順。各コメントの見出しと、{note_for} に関わる決定の行だけを逐語で抜粋。"
                              "相互に食い違う場合は、より後のコメントが優先）]")


def build_bundle(mid, lw):
    bd = Bundle()
    for k, p in DOCS.items():
        bd.lines[k] = p.read_text(encoding="utf-8").split("\n")
    L = bd.lines
    bd.note("(This block is a specification, not text to be drawn. No letter, number or word from it may appear in the picture. Lines about other maps are context only: draw only this one map.)")
    # --- Issue #142: 題名・本文は全文逐語。コメントは『最新の決定コメント』の決定部分だけ逐語（旧コメント・BDY-02固有の決定・作業メモは収録しない）
    title = run_gh(["--json", "title", "--jq", ".title"]).rstrip("\n")
    body = run_gh(["--json", "body", "--jq", ".body"]).rstrip("\n")
    comments = json.loads(run_gh(["--json", "comments"]))["comments"]
    if mid == "BDY-02":
        dec, head_note = bdy02_issue_decisions(comments)
    elif mid in ROOM_PICKS:
        dec, head_note = bdy02_issue_decisions(comments, ROOM_PICKS[mid], mid)
    else:
        latest = [c["body"] for c in comments if c["body"].startswith("## kako-jun 決定（")][-1]
        dec = []
        for l in latest.split("\n"):
            if l.startswith("## これからやること"):  # 作業メモは送信文に入れない
                break
            if "広間" in l:  # 広間の決定は BDY-02 固有。広間の無いMAPには持ち込まない（hall の有る割付図は measure/build_prompt が拒否する）
                continue
            dec.append(l)
        dec = "\n".join(dec).rstrip("\n")
        head_note = f"[Issue #{ISSUE} 最新の決定コメント（逐語）]"
    bd.note(f"[Issue #{ISSUE} 全文（gh issue view {ISSUE} --json title,body。1行目=タイトル、以降=本文、逐語）]\n{title}\n{body}")
    bd.note("[優先規則] 最新のコメントが、それより前のコメントに優先する。\n"
            f"{head_note}\n{dec}")
    bd.issue_lines = set(title.split("\n")) | set(body.split("\n")) | set(dec.split("\n"))
    # --- topology 冒頭規則
    n = find_line(L["topology"], "以下は接続の向きを一意にする正本である")
    bd.line("topology", n)
    # --- 対象MAPの行（registry / spec / checklist / topology）
    rows = {}
    for key in ("registry", "spec", "checklist"):
        r = row_of(L[key], mid, key)
        rows[key] = r
        for h in table_header(L[key], r):
            bd.line(key, h)
        bd.line(key, r)
    trows, nbs = neighbours(L["topology"], mid)
    for r, *_ in trows:
        bd.line("topology", r)
    bd.rows, bd.topo_rows, bd.neighbours = rows, trows, nbs
    # --- 体内の現行空間設計・art-direction・研究・decisions
    # BDY-04（迷路）は slim: 他MAPの記述を含む長い行（topology 690・692）・別MAPの話（decisions 体内入口・topology/research の17MAP表）は載せない
    slim = mid == "BDY-04"
    h = find_line(L["topology"], "## 体内の現行空間設計")
    for n in ([] if slim else [h] + next_nonempty(L["topology"], h, 3)):  # slim（BDY-04）は手足・他MAPの記述が主の節なので載せない（BDY-04 の接続行は上の対象行で逐語）
        bd.line("topology", n)
    h = find_line(L["art"], "## #74 体内の最新空間・色の契約")
    sec_end = next((i + 1 for i in range(h, len(L["art"])) if L["art"][i].startswith("## ")), len(L["art"]) + 1)  # 次の見出しの前まで（節に段落が増えても取りこぼさない）
    for n in [h] + [n_ for n_ in next_nonempty(L["art"], h, 8) if n_ < sec_end]:
        if slim and L["art"][n - 1].startswith("**左右は身体の本人から見る"):  # 左右の規約は迷路（左右の無い1MAP）に無関係
            continue
        bd.line("art", n)
    bd.line("art", find_line(L["art"], "- 背景はタイルを無限に継ぎ足さない"))
    bd.line("research", find_line(L["research"], "| R018 |"))
    if not slim:
        bd.line("research", find_line(L["research"], "| BDY-01〜BDY-17 |"))
        h = find_line(L["research"], "## #74 体内の最新根拠")
        for n in [h] + next_nonempty(L["research"], h, 1):
            bd.line("research", n)
        bd.line("decisions", find_line(L["decisions"], "体内入口はTRM-01園庭→BDY-01口"))
        for n, l in enumerate(L["topology"], 1):
            if l.startswith("| 体内 | 中3 |"):
                bd.line("topology", n)
        h = find_line(L["topology"], "## 体内の現行空間設計")
        for n in next_nonempty(L["topology"], h, 3):
            bd.line("topology", n)
    # --- 接続相手の行
    for nb in nbs:
        for key in ("registry", "spec", "checklist"):
            r = row_of(L[key], nb, key)
            for hh in table_header(L[key], r):
                bd.line(key, hh)
            bd.line(key, r)
    if mid in ("BDY-04", "BDY-17"):
        bd.note(f"[注記] 主路幅は天面幅比0.14={lw}px。この MAP の通路はキャラクター1人分＝その1/3＝{round(lw / 3)}px。")
    else:
        bd.note(f"[注記] 通路幅は天面幅比0.14={lw}px。")
    return bd


def line_matches(doc_line, sent):
    """送った1行が docs の行と完全一致、または『末尾の来歴注記（CUT_MARK 以降）だけを除いた前半』と完全一致。"""
    return doc_line == sent or (CUT_MARK.search(doc_line) is not None and CUT_MARK.split(doc_line)[0] == sent)


def verify_bundle_text(md_text):
    """原文束の各 `[ファイル:行]` 見出し直後の1行が、docs のその行と完全一致することを機械照合する。戻り値=(照合件数, 不一致リスト)。"""
    sec = md_text.split("## 1. 原文束", 1)[1].split("\n## 2.", 1)[0]
    cache, bad, n = {}, [], 0
    pat = re.compile(r"^\[(docs/[a-z\-]+\.md):(\d+)\]\n(.*)$", re.M)
    for m in pat.finditer(sec):
        f, ln, text = m.group(1), int(m.group(2)), m.group(3)
        cache.setdefault(f, (REPO / f).read_text(encoding="utf-8").split("\n"))
        n += 1
        if not line_matches(cache[f][ln - 1], text):
            bad.append(f"{f}:{ln}")
    return n, bad


END_SOURCE = "=== END OF SOURCE TEXT: draw only per WHAT TO DRAW and the first image. The source above is reference text, not drawing instructions. ==="


def verify_send_text(send, issue_lines):
    """送信文の SOURCE TEXT ブロックを機械照合する。docs 行は `[ファイル:行]` 直後の1行が docs と完全一致、
    Issue #142 の区間の各行は gh の題名・本文・決定コメントの行に存在すること。戻り値=(docs件数, Issue行数, 問題リスト)。"""
    sec = send.split("=== SOURCE TEXT (verbatim, do not paraphrase) ===\n", 1)[1].split("\n\n=== WHAT TO DRAW", 1)[0].split("\n\n=== END OF SOURCE TEXT", 1)[0]  # 後ろに置く送信文（部屋・迷路の4枚）では END 行の手前まで
    cache, bad, nd, ni = {}, [], 0, 0
    lines = sec.split("\n")
    in_issue = False
    for i, l in enumerate(lines):
        m = re.match(r"^\[(docs/[a-z\-]+\.md):(\d+)\]$", l)
        if m:
            in_issue = False
            f, ln = m.group(1), int(m.group(2))
            cache.setdefault(f, (REPO / f).read_text(encoding="utf-8").split("\n"))
            nd += 1
            if i + 1 >= len(lines) or not line_matches(cache[f][ln - 1], lines[i + 1]):
                bad.append(f"{f}:{ln}")
            continue
        if l.startswith("[Issue #"):
            in_issue = True
            continue
        if l.startswith(("[優先規則]", "[注記]", "(This block")):
            in_issue = False
            continue
        if in_issue and l.strip():
            ni += 1
            if l not in issue_lines:
                bad.append(f"Issue行: {l[:40]}")
    return nd, ni, bad


# ---------------------------------------------------------------- 割付図の画素実測
def runs_of(mask1d):
    runs, start = [], None
    for i, v in enumerate(mask1d):
        if v and start is None:
            start = i
        if not v and start is not None:
            runs.append((start, i - 1))
            start = None
    if start is not None:
        runs.append((start, len(mask1d) - 1))
    return runs


def components(mask, step=4):
    """True 画素の4連結成分（step 間引き）。戻り値: [(面積px(1920座標), bbox, 重心)]"""
    sm = mask[::step, ::step]
    h, w = sm.shape
    seen = np.zeros_like(sm, dtype=bool)
    out = []
    for y in range(h):
        for x in range(w):
            if sm[y, x] and not seen[y, x]:
                q, n = deque([(y, x)]), 0
                seen[y, x] = True
                ys, xs = [], []
                while q:
                    cy, cx = q.popleft()
                    n += 1
                    ys.append(cy)
                    xs.append(cx)
                    for ny, nx in ((cy + 1, cx), (cy - 1, cx), (cy, cx + 1), (cy, cx - 1)):
                        if 0 <= ny < h and 0 <= nx < w and sm[ny, nx] and not seen[ny, nx]:
                            seen[ny, nx] = True
                            q.append((ny, nx))
                out.append((n * step * step, (min(xs) * step, min(ys) * step, max(xs) * step, max(ys) * step),
                            (float(np.mean(xs)) * step, float(np.mean(ys)) * step)))
    return sorted(out, key=lambda c: -c[0])


def region_name(cx, cy, mx0, my0, mx1, my1):
    fx, fy = (cx - mx0) / (mx1 - mx0), (cy - my0) / (my1 - my0)
    v = "upper" if fy < 1 / 3 else ("lower" if fy > 2 / 3 else "middle")
    h = "left" if fx < 1 / 3 else ("right" if fx > 2 / 3 else "centre")
    return f"{v} {h}" if not (v == "middle" and h == "centre") else "central"


def sx(x):
    return round(x * W2 / W)


def sy(y):
    return round(y * H2 / H)


def poly_by_port(mid, portals, bl):
    """BDY-02 以外: port -> 折れ線（先頭=模型の縁の点）。body_layout の SPECS を px 絶対座標に解決したもの。"""
    out = {}
    for pa, (kind, pts, isp) in zip(bl.SPECS[mid]["paths"], bl.resolve_paths(mid, portals)):
        for i in (0, len(pts) - 1):
            if isp[i]:
                out[pa["pts"][i]] = list(pts) if i == 0 else list(reversed(pts))
    return out


def measure(mid, bl):
    """clean 割付図の画素実測と、body_layout の折れ線（曲がりの位置）。食い違いは停止。"""
    path = CLEAN_DIR / f"{mid}.png"
    if not path.exists():
        die(f"割付図が無い: {path}")
    im = Image.open(path).convert("RGB")
    if im.size != (W, H):
        die(f"{path} が {im.size}（1920x1080 でない）")
    a = np.asarray(im)
    cols = {tuple(c) for c in np.unique(a.reshape(-1, 3), axis=0)}
    allowed = {C_DESK, C_BAND, C_TERRAIN, C_FLOOR, C_WALL}
    if not cols <= allowed:
        die(f"{mid}: 割付図に想定外の色 {sorted(cols - allowed)}（清書版でない）")
    isc = lambda c: np.all(a == np.array(c), axis=2)
    floor, wall, terr = isc(C_FLOOR), isc(C_WALL), isc(C_TERRAIN)
    M = dict(mx0=bl.MX0, my0=bl.MY0, mx1=bl.MX1, my1=bl.MY1, desk=bl.DESK_M, band=bl.BAND,
             foam=bl.BAND_FOAM, corr=bl.BAND_CORR)
    # 構図: 机90・帯48・天面
    d, b = M["desk"], M["band"]
    if not (np.all(a[:d] == C_DESK) and np.all(a[-d:] == C_DESK) and np.all(a[:, :d] == C_DESK) and np.all(a[:, -d:] == C_DESK)):
        die(f"{mid}: 机の余白が {d}px でない")
    if not (tuple(a[d, d]) == C_BAND and tuple(a[M["my0"] - 1, W // 2 + 700]) == C_BAND):
        die(f"{mid}: 土台縁の帯が想定位置にない")
    # 模型の外に床がない
    outside = floor.copy()
    outside[M["my0"]:M["my1"], M["mx0"]:M["mx1"]] = False
    if outside.any():
        die(f"{mid}: 模型の外に床色が {int(outside.sum())} 画素")
    # 辺ごとの床の連続区間。BDY-02 は模型の縁の行/列そのもの。他は縁から2px内側（斜めの帯・折れ線の縁との交わり。body_layout.expected_runs と同じ深さ）。
    # 『縁と40px内側の区間が一致』は、帯が辺に垂直だった頃の検査で、斜めの帯・折れ線では内側で区間が動くのが正しいので撤去した。
    # 縁の区間は接続表（body_layout の期待値）と突き合わせ、斜めの内側の幾何は measure_diag の画素再測定で照合する。
    dep = 0 if mid == "BDY-02" else EDGE_DEPTH
    edges = {}
    for s in "NSWE":
        at = {"N": floor[M["my0"] + dep, :], "S": floor[M["my1"] - 1 - dep, :],
              "W": floor[:, M["mx0"] + dep], "E": floor[:, M["mx1"] - 1 - dep]}[s]
        edges[s] = runs_of(at)
    # 接続表（body_layout）との突き合わせ
    rows, ev, nodes, svg_edges, portals = bl.build_model()
    ports = portals[mid]
    lw = int(round(bl.DEFAULT_MAIN_WIDTH_RATIO * bl.MW))
    if mid == "BDY-02":
        cor = bl.corridors(mid, ports)
    else:
        cor = poly_by_port(mid, portals, bl)
        want_runs, _ = bl.expected_runs(mid, portals, lw)
    per_edge = {}
    for s in "NSWE":
        ps = sorted([p for p in ports if ports[p]["side"] == s], key=lambda p: ports[p]["slot"])
        if len(ps) != len(edges[s]):
            die(f"{mid}: {s}辺 画素の床区間{len(edges[s])}本 != 接続表{len(ps)}本")
        per_edge[s] = []
        o = M["mx0"] if s in "NS" else M["my0"]
        span = bl.MW if s in "NS" else bl.MH
        wants = sorted(want_runs[s]) if mid != "BDY-02" else None
        for i, (p, (r0, r1)) in enumerate(zip(ps, edges[s])):
            if mid == "BDY-02":
                want, wlw = o + ports[p]["slot"] * span, lw
            else:
                want, wlw = wants[i]
            if abs((r0 + r1) / 2 - want) > 3 or abs((r1 - r0 + 1) - wlw) > 3:
                die(f"{mid}: {s}辺 {p} 画素{r0}-{r1} が接続表の帯 中心{want:.0f} 幅{wlw:.0f} と不一致")
            per_edge[s].append(dict(port=p, a=r0, b=r1, w=r1 - r0 + 1, other=ports[p]["other"],
                                    other_port=ports[p]["other_port"], role=ROLE[(mid, p)], poly=cor[p]))
    # 折れ線の整合: 各折れ線に沿って床であること（曲がりの位置の裏取り）
    for s in "NSWE":
        for e in per_edge[s]:
            pts = e["poly"]
            for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
                n = max(2, int(max(abs(x1 - x0), abs(y1 - y0)) // 8))
                for i in range(n + 1):
                    x = round(x0 + (x1 - x0) * i / n)
                    y = round(y0 + (y1 - y0) * i / n)
                    x, y = min(max(x, M['mx0']), M['mx1'] - 1), min(max(y, M['my0']), M['my1'] - 1)
                    if not floor[y, x]:
                        die(f"{mid}: {e['port']} の折れ線 ({x},{y}) が床でない（曲がりの位置が画素と不一致）")
    # 広間: 壁色の画素があるか（割付図に広間が描かれているか）
    hall = bool(wall.any())
    # 区画: 地形の連結成分
    comps = components(terr)
    regions = []
    for area, bbox, (cx, cy) in comps:
        regions.append(dict(area=area, bbox=bbox, name=region_name(cx, cy, M["mx0"], M["my0"], M["mx1"], M["my1"]),
                            wide=area >= 20000))
    return dict(M=M, lw=lw, edges=per_edge, hall=hall, regions=regions, floor=floor, terr=terr, cor=cor, ports=ports,
                hub=(round(M["mx0"] + bl.HUB.get(mid, (.5, .5))[0] * bl.MW), round(M["my0"] + bl.HUB.get(mid, (.5, .5))[1] * bl.MH)))


# ---------------------------------------------------------------- 経路の言葉
def merge_collinear(pts):
    out = [pts[0]]
    for p in pts[1:]:
        if abs(p[0] - out[-1][0]) < 1e-6 and abs(p[1] - out[-1][1]) < 1e-6:
            continue
        out.append(p)
    res = [out[0]]
    for i in range(1, len(out) - 1):
        a, b, c = res[-1], out[i], out[i + 1]
        cross = (b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0])
        if abs(cross) > 1e-6:
            res.append(b)
    res.append(out[-1])
    return res


def seg_words(a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    if abs(dx) < 1:
        return f"straight {'down' if dy > 0 else 'up'}", "y", round(b[1])
    if abs(dy) < 1:
        return f"straight {'right' if dx > 0 else 'left'}", "x", round(b[0])
    return f"sloping {'down' if dy > 0 else 'up'} and to the {'right' if dx > 0 else 'left'}", None, None


def path_text(poly, hub):
    pts = merge_collinear(poly)
    segs = list(zip(pts, pts[1:]))
    parts = []
    for i, (a, b) in enumerate(segs):
        w, ax, v = seg_words(a, b)
        last = i == len(segs) - 1
        if last:
            parts.append(f"{w} toward the middle of the model" if ax is None else f"{w} to the middle of the model")
        else:
            parts.append(f"{w} to about {ax} {v} (in 1672x941: {ax} {(sx if ax == 'x' else sy)(v)})" if ax else f"{w}")
    if len(parts) == 1:
        return f"running {parts[0]}"
    return "running " + ", then ".join(parts)


def rng(axis, r0, r1, base=(0, 0)):
    """1920座標の範囲と 1672x941 座標の範囲。"""
    lo, hi = r0, r1
    f = sx if axis == "x" else sy
    return f"{axis} {lo} to {hi} (in 1672x941: {axis} {f(lo)} to {f(hi)})"


# ---------------------------------------------------------------- 本文（P1〜）
def classify(mid, m):
    es = [(s, e) for s in "NSWE" for e in m["edges"][s]]
    n = len(es)
    sides = [s for s, _ in es]
    if n == 1:
        return "stub"
    if n == 2:
        return "straight" if {sides[0], sides[1]} in ({"N", "S"}, {"W", "E"}) else "bend"
    return "junction"


def tip_of_stub(m, mid):
    """行き止まりの先端: 床画素を通路の軸に沿って縁から辿り、最も奥の床座標を測る。"""
    s, e = next((s, e) for s in "NSWE" for e in m["edges"][s])
    f, M = m["floor"], m["M"]
    c = (e["a"] + e["b"]) // 2
    if s == "N":
        y = M["my0"]
        while f[y + 1, c]:
            y += 1
        return s, ("y", y, c)
    if s == "S":
        y = M["my1"] - 1
        while f[y - 1, c]:
            y -= 1
        return s, ("y", y, c)
    if s == "W":
        x = M["mx0"]
        while f[c, x + 1]:
            x += 1
        return s, ("x", x, c)
    x = M["mx1"] - 1
    while f[c, x - 1]:
        x -= 1
    return s, ("x", x, c)


def sliver_info(m):
    """同じ辺に床区間が2本以上あるとき、その間の地形の細い帯の幅と、辺から内側へ伸びる先端位置。"""
    out = []
    f, M = m["floor"], m["M"]
    for s in "NSWE":
        es = m["edges"][s]
        for e1, e2 in zip(es, es[1:]):
            gap0, gap1 = e1["b"] + 1, e2["a"] - 1
            mid = (gap0 + gap1) // 2
            if s in "NS":
                x = mid
                ys = range(M["my0"], M["my1"]) if s == "N" else range(M["my1"] - 1, M["my0"] - 1, -1)
                depth = 0
                for y in ys:
                    if f[y, x]:
                        break
                    depth += 1
                out.append((s, gap1 - gap0 + 1, depth))
            else:
                y = mid
                xs = range(M["mx0"], M["mx1"]) if s == "W" else range(M["mx1"] - 1, M["mx0"] - 1, -1)
                depth = 0
                for xx in xs:
                    if f[y, xx]:
                        break
                    depth += 1
                out.append((s, gap1 - gap0 + 1, depth))
    return out


def build_prompt(mid, m, bl):
    M, lw = m["M"], m["lw"]
    mx0, my0, mx1, my1 = M["mx0"], M["my0"], M["mx1"], M["my1"]
    tw, th = mx1 - mx0, my1 - my0
    shape = classify(mid, m)
    n = sum(len(v) for v in m["edges"].values())
    hub = m["hub"]
    hub2 = (sx(hub[0]), sy(hub[1]))
    wide = [r for r in m["regions"] if r["wide"]]
    narrow = [r for r in m["regions"] if not r["wide"]]
    P = {}
    # P1
    P["P1"] = (
        f"P1. COMPOSITION. The whole picture is a hand-made tabletop miniature seen from almost straight above: a model standing on a desk. "
        f"From the outside in on ALL FOUR sides (north, south, west and east alike): (a) the desk surface, a warm natural wooden tabletop with visible wood grain, a {M['desk']} px margin on all four sides of the frame, "
        f"mostly clear wood (at most a few small craft leftovers lie on it, well clear of the model); (b) the model's base, seen from above as a border band {M['band']} px wide that frames the top surface all the way around, unbroken "
        f"(no side face of the model is visible); (c) inside the band, the top surface of the model, which is the map. "
        f"Frame coordinates (1920x1080): the base band's outer edge is the rectangle x {M['desk']} to {W - M['desk']}, y {M['desk']} to {H - M['desk']}; "
        f"the model's top surface is the rectangle x {mx0} to {mx1}, y {my0} to {my1} ({tw} x {th} px). "
        f"(In the 1672x941 frame these are: band outer edge x {sx(M['desk'])} to {sx(W - M['desk'])}, y {sy(M['desk'])} to {sy(H - M['desk'])}; top surface x {sx(mx0)} to {sx(mx1)}, y {sy(my0)} to {sy(my1)}.) "
        f"On every one of the four sides of the picture, going inward from the picture's edge, you see in this order at full width: the wooden desk ({M['desk']} px), then the cream foamboard rim ({M['foam']} px), then the brown corrugated cardboard cross-section ({M['corr']} px), then the terrain. "
        f"The model's top surface lies wholly inside the picture and touches none of its edges; the north and south sides show the desk, the rim and the corrugated band exactly as the west and east sides do. "
        f"Nothing is drawn outside the model except the wooden desk and its few craft leftovers: no wall, no room, no sky, no horizon, no people. "
        f"The model is a miniature, so the whole picture is a model; the picture never reads as a photograph of a real place.")
    # P2
    P["P2"] = (
        f"P2. THE BASE BAND. Seen from above it is a framing border around the top surface. Its outer {M['foam']} px (x {M['desk']} to {M['desk'] + M['foam']} along the left side, and likewise on the other sides) "
        f"is the rim of a 5 mm foamboard slab (smooth pale white-cream paper-faced foam core, with the paper skin and the foam core visible along the rim). "
        f"Its inner {M['corr']} px (x {M['desk'] + M['foam']} to {mx0} on the left, and likewise on the other sides) is the exposed cross-section of corrugated cardboard "
        f"(the wavy flute layer between two flat liners, brown), glued around the foamboard's top edge with masking tape and white PVA glue, with ragged hand-cut paper edges. "
        f"The band runs unbroken along all four sides, north and south included, with both the foamboard rim and the corrugated layer clearly visible on each side. It is not interrupted where the passage{'s' if n > 1 else ''} reach{'' if n > 1 else 'es'} the model's edge. A few extra strips of masking tape and small PVA drips may lie on the band, "
        f"never hiding the corrugated layer over any long stretch.")
    # P3
    sides_txt = []
    order_note = {"N": "x", "S": "x", "W": "y", "E": "y"}
    for s in "NESW":
        es = m["edges"][s]
        if not es:
            continue
        edge_c = {"N": f"y {my0}", "S": f"y {my1}", "W": f"x {mx0}", "E": f"x {mx1}"}[s]
        ax = order_note[s]
        items = []
        for e in es:
            r = rng(ax, e["a"], e["b"])
            items.append(f"the {e['role'].replace('the ', '', 1)} at {r} ({path_text(e['poly'], hub)})")
        head = f"{SIDE_EN[s]}, {edge_c}), {len(es)} passage{'s' if len(es) > 1 else ''}: "
        sides_txt.append("  - " + head + "; ".join(items) + ".")
    quant = "A single flat floor band" if n == 1 else f"{NUM_EN.get(n, n)} flat floor bands"
    P["P3"] = (
        f"P3. THE PASSAGE{'S' if n > 1 else ''} AND THE MODEL'S EDGE. The model's top surface is made of thin flat paper-clay surfaces. "
        f"{quant}, {'each ' if n > 1 else ''}{lw} px wide ({lw / tw:.2f} of the model's width of {tw} px, which is {sx(lw)} px in the 1672x941 frame; a stand-in for three characters side by side; no character is drawn), "
        f"{'runs' if n == 1 else 'run'} from the middle of the model out to the model's edge, and "
        f"{'it reaches' if n == 1 else 'each reaches'} the model's edge and stops flush against the inner edge of the corrugated band of P2: the floor band ends where the model ends, at the band, "
        f"and never continues onto the band, the desk or the frame edge ({'each leads' if n > 1 else 'it leads'} on to the next map across the model's edge; the character stands anywhere within a stretch of the edge to cross over, "
        f"so nothing marks a crossing point). No marker, coloured zone, arrow, line or label of any kind is drawn at the edges. "
        f"Positions where each band meets the model's edge, in the 1920x1080 frame, measured from the layout diagram (first image):\n"
        + "\n".join(sides_txt) + "\n"
        f"  Along every other stretch of the model's four edges, the edge is solid raised paper-clay terrain meeting the corrugated band: "
        f"the floor band{'s are the only floor' if n > 1 else ' is the only floor'} that reach{'' if n > 1 else 'es'} the model's edge, {n} in all.")
    # P4
    if m["hall"] and mid != "BDY-02":
        die(f"{mid}: 割付図に広間（壁）が描かれている。広間つきMAPは BDY-02 だけ（専用の build_prompt_hall）")
    slv = sliver_info(m)
    if shape == "stub":
        s, (ax, v, c) = tip_of_stub(m, mid)
        tipc = f"{ax} {v}"
        if ax == "y":
            tipc2 = f"{ax} {sy(v)}"
        else:
            tipc2 = f"{ax} {sx(v)}"
        P["P4"] = (
            f"P4. THE END OF THE PASSAGE. The single passage ends in a closed, rounded end: a semicircular cap of radius {lw // 2} px whose centre is at about ({hub[0]}, {hub[1]}) (in 1672x941: about ({hub2[0]}, {hub2[1]})) "
            f"(the middle of the model) and whose farthest point is at {tipc} (in 1672x941: {tipc2}). The end is plain flat floor, level with the rest of the passage, "
            f"and the terrain closes it all around: there is no door, no gate, no hole, no object and no second route beyond it. "
            f"There is no hall, no room and no wall in this map; the whole floor is this one band."
            + (" The mouth is a story role name only: no lips, no teeth and no tongue are drawn, and no kiss is drawn; what is drawn is one passage and its closed end only." if mid == "BDY-01" else ""))
    elif shape == "straight":
        P["P4"] = (
            f"P4. THE ROUTE. The two bands form ONE single straight route that runs all the way across the model from one edge to the opposite edge, passing through the middle of the model "
            f"at about ({hub[0]}, {hub[1]}) (in 1672x941: about ({hub2[0]}, {hub2[1]})). It keeps the same {lw} px width over its whole length. There is no hall, no room, no wall and no side branch in this map.")
    elif shape == "bend":
        sides = [s for s in "NSWE" for _ in m["edges"][s]]
        P["P4"] = (
            f"P4. THE BEND. The two bands meet at the middle of the model, about ({hub[0]}, {hub[1]}) (in 1672x941: about ({hub2[0]}, {hub2[1]})), and form ONE continuous bent route (one corner, as in the layout diagram): "
            f"the route comes in from the {SIDE_EN[sides[0]].split(' ')[0].lower()} edge, turns one corner at the middle of the model, and leaves by the {SIDE_EN[sides[1]].split(' ')[0].lower()} edge. "
            f"The outer corner of the bend is rounded (radius {lw // 2} px) and the inner corner is a sharp right angle, both as in the layout diagram. "
            f"The width stays {lw} px along the whole route. There is no hall, no room, no wall and no side branch in this map.")
    else:
        sl_txt = ""
        for s, g, dep in slv:
            sl_txt += (f" Between the two bands that meet the {SIDE_EN[s].split(' ')[0].lower()} edge, a thin sliver of terrain {g} px wide runs inward from the edge for about {dep} px "
                       f"and ends in a point; it is solid raised terrain, not floor.")
            if g < SLIVER_NARROW:
                sl_txt += (" In this narrow band, the two facing partitions are merged into ONE single low ridge, and only one thin line of yarn runs along it; "
                           "the floor width of each passage is kept measured from the inner faces of the partitions.")
        P["P4"] = (
            f"P4. THE JUNCTION. The {n} bands meet and merge at the middle of the model, about ({hub[0]}, {hub[1]}) (in 1672x941: about ({hub2[0]}, {hub2[1]})), into one continuous flat floor area, exactly as in the layout diagram "
            f"(each band keeps its {lw} px width where it meets the model's edge, and the bands sweep toward the middle as described in P3).{sl_txt} "
            f"There is no hall, no round room and no wall in this map: the floor is simply the merged bands, flat and empty.")
    # P5
    P["P5"] = (
        f"P5. NOTHING ELSE ON THE ROUTE. Only the edges, bends and ends described in P3 and P4 are drawn: the route has no other branch, loop, crossing, side room or detour, "
        f"and no connection to any other map except through the model's edge{'s' if n > 1 else ''} named in P3. The floor is empty: no body parts, no faces, no object lies on it.")
    # P6
    P["P6"] = (
        f"P6. BORDERS OF THE PASSAGE{'S' if n > 1 else ''}. Along the passage edges, on the terrain side of the floor outline, run LOW PARTITIONS: narrow low ridges (seen from above as narrow raised borders) "
        f"built from strips of corrugated cardboard with paper clay smoothed over their tops, which make the passage{'s' if n > 1 else ''}. The partitions stand outside the floor outline, so the floor width stays {lw} px between their inner faces. "
        f"There are no doors, door frames or gates, no cave mouths, no round holes or tunnel mouths, no outline of any body: the top of the model is only flat floor, low partitions and terrain.")
    # P7
    reg_names = ", ".join(r["name"] for r in wide) if wide else "none"
    P["P7"] = (
        f"P7. THE TERRAIN. The terrain between and around the passage{'s' if n > 1 else ''} is thin, flat paper clay, painted in flat faces: matte poster paint in flesh skin tone, pale pink and cream, "
        f"laid on face by face with a flat brush (brush streaks and uneven coats visible), a different tone for each face. "
        f"It reads as a thin flat sheet of painted clay; it has no thick mounded layers, no stacked flesh-like bands, no striations and no fleshy cross-sections. "
        f"The passages divide the terrain into {len(wide)} wide region{'s' if len(wide) != 1 else ''} ({reg_names})"
        + (f" and {len(narrow)} narrow strip{'s' if len(narrow) != 1 else ''}" if narrow else "") + ".")
    P["P8"] = ("P8. COLORS: matte poster paint in flesh skin tone, pale pink and cream. Passage floors: cream and pale peach, the same range everywhere. "
               "Terrain and partitions: skin tone and pale pink. The desk is warm natural wood.")
    P["P9"] = (
        "P9. YARN. Wool yarn in cream and pale pink as the base colours, with light and deep skin-tone yarn also welcome. Double-wound yarn runs along the foot of the partitions and along the outer edges of the passage floors "
        "and at the seams between partitions and terrain, and spirals and coils of yarn lie on the terrain as ornamental swirls and borders, wound like a trim. "
        "The yarn is always on the terrain side of the floor outline, never on the floor, and it works as decorative swirls and edging only.")
    P["P10"] = (
        f"P10. RED ORIGAMI: EXACTLY SIX (6) hand-cut red paper pieces with uneven edges (cut with scissors from red origami paper, flat on the surface, glued with PVA), no more and no fewer: count them, six, with no seventh and no spare piece anywhere. "
        f"All six lie on the terrain faces INSIDE the model's top surface (x {M['mx0']} to {M['mx1']}, y {M['my0']} to {M['my1']}; in 1672x941: x {sx(M['mx0'])} to {sx(M['mx1'])}, y {sy(M['my0'])} to {sy(M['my1'])}), as clear craft accents, spread over the terrain "
        "(not on the partitions, not on the floors, not on the base band; none on the desk, none on the table, none on the frame edge, none anywhere outside the model). "
        "Their outlines are irregular and unequal, not drawn as any particular symbol; they are clean paper cut-outs, never blood stains or liquid. "
        "They are the only red objects in the picture: the six pieces inside the model are the whole red of the picture.")
    kinds = ("small lumps and balls of paper clay with fingerprints and with swirls and dot patterns pressed by a toothpick; buttons, beads and felt pieces (felt flowers) in skin tone, pale pink and cream; "
             "small toothpick stakes standing in the terrain; drips and dabs of white PVA glue; extra strips of masking tape; swirls, dots and wave patterns carved into the terrain surface with a toothpick")
    if len(wide) >= 2:
        dens = f"Each of the {len(wide)} wide terrain regions shows 3 to 5 kinds of these small items and patterns"
    else:
        dens = ("The wide terrain shows at least 6 clusters (for example a yarn swirl, a group of clay balls, buttons and beads, felt flowers, toothpick stakes, a pressed pattern), "
                "each cluster made of 3 to 5 kinds of these small items and patterns, spread over its whole area in proportion to its size")
    P["P11"] = (
        f"P11. DECORATION (a kindergarten-craft richness, in the manner of the shared diorama style). Hand-made trimmings are placed on the terrain (the surfaces that are not floor), along the foot of the partitions, on the base band and on the desk only: "
        f"{kinds}. The yarn of P9 is part of the decoration. {dens}; "
        f"{'the narrow strips carry only a thin edging of yarn' if narrow else 'the whole terrain feels rich and busy with handwork'}. "
        f"The floor stays perfectly flat, clean and empty: nothing is placed where the characters walk, and the width of the passage{'s' if n > 1 else ''} and the flatness of the floor are never reduced by the decoration. "
        f"The decoration never forms the outline of a body and never looks like an organ or a vessel; the yarn is ornamental swirls and edging only.")
    P["P12"] = (
        "P12. MATERIALS AND TOOLS (every material must be identifiable at full size): base: 5 mm foamboard with the corrugated cardboard cross-section band described in P2; terrain surface and partitions: paper clay modelled by hand, "
        "with fingerprints and toothpick marks; floors and terrain: matte poster paint applied with a flat brush; edges and seams: yarn; trimmings: buttons, beads, felt pieces, paper-clay balls, wooden toothpick stakes; "
        "joints and fixing: strips of masking tape and white PVA glue with squeeze-out and drips visible; accents: 6 pieces of red origami paper cut by hand with scissors; desk: wooden tabletop with visible wood grain. "
        "Hand-made roughness: glue squeeze-out, ragged hand-cut paper edges, paint unevenness, visible material seams. Parts look like paper and clay (matte, soft edges), not like real skin, flesh, organs or stone. "
        "It reads as a crude hand-made miniature in which the whole picture is the model, and not as a photograph of a real place.")
    P["P13"] = (
        "P13. CAMERA: the camera looks down steeper than 45 degrees from horizontal, as close to straight down as possible, never lower than 45 degrees from horizontal. North is the top of the image. "
        "Flat evenly lit tabletop light. The picture has no sky, no horizon, no vanishing point, no people, no characters, no readable text, no letters, no numbers, no logos.")
    P["P14"] = ("P14. DIMENSIONS: request 1920x1080 (16:9). If the tool cannot return it, 1672x941 is acceptable (every coordinate above then scales by 0.871; the 1672x941 values are given alongside). "
                "Any other size is a failure; never resize or crop to pass. Measure the real output file.")
    return P, shape


# ---------------------------------------------------------------- 警告・TBD
def warnings_for(mid, m, shape, slv):
    w = []
    if mid == "BDY-01":
        w.append("TBD: BDY-01 の event-mouth（TRM-01.event-kiss からの一方向イベント）の到着位置・向きは原文に無い。割付図にも印だけで床の形は無い。"
                 "絵には到着点の造形を足さない（本文に書かない）。")
    for s in "NSWE":
        for e in m["edges"][s]:
            decided = e["other"] == "BDY-02"
            w.append(f"{'決定済み' if decided else '仮案'}: {s}辺の {e['port']}→{e['other']}.{e['other_port']}。"
                     + ("相手の BDY-02 側の辺（kako-jun決定 2026-10-22）の反対辺。位置は割付図の提案" if decided
                        else "辺・位置・向きは body.svg 由来の機械導出（consistency.md。原文に無い。kako-jun 確認でやり直し可）"))
    w.append(f"仮置き: 通路幅 {m['lw']}px は『キャラクター3人分程度』の仮置き（模型天面幅比0.14）。画素値は原文でTBD。")
    if shape == "stub":
        w.append("割付図由来: 行き止まりの先端形状（半円の閉じた端）は原文に無い。"
                 + ("topology の『手足末端は閉じ』に整合。" if mid in ("BDY-06", "BDY-08", "BDY-11", "BDY-14") else
                    "BDY-01 の末端の扱いは原文に記述なし（口の中の到着位置はTBD）。"))
    if shape == "junction":
        w.append("割付図に広間は描かれていない（壁の画素なし）。4本は中央で合流する床として書き、広間・壁は足さない。"
                 "BDY-02 のような広間にするかは kako-jun 判断（割付図の変更が要る）。")
        w.append("BDY-03 の S 辺の通路は BDY-15（保留）への接続。BDY-15 の中身は描かない（BDY-03 側の通路だけ描く）。")
    for s, g, dep in slv:
        w.append(f"警告: {s}辺の2本の間に地形の細い帯（幅{g}px・奥行{dep}px）が残る。装飾の置ける面積が小さく、細い毛糸の縁取りだけにしている。")
    for r in m["regions"]:
        if not r["wide"]:
            w.append(f"警告: 狭い地形区画 {r['name']}（面積約{r['area']}px、bbox {r['bbox']}）は装飾なし・毛糸の縁取りのみ。")
    w.append("赤い折り紙6枚は BDY-02 の決定（2026-10-22「推奨で」）の流用で、他MAPへの適用は未承認の既定。後で変えられる。")
    w.append("参照3（BDY-02 採用画像）は様式のみ。通路・広間・赤紙位置の混入に注意（生画像レビューで確認）。")
    w.append("生成前の独立レビューは未実施（SKILL: 生成可には独立レビュー通過が必要）。")
    return w


# ---------------------------------------------------------------- 照合表・検査項目・md 全体
def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def fragment_table(mid, bundle_text, m, shape, slim=False):
    """原文の断片（束に逐語で存在することを確認）→ 本文のP。"""
    def must(frag):
        if frag not in bundle_text:
            die(f"照合表の原文断片が束に無い: {frag!r}")
        return frag

    rows = ([] if slim else [(must("手足末端は閉じ、手足相互の連絡や迂回路を足さない"), "topology", "P3, P4, P5（余計な経路・迂回路を足さない。末端は閉じる）")]) + [
        (must("幼稚園児の架空人体・非写実・肌色寄り"), "registry/spec/checklist", "P6（体の輪郭・洞窟口なし。平らな床・低い仕切り・地形だけ）, P7, P8"),
        (must("door-passageは物理的な扉でない"), "topology", "P6（扉・枠・門なし）"),
        (must("pixel/maskはTBD（mask未作成）" if mid in ROOM_MAPS else "通行幅・pixel/mask・脳内迷路はTBD"), "registry/spec/checklist", "P3（幅 230px は割付図の仮置き。画素値はTBDのまま）" if mid not in ROOM_MAPS else "P3, P4（通路幅・形は台帳が決定済み。形の詳細は割付図が正本。pixel/maskだけTBD）"),
        (must("幼稚園児が想像する架空人体"), "research R018", "P7, P8, P10, P12（非写実・肌色寄り・血に見えない）"),
        (must("5 mm foamboardの土台と見えるcorrugated cardboard断面"), "art-direction", "P2（土台縁の帯: 外28px foamboard・内20px corrugated 断面）"),
        (must("指跡・爪楊枝の跡を残したpaper clay"), "art-direction", "P7, P11, P12（指跡・爪楊枝の跡）"),
        (must("肌色・薄桃・クリーム色のmatte poster paint"), "art-direction", "P7, P8"),
        (must("赤い折り紙を切った形を血痕に見えない明確な工作アクセントとして置く"), "art-direction", "P10（手切りの赤い紙片6枚。地形の上のみ）"),
        (must("毛糸は通路の縁や造形の継ぎ目に用い"), "art-direction", "P9（毛糸は床の外側＝地形側）, P11"),
        (must("雪の綿は使わない"), "art-direction", "P12（材料列挙に綿なし）, 参照2の綿は継承しない"),
        (must("白いPVA接着剤とmasking tapeで固定し、紙端・接着・塗りの手作り感を残す"), "art-direction", "P2, P11, P12"),
        (must("通路は画像端でなく模型の縁まで届き、土台の板とまわりの机は見えたまま。遷移位置は画面端固定でなく範囲指定"),
         "art-direction:30", "P1（机・土台縁・天面）, P3（模型の縁で止まる・遷移位置に印を描かない）"),
        (must("視点は、真上に近い見下ろし"), "art-direction:30", "P13（鉛直下向き45°より急）"),
    ]
    if not slim:  # BDY-04 の slim な原文束には decisions の『体内入口』行（別MAPの話）を載せない
        rows.append((must("体内入口はTRM-01園庭→BDY-01口の物語イベント"), "decisions", "（BDY-01 のイベント到着は絵に描かない。警告）" if mid == "BDY-01" else "P4/P5（接続は模型の縁のみ）"))
    return rows


def render_md(mid, m, bl, bundle, P, shape, warns, wrapper, refs_text, body, table, out_name, send_sha="", ctx02=None):
    M, lw = m["M"], ctx02.get("lw", m["lw"])  # 通路幅（BDY-04・17 は1人幅 77px）
    reg_row = bundle.lines["registry"][bundle.rows["registry"] - 1]
    title_jp = re.match(r"^\|[^|]*\|[^|]*\|[^|]*\|\s*([^。|]*)", reg_row).group(1).strip()
    fence = "````"
    lines = []
    A = lines.append
    A(f"# {mid}（{title_jp}）" + "装飾込み1回生成の" + f"完全 imagegen prompt（`build_body_prompt.py` 自動生成。Issue #{ISSUE}）\n")
    A(("状態: **機械生成・独立レビュー済み（条件付き可）・指摘反映済み・画像は未生成**。" if mid == "BDY-02" else "状態: **機械生成・独立レビュー未実施・画像未生成**。") + "`.claude/skills/sit-field-background/SKILL.md` のゲート（台帳原文・材料固定宣言・一意解釈・寸法）に沿う。"
      + "型は採用済み BDY-02（v2 の構図・原文束、v3 の装飾語彙）。画像は生成しない。\n")
    A("## 0. 来歴・警告・TBD\n")
    A("来歴:\n- 生成器: `.claude/skills/sit-field-background/tools/build_body_prompt.py`（使い方: `build_body_prompt.py " + mid + " --out DIR`）。"
      "入力は docs の対象行（逐語）・Issue #142・`verification/body-layout/clean/" + mid + ".png` の画素実測・`body_layout.py` の折れ線。")
    A(f"- 型: `docs/production/20261022-bdy02-adoption.md` と `20261022-bdy02-adoption-prompts/`（v2-prompt-full.txt=構図・原文束、v3-edit-prompt.txt=装飾語彙）。")
    A(f"- 入力 sha256（参照2枚。様式参照画像は幾何を崩す疑いがあるので使わない）: clean `{sha(CLEAN_DIR / (mid + '.png'))}` / 材料見本 `{sha(SWATCH)}`")
    A(f"- 送信文 sha256: `{send_sha}`")
    A("- 送信文: `" + mid + "" + "-prompt-send.txt`（wrapper + 本文。この .md の §3.1 と §3.2 を連結したもの。§3.2 は §1 の原文束を SOURCE TEXT として含む。原文束の外に内部メモ・TBD・仮案を含まない）。\n")
    A("警告・TBD（ビルダーが検出）:\n" + "\n".join(f"- {w}" for w in warns) + "\n")
    A("## 1. 原文束（逐語。要約・言い換えなし）\n")
    t = bundle.text()
    run = max((len(x) for x in re.findall(r"`+", t)), default=0)
    fence = "`" * max(3, run + 1)
    A(f"{fence}text\n{t}{fence}\n")
    A(f"## 2. 参照一覧（実画像として入力する順。参照は2枚）\n")
    A("| # | パス | 用途 | 継承禁止事項 |\n|---|---|---|---|")
    ncol_jp = 5 if ctx02.get("wall") else 4
    A(f"| 1 | `verification/body-layout/clean/{mid}.png`（1920x1080、{ncol_jp}色のベタ。灰=机、茶=土台縁の帯、くすんだ桃茶=天面の地形、クリーム=歩ける床{'、青灰=広間の壁の弧' if ctx02.get('wall') else ''}。文字・注記・遷移範囲の着色なし。画像編集の入力＝塗り直しの土台） | 幾何のみ（机・土台縁・天面の入れ子、通路の本数・辺・位置・幅・曲がり・端） | 色を塗らせない（5色ベタ・硬い直線エッジは継承しない）。文字・遷移範囲の印を残さない |")
    A("| 2 | `verification/body-layout/BDY-material-swatch-corrugated-edge.png`（1540x52。寺町の採用画像の下端の帯を無加工で切り出した材料見本） | 材料の感じのみ: corrugated cardboard 断面・masking tape・ちぎれた紙端 | 帯上端の白い綿の繊維・茶色の色味は継承しない。雪を持ち込まない |")
    A("添付順 = 1, 2（wrapper の『Two images』の列挙と本文 REFERENCE の FIRST/SECOND が一致）。\n")
    A("## 3. 送信予定の完全 prompt\n")
    A("### 3.1 前置き指示（wrapper）\n")
    A(f"```text\n{wrapper}\n```\n")
    A("### 3.2 本文\n")
    fb = "`" * max(3, max((len(x) for x in re.findall(r"`+", body)), default=0) + 1)
    A(f"{fb}text\n{body}\n{fb}\n")
    A("## 4. 原文 → prompt 中の対応文 照合表\n")
    A("| 原文（逐語の断片。束に存在を確認済み） | 出典 | prompt 対応文 |\n|---|---|---|")
    for frag, src, p in table:
        A(f"| {frag} | {src} | {p} |")
    A(f"| 接続（{'、'.join(e['port'] + '→' + e['other'] + '.' + e['other_port'] for s in 'NESW' for e in m['edges'][s])}） | spec / topology の接続列 | P3（辺・位置は割付図の実測） |")
    A("")
    A("## 5. 割付図の実測（`clean/" + mid + ".png`。1920x1080 と ×0.871 の 1672x941）\n")
    A(f"- 構図: 机{M['desk']}px・土台縁{M['band']}px（foamboard {M['foam']} + corrugated {M['corr']}）・天面 x{M['mx0']}–{M['mx1']} y{M['my0']}–{M['my1']}（{M['mx1'] - M['mx0']}x{M['my1'] - M['my0']}）。通路幅 {lw}px（1672: {sx(lw)}px）。")
    A(ctx02["report"])
    A("| 辺 | port | 区間（1920） | 区間（1672x941） | 幅 | 折れ線（1920座標） |\n|---|---|---|---|---|---|")
    for s in "NESW":
        for e in m["edges"][s]:
            ax = "x" if s in "NS" else "y"
            f = sx if ax == "x" else sy
            poly = ", ".join(f"({round(x)},{round(y)})" for x, y in merge_collinear(e["poly"]))
            A(f"| {s} | {e['port']} | {ax} {e['a']}–{e['b']} | {ax} {f(e['a'])}–{f(e['b'])} | {e['w']} | {poly} |")
    A("")
    A("地形の区画（連結成分）: " + "; ".join(f"{r['name']}（{'広' if r['wide'] else '狭'}、面積約{r['area']}px、bbox {r['bbox']}）" for r in m["regions"]) + "\n")
    A("## 6. 寸法・検査項目（生成後。生画像レビュー用）\n")
    A(ctx02["checks"] + "\n")
    return "\n".join(lines)


# ---------------------------------------------------------------- 座標の丸め・表記
def r5(v):
    """実測値を 5px 刻みの名目値に丸める（実測との差が 3px を超えたら停止）。"""
    n = int(round(v / 5.0) * 5)
    if abs(n - v) > 3:
        die(f"実測 {v:.1f} が 5px 刻みの名目値 {n} から 3px を超えて外れる")
    return n


def pt2(x, y):
    return f"({x}, {y}) (in 1672x941: ({sx(x)}, {sy(y)}))"


# ---------------------------------------------------------------- 装飾込み1回生成（onepass）の送信文の前置き


def out_name_onepass(mid):
    return f"{mid.lower().replace('-', '')}-op-{'v4' if mid == 'BDY-02' else 'v1'}.png"  # BDY-02 は作り直し4版目（独立レビュー反映版）


def wrapper_onepass(out_name, ncol="four"):
    return (
        "Invoke the $imagegen skill and use the built-in image_gen tool at the HIGHEST quality (quality: high), keeping the editing source's size 1920x1080 (16:9), to repaint the image as described in the prompt below. "
        "This is an IMAGE EDIT: use the image_gen tool in image-edit mode on the first attached image. Two images are attached, in this order: "
        f"(1) the editing source (a flat {ncol}-colour layout diagram with no text; keep its geometry exactly, and use the meaning of its colours as described in the prompt); "
        "(2) a thin close-up strip of the edge of a hand-made cardboard miniature, for materials and craft feel only (as described in the prompt). "
        "Call image_gen EXACTLY ONCE: no retries, no regeneration, no multiple candidates, even if you think the result is imperfect. "
        f"Then save the REAL generated PNG (decode the tool result) into the current workspace at out/{out_name}. "
        "You are STRICTLY FORBIDDEN from fabricating/drawing the image with magick/ImageMagick/PIL/Pillow/numpy/SVG/canvas/any code; only the image_gen tool. "
        "If the image_gen tool is genuinely not in your toolset, do NOT fabricate - output exactly: IMAGE_GEN_TOOL_UNAVAILABLE. Do not resize or crop the result. "
        "Do not use any files in ~/.codex/generated_images/ made by other calls; only the image generated in this call. Report the saved file path.\n"
        "Output a 16:9 landscape image. Keep the size of the editing source (1920x1080); if not possible, 1672x941. Do NOT use 3:2 or 1536x1024. "
        "Do not mirror or flip the image; keep the direction of the editing source.")


# 送信文の語彙検査: 台座・内部語。SOURCE TEXT の外（wrapper・WHAT TO DRAW・REFERENCE）は内部語・仮案・TBD語も禁止。
LEAK_ALWAYS = ["台座", "pedestal", "plinth", "採用済み", "草案", "scratchpad", "BDY-style-reference", "bdy10"]
LEAK_OUTSIDE = ["仮案", "未決", "保留", "TBD", "内部", "要確認", "kako-jun", "Issue", "試験", "仮置き", "mock", "モック"]


FORBIDDEN_MOTIF = ["flowers?", "leaf", "foliage", "leaves (?:of|on) (?:felt|paper)", "clouds?", "stars?", "flags?", "fences?", "hearts", "heart-shaped", "heart shapes?", "animals?", "felt", "sequins?", "gardens?", "straws?", "mountains?", "trees?", "food"]


def leak_check(send, mid="BDY-02"):
    """戻り値: [(語, 位置の種別)]。種別: 'source'（SOURCE TEXT 内）/ 'outside'。空なら OK。"""
    a, b = "=== SOURCE TEXT (verbatim, do not paraphrase) ===\n", "\n\n=== WHAT TO DRAW"
    head, rest = send.split(a, 1)
    src, tail = rest.split(b, 1) if b in rest else (rest, "")  # 部屋・迷路の4枚は SOURCE が最後（wrapper → DRAW → REFERENCE → SOURCE）
    hits = []
    for w in LEAK_ALWAYS:
        if w == mid.lower().replace("-", ""):  # 自分のMAPの出力ファイル名（bdy10-s1-v1.png など）は様式参照の名前ではない
            continue
        for name, t in (("source", src), ("outside", head + tail)):
            if w in t:
                hits.append((w, name))
    for w in LEAK_OUTSIDE:
        if w in head + tail:
            hits.append((w, "outside"))
    for w in FORBIDDEN_MOTIF:  # 人体と無関係なモチーフ語は SOURCE TEXT の外（自作部分）に出さない（単語境界で照合）
        if re.search(rf"\b(?:{w})\b", head + tail, re.I):
            hits.append((w, "outside"))
    other = sorted(set(re.findall(r"BDY-\d+", head + tail)) - {mid})  # 送信文の自作部分に他MAPのIDを出さない
    hits += [(x, "outside") for x in other]
    return hits


# ---------------------------------------------------------------- BDY-02 以外（体内の手足・胴下段・口）: 斜めの帯・折れ線の画素実測と onepass の本文
# 広間の無い12枚のうち対象は BDY-01・03・05〜14。形は stub（末端の丸い閉じた端）/ through（辺から辺への1本の斜めの帯）/
# knee（折れ点1つ・BDY-09,12）/ junction（BDY-03 の4本合流）。座標・角度は clean 画素から実測し、body_layout の折れ線とは
# 『角度1.5度・位置4px』で突き合わせる（食い違えば停止）。本文に書く値は画素実測が正本。
def _run_along(fl, c, n, smax):
    """点 c から法線 n の両側へ、床が続く符号つき距離 (lo<=0<=hi)。c が床でなければ None。"""
    h_, w_ = fl.shape

    def at(s):
        x, y = int(round(c[0] + n[0] * s)), int(round(c[1] + n[1] * s))
        return 0 <= x < w_ and 0 <= y < h_ and bool(fl[y, x])
    if not at(0):
        return None
    hi = lo = 0.0
    while hi < smax and at(hi + 0.5):
        hi += 0.5
    while lo > -smax and at(lo - 0.5):
        lo -= 0.5
    return lo, hi


def fit_centre(fl, p0, p1, lw, skip0, skip1):
    """p0→p1 の区間を、法線方向の床の連続区間の中点列で直線に当てる（端から skip だけ除く）。戻り値 dict(pt, d, w, resid)。"""
    L = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
    d = np.array([(p1[0] - p0[0]) / L, (p1[1] - p0[1]) / L])
    n = np.array([-d[1], d[0]])
    pts, ws, t = [], [], skip0
    while t <= L - skip1:
        c = np.array(p0) + d * t
        r = _run_along(fl, c, n, lw * 1.3)
        if r is None:
            die(f"帯の中心線 ({c[0]:.0f},{c[1]:.0f}) が床でない（折れ線が画素と不一致）")
        if abs((r[1] - r[0] + 1) - lw) <= 3:  # 帯の幅が通路幅と合う走査だけを使う（他の帯との合流・縁での切れの走査は除く）
            pts.append(c + n * (r[0] + r[1]) / 2)
            ws.append(r[1] - r[0] + 1)
        t += 6
    if len(pts) < 8:
        die(f"帯の区間が短くて（幅の合う走査が{len(pts)}本）当てられない: {p0}→{p1}")
    P = np.array(pts)
    mu = P.mean(0)
    u, sv, vt = np.linalg.svd(P - mu)
    dd = vt[0] if vt[0] @ d > 0 else -vt[0]
    nn = np.array([-dd[1], dd[0]])
    return dict(pt=mu, d=dd, w=float(np.median(ws)), resid=float(np.abs((P - mu) @ nn).max()))


def lines_meet(fits):
    """複数の直線（点+向き）に最も近い点（最小二乗）。2本なら交点。"""
    A, b = np.zeros((2, 2)), np.zeros(2)
    for f in fits:
        Pm = np.eye(2) - np.outer(f["d"], f["d"])
        A += Pm
        b += Pm @ f["pt"]
    return np.linalg.solve(A, b)


def edge_cross(f, side, M):
    """直線 f が模型の辺 side と交わる点。"""
    pt, d = f["pt"], f["d"]
    if side in "NS":
        y = M["my0"] if side == "N" else M["my1"]
        s = (y - pt[1]) / d[1]
    else:
        x = M["mx0"] if side == "W" else M["mx1"]
        s = (x - pt[0]) / d[0]
    return pt + d * s


def dir_words(d):
    """向き d（画像座標: y は下向き）→ ('up'|'down', 'left'|'right')。"""
    return ("down" if d[1] > 0 else "up"), ("right" if d[0] > 0 else "left")


def slope_phrase(d, ang):
    v, h = dir_words(d)
    if ang > 89.0:
        return f"straight {v}"
    if ang < 1.0:
        return f"straight {h}"
    return f"sloping {v} and to the {h} at about {ang:.1f} degrees {'below' if v == 'down' else 'above'} horizontal"


def measure_diag(mid, m, bl, portals):
    """BDY-02 以外の clean 割付図から、斜めの帯の中心線（角度・折れ点・合流点・末端の丸い端・辺との交点）と、同じ辺の2本の間の細い地形帯を画素で実測する。"""
    fl, M, lw = m["floor"], m["M"], m["lw"]
    paths = bl.resolve_paths(mid, portals)
    specs = bl.SPECS[mid]["paths"]
    segs = []  # dict(path, i, a, b, fit)
    for pi, (kind, pts, isp) in enumerate(paths):
        for i in range(len(pts) - 1):
            a, b = pts[i], pts[i + 1]
            dxu, dyu = b[0] - a[0], b[1] - a[1]
            Ls = math.hypot(dxu, dyu)
            dxu, dyu = dxu / Ls, dyu / Ls

            def port_skip(sd):  # 縁で帯が切られるため、帯に直角な走査（±lw/2）が模型の内側に収まる距離だけ縁から離す
                return max(12.0, ((lw / 2) * abs(dxu) + 4) / max(abs(dyu), 1e-6)) if sd in "NS" else max(12.0, ((lw / 2) * abs(dyu) + 4) / max(abs(dxu), 1e-6))
            s0 = port_skip(portals[mid][specs[pi]["pts"][i]]["side"]) if (i == 0 and isp[0]) else 0.6 * lw
            s1 = port_skip(portals[mid][specs[pi]["pts"][i + 1]]["side"]) if (i + 1 == len(pts) - 1 and isp[-1]) else 0.6 * lw
            f = fit_centre(fl, a, b, lw, s0, s1)
            ang_a = math.degrees(math.atan2(abs(b[1] - a[1]), abs(b[0] - a[0])))
            ang = math.degrees(math.atan2(abs(f["d"][1]), abs(f["d"][0])))
            if abs(ang - ang_a) > 1.5:
                die(f"{mid}: 帯の角度 画素実測{ang:.1f}度 が body_layout の折れ線 {ang_a:.1f}度 と不一致")
            if abs(f["w"] - lw) > 3:
                die(f"{mid}: 帯の幅 画素実測{f['w']:.1f}px が通路幅{lw}px と不一致")
            f["ang"] = ang
            segs.append(dict(path=pi, i=i, a=a, b=b, fit=f))
    # 点のグループ: 解析の座標が同じ点は1つの節点（折れ点・合流点）
    nodes = {}
    for sg in segs:
        for end, p in ((0, sg["a"]), (1, sg["b"])):
            nodes.setdefault((round(p[0]), round(p[1])), []).append((sg, end))
    out_nodes, hub, caps, knees = {}, None, [], []
    by_port, path_pts = {}, []
    for pi, (kind, pts, isp) in enumerate(paths):
        path_pts.append([None] * len(pts))
    for key, mem in nodes.items():
        fits = [sg["fit"] for sg, _ in mem]
        sg0, end0 = mem[0]
        pi = sg0["path"]
        idx = sg0["i"] + end0
        isport = paths[pi][2][idx]
        if isport:
            side = bl_side(bl, mid, portals, specs[pi]["pts"][idx])
            c = edge_cross(fits[0], side, M)
            if math.hypot(*(c - np.array(key))) > 4:
                die(f"{mid}: 帯の中心線と辺の交点 ({c[0]:.0f},{c[1]:.0f}) が接続表の位置 {key} と不一致")
            q = (round(float(c[0])), round(float(c[1])))
            for sg, end in mem:
                path_pts[sg["path"]][sg["i"] + end] = q
            d_in = fits[0]["d"] if end0 == 0 else -fits[0]["d"]
            by_port[specs[pi]["pts"][idx]] = dict(edge=q, d=d_in, ang=fits[0]["ang"], side=side)
        elif len(mem) == 1:  # 自由端 = 丸い閉じた端
            f = fits[0]
            d_out = f["d"] if end0 == 1 else -f["d"]
            p = np.array(key, float)
            q = p - d_out * lw
            x = q.copy()
            while True:
                nxt = x + d_out * 0.5
                xx, yy = int(round(nxt[0])), int(round(nxt[1]))
                if not fl[yy, xx]:
                    break
                x = nxt
            far = x
            centre = far - d_out * lw / 2
            if math.hypot(*(centre - p)) > 4:
                die(f"{mid}: 末端の丸い端の中心 ({centre[0]:.0f},{centre[1]:.0f}) が body_layout の端 {key} と不一致")
            cq = (r5(centre[0]), r5(centre[1]))
            fq = (round(float(far[0])), round(float(far[1])))
            caps.append(dict(centre=cq, far=fq, d=d_out, ang=f["ang"]))
            path_pts[pi][idx] = cq
        else:
            c = lines_meet(fits)
            if math.hypot(*(c - np.array(key, float))) > 4:
                die(f"{mid}: 折れ点・合流点の画素実測 ({c[0]:.0f},{c[1]:.0f}) が body_layout の点 {key} と不一致")
            q = (r5(c[0]), r5(c[1]))
            for sg, end in mem:
                path_pts[sg["path"]][sg["i"] + end] = q
            if len(mem) == 2:
                knees.append(q)
            if len(mem) >= 3:
                hub = q
    # 折れ点の曲がり（進行方向の変化）
    turn = None
    if knees:
        sgs = [sg for sg in segs if sg["path"] == 0]
        f1, f2 = sgs[0]["fit"], sgs[1]["fit"]
        turn = math.degrees(math.acos(max(-1.0, min(1.0, float(f1["d"] @ f2["d"])))))
    # 同じ辺の2本の間の地形のくさび（辺から内向きに、2本が1本に合わさって地形が尽きる所まで。幅が SLIVER_NARROW 未満になる区間も測る）
    slivers = []
    for s in "NSWE":
        es = m["edges"][s]
        for e1, e2 in zip(es, es[1:]):
            g = e2["a"] - e1["b"] - 1
            lo_, hi_ = e1["a"], e2["b"]
            last, k80, kt = None, None, None
            for k in range(EDGE_DEPTH, 900):
                if s in "NS":
                    pos = M["my0"] + k if s == "N" else M["my1"] - 1 - k
                    runs = runs_of(fl[pos, lo_:hi_ + 1])
                else:
                    pos = M["mx0"] + k if s == "W" else M["mx1"] - 1 - k
                    runs = runs_of(fl[lo_:hi_ + 1, pos])
                if len(runs) < 2:
                    break
                gap = runs[1][0] - runs[0][1] - 1
                if k80 is None and gap < SLIVER_NARROW:
                    k80 = (k, pos)
                last, kt = (pos, lo_ + (runs[0][1] + runs[1][0]) // 2), k
            if last is None:
                die(f"{mid}: {s}辺の2本の間の地形帯が見つからない")
            tp = (last[1], last[0]) if s in "NS" else (last[0], last[1])
            slivers.append(dict(side=s, g=g, tip=(round(tp[0]), round(tp[1])), depth=int(kt) + 1,
                                narrow_from=(k80[1] if k80 else None), narrow_len=(int(kt - k80[0]) + 1 if k80 else 0),
                                axis=("y" if s in "NS" else "x")))
    # 形
    nseg = len(segs)
    nports = sum(len(m["edges"][s]) for s in "NSWE")
    if hub:
        shape = "junction"
    elif nports == 1:
        shape = "stub"
    elif nseg == 1:
        shape = "through"
    else:
        shape = "knee"
    if shape == "knee" and not (33.0 <= turn <= 37.0):
        die(f"{mid}: 折れ点の曲がり {turn:.1f}度 が『鈍角35度』(33〜37) でない")
    return dict(shape=shape, segs=segs, path_pts=path_pts, by_port=by_port, caps=caps, knees=knees, hub=hub, turn=turn, slivers=slivers,
                angs=[round(sg["fit"]["ang"], 1) for sg in segs], resid=max(sg["fit"]["resid"] for sg in segs))


def bl_side(bl, mid, portals, port):
    return portals[mid][port]["side"]


def side_en(s):
    return SIDE_EN[s].split(" ")[0].lower()


def band_end_text(info):
    return f"{pt2(*info['edge'])}"


# ---------------------------------------------------------------------------
# 装飾のMAPごとの変化（マンネリ回避。kako-jun 2026-10-22「周りの装飾もマンネリにならないほうがいい」）
# BDY ID から決定的に決める（表 DECO_PICK ＋ MAP ID を seed にした random.Random で細部）。BDY-02・BDY-09 も新プール（採用済みの旧版は --force-redo でだけ作り直す）。
# ---------------------------------------------------------------------------
FAMILY = {  # モチーフ族 -> (主役のときの文, 脇役のときの文)。人体に関係する抽象的な工作物だけ（kako-jun 指示 2026-10-22「人体と関係ない花とか雲を使うのはやめろ」）。
    # 使わない: 花・葉・雲・星・旗・柵・ハート形・動物・食べ物・風景、臓器の形（心臓・肺・胃・脳・腸）、血管の網、血・傷・内臓に見える形。禁止語は prompt に書かない（書くと描かれやすい）。肯定形で下の8族だけを書く。
    "BONE": ("small bones made by hand: a short toothpick (or a thin roll of paper clay) with a small ball of paper clay at each end, like a tiny cartoon bone, in cream and ivory, lying singly, crossed in pairs or in little piles",
             "a few tiny ball-ended bones"),
    "CELL": ("cells and grains: round balls of paper clay with fingerprints, beads, buttons and small flat discs in cream, pale pink and skin tone, glued singly, in pairs, in lines or in small heaps",
             "a few clay balls, beads and small discs"),
    "THREAD": ("muscle and nerve threads: bundles of wool yarn, twisted cords, spirals, swirls and coils in cream, pale pink and skin-tone shades, laid as short separate strands and curls; each strand stays on its own and never joins others into a net and never branches",
               "a few short yarn bundles and small coils"),
    "PULSE": ("pulse lines: wool yarn in cream or pale pink glued down as jagged zigzag lines of yarn, in short separate lines",
              "a few short zigzag lines of yarn"),
    "SKIN": ("skin texture carved into the paper clay with a toothpick: fingerprint-like swirls of concentric lines, fields of tiny pore dots, and wrinkle patterns of short parallel curved lines",
             "a few small patches of carved fingerprint swirls and pore dots"),
    "PLASTER": ("adhesive bandage strips: small pieces of skin-coloured paper tape or masking tape stuck on in crosses or at a slant, with one edge slightly lifted",
                "a few small skin-coloured tape crosses"),
    "HAIR": ("hair: short tufts of cut thread in cream, ivory and light brown, glued down in small clumps",
             "a few small tufts of thread hair"),
    "GERM": ("germs as a child imagines them: small round balls of paper clay with short toothpick spikes sticking out all around, cute abstract shapes, in cream, pale pink or light brown",
             "a few tiny spiky clay balls"),
}
COLOR_RULE = ("COLOURS OF THE DECORATION: every decoration item is coloured only within skin tone, pale pink, cream, ivory and brown shades "
              "(yarn: light to deep shades of cream, pale pink and skin tone; beads, buttons, discs and clay balls: cream, pale pink, skin tone or light brown; toothpicks: natural wood). "
              "The red of the six origami pieces of P10 is the only other colour in the model, and the desk is natural wood. "
              "So the whole model reads as one warm family of skin, pale pink, cream and brown.")
LAYOUT = {
    "scatter": "SCATTERED: small groups spread evenly over every terrain region, no two groups alike",
    "wallband": "WALL BAND: the decoration forms a continuous belt that follows the foot of the partitions and the inner side of the base band, the middle of each terrain region staying calmer",
    "corners": "CORNER CLUMPS: the decoration gathers in tight clumps in the corners of the terrain (where partitions meet the base band), with open painted surface between the clumps",
    "diagonal": "DIAGONAL ROWS: the decoration lines up in slanting rows that run roughly parallel to the passage direction, one row after another across each terrain region",
    "spiral": "SPIRAL CHAIN: a chain of spiral shapes (fingerprint swirls, coils of yarn, rolled clay, round cells in rings) linked one after another across each terrain region, small items filling the gaps",
    "mass": "ONE BIG MASS: most of the decoration is one large heaped cluster in the biggest terrain region, with a few small items in the other regions; the rest of the terrain is left as calm painted surface",
}
TONE = {
    "skin": "flesh skin tone leaning slightly warm, with pale pink faces mixed in",
    "pink": "pale pink leaning, with a few skin-tone faces mixed in",
    "cream": "cream leaning (pale cream and light peach faces), with a few pale pink faces mixed in",
    "brown": "warm brown-leaning skin tones",
}
# 土台縁の毛糸（床際の縁取り）・テープ・PVA の色、机の木目・机の切れ端。色は肌色・薄桃・クリーム・茶系・象牙色の範囲だけ
DECO_PICK = {  # mid: (主役族, レイアウト, 地形の色味, 縁取りの毛糸, 土台縁のテープ・PVA, 机の木目, 机の切れ端と置き方)
    # BDY-02・09 は kako-jun『つくりなおせ』(2026-10-22) で旧プールから新プールへ。隣（BDY-02: 01・03・05・07、BDY-09: 03・10）と主役族2種以上・配置・色味を被らせない。
    "BDY-02": (("PULSE", "THREAD", "SKIN"), "scatter", "brown", "deep skin-tone", "cream masking tape and white PVA", "warm medium-brown grain with fine straight lines",
               "a few thread ends and a small clay crumb along the lower desk margin"),
    "BDY-09": (("HAIR", "GERM", "CELL"), "diagonal", "cream", "light skin-tone", "ivory masking tape and a thin PVA line", "pale honey grain with a few soft knots",
               "two short thread tufts and a spare toothpick along the left desk margin"),
    "BDY-01": (("BONE", "SKIN", "HAIR"), "corners", "pink", "cream", "cream masking tape and clear-white PVA", "medium honey-coloured oak grain",
               "two short scraps of masking tape and a few thread ends in the lower-left corner of the desk"),
    "BDY-03": (("CELL", "PLASTER", "PULSE"), "mass", "skin", "pale pink", "ivory masking tape and white PVA", "light pale birch grain with fine lines",
               "a loose curl of tape and a toothpick lying along the top desk margin"),
    "BDY-05": (("BONE", "THREAD", "GERM"), "wallband", "skin", "light skin-tone", "kraft-brown paper tape and white PVA", "dark walnut-coloured grain, fairly strong",
               "a few thread ends and a small clay crumb in the upper-right corner of the desk"),
    "BDY-06": (("SKIN", "PULSE", "HAIR"), "diagonal", "pink", "pale pink", "white masking tape and a thin PVA line", "medium grain with a visible knot near one side",
               "a torn paper-tape strip and two tape scraps along the right desk margin"),
    "BDY-07": (("CELL", "PLASTER", "HAIR"), "spiral", "cream", "cream", "cream masking tape and white PVA", "light honey grain, wide and soft",
               "a small ball of leftover yarn and a toothpick in the lower-right corner of the desk"),
    "BDY-08": (("GERM", "BONE", "THREAD"), "scatter", "skin", "light skin-tone", "skin-coloured masking tape and white PVA", "medium grain with tight lines",
               "a few thread ends and tape scraps scattered along the left desk margin"),
    "BDY-10": (("BONE", "PULSE", "SKIN"), "wallband", "pink", "pale pink", "cream masking tape and white PVA", "dark reddish-brown grain",
               "a small lump of clay with fingerprints and a thread end in the upper-left corner of the desk"),
    "BDY-11": (("GERM", "PLASTER", "THREAD"), "mass", "skin", "cream", "white masking tape and white PVA", "light grain, nearly plain",
               "two spare cream beads and a toothpick near the bottom desk margin"),
    "BDY-12": (("THREAD", "SKIN", "GERM"), "spiral", "cream", "light skin-tone", "cream masking tape and a thin PVA line", "medium grain with long waves",
               "a coil of yarn and one tape scrap in the upper-right corner of the desk"),
    "BDY-13": (("CELL", "BONE", "HAIR"), "corners", "pink", "pale pink", "kraft-brown paper tape and white PVA", "dark grain with a few cracks",
               "a few small clay balls and a thread end at the lower-left of the desk"),
    "BDY-14": (("PLASTER", "PULSE", "GERM"), "diagonal", "cream", "cream", "white masking tape and a thin PVA line", "light pale grain with a soft stripe",
               "paper-tape scraps and a crumb of clay along the right desk margin"),
    # BDY-04・15・16・17（部屋・迷路。2026-10-22）。隣（BDY-04/16/17 は BDY-02、BDY-15 は BDY-03）と、4枚どうしで 主役族の重なり1種以下・配置・色味が全て違う。
    "BDY-04": (("SKIN", "CELL", "GERM"), "spiral", "pink", "cream", "skin-coloured masking tape and white PVA", "honey-brown grain with a few wide soft rings",
               "a thread end and two tiny clay balls along the upper desk margin"),
    "BDY-15": (("GERM", "PLASTER", "HAIR"), "corners", "brown", "deep skin-tone", "kraft-brown paper tape and a thin PVA line", "pale oak grain with close fine lines",
               "a torn scrap of tape and a toothpick in the lower-right corner of the desk"),
    "BDY-16": (("PULSE", "BONE", "CELL"), "wallband", "cream", "pale pink", "white masking tape and white PVA", "dark chestnut grain with long straight lines",
               "a short loop of yarn and one spare bead along the left desk margin"),
    "BDY-17": (("THREAD", "CELL", "HAIR"), "diagonal", "skin", "light skin-tone", "cream masking tape and clear-white PVA", "pale ash grain with a soft wavy stripe",
               "two thread tufts and a crumb of clay in the upper-left corner of the desk"),
}
ADOPTED = ("BDY-02", "BDY-09")  # 採用済み（旧プールの装飾）。既定は拒否。作り直しは --force-redo だけ（kako-jun 2026-10-22『つくりなおせ』）
ADJACENT = [("BDY-01", "BDY-02"), ("BDY-02", "BDY-03"), ("BDY-02", "BDY-05"), ("BDY-02", "BDY-07"), ("BDY-05", "BDY-06"), ("BDY-07", "BDY-08"),
            ("BDY-03", "BDY-09"), ("BDY-09", "BDY-10"), ("BDY-10", "BDY-11"), ("BDY-03", "BDY-12"), ("BDY-12", "BDY-13"), ("BDY-13", "BDY-14"),
            # 部屋・迷路の4枚: 接続の隣（頭・心臓・肺は BDY-02、胃は BDY-03）と、4枚どうし（同じ胴体の枝の部屋）
            ("BDY-02", "BDY-04"), ("BDY-03", "BDY-15"), ("BDY-02", "BDY-16"), ("BDY-02", "BDY-17"),
            ("BDY-04", "BDY-15"), ("BDY-04", "BDY-16"), ("BDY-04", "BDY-17"), ("BDY-15", "BDY-16"), ("BDY-15", "BDY-17"), ("BDY-16", "BDY-17")]
PAIRS = [("BDY-05", "BDY-07"), ("BDY-06", "BDY-08"), ("BDY-09", "BDY-12"), ("BDY-10", "BDY-13"), ("BDY-11", "BDY-14")]


def deco_of(mid):
    p, lay, tone, yarn, tape, desk, left = DECO_PICK[mid]
    return dict(prim=p, layout=lay, tone=tone, yarn=yarn, tape=tape, desk=desk, leftovers=left)


def check_deco_plan():
    """隣接MAPで 主役族が2種以上重ならない・配置パターンと地形の色味が違う、を機械検査。違反なら止める。"""
    bad = []
    for a, b in ADJACENT:
        da, db = deco_of(a), deco_of(b)
        ov = set(da["prim"]) & set(db["prim"])
        if len(ov) > 1:
            bad.append(f"{a}-{b}: 主役族が{len(ov)}種重なる {sorted(ov)}")
        if da["layout"] == db["layout"]:
            bad.append(f"{a}-{b}: 配置パターンが同じ {da['layout']}")
        if da["tone"] == db["tone"]:
            bad.append(f"{a}-{b}: 地形の色味が同じ {da['tone']}")
    for a, b in PAIRS:
        if deco_of(a)["layout"] == deco_of(b)["layout"]:
            bad.append(f"{a}/{b}: 左右の対で配置パターンが同じ")
    if bad:
        die("装飾計画の隣接検査に失敗: " + " / ".join(bad))


def write_decoration_plan(path):
    """MAPごとの装飾選択を一覧表にして出す（decoration-plan.md）。隣接MAPの被り検査の結果つき。"""
    check_deco_plan()
    ids = ["BDY-01", "BDY-02", "BDY-03", "BDY-04", "BDY-05", "BDY-06", "BDY-07", "BDY-08", "BDY-09", "BDY-10", "BDY-11", "BDY-12", "BDY-13", "BDY-14",
           "BDY-15", "BDY-16", "BDY-17"]
    L = ["# 体内BDY 装飾計画（MAPごとに変える）", "",
         "生成元: `.claude/skills/sit-field-background/tools/build_body_prompt.py --plan <このファイル>`（表は `DECO_PICK` から機械出力。手で直さない）。",
         "BDY-02・BDY-09 も新プールで作り直す（kako-jun 2026-10-22『つくりなおせ』。採用済みの旧版は新版が採用されるまで残す。ビルダーは `--force-redo` が要る）。新プールは人体に関係する抽象的な工作物だけ（骨・細胞・筋肉の糸・鼓動線・皮膚・ばんそうこう・毛・ばい菌）。", "",
         "| MAP | 役割 | 主役モチーフ族 | 配置パターン | 地形の色味 | 縁取り毛糸 | 土台縁のテープ・PVA | 机の木目 | 机の切れ端 |", "|---|---|---|---|---|---|---|---|---|"]
    role = {"BDY-01": "口(閉端)", "BDY-02": "上半身(広間・首・分岐。作り直し)", "BDY-03": "下半身(合流)", "BDY-05": "左手1", "BDY-06": "左手2(閉端)", "BDY-07": "右手1", "BDY-08": "右手2(閉端)",
            "BDY-09": "左足1(作り直し)", "BDY-10": "左足2", "BDY-11": "左足3(閉端)", "BDY-12": "右足1", "BDY-13": "右足2", "BDY-14": "右足3(閉端)",
            "BDY-04": "頭(脳の迷路・1人幅)", "BDY-15": "胃(J字の1袋)", "BDY-16": "心臓(2x2の4部屋の環)", "BDY-17": "肺(外周の環・5部屋)"}
    for mid in ids:
        d = deco_of(mid)
        prim = "/".join(d["prim"])
        L.append(f"| {mid} | {role[mid]} | {prim} | {d['layout']} | {d['tone']} | {d['yarn']} | {d['tape']} | {d['desk']} | {d['leftovers']} |")
    L += ["", "## 隣接MAPの被り検査（機械検査・違反があれば --all / --plan は停止）", "",
          "| 隣接 | 主役族の重なり | 配置パターン | 地形の色味 |", "|---|---|---|---|"]
    for a, b in ADJACENT:
        da, db = deco_of(a), deco_of(b)
        ov = sorted(set(da["prim"]) & set(db["prim"]))
        L.append(f"| {a} - {b} | {len(ov)}種 {ov if ov else ''} (<=1) | {da['layout']} / {db['layout']} (異) | {da['tone']} / {db['tone']} (異) |")
    L += ["", "## 左右の対（同じ族を使ってよいが配置は変える）", "", "| 対 | 主役族 | 配置 |", "|---|---|---|"]
    for a, b in PAIRS:
        da, db = deco_of(a), deco_of(b)
        L.append(f"| {a} / {b} | {'/'.join(da['prim'])} ; {'/'.join(db['prim'])} | {da['layout']} / {db['layout']} |")
    L += ["", "## 規則", "", "- 手の連続 05→06 / 07→08、足 09→10→11 / 12→13→14 は主役族の重なり1種以下・配置・色味を必ず変える。",
          "- 地形の色味は隣接MAPと必ず変える（茶 brown は隣が肌・薄桃・クリームだけの BDY-02 に割り当て）。",
          "- 赤い折り紙は模型の中の地形の上にちょうど6枚（模型の外・机・床・土台縁には置かない）。置き場所の言及は MAP ID を seed にした順で変える。",
          "- 床は平らに空ける。装飾は地形・壁際・土台縁・机だけ。装飾は文章のみ（様式参照画像なし）。"]
    Path(path).write_text("\n".join(L) + "\n", encoding="utf-8")


def deco_texts(mid, wide_names, n_wide):
    """(P7の色味文, P8の装飾色文, P9, P10の置き方の追記, P12の装飾列挙, 縁取り毛糸の色)。seed = MAP ID。"""
    d = deco_of(mid)
    r = random.Random(mid)
    prim = d["prim"]
    minor = [k for k in FAMILY if k not in prim]
    r.shuffle(minor)
    minor = minor[:3]
    lead = []
    for i, k in enumerate(prim):
        lead.append(("MAIN motif " if i == 0 else "SECOND motif " if i == 1 else "THIRD motif ") + f"({k.lower()}): " + FAMILY[k][0])
    side = "; ".join(FAMILY[k][1] for k in minor)
    p9 = (
        "P9. DECORATION (hand-made craft ornament about the human body, placed on the terrain, along the foot of the partitions, on the edge of the base band and on the desk only). "
        "The decoration is made ONLY of small abstract handmade items that belong to the human body, in the kinds listed below as the leading and the supporting motifs; no other kind of ornament is used. "
        f"This map has its own decoration theme, different from the neighbouring maps. The leading motifs are: " + "; ".join(lead) + ". "
        f"Only as small supporting touches, never as the main look: {side}. "
        f"ARRANGEMENT: {LAYOUT[d['layout']]}. "
        f"EDGE COLOURS: the edging strand of yarn at the foot of the partitions is {d['yarn']}; the masking tape and PVA of the base band are {d['tape']}. {COLOR_RULE} "
        f"THE DESK: a warm wooden tabletop, {d['desk']}; around the model lie {d['leftovers']} (only these, small and few; nothing on the desk covers or touches the base band over a long stretch). "
        f"DENSITY at kindergarten-craft level, in proportion to the area of the terrain: "
        + (f"each of the {n_wide} wide regions of terrain shows 3 to 5 kinds of small items and patterns, " if n_wide >= 2 else "")
        + "the decoration forms at least 6 groups over the terrain (arranged as the ARRANGEMENT says), so the picture feels rich and handmade. ")
    p7tone = f"matte poster paint, the terrain {TONE[d['tone']]}"
    p8 = (f"Terrain: matte poster paint, {TONE[d['tone']]}, one tone per face. {COLOR_RULE} The edging yarn is {d['yarn']}. The desk is warm natural wood ({d['desk']}).")
    names = list(wide_names)
    r.shuffle(names)
    p10add = ("Where they sit: spread them over the terrain with this map's own pattern" + (f", with the first ones in the {names[0]} region" if names else "") +
              (f" and the next ones towards the {names[1]} region" if len(names) > 1 else "") + "; each lies in a different spot from the usual even spread.")
    p12dec = "decoration (handmade items about the human body): " + ", ".join({"BONE": "toothpicks and paper clay for small bones", "CELL": "paper-clay balls, beads and buttons for cells",
                                         "THREAD": "wool yarn for muscle and nerve threads", "PULSE": "wool yarn for zigzag pulse lines", "SKIN": "toothpick-carved skin patterns in paper clay",
                                         "PLASTER": "skin-coloured paper tape for adhesive bandages", "HAIR": "cut thread for hair tufts", "GERM": "paper clay and toothpick points for germs"}[k] for k in prim) + ", with small supporting touches of the other body-related items"
    return p7tone, p8, p9, p10add, p12dec, d


def build_prompt_diag(mid, m, dg, bl):
    """onepass の本文（P1〜P14）。P1/P2/P5/P10/P13/P14 は共通（build_prompt）、P3/P4 は clean の画素実測、P6〜P12 は構造＋装飾の語彙（P9 が装飾、P11 が床は空のまま）。"""
    base, _ = build_prompt(mid, m, bl)
    M, lw = m["M"], m["lw"]
    tw = M["mx1"] - M["mx0"]
    n = sum(len(v) for v in m["edges"].values())
    shape = dg["shape"]
    pl = "s" if n > 1 else ""
    P = dict(base)
    # ---- P3
    sides_txt = []
    for s in "NESW":
        es = m["edges"][s]
        if not es:
            continue
        ax = "x" if s in "NS" else "y"
        edge_c = {"N": f"y {M['my0']}", "S": f"y {M['my1']}", "W": f"x {M['mx0']}", "E": f"x {M['mx1']}"}[s]
        items = []
        for e in es:
            bi = dg["by_port"][e["port"]]
            items.append(f"the {e['role'].replace('the ', '', 1)} at {rng(ax, e['a'], e['b'])}; its centre line crosses the edge at {band_end_text(bi)} and runs inward {slope_phrase(bi['d'], bi['ang'])}")
        sides_txt.append(f"  - {SIDE_EN[s]}, {edge_c}), {len(es)} passage{'s' if len(es) > 1 else ''}: " + "; ".join(items) + ".")
    if shape == "stub":
        lead = (f"A single flat floor band, {lw} px wide measured across the band", " runs from a closed end inside the model out to the model's edge, and it reaches")
    elif shape == "junction":
        lead = (f"{NUM_EN.get(n, n)} flat floor bands, each {lw} px wide measured across the band", " run from the junction in the middle of the model out to the model's edge, and each reaches")
    else:
        lead = (f"One continuous flat floor route, {lw} px wide measured across the route", " has its two ends at the model's edge, and each end reaches")
    P["P3"] = (
        f"P3. THE PASSAGE{'S' if n > 1 else ''} AND THE MODEL'S EDGE. The model's top surface is made of thin flat paper-clay surfaces. "
        f"{lead[0]} ({lw / tw:.2f} of the model's width of {tw} px, which is {sx(lw)} px in the 1672x941 frame; a stand-in for three characters side by side; no character is drawn),"
        f"{lead[1]} the model's edge and stops flush against the inner edge of the corrugated band of P2: the floor band ends where the model ends, at the band, "
        f"and never continues onto the band, the desk or the frame edge ({'each leads' if n > 1 else 'it leads'} on to the next map across the model's edge; the character stands anywhere within a stretch of the edge to cross over, "
        f"so nothing marks a crossing point). No marker, coloured zone, arrow, line or label of any kind is drawn at the edges. "
        f"The bands are diagonal, so where a band meets the edge it is wider along the edge than across itself; the stretches below are measured along the edge, {EDGE_DEPTH} px inside it. "
        f"Positions where each band meets the model's edge, in the 1920x1080 frame, measured from the layout diagram (first image):\n"
        + "\n".join(sides_txt) + "\n"
        f"  Along every other stretch of the model's four edges, the edge is solid raised paper-clay terrain meeting the corrugated band: "
        f"the floor band{'s are the only floor' if n > 1 else ' is the only floor'} that reach{'' if n > 1 else 'es'} the model's edge, {n} in all.")
    # ---- P4
    bp = dg["by_port"]
    ports_order = [pa for pa in m["edges"]["N"] + m["edges"]["E"] + m["edges"]["S"] + m["edges"]["W"]]
    nowall = " There is no hall, no room and no wall in this map"
    if shape == "stub":
        e = ports_order[0]
        b = bp[e["port"]]
        cap = dg["caps"][0]
        P["P4"] = (
            f"P4. THE ROUTE AND ITS CLOSED END. The single passage is ONE straight diagonal band {lw} px wide with no bend and no branch. Its centre line starts at the {side_en(b['side'])} edge at {pt2(*b['edge'])}, "
            f"runs {slope_phrase(b['d'], b['ang'])}, and ends at a closed, rounded end: a semicircular cap of radius {lw // 2} px whose centre is at about {pt2(*cap['centre'])} and whose farthest point is at about {pt2(*cap['far'])}. "
            f"The width of {lw} px is measured across the band, perpendicular to its centre line. The end is plain flat floor, level with the rest of the passage, "
            f"and the terrain closes it all around: there is no door, no gate, no hole, no object and no second route beyond it."
            f"{nowall}; the whole floor is this one band."
            + (" The mouth is a story role name only: no lips, no teeth and no tongue are drawn, and no kiss is drawn; what is drawn is one passage and its closed end only." if mid == "BDY-01" else ""))
    elif shape == "through":
        # 辺→辺の向き: SPECS の port の並び順
        order = [pp for pp in bl.SPECS[mid]["paths"][0]["pts"] if isinstance(pp, str)]
        b1, b2 = bp[order[0]], bp[order[1]]
        P["P4"] = (
            f"P4. THE ROUTE. The two band ends are joined by ONE single straight diagonal band {lw} px wide, with no bend, no corner and no branch. Its centre line runs from {pt2(*b1['edge'])} at the {side_en(b1['side'])} edge "
            f"to {pt2(*b2['edge'])} at the {side_en(b2['side'])} edge; seen from the {side_en(b1['side'])} edge it runs {slope_phrase(b1['d'], b1['ang'])}. "
            f"The width of {lw} px is measured across the band, perpendicular to its centre line, over its whole length. It leaves the model across the {side_en(b2['side'])} edge and nothing else.{nowall} and no side branch.")
    elif shape == "knee":
        order = [pp for pp in bl.SPECS[mid]["paths"][0]["pts"] if isinstance(pp, str)]
        b1, b2 = bp[order[0]], bp[order[1]]
        f1, f2 = dg["segs"][0]["fit"], dg["segs"][1]["fit"]
        k = dg["knees"][0]
        P["P4"] = (
            f"P4. THE ROUTE AND ITS ONE BEND. The two band ends are joined by ONE continuous diagonal route with exactly ONE bend (a single knee), {lw} px wide across its centre line along its whole length. "
            f"From the {side_en(b1['side'])} edge, centre point {pt2(*b1['edge'])}, the first leg runs {slope_phrase(f1['d'], f1['ang'])} to the bend at about {pt2(*k)}. "
            f"There the direction changes by only {dg['turn']:.0f} degrees (an obtuse interior angle of {180 - dg['turn']:.0f} degrees: a gentle bend, not a sharp turn), "
            f"and the second leg runs {slope_phrase(f2['d'], f2['ang'])} to the {side_en(b2['side'])} edge, centre point {pt2(*b2['edge'])}. "
            f"The outer corner of the bend is rounded (radius {lw // 2} px) and the inner corner is a plain sharp corner. Exactly one bend: no second bend, no branch.{nowall}.")
    else:
        hub = dg["hub"]
        parts = []
        for s in "NESW":
            for e in m["edges"][s]:
                b = bp[e["port"]]
                role = e["role"].replace("the ", "", 1)
                if b["ang"] > 89.0:
                    parts.append(f"the {role} comes in from the {side_en(s)} edge exactly vertical, at {rng('x', e['a'], e['b'])}, straight down to the junction (no bend)")
                else:
                    parts.append(f"the {role} leaves the junction {slope_phrase((-b['d'][0], -b['d'][1]), b['ang'])} to the {side_en(s)} edge, where its centre line crosses at {pt2(*b['edge'])}")
        sl_txt = ""
        for sv in dg["slivers"]:
            sl_txt += (f" Between the two bands that meet the {side_en(sv['side'])} edge lies a wedge of solid raised terrain (not floor): {sv['g']} px wide along the edge ({EDGE_DEPTH} px inside it), "
                       f"narrowing inward for about {sv['depth']} px to a point at about {pt2(*sv['tip'])}.")
            if sv["narrow_len"]:
                sl_txt += (f" Where the gap between the two bands is narrower than {SLIVER_NARROW} px (the last {sv['narrow_len']} px before the point, from about {sv['axis']} {sv['narrow_from']}), "
                           "the two facing partitions are merged into ONE single low ridge, and at most one thin line of yarn runs along it; "
                           "the floor width of each passage is kept measured from the inner faces of the partitions.")
        P["P4"] = (
            f"P4. THE JUNCTION. The {n} bands, each {lw} px wide across its centre line, meet and merge at ONE junction at about {pt2(*hub)}, into one continuous flat floor area: "
            + "; ".join(parts) + f".{sl_txt} "
            f"There is no hall, no round room and no wall in this map: the floor is simply the merged bands, flat and empty.")
    # ---- P6〜P12（構造のみ）
    wide = [r for r in m["regions"] if r["wide"]]
    narrow = [r for r in m["regions"] if not r["wide"]]
    reg_names = ", ".join(r["name"] for r in wide) if wide else "none"
    P["P6"] = (
        f"P6. PARTITIONS. Along the passage edges, on the terrain side of the floor outline, run LOW PARTITIONS: narrow low ridges (seen from above as narrow raised borders) "
        f"made of ONE narrow, low band of corrugated cardboard each (no stacking), with paper clay smoothed over its top, which make the passage{pl}. Each partition is only about 12 px wide (in 1672x941: about 10 px) and stands entirely on the terrain side of the floor outline, "
        f"on the boundary where the terrain (brown) face meets the floor; no floor colour appears outside a partition. The clear cream floor between the inner faces of the partitions keeps exactly the width of the cream area of the first image, {lw} px (in 1672x941: about {sx(lw)} px); "
        f"the thickness of a partition is never counted inside the floor width and never eats into it. Outside each partition, on the terrain side along its foot, runs ONE thin edging strand of yarn (cream or pale pink); it lies on the terrain, never on the floor, and is never counted in the floor width. "
        f"There are no doors, door frames or gates, no cave mouths, no round holes or tunnel mouths, no outline of any body: the top of the model is only flat floor, low partitions, yarn edging and decorated terrain.")
    P["P7"] = (
        "P7. THE TERRAIN. The terrain between and around the passage" + pl + " is a thin, flat sheet of paper clay, painted face by face in matte poster paint in flesh skin tone, pale pink and brown-leaning tones, "
        "laid on with a flat brush (brush streaks and uneven coats visible), a different tone for each face. The terrain is the place for the handwork decoration of P9, which stays inside the same warm range of colours (see P8). "
        "It has no thick mounded layers, no stacked flesh-like bands, no striations and no fleshy cross-sections. "
        f"The passage{pl} divide{'' if n > 1 else 's'} the terrain into {len(wide)} wide region{'s' if len(wide) != 1 else ''} ({reg_names})"
        + (f" and {len(narrow)} narrow strip{'s' if len(narrow) != 1 else ''}" if narrow else "") + ".")
    P["P8"] = (f"P8. COLORS: passage floor{pl}: matte poster paint in cream and pale peach, the same range everywhere. "
               "Terrain: matte poster paint in skin tone, pale pink and brown-leaning tones, one tone per face. Partitions: corrugated cardboard strips with paper clay on top, in brown and skin tones. "
               "Decoration: " + COLOR_RULE + " The desk is warm natural wood.")
    wide_n = len(wide)
    narrow_txt = ""
    for sv in dg["slivers"]:
        if sv["narrow_len"]:
            narrow_txt += (f"The narrowest part of the wedge of terrain between the two bands at the {side_en(sv['side'])} edge (the last {sv['narrow_len']} px before its point, "
                           f"from about {sv['axis']} {sv['narrow_from']}) carries only a single strand of yarn along its one low ridge. ")
    if narrow:
        narrow_txt += "Any other narrow strip carries only a thin edging of yarn. "
    dens = (f"each of the {wide_n} wide regions of terrain shows 3 to 5 kinds of small items and patterns, " if wide_n >= 2 else "")
    P["P9"] = (
        "P9. DECORATION (hand-made craft ornament about the human body, placed on the terrain, along the foot of the partitions, on the edge of the base band and on the desk only). "
        "Only small abstract handmade items that belong to the human body: " + "; ".join(f"({k.lower()}) {v[0]}" for k, v in FAMILY.items()) + ". "
        f"DENSITY at kindergarten-craft level, in proportion to the area of the terrain: {dens}the decoration forms at least 6 clusters spread over the terrain, each cluster made of 3 to 5 of these kinds of small items, "
        "so the picture feels rich and busy with handwork. " + narrow_txt +
        "Yarn and threads are short separate strands, swirls and edging: they never run as a net like blood vessels or veins and never look like an organ.")
    P["P11"] = ("P11. THE FLOOR STAYS EMPTY. Nothing of P9 lies on the cream floor, crosses into it or touches it: the floor"
                f"{'s' if n > 1 else ''} stay{'' if n > 1 else 's'} perfectly flat, clean and empty, nothing is placed where the characters walk, and the width of the passage{pl} and the flatness of the floor are exact. "
                "The surfaces of the model are flat floors, walls and decorated terrain only.")
    P["P12"] = ("P12. MATERIALS (every material must be identifiable at full size): base: 5 mm foamboard with the corrugated cardboard cross-section band described in P2; terrain surface: paper clay modelled by hand; "
                "partitions: one low corrugated cardboard strip each under smoothed paper clay; floors and terrain: matte poster paint applied with a flat brush; the joint of the band: masking tape; "
                "decoration (handmade items about the human body): wool yarn, thread, paper-clay balls, buttons, beads, toothpicks, skin-coloured tape, white PVA glue; accents: 6 pieces of red origami paper cut by hand with scissors; desk: wooden tabletop with visible wood grain. "
                "Hand-made roughness: ragged hand-cut paper edges, paint unevenness, visible material seams. Parts look like paper and clay (matte, soft edges), not like real skin, flesh, organs or stone. "
                "It reads as a crude hand-made miniature in which the whole picture is the model, and not as a photograph of a real place.")
    P["P10"] = P["P10"] + " Nothing of P9 is laid over them: they are not a base for ornament."
    apply_deco(P, mid, wide, pl, narrow_txt)  # MAPごとの装飾（マンネリ回避。BDY-02・09 も新プール）
    return P


def apply_deco(P, mid, wide, pl, narrow_txt):
    """MAPごとの装飾（DECO_PICK）を P6〜P10・P12 に反映する。onepass の本文（build_prompt_diag・build_prompt_hall）が共用。"""
    p7t, p8t, p9t, p10a, p12d, dd = deco_texts(mid, [r_["name"] for r_ in wide], len(wide))
    P["P6"] = P["P6"].replace("(cream or pale pink)", f"({dd['yarn']})").replace("terrain (brown) face", "terrain face")
    P["P7"] = P["P7"].replace("painted face by face in matte poster paint in flesh skin tone, pale pink and brown-leaning tones,", f"painted face by face in {p7t},")
    P["P8"] = (f"P8. COLORS: passage floor{pl}: matte poster paint in cream and pale peach, the same range everywhere. " + p8t.replace("Terrain:", "Terrain:", 1)
               + " Partitions: corrugated cardboard strips with paper clay on top, in brown and skin tones.")
    P["P9"] = p9t + narrow_txt + "Yarn and threads are short separate strands, swirls and edging: they never run as a net like blood vessels or veins and never look like an organ."
    P["P10"] = P["P10"] + " " + p10a
    P["P12"] = P["P12"].replace("decoration: wool yarn, paper-clay balls, buttons, beads, felt, toothpicks, white PVA glue;", p12d + ";")
    return dd


def reference_text_diag(n, shape):
    pl = "s" if n > 1 else ""
    return (
        "=== REFERENCE (two attached images, in this order) ===\n"
        "FIRST IMAGE: a flat layout diagram with four plain flat colours and no text. Its colours mean: grey = the desk; ochre-brown band = the base band's edge (P1, P2); "
        f"dusty rose-brown inside the band = the model's top terrain (P7); light cream = the walkable floor of the passage{pl} (P3, P4). "
        f"Copy ONLY the geometry exactly: the nesting of desk, base band (foamboard rim, then corrugated layer) and model top on all four sides, the number of passages ({n}), the model's edge each reaches, the position along that edge, the band width, "
        "the slope of each diagonal band, and its bend, junction or rounded end exactly as in P4. "
        "Treat the cream area as the clear floor width: the partitions stand in the terrain area next to it, never inside the cream. "
        "Repaint everything as the hand-made miniature described above. Do NOT carry over the diagram's four flat colours as flat fills (the desk is a warm wooden tabletop, the base band is foamboard and corrugated cardboard, "
        "there is no flat brown area anywhere in the result) or its perfectly straight, hard edges.\n"
        "SECOND IMAGE: a thin close-up strip of the front edge of a hand-made cardboard miniature base. Take from it ONLY the feel of three materials, to be used for the base band of P2: "
        "the exposed corrugated cardboard cross-section (the wavy flute layer along the top of the strip), the masking tape, and the ragged torn paper edge. "
        "Take no content from it, and ignore the few white cotton fibres at its top edge and its brown colour. "
        "The decoration of P9 is described by the text only: no attached image carries any decoration to copy.")


def checks_diag(mid, m, dg):
    M, lw = m["M"], m["lw"]
    shape = dg["shape"]
    n = sum(len(v) for v in m["edges"].values())
    out = []
    out.append("寸法（`file` / `identify` で実ファイルを測る。prompt指定・ファイル名は証拠にならない）:\n- [ ] 1920x1080、または 1672x941（その場合は座標に0.871を掛けて比較）。それ以外は failed。リサイズ・切り抜きで通さない。")
    out.append(f"構図（割付図 `verification/body-layout/clean/{mid}.png` と実画素・目視で比較）:\n"
               f"- [ ] 机（木目の木の机）が四辺に約{M['desk']}px見える。その内側に約{M['band']}px幅の土台縁の帯（外{M['foam']}px foamboard・内{M['corr']}px corrugated 断面）が**四辺すべて（北・南・西・東）**で途切れず見える（北辺・南辺も西辺・東辺と同じ幅で、机→縁取り→波形→天面の順）。模型の天面は画像の内側に収まり画像の縁に接しない。天面は x{M['mx0']}–{M['mx1']}・y{M['my0']}–{M['my1']} 付近。\n"
               f"- [ ] 通路が模型の縁（土台縁の帯の内側）に届く。画像端（机の外）に通路が出ていない。床は模型の外に一画素も無い。")
    pas = [f"- [ ] 通路は**{n}本**。"]
    for s in "NESW":
        for e in m["edges"][s]:
            ax = "x" if s in "NS" else "y"
            f = sx if ax == "x" else sy
            bi = dg["by_port"][e["port"]]
            pas.append(f"- [ ] {s}辺 {e['port']}: 縁から{EDGE_DEPTH}px内側で {ax} {e['a']}–{e['b']}（1672: {ax} {f(e['a'])}–{f(e['b'])}）。中心線が縁と交わる点 {bi['edge']}、帯の幅（帯に直角に測る）約{lw}px（1672: 約{sx(lw)}px）、水平から約{bi['ang']:.1f}度。")
    pas.append("- [ ] 他の縁の区間には床が出ていない。遷移範囲の印（色帯・矢印・線・文字）が絵に無い。")
    out.append("通路:\n" + "\n".join(pas))
    g = []
    if shape == "stub":
        cap = dg["caps"][0]
        g.append(f"- [ ] 経路は縁から斜めの**直線1本**（折れ・分岐なし）で、末端は閉じた半円（半径{lw // 2}px、中心 {cap['centre']}、最奥 {cap['far']}）。扉・穴・物・第2の道が無い。広間・壁が無い。")
        if mid == "BDY-01":
            g.append("- [ ] 口は役割名だけ: 唇・歯・舌・キスの造形が無い。")
    elif shape == "through":
        g.append(f"- [ ] 経路は辺から辺への斜めの**直線1本**（水平から約{dg['angs'][0]:.1f}度、折れ・分岐なし）。広間・壁が無い。")
    elif shape == "knee":
        g.append(f"- [ ] 経路は**折れ点1つ**: 第1区間 水平から約{dg['angs'][0]:.1f}度 → 折れ点 {dg['knees'][0]} → 第2区間 約{dg['angs'][1]:.1f}度。曲がりは約{dg['turn']:.0f}度の鈍角（内角約{180 - dg['turn']:.0f}度）で、急な曲がりでない。外側の角は丸く、内側は鋭い。2つ目の折れ・分岐が無い。")
    else:
        g.append(f"- [ ] 4本が1つの合流点 {dg['hub']} で合わさる。北の帯は垂直、他の3本は斜め（水平から約" + "・".join(f"{a:.1f}" for a in dg["angs"][1:]) + "度）。広間・壁が無い。")
        for sv in dg["slivers"]:
            g.append(f"- [ ] {sv['side']}辺の2本の間に地形のくさび（縁で幅約{sv['g']}px、奥へ約{sv['depth']}px、先端 {sv['tip']}）が残り、床になっていない。幅{SLIVER_NARROW}px未満の先端側{sv['narrow_len']}px（{sv['axis']} {sv['narrow_from']} から先）は仕切りが1本の低い尾根に合わさり、毛糸は1本まで。")
    out.append("経路の形（本命の検査。割付図の実測値）:\n" + "\n".join(g))
    out.append("材料・質感・装飾（装飾込み1回生成）:\n"
               "- [ ] ① 土台縁の帯に corrugated cardboard 断面と foamboard の縁 ② 仕切りが細く低い corrugated の帯1本（幅約12px）＋毛糸の縁取り1本（床の幅に含まれない）\n"
               "- [ ] ③ 地形が paper clay の面で、肌色・薄桃・茶系の matte poster paint ④ 赤い折り紙の切片が**ちょうど6枚**（数えて6枚・7枚目なし。全て模型の中の地形の上。模型の外・机・床・土台縁の帯には無い。装飾の下敷きでない）\n"
               "- [ ] ⑤ 机が木目の木の机\n"
               "- [ ] ⑥ 装飾は人体に関係する抽象的な工作物だけ: 骨(両端に玉の小さな骨)・細胞や粒(粘土玉・ビーズ・ボタン)・筋肉や神経の糸(毛糸の束や渦。網状でない)・鼓動のぎざぎざ線・皮膚の彫り(指紋の渦・毛穴・しわ)・ばんそうこう(肌色テープの十字)・毛(糸の房)・ばい菌(とげのある粘土玉)。少なくとも6か所の塊・各塊3〜5種。花・葉・雲・星・旗・柵・ハート形・動物・食べ物・風景・臓器の形・血管の網が無い\n"
               "- [ ] ⑥b 装飾の色が肌色・薄桃・クリーム・茶系・象牙色の範囲（緑・青・黄・紫・オレンジが無い）。赤は折り紙6枚だけ\n"
               "- [ ] ⑦ 床（クリームの通路）には何も置かれず平ら。毛糸が血管・臓器に見える走り方をしていない")
    out.append("許容差（レビュー側基準。生成入力には入れない）: 通路位置 ±25px、幅 ±10%（1672x941 の場合は ×0.871）。床マスクIoU（clean 割付図に対して）≥0.95 を目安。")
    return "\n\n".join(out)


def report_diag(mid, m, dg):
    L = [f"- 経路の形: {dg['shape']}（stub=末端の丸い閉じた端 / through=辺から辺の1本 / knee=折れ点1つ / junction=4本合流）。広間: なし（割付図に壁の画素なし）。"]
    L.append("- 斜めの帯の中心線（clean 画素から、帯に直角な床の連続区間の中点列を直線に当てた実測。body_layout の折れ線と角度1.5度・位置4px以内で一致を確認）: "
             + "; ".join(f"区間{k + 1} 水平から{sg['fit']['ang']:.2f}度（直線残差 最大{sg['fit']['resid']:.2f}px、帯幅{sg['fit']['w']:.0f}px）" for k, sg in enumerate(dg["segs"])) + "。")
    for p, bi in dg["by_port"].items():
        L.append(f"- {p}: 中心線が{bi['side']}辺と交わる点 {pt2(*bi['edge'])}。")
    for c in dg["caps"]:
        L.append(f"- 末端の丸い端: 中心 {pt2(*c['centre'])}（実測を5px刻みに丸め）、最奥 {pt2(*c['far'])}、半径{m['lw'] // 2}px。")
    for k in dg["knees"]:
        L.append(f"- 折れ点: {pt2(*k)}、曲がり {dg['turn']:.1f}度（内角{180 - dg['turn']:.1f}度）。")
    if dg["hub"]:
        L.append(f"- 合流点: {pt2(*dg['hub'])}（4本の中心線の最小二乗の交点を5px刻みに丸め）。")
    for sv in dg["slivers"]:
        L.append(f"- {sv['side']}辺の2本の間の地形のくさび: 縁（{EDGE_DEPTH}px内側）で幅{sv['g']}px、奥行き約{sv['depth']}px、先端 {sv['tip']}。幅{SLIVER_NARROW}px未満になる先端側 {sv['narrow_len']}px（{sv['axis']} {sv['narrow_from']} から先）。")
    return "\n".join(L)


# ---------------------------------------------------------------------------
# BDY-02 専用（広間・首・分岐）。採用時（docs/production/20261022-bdy02-adoption-prompts/BDY-02-stage1-prompt-send.txt）に構造の記述が
# 成功した文を保ち、座標・角度は clean 割付図の画素から実測し直す（別コードの照合: verification/body-layout/remeasure_bdy02.py）。
# 装飾・色・赤紙6枚・四辺の土台縁・床の幅を守る壁の語は、他MAPの onepass と同じ共通部品（P1/P2/P10/P13/P14 と apply_deco）。
# ---------------------------------------------------------------------------
def _shift4(mask):
    """4近傍のどれかに mask が True の画素。"""
    s = np.zeros_like(mask)
    s[1:] |= mask[:-1]
    s[:-1] |= mask[1:]
    s[:, 1:] |= mask[:, :-1]
    s[:, :-1] |= mask[:, 1:]
    return s


def _fit_ellipse_axis(x, y, c0):
    """軸平行の楕円 A u²+C v²+D u+E v=1（u,v=座標-c0）の代数的当てはめ。戻り値 (cx, cy, rx, ry)。"""
    u, v = x - c0[0], y - c0[1]
    A = np.c_[u * u, v * v, u, v]
    a_, c_, d_, e_ = np.linalg.lstsq(A, np.ones(len(u)), rcond=None)[0]
    cu, cv = -d_ / (2 * a_), -e_ / (2 * c_)
    R = 1 + d_ * d_ / (4 * a_) + e_ * e_ / (4 * c_)
    return c0[0] + cu, c0[1] + cv, math.sqrt(R / a_), math.sqrt(R / c_)


def _ellipse_trimmed(x, y, seed, win=8.0, trim=2.0, iters=4):
    """seed=(cx,cy,rx,ry) の近く（±win px）の境界画素から楕円を当て、残差 trim px 超の外れ（帯が壁に接する所の端の画素）を捨てて当て直す。"""
    cx, cy, rx, ry = seed
    keep = np.ones(len(x), bool)

    def res(p):
        return (np.hypot((x - p[0]) / p[2], (y - p[1]) / p[3]) - 1) * min(p[2], p[3])
    keep = np.abs(res(seed)) < win
    p = seed
    for _ in range(iters):
        p = _fit_ellipse_axis(x[keep], y[keep], (seed[0], seed[1]))
        keep = np.abs(res(p)) < trim
    return p, int(keep.sum())


def _label_wall(mask):
    """壁色画素の4連結成分（全解像度）。戻り値: [(画素数, xs, ys)] 画素数の多い順。"""
    ys, xs = np.nonzero(mask)
    pts = set(zip(xs.tolist(), ys.tolist()))
    out = []
    while pts:
        p0 = pts.pop()
        q, cx_, cy_ = [p0], [p0[0]], [p0[1]]
        while q:
            x, y = q.pop()
            for nb in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if nb in pts:
                    pts.remove(nb)
                    q.append(nb)
                    cx_.append(nb[0])
                    cy_.append(nb[1])
        out.append((len(cx_), np.array(cx_), np.array(cy_)))
    return sorted(out, key=lambda t: -t[0])


def _lower_edge_line(fl, xs, ylo, yhi):
    """列 xs ごとに、床の最下端（ylo〜yhi の範囲）を拾い、y = k x + c の直線に当てる。戻り値 (k, c, 点数, 最大残差)。"""
    pts = []
    for x in xs:
        idx = np.nonzero(fl[ylo:yhi, x])[0]
        if len(idx):
            pts.append((x, ylo + idx.max() + 0.5))
    if len(pts) < 20:
        die(f"BDY-02: 斜めの帯の下縁の画素が少なすぎる（{len(pts)}列）")
    P = np.array(pts, float)
    k, c = np.polyfit(P[:, 0], P[:, 1], 1)
    return float(k), float(c), len(pts), float(np.abs(P[:, 1] - (k * P[:, 0] + c)).max())


def measure_hall(m, bl):
    """BDY-02 の clean 割付図から、広間（楕円の床の中心・半径・壁の厚み・壁の弧の方位）・首・分岐点・口の帯・5本の帯の斜めを画素で実測する。
    body_layout.py の定数・折れ線は『種』と突き合わせだけに使い（角度1.5度・位置/半径3px 以内。食い違えば停止）、本文に書く値は画素実測が正本。"""
    M, lw, fl, terr = m["M"], m["lw"], m["floor"], m["terr"]
    a = np.asarray(Image.open(CLEAN_DIR / "BDY-02.png").convert("RGB"))
    wall = np.all(a == np.array(C_WALL), axis=2)
    (hcx, hcy), hry = bl.BDY02_HALL
    hrx = bl.BDY02_HALL_RX
    # ---- 楕円: 壁の外縁（地形に接する壁画素）と内縁（床に接する壁画素）
    oy, ox = np.nonzero(wall & _shift4(terr))
    iy, ix = np.nonzero(wall & _shift4(fl))
    po, no = _ellipse_trimmed(ox.astype(float), oy.astype(float), (hcx, hcy, hrx + bl.WALL_T, hry + bl.WALL_T))
    pi_, ni = _ellipse_trimmed(ix.astype(float), iy.astype(float), (hcx, hcy, hrx, hry))
    if min(no, ni) < 150:
        die(f"BDY-02: 広間の壁の縁の画素が少なすぎる（外{no}・内{ni}）")
    cx, cy = r5((po[0] + pi_[0]) / 2), r5((po[1] + pi_[1]) / 2)
    rx, ry = r5(pi_[2]), r5(pi_[3])
    wt = int(round(((po[2] - pi_[2]) + (po[3] - pi_[3])) / 2 + 1))  # 境界画素の中心は縁から0.5pxずつ内側なので +1
    if (cx, cy, rx, ry, wt) != (hcx, hcy, hrx, hry, bl.WALL_T):
        die(f"BDY-02: 広間の画素実測 中心({cx},{cy}) 半径({rx},{ry}) 壁厚{wt} が body_layout の ({hcx},{hcy}) ({hrx},{hry}) {bl.WALL_T} と不一致")
    # ---- 壁の弧: 4連結成分と、広間の中心から見た方位（北から時計回り）・外接枠
    arcs = []
    for n_, xs_, ys_ in _label_wall(wall):
        if n_ < 200:
            continue
        b_ = np.degrees(np.arctan2(xs_ - cx, -(ys_ - cy))) % 360
        if b_.max() - b_.min() > 180:
            b_ = np.where(b_ > 180, b_ - 360, b_)
        b0, b1 = float(b_.min()) % 360, float(b_.max()) % 360
        mid_b = ((b0 + b1) / 2) % 360 if b1 >= b0 else ((b0 + b1 + 360) / 2) % 360
        name = ("upper right" if mid_b < 90 else "lower right" if mid_b < 180 else "lower left" if mid_b < 270 else "upper left")
        arcs.append(dict(name=name, b0=int(round(b0)), b1=int(round(b1)), x0=int(xs_.min()), x1=int(xs_.max()), y0=int(ys_.min()), y1=int(ys_.max())))
    arcs.sort(key=lambda t: t["b0"])
    # ---- 首: 分岐点より下〜広間の上の行で、x=cx を含む床の連続区間が全行で同じ1本
    ports = {e["port"]: (s, e) for s in "NESW" for e in m["edges"][s]}
    head, mouth = ports["door-passage-head"][1], ports["door-passage-mouth"][1]
    jy_seed = int(bl.BDY02_J[1])
    runs = set()
    for y in range(jy_seed + 100, cy - ry - 10):
        for r0, r1 in runs_of(fl[y, M["mx0"]:M["mx1"]]):
            if r0 + M["mx0"] <= cx <= r1 + M["mx0"]:
                runs.add((r0 + M["mx0"], r1 + M["mx0"]))
    if len(runs) != 1:
        die(f"BDY-02: 首の床の区間が行ごとに一定でない {sorted(runs)}")
    nk0, nk1 = next(iter(runs))
    if (nk0, nk1) != (head["a"], head["b"]):
        die(f"BDY-02: 首の x 区間 {nk0}-{nk1} が頭の通路 {head['a']}-{head['b']} と違う（頭と首は同じ x 区間）")
    ncx = (nk0 + nk1) / 2
    # ---- 口の帯の斜め（分岐点 J → K）: 帯に直角な床の連続区間の中点列の直線当て（他MAPの斜めの帯と同じ方法）
    mpoly = mouth["poly"]
    fm = fit_centre(fl, mpoly[0], mpoly[1], lw, 0.6 * lw, 0.6 * lw)
    ang_m = math.degrees(math.atan2(abs(fm["d"][1]), abs(fm["d"][0])))
    ang_l = math.degrees(math.atan2(abs(mpoly[1][1] - mpoly[0][1]), abs(mpoly[1][0] - mpoly[0][0])))
    if abs(ang_m - ang_l) > 1.5:
        die(f"BDY-02: 口の帯の角度 画素実測{ang_m:.1f}度 が body_layout {ang_l:.1f}度 と不一致")
    mcx = (mouth["a"] + mouth["b"]) / 2

    def y_on_mouth(x):  # 口の帯の中心線の y（右上がり: x が増えると y が減る）
        return fm["pt"][1] + (x - fm["pt"][0]) * (fm["d"][1] / fm["d"][0])
    jy = r5(y_on_mouth(ncx))
    ky = r5(y_on_mouth(mcx))
    if abs(jy - bl.BDY02_J[1]) > 3 or abs(ky - bl.BDY02_K_Y) > 3:
        die(f"BDY-02: 分岐点 y {jy}・口の折れ y {ky} が body_layout ({bl.BDY02_J[1]}, {bl.BDY02_K_Y}) と不一致")
    # 首の東縁の開口（口の帯が首に開く縦の範囲）
    col = fl[:, nk1 + 2]
    op0 = op1 = None
    for r0, r1 in runs_of(col[M["my0"] + 2: jy + 100]):
        if r0 + M["my0"] + 2 <= jy <= r1 + M["my0"] + 2:
            op0, op1 = r0 + M["my0"] + 2, r1 + M["my0"] + 2
    if op0 is None:
        die("BDY-02: 首の東縁に口の帯の開口が見つからない")
    # 頭と口の間の地形のくさび
    wx0, wx1 = head["b"] + 1, mouth["a"] - 1
    wy_tip = None
    for y in range(M["my0"] + EDGE_DEPTH, M["my0"] + 120):
        if fl[y, wx0]:
            wy_tip = y
            break
    if wy_tip is None:
        die("BDY-02: 頭と口の間の地形のくさびの先端が見つからない")
    # ---- 5本の帯の斜め
    arms = {}
    for p_, (s_, e_) in ports.items():
        poly = e_["poly"]
        if p_ in ("door-passage-head", "door-passage-mouth", "door-passage-lower"):
            continue
        p1, p2 = poly[1], poly[2]
        ang_l = math.degrees(math.atan2(abs(p2[1] - p1[1]), abs(p2[0] - p1[0])))
        dx, dy = p2[0] - p1[0], p2[1] - p1[1]
        if p_ in ("door-passage-right-arm", "door-passage-left-arm"):
            f = fit_centre(fl, p1, p2, lw, 0.6 * lw, 0.6 * lw)
            ang = math.degrees(math.atan2(abs(f["d"][1]), abs(f["d"][0])))
            yc = (e_["a"] + e_["b"]) / 2  # 辺から水平に入る区間の中心線の y
            x_turn = f["pt"][0] + (yc - f["pt"][1]) * (f["d"][0] / f["d"][1])
            turn = ("x", r5(x_turn))
        else:  # 肺・心臓: 斜めの区間が短く、床の幅に合う走査が取れない。下縁（細い側）の直線から中心線を出す
            xc = (e_["a"] + e_["b"]) / 2
            if dx > 0:  # 肺: 縦の帯の東縁の外側へ下縁が伸びる
                xs = range(int(xc + lw / 2) + 6, int(xc + lw / 2) + 60)
            else:  # 心臓: 縦の帯の西縁の外側へ
                xs = range(int(xc - lw / 2) - 60, int(xc - lw / 2) - 6)
            k, c, npts, resid = _lower_edge_line(fl, xs, int(p1[1]) + 40, M["my1"])
            ang = math.degrees(math.atan(abs(k)))
            yc_line = lambda x: k * x + c - (lw / 2) / math.cos(math.radians(ang))  # 下縁から帯の中心線へ（斜めに lw/2）
            turn = ("y", r5(yc_line(xc)))
        if abs(ang - ang_l) > 1.5:
            die(f"BDY-02: {p_} の斜めの角度 画素実測{ang:.1f}度 が body_layout {ang_l:.1f}度 と不一致")
        t_seed = p1[0] if turn[0] == "x" else p1[1]
        if abs(turn[1] - t_seed) > 5:
            die(f"BDY-02: {p_} の折れ位置 画素実測 {turn} が body_layout {p1} と不一致")
        arms[p_] = dict(ang=ang, turn=turn, down=dy > 0, right=dx > 0)
    return dict(c=(cx, cy), rx=rx, ry=ry, wt=wt, arcs=arcs, neck=(nk0, nk1), jy=jy, ky=ky, mouth_ang=ang_m, opening=(op0, op1),
                wedge=(wx0, wx1, wy_tip), arms=arms)


def _slope_in(down, right, ang):
    return f"sloping {'down' if down else 'up'} and to the {'right' if right else 'left'} at about {ang:.1f} degrees {'below' if down else 'above'} horizontal"


def build_prompt_hall(mid, m, hd, bl):
    """BDY-02 の onepass 本文（P1〜P14）。P3〜P6 は採用時（段階1）に成功した構造の文を保ち、座標は measure_hall の実測。
    装飾（P9）・色・赤紙6枚・四辺の土台縁・床の幅を守る細い壁は、他MAPと同じ共通部品。"""
    base, _ = build_prompt(mid, m, bl)
    M, lw = m["M"], m["lw"]
    tw = M["mx1"] - M["mx0"]
    P = dict(base)
    cx, cy, rx, ry, wt = hd["c"][0], hd["c"][1], hd["rx"], hd["ry"], hd["wt"]
    nk0, nk1 = hd["neck"]
    jy, ky = hd["jy"], hd["ky"]
    arm = hd["arms"]
    ports = {e["port"]: (s, e) for s in "NESW" for e in m["edges"][s]}
    mouth = ports["door-passage-mouth"][1]
    mcx = (mouth["a"] + mouth["b"]) // 2
    desc = {
        "door-passage-head": "running straight down into the neck of P5",
        "door-passage-mouth": f"running straight down to about y {ky} (in 1672x941: y {sy(ky)}), then {_slope_in(True, False, hd['mouth_ang'])} into the neck of P5",
        "door-passage-lower": "running straight up into the hall",
    }
    for p_, a_ in arm.items():
        sd = ports[p_][0]
        lead = {"W": "to the right", "E": "to the left", "S": "up"}[sd]
        t_ax, t_v = a_["turn"]
        at = f"about {t_ax} {t_v} (in 1672x941: {t_ax} {(sx if t_ax == 'x' else sy)(t_v)})"
        into = "into the hall of P4" if sd in "WE" else "into the hall"
        desc[p_] = f"running straight {lead} to {at}, then {_slope_in(a_['down'], a_['right'], a_['ang'])} {into}; the outer corner of that bend is rounded, radius {lw // 2} px"
    sides_txt = []
    for s in "NESW":
        es = m["edges"][s]
        if not es:
            continue
        ax = "x" if s in "NS" else "y"
        edge_c = {"N": f"y {M['my0']}", "S": f"y {M['my1']}", "W": f"x {M['mx0']}", "E": f"x {M['mx1']}"}[s]
        items = [f"{e['role']} at {rng(ax, e['a'], e['b'])} ({desc[e['port']]})" for e in es]
        sides_txt.append(f"  - {SIDE_EN[s]}, {edge_c}), {len(es)} passage{'s' if len(es) > 1 else ''}: " + "; ".join(items) + ".")
    P["P3"] = (
        f"P3. THE SEVEN PASSAGES AND THE MODEL'S EDGE. The model's top surface is made of thin flat paper-clay surfaces. Seven flat floor bands, each {lw} px wide measured across the band ({lw / tw:.2f} of the model's width of {tw} px, "
        f"which is {sx(lw)} px in the 1672x941 frame; a stand-in for three characters side by side; no character is drawn), each reach the model's edge and stop flush against the inner edge of the corrugated band of P2: "
        f"the floor band ends where the model ends, at the band, and never continues onto the band, the desk or the frame edge (each leads on to the next map across the model's edge; the character stands anywhere within a stretch of the edge to cross over, "
        f"so nothing marks a crossing point). No marker, coloured zone, arrow, line or label of any kind is drawn at the edges. "
        f"The person whose body this is lies on their back and is seen from the front, so the picture's left (west) is that person's right side and the picture's right (east) is that person's left side. "
        f"Positions where each band meets the model's edge, in the 1920x1080 frame, measured from the layout diagram (first image):\n" + "\n".join(sides_txt) + "\n"
        f"  Along every other stretch of the model's four edges, the edge is solid raised paper-clay terrain meeting the corrugated band: the floor bands are the only floor that reaches the model's edge, 7 in all. "
        f"The heart passage and the lung passage are plain floor bands like the others: nothing but floor is drawn at them or beyond them.")
    arcs_txt = "; ".join(f"{a_['name']} arc: bearing {a_['b0']} to {a_['b1']} degrees (x {a_['x0']} to {a_['x1']}, y {a_['y0']} to {a_['y1']}; in 1672x941: x {sx(a_['x0'])} to {sx(a_['x1'])}, y {sy(a_['y0'])} to {sy(a_['y1'])})" for a_ in hd["arcs"])
    P["P4"] = (
        f"P4. THE HALL. In the lower middle of the model lies an open hall: a wide oval FLOOR of flat paper clay, wider than it is tall, centred at ({cx}, {cy}) (in 1672x941: ({sx(cx)}, {sy(cy)})), "
        f"horizontal radius {rx} px and vertical radius {ry} px (it spans x {cx - rx} to {cx + rx} and y {cy - ry} to {cy + ry}: {2 * rx} px wide and {2 * ry} px tall), perfectly level and flat, level with the passage floors, "
        f"and the same plain floor (same cream and pale peach, no new colour). The hall floor is open and empty from edge to edge: nothing rises from it and nothing lies on it. "
        f"Along four stretches of the oval's outline (listed below) stands a thin low paper-clay WALL, {wt} px thick, standing OUTSIDE the floor oval, on the terrain side, never on the floor; "
        f"everywhere else along the oval there is no wall and the floor continues into the passages. "
        f"The wall is ONE low band of corrugated cardboard (the same build as the partitions of P6, here {wt} px wide) with paper clay smoothed over its top, in the brown of corrugated cardboard, "
        f"with ONE strand of yarn along its outer foot as its edging; in the first image the blue-grey arcs only mark where the wall stands, and the wall itself is cardboard brown. "
        f"The wall is visible in {len(hd['arcs'])} arcs only, at these bearings measured clockwise from north around the hall's centre: {arcs_txt}. "
        f"On every other part of the oval's outline, one of the passage floors joins the hall floor with its full width and the floor carries on without a wall: six floor bands meet the hall, namely the neck of P5 on the north side, "
        f"the right-arm passage on the west, the left-arm passage on the east, and the lung, lower-body and heart passages on the south. "
        f"The hall floor is measured to the inner face of the wall arcs: the cream area of the first image is the clear floor width, so the oval keeps its full {2 * rx} x {2 * ry} px, however the wall is made. "
        f"The wall never reduces the floor: it is a thin band, and it never thickens. The hall floor is plain, bare, flat floor.")
    op0, op1 = hd["opening"]
    wx0, wx1, wy = hd["wedge"]
    kx = mcx
    ang_m = hd["mouth_ang"]
    P["P5"] = (
        f"P5. THE NECK AND ITS BRANCH. From the north side of the hall, ONE single neck band {lw} px wide (x {nk0} to {nk1}, the same x range as the head passage) runs due north: exactly vertical, with no bend. "
        f"Its lower end opens into the hall's northern edge at about ({cx}, {cy - ry}) (in 1672x941: ({sx(cx)}, {sy(cy - ry)})). Its length from the hall to the branch point is about {cy - ry - jy} px. "
        f"At the branch point, about ({cx}, {jy}) (in 1672x941: ({sx(cx)}, {sy(jy)})), the neck divides, in one single fork, into exactly two bands: "
        f"(a) the head band keeps going due north at the same x range, x {nk0} to {nk1}, up to the model's north edge at y {M['my0']}, where it is the head passage of P3; "
        f"(b) the mouth band leaves the neck's east side: its centre line runs from the branch point up and to the right at {ang_m:.1f} degrees above horizontal to about ({kx}, {ky}) (in 1672x941: ({sx(kx)}, {sy(ky)})), "
        f"where the band turns with a rounded outer corner (radius {lw // 2} px) and runs straight up to the north edge at x {mouth['a']} to {mouth['b']} (in 1672x941: x {sx(mouth['a'])} to {sx(mouth['b'])}), where it is the mouth passage of P3. "
        f"At the neck's east edge the opening of the mouth band spans y {op0} to {op1} (measured vertically): the lower edge of the mouth band meets the neck's east edge at about y {op1}. "
        f"Between the head band and the mouth band at the north edge lies a small wedge of solid terrain (x {wx0} to {wx1} at the north edge) that narrows to a point at about y {wy} where the two bands part from the neck. "
        f"Below the branch point there is the neck alone: no second band runs beside it, and its west edge is one straight vertical line (x {nk0}) from the north edge all the way down to the hall. "
        f"Read from the hall northward, the route is: the hall, one neck, one fork, then the head band due north and the mouth band to the upper right. "
        f"The mouth and the head are story role names only: each is a plain floor band, and nothing but floor bands is drawn there.")
    n = 7
    pl = "s"
    wide = [r for r in m["regions"] if r["wide"]]
    narrow = [r for r in m["regions"] if not r["wide"]]
    reg_names = ", ".join(r["name"] for r in wide)
    P["P6"] = (
        f"P6. PARTITIONS AND THE HALL WALL. Along the passage edges, on the terrain side of the floor outline, run LOW PARTITIONS: narrow low ridges (seen from above as narrow raised borders) "
        f"made of ONE narrow, low band of corrugated cardboard each (no stacking), with paper clay smoothed over its top, which make the passages. Each partition is only about 12 px wide (in 1672x941: about 10 px) and stands entirely on the terrain side of the floor outline, "
        f"on the boundary where the terrain face meets the floor; no floor colour appears outside a partition. The clear cream floor between the inner faces of the partitions keeps exactly the width of the cream area of the first image, {lw} px (in 1672x941: about {sx(lw)} px); "
        f"the thickness of a partition is never counted inside the floor width and never eats into it. The hall's wall arcs of P4 are built the same way: ONE low corrugated cardboard band, {wt} px wide, in cardboard brown, standing outside the floor oval. "
        f"Outside each partition and each wall arc, on the terrain side along its foot, runs ONE thin edging strand of yarn (cream or pale pink); it lies on the terrain, never on the floor, and is never counted in the floor width. "
        f"There are no doors, door frames or gates, no cave mouths, no round holes or tunnel mouths: the top of the model is only flat floors, an open oval hall with its thin wall arcs, low partitions, yarn edging and decorated terrain.")
    P["P7"] = (
        "P7. THE TERRAIN. The terrain between and around the passages is a thin, flat sheet of paper clay, painted face by face in matte poster paint in flesh skin tone, pale pink and brown-leaning tones, "
        "laid on with a flat brush (brush streaks and uneven coats visible), a different tone for each face. The terrain is the place for the handwork decoration of P9, which stays inside the same warm range of colours (see P8). "
        "It has no thick mounded layers, no stacked flesh-like bands, no striations and no fleshy cross-sections. "
        f"The passages and the hall divide the terrain into {len(wide)} wide regions ({reg_names}) and {len(narrow)} narrow strips and wedges.")
    P["P8"] = ""  # apply_deco が置き換える
    P["P9"] = ""  # 同上
    P["P11"] = ("P11. THE FLOOR STAYS EMPTY. Nothing of P9 lies on the cream floor, crosses into it or touches it: the floors and the hall floor stay perfectly flat, clean and empty, nothing is placed where the characters walk, "
                "and the width of the passages, the shape of the hall and the flatness of the floor are exact. The surfaces of the model are flat floors, walls and decorated terrain only.")
    P["P12"] = ("P12. MATERIALS (every material must be identifiable at full size): base: 5 mm foamboard with the corrugated cardboard cross-section band described in P2; terrain surface: paper clay modelled by hand; "
                "partitions and the hall wall: one narrow low corrugated cardboard band each under smoothed paper clay, with one strand of yarn along the foot; floors and terrain: matte poster paint applied with a flat brush; the joint of the band: masking tape; "
                "decoration (handmade items about the human body): wool yarn, thread, paper-clay balls, buttons, beads, toothpicks, skin-coloured tape, white PVA glue; accents: 6 pieces of red origami paper cut by hand with scissors; desk: wooden tabletop with visible wood grain. "
                "Hand-made roughness: ragged hand-cut paper edges, paint unevenness, visible material seams. Parts look like paper and clay (matte, soft edges), not like real skin, flesh, organs or stone. "
                "It reads as a crude hand-made miniature in which the whole picture is the model, and not as a photograph of a real place.")
    # 装飾（P9）・色（P8）・赤紙の置き方（P10）は他MAPと同じ共通部品
    P["P10"] = P["P10"].replace("(not on the partitions,", "(not on the partitions, not on the hall wall,") + " Nothing of P9 is laid over them: they are not a base for ornament."
    narrow_txt = ("The narrow strips and wedges (such as the wedge between the head band and the mouth band) carry only a thin edging of yarn. ")
    dd = apply_deco(P, mid, wide, pl, narrow_txt)
    P["P9"] = P["P9"].replace("along the foot of the partitions,", "along the foot of the partitions and of the hall wall arcs,")
    bdy02_override(P, mid, M, wide, dd)
    return P


def reference_text_hall():
    return (
        "=== REFERENCE (two attached images, in this order) ===\n"
        "FIRST IMAGE: a flat layout diagram with five plain flat colours and no text. Its colours mean: grey = the desk; ochre-brown band = the base band's edge (P1, P2); "
        "dusty rose-brown inside the band = the model's top terrain (P7); light cream = the walkable floor of the seven passages and of the hall (P3, P4, P5); blue-grey arcs = the places where the hall's wall stands (P4), standing outside the cream floor oval. "
        "Copy ONLY the geometry exactly: the nesting of desk, base band (foamboard rim, then corrugated layer) and model top on all four sides, the number of passages (7), the model's edge each reaches, the position along that edge, the band width, "
        "the outline of each band including its slopes and bends, the single vertical neck and its fork into the head band and the mouth band, and the hall's centre, floor oval and wall arcs. "
        "Treat the cream area as the clear floor width: the walls and partitions stand in the terrain area next to it, never inside the cream. "
        "Repaint everything as the hand-made miniature described above: the wall arcs become thin cardboard-brown walls (P4). Do NOT carry over the diagram's five flat colours as flat fills (the desk is a warm wooden tabletop, the base band is foamboard and corrugated cardboard, "
        "there is no flat brown area anywhere in the result, and no blue-grey) or its perfectly straight, hard edges.\n"
        "SECOND IMAGE: a thin close-up strip of the front edge of a hand-made cardboard miniature base. Take from it ONLY the feel of three materials, to be used for the base band of P2: "
        "the exposed corrugated cardboard cross-section (the wavy flute layer along the top of the strip), the masking tape, and the ragged torn paper edge. "
        "Take no content from it, and ignore the few white cotton fibres at its top edge and its brown colour. "
        "The decoration of P9 is described by the text only: no attached image carries any decoration to copy.")


def report_hall(m, hd):
    L = [f"- 経路の形: 広間（横長の楕円の床。壁は細い arc）→ 首1本 → 分岐点 → 頭・口。広間: 中心 {hd['c']}・横半径{hd['rx']}・縦半径{hd['ry']}・壁厚{hd['wt']}（clean の壁色画素に楕円を当てた実測。body_layout の定数と一致を確認）。",
         "- 壁の弧: " + "; ".join(f"{a['name']} 方位{a['b0']}–{a['b1']}度 x{a['x0']}–{a['x1']} y{a['y0']}–{a['y1']}" for a in hd["arcs"]) + "。",
         f"- 首: 行ごとの床の区間が x {hd['neck'][0]}–{hd['neck'][1]} の1本（頭の通路と同じ x 区間）。分岐点 y {hd['jy']}（口の帯の中心線が x=首の中心を通る高さ）。口の帯 水平から{hd['mouth_ang']:.2f}度、折れ y {hd['ky']}。首の東縁の開口 y {hd['opening'][0]}–{hd['opening'][1]}。頭と口の間のくさびの先端 y {hd['wedge'][2]}。"]
    for p, a in hd["arms"].items():
        L.append(f"- {p}: 斜め{a['ang']:.2f}度、折れ位置 {a['turn'][0]} {a['turn'][1]}。")
    return "\n".join(L)


def checks_hall(mid, m, hd):
    M, lw = m["M"], m["lw"]
    out = []
    out.append("寸法（`file` / `identify` で実ファイルを測る。prompt指定・ファイル名は証拠にならない）:\n- [ ] 1920x1080、または 1672x941（その場合は座標に0.871を掛けて比較）。それ以外は failed。リサイズ・切り抜きで通さない。")
    out.append(f"構図（割付図 `verification/body-layout/clean/{mid}.png` と実画素・目視で比較）:\n"
               f"- [ ] 机（木目の木の机）が四辺に約{M['desk']}px見える。その内側に約{M['band']}px幅の土台縁の帯（外{M['foam']}px foamboard・内{M['corr']}px corrugated 断面）が**四辺すべて（北・南・西・東）**で途切れず見える。模型の天面は画像の内側に収まる。天面は x{M['mx0']}–{M['mx1']}・y{M['my0']}–{M['my1']} 付近。\n"
               f"- [ ] 通路が模型の縁（土台縁の帯の内側）に届く。画像端（机の外）に通路が出ていない。床は模型の外に一画素も無い。")
    pas = ["- [ ] 通路は**7本**（北2・東1・南3・西1）。"]
    for s in "NESW":
        for e in m["edges"][s]:
            ax = "x" if s in "NS" else "y"
            f = sx if ax == "x" else sy
            pas.append(f"- [ ] {s}辺 {e['port']}: {ax} {e['a']}–{e['b']}（1672: {ax} {f(e['a'])}–{f(e['b'])}）、幅約{lw}px（1672: 約{sx(lw)}px）。")
    pas.append("- [ ] 他の縁の区間には床が出ていない。遷移範囲の印（色帯・矢印・線・文字）が絵に無い。")
    out.append("通路:\n" + "\n".join(pas))
    cx, cy = hd["c"]
    out.append("経路の形（本命の検査。割付図の実測値）:\n"
               f"- [ ] 広間: 横長の楕円の床（中心({cx},{cy})・横半径{hd['rx']}・縦半径{hd['ry']}）。床は平らで空。台座が無い。壁は細い段ボール茶の帯（厚み約{hd['wt']}px、青灰でない）の弧が{len(hd['arcs'])}か所だけ見え、他は帯が床に接する。壁が太って床を削っていない。\n"
               f"- [ ] 首は広間の北から**1本**（x {hd['neck'][0]}–{hd['neck'][1]}、真北、曲がりなし）。分岐点 ({cx},{hd['jy']}) の上で頭（真北）と口（右上へ約{hd['mouth_ang']:.1f}度→y {hd['ky']} で辺へ垂直）に分かれる。分岐点より下に2本目の帯が無い。\n"
               "- [ ] 西辺=右腕・東辺=左腕・南辺=肺（x450–680）・下半身（x845–1075）・心臓（x1239–1469）。左右は本人から見る（画面左=本人の右）。口・頭・肺・心臓に唇・歯・舌・頭蓋・臓器の造形が無い（通路の名前だけ）。")
    out.append("材料・質感・装飾（装飾込み1回生成）:\n"
               "- [ ] ① 土台縁の帯に corrugated cardboard 断面と foamboard の縁 ② 仕切りと広間の壁が細く低い corrugated の帯1本＋毛糸の縁取り1本（床の幅に含まれない）\n"
               "- [ ] ③ 地形が paper clay の面で、肌色・薄桃・茶系の matte poster paint ④ 赤い折り紙の切片が**ちょうど6枚**（全て模型の中の地形の上。壁・床・土台縁・机に無い）\n"
               "- [ ] ⑤ 机が木目の木の机\n"
               "- [ ] ⑥ 装飾は人体に関係する抽象的な工作物だけ（骨・細胞や粒・筋肉や神経の糸・鼓動のぎざぎざ線・皮膚の彫り・ばんそうこう・毛・ばい菌）。少なくとも6か所の塊・各塊3〜5種。花・葉・雲・星・旗・柵・ハート形・動物・食べ物・風景・臓器の形・血管の網が無い。フェルトの花が無い\n"
               "- [ ] ⑥b 装飾の色が肌色・薄桃・クリーム・茶系・象牙色の範囲（緑・青・黄・紫・オレンジが無い）。赤は折り紙6枚だけ\n"
               "- [ ] ⑦ 床（クリームの通路・広間）には何も置かれず平ら。毛糸が血管・臓器に見える走り方をしていない")
    out.append("許容差（レビュー側基準。生成入力には入れない）: 通路位置 ±25px、幅 ±10%（1672x941 の場合は ×0.871）。床マスクIoU（clean 割付図に対して）≥0.95 を目安。")
    return "\n\n".join(out)


# BDY-02 だけの本文の上書き（独立レビュー 2026-10-22 条件付き可の指摘反映）: 装飾が幾何を圧倒しないよう P9 を圧縮し、色の段落は P8 に1回だけ置く。
# 許可品目は BDY-02 の主役・脇役が使うものだけ。赤紙は枚数と領域と座標を固定。他MAPの本文（共通部品 deco_texts）は変えない。
BDY02_RED = [("lower left", [(250, 800), (380, 880)]), ("upper left", [(300, 230), (600, 330)]),
             ("lower right", [(1560, 780)]), ("upper right", [(1620, 190)])]  # clean 実測の地形区画（bbox 内の地形の上。各点の周囲45pxが全て地形）


def bdy02_override(P, mid, M, wide, dd):
    prim = dd["prim"]
    r = random.Random(mid)
    minor = [k for k in FAMILY if k not in prim]
    r.shuffle(minor)
    side = "; ".join(FAMILY[k][1] for k in minor[:3])
    P["P8"] = (
        "P8. COLORS: passage floors: matte poster paint in cream and pale peach, the same range everywhere. "
        f"Terrain: matte poster paint, {TONE[dd['tone']]}, one tone per face. "
        "COLOURS OF THE DECORATION: every decoration item is coloured only within skin tone, pale pink, cream, ivory and brown shades "
        "(yarn and thread: light to deep shades of cream, pale pink and skin tone; paper-clay items: cream, pale pink, skin tone or light brown; toothpicks: natural wood). "
        "The red of the six origami pieces of P10 is the only other colour in the model, and the desk is natural wood. "
        "So the whole model reads as one warm family of skin, pale pink, cream and brown. "
        f"The edging yarn is {dd['yarn']}. The desk is warm natural wood ({dd['desk']}). Partitions: corrugated cardboard strips with paper clay on top, in brown and skin tones.")
    P["P9"] = (
        "P9. DECORATION (small hand-made ornament about the human body, secondary to the geometry). Leading motifs: "
        "(1) pulse lines: cream or pale pink wool yarn glued down as jagged zigzag lines, in short separate pieces; "
        "(2) muscle and nerve threads: short separate bundles, twisted cords, spirals and coils of wool yarn in cream, pale pink and skin tones, each strand on its own, never joined into a net and never branching; "
        "(3) skin texture carved into the paper clay with a toothpick: fingerprint-like swirls of concentric lines, fields of tiny pore dots, short parallel curved wrinkle lines. "
        f"Only as small supporting touches: {side}. "
        "WHERE: only on the terrain faces of the 4 wide regions, along the foot of the partitions and of the hall wall arcs, on the edge of the base band and on the desk; the cream floors and the hall floor stay clear (P11). "
        f"ARRANGEMENT: {LAYOUT[dd['layout']]}. "
        f"EDGE: the edging yarn at the foot of the partitions is {dd['yarn']}; the base band's masking tape is cream and its PVA white. "
        f"THE DESK: warm wood grain; around the model lie {dd['leftovers']} (few and small; nothing covers the base band). "
        "DENSITY at kindergarten-craft level: each of the 4 wide regions shows 3 to 5 kinds of small items, at least 6 groups over the terrain; "
        "the narrow strips and wedges (such as the wedge between the head band and the mouth band) carry only a thin edging of yarn. "
        "The geometry in P3 to P6 (floor widths, the single neck, the branch, the hall) always has priority over decoration.")
    pieces = []
    for name, pts in BDY02_RED:
        n_ = {1: "one", 2: "two"}[len(pts)]
        where = " and ".join(f"({x}, {y}) (in 1672x941: ({sx(x)}, {sy(y)}))" for x, y in pts)
        pieces.append(f"{n_} in the {name} terrain region, about {where}")
    P["P10"] = (
        "P10. RED ORIGAMI: EXACTLY SIX (6) hand-cut red paper pieces with uneven edges (cut with scissors from red origami paper, flat on the surface, glued with PVA), no more and no fewer: count them, six, with no seventh and no spare piece anywhere. "
        "Exactly six red origami pieces, each about 45 px across: " + "; ".join(pieces) + " (six in total), "
        f"all on terrain faces inside the model (x {M['mx0']} to {M['mx1']}, y {M['my0']} to {M['my1']}; in 1672x941: x {sx(M['mx0'])} to {sx(M['mx1'])}, y {sy(M['my0'])} to {sy(M['my1'])}), "
        "none on any floor, wall, rim or desk, none anywhere outside the model. "
        "Their outlines are irregular and unequal, not drawn as any particular symbol; they are clean paper cut-outs, never blood stains or liquid. "
        "They are the only red objects in the picture. Nothing of P9 is laid over them: they are not a base for ornament.")
    P["P12"] = (
        "P12. MATERIALS (every material must be identifiable at full size): base: 5 mm foamboard with the corrugated cardboard cross-section band described in P2; terrain surface: paper clay modelled by hand; "
        "partitions (12 px) and the hall wall arcs (22 px): one low corrugated cardboard band each under smoothed paper clay, with one strand of yarn along the foot; floors and terrain: matte poster paint applied with a flat brush; the joint of the band: masking tape; "
        "decoration: wool yarn and thread (zigzag lines, muscle threads, hair tufts), toothpick-carved patterns in paper clay, small paper-clay balls with toothpick spikes, toothpicks with clay ends, white PVA glue; "
        "accents: 6 pieces of red origami paper cut by hand with scissors; desk: wooden tabletop with visible wood grain. "
        "Hand-made roughness: ragged hand-cut paper edges, paint unevenness, visible material seams. Parts look like paper and clay (matte, soft edges). "
        "It reads as a crude hand-made miniature in which the whole picture is the model, and not as a photograph of a real place.")


# ---------------------------------------------------------------------------
# 部屋・迷路の4枚（BDY-04 脳の迷路・BDY-15 胃のJ字の1袋・BDY-16 心臓の4部屋・BDY-17 肺の外周の環＝案A）。
# kako-jun が脳=迷路・胃=J字の1袋・心臓=2x2の4部屋・肺=案Aを決定し、モックを承認済み（Issue #142。2026-10-22）。
# 形は clean 割付図の画素から実測する（body_layout.py の SPECS は『種』と突き合わせるだけ。食い違えば停止）。
# 迷路は『13列x6行の格子の全通路』を行・列ごとの連なりとして列挙し、通路の本数と行き止まりの数を守らせる（生成による簡略化・正解の道の変更の防止）。
# 別コードの再測定: verification/body-layout/remeasure_body_rooms.py（scipy の距離変換・境界円当てはめ・格子の走査）。
# ---------------------------------------------------------------------------
STAND_IN = {
    230: "a stand-in for three characters side by side; no character is drawn",
    77: "the width of one character; no character is drawn",
}


def _nonfloor_boundary(fl):
    ys, xs = np.nonzero((~fl) & _shift4(fl))
    return xs.astype(float), ys.astype(float)


def inscribed(bnd, p, win=10, near=340):
    """点 p の近く（±win px）で、床だけでできる最大の円。戻り値 (中心 (x,y), 半径)。半径は『最も近い床でない画素の中心までの距離 - 0.5』。"""
    xs, ys = bnd
    sel = (np.abs(xs - p[0]) < near + win) & (np.abs(ys - p[1]) < near + win)
    X, Y = xs[sel], ys[sel]
    res = []
    for dx in range(-win, win + 1):
        for dy in range(-win, win + 1):
            cx, cy = p[0] + dx, p[1] + dy
            res.append((float(np.sqrt(((X - cx) ** 2 + (Y - cy) ** 2).min())) - 0.5, cx, cy))
    best = max(r[0] for r in res)
    top = [r for r in res if r[0] >= best - 0.6]
    return (float(np.mean([r[1] for r in top])), float(np.mean([r[2] for r in top]))), best


def _run_containing(v, i):
    """1次元の真偽列 v で、位置 i を含む True の連続区間 (始, 終)。i が False なら None。"""
    for a, b in runs_of(v):
        if a <= i <= b:
            return a, b
    return None


def _erode_sq(mask, n):
    """正方形（一辺 2n+1）での収縮。結果が True の画素は、周囲 n px の正方形が全て mask の中。"""
    out = mask.copy()
    for ax in (1, 0):
        for _ in range(n):
            t = out.copy()
            if ax == 1:
                t[:, 1:] &= out[:, :-1]
                t[:, :-1] &= out[:, 1:]
            else:
                t[1:, :] &= out[:-1, :]
                t[:-1, :] &= out[1:, :]
            out = t
    return out


def _floor_dist_fn(floor):
    """点 p から床の画素までの最短距離を返す関数（床の輪郭画素だけを使う。p の周囲 ±300px の輪郭で足りる範囲だけ正確）。"""
    by, bx = np.nonzero(floor & _shift4(~floor))
    bx, by = bx.astype(float), by.astype(float)

    def dist(p):
        sel = (np.abs(bx - p[0]) < 300) & (np.abs(by - p[1]) < 300)
        return float(np.sqrt((bx[sel] - p[0]) ** 2 + (by[sel] - p[1]) ** 2).min()) if sel.any() else 300.0
    return dist


def red_points(terr, h, k=6, floor=None, clear=0):
    """地形の上の赤紙の中心 k 個（周囲 h px が全て地形の画素だけから、最遠点サンプリングで決定的に。5px刻みに丸める）。
    floor を渡すと、床の画素から clear px 以上離れること（赤紙の半分＋仕切り＋毛糸の余白）を保証する:
    足りない点だけを、近傍 ±80px（5px刻み・条件を満たす点）のうち元の位置に最も近い点へ寄せ直す。"""
    ok = _erode_sq(terr, h)
    ys, xs = np.nonzero(ok[::5, ::5])
    cand = np.c_[xs * 5, ys * 5].astype(float)
    if len(cand) < k:
        die(f"赤紙の置ける地形（周囲{h}pxが全て地形）の点が{len(cand)}個しかない")
    chosen = [cand[np.argmin(cand[:, 0] + cand[:, 1])]]
    while len(chosen) < k:
        d = np.min([np.hypot(*(cand - c).T) for c in chosen], axis=0)
        chosen.append(cand[np.argmax(d)])
    out = []
    for c in chosen:
        q = (int(round(c[0] / 5.0) * 5), int(round(c[1] / 5.0) * 5))
        out.append(q if ok[q[1], q[0]] else (int(c[0]), int(c[1])))
    if floor is not None and clear > 0:
        dist = _floor_dist_fn(floor)
        for i, q in enumerate(out):
            if dist(q) >= clear:
                continue
            best = None
            for dx in range(-80, 81, 5):
                for dy in range(-80, 81, 5):
                    x, y = q[0] + dx, q[1] + dy
                    if 0 <= x < ok.shape[1] and 0 <= y < ok.shape[0] and ok[y, x]:
                        d = dist((x, y))
                        if d >= clear and (best is None or (-math.hypot(dx, dy), d) > best[0]):
                            best = ((-math.hypot(dx, dy), d), (x, y))
            if best is None:
                die(f"赤紙 {q} の近傍に、床から{clear}px以上離れた地形の点がない")
            out[i] = best[1]
    return sorted(out, key=lambda t: (t[1], t[0]))


# ---- BDY-04 迷路
def measure_maze(m, bl):
    fl, M = m["floor"], m["M"]
    sp = bl.SPECS["BDY-04"]
    C, R, PITCH = bl.MAZE_COLS, bl.MAZE_ROWS, bl.MAZE_PITCH
    lw1 = bl.mlw("BDY-04", m["lw"])
    ox, oy = M["mx0"] + bl.MAZE_X0, M["my0"] + bl.MAZE_Y0
    X = lambda c: ox + c * PITCH
    Y = lambda r: oy + r * PITCH
    cells = [(c, r) for r in range(R) for c in range(C)]
    for c, r in cells:
        if not fl[Y(r), X(c)]:
            die(f"BDY-04: 格子の中心 ({X(c)},{Y(r)}) が床でない（78セルは全て通路）")
    links, gaps, widths = set(), [], []
    for c, r in cells:
        for dc, dr in ((1, 0), (0, 1)):
            n = (c + dc, r + dr)
            if n[0] >= C or n[1] >= R:
                continue
            line = fl[Y(r), X(c):X(n[0]) + 1] if dc else fl[Y(r):Y(n[1]) + 1, X(c)]
            if line.all():
                links.add(((c, r), n))
                mx, my = (X(c) + X(n[0])) // 2, (Y(r) + Y(n[1])) // 2
                run = _run_containing(fl[my, :] if not dc else fl[:, mx], mx if not dc else my)
                widths.append(run[1] - run[0] + 1)
            else:
                rr = runs_of(~line)
                if len(rr) != 1:
                    die(f"BDY-04: セル {(c, r)}-{n} の間の地形が1区間でない（半端な通路）")
                gaps.append(rr[0][1] - rr[0][0] + 1)
    if not (min(widths) >= lw1 and max(widths) <= lw1 + 2):
        die(f"BDY-04: 通路幅の実測 {min(widths)}〜{max(widths)}px が {lw1}px と不一致")
    if len(links) != len(cells) - 1:
        die(f"BDY-04: 通路 {len(links)} 本 != セル数-1（{len(cells) - 1}。ループなし・全セル連結の木でない）")
    adj = {}
    for a, b in links:
        adj.setdefault(a, set()).add(b)
        adj.setdefault(b, set()).add(a)
    if {frozenset(x) for x in links} != {frozenset((a, b)) for a, nb in sp["tree"].items() for b in nb}:
        die("BDY-04: 画素から読んだ通路の接続が body_layout の迷路（seed）と不一致")
    root = sp["root"]
    deg = {c: len(adj[c]) + (1 if c == root else 0) for c in adj}
    dead = sorted([c for c, d in deg.items() if d == 1], key=lambda c: (c[1], c[0]))
    tj = sorted([c for c, d in deg.items() if d >= 3], key=lambda c: (c[1], c[0]))
    corners = 0
    for c, d in deg.items():
        if d == 2:
            nn = list(adj[c]) + ([(c[0], c[1] + 1)] if c == root else [])
            (a_, b_) = nn
            if (a_[0] - c[0], a_[1] - c[1]) != (c[0] - b_[0], c[1] - b_[1]):
                corners += 1
    ex = sp["expect"]
    if (corners, len(tj), len(dead)) != (ex["corners"], ex["tjunc"], ex["deadends"]):
        die(f"BDY-04: 曲がり{corners}・T字{len(tj)}・行き止まり{len(dead)} が body_layout の期待 {ex} と不一致")
    # 再構成: 読んだ通路の接続だけから床を描き直し、clean の床との不一致画素を数える（全通路が列挙に含まれることの確認）
    from PIL import ImageDraw
    im = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(im)
    hw = lw1 / 2
    for (a, b) in links:
        d.rectangle([min(X(a[0]), X(b[0])) - (hw if a[0] == b[0] else 0), min(Y(a[1]), Y(b[1])) - (hw if a[1] == b[1] else 0),
                     max(X(a[0]), X(b[0])) + (hw if a[0] == b[0] else 0), max(Y(a[1]), Y(b[1])) + (hw if a[1] == b[1] else 0)], fill=255)
    for c in adj:
        d.ellipse([X(c[0]) - hw, Y(c[1]) - hw, X(c[0]) + hw, Y(c[1]) + hw], fill=255)
    d.rectangle([X(root[0]) - hw, Y(root[1]), X(root[0]) + hw, M["my1"] - 1], fill=255)
    rec = np.asarray(im) > 0
    box = np.zeros_like(fl)
    box[M["my0"]:M["my1"], M["mx0"]:M["mx1"]] = True
    # 床の輪郭から2px以内の差は線の太さの丸め（clean の帯は 77px を78画素で塗る）。輪郭から2px超離れた不一致が残れば、通路の漏れか余計な通路
    edge_band = (fl & _shift4(~fl)) | ((~fl) & _shift4(fl))
    for _ in range(2):
        edge_band = edge_band | _shift4(edge_band)
    mism = int(((rec ^ fl) & box & ~edge_band).sum())
    if mism > 20:
        die(f"BDY-04: 読んだ通路から描き直した床と clean の床が、輪郭から2px超離れて {mism} 画素違う。列挙に漏れがある")
    hruns, vruns = [], []
    for r in range(R):
        c = 0
        while c < C:
            c2 = c
            while c2 + 1 < C and ((c2, r), (c2 + 1, r)) in links:
                c2 += 1
            if c2 > c:
                hruns.append((r, c, c2))
            c = c2 + 1
    for c in range(C):
        r = 0
        while r < R:
            r2 = r
            while r2 + 1 < R and ((c, r2), (c, r2 + 1)) in links:
                r2 += 1
            if r2 > r:
                vruns.append((c, r, r2))
            r = r2 + 1
    # 入口から最も遠い行き止まりまでの道の曲がり点
    dist, par, q = {root: 0}, {}, [root]
    for c in q:
        for n in sorted(adj[c]):
            if n not in dist:
                dist[n] = dist[c] + 1
                par[n] = c
                q.append(n)
    far = max(dead, key=lambda c: (dist[c], -c[1], -c[0]))
    path = [far]
    while path[-1] != root:
        path.append(par[path[-1]])
    path.reverse()
    pts = [(X(root[0]), M["my1"])] + [(X(c[0]), Y(c[1])) for c in path]
    turn = [pts[0]]
    for i in range(1, len(pts) - 1):
        a, b, c = pts[i - 1], pts[i], pts[i + 1]
        if (b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0]) != 0:
            turn.append(b)
    turn.append(pts[-1])
    xs_, ys_ = [X(c) for c in range(C)], [Y(r) for r in range(R)]
    edge = m["edges"]["S"][0]
    frame = (min(xs_) - hw - M["mx0"], M["mx1"] - (max(xs_) + hw), min(ys_) - hw - M["my0"], M["my1"] - (max(ys_) + hw))
    return dict(X=X, Y=Y, C=C, R=R, pitch=PITCH, lw=lw1, cells=len(cells), links=len(links), widths=(min(widths), max(widths)), gap_min=min(gaps), gap_max=max(gaps),
                dead=dead, tj=tj, corners=corners, hruns=hruns, vruns=vruns, root=root, far=far, far_dist=dist[far], turn=turn, mism=mism,
                frame=frame, entrance=(edge["a"], edge["b"]), seed=sp["seed"], root_pt=(X(root[0]), Y(root[1])),
                longest=max(dist.values()), dist=dist, tie_far=sorted([c for c in dead if dist[c] == dist[far]], key=lambda c: (c[1], c[0])))


# ---- BDY-15 胃（J字の1袋）
def measure_sac(m, bl, bnd):
    fl, M = m["floor"], m["M"]
    ctrl = []
    for i, (x, y, r) in enumerate(bl.SAC15):
        if i == 1:  # 制御点の2つ目は1つ目と同じ位置（ドームの中心）
            continue
        p = (M["mx0"] + x, M["my0"] + y)
        c, rr = inscribed(bnd, p, win=0)  # 制御点の位置そのものでの最大内接円（細くなる先端で中心をずらすと半径が過大に出る）
        if abs(rr - r) > 4:
            die(f"BDY-15: 袋の制御点 {p} の最大内接円の半径 画素実測{rr:.1f}px が body_layout の {r}px と不一致")
        ctrl.append(dict(c=p, r_spec=r, r_meas=rr, c_meas=c))
    ys, xs = np.nonzero(fl)
    # 入口の帯（西辺）
    edge = m["edges"]["W"][0]
    # 各列の床の区間（1本のとき）
    prof = []
    xcols = [150, 250] + list(range(350, 900, 50)) + list(range(900, 1600, 100)) + [1590]
    for x in xcols:
        rr = runs_of(fl[:, x])
        if len(rr) != 1:
            die(f"BDY-15: 列 x={x} の床の区間が{len(rr)}本（1つの袋は1本）")
        prof.append((x, rr[0][0], rr[0][1]))
    bend_x = next(x for x in range(M["mx0"], M["mx1"]) if (runs_of(fl[:, x])[0][1] > edge["b"] + 2))
    xmax = int(xs.max())
    tip = (xmax, int(round(ys[xs == xmax].mean())))
    ymax = int(ys.max())
    low = (int(round(xs[ys == ymax].mean())), ymax)
    cap = ctrl[-1]
    # 床は1つの連結（袋の外に島がない）
    comp = components(fl, 4)
    if len(comp) != 1:
        die(f"BDY-15: 床が{len(comp)}個に分かれている（1つの袋）")
    widest = max(c["r_meas"] for c in ctrl)
    return dict(ctrl=ctrl, prof=prof, tip=tip, low=low, cap=cap, widest=widest, entrance=(edge["a"], edge["b"]), area=int(fl.sum()), bend_x=bend_x)


# ---- BDY-16 心臓・BDY-17 肺（丸い部屋と環の通路）
def measure_ring_rooms(mid, m, bl, bnd):
    fl, M = m["floor"], m["M"]
    sp = bl.SPECS[mid]
    lw1 = bl.mlw(mid, m["lw"])
    rooms = []
    for name, x, y, r in sp["rooms"]:
        p = (M["mx0"] + x, M["my0"] + y)
        c, rr = inscribed(bnd, p, win=8)
        if abs(c[0] - p[0]) > 3 or abs(c[1] - p[1]) > 3 or abs(rr - r) > 3:
            die(f"{mid}: 丸い部屋 {name} の画素実測 中心({c[0]:.1f},{c[1]:.1f}) 半径{rr:.1f} が body_layout の ({p[0]},{p[1]}) {r} と不一致")
        rooms.append(dict(name=name, c=(p[0], p[1]), r=r, c_meas=(round(c[0], 1), round(c[1], 1)), r_meas=round(rr, 1)))  # 画素実測が公称の ±3px 以内なので、公称値（整数）を書く
    if len({q["r"] for q in rooms}) < 1:
        die(f"{mid}: 部屋がない")
    side = next(s for s in "NSWE" if m["edges"][s])
    e = m["edges"][side][0]
    res = dict(rooms=rooms, lw=lw1, side=side, entrance=(e["a"], e["b"]))
    terr = m["terr"]
    if mid == "BDY-16":
        xs = sorted({M["mx0"] + x for _n, x, _y, _r in sp["rooms"]})
        ys = sorted({M["my0"] + y for _n, _x, y, _r in sp["rooms"]})
        top = _run_containing(fl[:, (xs[0] + xs[1]) // 2], ys[0])
        bot = _run_containing(fl[:, (xs[0] + xs[1]) // 2], ys[1])
        lef = _run_containing(fl[(ys[0] + ys[1]) // 2, :], xs[0])
        rig = _run_containing(fl[(ys[0] + ys[1]) // 2, :], xs[1])
        if None in (top, bot, lef, rig):
            die("BDY-16: 環の4本の通路の中心線が床でない")
        res.update(xs=xs, ys=ys, top=top, bot=bot, left=lef, right=rig, island=(lef[1] + 1, top[1] + 1, rig[0] - 1, bot[0] - 1))
        for nm, (a, b) in (("上", top), ("下", bot), ("左", lef), ("右", rig)):
            if abs((b - a + 1) - m["lw"]) > 3:
                die(f"BDY-16: 環の{nm}の通路の幅 {b - a + 1}px が {m['lw']}px と不一致")
    else:
        left = sorted([q for q in rooms if q["c"][0] < 960], key=lambda q: q["c"][1])
        right = sorted([q for q in rooms if q["c"][0] > 960], key=lambda q: q["c"][1])
        xl, xr = left[0]["c"][0], right[0]["c"][0]
        yt, yb = left[0]["c"][1], left[-1]["c"][1]
        xm = (xl + int(960)) // 2 + 50
        top = _run_containing(fl[:, xm], yt)
        bot = _run_containing(fl[:, 960], yb)
        lef = _run_containing(fl[(left[0]["c"][1] + left[1]["c"][1]) // 2, :], xl)
        lef2 = _run_containing(fl[(left[1]["c"][1] + left[2]["c"][1]) // 2, :], xl)
        rig = _run_containing(fl[(right[0]["c"][1] + right[1]["c"][1]) // 2, :], xr)
        ent = _run_containing(fl[M["my0"] + 30, :], 960)
        if None in (top, bot, lef, lef2, rig, ent):
            die("BDY-17: 環の通路の中心線が床でない")
        for nm, (a, b) in (("上", top), ("下", bot), ("左上", lef), ("左下", lef2), ("右", rig), ("入口", ent)):
            if abs((b - a + 1) - lw1) > 2:
                die(f"BDY-17: 環の{nm}の通路の幅 {b - a + 1}px が {lw1}px と不一致")
        t1, b0, l1, r0 = top[1], bot[0], lef[1], rig[0]
        sub = terr[t1 + 1:b0, l1 + 1:r0]  # 環の内側の長方形。環の床に囲まれているので、ここの地形は全て島
        iy, ix = np.nonzero(sub)
        isl = (int(ix.min()) + l1 + 1, int(iy.min()) + t1 + 1, int(ix.max()) + l1 + 1, int(iy.max()) + t1 + 1)
        res.update(xl=xl, xr=xr, yt=yt, yb=yb, top=top, bot=bot, left=lef, right=rig, island=isl, left_rooms=left, right_rooms=right)
    return res


def measure_rooms(mid, m, bl):
    bnd = _nonfloor_boundary(m["floor"])
    if mid == "BDY-04":
        rg = measure_maze(m, bl)
    elif mid == "BDY-15":
        rg = measure_sac(m, bl, bnd)
    else:
        rg = measure_ring_rooms(mid, m, bl, bnd)
    rg["kind"] = mid
    h, sz = (26, 30) if mid == "BDY-04" else (40, 45)  # 迷路の赤紙は約30px（1672版 約26px。仕切り・毛糸との余裕を取る。座標は従来どおり）
    rg["red"] = red_points(m["terr"], h, floor=m["floor"], clear=(36 if mid == "BDY-04" else 50))  # 赤紙の半分＋仕切り(8/12px)＋毛糸の余白。迷路36px・他50px
    rg["red_size"] = sz
    return rg


def _c1(p):
    return f"({p[0]}, {p[1]})"


def _pt(p):
    return pt2(int(round(p[0])), int(round(p[1])))


def rooms_p3(mid, m, rg):
    M, lw = m["M"], rg.get("lw", m["lw"])
    tw = M["mx1"] - M["mx0"]
    s = next(s for s in "NSWE" if m["edges"][s])
    e = m["edges"][s][0]
    ax = "x" if s in "NS" else "y"
    edge_c = {"N": f"y {M['my0']}", "S": f"y {M['my1']}", "W": f"x {M['mx0']}", "E": f"x {M['mx1']}"}[s]
    into = {"BDY-04": f"into the first cell of the maze, at about {_pt(rg['root_pt']) if mid == 'BDY-04' else ''}",
            "BDY-15": "into the pouch of P4",
            "BDY-16": "into the upper-left room of P4",
            "BDY-17": "to the ring of P4, joining its top passage at about " + (_pt((960, rg["yt"])) if mid == "BDY-17" else "")}[mid]
    return _p3_trim(mid, (
        f"P3. THE ENTRANCE AND THE MODEL'S EDGE. The model's top surface is made of thin flat paper-clay surfaces. "
        f"ONE single flat floor band, {lw} px wide measured across the band ({lw / tw:.2g} of the model's width of {tw} px, which is {sx(lw)} px in the 1672x941 frame; {STAND_IN[lw]}), "
        f"runs straight inward from the model's edge (exactly perpendicular to the edge, with no bend) {into}, and it reaches the model's edge and stops flush against the inner edge of the corrugated band of P2: "
        f"the floor band ends where the model ends, at the band, and never continues onto the band, the desk or the frame edge (it leads on to the next map across the model's edge; "
        f"the character stands anywhere within a stretch of the edge to cross over, so nothing marks a crossing point). No marker, coloured zone, arrow, line or label of any kind is drawn at the edge. "
        f"Position where the band meets the model's edge, in the 1920x1080 frame, measured from the layout diagram (first image):\n"
        f"  - {SIDE_EN[s]}, {edge_c}), 1 passage: the {e['role'].replace('the ', '', 1)} at {rng(ax, e['a'], e['b'])}.\n"
        f"  Along every other stretch of the model's four edges, the edge is solid raised paper-clay terrain meeting the corrugated band: "
        f"the entrance band is the only floor that reaches the model's edge, 1 in all."))


def _p3_trim(mid, t):
    """BDY-04 の P3 だけ: 『戻る先』の言い回しと入口点の 1672 併記を削る（文字数と余計な臓器語の抑制）。"""
    if mid == "BDY-04":
        t = t.replace(" (leading back down toward the upper torso)", "")
        t = re.sub(r"(at about \(\d+, \d+\)) \(in 1672x941: \(\d+, \d+\)\)", r"\1", t, count=1)
    return t


def maze_landmarks(rg):
    """迷路の全体構造のランドマーク6個（clean 画素の実測から。各主張は列挙(hruns/vruns/dead/tj)で機械検査し、食い違えば停止する）。"""
    X, Y = rg["X"], rg["Y"]
    H, V, dead = set(rg["hruns"]), set(rg["vruns"]), set(rg["dead"])
    longest_h = max(c1 - c0 for _r, c0, c1 in rg["hruns"])
    need = [(0, 0, 6) in H, (0, 0, 6)[2] - (0, 0, 6)[1] == longest_h, (6, 0) in dead,  # 最上段の長い横1本（最長の横）。右端は行き止まり
            (5, 8, 12) in H, (8, 5) in dead,  # 最下段右の長い横。左端は行き止まり
            (0, 2, 5) in V, (0, 2) in dead,  # 左端の縦の長い1本。上端は行き止まり
            (0, 10, 12) in H, (10, 0, 1) in V, (12, 0, 2) in V, (12, 2) in dead, (1, 11, 12) in H,  # 右上のU字
            (2, 7, 11) in H, (3, 7, 10) in H, (7, 2, 3) in V, not any(c in (8, 9, 10) and r0 <= 2 and r1 >= 3 for c, r0, r1 in V),  # 中央右の長い横2段
            (6, 1, 3) in V]  # 中央の縦
    if not all(need):
        die("BDY-04: 迷路のランドマークの前提が clean の実測と合わない: " + str([i for i, v in enumerate(need) if not v]))
    return (
        f"LANDMARKS of the whole maze, to check the drawing against (centre lines, 1920x1080 frame): "
        f"(1) the longest straight corridor of the maze runs along the top row from {_c1((X(0), Y(0)))} to {_c1((X(6), Y(0)))}, and ends there in a closed round end; "
        f"(2) along the bottom row on the right, a long straight corridor runs from {_c1((X(8), Y(5)))}, where it ends in a closed round end, to {_c1((X(12), Y(5)))}; "
        f"(3) down the left side, a long straight vertical corridor runs at x {X(0)} from {_c1((X(0), Y(2)))}, where it ends in a closed round end, down to {_c1((X(0), Y(5)))}; "
        f"(4) in the upper right is a U-shaped hook: a corridor runs along the top row from {_c1((X(10), Y(0)))} to {_c1((X(12), Y(0)))}, turns down at its left end to {_c1((X(10), Y(1)))}, "
        f"and turns down at its right end to {_c1((X(12), Y(2)))}, where it ends in a closed round end (a short corridor from the left joins the right leg at {_c1((X(12), Y(1)))}); "
        f"(5) in the middle on the right, two long straight corridors lie one above the other with a wall between them: one at y {Y(2)} from x {X(7)} to x {X(11)}, one at y {Y(3)} from x {X(7)} to x {X(10)}, "
        f"and the only short link between them is the vertical corridor at x {X(7)} from y {Y(2)} to y {Y(3)}; "
        f"(6) in the middle of the maze a vertical corridor runs at x {X(6)} from {_c1((X(6), Y(1)))} down to {_c1((X(6), Y(3)))}. ")


def maze_p4(mid, m, rg):
    M = m["M"]
    X, Y, lw = rg["X"], rg["Y"], rg["lw"]
    ex0, ex1 = rg["entrance"]
    ex_c = (ex0 + ex1 + 1) // 2
    # 行ごとにまとめる（同じ行の複数の連なりは ' and ' でつなぐ）
    rows_txt = []
    for r in range(rg["R"]):
        segs = [(c0, c1) for rr, c0, c1 in rg["hruns"] if rr == r]
        rows_txt.append(f"    row {r} (y {Y(r)}): " + (" and ".join(f"x {X(c0)} to {X(c1)}" for c0, c1 in segs) if segs else "no horizontal run"))
    cols_txt = []
    for c in range(rg["C"]):
        segs = [(r0, r1) for cc, r0, r1 in rg["vruns"] if cc == c]
        cols_txt.append(f"    column {c} (x {X(c)}): " + (" and ".join(f"y {Y(r0)} to {Y(r1)}" for r0, r1 in segs) if segs else "no vertical run"))
    dead = ", ".join(_c1((X(c), Y(r))) for c, r in rg["dead"])
    tj = ", ".join(_c1((X(c), Y(r))) for c, r in rg["tj"])
    fr = rg["frame"]
    wall_ratio = rg["gap_min"] / lw
    if not (0.5 <= wall_ratio <= 0.6):
        die(f"BDY-04: 壁の厚み{rg['gap_min']}px が通路幅{lw}pxの0.5〜0.6倍でない")
    far = rg["far"]
    other = [c for c in rg["tie_far"] if c != far]
    if len(other) != 1:
        die(f"BDY-04: 最奥と同距離の行き止まりが2本でない: {rg['tie_far']}")
    far_txt = (f"The route from the entrance to the dead end at {_c1((X(far[0]), Y(far[1])))} is one of the two longest routes of the maze "
               f"(the other ends at the dead end at {_c1((X(other[0][0]), Y(other[0][1])))}; both are {rg['far_dist']} links from the entrance). ")
    return (
        f"P4. THE MAZE. The cream area of the first image is the stencil for the floor: every cream pixel stays floor, every other pixel stays terrain. "
        f"Do not move, add, remove, merge or simplify any passage, dead end or junction; only repaint the surfaces. "
        f"The maze is a {rg['C']} columns x {rg['R']} rows lattice, a loop-free network (exactly one route between any two cells), passage width {lw} px, partition wall about {wall_ratio:.2f} times the passage width ({rg['gap_min']} px). "
        f"The whole floor of this map is ONE maze of narrow corridors. Every corridor is exactly {lw} px wide across its whole length (in 1672x941: about {sx(lw)} px), the width of one character; "
        f"no corridor is ever wider or narrower. The corridors lie on a regular square grid of {rg['C']} columns by {rg['R']} rows; the centres of neighbouring grid cells are {rg['pitch']} px apart. "
        f"In the 1920x1080 frame the centre of the cell in column c (c = 0 to {rg['C'] - 1}, counted from the left) and row r (r = 0 to {rg['R'] - 1}, counted from the top) is at x = {X(0)} + {rg['pitch']} c and y = {Y(0)} + {rg['pitch']} r "
        f"(the top-left cell is at {_c1((X(0), Y(0)))}, the bottom-right cell at {_c1((X(rg['C'] - 1), Y(rg['R'] - 1)))}); in the 1672x941 frame every coordinate in this paragraph is multiplied by 0.871. "
        f"A corridor runs from cell to cell along the grid lines, horizontally along a row's centre line or vertically along a column's centre line, so every bend is a right angle "
        f"(the outer corner of each bend is rounded with radius {lw // 2} px, the inner corner is a plain sharp right angle). All {rg['cells']} cells are part of the maze, joined by {rg['links']} corridor links between neighbouring cells. "
        f"THE ENTRANCE: the single entrance band comes in from the south edge at x {ex0} to {ex1} (centre x {ex_c}) and runs straight up to the cell in column {rg['root'][0]}, row {rg['root'][1]}, at {_c1(rg['root_pt'])}, where the maze begins. "
        f"THE WALLS: between any two corridors lies a wall of terrain at least {rg['gap_min']} px thick (neighbouring cells that are not joined are separated by {rg['gap_min']} px of terrain), "
        f"and a frame of terrain about {int(min(fr))} px wide runs all around the maze, between the outermost corridors and the base band. Two corridors never touch except where they are joined at a cell. "
        + maze_landmarks(rg) +
        f"THE CORRIDORS: every corridor is a straight run between the listed end points (centre lines, 1920x1080 frame). "
        f"Horizontal runs, by row, from the cell centre at the left end to the cell centre at the right end:\n" + "\n".join(rows_txt) + "\n"
        f"  Vertical runs, by column, from the cell centre at the top end to the cell centre at the bottom end:\n" + "\n".join(cols_txt) + "\n"
        f"  Each run is a straight corridor {lw} px wide, and every cell centre lies on at least one run; two runs that share a cell centre are joined there. "
        f"COUNTS that stay exactly as they are: {rg['links']} corridor links; {rg['corners']} bends (right-angle turns of a corridor); {len(rg['tj'])} T-junctions (a cell where three corridors meet) at {tj}; "
        f"{len(rg['dead'])} dead ends, each a closed, rounded end (a semicircular cap of radius {lw // 2} px beyond the last cell centre) at the cell centres {dead}. "
        f"There is no crossing of four corridors and no loop: from the entrance there is exactly ONE route to every point of the maze, never two ways to the same place. "
        + far_txt +
        f"Keep the number of corridors and the number of dead ends as listed: do not add a corridor, do not remove one, do not shorten, extend, straighten or reroute one, do not open a wall to join two corridors, "
        f"do not turn a dead end into a loop, and do not replace the maze by any simpler or more regular pattern. Nothing lies at the dead ends: no object, no mark, no door.")


def sac_p4(mid, m, rg):
    M = m["M"]
    c0 = rg["ctrl"]
    dome, body = c0[0], c0[3]
    cap = rg["cap"]
    ent0, ent1 = rg["entrance"]
    prof = "; ".join(f"x {x} (in 1672x941: {sx(x)}): y {a} to {b} (in 1672x941: {sy(a)} to {sy(b)})" for x, a, b in rg["prof"])
    ctl = "; ".join(f"{_c1(c['c'])} with a half-width of about {int(round(c['r_meas']))} px" for c in c0)
    return (
        f"P4. THE POUCH. The whole floor is ONE single pouch bent like the letter J: one room, with no branch, no side room, no second route and no loop. It has the entrance band at its west end and a closed, rounded end at its east end. "
        f"All values are measured from the first image (1920x1080 frame; the 1672x941 values are given alongside where they are listed). "
        f"(a) The entrance band is {m['lw']} px wide (y {ent0} to {ent1} at the west edge x {M['mx0']}; in 1672x941: y {sy(ent0)} to {sy(ent1)}) and runs straight east, flat, with its top edge along y {ent0} and its bottom edge along y {ent1} as far as x {rg['bend_x']}, where the bottom edge turns down. "
        f"(b) The dome: the top edge of the entrance band carries straight on east along y {ent0} into a round dome that is the first, upper-left part of the pouch: a circle of radius about {int(round(dome['r_meas']))} px centred at about {_pt(dome['c'])}; the top of the dome joins the entrance band's top edge along y {ent0} with no step. "
        f"(c) The belly: the second, larger round part of the pouch, below and to the right of the dome, is the widest part of the pouch, about {int(round(2 * rg['widest']))} px across (twice the width of the entrance band), whose lowest point is at about {_pt(rg['low'])}; "
        f"the left side of the belly drops from the entrance band's bottom edge (x about 358, y {ent1}) in a smooth round curve to that lowest point. "
        f"(d) The narrowing arm: from the belly the pouch runs to the right and narrows steadily to about {int(round(2 * cap['r_meas']))} px wide, and ends in a closed, rounded end: a semicircular cap of radius about {int(round(cap['r_meas']))} px centred at about {_pt(cap['c'])}, whose farthest point is at about {_pt(rg['tip'])}. "
        f"The end is plain flat floor, level with the rest of the pouch, and the terrain closes it all around: there is no door, no gate, no hole, no object and no second route beyond it. "
        f"The centre line of the pouch passes through these points in order, from the dome to the closed end, with the half-width of the floor at each: {ctl}. "
        f"The floor between the top edge and the bottom edge in the vertical line at each x is: {prof}. "
        f"The pouch bends twice and never branches: it is a single closed room drawn as the first image shows it, not divided in two, not wider at any other place, and with no second dome or side pocket. "
        f"There is no hall and no wall of any other room in this map; the whole floor is this one pouch.")


def ring16_p4(mid, m, rg):
    M = m["M"]
    rooms = rg["rooms"]
    r = rooms[0]["r"]
    ul, ll, ur, lr = rooms  # body_layout の rooms の順: 画面左上・左下・右上・右下（名前は注記のみ）
    (t0, t1), (b0, b1), (l0, l1), (r0, r1) = rg["top"], rg["bot"], rg["left"], rg["right"]
    ix0, iy0, ix1, iy1 = rg["island"]
    e0, e1 = rg["entrance"]
    return (
        f"P4. FOUR ROUND ROOMS AND A SQUARE RING OF PASSAGES. The whole floor is ONE connected shape: four round rooms joined by four straight passages into a rectangular ring, entered by one passage from the north edge. "
        f"This map's rooms are plain round floors, one at each corner of the ring (all values measured from the first image, 1920x1080 frame; 1672x941 values alongside). "
        f"THE FOUR ROOMS: each is a perfectly round floor of radius {r} px ({2 * r} px across), wider than any passage; the upper-left room is centred at {_pt(ul['c'])}, the lower-left room at {_pt(ll['c'])}, "
        f"the upper-right room at {_pt(ur['c'])} and the lower-right room at {_pt(lr['c'])}. "
        f"THE RING: the four rooms are joined by four straight passages, each {m['lw']} px wide (in 1672x941: about {sx(m['lw'])} px) with a flat floor and straight, parallel edges: "
        f"the top passage between the two upper rooms runs along y {t0} to {t1} (centre line y {(t0 + t1) // 2}; in 1672x941: y {sy(t0)} to {sy(t1)}), the bottom passage between the two lower rooms along y {b0} to {b1} (centre line y {(b0 + b1) // 2}; in 1672x941: y {sy(b0)} to {sy(b1)}), "
        f"the left passage between the two left rooms along x {l0} to {l1} (centre line x {(l0 + l1) // 2}; in 1672x941: x {sx(l0)} to {sx(l1)}), and the right passage between the two right rooms along x {r0} to {r1} (centre line x {(r0 + r1) // 2}; in 1672x941: x {sx(r0)} to {sx(r1)}). "
        f"Each passage meets its two rooms on the line through their centres, so the ring is a rectangle whose four corners are the four rooms, and each round room bulges out beyond the passage on both sides. "
        f"THE ISLAND: inside the ring lies one solid rectangle of terrain (not floor), x {ix0} to {ix1} and y {iy0} to {iy1} ({ix1 - ix0 + 1} x {iy1 - iy0 + 1} px; in 1672x941: x {sx(ix0)} to {sx(ix1)}, y {sy(iy0)} to {sy(iy1)}). "
        f"THE ENTRANCE: the entrance band (x {e0} to {e1}, the same x range as the left passage) comes straight down from the north edge into the top of the upper-left room, in one straight vertical line with that room and the left passage. "
        f"The ring has exactly four rooms, four passages and one entrance, no dead end and no other opening; the rooms are story role names only, and each is drawn as a plain round floor with nothing in it and no outline of any organ.")


def lung17_p4(mid, m, rg):
    M = m["M"]
    lw = rg["lw"]
    L, Rr = rg["left_rooms"], rg["right_rooms"]
    rl, rr_ = L[0]["r"], Rr[0]["r"]
    (t0, t1), (b0, b1), (l0, l1), (r0, r1) = rg["top"], rg["bot"], rg["left"], rg["right"]
    isl = rg["island"]
    e0, e1 = rg["entrance"]
    xl, xr, yt, yb = rg["xl"], rg["xr"], rg["yt"], rg["yb"]
    return (
        f"P4. FIVE ROUND ROOMS ON AN OUTER RING. The whole floor is ONE connected shape: an outer ring of narrow passages with five round rooms on it, entered by one passage from the north edge. "
        f"All values are measured from the first image (1920x1080 frame; 1672x941 values alongside). Every passage is exactly {lw} px wide (in 1672x941: about {sx(lw)} px), the width of one character, over its whole length. "
        f"THE RING: a rectangle of passages whose centre lines run along y {yt} (top; floor y {t0} to {t1}), y {yb} (bottom; floor y {b0} to {b1}), x {xl} (left; floor x {l0} to {l1}) and x {xr} (right; floor x {r0} to {r1}); "
        f"in 1672x941 these centre lines are y {sy(yt)}, y {sy(yb)}, x {sx(xl)} and x {sx(xr)}. The top and bottom passages run from the left rooms' column to the right rooms' column. "
        f"THE FIVE ROOMS: each is a perfectly round floor, wider than any passage. Three smaller rooms of radius {rl} px stand on the left passage, centred at {_pt(L[0]['c'])}, {_pt(L[1]['c'])} and {_pt(L[2]['c'])} "
        f"(the top-left and bottom-left rooms are at the ring's corners and the third is halfway between them); two larger rooms of radius {rr_} px stand at the right corners of the ring, centred at {_pt(Rr[0]['c'])} and {_pt(Rr[1]['c'])}. "
        f"The left passage therefore threads the three left rooms one after another, with a short passage between neighbouring rooms; the right passage runs straight between the two right rooms with no room between them. "
        f"THE ENTRANCE: the entrance band (x {e0} to {e1}, centred on the middle of the picture, x 960; in 1672x941: x {sx(e0)} to {sx(e1)}) comes straight down from the north edge and joins the top passage at about {_pt((960, yt))}, in one single T-junction; "
        f"from there the top passage runs left to the top-left room and right to the top-right room. "
        f"THE ISLAND: the terrain inside the ring is one solid island (not floor) with its edges scalloped by the rooms, spanning x {isl[0]} to {isl[2]} and y {isl[1]} to {isl[3]} (in 1672x941: x {sx(isl[0])} to {sx(isl[2])}, y {sy(isl[1])} to {sy(isl[3])}). "
        f"The ring has exactly five rooms, one T-junction and four corners (each corner is a room), no dead end and no other opening; the rooms are story role names only, and each is drawn as a plain round floor with nothing in it and no outline of any organ.")


def build_prompt_rooms(mid, m, rg, bl):
    """部屋・迷路の4枚の onepass 本文（P1〜P14）。P1/P2/P13/P14 は共通（build_prompt）。構図・色・赤紙6枚・四辺の土台縁・床の幅を守る細い仕切り・参照2枚は他MAPと同じ共通部品。"""
    base, _ = build_prompt(mid, m, bl)
    M = m["M"]
    P = dict(base)
    lw = rg.get("lw", m["lw"])
    maze = mid == "BDY-04"
    wide = [r for r in m["regions"] if r["wide"]]
    narrow = [r for r in m["regions"] if not r["wide"]]
    pw = 8 if maze else 12  # 仕切りの帯の幅（迷路は壁が細いので8px。kako-jun 指示）
    P["P3"] = rooms_p3(mid, m, rg)
    P["P4"] = {"BDY-04": maze_p4, "BDY-15": sac_p4, "BDY-16": ring16_p4, "BDY-17": lung17_p4}[mid](mid, m, rg)
    P["P5"] = (
        "P5. NOTHING ELSE ON THE FLOOR. Only the entrance, the rooms, the passages, the bends, the junctions and the closed ends described in P3 and P4 are drawn: "
        "the floor has no other branch, room, loop, crossing or detour than the ones listed there, and no connection to any other map except through the one model's edge named in P3. "
        "The floor is empty: no body parts, no faces, no object lies on it.")
    branch_note = {
        "BDY-15": ' The ledger word "branch room" in the source text names this map\'s own single room; there is no branch inside the pouch.',
        "BDY-16": ' The ledger word "branch room" in the source text names this map\'s own four rooms; they are joined only by the ring of four passages, and no side room or branch leaves the ring.',
        "BDY-17": ' The ledger word "branch room" in the source text names this map\'s own five rooms on the outer ring; no side room or branch leaves the ring, apart from the one entrance band.',
    }
    if mid in branch_note:
        P["P5"] += branch_note[mid]
    if maze:
        P["P5"] = (
            "P5. NOTHING ELSE ON THE FLOOR. Only the entrance, the corridors, the bends, the T-junctions and the dead ends described in P3 and P4 are drawn: "
            "no hall, no round room, no loop, no crossing of four corridors, and no connection to any other map except through the one model's edge named in P3. "
            "The maze keeps all its corridors and all its dead ends exactly as listed in P4. The floor is empty: no body parts, no faces, no object lies on it.")
    foot = ("Each partition is only about 8 px wide (in 1672x941: about 7 px)" if maze else "Each partition is only about 12 px wide (in 1672x941: about 10 px)")
    wall_note = (
        f" A wall of about {rg['gap_min']} px between two corridors therefore carries two partitions, one for each corridor, with about {rg['gap_min'] - 2 * pw} px of flat painted terrain left between them; "
        "no yarn strand is laid in that narrow channel. Along the outer frame of the maze, on the terrain side of the outermost partitions, runs ONE thin edging strand of yarn (cream or pale pink)."
        if maze else
        " Outside each partition, on the terrain side along its foot, runs ONE thin edging strand of yarn (cream or pale pink).")
    P["P6"] = (
        f"P6. PARTITIONS. Along the floor edges ({'the edges of the corridors' if maze else 'the edges of the passages and of the rooms'}), on the terrain side of the floor outline, run LOW PARTITIONS: narrow low ridges (seen from above as narrow raised borders) "
        f"made of ONE narrow, low band of corrugated cardboard each (no stacking), with paper clay smoothed over its top, which make the {'corridors' if maze else 'passages and the rooms'}. {foot} and stands entirely on the terrain side of the floor outline, "
        f"on the boundary where the terrain face meets the floor; no floor colour appears outside a partition. The clear cream floor between the inner faces of the partitions keeps exactly the width of the cream area of the first image, "
        f"{lw} px for the {'corridors' if maze else 'passages'} (in 1672x941: about {sx(lw)} px){'' if maze else ', and the full round of each room'}; the thickness of a partition is never counted inside the floor width and never eats into it.{wall_note} "
        f"There are no doors, door frames or gates, no cave mouths, no round holes or tunnel mouths, no outline of any body or organ: the top of the model is only flat floor, low partitions, yarn edging and decorated terrain.")
    if maze:
        P["P7"] = (
            "P7. THE TERRAIN. The terrain is a thin, flat sheet of paper clay, painted face by face in matte poster paint in flesh skin tone, pale pink and brown-leaning tones, "
            "laid on with a flat brush (brush streaks and uneven coats visible), a different tone for each face. The terrain is the place for the handwork decoration of P9, which stays inside the same warm range of colours (see P8). "
            "It has no thick mounded layers, no stacked flesh-like bands, no striations and no fleshy cross-sections. "
            f"It is ONE connected surface: the frame around the maze (about {int(min(rg['frame']))} px wide on every side) and the walls between the corridors ({rg['gap_min']} px thick or more) are the same sheet; the corridors are cut out of it.")
    else:
        P["P7"] = (
            "P7. THE TERRAIN. The terrain around the rooms and passages is a thin, flat sheet of paper clay, painted face by face in matte poster paint in flesh skin tone, pale pink and brown-leaning tones, "
            "laid on with a flat brush (brush streaks and uneven coats visible), a different tone for each face. The terrain is the place for the handwork decoration of P9, which stays inside the same warm range of colours (see P8). "
            "It has no thick mounded layers, no stacked flesh-like bands, no striations and no fleshy cross-sections. "
            f"The floor divides the terrain into {len(wide)} wide region{'s' if len(wide) != 1 else ''}" + (f" and {len(narrow)} narrow strip{'s' if len(narrow) != 1 else ''}" if narrow else "")
            + (" (the terrain outside the ring and the island inside it)." if mid in ("BDY-16", "BDY-17") else " (the terrain around the pouch)." if mid == "BDY-15" else "."))
    P["P8"] = ""
    P["P9"] = ""
    P["P11"] = (f"P11. THE FLOOR STAYS EMPTY. Nothing of P9 lies on the cream floor, crosses into it or touches it: the {'corridors' if maze else 'passages and the rooms'} stay perfectly flat, clean and empty, nothing is placed where the characters walk, "
                f"and the width of the {'corridors' if maze else 'passages'}, {'the position of every dead end' if maze else 'the shape of the rooms'} and the flatness of the floor are exact. The surfaces of the model are flat floors, partitions and decorated terrain only. "
                "The floor and terrain contain no figures, spirits, flames or water pictures; every object is a small hand-made craft piece in the colours listed.")
    P["P12"] = ("P12. MATERIALS (every material must be identifiable at full size): base: 5 mm foamboard with the corrugated cardboard cross-section band described in P2; terrain surface: paper clay modelled by hand; "
                "partitions: one low corrugated cardboard strip each under smoothed paper clay; floors and terrain: matte poster paint applied with a flat brush; the joint of the band: masking tape; "
                "decoration (handmade items about the human body): wool yarn, thread, paper-clay balls, buttons, beads, toothpicks, skin-coloured tape, white PVA glue; accents: 6 pieces of red origami paper cut by hand with scissors; desk: wooden tabletop with visible wood grain. "
                "Hand-made roughness: ragged hand-cut paper edges, paint unevenness, visible material seams. Parts look like paper and clay (matte, soft edges), not like real skin, flesh, organs or stone. "
                "It reads as a crude hand-made miniature in which the whole picture is the model, and not as a photograph of a real place.")
    P["P10"] = ""
    narrow_txt = (f"The walls between the corridors (about {rg['gap_min']} px of terrain) are decorated only with toothpick-carved lines and dots (fingerprint swirls, pore dots, short parallel scratch lines) and flat strips of skin-coloured paper tape; "
                  "no raised or three-dimensional item stands on a wall, and every carving stays inside its wall without crossing a partition. " if maze else "")
    dd = apply_deco(P, mid, wide, "s" if not maze else "s", narrow_txt)
    if maze:
        P["P9"] = P["P9"].replace(
            "placed on the terrain, along the foot of the partitions, on the edge of the base band and on the desk only",
            "placed on the terrain only: the raised items (coils and bundles of yarn, clay balls, buttons, beads, spiky germs, thread tufts) stand on the terrain frame around the maze, on the four {int(min(rg['frame']))} px corner squares of the outer frame, "
            "on the edge of the base band and on the desk; the walls between the corridors are not kept bare, they carry the carved patterns and flat tape strips described below; and nothing is placed inside a corridor")
        for k_ in ("P3", "P4", "P5", "P6"):  # 30,000字以下のための削減: 通路幅・仕切り・入口の 1672 併記の重複（P1 の枠と P4 の係数 0.871 と P3 の幅の併記が残る）
            P[k_] = re.sub(r" \(in 1672x941: (?:about \d+ px|x \d+ to \d+)\)", "", P[k_])
        P["P4"] = P["P4"].replace(", the width of one character; no corridor is ever wider or narrower.", ", the width of one character.")
        P["P4"] = P["P4"].replace("Each run is a straight corridor {lw} px wide, and every cell centre".format(lw=lw), "Each run is a straight corridor, and every cell centre")
        P["P5"] = P["P5"].replace(" The maze keeps all its corridors and all its dead ends exactly as listed in P4.", "")
        P["P9"] = P["P9"].replace("wrinkle patterns of short parallel curved lines", "short parallel scratch lines")
        P["P9"] = P["P9"].replace("the edging strand of yarn at the foot of the partitions is", "the edging strand of yarn at the foot of the outermost partitions is")
        P["P9"] = P["P9"].replace("linked one after another across each terrain region, small items filling the gaps", "linked one after another around the terrain frame and over the corner squares, small items filling the gaps")
        P["P9"] = P["P9"].replace(
            "the decoration forms at least 6 groups over the terrain (arranged as the ARRANGEMENT says), so the picture feels rich and handmade.",
            "the decoration forms at least 6 groups of raised items on the frame, the corner squares and the desk (arranged as the ARRANGEMENT says: the chain runs all the way around the frame), with carved patterns along the walls, so the picture feels rich and handmade.")
    else:
        P["P9"] = P["P9"].replace(
            "placed on the terrain, along the foot of the partitions, on the edge of the base band and on the desk only",
            "placed on the terrain outside the rooms and the passages (the terrain around the ring or the pouch and, where there is one, on the island inside the ring), along the foot of the partitions, on the edge of the base band and on the desk only; nothing is placed inside any room or passage")
    P["P9"] = P["P9"].replace(COLOR_RULE + " ", "The colours of the decoration are given in P8. ")  # 色の段落は P8 に1回だけ（重複を除く）
    pcs = "; ".join(f"{_pt(q)}" for q in rg["red"])
    if maze:  # 迷路の送信文は30,000字以下に収めるため、赤紙の座標の 1672 併記を省く（P4 の係数 0.871 と赤紙の大きさの併記で足りる）
        pcs = re.sub(r" \(in 1672x941: \(\d+, \d+\)\)", "", pcs)
    P["P10"] = (
        "P10. RED ORIGAMI: EXACTLY SIX (6) hand-cut red paper pieces with uneven edges (cut with scissors from red origami paper, flat on the surface, glued with PVA), no more and no fewer: count them, six, with no seventh and no spare piece anywhere. "
        f"Exactly six red origami pieces, each about {rg['red_size']} px across (in 1672x941: about {sx(rg['red_size'])} px), centred at about: {pcs} (six in total), "
        f"all on terrain faces inside the model (x {M['mx0']} to {M['mx1']}, y {M['my0']} to {M['my1']}; in 1672x941: x {sx(M['mx0'])} to {sx(M['mx1'])}, y {sy(M['my0'])} to {sy(M['my1'])}), "
        "none on any floor, partition, rim or desk, none anywhere outside the model. "
        "Their outlines are irregular and unequal, not drawn as any particular symbol; they are clean paper cut-outs, never blood stains or liquid. "
        "They are the only red objects in the picture. Nothing of P9 is laid over them: they are not a base for ornament.")
    return P


def reference_text_rooms(mid, m, rg):
    if mid == "BDY-04":
        geom = ("the single entrance at the south edge and its position, the grid of corridors (every corridor, every bend, every T-junction and every dead end where the first image has it, not one pixel moved), the corridor width of 77 px, "
                "the walls between the corridors and the frame around the maze")
    elif mid == "BDY-15":
        geom = "the single entrance at the west edge and its position and width, and the outline of the one J-shaped pouch (its dome, belly, narrowing arm and closed rounded end) exactly as drawn"
    elif mid == "BDY-16":
        geom = "the single entrance at the north edge and its position and width, the four round rooms, the four passages that join them in a rectangular ring, and the solid island inside the ring, exactly as drawn"
    else:
        geom = "the single entrance at the north edge and its position and width, the outer ring of passages, the five round rooms (three on the left, two on the right) and the solid island inside the ring, exactly as drawn"
    return (
        "=== REFERENCE (two attached images, in this order) ===\n"
        "FIRST IMAGE: a flat layout diagram with four plain flat colours and no text. Its colours mean: grey = the desk; ochre-brown band = the base band's edge (P1, P2); "
        "dusty rose-brown inside the band = the model's top terrain (P7); light cream = the walkable floor (P3, P4). "
        f"Copy ONLY the geometry exactly: the nesting of desk, base band (foamboard rim, then corrugated layer) and model top on all four sides, {geom}. "
        "Treat the cream area as the clear floor width: the partitions stand in the terrain area next to it, never inside the cream. "
        "Repaint everything as the hand-made miniature described above. Do NOT carry over the diagram's four flat colours as flat fills (the desk is a warm wooden tabletop, the base band is foamboard and corrugated cardboard, "
        "there is no flat brown area anywhere in the result) or its perfectly straight, hard edges.\n"
        "SECOND IMAGE: a thin close-up strip of the front edge of a hand-made cardboard miniature base. Take from it ONLY the feel of three materials, to be used for the base band of P2: "
        "the exposed corrugated cardboard cross-section (the wavy flute layer along the top of the strip), the masking tape, and the ragged torn paper edge. "
        "Take no content from it, and ignore the few white cotton fibres at its top edge and its brown colour. "
        "The decoration of P9 is described by the text only: no attached image carries any decoration to copy.")


def report_rooms(mid, m, rg):
    L = []
    if mid == "BDY-04":
        L.append(f"- 経路の形: 迷路（広間・壁の弧なし。割付図に壁の画素なし）。格子 {rg['C']}列x{rg['R']}行・ピッチ{rg['pitch']}px・セル中心 x={rg['X'](0)}+{rg['pitch']}c, y={rg['Y'](0)}+{rg['pitch']}r。"
                 f"通路幅 実測 {rg['widths'][0]}〜{rg['widths'][1]}px（公称{rg['lw']}px）・壁の厚み 実測 {rg['gap_min']}〜{rg['gap_max']}px・外周の地形の枠 {', '.join(f'{v:.1f}' for v in rg['frame'])}px（左・右・上・下）。")
        L.append(f"- 通路 {rg['links']}本（セル{rg['cells']}・木＝ループなし）・曲がり{rg['corners']}・T字{len(rg['tj'])}・行き止まり{len(rg['dead'])}（body_layout の seed={rg['seed']} の迷路と接続が一致）。"
                 f"読んだ接続だけから描き直した床と clean の床の、輪郭から2px超離れた不一致 {rg['mism']} 画素。入口 {rg['entrance']}（南辺）→ セル {rg['root']} {rg['root_pt']}。入口から最奥まで {rg['far_dist']} セル（最奥 {rg['far']}）。")
        L.append("- 横の連なり（行, 左端セル中心x→右端セル中心x）: " + "; ".join(f"r{r} x{rg['X'](a)}-{rg['X'](b)}" for r, a, b in rg["hruns"]))
        L.append("- 縦の連なり（列, 上端セル中心y→下端セル中心y）: " + "; ".join(f"c{c} y{rg['Y'](a)}-{rg['Y'](b)}" for c, a, b in rg["vruns"]))
        L.append("- 行き止まり（丸い閉じた端の中心）: " + ", ".join(str((rg['X'](c), rg['Y'](r))) for c, r in rg["dead"]) + "。T字: " + ", ".join(str((rg['X'](c), rg['Y'](r))) for c, r in rg["tj"]) + "。")
    elif mid == "BDY-15":
        L.append("- 経路の形: 分岐なしJ字の1つの袋（入口の帯→ドーム→胃体→幽門の丸い閉じた端）。床は1連結。")
        L.append("- 中心線の制御点（clean 画素での最大内接円の半径）: " + "; ".join(f"{c['c']} 仕様半径{c['r_spec']}・実測{c['r_meas']:.1f}" for c in rg["ctrl"]) + "。")
        L.append(f"- 最下点 {rg['low']}・先端（最右）{rg['tip']}・床面積 {rg['area']}px。列ごとの床の区間: " + "; ".join(f"x{x}:y{a}-{b}" for x, a, b in rg["prof"]) + "。")
    elif mid == "BDY-16":
        L.append("- 経路の形: 丸い4部屋を四角い環の通路でつなぐ。部屋: " + "; ".join(f"{q['name']} 中心{q['c']} 半径{q['r']}" for q in rg["rooms"]) + "（名前は注記のみ・絵に描かない）。")
        L.append(f"- 環の通路（画素の床の区間）: 上 y{rg['top']}・下 y{rg['bot']}・左 x{rg['left']}・右 x{rg['right']}。島（地形）: x{rg['island'][0]}–{rg['island'][2]}・y{rg['island'][1]}–{rg['island'][3]}。入口 {rg['side']}辺 {rg['entrance']}。")
    else:
        L.append("- 経路の形: 外周の環に丸い5部屋（左3・右2）。部屋: " + "; ".join(f"{q['name']} 中心{q['c']} 半径{q['r']}" for q in rg["rooms"]) + "（名前は注記のみ・絵に描かない）。")
        L.append(f"- 環の中心線: 上 y{rg['yt']}（床{rg['top']}）・下 y{rg['yb']}（床{rg['bot']}）・左 x{rg['xl']}（床{rg['left']}）・右 x{rg['xr']}（床{rg['right']}）。入口 {rg['side']}辺 {rg['entrance']}。島 bbox {rg['island']}。")
    L.append("- 赤紙6枚の中心（周囲の正方形が全て地形の画素から、最遠点サンプリングで決定。5px刻み）: " + ", ".join(str(q) for q in rg["red"]) + f"（各約{rg['red_size']}px）。")
    return "\n".join(L)


def checks_rooms(mid, m, rg):
    M, lw = m["M"], rg.get("lw", m["lw"])
    out = []
    out.append("寸法（`file` / `identify` で実ファイルを測る。prompt指定・ファイル名は証拠にならない）:\n- [ ] 1920x1080、または 1672x941（その場合は座標に0.871を掛けて比較）。それ以外は failed。リサイズ・切り抜きで通さない。")
    out.append(f"構図（割付図 `verification/body-layout/clean/{mid}.png` と実画素・目視で比較）:\n"
               f"- [ ] 机（木目の木の机）が四辺に約{M['desk']}px見える。その内側に約{M['band']}px幅の土台縁の帯（外{M['foam']}px foamboard・内{M['corr']}px corrugated 断面）が**四辺すべて（北・南・西・東）**で途切れず見える（机→縁取り→波形→天面の順）。模型の天面は画像の内側に収まり画像の縁に接しない。天面は x{M['mx0']}–{M['mx1']}・y{M['my0']}–{M['my1']} 付近。\n"
               f"- [ ] 入口の通路が模型の縁（土台縁の帯の内側）に届く。画像端（机の外）に通路が出ていない。床は模型の外に一画素も無い。")
    s = next(s for s in "NSWE" if m["edges"][s])
    e = m["edges"][s][0]
    ax = "x" if s in "NS" else "y"
    f = sx if ax == "x" else sy
    out.append(f"通路（入口は1本だけ）:\n- [ ] {s}辺: 縁から{EDGE_DEPTH}px内側で {ax} {e['a']}–{e['b']}（1672: {ax} {f(e['a'])}–{f(e['b'])}）、幅約{lw}px（1672: 約{sx(lw)}px）、辺に垂直。他の縁には床が出ていない。遷移範囲の印（色帯・矢印・線・文字）が絵に無い。")
    g = []
    if mid == "BDY-04":
        g.append(f"- [ ] 迷路: 通路は**{rg['links']}本**・行き止まり**{len(rg['dead'])}か所**（丸い閉じた端）・T字{len(rg['tj'])}・曲がり{rg['corners']}。ループなし（入口から各所へ道は1本）。格子は{rg['C']}列x{rg['R']}行・ピッチ{rg['pitch']}px。**通路の配置は割付図（参照1）と一致**（簡略化・正解の道の変更・壁を開けた近道・行き止まりを繋いだループが無い）。")
        g.append(f"- [ ] 通路幅{rg['lw']}px一定（壁の内側基準）・壁の最小厚約{rg['gap_min']}px・仕切りは約8pxの細い帯1本。外周の地形の枠が四辺に約{int(min(rg['frame']))}px。入口は南辺 x{rg['entrance'][0]}–{rg['entrance'][1]}。")
    elif mid == "BDY-15":
        g.append("- [ ] 分岐なしJ字の**1つの袋**（入口の帯→入口の上のドーム→胴の丸い腹（最大約460px）→右へ細くなり約130px→丸く閉じた端）。分岐・横の枝・第2の部屋・出口が無い。ドームが入口の帯の上端と同じ高さ。")
        g.append(f"- [ ] 先端 {rg['tip']}・最下点 {rg['low']} 付近。入口の帯 y{rg['entrance'][0]}–{rg['entrance'][1]}（幅230px）。")
    elif mid == "BDY-16":
        g.append("- [ ] 丸い部屋が**4つ**（各半径160px、2x2）を、**4本の直線の通路（幅230px）の四角い環**でつなぐ。環の中の島は地形。行き止まり・5つ目の部屋・斜めの通路が無い。入口は北辺の1本（左の通路と同じx範囲）で左上の部屋へ。部屋名・心臓の形・臓器の輪郭が絵に無い。")
        g.append("- [ ] 部屋の中心: " + ", ".join(str(q["c"]) for q in rg["rooms"]) + "。")
    else:
        g.append("- [ ] 丸い部屋が**5つ**（左3・半径110px、右2・半径135px）を**外周の環（幅77px）**でつなぐ。入口は北辺中央（x960）の1本で、環の上辺にT字で合流。行き止まり・渦巻き・内側の通路が無い。環の中の島は地形。部屋名・肺の形・臓器の輪郭が絵に無い。")
        g.append("- [ ] 部屋の中心: " + ", ".join(str(q["c"]) for q in rg["rooms"]) + "。")
    out.append("経路の形（本命の検査。割付図の実測値）:\n" + "\n".join(g))
    out.append("材料・質感・装飾（装飾込み1回生成）:\n"
               "- [ ] ① 土台縁の帯に corrugated cardboard 断面と foamboard の縁 ② 仕切りが細く低い corrugated の帯1本（床の幅に含まれない）\n"
               "- [ ] ③ 地形が paper clay の面で、肌色・薄桃・茶系の matte poster paint ④ 赤い折り紙の切片が**ちょうど6枚**（数えて6枚・7枚目なし。全て模型の中の地形の上。模型の外・机・床・土台縁の帯には無い。装飾の下敷きでない）\n"
               "- [ ] ⑤ 机が木目の木の机\n"
               "- [ ] ⑥ 装飾は人体に関係する抽象的な工作物だけ（骨・細胞や粒・筋肉や神経の糸・鼓動のぎざぎざ線・皮膚の彫り・ばんそうこう・毛・ばい菌）。少なくとも6か所の塊。花・葉・雲・星・旗・柵・ハート形・動物・食べ物・風景・臓器の形・血管の網が無い\n"
               "- [ ] ⑥b 装飾の色が肌色・薄桃・クリーム・茶系・象牙色の範囲（緑・青・黄・紫・オレンジが無い）。赤は折り紙6枚だけ\n"
               "- [ ] ⑦ 床には何も置かれず平ら。毛糸が血管・臓器に見える走り方をしていない\n"
               + ("- [ ] ⑧ 迷路の壁の面（約42px）に立体の小物（毛糸の渦・粘土玉・ばい菌・骨）が無い（彫り・点・平らな紙テープのみ）。立体の小物は外周の枠・角の正方形・机だけ\n" if mid == "BDY-04" else "")
               + "- [ ] ⑨ 精霊・炎・水の絵・人物が地形や床に無い（全て小さな手作りの工作物）")
    out.append("許容差（レビュー側基準。生成入力には入れない）: 通路位置 ±25px、幅 ±10%（1672x941 の場合は ×0.871）。床マスクIoU（clean 割付図に対して）≥0.95 を目安。迷路は通路の接続（行き止まりの数・T字の数）の一致を床IoUより優先して見る。")
    return "\n\n".join(out)


def fragment_table_rooms(mid, bundle_text, m, shape):
    base = [r for r in fragment_table(mid, bundle_text, m, shape, slim=(mid == "BDY-04")) if not r[0].startswith("手足末端は閉じ")]
    base = [(a, b, ("P3（入口の幅。画素値はTBDのまま。通路の形は P4）" if a.startswith(("通行幅・pixel/mask", "pixel/mask")) else c)) for a, b, c in base]

    def must(frag):
        if frag not in bundle_text:
            die(f"照合表の原文断片が束に無い: {frag!r}")
        return frag
    extra_f = {
        "BDY-04": lambda: [(must("頭・脳の迷路通路"), "registry/spec/checklist", "P3・P4（迷路の通路。通路の列挙・行き止まり・T字・曲がりの数は clean 画素の実測。ステンシル宣言・ランドマークも実測）"),
                   (must("脳は迷路状通路"), "art-direction:199", "P4（迷路状）"),
                   (must("脳は迷路状ということだな"), "Issue #142", "P4（迷路状。通路の配置は参照1のとおり）"),
                   (must("この MAP の通路はキャラクター1人分＝その1/3＝77px"), "[注記]（ビルダーの数値事実）", "P3・P4（1人幅77px・格子13x6）")],
        "BDY-15": lambda: [(must("分岐なしJ字の1袋"), "Issue #142", "P4（分岐なしJ字の1つの袋。docs の『単純な分岐室』は、この MAP の部屋は1つの袋、の形で P4 が明示）"),
                   (must("最大幅460px"), "Issue #142", "P4（胃体の最大幅約460px・入口の2倍）"),
                   (must("幽門（130px・丸く閉じた行き止まり）"), "Issue #142", "P4（幽門約130px・丸い閉じた端）")],
        "BDY-16": lambda: [(must("心臓=解剖学の4つの部屋（右心房・右心室・左心房・左心室）を抽象的な4つの部屋と通路で表す"), "Issue #142", "P4（丸い4部屋を四角い環の通路でつなぐ。部屋名は絵に描かない。docs の『単純な分岐室』は、この MAP の部屋は4つの丸い部屋、の形で P4 が明示）"),
                   (must("心臓は自然にすればいい"), "Issue #142", "P4（心臓は自然に。本人の左側＝画面右は BDY-02 の南辺の位置）")],
        "BDY-17": lambda: [(must("肺BDY-17は人間の肺が渦巻きでないため行き止まりなし（外周の環に右肺3葉=画面左・左肺2葉=画面右の丸い5部屋"), "topology", "P3・P4（外周の環・丸い5部屋・通路幅77px・行き止まりなし）"),
                   (must("案A（外周の環）"), "Issue #142", "P4（案A。渦巻き＝案Bは不採用）"),
                   (must("通路をキャラ１人分の幅で左から上にぐるっとまわしては"), "Issue #142", "P3・P4（入口は北辺中央・通路はキャラ1人分幅・左から上へぐるっと一周する環）")],
    }
    extra = extra_f[mid]()
    return base + extra


def build_one(mid, out_dir, bl, force_redo=False):
    """装飾込み1回生成（onepass）の prompt を書く。参照2枚（clean 割付図・材料見本）・様式参照なし・SOURCE TEXT 逐語。"""
    if mid in ON_HOLD:
        die(f"{mid}: 保留（原文未確定）。{ON_HOLD[mid]}が未確定のため、形を発明せず kako-jun の決定を待つ。", 3)
    if mid in ADOPTED and not force_redo:
        die(f"{mid}: 採用済み（旧プールの装飾）。既定は再生成しない。作り直しは kako-jun 2026-10-22『つくりなおせ』（Issue #142）の明示オプション --force-redo で、BDY-02・BDY-09 だけ。")
    if mid not in TARGETS:
        die(f"{mid}: 対象外（対象 = {', '.join(TARGETS)}）")
    m = measure(mid, bl)
    bundle = build_bundle(mid, m["lw"])
    _, _, _, _, portals = bl.build_model()
    if mid == "BDY-02":
        hd = measure_hall(m, bl)
        shape = "hall"
        P = build_prompt_hall(mid, m, hd, bl)
        ctx = dict(report=report_hall(m, hd), checks=checks_hall(mid, m, hd), generic=True, wall=True)
        refs = reference_text_hall()
        wrapper = wrapper_onepass(out_name_onepass(mid), "five")
        warns = ["決定済み: 首は1本で上で頭（北）と口（北東）に分岐・南辺は肺=左・下半身=中央・心臓=右・左右は本人から見る（kako-jun 2026-10-22。Issue #142 の決定コメント）。",
                 "作り直し: 採用済みの BDY-02（旧プール・フェルトの花入り）を新プールで作り直す（kako-jun 2026-10-22『つくりなおせ』）。採用時の構造記述（段階1）を保ち、装飾・色・赤紙・土台縁・壁の細さは共通部品。壁（広間の弧を含む）は細い corrugated 帯＋毛糸1本で床の幅を守る。広間の壁の弧は段ボール茶（青灰でない）。",
                 "座標・角度は clean 画素の実測（body_layout の定数と照合済み）。別コードの再測定は verification/body-layout/remeasure_bdy02.py <送信文>。",
                 "装飾込み1回生成（onepass）: 参照は2枚（clean 割付図・材料見本）。様式参照画像は使わない。",
                 "独立レビュー（opus。2026-10-22）は条件付き可。指摘（装飾が幾何を圧倒・P4冒頭の環状の誤読・P10の赤紙の曖昧語・許可品目の矛盾・禁止語）を反映済み: P9 を圧縮し色の段落は P8 に1回だけ、P4 は4区間だけ壁と明記、赤紙は6枚の領域と座標を固定、許可品目は主役・脇役が使うものだけ。",
                 "[注記] 通路幅は天面幅比0.14=230px。の行は docs 由来でなく、ビルダーが clean 実測から原文束の末尾に加えた注記（照合表の docs 行数には含めない）。",
                 "腕・心臓・口の曲がりの外角の丸みは半径115px（clean の帯は折れ点に半径=幅の半分の円を置いて描く。口は実測で確認、左腕・心臓も外角の最遠画素が116px、右腕は約116〜120px）。肺は広間の床が重なり画素では分離できないが同じ作り。"]
    elif mid in ROOM_MAPS:
        rg = measure_rooms(mid, m, bl)
        shape = "rooms"
        P = build_prompt_rooms(mid, m, rg, bl)
        ctx = dict(report=report_rooms(mid, m, rg), checks=checks_rooms(mid, m, rg), generic=True, lw=rg.get("lw", m["lw"]))
        refs = reference_text_rooms(mid, m, rg)
        wrapper = wrapper_onepass(out_name_onepass(mid), "four")
        warns = ["決定済み: 脳=迷路・胃=分岐なしJ字の1袋・心臓=2x2の丸い4部屋の環・肺=案A（外周の環・行き止まりなし）。kako-jun 決定・モック承認（2026-10-22。Issue #142）。"
                 "docs の『単純な分岐室』『分岐室』は逐語の原文として残る。この MAP の形は P4 が肯定形で明示している（原文束の外の自作部分）。",
                 "座標・半径・通路の接続は clean 画素の実測（body_layout の SPECS と照合済み）。別コードの再測定: verification/body-layout/remeasure_body_rooms.py [BDY-xx]（prompts/BDY-xx-prompt-send.txt の数値を clean 画素と照合）。",
                 "装飾込み1回生成（onepass）: 参照は2枚（clean 割付図・材料見本）。様式参照画像は使わない。壁・仕切りは細い corrugated の帯1本（迷路 約8px・他 約12px）＋毛糸1本で、床の幅は壁の内側基準で守る。",
                 "赤紙6枚は clean の地形で周囲の正方形が全て地形の点から決定的に選び、座標を本文に固定した（BDY-02 の方式）。",
                 "部屋名（右心房など）は原文束にだけ現れ、絵には描かない。本文は部屋を丸い床と呼び、臓器の輪郭を描かせない。",
                 "生成前の独立レビューは未実施（SKILL: 生成可には独立レビュー通過が必要）。"]
        if mid == "BDY-04":
            warns.append("迷路の記述（2026-10-22 独立レビュー反映）: P4 の先頭に『ステンシル宣言』（cream=床・他=地形・通路を動かさない・13x6格子・木・幅77px・壁は幅の約0.55倍）、全体構造のランドマーク6個（clean 画素の実測から機械検査）、"
                         "格子の全通路の行・列ごとの列挙、本数77・行き止まり11・T字10・曲がり38。経路の曲がり点列は外した。原文束（SOURCE TEXT）は WHAT TO DRAW と REFERENCE の後ろ（wrapper → DRAW → REFERENCE → SOURCE）。"
                         "原文束は迷路に無関係な行（topology 690・692・体内の17MAP表・decisions の体内入口・research の17MAP行）と Issue の『櫛型より複雑にする』決定行を載せない（slim）。"
                         "生成が迷路を簡略化する危険があり、生画像で通路の接続を必ず確認する（再生成は最大2回まで許可）。")
        if mid in ("BDY-04", "BDY-17"):
            warns.append("入口の帯の幅は1人幅（77px）。原文に無く、割付図（承認済みモック）どおり。")
    else:
        dg = measure_diag(mid, m, bl, portals)
        shape = dg["shape"]
        for s_ in "NSWE":
            for e in m["edges"][s_]:
                e["poly"] = dg["path_pts"][[i for i, pa in enumerate(bl.SPECS[mid]["paths"]) if e["port"] in pa["pts"]][0]]
        P = build_prompt_diag(mid, m, dg, bl)
        ctx = dict(report=report_diag(mid, m, dg), checks=checks_diag(mid, m, dg), generic=True)
        n_ = sum(len(v) for v in m["edges"].values())
        refs = reference_text_diag(n_, shape)
        wrapper = wrapper_onepass(out_name_onepass(mid), "four")
        warns = [w for w in warnings_for(mid, m, shape, []) if not w.startswith("参照3（BDY-02 採用画像）")]
        for sv in dg["slivers"]:
            warns.append(f"警告: {sv['side']}辺の2本の間に地形のくさび（縁で幅{sv['g']}px・奥行{sv['depth']}px）。幅{SLIVER_NARROW}px未満の先端側{sv['narrow_len']}pxは仕切りを1本の低い尾根に合わせ、毛糸は1本まで。")
    if mid in ADOPTED and mid != "BDY-02":
        warns.append("作り直し: 採用済みの BDY-09（旧プール・フェルトの花入り）を新プールで作り直す（kako-jun 2026-10-22『つくりなおせ』）。")
    if mid != "BDY-02" and mid not in ROOM_MAPS:
        warns.append("装飾込み1回生成（onepass）: 参照は2枚（clean 割付図・材料見本）。様式参照画像は幾何を崩す疑いがあるので使わない（様式は本文の文章のみ）。斜めの帯・折れ点・合流点・末端の座標は clean 画素の実測（body_layout の折れ線と照合済み）。")
    if mid in ("BDY-09", "BDY-12"):
        warns.append("決定済み: 折れ点は膝の1つだけ・進行方向の変化35度の鈍角（kako-jun 指示 2026-10-22『２回曲げちゃダメだ。関節は１つであるべき』『鈍角にしろ』。body_layout.py THIGH_KNEES）。")
    head = (f"Generate ONE image: the final field background for map {mid} ({LABEL[mid]}, of the imaginary human body inside which the story travels). "
            f"Do not generate any other map.")
    source = ("=== SOURCE TEXT (verbatim, do not paraphrase) ===\n" + bundle.text().rstrip("\n"))
    if mid in ROOM_MAPS:  # 原文束が最後に来る4枚だけ、原文束の終わりを明示する（原文束の後ろの文が指示と誤読されない）
        source += "\n\n" + END_SOURCE
    draw = ("=== WHAT TO DRAW (positive description; sentence numbers P1.. are referenced below) ===\n"
            + "\n".join(P[f"P{i}"] for i in range(1, 15)))
    if mid in ROOM_MAPS:  # wrapper → DRAW → REFERENCE → SOURCE（原文束は最後。台帳原文ゲートは添付を要求するだけで順序は不問。迷路の形の指示を先頭に近づける）
        body = head + "\n\n" + draw + "\n\n" + refs + "\n\n\n" + source
    else:
        body = (head + "\n\n" + source + "\n\n\n" + draw + "\n\n" + refs)
    table = fragment_table_rooms(mid, bundle.text(), m, shape) if mid in ROOM_MAPS else fragment_table(mid, bundle.text(), m, shape)
    send = wrapper + "\n" + body + "\n"
    out_name = out_name_onepass(mid)
    md = render_md(mid, m, bl, bundle, P, shape, warns, wrapper, None, body, table, out_name,
                   hashlib.sha256(send.encode("utf-8")).hexdigest(), ctx02=ctx)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"{mid}-prompt.md").write_text(md, encoding="utf-8")
    (out_dir / f"{mid}-prompt-send.txt").write_text(send, encoding="utf-8")
    nb, bad = verify_bundle_text(md)
    if bad:
        die(f"{mid}: 原文束が docs と不一致: {bad}")
    lk = leak_check(send, mid)
    if lk:
        die(f"{mid}: 送信文に台座語・内部語: {lk}")
    nd, ni, bad2 = verify_send_text(send, bundle.issue_lines)
    if bad2 or nd != nb:
        die(f"{mid}: 送信文の原文束が docs/Issue と不一致（docs {nd}件 vs md {nb}件）: {bad2}")
    print(f"{mid} onepass: OK 形={shape} 通路={sum(len(v) for v in m['edges'].values())} "
          f"区画(広/狭)={sum(r['wide'] for r in m['regions'])}/{sum(not r['wide'] for r in m['regions'])} 原文行照合={nb}件一致 警告={len(warns)}")
    for w in warns:
        if w.startswith(("TBD", "警告")):
            print(f"  ! {w}")
    return md, send


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("map_id", nargs="?", help="BDY-01 など")
    ap.add_argument("--out", help="出力ディレクトリ")
    ap.add_argument("--all", action="store_true", help="対象15枚すべて（BDY-01・03〜08・10〜17。採用済みの BDY-02・09 は含めない。作り直しは --force-redo で1枚ずつ）")
    ap.add_argument("--force-redo", action="store_true", help="採用済みの BDY-02・BDY-09 を新プールで作り直す（kako-jun 2026-10-22『つくりなおせ』。既定は採用済み保護で拒否。--all には含めない）")
    ap.add_argument("--plan", metavar="OUT_MD", help="MAPごとの装飾計画の一覧表を出力して終了")
    ap.add_argument("--verify-send", metavar="SEND_TXT", help="既存の -prompt-send.txt の SOURCE TEXT を docs/Issue と再照合して終了")
    ap.add_argument("--verify-bundle", metavar="PROMPT_MD", help="既存の -prompt.md の原文束を docs の行番号どおりに再照合して終了")
    a = ap.parse_args()
    if a.plan:
        write_decoration_plan(a.plan)
        print(f"装飾計画を出力: {a.plan}")
        sys.exit(0)
    if a.verify_send:
        txt = Path(a.verify_send).read_text(encoding="utf-8")
        if "=== SOURCE TEXT" not in txt:
            print("SOURCE TEXT がない送信文。照合できない（onepass の送信文は必ず SOURCE TEXT を持つ）")
            sys.exit(1)
        mm = re.search(r"final field background for map (BDY-\d+)", txt)
        bundle = build_bundle(mm.group(1) if mm else "BDY-01", 0)
        nd, ni, bad = verify_send_text(txt, bundle.issue_lines)
        print(f"docs {nd} 件・Issue {ni} 行を照合、不一致 {len(bad)} 件 {bad}")
        sys.exit(1 if bad else 0)
    if a.verify_bundle:
        n, bad = verify_bundle_text(Path(a.verify_bundle).read_text(encoding="utf-8"))
        print(f"照合 {n} 件、不一致 {len(bad)} 件 {bad}")
        sys.exit(1 if bad else 0)
    if not a.out or not (a.all or a.map_id):
        ap.error("map_id（または --all）と --out が要る")
    check_deco_plan()
    bl = load_layout()
    if a.force_redo and (a.all or a.map_id.upper() not in ADOPTED):
        ap.error("--force-redo は BDY-02・BDY-09 を1枚ずつ指定したときだけ（--all には含めない）")
    ids = [t for t in TARGETS if t not in ADOPTED] if a.all else [a.map_id.upper()]
    for mid in ids:
        build_one(mid, Path(a.out), bl, a.force_redo)


if __name__ == "__main__":
    main()
