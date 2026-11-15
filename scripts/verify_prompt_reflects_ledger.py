#!/usr/bin/env python3
"""台帳（docs/ledger/*.yaml）の内容が、生成される imagegen 編集プロンプトに漏れなく反映されているかを検査する。
  uv run python3 scripts/verify_prompt_reflects_ledger.py                 # 全MAPのプロンプトを導出して検査。違反があれば exit 1
  uv run python3 scripts/verify_prompt_reflects_ledger.py --from-json F   # 導出済みの JSON（oblique_prompt_probe.py の出力）を使う
  uv run python3 scripts/verify_prompt_reflects_ledger.py --maps TRM-05,TRM-05-fire   # 対象MAPを絞る
  LEDGER_ROOT=/path/to/root ...                                 # root 差し替え（テスト用）

プロンプトは tools/oblique_prompt_probe.py が oblique_build と同じ導出で作る（画像生成 API は呼ばない）。
必須キーが揃わないMAPはプロンプトを組めないので『ゲートで停止』として対象外に表示する。
屋外MAPの建物・塀・門の look 未記入は生成の起動だけを止める理由（stopped）。プロンプトは組んで反映検査を走らせ、理由は別行で表示する。

検査（生成可能なMAPごと）:
  (i)   そのMAPに該当する有効な決定のうち プロンプト出力=必須 のものは、[決定ID] と決定の要点が逐語で DECISIONS 節に現れ、
        必須語が（注記を除いた本文に）現れ、禁止語は決定・FORBIDDEN 節・否定表現・決定参照つき行以外に現れない
  (ii)  採用要素（継承要素）: [採用要素ID]・要素・確認語がプロンプトに現れる。素材IDが有る有効な行は、元MAPの採用画像が
        REFERENCE IMAGES に（素材表と同じパスで）現れる
  (iii) 特徴(自由記述)は MAP・建物・部位・窓列・要素・窓・端・採用要素・決定のどれも FEATURES 節（決定は DECISIONS 節）にそのまま現れる
  (iv)  建物窓列に紐づく窓（渡り廊下棟の連窓など）が、その窓を持つ全MAP（屋内・外観）の WINDOWS 節に個数・位置つきで一致して現れる
  (v)   回帰アンカー: 過去に漏れた事例（畳・化石の石・-fire の勝手口・火事版の上半分・渡り廊下の窓列）を台帳側の件数に依らず
        固定の期待で検査する（台帳から記述を消されても検出するため、ここに期待をハードコードする）
  (vi)  時期差分MAP（-kids・-fire など。台帳 時期差分 に行があるもの）は、基準MAPを依存MAPに持ち、REFERENCE IMAGES に基準MAPの行
        （確定画像のパス、未採用なら『未確定』）と台帳 プロンプト文面.PR.reference.base-era の使い方の文が現れる（#193）。
        TRM-05-kids・TRM-05-fire は台帳側の依存を消されても検出するよう、基準MAPをここにもハードコードする
  (vii) エリア固定（#195）: 装飾プールを持つMAPのプロンプトに、そのプールのエリアの エリア固定（机の天面・台座の素材・木の種類と見た目）が全部現れ、
        別エリアのエリア固定の本文（そのエリア固有の台座・木）は現れない（他エリアの素材の漏れ）。エリア固定を持たない・プールが無いMAPは対象外
  (viii) コミット済みの edit-prompt（docs/production/oblique-mocks/MAP/MAP-edit-prompt.txt）の DECISIONS の決定ID一覧が、台帳から今出る一覧と一致する
        （包含検査では見えない『余分な決定・古さ』を検出する。古いプロンプトを imagegen に渡さないため。#191）。
        main の時点から古いままの MAP は KNOWN_STALE_COMMITTED に理由つきで明示して除外する（本検査では再生成しない）
"""
import json
import os
import re
import shlex
import subprocess
import sys

import ledger_yaml as LY

A = re.ASCII
WS = " \t\r\n\f\v"



def die(msg):
    """Ruby の abort/warn と同じく、末尾が改行なら改行を足さずに stderr へ出して exit 1"""
    sys.stderr.write(msg if msg.endswith("\n") else msg + "\n")
    sys.exit(1)

def strip(s):
    return s.strip(WS + "\0")


def lines_nl(text):
    return re.findall(r"[^\n]*\n|[^\n]+", text)


def chomp_lines(text):
    """Ruby の text.lines.map(&:chomp)"""
    return [re.sub(r"(\r\n|\n|\r)\Z", "", l) for l in lines_nl(text)]


def rsplit(s, pat):
    """Ruby の String#split（末尾の空要素を落とす）"""
    out = re.split(pat, s)
    while out and out[-1] == "":
        out.pop()
    return out


def to_i(s):
    m = re.match(r"\s*([+-]?\d[\d_]*)", s or "", A)
    return int(m.group(1).replace("_", "")) if m else 0


def to_f(s):
    m = re.match(r"\s*([+-]?\d[\d_]*(?:\.\d+)?(?:[eE][+-]?\d+)?)", s or "", A)
    return float(m.group(1).replace("_", "")) if m else 0.0


