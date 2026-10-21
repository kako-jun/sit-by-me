# M009 prompt contract review

## Source and visual contract

- Source: `docs/monsters.md` M009, `docs/dungeon-enemies.md` M009, and `docs/art-direction.md`.
- Grid class: **1x1**. Keep the visual mark extremely small, centered, transparent, and isolated.
- Subject: a tiny purple error cell, about one visible dot in scale. The bright center is part of the cell.
- Do not add rays, cross streaks, sparkles, aura, particles, background, text, or a surrounding container.
- Maintain the project’s photoreal material treatment while keeping the cell legible at its deliberately tiny scale.

## Prompt decision

The first candidate (`exec-9a272077-3178-4b29-8b8f-54f78614633b.png`) was blocked: the visible mark was too large and read as a magical starburst. A targeted edit prompt specified a maximum alpha-visible box of 40×40 px on a 1254×1254 transparent canvas, centered, with no rays or surrounding effects.

## Review result

The corrected prompt was followed by candidate `exec-eeab27c6-666d-4be4-852a-bb5bbd05b70e.png`. Prompt contract: **pass**. Raw image measurements and visual findings are in [the raw-image review](20261021-M009-raw-image-eeab27c6.md). Adoption remains pending.
