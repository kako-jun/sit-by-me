"""石川県の行政区域(国土数値情報 N03-20230101)から能登半島の輪郭シルエットを描く。
輪郭は座標変換(Web メルカトル)以外一切加工しない。能登島のポリゴンだけを除く。
タイトル文字は Cinzel Bold(SIL OFL 1.1, scripts/fonts/) をアウトライン化し、縦に引き伸ばして能登島の外接矩形内に収める。
usage: uv run --with shapely --with fonttools python3 -I scripts/noto_logo_geo.py <N03 geojson> <outdir>
出典: 国土交通省 国土数値情報 行政区域データ N03-20230101 石川県 (CC BY 4.0 相当、出典表示)
"""
import json, math, sys
from shapely.geometry import shape, box
from shapely.ops import unary_union

src, out = sys.argv[1], sys.argv[2]
d = json.load(open(src))
polys, island = [], []
for f in d["features"]:
    g = shape(f["geometry"])
    for pg in (g.geoms if g.geom_type == "MultiPolygon" else [g]):
        c = pg.centroid
        # 能登島: 七尾市に属する約 47km2 の島ポリゴン
        if f["properties"]["N03_004"] == "七尾市" and 0.004 < pg.area < 0.006 and 136.9 < c.x < 137.1 and 37.1 < c.y < 37.2:
            island.append(pg); continue
        polys.append(pg)
assert len(island) == 1, len(island)
# 能登島の外接矩形内にある小さな離れ小島(文字を置く空きに残る点景)だけ除く。それ以外の輪郭は不変。
ib = box(*island[0].bounds)
polys = [pg for pg in polys if not (pg.area < 0.0005 and ib.contains(pg))]
land = unary_union(polys)
print("island centroid", island[0].centroid, "bounds", island[0].bounds)

def merc(lon, lat):
    return (math.radians(lon), math.log(math.tan(math.pi/4 + math.radians(lat)/2)))

def project(g, bounds, W):
    # bounds: lon0,lat0,lon1,lat1 -> SVG(W x H) 等角(メルカトル)
    x0, y0 = merc(bounds[0], bounds[1]); x1, y1 = merc(bounds[2], bounds[3])
    s = W / (x1 - x0); H = (y1 - y0) * s
    def p(lon, lat):
        x, y = merc(lon, lat); return ((x - x0) * s, (y1 - y) * s)
    def ring(r): return "M" + "L".join("%.2f,%.2f" % p(*c) for c in r.coords) + "Z"
    parts = []
    for pg in (g.geoms if hasattr(g, "geoms") else [g]):
        parts.append(ring(pg.exterior) + "".join(ring(i) for i in pg.interiors))
    return " ".join(parts), W, H, p

def title_paths(box_px, lines=("SIT BY ME",), xs=None, track=0.07, fill=1.0):
    from fontTools.ttLib import TTFont
    from fontTools.varLib import instancer
    from fontTools.pens.svgPathPen import SVGPathPen
    from fontTools.pens.transformPen import TransformPen
    import os
    f = instancer.instantiateVariableFont(TTFont(os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts", "Cinzel[wght].ttf")), {"wght": 700})
    gs, cmap, upm = f.getGlyphSet(), f.getBestCmap(), f["head"].unitsPerEm
    cap = f["OS/2"].sCapHeight
    bx0, by0, bx1, by1 = box_px
    W, H = bx1 - bx0, by1 - by0
    lh = H / len(lines)
    ch = lh * fill * 0.9              # 文字(キャップ)高さ
    sy = ch / cap
    if xs is None:  # 1行。字幅比 XS を決め、矩形幅(能登島の外接矩形の96%)に収まる最大の高さを求める
        XS = 0.5
        adv0 = sum(gs[cmap[ord(c)]].width for c in lines[0])
        Wt = W * 0.96
        ch = min(ch, Wt * 0.95 / (adv0 / cap * XS + track * (len(lines[0]) - 1)))
        sy = ch / cap
        xs = XS
        bx0 -= (Wt - W) / 2; W = Wt
    sx = sy * xs
    out = []
    for i, ln in enumerate(lines):
        adv = [gs[cmap[ord(c)]].width for c in ln]
        tw = sum(adv) * sx + track * ch * (len(ln) - 1)
        x = bx0 + (W - tw) / 2
        base = by0 + lh * i + (lh - ch) / 2 + ch
        for c, a in zip(ln, adv):
            pen = SVGPathPen(gs)
            gs[cmap[ord(c)]].draw(TransformPen(pen, (sx, 0, 0, -sy, x, base)))
            out.append(pen.getCommands())
            x += a * sx + track * ch
    print("title box", W, H, "line h", ch, "text w max", tw)
    return " ".join(out)

def build(name, bounds, W, eyes):
    clip = land.intersection(box(*bounds))
    d, W, H, p = project(clip, bounds, W)
    isl, _, _, _ = project(island[0].intersection(box(*bounds)), bounds, W)
    ex = ""
    for lon, lat, r in eyes:
        cx, cy = p(lon, lat)
        ex += f'<g transform="translate({cx:.1f},{cy:.1f}) rotate(-20)"><path d="M{-r},0 Q0,{-r*0.9} {r*1.3},{r*0.15} Q0,{r*0.5} {-r},0Z" fill="#e8eef5"/><ellipse cx="{r*0.2}" cy="{-r*0.05}" rx="{r*0.22}" ry="{r*0.4}" fill="#14213d"/></g>'
    ib = island[0].bounds
    a = p(ib[0], ib[3]); b = p(ib[2], ib[1])
    tp = title_paths((a[0], a[1], b[0], b[1]))
    ex += (f'<path d="{tp}" fill="#14213d" stroke="#14213d" stroke-width="7" stroke-linejoin="round"/>'
           f'<path d="{tp}" fill="#e8eef5"/>')
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.0f} {H:.0f}" width="{W:.0f}" height="{H:.0f}">'
           f'<path d="{d}" fill="#14213d" fill-rule="evenodd" stroke="#e8eef5" stroke-width="3" stroke-linejoin="round"/>{ex}</svg>')
    open(f"{out}/{name}.svg", "w").write(svg)
    print(name, W, H)

if __name__ == "__main__":
    import ast
    cfg = ast.literal_eval(open(sys.argv[3]).read()) if len(sys.argv) > 3 else {}
    for k, v in cfg.items():
        build(k, v["bounds"], v.get("W", 1600), v.get("eyes", []))
