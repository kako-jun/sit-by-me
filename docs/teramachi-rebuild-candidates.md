# 寺町背景・再構築候補台帳（2026-10-16）

`sample/field/rebuild/` は既存の `sample/field/` を上書きしない、寺町の再生成候補置場である。ここにある画像は採用物でも実装入力でもない。`map-topology.md` §3.0 と各MAP契約、walk mask、独立red-teamの三つがそろうまで、採用状態へ変更してはならない。

共通条件: 北=上、現代K県の雪国、手作り模型の真上寄り俯瞰、人物・文字なし、生活の雪汚れ、必須路を先に確保し、宝箱枝を主路に混ぜない。寺町は河岸段丘であり、犀川側の団地へは石段とは別に車椅子スロープを設ける。候補画像はすべて walk mask 未作成である。

| ID | 候補画像 | 必須接続 | 禁止・固有条件 | 現状態 |
|---|---|---|---|---|
| E01 | `E01-teramachi-kindergarten-rebuild-candidate.png` | right→E02、door-north→E11 | 幼稚園北通用門は園庭主路と分離 | review-pending |
| E02 | `E02-teramachi-connector-rebuild-candidate.png` | left→E01、right→E03、top→N2 | 用水と寺門、bottomは閉鎖 | review-pending |
| E03 | `E03-teramachi-hinomi-bend-rebuild-candidate.png` | left→E02、right→E04、bottom→E10 | 火の見櫓、topは閉鎖 | review-pending |
| E04 | `E04-teramachi-wide-road-rebuild-v2-candidate.png` | left→E03、right→E05、top→E11 | 消雪パイプと寺の長塀、bottomは閉鎖 | mask-created-needs-redteam |
| E05 | `E05-teramachi-well-merge-rebuild-candidate.png` | left→E04、right→E06 | 井戸と用水は主路外、top/bottom閉鎖 | review-pending |
| E06 | `E06-teramachi-sento-rebuild-v2-candidate.png` | left→E05、bottom→E07 | 銭湯煙突、top/right閉鎖 | mask-created-needs-redteam |
| E07 | `E07-teramachi-barrier-free-ramp-rebuild-v2-candidate.png` | top→E06、bottom→E08 | 犀川側へ蛇行する車椅子主路。石段なし | mask-created-needs-redteam |
| E08 | `E08-teramachi-danchi-court-rebuild-v2-candidate.png` | top→E07、right→E09、door→F03 | 県営住宅中庭。石段は立位期のみ | mask-created-needs-redteam |
| E09 | `E09-teramachi-old-slope-foot-rebuild-v6-candidate.png` | left→E08、top→E13 | 石段下、車椅子不可。画像端接続はpass、浅い俯瞰・mask・linksが未解決 | blocked |
| E10 | `E10-teramachi-narrow-lane-rebuild-candidate.png` | top→E03 | 画面内で終わる宝箱枝。他辺閉鎖 | review-pending |
| E11 | `E11-temple-grounds-rebuild-v4-candidate.png` | bottom→E04、door-main→F01、door-residence→E12、door-kindergarten→E01 | 本堂と庫裏を別扉にし、段差なし主路 | image-pass-mask-needed |
| E12 | `E12-temple-residence-rebuild-v3-candidate.png` | door-temple→E11、door-hall→F01、door-playroom→F02 | 庫裏。外部へ通じる偽出口なし | image-pass-mask-needed |
| E13 | `E13-teramachi-slope-top-rebuild-v2-candidate.png` | bottom→E09、right→N10 | 段丘上。学校側車椅子坂と石段を混同しない | mask-created-needs-redteam |
| F01 | `F01-temple-main-hall-rebuild-v2-candidate.png` | door-south→E11、door-east→E12 | 本堂。扉前の段差なし・回転余地 | mask-created-needs-redteam |
| F02 | `F02-kindergarten-playroom-rebuild-candidate.png` | door-west→E12 | 遊戯室。舞台袖は画面内終端 | review-pending |
| F03 | `F03-danchi-apartment-rebuild-v2-candidate.png` | door→E08 | 団地室。玄関から居間まで段差なし・回転余地 | mask-created-needs-redteam |

## 次の採用ゲート

1. 独立red-teamが生画像を確認し、各候補を採用可／再生成に判定する。
2. 採用可候補にのみ、輪郭のない編集用 traversal map と前景用マスクを作成する。
3. `links`、三値traversal、扉IDを相手MAPと往復照合する。E01/E11/E12/F01/F02 は屋外・屋内の遷移不変条件も満たす。
4. その後に初めて既存legacyとの差し替え判断を行う。red-teamは画像を採用しない。

## 2026-10-16の進捗と明示的なTBD

- v2 の E04/E06/E07/E08/E13/F01/F03 は、画像契約を独立red-teamが通過し、候補用マスク一式を生成済み。ただしマスク込みの独立再監査と、相手MAPとの往復リンク照合が未完のため、採用不可。
- E11 v4 と E12 v3 は画像契約のみ通過。三値マスク、foreground、door `links`、E01/F01/F02との往復照合が未作成。
- E09 v6 は、left edgeの石畳から中央の石段を経てtop edgeへ抜ける再構図候補。独立red-teamはleft/top接続・right/bottom閉鎖を確認したが、浅い俯瞰の画風懸念とmask/links未作成によりblocked。詳細: `docs/reviews/artifact-redteam/20261016-teramachi-e09-v6.md`。
- E01/E02/E03/E05/E10/F02 は初回候補のまま。画像・mask・prompt記録・独立採否レビューが未完。
- すべての候補で、生成時の完全なprompt本文と候補ごとの参照Refの記録が未完。記録なしに採用してはならない。

## E09 v6 生成記録（2026-10-16）

- 出力: `sample/field/rebuild/E09-teramachi-old-slope-foot-rebuild-v6-candidate.png`（1254×1254）
- Ref: `R006,R011`（寺町・生活圏の正本参照）。既存E09は題材・配置の参考に使わず、現行の接続正本だけを使用した。
- prompt: `square, near-overhead handmade tabletop diorama; snowy fictional K-prefecture old stair foot; one broad standing-only route enters from the left image edge at mid-height as flat stone paving, turns to a steep old stone staircase, and continues through the top image edge near center. Both exits are open and continuous. No other external route: right/bottom edges are retaining walls, houses, snowbanks, exposed cardboard base. Cotton-fiber snow, rough paper-clay stone walls, hand-cut black-paper paving, sponge/yarn model trees, visible cardboard, glue seams and paint irregularities. Camera 80–85° overhead, shallow depth, no horizon or sky. No people, readable text, vehicles, photorealism, camera-level street view, or wheelchair ramp.`
- adoption state: `blocked`。独立red-teamはleft/top到達とright/bottom閉鎖を確認したが、浅い俯瞰の画風懸念、traversal/foreground/runtime mask、E08/E13との相互links未作成をblockerとして記録した。
