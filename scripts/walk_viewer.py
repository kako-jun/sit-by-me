#!/usr/bin/env python3
"""歩行アニメーション ビューア生成。

人物 4 人 x 全形態 x 8 方向の歩行を静的 HTML で動かして目視確認する。
使い方: uv run python3 scripts/walk_viewer.py --out <出力ディレクトリ>
読み取り専用(リポの画像・台帳は変更しない)。出力先に img -> リポの画像 への symlink を作る。
再生成すれば最新の候補が反映される。
"""
import argparse
import html
import json
import re
from collections import Counter, OrderedDict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CHARS_DIR = REPO / "assets/images/characters"
CAND_DIR = CHARS_DIR / "shared/direction-candidates"
LEDGER = REPO / "docs/ledger/人物形態.yaml"
DEFAULT_OUT = "walk-viewer-out"

CHARS = OrderedDict([("C001", "オットン"), ("C002", "ナム"), ("C003", "シャー"), ("C004", "ペー子")])
DIRS = ["down", "downleft", "left", "upleft", "up", "upright", "right", "downright"]
FRAMES = [1, 2, 3]
AGES = ["kindergarten", "elementary", "teen", "midlife", "adult"]
AGE_JA = {"kindergarten": "幼稚園", "elementary": "小学生", "teen": "中学生", "midlife": "中年", "adult": "青年"}
MIRROR = {"downright": "downleft", "upright": "upleft"}
KINDS = ["正本", "候補", "反転", "なし"]

DIR_RE = "|".join(sorted(DIRS, key=len, reverse=True))
AGE_RE = "|".join(AGES)
# 正本: C001-walk-down-1 / C001-elementary-walk-down-1 / C001-adult-wheelchair-walk-down-1
CANON_RE = re.compile(rf"^(C\d{{3}})-(?:({AGE_RE})-)?(wheelchair-)?walk-({DIR_RE})-(\d)\.webp$")
# 候補: C004-adult-downleft-3-scale-v3
CAND_RE = re.compile(rf"^(C\d{{3}})-({AGE_RE})-({DIR_RE})-(\d)-(.+)\.webp$")
# 規則どおり(= 既知の標準形)の候補サフィックス
CAND_STD = re.compile(r"^(method-pilot|resume)(-v\d+)?$")


def scan():
    """canon[(c,age,wc,dir,frame)] = path, cand[...] = [paths]。例外名も返す。"""
    canon, cand, exceptions = {}, {}, []
    for c in CHARS:
        for p in sorted((CHARS_DIR / c / "walk").glob("*.webp")):
            m = CANON_RE.match(p.name)
            if not m:
                exceptions.append(f"[正本] 規則外: {p.relative_to(CHARS_DIR)}")
                continue
            _, age, wc, d, f = m.groups()
            age = age or "kindergarten"
            canon[(c, age, bool(wc), d, int(f))] = p
    for p in sorted(CAND_DIR.rglob("*")):
        if p.is_dir():
            exceptions.append(f"[候補] ディレクトリ(中身: {len(list(p.iterdir()))}件): {p.relative_to(CHARS_DIR)}")
            continue
        m = CAND_RE.match(p.name)
        if not m:
            exceptions.append(f"[候補] 規則外: {p.relative_to(CHARS_DIR)}")
            continue
        c, age, d, f, suffix = m.groups()
        if c not in CHARS:
            continue
        if not CAND_STD.match(suffix):
            exceptions.append(f"[候補] 非標準サフィックス: {p.name}")
        cand.setdefault((c, age, False, d, int(f)), []).append(p)
    return canon, cand, exceptions


def newest(paths):
    return max(paths, key=lambda p: (p.stat().st_mtime, p.name))


def resolve(canon, cand, key):
    """1コマ分の解決。None か dict(src,kind,name,flip,note)。"""
    c, age, wc, d, f = key
    cp = canon.get(key)
    cl = cand.get(key)
    if cp:
        note = ""
        if cl:
            n = newest(cl)
            if n.stat().st_mtime > cp.stat().st_mtime:
                note = f"候補あり(正本より新しい): {n.name}"
            else:
                note = f"候補あり: {n.name}"
        return dict(path=cp, kind="正本", flip=False, note=note)
    if cl:
        return dict(path=newest(cl), kind="候補", flip=False, note="")
    if d in MIRROR:
        mk = (c, age, wc, MIRROR[d], f)
        mp = canon.get(mk)
        if mp:
            return dict(path=mp, kind="反転", flip=True, note="左向き正本を反転")
        ml = cand.get(mk)
        if ml:
            return dict(path=newest(ml), kind="反転", flip=True, note="左向き候補を反転")
    return None


