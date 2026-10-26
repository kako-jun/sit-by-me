"""台帳（docs/ledger/<表名>.yaml）の読み書きと共通の値変換。マスターは日本語キーの YAML（UTF-8・LF・BOM なし）。

表ごとに 1 ファイル。中身は「行のリスト」で、各行はキー=日本語列名の辞書。
全スカラーを文字列として扱う（読み込み時に文字列へ正規化、書き出し時に必ず引用。no/yes/null/001/1e3 が型変換されない）。
空欄は空文字。複数行テキストは block scalar。ファイル先頭の `#` コメントは表の説明（書き出しで再生成される。
人が行の途中に足したコメントはプログラム経由の write で消える）。

行の順序は意味を持つ（plan の配列順＝描画順）。主キー昇順に並べ替えない。
YAML の読み込みに PyYAML が要る（リポ直下の pyproject.toml で依存宣言。`uv run python3` で自動的に入る）。
"""
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
# LEDGER_ROOT でリポジトリ root を差し替えられる（テストの fixture 用。Ruby 側 ledger_yaml.rb と同じ環境変数）
REPO = os.environ.get("LEDGER_ROOT") or os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
LEDGER = os.path.join(REPO, "docs", "ledger")
BUILDER_VERSION = "ledger-build/1"

FREE = "特徴(自由記述)"

# 表ごとの列（この順で書く。列を足すときは末尾の特徴の直前）
SCHEMA = {
    "エリア": ["エリアID", "区域コード", "名称", "目標枚数", "台帳段階", "机の天面の材質", "台座の素材", "木の種類", "外周の装飾方針", "備考", FREE],
    "MAP": ["MAP_ID", "エリアID", "名称", "字幕", "時期", "屋内外", "状態", "建物ID", "表現する部位", "一言特徴", "描画方式", "装飾プールID", "依存MAP", "依存の確度", "依存の根拠",
            "床材", "壁材", "窓", "扉の意匠", "工作の材質", "時期差分", "採用状態", "寸法根拠", "備考", "設計意図", "plan追加JSON", FREE],
    "建物": ["建物ID", "名称", "エリアID", "種別", "外形", "屋根", "外壁", "窓列", "扉", "材質", "関係", "状態", "備考", FREE],
    "建物部位": ["部位ID", "建物ID", "部位種別", "方角", "状態", "材質", "見た目", "決定参照", FREE],
    "建物窓列": ["窓列ID", "建物ID", "部位ID", "個数", "先頭比", "間隔比", "幅比", "窓台比", "高さ比", "窓種別", "理由", "決定参照", FREE],
    "建物関係": ["通番", "建物A", "建物B", "関係", "方角", "接続端ID", "決定参照", FREE],
    "建物時期差分": ["建物ID", "時期", "部位ID", "差分", "内容", "決定参照", FREE],
    "端": ["端ID", "MAP_ID", "適用時期", "種別", "壁", "壁側", "面", "中心", "沿い範囲", "相手端", "幅クラス", "状態", "通路", "建物部位ID", "備考", "決定参照", "属性JSON", FREE],
    "接続": ["端A", "端B", "種別", "期待", "ラベル", "方角A", "方角B", "外部", "無効時期", "図", "主路・状態", "出典注記", "決定参照", "属性JSON", FREE],
    "接続図設定": ["図ID", "項目", "値", "型", "決定参照"],
    "要素": ["MAP_ID", "適用時期", "要素ID", "種別", "名称", "建物部位ID", "見た目", "決定参照", "属性JSON", FREE],
    "窓": ["窓ID", "MAP_ID", "適用時期", "壁", "壁側", "中心", "幅", "種別", "窓台", "高さ", "状態", "沿い範囲", "建物窓列ID", "連番", "備考", "決定参照", "属性JSON", FREE],
    "時期差分": ["MAP_ID", "時期", "項目", "値", "決定参照"],
    "既定値": ["既定ID", "MAP_ID", "適用時期", "内容", "決定参照"],
    "エリア固定": ["エリアID", "項目", "値", "型", "決定参照"],
    "装飾プール": ["プールID", "項目", "値", "型", "決定参照"],
    "語彙": ["語彙ID", "グループ", "値", "英語断片", "説明"],
    "決定": ["決定ID", "日付", "対象種別", "対象ID", "対象名", "決定の要点", "逐語", "出典", "出典URL", "状態", "置換先", "プロンプト出力", "必須語", "禁止語", "対象MAP", "備考", FREE],
    "採用要素": ["採用要素ID", "素材ID", "元MAP", "要素", "内容", "継承先MAP", "継承方法", "状態", "確認語", "決定参照", FREE],
    "素材": ["素材ID", "所有者ID", "種別", "パス", "状態", "日付", "来歴", "sha256", FREE],
    "生成物": ["生成物ID", "種別", "パス", "元の表", "入力ハッシュ", "生成日時", "再生成コマンド", "備考"],
    "必須キー": ["対象テーブル", "キー", "必須度", "条件", "語彙グループ", "説明"],
    "未決": ["未決ID", "対象テーブル", "対象ID", "キー", "内容", "状態", "解決決定ID"],
    "キー別名": ["正規名", "別名", "対象テーブル", "説明"],
    # Issue点検: GitHub の Issue 本文・コメントのうち『kako-jun の決定』と読める候補と、決定表との突合結果（audit_issue_decisions.rb が更新）
    # 分類: 決定表に反映済み（決定IDが要る）／未反映(要取込み)／決定でない／対象外
    "Issue点検": ["Issue番号", "コメントURL", "候補の要約", "分類", "決定ID", "備考"],
    # ファイル配置: パターンは repo root からの相対パス（/ 区切り）に fullmatch する正規表現。{MAP_ID} は MAP ID の正規表現に展開する
    # 到達: リンク（INDEX からのリンクの連鎖で到達できなければ孤立としてエラー）／許可（許可リスト。理由が要る）
    "ファイル配置": ["配置ID", "パターン", "種別", "用途", "所有表", "生成元", "到達", "入口", "許可リスト理由", "検査", "備考"],
    # 描画定数: oblique_mock.py / oblique_topology.py が読む寸法・視点・幅クラス・窓種別・台座の飾りの位置（値は文字列。配列は JSON）
    "描画定数": ["定数ID", "グループ", "値", "単位", "説明", "コード内の名前"],
    # プロンプト文面: プロンプト・接続表・窓一覧・接続図に出る文面（{名前} が変数の差し込み口。oblique_text.text が差し込む）
    "プロンプト文面": ["文面ID", "区分", "文面", "変数", "使用箇所", "備考"],
}

