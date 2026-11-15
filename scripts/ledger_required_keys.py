"""必須キー（docs/ledger/必須キー.yaml）の強制。空欄=未決として検出、語彙外の値=エラー、『未決(要確認)』は未決表への登録が要る。

  uv run python3 scripts/ledger_required_keys.py MAP_ID   # そのMAP（とエリア・建物・端）の必須キーが全部埋まっているか。欠落を列挙して exit 1
verify_map_ledger.py からはライブラリとして使う。
"""
import re
import sys
from collections import defaultdict

import ledger_yaml as LY

UNDECIDED = "未決(要確認)"
NOT_APPLICABLE = ["該当なし", "なし"]
KEY_TABLE_ID = {"エリア": "エリアID", "MAP": "MAP_ID", "建物": "建物ID", "端": "端ID", "決定": "決定ID", "採用要素": "採用要素ID", "素材": "素材ID", "生成物": "生成物ID",
                "図配置": "配置ID", "MAP仕様": "仕様ID", "MAP契約": "契約ID", "特殊遷移": "遷移ID", "体内幾何": "幾何ID",
                "敵": "敵ID", "召喚獣": "召喚獣ID", "敵配置": "配置ID", "ダンジョン": "ダンジョンID", "人物": "人物ID",
                "Issue出典": "出典ID", "Issue命題": "命題ID"}
KEY_TABLE_ID.update({t: cols[0] for t, cols in LY.schema().items()})

ANNOTATED_GROUPS = ["採用要素状態"]
REQUIRED_DEGREES = ["必須", "条件付き必須"]
# 必須キー表がこれを持っていなくても生成ゲートが開かないように、コード側に固定した最低限の必須キー（対象テーブル => キー）。
ANCHOR_KEYS = {
    "エリア": ["名称", "区域コード", "机の天面の材質", "台座の素材", "木の種類", "外周の装飾方針"],
    "エリア景観": ["エリアID", "一言で言い当てる特徴", "出典", "冬の景色の仮想表現"],
    "MAP": ["エリアID", "屋内外", "状態", "描画方式", "床材", "壁材", "窓", "扉の意匠", "工作の材質", "時期差分", "建物ID", "表現する部位", "依存MAP", "装飾プールID", "@接続", "@窓の整合", "@時期差分の整合"],
}


def check_definition(tables):
    """必須キー表そのものの健全性: 未知の対象テーブル・未知の必須度は黙って無効にせずエラー、アンカーの行が在って必須度が有効であること"""
    errors = []
    for rk in tables["必須キー"]:
        if rk["対象テーブル"] not in KEY_TABLE_ID:
            errors.append(f"必須キー {rk['対象テーブル']}.{rk['キー']}: 対象テーブル『{rk['対象テーブル']}』は検査未対応（KEY_TABLE_ID に無い。黙って無効になる）")
        if rk["必須度"] not in REQUIRED_DEGREES:
            errors.append(f"必須キー {rk['対象テーブル']}.{rk['キー']}: 必須度『{rk['必須度']}』は {'／'.join(REQUIRED_DEGREES)} のどちらでもない（黙って無効になる）")
    for t, keys in ANCHOR_KEYS.items():
        for k in keys:
            if not any(rk["対象テーブル"] == t and rk["キー"] == k for rk in tables["必須キー"]):
                errors.append(f"必須キー表に最低限の行『{t}.{k}』が無い（コード側アンカー。消すと生成ゲートが黙って開く）")
    return errors


def cond_true(cond, row):
    if not cond:
        return True
    for c in cond.split("&"):
        m = re.fullmatch(r"(.+?)(!=|=)(.*)", c.strip(), re.S)
        if m:
            eq = row[m.group(1)] == m.group(3)
            if not (eq if m.group(2) == "=" else not eq):
                return False
    return True


def vocab(tables):
    out = defaultdict(list)
    for r in tables["語彙"]:
        out[r["グループ"]].append(r["値"])
    return out


