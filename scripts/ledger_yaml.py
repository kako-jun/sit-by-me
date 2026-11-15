"""docs/ledger/<表名>.yaml の読み込み（検査・描画スクリプト共通）。

マスターは日本語キーの YAML（表ごと1ファイル、中身は行のリスト）。全スカラーは文字列。
構文検査・表定義(SCHEMA)は .claude/skills/sit-field-background/tools/ledger_io.py に一本化してあり、ここは root 差し替えと
行の包み（欠けた列は '' を返す Row）だけを足す。書き出しは ledger_io.py だけが行う。
scripts/ だけを複製した最小の検査用 root（ledger_io.py が無い）では、表定義が無いので列照合だけ省く（構文検査は下の
フォールバックで行う。旧 Ruby 版と同じ挙動）。
"""
import glob
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get("LEDGER_ROOT") or os.path.abspath(os.path.join(HERE, ".."))
LEDGER = os.path.join(ROOT, "docs", "ledger")
TOOLS = os.path.join(HERE, "..", ".claude", "skills", "sit-field-background", "tools")
if os.path.isfile(os.path.join(TOOLS, "ledger_io.py")) and TOOLS not in sys.path:
    sys.path.insert(0, TOOLS)
try:
    import ledger_io  # noqa: E402
except ImportError:  # 最小の検査用 root。列照合を省き、構文検査はフォールバックを使う
    ledger_io = None


class Row(dict):
    """行。欠けた列は '' を返す（キーの有無は in / keys() で見る）。"""

    def __missing__(self, key):
        return ""


def path(table):
    return os.path.join(LEDGER, f"{table}.yaml")


def _fallback_check_syntax(table, text):
    """ledger_io.check_syntax と同じ規則（ledger_io.py が無い最小 root 用。規則を変えるときは両方）。"""
    import yaml
    node = yaml.compose(text, Loader=getattr(yaml, "CSafeLoader", yaml.SafeLoader))
    if node is None:
        return None
    if not isinstance(node, yaml.SequenceNode):
        raise ValueError(f"{table}: 最上位は行のリストでなければならない")
    for i, item in enumerate(node.value):
        if not isinstance(item, yaml.MappingNode):
            raise ValueError(f"{table}: {i + 1}行目が辞書でない")
        seen = {}
        for k, v in item.value:
            for n in (k, v):
                if not isinstance(n, yaml.ScalarNode):
                    raise ValueError(f"{table}: {n.start_mark.line + 1}行目: スカラー以外（入れ子）は使えない")
                if n.style not in ('"', "'", "|", ">"):
                    raise ValueError(f"{table}: {n.start_mark.line + 1}行目: 引用符のないスカラー『{n.value}』（全スカラーは \"…\" か |- ブロックで書く）")
            if k.value in seen:
                raise ValueError(f"{table}: {k.start_mark.line + 1}行目: キー『{k.value}』が同じ行（{seen[k.value]}行目に既出）で重複している")
            seen[k.value] = k.start_mark.line + 1
    return node


def schema():
    return ledger_io.SCHEMA if ledger_io else {}


def read(table, root=None):
    p = os.path.join(root or ROOT, "docs", "ledger", f"{table}.yaml")
    if not os.path.isfile(p):
        return []
    with open(p, encoding="utf-8", newline="") as f:
        text = f.read()
    node = (ledger_io.check_syntax if ledger_io else _fallback_check_syntax)(table, text)
    if node is None:
        return []
    cols = schema().get(table)
    rows = []
    for i, item in enumerate(node.value):
        row = Row((k.value, v.value) for k, v in item.value)
        if cols is not None:
            extra = [k for k in row if k not in cols]
            if extra:
                raise ValueError(f"{table}.yaml: {i + 1}行目に表定義に無い列 {extra}（ledger_io.py の SCHEMA。綴り間違い？ 正しい列: {' / '.join(cols)}）")
        rows.append(row)
    return rows


def header(table):
    """表に現れるキー（先頭から出現順の和集合）。"""
    seen = {}
    for r in read(table):
        for k in r:
            seen.setdefault(k, None)
    return list(seen)


def tables():
    return sorted(os.path.basename(p)[:-5] for p in glob.glob(os.path.join(LEDGER, "*.yaml")))


def load_all():
    return {t: read(t) for t in tables()}
