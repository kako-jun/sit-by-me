# tools/ 一覧（フィールド背景の制作ツール）

> **運用（絶対。台帳 = `docs/ledger/*.yaml` が唯一のマスター）**: ①決定は先に `決定.yaml` へ（Issue は決定IDを参照するだけ・Issue にだけ書かない）。②必須キー（`必須キー.yaml`）が欠けたMAPは `oblique_build.py` が起動しない。表に収まらない決まりは各表の `特徴(自由記述)` 欄へそのまま書く。③画像生成は台帳整理の完了＋kako-jun の再開指示後（現在は停止中）。④生成画像は Claude は見ない（kako-jun が見る）。⑤プロンプトの文面・寸法は台帳の `プロンプト文面`・`描画定数` を直す（コードに直書きしない）。詳細は [SKILL.md](../SKILL.md)「台帳の運用」。

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

## 区分C: 斜め視点用（寺町 TRM-02〜05。#144。体内のツールとは独立）

体内（真上）と違い、採用画像は少し手前の斜めから見下ろす。絵から平面図を逆算する3×3ホモグラフィで位置合わせし、床マスク・出口・NPC を出す。体内のツール・成果物は変更しない。依存は numpy/scipy/opencv-python-headless（`--masks-dir` の WebP 出力だけ pillow）。入力JSONの置き場と作り方は `docs/production/oblique-masks/README.md`。

| ツール | 入力 → 出力 | 使い方 |
|---|---|---|
| `oblique_common.py` | 共通部品（入力JSONの読み込み・ホモグラフィ・表出力）。単体では実行しない | - |
| `oblique_register.py` | 入力JSON＋採用画像 → ホモグラフィ（部屋ごと）・平面図への逆射影PNG・縦横比の検証（`circular`＝循環／`independent`＝独立／`quad-only`＝4点のみ）・register.json | `uv run --with numpy --with scipy --with opencv-python-headless python3 -I oblique_register.py INPUT.json --image IMG --out DIR` |
| `oblique_mask.py` | 入力JSON＋採用画像＋register → 3値の edit PNG（white/black/orange `#FF9D00`）・白のみの mask・確認用 overlay・result.json（床・blocked・出口・NPC の判定表） | `uv run --with numpy --with scipy --with opencv-python-headless --with pillow python3 -I oblique_mask.py INPUT.json --image IMG --reg DIR --out DIR [--masks-dir assets/images/fields/masks]` |

動作確認（ヘルプ）: `uv run --with numpy --with scipy --with opencv-python-headless --with pillow python3 -I oblique_register.py -h`（`oblique_mask.py` も同様）。同じ入力から同じ画素が出る（TRM-02 で2回実行し cmp 一致を確認）。

## 区分D: 斜めモック一式（寺町 TRM-02〜05 ほか。#144。画像生成なし・決定論）

平面スペック JSON（`docs/production/oblique-mocks/<MAP>-plan.json`）から、斜めモック・歩行マスク・手前オクルージョン・白黒ワイヤー接続図・imagegen 編集用プロンプトを機械生成する。**絵の認識・LLM は使わない**。標準手順は `../SKILL.md`「斜め視点のエリア」。実行は `uv run --with numpy --with opencv-python-headless --with pillow python3 -I <tool>.py`。

