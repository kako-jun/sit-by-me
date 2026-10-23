# BDY-04（頭・脳の迷路通路）装飾込み1回生成の完全 imagegen prompt（`build_body_prompt.py` 自動生成。Issue #142）

> 履歴: 2026-10-22 時点の生成記録。2026-10-23 に TRM-01 は TRM-03 に統合（園庭=TRM-03の右の区画、起点は TRM-03.event-kiss）。現行の正本は docs/map-topology.md と docs/production/body-masks/BDY-01-links.json。本文中の TRM-01・行番号は当時のまま（送信済みの逐語記録）。

状態: **機械生成・独立レビュー未実施・画像未生成**。`.claude/skills/sit-field-background/SKILL.md` のゲート（台帳原文・材料固定宣言・一意解釈・寸法）に沿う。型は採用済み BDY-02（v2 の構図・原文束、v3 の装飾語彙）。画像は生成しない。

## 0. 来歴・警告・TBD

来歴:
- 生成器: `.claude/skills/sit-field-background/tools/build_body_prompt.py`（使い方: `build_body_prompt.py BDY-04 --out DIR`）。入力は docs の対象行（逐語）・Issue #142・`verification/body-layout/clean/BDY-04.png` の画素実測・`body_layout.py` の折れ線。
- 型: `docs/production/20261022-bdy02-adoption.md` と `20261022-bdy02-adoption-prompts/`（v2-prompt-full.txt=構図・原文束、v3-edit-prompt.txt=装飾語彙）。
- 入力 sha256（参照2枚。様式参照画像は幾何を崩す疑いがあるので使わない）: clean `8471d90252f1ede8ced36e5e96477cff1aaa664078a5f4d12d7b1498c1d04ff0` / 材料見本 `764b7ae7f1aa0ff19bd8e79a8724fc8b975c4d5465440fb539f5566f52828b45`
- 送信文 sha256: `4463974f5a1abc5b42eb8a8e025b248bb2cfd9ba6c3311d1d371efe319c91d7f`
- 送信文: `BDY-04-prompt-send.txt`（wrapper + 本文。この .md の §3.1 と §3.2 を連結したもの。§3.2 は §1 の原文束を SOURCE TEXT として含む。原文束の外に内部メモ・TBD・仮案を含まない）。

警告・TBD（ビルダーが検出）:
- 決定済み: 脳=迷路・胃=分岐なしJ字の1袋・心臓=2x2の丸い4部屋の環・肺=案A（外周の環・行き止まりなし）。kako-jun 決定・モック承認（2026-10-22。Issue #142）。docs の『単純な分岐室』『分岐室』は逐語の原文として残る。この MAP の形は P4 が肯定形で明示している（原文束の外の自作部分）。
- 座標・半径・通路の接続は clean 画素の実測（body_layout の SPECS と照合済み）。別コードの再測定: verification/body-layout/remeasure_body_rooms.py [BDY-xx]（prompts/BDY-xx-prompt-send.txt の数値を clean 画素と照合）。
- 装飾込み1回生成（onepass）: 参照は2枚（clean 割付図・材料見本）。様式参照画像は使わない。壁・仕切りは細い corrugated の帯1本（迷路 約8px・他 約12px）＋毛糸1本で、床の幅は壁の内側基準で守る。
- 赤紙6枚は clean の地形で周囲の正方形が全て地形の点から決定的に選び、座標を本文に固定した（BDY-02 の方式）。
- 部屋名（右心房など）は原文束にだけ現れ、絵には描かない。本文は部屋を丸い床と呼び、臓器の輪郭を描かせない。
- 生成前の独立レビューは未実施（SKILL: 生成可には独立レビュー通過が必要）。
- 迷路の記述（2026-10-22 独立レビュー反映）: P4 の先頭に『ステンシル宣言』（cream=床・他=地形・通路を動かさない・13x6格子・木・幅77px・壁は幅の約0.55倍）、全体構造のランドマーク6個（clean 画素の実測から機械検査）、格子の全通路の行・列ごとの列挙、本数77・行き止まり11・T字10・曲がり38。経路の曲がり点列は外した。原文束（SOURCE TEXT）は WHAT TO DRAW と REFERENCE の後ろ（wrapper → DRAW → REFERENCE → SOURCE）。原文束は迷路に無関係な行（topology 690・692・体内の17MAP表・decisions の体内入口・research の17MAP行）と Issue の『櫛型より複雑にする』決定行を載せない（slim）。生成が迷路を簡略化する危険があり、生画像で通路の接続を必ず確認する（再生成は最大2回まで許可）。
- 入口の帯の幅は1人幅（77px）。原文に無く、割付図（承認済みモック）どおり。

## 1. 原文束（逐語。要約・言い換えなし）

