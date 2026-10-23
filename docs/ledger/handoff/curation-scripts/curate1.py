# -*- coding: utf-8 -*-
"""曲線1: エリア・語彙・必須キー・未決・キー別名・建物・MAP キー・決定（CSV を書く）"""
import json, sys, re
sys.path.insert(0, '/home/kako-jun/repos/2026/sit-by-me-wt-ledger-master/.claude/skills/sit-field-background/tools')
sys.path.insert(0, '/tmp/claude-1001/-home-kako-jun-repos-private-freeza/9f3f94f0-2c9d-45f2-a837-2e8539f6df7f/scratchpad/lm')
import ledger_io as L

UNDECIDED = "未決(要確認)"
NA = "該当なし"

# ---------------- エリア
areas = json.load(open(L.REPO + '/docs/topology/areas.json'))['areas']
ids = json.load(open(L.REPO + '/docs/topology/map-ids.json'))['areas']
rows = []
for a in areas:
    code = a['maps'][0].split('-')[0]
    r = {"エリアID": a['id'], "区域コード": code, "名称": a['name'], "目標枚数": ids[code],
         "台帳段階": "対象" if a['id'] == 'teramachi' else "対象外"}
    if a['id'] == 'teramachi':
        r.update({"机の天面の材質": "茶色の木の板張り(横目)", "台座の素材": "段ボール(波形断面)+綿の雪", "木の種類": "松+枯木",
                  "外周の装飾方針": "綿の雪・雪から覗く草・木で埋める(白い素地を残さない)",
                  "備考": "TRM-01 は 2026-10-23 に TRM-03 へ統合して廃止（欠番。IDは詰めない）。第1段階の対象（TRM-02〜17）"})
    else:
        r["備考"] = "第2段階以降（旧 md 台帳が併存。新規制作時に必須キーを埋める）"
    rows.append(r)
L.write("エリア", rows)

# ---------------- 語彙
V = []
def v(group, value, desc="", en=""):
    V.append({"語彙ID": f"V-{len(V)+1:03d}", "グループ": group, "値": value, "英語断片": en, "説明": desc})
for g, vals in {
    "屋内外": ["屋内", "屋外"],
    "MAP状態": ["モック承認済み", "未設計", "廃止"],
    "採用状態": ["未採用", "基準採用済み", "廃止(統合)", "没"],
    "描画方式": ["斜めモック", "未設計"],
    "依存の確度": ["確定", "導出", "要確認"],
    "表現する部位": ["内側", "外側", NA],
    "台帳段階": ["対象", "対象外"],
    "状態": ["確定", "既定(要確認)"],
    "壁側": ["北", "南", "東", "西"],
    "幅区分": ["2人分", "1.5人分", "1人分"],
    "窓種別": ["腰高", "掃き出し"],
    "要素種別": ["床", "壁", "家具", "経路", "樹木帯", "注記"],
    "端種別": ["戸口", "開口", "縁"],
    "時期差分有無": ["なし", "あり(→時期差分・建物時期差分)", UNDECIDED],
    "決定状態": ["有効", "訂正済み", "撤回"],
    "プロンプト出力": ["必須", "なし"],
    "部位種別": ["外形", "屋根", "壁", "窓列", "扉", "床", "柱"],
    "部位状態": ["閉", "開放", "なし"],
    "建物種別": ["棟", "渡り廊下棟"],
    "建物関係": ["渡り廊下で接続", "内包", "隣接"],
}.items():
    for x in vals:
        v(g, x)
for x, en in [("茶色の木の板張り(横目)", "warm brown wooden plank work desk top, grain running left-right"), ]:
    v("机の天面の材質", x, "", en)
v("机の天面の材質", UNDECIDED)
v("台座の素材", "段ボール(波形断面)+綿の雪", "", "corrugated cardboard slab edge with cotton snow top")
v("台座の素材", UNDECIDED)
v("木の種類", "松+枯木", "", "snow-laden Japanese pine and bare deciduous tree only")
v("木の種類", UNDECIDED)
v("外周の装飾方針", "綿の雪・雪から覗く草・木で埋める(白い素地を残さない)", "", "fill the area outside the building with cotton snow, grass and trees")
v("外周の装飾方針", UNDECIDED)
for x in ["板張り", "板張り(リノリウム可)", "板張り(ロールござ可)", "綿の雪の地面+石畳の参道", "黒紙・サンドペーパーの道(綿の雪)", UNDECIDED, NA]:
    v("床材", x)
