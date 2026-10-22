# M114 18禁週刊誌改訂候補 — 2026-10-22

- Target: M114 18禁の成人向け週刊誌（目隠しされた表紙）
- Stage: contract/prompt
- Status: candidate generated; exact final prompt is recorded in 20261022-M114-weekly-magazine-generation.md
- Grid class: 1x2
- Read-only reference: current adopted M114 image `assets/images/enemies/M114.webp`; keep it intact until user adopts a replacement
- User direction: the book should read as an 18+ erotic magazine through its colors and Japanese weekly-magazine look; a plain cloth-wrapped book lacks character.

## Canonical source excerpts (verbatim)

From `docs/monsters.md` M114:

```
| M114 | 18禁の成人向け週刊誌（目隠しされた表紙） | 恐怖メディア | 未定（棚の高い位置） | 未定 | 未定 | 未定 | 現行採用: `assets/images/enemies/M114.webp`（元画像 `exec-e323a5bf-5d5e-4983-9c9d-cbbc1609a330.png`、1024×1536、1x2。kako-jun 2026-10-21 全部採用）。kako-jun 2026-10-22 指示で新版候補を作成中：18禁の成人向け週刊誌と分かる色・表紙構成。採否前は現行画像を保持。[旧候補レビュー](reviews/artifact-redteam/20261021-M114-raw-image-e323a5bf.md) | #12
```

From `docs/monsters.md` grid decision:

```
| M114〜M116 | 1x2 | 棚に立てる本・DVDケース |
```

From `docs/art-direction.md`:

```
| 大人・子供向けの恐怖メディア | 18禁の成人向け週刊誌、架空のホラーDVD、怪奇本、怪人・ひとさらい風の絵本、笑い袋 |
```

From `docs/dungeon-enemies.md`:

```
| M114 | 18禁の成人向け週刊誌 | 置き場の記録が無い（理由なし） |
```

M114 remains unassigned. Do not add a shelf, scene, or encounter location.

## Prompt to generate

Create one separate, unadopted M114 candidate. Use the current adopted M114 in Image 1 only as a read-only upright-book and spine reference; do not edit or overwrite it.

Render one closed, upright weekly magazine book as a realistic isolated object on a transparent 1024×1536 px portrait canvas, logical gridClass 1x2. Keep the complete silhouette visible. Show the front cover at a three-quarter view with the spine visible along the image-left edge. The book should fill most of the canvas without cropping.

Make it immediately read as a Japanese 18+ erotic weekly magazine. Use a vivid fuchsia #E6007E, vermilion #D62828, bright yellow #F2C94C, cream #F4E8D0, and near-black #17131D cover palette. Use familiar Japanese weekly-magazine cover styling: energetic bursts, halftone dots, stacked colored story panels, thick borders, and a nonverbal red-and-white age-warning badge near the upper left. Keep all cover lettering as unreadable decorative marks; no legible title, words, numbers, or existing magazine logos.

The central cover art is a printed, stylized pin-up of a clearly adult fictional woman, posed suggestively in opaque black lace lingerie with a red satin robe over her shoulders. It is printed artwork on the book, not a separate person in the scene. A single dark-red cloth strip crosses the model’s eyes like a blindfold, echoing the original M114 concept. Keep this clearly adult and erotic in magazine tone, while showing no nudity, visible nipples or genitals, sexual acts, or transparent fabric. Do not show or imply the magazine contents. The closed book remains the only enemy object and reads clearly as a book.

Use photorealistic generated-object studio rendering for the physical book and printed cover. No scene, shelf, floor, base, contact shadow, border, frame, acrylic stand, or extra props. The book has no head, torso, or eyes of its own; anatomical yaw and gaze checks for the book are N/A. Do not invent encounter placement, ability, element, or other story details.

Tool setting: `transparent_background: true`.

## Review history

The first proposed revision prompt used a readable 18禁 badge and was blocked because letters reverse in mirrored battle use. The second prompt removed readable text and passed on content direction, but was blocked on subjective descriptors and pixel-level specificity. Per the user's prior instruction that acrylic-stand presentation makes excessive precision unnecessary, this prompt fixes the main palette and cover placement while keeping the rest practical. No readable text is included.
