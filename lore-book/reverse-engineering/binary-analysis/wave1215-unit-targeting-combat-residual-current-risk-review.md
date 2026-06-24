# Wave1215 Unit Targeting Combat Residual Current-Risk Review

Status: complete static current-risk read-only review; validation passed; historical artifact committed
Date: 2026-06-07
Tag: `wave1215-unit-targeting-combat-residual-current-risk-review`

Wave1215 re-read `5 unit-targeting combat residual current-risk rows` from the `wave1108-current-risk-rank` continuity denominator with fresh Ghidra export evidence. This is a read-only review with no mutation, no rename, no signature change, no comment change, no tag change, no function-boundary change, and no executable-byte change.

Static closure remains `6411/6411 = 100.00%` with `0 / 0 / 0` commentless/exact-undefined/`param_N` debt. Active current-risk progress is `1138/1179 = 96.52%`; remaining active focused work: 41. The legacy additive counter is deprecated (`1169/1179`) because it includes a 26 duplicate-address overcount and Wave1145 arithmetic overcount: 5. Wave911 is historical-retired/non-reconstructable at `812/1408 = 57.67%`; current risk candidates: 6166; current focused candidates: 1127; live regenerated current focused candidates: 1127; current-risk denominator; continuity denominator; focused threshold `15`; not Wave911 reconstruction.

## Targets

| Address | Function | Static evidence |
| --- | --- | --- |
| `0x004027c0` | `CAirGuide__AcquireNearestTargetReader` | CALL xref `0x004026fa` from `CAirGuide__HandleEvent`; clears reader `+0x2c`, scans mapwho around the owner, excludes owner/flagged entries, and selects the nearest threshold candidate. |
| `0x00445070` | `CDiveBomber__SelectTarget` | CALL xref `0x004fd4e1` from `CCannon__SelectTarget`; walks the `+0x15c/+0x160` target list, resolves candidate records through `this+4` and `candidate+0x88`, picks highest priority `record+0x40`, or falls back through `CThing__GetCentrePos`. |
| `0x0044e640` | `ComponentTargeting__ScanListsAndMaybeTriggerAction_0044e640` | DATA xref `0x005d96ac`; owner-deferred component-targeting boundary scans list heads selected by object state, compares range/position against owner at `this+0x08`, and conditionally dispatches `0x004ffdd0`. |
| `0x00477cb0` | `CSquadNormal__SelectBestEngagementTarget` | CALL xref `0x004e815a` from `CSquadNormal__ScheduleTargetReaderRefresh` plus no-function callsite `0x004ea584`; one stack argument, state `+0x7c` selects `DAT_00855090`, `DAT_008550b0`, or `DAT_008550c0`, then scores candidates with config weights at `squad+0xa0`. |
| `0x004ea8d0` | `CRelaxedSquad__CreateIterator` | DATA xref `0x005e3b10`; allocates a `0x10`-byte `CSPtrSet`, initializes it, walks member nodes at `this+0xa4`, adds non-null members with `CSPtrSet__AddToHead`, and returns the set snapshot. |

Context exports covered `CAirGuide__HandleEvent`, `CGenericActiveReader__SetReader`, `CMCBuggy__GetTargetValueOrFallback`, `CCannon__SelectTarget`, `CThing__GetCentrePos`, `CSPtrSet__Init`, `CSPtrSet__AddToHead`, `CSquadNormal__IsFactionCompatible`, `CSquadNormal__ScheduleTargetReaderRefresh`, `CSquadNormal__IsValidLinkedSupportForTarget`, `ProjectileBurstCallerBoundary_0044e020`, `ProjectileBurstCallerBoundary_004f4920`, `CSquadNormal__SetReaderAndRefreshSupportSelection`, `CPlane__Hit_CheckFatalDamageAndDie`, and `CSentinel__Init`.

Fresh Ghidra export counts: `5` metadata rows, `5` tag rows, `6 xref rows`, `794 instruction rows`, and `5 decompile rows`. Context export counts: `15` metadata rows, `15` tag rows, `425 context xref rows`, `1123 context instruction rows`, and `15 context decompile rows`. Data-slot evidence includes `1 data-slot xref row` confirming `0x005d96ac` is a non-function slot for the component-targeting boundary.

Codex read-only consults used; no Cursor/Composer. The central accounting paths are `static-reaudit-current-risk-ledger.json`, `static-reaudit-measurement-register.md`, `reverse-engineering/binary-analysis/static-reaudit-progress.json`, `reverse-engineering/binary-analysis/static-reaudit-accounting-guard.md`, `reverse-engineering/binary-analysis/mapped-systems.md`, `unit-battleengine-gameplay-static-contract.md`, and `wave1108-current-risk-rank`.

Verified backup: `G:\GhidraBackups\BEA_20260607-090802_post_wave1215_unit_targeting_combat_residual_current_risk_review_verified` (`19` files, `176425863` bytes, `DiffCount=0`, `HashDiffCount=0`).

Boundary: this wave strengthens rebuild-grade static contracts and the rebuild-grade specification aiming at no noticeable difference for air-guide target-reader acquisition, dive-bomber target output, owner-deferred component targeting, normal-squad engagement scoring, and relaxed-squad iterator snapshots. Runtime targeting behavior, runtime squad AI behavior, runtime component behavior, exact layouts, exact source identity, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.