```text
(This block is a specification, not text to be drawn. No letter, number or word from it may appear in the picture. Lines about other maps are context only: draw only this one map.)
[Issue #142 全文（gh issue view 142 --json title,body。1行目=タイトル、以降=本文、逐語）]
素材: 体内17MAP（BDY-01〜17）の配置モック・契約・背景生成
## 背景
kako-jun 指示（2026-10-22）: 「体内など、未確定の要素が少ないマップからエリアぜんぶのマップ画像を作っていきたい」。全15エリア・130MAPの背景を、未確定が少ないエリアから順に作る。第1弾は体内17MAP（BDY-01〜17）。

## 体内を最初にする根拠
- 接続は map-topology.md v2台帳と docs/topology/body.svg で確定済み（17ノード・17接続・一本道＋分岐室）。
- 材料は art-direction.md「#74 体内の最新空間・色の契約」で確定（foamboard土台・corrugated断面・paper clay・肌色/薄桃/クリームのposter paint・赤い折り紙は工作アクセント）。
- 未確定は「通行幅（キャラ3人分）の画素値・脳の迷路形・pixel/mask」だけ。BDY-02 は先行previewが却下済みで、再生成前に配置モックが必要（contract-checklist 140行）。

## これからやること
1. **配置モック（割付図）**: 17MAPそれぞれの画像端の接続辺・通路の向き・幅（3人分）を、体内の方位（body.svg）と整合させて幾何で作る。BDY-02 から着手し、全MAPの辺の整合（出た辺の反対の辺から入る）を機械検査する。
2. **契約と完全prompt**: 対象行の原文束（registry/specifications/topology/checklist）を逐語添付し、独立レビュー（opus）を通す。
3. **1枚ずつ生成→実寸検査（1920×1080 または 1672×941）→生画像レビュー→kako-jun採否**。順序は BDY-02 → 首（BDY-01）・頭（BDY-04）→ 手足 → 分岐室（心臓・肺・胃）→ BDY-03。
4. 不合格は削除して来歴だけ記録。採用はWebP化して reference 配下へ（mask・links・red-team は別工程）。

## 体内の後の順序
体内が通ったら、未確定の少ない順に他エリアへ進む。順序案は別コメントで棚卸し後に提示する。
[優先規則] 最新のコメントが、それより前のコメントに優先する。
[Issue #142 決定コメント（時系列順。各コメントの見出しと、BDY-04 に関わる決定の行だけを逐語で抜粋。相互に食い違う場合は、より後のコメントが優先）]
## kako-jun 決定・指摘（2026-10-22、モック一覧を見て）
4. **脳・心臓・肺など**（「肺や心臓などは、医学的に右心室など4つに分かれているとかを抽象的に表現すればいい。脳は迷路状ということだな」）→ 脳=迷路状。心臓=解剖学の4つの部屋（右心房・右心室・左心房・左心室）を抽象的な4つの部屋と通路で表す。肺・胃も同様に実際の区分を抽象化（分け方の詳細は kako-jun が示した「など」までなので仮案を出してモックで確認）。血・写実的な臓器は描かない（既存方針）。
[docs/map-topology.md:118]
以下は接続の向きを一意にする正本である。`→` の両側は必ず反対の画像辺とし、`door` は画像端でなく室内・階層遷移である。`event` は一方向の物語イベント、`oneway` は一方向の通常移動。`door-passage-*` は体内の抽象通路名で物理的な扉ではない。`pending` は旧仮説のID追跡だけの行で、隣接・通行路・生成契約ではない。`§3.1` 以降の旧試作時の図・発注文は履歴説明であり、ここにない辺指定を新規プロンプト、画像生成、マスクに使ってはならない。
[docs/map-asset-registry.md:91]
| ID | 画像 | 地区 | 未決のため必要な個別契約 |
[docs/map-asset-registry.md:92]
|---|---|---|---|
[docs/map-asset-registry.md:116]
| BDY-04 | `BDY-04` | 抽象体内 | 頭・脳の迷路通路。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。迷路状の通路。通路幅はキャラクター1人分（約77px。模型の天面比0.047）、入口は南辺中央1本、行き止まりの迷路（出口なし）。形の詳細（座標・格子）は verification/body-layout の割付図が正本。pixel/maskはTBD（mask未作成）。 |
[docs/map-specifications.md:117]
| MAP | 時期 | 一言特徴 | 方位・主路・通行条件 | 暫定固定 |
[docs/map-specifications.md:118]
|---|---|---|---|---|
[docs/map-specifications.md:124]
| BDY-04 | 中3 | 頭・脳の迷路通路 | door-passage-torso→BDY-02.door-passage-head | 上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。迷路状の通路。通路幅はキャラクター1人分（約77px。模型の天面比0.047）、入口は南辺中央1本、行き止まりの迷路（出口なし）。形の詳細（座標・格子）は verification/body-layout の割付図が正本。pixel/maskはTBD（mask未作成）。 |
[docs/map-contract-checklist.md:11]
| ID | 状態 | Ref | mask / 出力 | 具体的TBD |
[docs/map-contract-checklist.md:12]
|---|---|---|---|---|
[docs/map-contract-checklist.md:80]
| BDY-04 | blocked | R018 | 未生成・mask未作成 | 頭・脳の迷路通路。door-passage-torso→BDY-02.door-passage-head。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。迷路状の通路。通路幅はキャラクター1人分（約77px。模型の天面比0.047）、入口は南辺中央1本、行き止まりの迷路（出口なし）。形の詳細（座標・格子）は verification/body-layout の割付図が正本。pixel/maskはTBD（mask未作成）。 |
[docs/map-topology.md:248]
| BDY-02.door-passage-head | BDY-04.door-passage-torso | door | 架空人体の抽象通路。door-passageは物理的な扉でない。上半身/下半身2枚・手各2枚・足各3枚の連続一本道 |
[docs/art-direction.md:195]
## #74 体内の最新空間・色の契約
[docs/art-direction.md:199]
体内は医学的な身体の再現でなく、現実離れした幼稚園児の想像する架空人体の抽象的概念。肌色寄りでよく、血や写実的な臓器・内壁を描かず、グロくしない。胴体は縦2MAPの上半身/下半身、手各2MAP・足各3MAPの縦通路ボリューム。頭は上、手は斜め上、足は斜め下。脳は迷路状通路、心臓・肺は単純な分岐室。背景共通の手作りジオラマに合わせ、5 mm foamboardの土台と見えるcorrugated cardboard断面、指跡・爪楊枝の跡を残したpaper clayの丸い地形を使う。肌色・薄桃・クリーム色のmatte poster paintで着色し、赤い折り紙を切った形を血痕に見えない明確な工作アクセントとして置く。毛糸は通路の縁や造形の継ぎ目に用い、雪の綿は使わない。白いPVA接着剤とmasking tapeで固定し、紙端・接着・塗りの手作り感を残す。旧『紙粘土・セロファンだけ』『口から手足が直結』という解釈を新規生成の固定根拠にしない（材料決定は2026-10-21 kako-junとの相談）。
[docs/art-direction.md:30]
- 背景はタイルを無限に継ぎ足さない。場所ごとに、全景・広い道路・狭い道・接続画を同じカメラ、光、反復物で一度に作る。視点は、真上に近い見下ろし（2026-10-14 変更。以前の「高めの斜め見下ろし（約45°）」は撤回）。フィールドは固定の一枚絵で、スクロールしない。絵の端（模型の縁の辺）で次の絵に切り替わる（2026-10-14）。通路は画像端でなく模型の縁まで届き、土台の板とまわりの机は見えたまま。遷移位置は画面端固定でなく範囲指定（2026-10-22 kako-jun）。
[docs/map-reference-research.md:24]
| R018 | BDY-01〜BDY-17 | `docs/art-direction.md` と `docs/assets-policy.md`／プロジェクト正本 | 人体の写実・流血・臓器表現を避け、幼稚園児が想像する架空人体を肌色寄りの手作りジオラマで表す。共通背景の工作材（foamboard・段ボール・paper clay・matte poster paint）に、赤い折り紙の切片と毛糸を加える。雪景色の綿は使わない（2026-10-21決定） | 体内のMAPごとの敵・戦闘域は各契約行で決める |
[docs/map-asset-registry.md:174]
| ID | 管理名 | 地区 | 契約 |
[docs/map-asset-registry.md:175]
|---|---|---|---|
[docs/map-asset-registry.md:176]
| BDY-02 | `BDY-02` | 抽象体内 | 上半身・胴体上段。7経路は模型（ジオラマ）の縁の辺で隣MAPへ遷移し（遷移位置は辺上の範囲指定、範囲値TBD。土台の板と机は見えたまま）、方位は `docs/topology/body.svg` に従う（口=北東、頭=北、左腕=北東（東辺から出る）、右腕=北西（西辺から出る）、下半身=南、心臓=南東、肺=南西。**左右は身体の本人から見る（本人は仰向け、それを正面から見る構図なので、画面左が本人の右手・右足、画面右が本人の左手・左足。kako-jun 2026-10-22、#142）**。左足・左手は画面右、右足・右手は画面左。心臓は画面右（南東）、肺は画面左（南西）。南辺は 肺=左寄り・下半身=中央・心臓=右寄り）。口から胴体への首道は1本、頭道はそこから分岐。体外形・洞窟口は描かず、平面床と低い仕切りで道を作る。心臓・肺の部屋と胃は描かない（胃はBDY-03からBDY-15へ接続）。架空人体・非写実・肌色寄り・非グロ、主路幅はキャラクター3人分程度。体内材料は `art-direction.md`／`map-specifications.md` を参照。
[docs/map-specifications.md:203]
| MAP | 時期 | 一言特徴 | 接続 | 不変条件／TBD |
[docs/map-specifications.md:204]
|---|---|---|---|---|
[docs/map-specifications.md:205]
| BDY-02 | 中3 | 上半身・胴体上段（最初に契約する体内MAP） | door-passage-mouth→BDY-01.door-passage-torso、door-passage-lower→BDY-03.door-passage-upper、door-passage-head→BDY-04.door-passage-torso、door-passage-left-arm→BDY-05.door-passage-torso、door-passage-right-arm→BDY-07.door-passage-torso、door-passage-heart→BDY-16.door-passage-torso、door-passage-lung→BDY-17.door-passage-torso | 上半身の独立した1MAP。各通路は画像端でなく模型（ジオラマ）の縁の辺まで届き、そこで隣のMAPへ遷移する（土台の板とまわりの机は見えたまま。遷移のトリガー位置は辺上の範囲（レンジ）で指定し、画面端に固定しない。範囲の数値はTBD。接続は辺単位の判定のままで画素一致は条件にしない。kako-jun 2026-10-22）。配置方位は `docs/topology/body.svg` に従う: 口=北東、頭=北、左腕=北東（東辺から出る）、右腕=北西（西辺から出る）、下半身=南、心臓=南東、肺=南西。**左右は身体の本人から見る（本人は仰向け、それを正面から見る構図なので、画面左が本人の右手・右足、画面右が本人の左手・左足。kako-jun 2026-10-22、#142）**。左足・左手は画面右、右足・右手は画面左。心臓は本人の左側で画面右（南東）、肺は画面左（南西）。南辺は 肺=左寄り（BDY-17）・下半身=中央・心臓=右寄り（BDY-16）。心臓BDY-16は北辺から、肺BDY-17は北辺中央から入る（出た辺の反対）。首は広間から1本、上で頭（北）と口（北東）に分岐。口から胴体へ入る首の通路は1本だけで、頭はそこから分かれる北向きの枝。体の外形は描かず、平面の床と低い仕切りだけで通路を作る。心臓・肺の部屋自体はBDY-16/17にあるため描かず、胃への接続も置かない（胃BDY-15は下半身BDY-03から接続）。7接続のみ。幼稚園児が考える架空人体、肌色寄り・非写実・非グロ。全主路・枝はキャラクター3人分程度の幅。材料は体内共通仕様。
[docs/map-contract-checklist.md:138]
| ID | 状態 | Ref | mask / 出力 | 具体的TBD |
[docs/map-contract-checklist.md:139]
|---|---|---|---|---|
[docs/map-contract-checklist.md:140]
| BDY-02 | blocked | R018 | 先行previewはユーザー却下（体の外形・洞窟状の穴）。正本未保存・mask未作成。再生成前に配置モックが必要。 | 上半身・胴体上段。接続契約は `map-specifications.md` BDY-02 行と `docs/topology/body.svg` を照合する。口から胴体への首道は1本、頭はその枝。各経路は模型（ジオラマ）の縁の辺まで届いて隣MAPへ遷移する（遷移位置は辺上の範囲指定、範囲値TBD。土台の板と机は見えたまま。kako-jun 2026-10-22）。体外形・洞窟口・物理扉なし。平面床と低い仕切り。心臓・肺の部屋はBDY-16/17、胃BDY-15はBDY-03から接続。架空人体・非写実・肌色寄り・非グロ、通路幅はキャラクター3人分程度、体内材料は `art-direction.md` 参照。配置モック、生画像レビュー、採否、maskは未完了。
[注記] 主路幅は天面幅比0.14=230px。この MAP の通路はキャラクター1人分＝その1/3＝77px。
```

