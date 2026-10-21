# TRM-02 幼稚園の遊戯室（室内）の採用（2026-10-21、#51）

状態: **採用（TRM-02 幼稚園の遊戯室の室内）= v3**。mask・links・独立red-team未通過のため **runtimeへは切り替えない**（寺町は16枚全件通過後の一括切替。旧legacyは据え置き）。台帳statusは `recreate-required-1920x1080` のまま。時期別の画像は作らない（幼稚園は火事で無傷。TRM-02 は1枚）。

## 決定
kako-jun「よい」（2026-10-21）で v3 を採用。

## 保存物
- 保存先: `assets/images/fields/reference/teramachi-kindergarten-interior-adopted.webp`（外観参照の置き場。`scripts/verify_asset_layout.py` の許可パターン内。正本の `fields/TRM-02.webp` へはruntime切替時に移す）
- 形式: 非可逆WebP（品質85）、実寸 **1672×941 のまま（リサイズなし）**、322,080 bytes、sha256 `5673dc7e998d19396311fe83dd4ac43c556df9d6692e0203e56012e52f944848`。PNGは残さない。
- 元PNG（v3、編集の貼り戻し後）: 1672×941、sha256 `d2dc6a4c74423e703dedfcd0b11afe3548ab304faca718e23d3fbe6c745f2523`。

## 来歴
- 参照3枚（この順）: (1) 採用外観 v7（`teramachi-temple-grounds-exterior-standing`）、(2) 採用 TRM-04（`teramachi-main-hall-interior-adopted`）、(3) 割付図 `layout-trm02`（幼稚園棟のみ、690×480px、画像幅比0.41、本堂南面幅640pxに対し約1.08、奥行きは本堂の0.8。TRM-04/05 と同じ縮尺・南端）。
- 1回目（trm02.png）: 生画像レビュー(a6f3fbd) FAIL（西壁の開口が壁の中ほどで TRM-04 の東廊下の東端と高さが合わない／質感が TRM-04・05 より弱い／棟が本堂の約1.54倍で大きすぎ）。kako-jun も「幼稚園の内装が簡素すぎる。舞台が演劇の戦闘での背景とも一致してない」「おもちゃ箱とか本棚とか、端に寄せた、机とか」と指摘。
- prompt の修正: 内装（壁際のおもちゃ箱・本棚・机）、舞台（BG005 を根拠にした記述は BG005 が没のため取り消し、BG009 の構成を方向性として採用: 段ボールの低い台・緑の幕・手描きの雪山と城の書き割り）、大きさ（南壁は画像幅の約2/5）・質感（TRM-04 と同じ荒い紙粘土・爪楊枝とヘラの跡）・西壁の開口の位置（南端）。
- 2回目（v2）: 独立生画像レビュー(a6f3fbd) PASS（棟の大きさのみ未達: 南面が本堂の約1.56倍、目標1.08倍）。元PNG sha256 `6570f28c632687f1579303546f171e2be203e416e64d63c19444458d4e22b6ec`。ただし kako-jun「かなりいいのに、窓の内側に雪と木がある」。**先の決定「幼稚園の部屋から外の雪景色が見えていたほうが空間の広がりも感じる」の私の読みを訂正**: 見下ろしでは南の窓越しに見えるのは室内の床。外の雪・草・木は建物の外側の土台の上で広がりを出す。窓のガラスの中に雪や木を描かない。
- **v2 → v3（採用）の編集手順**: 南面の窓の帯を範囲限定の画像編集で、窓のガラス越しに室内の床が見えるように直した。マスク `mask-trm02-v2.png`（白=南面の窓の帯の範囲のみ、黒=不変。sha256 `90be80f17144d55c818c616e4d068e677f228c1ab711557336912224c4112654`）、imagegen の画像編集（マスク付き）を1回だけ実行、生出力 `trm02-v3-raw.png`（sha256 `92f3b96287d7672be12bc320ae3aa42fcb020f934408d1475eeddfd0c4145d58`）のマスク領域のみを v2 に貼り戻して v3 とした。マスク外の差分は784画素。編集指示: 「In the four floor-length glass windows of the south wall, replace the snow and the small trees seen inside the glass panes with the room behind the glass: through the clear glass only the dark plank floor of the room is visible … Keep the window frames, the posts, the wall, the entrance door, the snow and the trees outside the building, and everything else exactly as they are」。
- 許容した逸脱: 棟が本堂の約1.56倍。住居（約1.14倍）より大きい順序は決定どおり。kako-jun一任によるコーディネーター決定で許容（後から変更可）。
- 舞台: BG009（履歴 1bb09d0 の劇背景の候補。汚いので正本にしない）の構成を方向性として採用（BG005 は没）。劇の戦闘背景 BG010 は、この画像を参照に新規生成する。
- **4マップ（TRM-03 外観 v7・TRM-04 v11・TRM-05 v12・TRM-02 v3）の基準状態が揃った。**

