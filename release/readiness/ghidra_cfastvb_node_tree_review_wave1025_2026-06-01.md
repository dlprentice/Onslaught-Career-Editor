# Ghidra CFastVB Node-Tree Review Wave1025 Readiness Note

Status: complete read-only static review
Date: 2026-06-01
Scope: `cfastvb-node-tree-review-wave1025`

Wave1025 re-read thirteen CFastVB/CDXTexture/CTexture node-tree, serialized-chunk, shader-parser selector, and strip-selection residual rows from the Wave911 top-500 tail. The review made no mutation: no Ghidra mutation, no rename, no signature change, no comment/tag change, no function-boundary change, and no executable-byte change.

Primary targets:

| Address | Saved state | Fresh evidence |
| --- | --- | --- |
| `0x0056ff40 CFastVB__TriangleListContainsVertexTriplet_0056ff40` | `uint __stdcall CFastVB__TriangleListContainsVertexTriplet_0056ff40(void * triangle_list_span, void * triangle)` | RET `0x8`; called by `0x00570000 CFastVB__BuildTriangleStripFromSeedRecord`; preserved as the Wave651 strip-selection predicate. |
| `0x00570be0 CFastVB__InitializeCandidateParentLinks_00570be0` | `void __stdcall CFastVB__InitializeCandidateParentLinks_00570be0(void * out_candidate_span, void * selected_candidate_bucket)` | RET `0x8`; called by `0x005725e0 CFastVB__GenerateStripCandidatesFromAdjacency`; preserved as the Wave651 parent-link initializer. |
| `0x00598a81 CFastVB__NodeType9__ctor` | `int CFastVB__NodeType9__ctor(void)` | Hidden-ECX/locked-storage constructor; body returns with RET `0x14`; four selector callsites synthesize node-type 9 records. |
| `0x00598da4 CDXTexture__NodeType13__ctor` | `int CDXTexture__NodeType13__ctor(void)` | Hidden-ECX/locked-storage constructor; body returns with RET `0xc`; selector path calls it before node-type 13 ref-bump context. |
| `0x0059902a CDXTexture__RegisterSerializedChunk` | `int CDXTexture__RegisterSerializedChunk(void)` | Hidden-ECX/locked-storage serialized-chunk registry helper with broad texture parser/serializer call fan-in; signature intentionally remains bounded. |
| `0x005997e1 CTexture__NodeType12_Ctor_DeleteOnFlag` | `int CTexture__NodeType12_Ctor_DeleteOnFlag(void)` | Hidden-ECX/locked-storage constructor-like node payload helper; passes kind `0x11` to the base constructor, so the existing name is treated as historical retail naming drift, not proof of an exact source type name. |
| `0x0059996f CTexture__NodeType12_Ctor_ScalarDeletingDtor` | `int CTexture__NodeType12_Ctor_ScalarDeletingDtor(void)` | Hidden-ECX/locked-storage constructor-like helper; returns with RET `0x14` and seeds fixed scalar defaults at `+0x20` and `+0x24`. |
| `0x00599b69 CFastVB__NodeTreeHasBitFlag0x200` | `uint __thiscall CFastVB__NodeTreeHasBitFlag0x200(void * this, void * node_tree)` | Recursive node-tree predicate; RET `0x4`; keeps Wave708 phantom-parameter removal coherent. |
| `0x00599bd7 CFastVB__NodeTreeHasOnlyLeafType0to2` | `int __thiscall CFastVB__NodeTreeHasOnlyLeafType0to2(void * this, void * node_tree)` | Recursive node-tree leaf-type predicate; RET `0x4`; unknown paths dispatch parser diagnostics. |
| `0x00599c49 CFastVB__CountNodeTreeExpandedLeafCount` | `int __thiscall CFastVB__CountNodeTreeExpandedLeafCount(void * this, void * node_tree)` | Recursive expanded-leaf counter; RET `0x4`; counts wrapper/leaf kinds under parser context in ECX. |
| `0x00599d80 CFastVB__FlattenNodeTreeLeafByLinearIndex` | `int __thiscall CFastVB__FlattenNodeTreeLeafByLinearIndex(void * this, void * node_tree, uint linear_leaf_index, void * out_leaf_scratch)` | RET `0xc`; caller and body evidence still support ECX parser context plus three stack args. |
| `0x0059a54d CFastVB__ScoreNodeTreeMatch` | `int __thiscall CFastVB__ScoreNodeTreeMatch(void * this, void * source_payload, void * candidate_payload, void * candidate_binding_chain, int match_flags)` | RET `0x10`; matches Wave709 source/candidate payload score helper with parser context in ECX and four stack args. |
| `0x0059a71a CFastVB__SelectBestNodeTreeMatch` | `int CFastVB__SelectBestNodeTreeMatch(void)` | Hidden-ECX/stack ABI selector hub; call windows at `0x00599349` and `0x00599576` show ECX plus eight pushes before CALL, and the body ends in RET `0x20`. Current signature remains intentionally bounded because Ghidra reports locked storage. |

