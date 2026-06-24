# texture.cpp Function Mappings

Wave1216 (`wave1216-render-resource-texture-hud-tail-current-risk-review`) corrected stale texture node labels: `CTexture__NodeType11_Ctor_WithDescriptorCopy`, `CTexture__NodeType11_Dtor_DeleteOnFlag_Body`, `CTexture__NodeType11_Dtor_DeleteOnFlag`, and `CTexture__NodeType12_Ctor_WithStackScalars`. Verified backup: `G:\GhidraBackups\BEA_20260607-101007_post_wave1216_render_resource_texture_hud_tail_current_risk_review_verified`. Runtime texture behavior, exact layouts, exact source identity, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.

Wave1163 current-risk update: Wave1163 (`wave1163-texture-node-tree-inflate-huffman-current-risk-review`) accounts for `17 CFastVB/CTexture/CDXTexture current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator with fresh Ghidra export evidence. It is a read-only review with no mutation, no rename, no signature change, no comment/tag change, no function-boundary change, no executable-byte change, no BEA launch, no installed-game mutation, no save mutation, and no runtime-file mutation. Static closure remains `6411/6411 = 100.00%` with static debt `0 / 0 / 0`; expanded post-100 static surface remains `1560/1560 = 100.00%`; Wave911 focused is historical-retired/non-reconstructable at `812/1408 = 57.67%`; Wave911 top-500 remains `500/500 = 100.00%`; Wave1108 current focused accounting is now `564/1179 = 47.84%`; current risk candidates: 6166; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 615; focused threshold `15`; not Wave911 reconstruction. Fresh exports verified `68 xref rows` and `2779 instruction rows`. Static anchors include `CTexture__NodePayloadRecordCtor`, `CFastVB__NodeType9__ctor`, `CDXTexture__NodeType13__ctor`, `CDXTexture__RegisterSerializedChunk`, `CFastVB__AreNodeTreesCompatible`, `CFastVB__SelectBestNodeTreeMatch`, `CTexture__LoadDefaultHuffmanTables`, `CDXTexture__InflateStream_ProcessZlibState`, `CDXTexture__BuildInflateHuffmanTable`, and `CDXTexture__FlushEntropyBitWriter`. JPEG Huffman separate from inflate Huffman is an explicit static map boundary. Verified backup: `G:\GhidraBackups\BEA_20260606-025611_post_wave1163_texture_node_tree_inflate_huffman_current_risk_review_verified`. Runtime parser behavior, runtime texture decode behavior, runtime JPEG behavior, runtime inflate/decompression behavior, exact node-tree/payload/chunk/z_stream/Huffman-table/entropy-writer layouts, hidden ABI completeness, exact source-body identity, BEA patching behavior, visual QA, gameplay outcomes, and rebuild parity remain separate proof. Current system contract: `texture-resource-decode-static-contract.md`. Probe token anchor: Wave1163; wave1163-texture-node-tree-inflate-huffman-current-risk-review; 564/1179 = 47.84%; 17 CFastVB/CTexture/CDXTexture current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 615; current risk candidates: 6166; fresh Ghidra export; read-only review; no mutation; 0 / 0 / 0; 6411/6411 = 100.00%; 68 xref rows; 2779 instruction rows; CTexture__NodePayloadRecordCtor; CFastVB__NodeType9__ctor; CDXTexture__NodeType13__ctor; CDXTexture__RegisterSerializedChunk; CFastVB__AreNodeTreesCompatible; CFastVB__SelectBestNodeTreeMatch; CTexture__LoadDefaultHuffmanTables; CDXTexture__InflateStream_ProcessZlibState; CDXTexture__BuildInflateHuffmanTable; CDXTexture__FlushEntropyBitWriter; JPEG Huffman separate from inflate Huffman; G:\GhidraBackups\BEA_20260606-025611_post_wave1163_texture_node_tree_inflate_huffman_current_risk_review_verified; texture-resource-decode-static-contract.md; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.

> Functions from texture.cpp mapped to BEA.exe binary
> Debug path: "C:\dev\ONSLAUGHT2\texture.cpp" at 0x00632ef0

## Overview

> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

- **Functions Mapped:** 17 documented texture.cpp-adjacent functions plus broader texel pack/unpack helpers
- **Status:** active static read-back; Wave661 moved two stale CTexture labels into owner-neutral Math names on 2026-05-21
- **Classes:** CTexture, CTextureBase

Wave1071 (`texel-unpack-head-mid-review-wave1071`) re-read the CTexture-owned Wave672/Wave673 texel-unpack head/middle rows with no mutation, including `0x00584b5f CTexture__UnpackTexels_Bgr8ToFloat4`, `0x00584c04 CTexture__UnpackTexels_Bgra8ToFloat4`, `0x00584cc3 CTexture__UnpackTexels_Bgr8ToFloat4_AlphaOne`, `0x0058579b CTexture__UnpackTexels_Bits444ToFloat4_AlphaOne`, `0x0058586b CTexture__UnpackTexels_PaletteIndexA8ToFloat4`, and `0x00585cb0 CTexture__UnpackTexels_Signed8_8_ToFloat4_RG`. Fresh metadata/tags/xrefs/instructions/decompile evidence keeps the rows tied to DATA-slot texel profile entries and observed lane-expansion behavior. Queue closure remains `6246/6246 = 100.00%`; expanded static surface progress advances to `1319/1560 = 84.55%`; verified backup: `G:\GhidraBackups\BEA_20260602-031627_post_wave1071_texel_unpack_head_mid_review_verified`. Runtime texture output behavior, runtime codec/FourCC behavior, exact profile/descriptor layouts, exact source identity, BEA patching, gameplay outcomes, and rebuild parity remain separate proof.

Wave1070 (`texel-unpack-tail-review-wave1070`) re-read three CTexture-owned texel-unpack rows with no mutation: `0x005860ba CTexture__UnpackTexels_Signed16_16_ToFloat4_RG`, `0x00586438 CTexture__UnpackTexels_NormalXY_Signed8_8_ReconstructZ`, and `0x0058686f CTexture__UnpackTexels_CopyRaw128`. Fresh metadata/tags/xrefs/instructions/decompile evidence keeps the rows tied to their Wave674 texel-unpack DATA slots, source-field reads, normal reconstruction/raw-copy behavior, and current bounded signatures. Queue closure remains `6246/6246 = 100.00%`; expanded static surface progress advances to `1278/1560 = 81.92%`; verified backup: `G:\GhidraBackups\BEA_20260602-022701_post_wave1070_texel_unpack_tail_review_verified`. Runtime texture output behavior, runtime codec/FourCC behavior, exact profile/descriptor layouts, exact source identity, BEA patching, gameplay outcomes, and rebuild parity remain separate proof.

Wave1057 math dispatch thunk review (`math-dispatch-thunk-review-wave1057`) re-read the texture-adjacent math/CFastVB dispatch island with no mutation. Texture-side context includes dispatch wrappers around the same global math table, while exact anchors include `0x005771af Math__BuildScaleMatrix4x4_Dispatch`, `0x005771dd Math__BuildScaleMatrix4x4`, `0x00577239 Math__BuildTranslationMatrix4x4_Dispatch`, `0x005775c3 Math__BuildQuaternionRotationMatrix`, `0x0057798e CFastVB__BuildAxisAngleQuaternion_Dispatch`, `0x00577a3e Math__BuildQuaternionFromEulerAngles`, `0x00577eaa Math__InterpolateVec4ByRatio`, `CFastVB__InitDispatchTableByCpuFeature`, `CFastVB__InitMathDispatchTable`, `CFastVB__InitDispatchTableVariant_005980be`, and `CFastVB__InitDispatchOpsFromFeatureFlags`. Queue closure remains `6246/6246 = 100.00%`; Wave911 focused progress is `799/1408 = 56.75%`; expanded static surface progress is `1121/1509 = 74.29%`; top-500 coverage is `500/500 = 100.00%`. Verified backup: `G:\GhidraBackups\BEA_20260601-184232_post_wave1057_math_dispatch_thunk_review_verified`. Exact dispatch-table slot schema, exact vector/matrix/quaternion/ratio/lane-order/storage layouts, runtime CPU feature selection, runtime math/render correctness, exact source-body identity, BEA patching, gameplay outcomes, and rebuild parity remain separate proof. Probe token anchor: Wave1057; math-dispatch-thunk-review-wave1057; 0x005771af Math__BuildScaleMatrix4x4_Dispatch; 0x005771dd Math__BuildScaleMatrix4x4; 0x00577239 Math__BuildTranslationMatrix4x4_Dispatch; 0x005775c3 Math__BuildQuaternionRotationMatrix; 0x0057798e CFastVB__BuildAxisAngleQuaternion_Dispatch; 0x00577a3e Math__BuildQuaternionFromEulerAngles; 0x00577eaa Math__InterpolateVec4ByRatio; CFastVB__InitDispatchTableByCpuFeature; CFastVB__InitMathDispatchTable; CFastVB__InitDispatchTableVariant_005980be; CFastVB__InitDispatchOpsFromFeatureFlags; 799/1408 = 56.75%; 1121/1509 = 74.29%; 500/500 = 100.00%; 6246/6246 = 100.00%; G:\GhidraBackups\BEA_20260601-184232_post_wave1057_math_dispatch_thunk_review_verified; no mutation.

Wave1025 CFastVB node-tree review (`cfastvb-node-tree-review-wave1025`) re-read CTexture-side node-type constructor helpers with no mutation, including `0x005997e1 CTexture__NodeType12_Ctor_DeleteOnFlag` and `0x0059996f CTexture__NodeType12_Ctor_ScalarDeletingDtor`, plus selector call context in `0x0059930d CTexture__ValidateConstantRegisterDeclarationType`. The review preserves the hidden-ECX/locked-storage boundary and treats node-type naming drift as static retail evidence rather than exact source identity. Verified backup: `G:\GhidraBackups\BEA_20260601-004522_post_wave1025_cfastvb_node_tree_review_verified`. Runtime shader/parser/texture behavior, exact node payload layouts, exact source-body identity, BEA patching, and rebuild parity remain separate proof.

Wave900 final static tail (`final-static-tail-wave900`, `wave900-readback-verified`) closed `0x005d5120 CTexture__FindTexture_Unwind`, the remaining texture.cpp unwind cleanup row, and completed the current static function-quality proxy. Probe token anchor: Wave900 final static tail; final-static-tail-wave900; 0x005d04e6 RtlUnwind; 0x005d06f0 CRT__InitSehFrameNoop; 0x005d08ad CRT__TmpFile_OpenUniqueBinaryStream; 0x005d0a9f CRT__LongJmpProbe_NoOp; 0x005d0c0c GetCurrentProcessId; 0x005d0c7f CRT__LCMapStringW_AnsiCompat; 0x005d5120 CTexture__FindTexture_Unwind; 6113/6113 = 100.00%; G:\GhidraBackups\BEA_20260526-090248_post_wave900_final_static_tail_verified. Static evidence ties the row to scope-table DATA xref `0x0061d9cc`, debug path pointer `0x00632ef0`, line token `0x98`, allocation/type value `0x2`, and `OID__FreeObject_Callback(EBP-0x210)`. Exact parent source body, allocation ownership, runtime exception cleanup behavior, BEA patching, and rebuild parity remain deferred.

Wave904 (`texture-render-static-review-wave904`) reviews the broader CTexture/CDXTexture/CFastVB/CVBufTexture chain as a `static-coherent texture/resource/decode/render core` after export-contract queue closure `6113/6113 = 100.00%` (static review slice only). It covers `1289` rows across `25` selected families, including `CDXTexture` `366`, `CFastVB` `347`, `CTexture` `233`, and `CVBufTexture` `40`; CTexture-side anchors include `CTexture__FindTexture`, `CTexture__ctor`, `CTexture__Release`, and `CTexture__InitializeDecodePipelineFromHeader`, with cross-system anchors `CDXTexture__LoadTextureFromFile_Core`, `CDXTexture__DecodeMemoryToTextureObject`, `CDXTexture__ValidateJpegFrameAndComputeMcuLayout`, `CFastVB__RenderTriangleStripImmediate`, and `CVBufTexture__DrawSpriteEx`. Asset bridge counts include `847/847` loose textures and `352/352` model material/texture-binding rows. Verified backup: `G:\GhidraBackups\BEA_20260526-101300_post_wave904_texture_render_static_review_verified`.

Wave895 decode feature tail (`decode-feature-tail-wave895`, `wave895-readback-verified`) saved comments/tags for nine raw commentless CFastVB/CTexture/CDXTexture decode-feature rows. Probe token anchor: Wave895 decode feature tail; decode-feature-tail-wave895; 0x00598390 CFastVB__DetectCpuFeatureMask; 0x0059a71a CFastVB__SelectBestNodeTreeMatch; 0x0059b150 CTexture__InitDecodeLookupScratchTables; 0x0059b1d0 CTexture__InitializeDecodePipelineFromHeader; 0x0059b510 CDXTexture__ValidateJpegFrameAndBuildScanLayout; 0x0059b6f0 CTexture__BuildComponentPlaneLayoutTables; 0x0059b880 CTexture__EnsureComponentDecodeScratchBlocks; 0x0059be00 CDXTexture__CreateDecodeJobDescriptor; 0x0059be70 CDXTexture__AllocDecodeBlockAndLink; 0x0059c610 CFastVB__ReleaseOwnedObjectAndReset_Core; 6086/6113 = 99.56%; G:\GhidraBackups\BEA_20260526-064920_post_wave895_decode_feature_tail_verified. Static evidence ties the CTexture-owned portion to decode lookup scratch initialization, decode-pipeline setup, JPEG/component scan-layout work, and component-plane/MCU layout table construction. Exact feature-bit names, node-tree layout, decode-state/component-plane/descriptor/allocator-state layouts, hidden register/stack ABI completeness, runtime parser/texture/JPEG/image decode behavior, BEA patching, and rebuild parity remain deferred.

Wave894 JPEG header parser tail (`jpeg-header-parser-tail-wave894`, `wave894-readback-verified`) saved comments/tags for four raw commentless JPEG/image header parser and decode descriptor rows across texture decode ownership. Probe token anchor: Wave894 JPEG header parser tail; jpeg-header-parser-tail-wave894; 0x005913b0 CFastVB__JpegParser_ResetFrameState; 0x00591720 CFastVB__JpegParser_ParseSOFComponents; 0x0059364c CDXTexture__GetImageHeaderInfo; 0x00594f15 CTexture__FinalizeDecodeFormatDescriptor; raw no-function callsites 0x00592617 and 0x0059274a; PNG decode callsite 0x0057ba81; PNG IHDR callsite 0x0059d86d; 0x00598390 CFastVB__DetectCpuFeatureMask; 6077/6113 = 99.41%; G:\GhidraBackups\BEA_20260526-062021_post_wave894_jpeg_header_parser_tail_verified. Static evidence ties the tranche to hidden-register JPEG parser state reset, SOF component parsing, image header descriptor query, and IHDR row-byte descriptor finalization. Exact JPEG parser state layout, exact PNG/JPEG shared descriptor schema, exact color/format/sampling enum names, hidden register ABI completeness, runtime image decode behavior, BEA patching, and rebuild parity remain deferred.

Wave893 CTexture directive parser tail (`ctexture-directive-parser-tail-wave893`, `wave893-readback-verified`) saved comments/tags for eight raw commentless CTexture preprocessor, directive-parser, shader-parser, diagnostic, register-reference, and parser work-queue rows. Probe token anchor: Wave893 CTexture directive parser tail; ctexture-directive-parser-tail-wave893; 0x0058aacf CTexture__HandleDirective_If; 0x0058b812 CTexture__RunDirectiveParser; 0x0058bd25 CTexture__InitializePreprocessorStateFromMemorySpan; 0x0058c396 CTexture__InitBufferCursorRange; 0x0058d821 CTexture__EmitParserMessageBySeverity; 0x0058f34c CTexture__ResolveOrCreateRegisterReference; 0x0059020b CTexture__ParseScriptWithYaccTables; 0x00590da0 CTexture__DrainParserWorkQueue; DAT_009d1430; DAT_00657b48; DAT_009d2010; DAT_00658438; 0x005913b0 CFastVB__JpegParser_ResetFrameState; 6073/6113 = 99.35%; G:\GhidraBackups\BEA_20260526-055039_post_wave893_ctexture_directive_parser_tail_verified. Static evidence ties the tranche to macro/directive token expansion, YACC-style directive parsing, preprocessor context setup, source-buffer cursor initialization, diagnostic emission, register-reference lookup, YACC-style shader/script parsing, and parser work-queue draining. Exact preprocessor/parser/register/work-queue layouts, exact token/action/diagnostic enum meanings, exact grammar/source identity, runtime macro expansion, shader parsing, decode scheduling behavior, BEA patching, and rebuild parity remain deferred.

Wave889 texture codec surface prelude (`texture-codec-surface-prelude-wave889`, `wave889-readback-verified`) saved comments/tags for the texture codec, surface-node, mapped-resource, vertex-shader parser, and resample prelude tranche. Probe token anchor: Wave889 texture codec surface prelude; texture-codec-surface-prelude-wave889; 0x00579a9a CVertexShader__CompileScriptWithDirectiveParser; 0x00579b39 CDXTexture__LookupNamedFormatDescriptor; 0x00579e08 CDXTexture__DecodeBmpDibFromMemory; 0x0057ca6a CDXTexture__DecodeFromMemory_WithFallbackCodecs; 0x0057c7a4 CMeshCollisionVolume__LoadMappedTextureResourcesByMode; 0x0057cca4 CFastVB__BuildResampleKernelBuckets; 0x0057cf60 CDXTexture__CopyDxtBlockRegion; 0x0057d0ee CWaypointManager__BoxBlurPackedColorRows_Scalar; 6054/6113 = 99.03%; G:\GhidraBackups\BEA_20260526-040930_post_wave889_texture_codec_surface_prelude_verified. Static evidence ties the tranche to directive parsing, descriptor lookup, codec dispatch, surface-node cleanup, mapped texture export, resample bucket setup, and DXT block copying. Exact texture/codec/surface-node/mapped-file/descriptor/parser/resample table layouts, exact source-body identity, runtime texture decode/encode/export/resample/render behavior, BEA patching, and rebuild parity remain deferred.

## Wave886 Texture Decode/Upload Tail (2026-05-26)

Wave888 texture transform dispatch tail (`texture-transform-dispatch-tail-wave888`, `wave888-readback-verified`) saved comments/tags for CTexture-side dispatch wrappers and transform helpers. Exact anchors include `0x00578a20 CTexture__MapNormalizedUvToVolumeCoords` and `0x00579273 CTexture__BuildTransformMatrixWithOptionalOffsets`; companion rows include `0x00577b17 CTexture__DispatchPtr00656f7c_WithInit`, `0x00577d47 CTexture__DispatchPtr0065700c_WithInit`, and `0x005783d9 CTexture__DispatchPtr00657040_WithInit`. Probe token anchor: `Wave888 texture transform dispatch tail`; `texture-transform-dispatch-tail-wave888`; `0x0057617e CDXTexture__DispatchPtr00656f48_WithInit`; `0x00576286 CDXTexture__DispatchPtr00656f68_WithInit`; `0x00576404 Math__InterpolateVec4Cubic`; `0x00576621 Math__InterpolateVec4ByUV`; `0x005768fe CFastVB__DispatchIndirect_00656f3c`; `0x0057770b CFastVB__BuildTransformMatrixWithOffsets`; `0x00578a20 CTexture__MapNormalizedUvToVolumeCoords`; `0x00578dad CFastVB__MapVolumeCoordsToNormalizedUv`; `0x00578f53 CFastVB__ApplyOptionalTransformPasses`; `0x00579273 CTexture__BuildTransformMatrixWithOptionalOffsets`; `0x00656f48`; `0x0065715c`; `0x00579a9a CVertexShader__CompileScriptWithDirectiveParser`; `6052/6113 = 99.00%`; `G:\GhidraBackups\BEA_20260526-033426_post_wave888_texture_transform_dispatch_tail_verified`. Exact dispatch-table slot targets, exact CPU feature policy, exact descriptor/matrix/vertex-shader/texture-transform layouts, runtime texture/math/render behavior, BEA patching, and rebuild parity remain deferred.

Wave886 texture decode/upload tail (`texture-decode-upload-tail-wave886`, `wave886-readback-verified`) saved comments/tags for `0x00573d80 CTexture__InsertNodeIntoTree` and nine companion DXTexture/mapped-file decode/upload helpers documented in [`DXTexture.cpp`](../DXTexture.cpp/_index.md): `0x00574492 CDXTexture__UploadDecodedBufferToSurface`, `0x0057473b CDXTexture__NormalizeTextureConversionParams`, `0x0057516c CDXTexture__DecodeMemoryToTextureObject`, and `0x005758e6 CDXTexture__DecodeMappedMemoryEntry`. Probe token anchor: `Wave886 texture decode/upload tail`; `texture-decode-upload-tail-wave886`; `0x00573d80 CTexture__InsertNodeIntoTree`; `0x00574492 CDXTexture__UploadDecodedBufferToSurface`; `0x0057473b CDXTexture__NormalizeTextureConversionParams`; `0x0057516c CDXTexture__DecodeMemoryToTextureObject`; `0x005758e6 CDXTexture__DecodeMappedMemoryEntry`; `CFastVB__InsertNodeIntoRBTreeWithHint_00573340`; `CDXTexture__DecodeFromMemory_WithFallbackCodecs`; `CFastVB__InitDualTexelConversionPipeline`; `CDXTexture__GenerateMipChainBySurfaceCopy`; `0x005759b6 CFastVB__DispatchIndirect_00657014`; `5978/6113 = 97.79%`; `G:\GhidraBackups\BEA_20260526-023255_post_wave886_texture_decode_upload_tail_verified`.

Wave887 texture dispatch/interpolation tail (`texture-dispatch-interpolation-tail-wave887`, `wave887-readback-verified`) saved comments/tags for CTexture-side dispatch wrappers plus companion DXTexture/FastVB/Math/CVBufTexture rows. Probe token anchor: `Wave887 texture dispatch/interpolation tail`; `texture-dispatch-interpolation-tail-wave887`; `0x005759b6 CFastVB__DispatchIndirect_00657014`; `0x005759c3 CDXTexture__PackTexels_DispatchIndirect_005759c3`; `0x00575b47 Math__InterpolateVec2Cubic`; `0x00575dc9 CFastVB__HermiteInterpolateVec3`; `0x0057600b CVBufTexture__DispatchTextureTransformThunk`; `0x00576161 CFastVB__DispatchIndirectByGlobalTable`; dispatch slots `0x00657014` and `0x00656f58`; `0x0057617e CDXTexture__DispatchPtr00656f48_WithInit`; `6008/6113 = 98.28%`; `G:\GhidraBackups\BEA_20260526-030217_post_wave887_texture_dispatch_interpolation_tail_verified`. Exact dispatch-table slot targets, exact CPU feature policy, runtime texture/math/render behavior, BEA patching, and rebuild parity remain deferred.

Static evidence shows `CTexture__InsertNodeIntoTree` is the remaining Wave654-family red-black tree insert helper: it is reached from `0x00573530 CFastVB__InsertNodeIntoRBTreeWithHint_00573340`, allocates a `0x14`-byte node through `OID__AllocObject_DefaultTag_00662b2c`, links against sentinel `DAT_009d0c44`, updates the tree count, and runs insert fixup rotations/recolors. The existing CTexture owner name is retained from the prior tree-family naming evidence even though the direct caller is adjacent CFastVB tree code. Exact owner/template identity, concrete node layout, runtime texture/tree behavior, BEA patching, and rebuild parity remain deferred.

## Wave876 Texture Core Tail (2026-05-25)

Wave876 texture core tail (`texture-core-tail-wave876`, `wave876-readback-verified`) saved comments/tags/signatures for the texture.cpp-adjacent raw head rows `0x00556cc0 CTexture__ctor`, `0x00556f50 CTexture__Release`, `0x00557060 CTextureSequence__EnsureLoaded`, and `0x005572c0 CTextureSequence__ReleaseIfLoaded`, while the same tranche also documented `0x00557a90 CDXTexture__LoadTextureFromFile_Core`, `0x00558690 CDXTexture__GetAnimatedFrame`, `0x005588f0 CVBufTexture__RenderModePass`, and `0x0055a0f0 CEngine__TextureFormatIndexToD3D` in their owner docs. Probe token anchor: `Wave876 texture core tail`; `texture-core-tail-wave876`; `0x00556cc0 CTexture__ctor`; `0x00557a90 CDXTexture__LoadTextureFromFile_Core`; `0x00558690 CDXTexture__GetAnimatedFrame`; `0x005588f0 CVBufTexture__RenderModePass`; `0x0055a0f0 CEngine__TextureFormatIndexToD3D`; high-importance texture/resource/render connector rows with low local evidence density, not low-importance filler; `0x0055b0e0 CWaterRenderSystem__ctor`; `5885/6113 = 96.27%`; `G:\GhidraBackups\BEA_20260525-212045_post_wave876_texture_core_tail_verified`.

Static evidence ties the constructor to `CTextureBase__Init(this+0x08)`, `CDXSurf__vtable`, texture/resource field initialization, and callsites in `CTexture__FindTexture`, `CDXBattleLine`, `CDXCompass`, `CDXFont`, and `CDXTexture__Deserialize`. `CTexture__Release` clears render-state cache slots 0-3 and dispatches the release/delete vtable slot. `CTextureSequence__EnsureLoaded` and `CTextureSequence__ReleaseIfLoaded` are vtable/data-slot texture resource helpers around `DAT_00888c8c`, `this+0x14c`, `this+0xac/+0xb0/+0x148/+0x150`, and `this+0xb8`. Exact texture class layouts, runtime texture load/decode/animation/render/dump behavior, BEA patching, and rebuild parity remain deferred.

## Wave832 Texture/Surface Prelude (2026-05-24)

Wave832 Texture/Surface Prelude (`texture-surface-prelude-wave832`, `wave832-readback-verified`) hardened `0x004f2710 CTextureBase__Init` as `void * __fastcall CTextureBase__Init(void * texture_base)` and paired it with adjacent surface-list teardown evidence for `0x004f2790 CDXSurf__UnlinkNodeFromGlobalList` as `void __fastcall CDXSurf__UnlinkNodeFromGlobalList(void * texture_base)`. These are important connective/static infrastructure rows: texture-base name initialization and global texture/surface list maintenance.

Probe anchors: `Wave832 Texture/Surface Prelude`, `texture-surface-prelude-wave832`, `0x004f2710 CTextureBase__Init`, `void * __fastcall CTextureBase__Init(void * texture_base)`, `0x004f2790 CDXSurf__UnlinkNodeFromGlobalList`, `void __fastcall CDXSurf__UnlinkNodeFromGlobalList(void * texture_base)`, `DAT_0083d9b0`, `JCLTEX #%d`, `0x00556ce1`, `0x00556e70`, `5654/6098 = 92.72%`, `0x004f5b70 CParticleDescriptor__SetIndexedParam`, `G:\GhidraBackups\BEA_20260524-230834_post_wave832_texture_surface_prelude_verified`.

