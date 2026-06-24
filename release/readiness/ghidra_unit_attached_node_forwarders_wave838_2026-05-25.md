# Ghidra Unit Attached Node Forwarders Wave838 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-25
Scope: `unit-attached-node-forwarders-wave838`

Wave838 Unit Attached Node Forwarders saved names, signatures, comments, and tags for three adjacent CUnit-tail attached-node/controller forwarding helpers:

| Address | Saved State | Static Evidence |
| --- | --- | --- |
| `0x004fce40 CUnit__ForwardAttachedNodeVFunc14IfPresent` | `int __thiscall CUnit__ForwardAttachedNodeVFunc14IfPresent(void * this, int node_arg0, int node_arg1, int node_arg2, int node_arg3)` | Corrects stale `CUnitAI__CallAttachedNodeVFunc14IfPresent`; loads `this+0x208`, null-gates it, forwards four stack dwords to attached-node vfunc `+0x14`, and returns with `RET 0x10` at `0x004fce71`. Xrefs include `0x0044610a CUnitAI__UpdateDoorWingEngagement_MidRange`. |
| `0x004fce80 CUnit__ForwardAttachedNodeVFunc18IfPresent` | `int __thiscall CUnit__ForwardAttachedNodeVFunc18IfPresent(void * this, int node_arg0, int node_arg1, int node_arg2, int node_arg3)` | Refines stale broad `CUnit__ForwardControllerQuery18`; same `this+0x208` attached-node pattern, vfunc `+0x18`, and `RET 0x10` at `0x004fceb1`. Static callers include `0x0047a38a`, `0x0048a113`, `0x004ef404`, `0x004fecda`, and `0x004feda1`. |
| `0x004fcec0 CUnit__ForwardAttachedNodeVFunc1CIfPresent` | `int __thiscall CUnit__ForwardAttachedNodeVFunc1CIfPresent(void * this, int node_arg0, int node_arg1, int node_arg2, int node_arg3)` | Corrects stale `CUnitAI__GetAttachedNodeReadyState`; same `this+0x208` attached-node pattern, vfunc `+0x1c`, and `RET 0x10` at `0x004fcef1`. Xrefs include `CSquadNormal__BuildAttackFormation` at `0x004e8ba9/0x004e8c06` and CUnitAI door-wing callers `0x00445db5/0x0044626e/0x00446472`. |

Read-back evidence:

- `ApplyUnitAttachedNodeForwardersWave838.java dry`: `updated=0 skipped=3 renamed=0 would_rename=3 signature_updated=3 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnitAttachedNodeForwardersWave838.java apply`: `updated=3 skipped=0 renamed=3 would_rename=0 signature_updated=3 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnitAttachedNodeForwardersWave838.java final dry`: `updated=0 skipped=3 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: `3` metadata rows, `3` tag rows, `19` xref rows, `171` target-window instruction rows, `483` deep target instruction rows, `855` xref-site instruction rows, `8` context metadata rows, `8` context decompile rows, and `3` target decompile rows.
- Queue after Wave838: `6098` total functions, `5662` commented, `436` commentless, `0` exact-undefined signatures, `0` `param_N`, comment-backed proxy `5662/6098 = 92.85%`, strict clean-signature proxy `5662/6098 = 92.85%`.
- Next raw commentless row: `0x004fde70 CWarspite__TransitionToUndeploying`; commentless high-signal, signature, and name-confidence queues remain empty.
- Verified backup: `G:\GhidraBackups\BEA_20260525-021158_post_wave838_unit_attached_node_forwarders_verified`, `19` files, `171838343` bytes, `DiffCount=0`.

What this proves:

- The three target rows exist in the saved Ghidra project.
- Saved names place the shared attached-node forwarders under `CUnit`, with explicit stale-name correction anchors.
- Saved signatures reflect one ECX receiver and four explicit stack dword arguments, consistent with `RET 0x10`.
- Saved comments and tags include `unit-attached-node-forwarders-wave838` and `wave838-readback-verified`.
- Static instruction, xref, and decompile exports show the common `this+0x208` attached-node pointer, null gate, four-dword forwarding frame, and vfunc slot dispatches `+0x14`, `+0x18`, and `+0x1c`.

What remains unproven:

- Exact attached-node/controller concrete type.
- Exact argument layout beyond the four observed dword stack slots.
- Return-value semantics on the null path and callee path.
- Runtime behavior.
- BEA patching behavior.
- Rebuild parity.
