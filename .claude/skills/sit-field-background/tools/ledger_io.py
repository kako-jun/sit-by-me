"""台帳（docs/ledger/*.csv）の読み書きと共通の値変換。マスターは日本語ヘッダの CSV（UTF-8・LF・BOM なし）。

行の順序は意味を持つ（plan の配列順＝描画順）。主キー昇順に並べ替えない。
"""
import csv
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
    "MAP": ["MAP_ID", "エリアID", "名称", "字幕", "時期", "屋内外", "状態", "建物ID", "表現する部位", "一言特徴", "描画方式", "装飾プールID", "依存MAP",
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


def path(table):
    return os.path.join(LEDGER, f"{table}.csv")


def read(table):
    p = path(table)
    if not os.path.exists(p):
        return []
    with open(p, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write(table, rows):
    cols = SCHEMA[table]
    os.makedirs(LEDGER, exist_ok=True)
    with open(path(table), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(cols)
        for r in rows:
            extra = set(r) - set(cols)
            if extra:
                raise KeyError(f"{table}: 未定義の列 {sorted(extra)}")
            w.writerow([("" if r.get(c) is None else str(r.get(c))) for c in cols])


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