for x in ["漆喰と木の柱・梁", "土塀", UNDECIDED, NA]:
    v("壁材", x)
for x in ["窓あり", "窓なし", UNDECIDED, NA]:
    v("窓", x)
for x in ["建物の扉に従う(→建物表)", UNDECIDED, NA]:
    v("扉の意匠", x)
for x in ["標準(段ボール・紙粘土・綿の雪・木)", UNDECIDED, NA]:
    v("工作の材質", x, "sit-diorama の共通規約（build_map_prompt.rb の固定文）" if x.startswith("標準") else "")
for x in ["なし", "あり(→時期差分・建物時期差分)", UNDECIDED, NA]:
    pass
for x in ["なし", NA]:
    v("依存MAP", x)
for x in ["装飾プール:teramachi-winter", "teramachi-winter", "teramachi-winter-exterior", UNDECIDED, NA]:
    v("装飾プールID", x)
for g, vals in {"禁止語": ["畳", "矢来", "アンモナイト", "クリスマスツリー", "池", "ガラスの中", "洋風の杉"]}.items():
    for x in vals:
        v(g, x)
L.write("語彙", V)

# ---------------- 建物
B = []
def bld(**k):
    B.append(k)
bld(建物ID="BLD-TRM-honden", 名称="本堂棟", エリアID="teramachi", 種別="棟", 外形="寺の中央の大きな棟（外観は参道の正面）",
    屋根="灰色の瓦の大きな寄棟（雪・堂々とした軒）", 外壁="クリーム色の漆喰と木の柱", 窓列="窓なし(確定)", 扉="正面に格子戸の大きな引き戸と石の踏み段（南壁中央）",
    材質="漆喰・木・瓦", 関係="→建物関係（渡り廊下棟で西の住居・東の幼稚園と接続）", 状態="有効",
    備考="内部は TRM-04（広間・須弥壇）。須弥壇・掛軸・装飾柱の作り込みは TRM-04 の要素表", **{L.FREE: ""})
bld(建物ID="BLD-TRM-jukyo", 名称="住居棟（庫裏）", エリアID="teramachi", 種別="棟", 外形="本堂の西（左）。本堂より低い棟",
    屋根="灰色の瓦の寄棟（雪）", 外壁="クリーム色の漆喰と木の柱", 窓列="南面に腰高窓2（扉・窓・窓の順）。北壁に腰高窓1（内部のみ）", 扉="南面左に焦げ茶の木の板戸（小窓つき。外への戸口）",
    材質="漆喰・木・瓦", 関係="→建物関係（西の渡り廊下棟で本堂と接続）", 状態="有効", 備考="内部は TRM-05", **{L.FREE: ""})
bld(建物ID="BLD-TRM-youchien", 名称="幼稚園棟（遊戯室）", エリアID="teramachi", 種別="棟", 外形="本堂の東（右）。住居より wider and deeper で屋根も大きい",
    屋根="灰色の瓦の寄棟（雪）", 外壁="クリーム色の漆喰と木の柱", 窓列="南面に掃き出し窓4（枚数は仮）", 扉="南面右端に木の戸（外への戸口）",
    材質="漆喰・木・瓦", 関係="→建物関係（東の渡り廊下棟で本堂と接続）", 状態="有効", 備考="内部は TRM-02", **{L.FREE: ""})
for side, name, ja in (("w", "西", "住居"), ("e", "東", "幼稚園")):
    bld(建物ID=f"BLD-TRM-corridor-{side}", 名称=f"{name}の渡り廊下棟（本堂-{ja}）", エリアID="teramachi", 種別="渡り廊下棟",
        外形="本堂と%sをつなぐ細長い棟。外端は閉じた壁" % ja, 屋根="灰色の瓦の低い寄棟（雪）", 外壁="クリーム色の漆喰の壁と木の柱（閉じた壁）",
        窓列="南壁に腰高の連窓3つ", 扉="本堂側の開口は戸のない通り抜け（梁・鴨居なし）", 材質="漆喰・縦板の腰壁・木の板張りの床", 関係="→建物関係", 状態="有効",
        備考="屋内（TRM-04）と外観（TRM-03）は同じ行・同じ部位から導出する（TRM.building-shared）", **{L.FREE: ""})
