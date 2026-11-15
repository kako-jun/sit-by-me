#!/usr/bin/env python3
"""docs/ledger/*.yaml（日本語マスター）の整合性検証。外部キー・一意性・必須キー・語彙・別名・決定の整合・生成物の鮮度・自由記述の矛盾警告。

  uv run python3 scripts/verify_ledger.py            # エラーがあれば exit 1（警告は表示だけ）
"""
import glob
import json
import os
import re
import subprocess
import sys
from collections import defaultdict

import ledger_required_keys as LRK
import ledger_yaml as LY

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.abspath(os.path.join(HERE, ".."))
WS = " \t\n\v\f\r\0"
A = re.ASCII


# ---- Ruby の String 組み込みと同じ挙動にそろえる小道具（出力を旧実装と一致させるため）
def rstrip_ws(s):
    return s.strip(WS)


def blank(s):
    return not s.strip(WS)


def split_rb(s, sep):
    """String#split(sep): 末尾の空要素を落とす"""
    parts = s.split(sep)
    while parts and parts[-1] == "":
        parts.pop()
    return parts


def to_i(s):
    m = re.match(r"\s*([+-]?\d+(?:_\d+)*)", s, A)
    return int(m.group(1).replace("_", "")) if m else 0


def inspect_list(items):
    return "[" + ", ".join('"' + x.replace("\\", "\\\\").replace('"', '\\"') + '"' for x in items) + "]"


def rlines(s):
    """String#lines（\\n だけで区切り、改行を残す）"""
    return re.findall(r"[^\n]*\n|[^\n]+", s)


def first_val(r):
    return next(iter(r.values()), "")


def uniq(xs):
    return list(dict.fromkeys(xs))


def split_semi(s):
    return [x.strip(WS) for x in split_rb(s, ";") if x.strip(WS)]


def group_by(rows, keyf):
    g = {}
    for r in rows:
        g.setdefault(keyf(r), []).append(r)
    return g


CODE_REF = re.compile(r"""["']((?:PR|MK|TP)\.[A-Za-z0-9._-]*|(?:view|width|door|window|slab|occlusion|topology|battle|town|tree|craft|desk)\.[A-Za-z0-9._-]*)["']""")
FREE_TEXT_COVERED = ["エリア", "MAP", "建物", "建物部位", "建物窓列", "建物関係", "建物時期差分", "端", "接続", "要素", "窓", "素材", "採用要素", "決定"]
DOMAIN_FREE_TEXT_COVERED = ["MAP仕様", "MAP契約", "特殊遷移", "体内幾何", "敵", "召喚獣", "敵配置", "ボスギミック", "人物"]
UNIQUE = {
    "エリア": ["エリアID"], "MAP": ["MAP_ID"], "建物": ["建物ID"], "建物部位": ["部位ID"], "建物窓列": ["窓列ID"],
    "端": ["端ID", "適用時期"], "窓": ["窓ID", "適用時期"], "要素": ["MAP_ID", "適用時期", "要素ID"], "決定": ["決定ID"], "採用要素": ["採用要素ID"],
    "素材": ["素材ID"], "生成物": ["生成物ID"], "語彙": ["語彙ID"], "未決": ["未決ID"], "既定値": ["既定ID"], "ファイル配置": ["配置ID"], "Issue点検": ["コメントURL"],
    "エリア景観": ["エリアID"], "描画定数": ["定数ID"], "プロンプト文面": ["文面ID"], "戦闘背景": ["背景ID"],
}
ISSUE_URL_RE = re.compile(r"https://github\.com/[^/]+/[^/]+/issues/(\d+)(?:#issuecomment-\d+)?")
AREA_FIXED_REQUIRED = ["name", "desk.look", "desk.grain", "slab.look"]
AREA_LANDSCAPE_EXEMPT = ["body"]
MAP_ID_RE = r"(?:TRM|KRB|STN|NTR|NTB|UTS|SNL|SCH|NTA|UCH|BDY|APT|OVS|GRD|CST)-\d{2}"
DEC_TABS = {"エリア": ["エリア", "エリアID"], "MAP": ["MAP", "MAP_ID"], "建物": ["建物", "建物ID"],
            "端": ["端", "端ID"], "要素": ["要素", "要素ID"], "窓": ["窓", "窓ID"], "接続": ["接続", "端A"],
            "敵": ["敵", "敵ID"], "召喚獣": ["召喚獣", "召喚獣ID"], "人物": ["人物", "人物ID"],
            "敵配置": ["敵配置", "配置ID"], "ボスギミック": ["ボスギミック", "ギミックID"],
            "BGMスロット": ["BGMスロット", "スロットID"], "素材": ["素材", "素材ID"],
            "刀候補": ["刀候補", "刀候補ID"], "能力候補": ["能力候補", "能力ID"], "魔法": ["魔法", "魔法ID"]}


