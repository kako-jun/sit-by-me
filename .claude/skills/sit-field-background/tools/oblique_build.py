"""斜め視点マップの一括ビルド（Make 風）。平面スペック1つ → 全決定論の成果物。途中から再開できる。

段階（上から順。入力 hash が前回と同じ段はスキップ、変わった段以降だけ再実行）:
  validate  平面スペックのスキーマ・整合の検査（欠落・戸口の相手不一致・幅不足・戸口前の障害物・到達不能）
  mock      クリーン版（imagegen 編集元・ラベルなし）とレビュー版（ラベル付き）
  wire      個別の白黒ワイヤー図（昔の攻略本流）
  mask      歩行マスク（床=白・blocked=黒・戸口=出口範囲）
  occlusion 手前オクルージョンマスク（壁・背の高い家具がキャラを隠す領域。深度つき）
  prompt    imagegen 編集用プロンプトを機械生成（台帳 ready でなければ blocked と記録。生成そのものはしない）
  --- 承認ゲート（全MAPのモック・接続図を kako-jun がレビュー）---
  adopt     （手動）採用画像を記録: --adopt IMAGE [--take N]
  verify    （手動）採用記録の鮮度検査（モック/プロンプトが変わっていないか・寸法）
画像認識や LLM を使うのは承認後の imagegen だけ。ここまでは全部スクリプト。

使い方:
  uv run --with numpy --with opencv-python-headless --with pillow python3 -I oblique_build.py PLAN.json [--variant kids] [--from STAGE] [--force]
  uv run ... oblique_build.py --all docs/production/oblique-mocks/connections.json   # 全MAP＋接続図・一覧・接続表
  uv run ... oblique_build.py --status docs/production/oblique-mocks/connections.json
  uv run ... oblique_build.py PLAN.json --adopt path/to/adopted.png --take 3
出力: <out>/<MAP>/ に成果物と manifest.json（各段の入力 hash・出力 sha256。台帳の行へのリンク）。
"""
import argparse
import hashlib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import oblique_mock as M  # noqa: E402
import oblique_text as X  # noqa: E402
import oblique_topology as T  # noqa: E402
import ledger_query as LQ  # noqa: E402
import ledger_io as LIO  # noqa: E402
from PIL import Image  # noqa: E402

STAGES = ["validate", "mock", "wire", "mask", "occlusion", "prompt"]
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
ID_RE = re.compile(r"^[A-Z]{3}-\d{2}\.[A-Za-z0-9-]+$")
from oblique_freshness import PROMPT_VERSION, DECOR_FILE, prompt_input_sha  # noqa: E402  プロンプト段の入力 hash は起動判定と共有
DECOR_LAYER_KEYS = ("desk", "slab_edge", "outside", "building")
DECOR_REQUIRED = ("geometry_fixed", "fill_rule", "layers", "surfaces", "kinds", "allow", "forbid", "trees")


def load_decor(p):
    """plan の decor_pool が指す装飾プール（sit-oblique-decor/1）を返す。無ければ None。"""
    pid = p.get("decor_pool")
    if not pid:
        return None
    with open(DECOR_FILE, encoding="utf-8") as f:
        doc = json.load(f)
    if doc.get("schema") != "sit-oblique-decor/1":
        return None
    pool = doc["pools"].get(pid)
    return effective_pool(doc, pool) if pool else None


AREA_OVERRIDE_PLAN_KEYS = ("area", "area_fixed", "desk_look", "trees", "slab_look")


def effective_pool(doc, pool):
    """プールに area_fixed（机の天面・木の種類・台座の素材）を継承させた実効プール。上書きはここでは起きない（validate_decor がエラーにする）。"""
    import copy
    a = (doc.get("areas") or {}).get(pool.get("area", ""))
    if not a:
        return pool
    e = copy.deepcopy(pool)
    e.setdefault("layers", {}).setdefault("desk", {})["look"] = a["desk"]["look"]
    e["layers"].setdefault("slab_edge", {})["look"] = a["slab"]["look"]
    e["trees"] = a["trees"]
    e["area_fixed"] = {"area": pool["area"], "desk": a["desk"], "slab": a["slab"], "trees": a["trees"]}
    return e


def area_fixed_sha(doc, area):
    a = (doc.get("areas") or {}).get(area)
    return hashlib.sha256(json.dumps(a, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:12] if a else None


def check_area_consistency(plan_dir):
    """同じエリアの全 MAP が同じ area_fixed を継承していること、MAP/プール側で上書きしていないこと。(errors, {area: [map...]})"""
    import glob
    with open(DECOR_FILE, encoding="utf-8") as f:
        doc = json.load(f)
    E, by_area = [], {}
    for pf in sorted(glob.glob(os.path.join(plan_dir, "*-plan.json"))):
        with open(pf, encoding="utf-8") as f:
            pl = json.load(f)
        pid = pl.get("decor_pool")
        if not pid:
            continue
        pool = doc.get("pools", {}).get(pid)
        if not pool:
            E.append(f"{pl.get('map_id')}: decor_pool {pid} が無い"); continue
        by_area.setdefault(pool.get("area"), []).append(pl.get("map_id"))
        for k in AREA_OVERRIDE_PLAN_KEYS:
            if k in pl:
                E.append(f"{pl.get('map_id')}: plan の {k} はエリア固定項目の上書き（禁止）")
    for ar in by_area:
        if ar not in (doc.get("areas") or {}):
            E.append(f"エリア {ar}（{by_area[ar]}）が decor-pools.json の areas に無い")
    return E, by_area


def box_look(b, pool):
    return b.get("look") or ((pool or {}).get("kinds", {}).get(b.get("kind", "")) or "")


# plan の最上位に置ける既知のキー（台帳 MAP.plan追加JSON から入るものを含む）。未知は警告（typo 検出）
KNOWN_PLAN_KEYS = frozenset({
    "schema", "map_id", "name", "subtitle", "source", "design", "floors", "walls", "boxes", "doors", "windows", "openings", "markers", "paths",
    "closed_edges", "no_window_walls", "assumptions", "decor_pool", "depends_on", "indoor", "tree_zones", "variant", "variants", "annotations",
    "sym_chamfer_room_px", "_hide_walls", "_provenance", "boundaries", "scenery_doors", "variation", "forbid_skip"})


def validate_decor(p, E, Wn):
    pid = p.get("decor_pool")
    if not pid:
        Wn.append("decor_pool 未指定: edit-prompt に見た目（look）と許す/禁じる装飾が出ない（簡素な絵になりやすい。E2 round1 の失敗）")
        return
    try:
        with open(DECOR_FILE, encoding="utf-8") as f:
            doc = json.load(f)
    except Exception as ex:  # noqa: BLE001
        E.append(f"decor-pools.json を読めない: {ex}"); return
    if doc.get("schema") != "sit-oblique-decor/1":
        E.append("decor-pools.json の schema が sit-oblique-decor/1 でない"); return
    pool = doc.get("pools", {}).get(pid)
    if pool is None:
        E.append(f"decor_pool {pid} が decor-pools.json に無い"); return
    # エリア固定項目: area を継承。プール側・plan 側の上書きはエラー
    area = pool.get("area")
    areas = doc.get("areas") or {}
    if area not in areas:
        E.append(f"decor_pool {pid}: area {area!r} が decor-pools.json の areas に無い（エリアを足すときは kako-jun と area_fixed を決める）"); return
    a = areas[area]
    if not (a.get("desk", {}).get("look") and isinstance(a["desk"].get("mean_rgb"), list) and len(a["desk"]["mean_rgb"]) == 3 and a["desk"].get("grain") in ("horizontal", "vertical")):
        E.append(f"areas.{area}.desk に look・mean_rgb[3]・grain(horizontal|vertical) が必要")
    if not a.get("slab", {}).get("look"):
        E.append(f"areas.{area}.slab.look（台座の素材）が必要")
    if pool.get("trees"):
        E.append(f"decor_pool {pid}: trees はエリア固定項目（areas.{area}.trees）。プール側で上書きできない")
    for lk in ("desk", "slab_edge"):
        if (pool.get("layers") or {}).get(lk, {}).get("look"):
            E.append(f"decor_pool {pid}: layers.{lk}.look はエリア固定項目（areas.{area}）。プール側で上書きできない")
    for k in AREA_OVERRIDE_PLAN_KEYS:
        if k in p:
            E.append(f"plan の {k} はエリア固定項目の上書き（禁止）。エリア固定は decor-pools.json の areas.{area} で決める")
    pool = effective_pool(doc, pool)
    for k in DECOR_REQUIRED:
        if not pool.get(k):
            E.append(f"decor_pool {pid}: {k} が必要")
    for lk in DECOR_LAYER_KEYS:
        ly = (pool.get("layers") or {}).get(lk)
        if not (isinstance(ly, dict) and ly.get("look") and ly.get("fixed")):
            E.append(f"decor_pool {pid}: layers.{lk} に look と fixed が必要")
    tr = pool.get("trees") or {}
    for tk in ("pine", "deadtree"):
        t = tr.get(tk)
        if not (isinstance(t, dict) and t.get("look") and isinstance(t.get("count"), list) and len(t["count"]) == 2):
            E.append(f"decor_pool {pid}: trees.{tk} に look と count [最小,最大] が必要")
    if not (isinstance(tr.get("total"), list) and len(tr["total"]) == 2 and tr.get("forbid")):
        E.append(f"decor_pool {pid}: trees.total [最小,最大] と trees.forbid が必要")
    elif all(isinstance(tr.get(k), dict) and isinstance(tr[k].get("count"), list) for k in ("pine", "deadtree")):
        lo = tr["pine"]["count"][0] + tr["deadtree"]["count"][0]; hi = tr["pine"]["count"][1] + tr["deadtree"]["count"][1]
        if lo < tr["total"][0] or hi > tr["total"][1]:
            E.append(f"decor_pool {pid}: 松+枯木の本数（{lo}〜{hi}）が total {tr['total']} に収まらない")
    for sk in ("wall", "floor", "door", "window"):
        if not (pool.get("surfaces") or {}).get(sk):
            E.append(f"decor_pool {pid}: surfaces.{sk} が必要")
    for b in p["boxes"]:
        if not box_look(b, pool):
            E.append(f"boxes {b['id']}: look（または pool.kinds に載る kind）が必要")
    if pool.get("outdoor"):
        oe, ow = outdoor_look_problems(p, pool)
        E.extend(oe); Wn.extend(ow)
    # forbid_skip は build_prompt が全MAP（屋内も）に適用するので検査も全MAP
    for sk in p.get("forbid_skip", []):
        if not (isinstance(sk, dict) and sk.get("match") and sk.get("reason")):
            E.append("forbid_skip の各要素に match（外す禁止項目の部分文字列）と reason が必要")
            continue
        hits = [f for f in pool.get("forbid", []) if sk["match"] in f]
        if not hits:
            E.append(f"forbid_skip の match『{sk['match']}』に当たる禁止項目がプールに無い")
        elif len(hits) > 1:
            Wn.append(f"forbid_skip の match『{sk['match']}』が禁止項目 {len(hits)} 件に一致（部分一致で意図しない項目も外れる。1件に絞る）")


# 屋外MAPで実体（look）を必須にする種類（kako-jun 2026-11-02、Issue #191『モックは最低限の位置関係。それ以外は現実の写真を参考に具体的に』『境界はただの色にしない』）
OUTDOOR_LOOK_KINDS = ("building", "fence", "retaining", "closure", "gate")
# 歩けない理由として視覚的に読める語（段差・塀・閉じた門・水など）
BLOCK_REASON_WORDS = ("土塀", "石垣", "生垣", "板塀", "縁石", "段差", "石段", "護岸", "擁壁", "断崖", "閉じた門", "閉じた扉", "門扉", "用水", "水路", "水面", "池の", "川面", "側溝", "堀", "柵", "フェンス", "建物", "外壁", "塀", "雪囲い", "四つ目垣")  # 雪囲い・四つ目垣は寺町の既存の look（TRM-08 b-w-south・TRM-15 b-branch-w など）に出る語。道の縁の境界の種類 EDGE_KIND_GROUPS と同じ語
# 『歩けない』と書いただけ・ただの地面、は実体にならない
_GENERIC_GROUND = {"", "地面", "雪", "雪面", "雪の地面", "雪に覆われた地面", "雪に覆われた地面。"}


# 道の縁の実体ゲート（Issue #191。kako-jun 2026-11-11『道路脇に段差や塀や溝がなく、外も歩けるようにみえる』）
EDGE_CELL = 4          # 平面（土台 1600x1270）の格子（単位）
EDGE_REACH = 24        # 縁の外側にこの距離（単位）以内に実体の帯・壁・箱・護岸があれば覆われているとみなす
EDGE_MIN_LEN = 60      # 覆われていない縁がこの長さ（単位）以上なら報告する
EDGE_BACKDROP_RATIO = 0.4  # 面積が平面のこの割合以上の歩けない床は『背景の地面』であり実体の縁ではない


def _rc(r):
    return [(r[0], r[1]), (r[2], r[1]), (r[2], r[3]), (r[0], r[3])]


def road_edge_uncovered(p):
    """歩ける床の縁のうち、歩けない面（平面の内側）に接するのに、境界の帯（boundaries）・壁・blocked の箱・
    歩けない理由のある歩けない床のどれも付いていない部分を返す。[(床ID, 長さ(単位), (x0,y0,x1,y1)), ...]。
    平面の外周に接する辺は隣のMAPへ続く出入口なので対象外。"""
    import numpy as np
    import cv2
    c = EDGE_CELL
    gw, gh = M.BASE_W // c, M.BASE_D // c

    def mask_of(polys):
        g = np.zeros((gh, gw), np.uint8)
        for pl in polys:
            cv2.fillPoly(g, [np.round(np.array(pl, dtype=float) / c).astype(np.int32)], 255)
        return g

    shaped = lambda f: "rect" in f or "poly" in f  # noqa: E731  形のある床だけ（形の無い簡易plan は対象外）
    walk_floors = [f for f in p.get("floors", []) if f.get("walkable", True) and not f.get("no_step") and shaped(f)]
    if not walk_floors:
        return []
    cover = []
    for bd in p.get("boundaries", []):
        cover.append(_rc(bd["rect"]) if bd.get("rect") else [tuple(q) for q in bd["poly"]])
    for w in p.get("walls", []):
        if "rect" in w:
            cover.append(_rc(w["rect"]))
    for b in p.get("boxes", []):
        if b.get("blocked") and "rect" in b:
            cover.append(_rc(b["rect"]))
    for f in p.get("floors", []):
        if f.get("walkable", True) or not shaped(f):
            continue
        pl = M.floor_poly(f)
        area = abs(cv2.contourArea(np.array(pl, dtype=np.float32)))
        if area >= EDGE_BACKDROP_RATIO * M.BASE_W * M.BASE_D:
            continue
        if any(wd in (f.get("look") or "") for wd in BLOCK_REASON_WORDS):
            cover.append(pl)
    k = 2 * (EDGE_REACH // c) + 1
    cov = cv2.dilate(mask_of(cover), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)))
    out = []
    for f in walk_floors:
        fm = mask_of([M.floor_poly(f)])
        others = [o for o in walk_floors if o is not f]
        other_walk = cv2.dilate(mask_of([M.floor_poly(o) for o in others]), np.ones((5, 5), np.uint8)) if others else np.zeros_like(fm)
        er = cv2.erode(fm, np.ones((3, 3), np.uint8), borderType=cv2.BORDER_CONSTANT, borderValue=0)
        edge = (fm > 0) & (er == 0)
        edge[:2, :] = False; edge[-2:, :] = False; edge[:, :2] = False; edge[:, -2:] = False  # 平面の外周＝隣MAPへの出入口
        edge &= other_walk == 0  # 別の歩ける床と接する縁は対象外
        bad = edge & (cov == 0)
        n_lab, lab = cv2.connectedComponents(bad.astype(np.uint8), connectivity=8)
        for i in range(1, n_lab):
            ys, xs = np.where(lab == i)
            length = max(xs.max() - xs.min(), ys.max() - ys.min()) * c
            if length >= EDGE_MIN_LEN:
                out.append((f.get("id"), int(length), (int(xs.min() * c), int(ys.min() * c), int(xs.max() * c), int(ys.max() * c))))
    return out


