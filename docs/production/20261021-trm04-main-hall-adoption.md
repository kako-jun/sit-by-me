# TRM-04 本堂（室内）の採用（2026-10-21、#51）

状態: **採用（TRM-04 本堂の室内。TRM-05/TRM-02生成の参照）**。mask・links・独立red-team未通過のため **runtimeへは切り替えない**（寺町は16枚全件通過後の一括切替。旧legacyは据え置き）。台帳statusは `recreate-required-1920x1080` のまま。なお以前の v2 は人の判断で不採用にした（記録は本書末尾に残す）。この採用は v2 とは別の画像（v11）。

## 保存物
- 保存先: `assets/images/fields/reference/teramachi-main-hall-interior-adopted.webp`（外観参照の置き場。`scripts/verify_asset_layout.py` の許可パターン内。正本の `fields/TRM-04.webp` へはruntime切替時に移す）
- 形式: 非可逆WebP（品質85、`magick in.png -quality 85 out.webp`）、実寸 **1672×940 のまま（リサイズなし）**、363,540 bytes、sha256 `837d3a108990ee5e1bdd931417eca350c4406b28fbe780c46e39066d5ed96042`。PNGは残さない。
- 元PNG（v11、生成原本ではなく編集の貼り戻し後。リポには置かない）: 1672×940、sha256 `8d1a1a50e02511d6e2ff38b434a57b51f774e0dad916220372399393af3f5465`。

## 採用の判断
kako-jun が9回目（v9）を「よい。ただし仏壇前の柵や注意書きはいらない。参考写真は観光用のかも。実際は個人の寺にはないものだ」と判断。v9 から矢来（仏壇前の柵）と矢来の上の名簿だけを消した v11 を採用。

## 来歴（11回の画像。各回のFAIL理由）
- 参照: 採用外観1枚（`teramachi-temple-grounds-exterior-standing`）。v9 以降は割付図 `layout-trm04`（1672×941、白地に薄いグレーの矩形3つ。本堂の南面幅=640px、西の廊下340px、東の廊下250px、南端を揃える）を2枚目の参照に添付。
- v1: 生画像レビュー(a6f3fbd) FAIL（外観の土台縁の雪の混入、廊下が外観より長い、座布団、本尊の姿）。
- v2: 独立レビュー PASS だが kako-jun が畳が不自然として不採用（下の記録）。以後、床は板張りに。
- v3: 荘厳・板張り・材料は良好。戸口の位置と向き・東廊下の長さ・廊下の北壁・芳名板の位置でFAIL。
- v4: 戸口が廊下の南壁の両端に付く、芳名板が東廊下の北壁に付く（向きの文章がモデルに通じない）。
- v5: 戸口が3回連続で北壁、芳名板が東廊下、廊下が長く取り付きが北寄り、door-west/east が読めない。見下ろしでは外端の壁が細い帯になるため、廊下の外端を「壁なしの開口」に変更。
- v6: kako-jun が「部屋の外側に外の景色（雪・草・木）を描く。白い素地は不自然」と決定。
- v7: 戸板が描かれる、廊下の長さ・南壁の面一でFAIL。
- v8: 戸口・掲示物・外の景色・荘厳は合格。廊下の長さ（西0.61・東0.62、外観は0.53/0.39、全長2.23）と南壁の面一（約195pxずれ）のみ不合格。文章での比率指定は3回無視されたため、割付図を2枚目の参照にする方式に変更。
- v9: 割付図方式で kako-jun が「よい」。矢来と名簿は不要の決定。
- v10: 矢来と名簿を除く再生成を試みたが採用に至らず（詳細はこの記録に無い）。
- v11（採用）: v9 を土台に、矢来と名簿だけを imagegen の範囲限定編集で消し、マスク領域のみ v9 に貼り戻した。
- 判定: 独立生画像レビュー(a6f3fbd)は、戸口・掲示物・外の景色・荘厳は合格（v8）。v11 は kako-jun が「よい」とした v9 からの限定編集で、マスク外の差分は4画素。

## v9 → v11 の編集手順
1. マスク `mask-trm04-v9.png`（1672×940、グレースケール。白の矩形=編集可の範囲、黒=変更不可。矢来と名簿のある範囲だけ）を作った（sha256 `7c3a7dc5752bb51c5cca223dedcc75de93be222cdc5fabcf3f61e1f7c078c530`）。
2. imagegen の画像編集（マスク付き）を1回だけ実行。出力 `trm04-v11-raw.png`（1672×940、sha256 `1a89f6018059a967ec6ba906deb325efd81be8915beab9dc5e26e50559c71789`）。
3. マスク領域のみ v9（元PNG sha256 `b3d25a3b86965819c639f8b35c0b0decaecdeedb06c93e26ccde92fb5eda1b98`）に貼り戻して v11 とした。マスク外の差分は4画素。
編集指示: 「Remove the low black fence and the small white paper list that stand in front of the altar table. Continue the dark plank floor of the front area up to the black edge of the raised inner sanctuary step. Change nothing else」

## 許容した逸脱（来歴のみ・再生成しない）
- 東の廊下が外観より長い（外観比0.39に対し長め）。kako-jun「よい」で許容。
- 本堂南面（door-south の外）に灰色の段ボールの段ブロック1個（外観の石段に対応）。
- 余間の掛軸（聖徳太子・七高僧）は観光寺院由来かもしれない（要確認）。本尊は立像が既定（要確認、坐像でも可）。

## 前置き指示（wrapper、v9 時点）
```text
Invoke the $imagegen skill and use the built-in image_gen tool at the HIGHEST quality (quality: high), requesting 1920x1080 (16:9), to create the image described in the prompt below. Two reference images are attached, in this order: (1) the adopted exterior of the same building; (2) a layout block diagram (use both as described in the prompt). Call image_gen EXACTLY ONCE: no retries, no regeneration, no multiple candidates, even if you think the result is imperfect. Then save the REAL generated PNG (decode the tool result) into the current workspace at out/trm04-v9.png. You are STRICTLY FORBIDDEN from fabricating/drawing the image with magick/ImageMagick/PIL/Pillow/numpy/SVG/canvas/any code; only the image_gen tool. If the image_gen tool is genuinely not in your toolset, do NOT fabricate - output exactly: IMAGE_GEN_TOOL_UNAVAILABLE. Do not resize or crop the result. Do not use any files in ~/.codex/generated_images/ made by other calls; only the image generated in this call. Report the saved file path.
Output a 16:9 landscape image. Target 1920x1080; if not possible, 1672x941. Do NOT use 3:2 or 1536x1024.
```

