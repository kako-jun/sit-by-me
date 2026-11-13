#!/usr/bin/env python3
"""イベント台帳（docs/ledger/イベント/*.yaml）から、name-name の一枚絵フィールドで動く md を生成する（#250 第一歩）。

正本は台帳。出力（play/ 配下）は何度も書き換わる派生物で、手で編集しない。
scripts/preview_event.py はレビュー用の別物で、ここからは使わない。
build_ledger.py の `build` / `check` から呼ばれる。単体でも `uv run python3 scripts/field_md.py check`（鮮度・孤児・上書き防止の検査）が使える。

第一歩の範囲は E001〜E003（opening_battle / evacuation_after_play / play_cancelled_promise）と、全部入りサンプルの歩ける場面 sample_field（サンプル専用・暫定。台帳 サンプルMAP.yaml）。
TBD が残る台帳（状態=blocked）からも骨組みは作れるが、blocked は解除しない。

台帳の列（イベント台帳は既存の語に合わせる。許容値は下の定数で厳密に判定し、typo は FAIL にする）:
  背景画像・歩行マスク（assets/images からの相対）・出現位置（x,y）・発火条件（空 または 場面開始・1回）・
  戦闘背景（任意。assets/images からの相対。name-name の `戦闘背景=` に出す。空なら出さない＝戦闘は黒背景。配信用複製の fields/play/ のパス）・
  行き先（そのイベント末尾に [場面移動:] を足す先のイベントID）・暫定（注記の正本。生成物の先頭コメントに出る）。
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
EVENTS = ROOT / "docs/ledger/イベント"
OUT = ROOT / "play"
# name-name の worker は scriptsDir 直下 + サブディレクトリ1段だけを列挙する。
# play/ を scriptsDir にすれば、play/script.md（入口）・play/data.md・play/events/*.md が全部拾われる。
FORMS = ROOT / "assets/field/sit-character-forms.json"
TRIGGER_AUTO_ONCE = "場面開始・1回"  # 発火条件の許容値（空欄は「別イベントから起動」でトリガーなし）
# 「FF の見た目」の定義（作品全体で共通。台帳の列にはしない）。決定の出典:
#   戦闘は FF5・6 式・サイドビュー・ATB（待機/アクティブ）: docs/systems.md 7・14・25 行、decisions.md 170 行（kako-jun 2026-10-14）
#   窓は FF 風の青（縦グラデ・白枠・白文字。色だけをテーマにする）: docs/systems.md 22 行、decisions.md 171 行
#   キャラはアクスタ（板・台座・影。戦闘もフィールドの歩行絵も）: decisions.md 12・32 行
#   基本コマンドは わざ／まほう／どうぐ／にげる（「たたかう」は無い）: docs/systems.md（2026-10-15 決定）
#   コマンドの表示名は battle_command_labels で「じゅもん」→「まほう」にする（docs/systems.md。一枚絵フィールドで効くのは name-name #1154 の対応後）
#   コマンド窓は十字（battle_command_layout: cross。上・左・右・下 = battle_commands の並び順 = わざ・まほう・どうぐ・にげる。name-name docs/guide/controls.md「コマンド窓の配置と名前」。kako-jun 2026-11-14 #276）
#   未対応（一枚絵フィールドでは name-name が無視する。書かない）: battle_perspective / battle_horizon（遠近の擬似3D。docs/systems.md 戦闘節）。name-name 側の Issue（#1154）で追う
#   敵名窓: FF 式（battle_enemy_list: window）。戦闘開始・終了は FF5/6 風の遷移（battle_transition: ff）
# 戦闘背景（battle_background）は、採用済みのジオラマ背景が無いので書かない（別担当の準備待ち。黒で出さないための迂回は置かない）。
FF_LOOK = [
    "battle_layout: Side",
    "battle_presentation: ff",
    "battle_atb: on",
    "battle_atb_mode: wait",
    "window_style: ff-blue",
    "sprite_style: acrylic",
    "battle_enemy_list: window",
    "battle_transition: ff-mosaic",
    "battle_motion: snappy",
    "battle_enemy_grid: 6x2",
    "field_emotions: field/sit-field-emotions.json",
    "battle_commands: skill, spell, item, escape",
    "battle_command_labels: spell=まほう",
    "battle_command_layout: cross",
]
ENTRY_EVENT = "opening_battle"
FIELD_EVENTS = ("opening_battle", "evacuation_after_play", "play_cancelled_promise")
# 全部入りサンプルの歩ける場面（#276 / #250）。台帳 サンプルMAP.yaml（SMP-01 の1行。docs/demo/README.md）が正本。
# 場面ID は名前付き（発生順を埋め込まない）。サンプル専用・暫定で、本編の MAP・接続・エンカウントの決定は借りない・変えない。
SAMPLE_SCENE = "sample_field"
SAMPLE_NOTE = "サンプル専用・暫定"
# サンプル専用エンカウント（決定 DEMO.sample-road-encounter-switch。本編の「スマホ購入前の寺町では通常エンカウントなし」は変えない）。
# 率・群・敵の数値はすべて暫定（数値の正本は台帳に無く #237 で案を詰める）。戦闘が数ターンで終わる程度の仮値。
#   率 1/8: 歩き始めて数歩〜十数歩で遭遇する程度の、デモで確かめやすい値（DQ4 式の分母。name-name の docs/spec/markdown-v0.1.md「エンカウント」）。
#   敵は台帳 敵.yaml の実在の敵で、採用済み画像（assets/images/enemies/<ID>.webp）があるものだけ。
#   ドロップは付けない: 敵戦利品.yaml は全敵「未定」で、アイテム台帳に実在する落とし物が無いため（架空を作らない）。
SAMPLE_ENCOUNTER_RATE = "1/8"
SAMPLE_ENCOUNTER_GROUPS = ("M101", "M104", "M148", "M104+M148")
# (HP, ATK, DEF, AGI, EXP, GOLD)。M001 の 9999 とは別の、数ターンで終わる仮値。GOLD は name-name のキー名で、通貨は円（decisions.md 183 行）。
SAMPLE_ENEMY_STATS = {
    "M101": (90, 14, 0, 3, 12, 30),
    "M104": (50, 10, 0, 9, 8, 15),
    "M148": (70, 8, 0, 5, 10, 20),
}
# サンプル専用・暫定の味方の経験値表と成長（決定 SIT.currency-yen「経験値・レベルの概念を置く」。数値の正本は台帳に無く #237 で詰める）。
# name-name の書式: 経験値表=Lv1→2 から順の累計 exp（長さ+1 が上限 Lv）、成長=Lv が1上がるごとに足す能力値。
# 経験値は生存した味方に等分（端数切り捨て）。敵 EXP 8〜12 を4人で割る（1人あたり2〜3）ので、3〜4戦で Lv2 に届く仮値。
# 魔法の習得 Lv は変えない: 台帳 魔法.yaml に「Lv で覚える」魔法の決定が無く、新しい魔法は作らない（MAG-07・MAG-08 は Lv1 のまま）。
SAMPLE_EXP_TABLE = (8, 20, 40, 80)
SAMPLE_GROWTH = "hp+10, atk+2, def+1, agi+1"
PARTY = ("C001", "C002", "C003", "C004")
MONSTER_SPRITE = "enemies/{id}.webp"
FORM = "elementary"  # 歩行絵・戦闘ポーズが全員揃う時期。ERA-01 は幼稚園期なので暫定
FORMS_GENERATED_KEY = "_generated"  # 目録 JSON の生成物の印（name-name は未知キーを読まない）
MARKER = "<!-- 生成物。台帳が正本。編集しない。"  # 先頭の固定部分。続けて暫定の注記と -->
ID_RE = re.compile(r"[a-zA-Z0-9_-]+\Z")
# 数値は仮値。敵.yaml の M001「HP は極めて高い（数値は未決）」と矛盾しないよう、仮の大きな値を置いただけ。
PROVISIONAL_HP = {"monster": 9999, "party": 100}
# 仮の能力値（台帳に数値が無い）。ATB のゲージと攻撃が動くよう 0 以外にしただけで、バランスを意味しない。
PROVISIONAL_STATS = {"monster": {"ATK": 10, "DEF": 0, "AGI": 5}, "party": {"ATK": 20, "DEF": 5, "AGI": 10}}
# 台帳 魔法.yaml に実在する魔法のうち、基本の攻撃（無属性）と回復。効果の数値は台帳に無いので仮値（暫定）。
SPELLS = {"MAG-07": ("敵単体", "damage 40..60"), "MAG-08": ("味方単体", "heal 40..60")}


def _load(path):
    record = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(record, dict) or record.get("イベントID") != path.stem or not ID_RE.fullmatch(path.stem):
        raise SystemExit(f"{path.name}: イベントIDとファイル名が一致しません")
    return record


_TABLE_CACHE = {}


def _table(name):
    """台帳の表。素材.yaml が大きく parse が遅いので、内容のハッシュが同じなら parse し直さない（呼び出し側は書き換えない）。

    キーは内容の sha256（mtime・size は使わない: 同じ大きさの書き換えで古い値を返しうるため）。
    """
    path = ROOT / "docs/ledger" / f"{name}.yaml"
    raw = path.read_bytes()
    key = (str(path), hashlib.sha256(raw).hexdigest())
    if key not in _TABLE_CACHE:
        _TABLE_CACHE[key] = yaml.safe_load(raw.decode("utf-8"))
    return _TABLE_CACHE[key]


def _text(record, key):
    value = record.get(key)
    return str(value).strip() if value is not None else ""


def _position(record, key="出現位置"):
    match = re.fullmatch(r"(\d+),(\d+)", _text(record, key))
    if not match:
        raise SystemExit(f"{record['イベントID']}: {key} は x,y の形で書く: {_text(record, key)!r}")
    return f"@{match.group(1)},{match.group(2)}"


def _head(note):
    return f"{MARKER}{(' 暫定: ' + note) if note else ''} -->"


def _scene_title(record):
    return _text(record, "名称").replace("\n", " ") or record["イベントID"]


def _frontmatter(title, extra=()):
    return "\n".join(["---", "engine: name-name", f"title: {title}", *extra, "---"])


def _script(record, records, sample=None):
    """台帳の脚本。「行き先」があれば、イベント末尾に [場面移動:] を足す（到着位置は行き先の出現位置）。

    台帳に「行き先」が無く、サンプルMAP の起動イベントの最後（サンプルへ入る側）なら、生成器側で sample_field への
    [場面移動:] を足す（イベント台帳を変えない。行き先の書式は同じ）。
    """
    script = record["脚本"].rstrip()
    ident = record["イベントID"]
    target = _text(record, "行き先")
    if target:
        if target not in records or not _text(records[target], "出現位置"):
            raise SystemExit(f"{ident}: 行き先 {target} の台帳に出現位置がありません")
        destination = f"[場面移動: {target} {_position(records[target])}]"
    elif sample and sample["entry_from"] == ident:
        destination = f"[場面移動: {SAMPLE_SCENE} {sample['position']}]"
    else:
        return script
    lines = script.split("\n")
    closing = [i for i, line in enumerate(lines) if line == "[/イベント]"]
    if not closing:
        raise SystemExit(f"{ident}: [/イベント] が無く、場面移動を足せません")
    lines.insert(closing[-1], destination)
    return "\n".join(lines)


def sample_map(records):
    """台帳 サンプルMAP.yaml（1行）→ 歩ける場面の定義。画像は素材.yaml・戦闘背景.yaml の登録を正本として引く。

    背景=流用元MAP の「背景(基準)」で採用の素材（1件）。1MiB 超は fields/play/ の配信用複製を使う流儀だが、
    TRM-03 は約0.5MB なので登録パスをそのまま使う（超える場合は FAIL にして気づかせる）。
    歩行マスク=流用元MAP の「マスク」素材のうち `-mask.webp` で終わるもの（overlay は可視化用・traversal-edit は編集用）。
    戦闘背景=戦闘背景.yaml の 配信用複製（opening_battle の bg011 と同じ流儀）。
    出現位置=サンプルへ入る側の最後の起動イベントの出現位置。同じ背景・同じマスクを使う場面なので、そこは歩ける。
    （確認 2026-11-13: TRM-03 マスクの (1330,480) は白=歩行可。tests が画像で再確認する）
    """
    rows = _table("サンプルMAP")
    if len(rows) != 1:
        raise SystemExit(f"サンプルMAP は1行だけ（決定 DEMO.sample-single-map）: {len(rows)} 行")
    row = rows[0]
    source = row["流用元MAP"]
    assets = _table("素材")
    backgrounds = [a for a in assets if a["所有者ID"] == source and a["種別"] == "背景(基準)" and a["状態"] == "採用"]
    masks = [a for a in assets if a["所有者ID"] == source and a["種別"] == "マスク" and a["パス"].endswith("-mask.webp")]
    if len(backgrounds) != 1 or len(masks) != 1:
        raise SystemExit(f"サンプルMAP: {source} の採用済み背景(基準) と -mask.webp のマスクは1件ずつ必要（{len(backgrounds)}/{len(masks)}）")
    prefix = "assets/images/"
    paths = {"背景": backgrounds[0]["パス"], "マスク": masks[0]["パス"]}
    for kind, path in paths.items():
        if not path.startswith(prefix) or not (ROOT / path).is_file():
            raise SystemExit(f"サンプルMAP: {kind} の画像が実在しません: {path}")
    if (ROOT / paths["背景"]).stat().st_size > 1024 * 1024:
        raise SystemExit(f"サンプルMAP: 背景が 1MiB を超えます。fields/play/ の配信用複製を使う流儀に直してください: {paths['背景']}")
    battle = ""
    if row["戦闘背景"]:
        bgs = [b for b in _table("戦闘背景") if b["背景ID"] == row["戦闘背景"] and b["状態"] == "採用" and b["配信用複製"]]
        if len(bgs) != 1 or not (ROOT / prefix / bgs[0]["配信用複製"]).is_file():
            raise SystemExit(f"サンプルMAP: 戦闘背景 {row['戦闘背景']} の採用済み配信用複製が実在しません")
        battle = bgs[0]["配信用複製"]
    launch = [e for e in row["起動イベント"].split(";") if e]
    entry_from = launch[-1] if launch else ""
    if entry_from not in records:
        raise SystemExit(f"サンプルMAP: 起動イベントの最後 {entry_from!r} が play/ の場面にありません")
    entry = records[entry_from]
    # 背景だけでマスクが空などの不備は _scene_block が専用のメッセージで止める。ここは両方あるのに食い違う場合だけ
    if _text(entry, "背景画像") and _text(entry, "歩行マスク") and (
            _text(entry, "背景画像") != paths["背景"][len(prefix):] or _text(entry, "歩行マスク") != paths["マスク"][len(prefix):]):
        raise SystemExit(f"サンプルMAP: {entry_from} の背景・マスクが流用元 {source} の登録と違います（出現位置を借りられません）")
    encounter = row["エンカウント"] == "あり"
    return {
        "title": row["名称"], "background": paths["背景"][len(prefix):], "mask": paths["マスク"][len(prefix):], "battle": battle,
        "entry_from": entry_from, "position": _position(entry), "encounter": encounter, "source": source,
    }


def _scene_block(record, records, sample=None):
    ident = record["イベントID"]
    lines = [f"## {ident}: {_scene_title(record)}", ""]
    if _text(record, "背景画像"):
        if not _text(record, "歩行マスク"):
            raise SystemExit(f"{ident}: 背景画像 があるのに 歩行マスク がありません")
        battle_bg = _text(record, "戦闘背景")
        if re.search(r"[\s\]]", battle_bg):
            raise SystemExit(f"{ident}: 戦闘背景 は空白と ] を含められない: {battle_bg!r}")
        battle = f" 戦闘背景={battle_bg}" if battle_bg else ""
        lines.append(f"[フィールドマップ 背景={_text(record, '背景画像')} マスク={_text(record, '歩行マスク')}{battle}]")
        lines.append(f"[プレイヤー {_position(record)}]")
        start = _text(record, "発火条件")
        if start not in ("", TRIGGER_AUTO_ONCE):
            raise SystemExit(f"{ident}: 発火条件 は {TRIGGER_AUTO_ONCE!r} か空欄だけ: {start!r}")
        if start == TRIGGER_AUTO_ONCE:
            lines.append(f"[トリガー auto scene={ident} once=true]")
        lines.append("")
    lines.append(_script(record, records, sample))
    return "\n".join(lines)


def render_event(record, records, sample=None):
    head = _frontmatter(_text(record, "名称") or record["イベントID"], ["hidden: true"])
    return f"{head}\n{_head(_text(record, '暫定').replace(chr(10), ' '))}\n\n{_scene_block(record, records, sample)}\n"


def render_sample_field(sample):
    """歩ける場面 sample_field。マップ端の切り替えは作らない（決定 DEMO.sample-single-map）。NPC は出さない。"""
    head = _frontmatter(sample["title"], ["hidden: true"])
    note = (f"{SAMPLE_NOTE}。台帳 サンプルMAP.yaml（流用元 {sample['source']} の採用済み画像・マスクの流用。本編の MAP は借りない）。"
            "エンカウントの率・群・敵の数値は仮（数値の正本は #237）。出現位置はサンプルへ入る側のイベントの出現位置")
    lines = [f"## {SAMPLE_SCENE}: {sample['title']}", ""]
    battle = f" 戦闘背景={sample['battle']}" if sample["battle"] else ""
    lines.append(f"[フィールドマップ 背景={sample['background']} マスク={sample['mask']}{battle}]")
    if sample["encounter"]:
        lines.append(f"[エンカウント率: {SAMPLE_ENCOUNTER_RATE}]")
        lines.append(f"[エンカウント群: {', '.join(SAMPLE_ENCOUNTER_GROUPS)}]")
    lines.append(f"[プレイヤー {sample['position']}]")
    return f"{head}\n{_head(note)}\n\n" + "\n".join(lines) + "\n"


def sample_monster_ids(sample):
    if not sample["encounter"]:
        return set()
    ids = {m for g in SAMPLE_ENCOUNTER_GROUPS for m in g.split("+")}
    if ids - set(SAMPLE_ENEMY_STATS):
        raise SystemExit(f"エンカウント群に数値の無い敵がいます: {sorted(ids - set(SAMPLE_ENEMY_STATS))}")
    return ids


def _enemy_sizes():
    """敵ごとのサイズ区分（台帳 敵配置.yaml『名前・サイズ』の『（2x1）』表記。決定 SIT.enemy-size-classes）。

    数字（NxM）が無い値（『大型。区分は未定』など）は区分が決まっていないので無視し、警告を出す（書かない＝name-name の既定 1x1）。
    台帳に無い敵も書かない。サイズを推測で決めない。
    """
    sizes = {}
    for r in _table("敵配置"):
        text = str(r.get("名前・サイズ", ""))
        m = re.search(r"(\d+)x(\d+)", text)
        if m:
            sizes.setdefault(r["敵ID"], f"{m.group(1)}x{m.group(2)}")
        elif r["敵ID"] and re.search(r"区分|大型|中型|小型", text) and r["敵ID"] not in sizes:
            print(f"警告: {r['敵ID']} のサイズは数字の区分が無いため無視する（既定 1x1）: {text}", file=sys.stderr)
    return sizes


def render_script(records):
    entry = records[ENTRY_EVENT]
    head = _frontmatter("Sit by Me", FF_LOOK)
    body = [
        "## start: はじまり",
        "",
        f"[フィールド: {ENTRY_EVENT} {_position(entry)}]",
    ]
    note = "入口の座標は台帳 opening_battle の出現位置（暫定）"
    return f"{head}\n{_head(note)}\n\n" + "\n".join(body) + "\n"


def render_data(records, sample=None):
    enemies = {r["敵ID"]: r for r in _table("敵")}
    people = {r["人物ID"]: r for r in _table("人物")}
    monster_ids = sorted({m for r in records.values() for m in re.split(r"[,;、\s]+", _text(r, "敵")) if m} | (sample_monster_ids(sample) if sample else set()))
    head = _frontmatter("共通定義", ["hidden: true"])
    lines = [
        "## data: 共通定義",
        "",
        f"[人物の形態 目録={FORMS.relative_to(ROOT / 'assets')} 素材=characters]",
        f"[歩行絵 主人公 人物={PARTY[0]} 形態={FORM}]",
        # 操作画像（手のカーソル=実写的な白手袋・選択中の印=白い磁器の円錐。ドット絵にしない）: docs/systems.md 8・22 行、assets-policy.md UI素材
        "[操作画像 手=ui/hand-cursor-v1.webp 選択マーク=ui/select-mark-cone-v1.webp]",
        # 通貨は円（ギルにしない）: docs/decisions.md 183 行
        "[通貨名: 円]",
        # フィールドメニュー 9 項目と順序（ロードは入れない）: docs/systems.md 88 行
        "[メニュー: item, magic, equip, appstore, magicite, job, status, save, config]",
        "",
    ]
    sizes = _enemy_sizes()
    for mid in monster_ids:
        enemy = enemies[mid]
        if mid in SAMPLE_ENEMY_STATS:
            # サンプル専用の暫定値（SAMPLE_ENEMY_STATS）。台帳に実在し、採用済み画像のある敵だけ。
            if not str(enemy["画像状態"]).startswith("採用") or not (ROOT / "assets/images" / MONSTER_SPRITE.format(id=mid)).is_file():
                raise SystemExit(f"{mid}: 採用済みの画像がありません")
            hp, atk, dfn, agi, exp, gold = SAMPLE_ENEMY_STATS[mid]
            stats = [f"HP: {hp}", f"ATK: {atk}", f"DEF: {dfn}", f"AGI: {agi}", f"EXP: {exp}", f"GOLD: {gold}"]
        else:
            stats = [f"HP: {PROVISIONAL_HP['monster']}", *[f"{k}: {v}" for k, v in PROVISIONAL_STATS["monster"].items()]]
        lines += [
            f"[モンスター {mid}]",
            f"名前: {enemy['名称']}",
            *stats,
            *([f"サイズ: {sizes[mid]}"] if mid in sizes else []),
            f"スプライト: {MONSTER_SPRITE.format(id=mid)}",
            "[/モンスター]",
            "",
        ]
    magic = {r["魔法ID"]: r for r in _table("魔法")}
    for sid, (target, effect) in SPELLS.items():
        name = re.sub(r"[*]", "", magic[sid]["魔法名"]).split("（")[0].strip()
        lines += [f"[呪文 {sid}]", f"名前: {name}", "MP: 0", f"対象: {target}", f"効果: {effect}", "[/呪文]", ""]
    for cid in PARTY:
        # 劇戦闘への固定付与（最強級の魔法・アビリティ）は台帳に具体が無い（systems.md: 保留）ので書かない。
        lines += [
            f"[パーティ {cid}]",
            f"名前: {people[cid]['呼称']}",
            f"HP: {PROVISIONAL_HP['party']}",
            "MP: 0",
            *[f"{k}: {v}" for k, v in PROVISIONAL_STATS["party"].items()],
            *[f"習得: Lv1 {sid}" for sid in SPELLS],
            *([f"経験値表: {', '.join(map(str, SAMPLE_EXP_TABLE))}", f"成長: {SAMPLE_GROWTH}"] if sample and sample["encounter"] else []),
            f"人物: {cid}",
            f"形態: {FORM}",
            "[/パーティ]",
            "",
        ]
    note = "数値は台帳 opening_battle の暫定を参照（HP・ATK・DEF・AGI と魔法の効果は仮値）。魔法は台帳 魔法.yaml の MAG-07・MAG-08 だけ"
    if sample and sample["encounter"]:
        note += f"。{SAMPLE_NOTE}: M101・M104・M148 の HP・ATK・DEF・AGI・EXP・GOLD も仮値（M001 の仮値とは別。数値の正本は #237）。味方 C001〜C004 の経験値表・成長も暫定値（生存者への等分で3〜4戦で Lv2）"
    return f"{head}\n{_head(note)}\n\n" + "\n".join(lines).rstrip() + "\n"


def render_readme(records, sample=None):
    rows = ["| 生成ファイル | 正本 |", "|---|---|", "| [script.md](script.md)（入口） | 台帳 docs/ledger/イベント/%s.yaml の出現位置 |" % ENTRY_EVENT,
            "| [data.md](data.md) | 敵.yaml・人物.yaml・イベント台帳の敵（数値は opening_battle の暫定列を参照） |"]
    for ident in FIELD_EVENTS:
        rows.append(f"| [events/{ident}.md](events/{ident}.md) | [{ident}.yaml](../docs/ledger/イベント/{ident}.yaml) |")
    if sample:
        rows.append(f"| [events/{SAMPLE_SCENE}.md](events/{SAMPLE_SCENE}.md)（{SAMPLE_NOTE}。歩ける場面・エンカウント） | [サンプルMAP.yaml](../docs/ledger/サンプルMAP.yaml)（[docs/demo/README.md](../docs/demo/README.md)） |")
    return "\n".join([
        _head("各台帳の「暫定」列を参照"),
        "# play/（name-name の /play が読む md）",
        "",
        "**生成物。台帳が正本。編集しない。** `uv run python3 scripts/build_ledger.py build` で作り直す。",
        "name-name の worker が `scriptsDir=play` として `play/` 直下とサブディレクトリ1段（`events/`）の md を読む。",
        "暫定の項目と理由は各台帳の「暫定」列が正本（ここには複製しない）。台帳の状態は blocked のまま。",
        "",
        *rows,
        "",
        "## 途中の場面から始める（デモ・確認の手順）",
        "",
        "オープニングを毎回通らない。**再開点を選んで `?resume=` で開く**（セーブ JSON は台帳 `docs/ledger/再開点/` から生成）。",
        "",
        "1. `play/saves/<再開点ID>.save.json`（下の一覧）を選ぶ。",
        "2. /play を開くのと同じオリジンのコンソールで `localStorage.setItem('name-name-save-sit-by-me-0', <その JSON の中身>)`。",
        "3. `/play/sit-by-me?resume=0` を開く。",
        "",
        "| 再開点 | 内容 |",
        "|---|---|",
        *[f"| [{r}](saves/{r}.save.json) | {n} |" for r, n in resume_rows()],
        "",
        "セーブからの再開直後は、既定では場面開始のトリガーを起こさない。`*_start` の再開点は `field.fireAuto: true`（name-name Issue #1155）で、その場面のイベント（劇戦闘・約束の会話）を再開直後に起こす。#1155 が入るまでは歩けるだけ（各再開点の暫定に書く）。",
        "",
        "見た目の決定の一覧と、画面を見せてよい状態のチェックリスト: [demo-look-list.md](../docs/production/demo-look-list.md)",
        "",
        "人物の形態の目録（歩行絵・戦闘ポーズの一覧）: `assets/field/sit-character-forms.json`（素材のファイル名から生成）。",
        "",
    ]) + "\n"


def resume_rows():
    import resume_saves

    rows = []
    for path in sorted(resume_saves.DIR.glob("*.yaml")):
        r = yaml.safe_load(path.read_text(encoding="utf-8"))
        rows.append((path.stem, str(r["名称"]).replace("|", "/")))
    return rows



def provenance_sha(doc):
    """JSON 生成物の入力ハッシュ = `_provenance` を除いた本体の正規化 JSON の sha256。verify_ledger.rb が
    最上位の `_provenance.input_sha` と生成物表の入力ハッシュの一致を要求するため、本体から導く（自己参照を避ける）。"""
    body = {k: v for k, v in doc.items() if k != "_provenance"}
    return hashlib.sha256(json.dumps(body, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


def with_provenance(doc, indent=2):
    """`_provenance.input_sha` を最上位の先頭に付けた JSON テキストを返す。"""
    out = {"_provenance": {"input_sha": provenance_sha(doc)}, **doc}
    return json.dumps(out, ensure_ascii=False, indent=indent) + "\n"


def registered_sha(relative, output):
    """生成物表に登録する入力ハッシュ。JSON は provenance の値、それ以外は出力全体の sha256。"""
    if relative.endswith("sit-field-emotions.json"):
        return ""  # render_emotions のコメント参照
    if relative.endswith(".json"):
        return provenance_sha(json.loads(output.decode("utf-8")))
    return hashlib.sha256(output).hexdigest()


def forms_manifest(listing):
    """目録（name-name の frontend/scripts/gen_sit_character_forms.py と同じ形式。刀の項目は付けない）を作る純関数。

    listing: {人物ID: {"poses": [poses/ のファイル名], "walk": [walk/ のファイル名]}}。ファイル名だけで決まる（時刻・環境に依らない）。
    """
    poses_order = ["idle", "ready", "step", "swing-windup", "slash", "swing-followthrough", "cast", "special", "hurt", "down", "victory"]
    dirs = ["up", "down", "left", "right", "upleft", "upright", "downleft", "downright"]
    characters = {}
    for cid in sorted(listing):
        forms = {}
        pose_re = re.compile(rf"^{cid}-(?P<form>.+?)(?P<char>-character)?-(?P<pose>swing-windup|swing-followthrough|[a-z]+)\.webp$")
        for name in sorted(listing[cid]["poses"]):
            m = pose_re.match(name)
            if not m or m["pose"] not in poses_order:
                continue
            entry = forms.setdefault(m["form"], {"poses": {}, "walk": False})
            entry["poses"].setdefault("character" if m["char"] else "plain", []).append(m["pose"])
        walk_re = re.compile(rf"^{cid}-(?P<form>.+)-walk-(?P<dir>[a-z]+)-(?P<n>[123])\.webp$")
        walk = {}
        for name in listing[cid]["walk"]:
            m = walk_re.match(name)
            if m:
                walk.setdefault(m["form"], set()).add((m["dir"], m["n"]))
        for form, got in walk.items():
            if len(got) == len(dirs) * 3:
                forms.setdefault(form, {"poses": {}, "walk": False})["walk"] = True
        for entry in forms.values():
            for variant in entry["poses"]:
                entry["poses"][variant].sort(key=poses_order.index)
        characters[cid] = {**({"plainBaked": True} if cid == "C001" else {}), "forms": dict(sorted(forms.items()))}
    doc = {FORMS_GENERATED_KEY: "scripts/field_md.py が assets/images/characters の素材から生成。手で編集しない（#250）", "characters": characters}
    text = with_provenance(doc)
    text = re.sub(r"\[\s*((?:\"[a-z-]+\",?\s*)+)\]", lambda m: "[" + " ".join(m.group(1).split()).rstrip(",") + "]", text)
    return text


def render_forms():
    listing = {}
    for cid in PARTY:
        base = ROOT / "assets/images/characters" / cid
        listing[cid] = {"poses": [f.name for f in (base / "poses").glob(f"{cid}-*.webp")],
                        "walk": [f.name for f in (base / "walk").glob(f"{cid}-*-walk-*.webp")]}
    return forms_manifest(listing)


EMOTIONS = {"!": "exclaim", "?": "question", "...": "dots"}  # 採用済みの3枚（docs/field-emotion-registry.md）


def render_emotions():
    """フィールドの感情吹き出しの宣言 JSON（name-name の field_emotions。種類名 → 宣言）。素材が実在しない種類は FAIL。"""
    doc = {}
    for kind, name in EMOTIONS.items():
        rel = f"effects/field-emotion/field-emotion-{name}.png"
        if not (ROOT / "assets/images" / rel).is_file():
            raise SystemExit(f"感情吹き出しの素材がありません: assets/images/{rel}")
        doc[kind] = {"image": rel}
    # このファイルは種類名 → 宣言の形（name-name の field_emotions）なので、`_provenance` は足さない。
    # 入力ハッシュは登録せず（registered_sha が空）、鮮度は field_md.py check のバイト一致で見る。
    # （`_provenance` を足したときの name-name 側の警告の有無は未確認。）
    return json.dumps(doc, ensure_ascii=False, indent=2) + "\n"


def outputs():
    """[(生成物ID, 種別, 相対パス, 元の表, bytes)]。決定的（時刻・環境に依らない）。"""
    records = {ident: _load(EVENTS / f"{ident}.yaml") for ident in FIELD_EVENTS}
    sample = sample_map(records)
    # 場面 sample_field の再開点の位置は、生成器が導く出現位置（サンプルへ入る側のイベントの出現位置）と一致させる
    # （手書きの複製が E003 の出現位置の変更で取り残されないように）。
    import resume_saves
    for path in sorted(resume_saves.DIR.glob("*.yaml")):
        r = yaml.safe_load(path.read_text(encoding="utf-8"))
        if str(r.get("場面ID")) == SAMPLE_SCENE and "@" + str(r.get("位置")) != sample["position"]:
            raise SystemExit(f"{path.stem}: 位置 {r.get('位置')} がサンプルの出現位置 {sample['position'][1:]} と違います（{sample['entry_from']} の出現位置が正本）")
    source = "イベント台帳|敵|人物|サンプルMAP"
    items = [
        ("G-play-script", "name-name 入口md", "play/script.md", source, render_script(records)),
        ("G-play-data", "name-name 共通定義md", "play/data.md", source, render_data(records, sample)),
        ("G-play-readme", "play/ の説明", "play/README.md", source, render_readme(records, sample)),
    ]
    for ident in FIELD_EVENTS:
        items.append((f"G-play-event-{ident}", "name-name 場面md", f"play/events/{ident}.md", f"イベント台帳:{ident}", render_event(records[ident], records, sample)))
    items.append((f"G-play-event-{SAMPLE_SCENE}", "name-name 場面md", f"play/events/{SAMPLE_SCENE}.md", "サンプルMAP|素材|戦闘背景", render_sample_field(sample)))
    items.append(("G-play-field-emotions", "感情吹き出しの宣言JSON", "assets/field/sit-field-emotions.json", "assets/images/effects/field-emotion", render_emotions()))
    items.append(("G-play-character-forms", "人物の形態の目録JSON", "assets/field/sit-character-forms.json", "assets/images/characters", render_forms()))
    import resume_saves  # 再開点の台帳 → セーブJSON（同じ scripts/ 内）

    scenes = {ident for ident, r in records.items() if _text(r, "背景画像")} | {SAMPLE_SCENE}
    return [(a, b, c, d, e.encode("utf-8")) for a, b, c, d, e in items] + resume_saves.outputs(scenes)


def preflight(items):
    """孤児（play/ 配下の全ファイル）を黙って残さない・生成物でないファイルを上書きしない（消さない）。

    play/ は name-name が読む md だけの置き場なので、台帳に対応しないファイルは拡張子を問わず孤児として止める
    （verify_asset_layout.py はファイル配置の規則外のファイルを見つけるだけで、孤児の削除漏れは見ない）。
    """
    expected = {ROOT / relative for _, _, relative, _, _ in items}
    orphans = sorted(p for p in OUT.rglob("*") if p.is_file() and p not in expected)
    if orphans:
        names = ", ".join(str(p.relative_to(ROOT)) for p in orphans)
        raise SystemExit(f"対応する台帳のないファイルが play/ に残っているため生成・検査を止めます: {names}")
    for _, _, relative, _, _ in items:
        path = ROOT / relative
        if not path.exists():
            continue
        if relative.endswith(".save.json") or relative.endswith("sit-field-emotions.json"):
            continue  # セーブ JSON は形式を足せない（鮮度の検査で手編集を検出する）。台帳が正本
        text = path.read_text(encoding="utf-8")
        marked = f'"{FORMS_GENERATED_KEY}"' in text if path.suffix == ".json" else MARKER in text
        if not marked:
            raise SystemExit(f"生成先が生成物ではないため上書きしません: {relative}")


def check():
    """鮮度（バイト一致）・孤児・上書き防止を検査する。build_ledger.py check は台帳登録のハッシュも見る。"""
    items = outputs()
    preflight(items)
    for _, _, relative, _, output in items:
        path = ROOT / relative
        if not path.is_file() or path.read_bytes() != output:
            raise SystemExit(f"FAIL: {relative} is stale")
    print(f"PASS: play/ の {len(items)} ファイルは台帳と一致")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("check",))
    parser.parse_args()
    check()