# 道の縁の境界の種類（バリエーションと、隣のMAPとのつなぎ目の連続性。決定 SIT.road-edge-solid-boundary、Issue #191）
# 語は BLOCK_REASON_WORDS に合わせた既存の語だけ（造語しない）。look にその語が出てきたら、その種類の境界とみなす。
EDGE_KIND_GROUPS = (
    ("土塀", ("土塀",)),
    ("板塀", ("板塀",)),
    ("石垣・石積み", ("石垣", "石積み", "擁壁")),
    ("側溝・縁石", ("側溝", "縁石")),
    ("用水・護岸", ("用水", "護岸")),
    ("生垣", ("生垣", "刈り込み")),
    ("雪囲い", ("雪囲い", "四つ目垣")),
)
SEAM_SIDES = ("left", "right", "top", "bottom")
SEAM_INSET = 70   # 端からこの距離（単位）内側で、道の幅を測る
SEAM_EDGE_TOUCH = 16  # この距離（単位）以内に辺へ届く床だけを『辺に接する道』とみなす
SEAM_NEAR_EDGE = 20   # 内側に境界が無いとき、端からこの距離の位置の塀・擁壁の帯を見る
SEAM_REACH = 18   # 道の縁からこの距離（単位）外側にある境界を、つなぎ目の境界とみなす
SEAM_SIDE_JA = {"left": "左", "right": "右", "top": "上", "bottom": "下"}
SEAM_LOHI_JA = {"left": ("北", "南"), "right": ("北", "南"), "top": ("西", "東"), "bottom": ("西", "東")}


def edge_kinds(look):
    """look の文に出てくる道の縁の境界の種類（EDGE_KIND_GROUPS の名前）の一覧。出てくる順。"""
    look = look or ""
    hits = []
    for name, words in EDGE_KIND_GROUPS:
        pos = [look.find(w) for w in words if w in look]
        if pos:
            hits.append((min(pos), name))
    return [n for _, n in sorted(hits)]


def _seam_items_at(p, x, y):
    """点 (x, y) を覆う境界の帯・壁・blocked 箱・歩けない小さな床（id, look）。"""
    import numpy as np
    import cv2

    def inside(rc, tol=8):
        return rc[0] - tol <= x <= rc[2] + tol and rc[1] - tol <= y <= rc[3] + tol
    out = []
    for b in p.get("boundaries", []):
        if (b.get("rect") and inside(b["rect"])) or (b.get("poly") and cv2.pointPolygonTest(np.array(b["poly"], np.float32), (float(x), float(y)), True) >= -8):
            out.append((b.get("id"), b.get("look") or ""))
    for w in p.get("walls", []):
        if "rect" in w and inside(w["rect"]):
            out.append((w.get("id"), w.get("look") or ""))
    for bx in p.get("boxes", []):
        if bx.get("blocked") and "rect" in bx and inside(bx["rect"]):
            out.append((bx.get("id"), bx.get("look") or ""))
    for fl in p.get("floors", []):
        if not fl.get("walkable", True) and "poly" not in fl and "rect" in fl and fl["rect"] != [0, 0, M.BASE_W, M.BASE_D] and inside(fl["rect"]):
            out.append((fl.get("id"), fl.get("look") or ""))
    return out