## 送信した完全prompt（v9 の送信text、原文のまま）
```text
Generate ONE image: the final field background for map TRM-04 (main hall, INDOOR, central room of the temple building group). Do not generate any other map.

=== SOURCE TEXT (verbatim, do not paraphrase) ===
[Specification row]
| TRM-04 | 全時期 | 仏具の鈍い金と畳が対照になる本堂（屋内） | door-south→TRM-03、door-west→TRM-05.door-hall、door-east→TRM-02.door-west。参拝域は端へ出ない | #60。中央の屋内分岐。住居・幼稚園へ外に出ず移動 |
[Asset registry row]
| TRM-04 | `teramachi-main-hall-interior` | 寺町 | ドア接続・時期・室内通路 |
[Contract checklist row]
| TRM-04 | recreate-required-1920x1080 | R021,R024 | 旧本堂画像は参照専用。新背景・mask未作成 | #60の中央屋内本堂。TRM-03南、TRM-05西、TRM-02東の扉位置、畳・仏具と主路、段差・幅・回転域を記録する |
[Rebuild candidate row]
| TRM-04 | `TRM-04-temple-main-hall-rebuild-v2-candidate.png` | door-south→TRM-03、door-west→TRM-05.door-hall、door-east→TRM-02.door-west | 中央の屋内本堂。扉前の段差なし・回転余地 | recreate-required-1920x1080 |
[Connections touching TRM-04, map-topology.md]
| TRM-03.door-main | TRM-04.door-south | door | 本堂内部 |
| TRM-04.door-west | TRM-05.door-hall | door | 本堂から西（境内から北を見て左）の庫裏（住居）への渡り廊下 |
| TRM-04.door-east | TRM-02.door-west | door | 本堂から東（境内から北を見て右）の幼稚園への屋内廊下。TRM-02側は本堂側（西）から入るので既存IDのwestと整合。扉の位置・廊下長はTBD |
[Outdoor/indoor transition invariants]
| `TRM-03.door-main` | `TRM-04.door-south` | 境内から本堂へ。段差を主路にせず、扉前に回転余地を残す。 |
| `TRM-04.door-west` | `TRM-05.door-hall` | 本堂から西（左）の庫裏へ渡る廊下。畳廊下の方位と扉位置を一致させる。扉位置TBD。 |
| `TRM-04.door-east` | `TRM-02.door-west` | 中央の本堂から東（右）の幼稚園へ屋内廊下で移動。TRM-02は本堂側（西面）から入る。扉位置・廊下長TBD。舞台袖は画面内終端。 |
[Site layout section 6]
| TRM-03.door-main | TRM-04.door-south | ドア（本堂の正面） | 境内から本堂 |
| TRM-04.door-west | TRM-05.door-hall | ドア（渡り廊下） | 本堂（中央）から西の住居。内部どうし |
| TRM-04.door-east | TRM-02.door-west | ドア（屋内廊下） | 本堂から東の幼稚園・遊戯室 |
[Decision, decisions.md]
| **寺町の寺（幼馴染の実家）は浄土真宗大谷派（kako-jun 2026-10-15）。卒塔婆は置かない** | 寺の絵・文章に卒塔婆（宗派上ない）を描かない。仏壇は金仏壇、本尊は阿弥陀如来。浄土真宗は地蔵信仰・現世利益の習俗が基本ない（確認済み: 六地蔵は宗派に合わない。宗派に合う版を別ファイルで作った。`temple-grounds-shinshu-diorama.png`＝親鸞聖人の石像、`teramachi-hinomi-bend-shinshu-diorama.png`・`teramachi-connector-shinshu-diorama.png`＝地蔵を石碑に。元の絵は残す。ほか teramachi-* の絵に地蔵・卒塔婆はない。幼稚園の絵の狛犬は寺院にも置かれるので変えていない）。境内の絵・庫裏の絵・台詞に反映。既存の絵に卒塔婆は見当たらない（目視） |

[Neighbouring maps, map-specifications.md (verbatim)]
| TRM-03 temple-grounds | 全時期 | 親鸞像のある浄土真宗の境内（屋外） | bottom→TRM-07、door-main→TRM-04、door-kindergarten→TRM-01.door-west | #60/#51。本堂中心・境内から見て左（西）住居・右（東）幼稚園の同じ建物群。TRM-01は境内の右隣。住居／遊戯室への屋外doorなし |
| TRM-05 residence | 全時期 | 庫裏の台所と幼馴染の部屋（屋内） | door-hall→中央TRM-04のdoor-west。TRM-02直結なし | #60/#51。本堂の西（左）。台所は火事イベントの場所 |
| TRM-02 | 幼稚園期・火事後 | 舞台幕と小さな椅子が残る遊戯室（屋内） | door-west→TRM-04.door-east（本堂側＝西から入る）。扉位置・廊下長はTBD。舞台袖は画面内終端。TRM-05直結なし | #60/#51。本堂の東（右）。劇の自動イベント用。TRM-01と同じ幼稚園で、園庭直結は未契約 |
[Decisions, kako-jun 2026-10-21 (verbatim)]
段差はこれでいいのでは。車椅子生活になるとは思ってなかったのだし、最初からスロープだったら不自然。車椅子の子ができたと分かったあとに、この画像を渡してスロープがついた別マップに差し替えたほうがストーリー的に自然
渡り廊下がながすぎる
本堂を通らなくても左右の建物にも入口は必要だろ
右側の幼稚園のほうが大きな建物であるべき
住居と違って掃き出し窓があるべき
- **屋内の視点**: 外観と同じ向きで天井を外した見下ろし（案どおり）。
- **生成順と参照**: まず外観 TRM-03 を作る。室内3つ（TRM-04/05/02）は、採用した外観画像を参照画像に渡し「この建物のこの部屋の室内を描け」の形で作る。扉・像・墓地などの位置は、採用した外観画像で確定し、以後の参照とする。
- **材料語彙**: スキルに畳・舞台幕などを追加する（案どおり）。
[Decision, kako-jun 2026-10-21 (verbatim)]
畳がすごく不自然だ。苦手なら板張りにしろ。寺の本堂は普通の和室じゃないので、札とかが壁にあったりする。浄土真宗の寺の写真を調べろ
[Research summary (research-jodo-shinshu-hondo.md; sources in source-bundle SRC 28)]
A 浄土真宗 main hall has: a wide front area (外陣), a low boundary fence (矢来), a raised inner sanctuary (内陣, one step higher), and side alcoves (余間) at the left and right of the sanctuary. The principal image is a gold standing Amida Nyorai in a gilded shrine (御宮殿) on a waisted red-and-black lacquered platform (須弥壇), with a front table (前卓) holding a three-piece set (三具足). Verified wall notices: a brush-written wooden name plaque (芳名板) on the white wall at the right of the front area, and a paper name list (過去帳・志納者一覧) pinned at the top of the boundary fence.
[Decision, kako-jun 2026-10-21 (verbatim)]
幼稚園に向かう渡り廊下には子どもらしい飾りを貼ればいい。描いた絵とかね
[Decision, kako-jun 2026-10-21 (verbatim)]
渡り廊下の端の扉の向きが違うのでは
左右に向けてあるべきだ
[Decision, kako-jun 2026-10-21 (verbatim)]
部屋以外の外側の空間には外の景色を書けばいいのではないのか。雪とか草とか木とか。その位置が他の画像と比べて厳密に一致してなくてもプレイヤーは気にしない。白いダンボールで埋めるのは不自然。幼稚園の部屋から外の雪景色が見えていたほうが空間の広がりも感じる
[Notes]
The entrance doors of the residence and the kindergarten (決定「本堂を通らなくても左右の建物にも入口は必要だろ」) are not contracted yet (door IDs undecided): they belong to TRM-05 and TRM-02, not to this room. The steps in front of the hall belong to the exterior TRM-03 (decision 2026-10-21); this room is used in every period and keeps 扉前の段差なし・回転余地.

=== ARCHITECTURE INVARIANT TABLE (verbatim, shared by all four maps) ===
| ヒロインの住居、幼稚園、本堂は外へ出ずに屋内廊下でつながる。本堂を中央に置き、幼稚園と住居を直接接続しない。 | 屋根・外壁を保ち、本堂中央・境内から見て左（西）が住居・右（東）が幼稚園（#51 2026-10-19で左右反転。上の#60原文のdoor-east/westは旧配置の記述）。別棟や外部渡り廊下で代替しない |
| 本堂（中央）・住居（西）・幼稚園（東）は、屋根と壁のある廊下棟で外観上もつながり一つの連続した建物群に見える（根拠 docs/map-topology.md の TRM-04.door-west↔TRM-05.door-hall 渡り廊下、TRM-04.door-east↔TRM-02.door-west 屋内廊下）。 | 住居と幼稚園は直接つながない（本堂経由のみ）。吹きさらしの外部渡り廊下は不可、屋根と壁のある廊下棟は必須。屋外通路・離れた独立棟も不可。審査基準: 本堂の左右の壁面に屋根付き廊下棟が接し、棟の屋根が本堂・住居・幼稚園の屋根へ切れ目なく続く。廊下棟の両端が壁に接し、地面の隙間・雪原が屋根と屋根の間に通らない。住居と幼稚園の間に直接の廊下がない。廊下の長さ・幅・扉位置はTBDで、描き込んで確定させない |
| TRM-03 境内（外部） | 屋外境内。屋根を外した室内・家具を見せない |
| TRM-01の正本行「私立幼稚園の園庭（屋外）」／TRM-02の正本行「遊戯室（屋内）」 | 園庭と遊戯室は同じ幼稚園の外部／内部。TRM-01を室内にしない。未契約の園庭直結doorを足さない |
| TRM-04.door-west ↔ TRM-05.door-hall | 西の住居まで屋内で連続。具体的廊下形状は未確定 |
| TRM-04.door-east ↔ TRM-02.door-west | 東の幼稚園まで屋内で連続（TRM-02は本堂側の西面から入る）。扉位置・廊下長は推測しない |
| TRM-03から住居・幼稚園へ屋外を経由する新規doorは作らない。 | 境内の正面入口はTRM-04へ。住居・遊戯室の外部入口を発明しない |

#60によりTRM-03は屋外、TRM-04/TRM-05/TRM-02は屋内。本堂を中央、境内から北（本堂）を見て左＝西が住居、右＝東が幼稚園とする（#51 2026-10-19の決定。旧「住居＝東・幼稚園＝西」は廃止）。園庭TRM-01は境内TRM-03の右（東）隣で、TRM-03.door-kindergarten↔TRM-01.door-westの通用門でつなぐ。`TRM-05.door-playroom ↔ TRM-02.door-west` と `TRM-03.door-residence ↔ TRM-05.door-temple` は現行グラフから除外する。TRM-03から住居・遊戯室への屋外doorを新設しない。TRM-01↔TRM-03は園庭と境内の屋外通用門で、TRM-02への直結を意味しない。建物の外形・廊下の長さ・画面内配置・通行幅はこの接続図から推測せず、[制作前確認](production/20261018-teramachi-preflight.md)のTBDを解く。

For this image, the 2026-10-21 decisions above take precedence over any older row (for example the rows that say 畳 (the floor is plank, not tatami),  the old east/west door text of #60, the row forbidding new outdoor doors from TRM-03, and 廊下長 TBD).

=== WHAT TO DRAW (positive description) ===
This is an INDOOR map: draw only the interior of the main hall (本堂), the CENTER building of the temple building group, as a miniature built on the same 5 mm foamboard base. VIEWPOINT (kako-jun 2026-10-21): the same orientation as the exterior reference image (north = top; the residence is on the left (west) and the kindergarten on the right (east), as in the reference), looking down with the ceiling and the roof removed, so that the inner sides of the walls and the floor are visible. The roof and the outer faces of the building's walls are not drawn; every wall is a closed interior wall except the three openings below. The ground outside the building's walls, all over the base, is outdoor scenery: cotton-batting snow with a little grass showing through, and several trees (bare leafless winter trees of thin wire and yarn, and snow-covered evergreen trees of green sponge), the same kind of scenery as the reference; nothing of the outdoor scenery enters the room: the floor inside the walls is plank floor only. Outside the walls there is only snow, grass and trees; the graveyard, the playground and its equipment, the Shinran statue, the stone paving and the stone steps of the reference are not drawn, except one grey cardboard step block directly in front of door-south, outside the wall. Trees stand clear of the walls (none overlaps a wall or window).
C1. The room is the main hall (本堂, 屋内) of a small neighbourhood 浄土真宗大谷派 temple, used in every story period (全時期). It is a temple hall and not an ordinary Japanese living room. The floor is a plank floor (decision 2026-10-21): thin cardboard strips painted matte brown, joints drawn as thin lines, slightly worn; there is no tatami in this room. The contrast of dull gold Buddhist implements (仏具の鈍い金) against the plain brown plank floor is the feature of the room. The worship area (参拝域) is the plank floor and does not extend to any image edge.
C2. The room is the central indoor branch (中央の屋内分岐): from it one goes to the residence (west, left) and to the kindergarten (east, right) without going outside (住居・幼稚園へ外に出ず移動). The residence and the kindergarten are not directly joined: only this hall lies between them.
C3. The room is the hall shown in the exterior reference: the central building in the middle of the row of three, with a corridor wing joined on its west wall and on its east wall. door-south is the lattice doors of cardboard and wooden toothpick at the middle of the hall's south face (TRM-03.door-main <-> TRM-04.door-south); door-west is where the west corridor wing meets the hall's west wall, in the southern part of that wall as in the reference; door-east is where the east corridor wing meets the hall's east wall, in the southern part of that wall as in the reference. Inside door-south the floor is level with the door sill, with no step (扉前の段差なし), and the plank floor directly inside the door is left empty of altar, implements and objects as turning room (回転余地). Each corridor wing joins the southern half of the hall's side wall; the south wall of each corridor lines up with the hall's south wall (nearly flush, as in the reference): the bottom edge of each corridor's south wall is on the same horizontal line in the image as the bottom edge of the hall's south wall, so the hall does not stick out far to the south of the corridors, as in the layout diagram. At each junction the hall's side wall has a visible open doorway (posts, lintel, threshold strip) into the corridor.
C4. The hall is divided into zones from south to north. The wide front area (外陣, the largest part of the floor, beginning at door-south) is plain: bare plank floor, a few worn spots, no furniture, no cushion (no zabuton). North of it a low boundary fence (矢来) of cardboard painted matte black crosses the room from side wall to side wall. North of the fence the inner sanctuary (内陣) is raised one step above the front area; the step is shown as a cardboard edge board painted matte black. On the left and the right of the inner sanctuary there is a small side alcove (余間).
C5. In the center of the inner sanctuary stands a gilded miniature shrine pavilion (御宮殿) with a little gold roof, on a waisted platform (須弥壇) painted matte dark red and black. Inside the shrine stands the principal image, a gold standing (立像) Amida Nyorai (阿弥陀如来) with the right hand raised, a halo of gold foil behind it (its shape is chosen by the image). In front, on the raised step of the sanctuary, stands a small table (前卓) draped with a water-cloth and a triangular cloth, holding a three-piece set (三具足) of dull gold: an incense burner in the middle, a candle stand on one side and a flower vase on the other. Two hexagonal gold hanging lanterns hang from a wooden-toothpick beam before the shrine. The two pillars flanking the shrine are covered with gold paper. This is a modest temple: gold is used only on the shrine, the implements and those two pillars; the cloths are faded purple and gold.
C6. On the wall behind the sanctuary, on the left and the right of the shrine, hang two tall scrolls with portraits of Shinran (親鸞) and Rennyo (蓮如), painted on narrow paper in dark ink and gold. In the two side alcoves hang narrow scrolls with portraits of Prince Shotoku (聖徳太子) and the Seven Patriarchs (七高僧); which side holds which is chosen by the image.
C7. Notices on the walls are exactly two kinds, and no others: (1) on the north wall of the west corridor, from end to end, several narrow wooden name plaques (芳名板) in a row, each marked with brush-written black ink strokes that are not readable as characters; (2) at the top of the boundary fence (矢来), a thin paper name list (過去帳・志納者一覧) pinned flat, with ink lines instead of readable characters. The hall's own walls carry nothing else; the only other wall decoration of the model is the children's drawings in the east corridor (C9).
C8. door-west -> TRM-05.door-hall: a short corridor (渡り廊下) with the same plank floor continues west from the hall's west wall to the residence; the west corridor is about half as long as the hall's south face is wide, as the west corridor wing in the reference and as in the layout diagram. There is NO door leaf anywhere in the corridor, and nothing at all on the corridor's north wall except the name plaques, which run right into the corner. The far end of the corridor has no wall: the plank floor stops at a pale threshold strip at the very left end of the model, framed only by two corner posts and a lintel beam, and the snow begins directly beyond it. The opening at the west end faces west, toward the left edge of the image: a person walking along the corridor leaves through it toward the left, so the doorway's threshold strip, posts and lintel stand across the corridor's width at its left end, and the open side faces left. This doorway marks the way on to the residence (the residence itself is not drawn). The south wall of the corridor holds only the window row and nothing else; the corridor's north wall has no door and no window.
C9. door-east -> TRM-02.door-west: a short indoor corridor (屋内廊下) with the same plank floor continues east from the hall's east wall to the kindergarten; the east corridor is visibly shorter than the west corridor, about four fifths of the west corridor's length, as in the layout diagram. There is NO door leaf anywhere in the corridor, and nothing at all on the corridor's north wall except the children's drawings, which run right into the corner. The far end of the corridor has no wall: the plank floor stops at a pale threshold strip at the very right end of the model, framed only by two corner posts and a lintel beam, and the snow begins directly beyond it. The opening at the east end faces east, toward the right edge of the image: a person walking along the corridor leaves through it toward the right, so the doorway's threshold strip, posts and lintel stand across the corridor's width at its right end, and the open side faces right. This doorway marks the way on to the kindergarten (the kindergarten itself is not drawn). The south wall of the corridor holds only the window row and nothing else; the corridor's north wall has no door and no window. On the north wall of the east corridor (the wall without windows), several children's drawings (crayon drawings on drawing paper, colored with crayon-like colored pencil strokes, with no readable characters) are stuck flat with masking tape; they are paper pictures, not plaques. The north wall of the east corridor carries only the drawings: no board, no window and no door. The west corridor carries no drawings.
C10. The hall itself has no opening besides door-south, door-west and door-east; its other walls are plain closed interior walls of paper clay. The south wall of each short corridor shows, from inside, the same row of windows that the reference shows on that corridor wing (frames of wooden toothpick); nothing outdoors is visible through them. Each corridor's north wall has no door; along it hang (west) the name plaques, (east) the children's drawings. The whole building from the west threshold to the east threshold is clearly less than twice the hall's south-face width; the corridors must not reach the left or right side of the base, as in the layout diagram.
C11. No steps are drawn inside the room except the one step of the inner sanctuary (C4). The exact arrangement of the alcoves and of the items inside the sanctuary follows C4 to C7 and is otherwise chosen by the image.
=== CAMERA, MATERIALS, SIZE, REFERENCE ===
FRAME: hand-made tabletop diorama, camera looks down steeper than 45 degrees from horizontal, as close to straight-down as possible (exact number is TBD; oblique is tolerated, never shallower than 45 degrees from horizontal). North = top of the image. No sky, no horizon, no vanishing point. No people, no readable text, no logos.

MATERIALS AND TOOLS (SKILL fixed vocabulary; every material must be identifiable at full size):
- Base: 5 mm foamboard, with exposed corrugated cardboard cross-section visible along the front edge of the diorama; masking tape strips and white PVA glue squeeze-out visible. Outside the walls the base carries the outdoor scenery described in the drawing section. The base sits on a plain wooden tabletop (not asphalt, not a road surface); the table and the room remain visible around the base (do not crop the base).
- Walls: paper clay carved with a wooden toothpick (finger marks, spatula marks), matte poster paint with a flat brush (brush streaks, uneven coats). Pillars and frames: wooden toothpick.
- Scenery outside the walls: snow = cotton batting fixed with white PVA glue; grass = small tufts of green yarn; bare trees = thin wire and yarn; evergreen trees = green sponge and yarn with cotton snow on the branches; one grey cardboard step block directly in front of door-south, outside the wall.
- Floor: plank floor of thin cardboard strips painted matte brown, joints drawn as thin lines.
- Altar and Buddhist implements: dull gold matte poster paint on paper clay and cardboard; the red-and-black platform and fence in matte poster paint; lanterns and small brass-colored parts of beads and buttons. The standing Amida Nyorai image is a small paper-clay figure painted dull gold, with a halo of gold foil paper.
- Children's drawings: colored paper and drawing paper with crayon-like colored pencil strokes, stuck with masking tape.
- Scrolls and notices: narrow paper strips painted with dark ink and gold; name plaques of thin cardboard painted pale wood with brush strokes in black ink.
- Hand-made roughness required: glue squeeze-out, thread lint, ragged hand-cut paper edges, paint unevenness, visible material seams, coarse grain.
- Paper pieces and paper-clay parts look like paper and clay (matte, soft edges), not real wood, real metal or real stone; masking tape strips and glue squeeze-out are clearly visible at the base edges. It must read as a crude hand-made model, not a photograph.

DIMENSIONS: request 1920x1080 (16:9). If the tool cannot return it, 1672x941 or 1672x940 (16:9) is acceptable (kako-jun 2026-10-21). Any other size is a failure; never resize/crop to pass. Measure the real output file (file/identify).

REFERENCE (two attached images: first the adopted exterior, second the layout block diagram): the adopted exterior image of the same temple building group (teramachi-temple-grounds-exterior-standing, 1672x941). Instruction: this is the exterior of this building. Draw the interior of THIS room, the main hall in the center, of THIS building, with the ceiling and roof removed, from the same north-up direction. Take from the reference: the order of the three buildings (residence left, main hall center, kindergarten right), the hall's footprint in the middle of the row, the lattice doors of cardboard and wooden toothpick at the middle of the hall's south face, the places where the two short corridor wings meet the hall's west and east walls, and the matte grey roof, cream walls and dark-brown matte poster paint. The second attached image is a layout block diagram: copy its rectangles' proportions and alignment exactly (the large rectangle is the hall, the two small rectangles at its left and right are the west and east corridors, their south edges on the same horizontal line as the hall's south edge); it carries no style. Do not copy its colors or lines into the model; the rectangles of the diagram are not drawn in the picture, and the model is built only of the materials above. Take the outdoor scenery style (snow, a little grass, trees) from the reference for the ground outside the walls. Inside the walls there is no snow and no plant, and its surfaces are hand-made paper, clay and cardboard, not the reference's photographic precision.
```