## 2. 参照一覧（実画像として入力する順。参照は2枚）

| # | パス | 用途 | 継承禁止事項 |
|---|---|---|---|
| 1 | `verification/body-layout/clean/BDY-04.png`（1920x1080、4色のベタ。灰=机、茶=土台縁の帯、くすんだ桃茶=天面の地形、クリーム=歩ける床。文字・注記・遷移範囲の着色なし。画像編集の入力＝塗り直しの土台） | 幾何のみ（机・土台縁・天面の入れ子、通路の本数・辺・位置・幅・曲がり・端） | 色を塗らせない（5色ベタ・硬い直線エッジは継承しない）。文字・遷移範囲の印を残さない |
| 2 | `verification/body-layout/BDY-material-swatch-corrugated-edge.png`（1540x52。寺町の採用画像の下端の帯を無加工で切り出した材料見本） | 材料の感じのみ: corrugated cardboard 断面・masking tape・ちぎれた紙端 | 帯上端の白い綿の繊維・茶色の色味は継承しない。雪を持ち込まない |
添付順 = 1, 2（wrapper の『Two images』の列挙と本文 REFERENCE の FIRST/SECOND が一致）。

## 3. 送信予定の完全 prompt

### 3.1 前置き指示（wrapper）

```text
Invoke the $imagegen skill and use the built-in image_gen tool at the HIGHEST quality (quality: high), keeping the editing source's size 1920x1080 (16:9), to repaint the image as described in the prompt below. This is an IMAGE EDIT: use the image_gen tool in image-edit mode on the first attached image. Two images are attached, in this order: (1) the editing source (a flat four-colour layout diagram with no text; keep its geometry exactly, and use the meaning of its colours as described in the prompt); (2) a thin close-up strip of the edge of a hand-made cardboard miniature, for materials and craft feel only (as described in the prompt). Call image_gen EXACTLY ONCE: no retries, no regeneration, no multiple candidates, even if you think the result is imperfect. Then save the REAL generated PNG (decode the tool result) into the current workspace at out/bdy04-op-v1.png. You are STRICTLY FORBIDDEN from fabricating/drawing the image with magick/ImageMagick/PIL/Pillow/numpy/SVG/canvas/any code; only the image_gen tool. If the image_gen tool is genuinely not in your toolset, do NOT fabricate - output exactly: IMAGE_GEN_TOOL_UNAVAILABLE. Do not resize or crop the result. Do not use any files in ~/.codex/generated_images/ made by other calls; only the image generated in this call. Report the saved file path.
Output a 16:9 landscape image. Keep the size of the editing source (1920x1080); if not possible, 1672x941. Do NOT use 3:2 or 1536x1024. Do not mirror or flip the image; keep the direction of the editing source.
```

### 3.2 本文