Static evidence: `CTexture__ctor` callsite `0x00556ce1` loads `ECX=this+0x08` before calling `CTextureBase__Init`; the initializer records the prior global list head `DAT_0083d9b0` at `texture_base+0x98`, links the owner by storing `texture_base-0x08`, zeroes the name/subobject head, formats `JCLTEX #%d`, and increments `DAT_0083d99c`. The paired unlink helper is documented in [`DXSurf.cpp`](../DXSurf.cpp.md) and [`CDXSurf__UnlinkNodeFromGlobalList.md`](../DXSurf.cpp/CDXSurf__UnlinkNodeFromGlobalList.md).

Post-Wave832 queue telemetry is `6098` total, `5654` commented, `444` commentless, `0` exact-undefined signatures, `0` `param_N`, strict proxy `5654/6098 = 92.72%`, and next raw head `0x004f5b70 CParticleDescriptor__SetIndexedParam`. Verified backup: `G:\GhidraBackups\BEA_20260524-230834_post_wave832_texture_surface_prelude_verified`. Exact texture.cpp or DXSurf.cpp source-body identity, concrete `CTextureBase`, `CDXSurf`, or `CTexture` ownership boundary, full field layout, runtime texture/surface lifetime behavior, BEA patching, and rebuild parity remain deferred.

## Wave806 Texture Refcount Helper Correction (2026-05-24)

Wave806 raw commentless head (`raw-commentless-head-wave806`, `wave806-readback-verified`) superseded the stale `0x004f27e0 CHud__DecrementCounter9C` label with `0x004f27e0 CTexture__DecrementRefCountFromNameField`. Saved signature is `void __thiscall CTexture__DecrementRefCountFromNameField(void * this)`.

Static read-back evidence shows the body decrements `*(this+0x9c)`. Observed release callsites pass `texture+0x08`, so this updates the CTexture refcount at `texture+0xa4`, matching the `CTexture__FindTexture` cache-hit increment path. Pre-Wave806 xref export found 115 callers across texture/resource shutdown paths, including `CDXLandscape__ReleaseMixerDetailTextureRef`, `CLTShell__ShutdownRuntimeAndReleaseResources`, `CVBufTexture__dtor`, and several frontend/resource cleanup helpers.

Post-Wave806 queue telemetry is `6098` total, `5581` commented, `517` commentless, `0` exact-undefined signatures, `0` `param_N`, strict proxy `5581/6098 = 91.52%`, and next raw head `0x0048f2f0 CDXLandscape__SetUpdateBoundsAndRebuildVB`. Verified backup: `G:\GhidraBackups\BEA_20260524-102416_post_wave806_raw_commentless_head_verified`. Exact CTexture layout/type recovery, runtime texture lifetime behavior, BEA patching, and rebuild parity remain deferred.

