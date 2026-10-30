"""斜めツール（oblique_*.py）が使う文面と定数の読み出し口。正本は台帳（docs/ledger）の次の2表。

  描画定数.yaml     視点・土台の寸法・戸口の幅の区分・窓の種別・台座の飾りの位置など、数値や短い語の定数
  プロンプト文面.yaml  imagegen 用プロンプト・接続表・窓一覧・接続図の凡例に出る日本語/英語の文面（{名前} が変数の差し込み口）

コードにはアルゴリズム（検査の計算・描画の手順）だけを残し、プロンプトに出る言葉と寸法の数値は台帳を変えれば変わる。
表が読めない・ID が無いときは黙って既定値を使わず、その場で止まる（再現性のため）。
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ledger_io as LIO  # noqa: E402

_CACHE = {}


def _table(name):
    if name not in _CACHE:
        _CACHE[name] = {r[SCHEMA_KEY[name]]: r for r in LIO.read(name)}
    return _CACHE[name]


SCHEMA_KEY = {"描画定数": "定数ID", "プロンプト文面": "文面ID"}
_PH = re.compile(r"\{([A-Za-z0-9_]+)\}")


def const(cid):
    """描画定数の値（文字列）。"""
    t = _table("描画定数")
    if cid not in t:
        sys.exit(f"描画定数 {cid} が台帳（docs/ledger/描画定数.yaml）に無い")
    return t[cid]["値"]


def const_num(cid):
    v = float(const(cid))
    return int(v) if v == int(v) else v


def const_json(cid):
    return json.loads(const(cid))


def text(tid, **kw):
    """文面 tid の {名前} に kw を差し込む（波括弧を含む文面でも壊れないよう、渡した名前だけを置換する）。差し込み忘れ・余計な変数はエラー。"""
    t = _table("プロンプト文面")
    if tid not in t:
        sys.exit(f"プロンプト文面 {tid} が台帳（docs/ledger/プロンプト文面.yaml）に無い")
    s = t[tid]["文面"]
    names = set(_PH.findall(s))
    if names != set(kw):
        sys.exit(f"プロンプト文面 {tid}: 変数が合わない（文面の変数 {sorted(names)} / 渡した変数 {sorted(kw)}）")
    return _PH.sub(lambda m: str(kw[m.group(1)]), s)


def base_era_reference(base, era):
    """時期差分MAPの REFERENCE IMAGES 節に入る、基準MAPの確定画像の使い方の文（台帳 プロンプト文面.PR.reference.base-era。#193）。"""
    return text("PR.reference.base-era", base=base, era=era)