```text
Generate ONE image: the final field background for map BDY-04 (a maze of narrow one-person-wide passages, of the imaginary human body inside which the story travels). Do not generate any other map.

=== WHAT TO DRAW (positive description; sentence numbers P1.. are referenced below) ===
P1. COMPOSITION. The whole picture is a hand-made tabletop miniature seen from almost straight above: a model standing on a desk. From the outside in on ALL FOUR sides (north, south, west and east alike): (a) the desk surface, a warm natural wooden tabletop with visible wood grain, a 90 px margin on all four sides of the frame, mostly clear wood (at most a few small craft leftovers lie on it, well clear of the model); (b) the model's base, seen from above as a border band 48 px wide that frames the top surface all the way around, unbroken (no side face of the model is visible); (c) inside the band, the top surface of the model, which is the map. Frame coordinates (1920x1080): the base band's outer edge is the rectangle x 90 to 1830, y 90 to 990; the model's top surface is the rectangle x 138 to 1782, y 138 to 942 (1644 x 804 px). (In the 1672x941 frame these are: band outer edge x 78 to 1594, y 78 to 863; top surface x 120 to 1552, y 120 to 821.) On every one of the four sides of the picture, going inward from the picture's edge, you see in this order at full width: the wooden desk (90 px), then the cream foamboard rim (28 px), then the brown corrugated cardboard cross-section (20 px), then the terrain. The model's top surface lies wholly inside the picture and touches none of its edges; the north and south sides show the desk, the rim and the corrugated band exactly as the west and east sides do. Nothing is drawn outside the model except the wooden desk and its few craft leftovers: no wall, no room, no sky, no horizon, no people. The model is a miniature, so the whole picture is a model; the picture never reads as a photograph of a real place.
P2. THE BASE BAND. Seen from above it is a framing border around the top surface. Its outer 28 px (x 90 to 118 along the left side, and likewise on the other sides) is the rim of a 5 mm foamboard slab (smooth pale white-cream paper-faced foam core, with the paper skin and the foam core visible along the rim). Its inner 20 px (x 118 to 138 on the left, and likewise on the other sides) is the exposed cross-section of corrugated cardboard (the wavy flute layer between two flat liners, brown), glued around the foamboard's top edge with masking tape and white PVA glue, with ragged hand-cut paper edges. The band runs unbroken along all four sides, north and south included, with both the foamboard rim and the corrugated layer clearly visible on each side. It is not interrupted where the passage reaches the model's edge. A few extra strips of masking tape and small PVA drips may lie on the band, never hiding the corrugated layer over any long stretch.
P3. THE ENTRANCE AND THE MODEL'S EDGE. The model's top surface is made of thin flat paper-clay surfaces. ONE single flat floor band, 77 px wide measured across the band (0.047 of the model's width of 1644 px, which is 67 px in the 1672x941 frame; the width of one character; no character is drawn), runs straight inward from the model's edge (exactly perpendicular to the edge, with no bend) into the first cell of the maze, at about (960, 840), and it reaches the model's edge and stops flush against the inner edge of the corrugated band of P2: the floor band ends where the model ends, at the band, and never continues onto the band, the desk or the frame edge (it leads on to the next map across the model's edge; the character stands anywhere within a stretch of the edge to cross over, so nothing marks a crossing point). No marker, coloured zone, arrow, line or label of any kind is drawn at the edge. Position where the band meets the model's edge, in the 1920x1080 frame, measured from the layout diagram (first image):
  - South edge (bottom, y 942), 1 passage: the entrance passage at x 921 to 998.
  Along every other stretch of the model's four edges, the edge is solid raised paper-clay terrain meeting the corrugated band: the entrance band is the only floor that reaches the model's edge, 1 in all.
P4. THE MAZE. The cream area of the first image is the stencil for the floor: every cream pixel stays floor, every other pixel stays terrain. Do not move, add, remove, merge or simplify any passage, dead end or junction; only repaint the surfaces. The maze is a 13 columns x 6 rows lattice, a loop-free network (exactly one route between any two cells), passage width 77 px, partition wall about 0.55 times the passage width (42 px). The whole floor of this map is ONE maze of narrow corridors. Every corridor is exactly 77 px wide across its whole length, the width of one character. The corridors lie on a regular square grid of 13 columns by 6 rows; the centres of neighbouring grid cells are 120 px apart. In the 1920x1080 frame the centre of the cell in column c (c = 0 to 12, counted from the left) and row r (r = 0 to 5, counted from the top) is at x = 240 + 120 c and y = 240 + 120 r (the top-left cell is at (240, 240), the bottom-right cell at (1680, 840)); in the 1672x941 frame every coordinate in this paragraph is multiplied by 0.871. A corridor runs from cell to cell along the grid lines, horizontally along a row's centre line or vertically along a column's centre line, so every bend is a right angle (the outer corner of each bend is rounded with radius 38 px, the inner corner is a plain sharp right angle). All 78 cells are part of the maze, joined by 77 corridor links between neighbouring cells. THE ENTRANCE: the single entrance band comes in from the south edge at x 921 to 998 (centre x 960) and runs straight up to the cell in column 6, row 5, at (960, 840), where the maze begins. THE WALLS: between any two corridors lies a wall of terrain at least 42 px thick (neighbouring cells that are not joined are separated by 42 px of terrain), and a frame of terrain about 63 px wide runs all around the maze, between the outermost corridors and the base band. Two corridors never touch except where they are joined at a cell. LANDMARKS of the whole maze, to check the drawing against (centre lines, 1920x1080 frame): (1) the longest straight corridor of the maze runs along the top row from (240, 240) to (960, 240), and ends there in a closed round end; (2) along the bottom row on the right, a long straight corridor runs from (1200, 840), where it ends in a closed round end, to (1680, 840); (3) down the left side, a long straight vertical corridor runs at x 240 from (240, 480), where it ends in a closed round end, down to (240, 840); (4) in the upper right is a U-shaped hook: a corridor runs along the top row from (1440, 240) to (1680, 240), turns down at its left end to (1440, 360), and turns down at its right end to (1680, 480), where it ends in a closed round end (a short corridor from the left joins the right leg at (1680, 360)); (5) in the middle on the right, two long straight corridors lie one above the other with a wall between them: one at y 480 from x 1080 to x 1560, one at y 600 from x 1080 to x 1440, and the only short link between them is the vertical corridor at x 1080 from y 480 to y 600; (6) in the middle of the maze a vertical corridor runs at x 960 from (960, 360) down to (960, 600). THE CORRIDORS: every corridor is a straight run between the listed end points (centre lines, 1920x1080 frame). Horizontal runs, by row, from the cell centre at the left end to the cell centre at the right end:
    row 0 (y 240): x 240 to 960 and x 1080 to 1320 and x 1440 to 1680
    row 1 (y 360): x 240 to 360 and x 600 to 720 and x 960 to 1200 and x 1320 to 1440 and x 1560 to 1680
    row 2 (y 480): x 360 to 480 and x 600 to 720 and x 1080 to 1560
    row 3 (y 600): x 240 to 360 and x 600 to 720 and x 840 to 960 and x 1080 to 1440 and x 1560 to 1680
    row 4 (y 720): x 360 to 480 and x 720 to 960 and x 1080 to 1320 and x 1440 to 1560
    row 5 (y 840): x 240 to 480 and x 600 to 840 and x 960 to 1080 and x 1200 to 1680
  Vertical runs, by column, from the cell centre at the top end to the cell centre at the bottom end:
    column 0 (x 240): y 240 to 360 and y 480 to 840
    column 1 (x 360): y 360 to 480 and y 720 to 840
    column 2 (x 480): y 360 to 720
    column 3 (x 600): y 360 to 480 and y 600 to 840
    column 4 (x 720): y 240 to 360 and y 480 to 600 and y 720 to 840
    column 5 (x 840): y 240 to 480 and y 600 to 720
    column 6 (x 960): y 360 to 600
    column 7 (x 1080): y 240 to 360 and y 480 to 600 and y 720 to 840
    column 8 (x 1200): no vertical run
    column 9 (x 1320): y 240 to 360 and y 720 to 840
    column 10 (x 1440): y 240 to 360 and y 600 to 720
    column 11 (x 1560): y 360 to 480 and y 600 to 720
    column 12 (x 1680): y 240 to 480 and y 600 to 840
  Each run is a straight corridor, and every cell centre lies on at least one run; two runs that share a cell centre are joined there. COUNTS that stay exactly as they are: 77 corridor links; 38 bends (right-angle turns of a corridor); 10 T-junctions (a cell where three corridors meet) at (720, 240), (840, 240), (1080, 360), (1680, 360), (480, 480), (240, 600), (840, 720), (360, 840), (720, 840), (1320, 840); 11 dead ends, each a closed, rounded end (a semicircular cap of radius 38 px beyond the last cell centre) at the cell centres (960, 240), (480, 360), (1200, 360), (240, 480), (840, 480), (1680, 480), (360, 600), (960, 720), (480, 840), (840, 840), (1200, 840). There is no crossing of four corridors and no loop: from the entrance there is exactly ONE route to every point of the maze, never two ways to the same place. The route from the entrance to the dead end at (240, 480) is one of the two longest routes of the maze (the other ends at the dead end at (360, 600); both are 65 links from the entrance). Keep the number of corridors and the number of dead ends as listed: do not add a corridor, do not remove one, do not shorten, extend, straighten or reroute one, do not open a wall to join two corridors, do not turn a dead end into a loop, and do not replace the maze by any simpler or more regular pattern. Nothing lies at the dead ends: no object, no mark, no door.
P5. NOTHING ELSE ON THE FLOOR. Only the entrance, the corridors, the bends, the T-junctions and the dead ends described in P3 and P4 are drawn: no hall, no round room, no loop, no crossing of four corridors, and no connection to any other map except through the one model's edge named in P3. The floor is empty: no body parts, no faces, no object lies on it.
P6. PARTITIONS. Along the floor edges (the edges of the corridors), on the terrain side of the floor outline, run LOW PARTITIONS: narrow low ridges (seen from above as narrow raised borders) made of ONE narrow, low band of corrugated cardboard each (no stacking), with paper clay smoothed over its top, which make the corridors. Each partition is only about 8 px wide and stands entirely on the terrain side of the floor outline, on the boundary where the terrain face meets the floor; no floor colour appears outside a partition. The clear cream floor between the inner faces of the partitions keeps exactly the width of the cream area of the first image, 77 px for the corridors; the thickness of a partition is never counted inside the floor width and never eats into it. A wall of about 42 px between two corridors therefore carries two partitions, one for each corridor, with about 26 px of flat painted terrain left between them; no yarn strand is laid in that narrow channel. Along the outer frame of the maze, on the terrain side of the outermost partitions, runs ONE thin edging strand of yarn (cream). There are no doors, door frames or gates, no cave mouths, no round holes or tunnel mouths, no outline of any body or organ: the top of the model is only flat floor, low partitions, yarn edging and decorated terrain.
P7. THE TERRAIN. The terrain is a thin, flat sheet of paper clay, painted face by face in matte poster paint, the terrain pale pink leaning, with a few skin-tone faces mixed in, laid on with a flat brush (brush streaks and uneven coats visible), a different tone for each face. The terrain is the place for the handwork decoration of P9, which stays inside the same warm range of colours (see P8). It has no thick mounded layers, no stacked flesh-like bands, no striations and no fleshy cross-sections. It is ONE connected surface: the frame around the maze (about 63 px wide on every side) and the walls between the corridors (42 px thick or more) are the same sheet; the corridors are cut out of it.
P8. COLORS: passage floors: matte poster paint in cream and pale peach, the same range everywhere. Terrain: matte poster paint, pale pink leaning, with a few skin-tone faces mixed in, one tone per face. COLOURS OF THE DECORATION: every decoration item is coloured only within skin tone, pale pink, cream, ivory and brown shades (yarn: light to deep shades of cream, pale pink and skin tone; beads, buttons, discs and clay balls: cream, pale pink, skin tone or light brown; toothpicks: natural wood). The red of the six origami pieces of P10 is the only other colour in the model, and the desk is natural wood. So the whole model reads as one warm family of skin, pale pink, cream and brown. The edging yarn is cream. The desk is warm natural wood (honey-brown grain with a few wide soft rings). Partitions: corrugated cardboard strips with paper clay on top, in brown and skin tones.
P9. DECORATION (hand-made craft ornament about the human body, placed on the terrain only: the raised items (coils and bundles of yarn, clay balls, buttons, beads, spiky germs, thread tufts) stand on the terrain frame around the maze, on the four {int(min(rg['frame']))} px corner squares of the outer frame, on the edge of the base band and on the desk; the walls between the corridors are not kept bare, they carry the carved patterns and flat tape strips described below; and nothing is placed inside a corridor). The decoration is made ONLY of small abstract handmade items that belong to the human body, in the kinds listed below as the leading and the supporting motifs; no other kind of ornament is used. This map has its own decoration theme, different from the neighbouring maps. The leading motifs are: MAIN motif (skin): skin texture carved into the paper clay with a toothpick: fingerprint-like swirls of concentric lines, fields of tiny pore dots, and short parallel scratch lines; SECOND motif (cell): cells and grains: round balls of paper clay with fingerprints, beads, buttons and small flat discs in cream, pale pink and skin tone, glued singly, in pairs, in lines or in small heaps; THIRD motif (germ): germs as a child imagines them: small round balls of paper clay with short toothpick spikes sticking out all around, cute abstract shapes, in cream, pale pink or light brown. Only as small supporting touches, never as the main look: a few short zigzag lines of yarn; a few small tufts of thread hair; a few short yarn bundles and small coils. ARRANGEMENT: SPIRAL CHAIN: a chain of spiral shapes (fingerprint swirls, coils of yarn, rolled clay, round cells in rings) linked one after another around the terrain frame and over the corner squares, small items filling the gaps. EDGE COLOURS: the edging strand of yarn at the foot of the outermost partitions is cream; the masking tape and PVA of the base band are skin-coloured masking tape and white PVA. The colours of the decoration are given in P8. THE DESK: a warm wooden tabletop, honey-brown grain with a few wide soft rings; around the model lie a thread end and two tiny clay balls along the upper desk margin (only these, small and few; nothing on the desk covers or touches the base band over a long stretch). DENSITY at kindergarten-craft level, in proportion to the area of the terrain: the decoration forms at least 6 groups of raised items on the frame, the corner squares and the desk (arranged as the ARRANGEMENT says: the chain runs all the way around the frame), with carved patterns along the walls, so the picture feels rich and handmade. The walls between the corridors (about 42 px of terrain) are decorated only with toothpick-carved lines and dots (fingerprint swirls, pore dots, short parallel scratch lines) and flat strips of skin-coloured paper tape; no raised or three-dimensional item stands on a wall, and every carving stays inside its wall without crossing a partition. Yarn and threads are short separate strands, swirls and edging: they never run as a net like blood vessels or veins and never look like an organ.
P10. RED ORIGAMI: EXACTLY SIX (6) hand-cut red paper pieces with uneven edges (cut with scissors from red origami paper, flat on the surface, glued with PVA), no more and no fewer: count them, six, with no seventh and no spare piece anywhere. Exactly six red origami pieces, each about 30 px across (in 1672x941: about 26 px), centred at about: (165, 165); (1135, 165); (1755, 280); (650, 915); (1200, 915); (1755, 915) (six in total), all on terrain faces inside the model (x 138 to 1782, y 138 to 942; in 1672x941: x 120 to 1552, y 120 to 821), none on any floor, partition, rim or desk, none anywhere outside the model. Their outlines are irregular and unequal, not drawn as any particular symbol; they are clean paper cut-outs, never blood stains or liquid. They are the only red objects in the picture. Nothing of P9 is laid over them: they are not a base for ornament.
P11. THE FLOOR STAYS EMPTY. Nothing of P9 lies on the cream floor, crosses into it or touches it: the corridors stay perfectly flat, clean and empty, nothing is placed where the characters walk, and the width of the corridors, the position of every dead end and the flatness of the floor are exact. The surfaces of the model are flat floors, partitions and decorated terrain only. The floor and terrain contain no figures, spirits, flames or water pictures; every object is a small hand-made craft piece in the colours listed.
P12. MATERIALS (every material must be identifiable at full size): base: 5 mm foamboard with the corrugated cardboard cross-section band described in P2; terrain surface: paper clay modelled by hand; partitions: one low corrugated cardboard strip each under smoothed paper clay; floors and terrain: matte poster paint applied with a flat brush; the joint of the band: masking tape; decoration (handmade items about the human body): wool yarn, thread, paper-clay balls, buttons, beads, toothpicks, skin-coloured tape, white PVA glue; accents: 6 pieces of red origami paper cut by hand with scissors; desk: wooden tabletop with visible wood grain. Hand-made roughness: ragged hand-cut paper edges, paint unevenness, visible material seams. Parts look like paper and clay (matte, soft edges), not like real skin, flesh, organs or stone. It reads as a crude hand-made miniature in which the whole picture is the model, and not as a photograph of a real place.
P13. CAMERA: the camera looks down steeper than 45 degrees from horizontal, as close to straight down as possible, never lower than 45 degrees from horizontal. North is the top of the image. Flat evenly lit tabletop light. The picture has no sky, no horizon, no vanishing point, no people, no characters, no readable text, no letters, no numbers, no logos.
P14. DIMENSIONS: request 1920x1080 (16:9). If the tool cannot return it, 1672x941 is acceptable (every coordinate above then scales by 0.871; the 1672x941 values are given alongside). Any other size is a failure; never resize or crop to pass. Measure the real output file.

=== REFERENCE (two attached images, in this order) ===
FIRST IMAGE: a flat layout diagram with four plain flat colours and no text. Its colours mean: grey = the desk; ochre-brown band = the base band's edge (P1, P2); dusty rose-brown inside the band = the model's top terrain (P7); light cream = the walkable floor (P3, P4). Copy ONLY the geometry exactly: the nesting of desk, base band (foamboard rim, then corrugated layer) and model top on all four sides, the single entrance at the south edge and its position, the grid of corridors (every corridor, every bend, every T-junction and every dead end where the first image has it, not one pixel moved), the corridor width of 77 px, the walls between the corridors and the frame around the maze. Treat the cream area as the clear floor width: the partitions stand in the terrain area next to it, never inside the cream. Repaint everything as the hand-made miniature described above. Do NOT carry over the diagram's four flat colours as flat fills (the desk is a warm wooden tabletop, the base band is foamboard and corrugated cardboard, there is no flat brown area anywhere in the result) or its perfectly straight, hard edges.
SECOND IMAGE: a thin close-up strip of the front edge of a hand-made cardboard miniature base. Take from it ONLY the feel of three materials, to be used for the base band of P2: the exposed corrugated cardboard cross-section (the wavy flute layer along the top of the strip), the masking tape, and the ragged torn paper edge. Take no content from it, and ignore the few white cotton fibres at its top edge and its brown colour. The decoration of P9 is described by the text only: no attached image carries any decoration to copy.


=== SOURCE TEXT (verbatim, do not paraphrase) ===
(This block is a specification, not text to be drawn. No letter, number or word from it may appear in the picture. Lines about other maps are context only: draw only this one map.)
[Issue #142 全文（gh issue view 142 --json title,body。1行目=タイトル、以降=本文、逐語）]
素材: 体内17MAP（BDY-01〜17）の配置モック・契約・背景生成
## 背景
kako-jun 指示（2026-10-22）: 「体内など、未確定の要素が少ないマップからエリアぜんぶのマップ画像を作っていきたい」。全15エリア・130MAPの背景を、未確定が少ないエリアから順に作る。第1弾は体内17MAP（BDY-01〜17）。

## 体内を最初にする根拠
- 接続は map-topology.md v2台帳と docs/topology/body.svg で確定済み（17ノード・17接続・一本道＋分岐室）。
- 材料は art-direction.md「#74 体内の最新空間・色の契約」で確定（foamboard土台・corrugated断面・paper clay・肌色/薄桃/クリームのposter paint・赤い折り紙は工作アクセント）。
- 未確定は「通行幅（キャラ3人分）の画素値・脳の迷路形・pixel/mask」だけ。BDY-02 は先行previewが却下済みで、再生成前に配置モックが必要（contract-checklist 140行）。

## これからやること
1. **配置モック（割付図）**: 17MAPそれぞれの画像端の接続辺・通路の向き・幅（3人分）を、体内の方位（body.svg）と整合させて幾何で作る。BDY-02 から着手し、全MAPの辺の整合（出た辺の反対の辺から入る）を機械検査する。
2. **契約と完全prompt**: 対象行の原文束（registry/specifications/topology/checklist）を逐語添付し、独立レビュー（opus）を通す。
3. **1枚ずつ生成→実寸検査（1920×1080 または 1672×941）→生画像レビュー→kako-jun採否**。順序は BDY-02 → 首（BDY-01）・頭（BDY-04）→ 手足 → 分岐室（心臓・肺・胃）→ BDY-03。
4. 不合格は削除して来歴だけ記録。採用はWebP化して reference 配下へ（mask・links・red-team は別工程）。

## 体内の後の順序
体内が通ったら、未確定の少ない順に他エリアへ進む。順序案は別コメントで棚卸し後に提示する。
[優先規則] 最新のコメントが、それより前のコメントに優先する。
[Issue #142 決定コメント（時系列順。各コメントの見出しと、BDY-04 に関わる決定の行だけを逐語で抜粋。相互に食い違う場合は、より後のコメントが優先）]
## kako-jun 決定・指摘（2026-10-22、モック一覧を見て）
4. **脳・心臓・肺など**（「肺や心臓などは、医学的に右心室など4つに分かれているとかを抽象的に表現すればいい。脳は迷路状ということだな」）→ 脳=迷路状。心臓=解剖学の4つの部屋（右心房・右心室・左心房・左心室）を抽象的な4つの部屋と通路で表す。肺・胃も同様に実際の区分を抽象化（分け方の詳細は kako-jun が示した「など」までなので仮案を出してモックで確認）。血・写実的な臓器は描かない（既存方針）。
[docs/map-topology.md:118]
以下は接続の向きを一意にする正本である。`→` の両側は必ず反対の画像辺とし、`door` は画像端でなく室内・階層遷移である。`event` は一方向の物語イベント、`oneway` は一方向の通常移動。`door-passage-*` は体内の抽象通路名で物理的な扉ではない。`pending` は旧仮説のID追跡だけの行で、隣接・通行路・生成契約ではない。`§3.1` 以降の旧試作時の図・発注文は履歴説明であり、ここにない辺指定を新規プロンプト、画像生成、マスクに使ってはならない。
[docs/map-asset-registry.md:91]
| ID | 画像 | 地区 | 未決のため必要な個別契約 |
[docs/map-asset-registry.md:92]
|---|---|---|---|
[docs/map-asset-registry.md:116]
| BDY-04 | `BDY-04` | 抽象体内 | 頭・脳の迷路通路。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。迷路状の通路。通路幅はキャラクター1人分（約77px。模型の天面比0.047）、入口は南辺中央1本、行き止まりの迷路（出口なし）。形の詳細（座標・格子）は verification/body-layout の割付図が正本。pixel/maskはTBD（mask未作成）。 |
[docs/map-specifications.md:117]
| MAP | 時期 | 一言特徴 | 方位・主路・通行条件 | 暫定固定 |
[docs/map-specifications.md:118]
|---|---|---|---|---|
[docs/map-specifications.md:124]
| BDY-04 | 中3 | 頭・脳の迷路通路 | door-passage-torso→BDY-02.door-passage-head | 上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。迷路状の通路。通路幅はキャラクター1人分（約77px。模型の天面比0.047）、入口は南辺中央1本、行き止まりの迷路（出口なし）。形の詳細（座標・格子）は verification/body-layout の割付図が正本。pixel/maskはTBD（mask未作成）。 |
[docs/map-contract-checklist.md:11]
| ID | 状態 | Ref | mask / 出力 | 具体的TBD |
[docs/map-contract-checklist.md:12]
|---|---|---|---|---|
[docs/map-contract-checklist.md:80]
| BDY-04 | blocked | R018 | 未生成・mask未作成 | 頭・脳の迷路通路。door-passage-torso→BDY-02.door-passage-head。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。迷路状の通路。通路幅はキャラクター1人分（約77px。模型の天面比0.047）、入口は南辺中央1本、行き止まりの迷路（出口なし）。形の詳細（座標・格子）は verification/body-layout の割付図が正本。pixel/maskはTBD（mask未作成）。 |
[docs/map-topology.md:248]
| BDY-02.door-passage-head | BDY-04.door-passage-torso | door | 架空人体の抽象通路。door-passageは物理的な扉でない。上半身/下半身2枚・手各2枚・足各3枚の連続一本道 |
[docs/art-direction.md:195]
## #74 体内の最新空間・色の契約
[docs/art-direction.md:199]
体内は医学的な身体の再現でなく、現実離れした幼稚園児の想像する架空人体の抽象的概念。肌色寄りでよく、血や写実的な臓器・内壁を描かず、グロくしない。胴体は縦2MAPの上半身/下半身、手各2MAP・足各3MAPの縦通路ボリューム。頭は上、手は斜め上、足は斜め下。脳は迷路状通路、心臓・肺は単純な分岐室。背景共通の手作りジオラマに合わせ、5 mm foamboardの土台と見えるcorrugated cardboard断面、指跡・爪楊枝の跡を残したpaper clayの丸い地形を使う。肌色・薄桃・クリーム色のmatte poster paintで着色し、赤い折り紙を切った形を血痕に見えない明確な工作アクセントとして置く。毛糸は通路の縁や造形の継ぎ目に用い、雪の綿は使わない。白いPVA接着剤とmasking tapeで固定し、紙端・接着・塗りの手作り感を残す。旧『紙粘土・セロファンだけ』『口から手足が直結』という解釈を新規生成の固定根拠にしない（材料決定は2026-10-21 kako-junとの相談）。
[docs/art-direction.md:30]
- 背景はタイルを無限に継ぎ足さない。場所ごとに、全景・広い道路・狭い道・接続画を同じカメラ、光、反復物で一度に作る。視点は、真上に近い見下ろし（2026-10-14 変更。以前の「高めの斜め見下ろし（約45°）」は撤回）。フィールドは固定の一枚絵で、スクロールしない。絵の端（模型の縁の辺）で次の絵に切り替わる（2026-10-14）。通路は画像端でなく模型の縁まで届き、土台の板とまわりの机は見えたまま。遷移位置は画面端固定でなく範囲指定（2026-10-22 kako-jun）。
[docs/map-reference-research.md:24]
| R018 | BDY-01〜BDY-17 | `docs/art-direction.md` と `docs/assets-policy.md`／プロジェクト正本 | 人体の写実・流血・臓器表現を避け、幼稚園児が想像する架空人体を肌色寄りの手作りジオラマで表す。共通背景の工作材（foamboard・段ボール・paper clay・matte poster paint）に、赤い折り紙の切片と毛糸を加える。雪景色の綿は使わない（2026-10-21決定） | 体内のMAPごとの敵・戦闘域は各契約行で決める |
[docs/map-asset-registry.md:174]
| ID | 管理名 | 地区 | 契約 |
[docs/map-asset-registry.md:175]
|---|---|---|---|
[docs/map-asset-registry.md:176]
| BDY-02 | `BDY-02` | 抽象体内 | 上半身・胴体上段。7経路は模型（ジオラマ）の縁の辺で隣MAPへ遷移し（遷移位置は辺上の範囲指定、範囲値TBD。土台の板と机は見えたまま）、方位は `docs/topology/body.svg` に従う（口=北東、頭=北、左腕=北東（東辺から出る）、右腕=北西（西辺から出る）、下半身=南、心臓=南東、肺=南西。**左右は身体の本人から見る（本人は仰向け、それを正面から見る構図なので、画面左が本人の右手・右足、画面右が本人の左手・左足。kako-jun 2026-10-22、#142）**。左足・左手は画面右、右足・右手は画面左。心臓は画面右（南東）、肺は画面左（南西）。南辺は 肺=左寄り・下半身=中央・心臓=右寄り）。口から胴体への首道は1本、頭道はそこから分岐。体外形・洞窟口は描かず、平面床と低い仕切りで道を作る。心臓・肺の部屋と胃は描かない（胃はBDY-03からBDY-15へ接続）。架空人体・非写実・肌色寄り・非グロ、主路幅はキャラクター3人分程度。体内材料は `art-direction.md`／`map-specifications.md` を参照。
[docs/map-specifications.md:203]
| MAP | 時期 | 一言特徴 | 接続 | 不変条件／TBD |
[docs/map-specifications.md:204]
|---|---|---|---|---|
[docs/map-specifications.md:205]
| BDY-02 | 中3 | 上半身・胴体上段（最初に契約する体内MAP） | door-passage-mouth→BDY-01.door-passage-torso、door-passage-lower→BDY-03.door-passage-upper、door-passage-head→BDY-04.door-passage-torso、door-passage-left-arm→BDY-05.door-passage-torso、door-passage-right-arm→BDY-07.door-passage-torso、door-passage-heart→BDY-16.door-passage-torso、door-passage-lung→BDY-17.door-passage-torso | 上半身の独立した1MAP。各通路は画像端でなく模型（ジオラマ）の縁の辺まで届き、そこで隣のMAPへ遷移する（土台の板とまわりの机は見えたまま。遷移のトリガー位置は辺上の範囲（レンジ）で指定し、画面端に固定しない。範囲の数値はTBD。接続は辺単位の判定のままで画素一致は条件にしない。kako-jun 2026-10-22）。配置方位は `docs/topology/body.svg` に従う: 口=北東、頭=北、左腕=北東（東辺から出る）、右腕=北西（西辺から出る）、下半身=南、心臓=南東、肺=南西。**左右は身体の本人から見る（本人は仰向け、それを正面から見る構図なので、画面左が本人の右手・右足、画面右が本人の左手・左足。kako-jun 2026-10-22、#142）**。左足・左手は画面右、右足・右手は画面左。心臓は本人の左側で画面右（南東）、肺は画面左（南西）。南辺は 肺=左寄り（BDY-17）・下半身=中央・心臓=右寄り（BDY-16）。心臓BDY-16は北辺から、肺BDY-17は北辺中央から入る（出た辺の反対）。首は広間から1本、上で頭（北）と口（北東）に分岐。口から胴体へ入る首の通路は1本だけで、頭はそこから分かれる北向きの枝。体の外形は描かず、平面の床と低い仕切りだけで通路を作る。心臓・肺の部屋自体はBDY-16/17にあるため描かず、胃への接続も置かない（胃BDY-15は下半身BDY-03から接続）。7接続のみ。幼稚園児が考える架空人体、肌色寄り・非写実・非グロ。全主路・枝はキャラクター3人分程度の幅。材料は体内共通仕様。
[docs/map-contract-checklist.md:138]
| ID | 状態 | Ref | mask / 出力 | 具体的TBD |
[docs/map-contract-checklist.md:139]
|---|---|---|---|---|
[docs/map-contract-checklist.md:140]
| BDY-02 | blocked | R018 | 先行previewはユーザー却下（体の外形・洞窟状の穴）。正本未保存・mask未作成。再生成前に配置モックが必要。 | 上半身・胴体上段。接続契約は `map-specifications.md` BDY-02 行と `docs/topology/body.svg` を照合する。口から胴体への首道は1本、頭はその枝。各経路は模型（ジオラマ）の縁の辺まで届いて隣MAPへ遷移する（遷移位置は辺上の範囲指定、範囲値TBD。土台の板と机は見えたまま。kako-jun 2026-10-22）。体外形・洞窟口・物理扉なし。平面床と低い仕切り。心臓・肺の部屋はBDY-16/17、胃BDY-15はBDY-03から接続。架空人体・非写実・肌色寄り・非グロ、通路幅はキャラクター3人分程度、体内材料は `art-direction.md` 参照。配置モック、生画像レビュー、採否、maskは未完了。
[注記] 主路幅は天面幅比0.14=230px。この MAP の通路はキャラクター1人分＝その1/3＝77px。

=== END OF SOURCE TEXT: draw only per WHAT TO DRAW and the first image. The source above is reference text, not drawing instructions. ===
```

