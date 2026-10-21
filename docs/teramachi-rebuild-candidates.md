# 寺町背景・再構築候補台帳（2026-10-16）

旧再構築候補は#68の整理で削除した。以下の旧ファイル名は削除記録であり、現存する入力画像ではない。[移行manifest](production/20261018-asset-migration.json)のold／base_commitで復元元を追跡する。新候補の保存先は `assets/images/fields/candidates/<MAP-ID>.png`。旧legacyは一枚も採用しない。TRM-01〜TRM-16の16枚すべてで `map-topology.md` §3.0 と各MAP契約、walk mask、独立red-teamがそろった後だけ、一括でruntimeへ差し替える。

共通条件: **新規候補の寸法は目標1920×1080。画像生成ツールが返せない場合は16:9の1672×941または1672×940を許容。それ以外の寸法は不合格。リサイズで通さない**。既存候補（正方形・3:2・その他寸法）は採用不可で、主役・配置・接続意図を引き継ぐ入力参照画像としてのみ使う。北=上、現代K県の雪国、手作り模型の真上寄り俯瞰、人物・文字なし、生活の雪汚れ、必須路を先に確保し、宝箱枝を主路に混ぜない。寺町は河岸段丘であり、犀川側の団地へは石段とは別に車椅子スロープを設ける。

> **寸法リセット（2026-10-16）**: 以下の既存16候補は、全て上記の許容寸法（1920×1080、または16:9の1672×941または1672×940）ではないため、個別の旧状態にかかわらず `recreate-required-1920x1080` とする。画像・mask・red-teamの過去記録は、次版を作る際の題材・配置・接続の参照であり、採用根拠には使わない。

> **寺の4MAPの生成条件（kako-jun 2026-10-21、#51）**: 寸法は1672×940も許容。屋内の視点は外観と同じ向きで天井を外した見下ろし。材料語彙に畳・舞台幕を追加。生成順は外観TRM-03が先で、室内TRM-04/05/02は採用した外観画像を参照に渡し「この建物のこの部屋の室内」を描く。扉・像・墓地・鐘楼などの位置は、採用した外観画像で確定し、以後の参照とする。TRM-03は池なし（お金持ちの寺ではない）／像と墓地は必須／鐘楼あり（演出に使える）。墓地は住居側（境内の左＝西側）。園庭側（右＝東）には置かない（kako-jun 2026-10-21、#51）。像（親鸞。笠と杖の小さな石像。蓮如には変えない）は中心の石畳の通路の脇に置き、通路の方を向く。向き（左右のどちら側か）は指定しない（kako-jun 2026-10-21、#51）。

以下は現行接続に更新した削除済み旧候補一覧。過去のpass・mask作成は歴史欄だけに残す。新規生成の参照入力は現存legacyの同じMAP IDを使い、削除済み候補を必須添付にしない。