## 前置き指示（wrapper、2回目）
```text
Invoke the $imagegen skill and use the built-in image_gen tool at the HIGHEST quality (quality: high), requesting 1920x1080 (16:9), to create the image described in the prompt below. Three reference images are attached, in this order: (1) the adopted exterior of the same building; (2) the adopted interior of the main hall of the same building; (3) a layout block diagram (use all three as described in the prompt). Call image_gen EXACTLY ONCE: no retries, no regeneration, no multiple candidates, even if you think the result is imperfect. Then save the REAL generated PNG (decode the tool result) into the current workspace at out/trm02-v2.png. You are STRICTLY FORBIDDEN from fabricating/drawing the image with magick/ImageMagick/PIL/Pillow/numpy/SVG/canvas/any code; only the image_gen tool. If the image_gen tool is genuinely not in your toolset, do NOT fabricate - output exactly: IMAGE_GEN_TOOL_UNAVAILABLE. Do not resize or crop the result. Do not use any files in ~/.codex/generated_images/ made by other calls; only the image generated in this call. Report the saved file path.
Output a 16:9 landscape image. Target 1920x1080; if not possible, 1672x941. Do NOT use 3:2 or 1536x1024.
```

## 送信した完全prompt（2回目の送信text、原文のまま。窓の記述は v3 の編集前の版で、窓越しは室内の床に訂正済み）
```text
Generate ONE image: the final field background for map TRM-02 (kindergarten playroom / 遊戯室, INDOOR, the EAST room of the temple building group). Do not generate any other map.

=== SOURCE TEXT (verbatim, do not paraphrase) ===
[Specification row]
| TRM-02 | 幼稚園期・火事後 | 舞台幕と小さな椅子が残る遊戯室（屋内） | door-west→TRM-04.door-east（本堂側＝西から入る）。扉位置・廊下長はTBD。舞台袖は画面内終端。TRM-05直結なし | #60/#51。本堂の東（右）。劇の自動イベント用。TRM-01と同じ幼稚園で、園庭直結は未契約 |
[Asset registry row]
| TRM-02 | `teramachi-kindergarten-hall` | 寺町 | ドア接続・舞台と通路 |
[Contract checklist row]
| TRM-02 | recreate-required-1920x1080 | R021,R024 | 旧遊戯室画像は参照専用。新背景・mask未作成 | #60/#51の東（右）の屋内幼稚園。TRM-04.door-east↔TRM-02.door-west（本堂側＝西から入る）の扉位置・廊下長、舞台袖・椅子・主路の分離、段差・幅・回転域を記録する。TRM-05直結なし |
[Rebuild candidate row]
| TRM-02 | `TRM-02-kindergarten-playroom-rebuild-candidate.png` | door-west→TRM-04.door-east | 本堂の東（右）の屋内遊戯室。扉位置TBD。舞台袖は画面内終端 | recreate-required-1920x1080 |
[Connections touching TRM-02, map-topology.md]
| TRM-04.door-east | TRM-02.door-west | door | 本堂から東（境内から北を見て右）の幼稚園への屋内廊下。TRM-02側は本堂側（西）から入るので既存IDのwestと整合。扉の位置・廊下長はTBD |
[Outdoor/indoor transition invariants]
| `TRM-04.door-east` | `TRM-02.door-west` | 中央の本堂から東（右）の幼稚園へ屋内廊下で移動。TRM-02は本堂側（西面）から入る。扉位置・廊下長TBD。舞台袖は画面内終端。 |
[Site layout section 6]
- **幼稚園（TRM-01園庭／TRM-02遊戯室）**: 園庭TRM-01は境内TRM-03の右（東）隣で寺の入口のそば。TRM-03↔TRM-01は境内東脇の通用門（door）。TRM-02は本堂TRM-04の東（右）の屋内。TRM-01↔TRM-02の直結は未契約。
| TRM-04.door-east | TRM-02.door-west | ドア（屋内廊下） | 本堂から東の幼稚園・遊戯室 |
[Specification row of the courtyard TRM-01 (same kindergarten, outdoor)]
| TRM-01 kindergarten | 幼稚園前半〜終幕 | 本堂の裏で雪遊びをする私立幼稚園の園庭（屋外） | 段丘上。bottom→TRM-08.top（正門）、door-west→TRM-03.door-kindergarten（境内の右隣の通用門） | TRM-02は同じ幼稚園の屋内。TRM-01↔TRM-02の直結doorは未契約のため描かない |

[Decision, kako-jun 2026-10-21 (verbatim message)]
畳が苦手なら幼稚園も板やりのにうむ床にしろ
(reading: 板張りかリノリウム)
[Decision, kako-jun 2026-10-21 (verbatim)]
部屋以外の外側の空間には外の景色を書けばいいのではないのか。雪とか草とか木とか。その位置が他の画像と比べて厳密に一致してなくてもプレイヤーは気にしない。白いダンボールで埋めるのは不自然。幼稚園の部屋から外の雪景色が見えていたほうが空間の広がりも感じる
[Decisions, kako-jun 2026-10-21 (verbatim; 「板やりのにうむ」 was read as 「板張りかリノリウム」)]
畳が苦手なら幼稚園も板やりのにうむ床にしろ
住居と違って掃き出し窓があるべき
右側の幼稚園のほうが大きな建物であるべき
本堂を通らなくても左右の建物にも入口は必要だろ
部屋以外の外側の空間には外の景色を書けばいいのではないのか。雪とか草とか木とか。その位置が他の画像と比べて厳密に一致してなくてもプレイヤーは気にしない。白いダンボールで埋めるのは不自然。幼稚園の部屋から外の雪景色が見えていたほうが空間の広がりも感じる
よいが、仏壇前の柵や注意書きはいらない。参考写真は観光用のかもね。実際は個人の寺にはないものだ
火事では住居棟だけ全部燃える。本堂や幼稚園には被害はない。父親の寝室が一番被害は少ない
住居部分は幼馴染の個室もあるだろう。そこに化石が置かれる。燃えるのは台所とその部屋とかだ。幼稚園のトイレは住居と兼用でもいい
[Decisions, kako-jun 2026-10-21 (verbatim)]
幼稚園の内装が簡素すぎる。舞台が演劇の戦闘での背景とも一致してない
おもちゃ箱とか本棚とか、端に寄せた、机とか
[Notes]
The kindergarten is undamaged by the fire (no before/after difference for this room). The entrance door of the kindergarten belongs to a connection not yet contracted (door ID undecided); the exterior shows it. The toilet may be shared with the residence and is not drawn.

=== ARCHITECTURE INVARIANT TABLE (verbatim, shared by all four maps) ===
| ヒロインの住居、幼稚園、本堂は外へ出ずに屋内廊下でつながる。本堂を中央に置き、幼稚園と住居を直接接続しない。 | 屋根・外壁を保ち、本堂中央・境内から見て左（西）が住居・右（東）が幼稚園（#51 2026-10-19で左右反転。上の#60原文のdoor-east/westは旧配置の記述）。別棟や外部渡り廊下で代替しない |
| 本堂（中央）・住居（西）・幼稚園（東）は、屋根と壁のある廊下棟で外観上もつながり一つの連続した建物群に見える（根拠 docs/map-topology.md の TRM-04.door-west↔TRM-05.door-hall 渡り廊下、TRM-04.door-east↔TRM-02.door-west 屋内廊下）。 | 住居と幼稚園は直接つながない（本堂経由のみ）。吹きさらしの外部渡り廊下は不可、屋根と壁のある廊下棟は必須。屋外通路・離れた独立棟も不可。審査基準: 本堂の左右の壁面に屋根付き廊下棟が接し、棟の屋根が本堂・住居・幼稚園の屋根へ切れ目なく続く。廊下棟の両端が壁に接し、地面の隙間・雪原が屋根と屋根の間に通らない。住居と幼稚園の間に直接の廊下がない。廊下の長さ・幅・扉位置はTBDで、描き込んで確定させない |
| TRM-03 境内（外部） | 屋外境内。屋根を外した室内・家具を見せない |
| TRM-01の正本行「私立幼稚園の園庭（屋外）」／TRM-02の正本行「遊戯室（屋内）」 | 園庭と遊戯室は同じ幼稚園の外部／内部。TRM-01を室内にしない。未契約の園庭直結doorを足さない |
| TRM-04.door-west ↔ TRM-05.door-hall | 西の住居まで屋内で連続。具体的廊下形状は未確定 |
| TRM-04.door-east ↔ TRM-02.door-west | 東の幼稚園まで屋内で連続（TRM-02は本堂側の西面から入る）。扉位置・廊下長は推測しない |
| TRM-03から住居・幼稚園へ屋外を経由する新規doorは作らない。 | 境内の正面入口はTRM-04へ。住居・遊戯室の外部入口を発明しない |

#60によりTRM-03は屋外、TRM-04/TRM-05/TRM-02は屋内。本堂を中央、境内から北（本堂）を見て左＝西が住居、右＝東が幼稚園とする（#51 2026-10-19の決定。旧「住居＝東・幼稚園＝西」は廃止）。園庭TRM-01は境内TRM-03の右（東）隣で、TRM-03.door-kindergarten↔TRM-01.door-westの通用門でつなぐ。`TRM-05.door-playroom ↔ TRM-02.door-west` と `TRM-03.door-residence ↔ TRM-05.door-temple` は現行グラフから除外する。TRM-03から住居・遊戯室への屋外doorを新設しない。TRM-01↔TRM-03は園庭と境内の屋外通用門で、TRM-02への直結を意味しない。建物の外形・廊下の長さ・画面内配置・通行幅はこの接続図から推測せず、[制作前確認](production/20261018-teramachi-preflight.md)のTBDを解く。

For this image, the 2026-10-21 decisions above take precedence over any older row (for example the rows that say 幼稚園期・火事後, 屋外doorなし, or 畳).

=== WHAT TO DRAW (positive description) ===
This is an INDOOR map: draw only the interior of the kindergarten playroom (遊戯室), inside the EAST building of the temple building group (right when looking north from the grounds), as a miniature built on the same 5 mm foamboard base, at the same scale as the main hall of the adopted TRM-04 image. VIEWPOINT (kako-jun 2026-10-21): the same orientation as the exterior reference image (north = top), looking down with the ceiling and the roof removed, so that the inner sides of the walls and the floor are visible. The roof and the outer faces of the building's walls are not drawn; every wall is a closed interior wall except the openings below. The ground outside the building's walls, all over the base, is outdoor scenery: cotton-batting snow with a little grass showing through, and several trees (bare leafless winter trees of thin wire and yarn, and snow-covered evergreen trees of green sponge), the same kind of scenery as the exterior reference; nothing of the outdoor scenery enters the room: the floor inside the walls is only the room floor described below. Outside the walls there is only snow, grass and trees; the graveyard, the playground and its equipment, the Shinran statue, the stone paving and the stone steps of the exterior reference are not drawn. Trees stand clear of the walls (none overlaps a wall or window). The snowy scenery spreads out around the building and is seen through the room's floor-length windows, giving a sense of space.
C1. The room is the playroom (遊戯室, 屋内) of the private kindergarten run by the temple, in the east building (right) of the row of three; it is the largest of the three buildings. It keeps a stage curtain and small chairs that are left standing in it (舞台幕と小さな椅子が残る). The room is undamaged: no fire, no smoke, no damage.
C2. The room holds a stage and, around it, the furnishing of a kindergarten playroom. The stage is a low stage platform of corrugated cardboard with a worn plank floor, its front edge showing the corrugated cardboard section and masking tape; at the back a green curtain of cloth or paper with a scalloped gathered top; in front of it a row of hand-painted cardboard backdrop panels with blue-white snowy mountains, clouds and a castle with red-roofed towers (matte poster paint, cut-out edges visible). The stage wings (舞台袖) end inside the frame. Toy boxes, bookshelves and tables are pushed against the walls (the floor in the middle is left clear for the play): along the north wall beside the stage and along the east wall, not under the south windows; several of each kind, their places chosen by the image; picture books and toys show no readable characters. Several small chairs (小さな椅子, hand-made of cardboard and wooden toothpicks) are left standing, gathered near the edges. The floor inside door-west and along the south side to the entrance door is left clear. Nothing else is specified in the source text; the exact arrangement is chosen by the image. This is a kindergarten of a neighbourhood temple: no tourist signs, no fences, no notices.
C3. The footprint of the room follows the layout diagram (third attached image): a single rectangle, wider than the residence (left building) in the first image, about one and one tenth of the hall's width in the TRM-04 image, standing at the same scale as the hall of the adopted TRM-04 image: the room's south wall spans about two fifths of the image width, the footprint is wider than it is deep, as in the layout diagram; wide snow margins remain on the left and the right of the building. The kindergarten's south wall spans about two fifths of the image width (the TRM-04 hall spans about two fifths as well, slightly less); wide snow margins remain on the left and the right of the building; as in the layout diagram.
C4. The south wall of the kindergarten has the row of floor-length sliding glass windows shown on the kindergarten's south face in the first image (about four panels, provisional) (掃き出し窓: tall glass windows that reach the floor and open toward the snowy ground outside; these are windows, not doors; frames of wooden toothpick) and, separate from the windows at the east end of the south wall, one entrance door as in the exterior reference: a wooden sliding or hinged door of cardboard and wooden toothpick set in the wall itself, with the snow in front of it level with its sill and no step. The windows look out onto the snowy scenery. The entrance door opens to the outside; no other door leads outside.
C5. door-west -> TRM-04.door-east: in the southern part of the west wall there is an open doorway spanning the corridor's width: two wooden-toothpick posts and a lintel beam seen from above, and a pale threshold strip across the floor at the line of the west wall. The floor runs out to the threshold, and the snow begins directly beyond it. The opening faces west, toward the left edge of the image: the way out through it leads toward the left edge. There is no door leaf. This opening matches the east threshold of the east corridor in the adopted TRM-04 image. The open doorway in the west wall is at the southern end of the west wall: its south post stands close to the building's south-west corner, and the wall continues plain and closed to the north of the doorway, as in the east end of the corridor of the TRM-04 image (the corridor's south wall is level with the hall's south wall). The rest of the west wall is a plain closed wall.
C6. The north wall and the east wall are plain closed interior walls of paper clay without openings or windows. There is no connection to the residence.
C7. The floor of the room is either a plank floor (thin cardboard strips painted matte brown, joints drawn as thin lines, the same boards as in the adopted TRM-04 image) or a linoleum floor (a smooth flat sheet of matte colored paper); the image chooses one of the two; no tatami in this room. The stage is a low raised platform; apart from the stage, the floor is level and no steps are drawn.
=== CAMERA, MATERIALS, SIZE, REFERENCE ===
FRAME: hand-made tabletop diorama, camera looks down steeper than 45 degrees from horizontal, as close to straight-down as possible (exact number is TBD; oblique is tolerated, never shallower than 45 degrees from horizontal). North = top of the image. No sky, no horizon, no vanishing point. No people, no readable text, no logos.

MATERIALS AND TOOLS (SKILL fixed vocabulary; every material must be identifiable at full size):
- Base: 5 mm foamboard, with exposed corrugated cardboard cross-section visible along the front edge of the diorama; masking tape strips and white PVA glue squeeze-out visible. Outside the walls the base carries the outdoor scenery described above. The base sits on a plain wooden tabletop (not asphalt, not a road surface); the table and the room remain visible around the base (do not crop the base).
- Walls: walls of rough paper clay with visible toothpick and spatula marks and cracks, exactly like the adopted TRM-04 image; matte poster paint with a flat brush (brush streaks, uneven coats), cream walls and dark-brown frames as in the adopted TRM-04 image. Pillars and frames: wooden toothpick.
- Floor: floor boards of thin cardboard strips with uneven cut edges, painted matte brown, joints drawn as thin lines; or linoleum of a smooth flat sheet of matte colored paper.
- Stage platform: corrugated cardboard, matte poster paint.
- Stage: corrugated cardboard platform with its cut section and masking tape visible at the front edge, worn plank floor of thin cardboard strips; green curtain of cloth or paper with a scalloped gathered top; backdrop panels of hand-painted corrugated cardboard (matte poster paint, cut-out edges visible).
- Toy boxes, bookshelves and tables: cardboard, paper clay, colored paper and wooden toothpicks.
- Stage curtain: cloth or paper gathered by hand with ragged hand-cut edges. Small chairs: cardboard and wooden toothpicks.
- Scenery outside the walls: snow = cotton batting fixed with white PVA glue; grass = small tufts of green yarn; bare trees = thin wire and yarn; evergreen trees = green sponge and yarn with cotton snow on the branches.
- Small items: beads and buttons.
- Hand-made roughness required: glue squeeze-out, thread lint, ragged hand-cut paper edges, paint unevenness, visible material seams, coarse grain.
- Paper pieces and paper-clay parts look like paper and clay (matte, soft edges), not real wood, real metal or real stone; masking tape strips and glue squeeze-out are clearly visible at the base edges. It must read as a crude hand-made model, not a photograph.

DIMENSIONS: request 1920x1080 (16:9). If the tool cannot return it, 1672x941 or 1672x940 (16:9) is acceptable (kako-jun 2026-10-21). Any other size is a failure; never resize/crop to pass. Measure the real output file (file/identify).

REFERENCE (three attached images, in this order: first the adopted exterior, second the adopted interior of the main hall, third the layout block diagram). First image: the exterior of the same temple building group; this room is the interior of the right (east) building, the kindergarten, of THAT building; take from it the kindergarten's outline relative to the hall, the row of floor-length windows and the entrance door of its south face, and the outdoor scenery style (snow, a little grass, trees). Second image: the interior of the main hall of the same building group; take from it the materials, colors, plank floor, wall construction and the viewing angle, so that the two interiors look like parts of one model; the east threshold of its east corridor is where this room's west opening (C5) attaches. Third image: a layout block diagram: copy its rectangle's proportions and position exactly, and copy the rectangle's size relative to the image frame exactly; it carries no style. Do not copy its colors or lines into the model; the rectangle of the diagram is not drawn in the picture. Do not take the main hall's altar, shrine, notices or children's drawings into this room, and nothing from the exterior's graveyard, playground, statue or stone paving.
```
