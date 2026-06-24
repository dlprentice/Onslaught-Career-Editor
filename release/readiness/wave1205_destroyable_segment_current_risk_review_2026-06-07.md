# Wave1205 Destroyable Segment Current-Risk Review Readiness Note

Status: complete static read-only review; validation passed; later static closeout validation passed
Date: 2026-06-07
Scope: `wave1205-destroyable-segment-current-risk-review`

Wave1205 reviewed `5 destroyable-segment current-risk rows` with fresh Ghidra read-back evidence and no mutation. The rows are `CDestructableSegment__RegisterChild`, `CDestroyableCoreSegment__AreCoreChildrenDestroyed`, `CDestructableSegmentsController__GetSegmentLastDamageTimeByIndex`, `CDestructableSegmentsController__GetSegmentLastDamageAmountByIndex`, and `CDestructableSegmentsController__SetAllSegmentsActiveFlagAndRefreshMetric`.

Read-back evidence:

- `5` metadata rows, `5` tag rows, `9 xref rows`, `96 instruction rows`, and `5 decompile rows`.
- Read-only review: no mutation, no rename, no signature change, no comment change, no tag change, no function-boundary change, and no executable-byte change.
- Codex read-only consults used; no Cursor/Composer.
- Verified backup: `G:\GhidraBackups\BEA_20260607-021737_post_wave1205_destroyable_segment_current_risk_review_verified`, `19` files, `176425863` bytes, `DiffCount=0`, `HashDiffCount=0`.
- Static closure remains `6411/6411 = 100.00%`; static debt remains `0 / 0 / 0`.
- Active current-risk progress is `1076/1179 = 91.26%`; remaining active focused work: 103.
- Current risk candidates: 6166; current focused candidates: 1141; live regenerated current focused candidates: 1141.
- Active completion target: `1179/1179 current-risk focused rows reviewed or superseded with bounded static evidence`.
- Legacy additive counter is deprecated (`1107/1179`), with 26 duplicate-address overcount and Wave1145 arithmetic overcount: 5.
- Wave911 remains historical-retired/non-reconstructable at `812/1408 = 57.67%`.

What this proves:

- The five target function rows exist in the saved Ghidra project with bounded names, signatures, comments, and tags.
- Fresh xrefs tie the rows to controller init/process, threshold/cascade, unit-AI segment-entry, CUnit recent segment damage meter, and one global callsite.
- The destroyable-segment static contract now has current-risk read-back for child registration, core-child destruction predicate, damage telemetry getters, and bulk active-flag/cache refresh.

What remains unproven:

- Runtime destructable-segment behavior.
- Runtime destroyable-segment behavior.
- Runtime cascade behavior.
- Exact concrete layouts.
- Exact source-body identity.
- BEA patching behavior.
- Gameplay outcomes, visual QA, rebuild parity, and no-noticeable-difference parity.

Probe token anchor: Wave1205; wave1205-destroyable-segment-current-risk-review; 1076/1179 = 91.26%; 5 destroyable-segment current-risk rows; current focused candidates: 1141; live regenerated current focused candidates: 1141; remaining active focused work: 103; current risk candidates: 6166; fresh Ghidra export; read-only review; no mutation; no rename; no signature change; no comment change; no tag change; no function-boundary change; no executable-byte change; Codex read-only consults used; unique-address accounting; legacy additive counter is deprecated; 1107/1179; 26 duplicate-address overcount; Wave1145 arithmetic overcount: 5; Wave911 is historical-retired/non-reconstructable at 812/1408 = 57.67%; CDestructableSegment__RegisterChild; CDestroyableCoreSegment__AreCoreChildrenDestroyed; CDestructableSegmentsController__GetSegmentLastDamageTimeByIndex; CDestructableSegmentsController__GetSegmentLastDamageAmountByIndex; CDestructableSegmentsController__SetAllSegmentsActiveFlagAndRefreshMetric; 0 / 0 / 0; 6411/6411 = 100.00%; 9 xref rows; 96 instruction rows; 5 decompile rows; G:\GhidraBackups\BEA_20260607-021737_post_wave1205_destroyable_segment_current_risk_review_verified; static-reaudit-current-risk-ledger.json; wave1108-current-risk-rank; current-risk denominator; continuity denominator; focused threshold `15`; not Wave911 reconstruction; rebuild-grade static contracts; no noticeable difference.