def inspect_n(n):
    return "nil" if n is None else str(n)


VARIANT_RE = re.compile(r"-(kids|fire|burnt|wc)\Z")
# 否定・指示の文脈（禁止語がそのまま書いてあっても『描かない』と言っているだけの節）。
# 否定は禁止語と**同じ節**（。、，,；; 区切り）にあるものだけが免除になる。
NEGATION_RE = re.compile(r"描かない|使わない|置かない|入れない|足さない|でなく|ではなく|にせず|禁止|不可|（決定 ")
CLAUSE_SPLIT = r"[。、，,；;]"
PROBE = ".claude/skills/sit-field-background/tools/oblique_prompt_probe.py"

# 過去に漏れた事例。maps の全MAPで: decisions の [決定ID] と要点が現れ、words が現れ、
# leak（正規表現）は決定・否定表現の行以外に現れない。door_wall は『勝手口』を含む行に別の壁方角を書かない。
ANCHORS = [
    {"id": "tatami", "maps": "TRM-02 TRM-03 TRM-04 TRM-05 TRM-05-kids TRM-05-fire".split(), "decisions": ["TRM.no-tatami"], "leak": "(?<!石)畳",
     "what": "畳の語（畳を描かない決定が出て、畳が本文に漏れない）"},
    {"id": "fossil-stone", "maps": "TRM-05 TRM-05-kids TRM-05-fire".split(), "decisions": ["TRM-05.fossil", "TRM-05.stone-pos"], "words": ["茶色と黒", "右上隅"],
     "leak": "アンモナイト", "what": "化石の石（決定表から展開される）"},
    {"id": "fossil-state", "maps": ["TRM-05-fire"], "decisions": ["TRM-05.fossil-state"], "words": ["割れかけ"], "what": "火事版の化石の状態"},
    {"id": "door-back-fire", "maps": ["TRM-05-fire"], "decisions": ["TRM-05.door-back", "TRM-05.door-back-fire"], "words": ["北壁", "燃えカス"],
     "door_wall": "北壁", "what": "-fire の勝手口は北壁（西壁などにならない）"},
    {"id": "fire-upper-half", "maps": ["TRM-05-fire"], "decisions": ["TRM-05-fire.upper-half", "TRM-05.fire"], "words": ["上半分だけ", "上半分"], "what": "火事版は上半分だけが燃える指示"},
    {"id": "corridor-windows", "maps": ["TRM-03", "TRM-04"], "decisions": ["TRM.building-shared"], "words": ["連窓"],
     "corridor": {"BLD-TRM-corridor-w.south-wins": 3, "BLD-TRM-corridor-e.south-wins": 3}, "what": "渡り廊下棟の窓列（屋内・外観で一致）"},
]

# コミット済みの edit-prompt が古いまま（決定ID一覧が台帳と違う）なのに再生成しない MAP。理由つきで書く。再生成したら外す。
KNOWN_STALE_COMMITTED = {}

COMPOUND_OK = {"畳": ["石畳"]}
BARE_NOUN_RE = re.compile(r"[^はをがにでも]{1,8}\Z")
REQUIRED_BASE = {"TRM-05-kids": "TRM-05", "TRM-05-fire": "TRM-05"}
AREA_FIXED_ITEMS = re.compile(r"(?:desk\.look|slab\.look|trees\.(?:pine|deadtree|kinds\[\d+\])\.(?:label|look))\Z", A)
CORE_WORDS = ["手作りミニチュア", "綿の雪", "段ボール"]
PHOTOREAL_AFFIRM = re.compile(r"(?:実写|フォトリアル|写真のよう|実物のよう)[^。\n]{0,12}(?:で描|に描|仕上げ|にする|とする)")
CORE_NEGATE = re.compile(r"(?:ミニチュア|工作|綿|段ボール)(?:の素材)?(?:は|を)?[^。\n]{0,6}(?:ではなく|にしない|使わない|不要|描かない)|本物の雪|実物の雪")
REAL_WORDS = "版築 釉薬瓦 戸室石 錆 濡れた艶 藁すさ".split()
CRAFT_MATERIAL_WORDS = "爪楊枝 割り箸 鉄道模型 綿 マッチ棒".split()


def first_compact(it):
    for x in it:
        if x is not None:
            return x
    return None


