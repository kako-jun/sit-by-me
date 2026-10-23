# BDY-16（心臓・分岐室）装飾込み1回生成の完全 imagegen prompt（`build_body_prompt.py` 自動生成。Issue #142）

> 履歴: 2026-10-22 時点の生成記録。2026-10-23 に TRM-01 は TRM-03 に統合（園庭=TRM-03の右の区画、起点は TRM-03.event-kiss）。現行の正本は docs/map-topology.md と docs/production/body-masks/BDY-01-links.json。本文中の TRM-01・行番号は当時のまま（送信済みの逐語記録）。

状態: **機械生成・独立レビュー未実施・画像未生成**。`.claude/skills/sit-field-background/SKILL.md` のゲート（台帳原文・材料固定宣言・一意解釈・寸法）に沿う。型は採用済み BDY-02（v2 の構図・原文束、v3 の装飾語彙）。画像は生成しない。

## 0. 来歴・警告・TBD

来歴:
- 生成器: `.claude/skills/sit-field-background/tools/build_body_prompt.py`（使い方: `build_body_prompt.py BDY-16 --out DIR`）。入力は docs の対象行（逐語）・Issue #142・`verification/body-layout/clean/BDY-16.png` の画素実測・`body_layout.py` の折れ線。
- 型: `docs/production/20261022-bdy02-adoption.md` と `20261022-bdy02-adoption-prompts/`（v2-prompt-full.txt=構図・原文束、v3-edit-prompt.txt=装飾語彙）。
- 入力 sha256（参照2枚。様式参照画像は幾何を崩す疑いがあるので使わない）: clean `86aff09e689136d1d0e5525061cf8f3ea2fc9a392fefa55fd1bc58976708fd68` / 材料見本 `764b7ae7f1aa0ff19bd8e79a8724fc8b975c4d5465440fb539f5566f52828b45`
- 送信文 sha256: `24a1b26e19f96148f1d5a1c9c45df17f27edb46390db8da5ef66e97b33a33d57`
- 送信文: `BDY-16-prompt-send.txt`（wrapper + 本文。この .md の §3.1 と §3.2 を連結したもの。§3.2 は §1 の原文束を SOURCE TEXT として含む。原文束の外に内部メモ・TBD・仮案を含まない）。

