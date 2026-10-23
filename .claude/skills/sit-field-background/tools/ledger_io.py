"""台帳（docs/ledger/<表名>.yaml）の読み書きと共通の値変換。マスターは日本語キーの YAML（UTF-8・LF・BOM なし）。

表ごとに 1 ファイル。中身は「行のリスト」で、各行はキー=日本語列名の辞書。
全スカラーを文字列として扱う（読み込み時に文字列へ正規化、書き出し時に必ず引用。no/yes/null/001/1e3 が型変換されない）。
空欄は空文字。複数行テキストは block scalar。ファイル先頭の `#` コメントは表の説明（書き出しで再生成される。
人が行の途中に足したコメントはプログラム経由の write で消える）。

行の順序は意味を持つ（plan の配列順＝描画順）。主キー昇順に並べ替えない。
YAML の読み込みに PyYAML が要る（リポ直下の pyproject.toml で依存宣言。`uv run python3` で自動的に入る）。
"""
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
LEDGER = os.path.join(REPO, "docs", "ledger")
BUILDER_VERSION = "ledger-build/1"

FREE = "特徴(自由記述)"

# 表ごとの列（この順で書く。列を足すときは末尾の特徴の直前）
SCHEMA = {
    "エリア": ["エリアID", "区域コード", "名称", "目標枚数", "台帳段階", "机の天面の材質", "台座の素材", "木の種類", "外周の装飾方針", "備考", FREE],
    "MAP": ["MAP_ID", "エリアID", "名称", "字幕", "時期", "屋内外", "状態", "建物ID", "表現する部位", "一言特徴", "描画方式", "装飾プールID", "依存MAP", "依存の確度", "依存の根拠",
            "床材", "壁材", "窓", "扉の意匠", "工作の材質", "時期差分", "採用状態", "寸法根拠", "備考", FREE],
    "建物": ["建物ID", "名称", "エリアID", "種別", "外形", "屋根", "外壁", "窓列", "扉", "材質", "関係", "状態", "備考", FREE],
    "建物部位": ["部位ID", "建物ID", "部位種別", "方角", "状態", "材質", "見た目", "決定参照", FREE],
    "建物窓列": ["窓列ID", "建物ID", "部位ID", "個数", "先頭比", "間隔比", "幅比", "窓台比", "高さ比", "窓種別", "理由", "決定参照", FREE],
    "建物関係": ["通番", "建物A", "建物B", "関係", "方角", "接続端ID", "決定参照", FREE],
    "建物時期差分": ["建物ID", "時期", "部位ID", "差分", "内容", "決定参照", FREE],
    "端": ["端ID", "MAP_ID", "適用時期", "種別", "壁", "壁側", "面", "中心", "沿い範囲", "相手端", "幅クラス", "状態", "通路", "建物部位ID", "備考", "決定参照", "属性JSON", FREE],
    "接続": ["端A", "端B", "種別", "期待", "ラベル", "方角A", "方角B", "外部", "無効時期", "図", "主路・状態", "決定参照", FREE],
    "接続図設定": ["図ID", "項目", "値", "型", "決定参照"],
    "要素": ["MAP_ID", "適用時期", "要素ID", "種別", "名称", "建物部位ID", "見た目", "決定参照", "属性JSON", FREE],
    "窓": ["窓ID", "MAP_ID", "適用時期", "壁", "壁側", "中心", "幅", "種別", "窓台", "高さ", "状態", "沿い範囲", "建物窓列ID", "連番", "備考", "決定参照", "属性JSON", FREE],
    "時期差分": ["MAP_ID", "時期", "項目", "値", "決定参照"],
    "既定値": ["既定ID", "MAP_ID", "適用時期", "内容", "決定参照"],
    "エリア固定": ["エリアID", "項目", "値", "型", "決定参照"],
    "装飾プール": ["プールID", "項目", "値", "型", "決定参照"],
    "語彙": ["語彙ID", "グループ", "値", "英語断片", "説明"],
    "決定": ["決定ID", "日付", "対象種別", "対象ID", "対象名", "決定の要点", "逐語", "出典", "出典URL", "状態", "置換先", "プロンプト出力", "必須語", "禁止語", "対象MAP", "備考", FREE],
    "採用要素": ["採用要素ID", "素材ID", "元MAP", "要素", "内容", "継承先MAP", "継承方法", "状態", "確認語", "決定参照", FREE],
    "素材": ["素材ID", "所有者ID", "種別", "パス", "状態", "日付", "来歴", "sha256", FREE],
    "生成物": ["生成物ID", "種別", "パス", "元の表", "入力ハッシュ", "生成日時", "再生成コマンド", "備考"],
    "必須キー": ["対象テーブル", "キー", "必須度", "条件", "語彙グループ", "説明"],
    "未決": ["未決ID", "対象テーブル", "対象ID", "キー", "内容", "状態", "解決決定ID"],
    "キー別名": ["正規名", "別名", "対象テーブル", "説明"],
}


