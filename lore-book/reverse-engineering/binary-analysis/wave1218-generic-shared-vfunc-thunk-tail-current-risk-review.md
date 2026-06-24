# Wave1218 Generic Shared Vfunc Thunk Tail Current-Risk Review

Wave1218 measured anchor: unique-address accounting governs active current-risk progress. Probe token anchor: Wave1218; wave1218-generic-shared-vfunc-thunk-tail-current-risk-review; 1163/1179 = 98.64%; 8 generic/shared vfunc-thunk tail current-risk rows; VFuncSlot_12_00405db0; CDebris__GetClassId; CFlexArray__Free_thunk; SharedVFunc__NoOp_Ret08; CWaitingThread__dtor_thunk; SharedGroundUnit__VFunc_66_UpdateVerticalDriftPickupAndEffects_0049fc10; SharedVFunc__ReturnZero_004d6b20; SharedVFunc__ForwardProcessNoOp; 6411/6411 = 100.00%; 0 / 0 / 0; 143 xref rows; 122 instruction rows; 8 decompile rows; current focused candidates: 1117; live regenerated current focused candidates: 1117; remaining active focused work: 16; current risk candidates: 6166; fresh Ghidra export; read-only review; no mutation; no rename; no signature change; no comment change; no tag change; no function-boundary change; no executable-byte change; unique-address accounting; Codex read-only consults used; no Cursor/Composer; legacy additive counter is deprecated (`1194/1179`); 26 duplicate-address overcount; Wave1145 arithmetic overcount: 5; Wave911 is historical-retired/non-reconstructable at 812/1408 = 57.67%; 1179/1179 current-risk focused rows reviewed or superseded with bounded static evidence; static-reaudit-current-risk-ledger.json; static-reaudit-measurement-register.md; continuity denominator; G:\GhidraBackups\BEA_20260607-222830_post_wave1218_generic_shared_vfunc_thunk_tail_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction; rebuild-grade static contracts; no noticeable difference.

Status: complete static current-risk read-only review; later validation passed by current-risk closeout gates
Date: 2026-06-07
Tag: `wave1218-generic-shared-vfunc-thunk-tail-current-risk-review`

Wave1218 re-read `8 generic/shared vfunc-thunk tail current-risk rows` from the `wave1108-current-risk-rank` continuity denominator with fresh Ghidra export evidence. This is a read-only review with no mutation, no rename, no signature change, no comment change, no tag change, no function-boundary change, and no executable-byte change.

Static closure remains `6411/6411 = 100.00%` with `0 / 0 / 0` commentless/exact-undefined/`param_N` debt. Active current-risk progress is `1163/1179 = 98.64%`; remaining active focused work: 16. The legacy additive counter is deprecated (`1194/1179`) because it includes a 26 duplicate-address overcount and Wave1145 arithmetic overcount: 5. Wave911 is historical-retired/non-reconstructable at `812/1408 = 57.67%`; current risk candidates: 6166; current focused candidates: 1117; live regenerated current focused candidates: 1117; current-risk denominator; continuity denominator; focused threshold `15`; not Wave911 reconstruction.

## Targets

| Address | Function | Static evidence |
| --- | --- | --- |
| `0x00405db0` | `VFuncSlot_12_00405db0` | Generic no-op vtable slot returning with `RET 0x8`; exact owner table and argument semantics remain unproven. |
| `0x00441370` | `CDebris__GetClassId` | CDebris class/OID id helper returning `0x1f`; exact source enum identity remains unproven. |
| `0x0044b290` | `CFlexArray__Free_thunk` | Exact jump thunk to `CFlexArray__Free`; direct callers branch to the thunk, while exact thunk provenance and element-type ownership remain unproven. |
| `0x00452da0` | `SharedVFunc__NoOp_Ret08` | Shared no-op target reused by broad unrelated tables and a missile post-hook caller; instruction body is `RET 0x8`. |
| `0x00466290` | `CWaitingThread__dtor_thunk` | One-instruction cleanup thunk to `0x00528bf0 CWaitingThread__dtor_body`; runtime threading behavior and exact layout remain separate proof. |
| `0x0049fc10` | `SharedGroundUnit__VFunc_66_UpdateVerticalDriftPickupAndEffects_0049fc10` | Shared GroundUnit slot-66 body for vtables `0x005e0684` and `0x005e3074`; static vertical-drift, pickup, and linked-effect evidence only. |
| `0x004d6b20` | `SharedVFunc__ReturnZero_004d6b20` | Broad shared vtable/callsite target that returns zero without reading object state; owner-specific naming remains intentionally avoided. |
| `0x004e66d0` | `SharedVFunc__ForwardProcessNoOp` | Owner-neutral process/no-op forwarder; stale CWaypoint ownership remains superseded by `RET 0x4` and ECX passthrough evidence. |

Fresh Ghidra export counts: `8` metadata rows, `8` tag rows, `143 xref rows`, `122 instruction rows`, and `8 decompile rows`.

Codex read-only consults used; no Cursor/Composer. The central accounting paths are `static-reaudit-current-risk-ledger.json`, `static-reaudit-measurement-register.md`, `reverse-engineering/binary-analysis/static-reaudit-progress.json`, `reverse-engineering/binary-analysis/static-reaudit-accounting-guard.md`, `reverse-engineering/binary-analysis/mapped-systems.md`, and `wave1108-current-risk-rank`.

Verified backup: `G:\GhidraBackups\BEA_20260607-222830_post_wave1218_generic_shared_vfunc_thunk_tail_current_risk_review_verified` (`19` files, `176425863` bytes, `DiffCount=0`, `HashDiffCount=0`).

Boundary: this wave strengthens rebuild-grade static contracts and the rebuild-grade specification aiming at no noticeable difference for owner-neutral vtable no-ops, thunk dispatch, class metadata, waiting-thread cleanup thunk context, and shared GroundUnit/RTCutscene/SquadNormal helper boundaries. Runtime behavior, runtime threading behavior, runtime pickup/effect behavior, exact layouts, exact source identity, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.
