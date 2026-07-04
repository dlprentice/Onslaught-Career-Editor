# Wave1192 FearGrid/AI-Grid Current-Risk Review

Status: complete static read-back evidence pending artifact commit
Date: 2026-06-06
Tag: `wave1192-feargrid-ai-grid-current-risk-review`

Wave1192 accounts for `6 FearGrid/AI-grid current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator. It also re-read context row `FearGridTrackedObject__LookupFearWeightByArchetype` because `CFearGrid__RebuildOccupancyAndScheduleTick` depends on its archetype weight lookup. This is a static AI-grid contract review for occupancy, clearance, free-cell search, tracked-object weighting, and the CUnitAI cooldown bridge; it is meant to make the clean-room rebuild specification more concrete, not to claim runtime pathing, AI, or gameplay parity.

Targets:

| Address | Function | Static contract |
| --- | --- | --- |
| `0x0040dda0` | `CUnitAI__RefreshGridCooldownFromOccupiedCells` | HUD objective-panel caller bridge that gates on `DAT_00672fd0`, calls object vfunc `+0x10c`, samples `CFearGrid__GetOccupancyAtWorldVector` through `DAT_008a9d7c` and `DAT_008a9d80`, and refreshes `this+0x2e8` when either occupancy grid is active. |
| `0x0044c3d0` | `CFearGrid__ctor_base` | Constructor-style body installs vtable `0x005db2a4`, stores `grid_id` at `this+0x8008`, calls `CFearGrid__RebuildOccupancyAndScheduleTick`, returns `this`, and ends with `RET 0x4`. |
| `0x0044c440` | `CFearGrid__RebuildOccupancyAndScheduleTick` | Clears the occupancy plane at `this+0x08`, initializes the clearance plane at `this+0x4008`, filters tracked objects by grid id, calls the tracked-object weight helper, marks occupancy, clears nearby blocking clearance cells, and schedules event 1000. |
| `0x0044c720` | `CFearGrid__GetOccupancyAtWorldVector` | Takes a 16-byte by-value world vector, maps world X/Y into 8-unit 64x64 grid coordinates, reads the occupancy plane at `this+0x08`, returns zero outside the grid, and ends with `RET 0x10`. |
| `0x0044c780` | `CFearGrid__ReadClearanceAtWorldVectorIfAboveTerrainDelta` | Samples terrain through `CStaticShadows__SampleShadowHeightBilinear`, applies the threshold at `0x005db2b0`, reads the clearance plane at `this+0x4008` when in range, otherwise returns fallback clear value, and ends with `RET 0x10`. |
| `0x0044c810` | `CFearGrid__FindNearestFreeCellSpiral` | Converts an in/out world vector into grid coordinates, spirals through the occupancy plane at `this+0x08` for a zero cell, snaps the vector back using scale constant `0x005d8c44`, and ends with `RET 0x4`. |
| `0x004daff0` | `FearGridTrackedObject__LookupFearWeightByArchetype` | Context row: reads tracked-object name pointer `this+0x118`, scans `DAT_008553f8`, compares against `entry+0x30`, returns `entry+0x34` on match or `_DAT_005d856c` on miss; not counted as one of the six focused rows. |

Read-back evidence:

| Item | Result |
| --- | --- |
| Pre/post rows | `7` metadata rows, `7` tag rows, `14 xref rows`, `570 instruction rows`, and `7 decompile rows` |
| Dry run | `updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=7 tags_added=93 missing=0 bad=0` |
| Apply | `updated=7 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=7 tags_added=93 missing=0 bad=0`; `REPORT: Save succeeded` |
| Final dry | `updated=0 skipped=7 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0` |
| Backup | `[maintainer-local-ghidra-backup-root]\BEA_20260606-183042_post_wave1192_feargrid_ai_grid_current_risk_review_verified` |

No rename, no signature change, no function-boundary change, and no executable-byte change occurred. Codex read-only consults used; no Cursor/Composer.

Static closure remains `6411/6411 = 100.00%` with `0 / 0 / 0` debt. Expanded static surface remains `1560/1560 = 100.00%`. Wave1108 current focused accounting is now `832/1179 = 70.57%`; current risk candidates: 6166; current focused candidates: 1167; live regenerated current focused candidates: 1167; remaining active focused work: 347; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.

Static clean-room target: rebuild-grade static contracts as a rebuild-grade specification for a future clean-room implementation aiming at no noticeable difference. Exact CFearGrid/CUnitAI/tracked-object/vector/list/grid-entry layouts, exact source-body identity, runtime AI/fear/pathing/firing/cooldown behavior, gameplay parity, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.

Probe token anchor: Wave1192; wave1192-feargrid-ai-grid-current-risk-review; 832/1179 = 70.57%; 6 FearGrid/AI-grid current-risk rows; context row FearGridTrackedObject__LookupFearWeightByArchetype; current focused candidates: 1167; live regenerated current focused candidates: 1167; remaining active focused work: 347; current risk candidates: 6166; fresh Ghidra export; comment/tag normalization; updated=7 skipped=0; comment_only_updated=7; tags_added=93; final dry updated=0 skipped=7; no rename; no signature change; no function-boundary change; no executable-byte change; Codex read-only consults used; no Cursor/Composer; CUnitAI__RefreshGridCooldownFromOccupiedCells; CFearGrid__ctor_base; CFearGrid__RebuildOccupancyAndScheduleTick; CFearGrid__GetOccupancyAtWorldVector; CFearGrid__ReadClearanceAtWorldVectorIfAboveTerrainDelta; CFearGrid__FindNearestFreeCellSpiral; FearGridTrackedObject__LookupFearWeightByArchetype; DAT_008a9d7c; DAT_008a9d80; DAT_008553f8; event 1000; 0 / 0 / 0; 6411/6411 = 100.00%; 14 xref rows; 570 instruction rows; 7 decompile rows; [maintainer-local-ghidra-backup-root]\BEA_20260606-183042_post_wave1192_feargrid_ai_grid_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction; rebuild-grade static contracts; no noticeable difference; rebuild-grade specification.
