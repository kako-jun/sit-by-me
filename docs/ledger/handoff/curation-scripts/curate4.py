# -*- coding: utf-8 -*-
"""曲線4: 意図的な修正（畳・化石の石・勝手口・渡り廊下棟）と決定参照への置換。JSON の決定文の写しを台帳参照へ。"""
import json, sys, re
sys.path.insert(0, '/home/kako-jun/repos/2026/sit-by-me-wt-ledger-master/.claude/skills/sit-field-background/tools')
import ledger_io as L

def rep(rows, pred, **upd):
    n = 0
    for r in rows:
        if pred(r):
            r.update(upd); n += 1
    assert n, upd
    return n

# ---- 要素
E = L.read("要素")
for r in E:
    if r["MAP_ID"] == "TRM-05" and r["要素ID"] in ("futon-n", "futon-s"):
        r["見た目"] = r["見た目"].replace("（畳は描かない）。", "。"); r["決定参照"] = "TRM.no-tatami"
rep(E, lambda r: r["MAP_ID"] == "TRM-05" and r["要素ID"] == "rock", 見た目="", 決定参照="TRM-05.fossil;TRM-05.stone-pos")
for r in E:
    if r["MAP_ID"] == "TRM-04" and r["要素ID"] == "dais":
        r["見た目"] = r["見た目"].replace("仏壇の前に柵（矢来）・注意書き・名簿を置かない（個人の寺にはない。#51）。", "").rstrip(); r["決定参照"] = "TRM-04.no-fence"
for r in E:
    if r["適用時期"] == "fire" and r["要素ID"] == "burnt-back-door-embers":
        a = json.loads(r["属性JSON"]); a["prompt"] = "北壁の左端の勝手口は焼け落ちて通れない。この位置（箱のまま）に燃えカス（黒く焦げた木片・灰）が残る"
        r["属性JSON"] = L.jdump(a); r["決定参照"] = "TRM-05.door-back-fire"
    if r["適用時期"] == "fire" and r["要素ID"] == "burnt-back-door-flame":
        r["決定参照"] = "TRM-05.door-back-fire"
    if r["適用時期"] == "fire" and r["要素ID"] == "fire-zone":
        r["決定参照"] = "TRM-05-fire.upper-half"
# TRM-04 廊下・本堂の壁・扉: 建物部位から導出
PART = {("TRM-04", "corr-w-s"): ("西廊下の南壁", "BLD-TRM-corridor-w.south-wall"), ("TRM-04", "corr-e-s"): ("東廊下の南壁", "BLD-TRM-corridor-e.south-wall"),
        ("TRM-04", "corr-w-n"): ("西廊下の北壁", "BLD-TRM-corridor-w.north-wall"), ("TRM-04", "corr-e-n"): ("東廊下の北壁", "BLD-TRM-corridor-e.north-wall")}
for r in E:
    k = (r["MAP_ID"], r["要素ID"])
    if k in PART and r["適用時期"] == "":
        lab, pid = PART[k]
        r["見た目"] = f"{lab}: {{部位:{pid}}}"; r["建物部位ID"] = pid; r["決定参照"] = "TRM.building-shared"
    if k == ("TRM-04", "hall-s"):
        r["見た目"] = "{部位:BLD-TRM-honden.south-door}"; r["建物部位ID"] = "BLD-TRM-honden.south-door"
