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
      参照見本（TRM-02 の舞台の柱・ランタン・緞帳・書き割りの空と山・舞台板だけを切り出して並べた見本。城・樅を含まない。城・樅の位置は台帳『配置』が正本）。
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
    "curtain": (40, 100, 50), "backdrop": (95, 155, 220), "front_board": (85, 50, 28), "front_card": (190, 150, 90),
}
FLOOR = (120, 70, 38)
FLOOR_MIN = 0.95  # check --zoomed が要る枠内の床画素の割合の下限（9割だと城の胴の端・柱の根元が枠に入っても通ったため）
SEARCH_MARGIN = 0.97  # zoom-search の合格線。拡大後の再計算で数%ずれるので check より厳しくして余裕を持たせる
DESK = (60, 35, 22)


def load(bg_id):
    for r in LIO.read("戦闘背景"):
        if r["背景ID"] == bg_id:
            if not r["配置"].strip():
                sys.exit(f"{bg_id}: 台帳の『配置』が空（生成しない。まず台帳に配置を書く）")
            return r, json.loads(r["配置"])
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
        if x < 0 or y < 0 or x + w > W or y + h > H:
            problems.append(f"{it['id']}: 画面の外にはみ出す")
        if it["object"]:
            for sr in L["safe_rects"]:
                if overlap(it["box"], sr["box"]):
                    problems.append(f"{it['id']}（{it['名']}）が安全矩形 {sr['id']}（{sr['名']}）に重なる")
    f = L["floor"]
    rise = f["back_left"][1] - f["back_right"][1]
    if rise < f["min_rise_px"]:
        problems.append(f"床の奥の縁の上がりが {rise}px（{f['min_rise_px']}px 以上が要る。右端のyを左端より小さく）")
    return problems


def layout_image(L):
    from PIL import Image, ImageDraw
    W, H = L["canvas"]
    im = Image.new("RGB", (W, H), DESK)
    d = ImageDraw.Draw(im)
    f = L["floor"]
    d.polygon([tuple(f["back_left"]), tuple(f["back_right"]), tuple(f["front_right"]), tuple(f["front_left"])], fill=FLOOR)
    (bx0, by0), (bx1, by1) = f["back_left"], f["back_right"]

    def edge(x):  # 床の奥の縁（右上がりの直線）
        return by0 + (by1 - by0) * (x - bx0) / (bx1 - bx0)

    for it in L["items"]:
        x, y, w, h = it["box"]
        if it["kind"] == "backdrop":  # 書き割り板の下端は床の奥の縁に沿う
            d.polygon([(x, y), (x + w, y), (x + w, edge(x + w)), (x, edge(x))], fill=KIND_COLOUR["backdrop"])
        else:
            d.rectangle([x, y, x + w, y + h], fill=KIND_COLOUR[it["kind"]])
    return im


def build_prompt(L):
    W, H = L["canvas"]
    f = L["floor"]
    parts = [
        X.text("PR.battle.head", w=W, h=H),
        X.text("PR.battle.subject", rise=f["min_rise_px"]),
        X.text("PR.battle.floor"),
    ]
    for it in L["items"]:
        if it["object"] or it["kind"] == "backdrop":
            x, y, w, h = it["box"]
            parts.append(X.text("PR.battle.item", name=it["名"], x0=x, x1=x + w, y0=y, y1=y + h))
    fb = next(i for i in L["items"] if i["kind"] == "front_board")
    fc = next(i for i in L["items"] if i["kind"] == "front_card")
    parts.append(X.text("PR.battle.front", a=fb["box"][1], b=fc["box"][1], c=fc["box"][1] + fc["box"][3]))
    parts.append(X.text("PR.battle.only"))
    parts.append(X.text("PR.battle.materials"))
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
    layout_image(L).save(out / "layout.png")
    (out / "send.txt").write_text(build_prompt(L), encoding="utf-8")
    (out / "refs.txt").write_text(f"1. {out / 'layout.png'}（割付図）\n2. {a.stage_ref}（採用済み TRM-02 の舞台部分の切り出し。材料・色・モチーフのみ）\n", encoding="utf-8")
    print(f"OK: {out}/layout.png send.txt refs.txt（生成前の検査 合格: 物は全て安全矩形の外・床の奥の縁は右上がり）")


