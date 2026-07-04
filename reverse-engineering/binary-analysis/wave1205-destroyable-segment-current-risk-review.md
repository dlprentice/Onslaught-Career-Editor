# Wave1205 Destroyable Segment Current-Risk Review

Status: complete static read-only review; validation passed; later static closeout validation passed
Date: 2026-06-07
Tag: `wave1205-destroyable-segment-current-risk-review`

Wave1205 reviewed `5 destroyable-segment current-risk rows` from the `wave1108-current-risk-rank` continuity denominator with fresh Ghidra metadata, tags, xrefs, instructions, and decompile exports. The wave made no mutation: no rename, no signature change, no comment change, no tag change, no function-boundary change, and no executable-byte change.

| Address | Static evidence |
| --- | --- |
| `0x00442700 CDestructableSegment__RegisterChild` | One call to `CSPtrSet__AddToHead((this+0x24), childSegment)`; reached from `CDestructableSegmentsController__Init` and `CDestructableSegmentsController__ProcessNode`. This confirms child-list registration, not global monitor registration. |
| `0x004433f0 CDestroyableCoreSegment__AreCoreChildrenDestroyed` | Reached from threshold/cascade and unit-AI segment-entry callers; warns on missing first core child, walks the `this+0x24` child `CSPtrSet`, and returns false while a child still reports the checked vfunc-slot state and has not set field `+0x38`. |
| `0x004442d0 CDestructableSegmentsController__GetSegmentLastDamageTimeByIndex` | Called twice by `CUnit__VFunc26_GetRecentSegmentDamageMeter`; indexed segment-array getter for field `+0x14`, with fallback constant `0x005d8be0`. |
| `0x00444300 CDestructableSegmentsController__GetSegmentLastDamageAmountByIndex` | Called by `CUnit__VFunc26_GetRecentSegmentDamageMeter`; indexed segment-array getter for field `+0x18`, with zero fallback at `0x005d856c`. |
| `0x00444620 CDestructableSegmentsController__SetAllSegmentsActiveFlagAndRefreshMetric` | Walks controller segment array `this+0x04` up to count `this+0x08`, writes `activeFlag` to segment field `+0x1c`, then refreshes controller cached metric `this+0x18` from `CDestroyableSegment__SumActiveValueRecursive(root)`. |

Evidence counts:

- Fresh exports: `5` metadata rows, `5` tag rows, `9 xref rows`, `96 instruction rows`, and `5 decompile rows`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260607-021737_post_wave1205_destroyable_segment_current_risk_review_verified`, `19` files, `176425863` bytes, `DiffCount=0`, `HashDiffCount=0`.
- Codex read-only consults used; no Cursor/Composer.
- Static closure remains `6411/6411 = 100.00%` with `0 / 0 / 0` commentless/exact-undefined/`param_N` debt.
- Active current-risk progress is `1076/1179 = 91.26%`; remaining active focused work: 103.
- Current risk candidates: 6166; current focused candidates: 1141; live regenerated current focused candidates: 1141.
- Legacy additive counter is deprecated (`1107/1179`) because it includes a 26 duplicate-address overcount and Wave1145 arithmetic overcount: 5.
- Wave911 is historical-retired/non-reconstructable at `812/1408 = 57.67%`.

Contract impact:

- `destroyable-segments-static-contract.md` now has fresh current-risk read-back for the child registration, core-child destroyed gate, damage telemetry getters, and bulk active-flag/cache-refresh helpers around the already reviewed vfunc damage/break/rubble spine.
- `DestructableSegmentsController.cpp/_index.md` remains the owner-map landing page for these rows.
- The active measurement path remains `static-reaudit-current-risk-ledger.json`, `static-reaudit-progress.json`, `static-reaudit-accounting-guard.md`, `static-reaudit-measurement-register.md`, `mapped-systems.md`, and `wave1108-current-risk-rank.md`.
- `wave1108-current-focused-candidates.tsv` is a live focused-candidate artifact, not the complete active denominator by itself; the `1179` current-risk continuity denominator is enforced by the generated ledger and accounting guard.

Boundary:

This is static retail Ghidra evidence only. Runtime destructable-segment behavior, runtime destroyable-segment behavior, runtime cascade behavior, exact concrete layouts, exact source-body identity, BEA patching behavior, gameplay outcomes, visual QA, rebuild parity, and no-noticeable-difference parity remain separate proof. The static target remains rebuild-grade static contracts and a rebuild-grade specification aiming at no noticeable difference.

Probe token anchor: Wave1205; wave1205-destroyable-segment-current-risk-review; 1076/1179 = 91.26%; 5 destroyable-segment current-risk rows; current focused candidates: 1141; live regenerated current focused candidates: 1141; remaining active focused work: 103; current risk candidates: 6166; fresh Ghidra export; read-only review; no mutation; no rename; no signature change; no comment change; no tag change; no function-boundary change; no executable-byte change; Codex read-only consults used; unique-address accounting; legacy additive counter is deprecated; 1107/1179; 26 duplicate-address overcount; Wave1145 arithmetic overcount: 5; Wave911 is historical-retired/non-reconstructable at 812/1408 = 57.67%; CDestructableSegment__RegisterChild; CDestroyableCoreSegment__AreCoreChildrenDestroyed; CDestructableSegmentsController__GetSegmentLastDamageTimeByIndex; CDestructableSegmentsController__GetSegmentLastDamageAmountByIndex; CDestructableSegmentsController__SetAllSegmentsActiveFlagAndRefreshMetric; 0 / 0 / 0; 6411/6411 = 100.00%; 9 xref rows; 96 instruction rows; 5 decompile rows; [maintainer-local-ghidra-backup-root]\BEA_20260607-021737_post_wave1205_destroyable_segment_current_risk_review_verified; static-reaudit-current-risk-ledger.json; wave1108-current-risk-rank; current-risk denominator; continuity denominator; focused threshold `15`; not Wave911 reconstruction; rebuild-grade static contracts; no noticeable difference.
