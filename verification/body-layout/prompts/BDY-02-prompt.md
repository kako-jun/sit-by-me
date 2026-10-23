# BDY-02（上半身・胴体上段）装飾込み1回生成の完全 imagegen prompt（`build_body_prompt.py` 自動生成。Issue #142）

> 履歴: 2026-10-22 時点の生成記録。2026-10-23 に TRM-01 は TRM-03 に統合（園庭=TRM-03の右の区画、起点は TRM-03.event-kiss）。現行の正本は docs/map-topology.md と docs/production/body-masks/BDY-01-links.json。本文中の TRM-01・行番号は当時のまま（送信済みの逐語記録）。

状態: **機械生成・独立レビュー済み（条件付き可）・指摘反映済み・画像は未生成**。`.claude/skills/sit-field-background/SKILL.md` のゲート（台帳原文・材料固定宣言・一意解釈・寸法）に沿う。型は採用済み BDY-02（v2 の構図・原文束、v3 の装飾語彙）。画像は生成しない。

## 0. 来歴・警告・TBD

来歴:
- 生成器: `.claude/skills/sit-field-background/tools/build_body_prompt.py`（使い方: `build_body_prompt.py BDY-02 --out DIR`）。入力は docs の対象行（逐語）・Issue #142・`verification/body-layout/clean/BDY-02.png` の画素実測・`body_layout.py` の折れ線。
- 型: `docs/production/20261022-bdy02-adoption.md` と `20261022-bdy02-adoption-prompts/`（v2-prompt-full.txt=構図・原文束、v3-edit-prompt.txt=装飾語彙）。
- 入力 sha256（参照2枚。様式参照画像は幾何を崩す疑いがあるので使わない）: clean `720ffd1c396196e4fa9fac15e8be2fea29afe5f362f9f5a0c383ad0586ef1d45` / 材料見本 `764b7ae7f1aa0ff19bd8e79a8724fc8b975c4d5465440fb539f5566f52828b45`
- 送信文 sha256: `1b2919851156af8249c815c3206ad19995cbc7838cbefe8ed2b1ef1434282955`
- 送信文: `BDY-02-prompt-send.txt`（wrapper + 本文。この .md の §3.1 と §3.2 を連結したもの。§3.2 は §1 の原文束を SOURCE TEXT として含む。原文束の外に内部メモ・TBD・仮案を含まない）。