class PromptReflection:
    def __init__(self, records, root=LY.ROOT, only=None):
        self.root = root
        self.t = LY.load_all()
        self.records = [r for r in records if only is None or r["map_id"] in only]
        self.errors = []
        self.skipped = []
        self.stopped = []
        self.checked = []
        self.slab_lines = {}
        self.desk_lines = {}
        self._decision_clauses = None
        self.prompt = ""
        self.final = ""
        self.lines = []

    def err(self, map_id, msg):
        self.errors.append(f"{map_id}: {msg}")

    @staticmethod
    def base_of(id_):
        return VARIANT_RE.sub("", id_, count=1)

    def era_of(self, id_):
        b = self.base_of(id_)
        return "" if id_ == b else id_[len(b) + 1:]

    @staticmethod
    def split(s):
        return [x for x in (strip(x) for x in (s or "").split(";")) if x]

    def expand(self, spec):
        out = []
        for tok in self.split(spec):
            m = re.fullmatch(r"TRM-(\d\d)\.\.TRM-(\d\d)", tok, A)
            if m:
                out.extend("TRM-%02d" % n for n in range(int(m.group(1)), int(m.group(2)) + 1))
            else:
                out.append(tok)
        return out

    def targets(self, map_id, spec):
        toks = self.expand(spec)
        return map_id in toks or self.base_of(map_id) in toks

    def run(self):
        for rec in self.records:
            id_ = rec["map_id"]
            if rec.get("gated"):
                self.skipped.append([id_, rec["gated"]])
                continue
            if rec.get("stopped"):
                self.stopped.append([id_, rec["stopped"]])
            self.checked.append(id_)
            self.prompt = rec["prompt"]
            self.final = rec["prompt_final"] if rec.get("prompt_final") is not None else self.prompt
            self.lines = chomp_lines(self.prompt)
            self.check_decisions(id_)
            self.check_inherits(id_)
            self.check_free_text(id_)
            self.check_window_rows(id_)
            self.check_base_reference(id_)
            self.check_area_fixed(id_)
            self.check_reality(id_)
            self.check_core_constraints(id_)
            self.check_craft(id_)
            self.check_committed_prompt(id_)
        self.check_anchors()
        self.check_swatch_sheet_in_refs()
        self.check_slab_props_varied()
        self.check_desk_props_varied()
        return self

    # ---- プロンプトの節: 見出し行から次の空行まで
    def section(self, prefix):
        i = next((k for k, l in enumerate(self.lines) if l.startswith(prefix)), None)
        if i is None:
            return []
        out = []
        for l in self.lines[i + 1:]:
            if not strip(l):
                break
            out.append(l)
        return out

    def decision_lines(self):
        return self.section("DECISIONS（")

    @staticmethod
    def strip_annot(line):
        return re.sub(r"（(?:必須語: [^）]*)?(?: / )?(?:禁止語: [^）]*)?）\Z", "", line, count=1)

    def forbidden_section(self):
        return self.section("FORBIDDEN（")

    def leak_lines(self, with_inherited=False):
        excluded = self.decision_lines() + self.forbidden_section()
        if not with_inherited:
            excluded = excluded + self.section("INHERITED ELEMENTS（")
        return [l for l in self.lines if l not in excluded]

    def leaking_clause(self, line, pred, negation=True):
        """行の中で、述語に一致する節（否定を含む節は除く）。無ければ None。"""
        if not negation and self.annotated_expansion(line):
            return None
        clauses = rsplit(line, CLAUSE_SPLIT)
        for i, c in enumerate(clauses):
            if not pred(c):
                continue
            if negation:
                nxt = clauses[i + 1] if i + 1 < len(clauses) else None
                if not (NEGATION_RE.search(c) or self.enumerated_under_negation(c, nxt)):
                    return c
            elif strip(c) not in self.decision_clauses():
                return c
        return None

    @staticmethod
    def enumerated_under_negation(clause, following):
        return following is not None and bool(NEGATION_RE.search(following)) and bool(BARE_NOUN_RE.match(strip(clause)))

    def annotated_expansion(self, line):
        m = re.search(r"（決定 ([^）]+)）\s*\Z", line, A)
        if not m:
            return False
        ids = [i for i in re.split(r"[,、\s]+", m.group(1), flags=A) if i]
        return bool(ids) and all(any(d["決定ID"] == i and d["状態"] == "有効" for d in self.t["決定"]) for i in ids)

    def decision_clauses(self):
        if self._decision_clauses is None:
            out = []
            for d in self.t["決定"]:
                if d["状態"] == "有効":
                    out.extend(strip(c) for c in rsplit(d["決定の要点"], CLAUSE_SPLIT))
            self._decision_clauses = [c for c in out if c]
        return self._decision_clauses

    @staticmethod
    def mentions(line, word):
        for c in COMPOUND_OK.get(word, []):
            line = line.replace(c, "")
        return word in line

    # ---- (i)
    def active_decisions(self, map_id):
        return [d for d in self.t["決定"] if d["状態"] == "有効" and d["プロンプト出力"] == "必須" and self.targets(map_id, d["対象MAP"])]

    def check_decisions(self, map_id):
        dl = self.decision_lines()
        leak = self.leak_lines()
        for d in self.active_decisions(map_id):
            did = d["決定ID"]
            line = next((l for l in dl if l.startswith(f"- [{did}] ")), None)
            if line is None:
                self.err(map_id, f"決定 {did} がプロンプトの DECISIONS 節に現れない（プロンプト出力=必須・有効・対象MAP）")
                continue
            if d["決定の要点"] not in self.strip_annot(line):
                self.err(map_id, f"決定 {did} の要点が DECISIONS 節に逐語で現れない（台帳『決定の要点』と違う）")
            for w in self.split(d["必須語"]):
                pool = [self.strip_annot(l) for l in dl] + [l for l in self.lines if l not in dl]
                if not any(w in l for l in pool):
                    self.err(map_id, f"決定 {did} の必須語『{w}』がプロンプト本文に現れない")
            for w in self.split(d["禁止語"]):
                hit = first_compact(self.leaking_clause(l, lambda c, w=w: self.mentions(c, w)) for l in leak)
                if hit is not None:
                    self.err(map_id, f"決定 {did} の禁止語『{w}』がプロンプトに現れる: 「{strip(hit)[:80]}」")

    # ---- (viii)
    @staticmethod
    def decision_ids(lines):
        out = []
        for l in lines:
            m = re.match(r"- \[([^\]]+)\] ", l)
            if m:
                out.append(m.group(1))
        return out

    def check_committed_prompt(self, map_id):
        path = os.path.join(self.root, "docs/production/oblique-mocks", map_id, f"{map_id}-edit-prompt.txt")
        if not os.path.exists(path):
            return
        with open(path, encoding="utf-8", newline="") as f:
            committed = chomp_lines(f.read())
        i = next((k for k, l in enumerate(committed) if l.startswith("DECISIONS（")), None)
        had = []
        if i is not None:
            blk = []
            for l in committed[i + 1:]:
                if not strip(l):
                    break
                blk.append(l)
            had = self.decision_ids(blk)
        want = self.decision_ids(self.decision_lines())
        if sorted(had) == sorted(want):
            return
        if map_id in KNOWN_STALE_COMMITTED:
            return
        extra = [x for x in had if x not in want]
        miss = [x for x in want if x not in had]
        self.err(map_id, f"コミット済み {os.path.basename(path)} の決定ID一覧が台帳から今出る一覧と違う（古い。oblique_build.py を再実行）: "
                         f"余分={','.join(extra) if extra else 'なし'} / 不足={','.join(miss) if miss else 'なし'}")

    # ---- (ii)
    def inherit_rows(self, map_id):
        return [a for a in self.t["採用要素"] if a["状態"].split("（")[0] in ("有効", "記録") and self.targets(map_id, a["継承先MAP"])]

    def check_inherits(self, map_id):
        inh = self.section("INHERITED ELEMENTS（")
        refs = self.section("REFERENCE IMAGES（")
        for a in self.inherit_rows(map_id):
            aid = a["採用要素ID"]
            line = next((l for l in inh if l.startswith(f"- [{aid}] ")), None)
            if line is None:
                self.err(map_id, f"採用要素 {aid} がプロンプトの INHERITED ELEMENTS 節に現れない")
                continue
            for label, w in (("要素", a["要素"]), ("内容", a["内容"]), ("確認語", a["確認語"])):
                if w and w not in line:
                    self.err(map_id, f"採用要素 {aid} の{label}『{w[:30]}』がプロンプトに現れない")
            if not a["素材ID"]:
                continue
            mat = next((m for m in self.t["素材"] if m["素材ID"] == a["素材ID"]), None)
            path = mat["パス"] if mat else None
            if mat is None or not path:
                self.err(map_id, f"採用要素 {aid}: 素材 {a['素材ID']} が素材表に無い、またはパスが空（参考画像にできない）")
            elif not any(l.startswith(f"- {a['元MAP']}: {path}") for l in refs):
                self.err(map_id, f"採用要素 {aid}: 元MAP {a['元MAP']} の採用画像 {path} が REFERENCE IMAGES に現れない（plan の depends_on か素材表を確認）")

    # ---- (vi)
    def check_base_reference(self, map_id):
        era = self.era_of(map_id)
        if not era:
            return
        base = self.base_of(map_id)
        in_ledger = any(r["MAP_ID"] == base and r["時期"] == era for r in self.t["時期差分"])
        if not (in_ledger or map_id in REQUIRED_BASE):
            return
        deps = [v for r in self.t["時期差分"] if r["MAP_ID"] == base and r["時期"] == era and r["項目"] == "依存" for v in self.split(r["値"])]
        if base not in deps:
            self.err(map_id, f"時期差分MAPの依存に基準MAP {base} が無い（台帳 時期差分.依存。基準の確定画像を参照に含める #193）")
        refs = self.section("REFERENCE IMAGES（")
        if not any(l.startswith(f"- {base}: ") for l in refs):
            self.err(map_id, f"基準MAP {base} が REFERENCE IMAGES に現れない（時期差分MAPは基準の確定画像、未採用なら『未確定』で blocked を示す）")
        tpl = next((r for r in self.t["プロンプト文面"] if r["文面ID"] == "PR.reference.base-era"), None)
        if tpl is None:
            self.err(map_id, "台帳 プロンプト文面.PR.reference.base-era が無い")
        elif not any(l == tpl["文面"].replace("{base}", base).replace("{era}", era) for l in refs):
            self.err(map_id, "基準参照の使い方の文（プロンプト文面.PR.reference.base-era）が REFERENCE IMAGES 節に現れない")

    # ---- (iii)
    def free_texts(self, map_id):
        base = self.base_of(map_id)
        era = self.era_of(map_id)
        t = self.t
        m = next((r for r in t["MAP"] if r["MAP_ID"] == base), None)
        bids = [b for b in self.split(m["建物ID"]) if b not in ("該当なし", "なし")] if m else []
        F = "特徴(自由記述)"
        out = []
        if m:
            out.append(["MAP", m["MAP_ID"], m[F]])
        for a in t["エリア"]:
            if m and a["エリアID"] == m["エリアID"]:
                out.append(["エリア", a["エリアID"], a[F]])
        out += [["建物", b["建物ID"], b[F]] for b in t["建物"] if b["建物ID"] in bids]
        out += [["建物部位", p["部位ID"], p[F]] for p in t["建物部位"] if p["建物ID"] in bids]
        out += [["建物窓列", w["窓列ID"], w[F]] for w in t["建物窓列"] if w["建物ID"] in bids]
        out += [["建物関係", r["通番"], r[F]] for r in t["建物関係"] if r["建物A"] in bids or r["建物B"] in bids]
        out += [["建物時期差分", f"{r['建物ID']}/{r['時期']}/{r['部位ID']}", r[F]] for r in t["建物時期差分"] if r["建物ID"] in bids and r["時期"] == era]
        for tbl, key in (("要素", "要素ID"), ("窓", "窓ID"), ("端", "端ID")):
            out += [[tbl, r[key], r[F]] for r in t[tbl] if r["MAP_ID"] == base and r["適用時期"] in ("", era)]
        out += [["接続", f"{r['端A']}⇄{r['端B']}", r[F]] for r in t["接続"] if (rsplit(r["端A"], r"\.") or [""])[0] == base or (rsplit(r["端B"], r"\.") or [""])[0] == base]
        out += [["素材", r["素材ID"], r[F]] for r in t["素材"] if self.base_of(r["所有者ID"]) == base and r["状態"] == "採用"]
        out += [["採用要素", a["採用要素ID"], a[F]] for a in self.inherit_rows(map_id)]
        return [x for x in out if x[2]]

    def check_free_text(self, map_id):
        feat = "\n".join(self.section("FEATURES（"))
        for tbl, id_, text in self.free_texts(map_id):
            if text not in feat:
                self.err(map_id, f"{tbl} {id_} の特徴(自由記述)が FEATURES 節にそのまま現れない: 「{text[:40]}」")
        dl = "\n".join(self.decision_lines())
        for d in self.active_decisions(map_id):
            t = d["特徴(自由記述)"]
            if t and t not in self.prompt and t not in dl:
                self.err(map_id, f"決定 {d['決定ID']} の特徴(自由記述)がプロンプトに現れない: 「{t[:40]}」")

    # ---- (iv)
    def window_rows(self, map_id):
        base = self.base_of(map_id)
        era = self.era_of(map_id)
        out = {}
        for w in self.t["窓"]:
            if w["MAP_ID"] == base and w["適用時期"] in ("", era) and w["建物窓列ID"]:
                out.setdefault((w["壁"], w["建物窓列ID"]), []).append(w)
        return out

    @staticmethod
    def expected_positions(row):
        n = to_i(row["個数"])
        if n == 0 or not row["先頭比"] or not row["間隔比"]:
            return []
        return [to_f(row["先頭比"]) + (i * to_f(row["間隔比"])) for i in range(n)]

    def parse_window_line(self, wall):
        line = next((l for l in self.section("WINDOWS（") if l.startswith(f"- 壁 {wall}（") or l.startswith(f"- 壁 {wall}:")), None)
        if line is None:
            return None
        m = re.search(r": (\d+)枚の", line, A)
        n = int(m.group(1)) if m else None
        pos = [float(x) for x in re.findall(r"#\d+ at ([0-9.]+)", line, A)]
        return [n, pos, line]

    def check_window_rows(self, map_id):
        for (wall, rid), wins in self.window_rows(map_id).items():
            row = next((r for r in self.t["建物窓列"] if r["窓列ID"] == rid), None)
            if row is None:
                self.err(map_id, f"窓 {wins[0]['窓ID']} が参照する建物窓列 {rid} が台帳に無い")
                continue
            parsed = self.parse_window_line(wall)
            if parsed is None:
                self.err(map_id, f"建物窓列 {rid}（壁 {wall}）の窓が WINDOWS 節に現れない")
                continue
            n, pos, _ = parsed
            if n != to_i(row["個数"]):
                self.err(map_id, f"建物窓列 {rid}（壁 {wall}）: 個数 {row['個数']} のはずが WINDOWS 節では {inspect_n(n)} 枚")
            if len(wins) != to_i(row["個数"]):
                self.err(map_id, f"建物窓列 {rid}: 台帳の窓（窓表）が {len(wins)} 個で個数 {row['個数']} と違う")
            exp = self.expected_positions(row)
            if not exp:
                continue
            if len(pos) != len(exp) or any(abs(a - b) > 0.015 for a, b in zip(pos, exp)):
                self.err(map_id, f"建物窓列 {rid}（壁 {wall}）: WINDOWS 節の位置 {pos} が台帳（先頭比・間隔比）の {[round(x, 2) for x in exp]} と一致しない")

    # ---- (vii)
    def area_fixed_texts(self, area):
        return [[r["項目"], r["値"]] for r in self.t["エリア固定"]
                if r["エリアID"] == area and r["型"] == "文" and AREA_FIXED_ITEMS.match(r["項目"]) and strip(r["値"])]

    def pool_area_of(self, map_id):
        row = next((m for m in self.t["MAP"] if m["MAP_ID"] == self.base_of(map_id)), None)
        pid = row["装飾プールID"] if row else None
        if not pid or pid in ("未決(要確認)", "該当なし", "なし"):
            return None
        r = next((r for r in self.t["装飾プール"] if r["プールID"] == pid and r["項目"] == "area"), None)
        return r["値"] if r else None

    def check_area_fixed(self, map_id):
        area = self.pool_area_of(map_id)
        if area is None:
            return
        own = self.area_fixed_texts(area)
        if not own:
            self.err(map_id, f"エリア固定: エリア {area} の エリア固定（机・台座・木）が台帳に無い")
        for item, text in own:
            if text not in self.prompt:
                self.err(map_id, f"エリア固定 {area}.{item} がプロンプトに現れない（机・台座・木の固定が落ちた）")
        own_texts = [t for _, t in own]
        for other in dict.fromkeys(r["エリアID"] for r in self.t["エリア固定"]):
            if other == area:
                continue
            for item, text in self.area_fixed_texts(other):
                if text in own_texts:
                    continue
                if text in self.prompt:
                    self.err(map_id, f"エリア固定 {other}.{item} が別エリア {area} のMAPのプロンプトに漏れている")

    def outdoor_pool(self, map_id):
        m = next((m for m in self.t["MAP"] if m["MAP_ID"] == self.base_of(map_id)), None)
        pid = m["装飾プールID"] if m else None
        return any(r["プールID"] == pid and r["項目"] == "outdoor" and r["値"] == "true" for r in self.t["装飾プール"])

    def check_reality(self, map_id):
        outdoor = self.outdoor_pool(map_id)
        has = "STRUCTURE（屋外" in self.prompt
        if outdoor and not has:
            self.err(map_id, "屋外MAPのプロンプトに STRUCTURE 節（境界の実体・歩けない理由）が無い")
        if not outdoor and has:
            self.err(map_id, "屋内MAPのプロンプトに屋外用 STRUCTURE 節が混入している")
        if not outdoor:
            return
        for tid in "PR.reality.road-edge PR.reality.shosetsu PR.reality.wire PR.forbid.road-edge PR.forbid.shosetsu PR.forbid.wire PR.forbid.miniature".split():
            tpl = next((r for r in self.t["プロンプト文面"] if r["文面ID"] == tid), None)
            if tpl is None:
                self.err(map_id, f"台帳 プロンプト文面.{tid} が無い")
            elif tpl["文面"] not in self.prompt:
                self.err(map_id, f"屋外MAPのプロンプトに {tid} の文（道路の縁は実体の境界／消雪パイプは穴だけ／工作の素材のミニチュア）が入っていない")

    def check_core_constraints(self, map_id):
        for w in CORE_WORDS:
            if w not in self.prompt:
                self.err(map_id, f"中核制約『{w}』がプロンプトに無い（REALITY など後から足した節が押し流していないか）")
        sl = next((l for l in self.lines if l.startswith("- 台座の前縁の飾り")), None)
        if sl is None:
            self.err(map_id, "台座の前縁の飾り（MAP ごとの配置）の行が無い")
        else:
            self.slab_lines[map_id] = sl
        dl = next((l for l in self.lines if l.startswith("- 作業机の上の置き物")), None)
        if dl is None:
            if any(l.startswith("- 作業机") for l in self.lines):
                self.err(map_id, "作業机の上の置き物（MAP ごと）の行が無い")
        else:
            self.desk_lines[map_id] = dl
        for l in self.lines:
            if PHOTOREAL_AFFIRM.search(l) and "描かない" not in l and "しない" not in l:
                self.err(map_id, f"実写・フォトリアルを肯定する文言: {l[:60]}")
            if CORE_NEGATE.search(l) and "描かない" not in l and "実写のような" not in l and not l.startswith("- "):
                self.err(map_id, f"中核制約（ミニチュア・綿・工作・段ボール）を打ち消す文言: {l[:60]}")

    def check_craft(self, map_id):
        mini = next((r for r in self.t["プロンプト文面"] if r["文面ID"] == "PR.miniature"), None)
        if mini is None or mini["文面"] not in self.prompt:
            self.err(map_id, "プロンプトに MINIATURE MATERIALS（台帳 プロンプト文面.PR.miniature）が無い")
        else:
            ri = next((k for k, l in enumerate(self.lines) if l.startswith("ROLE:")), None)
            if not (ri is not None and (self.lines[ri + 1] if ri + 1 < len(self.lines) else "").startswith("MINIATURE MATERIALS:")):
                self.err(map_id, "MINIATURE MATERIALS が ROLE の直後にない（中核制約を最優先で冒頭に置く）")
        for w in REAL_WORDS:
            if w in self.final:
                self.err(map_id, f"送信文に実物の材質語『{w}』が残っている（描画定数 craft.words に工作語への置換を足す）")
        if not self.outdoor_pool(map_id):
            return
        for w in CRAFT_MATERIAL_WORDS:
            if w not in self.final:
                self.err(map_id, f"屋外MAPの送信文に材料語『{w}』が無い（鉄道模型のジオラマの材料表が落ちた）")

    def check_slab_props_varied(self):
        lines = self.slab_lines
        if len(lines) < 2:
            return
        groups = {}
        for k, v in lines.items():
            if "この MAP は無し" not in v:
                groups.setdefault(v, []).append(k)
        for g in groups.values():
            if len(g) > 1:
                self.err("・".join(g), "台座の前縁の飾りが別の MAP と同じ配置（MAP ごとにランダムにする）")
        if len(set(lines.values())) == 1:
            self.err("台座の前縁の飾り", "全 MAP が同じ配置になっている")
        plain = sum(1 for v in lines.values() if "この MAP は無し" in v)
        if not plain * 2 > len(lines):
            self.err("台座の前縁の飾り", f"素の段ボール断面だけの MAP が過半でない（{plain}/{len(lines)}。既定は素。テープ・糊は継ぎ目がある所だけ）")
        for m, v in lines.items():
            if "この MAP は無し" not in v and "継ぎ目" not in v:
                self.err(m, "前縁の飾りが継ぎ目に従属していない（継ぎ目の記述が無い）")

    def check_desk_props_varied(self):
        lines = self.desk_lines
        if len(lines) < 2:
            return
        groups = {}
        for k, v in lines.items():
            if "この MAP は無し" not in v:
                groups.setdefault(v, []).append(k)
        for g in groups.values():
            if len(g) > 1:
                self.err("・".join(g), "作業机の上の置き物が別の MAP と同じ")
        zero = sum(1 for v in lines.values() if "この MAP は無し" in v)
        if not zero * 2 > len(lines):
            self.err("作業机の上の置き物", f"置き物が0個の MAP が過半でない（{zero}/{len(lines)}。置く理由の無い MAP に詰め込まない）")

    def check_swatch_sheet_in_refs(self):
        sh = os.path.join(self.root, "docs/production/oblique-mocks/material-swatch/material-swatch-sheet.webp")
        run = os.path.join(self.root, ".claude/skills/sit-field-background/tools/oblique_e2_run.sh")
        if not os.path.exists(sh):
            self.err("素材見本シート", f"{sh} が無い")
        ok = False
        if os.path.exists(run):
            with open(run, encoding="utf-8") as f:
                ok = "material-swatch-sheet" in f.read()
        if not ok:
            self.err("素材見本シート", "oblique_e2_run.sh の REFS に素材見本シート（material-swatch-sheet）が入っていない")

    # ---- (v)
    def check_anchors(self):
        by_id = {r["map_id"]: r for r in self.records}
        all_ids = [d["決定ID"] for d in self.t["決定"]]
        for a in ANCHORS:
            for mid in a["maps"]:
                rec = by_id.get(mid)
                if rec is None:
                    continue
                if rec.get("gated"):
                    self.err(mid, f"回帰アンカー {a['id']}（{a['what']}）: このMAPがゲートで止まっていて検査できない")
                    continue
                self.prompt = rec["prompt"]
                self.lines = chomp_lines(self.prompt)
                dl = self.decision_lines()
                for did in a["decisions"]:
                    if did not in all_ids:
                        self.err(mid, f"回帰アンカー {a['id']}（{a['what']}）: 決定 {did} が台帳に無い")
                    d = next((x for x in self.t["決定"] if x["決定ID"] == did), None)
                    if d and not (d["状態"] == "有効" and d["プロンプト出力"] == "必須" and self.targets(mid, d["対象MAP"])):
                        self.err(mid, f"回帰アンカー {a['id']}: 決定 {did} が有効・プロンプト出力=必須・対象MAP になっていない")
                    if not any(l.startswith(f"- [{did}] ") for l in dl):
                        self.err(mid, f"回帰アンカー {a['id']}（{a['what']}）: [{did}] がプロンプトの DECISIONS 節に現れない")
                for w in a.get("words", []):
                    if w not in self.prompt:
                        self.err(mid, f"回帰アンカー {a['id']}（{a['what']}）: 語『{w}』がプロンプトに現れない")
                if a.get("leak"):
                    rx = re.compile(a["leak"])
                    hit = first_compact(self.leaking_clause(l, lambda c: bool(rx.search(c)), negation=False) for l in self.leak_lines(with_inherited=True))
                    if hit is not None:
                        self.err(mid, f"回帰アンカー {a['id']}（{a['what']}）: 漏れてはいけない語 {a['leak']} が現れる: 「{strip(hit)[:80]}」")
                if a.get("door_wall"):
                    self.check_door_wall(mid, a)
                if a.get("corridor"):
                    self.check_corridor(mid, a)

    def check_door_wall(self, mid, a):
        # 文（。区切り）単位で見る: 同じ行の別の文（石の北東の隅など）の壁方角は勝手口の位置ではない
        lines = [s for l in self.lines for s in rsplit(l, "。") if "勝手口" in s or "door-back" in s]
        bad = next((l for l in lines if any(w != a["door_wall"] for w in re.findall(r"[東西南北]壁", l))), None)
        if bad is not None:
            self.err(mid, f"回帰アンカー {a['id']}（{a['what']}）: 勝手口の行に {a['door_wall']} 以外の壁方角がある: 「{strip(bad)[:100]}」")
        if not any(a["door_wall"] in l for l in lines):
            self.err(mid, f"回帰アンカー {a['id']}（{a['what']}）: 勝手口を {a['door_wall']} と書いた行が無い")

    def check_corridor(self, mid, a):
        for rid, n in a["corridor"].items():
            row = next((r for r in self.t["建物窓列"] if r["窓列ID"] == rid), None)
            if row is None:
                self.err(mid, f"回帰アンカー {a['id']}（{a['what']}）: 建物窓列 {rid} が台帳に無い")
                continue
            if to_i(row["個数"]) != n:
                self.err(mid, f"回帰アンカー {a['id']}: 建物窓列 {rid} の個数が {row['個数']}（期待 {n}）")
            linked = [(k, v) for k, v in self.window_rows(mid).items() if k[1] == rid]
            if not linked:
                self.err(mid, f"回帰アンカー {a['id']}（{a['what']}）: このMAPに建物窓列 {rid} へ紐づく窓が無い（屋内と外観で窓列が一致しない）")
                continue
            for (wall, _), wins in linked:
                parsed = self.parse_window_line(wall)
                if parsed is None:
                    self.err(mid, f"回帰アンカー {a['id']}: 壁 {wall} の窓が WINDOWS 節に現れない")
                    continue
                if parsed[0] != n or len(wins) != n:
                    self.err(mid, f"回帰アンカー {a['id']}: 壁 {wall} の窓が {inspect_n(parsed[0])} 枚（期待 {n}）")

    def check_cross_map(self):
        by_row = {}
        for rec in self.records:
            if rec.get("gated") or not rec.get("prompt"):
                continue
            self.prompt = rec["prompt"]
            self.lines = chomp_lines(self.prompt)
            for (wall, rid), _ in self.window_rows(rec["map_id"]).items():
                row = next((r for r in self.t["建物窓列"] if r["窓列ID"] == rid), None)
                if row is None or not self.expected_positions(row):
                    continue
                p = self.parse_window_line(wall)
                if p:
                    by_row.setdefault(rid, []).append([rec["map_id"], p[1]])
        for rid, lst in by_row.items():
            base = lst[0][1]
            for mid, pos in lst:
                if len(pos) == len(base) and all(abs(x - y) <= 0.015 for x, y in zip(pos, base)):
                    continue
                self.err(mid, f"建物窓列 {rid}: 位置 {pos} が {lst[0][0]} の {base} と一致しない（屋内と外観で窓列が違う）")


