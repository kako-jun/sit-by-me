# Branch integration audit (2026-10-25)

This is a **Git-derived historical audit, not a gameplay master**. Gameplay, adoption status, geometry and policies remain authoritative in the YAML tables in this directory. This record captures branch closure once; it is not a generated view that must refresh on every commit. Source branches and commits remain available. Their original histories must not enter public main; final integration uses squash.

The [path audit](branch-integration-paths.json) records every changed source path, source commit/blob, current destination or supersession reason, the comparison/main tree hashes, and exact-byte proof for the 28 recovered gameplay images. Source comparisons used main `5b261b4`; subsequent PR157 integration is recorded below. The isolated recovered-code proof tree is `1cc48e2afbe2bc80301eeb3ceb98e708367907af`; it is not an independently publishable migration tree.

| Remote branch / recorded source head | Completed work | Current integration state |
|---|---|---|
| `51-asset-preflight-20261018` / `c4afe0e` | Asset moves absorbed by the [migration manifest](../production/20261018-asset-migration.json); WebP `f79eb74`, MAP IDs `d3c8950`, pruning `4cef5de`, branding `549989e` supersede old PNG/raw/fixtures/drafts | Already absorbed; keep later canonical state |
| `68-ignore-finder-metadata` / `2042408` | Exact Finder metadata exclusion and both nested/hidden sample regression tests exist in current verifier/tests | Already absorbed |
| `oblique-mask-tools-20261023` / `a5d027d` | Source head is an ancestor of `29da5dc`, which entered squashed PR158/159; later YAML/opening/canonical-adoption enhancements remain | Already absorbed; private `.gi` inventories intentionally remain excluded |
| `body-maps-baseline-20261022` / `3c9f9e9` | Recovered 28 gameplay images and 20 weapon masters; recovered map-enemy skill; entity/policy facts integrated into canonical YAML. Current body geometry supersedes old alternate BDY-17/registration evidence | Recovered in the shared worktree; final consolidated PR138 validation/merge pending |
| `teramachi-rest-mocks-20261023` / `029d19e` | Recovered polygon floors, water/stairs surfaces, marker widths, fence labels and YAML town renderer; plan facts already in YAML. Twelve old derived mock sets remain historical at source | Recovered in the shared worktree; final consolidated PR138 validation/merge pending |
| `trm-temple-map-conditions` (PR138) / `5e271ce` | Recovered battle/layout/pasteback tools; BG005 actual file deleted per `19ab92a`, with canonical rejection synchronized by core. Old tatami/camera/exterior-first conditions and adoption style references are superseded by current YAML | Consolidated migration PR138 validation/merge pending; do not publish the isolated code proof tree |
| `155-c001-kindergarten-diagonal-walk` (PR157) / `59bcdfa` | All C001/C002 source edits reconciled; asset-layout conflict retained YAML placement IDs plus the walk convention | Reconciled and squashed into main `ae90c04` |

Historical source commits preserve superseded adoption and review records. They are evidence, not permission to restore deleted runtime images or rejected takes. No bulk source snapshot dump is imported.

Focused checks passed without displaying or creating images: Python AST syntax, rectangular/polygon walk-grid boundaries, explicit/default marker widths, malformed polygon rejection, current-YAML guide geometry for TRM-02/04/05, preservation of opening/canonical APIs, town check (22 connections, zero problems), and battle measurement (slope 0.03165; rise 52.9px; floor share 0.852). Full migration tests and independent review govern the final PR138 merge.
