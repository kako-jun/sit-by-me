# -*- coding: utf-8 -*-
"""曲線5: 必須キー・未決・キー別名・採用要素・素材"""
import json, sys, os, glob
sys.path.insert(0, '<repo>/.claude/skills/sit-field-background/tools')
import ledger_io as L
S = '<scratchpad>/lm/'
rows = []
def rk(t, k, lv, cond="", grp="", desc=""):
    rows.append({"対象テーブル": t, "キー": k, "必須度": lv, "条件": cond, "語彙グループ": grp, "説明": desc})
for k, g, d in (("机の天面の材質", "机の天面の材質", "作業机（最外層）の天面。エリア内の全MAPで同じ"), ("台座の素材", "台座の素材", "台座の素材と前縁の見た目"),
                ("木の種類", "木の種類", "建物の外側に植える木の種類（エリア固定）"), ("外周の装飾方針", "外周の装飾方針", "建物の外側の面の埋め方")):
    rk("エリア", k, "条件付き必須", "台帳段階=対象", g, d)
rk("エリア", "名称", "必須"); rk("エリア", "区域コード", "必須")
for k, g in (("屋内外", "屋内外"), ("状態", "MAP状態"), ("描画方式", "描画方式")):
    rk("MAP", k, "必須", "", g)
rk("MAP", "エリアID", "必須", "", "", "エリア表への外部キー")
for k, g, d in (("床材", "床材", "屋内=床、屋外=地面の材質"), ("壁材", "壁材", "壁・塀の材質。無ければ『該当なし』と明示する"), ("窓", "窓", "個数・位置・種別は窓表。無い場合は『窓なし』を明示する（本堂のように）"),
                ("扉の意匠", "扉の意匠", "扉のデザイン（建物がある場合は建物表の扉に従う）"), ("工作の材質", "工作の材質", "家具・小物の素材（ジオラマ共通規約）"),
                ("時期差分", "時期差分有無", "時期別の差し替えの有無。あるなら時期差分表か建物時期差分表に行がある"), ("採用状態", "採用状態", "画像の採用状態"),
                ("装飾プールID", "装飾プールID", "装飾プール表のID（未設計は未決を明示）"), ("依存MAP", "依存MAP", "参考画像として渡す確定済みMAP。独立なら『なし』")):
    rk("MAP", k, "条件付き必須", "状態!=廃止", g, d)
rk("MAP", "建物ID", "条件付き必須", "描画方式=斜めモック", "", "屋内MAPが属する棟／外観MAPが描く棟（;区切り）")
rk("MAP", "表現する部位", "条件付き必須", "描画方式=斜めモック", "表現する部位", "屋内=内側／外観=外側")
rk("MAP", "@接続", "条件付き必須", "状態!=廃止", "", "接続表に1行以上（出入口と相手）")
rk("MAP", "@窓の整合", "条件付き必須", "描画方式=斜めモック", "", "窓=窓あり→窓表に窓の行／窓なし→窓の行なし（窓なし行は可）")
rk("MAP", "@時期差分の整合", "条件付き必須", "状態!=廃止", "", "時期差分=あり→時期差分表か建物時期差分表に行／なし→行なし")
for k in ("外形", "屋根", "外壁", "窓列", "扉", "材質", "関係"):
    rk("建物", k, "必須", "", "", "建物単位の必須キー")
rk("端", "幅クラス", "条件付き必須", "種別=戸口", "幅区分", "出入口の幅区分")
rk("端", "壁側", "条件付き必須", "種別!=縁", "壁側")
rk("端", "相手端", "条件付き必須", "種別!=開口", "", "接続の相手")
for k in ("決定ID", "日付", "対象種別", "対象ID", "決定の要点", "逐語", "出典", "状態", "プロンプト出力", "対象MAP"):
    rk("決定", k, "必須", "", {"状態": "決定状態", "プロンプト出力": "プロンプト出力"}.get(k, ""))
rk("決定", "@語句", "条件付き必須", "プロンプト出力=必須", "", "必須語または禁止語のどちらか")
rk("決定", "出典URL", "条件付き必須", "出典!=会話（Issue #144 に記録）", "", "Issue コメントのURL")
for k in ("元MAP", "要素", "内容", "継承先MAP", "継承方法", "状態"):
    rk("採用要素", k, "必須")
for k in ("素材ID", "所有者ID", "種別", "状態", "来歴"):
    rk("素材", k, "必須")
