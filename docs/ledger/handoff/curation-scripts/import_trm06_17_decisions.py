"""決定・未決の追加（TRM-06〜17 取込みの続き。一度きり）。"""
import sys
sys.path.insert(0, "/Users/kako-jun/repos/2026/sit-by-me-wt-ledger-master/.claude/skills/sit-field-background/tools")
import ledger_io as L

D = L.read("決定")
readme = """- 石の敷居は通れる（bridge）。須弥壇の段は blocked（広間とは別、部屋にしない）。扉は本堂の壁（廊下の外端案は不採用）。assist は0。
- キャラの基準 `char_unit`（入力JSONに根拠付き）: 体内の1人幅77px（1920幅）→ 1672幅で67.1px、2人幅134.1px。各出口の中心でその room の行列の局所スケールにより平面長へ換算した。
- 出口は fixed: `door-west`・`door-east` は側壁の下寄り v=0.552〜0.968（中心 0.76）、`door-front`（台帳 ID は TRM-04.door-south）は南壁の中央 u=0.392〜0.608。
- 絵の修正候補: 西・東の敷居（広間と廊下の間に壁・柱・段があるが、設計では通れる）。"""
row = {c: "" for c in L.SCHEMA["決定"]}
row.update({
    "決定ID": "TRM-04.mask-confirmed", "日付": "2026-10-23", "対象種別": "MAP", "対象ID": "TRM-04", "対象名": "本堂のマスク・出口の確定",
    "決定の要点": "本堂 TRM-04 のマスク: 石の敷居は通れる（bridge）。須弥壇の段は blocked（広間とは別、部屋にしない）。扉は本堂の壁（廊下の外端案は不採用）。assist は0。"
                 "出口は door-west・door-east が側壁の下寄り（v=0.552〜0.968、中心 0.76）、正面（台帳 ID は TRM-04.door-south）が南壁の中央（u=0.392〜0.608）。"
                 "西・東の敷居は広間と廊下の間に壁・柱・段があるが、設計では通れる（絵の修正候補）。",
    "逐語": "（kako-jun の発言そのものは台帳に未転記。docs/production/oblique-masks/README.md「TRM-04（本堂）の確定（kako-jun 2026-10-23）」の記述を逐語で転記）\n" + readme,
    "出典": "docs/production/oblique-masks/README.md（kako-jun 2026-10-23 の確定の記録。発言の逐語は Issue #144 側で未確認）",
    "出典URL": "https://github.com/kako-jun/sit-by-me/blob/main/docs/production/oblique-masks/README.md",
    "状態": "有効", "プロンプト出力": "なし", "対象MAP": "TRM-04",
    "備考": "マスク・出口の設計値。プロンプトには入れない。char_unit の数値は採用画像 v11 からの算出値（旧方式の記録）。2026-10-23 の方針転換でモックが正本になったため、座標は plan を優先する",
})
D.append(row)
L.write("決定", D)

U = L.read("未決")
n = max(int(u["未決ID"].split("-")[1]) for u in U)
for u in U:
    if u["未決ID"] == "U-043":
        u["内容"] = ("勝手口の外側の戸口 TRM-06.door-house の意匠。幅は1人分（TRM-05.door-back と一致・決定済み）。位置・向き（住居の東面・中央 y520）は plan の既定（要確認）で、"
                   "TRM-05 の北壁左端とは画面の向きを一致させていない（円環 TRM-16→TRM-15→TRM-06→TRM-16 が非ユークリッドのため）")
def add(tb, tid, key, text):
    global n
    n += 1
    U.append({"未決ID": f"U-{n:03d}", "対象テーブル": tb, "対象ID": tid, "キー": key, "内容": text, "状態": "未決", "解決決定ID": ""})
add("MAP", "TRM-06", "宝箱枝", "宝箱枝は作らない既定（台帳 map-topology の『宝箱枝の扱いTBD』。主路を優先。TRM-06 の plan の既定）")
add("MAP", "TRM-13", "歩行マスク(3値)", "車椅子不可の石段（立位期のみ）の3値マスク（assist）はモック段階では出していない。plan の floors の look と assumptions に残してある")
add("MAP", "TRM-11", "歩行マスク(3値)", "TRM-11.right（立位期だけ通れる石段口）の3値マスク（assist）はモック段階では出していない")
add("MAP", "TRM-06", "屋外MAPの装飾", "屋外MAP（TRM-06〜11・13〜17）は plan に decor_pool が無い。装飾（木の本数・屋根・民家の見た目・路面）は全体レビュー承認後に採用済み画像と合わせて決める（装飾プールIDの未決と同件）")
L.write("未決", U)