## 編集の指示（v11）
```text
Invoke the $imagegen skill and use the built-in image_gen tool at the HIGHEST quality (quality: high) to EDIT the first attached image (image edit with a mask). Two images are attached, in this order: (1) the image to edit, 1672x940; (2) an edit mask of the same size: WHITE rectangle = the only region that may be edited, BLACK = must stay unchanged. Call image_gen EXACTLY ONCE: no retries, no regeneration, no multiple candidates. Keep the output at the same 1672x940 size and framing as the first image. Then save the REAL generated PNG (decode the tool result) into the current workspace at out/trm04-v11-raw.png. You are STRICTLY FORBIDDEN from fabricating/drawing/editing the image with magick/ImageMagick/PIL/Pillow/numpy/SVG/canvas/any code; only the image_gen tool. If the image_gen tool is genuinely not in your toolset, do NOT fabricate - output exactly: IMAGE_GEN_TOOL_UNAVAILABLE. Do not resize or crop the result. Do not use any files in ~/.codex/generated_images/ made by other calls; only the image generated in this call. Report the saved file path.

Edit instruction: Remove the low black fence and the small white paper list that stand in front of the altar table. Continue the dark plank floor of the front area up to the black edge of the raised inner sanctuary step. Change nothing else: keep the gold standing Amida statue, the gold shrine, the lanterns, the table with the purple cloth, all walls, corridors, plaques, drawings, trees and snow exactly as they are. Keep the handmade miniature look (cardboard, paper clay, masking tape).
```