# TRM-02 の舞台の見本（採用済み画像の座標。城・樅を含まない部分だけ）: (名前, x, y, w, h)
TRM02 = "assets/images/fields/reference/teramachi-kindergarten-playroom-trm02-adopted.webp"
REF_PARTS = (("柱・ランタン・左の緞帳", 600, 160, 78, 170), ("空と綿の雲", 705, 205, 70, 50), ("雪山", 677, 258, 85, 28),
             ("舞台板と前面", 610, 322, 455, 80), ("右の緞帳・柱・ランタン", 1000, 160, 80, 170))


def cmd_ref(a):
    from PIL import Image
    src = Image.open(HERE.parents[3] / TRM02).convert("RGB")
    parts = [src.crop((x, y, x + w, y + h)) for _, x, y, w, h in REF_PARTS]
    sheet = Image.new("RGB", (480, 260), (40, 30, 24))
    sheet.paste(parts[0], (0, 0))
    sheet.paste(parts[1], (84, 0))
    sheet.paste(parts[2], (84, 56))
    sheet.paste(parts[4], (400, 0))
    sheet.paste(parts[3].resize((480, 84)), (0, 176))
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


def floor_mask(px):
    """床の板に見える画素のマスク（全画素を一度だけ判定）。物（青空・緑・白・金・明るい段ボール）と、前面の濃い板（周囲 15px の平均の赤が 78 未満）は床でない。板の細い暗い隙間は床のまま。"""
    from PIL import Image, ImageFilter
    import numpy as np
    r, g, b = px[..., 0], px[..., 1], px[..., 2]
    obj = (b > r) | (g > r + 8) | (np.minimum(np.minimum(r, g), b) > 175) | (r > 190)
    blur = np.asarray(Image.fromarray(r.astype("uint8")).filter(ImageFilter.BoxBlur(15)), dtype=int)
    return ~obj & (blur >= 78)


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
    castle = next(i for i in L["items"] if i["kind"] == "castle")
    x, y, w, h = castle["box"]
    d.rectangle([x, y, x + w, y + h], outline=(0, 255, 255), width=2)
    ov.save(out / "overlay.png")
    # 城の赤い屋根（赤い円錐屋根）の位置: 赤い画素の外接矩形を城の枠・安全矩形と比べる
    px = np.asarray(im, dtype=int)
    red = (px[..., 0] > 180) & (px[..., 1] < 70) & (px[..., 2] < 70) & (px[..., 0] - px[..., 1] > 120)  # 赤い円錐屋根（木の赤茶は除く閾値）
    ys, xs = np.nonzero(red)
    if len(xs) < 200:
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
            if overlap(bx, sr["box"]):
                report["problems"].append(f"城の屋根 {bx} が安全矩形 {sr['id']} に重なる")
    if a.zoomed:
        report["floor_fraction"] = {}
        integ = Integral(floor_mask(px))
        for sr in L["safe_rects"]:
            if sr["id"].startswith("ally") or sr["id"] == "enemy":
                fr = integ.frac(sr["box"])
                report["floor_fraction"][sr["id"]] = round(fr, 3)
                if fr < FLOOR_MIN:
                    report["problems"].append(f"枠 {sr['id']} の床画素が {fr:.0%}（{FLOOR_MIN:.0%} 以上が要る。枠が床の上に載っていない）")
        rise, need = None, 0
    else:
        rise = edge_rise(px, L["floor"])
        need = L["floor"]["min_rise_px"]
    report["back_edge_rise_px"] = None if rise is None else round(rise, 1)
    if a.zoomed:
        pass
    elif rise is None:
        report["problems"].append("奥の縁（書き割りの下端）が測れない。overlay.png 上で左右の y を測って記録する")
    elif rise < need:
        report["problems"].append(f"奥の縁の上がりが {rise:.1f}px（{need}px 以上が要る。右端が左端より高い）")
    report["manual"] = "樅・緞帳・柱・ランタン・前縁（テープ糊なし・無地）・ミニチュア感は overlay.png を目視して適合表を作る（奥の縁の上がりは自動測定が不確かなら overlay.png 上で左右の y を測る）"
    (out / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=1))
    return 1 if report["problems"] else 0