| ツール | 内容 | 使い方 |
|---|---|---|
| `oblique_build.py` | Make 風の一括ビルド。段階 validate→mock→wire→mask→occlusion→prompt（→承認ゲート→adopt→verify）。段ごとの入力 hash を MAP ごとの `manifest.json` に記録し、変わらない段はスキップ | `oblique_build.py PLAN.json [--variant kids] [--from STAGE] [--force]`／`--all connections.json`（全MAP＋接続図）／`--status connections.json`／`PLAN.json --adopt IMG --take N` |
| `oblique_mock.py` | 射影・描画・マスク・オクルージョン。クリーン版（ラベルなし・imagegen 編集元）・ラベル付き版・歩行マスク（床=白・blocked=黒・戸口=出口範囲）・オクルージョン（隠す領域・深度・黒シアン編集地図・重ね確認画像） | 単体でも `oblique_mock.py PLAN.json --out DIR` |
| `oblique_build.py` の decor | 平面スペックの `decor_pool`（`decor-pools.json`）と box の `kind`/`look` を検証し、edit-prompt v4（COORDINATES＝幾何の画素座標・TREE PLACEMENT・LAYERS・SURFACES・見た目つき OBJECTS・ALLOWED/FORBIDDEN。座標は plan とモックの射影から機械的に出す）を出す。プールは MAP をまたいで再利用（本堂・住居・外観は pool の kinds/層を足して使う。他 MAP の雛形は `teramachi-winter` を複製する。エリア固定項目 `areas.<area>`（机の天面の材質・木の種類=寺町は松＋枯木・台座の素材）は pool が `area` で継承し、pool/plan 側の上書きはエラー。`--all` は同じエリアの全MAPの継承と上書きの有無も検査する。新エリアは area_fixed を kako-jun と決めてから `areas` に足す） | `oblique_build.py PLAN.json`（prompt 段） |
| `oblique_topology.py` | 接続図 `connection-diagram.png`（白背景・黒線のワイヤーで各MAPと戸口の線・door ID・幅・方角・寺町外の端点）・`overview.png`（カラー一覧）・`connections.md`（接続表。位置整合を検査）・個別ワイヤー図 | `oblique_build.py --all` が呼ぶ |
| `oblique_e2_run.sh` | **E2 一括**（依存グラフで親が未確定なら起動拒否。確定済みの親の採用画像を参考画像＋役割節で自動添付。`DRY_RUN=1` で生成せずに確認。`--adopt --canonical` で確定を記録）（テイク数は4固定・既定 N=4。自動の順位づけ・絞り込みなし。全テイクのパスを出力し、採用は kako-jun の目視。測定は参考=基準内/基準超）: クリーンモックを編集元に imagegen を N テイク並列生成（codex、`$imagegen` 明示・品質high・参照=clean＋素材見本のみ）→ 測定 → ログ縮約。プロンプト既定は `<MAP>-edit-prompt.txt` の台帳ゲート行より前＋参照・出力の節（`<MAP>/e2/prompt-base.txt` に自動生成） | `[STYLE_REF=git:REV:PATH] [REF_IMAGE=...] oblique_e2_run.sh MAP N [ROUND] [PROMPT_FILE]`（リポ直下。STYLE_REF を付けると参照3枚目に様式参照を添付=B案。REF_IMAGE は測定の基準画像。ROUND は `e2/round2a` のように分ける） |
| `oblique_e2_schedule.py` | 依存グラフ（`dependency-graph.json`）と確定状態（manifest の adoption.canonical）から『今起動できるMAP』を出す。`list`・`check MAP`（親が未確定なら理由つきでエラー）・`refs MAP`（確定済みの親の正本画像）・`graph`（循環・存在しないID・自己参照・plan との不一致を検査）・`launch [--dry-run]`（起動可能なMAPを並列にバックグラウンド起動） | `uv run python3 -I oblique_e2_schedule.py list` |
| `oblique_e2_measure.py` | 生成物の幾何保持を**画像を見ずに**測る（決定論）: 輪郭 recall@6px・Chamfer・ずらし基準との差、領域（戸口/窓/家具）ごとの最良ずれ、戸口のピンク残り、窓ガラス内の白/緑、床の輝度標準偏差、テイク間 Chamfer・ずれの標準偏差、本物確認。`metrics.json`/`metrics.md`/`overlay-takeN.png`（モック輪郭=赤を重ねる）を出す。GATES が合否基準。モック自身で自己較正（測れない領域は除外） | `uv run --with numpy --with opencv-python-headless --with pillow python3 -I oblique_e2_measure.py MAP [--round e2] [--takes 4] [--ref git:REV:PATH]`。`--ref`（元の採用画像）を付けると装飾量（領域のエッジ密度・色エントロピーの対 ref 比）・層の平均色と分離・建物の外の木/草/平坦白・元画像の構図コピー検出も出す（DECOR_GATES）。机の天面はエリア固定値（`areas.<area>.desk`）に対する ΔE≤15・板目の向き（横方向エネルギー比≥0.8）・テイク間の最大ペア差 ΔE≤8（超えたら幾何+装飾の合格を取り消す）。針葉の判定は暗い緑・青緑・オリーブ（G≥R+3・G≥B+3・輝度<125）で松も拾い、幹・枝は暗い茶（枯木の枝も同じ）。木の塊は針葉＋枝の連結成分（面積≥200px） |