# TRM-03 渡り廊下棟: roof-passage を取り消し、屋内の確定画像と同じ建物行から導出（閉じた壁・連窓・板張り・低い瓦屋根）
for r in E:
    if r["MAP_ID"] == "TRM-03" and r["要素ID"] in ("conn-w", "conn-e"):
        a = json.loads(r["属性JSON"])
        for k in ("floor", "floor_status"):
            a.pop(k, None)
        a["kind"] = "building"; a["window_count"] = 3
        r["属性JSON"] = L.jdump(a)
        s = r["要素ID"][-1]; side = "西" if s == "w" else "東"; ja = "住居" if s == "w" else "幼稚園"; b = f"BLD-TRM-corridor-{s}"
        r["名称"] = "渡り廊下棟"
        r["見た目"] = f"渡り廊下棟（{side}。本堂と{ja}をつなぐ）: {{部位:{b}.roof}}。南面: {{部位:{b}.south-wall}}（腰高の連窓3つ）。外端は閉じた壁。床は木の板張り。"
        r["建物部位ID"] = f"{b}.south-wall"; r["決定参照"] = "TRM.building-shared;TRM-03.corridor"
L.write("要素", E)

# ---- 端
X = L.read("端")
NOTE = {
 "TRM-05.door-outside": ("外へ。下辺の中央より左寄り（ダイニング側）。幅100単位（1.5人分。接続の両側で一致）", "TRM.entrances;TRM.door-width-outside"),
 "TRM-05.door-back": ("勝手口（裏口）。北壁の左端（x420〜486）。台所の並びは戸口の右隣に続く。戸口の前（室内側）は家具で塞がない", "TRM-05.door-back"),
 "TRM-02.door-outside": ("外へ。下辺の右端付近。扉前は空ける。幅100単位（1.5人分。接続の両側で一致）", "TRM.entrances;TRM.door-width-outside"),
 "TRM-03.door-residence": ("住居の外への戸口。建物幅の0.29（内部の戸口と揃える）。幅100単位（1.5人分。接続の両側で一致）。境内側の位置は既定（要確認）", "TRM.entrances;TRM.door-width-outside"),
 "TRM-03.door-playroom": ("幼稚園の外への戸口。建物幅の0.84（内部の戸口と揃える）。幅100単位（1.5人分。接続の両側で一致）。境内側の位置は既定（要確認）", "TRM.entrances;TRM.door-width-outside"),
 "TRM-05.door-hall": ("本堂から入る。東壁・下寄り（v=0.76）。南寝室に入る形（要確認）", "TRM.entrances"),
 "TRM-02.door-west": ("本堂へ。西壁・上下の中央より下寄り（v=0.76）", "TRM.entrances"),
}
for r in X:
    if r["端ID"] in NOTE and r["適用時期"] == "":
        r["備考"], r["決定参照"] = NOTE[r["端ID"]]
    if r["端ID"] in ("TRM-04.door-west", "TRM-04.door-east"):
        r["決定参照"] = "TRM.open-passage"
    if r["端ID"] in ("open-dining-bed-n", "open-dining-bed-s"):
        r["決定参照"] = "TRM-05.partition-openings"
L.write("端", X)

