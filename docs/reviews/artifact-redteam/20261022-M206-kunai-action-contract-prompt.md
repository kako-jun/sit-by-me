# M206 kunai action revision — 2026-10-22

- Target: M206 城の雑魚: 忍者
- Stage: contract/prompt
- Status: awaiting independent prompt review before generating a new candidate
- Grid class: `1x2` (`docs/monsters.md` §3-7)
- Read-only reference: previous unadopted M206 candidate `exec-5b7f8edf-9bc0-4fbb-bc7a-1bf8c4ea2d19.png` at `/home/kako-jun/.codex/generated_images/01a15ccc-868c-7f60-8889-229de4286e8f/`
- Output role: one separate, unadopted candidate. Do not alter the adopted `assets/images/enemies/M206.webp` or the prior candidate.
- User change request: make the movement more intense and give both M206 and M209 a ninja weapon. M206 receives a kunai; M209 receives a shuriken.

## Canonical source rows (verbatim)

From `docs/monsters.md` M206:

```
| M206 | 城の雑魚: 忍者 | 物語の敵 | 金沢城（ラストダンジョン。専用雑魚。kako-jun 2026-10-21、#140） | 未定 | 未定 | 雑魚（M014とは別物） | 現行採用画像: `assets/images/enemies/M206.webp`（元画像 `exec-cf3ba92a-2acf-407f-90e0-8be7a1ab3243.png`、1024×1536・1x2。kako-jun 2026-10-21 全部採用）。前傾して走り込み、くないで攻撃する候補を作成中。[初回候補](reviews/artifact-redteam/20261022-M206-M209-raw-image-review.md) | #140 |
```

From `docs/monsters.md` §3-7:

```
| M206 | 1x2 | 前傾を深くして走り込み、くないを突き出して攻撃する忍者人形（#140。縦長） |
```

From `docs/dungeon-enemies.md` M206:

```
| M206 | 城の雑魚: 忍者（1x2） | 和風の城敵として追加（kako-jun 2026-10-21、#140）。前傾して走り込み、くないで攻撃 | 未定 | 雑魚 | 未定 | くないを持つ新版候補を作成中。現行画像は採用済みのまま保持 | 未定 | 未定 | 対象外（壮年。青年前半より後） |
```

`docs/content-registry.md` に M206 の対象行なし。

- `docs/art-direction.md` §95: humans are not enemies; mannequins and dolls remain display objects/toys.
- `docs/assets-policy.md`: enemy battle masters are photorealistic generated images on transparent backgrounds, without acrylic treatment, base, or contact shadow.
- User preference: acrylic-stand rendering makes strict pixel margins unnecessary; keep the full figure and weapon visible without cropping.

## Complete prompt

Use case: product-mockup
Asset type: Sit by Me ordinary RPG battle enemy master sprite, M206, logical gridClass `1x2`.
Primary request: Create a new separate candidate by revising the previous M206 ninja-puppet candidate into a much more forceful running attack. Treat Image 1 as read-only; do not modify or overwrite it or the adopted canonical asset. Keep the same carved black wooden articulated mannequin identity and design.
Input image: Image 1 is a read-only identity and material reference: the previous unadopted M206 candidate `exec-5b7f8edf-9bc0-4fbb-bc7a-1bf8c4ea2d19.png`.
Scene/backdrop: clean isolated transparent cutout, no scene, halo, fog, or backdrop gradient.
Subject: one full-body black carved wooden ninja mannequin, logical gridClass `1x2`, on a 1024×1536 px portrait canvas. Show a forceful sprint attack toward +x: torso pitched 40° forward from vertical, front knee driving toward +x and leading foot reaching ahead to plant, rear leg sharply extended back with its foot raised, hips low, shoulders counter-twisted while preserving the required camera yaw. The forward arm is fully thrust toward +x and holds one short dark-steel kunai with a triangular blade and ring pommel, blade pointing toward +x; the other arm drives backward for balance. The kunai is 18% of the puppet’s total height. Preserve attached articulated limbs, blank carved mask, tied head piece, dark wood plates, and visible ball joints. It remains an inanimate wooden puppet, never a living person.
Style/medium: photorealistic generated-object studio image; matching carved dark wood and joint details from Image 1.
Composition/framing: head and torso yaw are each exactly 45° from camera-front 0° toward +x, with front and right planes visible. Keep all of the figure and the entire kunai at least 12 px inside the canvas; do not crop any body part or weapon.
Lighting/mood: directional object lighting that reveals the wooden carving and steel kunai; do not add a background glow.
Materials/textures: dark carved wood, visible wood joints, one matte dark-steel kunai.
Constraints: revise the pose and add one kunai only. Preserve the puppet's identity and materials. Use actual transparent background with tool setting `transparent_background: true`; areas outside the puppet and weapon must be fully transparent, with no scattered marks.
Avoid: upright/standing pose; airborne jump or flying-kick pose; non-attacking run; clothing; extra weapons; shuriken; living human, skin, realistic anatomy, or real person; extra objects; motion trails; floor; scenery; colored halo; background; contact shadow; outline; one-sided symbol; border; text; logo; watermark; base; pedestal; acrylic stand.

## Tool setting

`transparent_background: true`
