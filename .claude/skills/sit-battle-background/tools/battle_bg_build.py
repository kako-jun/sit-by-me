"""戦闘背景（台帳 戦闘背景.yaml の1行）から、割付図(clean)・送信文・参照リストを機械生成し、生成後の安全矩形の重なりを検査する。

正本は台帳の『配置』列（JSON: 安全矩形・床の四隅・各物の位置）。送信文の文面は プロンプト文面.yaml の PR.battle.*（コードに文面を持たない）。
手で送信文を書かない・手で割付図を描かない（kako-jun 2026-11-12「画像作成はぜんぶスキル以外ではするな。再現性がなくなる」）。

使い方（リポ root から）:
  uv run --with pillow --with numpy python3 -I .claude/skills/sit-battle-background/tools/battle_bg_build.py build BG011 --stage-ref STAGE.png --out DIR
      生成前の検査（物が安全矩形に重ならないか・床の奥の縁が右上がりか）。通れば DIR/layout.png・DIR/send.txt・DIR/refs.txt を出す。重なれば停止。
  ... check BG011 IMAGE.png --out DIR [--zoomed]
      生成後の検査: 実寸、安全矩形を重ねた DIR/overlay.png、城の赤い屋根の位置（城の枠の外・矩形への重なり）。物の有無の最終判断は目視。
      --zoomed（zoom 後の画像）: 城は見切れてよいので屋根が無くてもよく（有れば矩形への重なりだけ見る）、奥の縁の上がりは測らず、代わりに敵・味方の枠が床（濃い茶色の板）の上に載っているか（枠内の床画素の割合）を見る。
  ... ref --out STAGE.png
      参照見本（TRM-02 の舞台の柱・ランタン・緞帳・書き割りの空と山・舞台板だけを切り出して並べた見本。城・樅を含まない。見本に城・樅が入ると構図を写して台帳の座標を無視したため。城・樅の位置は台帳『配置』が正本）。
  ... zoom BG011 IMAGE.png --crop X,Y,W,H --out OUT.png
      クロップ枠（16:9）を 1672x941 に Lanczos 拡大する。元画像は変えない。枠・倍率・元画像の sha256 を OUT の隣の zoom-report.json に残す。座標を守れない・床が傾く時は再生成せずまずこれ（局所合成より先）。
  ... zoom-search BG011 IMAGE.png --out DIR [--scales 1.3,1.5,1.7,...] [--top 8]
      クロップ枠を倍率×位置で探索し、各候補を check --zoomed と同じ基準（全枠の床画素97%以上）で採点。合格候補のうち『舞台セット（床以外の画素）が最も多く見える』順に番号付けして DIR/contact.png（コンタクトシート。合格は緑・不合格は赤）と DIR/search.json に出す。倍率の下限は、全枠が床に載る最小の倍率が決める（BG011 take7 は約2.4）。
  ... mask BG011 castle --out MASK.png
      城の枠だけを白にした局所合成用マスク（image-local-replace で城だけ直す時）。
"""
import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "sit-field-background" / "tools"))
import ledger_io as LIO  # noqa: E402
import oblique_text as X  # noqa: E402

KIND_COLOUR = {
    "castle": (250, 250, 250), "fir": (245, 250, 245), "post": (75, 45, 25), "lantern": (214, 176, 70),
    "wall": (225, 210, 185), "roof": (80, 80, 92), "fence": (190, 160, 100), "curtain": (40, 100, 50), "backdrop": (95, 155, 220),
    "pillar": (190, 185, 205), "light": (255, 241, 200),  # BG013（時の最果て）: 石の柱・光の柱
}
FLOOR = (120, 70, 38)
SLOPED = ("backdrop", "wall")  # 下端が床の奥の縁に沿う板（書き割り・土塀）
FLOOR_MIN = 0.95  # check --zoomed が要る枠内の床画素の割合の下限（9割だと城の胴の端・柱の根元が枠に入っても通ったため）
SEARCH_MARGIN = 0.97  # zoom-search の合格線。拡大後の再計算で数%ずれるので check より厳しくして余裕を持たせる
DESK = (60, 35, 22)


def load(bg_id):
    for r in LIO.read("戦闘背景"):
        if r["背景ID"] == bg_id:
            if not r["配置"].strip():
                sys.exit(f"{bg_id}: 台帳の『配置』が空（生成しない。まず台帳に配置を書く）")
            L = json.loads(r["配置"])
            base = L.get("継承")  # 安全矩形・床・描画オフセット・画面サイズは同じ規則なので、継承元の台帳行を単一正本にする
            if base:
                _, B0 = load(base)
                for k in ("canvas", "safe_rects", "floor", "描画オフセット"):
                    L.setdefault(k, B0[k])
            return r, L
    sys.exit(f"戦闘背景 {bg_id} が台帳に無い")


def overlap(a, b):
    """矩形 [x,y,w,h] の重なり面積。"""
    w = min(a[0] + a[2], b[0] + b[2]) - max(a[0], b[0])
    h = min(a[1] + a[3], b[1] + b[3]) - max(a[1], b[1])
    return max(w, 0) * max(h, 0) if w > 0 and h > 0 else 0


