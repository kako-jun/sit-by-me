"""斜め視点モック（平面図スペックJSON → 斜めの射影で描いた PNG / マスク）。画像生成AIは使わない。

視点は採用済み4枚の測定値（見下ろし約42度・側辺の開き約10度・奥幅/手前幅0.835・土台前面35px・出力1672x941）。
平面は土台の天面 1600 x 1270 の単位（平面単位）。1キャラ=66平面単位（土台の手前縁で約67px）、出入口は2人分=132。
スペックの形は docs/production/oblique-mocks/*-plan.json（schema `sit-oblique-plan/1`）。

使い方:
  uv run --with numpy --with opencv-python-headless --with pillow python3 -I oblique_mock.py \
      PLAN.json --out DIR [--variant kids]
  出力: <id>-clean.png（ラベルなし・imagegen 編集元）・<id>-review.png（ラベル付き）・
        <id>-mask.png（床=白・blocked=黒）・<id>-exits.png（出口を着色）・<id>-mask.json（出口の範囲）
"""
import argparse
import copy
import json
import os
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H_IMG = 1672, 941
BASE_W, BASE_D = 1600, 1270
CHAR = 66
DOOR_W = 2 * CHAR
WIDTH_CLASSES = {"2people": 2 * CHAR, "1.5people": 100, "1person": CHAR}  # 戸口の幅の区分（既定=2人分。勝手口だけ1人分）


def door_w(d):
    return WIDTH_CLASSES.get(d.get("width_class", "2people"), DOOR_W)


FLOOR_SURFACES = ("water", "stairs")  # 床の面種別（任意）。water=水路（歩けない・斜線で描く）、stairs=石段（段の線で描く）

DOOR_H = 2 * CHAR
KV = 0.74  # cos(42度)
SLAB = 35
_SRC = np.float32([[0, 0], [BASE_W, 0], [BASE_W, BASE_D], [0, BASE_D]])
_DST = np.float32([[165, 55], [1525, 55], [1650, 850], [22, 850]])
HM = cv2.getPerspectiveTransform(_SRC, _DST)
HI = np.linalg.inv(HM)
FONT = "/usr/share/fonts/noto-cjk/NotoSansCJK-Medium.ttc"
DOOR_COLOR = "#ff2fa0"
OPEN_COLOR = "#2ee06a"  # 開口（通れる所）=明るい緑。仕切り=濃い灰。戸口=ピンク


def proj(x, y, z=0.0):
    p = HM @ np.array([x, y, 1.0])
    u, v = p[0] / p[2], p[1] / p[2]
    if z:
        a = HM @ np.array([0.0, y, 1.0])
        b = HM @ np.array([1.0, y, 1.0])
        sx = abs(b[0] / b[2] - a[0] / a[2])
        v -= z * sx * KV
    return (float(u), float(v))


def unproj(u, v):
    p = HI @ np.array([u, v, 1.0])
    return (float(p[0] / p[2]), float(p[1] / p[2]))


def sx_at(y):
    a, b = proj(0, y), proj(1, y)
    return b[0] - a[0]


# ---------------------------------------------------------------- スペック
def load_plan(path, variant=None):
    with open(path, encoding="utf-8") as f:
        p = json.load(f)
    if p.get("schema") != "sit-oblique-plan/1":
        sys.exit("schema が sit-oblique-plan/1 ではない")
    p.setdefault("floors", []); p.setdefault("walls", []); p.setdefault("doors", [])
    p.setdefault("openings", []); p.setdefault("boxes", []); p.setdefault("markers", []); p.setdefault("windows", []); p.setdefault("paths", []); p.setdefault("annotations", [])
    p["variant"] = None
    for f in p["floors"]:  # 床は rect か poly（平面の多角形。斜めの道・水路用）。poly は外接矩形を rect に入れる（検証・他の処理は rect を使う）
        if f.get("poly"):
            xs = [q[0] for q in f["poly"]]; ys = [q[1] for q in f["poly"]]
            f["rect"] = [min(xs), min(ys), max(xs), max(ys)]
    if variant:
        v = p.get("variants", {}).get(variant)
        if v is None:
            sys.exit(f"variant {variant} が無い")
        p = copy.deepcopy(p)
        rm = set(v.get("remove", []))
        for k in ("floors", "walls", "doors", "openings", "boxes", "markers", "windows", "annotations"):
            p[k] = [e for e in p[k] if e["id"] not in rm]
            p[k] += v.get("add", {}).get(k, [])
        p["name"] = v.get("name", p["name"]); p["subtitle"] = v.get("subtitle", p.get("subtitle", ""))
        p["assumptions"] = p.get("assumptions", []) + v.get("assumptions", [])
        p["variant"] = variant
        p["map_id"] = p["map_id"] + "-" + variant
    p.pop("variants", None)
    return p


