# MAP位置関係図

- [overview.svg](./overview.svg): 北上固定のエリア間位置関係。
- [late-dungeons.svg](./late-dungeons.svg): 兼六園・金沢城・双塔・登山道。v2の接続から生成する現行図。

丸はMAP、実線は必須主路、茶破線はドア・乗車・ワープ・飛行機遷移、灰破線は主路と独立した任意枝を表す。画像生成・マスク実装で使う正確な出入口名は、図ではなく [`../map-topology.md`](../map-topology.md) の「MAP相互接続台帳 v2」を正本とする。

旧atlas.svgは旧直列接続が残るため削除した（Git履歴から復元可能）。全104件の正本はv2のMarkdown台帳で、現行図は上記4地区に範囲を限定する。サニーランドのpending接続は描画しない。図そのものを接続の決定根拠にしてはならない。

更新: `ruby scripts/render_late_topology.rb`。検証: `ruby scripts/verify_map_ledger.rb`。兼六園・城は北上、双塔は高さ、卯辰山は登る順を示す。線は正確な地理的道幅や園路曲線ではない。
