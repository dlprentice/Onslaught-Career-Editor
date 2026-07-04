# Ghidra Missile Linked-Object Dispatch Review Wave941 Readiness

Status: complete read-only static review
Date: 2026-05-28
Scope: `missile-linked-object-dispatch-review-wave941`

Wave941 re-reviewed the missile linked-object dispatch chain selected from the Wave911 risk-ranked continuation queue after Composer 2.5 consults and fresh serialized Ghidra exports. The cluster ties `CMissile__Init`, `CMissile__DispatchLinkedObjectVFunc68AndPostHook`, the CMissile scalar-deleting destructor/body pair, the CRound base projectile context, the resource descriptor/PCRTID creation path, and the related CMissile/CRound vtable anchors.

The fresh evidence found no Ghidra rename, signature, comment, function-boundary, or tag correction strong enough to justify a mutation. No executable bytes were changed.

Primary targets:

| Address | Saved row | Read-back evidence |
| --- | --- | --- |
| `0x004baae0` | `CMissile__Init` | Reads optional resource path pointer at `this+0xf0+0x0c`, allocates `0x428` bytes with OID type `0x61` and Missile.cpp debug path evidence, constructs a `CResourceDescriptor`, calls `PCRTID__CreateObject`, stores the linked object at `this+0x30`, calls linked-object vfunc `+4`, frees the temporary descriptor, then calls `CRound__Init`. |
| `0x004bac10` | `CMissile__DispatchLinkedObjectVFunc68AndPostHook` | Vtable DATA xref `0x005e3cc0`; instruction read-back loads `this+0x30`, dispatches linked-object vfunc `+0x68` with two stack arguments, calls `0x00452da0 SharedVFunc__NoOp_Ret08` with `ECX=this`, and returns with `RET 0x8`. |
| `0x0050f8b0` | `CMissile__scalar_deleting_dtor` | CMissile vtable slot at `0x005e3ba8`; calls `0x0050f8d0 CMissile__Destructor`, conditionally frees `this` when delete flag bit 0 is set, returns `this`, and ends with `RET 0x4`. |
| `0x0050f8d0` | `CMissile__Destructor` | Removes linked set cells at `this+0xec` and `this+0xe8`, removes the `this+0xe0` particle/global-list node, then calls `CActor__dtor_base`. |

Context anchors:

- `0x0050f7a0 CWorldPhysicsManager__CreateProjectile` preserves the projectile factory branch that allocates a `0x134` CRound object and selects the missile-style vtable path when `round_definition+0x70` is nonzero.
- `0x00403f40 CResourceDescriptor__ctor`, `0x00403f80 CResourceDescriptor__dtor`, and `0x00516580 PCRTID__CreateObject` preserve the descriptor-backed linked-object creation path used by `CMissile__Init`.
- `0x004d8410 CRound__Init`, `0x004d8dc0 VFuncSlot_02_004d8dc0`, `0x004d9ef0 CRound__UpdateRoundAndTriggerLaunchEffect`, and `0x004db630 CRound__ArmProjectileAndSpawnTrailEffect` preserve the CRound base and launch context previously re-reviewed in Wave920.
- `0x00452da0 SharedVFunc__NoOp_Ret08` remains a broad shared post-hook target, not a missile-specific source virtual method.
- Vtable anchors `0x005e3ba4`, `0x005e3ba8`, `0x005e3bc8`, `0x005e3cb8`, `0x005e3cc0`, and `0x005de82c` keep the missile-style table, destructor table, init table, launch table, dispatch table, and CRound base table connected. `0x005de850 -> 0x004d8410` is the CRound init slot-9 DATA xref; it is proven by the xref export rather than by the eight-slot vtable slice.

Fresh read-back evidence:

- Primary exports: 4 metadata rows, 4 tag rows, 4 xref rows, 168 instruction rows, and 4 decompile rows.
- Context exports: 12 metadata rows, 12 tag rows, 103 xref rows, 931 instruction rows, and 12 decompile rows.
- Vtable export: 48 rows across `0x005e3ba4`, `0x005e3ba8`, `0x005e3bc8`, `0x005e3cb8`, `0x005e3cc0`, and `0x005de82c`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260528-034712_post_wave941_missile_linked_object_dispatch_review_verified`, 19 files, 173247367 bytes, `DiffCount=0`.
- Mutation status: read-only review; no dry/apply/final-dry mutation scripts were run because the saved rows already matched the bounded static evidence.

Progress:

- Wave911 focused re-audit progress after Wave941: `179/1408 = 12.71%`.
- Static export-contract function-quality closure remains `6113/6113 = 100.00%`.

Probe token anchor: Wave941; `missile-linked-object-dispatch-review-wave941`; `0x004baae0 CMissile__Init`; `0x004bac10 CMissile__DispatchLinkedObjectVFunc68AndPostHook`; `0x0050f8b0 CMissile__scalar_deleting_dtor`; `0x0050f8d0 CMissile__Destructor`; `0x0050f7a0 CWorldPhysicsManager__CreateProjectile`; `0x004d8410 CRound__Init`; `0x00452da0 SharedVFunc__NoOp_Ret08`; `0x005e3ba4`; `0x005e3ba8`; `0x005e3bc8`; `0x005e3cb8`; `0x005e3cc0`; `0x005de82c`; `0x005de850`; read-only review; `179/1408 = 12.71%`; `6113/6113 = 100.00%`; `[maintainer-local-ghidra-backup-root]\BEA_20260528-034712_post_wave941_missile_linked_object_dispatch_review_verified`.

What this proves:

- The selected missile linked-object dispatch rows remain present in the saved Ghidra project with coherent names, signatures, xrefs, instructions, vtable anchors, and decompile outputs.
- The old neutral `VTable_005e3cc0__Slot00_Dispatch68_AndPostHook` wording is superseded by the saved/live `CMissile__DispatchLinkedObjectVFunc68AndPostHook` row.
- The CMissile init, dispatch, and teardown chain is statically coherent with the CRound/resource-descriptor/PCRTID context.

What remains unproven:

- Runtime missile payload behavior.
- Exact `+0x68` linked-object source virtual name.
- Concrete CMissile, CRound, descriptor, linked-object, active-reader, and effect layouts.
- Runtime projectile/guidance/trail behavior.
- BEA patching behavior.
- Rebuild parity.