def wall_by_id(p, wid):
    for w in p["walls"]:
        if w["id"] == wid:
            return w
    sys.exit(f"wall {wid} が無い")


def is_h(w):
    r = w["rect"]
    return (r[2] - r[0]) >= (r[3] - r[1])


def visible_face_x(w):
    r = w["rect"]
    return r[2] if (r[0] + r[2]) / 2 <= BASE_W / 2 else r[0]


def span(d):
    return d["center"] - door_w(d) / 2, d["center"] + door_w(d) / 2


def door_geom(p, d):
    """扉の平面での範囲 patch（地面の着色範囲）、パネル四角（画像）、アンカー（画像）を返す。"""
    w = wall_by_id(p, d["wall"])
    r = w["rect"]
    a, b = span(d)
    if is_h(w):
        # 歩く側は壁の高さの約1.4倍まで伸ばす（手前の壁が隠す床の帯を越えて、見える床とつなぐ）
        dw = max(60, w["h"] * 1.4)
        n_, s_ = (dw if d.get("face") == "north" else 60), (dw if d.get("face") == "south" else 60)
        patch = [a, r[1] - n_, b, r[3] + s_]
        y = r[3]
        panel = [proj(a, y), proj(b, y), proj(b, y, DOOR_H), proj(a, y, DOOR_H)]
        anchor = proj(d["center"], y)
    else:
        patch = [r[0] - 60, a, r[2] + 60, b]
        x = visible_face_x(w)
        panel = [proj(x, a), proj(x, b), proj(x, b, DOOR_H), proj(x, a, DOOR_H)]
        anchor = proj(x, d["center"])
    return patch, panel, anchor


WINDOW_KINDS = {"floor": "掃き出し窓（床まで届く引き違い・扉ではない）", "waist": "腰高窓"}


def window_geom(p, win, hs=1.0):
    """窓のガラス四角（画像）と中心の画像点。壁の見える面（横壁=南向きの y1 面・縦壁=中央側の面）に描く。"""
    w = wall_by_id(p, win["wall"])
    r = w["rect"]
    a, b = win["center"] - win["width"] / 2, win["center"] + win["width"] / 2
    z0, z1 = win["sill"] * hs, (win["sill"] + win["height"]) * hs
    if is_h(w):
        y = r[3]
        q = [proj(a, y, z0), proj(b, y, z0), proj(b, y, z1), proj(a, y, z1)]
    else:
        x = visible_face_x(w)
        q = [proj(x, a, z0), proj(x, b, z0), proj(x, b, z1), proj(x, a, z1)]
    return q


def rect_poly(rc, z=0.0):
    x0, y0, x1, y1 = rc
    return [proj(x0, y0, z), proj(x1, y0, z), proj(x1, y1, z), proj(x0, y1, z)]


def floor_poly(f):
    """床の平面の多角形（poly があればそれ、無ければ rect の四隅）。"""
    if f.get("poly"):
        return [tuple(q) for q in f["poly"]]
    x0, y0, x1, y1 = f["rect"]
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def floor_img_poly(f):
    return [proj(x, y) for x, y in floor_poly(f)]


def marker_w(m):
    return m.get("width", DOOR_W)  # 端の出入口の幅（平面単位）。既定=キャラ2人分。広い道・狭い道は plan の markers[].width で指定する


def marker_rect(m):
    c = m["at"]
    h = marker_w(m) / 2
    if m["edge"] == "south":
        return [c - h, BASE_D - 70, c + h, BASE_D]
    if m["edge"] == "east":
        return [BASE_W - 70, c - h, BASE_W, c + h]
    if m["edge"] == "west":
        return [0, c - h, 70, c + h]
    return [c - h, 0, c + h, 70]


# ---------------------------------------------------------------- 描画要素
def shade(hexc, f):
    c = hexc.lstrip("#")
    r, g, b = int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)
    return "#%02x%02x%02x" % tuple(max(0, min(255, int(v * f))) for v in (r, g, b))


