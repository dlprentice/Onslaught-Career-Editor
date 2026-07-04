# Ghidra CUnit Tail Linked VFunc Review Wave1048

Status: complete read-only static review
Date: 2026-06-01
Scope: `cunit-tail-linked-vfunc-review-wave1048`

Wave1048 re-read six CUnit tail helpers spanning the attached-node forwarder trio and the slot 22/23/26 linked-target / recent-segment-damage helpers. Fresh metadata, tag, xref, instruction, decompile, and vtable-slot evidence matched the saved Ghidra state, so the wave made no mutation: no rename, signature change, comment/tag change, function-boundary change, executable-byte change, BEA launch, or runtime/game-file mutation occurred.

Reviewed rows:

| Address | Saved row | Fresh static evidence |
| --- | --- | --- |
| `0x004fce40 CUnit__ForwardAttachedNodeVFunc14IfPresent` | `int __thiscall CUnit__ForwardAttachedNodeVFunc14IfPresent(void * this, int node_arg0, int node_arg1, int node_arg2, int node_arg3)` | Loads attached-node/controller pointer at `this+0x208`, null-gates it, copies four explicit stack dwords into a call frame, dispatches attached-node vfunc `+0x14`, and ends with `RET 0x10`. |
| `0x004fce80 CUnit__ForwardAttachedNodeVFunc18IfPresent` | `int __thiscall CUnit__ForwardAttachedNodeVFunc18IfPresent(void * this, int node_arg0, int node_arg1, int node_arg2, int node_arg3)` | Same attached-node pattern; dispatches vfunc `+0x18` and has call xrefs from GillM/HUD/monitor/Warspite-side contexts including `0x0047a38a`, `0x0048a113`, `0x004ef404`, `0x004fecda`, and `0x004feda1`. |
| `0x004fcec0 CUnit__ForwardAttachedNodeVFunc1CIfPresent` | `int __thiscall CUnit__ForwardAttachedNodeVFunc1CIfPresent(void * this, int node_arg0, int node_arg1, int node_arg2, int node_arg3)` | Same attached-node pattern; dispatches vfunc `+0x1c`, with CUnitAI door-wing and CSquadNormal xrefs still supporting bounded CUnit ownership. |
| `0x004fd5e0 CUnit__VFunc26_GetRecentSegmentDamageMeter` | `int __thiscall CUnit__VFunc26_GetRecentSegmentDamageMeter(void * this, int segment_index)` | `RET 0x4` confirms one stack argument. Reads destructible-segment controller at `this+0x170`, calls `CDestructableSegmentsController__GetSegmentLastDamageTimeByIndex` and `CDestructableSegmentsController__GetSegmentLastDamageAmountByIndex`, dispatches adjusted `this-8` vfunc `+0x1ac`, and returns a clamped decaying `0..100` meter or `this+0x210` fallback. |
| `0x004fd6a0 CUnit__VFunc22_ActivateLinkedTargetsAndChildren` | `void __fastcall CUnit__VFunc22_ActivateLinkedTargetsAndChildren(void * this)` | If `this+0x214` is clear, sets it to `1`, dispatches linked target/reader at `this+0x148` through vfunc `+0x58`, then walks `this+0x19c` child/linked-reader chain and dispatches each non-null child through vfunc `+0x58`. |
| `0x004fd700 CUnit__VFunc23_DeactivateLinkedTargetsAndChildren` | `void __fastcall CUnit__VFunc23_DeactivateLinkedTargetsAndChildren(void * this)` | If `this+0x214` is set, clears it to `0`, dispatches linked target/reader at `this+0x148` through vfunc `+0x5c`, then walks `this+0x19c` child/linked-reader chain and dispatches each non-null child through vfunc `+0x5c`. |

Evidence counts:

- Primary exports: `6` metadata rows, `6` tag rows, `116` xref rows, `175` function-body instruction rows, and `6` decompile rows.
- Context exports: `10` metadata rows, `10` tag rows, `78` xref rows, `596` function-body instruction rows, and `10` decompile rows.
- Vtable export: `4` vtable anchors, `528` slot rows. Sample confirmations: `0x005d8d1c` slot `98` -> `0x004fd5e0`, slot `124` -> `0x004fd6a0`, slot `125` -> `0x004fd700`; `0x005e0b30`, `0x005e297c`, and `0x005e32d4` slots `22` and `23` point at the activation/deactivation helpers.
- Queue closure remains `6246/6246 = 100.00%`, with `0` commentless rows, `0` exact-undefined signatures, and `0` `param_N` signatures.
- Wave1048 newly direct-reviews four Wave911 focused rows beyond earlier context coverage, so Wave911 focused progress advances to `744/1408 = 52.84%`; expanded static surface progress advances to `1002/1509 = 66.40%`; top-500 risk-ranked coverage remains `500/500 = 100.00%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260601-131919_post_wave1048_cunit_tail_linked_vfunc_review_verified`, 19 files, 174590855 bytes, `DiffCount=0`, `HashDiffCount=0`.

What this proves:

- The six reviewed CUnit tail helpers still exist as saved Ghidra function objects in the loaded database.
- The saved names, signatures, comments, tags, xrefs, vtable slots, instruction bodies, and decompile exports remain internally coherent with the attached-node, linked-reader activation/deactivation, and recent segment-damage meter evidence.
- The review is static Ghidra evidence only, tied to serialized metadata/tags/xrefs/instructions/decompile/vtable exports and a verified project backup.

What remains separate proof:

- Runtime CUnit activation/deactivation behavior, linked-reader side effects, recent segment-damage meter behavior, and HUD/gameplay use.
- Exact `CUnit`, attached-node/controller, linked-reader, destructible-segment, and adjusted-subobject layouts beyond observed offsets.
- Exact source-body identity or final source method names for the vfunc-style helpers.
- BEA patching behavior, gameplay outcomes, and rebuild parity.

Probe token anchor: Wave1048; cunit-tail-linked-vfunc-review-wave1048; 0x004fce40 CUnit__ForwardAttachedNodeVFunc14IfPresent; 0x004fce80 CUnit__ForwardAttachedNodeVFunc18IfPresent; 0x004fcec0 CUnit__ForwardAttachedNodeVFunc1CIfPresent; 0x004fd5e0 CUnit__VFunc26_GetRecentSegmentDamageMeter; 0x004fd6a0 CUnit__VFunc22_ActivateLinkedTargetsAndChildren; 0x004fd700 CUnit__VFunc23_DeactivateLinkedTargetsAndChildren; CDestructableSegmentsController__GetSegmentLastDamageTimeByIndex; CDestructableSegmentsController__GetSegmentLastDamageAmountByIndex; 0x005d8d1c; 0x005e0b30; 0x005e297c; 0x005e32d4; 744/1408 = 52.84%; 1002/1509 = 66.40%; 500/500 = 100.00%; 6246/6246 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260601-131919_post_wave1048_cunit_tail_linked_vfunc_review_verified; no mutation.