## Wave796 Final Signature Debt (2026-05-24)

Wave796 signature debt (`signature-debt-wave796`, `wave796-readback-verified`) saved the final CTexture row-batch param-name hardening rows: `0x0059c070 CTexture__ProcessRowBatchesLinearStride` and `0x0059c110 CTexture__ProcessRowBatchesMcuStride128`. Saved signatures are `void __stdcall CTexture__ProcessRowBatchesLinearStride(int callback_context, int callback_mode)` and `void __stdcall CTexture__ProcessRowBatchesMcuStride128(int callback_context, int callback_mode)`. The pass made no renames, no function-boundary changes, and no executable-byte changes; queue telemetry after the pass is 0 exact-undefined signatures, 0 param_N signatures, and strict clean-signature proxy `5544/6098 = 90.92%`. Verified backup: `G:\GhidraBackups\BEA_20260524-050846_post_wave796_final_param_signature_debt_verified`. Hidden ESI row-batch descriptor layout, callback contract, runtime texture behavior, BEA patching, and rebuild parity remain deferred.

## Function List

| Address | Name | Status | Description | Link |
|---------|------|--------|-------------|------|
| 0x004f27e0 | CTexture__DecrementRefCountFromNameField | WAVE806 | Decrements the texture refcount field reached via the name-field subobject; supersedes `CHud__DecrementCounter9C` | - |
| 0x004f27f0 | CTexture__FindTexture | NAMED | Finds or loads a texture by name | [View](CTexture__FindTexture.md) |
| 0x004f29c0 | CTexture__InitDefaultTextureResourcesAndStatus | NAMED | Lazily resolves `meshtex/default.tga` and emits texture-resource status | - |
| 0x004f2a30 | CTexture__ClearOut | NAMED | Texture shutdown clear-out, zero-ref release, and leak logging | - |
| 0x004f2b40 | CTexture__FreeLevelResources | NAMED | End-of-level texture free helper and leak logging | - |
| 0x005d5120 | CTexture__FindTexture_Unwind | NAMED | Exception unwind handler for FindTexture | [View](CTexture__FindTexture_Unwind.md) |
| 0x00556cc0 | CTexture__ctor | WAVE876 | CTexture constructor - calls `CTextureBase__Init` with `ECX=this+0x08`, initializes vtable and fields | - |
| 0x004f2710 | CTextureBase__Init | WAVE832 | Initializes texture-base/name subobject, links owner into `DAT_0083d9b0`, and formats `JCLTEX #%d` generated names | [View](CTextureBase__Init.md) |
| 0x00556f50 | CTexture__Release | WAVE876 | Clears render-state cache slots and dispatches texture release/delete vtable slot | - |
| 0x00572e40 | CTexture__DestroyNodeTreeAndStorage | NAMED | Destroys sentinel-backed tree/list state and releases shared sentinel storage | - |
| 0x005738e0 | CTexture__EraseNodeFromTree | NAMED | Removes a node from a sentinel-backed red-black tree and runs delete fixup | - |
| 0x00573cc0 | CTexture__DestroySubtreeRecursive | NAMED | Recursively frees subtree nodes until the shared sentinel is reached | - |
| 0x00573d80 | CTexture__InsertNodeIntoTree | WAVE886 | Inserts a node into the sentinel-backed red-black tree, then runs insert fixup rotations/recolors; direct caller is `CFastVB__InsertNodeIntoRBTreeWithHint_00573340` | - |
| 0x00574080 | CTexture__WalkNodeListUntilSentinel | NAMED | Narrow sentinel walk helper with no visible decompile side effect | - |
| 0x005740a0 | CTexture__RotateTreeLeft | NAMED | Left-rotation helper for adjacent red-black tree fixup paths | - |
| 0x00574100 | CTexture__InitTreeNodeParentAndKey | NAMED | Allocates a 0x14-byte tree node, stores parent/color fields, and returns it | - |
| 0x00574120 | CTexture__TreeIteratorNext | NAMED | Advances an iterator slot to the in-order successor | - |
| 0x00574180 | CTexture__TreeIteratorPrev | NAMED | Retreats an iterator slot to the in-order predecessor | - |

## Wave768 texture.cpp Unwind Continuation

Wave768 static read-back (`unwind-continuation-wave768`, `wave768-readback-verified`) saved comments/tags/signatures for texture.cpp-adjacent compiler-generated SEH unwind cleanup callbacks around the already-clean `0x005d5120 CTexture__FindTexture_Unwind`. Exact anchors include `0x005d5100 Unwind@005d5100`, `0x005d5198 Unwind@005d5198`, and `0x005d5200 Unwind@005d5200`. Evidence includes DATA scope-table xrefs `0x0061d9a4` through `0x0061dad4`, texture.cpp debug path `0x00632ef0`, `CDXMemBuffer__dtor_base`, `CMonitor__Shutdown_Thunk`, `CMapWhoEntry__RemoveFromMap`, `CCollisionSeekingRound__Destructor`, and `CThing__dtor_base`. Verified backup: `G:\GhidraBackups\BEA_20260523-171555_post_wave768_unwind_continuation_verified`. Exact parent source-body identity, runtime exception behavior, runtime cleanup behavior, BEA patching, and rebuild parity remain deferred.

## Wave689 CTexture Script Loader Tail Read-Back Note

Wave689 CTexture script loader tail saved six script-loader, query-stub, query-interface, and memory-write-stream helpers. Tag anchor: `ctexture-script-loader-tail-wave689`; the next queue head after this pass is `0x00590e10 CDXTexture__FillInputBufferFromSource`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x005907d9` | `int __thiscall CTexture__LoadScriptAndDispatchByVersion(void * this, void * preprocessor_context, uint compile_flags, uint assembly_fragment_version, void * out_stream_slot, void * unused_context)` | Validates compile flags and `out_stream_slot`, resets parser compile-context slots, optionally creates Wave687 parser-state symbol tables for assembly fragments, reads and normalizes shader-version tokens, maps observed vs/ps constants to the internal version index, optionally creates the D3D9 shader validator callback, runs the yacc parser, finalizes symbol/debug chunks, writes the output stream, releases the validator, and pops the preprocessor frame. |
| `0x00590c4a` | `void __fastcall CTexture__SetQueryStubVtableAndReleaseChild(void * query_stub)` | Sets `query_stub` vtable to `PTR_CDXTexture__QueryInterfaceByGuid_005ed3dc` and frees the child/callback pointer at `query_stub+0x0c` through `OID__FreeObject_Callback`. |
| `0x00590cc2` | `void * __thiscall CTexture__Dtor_QueryStub_DeleteOnFlag(void * this, uint delete_flags)` | Scalar-deleting destructor wrapper for the query/memory-stream stub; calls the query-stub cleanup helper, frees `this` when `delete_flags` bit 0 is set, returns `this`, and ends with `RET 0x4`. |
| `0x00590cde` | `int __stdcall CDXTexture__QueryInterfaceByGuid(void * object_stub, void * requested_guid, void * out_interface_slot)` | Clears `out_interface_slot`, compares `requested_guid` against two observed 16-byte GUID constants, returns `E_NOINTERFACE` on mismatch, otherwise writes `object_stub` and calls the vtable AddRef-like slot at `+0x04`. |
| `0x00590d25` | `void __fastcall CTexture__InitMemoryWriteStream(void * memory_write_stream)` | Initializes a `0x10`-byte memory-write stream/query stub by clearing `+0x08/+0x0c`, installing the query-interface vtable, and setting the refcount-like field at `+0x04` to `1`. |
| `0x00590d3d` | `int __stdcall CTexture__CreateMemoryWriteStream(int initial_byte_count, void * out_stream_slot)` | Validates `out_stream_slot`, allocates and initializes a memory-write stream/query stub, calls vtable `+0x18` with `initial_byte_count`, releases through vtable `+0x14` on setup failure, and writes the stream pointer on success. |

Wave689 read-back evidence verified `6` metadata rows, `6` tag rows, `7` xref rows, `546` instruction rows, and `6` clean decompile rows. Pre-state evidence covered the same focused exports and candidate exports for `13` adjacent script-loader, query-stub, memory-stream, and JPEG rows before the final six-row tranche was selected. The pass hardened `6` signatures, made no renames, made no function-boundary changes, and made no executable-byte changes. Post-Wave689 queue telemetry is `6098` total, `3945` commented, `2153` commentless, `1216` exact-undefined signatures, `376` `param_N`, strict clean-signature proxy `3895/6098 = 63.87%`, and next head `0x00590e10 CDXTexture__FillInputBufferFromSource`. Verified backup: `G:\GhidraBackups\BEA_20260521-120555_post_wave689_ctexture_script_loader_tail_verified`.

Exact compile flag enum, shader-version enum, parser-context layout, D3D validator ABI, output stream contract, stub/stream object layouts, COM contract completeness, runtime texture compiler behavior, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave689 CTexture script loader tail`, `ctexture-script-loader-tail-wave689`, `0x005907d9 CTexture__LoadScriptAndDispatchByVersion`, `0x00590d3d CTexture__CreateMemoryWriteStream`, `0x00590e10 CDXTexture__FillInputBufferFromSource`.

## Wave688 CTexture Parser Tail Read-Back Note

Wave688 CTexture parser tail saved five parser-terminal, register-node parser, node/binding cleanup, compile-context cleanup, and parser-reduction helpers. Tag anchor: `ctexture-parser-tail-wave688`; the next queue head after this pass is `0x005907d9 CTexture__LoadScriptAndDispatchByVersion`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x0058f593` | `uint __fastcall CTexture__ReadParserTerminalToken(void * parser_compile_context)` | Reads preprocessed tokens through `CTexture__GetNextTokenWithPreprocessor` into `parser_compile_context+0x10`, maps token classes to parser terminal ids, recognizes `entrypoint`/`true`/`false`, calls `CTexture__ParseShaderSemanticToken` when semantic parsing is enabled, and sets `+0x4c/+0x50` error flags on lexer failure. |
| `0x0058f66f` | `int __thiscall CTexture__ParseScriptTokensAndBuildNodes(void * this, void * token_descriptor, int relative_register_node, int unused_context)` | Parses underscore-delimited register/expression token text from `token_descriptor+0x08`, matches register strings against the observed `0x48`-byte descriptor table, derives register classes/modifiers, handles relative register offsets, allocates `0x2c`-byte node payloads, calls the deferred register-reference helper when parser state permits, and emits diagnostic `0x7d5` for invalid register forms. |
| `0x0058fb70` | `void __fastcall CTexture__DestroyNodeAndBindingsRecord(void * node_payload_record)` | Frees the object/callback pointer at `node_payload_record+0x00` and releases a non-null linked binding record at `+0x20` through the Wave687 binding destructor wrapper. |
| `0x0058fb8b` | `void __fastcall CTexture__DestroyParserCompileContext(void * parser_compile_context)` | Tears down the compile context by releasing `+0x08` through vtable slot `+0x08`, releasing the `+0x34` owner/list through its vtable, freeing `+0x58` callback storage, and releasing the `+0x78` parser-state object through the Wave687 parser-state destructor wrapper. |
| `0x0058fbc5` | `void __thiscall CTexture__ApplyParserReductionAction(void * this, uint reduction_rule_id, uint rhs_count, uint unused_context)` | Pops `rhs_count` nodes from the `+0x34` parser stack, switches on `reduction_rule_id`, links node lists, validates/coissues/predicates instruction nodes, applies channel masks and swizzles, builds relative-address and literal nodes, emits observed diagnostics, cleans unused stack entries, and pushes the reduction result through a `0x14`-byte parser-stack record. |

Wave688 read-back evidence verified `5` metadata rows, `5` tag rows, `7` xref rows, `185` instruction rows, and `5` clean decompile rows. Pre-state evidence covered the same focused exports and candidate exports for `8` adjacent parser-tail, script-loader, and query-stub rows before the final five-row tranche was selected. The pass hardened `5` signatures, made no renames, made no function-boundary changes, and made no executable-byte changes. Post-Wave688 queue telemetry is `6098` total, `3939` commented, `2159` commentless, `1216` exact-undefined signatures, `382` `param_N`, strict clean-signature proxy `3889/6098 = 63.78%`, and next head `0x005907d9 CTexture__LoadScriptAndDispatchByVersion`. Verified backup: `G:\GhidraBackups\BEA_20260521-114344_post_wave688_ctexture_parser_tail_verified`.

Exact token enum, yacc grammar/rule mapping, descriptor-table schema, register enum, node layout, parser stack/compile-context layouts, instruction ABI, runtime texture compiler behavior, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave688 CTexture parser tail`, `ctexture-parser-tail-wave688`, `0x0058f593 CTexture__ReadParserTerminalToken`, `0x0058fbc5 CTexture__ApplyParserReductionAction`, `0x005907d9 CTexture__LoadScriptAndDispatchByVersion`.

## Wave687 CTexture Debug Bindings Tail Read-Back Note

Wave687 CTexture debug bindings tail saved eight debug-chunk, binding cleanup, constant-stream materialization, symbol hash-table, and parser-state destructor helpers. Tag anchor: `ctexture-debug-bindings-tail-wave687`; the next queue head after this pass is `0x0058f593 CTexture__ReadParserTerminalToken`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x0058eefb` | `int __fastcall CTexture__ParseDebugChunkAndRelocateBindings(void * texture_compile_context)` | Builds a DBGU owned-node list, finds binding records in the compile context `+0x34` list with kind `0x11`, allocates relocation arrays, registers serialized chunks, shifts the pending constant stream, relocates offsets, serializes records, and reports diagnostic `0x7ee`. |
| `0x0058f1e0` | `void * __thiscall CTexture__Dtor_ReleaseBindings_DeleteOnFlag(void * this, uint delete_flags)` | Destructor wrapper calls the binding-record release helper and frees `this` when delete flag bit `0` is set. |
| `0x0058f1fc` | `void __fastcall CDXTexture__ReleaseTexturePointerArray7(void * texture_pointer_array7)` | Releases exactly seven pointer slots by calling the observed binding destructor wrapper with delete flag `1`. |
| `0x0058f219` | `int __thiscall CTexture__CreateStreamAndWriteConstantTable(void * this, void * out_memory_stream)` | Creates a memory write stream sized from `+0x5c * 4`, copies the `+0x58` constant buffer into it, and stores the stream in the caller-provided output slot. |
| `0x0058f270` | `int __thiscall CTexture__InsertSymbolNodeInHashTable(void * this, char * identifier_text, void * payload_record, int symbol_kind)` | Hashes identifier text, copies it into a new `0x24`-byte symbol node, stores payload and symbol kind, and links the node at the previous bucket head. |
| `0x0058f305` | `void * __fastcall CTexture__InitSymbolHashTables(void * symbol_table_context)` | Zeros three seven-bucket tables at `+0x00`, `+0x1c`, and `+0x38`, then clears bookkeeping fields at `+0x54`, `+0x58`, `+0x5c`, and `+0x60`. |
| `0x0058f331` | `void __fastcall CTexture__ReleaseSymbolHashTables(void * symbol_table_context)` | Releases three seven-slot tables in the observed `+0x38`, `+0x1c`, `+0x00` order. |
| `0x0058f577` | `void * __thiscall CTexture__Dtor_ReleaseParserState_DeleteOnFlag(void * this, uint delete_flags)` | Parser-state destructor wrapper releases the symbol hash tables and frees `this` when delete flag bit `0` is set. |

Wave687 read-back evidence verified `8` metadata rows, `8` tag rows, `14` xref rows, `584` instruction rows, and `8` clean decompile rows. Pre-state evidence covered the same focused exports and candidate exports for `13` adjacent debug-chunk, binding, symbol-table, parser-state, token-reader, parser-build, and reduction rows before the final eight-row tranche was selected. The pass hardened `8` signatures, made no renames, made no function-boundary changes, and made no executable-byte changes. Post-Wave687 queue telemetry is `6098` total, `3934` commented, `2164` commentless, `1216` exact-undefined signatures, `387` `param_N`, strict clean-signature proxy `3884/6098 = 63.69%`, and next head `0x0058f593 CTexture__ReadParserTerminalToken`. Verified backup: `G:\GhidraBackups\BEA_20260521-111832_post_wave687_ctexture_debug_bindings_tail_verified`.

Exact DBGU/debug chunk schema, binding-record layout, compile-context field names, symbol-node class, payload-record layout, parser-state class identity, parser token/reduction behavior, runtime texture compiler behavior, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave687 CTexture debug bindings tail`, `ctexture-debug-bindings-tail-wave687`, `0x0058eefb CTexture__ParseDebugChunkAndRelocateBindings`, `0x0058f577 CTexture__Dtor_ReleaseParserState_DeleteOnFlag`, `0x0058f593 CTexture__ReadParserTerminalToken`.

