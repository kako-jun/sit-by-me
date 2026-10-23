#!/usr/bin/env python3
"""体内 BDY-xx の配置モック（body_layout.py の SPECS）から、機械可読の幾何 JSON を出す。画像生成はしない。

実行:
  uv run --with pillow python3 -I body_geometry_json.py [--out DIR] [--maps BDY-04 BDY-02 ...]
  既定の出力先: verification/body-layout/geometry/BDY-xx.json（+ index.json）

座標系: 各点は {"px":[x,y] (1920x1080 の画素), "ratio":[u,v] (模型の天面の矩形に対する 0..1)}。
  u = (x - 138) / 1644,  v = (y - 138) / 804。縁上の点は u/v が 0 か 1 になる。
  模型の天面 = 机90px + 土台の縁の帯48px（foamboard28+corrugated20）の内側。
スキーマ: sit-body-mock-geometry/1（docs/production/20261022-body-mocks-and-registration.md に表）。
"""
import argparse
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import body_layout as BL  # noqa: E402  (import 時にファイルは書かない。迷路の seed 探索だけが走る)

SCHEMA = "sit-body-mock-geometry/1"


def P(x, y):
    return {"px": [round(float(x), 2), round(float(y), 2)],
            "ratio": [round((x - BL.MX0) / BL.MW, 5), round((y - BL.MY0) / BL.MH, 5)]}


def R(v):
    return round(float(v), 2)


def edge_range(side, slot, half):
    """辺上の範囲（遷移トリガー候補）。辺に沿う座標 a..b を px と比で。"""
    if side in "NS":
        c, o, L = BL.MX0 + slot * BL.MW, BL.MX0, BL.MW
    else:
        c, o, L = BL.MY0 + slot * BL.MH, BL.MY0, BL.MH
    a, b = c - half, c + half
    return dict(along="x" if side in "NS" else "y", a_px=R(a), b_px=R(b),
                a_ratio=round((a - o) / L, 5), b_ratio=round((b - o) / L, 5), depth_px=BL.RANGE_DEPTH)