def box_polys(rc, h, color, top=None, z0=0.0):
    x0, y0, x1, y1 = rc
    sidex = x1 if (x0 + x1) / 2 <= BASE_W / 2 else x0
    side = [proj(sidex, y0, z0), proj(sidex, y1, z0), proj(sidex, y1, h), proj(sidex, y0, h)]
    front = [proj(x0, y1, z0), proj(x1, y1, z0), proj(x1, y1, h), proj(x0, y1, h)]
    topp = rect_poly(rc, h)
    return [(side, shade(color, 0.65), "side"), (front, shade(color, 0.85), "front"), (topp, top or shade(color, 1.12), "top")]


def opening_cuts(p, w):
    cuts = []
    for o in p["openings"] + [d for d in p["doors"] if d.get("passage")]:
        if o["wall"] == w["id"]:
            cuts.append(span(o))  # 開口・passage の戸口は壁面を抜く（梁・鴨居・垂れ壁を描かない）
    return cuts


def wall_pieces(p, w):
    """壁を描画用の箱に分ける。縦壁は100単位ごと。開口の範囲は抜く。"""
    r = w["rect"]
    cuts = opening_cuts(p, w)
    if is_h(w):
        axis0, axis1 = r[0], r[2]
    else:
        axis0, axis1 = r[1], r[3]
    pts = sorted({axis0, axis1, *[c for cut in cuts for c in cut]})
    if not is_h(w):
        k = axis0
        while k < axis1:
            pts.append(k); k += 100
        pts = sorted(set(pts))
    out = []
    for s, e in zip(pts[:-1], pts[1:]):
        mid = (s + e) / 2
        if any(a <= mid <= b for a, b in cuts):
            continue
        out.append([s, r[1], e, r[3]] if is_h(w) else [r[0], s, r[2], e])
    return out


def build_items(p, style):
    """(key, tag, polys, meta) のリスト。painter 法で key 昇順に描く。"""
    wire = style == "wire"
    hs = 0.4 if wire else 1.0
    bs = 0.6 if wire else 1.0
    items = []
    for f in p["floors"]:
        items.append((-1000, "floor", [(floor_img_poly(f), f["color"], "floor")], f))
    for o in p["openings"]:
        w = wall_by_id(p, o["wall"])
        r = w["rect"]
        a, b = span(o)
        rc = [a, r[1] - 2, b, r[3] + 2] if is_h(w) else [r[0] - 2, a, r[2] + 2, b]
        items.append((-450, "opening", [(rect_poly(rc), OPEN_COLOR, "opening")], o))
    for d in p["doors"]:
        patch, panel, anchor = door_geom(p, d)
        items.append((-450, "doorpatch", [(rect_poly(patch), "#ff9bd0", "doorpatch")], d))
        if d.get("passage"):
            w_ = wall_by_id(p, d["wall"]); r_ = w_["rect"]; a_, b_ = span(d)
            rc_ = [a_, r_[1] - 2, b_, r_[3] + 2] if is_h(w_) else [r_[0] - 2, a_, r_[2] + 2, b_]
            items.append((-440, "opening", [(rect_poly(rc_), OPEN_COLOR, "opening")], d))
    for m in p["markers"]:
        items.append((-450, "marker", [(rect_poly(marker_rect(m)), DOOR_COLOR, "marker")], m))
    for w in p["walls"]:
        kind = w.get("kind", "wall")
        color = w.get("color") or ("#4a4f57" if kind == "partition" else "#cdb98f" if kind == "fence" else "#9a9a96" if kind == "retaining" else "#d8c9a6")
        top = w.get("top_color") or ("#262a30" if kind == "partition" else None)
        h = w["h"] * hs
        if kind == "roof-passage":
            # 渡り廊下: 床（石）＋四隅の柱＋屋根の板だけ。壁・窓は無い開放した通路
            r = w["rect"]
            items.append((-450, "floor", [(rect_poly(r), "#b07a45", "floor")], {"id": w["id"] + "-floor", "walkable": False, "label": ""}))
            ps = 16
            for rc in ([r[0], r[1], r[0] + ps, r[1] + ps], [r[2] - ps, r[1], r[2], r[1] + ps], [r[0], r[3] - ps, r[0] + ps, r[3]], [r[2] - ps, r[3] - ps, r[2], r[3]]):
                items.append((rc[3] - 0.5, "wall", box_polys(rc, h - 12 * hs, "#7a5a3a"), w))
            items.append((r[3], "wall", box_polys(r, h, "#6c7077", w.get("top_color"), z0=h - 12 * hs), w))
            continue
        for rc in wall_pieces(p, w):
            items.append((rc[3], "wall", box_polys(rc, h, color, top), w))
    for b in p["boxes"]:
        items.append(((-500 + b["rect"][3] / 10000.0) if b["h"] < 20 else b["rect"][3], "box", box_polys(b["rect"], b["h"] * bs, b["color"]), b))
    for wn in p["windows"]:
        w = wall_by_id(p, wn["wall"])
        items.append((w["rect"][3] + 0.1, "window", [(window_geom(p, wn, hs), "#a9d6ee", "window")], wn))
    for d in p["doors"]:
        if d.get("passage"):
            continue
        patch, panel, anchor = door_geom(p, d)
        w = wall_by_id(p, d["wall"])
        key = w["rect"][3] + 0.2 if is_h(w) else w["rect"][3] + 0.2
        items.append((key, "door", [(panel, DOOR_COLOR, "door")], d))
    return sorted(items, key=lambda t: t[0])


