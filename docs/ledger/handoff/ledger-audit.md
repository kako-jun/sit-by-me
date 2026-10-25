# sit-by-me MAP台帳の分散・重複の実態と統合案

調査対象: <repo> (branch oblique-mask-tools-20261023)。読み取りのみ・リポ無変更。
根拠は「確認」(ファイル/行/コマンド出力で確認) と「推測」に分けて書く。Issue 全文は i51.txt / i144.txt (同ディレクトリ) に保存。

## 1. 台帳の一覧と役割

| ファイル | 保持する情報(MAP単位) | 形式 | 読む主体 |
|---|---|---|---|
| docs/topology/map-ids.json, areas.json | MAP ID 一覧・エリア所属 | JSON | verify_map_ledger.rb (L22,25,161) |
| docs/map-contract-checklist.md (58KB) | 1行/MAP: status(ready/blocked/recreate-required…)・参照R番号・マスク/出力・TBD・接続メモ・没記録・時期差分(-kids/-fire) | md表 | build_map_prompt.rb (status, tbd の2セルのみ), verify_map_ledger.rb |
| docs/map-specifications.md (60KB) | 1行/MAP: 時期・一言特徴(feature)・必須ルート・固定制約 | md表 | build_map_prompt.rb (era/feature/route/fixed を prompt に出す), verify |
| docs/map-topology.md (94KB) | MAP相互接続台帳 v2(`TRM-04.door-west` 等のedge)、地形不変条件、エリア図 | md表+散文 | build_map_prompt.rb(「MAP相互接続台帳 v2」節を抽出), verify, render_*.rb |
| docs/map-asset-registry.md (45KB) | 1画像1行: 画像パス・status(legacy/retired)・特徴・時期別方針・採用記録リンク | md表 | verify_map_ledger.rb。build_map_prompt.rb は読まない |
| docs/teramachi-rebuild-candidates.md | 寺町の再構築候補画像・接続の写し | md表 | verify(推測: 一部) / 人間 |
| docs/map-reference-research.md | 参照資料 R001… | md | verify (R番号の存在確認) |
| docs/decisions.md (210KB) 他 art-direction/story/systems/monsters… | 設計決定の逐語・日付(物語・美術の決定、MAP制作の決定が混在) | md | 人間のみ。機械は読まない |
| docs/production/*.md, *-prompts/ | 採用記録・送信文・sha256・没記録(日付つき一回性の記録) | md | 人間 |
| docs/production/oblique-mocks/<MAP>-plan.json | 平面スペック(sit-oblique-plan/1): 床・壁・戸口・家具箱・窓・`look`(見た目)・`decor_pool` | JSON(手書き) | oblique_build.py → モック/マスク/オクルージョン/edit-prompt |
| oblique-mocks/decor-pools.json | 装飾プール+エリア固定(机・木・台座)。禁止語・床材の方針文 | JSON(手書き) | oblique_build.py L40-163, oblique_e2_measure.py |
| oblique-mocks/connections*.json, connections.md, windows.md, decisions-checklist.md, dependency-*.json | 接続・窓一覧・承認待ち決定・依存順 | JSON/md | oblique_build.py(connections), 人間(他) |
| oblique-mocks/<MAP>/manifest.json | ステージ別 input_sha・出力。`ledger.row_id` を既に持つ(oblique_build.py L626) | JSON(生成物) | oblique_build.py |
| .claude/skills/sit-field-background/{SKILL,gates,pitfalls}.md | 手順・過去の決定(kako-jun 2026-10-23 の視点・幅・テイク数など) | md | エージェント |
| docs/issue-map.md | Issue→決定の索引 | md | 人間 |

観察: MAP の 1 項目(例 TRM-05)の情報が、checklist / specifications / topology / registry / candidates / decisions(物語側) / plan / decor-pools / connections / windows.md / manifest / skills の最大12箇所に散る(確認: TRM-05 を grep した結果)。

## 2. 重複・食い違い(確認済み実例)

| # | 情報 | 重複箇所 | 食い違い/漏れ |
|---|---|---|---|
| D1 | TRM-05 の寝室方針(-kids は寝室1つ、小学生から2つ、時期別は同一ID差し替え) | map-asset-registry.md:62, map-specifications.md:20, map-contract-checklist.md:23 の3表に同文を丸写し | 3箇所の同期が手作業。1つ直すと残りが古くなる |
| D2 | 床材(畳) | Issue #51 (2026-10-21「畳をやめる」)・decor-pools.json:31,58,119・TRM-05-plan.json の look | **台帳が逆**: map-specifications.md:46「仏具の鈍い金と畳が対照になる本堂」、map-contract-checklist.md:57「畳・仏具と主路」、map-topology.md:290「畳廊下」が残存。#51 コメント(L491)は「畳の語は書き換えず『要整合』注記」としたが、台帳の畳は未修正のまま。plan/decor 側だけが正 |
| D3 | 勝手口 TRM-05.door-back ↔ TRM-06.door-house | Issue #144(位置: 北壁左端・幅1人分・-fireで焼失)、plan.json、connections.json | **台帳に無い**: map-specifications.md:18「TRM-05への勝手口の扉はTBD」、map-topology.md:128「台帳になく TBD」、checklist:23 も記述なし。決定が台帳に降りていない |
| D4 | 化石の石の色 | TRM-05-plan.json:374 と TRM-05-edit-prompt.txt のみに「茶色と黒の混ざった石(割っていない・拳ほど・アンモナイト模様は描かない)」。Issue #51:444「化石の形・大きさは原文に無い、TBD」 | `grep -rl 茶色と黒 docs .claude` はplan と生成prompt だけ。台帳(docs/*.md)にゼロ。台帳側はTBDのまま、story.md:295 は「中身不明」までしか書かない |
| D5 | 戸口幅 | plan.json(2人分132 / 外への戸口1.5人分100 / 勝手口66)、SKILL.md「決定」節(width_class) | 台帳は map-specifications.md:47「幅・正確な位置TBD」、checklist:58「幅TBD」、candidates:27「扉の幅・正確な位置TBD」のまま |
| D6 | 木の種類 | decor-pools.json:47,56,142(寺町の木は松と枯木の2種。kako-jun 2026-10-23) | 台帳 md(specifications/registry/topology)に寺町の木の記述が見つからない(grep)。Issue #51:275,290 は「木は描かせない・原文に根拠なし」→後に変更。経緯がどの台帳にも1箇所に統合されていない |
| D7 | 窓(個数・位置・種別) | windows.md、plan.json の windows[] | 台帳に窓の列が無い。windows.md:16-20,46 に「本堂に窓は置かない(2026-10-23)」→台帳には無い |
| D8 | 戸口の位置 | map-topology.md edge、map-specifications.md、candidates、checklist の4表に同じ「西壁側・上下の中央より下寄り」を複写 | plan.json は画素矩形(例 door-hall [1190,413,1195,592])。人間の文章と座標の対応を検証する仕組みなし |
| D9 | 決定の逐語 | decisions.md(物語)・Issue コメント・SKILL.md(2026-10-23 決定)・decor-pools の note に分散 | MAP制作の決定の正本がどこか不明。SKILL.md「決定」節は寺町斜め視点の共通決定を抱え込んでいる |
| D10 | edit-prompt の台帳ゲート | oblique_build.py:588 ledger_gate は build_map_prompt.rb を呼ぶだけ | TRM-05-edit-prompt.txt:135-136 が「BLOCKED(原文束は未取得)」。台帳が recreate-required で ready でないため、**台帳原文は edit-prompt に1語も入らない**。prompt は plan+decor-pools だけから決定論で生成されている |

## 3. 情報の流れの現状

```
決定(kako-jun発言) ─→ Issue コメント(#51/#144。逐語記録)
                      ├─(手動)→ plan.json の look / decor-pools.json / connections.json / windows.md
                      ├─(手動・不完全)→ 台帳 md(checklist/spec/topology/registry/candidates)
                      └─(手動)→ SKILL.md の「決定」節
oblique_build.py: plan + decor-pools + connections ─(決定論)→ モック/マスク/occlusion/edit-prompt
build_map_prompt.rb: checklist(status,tbd)+spec(era,feature,route,fixed)+topology edges → 原文束
   → status が ready でなければ BLOCKED (D10)。ready であっても、台帳の自由文 notes(checklist の「メモ」列、registry、decisions) は読まない
```

漏れの発生点:
- 畳: 決定は Issue #51 → decor-pools/plan の「畳は描かない」に入った。台帳(spec:46, checklist:57, topology:290)には畳が残り、台帳→prompt の経路は D10 で閉じている。**今回の「漏れ」は、実は prompt が台帳を読んでいない構造(経路が plan/decor だけ)と、台帳側の更新が手動で漏れる構造の両方**。
- 化石の石: 決定が plan.json の `look` にだけ書かれ、台帳に書かれなかった(D4)。新たに別 MAP(例 -fire 差分)を生成するとき、台帳を見ても出てこない。
- 勝手口: Issue → plan/connections に入ったが、台帳の「TBD」表記は残った(D3)。台帳を見る人・build_map_prompt.rb は存在を知らない。
- 推測: 「プロンプトから決定が漏れる」の根は、(1) 台帳が生成入力になっていない(D10)、(2) plan.json の `look` 等が自由文で決定を直接保持している、(3) Issue に書いた決定を台帳へ降ろす強制が無い、の3点。

## 4. 統合案

### 方針
台帳(docs/ の md)が入口かつ唯一のマスター。JSON/prompt などの派生物は作ってよい(kako-jun「JSONを作るのはいいが台帳から参照できるように」)。ただし (i) 台帳の行から全成果物へパスで辿れる、(ii) JSON に載せてよいのは機械が読む構造(座標・寸法・個数・ID)、(iii) 決定の文は台帳にだけ書き、JSON には台帳アンカー参照を持たせる。

### (a) マスターの割当(MAP 1箇所ずつ)

| 情報 | マスター | 他は |
|---|---|---|
| MAP の存在・エリア | topology/map-ids.json(現状維持) | 参照 |
| 一言特徴・時期・必須ルート・固定制約・材料/見た目の決定(床材・木・窓方針・石の色・禁止) | **map-specifications.md を「MAP仕様」の唯一のマスターに格上げ**。1MAPに複数の決定行を持たせる(下記の決定ブロック) | checklist/registry/candidates は書かない |
| 接続(edge)と戸口の向き・位置の自然言語 | map-topology.md の edge 台帳 v2 | spec/candidates/checklist の複写を削除し「→topology」 |
| 作業状態(status・TBD・没・採用・sha256) | map-contract-checklist.md | 他に書かない |
| 画像ファイルの所在・時期別の差し替え | map-asset-registry.md | 同上 |
| 座標・寸法・個数(機械が読む構造) | plan.json / connections.json / decor-pools.json (JSON) | 台帳の ID/アンカーで紐づけ、決定文は持たない |
| 物語・美術の上位決定 | decisions.md(物語/美術) | MAP制作の決定は spec に降ろし、decisions はそこへリンク |
| 経緯・没・日付つき一回性の記録 | docs/production/*.md | 台帳の行からリンク |

### 台帳に追加する構造(推奨: map-specifications.md の各MAPに「決定ブロック」+ checklist/registry に「成果物リンク」列)

決定ブロック(MAP 1つにつき、表の下に機械が読める構造化行。md のまま維持。ID は安定):
```
<!-- decision:TRM-05.floor -->
- TRM-05.floor | 2026-10-21 | #51 | kako-jun「畳がすごく不自然だ…」 | 床は板張り(または細長いロールござ)。畳は描かない | tags: floor, forbid:畳
<!-- decision:TRM-05.fossil -->
- TRM-05.fossil | 2026-10-23 | #144 | kako-jun「…」 | 化石の石はゴツゴツした茶色と黒の混ざった石(割っていない・拳大・渦巻き模様なし) | tags: object
<!-- decision:TRM-05.door-back -->
- TRM-05.door-back | 2026-10-23 | #144 | 「勝手口は上辺の左端だ」「キャラ１人分の幅」 | 北壁左端・幅1人分・相手 TRM-06.door-house・-fire で焼失 | tags: door
```
列 = `決定ID(MAP.キー) | 日付 | 出典Issue | 逐語 | 決定内容(1文) | tags(prompt出力要否、禁止語)`。

成果物リンク(map-contract-checklist.md に新列 `成果物` を追加。1MAP=1セルに key:path をカンマ区切り。時期差分は suffix):
```
| TRM-05 | recreate-required-… | … | plan:oblique-mocks/TRM-05-plan.json, decor:oblique-mocks/decor-pools.json#teramachi-winter, conn:oblique-mocks/connections.json, windows:oblique-mocks/windows.md#TRM-05, manifest:oblique-mocks/TRM-05/manifest.json, prompt:oblique-mocks/TRM-05/TRM-05-edit-prompt.txt, image:assets/images/fields/reference/… |
```
JSON 側の逆参照スキーマ(決定文を重複保持しない):
```
plan.json:   "ledger": {"map_row": "TRM-05", "decisions": ["TRM-05.floor","TRM-05.fossil","TRM-05.door-back"]}
             boxes[i].look は廃止または "decision_ref": "TRM-05.fossil"(文は台帳から展開)
             doors[i]: {"id":"TRM-05.door-back","edge_ref":"topology:TRM-05.door-back","width_class":"1p"}
decor-pools.json: pools.teramachi-winter.rules[i] = {"decision_ref":"TRM-05.floor"}(禁止語は台帳の tags forbid: から導出)
connections.json: edges[i].topology_ref = "TRM-06.right⇄TRM-16.left" (topology の edge 行を指す)
manifest.json:   "ledger": {"row_id","decision_hashes":{"TRM-05.floor":"sha8"}}(既存 L626 の ledger キーを拡張)
```
座標・寸法・個数・幅クラス(数値)は JSON に残す。「何を描くか・描かないか」の文は台帳。

### (b) 重複の削除
- D1: 寝室方針は specifications の決定ブロック1箇所に。registry/checklist は `→ spec:TRM-05.bedroom`。
- D5/D8: 戸口幅・位置の自然言語は topology edge に1行、他は削除。TBD は plan の確定値に置換して台帳側の「TBD」文言を消す。
- D2/D3: 畳の語を spec:46/checklist:57/topology:290 から決定ブロックに沿って書き直す(要整合注記を終わらせる)。
- registry/candidates/checklist の同文の丸写しは「→ リンク」化。candidates.md は、成果物リンク列に統合して廃止も検討(推測: 内容の大半が重複)。

### (c) 派生物の機械導出
- `scripts/build_ledger_json.rb`(新) が specifications の決定ブロック+topology edge を読み、`oblique-mocks/ledger-derived/<MAP>.json` を出す(決定ID→文、禁止語リスト、edge 一覧)。
- oblique_build.py の edit-prompt は、台帳から導出した上記 JSON を読んで FILL/FORBID/DOORS 節を組む。`look`・decor-pools の決定文の直書きを減らし、plan には `decision_ref` だけ置く。ledger_gate(L588)は「ready でなければ原文束省略」から、「決定ブロックは status に関係なく必ず入れる」に変える(D10 の解消。現状は BLOCKED 時に台帳が1語も入らない)。
- 検証(verify_map_ledger.rb に追加): (1) plan/decor/connections/windows にある `decision_ref` が全て台帳に存在、(2) plan.look 等に「決定ブロックと無関係な自由文」があれば警告→エラー(第3段階)、(3) 台帳に決定ブロックがあるのに plan で一度も参照されない決定はエラー。

### (d) Issue は仮、の運用担保
- 規則: 決定を受けたら先に台帳(決定ブロック)に書き、Issue コメントは `台帳: spec:TRM-05.floor` の参照だけ。
- スキル(sit-field-background SKILL.md 冒頭に追加): 「決定を受けたら: ①決定ブロックを書く ②verify_map_ledger.rb ③`oblique_build.py` を再実行 ④Issue に参照を書く」。工程0〜12 の各工程の入力に「決定ID」を含める。
- verify_map_ledger.rb: `gh` 依存を避け、docs 内の「Issue #N 逐語」表記を検出する弱い検査(出典Issueが空の決定ブロックをエラー)。Issue→台帳の突合は SKILL に「PR/コメント投稿前チェックリスト」として置く(機械化は難しい。推測)。
- 成果物リンクの検査(kako-jun追加条件): checklist の `成果物` 列の全パスが存在すること(リンク切れ検出)、`docs/production/oblique-mocks/` と各 MAP ディレクトリにある JSON/manifest/prompt が、いずれかの MAP 行から参照されていること(台帳に無い JSON の存在を検出。`*-plan.json`・`decor-pools.json`・`connections*.json`・`windows.md`・`*/manifest.json`・`*-edit-prompt.txt` を glob)。生成物(PNG 等)は対象外にして除外パターンを `docs/production/.ledger-ignore` に持つ。

### (e) 台帳→prompt 漏れの回帰テスト
- `scripts/verify_prompt_reflects_ledger.rb`(新): 各 MAP の決定ブロックの `tags: forbid:`・`must:` から語(例 畳を描かない=禁止語リスト、「茶色と黒」=必須語)を取り、生成済み `*-edit-prompt.txt` に必須語が含まれる/禁止語が肯定形で含まれないことを検査。決定ID→prompt 行の対応をテストの出力にも出す。
- 逆検査: prompt 中の `look:` 由来の文が、台帳の決定ブロックまたは plan の `decision_ref` に辿れること(辿れない自由文を警告)。
- CI(推測: 現リポの workflow 状況は未確認)に verify_map_ledger.rb と上記2本を足す。

## 5. 移行手順と影響

段階1(最小・効果最大): **ledger_gate の解消+決定ブロックの導入+成果物リンク列+リンク検査**
1. TRM-02〜05(+06 勝手口)分の決定を Issue #51/#144 から拾い、specifications に決定ブロックとして書く(畳、化石の石、勝手口、木=松と枯木、本堂に窓なし、戸口幅クラス、寝室方針)。D2〜D7 を同時に直す。
2. checklist に `成果物` 列追加。verify_map_ledger.rb にリンク切れ/孤立 JSON 検査を追加。
3. oblique_build.py の edit-prompt に、決定ブロックを status 非依存で出力。
- 壊れうる箇所: build_map_prompt.rb は行を `|` split と固定列位置で読む(L36-48)→ 列追加は末尾に限り、既存セル番号を変えない。verify_map_ledger.rb の表パースも同様(L38 付近)。manifest の `input_sha` に台帳ハッシュを足すと既存の全ステージが再生成扱いになる(想定内)。docs: SKILL.md「決定」節の寺町共通決定は spec のエリア決定ブロックへ移す(第3段階)。
- 最も効果が大きいもの: 手順 3(台帳が必ず prompt に入る)+手順 1(寺町の決定を台帳に降ろす)。今回の漏れ3件は全てこれで塞がる。

段階2: plan/decor-pools/connections に `decision_ref` を導入し、look/決定文の直書きを台帳参照に置換、verify に参照整合を追加。
段階3: ledger-derived JSON をビルダー入力に切替、`look` の自由文を禁止、重複(D1,D5,D8)を削除、candidates.md の統合/廃止、SKILL.md の決定節を移管。回帰テスト(e)を CI へ。
段階4: 寺町以外のエリアへ展開(旧エリアの md 行は既存のまま、新規制作時に決定ブロックを書く。全件の遡及はしない)。

## 6. kako-jun に決めてほしい点(推奨つき)

1. 決定の置き場: MAP制作の決定を `map-specifications.md` の「決定ブロック」に集約し、decisions.md(物語・美術)にはリンクだけにする。推奨: はい(MAP別のため、既存の spec 行と同じ場所で読める)。代案=新規 `docs/map-decisions.md`(spec が肥大するのを避ける)。
2. `legacy` status の廃止(map-asset-registry.md が既に「要確認・kako-jun判断待ち」と明記)と candidates.md の統合/廃止。推奨: candidates.md は成果物リンク列に統合して廃止、legacy は寺町以外が上書きで置き換わった時点で消す。
3. edit-prompt への台帳取り込みの強さ: 決定ブロックを status 非依存で必ず prompt に含める(推奨)か、ready の MAP だけにするか。推奨は前者(今回の漏れは status が ready でなくても prompt が作られたから起きた)。