開口: 左右に行き来する開口（`openings[]`、または戸口に `passage: true`）は壁面を抜き、梁・鴨居・垂れ壁を描かない（クリーン版にも）。渡り廊下は壁 `kind: "roof-passage"`（床＋四隅の柱＋屋根の板だけの開放した通路）。edit-prompt に『開口の上に梁・鴨居・垂れ壁・壁を描かない。奥まで見通せる開放した通路』を出し、オクルージョンは開口部分で壁のシルエットが出ない。

窓: 平面スペックの `windows[]`（壁・中心・幅・窓台高さ・高さ・種別 floor/waist・status・along_ref）と各壁の `window_count` を検証（壁内に収まる・戸口/開口/他の窓/家具と重ならない・壁高以内・個数一致）。モック（クリーン含む）・ワイヤーに描き、edit-prompt に出し、`windows.md`（MAP×壁×個数×位置(中心・比)×種別×status）を生成する。窓は歩行・オクルージョンに影響しない。

視点・寸法・文面の正本は台帳（コードは読むだけ）: `oblique_text.py` が台帳の **`描画定数.yaml`**（視点＝画像1672×941・土台1600×1270・台形の4隅・見下ろし約42度・1キャラ=66単位・戸口の高さ132・幅クラス（2人分132/1.5人分100/1人分66）・窓種別の名前・台座の飾り（マステ4・糊4）の位置・オクルージョンのキャラ寸法 67×100px〔既定・要確認〕・overview の並び）と **`プロンプト文面.yaml`**（imagegen 用プロンプト〔PR.*〕・モックのラベル〔MK.*〕・接続図/接続表/窓一覧の文面〔TP.*〕。`{名前}` が変数の差し込み口）を読む。数値や言い回しを変えるときは台帳を直す（コードを直さない）。`ruby scripts/verify_ledger.rb` が、コードが参照するIDが全て在る・どの行もコードから参照されている・変数列が本文と一致する、を検査する。スペックの書き方・戸口の相手・開口の既定は `docs/production/oblique-mocks/*-plan.json` を雛形にする。

**コード内に残したもの（台帳に置かない理由）**
- 描画の見た目の調整値: 机・床・壁・扉・窓・開口の色、机の木目の乱数（seed 7・帯の太さ48〜78）、ラベルの文字サイズ・枠線、台座の前面の色、柱の太さ16・屋根板の厚み12、壁を100単位に分ける刻み、戸口の歩く側の伸ばし（壁の高さ×1.4・最小60）。画像の質感だけを決めるアルゴリズム定数で、プロンプト・決定・接続に出ない。
- 検査アルゴリズムの定数: 格子の刻み2、戸口の前の障害物検査の80単位、経路の入口の100単位、位置整合の許容0.05・0.03、`min_width` の既定。判定の計算手順であり、変えるときはコードのレビューが要る。
- 検査の診断メッセージ（`validate_plan` の `E.append(...)`・`oblique_topology.build` の problems）: 失敗時に開発者へ出す文で、プロンプト・接続表・窓一覧・接続図に入らない（manifest に失敗として記録されるだけ）。
- 表の見出し行・列名（`connections.md`／`windows.md` の `| 戸口A | Aの位置 | …`）と画像の座標・フォントサイズ: 出力の書式であって文面ではない。
- `FONT`（`/usr/share/fonts/noto-cjk/...`）: 実行環境のパス。環境ごとに違うので台帳に置かない（Linux 前提。macOS では差し替えが要る）。
- （削除済み）`oblique_topology.py` の `if False` で無効化されていた旧ラベル「寺町外の端点」は死にコードだったので消した。