---
# 付記: v2 は不採用だった（2026-10-21、人の判断）

状態: **不採用**（kako-jun の判断。独立生画像レビュー(a6f3fbd)はPASSだったが、人の判断で不採用）。画像ファイルはリポから削除済み。TRM-03 外観の採用は維持。

## 決定（kako-jun 2026-10-21、逐語）
「畳がすごく不自然だ。苦手なら板張りにしろ。寺の本堂は普通の和室じゃないので、札とかが壁にあったりする。浄土真宗の寺の写真を調べろ」

- 反映: 本堂の床は畳でなく板張りにする（畳の表現が不自然なため）。本堂は普通の和室ではなく、壁に札などがある（具体は浄土真宗の本堂の調査後に追記）。TRM-05 の完成promptは調査結果の反映後に再開する（保留）。

## 来歴（記録のみ）
- 生成: 2回目（v2）。参照画像は採用外観1枚（`teramachi-temple-grounds-exterior-standing`）。codex exec で $imagegen を明示起動、1回のみ。実寸 1672×941（リサイズなし）、元PNG sha256 `8f4f6861882944b647c1d03f273c12dbe477cbf39de9a027d05594735155276e`。WebP化した版（267,706 bytes、sha256 `42f9dbd1773cb52cf69dc996a1641b57a02407d497f9da790a904800c04041ed`）は `fields/reference/` から削除した。
- 独立生画像レビュー(a6f3fbd): PASS（軽微: 東廊下が本堂南面幅に対して0.48で外観の0.39よりやや長い）。
- 不採用の理由: 畳の表現が不自然、本堂が普通の和室になっている。

