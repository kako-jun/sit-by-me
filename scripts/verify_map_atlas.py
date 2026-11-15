import json
import os
import re
import sys
import xml.etree.ElementTree as ET

import ledger_yaml as LY
from map_graph import Graph


def assert_(condition, message):
    if not condition:
        raise RuntimeError(message)


def local(tag):
    return tag.rsplit("}", 1)[-1]


def document(root, relative):
    path = os.path.join(root, "docs/topology", relative)
    assert_(os.path.isfile(path), f"missing diagram {relative}")
    return ET.parse(path).getroot()


def elements(doc, attribute):
    return [n for n in doc.iter() if attribute in n.attrib]


def by_tag(doc, tag):
    return [n for n in doc.iter() if local(n.tag) == tag]


def check(root, file, nodes, edges, areas, references=None):
    doc = document(root, file)
    owned = [n.attrib["data-map"] for n in elements(doc, "data-map")]
    assert_(sorted(owned) == sorted(nodes), f"{file}: missing/extra owned MAP")
    labels = [(n.text or "").strip() for n in by_tag(doc, "text") if "id" in n.attrib.get("class", "").split()]
    for id_ in nodes:
        assert_(id_ in labels, f"{file}: visible ID label missing {id_}")
    area_ids = [n.attrib["data-area"] for n in elements(doc, "data-area")]
    assert_(sorted(area_ids) == sorted(areas), f"{file}: missing/extra area")
    paths = elements(doc, "data-edge-id")
    assert_(sorted(n.attrib["data-edge-id"] for n in paths) == sorted(e["id"] for e in edges), f"{file}: missing/extra canonical connection")
    expected = {e["id"]: e for e in edges}
    text_contents = [t.text or "" for t in by_tag(doc, "text")]
    markers = {n.attrib.get("id") for n in by_tag(doc, "marker")}
    for path in paths:
        e = expected[path.attrib["data-edge-id"]]
        assert_(local(path.tag) == "path", f"{file}: connection must be visible path")
        for key in ("from", "to", "from_port", "to_port", "kind"):
            attr = "data-" + key.replace("_", "-")
            assert_(path.attrib.get(attr) == e[key], f"{file}: corrupt {attr}")
        assert_(path.attrib.get("class") == e["kind"], f"{file}: wrong visible line kind")
        assert_(bool(path.attrib.get("d", "")), f"{file}: missing line geometry")
        if e["kind"] in ("event", "oneway"):
            m = re.fullmatch(r"url\(#([A-Za-z0-9_-]+)\)", path.attrib.get("marker-end", ""))
            assert_(m and m.group(1) in markers, f"{file}: directed event/travel needs end arrow")
            assert_("marker-start" not in path.attrib, f"{file}: reversed or bidirectional arrow")
        else:
            assert_("marker-end" not in path.attrib and "marker-start" not in path.attrib, f"{file}: ordinary passage must be bidirectional")
        connector = "→" if e["kind"] in ("event", "oneway") else "↔"
        caption = f'{e["from"]}.{e["from_port"]} {connector} {e["to"]}.{e["to_port"]}'
        assert_(any(caption in text for text in text_contents), f"{file}: missing visible endpoint caption")
    if references is not None:
        refs = [n.attrib["data-reference-map"] for n in elements(doc, "data-reference-map")]
        assert_(sorted(refs) == sorted(references), f"{file}: missing/extra remote MAP reference")
    return doc


def verify(root):
    g = Graph(root)
    all_ = [m for a in g.areas for m in a["maps"]]
    ids = [a["id"] for a in g.areas]
    with open(os.path.join(root, "docs/topology/map-ids.json"), encoding="utf-8") as f:
        expected_total = json.load(f)["expected_count"]
    assert_(len(all_) == expected_total and len(set(all_)) == expected_total, f"atlas membership must contain all {expected_total} MAPs exactly once")
    assert_(len(ids) == 15 and len(set(ids)) == 15, "atlas must cover all 15 areas")
    check(root, "atlas.svg", all_, g.edges, ids)
    check(root, "overview.svg", [], g.cross(), ids)
    areas_dir = os.path.join(root, "docs/topology/areas")
    actual_files = sorted(f[:-4] for f in os.listdir(areas_dir) if f.endswith(".svg")) if os.path.isdir(areas_dir) else []
    assert_(actual_files == sorted(ids), "missing/extra per-area SVG file")
    for area in g.areas:
        incident = g.incident(area)
        remote = list(dict.fromkeys(i for e in incident for i in (e["from"], e["to"]) if i not in area["maps"]))
        check(root, "areas/" + area["id"] + ".svg", area["maps"], incident, [area["id"]], remote)
    return True


if __name__ == "__main__":
    try:
        verify(LY.ROOT)
        g = Graph(LY.ROOT)
        print(f'PASS: full atlas {sum(len(a["maps"]) for a in g.areas)} MAPs / {len(g.edges)} connections, 15 areas, overview cross-area ports and directed events')
    except Exception as e:
        print(f"FAIL: atlas: {e}", file=sys.stderr)
        sys.exit(1)
