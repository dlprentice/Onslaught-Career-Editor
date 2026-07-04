# Ghidra DXCompass Lifecycle Review Wave1060 Readiness Note

Status: complete static re-audit comment/tag-normalization evidence
Date: 2026-06-01
Scope: `dxcompass-lifecycle-review-wave1060`

Wave1060 re-read the DXCompass lifecycle/render-support surface after earlier DXCompass, HUD-head, and Wave1013 HUD context work. The pass saved function-tag normalization for nine already named/commented rows and corrected one stale caller comment at `0x00427210 CDXCompass__Render`. It made no renames, no signature changes, no function-boundary changes, and no executable-byte changes.

Primary targets:

| Address | Existing saved identity | Fresh evidence |
| --- | --- | --- |
| `0x00406040 CDXCompass__GetTrackedPositionX` | `double __fastcall CDXCompass__GetTrackedPositionX(void * context)` | Reads the tracked pointer from `context+0x4b0` and returns the `+0x1c` float through the FPU; called by `CDXCompass__Render` and `CDXCompass__UpdateDynamicOverlayTexture`. |
| `0x0040c630 CDXCompass__GetTrackedPositionY` | `double __fastcall CDXCompass__GetTrackedPositionY(void * context)` | Reads the tracked pointer from `context+0x4b0` and returns the `+0x20` float through the FPU; called by `CDXCompass__Render` and `CDXCompass__UpdateDynamicOverlayTexture`. |
| `0x004270e0 CDXCompass__InitMarkerArrays` | `void __fastcall CDXCompass__InitMarkerArrays(void * this)` | Called by `CHud__Init`; zeroes the two 30-slot compass marker arrays at `this+0x3c24` with `0x18` stride, then calls `CDXCompass__Init`. |
| `0x00427110 CDXCompass__LoadTextures` | `void __fastcall CDXCompass__LoadTextures(void * this)` | Called by `CHud__LoadTextures`; loads `ThreatFlash`, `DamageFlash`, `BarLine`, and `CompassObjectiveMarker` refs into `this+0x3ef4` through `this+0x3f00`. |
| `0x00427190 CDXCompass__DestroyTextures` | `void __fastcall CDXCompass__DestroyTextures(void * this)` | Called by `CHud__ShutDown`; releases those four compass texture refs through the texture ref-count helper and zeroes the slots. |
| `0x00427200 CDXCompass__Reset` | `void __fastcall CDXCompass__Reset(void * this)` | Clears the compass render/state flag at `this+0x3c10`; `CDXCompass__InitFields` is the observed reset-context caller. |
| `0x00427210 CDXCompass__Render` | `void __thiscall CDXCompass__Render(void * this, void * battleEngineContext)` | Called by `CDXCompass__RenderWorldSpaceOverlay`; draws threat/damage/bar/objective compass sprites, calls the tracked X/Y getters, toggles render state, and flushes `CFastVB`. |

Context rows tagged by the same normalization pass:

- `0x0053be40 CDXCompass__Init`
- `0x0053c1d0 CDXCompass__BuildRingGeometry`

Read-back evidence:

- Primary pre exports: `7` metadata rows, `7` tag rows, `12` xref rows, `731` function-body instruction rows, and `7` decompile rows.
- Context pre exports: `13` metadata rows, `13` tag rows, `14` xref rows, `2339` function-body instruction rows, and `13` decompile rows.
- Post tagged exports: `9` metadata rows, `9` tag rows, `15` xref rows, `1081` function-body instruction rows, and `9` decompile rows.
- Dry run reported `updated=0 skipped=0 tags_added=110 missing=0 bad=0`.
- Apply reported `updated=9 skipped=0 tags_added=110 missing=0 bad=0` with `REPORT: Save succeeded`.
- Final dry/read-back reported `updated=0 skipped=9 tags_added=0 missing=0 bad=0`.
- Comment-correction dry/apply/final-dry reported `updated=0 skipped=8 tags_added=0 comment_updated=1 missing=0 bad=0`, then `updated=1 skipped=8 tags_added=0 comment_updated=1 missing=0 bad=0`, then `updated=0 skipped=9 tags_added=0 comment_updated=0 missing=0 bad=0`.
- Queue closure remains `6246/6246 = 100.00%`.
- Wave911 focused progress remains `812/1408 = 57.67%` because the Wave1060 rows were outside the original Wave911 focused seed.
- Expanded static surface progress advances to `1148/1509 = 76.08%`; `0x00427210 CDXCompass__Render` was already present in post-900 context evidence, so it is not double-counted.
- Wave911 top-500 coverage remains `500/500 = 100.00%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260601-205027_post_wave1060_dxcompass_lifecycle_review_verified`, `19` files, `174721927` bytes, `DiffCount=0`, `HashDiffCount=0`.

What this proves:

- The nine target/context rows exist in the saved Ghidra project with expected names and signatures.
- The saved comments remain coherent with fresh metadata/xref/instruction/decompile evidence.
- `0x00427210 CDXCompass__Render` now names `CDXCompass__RenderWorldSpaceOverlay` instead of the stale `CDXBattleLine` caller label.
- The rows now carry `dxcompass-lifecycle-review-wave1060` and `wave1060-readback-verified` function tags.
- The old tag-coverage caveat for these reviewed DXCompass rows is superseded by read-back evidence.

What remains unproven:

- Runtime compass/HUD rendering behavior.
- Exact `CHud`/`CDXCompass`/battle-engine context layouts.
- Exact source-body identity.
- BEA patching behavior, gameplay outcomes, and rebuild parity.

Next candidate note: continue with the next focused static re-audit cluster; prefer read-only review first and mutate only when fresh evidence proves a correction or normalization need.

Probe token anchor: Wave1060; dxcompass-lifecycle-review-wave1060; 0x00406040 CDXCompass__GetTrackedPositionX; 0x0040c630 CDXCompass__GetTrackedPositionY; 0x004270e0 CDXCompass__InitMarkerArrays; 0x00427110 CDXCompass__LoadTextures; 0x00427190 CDXCompass__DestroyTextures; 0x00427200 CDXCompass__Reset; 0x00427210 CDXCompass__Render; 0x0053be40 CDXCompass__Init; 0x0053c1d0 CDXCompass__BuildRingGeometry; 812/1408 = 57.67%; 1148/1509 = 76.08%; 500/500 = 100.00%; 6246/6246 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260601-205027_post_wave1060_dxcompass_lifecycle_review_verified; tag normalization.