## 台帳（docs/ledger/<表名>.yaml）

マスターは日本語キーの YAML（表ごと1ファイル、行のリスト、全スカラーは引用つき文字列）。派生物（plan・decor-pools・connections・dependency-graph の JSON）は `ledger_build.py` が台帳から作る。

| ファイル | 役割 |
|---|---|
| `oblique_text.py` | 斜めツールが台帳の `描画定数`・`プロンプト文面` を読む口（`text(ID, 変数…)`・`const(ID)`）。ID や変数が合わなければ止まる（既定値で黙って続けない） |
| `ledger_io.py` | 表定義 `SCHEMA` と読み書き（`read`/`write`。行は日本語キーの dict）。PyYAML はリポ直下 `pyproject.toml` で依存宣言 |
| `ledger_build.py` | 派生 JSON（plan・decor-pools・dependency-graph・接続図2種=幼稚園一式 `connections.json`／寺町全体 `connections-teramachi.json`）の生成（`build`）と鮮度検査（`check`）、必須キー雛形（`template`） |
| `ledger_query.py` | MAP 1枚分のプロンプト台帳節 |
| `ledger_index.py` | `docs/INDEX.md` の生成ビュー（台帳の表一覧・派生物・ファイル配置規則）の生成（`build`）と鮮度検査（`check`）。`verify_ledger.rb` が `check` を実行する。root は `LEDGER_ROOT` で差し替え可（`ledger_io.py` も同じ） |
| `oblique_prompt_probe.py` | 全MAPの imagegen 編集プロンプトをファイルに書かず JSON で出す（ゲート停止MAPは `gated` に欠落一覧）。`scripts/verify_prompt_reflects_ledger.rb` が使う。`uv run --with numpy --with opencv-python-headless --with pillow python3 oblique_prompt_probe.py`。画像生成 API は呼ばない |
| `ledger_write_rows.py` | 標準入力の JSON（行の配列）を台帳の1表として書く（YAML の書き出しは Python の `ledger_io` だけ）。`audit_issue_decisions.rb --write` が使う |
| `ledger_csv_to_yaml_once.py` | 一度きりの CSV→YAML 変換（変換済み。`--verify-only` は コミット 40bf95d の CSV との無損失突合） |

接続表の `図` は `;` 区切りで複数の接続図に属せる。`属性JSON` は `{図ID: {辺の出力キー: 値}}`（null=その図では出さない）で図ごとの上書きを持つ。MAP の `設計意図` は plan の `design`、`plan追加JSON` は plan 最上位の追加キー（例 `indoor`）、要素の種別 `閉鎖辺` は plan の `closed_edges`（屋外MAPの閉鎖した辺と理由）。

ファイルの置き場所は台帳 `ファイル配置.yaml` が正本。`ruby scripts/verify_index_reachable.rb` が、全ファイルが配置規則にちょうど1つ一致し、到達=リンクのファイルが `docs/INDEX.md` からのリンクで辿れる（孤立・壊れたリンクはエラー）ことを検査する。新しいツール・スクリプト・ドキュメントを足したら INDEX から辿れるようにリンクを張る。

`ruby scripts/verify_prompt_reflects_ledger.rb` が、台帳の決定（ID・要点・必須語・禁止語）・採用要素（参考画像とプロンプトの両方）・自由記述・建物窓列の窓が、導出したプロンプトに漏れなく現れるかを検査する（`--maps ID,ID`・`--from-json`。回帰アンカー=畳・化石の石・-fire の勝手口が北壁・火事版の上半分・渡り廊下の窓列はスクリプト内に期待を固定）。

### Issue の決定点検（`ruby scripts/audit_issue_decisions.rb`）

Issue 本文・コメントから『kako-jun の決定』と読める候補を全件走査し、決定表と突合して `docs/ledger/Issue点検.yaml`（列: Issue番号・コメントURL・候補の要約・分類・決定ID・備考）に載せる。`gh` が要る（オフラインは `--fetch F` で保存した JSON を `--from-json F` で読む）。`--write` で表を更新、無指定は表との過不足検査（未点検の候補・自動判定とずれた分類があれば exit 1）、`--list 分類` で一覧。`verify_ledger.rb` は表の外部キー（決定ID）・分類の語彙（語彙表の『Issue点検分類』）・URL と Issue番号の整合を検査する。