## Wave686 CTexture Channel Constant Tail Read-Back Note

Wave686 CTexture channel constant tail saved seven channel-mask, swizzle-mask, pending constant-stream, instruction operand-validation, and symbol-table finalization helpers. Tag anchor: `ctexture-channel-constant-tail-wave686`; the next queue head after this pass is `0x0058eefb CTexture__ParseDebugChunkAndRelocateBindings`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x0058e256` | `uint __thiscall CTexture__ParseChannelMaskStrict(void * this, void * token_record, int unused_context)` | Parses ordered channel mask text from `token_record+0x08`, accepts `x/y/z/w` or `r/g/b/a`, sets observed channel bitfields, returns default `0xf0000`, and reports diagnostic `0x7d3` for invalid or out-of-order masks. |
| `0x0058e309` | `uint __thiscall CTexture__ParseSwizzleMask(void * this, void * token_record, int unused_context)` | Parses up to four swizzle characters from `token_record+0x08`, accepts component aliases, packs two-bit selectors from bit `0x10`, returns default `0xe40000`, and reports diagnostic `0x7d4` for invalid forms. |
| `0x0058e3c3` | `int __thiscall CTexture__FlushPendingConstantTableWrites(void * this, void * source_location, int unused_context)` | Flushes pending constant dwords through the observed writer vtable slot, tracks source location/error fields, and advances the flushed count. |
| `0x0058e413` | `int __thiscall CTexture__EnsurePendingConstantCapacity(void * this, int additional_dword_count, int unused_context)` | Grows the pending constant dword array from an initial `0x100` dword capacity, doubling until the requested count fits and propagating allocation failure. |
| `0x0058e491` | `int __thiscall CTexture__AppendPendingConstantEntry(void * this, int constant_dword, int unused_context)` | Ensures capacity for one pending constant dword, appends `constant_dword`, increments the pending count, and propagates allocation status. |
| `0x0058e4b5` | `int __thiscall CTexture__ValidateInstructionOperandsAndReserveConstantSlots(void * this, void * instruction_record, uint unused_context)` | Validates instruction operands against observed shader-version, predicate, relative-addressing, modifier, and SUB rules, reserves pending constant slots, emits packed instruction/operand dwords, and reports diagnostics including `0x7d7`, `0x7d8`, `0x7d9`, `0x7dd`, and `0x7e3-0x7ea`. |
| `0x0058ecdb` | `int __fastcall CTexture__FinalizeSymbolTablesIntoConstantStream(void * constant_stream_context)` | Builds a FINF owned-node list, flattens/sorts three symbol hash tables, allocates `0x14`-byte symbol records, emits serialized chunks/debug-comment dwords, updates count fields, and reports diagnostic `0x7ef` when fragment info exceeds `0x8000` dwords. |

Wave686 read-back evidence verified `7` metadata rows, `7` tag rows, `13` xref rows, `511` instruction rows, and `7` clean decompile rows. Pre-state evidence covered the same focused exports and candidate exports for `11` adjacent channel, constant-stream, debug-chunk, destructor, release, and stream-write rows before the final seven-row tranche was selected. The pass hardened `7` signatures, made no renames, made no function-boundary changes, and made no executable-byte changes. Post-Wave686 queue telemetry is `6098` total, `3926` commented, `2172` commentless, `1216` exact-undefined signatures, `395` `param_N`, strict clean-signature proxy `3876/6098 = 63.56%`, and next head `0x0058eefb CTexture__ParseDebugChunkAndRelocateBindings`. Verified backup: `G:\GhidraBackups\BEA_20260521-105415_post_wave686_ctexture_channel_constant_tail_verified`.

Exact channel-mask enum ownership, swizzle enum ownership, token-record layout, constant-stream format, shader ABI encoding, FINF/debug chunk schema, runtime texture compiler behavior, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave686 CTexture channel constant tail`, `ctexture-channel-constant-tail-wave686`, `0x0058e256 CTexture__ParseChannelMaskStrict`, `0x0058ecdb CTexture__FinalizeSymbolTablesIntoConstantStream`, `0x0058eefb CTexture__ParseDebugChunkAndRelocateBindings`.

## Wave685 CTexture Parser Symbol Tail Read-Back Note

Wave685 CTexture parser symbol tail saved eight parser-symbol, seven-bucket identifier-table, semantic-value, yacc diagnostic, and shader semantic-token helpers. Tag anchor: `ctexture-parser-symbol-tail-wave685`; the next queue head after this pass is `0x0058e256 CTexture__ParseChannelMaskStrict`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x0058d419` | `int __thiscall CTexture__ParseVertexSemanticUsageToken(void * this, char * semantic_text, void * out_semantic_kind, void * out_usage_index)` | Splits vertex semantic text into an uppercase semantic prefix and optional decimal usage index, rejects usage above fifteen, maps observed D3D-style names to byte codes, and returns HRESULT-style status. |
| `0x0058d6b4` | `uint __stdcall CTexture__HashIdentifierMod7(char * identifier_text)` | Case-folds identifier text through the observed `hash * 0x13 + char` accumulator and returns the bucket modulo seven. |
| `0x0058d6f0` | `void * __thiscall CTexture__FindIdentifierInHashTable(void * this, char * identifier_text)` | Searches seven linked buckets rooted at `this+0x20`, comparing identifier strings through `lstrcmpiA`, and returns the matching node pointer or null. |
| `0x0058d722` | `void __thiscall CDXTexture__CollectHashBucketsToArray(void * this, void * out_node_array)` | Walks each of the seven hash buckets and writes linked identifier nodes into the caller-provided output array. |
| `0x0058d747` | `void __fastcall CTexture__ResetParserSemanticValue(void * semantic_value)` | Clears observed parser semantic-value fields at offsets `0x00`, `0x04`, `0x08`, `0x34`, `0x58`, `0x5c`, `0x60`, and `0x78`. |
| `0x0058d763` | `void __cdecl CTexture__ReportYaccSyntaxError(void * parser_state, char * message_format, ...)` | Varargs syntax diagnostic helper marks parser error state, formats generic unexpected-token syntax errors, and emits selected version/modifier diagnostics. |
| `0x0058d88d` | `int __thiscall CTexture__NormalizeParserResultOrReport(void * this, void * reduction_result)` | Returns non-null parser reduction results; a null result emits `internal error: production failed` once and marks the parser error fields. |
| `0x0058d8c2` | `uint __thiscall CTexture__ParseShaderSemanticToken(void * this, void * token_record)` | Parses underscore-prefixed shader semantic tokens from `token_record+0x08`, uses the observed version table at `this+0x38`, updates token fields at `+0x40/+0x44/+0x48/+0x54`, and returns failure code `0x10d` on rejected forms. |

Wave685 read-back evidence verified `8` metadata rows, `8` tag rows, `17` xref rows, `264` instruction rows, and `8` clean decompile rows. Pre-state evidence covered the same focused exports and candidate exports for `15` adjacent parser, channel-mask, swizzle, and constant-stream rows before the final eight-row tranche was selected. The pass hardened `8` signatures, marked `1` cdecl yacc diagnostic helper as varargs, made no renames, made no function-boundary changes, and made no executable-byte changes. Post-Wave685 queue telemetry is `6098` total, `3919` commented, `2179` commentless, `1216` exact-undefined signatures, `402` `param_N`, strict clean-signature proxy `3869/6098 = 63.45%`, and next head `0x0058e256 CTexture__ParseChannelMaskStrict`. Verified backup: `G:\GhidraBackups\BEA_20260521-102431_post_wave685_ctexture_parser_symbol_tail_verified`.

Exact semantic enum ownership, symbol-node structure, yacc state layout, shader semantic table schema, runtime texture compiler behavior, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave685 CTexture parser symbol tail`, `ctexture-parser-symbol-tail-wave685`, `0x0058d419 CTexture__ParseVertexSemanticUsageToken`, `0x0058d8c2 CTexture__ParseShaderSemanticToken`, `0x0058e256 CTexture__ParseChannelMaskStrict`.

## Wave684 CTexture Lexical Token Read-Back Note

Wave684 CTexture lexical token saved twenty lexical-token, literal-parser, diagnostic, sorted-key support, and adjacent CFastVB bridge helpers. Tag anchor: `ctexture-lexical-token-wave684`; the next queue head after this pass was `0x0058d419 CTexture__ParseVertexSemanticUsageToken`, later hardened by Wave685.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x0058c0e4` | `void __fastcall CFastVB__ResetConversionStatus(void * conversion_status_slot)` | Clears the first dword in a conversion-status slot without touching surrounding CFastVB state. |
| `0x0058c178` | `int __thiscall CDXTexture__InsertOrFindKeyInSortedTable(void * this, int key_value, uint * out_index, void * unused_context)` | Binary-searches the sorted key table, writes the found/insert index, grows/copies key/value arrays, and inserts missing keys with default value `1`. |
| `0x0058c457` | `int __thiscall CTexture__ParseFloatingLiteral(void * this, char * source_cursor, double * out_value, void * unused_context)` | Recognizes digit-start or dot-digit floating literals, calls the CRT double parser, writes `out_value`, and returns consumed length. |
| `0x0058c5d3` | `uint __thiscall CTexture__ParseIdentifierToken(void * this, char * source_cursor, void * out_identifier_node, void * unused_context)` | Scans alpha/underscore-led identifiers through the CRT character-class mask helper, allocates token text from `this+0x2c`, and stores the node pointer. |
| `0x0058c652` | `int __thiscall CTexture__ParseOperatorToken(void * this, char * source_cursor, char * out_operator_text, void * unused_context)` | Recognizes one- through three-character operators/punctuators, copies matched text to `out_operator_text`, and returns consumed length. |
| `0x0058c75e` | `int __thiscall CTexture__ReadTypePrefixToken_FH(void * this, char * source_cursor, void * out_token_kind, void * unused_context)` | Reads optional `f`/`h` numeric suffixes and writes observed token-kind values `7`, `6`, or default `5`. |
| `0x0058c7a4` | `int __thiscall CTexture__ParseIntegerSuffix_UL(void * this, char * source_cursor, void * out_token_kind, void * unused_context)` | Scans optional `u`/`l` integer suffixes and writes observed unsigned-long/long token-kind values. |
| `0x0058c82b` | `void __thiscall CDXTexture__SetKeyEntryModeFlags(void * this, void * key_value, int mode_value, uint unused_context)` | Inserts/finds the key-table entry and updates mode flags for `0xff`, `0x10`, or low-nibble replacement. |
| `0x0058c893` | `void __cdecl CTexture__AppendDiagnosticMessage(void * diagnostic_accumulator, void * source_location, int diagnostic_id, char * diagnostic_format, ...)` | Varargs diagnostic formatter that prefixes source text, formats error text, appends a newline, increments `+0x08`, and appends the text line. |
| `0x0058c95c` | `int __cdecl CTexture__AppendDiagnosticMessageDedup(void * diagnostic_accumulator, void * source_location, int diagnostic_id, char * diagnostic_format, ...)` | Varargs diagnostic formatter with sorted diagnostic-key dedup/mode gating, emitted flag update, error/warning counts, and append status return. |
| `0x0058cabd` | `void __thiscall CTexture__LogUnexpectedTokenError(void * this, int diagnostic_id, void * token_record, void * unused_context)` | Unexpected-token reporter chooses token text for version/integer/float/string/EOL/EOF cases and routes to the diagnostic appender. |
| `0x0058cc00` | `int __fastcall CTexture__SkipWhitespaceAndComments(void * source_cursor_state)` | Skips whitespace, newlines, continuations, line/block/semicolon comments, increments line state, and reports diagnostic `0x3e9` for unterminated block comments. |
| `0x0058cd30` | `int __thiscall CTexture__ParseHexIntegerLiteral(void * this, char * source_cursor, uint * out_value, void * unused_context)` | Parses `0x` hex literals, writes the value, warns with diagnostic `0x3ea` for the observed long-span case, and returns consumed length. |
| `0x0058cdd5` | `int __thiscall CTexture__ParseOctalIntegerLiteral(void * this, char * source_cursor, uint * out_value, void * unused_context)` | Parses leading-zero octal literals, tracks high-bit overflow, warns with diagnostic `0x3eb`, and returns consumed length. |
| `0x0058ce51` | `int __thiscall CTexture__ParseDecimalIntegerLiteral(void * this, char * source_cursor, uint * out_value, void * unused_context)` | Parses decimal literals, checks overflow against the observed `0x19999999` threshold and wrap path, warns with diagnostic `0x3ec`, and returns consumed length. |
| `0x0058cef2` | `int __thiscall CTexture__ParseEscapedCharLiteral(void * this, char * source_cursor, int * out_char_value, void * unused_context)` | Parses normal or escaped character values, including simple, octal, and hex escapes, and warns with diagnostic `0x3ef` when no escaped char is available. |
| `0x0058d088` | `int __thiscall CTexture__ParseDottedFormatAndResolveDescriptor(void * this, char * source_cursor, void * out_format_descriptor, void * unused_context)` | Flag-gated dotted format parser bounds observed fields, calls named-format descriptor lookup, stores the descriptor when found, and returns consumed length. |
| `0x0058d18b` | `int __thiscall CTexture__ParseCharLiteralToken(void * this, char * source_cursor, int * out_char_value, void * unused_context)` | Parses single-quoted character tokens through the escaped-character helper, requires the closing quote, and returns consumed length or `0`. |
| `0x0058d1ca` | `int __thiscall CTexture__ParseStringLiteralToken(void * this, char * source_cursor, void * out_string_node, void * unused_context)` | Parses quoted and flag-gated angle-bracket strings, reports diagnostics `0x3ed/0x3ee`, allocates copied payload, and returns consumed length. |
| `0x0058d2ad` | `int __thiscall CTexture__ReadNextLexToken(void * this, void * source_location, void * out_token_record, void * unused_context)` | Snapshots source/token positions, calls whitespace/literal/descriptor/identifier/operator parsers, stores token kind/span data, advances the cursor, and returns `0`. |

Wave684 read-back evidence verified `20` metadata rows, `20` tag rows, `118` xref rows, `660` instruction rows, and `20` clean decompile rows. Pre-state evidence covered the same focused exports, a `2020`-row wide instruction export, and candidate exports for `25` adjacent rows before the final twenty-row tranche was selected. The pass hardened `20` signatures, marked `2` cdecl diagnostic helpers as varargs, removed `2` address suffixes from semantic CTexture helper names, made no function-boundary changes, and made no executable-byte changes. Post-Wave684 queue telemetry is `6098` total, `3911` commented, `2187` commentless, `1216` exact-undefined signatures, `410` `param_N`, strict clean-signature proxy `3861/6098 = 63.32%`, and next head `0x0058d419 CTexture__ParseVertexSemanticUsageToken`, later hardened by Wave685. Verified backup: `G:\GhidraBackups\BEA_20260521-095848_post_wave684_ctexture_lexical_token_verified`.

Exact token enum, diagnostic catalog, lexer state layout, format descriptor ABI, runtime texture compiler behavior, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave684 CTexture lexical token`, `ctexture-lexical-token-wave684`, `0x0058c0e4 CFastVB__ResetConversionStatus`, `0x0058d2ad CTexture__ReadNextLexToken`, `0x0058d419 CTexture__ParseVertexSemanticUsageToken`.