# ---------------------------------------------------------------- 描画
def font(sz):
    return ImageFont.truetype(FONT, sz)


def table_bg(d, wire):
    if wire:
        return
    d.rectangle([0, 0, W, H_IMG], fill="#9a5f2f")
    rng = np.random.RandomState(7)
    y = 0
    while y < H_IMG:
        hh = int(rng.randint(48, 78))
        tone = int(rng.randint(-10, 10))
        d.rectangle([0, y, W, y + hh], fill=(150 + tone, 92 + tone, 46 + tone))
        d.line([(0, y), (W, y)], fill="#6e4220", width=2)
        y += hh


def draw_slab(d, wire, props=True):
    tl, tr, br, bl = [tuple(map(float, q)) for q in _DST]
    top = [tl, tr, br, bl]
    front = [bl, br, (br[0], br[1] + SLAB), (bl[0], bl[1] + SLAB)]
    if wire:
        d.polygon(top, fill="#ffffff", outline="#000000"); d.polygon(front, fill="#ffffff", outline="#000000")
        return
    d.polygon(front, fill="#b98a4e", outline="#6e4a22")
    d.line([(bl[0], bl[1] + 8), (br[0], br[1] + 8)], fill="#a07238", width=3)
    d.polygon(top, fill="#f3f7fb")
    if props:
        # 机の上の小物は手前に固定（マステ4・糊4）
        for x in (330, 640, 1040, 1520):
            d.rectangle([x, 862, x + 70, 890], fill="#e2c78e", outline="#9a7a3a")
        for x in (120, 520, 1260, 1590):
            d.ellipse([x, 872, x + 16, 906], fill="#f6f6f6", outline="#cccccc")


def center_of(poly):
    xs = [q[0] for q in poly]; ys = [q[1] for q in poly]
    return sum(xs) / len(xs), sum(ys) / len(ys)


def dashed(d, p1, p2, fill, width, dash=14):
    x0, y0 = p1; x1, y1 = p2
    L = max(1.0, ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5)
    n = int(L // dash)
    for i in range(0, n, 2):
        a = i / n; b = min(1.0, (i + 1) / n)
        d.line([(x0 + (x1 - x0) * a, y0 + (y1 - y0) * a), (x0 + (x1 - x0) * b, y0 + (y1 - y0) * b)], fill=fill, width=width)


def decorate_surface(img, f, wire, ss):
    """床の面種別の描き分け。water=斜線（水面）、stairs=段の線（石段。平面で y 一定の線を射影）。多角形の内側だけに引く。"""
    surf = f.get("surface")
    if surf not in FLOOR_SURFACES:
        return
    from PIL import ImageChops
    poly = [(u * ss, v * ss) for u, v in floor_img_poly(f)]
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).polygon(poly, fill=255)
    layer = Image.new("L", img.size, 0)
    ld = ImageDraw.Draw(layer)
    x0, y0, x1, y1 = f["rect"]
    if surf == "water":
        step = 16 * ss
        for k in range(-img.size[1], img.size[0], step):
            ld.line([(k, 0), (k + img.size[1], img.size[1])], fill=255, width=max(1, int(2 * ss * (1.0 if wire else 0.6))))
        col = "#000000" if wire else "#a9d0ec"
    else:
        yy = y0 + 12
        while yy < y1:
            a, b = proj(x0, yy), proj(x1, yy)
            ld.line([(a[0] * ss, a[1] * ss), (b[0] * ss, b[1] * ss)], fill=255, width=max(1, int(2 * ss)))
            yy += 24
        col = "#000000" if wire else "#6e6a62"
    layer = ImageChops.multiply(layer, mask)
    img.paste(col, mask=layer)