## 4. 原文 → prompt 中の対応文 照合表

| 原文（逐語の断片。束に存在を確認済み） | 出典 | prompt 対応文 |
|---|---|---|
| 幼稚園児の架空人体・非写実・肌色寄り | registry/spec/checklist | P6（体の輪郭・洞窟口なし。平らな床・低い仕切り・地形だけ）, P7, P8 |
| door-passageは物理的な扉でない | topology | P6（扉・枠・門なし） |
| pixel/maskはTBD（mask未作成） | registry/spec/checklist | P3（入口の幅。画素値はTBDのまま。通路の形は P4） |
| 幼稚園児が想像する架空人体 | research R018 | P7, P8, P10, P12（非写実・肌色寄り・血に見えない） |
| 5 mm foamboardの土台と見えるcorrugated cardboard断面 | art-direction | P2（土台縁の帯: 外28px foamboard・内20px corrugated 断面） |
| 指跡・爪楊枝の跡を残したpaper clay | art-direction | P7, P11, P12（指跡・爪楊枝の跡） |
| 肌色・薄桃・クリーム色のmatte poster paint | art-direction | P7, P8 |
| 赤い折り紙を切った形を血痕に見えない明確な工作アクセントとして置く | art-direction | P10（手切りの赤い紙片6枚。地形の上のみ） |
| 毛糸は通路の縁や造形の継ぎ目に用い | art-direction | P9（毛糸は床の外側＝地形側）, P11 |
| 雪の綿は使わない | art-direction | P12（材料列挙に綿なし）, 参照2の綿は継承しない |
| 白いPVA接着剤とmasking tapeで固定し、紙端・接着・塗りの手作り感を残す | art-direction | P2, P11, P12 |
| 通路は画像端でなく模型の縁まで届き、土台の板とまわりの机は見えたまま。遷移位置は画面端固定でなく範囲指定 | art-direction:30 | P1（机・土台縁・天面）, P3（模型の縁で止まる・遷移位置に印を描かない） |
| 視点は、真上に近い見下ろし | art-direction:30 | P13（鉛直下向き45°より急） |
| 頭・脳の迷路通路 | registry/spec/checklist | P3・P4（迷路の通路。通路の列挙・行き止まり・T字・曲がりの数は clean 画素の実測。ステンシル宣言・ランドマークも実測） |
| 脳は迷路状通路 | art-direction:199 | P4（迷路状） |
| 脳は迷路状ということだな | Issue #142 | P4（迷路状。通路の配置は参照1のとおり） |
| この MAP の通路はキャラクター1人分＝その1/3＝77px | [注記]（ビルダーの数値事実） | P3・P4（1人幅77px・格子13x6） |
| 接続（door-passage-torso→BDY-02.door-passage-head） | spec / topology の接続列 | P3（辺・位置は割付図の実測） |