## Wave683 CTexture Preprocessor Token Read-Back Note

Wave683 CTexture preprocessor token saved thirteen preprocessor setup, directive action, token fetch, include-frame EOF, token-list storage, diagnostic text, and line-continuation helpers. Tag anchor: `ctexture-preprocessor-token-wave683`; the next queue head after this pass is `0x0058c0e4 CFastVB__ResetConversionStatus`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x0058b1a0` | `int __thiscall CTexture__InitPreprocessorDefaultDefines(void * this, void * default_define_pairs)` | Seeds built-in `DIRECT3D`, string-table, and `DIRECT3D_VERSION/D3DX_VERSION` macro symbols, then optionally feeds caller default-define pairs through a temporary token-list context and the `#define` handler. |
| `0x0058b3c7` | `void __thiscall CTexture__ExecuteDirectiveParserAction(void * this, int action_id, uint operand_count)` | Directive-parser action dispatcher pops operand stack nodes, routes directive action ids, evaluates arithmetic/comparison/logical expression cases, and reports stack underflow, divide-by-zero, and out-of-memory paths. |
| `0x0058bd87` | `uint __thiscall CTexture__GetNextTokenWithPreprocessor(void * this, void * out_token)` | Token fetcher serves queued pushback or lexical tokens, runs the line-start directive parser, handles `__FILE__`/`__LINE__`, manages include-frame EOF pop, and skips disabled conditional blocks. |
| `0x0058c08a` | `int __fastcall CTexture__Preprocessor_PopIncludeFrameAtEof(void * preprocessor_context)` | Drains tokens until EOF, unlinks the current include-file frame from the `+0x48` chain, destroys that frame, and refreshes provider slot `+0x80`. |
| `0x0058c0ea` | `void __fastcall CTexture__TokenList_FreeChain(void * list_head_slot)` | Frees a singly linked token/text allocation chain, writing the next link back to the head slot until empty. |
| `0x0058c107` | `void * __thiscall CTexture__TokenList_PushAllocatedNode(void * this, int payload_size)` | Allocates `payload_size+4`, links the new node at the token-list head, and returns the allocated node pointer used by token callers. |
| `0x0058c129` | `void __fastcall CTexture__TokenList_InitState(void * token_list_state)` | Initializes a `0x20`-byte token-list aggregate by clearing observed head/count/buffer-like fields and setting the `+0x10` default flag/value to `1`. |
| `0x0058c149` | `void __fastcall CTexture__TokenList_ClearAndFreeBuffers(void * token_list_state)` | Frees the token-list node chain and the owned buffer/string slots observed at `+0x18` and `+0x1c`. |
| `0x0058c2b9` | `int __thiscall CTexture__AppendDiagnosticTextLine(void * this, char * text_line)` | Allocates and links a diagnostic text-line node, copies the incoming NUL-terminated payload, and increases the byte-count field. |
| `0x0058c30f` | `int __thiscall CTexture__TokenList_EmitConcatenatedText(void * this, void * out_stream_slot)` | Creates a memory write stream, writes the NUL terminator, and copies linked text-node payloads backward into the output buffer. |
| `0x0058c378` | `int __fastcall CTexture__TokenList_GetCount(void * token_list_state)` | Returns token-list state dword `+0x08`, used before emitting or consuming accumulated token/text content. |
| `0x0058c37c` | `void __fastcall CTexture__TokenList_InitState_Extended(void * preprocessor_span_state)` | Initializes the extended preprocessor span/token state and sets the logical line/counter field at `+0x1c` to `1`. |
| `0x0058c3fe` | `int __fastcall CTexture__SkipLineContinuationAndAdvance(void * source_cursor_state)` | Advances a source cursor until newline/end, treats backslash-LF and backslash-CRLF as line continuations, increments the line counter, and returns true only for a real newline. |

Wave683 read-back evidence verified `13` metadata rows, `13` tag rows, `31` xref rows, `585` instruction rows, and `13` clean decompile rows. A wider pre-instruction export verified `14313` rows for return-arity review before mutation, and candidate exports covered `18` adjacent rows before the final thirteen-row tranche was selected. The pass hardened `13` signatures, removed `8` address suffixes from semantic CTexture helper names, made no function-boundary changes, and made no executable-byte changes. Post-Wave683 queue telemetry is `6098` total, `3891` commented, `2207` commentless, `1216` exact-undefined signatures, `430` `param_N`, strict clean-signature proxy `3841/6098 = 62.99%`, and next head `0x0058c0e4 CFastVB__ResetConversionStatus`. Verified backup: `G:\GhidraBackups\BEA_20260521-092456_post_wave683_ctexture_preprocessor_token_verified`.

Exact token enum, parser action enum, source/include context layouts, stream/provider sentinel contract, token-list field names, runtime macro expansion/preprocessor behavior, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave683 CTexture preprocessor token`, `ctexture-preprocessor-token-wave683`, `0x0058b1a0 CTexture__InitPreprocessorDefaultDefines`, `0x0058c3fe CTexture__SkipLineContinuationAndAdvance`, `0x0058c0e4 CFastVB__ResetConversionStatus`.

## Wave682 CTexture Macro Symbol Read-Back Note

Wave682 CTexture macro symbol saved nine macro-symbol, quoted-string, conditional-normalization, `#define`, generic `#pragma`, and `#ifdef`/`#ifndef` helpers. Tag anchor: `ctexture-macro-symbol-wave682`; the next queue head after this pass is `0x0058b1a0 CTexture__InitPreprocessorDefaultDefines`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x0058a578` | `int __stdcall CTexture__GetSymbolNameLength(char * symbol_name)` | Current-name helper walks a non-null macro symbol string to its NUL terminator and returns the observed zero bucket/index value used by adjacent macro-symbol list helpers. |
| `0x0058a58d` | `int __thiscall CTexture__InsertOrReplaceMacroSymbol(void * this, void * macro_symbol_node)` | Inserts a macro-symbol node into the context list selected from `this+0x4c`, compares names bytewise, replaces an equal-name node by unlinking/destroying it, or links before the first greater name. |
| `0x0058a60a` | `int __thiscall CTexture__FindMacroSymbol(void * this, char * symbol_name, void * out_macro_value, void * out_macro_payload)` | Searches the context macro-symbol list selected from `this+0x4c`, stops when the sorted chain passes the requested symbol, and optionally copies node `+0x04/+0x08` payload slots to caller outputs. |
| `0x0058a67b` | `void __stdcall CTexture__EscapeQuotedStringInPlace(char * source_text, int source_length, char * destination_text)` | Scans a bounded text span, toggles quote-state on unescaped double quotes, and emits added backslashes before quote characters and in-quote backslashes when a destination buffer is provided. |
| `0x0058a6e0` | `int __thiscall CTexture__NormalizeConditionalResultOrReport(void * this, int condition_result)` | Normalizes a conditional-expression result and, when the result is zero and parser error flag `+0x2c` is clear, appends a diagnostic and marks the parser error flag. |
| `0x0058a713` | `int __thiscall CTexture__HandleDirective_Define(void * this, char * macro_name, int has_parameter_list)` | `#define` handler allocates a 0x10-byte macro-symbol node, stores the macro name, optionally parses parenthesized parameters, captures replacement tokens, and inserts/replaces the macro symbol. |
| `0x0058a981` | `int __thiscall CTexture__RemoveMacroSymbol(void * this, char * symbol_name)` | Searches the context macro-symbol list selected from `this+0x4c`, unlinks the matching node when found, clears its next link, and destroys it through the existing destructor path. |
| `0x0058a9ef` | `int __fastcall CTexture__HandleDirective_Pragma(void * directive_parser_context)` | Generic `#pragma` dispatcher reads the next token, compares identifier text against `pack_matrix` and `warning`, delegates to the specialized Wave681 handlers, otherwise skips the logical line. |
| `0x0058aa69` | `int __thiscall CTexture__HandleDirective_IfdefIfndef(void * this, char * symbol_name)` | `#ifdef`/`#ifndef` helper queries the macro-symbol table, accepts a simple payload shape with empty parameter/replacement chains and kind range 2..4, and returns the stored node `+0x18` value for that shape. |

Wave682 read-back evidence verified `9` metadata rows, `9` tag rows, `21` xref rows, `333` instruction rows, and `9` clean decompile rows. A wider pre-instruction export verified `3249` rows for return-arity review before mutation. The pass hardened `9` signatures, made no renames, no function-boundary changes, and no executable-byte changes. Post-Wave682 queue telemetry is `6098` total, `3878` commented, `2220` commentless, `1216` exact-undefined signatures, `443` `param_N`, strict clean-signature proxy `3828/6098 = 62.77%`, and next head `0x0058b1a0 CTexture__InitPreprocessorDefaultDefines`. Verified backup: `G:\GhidraBackups\BEA_20260521-085906_post_wave682_ctexture_macro_symbol_verified`.

Exact macro node layout, bucket policy, token descriptor layout, expression-value convention, ifdef/ifndef polarity, runtime macro expansion/preprocessor behavior, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave682 CTexture macro symbol`, `ctexture-macro-symbol-wave682`, `0x0058a578 CTexture__GetSymbolNameLength`, `0x0058aa69 CTexture__HandleDirective_IfdefIfndef`, `0x0058b1a0 CTexture__InitPreprocessorDefaultDefines`.

## Wave681 CTexture Directive Control Read-Back Note

Wave681 CTexture directive control saved ten diagnostic, source-location, conditional, and pragma command helpers. Tag anchor: `ctexture-directive-control-wave681`; the next queue head after this pass was `0x0058a578 CTexture__GetSymbolNameLength`, later hardened by Wave682.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x00589bd6` | `void __cdecl CTexture__ReportDirectiveParseError(void * directive_parser_context, char * diagnostic_format, ...)` | Diagnostic helper marks the parser error flag, special-cases syntax-error tokens, and formats cdecl varargs into a bounded diagnostic buffer. |
| `0x00589c82` | `int __thiscall CTexture__SetCurrentSourceLocation(void * this, int line_or_token_position, int source_location_value, int unused_context)` | Updates active include-context source-location fields and adjusts the line/token position when the current token is not end-of-line. |
| `0x00589cab` | `int __fastcall CTexture__HandleDirective_Include(void * directive_parser_context)` | `#include` handler accepts string/resource include tokens, reports syntax/provider/nesting errors, opens a new include context, and links it at parser context `+0x50`. |
| `0x00589e73` | `int __fastcall CTexture__HandleDirective_Error(void * directive_parser_context)` | `#error` handler captures the remaining logical line, folds continuations, appends a bounded diagnostic, and marks parser status/error flags. |
| `0x00589f49` | `int __thiscall CTexture__PushConditionalFrame(void * this, int condition_value, void * unused_context)` | Allocates and links a conditional frame below active include-context `+0x38`, records parent activity, and updates parser activity at `this+0x3c`. |
| `0x00589fa1` | `int __thiscall CTexture__HandleDirective_Elif(void * this, int condition_value, int unused_context)` | `#elif` handler validates the current frame, rejects `#elif` after `#else`, records branch state, and recomputes active conditional state. |
| `0x0058a014` | `int __fastcall CTexture__HandleDirective_Else(void * directive_parser_context)` | `#else` handler validates the current frame, rejects duplicate/missing-frame cases, and activates only when no prior branch fired under an active parent. |
| `0x0058a076` | `int __fastcall CTexture__HandleDirective_Endif(void * directive_parser_context)` | `#endif` handler restores parent activity, unlinks the top conditional frame, clears its child link, and destroys it. |
| `0x0058a0c6` | `int __fastcall CTexture__HandlePragma_PackMatrix(void * directive_parser_context)` | `#pragma pack_matrix` parser accepts optional row/column-major arguments, writes parser matrix-pack mode at `+0x24`, and sets the pragma-handled flag at `+0x28`. |
| `0x0058a1e3` | `int __fastcall CTexture__HandlePragma_Warning(void * directive_parser_context)` | `#pragma warning` parser handles once/error/disable/default modes, collects numeric warning ids, applies each via `CDXTexture__SetKeyEntryModeFlags`, and frees temporary arrays. |

Wave681 read-back evidence verified `10` metadata rows, `10` tag rows, `14` xref rows, `370` instruction rows, and `10` clean decompile rows. The pass hardened `10` signatures, marked one cdecl varargs helper, made no renames, no function-boundary changes, and no executable-byte changes. Post-Wave681 queue telemetry is `6098` total, `3869` commented, `2229` commentless, `1216` exact-undefined signatures, `452` `param_N`, strict clean-signature proxy `3819/6098 = 62.63%`, and next head `0x0058a578 CTexture__GetSymbolNameLength`. Verified backup: `G:\GhidraBackups\BEA_20260521-083644_post_wave681_ctexture_directive_control_verified`.

