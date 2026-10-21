# TRM-03 立位期の採用外観（2026-10-21、#51）

状態: **採用外観（立位期のTRM-03）。室内3MAP（TRM-04/05/02）生成の唯一の参照画像**。mask・links・独立red-team未通過のため **runtimeへは切り替えない**（寺町は16枚全件通過後の一括切替。旧legacyは据え置き）。台帳statusは `recreate-required-1920x1080` のまま。

## 決定（kako-jun 2026-10-21、逐語）
「段差はこれでいいのでは。車椅子生活になるとは思ってなかったのだし、最初からスロープだったら不自然。車椅子の子ができたと分かったあとに、この画像を渡してスロープがついた別マップに差し替えたほうがストーリー的に自然」

- 本堂前の2段の石段は、立位期のTRM-03では許容する。「段差を主路にせず／扉前に回転余地を残す／車椅子通路」は、**車椅子期の別マップ（この外観を参照にスロープ付きで差し替える）**に適用する。車椅子期の別マップ（新ID・MAP数・接続・差し替えの時点）は未決（Issue #51）。

## 保存物
- 保存先: `assets/images/fields/reference/teramachi-temple-grounds-exterior-standing.webp`（外観参照の置き場。`scripts/verify_asset_layout.py` の許可パターン内。正本の `fields/TRM-03.webp` へはruntime切替時に移す）
- 形式: 非可逆WebP（品質85、`magick in.png -quality 85 out.webp`）、実寸 **1672×941 のまま（リサイズなし）**、391,674 bytes、sha256 `3c9d1ce7474610616b60a8a7e2ef83bd963c1d769518a0e44e9c38045ac30566`。
- 元PNG（生成原本、リポには置かない）: 1672×941、sha256 `4e27dbd2b085641cc158b33f0688a3e9d10269d4ecb05a65d75f1f3f20a6fb7f`。アルファなし（RGB）。

## 来歴
- 生成: 5回目（v5）。参照画像なし（テキストのみ）。codex exec で $imagegen を明示起動、1回のみ。寸法 1672×941（16:9。#51の決定により許容）、リサイズなし。
- 独立生画像レビュー(aab04e2): FAIL理由は本堂前の2段の石段のみ。上の決定で解消（立位期は石段を許容）。
- 軽微な逸脱（来歴のみ・今回は再生成しない）: 掃き出し窓越しにぬいぐるみが見える／墓石に彫り跡がある／南面の前に木が立つ箇所がある／棟端が鬼瓦風／ブランコ・そりの材質が本物の木に見える。
- 寸法関係: 外観の廊下棟は短く、幼稚園棟は住居棟より大きく、幼稚園の南面に掃き出し窓（床まで届く引き違いのガラス窓）、住居の南面は腰高窓、住居・幼稚園の南面に玄関の扉各1（決定による新規の玄関。接続は未契約）。室内MAPはこの見え方と一致させる。

## 前置き指示（wrapper）
```text
Invoke the $imagegen skill and use the built-in image_gen tool at the HIGHEST quality (quality: high), requesting 1920x1080 (16:9), to create the image described in the prompt below. No reference image is attached; use text only. Call image_gen EXACTLY ONCE: no retries, no regeneration, no multiple candidates, even if you think the result is imperfect. Then save the REAL generated PNG (decode the tool result) into the current workspace at out/trm03-v5.png. You are STRICTLY FORBIDDEN from fabricating/drawing the image with magick/ImageMagick/PIL/Pillow/numpy/SVG/canvas/any code; only the image_gen tool. If the image_gen tool is genuinely not in your toolset, do NOT fabricate - output exactly: IMAGE_GEN_TOOL_UNAVAILABLE. Do not resize or crop the result. Do not use any files in ~/.codex/generated_images/ made by other calls; only the image generated in this call. Report the saved file path.
Output a 16:9 landscape image. Target 1920x1080; if not possible, 1672x941. Do NOT use 3:2 or 1536x1024.
```