def pre_check(L):
    """生成前の検査。問題の一覧を返す（空なら合格）。"""
    problems = []
    W, H = L["canvas"]
    for it in L["items"]:
        x, y, w, h = it["box"]
        cut = it.get("cutoff", False)  # 上端・左右端で見切れてよい舞台セット（画面の外へ出てよい。ログ帯への重なりも許す）
        if not cut and (x < 0 or y < 0 or x + w > W or y + h > H):
            problems.append(f"{it['id']}: 画面の外にはみ出す")
        if it["object"]:
            for sr in L["safe_rects"]:
                if cut and sr["id"] == "log":
                    continue
                if overlap(it["box"], sr["box"]):
                    problems.append(f"{it['id']}（{it['名']}）が安全矩形 {sr['id']}（{sr['名']}）に重なる")
    f = L["floor"]
    quad = [f["back_left"], f["back_right"], f["front_right"], f["front_left"]]
    for sr in L["safe_rects"]:
        if sr["id"] != "log":  # 敵・味方の枠と下段の窓の四隅は床の四角形の中（ログ帯は上端の舞台セットがかかってよい）
            x, y, w, h = sr["box"]
            for cn, pt in (("左上", (x, y)), ("右上", (x + w, y)), ("右下", (x + w, y + h)), ("左下", (x, y + h))):
                if not point_in_quad(pt, quad):
                    problems.append(f"枠 {sr['id']} の{cn}の角 {pt} が床の四角形の外（枠が床に載らない）")
    rise = f["back_left"][1] - f["back_right"][1]
    if rise < f["min_rise_px"]:
        problems.append(f"床の奥の縁の上がりが {rise}px（{f['min_rise_px']}px 以上が要る。右端のyを左端より小さく）")
    return problems


def draw_offset(L, x):
    """モデルの描画オフセット（観測値）: 奥の縁と書き割りは割付図より下へずれて描かれる。x の位置でのずれ(px)を、左右2点の実測から直線で出す（外側は端値固定＝clamp）。台帳『配置.描画オフセット』が無ければ 0。"""
    o = L.get("描画オフセット")
    if not o:
        return 0.0
    (xl, dl), (xr, dr) = (o["x_left"], o["dy_left"]), (o["x_right"], o["dy_right"])
    t = min(max((x - xl) / (xr - xl), 0.0), 1.0)
    return dl + (dr - dl) * t


def corrected_layout(L):
    """モデルに渡す（割付図・送信文の）配置。奥の縁と、奥の縁に立つ舞台セット（cutoff の物）を、観測した描画オフセットの分だけ上へ寄せる。台帳の値（狙い）は変えない。見切れの物は画面に最低 min_visible px 残す。"""
    import copy
    C = copy.deepcopy(L)
    f = C["floor"]
    for k in ("back_left", "back_right"):
        f[k][1] -= draw_offset(L, f[k][0])
    mv = L.get("描画オフセット", {}).get("min_visible", 0)
    for it in C["items"]:
        if it.get("cutoff"):
            x, y, w, h = it["box"]
            y -= draw_offset(L, x + w / 2)
            if it["kind"] not in SLOPED and y + h < mv:  # 見切れの物は画面に最低 mv px 残す
                y = mv - h
            it["box"] = [round(x), round(y), round(w), round(h)]
    for k in ("back_left", "back_right"):
        f[k] = [round(f[k][0]), round(f[k][1])]
    return C


def point_in_quad(pt, quad):
    """点 pt が凸四角形 quad（順に回る4点）の中（辺上を含む）か。"""
    sign = 0
    for i in range(4):
        (x0, y0), (x1, y1) = quad[i], quad[(i + 1) % 4]
        cross = (x1 - x0) * (pt[1] - y0) - (y1 - y0) * (pt[0] - x0)
        if abs(cross) < 1e-9:
            continue
        if sign == 0:
            sign = 1 if cross > 0 else -1
        elif (cross > 0) != (sign > 0):
            return False
    return True


def layout_image(L):
    from PIL import Image, ImageDraw
    W, H = L["canvas"]
    im = Image.new("RGB", (W, H), DESK)
    d = ImageDraw.Draw(im)
    f = L["floor"]
    d.polygon([tuple(f["back_left"]), tuple(f["back_right"]), tuple(f["front_right"]), tuple(f["front_left"])], fill=tuple(L.get("地面色", FLOOR)))
    (bx0, by0), (bx1, by1) = f["back_left"], f["back_right"]

    def edge(x):  # 床の奥の縁（右上がりの直線）
        return by0 + (by1 - by0) * (x - bx0) / (bx1 - bx0)

    for it in sorted(L["items"], key=lambda i: i["kind"] not in SLOPED):  # 書き割り・土塀を先に描き、その前に物を重ねる
        x, y, w, h = it["box"]
        if it["kind"] in SLOPED:  # 書き割り板・土塀の下端は床の奥の縁に沿う
            d.polygon([(x, y), (x + w, y), (x + w, edge(x + w)), (x, edge(x))], fill=KIND_COLOUR[it["kind"]])
        else:
            d.rectangle([x, y, x + w, y + h], fill=KIND_COLOUR[it["kind"]])
    return im