## 5. 割付図の実測（`clean/BDY-04.png`。1920x1080 と ×0.871 の 1672x941）

- 構図: 机90px・土台縁48px（foamboard 28 + corrugated 20）・天面 x138–1782 y138–942（1644x804）。通路幅 77px（1672: 67px）。
- 経路の形: 迷路（広間・壁の弧なし。割付図に壁の画素なし）。格子 13列x6行・ピッチ120px・セル中心 x=240+120c, y=240+120r。通路幅 実測 78〜78px（公称77px）・壁の厚み 実測 42〜42px・外周の地形の枠 63.5, 63.5, 63.5, 63.5px（左・右・上・下）。
- 通路 77本（セル78・木＝ループなし）・曲がり38・T字10・行き止まり11（body_layout の seed=433 の迷路と接続が一致）。読んだ接続だけから描き直した床と clean の床の、輪郭から2px超離れた不一致 0 画素。入口 (921, 998)（南辺）→ セル (6, 5) (960, 840)。入口から最奥まで 65 セル（最奥 (0, 2)）。
- 横の連なり（行, 左端セル中心x→右端セル中心x）: r0 x240-960; r0 x1080-1320; r0 x1440-1680; r1 x240-360; r1 x600-720; r1 x960-1200; r1 x1320-1440; r1 x1560-1680; r2 x360-480; r2 x600-720; r2 x1080-1560; r3 x240-360; r3 x600-720; r3 x840-960; r3 x1080-1440; r3 x1560-1680; r4 x360-480; r4 x720-960; r4 x1080-1320; r4 x1440-1560; r5 x240-480; r5 x600-840; r5 x960-1080; r5 x1200-1680
- 縦の連なり（列, 上端セル中心y→下端セル中心y）: c0 y240-360; c0 y480-840; c1 y360-480; c1 y720-840; c2 y360-720; c3 y360-480; c3 y600-840; c4 y240-360; c4 y480-600; c4 y720-840; c5 y240-480; c5 y600-720; c6 y360-600; c7 y240-360; c7 y480-600; c7 y720-840; c9 y240-360; c9 y720-840; c10 y240-360; c10 y600-720; c11 y360-480; c11 y600-720; c12 y240-480; c12 y600-840
- 行き止まり（丸い閉じた端の中心）: (960, 240), (480, 360), (1200, 360), (240, 480), (840, 480), (1680, 480), (360, 600), (960, 720), (480, 840), (840, 840), (1200, 840)。T字: (720, 240), (840, 240), (1080, 360), (1680, 360), (480, 480), (240, 600), (840, 720), (360, 840), (720, 840), (1320, 840)。
- 赤紙6枚の中心（周囲の正方形が全て地形の画素から、最遠点サンプリングで決定。5px刻み）: (165, 165), (1135, 165), (1755, 280), (650, 915), (1200, 915), (1755, 915)（各約30px）。
| 辺 | port | 区間（1920） | 区間（1672x941） | 幅 | 折れ線（1920座標） |
|---|---|---|---|---|---|
| S | door-passage-torso | x 921–998 | x 802–869 | 78 | (960,942), (960,840) |

