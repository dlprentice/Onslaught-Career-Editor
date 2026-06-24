# Wave1192 FearGrid/AI-Grid Current-Risk Review

Status: complete static read-back evidence pending artifact commit
Date: 2026-06-06
Tag: `wave1192-feargrid-ai-grid-current-risk-review`

Wave1192 accounts for `6 FearGrid/AI-grid current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator with fresh Ghidra export evidence and saved comment/tag normalization. The counted rows are `CUnitAI__RefreshGridCooldownFromOccupiedCells`, `CFearGrid__ctor_base`, `CFearGrid__RebuildOccupancyAndScheduleTick`, `CFearGrid__GetOccupancyAtWorldVector`, `CFearGrid__ReadClearanceAtWorldVectorIfAboveTerrainDelta`, and `CFearGrid__FindNearestFreeCellSpiral`. Context row `FearGridTrackedObject__LookupFearWeightByArchetype` was re-read because the grid rebuild uses it to mark occupancy from tracked-object archetype weights.

Evidence:

| Item | Result |
| --- | --- |
| Dry run | `updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=7 tags_added=93 missing=0 bad=0` |
| Apply | `updated=7 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=7 tags_added=93 missing=0 bad=0` |
| Final dry | `updated=0 skipped=7 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0` |
| Post exports | `7` metadata rows, `7` tag rows, `14 xref rows`, `570 instruction rows`, and `7 decompile rows` |
| Backup | `G:\GhidraBackups\BEA_20260606-183042_post_wave1192_feargrid_ai_grid_current_risk_review_verified` |

No rename, no signature change, no function-boundary change, and no executable-byte change occurred. Codex read-only consults used; no Cursor/Composer.

Static closure remains `6411/6411 = 100.00%` with `0 / 0 / 0` commentless/exact-undefined/`param_N` debt. Wave1108 current focused accounting is now `832/1179 = 70.57%`; current risk candidates: 6166; current focused candidates: 1167; live regenerated current focused candidates: 1167; remaining active focused work: 347; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.

Static rebuild anchors include `DAT_008a9d7c`, `DAT_008a9d80`, `DAT_008553f8`, and event 1000 scheduling. Static clean-room target: rebuild-grade static contracts as a rebuild-grade specification for a future clean-room implementation aiming at no noticeable difference. Exact CFearGrid/CUnitAI/tracked-object/vector/list/grid-entry layouts, exact source-body identity, runtime AI/fear/pathing/firing/cooldown behavior, gameplay parity, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.

Probe token anchor: Wave1192; wave1192-feargrid-ai-grid-current-risk-review; 832/1179 = 70.57%; 6 FearGrid/AI-grid current-risk rows; context row FearGridTrackedObject__LookupFearWeightByArchetype; current focused candidates: 1167; live regenerated current focused candidates: 1167; remaining active focused work: 347; current risk candidates: 6166; fresh Ghidra export; comment/tag normalization; updated=7 skipped=0; comment_only_updated=7; tags_added=93; final dry updated=0 skipped=7; no rename; no signature change; no function-boundary change; no executable-byte change; Codex read-only consults used; no Cursor/Composer; CUnitAI__RefreshGridCooldownFromOccupiedCells; CFearGrid__ctor_base; CFearGrid__RebuildOccupancyAndScheduleTick; CFearGrid__GetOccupancyAtWorldVector; CFearGrid__ReadClearanceAtWorldVectorIfAboveTerrainDelta; CFearGrid__FindNearestFreeCellSpiral; FearGridTrackedObject__LookupFearWeightByArchetype; DAT_008a9d7c; DAT_008a9d80; DAT_008553f8; event 1000; 0 / 0 / 0; 6411/6411 = 100.00%; 14 xref rows; 570 instruction rows; 7 decompile rows; G:\GhidraBackups\BEA_20260606-183042_post_wave1192_feargrid_ai_grid_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction; rebuild-grade static contracts; no noticeable difference; rebuild-grade specification.
