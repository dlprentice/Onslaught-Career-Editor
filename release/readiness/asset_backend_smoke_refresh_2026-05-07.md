# Asset Backend Smoke Refresh - 2026-05-07

Status: pass

Source/evidence commit: 89d787579f053e4d81279be10e4882e895f44345

## Scope

Refresh the bounded Battle Engine Aquila asset backend smoke against the user's local read-only Steam install after the latest WinUI/AppCore hardening waves. This report is public-safe and does not include absolute local paths, raw assets, screenshots, media payloads, extracted PNG/FBX files, data URLs, hashes of private payloads, or proof JSON.

Generated outputs remain local and ignored under `subagents/`.

## Commands

Initial attempt:

```powershell
py -3 tools\export_game_assets.py --game-root "<read-only local install>" --out-root subagents\asset_backend_smoke_2026-05-07 --limit-archives 1 --limit-loose-textures 1 --limit-loose-meshes 1 --limit-embedded-bodies 1 --progress-every 1
```

Result: fail

Reason: shell quoting split the install path at `Program Files (x86)`. This was a command-invocation failure, not an asset backend failure.

Rerun:

```text
py -3 tools/export_game_assets.py --game-root "<read-only local install>" --out-root subagents/asset_backend_smoke_2026-05-07 --limit-archives 1 --limit-loose-textures 1 --limit-loose-meshes 1 --limit-embedded-bodies 1 --progress-every 1
```

Result: pass

Important output:

```text
status: ok
loose_textures: attempted 1, succeeded 1, failed 0
loose_meshes: attempted 1, succeeded 1, failed 0
embedded_meshes: attempted 1, succeeded 1, failed 0
language_count: 6
merged language rows: 2571
video files inventoried: 66
video magic values: BIKi
bounded catalog entries: 2640
```

## Bounded Smoke Results

| Lane | Result | Public-safe summary |
| --- | --- | --- |
| Packed resource AYA inventory | PASS | One packed archive was inventoried; texture and mesh references were resolved for that archive. |
| Loose texture export | PASS | One loose texture was exported successfully to local ignored output. |
| Loose mesh export | PASS | One loose mesh was exported successfully to local ignored output. |
| Embedded packed mesh export | PASS | One embedded mesh body was exported successfully to local ignored output. |
| Language corpus export | PASS | Six languages were exported and merged; each language reported 2,571 rows. |
| Video manifest export | PASS | 66 local `.vid` files were inventoried; detected magic was `BIKi`. |
| Cross-surface asset catalog | PASS | The bounded catalog contained one texture entry, one loose mesh entry, one embedded mesh entry, 66 video entries, and 2,571 language entries. |

## What Is Proven

- The current asset extraction backend still runs end-to-end from the active repo.
- The read-only local install can feed packed AYA inventory, texture export, mesh export, embedded mesh export, language export, video manifest generation, and bounded catalog generation.
- Outputs remain under ignored local evidence storage.

## What Is Not Proven

- Full current-corpus extraction coverage for every texture, mesh, embedded body, language row, or video file.
- Public redistribution rights for extracted assets.
- Full native 3D/material/animation rendering.
- Rebuildability of the full game from extracted assets.
- Semantic gameplay logic reconstruction.

## Privacy And Release Boundary

Private extraction outputs, logs, generated catalogs, absolute local paths, and raw asset/media payloads remain excluded from public/community release scope.