# 第2段階以降の台帳。既存の28表と同じく、行は引用済み文字列の列だけで
# 表す。複合値を持つ派生JSONは「経路・型・値」の行へ分解して記録する。
SCHEMA.update({
    "制作規約": ["規約ID", "対象種別", "対象ID", "区分", "内容", "確度", "根拠"],
    "図配置": ["配置ID", "エリアID", "MAP_ID", "順番", "X", "Y", "図ラベル", "備考"],
    "エリア構造": ["経路", "型", "値", "根拠"],
    "MAP仕様": ["仕様ID", "MAP_ID", "原文ID表記", "節", "時期", "一言特徴", "経路・通行", "暫定固定", "原文列名", "根拠", "決定参照", FREE],
    "文書ビュー": ["ビューID", "パス", "元の表", "ヘッダーJSON", "行参照", "根拠"],
    "MAP契約": ["契約ID", "MAP_ID", "資料区分", "参照ID", "旧状態", "画像識別子", "mask・出力", "具体的TBD", "通行・接続", "素材状態", "根拠", FREE],
    "特殊遷移": ["遷移ID", "種別", "階", "起点MAP", "起点端", "到着MAP", "行先表示", "条件", "状態", "根拠", FREE],
    "体内幾何": ["幾何ID", "MAP_ID", "変種", "経路", "型", "値", "確度", "根拠", FREE],
    "海外進行": ["経路", "型", "値", "根拠"],
    "敵": ["敵ID", "名称", "分類", "登場設定", "属性", "弱点・耐性", "役割", "遭遇状態", "画像状態", "根拠", FREE],
    "召喚獣": ["召喚獣ID", "名称", "登場・取得", "属性", "敵として戦うか", "画像状態", "根拠", FREE],
    "敵サイズ": ["サイズ行ID", "敵ID", "形態", "グリッド種別", "根拠"],
    "ダンジョン": ["ダンジョンID", "名称", "含む地区・MAP", "時期", "分ける理由", "目標種数", "備考"],
    "敵配置": ["配置ID", "敵ID", "召喚獣ID", "ダンジョンID", "対象MAP", "時期", "名前・サイズ", "理由", "ラーニング", "役割", "個性パターン案", "画像状態", "評価", "報酬の個性", "再戦可否", "採用状態", "出典", FREE],
    "兼六園再登場": ["再登場ID", "グループID", "MAP_ID", "元ダンジョンID", "敵ID", "種数換算", "理由", "状態"],
    "ボスギミック": ["ギミックID", "内容", "出典", "実現可否", "使う予定", "採用状態", FREE],
    "戦闘パターン案": ["パターンID", "対象ID", "案", "根拠", "ギミックID", "実現可否", "採用状態"],
    "敵戦利品": ["敵ID", "ドロップ", "ぬすむ通常", "ぬすむレア", "根拠"],
    "BGMスロット": ["スロットID", "抽象名", "場面", "気分", "Largo", "系統", "長さ", "兼用先", "状態", "根拠"],
    "BGM回想編曲": ["編曲ID", "元スロットID", "回想場面", "編曲案", "気分", "Largo", "系統", "状態"],
    "BGM旧スロット対応": ["対応ID", "旧スロットID", "旧抽象名", "現行スロットID", "扱い", "理由"],
    "BGM録音": ["録音行ID", "録音ID", "録音名", "演奏者", "録音年", "楽章", "ファイルパス", "ランク", "ライセンス表記(原文)", "出典URL", "クレジット文言", "ffprobeで実測した長さ(秒)", "形式", "備考"],
    "BGMフレーズ": ["フレーズ行ID", "主題ID", "楽章", "主題名", "録音ID", "元録音ID", "開始秒", "終了秒", "気分(悲/楽/緊)", "割当スロット候補", "出力ファイル", "要耳確認"],
    "人物": ["人物ID", "呼称", "旧接頭辞", "牌", "人物の芯", "見た目の核", "役割", "根拠", FREE],
    "人物形態": ["形態ID", "人物ID", "年齢", "衣装", "車椅子", "マスターパス", "状態", "根拠"],
    "素材移行": ["旧パス", "新パス", "操作", "理由", "sha256", "剪定パス"],
    "素材移行設定": ["設定ID", "値", "説明"],
    "刀候補": ["刀候補ID", "刀名", "種別", "作者", "時代", "指定", "所蔵", "特徴", "逸話", "個性の素", "確度", "注", "出典", "状態"],
    "刀配分案": ["配分ID", "人物ID", "枠", "刀候補ID", "理由", "状態"],
    "能力候補": ["能力ID", "候補", "型・参照元", "重荷", "素質", "時代", "定番", "ジョブ重なり", "cmd", "MG", "状態", "根拠"],
    "刀能力配分案": ["配分ID", "人物ID", "刀候補ID", "能力候補ID", "型", "根拠", "状態"],
    "ジョブ候補": ["候補ID", "役割", "人物ID", "履歴", "候補プール", "根拠", "状態"],
    "魔法": ["魔法ID", "属性", "魔法名", "効果", "根拠", "状態"],
    "Issue出典": ["出典ID", "Issue番号", "種別", "URL", "投稿日", "本文SHA256", "安全化SHA256", "本文", "点検状態", "備考"],
    "Issue命題": ["命題ID", "出典ID", "位置", "要点", "原文抜粋", "帰属", "分類", "決定ID", "未決ID", "参照先", "備考"],
})


