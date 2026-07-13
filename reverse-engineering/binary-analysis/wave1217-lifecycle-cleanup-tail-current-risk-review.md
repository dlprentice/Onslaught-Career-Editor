# Wave1217 Lifecycle Cleanup Tail Current-Risk Review

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 live correction closeout:** `0x004df520` → `CActor__dtor_base_Thunk` (was `CActor__dtor_base`). Current live Ghidra reflects confirmed rows only; older conflicting text below is superseded only where confirmed. Use the [closeout](ghidra-full-reaudit-closeout-2026-07-13.md); final per-address decisions and exact before/after metadata are in `reverse-engineering/binary-analysis/ghidra-reviewed-correction-decisions-2026-07-13.jsonl` and `reverse-engineering/binary-analysis/ghidra-reviewed-correction-plan-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Wave1217 measured anchor: unique-address accounting governs active current-risk progress. Probe token anchor: Wave1217; wave1217-lifecycle-cleanup-tail-current-risk-review; 1155/1179 = 97.96%; 10 lifecycle/cleanup tail current-risk rows; CCarrierAI__scalar_deleting_dtor; CTree__scalar_deleting_dtor; CActorBase__shared_scalar_deleting_dtor_004bfd00; CRTBuilding__ScalarDeletingDestructor; CActor__dtor_base_Thunk; CCSPersistentThing__dtor_base; CTree__dtor_base; CWarspite__ScalarDeletingDestructor; CMine__VFunc02_CleanupLinkedParticleAndForward; CMine__TryDestroyedResetAndDispatchVFunc1D4; 6411/6411 = 100.00%; 0 / 0 / 0; 12 xref rows; 137 instruction rows; 10 decompile rows; 103 context xref rows; 681 context instruction rows; 14 context decompile rows; 29 data-xref rows; current focused candidates: 1117; live regenerated current focused candidates: 1117; remaining active focused work: 24; current risk candidates: 6166; fresh Ghidra export; comment/tag normalization; stale CTree destructor-body reference corrected; CCarrierAI tag gap corrected; updated=10 skipped=0; comment_only_updated=10; tags_added=80; no rename; no signature change; no function-boundary change; no executable-byte change; unique-address accounting; Codex read-only consults used; no Cursor/Composer; legacy additive counter is deprecated (`1186/1179`); 26 duplicate-address overcount; Wave1145 arithmetic overcount: 5; Wave911 is historical-retired/non-reconstructable at 812/1408 = 57.67%; 1179/1179 current-risk focused rows reviewed or superseded with bounded static evidence; static-reaudit-current-risk-ledger.json; static-reaudit-measurement-register.md; unit-battleengine-gameplay-static-contract.md; mesh-resource-render-static-contract.md; continuity denominator; [maintainer-local-ghidra-backup-root]\BEA_20260607-110625_post_wave1217_lifecycle_cleanup_tail_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction; rebuild-grade static contracts; no noticeable difference.

Status: complete static current-risk lifecycle cleanup tail normalization; later validation passed by current-risk closeout gates
Date: 2026-06-07
Tag: `wave1217-lifecycle-cleanup-tail-current-risk-review`

Wave1217 re-read `10 lifecycle/cleanup tail current-risk rows` from the `wave1108-current-risk-rank` continuity denominator with fresh Ghidra export evidence. Mutation was limited to comment/tag normalization: stale CTree destructor-body reference corrected, CCarrierAI tag gap corrected, `updated=10 skipped=0`, `comment_only_updated=10`, `tags_added=80`, no rename, no signature change, no function-boundary change, and no executable-byte change.

Static closure remains `6411/6411 = 100.00%` with `0 / 0 / 0` commentless/exact-undefined/`param_N` debt. Active current-risk progress is `1155/1179 = 97.96%`; remaining active focused work: 24. The legacy additive counter is deprecated (`1186/1179`) because it includes a 26 duplicate-address overcount and Wave1145 arithmetic overcount: 5. Wave911 is historical-retired/non-reconstructable at `812/1408 = 57.67%`; current risk candidates: 6166; current focused candidates: 1117; live regenerated current focused candidates: 1117; current-risk denominator; continuity denominator; focused threshold `15`; not Wave911 reconstruction.

## Targets

| Address | Function | Static evidence |
| --- | --- | --- |
| `0x00421b80` | `CCarrierAI__scalar_deleting_dtor` | Vtable DATA xref `0x005d93d8`; calls `CCarrierAI__dtor_base`, frees on delete flag bit 0, returns `this`. |
| `0x004bfce0` | `CTree__scalar_deleting_dtor` | Vtable DATA xref `0x005dd9dc`; calls `CTree__dtor_base at 0x004f63c0`; stale CTree destructor-body reference corrected. |
| `0x004bfd00` | `CActorBase__shared_scalar_deleting_dtor_004bfd00` | Shared actor-base wrapper with DATA xrefs `0x005dd5f4`, `0x005ded4c`, and `0x005e45e4`; owner name remains intentionally shared/bounded. |
| `0x004db8d0` | `CRTBuilding__ScalarDeletingDestructor` | Vtable DATA xref `0x005de9c0`; calls `CRTBuilding__Destructor` and frees on delete flag bit 0. |
| `0x004df520` | `CActor__dtor_base_Thunk` | Called by the shared actor-base wrapper at `0x004bfd03`; jumps to `CActor__dtor_base`, which chains through `CComplexThing__dtor_base`. |
| `0x004f3a70` | `CCSPersistentThing__dtor_base` | Called by `CCSPersistentThing__scalar_deleting_dtor`; shuts down monitor state and chains into `CCollisionSeekingRound__Destructor`. |
| `0x004f63c0` | `CTree__dtor_base` | Called by `CTree__scalar_deleting_dtor`; frees the falling-tree data pointer at `this+0x48`, clears it, then calls `CThing__dtor_base`. |
| `0x005044f0` | `CWarspite__ScalarDeletingDestructor` | Vtable DATA xref `0x005dfbe0`; calls `CWarspite__Destructor` and frees on delete flag bit 0. |
| `0x004ba490` | `CMine__VFunc02_CleanupLinkedParticleAndForward` | DATA xref `0x005e1b8c`; clears linked particle/effect owner-link state, removes/frees the list node, then forwards to `CUnit__VFunc02_CleanupWorldLinksAndForward`. |
| `0x004ba9d0` | `CMine__TryDestroyedResetAndDispatchVFunc1D4` | DATA xref `0x005e1c4c`; calls `CGroundUnit__MarkDestroyedAndResetState`, then dispatches receiver vfunc `+0x1d4` when the reset gate succeeds. |

Fresh Ghidra export counts: `10` metadata rows, `10` tag rows, `12 xref rows`, `137 instruction rows`, and `10 decompile rows`. Context export counts: `14` metadata rows, `14` tag rows, `103 context xref rows`, `681 context instruction rows`, and `14 context decompile rows`. Data evidence includes `29 data-xref rows`.

Codex read-only consults used; no Cursor/Composer. The central accounting paths are `static-reaudit-current-risk-ledger.json`, `static-reaudit-measurement-register.md`, `reverse-engineering/binary-analysis/static-reaudit-progress.json`, `reverse-engineering/binary-analysis/static-reaudit-accounting-guard.md`, `reverse-engineering/binary-analysis/mapped-systems.md`, `unit-battleengine-gameplay-static-contract.md`, `mesh-resource-render-static-contract.md`, and `wave1108-current-risk-rank`.

Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260607-110625_post_wave1217_lifecycle_cleanup_tail_current_risk_review_verified` (`19` files, `176425863` bytes, `DiffCount=0`, `HashDiffCount=0`).

Boundary: this wave strengthens rebuild-grade static contracts and the rebuild-grade specification aiming at no noticeable difference for lifecycle cleanup, scalar-deleting wrappers, actor/tree/persistent-collision cleanup, render-building cleanup, Warspite cleanup, and Mine particle/destruction forwarding. Runtime cleanup behavior, exact layouts, exact source identity, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.
