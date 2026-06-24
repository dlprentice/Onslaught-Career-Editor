# Texture Resource Decode Static Contract

Historical Wave1216 and Wave1163 anchors below are at-wave snapshots; their older active current-risk counters are preserved as evidence provenance, not current status.

Wave1216 measured anchor: unique-address accounting governs active current-risk progress. Probe token anchor: Wave1216; wave1216-render-resource-texture-hud-tail-current-risk-review; 1145/1179 = 97.12%; 7 render/resource/texture/HUD tail current-risk rows; CThing__InitRenderThingFromInitMeshName; CPDMesh__dtor_base; CWaterRenderSystem__ResetAndMarkSourceFlag; CAtmosphericsProfile__ResetAndInitSnowResources; CHudComponent__RenderPassEntry; CTexture__NodeType11_Ctor_WithDescriptorCopy; CTexture__NodeType12_Ctor_WithStackScalars; CTexture__NodeType11_Dtor_DeleteOnFlag_Body; CTexture__NodeType11_Dtor_DeleteOnFlag; 6411/6411 = 100.00%; 0 / 0 / 0; 12 xref rows; 962 instruction rows; 7 decompile rows; 28 context xref rows; 1015 context instruction rows; 9 context decompile rows; 6 texture-context xref rows; 111 texture-context instruction rows; 6 texture-context decompile rows; 13 data-xref rows; current focused candidates: 1127; live regenerated current focused candidates: 1127; remaining active focused work: 34; current risk candidates: 6166; fresh Ghidra export; texture label correction; 4 renamed; 4 comments updated; 25 tags added; no signature change; no function-boundary change; no executable-byte change; unique-address accounting; Codex read-only consults used; no Cursor/Composer; legacy additive counter is deprecated (`1176/1179`); 26 duplicate-address overcount; Wave1145 arithmetic overcount: 5; Wave911 is historical-retired/non-reconstructable at 812/1408 = 57.67%; 1179/1179 current-risk focused rows reviewed or superseded with bounded static evidence; static-reaudit-current-risk-ledger.json; static-reaudit-measurement-register.md; mesh-resource-render-static-contract.md; texture-resource-decode-static-contract.md; continuity denominator; G:\GhidraBackups\BEA_20260607-101007_post_wave1216_render_resource_texture_hud_tail_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction; rebuild-grade static contracts; no noticeable difference.