def build_prompt(L):
    W, H = L["canvas"]
    f = L["floor"]
    T = {"head": "head", "subject": "subject", "floor": "floor", "only": "only", "materials": "materials"}
    T.update(L.get("文面", {}))  # 背景ごとの文面ID（プロンプト文面.yaml の PR.battle.<名前>）
    parts = [
        X.text("PR.battle." + T["head"], w=W, h=H),
        X.text("PR.battle." + T["subject"], rise=f["min_rise_px"]),
        X.text("PR.battle." + T["floor"]),
    ]
    for it in L["items"]:
        if it["object"] or it["kind"] in SLOPED:
            x, y, w, h = it["box"]
            if it.get("cutoff"):
                parts.append(X.text("PR.battle.item-cut", name=it["名"], x0=x, x1=x + w, y1=max(y + h, L.get("描画オフセット", {}).get("min_visible", 0))))
            else:
                parts.append(X.text("PR.battle.item", name=it["名"], x0=x, x1=x + w, y0=y, y1=y + h))
    parts.append(X.text("PR.battle." + T["only"]))
    parts.append(X.text("PR.battle." + T["materials"]))
    return "\n\n".join(parts) + "\n"


def cmd_build(a):
    if not Path(a.stage_ref).is_file():
        sys.exit(f"--stage-ref {a.stage_ref} が無い（先に ref サブコマンドで作る）")
    _, L = load(a.bg_id)
    problems = pre_check(L)
    if problems:
        sys.exit("生成前の検査に失敗（生成しない）:\n  " + "\n  ".join(problems))
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    C = corrected_layout(L)  # 検査は台帳の値（狙い）、モデルへは描画オフセットを引いた値
    layout_image(C).save(out / "layout.png")
    (out / "send.txt").write_text(build_prompt(C), encoding="utf-8")
    (out / "refs.txt").write_text(f"1. {out / 'layout.png'}（割付図）\n2. {a.stage_ref}（採用済み TRM-02 の舞台部分の切り出し。材料・色・モチーフのみ）\n", encoding="utf-8")
    print(f"OK: {out}/layout.png send.txt refs.txt（生成前の検査 合格: 物は全て安全矩形の外・床の奥の縁は右上がり）")


# TRM-02 の舞台の見本（採用済み画像の座標。城・樅を含まない部分だけ）: (名前, x, y, w, h)
TRM02 = "assets/images/fields/reference/teramachi-kindergarten-playroom-trm02-adopted.webp"
REF_PARTS = (("柱・ランタン・左の緞帳", 600, 160, 78, 170), ("空と綿の雲", 705, 205, 70, 50), ("雪山", 677, 258, 85, 28),
             ("舞台板", 610, 322, 455, 50), ("右の緞帳・柱・ランタン", 1000, 160, 80, 170))


def cmd_ref(a):
    from PIL import Image
    if a.bg:  # 背景の台帳『配置.参照見本』（採用済みの絵の切り出しを並べた見本シート）から作る
        _, L = load(a.bg)
        spec = L["参照見本"]
        src = Image.open(HERE.parents[3] / spec["source"]).convert("RGB")
        tiles = []
        for name, x, y, w, h in spec["parts"]:
            t = src.crop((x, y, x + w, y + h))
            tiles.append(t.resize((round(t.width * spec["tile_h"] / t.height), spec["tile_h"])))
        sheet = Image.new("RGB", (spec["sheet_w"], spec["tile_h"] * spec["rows"]), (40, 30, 24))
        cx = cy = 0
        for t in tiles:
            if cx + t.width > spec["sheet_w"]:
                cx, cy = 0, cy + spec["tile_h"]
            sheet.paste(t, (cx, cy))
            cx += t.width
        sheet.save(a.out)
        print(f"OK: {a.out}（{a.bg} の参照見本シート。{spec['source']} の切り出し）")
        return
    src = Image.open(HERE.parents[3] / TRM02).convert("RGB")
    parts = [src.crop((x, y, x + w, y + h)) for _, x, y, w, h in REF_PARTS]
    sheet = Image.new("RGB", (480, 260), (40, 30, 24))
    sheet.paste(parts[0], (0, 0))
    sheet.paste(parts[1], (84, 0))
    sheet.paste(parts[2], (84, 56))
    sheet.paste(parts[4], (400, 0))
    sheet.paste(parts[3].resize((480, 52)), (0, 176))
    sheet.save(a.out)
    print(f"OK: {a.out}（TRM-02 の舞台の見本。城・樅を含まない）")


