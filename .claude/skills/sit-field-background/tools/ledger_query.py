"""台帳（docs/ledger/*.yaml）から MAP 1枚分のプロンプト材料を JOIN して決定論で出す。

同じ表・同じ入力なら同じ出力（行は主キー・表の並び順で固定）。決定は status（ready か否か）に依存せず必ず入れる。
  uv run python3 ledger_query.py MAP_ID          # 台帳節（edit-prompt に入る文）を表示
  uv run python3 ledger_query.py --missing MAP_ID # 必須キーの欠落（Ruby の検証器に委譲）
"""
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ledger_io as L  # noqa: E402
import oblique_text as X  # noqa: E402

VARIANT_RE = re.compile(r"-(kids|fire|burnt|wc)$")


def base_of(map_id):
    return VARIANT_RE.sub("", map_id)


def expand_maps(spec):
    out = []
    for tok in L.split_list(spec):
        m = re.match(r"^TRM-(\d\d)\.\.TRM-(\d\d)$", tok)
        out += [f"TRM-{n:02d}" for n in range(int(m.group(1)), int(m.group(2)) + 1)] if m else [tok]
    return out


def targets(map_id, spec):
    """決定の対象MAP列がこのMAPを含むか。基準ID（TRM-05）は時期差分（-kids など）にも及ぶ。"""
    toks = expand_maps(spec)
    return map_id in toks or base_of(map_id) in toks


class Ledger:
    def __init__(self):
        relevant = ("エリア", "MAP", "建物", "建物部位", "建物窓列", "建物関係", "建物時期差分",
                    "端", "接続", "要素", "窓", "素材", "採用要素", "決定", "語彙", "MAP仕様", "MAP契約", "特殊遷移", "体内幾何", "制作規約")
        self.T = {t: L.read(t) for t in relevant}

    def row(self, table, key, val):
        return next((r for r in self.T[table] if r[key] == val), None)

    def decisions(self, map_id):
        return [d for d in self.T["決定"] if d["状態"] == "有効" and d["プロンプト出力"] == "必須" and targets(map_id, d["対象MAP"])]

    def all_decisions_for(self, map_id):
        return [d for d in self.T["決定"] if d["状態"] == "有効" and targets(map_id, d["対象MAP"])]

    def map_row(self, map_id):
        return self.row("MAP", "MAP_ID", base_of(map_id))

    def buildings(self, map_id):
        m = self.map_row(map_id)
        out = []
        for bid in L.split_list(m["建物ID"]) if m else []:
            if bid in ("該当なし", "なし"):  # 建物の無いMAP（道・屋内の団地室など）
                continue
            b = self.row("建物", "建物ID", bid)
            parts = [p for p in self.T["建物部位"] if p["建物ID"] == bid]
            wins = [w for w in self.T["建物窓列"] if w["建物ID"] == bid]
            out.append((b, parts, wins))
        return out

    def inherits(self, map_id):
        return [a for a in self.T["採用要素"] if a["状態"].split("（")[0] in ("有効", "記録") and targets(map_id, a["継承先MAP"])]

    def references(self, map_id, depends):
        """依存MAPの採用画像（参考画像として渡す）。戻り [(MAP, パス, sha256)]。未採用の依存MAPは (MAP, None, None)。"""
        out = []
        for d in depends:
            hit = [r for r in self.T["素材"] if r["所有者ID"] == d and r["状態"] == "採用" and r["種別"].startswith("背景") and r["パス"]]
            out.append((d, hit[0]["パス"], hit[0]["sha256"]) if hit else (d, None, None))
        return out

    def area(self, map_id):
        m = self.map_row(map_id)
        return self.row("エリア", "エリアID", m["エリアID"]) if m else None

    def free_texts(self, map_id, plan=None):
        """特徴(自由記述)。自由記述欄のある全表（エリア・MAP・建物・建物部位・建物窓列・建物関係・建物時期差分・端・接続・要素・窓・素材・採用要素）のうち
        このMAPに関わる行を、MAP → エリア → 建物 → 建物部位 → 建物窓列 → 建物関係 → 建物時期差分 → 要素 → 窓 → 端 → 接続 → 素材(採用) → 採用要素 の順で返す。
        （決定の自由記述は DECISIONS 節の行末に入る。verify_ledger.rb の check_free_text_tables が、自由記述欄のある表の取りこぼしを検出する）"""
        out = []
        m = self.map_row(map_id)
        if m and m[L.FREE]:
            out.append((f"MAP {m['MAP_ID']}", m[L.FREE]))
        ar = self.area(map_id)
        if ar and ar[L.FREE]:
            out.append((f"エリア {ar['エリアID']}", ar[L.FREE]))
        bids = []
        for b, parts, wins in self.buildings(map_id):
            bids.append(b["建物ID"])
            if b[L.FREE]:
                out.append((f"建物 {b['建物ID']}", b[L.FREE]))
            for p in parts:
                if p[L.FREE]:
                    out.append((f"部位 {p['部位ID']}", p[L.FREE]))
            for w in wins:
                if w[L.FREE]:
                    out.append((f"建物窓列 {w['窓列ID']}", w[L.FREE]))
        base = base_of(map_id)
        era = map_id[len(base) + 1:] if map_id != base else ""
        for r in self.T["建物関係"]:
            if (r["建物A"] in bids or r["建物B"] in bids) and r[L.FREE]:
                out.append((f"建物関係 {r['通番']}", r[L.FREE]))
        for r in self.T["建物時期差分"]:
            if r["建物ID"] in bids and r["時期"] == era and r[L.FREE]:
                out.append((f"建物時期差分 {r['建物ID']}/{r['時期']}/{r['部位ID']}", r[L.FREE]))
        for r in self.T["要素"]:
            if r["MAP_ID"] == base and r["適用時期"] in ("", era) and r[L.FREE]:
                out.append((f"要素 {r['要素ID']}", r[L.FREE]))
        for r in self.T["窓"]:
            if r["MAP_ID"] == base and r["適用時期"] in ("", era) and r[L.FREE]:
                out.append((f"窓 {r['窓ID']}", r[L.FREE]))
        for r in self.T["端"]:
            if r["MAP_ID"] == base and r["適用時期"] in ("", era) and r[L.FREE]:
                out.append((f"端 {r['端ID']}", r[L.FREE]))
        for r in self.T["接続"]:
            if (r["端A"].split(".")[0] == base or r["端B"].split(".")[0] == base) and r[L.FREE]:
                out.append((f"接続 {r['端A']}⇄{r['端B']}", r[L.FREE]))
        for r in self.T["素材"]:
            if base_of(r["所有者ID"]) == base and r["状態"] == "採用" and r[L.FREE]:
                out.append((f"素材 {r['素材ID']}", r[L.FREE]))
        for a in self.inherits(map_id):
            if a[L.FREE]:
                out.append((f"採用要素 {a['採用要素ID']}", a[L.FREE]))
        for table in ("MAP仕様", "MAP契約", "体内幾何"):
            for r in self.T[table]:
                if r["MAP_ID"] in (base, "GLOBAL") and r[L.FREE]:
                    out.append((f"{table} {r[L.SCHEMA[table][0]]}", r[L.FREE]))
        for r in self.T["特殊遷移"]:
            if (r["起点MAP"] == base or base in L.split_list(r["到着MAP"])) and r[L.FREE]:
                out.append((f"特殊遷移 {r['遷移ID']}", r[L.FREE]))
        return out


