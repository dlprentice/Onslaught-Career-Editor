# Wave1193 Top Residual Score20-18 Current-Risk Review

Status: complete static read-back evidence committed
Date: 2026-06-06
Tag: `wave1193-top-residual-score20-18-current-risk-review`

Wave1193 accounts for `24 top residual score20-18 current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator. This is a mixed top-residual cleanup wave for rows that still carried high current-risk scores after earlier static closure and subsystem reviews. It saved comment/tag normalization only: no rename, no signature change, no function-boundary change, and no executable-byte change.

Score-band split:

| Band | Rows | Representative static contracts |
| --- | ---: | --- |
| score20 residual rows: 5 | `5` | Cockpit destructor-base cleanup, CShell resource-name copy, CRT runtime/static-init, and CRT errno/FPU source-kind handling. |
| score19 residual rows: 10 | `10` | Shared owner-neutral vfunc no-ops/returners, frontend page no-op, CHazard cleanup, CMissile linked-object dispatch, WingmanStart init, CDXGame destructor thunk, and CRT spawn thunk. |
| score18 residual rows: 9 | `9` | Carrier/Warspite cleanup, destructable-segment controller init, CFEPMain process/save path, CGroundUnit init, CUnitAI firing/postfire animation queue, CBigAirUnit constructor, and CTexture transform matrix tail. |

Representative anchors:

| Address | Function | Static contract |
| --- | --- | --- |
| `0x00424730` | `CCockpit__dtor_base` | Restores CCockpit vtables, releases the owned object at `this+0x8c` when present, then calls `CMonitor__Shutdown`. |
| `0x0055dd7b` | `CRT__RunStaticInitRangesWithOptionalCallback` | Conditionally calls `PTR_CRT__InitRuntimeFromStoredFrameGlobals_006532e8`, then walks static initializer ranges `0x00622b10-0x00622b28` and `0x00622000-0x00622b0c`. |
| `0x00405930` | `SharedVFunc__ReturnZero_00405930` | Owner-neutral broad vtable target that returns integer zero without receiver field access. |
| `0x0047e6e0` | `CHazard__VFunc02_CleanupWorldSoundAndLinkedState` | Cleans hazard audio/linked state, removes world occupancy, then delegates to base cleanup. |
| `0x00444660` | `CDestructableSegmentsController__Init` | Walks mesh nodes, allocates and clears segment tracking, links component monitor entries, and caches root health/value. |
| `0x00462640` | `CFEPMain__Process` | State-gated frontend process/save path with `CCareer__Save` and `CFEPOptions__WriteDefaultOptionsFile` evidence. |
| `0x0047d420` | `CUnitAI__QueueFiringOrPostfireAnimation` | Queues firing or postfire animation after spawn/finalize state and dispatches vfunc `+0xf0`. |
| `0x00579273` | `CTexture__BuildTransformMatrixWithOptionalOffsets` | Stack-locked transform matrix tail with quaternion rotation, pivot offsets, translation offsets, indirect dispatch calls, and `RET 0x1c`. |

Read-back evidence:

| Item | Result |
| --- | --- |
| Pre/post rows | `24` metadata rows, `24` tag rows, `1554 xref rows`, `1386 instruction rows`, and `24 decompile rows` |
| Dry run | `updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=24 tags_added=319 missing=0 bad=0` |
| Apply | `updated=24 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=24 tags_added=319 missing=0 bad=0`; `REPORT: Save succeeded` |
| Final dry | `updated=0 skipped=24 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0` |
| Backup | `[maintainer-local-ghidra-backup-root]\BEA_20260606-185314_post_wave1193_top_residual_score20_18_current_risk_review_verified` |

Static closure remains `6411/6411 = 100.00%` with `0 / 0 / 0` debt. Expanded static surface remains `1560/1560 = 100.00%`. Wave1108 current focused accounting is now `856/1179 = 72.60%`; current risk candidates: 6166; current focused candidates: 1154; live regenerated current focused candidates: 1154; remaining active focused work: 323; current-risk denominator; focused threshold `15`; not Wave911 reconstruction. Fresh Ghidra export, comment/tag normalization, Codex read-only consults used, no Cursor/Composer.

Static clean-room target: rebuild-grade static contracts as a rebuild-grade specification for a future clean-room implementation aiming at no noticeable difference. Exact layouts, exact source-body identity, runtime cleanup/init/frontend/projectile/render/CRT behavior, gameplay or visual parity, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.

Probe token anchor: Wave1193; wave1193-top-residual-score20-18-current-risk-review; 856/1179 = 72.60%; 24 top residual score20-18 current-risk rows; score20 residual rows: 5; score19 residual rows: 10; score18 residual rows: 9; current focused candidates: 1154; live regenerated current focused candidates: 1154; remaining active focused work: 323; current risk candidates: 6166; fresh Ghidra export; comment/tag normalization; updated=24 skipped=0; comment_only_updated=24; tags_added=319; final dry updated=0 skipped=24; no rename; no signature change; no function-boundary change; no executable-byte change; Codex read-only consults used; no Cursor/Composer; CCockpit__dtor_base; CRT__RunStaticInitRangesWithOptionalCallback; SharedVFunc__ReturnZero_00405930; CHazard__VFunc02_CleanupWorldSoundAndLinkedState; CDestructableSegmentsController__Init; CFEPMain__Process; CUnitAI__QueueFiringOrPostfireAnimation; CTexture__BuildTransformMatrixWithOptionalOffsets; 0 / 0 / 0; 6411/6411 = 100.00%; 1554 xref rows; 1386 instruction rows; 24 decompile rows; [maintainer-local-ghidra-backup-root]\BEA_20260606-185314_post_wave1193_top_residual_score20_18_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction; rebuild-grade static contracts; no noticeable difference; rebuild-grade specification.