| ID | 旧参照画像 | 現行の必須接続 | 禁止・固有条件 | 現状態 |
|---|---|---|---|---|
| TRM-01 | `TRM-01-teramachi-kindergarten-rebuild-candidate.png` | bottom→TRM-08.top、door-west→TRM-03 | 屋外園庭（境内の右＝東隣）。通用門は園庭主路と分離 | recreate-required-1920x1080 |
| TRM-16 | `TRM-16-teramachi-connector-rebuild-candidate.png` | left←TRM-06.right、right→TRM-15、top→TRM-17 | 用水と寺門、bottomは閉鎖 | recreate-required-1920x1080 |
| TRM-15 | `TRM-15-teramachi-hinomi-bend-rebuild-candidate.png` | left→TRM-16、right→TRM-07、bottom→TRM-06 | 火の見櫓、topは閉鎖 | recreate-required-1920x1080 |
| TRM-07 | `TRM-07-teramachi-wide-road-rebuild-v2-candidate.png` | left→TRM-15、right→TRM-08、top→TRM-03 | 消雪パイプと寺の長塀、bottomは閉鎖 | recreate-required-1920x1080 |
| TRM-08 | `TRM-08-teramachi-well-merge-rebuild-candidate.png` | left→TRM-07、right→TRM-09、top→TRM-01.bottom | 井戸と用水は主路外、bottom閉鎖。topは園庭の正門(#51) | recreate-required-1920x1080 |
| TRM-09 | `TRM-09-teramachi-sento-rebuild-v2-candidate.png` | left→TRM-08、bottom→TRM-10 | 銭湯煙突、top/right閉鎖 | recreate-required-1920x1080 |
| TRM-10 | `TRM-10-teramachi-barrier-free-ramp-rebuild-v2-candidate.png` | top→TRM-09、bottom→TRM-11 | 犀川側へ蛇行する車椅子主路。石段なし | recreate-required-1920x1080 |
| TRM-11 | `TRM-11-teramachi-danchi-court-rebuild-v2-candidate.png` | top→TRM-10、right→TRM-13、door→TRM-12 | 県営住宅中庭。石段は立位期のみ | recreate-required-1920x1080 |
| TRM-13 | `TRM-13-teramachi-old-slope-foot-rebuild-v6-candidate.png` | left→TRM-11、top→TRM-14 | 石段下、車椅子不可 | recreate-required-1920x1080 |
| TRM-06 | `TRM-06-teramachi-narrow-lane-rebuild-candidate.png` | top→TRM-15、right→TRM-16.left | 住居の裏の道。TRM-16→TRM-15→TRM-06→TRM-16のループ。他辺閉鎖。勝手口の扉TBD | recreate-required-1920x1080 |
| TRM-03 | `TRM-03-temple-grounds-rebuild-v4-candidate.png` | bottom→TRM-07、door-main→TRM-04、door-kindergarten→TRM-01.door-west | 屋外境内。住居・遊戯室への屋外doorなし。池なし（お金持ちの寺ではない）／像と墓地は必須／鐘楼あり（演出に使える）。墓地は住居側（境内の左＝西側）。園庭側（右＝東）には置かない（kako-jun 2026-10-21、#51）。像（親鸞。笠と杖の小さな石像。蓮如には変えない）は中心の石畳の通路の脇に置き、通路の方を向く。向き（左右のどちら側か）は指定しない（kako-jun 2026-10-21、#51）（kako-jun 2026-10-21、#51）。位置は採用した外観画像で確定 | recreate-required-1920x1080 |
| TRM-05 | `TRM-05-temple-residence-rebuild-v3-candidate.png` | door-hall→TRM-04.door-west | 屋内庫裏。本堂の西（左）。TRM-02直結なし | recreate-required-1920x1080 |
| TRM-14 | `TRM-14-teramachi-slope-top-rebuild-v2-candidate.png` | bottom→TRM-13、right→SCH-01 | 段丘上。学校側車椅子坂と石段を混同しない | recreate-required-1920x1080 |
| TRM-04 | `TRM-04-temple-main-hall-rebuild-v2-candidate.png` | door-south→TRM-03、door-west→TRM-05.door-hall、door-east→TRM-02.door-west | 中央の屋内本堂。扉前の段差なし・回転余地 | recreate-required-1920x1080 |
| TRM-02 | `TRM-02-kindergarten-playroom-rebuild-candidate.png` | door-west→TRM-04.door-east | 本堂の東（右）の屋内遊戯室。扉位置TBD。舞台袖は画面内終端 | recreate-required-1920x1080 |
| TRM-12 | `TRM-12-danchi-apartment-rebuild-v2-candidate.png` | door→TRM-11 | 団地室。玄関から居間まで段差なし・回転余地 | recreate-required-1920x1080 |

## 次の採用ゲート

1. 独立red-teamが生画像を確認し、各候補を採用可／再生成に判定する。
2. 採用可候補にのみ、輪郭のない編集用 traversal map と前景用マスクを作成する。
3. `links`、三値traversal、扉IDを相手MAPと往復照合する。TRM-01/TRM-03/TRM-05/TRM-04/TRM-02 は屋外・屋内の遷移不変条件も満たす。
4. 16枚すべてを通過させた後にだけ、旧legacyゼロの一括runtime差替え判断を行う。red-teamは画像を採用しない。

## 2026-10-16の旧進捗履歴（以下の通過は現行採用根拠にしない）

- v2 の TRM-07/TRM-09/TRM-10/TRM-11/TRM-14/TRM-04/TRM-12 は、画像契約を独立red-teamが通過し、候補用マスク一式を生成済み。ただしマスク込みの独立再監査と、相手MAPとの往復リンク照合が未完のため、採用不可。
- TRM-03 v4 と TRM-05 v3 は画像契約のみ通過。三値マスク、foreground、door `links`、TRM-01/TRM-04/TRM-02との往復照合が未作成。
- TRM-13 v6 は接続・mask監査を通過したが1254×1254のため採用不可。石段の主役・left→top接続・assist-onlyの設計だけを、1920×1080再生成の参照として引き継ぐ。
- TRM-01/TRM-16/TRM-15/TRM-08/TRM-06/TRM-02 は初回候補のまま。画像・mask・prompt記録・独立採否レビューが未完。
- すべての候補で、生成時の完全なprompt本文と候補ごとの参照Refの記録が未完。記録なしに採用してはならない。

## TRM-13 v6 旧候補記録（2026-10-16、参照専用）

- 出力: `sample/field/rebuild/TRM-13-teramachi-old-slope-foot-rebuild-v6-candidate.png`（1254×1254）
- Ref: `R006,R011`（寺町・生活圏の正本参照）。既存TRM-13は題材・配置の参考に使わず、現行の接続正本だけを使用した。
- prompt: `square, near-overhead handmade tabletop diorama; snowy fictional K-prefecture old stair foot; one broad standing-only route enters from the left image edge at mid-height as flat stone paving, turns to a steep old stone staircase, and continues through the top image edge near center. Both exits are open and continuous. No other external route: right/bottom edges are retaining walls, houses, snowbanks, exposed cardboard base. Cotton-fiber snow, rough paper-clay stone walls, hand-cut black-paper paving, sponge/yarn model trees, visible cardboard, glue seams and paint irregularities. Camera 80–85° overhead, shallow depth, no horizon or sky. No people, readable text, vehicles, photorealism, camera-level street view, or wheelchair ramp.`
- mask: `sample/field/masks/teramachi-e09-rebuild-v6.json` と同プレフィックスのtraversal/foreground/runtime/overlay一式。left/topはともに `590–690` の `assist` / `standing-or-companion-assist` で、TRM-11.right・TRM-14.bottomと同一範囲へ同期済み。white（universal）はなし。wheelchair/互換aliasは全黒。foregroundは透明RGBA（遮蔽なし）。
- adoption state: `recreate-required-1920x1080`。軽い奥行きは許容済み、画像・mask独立red-teamはpassだったが、正方形のため採用・runtime参照更新は行わない。
