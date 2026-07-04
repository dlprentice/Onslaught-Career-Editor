# Wave1163 Texture Node-Tree / Inflate-Huffman Current-Risk Review Readiness Note

Status: complete static read-only evidence pending validation
Date: 2026-06-06
Scope: `wave1163-texture-node-tree-inflate-huffman-current-risk-review`

Wave1163 re-read `17 CFastVB/CTexture/CDXTexture current-risk rows` from the active `wave1108-current-risk-rank` current-risk denominator. Fresh Ghidra metadata, tag, xref, instruction, and decompile exports showed the saved names, signatures, comments, and tags remain coherent. No Ghidra mutation was performed.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x005987f4 CTexture__NodePayloadRecordCtor` | Hidden-ECX node-payload constructor from Wave703; installs the CDXTexture node-payload vtable and preserves the locked-storage ABI boundary. |
| `0x00598a81 CFastVB__NodeType9__ctor` | Hidden-ECX node-type 9 constructor from Wave704; sets kind/class field 8 and vtable `0x005ef250`. |
| `0x00598da4 CDXTexture__NodeType13__ctor` | Hidden-ECX node-type 13 constructor from Wave704; copies descriptor dwords and binds vtable `0x005ef270`. |
| `0x0059902a CDXTexture__RegisterSerializedChunk` | Serialized-chunk registry helper from Wave705; handles sentinel length, dedupe, copy/adopt flags, alignment, tail-link append, and optional output offset. |
| `0x00599b69 CFastVB__NodeTreeHasBitFlag0x200` | Recursive node-tree predicate over wrapper kinds 1/5/7/10 and leaf kind 8 payload flag mask. |
| `0x00599bd7 CFastVB__NodeTreeHasOnlyLeafType0to2` | Recursive node-tree predicate checking leaf kind/type range 0..2. |
| `0x00599c49 CFastVB__CountNodeTreeExpandedLeafCount` | Recursive expanded leaf-count helper over wrapper/repeat/leaf nodes. |
| `0x00599cd2 CFastVB__AreNodeTreesStructurallyEqual` | Structural node-tree comparator for nested wrappers and leaf field equality. |
| `0x0059a21f CFastVB__AreNodeTreesCompatible` | Compatibility helper with parser context in ECX, expanded non-leaf scratch records, relaxed leaf-type path, flattening, and structural fallback. |
| `0x0059a54d CFastVB__ScoreNodeTreeMatch` | Compatibility score helper for source/candidate payloads, binding-chain records, match flag filtering, and nested node-tree candidates. |
| `0x0059a71a CFastVB__SelectBestNodeTreeMatch` | Hidden-ABI selector called from CTexture and CDXTexture parser contexts; handles diagnostics and synthesized/reference node-type records. |
| `0x005958e0 CTexture__LoadDefaultHuffmanTables` | JPEG default Huffman-table loader; separate from zlib/inflate Huffman table builders. |
| `0x0059c8c1 CDXTexture__InflateStream_ProcessZlibState` | Zlib inflate stream state machine; Wave964 resolved the old `extraout_EAX` caveat at the block-header call. |
| `0x005bcfd3 CDXTexture__InflateCodesState_Process` | Inflate literal/length and distance code-state processor. |
| `0x005bd53b CDXTexture__BuildInflateHuffmanTable` | Zlib/inflate Huffman-table builder with hidden EAX/stack ABI boundary. |
| `0x005bd933 CDXTexture__InflateDynamicTree_BuildLitDistTrees` | Dynamic inflate literal/length and distance tree builder. |
| `0x005b3fd0 CDXTexture__FlushEntropyBitWriter` | JPEG entropy bit-writer flush helper; separate from inflate output-window flush behavior. |

Read-back evidence:

- Pre exports: `17` metadata rows, `17` tag rows, `68` xref rows, `2779` instruction rows, and `17` decompile rows.
- Xref mix: `68` `UNCONDITIONAL_CALL` rows.
- Static closure remains `6411/6411 = 100.00%` with static debt `0 / 0 / 0`.
- Expanded post-100 static surface remains `1560/1560 = 100.00%`.
- Wave1108 current focused accounting advances to `564/1179 = 47.84%`; remaining active focused work: `615`.
- Current risk candidates: `6166`; current focused candidates: `1178`; live regenerated current focused candidates: `1178`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260606-025611_post_wave1163_texture_node_tree_inflate_huffman_current_risk_review_verified`, `19` files, `175999879` bytes, `DiffCount=0`, `HashDiffCount=0`.

What this proves:

- The reviewed CFastVB, CTexture, and CDXTexture rows exist in the saved Ghidra project and have coherent names, signatures, comments, tags, xrefs, instructions, and decompile exports.
- The texture/resource/decode static map now ties serialized parser node payloads, node-tree compatibility/selection, JPEG default Huffman/entropy helpers, and zlib/inflate dynamic Huffman helpers into one current-risk read-back slice.
- No saved Ghidra correction was needed for this tranche.

What remains separate:

- Runtime parser behavior.
- Runtime texture decode behavior.
- Runtime JPEG behavior.
- Runtime inflate/decompression behavior.
- Exact node-tree, payload, chunk-builder, `z_stream`, inflate-state, Huffman-table, and entropy-writer layouts.
- Hidden ABI completeness.
- Exact source-body identity.
- BEA patching behavior.
- Visual QA.
- Gameplay outcomes.
- Rebuild parity.

Probe token anchor: Wave1163; wave1163-texture-node-tree-inflate-huffman-current-risk-review; 564/1179 = 47.84%; 17 CFastVB/CTexture/CDXTexture current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 615; current risk candidates: 6166; fresh Ghidra export; read-only review; no mutation; 0 / 0 / 0; 6411/6411 = 100.00%; 68 xref rows; 2779 instruction rows; CTexture__NodePayloadRecordCtor; CFastVB__NodeType9__ctor; CDXTexture__NodeType13__ctor; CDXTexture__RegisterSerializedChunk; CFastVB__AreNodeTreesCompatible; CFastVB__SelectBestNodeTreeMatch; CTexture__LoadDefaultHuffmanTables; CDXTexture__InflateStream_ProcessZlibState; CDXTexture__BuildInflateHuffmanTable; CDXTexture__FlushEntropyBitWriter; JPEG Huffman separate from inflate Huffman; [maintainer-local-ghidra-backup-root]\BEA_20260606-025611_post_wave1163_texture_node_tree_inflate_huffman_current_risk_review_verified; texture-resource-decode-static-contract.md; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.
