# Missile.cpp Functions

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 live correction closeout:** `0x004d8410` comment correction. Current live Ghidra reflects confirmed rows only; older conflicting text below is superseded only where confirmed. Use the [closeout](../../ghidra-full-reaudit-closeout-2026-07-13.md); final per-address decisions and exact before/after metadata are in `reverse-engineering/binary-analysis/ghidra-reviewed-correction-decisions-2026-07-13.jsonl` and `reverse-engineering/binary-analysis/ghidra-reviewed-correction-plan-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

> Source File: Missile.cpp | Binary: BEA.exe
> Debug Path: 0x006309c0

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

## Overview

Missile weapon/projectile implementation. CMissile handles guided missile behavior, initialization from configuration paths, and tracking.

## Functions

| Address | Name | Purpose | Size |
|---------|------|---------|------|
| 0x004baae0 | CMissile__Init | Initializes optional descriptor-backed linked object and base `CRound` state | ~0x12d bytes |
| 0x004bac10 | CMissile__DispatchLinkedObjectVFunc68AndPostHook | Dispatches linked object vfunc `+0x68`, then shared post hook | ~0x24 bytes |

## Wave759 Missile.cpp Unwind Continuation

Wave759 static read-back (`unwind-continuation-wave759`, `wave759-readback-verified`) hardened `0x005d3c50 Unwind@005d3c50` as a `void __cdecl Unwind@005d3c50(void)` compiler-generated SEH unwind allocation-cleanup callback. DATA scope-table xref `0x0061c8ec` points at the body; instruction evidence calls `OID__FreeObject_Callback` on `*(EBP-0x10)` with Missile.cpp debug path `0x006309c0`, line token `0x61`, and allocation/type value `0x0b`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260523-130827_post_wave759_unwind_continuation_verified`. Exact parent source-body identity, runtime exception behavior, runtime cleanup behavior, BEA patching, and rebuild parity remain deferred.

## Exception Handlers

| Address | Name | Line | Purpose |
|---------|------|------|---------|
| 0x005d3c50 | Unwind@005d3c50 | 0x61 | Wave759 cleanup for the Missile.cpp allocation/free-object row |

## Key Observations

- **Large allocation** - 0x428 bytes (1064 bytes) for missile data structure
- **Path-based init** - Loads from string at this+0xf0+0xc
- **Function pointers** - Sets up callbacks at 0x00403f40 and 0x00403f80
- **Pool ID 0x61** - Uses memory pool 97

## Wave456 Missile Evidence

Wave456 is static retail Ghidra evidence only. It saved comments, signatures, tags, and corrected names for the `CMissile` queue head.

| Address | Name | Evidence |
|---------|------|----------|
| 0x004baae0 | CMissile__Init | Reads optional resource path pointer at `this+0xf0+0x0c`, allocates a `0x428` descriptor object with OID type `0x61` and `Missile.cpp` debug path evidence, constructs/copies a `CResourceDescriptor`, calls `PCRTID__CreateObject`, stores the created object at `this+0x30`, invokes the created-object descriptor load vfunc, destroys the temporary descriptor, and calls `CRound__Init`. |
| 0x004bac10 | CMissile__DispatchLinkedObjectVFunc68AndPostHook | Vtable data xref `0x005e3cc0`; `RET 0x8` confirms two stack arguments after `this`, dispatches the linked object at `this+0x30` through vfunc `+0x68` with `arg0/arg1`, then calls `SharedVFunc__NoOp_Ret08`. |

Runtime missile payload behavior, exact virtual slot names, concrete layouts, and exact source identity remain unproven.

## Wave941 Missile Linked-Object Dispatch Review

Wave941 (`missile-linked-object-dispatch-review-wave941`) re-reviewed `0x004baae0 CMissile__Init`, `0x004bac10 CMissile__DispatchLinkedObjectVFunc68AndPostHook`, `0x0050f8b0 CMissile__scalar_deleting_dtor`, and `0x0050f8d0 CMissile__Destructor` with fresh serialized Ghidra exports. Context anchors were `0x0050f7a0 CWorldPhysicsManager__CreateProjectile`, `0x004d8410 CRound__Init`, `0x00452da0 SharedVFunc__NoOp_Ret08`, and vtable anchors `0x005e3ba4`, `0x005e3ba8`, `0x005e3bc8`, `0x005e3cb8`, `0x005e3cc0`, `0x005de82c`, and `0x005de850`. The review was read-only: no mutation, no rename, no signature change, no comment change, no function-boundary change, and no executable-byte change.

Fresh read-back preserved the Wave456 evidence: `CMissile__Init` builds a descriptor-backed linked object at `this+0x30` before delegating to `CRound__Init`, and `CMissile__DispatchLinkedObjectVFunc68AndPostHook` dispatches that linked object through vfunc `+0x68` before calling the broad shared post-hook. Wave911 focused re-audit progress after this pass is `179/1408 = 12.71%`; export-contract closure remains `6113/6113 = 100.00%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260528-034712_post_wave941_missile_linked_object_dispatch_review_verified`.

Probe token anchor: Wave941; `missile-linked-object-dispatch-review-wave941`; `0x004baae0 CMissile__Init`; `0x004bac10 CMissile__DispatchLinkedObjectVFunc68AndPostHook`; `0x0050f8b0 CMissile__scalar_deleting_dtor`; `0x0050f8d0 CMissile__Destructor`; `0x0050f7a0 CWorldPhysicsManager__CreateProjectile`; `0x004d8410 CRound__Init`; `0x00452da0 SharedVFunc__NoOp_Ret08`; `0x005e3ba4`; `0x005e3ba8`; `0x005e3bc8`; `0x005e3cb8`; `0x005e3cc0`; `0x005de82c`; `0x005de850`; read-only review; `179/1408 = 12.71%`; `6113/6113 = 100.00%`; `[maintainer-local-ghidra-backup-root]\BEA_20260528-034712_post_wave941_missile_linked_object_dispatch_review_verified`.

## Related Files

- Round.cpp - CRound base class for projectiles
- BattleEngine.cpp - AddProjectile creates missiles

---
*Discovered via Phase 1 xref analysis (Dec 2025)*
