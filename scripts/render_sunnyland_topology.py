import os

import ledger_yaml as LY
from map_graph import esc

root = LY.ROOT
maps = [row for row in LY.read("MAP") if row["エリアID"] == "sunnyland"]
map_ids = [row["MAP_ID"] for row in maps]
expected_ids = [f"SNL-{i:02d}" for i in range(1, 13)]
if sorted(map_ids) != sorted(expected_ids):
    raise RuntimeError(f"sunnyland MAP ledger mismatch: {map_ids!r}")
specified_ids = [r["MAP_ID"] for r in LY.read("MAP仕様")]
if any(i not in specified_ids for i in expected_ids):
    raise RuntimeError("MAP仕様.yaml lacks one or more sunnyland MAP IDs")

edges = []
for row in LY.read("接続"):
    a, b, kind = row["端A"], row["端B"], row["種別"]
    if kind not in ("door", "edge"):
        continue
    if not (a.split(".", 1)[0].startswith("SNL-") and b.split(".", 1)[0].startswith("SNL-")):
        continue
    edges.append([a.split(".", 1)[0], a.split(".", 1)[-1], b.split(".", 1)[0], b.split(".", 1)[-1], kind])
nodes = {'SNL-01': [140, 290, '入口1F・受付'], 'SNL-02': [360, 290, '下り廊下・前半'], 'SNL-04': [590, 290, '下り廊下・後半'], 'SNL-05': [820, 290, '地下水族館'], 'SNL-06': [1080, 420, '小さな屋外・シャチホコ'], 'SNL-09': [1080, 680, '狭い昭和の屋外動物園'], 'SNL-10': [820, 680, '創作の屋外階段'], 'SNL-11': [590, 680, '和室の宿泊棟'], 'SNL-12': [140, 680, '入口2F・全方向の窓'], 'SNL-03': [360, 440, '途中右のゲームセンター'], 'SNL-07': [1320, 245, 'ラッコ館・任意宝箱'], 'SNL-08': [1320, 580, '海底洞窟・任意宝箱']}
if len(edges) != 14:
    raise RuntimeError(f"sunnyland connection ledger mismatch: {len(edges)}")
svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="1540" height="880" viewBox="0 0 1540 880" role="img" aria-labelledby="title desc">', '<title id="title">サニーランド双方向円環</title><desc id="desc">入口1階から廊下と地下水族館、屋外空間、動物園、創作の階段、宿泊棟、入口2階へ巡る。任意施設は入口出口別。方位や正確な勾配の図ではない。</desc>', '<style>text{font-family:-apple-system,BlinkMacSystemFont,"Hiragino Sans",sans-serif;fill:#233a47}.door{fill:none;stroke:#a45f30;stroke-width:4;stroke-dasharray:9 6}.node{fill:white;stroke:#467260;stroke-width:3}.label{font-size:17px;text-anchor:middle}.note{font-size:18px}.id{font-size:15px;font-weight:bold;text-anchor:middle}</style>', '<rect width="1540" height="880" fill="#edf3f1"/><text x="35" y="45" font-size="30" font-weight="bold">サニーランド：最初から両方向に進める円環・12MAP</text>', '<text x="35" y="85" class="note">概念図：紙面の上下＝階高や南北ではない。下り廊下は約2MAP、周囲は雪の森。ゲームセンターの右は下降時の進行基準。</text>', '<text x="35" y="122" class="note">入口棟は八角形。水族館出口付近＝ピラルク巨大水槽／壁際＝サメ・クジラの陰茎標本。</text>']
seen = {}
for a, ap, b, bp, kind in edges:
    if a not in nodes or b not in nodes:
        continue
    ax, ay = nodes[a][:2]
    bx, by = nodes[b][:2]
    pair = tuple(sorted([a, b]))
    index = seen.get(pair, 0)
    seen[pair] = index + 1
    if pair in (("SNL-06", "SNL-07"), ("SNL-06", "SNL-08")):
        midx = (ax + bx) // 2
        midy = (ay + by) // 2 + (-70 if index == 0 else 70)
        d = f"M{ax} {ay} Q{midx} {midy} {bx} {by}"
    else:
        d = f"M{ax} {ay} L{bx} {by}"
    svg.append(f'<path class="{kind}" d="{d}" data-from="{a}" data-to="{b}" data-from-port="{ap}" data-to-port="{bp}"/>')
for id_, (x, y, label) in nodes.items():
    svg.append(f'<circle class="node" data-map="{id_}" cx="{x}" cy="{y}" r="34"/><text class="id" x="{x}" y="{y + 5}">{id_}</text><text class="label" x="{x}" y="{y + 63}">{esc(label)}</text>')
svg += ['<text x="35" y="790" class="note">入口1F→水族館側と入口2F→宿泊棟側の2経路。動物園→屋外階段→宿泊棟端はユーザー創作。</text>', '<text x="35" y="825" class="note">ラッコ館・洞窟は入口と出口別、主円環には不要。同じ屋外空間の別扉へ戻すのはゲーム配置の採用。</text>', '<text x="35" y="858" class="note">洞窟＝低予算昭和の海底探検の作り物（ダイオウイカ・難破船・ニンゲン）。画像・mask未生成、階内経路／幅TBD。</text>', '</svg>']
with open(os.path.join(root, "docs/topology/sunnyland.svg"), "w", encoding="utf-8", newline="") as f:
    f.write("\n".join(svg) + "\n")
print("Rendered docs/topology/sunnyland.svg from YAML ledger")
