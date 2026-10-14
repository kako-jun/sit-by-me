---
name: sit-assets
description: Create or organize Sit by Me enemy, summon, and map assets without duplicating existing work. Use for requests to generate or catalog these game assets; not for player-character pose sheets (use `sit-characters`).
---

# Sit Assets

Build assets for *Sit by Me* as an extension of its existing asset library, rather
than as isolated image-generation requests.

## First, establish what already exists

- Read `docs/assets-policy.md` and `docs/art-direction.md`.
- Inspect tracked files under `assets/` and `sample/`; check the relevant open
  issue before generating. In particular, Issue #12 is the source for enemy
  trial assets, Issue #11 for field backgrounds, Issue #6 for summons, and
  Issue #17 for the magic list.
- State whether the requested asset is new, a deliberate replacement, or
  already exists. Do not regenerate an existing approved asset merely because
  it was not found by name.

## Asset families

Classify every proposed enemy before generating it. The class decides the
visual language and helps connect it to a magic later.

| Family | Examples | Visual rule |
| --- | --- | --- |
| Machine / unattended object | road roller, drill, gun | Generate a realistic-looking object, with no operator. |
| Traffic / noise | reckless bicycle or car, loud motorcycle | Show vehicle, light, exhaust, and sound; never the driver. |
| Giant city object | large commercial sign, festival-float-like landmark | Use a fictional local landmark; make it a mid-boss through scale rather than a copied design. |
| Dark opening | open manhole, drain, underpass mouth | Make the unseeable depth or fall the source of fear. |
| Creature / internal bio | hornet, pathogen | Generate a realistic-looking creature or bio form. |
| Toxic natural object | poisonous mushroom | Keep the danger in its colour, shape, and spores; avoid rot or bodily imagery. |
| Sharp object | nails, broken glass, wire fence, icicle, sea urchin | Communicate puncture and exclusion through a readable silhouette. |
| Pareidolia / environment | night branches, wall stain | Keep the threatening shape ambiguous rather than making it an unambiguous demon. |
| Encroaching facility | fire shutter, closing gate | Treat it as a background-linked scene hazard; it need not have a facing direction. |
| Display object | mannequin, doll | Keep it clearly an inanimate object, never an actual person. Use rearrangement, reflection, or joining forms for unease. |
| Adult-world media | adults-only books, horror DVD packages | Keep adults-only material opaque: no explicit content. Use generic, text-free horror packaging rather than any real work or logo. |
| Knowledge too large to hold | thick encyclopedia, difficult study book | Make pages, questions, and the book's weight threatening; do not copy a known work's page count, name, or cover. |
| Medical / classroom uncanny | anatomy model, specimen jar, skeleton, syringe, dental drill | Keep it educational or clinical in form; do not show injury, organs, or a patient. |
| Scary child media / toy | spooky picture book, villain drawing, laughing toy | Use fictional, text-free art. Wanted-poster-like art and abduction-like road signs must not depict a real person, name, or event. |
| Smell / air | tobacco smoke and ash, alcohol fumes | Make the smell, haze, or air itself threatening; never portray a smoker or drinker as the enemy. |
| Decay / falling hazard | chandelier, broken window, torn shoji, broken bottle | Make instability, sharpness, or a former home's ruin frightening; avoid gore. |
| Natural phenomenon / summon | sea, wind, earthquake, JPCZ | A summon is an enemy-origin asset. Generate it with the same realistic visual base as an enemy. |
| Adult-world dread | monochrome old-film samurai image, inflation, distant war, nuclear fear | Make a fear learned through old films or news into an abstract image. Never make a nation, military, civilian, or real weapon the enemy. |
| Media-made foreign dread | hopping paper figure, patterned blade, bandaged figure, dark mound, woven charm, mask | Use wholly fictional objects. Frame the collage as the protagonist's inherited misconception, not as any real country, people, religion, craft, or funeral custom. |
| Handmade stage object | cardboard dragon | Generate a realistic-looking handmade theatre prop. |

Backgrounds are realistic generated imagery. A field set is made as a coherent
pack (overview, wide road, narrow lane, connector) with the same camera,
light, and repeating landmarks.

## Enemy and summon orientation

Create one canonical **right-facing** master: it faces the party when placed on
the left side of a side-view battle. The renderer may mirror that master when
needed. This also applies to a summon: it starts as an enemy asset and, when
called as an ally on the right, is displayed mirrored to face left.

Never bake a separate ally-facing copy unless mirroring would change its
meaning. Avoid readable text, logos, and left/right-significant motifs in
these masters. Keep acrylic outline, base, and shadow out of the source image;
the renderer supplies them.

For insects and internal-bio enemies, preserve fear without turning toward
revulsion. Do not propose cockroaches, rot, exposed organs, bodily fluids, or
visible parasitism. Their silhouettes must remain readable at battle scale.

## Generate and record

- Use transparent-background generation by default. Store the generation
  original under `assets/enemies/raw/` and the tight usable PNG under
  `assets/enemies/`, unless the requested asset has an established destination
  such as `sample/field/`.
- After a new enemy is accepted, add or update its row in Issue #17. Each row
  contains: enemy / scene; family; visible action or anomaly; and resulting
  **magic**. Magic is learned only from enemies: after a party member takes
  that move, it is automatically learned when the battle ends. There is no
  separate learning command and no default party spell list.
- Present generated candidates to kako-jun for adoption before treating them
  as final.
