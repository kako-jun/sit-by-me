import os
import re

import ledger_yaml as LY
from map_graph import Graph, esc

ROOT = LY.ROOT
STYLE = 'text{font-family:-apple-system,BlinkMacSystemFont,"Hiragino Sans",sans-serif;fill:#263f4e}.node{fill:#fff;stroke:#527b69;stroke-width:3}.ref{fill:#fff7eb;stroke:#ad8456;stroke-width:2}.edge{fill:none;stroke:#527b69;stroke-width:3}.door{fill:none;stroke:#a16b42;stroke-width:3;stroke-dasharray:8 5}.event{fill:none;stroke:#ac4871;stroke-width:4;stroke-dasharray:6 5}.oneway{fill:none;stroke:#5262a8;stroke-width:4}.id{font-size:15px;font-weight:bold;text-anchor:middle}.label{font-size:16px;text-anchor:middle;paint-order:stroke;stroke:#fbfdfb;stroke-width:5;stroke-linejoin:round}.note{font-size:16px}.small{font-size:14px}.heading{font-size:25px;font-weight:bold}'
DIRECTED = ("event", "oneway")


def header(w, h, title):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img"><title>{esc(title)}</title><defs><marker id="directed-arrow" markerWidth="9" markerHeight="9" refX="8" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8 Z" fill="#8b4c83"/></marker></defs><style>{STYLE}</style><rect width="{w}" height="{h}" fill="#edf3f1"/>'


def attrs(e, canonical=True):
    key = "data-edge-id" if canonical else "data-reference-edge-id"
    return f'{key}="{esc(e["id"])}" data-kind="{e["kind"]}" data-from="{e["from"]}" data-to="{e["to"]}" data-from-port="{e["from_port"]}" data-to-port="{e["to_port"]}"'


def arrow(e):
    return ' marker-end="url(#directed-arrow)"' if e["kind"] in DIRECTED else ""


def port_label(e):
    return f'{e["from"]}.{e["from_port"]} {"→" if e["kind"] in DIRECTED else "↔"} {e["to"]}.{e["to_port"]}'


def node_label(id_, spec):
    text = spec.get(id_, id_)
    return [text[i:i + 12] for i in range(0, len(text), 12)][:3]


