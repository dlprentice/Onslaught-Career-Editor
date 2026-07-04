# Wave1163 Texture Node-Tree / Inflate-Huffman Current-Risk Review

Status: complete static read-only evidence pending validation
Date: 2026-06-06
Tag: `wave1163-texture-node-tree-inflate-huffman-current-risk-review`

Wave1163 re-read `17 CFastVB/CTexture/CDXTexture current-risk rows` from the active `wave1108-current-risk-rank` current-risk denominator with fresh Ghidra metadata, tag, xref, instruction, and decompile exports. The pass is read-only: no Ghidra mutation, no rename, no signature change, no comment/tag change, no function-boundary change, no executable-byte change, no BEA launch, no installed-game mutation, no save mutation, and no runtime-file mutation.

This wave is a current-risk continuation of the Wave904 texture/resource/decode/render core, Wave964 inflate re-audit, Wave1025 node-tree review, and older Wave700/Wave703-Wave709/Wave733/Wave738/Wave895/Wave899 decode-tail rows.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x005987f4 CTexture__NodePayloadRecordCtor` | Hidden-ECX node-payload constructor storing stack fields, setting kind/class field `1`, and installing the CDXTexture node-payload vtable. |
| `0x00598a81 CFastVB__NodeType9__ctor` | Hidden-ECX node-type 9 constructor, kind/class field `8`, vtable `0x005ef250`. |
| `0x00598da4 CDXTexture__NodeType13__ctor` | Hidden-ECX node-type 13 constructor, kind/class field `0xd`, vtable `0x005ef270`, descriptor-copy storage. |
| `0x0059902a CDXTexture__RegisterSerializedChunk` | Serialized-chunk registry helper with dedupe/copy/adopt/alignment/tail-link behavior. |
| `0x00599b69 CFastVB__NodeTreeHasBitFlag0x200` | Recursive predicate for payload bit `0x200`. |
| `0x00599bd7 CFastVB__NodeTreeHasOnlyLeafType0to2` | Recursive predicate for leaf type range `0..2`. |
| `0x00599c49 CFastVB__CountNodeTreeExpandedLeafCount` | Recursive expanded leaf-count helper. |
| `0x00599cd2 CFastVB__AreNodeTreesStructurallyEqual` | Structural node-tree equality helper. |
| `0x0059a21f CFastVB__AreNodeTreesCompatible` | Parser-context compatibility helper with relaxed-match support and flattening fallback. |
| `0x0059a54d CFastVB__ScoreNodeTreeMatch` | Payload/binding-chain compatibility score helper. |
| `0x0059a71a CFastVB__SelectBestNodeTreeMatch` | Hidden-ABI selector called from CTexture and CDXTexture parser contexts. |
| `0x005958e0 CTexture__LoadDefaultHuffmanTables` | JPEG default Huffman table loader; not an inflate Huffman builder. |
| `0x0059c8c1 CDXTexture__InflateStream_ProcessZlibState` | Zlib inflate state machine with Wave964 `extraout_EAX` caveat resolved. |
| `0x005bcfd3 CDXTexture__InflateCodesState_Process` | Inflate literal/length and distance code-state processor. |
| `0x005bd53b CDXTexture__BuildInflateHuffmanTable` | Zlib/inflate Huffman table builder. |
| `0x005bd933 CDXTexture__InflateDynamicTree_BuildLitDistTrees` | Dynamic inflate literal/length and distance tree builder. |
| `0x005b3fd0 CDXTexture__FlushEntropyBitWriter` | JPEG entropy bit-writer flush helper; not an inflate output-window flush. |

Fresh read-back evidence:

- Pre exports: `17` metadata rows, `17` tag rows, `68` xref rows, `2779` instruction rows, and `17` decompile rows.
- Xref mix: `68` `UNCONDITIONAL_CALL` rows.
- Static closure remains `6411/6411 = 100.00%` with static debt `0 / 0 / 0`.
- Expanded post-100 static surface remains `1560/1560 = 100.00%`.
- Wave1108 current focused accounting advances to `564/1179 = 47.84%`; remaining active focused work: `615`.
- Current risk candidates: `6166`; current focused candidates: `1178`; live regenerated current focused candidates: `1178`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260606-025611_post_wave1163_texture_node_tree_inflate_huffman_current_risk_review_verified`, `19` files, `175999879` bytes, `DiffCount=0`, `HashDiffCount=0`.

What this proves:

- The reviewed texture decode, serialized node-tree, JPEG entropy, and zlib/inflate Huffman rows exist in the saved Ghidra project and have coherent names, signatures, comments, tags, xrefs, instructions, and decompile exports.
- Wave1163 adds a current-risk read-back bridge between the parser/node-tree lane and the image decode lane, while keeping the three tree surfaces distinct: CTexture sentinel/RB-tree helpers, serialized parser/node-tree helpers, and CDXTexture surface-node/resource helpers.
- JPEG Huffman/default entropy helpers and zlib/inflate Huffman table builders are documented as separate static lanes.
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