# ---- 窓
Wn = L.read("窓")
for r in Wn:
    i = r["窓ID"]
    if i.startswith("TRM-04.win-c"):
        s = i[-2]; r["建物窓列ID"] = f"BLD-TRM-corridor-{s}.south-wins"; r["連番"] = i[-1]
        for k in ("中心", "幅", "種別", "窓台", "高さ"):
            r[k] = ""
        r["備考"] = ("西" if s == "w" else "東") + "廊下の南壁の連窓（腰高）。外は見えない。屋内と外観で同じ窓列（建物窓列から導出）"
        r["状態"] = "確定"; r["決定参照"] = "TRM.building-shared"
    elif i.startswith("TRM-05.win-s"):
        r["備考"] = "南面の腰高窓（扉・窓・窓の順）。個数2は採用外観v7。位置は既定（要確認）"; r["決定参照"] = "TRM.windows-spec"; r["建物窓列ID"] = "BLD-TRM-jukyo.south-wins"
    elif i == "TRM-05.win-n1":
        r["備考"] = "北壁の腰高窓1つ（石のすぐ左の壁）。種別・寸法は既定（要確認。掃き出しにしない）。石は北東の隅"; r["決定参照"] = "TRM-05.stone-pos"
    elif i.startswith("TRM-02.win-s"):
        r["備考"] = "南面の掃き出し窓（床まで届く引き違い・扉ではない）。枚数4は仮。位置は採用v3の窓の帯に合わせた既定（要確認）。窓から見えるのは室内の床で外の景色ではない"
        r["決定参照"] = "TRM-03.kindergarten-bigger;TRM.windows-spec;TRM.window-glass"; r["建物窓列ID"] = "BLD-TRM-youchien.south-wins"
    elif i.startswith("TRM-03.win-res"):
        r["備考"] = "住居棟の南面の腰高窓（扉・窓・窓の順）。個数2は採用外観v7。位置は既定（要確認）"; r["決定参照"] = "TRM.windows-spec"; r["建物窓列ID"] = "BLD-TRM-jukyo.south-wins"
    elif i.startswith("TRM-03.win-kg"):
        r["備考"] = "幼稚園棟の南面の掃き出し窓（床まで届く引き違い・扉ではない。玄関扉 door-playroom とは別）。枚数4は仮。位置は既定（要確認）"
        r["決定参照"] = "TRM-03.kindergarten-bigger"; r["建物窓列ID"] = "BLD-TRM-youchien.south-wins"
    elif ".nowin." in i:
        r["備考"] = "本堂に窓は置かない"; r["決定参照"] = "TRM.hall-no-window"
# TRM-03 の廊下棟の連窓（屋内の廊下と同じ建物窓列）
for s, lo, hi in (("w", 379, 596), ("e", 959, 1142)):
    for n in (1, 2, 3):
        Wn.insert([k for k, x in enumerate(Wn) if x["MAP_ID"] == "TRM-03" and x["適用時期"] == "" and ".win-kg" in x["窓ID"]][-1] + 1 if False else len([x for x in Wn if x["MAP_ID"] != "TRM-05" or True]) , {
            "窓ID": f"TRM-03.win-c{s}{n}", "MAP_ID": "TRM-03", "適用時期": "", "壁": f"conn-{s}", "壁側": "南", "状態": "確定", "沿い範囲": json.dumps([lo, hi]),
            "建物窓列ID": f"BLD-TRM-corridor-{s}.south-wins", "連番": str(n), "種別": "", "備考": ("西" if s == "w" else "東") + "の渡り廊下棟の南壁の連窓（腰高）。屋内（TRM-04）の廊下と同じ窓列（建物窓列から導出）",
            "決定参照": "TRM.building-shared", "属性JSON": "", L.FREE: ""})
# 窓なし行の並びを保つため MAP ごとにまとめ直す（同一MAP内の相対順は維持）
order = []
for r in Wn:
    if r["MAP_ID"] not in order:
        order.append(r["MAP_ID"])
Wn = [r for m in order for r in Wn if r["MAP_ID"] == m]
L.write("窓", Wn)

# ---- 既定値
A = L.read("既定値")
byid = {r["既定ID"]: r for r in A}
def setA(i, text, ref=""):
    byid[i]["内容"] = text; byid[i]["決定参照"] = ref
def show(mid):
    return [(r["既定ID"], r["内容"][:70]) for r in A if r["MAP_ID"] == mid]