L.write("建物", B)

P = []
def part(pid, bid, kind, side, state, mat, look, ref="", free=""):
    P.append({"部位ID": pid, "建物ID": bid, "部位種別": kind, "方角": side, "状態": state, "材質": mat, "見た目": look, "決定参照": ref, L.FREE: free})
for s, name in (("w", "西"), ("e", "東")):
    b = f"BLD-TRM-corridor-{s}"
    part(f"{b}.roof", b, "屋根", "", "閉", "灰色の瓦・綿の雪", "灰色の瓦（波形）の低い寄棟屋根に綿の雪（外観からだけ見える。屋内は描かない）", "TRM.building-shared")
    part(f"{b}.south-wall", b, "壁", "南", "閉", "漆喰・縦板の腰壁", "窓の下は縦板の腰壁、漆喰の壁。窓は細い木の桟の腰高ガラス窓（外景は描かない）。", "TRM.building-shared;TRM.window-glass")
    part(f"{b}.south-windows", b, "窓列", "南", "閉", "木の桟のガラス窓", "腰高の連窓3つ（等間隔）", "TRM.building-shared")
    part(f"{b}.end-wall", b, "壁", "西" if s == "w" else "東", "閉", "漆喰・木の柱", "外端は閉じた壁（開口にしない）", "TRM.building-shared")
    part(f"{b}.floor", b, "床", "", "閉", "濃い茶色の木の板張り", "濃い茶色の木の板張り（横板・継ぎ目・節）", "TRM-03.corridor")
part("BLD-TRM-corridor-w.north-wall", "BLD-TRM-corridor-w", "壁", "北", "閉", "漆喰", "芳名板（細い縦長の白木の札を横一列に並べる。札に文字は書かない・無地の木札）。", "")
part("BLD-TRM-corridor-e.north-wall", "BLD-TRM-corridor-e", "壁", "北", "閉", "漆喰", "子どもの絵（3枚: 花・人物・虹の色鉛筆画をマスキングテープで貼る）。文字は入れない。", "TRM-04.east-corridor-art")
part("BLD-TRM-corridor-w.hall-opening", "BLD-TRM-corridor-w", "扉", "東", "開放", "なし", "本堂広間との境は戸のない通り抜けの開口（梁・鴨居・垂れ壁・壁を描かない）", "TRM.open-passage")
part("BLD-TRM-corridor-e.hall-opening", "BLD-TRM-corridor-e", "扉", "西", "開放", "なし", "本堂広間との境は戸のない通り抜けの開口（梁・鴨居・垂れ壁・壁を描かない）", "TRM.open-passage")
part("BLD-TRM-honden.south-door", "BLD-TRM-honden", "扉", "南", "閉", "木・格子", "南壁の中央は格子戸の引き戸（上半分が細かい格子、下半分が縦板）。戸の前に石の踏み段。", "")
part("BLD-TRM-honden.windows", "BLD-TRM-honden", "窓列", "", "なし", "", "窓は置かない（窓の数0）", "TRM.hall-no-window")
part("BLD-TRM-jukyo.south-door", "BLD-TRM-jukyo", "扉", "南", "閉", "木", "焦げ茶の木の板戸（小窓つき）。幅は1.5人分", "TRM.door-width-outside")
part("BLD-TRM-jukyo.south-windows", "BLD-TRM-jukyo", "窓列", "南", "閉", "木の桟のガラス窓", "南面は腰高窓のみ（扉・窓・窓の順）", "TRM.windows-spec")
part("BLD-TRM-youchien.south-door", "BLD-TRM-youchien", "扉", "南", "閉", "木", "木の戸（1.5人幅）。掃き出し窓とは別に玄関の扉を1つ", "TRM.door-width-outside")
part("BLD-TRM-youchien.south-windows", "BLD-TRM-youchien", "窓列", "南", "閉", "木の桟のガラス窓", "南面は床まで届く引き違いの掃き出し窓（扉ではない）", "TRM-03.kindergarten-bigger")
L.write("建物部位", P)