def render(p, style="color", labels=False, ss=2):
    """style: color | wire。戻り値 (PIL RGB 画像 W x H_IMG, アンカー辞書 {door_id: (x, y)})。"""
    wire = style == "wire"
    img = Image.new("RGB", (W * ss, H_IMG * ss), "#ffffff")
    d = ImageDraw.Draw(img)

    class S:  # 座標を ss 倍して描く薄いラッパ
        def polygon(self, pts, fill=None, outline=None, width=1):
            d.polygon([(a * ss, b * ss) for a, b in pts], fill=fill)
            if outline:
                d.line([(a * ss, b * ss) for a, b in list(pts) + [pts[0]]], fill=outline, width=max(1, int(width * ss)))
        def line(self, pts, fill, width):
            d.line([(a * ss, b * ss) for a, b in pts], fill=fill, width=int(width * ss))
        def rectangle(self, bb, fill=None, outline=None):
            d.rectangle([v * ss for v in bb], fill=fill, outline=outline)
        def ellipse(self, bb, fill=None, outline=None):
            d.ellipse([v * ss for v in bb], fill=fill, outline=outline)
    s = S()
    table_bg(s, wire)
    draw_slab(s, wire, props=not wire)
    items = build_items(p, style)
    outline = "#000000" if wire else None
    lw = 2.0 if wire else 1
    blocked_gray = "#cfcfcf"
    for key, tag, polys, meta in items:
        for pts, col, role in polys:
            fill = col
            ol = outline
            if wire:
                fill = "#ffffff"
                if role == "floor":
                    fill = "#ffffff" if meta.get("walkable", True) else "#e4e4e4"
                    ol = "#000000"
                    lwx = 1.2
                elif role == "opening":
                    fill = "#ffffff"; ol = None
                elif role in ("doorpatch",):
                    fill = "#ffffff"; ol = None
                elif role == "marker":
                    fill = "#000000"; ol = None
                elif role == "door":
                    fill = "#000000"
                elif role == "window":
                    fill = "#ffffff"
                elif tag == "box":
                    fill = blocked_gray if role == "top" else "#ffffff"
                elif tag == "wall" and meta.get("kind") == "partition":
                    fill = "#555555" if role == "top" else "#ffffff"
                elif tag == "wall" and role == "top":
                    fill = "#ffffff"
            else:
                if role == "window":
                    ol = "#5a3a1a"
                elif role == "door":
                    ol = "#6a0036"
                elif role == "floor":
                    ol = None
                elif role == "opening":
                    ol = "#0b6b2e"
            s.polygon(pts, fill=fill, outline=ol, width=(3 if role == "window" else lw))
            if role == "floor":
                decorate_surface(img, meta, wire, ss)
            if role == "window":  # 引き違いの中桟
                mx0 = ((pts[0][0] + pts[1][0]) / 2, (pts[0][1] + pts[1][1]) / 2)
                mx1 = ((pts[2][0] + pts[3][0]) / 2, (pts[2][1] + pts[3][1]) / 2)
                s.line([mx0, mx1], "#000000" if wire else "#5a3a1a", 2)
        if wire and tag == "opening":
            pts = polys[0][0]
            dashed(s, pts[0], pts[3], "#000000", 5); dashed(s, pts[1], pts[2], "#000000", 5)
    if not wire:
        # 地面の着色の上に床の線（色モック）
        pass
    anchors = {}
    for dd in p["doors"]:
        anchors[dd["id"]] = door_geom(p, dd)[2]
    for m in p["markers"]:
        r = marker_rect(m)
        anchors[m["id"]] = proj((r[0] + r[2]) / 2, (r[1] + r[3]) / 2)
    for o in p["openings"]:
        w = wall_by_id(p, o["wall"])
        r = w["rect"]
        anchors[o["id"]] = proj((r[0] + r[2]) / 2, o["center"]) if not is_h(w) else proj(o["center"], (r[1] + r[3]) / 2)
    if labels:
        f1, f2 = font(18 * ss), font(16 * ss)
        def text(xy, t, f, fg="#000000", bg="#ffffff"):
            x, y = xy
            bb = d.textbbox((0, 0), t, font=f)
            tw, th = bb[2] - bb[0], bb[3] - bb[1]
            d.rectangle([x * ss - tw / 2 - 4, y * ss - th / 2 - 4, x * ss + tw / 2 + 4, y * ss + th / 2 + 6], fill=bg)
            d.text((x * ss - tw / 2, y * ss - th / 2 - bb[1]), t, font=f, fill=fg)
        for key, tag, polys, meta in items:
            if tag == "box" and meta.get("label"):
                cx, cy = proj(*meta["label_at"]) if meta.get("label_at") else center_of(polys[2][0])
                text((cx, cy), meta["label"], f2, "#222222", "#fffbe6")
            elif tag == "floor" and meta.get("label"):
                cx, cy = proj(*meta["label_at"]) if meta.get("label_at") else center_of(polys[0][0])
                text((cx, cy), meta["label"], f2, "#555555", "#f4f4f4")
            elif tag == "wall" and meta.get("kind") == "partition" and meta.get("label") and meta["id"] not in getattr(render, "_seen", set()):
                pass
        seen = set()
        for key, tag, polys, meta in items:
            if tag == "wall" and meta.get("kind") == "partition" and meta["id"] not in seen:
                seen.add(meta["id"])
                cx, cy = center_of(polys[2][0])
                text((cx, cy), meta.get("label", "仕切り"), f2, "#ffffff", "#4a4f57")
            if tag == "wall" and (meta.get("kind") == "building" or (meta.get("kind") in ("fence", "retaining") and meta.get("label"))) and meta["id"] not in seen:
                seen.add(meta["id"])
                cx, cy = center_of(polys[2][0])
                text((cx, cy), meta.get("label", ""), f1, "#222222", "#ffffff")
        for dd in p["doors"]:
            ax, ay = anchors[dd["id"]]
            text((ax, ay + 24), dd["id"], f2, "#ffffff", "#c0006a")
        for o in p["openings"]:
            ax, ay = anchors[o["id"]]
            text((ax, ay), "開口(要確認)", f2, "#222222", OPEN_COLOR)
        for m in p["markers"]:
            ax, ay = anchors[m["id"]]
            text((ax, ay - 30), m["id"], f2, "#ffffff", "#c0006a")
        for an in p["annotations"]:
            ax, ay = proj(*an["at"])
            text((ax, ay), an["text"], f2, "#ffffff", "#c04000")
        for i, (lab, colr, fg) in enumerate((("仕切り=壁（濃い灰）", "#4a4f57", "#ffffff"), ("開口=通れる所（緑）", OPEN_COLOR, "#003311"), ("戸口（ピンク）", DOOR_COLOR, "#ffffff"))):
            text((130 + i * 230, H_IMG - 28), lab, f2, fg, colr)
        text((W / 2, 24), f"{p['map_id']} {p['name']} - {p.get('subtitle','')}   [レビュー用・ラベル付き]", f1, "#000000", "#fff6c8")
    return img.resize((W, H_IMG), Image.LANCZOS), anchors