Wave1163 current-risk update: Wave1163 (`wave1163-texture-node-tree-inflate-huffman-current-risk-review`) accounts for `17 CFastVB/CTexture/CDXTexture current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator with fresh Ghidra export evidence. It is a read-only review with no mutation, no rename, no signature change, no comment/tag change, no function-boundary change, no executable-byte change, no BEA launch, no installed-game mutation, no save mutation, and no runtime-file mutation. Static closure remains `6411/6411 = 100.00%` with static debt `0 / 0 / 0`; expanded post-100 static surface remains `1560/1560 = 100.00%`; Wave911 focused is historical-retired/non-reconstructable at `812/1408 = 57.67%`; Wave911 top-500 remains `500/500 = 100.00%`; Wave1108 current focused accounting is now `564/1179 = 47.84%`; current risk candidates: 6166; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 615; focused threshold `15`; not Wave911 reconstruction. Fresh exports verified `68 xref rows` and `2779 instruction rows`. Static anchors include `CTexture__NodePayloadRecordCtor`, `CFastVB__NodeType9__ctor`, `CDXTexture__NodeType13__ctor`, `CDXTexture__RegisterSerializedChunk`, `CFastVB__AreNodeTreesCompatible`, `CFastVB__SelectBestNodeTreeMatch`, `CTexture__LoadDefaultHuffmanTables`, `CDXTexture__InflateStream_ProcessZlibState`, `CDXTexture__BuildInflateHuffmanTable`, and `CDXTexture__FlushEntropyBitWriter`. JPEG Huffman separate from inflate Huffman is an explicit static map boundary. Verified backup: `G:\GhidraBackups\BEA_20260606-025611_post_wave1163_texture_node_tree_inflate_huffman_current_risk_review_verified`. Runtime parser behavior, runtime texture decode behavior, runtime JPEG behavior, runtime inflate/decompression behavior, exact node-tree/payload/chunk/z_stream/Huffman-table/entropy-writer layouts, hidden ABI completeness, exact source-body identity, BEA patching behavior, visual QA, gameplay outcomes, and rebuild parity remain separate proof. Current system contract: `texture-resource-decode-static-contract.md`. Probe token anchor: Wave1163; wave1163-texture-node-tree-inflate-huffman-current-risk-review; 564/1179 = 47.84%; 17 CFastVB/CTexture/CDXTexture current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 615; current risk candidates: 6166; fresh Ghidra export; read-only review; no mutation; 0 / 0 / 0; 6411/6411 = 100.00%; 68 xref rows; 2779 instruction rows; CTexture__NodePayloadRecordCtor; CFastVB__NodeType9__ctor; CDXTexture__NodeType13__ctor; CDXTexture__RegisterSerializedChunk; CFastVB__AreNodeTreesCompatible; CFastVB__SelectBestNodeTreeMatch; CTexture__LoadDefaultHuffmanTables; CDXTexture__InflateStream_ProcessZlibState; CDXTexture__BuildInflateHuffmanTable; CDXTexture__FlushEntropyBitWriter; JPEG Huffman separate from inflate Huffman; G:\GhidraBackups\BEA_20260606-025611_post_wave1163_texture_node_tree_inflate_huffman_current_risk_review_verified; texture-resource-decode-static-contract.md; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.

Status: active static contract
Last updated: 2026-06-07
Current anchor: `wave1163-texture-node-tree-inflate-huffman-current-risk-review`

This contract summarizes the static-only texture/resource/decode map for clean-room planning. It is built from saved Ghidra evidence and public-safe read-back docs, not from runtime texture pixels or rebuild proof.

Wave1220 static closeout acceptance: active current-risk focused accounting is `1179/1179 = 100.00%`; remaining active focused work: 0. This is static Ghidra/read-back/system-map acceptance for the current-risk lane, not runtime parser/texture/decompression/JPEG behavior, exact layout proof, exact source-body identity, BEA patching proof, visual output proof, rebuild parity, or no-noticeable-difference parity.

## Static Scope

The texture/resource/decode lane covers resource ingress, texture lookup/lifetime, serialized parser/node-tree helpers, decode setup, codec fronts, JPEG entropy helpers, zlib/inflate helpers, texel conversion/upload, and render-facing texture handoff. Wave1163 adds fresh current-risk read-back over the serialized node-tree plus JPEG/default Huffman and inflate Huffman split.

Core entry points and prior reviews:

- Wave904 `texture-render-static-review-wave904`: static-coherent texture/resource/decode/render core after initial function-quality closure.
- Wave964 `cdxtexture-inflate-codes-tree-review-wave964`: inflate state, block-header return, code-state, and dynamic tree caveat cleanup.
- Wave1025 `cfastvb-node-tree-review-wave1025`: CFastVB/CTexture/CDXTexture parser node-tree review.
- Wave1163 `wave1163-texture-node-tree-inflate-huffman-current-risk-review`: `17 CFastVB/CTexture/CDXTexture current-risk rows`, `564/1179 = 47.84%`, fresh read-only Ghidra export, no mutation.

## Subsystem Map

| Lane | Static anchors | Static contract |
| --- | --- | --- |
| Archive/resource ingress | `CChunkReader`, `CDXMemBuffer__Read`, resource path builders, mapped-file helpers | Resource streams and mapped buffers feed texture load/decode. Exact archive-file runtime behavior and asset extraction parity remain separate proof. |
| Texture lookup/lifetime | `CTexture__FindTexture`, `CTexture__ctor`, `CTexture__Release`, texture global list/fallback fields | Texture names, fallback behavior, list membership, and release paths are statically mapped. Exact concrete `CTexture` layout and runtime D3D resource lifetime remain separate proof. |
| Serialized parser/node-tree | `CTexture__NodePayloadRecordCtor`, `CFastVB__NodeType9__ctor`, `CDXTexture__NodeType13__ctor`, `CDXTexture__RegisterSerializedChunk`, `CFastVB__AreNodeTreesCompatible`, `CFastVB__ScoreNodeTreeMatch`, `CFastVB__SelectBestNodeTreeMatch` | Parser node payloads, node-type constructors, serialized chunk registry, structural predicates, compatibility scoring, and selector diagnostics are statically coherent. Hidden ECX/EAX/stack ABI and exact node/payload/chunk layouts remain separate proof. |
| Decode setup | `CTexture__InitDecodeLookupScratchTables`, `CTexture__InitializeDecodePipelineFromHeader`, `CDXTexture__CreateDecodeJobDescriptor`, `CDXTexture__AllocDecodeBlockAndLink` | Decode scratch tables, image descriptors, component-plane setup, and job/block allocation are statically mapped. Runtime image fidelity and exact descriptor schemas remain separate proof. |
| Codec fronts | `CDXTexture__DecodeMemoryToTextureObject`, `CDXTexture__DecodeFromMemory_WithFallbackCodecs`, `CDXTexture__GetImageHeaderInfo`, PNG/JPEG/BMP/DDS decode helpers | Format dispatch and header/descriptor validation paths are statically mapped. Exact third-party library/source identity and runtime pixels remain separate proof. |
| JPEG entropy/Huffman | `CTexture__LoadDefaultHuffmanTables`, `CDXTexture__FlushEntropyBitWriter`, JPEG scan/layout and entropy helpers | JPEG default Huffman tables and entropy bit-writer state are a distinct static lane. Do not conflate these with zlib/inflate Huffman table builders. Runtime JPEG output and exact entropy-writer layout remain separate proof. |
| Zlib/inflate/Huffman | `CDXTexture__InflateStream_ProcessZlibState`, `CDXTexture__InflateCodesState_Process`, `CDXTexture__BuildInflateHuffmanTable`, `CDXTexture__InflateDynamicTree_BuildLitDistTrees` | Inflate stream/state, code-state processing, dynamic literal/distance tree construction, and table building are statically mapped. Exact `z_stream`, inflate-state, table-entry schema, zlib version/source identity, and runtime decompression behavior remain separate proof. |
| Texel conversion/upload | `CFastVB`/`CTexture`/`CDXTexture` pack/unpack profile rows, `CDXTexture__UploadDecodedBufferToSurface`, surface upload helpers | Packed texel conversion callbacks, profile factories, dither/non-dither paths, and upload handoff are statically mapped. Runtime GPU upload, pixel correctness, and device behavior remain separate proof. |
| Render-facing handoff | `CFastVB__RenderTriangleStripImmediate`, `CVBufTexture__DrawSpriteEx`, `CDXTexture__LoadTextureFromFile_Core` | Texture decode connects into render buffers and sprite/mesh/HUD render consumers. Runtime render correctness and visual QA remain separate proof. |

## Current Wave1163 Evidence

Wave1163 verified `17` metadata rows, `17` tag rows, `68` xref rows, `2779` instruction rows, and `17` decompile rows for:

`CTexture__NodePayloadRecordCtor`, `CFastVB__NodeType9__ctor`, `CDXTexture__NodeType13__ctor`, `CDXTexture__RegisterSerializedChunk`, `CFastVB__NodeTreeHasBitFlag0x200`, `CFastVB__NodeTreeHasOnlyLeafType0to2`, `CFastVB__CountNodeTreeExpandedLeafCount`, `CFastVB__AreNodeTreesStructurallyEqual`, `CFastVB__AreNodeTreesCompatible`, `CFastVB__ScoreNodeTreeMatch`, `CFastVB__SelectBestNodeTreeMatch`, `CTexture__LoadDefaultHuffmanTables`, `CDXTexture__InflateStream_ProcessZlibState`, `CDXTexture__InflateCodesState_Process`, `CDXTexture__BuildInflateHuffmanTable`, `CDXTexture__InflateDynamicTree_BuildLitDistTrees`, and `CDXTexture__FlushEntropyBitWriter`.

Verified backup: `G:\GhidraBackups\BEA_20260606-025611_post_wave1163_texture_node_tree_inflate_huffman_current_risk_review_verified`.

## Clean-Room Planning Boundaries

Useful static outputs for clean-room work:

- Implement archive/resource stream readers from documented AYA/resource docs and static file/stream anchors.
- Implement texture registry/lifetime behavior from `CTexture__FindTexture`, constructor/release rows, and resource load paths.
- Implement a parser node model with separate node payload, node-type constructors, serialized chunk registry, compatibility predicates, and selector diagnostics.
- Implement JPEG/default Huffman and entropy writer logic separately from zlib/inflate table construction.
- Implement zlib/inflate stream/state/table logic as an independent decompression lane; do not infer runtime decompression fidelity until tested.
- Implement texel conversion/upload as a staged CPU conversion plus render handoff plan; do not claim D3D8 runtime parity without runtime proof.

Static boundaries that remain outside this contract:

- Runtime parser/texture/decompression/JPEG behavior.
- Runtime texture pixels and GPU upload behavior.
- Exact concrete layouts for node trees, payloads, chunk builders, `z_stream`, inflate state, table entries, entropy writer, texture objects, and Direct3D surfaces.
- Exact source-body identity and third-party library identity.
- BEA patching behavior, visual QA, gameplay outcomes, and rebuild parity.

Probe token anchor: Wave1163; wave1163-texture-node-tree-inflate-huffman-current-risk-review; 564/1179 = 47.84%; 17 CFastVB/CTexture/CDXTexture current-risk rows; texture-resource-decode-static-contract.md; archive/resource ingress; serialized parser/node-tree; JPEG Huffman separate from inflate Huffman; zlib/inflate/Huffman; texel conversion/upload; no runtime texture decode proof; no rebuild parity.
