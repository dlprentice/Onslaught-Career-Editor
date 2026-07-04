# Ghidra Node-Type Lifecycle Wave706 Readiness

Status: passed
Date: 2026-05-21

Wave706 node-type lifecycle saved nine adjacent CFastVB/CTexture node-type `0x11` and `0x12` lifecycle rows with the `node-type-lifecycle-wave706` and `wave706-readback-verified` tags.

## Targets

| Address | Saved signature | Static evidence |
| --- | --- | --- |
| `0x005997a5` | `void * __fastcall CFastVB__InitNodeType17(void * node_type17)` | Initializes node-type `0x11`, zeroes descriptor/resource slots, binds vtable `0x005ef374`, and returns the initialized pointer. |
| `0x005997e1` | `int CTexture__NodeType12_Ctor_DeleteOnFlag(void)` | Hidden-ECX node-type `0x11` constructor copies descriptor/scalar stack inputs and clears owned slots; comment/tag-only for locked storage. |
| `0x00599831` | `void __fastcall CTexture__NodeType12_Dtor_DeleteOnFlag_Body(void * node_type17)` | Releases optional owned slots at `+0x3c/+0x40/+0x44..+0x50` and then releases the base node-payload chain. |
| `0x00599878` | `void * __fastcall CFastVB__CloneNodeTreeWithAddRef(void * source_node_type17)` | Allocates and initializes a node-type `0x11` clone, copies descriptor fields, clones/add-refs optional child resources, and destroys a partial clone on failure. |
| `0x0059993c` | `void * __fastcall CTexture__NodeType12_Ctor(void * node_type12)` | Initializes node-type `0x12`, binds vtable `0x005ef384`, and seeds defaults `0xf0000` and `0xe40000`. |
| `0x0059996f` | `int CTexture__NodeType12_Ctor_ScalarDeletingDtor(void)` | Hidden-ECX node-type `0x12` constructor copies five stack scalars and seeds the same defaults; comment/tag-only for locked storage. |
| `0x005999b5` | `void __fastcall CTexture__NodeType12_ScalarDeletingDtor_Body(void * node_type12)` | Releases the optional owned pointer at `+0x28` and then releases the base node-payload chain. |
| `0x00599a3c` | `void * __thiscall CTexture__NodeType12_Dtor_DeleteOnFlag(void * this, uint delete_flags)` | Scalar-deleting wrapper for the node-type `0x11` destructor body; `RET 0x4` evidence removed an unused phantom parameter. |
| `0x00599a58` | `void * __thiscall CTexture__NodeType12_ScalarDeletingDtor(void * this, uint delete_flags)` | Scalar-deleting wrapper for the node-type `0x12` destructor body; `RET 0x4` evidence removed an unused phantom parameter. |

## Evidence

- Accepted dry/apply/final dry:
  - `updated=0 skipped=9 renamed=0 would_rename=0 signature_updated=7 comment_only_updated=2 missing=0 bad=0`
  - `updated=9 skipped=0 renamed=0 would_rename=0 signature_updated=7 comment_only_updated=2 missing=0 bad=0`
  - `updated=0 skipped=9 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports verified `9` metadata rows, `9` tag rows, `12` xref rows, `801` instruction rows, and `9` clean decompile rows.
- Queue after Wave706: `6098` total, `4104` commented, `1994` commentless, `1216` exact-undefined signatures, `231` `param_N`, comment-backed proxy `4104/6098 = 67.30%`, strict clean-signature proxy `4050/6098 = 66.42%`.
- Raw commentless head remains `0x0042f220 CSPtrSet__Clear`.
- High-signal head moved to `0x00599a74 CFastVB__SelectBestNodeTreeMatch_ReportWarningAndSetFlag`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260521-201902_post_wave706_node_type_lifecycle_verified`, `19` files, `165448583` bytes, `DiffCount=0`.

## Boundaries

This is static Ghidra metadata/read-back evidence only. Exact node-type enum meanings, concrete field schema, hidden constructor ABI, child-resource ownership, reference-count semantics, runtime texture behavior, runtime vertex-buffer behavior, BEA patching, parser/source identity, and rebuild parity remain unproven.

Probe anchors: `Wave706 node-type lifecycle`, `node-type-lifecycle-wave706`, `0x005997a5 CFastVB__InitNodeType17`, `0x00599a58 CTexture__NodeType12_ScalarDeletingDtor`, `0x0042f220 CSPtrSet__Clear`, `0x00599a74 CFastVB__SelectBestNodeTreeMatch_ReportWarningAndSetFlag`.
