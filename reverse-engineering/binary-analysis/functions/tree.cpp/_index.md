# tree.cpp Functions

> Source File: `tree.cpp` | Binary: `BEA.exe`
> Debug Path: `0x00633a84`

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

## Overview

`tree.cpp` implements destructible environmental tree behavior. Current saved Ghidra evidence covers the CTree falling-tree allocation/update/event slice plus the earlier CRTTree runtime render-object slice. Wave520 (2026-05-18) hardened 8 CTree targets, corrected the destructor-body label, and recovered 3 vtable-backed CTree boundaries.

This page is static retail-binary evidence only. `tree.cpp` is not present in the current `references/Onslaught/` snapshot, so exact source-body identity, concrete CTree/FallingTreeData layouts, runtime falling-tree physics, runtime particle behavior, BEA patching, and rebuild parity remain unproven.

## Wave768 tree.cpp Unwind Continuation

Wave768 static read-back (`unwind-continuation-wave768`, `wave768-readback-verified`) saved `0x005d5320 Unwind@005d5320` as a `void __cdecl Unwind@...(void)` compiler-generated SEH allocation-cleanup row tied to tree.cpp debug path `0x00633a84`. DATA scope-table xref `0x0061dc14` points at the body; instruction/decompile evidence calls `OID__FreeObject_Callback` on `*(EBP+0x4)` with line token `0x8f` and allocation/type value `0x5c`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260523-171555_post_wave768_unwind_continuation_verified`. Static retail Ghidra evidence only; exact parent source-body identity, runtime tree behavior, runtime exception behavior, BEA patching, and rebuild parity remain deferred.

## Wave769 tree.cpp Unwind Continuation

Wave769 static read-back (`unwind-continuation-wave769`, `wave769-readback-verified`) saved the continued tree.cpp unwind cleanup head plus adjacent repeated object cleanup rows as `void __cdecl Unwind@...(void)` comments/tags/signatures. The tree.cpp-anchored rows include `0x005d5350 Unwind@005d5350`, `0x005d5380 Unwind@005d5380`, and `0x005d5388 Unwind@005d5388`; evidence ties them to DATA scope-table xrefs `0x0061dc3c` through `0x0061dc6c`, debug path `0x00633a84`, `OID__FreeObject_Callback`, `CLine__SetBaseVtable_00426360`, and `CParticleManager__RemoveFromGlobalList_Thunk`. The pass also documents repeated object cleanup runs through `0x005d54da Unwind@005d54da` using `CActor__dtor_base`, `CGenericActiveReader__dtor`, and `CSPtrSet__Clear`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260523-174151_post_wave769_unwind_continuation_verified`. Static retail Ghidra evidence only; exact parent source-body identity, runtime tree behavior, runtime exception behavior, BEA patching, and rebuild parity remain deferred.

## Wave1217 Lifecycle Cleanup Tail Current-Risk Review

