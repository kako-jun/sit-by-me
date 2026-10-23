---
name: sit-field-mask
description: Create, edit, validate, and review Sit by Me field traversal masks and foreground occlusion layers. Use after a field background is accepted or when its accessibility, exits, or foreground display changes; do not use to generate the background itself.
---

# Sit by Me Field Masks

**画像の保存形式（#68決定、2026-10-19）**: imagegenの出力（PNG）→切り出し→**WebP（非可逆・品質85・アルファ保持）**にして正本パスへ保存する（`magick in.png -quality 85 out.webp`、または `verification/characters/tools/key_*.py` が直接WebPで出す）。PNGは残さない（name-name のTUIは WebP のみデコードできる）。実寸（不変）・アルファ（`magick in.png -alpha extract` と変換後WebPの同コマンドを `compare -metric AE` で比べAE=0）の検査はWebPで行う。寸法ゲートの基準（1920×1080等）は変えない。 マスク・編集マップなど厳密な画素が要るものは**可逆WebP**（`-define webp:lossless=true`）で保存し、PNGは残さない。 MAPの既存PNG（fields/legacy・masks）はMAP改名PR（PR-M）でWebP化するまで現状のまま。

失敗の来歴（完全prompt・参照・実寸/検査結果・判定理由）はIssueまたはレビュー文書に記録し、失敗画像はリバートする（バイナリを別置き場に保存しない）。

Treat a field mask as a first-class MAP asset. Start only after the specific candidate passes independent raw-image review and its connection/era contract is resolved; final MAP `ready` is the result of masks and adoption review, not a prerequisite. Read the actual background, specification, topology, and era/event conditions. Under #51, old/legacy candidates and masks remain reference-only and cannot satisfy the new-image gate.

## 一意解釈ゲート（このスキルの全行より優先）

マスクの条件には、画像座標、画像端、ピクセル数、`#000000`、`#FF9D00`、`#FFFFFF`、`#00FFFF`、MAP ID、リンクID、または原文の通行条件だけを使う。`少し`、`広い`、`狭い`、`十分`、`安全`、`自然`、`近い`、`遠い`は塗り分け条件として禁止する。最小幅・座標・接続先へ変換できなければマスクを作らない。道路を補正するために直線・直交・格子状の白領域を足してはならない。

## ミニチュア材料との分離

マスクは材料の見た目を推測して作らない。背景の生成入力に記録された `paper clay`、綿雪、紙道路、セロファン水、段ボール土台などを原寸画像で確認し、それぞれを通行可能・不可にする根拠をMAP原文から一意に取る。材料名だけで通行クラスを決めること、見た目を補完することは禁止する。

## Three traversal classes

The editable traversal source is a full-size RGB PNG with **flat fills only**—no baked contour or antialiased border. It is designed for direct Photoshop painting with the Pencil tool or Fill tool.

| Edit colour | Runtime class | Meaning |
|---|---|---|
| `#000000` black | `blocked` | Nobody may enter: water, wall, building, drop, deep snow, road edge, map base, or unsafe obstacle. |
| `#FF9D00` orange | `assist` | A standing character can pass; a wheelchair user cannot until the story’s companion-assist condition unlocks it. Use for stairs, narrow/rough paths, and safely assistable rubble only. |
| `#FFFFFF` white | `universal` | Everybody, including an unassisted wheelchair user, may pass. Must have adequate width, turning space, and no step/obstacle. |

Do not use colour to mean a merely cosmetic difference. A required main route must be `universal` whenever the MAP contract says it is a wheelchair route. A dead-end reward branch never changes a required route’s class. Per-era variations are separate named source masks; never overwrite an earlier era’s mask.

## Foreground occlusion

Keep foreground display independent of traversal:

- `*-foreground-edit.png` is a full-size, solid-colour RGB edit map: black `#000000` = no cover; cyan `#00FFFF` = render the matching foreground cutout in front of the player.
- `*-foreground.png` is the transparent RGBA artwork actually drawn in front. It contains only the foreground objects, never a coloured guide or contour.
- Foreground objects that overlap the viewpoint (including those in oblique-angle backgrounds) are not separated at generation time; they are handled by this mask layer afterwards.
- A foreground tree, rail, wall edge, or roof may cover the player visually while the ground beneath remains `universal`; it must not silently turn the route into `blocked`.

## Workflow

For #51, measure the actual background before authoring: target 1920×1080; 16:9 1672×941 is accepted when the image tool cannot return 1920×1080; any other size fails and is never rescaled to pass. Every edit PNG, runtime mask, foreground and metadata size must match that exact candidate's measured size. Verify outputs with image inspection, not their filenames. Do not rescale a rejected background or reuse its mask to manufacture compliance. Keep the candidate path/version and dimensions with the links and review evidence.

