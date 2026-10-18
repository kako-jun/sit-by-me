# MAP位置関係図

- overview.svg: 工程Bで全面更新予定。現ファイルは旧図であり現行接続の根拠にしない。
- [body.svg](./body.svg): 工程Aの体内17MAP。全126IDとエリア所属・体内の方向／枚数契約は登録済み。
- [late-dungeons.svg](./late-dungeons.svg): 兼六園・金沢城・双塔・登山道。v2の接続から生成する現行図。

丸はMAP、実線は必須主路、茶破線はドア・乗車・ワープ・飛行機遷移、灰破線は主路と独立した任意枝を表す。画像生成・マスク実装で使う正確な出入口名は、図ではなく [`../map-topology.md`](../map-topology.md) の「MAP相互接続台帳 v2」を正本とする。

旧atlas.svgは旧直列接続が残るため削除した（Git履歴から復元可能）。全126件の正本はv2のMarkdown台帳。工程Aコミット・プッシュ後、工程Bでoverview.svg・全MAPアトラス・各エリア図を作成する。工程Aは全図完成を意味しない。サニーランドの旧pending接続は廃止し、確定した双方向円環はsunnyland.svgへ描画する。図そのものを接続の決定根拠にしてはならない。

更新: `ruby scripts/render_late_topology.rb`。検証: `ruby scripts/verify_map_ledger.rb`。兼六園・城は北上、双塔は高さ、卯辰山は登る順を示す。線は正確な地理的道幅や園路曲線ではない。

- [sunnyland.svg](sunnyland.svg): 八角形入口1/2階・地下水族館・屋外動物園・宿泊棟の双方向円環と任意施設。`ruby scripts/render_sunnyland_topology.rb`で更新。
- [map-ids.json](map-ids.json): 全117IDの割当。新規F61–F65はサニーランド、F66–F73は3塔の追加階。既存IDを後続地区へ押し出さない。
- [overseas-progression.json](overseas-progression.json): ゲーム実装から分離した設計状態契約。`ruby scripts/verify_overseas_progression.rb`で検査。