setA("TRM-05.a02", "本堂からの戸口（東壁・v=0.76）は南寝室の側に着く。採用画像の石の敷居は東壁の中ほど（v≈0.5）にあったが、戸口は上下の中央より下寄り。", "TRM.entrances")
setA("TRM-05.a04", "勝手口 door-back は北壁（画面上辺）の左（西）端（x420〜486・幅66）。台所の並び（コンロ・流し・食器棚・冷蔵庫）は戸口の右端（x486）から仕切り（x785）まで隙間なく並べる（幅: コンロ80・流し96・食器棚70・冷蔵庫53。基準寸法75/90/65/50を比例配分。寸法は既定・要確認）。西の棚（Y492〜735）・食卓は元の位置。相手は TRM-06.door-house（寺町内・未制作MAP）。", "TRM-05.door-back;TRM-05.kitchen")
setA("TRM-05.a05", "石は北東の隅（北壁と東壁の内側の角。x1125〜1170・Y280〜350）に置く。石のすぐ左の北壁に腰高窓1つ（中心x1070・幅80・窓台50・高さ55）。窓の種別・寸法は既定（要確認）。箪笥・台所・勝手口とは重ならない。", "TRM-05.stone-pos")
setA("TRM-05.a06", "南寝室の布団は北の仕切り・西の仕切りの角に寄せた: [821,680,1015,858]→[809,615,1003,775]（壁に隙間なし。奥行き178→160に詰めた。door-hall から南の開口の通路（Y775〜907）を空けるため。寸法は既定・要確認）。長持も通路にかかっていたため北へ60（Y640〜734）。通路は paths で検証（幅2人分・踏ませない床と家具の上を通らない）。", "TRM-05.futon-chest")
setA("TRM-05.a07", "長持を東壁・水平な仕切りの角に隙間なく付けた: [1000,640,1066,734]→[1104,615,1170,709]（南寝室の東壁沿い・水平な仕切りの直下）。石・北壁の窓・door-hall・南の開口への通路（2人幅）とは干渉しない。壁際に寄せられる他の家具（棚・箪笥・台所）は元から壁に接しており、食卓・長椅子は台所の中央で自然。", "TRM-05.futon-chest")
A = [r for r in A if r["既定ID"] not in ("TRM-05.a08", "TRM-05.a09")]; byid = {r["既定ID"]: r for r in A}
setA("TRM-05.a10", "住居・幼稚園の外への戸口（TRM-03.door-residence/door-playroom、TRM-05.door-outside、TRM-02.door-outside）の幅は100単位（1.5人分）。高さは2人分のまま。扉の左右の壁が増えたが、窓・家具との重なりは無い（検証済み）。", "TRM.door-width-outside")
setA("TRM-05.kids.a01", "仕切りの下半分を取り、寝室を1室にした。開口は南側の1か所のみ（既定・要確認）。寝室内の家具の再配置は仮。", "TRM-05.bedrooms")
setA("TRM-05.fire.a01", "火の範囲 Y280〜640（上半分。既定・要確認）。燃えた所は blocked。", "TRM-05.fire;TRM-05-fire.upper-half")
setA("TRM-05.fire.a02", "-burnt は未作成（設計が曖昧なため発明しない）。", "TRM-05.door-back-fire")
setA("TRM-05.fire.a03", "焼失した戸口: 同じ位置（北壁の左端 x420〜486）に火・燃えカスの blocked 箱を置いた。通常戸口ではなく、TRM-06 へは行けない。炎・燃えカスの箱の大きさは既定（要確認）。", "TRM-05.door-back-fire")
setA("TRM-02.a04", "外への戸口（TRM-02.door-outside）の幅は TRM-03.door-playroom と同じ100単位。扉の左右の壁が増えたが、窓・家具との重なりは無い（検証済み）。", "TRM.door-width-outside")
setA("TRM-03.a03", "境内側の戸口位置（住居・幼稚園）は既定を置いた（要確認）。園庭＝境内の右の区画（幼稚園の前）。東の通用門・TRM-01 への接続は無い。", "TRM-03.garden")
setA("TRM-03.a04", "園庭の遊具（滑り台1・ブランコ1・半円アーチ4=赤青黄青・動物型1）の位置と大きさは既定（要確認）。幼稚園の掃き出し窓の前（Y425〜600）と、参道・door-playroom 前の通路は空けた。歩行マスクでは遊具=blocked。", "TRM-03.garden-play")
setA("TRM-03.a05", "本堂の壁は window_count=0 で、窓は描かない。", "TRM.hall-no-window")
setA("TRM-03.a06", "渡り廊下棟（conn-w/conn-e）は屋内（TRM-04）の廊下と同じ建物行から導出する（閉じた壁・南壁に連窓3・木の板張りの床・低い瓦屋根）。屋根は箱の天面色で表し高さ70。柱・屋根の寸法は既定（要確認）。", "TRM.building-shared;TRM-03.corridor")
setA("TRM-03.a07", "住居・幼稚園の外への戸口（door-residence/door-playroom）の幅は100単位。内部側（TRM-05/TRM-02 の door-outside）も同幅。窓の位置は変えていない（重ならない）。", "TRM.door-width-outside")
setA("TRM-04.a04", "本堂の壁は window_count=0 で、窓は描かない。", "TRM.hall-no-window")
setA("TRM-04.a05", "本堂の広間⇄西廊下・東廊下の開口（door-west/east）は passage（梁・鴨居・垂れ壁・壁を描かない開放した通路）。", "TRM.open-passage")
L.write("既定値", A)

