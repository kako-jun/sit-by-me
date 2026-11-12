"""戦闘背景（台帳 戦闘背景.yaml の1行）から、割付図(clean)・送信文・参照リストを機械生成し、生成後の安全矩形の重なりを検査する。

正本は台帳の『配置』列（JSON: 安全矩形・床の四隅・各物の位置）。送信文の文面は プロンプト文面.yaml の PR.battle.*（コードに文面を持たない）。
手で送信文を書かない・手で割付図を描かない（kako-jun 2026-11-12「画像作成はぜんぶスキル以外ではするな。再現性がなくなる」）。

使い方（リポ root から）:
  uv run --with pillow --with numpy python3 -I .claude/skills/sit-battle-background/tools/battle_bg_build.py build BG011 --stage-ref STAGE.png --out DIR
      生成前の検査（物が安全矩形に重ならないか・床の奥の縁が右上がりか）。通れば DIR/layout.png・DIR/send.txt・DIR/refs.txt を出す。重なれば停止。
  ... check BG011 IMAGE.png --out DIR
      生成後の検査: 実寸、安全矩形を重ねた DIR/overlay.png、城の赤い屋根の位置（城の枠の外・矩形への重なり）。物の有無の最終判断は目視。
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
    for it in L["items"]:
        x, y, w, h = it["box"]
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
    red = (px[..., 0] > 160) & (px[..., 1] < 100) & (px[..., 2] < 80) & (px[..., 0] - px[..., 1] > 90)
    ys, xs = np.nonzero(red)
    if len(xs) < 200:
        report["castle_roof"] = None
        report["problems"].append("城の赤い屋根が検出できない（城が無い/色が違う。目視で確認）")
    else:
        bx = [int(xs.min()), int(ys.min()), int(xs.max() - xs.min()), int(ys.max() - ys.min())]
        report["castle_roof"] = bx
        tol = 30
        if bx[0] < x - tol or bx[1] < y - tol or bx[0] + bx[2] > x + w + tol or bx[1] + bx[3] > y + h + tol:
            report["problems"].append(f"城の屋根 {bx} が城の枠 {castle['box']}（±{tol}）の外")
        for sr in L["safe_rects"]:
            if overlap(bx, sr["box"]):
                report["problems"].append(f"城の屋根 {bx} が安全矩形 {sr['id']} に重なる")
    report["manual"] = "樅・緞帳・柱・ランタン・前縁（テープ糊なし・無地）・奥の縁の右上がり・ミニチュア感は overlay.png を目視"
    (out / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=1))
    return 1 if report["problems"] else 0


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
    m = sub.add_parser("mask")
    m.add_argument("bg_id")
    m.add_argument("item")
    m.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    r = {"build": cmd_build, "check": cmd_check, "mask": cmd_mask}[a.cmd](a)
    return r or 0


if __name__ == "__main__":
    sys.exit(main())
