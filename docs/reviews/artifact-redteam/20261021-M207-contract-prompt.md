# M207 prompt contract review

## Source and visual contract

- Source: `docs/monsters.md` M207 and `docs/dungeon-enemies.md` §2.12.
- Grid class: **1x2**. Subject: a cracked porcelain statue/doll of a Japanese-inspired castle princess, with a featureless faceplate; keep it clearly inanimate and fully framed.
- Direction contract: head and torso should turn toward image-right in a front-right three-quarter view, with front and right planes visible.
- Use fictional Japanese-inspired fantasy styling; avoid a real person, historical uniform, or identifiable crest.
- Transparent background and photoreal ceramic material treatment.

## Prompt decision

The first generated candidate (`exec-597ea9cb-94b2-4a39-80ca-7cdfacd90b5c.png`) was blocked for near-profile orientation and European fantasy styling. An edit changed the styling to Japanese-inspired porcelain. A second orientation edit produced `exec-117d819c-1ef7-4df8-ba17-95191511b45d.png`.

## Review result

The prompt contract was reviewed as acceptable, but the final raw image review still flags the faceplate as facing image-left/profile rather than image-right three-quarter. Japanese-inspired styling, inanimate statue identity, transparency, and full framing pass. The final image is retained as a **candidate with an orientation caveat**, not marked as a pass; adoption remains pending. See [the raw-image review](20261021-M207-raw-image-117d819c.md).