def build(m, rows, ev, nodes, portals, ratio=BL.DEFAULT_MAIN_WIDTH_RATIO):
    lwb = int(round(ratio * BL.MW))
    lw = BL.mlw(m, lwb)
    is02 = m == "BDY-02"
    ports = portals[m]
    out = dict(schema=SCHEMA, map=m, name=BL.NAMES[m], canvas=dict(w=BL.W, h=BL.H),
               model_rect=dict(px=dict(x0=BL.MX0, y0=BL.MY0, x1=BL.MX1, y1=BL.MY1, w=BL.MW, h=BL.MH),
                               desk_margin_px=BL.DESK_M, band_px=dict(foam=BL.BAND_FOAM, corrugated=BL.BAND_CORR)),
               coord_note="ratio=((x-138)/1644,(y-138)/804)。1672幅の採用画像へは x*(1672/1920) ではなく body_register.py の変換を使う",
               main_width_px=lwb, passage_width_px=lw,
               clean_colors=dict(floor=list(BL.FLOOR), terrain=list(BL.CLEAN_TERRAIN), desk=list(BL.CLEAN_DESK),
                                 band=list(BL.CLEAN_BAND), wall=list(BL.CLEAN_WALL)))
    # 出口（遷移トリガー候補）
    dirs = None if is02 else BL.inward_dirs(m, portals)
    exits = []
    for p, d in sorted(ports.items(), key=lambda kv: ("NESW".index(kv[1]["side"]), kv[1]["slot"])):
        half = lw / 2 if is02 else BL.edge_half(d["side"], dirs[p], lw)
        x, y = BL.edge_point(d["side"], d["slot"])
        e = dict(port=p, side=d["side"], slot=round(d["slot"], 4), edge_point=P(x, y), partner=f"{d['other']}.{d['other_port']}",
                 range=edge_range(d["side"], d["slot"], half))
        if dirs:
            e["inward_dir"] = [round(dirs[p][0], 4), round(dirs[p][1], 4)]
        exits.append(e)
    out["exits"] = exits
    if ev and m == "BDY-01":
        out["events"] = [dict(id="event-mouth", note="到着位置・向きは原文に無い(TBD)")]
    # 通路の中心線
    cors = []
    if is02:
        for p, kind, pl, isp in BL.bdy02_paths(ports):
            cors.append(dict(kind=kind, port=p, width_px=lw, polyline=[dict(P(*pt), is_port=bool(ip)) for pt, ip in zip(pl, isp)]))
        (cx, cy), r = BL.BDY02_HALL
        out["hall"] = dict(center=P(cx, cy), rx_px=BL.BDY02_HALL_RX, ry_px=r, wall_thickness_px=BL.WALL_T,
                           note="広間=横長の楕円の床。壁(WALL_T)は床の外側を一周し、帯が接する所だけ途切れる")
        out["neck"] = dict(junction=P(*BL.BDY02_J), mouth_bend_y_px=BL.BDY02_K_Y)
    else:
        for kind, pts, isp in BL.resolve_paths(m, portals):
            if kind == "graph":
                continue
            cors.append(dict(kind=kind, width_px=lw, polyline=[dict(P(*pt), is_port=bool(ip)) for pt, ip in zip(pts, isp)]))
        rooms = BL.SPECS[m].get("rooms", [])
        if rooms:
            out["rooms"] = [dict(name=n, center=P(BL.MX0 + x, BL.MY0 + y), radius_px=r) for n, x, y, r in rooms]
        if "sac" in BL.SPECS[m]:
            out["sac_centerline"] = [dict(P(BL.MX0 + x, BL.MY0 + y), radius_px=R(r)) for x, y, r in BL.sac_samples(m)[::20]]
    out["corridors"] = cors
    if m == "BDY-04":
        sp = BL.SPECS[m]
        cells = {f"{c},{r}": P(BL.MX0 + BL.MAZE_X0 + c * BL.MAZE_PITCH, BL.MY0 + BL.MAZE_Y0 + r * BL.MAZE_PITCH)
                 for c in range(BL.MAZE_COLS) for r in range(BL.MAZE_ROWS)}
        edges = sorted({tuple(sorted([a, b])) for a, ns in sp["tree"].items() for b in ns})
        out["maze"] = dict(cols=BL.MAZE_COLS, rows=BL.MAZE_ROWS, pitch_px=BL.MAZE_PITCH, seed=sp["seed"],
                           origin_in_model_px=[BL.MAZE_X0, BL.MAZE_Y0], root_cell=list(sp["root"]),
                           cell_count=len(cells), edge_count=len(edges), cells=cells,
                           edges=[[list(a), list(b)] for a, b in edges])
    if m in BL.SPECS and BL.SPECS[m] and "expect" in BL.SPECS[m]:
        out["expect"] = BL.SPECS[m]["expect"]
    # 位相の期待値（床の連結成分・出口数）
    out["topology_expect"] = dict(floor_components=1, exits_per_side={s: sum(1 for e in exits if e["side"] == s) for s in "NESW"},
                                  exit_count=len(exits))
    limbs = [c for c in cors if c["kind"] == "limb"]
    if len(cors) == 1 and len(limbs) == 1:   # 道が1本だけの MAP は折れ点の数が仕様（BDY-09/12=1、他の手足=0）
        out["topology_expect"]["bends"] = len(limbs[0]["polyline"]) - 2
    if m == "BDY-04":
        co, tj, de = BL.bend_counts(m)
        out["topology_expect"].update(corners=co, t_junctions=tj, dead_ends=de, passages=len(edges))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(BL.REPO / "verification/body-layout/geometry"))
    ap.add_argument("--maps", nargs="*", help="既定は BDY-01..17")
    a = ap.parse_args()
    outdir = Path(a.out)
    outdir.mkdir(parents=True, exist_ok=True)
    rows, ev, nodes, _svg, portals = BL.build_model()
    maps = a.maps or [f"BDY-{i:02d}" for i in range(1, 18)]
    idx = []
    for m in maps:
        BL.use17("A")
        g = build(m, rows, ev, nodes, portals)
        (outdir / f"{m}.json").write_text(json.dumps(g, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        idx.append(dict(map=m, exits=len(g["exits"]), corridors=len(g["corridors"])))
    (outdir / "index.json").write_text(json.dumps(dict(schema=SCHEMA, maps=idx), ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {len(maps)} files to {outdir}")


if __name__ == "__main__":
    main()