# 表の説明（YAML ファイル先頭のコメントになる）
TABLE_DOC = {
    "エリア": "エリア（区域）の台帳。1行=1エリア。",
    "MAP": "MAP（1枚の背景）の台帳。1行=1MAP。設計意図=plan の design。plan追加JSON=plan の最上位に足す追加キー(例 indoor)。",
    "建物": "建物の台帳。屋内と外観は同じ建物行から導出する。",
    "建物部位": "建物の部位（壁・屋根・扉など）。",
    "建物窓列": "建物の壁ごとの窓列。",
    "建物関係": "建物どうしの関係（渡り廊下で接続など）。",
    "建物時期差分": "建物の時期ごとの差分。",
    "端": "MAP の端（戸口・開口・縁）。",
    "接続": "端と端の接続。図は ; 区切りで複数の接続図に属せる。属性JSON は {図ID: {辺の出力キー: 値(null=その図では出さない)}} で図ごとの上書きを持つ。",
    "接続図設定": "接続図の描画設定（図ID×項目）。",
    "要素": "MAP 内の要素（家具・物・樹木など）。",
    "窓": "MAP の壁の窓。",
    "時期差分": "MAP の時期ごとの差分。",
    "既定値": "仮置きの既定値（要確認）。",
    "エリア固定": "エリア単位で固定する指定（机の天面・木の種類・台座など）。",
    "装飾プール": "装飾プールの設定。",
    "語彙": "許す・禁じる語彙と英語プロンプト断片。",
    "決定": "kako-jun の決定（逐語・出典つき）。status に関係なくプロンプトへ入る。",
    "採用要素": "採用画像から次の絵へ継承する要素。",
    "素材": "素材（画像・マスクなど。没も行で保持）。",
    "生成物": "派生物（JSON）の登録と鮮度検査用ハッシュ。",
    "必須キー": "対象テーブルごとの必須キー定義。",
    "未決": "未決（要確認）の一覧。",
    "キー別名": "列名・キー名の別名と正規名。",
    "Issue点検": "Issue の決定候補と決定表の突合結果（audit_issue_decisions.rb が更新。分類=決定表に反映済み／未反映(要取込み)／決定でない／対象外）。",
    "描画定数": "斜めツール（oblique_mock.py・oblique_topology.py）の寸法・視点・幅クラス・窓種別・台座の飾りの位置。コードはここを読む。",
    "プロンプト文面": "imagegen 用プロンプト・接続表・窓一覧・接続図に出る文面（{名前}=変数の差し込み口）。コードは oblique_text.text で読み、文面を直接持たない。",
    "ファイル配置": "リポ内のファイルの置き場所規則（パターン・種別・用途・所有表/生成元・許可リスト理由）。asset-layout.md と verify_asset_layout.py の規則を合流した正本。",
}