def ledger_forms():
    """台帳の (人物, 年齢, 衣装, 車椅子) 一覧(見出し用の補足)。"""
    out = []
    if not LEDGER.exists():
        return out
    cur = {}
    for line in LEDGER.read_text(encoding="utf-8").splitlines():
        m = re.match(r'^\s*(?:- )?"([^"]+)": "(.*)"\s*$', line)
        if not m:
            continue
        k, v = m.groups()
        if k == "形態ID" and cur:
            out.append(cur)
            cur = {}
        cur[k] = v
    if cur:
        out.append(cur)
    return out


def form_label(age, wc):
    return AGE_JA[age] + ("・車椅子" if wc else "")


def build():
    canon, cand, exceptions = scan()
    pages = OrderedDict()
    stats = OrderedDict()
    for c in CHARS:
        keys = {(k[1], k[2]) for k in list(canon) + list(cand) if k[0] == c}
        forms = sorted(keys, key=lambda t: (AGES.index(t[0]), t[1]))
        secs = []
        for age, wc in forms:
            cells = {}
            for d in DIRS:
                frs = {f: resolve(canon, cand, (c, age, wc, d, f)) for f in FRAMES}
                have = [f for f in FRAMES if frs[f]]
                if not have:
                    kind = "なし"
                else:
                    kinds = {frs[f]["kind"] for f in have}
                    if "反転" in kinds:
                        kind = "反転"
                    elif "候補" in kinds:
                        kind = "候補"
                    else:
                        kind = "正本"
                cells[d] = dict(frames=frs, kind=kind, missing=[f for f in FRAMES if not frs[f]] if have else [])
                stats.setdefault((c, form_label(age, wc)), Counter())[kind] += 1
            secs.append((age, wc, cells))
        pages[c] = secs
    return pages, stats, exceptions, canon


def rel(p):
    return "img/" + p.relative_to(CHARS_DIR).as_posix()


CSS = """
:root{--bg:#14161a;--fg:#e6e6e6;--mut:#9aa0a8;--card:#1d2026;--line:#333842;--acc:#7cc4ff;--stage:#14161a;--w:0;--h:0;--z:1}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:14px/1.5 system-ui,sans-serif}
header.bar{position:sticky;top:0;z-index:5;background:#0e1013;border-bottom:1px solid var(--line);padding:8px 16px;display:flex;flex-wrap:wrap;gap:14px;align-items:center}
header.bar label{display:flex;gap:6px;align-items:center;color:var(--mut)}
header.bar button,header.bar select{background:var(--card);color:var(--fg);border:1px solid var(--line);padding:4px 10px;border-radius:4px;cursor:pointer}
a{color:var(--acc)} main{padding:16px;max-width:1700px;margin:auto}
h1{font-size:20px} h2{font-size:17px;border-bottom:1px solid var(--line);padding-bottom:4px;margin-top:32px}
.compass{display:grid;grid-template-columns:repeat(3,max-content);gap:10px;justify-content:start}
.cell{background:var(--card);border:1px solid var(--line);border-radius:6px;padding:6px;display:flex;flex-direction:column;gap:4px;width:calc(var(--w)*var(--z)*1px + 14px);cursor:pointer}
.cell.paused{outline:2px solid #d8a13a}
.stage{position:relative;width:calc(var(--w)*var(--z)*1px);height:calc(var(--h)*var(--z)*1px);background:var(--stage)}
.stage img{position:absolute;bottom:0;left:50%;transform:translateX(-50%);width:auto;height:auto;zoom:var(--z);image-rendering:auto}
.stage img.flip{transform:translateX(-50%) scaleX(-1)}
.stage .guide{position:absolute;left:0;right:0;bottom:0;border-top:1px solid #ff3b6b;display:none;pointer-events:none}
body.guides .stage .guide{display:block}
.stage .none{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;color:#ff8a8a;font-size:20px;border:2px dashed #7a3a3a}
.meta{font-size:12px;color:var(--mut);word-break:break-all}
.tag{display:inline-block;padding:0 6px;border-radius:3px;font-size:12px;color:#000}
.tag.k0{background:#7be39a}.tag.k1{background:#ffd166}.tag.k2{background:#7cc4ff}.tag.k3{background:#ff8a8a}
.center{display:flex;align-items:center;justify-content:center;color:var(--mut);text-align:center}
table{border-collapse:collapse} td,th{border:1px solid var(--line);padding:3px 10px;text-align:right} th{background:var(--card)} td:first-child,th:first-child{text-align:left}
.note{color:var(--mut)} .ex li{font-family:monospace;font-size:12px}
"""