def area_content(g, area, spec, canonical_cross=True):
    coords = area["layout"]
    xs = [c[0] for c in coords.values()]
    ys = [c[1] for c in coords.values()]
    minx, miny = min(xs), min(ys)
    w = max(max(xs) - minx + (520 if area["id"] == "overseas" else 280), 1100)
    positions = {k: [x - minx + 140, y - miny + 160] for k, (x, y) in coords.items()}
    diagram_bottom = max(ys) - miny + 285
    incident = g.incident(area)
    h = diagram_bottom + len(incident) * 42 + 130
    if area["id"] in ("garden", "castle"):
        north = "北↑・接続概念図（縮尺ではない）"
    elif area["id"] == "body":
        north = "架空人体の空間配置・地理的方位ではない"
    elif area["id"] == "overseas":
        north = "階層と移動の概念図・地理的方位ではない"
    else:
        north = "接続模式図・地理的方位／縮尺を表さない"
    out = [f'<g data-area="{area["id"]}"><rect x="8" y="8" width="{w - 16}" height="{h - 16}" rx="12" fill="#fbfdfb" stroke="#8aa79a"/><text x="25" y="45" class="heading">{esc(area["name"])}・{len(area["maps"])}MAP</text><text x="25" y="78" class="note">{esc(north)}</text>']
    if area["id"] == "city":
        out.append('<text x="25" y="108" class="note">デパート5階（KRB-02・KRB-03・KRB-04・KRB-05・KRB-06）のエレベーターはMAPを持たず、特殊遷移表の「階選択遷移」。各階の扉に入るとウィンドウで階を選び、選んだ階の扉前に着く。</text>')
        out.append('<text x="25" y="134" class="note">箱は全階を結ぶので階をつなぐ線は描かない。4階KRB-05は条件つき。</text>')
    counts = {}
    for e in g.internal(area):
        ax, ay = positions[e["from"]]
        bx, by = positions[e["to"]]
        pair = tuple(sorted([e["from"], e["to"]]))
        ix = counts.get(pair, 0)
        counts[pair] = ix + 1
        # Separate the otter/cave entrance and exit, preserving their endpoint identities.
        if any(i in pair for i in ("SNL-07", "SNL-08")):
            d = f'M{ax} {ay} Q{(ax + bx) // 2} {(ay + by) // 2 + (-65 if ix == 0 else 65)} {bx} {by}'
        else:
            d = f"M{ax} {ay} L{bx} {by}"
        out.append(f'<path class="{e["kind"]}" {attrs(e)} d="{d}"{arrow(e)}/>')
    for id_ in area["maps"]:
        x, y = positions[id_]
        out.append(f'<circle class="node" data-map="{id_}" cx="{x}" cy="{y}" r="34"/><text class="id" x="{x}" y="{y + 5}">{id_}</text>')
        if area["id"] == "overseas" and id_ == "OVS-15":
            out.append(f'<text x="{x}" y="{y - 48}" class="label">空中通路・シャー共闘</text>')
        elif area["id"] == "overseas" and id_ in ("OVS-01", "OVS-02", "OVS-03"):
            for i, line in enumerate(node_label(id_, spec)):
                out.append(f'<text x="{x}" y="{y + 53 + i * 21}" class="label">{esc(line)}</text>')
        elif area["id"] == "overseas":
            for i, line in enumerate(node_label(id_, spec)):
                out.append(f'<text x="{x + 65}" y="{y - 8 + i * 21}" class="label" style="text-anchor:start">{esc(line)}</text>')
        else:
            label_y = y - 42 if id_ == "BDY-01" else y + 53
            label_x = x + 75 if id_ == "BDY-13" else x
            for i, line in enumerate(node_label(id_, spec)):
                out.append(f'<text x="{label_x}" y="{label_y + i * 21}" class="label">{esc(line)}</text>')
    out.append(f'<text x="25" y="{diagram_bottom}" class="note">全接続口（各行は上のMAP IDを参照。外部は隣接エリア名と到着口を明記）</text>')
    referenced = []
    for i, e in enumerate(incident):
        y = diagram_bottom + 35 + i * 42
        external = g.owner(e["from"]) != g.owner(e["to"])
        if external:
            peer = e["to"] if e["from"] in area["maps"] else e["from"]
            if peer not in referenced:
                out.append(f'<circle class="ref" data-reference-map="{peer}" data-reference="{peer}" cx="40" cy="{y - 5}" r="13"/>')
                referenced.append(peer)
            out.append(f'<text x="65" y="{y}" class="small">{esc(port_label(e))}  [外部: {esc(g.owner(peer))}]</text>')
            out.append(f'<path class="{e["kind"]}" {attrs(e, canonical_cross)} d="M{w - 160} {y - 7} L{w - 45} {y - 7}"{arrow(e)}/>')
        else:
            out.append(f'<text x="25" y="{y}" class="small">{esc(port_label(e))}</text>')
    out.append("</g>")
    return "\n".join(out), w, h


def write(path, text):
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)


def run():
    g = Graph(ROOT)
    spec = {r["MAP_ID"]: r["一言特徴"] for r in LY.read("MAP仕様") if re.fullmatch(r"[A-Z]{3}-\d{2}", r["MAP_ID"])}
    folder = os.path.join(ROOT, "docs/topology/areas")
    os.makedirs(folder, exist_ok=True)
    panels = []
    for area in g.areas:
        content, w, h = area_content(g, area, spec)
        write(os.path.join(folder, area["id"] + ".svg"), header(w, h, area["name"]) + content + "</svg>")
        content, w, h = area_content(g, area, spec, canonical_cross=False)
        panels.append((area, content, w, h))
    total = sum(len(a["maps"]) for a in g.areas)
    cross = g.cross()
    col_width = max(p[2] for p in panels) + 30
    rows = [panels[i:i + 3] for i in range(0, len(panels), 3)]
    row_heights = [max(p[3] for p in row) + 30 for row in rows]
    atlas_h = 150 + sum(row_heights) + len(cross) * 55 + 100
    atlas = [header(col_width * 3, atlas_h, f"全{total}MAP・全接続アトラス"), f'<text x="30" y="45" class="heading">全{total}MAP接続アトラス：所有MAPは各1回、外部口と全接続を併記</text>', '<text x="30" y="85" class="note">各枠は独立した模式図。庭園・城は北上、ほかは注記に従う。詳細はareas/各エリア.svgを等倍表示。</text>']
    y = 120
    for ri, row in enumerate(rows):
        for ci, p in enumerate(row):
            atlas.append(f'<g transform="translate({ci * col_width} {y})">{p[1]}</g>')
        y += row_heights[ri]
    atlas.append(f'<text x="30" y="{y + 35}" class="heading">エリア間の全接続（{len(cross)}件）：一方向は矢印、双方向は↔</text>')
    for i, e in enumerate(cross):
        ey = y + 85 + i * 55
        atlas.append(f'<text x="30" y="{ey}" class="note">{esc(g.owner(e["from"]))} / {esc(port_label(e))} / {esc(g.owner(e["to"]))}</text><path class="{e["kind"]}" {attrs(e)} d="M1400 {ey - 8} L1600 {ey - 8}"{arrow(e)}/>')
    atlas.append("</svg>")
    write(os.path.join(ROOT, "docs/topology/atlas.svg"), "\n".join(atlas))
    overview(g)
    print(f"Rendered overview, atlas and {len(g.areas)} area diagrams: {total} maps, {len(g.edges)} connections")