Exact parser layout, diagnostic string catalog, token enum, conditional-frame layout, source-location semantics, pragma option mapping, runtime preprocessor behavior, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave681 CTexture directive control`, `ctexture-directive-control-wave681`, `0x00589bd6 CTexture__ReportDirectiveParseError`, `0x0058a1e3 CTexture__HandlePragma_Warning`, `0x0058a578 CTexture__GetSymbolNameLength`.

## Wave680 CTexture Include Context Read-Back Note

Wave680 CTexture include context saved eighteen include-node, include-source, preprocessor-context, and directive-parser helpers. Tag anchor: `ctexture-include-context-wave680`; the next queue head after this pass is `0x00589bd6 CTexture__ReportDirectiveParseError`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x00589367` | `void __fastcall CTexture__ReleaseIncludeNodeTreeRecursive(void * include_node)` | Recursive include-node release helper visits payload slots, follows child link `+0x0c`, and frees child nodes. |
| `0x0058939b` | `void * __thiscall CTexture__IncludeNodeDtor(void * this, int delete_flags, int unused_context)` | Scalar-deleting destructor wrapper calls the recursive include-node release helper and frees `this` when `delete_flags` bit 0 is set. |
| `0x005893b7` | `void __thiscall CTexture__IncludeNodeCtor(void * this, void * primary_payload, int secondary_payload, int unused_context)` | Include-node constructor clears link slots and stores the observed primary/secondary payload fields. |
| `0x005893d1` | `void __fastcall CTexture__FreeChildIncludeNodeChainRecursive(void * include_node)` | Child-chain cleanup follows the `+0x0c` child link recursively and frees each child node without the payload destructor path. |
| `0x005893e9` | `void * __thiscall CTexture__IncludeNodeChain_scalar_deleting_dtor(void * this, int delete_flags, int unused_context)` | Scalar-deleting destructor wrapper for child-only include-node chains calls the child-chain cleanup helper. |
| `0x00589405` | `void * __fastcall CTexture__PreprocessorContextCtor(void * preprocessor_context)` | Initializes token-list state, mapped-file context, GDI bitmap record, source-buffer, and child-context slots. |
| `0x00589438` | `void __fastcall CTexture__CleanupIncludeContextRecursive(void * preprocessor_context)` | Recursively tears down include-node chains, child contexts, provider-backed buffers, GDI object slot, and mapped-file state. |
| `0x0058948d` | `void * __thiscall CTexture__IncludeContextDtor(void * this, int delete_flags, int unused_context)` | Scalar-deleting destructor wrapper for include contexts calls the recursive include-context cleanup helper. |
| `0x005894a9` | `int CTexture__OpenIncludeSourceAndInitBuffer(void)` | Locked-storage include-source helper records provider state, handles path conversion, opens mapped-file or provider-backed input, and initializes buffer cursor ranges. |
| `0x00589650` | `int CTexture__InitBufferFromMemorySpan(void)` | Locked-storage memory-span helper records caller buffer pointer/count and delegates to shared buffer cursor initialization. |
| `0x00589689` | `void __fastcall CTexture__FreeIncludeFileChainRecursive(void * include_file_node)` | Include-file chain cleanup follows the next link recursively and frees each linked include-file node. |
| `0x005896a1` | `void * __thiscall CTexture__IncludeFileChainDtor(void * this, int delete_flags, int unused_context)` | Scalar-deleting destructor wrapper for include-file chains calls the recursive include-file cleanup helper. |
| `0x005896bd` | `void * __fastcall CTexture__DirectiveParserContextCtor(void * directive_parser_context)` | Initializes directive-parser state, snapshots current locale, forces C locale when needed, and saves/masks FPU control state. |
| `0x00589762` | `void __fastcall CTexture__DirectiveParserContextDtor(void * directive_parser_context)` | Releases parser payloads and include chains, restores saved locale/FPU state, and clears token-list buffers. |
| `0x00589802` | `int __thiscall CTexture__PushPreprocessorStateNode(void * this, int state_value, int unused_context)` | Allocates and links a preprocessor state node, mirrors the state value, and returns zero or allocation failure. |
| `0x00589846` | `int __thiscall CTexture__GetCurrentSourceLocation(void * this, void * out_primary_location, void * out_secondary_location, void * unused_context)` | Copies active include-context source-location fields into non-null output slots. |
| `0x0058986b` | `int __thiscall CTexture__GetActiveIncludeRange(void * this, void * out_range_start, void * out_range_length, void * unused_context)` | Walks terminal child include context and writes guarded source range start/length outputs. |
| `0x005898a4` | `int __fastcall CTexture__MapLexTokenToPreprocessorToken(void * directive_parser_context)` | Maps lexical token records into preprocessor token codes, including directive keywords, operator pairs, `defined()`, inactive conditional handling, error/end-token state, and fallback token classes. |

Wave680 read-back evidence verified `18` metadata rows, `18` tag rows, `33` xref rows, `1458` instruction rows, and `18` clean decompile rows. The pass hardened `16` signatures and preserved two locked-storage signatures, made no renames, no function-boundary changes, and no executable-byte changes. Post-Wave680 queue telemetry is `6098` total, `3859` commented, `2239` commentless, `1216` exact-undefined signatures, `462` `param_N`, strict clean-signature proxy `3809/6098 = 62.46%`, and next head `0x00589bd6 CTexture__ReportDirectiveParseError`. Verified backup: `G:\GhidraBackups\BEA_20260521-080705_post_wave680_ctexture_include_context_verified`.

Exact node/context/parser layouts, provider ABI, token enum, path encoding policy, source-location/range semantics, runtime preprocessor behavior, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave680 CTexture include context`, `ctexture-include-context-wave680`, `0x00589367 CTexture__ReleaseIncludeNodeTreeRecursive`, `0x005898a4 CTexture__MapLexTokenToPreprocessorToken`, `0x00589bd6 CTexture__ReportDirectiveParseError`.

## Wave675 Texel Codec Continuation Read-Back Note

Wave675 texel codec continuation saved three CTexture-labelled unpack/read/write helpers alongside CFastVB profile, scratch row-window, codec profile, and destructor-like rows in [`FastVB.cpp`](../FastVB.cpp/_index.md). Tag anchor: `texel-codec-continuation-wave675`; the next queue head after this pass is `0x00587dee CFastVB__InitTexelUnpackVTable_005ea264`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x005869b0` | `void __thiscall CTexture__UnpackTexels_Bits16_16_16_ToFloat4(void * this, uint source_x, uint source_y, float * destination_vec4_array, int unused_context)` | 16-16-16 unpacker expands three 16-bit source lanes into RGB float4 output, writes alpha `1.0`, and reaches the observed key-color/post-process gates. |
| `0x005876ab` | `void __thiscall CTexture__WriteTexelBlockWithQuadCache(void * this, uint block_x, uint block_y, float * source_vec4_array, int unused_context)` | Write helper maintains a 4x4 quad cache, lazily decodes needed source blocks, stores caller vec4 data into cache rows, and invokes the configured encode callback when a quad becomes complete. |
| `0x00587af0` | `void __thiscall CTexture__ReadTexelBlockWithQuadCache(void * this, uint block_x, uint block_y, float * destination_vec4_array, int unused_context)` | Read helper lazily fills a cached 4x4 decoded block via the configured decode callback, copies requested vec4 rows to the destination, then applies key-color zeroing and post-process gates. |

Wave675 read-back evidence verified `25` metadata rows, `25` tag rows, `52` xref rows, `1125` instruction rows, and `25` clean decompile rows across `0x005869b0 CTexture__UnpackTexels_Bits16_16_16_ToFloat4` through `0x00587dd6 CFastVB__TexelUnpackProfileRegistry_005ea254__ctor`. Post-Wave675 queue telemetry is `6098` total, `3821` commented, `2277` commentless, `1217` exact-undefined signatures, `496` `param_N`, strict clean-signature proxy `3771/6098 = 61.84%`, and next head `0x00587dee CFastVB__InitTexelUnpackVTable_005ea264`. Verified backup: `G:\GhidraBackups\BEA_20260521-055935_post_wave675_texel_codec_continuation_verified`.

Exact profile ABI, descriptor layout, FourCC semantics, DXT block ABI, quad-cache contract, runtime texture output behavior, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave675 texel codec continuation`, `texel-codec-continuation-wave675`, `0x005869b0 CTexture__UnpackTexels_Bits16_16_16_ToFloat4`, `0x00587dd6 CFastVB__TexelUnpackProfileRegistry_005ea254__ctor`, `0x00587dee CFastVB__InitTexelUnpackVTable_005ea264`.

## Wave674 Texel Unpack Tail Read-Back Note

Wave674 texel unpack tail saved three CTexture-labelled unpackers alongside CFastVB profile/unpacker rows in [`FastVB.cpp`](../FastVB.cpp/_index.md) and four CDXTexture rows in [`DXTexture.cpp`](../DXTexture.cpp/_index.md). Tag anchor: `texel-unpack-tail-wave674`; the next queue head after this pass is `0x005869b0 CTexture__UnpackTexels_Bits16_16_16_ToFloat4`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x005860ba` | `void __thiscall CTexture__UnpackTexels_Signed16_16_ToFloat4_RG(void * this, uint source_x, uint source_y, float * destination_vec4_array, int unused_context)` | Signed 16-16 RG unpacker advances two 16-bit words per texel, sign-scales R/G with the observed `-0x8000` correction, and fills Z/A with `1.0`. |
| `0x00586438` | `void __thiscall CTexture__UnpackTexels_NormalXY_Signed8_8_ReconstructZ(void * this, uint source_x, uint source_y, float * destination_vec4_array, int unused_context)` | Normal XY unpacker sign-scales two signed bytes, reconstructs Z with `sqrt(max(0, 1 - x*x - y*y))`, and writes alpha `1.0`. |
| `0x0058686f` | `void __thiscall CTexture__UnpackTexels_CopyRaw128(void * this, uint source_x, uint source_y, float * destination_vec4_array, int unused_context)` | Raw 128-bit copy unpacker copies 16 bytes per texel into the destination vector rows before the observed key-color/post-process gates. |

Wave674 read-back evidence verified `25` metadata rows, `25` tag rows, `25` xref rows, `1125` instruction rows, and `25` clean decompile rows across `0x0058609e CFastVB__TexelUnpackProfile_005ea020__ctor` through `0x00586994 CFastVB__InitTexelUnpackVTable_005ea118`. Post-Wave674 queue telemetry is `6098` total, `3796` commented, `2302` commentless, `1217` exact-undefined signatures, `521` `param_N`, strict clean-signature proxy `3746/6098 = 61.43%`, and next head `0x005869b0 CTexture__UnpackTexels_Bits16_16_16_ToFloat4`. Verified backup: `G:\GhidraBackups\BEA_20260521-052857_post_wave674_texel_unpack_tail_verified`.

Exact profile ABI, signed-normal format contracts, raw-copy destination contract, runtime texture output behavior, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave674 texel unpack tail`, `texel-unpack-tail-wave674`, `0x0058609e CFastVB__TexelUnpackProfile_005ea020__ctor`, `0x00586994 CFastVB__InitTexelUnpackVTable_005ea118`, `0x005869b0 CTexture__UnpackTexels_Bits16_16_16_ToFloat4`.

## Wave673 Texel Unpack Continuation Read-Back Note

Wave673 texel unpack continuation saved three CTexture-labelled unpackers alongside CFastVB profile/unpacker rows in [`FastVB.cpp`](../FastVB.cpp/_index.md) and two CDXTexture rows in [`DXTexture.cpp`](../DXTexture.cpp/_index.md). Tag anchor: `texel-unpack-continuation-wave673`; the next queue head after this pass is `0x0058609e CFastVB__TexelUnpackProfile_005ea020__ctor`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x0058579b` | `void __thiscall CTexture__UnpackTexels_Bits444ToFloat4_AlphaOne(void * this, uint source_x, uint source_y, float * destination_vec4_array, int unused_context)` | 4-4-4 alpha-one unpacker advances two bytes per texel, writes R from byte1 low nibble, G from byte0 high nibble, B from byte0 low nibble, and A=`1.0`, then applies the observed key-color/post-process gates. |
| `0x0058586b` | `void __thiscall CTexture__UnpackTexels_PaletteIndexA8ToFloat4(void * this, uint source_x, uint source_y, float * destination_vec4_array, int unused_context)` | Palette-index plus A8 unpacker copies a vec4 palette entry from `this+0x38` indexed by byte0 and overwrites alpha from byte1 using the observed 8-bit scale. |
| `0x00585cb0` | `void __thiscall CTexture__UnpackTexels_Signed8_8_ToFloat4_RG(void * this, uint source_x, uint source_y, float * destination_vec4_array, int unused_context)` | Signed 8-8 RG unpacker sign-scales byte0/byte1 into R/G with the observed `-128` adjustment and fills Z/A with `1.0`. |

Wave673 read-back evidence verified `25` metadata rows, `25` tag rows, `67` xref rows, `1125` instruction rows, and `25` clean decompile rows across `0x0058577f CFastVB__TexelUnpackProfile_005e9f3c__ctor` through `0x00585fa3 CFastVB__UnpackTexels_Signed8_8_8_8_ToFloat4`. Post-Wave673 queue telemetry is `6098` total, `3771` commented, `2327` commentless, `1217` exact-undefined signatures, `546` `param_N`, strict clean-signature proxy `3721/6098 = 61.02%`, and next head `0x0058609e CFastVB__TexelUnpackProfile_005ea020__ctor`. Verified backup: `G:\GhidraBackups\BEA_20260521-045554_post_wave673_texel_unpack_continuation_verified`.

Exact profile ABI, palette layout, format-table contract, signed-normal format contracts, runtime texture output behavior, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave673 texel unpack continuation`, `texel-unpack-continuation-wave673`, `0x0058577f CFastVB__TexelUnpackProfile_005e9f3c__ctor`, `0x00585fa3 CFastVB__UnpackTexels_Signed8_8_8_8_ToFloat4`, `0x0058609e CFastVB__TexelUnpackProfile_005ea020__ctor`.

## Wave672 Texel Unpack Head Read-Back Note

Wave672 texel unpack head saved three CTexture-labelled unpackers alongside nine CFastVB rows in [`FastVB.cpp`](../FastVB.cpp/_index.md), one current-owner `CMeshCollisionVolume` row in [`MeshCollisionVolume.cpp`](../MeshCollisionVolume.cpp/_index.md), and three CDXTexture rows in [`DXTexture.cpp`](../DXTexture.cpp/_index.md). Tag anchor: `texel-unpack-head-wave672`; the next queue head after this pass is `0x0058577f CFastVB__TexelUnpackProfile_005e9f3c__ctor`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x00584b5f` | `void __thiscall CTexture__UnpackTexels_Bgr8ToFloat4(void * this, uint source_x, uint source_y, float * destination_vec4_array, int unused_context)` | BGR8 unpacker computes the source pointer from `+0x1058/+0x105c/+0x20`, uses `+0x106c` as the byte span, writes R/G/B from bytes `2/1/0`, forces alpha to `1.0`, then optionally runs key-color zeroing and post-process/gamma-or-square. |
| `0x00584c04` | `void __thiscall CTexture__UnpackTexels_Bgra8ToFloat4(void * this, uint source_x, uint source_y, float * destination_vec4_array, int unused_context)` | BGRA8 unpacker writes R/G/B/A from bytes `2/1/0/3` scaled by the observed 8-bit factor through the shared source/count/gate fields. |
| `0x00584cc3` | `void __thiscall CTexture__UnpackTexels_Bgr8ToFloat4_AlphaOne(void * this, uint source_x, uint source_y, float * destination_vec4_array, int unused_context)` | Current-name BGR8 alpha-one unpacker advances through 4-byte source records in the retail decompile, writes R/G/B from bytes `2/1/0`, and forces alpha to `1.0`; exact current-name/stride rationale remains open. |