# 表の説明（YAML ファイル先頭のコメントになる）
TABLE_DOC = {
    "エリア": "エリア（区域）の台帳。1行=1エリア。",
    "MAP": "MAP（1枚の背景）の台帳。1行=1MAP。",
    "建物": "建物の台帳。屋内と外観は同じ建物行から導出する。",
    "建物部位": "建物の部位（壁・屋根・扉など）。",
    "建物窓列": "建物の壁ごとの窓列。",
    "建物関係": "建物どうしの関係（渡り廊下で接続など）。",
    "建物時期差分": "建物の時期ごとの差分。",
    "端": "MAP の端（戸口・開口・縁）。",
    "接続": "端と端の接続。",
    "接続図設定": "接続図の描画設定（図ID×項目）。",
    "要素": "MAP 内の要素（家具・物・樹木など）。",
    "窓": "MAP の壁の窓。",
    "時期差分": "MAP の時期ごとの差分。",
    "既定値": "仮置きの既定値（要確認）。",
    "エリア固定": "エリア単位で固定する指定（机の天面・木の種類・台座など）。",
    "装飾プール": "装飾プールの設定。",
    "語彙": "許す・禁じる語彙と英語プロンプト断片。",
    "決定": "kako-jun の決定（逐語・出典つき）。status に関係なくプロンプトへ入る。",
    "採用要素": "採用画像から次の絵へ継承する要素。",
    "素材": "素材（画像・マスクなど。没も行で保持）。",
    "生成物": "派生物（JSON）の登録と鮮度検査用ハッシュ。",
    "必須キー": "対象テーブルごとの必須キー定義。",
    "未決": "未決（要確認）の一覧。",
    "キー別名": "列名・キー名の別名と正規名。",
}


def path(table):
    return os.path.join(LEDGER, f"{table}.yaml")


def _q(v):
    """全スカラーを二重引用符つきで書く（JSON の文字列表記は YAML の二重引用符スカラーと互換）。"""
    return json.dumps(v, ensure_ascii=False)


def _block_ok(v):
    """block scalar（|-）で無損失に書ける文字列か。"""
    if "\n" not in v or v != v.strip() or "\n\n\n" in v:
        return False
    for ch in v:
        if ch == "\n":
            continue
        if ord(ch) < 32 or ord(ch) == 127 or ch in "\u0085\u2028\u2029\ufeff":
            return False
    # 空白だけの行・行末の空白は block scalar で壊れやすいので引用に回す
    return all(ln == ln.rstrip() and (ln.strip() or not ln) for ln in v.split("\n"))


def dumps(table, rows):
    cols = SCHEMA[table]
    out = [f"# 表: {table} — {TABLE_DOC.get(table, '')}", f"# 列: {' / '.join(cols)}",
           "# 全スカラーは文字列（引用符つき）。空欄は \"\"。複数行は |- ブロック。"]
    if not rows:
        out.append("[]")
    for r in rows:
        extra = set(r) - set(cols)
        if extra:
            raise KeyError(f"{table}: 未定義の列 {sorted(extra)}")
        for i, c in enumerate(cols):
            v = "" if r.get(c) is None else str(r.get(c))
            lead = "- " if i == 0 else "  "
            if _block_ok(v):
                out.append(f"{lead}{_q(c)}: |-")
                out.extend(("      " + ln) if ln else "" for ln in v.split("\n"))
            else:
                out.append(f"{lead}{_q(c)}: {_q(v)}")
    return "\n".join(out) + "\n"


def _str(v):
    if v is None:
        return ""
    if isinstance(v, bool):
        return "true" if v else "false"
    return str(v)


def parse(table, text):
    import yaml
    data = yaml.safe_load(text)
    if data is None:
        return []
    if not isinstance(data, list):
        raise ValueError(f"{table}: 最上位は行のリストでなければならない")
    cols = SCHEMA.get(table, [])
    rows = []
    for i, r in enumerate(data):
        if not isinstance(r, dict):
            raise ValueError(f"{table}: {i + 1}行目が辞書でない")
        row = {_str(k): _str(v) for k, v in r.items()}
        for c in cols:
            row.setdefault(c, "")
        rows.append(row)
    return rows


def read(table):
    p = path(table)
    if not os.path.exists(p):
        return []
    with open(p, encoding="utf-8", newline="") as f:
        return parse(table, f.read())


def write(table, rows):
    os.makedirs(LEDGER, exist_ok=True)
    with open(path(table), "w", encoding="utf-8", newline="") as f:
        f.write(dumps(table, rows))


def jdump(o):
    return json.dumps(o, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha(s):
    return hashlib.sha256(s.encode("utf-8") if isinstance(s, str) else s).hexdigest()


def sha_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


# ---- 値の語彙（JSON の英語値 ⇔ 台帳の日本語値）。語彙表の「グループ」と対応する
SIDE = {"west": "西", "east": "東", "north": "北", "south": "南"}
STATUS = {"fixed": "確定", "default": "既定(要確認)"}
WIDTH = {"2people": "2人分", "1.5people": "1.5人分", "1person": "1人分"}
WKIND = {"waist": "腰高", "floor": "掃き出し"}
EKIND = {"floors": "床", "walls": "壁", "boxes": "家具", "paths": "経路", "tree_zones": "樹木帯", "annotations": "注記"}
EDGE_KIND = {"doors": "戸口", "openings": "開口", "markers": "縁"}


def inv(d):
    return {v: k for k, v in d.items()}


def jp(d, v):
    return d.get(v, v) if v is not None else ""


def en(d, v):
    return inv(d).get(v, v) if v not in (None, "") else None


def split_list(s):
    return [x for x in (s or "").split(";") if x]