- 候補のヒューリスティック（誤検出より漏れ検出を優先）: 投稿者では絞らない（Claude が kako-jun のアカウントで投稿するため全コメントが本人投稿）。見出し（# 行に 決定|確定|承認|合意|指示|発言|指摘|判定|回答|方針|訂正）／本文に『逐語』／kako-jun・本人・ユーザー・発言・原文・指示・回答・承認 を含む行の「…」引用／kako-jun の直後に 指示|決定|承認|OK|まかせ|よい|判断、のいずれか。
- 分類（上から順）: 対象外=プルリクエストの会話／決定表に反映済み=コメントURLが 決定.出典URL にある、または逐語に抽出した引用（10字以上）が全て 決定.逐語・決定の要点 に含まれる（決定ID を付ける）／決定でない=先頭の見出しが作業記録（結果・これからやること・実施記録・進捗 等）で引用が1つも無い／それ以外は未反映(要取込み)。未反映の中で決定表へ取り込む根拠にできるのは備考が『逐語あり』のものだけ（『逐語の引用なし』は要確認）。
- 自動判定を人が覆すときは、表の行の備考に `【手動】` を付けて分類を直す（`--write` で保たれ、検査でもずれと数えない）。

検証は Ruby（`scripts/verify_ledger.rb` ほか。Homebrew の Ruby 4.x: `PATH=/opt/homebrew/opt/ruby/bin:$PATH`）。

## 次にやること（優先度順。今回は大規模リファクタをしない）

1. **【高】`body_layout.py` の `SPECS` を JSON 仕様に外出し**。新エリアは JSON を書くだけで割付図・接続検査・幾何JSONが出る。`body_geometry_json.py`・`body_sheet.py`・`build_body_prompt.py`・`check_body_image.py` が `body_layout` を import（または ast で読む）しているので、まず JSON を読む薄い層を足し、既存 SPECS を JSON へ書き出して出力が不変（割付図の sha256 一致）なことを確認してから置き換える。
2. **【高】`build_body_prompt.py` の部品分離**: ①構図（天面の内側・机→縁→天面。P1・P2）②色の制約（肯定形・範囲）③装飾プール（族・配置・色味・隣接検査）④赤紙（定数アクセントの数と座標）⑤SOURCE TEXT 検証（逐語抽出・`--verify-*`・`leak_check`）を別モジュールに。エリア固有は族プール・原文行の選別・形別の本文だけにする。
3. **【中】チェッカーの期待値の外出し**（`check_body_image.py`）: 色の範囲・通路本数・赤紙の数・広間の有無・天面 rect を JSON 引数に。床色を手動指定する `--floor-color`（`estimate_floor_color` が失敗した BDY-07 の対策）、机・縁が近い色のときの判定を『判定不能』にする。
4. **【中】共通定数の集約**: 天面 rect（138,138,1782,942）が `body_layout`・`body_geometry_json`・`body_mask_export`・`body_register`・`body_step_scan` に、寸法 1672/OK_SIZES が `check_body_image`・`build_body_prompt` ほかに重複している（grep で確認）。1ファイル（例 `body_consts.py`）へ。
5. **【低】`body_mask_export.py` の 3値対応（assist）**: 小学校より前のエリア用。`sit-field-mask` の3クラスを出力できるように。
6. **【低】ツールのテスト**: 体内17枚の clean を使い、リファクタ前後の出力 sha256 が一致することを確認するスモークテスト。

注（E2 の画像）: `docs/production/oblique-mocks/*/e2/` の生成画像（take*.png）・重ね画像（overlay-*.png）・style-ref.png は 2026-10-23 以降 git に入れない（`.gitignore`。ディスクには残る）。それ以前に追跡済みの TRM-02 e2 の PNG は履歴に残る（追跡だけ外した）。metrics・prompt・report は追跡する。

