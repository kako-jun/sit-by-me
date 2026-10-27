"""体内割付図の入力を `docs/ledger/体内幾何.yaml` から読む。

迷路の探索結果・描画画素は派生値。表は提案と確定を区別したまま読む。
BODY_DOCS_ROOT は既存の検証 fixture が使う入力rootの切り替え口。
"""
import os
from pathlib import Path

import ledger_flat as F
import ledger_io as L


def rows(table):
    root = Path(os.environ.get("BODY_DOCS_ROOT") or L.REPO)
    path = root / "docs/ledger" / f"{table}.yaml"
    if not path.is_file():
        raise FileNotFoundError(f"台帳が無い: {path}")
    return L.parse(table, path.read_text(encoding="utf-8"))


def load():
    grouped = {}
    for row in rows("体内幾何"):
        key = (row["MAP_ID"], row["変種"])
        grouped.setdefault(key, []).append((row["経路"], row["値"], row["型"]))
    return {key: F.unflatten(values) for key, values in grouped.items()}


def constants():
    return load()["GLOBAL", "基準"]


def specs():
    values = load()
    return {mid: spec for (mid, variant), spec in values.items()
            if mid != "GLOBAL" and mid != "BDY-04" and variant in ("基準", "A")}


def variant(map_id, name):
    return load()[map_id, name]


def maze_seed():
    return load()["BDY-04", "基準"]["seed"]