def load_records(argv, root):
    if "--from-json" in argv:
        with open(argv[argv.index("--from-json") + 1], encoding="utf-8") as f:
            return json.load(f)
    probe = os.path.join(root, PROBE)
    cmd = os.environ.get("LEDGER_PROBE_CMD") or \
        f"uv run --project {shlex.quote(root)} --with numpy --with opencv-python-headless --with pillow python3 {shlex.quote(probe)}"
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True, env={**os.environ, "LEDGER_ROOT": root})
    out = p.stdout + p.stderr  # Open3.capture2e 相当（標準出力と標準エラーを混ぜる）
    if p.returncode != 0:
        die("プロンプトの導出に失敗: " + "".join(l + "\n" for l in out.splitlines()[-5:]))
    return json.loads(p.stdout[p.stdout.index("["):])


def main():
    argv = sys.argv[1:]
    root = LY.ROOT
    only = argv[argv.index("--maps") + 1].split(",") if "--maps" in argv else None
    v = PromptReflection(load_records(argv, root), root=root, only=only).run()
    v.check_cross_map()
    for id_, miss in v.skipped:
        print(f"ゲートで停止（対象外）: {id_}（ゲート理由: 必須キー欠落 {len(miss)} 件: {str(miss[0] if miss else '')[:60]} …）")
    for id_, why in v.stopped:
        print(f"生成停止（反映検査は実施）: {id_}（理由: 屋外MAPの建物・塀・門の look 未記入 {len(why)} 件: {str(why[0] if why else '')[:60]} …）")
    print(f"検査したMAP（{len(v.checked)}）: {', '.join(v.checked)}")
    if not v.errors:
        print(f"PASS: プロンプトは台帳を漏れなく反映（検査MAP {len(v.checked)}・ゲート停止 {len(v.skipped)}・生成停止(look未記入) {len(v.stopped)}・回帰アンカー {len(ANCHORS)}）")
        return 0
    print(f"FAIL: {len(v.errors)} 件の漏れ", file=sys.stderr)
    for e in v.errors:
        print(f"  - {e}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