## 送信した完全prompt（原文のまま）
```text
Generate ONE image: the final field background for map TRM-03 (temple-grounds, OUTDOOR). Do not generate any other map.

=== SOURCE TEXT (verbatim, do not paraphrase) ===
[Specification row, map-specifications.md]
| TRM-03 temple-grounds | 全時期 | 親鸞像のある浄土真宗の境内（屋外） | bottom→TRM-07、door-main→TRM-04、door-kindergarten→TRM-01.door-west | #60/#51。本堂中心・境内から見て左（西）住居・右（東）幼稚園の同じ建物群。TRM-01は境内の右隣。住居／遊戯室への屋外doorなし […] |
[Asset registry row]
| TRM-03 | `assets/images/fields/legacy/TRM-03.webp` | 寺町 | retired-replacement-required |
[Contract checklist row]
| TRM-03 | recreate-required-1920x1080 | R006,R011,R024 | 旧境内画像は参照専用。新背景・mask未作成 | #60の屋外境内。TRM-07端、TRM-01.door-west通用門（境内の右＝東側）、TRM-04正面扉、墓地のblocked域・像・鐘楼を、採用した外観画像で確定して記録[…]。TRM-05/TRM-02屋外doorなし。共通外観参照は通過済み（順序・包含関係の確認用）だがTRM-03最終背景は未生成 |
[Rebuild candidate row]
| TRM-03 | `TRM-03-temple-grounds-rebuild-v4-candidate.png` | bottom→TRM-07、door-main→TRM-04、door-kindergarten→TRM-01.door-west | 屋外境内。住居・遊戯室への屋外doorなし […] | recreate-required-1920x1080 |
[Connections touching TRM-03, map-topology.md]
| TRM-01.door-west | TRM-03.door-kindergarten | door | 境内（TRM-03）の右（東）隣の園庭へ入る通用門。扉の位置・形はTBD |
| TRM-07.top | TRM-03.bottom | edge | 山門から境内へ |
| TRM-03.door-main | TRM-04.door-south | door | 本堂内部 |
[Outdoor/indoor transition invariants, map-topology.md]
| `TRM-01.door-west` | `TRM-03.door-kindergarten` | 園庭の西側（境内側）通用門。境内の右（東）脇の同じ門へ入る。園庭主路（TRM-01.bottom→TRM-08.top）とは分離する。 |
| `TRM-03.door-main` | `TRM-04.door-south` | 境内から本堂へ。段差を主路にせず、扉前に回転余地を残す。 |
[Site layout, map-topology.md section 6]
- **境内（`temple-grounds` / TRM-03）**: 山門（南）から本堂（北）へ石畳。境内から見て左（西）に住居側、右（東）に幼稚園側の建物が続く。屋外から住居・幼稚園へのdoorは作らない（屋内でTRM-04経由）。
- **幼稚園（TRM-01園庭／TRM-02遊戯室）**: 園庭TRM-01は境内TRM-03の右（東）隣で寺の入口のそば。TRM-03↔TRM-01は境内東脇の通用門（door）。TRM-02は本堂TRM-04の東（右）の屋内。TRM-01↔TRM-02の直結は未契約。
| TRM-07.top | TRM-03.bottom | 辺（縦の石畳） | 山門から境内へ |
| TRM-03.door-main | TRM-04.door-south | ドア（本堂の正面） | 境内から本堂 |
| TRM-03.door-kindergarten | TRM-01.door-west | ドア（通用門） | 境内の東脇から右隣の園庭へ。扉位置TBD |
[Decision, decisions.md]
| **寺町の寺（幼馴染の実家）は浄土真宗大谷派（kako-jun 2026-10-15）。卒塔婆は置かない** | 寺の絵・文章に卒塔婆（宗派上ない）を描かない。仏壇は金仏壇、本尊は阿弥陀如来。浄土真宗は地蔵信仰・現世利益の習俗が基本ない（確認済み: 六地蔵は宗派に合わない。宗派に合う版を別ファイルで作った。`temple-grounds-shinshu-diorama.png`＝親鸞聖人の石像、`teramachi-hinomi-bend-shinshu-diorama.png`・`teramachi-connector-shinshu-diorama.png`＝地蔵を石碑に。元の絵は残す。ほか teramachi-* の絵に地蔵・卒塔婆はない。幼稚園の絵の狛犬は寺院にも置かれるので変えていない）。境内の絵・庫裏の絵・台詞に反映。既存の絵に卒塔婆は見当たらない（目視） |

[Common conditions, map-asset-registry.md]
全画像の共通条件は、現代の K県、冬、手作りジオラマ、真上寄り、人物・文字なし。昭和から残る建物や設備は存在してよいが、時代設定を昭和に戻さない。汚れは雪国の日常（融雪水、砂、泥、塩の白残り、黒ずんだ木、錆）であり、廃墟でない場所を廃墟化しない。
[Neighbouring maps, map-specifications.md]
| TRM-01 kindergarten | 幼稚園前半〜終幕 | 本堂の裏で雪遊びをする私立幼稚園の園庭（屋外） | 段丘上。bottom→TRM-08.top（正門）、door-west→TRM-03.door-kindergarten（境内の右隣の通用門） | TRM-02は同じ幼稚園の屋内。TRM-01↔TRM-02の直結doorは未契約のため描かない |
| TRM-07 wide-road | 全時期 | 消雪パイプと寺の長塀の広い道 | TRM-15西↔TRM-08東、北の山門→TRM-03 | 山門は中央より北寄り |
| TRM-04 | 全時期 | 仏具の鈍い金と畳が対照になる本堂（屋内） | door-south→TRM-03、door-west→TRM-05.door-hall、door-east→TRM-02.door-west。参拝域は端へ出ない | #60。中央の屋内分岐。住居・幼稚園へ外に出ず移動 |
[Statue, art-direction.md (excerpt)]
宗派に合う版は `temple-grounds-shinshu-diorama.png`（六地蔵を、笠と杖の親鸞聖人の小さな石像に差し替え）。
[Kindergarten playground, source rows (verbatim)]
| TRM-01 | `assets/images/fields/legacy/TRM-01.webp` | 寺町 | retired-replacement-required |
| TRM-01 kindergarten | 幼稚園前半〜終幕 | 本堂の裏で雪遊びをする私立幼稚園の園庭（屋外） | 段丘上。bottom→TRM-08.top（正門）、door-west→TRM-03.door-kindergarten（境内の右隣の通用門） | TRM-02は同じ幼稚園の屋内。TRM-01↔TRM-02の直結doorは未契約のため描かない |
| TRM-01 | recreate-required-1920x1080 | R006,R011 | `assets/images/fields/legacy/TRM-01.webp`; mask未記録 | 園庭の既存画像におけるTRM-08(bottom)/TRM-03(door-west)の実端、幼稚園期のtraversalを採寸する。TRM-16との接続は#51で廃止 |
| TRM-01 | `TRM-01-teramachi-kindergarten-rebuild-candidate.png` | bottom→TRM-08.top、door-west→TRM-03 | 屋外園庭（境内の右＝東隣）。通用門は園庭主路と分離 | recreate-required-1920x1080 |
- **園庭 E01 は寺の入口のそばにあるはずで、E11（境内）の右側にあるべき。** 現行は E01 が主路の西端で E11 と通用門(door)だけでつながり、遠く見える。
- 事実としての所見: 屋根・外壁は保たれ、断面・室内なし。左=住居、中央奥=本堂（参道が南の山門へ）、右=幼稚園舎＋園庭（滑り台・ブランコ）の順。人物・文字・空・地平線なし。土台の段ボール断面・マスキングテープ・綿の雪・紙粘土が判別できる。
[Decision, kako-jun 2026-10-21 (verbatim)]
園庭は寺の正面の空間（境内）の右側半分に作るべき
[Decisions, kako-jun 2026-10-21 after viewing v3 (verbatim)]
渡り廊下がながすぎる
本堂を通らなくても左右の建物にも入口は必要だろ
右側の幼稚園のほうが大きな建物であるべき
住居と違って掃き出し窓があるべき
右端の門もなんのためにあるのかわからん
[Decision, Issue #51, kako-jun 2026-10-21 (verbatim)]
- **TRM-03 の内容**: […]像と墓地は必要。鐘楼もあってよい（演出に使える）。
- **生成順と参照**: まず外観 TRM-03 を作る。室内3つ（TRM-04/05/02）は、採用した外観画像を参照画像に渡し「この建物のこの部屋の室内を描け」の形で作る。扉・像・墓地などの位置は、採用した外観画像で確定し、以後の参照とする。

=== ARCHITECTURE INVARIANT TABLE (verbatim, shared by all four maps) ===
| ヒロインの住居、幼稚園、本堂は外へ出ずに屋内廊下でつながる。本堂を中央に置き、幼稚園と住居を直接接続しない。 | 屋根・外壁を保ち、本堂中央・境内から見て左（西）が住居・右（東）が幼稚園（#51 2026-10-19で左右反転。上の#60原文のdoor-east/westは旧配置の記述）。別棟や外部渡り廊下で代替しない |
| 本堂（中央）・住居（西）・幼稚園（東）は、屋根と壁のある廊下棟で外観上もつながり一つの連続した建物群に見える（根拠 docs/map-topology.md の TRM-04.door-west↔TRM-05.door-hall 渡り廊下、TRM-04.door-east↔TRM-02.door-west 屋内廊下）。 | 住居と幼稚園は直接つながない（本堂経由のみ）。吹きさらしの外部渡り廊下は不可、屋根と壁のある廊下棟は必須。屋外通路・離れた独立棟も不可。審査基準: 本堂の左右の壁面に屋根付き廊下棟が接し、棟の屋根が本堂・住居・幼稚園の屋根へ切れ目なく続く。廊下棟の両端が壁に接し、地面の隙間・雪原が屋根と屋根の間に通らない。住居と幼稚園の間に直接の廊下がない。廊下の長さ・幅・扉位置はTBDで、描き込んで確定させない |
| TRM-03 境内（外部） | 屋外境内。屋根を外した室内・家具を見せない |
| TRM-01の正本行「私立幼稚園の園庭（屋外）」／TRM-02の正本行「遊戯室（屋内）」 | 園庭と遊戯室は同じ幼稚園の外部／内部。TRM-01を室内にしない。未契約の園庭直結doorを足さない |
| TRM-04.door-west ↔ TRM-05.door-hall | 西の住居まで屋内で連続。具体的廊下形状は未確定 |
| TRM-04.door-east ↔ TRM-02.door-west | 東の幼稚園まで屋内で連続（TRM-02は本堂側の西面から入る）。扉位置・廊下長は推測しない |
| TRM-03から住居・幼稚園へ屋外を経由する新規doorは作らない。 | 境内の正面入口はTRM-04へ。住居・遊戯室の外部入口を発明しない |

#60によりTRM-03は屋外、TRM-04/TRM-05/TRM-02は屋内。本堂を中央、境内から北（本堂）を見て左＝西が住居、右＝東が幼稚園とする（#51 2026-10-19の決定。旧「住居＝東・幼稚園＝西」は廃止）。園庭TRM-01は境内TRM-03の右（東）隣で、TRM-03.door-kindergarten↔TRM-01.door-westの通用門でつなぐ。`TRM-05.door-playroom ↔ TRM-02.door-west` と `TRM-03.door-residence ↔ TRM-05.door-temple` は現行グラフから除外する。TRM-03から住居・遊戯室への屋外doorを新設しない。TRM-01↔TRM-03は園庭と境内の屋外通用門で、TRM-02への直結を意味しない。建物の外形・廊下の長さ・画面内配置・通行幅はこの接続図から推測せず、[制作前確認](production/20261018-teramachi-preflight.md)のTBDを解く。

=== WHAT TO DRAW (positive description, each clause maps to source text above) ===
C1. North is the top. This is the OUTDOOR temple grounds (境内, 屋外) of a 浄土真宗 temple (親鸞像のある浄土真宗の境内). Used in every story period (全時期); the scene is winter with snow, contemporary K Prefecture. Follow the Common conditions text above: buildings and equipment surviving from the Showa era may exist but the setting is not returned to the Showa era; dirt is everyday snow-country dirt (sand, mud, white salt residue, blackened wood, rust) and the place is not turned into a ruin.
C2. Along the north (top) of the diorama stands ONE continuous building group seen from outside with roofs and exterior walls kept intact: from left (west) to right (east) the residence (住居/庫裏), the main hall (本堂) in the center, and the kindergarten building (幼稚園). The main hall and the residence are joined by one roofed, walled corridor wing; the main hall and the kindergarten are joined by one roofed, walled corridor wing. Each wing touches the wall of the main hall and the wall of the neighbouring building at both ends; the roof of each wing continues without a break into the roofs of the neighbouring buildings, so no ground or snow passes between roofs. The residence and the kindergarten have NO corridor directly between them: only the main hall stands between them. The complete roofs of the residence, both corridor wings, the main hall and the kindergarten building, including their north eaves, lie fully inside the base board; the five roof masses are separately countable (each wing is its own roof mass between two building roofs). A strip of snow-covered base board lies north of every roof, including the main hall's roof. The kindergarten building (right) is wider and deeper than the residence (left), and its roof mass is larger than the residence's roof mass. Each corridor wing is shorter, along the east-west direction, than the width of the residence's roof and shorter than the width of the kindergarten building's roof; the residence, the first corridor wing, the main hall, the second corridor wing and the kindergarten building still touch one another in an unbroken row. Each corridor wing keeps its own visible roof (its own ridge line and eave line between the two neighbouring roofs), so it still counts as a separate roof mass. Within this limit, the exact wing length, the wing width and the door positions are fixed by the adopted image.
C3. For this image, the 2026-10-21 decision 本堂を通らなくても左右の建物にも入口は必要だろ takes precedence over the rows saying 住居／遊戯室への屋外doorなし and over the rule against a new door from TRM-03 to the residence or the kindergarten. All buildings and wings are closed: full corrugated-cardboard roofs under cotton snow and continuous exterior walls. No interior, furniture, cutaway or removed roof is visible anywhere. No outdoor corridor, no separate detached building. The south face of the residence shows ordinary waist-height windows (no floor-length windows) and one entrance door. The south face of the kindergarten building shows a row of four floor-length sliding glass windows (掃き出し窓: tall glass windows that reach the floor and open toward the playground; these are windows, not doors) and, separate from the windows, one entrance door. Each entrance door is a hand-made wooden sliding door or hinged door of cardboard and wooden toothpicks, set directly in the south wall; the snow in front of it lies level with its sill, with no step. Where each entrance door stands along its wall is not fixed here; it is fixed by the adopted image. Besides door-main of the main hall and these two entrance doors, there is no other door on the south side of the building group. Apart from its corridor wing to the main hall, nothing is attached to the residence or the kindergarten: the door is set in the wall itself, with no annex, porch or gate.
C4. The south face of the main hall, with its entrance door-main (to TRM-04.door-south), is visible and faces the grounds. The main hall entrance floor is at ground level: the veranda, if any, is flat at ground level, with no raised veranda and no steps or stairs in front of door-main. The stone paving reaches the main-hall entrance at the same level as the entrance floor, and a level paved area lies directly in front of the door (turning room before the door). The door's exact position on the facade is not specified here; it is fixed by the adopted image.
C5. The stone paving (縦の石畳) reaches the bottom image edge, continuing toward the 山門 of the neighbouring map TRM-07 (TRM-07.top -> TRM-03.bottom, edge; 山門から境内へ), and runs north into the grounds to door-main. The 山門 belongs to TRM-07: no gate structure and no wall is drawn at the bottom edge on the TRM-03 side; the paving simply ends at the bottom edge of the base board. The paving's x-position, width and bends are not specified here; they are fixed by the adopted image. Add no other path, crossing, curve or right angle.
C6. Only the bottom edge carries paving; the left, right and top edges end at the base board edge.
C8. A small stone statue of Shinran (a figure wearing a sedge hat and carrying a staff), carved from paper clay, an upright, slender adult monk figure with a solemn face (not a round, child-like figure), stands in the grounds (required: 親鸞像; the source text says 小さな石像). The Shinran statue stands beside the central paving, turned to face the paving. Its face and chest point sideways toward the paving, so from above the figure is seen in side view; its front does not point toward the bottom edge. Which side of the paving, and its exact position and size, are not specified here; they are fixed by the adopted image. This Shinran figure is the only statue in the grounds.
C9. A graveyard (墓地) of gravestones carved from paper clay (stone faces completely smooth and blank, without characters or symbols; flat, unmarked faces) exists in the grounds as an impassable (blocked) area (required). The graveyard stands in the left (west) half of the grounds, on the residence side. Its exact position within that half, its shape and its size are not specified here; they are fixed by the adopted image.
C10. The grounds contain a bell tower (鐘楼): corrugated-cardboard roof, wooden-toothpick pillars, the bell hangs from the roof beam, a small bell shaped by hand from paper clay painted dark grey (required; used for staging). Its position and size are not specified here; they are fixed by the adopted image. The grounds hold the paving, the Shinran statue, the graveyard, the bell tower, the playground (C12) and the trees (C13) on open snow.
C11. The paving runs unbroken from the bottom edge to door-main. All open ground in the grounds is cotton-batting snow over foamboard, apart from the paving, the listed objects, the trees (C13) and the patches of exposed brown soil (C13).
C12. For this image, the 2026-10-21 decision 園庭は寺の正面の空間（境内）の右側半分 takes precedence over the rows that place TRM-01 behind the main hall (本堂の裏) or outside this map. The kindergarten's playground (園庭) lies in the right (east) half of the grounds, in the space in front of the temple. It is the outdoor playground (屋外) of the private kindergarten run by the temple, where children play in the snow (雪遊びをする私立幼稚園の園庭), beside the kindergarten building. It holds playground equipment and snow-play objects, several in all, spread over the right half and not gathered in one spot: a slide (a small tower of unpainted wooden toothpicks, glue blobs at joints, with a cardboard platform, a red-painted cardboard ladder on one side and a blue-painted cardboard slide on the other); a swing set (red-painted toothpick frame, two small seats of corrugated cardboard with visible corrugated cut edges, hanging on yarn); a row of several half-ring arch pieces of paper clay, painted red, blue and yellow with matte poster paint, standing half-buried in the snow; one spotted animal-shaped playground ride of paper clay painted white with brown spots; several snowmen made of cotton-batting balls stacked in two, with small black cut-paper eyes; one sled of folded corrugated cardboard with visible corrugated cut edges; snow mounds of heaped cotton batting; and footprints pressed into the snow. The rest of the playground is open cotton-batting snow. The exact place of each object inside the right half is fixed by the adopted image.
C13. Trees are planted in the grounds. There are two kinds: bare leafless winter trees (thin wire and yarn) and snow-covered evergreen trees (green sponge and yarn, snow lying on the branches). Several trees of each kind stand at various places in the grounds: beside the buildings, around the graveyard, around the playground and along the paving; no single place holds them all. The surface varies, using the everyday snow-country dirt of the Common conditions text (sand, mud, white salt residue, blackened wood, rust): the cotton-batting snow is lumpy with rises and dips, with patches of exposed brown soil, footprints in the snow, and dirty marks on the paving stones. The roofs, corridor wings and south faces of the building group stay fully visible; trees stand clear of them (none overlaps a roof or wall); no tree stands in front of the south faces; trees near buildings stand at their ends or behind them, with open snow between tree and wall.
=== CAMERA, MATERIALS, SIZE, REFERENCE ===
FRAME: hand-made tabletop diorama, camera looks down steeper than 45 degrees from horizontal, as close to straight-down as possible (exact number is TBD; oblique is tolerated, never shallower than 45 degrees from horizontal). North = top of the image. No sky, no horizon, no vanishing point. No people, no readable text, no logos. Objects that stand in front are NOT separated into layers (a later mask handles them).

MATERIALS AND TOOLS (SKILL fixed vocabulary; list every material in the image, all must be identifiable at full size):
- Base: 5 mm foamboard, with exposed corrugated cardboard cross-section visible along the front edge of the diorama; masking tape strips and white PVA glue squeeze-out visible. The base sits on a plain wooden tabletop (not asphalt, not a road surface); the table and the room remain visible around the base (do not crop the base).
- Walls and stone: paper clay carved with a wooden toothpick (finger marks, spatula marks). Roofs: plain sheets of corrugated cardboard painted matte grey, corrugation ripples visible, cut by craft knife with hand-cut ragged edges; every roof is a plain sheet (no individual roof tiles, no ridge ornaments). Pillars: wooden toothpick. Painting: matte poster paint with a flat brush (brush streaks, uneven coats).
- Paving: matte black construction paper (black, not grey) cut into paving-stone pieces, cut edges visible. Snow: cotton batting (fibers visible) fixed with white PVA glue. Statue and gravestones: paper clay carved with a wooden toothpick. Bell tower: corrugated cardboard roof, wooden toothpick pillars, a small bell of hand-shaped paper clay painted dark grey.
- Trees: bare trees from thin wire and yarn; evergreen trees from green sponge and yarn; snow on the branches from cotton batting. Exposed soil patches: brown matte poster paint and sand-like grit under thin cotton.
- Small items: buttons and cut paper.
- Paper pieces and paper-clay stones look like paper and clay (matte, soft edges), not real slate or real stone; masking tape strips and glue squeeze-out are clearly visible at the base edges.
- Hand-made roughness required: glue squeeze-out, thread lint, ragged hand-cut paper edges, paint unevenness, visible material seams, coarse grain.
- Must NOT appear: real asphalt, real snow, real roof tiles, real wood as a model material, uniform CGI surfaces, "miniature-look" with unidentifiable material, photographic precision. It must read as a crude hand-made model, not a photograph.

DIMENSIONS: request 1920x1080 (16:9). If the tool cannot return it, 1672x941 or 1672x940 (16:9) is acceptable (kako-jun 2026-10-21; the tool previously returned 1672x940). Any other size is a failure; never resize/crop to pass. Measure the real output file (file/identify); the prompt text, file name and past reviews are not evidence.

REFERENCE: none. No reference image is attached (text-only generation). The order and containment of the three buildings are given by C2 alone.
```
