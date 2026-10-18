# Asset organization independent review — 2026-10-18

Reviewer: Codex independent reviewer (`preflight_review`), not the implementation author. Scope: #68 ID-based organization, authorized failed-background removal, active verification references, and preservation of bytes/identity. Disposition: **pass within this scope; no actionable unresolved findings**. This is not an image-quality or runtime-adoption review.

Reviewed `git diff origin/main`, staged and unstaged changes, and the actual new/untracked manifest, assets, verification configurations, scripts and tests. Historical prose paths are intentionally retained as dated evidence and resolve through the migration manifest rather than being treated as active URLs.

## Independent evidence

- Compared all **712 manifest SHA-256 values**, including deletion tombstones, directly with original Git blobs at manifest `base_commit` using `git cat-file --batch`: zero mismatches. The manifest covers the original assets/sample tracked set once, with no duplicate source or destination. There are 565 retained files, of which 533 are under `assets/images`; the remainder are verification tools/configurations. Existing PNG/SVG bytes match their originals.
- Independently derived processed enemy/summon IDs from the **original** `docs/monsters.md`, rather than trusting author mapping: all **47** mappings agree. This includes M001's former exceptional dragon location. Raw enemy/summon files retain corresponding IDs and raw roles; M131's alpha variant has a distinct `-alpha` name.
- Independently compared all **33 canonical field** destination IDs with the original `docs/map-asset-registry.md`: all agree. Twelve older variants remain distinct, while generic prototypes use VFIELD IDs and diagrams use DIAG IDs instead of invented MAP identities.
- All **330 character** filenames carry the same C001–C004 prefix as their parent identity directory, and preserve the entire original era/outfit/pose/direction/frame suffix. The new management-ID table explicitly maps the four existing people; no new character art or identity was invented.
- The original adopted `stage-b.png` bytes map to **BG005**, and stage-b verification configuration and skill references point to that file. BG001 remains the original camera reference. Relocation does not promote other candidates to adopted status.
- S001/S008 are not fabricated. The six existing summon images are S002–S007; the canonical S008 row now records absent art. No active verification JSON points to a nonexistent S008 image.
- Deletion scope is exactly **147** manifest records: 44 rebuilding backgrounds, 82 associated rebuild mask/config files, 10 pre-sync duplicates, and 11 failed or unreviewed battle candidates. Reasons distinguish unreviewed from proven pixel failure. User-authorized failed/old-image removal is recoverable from the source commit and original hash; no duplicate binary archive is required in the worktree. Existing active legacy verification backgrounds are retained, not substituted for the planned new sixteen MAPs.
- No files remain under the former sample tree. All retained raster images use the canonical image root and ID paths. Verification JSON references retain the existing intended asset versions and resolve to actual new files; old aliases are absent. Moved mask generators use their new JSON-relative image/output paths.

## Executed checks

Ran the actual `uv run python3 scripts/verify_asset_layout.py`: **712 manifest entries / 565 kept files / 167 active references passed**. Inspected its root-confined path resolution and checks for duplicate mappings, absent old paths, exact retained image hashes and active dangling references. The final deliverable is a read-only verifier, not a persistent destructive migration executor; repeated execution does not perform moves or deletions.

Ran `uv run python3 -m unittest discover -s tests -v`: **8 tests passed**. These include an actual temporary HTTP server loading stage-b and wheelchair field JSON and referenced PNG signatures, exact suffix/identity preservation, source coverage, duplicate-source/destination rejection, missing-asset failure, repeated verifier use, and rejection of a live missing S008 reference while allowing historical prose mentioning it. Failure tests operate in temporary directories and preserve existing inputs.

Ran `ruby scripts/verify_map_ledger.rb`: **104 contracts/assets/specifications passed**, 104 topology MAPs, 102 topology rows and zero repeated edge endpoints. Rechecked the production bundle's copied SOURCE rows against current canonical files: all match verbatim.

The initial two workflow findings were corrected and independently rechecked in [generation preflight](20261018-generation-preflight.md). This review establishes repository organization, bytes/IDs and fixture loading, not a running name-name gameplay session. New imagery, masks, all-MAP traversal and the sixteen-image runtime cutover remain subsequent work.