# ---- MAP の寸法根拠・自由記述
M = L.read("MAP")
for r in M:
    r["寸法根拠"] = re.sub(r"戸口の位置・幅は kako-jun 決定（#144）と台帳。", "戸口の位置・幅は台帳（決定 TRM.entrances ほか）。", r["寸法根拠"])
    r["寸法根拠"] = re.sub(r"戸口は kako-jun 決定（#144）。", "戸口は台帳（決定 TRM.entrances・TRM-05.door-back）。", r["寸法根拠"])
L.write("MAP", M)

# ---- 装飾プール / エリア固定
P = L.read("装飾プール")
def poolfix(pred, **u):
    n = 0
    for r in P:
        if pred(r): r.update(u); n += 1
    return n
n = 0
for r in P:
    v = r["値"]
    if r["項目"].startswith("forbid["):
        for key, ref in (("畳（い草の敷物", "TRM.no-tatami"), ("観光寺院風の柵", "TRM-04.no-fence"), ("窓ガラスの内側に雪", "TRM.window-glass"),
                         ("洋風の木（杉", "TRM.trees-pine"), ("作業机の天面の材質", "TRM.desk")):
            if v.startswith(key):
                r["値"] = ""; r["決定参照"] = ref; n += 1
    if r["項目"] == "surfaces.floor":
        r["値"] = v.replace("畳は描かない（#51）。", "")
        r["決定参照"] = "TRM.no-tatami"
    if r["項目"] == "kinds.stage":
        r["値"] = re.sub(r"和風の城・天守閣にしない（kako-jun 2026-10-23）。", "和風の城・天守閣にしない。", v); r["決定参照"] = "TRM-02.stage-castle"
    if r["項目"] == "kinds.statue":
        r["値"] = v.replace("（#51 2026-10-21）", ""); r["決定参照"] = "TRM-03.cemetery-statue"
    if r["プールID"] == "_doc" and r["項目"] == "note":
        r["値"] = v.replace("kako-jun 指摘（2026-10-23）で", "").replace("kako-jun と決めてから", "台帳（エリア表の必須キーと決定表）に決めてから")
print("pool forbid replaced", n)
L.write("装飾プール", P)
Fx = L.read("エリア固定")
for r in Fx:
    if r["項目"] == "status_note":
        r["値"] = "机の天面は採用済み4枚（幼稚園・本堂・住居・境内外観）に共通する見た目を既定として固定（要確認）。板目の向きは4枚中3枚が画面の左右方向（本堂は混在）の実測から『横』を既定にした。"
        r["決定参照"] = "TRM.desk"
    if r["項目"] == "trees.note":
        r["値"] = "寺町の木は松と枯木の2種に固定。本数と比率は既定（要確認）。"; r["決定参照"] = "TRM.trees-pine"
    if r["項目"] == "trees.forbid":
        r["値"] = ""; r["決定参照"] = "TRM.trees-pine"
L.write("エリア固定", Fx)
print("ok")