# ---------------------------------------------------------------- マスク
def derive_mask(p):
    """平面図からマスクを導く。floors(walkable)=白、壁・blocked の箱=黒（画像上の見た目の覆いも黒）、戸口・開口=白。"""
    m = np.zeros((H_IMG, W), np.uint8)
    ex = np.zeros((H_IMG, W), np.uint8)

    def fill(arr, pts, v):
        cv2.fillPoly(arr, [np.round(np.array(pts)).astype(np.int32)], v)
    for f in p["floors"]:
        if f.get("walkable", True):
            fill(m, floor_img_poly(f), 255)
    for key, tag, polys, meta in build_items(p, "color"):
        if tag == "wall" or (tag == "box" and meta.get("blocked")):
            for pts, _, _ in polys:
                fill(m, pts, 0)
    exits = []
    for o in p["openings"]:
        w = wall_by_id(p, o["wall"]); r = w["rect"]; a, b = span(o)
        rc = [a, r[1] - 2, b, r[3] + 2] if is_h(w) else [r[0] - 2, a, r[2] + 2, b]
        fill(m, rect_poly(rc), 255)
    for d in p["doors"]:
        patch, panel, anchor = door_geom(p, d)
        poly = rect_poly(patch)
        fill(m, poly, 255); fill(m, panel, 255)
        hull = cv2.convexHull(np.round(np.array(poly + panel)).astype(np.int32)).reshape(-1, 2)
        fill(ex, hull, 255)
        fill(m, hull, 255)  # 床から戸口のパネルまでを白でつなぐ（壁の上辺の帯を抜く）
        exits.append({"id": d["id"], "partner": d.get("partner"), "wall_side": d["wall_side"], "plan_patch": patch, "image_polygon": hull.tolist(), "status": d.get("status")})
    for mk in p["markers"]:
        r = marker_rect(mk)
        poly = rect_poly(r)
        fill(m, poly, 255)
        hull = np.round(np.array(poly)).astype(np.int32)
        fill(ex, hull, 255)
        exits.append({"id": mk["id"], "partner": mk.get("partner"), "wall_side": mk["edge"], "plan_patch": r, "image_polygon": hull.tolist(), "status": mk.get("status")})
    n, lab = cv2.connectedComponents((m > 0).astype(np.uint8))
    # 出口ごとの所属成分
    comps = {}
    for e in exits:
        mm = np.zeros_like(m); fill(mm, e["image_polygon"], 255)
        ids = set(np.unique(lab[(mm > 0) & (m > 0)]).tolist()) - {0}
        comps[e["id"]] = sorted(ids)
    return m, ex, exits, n - 1, comps