def overview(g):
    # Real-region positions follow the established geography. Fiction/event layers are separate.
    pos = {'teramachi': [390, 1070], 'school': [650, 1160], 'city': [650, 740], 'station': [430, 430], 'mountain': [1150, 450], 'sunnyland': [1480, 310], 'uchinada': [260, 150], 'noto_train': [1400, 120], 'noto_before': [1730, 150], 'noto_after': [1730, 650], 'garden': [1190, 980], 'castle': [1190, 760], 'body': [1710, 1300], 'airport': [410, 1600], 'overseas': [1110, 1600]}
    cross = g.cross()
    list_y = 1800
    h = list_y + len(cross) * 58 + 100
    out = [header(2050, h, "全エリア間の位置関係と接続"), '<text x="30" y="45" class="heading">全15エリアの位置関係と全接続</text>', '<text x="30" y="83" class="note">北↑（実在地域の相対配置）。距離・縮尺は模式化。下段の空港境界・海外・体内は地理配置から分離。</text>', '<rect x="80" y="100" width="1910" height="1110" rx="15" fill="#f9fcfa" stroke="#a4b9ae"/><rect x="80" y="1230" width="1910" height="490" rx="15" fill="#fff8f0" stroke="#b9a38e"/><text x="100" y="1260" class="note">非地理のイベント層／所在・方角を固定しない空港境界と海外</text>']
    for e in cross:
        ax, ay = pos[g.owner(e["from"])]
        bx, by = pos[g.owner(e["to"])]
        d = "M390 1070 L930 1070 L1560 1170 L1710 1300" if e["kind"] == "event" else f"M{ax} {ay} L{bx} {by}"
        out.append(f'<path class="{e["kind"]}" {attrs(e, False)} d="{d}"{arrow(e)}/>')
    out.append('<text x="850" y="1047" class="label">TRM-03園庭（境内の右の区画） → BDY-01口（物語イベント）</text>')
    for a in g.areas:
        x, y = pos[a["id"]]
        out.append(f'<g data-area="{a["id"]}"><rect x="{x - 145}" y="{y - 44}" width="290" height="88" rx="10" fill="#fff" stroke="#527b69" stroke-width="3"/><text x="{x}" y="{y - 8}" class="label">{esc(a["name"])}</text><text x="{x}" y="{y + 21}" class="label">{len(a["maps"])} MAP（{a["id"]}）</text></g>')
    out.append('<text x="100" y="1305" class="note">奥能登被災前／後は時期差分（徒歩接続ではない）。未登録の接続を補って描かない。</text><text x="100" y="1340" class="note">K空港はワープ到達・起点を固定しない。体内は園庭のイベントから、海外へは一方向の旅客機。</text>')
    out.append(f'<text x="30" y="1765" class="heading">エリアをまたぐ全{len(cross)}接続の出入口（線の交差は乗換・接続を意味しない）</text>')
    for i, e in enumerate(cross):
        y = list_y + i * 58
        out.append(f'<text x="30" y="{y}" class="note">{esc(g.owner(e["from"]))} / {esc(port_label(e))} / {esc(g.owner(e["to"]))}</text><path class="{e["kind"]}" {attrs(e)} d="M1550 {y - 7} L1790 {y - 7}"{arrow(e)}/>')
    out.append("</svg>")
    write(os.path.join(ROOT, "docs/topology/overview.svg"), "\n".join(out))


if __name__ == "__main__":
    run()
