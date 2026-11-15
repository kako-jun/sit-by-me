"""台帳（エリア・図配置・接続）から MAP グラフを組む。描画・検証スクリプト共通。"""
import ledger_yaml as LY
from collections import defaultdict


class Graph:
    def __init__(self, root):
        self.root = root
        area_rows = LY.read("エリア", root=root)
        placements = defaultdict(list)
        for r in LY.read("図配置", root=root):
            placements[r["エリアID"]].append(r)
        self.areas = []
        for area in area_rows:
            if area["エリアID"] not in placements:
                raise KeyError(area["エリアID"])
            rows = sorted(placements[area["エリアID"]], key=lambda r: int(r["順番"]))
            self.areas.append({"id": area["エリアID"], "name": area["名称"],
                               "maps": [r["MAP_ID"] for r in rows],
                               "layout": {r["MAP_ID"]: [int(r["X"]), int(r["Y"])] for r in rows}})
        self.edges = []
        for r in LY.read("接続", root=root):
            if r["種別"] not in ("edge", "door", "event", "oneway"):
                raise ValueError(f"invalid topology kind {r['種別']}")
            a, _, ap = r["端A"].partition(".")
            b, _, bp = r["端B"].partition(".")
            if "." not in r["端A"] or "." not in r["端B"]:
                raise ValueError("missing endpoint")
            self.edges.append({"from": a, "from_port": ap, "to": b, "to_port": bp, "kind": r["種別"],
                               "note": r["主路・状態"], "id": f"{r['端A']}>{r['端B']}:{r['種別']}"})

    def owner(self, id_):
        for a in self.areas:
            if id_ in a["maps"]:
                return a["id"]
        return None

    def internal(self, area):
        return [e for e in self.edges if e["from"] in area["maps"] and e["to"] in area["maps"]]

    def incident(self, area):
        return [e for e in self.edges if e["from"] in area["maps"] or e["to"] in area["maps"]]

    def cross(self):
        return [e for e in self.edges if self.owner(e["from"]) != self.owner(e["to"])]


def esc(s):
    """Ruby の CGI.escapeHTML と同じ（' は &#39;）。"""
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;").replace("'", "&#39;")