Wave672 read-back evidence verified `16` metadata rows, `16` tag rows, `16` xref rows, `1616` instruction rows, and `16` clean decompile rows across `0x00584b5f CTexture__UnpackTexels_Bgr8ToFloat4` through `0x005856b8 CDXTexture__UnpackTexels_Bits332A8ToFloat4`. Post-Wave672 queue telemetry is `6098` total, `3746` commented, `2352` commentless, `1217` exact-undefined signatures, `571` `param_N`, strict clean-signature proxy `3696/6098 = 60.61%`, and next head `0x0058577f CFastVB__TexelUnpackProfile_005e9f3c__ctor`. Verified backup: `G:\GhidraBackups\BEA_20260521-042809_post_wave672_texel_unpack_head_verified`.

Exact profile ABI, format-table contract, current owner/layout identity, lane-order enum contracts, runtime texture output behavior, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave672 texel unpack head`, `texel-unpack-head-wave672`, `0x00584b5f CTexture__UnpackTexels_Bgr8ToFloat4`, `0x005856b8 CDXTexture__UnpackTexels_Bits332A8ToFloat4`, `0x0058577f CFastVB__TexelUnpackProfile_005e9f3c__ctor`.

## Wave671 Texel Callback/Raw Packers Read-Back Note

Wave671 texel callback/raw packers saved one CTexture-labelled no-dither-named packer alongside seven CDXTexture rows documented in [`DXTexture.cpp`](../DXTexture.cpp/_index.md). Tag anchor: `texel-callback-raw-packers-wave671`; the next queue head after this pass is `0x00584b5f CTexture__UnpackTexels_Bgr8ToFloat4`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x00584a4c` | `void __thiscall CTexture__PackTexels_NoDither_Bits16_16_16(void * this, uint output_x, uint output_y, float * source_vec4_array, int unused_context)` | Currently named no-dither 16-16-16 packer optionally runs domain conversion and normalization, reads the shared `+0x34` dither-table term in the current decompile, then writes three 16-bit words per texel from observed source lanes `+8`, `+4`, and `+0`. |

Wave671 read-back evidence verified `8` metadata rows, `8` tag rows, `9` xref rows, `840` instruction rows, and `8` clean decompile rows across `0x00584724 CDXTexture__PackTexels_CallbackPerTexel_RepeatA` through `0x00584a4c CTexture__PackTexels_NoDither_Bits16_16_16`. Post-Wave671 queue telemetry is `6098` total, `3730` commented, `2368` commentless, `1217` exact-undefined signatures, `587` `param_N`, strict clean-signature proxy `3680/6098 = 60.35%`, and next head `0x00584b5f CTexture__UnpackTexels_Bgr8ToFloat4`. Verified backup: `G:\GhidraBackups\BEA_20260521-035844_post_wave671_texel_callback_raw_packers_verified`.

Exact callback ABI, selector contract, byte-count contract, source-record contract, exact no-dither naming rationale, luminance/alpha contract, lane-order contract, runtime texture output behavior, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave671 texel callback/raw packers`, `texel-callback-raw-packers-wave671`, `0x00584724 CDXTexture__PackTexels_CallbackPerTexel_RepeatA`, `0x00584a4c CTexture__PackTexels_NoDither_Bits16_16_16`, `0x00584b5f CTexture__UnpackTexels_Bgr8ToFloat4`.

## Wave670 Texel Packer Continuation Read-Back Note

Wave670 texel packer continuation saved six CTexture-labelled texel packers alongside three CFastVB rows documented in [`FastVB.cpp`](../FastVB.cpp/_index.md). Tag anchor: `texel-packer-continuation-wave670`; the next queue head after this pass is `0x00584724 CDXTexture__PackTexels_CallbackPerTexel_RepeatA`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x00583c8e` | `void __thiscall CTexture__PackTexels_Dither_Bits8_8(void * this, uint output_x, uint output_y, float * source_vec4_array, int unused_context)` | Dithered 8-8-style packer writes one 16-bit output from two rounded 8-bit source lanes using observed output pointer fields `+0x1058/+0x105c/+0x20`, count `+0x1060`, dither table `+0x34`, optional domain conversion `+0x1050`, and optional normalization `+0x10`. |
| `0x00583d89` | `void __thiscall CTexture__PackTexels_Dither_Bits5_5_5(void * this, uint output_x, uint output_y, float * source_vec4_array, int unused_context)` | Dithered 5-5-5-style word packer writes one 16-bit output from three rounded source lanes through the shared packer gates. |
| `0x00583eb3` | `void __thiscall CTexture__PackTexels_Dither_Bits8_8_8_Alt(void * this, uint output_x, uint output_y, float * source_vec4_array, int unused_context)` | Alternate dithered 8-8-8-style packer writes one 32-bit store from three rounded source lanes while preserving observed lane order. |
| `0x00583fe5` | `void __thiscall CTexture__PackTexels_Dither_Bits8_8_8_8_Alt(void * this, uint output_x, uint output_y, float * source_vec4_array, int unused_context)` | Alternate dithered 8-8-8-8-style packer writes one 32-bit texel from four rounded source lanes. |
| `0x00584535` | `void __thiscall CTexture__PackTexels_Dither_Bits8_8_FromAuxLookup(void * this, uint output_x, uint output_y, float * source_vec4_array, int unused_context)` | Dithered 8-8-style packer calls the observed indirect helper `0x00575d99` to populate two local float lanes, then writes one 16-bit output. |
| `0x0058463a` | `void __thiscall CTexture__PackTexels_Dither_L16_Alt(void * this, uint output_x, uint output_y, float * source_vec4_array, int unused_context)` | Alternate dithered luminance packer writes one 16-bit output from weighted RGB lanes using constants at `0x005e72dc/0x005e72e0/0x005e72e4`. |

Wave670 read-back evidence verified `9` metadata rows, `9` tag rows, `9` xref rows, `729` instruction rows, and `9` clean decompile rows across `0x00583c8e CTexture__PackTexels_Dither_Bits8_8` through `0x0058463a CTexture__PackTexels_Dither_L16_Alt`. Post-Wave670 queue telemetry is `6098` total, `3722` commented, `2376` commentless, `1217` exact-undefined signatures, `595` `param_N`, strict clean-signature proxy `3672/6098 = 60.22%`, and next head `0x00584724 CDXTexture__PackTexels_CallbackPerTexel_RepeatA`. Verified backup: `G:\GhidraBackups\BEA_20260521-033410_post_wave670_texel_packer_continuation_verified`.

Exact dither table provenance, exact no-dither naming rationale, texel-pack callback ABI, channel-order enum contracts, indirect helper target, auxiliary lookup contract, luminance contract, runtime texture output behavior, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave670 texel packer continuation`, `texel-packer-continuation-wave670`, `0x00583c8e CTexture__PackTexels_Dither_Bits8_8`, `0x0058463a CTexture__PackTexels_Dither_L16_Alt`, `0x00584724 CDXTexture__PackTexels_CallbackPerTexel_RepeatA`.

## Wave669 Dither Packer Tail Read-Back Note

Wave669 dither packer tail saved two CTexture-labelled luminance packers alongside CDXTexture and CFastVB packers documented in [`DXTexture.cpp`](../DXTexture.cpp/_index.md) and [`FastVB.cpp`](../FastVB.cpp/_index.md). Tag anchor: `dither-packer-tail-wave669`; the next queue head after this pass is `0x00583c8e CTexture__PackTexels_Dither_Bits8_8`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x00583a94` | `void __thiscall CTexture__PackTexels_Dither_A4L4(void * this, uint output_x, uint output_y, float * source_vec4_array, int unused_context)` | Dithered A4L4-style packer writes one byte with dithered alpha in the high nibble and weighted RGB luminance in the low nibble using the observed 4-bit scale. |
| `0x00583ba4` | `void __thiscall CTexture__PackTexels_Dither_L16(void * this, uint output_x, uint output_y, float * source_vec4_array, int unused_context)` | Dithered luminance packer writes one 16-bit output from weighted RGB lanes using the observed 16-bit scale and shared dither term. |

Wave669 read-back evidence verified `12` metadata rows, `12` tag rows, `12` xref rows, `444` instruction rows, and `12` clean decompile rows across `0x00582ef8 CDXTexture__PackTexels_Dither_Bits2_10_10_10` through `0x00583ba4 CTexture__PackTexels_Dither_L16`. Post-Wave669 queue telemetry is `6098` total, `3713` commented, `2385` commentless, `1217` exact-undefined signatures, `604` `param_N`, strict clean-signature proxy `3663/6098 = 60.07%`, and next head `0x00583c8e CTexture__PackTexels_Dither_Bits8_8`. Verified backup: `G:\GhidraBackups\BEA_20260521-030557_post_wave669_dither_packer_tail_verified`.

Exact luminance contract, dither table provenance, texel-pack callback ABI, runtime texture output behavior, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave669 dither packer tail`, `dither-packer-tail-wave669`, `0x00582ef8 CDXTexture__PackTexels_Dither_Bits2_10_10_10`, `0x00583ba4 CTexture__PackTexels_Dither_L16`, `0x00583c8e CTexture__PackTexels_Dither_Bits8_8`.

## Wave668 Dither Packer Head Read-Back Note

Wave668 dither packer head saved the CTexture-labelled decoded-texel post-process row and four CTexture-labelled dither packers, alongside seven CFastVB-labelled packers documented in [`FastVB.cpp`](../FastVB.cpp/_index.md). Tag anchor: `dither-packer-head-wave668`; the next queue head after this pass is `0x00582ef8 CDXTexture__PackTexels_Dither_Bits2_10_10_10`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x0058210e` | `void __thiscall CTexture__PostProcessDecodedTexels_GammaOrSquare(void * this, float * texel_vec4_array, uint unused_context)` | Post-processes count-controlled decoded vec4 texels using count `+0x1060`, mode `+0x08`, and gamma/square selector `+0x14`; modes `1/4` transform RGB lanes while other modes transform alpha. |
| `0x00582a99` | `void __thiscall CTexture__PackTexels_Dither_Bits332(void * this, uint output_x, uint output_y, float * source_vec4_array, int unused_context)` | Dithered callback at table slot `0x005e9fb4`; writes one 8-bit 3-3-2 packed texel from RGB lanes using observed 3-bit/2-bit scale constants plus dither. |
| `0x00582bbe` | `void __thiscall CTexture__PackTexels_Dither_Bits8(void * this, uint output_x, uint output_y, float * source_vec4_array, int unused_context)` | Dithered callback at table slot `0x005e9fc4`; writes one 8-bit single-channel output from the observed source lane at `+0x0c`. |
| `0x00582c8a` | `void __thiscall CTexture__PackTexels_Dither_Bits565(void * this, uint output_x, uint output_y, float * source_vec4_array, int unused_context)` | Dithered callback at table slot `0x005e9fd8`; writes 16-bit packed output with the observed 5/6/5-like scale mix and source-lane participation shown in decompile. |
| `0x00582dd3` | `void __thiscall CTexture__PackTexels_Dither_Bits444(void * this, uint output_x, uint output_y, float * source_vec4_array, int unused_context)` | Dithered callback at table slot `0x005e9fe8`; writes 16-bit 4-4-4 packed output by rounding three source lanes with observed 4-bit scale constants and packing nibbles. |

Wave668 read-back evidence verified `12` metadata rows, `12` tag rows, `52` xref rows, `444` instruction rows, and `12` clean decompile rows across the dither-packer head cluster from `0x0058210e CTexture__PostProcessDecodedTexels_GammaOrSquare` through `0x00582dd3 CTexture__PackTexels_Dither_Bits444`. Post-Wave668 queue telemetry is `6098` total, `3701` commented, `2397` commentless, `1217` exact-undefined signatures, `616` `param_N`, strict clean-signature proxy `3651/6098 = 59.87%`, and next head `0x00582ef8 CDXTexture__PackTexels_Dither_Bits2_10_10_10`. Verified backup: `G:\GhidraBackups\BEA_20260521-024019_post_wave668_dither_packer_head_verified`.

