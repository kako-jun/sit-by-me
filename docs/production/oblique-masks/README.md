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

## TRM-02 で設計書に書かれていない点（kako-jun への質問）

`TRM-02.door-west`（相手 `TRM-04.door-east`）の**西壁上の位置**と廊下長は map-specifications.md:47・map-topology.md:141,287・map-contract-checklist.md:58 のすべてで TBD。入力JSONでは `TBD` とし、候補 A-nw（北寄り）・B-mid（中ほど）・C-sw（南寄り）を並べてある。決まれば `position` を書き換えて再実行するだけでよい。