def missing_keys(map_id):
    """必須キーの欠落（Ruby の検証器に委譲。空なら起動してよい）。

    閉じる側に倒す: 『終了コード1・stderr 空・欠落行あり』だけを欠落とみなす。『終了コード0・出力なし』だけが OK。
    Ruby の例外（終了コード1・stdout 空・stderr にバックトレース）や、それ以外の組み合わせは RuntimeError で止める
    （例外を『欠落なし』と読んでゲートを素通しさせない）。
    """
    script = os.path.join(L.REPO, "scripts", "ledger_required_keys.rb")
    r = subprocess.run(["ruby", script, base_of(map_id)], capture_output=True, text=True, timeout=60)
    lines = [x for x in r.stdout.splitlines() if x.strip()]
    if r.returncode == 0 and not lines and not r.stderr.strip():
        return []
    if r.returncode == 1 and lines and not r.stderr.strip():
        return lines
    raise RuntimeError(f"{map_id}: 必須キー検査(ledger_required_keys.rb)が異常終了した（exit {r.returncode}）。ゲートを開けないため停止: "
                       f"{(r.stderr.strip() or r.stdout.strip())[:300]}")


def sections(map_id, depends=None):
    """edit-prompt に入れる台帳節（テキスト）と、入力ハッシュに入れる材料を返す。"""
    led = Ledger()
    m = led.map_row(map_id)
    if m is None:
        raise KeyError(f"{map_id}: MAP表に行が無い")
    L_ = []
    ar = led.area(map_id)
    L_ += ["LEDGER（docs/ledger/*.yaml が唯一のマスター。決定・建物・継承要素は status（ready か否か）に関係なく全件入れる）:", ""]
    L_.append(f"AREA FIXED（エリア『{ar['名称']}』の必須キー。全MAP共通・変えない）:")
    for k in ("机の天面の材質", "台座の素材", "木の種類", "外周の装飾方針"):
        v = led.T["語彙"]
        en = next((x["英語断片"] for x in v if x["グループ"] == k and x["値"] == ar[k]), "")
        L_.append(f"- {k}: {ar[k]}" + (f"（{en}）" if en else ""))
    L_ += ["", f"MAP KEYS（{m['MAP_ID']} の必須キー）:"]
    for k in ("屋内外", "床材", "壁材", "窓", "扉の意匠", "工作の材質", "時期差分"):
        L_.append(f"- {k}: {m[k]}")
    rules = [r for r in led.T["制作規約"] if r["対象ID"] in ("全体", m["エリアID"], base_of(map_id))]
    if rules:
        L_ += ["", "PRODUCTION RULES（台帳の制作規約・確度も引き継ぐ）:"]
        L_ += [f"- [{r['規約ID']}] {r['内容']}（{r['確度']}）" for r in rules]
    for b, parts, wins in led.buildings(map_id):
        side = m["表現する部位"]
        L_ += ["", f"BUILDING {b['建物ID']}（{b['名称']}。{side}を描く。屋内と外観は同じ行から導出）:",
               f"- 外形: {b['外形']}", f"- 屋根: {b['屋根']}", f"- 外壁: {b['外壁']}", f"- 窓列: {b['窓列']}", f"- 扉: {b['扉']}", f"- 材質: {b['材質']}"]
        for p in parts:
            L_.append(f"  - 部位 {p['部位ID']}（{p['部位種別']}{('・' + p['方角']) if p['方角'] else ''}・{p['状態']}）: {p['見た目']}")
    L_ += ["", "DECISIONS（このMAPが対象の有効な決定。逐語は台帳）:"]
    for d in led.decisions(map_id):
        extra = []
        if d["必須語"]:
            extra.append("必須語: " + d["必須語"].replace(";", "・"))
        if d["禁止語"]:
            extra.append("禁止語: " + d["禁止語"].replace(";", "・"))
        L_.append(f"- [{d['決定ID']}] {d['決定の要点']}" + (f"（{' / '.join(extra)}）" if extra else "") + (f" 特徴: {d[L.FREE]}" if d[L.FREE] else ""))
    inh = led.inherits(map_id)
    L_ += ["", "INHERITED ELEMENTS（継承する要素: 採用画像の良い点。参考画像とこの文の両方で伝える。漏らさず再現する）:"]
    L_ += [f"- [{a['採用要素ID']}] {a['要素']}: {a['内容']}（確認語: {a['確認語']}）" for a in inh] or ["- なし"]
    refs = led.references(map_id, depends or [])
    L_ += ["", "REFERENCE IMAGES（依存MAPの確定画像。位置・配置はモックが正本。扉・材質・家具・装飾のデザインだけを参考にし、構図はコピーしない）:"]
    L_ += [(f"- {d}: {p}（sha256 {s[:12]}）" if p else f"- {d}: 未確定（依存MAPが採用されるまでこのMAPの生成は起動しない）") for d, p, s in refs] or ["- なし（依存MAPなし）"]
    base = base_of(map_id)
    if base != map_id and base in (depends or []):  # 同じ部屋・建物の別時期: 基準の確定画像の使い方（文面は台帳 プロンプト文面.PR.reference.base-era）
        L_.append(X.base_era_reference(base, map_id[len(base) + 1:]))
    ft = led.free_texts(map_id)
    if ft:
        L_ += ["", "FEATURES（固有の特徴（台帳の自由記述）。そのまま入れる）:"] + [f"- {who}: {t}" for who, t in ft]
    text = "\n".join(L_) + "\n"
    material = {"decisions": [d["決定ID"] for d in led.decisions(map_id)], "inherits": [a["採用要素ID"] for a in inh], "refs": [(d, s) for d, p, s in refs]}
    return text, material


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--missing":
        mk = missing_keys(sys.argv[2])
        print("\n".join(mk) if mk else "OK（必須キーは全部埋まっている）")
        sys.exit(1 if mk else 0)
    deps = None
    t, mat = sections(sys.argv[1], deps)
    print(t)