def cmd_zoom(a):
    import hashlib
    from PIL import Image
    _, L = load(a.bg_id)
    W, H = L["canvas"]
    x, y, w, h = [int(v) for v in a.crop.split(",")]
    im = Image.open(a.image).convert("RGB")
    if x < 0 or y < 0 or x + w > im.width or y + h > im.height:
        sys.exit(f"クロップ枠 {x},{y},{w},{h} が元画像 {im.size} の外")
    if abs(w * H - h * W) > max(w, h):  # 16:9（1px 程度の丸めは許す）
        sys.exit(f"クロップ枠 {w}x{h} が {W}:{H} の比でない")
    out = im.crop((x, y, x + w, y + h)).resize((W, H), Image.LANCZOS)
    out.save(a.out)
    report = {"source": str(a.image), "source_sha256": hashlib.sha256(Path(a.image).read_bytes()).hexdigest(),
              "crop": [x, y, w, h], "scale": round(W / w, 4), "output": [W, H]}
    Path(a.out).with_name("zoom-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False))


def _candidate(integ, L, scale, cx, cy):
    """元画像のクロップ枠（左上 cx,cy・倍率 scale）を採点する。拡大後の枠 [x,y,w,h] は元画像の [cx+x/scale, cy+y/scale, w/scale, h/scale] に当たる。"""
    W, H = L["canvas"]
    cw, ch = W / scale, H / scale
    if cx < 0 or cy < 0 or cx + cw > integ.w or cy + ch > integ.h:
        return None
    fr = {}
    for sr in L["safe_rects"]:
        if sr["id"].startswith("ally") or sr["id"] == "enemy":
            x, y, w, h = sr["box"]
            fr[sr["id"]] = integ.frac([cx + x / scale, cy + y / scale, w / scale, h / scale])
    return {"scale": scale, "crop": [int(cx), int(cy), int(cw), int(ch)], "floor_fraction": fr,
            "ok": all(v >= SEARCH_MARGIN for v in fr.values()), "set_visible": 1 - integ.frac([cx, cy, cw, ch])}


def cmd_zoom_search(a):
    import numpy as np
    from PIL import Image, ImageDraw
    _, L = load(a.bg_id)
    W, H = L["canvas"]
    im = Image.open(a.image).convert("RGB")
    px = np.asarray(im, dtype=int)
    integ = Integral(floor_mask(px))
    scales = [float(v) for v in a.scales.split(",")]
    cands = []
    for sc in scales:
        cw, ch = W / sc, H / sc
        for cy in range(0, int(px.shape[0] - ch) + 1, 4):
            for cx in range(0, int(px.shape[1] - cw) + 1, 10):
                c = _candidate(integ, L, sc, cx, cy)
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
    z = sub.add_parser("zoom")
    z.add_argument("bg_id")
    z.add_argument("image")
    z.add_argument("--crop", required=True)
    z.add_argument("--out", required=True)
    zs = sub.add_parser("zoom-search")
    zs.add_argument("bg_id")
    zs.add_argument("image")
    zs.add_argument("--out", required=True)
    zs.add_argument("--scales", default="1.3,1.5,1.7,1.9,2.1,2.3,2.5")
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