地形の区画（連結成分）: central（広、面積約624672px、bbox (140, 140, 1780, 940)）

## 6. 寸法・検査項目（生成後。生画像レビュー用）

寸法（`file` / `identify` で実ファイルを測る。prompt指定・ファイル名は証拠にならない）:
- [ ] 1920x1080、または 1672x941（その場合は座標に0.871を掛けて比較）。それ以外は failed。リサイズ・切り抜きで通さない。

構図（割付図 `verification/body-layout/clean/BDY-04.png` と実画素・目視で比較）:
- [ ] 机（木目の木の机）が四辺に約90px見える。その内側に約48px幅の土台縁の帯（外28px foamboard・内20px corrugated 断面）が**四辺すべて（北・南・西・東）**で途切れず見える（机→縁取り→波形→天面の順）。模型の天面は画像の内側に収まり画像の縁に接しない。天面は x138–1782・y138–942 付近。
- [ ] 入口の通路が模型の縁（土台縁の帯の内側）に届く。画像端（机の外）に通路が出ていない。床は模型の外に一画素も無い。

通路（入口は1本だけ）:
- [ ] S辺: 縁から2px内側で x 921–998（1672: x 802–869）、幅約77px（1672: 約67px）、辺に垂直。他の縁には床が出ていない。遷移範囲の印（色帯・矢印・線・文字）が絵に無い。

