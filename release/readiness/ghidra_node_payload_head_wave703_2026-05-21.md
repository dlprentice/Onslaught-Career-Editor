# Ghidra Node Payload Head Wave703 Readiness

Status: validated
Date: 2026-05-21
Scope: saved Ghidra metadata only; no executable bytes, function boundaries, original game files, copied profiles, runtime proof, or public asset payloads changed.

## What Changed

Wave703 node payload head saved signatures, parameter names, comments, and tags for twelve adjacent CTexture/CDXTexture/CFastVB node-payload helpers at the head of the current queue.

Probe anchors: `0x00598702 CTexture__NodePayloadBaseCtor`, `0x005988f5 CFastVB__CompareNodeValuesByTagAndPayload`, and next queue head `0x005989c3 CTexture__NodeType8_InitDefaults`.

| Address | Saved signature | Static evidence |
| --- | --- | --- |
| `0x00598702` | `void __thiscall CTexture__NodePayloadBaseCtor(void * this, int format_class_id_or_kind)` | Initializes the node-payload header, clears child and sibling links, installs the base release-node vtable, stores the format class/kind field, and ends with `RET 0x4`. |
| `0x0059871c` | `void __fastcall CDXTexture__ReleaseNodePayloadChain(void * node_payload)` | Resets to the base release vtable, releases the child chain through vslot 0 with delete flag 1, and drains sibling links at `+0xc`. |
| `0x00598749` | `bool __thiscall CTexture__HasSameFormatClassId(void * this, void * candidate_node)` | Returns false for a null candidate and otherwise compares `candidate_node+0x4` to `this+0x4`. |
| `0x0059877e` | `void CTexture__NodePayloadNoOp(void)` | Single-RET no-op used as a node-payload/vtable slot and parser cleanup helper; comment/tag-only because Ghidra reports locked storage. |
| `0x0059877f` | `uint __stdcall CTexture__NodePayloadMatchesTypeOrNullIsZero(void * node_or_null, int expected_type)` | Returns `expected_type == 0` for null nodes, otherwise dispatches node vslot `+0x4`. |
| `0x0059879e` | `int __stdcall CDXTexture__InvokeNodeScoreOrZero(void * node_or_null)` | Returns zero for null nodes, otherwise dispatches node vslot `+0x8`. |
| `0x005987b2` | `void * __stdcall CTexture__AppendNodeAtTail_Link0c(void * chain_head, void * node_to_append)` | Appends at the first null `+0xc` link and returns the resulting chain head. |
| `0x005987d9` | `void __fastcall CDXTexture__NodePayload__ctor(void * node_payload)` | Initializes a 0x14-byte kind-1 payload with null child/sibling links, the CDXTexture node-payload vtable, and zeroed `+0x10`. |
| `0x005987f4` | `int CTexture__NodePayloadRecordCtor(void)` | Hidden-ECX constructor stores three stack values into `+0x8/+0xc/+0x10`, installs the CDXTexture node-payload vtable, and ends with `RET 0xc`; comment/tag-only because Ghidra reports locked storage. |
| `0x0059881b` | `int __thiscall CTexture__IsFormatChainCompatible(void * this, void * candidate_chain)` | Checks format class, then walks `+0xc` node links and validates kind-1 child chains or non-kind payloads through the matcher helper. |
| `0x00598873` | `void * __fastcall CFastVB__CloneNodeChainWithAddRef(void * source_chain)` | Clones kind-1 wrapper nodes, copies `+0x10`, clones children through vslot `+0x8`, rolls back failed child clones, and links cloned siblings. |
| `0x005988f5` | `int __fastcall CFastVB__CompareNodeValuesByTagAndPayload(void * left_payload)` | Compares the ECX-held left payload with a hidden EAX-held right payload by tag, including scalar/pointer, inline-string, indirect-string, and double-like cases. |

Tag anchor: `ctexture-node-payload-head-wave703`; read-back tag: `wave703-readback-verified`.

## Evidence

- Pre-export found all `12` targets: `12` metadata rows, `12` tag rows, `60` xref rows, `444` instruction rows, and `12` decompile rows.
- `ApplyNodePayloadHeadWave703.java` dry run: `updated=0 skipped=12 renamed=0 would_rename=0 signature_updated=10 comment_only_updated=2 missing=0 bad=0`.
- Apply run: `updated=12 skipped=0 renamed=0 would_rename=0 signature_updated=10 comment_only_updated=2 missing=0 bad=0`.
- Final dry run: `updated=0 skipped=12 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`.
- Post-export verified all `12` saved signatures/tags/comments with `60` xref rows, `444` instruction rows, and `12` clean decompile rows.
- Queue refresh after Wave703: `6098` total functions, `4068` commented, `2030` commentless, `1216` exact-undefined signatures, `260` `param_N` signatures, comment-backed proxy `4068/6098 = 66.71%`, strict clean-signature proxy `4014/6098 = 65.82%`.
- Next queue head: `0x005989c3 CTexture__NodeType8_InitDefaults`.
- Verified Ghidra backup: `[maintainer-local-ghidra-backup-root]\BEA_20260521-182413_post_wave703_node_payload_head_verified`, `19` files, `165317511` bytes, `DiffCount=0`.

## Boundaries

This wave proves saved static retail Ghidra metadata only. Exact node-payload struct layout, payload type enum, vtable contract, hidden-register comparator ABI, AddRef semantics, parser reduction behavior, runtime texture behavior, runtime vertex-buffer behavior, BEA patching, and rebuild parity remain unproven.

The installed Steam game and original `BEA.exe` were not modified.
