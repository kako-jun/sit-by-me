# TRM-05 住居（室内、中3の火事前の基準状態）の採用（2026-10-21、#51）

状態: **採用（TRM-05 住居の室内。中3・火事前の基準状態）**。mask・links・独立red-team未通過のため **runtimeへは切り替えない**（寺町は16枚全件通過後の一括切替。旧legacyは据え置き）。台帳statusは `recreate-required-1920x1080` のまま。時期別（幼稚園期・小学校以降・火事の時点・火事後）は別画像・未決（Issue #51）。

## 決定
kako-jun「採用でいい」（2026-10-21）。

## 保存物
- 保存先: `assets/images/fields/reference/teramachi-residence-interior-adopted.webp`（外観参照の置き場。`scripts/verify_asset_layout.py` の許可パターン内。正本の `fields/TRM-05.webp` へはruntime切替時に移す）
- 形式: 非可逆WebP（品質85）、実寸 **1672×941 のまま（リサイズなし）**、316,742 bytes、sha256 `353859f04c2bac75f5b872d68843633b16bc26dc2054e0b5d0b1cb3a828948af`。PNGは残さない。
- 元PNG（v12）: 1672×941、sha256 `3fefe4c3cb19d29a3d6b7b30a68185e1a3f5bf6982be810d9007b09ed287f931`。

## 来歴
- 参照3枚（この順）: (1) 採用外観（`teramachi-temple-grounds-exterior-standing`）、(2) 採用 TRM-04（`teramachi-main-hall-interior-adopted`）、(3) 割付図 `layout-trm05`（住居棟のみ、520×510px、画像幅比0.31、ほぼ正方形、本堂南面幅640pxに対し約0.81）。
- 生成と編集の経緯（v1〜v12）:
  - v1: 建物の大きさと形のみ不合格（住居の南面が本堂の約1.53倍、横長1.9。室内・扉と窓・door-hall・外の景色は合格）→ prompt に「画像幅の約1/3・ほぼ正方形」を足し、割付図を500×490から520×510pxに作り直した。
  - v2: kako-jun「寝室が1つなのは変だろ。2人暮らし」「化石の形がおかしい。アンモナイトじゃない」→ 寝室2つ（父の寝室・幼馴染の個室）、化石は割っていない川の石（のち「ゴツゴツした茶色と黒」）に。
  - v3〜v7: 台所の設備を昭和らしく（ガスコンロ等）、玄関扉の位置・寝室への出入口の柱や梁が見えない等の指摘を、prompt と範囲限定編集で順に直した（各回の詳細は Issue #51 のコメントと作業記録）。
  - v8: kako-jun「左に移せ。別画像にしろ。柱2本の意味がわからん。ないほうがいい」→ 外観の扉を左へ（外観 v7）、寝室の出入口の柱・敷居の台座は不要、時期別は別画像。
  - v9: 柱を消す編集で仕切りの壁ごと消え、kako-jun が「部屋の仕切りもへんになった」と不採用。外観 v6（扉と窓が重なる）も同時に不採用。
  - v10・v11: 仕切りの再編集（壁の途切れだけの素直な開口）を試みたが採用に至らず。
  - **v12（採用）**: v8 を土台に、v4 の元の仕切りを PIL で切り貼りした。
- 独立生画像レビュー: 室内・扉と窓・door-hall・外の景色は合格（v1 時点の良い点）。採用は kako-jun の判断。
- 許容した逸脱: 住居が本堂の約1.14倍の大きさ（割付図の0.81より大きい）、仕切りは最初の版（v4）のまま。
- 注意: 室内の玄関扉は建物の左端寄り（外観 v7 に一致）、東壁の開口（柱2本・まぐさ・敷居の帯）は変更していない（「柱の意味が分からない」が当てはまるかは要確認）。

## 前置き指示（wrapper）
```text
Invoke the $imagegen skill and use the built-in image_gen tool at the HIGHEST quality (quality: high), requesting 1920x1080 (16:9), to create the image described in the prompt below. Three reference images are attached, in this order: (1) the adopted exterior of the same building; (2) the adopted interior of the main hall of the same building; (3) a layout block diagram (use all three as described in the prompt). Call image_gen EXACTLY ONCE: no retries, no regeneration, no multiple candidates, even if you think the result is imperfect. Then save the REAL generated PNG (decode the tool result) into the current workspace at out/trm05.png. You are STRICTLY FORBIDDEN from fabricating/drawing the image with magick/ImageMagick/PIL/Pillow/numpy/SVG/canvas/any code; only the image_gen tool. If the image_gen tool is genuinely not in your toolset, do NOT fabricate - output exactly: IMAGE_GEN_TOOL_UNAVAILABLE. Do not resize or crop the result. Do not use any files in ~/.codex/generated_images/ made by other calls; only the image generated in this call. Report the saved file path.
Output a 16:9 landscape image. Target 1920x1080; if not possible, 1672x941. Do NOT use 3:2 or 1536x1024.
```