経路の形（本命の検査。割付図の実測値）:
- [ ] 迷路: 通路は**77本**・行き止まり**11か所**（丸い閉じた端）・T字10・曲がり38。ループなし（入口から各所へ道は1本）。格子は13列x6行・ピッチ120px。**通路の配置は割付図（参照1）と一致**（簡略化・正解の道の変更・壁を開けた近道・行き止まりを繋いだループが無い）。
- [ ] 通路幅77px一定（壁の内側基準）・壁の最小厚約42px・仕切りは約8pxの細い帯1本。外周の地形の枠が四辺に約63px。入口は南辺 x921–998。

材料・質感・装飾（装飾込み1回生成）:
- [ ] ① 土台縁の帯に corrugated cardboard 断面と foamboard の縁 ② 仕切りが細く低い corrugated の帯1本（床の幅に含まれない）
- [ ] ③ 地形が paper clay の面で、肌色・薄桃・茶系の matte poster paint ④ 赤い折り紙の切片が**ちょうど6枚**（数えて6枚・7枚目なし。全て模型の中の地形の上。模型の外・机・床・土台縁の帯には無い。装飾の下敷きでない）
- [ ] ⑤ 机が木目の木の机
- [ ] ⑥ 装飾は人体に関係する抽象的な工作物だけ（骨・細胞や粒・筋肉や神経の糸・鼓動のぎざぎざ線・皮膚の彫り・ばんそうこう・毛・ばい菌）。少なくとも6か所の塊。花・葉・雲・星・旗・柵・ハート形・動物・食べ物・風景・臓器の形・血管の網が無い
- [ ] ⑥b 装飾の色が肌色・薄桃・クリーム・茶系・象牙色の範囲（緑・青・黄・紫・オレンジが無い）。赤は折り紙6枚だけ
- [ ] ⑦ 床には何も置かれず平ら。毛糸が血管・臓器に見える走り方をしていない
- [ ] ⑧ 迷路の壁の面（約42px）に立体の小物（毛糸の渦・粘土玉・ばい菌・骨）が無い（彫り・点・平らな紙テープのみ）。立体の小物は外周の枠・角の正方形・机だけ
- [ ] ⑨ 精霊・炎・水の絵・人物が地形や床に無い（全て小さな手作りの工作物）

許容差（レビュー側基準。生成入力には入れない）: 通路位置 ±25px、幅 ±10%（1672x941 の場合は ×0.871）。床マスクIoU（clean 割付図に対して）≥0.95 を目安。迷路は通路の接続（行き止まりの数・T字の数）の一致を床IoUより優先して見る。