Wave1217 (`wave1217-lifecycle-cleanup-tail-current-risk-review`) re-read and comment/tag-normalized the CTree lifecycle tail rows `CTree__scalar_deleting_dtor` and `CTree__dtor_base`. The review corrected a stale destructor-body reference so the scalar-deleting wrapper is tied to the actual `CTree__dtor_base` body at `0x004f63c0`, preserved the saved names/signatures, and made no rename, signature, function-boundary, or executable-byte change. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260607-110625_post_wave1217_lifecycle_cleanup_tail_current_risk_review_verified`. Runtime tree cleanup behavior, exact layouts, exact source identity, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.

## Wave520 CTree Functions

| Address | Name | Purpose | Notes |
| --- | --- | --- | --- |
| `0x004f5f60` | [CTree__InitFallingTreeData](./CTree__InitFallingTreeData.md) | Initializes the 0xc0-byte falling-tree data object from a tree-type matrix, scale, and impact vector | `RET 0x0c`; called by `CTree__CreateFallingTree` |
| `0x004f63c0` | [CTree__dtor_base](./CTree__dtor_base.md) | Destructor body that frees the falling-tree data pointer and delegates to `CThing__dtor_base` | Corrected from stale scalar-deleting wrapper label |
| `0x004f6430` | [CTree__ComputeLodBucket](./CTree__ComputeLodBucket.md) | Computes a clamped tree LOD bucket from render/resource scalars | Called by `CEngine__InitDamageSystem` |
| `0x004f68e0` | [CTree__VFunc_28_CreateFallingTreeAfterDelay](./CTree__VFunc_28_CreateFallingTreeAfterDelay.md) | Timer-gated vtable entry that normalizes a direction vector and calls `CTree__CreateFallingTree` | Recovered from CTree vtable slot 40 |
| `0x004f69b0` | [CTree__CreateFallingTree](./CTree__CreateFallingTree.md) | Allocates/initializes falling-tree data, schedules event `0xbb9`, and calls the update helper | `RET 0x4`; uses `DAT_008406b8` tree-type matrix blocks |
| `0x004f6aa0` | [CTree__VFunc_27_CreateFallingTreeFromThing](./CTree__VFunc_27_CreateFallingTreeFromThing.md) | Collision/thing-gated vtable entry that threshold-checks and calls `CTree__CreateFallingTree` | Recovered from CTree vtable slot 39 |
| `0x004f6b80` | [CTree__UpdateFallingTree](./CTree__UpdateFallingTree.md) | Integrates falling-tree motion, traces against the heightfield, emits the ground-hit particle effect, and reschedules events | Static evidence only for runtime physics/particles |
| `0x004f7050` | [CTree__HandleEvent](./CTree__HandleEvent.md) | CTree event-handler boundary for event `3000` update and `3001` target dispatch | Recovered from CTree vtable slot 0 |

## Wave520 Evidence

- Mutation script: `tools/ApplyCTreeWave520.java`.
- Focused probe: `tools/ghidra_ctree_wave520_probe.py`.
- Read-back artifacts: `subagents/ghidra-static-reaudit/wave520-tree-004f5f60/`.
- Dry/apply/final verify: dry `updated=0 skipped=8 renamed=0 would_rename=1 created=0 would_create=3 missing=0 bad=0`; apply `updated=8 skipped=0 renamed=1 would_rename=0 created=3 would_create=0 missing=0 bad=0`; verify dry `updated=0 skipped=8 renamed=0 would_rename=0 created=0 would_create=0 missing=0 bad=0`.
- Post read-back verified `8` metadata rows, `8` tag rows, `12` xref rows, `1544` instruction rows, `1155` focused boundary rows, `8` decompile exports, and `144` vtable-slot rows.
- Queue after Wave520: `6082` functions, `2465` commented, `3617` commentless, `1595` exact-undefined signatures, and `1392` `param_N` signatures.
- Backup: `[maintainer-local-ghidra-backup-root]\BEA_20260517-225110_post_wave520_ctree_verified` with `19` files, `158632839` bytes, `MissingCount=0`, `ExtraCount=0`, and `HashDiffCount=0`.

## CTree Static Observations

- CTree vtable `0x005dd9d8` slot 0 points to `CTree__HandleEvent`.
- CTree vtable `0x005dd9d8` slot 1 points to the existing scalar-deleting wrapper `CTree__scalar_deleting_dtor` at `0x004bfce0`, which calls the corrected destructor body at `0x004f63c0`.
- CTree vtable `0x005dd9d8` slots 39 and 40 point to the recovered falling-tree creation gates at `0x004f6aa0` and `0x004f68e0`.
- `CTree__CreateFallingTree` copies a 12-dword tree-type matrix block from `DAT_008406b8 + this[0x40] * 0x30`, allocates `0xc0` bytes, initializes the object through `CTree__InitFallingTreeData`, stores it at `this+0x48`, schedules event `0xbb9`, and immediately calls `CTree__UpdateFallingTree`.
- `CTree__UpdateFallingTree` references the particle string `Tree Ground Hit Effect`, schedules event `0x7d2` on settle, and uses event `3000` for continued updates.

## CRTTree Runtime Render Object Evidence (Wave497)

Wave497 recovered a CRTTree vtable slice from `PCRTID.cpp` type id `2` / vtable `0x005deb9c`. This is saved static retail-binary evidence only. It does not prove exact source virtual names, concrete `CRTTree` or tree-resource layouts, runtime tree rendering, or rebuild parity.

Wave1046 (`renderthing-crttree-review-wave1046`) re-read this CRTTree render-object slice and adjacent shared `CRenderThing` helpers with no mutation. Fresh evidence reconfirmed `0x004dd960 CRTTree__VFuncSlot02_BuildRenderOutputs`, `0x004de050 CRTTree__VFuncSlot06_GetResourceScalar164`, `0x004de060 SharedVFunc__ReturnResourceField150_004de060`, and the shared `CRenderThing` rows against vtable anchors `0x005deb9c`, `0x005deb1c`, `0x005deaac`, and `0x005dea38`; render-context evidence includes `DAT_0083cd58`, `0x0083ccd8`, and `0x004b6260 CSphere__RenderAnimatedRecursive`. Fresh primary exports verified `8` metadata rows, `8` tag rows, `19` xref rows, `429` function-body instruction rows, `8` decompile rows, and `144` vtable-slot rows; context exports verified `20` metadata rows, `20` tag rows, `1087` xref rows, `1090` function-body instruction rows, and `20` decompile rows. Queue closure remains `6246/6246 = 100.00%`; expanded static surface progress is `993/1509 = 65.81%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260601-120449_post_wave1046_renderthing_crttree_review_verified`. Runtime tree/vegetation/falling-tree/render behavior, exact `CRTTree`/`CRTMesh`/resource/output-record layouts, exact source virtual names, BEA patching, gameplay outcomes, and rebuild parity remain separate proof.

| Address | Saved signature | Evidence |
| --- | --- | --- |
| `0x004dd7b0` | `void __thiscall CRTTree__Init(void * this, void * init)` | Initializes the render object, resolves a tree/resource pointer from `init+0x408`, stores pointers at `this+0x14/+0x18`, falls back to `DAT_0089c9c8`, bumps `+0x170`, and caches resource scalars. |
| `0x004dd850` | `void __fastcall CRTTree__VFuncSlot03_UpdateVisibilityState(void * this)` | Updates tree visibility/imposter state with `DAT_0083cd58` gating and helper dispatch through `this+0x18`. |
| `0x004dd960` | `void __thiscall CRTTree__VFuncSlot02_BuildRenderOutputs(void * this, void * renderContext)` | Builds render output state using camera/context transforms, resource/falling-tree state, `DAT_0083cd58`, matrix setup, and animated/render helper calls. |
| `0x004ddfd0` | `void __fastcall CRTTree__Destructor(void * this)` | Hides/unregisters the tree with `CDXTrees__HideTree`, decrements `this+0x14 -> +0x170`, clears `this+0x14`, restores the CRenderThing vtable, and destroys child pointer `this+0x10` when present. |
| `0x004de050` | `float __fastcall CRTTree__VFuncSlot06_GetResourceScalar164(void * this)` | Compact resource scalar getter from `*(this+0x14)+0x164`. |
| `0x004de060` | `void * __fastcall SharedVFunc__ReturnResourceField150_004de060(void * this)` | Shared CRTMesh/CRTTree getter returning `*(this+0x14)+0x150`. |
| `0x004de080` | `void * __thiscall CRTTree__ScalarDeletingDestructor(void * this, byte flags)` | Scalar-deleting destructor wrapper; calls `CRTTree__Destructor(this)`, frees on `flags & 1`, and returns `this`. |

CRTTree vtable slot 28 still points at non-code address `0x00616840` and remains deferred.

## Related Classes And Strings

| Item | Address | Notes |
| --- | --- | --- |
| `CTree` RTTI | `0x00630b98` | Main tree object class |
| `CTreeDetail` RTTI | `0x006313a8` | Tree detail/LOD system |
| `CTreeInitThing` RTTI | `0x0062d760` | Tree initialization helper |
| `CRTTree` RTTI | `0x006321b0` | Runtime tree render object |
| `CDXTrees` RTTI | `0x006529a0` | DirectX tree renderer, covered separately in `DXTrees.cpp` docs |
| `Tree Ground Hit Effect` | `0x00633aa0` | Particle effect string referenced by `CTree__UpdateFallingTree` |
| `DefaultTree0` | `0x0062d7a0` | Default tree type name |
| `Loading trees` | `0x0063d418` | Loading message |

## Claim Boundary

The Wave520 records are static saved-Ghidra metadata and instruction/decompile/vtable evidence. They are not runtime proof of tree knockdown behavior, ground collision response, particle spawning, or exact source layout parity. Treat offset names and field names as partial observed layout hints until broader runtime or source-correlated evidence closes them.
