# M209 shuriken airborne revision — 2026-10-22

- Target: M209 城の雑魚: くのいち
- Stage: contract/prompt
- Status: awaiting independent prompt review before generating a new candidate
- Grid class: `1x2` (`docs/monsters.md` §3-7)
- Read-only reference: previous unadopted M209 candidate `exec-076d1aea-a11f-42a8-92e6-42cd02902231.png` at `［ローカルパス省略］/`
- Output role: one separate, unadopted candidate. Do not alter the prior candidate or create/overwrite the canonical `assets/images/enemies/M209.webp` before user approval.
- User change request: keep the light-blue airborne kunoichi distinct from M206 and give both enemies ninja-like weapons. M209 receives a shuriken.

## Canonical source rows (verbatim)

From `docs/monsters.md` M209:

```
| M209 | 城の雑魚: くのいち | 物語の敵 | 金沢城（ラストダンジョン。専用雑魚。kako-jun 2026-10-21、#140） | 未定 | 未定 | 雑魚（M014とは別物）。忍者 M206 と異なり、水色の忍装束を着た木製人形が空中から蹴りかかり、手裏剣を構える | 初回候補 `exec-076d1aea-a11f-42a8-92e6-42cd02902231.png` を生成済み（gridClass 1x2）。武器を持たせた新版を作成中。[初回画像レビュー](reviews/artifact-redteam/20261022-M206-M209-raw-image-review.md) | #140 |
```

From `docs/monsters.md` §3-7:

```
| M209 | 1x2 | 水色の忍装束の人形が空中蹴りを放ち、手裏剣を構えるくのいち（#140。縦長の跳躍姿勢） |
```

From `docs/dungeon-enemies.md` M209:

```
| M209 | 城の雑魚: くのいち（1x2） | 和風の城敵として追加（kako-jun 2026-10-21、#140）。M206 と区別し、水色の忍装束を着た木製人形が空中蹴りを放ちながら手裏剣を構える | 未定 | 雑魚 | 未定 | 手裏剣を持つ新版候補を作成中。初回候補は引き続き保管 | 未定 | 未定 | 対象外（壮年。青年前半より後） |
```

`docs/content-registry.md` に M209 の対象行なし。

- `docs/art-direction.md` §95: humans are not enemies; mannequins and dolls remain display objects/toys.
- `docs/assets-policy.md`: enemy battle masters are photorealistic generated images on transparent backgrounds, without acrylic treatment, base, or contact shadow.
- User preference: acrylic-stand rendering makes strict pixel margins unnecessary; keep the full figure and weapon visible without cropping.

## Complete prompt

Use case: product-mockup
Asset type: Sit by Me ordinary RPG battle enemy master sprite, M209, logical gridClass `1x2`.
Primary request: Create a new separate candidate by revising the previous M209 kunoichi puppet candidate to add one clearly readable ninja weapon. Treat Image 1 as read-only; do not modify or overwrite it. Preserve the light water-blue outfit and airborne flying-kick attack.
Input image: Image 1 is a read-only identity, pose, and color reference: the previous unadopted M209 candidate `exec-076d1aea-a11f-42a8-92e6-42cd02902231.png`.
Scene/backdrop: clean isolated transparent cutout, no scene, halo, fog, or backdrop gradient.
Subject: one full-body wooden kunoichi mannequin, logical gridClass `1x2`, on a 1024×1536 px portrait canvas. Preserve the dominant light water-blue outfit `#78D7E6` and dark-blue trim `#234A68`. Keep her airborne: torso angled forward 25° from vertical, leading leg extended in a flying kick toward +x, trailing leg folded beneath the body. The forward arm reaches toward +x holding one steel four-point shuriken, diameter 12% of the puppet's total height; the other arm counterbalances. Keep the blank carved wooden mask, articulated wooden joints, and exposed carved-wood hands and feet. She must read as a constructed mannequin, not a living person.
Style/medium: photorealistic generated-object studio image, with woven blue fabric over a jointed wooden display puppet.
Composition/framing: head and torso yaw are each exactly 45° from camera-front 0° toward +x, with front and right planes visible. Keep all of the figure and the entire shuriken at least 12 px inside the canvas; do not crop any body part or weapon.
Lighting/mood: object lighting that preserves the light-blue garment and reveals the wooden joints; do not add a background glow.
Materials/textures: woven water-blue cloth, carved warm-brown wood at mask and joints, one matte steel four-point shuriken.
Constraints: add one shuriken only; preserve the existing airborne-kick identity and outfit. Use actual transparent background with tool setting `transparent_background: true`; areas outside the puppet and weapon must be fully transparent, with no scattered marks.
Avoid: standing, walking, or grounded pose; dark overall outfit; extra weapons; kunai; living human, skin, realistic human face, or identifiable real person; extra characters; motion trails; floor; scenery; colored halo; background; contact shadow; outline; one-sided symbol; border; text; logo; watermark; base; pedestal; acrylic stand.

## Tool setting

`transparent_background: true`
