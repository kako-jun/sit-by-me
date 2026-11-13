"""サンプル専用マップ SMP-01（時の最果て）の編集用プロンプトを plan から機械生成する（決定 DEMO.sample-bg-last-place、Issue #281）。

本編の台帳MAP・装飾プール・エリア固定には行を持たず、plan（docs/production/sample-field/SMP-01-plan.json）の look と
台帳 プロンプト文面.yaml の PR.sample.* だけから組む。画像生成そのものはしない（実行は run サブコマンドの codex exec。承認済みのときだけ）。

使い方:
  uv run --with numpy --with opencv-python-headless --with pillow python3 -I sample_field_build.py build [--out DIR]
  出力: DIR/send.txt（imagegen 用の完全な送信文）・DIR/prompt.txt（来歴つき）。参照は SMP-01-clean.png の1枚だけ。
"""
import argparse
import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import oblique_mock as M  # noqa: E402
import oblique_text as X  # noqa: E402

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))
DIR = os.path.join(REPO, "docs", "production", "sample-field")
PLAN = os.path.join(DIR, "SMP-01-plan.json")


def _pts(poly, step=1):
    return [[round(u), round(v)] for u, v in poly[::step]]


def _bbox(poly):
    xs = [q[0] for q in poly]; ys = [q[1] for q in poly]
    return [round(min(xs)), round(min(ys)), round(max(xs)), round(max(ys))]


def problems(p):
    """look 空欄・足場が無い・光源が無いなどの生成前の検査。"""
    out = []
    for e in p["floors"] + p["boxes"]:
        if not (e.get("look") or "").strip():
            out.append(f"{e['id']}: look が空（生成しない）")
    if not any(f.get("walkable") for f in p["floors"]):
        out.append("歩ける床が無い")
    if not any(b.get("kind") == "light" for b in p["boxes"]):
        out.append("光源（kind=light）が無い")
    if not any(b.get("kind") == "column" for b in p["boxes"]):
        out.append("柱（kind=column）が無い")
    return out


def build_prompt(p):
    L = [X.text("PR.sample.title", key=p["map_id"]), "", X.text("PR.sample.role"), "", X.text("PR.sample.miniature"), "",
         X.text("PR.sample.layers"), "", X.text("PR.sample.frame"), "", "SURFACES（床・面。座標は平面の外形を画像へ射影した多角形の頂点）:"]
    for f in p["floors"]:
        poly = M.floor_img_poly(f)
        step = max(1, len(poly) // 12)
        L.append(X.text("PR.sample.look", id=f["id"], label=f.get("label") or f["id"], look=f["look"], pts=_pts(poly, step), bbox=_bbox(poly)))
    L += ["", "OBJECTS（柱と光源。外接矩形が位置と大きさ。上端はモックの箱の天面の位置）:"]
    for b in p["boxes"]:
        polys = M.box_polys(b["rect"], b["h"], b["color"])
        allp = [q for pl in polys for q in pl[0]]
        L.append(X.text("PR.sample.obj", id=b["id"], label=b.get("label") or b["id"], look=b["look"], bbox=_bbox(allp)))
    L += ["", X.text("PR.sample.forbid"), "", X.text("PR.notext"), "", X.text("PR.sample.output")]
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["build"])
    ap.add_argument("--out", default=os.path.join(DIR, "e2"))
    a = ap.parse_args()
    p = M.load_plan(PLAN)
    pr = problems(p)
    if pr:
        sys.exit("生成前の検査に失敗:\n" + "\n".join("- " + x for x in pr))
    os.makedirs(a.out, exist_ok=True)
    body = build_prompt(p)
    clean = os.path.join(DIR, "SMP-01-clean.png")
    sha = hashlib.sha256(open(clean, "rb").read()).hexdigest()
    with open(os.path.join(a.out, "prompt.txt"), "w", encoding="utf-8") as f:
        f.write(body + f"\n# 参照: 1枚目=SMP-01-clean.png sha256 {sha}（他の参照なし。寺町の素材見本シートは雪・瓦の見本なので渡さない）\n")
    with open(os.path.join(a.out, "send.txt"), "w", encoding="utf-8") as f:
        f.write(body)
    print(f"ok: {a.out}/send.txt ({len(body)} 文字)  clean sha256 {sha}")


if __name__ == "__main__":
    main()
