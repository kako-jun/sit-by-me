# M015 / M016 generated candidate provenance

Status: revised candidates adopted by kako-jun 2026-10-22 and converted to canonical WebP. Independent red-team review remains pending. This file records generation inputs and measurements; it is not a review result.

| ID | gridClass | Target canvas | Candidate | Actual canvas | Alpha bbox | Alpha range |
|---|---|---:|---|---:|---|---|
| M015 | 2x2 | 1024x1536 portrait | `~/.codex/generated_images/01a1620f-7a1f-7f21-852d-2a0822ec3022/exec-c90a1d0d-30b8-4f5c-b619-a199ee319550.png` | 1024x1536 | 983x1519+25+17 | 0–0.996078 |
| M016 | 2x2 | 1536x1024 landscape | `~/.codex/generated_images/01a1620f-7a1f-7f21-852d-2a0822ec3022/exec-aaf7653b-a39a-4fc8-9787-1d7222d7729f.png` | 1536x1024 | 1497x1024+25+0 | 0–0.996078 |

References: none. Both candidates were generated with the built-in image generation tool and transparent background enabled. `alpha-min=0` confirms transparent pixels exist. M016's alpha bounding box touches the top and bottom edges; edge contact and possible clipping require human inspection.

## Revision candidates after pose and motif feedback

On 2026-10-22, kako-jun requested non-upright dynamic poses for both enemies and a stronger bull motif for M016, specifically a horned helmet that leaves the mohawk visible. The following candidates edit the first-round images; the originals above remain unchanged.

| ID | Reference candidate | Revised candidate | Actual canvas | Alpha bbox | Alpha range |
|---|---|---|---:|---|---|
| M015 | `exec-c90a1d0d-30b8-4f5c-b619-a199ee319550.png` | `~/.codex/generated_images/01a1620f-7a1f-7f21-852d-2a0822ec3022/exec-8859476b-280f-45ad-a985-5efbaf925a19.png` | 1024x1536 | 1006x1486+0+26 | 0–0.996078 |
| M016 | `exec-aaf7653b-a39a-4fc8-9787-1d7222d7729f.png` | `~/.codex/generated_images/01a1620f-7a1f-7f21-852d-2a0822ec3022/exec-731fdb92-d2b6-444c-8ddb-49f6494a6051.png` | 1536x1024 | 1502x1024+0+0 | 0–0.996078 |

Transparent pixels are present in both revised candidates. Their alpha bounding boxes touch image edges. kako-jun approved both after visual inspection; independent review remains pending.

## Adoption

After inspection, kako-jun approved both revised candidates. They were converted without resizing to the canonical enemy paths at WebP quality 85. Alpha-channel comparison against each PNG source returned AE=0.

| ID | Canonical asset | Canvas | Alpha bbox | PNG-to-WebP alpha AE |
|---|---|---:|---|---:|
| M015 | `assets/images/enemies/M015.webp` | 1024x1536 | 1006x1486+0+26 | 0 |
| M016 | `assets/images/enemies/M016.webp` | 1536x1024 | 1502x1024+0+0 | 0 |

### Exact M015 edit prompt

```text
Edit this M015 enemy sprite while preserving its character identity, photorealistic rendering, elderly face with unsettling clown-like makeup and fixed smile, flamboyant floral aloha shirt, dark trousers, transparent background, and portrait 1024 × 1536 canvas. Keep one complete figure with head and both shoes inside the frame. Change the upright neutral stance into a clearly dynamic spellcasting pose: twist his torso, bend one knee, lean into the action, raise one hand forward with fingers spread as if casting magic, and sweep the other arm back for balance. No straight upright standing pose. Keep the head and torso yaw at 45° from camera front toward the viewer's right, showing both front and right planes; eyes look directly toward +x. Preserve the eerie clown-like quality. Transparent background. No text, logos, extra people, weapons, scenery, base, outline, or ground shadow.
```

### Exact M016 edit prompt

```text
Edit this M016 enemy sprite while preserving its character identity, photorealistic rendering, adult Tokuryu executive, corpulent heavyset body, tall visible mohawk, spiked shoulder pads, bullfighting bull motif, transparent background, and landscape 1536 × 1024 canvas. Reduce bodybuilder-like muscle definition in arms and shoulders; retain a clearly fat torso and prominent belly. Add a horned bull helmet with two large curved bull horns rising from the sides and an open crown so the mohawk remains fully visible above it. Change the upright neutral stance into a low, dynamic bull-charge battle pose: torso pitched forward, knees bent, one foot lunging forward, body twisted, one arm thrust forward and the other held back for balance. No straight upright standing pose. Keep his head and torso yaw at 45° from camera front toward the viewer's right, showing both front and right planes; eyes look directly toward +x. Keep him visibly human, not an animal or minotaur. Show the complete figure from head through both shoes within the frame with transparent margins; do not crop any horn, mohawk, shoulder spike, hand, or shoe. Transparent background. No text, logos, extra people, weapons, scenery, base, outline, or ground shadow.
```

## Exact prompts

### M015

```text
Generate one photorealistic battle sprite for enemy M015, logical gridClass 2x2. Portrait canvas, exact target 1024 × 1536 pixels. Show one complete standing elderly male human, head through both shoes, centered with visible transparent margins on all sides and no cropping. His head and torso yaw are 45° from camera front toward the viewer's right; show both the front and right planes of his face and torso. His eye gaze points directly to +x, viewer's right. He is an elderly executive of the fictional Tokuryu criminal organization, wearing a flamboyant aloha shirt with vivid tropical print and dark trousers. His appearance blends an unsettling clown-like theatrical quality into a believable elderly man: subtly unnerving painted facial accents and an uncanny fixed expression, strange rather than humorous. Hands relaxed but imposing. Transparent background. One character only. No text, logos, second figure, weapons, scenery, display base, outline, or ground shadow. Enemy master art, realistic photographic rendering, crisp readable silhouette.
```

### M016

```text
Generate one photorealistic battle sprite for enemy M016, logical gridClass 2x2. Landscape canvas, exact target 1536 × 1024 pixels. Show one complete standing adult human gang executive, head through both shoes, centered with visible transparent margins on all sides and no cropping. His head and torso yaw are 45° from camera front toward the viewer's right; show both the front and right planes of his face and torso. His eye gaze points directly to +x, viewer's right. He has a clearly corpulent, heavyset body, not a muscular body, a tall mohawk, and large shoulder pads studded with spikes. Use the bull of bullfighting as his visual motif, integrated into his clothing and armor with unmistakable bull imagery such as curved horn shapes and a bull emblem; keep him visibly human, not a literal bull or minotaur. A forceful battle-ready stance. Transparent background. One character only. No text, logos, second figure, weapons, scenery, display base, outline, or ground shadow. Enemy master art, realistic photographic rendering, crisp readable silhouette.
```