def seam_edges(p, side):
    """辺 side（left/right/top/bottom）に接する道の両脇の境界。{'range': (lo, hi), 'lo': {id, look, kinds}, 'hi': {...}}。
    lo は北（左右の辺）／西（上下の辺）側、hi は南／東側。道が辺に無ければ None。境界が無い側は id=None・kinds=[]。"""
    import numpy as np
    import cv2
    c = 4
    g = np.zeros((M.BASE_D // c, M.BASE_W // c), np.uint8)
    vert = side in ("left", "right")
    for f in p.get("floors", []):
        if f.get("walkable", True) and not f.get("no_step") and ("rect" in f or "poly" in f):
            pts = np.array(M.floor_poly(f), dtype=float)
            # 辺に届いている床（道）だけを測る。中庭など辺に届かない広い床が道の幅を広げないため
            reach = pts[:, 0].max() >= M.BASE_W - SEAM_EDGE_TOUCH if side == "right" else pts[:, 0].min() <= SEAM_EDGE_TOUCH if side == "left" else pts[:, 1].max() >= M.BASE_D - SEAM_EDGE_TOUCH if side == "bottom" else pts[:, 1].min() <= SEAM_EDGE_TOUCH
            if reach:
                cv2.fillPoly(g, [np.round(pts / c).astype(np.int32)], 255)
    if vert:
        x = SEAM_INSET if side == "left" else M.BASE_W - SEAM_INSET
        col = g[:, x // c]
    else:
        y = SEAM_INSET if side == "top" else M.BASE_D - SEAM_INSET
        col = g[y // c, :]
    idx = np.where(col > 0)[0]
    if len(idx) == 0:
        return None
    lo, hi = int(idx.min() * c), int(idx.max() * c)
    res = {"range": (lo, hi)}
    for nm, al in (("lo", lo - SEAM_REACH), ("hi", hi + SEAM_REACH)):
        its = _seam_items_at(p, x, al) if vert else _seam_items_at(p, al, y)
        if not its:  # 端から SEAM_INSET の内側に無ければ、端の塀・擁壁の帯そのもの（端から SEAM_NEAR_EDGE の位置）を見る
            nx = (SEAM_NEAR_EDGE if side == "left" else M.BASE_W - SEAM_NEAR_EDGE) if vert else None
            ny = None if vert else (SEAM_NEAR_EDGE if side == "top" else M.BASE_D - SEAM_NEAR_EDGE)
            its = _seam_items_at(p, nx, al) if vert else _seam_items_at(p, al, ny)
        # 境界の帯を先に、次に壁・箱・床（_seam_items_at の順）。最初の1つがつなぎ目の境界
        res[nm] = {"id": its[0][0], "look": its[0][1], "kinds": edge_kinds(its[0][1])} if its else {"id": None, "look": "", "kinds": []}
    return res


def seam_connections(map_id=None):
    """台帳 接続 の、屋外MAP同士を辺で結ぶ接続（期待=opposite）。[(MAP_A, 辺A, MAP_B, 辺B)]。map_id 指定でそのMAPの接続だけ。"""
    out = []
    for r in LIO.read("接続"):
        if r.get("種別") != "edge" or r.get("期待") != "opposite":
            continue
        (ma, sa), (mb, sb) = r["端A"].split(".", 1), r["端B"].split(".", 1)
        if sa in SEAM_SIDES and sb in SEAM_SIDES and ma.startswith("TRM-") and mb.startswith("TRM-"):
            if map_id in (None, ma, mb):
                out.append((ma, sa, mb, sb))
    return out


def _load_plan_for_seam(map_id, plans_dir=None):
    pp = os.path.join(plans_dir or os.path.join(LIO.REPO, "docs", "production", "oblique-mocks"), f"{map_id}-plan.json")
    return M.load_plan(pp) if os.path.exists(pp) else None


def seam_mismatches(plans_dir=None):
    """つなぎ目の両側で道の縁の境界の種類が食い違う箇所。戻り: (mismatches, unknown)
    mismatches: [(MAP_A, 辺A, 側(北/西/南/東), kinds_A, MAP_B, 辺B, kinds_B)]（両側とも種類が読めて、共通の種類が1つも無い）
    unknown: 片側の境界が無い／種類が読めない（比較できない）箇所。"""
    mism, unknown = [], []
    for ma, sa, mb, sb in seam_connections():
        pa, pb = _load_plan_for_seam(ma, plans_dir), _load_plan_for_seam(mb, plans_dir)
        if pa is None or pb is None:
            continue
        ea, eb = seam_edges(pa, sa), seam_edges(pb, sb)
        if ea is None or eb is None:
            continue
        for nm, ja in zip(("lo", "hi"), SEAM_LOHI_JA[sa]):
            ka, kb = ea[nm]["kinds"], eb[nm]["kinds"]
            if not ka or not kb:
                unknown.append((ma, sa, ja, ka, mb, sb, kb))
            elif not set(ka) & set(kb):
                mism.append((ma, sa, ja, ka, mb, sb, kb))
    return mism, unknown


def seam_lines(p):
    """build_prompt 用: このMAPの各辺について、隣のMAPの道の縁の境界の種類つきで『つなぎ目で続く』文を返す。"""
    key = p.get("map_id")
    lines = []
    for ma, sa, mb, sb in seam_connections(key):
        mine, side, other, oside = (ma, sa, mb, sb) if ma == key else (mb, sb, ma, sa)
        po = _load_plan_for_seam(other)
        pm = p
        if po is None:
            continue
        eo, em = seam_edges(po, oside), seam_edges(pm, side)
        if eo is None or em is None:
            continue
        parts = []
        for nm, ja in zip(("lo", "hi"), SEAM_LOHI_JA[side]):
            ko = eo[nm]["kinds"][:2]  # 表示は look に最初に出る主たる1〜2種類（一致判定は全種類で行う）
            if ko:
                parts.append(f"{ja}側は{'・'.join(ko)}")
        if parts:
            lines.append(X.text("PR.seam.item", side=SEAM_SIDE_JA[side], other=other, kinds="、".join(parts)))
    return lines


# 景色の扉の前面ゲート（Issue #191, kako-jun 2026-11-11『入れない景色としての扉をあたかも入れるような見た目にするな』。決定 SIT.scenery-door-not-enterable）
DOOR_FRONT_REACH = 24      # 扉の載る壁・帯の外側のこの距離（単位）の帯を『扉の前』とみなす
DOOR_FRONT_MIN_CELLS = 3   # 前面が歩ける床に境界なしで接するセル数（4x4単位）がこれ以上なら警告
DOOR_STEP_WORDS = ("段差", "側溝", "溝", "縁石", "石積み", "基礎", "護岸", "石垣")


def scenery_door_front_problems(p):
    """scenery_doors の前面が、境界（boundaries・別の壁・blocked の箱・歩けない理由のある床）を挟まず歩ける床に接している扉。
    [(扉ID, 扉の載る壁/帯ID, セル数)]。扉が boundaries の帯に載るときは、その帯の look に段差・側溝・縁石などがあれば挟んでいるとみなす。"""
    import numpy as np
    import cv2
    c = EDGE_CELL
    gw, gh = M.BASE_W // c, M.BASE_D // c

    def mask_of(polys):
        g = np.zeros((gh, gw), np.uint8)
        for pl in polys:
            cv2.fillPoly(g, [np.round(np.array(pl, dtype=float) / c).astype(np.int32)], 255)
        return g

    def shape(it):
        if it.get("rect"):
            return _rc(it["rect"])
        if it.get("poly"):
            return [tuple(q) for q in it["poly"]]
        return None
    walk = [M.floor_poly(f) for f in p.get("floors", []) if f.get("walkable", True) and not f.get("no_step") and ("rect" in f or "poly" in f)]
    if not walk or not p.get("scenery_doors"):
        return []
    wmask = mask_of(walk)
    hosts = {}
    for w in p.get("walls", []):
        if "rect" in w:
            hosts[w["id"]] = ("wall", w)
    for b in p.get("boundaries", []):
        if shape(b):
            hosts[b["id"]] = ("boundary", b)
    for bx in p.get("boxes", []):
        if "rect" in bx:
            hosts[bx["id"]] = ("box", bx)
    out = []
    k = 2 * (DOOR_FRONT_REACH // c) + 1
    for sd in p["scenery_doors"]:
        ref = sd.get("wall") or sd.get("boundary") or sd.get("at")
        kind, host = hosts.get(ref, (None, None))
        if host is None:
            continue
        if any(wd in ((host.get("look") if kind in ("boundary", "wall") else "") or "") + (sd.get("look") or "") for wd in DOOR_STEP_WORDS):  # 扉の載る壁・帯、または扉の look に段差・溝・基礎などがある
            continue
        hm = mask_of([shape(host)])
        # 他の境界の帯・壁・blocked の箱が前面を覆う（扉の載る壁そのものは除く）
        cover = []
        for b in p.get("boundaries", []):
            if b.get("id") != ref and shape(b):
                cover.append(shape(b))
        for w in p.get("walls", []):
            if w.get("id") != ref and "rect" in w:
                cover.append(_rc(w["rect"]))
        for bx in p.get("boxes", []):
            if bx.get("id") != ref and bx.get("blocked") and "rect" in bx:
                cover.append(_rc(bx["rect"]))
        cm = mask_of(cover) if cover else np.zeros_like(hm)
        front = (cv2.dilate(hm, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k))) > 0) & (hm == 0) & (cm == 0) & (wmask > 0)
        n = int(front.sum())
        if n >= DOOR_FRONT_MIN_CELLS:
            out.append((sd.get("id"), ref, n))
    return out


def outdoor_look_problems(p, pool):
    """屋外MAP（装飾プールの outdoor: true）の look ゲート。(errors, warnings)。
    errors: kind=building/fence/retaining/closure/gate の壁、およびそれらの kind の box が look 空欄（生成を起動しない）。
    warnings: 歩けない面（walkable:false）の look が空・ただの地面・歩けない理由（段差・塀・門・水など）を含まない。"""
    E, Wn = [], []
    for w in p.get("walls", []):
        if w.get("kind") in OUTDOOR_LOOK_KINDS and not (w.get("look") or "").strip():
            E.append(f"屋外MAP: 壁 {w['id']}（kind={w['kind']}）の look が空欄。台帳に現実の写真・資料を参考にした材質・色・形・経年・雪の載り方を書いてから生成する（Issue #191）")
    for b in p.get("boxes", []):
        if b.get("kind") in OUTDOOR_LOOK_KINDS and not (b.get("look") or "").strip():
            E.append(f"屋外MAP: box {b['id']}（kind={b['kind']}）自身の look が空欄（kind の既定文では足りない）。現実参照の具体的な描写を書く（Issue #191）")
    for f in p.get("floors", []):
        if f.get("walkable", True):
            continue
        lk = re.sub(r"[（(]?歩けない[^）)]*[）)]?", "", f.get("look") or "").strip()
        if lk in _GENERIC_GROUND:
            Wn.append(f"屋外MAP: 歩けない面 {f['id']} の look が空・ただの地面。境界を色の違いだけにしない（土塀・石垣・生垣・縁石・段差・水など実体のある要素にする。Issue #191）")
        elif not any(wd in lk for wd in BLOCK_REASON_WORDS) and not f.get("surface"):
            Wn.append(f"屋外MAP: 歩けない面 {f['id']} の look に歩けない視覚的な理由（段差・塀・閉じた門・水など）が読めない。入れそうに見える面になっていないか（Issue #191）")
    # 境界物の帯（歩ける床の外側）。plan.boundaries[]: {id, rect|poly, look}
    for bd in p.get("boundaries", []):
        if not (bd.get("look") or "").strip():
            E.append(f"屋外MAP: boundaries {bd.get('id')} の look が空欄（土塀・石垣・生垣・縁石・段差・護岸などの実体を現実参照で書く）")
        if not (bd.get("rect") or bd.get("poly")):
            E.append(f"屋外MAP: boundaries {bd.get('id')} に rect または poly が無い（境界物を描く領域）")
    if any(f.get("walkable", True) for f in p.get("floors", [])) and not p.get("boundaries"):
        Wn.append("屋外MAP: plan に boundaries（歩ける床の外側の境界物の帯）が無い。床の色の切り替えだけの境界になる（Issue #191）")
    # 景色としての扉・門・潜り戸（通行しない）。plan.scenery_doors[]: {id, wall|at, look}
    for sd in p.get("scenery_doors", []):
        if not (sd.get("look") or "").strip():
            E.append(f"屋外MAP: scenery_doors {sd.get('id')} の look が空欄（閉じている・通行しない景色の扉の材質・形・状態）")
    for fid, ln, bb in road_edge_uncovered(p):  # 道の縁（歩けない面に接する辺）に境界の実体が付いていない（決定 SIT.road-edge-solid-boundary）
        Wn.append(f"屋外MAP: 歩ける床 {fid} の縁（長さ約{ln}、範囲 {list(bb)}）に段差・塀・側溝・縁石・護岸などの実体（boundaries・壁・護岸の歩けない面）が付いていない。道の外側が歩けるように見える（決定 SIT.road-edge-solid-boundary、Issue #191）")
    kinds_per = [edge_kinds(bd.get("look")) for bd in p.get("boundaries", [])]
    if len(kinds_per) >= 3 and all(k for k in kinds_per) and len({k[0] for k in kinds_per}) == 1 and all(set(k) == {kinds_per[0][0]} for k in kinds_per):
        Wn.append(f"屋外MAP: boundaries {len(kinds_per)} 本がすべて同じ種類（{kinds_per[0][0]}だけ）。道の縁は段差・側溝・縁石・土塀・石垣・板塀・生垣・護岸などを現実参照で区間ごとに使い分ける（決定 SIT.road-edge-solid-boundary、Issue #191）")
    for sid, ref, n in scenery_door_front_problems(p):
        Wn.append(f"屋外MAP: 景色の扉 {sid}（{ref}）の前が、境界（段差・塀・溝・植栽・雪囲いなど）を挟まず歩ける床に接している（約{n}セル）。入れるように見える（決定 SIT.scenery-door-not-enterable、Issue #191）")
    if not p.get("variation"):
        Wn.append("屋外MAP: plan に variation（足跡・汚れ・土の露出・除雪の雪山・スノーポール・消雪パイプ・電柱など、このMAPの look から来る変化の語）が無い。単調になりやすい（Issue #191）")
    if pool and pool.get("trees"):
        tw = tree_room_warning(p, pool)
        if tw:
            Wn.append(tw)
    for z in p.get("tree_zones", []):  # 木の帯が歩ける床と重なると『歩く地面の上には置かない』と矛盾する
        zr = z["rect"]
        for fl in p["floors"]:
            if fl.get("walkable") and tree_zone_hits_floor(zr, fl):
                Wn.append(f"屋外MAP: tree_zones {z.get('id')} が歩ける床 {fl.get('id')} と重なる（木を歩く地面の上に置かせてしまう）")
    return E, Wn



def sha_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha_file(path):
    with open(path, "rb") as f:
        return sha_bytes(f.read())


def src_sha(*names):
    return sha_bytes(b"".join(open(os.path.join(HERE, n), "rb").read() for n in names))


# ---------------------------------------------------------------- 検査

def plan_free_grid(p, cell=2):
    """平面（土台 1600x1270 単位）で歩ける所の格子。床（no_step=踏ませない床は除く）＋戸口・開口の通り道、から壁・blocked の箱を引く。"""
    import numpy as np
    import cv2
    gw, gh = M.BASE_W // cell, M.BASE_D // cell
    g = np.zeros((gh, gw), np.uint8)

    def fill(rc, v):
        x0, y0, x1, y1 = [int(round(c / cell)) for c in rc]
        g[max(0, y0):max(0, y1), max(0, x0):max(0, x1)] = v
    def fill_floor(floor, value):
        if "poly" not in floor:
            fill(floor["rect"], value)
            return
        points = np.round(np.array(M.floor_poly(floor)) / cell).astype(np.int32)
        cv2.fillPoly(g, [points], value)

    for f in p["floors"]:
        if f.get("walkable", True) and not f.get("no_step"):
            fill_floor(f, 255)
    for f in p["floors"]:
        if f.get("no_step"):
            fill_floor(f, 0)
    for w in p["walls"]:
        fill(w["rect"], 0)
    for bx in p["boxes"]:
        if bx.get("blocked"):
            fill(bx["rect"], 0)
    for o in p["openings"]:
        w = M.wall_by_id(p, o["wall"]); r = w["rect"]; a, b_ = M.span(o)
        fill([a, r[1], b_, r[3]] if M.is_h(w) else [r[0], a, r[2], b_], 255)
    for d in p["doors"]:
        w = M.wall_by_id(p, d["wall"]); r = w["rect"]; a, b_ = M.span(d)
        fill([a, r[1], b_, r[3]] if M.is_h(w) else [r[0], a, r[2], b_], 255)
    return g


def endpoint(p, ident):
    """戸口・開口の通り道の入口の平面点（歩く側へ少し入った所）。"""
    for d in p["doors"] + p["openings"]:
        if d["id"] == ident:
            w = M.wall_by_id(p, d["wall"]); r = w["rect"]
            face = d.get("face", "east")
            if M.is_h(w):
                return (d["center"], (r[1] - 100) if face == "north" else (r[3] + 100))
            return ((r[0] - 100) if face == "west" else (r[2] + 100), d["center"])
    return None


def check_paths(p):
    """paths[]: 戸口⇄開口の通り道に、戸口幅（キャラ2人分）の通路を確保できるか。no_step の床・blocked の箱の上は通らない。"""
    import numpy as np
    import cv2
    E = []
    if not p.get("paths"):
        return E
    cell = 2
    g = plan_free_grid(p, cell)
    for pa in p["paths"]:
        half = (pa.get("min_width", M.DOOR_W) / 2 - 2) / cell
        k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (int(2 * half) + 1, int(2 * half) + 1))
        er = cv2.erode(g, k)
        a, b_ = endpoint(p, pa["from"]), endpoint(p, pa["to"])
        if a is None or b_ is None:
            E.append(f"paths {pa.get('id')}: from/to の戸口・開口が無い"); continue
        sa = (int(a[0] / cell), int(a[1] / cell)); sb = (int(b_[0] / cell), int(b_[1] / cell))
        n, lab = cv2.connectedComponents((er > 0).astype(np.uint8))
        la, lb = lab[sa[1], sa[0]], lab[sb[1], sb[0]]
        if la == 0 or lb == 0 or la != lb:
            E.append(f"paths {pa.get('id')}: {pa['from']} から {pa['to']} へ幅{pa.get('min_width', M.DOOR_W)}（キャラ2人分）の通路が取れない（布団・長持・家具が通路に乗っている、または狭い）")
    return E

def validate_plan(p):
    """(errors, warnings)。errors があれば後段へ進まない。"""
    E, Wn = [], []
    for k in ("map_id", "name"):
        if not p.get(k):
            E.append(f"必須項目 {k} が無い")
    ids = {}

    def reg(kind, e):
        if "id" not in e:
            E.append(f"{kind} に id が無い: {e}")
            return
        if e["id"] in ids:
            E.append(f"id 重複: {e['id']}")
        ids[e["id"]] = kind

    def rect_ok(kind, e):
        r = e.get("rect")
        if not (isinstance(r, list) and len(r) == 4 and all(isinstance(v, (int, float)) for v in r)):
            E.append(f"{kind} {e.get('id')}: rect は [x0,y0,x1,y1]"); return False
        if r[2] <= r[0] or r[3] <= r[1]:
            E.append(f"{kind} {e['id']}: rect の大きさが0以下 {r}"); return False
        if r[0] < 0 or r[1] < 0 or r[2] > M.BASE_W or r[3] > M.BASE_D:
            E.append(f"{kind} {e['id']}: 土台（{M.BASE_W}x{M.BASE_D}）の外に出ている {r}")
        return True

    for kind in ("floors", "walls", "boxes"):
        for e in p[kind]:
            reg(kind, e)
            if rect_ok(kind, e):
                if kind in ("walls", "boxes") and e.get("h", 0) <= 0:
                    E.append(f"{kind} {e['id']}: h（高さ）が必要")
                if kind != "walls" and kind != "floors" and "color" not in e:
                    E.append(f"boxes {e['id']}: color が必要")
                if kind == "floors" and "color" not in e:
                    E.append(f"floors {e['id']}: color が必要")
    for f in p["floors"]:
        if f.get("poly") is not None:
            pl = f["poly"]
            if not (isinstance(pl, list) and len(pl) >= 3 and all(isinstance(q, list) and len(q) == 2 and all(isinstance(v, (int, float)) for v in q) for q in pl)):
                E.append(f"floors {f.get('id')}: poly は [[x,y],...]（3点以上）")
        if f.get("surface") is not None and f["surface"] not in M.FLOOR_SURFACES:
            E.append(f"floors {f.get('id')}: surface は {list(M.FLOOR_SURFACES)} のどれか")
    walls = {w["id"]: w for w in p["walls"] if "rect" in w and "id" in w}
    seen_span = {}
    for kind in ("doors", "openings"):
        for d in p[kind]:
            reg(kind, d)
            did = d.get("id", "?")
            if d.get("wall") not in walls:
                E.append(f"{kind} {did}: wall {d.get('wall')} が無い"); continue
            w = walls[d["wall"]]
            r = w["rect"]
            if d.get("wall_side") not in M.__dict__.get("_SIDES", ("north", "south", "west", "east")):
                E.append(f"{kind} {did}: wall_side が north/south/west/east でない")
            if kind == "doors" and d.get("face") not in ("north", "south", "west", "east"):
                E.append(f"doors {did}: face（歩く側）が必要")
            if not isinstance(d.get("center"), (int, float)):
                E.append(f"{kind} {did}: center が必要"); continue
            if not (isinstance(d.get("along_ref"), list) and len(d["along_ref"]) == 2 and d["along_ref"][1] > d["along_ref"][0]):
                E.append(f"{kind} {did}: along_ref [a,b] が必要（位置の比の基準）")
            lo, hi = (r[0], r[2]) if M.is_h(w) else (r[1], r[3])
            a, b = M.span(d)
            if d.get("width_class", M.WIDTH_DEFAULT) not in M.WIDTH_CLASSES:
                E.append(f"{kind} {did}: width_class は {list(M.WIDTH_CLASSES)}")
            if kind == "doors" and "width_class" not in d:
                E.append(f"doors {did}: width_class（2people|1person）が必要")
            if a < lo or b > hi:
                E.append(f"{kind} {did}: 戸口の幅（{d.get('width_class', M.WIDTH_DEFAULT)}={M.door_w(d):.0f}）が壁の長さに収まらない（壁 {lo}〜{hi}、戸口 {a:.0f}〜{b:.0f}）")
            if kind == "doors":
                if M.DOOR_H > w["h"]:
                    E.append(f"doors {did}: 戸口の高さ{M.DOOR_H}（キャラ2人分）が壁の高さ{w['h']}を超える")
                pr = d.get("partner")
                if not pr or not ID_RE.match(pr):
                    E.append(f"doors {did}: partner（相手の door ID。MAP-ID.name の形）が必要")
                if not ID_RE.match(did):
                    E.append(f"doors {did}: id は MAP-ID.name の形")
            seen_span.setdefault(d["wall"], []).append((a, b, did))
    for wid, spans in seen_span.items():
        spans.sort()
        for (a1, b1, i1), (a2, b2, i2) in zip(spans[:-1], spans[1:]):
            if a2 < b1:
                E.append(f"壁 {wid}: {i1} と {i2} の戸口・開口が重なる")
    for m in p["markers"]:
        reg("markers", m)
        if m.get("edge") not in ("north", "south", "west", "east"):
            E.append(f"markers {m.get('id')}: edge が不正")
        if not m.get("partner") or not ID_RE.match(m["partner"]):
            E.append(f"markers {m.get('id')}: partner が必要")
        if "width" in m and not (isinstance(m["width"], (int, float)) and M.CHAR <= m["width"] <= 600):
            E.append(f"markers {m.get('id')}: width は {M.CHAR}〜600（平面単位）。未指定=2人分{M.DOOR_W}")
    # 窓
    for wn in p["windows"]:
        reg("windows", wn)
        wid = wn.get("id", "?")
        if wn.get("wall") not in walls:
            E.append(f"windows {wid}: wall {wn.get('wall')} が無い"); continue
        w = walls[wn["wall"]]; r = w["rect"]
        if wn.get("kind") not in M.WINDOW_KINDS:
            E.append(f"windows {wid}: kind は {list(M.WINDOW_KINDS)} のどれか（掃き出し=floor・腰高=waist）"); continue
        if wn.get("status") not in ("fixed", "default"):
            E.append(f"windows {wid}: status は fixed|default")
        for k in ("center", "width", "sill", "height"):
            if not isinstance(wn.get(k), (int, float)):
                E.append(f"windows {wid}: {k} が必要")
        if not isinstance(wn.get("center"), (int, float)) or not isinstance(wn.get("width"), (int, float)) or not isinstance(wn.get("sill"), (int, float)) or not isinstance(wn.get("height"), (int, float)):
            continue
        if wn["kind"] == "floor" and wn["sill"] != 0:
            E.append(f"windows {wid}: 掃き出し窓は sill=0（床まで届く）")
        if wn["kind"] == "waist" and wn["sill"] <= 0:
            E.append(f"windows {wid}: 腰高窓は sill>0")
        lo, hi = (r[0], r[2]) if M.is_h(w) else (r[1], r[3])
        a, b = wn["center"] - wn["width"] / 2, wn["center"] + wn["width"] / 2
        if a < lo or b > hi:
            E.append(f"windows {wid}: 壁の長さに収まらない（壁 {lo}〜{hi}、窓 {a:.0f}〜{b:.0f}）")
        if wn["sill"] + wn["height"] > w["h"]:
            E.append(f"windows {wid}: 窓の上端 {wn['sill'] + wn['height']} が壁の高さ {w['h']} を超える")
        for d in p["doors"] + p["openings"]:
            if d.get("wall") == wn["wall"]:
                da, db = M.span(d)
                top = M.DOOR_H if d in p["doors"] else w["h"]
                if a < db and b > da and wn["sill"] < top:
                    E.append(f"windows {wid}: 戸口・開口 {d['id']} と重なる")
        for o in p["windows"]:
            if o is not wn and o.get("wall") == wn["wall"] and isinstance(o.get("center"), (int, float)):
                oa, ob = o["center"] - o["width"] / 2, o["center"] + o["width"] / 2
                osl, oh = o.get("sill"), o.get("height")  # 階ごとに縦に並ぶ窓（団地の棟）は縦に離れていれば重ならない
                vert = not isinstance(osl, (int, float)) or not isinstance(oh, (int, float)) or (wn["sill"] < osl + oh and osl < wn["sill"] + wn["height"])
                if a < ob and b > oa and vert:
                    E.append(f"windows {wid}: 窓 {o['id']} と重なる")
        face = r[3] if M.is_h(w) else M.visible_face_x(w)
        for bx in p["boxes"]:
            q = bx["rect"]
            if M.is_h(w):
                adj = abs(q[1] - face) <= 2 and q[0] < b and q[2] > a
            else:
                adj = (abs(q[0] - face) <= 2 or abs(q[2] - face) <= 2) and q[1] < b and q[3] > a
            if adj and bx["h"] > wn["sill"]:
                E.append(f"windows {wid}: 家具 {bx['id']} が窓の前をふさぐ")
    for w in p["walls"]:
        n = sum(1 for x in p["windows"] if x.get("wall") == w["id"])
        if w.get("window_count", 0) != n:
            E.append(f"壁 {w['id']}: window_count={w.get('window_count', 0)} と windows[] の実数 {n} が不一致")
    for nw in p.get("no_window_walls", []):
        if nw.get("wall") not in walls:
            E.append(f"no_window_walls: wall {nw.get('wall')} が無い")
        elif any(x.get("wall") == nw["wall"] for x in p["windows"]):
            E.append(f"no_window_walls: 壁 {nw['wall']} は窓なしと確定しているのに windows[] がある")
    E += check_paths(p)
    # 戸口の前（歩く側）を blocked の箱が塞いでいないか
    for d in p["doors"]:
        if d.get("wall") not in walls or d.get("face") not in ("north", "south", "west", "east"):
            continue
        w = walls[d["wall"]]; r = w["rect"]; a, b = M.span(d)
        pad = 80
        if M.is_h(w):
            zone = [a, r[1] - pad, b, r[1]] if d["face"] == "north" else [a, r[3], b, r[3] + pad]
        else:
            zone = [r[0] - pad, a, r[0], b] if d["face"] == "west" else [r[2], a, r[2] + pad, b]
        for bx in p["boxes"]:
            if bx.get("blocked"):
                q = bx["rect"]
                if q[0] < zone[2] and q[2] > zone[0] and q[1] < zone[3] and q[3] > zone[1]:
                    E.append(f"doors {d['id']}: 戸口の前（{pad}単位）を箱 {bx['id']} が塞いでいる")
    if not E:
        # 到達性: 全出口が同じ白成分
        try:
            _, _, exits, n, comps = M.derive_mask(p)
            if exits:
                common = set(comps[exits[0]["id"]])
                for e in exits[1:]:
                    common &= set(comps[e["id"]])
                if not common:
                    E.append(f"出口どうしが歩行マスク上でつながらない: { {k: v for k, v in comps.items()} }")
                for e in exits:
                    if not comps[e["id"]]:
                        E.append(f"出口 {e['id']} が歩行マスクの白に重ならない")
        except Exception as ex:  # noqa: BLE001
            E.append(f"マスク導出に失敗: {ex}")
    for a_ in p.get("assumptions", []):
        Wn.append(a_)
    for d in p["doors"] + p["openings"]:
        if d.get("status") == "default":
            Wn.append(f"既定（要確認）: {d['id']}")
    validate_decor(p, E, Wn)
    for k in p:  # 台帳 plan追加JSON の typo（boundries など）が黙って無視されないよう、未知の最上位キーは警告
        if k not in KNOWN_PLAN_KEYS:
            Wn.append(f"plan の最上位キー『{k}』は既知のキーに無い（typo なら無視される。新しいキーなら oblique_build.KNOWN_PLAN_KEYS に足す）")
    dep = p.get("depends_on")
    if dep is not None:
        base = re.sub(r"-(kids|fire|burnt|wc)$", "", p.get("map_id", ""))
        if not (isinstance(dep, list) and all(isinstance(x, str) and re.match(r"^[A-Z]{3}-\d{2}(-[a-z]+)?$", x) for x in dep)):
            E.append("depends_on は MAP ID（例 TRM-04・TRM-05-kids）の配列")
        else:
            if p.get("map_id") in dep or base in dep and base == p.get("map_id"):
                E.append(f"depends_on が自己参照: {p.get('map_id')}")
            if len(set(dep)) != len(dep):
                E.append("depends_on に重複がある")
            # ※ depends_on が無い変種はこの規則の外（上の if dep is not None の中）。素通りしないよう、台帳側は verify_prompt_reflects_ledger.rb の検査 (vi) が、起動側は dependency-graph.json と plan の一致検査（oblique_e2_schedule.py graph）が補う
            if p.get("variant") and base not in dep:  # 同じ部屋・建物の別時期は基準MAPの確定画像を必ず参照する（#193）
                E.append(f"時期差分MAP {p.get('map_id')} の depends_on に基準MAP {base} が無い（別時期の同一性のため基準の確定画像を参照に含める）")
    return E, Wn


# ---------------------------------------------------------------- プロンプト
def _bbox(polys):
    xs = [q[0] for poly in polys for q in poly]; ys = [q[1] for poly in polys for q in poly]
    return [round(min(xs)), round(min(ys)), round(max(xs)), round(max(ys))]


def _pts(poly):
    return " ".join(f"({round(x)},{round(y)})" for x, y in poly)


def tree_band_sizes(p):
    """木の帯（台座の上面の台形の内側で、建物・壁の外接矩形の外側）の画素座標と幅。coord_section の TREE PLACEMENT と検査が同じ値を使う。"""
    tl, tr, br, bl = [tuple(map(float, q)) for q in M._DST]
    ws = p["walls"]
    if not ws:  # 壁が無い plan は建物の外接矩形が定まらない（帯を数えない）
        return {}
    x0 = min(w["rect"][0] for w in ws); y0 = min(w["rect"][1] for w in ws); x1 = max(w["rect"][2] for w in ws); y1 = max(w["rect"][3] for w in ws)
    ground = [M.proj(x0, y0), M.proj(x1, y0), M.proj(x1, y1), M.proj(x0, y1)]
    hb = max((w["h"] for w in ws if M.is_h(w) and w["rect"][1] == y0), default=0); hf = max((w["h"] for w in ws if M.is_h(w) and w["rect"][3] == y1), default=0)
    top = [M.proj(x0, y0, hb), M.proj(x1, y0, hb), M.proj(x1, y1, hf), M.proj(x0, y1, hf)]
    bx0, by0, bx1, by1 = _bbox([ground, top])
    sx0, sy0 = int(min(tl[0], bl[0])), int(tl[1]); sx1, sy1 = int(max(tr[0], br[0])), int(bl[1])
    return {"sx0": sx0, "sy0": sy0, "sx1": sx1, "sy1": sy1, "bx0": bx0, "by0": by0, "bx1": bx1, "by1": by1,
            "top": by0 - sy0, "bottom": sy1 - by1, "left": bx0 - sx0, "right": sx1 - bx1}


def tree_zone_hits_floor(zr, fl, step=3):
    """木の帯の矩形が歩ける床（rect または poly）と重なるか。poly は帯の格子点が多角形の内側に入るかで見る。"""
    if "poly" in fl:
        poly = M.floor_poly(fl)
        def inside(x, y):
            c = False
            for i in range(len(poly)):
                (x1, y1), (x2, y2) = poly[i], poly[(i + 1) % len(poly)]
                if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
                    c = not c
            return c
        xs = range(int(zr[0]), int(zr[2]) + 1, step); ys = range(int(zr[1]), int(zr[3]) + 1, step)
        return any(inside(x, y) for x in xs for y in ys)
    fr = fl.get("rect")
    return bool(fr) and zr[0] < fr[2] and zr[2] > fr[0] and zr[1] < fr[3] and zr[3] > fr[1]


def tree_room_warning(p, pool):
    """木の本数に対して置ける帯（または plan の tree_zones）が足りなければ警告文。木の要求と帯の矛盾を検出する（Issue #191）。"""
    tr = pool["trees"]; need = tr["total"][0]
    min_w, per = X.const_num("tree.min-band-px"), X.const_num("tree.min-area-per-tree")
    if p.get("tree_zones"):
        area = 0
        for z in p["tree_zones"]:  # plan 単位の rect を画素へ射影してから px² で数える
            bx0, by0, bx1, by1 = _bbox([M.rect_poly(z["rect"])])
            area += max(0, bx1 - bx0) * max(0, by1 - by0)
        what = "tree_zones の面積（画素に射影）"
    else:
        t = tree_band_sizes(p)
        if not t:
            return None
        w_, h_ = t["sx1"] - t["sx0"], t["by1"] - t["by0"]
        area = sum(wd * ln for wd, ln in ((t["top"], w_), (t["bottom"], w_), (t["left"], h_), (t["right"], h_)) if wd >= min_w)
        what = f"木の帯（奥{t['top']}px・手前{t['bottom']}px・左{t['left']}px・右{t['right']}px。幅{min_w}px未満は使えない）の面積"
    if area / max(need, 1) < per:
        return f"屋外MAP: {what} {area}px² が木の最小本数 {need} 本（1本あたり {per}px² 必要）を満たせない。plan の tree_zones に民家の裏・塀の根元など実面積のある矩形を置くか、木の本数を MAP に合わせる（Issue #191）"
    return None


def walk_names(p):
    """歩ける床（walkable で名前があるもの）の名前を『・』で並べた語。屋外MAPの文面の『歩く地面（○○）』に差し込む。名前が無ければ『歩く床』。"""
    names = []
    for f in p.get("floors", []):
        lb = (f.get("label") or "").strip()
        if f.get("walkable", True) and lb and lb not in names:
            names.append(lb)
    return "・".join(names) or "歩く床"


def box_names(p):
    """家具箱（OBJECTS）の名前を『・』で並べた語（重複は1つに）。箱が無ければ空。"""
    names = []
    for b in p.get("boxes", []):
        lb = (b.get("label") or b.get("id") or "").strip()
        if lb and lb not in names:
            names.append(lb)
    return "・".join(names)


def outdoor_pool_for_plan(p, pool):
    """屋外の装飾プールを plan に合わせた版にする（文面は台帳。ここは差し込みと出し分けだけ）。
    - 『{歩く地面}』『{箱}』をこの MAP の歩ける床・箱の名前にする（その MAP に無い参道・墓地・遊具などを出さない）
    - 全ての壁に look がある MAP は、LAYERS 建物行・SURFACES の wall／roof／door をプール既定（寄棟・漆喰・灰色の瓦）でなく『壁ごとの look に従う』にする
    - 全ての床に look がある MAP は、SURFACES floor を『FLOORS の look に従う』にする
    - plan の窓が0件の MAP は、SURFACES window をプール既定（木の桟の窓）でなく『窓は描かない』にする（窓が実在する MAP は従来どおり）
    look が無い面があれば従来どおり既定を出す。屋外でないプールはそのまま返す。"""
    if not pool.get("outdoor"):
        return pool
    import copy
    q = copy.deepcopy(pool)
    walk, boxes = walk_names(p), box_names(p)
    sub = lambda t: t.replace("{歩く地面}", walk).replace("{箱}", boxes)  # noqa: E731
    walls_looked = bool(p.get("walls")) and all((w.get("look") or "").strip() for w in p["walls"])
    floors_looked = bool(p.get("floors")) and all((f.get("look") or "").strip() for f in p["floors"])
    if walls_looked:
        q["layers"]["building"]["look"] = X.text("PR.layer.building.from-look")
        for k in ("wall", "roof", "door"):
            if k in q["surfaces"]:
                q["surfaces"][k] = X.text("PR.surfaces." + k + ".from-look")
    if floors_looked and "floor" in q["surfaces"]:
        q["surfaces"]["floor"] = X.text("PR.surfaces.floor.from-look")
    if "window" in q["surfaces"]:  # 窓が0件ならプール既定の窓（細い木の桟…）を出さない（MAP KEYS『窓: 該当なし』・各壁の『窓は描かず』と矛盾する）
        if not p.get("windows"):
            q["surfaces"]["window"] = X.text("PR.surfaces.window.none")
    q["_all_look"] = walls_looked and floors_looked and not p.get("windows")  # SURFACES の各項目が全部『look に従う』（見出し行の出し分け）
    for ly in q["layers"].values():
        ly["look"] = sub(ly["look"]); ly["fixed"] = sub(ly["fixed"])
    q["allow"] = [sub(a) for a in q["allow"] if not ("{箱}" in a and not boxes)]
    q["forbid"] = [sub(a) for a in q["forbid"]]
    q["_walk"] = walk
    return q


def coord_section(p, pool):
    """幾何を画素座標で固定する節（plan とモックの射影から機械的に出す。手書き禁止）。画像 M.W x M.H_IMG・左上原点・x右・y下。文面は台帳『プロンプト文面』。"""
    tl, tr, br, bl = [tuple(map(float, q)) for q in M._DST]
    L = ["", X.text("PR.coord.head", W=M.W, H=M.H_IMG),
         X.text("PR.coord.slab-top", pts=_pts([tl, tr, br, bl])),
         X.text("PR.coord.slab-front", pts=_pts([bl, br, (br[0], br[1] + M.SLAB), (bl[0], bl[1] + M.SLAB)]))]
    L.append(X.text("PR.coord.slab-flute"))
    ws = p["walls"]
    exterior = any(w.get("kind") == "building" for w in ws)
    x0 = min(w["rect"][0] for w in ws); y0 = min(w["rect"][1] for w in ws); x1 = max(w["rect"][2] for w in ws); y1 = max(w["rect"][3] for w in ws)
    ground = [M.proj(x0, y0), M.proj(x1, y0), M.proj(x1, y1), M.proj(x0, y1)]
    # 外周の辺に接する横長の壁が無いMAP（屋外の道。辺は閉鎖の塀が部分的に覆うだけ）は高さ0（上端=接地線）。屋内はどちらの辺にも壁がある
    hb = max((w["h"] for w in ws if M.is_h(w) and w["rect"][1] == y0), default=0); hf = max((w["h"] for w in ws if M.is_h(w) and w["rect"][3] == y1), default=0)
    top = [M.proj(x0, y0, hb), M.proj(x1, y0, hb), M.proj(x1, y1, hf), M.proj(x0, y1, hf)]
    if exterior:  # 外観: 建物ごとに接地線と上端（屋根は上端の外形に収める）
        for w in ws:
            g_ = M.rect_poly(w["rect"]); t_ = M.rect_poly(w["rect"], w["h"])
            lb = w.get("label") or ""
            L.append(X.text("PR.coord.building" if lb else "PR.coord.building.nolabel", id=w["id"], **({"label": lb} if lb else {}), h=w["h"], ground=_pts(g_), top=_pts(t_), bbox=_bbox([g_, t_])))
    else:
        L.append(X.text("PR.coord.ground", pts=_pts(ground)))
        L.append(X.text("PR.coord.top", hb=hb, hf=hf, pts=_pts(top)))
        L.append(X.text("PR.coord.bbox", bbox=_bbox([ground, top])))
    for f in p["floors"]:
        L.append(X.text("PR.coord.floor", id=f["id"], pts=_pts(M.floor_img_poly(f))))
    for d in p["doors"]:
        _, panel, _ = M.door_geom(p, d)
        L.append(X.text("PR.coord.door", id=d["id"], pts=_pts(panel), bbox=_bbox([panel])))
    for w in p["windows"]:
        q = M.window_geom(p, w)
        L.append(X.text("PR.coord.window", id=w.get("id", ""), pts=_pts(q), bbox=_bbox([q])))
    for b in p["boxes"]:
        polys = [q for q, _, _ in M.box_polys(b["rect"], b["h"], b["color"])]
        L.append(X.text("PR.coord.box", id=b["id"], label=b.get("label") or "", bbox=_bbox(polys)))
    tr_ = pool["trees"]
    n_lo, n_hi = -(-tr_["total"][0] // 4), -(-tr_["total"][1] // 4)
    tb = tree_band_sizes(p)
    sx0, sy0, sx1, sy1, bx0, by0, bx1, by1 = (tb[k] for k in ("sx0", "sy0", "sx1", "sy1", "bx0", "by0", "bx1", "by1"))
    cnt = dict(tmin=tr_["total"][0], tmax=tr_["total"][1], pmin=tr_["pine"]["count"][0], pmax=tr_["pine"]["count"][1], dmin=tr_["deadtree"]["count"][0], dmax=tr_["deadtree"]["count"][1])
    if p.get("tree_zones"):  # 歩く地面の上に木を置かない MAP（外観）: 木を置ける帯を plan の矩形から出す。『各辺に○本』『四辺』は出さない
        zs = [f"{z['id']}: {_bbox([M.rect_poly(z['rect'])])}" for z in p["tree_zones"]]
        L += ["", X.text("PR.tree.head.zones", **cnt), X.text("PR.tree.zones", zones="／".join(zs), walk=walk_names(p))]
    else:
        L += ["", X.text("PR.tree.head", nlo=n_lo, nhi=n_hi, **cnt),
              X.text("PR.tree.bands", sy0=sy0, by0=by0, sx0=sx0, sx1=sx1, by1=by1, sy1=sy1, bx0=bx0, bx1=bx1)]
    pats = []
    for d in p["doors"]:
        patch, _, _ = M.door_geom(p, d)
        pats.append(f"{d['id']}: {_pts(M.rect_poly(patch))}")
    if pats:  # 床パッチ（戸口の前）が無い MAP は行ごと出さない（コロンの後が空の行を作らない）
        # 文面は既定が PR.keepout。プールが keepout を持てばそれ（例: 団地の室内は戸口の前が雪の地面でなく廊下の床）。差し込み口は {pats}
        L.append((pool.get("keepout") or X.text("PR.keepout", pats="{pats}")).replace("{pats}", "／".join(pats)))
    return L


def door_section(p):
    """戸口の個数と一覧を冒頭近くに固定する（見落とし防止。細い戸口ほど強調）。文面は台帳『プロンプト文面』。"""
    WN = {k: X.text("PR.door.wname." + k) for k in ("1person", "1.5people", "2people")}
    ds = [d for d in p["doors"] if not d.get("passage")]
    ps = [d for d in p["doors"] if d.get("passage")]
    form = (load_decor(p) or {}).get("door_form") or X.text("PR.door.form")  # 装飾プールの door_form（無ければ既定の文面）
    L = [X.text("PR.door.head", n=len(ds), form=form)]
    for d in ds:
        _, panel, _ = M.door_geom(p, d)
        w = M.wall_by_id(p, d["wall"])
        wd = d.get("width_class", M.WIDTH_DEFAULT)
        strong = X.text("PR.door.strong") if wd == "1person" else ""
        L.append(X.text("PR.door.item", id=d["id"], side=d["wall_side"], label=w.get("label") or w["id"], bbox=_bbox([panel]), wname=WN.get(wd, wd), units=f"{M.door_w(d):.0f}", strong=strong))
    if ps:
        L.append(X.text("PR.door.passage-note", n=len(ps)))
    return "\n".join(L)


def _obj_line(b, pool):
    blk = X.text("PR.object.blocked") if b.get("blocked") else X.text("PR.object.walkable")
    label = b.get("label") or X.text("PR.object.default-label")
    if pool:
        s = X.text("PR.object.pool", id=b["id"], label=label, h=b["h"], blk=blk, look=box_look(b, pool))
    else:
        s = X.text("PR.object.nopool", id=b["id"], label=label, h=b["h"], blk=blk)
    return s + (X.text("PR.object.prompt-suffix", prompt=b["prompt"]) if b.get("prompt") else "")


def scenery_sections(p):
    """屋外MAPの節: 景色としての扉・門（通行戸口と別枠）／境界物の帯／変化の語。文面は台帳『プロンプト文面』、中身は plan（台帳 MAP の plan追加JSON）の look から来る語だけ。"""
    blocks = []
    sds = p.get("scenery_doors", [])
    if sds:  # 一覧が空なら見出しも出さない（空見出しが『扉を足してよい』と読めるため）
        blocks.append([X.text("PR.door.scenery-head")] + [X.text("PR.door.scenery-item", id=sd["id"], where=sd.get("wall") or sd.get("boundary") or "", look=sd["look"]) for sd in sds])
    bds = p.get("boundaries", [])
    if bds:
        b = [X.text("PR.boundary.head")]
        for bd in bds:
            area = _bbox([M.rect_poly(bd["rect"])]) if bd.get("rect") else _bbox([[M.proj(x, y) for x, y in bd["poly"]]])
            b.append(X.text("PR.boundary.item", id=bd["id"], bbox=area, look=bd["look"]))
        blocks.append(b)
    if p.get("variation"):
        blocks.append([X.text("PR.variation.head")] + [X.text("PR.variation.item", v=v) for v in p["variation"]])
    L = []
    for b in blocks:
        L += (["" ] if L else []) + b
    L.append("")
    return L


def seam_section(p):
    """屋外MAPの節: 隣のMAPとのつなぎ目で道の縁の境界が続く（隣の境界の種類つき）。接続が無い・隣に境界が無いMAPでは出ない。"""
    ls = seam_lines(p)
    return ([X.text("PR.seam.head")] + ls + [""]) if ls else []


def build_prompt(p, key, ledger_text=""):
    """imagegen 編集用プロンプト（決定論）。モック=編集元1枚。原文束は台帳（build_map_prompt.rb）に依存するので別セクション。
    文面はすべて台帳『プロンプト文面』（oblique_text.text）。ここは並べ方と差し込みだけ。"""
    pool = load_decor(p)
    if pool:
        pool = outdoor_pool_for_plan(p, pool)
        L = [X.text("PR.title", version=PROMPT_VERSION, key=key), "",
             X.text("PR.role"),
             X.text("PR.geometry", text=pool["geometry_fixed"]),
             X.text("PR.fill", text=pool["fill_rule"]),
             *([X.text("PR.reality"), X.text("PR.reality.road-edge"), X.text("PR.reality.shosetsu")] + ([X.text("PR.reality.pool-note", text=pool["reality_note"])] if pool.get("reality_note") else []) + [X.text("PR.reality.miniature")] if pool.get("outdoor") else []),
             door_section(p),
             *(scenery_sections(p) + seam_section(p) if pool.get("outdoor") else []),
             X.text("PR.notext"), "",
             ledger_text, "",
             X.text("PR.layers-head")]
        L = L[:-1] + coord_section(p, pool) + ["", L[-1]]  # LAYERS 見出しの直前に座標節
        for k in DECOR_LAYER_KEYS:
            ly = pool["layers"][k]
            L.append(X.text("PR.layer", label=ly.get("label", k), look=ly["look"], fixed=ly["fixed"]) + (X.text("PR.layer.areafixed", area=pool["area"]) if k in ("desk", "slab_edge") else ""))
        tr = pool["trees"]
        L += ["", X.text("PR.trees-head", status=X.text("PR.trees-status.default") if tr.get("status") == "default" else X.text("PR.trees-status.fixed")),
              X.text("PR.trees-total.zones" if p.get("tree_zones") else "PR.trees-total", tmin=tr["total"][0], tmax=tr["total"][1], pmin=tr["pine"]["count"][0], pmax=tr["pine"]["count"][1], dmin=tr["deadtree"]["count"][0], dmax=tr["deadtree"]["count"][1]),
              X.text("PR.trees-kind", label=tr["pine"]["label"], look=tr["pine"]["look"]),
              X.text("PR.trees-kind", label=tr["deadtree"]["label"], look=tr["deadtree"]["look"]),
              X.text("PR.trees-forbid", forbid=tr["forbid"])]
        L += ["", X.text("PR.surfaces-head")] + ([X.text("PR.surfaces.outdoor-note.all-look" if pool.get("_all_look") else "PR.surfaces.outdoor-note")] if pool.get("outdoor") else []) + [X.text("PR.kv", k=k, v=v) for k, v in pool["surfaces"].items()]
        for w in p["walls"]:
            if w.get("look"):
                L.append(X.text("PR.wall-look", id=w["id"], look=w["look"]))
        L += ["", X.text("PR.objects-head.pool")]
        for b in p["boxes"]:
            L.append(_obj_line(b, pool))
    else:
        L = [X.text("PR.title", version=PROMPT_VERSION, key=key), "",
             X.text("PR.nopool.role"),
             X.text("PR.nopool.geometry"),
             X.text("PR.nopool.doors"),
             X.text("PR.nopool.notext"), "",
             X.text("PR.nopool.objects-head")]
        for b in p["boxes"]:
            L.append(_obj_line(b, None))
    for w in p["walls"]:
        if w.get("kind") == "partition":
            L.append(X.text("PR.partition", id=w["id"]))
    ops = [d for d in p["openings"]] + [d for d in p["doors"] if d.get("passage")]
    rps = [w for w in p["walls"] if w.get("kind") == "roof-passage"]
    if ops or rps:
        L += ["", X.text("PR.passages-head")]
        vmap = {v["id"]: v for v in M.opening_voids(p)}
        for o in ops:
            v = vmap.get(o["id"])
            co = X.text("PR.passage.coords", hull=_bbox([v['hull']]), ground=_pts(v['ground'])) if v else ""
            L.append(X.text("PR.passage.item", id=o["id"], wall=o["wall"], center=o["center"], width=f"{M.door_w(o) if 'width_class' in o or o in p['doors'] else M.DOOR_W:.0f}", co=co))
        for w in rps:
            L.append(X.text("PR.passage.roof", id=w["id"], label=w.get("label") or X.text("PR.passage.roof-default-label")))
    if p["doors"]:
        WN = {k: X.text("PR.door-widths.wname." + k) for k in ("1person", "1.5people", "2people")}
        L += ["", X.text("PR.door-widths-head")] + [X.text("PR.door-widths.item", id=d["id"], wname=WN[d.get("width_class", M.WIDTH_DEFAULT)], units=f"{M.door_w(d):.0f}", side=d["wall_side"]) for d in p["doors"]]
    if p["windows"]:
        L += ["", X.text("PR.windows-head")]
        for w in p["walls"]:
            ws = sorted([x for x in p["windows"] if x["wall"] == w["id"]], key=lambda x: x["center"])
            if not ws:
                continue
            ax = X.text("PR.windows.axis.h") if M.is_h(w) else X.text("PR.windows.axis.v")
            kinds = {M.WINDOW_KINDS[x["kind"]] for x in ws}
            lo, hi = ws[0].get("along_ref", [0, 1])
            pos = ", ".join(X.text("PR.windows.pos", i=i + 1, ratio=f"{(x['center']-lo)/(hi-lo):.2f}") for i, x in enumerate(ws))
            L.append(X.text("PR.windows.wall", id=w["id"], label=w.get("label") or w.get("kind", "wall"), n=len(ws), kinds="・".join(sorted(kinds)), axis=ax, pos=pos, sill=ws[0]["sill"], h=ws[0]["height"], w=ws[0]["width"]))
    for nw in p.get("no_window_walls", []):
        L.append(X.text("PR.windows.none", wall=nw["wall"], reason=nw.get("reason", "")))
    L += ["", X.text("PR.floors-head")] + [X.text("PR.floors.item" if f.get("label") else "PR.floors.item.nolabel", id=f["id"], **({"label": f["label"]} if f.get("label") else {}), walk=X.text("PR.floors.walkable") if f.get("walkable", True) else X.text("PR.floors.blocked")) + (X.text("PR.floors.look", look=f["look"]) if f.get("look") else "") for f in p["floors"]]
    if pool:
        L += ["", X.text("PR.allowed-head")] + [f"- {a}" for a in pool["allow"]]
        skips = [k["match"] for k in p.get("forbid_skip", [])]  # この MAP に当てはまらない禁止項目（reason つきで plan に明記したものだけ外す）
        fb = []
        for a in pool["forbid"]:
            if any(m_ in a for m_ in skips):  # 外した行が『歩く地面への新規物』なら、この MAP の歩く床の名前で『木・雪山・電柱を置かない』に言い直す
                if pool.get("_walk") and "歩く地面（" in a:
                    fb.append(X.text("PR.forbid.walk-zones", walk=pool["_walk"]))
                continue
            fb.append(a)
        if pool.get("outdoor"):  # 屋外の全MAP共通（決定 SIT.road-edge-solid-boundary・SIT.shosetsu-hole-only）。MAP ごとの plan には書かせない
            fb += [X.text("PR.forbid.road-edge"), X.text("PR.forbid.shosetsu"), X.text("PR.forbid.miniature")]
        L += ["", X.text("PR.forbidden-head")] + [f"- {a}" for a in fb]
    L += ["", X.text("PR.assumptions-head")] + [f"- {a}" for a in p.get("assumptions", [])]
    return "\n".join(L) + "\n"


# ---------------------------------------------------------------- manifest
def load_manifest(path):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {"schema": "sit-oblique-manifest/1", "stages": {}}


def save_manifest(path, m):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(m, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")


def build_one(plan_path, outroot, variant=None, from_stage=None, force=False, log=print):
    p = M.load_plan(plan_path, variant)
    key = p["map_id"]
    out = os.path.join(outroot, key)
    os.makedirs(out, exist_ok=True)
    mpath = os.path.join(out, "manifest.json")
    man = load_manifest(mpath)
    miss = LQ.missing_keys(key)
    if miss:  # 必須キーが全部埋まっているMAPだけを起動する（足りないキーを一覧で報告）
        log(f"[{key}] 必須キー欠落のため起動しない（docs/ledger の必須キー表）:")
        for m_ in miss:
            log("   MISSING: " + m_)
        return man, ["必須キー欠落: " + "; ".join(miss)]
    ledger_text, ledger_mat = LQ.sections(key, p.get("depends_on", []))
    unadopted = [d for d, pth in [(d_, pth_) for d_, pth_, _ in LQ.Ledger().references(key, p.get("depends_on", []))] if not pth]
    blocked_base = LQ.base_of(key) if variant and LQ.base_of(key) in unadopted else ""  # 基準の採用待ち（#193）
    plan_sha = sha_file(plan_path) + (f"+{variant}" if variant else "")
    tool_mock = src_sha("oblique_mock.py")
    tool_topo = src_sha("oblique_mock.py", "oblique_topology.py")
    man.update({"map_id": key, "plan": os.path.relpath(plan_path, REPO), "plan_sha256": plan_sha,
                "ledger": {"tables": "docs/ledger/*.yaml", "row_id": re.sub(r"-(kids|fire|burnt|wc)$", "", key), "era_suffix": variant,
                           "decisions": ledger_mat["decisions"], "inherits": ledger_mat["inherits"], "references": ledger_mat["refs"],
                           "input_sha": sha_bytes((ledger_text + json.dumps(ledger_mat, sort_keys=True)).encode())}})
    inputs = {"validate": sha_bytes((plan_sha + tool_mock + src_sha("oblique_build.py")).encode()),
              "mock": sha_bytes((plan_sha + tool_mock).encode()), "wire": sha_bytes((plan_sha + tool_topo).encode()),
              "mask": sha_bytes((plan_sha + tool_mock).encode()), "occlusion": sha_bytes((plan_sha + tool_mock).encode()),
              "prompt": prompt_input_sha(plan_sha, ledger_text, ledger_mat)}
    dirty = bool(force)
    errors = []
    for st in STAGES:
        if from_stage == st:
            dirty = True
        rec = man["stages"].get(st, {})
        fresh = (rec.get("input_sha") == inputs[st] and all(os.path.exists(os.path.join(out, o)) and sha_file(os.path.join(out, o)) == h for o, h in rec.get("outputs", {}).items()) and rec.get("status") in ("ok", "blocked"))
        if fresh and not dirty:
            log(f"[{key}] {st}: skip（入力 hash 同じ）")
            if st == "validate" and rec.get("status") == "ok":
                pass
            continue
        dirty = True  # 以降は再実行
        if st == "validate":
            errs, warns = validate_plan(p)
            man["stages"][st] = {"input_sha": inputs[st], "status": "error" if errs else "ok", "outputs": {}, "errors": errs, "warnings": warns}
            log(f"[{key}] validate: {'ERROR ' + str(len(errs)) if errs else 'ok'}（警告・既定要確認 {len(warns)}）")
            for e in errs:
                log("   ERROR: " + e)
            if errs:
                errors = errs
                # 古いプロンプトを残さない: validate エラーでは再生成されないので、前回のプロンプト記録は失効にし、ファイルも消す（起動判定は stale を拒否する）
                old_pr = man["stages"].get("prompt")
                if old_pr is not None:
                    for o in old_pr.get("outputs", {}):
                        if os.path.exists(os.path.join(out, o)):
                            os.remove(os.path.join(out, o))
                    man["stages"]["prompt"] = {"status": "stale", "outputs": {}, "reason": "validate エラーのため前回のプロンプトは失効（ファイルも削除）。エラーを直して oblique_build.py を再実行する"}
                save_manifest(mpath, man)
                return man, errs
            continue
        files, extra = [], {}
        if st == "mock":
            files = M.write_mock(p, out)
        elif st == "wire":
            fn = f"wire-{key}.png"
            T.wire_single(p, os.path.join(out, fn), None)
            files = [fn]
        elif st == "mask":
            files, doc = M.write_mask(p, out)
            extra = {"white_components": doc["white_components"], "exit_components": doc["exit_components"]}
        elif st == "occlusion":
            files = M.write_occlusion(p, out)
        elif st == "prompt":
            text = build_prompt(p, key, ledger_text)
            fn = f"{key}-edit-prompt.txt"
            with open(os.path.join(out, fn), "w", encoding="utf-8") as f:
                f.write(text)
                f.write("\n" + X.text("PR.trailer.head") + "\n")
                f.write(X.text("PR.trailer.counts", nd=len(ledger_mat['decisions']), ni=len(ledger_mat['inherits'])) + "\n")
                if unadopted:
                    f.write(X.text("PR.trailer.draft", maps=", ".join(unadopted)) + "\n")
                    if blocked_base:
                        f.write(X.text("PR.trailer.blocked-base", base=blocked_base) + "\n")
            files = [fn]
            extra = {"unadopted_dependencies": unadopted, **({"blocked_base": blocked_base} if blocked_base else {})}
        man["stages"][st] = {"input_sha": inputs[st], "status": "ok" if st != "prompt" or not extra.get("unadopted_dependencies") else "blocked",
                             "outputs": {fn: sha_file(os.path.join(out, fn)) for fn in files}, **extra}
        log(f"[{key}] {st}: 実行 → {', '.join(files)}")
    save_manifest(mpath, man)
    return man, errors


def adopt(plan_path, outroot, image, take, variant=None, canonical=None):
    p = M.load_plan(plan_path, variant)
    key = p["map_id"]
    out = os.path.join(outroot, key)
    mpath = os.path.join(out, "manifest.json")
    man = load_manifest(mpath)
    im = Image.open(image)
    if im.size != (M.W, M.H_IMG):
        sys.exit(f"採用画像の寸法が {M.W}x{M.H_IMG} でない: {im.size}（リサイズで通さない。例外は kako-jun の承認＋記録）")
    pr = man["stages"].get("prompt", {})
    mk = man["stages"].get("mock", {})
    if not pr or not mk:
        sys.exit("先に prompt・mock 段を実行する")
    man["adoption"] = {"image": os.path.relpath(image, REPO) if os.path.abspath(image).startswith(REPO) else image, "image_sha256": sha_file(image),
                       "size": list(im.size), "take": take, "prompt_sha256": next(iter(pr["outputs"].values())), "mock_clean_sha256": mk["outputs"].get(f"{key}-clean.png"),
                       "plan_sha256": man["plan_sha256"]}
    if canonical:  # 正本パス（確定画像。後続MAPの参考画像として自動で渡される）
        if not os.path.exists(os.path.join(REPO, canonical)):
            sys.exit(f"正本パスが無い: {canonical}")
        man["adoption"]["canonical"] = canonical
        man["adoption"]["canonical_sha256"] = sha_file(os.path.join(REPO, canonical))
    save_manifest(mpath, man)
    print(f"[{key}] adopt 記録: take {take} sha256 {man['adoption']['image_sha256'][:12]}…")


def verify(man, key):
    a = man.get("adoption")
    if not a:
        return "未採用"
    cur_plan = man.get("plan_sha256")
    return "採用済み・最新" if a["plan_sha256"] == cur_plan else "採用後にスペックが変わった（再生成が要る）"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("target", help="PLAN.json、または --all/--status 時は connections.json")
    ap.add_argument("--variant")
    ap.add_argument("--out", help="出力ルート（既定: スペックと同じディレクトリ）")
    ap.add_argument("--from", dest="from_stage", choices=STAGES)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--adopt")
    ap.add_argument("--take", type=int, default=1)
    ap.add_argument("--canonical", help="--adopt 時: 正本パス（リポ相対。WebP 等）。確定の印になり、依存する MAP の参考画像に使われる")
    a = ap.parse_args()
    if a.all or a.status:
        base = os.path.dirname(os.path.abspath(a.target))
        out = a.out or base
        with open(a.target, encoding="utf-8") as f:
            C = json.load(f)
        jobs = []
        for fn in C["plans"]:
            pp = os.path.join(base, fn)
            jobs.append((pp, None))
            with open(pp, encoding="utf-8") as f:
                for v in json.load(f).get("variants", {}):
                    jobs.append((pp, v))
        if a.status:
            for pp, v in jobs:
                p = M.load_plan(pp, v)
                mp = os.path.join(out, p["map_id"], "manifest.json")
                man = load_manifest(mp)
                st = {k: man["stages"].get(k, {}).get("status", "-") for k in STAGES}
                print(p["map_id"], st, verify(man, p["map_id"]))
            return
        bad = 0
        for pp, v in jobs:
            _, errs = build_one(pp, out, v, a.from_stage, a.force)
            bad += bool(errs)
        cerr, by_area = check_area_consistency(base)
        for ar, maps in by_area.items():
            print(f"[area:{ar}] area_fixed を継承する MAP: {', '.join(maps)}")
        for e_ in cerr:
            print(f"[area] ERROR: {e_}")
        bad += bool(cerr)
        # 接続図（全MAP横断）。入力 hash で skip
        cm = os.path.join(out, "connection-manifest.json")
        h = sha_bytes((sha_file(a.target) + "".join(sha_file(os.path.join(base, fn)) for fn in C["plans"]) + src_sha("oblique_mock.py", "oblique_topology.py")).encode())
        cur = load_manifest(cm)
        outs = ["connection-diagram.png", "overview.png", "connections.md", "windows.md"]
        if not a.force and cur.get("input_sha") == h and all(os.path.exists(os.path.join(out, o)) for o in outs) and not a.from_stage:
            print("[connections] diagram: skip（入力 hash 同じ）")
        else:
            probs = T.build(a.target, out)
            cur = {"schema": "sit-oblique-manifest/1", "input_sha": h, "problems": probs, "outputs": {o: sha_file(os.path.join(out, o)) for o in outs}}
            save_manifest(cm, cur)
            print("[connections] diagram: 実行 → " + ", ".join(outs), "| 問題:", probs or "なし")
            bad += bool(probs)
        sys.exit(1 if bad else 0)
    out = a.out or os.path.dirname(os.path.abspath(a.target))
    if a.adopt:
        adopt(a.target, out, a.adopt, a.take, a.variant, a.canonical)
        return
    _, errs = build_one(a.target, out, a.variant, a.from_stage, a.force)
    sys.exit(1 if errs else 0)


if __name__ == "__main__":
    main()