def edge_rise(px, floor):
    """生成画像の奥の縁（書き割りの塗り〔青空・白い雪〕の最下端）を中央部の列で測り、床の奥の縁の左右の端の x まで直線で延ばした上がり量(px)を返す。測れなければ None。"""
    import numpy as np
    H = px.shape[0]
    xs, ys = [], []
    for x in range(420, 1300, 20):
        col = px[: int(H * 0.6), x, :]
        blue = (col[:, 2] > col[:, 0] + 25) & (col[:, 2] > col[:, 1])
        white = col.min(axis=1) > 190
        idx = np.nonzero(blue | white)[0]
        if len(idx):
            xs.append(x)
            ys.append(int(idx.max()))
    if len(xs) < 10:
        return None
    k, b = np.polyfit(xs, ys, 1)
    return float(-(k * (floor["back_right"][0] - floor["back_left"][0])))


OBJ_MAX = 0.005  # 枠内に許す『舞台セットの物ピクセル』の割合（板のハイライトなどの誤検出の余裕）


def red_roof_mask(px):
    """赤い円錐屋根。採用済み TRM-02 の屋根の実色に合わせ、g/r<0.50 かつ r-g>95 かつ r-b>100。TRM-02 の屋根らしい赤みの画素（r>150・r-g>60・r-b>80、1114画素）の中央値は (200,94,55)・r-g≈107、判定で拾えた画素（630画素）の中央値は (207,91,50)・r-g≈117。木の橙のハイライト (209,122,63)（g/r≈0.58、r-g=87）は含めない。実測: TRM-02 の屋根らしい赤みの画素の約57%を拾い、take10 の床の誤検出は0.002%（24画素）。注意: r-g>95 の閾値は屋根の r-g 中央値（≈107〜117）に近い崖で、床の誤検出を抑えるために take10 の1枚で調整した値であり、複数の絵で検証していない。別の絵で屋根の検出が不安定なら、屋根らしい画素を含む実画像で閾値を取り直す。"""
    r, g, b = px[..., 0], px[..., 1], px[..., 2]
    return (r > 150) & (g * 100 < r * 50) & (r - g > 95) & (r - b > 100)


def gold_mask(px):
    """金（ランタンの真鍮・房。床板の釘の頭のような小さな金の点は除く）。TRM-02 のランタンの中央値 (207,143,74)（g/r≈0.69）に合わせ、g/r>0.62 かつ b<110。木のハイライト g/r≈0.58 と淡い桃色 (b≥140) は含めない。実測: TRM-02 のランタンの暖色画素の約28%を拾い（5x5 以上の塊に絞った後。絞る前は約53%）、take10 の床の誤検出は0.16%（絞る前）。注意: 5x5 に絞ったため、細い金の飾り紐・房（幅5px未満の筋）の検出感度は落ちる（枠への侵入は overlay の目視で補う）。"""
    import numpy as np
    r, g, b = px[..., 0], px[..., 1], px[..., 2]
    m = (r > 190) & (g * 100 > r * 62) & (b < 110)
    # 床板の釘の頭（小さな金の点）は物にしない: 5x5 の範囲がほぼ全部金色（23/25以上）の塊だけを金とする
    sat = np.pad(m.astype("int32").cumsum(0).cumsum(1), ((1, 0), (1, 0)))
    box = sat[5:, 5:] - sat[:-5, 5:] - sat[5:, :-5] + sat[:-5, :-5]
    core = np.zeros(m.shape, dtype=bool)
    core[2:2 + box.shape[0], 2:2 + box.shape[1]] = box >= 23
    grown = np.zeros(m.shape, dtype=bool)
    for dy in range(-2, 3):
        for dx in range(-2, 3):
            grown |= np.roll(np.roll(core, dy, 0), dx, 1)
    return m & grown


def object_mask(px, ground="wood"):
    """舞台セット・背景の物に見える画素。wood/road: 青空・緑の緞帳・白い粘土や雪や雲・金の房やランタン・赤い屋根（床の板の色と、木の橙色のハイライトは含まない）。
    snow（厚い雪の地面）: 白い雪が床なので、白は物にしない。色のある面（土塀・藁・青・緑・金・赤。最大-最小が55超）と暗い面（瓦・石。最大が100未満）が物。
    thin-snow（薄雪の路面）: 黒い路面が床なので、暗い面は物にしない。色のある面（最大-最小が55超）だけが物。瓦・石の暗い灰色は色で区別できず、overlay の目視で数える。"""
    import numpy as np
    r, g, b = px[..., 0], px[..., 1], px[..., 2]
    if ground == "void-stone":  # 石の足場（BG013）: 柱は床と同じ色で色では区別できない（overlay の目視）。枠が虚空（暗い）に落ちた画素と光源の明るいクリーム色だけを物に数える
        return (np.maximum(np.maximum(r, g), b) < 45) | (np.minimum(np.minimum(r, g), b) >= 225)
    if ground == "thin-snow":  # 薄雪の路面: 黒いアスファルト・灰色・白い雪はどれも路面。色のある面だけが物
        return np.maximum(np.maximum(r, g), b) - np.minimum(np.minimum(r, g), b) > 55
    if ground == "snow":
        mx = np.maximum(np.maximum(r, g), b)
        mn = np.minimum(np.minimum(r, g), b)
        return (mx - mn > 55) | (mx < 100)
    return (b > r + 25) | (g > r + 8) | (np.minimum(np.minimum(r, g), b) > 175) | gold_mask(px) | red_roof_mask(px)