BAR = """
<header class="bar">
<span><a href="index.html">index</a>__NAV__</span>
<button id="pp">全体 停止</button>
<label>速度 <input id="fps" type="range" min="1" max="24" value="6"><span id="fpsv">6</span> fps</label>
<label>拡大 <input id="zoom" type="range" min="1" max="3" step="0.25" value="1"><span id="zoomv">1</span>x</label>
<label>背景 <select id="bg"><option value="#14161a">暗色</option><option value="#ffffff">白</option><option value="chk">市松</option><option value="#4f7a3a">緑の地面</option></select></label>
<label><input id="gd" type="checkbox"> 足元ガイド線</label>
<span class="note">セルをクリックで個別に一時停止</span>
</header>
"""

JS = """
const SEQ=[0,1,2,1];let tick=0,playing=true,timer=null;
const cells=[...document.querySelectorAll('.cell[data-frames]')].map(el=>({el,fr:JSON.parse(el.dataset.frames),img:el.querySelector('img'),now:el.querySelector('.now'),paused:false}));
function show(c){const fr=c.fr;if(!fr.length)return;
 // 欠けコマがある場合は存在するコマだけを順に回す
 const idx=fr.length>=3?SEQ[tick%4]:(tick%fr.length);const g=fr[idx];
 c.img.src=g.s;c.img.classList.toggle('flip',g.f);c.now.textContent='コマ'+g.n+': '+g.name;}
function step(){tick++;cells.forEach(c=>{if(!c.paused)show(c)});}
function restart(){clearInterval(timer);if(playing)timer=setInterval(step,1000/(+document.getElementById('fps').value));}
cells.forEach(c=>{c.el.addEventListener('click',()=>{c.paused=!c.paused;c.el.classList.toggle('paused',c.paused)});show(c)});
const $=id=>document.getElementById(id);
$('pp').onclick=()=>{playing=!playing;$('pp').textContent=playing?'全体 停止':'全体 再生';restart()};
$('fps').oninput=e=>{$('fpsv').textContent=e.target.value;restart()};
$('zoom').oninput=e=>{$('zoomv').textContent=e.target.value;document.documentElement.style.setProperty('--z',e.target.value)};
$('bg').onchange=e=>{const v=e.target.value;const r=document.documentElement.style;
 if(v==='chk'){r.setProperty('--stage','repeating-conic-gradient(#bbb 0 25%,#fff 0 50%) 0 0/16px 16px')}else r.setProperty('--stage',v)};
$('gd').onchange=e=>document.body.classList.toggle('guides',e.target.checked);
restart();
"""


def page(title, body, nav=""):
    return (f"<!doctype html><html lang=\"ja\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
            f"<title>{html.escape(title)}</title><style>{CSS}</style></head><body>"
            f"{BAR.replace('__NAV__', nav)}<main>{body}</main><script>{JS}</script></body></html>")


def cell_html(d, cell):
    frs = cell["frames"]
    kind = cell["kind"]
    ki = KINDS.index(kind)
    avail = [(f, frs[f]) for f in FRAMES if frs[f]]
    data = [dict(s=rel(r["path"]), f=r["flip"], n=f, name=r["path"].name) for f, r in avail]
    if not avail:
        stage = '<div class="stage"><div class="none">なし</div><div class="guide"></div></div>'
        attr = ""
        extra = ""
    else:
        first = data[0]
        stage = (f'<div class="stage"><img src="{first["s"]}" alt="{d}"{" class=flip" if first["f"] else ""}>'
                 f'<div class="guide"></div></div>')
        attr = f" data-frames='{html.escape(json.dumps(data), quote=True)}'"
        notes = []
        if cell["missing"]:
            notes.append("欠けコマ: " + ",".join(map(str, cell["missing"])))
        kinds = Counter(r["kind"] for _, r in avail)
        if len(kinds) > 1:
            notes.append("混在: " + " ".join(f"{k}{n}" for k, n in kinds.items()))
        for _, r in avail:
            if r["note"]:
                notes.append(r["note"])
        extra = "".join(f'<div class="meta">{html.escape(n)}</div>' for n in dict.fromkeys(notes))
        extra += '<div class="meta now"></div>'
    return (f'<div class="cell"{attr}>{stage}<div><b>{d}</b> <span class="tag k{ki}">{kind}</span></div>{extra}</div>')