W = []
def wl(wid, bid, part_, n, a, b_, c, d_, e, kind, why, ref=""):
    W.append({"窓列ID": wid, "建物ID": bid, "部位ID": part_, "個数": n, "先頭比": a, "間隔比": b_, "幅比": c, "窓台比": d_, "高さ比": e, "窓種別": kind, "理由": why, "決定参照": ref, L.FREE: ""})
for s in ("w", "e"):
    wl(f"BLD-TRM-corridor-{s}.south-wins", f"BLD-TRM-corridor-{s}", f"BLD-TRM-corridor-{s}.south-windows", 3, "0.165289" if s == "w" else "0.236915", "0.303030", "0.192837", "0.181818", "0.454545", "腰高", "廊下棟の南壁の連窓（屋内・外観で共通。東は西より先頭が26単位右）", "TRM.building-shared")
wl("BLD-TRM-honden.windows", "BLD-TRM-honden", "BLD-TRM-honden.windows", 0, "", "", "", "", "", "", "窓なし（確定）", "TRM.hall-no-window")
wl("BLD-TRM-jukyo.south-wins", "BLD-TRM-jukyo", "BLD-TRM-jukyo.south-windows", 2, "", "", "", "", "", "腰高", "南面の腰高窓2（扉・窓・窓の順）", "TRM.windows-spec")
wl("BLD-TRM-youchien.south-wins", "BLD-TRM-youchien", "BLD-TRM-youchien.south-windows", 4, "", "", "", "", "", "掃き出し", "南面の掃き出し窓4（枚数は仮）", "TRM-03.kindergarten-bigger")
L.write("建物窓列", W)

R = [
 {"通番": 1, "建物A": "BLD-TRM-honden", "建物B": "BLD-TRM-corridor-w", "関係": "渡り廊下で接続", "方角": "西", "接続端ID": "TRM-04.door-west", "決定参照": "TRM.left-right"},
 {"通番": 2, "建物A": "BLD-TRM-corridor-w", "建物B": "BLD-TRM-jukyo", "関係": "渡り廊下で接続", "方角": "西", "接続端ID": "TRM-05.door-hall", "決定参照": "TRM.left-right"},
 {"通番": 3, "建物A": "BLD-TRM-honden", "建物B": "BLD-TRM-corridor-e", "関係": "渡り廊下で接続", "方角": "東", "接続端ID": "TRM-04.door-east", "決定参照": "TRM.left-right"},
 {"通番": 4, "建物A": "BLD-TRM-corridor-e", "建物B": "BLD-TRM-youchien", "関係": "渡り廊下で接続", "方角": "東", "接続端ID": "TRM-02.door-west", "決定参照": "TRM.left-right"},
]
for r in R:
    r[L.FREE] = ""
L.write("建物関係", R)
BT = [
 {"建物ID": "BLD-TRM-jukyo", "時期": "kids", "部位ID": "", "差分": "置換", "内容": "寝室は父と同じ1つ（仕切りの下半分を取る）。外観は基準と同じ", "決定参照": "TRM-05.bedrooms"},
 {"建物ID": "BLD-TRM-jukyo", "時期": "fire", "部位ID": "", "差分": "焼失", "内容": "火事の時点: 上半分（北側）だけが燃える。勝手口は焼失。外観は基準", "決定参照": "TRM-05.fire;TRM-05-fire.upper-half"},
 {"建物ID": "BLD-TRM-jukyo", "時期": "burnt", "部位ID": "", "差分": "焼失", "内容": "火事後: 住居棟だけ全焼（父の寝室が最も軽い）。本堂・幼稚園は無傷。未作成（設計が曖昧なため発明しない）", "決定参照": "TRM-05.fire"},
 {"建物ID": "BLD-TRM-honden", "時期": "wc", "部位ID": "BLD-TRM-honden.south-door", "差分": "追加", "内容": "車椅子期: 本堂前の石段にスロープを付ける（外観の別画像。同一IDで差し替え。未作成）", "決定参照": "TRM-03.standing"},
]
for r in BT:
    r[L.FREE] = ""
L.write("建物時期差分", BT)
