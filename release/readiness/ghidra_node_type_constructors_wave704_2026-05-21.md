# Ghidra Node-Type Constructors Wave704 Readiness

Status: validated
Date: 2026-05-21
Scope: saved Ghidra metadata only; no executable bytes, function boundaries, original game files, copied profiles, runtime proof, or public asset payloads changed.

## What Changed

Wave704 node-type constructors/destructors saved signatures, parameter names, comments, and tags for twenty adjacent CTexture/CDXTexture/CFastVB node-type constructors, destructors, scalar-deleting wrappers, comparators, and owned-list helpers.

Probe anchors: `0x005989c3 CTexture__NodeType8_InitDefaults`, `0x00598ff4 CTexture__FreeOwnedNodeListAndPayloads`, raw commentless head `0x0042f220 CSPtrSet__Clear`, and high-signal head `0x00599161 CTexture__ComputeDebugChunkDwordCount`.

| Address | Saved signature | Static evidence |
| --- | --- | --- |
| `0x005989c3` | `void __fastcall CTexture__NodeType8_InitDefaults(void * node_type8)` | Initializes a node-type-8 payload, clears child/sibling links, sets kind/class field `+0x4` to `2`, and binds vtable `0x005ef240`. |
| `0x005989db` | `void __thiscall CTexture__NodeType8_InitFromDescriptor(void * this, void * descriptor_words32)` | Reuses the node-type-8 setup, copies eight descriptor dwords into storage at `+0x10`, and returns through `RET 0x4`. |
| `0x00598a56` | `void __fastcall CFastVB__InitNodeType9(void * node_type9)` | Initializes a node-type-9 payload with kind/class field `8`, vtable `0x005ef250`, null links, zeroed payload fields, and default tag/value field `+0x14 = 9`. |
| `0x00598a81` | `int CFastVB__NodeType9__ctor(void)` | Hidden-ECX constructor copies five stack values into `+0x10..+0x20`; comment/tag-only because Ghidra reports locked storage. |
| `0x00598abd` | `void __fastcall CFastVB__NodeType9__dtor(void * node_type9)` | Restores node-type-9 vtable `0x005ef250` and releases the child/sibling chain through `CDXTexture__ReleaseNodePayloadChain`. |
| `0x00598b48` | `void __fastcall CFastVB__InitNodeType10(void * node_type10)` | Initializes node-type-10 storage with kind/class field `10`, vtable `0x005ef260`, null links, and zeroed owned/resource slots through `+0x38`. |
| `0x00598b81` | `void __fastcall CFastVB__NodeType10_dtor(void * node_type10)` | Releases owned/interface pointers at `+0x20/+0x24/+0x28/+0x2c/+0x30`, frees `+0x38`, then releases the base payload chain. |
| `0x00598d6b` | `void * __fastcall CFastVB__InitNodeType13(void * node_type13)` | Initializes node-type-13 storage with kind/class field `0xd`, vtable `0x005ef270`, zeroed slots through `+0x3c`, and `+0x10 = 3`. |
| `0x00598da4` | `int CDXTexture__NodeType13__ctor(void)` | Hidden-ECX node-type-13 constructor copies stack scalar fields and eight descriptor dwords into `+0x20`; comment/tag-only for locked storage. |
| `0x00598ddc` | `int CDXTexture__NodeType13__ctorWithRefBump(void)` | Hidden-ECX node-type-13 constructor stores a stack-provided referenced object at `+0x18`, copies descriptor dwords, and calls referenced vslot `+4` when non-null. |
| `0x00598e22` | `void __fastcall CTexture__Dtor_ReleaseNodePayloadByKind(void * node_payload)` | Restores vtable `0x005ef270`, releases optional `+0x18` state based on `+0x10`, then releases the base payload chain. |
| `0x00598e5d` | `int __thiscall CDXTexture__CompareNodePayloadWithOptionalChild(void * this, void * candidate_payload)` | Compares format/class id, four dwords at `+0x10`, and an optional type-4 child/payload field. |
| `0x00598f22` | `void * __thiscall CDXTexture__Dtor_ReleaseNodePayload_DeleteOnFlag(void * this, uint delete_flags)` | Releases a node-payload chain, frees `this` when delete bit 0 is set, returns `this`, and ends with `RET 0x4`. |
| `0x00598f3e` | `void * __thiscall CDXTexture__Dtor_NodePayload_DeleteOnFlag(void * this, uint delete_flags)` | Resets vtable `0x005ef230`, releases the payload chain, and frees on delete bit 0. |
| `0x00598f60` | `void * __thiscall CFastVB__NodeType8_scalar_deleting_dtor(void * this, uint delete_flags)` | Scalar-deleting wrapper for node-type 8; resets vtable `0x005ef240`, releases the chain, and frees on delete bit 0. |
| `0x00598f82` | `void * __thiscall CFastVB__NodeType9_scalar_deleting_dtor(void * this, uint delete_flags)` | Scalar-deleting wrapper for node-type 9; resets vtable `0x005ef250`, releases the chain, and frees on delete bit 0. |
| `0x00598fa4` | `void * __thiscall CFastVB__NodeType10_scalar_deleting_dtor(void * this, uint delete_flags)` | Calls the node-type-10 destructor body, frees on delete bit 0, and returns `this`. |
| `0x00598fc0` | `void * __thiscall CTexture__Dtor_ReleaseNodePayload_DeleteOnFlag(void * this, uint delete_flags)` | Calls the kind-dispatch destructor body, frees on delete bit 0, and returns `this`. |
| `0x00598fdc` | `void __thiscall CTexture__InitOwnedNodeList(void * this, void * owner_context)` | Initializes an owned-node-list header, stores owner context, clears head state, and points the tail link at the head slot. |
| `0x00598ff4` | `void __fastcall CTexture__FreeOwnedNodeListAndPayloads(void * owned_node_list)` | Drains an owned-node list, conditionally frees payloads based on observed node flags, and frees each node record. |