def compass(cells):
    order = [["upleft", "up", "upright"], ["left", None, "right"], ["downleft", "down", "downright"]]
    out = ['<div class="compass">']
    for row in order:
        for d in row:
            out.append(cell_html(d, cells[d]) if d else '<div class="center">8方向<br>(画面上の位置=向き)</div>')
    out.append("</div>")
    return "".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=DEFAULT_OUT)
    out = Path(ap.parse_args().out)
    out.mkdir(parents=True, exist_ok=True)
    link = out / "img"
    if link.is_symlink() or link.exists():
        link.unlink()
    link.symlink_to(CHARS_DIR)

    pages, stats, exceptions, canon = build()
    led = ledger_forms()
    nav = "".join(f' | <a href="{c}.html">{c} {n}</a>' for c, n in CHARS.items())

    sizes = {}
    try:
        from PIL import Image  # 任意。無ければ既定サイズ
    except Exception:
        Image = None

    for c, secs in pages.items():
        # セル枠サイズ = 人物ページ内で使う画像の最大寸法
        w = h = 0
        if Image:
            for _, _, cells in secs:
                for cell in cells.values():
                    for r in cell["frames"].values():
                        if r:
                            p = r["path"]
                            if p not in sizes:
                                with Image.open(p) as im:
                                    sizes[p] = im.size
                            w, h = max(w, sizes[p][0]), max(h, sizes[p][1])
        w, h = w or 310, h or 400
        body = [f'<h1>{c} {CHARS[c]} 歩行ビューア</h1>',
                '<p class="note">コマ順 1→2→3→2。正本=assets/images/characters/{id}/walk、候補=shared/direction-candidates(同キーは更新時刻が最新)。'
                '反転=左向きをCSSで左右反転(実ファイルなし)。</p>',
                f'<style>:root{{--w:{w};--h:{h}}}</style>']
        have = {(a, wc) for a, wc, _ in secs}
        missing_led = [f'{AGE_JA.get(r.get("年齢"), r.get("年齢"))}/{r.get("衣装")}/{"車椅子" if r.get("車椅子") == "はい" else "車椅子なし"}'
                       for r in led if r.get("人物ID") == c
                       and (r.get("年齢"), r.get("車椅子") == "はい") not in have]
        for age, wc, cells in secs:
            cnt = Counter(x["kind"] for x in cells.values())
            summ = " ".join(f"{k}{cnt[k]}" for k in KINDS if cnt[k])
            body.append(f'<h2>{form_label(age, wc)} <span class="note">({age}{"-wheelchair" if wc else ""}) {summ}</span></h2>')
            body.append(compass(cells))
        if missing_led:
            body.append('<h2>歩行素材が無い台帳上の形態</h2><p class="note">' + html.escape(" / ".join(sorted(set(missing_led)))) + "</p>")
        (out / f"{c}.html").write_text(page(f"{c} {CHARS[c]} 歩行", "".join(body), nav), encoding="utf-8")

    # index
    rows = ["<tr><th>人物</th><th>形態</th>" + "".join(f"<th>{k}</th>" for k in KINDS) + "<th>計</th></tr>"]
    tot = Counter()
    for (c, fl), cnt in stats.items():
        rows.append(f'<tr><td><a href="{c}.html">{c} {CHARS[c]}</a></td><td>{fl}</td>'
                    + "".join(f"<td>{cnt[k]}</td>" for k in KINDS) + f"<td>{sum(cnt.values())}</td></tr>")
        tot.update(cnt)
    rows.append("<tr><th>合計</th><th></th>" + "".join(f"<th>{tot[k]}</th>" for k in KINDS) + f"<th>{sum(tot.values())}</th></tr>")
    body = ["<h1>歩行アニメーション ビューア</h1>",
            "<ul>" + "".join(f'<li><a href="{c}.html">{c} {n}</a></li>' for c, n in CHARS.items()) + "</ul>",
            "<h2>集計(8方向セル単位)</h2><table>" + "".join(rows) + "</table>",
            "<h2>ファイル名の例外</h2><ul class=\"ex\">" + "".join(f"<li>{html.escape(e)}</li>" for e in exceptions) + "</ul>"]
    (out / "index.html").write_text(page("歩行ビューア", "".join(body), nav), encoding="utf-8")

    # コンソール集計
    print(f"{'char':6}{'form':14}" + "".join(f"{k:>5}" for k in KINDS))
    for (c, fl), cnt in stats.items():
        print(f"{c:6}{fl:14}" + "".join(f"{cnt[k]:>5}" for k in KINDS))
    print("TOTAL " + " ".join(f"{k}={tot[k]}" for k in KINDS), "cells=", sum(tot.values()))
    print("exceptions:")
    for e in exceptions:
        print("  " + e)
    print("out:", out)


if __name__ == "__main__":
    main()