# ---------------------------------------------------------------- 手前オクルージョン
OCC_MIN_H = 20.0       # これ未満の高さの箱（敷物・低い段）は隠さない
OCC_MIN_FLOOR_PX = 200  # キャラの体が重ならない物（奥壁・手前の壁）は出さない
CHAR_PX = 67
BODY_PX = 100  # キャラの高さ（既定・要確認。1キャラ幅=67px から約1.5倍）


def derive_occlusion(p):
    """モックの幾何だけから『手前の壁・背の高い家具がキャラを隠す領域』を決定論的に出す（絵の認識は使わない）。

    occ   : 255=手前の物のシルエット（壁面・箱の前面・側面・上面）。戸口の開口は抜く。
            キャラ（幅 CHAR_PX=67・高さ BODY_PX=100）が背後に入りうる物だけ出す（奥壁・背後に歩ける床の無い物は出ない）。
    depth : uint16。その画素を覆う物の接地線（前縁）の画像 y。重なる時は最大（最も手前）。
            ルール: スプライトの足元 y が depth より小さい（=物の背後）ときだけ、その画素でスプライトを隠す。
    """
    occ = np.zeros((H_IMG, W), np.uint8)
    depth = np.zeros((H_IMG, W), np.uint16)
    walk, exm, _, _, _ = derive_mask(p)
    walk_b = ((walk > 0) & (exm == 0)).astype(np.uint8)  # 戸口の出口範囲（パネルを含む）は足元に数えない
    rows = np.arange(H_IMG)[:, None]
    kern = np.ones((BODY_PX + 1, CHAR_PX), np.uint8)  # 足元から上へ体が伸びる範囲
    pieces = []
    for key, tag, polys, meta in build_items(p, "color"):
        if tag == "wall":
            pass
        elif tag == "box" and meta["h"] >= OCC_MIN_H:
            pass
        else:
            continue
        sil = np.zeros((H_IMG, W), np.uint8)
        for pts, _, _ in polys:
            cv2.fillPoly(sil, [np.round(np.array(pts)).astype(np.int32)], 255)
        base_y = int(round(proj(BASE_W / 2, key)[1]))
        feet = (walk_b * (rows < base_y - 4)).astype(np.uint8)
        body = cv2.dilate(feet, kern, anchor=(CHAR_PX // 2, 0))
        behind = int(((sil > 0) & (body > 0)).sum())
        if behind < OCC_MIN_FLOOR_PX:
            continue
        m = sil > 0
        occ[m] = 255
        depth[m] = np.maximum(depth[m], base_y)
        pieces.append({"id": meta["id"], "kind": tag, "base_y": base_y, "area_px": int(m.sum()), "body_overlap_px": behind})
    for d in p["doors"]:
        _, panel, _ = door_geom(p, d)
        cv2.fillPoly(occ, [np.round(np.array(panel)).astype(np.int32)], 0)
        cv2.fillPoly(depth, [np.round(np.array(panel)).astype(np.int32)], 0)
    return occ, depth, pieces


def write_mock(p, out):
    os.makedirs(out, exist_ok=True)
    mid = p["map_id"]
    clean, _ = render(p, "color", labels=False)
    review, _ = render(p, "color", labels=True)
    clean.save(os.path.join(out, f"{mid}-clean.png"))
    review.save(os.path.join(out, f"{mid}-review.png"))
    return [f"{mid}-clean.png", f"{mid}-review.png"]


def write_mask(p, out):
    os.makedirs(out, exist_ok=True)
    mid = p["map_id"]
    m, ex, exits, ncomp, comps = derive_mask(p)
    Image.fromarray(m).save(os.path.join(out, f"{mid}-mask.png"))
    rgb = np.stack([m, m, m], -1).astype(np.uint8) // 2 + 40
    rgb[m == 0] = (30, 30, 30)
    rgb[(ex > 0)] = (0, 200, 90)
    Image.fromarray(rgb).save(os.path.join(out, f"{mid}-exits.png"))
    doc = {"schema": "sit-oblique-mock-mask/1", "map_id": mid, "size": [W, H_IMG], "white_components": ncomp,
           "door_width_plan": DOOR_W, "exits": exits, "exit_components": comps,
           "note": "平面図から導いた。床=白・blocked=黒（壁・blocked の箱は画像上の覆いも黒）・戸口と開口=白"}
    with open(os.path.join(out, f"{mid}-mask.json"), "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
    return [f"{mid}-mask.png", f"{mid}-exits.png", f"{mid}-mask.json"], doc


def write_occlusion(p, out):
    os.makedirs(out, exist_ok=True)
    mid = p["map_id"]
    clean, _ = render(p, "color", labels=False)
    m, _, _, _, _ = derive_mask(p)
    occ, depth, pieces = derive_occlusion(p)
    Image.fromarray(occ).save(os.path.join(out, f"{mid}-occlusion.png"))
    edit = np.zeros((H_IMG, W, 3), np.uint8); edit[occ > 0] = (0, 255, 255)
    Image.fromarray(edit).save(os.path.join(out, f"{mid}-occlusion-edit.png"))
    cv2.imwrite(os.path.join(out, f"{mid}-occlusion-depth.png"), depth)
    ov = np.array(clean).astype(np.float32) * 0.55
    g = m > 0
    ov[g] = ov[g] * 0.6 + np.array([0, 150, 60]) * 0.7
    c = occ > 0
    ov[c] = ov[c] * 0.4 + np.array([0, 255, 255]) * 0.6
    Image.fromarray(np.clip(ov, 0, 255).astype(np.uint8)).save(os.path.join(out, f"{mid}-occlusion-overlay.png"))
    with open(os.path.join(out, f"{mid}-occlusion.json"), "w", encoding="utf-8") as f:
        json.dump({"schema": "sit-oblique-mock-occlusion/1", "map_id": mid, "size": [W, H_IMG],
                   "rule": "スプライトの足元y < depth[画素] の画素だけ、occlusion の白で隠す。奥壁・キャラの体が重ならない物は出さない。戸口の開口は抜く。歩行マスクとは別レイヤー（前景に隠れる床を通行不能にしない）。",
                   "char_px": [CHAR_PX, BODY_PX], "occluders": pieces}, f, ensure_ascii=False, indent=1)
    return [f"{mid}-occlusion.png", f"{mid}-occlusion-edit.png", f"{mid}-occlusion-depth.png", f"{mid}-occlusion-overlay.png", f"{mid}-occlusion.json"]


def write_outputs(p, out):
    write_mock(p, out)
    _, doc = write_mask(p, out)
    write_occlusion(p, out)
    return None, None, doc


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("plan")
    ap.add_argument("--out", required=True)
    ap.add_argument("--variant")
    a = ap.parse_args()
    p = load_plan(a.plan, a.variant)
    _, _, doc = write_outputs(p, a.out)
    print(p["map_id"], "components:", doc["white_components"], "exits:", {e["id"]: doc["exit_components"][e["id"]] for e in doc["exits"]})


if __name__ == "__main__":
    main()
