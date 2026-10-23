# 斜め視点マスクの入力・結果（寺町 TRM-02〜05。#144）

ツール: `.claude/skills/sit-field-background/tools/oblique_register.py`・`oblique_mask.py`（使い方は同ディレクトリの README 区分C）。決定は `.claude/skills/sit-field-mask/SKILL.md` の「斜め視点のエリア」。

| ファイル | 内容 |
|---|---|
| `<MAP>-input.json` | 入力（人が書く）。床の4点・縦横比・blocked/assist 多角形・出口・NPC |
| `<MAP>-oblique-register.json` | 位置合わせの結果（行列・縦横比の検証。ツールが出す） |
| `<MAP>-oblique-result.json` | マスクの結果（床・blocked・出口・NPC の判定。ツールが出す） |

マスク本体と確認画像は `assets/images/fields/masks/<MAP>-{traversal-edit,mask,mask-overlay}.webp`。採用画像は作業ツリーに無いので、git 履歴（TRM-02=`9652459` の teramachi-kindergarten-hall）から取り出して `--image` に渡す。台帳の status は変えない。

## 入力JSON（`sit-oblique-input/1`）の作り方（本堂・住居・外装へ展開するとき）

1. `map_id`・`image.expected_size`（採用画像の実寸。本堂は 1672×940）。
2. `rooms[]`: 部屋（床の高さが違う帯は別の room）ごとに `quad`（床＝壁の足元の4点を 左上・右上・右下・左下の順で画素指定）と `plan_aspect.w_over_h`。縦横比の `source` は、台帳・設計書の寸法なら `"ledger"`、既知の円から決めたなら `"circle:<円のid>"`（後者の円は循環検証と出る）。`circles[].outline` は円形の物の天板の縁の点（6倍程度に拡大した切り抜きで人が拾う）。`lines[]` は水平な縁（舞台前縁・畳の縁など）の点列。
3. `floor`: 床の芯の色の絞り（`core_hsv`。雪の外装は別の色域）、`thr`（Lab のマハラノビス距離。既定5）。
4. `blocked[]`: 登れない所・扉など（多角形・理由）。`assist[]`: 既定は空。通学路など最小限、車椅子になる前にしか取れない宝箱の場所だけ多角形で足す。
5. `exits[]`: 設計書の遷移（辺・相手の door ID）と、根拠の行の引用（`design_source`）。位置が設計書に無ければ `position: {"status":"TBD"}` のまま `candidates[]`（平面座標 `plan_box: [u0,u1,v0,v1]`）を並べる。位置が決まったら `position: {"status":"fixed","plan_box":[...]}`（または `image_polygon`）に書き換える。絵から出入口を読まない。
6. `npcs[]`: 平面座標 `uv`（0..1）。ツールが床の縁から12px以上内側へ寄せる。

実行: register → mask の順（mask は register.json が今の入力・画像と一致することを検査する）。

## TRM-02 の出口（2026-10-23 kako-jun 決定 #144 を反映）

- `TRM-02.door-west`（相手 `TRM-04.door-east`）: 西壁・**上下の中央より下寄り（平面 v>0.5）**。幅・正確な位置は未指定なので `position` は TBD のまま、候補 D-lower-half（v=0.5〜1.0）・E-mid-low（0.6〜0.8）・C-sw（0.78〜0.98）を残す。旧 A-nw・B-mid は捨てた。kako-jun に幅と位置を確認する。
- `TRM-02.door-outside`（相手 `TRM-03.door-playroom`）: 下辺（南壁）の右端付近。E1 の木の扉の足元（u=0.84〜0.93、v=0.92〜1.0）を `fixed` で置いたが、**検査は FAIL**（縁px0・white0）。採用画像ではその扉の前の床を丸テーブル・椅子・棚の家具が塞いでいるため（床マスクの外）。作り直しでは扉前を空けるか、出口位置を白い南縁（x<約1190）へ移すか、kako-jun が決める。

## bridge・carve・絵の修正候補・from_room（TRM-04 で追加。2026-10-23。#144）

方針（kako-jun）: マスクは設計（台帳・決定）が正本。絵と食い違う所はマスクを設計に合わせ、食い違いは「絵の修正候補」として記録する。今の絵が100%正解ではないので、完全一致に拘らない。

優先順位: 床の色 ＜ blocked（引く）＜ **bridge**（足す。blocked は越えない）＜ **carve**（足す。blocked を上書き）＜ assist（white の中だけ橙）。

入力JSONのトップレベルに配列で書く（どちらも省略可）。

```json
"bridges": [
 {"id": "west-sill", "room": "hall",
  "plan_uv_polygon": [[-0.075,0.46],[0.0,0.46],[0.0,0.88],[-0.075,0.88]],
  "reason": "床色でないが通れる所（石の敷居など）。根拠を書く"}
],
"carves": [
 {"id": "...", "room": "hall",
  "line_uv": {"from": [0.5,0.0], "to": [0.5,-0.3], "width_plan_px": 300},
  "reason": "絵では家具で塞がれているが、設計では通路"}
]
```

- 形はどれか1つ: `plan_uv_polygon`（room の平面座標 0..1 の多角形。範囲外も可＝行列を外挿するので、room の quad の外の隙間も指せる）／`plan_px_polygon`（平面図の画素）／`image_polygon`（画像の画素。最後の手段）／`line_uv`（線＋幅。幅は平面図の画素）。`room` は image_polygon 以外で必須。
- 結果 `result.json` に `bridges[]`・`carves[]`（追加した white の画素数）と **`picture_fix_candidates[]`**（絵の修正候補の一覧: kind・id・room・reason・area_px・image_bbox・centroid・carve が重なった blocked の id）が出る。判定表にも1行ずつ出るが、判定は落とさない（連結を1にするのに使うため）。blocked 検査の「white 漏れ」は carve した範囲を除く。
- 重ね画像: bridge=水色、carve=黄。

`plan_aspect.source` に `from_room:<id>` または `from_room:<id>*<ratio>` を書くと、別の部屋の行列から縦横比を出す（同じ高さの床が壁で分かれた廊下など。`w_over_h` は null でよい）。その部屋の4点を元の部屋の行列へ外挿し、平面での幅÷奥行き×ratio を入れる。独立検証にはならない。元の部屋は `from_room` でない部屋。

円の点が少なくモーメント法が不安定なときは、その値を判定から外して `WARN` と出す（外接矩形の真円度だけで見る）。重ね画像の候補ラベルは出口ごとに縦へずらして重ならないようにした。

## TRM-04（本堂）の確定（kako-jun 2026-10-23）

- 石の敷居は通れる（bridge）。須弥壇の段は blocked（広間とは別、部屋にしない）。扉は本堂の壁（廊下の外端案は不採用）。assist は0。
- キャラの基準 `char_unit`（入力JSONに根拠付き）: 体内の1人幅77px（1920幅）→ 1672幅で67.1px、2人幅134.1px。各出口の中心でその room の行列の局所スケールにより平面長へ換算した。
- 出口は fixed: `door-west`・`door-east` は側壁の下寄り v=0.552〜0.968（中心 0.76）、`door-front`（台帳 ID は TRM-04.door-south）は南壁の中央 u=0.392〜0.608。
- 絵の修正候補: 西・東の敷居（広間と廊下の間に壁・柱・段があるが、設計では通れる）。詳細は `TRM-04-oblique-result.json` の `picture_fix_candidates`。