for k in ("生成物ID", "種別", "パス", "元の表", "再生成コマンド"):
    rk("生成物", k, "必須")
L.write("必須キー", rows)
print(len(rows), "required keys")

# ---- キー別名
al = [("床材", "床の材質", "MAP", ""), ("床材", "floor_material", "MAP", ""), ("床材", "床の素材", "MAP", ""), ("壁材", "壁の材質", "MAP", ""), ("壁材", "wall_material", "MAP", ""),
      ("机の天面の材質", "机の材質", "エリア", ""), ("机の天面の材質", "desk_material", "エリア", ""), ("台座の素材", "台座の材質", "エリア", ""), ("台座の素材", "slab_material", "エリア", ""),
      ("木の種類", "樹種", "エリア", ""), ("木の種類", "trees", "エリア", ""), ("工作の材質", "工作の素材", "MAP", ""), ("扉の意匠", "扉のデザイン", "MAP", ""), ("扉の意匠", "door_design", "MAP", ""),
      ("窓", "窓の有無", "MAP", ""), ("幅クラス", "幅区分", "端", "語彙グループ名と端表の列名は別（列=幅クラス、語彙=幅区分）"), ("依存MAP", "depends_on", "MAP", ""),
      ("時期差分", "時期の差分", "MAP", ""), ("外周の装飾方針", "外周の装飾", "エリア", ""), ("特徴(自由記述)", "備考の特徴", "全表", "")]
L.write("キー別名", [{"正規名": a, "別名": b, "対象テーブル": c, "説明": d} for a, b, c, d in al])

# ---- 未決
un = json.load(open(S + 'unresolved.json'))
U = []
for t, i, k, c in un:
    U.append({"対象テーブル": t, "対象ID": i, "キー": k, "内容": c or "決まっていない（旧 md 台帳・Issue に決定が無い。発明しない）", "状態": "未決", "解決決定ID": ""})
extra = [
 ("建物窓列", "BLD-TRM-youchien.south-wins", "個数", "掃き出し窓の枚数4は仮（#51。kako-jun 決定は『4枚は仮』のまま）"),
 ("建物時期差分", "BLD-TRM-jukyo.burnt", "差分", "火事後（-burnt）の設計が曖昧（焼ける線・南側の被害の程度）。未作成"),
 ("建物時期差分", "BLD-TRM-honden.wc", "差分", "車椅子期（TRM-03-wc）の差し替えの時点・方式（#51 の未決）"),
 ("要素", "TRM-04.dais", "見た目", "本尊の姿は立像が既定（kako-jun 要確認）。余間の掛軸は観光寺院由来かもしれない（要確認）"),
 ("端", "TRM-06.door-house", "扉の意匠", "勝手口の外側の戸口（TRM-06 側）の幅・意匠。TRM-05.door-back（1人分）と一致させる想定だが TRM-06 の設計が別ブランチ"),
 ("MAP", "TRM-09", "時期差分", "時期差は営業灯だけ（specifications の記述）。差分の表現が未設計"),
 ("MAP", "TRM-13", "時期差分", "事故後は入口を閉鎖（specifications の記述）。差分の表現が未設計"),
]
for t, i, k, c in extra:
    U.append({"対象テーブル": t, "対象ID": i, "キー": k, "内容": c, "状態": "未決", "解決決定ID": ""})
for n, r in enumerate(U, 1):
    r["未決ID"] = f"U-{n:03d}"
L.write("未決", U)
print(len(U), "unresolved rows")

# ---- 素材
def fsha(p):
    return L.sha_file(L.REPO + "/" + p) if os.path.exists(L.REPO + "/" + p) else ""
M = []
def mat(oid, kind, path, status, date, origin):
    M.append({"素材ID": f"A-{len(M)+1:03d}", "所有者ID": oid, "種別": kind, "パス": path, "状態": status, "日付": date, "来歴": origin, "sha256": fsha(path) if path else "", L.FREE: ""})
mat("TRM-04", "背景(基準)", "assets/images/fields/reference/teramachi-main-hall-interior-trm04-adopted.webp", "採用", "2026-10-23", "e2 の take4 を採用（kako-jun「04は４枚目」）。docs/production/20261023-trm04-adoption.md")
for f in sorted(glob.glob(L.REPO + "/assets/images/fields/masks/TRM-0*")):
    p = os.path.relpath(f, L.REPO)
    base = os.path.basename(p)
    own = "TRM-" + base.split("-")[1]
    if "TRM-04" in base:
        mat(own, "マスク", p, "採用", "2026-10-23", "モック（平面図）から作成。red-team 未")
    else:
        mat(own, "マスク", p, "参照専用", "", "旧採用画像（v3/v7/v12）由来の旧マスク。モックから作り直す対象（決定 TRM.mock-master）")
