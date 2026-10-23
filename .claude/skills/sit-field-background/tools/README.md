# tools/ 一覧（フィールド背景の制作ツール）

全て**画像を生成しない**。実行は `uv run ... python3 -I`（`python3` の直接実行は禁止）。どのツールも `-h` で使い方が出る（動作確認コマンド: 下）。体内で作ったため、現状は**全ツールが BDY（体内）前提のコードや定数を持つ**。新エリアで使えるかの区分は『引数と定数の差し替えで済む見込み（未検証）』と『体内専用』の2つで書く。**「そのまま動く」と実証済みのものはまだ無い**（新エリアの1枚目で確認し、この表を更新する）。

## 動作確認（ヘルプ）

```
cd <repo>/.claude/skills/sit-field-background/tools
for f in body_layout body_geometry_json body_mask_export body_register body_sheet body_floor_overlay check_body_image build_body_prompt; do
  uv run --with pillow --with numpy --with scipy --with opencv-python-headless python3 -I $f.py -h | head -3
done
uv run --with opencv-python-headless --with numpy --with pillow python3 -I body_step_scan.py -h | head -3
```

## 区分A: 引数と定数の差し替えで新エリアにも使える見込み（要1枚目で検証）

模型の構成（外周に机→土台の縁の帯→天面）と、クリーム系の床という前提は、寺町の見本由来で共通。ただしコード内の `BDY` の MAP ID・パス・床色定数・天面 rect（1920基準で x138〜1782, y138〜942）は体内の値。

| ツール | 入力 → 出力 | 使い方 | 新エリアで差し替える所 |
|---|---|---|---|
| `body_floor_overlay.py` | MAP ID・生成画像・clean 割付図 → 床IoU＋重ね画像（緑=一致・赤=期待のみ・青=実測のみ） | `... body_floor_overlay.py BDY-07 gen.png [--clean path] [--out ov.png]` | `--clean` で割付図を指す（MAP ID 固定のパス規則が既定）。IoU の定義は `check_body_image.floor_iou_ov` |
| `body_register.py` | 採用画像＋clean 割付図（＋幾何JSON）→ 位置合わせ変換・床の切り出し（`-floor-cut.png`）・位相検査・重ね画像・register.json | `... body_register.py BDY-04 adopted.webp --out DIR [--clean path] [--geometry json] [--npc "kiosk:0.30,0.50"]` | 迷路／脚の折れ点の位相検査は BDY 専用の分岐。連結成分・出口・スライス断面は汎用 |
| `body_mask_export.py` | `body_register.py` の出力 → 2値マスク3種・links・register・export-report | `... body_mask_export.py --reg REGDIR --masks assets/images/fields/masks --notes-dir docs/production/body-masks [--maps ..]` | 承認の事実（red-team 済み・逸脱承認）は `docs/production/body-masks/approvals.json` から読む（無ければ書かない）。接続検査の problems は exit 1、不正な `--maps`・入力欠落は exit 2。出力名 `BDY-xx-*`・既定の MAP 一覧・接続の反対辺検査（topology から読む部分）。3値のエリアは assist 出力の追加が要る |
| `body_step_scan.py` | clean 画像のディレクトリ → 斜めの帯の段差（Z形）の件数 | `... body_step_scan.py [clean dir]` | 床色定数 `FLOOR=(232,201,168)` と天面 rect 定数 |

## 区分B: 体内専用（新エリアでは作り直し。構造は参考にする）

| ツール | 内容 | 新エリアでの扱い |
|---|---|---|
| `body_layout.py`（1299行） | 体内17枚の割付図（`SPECS` に MAP ごとの幾何、`expected_runs`、迷路の seed 探索、接続の機械検査 C1〜C7）。`--clean` で清書用 | 構図（机→縁→天面→通路は縁まで）と接続検査の考え方を残し、`SPECS` を JSON 仕様に外出しして作り直す（次にやること1） |
| `body_geometry_json.py` | `body_layout.py` の割付図を幾何JSON（`sit-body-mock-geometry/1`。比率0..1と px）へ出力 | スキーマは共通化可。入力が `body_layout` の `SPECS` 直結 |
| `body_sheet.py` | 17枚の一覧画像（体の配置に沿った並べ＋接続線） | 配置（列・行）の表 `POS` を新エリア用に差し替えれば流用可 |
| `build_body_prompt.py`（2956行） | 送信文・来歴の機械生成。原文束の逐語検証、形の実測、装飾計画（8族・`DECO_PICK`）、赤紙の座標、`leak_check`、`--verify-send`・`--verify-bundle`・`--plan` | 部品を分離して再利用（次にやること2）。体内の族プール・原文行の選別（`ROOM_PICKS`）は体内専用 |
| `check_body_image.py` | 生成画像を期待幾何と実測で突き合わせる（寸法・床IoU・土台縁4層・通路・広間・赤紙・色の逸脱・装飾の色域） | 期待値（色の範囲・通路本数・広間の有無）を外出しして再利用（次にやること3）。限界は `../pitfalls.md` C |

## 次にやること（優先度順。今回は大規模リファクタをしない）

1. **【高】`body_layout.py` の `SPECS` を JSON 仕様に外出し**。新エリアは JSON を書くだけで割付図・接続検査・幾何JSONが出る。`body_geometry_json.py`・`body_sheet.py`・`build_body_prompt.py`・`check_body_image.py` が `body_layout` を import（または ast で読む）しているので、まず JSON を読む薄い層を足し、既存 SPECS を JSON へ書き出して出力が不変（割付図の sha256 一致）なことを確認してから置き換える。
2. **【高】`build_body_prompt.py` の部品分離**: ①構図（天面の内側・机→縁→天面。P1・P2）②色の制約（肯定形・範囲）③装飾プール（族・配置・色味・隣接検査）④赤紙（定数アクセントの数と座標）⑤SOURCE TEXT 検証（逐語抽出・`--verify-*`・`leak_check`）を別モジュールに。エリア固有は族プール・原文行の選別・形別の本文だけにする。
3. **【中】チェッカーの期待値の外出し**（`check_body_image.py`）: 色の範囲・通路本数・赤紙の数・広間の有無・天面 rect を JSON 引数に。床色を手動指定する `--floor-color`（`estimate_floor_color` が失敗した BDY-07 の対策）、机・縁が近い色のときの判定を『判定不能』にする。
4. **【中】共通定数の集約**: 天面 rect（138,138,1782,942）が `body_layout`・`body_geometry_json`・`body_mask_export`・`body_register`・`body_step_scan` に、寸法 1672/OK_SIZES が `check_body_image`・`build_body_prompt` ほかに重複している（grep で確認）。1ファイル（例 `body_consts.py`）へ。
5. **【低】`body_mask_export.py` の 3値対応（assist）**: 小学校より前のエリア用。`sit-field-mask` の3クラスを出力できるように。
6. **【低】ツールのテスト**: 体内17枚の clean を使い、リファクタ前後の出力 sha256 が一致することを確認するスモークテスト。