def floor_mask(px, ground="wood"):
    """床・路面に見える画素のマスク（全画素を一度だけ判定）。地面ごとに色の規則が違う:
    wood（BG011 の舞台板）: 物でなく、赤みのある茶色（赤が青より15以上大きく、赤が35以上）。濃い影の板も床。黒・灰色は床でない。
    road（アスファルト）: 物でなく、暗い灰色〜茶灰色。
    snow（厚い雪の地面）: 白〜灰白の低彩度（最小チャンネル100以上・最大-最小が55以下）。雪の影の灰色も床。
    thin-snow（薄雪の路面。BG012）: 低彩度（最大-最小が55以下）で最大が20以上＝黒い湿ったアスファルト・灰色・白い雪。"""
    import numpy as np
    r, g, b = px[..., 0], px[..., 1], px[..., 2]
    if ground == "void-stone":  # 石の足場の上面（灰紫の石）: 低彩度で、虚空（暗い）でも光源（明るいクリーム）でもない
        mx, mn = np.maximum(np.maximum(r, g), b), np.minimum(np.minimum(r, g), b)
        return (mx - mn <= 70) & (mx >= 70) & (mx <= 235)
    if ground == "thin-snow":
        mx, mn = np.maximum(np.maximum(r, g), b), np.minimum(np.minimum(r, g), b)
        return (mx - mn <= 55) & (mx >= 20)
    if ground == "snow":
        return (np.minimum(np.minimum(r, g), b) >= 100) & (np.maximum(np.maximum(r, g), b) - np.minimum(np.minimum(r, g), b) <= 55)
    if ground == "road":
        return ~object_mask(px) & (r < 150) & (np.abs(r - b) < 60)
    return ~object_mask(px) & (r > b + 15) & (r >= g) & (r >= 35)