## 前置き指示（wrapper）
```text
Invoke the $imagegen skill and use the built-in image_gen tool at the HIGHEST quality (quality: high), requesting 1920x1080 (16:9), to create the image described in the prompt below. The attached reference image is the adopted exterior of the same building (use it as described in the prompt). Call image_gen EXACTLY ONCE: no retries, no regeneration, no multiple candidates, even if you think the result is imperfect. Then save the REAL generated PNG (decode the tool result) into the current workspace at out/trm04-v2.png. You are STRICTLY FORBIDDEN from fabricating/drawing the image with magick/ImageMagick/PIL/Pillow/numpy/SVG/canvas/any code; only the image_gen tool. If the image_gen tool is genuinely not in your toolset, do NOT fabricate - output exactly: IMAGE_GEN_TOOL_UNAVAILABLE. Do not resize or crop the result. Do not use any files in ~/.codex/generated_images/ made by other calls; only the image generated in this call. Report the saved file path.
Output a 16:9 landscape image. Target 1920x1080; if not possible, 1672x941. Do NOT use 3:2 or 1536x1024.
```

## 送信した完全prompt（原文のまま）
```text
Generate ONE image: the final field background for map TRM-04 (main hall, INDOOR, central room of the temple building group). Do not generate any other map.

=== SOURCE TEXT (verbatim, do not paraphrase) ===
[Specification row]
| TRM-04 | 全時期 | 仏具の鈍い金と畳が対照になる本堂（屋内） | door-south→TRM-03、door-west→TRM-05.door-hall、door-east→TRM-02.door-west。参拝域は端へ出ない | #60。中央の屋内分岐。住居・幼稚園へ外に出ず移動 |
[Asset registry row]
| TRM-04 | `teramachi-main-hall-interior` | 寺町 | ドア接続・時期・室内通路 |
[Contract checklist row]
| TRM-04 | recreate-required-1920x1080 | R021,R024 | 旧本堂画像は参照専用。新背景・mask未作成 | #60の中央屋内本堂。TRM-03南、TRM-05西、TRM-02東の扉位置、畳・仏具と主路、段差・幅・回転域を記録する |
[Rebuild candidate row]
| TRM-04 | `TRM-04-temple-main-hall-rebuild-v2-candidate.png` | door-south→TRM-03、door-west→TRM-05.door-hall、door-east→TRM-02.door-west | 中央の屋内本堂。扉前の段差なし・回転余地 | recreate-required-1920x1080 |
[Connections touching TRM-04, map-topology.md]
| TRM-03.door-main | TRM-04.door-south | door | 本堂内部 |
| TRM-04.door-west | TRM-05.door-hall | door | 本堂から西（境内から北を見て左）の庫裏（住居）への渡り廊下 |
| TRM-04.door-east | TRM-02.door-west | door | 本堂から東（境内から北を見て右）の幼稚園への屋内廊下。TRM-02側は本堂側（西）から入るので既存IDのwestと整合。扉の位置・廊下長はTBD |
[Outdoor/indoor transition invariants]
| `TRM-03.door-main` | `TRM-04.door-south` | 境内から本堂へ。段差を主路にせず、扉前に回転余地を残す。 |
| `TRM-04.door-west` | `TRM-05.door-hall` | 本堂から西（左）の庫裏へ渡る廊下。畳廊下の方位と扉位置を一致させる。扉位置TBD。 |
| `TRM-04.door-east` | `TRM-02.door-west` | 中央の本堂から東（右）の幼稚園へ屋内廊下で移動。TRM-02は本堂側（西面）から入る。扉位置・廊下長TBD。舞台袖は画面内終端。 |
[Site layout section 6]
| TRM-03.door-main | TRM-04.door-south | ドア（本堂の正面） | 境内から本堂 |
| TRM-04.door-west | TRM-05.door-hall | ドア（渡り廊下） | 本堂（中央）から西の住居。内部どうし |
| TRM-04.door-east | TRM-02.door-west | ドア（屋内廊下） | 本堂から東の幼稚園・遊戯室 |
[Decision, decisions.md]
| **寺町の寺（幼馴染の実家）は浄土真宗大谷派（kako-jun 2026-10-15）。卒塔婆は置かない** | 寺の絵・文章に卒塔婆（宗派上ない）を描かない。仏壇は金仏壇、本尊は阿弥陀如来。浄土真宗は地蔵信仰・現世利益の習俗が基本ない（確認済み: 六地蔵は宗派に合わない。宗派に合う版を別ファイルで作った。`temple-grounds-shinshu-diorama.png`＝親鸞聖人の石像、`teramachi-hinomi-bend-shinshu-diorama.png`・`teramachi-connector-shinshu-diorama.png`＝地蔵を石碑に。元の絵は残す。ほか teramachi-* の絵に地蔵・卒塔婆はない。幼稚園の絵の狛犬は寺院にも置かれるので変えていない）。境内の絵・庫裏の絵・台詞に反映。既存の絵に卒塔婆は見当たらない（目視） |

[Neighbouring maps, map-specifications.md (verbatim)]
| TRM-03 temple-grounds | 全時期 | 親鸞像のある浄土真宗の境内（屋外） | bottom→TRM-07、door-main→TRM-04、door-kindergarten→TRM-01.door-west | #60/#51。本堂中心・境内から見て左（西）住居・右（東）幼稚園の同じ建物群。TRM-01は境内の右隣。住居／遊戯室への屋外doorなし |
| TRM-05 residence | 全時期 | 庫裏の台所と幼馴染の部屋（屋内） | door-hall→中央TRM-04のdoor-west。TRM-02直結なし | #60/#51。本堂の西（左）。台所は火事イベントの場所 |
| TRM-02 | 幼稚園期・火事後 | 舞台幕と小さな椅子が残る遊戯室（屋内） | door-west→TRM-04.door-east（本堂側＝西から入る）。扉位置・廊下長はTBD。舞台袖は画面内終端。TRM-05直結なし | #60/#51。本堂の東（右）。劇の自動イベント用。TRM-01と同じ幼稚園で、園庭直結は未契約 |
[Decisions, kako-jun 2026-10-21 (verbatim)]
段差はこれでいいのでは。車椅子生活になるとは思ってなかったのだし、最初からスロープだったら不自然。車椅子の子ができたと分かったあとに、この画像を渡してスロープがついた別マップに差し替えたほうがストーリー的に自然
渡り廊下がながすぎる
本堂を通らなくても左右の建物にも入口は必要だろ
右側の幼稚園のほうが大きな建物であるべき
住居と違って掃き出し窓があるべき
- **屋内の視点**: 外観と同じ向きで天井を外した見下ろし（案どおり）。
- **生成順と参照**: まず外観 TRM-03 を作る。室内3つ（TRM-04/05/02）は、採用した外観画像を参照画像に渡し「この建物のこの部屋の室内を描け」の形で作る。扉・像・墓地などの位置は、採用した外観画像で確定し、以後の参照とする。
- **材料語彙**: スキルに畳・舞台幕などを追加する（案どおり）。
[Notes]
The entrance doors of the residence and the kindergarten (決定「本堂を通らなくても左右の建物にも入口は必要だろ」) are not contracted yet (door IDs undecided): they belong to TRM-05 and TRM-02, not to this room. The steps in front of the hall belong to the exterior TRM-03 (decision 2026-10-21); this room is used in every period and keeps 扉前の段差なし・回転余地.

=== ARCHITECTURE INVARIANT TABLE (verbatim, shared by all four maps) ===
| ヒロインの住居、幼稚園、本堂は外へ出ずに屋内廊下でつながる。本堂を中央に置き、幼稚園と住居を直接接続しない。 | 屋根・外壁を保ち、本堂中央・境内から見て左（西）が住居・右（東）が幼稚園（#51 2026-10-19で左右反転。上の#60原文のdoor-east/westは旧配置の記述）。別棟や外部渡り廊下で代替しない |
| 本堂（中央）・住居（西）・幼稚園（東）は、屋根と壁のある廊下棟で外観上もつながり一つの連続した建物群に見える（根拠 docs/map-topology.md の TRM-04.door-west↔TRM-05.door-hall 渡り廊下、TRM-04.door-east↔TRM-02.door-west 屋内廊下）。 | 住居と幼稚園は直接つながない（本堂経由のみ）。吹きさらしの外部渡り廊下は不可、屋根と壁のある廊下棟は必須。屋外通路・離れた独立棟も不可。審査基準: 本堂の左右の壁面に屋根付き廊下棟が接し、棟の屋根が本堂・住居・幼稚園の屋根へ切れ目なく続く。廊下棟の両端が壁に接し、地面の隙間・雪原が屋根と屋根の間に通らない。住居と幼稚園の間に直接の廊下がない。廊下の長さ・幅・扉位置はTBDで、描き込んで確定させない |
| TRM-03 境内（外部） | 屋外境内。屋根を外した室内・家具を見せない |
| TRM-01の正本行「私立幼稚園の園庭（屋外）」／TRM-02の正本行「遊戯室（屋内）」 | 園庭と遊戯室は同じ幼稚園の外部／内部。TRM-01を室内にしない。未契約の園庭直結doorを足さない |
| TRM-04.door-west ↔ TRM-05.door-hall | 西の住居まで屋内で連続。具体的廊下形状は未確定 |
| TRM-04.door-east ↔ TRM-02.door-west | 東の幼稚園まで屋内で連続（TRM-02は本堂側の西面から入る）。扉位置・廊下長は推測しない |
| TRM-03から住居・幼稚園へ屋外を経由する新規doorは作らない。 | 境内の正面入口はTRM-04へ。住居・遊戯室の外部入口を発明しない |

#60によりTRM-03は屋外、TRM-04/TRM-05/TRM-02は屋内。本堂を中央、境内から北（本堂）を見て左＝西が住居、右＝東が幼稚園とする（#51 2026-10-19の決定。旧「住居＝東・幼稚園＝西」は廃止）。園庭TRM-01は境内TRM-03の右（東）隣で、TRM-03.door-kindergarten↔TRM-01.door-westの通用門でつなぐ。`TRM-05.door-playroom ↔ TRM-02.door-west` と `TRM-03.door-residence ↔ TRM-05.door-temple` は現行グラフから除外する。TRM-03から住居・遊戯室への屋外doorを新設しない。TRM-01↔TRM-03は園庭と境内の屋外通用門で、TRM-02への直結を意味しない。建物の外形・廊下の長さ・画面内配置・通行幅はこの接続図から推測せず、[制作前確認](production/20261018-teramachi-preflight.md)のTBDを解く。

For this image, the 2026-10-21 decisions above take precedence over any older row (for example the old east/west door text of #60, the row forbidding new outdoor doors from TRM-03, and 廊下長 TBD).

=== WHAT TO DRAW (positive description) ===
This is an INDOOR map: draw only the interior of the main hall (本堂), the CENTER building of the temple building group, as a miniature built on the same 5 mm foamboard base. VIEWPOINT (kako-jun 2026-10-21): the same orientation as the exterior reference image (north = top; the residence is on the left (west) and the kindergarten on the right (east), as in the reference), looking down with the ceiling and the roof removed, so that the inner sides of the walls and the floor are visible. The exterior of the building, the snow, the garden, the courtyard and the grounds are not drawn; every wall is a closed interior wall except the three openings below. The base top outside the walls is bare foamboard; no cotton batting, no snow, no white ledge anywhere, including in front of the south wall and door-south.
C1. The room is the main hall (本堂, 屋内) of a 浄土真宗大谷派 temple, used in every story period (全時期). Its feature is the contrast of dull gold Buddhist implements (仏具の鈍い金) against tatami (畳). The room holds the altar with the principal image Amida Nyorai (本尊は阿弥陀如来) as a standing figure (立像) and dull gold Buddhist implements, on a floor of tatami. The worship area (参拝域) is tatami and does not extend to any image edge. No sotoba (卒塔婆). No jizo.
C2. The room is the central indoor branch (中央の屋内分岐): from it one goes to the residence (west, left) and to the kindergarten (east, right) without going outside (住居・幼稚園へ外に出ず移動). The residence and the kindergarten are not directly joined: only this hall lies between them.
C3. The room is the hall shown in the exterior reference: the central, tallest building in the middle of the row of three buildings, with a corridor wing joined on its west wall and on its east wall. Each opening in the walls corresponds to what the reference shows: door-south is the lattice doors of cardboard and wooden toothpick at the middle of the hall's south face (TRM-03.door-main <-> TRM-04.door-south); door-west is where the west corridor wing meets the hall's west wall, in the southern part of that wall as in the reference; door-east is where the east corridor wing meets the hall's east wall, in the southern part of that wall as in the reference. Inside door-south the floor is level with the door sill, with no step (扉前の段差なし), and the tatami directly inside the door is left empty of altar, implements and objects as turning room (回転余地).
C4. door-west -> TRM-05.door-hall: a short corridor (渡り廊下) of tatami continues west from the hall's west wall to the residence. The corridor is of the same length relative to the hall's south-face width as the west corridor wing in the reference (about half of that width) and ends at the edge of the room's miniature, where a doorway marks the way on to the residence (the residence itself is not drawn).
C5. door-east -> TRM-02.door-west: a short indoor corridor (屋内廊下) whose floor material is chosen by the image continues east from the hall's east wall to the kindergarten, of the same length relative to the hall's south-face width as the east corridor wing in the reference (less than half of that width). A doorway at its end marks the way on to the kindergarten (the kindergarten itself is not drawn).
C6. The hall itself has no opening besides door-south, door-west and door-east; its other walls are plain closed interior walls of paper clay. The south wall of each short corridor shows, from inside, the same row of windows that the reference shows on that corridor wing (frames of wooden toothpick); nothing outdoors is visible through them. The north wall of each corridor is a plain closed wall with no windows.
C7. No steps are drawn inside the room. Do not draw any item that is not named in the source text beyond the altar, the Buddhist implements and the tatami floor; the arrangement of the tatami and the exact position of the altar are chosen by the image, and not by this text. In front of the altar the tatami is bare and empty: no cushion (no zabuton).
=== CAMERA, MATERIALS, SIZE, REFERENCE ===
FRAME: hand-made tabletop diorama, camera looks down steeper than 45 degrees from horizontal, as close to straight-down as possible (exact number is TBD; oblique is tolerated, never shallower than 45 degrees from horizontal). North = top of the image. No sky, no horizon, no vanishing point. No people, no readable text, no logos.

MATERIALS AND TOOLS (SKILL fixed vocabulary; every material must be identifiable at full size):
- Base: 5 mm foamboard, with exposed corrugated cardboard cross-section visible along the front edge of the diorama; masking tape strips and white PVA glue squeeze-out visible. No snow on the base. The base sits on a plain wooden tabletop (not asphalt, not a road surface); the table and the room remain visible around the base (do not crop the base).
- Walls: paper clay carved with a wooden toothpick (finger marks, spatula marks), matte poster paint with a flat brush (brush streaks, uneven coats). Pillars: wooden toothpick.
- Tatami: pale grass-green paper or thin cardboard with ruled lines drawn for the tatami edges and weave.
- Altar and Buddhist implements: dull gold matte poster paint on paper clay, cardboard and beads. The standing (立像) Amida Nyorai image is a small paper-clay figure painted dull gold.
- Hand-made roughness required: glue squeeze-out, thread lint, ragged hand-cut paper edges, paint unevenness, visible material seams, coarse grain.
- Paper pieces and paper-clay parts look like paper and clay (matte, soft edges), not real wood, real tatami, real metal or real stone; masking tape strips and glue squeeze-out are clearly visible at the base edges. It must read as a crude hand-made model, not a photograph.

DIMENSIONS: request 1920x1080 (16:9). If the tool cannot return it, 1672x941 or 1672x940 (16:9) is acceptable (kako-jun 2026-10-21). Any other size is a failure; never resize/crop to pass. Measure the real output file (file/identify).

REFERENCE (the only attached image): the adopted exterior image of the same temple building group (teramachi-temple-grounds-exterior-standing, 1672x941). Instruction: this is the exterior of this building. Draw the interior of THIS room, the main hall in the center, of THIS building, with the ceiling and roof removed, from the same north-up direction. Take from the reference: the order of the three buildings (residence left, main hall center, kindergarten right), the hall's footprint in the middle of the row, the lattice doors of cardboard and wooden toothpick at the middle of the hall's south face, the places where the two short corridor wings meet the hall's west and east walls, and the matte grey roof, cream walls and dark-brown matte poster paint. Do not take the snow strip along the reference base edge. The interior has no snow, no trees, no graveyard, no Shinran statue, no playground and no outdoor object, and its surfaces are hand-made paper, clay and cardboard, not the reference's photographic precision.
```