Tag anchor: `node-type-constructors-wave704`; read-back tag: `wave704-readback-verified`.

## Evidence

- Pre-export found all `20` targets: `20` metadata rows, `20` tag rows, `45` xref rows, `2420` instruction rows, and `20` decompile rows.
- `ApplyNodeTypeConstructorsWave704.java` dry run: `updated=0 skipped=20 renamed=0 would_rename=0 signature_updated=17 comment_only_updated=3 missing=0 bad=0`.
- Apply run: `updated=20 skipped=0 renamed=0 would_rename=0 signature_updated=17 comment_only_updated=3 missing=0 bad=0`.
- Final dry run: `updated=0 skipped=20 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`.
- A comment precision fix for `0x00598ddc` then ran dry/apply/final-dry: `updated=0 skipped=20 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=1 missing=0 bad=0`, `updated=1 skipped=19 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=1 missing=0 bad=0`, and `updated=0 skipped=20 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`.
- Post-export verified all `20` saved signatures/tags/comments with `45` xref rows, `2420` instruction rows, and `20` clean decompile rows.
- Queue refresh after Wave704: `6098` total functions, `4088` commented, `2010` commentless, `1216` exact-undefined signatures, `243` `param_N` signatures, comment-backed proxy `4088/6098 = 67.04%`, strict clean-signature proxy `4034/6098 = 66.15%`.
- Earliest raw commentless row: `0x0042f220 CSPtrSet__Clear`.
- Next commentless high-signal row: `0x00599161 CTexture__ComputeDebugChunkDwordCount`.
- Verified Ghidra backup: `G:\GhidraBackups\BEA_20260521-185425_post_wave704_node_type_constructors_verified`, `19` files, `165415815` bytes, `DiffCount=0`.

## Boundaries

This wave proves saved static retail Ghidra metadata only. Exact node-type enum values, concrete node/owned-list/descriptor layouts, hidden calling-convention ABI, reference-count semantics, parser/source identity, runtime texture behavior, runtime vertex-buffer behavior, BEA patching, and rebuild parity remain unproven.

The installed Steam game and original `BEA.exe` were not modified.