def plank_seams(gray, x0, x1, y0, y1, k=2.5, gap=8, win=41):
    """床板の継ぎ目線の本数を、縦帯 x0〜x1・y0〜y1 の明るさの縦方向の谷から数える（win px の移動平均を引いた残差が -k 未満の局所最小、間隔 gap px 以上）。木目の筋も数えるので、板の継ぎ目と厳密には区別できない間接検査。"""
    import numpy as np
    a = np.asarray(gray, dtype=float)[y0:y1, x0:x1]
    prof = a.mean(axis=1)
    base = np.convolve(np.pad(prof, win // 2, mode="edge"), np.ones(win) / win, mode="valid")
    hp = prof - base
    idx = []
    for i in range(1, len(hp) - 1):
        if hp[i] < -k and hp[i] <= hp[i - 1] and hp[i] < hp[i + 1]:
            if not idx or i - idx[-1] >= gap:
                idx.append(i)
            elif hp[i] < hp[idx[-1]]:
                idx[-1] = i
    return idx


def black_mask(px):
    """黒い路面（最大チャンネル110未満）のマスク。薄雪の路面の『枠の上端帯に石・縁石が入っていないか』の検査に使う。"""
    return px.max(axis=2) < 110


class Integral:
    """マスクの積分画像。矩形内の真の画素数を O(1) で出す。"""

    def __init__(self, mask):
        import numpy as np
        self.sat = np.pad(mask.astype("int64").cumsum(0).cumsum(1), ((1, 0), (1, 0)))
        self.h, self.w = mask.shape

    def frac(self, box):
        x, y, w, h = [int(round(v)) for v in box]
        x0, y0 = max(x, 0), max(y, 0)
        x1, y1 = min(x + w, self.w), min(y + h, self.h)
        if x1 <= x0 or y1 <= y0:
            return 0.0
        t = self.sat
        return float(t[y1, x1] - t[y0, x1] - t[y1, x0] + t[y0, x0]) / ((x1 - x0) * (y1 - y0))


def cmd_check(a):
    import numpy as np
    from PIL import Image, ImageDraw
    _, L = load(a.bg_id)
    im = Image.open(a.image).convert("RGB")
    W, H = L["canvas"]
    report = {"size_ok": im.size == (W, H), "size": list(im.size), "problems": []}
    if not report["size_ok"]:
        report["problems"].append(f"実寸 {im.size}（{W}x{H} でない）")
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    ov = im.copy()
    d = ImageDraw.Draw(ov)
    for sr in L["safe_rects"]:
        x, y, w, h = sr["box"]
        d.rectangle([x, y, x + w, y + h], outline=(255, 0, 0), width=3)
    castle = next((i for i in L["items"] if i["kind"] == "castle"), None)  # 城のある背景（BG011）だけ
    if castle:
        x, y, w, h = castle["box"]
        d.rectangle([x, y, x + w, y + h], outline=(0, 255, 255), width=2)
    ov.save(out / "overlay.png")
    # 城の赤い屋根（赤い円錐屋根）の位置: 赤い画素の外接矩形を城の枠・安全矩形と比べる
    px = np.asarray(im, dtype=int)
    red = red_roof_mask(px)  # 赤い円錐屋根（木のハイライトは除く）
    ys, xs = np.nonzero(red)
    if castle is None:
        report["castle_roof"] = None  # 城の無い背景（BG012 など）は屋根の検査をしない
    elif len(xs) < 200:
        report["castle_roof"] = None
        if not a.zoomed:
            report["problems"].append("城の赤い屋根が検出できない（城が無い/色が違う。目視で確認）")
    else:
        x0, x1 = np.percentile(xs, [1, 99])  # 外れ値（小さな赤い点）を除く
        y0, y1 = np.percentile(ys, [1, 99])
        bx = [int(x0), int(y0), int(x1 - x0), int(y1 - y0)]
        report["castle_roof"] = bx
        tol = 30
        if not a.zoomed and (bx[0] < x - tol or bx[1] < y - tol or bx[0] + bx[2] > x + w + tol or bx[1] + bx[3] > y + h + tol):
            report["problems"].append(f"城の屋根 {bx} が城の枠 {castle['box']}（±{tol}）の外")
        for sr in L["safe_rects"]:
            if (a.zoomed or castle.get("cutoff")) and sr["id"] == "log":
                continue  # 見切れてよい上端の舞台セットはログ帯にかかってよい
            if overlap(bx, sr["box"]):
                report["problems"].append(f"城の屋根 {bx} が安全矩形 {sr['id']} に重なる")
    pl = L.get("床板")  # 床板の幅（巨大な1枚板に見えないか）の間接検査: 板の継ぎ目線の本数
    if pl:
        gray = np.asarray(im.convert("L"))
        counts = [len(plank_seams(gray, x0, x1, pl["y0"], pl["y1"], pl["k"], pl["gap"], pl["win"])) for x0, x1 in pl["strips"]]
        report["plank_seams"] = counts
        if min(counts) < pl["min_seams"]:
            report["problems"].append(f"床板の継ぎ目線が {min(counts)} 本（{pl['min_seams']} 本以上が要る。板の幅が大きく、巨大な1枚板に見える）")
    if a.zoomed:
        report["floor_fraction"] = {}
        integ = Integral(floor_mask(px, L.get("地面", "wood")))
        objm = Integral(object_mask(px, L.get("地面", "wood")))
        report["object_fraction"] = {}
        for sr in L["safe_rects"]:
            if sr["id"] != "log":  # 敵・味方の枠と下段の窓（コマンド・敵名・status）は床の上で、物が無い
                of = objm.frac(sr["box"])
                report["object_fraction"][sr["id"]] = round(of, 4)
                if of > OBJ_MAX:
                    report["problems"].append(f"枠 {sr['id']} に舞台セットの物（城・塔・柱・ランタン・緞帳・書き割り）の画素が {of:.1%}（{OBJ_MAX:.1%} 以下が要る）")
                fr = integ.frac(sr["box"])
                report["floor_fraction"][sr["id"]] = round(fr, 3)
                if fr < FLOOR_MIN:
                    report["problems"].append(f"枠 {sr['id']} の床画素が {fr:.0%}（{FLOOR_MIN:.0%} 以上が要る。枠が床の上に載っていない）")
        rise, need = None, 0
    else:
        rise = edge_rise(px, L["floor"])
        need = L["floor"]["min_rise_px"]
    snow = L.get("雪の量")  # 薄雪の路面（BG012）: 敵・味方の枠の中で、黒い路面と白い雪の割合を見る
    if a.zoomed and snow:
        mx, mn = px.max(axis=2), px.min(axis=2)
        black = (mx < 110)
        white = (mn >= 150) & (mx - mn <= 55)
        tot = b_ = w_ = 0
        for sr in L["safe_rects"]:
            if sr["id"].startswith("ally") or sr["id"] == "enemy":
                x, y, w, h = [int(v) for v in sr["box"]]
                tot += w * h
                b_ += int(black[y:y + h, x:x + w].sum())
                w_ += int(white[y:y + h, x:x + w].sum())
        tb = L["雪の量"].get("top_band")
        if tb:  # 枠の上端帯に石・縁石・綿の塊が入っていないか（路面の黒が少ない帯は NG）
            report["top_band_black"] = {}
            for sr in L["safe_rects"]:
                if sr["id"].startswith("ally") or sr["id"] == "enemy":
                    x, y, w, h = sr["box"]
                    bh = max(int(h * tb["frac"]), 1)
                    f = float(black[int(y):int(y) + bh, int(x):int(x) + w].mean())
                    report["top_band_black"][sr["id"]] = round(f, 3)
                    if f < tb["black_min"]:
                        report["problems"].append(f"枠 {sr['id']} の上端帯（上端から{tb['frac']:.0%}）の路面の黒が {f:.0%}（{tb['black_min']:.0%} 以上が要る。石・縁石・綿の塊が枠に入っている）")
        flat = L["雪の量"].get("flat_left")
        if flat:  # 路面のうねり・盛り上がり・湾曲した轍（左端）の間接検査: 左端の帯の低周波の明るさのむら
            from PIL import ImageFilter
            bl = np.asarray(im.convert("L").filter(ImageFilter.BoxBlur(flat["blur"])), dtype=float)[flat["y0"]:flat["y1"], :flat["w"]]
            lf = float((bl - bl.mean(axis=1, keepdims=True)).std())
            report["left_lowfreq"] = round(lf, 2)
            if lf > flat["max"]:
                report["problems"].append(f"画面左端の路面の低周波の明るさのむらが {lf:.1f}（{flat['max']} 以下が要る。路面がうねり・盛り上がり・湾曲した轍に見える）")
        report["road_black_fraction"] = round(b_ / tot, 3)
        report["road_white_fraction"] = round(w_ / tot, 3)
        if b_ / tot < snow["black_min"]:
            report["problems"].append(f"路面の黒い面が {b_ / tot:.0%}（{snow['black_min']:.0%} 以上が要る。雪が積もりすぎ）")
        if w_ / tot > snow["white_max"]:
            report["problems"].append(f"路面の白い雪が {w_ / tot:.0%}（{snow['white_max']:.0%} 以下が要る。雪が積もりすぎ）")
    report["back_edge_rise_px"] = None if rise is None else round(rise, 1)
    if a.zoomed:
        pass
    elif rise is None:
        report["problems"].append("奥の縁（書き割りの下端）が測れない。overlay.png 上で左右の y を測って記録する")
    elif rise < need:
        report["problems"].append(f"奥の縁の上がりが {rise:.1f}px（{need}px 以上が要る。右端が左端より高い）")
    report["manual"] = "樅・緞帳・柱・ランタン・床板の線の向き（奥の縁と同じ右上がりの遠近で、手前ほど間隔が広い）・ミニチュア感は overlay.png を目視して適合表を作る（奥の縁の上がりは自動測定が不確かなら overlay.png 上で左右の y を測る）"
    (out / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=1))
    return 1 if report["problems"] else 0


def crop_ratio_ok(w, h, W, H):
    """クロップ枠が W:H か。高さを四捨五入した分（0.5px）だけ許す（zoom-search の候補は h=round(w*H/W) なので必ず通る）。"""
    return abs(w * H - h * W) <= W / 2 + 1e-9


def cmd_zoom(a):
    import hashlib
    from PIL import Image
    _, L = load(a.bg_id)
    W, H = L["canvas"]
    x, y, w, h = [int(v) for v in a.crop.split(",")]
    im = Image.open(a.image).convert("RGB")
    if x < 0 or y < 0 or x + w > im.width or y + h > im.height:
        sys.exit(f"クロップ枠 {x},{y},{w},{h} が元画像 {im.size} の外")
    if not crop_ratio_ok(w, h, W, H):
        sys.exit(f"クロップ枠 {w}x{h} が {W}:{H} の比でない")
    out = im.crop((x, y, x + w, y + h)).resize((W, H), Image.LANCZOS)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    out.save(a.out)
    report = {"source": str(a.image), "source_sha256": hashlib.sha256(Path(a.image).read_bytes()).hexdigest(),
              "crop": [x, y, w, h], "scale": round(W / w, 4), "output": [W, H]}
    Path(a.out).with_name("zoom-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))


def _candidate(integ, L, scale, cx, cy, obj=None, blk=None):
    """元画像のクロップ枠（左上 cx,cy・倍率 scale）を採点する。拡大後の枠 [x,y,w,h] は元画像の [cx+x/scale, cy+y/scale, w/scale, h/scale] に当たる。"""
    W, H = L["canvas"]
    cw = round(W / scale)
    ch = round(cw * H / W)  # zoom の 16:9 判定と同じ丸め（候補が zoom に弾かれない）
    if cx < 0 or cy < 0 or cx + cw > integ.w or cy + ch > integ.h:
        return None
    fr = {}
    for sr in L["safe_rects"]:
        if sr["id"] != "log":
            x, y, w, h = sr["box"]
            fr[sr["id"]] = integ.frac([cx + x / scale, cy + y / scale, w / scale, h / scale])
    objf = {k: (obj.frac([cx + sr["box"][0] / scale, cy + sr["box"][1] / scale, sr["box"][2] / scale, sr["box"][3] / scale]) if obj else 0.0)
            for k, sr in ((s["id"], s) for s in L["safe_rects"]) if k != "log"}
    tb = L.get("雪の量", {}).get("top_band")
    band = {}
    if tb and blk:  # 薄雪の路面: 枠の上端帯の路面の黒（石・縁石が入る候補を落とす）
        for k, sr in ((s["id"], s) for s in L["safe_rects"]):
            if k.startswith("ally") or k == "enemy":
                x, y, w, h = sr["box"]
                band[k] = blk.frac([cx + x / scale, cy + y / scale, w / scale, h * tb["frac"] / scale])
    band_ok = all(v >= tb["black_min"] for v in band.values()) if band else True
    return {"scale": scale, "crop": [int(cx), int(cy), cw, ch], "floor_fraction": fr, "object_fraction": objf, "top_band_black": band,
            "ok": all(v >= SEARCH_MARGIN for v in fr.values()) and all(v <= OBJ_MAX for v in objf.values()) and band_ok,
            "set_visible": 1 - integ.frac([cx, cy, cw, ch])}


def cmd_zoom_search(a):
    import numpy as np
    from PIL import Image, ImageDraw
    _, L = load(a.bg_id)
    W, H = L["canvas"]
    im = Image.open(a.image).convert("RGB")
    px = np.asarray(im, dtype=int)
    integ = Integral(floor_mask(px, L.get("地面", "wood")))
    obj = Integral(object_mask(px, L.get("地面", "wood")))
    blk = Integral(black_mask(px))
    scales = [float(v) for v in a.scales.split(",")]
    cands = []
    for sc in scales:
        cw, ch = W / sc, H / sc
        for cy in range(0, int(px.shape[0] - ch) + 1, 4):
            for cx in range(0, int(px.shape[1] - cw) + 1, 10):
                c = _candidate(integ, L, sc, cx, cy, obj, blk)
                if c:
                    cands.append(c)
    ok = sorted([c for c in cands if c["ok"]], key=lambda c: -c["set_visible"])
    # 不合格でも倍率ごとの最良（最も床画素が多い）を比較用に載せる
    best_by_scale = {}
    for c in cands:
        if not c["ok"]:
            k = c["scale"]
            m = min(c["floor_fraction"].values())
            if k not in best_by_scale or m > best_by_scale[k][0]:
                best_by_scale[k] = (m, c)
    shown = ok[: a.top] + [v[1] for k, v in sorted(best_by_scale.items()) if not ok or k < ok[-1]["scale"]][:4]
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    tw, th = 640, 360
    cols = 3
    rows_n = (len(shown) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * tw, rows_n * (th + 40)), (30, 30, 30))
    d = ImageDraw.Draw(sheet)
    for i, c in enumerate(shown, 1):
        x, y, w, h = c["crop"]
        t = im.crop((x, y, x + w, y + h)).resize((tw, th), Image.LANCZOS)
        ox, oy = ((i - 1) % cols) * tw, ((i - 1) // cols) * (th + 40)
        sheet.paste(t, (ox, oy + 40))
        mn = min(c["floor_fraction"].values())
        d.rectangle([ox, oy, ox + tw, oy + 38], fill=(20, 90, 30) if c["ok"] else (110, 20, 20))
        d.text((ox + 6, oy + 4), f"#{i} x{c['scale']} crop={x},{y},{w},{h}", fill=(255, 255, 255))
        d.text((ox + 6, oy + 20), f"{'OK' if c['ok'] else 'NG'} min floor {mn:.0%} / stage set visible {c['set_visible']:.0%}", fill=(255, 255, 255))
        c["no"] = i
    sheet.save(out / "contact.png")
    (out / "search.json").write_text(json.dumps({"ok_count": len(ok), "candidates": shown}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"合格 {len(ok)} 件（全 {len(cands)} 候補）。contact.png に {len(shown)} 件。最良の合格: " + (f"#1 x{ok[0]['scale']} crop={ok[0]['crop']}" if ok else "なし"))


def cmd_mask(a):
    from PIL import Image, ImageDraw
    _, L = load(a.bg_id)
    it = next((i for i in L["items"] if i["id"] == a.item), None)
    if it is None:
        sys.exit(f"配置に物 {a.item} が無い")
    W, H = L["canvas"]
    m = Image.new("L", (W, H), 0)
    x, y, w, h = it["box"]
    ImageDraw.Draw(m).rectangle([x, y, x + w, y + h], fill=255)
    m.save(a.out)
    print(f"OK: {a.out}（{a.item} の枠 {it['box']}）")


def main(argv=None):
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("bg_id")
    b.add_argument("--stage-ref", required=True)
    b.add_argument("--out", required=True)
    c = sub.add_parser("check")
    c.add_argument("bg_id")
    c.add_argument("image")
    c.add_argument("--out", required=True)
    c.add_argument("--zoomed", action="store_true")
    rf = sub.add_parser("ref")
    rf.add_argument("--out", required=True)
    rf.add_argument("--bg", help="背景ID（台帳『配置.参照見本』から作る）。省略すると BG011 の TRM-02 舞台の見本")
    z = sub.add_parser("zoom")
    z.add_argument("bg_id")
    z.add_argument("image")
    z.add_argument("--crop", required=True)
    z.add_argument("--out", required=True)
    zs = sub.add_parser("zoom-search")
    zs.add_argument("bg_id")
    zs.add_argument("image")
    zs.add_argument("--out", required=True)
    zs.add_argument("--scales", default="1.0,1.05,1.1,1.2,1.3,1.5,1.7,1.9,2.1,2.3,2.5")
    zs.add_argument("--top", type=int, default=6)
    m = sub.add_parser("mask")
    m.add_argument("bg_id")
    m.add_argument("item")
    m.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    r = {"build": cmd_build, "check": cmd_check, "mask": cmd_mask, "ref": cmd_ref, "zoom": cmd_zoom, "zoom-search": cmd_zoom_search}[a.cmd](a)
    return r or 0


if __name__ == "__main__":
    sys.exit(main())