TABLE_DOC.update({
    "図配置": "MAPの接続模式図上の順序と座標。地理的な実距離ではない。",
    "エリア構造": "area JSON の体内部位分類など、模式図座標では表せない構造値。経路・型・値で保持する。",
    "MAP仕様": "MAPごとの個別仕様。原表の各行を名前付き列として保持し、MAP行へ重複転記しない。",
    "MAP契約": "旧MAP仕様・契約表の移行先。参考、旧状態、既存素材、通行条件、未決の出典を保持する。",
    "特殊遷移": "歩行接続ではない階選択やワープの遷移。未決の端点を推測しない。",
    "体内幾何": "体内の幾何入力。MAP・変種・経路ごとの型付き値を保ち、モック生成コードはこれを読む。",
    "海外進行": "海外三塔の設計状態機械。経路ごとの型付き値からJSONを導出する。",
    "Issue出典": "全Issue本文・コメントの安全化済み出典。原文SHA256と安全化SHA256を区別する。",
    "Issue命題": "Issue中の命題を分類し、決定・未決・既存台帳へ関連づける。",
    "素材移行": "旧素材の移動・削除・剪定先を監査可能な行で保持し、manifest JSONを導出する。",
})
for _table in SCHEMA:
    TABLE_DOC.setdefault(_table, f"{_table}の台帳。元資料の提案と確定状態を区別して保持する。")


def path(table):
    return os.path.join(LEDGER, f"{table}.yaml")


def _q(v):
    """全スカラーを二重引用符つきで書く（JSON の文字列表記は YAML の二重引用符スカラーと互換）。"""
    return json.dumps(v, ensure_ascii=False)


def _block_ok(v):
    """block scalar（|-）で無損失に書ける文字列か。"""
    if "\n" not in v or v != v.strip() or "\n\n\n" in v:
        return False
    for ch in v:
        if ch == "\n":
            continue
        if ord(ch) < 32 or ord(ch) == 127 or ch in "\u0085\u2028\u2029\ufeff":
            return False
    # 空白だけの行・行末の空白は block scalar で壊れやすいので引用に回す
    return all(ln == ln.rstrip() and (ln.strip() or not ln) for ln in v.split("\n"))


def dumps(table, rows):
    cols = SCHEMA[table]
    out = [f"# 表: {table} — {TABLE_DOC.get(table, '')}", f"# 列: {' / '.join(cols)}",
           "# 全スカラーは文字列（引用符つき）。空欄は \"\"。複数行は |- ブロック。"]
    if not rows:
        out.append("[]")
    for r in rows:
        extra = set(r) - set(cols)
        if extra:
            raise KeyError(f"{table}: 未定義の列 {sorted(extra)}")
        for i, c in enumerate(cols):
            v = "" if r.get(c) is None else str(r.get(c))
            lead = "- " if i == 0 else "  "
            if _block_ok(v):
                out.append(f"{lead}{_q(c)}: |-")
                out.extend(("      " + ln) if ln else "" for ln in v.split("\n"))
            else:
                out.append(f"{lead}{_q(c)}: {_q(v)}")
    return "\n".join(out) + "\n"


