# 寺町背景・再構築候補台帳（参照のみ。現行の正本は台帳）

**この文書は参照専用**。寺町 MAP の接続・禁止/固有条件・状態・既定・未決・決定は台帳（`docs/ledger/*.yaml`）へ移した。ここには台帳に載せない旧記録（削除済みの旧候補画像の名前・2026-10-16 時点の進捗・TRM-13 v6 の旧候補記録）だけを残す。現行の判断に使わない。

## 台帳の何を見るか

| 知りたいこと | 台帳の場所 |
|---|---|
| MAP の状態・採用状態・一言特徴・設計意図・寸法の根拠 | [MAP.yaml](ledger/MAP.yaml) |
| 現行の必須接続（どの端がどの MAP の端へつながるか）・扉の位置/幅 | [端.yaml](ledger/端.yaml)・[接続.yaml](ledger/接続.yaml) |
| 禁止・固有条件（閉鎖する辺とその理由、井戸・用水・煙突・櫓などの要素） | [要素.yaml](ledger/要素.yaml)（種別『閉鎖辺』を含む）・[決定.yaml](ledger/決定.yaml) |
| 仮置きの値（旧 legacy 画像の概略構図を参考にした既定。要確認） | [既定値.yaml](ledger/既定値.yaml) |
| まだ決まっていないこと | [未決.yaml](ledger/未決.yaml) |
| 画像の寸法（1920×1080、返せない場合は 16:9 の 1672×941。リサイズで通さない） | 決定 `TRM.size` |
| 時期別の画像（同一IDの差し替え。-kids/-fire/-burnt/-wc）・寝室の方針 | 決定 `TRM.era-variants`・`TRM-05.bedrooms` |
| 採用画像・マスクなどの素材 | [素材.yaml](ledger/素材.yaml)・[採用要素.yaml](ledger/採用要素.yaml) |

寺町の地形制約（河岸段丘・団地へは石段とは別に車椅子スロープ）は [map-topology.md](map-topology.md)「寺町の地形不変条件」が正本。

## 削除済みの旧候補画像（名前だけの記録）

旧再構築候補は #68 の整理で削除した。以下は削除記録であり、現存する入力画像ではない。[移行manifest](production/20261018-asset-migration.json) の old／base_commit で復元元を追跡する。新規生成の参照入力は現存 legacy の同じ MAP ID を使い、削除済み候補を必須添付にしない。

| ID | 旧参照画像 |
|---|---|
| TRM-16 | `TRM-16-teramachi-connector-rebuild-candidate.png` |
| TRM-15 | `TRM-15-teramachi-hinomi-bend-rebuild-candidate.png` |
| TRM-07 | `TRM-07-teramachi-wide-road-rebuild-v2-candidate.png` |
| TRM-08 | `TRM-08-teramachi-well-merge-rebuild-candidate.png` |
| TRM-09 | `TRM-09-teramachi-sento-rebuild-v2-candidate.png` |
| TRM-10 | `TRM-10-teramachi-barrier-free-ramp-rebuild-v2-candidate.png` |
| TRM-11 | `TRM-11-teramachi-danchi-court-rebuild-v2-candidate.png` |
| TRM-13 | `TRM-13-teramachi-old-slope-foot-rebuild-v6-candidate.png` |
| TRM-06 | `TRM-06-teramachi-narrow-lane-rebuild-candidate.png` |
| TRM-03 | `TRM-03-temple-grounds-rebuild-v4-candidate.png` |
| TRM-05 | `TRM-05-temple-residence-rebuild-v3-candidate.png` |
| TRM-14 | `TRM-14-teramachi-slope-top-rebuild-v2-candidate.png` |
| TRM-04 | `TRM-04-temple-main-hall-rebuild-v2-candidate.png` |
| TRM-02 | `TRM-02-kindergarten-playroom-rebuild-candidate.png` |
| TRM-12 | `TRM-12-danchi-apartment-rebuild-v2-candidate.png` |

## 旧ゲート（2026-10-16 時点。現行の運用は台帳と `ruby scripts/verify_ledger.rb`）

1. 独立 red-team が生画像を確認し、各候補を採用可／再生成に判定する。
2. 採用可候補にのみ、輪郭のない編集用 traversal map と前景用マスクを作成する。
3. `links`、三値traversal、扉IDを相手MAPと往復照合する。
4. 15枚（TRM-02〜TRM-16）すべてを通過させた後にだけ、旧legacyゼロの一括runtime差替え判断を行う。red-teamは画像を採用しない。

## 2026-10-16の旧進捗履歴（以下の通過は現行採用根拠にしない）

- v2 の TRM-07/TRM-09/TRM-10/TRM-11/TRM-14/TRM-04/TRM-12 は、画像契約を独立red-teamが通過し、候補用マスク一式を生成済み。ただしマスク込みの独立再監査と、相手MAPとの往復リンク照合が未完のため、採用不可。
- TRM-03 v4 と TRM-05 v3 は画像契約のみ通過。三値マスク、foreground、door `links`、TRM-04/TRM-02との往復照合が未作成。
- TRM-13 v6 は接続・mask監査を通過したが1254×1254のため採用不可。石段の主役・left→top接続・assist-onlyの設計だけを、1920×1080再生成の参照として引き継ぐ。
- （旧）TRM-01/TRM-16/TRM-15/TRM-08/TRM-06/TRM-02 は初回候補のまま（TRM-01は2026-10-23に廃止、TRM-03へ統合）。画像・mask・prompt記録・独立採否レビューが未完。
- すべての候補で、生成時の完全なprompt本文と候補ごとの参照Refの記録が未完。記録なしに採用してはならない。

## TRM-13 v6 旧候補記録（2026-10-16、参照専用）

- 出力: `sample/field/rebuild/TRM-13-teramachi-old-slope-foot-rebuild-v6-candidate.png`（1254×1254）
- Ref: `R006,R011`（寺町・生活圏の正本参照）。既存TRM-13は題材・配置の参考に使わず、現行の接続正本だけを使用した。
- prompt: `square, near-overhead handmade tabletop diorama; snowy fictional K-prefecture old stair foot; one broad standing-only route enters from the left image edge at mid-height as flat stone paving, turns to a steep old stone staircase, and continues through the top image edge near center. Both exits are open and continuous. No other external route: right/bottom edges are retaining walls, houses, snowbanks, exposed cardboard base. Cotton-fiber snow, rough paper-clay stone walls, hand-cut black-paper paving, sponge/yarn model trees, visible cardboard, glue seams and paint irregularities. Camera 80–85° overhead, shallow depth, no horizon or sky. No people, readable text, vehicles, photorealism, camera-level street view, or wheelchair ramp.`
- mask: `sample/field/masks/teramachi-e09-rebuild-v6.json` と同プレフィックスのtraversal/foreground/runtime/overlay一式。left/topはともに `590–690` の `assist` / `standing-or-companion-assist` で、TRM-11.right・TRM-14.bottomと同一範囲へ同期済み。white（universal）はなし。wheelchair/互換aliasは全黒。foregroundは透明RGBA（遮蔽なし）。
- adoption state: `recreate-required-1920x1080`。軽い奥行きは許容済み、画像・mask独立red-teamはpassだったが、正方形のため採用・runtime参照更新は行わない。