def run_capture(cmd, env_extra=None, cwd=None):
    env = {**os.environ, **(env_extra or {})}
    r = subprocess.run(cmd, env=env, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return r.stdout.decode("utf-8", "replace"), r.returncode == 0


class LedgerVerifier:
    def __init__(self, root=None):
        self.root = root or LY.ROOT
        self.errors = []
        self.warnings = []
        self.t = LRK.Tables(LY.load_all())
        self._map_ids = None
        self._layout_regexps = None

    def err(self, msg):
        self.errors.append(msg)

    def warn(self, msg):
        self.warnings.append(msg)

    def ids(self, table, col):
        return [r[col] for r in self.t[table]]

    @property
    def map_ids(self):
        if self._map_ids is None:
            self._map_ids = self.ids("MAP", "MAP_ID")
        return self._map_ids

    @staticmethod
    def base_map(id_):
        return re.sub(r"-(kids|fire|burnt|wc)\Z", "", id_)

    def schema(self):
        s = LY.schema()
        if not s:
            raise RuntimeError("表定義(ledger_io.py)が無い")
        return s

    def run(self):
        for fn in (self.check_presence, self.check_columns, self.check_required_definition_columns, self.check_free_text_tables, self.check_unique,
                   self.check_fks, self.check_required, self.check_aliases, self.check_decisions, self.check_area_fixed, self.check_area_landscape,
                   self.check_buildings, self.check_windows, self.check_confirmed_edges, self.check_layout, self.check_generated,
                   self.check_index_fresh, self.check_views_fresh, self.check_free_text, self.check_code_texts, self.check_domains):
            fn()
        return self

    # 描画定数・プロンプト文面: 空値なし、変数列と本文の {名前} が一致、コードが参照するIDが全て在り、どの行もコードから参照されている
    def check_code_texts(self):
        texts = self.t["プロンプト文面"]
        consts = self.t["描画定数"]
        for r in texts:
            id_ = r["文面ID"]
            if blank(r["文面"]):
                self.err(f"プロンプト文面 {id_}: 文面が空")
            vars_ = sorted(set(re.findall(r"\{([A-Za-z0-9_]+)\}", r["文面"])))
            if sorted(split_rb(r["変数"], ",")) != vars_:
                self.err(f"プロンプト文面 {id_}: 変数列 '{r['変数']}' が本文の変数 {','.join(vars_)} と違う")
            if blank(r["使用箇所"]):
                self.err(f"プロンプト文面 {id_}: 使用箇所が空")
        for r in consts:
            if blank(r["値"]):
                self.err(f"描画定数 {r['定数ID']}: 値が空")
            if blank(r["コード内の名前"]):
                self.err(f"描画定数 {r['定数ID']}: コード内の名前が空")
        tools = os.path.join(self.root, ".claude/skills/sit-field-background/tools")
        sources = (sorted(glob.glob(os.path.join(tools, "oblique_*.py"))) + [os.path.join(tools, "sample_field_build.py")]
                   + sorted(glob.glob(os.path.join(self.root, ".claude/skills/sit-battle-background/tools/*.py"))))
        refs = []
        for f in sources:
            with open(f, encoding="utf-8") as fh:
                refs += CODE_REF.findall(fh.read())
        refs = uniq(refs)
        all_ids = [r["文面ID"] for r in texts] + [r["定数ID"] for r in consts]
        for ref in refs:
            ok = any(i.startswith(ref) for i in all_ids) if ref.endswith(".") else ref in all_ids
            if not ok:
                self.err(f"コードが参照する台帳ID '{ref}' が 描画定数/プロンプト文面 に無い")
        for i in all_ids:
            used = any(i.startswith(ref) if ref.endswith(".") else ref == i for ref in refs)
            if not used:
                self.err(f"台帳ID {i} がどのコード（oblique_*.py・sample_field_build.py・戦闘背景ツール）からも参照されていない（死んだ行。消すか、コードを台帳参照にする）")

    def check_presence(self):
        for n in self.schema():
            if not os.path.isfile(os.path.join(self.root, "docs/ledger", f"{n}.yaml")):
                self.err(f"表 {n}.yaml が無い")

    def check_columns(self):
        schema = self.schema()
        for tb in LY.tables():
            cols = schema.get(tb)
            if cols is None:
                self.err(f"表 {tb}.yaml は表定義（ledger_io.py の SCHEMA）に無い")
                continue
            for i, row in enumerate(self.t[tb]):
                extra = [k for k in row if k not in cols]
                if extra:
                    self.err(f"表 {tb}.yaml の{i + 1}行目（{row[cols[0]]}）に表定義に無い列 {inspect_list(extra)}（綴り間違い？ 正しい列: {' / '.join(cols)}）")

    def check_free_text_tables(self):
        schema = self.schema()
        with_free = [t for t, cols in schema.items() if "特徴(自由記述)" in cols]
        for tb in with_free:
            if tb not in FREE_TEXT_COVERED and tb not in DOMAIN_FREE_TEXT_COVERED:
                self.err(f"表 {tb} に特徴(自由記述)の欄があるが、プロンプトへの導出（ledger_query.free_texts）と反映検査（verify_prompt_reflects_ledger.py）の対象になっていない（FREE_TEXT_COVERED に足す前に両方を実装する）")
        for tb in FREE_TEXT_COVERED:
            if tb not in with_free:
                self.err(f"FREE_TEXT_COVERED の表 {tb} に特徴(自由記述)の欄が無い（定義が変わった。導出・検査を見直す）")
        for tb in DOMAIN_FREE_TEXT_COVERED:
            if tb not in with_free:
                self.err(f"DOMAIN_FREE_TEXT_COVERED の表 {tb} に特徴(自由記述)の欄が無い")

    def check_required_definition_columns(self):
        schema = self.schema()
        for rk in self.t["必須キー"]:
            cols = schema.get(rk["対象テーブル"])
            if cols is None:
                continue
            if not (rk["キー"].startswith("@") or rk["キー"] in cols):
                self.err(f"必須キー {rk['対象テーブル']}.{rk['キー']}: キーが表定義に無い")
            for c in split_rb(rk["条件"], "&"):
                m = re.fullmatch(r"(.+?)(!=|=)(.*)", c.strip(WS), re.S)
                if not m:
                    continue
                if m.group(1) not in cols:
                    self.err(f"必須キー {rk['対象テーブル']}.{rk['キー']}: 条件『{c.strip(WS)}』の列『{m.group(1)}』が表定義に無い")

    def check_unique(self):
        for tb, cols in UNIQUE.items():
            dup = [k for k, v in group_by(self.t[tb], lambda r: tuple(r[c] for c in cols)).items() if len(v) > 1]
            if dup:
                self.err(f"{tb}: 主キー重複 {', '.join('/'.join(k) for k in dup)}")
        pairs = [tuple(sorted([r["端A"], r["端B"]])) for r in self.t["接続"]]
        counts = defaultdict(int)
        for p in pairs:
            counts[p] += 1
        dup = [k for k, n in counts.items() if n > 1]
        if dup:
            self.err(f"接続: 同じ端の組が重複 {', '.join('⇄'.join(k) for k in dup)}")
        ends = [e for r in self.t["接続"] for e in (r["端A"], r["端B"])]
        ecount = defaultdict(int)
        for e in ends:
            ecount[e] += 1
        for e, n in ecount.items():
            if n > 1 and re.search(r"\.door", e):
                self.err(f"接続: 扉の端 {e} が複数の接続に使われている")

    def fk(self, table, col, target_table, target_col, allow=(), list_=False, optional=True):
        s = self.ids(target_table, target_col)
        for r in self.t[table]:
            v = r[col]
            if v == "" and optional:
                continue
            for tok in (split_rb(v, ";") if list_ else [v]):
                if tok in allow or tok in s:
                    continue
                self.err(f"外部キー {table}.{col}='{tok}' が {target_table}.{target_col} に無い（{first_val(r)}）")

    def check_fks(self):
        fk = self.fk
        t = self.t
        fk("MAP", "エリアID", "エリア", "エリアID", optional=False)
        fk("MAP", "建物ID", "建物", "建物ID", list_=True, allow=["該当なし"])
        for m in t["MAP"]:
            for d in split_rb(m["依存MAP"], ";"):
                if d in ("なし", "該当なし", "未決(要確認)"):
                    continue
                if d not in self.ids("MAP", "MAP_ID"):
                    self.err(f"外部キー MAP.依存MAP='{d}' が MAP に無い（{m['MAP_ID']}）")
                if d == m["MAP_ID"]:
                    self.err(f"依存MAPの自己参照 {m['MAP_ID']}")
        self.check_dep_cycle()
        fk("建物", "エリアID", "エリア", "エリアID")
        fk("建物部位", "建物ID", "建物", "建物ID", optional=False)
        fk("建物窓列", "建物ID", "建物", "建物ID", optional=False)
        fk("建物窓列", "部位ID", "建物部位", "部位ID")
        fk("建物関係", "建物A", "建物", "建物ID")
        fk("建物関係", "建物B", "建物", "建物ID")
        fk("建物関係", "接続端ID", "端", "端ID")
        fk("建物時期差分", "建物ID", "建物", "建物ID", optional=False)
        fk("建物時期差分", "部位ID", "建物部位", "部位ID")
        fk("端", "MAP_ID", "MAP", "MAP_ID", optional=False)
        fk("端", "建物部位ID", "建物部位", "部位ID")
        fk("窓", "MAP_ID", "MAP", "MAP_ID", optional=False)
        fk("窓", "建物窓列ID", "建物窓列", "窓列ID")
        fk("要素", "MAP_ID", "MAP", "MAP_ID", optional=False)
        fk("要素", "建物部位ID", "建物部位", "部位ID")
        fk("既定値", "MAP_ID", "MAP", "MAP_ID", optional=False)
        fk("時期差分", "MAP_ID", "MAP", "MAP_ID", optional=False)
        for r in t["接続"]:
            for c in ("端A", "端B"):
                segs = split_rb(r[c], ".")
                if not (segs and segs[0] in self.map_ids):
                    self.err(f"接続.{c}='{r[c]}' の MAP が MAP ID 登録に無い")
        mapped = uniq(e["MAP_ID"] for e in t["端"])
        virtual = []
        for r in t["接続図設定"]:
            m = re.match(r'virtual_ports\["([^"]+)"\]', r["項目"])
            if m:
                virtual.append(m.group(1))
        virtual = uniq(virtual)
        edge_ids = self.ids("端", "端ID") + virtual
        for r in t["接続"]:
            for c in ("端A", "端B"):
                segs = split_rb(r[c], ".")
                mid = segs[0] if segs else None
                if mid in mapped and r[c] not in edge_ids:
                    self.err(f"接続.{c}='{r[c]}': MAP {mid} は端表に行があるのに、この端が端表にも接続図設定の仮想端点(virtual_ports)にも無い（存在しない端を指す接続）")
        for e in t["端"]:
            if e["相手端"] == "":
                continue
            ok = any(sorted([c["端A"], c["端B"]]) == sorted([e["端ID"], e["相手端"]]) for c in t["接続"])
            if not ok:
                self.err(f"端 {e['端ID']} の相手端 {e['相手端']} が接続表に無い（接続は接続表が正）")
        self.check_decision_fks()
        self.check_issue_audit()
        for a in t["採用要素"]:
            if not (a["素材ID"] == "" or a["素材ID"] in self.ids("素材", "素材ID")):
                self.err(f"外部キー 採用要素.素材ID='{a['素材ID']}' が素材に無い")
            if self.base_map(a["元MAP"]) not in self.ids("MAP", "MAP_ID"):
                self.err(f"採用要素 {a['採用要素ID']} の元MAP {a['元MAP']} が MAP に無い")
            for m in split_rb(a["継承先MAP"], ";"):
                if self.base_map(m) not in self.ids("MAP", "MAP_ID"):
                    self.err(f"採用要素 {a['採用要素ID']} の継承先MAP {m} が MAP に無い")
        for s in t["素材"]:
            owner = s["所有者ID"]
            if owner == "" or owner == "未決(要確認)":
                continue
            ok = (self.base_map(owner) in self.ids("MAP", "MAP_ID") or owner in self.ids("人物", "人物ID") or owner in self.ids("敵", "敵ID")
                  or owner in self.ids("召喚獣", "召喚獣ID") or owner in self.ids("サンプルMAP", "サンプルID")
                  or re.fullmatch(r"BG\d{3}", owner, A) is not None or owner in ("BRAND", "UI"))
            if not ok:
                self.err(f"素材 {s['素材ID']} の所有者 {owner} に対応する台帳行または素材名前空間が無い")
        dec = {d["決定ID"]: d for d in t["決定"]}
        for tb, rows in t.items():
            if not (rows and "決定参照" in rows[0]):
                continue
            for r in rows:
                for ref in split_rb(r["決定参照"], ";"):
                    if ref not in dec:
                        self.err(f"決定参照 {tb}({first_val(r)})='{ref}' が決定表に無い")
                    elif dec[ref]["状態"] != "有効":
                        self.err(f"決定参照 {tb}({first_val(r)})='{ref}' は {dec[ref]['状態']}（置換先 {dec[ref]['置換先']}）の決定を参照している")
        for u in t["未決"]:
            if not (u["解決決定ID"] == "" or u["解決決定ID"] in dec):
                self.err(f"未決 {u['未決ID']} の解決決定ID {u['解決決定ID']} が決定表に無い")

    def check_dep_cycle(self):
        skip = ("なし", "該当なし", "未決(要確認)")
        deps = {m["MAP_ID"]: [d for d in split_rb(m["依存MAP"], ";") if d not in skip] for m in self.t["MAP"]}
        state = {}

        def visit(n, path):
            if state.get(n) == "done":
                return
            if state.get(n) == "open":
                self.err(f"依存MAPの循環 {'→'.join(path + [n])}")
                return
            state[n] = "open"
            for d in deps.get(n) or []:
                visit(d, path + [n])
            state[n] = "done"

        for n in list(deps):
            visit(n, [])

    def check_decision_fks(self):
        for d in self.t["決定"]:
            tt = DEC_TABS.get(d["対象種別"])
            if d["対象種別"] == "全体":
                if d["対象ID"] != "sit-by-me":
                    self.err(f"決定 {d['決定ID']}: 全体の対象IDは sit-by-me")
            elif tt is None:
                self.err(f"決定 {d['決定ID']}: 対象種別 '{d['対象種別']}' が不正")
            else:
                s = self.ids(*tt)
                if d["対象種別"] == "接続":
                    s = s + self.ids("接続", "端B")
                if d["対象ID"] not in s:
                    self.err(f"決定 {d['決定ID']}: 対象ID '{d['対象ID']}' が {d['対象種別']} 表に無い")
            for m in split_rb(d["対象MAP"], ";"):
                if self.base_map(m) not in self.ids("MAP", "MAP_ID"):
                    self.err(f"決定 {d['決定ID']}: 対象MAP '{m}' が MAP に無い")
            if d["状態"] == "訂正済み":
                if d["置換先"] == "":
                    self.err(f"決定 {d['決定ID']}: 訂正済みなのに置換先が無い")
                if not (d["置換先"] == "" or d["置換先"] in self.ids("決定", "決定ID")):
                    self.err(f"決定 {d['決定ID']}: 置換先 {d['置換先']} が決定表に無い")

    def check_issue_audit(self):
        classes = [v["値"] for v in self.t["語彙"] if v["グループ"] == "Issue点検分類"]
        self.fk("Issue点検", "決定ID", "決定", "決定ID", list_=True)
        for r in self.t["Issue点検"]:
            id_ = r["コメントURL"]
            if r["分類"] not in classes:
                self.err(f"Issue点検 {id_}: 分類 '{r['分類']}' が語彙（Issue点検分類）に無い")
            if r["分類"] == "決定表に反映済み" and r["決定ID"] == "":
                self.err(f"Issue点検 {id_}: 分類が『決定表に反映済み』なのに決定IDが空")
            if not re.search(r"/(issues|pull)/" + re.escape(r["Issue番号"]) + r"(#|\Z)", id_):
                self.err(f"Issue点検 {id_}: Issue番号 '{r['Issue番号']}' が URL の Issue と違う")
            if r["候補の要約"] == "":
                self.err(f"Issue点検 {id_}: 候補の要約が空")
        pending = sum(1 for r in self.t["Issue点検"] if r["分類"] == "未反映(要取込み)")
        if pending > 0:
            self.warn(f"Issue点検: 未反映(要取込み)が {pending} 件（決定表へ取り込むか分類を確定する）")

    def check_required(self):
        errors, _undecided = LRK.check_rows(self.t)
        for e in errors:
            self.err(e)

    def check_aliases(self):
        aliases = {r["別名"]: r["正規名"] for r in self.t["キー別名"]}
        for r in self.t["必須キー"]:
            if r["キー"] in aliases:
                self.err(f"必須キー表のキー '{r['キー']}' は別名（正規名: {aliases[r['キー']]}）")
        for tb in LY.tables():
            for h in LY.header(tb):
                if h in aliases:
                    self.warn(f"別名の列名 {tb}.{h}（正規名 {aliases[h]} に直す）")
        for r in self.t["エリア固定"] + self.t["装飾プール"]:
            parts = split_rb(re.sub(r"[.\[]", "\x01", r["項目"]), "\x01")
            k = parts[-1] if parts else None
            if k in aliases:
                self.warn(f"項目 '{r['項目']}' の末尾が別名 {k}（正規名 {aliases[k]}）")

    def check_decisions(self):
        for d in self.t["決定"]:
            id_ = d["決定ID"]
            for w in split_rb(d["必須語"], ";"):
                if w not in d["決定の要点"]:
                    self.err(f"決定 {id_}: 必須語『{w}』が決定の要点に無い")
            for w in split_rb(d["禁止語"], ";"):
                if w not in d["決定の要点"]:
                    self.err(f"決定 {id_}: 禁止語『{w}』が決定の要点に無い")
            if not re.fullmatch(r"\d{4}-\d\d-\d\d", d["日付"], A):
                self.err(f"決定 {id_}: 日付が YYYY-MM-DD でない")
            self.check_source_urls(d)

    def check_source_urls(self, d):
        id_ = d["決定ID"]
        if not d["出典"].startswith("Issue"):
            return
        urls = split_semi(d["出典URL"])
        if not urls:
            self.err(f"決定 {id_}: 出典が Issue なのに出典URL が空")
            return
        for u in urls:
            if not ISSUE_URL_RE.fullmatch(u):
                self.err(f"決定 {id_}: 出典URL『{u}』が Issue のコメント（または本文）のURLでない")
        if len(set(urls)) != len(urls):
            self.err(f"決定 {id_}: 出典URL に重複がある")
        from_text = sorted(set(re.findall(r"#(\d+)", d["出典"])))
        from_urls = sorted(set(m.group(1) for m in (ISSUE_URL_RE.fullmatch(u) for u in urls) if m))
        if from_text != from_urls:
            self.err(f"決定 {id_}: 出典の Issue 番号 {inspect_list(from_text)} と出典URL の Issue 番号 {inspect_list(from_urls)} が食い違う")

    def check_area_fixed(self):
        areas = self.t["エリア"]
        fixed = group_by(self.t["エリア固定"], lambda r: r["エリアID"])
        codes = {a["エリアID"]: a["区域コード"] for a in areas}
        for a in areas:
            if a["台帳段階"] != "対象":
                continue
            rows = {r["項目"]: r["値"] for r in fixed.get(a["エリアID"], [])}
            for k in AREA_FIXED_REQUIRED:
                if blank(rows.get(k, "")):
                    self.err(f"エリア固定 {a['エリアID']}: 項目 {k} が無い（対象エリアは机の天面・台座を持つ）")
            others = [o for o in areas if o["エリアID"] != a["エリアID"]]
            for r in fixed.get(a["エリアID"], []):
                if r["型"] != "文":
                    continue
                for o in others:
                    if len(o["名称"]) >= 2 and o["名称"] in r["値"]:
                        self.err(f"エリア固定 {a['エリアID']}.{r['項目']}: 別エリアの名称『{o['名称']}』が混ざっている（プロンプトへ漏れる）")
                    if re.search(r"\b" + re.escape(codes[o["エリアID"]]) + r"-\d", r["値"], A):
                        self.err(f"エリア固定 {a['エリアID']}.{r['項目']}: 別エリアの MAP ID（{codes[o['エリアID']]}-）が混ざっている")
        area_ids = [a["エリアID"] for a in areas]
        for k in [k for k in fixed if k not in area_ids]:
            self.err(f"エリア固定: 未知のエリアID {k}")

    def check_area_landscape(self):
        areas = self.t["エリア"]
        rows = self.t["エリア景観"]
        for r in rows:
            id_ = r["エリアID"]
            if not any(a["エリアID"] == id_ for a in areas):
                self.err(f"エリア景観 {id_}: 未知のエリアID（エリア表に無い）")
            if id_ in AREA_LANDSCAPE_EXEMPT:
                self.err(f"エリア景観 {id_}: 体内は作成済みで対象外（行を作らない）")
            src = r["出典"]
            if not (re.search(r"https?://", src) or any(ln.strip(WS).startswith("出典なし（") and ln.strip(WS).endswith("）") for ln in rlines(src))):
                self.err(f"エリア景観 {id_}: 出典に URL（http で始まる）も『出典なし（理由）』も無い")
            virt = [s for s in (ln.strip(WS) for ln in rlines(r["冬の景色の仮想表現"])) if s]
            if not virt:
                self.err(f"エリア景観 {id_}: 冬の景色の仮想表現が空")
            for ln in virt:
                if not ln.startswith("【仮想】"):
                    self.err(f"エリア景観 {id_}: 冬の景色の仮想表現の行に【仮想】が無い（行頭に付けて事実と仮想を区別する）: {ln[:30]}…")
        have = [r["エリアID"] for r in rows]
        for a in areas:
            if a["台帳段階"] != "対象" or a["エリアID"] in AREA_LANDSCAPE_EXEMPT:
                continue
            if a["エリアID"] not in have:
                self.err(f"エリア景観: 台帳段階=対象のエリア {a['エリアID']} の行が無い")

    def check_buildings(self):
        parts = self.t["建物部位"]
        for w in self.t["建物窓列"]:
            part = next((p for p in parts if p["部位ID"] == w["部位ID"]), None)
            if not part:
                continue
            if part["状態"] == "開放" and to_i(w["個数"]) > 0:
                self.err(f"建物窓列 {w['窓列ID']}: 部位 {part['部位ID']} が開放なのに窓列がある（開放と窓列は両立しない）")
            if part["状態"] == "なし" and to_i(w["個数"]) > 0:
                self.err(f"建物窓列 {w['窓列ID']}: 部位が窓なしなのに個数が {w['個数']}")
        ws = [w for w in self.t["窓"] if w["建物窓列ID"] != ""]
        for (wid, mid, era, wall), rows in group_by(ws, lambda w: (w["建物窓列ID"], w["MAP_ID"], w["適用時期"], w["壁"])).items():
            x = next((x for x in self.t["建物窓列"] if x["窓列ID"] == wid), None)
            n = x.get("個数") if x is not None else None
            if n is not None and to_i(n) != len(rows):
                self.err(f"窓 {mid}{'' if era == '' else '-' + era} の壁 {wall}: 建物窓列 {wid} の個数 {n} と窓表の行数 {len(rows)} が違う")

    def check_confirmed_edges(self):
        for e in self.t["端"]:
            if e["状態"] == "確定" and blank(e["決定参照"]):
                self.err(f"端 {e['端ID']}: 状態が『確定』なのに決定参照が無い（根拠の決定を書くか、既定(要確認)にして未決へ）")

    def check_windows(self):
        for w in self.t["窓"]:
            if w["種別"] == "窓なし":
                continue
            if w["壁側"] == "" or w["状態"] == "":
                self.err(f"窓 {w['窓ID']}: 壁側/状態が空")

    def layout_regexps(self):
        if self._layout_regexps is None:
            out = []
            for r in self.t["ファイル配置"]:
                try:
                    out.append(re.compile(r"(?:" + r["パターン"].replace("{MAP_ID}", MAP_ID_RE) + r")", A))
                except re.error:
                    out.append(None)
            self._layout_regexps = out
        return self._layout_regexps

    def check_layout(self):
        rows = self.t["ファイル配置"]
        table_names = LY.tables()
        regs = self.layout_regexps()
        for i, r in enumerate(rows):
            id_ = r["配置ID"]
            if r["パターン"] == "" or regs[i] is None:
                self.err(f"ファイル配置 {id_}: パターンが空・正規表現として不正")
            if r["種別"] == "" or r["用途"] == "":
                self.err(f"ファイル配置 {id_}: 種別・用途が空")
            if r["到達"] not in ("リンク", "許可"):
                self.err(f"ファイル配置 {id_}: 到達 '{r['到達']}' は リンク/許可 のどちらでもない")
            if r["到達"] == "許可":
                if blank(r["許可リスト理由"]):
                    self.err(f"ファイル配置 {id_}: 到達=許可 には許可リスト理由が要る")
            elif not blank(r["許可リスト理由"]) or not blank(r["入口"]):
                self.err(f"ファイル配置 {id_}: 到達=リンク に許可リスト理由・入口がある")
            for tb in split_semi(r["所有表"]):
                if tb not in table_names:
                    self.err(f"外部キー ファイル配置.所有表='{tb}' が表に無い（{id_}）")
            for e in split_semi(r["入口"]):
                p = os.path.join(self.root, e.lstrip("/")) if e.startswith("/") else os.path.join(self.root, e)
                if not os.path.exists(p):
                    self.err(f"外部キー ファイル配置.入口='{e}' が実在しない（{id_}）")
        for g in self.t["生成物"]:
            if any(re_.fullmatch(g["パス"]) for re_ in regs if re_):
                continue
            self.err(f"生成物 {g['生成物ID']}: パス {g['パス']} がどの配置規則（ファイル配置）にも一致しない")

    def _fresh(self, script, label):
        tool = os.path.join(HERE, "..", ".claude", "skills", "sit-field-background", "tools", script)
        tool = os.path.abspath(tool)
        out, ok = run_capture(["uv", "run", "--project", PROJECT, "python3", tool, "check"], {"LEDGER_ROOT": self.root})
        if not ok:
            self.err(f"{label}の生成ビューが古い、または検査できない: {' / '.join(rlines(out.strip(WS))[:2])}")

    def check_index_fresh(self):
        self._fresh("ledger_index.py", "docs/INDEX.md ")

    def check_views_fresh(self):
        self._fresh("ledger_views.py", "docs/ledger-views/ ")

    def check_generated(self):
        for g in self.t["生成物"]:
            path = os.path.join(self.root, g["パス"])
            if not os.path.isfile(path):
                self.err(f"生成物 {g['生成物ID']}: パス {g['パス']} が無い（リンク切れ）")
                continue
            if not (g["パス"].endswith(".json") and g["入力ハッシュ"] != ""):
                continue
            if g["生成物ID"] == "G-asset-migration":
                continue
            with open(path, encoding="utf-8") as f:
                prov = json.load(f).get("_provenance") or {}
            if prov.get("input_sha") != g["入力ハッシュ"]:
                self.err(f"生成物 {g['生成物ID']}: JSON の _provenance.input_sha が生成物表と違う（手編集か古い）")
        if "LEDGER_SKIP_REGEN" in os.environ:
            return
        tool = os.path.join(self.root, ".claude/skills/sit-field-background/tools/ledger_build.py")
        if not os.path.isfile(tool):
            return
        out, ok = run_capture(["uv", "run", "python3", tool, "check"])
        if not ok:
            self.err(f"派生JSONが台帳から再生成した内容と一致しない: {' / '.join(rlines(out.strip(WS))[:3])}")

    def check_domains(self):
        for script, *args in (["verify_domain_ledger.py"], ["verify_content_ledger.py"], ["asset_metadata.py", "check"]):
            out, ok = run_capture(["uv", "run", "--project", PROJECT, "python3", os.path.join(PROJECT, "scripts", script), *args], {"LEDGER_ROOT": self.root}, cwd=PROJECT)
            if not ok:
                self.err(f"{script}: {' / '.join(rlines(out.strip(WS))[:5])}")
        for script, *args in (["content_ledger.py", "bgm-csv", "check"], ["content_ledger_views.py", "check"], ["map_source_views.py", "check"]):
            out, ok = run_capture(["uv", "run", "--project", PROJECT, "python3", os.path.join(PROJECT, "scripts", script), *args], {"LEDGER_ROOT": self.root}, cwd=PROJECT)
            if not ok:
                self.err(f"{script}: {' / '.join(rlines(out.strip(WS))[:3])}")

    def check_free_text(self):
        free = "特徴(自由記述)"
        forb = [w for d in self.t["決定"] if d["状態"] == "有効" for w in split_rb(d["禁止語"], ";")] + [v["値"] for v in self.t["語彙"] if v["グループ"] == "禁止語"]
        for tb, rows in self.t.items():
            if not (rows and free in rows[0]):
                continue
            for r in rows:
                text = r[free]
                if text == "":
                    continue
                who = f"{tb} {first_val(r)}"
                for w in uniq(forb):
                    if w not in text:
                        continue
                    if not re.search(r"描かない|ない|禁止|不可|しない", text):
                        self.warn(f"自由記述 {who}: 禁止語『{w}』が出る（否定形でなければ衝突）")
                m = re.search(r"\d+\s*(px|cm|mm|単位|ピクセル)", text, A)
                if m:
                    self.warn(f"自由記述 {who}: 寸法らしい数値（{m.group(0)}）→ 必須キー・要素表へ移す候補")
                m = re.search(r"\d+\s*(個|本|枚|つ|か所)", text, A)
                if m:
                    self.warn(f"自由記述 {who}: 個数らしい数値（{m.group(0)}）→ 必須キーへ移す候補")
                if tb == "MAP" and r["床材"] != "" and "畳" in text and "畳" not in r["床材"]:
                    self.warn(f"自由記述 {who}: 床材キー（{r['床材']}）と食い違う可能性（畳）")


def warn_line(msg):
    """Ruby の Kernel#warn と同じく、末尾が改行なら改行を足さない"""
    print(msg, file=sys.stderr, end="" if msg.endswith("\n") else "\n")


def main():
    v = LedgerVerifier().run()
    for w in v.warnings:
        warn_line(f"WARN: {w}")
    if not v.errors:
        print(f"PASS: ledger tables={len(LY.tables())}, decisions={len(v.t['決定'])}, maps={len(v.t['MAP'])}, warnings={len(v.warnings)}")
    else:
        for e in v.errors:
            warn_line(f"FAIL: {e}")
        print(f"FAIL: {len(v.errors)} errors", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