def check_rows(tables, only=None):
    """戻り値: (errors(blank/語彙外/未登録の未決), undecided([テーブル, ID, キー]))"""
    errors = check_definition(tables)
    undecided = []
    voc = vocab(tables)
    unresolved = [(r["対象テーブル"], r["対象ID"], r["キー"]) for r in tables["未決"]]
    map_ids = [r["MAP_ID"] for r in tables["MAP"]]
    pools = list(dict.fromkeys(r["プールID"] for r in tables["装飾プール"]))
    for rk in tables["必須キー"]:
        t = rk["対象テーブル"]
        idcol = KEY_TABLE_ID.get(t)
        if idcol is None:
            continue
        for row in tables[t]:
            id_ = row[idcol]
            if only and not only(t, row):
                continue
            if not (rk["必須度"] == "必須" or cond_true(rk["条件"], row)):
                continue
            key = rk["キー"]
            if key.startswith("@"):
                err = pseudo(key, tables, row, t)
                if err:
                    errors.append(f"{t} {id_}: {key} {err}")
                continue
            v = row[key]
            if not v.strip():
                errors.append(f"{t} {id_}: 必須キー『{key}』が空欄（未決は『{UNDECIDED}』と明示して未決表に載せる）")
                continue
            if v == UNDECIDED:
                undecided.append([t, id_, key])
                if (t, id_, key) not in unresolved:
                    errors.append(f"{t} {id_}: 『{key}』が{UNDECIDED}なのに未決表に行が無い")
                continue
            g = rk["語彙グループ"]
            if not g:
                continue
            toks = v.split(";") if key in ("依存MAP", "建物ID") else [v]
            for tok in toks:
                if g in ANNOTATED_GROUPS:
                    tok = tok.split("（")[0]
                ok = tok in voc.get(g, [])
                ok = ok or (key == "依存MAP" and tok in map_ids)
                ok = ok or (key == "装飾プールID" and tok in pools)
                if not ok:
                    errors.append(f"{t} {id_}: 『{key}』の値『{tok}』が語彙（{g}）に無い")
    return errors, undecided


def pseudo(key, tables, row, table):
    if key == "@接続":
        id_ = row["MAP_ID"]
        hit = any(c["端A"].startswith(f"{id_}.") or c["端B"].startswith(f"{id_}.") for c in tables["接続"])
        hit = hit or any(tr["起点MAP"] == id_ or tr["到着MAP"] == id_ for tr in tables.get("特殊遷移", []))
        return None if hit else "接続表・特殊遷移表に行が無い（出入口と相手を書く）"
    if key == "@窓の整合":
        id_ = row["MAP_ID"]
        wins = [w for w in tables["窓"] if w["MAP_ID"] == id_ and not w["適用時期"] and w["種別"] != "窓なし"]
        if row["窓"] == "窓あり":
            return "『窓あり』なのに窓表に窓の行が無い" if not wins else None
        if row["窓"] == "窓なし":
            return None if not wins else "『窓なし』なのに窓表に窓の行がある"
        return None
    if key == "@時期差分の整合":
        id_ = row["MAP_ID"]
        bs = row["建物ID"].split(";")
        rows = sum(1 for r in tables["時期差分"] if r["MAP_ID"] == id_)
        if row["表現する部位"] == "外側":
            rows += sum(1 for r in tables["建物時期差分"] if r["建物ID"] in bs)
        if row["時期差分"].startswith("あり"):
            return "『あり』なのに時期差分表・建物時期差分表に行が無い" if rows == 0 else None
        if row["時期差分"] == "なし":
            return None if rows == 0 else "『なし』なのに時期差分の行がある"
        return None
    if key == "@語句":
        return "必須語か禁止語のどちらかが要る" if not row["必須語"] and not row["禁止語"] else None
    return None


def for_map(tables, map_id):
    m = next((r for r in tables["MAP"] if r["MAP_ID"] == map_id), None)
    if m is None:
        return [f"MAP {map_id} が MAP 表に無い"], []
    bs = m["建物ID"].split(";")

    def only(t, row):
        if t == "エリア":
            return row["エリアID"] == m["エリアID"]
        if t == "MAP":
            return row["MAP_ID"] == map_id
        if t == "建物":
            return row["建物ID"] in bs
        if t == "端":
            return row["MAP_ID"] == map_id
        return False

    return check_rows(tables, only=only)


class Tables(dict):
    """表名 -> 行のリスト。未知の表は [] を返す（Ruby の Hash.new { [] } 相当）。"""

    def __missing__(self, key):
        return []


def main():
    id_ = sys.argv[1] if len(sys.argv) > 1 else ""
    needed = ["必須キー", "未決", "語彙", "エリア", "MAP", "建物", "端", "窓", "時期差分", "建物時期差分", "接続", "特殊遷移", "装飾プール"]
    tables = Tables({t: LY.read(t) for t in needed})
    errors, undecided = for_map(tables, id_)
    lines = list(errors)
    for t, i, k in undecided:
        if not any(f"{t} {i}: 『{k}』" in e for e in errors):
            lines.append(f"{t} {i}: 『{k}』が未決（生成を起動できない）")
    for ln in lines:
        print(ln)
    sys.exit(0 if not lines else 1)


if __name__ == "__main__":
    main()