## 完全prompt（採用時点の prompt-trm05.md の送信text。v8 生成時点以降の改訂を含む。各回の送信textは作業記録）
```text
Generate ONE image: the final field background for map TRM-05 (residence / 庫裏, INDOOR, the WEST room of the temple building group). Do not generate any other map.

=== SOURCE TEXT (verbatim, do not paraphrase) ===
[Specification row]
| TRM-05 residence | 全時期 | 庫裏の台所と幼馴染の部屋（屋内） | door-hall→中央TRM-04のdoor-west。TRM-02直結なし | #60/#51。本堂の西（左）。台所は火事イベントの場所 |
[Asset registry row]
| TRM-05 | `assets/images/fields/legacy/TRM-05.webp` | 寺町 | retired-replacement-required |
[Contract checklist row]
| TRM-05 | recreate-required-1920x1080 | R006,R011,R021,R024 | 旧庫裏画像は参照専用。新背景・mask未作成 | #60/#51の西（本堂から見て左）の屋内住居。TRM-04.door-west↔door-hallのみ。内部廊下の扉位置、幅・段差・回転域、火事時遮断範囲がTBD。TRM-02直結なし |
[Rebuild candidate row]
| TRM-05 | `TRM-05-temple-residence-rebuild-v3-candidate.png` | door-hall→TRM-04.door-west | 屋内庫裏。本堂の西（左）。TRM-02直結なし | recreate-required-1920x1080 |
[Connections touching TRM-05, map-topology.md]
| TRM-04.door-west | TRM-05.door-hall | door | 本堂から西（境内から北を見て左）の庫裏（住居）への渡り廊下 |
[Outdoor/indoor transition invariants]
| `TRM-04.door-west` | `TRM-05.door-hall` | 本堂から西（左）の庫裏へ渡る廊下。畳廊下の方位と扉位置を一致させる。扉位置TBD。 |
[Site layout section 6]
- **庫裏（TRM-05）**: 本堂の西（左）。渡り廊下TRM-04.door-west↔TRM-05.door-hall。幼稚園職員室への廊下は#60で廃止（住居↔幼稚園は直結しない）。
| TRM-04.door-west | TRM-05.door-hall | ドア（渡り廊下） | 本堂（中央）から西の住居。内部どうし |
[Old section 3.1 note (reference only; connection ledger v2 takes precedence)]
| `temple-grounds` →（庫裏のドア）→ `temple-residence-interior` | 屋内。ドア遷移（#842）。台所・板の間・幼馴染の部屋 |

[Decision, kako-jun 2026-10-21 (verbatim)]
住居部分は幼馴染の個室もあるだろう。そこに化石が置かれる。燃えるのは台所とその部屋とかだ。幼稚園のトイレは住居と兼用でもいい
[Decision, kako-jun 2026-10-21 (verbatim)]
住居も板張りでいいが、畳でなく細長いロールござを展開とかにしてもいい
[Decision, kako-jun 2026-10-21 (verbatim)]
部屋以外の外側の空間には外の景色を書けばいいのではないのか。雪とか草とか木とか。その位置が他の画像と比べて厳密に一致してなくてもプレイヤーは気にしない。白いダンボールで埋めるのは不自然。幼稚園の部屋から外の雪景色が見えていたほうが空間の広がりも感じる
[Neighbouring maps, map-specifications.md (verbatim)]
| TRM-03 temple-grounds | 全時期 | 親鸞像のある浄土真宗の境内（屋外） | bottom→TRM-07、door-main→TRM-04、door-kindergarten→TRM-01.door-west | #60/#51。本堂中心・境内から見て左（西）住居・右（東）幼稚園の同じ建物群。TRM-01は境内の右隣。住居／遊戯室への屋外doorなし |
| TRM-04 | 全時期 | 仏具の鈍い金と畳が対照になる本堂（屋内） | door-south→TRM-03、door-west→TRM-05.door-hall、door-east→TRM-02.door-west。参拝域は端へ出ない | #60。中央の屋内分岐。住居・幼稚園へ外に出ず移動 |
| TRM-02 | 幼稚園期・火事後 | 舞台幕と小さな椅子が残る遊戯室（屋内） | door-west→TRM-04.door-east（本堂側＝西から入る）。扉位置・廊下長はTBD。舞台袖は画面内終端。TRM-05直結なし | #60/#51。本堂の東（右）。劇の自動イベント用。TRM-01と同じ幼稚園で、園庭直結は未契約 |
[Decisions, kako-jun 2026-10-21 (verbatim)]
本堂を通らなくても左右の建物にも入口は必要だろ
住居と違って掃き出し窓があるべき
住居部分は幼馴染の個室もあるだろう。そこに化石が置かれる。燃えるのは台所とその部屋とかだ。幼稚園のトイレは住居と兼用でもいい
住居も板張りでいいが、畳でなく細長いロールござを展開とかにしてもいい
部屋以外の外側の空間には外の景色を書けばいいのではないのか。雪とか草とか木とか。その位置が他の画像と比べて厳密に一致してなくてもプレイヤーは気にしない。白いダンボールで埋めるのは不自然。幼稚園の部屋から外の雪景色が見えていたほうが空間の広がりも感じる
よいが、仏壇前の柵や注意書きはいらない。参考写真は観光用のかもね。実際は個人の寺にはないものだ
[Notes]
The entrance door in the residence's south wall belongs to a connection not yet contracted (door ID undecided); the exterior shows it. The state of the room before or after the fire is not defined in the ledger: this image shows the room BEFORE the fire (provisional).

=== ARCHITECTURE INVARIANT TABLE (verbatim, shared by all four maps) ===
| ヒロインの住居、幼稚園、本堂は外へ出ずに屋内廊下でつながる。本堂を中央に置き、幼稚園と住居を直接接続しない。 | 屋根・外壁を保ち、本堂中央・境内から見て左（西）が住居・右（東）が幼稚園（#51 2026-10-19で左右反転。上の#60原文のdoor-east/westは旧配置の記述）。別棟や外部渡り廊下で代替しない |
| 本堂（中央）・住居（西）・幼稚園（東）は、屋根と壁のある廊下棟で外観上もつながり一つの連続した建物群に見える（根拠 docs/map-topology.md の TRM-04.door-west↔TRM-05.door-hall 渡り廊下、TRM-04.door-east↔TRM-02.door-west 屋内廊下）。 | 住居と幼稚園は直接つながない（本堂経由のみ）。吹きさらしの外部渡り廊下は不可、屋根と壁のある廊下棟は必須。屋外通路・離れた独立棟も不可。審査基準: 本堂の左右の壁面に屋根付き廊下棟が接し、棟の屋根が本堂・住居・幼稚園の屋根へ切れ目なく続く。廊下棟の両端が壁に接し、地面の隙間・雪原が屋根と屋根の間に通らない。住居と幼稚園の間に直接の廊下がない。廊下の長さ・幅・扉位置はTBDで、描き込んで確定させない |
| TRM-03 境内（外部） | 屋外境内。屋根を外した室内・家具を見せない |
| TRM-01の正本行「私立幼稚園の園庭（屋外）」／TRM-02の正本行「遊戯室（屋内）」 | 園庭と遊戯室は同じ幼稚園の外部／内部。TRM-01を室内にしない。未契約の園庭直結doorを足さない |
| TRM-04.door-west ↔ TRM-05.door-hall | 西の住居まで屋内で連続。具体的廊下形状は未確定 |
| TRM-04.door-east ↔ TRM-02.door-west | 東の幼稚園まで屋内で連続（TRM-02は本堂側の西面から入る）。扉位置・廊下長は推測しない |
| TRM-03から住居・幼稚園へ屋外を経由する新規doorは作らない。 | 境内の正面入口はTRM-04へ。住居・遊戯室の外部入口を発明しない |

#60によりTRM-03は屋外、TRM-04/TRM-05/TRM-02は屋内。本堂を中央、境内から北（本堂）を見て左＝西が住居、右＝東が幼稚園とする（#51 2026-10-19の決定。旧「住居＝東・幼稚園＝西」は廃止）。園庭TRM-01は境内TRM-03の右（東）隣で、TRM-03.door-kindergarten↔TRM-01.door-westの通用門でつなぐ。`TRM-05.door-playroom ↔ TRM-02.door-west` と `TRM-03.door-residence ↔ TRM-05.door-temple` は現行グラフから除外する。TRM-03から住居・遊戯室への屋外doorを新設しない。TRM-01↔TRM-03は園庭と境内の屋外通用門で、TRM-02への直結を意味しない。建物の外形・廊下の長さ・画面内配置・通行幅はこの接続図から推測せず、[制作前確認](production/20261018-teramachi-preflight.md)のTBDを解く。

For this image, the 2026-10-21 decisions above take precedence over any older row (for example the rows that say 畳, 屋外doorなし, or that forbid a new door from TRM-03 to the residence).

=== WHAT TO DRAW (positive description) ===
This is an INDOOR map: draw only the interior of the residence (庫裏), the WEST building of the temple building group (left when looking north from the grounds), as a miniature built on the same 5 mm foamboard base, at the same scale as the main hall of the adopted TRM-04 image. VIEWPOINT (kako-jun 2026-10-21): the same orientation as the exterior reference image (north = top), looking down with the ceiling and the roof removed, so that the inner sides of the walls and the floor are visible. The roof and the outer faces of the building's walls are not drawn; every wall is a closed interior wall except the two openings below. The ground outside the building's walls, all over the base, is outdoor scenery: cotton-batting snow with a little grass showing through, and several trees (bare leafless winter trees of thin wire and yarn, and snow-covered evergreen trees of green sponge), the same kind of scenery as the reference; nothing of the outdoor scenery enters the room: the floor inside the walls is only the room floor described below. Outside the walls there is only snow, grass and trees; the graveyard, the playground and its equipment, the Shinran statue, the stone paving and the stone steps of the exterior reference are not drawn. Trees stand clear of the walls (none overlaps a wall or window). Seen through the residence's windows, the snowy scenery outside gives a sense of space.
C1. The room is the residence (庫裏) of the temple: the kitchen and the childhood friend's room (庫裏の台所と幼馴染の部屋, 屋内), used in every story period (全時期). It is the west building (left) of the row of three. The residence is smaller than the kindergarten building. This image shows the room before the fire; draw no fire, smoke or damage.
C2. The residence is the home of two people, the father (the head of the kindergarten) and the childhood friend. It contains the kitchen (台所), the wooden-floor area (板の間), and two bedrooms: the father's bedroom and the childhood friend's private room (幼馴染の個室). In the picture the father's bedroom is the room in the south-east and the childhood friend's private room is the room in the north-east; the kitchen and the wooden-floor area occupy the rest of the building. This is the room as it is in the third year of junior high school, before the fire (provisional). The wooden-floor area holds a table. The partition between the wooden-floor area and the bedrooms is one straight continuous partition wall with two plain doorway gaps, one for each bedroom, and the wall ends are flat; each doorway is simply an open gap in the partition wall: the wall ends are plain cut ends and the plank floor runs continuously through the gap; nothing stands in the gap. The other partition walls and the exact sizes of the rooms are chosen by the image. In the childhood friend's private room is kept the fossil (化石) the two of them picked up in the river: a rough, craggy, uneven stone, mottled brown and black, about the size of a fist, unbroken, with nothing visible inside. The kitchen has Showa-era furnishings: a two-burner gas range on a small stand, a tiled or stainless-steel sink with a faucet, an enamel pot, a plain wooden dish cupboard with glass doors, a small round-cornered refrigerator; all hand-made of cardboard, paper clay and paper (the era of the world stays the present day; only the kitchen fittings are Showa-style). This is an ordinary neighbourhood temple residence: no notices, no fences and no tourist signs.
C3. The footprint of the room follows the layout diagram (third attached image): a single rectangle, about four fifths of the hall's width in the TRM-04 image: the residence's south wall spans about one third of the image width (the TRM-04 hall spans about two fifths), and the footprint is nearly square, as deep as it is wide, as in the layout diagram; wide snow margins remain on the left and the right of the building and slightly less deep than the hall, standing at the same scale as the hall of the adopted TRM-04 image.
C4. The south wall of the residence has two ordinary waist-height windows (no floor-length windows; frames of wooden toothpick) and one entrance door: the entrance door in the south wall stands in the left half of the building, at about the left quarter to third of the building's width, in front of the wooden-floor area (板の間, the room with the table), a wooden sliding or hinged door of cardboard and wooden toothpick set in the wall itself, with the snow in front of it level with its sill and no step. The windows look out onto the snowy scenery. The entrance door opens to the outside; no other door leads outside.
C5. door-hall -> TRM-04.door-west: in the southern part of the east wall there is an open doorway spanning the corridor's width: two wooden-toothpick posts and a lintel beam seen from above, and a pale threshold strip across the floor at the line of the east wall. The plank floor runs out to the threshold, and the snow begins directly beyond it. The opening faces east, toward the right edge of the image: the way out through it leads toward the right edge. There is no door leaf. This opening matches the west threshold of the west corridor in the adopted TRM-04 image. The rest of the east wall is a plain closed wall.
C6. The north wall and the west wall are plain closed interior walls of paper clay without openings or windows. There is no connection to the kindergarten.
C7. The floor of the room is either a plank floor (thin cardboard strips painted matte brown, joints drawn as thin lines, the same boards as in the adopted TRM-04 image) or a narrow rolled-out rush mat (ござ: narrow bands of thin straw-colored cut paper or woven thin paper cord, unrolled over the plank floor); the image chooses; the kitchen and the wooden-floor area have the plank floor. No steps are drawn inside the room.
=== CAMERA, MATERIALS, SIZE, REFERENCE ===
FRAME: hand-made tabletop diorama, camera looks down steeper than 45 degrees from horizontal, as close to straight-down as possible (exact number is TBD; oblique is tolerated, never shallower than 45 degrees from horizontal). North = top of the image. No sky, no horizon, no vanishing point. No people, no readable text, no logos.

MATERIALS AND TOOLS (SKILL fixed vocabulary; every material must be identifiable at full size):
- Base: 5 mm foamboard, with exposed corrugated cardboard cross-section visible along the front edge of the diorama; masking tape strips and white PVA glue squeeze-out visible. Outside the walls the base carries the outdoor scenery described above. The base sits on a plain wooden tabletop (not asphalt, not a road surface); the table and the room remain visible around the base (do not crop the base).
- Walls: paper clay carved with a wooden toothpick (finger marks, spatula marks), matte poster paint with a flat brush (brush streaks, uneven coats), cream walls and dark-brown frames as in the adopted TRM-04 image. Pillars and frames: wooden toothpick.
- Floor: plank floor of thin cardboard strips painted matte brown, joints drawn as thin lines; or rush mat of thin straw-colored cut paper bands over it.
- Scenery outside the walls: snow = cotton batting fixed with white PVA glue; grass = small tufts of green yarn; bare trees = thin wire and yarn; evergreen trees = green sponge and yarn with cotton snow on the branches.
- Small items: cardboard, paper clay (the fossil), beads and buttons.
- Hand-made roughness required: glue squeeze-out, thread lint, ragged hand-cut paper edges, paint unevenness, visible material seams, coarse grain.
- Paper pieces and paper-clay parts look like paper and clay (matte, soft edges), not real wood, real metal or real stone; masking tape strips and glue squeeze-out are clearly visible at the base edges. It must read as a crude hand-made model, not a photograph.

DIMENSIONS: request 1920x1080 (16:9). If the tool cannot return it, 1672x941 or 1672x940 (16:9) is acceptable (kako-jun 2026-10-21). Any other size is a failure; never resize/crop to pass. Measure the real output file (file/identify).

REFERENCE (three attached images, in this order: first the adopted exterior, second the adopted interior of the main hall, third the layout block diagram). First image: the exterior of the same temple building group; this room is the interior of the left (west) building, the residence, of THAT building; take from it the residence's outline relative to the hall, the two waist-height windows and the entrance door of its south face, and the outdoor scenery style (snow, a little grass, trees). Second image: the interior of the main hall of the same building group; take from it the materials, colors, plank floor, wall construction and the viewing angle, so that the two interiors look like parts of one model; the west threshold of its west corridor is where this room's east opening (C5) attaches. Third image: a layout block diagram: copy its rectangle's proportions and position exactly, and copy the rectangle's size relative to the image frame and its square proportion exactly; it carries no style. Do not copy its colors or lines into the model; the rectangle of the diagram is not drawn in the picture. Do not take the main hall's altar, shrine, notices or children's drawings into this room, and nothing from the exterior's graveyard, playground, statue or stone paving.
```