Comparison and context evidence:

- Comparison exports covered adjacent node payload constructors/destructors, diagnostics, structural equality, leaf-format resolution, binding-chain comparison, pair mismatch scoring, compatibility testing, and CFastVB strip-builder helpers: `0x00598702`, `0x0059871c`, `0x00598a56`, `0x00598abd`, `0x00598d6b`, `0x00598ddc`, `0x005997a5`, `0x0059993c`, `0x00599a74`, `0x00599ac8`, `0x00599b13`, `0x00599cd2`, `0x00599e48`, `0x00599ffd`, `0x0059a10a`, `0x0059a21f`, `0x00570000`, `0x005708a0`, and `0x00570a90`.
- Context exports covered the primary call parents and parser/chunk/decode context rows: `0x00570000`, `0x005725e0`, `0x0058ecdb`, `0x0058eefb`, `0x0059930d`, `0x005994c4`, `0x0059a10a`, `0x0059a21f`, and `0x005ab14b`.
- Instruction-window exports covered the `0x0059a71a` callsites at `0x00599349 CTexture__ValidateConstantRegisterDeclarationType` and `0x00599576 CDXTexture__ProcessTextureChunkAndEmitBindings`, plus the `0x0059a71a` entry. They confirm ECX setup plus eight stack pushes before the selector calls.

Evidence counts:

- Primary exports: 13 metadata rows, 13 tag rows, 53 xref rows, 1475 body-instruction rows, and 13 decompile rows.
- Comparison exports: 19 metadata rows, 19 tag rows, 53 xref rows, 1928 body-instruction rows, and 19 decompile rows.
- Context exports: 9 metadata rows, 9 tag rows, 14 xref rows, 2728 body-instruction rows, and 9 decompile rows.
- Instruction-window export: 159 instruction rows.
- Queue closure remains `6238/6238 = 100.00%` with 0 commentless, 0 exact-undefined signatures, and 0 `param_N`.
- Wave911 focused re-audit progress after Wave1025: `576/1408 = 40.91%`; expanded static surface progress: `805/1493 = 53.92%`; Wave911 top-500 risk-ranked coverage: `500/500 = 100.00%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260601-004522_post_wave1025_cfastvb_node_tree_review_verified`, 19 files, 173968263 bytes, `DiffCount=0`, `HashDiffCount=0`.

What this proves:

- The saved names, signatures, comments, tags, xrefs, instruction bodies, and decompiles for the thirteen selected residual rows remain internally coherent with the earlier Wave651, Wave704-Wave709, and Wave895 evidence.
- The CFastVB/CDXTexture/CTexture parser node-tree selector island is statically coherent at the reviewed call graph level: constant-register validation and texture-chunk binding emission call the selector, which in turn reaches score, compatibility, constructor-like, diagnostic, and binding-chain helpers.
- `0x0059a71a CFastVB__SelectBestNodeTreeMatch` remains a high-value hidden-ABI hub, but the current static evidence supports preserving the intentionally bounded Ghidra signature rather than forcing a speculative C++ prototype.

What remains unproven:

- Exact source-body identity or exact source type names.
- Exact node-tree, payload, binding-chain, serialized-chunk, parser, or texture layouts beyond observed address-qualified offsets and call/RET evidence.
- Runtime shader/parser/texture behavior.
- Runtime render output.
- BEA patch behavior, gameplay outcomes, and rebuild parity.
