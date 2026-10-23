# 全MAP接続図

全129MAP・136接続・15エリアを、[接続正本v2](../map-topology.md)と[所属・配置台帳](areas.json)から生成する。体内工程Aのコミット・プッシュ後、工程Bの全図も更新済み。画像生成・ゲーム実装やmask完成を意味しない。

- [全エリア間の全体図](overview.svg)：金沢内の相対地理は北上。体内・海外・所在を固定しないK空港はイベント層へ分離。境界の全出入口を併記。
- [全129MAPアトラス](atlas.svg)：所有MAPを各1回表示し、全接続口と外部の隣接先を併記。下部にエリア間の全接続一覧。大きい図なので個別図の等倍表示も利用する。
- [体内詳細](body.svg)、[庭園・城・三塔・登山道](late-dungeons.svg)、[サニーランド円環詳細](sunnyland.svg)も保持。

| エリア | 個別接続図 |
|---|---|
| 寺町・寺院と住居 | [teramachi.svg](areas/teramachi.svg) |
| 香林坊・茶屋街・広坂・病院 | [city.svg](areas/city.svg) |
| 金沢駅 | [station.svg](areas/station.svg) |
| 小学校と通学坂 | [school.svg](areas/school.svg) |
| 卯辰山 | [mountain.svg](areas/mountain.svg) |
| サニーランド | [sunnyland.svg](areas/sunnyland.svg) |
| 内灘・内灘線 | [uchinada.svg](areas/uchinada.svg) |
| 奥能登への鉄道 | [noto_train.svg](areas/noto_train.svg) |
| 奥能登・被災前 | [noto_before.svg](areas/noto_before.svg) |
| 奥能登・被災後 | [noto_after.svg](areas/noto_after.svg) |
| 架空の体内 | [body.svg](areas/body.svg) |
| K空港 | [airport.svg](areas/airport.svg) |
| 海外・荒野と三塔 | [overseas.svg](areas/overseas.svg) |
| 兼六園 | [garden.svg](areas/garden.svg) |
| 金沢城 | [castle.svg](areas/castle.svg) |

緑実線=`edge`（双方向。辺単位・模型の縁の辺）、茶破線=`door`（双方向の扉・階層・抽象通路）、紫破線と矢印=`event`（園庭→体内の物語移動）、青実線と矢印=`oneway`（海外への旅客機）。体内の`door-passage-*`は物理的な建物の扉ではない。一方向の2種類だけに方向矢印を付ける。

白丸は所有MAP、薄茶色の小丸は別エリアの参照先。同じラッコ館・洞窟への入口と出口は別々の端IDを維持する。線の交差は接続点ではない。庭園・城は北上、ほかは見出しの注記に従う模式図で、距離・階高の縮尺を表さない。

奥能登の被災前／後は時期差分で相互の徒歩接続を追加していない。K空港はワープ到達だが正本に固定起点がなく、架空の歩行線を足していない。旧DIAG001/002 PNGは削除済み（復元は git 履歴から）。

再生成：`ruby scripts/render_map_atlas.rb`。詳細図は各`render_body_topology.rb`、`render_late_topology.rb`、`render_sunnyland_topology.rb`で更新。

検証：`ruby scripts/verify_map_ledger.rb`、ID付け替え表は `uv run python3 scripts/verify_map_id_renumber.py`（旧ID→新ID対応は [対応表](../production/20261019-map-id-renumber.json)）。全件数・一意所属・体内入口と方向／枚数・三塔進行・全図の端ID／種別／矢印／可視IDを検査。[ID登録](map-ids.json)は全129件。[海外設計状態契約](overseas-progression.json)はゲームruntimeと別の設計成果物。

デパートのエレベーターはMAPを持たず、接続台帳の外の「階選択遷移」（[map-topology.md](../map-topology.md)）で管理する。各階（KRB-02・KRB-03・KRB-04・KRB-05・KRB-06）の扉に入るとウィンドウで階を選び、選んだ階の扉前に着く。箱は全階を結ぶため、香林坊エリア図には階をつなぐ線を描かず注記で示す（4階KRB-05は条件つき）。

図の座標（`areas.json` の `layout`）は、docs の方向記述（斜め道・上り下り・左右）を模式的に反映する。距離・縮尺は表さない。接続の正本は台帳（[map-topology.md](../map-topology.md) v2）である。