警告・TBD（ビルダーが検出）:
- 決定済み: 脳=迷路・胃=分岐なしJ字の1袋・心臓=2x2の丸い4部屋の環・肺=案A（外周の環・行き止まりなし）。kako-jun 決定・モック承認（2026-10-22。Issue #142）。docs の『単純な分岐室』『分岐室』は逐語の原文として残る。この MAP の形は P4 が肯定形で明示している（原文束の外の自作部分）。
- 座標・半径・通路の接続は clean 画素の実測（body_layout の SPECS と照合済み）。別コードの再測定: verification/body-layout/remeasure_body_rooms.py [BDY-xx]（prompts/BDY-xx-prompt-send.txt の数値を clean 画素と照合）。
- 装飾込み1回生成（onepass）: 参照は2枚（clean 割付図・材料見本）。様式参照画像は使わない。壁・仕切りは細い corrugated の帯1本（迷路 約8px・他 約12px）＋毛糸1本で、床の幅は壁の内側基準で守る。
- 赤紙6枚は clean の地形で周囲の正方形が全て地形の点から決定的に選び、座標を本文に固定した（BDY-02 の方式）。
- 部屋名（右心房など）は原文束にだけ現れ、絵には描かない。本文は部屋を丸い床と呼び、臓器の輪郭を描かせない。
- 生成前の独立レビューは未実施（SKILL: 生成可には独立レビュー通過が必要）。

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
[Issue #142 決定コメント（時系列順。各コメントの見出しと、BDY-16 に関わる決定の行だけを逐語で抜粋。相互に食い違う場合は、より後のコメントが優先）]
## kako-jun 決定・指摘（2026-10-22、モック一覧を見て）
4. **脳・心臓・肺など**（「肺や心臓などは、医学的に右心室など4つに分かれているとかを抽象的に表現すればいい。脳は迷路状ということだな」）→ 脳=迷路状。心臓=解剖学の4つの部屋（右心房・右心室・左心房・左心室）を抽象的な4つの部屋と通路で表す。肺・胃も同様に実際の区分を抽象化（分け方の詳細は kako-jun が示した「など」までなので仮案を出してモックで確認）。血・写実的な臓器は描かない（既存方針）。

## kako-jun 決定（2026-10-22）: 左右は身体の本人から見る
「左右の考え方は、身体の本人からみてにして。本人は仰向けに寝ている。それを正面から見ている構図だ。だから画面左側は右手だ」
- 左右は**本人から見た**左右。本人は仰向けで、画面（正面から見る構図）の左側が本人の右手・右足、右側が本人の左手・左足。
- 部屋名（右心房＝画面左、右肺3葉＝画面左）は現行の置き方で本決定と一致。

## kako-jun 決定（2026-10-22、モック一覧と接続表を見て）
「心臓は自然にすればいい。肺は人間のがうずまきでないなら行き止まりなしでいいのでは。首はこれでいい。足の角度は太もも部分が１マップ内に短すぎてもったいないので曲がってる感じしてはどうか」
1. 心臓: 自然（本人の左側＝画面右）。BDY-02 の南辺は 肺=左寄り・下半身=中央・心臓=右寄り で確定。
[docs/map-topology.md:118]
以下は接続の向きを一意にする正本である。`→` の両側は必ず反対の画像辺とし、`door` は画像端でなく室内・階層遷移である。`event` は一方向の物語イベント、`oneway` は一方向の通常移動。`door-passage-*` は体内の抽象通路名で物理的な扉ではない。`pending` は旧仮説のID追跡だけの行で、隣接・通行路・生成契約ではない。`§3.1` 以降の旧試作時の図・発注文は履歴説明であり、ここにない辺指定を新規プロンプト、画像生成、マスクに使ってはならない。
[docs/map-asset-registry.md:91]
| ID | 画像 | 地区 | 未決のため必要な個別契約 |
[docs/map-asset-registry.md:92]
|---|---|---|---|
[docs/map-asset-registry.md:118]
| BDY-16 | `BDY-16` | 抽象体内 | 心臓・分岐室。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。丸い4部屋（右心房=画面左上・右心室=左下・左心房=右上・左心室=右下。左右は本人から見る）を四角い環の通路でつなぐ。入口は北辺。形の詳細（座標・格子）は verification/body-layout の割付図が正本。pixel/maskはTBD（mask未作成）。 |
[docs/map-specifications.md:117]
| MAP | 時期 | 一言特徴 | 方位・主路・通行条件 | 暫定固定 |
[docs/map-specifications.md:118]
|---|---|---|---|---|
[docs/map-specifications.md:126]
| BDY-16 | 中3 | 心臓・分岐室 | door-passage-torso→BDY-02.door-passage-heart | 上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。丸い4部屋（右心房=画面左上・右心室=左下・左心房=右上・左心室=右下。左右は本人から見る）を四角い環の通路でつなぐ。入口は北辺。形の詳細（座標・格子）は verification/body-layout の割付図が正本。pixel/maskはTBD（mask未作成）。 |
[docs/map-contract-checklist.md:11]
| ID | 状態 | Ref | mask / 出力 | 具体的TBD |
[docs/map-contract-checklist.md:12]
|---|---|---|---|---|
[docs/map-contract-checklist.md:82]
| BDY-16 | blocked | R018 | 未生成・mask未作成 | 心臓・分岐室。door-passage-torso→BDY-02.door-passage-heart。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。丸い4部屋（右心房=画面左上・右心室=左下・左心房=右上・左心室=右下。左右は本人から見る）を四角い環の通路でつなぐ。入口は北辺。形の詳細（座標・格子）は verification/body-layout の割付図が正本。pixel/maskはTBD（mask未作成）。 |
[docs/map-topology.md:260]
| BDY-02.door-passage-heart | BDY-16.door-passage-torso | door | 架空人体の抽象通路。door-passageは物理的な扉でない。上半身/下半身2枚・手各2枚・足各3枚の連続一本道 |
[docs/map-topology.md:686]
## 体内の現行空間設計（#74・追加ボリューム決定）
[docs/map-topology.md:688]
TRM-01園庭→BDY-01口は一方向の物語イベント。病院・海外からの体内経路や恒常的な徒歩口ではない。胴体は縦2MAP、上半身BDY-02→下半身BDY-03。頭BDY-04は上半身の上の迷路状通路。左右の手は上半身から斜め上へ伸び、左BDY-05→BDY-06（画面右上・上半身の東辺から出て、BDY-05の西辺から入る）／右BDY-07→BDY-08（画面左上・上半身の西辺から出て、BDY-07の東辺から入る）の各2MAPの一本道。左右の足は下半身から斜め下へ伸び、左BDY-09→BDY-10→BDY-11（画面右下・下半身の東辺から出る）／右BDY-12→BDY-13→BDY-14（画面左下・下半身の西辺から出る）の各3MAPの一本道。**左右は身体の本人から見る（本人は仰向け、それを正面から見る構図。画面左が本人の右手・右足、画面右が本人の左手・左足。心臓は本人の左側＝画面右、肺は画面左。kako-jun 2026-10-22、#142）。**手足末端は閉じ、手足相互の連絡や迂回路を足さない。方向は分岐の方位であり、各手足MAPには縦方向の通路ボリュームを持たせる。
[docs/map-topology.md:690]
BDY-15胃・BDY-16心臓・BDY-17肺はそれぞれ独立したMAPで、胴体からの単純な分岐室。医学的解剖や写実的臓器ではなく、現実離れした幼稚園児の想像する架空人体の抽象概念、肌色寄りでよい。胃の盾役・エラー細胞と、心臓での水の精霊・火による復活という既存の物語を保持。BDY-02の作画契約: 口→上半身→下半身を中央主路でつなぎ、頭・左右の腕・心臓・肺を枝にする。各経路は模型（ジオラマ）の縁の辺まで届いて隣MAPへ遷移し（遷移位置は辺上の範囲指定、範囲値TBD。土台の板とまわりの机は見えたまま。接続は辺単位の判定のまま。kako-jun 2026-10-22）、洞窟状の穴や物理的な扉は描かない。体の外形を描かず、平面床と低い仕切りで道を作る。配置方位は `docs/topology/body.svg` のBDY-02接続線に従う（心臓=南東・画面右、肺=南西・画面左。南辺は肺=左寄り・下半身=中央・心臓=右寄り。BDY-16は北辺から、BDY-17は北辺中央から入る。首は広間から1本、上で頭（北）と口（北東）に分岐）。心臓・肺の部屋はBDY-02内に描かず、胃はBDY-03からBDY-15へ接続する。空間接続から新たな攻略順・肺ボス・全枝任意という条件を決めない。脳BDY-04は迷路（通路幅はキャラクター1人分で約77px、入口は南辺中央1本、行き止まりの迷路で出口なし）。胃BDY-15は分岐なしJ字の1袋（入口は西辺230px→ドーム→胃体最大460px→幽門130pxで丸く閉じる）。心臓BDY-16は丸い4部屋（右心房=画面左上・右心室=左下・左心房=右上・左心室=右下）を四角い環の通路でつなぐ（入口は北辺）。肺BDY-17は人間の肺が渦巻きでないため行き止まりなし（外周の環に右肺3葉=画面左・左肺2葉=画面右の丸い5部屋、入口は北辺中央、通路幅は人間1人分）。形の詳細（座標・格子）は検証の割付図（verification/body-layout）が正本。pixel/mask・発火条件はTBD。
[docs/map-topology.md:692]
119案の単一胴体・各手足1MAPは追加口述により失効。全130MAP（#87/#89でKRB-02・NTB-07、#87でデパート2階KRB-03・4階KRB-05を追加）、体内17MAP。工程Aの体内正本をコミット・プッシュした後、工程Bの全体図・アトラス・全15エリア図も更新済み。
[docs/art-direction.md:195]
## #74 体内の最新空間・色の契約
[docs/art-direction.md:197]
**左右は身体の本人から見る（本人は仰向けに寝ていて、それを正面から見る構図。画面左側が本人の右手・右足、画面右側が本人の左手・左足。心臓は本人の左側＝画面右、肺は画面左。kako-jun 2026-10-22、#142）。**
[docs/art-direction.md:199]
体内は医学的な身体の再現でなく、現実離れした幼稚園児の想像する架空人体の抽象的概念。肌色寄りでよく、血や写実的な臓器・内壁を描かず、グロくしない。胴体は縦2MAPの上半身/下半身、手各2MAP・足各3MAPの縦通路ボリューム。頭は上、手は斜め上、足は斜め下。脳は迷路状通路、心臓・肺は単純な分岐室。背景共通の手作りジオラマに合わせ、5 mm foamboardの土台と見えるcorrugated cardboard断面、指跡・爪楊枝の跡を残したpaper clayの丸い地形を使う。肌色・薄桃・クリーム色のmatte poster paintで着色し、赤い折り紙を切った形を血痕に見えない明確な工作アクセントとして置く。毛糸は通路の縁や造形の継ぎ目に用い、雪の綿は使わない。白いPVA接着剤とmasking tapeで固定し、紙端・接着・塗りの手作り感を残す。旧『紙粘土・セロファンだけ』『口から手足が直結』という解釈を新規生成の固定根拠にしない（材料決定は2026-10-21 kako-junとの相談）。
[docs/art-direction.md:30]
- 背景はタイルを無限に継ぎ足さない。場所ごとに、全景・広い道路・狭い道・接続画を同じカメラ、光、反復物で一度に作る。視点は、真上に近い見下ろし（2026-10-14 変更。以前の「高めの斜め見下ろし（約45°）」は撤回）。フィールドは固定の一枚絵で、スクロールしない。絵の端（模型の縁の辺）で次の絵に切り替わる（2026-10-14）。通路は画像端でなく模型の縁まで届き、土台の板とまわりの机は見えたまま。遷移位置は画面端固定でなく範囲指定（2026-10-22 kako-jun）。
[docs/map-reference-research.md:24]
| R018 | BDY-01〜BDY-17 | `docs/art-direction.md` と `docs/assets-policy.md`／プロジェクト正本 | 人体の写実・流血・臓器表現を避け、幼稚園児が想像する架空人体を肌色寄りの手作りジオラマで表す。共通背景の工作材（foamboard・段ボール・paper clay・matte poster paint）に、赤い折り紙の切片と毛糸を加える。雪景色の綿は使わない（2026-10-21決定） | 体内のMAPごとの敵・戦闘域は各契約行で決める |
[docs/map-reference-research.md:57]
| BDY-01〜BDY-17 | 体内の抽象ダンジョン | 実在写真を参照しない。安全表現・接続・ボス配置の視覚契約をMAP別に書くまで生成不可 |
[docs/map-reference-research.md:86]
## #74 体内の最新根拠
[docs/map-reference-research.md:88]
ユーザー原文に基づく空間: 胴体は縦2MAP（上半身・下半身）、手は各2MAP、足は各3MAPの通路。頭上・手左右斜め上・足左右斜め下、脳は迷路、心臓・肺は単純な分岐室。非写実・現実離れした幼稚園児の想像する架空人体、肌色寄り。医学的資料から形状を推測しない。BDY-02上半身/BDY-03下半身への各部接続と肺BDY-17は制作上のID配置。胃を下半身、心臓と肺を上半身から分けることは抽象的なゲーム配置で、解剖の事実ではない。
[docs/decisions.md:341]
体内入口はTRM-01園庭→BDY-01口の物語イベント。胴体は縦2MAPの上半身BDY-02・下半身BDY-03、左右手各2MAP、左右足各3MAP。手足は一本道、頭は上の迷路通路、胃・心臓・肺は単純な分岐室。肌色寄りの幼稚園児の想像する架空人体で医学的写実はしない。新規BDY-02〜BDY-03・BDY-05・BDY-07・BDY-09〜BDY-10・BDY-12〜BDY-13・BDY-17を追加して全126MAP。既存の胃・心臓の物語条件を保持。工程Aをコミット・プッシュしてから、工程Bで全体図と残りの全MAP接続図を作る。
[docs/map-topology.md:46]
| 体内 | 中3 | ダンジョン・既存の部位イベント | 17MAP | 0 | 上半身/下半身各1、手各2、足各3、口・頭・胃・心臓・肺 | 肌色寄りの幼稚園児の架空人体。非写実 | 頭は上、手は斜め上、足は斜め下の一本道 | 脳は迷路、心臓・肺は分岐室 |
[docs/map-topology.md:618]
| 体内 | 中3 | ダンジョン・既存の部位イベント | 17MAP | 0 | 上半身/下半身各1、手各2、足各3、口・頭・胃・心臓・肺 | 肌色寄りの幼稚園児の架空人体。非写実 | 頭は上、手は斜め上、足は斜め下の一本道 | 脳は迷路、心臓・肺は分岐室 |
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
[注記] 通路幅は天面幅比0.14=230px。
```

## 2. 参照一覧（実画像として入力する順。参照は2枚）

| # | パス | 用途 | 継承禁止事項 |
|---|---|---|---|
| 1 | `verification/body-layout/clean/BDY-16.png`（1920x1080、4色のベタ。灰=机、茶=土台縁の帯、くすんだ桃茶=天面の地形、クリーム=歩ける床。文字・注記・遷移範囲の着色なし。画像編集の入力＝塗り直しの土台） | 幾何のみ（机・土台縁・天面の入れ子、通路の本数・辺・位置・幅・曲がり・端） | 色を塗らせない（5色ベタ・硬い直線エッジは継承しない）。文字・遷移範囲の印を残さない |
| 2 | `verification/body-layout/BDY-material-swatch-corrugated-edge.png`（1540x52。寺町の採用画像の下端の帯を無加工で切り出した材料見本） | 材料の感じのみ: corrugated cardboard 断面・masking tape・ちぎれた紙端 | 帯上端の白い綿の繊維・茶色の色味は継承しない。雪を持ち込まない |
添付順 = 1, 2（wrapper の『Two images』の列挙と本文 REFERENCE の FIRST/SECOND が一致）。

## 3. 送信予定の完全 prompt

### 3.1 前置き指示（wrapper）

```text
Invoke the $imagegen skill and use the built-in image_gen tool at the HIGHEST quality (quality: high), keeping the editing source's size 1920x1080 (16:9), to repaint the image as described in the prompt below. This is an IMAGE EDIT: use the image_gen tool in image-edit mode on the first attached image. Two images are attached, in this order: (1) the editing source (a flat four-colour layout diagram with no text; keep its geometry exactly, and use the meaning of its colours as described in the prompt); (2) a thin close-up strip of the edge of a hand-made cardboard miniature, for materials and craft feel only (as described in the prompt). Call image_gen EXACTLY ONCE: no retries, no regeneration, no multiple candidates, even if you think the result is imperfect. Then save the REAL generated PNG (decode the tool result) into the current workspace at out/bdy16-op-v1.png. You are STRICTLY FORBIDDEN from fabricating/drawing the image with magick/ImageMagick/PIL/Pillow/numpy/SVG/canvas/any code; only the image_gen tool. If the image_gen tool is genuinely not in your toolset, do NOT fabricate - output exactly: IMAGE_GEN_TOOL_UNAVAILABLE. Do not resize or crop the result. Do not use any files in ~/.codex/generated_images/ made by other calls; only the image generated in this call. Report the saved file path.
Output a 16:9 landscape image. Keep the size of the editing source (1920x1080); if not possible, 1672x941. Do NOT use 3:2 or 1536x1024. Do not mirror or flip the image; keep the direction of the editing source.
```

### 3.2 本文

```text
Generate ONE image: the final field background for map BDY-16 (four round rooms joined in a square ring, of the imaginary human body inside which the story travels). Do not generate any other map.

=== WHAT TO DRAW (positive description; sentence numbers P1.. are referenced below) ===
P1. COMPOSITION. The whole picture is a hand-made tabletop miniature seen from almost straight above: a model standing on a desk. From the outside in on ALL FOUR sides (north, south, west and east alike): (a) the desk surface, a warm natural wooden tabletop with visible wood grain, a 90 px margin on all four sides of the frame, mostly clear wood (at most a few small craft leftovers lie on it, well clear of the model); (b) the model's base, seen from above as a border band 48 px wide that frames the top surface all the way around, unbroken (no side face of the model is visible); (c) inside the band, the top surface of the model, which is the map. Frame coordinates (1920x1080): the base band's outer edge is the rectangle x 90 to 1830, y 90 to 990; the model's top surface is the rectangle x 138 to 1782, y 138 to 942 (1644 x 804 px). (In the 1672x941 frame these are: band outer edge x 78 to 1594, y 78 to 863; top surface x 120 to 1552, y 120 to 821.) On every one of the four sides of the picture, going inward from the picture's edge, you see in this order at full width: the wooden desk (90 px), then the cream foamboard rim (28 px), then the brown corrugated cardboard cross-section (20 px), then the terrain. The model's top surface lies wholly inside the picture and touches none of its edges; the north and south sides show the desk, the rim and the corrugated band exactly as the west and east sides do. Nothing is drawn outside the model except the wooden desk and its few craft leftovers: no wall, no room, no sky, no horizon, no people. The model is a miniature, so the whole picture is a model; the picture never reads as a photograph of a real place.
P2. THE BASE BAND. Seen from above it is a framing border around the top surface. Its outer 28 px (x 90 to 118 along the left side, and likewise on the other sides) is the rim of a 5 mm foamboard slab (smooth pale white-cream paper-faced foam core, with the paper skin and the foam core visible along the rim). Its inner 20 px (x 118 to 138 on the left, and likewise on the other sides) is the exposed cross-section of corrugated cardboard (the wavy flute layer between two flat liners, brown), glued around the foamboard's top edge with masking tape and white PVA glue, with ragged hand-cut paper edges. The band runs unbroken along all four sides, north and south included, with both the foamboard rim and the corrugated layer clearly visible on each side. It is not interrupted where the passage reaches the model's edge. A few extra strips of masking tape and small PVA drips may lie on the band, never hiding the corrugated layer over any long stretch.
P3. THE ENTRANCE AND THE MODEL'S EDGE. The model's top surface is made of thin flat paper-clay surfaces. ONE single flat floor band, 230 px wide measured across the band (0.14 of the model's width of 1644 px, which is 200 px in the 1672x941 frame; a stand-in for three characters side by side; no character is drawn), runs straight inward from the model's edge (exactly perpendicular to the edge, with no bend) into the upper-left room of P4, and it reaches the model's edge and stops flush against the inner edge of the corrugated band of P2: the floor band ends where the model ends, at the band, and never continues onto the band, the desk or the frame edge (it leads on to the next map across the model's edge; the character stands anywhere within a stretch of the edge to cross over, so nothing marks a crossing point). No marker, coloured zone, arrow, line or label of any kind is drawn at the edge. Position where the band meets the model's edge, in the 1920x1080 frame, measured from the layout diagram (first image):
  - North edge (top, y 138), 1 passage: the entrance passage (leading back toward the upper torso) at x 450 to 680 (in 1672x941: x 392 to 592).
  Along every other stretch of the model's four edges, the edge is solid raised paper-clay terrain meeting the corrugated band: the entrance band is the only floor that reaches the model's edge, 1 in all.
P4. FOUR ROUND ROOMS AND A SQUARE RING OF PASSAGES. The whole floor is ONE connected shape: four round rooms joined by four straight passages into a rectangular ring, entered by one passage from the north edge. This map's rooms are plain round floors, one at each corner of the ring (all values measured from the first image, 1920x1080 frame; 1672x941 values alongside). THE FOUR ROOMS: each is a perfectly round floor of radius 160 px (320 px across), wider than any passage; the upper-left room is centred at (565, 328) (in 1672x941: (492, 286)), the lower-left room at (565, 752) (in 1672x941: (492, 655)), the upper-right room at (1355, 328) (in 1672x941: (1180, 286)) and the lower-right room at (1355, 752) (in 1672x941: (1180, 655)). THE RING: the four rooms are joined by four straight passages, each 230 px wide (in 1672x941: about 200 px) with a flat floor and straight, parallel edges: the top passage between the two upper rooms runs along y 213 to 443 (centre line y 328; in 1672x941: y 186 to 386), the bottom passage between the two lower rooms along y 637 to 867 (centre line y 752; in 1672x941: y 555 to 755), the left passage between the two left rooms along x 450 to 680 (centre line x 565; in 1672x941: x 392 to 592), and the right passage between the two right rooms along x 1240 to 1470 (centre line x 1355; in 1672x941: x 1080 to 1280). Each passage meets its two rooms on the line through their centres, so the ring is a rectangle whose four corners are the four rooms, and each round room bulges out beyond the passage on both sides. THE ISLAND: inside the ring lies one solid rectangle of terrain (not floor), x 681 to 1239 and y 444 to 636 (559 x 193 px; in 1672x941: x 593 to 1079, y 387 to 554). THE ENTRANCE: the entrance band (x 450 to 680, the same x range as the left passage) comes straight down from the north edge into the top of the upper-left room, in one straight vertical line with that room and the left passage. The ring has exactly four rooms, four passages and one entrance, no dead end and no other opening; the rooms are story role names only, and each is drawn as a plain round floor with nothing in it and no outline of any organ.
P5. NOTHING ELSE ON THE FLOOR. Only the entrance, the rooms, the passages, the bends, the junctions and the closed ends described in P3 and P4 are drawn: the floor has no other branch, room, loop, crossing or detour than the ones listed there, and no connection to any other map except through the one model's edge named in P3. The floor is empty: no body parts, no faces, no object lies on it. The ledger word "branch room" in the source text names this map's own four rooms; they are joined only by the ring of four passages, and no side room or branch leaves the ring.
P6. PARTITIONS. Along the floor edges (the edges of the passages and of the rooms), on the terrain side of the floor outline, run LOW PARTITIONS: narrow low ridges (seen from above as narrow raised borders) made of ONE narrow, low band of corrugated cardboard each (no stacking), with paper clay smoothed over its top, which make the passages and the rooms. Each partition is only about 12 px wide (in 1672x941: about 10 px) and stands entirely on the terrain side of the floor outline, on the boundary where the terrain face meets the floor; no floor colour appears outside a partition. The clear cream floor between the inner faces of the partitions keeps exactly the width of the cream area of the first image, 230 px for the passages (in 1672x941: about 200 px), and the full round of each room; the thickness of a partition is never counted inside the floor width and never eats into it. Outside each partition, on the terrain side along its foot, runs ONE thin edging strand of yarn (pale pink). There are no doors, door frames or gates, no cave mouths, no round holes or tunnel mouths, no outline of any body or organ: the top of the model is only flat floor, low partitions, yarn edging and decorated terrain.
P7. THE TERRAIN. The terrain around the rooms and passages is a thin, flat sheet of paper clay, painted face by face in matte poster paint, the terrain cream leaning (pale cream and light peach faces), with a few pale pink faces mixed in, laid on with a flat brush (brush streaks and uneven coats visible), a different tone for each face. The terrain is the place for the handwork decoration of P9, which stays inside the same warm range of colours (see P8). It has no thick mounded layers, no stacked flesh-like bands, no striations and no fleshy cross-sections. The floor divides the terrain into 2 wide regions (the terrain outside the ring and the island inside it).
P8. COLORS: passage floors: matte poster paint in cream and pale peach, the same range everywhere. Terrain: matte poster paint, cream leaning (pale cream and light peach faces), with a few pale pink faces mixed in, one tone per face. COLOURS OF THE DECORATION: every decoration item is coloured only within skin tone, pale pink, cream, ivory and brown shades (yarn: light to deep shades of cream, pale pink and skin tone; beads, buttons, discs and clay balls: cream, pale pink, skin tone or light brown; toothpicks: natural wood). The red of the six origami pieces of P10 is the only other colour in the model, and the desk is natural wood. So the whole model reads as one warm family of skin, pale pink, cream and brown. The edging yarn is pale pink. The desk is warm natural wood (dark chestnut grain with long straight lines). Partitions: corrugated cardboard strips with paper clay on top, in brown and skin tones.
P9. DECORATION (hand-made craft ornament about the human body, placed on the terrain outside the rooms and the passages (the terrain around the ring or the pouch and, where there is one, on the island inside the ring), along the foot of the partitions, on the edge of the base band and on the desk only; nothing is placed inside any room or passage). The decoration is made ONLY of small abstract handmade items that belong to the human body, in the kinds listed below as the leading and the supporting motifs; no other kind of ornament is used. This map has its own decoration theme, different from the neighbouring maps. The leading motifs are: MAIN motif (pulse): pulse lines: wool yarn in cream or pale pink glued down as jagged zigzag lines of yarn, in short separate lines; SECOND motif (bone): small bones made by hand: a short toothpick (or a thin roll of paper clay) with a small ball of paper clay at each end, like a tiny cartoon bone, in cream and ivory, lying singly, crossed in pairs or in little piles; THIRD motif (cell): cells and grains: round balls of paper clay with fingerprints, beads, buttons and small flat discs in cream, pale pink and skin tone, glued singly, in pairs, in lines or in small heaps. Only as small supporting touches, never as the main look: a few small tufts of thread hair; a few short yarn bundles and small coils; a few small patches of carved fingerprint swirls and pore dots. ARRANGEMENT: WALL BAND: the decoration forms a continuous belt that follows the foot of the partitions and the inner side of the base band, the middle of each terrain region staying calmer. EDGE COLOURS: the edging strand of yarn at the foot of the partitions is pale pink; the masking tape and PVA of the base band are white masking tape and white PVA. The colours of the decoration are given in P8. THE DESK: a warm wooden tabletop, dark chestnut grain with long straight lines; around the model lie a short loop of yarn and one spare bead along the left desk margin (only these, small and few; nothing on the desk covers or touches the base band over a long stretch). DENSITY at kindergarten-craft level, in proportion to the area of the terrain: each of the 2 wide regions of terrain shows 3 to 5 kinds of small items and patterns, the decoration forms at least 6 groups over the terrain (arranged as the ARRANGEMENT says), so the picture feels rich and handmade. Yarn and threads are short separate strands, swirls and edging: they never run as a net like blood vessels or veins and never look like an organ.
P10. RED ORIGAMI: EXACTLY SIX (6) hand-cut red paper pieces with uneven edges (cut with scissors from red origami paper, flat on the surface, glued with PVA), no more and no fewer: count them, six, with no seventh and no spare piece anywhere. Exactly six red origami pieces, each about 45 px across (in 1672x941: about 39 px), centred at about: (180, 180) (in 1672x941: (157, 157)); (1645, 180) (in 1672x941: (1433, 157)); (985, 495) (in 1672x941: (858, 431)); (1520, 565) (in 1672x941: (1324, 492)); (365, 900) (in 1672x941: (318, 784)); (1740, 900) (in 1672x941: (1515, 784)) (six in total), all on terrain faces inside the model (x 138 to 1782, y 138 to 942; in 1672x941: x 120 to 1552, y 120 to 821), none on any floor, partition, rim or desk, none anywhere outside the model. Their outlines are irregular and unequal, not drawn as any particular symbol; they are clean paper cut-outs, never blood stains or liquid. They are the only red objects in the picture. Nothing of P9 is laid over them: they are not a base for ornament.
P11. THE FLOOR STAYS EMPTY. Nothing of P9 lies on the cream floor, crosses into it or touches it: the passages and the rooms stay perfectly flat, clean and empty, nothing is placed where the characters walk, and the width of the passages, the shape of the rooms and the flatness of the floor are exact. The surfaces of the model are flat floors, partitions and decorated terrain only. The floor and terrain contain no figures, spirits, flames or water pictures; every object is a small hand-made craft piece in the colours listed.
P12. MATERIALS (every material must be identifiable at full size): base: 5 mm foamboard with the corrugated cardboard cross-section band described in P2; terrain surface: paper clay modelled by hand; partitions: one low corrugated cardboard strip each under smoothed paper clay; floors and terrain: matte poster paint applied with a flat brush; the joint of the band: masking tape; decoration (handmade items about the human body): wool yarn, thread, paper-clay balls, buttons, beads, toothpicks, skin-coloured tape, white PVA glue; accents: 6 pieces of red origami paper cut by hand with scissors; desk: wooden tabletop with visible wood grain. Hand-made roughness: ragged hand-cut paper edges, paint unevenness, visible material seams. Parts look like paper and clay (matte, soft edges), not like real skin, flesh, organs or stone. It reads as a crude hand-made miniature in which the whole picture is the model, and not as a photograph of a real place.
P13. CAMERA: the camera looks down steeper than 45 degrees from horizontal, as close to straight down as possible, never lower than 45 degrees from horizontal. North is the top of the image. Flat evenly lit tabletop light. The picture has no sky, no horizon, no vanishing point, no people, no characters, no readable text, no letters, no numbers, no logos.
P14. DIMENSIONS: request 1920x1080 (16:9). If the tool cannot return it, 1672x941 is acceptable (every coordinate above then scales by 0.871; the 1672x941 values are given alongside). Any other size is a failure; never resize or crop to pass. Measure the real output file.

=== REFERENCE (two attached images, in this order) ===
FIRST IMAGE: a flat layout diagram with four plain flat colours and no text. Its colours mean: grey = the desk; ochre-brown band = the base band's edge (P1, P2); dusty rose-brown inside the band = the model's top terrain (P7); light cream = the walkable floor (P3, P4). Copy ONLY the geometry exactly: the nesting of desk, base band (foamboard rim, then corrugated layer) and model top on all four sides, the single entrance at the north edge and its position and width, the four round rooms, the four passages that join them in a rectangular ring, and the solid island inside the ring, exactly as drawn. Treat the cream area as the clear floor width: the partitions stand in the terrain area next to it, never inside the cream. Repaint everything as the hand-made miniature described above. Do NOT carry over the diagram's four flat colours as flat fills (the desk is a warm wooden tabletop, the base band is foamboard and corrugated cardboard, there is no flat brown area anywhere in the result) or its perfectly straight, hard edges.
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
[Issue #142 決定コメント（時系列順。各コメントの見出しと、BDY-16 に関わる決定の行だけを逐語で抜粋。相互に食い違う場合は、より後のコメントが優先）]
## kako-jun 決定・指摘（2026-10-22、モック一覧を見て）
4. **脳・心臓・肺など**（「肺や心臓などは、医学的に右心室など4つに分かれているとかを抽象的に表現すればいい。脳は迷路状ということだな」）→ 脳=迷路状。心臓=解剖学の4つの部屋（右心房・右心室・左心房・左心室）を抽象的な4つの部屋と通路で表す。肺・胃も同様に実際の区分を抽象化（分け方の詳細は kako-jun が示した「など」までなので仮案を出してモックで確認）。血・写実的な臓器は描かない（既存方針）。

## kako-jun 決定（2026-10-22）: 左右は身体の本人から見る
「左右の考え方は、身体の本人からみてにして。本人は仰向けに寝ている。それを正面から見ている構図だ。だから画面左側は右手だ」
- 左右は**本人から見た**左右。本人は仰向けで、画面（正面から見る構図）の左側が本人の右手・右足、右側が本人の左手・左足。
- 部屋名（右心房＝画面左、右肺3葉＝画面左）は現行の置き方で本決定と一致。

## kako-jun 決定（2026-10-22、モック一覧と接続表を見て）
「心臓は自然にすればいい。肺は人間のがうずまきでないなら行き止まりなしでいいのでは。首はこれでいい。足の角度は太もも部分が１マップ内に短すぎてもったいないので曲がってる感じしてはどうか」
1. 心臓: 自然（本人の左側＝画面右）。BDY-02 の南辺は 肺=左寄り・下半身=中央・心臓=右寄り で確定。
[docs/map-topology.md:118]
以下は接続の向きを一意にする正本である。`→` の両側は必ず反対の画像辺とし、`door` は画像端でなく室内・階層遷移である。`event` は一方向の物語イベント、`oneway` は一方向の通常移動。`door-passage-*` は体内の抽象通路名で物理的な扉ではない。`pending` は旧仮説のID追跡だけの行で、隣接・通行路・生成契約ではない。`§3.1` 以降の旧試作時の図・発注文は履歴説明であり、ここにない辺指定を新規プロンプト、画像生成、マスクに使ってはならない。
[docs/map-asset-registry.md:91]
| ID | 画像 | 地区 | 未決のため必要な個別契約 |
[docs/map-asset-registry.md:92]
|---|---|---|---|
[docs/map-asset-registry.md:118]
| BDY-16 | `BDY-16` | 抽象体内 | 心臓・分岐室。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。丸い4部屋（右心房=画面左上・右心室=左下・左心房=右上・左心室=右下。左右は本人から見る）を四角い環の通路でつなぐ。入口は北辺。形の詳細（座標・格子）は verification/body-layout の割付図が正本。pixel/maskはTBD（mask未作成）。 |
[docs/map-specifications.md:117]
| MAP | 時期 | 一言特徴 | 方位・主路・通行条件 | 暫定固定 |
[docs/map-specifications.md:118]
|---|---|---|---|---|
[docs/map-specifications.md:126]
| BDY-16 | 中3 | 心臓・分岐室 | door-passage-torso→BDY-02.door-passage-heart | 上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。丸い4部屋（右心房=画面左上・右心室=左下・左心房=右上・左心室=右下。左右は本人から見る）を四角い環の通路でつなぐ。入口は北辺。形の詳細（座標・格子）は verification/body-layout の割付図が正本。pixel/maskはTBD（mask未作成）。 |
[docs/map-contract-checklist.md:11]
| ID | 状態 | Ref | mask / 出力 | 具体的TBD |
[docs/map-contract-checklist.md:12]
|---|---|---|---|---|
[docs/map-contract-checklist.md:82]
| BDY-16 | blocked | R018 | 未生成・mask未作成 | 心臓・分岐室。door-passage-torso→BDY-02.door-passage-heart。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。丸い4部屋（右心房=画面左上・右心室=左下・左心房=右上・左心室=右下。左右は本人から見る）を四角い環の通路でつなぐ。入口は北辺。形の詳細（座標・格子）は verification/body-layout の割付図が正本。pixel/maskはTBD（mask未作成）。 |
[docs/map-topology.md:260]
| BDY-02.door-passage-heart | BDY-16.door-passage-torso | door | 架空人体の抽象通路。door-passageは物理的な扉でない。上半身/下半身2枚・手各2枚・足各3枚の連続一本道 |
[docs/map-topology.md:686]
## 体内の現行空間設計（#74・追加ボリューム決定）
[docs/map-topology.md:688]
TRM-01園庭→BDY-01口は一方向の物語イベント。病院・海外からの体内経路や恒常的な徒歩口ではない。胴体は縦2MAP、上半身BDY-02→下半身BDY-03。頭BDY-04は上半身の上の迷路状通路。左右の手は上半身から斜め上へ伸び、左BDY-05→BDY-06（画面右上・上半身の東辺から出て、BDY-05の西辺から入る）／右BDY-07→BDY-08（画面左上・上半身の西辺から出て、BDY-07の東辺から入る）の各2MAPの一本道。左右の足は下半身から斜め下へ伸び、左BDY-09→BDY-10→BDY-11（画面右下・下半身の東辺から出る）／右BDY-12→BDY-13→BDY-14（画面左下・下半身の西辺から出る）の各3MAPの一本道。**左右は身体の本人から見る（本人は仰向け、それを正面から見る構図。画面左が本人の右手・右足、画面右が本人の左手・左足。心臓は本人の左側＝画面右、肺は画面左。kako-jun 2026-10-22、#142）。**手足末端は閉じ、手足相互の連絡や迂回路を足さない。方向は分岐の方位であり、各手足MAPには縦方向の通路ボリュームを持たせる。
[docs/map-topology.md:690]
BDY-15胃・BDY-16心臓・BDY-17肺はそれぞれ独立したMAPで、胴体からの単純な分岐室。医学的解剖や写実的臓器ではなく、現実離れした幼稚園児の想像する架空人体の抽象概念、肌色寄りでよい。胃の盾役・エラー細胞と、心臓での水の精霊・火による復活という既存の物語を保持。BDY-02の作画契約: 口→上半身→下半身を中央主路でつなぎ、頭・左右の腕・心臓・肺を枝にする。各経路は模型（ジオラマ）の縁の辺まで届いて隣MAPへ遷移し（遷移位置は辺上の範囲指定、範囲値TBD。土台の板とまわりの机は見えたまま。接続は辺単位の判定のまま。kako-jun 2026-10-22）、洞窟状の穴や物理的な扉は描かない。体の外形を描かず、平面床と低い仕切りで道を作る。配置方位は `docs/topology/body.svg` のBDY-02接続線に従う（心臓=南東・画面右、肺=南西・画面左。南辺は肺=左寄り・下半身=中央・心臓=右寄り。BDY-16は北辺から、BDY-17は北辺中央から入る。首は広間から1本、上で頭（北）と口（北東）に分岐）。心臓・肺の部屋はBDY-02内に描かず、胃はBDY-03からBDY-15へ接続する。空間接続から新たな攻略順・肺ボス・全枝任意という条件を決めない。脳BDY-04は迷路（通路幅はキャラクター1人分で約77px、入口は南辺中央1本、行き止まりの迷路で出口なし）。胃BDY-15は分岐なしJ字の1袋（入口は西辺230px→ドーム→胃体最大460px→幽門130pxで丸く閉じる）。心臓BDY-16は丸い4部屋（右心房=画面左上・右心室=左下・左心房=右上・左心室=右下）を四角い環の通路でつなぐ（入口は北辺）。肺BDY-17は人間の肺が渦巻きでないため行き止まりなし（外周の環に右肺3葉=画面左・左肺2葉=画面右の丸い5部屋、入口は北辺中央、通路幅は人間1人分）。形の詳細（座標・格子）は検証の割付図（verification/body-layout）が正本。pixel/mask・発火条件はTBD。
[docs/map-topology.md:692]
119案の単一胴体・各手足1MAPは追加口述により失効。全130MAP（#87/#89でKRB-02・NTB-07、#87でデパート2階KRB-03・4階KRB-05を追加）、体内17MAP。工程Aの体内正本をコミット・プッシュした後、工程Bの全体図・アトラス・全15エリア図も更新済み。
[docs/art-direction.md:195]
## #74 体内の最新空間・色の契約
[docs/art-direction.md:197]
**左右は身体の本人から見る（本人は仰向けに寝ていて、それを正面から見る構図。画面左側が本人の右手・右足、画面右側が本人の左手・左足。心臓は本人の左側＝画面右、肺は画面左。kako-jun 2026-10-22、#142）。**
[docs/art-direction.md:199]
体内は医学的な身体の再現でなく、現実離れした幼稚園児の想像する架空人体の抽象的概念。肌色寄りでよく、血や写実的な臓器・内壁を描かず、グロくしない。胴体は縦2MAPの上半身/下半身、手各2MAP・足各3MAPの縦通路ボリューム。頭は上、手は斜め上、足は斜め下。脳は迷路状通路、心臓・肺は単純な分岐室。背景共通の手作りジオラマに合わせ、5 mm foamboardの土台と見えるcorrugated cardboard断面、指跡・爪楊枝の跡を残したpaper clayの丸い地形を使う。肌色・薄桃・クリーム色のmatte poster paintで着色し、赤い折り紙を切った形を血痕に見えない明確な工作アクセントとして置く。毛糸は通路の縁や造形の継ぎ目に用い、雪の綿は使わない。白いPVA接着剤とmasking tapeで固定し、紙端・接着・塗りの手作り感を残す。旧『紙粘土・セロファンだけ』『口から手足が直結』という解釈を新規生成の固定根拠にしない（材料決定は2026-10-21 kako-junとの相談）。
[docs/art-direction.md:30]
- 背景はタイルを無限に継ぎ足さない。場所ごとに、全景・広い道路・狭い道・接続画を同じカメラ、光、反復物で一度に作る。視点は、真上に近い見下ろし（2026-10-14 変更。以前の「高めの斜め見下ろし（約45°）」は撤回）。フィールドは固定の一枚絵で、スクロールしない。絵の端（模型の縁の辺）で次の絵に切り替わる（2026-10-14）。通路は画像端でなく模型の縁まで届き、土台の板とまわりの机は見えたまま。遷移位置は画面端固定でなく範囲指定（2026-10-22 kako-jun）。
[docs/map-reference-research.md:24]
| R018 | BDY-01〜BDY-17 | `docs/art-direction.md` と `docs/assets-policy.md`／プロジェクト正本 | 人体の写実・流血・臓器表現を避け、幼稚園児が想像する架空人体を肌色寄りの手作りジオラマで表す。共通背景の工作材（foamboard・段ボール・paper clay・matte poster paint）に、赤い折り紙の切片と毛糸を加える。雪景色の綿は使わない（2026-10-21決定） | 体内のMAPごとの敵・戦闘域は各契約行で決める |
[docs/map-reference-research.md:57]
| BDY-01〜BDY-17 | 体内の抽象ダンジョン | 実在写真を参照しない。安全表現・接続・ボス配置の視覚契約をMAP別に書くまで生成不可 |
[docs/map-reference-research.md:86]
## #74 体内の最新根拠
[docs/map-reference-research.md:88]
ユーザー原文に基づく空間: 胴体は縦2MAP（上半身・下半身）、手は各2MAP、足は各3MAPの通路。頭上・手左右斜め上・足左右斜め下、脳は迷路、心臓・肺は単純な分岐室。非写実・現実離れした幼稚園児の想像する架空人体、肌色寄り。医学的資料から形状を推測しない。BDY-02上半身/BDY-03下半身への各部接続と肺BDY-17は制作上のID配置。胃を下半身、心臓と肺を上半身から分けることは抽象的なゲーム配置で、解剖の事実ではない。
[docs/decisions.md:341]
体内入口はTRM-01園庭→BDY-01口の物語イベント。胴体は縦2MAPの上半身BDY-02・下半身BDY-03、左右手各2MAP、左右足各3MAP。手足は一本道、頭は上の迷路通路、胃・心臓・肺は単純な分岐室。肌色寄りの幼稚園児の想像する架空人体で医学的写実はしない。新規BDY-02〜BDY-03・BDY-05・BDY-07・BDY-09〜BDY-10・BDY-12〜BDY-13・BDY-17を追加して全126MAP。既存の胃・心臓の物語条件を保持。工程Aをコミット・プッシュしてから、工程Bで全体図と残りの全MAP接続図を作る。
[docs/map-topology.md:46]
| 体内 | 中3 | ダンジョン・既存の部位イベント | 17MAP | 0 | 上半身/下半身各1、手各2、足各3、口・頭・胃・心臓・肺 | 肌色寄りの幼稚園児の架空人体。非写実 | 頭は上、手は斜め上、足は斜め下の一本道 | 脳は迷路、心臓・肺は分岐室 |
[docs/map-topology.md:618]
| 体内 | 中3 | ダンジョン・既存の部位イベント | 17MAP | 0 | 上半身/下半身各1、手各2、足各3、口・頭・胃・心臓・肺 | 肌色寄りの幼稚園児の架空人体。非写実 | 頭は上、手は斜め上、足は斜め下の一本道 | 脳は迷路、心臓・肺は分岐室 |
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
[注記] 通路幅は天面幅比0.14=230px。

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
| 体内入口はTRM-01園庭→BDY-01口の物語イベント | decisions | P4/P5（接続は模型の縁のみ） |
| 心臓=解剖学の4つの部屋（右心房・右心室・左心房・左心室）を抽象的な4つの部屋と通路で表す | Issue #142 | P4（丸い4部屋を四角い環の通路でつなぐ。部屋名は絵に描かない。docs の『単純な分岐室』は、この MAP の部屋は4つの丸い部屋、の形で P4 が明示） |
| 心臓は自然にすればいい | Issue #142 | P4（心臓は自然に。本人の左側＝画面右は BDY-02 の南辺の位置） |
| 接続（door-passage-torso→BDY-02.door-passage-heart） | spec / topology の接続列 | P3（辺・位置は割付図の実測） |

## 5. 割付図の実測（`clean/BDY-16.png`。1920x1080 と ×0.871 の 1672x941）

- 構図: 机90px・土台縁48px（foamboard 28 + corrugated 20）・天面 x138–1782 y138–942（1644x804）。通路幅 230px（1672: 200px）。
- 経路の形: 丸い4部屋を四角い環の通路でつなぐ。部屋: 右心房 中心(565, 328) 半径160; 右心室 中心(565, 752) 半径160; 左心房 中心(1355, 328) 半径160; 左心室 中心(1355, 752) 半径160（名前は注記のみ・絵に描かない）。
- 環の通路（画素の床の区間）: 上 y(213, 443)・下 y(637, 867)・左 x(450, 680)・右 x(1240, 1470)。島（地形）: x681–1239・y444–636。入口 N辺 (450, 680)。
- 赤紙6枚の中心（周囲の正方形が全て地形の画素から、最遠点サンプリングで決定。5px刻み）: (180, 180), (1645, 180), (985, 495), (1520, 565), (365, 900), (1740, 900)（各約45px）。
| 辺 | port | 区間（1920） | 区間（1672x941） | 幅 | 折れ線（1920座標） |
|---|---|---|---|---|---|
| N | door-passage-torso | x 450–680 | x 392–592 | 231 | (565,138), (565,328) |

地形の区画（連結成分）: central（広、面積約589568px、bbox (140, 140, 1780, 940)）; central（広、面積約108976px、bbox (684, 444, 1236, 636)）

## 6. 寸法・検査項目（生成後。生画像レビュー用）

寸法（`file` / `identify` で実ファイルを測る。prompt指定・ファイル名は証拠にならない）:
- [ ] 1920x1080、または 1672x941（その場合は座標に0.871を掛けて比較）。それ以外は failed。リサイズ・切り抜きで通さない。

構図（割付図 `verification/body-layout/clean/BDY-16.png` と実画素・目視で比較）:
- [ ] 机（木目の木の机）が四辺に約90px見える。その内側に約48px幅の土台縁の帯（外28px foamboard・内20px corrugated 断面）が**四辺すべて（北・南・西・東）**で途切れず見える（机→縁取り→波形→天面の順）。模型の天面は画像の内側に収まり画像の縁に接しない。天面は x138–1782・y138–942 付近。
- [ ] 入口の通路が模型の縁（土台縁の帯の内側）に届く。画像端（机の外）に通路が出ていない。床は模型の外に一画素も無い。

通路（入口は1本だけ）:
- [ ] N辺: 縁から2px内側で x 450–680（1672: x 392–592）、幅約230px（1672: 約200px）、辺に垂直。他の縁には床が出ていない。遷移範囲の印（色帯・矢印・線・文字）が絵に無い。

経路の形（本命の検査。割付図の実測値）:
- [ ] 丸い部屋が**4つ**（各半径160px、2x2）を、**4本の直線の通路（幅230px）の四角い環**でつなぐ。環の中の島は地形。行き止まり・5つ目の部屋・斜めの通路が無い。入口は北辺の1本（左の通路と同じx範囲）で左上の部屋へ。部屋名・心臓の形・臓器の輪郭が絵に無い。
- [ ] 部屋の中心: (565, 328), (565, 752), (1355, 328), (1355, 752)。

材料・質感・装飾（装飾込み1回生成）:
- [ ] ① 土台縁の帯に corrugated cardboard 断面と foamboard の縁 ② 仕切りが細く低い corrugated の帯1本（床の幅に含まれない）
- [ ] ③ 地形が paper clay の面で、肌色・薄桃・茶系の matte poster paint ④ 赤い折り紙の切片が**ちょうど6枚**（数えて6枚・7枚目なし。全て模型の中の地形の上。模型の外・机・床・土台縁の帯には無い。装飾の下敷きでない）
- [ ] ⑤ 机が木目の木の机
- [ ] ⑥ 装飾は人体に関係する抽象的な工作物だけ（骨・細胞や粒・筋肉や神経の糸・鼓動のぎざぎざ線・皮膚の彫り・ばんそうこう・毛・ばい菌）。少なくとも6か所の塊。花・葉・雲・星・旗・柵・ハート形・動物・食べ物・風景・臓器の形・血管の網が無い
- [ ] ⑥b 装飾の色が肌色・薄桃・クリーム・茶系・象牙色の範囲（緑・青・黄・紫・オレンジが無い）。赤は折り紙6枚だけ
- [ ] ⑦ 床には何も置かれず平ら。毛糸が血管・臓器に見える走り方をしていない
- [ ] ⑨ 精霊・炎・水の絵・人物が地形や床に無い（全て小さな手作りの工作物）

許容差（レビュー側基準。生成入力には入れない）: 通路位置 ±25px、幅 ±10%（1672x941 の場合は ×0.871）。床マスクIoU（clean 割付図に対して）≥0.95 を目安。迷路は通路の接続（行き止まりの数・T字の数）の一致を床IoUより優先して見る。