def _str(v):
    if v is None:
        return ""
    if isinstance(v, bool):
        return "true" if v else "false"
    return str(v)


QUOTED_STYLES = ('"', "'", "|", ">")


def _check_syntax(table, text):
    """YAML の構文木で検査する: 全スカラー（キーも値も）は引用符つきか block scalar（未引用だと no/yes/null/2026-10-21 などが
    型変換される）、同じ行（辞書）に同じキーを2回書かない（yaml.safe_load は後勝ちで黙って上書きする）。"""
    import yaml
    node = yaml.compose(text, Loader=getattr(yaml, "CSafeLoader", yaml.SafeLoader))
    if node is None:
        return None
    if not isinstance(node, yaml.SequenceNode):
        raise ValueError(f"{table}: 最上位は行のリストでなければならない")
    for i, item in enumerate(node.value):
        if not isinstance(item, yaml.MappingNode):
            raise ValueError(f"{table}: {i + 1}行目が辞書でない")
        seen = {}
        for k, v in item.value:
            for n in (k, v):
                if not isinstance(n, yaml.ScalarNode):
                    raise ValueError(f"{table}: {n.start_mark.line + 1}行目: スカラー以外（入れ子）は使えない")
                if n.style not in QUOTED_STYLES:
                    raise ValueError(f"{table}: {n.start_mark.line + 1}行目: 引用符のないスカラー『{n.value}』（全スカラーは \"…\" か |- ブロックで書く）")
            if k.value in seen:
                raise ValueError(f"{table}: {k.start_mark.line + 1}行目: キー『{k.value}』が同じ行（{seen[k.value]}行目に既出）で重複している")
            seen[k.value] = k.start_mark.line + 1
    return node


def parse(table, text):
    node = _check_syntax(table, text)
    if node is None:
        return []
    cols = SCHEMA.get(table, [])
    rows = []
    for i, item in enumerate(node.value):
        # The validated syntax tree already contains string scalar values.
        # Construct directly instead of parsing multi-MB sources a second time.
        row = {k.value: v.value for k, v in item.value}
        unknown = [k for k in row if cols and k not in cols]
        if unknown:
            raise ValueError(f"{table}: {i + 1}行目に表定義（SCHEMA）に無い列 {unknown}（綴り間違い？ 正しい列: {' / '.join(cols)}）")
        for c in cols:
            row.setdefault(c, "")
        rows.append(row)
    return rows


def read(table):
    p = path(table)
    if not os.path.exists(p):
        return []
    with open(p, encoding="utf-8", newline="") as f:
        return parse(table, f.read())


def write(table, rows):
    os.makedirs(LEDGER, exist_ok=True)
    with open(path(table), "w", encoding="utf-8", newline="") as f:
        f.write(dumps(table, rows))


def jdump(o):
    return json.dumps(o, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha(s):
    return hashlib.sha256(s.encode("utf-8") if isinstance(s, str) else s).hexdigest()


def sha_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


# ---- 値の語彙（JSON の英語値 ⇔ 台帳の日本語値）。語彙表の「グループ」と対応する
SIDE = {"west": "西", "east": "東", "north": "北", "south": "南"}
STATUS = {"fixed": "確定", "default": "既定(要確認)"}
WIDTH = {"2people": "2人分", "1.5people": "1.5人分", "1person": "1人分"}
WKIND = {"waist": "腰高", "floor": "掃き出し"}
EKIND = {"floors": "床", "walls": "壁", "boxes": "家具", "paths": "経路", "tree_zones": "樹木帯", "annotations": "注記", "closed_edges": "閉鎖辺"}
EDGE_KIND = {"doors": "戸口", "openings": "開口", "markers": "縁"}


def inv(d):
    return {v: k for k, v in d.items()}


def jp(d, v):
    return d.get(v, v) if v is not None else ""


def en(d, v):
    return inv(d).get(v, v) if v not in (None, "") else None


def split_list(s):
    return [x for x in (s or "").split(";") if x]


if __name__ == "__main__":
    import sys
    if sys.argv[1:] == ["schema"]:  # Ruby 側の検査（verify_ledger.rb）が表定義を読む口
        print(json.dumps(SCHEMA, ensure_ascii=False))
    else:
        sys.exit("usage: ledger_io.py schema")