1. Derive every traversable exit and forbidden edge from the MAP’s connection contract. Record edge ranges and traversal class in its JSON source.
2. Start edit maps as flat colours at exactly the background resolution. Do not draw outlines into these edit files.
3. Generate runtime masks and a separate review preview with the repository’s mask tool. The preview may tint classes and draw contours; it is disposable and is never the Photoshop source or runtime mask.
4. Inspect at 100% and against the background: all mandatory paths reach their correct image edge; prohibited edges do not; black hazards cannot be crossed; orange is limited to assistable terrain; white has wheelchair clearance; cyan occlusion does not hide an exit or create an invisible collision.
5. Save production edit maps, runtime masks and foreground images as lossless WebP `assets/images/fields/masks/TRM-03-{role}.webp` (use the actual MAP ID: area code + 2-digit sequence). Existing legacy masks remain under `assets/images/fields/legacy/masks/` as lossless WebP named by MAP ID. Save directly over the canonical path (overwrite), commit when it passes, revert with git when it does not, and commit any take you may use before generating the next one (uncommitted new files are lost on overwrite). Adoption state lives in the ledger status, not in the folder. Update the MAP ledger with exact paths and era/assist conditions.
6. Send the result to `sit-artifact-redteam` before marking it `ready`.

## Generator contract

The former generator `make_masks.py` (removed in the #68 prune; restore from git history `1bb09d0:verification/fields/legacy-masks/make_masks.py` if needed) treated the two edit PNGs as canonical; JSON
holds background, size, links, and other metadata. A link's transition trigger is a range along the model's edge side (not a fixed position at the image edge); range values and runtime handling are TBD (kako-jun 2026-10-22). It accepts legacy `walkable`
as `traversal.universal`, so an existing MAP remains valid without conversion.
Optional `traversal.universal`, `traversal.assist`, `traversal.blocked`, and
`foreground` polygon arrays are initial templates only. The generator writes:

- `*-traversal-edit.png`: the flat RGB Photoshop traversal source.
- `*-wheelchair-mask.png`: white only; `*-standing-mask.png` and
  `*-assist-mask.png`: white plus orange. `*-mask.png` remains a compatible
  alias for the wheelchair output.
- `*-foreground-edit.png`: flat black/cyan Photoshop source, and
  `*-foreground-mask.png`: its runtime alpha mask. The separately authored
  `*-foreground.png` remains the transparent foreground artwork.
- `*-mask-overlay.png`: tinted, contoured review preview only.

The first run creates the two edit PNGs from JSON. Later runs read those PNGs,
so Photoshop changes survive; pass `--refresh-edit` only when deliberately
replacing them from the JSON polygons.

## 位置合わせから採用までの共通手順（屋外・屋内とも。体内 2026-10-22〜23 で確立）

エリアの全MAPに同じ手順を適用する。体内固有の値（寸法・定義の数値・MAP別の例外）は `../sit-field-background/body-appendix.md` の『体内の2値マスク・出口候補の出力』。ツール一覧は `../sit-field-background/tools/README.md`。

1. **位置合わせ**: 承認済みモック（clean 割付図と幾何JSON。座標は模型の天面の矩形に対する比率0〜1）と採用画像の床を重ね、拡大・平行移動（必要なら回転）を最小の自由度で求める。変換パラメータ・残差・信頼度・重ね画像を register に記録する。モックは意味づけ（出口・部屋）とノイズ除去に使い、**マスクの真実は採用画像の床の見え**とする。モックと画像のズレは『画像の描画による差。マスクは画像に従う』と記録する。
2. **床色基準の切り出し**: 床の芯の色からの距離で床を決める（壁の帯・面取り・影・地形・土台縁・机・装飾は black）。床色は画像から推定し、固定値にしない。2値のエリアは white=通れる／black=通れないだけ（assist を使わない）。
3. **出口の喉の定義**: 出口の喉（床が模型の縁へ出る部分）は『床色の連続』を white にする。影で暗い床・帯の切れ目を黙って black にしない（床の欠けは red-team で major になる）。縁を越えて white が出る出口は rect の縁と前縁の両方を `edge_definitions` に記録し、どちらを採るかは TBD として残す。rect を読めない辺は期待値にフォールバックし、register に明記する。
4. **links と禁止辺**: 出口の範囲＝縁から内側4pxの帯の white の連続区間（辺上の範囲指定。遷移の範囲値・ランタイム扱いは TBD）。禁止辺（出口でない辺）は『縁から内側4px以内と縁の外側に white が無い』を機械検査する。
5. **自前の検査**（作成者が全MAPで数える）: 寸法・値が {0,255}・traversal-edit = mask・可逆WebP（VP8L チャンク）・白の連結成分1・床色から遠い点（md>15）の白0・禁止辺・出口の個数と辺・links と実測の一致・特殊構造（迷路の格子・環の部屋）の数え直し。
6. **red-team 2回**: `sit-artifact-redteam` で第1回（mask/adoption）→ 指摘（床の欠け・喉・定義の食い違い）を全件修正 → 第2回で退行確認。承認済みの逸脱（寸法の例外など）は台帳・register・採用記録・Issue に同じ文で記録してから第2回へ。

## Hard stops

- Missing background, missing reciprocal edge, missing era/assist condition, or a map without an approved connection contract: keep the mask `blocked`.
- Never use a yellow/coloured outline as editable geometry. It is review-only.
- Never make stairs, deep snow, water, rubble, or foreground-only cover white merely to connect the route.

共通（#68運用）: 合格済みの正本を上書きする前に、現行がコミット済みか確認する。不合格テイクをコミット済みにしてしまった場合は `git revert <commit>`、または `git checkout <旧commit> -- <path>` で戻す。

体内など小学校以降のMAPは2値（white=通れる／black=通れない）で作り、assist（#FF9D00）は使わない（kako-jun、#142）。
