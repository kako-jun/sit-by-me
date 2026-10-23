# -*- coding: utf-8 -*-
"""曲線2: MAP のキー・決定表・必須キー・未決・別名・採用要素・素材"""
import json, sys, re
sys.path.insert(0, '<repo>/.claude/skills/sit-field-background/tools')
sys.path.insert(0, '<scratchpad>/lm')
import ledger_io as L
UND = "未決(要確認)"; NA = "該当なし"
STD = "標準(段ボール・紙粘土・綿の雪・木)"
unresolved = []   # (対象テーブル, 対象ID, キー, 内容)

maps = L.read("MAP")
by = {m["MAP_ID"]: m for m in maps}
INSIDE = {"TRM-02": ("屋内", "BLD-TRM-youchien", "内側"), "TRM-04": ("屋内", "BLD-TRM-honden;BLD-TRM-corridor-w;BLD-TRM-corridor-e", "内側"),
          "TRM-05": ("屋内", "BLD-TRM-jukyo", "内側"),
          "TRM-03": ("屋外", "BLD-TRM-honden;BLD-TRM-corridor-w;BLD-TRM-corridor-e;BLD-TRM-jukyo;BLD-TRM-youchien", "外側")}
FLOOR = {"TRM-02": "板張り(リノリウム可)", "TRM-03": "綿の雪の地面+石畳の参道", "TRM-04": "板張り", "TRM-05": "板張り(ロールござ可)", "TRM-12": UND, "TRM-13": UND}
WALL = {"TRM-02": "漆喰と木の柱・梁", "TRM-03": "漆喰と木の柱・梁", "TRM-04": "漆喰と木の柱・梁", "TRM-05": "漆喰と木の柱・梁",
        "TRM-06": "土塀", "TRM-07": "土塀", "TRM-08": "土塀"}
WINDOW = {"TRM-02": "窓あり", "TRM-03": "窓あり", "TRM-04": "窓あり", "TRM-05": "窓あり", "TRM-06": NA, "TRM-07": NA, "TRM-08": NA, "TRM-10": NA, "TRM-13": NA, "TRM-14": NA,
          "TRM-15": NA, "TRM-16": NA, "TRM-17": NA}
ERA = {"TRM-02": "なし", "TRM-03": "あり(→時期差分・建物時期差分)", "TRM-04": "なし", "TRM-05": "あり(→時期差分・建物時期差分)",
       "TRM-06": "なし", "TRM-07": "なし", "TRM-08": "なし", "TRM-15": "なし", "TRM-16": "なし", "TRM-17": "なし"}
FEATURE_FREE = {
    "TRM-05": "食卓（机）の上にみかんを置く（採用画像の良い点。→採用要素 TRM-05.mikan。決定 TRM.inherit-elements）",
}
for mid, m in by.items():
    n = int(mid.split("-")[1])
    if n == 1:
        m.update({"エリアID": "teramachi", "名称": "園庭（廃止）", "状態": "廃止", "屋内外": "屋外", "表現する部位": NA, "描画方式": "未設計", "装飾プールID": NA,
                  "依存MAP": "なし", "床材": NA, "壁材": NA, "窓": NA, "扉の意匠": NA, "工作の材質": NA, "時期差分": "なし", "採用状態": "廃止(統合)",
                  "備考": "2026-10-23 に TRM-03 の右の区画（園庭）へ統合して廃止（決定 TRM-03.garden）。欠番。"})
        continue
    plan = mid in INSIDE
    if plan:
        io, bid, part_ = INSIDE[mid]
        m.update({"屋内外": io, "建物ID": bid, "表現する部位": part_, "状態": "モック承認済み"})
    else:
        m.update({"屋内外": "屋内" if mid == "TRM-12" else "屋外", "表現する部位": NA, "状態": "未設計"})
        m["備考"] = "plan・モックは別ブランチ teramachi-rest-mocks-20261023（本ブランチ未取込）。画像生成は承認後"
    m["描画方式"] = "斜めモック" if plan else "未設計"
    m["床材"] = FLOOR.get(mid, "黒紙・サンドペーパーの道(綿の雪)")
    m["壁材"] = WALL.get(mid, UND if not plan else UND)
    m["窓"] = WINDOW.get(mid, UND)
    m["扉の意匠"] = "建物の扉に従う(→建物表)" if plan else (UND if mid in ("TRM-06", "TRM-11", "TRM-12") else NA)
    m["工作の材質"] = STD
    m["時期差分"] = ERA.get(mid, UND)
    m["採用状態"] = "基準採用済み" if mid == "TRM-04" else "未採用"
    if mid in ("TRM-05", "TRM-03"):
        pass
    m["装飾プールID"] = m["装飾プールID"] or UND
    if not m["依存MAP"]:
        m["依存MAP"] = "なし"
    if mid in FEATURE_FREE:
        m[L.FREE] = FEATURE_FREE[mid]
    # 床材=黒紙…は sit-diorama の共通規約の適用（決めたものではなく既定規約）
    for k in ("床材", "壁材", "窓", "扉の意匠", "時期差分", "装飾プールID", "依存の確度"):
        pass
    for k in ("床材", "壁材", "窓", "扉の意匠", "時期差分", "装飾プールID"):
        if m[k] == UND:
            unresolved.append(("MAP", mid, k, ""))
    if m.get("依存の確度") == "要確認":
        unresolved.append(("MAP", mid, "依存MAP", "依存グラフで『要確認』（同じ建物・扉・場所を共有するか）"))
L.write("MAP", maps)
json.dump(unresolved, open('<scratchpad>/lm/unresolved.json', 'w'), ensure_ascii=False)
print(len(unresolved), "unresolved")