for f in sorted(glob.glob(L.REPO + "/assets/images/fields/legacy/TRM-*.webp")):
    p = os.path.relpath(f, L.REPO)
    mat(os.path.basename(p).split(".")[0].rsplit("-pre", 1)[0], "背景(旧)", p, "参照専用", "", "旧 legacy 画像。採用根拠にならない（旧legacyは一枚も採用しない）")
mat("TRM-04", "背景(没)", "", "没", "2026-10-23", "e2 の take1〜3・retry1。削除済み（決定 TRM.serial-order）")
mat("TRM-02", "背景(没)", "", "没", "2026-10-23", "e2 round1〜3。削除済み（依存順を無視した並列生成のため）")
mat("TRM-03", "背景(没)", "", "没", "2026-10-23", "e2 の4テイク。削除済み（内部が確定していない段階での生成のため）")
mat("TRM-05", "背景(没)", "", "没", "2026-10-23", "基準・-kids・-fire の e2 生成物。削除済み。-fire は4テイク中3枚が『上半分だけが燃える』を守らず没（決定 TRM-05-fire.upper-half）")
mat("TRM-01", "背景(旧)", "", "没", "2026-10-23", "legacy/TRM-01.webp とマスク3枚。TRM-01 廃止に伴い削除（決定 TRM-08.top-closed）。履歴は git")
L.write("素材", M)
ids = {r["所有者ID"]: r["素材ID"] for r in M if r["状態"] == "採用" and r["種別"] == "背景(基準)"}
A = []
def ad(eid, src, mapid, elem, content, to, how, state, word, ref):
    A.append({"採用要素ID": eid, "素材ID": src, "元MAP": mapid, "要素": elem, "内容": content, "継承先MAP": to, "継承方法": how, "状態": state, "確認語": word, "決定参照": ref, L.FREE: ""})
t4 = ids["TRM-04"]
ad("TRM-04.door-design", t4, "TRM-04", "正面扉の意匠", "格子戸の引き戸（上半分が細かい格子・下半分が縦板・木枠）と石の踏み段。扉のデザインの正本。他の建物の扉もこの意匠に揃える", "TRM-02;TRM-03;TRM-05", "参考画像+プロンプト", "有効", "格子戸", "TRM.serial-order")
ad("TRM-04.wall-material", t4, "TRM-04", "壁の材質", "クリーム色の漆喰（紙粘土のざらつき）・濃い茶の木の柱と笠木・角の金属の角飾り", "TRM-02;TRM-03;TRM-05", "参考画像+プロンプト", "有効", "角飾り", "TRM.serial-order")
ad("TRM-04.floor-planks", t4, "TRM-04", "床の板張り", "濃い茶色の木の板張り（横板・継ぎ目・使い込んだ艶）", "TRM-02;TRM-05", "参考画像+プロンプト", "有効", "使い込んだ艶", "TRM.serial-order")
ad("TRM-04.corridor-windows", t4, "TRM-04", "廊下の南壁の連窓", "細い木の桟の腰高ガラス窓が3つ並ぶ（窓の下は縦板の腰壁）。外観の廊下棟も同じ", "TRM-03", "参考画像+プロンプト", "有効", "連窓", "TRM.building-shared")
ad("TRM-04.outer-trees", t4, "TRM-04", "建物の外の木", "雪をかぶった松（岩と苔つき）と枯木が台座の四辺に散る（松多め）", "TRM-02;TRM-03;TRM-05", "参考画像+プロンプト", "有効", "松", "TRM.trees-pine")
ad("TRM-05.mikan", "", "TRM-05", "食卓の上のみかん", "食卓（机）の上にみかんを置く。没になった4テイクの中で kako-jun が『よかった』と評した点", "TRM-05;TRM-05-kids;TRM-05-fire", "プロンプト（採用画像の確定後は参考画像も）", "記録（採用画像の確定後に素材IDを紐付ける）", "みかん", "TRM-05-fire.upper-half")
L.write("採用要素", A)
print(len(M), "materials", len(A), "inherit")