Exact dither table provenance, texel-pack callback ABI, channel-order enum contracts, gamma/curve identity, runtime texture output behavior, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave668 dither packer head`, `dither-packer-head-wave668`, `0x0058210e CTexture__PostProcessDecodedTexels_GammaOrSquare`, `0x00582dd3 CTexture__PackTexels_Dither_Bits444`, `0x00582ef8 CDXTexture__PackTexels_Dither_Bits2_10_10_10`.

## Wave661 CTexture Label Correction Context

Wave661 quaternion/matrix correction confirmed that two rows previously carrying `CTexture` labels belong in the owner-neutral math dispatch island:

| Address | Corrected Name | Saved Signature | Evidence |
|---------|----------------|-----------------|----------|
| `0x0057923a` | `Math__BuildMatrix4x4FromEulerAngles` | `void * __stdcall Math__BuildMatrix4x4FromEulerAngles(void * out_matrix4x4, float angle_x, float angle_y, float angle_z)` | Source/default dispatch-table slot `0x006570f0`; builds a quaternion local, then calls the quaternion-to-matrix dispatch thunk. |
| `0x00579527` | `Math__BuildProjectiveMatrix4x4FromPlane` | `void __stdcall Math__BuildProjectiveMatrix4x4FromPlane(void * out_matrix4x4, void * plane_vec4)` | Source/default dispatch-table slot `0x006570bc`; calls the slot-21 vector-normalization dispatch helper and writes a 4x4 projective matrix pattern. |

The same `quaternion-matrix-wave661` pass corrected `0x00577a3e Math__BuildQuaternionFromEulerAngles` and hardened `0x00579184 CFastVB__NormalizeQuaternionCopy`; details live in [`Math.cpp`](../Math.cpp/_index.md) and [`FastVB.cpp`](../FastVB.cpp/_index.md). Queue after Wave661 is `6098` total, `3623` commented, `2475` commentless, `1217` exact-undefined signatures, `694` `param_N`, comment-backed proxy `3623/6098 = 59.41%`, strict clean-signature proxy `3573/6098 = 58.59%`, and next head `0x00579b39 CDXTexture__LookupNamedFormatDescriptor`. Verified backup: `G:\GhidraBackups\BEA_20260520-234153_post_wave661_quaternion_matrix_verified`.

Exact plane equation convention, slot-21 fourth-lane behavior, matrix layout, runtime math correctness, BEA patching, and rebuild parity remain unproven. The `quaternion-matrix-wave661` tag marks saved static Ghidra evidence only.

## Wave660 CTexture Dispatch Context

Wave660 math dispatch continuation retained `0x005776a5 CTexture__DispatchPtr00656fd0_WithInit` at the head of the tranche while documenting its deferred argument/storage contract:

| Address | Name | Saved Signature | Evidence |
|---------|------|-----------------|----------|
| `0x005776a5` | `CTexture__DispatchPtr00656fd0_WithInit` | `void __stdcall CTexture__DispatchPtr00656fd0_WithInit(int slot_arg0, int slot_arg1, int slot_arg2, int slot_arg3)` | Runtime dispatch-table slot `0x00656fd0`; source/default slot 40 points elsewhere (`0x006570f0 -> 0x0057923a CTexture__DispatchMatrixOp00656f94_WithPostOp`), so the exact storage/argument contract stays deferred. |

The same Wave660 pass saved the adjacent quaternion and owner-neutral math dispatch rows under [`FastVB.cpp`](../FastVB.cpp/_index.md) and [`Math.cpp`](../Math.cpp/_index.md). Dry/apply/final dry reported `updated=0 skipped=17 created=0 would_create=2 body_set=0 would_set_body=2 renamed=0 would_rename=4 signature_updated=15 missing=0 bad=0`, then `updated=17 skipped=0 created=2 would_create=0 body_set=2 would_set_body=0 renamed=4 would_rename=0 signature_updated=13 missing=0 bad=0`, then `updated=0 skipped=17 created=0 would_create=0 body_set=0 would_set_body=0 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`. Queue after Wave660 is `6098` total, `3619` commented, `2479` commentless, `1217` exact-undefined signatures, `698` `param_N`, comment-backed proxy `3619/6098 = 59.35%`, strict clean-signature proxy `3569/6098 = 58.53%`, and next head `0x00579184 CFastVB__NormalizeQuaternionCopy`. Verified backup: `G:\GhidraBackups\BEA_20260520-230154_post_wave660_math_dispatch_verified`.

Exact vector/matrix storage contract, CTexture dispatch-table replacement behavior, runtime math correctness, BEA patching, and rebuild parity remain unproven. The `math-dispatch-wave660` tag marks saved static Ghidra evidence only.

## Wave654 CTexture/RB-tree helper hardening (2026-05-20)

Wave654 saved signatures, comments, and tags for eight adjacent sentinel-backed CTexture-labelled tree/list helpers:

| Address | Name | Saved Signature | Evidence |
|---------|------|-----------------|----------|
| `0x00572e40` | `CTexture__DestroyNodeTreeAndStorage` | `void __fastcall CTexture__DestroyNodeTreeAndStorage(void * tree_state)` | Tears down tree/list state, erases or recursively frees nodes, frees the header, and decrements the shared sentinel `DAT_009d0c44` refcount. |
| `0x005738e0` | `CTexture__EraseNodeFromTree` | `void __thiscall CTexture__EraseNodeFromTree(void * this, void * unused_out_slot, void * node, void * unused_context)` | Removes a node, updates header min/max/root links, and performs red-black delete fixup rotations/recolors. |
| `0x00573cc0` | `CTexture__DestroySubtreeRecursive` | `void __stdcall CTexture__DestroySubtreeRecursive(void * node)` | Walks right children first, frees each node, then advances through left links until the shared sentinel is reached. |
| `0x00574080` | `CTexture__WalkNodeListUntilSentinel` | `void __cdecl CTexture__WalkNodeListUntilSentinel(void * node_slot)` | Follows first-child/next links until `DAT_009d0c44`; no concrete iterator side effect is claimed. |
| `0x005740a0` | `CTexture__RotateTreeLeft` | `void __thiscall CTexture__RotateTreeLeft(void * this, void * pivot_node)` | Pivots `pivot_node`'s right child up and updates parent/root/header links. |
| `0x00574100` | `CTexture__InitTreeNodeParentAndKey` | `void * __stdcall CTexture__InitTreeNodeParentAndKey(void * parent_node, int node_color)` | Allocates a 0x14-byte node, stores `parent_node` at `+0x04`, stores `node_color` at `+0x10`, and returns the new node in `EAX`. |
| `0x00574120` | `CTexture__TreeIteratorNext` | `void __fastcall CTexture__TreeIteratorNext(void * iterator_slot)` | Advances the iterator slot to the in-order successor using left/right/parent links and the shared sentinel. |
| `0x00574180` | `CTexture__TreeIteratorPrev` | `void __fastcall CTexture__TreeIteratorPrev(void * iterator_slot)` | Retreats the iterator slot to the in-order predecessor using right/left/parent links and the shared sentinel. |

Read-back evidence: dry/apply/final dry reported `updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=8 missing=0 bad=0`, then `updated=8 skipped=0 renamed=0 would_rename=0 signature_updated=8 missing=0 bad=0`, then `updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`. Post exports verified `8` metadata rows, `8` tag rows, `13` xref rows, `392` instruction rows, and `8` clean decompile rows. Queue after Wave654 is `6093` total, `3551` commented, `2542` commentless, `1217` exact-undefined signatures, `757` `param_N`, comment-backed proxy `3551/6093 = 58.28%`, strict clean-signature proxy `3501/6093 = 57.46%`, and next head `0x00572f00 CFastVB__InitDwordSpanBuilderState_00572f00`. Verified backup: `G:\GhidraBackups\BEA_20260520-195520_post_wave654_ctexture_tree_verified`.

Several xrefs for this helper island come from adjacent `CFastVB` red-black tree routines. Treat the retained CTexture prefix as saved Ghidra naming evidence, not proof of exact owner/template identity, concrete node layout, runtime texture behavior, runtime CFastVB tree behavior, BEA patching, or rebuild parity.

## Wave513 Static Read-Back (2026-05-17)

Wave513 hardened the signatures and bounded comments for the texture cache/lifecycle head and adjacent TGA helpers. `CTexture__FindTexture` is now saved as:

```cpp
void * __cdecl CTexture__FindTexture(char * name, int texture_type, int load_arg, int required_mip_count, int allow_fallback, int load_flags)
```

The claim is intentionally narrow: the body walks `DAT_0083d9b0`, matches name/type/mipmap count, allocates a `0x158`-byte `CTexture` on miss, forwards the load arguments to vtable slot `+0x14`, and returns `DAT_0083d9b4` only when loading fails and fallback is allowed. The pass also documented the default-texture bootstrap and shutdown/end-of-level free helpers.

Evidence lives in `release/readiness/ghidra_texture_tga_wave513_2026-05-17.md`; runtime rendering behavior, exact class layout, and rebuild parity remain unproven.

## Recent Headless Semantic Promotions (2026-02-26)

| Address | Name | Status | Description | Link |
|---------|------|--------|-------------|------|
| 0x005894a9 | CTexture__OpenIncludeSourceAndInitBuffer | NAMED | Opens include source (file/provider), allocates buffers, initializes parse span fields | - |
| 0x00589650 | CTexture__InitBufferFromMemorySpan | NAMED | Initializes decode parse span from memory pointer + length and validates bounds | - |
| 0x00598749 | CTexture__HasSameFormatClassId | NAMED | Predicate for texture-comparator helpers; checks format/class-id equality | - |
| 0x00582a99 | CTexture__PackTexels_Dither_Bits332 | NAMED | Dithered texel packer for 8-bit 3-3-2 packed output | - |
| 0x00582bbe | CTexture__PackTexels_Dither_Bits8 | NAMED | Dithered texel packer for 8-bit single-channel output | - |
| 0x00582c8a | CTexture__PackTexels_Dither_Bits565 | NAMED | Dithered texel packer for 16-bit 5-6-5 packed output | - |
| 0x00582dd3 | CTexture__PackTexels_Dither_Bits444 | NAMED | Dithered texel packer for 16-bit 4-4-4 packed output | - |
| 0x00583a94 | CTexture__PackTexels_Dither_A4L4 | NAMED | Dithered texel packer for 4-bit alpha + 4-bit luminance output | - |
| 0x00583ba4 | CTexture__PackTexels_Dither_L16 | NAMED | Dithered texel packer for 16-bit luminance output | - |
| 0x00583c8e | CTexture__PackTexels_Dither_Bits8_8 | NAMED | Dithered texel packer for dual-channel 8-8 packed output | - |
| 0x00583d89 | CTexture__PackTexels_Dither_Bits5_5_5 | NAMED | Dithered texel packer for 5-5-5 packed output | - |
| 0x00583eb3 | CTexture__PackTexels_Dither_Bits8_8_8_Alt | NAMED | Dithered texel packer for alternate-order 8-8-8 packed output | - |
| 0x00583fe5 | CTexture__PackTexels_Dither_Bits8_8_8_8_Alt | NAMED | Dithered texel packer for alternate-order 8-8-8-8 packed output | - |
| 0x00584535 | CTexture__PackTexels_Dither_Bits8_8_FromAuxLookup | NAMED | Dithered 8-8 output path using auxiliary lookup helper per texel | - |
| 0x0058463a | CTexture__PackTexels_Dither_L16_Alt | NAMED | Alternate table-slot variant of dithered 16-bit luminance output | - |
| 0x00584a4c | CTexture__PackTexels_NoDither_Bits16_16_16 | NAMED | Non-dither texel packer writing three 16-bit color channels per texel | - |
| 0x00584b5f | CTexture__UnpackTexels_Bgr8ToFloat4 | NAMED | Unpacks BGR8 source texels into float4 RGBA (alpha forced to 1.0) before optional post-normalization | - |
| 0x00584c04 | CTexture__UnpackTexels_Bgra8ToFloat4 | NAMED | Unpacks BGRA8 source texels into normalized float4 RGBA channels | - |
| 0x00584cc3 | CTexture__UnpackTexels_Bgr8ToFloat4_AlphaOne | NAMED | Unpacks BGR8 source texels into float4 RGBA with forced alpha = 1.0 | - |
| 0x0058579b | CTexture__UnpackTexels_Bits444ToFloat4_AlphaOne | NAMED | Unpacks 4-4-4 packed texels into float4 RGB with alpha forced to 1.0 | - |
| 0x0058586b | CTexture__UnpackTexels_PaletteIndexA8ToFloat4 | NAMED | Expands palette-indexed texels through lookup table and applies 8-bit alpha | - |
| 0x00585cb0 | CTexture__UnpackTexels_Signed8_8_ToFloat4_RG | NAMED | Unpacks signed 8-8 texels into float4 RG lanes with Z/A initialized | - |
| 0x005860ba | CTexture__UnpackTexels_Signed16_16_ToFloat4_RG | NAMED | Unpacks signed 16-16 texels into float4 RG lanes with Z/A initialized | - |
| 0x00586438 | CTexture__UnpackTexels_NormalXY_Signed8_8_ReconstructZ | NAMED | Unpacks signed XY normals and reconstructs Z from unit-length constraint | - |
| 0x0058686f | CTexture__UnpackTexels_CopyRaw128 | NAMED | Raw-copy unpack path copying 128-bit texel records directly | - |
| 0x005869b0 | CTexture__UnpackTexels_Bits16_16_16_ToFloat4 | NAMED | Unpacks 16-16-16 packed texels into float4 RGB with alpha forced to 1.0 | - |
| 0x005876ab | CTexture__WriteTexelBlockWithQuadCache | NAMED | Writes texel blocks through quad cache and flushes completed rows | - |
| 0x00587af0 | CTexture__ReadTexelBlockWithQuadCache | NAMED | Reads texel blocks through quad cache with optional postfilter zeroing | - |

## Key Strings Referenced

| Address | String | Used By |
|---------|--------|---------|
| 0x00632ef0 | "C:\dev\ONSLAUGHT2\texture.cpp" | Debug path |
| 0x00632f10 | "Warning : loading texture %s manually!\n" | CTexture__FindTexture |
| 0x00632ec0 | "Texture '%s' not found in level resource file" | CTexture__FindTexture |
| 0x00632f38 | "Found possible match for texture %s, but mipmaps=%d, wanted %d\n" | CTexture__FindTexture |

## Global Variables

| Address | Type | Purpose |
|---------|------|---------|
| 0x0083d9b0 | CTexture* | Head of texture linked list |
| 0x0083d9b4 | CTexture* | Default/fallback texture |
| 0x0083d9b8 | int | Debug output flag |
| 0x0083d99c | int | Texture count |
| 0x00662f3c | char | Texture loading mode flag |
| 0x00662dd4 | int | Another texture mode flag |

## Analysis Notes

### CTexture__FindTexture (0x004f27f0)

This is the main texture lookup function. It:

1. **Iterates through texture linked list** starting at `DAT_0083d9b0`
2. **Matches by name** using `stricmp` (0x00568390, was `FUN_00568390`)
3. **Validates mipmap count** if param_4 != -1
4. **On cache miss**:
   - Logs warning "Warning : loading texture %s manually!"
   - Allocates 0x158 bytes (344 bytes) for new CTexture
   - Calls constructor via `FUN_00556cc0`
   - Calls virtual load method at vtable offset 0x14
5. **Ref counting**: Increments `texture[0x29]` on success
6. **Fallback**: Returns `DAT_0083d9b4` (default texture) if loading fails and param_5 is set

### CTexture Structure (inferred from constructor)

```
Offset  Size  Purpose
0x00    4     vtable pointer (PTR_FUN_005e59a0)
0x08    128   Name buffer (32 chars via loop init)
0x88    4     Unknown (set to 0)
0x8C    4     Unknown (set to 0)
0x90    4     Unknown (set to 0)
0x94    4     Scale X (0x3f800000 = 1.0f)
0x98    4     Scale Y (0x3f800000 = 1.0f)
0x9C-0xF8  64  Cleared in loop (16 dwords per iteration)
0xA0    4     Next texture in list
0xA4    4     Reference count
0xA8    4     Texture type/format
0x138   4     Unknown (set to 1)
0x148   4     Mipmap count (piVar3[0x52])
0x150   4     Unknown (set to 0)
0x154   4     Unknown (set to 1)
0x155   1     Unknown byte (set to 0)
0x156   2     Unknown word (set to 0xFFFF)
Total: 0x158 (344 bytes)
```

### Call Graph

```
CTexture__FindTexture (004f27f0)
  +-> stricmp (string compare)
  +-> FatalError__ExitWithLocalizedPrefix_A (Wave998 no-return fatal texture/resource failure path)
  +-> sprintf (sprintf-like)
  +-> DebugTrace (debug output)
  +-> OID__AllocObject (memory allocation wrapper)
  +-> CTexture__ctor (00556cc0)
  |     +-> CTextureBase__Init (004f2710)
  |     +-> CShaderBase__Init
  +-> CConsole__Printf (error logging)
  +-> CTexture__Release (00556f50)
```

## Cross-References

CTexture__FindTexture has **248 callers** - it's a core function used throughout:
- Model loading
- UI/HUD rendering
- Effects system
- Level loading

## Related
- Debug path string: 0x00632ef0
- Vtable: 0x005e59a0
- Parent: [../README.md](../README.md)