警告・TBD（ビルダーが検出）:
- 決定済み: 首は1本で上で頭（北）と口（北東）に分岐・南辺は肺=左・下半身=中央・心臓=右・左右は本人から見る（kako-jun 2026-10-22。Issue #142 の決定コメント）。
- 作り直し: 採用済みの BDY-02（旧プール・フェルトの花入り）を新プールで作り直す（kako-jun 2026-10-22『つくりなおせ』）。採用時の構造記述（段階1）を保ち、装飾・色・赤紙・土台縁・壁の細さは共通部品。壁（広間の弧を含む）は細い corrugated 帯＋毛糸1本で床の幅を守る。広間の壁の弧は段ボール茶（青灰でない）。
- 座標・角度は clean 画素の実測（body_layout の定数と照合済み）。別コードの再測定は verification/body-layout/remeasure_bdy02.py <送信文>。
- 装飾込み1回生成（onepass）: 参照は2枚（clean 割付図・材料見本）。様式参照画像は使わない。
- 独立レビュー（opus。2026-10-22）は条件付き可。指摘（装飾が幾何を圧倒・P4冒頭の環状の誤読・P10の赤紙の曖昧語・許可品目の矛盾・禁止語）を反映済み: P9 を圧縮し色の段落は P8 に1回だけ、P4 は4区間だけ壁と明記、赤紙は6枚の領域と座標を固定、許可品目は主役・脇役が使うものだけ。
- [注記] 通路幅は天面幅比0.14=230px。の行は docs 由来でなく、ビルダーが clean 実測から原文束の末尾に加えた注記（照合表の docs 行数には含めない）。
- 腕・心臓・口の曲がりの外角の丸みは半径115px（clean の帯は折れ点に半径=幅の半分の円を置いて描く。口は実測で確認、左腕・心臓も外角の最遠画素が116px、右腕は約116〜120px）。肺は広間の床が重なり画素では分離できないが同じ作り。

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
[Issue #142 決定コメント（時系列順。各コメントの見出しと、BDY-02 に関わる決定の行だけを逐語で抜粋。相互に食い違う場合は、より後のコメントが優先）]
## kako-jun 決定（2026-10-22「推奨で」）
BDY-02 の以下を、提示した推奨どおりに確定:
1. 口の辺 = 北辺（頭の右隣）。
5. 赤い折り紙 = 手切りで輪郭が不揃いな赤い紙片を6枚。毛糸 = クリームと薄桃。

## kako-jun 決定（2026-10-22、BDY-02 v1 を見て）
1. 「模型の縁まででいい。画面遷移のためにキャラが立つ場所は画面端固定でなく範囲指定すればいいのだ」— 通路は**画像端でなく模型（ジオラマ）の縁まで**届かせる。遷移のトリガー位置は画面端に固定せず、範囲（レンジ）で指定する。

## kako-jun 決定（2026-10-22）: 首は A案
「A」— 首は BDY-02 の内部で1本にし、上で頭（北）と口（北東）に分岐する。MAP数・接続は不変（BDY-02 の北辺の出口は頭・口の2か所のまま）。BDY-02 の内部の形（広間から北へ首が1本、上で分岐）だけを変える。

## kako-jun 決定（2026-10-22）: 左右は身体の本人から見る
「左右の考え方は、身体の本人からみてにして。本人は仰向けに寝ている。それを正面から見ている構図だ。だから画面左側は右手だ」
- 左右は**本人から見た**左右。本人は仰向けで、画面（正面から見る構図）の左側が本人の右手・右足、右側が本人の左手・左足。

## kako-jun 決定（2026-10-22、モック一覧と接続表を見て）
「心臓は自然にすればいい。肺は人間のがうずまきでないなら行き止まりなしでいいのでは。首はこれでいい。足の角度は太もも部分が１マップ内に短すぎてもったいないので曲がってる感じしてはどうか」
1. 心臓: 自然（本人の左側＝画面右）。BDY-02 の南辺は 肺=左寄り・下半身=中央・心臓=右寄り で確定。
3. 首: 現行の形（広間から首1本→上で頭・口に分岐）で確定。
[docs/map-topology.md:118]
以下は接続の向きを一意にする正本である。`→` の両側は必ず反対の画像辺とし、`door` は画像端でなく室内・階層遷移である。`event` は一方向の物語イベント、`oneway` は一方向の通常移動。`door-passage-*` は体内の抽象通路名で物理的な扉ではない。`pending` は旧仮説のID追跡だけの行で、隣接・通行路・生成契約ではない。`§3.1` 以降の旧試作時の図・発注文は履歴説明であり、ここにない辺指定を新規プロンプト、画像生成、マスクに使ってはならない。
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
[docs/map-topology.md:246]
| BDY-01.door-passage-torso | BDY-02.door-passage-mouth | door | 架空人体の抽象通路。door-passageは物理的な扉でない。上半身/下半身2枚・手各2枚・足各3枚の連続一本道 |
[docs/map-topology.md:247]
| BDY-02.door-passage-lower | BDY-03.door-passage-upper | door | 架空人体の抽象通路。door-passageは物理的な扉でない。上半身/下半身2枚・手各2枚・足各3枚の連続一本道 |
[docs/map-topology.md:248]
| BDY-02.door-passage-head | BDY-04.door-passage-torso | door | 架空人体の抽象通路。door-passageは物理的な扉でない。上半身/下半身2枚・手各2枚・足各3枚の連続一本道 |
[docs/map-topology.md:249]
| BDY-02.door-passage-left-arm | BDY-05.door-passage-torso | door | 架空人体の抽象通路。door-passageは物理的な扉でない。上半身/下半身2枚・手各2枚・足各3枚の連続一本道 |
[docs/map-topology.md:251]
| BDY-02.door-passage-right-arm | BDY-07.door-passage-torso | door | 架空人体の抽象通路。door-passageは物理的な扉でない。上半身/下半身2枚・手各2枚・足各3枚の連続一本道 |
[docs/map-topology.md:260]
| BDY-02.door-passage-heart | BDY-16.door-passage-torso | door | 架空人体の抽象通路。door-passageは物理的な扉でない。上半身/下半身2枚・手各2枚・足各3枚の連続一本道 |
[docs/map-topology.md:261]
| BDY-02.door-passage-lung | BDY-17.door-passage-torso | door | 架空人体の抽象通路。door-passageは物理的な扉でない。上半身/下半身2枚・手各2枚・足各3枚の連続一本道 |
[docs/map-topology.md:686]
## 体内の現行空間設計（#74・追加ボリューム決定）
[docs/map-topology.md:688]
TRM-01園庭→BDY-01口は一方向の物語イベント。病院・海外からの体内経路や恒常的な徒歩口ではない。胴体は縦2MAP、上半身BDY-02→下半身BDY-03。頭BDY-04は上半身の上の迷路状通路。左右の手は上半身から斜め上へ伸び、左BDY-05→BDY-06（画面右上・上半身の東辺から出て、BDY-05の西辺から入る）／右BDY-07→BDY-08（画面左上・上半身の西辺から出て、BDY-07の東辺から入る）の各2MAPの一本道。左右の足は下半身から斜め下へ伸び、左BDY-09→BDY-10→BDY-11（画面右下・下半身の東辺から出る）／右BDY-12→BDY-13→BDY-14（画面左下・下半身の西辺から出る）の各3MAPの一本道。**左右は身体の本人から見る（本人は仰向け、それを正面から見る構図。画面左が本人の右手・右足、画面右が本人の左手・左足。心臓は本人の左側＝画面右、肺は画面左。kako-jun 2026-10-22、#142）。**手足末端は閉じ、手足相互の連絡や迂回路を足さない。方向は分岐の方位であり、各手足MAPには縦方向の通路ボリュームを持たせる。
[docs/map-topology.md:690]
BDY-15胃・BDY-16心臓・BDY-17肺はそれぞれ独立したMAPで、胴体からの単純な分岐室。医学的解剖や写実的臓器ではなく、現実離れした幼稚園児の想像する架空人体の抽象概念、肌色寄りでよい。胃の盾役・エラー細胞と、心臓での水の精霊・火による復活という既存の物語を保持。BDY-02の作画契約: 口→上半身→下半身を中央主路でつなぎ、頭・左右の腕・心臓・肺を枝にする。各経路は模型（ジオラマ）の縁の辺まで届いて隣MAPへ遷移し（遷移位置は辺上の範囲指定、範囲値TBD。土台の板とまわりの机は見えたまま。接続は辺単位の判定のまま。kako-jun 2026-10-22）、洞窟状の穴や物理的な扉は描かない。体の外形を描かず、平面床と低い仕切りで道を作る。配置方位は `docs/topology/body.svg` のBDY-02接続線に従う（心臓=南東・画面右、肺=南西・画面左。南辺は肺=左寄り・下半身=中央・心臓=右寄り。BDY-16は北辺から、BDY-17は北辺中央から入る。首は広間から1本、上で頭（北）と口（北東）に分岐）。心臓・肺の部屋はBDY-02内に描かず、胃はBDY-03からBDY-15へ接続する。空間接続から新たな攻略順・肺ボス・全枝任意という条件を決めない。脳BDY-04は迷路（通路幅は人間1人分）。肺BDY-17は人間の肺が渦巻きでないため行き止まりなし（外周の環に右肺3葉・左肺2葉の抽象的な部屋、通路幅は人間1人分。形の詳細は検証の割付図が正本）。迷路形状・mask/pixel・幅・発火条件はTBD。
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
[docs/map-asset-registry.md:91]
| ID | 画像 | 地区 | 未決のため必要な個別契約 |
[docs/map-asset-registry.md:92]
|---|---|---|---|
[docs/map-asset-registry.md:111]
| BDY-01 | `BDY-01` | 抽象体内 | 口・体内入口。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。
[docs/map-specifications.md:117]
| MAP | 時期 | 一言特徴 | 方位・主路・通行条件 | 暫定固定 |
[docs/map-specifications.md:118]
|---|---|---|---|---|
[docs/map-specifications.md:119]
| BDY-01 | 中3 | 口・体内入口 | door-passage-torso→BDY-02.door-passage-mouth | 上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。
[docs/map-contract-checklist.md:11]
| ID | 状態 | Ref | mask / 出力 | 具体的TBD |
[docs/map-contract-checklist.md:12]
|---|---|---|---|---|
[docs/map-contract-checklist.md:75]
| BDY-01 | blocked | R018 | 未生成・mask未作成 | 口・体内入口。door-passage-torso→BDY-02.door-passage-mouth。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。
[docs/map-asset-registry.md:181]
| ID | 管理名 | 地区 | 契約 |
[docs/map-asset-registry.md:182]
|---|---|---|---|
[docs/map-asset-registry.md:183]
| BDY-03 | `BDY-03` | 抽象体内 | 下半身・胴体下段。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |
[docs/map-specifications.md:210]
| MAP | 時期 | 一言特徴 | 接続 | 不変条件／TBD |
[docs/map-specifications.md:211]
|---|---|---|---|---|
[docs/map-specifications.md:212]
| BDY-03 | 中3 | 下半身・胴体下段 | door-passage-upper→BDY-02.door-passage-lower、door-passage-left-leg→BDY-09.door-passage-torso、door-passage-right-leg→BDY-12.door-passage-torso、door-passage-stomach→BDY-15.door-passage-torso | 上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |
[docs/map-contract-checklist.md:145]
| ID | 状態 | Ref | mask / 出力 | 具体的TBD |
[docs/map-contract-checklist.md:146]
|---|---|---|---|---|
[docs/map-contract-checklist.md:147]
| BDY-03 | blocked | R018 | 未生成・mask未作成 | 下半身・胴体下段。door-passage-upper→BDY-02.door-passage-lower、door-passage-left-leg→BDY-09.door-passage-torso、door-passage-right-leg→BDY-12.door-passage-torso、door-passage-stomach→BDY-15.door-passage-torso。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |
[docs/map-asset-registry.md:116]
| BDY-04 | `BDY-04` | 抽象体内 | 頭・脳の迷路通路。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |
[docs/map-specifications.md:124]
| BDY-04 | 中3 | 頭・脳の迷路通路 | door-passage-torso→BDY-02.door-passage-head | 上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |
[docs/map-contract-checklist.md:80]
| BDY-04 | blocked | R018 | 未生成・mask未作成 | 頭・脳の迷路通路。door-passage-torso→BDY-02.door-passage-head。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |
[docs/map-asset-registry.md:184]
| BDY-05 | `BDY-05` | 抽象体内 | 左手通路1・付け根側。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。
[docs/map-specifications.md:213]
| BDY-05 | 中3 | 左手通路1・付け根側 | door-passage-torso→BDY-02.door-passage-left-arm、door-passage-tip→BDY-06.door-passage-base | 上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。
[docs/map-contract-checklist.md:148]
| BDY-05 | blocked | R018 | 未生成・mask未作成 | 左手通路1・付け根側。door-passage-torso→BDY-02.door-passage-left-arm、door-passage-tip→BDY-06.door-passage-base。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。
[docs/map-asset-registry.md:185]
| BDY-07 | `BDY-07` | 抽象体内 | 右手通路1・付け根側。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。
[docs/map-specifications.md:214]
| BDY-07 | 中3 | 右手通路1・付け根側 | door-passage-torso→BDY-02.door-passage-right-arm、door-passage-tip→BDY-08.door-passage-base | 上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。
[docs/map-contract-checklist.md:149]
| BDY-07 | blocked | R018 | 未生成・mask未作成 | 右手通路1・付け根側。door-passage-torso→BDY-02.door-passage-right-arm、door-passage-tip→BDY-08.door-passage-base。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。
[docs/map-asset-registry.md:118]
| BDY-16 | `BDY-16` | 抽象体内 | 心臓・分岐室。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |
[docs/map-specifications.md:126]
| BDY-16 | 中3 | 心臓・分岐室 | door-passage-torso→BDY-02.door-passage-heart | 上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |
[docs/map-contract-checklist.md:82]
| BDY-16 | blocked | R018 | 未生成・mask未作成 | 心臓・分岐室。door-passage-torso→BDY-02.door-passage-heart。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |
[docs/map-asset-registry.md:177]
| BDY-17 | `BDY-17` | 抽象体内 | 肺・分岐室。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |
[docs/map-specifications.md:206]
| BDY-17 | 中3 | 肺・分岐室 | door-passage-torso→BDY-02.door-passage-lung | 上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |
[docs/map-contract-checklist.md:141]
| BDY-17 | blocked | R018 | 未生成・mask未作成 | 肺・分岐室。door-passage-torso→BDY-02.door-passage-lung。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |
[注記] 通路幅は天面幅比0.14=230px。
```

## 2. 参照一覧（実画像として入力する順。参照は2枚）

| # | パス | 用途 | 継承禁止事項 |
|---|---|---|---|
| 1 | `verification/body-layout/clean/BDY-02.png`（1920x1080、5色のベタ。灰=机、茶=土台縁の帯、くすんだ桃茶=天面の地形、クリーム=歩ける床、青灰=広間の壁の弧。文字・注記・遷移範囲の着色なし。画像編集の入力＝塗り直しの土台） | 幾何のみ（机・土台縁・天面の入れ子、通路の本数・辺・位置・幅・曲がり・端） | 色を塗らせない（5色ベタ・硬い直線エッジは継承しない）。文字・遷移範囲の印を残さない |
| 2 | `verification/body-layout/BDY-material-swatch-corrugated-edge.png`（1540x52。寺町の採用画像の下端の帯を無加工で切り出した材料見本） | 材料の感じのみ: corrugated cardboard 断面・masking tape・ちぎれた紙端 | 帯上端の白い綿の繊維・茶色の色味は継承しない。雪を持ち込まない |
添付順 = 1, 2（wrapper の『Two images』の列挙と本文 REFERENCE の FIRST/SECOND が一致）。

## 3. 送信予定の完全 prompt

### 3.1 前置き指示（wrapper）

```text
Invoke the $imagegen skill and use the built-in image_gen tool at the HIGHEST quality (quality: high), keeping the editing source's size 1920x1080 (16:9), to repaint the image as described in the prompt below. This is an IMAGE EDIT: use the image_gen tool in image-edit mode on the first attached image. Two images are attached, in this order: (1) the editing source (a flat five-colour layout diagram with no text; keep its geometry exactly, and use the meaning of its colours as described in the prompt); (2) a thin close-up strip of the edge of a hand-made cardboard miniature, for materials and craft feel only (as described in the prompt). Call image_gen EXACTLY ONCE: no retries, no regeneration, no multiple candidates, even if you think the result is imperfect. Then save the REAL generated PNG (decode the tool result) into the current workspace at out/bdy02-op-v4.png. You are STRICTLY FORBIDDEN from fabricating/drawing the image with magick/ImageMagick/PIL/Pillow/numpy/SVG/canvas/any code; only the image_gen tool. If the image_gen tool is genuinely not in your toolset, do NOT fabricate - output exactly: IMAGE_GEN_TOOL_UNAVAILABLE. Do not resize or crop the result. Do not use any files in ~/.codex/generated_images/ made by other calls; only the image generated in this call. Report the saved file path.
Output a 16:9 landscape image. Keep the size of the editing source (1920x1080); if not possible, 1672x941. Do NOT use 3:2 or 1536x1024. Do not mirror or flip the image; keep the direction of the editing source.
```

### 3.2 本文

```text
Generate ONE image: the final field background for map BDY-02 (the upper torso (上半身・胴体上段), of the imaginary human body inside which the story travels). Do not generate any other map.

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
[Issue #142 決定コメント（時系列順。各コメントの見出しと、BDY-02 に関わる決定の行だけを逐語で抜粋。相互に食い違う場合は、より後のコメントが優先）]
## kako-jun 決定（2026-10-22「推奨で」）
BDY-02 の以下を、提示した推奨どおりに確定:
1. 口の辺 = 北辺（頭の右隣）。
5. 赤い折り紙 = 手切りで輪郭が不揃いな赤い紙片を6枚。毛糸 = クリームと薄桃。

## kako-jun 決定（2026-10-22、BDY-02 v1 を見て）
1. 「模型の縁まででいい。画面遷移のためにキャラが立つ場所は画面端固定でなく範囲指定すればいいのだ」— 通路は**画像端でなく模型（ジオラマ）の縁まで**届かせる。遷移のトリガー位置は画面端に固定せず、範囲（レンジ）で指定する。

## kako-jun 決定（2026-10-22）: 首は A案
「A」— 首は BDY-02 の内部で1本にし、上で頭（北）と口（北東）に分岐する。MAP数・接続は不変（BDY-02 の北辺の出口は頭・口の2か所のまま）。BDY-02 の内部の形（広間から北へ首が1本、上で分岐）だけを変える。

## kako-jun 決定（2026-10-22）: 左右は身体の本人から見る
「左右の考え方は、身体の本人からみてにして。本人は仰向けに寝ている。それを正面から見ている構図だ。だから画面左側は右手だ」
- 左右は**本人から見た**左右。本人は仰向けで、画面（正面から見る構図）の左側が本人の右手・右足、右側が本人の左手・左足。

## kako-jun 決定（2026-10-22、モック一覧と接続表を見て）
「心臓は自然にすればいい。肺は人間のがうずまきでないなら行き止まりなしでいいのでは。首はこれでいい。足の角度は太もも部分が１マップ内に短すぎてもったいないので曲がってる感じしてはどうか」
1. 心臓: 自然（本人の左側＝画面右）。BDY-02 の南辺は 肺=左寄り・下半身=中央・心臓=右寄り で確定。
3. 首: 現行の形（広間から首1本→上で頭・口に分岐）で確定。
[docs/map-topology.md:118]
以下は接続の向きを一意にする正本である。`→` の両側は必ず反対の画像辺とし、`door` は画像端でなく室内・階層遷移である。`event` は一方向の物語イベント、`oneway` は一方向の通常移動。`door-passage-*` は体内の抽象通路名で物理的な扉ではない。`pending` は旧仮説のID追跡だけの行で、隣接・通行路・生成契約ではない。`§3.1` 以降の旧試作時の図・発注文は履歴説明であり、ここにない辺指定を新規プロンプト、画像生成、マスクに使ってはならない。
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
[docs/map-topology.md:246]
| BDY-01.door-passage-torso | BDY-02.door-passage-mouth | door | 架空人体の抽象通路。door-passageは物理的な扉でない。上半身/下半身2枚・手各2枚・足各3枚の連続一本道 |
[docs/map-topology.md:247]
| BDY-02.door-passage-lower | BDY-03.door-passage-upper | door | 架空人体の抽象通路。door-passageは物理的な扉でない。上半身/下半身2枚・手各2枚・足各3枚の連続一本道 |
[docs/map-topology.md:248]
| BDY-02.door-passage-head | BDY-04.door-passage-torso | door | 架空人体の抽象通路。door-passageは物理的な扉でない。上半身/下半身2枚・手各2枚・足各3枚の連続一本道 |
[docs/map-topology.md:249]
| BDY-02.door-passage-left-arm | BDY-05.door-passage-torso | door | 架空人体の抽象通路。door-passageは物理的な扉でない。上半身/下半身2枚・手各2枚・足各3枚の連続一本道 |
[docs/map-topology.md:251]
| BDY-02.door-passage-right-arm | BDY-07.door-passage-torso | door | 架空人体の抽象通路。door-passageは物理的な扉でない。上半身/下半身2枚・手各2枚・足各3枚の連続一本道 |
[docs/map-topology.md:260]
| BDY-02.door-passage-heart | BDY-16.door-passage-torso | door | 架空人体の抽象通路。door-passageは物理的な扉でない。上半身/下半身2枚・手各2枚・足各3枚の連続一本道 |
[docs/map-topology.md:261]
| BDY-02.door-passage-lung | BDY-17.door-passage-torso | door | 架空人体の抽象通路。door-passageは物理的な扉でない。上半身/下半身2枚・手各2枚・足各3枚の連続一本道 |
[docs/map-topology.md:686]
## 体内の現行空間設計（#74・追加ボリューム決定）
[docs/map-topology.md:688]
TRM-01園庭→BDY-01口は一方向の物語イベント。病院・海外からの体内経路や恒常的な徒歩口ではない。胴体は縦2MAP、上半身BDY-02→下半身BDY-03。頭BDY-04は上半身の上の迷路状通路。左右の手は上半身から斜め上へ伸び、左BDY-05→BDY-06（画面右上・上半身の東辺から出て、BDY-05の西辺から入る）／右BDY-07→BDY-08（画面左上・上半身の西辺から出て、BDY-07の東辺から入る）の各2MAPの一本道。左右の足は下半身から斜め下へ伸び、左BDY-09→BDY-10→BDY-11（画面右下・下半身の東辺から出る）／右BDY-12→BDY-13→BDY-14（画面左下・下半身の西辺から出る）の各3MAPの一本道。**左右は身体の本人から見る（本人は仰向け、それを正面から見る構図。画面左が本人の右手・右足、画面右が本人の左手・左足。心臓は本人の左側＝画面右、肺は画面左。kako-jun 2026-10-22、#142）。**手足末端は閉じ、手足相互の連絡や迂回路を足さない。方向は分岐の方位であり、各手足MAPには縦方向の通路ボリュームを持たせる。
[docs/map-topology.md:690]
BDY-15胃・BDY-16心臓・BDY-17肺はそれぞれ独立したMAPで、胴体からの単純な分岐室。医学的解剖や写実的臓器ではなく、現実離れした幼稚園児の想像する架空人体の抽象概念、肌色寄りでよい。胃の盾役・エラー細胞と、心臓での水の精霊・火による復活という既存の物語を保持。BDY-02の作画契約: 口→上半身→下半身を中央主路でつなぎ、頭・左右の腕・心臓・肺を枝にする。各経路は模型（ジオラマ）の縁の辺まで届いて隣MAPへ遷移し（遷移位置は辺上の範囲指定、範囲値TBD。土台の板とまわりの机は見えたまま。接続は辺単位の判定のまま。kako-jun 2026-10-22）、洞窟状の穴や物理的な扉は描かない。体の外形を描かず、平面床と低い仕切りで道を作る。配置方位は `docs/topology/body.svg` のBDY-02接続線に従う（心臓=南東・画面右、肺=南西・画面左。南辺は肺=左寄り・下半身=中央・心臓=右寄り。BDY-16は北辺から、BDY-17は北辺中央から入る。首は広間から1本、上で頭（北）と口（北東）に分岐）。心臓・肺の部屋はBDY-02内に描かず、胃はBDY-03からBDY-15へ接続する。空間接続から新たな攻略順・肺ボス・全枝任意という条件を決めない。脳BDY-04は迷路（通路幅は人間1人分）。肺BDY-17は人間の肺が渦巻きでないため行き止まりなし（外周の環に右肺3葉・左肺2葉の抽象的な部屋、通路幅は人間1人分。形の詳細は検証の割付図が正本）。迷路形状・mask/pixel・幅・発火条件はTBD。
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
[docs/map-asset-registry.md:91]
| ID | 画像 | 地区 | 未決のため必要な個別契約 |
[docs/map-asset-registry.md:92]
|---|---|---|---|
[docs/map-asset-registry.md:111]
| BDY-01 | `BDY-01` | 抽象体内 | 口・体内入口。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。
[docs/map-specifications.md:117]
| MAP | 時期 | 一言特徴 | 方位・主路・通行条件 | 暫定固定 |
[docs/map-specifications.md:118]
|---|---|---|---|---|
[docs/map-specifications.md:119]
| BDY-01 | 中3 | 口・体内入口 | door-passage-torso→BDY-02.door-passage-mouth | 上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。
[docs/map-contract-checklist.md:11]
| ID | 状態 | Ref | mask / 出力 | 具体的TBD |
[docs/map-contract-checklist.md:12]
|---|---|---|---|---|
[docs/map-contract-checklist.md:75]
| BDY-01 | blocked | R018 | 未生成・mask未作成 | 口・体内入口。door-passage-torso→BDY-02.door-passage-mouth。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。
[docs/map-asset-registry.md:181]
| ID | 管理名 | 地区 | 契約 |
[docs/map-asset-registry.md:182]
|---|---|---|---|
[docs/map-asset-registry.md:183]
| BDY-03 | `BDY-03` | 抽象体内 | 下半身・胴体下段。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |
[docs/map-specifications.md:210]
| MAP | 時期 | 一言特徴 | 接続 | 不変条件／TBD |
[docs/map-specifications.md:211]
|---|---|---|---|---|
[docs/map-specifications.md:212]
| BDY-03 | 中3 | 下半身・胴体下段 | door-passage-upper→BDY-02.door-passage-lower、door-passage-left-leg→BDY-09.door-passage-torso、door-passage-right-leg→BDY-12.door-passage-torso、door-passage-stomach→BDY-15.door-passage-torso | 上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |
[docs/map-contract-checklist.md:145]
| ID | 状態 | Ref | mask / 出力 | 具体的TBD |
[docs/map-contract-checklist.md:146]
|---|---|---|---|---|
[docs/map-contract-checklist.md:147]
| BDY-03 | blocked | R018 | 未生成・mask未作成 | 下半身・胴体下段。door-passage-upper→BDY-02.door-passage-lower、door-passage-left-leg→BDY-09.door-passage-torso、door-passage-right-leg→BDY-12.door-passage-torso、door-passage-stomach→BDY-15.door-passage-torso。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |
[docs/map-asset-registry.md:116]
| BDY-04 | `BDY-04` | 抽象体内 | 頭・脳の迷路通路。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |
[docs/map-specifications.md:124]
| BDY-04 | 中3 | 頭・脳の迷路通路 | door-passage-torso→BDY-02.door-passage-head | 上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |
[docs/map-contract-checklist.md:80]
| BDY-04 | blocked | R018 | 未生成・mask未作成 | 頭・脳の迷路通路。door-passage-torso→BDY-02.door-passage-head。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |
[docs/map-asset-registry.md:184]
| BDY-05 | `BDY-05` | 抽象体内 | 左手通路1・付け根側。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。
[docs/map-specifications.md:213]
| BDY-05 | 中3 | 左手通路1・付け根側 | door-passage-torso→BDY-02.door-passage-left-arm、door-passage-tip→BDY-06.door-passage-base | 上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。
[docs/map-contract-checklist.md:148]
| BDY-05 | blocked | R018 | 未生成・mask未作成 | 左手通路1・付け根側。door-passage-torso→BDY-02.door-passage-left-arm、door-passage-tip→BDY-06.door-passage-base。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。
[docs/map-asset-registry.md:185]
| BDY-07 | `BDY-07` | 抽象体内 | 右手通路1・付け根側。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。
[docs/map-specifications.md:214]
| BDY-07 | 中3 | 右手通路1・付け根側 | door-passage-torso→BDY-02.door-passage-right-arm、door-passage-tip→BDY-08.door-passage-base | 上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。
[docs/map-contract-checklist.md:149]
| BDY-07 | blocked | R018 | 未生成・mask未作成 | 右手通路1・付け根側。door-passage-torso→BDY-02.door-passage-right-arm、door-passage-tip→BDY-08.door-passage-base。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。
[docs/map-asset-registry.md:118]
| BDY-16 | `BDY-16` | 抽象体内 | 心臓・分岐室。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |
[docs/map-specifications.md:126]
| BDY-16 | 中3 | 心臓・分岐室 | door-passage-torso→BDY-02.door-passage-heart | 上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |
[docs/map-contract-checklist.md:82]
| BDY-16 | blocked | R018 | 未生成・mask未作成 | 心臓・分岐室。door-passage-torso→BDY-02.door-passage-heart。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |
[docs/map-asset-registry.md:177]
| BDY-17 | `BDY-17` | 抽象体内 | 肺・分岐室。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |
[docs/map-specifications.md:206]
| BDY-17 | 中3 | 肺・分岐室 | door-passage-torso→BDY-02.door-passage-lung | 上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |
[docs/map-contract-checklist.md:141]
| BDY-17 | blocked | R018 | 未生成・mask未作成 | 肺・分岐室。door-passage-torso→BDY-02.door-passage-lung。上半身/下半身の胴体縦2MAP、手各2MAP、足各3MAP。幼稚園児の架空人体・非写実・肌色寄り。通行幅・pixel/mask・脳内迷路はTBD、blocked。 |
[注記] 通路幅は天面幅比0.14=230px。


=== WHAT TO DRAW (positive description; sentence numbers P1.. are referenced below) ===
P1. COMPOSITION. The whole picture is a hand-made tabletop miniature seen from almost straight above: a model standing on a desk. From the outside in on ALL FOUR sides (north, south, west and east alike): (a) the desk surface, a warm natural wooden tabletop with visible wood grain, a 90 px margin on all four sides of the frame, mostly clear wood (at most a few small craft leftovers lie on it, well clear of the model); (b) the model's base, seen from above as a border band 48 px wide that frames the top surface all the way around, unbroken (no side face of the model is visible); (c) inside the band, the top surface of the model, which is the map. Frame coordinates (1920x1080): the base band's outer edge is the rectangle x 90 to 1830, y 90 to 990; the model's top surface is the rectangle x 138 to 1782, y 138 to 942 (1644 x 804 px). (In the 1672x941 frame these are: band outer edge x 78 to 1594, y 78 to 863; top surface x 120 to 1552, y 120 to 821.) On every one of the four sides of the picture, going inward from the picture's edge, you see in this order at full width: the wooden desk (90 px), then the cream foamboard rim (28 px), then the brown corrugated cardboard cross-section (20 px), then the terrain. The model's top surface lies wholly inside the picture and touches none of its edges; the north and south sides show the desk, the rim and the corrugated band exactly as the west and east sides do. Nothing is drawn outside the model except the wooden desk and its few craft leftovers: no wall, no room, no sky, no horizon, no people. The model is a miniature, so the whole picture is a model; the picture never reads as a photograph of a real place.
P2. THE BASE BAND. Seen from above it is a framing border around the top surface. Its outer 28 px (x 90 to 118 along the left side, and likewise on the other sides) is the rim of a 5 mm foamboard slab (smooth pale white-cream paper-faced foam core, with the paper skin and the foam core visible along the rim). Its inner 20 px (x 118 to 138 on the left, and likewise on the other sides) is the exposed cross-section of corrugated cardboard (the wavy flute layer between two flat liners, brown), glued around the foamboard's top edge with masking tape and white PVA glue, with ragged hand-cut paper edges. The band runs unbroken along all four sides, north and south included, with both the foamboard rim and the corrugated layer clearly visible on each side. It is not interrupted where the passages reach the model's edge. A few extra strips of masking tape and small PVA drips may lie on the band, never hiding the corrugated layer over any long stretch.
P3. THE SEVEN PASSAGES AND THE MODEL'S EDGE. The model's top surface is made of thin flat paper-clay surfaces. Seven flat floor bands, each 230 px wide measured across the band (0.14 of the model's width of 1644 px, which is 200 px in the 1672x941 frame; a stand-in for three characters side by side; no character is drawn), each reach the model's edge and stop flush against the inner edge of the corrugated band of P2: the floor band ends where the model ends, at the band, and never continues onto the band, the desk or the frame edge (each leads on to the next map across the model's edge; the character stands anywhere within a stretch of the edge to cross over, so nothing marks a crossing point). No marker, coloured zone, arrow, line or label of any kind is drawn at the edges. The person whose body this is lies on their back and is seen from the front, so the picture's left (west) is that person's right side and the picture's right (east) is that person's left side. Positions where each band meets the model's edge, in the 1920x1080 frame, measured from the layout diagram (first image):
  - North edge (top, y 138), 2 passages: the head passage at x 845 to 1075 (in 1672x941: x 736 to 936) (running straight down into the neck of P5); the mouth passage at x 1239 to 1469 (in 1672x941: x 1079 to 1279) (running straight down to about y 225 (in 1672x941: y 196), then sloping down and to the left at about 17.7 degrees below horizontal into the neck of P5).
  - East edge (right, x 1782), 1 passage: the left-arm passage (the person's own left arm) at y 248 to 477 (in 1672x941: y 216 to 416) (running straight to the left to about x 1660 (in 1672x941: x 1446), then sloping down and to the left at about 26.6 degrees below horizontal into the hall of P4; the outer corner of that bend is rounded, radius 115 px).
  - South edge (bottom, y 942), 3 passages: the lung passage at x 450 to 680 (in 1672x941: x 392 to 592) (running straight up to about y 800 (in 1672x941: y 697), then sloping up and to the right at about 15.7 degrees above horizontal into the hall; the outer corner of that bend is rounded, radius 115 px); the lower-body passage at x 845 to 1075 (in 1672x941: x 736 to 936) (running straight up into the hall); the heart passage at x 1239 to 1469 (in 1672x941: x 1079 to 1279) (running straight up to about y 800 (in 1672x941: y 697), then sloping up and to the left at about 15.7 degrees above horizontal into the hall; the outer corner of that bend is rounded, radius 115 px).
  - West edge (left, x 138), 1 passage: the right-arm passage (the person's own right arm) at y 425 to 655 (in 1672x941: y 370 to 571) (running straight to the right to about x 300 (in 1672x941: x 261), then sloping down and to the right at about 16.6 degrees below horizontal into the hall of P4; the outer corner of that bend is rounded, radius 115 px).
  Along every other stretch of the model's four edges, the edge is solid raised paper-clay terrain meeting the corrugated band: the floor bands are the only floor that reaches the model's edge, 7 in all. The heart passage and the lung passage are plain floor bands like the others: nothing but floor is drawn at them or beyond them.
P4. THE HALL. In the lower middle of the model lies an open hall: a wide oval FLOOR of flat paper clay, wider than it is tall, centred at (960, 700) (in 1672x941: (836, 610)), horizontal radius 300 px and vertical radius 205 px (it spans x 660 to 1260 and y 495 to 905: 600 px wide and 410 px tall), perfectly level and flat, level with the passage floors, and the same plain floor (same cream and pale peach, no new colour). The hall floor is open and empty from edge to edge: nothing rises from it and nothing lies on it. Along four stretches of the oval's outline (listed below) stands a thin low paper-clay WALL, 22 px thick, standing OUTSIDE the floor oval, on the terrain side, never on the floor; everywhere else along the oval there is no wall and the floor continues into the passages. The wall is ONE low band of corrugated cardboard (the same build as the partitions of P6, here 22 px wide) with paper clay smoothed over its top, in the brown of corrugated cardboard, with ONE strand of yarn along its outer foot as its edging; in the first image the blue-grey arcs only mark where the wall stands, and the wall itself is cardboard brown. The wall is visible in 4 arcs only, at these bearings measured clockwise from north around the hall's centre: upper right arc: bearing 29 to 40 degrees (x 1076 to 1123, y 488 to 517; in 1672x941: x 937 to 978, y 425 to 450); lower right arc: bearing 128 to 151 degrees (x 1076 to 1175, y 861 to 912; in 1672x941: x 937 to 1023, y 750 to 795); lower left arc: bearing 209 to 232 degrees (x 745 to 844, y 861 to 912; in 1672x941: x 649 to 735, y 750 to 795); upper left arc: bearing 303 to 331 degrees (x 724 to 844, y 488 to 553; in 1672x941: x 630 to 735, y 425 to 482). On every other part of the oval's outline, one of the passage floors joins the hall floor with its full width and the floor carries on without a wall: six floor bands meet the hall, namely the neck of P5 on the north side, the right-arm passage on the west, the left-arm passage on the east, and the lung, lower-body and heart passages on the south. The hall floor is measured to the inner face of the wall arcs: the cream area of the first image is the clear floor width, so the oval keeps its full 600 x 410 px, however the wall is made. The wall never reduces the floor: it is a thin band, and it never thickens. The hall floor is plain, bare, flat floor.
P5. THE NECK AND ITS BRANCH. From the north side of the hall, ONE single neck band 230 px wide (x 845 to 1075, the same x range as the head passage) runs due north: exactly vertical, with no bend. Its lower end opens into the hall's northern edge at about (960, 495) (in 1672x941: (836, 431)). Its length from the hall to the branch point is about 145 px. At the branch point, about (960, 350) (in 1672x941: (836, 305)), the neck divides, in one single fork, into exactly two bands: (a) the head band keeps going due north at the same x range, x 845 to 1075, up to the model's north edge at y 138, where it is the head passage of P3; (b) the mouth band leaves the neck's east side: its centre line runs from the branch point up and to the right at 17.7 degrees above horizontal to about (1354, 225) (in 1672x941: (1179, 196)), where the band turns with a rounded outer corner (radius 115 px) and runs straight up to the north edge at x 1239 to 1469 (in 1672x941: x 1079 to 1279), where it is the mouth passage of P3. At the neck's east edge the opening of the mouth band spans y 192 to 432 (measured vertically): the lower edge of the mouth band meets the neck's east edge at about y 432. Between the head band and the mouth band at the north edge lies a small wedge of solid terrain (x 1076 to 1238 at the north edge) that narrows to a point at about y 192 where the two bands part from the neck. Below the branch point there is the neck alone: no second band runs beside it, and its west edge is one straight vertical line (x 845) from the north edge all the way down to the hall. Read from the hall northward, the route is: the hall, one neck, one fork, then the head band due north and the mouth band to the upper right. The mouth and the head are story role names only: each is a plain floor band, and nothing but floor bands is drawn there.
P6. PARTITIONS AND THE HALL WALL. Along the passage edges, on the terrain side of the floor outline, run LOW PARTITIONS: narrow low ridges (seen from above as narrow raised borders) made of ONE narrow, low band of corrugated cardboard each (no stacking), with paper clay smoothed over its top, which make the passages. Each partition is only about 12 px wide (in 1672x941: about 10 px) and stands entirely on the terrain side of the floor outline, on the boundary where the terrain face meets the floor; no floor colour appears outside a partition. The clear cream floor between the inner faces of the partitions keeps exactly the width of the cream area of the first image, 230 px (in 1672x941: about 200 px); the thickness of a partition is never counted inside the floor width and never eats into it. The hall's wall arcs of P4 are built the same way: ONE low corrugated cardboard band, 22 px wide, in cardboard brown, standing outside the floor oval. Outside each partition and each wall arc, on the terrain side along its foot, runs ONE thin edging strand of yarn (deep skin-tone); it lies on the terrain, never on the floor, and is never counted in the floor width. There are no doors, door frames or gates, no cave mouths, no round holes or tunnel mouths: the top of the model is only flat floors, an open oval hall with its thin wall arcs, low partitions, yarn edging and decorated terrain.
P7. THE TERRAIN. The terrain between and around the passages is a thin, flat sheet of paper clay, painted face by face in matte poster paint, the terrain warm brown-leaning skin tones, laid on with a flat brush (brush streaks and uneven coats visible), a different tone for each face. The terrain is the place for the handwork decoration of P9, which stays inside the same warm range of colours (see P8). It has no thick mounded layers, no stacked flesh-like bands, no striations and no fleshy cross-sections. The passages and the hall divide the terrain into 4 wide regions (upper left, lower right, lower left, upper right) and 3 narrow strips and wedges.
P8. COLORS: passage floors: matte poster paint in cream and pale peach, the same range everywhere. Terrain: matte poster paint, warm brown-leaning skin tones, one tone per face. COLOURS OF THE DECORATION: every decoration item is coloured only within skin tone, pale pink, cream, ivory and brown shades (yarn and thread: light to deep shades of cream, pale pink and skin tone; paper-clay items: cream, pale pink, skin tone or light brown; toothpicks: natural wood). The red of the six origami pieces of P10 is the only other colour in the model, and the desk is natural wood. So the whole model reads as one warm family of skin, pale pink, cream and brown. The edging yarn is deep skin-tone. The desk is warm natural wood (warm medium-brown grain with fine straight lines). Partitions: corrugated cardboard strips with paper clay on top, in brown and skin tones.
P9. DECORATION (small hand-made ornament about the human body, secondary to the geometry). Leading motifs: (1) pulse lines: cream or pale pink wool yarn glued down as jagged zigzag lines, in short separate pieces; (2) muscle and nerve threads: short separate bundles, twisted cords, spirals and coils of wool yarn in cream, pale pink and skin tones, each strand on its own, never joined into a net and never branching; (3) skin texture carved into the paper clay with a toothpick: fingerprint-like swirls of concentric lines, fields of tiny pore dots, short parallel curved wrinkle lines. Only as small supporting touches: a few tiny spiky clay balls; a few small tufts of thread hair; a few tiny ball-ended bones. WHERE: only on the terrain faces of the 4 wide regions, along the foot of the partitions and of the hall wall arcs, on the edge of the base band and on the desk; the cream floors and the hall floor stay clear (P11). ARRANGEMENT: SCATTERED: small groups spread evenly over every terrain region, no two groups alike. EDGE: the edging yarn at the foot of the partitions is deep skin-tone; the base band's masking tape is cream and its PVA white. THE DESK: warm wood grain; around the model lie a few thread ends and a small clay crumb along the lower desk margin (few and small; nothing covers the base band). DENSITY at kindergarten-craft level: each of the 4 wide regions shows 3 to 5 kinds of small items, at least 6 groups over the terrain; the narrow strips and wedges (such as the wedge between the head band and the mouth band) carry only a thin edging of yarn. The geometry in P3 to P6 (floor widths, the single neck, the branch, the hall) always has priority over decoration.
P10. RED ORIGAMI: EXACTLY SIX (6) hand-cut red paper pieces with uneven edges (cut with scissors from red origami paper, flat on the surface, glued with PVA), no more and no fewer: count them, six, with no seventh and no spare piece anywhere. Exactly six red origami pieces, each about 45 px across: two in the lower left terrain region, about (250, 800) (in 1672x941: (218, 697)) and (380, 880) (in 1672x941: (331, 767)); two in the upper left terrain region, about (300, 230) (in 1672x941: (261, 200)) and (600, 330) (in 1672x941: (522, 288)); one in the lower right terrain region, about (1560, 780) (in 1672x941: (1358, 680)); one in the upper right terrain region, about (1620, 190) (in 1672x941: (1411, 166)) (six in total), all on terrain faces inside the model (x 138 to 1782, y 138 to 942; in 1672x941: x 120 to 1552, y 120 to 821), none on any floor, wall, rim or desk, none anywhere outside the model. Their outlines are irregular and unequal, not drawn as any particular symbol; they are clean paper cut-outs, never blood stains or liquid. They are the only red objects in the picture. Nothing of P9 is laid over them: they are not a base for ornament.
P11. THE FLOOR STAYS EMPTY. Nothing of P9 lies on the cream floor, crosses into it or touches it: the floors and the hall floor stay perfectly flat, clean and empty, nothing is placed where the characters walk, and the width of the passages, the shape of the hall and the flatness of the floor are exact. The surfaces of the model are flat floors, walls and decorated terrain only.
P12. MATERIALS (every material must be identifiable at full size): base: 5 mm foamboard with the corrugated cardboard cross-section band described in P2; terrain surface: paper clay modelled by hand; partitions (12 px) and the hall wall arcs (22 px): one low corrugated cardboard band each under smoothed paper clay, with one strand of yarn along the foot; floors and terrain: matte poster paint applied with a flat brush; the joint of the band: masking tape; decoration: wool yarn and thread (zigzag lines, muscle threads, hair tufts), toothpick-carved patterns in paper clay, small paper-clay balls with toothpick spikes, toothpicks with clay ends, white PVA glue; accents: 6 pieces of red origami paper cut by hand with scissors; desk: wooden tabletop with visible wood grain. Hand-made roughness: ragged hand-cut paper edges, paint unevenness, visible material seams. Parts look like paper and clay (matte, soft edges). It reads as a crude hand-made miniature in which the whole picture is the model, and not as a photograph of a real place.
P13. CAMERA: the camera looks down steeper than 45 degrees from horizontal, as close to straight down as possible, never lower than 45 degrees from horizontal. North is the top of the image. Flat evenly lit tabletop light. The picture has no sky, no horizon, no vanishing point, no people, no characters, no readable text, no letters, no numbers, no logos.
P14. DIMENSIONS: request 1920x1080 (16:9). If the tool cannot return it, 1672x941 is acceptable (every coordinate above then scales by 0.871; the 1672x941 values are given alongside). Any other size is a failure; never resize or crop to pass. Measure the real output file.

=== REFERENCE (two attached images, in this order) ===
FIRST IMAGE: a flat layout diagram with five plain flat colours and no text. Its colours mean: grey = the desk; ochre-brown band = the base band's edge (P1, P2); dusty rose-brown inside the band = the model's top terrain (P7); light cream = the walkable floor of the seven passages and of the hall (P3, P4, P5); blue-grey arcs = the places where the hall's wall stands (P4), standing outside the cream floor oval. Copy ONLY the geometry exactly: the nesting of desk, base band (foamboard rim, then corrugated layer) and model top on all four sides, the number of passages (7), the model's edge each reaches, the position along that edge, the band width, the outline of each band including its slopes and bends, the single vertical neck and its fork into the head band and the mouth band, and the hall's centre, floor oval and wall arcs. Treat the cream area as the clear floor width: the walls and partitions stand in the terrain area next to it, never inside the cream. Repaint everything as the hand-made miniature described above: the wall arcs become thin cardboard-brown walls (P4). Do NOT carry over the diagram's five flat colours as flat fills (the desk is a warm wooden tabletop, the base band is foamboard and corrugated cardboard, there is no flat brown area anywhere in the result, and no blue-grey) or its perfectly straight, hard edges.
SECOND IMAGE: a thin close-up strip of the front edge of a hand-made cardboard miniature base. Take from it ONLY the feel of three materials, to be used for the base band of P2: the exposed corrugated cardboard cross-section (the wavy flute layer along the top of the strip), the masking tape, and the ragged torn paper edge. Take no content from it, and ignore the few white cotton fibres at its top edge and its brown colour. The decoration of P9 is described by the text only: no attached image carries any decoration to copy.
```

## 4. 原文 → prompt 中の対応文 照合表

| 原文（逐語の断片。束に存在を確認済み） | 出典 | prompt 対応文 |
|---|---|---|
| 手足末端は閉じ、手足相互の連絡や迂回路を足さない | topology | P3, P4, P5（余計な経路・迂回路を足さない。末端は閉じる） |
| 幼稚園児の架空人体・非写実・肌色寄り | registry/spec/checklist | P6（体の輪郭・洞窟口なし。平らな床・低い仕切り・地形だけ）, P7, P8 |
| door-passageは物理的な扉でない | topology | P6（扉・枠・門なし） |
| 通行幅・pixel/mask・脳内迷路はTBD | registry/spec/checklist | P3（幅 230px は割付図の仮置き。画素値はTBDのまま） |
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
| 接続（door-passage-head→BDY-04.door-passage-torso、door-passage-mouth→BDY-01.door-passage-torso、door-passage-left-arm→BDY-05.door-passage-torso、door-passage-lung→BDY-17.door-passage-torso、door-passage-lower→BDY-03.door-passage-upper、door-passage-heart→BDY-16.door-passage-torso、door-passage-right-arm→BDY-07.door-passage-torso） | spec / topology の接続列 | P3（辺・位置は割付図の実測） |

## 5. 割付図の実測（`clean/BDY-02.png`。1920x1080 と ×0.871 の 1672x941）

- 構図: 机90px・土台縁48px（foamboard 28 + corrugated 20）・天面 x138–1782 y138–942（1644x804）。通路幅 230px（1672: 200px）。
- 経路の形: 広間（横長の楕円の床。壁は細い arc）→ 首1本 → 分岐点 → 頭・口。広間: 中心 (960, 700)・横半径300・縦半径205・壁厚22（clean の壁色画素に楕円を当てた実測。body_layout の定数と一致を確認）。
- 壁の弧: upper right 方位29–40度 x1076–1123 y488–517; lower right 方位128–151度 x1076–1175 y861–912; lower left 方位209–232度 x745–844 y861–912; upper left 方位303–331度 x724–844 y488–553。
- 首: 行ごとの床の区間が x 845–1075 の1本（頭の通路と同じ x 区間）。分岐点 y 350（口の帯の中心線が x=首の中心を通る高さ）。口の帯 水平から17.67度、折れ y 225。首の東縁の開口 y 192–432。頭と口の間のくさびの先端 y 192。
- door-passage-left-arm: 斜め26.59度、折れ位置 x 1660。
- door-passage-lung: 斜め15.70度、折れ位置 y 800。
- door-passage-heart: 斜め15.73度、折れ位置 y 800。
- door-passage-right-arm: 斜め16.58度、折れ位置 x 300。
| 辺 | port | 区間（1920） | 区間（1672x941） | 幅 | 折れ線（1920座標） |
|---|---|---|---|---|---|
| N | door-passage-head | x 845–1075 | x 736–936 | 231 | (960,350), (960,138) |
| N | door-passage-mouth | x 1239–1469 | x 1079–1279 | 231 | (960,350), (1355,225), (1355,138) |
| E | door-passage-left-arm | y 248–477 | y 216–416 | 230 | (1782,363), (1662,363), (1090,650) |
| S | door-passage-lung | x 450–680 | x 392–592 | 231 | (565,942), (565,800), (760,745) |
| S | door-passage-lower | x 845–1075 | x 736–936 | 231 | (960,942), (960,800) |
| S | door-passage-heart | x 1239–1469 | x 1079–1279 | 231 | (1355,942), (1355,800), (1160,745) |
| W | door-passage-right-arm | y 425–655 | y 370–571 | 231 | (138,540), (300,540), (800,690) |

地形の区画（連結成分）: upper left（広、面積約238384px、bbox (140, 140, 844, 544)）; lower right（広、面積約144224px、bbox (1316, 480, 1780, 940)）; lower left（広、面積約86592px、bbox (140, 656, 484, 940)）; upper right（広、面積約64000px、bbox (1076, 140, 1780, 500)）; lower centre（狭、面積約9120px、bbox (680, 872, 844, 940)）; lower centre（狭、面積約8896px、bbox (1076, 872, 1236, 940)）; upper centre（狭、面積約4688px、bbox (1076, 140, 1236, 188)）

## 6. 寸法・検査項目（生成後。生画像レビュー用）

寸法（`file` / `identify` で実ファイルを測る。prompt指定・ファイル名は証拠にならない）:
- [ ] 1920x1080、または 1672x941（その場合は座標に0.871を掛けて比較）。それ以外は failed。リサイズ・切り抜きで通さない。

構図（割付図 `verification/body-layout/clean/BDY-02.png` と実画素・目視で比較）:
- [ ] 机（木目の木の机）が四辺に約90px見える。その内側に約48px幅の土台縁の帯（外28px foamboard・内20px corrugated 断面）が**四辺すべて（北・南・西・東）**で途切れず見える。模型の天面は画像の内側に収まる。天面は x138–1782・y138–942 付近。
- [ ] 通路が模型の縁（土台縁の帯の内側）に届く。画像端（机の外）に通路が出ていない。床は模型の外に一画素も無い。

通路:
- [ ] 通路は**7本**（北2・東1・南3・西1）。
- [ ] N辺 door-passage-head: x 845–1075（1672: x 736–936）、幅約230px（1672: 約200px）。
- [ ] N辺 door-passage-mouth: x 1239–1469（1672: x 1079–1279）、幅約230px（1672: 約200px）。
- [ ] E辺 door-passage-left-arm: y 248–477（1672: y 216–416）、幅約230px（1672: 約200px）。
- [ ] S辺 door-passage-lung: x 450–680（1672: x 392–592）、幅約230px（1672: 約200px）。
- [ ] S辺 door-passage-lower: x 845–1075（1672: x 736–936）、幅約230px（1672: 約200px）。
- [ ] S辺 door-passage-heart: x 1239–1469（1672: x 1079–1279）、幅約230px（1672: 約200px）。
- [ ] W辺 door-passage-right-arm: y 425–655（1672: y 370–571）、幅約230px（1672: 約200px）。
- [ ] 他の縁の区間には床が出ていない。遷移範囲の印（色帯・矢印・線・文字）が絵に無い。

経路の形（本命の検査。割付図の実測値）:
- [ ] 広間: 横長の楕円の床（中心(960,700)・横半径300・縦半径205）。床は平らで空。台座が無い。壁は細い段ボール茶の帯（厚み約22px、青灰でない）の弧が4か所だけ見え、他は帯が床に接する。壁が太って床を削っていない。
- [ ] 首は広間の北から**1本**（x 845–1075、真北、曲がりなし）。分岐点 (960,350) の上で頭（真北）と口（右上へ約17.7度→y 225 で辺へ垂直）に分かれる。分岐点より下に2本目の帯が無い。
- [ ] 西辺=右腕・東辺=左腕・南辺=肺（x450–680）・下半身（x845–1075）・心臓（x1239–1469）。左右は本人から見る（画面左=本人の右）。口・頭・肺・心臓に唇・歯・舌・頭蓋・臓器の造形が無い（通路の名前だけ）。

材料・質感・装飾（装飾込み1回生成）:
- [ ] ① 土台縁の帯に corrugated cardboard 断面と foamboard の縁 ② 仕切りと広間の壁が細く低い corrugated の帯1本＋毛糸の縁取り1本（床の幅に含まれない）
- [ ] ③ 地形が paper clay の面で、肌色・薄桃・茶系の matte poster paint ④ 赤い折り紙の切片が**ちょうど6枚**（全て模型の中の地形の上。壁・床・土台縁・机に無い）
- [ ] ⑤ 机が木目の木の机
- [ ] ⑥ 装飾は人体に関係する抽象的な工作物だけ（骨・細胞や粒・筋肉や神経の糸・鼓動のぎざぎざ線・皮膚の彫り・ばんそうこう・毛・ばい菌）。少なくとも6か所の塊・各塊3〜5種。花・葉・雲・星・旗・柵・ハート形・動物・食べ物・風景・臓器の形・血管の網が無い。フェルトの花が無い
- [ ] ⑥b 装飾の色が肌色・薄桃・クリーム・茶系・象牙色の範囲（緑・青・黄・紫・オレンジが無い）。赤は折り紙6枚だけ
- [ ] ⑦ 床（クリームの通路・広間）には何も置かれず平ら。毛糸が血管・臓器に見える走り方をしていない

許容差（レビュー側基準。生成入力には入れない）: 通路位置 ±25px、幅 ±10%（1672x941 の場合は ×0.871）。床マスクIoU（clean 割付図に対して）≥0.95 を目安。
