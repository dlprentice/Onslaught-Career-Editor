# DXTexture.cpp - DirectX Texture Management

Wave1211 (`wave1211-score17-residual-current-risk-review`) re-read and tag-normalized `0x005d06f0 CRT__InitSehFrameNoop` as one of `8 score-17 residual current-risk rows` in the current-risk denominator. Fresh evidence keeps the row tied to `CDXTexture__InitCpuVendorAndSimdFlags`, the `0x005891cb` callsite, and the bounded SEH-frame helper shape around `FS:[0]`. No rename, signature, comment, function-boundary, or executable-byte change was made. Active current-risk accounting after the wave is `1110/1179 = 94.15%`; verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260607-061324_post_wave1211_score17_residual_current_risk_review_verified`. Runtime CRT exception behavior, runtime CPU/SIMD initialization behavior, exact CRT/source identity, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.

Wave1163 current-risk update: Wave1163 (`wave1163-texture-node-tree-inflate-huffman-current-risk-review`) accounts for `17 CFastVB/CTexture/CDXTexture current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator with fresh Ghidra export evidence. It is a read-only review with no mutation, no rename, no signature change, no comment/tag change, no function-boundary change, no executable-byte change, no BEA launch, no installed-game mutation, no save mutation, and no runtime-file mutation. Static closure remains `6411/6411 = 100.00%` with static debt `0 / 0 / 0`; expanded post-100 static surface remains `1560/1560 = 100.00%`; Wave911 focused is historical-retired/non-reconstructable at `812/1408 = 57.67%`; Wave911 top-500 remains `500/500 = 100.00%`; Wave1108 current focused accounting is now `564/1179 = 47.84%`; current risk candidates: 6166; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 615; focused threshold `15`; not Wave911 reconstruction. Fresh exports verified `68 xref rows` and `2779 instruction rows`. Static anchors include `CTexture__NodePayloadRecordCtor`, `CFastVB__NodeType9__ctor`, `CDXTexture__NodeType13__ctor`, `CDXTexture__RegisterSerializedChunk`, `CFastVB__AreNodeTreesCompatible`, `CFastVB__SelectBestNodeTreeMatch`, `CTexture__LoadDefaultHuffmanTables`, `CDXTexture__InflateStream_ProcessZlibState`, `CDXTexture__BuildInflateHuffmanTable`, and `CDXTexture__FlushEntropyBitWriter`. JPEG Huffman separate from inflate Huffman is an explicit static map boundary. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260606-025611_post_wave1163_texture_node_tree_inflate_huffman_current_risk_review_verified`. Runtime parser behavior, runtime texture decode behavior, runtime JPEG behavior, runtime inflate/decompression behavior, exact node-tree/payload/chunk/z_stream/Huffman-table/entropy-writer layouts, hidden ABI completeness, exact source-body identity, BEA patching behavior, visual QA, gameplay outcomes, and rebuild parity remain separate proof. Current system contract: `texture-resource-decode-static-contract.md`. Probe token anchor: Wave1163; wave1163-texture-node-tree-inflate-huffman-current-risk-review; 564/1179 = 47.84%; 17 CFastVB/CTexture/CDXTexture current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 615; current risk candidates: 6166; fresh Ghidra export; read-only review; no mutation; 0 / 0 / 0; 6411/6411 = 100.00%; 68 xref rows; 2779 instruction rows; CTexture__NodePayloadRecordCtor; CFastVB__NodeType9__ctor; CDXTexture__NodeType13__ctor; CDXTexture__RegisterSerializedChunk; CFastVB__AreNodeTreesCompatible; CFastVB__SelectBestNodeTreeMatch; CTexture__LoadDefaultHuffmanTables; CDXTexture__InflateStream_ProcessZlibState; CDXTexture__BuildInflateHuffmanTable; CDXTexture__FlushEntropyBitWriter; JPEG Huffman separate from inflate Huffman; [maintainer-local-ghidra-backup-root]\BEA_20260606-025611_post_wave1163_texture_node_tree_inflate_huffman_current_risk_review_verified; texture-resource-decode-static-contract.md; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.

**Source File:** `[maintainer-local-source-export-root]\DXTexture.cpp`
**Debug Path Address:** `0x0065269c`

## Overview
> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

DXTexture.cpp implements DirectX-specific texture management functionality for the Battle Engine Aquila renderer. This module handles texture loading from AYA resource archives, texture format conversion, mipmap generation, and texture serialization/deserialization.

Wave1071 (`texel-unpack-head-mid-review-wave1071`) re-read the DXTexture-owned Wave672/Wave673 texel-unpack head/middle rows with no mutation, including `0x00585576 CDXTexture__UnpackTexels_Bits332ToFloat4`, `0x0058562d CDXTexture__UnpackTexels_A8ToFloat4_ZeroRGB`, `0x005856b8 CDXTexture__UnpackTexels_Bits332A8ToFloat4`, `0x00585da3 CDXTexture__UnpackTexels_Signed5_5_A6_ToFloat4`, and `0x00585e9f CDXTexture__UnpackTexels_Signed8_8_A8_ToFloat4_RG`. Fresh metadata/tags/xrefs/instructions/decompile evidence keeps the rows tied to DATA-slot texel profile entries and observed packed/signed lane expansion. Queue closure remains `6246/6246 = 100.00%`; expanded static surface progress advances to `1319/1560 = 84.55%`; verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260602-031627_post_wave1071_texel_unpack_head_mid_review_verified`. Runtime texture output behavior, runtime codec/FourCC behavior, exact profile/descriptor layouts, exact source identity, BEA patching, gameplay outcomes, and rebuild parity remain separate proof.

Wave1070 (`texel-unpack-tail-review-wave1070`) re-read four DXTexture-owned texel unpack callback rows with no mutation: `0x005861b4 CDXTexture__UnpackTexels_Signed2_10_10_10_ToFloat4`, `0x00586305 CDXTexture__UnpackTexels_Signed16_16_16_16_ToFloat4`, `0x00586609 CDXTexture__UnpackTexels_CallbackPerTexel_Stride2_SetRGBAOne`, and `0x0058677b CDXTexture__UnpackTexels_CallbackSingleTexel`. The rows remain DATA-slot coherent with the Wave674 texel-unpack vtables and fresh metadata/tags/xrefs/instructions/decompile evidence; Wave1070 made no rename, signature, comment, tag, function-boundary, executable-byte, or runtime/game-file mutation. Queue closure remains `6246/6246 = 100.00%`; expanded static surface progress advances to `1278/1560 = 81.92%`; verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260602-022701_post_wave1070_texel_unpack_tail_review_verified`. Runtime texture output behavior, runtime codec/FourCC behavior, exact profile/descriptor layouts, exact source identity, BEA patching, gameplay outcomes, and rebuild parity remain separate proof.

Wave1061 (`cdxtexture-png-decode-review-wave1061`) re-read twenty existing CDXTexture PNG decode/parser rows with no mutation: `0x00592dc2 CDXTexture__CreatePngDecodeContext`, `0x00592eb6 CDXTexture__ParsePngHeadersUntilIdat`, `0x00593043 CDXTexture__DecodePngPassRowsAndPostprocess`, `0x00593411 CDXTexture__ResetPngDecodeContext`, `0x0059d699 CDXTexture__ParsePngChunk_IHDR`, `0x0059d879 CDXTexture__ParsePngChunk_PLTE`, `0x0059d992 CDXTexture__ParsePngChunk_IEND`, `0x0059d9d8 CDXTexture__ParsePngChunk_gAMA`, `0x0059dad9 CDXTexture__ParsePngChunk_sRGB`, `0x0059dbbb CDXTexture__ParsePngChunk_tRNS`, `0x0059dd5c CDXTexture__HandlePngChunkAfterIdat`, and `0x0059dda2 CDXTexture__ProcessIdatChunkDataAndQueueDecode`. Fresh primary exports verified `20` metadata rows, `20` tag rows, `55` xref rows, `1578` function-body instruction rows, and `20` decompile rows; context exports verified `20` metadata rows, `20` tag rows, `51` xref rows, `1892` function-body instruction rows, and `20` decompile rows. Queue closure remains `6246/6246 = 100.00%`; Wave911 focused progress remains `812/1408 = 57.67%`; expanded static surface progress extends to `1168/1529 = 76.39%`; top-500 coverage remains `500/500 = 100.00%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260601-211936_post_wave1061_cdxtexture_png_decode_review_verified`, `19` files, `174721927` bytes, `DiffCount=0`, `HashDiffCount=0`. Exact PNG decode-state/image-context/chunk flag/CRC/source-read/gamma/sRGB/tRNS policy layouts, exact libpng/zlib/source identity, runtime PNG/image fidelity, runtime decompression behavior, BEA patching, gameplay outcomes, and rebuild parity remain separate proof. Probe token anchor: Wave1061; cdxtexture-png-decode-review-wave1061; 0x00592dc2 CDXTexture__CreatePngDecodeContext; 0x00592eb6 CDXTexture__ParsePngHeadersUntilIdat; 0x00593043 CDXTexture__DecodePngPassRowsAndPostprocess; 0x00593411 CDXTexture__ResetPngDecodeContext; 0x0059d699 CDXTexture__ParsePngChunk_IHDR; 0x0059d879 CDXTexture__ParsePngChunk_PLTE; 0x0059d992 CDXTexture__ParsePngChunk_IEND; 0x0059d9d8 CDXTexture__ParsePngChunk_gAMA; 0x0059dad9 CDXTexture__ParsePngChunk_sRGB; 0x0059dbbb CDXTexture__ParsePngChunk_tRNS; 0x0059dd5c CDXTexture__HandlePngChunkAfterIdat; 0x0059dda2 CDXTexture__ProcessIdatChunkDataAndQueueDecode; 812/1408 = 57.67%; 1168/1529 = 76.39%; 500/500 = 100.00%; 6246/6246 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260601-211936_post_wave1061_cdxtexture_png_decode_review_verified; no mutation.

Wave1025 CFastVB node-tree review (`cfastvb-node-tree-review-wave1025`) re-read DXTexture-side parser node-type and serialized-chunk rows with no mutation, including `0x00598da4 CDXTexture__NodeType13__ctor` and `0x0059902a CDXTexture__RegisterSerializedChunk`, plus selector call context in `0x005994c4 CDXTexture__ProcessTextureChunkAndEmitBindings`. The hidden-ECX/locked-storage signatures remain intentionally bounded. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260601-004522_post_wave1025_cfastvb_node_tree_review_verified`. Runtime texture/parser behavior, exact chunk-builder layout, exact source-body identity, BEA patching, and rebuild parity remain separate proof.

Wave900 final static tail (`final-static-tail-wave900`, `wave900-readback-verified`) closed the remaining CDXTexture/CRT support rows that touch this owner doc: `0x005d06f0 CRT__InitSehFrameNoop` is called by `CDXTexture__InitCpuVendorAndSimdFlags`, and `0x005d08ad CRT__TmpFile_OpenUniqueBinaryStream` is called by `CDXTexture__InitHostIoCallbacks`. Probe token anchor: Wave900 final static tail; final-static-tail-wave900; 0x005d04e6 RtlUnwind; 0x005d06f0 CRT__InitSehFrameNoop; 0x005d08ad CRT__TmpFile_OpenUniqueBinaryStream; 0x005d0a9f CRT__LongJmpProbe_NoOp; 0x005d0c0c GetCurrentProcessId; 0x005d0c7f CRT__LCMapStringW_AnsiCompat; 0x005d5120 CTexture__FindTexture_Unwind; 6113/6113 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260526-090248_post_wave900_final_static_tail_verified. Exact CRT helper source identity, runtime filesystem behavior, runtime exception behavior, BEA patching, and rebuild parity remain deferred.

Wave904 (`texture-render-static-review-wave904`) records the DXTexture side of the `static-coherent texture/resource/decode/render core` after export-contract queue closure `6113/6113 = 100.00%` (static review slice only). The reviewed slice covers `1289` rows across `25` selected families, including `CDXTexture` `366`, `CFastVB` `347`, `CTexture` `233`, and `CVBufTexture` `40`; DXTexture anchors include `CDXTexture__LoadTextureFromFile_Core`, `CDXTexture__DecodeMemoryToTextureObject`, and `CDXTexture__ValidateJpegFrameAndComputeMcuLayout`, with render/decode bridge anchors `CFastVB__RenderTriangleStripImmediate` and `CVBufTexture__DrawSpriteEx`. Asset bridge counts include `847/847` loose textures and `352/352` model material/texture-binding rows. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260526-101300_post_wave904_texture_render_static_review_verified`.

Wave964 CDXTexture inflate codes/tree review (`cdxtexture-inflate-codes-tree-review-wave964`, `wave964-readback-verified`) normalized one stale inflate-stream caveat in this owner doc: `0x0059c8c1 CDXTexture__InflateStream_ProcessZlibState` now records the fresh body-instruction/decompile evidence that `0x0059c9ce CALL 0x005b1e94` assigns the `0x005b1e94 CDXTexture__InflateProcessBlockHeader` return directly into the local status variable. The reviewed helper chain includes `0x005bcfd3 CDXTexture__InflateCodesState_Process`, `0x005bd53b CDXTexture__BuildInflateHuffmanTable`, `0x005bd933 CDXTexture__InflateDynamicTree_BuildLitDistTrees`, and `0x005be360 CDXTexture__InflateFast_DecodeBlockStream`; additional anchors include `0x005b2455 CALL 0x005bcfd3`, `0x005b245a CMP EAX, 0x1`, `0x005bd067 CALL 0x005be360`, `0x005bd8f6 CALL 0x005bd53b`, `0x005bd982 CALL 0x005bd53b`, `0x005bd9b9 CALL 0x005bd53b`, and `0x005b23f3 CALL 0x005bd933`. Fresh exports verified pre/post `12` metadata rows, `12` tag rows, `23` xref rows, `1740` around-address instruction rows, `2271` body-instruction rows, and `12` decompile rows. This was a comment/tag mutation only, adding `extraout-eax-gap-resolved`; it made no rename, signature change, function-boundary change, or executable-byte change. Wave911 focused re-audit progress after Wave964 is `323/1408 = 22.94%`; static export-contract closure remains `6152/6152 = 100.00%`; verified backup `[maintainer-local-ghidra-backup-root]\BEA_20260528-141856_post_wave964_cdxtexture_inflate_codes_tree_review_verified`. Exact `z_stream` layout, inflate-state layout, table-entry schemas, callback ABI, exact zlib/source identity, runtime inflate/decode behavior, BEA patching, and rebuild parity remain separate proof. Probe token anchor: Wave964; cdxtexture-inflate-codes-tree-review-wave964; 0x0059c8c1 CDXTexture__InflateStream_ProcessZlibState; 0x0059c9ce CALL 0x005b1e94; 0x005b1e94 CDXTexture__InflateProcessBlockHeader; 0x005bcfd3 CDXTexture__InflateCodesState_Process; 0x005bd53b CDXTexture__BuildInflateHuffmanTable; 0x005bd933 CDXTexture__InflateDynamicTree_BuildLitDistTrees; 0x005be360 CDXTexture__InflateFast_DecodeBlockStream; extraout-eax-gap-resolved; 323/1408 = 22.94%; 6152/6152 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260528-141856_post_wave964_cdxtexture_inflate_codes_tree_review_verified; comment/tag mutation only.

Wave899 CDXTexture JPEG decode tail (`cdxtexture-jpeg-decode-tail-wave899`, `wave899-readback-verified`) saved comments/tags for six raw commentless CDXTexture JPEG scan/layout, YCbCr conversion, and inflate Huffman-table rows. Probe token anchor: Wave899 CDXTexture JPEG decode tail; cdxtexture-jpeg-decode-tail-wave899; 0x005b7770 CDXTexture__ValidateJpegFrameAndComputeMcuLayout; 0x005b7920 CDXTexture__ValidateJpegScanScript; 0x005b7c50 CDXTexture__LoadCurrentJpegScanDescriptor; 0x005b7d30 CDXTexture__BuildCurrentScanMcuLayout; 0x005bce60 CDXTexture__ConvertYCbCrToRgb24_Mmx; 0x005bd53b CDXTexture__BuildInflateHuffmanTable; 0x005d04e6 RtlUnwind; 6106/6113 = 99.89%; [maintainer-local-ghidra-backup-root]\BEA_20260526-083306_post_wave899_cdxtexture_jpeg_decode_tail_verified. Static evidence ties the tranche to `CDXTexture__InitJpegScanController`, `CDXTexture__ProcessJpegScanStateMachine`, scan-script coverage checks, selected component MCU layout, raw YCbCr/RGB24 MMX conversion callsite `0x005afb05`, constants near `0x005f5000`, and dynamic inflate tree builders at `0x005bd8f6`, `0x005bd982`, and `0x005bd9b9`. Exact JPEG state/component/scan descriptor layouts, exact MMX color coefficient identity and lane packing, exact zlib/source identity and Huffman table-entry schema, runtime JPEG/image decode behavior, runtime decompression behavior, BEA patching, and rebuild parity remain deferred.

Wave895 decode feature tail (`decode-feature-tail-wave895`, `wave895-readback-verified`) saved comments/tags for nine raw commentless CFastVB/CTexture/CDXTexture decode-feature rows. Probe token anchor: Wave895 decode feature tail; decode-feature-tail-wave895; 0x00598390 CFastVB__DetectCpuFeatureMask; 0x0059a71a CFastVB__SelectBestNodeTreeMatch; 0x0059b150 CTexture__InitDecodeLookupScratchTables; 0x0059b1d0 CTexture__InitializeDecodePipelineFromHeader; 0x0059b510 CDXTexture__ValidateJpegFrameAndBuildScanLayout; 0x0059b6f0 CTexture__BuildComponentPlaneLayoutTables; 0x0059b880 CTexture__EnsureComponentDecodeScratchBlocks; 0x0059be00 CDXTexture__CreateDecodeJobDescriptor; 0x0059be70 CDXTexture__AllocDecodeBlockAndLink; 0x0059c610 CFastVB__ReleaseOwnedObjectAndReset_Core; 6086/6113 = 99.56%; [maintainer-local-ghidra-backup-root]\BEA_20260526-064920_post_wave895_decode_feature_tail_verified. Static evidence ties the DXTexture-owned portion to JPEG frame validation/scan layout, decode-state post-frame component layout, component scratch-block materialization, and two decode allocator vtable DATA callbacks registered at `0x0059c563` and `0x0059c56a`. Exact feature-bit names, node-tree layout, decode-state/component-plane/descriptor/allocator-state layouts, hidden register/stack ABI completeness, runtime parser/texture/JPEG/image decode behavior, BEA patching, and rebuild parity remain deferred.

Wave896 decode cleanup tail (`decode-cleanup-tail-wave896`, `wave896-readback-verified`) saved comments/tags for `0x0059ccb3 CDXTexture__FreeDecodeStateIfOwnerPresent`. Probe token anchor: Wave896 decode cleanup tail; decode-cleanup-tail-wave896; 0x0059c610 CFastVB__ReleaseOwnedObjectAndReset_Core; 0x0059ccb3 CDXTexture__FreeDecodeStateIfOwnerPresent; 0x005a09f8 CFastVB__ConvertHalfToFloat8_SIMDKernel; 6088/6113 = 99.59%; [maintainer-local-ghidra-backup-root]\BEA_20260526-071320_post_wave896_decode_cleanup_tail_verified. Static evidence ties the row to `0x00592dc2 CDXTexture__CreatePngDecodeContext`, nine `0x00593411 CDXTexture__ResetPngDecodeContext` callsites, and `0x0059517e CDXTexture__FreeDecodeBufferIfPresent`; the body requires both arguments to be non-null before calling `CRT__FreeBase(decode_buffer)`. Exact PNG/decode buffer ownership, allocation pairing, decode-state layout, runtime image decode cleanup behavior, BEA patching, and rebuild parity remain deferred.

Wave894 JPEG header parser tail (`jpeg-header-parser-tail-wave894`, `wave894-readback-verified`) saved comments/tags for four raw commentless JPEG/image header parser and decode descriptor rows. Probe token anchor: Wave894 JPEG header parser tail; jpeg-header-parser-tail-wave894; 0x005913b0 CFastVB__JpegParser_ResetFrameState; 0x00591720 CFastVB__JpegParser_ParseSOFComponents; 0x0059364c CDXTexture__GetImageHeaderInfo; 0x00594f15 CTexture__FinalizeDecodeFormatDescriptor; raw no-function callsites 0x00592617 and 0x0059274a; PNG decode callsite 0x0057ba81; PNG IHDR callsite 0x0059d86d; 0x00598390 CFastVB__DetectCpuFeatureMask; 6077/6113 = 99.41%; [maintainer-local-ghidra-backup-root]\BEA_20260526-062021_post_wave894_jpeg_header_parser_tail_verified. Static evidence ties the tranche to JPEG state reset, SOF component parsing, descriptor table state+0xdc with 0x15-dword stride, PNG header descriptor query, IHDR descriptor finalization, row-byte overflow checks, and warning string/ids 0x5eea60 and 0x5eeaec. Exact JPEG parser state layout, exact PNG/JPEG shared descriptor schema, exact color/format/sampling enum names, hidden register ABI completeness, runtime image decode behavior, BEA patching, and rebuild parity remain deferred.

Wave888 texture transform dispatch tail (`texture-transform-dispatch-tail-wave888`, `wave888-readback-verified`) saved comments/tags for DXTexture-side dispatch thunks in the transform tail. Exact anchors include `0x0057617e CDXTexture__DispatchPtr00656f48_WithInit`, `0x00576286 CDXTexture__DispatchPtr00656f68_WithInit`, `0x00577dd5 CDXTexture__DispatchPtr00657010_WithInit`, and `0x005780d6 CDXTexture__DispatchPtr00656f84_WithInit`. Probe token anchor: `Wave888 texture transform dispatch tail`; `texture-transform-dispatch-tail-wave888`; `0x0057617e CDXTexture__DispatchPtr00656f48_WithInit`; `0x00576286 CDXTexture__DispatchPtr00656f68_WithInit`; `0x00576404 Math__InterpolateVec4Cubic`; `0x00576621 Math__InterpolateVec4ByUV`; `0x005768fe CFastVB__DispatchIndirect_00656f3c`; `0x0057770b CFastVB__BuildTransformMatrixWithOffsets`; `0x00578a20 CTexture__MapNormalizedUvToVolumeCoords`; `0x00578dad CFastVB__MapVolumeCoordsToNormalizedUv`; `0x00578f53 CFastVB__ApplyOptionalTransformPasses`; `0x00579273 CTexture__BuildTransformMatrixWithOptionalOffsets`; dispatch slots `0x00656f48` and `0x0065715c`; `0x00579a9a CVertexShader__CompileScriptWithDirectiveParser`; `6052/6113 = 99.00%`; `[maintainer-local-ghidra-backup-root]\BEA_20260526-033426_post_wave888_texture_transform_dispatch_tail_verified`. Exact dispatch-table slot targets, exact CPU feature policy, exact descriptor/matrix/vertex-shader/texture-transform layouts, runtime texture/math/render behavior, BEA patching, and rebuild parity remain deferred.

Wave889 texture codec surface prelude (`texture-codec-surface-prelude-wave889`, `wave889-readback-verified`) saved comments/tags for the texture codec, surface-node, mapped-resource, vertex-shader parser, and resample prelude tranche. Probe token anchor: Wave889 texture codec surface prelude; texture-codec-surface-prelude-wave889; 0x00579a9a CVertexShader__CompileScriptWithDirectiveParser; 0x00579b39 CDXTexture__LookupNamedFormatDescriptor; 0x00579e08 CDXTexture__DecodeBmpDibFromMemory; 0x0057ca6a CDXTexture__DecodeFromMemory_WithFallbackCodecs; 0x0057c7a4 CMeshCollisionVolume__LoadMappedTextureResourcesByMode; 0x0057cca4 CFastVB__BuildResampleKernelBuckets; 0x0057cf60 CDXTexture__CopyDxtBlockRegion; 0x0057d0ee CWaypointManager__BoxBlurPackedColorRows_Scalar; 6054/6113 = 99.03%; [maintainer-local-ghidra-backup-root]\BEA_20260526-040930_post_wave889_texture_codec_surface_prelude_verified. Static evidence ties the tranche to directive parsing, descriptor lookup, codec dispatch, surface-node cleanup, mapped texture export, resample bucket setup, and DXT block copying. Exact texture/codec/surface-node/mapped-file/descriptor/parser/resample table layouts, exact source-body identity, runtime texture decode/encode/export/resample/render behavior, BEA patching, and rebuild parity remain deferred.

Wave890 texture filter MMX dispatch (`texture-filter-mmx-dispatch-wave890`, `wave890-readback-verified`) saved comments/tags for the texture filter/downsample dispatch rows around the Wave664 downsample island. Probe token anchor: Wave890 texture filter MMX dispatch; texture-filter-mmx-dispatch-wave890; 0x0057d0ee CWaypointManager__BoxBlurPackedColorRows_Scalar; 0x0057d244 CDXTexture__Downsample2x2Average32; 0x0057d32e CWaypointManager__BoxBlurPackedColorRows_SIMD; 0x0057d446 CWaypointManager__InitMmxDispatchAndRun; 0x0057d47e CDXTexture__InitMmxDispatchAndRun; dispatch slots 0x00657974 and 0x00657978; 0x00580a05 CDXTexture__UploadSurfaceRegionWithFallback; 6059/6113 = 99.12%; [maintainer-local-ghidra-backup-root]\BEA_20260526-043655_post_wave890_texture_filter_mmx_dispatch_verified. Static evidence ties the tranche to `CDXTexture__IsMmxEnabledBySystemConfig`, scalar and MMX/SIMD packed-color row filters, and the scalar `CDXTexture__Downsample2x2Average32` fallback. Exact owner/source identity, exact texture surface/context layout, hidden dispatch ABI, pointer-table ownership, runtime CPU selection/filtering/downsample behavior, BEA patching, and rebuild parity remain deferred.

Wave891 texture upload texel profile (`texture-upload-texel-profile-wave891`, `wave891-readback-verified`) saved comments/tags for DXTexture upload/profile rows `0x00580a05 CDXTexture__UploadSurfaceRegionWithFallback` and `0x00580ef4 CDXTexture__CreateTexelCodecProfileFromSurfaceDesc`, plus companion CFastVB profile constructor `0x00581a4f CFastVB__TexelUnpackProfile__ctorFromDescriptor`. Probe token anchor: Wave891 texture upload texel profile; texture-upload-texel-profile-wave891; 0x00580a05 CDXTexture__UploadSurfaceRegionWithFallback; 0x00580ef4 CDXTexture__CreateTexelCodecProfileFromSurfaceDesc; 0x00581a4f CFastVB__TexelUnpackProfile__ctorFromDescriptor; vtable slot 0x30; vtable slot 0x24; 0x005888bc CFastVB__InterpolateDualProfileStreams; 6062/6113 = 99.17%; [maintainer-local-ghidra-backup-root]\BEA_20260526-050306_post_wave891_texture_upload_texel_profile_head_verified. Static evidence ties the DXTexture rows to surface descriptor reads, optional-region validation, DXT/packed-format alignment, D3D debug mute around lock/probe paths, temporary-surface fallback, source-surface AddRef, and active texel codec profile descriptor fill. Exact texture surface/context layout, exact texel profile and descriptor layouts, exact Direct3D interface identity, runtime upload/lock/conversion/unpack/render behavior, BEA patching, and rebuild parity remain deferred.

Wave892 SIMD gate dual profile (`simd-gate-dual-profile-wave892`, `wave892-readback-verified`) saved comments/tags for DXTexture CPU/MMX gate rows `0x00589116 CDXTexture__IsMmxEnabledBySystemConfig` and `0x005891c6 CDXTexture__InitCpuVendorAndSimdFlags`, plus companion CFastVB interpolation callback `0x005888bc CFastVB__InterpolateDualProfileStreams`. Probe token anchor: Wave892 SIMD gate dual profile; simd-gate-dual-profile-wave892; 0x005888bc CFastVB__InterpolateDualProfileStreams; 0x00589116 CDXTexture__IsMmxEnabledBySystemConfig; 0x005891c6 CDXTexture__InitCpuVendorAndSimdFlags; 0x00657164; DisableMMX; GenuineIntel; 0x0058aacf CTexture__HandleDirective_If; 6065/6113 = 99.21%; [maintainer-local-ghidra-backup-root]\BEA_20260526-052708_post_wave892_simd_gate_dual_profile_verified. Static evidence ties the DXTexture rows to the `Software\\Microsoft\\Direct3D` / `DisableMMX` registry gate, cache global `DAT_00657a80`, `GetSystemInfo`, `CDXTexture__CpuHasMmxFeature`, `GenuineIntel`, `cpuid_basic_info(0)`, and split continuation `0x0058920c CDXTexture__DetectCpuSimdFlags`. Exact Windows registry policy, CPU-feature dispatch policy, split-continuation ownership, runtime SIMD/MMX selection/interpolation/render behavior, BEA patching, and rebuild parity remain deferred.

## Wave886 Texture Decode/Upload Tail Read-Back

Wave886 texture decode/upload tail (`texture-decode-upload-tail-wave886`, `wave886-readback-verified`) saved comments/tags for DXTexture-side connector rows `0x00574492 CDXTexture__UploadDecodedBufferToSurface`, `0x00574662 CDXTexture__ConvertSurfaceWithActiveProfile`, `0x0057473b CDXTexture__NormalizeTextureConversionParams`, `0x00574ae5 CDXTexture__DecodeMemoryAndUploadWithRect`, `0x00574b9d CDXTexture__CopyOrUploadSurfaceRegionWithFallback`, `0x00574da5 CDXTexture__ConvertSurfaceRegionWithActiveProfile`, `0x0057511b Platform__OpenDecodeUploadMappedTexture`, `0x0057516c CDXTexture__DecodeMemoryToTextureObject`, and `0x005758e6 CDXTexture__DecodeMappedMemoryEntry`; companion texture.cpp anchor is `0x00573d80 CTexture__InsertNodeIntoTree`. Probe token anchor: `Wave886 texture decode/upload tail`; `texture-decode-upload-tail-wave886`; `0x00573d80 CTexture__InsertNodeIntoTree`; `0x00574492 CDXTexture__UploadDecodedBufferToSurface`; `0x0057473b CDXTexture__NormalizeTextureConversionParams`; `0x0057516c CDXTexture__DecodeMemoryToTextureObject`; `0x005758e6 CDXTexture__DecodeMappedMemoryEntry`; `CFastVB__InsertNodeIntoRBTreeWithHint_00573340`; `CDXTexture__DecodeFromMemory_WithFallbackCodecs`; `CFastVB__InitDualTexelConversionPipeline`; `CDXTexture__GenerateMipChainBySurfaceCopy`; high-importance texture decode/upload and render-resource infrastructure with low local evidence density, not low-importance filler; `0x005759b6 CFastVB__DispatchIndirect_00657014`; `5978/6113 = 97.79%`; `[maintainer-local-ghidra-backup-root]\BEA_20260526-023255_post_wave886_texture_decode_upload_tail_verified`.

Wave887 texture dispatch/interpolation tail (`texture-dispatch-interpolation-tail-wave887`, `wave887-readback-verified`) saved comments/tags for adjacent texture/math/render dispatch rows including `0x005759b6 CFastVB__DispatchIndirect_00657014`, `0x005759c3 CDXTexture__PackTexels_DispatchIndirect_005759c3`, `0x00575b47 Math__InterpolateVec2Cubic`, `0x00575dc9 CFastVB__HermiteInterpolateVec3`, `0x0057600b CVBufTexture__DispatchTextureTransformThunk`, and `0x00576161 CFastVB__DispatchIndirectByGlobalTable`. Probe token anchor: `Wave887 texture dispatch/interpolation tail`; `texture-dispatch-interpolation-tail-wave887`; `0x005759b6 CFastVB__DispatchIndirect_00657014`; `0x005759c3 CDXTexture__PackTexels_DispatchIndirect_005759c3`; `0x00575b47 Math__InterpolateVec2Cubic`; `0x00575dc9 CFastVB__HermiteInterpolateVec3`; `0x0057600b CVBufTexture__DispatchTextureTransformThunk`; `0x00576161 CFastVB__DispatchIndirectByGlobalTable`; dispatch slots `0x00657014` and `0x00656f58`; `0x0057617e CDXTexture__DispatchPtr00656f48_WithInit`; `6008/6113 = 98.28%`; `[maintainer-local-ghidra-backup-root]\BEA_20260526-030217_post_wave887_texture_dispatch_interpolation_tail_verified`. Exact dispatch-table slot targets, exact CPU feature policy, runtime texture/math/render behavior, BEA patching, and rebuild parity remain deferred.

Static evidence ties the tranche to mapped-file texture loading (`CDXTexture__LoadTextureFromFile`, `CDXTexture__DecodeMappedFileToTexture`), platform screenshot upload (`Platform__ProcessPendingScreenDump`), decode from memory with fallback codecs, D3D copy/update fallback, active-profile texel conversion, texture creation through device vtable slots, mip-chain generation, and cleanup of temporary surface objects. The apply pass preserved existing names/signature displays because Ghidra still reports locked/hidden parameter storage and made no renames, function-boundary changes, executable-byte changes, or runtime launches. Exact texture/surface/codec/profile/palette/D3D object layouts, exact source-body identity, hidden ABI completeness, runtime texture decode/upload/copy/format behavior, BEA patching, and rebuild parity remain deferred.

## Wave876 Texture Core Tail Read-Back

Wave876 texture core tail (`texture-core-tail-wave876`, `wave876-readback-verified`) saved comments/tags/signatures for DXTexture-side rows `0x00557a00 CDXTexture__FormatToString`, `0x00557a90 CDXTexture__LoadTextureFromFile_Core`, `0x00558690 CDXTexture__GetAnimatedFrame`, and `0x00558870 CDXTexture__DumpAllTexturesToTga`; companion anchors include `0x00556cc0 CTexture__ctor`, `0x005588f0 CVBufTexture__RenderModePass`, and `0x0055a0f0 CEngine__TextureFormatIndexToD3D`. Probe token anchor: `Wave876 texture core tail`; `texture-core-tail-wave876`; `0x00556cc0 CTexture__ctor`; `0x00557a90 CDXTexture__LoadTextureFromFile_Core`; `0x00558690 CDXTexture__GetAnimatedFrame`; `0x005588f0 CVBufTexture__RenderModePass`; `0x0055a0f0 CEngine__TextureFormatIndexToD3D`; high-importance texture/resource/render connector rows with low local evidence density, not low-importance filler; `0x0055b0e0 CWaterRenderSystem__ctor`; `5885/6113 = 96.27%`; `[maintainer-local-ghidra-backup-root]\BEA_20260525-212045_post_wave876_texture_core_tail_verified`.

Static evidence ties `CDXTexture__LoadTextureFromFile_Core` to empty/procedural/ordinary texture-name branches, lower-cased `data\Textures` paths, animated-frame detection, per-frame `CDXTexture__LoadTextureFromFile`, mapped-file decode through `CDXTexture__DecodeMappedFileToTexture`, field updates at `this+0xac/+0xb0/+0x144`, and an `unaff_EBX` format-reconciliation path whose exact ABI/layout remains bounded. `CDXTexture__GetAnimatedFrame` has 53 xrefs and selects `this+0xb8` or `this+0xb8 + frame*4` by a time-scaled modulo frame count. Exact texture class layouts, exact texture-format enum names, runtime texture load/decode/animation/render/dump behavior, BEA patching, and rebuild parity remain deferred.

## Wave849 D3D State/Cache Core Read-Back

Wave849 D3D state/cache core (`d3d-state-cache-core-wave849`, `wave849-readback-verified`) documented the Direct3D texture-resource connector rows used by `CDXTexture__Deserialize`, `CDXTexture__CreateMipmaps`, and `CDXTexture__LoadTextureFromFile_Core`: `0x00513640 CEngine__GetConstant32`, `0x00513760 CEngine__TextureFormatField32FD4ToIndex`, `0x005139a0 CEngine__CreateTextureOrFatal`, and `0x00513a10 CEngine__CreateTextureUnchecked`. Probe token anchor: `Wave849 D3D state/cache core`; `0x00513640 CEngine__GetConstant32`; `0x00513a10 CEngine__CreateTextureUnchecked`; `CDXTexture__LoadTextureFromFile_Core`; `5691/6098 = 93.33%`; `0x00513a80 PlatformInput__GetKeyState3Core`; `[maintainer-local-ghidra-backup-root]\BEA_20260525-073710_post_wave849_d3d_state_cache_core_verified`.

The static evidence proves the saved metadata/signature shape and texture-path xrefs only. Exact texture argument schema, full texture-format table semantics, runtime texture allocation/upload behavior, BEA patching, and rebuild parity remain deferred.

## Wave796 Final Signature Debt Read-Back Note

Wave796 signature debt (`signature-debt-wave796`, `wave796-readback-verified`) saved the final DXTexture-side param-name hardening rows: `0x00591460 CDXTexture__DecodeJpegSegment_StartOfFrame`, `0x00591fc0 CDXTexture__ParseJfifApp0Header`, `0x005921a0 CDXTexture__ParseAdobeApp14Header`, `0x00592ca0 CDXTexture__FormatChunkTagForDiagnostics`, and `0x0059e310 CDXTexture__WriteJpegHuffmanTable`. The pass made no renames, no function-boundary changes, and no executable-byte changes; it cleared the queue to 0 exact-undefined signatures and 0 param_N signatures while leaving 554 commentless rows. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260524-050846_post_wave796_final_param_signature_debt_verified`.

Saved signatures:

| Address | Saved signature |
| --- | --- |
| `0x00591460` | `int __fastcall CDXTexture__DecodeJpegSegment_StartOfFrame(int sof_marker)` |
| `0x00591fc0` | `void __fastcall CDXTexture__ParseJfifApp0Header(int segment_start_offset)` |
| `0x005921a0` | `void __thiscall CDXTexture__ParseAdobeApp14Header(void * this, uint segment_start_offset, int unused_context)` |
| `0x00592ca0` | `void __thiscall CDXTexture__FormatChunkTagForDiagnostics(void * this, int decode_state, int message_text, void * unused_context)` |
| `0x0059e310` | `void __thiscall CDXTexture__WriteJpegHuffmanTable(void * this, int table_index, int unused_context)` |

Hidden register ABI details, exact decoder/state layouts, runtime texture/JPEG/PNG behavior, BEA patching, and rebuild parity remain deferred.

## Wave738 CDXTexture DCT/Inflate Tail Read-Back Note

Wave738 CDXTexture DCT/inflate tail saved ten adjacent CDXTexture inverse-DCT and inflate helper rows. Tag anchor: `cdxtexture-dct-inflate-tail-wave738`; the earliest raw commentless row after this pass is `0x0042f220 CSPtrSet__Clear`, and the next commentless high-signal row is `0x005be622 Direct3DCreate9`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x005bb9b0 CDXTexture__InverseDct8x8_DequantAndStore_Scalar` | `void __stdcall CDXTexture__InverseDct8x8_DequantAndStore_Scalar(void * coefficient_block_rows, void * quant_table_rows, void * idct_workspace_rows, int * row_offset_table, int output_base, void * clamp_table)` | Scalar 8x8 inverse-DCT/dequantize/output-store helper. RET `0x18` and wrapper call `0x005bbe59` show six stack parameters; the body multiplies coefficient/quant rows, writes a workspace, then clamps and stores through row offsets/output base. |
| `0x005bbe70 CDXTexture__InverseDct8x8_DequantAndStore_Mmx` | `int __stdcall CDXTexture__InverseDct8x8_DequantAndStore_Mmx(void * coefficient_block_rows, void * quant_table_rows, void * idct_workspace_rows, int * row_offset_table, int output_base, void * clamp_table)` | Packed/MMX-style inverse-DCT twin. RET `0x18` and wrapper call `0x005bc569` show six stack parameters; the helper returns constant zero, which the wrapper does not inspect. |
| `0x005bcfa0 CDXTexture__InflateCodesState_Create` | `void * __stdcall CDXTexture__InflateCodesState_Create(int literal_bits, int distance_bits, void * literal_table, void * distance_table, void * inflate_stream)` | Inflate code-state allocator. RET `0x14` call sites pass literal/distance bit widths, literal/distance tables, and inflate stream; the body allocates a `0x1c`-byte state and returns it in EAX. |
| `0x005bcfd3 CDXTexture__InflateCodesState_Process` | `int __stdcall CDXTexture__InflateCodesState_Process(void * inflate_state, void * inflate_stream, int status_code)` | Inflate code-state processor. RET `0xc` and caller compare against EAX correct the stale `void` return to int status; body calls fast decode, output flush, and reports invalid literal/length or distance codes. |
| `0x005bd52a CDXTexture__InvokeReleaseCallback` | `void __stdcall CDXTexture__InvokeReleaseCallback(void * release_payload, void * inflate_stream)` | Two-argument release callback wrapper. RET `0x8`; body calls stream callback `+0x24` with user data `+0x28` and the release payload. |
| `0x005bd8ba CDXTexture__InflateDynamicTree_BuildBitLengthTree` | `int __stdcall CDXTexture__InflateDynamicTree_BuildBitLengthTree(int code_length_count, void * bit_length_count_out, void * tree_workspace, void * bit_length_order_table, void * inflate_stream)` | Dynamic bit-length Huffman tree builder. RET `0x14`; body allocates a `0x13`-entry work table, calls the Huffman builder, writes oversubscribed/incomplete tree errors, frees the table, and returns status. |
| `0x005bd933 CDXTexture__InflateDynamicTree_BuildLitDistTrees` | `int __stdcall CDXTexture__InflateDynamicTree_BuildLitDistTrees(int literal_length_count, int distance_count, void * code_lengths, void * literal_bits_out, void * distance_bits_out, void * literal_table_out, void * distance_table_out, void * tree_workspace, void * inflate_stream)` | Literal/length and distance Huffman tree builder. RET `0x24` and call site `0x005b23f3` show nine stack parameters, resolving the previous hidden allocator-stream stack slot and stale five-parameter signature. |
| `0x005bda2d CDXTexture__InflateFixedTrees_InitDescriptors` | `int __stdcall CDXTexture__InflateFixedTrees_InitDescriptors(void * literal_bits_out, void * distance_bits_out, void * literal_table_out, void * distance_table_out, void * inflate_stream)` | Fixed inflate descriptor initializer. RET `0x14`; body writes fixed literal/distance bit counts and fixed table pointers from the `DAT_0065ee58`/`DAT_0065ee5c`/`DAT_0065ee60`/`DAT_0065fe60` group. |
| `0x005bda5e CDXTexture__InflateOutputWindowFlush` | `int __stdcall CDXTexture__InflateOutputWindowFlush(void * inflate_state, void * inflate_stream, int status_code)` | Output-window flush helper. RET `0xc`; body copies pending ring-window bytes to the stream output buffer, invokes optional callback `+0x38`, updates counters, and returns status. |
| `0x005be360 CDXTexture__InflateFast_DecodeBlockStream` | `int __stdcall CDXTexture__InflateFast_DecodeBlockStream(int literal_bits, int distance_bits, void * literal_table, void * distance_table, void * inflate_state, void * inflate_stream)` | Fast literal/length-distance decoder. RET `0x18`; body uses mask table `DAT_0065ff60`, decodes literals/copy lengths/distances, returns `0`/`1`/`-3`, and writes invalid distance or invalid literal/length code errors. |

Wave738 read-back evidence verified `10` metadata rows, `10` tag rows, `18` xref rows, `2810` instruction rows, and `10` decompile rows, plus read-only caller/xref-site exports with `3` caller decompile rows and `1602` xref-site instruction rows. Dry/apply/final dry reported `updated=0 skipped=10 renamed=0 would_rename=0 signature_updated=10 comment_only_updated=0 missing=0 bad=0`, then `updated=10 skipped=0 renamed=0 would_rename=0 signature_updated=10 comment_only_updated=0 missing=0 bad=0`, then `updated=0 skipped=10 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`. The pass made no renames, made no function-boundary changes, and made no executable-byte changes. Post-Wave738 queue telemetry is `6098` total, `4349` commented, `1749` commentless, `1216` exact-undefined signatures, `36` `param_N`, strict clean-signature proxy `4291/6098 = 70.37%`, raw commentless head `0x0042f220 CSPtrSet__Clear`, and high-signal head `0x005be622 Direct3DCreate9`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260522-131329_post_wave738_cdxtexture_dct_inflate_tail_verified`.

Exact JPEG color pipeline role, exact SIMD equivalence, zlib version/source identity, stream/state layouts, callback ownership model, runtime image behavior, runtime decompression behavior, no-function wrapper boundaries beyond observed call/RET evidence, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave738 CDXTexture DCT/inflate tail`, `cdxtexture-dct-inflate-tail-wave738`, `0x005bb9b0 CDXTexture__InverseDct8x8_DequantAndStore_Scalar`, `0x005bbe70 CDXTexture__InverseDct8x8_DequantAndStore_Mmx`, `0x005bcfa0 CDXTexture__InflateCodesState_Create`, `0x005bcfd3 CDXTexture__InflateCodesState_Process`, `0x005bd52a CDXTexture__InvokeReleaseCallback`, `0x005bd8ba CDXTexture__InflateDynamicTree_BuildBitLengthTree`, `0x005bd933 CDXTexture__InflateDynamicTree_BuildLitDistTrees`, `0x005bda2d CDXTexture__InflateFixedTrees_InitDescriptors`, `0x005bda5e CDXTexture__InflateOutputWindowFlush`, `0x005be360 CDXTexture__InflateFast_DecodeBlockStream`, `0x005be622 Direct3DCreate9`, `0x0042f220 CSPtrSet__Clear`, `[maintainer-local-ghidra-backup-root]\BEA_20260522-131329_post_wave738_cdxtexture_dct_inflate_tail_verified`.

## Wave736 JPEG Scan Controller Head Read-Back Note

Wave736 JPEG scan controller head saved three adjacent CDXTexture JPEG scan-controller rows. Tag anchor: `jpeg-scan-controller-head-wave736`; the earliest raw commentless row after this pass is `0x0042f220 CSPtrSet__Clear`, and the next commentless high-signal row is `0x005b81d0 CFastVB__SinCosApproxVec4_Paired`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x005b7ee0 CDXTexture__ProcessJpegScanStateMachine` | `void __stdcall CDXTexture__ProcessJpegScanStateMachine(void * jpeg_codec_state)` | JPEG scan-controller process callback. RET `0x4` callback slot is installed by `CDXTexture__InitJpegScanController` at controller `+0x00`; the helper reads controller state from state `+0x154`, drives phases `0`, `1`, and `2`, loads scan descriptors, builds MCU layout, invokes color-converter/upsampler/sample-buffer controllers on the non-direct path, runs DCT/quant, entropy/scan-script, output, source/writer callbacks, mirrors progress into state `+8`, and reports error id `0x30` for unexpected phases. |
| `0x005b8060 CDXTexture__AbortJpegScanStateMachine` | `void __stdcall CDXTexture__AbortJpegScanStateMachine(void * jpeg_codec_state)` | JPEG scan-controller abort callback. RET `0x4` callback slot is installed at controller `+0x04`; the helper clears controller `+0xc` and invokes writer/source callbacks at state `+0x164 +4` and `+8`. |
| `0x005b8110 CDXTexture__InitJpegScanController` | `void __stdcall CDXTexture__InitJpegScanController(void * jpeg_codec_state, int scan_controller_start_mode)` | JPEG scan-controller initializer. RET `0x8` caller `CDXTexture__InitializeJpegEncoderPipeline` pushes a mode flag then `jpeg_codec_state`; it allocates a `0x24`-byte controller at state `+0x154`, installs process/abort/local callback slots at controller `+0x00/+0x04/+0x08`, validates frame MCU layout and optional scan script, derives controller `+0x14` from `scan_controller_start_mode` and state `+0xb8`, clears controller `+0x18/+0x20`, and stores scan count at controller `+0x1c`. |

Wave736 read-back evidence verified `3` metadata rows, `3` tag rows, `3` xref rows, `783` instruction rows, and `3` decompile rows, plus read-only caller/xref-site exports with `1` caller decompile row and `340` xref-site instruction rows. Dry/apply/final dry reported `updated=0 skipped=3 renamed=0 would_rename=0 signature_updated=3 comment_only_updated=0 missing=0 bad=0`, then `updated=3 skipped=0 renamed=0 would_rename=0 signature_updated=3 comment_only_updated=0 missing=0 bad=0`, then `updated=0 skipped=3 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`. The pass made no renames, made no function-boundary changes, and made no executable-byte changes. Post-Wave736 queue telemetry is `6098` total, `4333` commented, `1765` commentless, `1216` exact-undefined signatures, `45` `param_N`, strict clean-signature proxy `4275/6098 = 70.11%`, raw commentless head `0x0042f220 CSPtrSet__Clear`, and high-signal head `0x005b81d0 CFastVB__SinCosApproxVec4_Paired`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260522-120358_post_wave736_jpeg_scan_controller_head_verified`.

Exact scan-controller struct, scan script semantics, local callback boundary at `0x005b8090`, callback ABI, JPEG mode enums, runtime JPEG output behavior, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave736 JPEG scan controller head`, `jpeg-scan-controller-head-wave736`, `0x005b7ee0 CDXTexture__ProcessJpegScanStateMachine`, `0x005b8060 CDXTexture__AbortJpegScanStateMachine`, `0x005b8110 CDXTexture__InitJpegScanController`, `0x005b81d0 CFastVB__SinCosApproxVec4_Paired`, `0x0042f220 CSPtrSet__Clear`, `[maintainer-local-ghidra-backup-root]\BEA_20260522-120358_post_wave736_jpeg_scan_controller_head_verified`.

## Wave735 Color Converter Dispatch Head Read-Back Note

Wave735 color converter dispatch head saved three adjacent CDXTexture JPEG color-converter rows. Tag anchor: `color-converter-dispatch-head-wave735`; the earliest raw commentless row after this pass is `0x0042f220 CSPtrSet__Clear`, and the next commentless high-signal row is `0x005b7ee0 CDXTexture__ProcessJpegScanStateMachine`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x005b71b0 CDXTexture__ConvertRgbRowsToGrayscale` | `void __stdcall CDXTexture__ConvertRgbRowsToGrayscale(void * jpeg_codec_state, void * source_row_table, void * output_row_table, int output_start_row, int row_count)` | RGB-to-grayscale/luma converter. RET `0x14` callback slot is installed by `CDXTexture__InitColorConverterDispatch`; the helper reads pixel width from state `+0x1c`, dereferences source and destination row tables, combines three RGB byte channels through lookup-table bands at `0x0/0x400/0x800`, and writes one output byte per pixel. |
| `0x005b7480 CDXTexture__CopyInterleavedChannelRows` | `void __stdcall CDXTexture__CopyInterleavedChannelRows(void * jpeg_codec_state, void * source_row_table, void * output_row_table, int output_start_row, int row_count)` | Interleaved channel copy helper. RET `0x14` callback slot is installed for direct-compatible one/three-channel paths; the helper reads pixel width from state `+0x1c`, source stride from state `+0x24`, advances the source cursor by stride per pixel, and writes one output byte per pixel. |
| `0x005b7580 CDXTexture__InitColorConverterDispatch` | `void __stdcall CDXTexture__InitColorConverterDispatch(void * jpeg_codec_state)` | JPEG color-converter controller initializer. RET `0x4` caller `CDXTexture__InitializeJpegEncoderPipeline` reaches this helper when state `+0xb0` is zero; it allocates a `0xc`-byte controller at state `+0x168`, installs entry `0x005b0ed0`, validates color mode fields, reports error ids `9`, `10`, or `0x1b`, and installs callback slot `+4` with copy, grayscale, or local conversion labels. |

Wave735 read-back evidence verified `3` metadata rows, `3` tag rows, `3` xref rows, `435` instruction rows, and `3` decompile rows, plus read-only caller/xref-site exports with `2` caller decompile rows and `855` xref-site instruction rows. Dry/apply/final dry reported `updated=0 skipped=3 renamed=0 would_rename=0 signature_updated=3 comment_only_updated=0 missing=0 bad=0`, then `updated=3 skipped=0 renamed=0 would_rename=0 signature_updated=3 comment_only_updated=0 missing=0 bad=0`, then `updated=0 skipped=3 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`. The pass made no renames, made no function-boundary changes, and made no executable-byte changes. Post-Wave735 queue telemetry is `6098` total, `4330` commented, `1768` commentless, `1216` exact-undefined signatures, `48` `param_N`, strict clean-signature proxy `4272/6098 = 70.06%`, raw commentless head `0x0042f220 CSPtrSet__Clear`, and high-signal head `0x005b7ee0 CDXTexture__ProcessJpegScanStateMachine`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260522-113700_post_wave735_color_converter_dispatch_head_verified`.

The first direct pre-metadata export omitted `-noanalysis`; follow-up read-only quality evidence showed no queue telemetry drift before the accepted dry/apply/read-back pass. Exact color-mode enum, lookup-table schema, channel order, row-table ownership, destination component semantics, controller schema, local helper boundaries, callback ABI, runtime JPEG output behavior, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave735 color converter dispatch head`, `color-converter-dispatch-head-wave735`, `0x005b71b0 CDXTexture__ConvertRgbRowsToGrayscale`, `0x005b7480 CDXTexture__CopyInterleavedChannelRows`, `0x005b7580 CDXTexture__InitColorConverterDispatch`, `0x005b7ee0 CDXTexture__ProcessJpegScanStateMachine`, `0x0042f220 CSPtrSet__Clear`, `[maintainer-local-ghidra-backup-root]\BEA_20260522-113700_post_wave735_color_converter_dispatch_head_verified`.

## Wave734 JPEG DCT/Component/Upsampler Head Read-Back Note

Wave734 JPEG DCT/component/upsampler head saved eleven adjacent CDXTexture JPEG pipeline, component-buffer, row-padding, and upsampler dispatch rows. Tag anchor: `jpeg-dct-component-upsampler-head-wave734`; the earliest raw commentless row after this pass is `0x0042f220 CSPtrSet__Clear`, and the next commentless high-signal row is `0x005b71b0 CDXTexture__ConvertRgbRowsToGrayscale`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x005b5b80 CDXTexture__InitJpegDctQuantPipeline` | `void __stdcall CDXTexture__InitJpegDctQuantPipeline(void * jpeg_codec_state)` | DCT/quant controller initializer. RET `0x4` caller `CDXTexture__InitializeJpegEncoderPipeline` reaches this helper; it allocates a `0x30`-byte controller at state `+0x170`, dispatches mode field `+0xc4`, installs controller/callback entries including `0x005b4b20`, `0x005b4ed0`, `0x005be000`, `0x005bdda0`, `0x005b5370`, and `0x005bdb70`, and reports error id `0x30` for unsupported modes. |
| `0x005b60a0 CDXTexture__BuildComponentWorkBufferViews` | `void __stdcall CDXTexture__BuildComponentWorkBufferViews(void * jpeg_codec_state)` | Component work-buffer view builder. RET `0x4` helper allocates a component-count by row-count slab, calls allocator callback `+8` per component, copies row pointer ranges, and stores per-component view-table pointers through controller state `+0x15c/+8`. |
| `0x005b61e0 CDXTexture__InitComponentSampleBuffers` | `void __stdcall CDXTexture__InitComponentSampleBuffers(void * jpeg_codec_state, int sample_buffer_mode)` | Component sample-buffer controller initializer. RET `0x8` nonzero `sample_buffer_mode` raises error id `4`; direct mode installs entry `0x005b5c80`, while the alternate path installs `0x005b5e90` and calls `CDXTexture__BuildComponentWorkBufferViews`. |
| `0x005b6290 CDXTexture__PadRowsWithLastSample` | `void __stdcall CDXTexture__PadRowsWithLastSample(void * row_table, int row_count, int valid_width_bytes, int padded_width_bytes)` | Row-padding helper. RET `0x10` repeats each row's last valid byte from `valid_width_bytes` to `padded_width_bytes`; callers include scalar/SSE horizontal and bilinear upsamplers plus nearby unfenced helpers. |
| `0x005b6500 CDXTexture__UpsampleHorizontal_Average2_Scalar` | `void __fastcall CDXTexture__UpsampleHorizontal_Average2_Scalar(void * source_row_table, void * component_descriptor, void * output_row_table)` | Scalar horizontal average-2 upsampler. Dispatch loads hidden EAX with `jpeg_codec_state`, ECX with `source_row_table`, EDX with `component_descriptor`, and pushes `output_row_table`; the helper pads source rows and writes averaged adjacent horizontal samples. |
| `0x005b65a0 CDXTexture__UpsampleHorizontal_Average2_Sse` | `void __fastcall CDXTexture__UpsampleHorizontal_Average2_Sse(void * component_descriptor, void * jpeg_codec_state, void * source_row_table, void * output_row_table)` | Packed/SSE horizontal average-2 upsampler. Selected by aligned dispatch paths; pads source rows, uses `DAT_005f4c00` and `DAT_005f4bf0`, combines adjacent packed samples, clamps bytes, and writes output rows. |
| `0x005b6650 CDXTexture__UpsampleBilinear2x2_Scalar` | `void __fastcall CDXTexture__UpsampleBilinear2x2_Scalar(void * source_row_table, void * component_descriptor, void * output_row_table)` | Scalar bilinear 2x2 upsampler. Dispatch loads hidden EAX with `jpeg_codec_state`, ECX with `source_row_table`, EDX with `component_descriptor`, and pushes `output_row_table`; the helper pads source rows and averages current/next row samples. |
| `0x005b6720 CDXTexture__UpsampleBilinear2x2_Sse` | `void __fastcall CDXTexture__UpsampleBilinear2x2_Sse(void * component_descriptor, void * jpeg_codec_state, void * source_row_table, void * output_row_table)` | Packed/SSE bilinear 2x2 upsampler. Selected by aligned dispatch paths; pads source rows, uses `DAT_005f4c10` and `DAT_005f4c08`, averages packed current/next row samples, clamps bytes, and writes output rows. |
| `0x005b6c30 CDXTexture__UpsampleDispatchHorizontal` | `void __stdcall CDXTexture__UpsampleDispatchHorizontal(void * jpeg_codec_state, void * component_descriptor, void * source_row_table, void * output_row_table)` | Horizontal upsampler dispatcher. RET `0x10` checks source-row alignment, reports error id `2` on unaligned input, selects the SSE helper for modes `5` or `6`, otherwise falls back to the scalar helper while preserving hidden EAX for the scalar path. |
| `0x005b6c90 CDXTexture__UpsampleDispatchBilinear` | `void __stdcall CDXTexture__UpsampleDispatchBilinear(void * jpeg_codec_state, void * component_descriptor, void * source_row_table, void * output_row_table)` | Bilinear upsampler dispatcher. RET `0x10` uses the same source-row alignment and mode `5`/`6` SSE gate as the horizontal dispatcher, otherwise falls back to the scalar helper while preserving hidden EAX for the scalar path. |
| `0x005b6cf0 CDXTexture__InitUpsamplerDispatch` | `void __stdcall CDXTexture__InitUpsamplerDispatch(void * jpeg_codec_state)` | Upsampler dispatch/controller initializer. RET `0x4` allocates a `0x34`-byte controller at state `+0x16c`, installs entries `0x005b0ed0` and `0x005b62f0`, walks component descriptors, chooses passthrough/horizontal/bilinear/generic entries based on sampling ratios, and reports error ids `0x19`, `0x26`, or `99` for unsupported paths. |

Wave734 read-back evidence verified `11` metadata rows, `11` tag rows, `17` xref rows, `1595` instruction rows, and `11` decompile rows, plus read-only caller/xref-site exports with `5` caller decompile rows and `765` xref-site instruction rows. Dry/apply/final dry reported `updated=0 skipped=11 renamed=0 would_rename=0 signature_updated=11 comment_only_updated=0 missing=0 bad=0`, then `updated=11 skipped=0 renamed=0 would_rename=0 signature_updated=11 comment_only_updated=0 missing=0 bad=0`, then `updated=0 skipped=11 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`. The pass made no renames, made no function-boundary changes, and made no executable-byte changes. Post-Wave734 queue telemetry is `6098` total, `4327` commented, `1771` commentless, `1216` exact-undefined signatures, `51` `param_N`, strict clean-signature proxy `4269/6098 = 70.01%`, raw commentless head `0x0042f220 CSPtrSet__Clear`, and high-signal head `0x005b71b0 CDXTexture__ConvertRgbRowsToGrayscale`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260522-110534_post_wave734_jpeg_dct_component_upsampler_head_verified`.

Exact JPEG state layout, DCT/quant controller schema, component descriptor schema, sample-buffer layout, row-table ownership, hidden EAX ABI on scalar upsamplers, SIMD/scalar equivalence, mode enum, sampling-ratio schema, runtime JPEG output behavior, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave734 JPEG DCT/component/upsampler head`, `jpeg-dct-component-upsampler-head-wave734`, `0x005b5b80 CDXTexture__InitJpegDctQuantPipeline`, `0x005b60a0 CDXTexture__BuildComponentWorkBufferViews`, `0x005b61e0 CDXTexture__InitComponentSampleBuffers`, `0x005b6290 CDXTexture__PadRowsWithLastSample`, `0x005b6500 CDXTexture__UpsampleHorizontal_Average2_Scalar`, `0x005b65a0 CDXTexture__UpsampleHorizontal_Average2_Sse`, `0x005b6650 CDXTexture__UpsampleBilinear2x2_Scalar`, `0x005b6720 CDXTexture__UpsampleBilinear2x2_Sse`, `0x005b6c30 CDXTexture__UpsampleDispatchHorizontal`, `0x005b6c90 CDXTexture__UpsampleDispatchBilinear`, `0x005b6cf0 CDXTexture__InitUpsamplerDispatch`, `0x005b71b0 CDXTexture__ConvertRgbRowsToGrayscale`, `0x0042f220 CSPtrSet__Clear`, `[maintainer-local-ghidra-backup-root]\BEA_20260522-110534_post_wave734_jpeg_dct_component_upsampler_head_verified`.

## Wave733 JPEG Entropy/Frequency Head Read-Back Note

Wave733 JPEG entropy/frequency head saved nine adjacent CDXTexture JPEG entropy frequency, canonical-Huffman, restart, bit-writer, and scan-script rows. Tag anchor: `jpeg-entropy-frequency-head-wave733`; the earliest raw commentless row after this pass is `0x0042f220 CSPtrSet__Clear`, and the next commentless high-signal row is `0x005b5b80 CDXTexture__InitJpegDctQuantPipeline`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x005b3840 CDXTexture__AccumulateJpegHuffmanFrequenciesFromBlock` | `void __stdcall CDXTexture__AccumulateJpegHuffmanFrequenciesFromBlock(void * jpeg_encoder_state, void * coeff_block, void * ac_frequency_counts)` | JPEG Huffman frequency accumulator. RET `0xc` caller `CDXTexture__EncodeMcuBlocksForScan` supplies hidden ECX as previous DC value, hidden EAX as the DC frequency table, and stack arguments for encoder state, coefficient block, and AC frequency counts; the helper computes DC category, walks AC coefficients through zig-zag table `DAT_005f37fc`, increments ZRL bucket `+0x3c0` and EOB bucket `0`, and updates AC run/size buckets. |
| `0x005b3920 CDXTexture__EncodeMcuBlocksForScan` | `int __stdcall CDXTexture__EncodeMcuBlocksForScan(void * jpeg_encoder_state, void * coeff_block_table)` | JPEG active-scan MCU frequency-count pass. RET `0x8` helper refreshes restart-interval counters at entropy state `+0x24`, zeroes per-component DC predictors at `+0x14` when a restart interval begins, loops scan component order from encoder state `+0x11c`, calls the frequency accumulator with component DC/AC frequency tables, and stores each block's first coefficient as the next DC predictor. |
| `0x005b39d0 CDXTexture__BuildCanonicalHuffmanCodes` | `void __stdcall CDXTexture__BuildCanonicalHuffmanCodes(void * jpeg_encoder_state, void * out_huffman_descriptor, void * frequency_counts)` | JPEG canonical-Huffman descriptor builder. RET `0xc` callers pass encoder state, output descriptor, and frequency-count table; the helper creates code lengths for `0x101` symbols, validates depth with error id `0x27`, applies the JPEG 16-bit length limit, writes count/symbol bytes, and clears descriptor `+0x114`. |
| `0x005b3e80 CDXTexture__InitJpegEntropyEncoderState` | `void __stdcall CDXTexture__InitJpegEntropyEncoderState(void * jpeg_encoder_state)` | JPEG entropy-state initializer. RET `0x4` caller `CDXTexture__InitializeJpegEncoderPipeline` selects this path when scan-script state is not used; the helper allocates a `0x6c`-byte controller through encoder allocator callback `+4`, stores it at encoder state `+0x174`, installs entry `0x005b3d20`, and clears component DC/restart/frequency slots. |
| `0x005b3ec0 CDXTexture__WriteEntropyBitsWithByteStuffing` | `void __stdcall CDXTexture__WriteEntropyBitsWithByteStuffing(uint bit_value)` | JPEG entropy bit writer. RET `0x4` callers pass `bit_value` on the stack while hidden EAX supplies bit count and hidden ESI supplies the writer/controller; the helper emits full bytes, refreshes the host output buffer through owner callback `+0x18`, and inserts a stuffed zero byte after emitted `0xff`. |
| `0x005b3fd0 CDXTexture__FlushEntropyBitWriter` | `void CDXTexture__FlushEntropyBitWriter(void)` | Comment/tag-only. Locked hidden-EAX helper that flushes pending entropy state through the bit writer in output mode, increments frequency buckets in frequency-collection mode, drains queued literal bytes from state `+0x40`, and clears pending counters at `+0x38/+0x3c`. |
| `0x005b4080 CDXTexture__EmitRestartMarkerAndReset` | `void __stdcall CDXTexture__EmitRestartMarkerAndReset(int restart_marker_code)` | JPEG restart-marker helper. RET `0x4` callers pass restart marker code while hidden EAX supplies the entropy writer/controller; the helper flushes pending bits, writes `0xff` plus marker byte, refreshes output, clears bit-buffer fields, and resets DC predictors or scan-script pending counters depending on mode. |
| `0x005b44c0 CDXTexture__WriteEncodedBlockWithRestartControl` | `int __stdcall CDXTexture__WriteEncodedBlockWithRestartControl(void * jpeg_encoder_state, void * coeff_block_table)` | JPEG encoded-block restart-control path. RET `0x8` helper snapshots output cursor fields, emits a restart marker when countdown `+0x44` reaches zero, loops scan components from encoder state `+0x118`, writes shifted first coefficients through the bit writer, restores output state, advances marker index modulo 8, and decrements the interval countdown. |
| `0x005b4ae0 CDXTexture__InitJpegEncoderScanScriptState` | `void __stdcall CDXTexture__InitJpegEncoderScanScriptState(void * jpeg_encoder_state)` | Alternate JPEG scan-script state initializer. RET `0x4` caller `CDXTexture__InitializeJpegEncoderPipeline` selects this path when the scan-script mode flag is set; the helper allocates a `0x6c`-byte controller through encoder allocator callback `+4`, stores it at encoder state `+0x174`, installs entry `0x005b4950`, clears component table slots, and clears state `+0x40`. |

Wave733 read-back evidence verified `9` metadata rows, `9` tag rows, `36` xref rows, `3069` instruction rows, and `9` decompile rows, plus read-only caller/context exports with `5` caller decompile rows and `713` xref-site instruction rows. Dry/apply/reconcile/final dry reported `updated=0 skipped=9 renamed=0 would_rename=0 signature_updated=8 comment_only_updated=1 missing=0 bad=0`; an initial apply saved eight rows and stopped on the expected `0x005b3840` Ghidra synthetic `__thiscall` read-back mismatch; accepted reconcile dry/apply reported `updated=0 skipped=9 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0` and `updated=1 skipped=8 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0`; final dry reported `updated=0 skipped=9 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`. The pass made no renames, made no function-boundary changes, and made no executable-byte changes. Post-Wave733 queue telemetry is `6098` total, `4316` commented, `1782` commentless, `1216` exact-undefined signatures, `62` `param_N`, strict clean-signature proxy `4258/6098 = 69.83%`, raw commentless head `0x0042f220 CSPtrSet__Clear`, and high-signal head `0x005b5b80 CDXTexture__InitJpegDctQuantPipeline`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260522-103248_post_wave733_jpeg_entropy_frequency_head_verified`.

Exact coefficient layout, scan layout, coefficient-block table layout, hidden ECX/EAX ABI, hidden EAX/ESI ABI, Huffman table and descriptor schemas, entropy-state layout, callback table contract, marker-code enum, restart-interval policy, scan-script-state layout, runtime JPEG output behavior, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave733 JPEG entropy/frequency head`, `jpeg-entropy-frequency-head-wave733`, `0x005b3840 CDXTexture__AccumulateJpegHuffmanFrequenciesFromBlock`, `0x005b3920 CDXTexture__EncodeMcuBlocksForScan`, `0x005b39d0 CDXTexture__BuildCanonicalHuffmanCodes`, `0x005b3e80 CDXTexture__InitJpegEntropyEncoderState`, `0x005b3ec0 CDXTexture__WriteEntropyBitsWithByteStuffing`, `0x005b3fd0 CDXTexture__FlushEntropyBitWriter`, `0x005b4080 CDXTexture__EmitRestartMarkerAndReset`, `0x005b44c0 CDXTexture__WriteEncodedBlockWithRestartControl`, `0x005b4ae0 CDXTexture__InitJpegEncoderScanScriptState`, `0x005b5b80 CDXTexture__InitJpegDctQuantPipeline`, `0x0042f220 CSPtrSet__Clear`, `[maintainer-local-ghidra-backup-root]\BEA_20260522-103248_post_wave733_jpeg_entropy_frequency_head_verified`.

## Wave732 JPEG Encoder Buffer/Entropy Head Read-Back Note

Wave732 JPEG encoder buffer/entropy head saved six adjacent CDXTexture/CFastVB JPEG encoder buffer and entropy rows. Tag anchor: `jpeg-encoder-buffer-entropy-head-wave732`; the earliest raw commentless row after this pass is `0x0042f220 CSPtrSet__Clear`, and the next commentless high-signal row is `0x005b3840 CDXTexture__AccumulateJpegHuffmanFrequenciesFromBlock`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x005b2860 CDXTexture__InitJpegEncoderComponentBuffers` | `void __stdcall CDXTexture__InitJpegEncoderComponentBuffers(void * jpeg_encoder_state, int component_buffer_mode)` | JPEG component-buffer controller initializer. RET `0x8` caller `CDXTexture__InitializeJpegEncoderPipeline` pushes encoder state and a zero mode flag; the helper allocates a `0x40`-byte controller at state `+0x158`, stores vtable entry `0x005b2810`, and allocates per-component buffers through allocator callback `+0x8` when state `+0xb0` and the mode flag allow it. |
| `0x005b3080 CDXTexture__InitJpegEncoderWorkingBuffers` | `void __stdcall CDXTexture__InitJpegEncoderWorkingBuffers(void * jpeg_encoder_state, int component_work_buffer_mode)` | JPEG working-buffer controller initializer. RET `0x8` caller computes a mode flag from state `+0xa8` and `+0xb8`; flag zero allocates a `0x500`-byte table slab and installs ten `0x80`-spaced table pointers, while nonzero mode allocates aligned per-component working buffers through allocator callback `+0x14`. |
| `0x005b3170 CDXTexture__BuildJpegHuffmanEncodeTable` | `void __stdcall CDXTexture__BuildJpegHuffmanEncodeTable(void * jpeg_encoder_state, int table_class, int table_index, void * out_encode_table)` | JPEG Huffman encode-table builder. RET `0x10` inputs are encoder state, table class selector, table index, and output table pointer; the helper validates table index 0..3, selects state `+0x68` or `+0x58` descriptor tables by class selector, allocates a `0x500`-byte encode table when needed, and writes canonical per-symbol code/length entries. |
| `0x005b3370 CFastVB__JpegEntropy_WriteBitsWithByteStuffing_005b3370` | `int __stdcall CFastVB__JpegEntropy_WriteBitsWithByteStuffing_005b3370(uint bit_value)` | JPEG entropy bit writer with byte stuffing. RET `0x4` callers pass `bit_value` on the stack while hidden EAX supplies bit count and hidden ESI supplies bit-writer state; the helper writes output bytes, refreshes through owner callback `+0x18`, and inserts `0x00` after emitted `0xff` bytes. |
| `0x005b3440 CFastVB__JpegEntropy_EncodeBlockZigZagHuffman` | `int __stdcall CFastVB__JpegEntropy_EncodeBlockZigZagHuffman(void * coeff_block, int previous_dc_value, void * dc_huffman_table, void * ac_huffman_table)` | JPEG 8x8 block entropy encoder. RET `0x10` visible stack arguments carry coefficient block, previous DC value, and DC/AC Huffman tables while hidden EAX supplies bit-writer state; the helper emits DC category/magnitude bits, walks AC coefficients through zig-zag table `DAT_005f37fc`, emits ZRL from AC table `+0x3c0`, and emits EOB from the AC table head. |
| `0x005b35b0 CFastVB__JpegEntropy_WriteMarkerAndResetDcPredictors` | `int __stdcall CFastVB__JpegEntropy_WriteMarkerAndResetDcPredictors(int restart_marker_code)` | JPEG entropy marker/restart path. RET `0x4` helper uses hidden EAX bit-writer state, flushes pending bits with value `0x7f`, writes marker prefix `0xff`, clears bit-buffer fields, emits a marker byte derived from the stack code, refreshes output as needed, and zeroes per-component DC predictors from owner state `+0xfc`. |

Wave732 read-back evidence verified `6` metadata rows, `6` tag rows, `15` xref rows, `606` instruction rows, and `6` decompile rows, plus read-only caller/context exports with `4` decompile rows and `524` instruction rows. Dry/apply/final dry reported `updated=0 skipped=6 renamed=0 would_rename=0 signature_updated=6 missing=0 bad=0`, then `updated=6 skipped=0 renamed=0 would_rename=0 signature_updated=6 missing=0 bad=0`, then `updated=0 skipped=6 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`. The pass made no renames, made no function-boundary changes, and made no executable-byte changes. Post-Wave732 queue telemetry is `6098` total, `4307` commented, `1791` commentless, `1216` exact-undefined signatures, `70` `param_N`, strict clean-signature proxy `4249/6098 = 69.68%`, raw commentless head `0x0042f220 CSPtrSet__Clear`, and high-signal head `0x005b3840 CDXTexture__AccumulateJpegHuffmanFrequenciesFromBlock`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260522-095636_post_wave732_jpeg_encoder_buffer_entropy_head_verified`.

Exact JPEG encoder-state/component/controller layouts, component and work-buffer mode semantics, allocator callback contracts, table class enum, descriptor layouts, coefficient block layout, hidden-register ABI, writer/owner layout, restart marker policy, runtime JPEG output behavior, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave732 JPEG encoder buffer/entropy head`, `jpeg-encoder-buffer-entropy-head-wave732`, `0x005b2860 CDXTexture__InitJpegEncoderComponentBuffers`, `0x005b3080 CDXTexture__InitJpegEncoderWorkingBuffers`, `0x005b3170 CDXTexture__BuildJpegHuffmanEncodeTable`, `0x005b3370 CFastVB__JpegEntropy_WriteBitsWithByteStuffing_005b3370`, `0x005b3440 CFastVB__JpegEntropy_EncodeBlockZigZagHuffman`, `0x005b35b0 CFastVB__JpegEntropy_WriteMarkerAndResetDcPredictors`, `0x005b3840 CDXTexture__AccumulateJpegHuffmanFrequenciesFromBlock`, `0x0042f220 CSPtrSet__Clear`, `[maintainer-local-ghidra-backup-root]\BEA_20260522-095636_post_wave732_jpeg_encoder_buffer_entropy_head_verified`.

## Wave731 Inflate Utility Head Read-Back Note

Wave731 inflate utility head saved five adjacent CDXTexture inflate utility rows. Tag anchor: `inflate-utility-head-wave731`; the earliest raw commentless row after this pass is `0x0042f220 CSPtrSet__Clear`, and the next commentless high-signal row is `0x005b2860 CDXTexture__InitJpegEncoderComponentBuffers`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x005b1e16 CDXTexture__InflateBuildFixedHuffmanTables` | `void * __stdcall CDXTexture__InflateBuildFixedHuffmanTables(void * inflate_stream, void * state_callback, uint window_size_bytes)` | Fixed-Huffman/window state initializer. RET `0xc` caller passes inflate stream, state callback, and window size; the helper allocates a `0x40`-byte state, a `0x5a0`-byte fixed Huffman table, and a window buffer, stores the callback at state `+0x38`, calls `CDXTexture__ResetDecodeWindowState`, and returns the state pointer or null. |
| `0x005b1e94 CDXTexture__InflateProcessBlockHeader` | `int __stdcall CDXTexture__InflateProcessBlockHeader(void * inflate_state, void * inflate_stream, int status_code)` | Inflate block-state machine. RET `0xc` caller `CDXTexture__InflateStream_ProcessZlibState` passes inflate state, stream, and status/flush code, then consumes EAX as a zlib-style status; this narrows prior `extraout_EAX` uncertainty for this helper while downstream helper ABIs remain deferred. |
| `0x005b25e0 CDXTexture__CloseAsyncDecodeHandles` | `int __stdcall CDXTexture__CloseAsyncDecodeHandles(void * inflate_state, void * inflate_stream)` | Async-decode cleanup helper. RET `0x8` caller passes inflate state and stream; the helper resets decode-window state, frees the window buffer, frees table/state allocations through the stream callbacks, and returns `0`. |
| `0x005b2613 CDXTexture__Adler32_Update` | `uint __stdcall CDXTexture__Adler32_Update(uint adler, void * source_buffer, uint byte_count)` | Adler-32 checksum helper. RET `0xc` inputs are checksum seed, source buffer, and byte count; null source returns `1`, non-null input processes `0x15b0`-byte chunks, reduces modulo `0xfff1`, and returns the packed checksum. |
| `0x005b272e CDXTexture__InflateDefaultAllocCallback` | `void * __stdcall CDXTexture__InflateDefaultAllocCallback(void * opaque, uint item_count, uint item_size)` | Default inflate allocator callback. RET `0xc` inputs are opaque, item count, and item size; opaque is unused, the helper calls `GetProcessHeap`, allocates with `HeapAlloc` flag `8`, and returns the allocated pointer in EAX. |

Wave731 read-back evidence verified `5` metadata rows, `5` tag rows, `6` xref rows, `2705` instruction rows, and `5` decompile rows, plus caller context exports with `3` decompile rows and `1143` instruction rows. Dry/apply/final dry reported `updated=0 skipped=5 renamed=0 would_rename=0 signature_updated=5 missing=0 bad=0`, then `updated=5 skipped=0 renamed=0 would_rename=0 signature_updated=5 missing=0 bad=0`, then `updated=0 skipped=5 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`. The pass made no renames, made no function-boundary changes, and made no executable-byte changes. Post-Wave731 queue telemetry is `6098` total, `4301` commented, `1797` commentless, `1216` exact-undefined signatures, `76` `param_N`, strict clean-signature proxy `4243/6098 = 69.58%`, raw commentless head `0x0042f220 CSPtrSet__Clear`, and high-signal head `0x005b2860 CDXTexture__InitJpegEncoderComponentBuffers`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260522-092519_post_wave731_inflate_utility_head_verified`.

Exact z_stream layout, inflate-state layout, callback ABI, downstream helper ABIs, allocator ownership/lifetime, block enum names, checksum source identity, runtime inflate behavior, runtime decode behavior, runtime heap behavior, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave731 inflate utility head`, `inflate-utility-head-wave731`, `0x005b1e16 CDXTexture__InflateBuildFixedHuffmanTables`, `0x005b1e94 CDXTexture__InflateProcessBlockHeader`, `0x005b25e0 CDXTexture__CloseAsyncDecodeHandles`, `0x005b2613 CDXTexture__Adler32_Update`, `0x005b272e CDXTexture__InflateDefaultAllocCallback`, `0x005b2860 CDXTexture__InitJpegEncoderComponentBuffers`, `0x0042f220 CSPtrSet__Clear`, `[maintainer-local-ghidra-backup-root]\BEA_20260522-092519_post_wave731_inflate_utility_head_verified`.

## Wave730 Aligned Window Prelude Read-Back Note

Wave730 aligned window prelude saved six adjacent CDXTexture aligned allocation, byte-budget, host I/O callback, default-budget, and decode-window reset rows. Tag anchor: `aligned-window-prelude-wave730`; the earliest raw commentless row after this pass is `0x0042f220 CSPtrSet__Clear`, and the next commentless high-signal row is `0x005b1e16 CDXTexture__InflateBuildFixedHuffmanTables`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x005b1c00 CDXTexture__AllocAligned16` | `void * __stdcall CDXTexture__AllocAligned16(void * allocator_owner, uint requested_size_bytes)` | Aligned allocation callback used by decode allocator helpers. RET `0x8` callers push allocator owner and requested size; the helper allocates `requested_size_bytes + 0x10`, returns a 16-byte-aligned payload pointer, and stores the base-pointer byte delta at `aligned_payload - 1`. |
| `0x005b1c30 CDXTexture__FreeAligned16` | `void __stdcall CDXTexture__FreeAligned16(void * allocator_owner, void * aligned_payload, uint tracked_size_bytes)` | Aligned free callback paired with `CDXTexture__AllocAligned16`. RET `0xc` callers pass allocator owner, aligned payload, and tracked size; the helper reads the byte delta, recovers the original malloc base pointer, and frees it through `CRT__FreeBase`. |
| `0x005b1c50 CDXTexture__GetBufferTailAvailable` | `int __stdcall CDXTexture__GetBufferTailAvailable(void * allocator_owner, int row_count_hint, int minimum_chunk_bytes, int committed_size_bytes)` | Byte-budget helper used by the row-allocation prelude. RET `0x10` caller context at `0x0059bf5a` pushes allocator owner, row-count hint, minimum chunk bytes, and committed bytes; the helper reads allocator state at owner `+4`, loads state `+0x2c`, and returns `budget_or_cap - committed_size_bytes`. |
| `0x005b1d50 CDXTexture__InitHostIoCallbacks` | `void __stdcall CDXTexture__InitHostIoCallbacks(void * decode_context, void * host_io_callbacks, uint window_size_bytes)` | Host I/O callback initializer for decode-window spill paths. RET `0xc` caller context at `0x0059bfb1/0x0059c027` passes decode context, callback table, and window size; the helper opens a temp binary stream, stores it at callback table `+0xc`, reports `0x3f` on failure, and installs entries at `0x005b1c70`, `0x005b1cd0`, and `0x005b1d30`. |
| `0x005b1da0 CDXTexture__GetDefaultDecodeBudgetBytes` | `int __cdecl CDXTexture__GetDefaultDecodeBudgetBytes(void)` | No-argument helper returning the default decode allocator budget value `1000000`, consumed by `CDXTexture__InitDecodeAllocatorVtable` before aligned allocation of the `0x54`-byte allocator state. |
| `0x005b1db0 CDXTexture__ResetDecodeWindowState` | `void __stdcall CDXTexture__ResetDecodeWindowState(void * inflate_state, void * host_io_state, void * previous_cookie_out)` | Decode-window reset helper called by async-decode begin, fixed-Huffman table setup, async handle close, and zlib stream processing. The helper snapshots the cookie, releases modes `4`/`5` and `6`, resets output pointers at `+0x30/+0x34`, clears accumulator state, and can invoke the state callback at `+0x38`. |

Wave730 read-back evidence verified `6` metadata rows, `6` tag rows, `15` xref rows, `3246` instruction rows, and `6` decompile rows. Dry/apply/final dry reported `updated=0 skipped=6 renamed=0 would_rename=0 signature_updated=6 missing=0 bad=0`, then `updated=6 skipped=0 renamed=0 would_rename=0 signature_updated=6 missing=0 bad=0`, then `updated=0 skipped=6 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`. The pass made no renames, made no function-boundary changes, and made no executable-byte changes. Post-Wave730 queue telemetry is `6098` total, `4296` commented, `1802` commentless, `1216` exact-undefined signatures, `81` `param_N`, strict clean-signature proxy `4238/6098 = 69.50%`, raw commentless head `0x0042f220 CSPtrSet__Clear`, and high-signal head `0x005b1e16 CDXTexture__InflateBuildFixedHuffmanTables`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260522-085034_post_wave730_aligned_window_prelude_verified`.

Exact allocator-owner/state layout, row-batch schema, budget semantics, callback table layout, temp-file policy, error surface, inflate-state layout, callback ABI, mode enum, runtime texture behavior, runtime zlib/decode behavior, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave730 aligned window prelude`, `aligned-window-prelude-wave730`, `0x005b1c00 CDXTexture__AllocAligned16`, `0x005b1c30 CDXTexture__FreeAligned16`, `0x005b1c50 CDXTexture__GetBufferTailAvailable`, `0x005b1d50 CDXTexture__InitHostIoCallbacks`, `0x005b1da0 CDXTexture__GetDefaultDecodeBudgetBytes`, `0x005b1db0 CDXTexture__ResetDecodeWindowState`, `0x005b1e16 CDXTexture__InflateBuildFixedHuffmanTables`, `0x0042f220 CSPtrSet__Clear`, `[maintainer-local-ghidra-backup-root]\BEA_20260522-085034_post_wave730_aligned_window_prelude_verified`.

## Wave729 Scanline Color Converter Head Read-Back Note

Wave729 scanline color converter head saved five adjacent CDXTexture scanline/color-transform rows. Tag anchor: `scanline-color-converter-head-wave729`; the earliest raw commentless row after this pass is `0x0042f220 CSPtrSet__Clear`, and the next commentless high-signal row is `0x005b1c00 CDXTexture__AllocAligned16`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x005b0ee0 CDXTexture__InitScanlineColorConverter` | `void __stdcall CDXTexture__InitScanlineColorConverter(void * decode_context)` | Allocates a `0x40`-byte controller through the context allocator, stores it at decode_context `+0x1cc`, validates component/count combinations from decode_context `+0x24/+0x28/+0x2c`, installs row conversion callbacks, calls the Wave728 YCC lookup-table builders, and writes selected output component counts at decode_context `+0x78/+0x7c`. |
| `0x005b10b0 CDXTexture__InitColorTransformLuts` | `void CDXTexture__InitColorTransformLuts(void)` | Comment/tag-only. Uses hidden EAX as the texture decode context, reads the color-transform controller at context `+0x1c8`, allocates four lookup buffers through the context allocator, stores them at controller `+0x10` through `+0x1c`, and fills fixed-point transform tables using `LAB_005b6900` as a clamp/base table. |
| `0x005b1400 CDXTexture__ConvertYccScanlinePairToRgb_Scalar` | `void __fastcall CDXTexture__ConvertYccScanlinePairToRgb_Scalar(void * decode_context, int row_pair_index, void * output_rgb_row_pair_table)` | Scalar row-pair YCC-to-RGB converter. Visible fastcall parameters carry decode_context, row_pair_index, and output RGB row-pair table; wrapper `0x005b1b40` passes the source component row table through hidden EAX for this scalar path. |
| `0x005b1630 CDXTexture__ConvertYccScanlinePairToRgb_Sse` | `void __fastcall CDXTexture__ConvertYccScanlinePairToRgb_Sse(void * decode_context, int row_pair_index, void * source_component_row_table)` | SSE row-pair YCC-to-RGB converter. Visible fastcall parameters carry decode_context, row_pair_index, and source component row table; wrapper `0x005b1b40` passes the output RGB row-pair table through hidden EAX for this SSE path. |
| `0x005b1b80 CDXTexture__InitColorTransformContext` | `void __stdcall CDXTexture__InitColorTransformContext(void * decode_context)` | Allocates a `0x30`-byte controller at decode_context `+0x1c8`, stores callback slots for the scalar/SSE row-pair bridge at `0x005b1b40`, optionally allocates the SSE scratch/output buffer, and calls `CDXTexture__InitColorTransformLuts` through hidden EAX context setup. |

Wave729 read-back evidence verified `5` metadata rows, `5` tag rows, `6` xref rows, `2705` instruction rows, and `5` decompile rows. Dry/apply/final dry reported `updated=0 skipped=5 renamed=0 would_rename=0 signature_updated=4 comment_only_updated=1 missing=0 bad=0`, then `updated=5 skipped=0 renamed=0 would_rename=0 signature_updated=4 comment_only_updated=1 missing=0 bad=0`, then `updated=0 skipped=5 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`. The pass made no renames, made no function-boundary changes, and made no executable-byte changes. Post-Wave729 queue telemetry is `6098` total, `4290` commented, `1808` commentless, `1216` exact-undefined signatures, `86` `param_N`, strict clean-signature proxy `4232/6098 = 69.40%`, raw commentless head `0x0042f220 CSPtrSet__Clear`, and high-signal head `0x005b1c00 CDXTexture__AllocAligned16`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260522-082119_post_wave729_scanline_color_converter_head_verified`.

Exact decode context layout, controller layout, callback ABI, row-table schemas, hidden EAX ABI, RGB byte order, coefficient identity, SIMD/scalar equivalence, runtime JPEG/color conversion behavior, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave729 scanline color converter head`, `scanline-color-converter-head-wave729`, `0x005b0ee0 CDXTexture__InitScanlineColorConverter`, `0x005b10b0 CDXTexture__InitColorTransformLuts`, `0x005b1400 CDXTexture__ConvertYccScanlinePairToRgb_Scalar`, `0x005b1630 CDXTexture__ConvertYccScanlinePairToRgb_Sse`, `0x005b1b80 CDXTexture__InitColorTransformContext`, `0x005b1c00 CDXTexture__AllocAligned16`, `0x0042f220 CSPtrSet__Clear`, `[maintainer-local-ghidra-backup-root]\BEA_20260522-082119_post_wave729_scanline_color_converter_head_verified`.

## Wave728 YCC Lookup Resource Head Read-Back Note

Wave728 YCC lookup resource head saved five adjacent CDXTexture entropy/resource, YCC lookup-table, row-interleave, and RGBA conversion rows. Tag anchor: `ycc-lookup-resource-head-wave728`; the earliest raw commentless row after this pass is `0x0042f220 CSPtrSet__Clear`, and the next commentless high-signal row is `0x005b0ee0 CDXTexture__InitScanlineColorConverter`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x005af670 CDXTexture__InitEntropyDecodeResources` | `void __stdcall CDXTexture__InitEntropyDecodeResources(void * decode_context)` | Allocates a `0xa0`-byte decode/resource controller through the context allocator, stores it at decode_context `+0x1c8`, installs the refill callback, checks component sampling/dimensions, selects per-component resampler/conversion callbacks including the Wave727 adaptive YCC helpers, flags the two-row YCC path, and allocates scanline/component row buffers. |
| `0x005af860 CDXTexture__BuildYccToRgbLookupTables` | `void CDXTexture__BuildYccToRgbLookupTables(void)` | Comment/tag-only. Uses hidden EAX as the texture decode context, reads the scanline/color controller at context `+0x1cc`, allocates four lookup buffers through the context allocator, stores them at controller `+8` through `+0x14`, and fills fixed coefficient tables. |
| `0x005afbd0 CDXTexture__InterleaveComponentRowsIntoScanline` | `void __stdcall CDXTexture__InterleaveComponentRowsIntoScanline(void * decode_context, void * component_row_tables, int source_row_index, void * output_scanline_table, int scanline_count)` | Reads component count from decode_context `+0x24` and output width from decode_context `+0x70`, selects component source rows through component_row_tables plus source_row_index, walks output_scanline_table entries, and writes component bytes at component-count stride. |
| `0x005afcf0 CDXTexture__ConvertYccToRgba_WithLookupTables` | `void __stdcall CDXTexture__ConvertYccToRgba_WithLookupTables(void * decode_context, void * source_component_row_table, int source_row_index, void * output_rgba_row_table, int scanline_count)` | Reads output width from decode_context `+0x70`, uses lookup-table pointers from the controller at decode_context `+0x1cc`, uses decode_context `+0x148` as a clamp/base table, selects Y/C/A rows from source_component_row_table plus source_row_index, and writes four bytes per output pixel. |
| `0x005afe60 CDXTexture__InitYccLookupTables` | `void CDXTexture__InitYccLookupTables(void)` | Comment/tag-only. Uses hidden EAX as the texture decode context, reads the scanline/color controller at context `+0x1cc`, allocates ten lookup buffers at controller `+0x18` through `+0x3c`, and fills paired fixed-point coefficient/clamp transforms over the byte domain. |

Wave728 read-back evidence verified `5` metadata rows, `5` tag rows, `11` xref rows, `2705` instruction rows, and `5` decompile rows; it also exported `0x005b0ee0 CDXTexture__InitScanlineColorConverter` as read-only caller context. Dry/apply/final dry reported `updated=0 skipped=5 renamed=0 would_rename=0 signature_updated=3 comment_only_updated=2 missing=0 bad=0`, then `updated=5 skipped=0 renamed=0 would_rename=0 signature_updated=3 comment_only_updated=2 missing=0 bad=0`, then `updated=0 skipped=5 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`. The pass made no renames, made no function-boundary changes, and made no executable-byte changes. Post-Wave728 queue telemetry is `6098` total, `4285` commented, `1813` commentless, `1216` exact-undefined signatures, `90` `param_N`, strict clean-signature proxy `4227/6098 = 69.32%`, raw commentless head `0x0042f220 CSPtrSet__Clear`, and high-signal head `0x005b0ee0 CDXTexture__InitScanlineColorConverter`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260522-075134_post_wave728_ycc_lookup_resource_head_verified`.

Exact decode context layout, controller layout, component descriptor schema, row-table schema, RGBA byte order, hidden EAX ABI, allocator contract, coefficient identity, clamp semantics, runtime JPEG/color conversion behavior, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave728 YCC lookup resource head`, `ycc-lookup-resource-head-wave728`, `0x005af670 CDXTexture__InitEntropyDecodeResources`, `0x005af860 CDXTexture__BuildYccToRgbLookupTables`, `0x005afbd0 CDXTexture__InterleaveComponentRowsIntoScanline`, `0x005afcf0 CDXTexture__ConvertYccToRgba_WithLookupTables`, `0x005afe60 CDXTexture__InitYccLookupTables`, `0x005b0ee0 CDXTexture__InitScanlineColorConverter`, `0x0042f220 CSPtrSet__Clear`, `[maintainer-local-ghidra-backup-root]\BEA_20260522-075134_post_wave728_ycc_lookup_resource_head_verified`.

## Wave727 YCC Chroma Conversion Head Read-Back Note

Wave727 YCC chroma conversion head saved six adjacent CDXTexture chroma upsample, YCC-to-RGB conversion, and adaptive dispatch rows. Tag anchor: `ycc-chroma-conversion-head-wave727`; the earliest raw commentless row after this pass is `0x0042f220 CSPtrSet__Clear`, and the next commentless high-signal row is `0x005af670 CDXTexture__InitEntropyDecodeResources`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x005aeaf0 CDXTexture__UpsampleChromaLinearHorizontal` | `void __fastcall CDXTexture__UpsampleChromaLinearHorizontal(void * decode_context, void * component_descriptor, void * source_row_table)` | Uses hidden EAX as the output row-pointer table, reads active row count from decode_context `+0x13c`, reads component width/sample count from component_descriptor `+0x28`, and writes first/interior/final horizontal interpolation samples with 3:1 weighted byte blends. |
| `0x005aebb0 CDXTexture__UpsampleAndConvertYccToRgb_Mmx` | `void __thiscall CDXTexture__UpsampleAndConvertYccToRgb_Mmx(void * this, void * decode_context, void * source_row_table, int hidden_edi_tail)` | MMX-shaped helper selected by the adaptive path. The this object supplies component width/sample count at `+0x28`, decode_context `+0x13c` supplies row count, hidden EAX supplies output rows, source_row_table is consumed relative to those rows, and the caller forwards an EDI tail. |
| `0x005aee40 CDXTexture__UpsampleAndConvertYccToRgb_Scalar` | `void __stdcall CDXTexture__UpsampleAndConvertYccToRgb_Scalar(void * decode_context, void * component_descriptor, void * source_row_table)` | Scalar fallback over two-line source-row neighborhoods, using hidden EAX output rows plus component width and decode row count to emit interpolated byte pairs. |
| `0x005aefa0 CDXTexture__ConvertYccBlocksToRgb_Sse` | `void __fastcall CDXTexture__ConvertYccBlocksToRgb_Sse(void * color_context, void * component_descriptor, void * decode_context, void * source_row_table)` | SSE-shaped helper selected by the auto dispatcher. It uses a forwarded color_context, component_descriptor width, decode_context row count, hidden EAX output rows, and current/previous/next source rows with packed conversion constants around `DAT_005f4a20`. |
| `0x005af570 CDXTexture__UpsampleAndConvertScanlineAdaptive` | `void __stdcall CDXTexture__UpsampleAndConvertScanlineAdaptive(void * decode_context, void * component_descriptor, void * source_row_table)` | Checks component width, scans source row flags against decode row count, signals the decode context callback when low flag bits are set, dispatches to the MMX-shaped helper for decode_context `+0x48` values `5` or `6` when every row is clean, otherwise falls back to horizontal chroma upsample. |
| `0x005af5f0 CDXTexture__ConvertYccBlocksToRgb_Auto` | `void __thiscall CDXTexture__ConvertYccBlocksToRgb_Auto(void * this, void * decode_context, void * component_descriptor, void * source_row_table, void * dispatch_tail)` | Checks component width, scans source row flags against decode row count, signals the decode context callback when low flag bits are set, dispatches to the SSE-shaped helper for decode_context `+0x48` values `5` or `6` when every row is clean, otherwise falls back to the scalar helper. |

Wave727 read-back evidence verified `6` metadata rows, `6` tag rows, `6` xref rows, `3246` instruction rows, and `6` decompile rows. Dry/apply/final dry reported `updated=0 skipped=6 renamed=0 would_rename=0 signature_updated=6 comment_only_updated=0 missing=0 bad=0`, then `updated=6 skipped=0 renamed=0 would_rename=0 signature_updated=6 comment_only_updated=0 missing=0 bad=0`, then `updated=0 skipped=6 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`. The pass made no renames, made no function-boundary changes, and made no executable-byte changes. Post-Wave727 queue telemetry is `6098` total, `4280` commented, `1818` commentless, `1216` exact-undefined signatures, `93` `param_N`, strict clean-signature proxy `4222/6098 = 69.24%`, raw commentless head `0x0042f220 CSPtrSet__Clear`, and high-signal head `0x005af670 CDXTexture__InitEntropyDecodeResources`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260522-072249_post_wave727_ycc_chroma_conversion_head_verified`.

Exact decode context layout, component descriptor schema, row-pointer table layout, hidden EAX/EDI/ECX ABI, YCC/RGB coefficient identity, dispatch policy, runtime JPEG/color conversion behavior, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave727 YCC chroma conversion head`, `ycc-chroma-conversion-head-wave727`, `0x005aeaf0 CDXTexture__UpsampleChromaLinearHorizontal`, `0x005aebb0 CDXTexture__UpsampleAndConvertYccToRgb_Mmx`, `0x005aee40 CDXTexture__UpsampleAndConvertYccToRgb_Scalar`, `0x005aefa0 CDXTexture__ConvertYccBlocksToRgb_Sse`, `0x005af570 CDXTexture__UpsampleAndConvertScanlineAdaptive`, `0x005af5f0 CDXTexture__ConvertYccBlocksToRgb_Auto`, `0x005af670 CDXTexture__InitEntropyDecodeResources`, `0x0042f220 CSPtrSet__Clear`, `[maintainer-local-ghidra-backup-root]\BEA_20260522-072249_post_wave727_ycc_chroma_conversion_head_verified`.

## Wave726 Decode Callback/Entropy Head Read-Back Note

Wave726 decode callback/entropy head saved six adjacent CTexture/CDXTexture/CFastVB decode callback, coefficient-resource, scanline-output, and entropy-input-window rows. Tag anchor: `decode-callback-entropy-head-wave726`; the earliest raw commentless row after this pass is `0x0042f220 CSPtrSet__Clear`, and the next commentless high-signal row is `0x005aeaf0 CDXTexture__UpsampleChromaLinearHorizontal`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x005ad550 CTexture__InitDecodeCallbackTables` | `void __stdcall CTexture__InitDecodeCallbackTables(void * decode_context)` | Initializes the texture decode callback table, allocates a `0xe8`-byte callback/controller table through the context allocator at decode_context `+4`, stores it at decode_context `+0x1c0`, seeds callback entries including `LAB_005ad410` and `LAB_005ad000`, clears four callback/data slots, and returns with `RET 0x4`. |
| `0x005ad590 CFastVB__JpegEntropy_CommitAndResetBlockState` | `int CFastVB__JpegEntropy_CommitAndResetBlockState(void)` | Comment/tag-only. Commits and resets JPEG entropy block state using hidden EBX texture/decode context, advances source byte position by buffered bits rounded to bytes, clears bit count, calls the source flush callback, zeroes per-component history slots, stores restart state from context `+0x118`, and clears the marker flag when context `+0x1a4` is zero. |
| `0x005ae190 CDXTexture__InitBlockCoefficientHistory` | `void __stdcall CDXTexture__InitBlockCoefficientHistory(void * decode_context)` | Initializes block coefficient history resources, allocates a `0x40`-byte controller at decode_context `+0x1c0`, installs `LAB_005adf50`, clears controller slots, allocates a component-count-scaled coefficient/history buffer at decode_context `+0xa4`, fills active dwords with `0xffffffff`, and returns with `RET 0x4`. |
| `0x005ae600 CDXTexture__InitPerComponentCoefficientBuffers` | `void __stdcall CDXTexture__InitPerComponentCoefficientBuffers(void * decode_context)` | Initializes per-component coefficient buffers, allocates a `0x54`-byte controller at decode_context `+0x1c4`, installs `LAB_005ae1f0`, allocates one `0x100`-byte buffer per component, stores each pointer in the component descriptor at `+0x50`, zeroes `0x40` dwords per component, seeds controller slots to `0xffffffff`, and returns with `RET 0x4`. |
| `0x005ae780 CDXTexture__InitScanlineOutputStage` | `void __stdcall CDXTexture__InitScanlineOutputStage(void * decode_context)` | Initializes the scanline output stage, allocates a `0x1c`-byte stage at decode_context `+0x1b4`, installs `LAB_005ae700`, clears stage slots, optionally stores decode_context `+0x13c`, dispatches through the stage callback when hidden ESI mode is nonzero, or allocates a row buffer sized from decode_context `+0x78` and `+0x70`, then returns with `RET 0x4`. |
| `0x005ae810 CDXTexture__RefillEntropyInputWindow` | `int CDXTexture__RefillEntropyInputWindow(void)` | Comment/tag-only. Refills/copies from the entropy input window using locked stack parameters and hidden EBP progress state, invokes per-component callbacks at row/span boundaries, clamps copy size by context span, window remaining count, and output cursor/end, dispatches the copy/fill callback at decode_context `+0x1cc +4`, advances output/window offsets, and increments hidden progress at span boundaries. |

Wave726 read-back evidence verified `6` metadata rows, `6` tag rows, `9` xref rows, `3246` instruction rows, and `6` decompile rows. Dry/apply/final dry reported `updated=0 skipped=6 renamed=0 would_rename=0 signature_updated=4 comment_only_updated=2 missing=0 bad=0`, then `updated=6 skipped=0 renamed=0 would_rename=0 signature_updated=4 comment_only_updated=2 missing=0 bad=0`, then `updated=0 skipped=6 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`. The pass made no renames, made no function-boundary changes, and made no executable-byte changes. Post-Wave726 queue telemetry is `6098` total, `4274` commented, `1824` commentless, `1216` exact-undefined signatures, `99` `param_N`, strict clean-signature proxy `4216/6098 = 69.14%`, raw commentless head `0x0042f220 CSPtrSet__Clear`, and high-signal head `0x005aeaf0 CDXTexture__UpsampleChromaLinearHorizontal`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260522-065624_post_wave726_decode_callback_entropy_head_verified`.

Exact decode context layout, callback table schema, allocator ownership, component descriptor schema, coefficient/history buffer layout, hidden EBX/ESI/EBP ABI, entropy input-window schema, copy/fill callback contract, runtime JPEG/decode behavior, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave726 decode callback/entropy head`, `decode-callback-entropy-head-wave726`, `0x005ad550 CTexture__InitDecodeCallbackTables`, `0x005ad590 CFastVB__JpegEntropy_CommitAndResetBlockState`, `0x005ae190 CDXTexture__InitBlockCoefficientHistory`, `0x005ae600 CDXTexture__InitPerComponentCoefficientBuffers`, `0x005ae780 CDXTexture__InitScanlineOutputStage`, `0x005ae810 CDXTexture__RefillEntropyInputWindow`, `0x005aeaf0 CDXTexture__UpsampleChromaLinearHorizontal`, `0x0042f220 CSPtrSet__Clear`, `[maintainer-local-ghidra-backup-root]\BEA_20260522-065624_post_wave726_decode_callback_entropy_head_verified`.

## Wave725 JPEG Scan/Huffman Head Read-Back Note

Wave725 JPEG scan/Huffman head saved eight adjacent CDXTexture JPEG scan, quant-table, color-conversion, Huffman, and entropy-bitstream rows. Tag anchor: `jpeg-scan-huffman-head-wave725`; the earliest raw commentless row after this pass is `0x0042f220 CSPtrSet__Clear`, and the next commentless high-signal row is `0x005ad550 CTexture__InitDecodeCallbackTables`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x005aba90 CDXTexture__SelectNextScanTableForProgress` | `void __fastcall CDXTexture__SelectNextScanTableForProgress(void * decode_context)` | Selects/reset the next JPEG scan table progress state using ECX texture/decode context, updates the scan/controller block at context `+0x1b0`, chooses the next scan table count from component descriptor fields under `+0x150/+0x144/+0x98`, and resets scan-progress counters at `+0x14/+0x18`. |
| `0x005ac180 CDXTexture__ValidateAndIndexQuantTables` | `int CDXTexture__ValidateAndIndexQuantTables(void)` | Comment/tag-only. Validates component quantization table availability and copies per-component table indexes into the decode color/scan controller using hidden EBX texture/decode context; allocates the controller table at scan block `+0x70` if needed. |
| `0x005ac930 CDXTexture__SelectColorConvertEntryPoint` | `void __stdcall CDXTexture__SelectColorConvertEntryPoint(void * decode_context)` | Selects the color-conversion entry point, calls the quant-table validator when context `+0x50` is set, installs `LAB_005ac2d0` for the indexed quant-table path or `LAB_005abff0` as fallback, clears context `+0xa0`, and returns with `RET 0x4`. |
| `0x005ac980 CDXTexture__InitColorConversionResources` | `void __stdcall CDXTexture__InitColorConversionResources(void * decode_context)` | Initializes color-conversion resources, allocates a `0x74`-byte controller at context `+0x1b0`, installs setup/select callbacks, and either allocates per-component row resources when hidden EBX mode is nonzero or a shared `0x500`-byte table block. |
| `0x005acac0 CDXTexture__BuildJpegHuffmanDecodeTable` | `void __stdcall CDXTexture__BuildJpegHuffmanDecodeTable(void * decode_context, int table_class, int table_index, void * decode_table_slot)` | Builds a JPEG Huffman decode lookup table from DC/AC table descriptors, validates table index range, allocates a `0x590`-byte table when needed, builds max-code/offset arrays, fills the 8-bit fast lookup and symbol tables, and validates AC run-length symbols. |
| `0x005acd90 CDXTexture__BitstreamReadBitsWithJpegStuffing` | `int __stdcall CDXTexture__BitstreamReadBitsWithJpegStuffing(void * bitstream_state, uint bit_buffer, int bit_count, int min_bits)` | Refills JPEG entropy bitstream state while honoring `0xff` byte-stuffing and marker detection, records nonzero marker bytes at decoder `+0x1a4`, pads after marker/error state when needed, writes back source/bit fields, and returns success/failure. |
| `0x005aceb0 CDXTexture__DecodeHuffmanSymbolFromBitstream` | `uint __stdcall CDXTexture__DecodeHuffmanSymbolFromBitstream(void * bitstream_state, uint bit_buffer, int bit_count, void * huffman_table, int min_bits)` | Decodes one JPEG Huffman symbol, refills through `CDXTexture__BitstreamReadBitsWithJpegStuffing` when needed, grows the code until it is within table max-code entries, returns the symbol from table descriptor offsets, and reports error id `0x76` on invalid code length. |
| `0x005acf90 CDXTexture__FinalizeScanBitstreamState` | `int CDXTexture__FinalizeScanBitstreamState(void)` | Comment/tag-only. Finalizes JPEG scan bitstream state using hidden ESI texture/decode context, advances source byte position by buffered-bit count, clears entropy bit count, calls the scan/source flush callback, zeroes per-component restart/history slots, stores restart state from context `+0x118`, and clears the marker field when context `+0x1a4` is zero. |

Wave725 read-back evidence verified `8` metadata rows, `8` tag rows, `34` xref rows, `4328` instruction rows, and `8` decompile rows. Dry/apply/final dry reported `updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=6 comment_only_updated=2 missing=0 bad=0`, then `updated=8 skipped=0 renamed=0 would_rename=0 signature_updated=6 comment_only_updated=2 missing=0 bad=0`, then `updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`. The pass made no renames, made no function-boundary changes, and made no executable-byte changes. Post-Wave725 queue telemetry is `6098` total, `4268` commented, `1830` commentless, `1216` exact-undefined signatures, `103` `param_N`, strict clean-signature proxy `4210/6098 = 69.04%`, raw commentless head `0x0042f220 CSPtrSet__Clear`, and high-signal head `0x005ad550 CTexture__InitDecodeCallbackTables`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260522-062642_post_wave725_jpeg_scan_huffman_head_verified`.

Exact JPEG/decode context layout, scan table schema, component descriptor schema, quant table descriptor schema, hidden EBX/ESI ABI, callback table contract, color conversion policy, DHT descriptor schema, Huffman decode-table layout, entropy state layout, source/error callback ABI, marker/restart policy, runtime JPEG decode behavior, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave725 JPEG scan/Huffman head`, `jpeg-scan-huffman-head-wave725`, `0x005aba90 CDXTexture__SelectNextScanTableForProgress`, `0x005ac180 CDXTexture__ValidateAndIndexQuantTables`, `0x005ac930 CDXTexture__SelectColorConvertEntryPoint`, `0x005ac980 CDXTexture__InitColorConversionResources`, `0x005acac0 CDXTexture__BuildJpegHuffmanDecodeTable`, `0x005acd90 CDXTexture__BitstreamReadBitsWithJpegStuffing`, `0x005aceb0 CDXTexture__DecodeHuffmanSymbolFromBitstream`, `0x005acf90 CDXTexture__FinalizeScanBitstreamState`, `0x005ad550 CTexture__InitDecodeCallbackTables`, `0x0042f220 CSPtrSet__Clear`, `[maintainer-local-ghidra-backup-root]\BEA_20260522-062642_post_wave725_jpeg_scan_huffman_head_verified`.

## Wave724 Texture Row Edge Padding Head Read-Back Note

Wave724 texture row edge padding head saved five adjacent texture/decode row-cache and edge-padding rows. Tag anchor: `texture-row-edge-padding-head-wave724`; the earliest raw commentless row after this pass is `0x0042f220 CSPtrSet__Clear`, and the next commentless high-signal row is `0x005aba90 CDXTexture__SelectNextScanTableForProgress`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x005ab420 CTexture__BuildComponentPlaneRowPointers` | `void CTexture__BuildComponentPlaneRowPointers(void)` | Comment/tag-only. Builds component-plane row pointer tables for the texture/decode row cache using hidden ESI context, allocates paired row-pointer arrays under context `+0x1ac` slots `+0x38/+0x3c`, and walks component descriptors under `+0xdc`. |
| `0x005ab4d0 CMeshCollisionVolume__ExpandEdgeRows_MirrorHigh` | `void __fastcall CMeshCollisionVolume__ExpandEdgeRows_MirrorHigh(void * texture_context)` | Mirrors/copies high-side edge rows for component-plane row buffers using ECX texture/decode context. Current `CMeshCollisionVolume` owner label is retained as Ghidra state, but static evidence is texture row-cache/edge-padding behavior rather than owner/source identity proof. |
| `0x005ab620 CMeshCollisionVolume__ExpandEdgeRows_MirrorBoth` | `void CMeshCollisionVolume__ExpandEdgeRows_MirrorBoth(void)` | Comment/tag-only. Mirrors/copies both edge sides for component-plane row buffers using hidden EAX texture/decode context. Current owner/source identity remains unproven. |
| `0x005ab700 CMeshCollisionVolume__FinalizeEdgePaddingRows` | `void CMeshCollisionVolume__FinalizeEdgePaddingRows(void)` | Comment/tag-only. Finalizes component-plane edge-padding rows using hidden EAX context and records first-component padding height at row-cache `+0x48`. Current owner/source identity remains unproven. |
| `0x005ab9c0 CDXTexture__InitComponentPlaneRowCache` | `void __stdcall CDXTexture__InitComponentPlaneRowCache(void * texture_context)` | Initializes the component-plane row cache, allocates the `0x50`-byte cache at context `+0x1ac`, installs `LAB_005ab950`, conditionally builds row pointers, and allocates per-component row cache buffers from the context allocator. |

Wave724 read-back evidence verified `5` metadata rows, `5` tag rows, `5` xref rows, `2405` instruction rows, and `5` decompile rows. Dry/apply/final dry reported `updated=0 skipped=5 renamed=0 would_rename=0 signature_updated=2 comment_only_updated=3 missing=0 bad=0`, then `updated=5 skipped=0 renamed=0 would_rename=0 signature_updated=2 comment_only_updated=3 missing=0 bad=0`, then `updated=0 skipped=5 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`. The pass made no renames, made no function-boundary changes, and made no executable-byte changes. Post-Wave724 queue telemetry is `6098` total, `4260` commented, `1838` commentless, `1216` exact-undefined signatures, `109` `param_N`, strict clean-signature proxy `4202/6098 = 68.91%`, raw commentless head `0x0042f220 CSPtrSet__Clear`, and high-signal head `0x005aba90 CDXTexture__SelectNextScanTableForProgress`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260522-055657_post_wave724_texture_row_edge_padding_head_verified`.

Exact texture/decode context layout, component descriptor schema, row-cache layout, edge-padding callback ABI, current owner/source identity, runtime texture/decode behavior, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave724 texture row edge padding head`, `texture-row-edge-padding-head-wave724`, `0x005ab420 CTexture__BuildComponentPlaneRowPointers`, `0x005ab4d0 CMeshCollisionVolume__ExpandEdgeRows_MirrorHigh`, `0x005ab620 CMeshCollisionVolume__ExpandEdgeRows_MirrorBoth`, `0x005ab700 CMeshCollisionVolume__FinalizeEdgePaddingRows`, `0x005ab9c0 CDXTexture__InitComponentPlaneRowCache`, `0x005aba90 CDXTexture__SelectNextScanTableForProgress`, `0x0042f220 CSPtrSet__Clear`, `[maintainer-local-ghidra-backup-root]\BEA_20260522-055657_post_wave724_texture_row_edge_padding_head_verified`.

## Wave723 Texture Node Output Serialization Head Read-Back Note

Wave723 texture node output serialization head saved two adjacent CDXTexture/CTexture texture node output rows. Tag anchor: `texture-node-output-serialization-head-wave723`; the earliest raw commentless row after this pass is `0x0042f220 CSPtrSet__Clear`, and the next commentless high-signal row is `0x005ab4d0 CMeshCollisionVolume__ExpandEdgeRows_MirrorHigh`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x005ab0ed CDXTexture__EvalNodeOutputSizeUnits` | `int __stdcall CDXTexture__EvalNodeOutputSizeUnits(void * node_tree)` | Recursive texture/node-tree output-unit count; null input returns zero, kind `1` sums the `+0xc` and `+0x8` child branches, kind `5` follows `+0x18`, kind `7` multiplies the recursive `+0x10` count by `+0x14`, kind `8` multiplies `+0x1c` by `+0x18`, kind `10` follows `+0x20`, and `RET 0x4` restores one stack argument. |
| `0x005ab14b CTexture__SerializeNodeTreeToBitstream` | `int __stdcall CTexture__SerializeNodeTreeToBitstream(void * chunk_builder, void * node_tree, uint output_unit_scale, uint * out_chunk_offset)` | Four-argument recursive serializer; null `out_chunk_offset` returns zero, unsupported node kinds return `0x80004005`, kind `7` scales while following `+0x10`, kind `8` registers typed payload data through `CDXTexture__RegisterSerializedChunk`, and kind `1` registers child records plus a final `0x10`-byte header. |

Wave723 read-back evidence verified `2` metadata rows, `2` tag rows, `6` xref rows, `666` instruction rows, and `2` decompile rows. Dry/apply/final dry reported `updated=0 skipped=2 renamed=0 would_rename=0 signature_updated=2 comment_only_updated=0 missing=0 bad=0`, then `updated=2 skipped=0 renamed=0 would_rename=0 signature_updated=2 comment_only_updated=0 missing=0 bad=0`, then `updated=0 skipped=2 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`. The pass made no renames, made no function-boundary changes, and made no executable-byte changes. Post-Wave723 queue telemetry is `6098` total, `4255` commented, `1843` commentless, `1216` exact-undefined signatures, `111` `param_N`, strict clean-signature proxy `4197/6098 = 68.82%`, raw commentless head `0x0042f220 CSPtrSet__Clear`, and high-signal head `0x005ab4d0 CMeshCollisionVolume__ExpandEdgeRows_MirrorHigh`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260522-052723_post_wave723_texture_node_output_serialization_head_verified`.

Exact chunk-builder layout, node field schema, node type/kind enum, output-unit semantics, serialized-chunk format, registry flag contract, runtime texture behavior, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave723 texture node output serialization head`, `texture-node-output-serialization-head-wave723`, `0x005ab0ed CDXTexture__EvalNodeOutputSizeUnits`, `0x005ab14b CTexture__SerializeNodeTreeToBitstream`, `0x005ab4d0 CMeshCollisionVolume__ExpandEdgeRows_MirrorHigh`, `0x0042f220 CSPtrSet__Clear`, `[maintainer-local-ghidra-backup-root]\BEA_20260522-052723_post_wave723_texture_node_output_serialization_head_verified`.

## Functions (5 total)

| Address | Name | Purpose |
|---------|------|---------|
| `0x00557300` | `CDXTexture__LoadTextureFromFile` | Load texture from file path in AYA archive |
| `0x005586e0` | `CDXTexture__DumpTextureToRGBA` | Convert texture to RGBA format for debugging |
| `0x00559410` | `CDXTexture__CreateMipmaps` | Generate mipmap chain for texture |
| `0x00559be0` | `CDXTexture__Deserialize` | Load texture from serialized data |
| `0x005d7dc0` | `CDXTexture__Deserialize_Unwind` | Exception handler for Deserialize |

## Wave716 JPEG Writer Head Read-Back Note

Wave716 JPEG writer head saved sixteen adjacent CDXTexture JPEG writer / CRC rows. Tag anchor: `jpeg-writer-head-wave716`; the earliest raw commentless row after this pass is `0x0042f220 CSPtrSet__Clear`, and the next commentless high-signal row is `0x0059f360 CFastVB__DispatchOp_TransformVec4_0059f360`.

The pass hardened eleven visible signatures/parameter names and left five hidden-register writer helpers comment/tag-only: `0x0059e310 CDXTexture__WriteJpegHuffmanTable`, `0x0059e4a0 CDXTexture__WriteJpegRestartIntervalMarker`, `0x0059e770 CDXTexture__WriteJpegScanHeader`, `0x0059e970 CDXTexture__WriteJpegApp0JfifSegment`, and `0x0059ebf0 CDXTexture__WriteJpegApp14AdobeMarker`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x0059dfb2 CDXTexture__Crc32_Update` | `uint __stdcall CDXTexture__Crc32_Update(uint crc_seed, void * source_bytes, uint byte_count)` | CRC-32 table update through `DAT_005f3ec0`, seed/result complement, null-source zero return, unrolled 8-byte loop, and tail-byte loop. |
| `0x0059e0b0 CDXTexture__WriteJpegMarkerByte` | `void __stdcall CDXTexture__WriteJpegMarkerByte(int marker_byte)` | Writes `0xff` plus marker byte through the ESI-held writer buffer, flushes through the output callback when needed, and reports error id `0x18` on flush failure. |
| `0x0059e110 CDXTexture__WriteJpegQuantTable` | `char __stdcall CDXTexture__WriteJpegQuantTable(int quant_table_index)` | Emits DQT marker `0xffdb`, computes 8-bit vs 16-bit precision, writes zigzag-ordered values through `DAT_005f37f8`, marks the descriptor written, and reports missing-table error id `0x34`. |
| `0x0059e310 CDXTexture__WriteJpegHuffmanTable` | `void __thiscall CDXTexture__WriteJpegHuffmanTable(void * this, void * param_1, int param_2)` | Comment/tag-only; writes DHT marker `0xffc4`, computes length from the 16 code-count bytes, writes table class/id, counts, symbols, and uses hidden EAX table-class context. |
| `0x0059e4a0 CDXTexture__WriteJpegRestartIntervalMarker` | `void CDXTexture__WriteJpegRestartIntervalMarker(void)` | Comment/tag-only; emits DRI marker `0xffdd`, fixed length 4, and the restart interval from the ESI-held writer context. |
| `0x0059e580 CDXTexture__WriteJpegFrameHeader` | `void __fastcall CDXTexture__WriteJpegFrameHeader(void * jpeg_encoder_state)` | Writes an SOF frame header selected by hidden EAX marker context, validates dimensions against `0xffff`, and emits precision, size, component count, sampling, and quant-table selectors. |
| `0x0059e770 CDXTexture__WriteJpegScanHeader` | `void CDXTexture__WriteJpegScanHeader(void)` | Comment/tag-only; emits SOS marker `0xffda`, component selector/table ids, spectral selection, and successive approximation bytes from the ESI-held scan context. |
| `0x0059e970 CDXTexture__WriteJpegApp0JfifSegment` | `void CDXTexture__WriteJpegApp0JfifSegment(void)` | Comment/tag-only; emits APP0 marker `0xffe0`, length `0x10`, `JFIF` identifier bytes, version/density fields, and zero thumbnail dimensions. |
| `0x0059ebf0 CDXTexture__WriteJpegApp14AdobeMarker` | `void CDXTexture__WriteJpegApp14AdobeMarker(void)` | Comment/tag-only; emits APP14 marker `0xffee`, length `0x0e`, `Adobe` identifier bytes, and a transform byte from the encoder color-transform state. |
| `0x0059ee20 CDXTexture__WriteJpegSegmentMarkerAndLength` | `void __stdcall CDXTexture__WriteJpegSegmentMarkerAndLength(void * jpeg_encoder_state, int marker_byte, uint payload_byte_count)` | Checks segment payload limit `0xfffd`, writes the marker through `CDXTexture__WriteJpegMarkerByte`, then emits big-endian length `payload_byte_count + 2`. |
| `0x0059eed0 CDXTexture__WriteJpegStartOfImageAndMetadata` | `void __stdcall CDXTexture__WriteJpegStartOfImageAndMetadata(void * jpeg_encoder_state)` | Writes SOI bytes `0xffd8`, conditionally writes APP0/JFIF metadata, and conditionally writes APP14/Adobe metadata. |
| `0x0059ef60 CDXTexture__WriteJpegQuantTablesAndFrame` | `void __stdcall CDXTexture__WriteJpegQuantTablesAndFrame(void * jpeg_encoder_state)` | Walks component quant-table selectors, calls the DQT writer, reports baseline precision error id `0x4b` when 16-bit quantization conflicts with mode, and writes the frame header. |
| `0x0059f050 CDXTexture__WriteJpegHuffmanAndScanHeaders` | `void __stdcall CDXTexture__WriteJpegHuffmanAndScanHeaders(void * jpeg_encoder_state)` | Emits needed DC/AC Huffman tables, refreshes restart interval state, writes the scan header, and still documents hidden EBX table-class context into the Huffman helper. |
| `0x0059f110 CDXTexture__WriteJpegEndOfImage` | `void __stdcall CDXTexture__WriteJpegEndOfImage(void * jpeg_encoder_state)` | Writes EOI bytes `0xffd9`. |
| `0x0059f260 CDXTexture__InitJpegWriterStageCallbacks` | `void __stdcall CDXTexture__InitJpegWriterStageCallbacks(void * jpeg_encoder_state)` | Allocates a `0x20`-byte writer-stage callback table and installs SOI/metadata, quant/frame, Huffman/scan, EOI, and segment-marker callbacks. |
| `0x0059f2b0 CDXTexture__InitializeJpegEncoderPipeline` | `void __stdcall CDXTexture__InitializeJpegEncoderPipeline(void * jpeg_encoder_state)` | Initializes scan controller, color conversion, sample buffers, DCT/quant stages, entropy or scan-script state, working buffers, component buffers, and writer-stage callbacks. |

Wave716 read-back evidence verified `16` metadata rows, `16` tag rows, `25` xref rows, `1104` instruction rows, and `16` decompile rows. Dry/apply/final dry reported `updated=0 skipped=16 renamed=0 would_rename=0 signature_updated=11 comment_only_updated=5 missing=0 bad=0`, then `updated=16 skipped=0 renamed=0 would_rename=0 signature_updated=11 comment_only_updated=5 missing=0 bad=0`, then `updated=0 skipped=16 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`. The pass made no renames, made no function-boundary changes, and made no executable-byte changes. Post-Wave716 queue telemetry is `6098` total, `4183` commented, `1915` commentless, `1216` exact-undefined signatures, `159` `param_N`, strict clean-signature proxy `4126/6098 = 67.66%`, raw commentless head `0x0042f220 CSPtrSet__Clear`, and high-signal head `0x0059f360 CFastVB__DispatchOp_TransformVec4_0059f360`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260522-013644_post_wave716_jpeg_writer_head_verified`.

Exact JPEG encoder-state layout, writer/output-manager ABI, callback table ownership, quant/Huffman descriptor schemas, progressive/baseline mode policy, color-transform enum, runtime JPEG output fidelity, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave716 JPEG writer head`, `jpeg-writer-head-wave716`, `0x0059dfb2 CDXTexture__Crc32_Update`, `0x0059e110 CDXTexture__WriteJpegQuantTable`, `0x0059e310 CDXTexture__WriteJpegHuffmanTable`, `0xffdb`, `0xffc4`, `0xffd9`, `0x0059f360 CFastVB__DispatchOp_TransformVec4_0059f360`, `0x0042f220 CSPtrSet__Clear`, `[maintainer-local-ghidra-backup-root]\BEA_20260522-013644_post_wave716_jpeg_writer_head_verified`.

## Wave715 PNG Chunk Parser Head Read-Back Note

Wave715 PNG chunk parser head saved eight adjacent CDXTexture PNG chunk parser/IDAT rows. Tag anchor: `png-chunk-parser-head-wave715`; the earliest raw commentless row after this pass is `0x0042f220 CSPtrSet__Clear`, and the next commentless high-signal row is `0x0059dfb2 CDXTexture__Crc32_Update`.

The pass made two dispatch-backed renames: raw bytes at `0x005ee8e4` are `49 45 4e 44` / `IEND`, so `0x0059d992` is `CDXTexture__ParsePngChunk_IEND`; raw bytes at `0x005ee904` are `74 52 4e 53` / `tRNS`, so `0x0059dbbb` is `CDXTexture__ParsePngChunk_tRNS`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x0059d699 CDXTexture__ParsePngChunk_IHDR` | `void __stdcall CDXTexture__ParsePngChunk_IHDR(void * png_decode_state, void * png_image_context, uint chunk_data_length)` | `RET 0xc`, `ParsePngHeadersUntilIdat` xref, 13-byte IHDR read, CRC finalization, IHDR field validation/stores, bits-per-pixel/row byte-count derivation, and format descriptor finalization. |
| `0x0059d879 CDXTexture__ParsePngChunk_PLTE` | `void __stdcall CDXTexture__ParsePngChunk_PLTE(void * png_decode_state, void * png_image_context, uint chunk_data_length)` | `RET 0xc`, PLTE ordering checks, palette allocation/read loop, decode-state palette pointer/count stores, image-context scan-parameter handoff, and indexed tRNS count clamp. |
| `0x0059d992 CDXTexture__ParsePngChunk_IEND` | `void __stdcall CDXTexture__ParsePngChunk_IEND(void * png_decode_state, void * png_image_context, uint chunk_data_length)` | `RET 0xc`, raw `IEND` dispatch constant bytes `49 45 4e 44`, prior IHDR/IDAT state requirement, terminal flag mark, nonzero-length warning, and CRC finalization. |
| `0x0059d9d8 CDXTexture__ParsePngChunk_gAMA` | `void __stdcall CDXTexture__ParsePngChunk_gAMA(void * png_decode_state, void * png_image_context, uint chunk_data_length)` | `RET 0xc`, gAMA ordering/duplicate policy, 4-byte big-endian gamma read, CRC-before-apply flow, sRGB/gAMA consistency warning, normalized gamma store, and image-context option handoff. |
| `0x0059dad9 CDXTexture__ParsePngChunk_sRGB` | `void __stdcall CDXTexture__ParsePngChunk_sRGB(void * png_decode_state, void * png_image_context, uint chunk_data_length)` | `RET 0xc`, sRGB ordering/duplicate policy, one-byte rendering intent read, CRC-before-apply flow, intent range check, gAMA/sRGB consistency warning, and option handoff. |
| `0x0059dbbb CDXTexture__ParsePngChunk_tRNS` | `void __stdcall CDXTexture__ParsePngChunk_tRNS(void * png_decode_state, void * png_image_context, uint chunk_data_length)` | `RET 0xc`, raw `tRNS` dispatch constant bytes `74 52 4e 53`, indexed palette alpha path, grayscale/RGB transparent sample path, decode-state transparency stores, and option handoff after CRC validation. |
| `0x0059dd5c CDXTexture__HandlePngChunkAfterIdat` | `void __stdcall CDXTexture__HandlePngChunkAfterIdat(void * png_decode_state, void * png_image_context, uint chunk_data_length)` | `RET 0xc`, fallback chunk-tag validation/logging, unknown critical chunk diagnostic, post-IDAT unknown-chunk flag mark, and payload drain through CRC finalizer. |
| `0x0059dda2 CDXTexture__ProcessIdatChunkDataAndQueueDecode` | `void __stdcall CDXTexture__ProcessIdatChunkDataAndQueueDecode(void * png_decode_state)` | `RET 0x4`; both call sites push only the decode-state stack argument, while ECX is pushed/popped as scratch local storage. The helper advances row/pass state, reads further IDAT chunks, pumps zlib, marks completion flags, and begins the async decode job. |

Wave715 read-back evidence verified `8` metadata rows, `8` tag rows, `9` xref rows, `4584` post-instruction rows, and `8` post-decompile rows. Caller post-decompile verifies the corrected chunk dispatch labels and clean one-argument `CDXTexture__ProcessIdatChunkDataAndQueueDecode(png_decode_state_00)` calls. Dry/apply/final dry reported `updated=0 skipped=8 renamed=0 would_rename=2 signature_updated=8 comment_only_updated=0 missing=0 bad=0`, then `updated=8 skipped=0 renamed=2 would_rename=0 signature_updated=8 comment_only_updated=0 missing=0 bad=0`, then `updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`. The pass hardened `8` signatures/parameter names, made `2` guarded renames, made no function-boundary changes, and made no executable-byte changes. Post-Wave715 queue telemetry is `6098` total, `4167` commented, `1931` commentless, `1216` exact-undefined signatures, `170` `param_N`, strict clean-signature proxy `4111/6098 = 67.42%`, raw commentless head `0x0042f220 CSPtrSet__Clear`, and high-signal head `0x0059dfb2 CDXTexture__Crc32_Update`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260522-005631_post_wave715_png_chunk_parser_head_verified`.

Exact PNG decode-state layout, image-context layout, chunk/flag enum, CRC/source-read bounds, gamma/sRGB/tRNS policy provenance, transparency field schema, zlib stream layout, async job contract, runtime PNG behavior, runtime decode/image fidelity, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave715 PNG chunk parser head`, `png-chunk-parser-head-wave715`, `0x0059d992 CDXTexture__ParsePngChunk_IEND`, `0x0059dbbb CDXTexture__ParsePngChunk_tRNS`, `49 45 4e 44`, `74 52 4e 53`, `CDXTexture__ProcessIdatChunkDataAndQueueDecode(png_decode_state_00)`, `0x0059dfb2 CDXTexture__Crc32_Update`, `0x0042f220 CSPtrSet__Clear`, `[maintainer-local-ghidra-backup-root]\BEA_20260522-005631_post_wave715_png_chunk_parser_head_verified`.

## Wave714 PNG Scanline / Pass Head Read-Back Note

Wave714 PNG scanline / pass head saved five adjacent CDXTexture PNG scanline/pass rows. Tag anchor: `png-scanline-pass-head-wave714`; the earliest raw commentless row after this pass is `0x0042f220 CSPtrSet__Clear`, and the next commentless high-signal row is `0x0059d699 CDXTexture__ParsePngChunk_IHDR`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x0059ce20 CDXTexture__ExpandPackedPixelsToScanline` | `void __stdcall CDXTexture__ExpandPackedPixelsToScanline(void * png_decode_state, void * output_scanline, uint pass_pixel_mask)` | `RET 0xc`, row-decoder xrefs, full-mask copy path, and 1/2/4-bit or byte-aligned packed-pixel expansion into optional workspaces. |
| `0x0059d036 CDXTexture__ExpandAdam7PassRowInPlace` | `void __stdcall CDXTexture__ExpandAdam7PassRowInPlace(void * row_layout_descriptor, void * row_buffer, int adam7_pass_index)` | `RET 0xc`, null guards, `DAT_005f39d8` pass-width table use, backward in-place row expansion, and descriptor width/byte-count updates. |
| `0x0059d301 CDXTexture__ApplyPngScanlineFilter` | `void __stdcall CDXTexture__ApplyPngScanlineFilter(void * png_decode_state, void * row_layout_descriptor, void * current_scanline, void * previous_scanline, int filter_type)` | `RET 0x14`, row-layout byte count and pixel-byte stride use, filter types 1..4 matching Sub/Up/Average/Paeth-style predictors, and warning/clear path for unknown filters. |
| `0x0059d47a CDXTexture__InitPngImageBuffersAndPassGeometry` | `void __stdcall CDXTexture__InitPngImageBuffersAndPassGeometry(void * png_decode_state)` | `RET 0x4`, post-decode transform application, normal/Adam7 row geometry and output bit-width computation, row-buffer allocation, previous-row clear, and initialization flag set. |
| `0x0059d614 CDXTexture__FinalizePngChunkAndVerifyCrc` | `int __stdcall CDXTexture__FinalizePngChunkAndVerifyCrc(void * png_decode_state, uint remaining_chunk_bytes)` | `RET 0x8`, remaining chunk payload drain, CRC helper call, `"CRC error"` log/warn paths, and nonzero invalid-CRC status. The post decompile still has the expected `extraout_var` artifact from the upstream bool-return CRC helper. |

Wave714 read-back evidence verified candidate and selected pre exports with `5` metadata rows, `5` tag rows, `22` xref rows, `185` instruction rows, and `5` decompile rows each. Dry/apply/final dry reported `updated=0 skipped=5 renamed=0 would_rename=0 signature_updated=5 comment_only_updated=0 missing=0 bad=0`, then `updated=5 skipped=0 renamed=0 would_rename=0 signature_updated=5 comment_only_updated=0 missing=0 bad=0`, then `updated=0 skipped=5 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`. Post exports verified `5` metadata rows, `5` tag rows, `22` xref rows, `185` instruction rows, and `5` decompile rows. The pass hardened `5` signatures/parameter names, made no renames, made no function-boundary changes, and made no executable-byte changes. Post-Wave714 queue telemetry is `6098` total, `4159` commented, `1939` commentless, `1216` exact-undefined signatures, `178` `param_N`, strict clean-signature proxy `4103/6098 = 67.28%`, raw commentless head `0x0042f220 CSPtrSet__Clear`, and high-signal head `0x0059d699 CDXTexture__ParsePngChunk_IHDR`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260522-002212_post_wave714_png_scanline_pass_head_verified`.

Exact PNG decode-state layout, row-layout descriptor schema, Adam7 table/mask semantics, chunk/CRC flag enum, row-workspace/buffer ownership, source-read bounds, warning/error policy, runtime PNG behavior, runtime decode/image fidelity, BEA patching, and rebuild parity remain unproven. `0x0059d614 CDXTexture__FinalizePngChunkAndVerifyCrc` intentionally retains the documented `extraout_var` upstream-helper artifact after local parameters were cleaned.

Probe anchors: `Wave714 PNG scanline / pass head`, `png-scanline-pass-head-wave714`, `0x0059ce20 CDXTexture__ExpandPackedPixelsToScanline`, `0x0059d614 CDXTexture__FinalizePngChunkAndVerifyCrc`, `extraout_var`, `0x0059d699 CDXTexture__ParsePngChunk_IHDR`, `0x0042f220 CSPtrSet__Clear`, `[maintainer-local-ghidra-backup-root]\BEA_20260522-002212_post_wave714_png_scanline_pass_head_verified`.

## Wave713 Inflate / PNG Helper Head Read-Back Note

Wave713 inflate / PNG helper head saved eleven adjacent CDXTexture inflate and PNG helper rows. Tag anchor: `inflate-png-helper-head-wave713`; the earliest raw commentless row after this pass is `0x0042f220 CSPtrSet__Clear`, and the next commentless high-signal row is `0x0059ce20 CDXTexture__ExpandPackedPixelsToScanline`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x0059c7cc CDXTexture__InflateInitStateFromHeader` | `int __stdcall CDXTexture__InflateInitStateFromHeader(void * inflate_stream, int window_bits, void * version_text, int stream_struct_size)` | `RET 0x10`, zlib-style stream/window/version/0x38-size inputs, default callbacks, 0x18 internal-state allocation, window bits 8..15, and fixed Huffman-table setup. |
| `0x0059c8ab CDXTexture__InflateInit_WindowBits15` | `int __stdcall CDXTexture__InflateInit_WindowBits15(void * inflate_stream, void * version_text, int stream_struct_size)` | `RET 0xc` wrapper into the header initializer with fixed window bits 15. |
| `0x0059c8c1 CDXTexture__InflateStream_ProcessZlibState` | `int __stdcall CDXTexture__InflateStream_ProcessZlibState(void * inflate_stream, int flush_mode)` | `RET 0x8`, PNG IDAT/pass-row xrefs, zlib CMF/FLG/data-check/block-processing state-machine shape, and zlib-style status returns. Wave964 resolved the saved downstream helper `extraout_EAX` caveat by tying callsite `0x0059c9ce` to the `CDXTexture__InflateProcessBlockHeader` int status return. |
| `0x0059cc24 CDXTexture__AllocZeroedDecodeState` | `void * __stdcall CDXTexture__AllocZeroedDecodeState(int state_class)` | `RET 0x4`, decode-state class 1 as 0x19c bytes, class 2 as 0x40 bytes, malloc, and zero-init loop. |
| `0x0059cc68 CDXTexture__FreeDecodeState` | `void __stdcall CDXTexture__FreeDecodeState(void * decode_state)` | `RET 0x4`, non-null decode-state free through `CRT__FreeBase`, and PNG context cleanup xrefs. |
| `0x0059cc7c CDXTexture__AllocOrThrow` | `void * __stdcall CDXTexture__AllocOrThrow(void * png_decode_state, uint byte_count)` | `RET 0x8`, null/zero guards, malloc of `byte_count`, and decode-error throw on allocation failure. |
| `0x0059ccf3 CDXTexture__MemsetByte` | `void * __stdcall CDXTexture__MemsetByte(void * unused_context, void * destination_buffer, int fill_byte, uint byte_count)` | `RET 0x10`, dword-plus-tail byte fill, destination return, and intentionally unused context argument. |
| `0x0059cd26 CDXTexture__ReadU32BigEndian` | `uint __stdcall CDXTexture__ReadU32BigEndian(void * source_buffer)` | `RET 0x4`, four-byte big-endian uint32 reader used by PNG header, CRC, IHDR, gAMA, IDAT, and pass-row callers. |
| `0x0059cd4b CDXTexture__ReadChunkBytesAndUpdateCrc` | `void __stdcall CDXTexture__ReadChunkBytesAndUpdateCrc(void * png_decode_state, void * destination_buffer, uint byte_count)` | `RET 0xc`, source read into destination, then running chunk CRC update over the same span. |
| `0x0059cd62 CDXTexture__IsPngChunkCrcInvalid` | `bool __stdcall CDXTexture__IsPngChunkCrcInvalid(void * png_decode_state)` | `RET 0x4`, stored CRC read, conditional comparison with running CRC at decode-state `+0x100`, and invalid-CRC boolean return. |
| `0x0059cdbe CDXTexture__ValidateChunkTagAsciiOrLog` | `void __stdcall CDXTexture__ValidateChunkTagAsciiOrLog(void * png_decode_state, void * chunk_type_bytes)` | `RET 0x8`, four-byte chunk-tag ASCII range validation, and `"invalid chunk type"` diagnostic path. |

Wave713 read-back evidence verified candidate and selected pre exports with `11` metadata rows, `11` tag rows, `44` xref rows, `2871` instruction rows, and `11` decompile rows each. Dry/apply/final dry reported `updated=0 skipped=11 renamed=0 would_rename=0 signature_updated=11 comment_only_updated=0 missing=0 bad=0`, then `updated=11 skipped=0 renamed=0 would_rename=0 signature_updated=11 comment_only_updated=0 missing=0 bad=0`, then `updated=0 skipped=11 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`. Post exports verified `11` metadata rows, `11` tag rows, `44` xref rows, `2871` instruction rows, and `11` decompile rows. The pass hardened `11` signatures/parameter names, made no renames, made no function-boundary changes, and made no executable-byte changes. Post-Wave713 queue telemetry is `6098` total, `4154` commented, `1944` commentless, `1216` exact-undefined signatures, `183` `param_N`, strict clean-signature proxy `4098/6098 = 67.20%`, raw commentless head `0x0042f220 CSPtrSet__Clear`, and high-signal head `0x0059ce20 CDXTexture__ExpandPackedPixelsToScanline`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260521-234937_post_wave713_inflate_png_helper_head_verified`.

Exact `z_stream`/inflate-state layout, callback ABI, zlib source identity, PNG decode-state layout, chunk/CRC flags, allocator ownership, runtime inflate behavior, runtime PNG behavior, runtime decode/image fidelity, BEA patching, and rebuild parity remain unproven. The historical `0x0059c8c1 CDXTexture__InflateStream_ProcessZlibState` `extraout_EAX` downstream-helper artifact was resolved by Wave964 static read-back, while runtime/layout proof remains separate.

Probe anchors: `Wave713 inflate / PNG helper head`, `inflate-png-helper-head-wave713`, `0x0059c7cc CDXTexture__InflateInitStateFromHeader`, `0x0059cdbe CDXTexture__ValidateChunkTagAsciiOrLog`, `0x0059c8c1 CDXTexture__InflateStream_ProcessZlibState`, historical `extraout_EAX` caveat resolved by Wave964, `0x0059ce20 CDXTexture__ExpandPackedPixelsToScanline`, `0x0042f220 CSPtrSet__Clear`, `[maintainer-local-ghidra-backup-root]\BEA_20260521-234937_post_wave713_inflate_png_helper_head_verified`.

## Wave712 Decode Row Utility Head Read-Back Note

Wave712 decode row utility head saved eleven adjacent CTexture/CDXTexture/CFastVB row utility and decode helper rows. Tag anchor: `decode-row-utility-head-wave712`; the earliest raw commentless row after this pass is `0x0042f220 CSPtrSet__Clear`, and the next commentless high-signal row is `0x0059c7cc CDXTexture__InflateInitStateFromHeader`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x0059c070 CTexture__ProcessRowBatchesLinearStride` | `void __stdcall CTexture__ProcessRowBatchesLinearStride(int param_1, int param_2)` | Comment/tag-only by design; `RET 0x8`, hidden `unaff_ESI` row-batch descriptor, linear row pointers, and callback slots `[0xc]` / `[0xd]`. |
| `0x0059c110 CTexture__ProcessRowBatchesMcuStride128` | `void __stdcall CTexture__ProcessRowBatchesMcuStride128(int param_1, int param_2)` | Comment/tag-only by design; `RET 0x8`, hidden `unaff_ESI` row-batch descriptor, 0x80 byte-offset scaling, and callback slots `[0xc]` / `[0xd]`. |
| `0x0059c630 CTexture__AllocJpegQuantTableDescriptor` | `void __stdcall CTexture__AllocJpegQuantTableDescriptor(void * decode_state)` | `RET 0x4`, JPEG quant-table callers, 0x84-byte descriptor allocation through `decode_state +4`, store to `+0x20`, and clear `descriptor +0x80`. |
| `0x0059c650 CTexture__AllocJpegHuffmanTableDescriptor` | `void __stdcall CTexture__AllocJpegHuffmanTableDescriptor(void * decode_state)` | `RET 0x4`, JPEG Huffman-table callers, 0x118-byte descriptor allocation through `decode_state +4`, store to `+0x24`, and clear `descriptor +0x114`. |
| `0x0059c670 CDXTexture__CeilDiv` | `int __stdcall CDXTexture__CeilDiv(int value, int divisor)` | `RET 0x8`, JPEG/decode geometry callers, and `(value + divisor - 1) / divisor` helper shape. |
| `0x0059c690 CDXTexture__AlignUpToMultiple` | `int __stdcall CDXTexture__AlignUpToMultiple(int value, int multiple)` | `RET 0x8`, workspace/resource callers, and align-up by subtracting the remainder from `value + multiple - 1`. |
| `0x0059c6b0 CTexture__CopyRowsFromPointerTable` | `void __stdcall CTexture__CopyRowsFromPointerTable(void * src_row_table, int src_row_index, void * dst_row_table, int dst_row_index, int row_count, uint bytes_per_row)` | `RET 0x18`, source/destination row pointer tables, row count, and dword-plus-tail row copy. |
| `0x0059c700 CFastVB__CopyBlockRows128Bytes` | `void __stdcall CFastVB__CopyBlockRows128Bytes(void * src, void * dst, int block_row_count)` | `RET 0xc`, caller at `0x005ac57f`, and copy of `block_row_count << 7` bytes from source to destination. |
| `0x0059c730 CDXTexture__ZeroBufferBytes` | `void __stdcall CDXTexture__ZeroBufferBytes(void * buffer, uint byte_count)` | `RET 0x8`, row/decode callers, and dword-plus-tail zero fill. |
| `0x0059c750 CDXTexture__BeginAsyncDecodeJob` | `int __stdcall CDXTexture__BeginAsyncDecodeJob(void * decode_job)` | `RET 0x4`, null input returns `-2`, job/state field clears, async status seed, and `CDXTexture__ResetDecodeWindowState` call. |
| `0x0059c78f CDXTexture__FinishAsyncDecodeJob` | `int __stdcall CDXTexture__FinishAsyncDecodeJob(void * decode_job)` | `RET 0x4`, null input/callback returns `-2`, async handle closes, completion callback invocation, and decode-state pointer clear. |

Wave712 read-back evidence verified candidate and selected pre exports with `11` metadata rows, `11` tag rows, `57` xref rows, `2651` instruction rows, and `11` decompile rows each. Dry/apply/final dry reported `updated=0 skipped=11 renamed=0 would_rename=0 signature_updated=9 comment_only_updated=2 missing=0 bad=0`, then `updated=11 skipped=0 renamed=0 would_rename=0 signature_updated=9 comment_only_updated=2 missing=0 bad=0`, then `updated=0 skipped=11 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`. Post exports verified `11` metadata rows, `11` tag rows, `57` xref rows, `2651` instruction rows, and `11` decompile rows. The pass hardened `9` signatures/parameter names, left `2` hidden-ABI row walkers comment/tag-only, made no renames, made no function-boundary changes, and made no executable-byte changes. Post-Wave712 queue telemetry is `6098` total, `4143` commented, `1955` commentless, `1216` exact-undefined signatures, `194` `param_N`, strict clean-signature proxy `4087/6098 = 67.02%`, raw commentless head `0x0042f220 CSPtrSet__Clear`, and high-signal head `0x0059c7cc CDXTexture__InflateInitStateFromHeader`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260521-232045_post_wave712_decode_row_utility_head_verified`.

Exact row-batch descriptor layout, callback ABI, descriptor schemas, allocator contract, async job/state layout, runtime JPEG/PNG/decode behavior, runtime texture behavior, BEA patching, source identity, and rebuild parity remain unproven. The two row-batch walkers intentionally retain `param_1`/`param_2` and visible `unaff_ESI` in post decompile because their hidden-register ABI is not solved.

Probe anchors: `Wave712 decode row utility head`, `decode-row-utility-head-wave712`, `0x0059c070 CTexture__ProcessRowBatchesLinearStride`, `0x0059c78f CDXTexture__FinishAsyncDecodeJob`, `0x0059c110 CTexture__ProcessRowBatchesMcuStride128`, `0x0059c7cc CDXTexture__InflateInitStateFromHeader`, `0x0042f220 CSPtrSet__Clear`, `[maintainer-local-ghidra-backup-root]\BEA_20260521-232045_post_wave712_decode_row_utility_head_verified`.

## Wave711 Decode Allocator Head Read-Back Note

Wave711 decode allocator head saved seven adjacent CTexture/CDXTexture decode allocator rows. Tag anchor: `decode-allocator-head-wave711`; the earliest raw commentless row after this pass is `0x0042f220 CSPtrSet__Clear`, and the next commentless high-signal row is `0x0059c070 CTexture__ProcessRowBatchesLinearStride`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x0059bae0 CDXTexture__AllocFromBank_SplitBlock` | `int __stdcall CDXTexture__AllocFromBank_SplitBlock(void * allocator_owner, int bank_index, uint requested_size_bytes)` | `RET 0xc`, split-block free-list search at allocator state `+0x34`, 8-byte alignment, and 0x10-byte block-header payload return. |
| `0x0059bc10 CDXTexture__AllocLinearBlockAndTrack` | `int __stdcall CDXTexture__AllocLinearBlockAndTrack(void * allocator_owner, int bank_index, uint requested_size_bytes)` | `RET 0xc`, linear tracked-list insertion at allocator state `+0x3c`, byte accounting at `+0x4c`, and 0x10-byte block-header payload return. |
| `0x0059bcc0 CDXTexture__AllocRowPointerTableAndRows` | `int __stdcall CDXTexture__AllocRowPointerTableAndRows(void * allocator_owner, int bank_index, uint row_stride_bytes, uint row_count)` | `RET 0x10`, row-stride product cap, split-block pointer-table allocation, linear row-batch allocation, and row pointer table fill. |
| `0x0059bd60 CDXTexture__AllocMcuRowPointerTableAndRows` | `int __stdcall CDXTexture__AllocMcuRowPointerTableAndRows(void * allocator_owner, int bank_index, int mcu_units_per_row, uint row_count)` | `RET 0x10`, `mcu_units_per_row*0x80` row stride, split-block pointer-table allocation, linear row-batch allocation, and row pointer table fill. |
| `0x0059c3f0 CDXTexture__ReleaseDecodeBankLists` | `void __stdcall CDXTexture__ReleaseDecodeBankLists(void * allocator_owner, int bank_index)` | `RET 0x8`, bank 0/1 validation, bank-1 descriptor callback cleanup, and split/linear tracked-list drains. |
| `0x0059c510 CDXTexture__InitDecodeAllocatorVtable` | `void __stdcall CDXTexture__InitDecodeAllocatorVtable(void * allocator_owner)` | `RET 0x4`, 0x54-byte allocator-state allocation, decode allocator vtable slot installation, default budget storage, and bank-list initialization. |
| `0x0059c5d0 CDXTexture__PumpDecodeAllocatorAndSetStage` | `void __stdcall CDXTexture__PumpDecodeAllocatorAndSetStage(void * decode_state)` | `RET 0x4`, allocator vtable slot `+0x24` release of bank 1, and decode stage writes to `+0x14`. |

Wave711 read-back evidence verified candidate exports with `11` metadata rows, `11` tag rows, `25` xref rows, `407` instruction rows, and `11` decompile rows; deferred hidden-ABI candidates were `0x0059be00 CDXTexture__CreateDecodeJobDescriptor`, `0x0059be70 CDXTexture__AllocDecodeBlockAndLink`, `0x0059c070 CTexture__ProcessRowBatchesLinearStride`, and `0x0059c110 CTexture__ProcessRowBatchesMcuStride128`. Selected post evidence verified `7` metadata rows, `7` tag rows, `19` xref rows, `1687` instruction rows, and `7` decompile rows. The pass hardened `7` signatures/parameter names, made no renames, made no function-boundary changes, and made no executable-byte changes. Post-Wave711 queue telemetry is `6098` total, `4132` commented, `1966` commentless, `1216` exact-undefined signatures, `203` `param_N`, strict clean-signature proxy `4078/6098 = 66.87%`, raw commentless head `0x0042f220 CSPtrSet__Clear`, and high-signal head `0x0059c070 CTexture__ProcessRowBatchesLinearStride`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260521-225104_post_wave711_decode_allocator_head_verified`.

Exact allocator-state layout, exact decode-state layout, helper return ABI, descriptor callback contract, row-batch hidden-register ABI, runtime texture behavior, runtime image decode behavior, BEA patching, source identity, and rebuild parity remain unproven. The selected allocator helpers still document the `CDXTexture__AllocAligned16` `extraout_EAX` decompiler artifact where present, and `0x0059c510` still has a stale no-op helper label on the null path.

Probe anchors: `Wave711 decode allocator head`, `decode-allocator-head-wave711`, `0x0059bae0 CDXTexture__AllocFromBank_SplitBlock`, `0x0059c5d0 CDXTexture__PumpDecodeAllocatorAndSetStage`, `0x0059be00 CDXTexture__CreateDecodeJobDescriptor`, `0x0059be70 CDXTexture__AllocDecodeBlockAndLink`, `0x0059c070 CTexture__ProcessRowBatchesLinearStride`, `0x0059c110 CTexture__ProcessRowBatchesMcuStride128`, `0x0042f220 CSPtrSet__Clear`, `[maintainer-local-ghidra-backup-root]\BEA_20260521-225104_post_wave711_decode_allocator_head_verified`.

## Wave710 Decode Dispatch Head Read-Back Note

Wave710 decode dispatch head saved eight adjacent CTexture/CDXTexture decode-dispatch and callback-context rows. Tag anchor: `decode-dispatch-head-wave710`; the earliest raw commentless row after this pass is `0x0042f220 CSPtrSet__Clear`, and the next commentless high-signal row is `0x0059bae0 CDXTexture__AllocFromBank_SplitBlock`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x0059aec0 CTexture__CanUseCompactDecodePath` | `int __fastcall CTexture__CanUseCompactDecodePath(int unused_ecx, void * decode_state)` | Plain `RET`, EDX-loaded decode state, and compact-path branch evidence. |
| `0x0059af40 CTexture__ComputeDecodeBlockGeometry` | `void __stdcall CTexture__ComputeDecodeBlockGeometry(void * decode_state)` | `RET 0x4`, block dimension writes, and call into `CTexture__CanUseCompactDecodePath`. |
| `0x0059b370 CTexture__RunDecodeDispatchStage` | `void __stdcall CTexture__RunDecodeDispatchStage(void * decode_state)` | `RET 0x4`, dispatch context at `+0x1a8`, and callback-context progress writes. |
| `0x0059b4d0 CTexture__CreateDecodeDispatchContext` | `void __stdcall CTexture__CreateDecodeDispatchContext(void * decode_state)` | `RET 0x4`, 0x1c-byte dispatch-context allocation, and hidden-register initializer calls. |
| `0x0059b920 CDXTexture__DecodeState_RunPostFrameCallbacks` | `void __stdcall CDXTexture__DecodeState_RunPostFrameCallbacks(void * decode_state)` | `RET 0x4`, post-frame callback dispatch, and helper calls with hidden-register ABI gaps deferred. |
| `0x0059b960 CDXTexture__DecodeState_AdvanceFrame` | `int __stdcall CDXTexture__DecodeState_AdvanceFrame(void * decode_state)` | `RET 0x4`, status return, frame-step state update, and terminal-flag checks. |
| `0x0059ba20 CDXTexture__DecodeState_ResetCallbackContext` | `void __stdcall CDXTexture__DecodeState_ResetCallbackContext(void * decode_state)` | `RET 0x4`, callback-context reset, and clear of the observed `+0xa4` field. |
| `0x0059ba90 CDXTexture__DecodeState_CreateCallbackContext` | `void __stdcall CDXTexture__DecodeState_CreateCallbackContext(void * decode_state)` | `RET 0x4`, 0x1c-byte callback-context allocation, and state words initialized to 0/0/1. |

Wave710 read-back evidence verified candidate exports with `13` metadata rows, `13` tag rows, `17` xref rows, `3133` instruction rows, and `13` decompile rows; deferred hidden-ABI candidates were `0x0059b150 CTexture__InitDecodeLookupScratchTables`, `0x0059b1d0 CTexture__InitializeDecodePipelineFromHeader`, `0x0059b510 CDXTexture__ValidateJpegFrameAndBuildScanLayout`, `0x0059b6f0 CTexture__BuildComponentPlaneLayoutTables`, and `0x0059b880 CTexture__EnsureComponentDecodeScratchBlocks`. Selected post evidence verified `8` metadata rows, `8` tag rows, `12` xref rows, `1928` instruction rows, and `8` clean decompile rows. The pass hardened `8` signatures/parameter names, made no renames, made no function-boundary changes, and made no executable-byte changes. Post-Wave710 queue telemetry is `6098` total, `4125` commented, `1973` commentless, `1216` exact-undefined signatures, `210` `param_N`, strict clean-signature proxy `4071/6098 = 66.76%`, raw commentless head `0x0042f220 CSPtrSet__Clear`, and high-signal head `0x0059bae0 CDXTexture__AllocFromBank_SplitBlock`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260521-221723_post_wave710_decode_dispatch_head_verified`.

Exact decode-state layout, dispatch/callback-context layout, callback ABI, helper hidden-register ABIs, JPEG frame semantics, runtime image decode behavior, runtime image fidelity, BEA patching, source identity, and rebuild parity remain unproven.

Probe anchors: `Wave710 decode dispatch head`, `decode-dispatch-head-wave710`, `0x0059aec0 CTexture__CanUseCompactDecodePath`, `0x0059ba90 CDXTexture__DecodeState_CreateCallbackContext`, `0x0059b150 CTexture__InitDecodeLookupScratchTables`, `0x0059b880 CTexture__EnsureComponentDecodeScratchBlocks`, `0x0042f220 CSPtrSet__Clear`, `0x0059bae0 CDXTexture__AllocFromBank_SplitBlock`.

## Wave706 Node-Type Lifecycle Read-Back Note

Wave706 node-type lifecycle saved nine adjacent CFastVB/CTexture node-type `0x11` and `0x12` lifecycle rows. Tag anchor: `node-type-lifecycle-wave706`; the earliest raw commentless row after this pass is `0x0042f220 CSPtrSet__Clear`, and the next commentless high-signal row is `0x00599a74 CFastVB__SelectBestNodeTreeMatch_ReportWarningAndSetFlag`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x005997a5` | `void * __fastcall CFastVB__InitNodeType17(void * node_type17)` | Initializes node-type `0x11`, zeroes descriptor/resource slots, binds vtable `0x005ef374`, and returns the initialized pointer; CFastVB companion row is also summarized in [`FastVB.cpp`](../FastVB.cpp/_index.md). |
| `0x005997e1` | `int CTexture__NodeType12_Ctor_DeleteOnFlag(void)` | Hidden-ECX node-type `0x11` constructor copies descriptor/scalar stack inputs and clears owned slots; comment/tag-only for locked storage. |
| `0x00599831` | `void __fastcall CTexture__NodeType12_Dtor_DeleteOnFlag_Body(void * node_type17)` | Releases optional owned slots at `+0x3c/+0x40/+0x44..+0x50` and then releases the base node-payload chain. |
| `0x00599878` | `void * __fastcall CFastVB__CloneNodeTreeWithAddRef(void * source_node_type17)` | Allocates and initializes a node-type `0x11` clone, copies descriptor fields, clones/add-refs optional child resources, and destroys a partial clone on failure; CFastVB companion row is also summarized in [`FastVB.cpp`](../FastVB.cpp/_index.md). |
| `0x0059993c` | `void * __fastcall CTexture__NodeType12_Ctor(void * node_type12)` | Initializes node-type `0x12`, binds vtable `0x005ef384`, and seeds defaults `0xf0000` and `0xe40000`. |
| `0x0059996f` | `int CTexture__NodeType12_Ctor_ScalarDeletingDtor(void)` | Hidden-ECX node-type `0x12` constructor copies five stack scalars and seeds defaults; comment/tag-only for locked storage. |
| `0x005999b5` | `void __fastcall CTexture__NodeType12_ScalarDeletingDtor_Body(void * node_type12)` | Releases the optional owned pointer at `+0x28` and then releases the base node-payload chain. |
| `0x00599a3c` | `void * __thiscall CTexture__NodeType12_Dtor_DeleteOnFlag(void * this, uint delete_flags)` | Scalar-deleting wrapper for the node-type `0x11` destructor body; `RET 0x4` evidence removed an unused phantom parameter. |
| `0x00599a58` | `void * __thiscall CTexture__NodeType12_ScalarDeletingDtor(void * this, uint delete_flags)` | Scalar-deleting wrapper for the node-type `0x12` destructor body; `RET 0x4` evidence removed an unused phantom parameter. |

Wave706 read-back evidence verified `9` metadata rows, `9` tag rows, `12` xref rows, `801` instruction rows, and `9` clean decompile rows. The pass hardened `7` signatures/parameter names, left `2` locked-storage rows comment/tag-only, made no renames, made no function-boundary changes, and made no executable-byte changes. Post-Wave706 queue telemetry is `6098` total, `4104` commented, `1994` commentless, `1216` exact-undefined signatures, `231` `param_N`, strict clean-signature proxy `4050/6098 = 66.42%`, raw commentless head `0x0042f220 CSPtrSet__Clear`, and high-signal head `0x00599a74 CFastVB__SelectBestNodeTreeMatch_ReportWarningAndSetFlag`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260521-201902_post_wave706_node_type_lifecycle_verified`.

Exact node-type enum meanings, concrete field schema, hidden constructor ABI, child-resource ownership, reference-count semantics, runtime texture behavior, runtime vertex-buffer behavior, BEA patching, parser/source identity, and rebuild parity remain unproven.

Probe anchors: `Wave706 node-type lifecycle`, `node-type-lifecycle-wave706`, `0x005997a5 CFastVB__InitNodeType17`, `0x00599a58 CTexture__NodeType12_ScalarDeletingDtor`, `0x0042f220 CSPtrSet__Clear`, `0x00599a74 CFastVB__SelectBestNodeTreeMatch_ReportWarningAndSetFlag`.

## Wave705 Texture Serialized-Chunk Prelude Read-Back Note

Wave705 texture serialized-chunk prelude saved seven adjacent CTexture/CDXTexture/CFastVB serialized-chunk, debug-chunk, node span/stride, constant-register, float-grid, and binding rows. Tag anchor: `texture-serialized-chunk-prelude-wave705`; the earliest raw commentless row after this pass is `0x0042f220 CSPtrSet__Clear`, and the next commentless high-signal row is `0x005997a5 CFastVB__InitNodeType17`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x0059902a` | `int CDXTexture__RegisterSerializedChunk(void)` | Hidden-ECX registry helper validates chunk pointer/length input, handles a string-length sentinel, deduplicates existing records, appends a 0x14-byte record, and writes an optional output offset; comment/tag-only for locked storage. |
| `0x00599161` | `int __fastcall CTexture__ComputeDebugChunkDwordCount(void * chunk_builder)` | Computes aligned debug-chunk payload dword count plus the two-dword header. |
| `0x0059916d` | `int __thiscall CTexture__SerializeDebugChunkSymbolRecords(void * this, uint * out_chunk_dwords, uint max_dword_count)` | Writes the `0xfffe` debug-chunk header, copies record bytes, pads with `0xab`/`0xabababab`, and uses `RET 0x8` evidence to remove an unused phantom parameter. |
| `0x00599258` | `int __stdcall CFastVB__ComputeNodeSpanAndStride(void * node_tree, uint * out_span, uint * out_stride)` | Recursively computes node-tree span and stride for observed node kinds `8`, `7`, and `1`; CFastVB companion row is also summarized in [`FastVB.cpp`](../FastVB.cpp/_index.md). |
| `0x0059930d` | `int __thiscall CTexture__ValidateConstantRegisterDeclarationType(void * this, void * match_template_words32, void * register_decl, uint * out_component_count)` | Validates bool/int constant-register declaration node shapes and emits diagnostics `0xb54`/`0xb55`; `RET 0xc` evidence removes an unused phantom parameter. |
| `0x00599406` | `int __stdcall CDXTexture__SerializeFloatGridChunk(void * chunk_builder, uint row_count, uint column_count, void * value_source, uint * out_chunk_offset)` | Serializes a temporary float grid, registers chunk kind `6`, frees the temp buffer, and restores the fifth stack argument from `RET 0x14`. |
| `0x005994c4` | `int CDXTexture__ProcessTextureChunkAndEmitBindings(void)` | Locked-storage binding emitter classifies token globals, selects a node tree, binds constant-register suffixes up to `8191`, serializes optional float-grid/node-tree chunks, and registers the final binding chunk. |

Wave705 read-back evidence verified `7` metadata rows, `7` tag rows, `29` xref rows, `847` instruction rows, and `7` clean decompile rows. The pass hardened `5` signatures/parameter names, left `2` locked-storage rows comment/tag-only, made no renames, made no function-boundary changes, and made no executable-byte changes. Post-Wave705 queue telemetry is `6098` total, `4095` commented, `2003` commentless, `1216` exact-undefined signatures, `238` `param_N`, strict clean-signature proxy `4041/6098 = 66.27%`, raw commentless head `0x0042f220 CSPtrSet__Clear`, and high-signal head `0x005997a5 CFastVB__InitNodeType17`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260521-194929_post_wave705_texture_serialized_chunk_prelude_verified`.

Exact chunk-builder layout, chunk/flag enums, record and binding schemas, node/declaration layouts, selected-node ABI, token enum, parser/source identity, runtime shader/texture behavior, runtime vertex-buffer behavior, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave705 texture serialized-chunk prelude`, `texture-serialized-chunk-prelude-wave705`, `0x0059902a CDXTexture__RegisterSerializedChunk`, `0x005994c4 CDXTexture__ProcessTextureChunkAndEmitBindings`, `0x0042f220 CSPtrSet__Clear`, `0x005997a5 CFastVB__InitNodeType17`.

## Wave704 Node-Type Constructors/Destructors Read-Back Note

Wave704 node-type constructors/destructors saved twenty adjacent CTexture/CDXTexture/CFastVB node-type and owned-list rows. Tag anchor: `node-type-constructors-wave704`; the earliest raw commentless row after this pass is `0x0042f220 CSPtrSet__Clear`, and the next commentless high-signal row is `0x00599161 CTexture__ComputeDebugChunkDwordCount`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x005989c3` | `void __fastcall CTexture__NodeType8_InitDefaults(void * node_type8)` | Initializes a node-type-8 payload, clears child/sibling links, sets kind/class field `+0x4` to `2`, and binds vtable `0x005ef240`. |
| `0x005989db` | `void __thiscall CTexture__NodeType8_InitFromDescriptor(void * this, void * descriptor_words32)` | Initializes the same node-type-8 header, then copies eight descriptor dwords into `+0x10`. |
| `0x00598a56` | `void __fastcall CFastVB__InitNodeType9(void * node_type9)` | Initializes node-type-9 state with kind/class `8`, vtable `0x005ef250`, null links, zeroed payload fields, and `+0x14 = 9`; CFastVB companion row is also summarized in [`FastVB.cpp`](../FastVB.cpp/_index.md). |
| `0x00598a81` | `int CFastVB__NodeType9__ctor(void)` | Hidden-ECX node-type-9 constructor copies five stack values into `+0x10..+0x20`; comment/tag-only because Ghidra reports locked storage. |
| `0x00598abd` | `void __fastcall CFastVB__NodeType9__dtor(void * node_type9)` | Restores node-type-9 vtable and releases the node-payload child/sibling chain. |
| `0x00598b48` | `void __fastcall CFastVB__InitNodeType10(void * node_type10)` | Initializes node-type-10 state with kind/class `10`, vtable `0x005ef260`, and zeroed owned/resource pointer slots through `+0x38`; CFastVB companion row is also summarized in [`FastVB.cpp`](../FastVB.cpp/_index.md). |
| `0x00598b81` | `void __fastcall CFastVB__NodeType10_dtor(void * node_type10)` | Releases owned pointers/resources at `+0x20/+0x24/+0x28/+0x2c/+0x30/+0x38`, then releases the base node-payload chain. |
| `0x00598d6b` | `void * __fastcall CFastVB__InitNodeType13(void * node_type13)` | Initializes node-type-13 state with kind/class `0xd`, vtable `0x005ef270`, zeroed storage through `+0x3c`, `+0x10 = 3`, and returns the node pointer. |
| `0x00598da4` | `int CDXTexture__NodeType13__ctor(void)` | Hidden-ECX node-type-13 constructor copies stack scalar fields and eight descriptor dwords into `+0x20`; comment/tag-only for locked storage. |
| `0x00598ddc` | `int CDXTexture__NodeType13__ctorWithRefBump(void)` | Hidden-ECX node-type-13 constructor stores a referenced object at `+0x18`, copies descriptor dwords, and calls referenced vslot `+4` when non-null. |
| `0x00598e22` | `void __fastcall CTexture__Dtor_ReleaseNodePayloadByKind(void * node_payload)` | Releases optional `+0x18` child/reference state based on `+0x10`, then releases the base node-payload chain. |
| `0x00598e5d` | `int __thiscall CDXTexture__CompareNodePayloadWithOptionalChild(void * this, void * candidate_payload)` | Compares format/class id, four dwords at `+0x10`, and optional type-4 child/payload compatibility. |
| `0x00598f22` | `void * __thiscall CDXTexture__Dtor_ReleaseNodePayload_DeleteOnFlag(void * this, uint delete_flags)` | Scalar-deleting-style release wrapper: releases the chain, frees on delete bit 0, returns `this`. |
| `0x00598f3e` | `void * __thiscall CDXTexture__Dtor_NodePayload_DeleteOnFlag(void * this, uint delete_flags)` | Resets vtable `0x005ef230`, releases the chain, frees on delete bit 0, returns `this`. |
| `0x00598f60` | `void * __thiscall CFastVB__NodeType8_scalar_deleting_dtor(void * this, uint delete_flags)` | Node-type-8 scalar-deleting wrapper; CFastVB companion row is also summarized in [`FastVB.cpp`](../FastVB.cpp/_index.md). |
| `0x00598f82` | `void * __thiscall CFastVB__NodeType9_scalar_deleting_dtor(void * this, uint delete_flags)` | Node-type-9 scalar-deleting wrapper; CFastVB companion row is also summarized in [`FastVB.cpp`](../FastVB.cpp/_index.md). |
| `0x00598fa4` | `void * __thiscall CFastVB__NodeType10_scalar_deleting_dtor(void * this, uint delete_flags)` | Calls the node-type-10 destructor body, then frees on delete bit 0; CFastVB companion row is also summarized in [`FastVB.cpp`](../FastVB.cpp/_index.md). |
| `0x00598fc0` | `void * __thiscall CTexture__Dtor_ReleaseNodePayload_DeleteOnFlag(void * this, uint delete_flags)` | Calls the kind-dispatch destructor body, then frees on delete bit 0. |
| `0x00598fdc` | `void __thiscall CTexture__InitOwnedNodeList(void * this, void * owner_context)` | Initializes an owned-node-list header and tail-link pointer. |
| `0x00598ff4` | `void __fastcall CTexture__FreeOwnedNodeListAndPayloads(void * owned_node_list)` | Drains owned-node records, conditionally frees payloads based on observed flags, and frees each node record. |

Wave704 read-back evidence verified `20` metadata rows, `20` tag rows, `45` xref rows, `2420` instruction rows, and `20` clean decompile rows. The pass hardened `17` signatures/parameter names, left `3` locked-storage rows comment/tag-only, made no renames, made no function-boundary changes, and made no executable-byte changes. Post-Wave704 queue telemetry is `6098` total, `4088` commented, `2010` commentless, `1216` exact-undefined signatures, `243` `param_N`, strict clean-signature proxy `4034/6098 = 66.15%`, raw commentless head `0x0042f220 CSPtrSet__Clear`, and high-signal head `0x00599161 CTexture__ComputeDebugChunkDwordCount`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260521-185425_post_wave704_node_type_constructors_verified`.

Exact node-type enum values, concrete node/owned-list/descriptor layouts, hidden calling-convention ABI, reference-count semantics, parser/source identity, runtime texture behavior, runtime vertex-buffer behavior, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave704 node-type constructors/destructors`, `node-type-constructors-wave704`, `0x005989c3 CTexture__NodeType8_InitDefaults`, `0x00598ff4 CTexture__FreeOwnedNodeListAndPayloads`, `0x0042f220 CSPtrSet__Clear`, `0x00599161 CTexture__ComputeDebugChunkDwordCount`.

## Wave703 Node Payload Head Read-Back Note

Wave703 node payload head saved twelve adjacent CTexture/CDXTexture/CFastVB node-payload helper rows. Tag anchor: `ctexture-node-payload-head-wave703`; the next queue head after this pass is `0x005989c3 CTexture__NodeType8_InitDefaults`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
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
| `0x00598873` | `void * __fastcall CFastVB__CloneNodeChainWithAddRef(void * source_chain)` | Clones kind-1 wrapper nodes, copies `+0x10`, clones children through vslot `+0x8`, rolls back failed child clones, and links cloned siblings; CFastVB companion row is also summarized in [`FastVB.cpp`](../FastVB.cpp/_index.md). |
| `0x005988f5` | `int __fastcall CFastVB__CompareNodeValuesByTagAndPayload(void * left_payload)` | Compares the ECX-held left payload with a hidden EAX-held right payload by tag, including scalar/pointer, inline-string, indirect-string, and double-like cases; CFastVB companion row is also summarized in [`FastVB.cpp`](../FastVB.cpp/_index.md). |

Wave703 read-back evidence verified `12` metadata rows, `12` tag rows, `60` xref rows, `444` instruction rows, and `12` clean decompile rows. The pass hardened `10` signatures/parameter names, left `2` locked-storage rows comment/tag-only, made no renames, made no function-boundary changes, and made no executable-byte changes. Post-Wave703 queue telemetry is `6098` total, `4068` commented, `2030` commentless, `1216` exact-undefined signatures, `260` `param_N`, strict clean-signature proxy `4014/6098 = 65.82%`, and next head `0x005989c3 CTexture__NodeType8_InitDefaults`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260521-182413_post_wave703_node_payload_head_verified`.

Exact node-payload struct layout, payload type enum, vtable contract, hidden-register comparator ABI, AddRef semantics, parser reduction behavior, runtime texture behavior, runtime vertex-buffer behavior, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave703 node payload head`, `ctexture-node-payload-head-wave703`, `0x00598702 CTexture__NodePayloadBaseCtor`, `0x005988f5 CFastVB__CompareNodeValuesByTagAndPayload`, `0x005989c3 CTexture__NodeType8_InitDefaults`.

## Wave702 DXT Codec / Dispatch Read-Back Note

Wave702 DXT codec / dispatch saved eleven adjacent DXT decode, encode, alpha-pack, and dispatch-table rows spanning CDXTexture/CTexture and CFastVB-labelled helpers. Tag anchor: `dxt-codec-dispatch-wave702`; the next queue head after this pass is `0x00598702 CTexture__NodePayloadBaseCtor`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x0059764a` | `int __stdcall CDXTexture__DecodeDxt1ColorBlockToRgba(float * rgba_float_block16_out, void * dxt1_color_block)` | Decodes two RGB565 endpoints into a DXT1 palette and writes sixteen RGBA float4 rows from the two-bit selector mask. |
| `0x0059778a` | `int __stdcall CTexture__DecodeDxt3BlockToFloatRgba(float * rgba_float_block16_out, void * dxt3_block)` | Reuses the DXT1 color decoder at `block+8`, then expands explicit 4-bit alpha nibbles into sixteen output alpha lanes. |
| `0x0059780d` | `int __stdcall CTexture__DecodeDxt5BlockToFloatRgba(float * rgba_float_block16_out, void * dxt5_block)` | Reuses the DXT1 color decoder at `block+8`, builds the DXT5 alpha ladder, and applies two 24-bit selector groups. |
| `0x00597949` | `int __stdcall CTexture__EncodeDxt5AlphaIndices_ErrorDiffusion(void * dxt_color_block_out, float * rgba_float_block16)` | Error-diffuses alpha samples, rounds corrected values, and calls the scalar selector quantizer with the observed alpha-mode marker. |
| `0x00597a61` | `void __stdcall CFastVB__PackScalarBlock_4BitEndpoints(void * dxt3_block_out, float * rgba_float_block16)` | Packs explicit 4-bit alpha nibbles with residual diffusion, then quantizes the color selector block at `output+8`; CFastVB companion row is also summarized in [`FastVB.cpp`](../FastVB.cpp/_index.md). |
| `0x00597b87` | `int __stdcall CFastVB__PackScalarBlock_InterpolatedEndpoints(void * dxt5_block_out, float * rgba_float_block16)` | Solves DXT5 alpha endpoints, builds selector remap tables, and packs selector bytes with residual diffusion; CFastVB companion row is also summarized in [`FastVB.cpp`](../FastVB.cpp/_index.md). |
| `0x00598056` | `void __stdcall CTexture__EncodeDxt3AlphaBlock(void * dxt3_block_out)` | Premultiplies a hidden source block into stack storage and forwards it to the DXT3 scalar-block packer. |
| `0x0059808a` | `int __stdcall CTexture__EncodeDxt5AlphaBlock(void * dxt5_block_out)` | Premultiplies a hidden source block into stack storage and forwards it to the DXT5 scalar-block packer. |
| `0x005980be` | `void __cdecl CFastVB__InitDispatchTableVariant_005980be(void * math_dispatch_table)` | Seeds one math dispatch-table variant with observed transform, matrix, quaternion, half-float, and batch helper pointers; CFastVB companion row is also summarized in [`FastVB.cpp`](../FastVB.cpp/_index.md). |
| `0x0059822c` | `void __cdecl CFastVB__InitDispatchTableVariant_0059822c(void * math_dispatch_table)` | Seeds an alternate dispatch-table variant with alternate matrix/quaternion/batch helpers and SIMD half-float conversion slots; CFastVB companion row is also summarized in [`FastVB.cpp`](../FastVB.cpp/_index.md). |
| `0x00598474` | `void __cdecl CFastVB__InitDispatchOpsFromFeatureFlags(void * math_dispatch_table)` | Queries `CFastVB__DetectCpuFeatureMask` and conditionally replaces dispatch slots for observed feature-mask bits; CFastVB companion row is also summarized in [`FastVB.cpp`](../FastVB.cpp/_index.md). |

Wave702 read-back evidence verified `11` metadata rows, `11` tag rows, `17` xref rows, `1067` instruction rows, and `11` clean decompile rows. The pass hardened `11` signatures/parameter names, made no renames, made no function-boundary changes, and made no executable-byte changes. Post-Wave702 queue telemetry is `6098` total, `4056` commented, `2042` commentless, `1216` exact-undefined signatures, `270` `param_N`, strict clean-signature proxy `4002/6098 = 65.63%`, and next head `0x00598702 CTexture__NodePayloadBaseCtor`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260521-175105_post_wave702_dxt_codec_dispatch_verified`.

Exact DXT block ABI, alpha selector ordering, residual diffusion policy, dispatch-table slot schema, CPU feature-bit names, runtime texture fidelity, runtime compression quality, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave702 DXT codec / dispatch`, `dxt-codec-dispatch-wave702`, `0x0059764a CDXTexture__DecodeDxt1ColorBlockToRgba`, `0x00598474 CFastVB__InitDispatchOpsFromFeatureFlags`, `0x00598702 CTexture__NodePayloadBaseCtor`.

## Wave701 Texture Math / DXT Prelude Read-Back Note

Wave701 texture math / DXT prelude saved twelve adjacent texture math, dispatch-table, RGB565, alpha-block, endpoint-solver, and DXT selector rows spanning CDXTexture/CTexture and CFastVB-labelled helpers. Tag anchor: `texture-math-dxt-prelude-wave701`; the next queue head after this pass is `0x0059764a CDXTexture__DecodeDxt1ColorBlockToRgba`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x005960c1` | `double __stdcall CDXTexture__FastReciprocalSqrtScalar(uint float_bits)` | Computes a table-assisted reciprocal square-root approximation from raw IEEE-style float bits using `DAT_00658c98/DAT_00658c9c` lookup tables and exponent adjustment. |
| `0x00596106` | `float * __stdcall CDXTexture__NormalizeVec3Fast(float * normalized_vec3_out, float * input_vec3)` | Measures a three-float vector, zeroes output for zero length, copies already-near-unit vectors, or scales xyz by the reciprocal square-root approximation. |
| `0x005961d0` | `void __stdcall CDXTexture__MultiplyMatrix4x4_InPlaceSafe(float * matrix4x4_out, float * left_matrix4x4, float * right_matrix4x4)` | Multiplies observed 4x4 float matrices, including the right-matrix alias case and a 16-dword scratch copy when both inputs alias the destination. |
| `0x005962b3` | `void __stdcall CDXTexture__MultiplyMatrix4x4_Safe(float * matrix4x4_out, float * left_matrix4x4, float * right_matrix4x4)` | Multiplies observed 4x4 float matrices through scratch storage when the destination aliases either input. |
| `0x00596341` | `void __stdcall CFastVB__InitMathDispatchTable(void * math_dispatch_table)` | Seeds dispatch slots with fixed helper labels and function pointers, including the two matrix multiply helpers and `CDXTexture__NormalizeVec3Fast`; CFastVB companion row is also summarized in [`FastVB.cpp`](../FastVB.cpp/_index.md). |
| `0x00596386` | `void __fastcall CDXTexture__UnpackRgb565ToRgbaFloat(uint rgb565_word)` | Expands RGB565 into normalized RGBA float lanes, writes alpha 1.0, and stores through a hidden EAX float4 pointer not represented in the saved signature. |
| `0x005963d2` | `int __fastcall CDXTexture__NormalizeColorBlockByAlpha(void * rgba_float_block16)` | Walks sixteen float4 RGBA entries, zeroes RGB at alpha 0, divides RGB by alpha below 1.0, and clamps normalized RGB lanes to 1.0. |
| `0x00596450` | `int __fastcall CTexture__PremultiplyAlphaBlock16(void * premultiplied_rgba_out)` | Copies sixteen hidden-EAX source float4 RGBA entries, multiplies RGB by alpha, and preserves alpha in the output block. |
| `0x00596480` | `uint __fastcall CFastVB__PackClampedRgbToR5G6B5(void * rgb_float_triplet)` | Clamps three float RGB lanes, rounds through 5-bit/6-bit scale constants, and packs an RGB565 endpoint word; CFastVB companion row is also summarized in [`FastVB.cpp`](../FastVB.cpp/_index.md). |
| `0x00596589` | `void __stdcall CFastVB__SolveScalarEndpointPairFromSamples(float * endpoint_min_out, float * endpoint_max_out, float * scalar_samples16)` | Scans sixteen scalar samples, chooses min/max candidates, uses hidden EBX as endpoint-count/mode input, and iteratively refines scalar endpoints; CFastVB companion row is also summarized in [`FastVB.cpp`](../FastVB.cpp/_index.md). |
| `0x005968a4` | `void __stdcall CFastVB__SolveVectorEndpointPairFromSamples(float * endpoint_min_rgb_out, float * endpoint_max_rgb_out, float * rgba_samples16, int endpoint_count)` | Scans sixteen four-float sample rows, chooses an RGB bounding axis/order, and optionally refines RGB endpoints for endpoint counts 3 or 4; CFastVB companion row is also summarized in [`FastVB.cpp`](../FastVB.cpp/_index.md). |
| `0x00596e23` | `int __stdcall CFastVB__QuantizeScalarBlockIndices(void * dxt_color_block_out, float alpha_mode_weight)` | Quantizes a hidden-EAX sixteen-pixel float RGBA block into endpoint and selector output, calls the vector endpoint solver, packs/unpacks RGB565 endpoints, and writes the 32-bit selector mask; CFastVB companion row is also summarized in [`FastVB.cpp`](../FastVB.cpp/_index.md). |

Wave701 read-back evidence verified `12` metadata rows, `12` tag rows, `24` xref rows, `1068` instruction rows, and `12` clean decompile rows. The pass hardened `12` visible signatures/parameter names, documented hidden EAX/EBX ABI gaps where present, made no renames, made no function-boundary changes, and made no executable-byte changes. Post-Wave701 queue telemetry is `6098` total, `4045` commented, `2053` commentless, `1216` exact-undefined signatures, `281` `param_N`, strict clean-signature proxy `3991/6098 = 65.45%`, and next head `0x0059764a CDXTexture__DecodeDxt1ColorBlockToRgba`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260521-172303_post_wave701_texture_math_dxt_prelude_verified`.

Exact lookup-table provenance, numeric error bounds, vector/matrix layout conventions, dispatch-table schema, CPU feature replacement behavior, hidden EAX/EBX helper ABI, RGB565 color-space convention, DXT block schema, alpha-mode semantics, residual diffusion policy, runtime math correctness, runtime texture fidelity, runtime compression quality, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave701 texture math / DXT prelude`, `texture-math-dxt-prelude-wave701`, `0x005960c1 CDXTexture__FastReciprocalSqrtScalar`, `0x00596e23 CFastVB__QuantizeScalarBlockIndices`, `0x0059764a CDXTexture__DecodeDxt1ColorBlockToRgba`.

## Wave700 CTexture JPEG Compression Defaults Read-Back Note

Wave700 CTexture JPEG compression defaults saved nine adjacent IJG-style JPEG compression-default, input/pass, quant-table, Huffman-table, and scan-script helper rows. Tag anchor: `ctexture-jpeg-compression-defaults-wave700`; the next queue head after this pass is `0x005960c1 CDXTexture__FastReciprocalSqrtScalar`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x00595350` | `void __stdcall CTexture__ProcessDecodeStateMachineStep(void * jpeg_compress_context)` | Advances the observed IJG-style compression pass controller after input consumption, accepts states `0x65/0x66/0x67`, emits diagnostics `0x43/0x14/0x18`, loops over component count at `+0xf8`, and finishes through coefficient/master/output controller slots before `CDXTexture__PumpDecodeAllocatorAndSetStage`. |
| `0x00595430` | `void __stdcall CTexture__ResetDecodePipelineForNextChunk(void * jpeg_compress_context, int reset_sent_table_flags)` | Requires state `100`, optionally clears sent-table flags through `CTexture__SetDecodeTableEpoch(..., 0)`, reinitializes the JPEG encoder pipeline, resets input offset `+0xe8`, and moves state to `0x65` or `0x66` based on `+0xb0`. |
| `0x005954a0` | `void __stdcall CTexture__ReadDecodeInputBytes(void * jpeg_compress_context, void * destination_buffer, uint requested_byte_count)` | Requires state `0x65`, reports diagnostic `0x7b` when input is exhausted, updates progress slots with `+0xe8/+0x20`, clamps the request to remaining input, dispatches the source-manager callback at `+0x158 +4` with `destination_buffer`, and advances `+0xe8`. |
| `0x00595550` | `void __stdcall CTexture__LoadAndScaleQuantizationTable(void * jpeg_compress_context, int table_index, void * source_quant_table, int quality_scale_percent, int force_baseline_range)` | Validates `table_index 0..3`, allocates a quant-table descriptor when absent, scales 64 entries as `(value * quality_scale_percent + 50) / 100`, clamps to `1..0x7fff`, optionally clamps to `<=0xff`, and clears sent-table state. |
| `0x00595820` | `void __stdcall CTexture__LoadHuffmanTableDefinition(void * jpeg_compress_context, void * huff_values_table)` | Allocates a Huffman descriptor when the register-held slot is null, copies the register-held bits/count header, validates a `1..0x100` symbol budget, copies `huff_values_table` bytes, and clears sent-table state. |
| `0x005958e0` | `void CTexture__LoadDefaultHuffmanTables(void)` | Comment/tag-only row because Ghidra reports unknown calling convention with locked storage and hidden ESI context; dispatches the four built-in tables at `DAT_005eef80`, `DAT_005eeec8`, `DAT_005eeea8`, and `DAT_005eedf0`. |
| `0x00595930` | `void __stdcall CTexture__DeflateConfig_SetPreset(void * jpeg_compress_context, int scan_script_preset)` | Existing `Deflate` name kept; body writes JPEG scan-script/component selector rows under state `100`, resets scan flags at `+0xd0/+0xdc/+0xe0/+0xe4`, configures preset cases `0..5`, and reports diagnostics `0x14/0x1a/0x0a`. |
| `0x00595c10` | `void __stdcall CTexture__ConfigureDeflatePresetByCompressionMode(void * jpeg_compress_context)` | Existing `Deflate` name kept; maps compression/color-mode field `+0x28` to JPEG scan-script presets `0/3/4` or inline case `1/5` setup, and reports diagnostic `0x09` for unsupported modes. |
| `0x00595da0` | `void __stdcall CTexture__InitializeJpegCompressionDefaults(void * jpeg_compress_context)` | Allocates the `0x348`-byte scan/component workspace when absent, sets data precision `8`, loads default quant tables from `0x5eecd8/0x5eebd8` at quality scale `0x32`, installs default Huffman tables, initializes component defaults, and configures the scan-script preset. |

Wave700 read-back evidence verified `9` metadata rows, `9` tag rows, `15` xref rows, `333` instruction rows, and `9` clean decompile rows. The pass hardened `8` signatures, left one locked-storage row comment/tag-only, made no renames, made no function-boundary changes, and made no executable-byte changes. Post-Wave700 queue telemetry is `6098` total, `4033` commented, `2065` commentless, `1216` exact-undefined signatures, `293` `param_N`, strict clean-signature proxy `3979/6098 = 65.25%`, and next head `0x005960c1 CDXTexture__FastReciprocalSqrtScalar`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260521-165600_post_wave700_ctexture_jpeg_compression_defaults_verified`.

Exact JPEG context layout, controller vtable ABI, source-manager ABI, quant-table descriptor layout, Huffman descriptor layout, hidden-register Huffman helper ABI, scan-script row layout, color-space enum, default table provenance, naming provenance for the existing `Deflate` labels, runtime JPEG encoder behavior, runtime entropy-table behavior, runtime image fidelity, BEA patching, and rebuild parity remain unproven. The current decompile evidence for the existing `Deflate`-named helpers shows JPEG scan-script/component selector setup, not zlib deflate proof.

Probe anchors: `Wave700 CTexture JPEG compression defaults`, `ctexture-jpeg-compression-defaults-wave700`, `0x00595350 CTexture__ProcessDecodeStateMachineStep`, `0x00595da0 CTexture__InitializeJpegCompressionDefaults`, `0x005960c1 CDXTexture__FastReciprocalSqrtScalar`.

## Wave699 CDXTexture PNG Decode-Workspace Tail Read-Back Note

Wave699 CDXTexture PNG decode-workspace tail saved eight adjacent PNG workspace, CRC, allocation, and IJG-style JPEG context/table helper rows. Tag anchor: `cdxtexture-png-decode-workspace-tail-wave699`; the next queue head after this pass is `0x00595350 CTexture__ProcessDecodeStateMachineStep`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x0059512b` | `void * __stdcall CDXTexture__AllocZeroedDecodeBuffer(void * allocator_context, uint element_count, uint element_size)` | Multiplies `element_count` by `element_size`, allocates through `CDXTexture__AllocOrThrow`, zeroes the allocated span, and returns the allocated buffer pointer; xrefs include PNG PLTE parsing and a CreatePngDecodeContext callback slot. |
| `0x0059517e` | `void __stdcall CDXTexture__FreeDecodeBufferIfPresent(void * decode_state, void * decode_buffer)` | Frees `decode_buffer` through `CRT__FreeBase` only when both inputs are non-null; xrefs include ResetPngDecodeContext and a CreatePngDecodeContext callback slot. |
| `0x00595183` | `void __stdcall CDXTexture__InitDecodeSeedDefault(void * png_decode_state)` | Initializes `png_decode_state +0x100` with `CDXTexture__Crc32_Update(0, null, 0)` before header/pass/IDAT processing. |
| `0x0059519a` | `void __stdcall CDXTexture__UpdateChunkCrc(void * png_decode_state, void * source_buffer, uint byte_count)` | Checks observed decode-state flags at `+0x10c/+0x5c`, then updates `+0x100` with CRC32 over `source_buffer` and `byte_count` unless flags suppress accumulation. |
| `0x005951d9` | `void __stdcall CDXTexture__ZeroDecodeWorkspace16Dwords(void * png_decode_state, void * workspace)` | Preserves the two-argument ABI while zeroing 16 dwords at `workspace`; current xrefs show two ResetPngDecodeContext workspace clears. |
| `0x005951e9` | `void * __stdcall CDXTexture__AllocZeroedInflateState(int state_required_flag)` | Returns null when the flag is zero; otherwise allocates decode-state class `2` through `CDXTexture__AllocZeroedDecodeState` and zeroes the first 16 dwords. |
| `0x00595220` | `void __stdcall CTexture__ResetDecodeContextWithDefaults(void * jpeg_compress_context, int expected_libjpeg_version, int expected_struct_size)` | Checks observed IJG-style constants `0x3e` and `0x180`, zeroes `0x60` dwords while preserving slots `+0x0/+0xc`, initializes allocator/vtable helper state, and sets default state fields including `+0x14 = 100`. |
| `0x005952e0` | `void __stdcall CTexture__SetDecodeTableEpoch(void * jpeg_compress_context, int sent_table_flag)` | Writes `sent_table_flag` into four quant-table slots at `+0x80` and paired DC/AC Huffman table slots at `+0x114`, matching an IJG `jpeg_suppress_tables`-style table-state sweep. |

Wave699 read-back evidence verified `8` metadata rows, `8` tag rows, `13` xref rows, `296` instruction rows, and `8` clean decompile rows. The pass hardened `8` signatures, made no renames, made no function-boundary changes, and made no executable-byte changes. Post-Wave699 queue telemetry is `6098` total, `4024` commented, `2074` commentless, `1216` exact-undefined signatures, `301` `param_N`, strict clean-signature proxy `3970/6098 = 65.10%`, and next head `0x00595350 CTexture__ProcessDecodeStateMachineStep`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260521-163011_post_wave699_cdxtexture_png_decode_workspace_tail_verified`.

Exact PNG decode-state layout, allocator ABI, overflow policy, workspace ownership, CRC flag enum, chunk-read contract, zlib/inflate-state layout, JPEG context layout, IJG/libjpeg source identity, runtime PNG behavior, runtime cleanup behavior, runtime image fidelity, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave699 CDXTexture PNG decode-workspace tail`, `cdxtexture-png-decode-workspace-tail-wave699`, `0x0059512b CDXTexture__AllocZeroedDecodeBuffer`, `0x005952e0 CTexture__SetDecodeTableEpoch`, `0x00595350 CTexture__ProcessDecodeStateMachineStep`.

## Wave698 CDXTexture PNG Decode-Option Tail Read-Back Note

Wave698 CDXTexture PNG decode-option tail saved eight adjacent PNG decode-option, source-read, and signature-check helper rows. Tag anchor: `cdxtexture-png-decode-option-tail-wave698`; the next queue head after this pass is `0x0059512b CDXTexture__AllocZeroedDecodeBuffer`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x00594ef8` | `void __stdcall CDXTexture__SetDecodeOptionFloat(void * png_decode_state, void * png_info_state, double option_value)` | Sets observed info-state flag `0x1` and stores `option_value` as a float at `+0x28`; xrefs include PNG gAMA parsing and sRGB default-gamma setup. |
| `0x00594fb6` | `void __stdcall CTexture__SetDecodeScanParameters(void * png_decode_state, void * png_info_state, void * scan_parameter_table, int scan_parameter_count)` | Sets observed info-state flag `0x8`, stores `scan_parameter_table` at `+0x10`, and stores the low-word count at `+0x14`; current xref is PNG PLTE parsing. |
| `0x00594fdc` | `void __stdcall CDXTexture__SetDecodeOptionByte(void * png_decode_state, void * png_info_state, int option_byte_value)` | Sets byte flag `0x8` at `info_state +0x9` and stores the low byte at `+0x2c`; xrefs include PNG-from-memory setup and the sRGB byte/default helper. |
| `0x00594ff9` | `void __stdcall CDXTexture__SetDecodeOptionByteWithDefaultFloat(void * png_decode_state, void * png_info_state, int option_byte_value)` | Calls the byte-option helper with `option_byte_value`, then calls the float-option helper with the static double at `0x005eeb30`; current xref is PNG sRGB parsing. |
| `0x00595030` | `void __stdcall CDXTexture__SetDecodeOptionParams(void * png_decode_state, void * png_info_state, void * parameter_table, int parameter_count, void * parameter_record)` | Stores an optional table at `+0x30`, copies a 10-byte record into `+0x34` when supplied, defaults a copied zero count to one, sets observed flag `0x10`, and stores the low-word count at `+0x16`. |
| `0x00595079` | `void __stdcall CDXTexture__ReadFromSource(void * png_decode_state, void * destination_buffer, uint requested_byte_count)` | Dispatches through the source callback at `decode_state +0x50` or throws a decode error when no callback is installed. |
| `0x005950a2` | `void __stdcall CDXTexture__SetReadFunction(void * png_decode_state, void * read_context, void * read_callback)` | Stores read context/callback at `+0x54/+0x50`, warns and clears a buffered-read slot when present, and clears `+0x120`. |
| `0x005950e0` | `int __stdcall CDXTexture__ComparePngSignatureBytes(void * signature_buffer, uint start_offset, uint bytes_to_check)` | Compares a caller-selected slice of `signature_buffer` against the 8-byte PNG signature literal at `0x005eebcc`, clamping to the remaining signature span. |

Wave698 read-back evidence verified `8` metadata rows, `8` tag rows, `18` xref rows, `296` instruction rows, and `8` clean decompile rows. The pass hardened `8` signatures, made no renames, made no function-boundary changes, and made no executable-byte changes. Post-Wave698 queue telemetry is `6098` total, `4016` commented, `2082` commentless, `1216` exact-undefined signatures, `310` `param_N`, strict clean-signature proxy `3962/6098 = 64.97%`, and next head `0x0059512b CDXTexture__AllocZeroedDecodeBuffer`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260521-160619_post_wave698_cdxtexture_png_decode_option_tail_verified`.

Exact PNG decode-state layout, info-state layout, option enum, PLTE/tRNS record layout, gamma/sRGB policy, read callback ABI, buffered-read state layout, source-stream behavior, PNG signature acceptance policy, runtime PNG behavior, runtime image fidelity, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave698 CDXTexture PNG decode-option tail`, `cdxtexture-png-decode-option-tail-wave698`, `0x00594ef8 CDXTexture__SetDecodeOptionFloat`, `0x005950e0 CDXTexture__ComparePngSignatureBytes`, `0x0059512b CDXTexture__AllocZeroedDecodeBuffer`.

## Wave697 CDXTexture PNG Row-Transform Tail Read-Back Note

Wave697 CDXTexture PNG row-transform tail saved nine adjacent PNG row-transform and post-decode helper rows. Tag anchor: `cdxtexture-png-row-transform-tail-wave697`; the next queue head after this pass is `0x00594ef8 CDXTexture__SetDecodeOptionFloat`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x00593d0b` | `void __stdcall CDXTexture__PngStrip16BitSamplesTo8Bit(void * png_row_descriptor, void * row_buffer)` | If the row descriptor bit-depth byte at `+0x9` is 16, walks `width * channel-count` 16-bit samples, copies each high byte into the 8-bit row lane, then updates bit depth, bits-per-pixel, and row byte count. |
| `0x00593d51` | `void __stdcall CDXTexture__PngInsertFillerChannel(void * png_row_descriptor, void * row_buffer, uint filler_sample_value, uint layout_flags)` | Inserts a filler sample into grayscale or RGB rows for 8-bit and 16-bit sample widths; `filler_sample_value` supplies sample bytes and `layout_flags` bit `0x80` selects before-color versus after-color placement. |
| `0x00593f8a` | `void __stdcall CDXTexture__PngApplyRowTransformLuts(void * png_row_descriptor, void * row_buffer, int byte_lut_table, void * word_lut_table, int word_lut_index_shift)` | Applies byte and 16-bit LUT tables across low-bit, 8-bit, and 16-bit grayscale/RGB/alpha row forms, using the observed word-table index shift for 16-bit samples. |
| `0x005942da` | `void __stdcall CDXTexture__ExpandIndexedRowToRgbOrRgba(void * png_row_descriptor, void * row_buffer, void * palette_rgb_table, void * palette_alpha_table, int palette_alpha_count)` | For indexed-color rows, expands packed indices when needed and rewrites palette indices into RGB or RGBA bytes using PLTE data plus optional transparency alpha data. |
| `0x005944e3` | `void __stdcall CDXTexture__PngExpandTransparentColorToAlpha(void * png_row_descriptor, void * row_buffer, void * transparent_color_record)` | Expands grayscale/RGB rows to gray+alpha or RGB+alpha output by comparing pixels against the transparent-color record for 8-bit and 16-bit sample widths. |
| `0x00594836` | `void __stdcall CDXTexture__PngConvertRgbRowsToPaletteIndices(void * png_row_descriptor, void * row_buffer, void * rgb_to_palette_lut, void * index_remap_lut)` | Converts RGB/RGBA 8-bit rows to indexed rows through an RGB-to-palette lookup and remaps already-indexed rows through an index LUT when provided. |
| `0x00594945` | `void __stdcall CDXTexture__BuildPngGammaAndExpandTables(void * png_decode_state)` | Builds PNG gamma or significant-bit expand LUT storage when needed, allocating byte or word tables and storing the observed word-LUT shift at `+0x12c`. |
| `0x00594c48` | `void __stdcall CDXTexture__ApplyPngPostDecodeTransforms(void * png_decode_state)` | Builds gamma/expand tables when needed, applies palette gamma adjustment, and shifts PLTE RGB entries according to significant-bit state. |
| `0x00594d5c` | `void __stdcall CDXTexture__ApplyPngRowTransforms(void * png_decode_state)` | Dispatches PNG row transforms from the decode state: palette expansion, transparency alpha, gamma LUTs, strip-16, RGB-to-palette, significant-bit shifts, packed expansion, RGB/BGR swap, filler insertion, and 16-bit byte swap. |

Wave697 read-back evidence verified `9` metadata rows, `9` tag rows, `9` xref rows, `333` instruction rows, and `9` clean decompile rows. Candidate exports covered `17` adjacent PNG row-transform and decode-option rows through `0x005950e0 CDXTexture__ComparePngSignatureBytes`. The pass hardened `9` signatures, made no renames, made no function-boundary changes, and made no executable-byte changes. Post-Wave697 queue telemetry is `6098` total, `4008` commented, `2090` commentless, `1216` exact-undefined signatures, `318` `param_N`, strict clean-signature proxy `3952/6098 = 64.81%`, and next head `0x00594ef8 CDXTexture__SetDecodeOptionFloat`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260521-154041_post_wave697_cdxtexture_png_row_transform_tail_verified`.

Exact PNG decode-state layout, row descriptor layout, transform-option enum, color-type enum, palette/tRNS table layout, filler-channel enum, gamma/color-management policy, RGB key packing, transform order, row callback ABI, runtime PNG transform behavior, runtime image fidelity, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave697 CDXTexture PNG row-transform tail`, `cdxtexture-png-row-transform-tail-wave697`, `0x00593d0b CDXTexture__PngStrip16BitSamplesTo8Bit`, `0x00594d5c CDXTexture__ApplyPngRowTransforms`, `0x00594ef8 CDXTexture__SetDecodeOptionFloat`.

## Wave696 CDXTexture PNG Transform Head Read-Back Note

Wave696 CDXTexture PNG transform head saved eight adjacent PNG transform-option and row-transform helper rows. Tag anchor: `cdxtexture-png-transform-head-wave696`; the next queue head after this pass is `0x00593d0b CDXTexture__PngStrip16BitSamplesTo8Bit`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x00593812` | `void __stdcall CDXTexture__ConfigureFillerChannel(void * png_decode_state, int filler_sample_value, int place_filler_after_color)` | Sets the PNG transform option byte at `+0x61` bit `0x80`, stores the low-byte filler sample at `+0x11e`, toggles layout flag `+0x5c` bit `0x80`, and adjusts observed output channel metadata for palette/color-type and bit-depth combinations. |
| `0x00593861` | `void __stdcall CDXTexture__Swap16BitSampleByteOrder(void * png_row_descriptor, void * row_buffer)` | When the row descriptor bit-depth byte at `+0x9` is 16, walks `width * channel-count` 16-bit samples and swaps the two bytes of each sample in place. |
| `0x00593890` | `void __stdcall CDXTexture__SwapRgbBgrChannelOrder(void * png_row_descriptor, void * row_buffer)` | For RGB/RGBA row descriptors, swaps red and blue lanes in place across 8-bit and 16-bit rows, using 3/4 byte strides for 8-bit rows and 6/8 byte strides for 16-bit rows. |
| `0x00593951` | `void __stdcall CDXTexture__SetGammaCorrectionParams(void * png_decode_state, double file_gamma, double display_gamma)` | Compares `file_gamma * display_gamma` against the observed default tolerance, sets transform option bit `0x20` when correction is needed, and stores the two gamma inputs as floats at `+0x130/+0x134`. |
| `0x00593989` | `void __stdcall CDXTexture__EnablePaletteExpansion(void * png_decode_state)` | Sets PNG transform option bit `0x10` at decode-state `+0x61`, enabling the nearby palette expansion/layout path. |
| `0x00593994` | `void __stdcall CDXTexture__ApplyPngPostprocessLayoutFlags(void * png_decode_state, void * png_info_state)` | Applies transform option/layout flags to PNG info metadata, including palette expansion, gamma propagation, 16-bit strip-to-8-bit layout, RGB-to-palette fallback, packed-sample expansion, channel-count derivation, bits-per-pixel calculation, and row-stride update. |
| `0x00593a81` | `void __stdcall CDXTexture__PngExpandPackedSamplesTo8Bit(void * png_row_descriptor, void * row_buffer)` | Expands packed 1/2/4-bit samples into one byte per sample from the end of the row, then updates bit depth to 8, bits-per-pixel to channel-count * 8, and row byte count to width * channel-count. |
| `0x00593b92` | `int __stdcall CDXTexture__PngShiftPackedSamplesBySigBits(void * png_row_descriptor, void * row_buffer, void * significant_bits_table)` | Derives per-channel right-shift counts from row bit depth and the significant-bits table, clamps non-positive shifts to zero, and applies in-place shifts for 2/4/8/16-bit sample forms across grayscale, RGB, and alpha-bearing rows. |

Wave696 read-back evidence verified `8` metadata rows, `8` tag rows, `9` xref rows, `296` instruction rows, and `8` clean decompile rows. Candidate exports covered `17` adjacent PNG transform rows through `0x00594d5c CDXTexture__ApplyPngRowTransforms`. The pass hardened `8` signatures, made no renames, made no function-boundary changes, and made no executable-byte changes. Post-Wave696 queue telemetry is `6098` total, `3999` commented, `2099` commentless, `1216` exact-undefined signatures, `327` `param_N`, strict clean-signature proxy `3943/6098 = 64.66%`, and next head `0x00593d0b CDXTexture__PngStrip16BitSamplesTo8Bit`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260521-151249_post_wave696_cdxtexture_png_transform_head_verified`.

Exact PNG decode-state layout, row descriptor layout, transform-option enum, color-type enum, filler-channel enum, significant-bits table layout, gamma/color-management policy, packed-sample ordering, row callback ABI, runtime PNG transform behavior, runtime image fidelity, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave696 CDXTexture PNG transform head`, `cdxtexture-png-transform-head-wave696`, `0x00593812 CDXTexture__ConfigureFillerChannel`, `0x00593b92 CDXTexture__PngShiftPackedSamplesBySigBits`, `0x00593d0b CDXTexture__PngStrip16BitSamplesTo8Bit`.

## Wave695 CDXTexture PNG Option Accessors Read-Back Note

Wave695 CDXTexture PNG option accessors saved twelve adjacent PNG cleanup, option-info, and transform-flag helper rows. Tag anchor: `cdxtexture-png-option-accessors-wave695`; the next queue head after this pass is `0x00593812 CDXTexture__ConfigureFillerChannel`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x00593526` | `void __stdcall CDXTexture__ReleasePngDecodeContextHandles(void * png_decode_context_slot, void * primary_row_workspace_slot, void * secondary_row_workspace_slot)` | Reads the PNG context and optional row-workspace slots, calls `CDXTexture__ResetPngDecodeContext` for a live context, frees non-null row workspaces, frees the decode context, and clears each owned slot. |
| `0x005935a3` | `uint __stdcall CDXTexture__TestDecodeOptionFlagMask(void * png_decode_state, void * png_info_state, uint flag_mask)` | Null-checks decode/info states and returns `info_state +0x8` masked by the requested valid-option flag. |
| `0x005935c0` | `int __stdcall CDXTexture__GetDecodeRowStride(void * png_decode_state, void * png_info_state)` | Null-checks decode/info states and returns the row-stride field at `info_state +0xc`. |
| `0x005935d9` | `int __stdcall CDXTexture__GetOutputChannelCount(void * png_decode_state, void * png_info_state)` | Null-checks decode/info states and returns the observed one-byte channel-count field at `info_state +0x1d`. |
| `0x005935f2` | `int __stdcall CDXTexture__GetOutputGamma(void * png_decode_state, void * png_info_state, double * out_gamma)` | Requires valid-option bit `0x1`, widens the float at `info_state +0x28` to an output double, and returns success. |
| `0x0059361e` | `int __stdcall CDXTexture__GetRenderingIntent(void * png_decode_state, void * png_info_state, int * out_rendering_intent)` | Requires valid-option bit `0x800`, writes the rendering-intent byte from `info_state +0x2c`, and returns `0x800`. |
| `0x0059371d` | `int __stdcall CDXTexture__GetPaletteBufferInfo(void * png_decode_state, void * png_info_state, void * out_palette_buffer, int * out_palette_count)` | Requires valid-option bit `0x8`, returns the palette pointer at `info_state +0x10`, writes the 16-bit palette count from `+0x14`, and returns `0x8`. |
| `0x00593753` | `int __stdcall CDXTexture__GetTransparencyInfo(void * png_decode_state, void * png_info_state, void * out_transparency_table, int * out_transparency_count, void * out_transparent_color)` | Requires valid-option bit `0x10`, branches on color type byte `+0x19`, returns the palette alpha table at `+0x30` for indexed color, returns the transparent-color record at `+0x34` when requested, and writes the 16-bit transparency count from `+0x16`. |
| `0x005937bc` | `void __stdcall CDXTexture__EnableByteSwapTransform(void * png_decode_state)` | Sets transform flag bit `0x1` at `png_decode_state +0x60`. |
| `0x005937c7` | `void __stdcall CDXTexture__EnableSwap16TransformIfNeeded(void * png_decode_state)` | Checks the observed bit-depth byte at `png_decode_state +0x117` and sets transform flag bit `0x10` only when the value is 16. |
| `0x005937db` | `void __stdcall CDXTexture__EnableExpandTo8Bit(void * png_decode_state)` | When observed bit depth is below 8, sets transform flag bit `0x4` and raises the output bit-depth byte at `+0x118` to 8. |
| `0x005937f6` | `int __stdcall CDXTexture__GetPngPassCountFromInterlace(void * png_decode_state)` | Returns one pass for non-interlaced PNG state; otherwise sets transform flag bit `0x2` and returns seven passes for the Adam7 path. |

Wave695 read-back evidence verified `12` metadata rows, `12` tag rows, `14` xref rows, `444` instruction rows, and `12` clean decompile rows. Candidate exports covered `20` adjacent PNG option/transform rows through `0x00593b92 CDXTexture__PngShiftPackedSamplesBySigBits`. The pass hardened `12` signatures, made no renames, made no function-boundary changes, and made no executable-byte changes. Post-Wave695 queue telemetry is `6098` total, `3991` commented, `2107` commentless, `1216` exact-undefined signatures, `335` `param_N`, strict clean-signature proxy `3941/6098 = 64.63%`, and next head `0x00593812 CDXTexture__ConfigureFillerChannel`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260521-150000_post_wave695_cdxtexture_png_option_accessors_verified`.

Exact PNG info-state layout, slot ownership, output pointer nullability contracts, palette/tRNS/gamma/sRGB enum identity, transform-flag enum, bit-depth/interlace fields, runtime PNG option behavior, runtime image fidelity, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave695 CDXTexture PNG option accessors`, `cdxtexture-png-option-accessors-wave695`, `0x00593526 CDXTexture__ReleasePngDecodeContextHandles`, `0x005937f6 CDXTexture__GetPngPassCountFromInterlace`, `0x00593812 CDXTexture__ConfigureFillerChannel`.

## Wave694 CDXTexture PNG Decode Context Read-Back Note

Wave694 CDXTexture PNG decode context saved six adjacent PNG decode-context rows. Tag anchor: `cdxtexture-png-decode-context-wave694`; the next queue head after this pass is `0x00593526 CDXTexture__ReleasePngDecodeContextHandles`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x00592dc2` | `void * __stdcall CDXTexture__CreatePngDecodeContext(void * png_version_string, void * callback_context, void * error_callback, void * warning_callback)` | Allocates and zeroes the PNG decode context, installs callback slots, allocates the observed `0x2000` zlib input buffer at `+0x9c`, seeds zlib allocator callbacks, initializes inflate with windowbits 15/version literal `1.1.4`, maps setup failures to decode errors, and seeds read-buffer fields at `+0x70/+0x74`. |
| `0x00592eb6` | `void __stdcall CDXTexture__ParsePngHeadersUntilIdat(void * png_decode_state, void * png_image_context)` | Reads and validates the PNG signature, distinguishes non-PNG/ASCII-converted signatures, loops through chunk length/type reads with CRC setup, dispatches observed IHDR/PLTE/tRNS/gAMA/sRGB handlers before IDAT, verifies header/palette ordering, records first IDAT byte count at `+0xfc`, and marks header/IDAT flags. |
| `0x00593024` | `void __stdcall CDXTexture__PreparePngRowOutputLayout(void * png_decode_state, void * png_image_context)` | Initializes PNG image buffers/pass geometry when flag `+0x5c` bit `0x40` is clear, then applies postprocess/output layout flags. |
| `0x00593043` | `void __stdcall CDXTexture__DecodePngPassRowsAndPostprocess(void * png_decode_state, void * previous_row_workspace, void * current_row_workspace)` | Decodes one PNG row/pass: handles Adam7/packed-pixel pre-expansion masks, reads IDAT chunks and CRCs, feeds zlib, applies PNG scanline filter and row transforms, expands packed pixels into optional workspaces, queues row postprocess work, and invokes optional row callback `+0x16c`. |
| `0x005933c6` | `void __stdcall CDXTexture__DecodePngRowsAcrossPasses(void * png_decode_state, int * row_workspace_pointer_table)` | Queries interlace pass count, resets the observed row counter from image height, and dispatches each row workspace pointer to the row decoder with a null secondary workspace. |
| `0x00593411` | `void __stdcall CDXTexture__ResetPngDecodeContext(void * png_decode_state, void * primary_row_workspace, void * secondary_row_workspace)` | Clears optional row workspaces, frees observed owned decode buffers/tables, finishes the async/zlib decode job rooted at `+0x64`, preserves the initial header/callback triplet, zeroes the larger decode-context body, and restores preserved fields. |

Wave694 read-back evidence verified `6` metadata rows, `6` tag rows, `6` xref rows, `630` instruction rows, and `6` clean decompile rows. Candidate exports covered `18` adjacent PNG decode rows through `0x005937f6 CDXTexture__GetPngPassCountFromInterlace`. The pass hardened `6` signatures, made no renames, made no function-boundary changes, and made no executable-byte changes. Post-Wave694 queue telemetry is `6098` total, `3979` commented, `2119` commentless, `1216` exact-undefined signatures, `347` `param_N`, strict clean-signature proxy `3929/6098 = 64.43%`, and next head `0x00593526 CDXTexture__ReleasePngDecodeContextHandles`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260521-142452_post_wave694_cdxtexture_png_decode_context_verified`.

Exact PNG decode-state layout, callback prototypes, zlib allocator ABI, image-context layout, chunk flag enum, CRC contract, pass-geometry contract, row-workspace ownership, Adam7 table semantics, zlib stream layout, row callback ABI, ownership bits, cleanup ABI, runtime PNG behavior, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave694 CDXTexture PNG decode context`, `cdxtexture-png-decode-context-wave694`, `0x00592dc2 CDXTexture__CreatePngDecodeContext`, `0x00593411 CDXTexture__ResetPngDecodeContext`, `0x00593526 CDXTexture__ReleasePngDecodeContextHandles`.

## Wave693 CDXTexture Parser-Context Diagnostics Read-Back Note

Wave693 CDXTexture parser-context diagnostics saved six CDXTexture/CTexture-labelled rows plus two CFastVB parser-context rows documented in [`FastVB.cpp`](../FastVB.cpp/_index.md). Tag anchor: `cdxtexture-parser-context-diagnostics-wave693`; the next queue head after this pass is `0x00592dc2 CDXTexture__CreatePngDecodeContext`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x00592ca0` | `void __thiscall CDXTexture__FormatChunkTagForDiagnostics(void * this, int param_1, int param_2, void * param_3)` | Comment/tag-only row because Ghidra's thiscall shape exposes the output buffer as `this`. Formats the current PNG chunk tag from decode-state `+0x10c`, copies printable bytes directly, expands non-printable bytes as bracketed uppercase hex nibbles, and appends optional message text. |
| `0x00592d29` | `void __stdcall CTexture__SetDecodeContextTriplet(void * decode_context, void * callback_context, void * error_callback, void * warning_callback)` | Stores the decode-context callback triplet: callback context at `+0x48`, error callback at `+0x40`, and warning callback at `+0x44`. |
| `0x00592d45` | `void __stdcall CDXTexture__ThrowDecodeError(void * decode_context, int message_or_code)` | Invokes the decode-context error callback when present, then transfers through `_longjmp(decode_context, 1)`. |
| `0x00592d63` | `void __stdcall CDXTexture__ReportDecodeWarning(void * decode_context, int message_or_code)` | Invokes the decode-context warning callback when present and returns without a longjmp transfer. |
| `0x00592d7a` | `void __stdcall CDXTexture__LogChunkTagDiagnostic(void * png_decode_state, void * optional_message_text)` | Builds a stack diagnostic string through `CDXTexture__FormatChunkTagForDiagnostics` and routes it through `CDXTexture__ThrowDecodeError`. |
| `0x00592d9e` | `void __stdcall CDXTexture__WarnPngChunkWithFormattedTag(void * png_decode_state, void * optional_message_text)` | Builds a stack diagnostic string through `CDXTexture__FormatChunkTagForDiagnostics` and routes it through `CDXTexture__ReportDecodeWarning`. |

Wave693 read-back evidence verified `8` metadata rows, `8` tag rows, `65` xref rows, `296` instruction rows, and `8` clean decompile rows across `0x00592b00 CFastVB__ParserContext_Shutdown` through `0x00592d9e CDXTexture__WarnPngChunkWithFormattedTag`. Candidate exports covered `14` adjacent parser-context/diagnostic/PNG decode rows before the final eight-row tranche was selected. The pass hardened `7` signatures, left `0x00592ca0` comment/tag-only, made no renames, made no function-boundary changes, and made no executable-byte changes. Post-Wave693 queue telemetry is `6098` total, `3973` commented, `2125` commentless, `1216` exact-undefined signatures, `353` `param_N`, strict clean-signature proxy `3923/6098 = 64.33%`, and next head `0x00592dc2 CDXTexture__CreatePngDecodeContext`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260521-135916_post_wave693_cdxtexture_parser_context_diagnostics_verified`.

Exact parser-context layout, callback-table ABI, diagnostic table ownership, output-buffer capacity, PNG chunk-state layout, callback prototypes, payload type, non-return contract, runtime PNG/JPEG decode fidelity, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave693 CDXTexture parser-context diagnostics`, `cdxtexture-parser-context-diagnostics-wave693`, `0x00592b00 CFastVB__ParserContext_Shutdown`, `0x00592d9e CDXTexture__WarnPngChunkWithFormattedTag`, `0x00592dc2 CDXTexture__CreatePngDecodeContext`.

## Wave692 CDXTexture JPEG Marker Reader Read-Back Note

Wave692 CDXTexture JPEG marker reader saved six adjacent JPEG marker-reader rows. Tag anchor: `cdxtexture-jpeg-marker-reader-wave692`; the next queue head after this pass was `0x00592b00 CFastVB__ParserContext_Shutdown`, later hardened by Wave693.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x00592380` | `int __stdcall CTexture__ReadJpegSegmentLengthAndEmitMarker(void * jpeg_decode_state)` | Reads the two-byte JPEG segment length through the buffered input source at `+0x18`, refills through callback `+0x0c` when needed, stores diagnostic id `0x5b` plus marker/length context through the error callback record, records the length minus the two length bytes, optionally skips remaining bytes through callback `+0x10`, and returns decoder status. |
| `0x00592420` | `int __stdcall CTexture__SkipJpegFillBytesAndReadMarker(void * jpeg_decode_state)` | Scans the buffered JPEG input stream until a marker prefix is found, skips non-marker bytes and stuffed `0xff/0x00` fill sequences while accumulating skipped-byte count at marker-reader `+0x18`, emits diagnostic id `0x74` when bytes were skipped, writes the current marker byte to decode-state `+0x1a4`, and returns decoder status. |
| `0x00592530` | `int __stdcall CFastVB__JpegParser_ReadAndValidateSOI(void * jpeg_decode_state)` | Reads the first two buffered JPEG bytes, refills through callback `+0x0c` when needed, validates the SOI marker bytes `0xff/0xd8`, emits diagnostic id `0x35` with the observed bytes on mismatch, advances the buffer cursor, records the marker byte at decode-state `+0x1a4`, and returns decoder status. |
| `0x005928d0` | `int __stdcall CDXTexture__ConsumeExpectedRestartMarker(void * jpeg_decode_state)` | Consumes or fetches the current JPEG marker, compares it with the expected restart marker computed from marker-reader `+0x14` plus `0xd0`, emits diagnostic id `0x62` for the matched restart marker, clears decode-state `+0x1a4` after a match, falls back to the marker-reader `+0x14` resync callback when mismatched, advances the expected restart index modulo eight, and returns decoder status. |
| `0x00592950` | `int __stdcall CDXTexture__ClassifyRestartMarkerResync(void * jpeg_decode_state, int expected_restart_index)` | Logs diagnostic id `0x79` for a restart-marker resync attempt, classifies the current marker relative to the expected restart index into observed result classes `1`/`2`/`3`, emits diagnostic id `0x61` with the marker and class, clears decode-state `+0x1a4` for class `1`, loops through `CTexture__SkipJpegFillBytesAndReadMarker` for class `2`, and returns decoder status for class `3`. |
| `0x00592a80` | `void __stdcall CDXTexture__InitJpegMarkerReader(void * jpeg_decode_state)` | Allocates the observed `0xac`-byte marker-reader context through the decode-state allocator at `+0x04`, stores it at decode-state `+0x1bc`, seeds callback slots for reset, frame/SOI handling, restart consumption, segment-length readers, and APP parser defaults, clears sixteen segment callback counters, installs default APP handlers at slots `+0x20/+0x58`, and clears decode-state marker fields at `+0xdc/+0x94/+0x1a4`. |

Wave692 read-back evidence verified `6` metadata rows, `6` tag rows, `10` xref rows, `222` instruction rows, and `6` clean decompile rows. Candidate exports covered `14` adjacent marker-reader/parser-context/diagnostic rows before the final six-row tranche was selected. The pass hardened `6` signatures, made no renames, made no function-boundary changes, and made no executable-byte changes. Post-Wave692 queue telemetry is `6098` total, `3965` commented, `2133` commentless, `1216` exact-undefined signatures, `360` `param_N`, strict clean-signature proxy `3915/6098 = 64.20%`, and next head `0x00592b00 CFastVB__ParserContext_Shutdown`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260521-132823_post_wave692_cdxtexture_jpeg_marker_reader_verified`.

Exact marker-reader object layout, segment-length contract, callback ABI, SOI precondition contract, restart recovery policy, resync-class enum, callback-table ABI, APP slot ownership, runtime decode fidelity, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave692 CDXTexture JPEG marker reader`, `cdxtexture-jpeg-marker-reader-wave692`, `0x00592380 CTexture__ReadJpegSegmentLengthAndEmitMarker`, `0x00592a80 CDXTexture__InitJpegMarkerReader`, `0x00592b00 CFastVB__ParserContext_Shutdown`.

## Wave691 CDXTexture JPEG Segment Parsers Read-Back Note

Wave691 CDXTexture JPEG segment parsers saved six adjacent JPEG segment parser rows. Tag anchor: `cdxtexture-jpeg-segment-parsers-wave691`; the next queue head after this pass is `0x00592380 CTexture__ReadJpegSegmentLengthAndEmitMarker`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x00591460` | `int __fastcall CDXTexture__DecodeJpegSegment_StartOfFrame(int param_1)` | Comment/tag-only row because Ghidra exposes register-context inputs around the fastcall parameter. Parses a JPEG start-of-frame segment, records marker/context fields into the decode state, reads precision, image dimensions, component count, component ids, sampling factors, and quant-table selectors, and emits observed diagnostics `0x3a`/`0x20`/`0x0b`/`0x65`. |
| `0x005919e0` | `int CDXTexture__DecodeJpegSegment_HuffmanTables(void)` | Comment/tag-only row because Ghidra reports unknown calling convention with locked parameter storage. Parses a DHT/Huffman-table segment, reads table class/id, sixteen code-length counts, symbol budget, descriptor allocation, and code/symbol byte copy. |
| `0x00591cb0` | `int __stdcall CDXTexture__DecodeJpegSegment_QuantizationTables(void * jpeg_decode_state)` | Parses a DQT/quantization-table segment, reads table id/precision, allocates a descriptor when missing, fills 64 coefficients through `DAT_005f37f8`, supports 8-bit and 16-bit coefficient forms, and emits observed diagnostics. |
| `0x00591ef0` | `int __stdcall CDXTexture__DecodeJpegSegment_RestartInterval(void * jpeg_decode_state)` | Parses a DRI/restart-interval segment, requires the observed length field to equal `4`, reads the restart interval value, stores it at the observed `+0x118` slot, and reports malformed length through diagnostic `0x0b`. |
| `0x00591fc0` | `void __fastcall CDXTexture__ParseJfifApp0Header(int param_1)` | Comment/tag-only row because Ghidra exposes payload length/start through register context around the fastcall parameter. Parses APP0 JFIF/JFXX header fields, including signature, version, density units, x/y density, thumbnail dimensions, and related diagnostics. |
| `0x005921a0` | `void __thiscall CDXTexture__ParseAdobeApp14Header(void * this, uint param_1, int param_2)` | Comment/tag-only row because Ghidra's thiscall shape treats a length as `this` and leaves the register-held payload pointer outside formal parameters. Parses APP14 Adobe signature, version/flags/transform diagnostics, stores the transform byte at the observed `+0x12c` slot, and sets the APP14-present flag at `+0x128`. |

Wave691 read-back evidence verified `6` metadata rows, `6` tag rows, `7` xref rows, `546` instruction rows, and `6` clean decompile rows. Candidate exports covered `12` adjacent JPEG segment/marker rows before the final six-row tranche was selected. The pass hardened `2` signatures, left `4` register-context/locked-storage rows comment/tag-only, made no renames, made no function-boundary changes, and made no executable-byte changes. Post-Wave691 queue telemetry is `6098` total, `3959` commented, `2139` commentless, `1216` exact-undefined signatures, `366` `param_N`, strict clean-signature proxy `3909/6098 = 64.10%`, and next head `0x00592380 CTexture__ReadJpegSegmentLengthAndEmitMarker`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260521-130107_post_wave691_cdxtexture_jpeg_segment_parsers_verified`.

Exact SOF marker enum, frame-header/component descriptor layout, Huffman descriptor layout, quant descriptor layout, restart-marker behavior, APP0 offset contract, APP14 offset contract, color-transform policy, runtime decode fidelity, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave691 CDXTexture JPEG segment parsers`, `cdxtexture-jpeg-segment-parsers-wave691`, `0x00591460 CDXTexture__DecodeJpegSegment_StartOfFrame`, `0x005921a0 CDXTexture__ParseAdobeApp14Header`, `0x00592380 CTexture__ReadJpegSegmentLengthAndEmitMarker`.

## Wave690 CDXTexture JPEG Decode Head Read-Back Note

Wave690 CDXTexture JPEG decode head saved eight adjacent JPEG decode setup, input-buffer, controller, state-machine, cleanup, output-default, pump, and finalize rows. Tag anchor: `cdxtexture-jpeg-decode-head-wave690`; the next queue head after this pass is `0x00591460 CDXTexture__DecodeJpegSegment_StartOfFrame`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x00590e10` | `int __stdcall CDXTexture__FillInputBufferFromSource(void * jpeg_decode_state, void * destination_buffer, int requested_byte_count)` | Validates input state/source bounds, reports exhausted-source or state mismatches through the decoder error callback, invokes the source read callback at `+0x1ac`, and advances the consumed-byte cursor. |
| `0x00590ea0` | `int __stdcall CDXTexture__ProcessInputControllerState(void * jpeg_decode_state)` | Handles `0xca`/`0xcb`/`0xcc` progression, creates decode dispatch context when needed, pumps input-controller callbacks, updates progress counters, and drains parser work. |
| `0x00590f80` | `void __stdcall CDXTexture__InitJpegDecodeState(void * jpeg_decode_state, int expected_header_size, int expected_context_size)` | Checks observed `0x3e`/`0x1d8` setup constants, clears the decode-state block while preserving saved header slots, initializes allocator/marker reader/callback context, and starts state `0xc8`. |
| `0x00591050` | `void __stdcall CFastVB__ReleaseOwnedObjectAndReset(void * decode_state_header)` | Releases an owned object through vtable slot `+0x28` when present, then clears the owner pointer and stage/status field. |
| `0x00591060` | `void CDXTexture__SelectJpegOutputDefaults(void)` | Comment/tag-only row because Ghidra records locked ESI register-context storage; selects output color/component defaults and reports unsupported combinations with observed error ids `0x6f`/`0x72`. |
| `0x005911d0` | `int __stdcall CDXTexture__AdvanceJpegDecodeState(void * jpeg_decode_state)` | Advances the JPEG state machine, primes marker/input callbacks, invokes output-default selection when the marker controller reports ready, and reports unexpected states. |
| `0x00591280` | `int __stdcall CDXTexture__DecodeJpegStream_PumpUntilReady(void * jpeg_decode_state)` | Handles `0xcd`/`0xce`/`0xcf`/`0xd2` stream states, reports short-source conditions, invokes stream finalization, pumps the marker controller until output is ready, then advances allocator/stage setup. |
| `0x00591340` | `int __stdcall CDXTexture__PumpDecoderStreamAndFinalize(void * jpeg_decode_state, int require_end_of_image)` | Validates initial state, advances the decode state machine, optionally reports strict end-of-image error `0x33`, pumps allocator/stage setup, and returns decoder status. |

Wave690 read-back evidence verified `8` metadata rows, `8` tag rows, `10` xref rows, `728` instruction rows, and `8` clean decompile rows. Candidate exports covered `13` adjacent JPEG setup/segment rows before the final eight-row tranche was selected. The pass hardened `7` signatures, left `0x00591060` comment/tag-only, made no renames, made no function-boundary changes, and made no executable-byte changes. Post-Wave690 queue telemetry is `6098` total, `3953` commented, `2145` commentless, `1216` exact-undefined signatures, `368` `param_N`, strict clean-signature proxy `3903/6098 = 64.00%`, and next head `0x00591460 CDXTexture__DecodeJpegSegment_StartOfFrame`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260521-123207_post_wave690_cdxtexture_jpeg_decode_head_verified`.

Exact JPEG source-manager ABI, decode-state layout, state enum, marker-controller ABI, output color enum, ESI helper signature/storage, segment-parser semantics, runtime decode fidelity, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave690 CDXTexture JPEG decode head`, `cdxtexture-jpeg-decode-head-wave690`, `0x00590e10 CDXTexture__FillInputBufferFromSource`, `0x00591340 CDXTexture__PumpDecoderStreamAndFinalize`, `0x00591460 CDXTexture__DecodeJpegSegment_StartOfFrame`.

## Wave679 CDXTexture Catch Bridge Read-Back Note

Wave679 CDXTexture catch bridge saved the compiler catch landing pad and adjacent Ghidra-split CPU SIMD flag continuation. Tag anchor: `cdxtexture-catch-bridge-wave679`; the next queue head after this pass is `0x00589367 CTexture__ReleaseIncludeNodeTreeRecursive`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x00589200` | `void * __cdecl Catch@00589200(void)` | Compiler catch/unwind landing pad for the adjacent CDXTexture CPU-feature path; copies local flag state from `EBP-0x14` to `EBP-0x3c`, returns continuation address `0x00589212`, and is reached only by EH table data xref `0x006202fc` in current read-back. |
| `0x0058920c` | `int CDXTexture__DetectCpuSimdFlags(void)` | Signature preserved because Ghidra still warns on the split continuation. It is reached from `CDXTexture__InitCpuVendorAndSimdFlags` at `0x005891fe`, checks CPUID availability, reads CPUID leaf 1, ORs observed EDX feature bits `0x02000000` and `0x04000000` into local flags `0x4` and `0x8`, restores `ExceptionList`, and returns the flag word. |

Wave679 read-back evidence verified `2` metadata rows, `2` tag rows, `2` xref rows, `98` instruction rows, and `2` clean decompile rows. Context exports verified `4` metadata rows, `4` tag rows, `64` xref rows, `244` instruction rows, and `4` clean decompile rows across `0x005890f1`, `0x00589200`, `0x0058920c`, and `0x0058926b`. Post-Wave679 queue telemetry is `6098` total, `3841` commented, `2257` commentless, `1216` exact-undefined signatures, `478` `param_N`, strict clean-signature proxy `3791/6098 = 62.17%`, and next head `0x00589367 CTexture__ReleaseIncludeNodeTreeRecursive`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260521-073516_post_wave679_cdxtexture_catch_bridge_verified`.

Exact MSVC EH model, exception-table layout, split-boundary ownership, feature-bit names, OS feature gating, runtime exception behavior, runtime dispatch policy, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave679 CDXTexture catch bridge`, `cdxtexture-catch-bridge-wave679`, `0x00589200 Catch@00589200`, `0x0058920c CDXTexture__DetectCpuSimdFlags`, `0x00589367 CTexture__ReleaseIncludeNodeTreeRecursive`.

## Wave678 CDXTexture Dispatch Prelude Read-Back Note

Wave678 CDXTexture dispatch prelude saved three CDXTexture-labelled vector/registry/CPUID helpers plus one CFastVB dispatch-table initializer documented in [`FastVB.cpp`](../FastVB.cpp/_index.md). Tag anchor: `cdxtexture-dispatch-prelude-wave678`; the next queue head after this pass was `0x00589200 Catch@00589200`, later hardened by Wave679.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x00588cc6` | `void __stdcall CDXTexture__ProjectPointToPlaneAndScale(float * source_point, float * plane_point, float * plane_normal, float scale, float * out_point)` | Copies `source_point` to `out_point`, subtracts `plane_point`, removes the `plane_normal` dot component, scales the tangent vector, and adds `plane_point` back. |
| `0x00589094` | `int __stdcall CDXTexture__RegistryValueEqualsDword(int expected_registry_type, void * value_name, void * out_value_buffer, int value_byte_count)` | Opens `HKLM\Software\Microsoft\Direct3D`, queries `value_name`, and returns true when `RegQueryValueExA` succeeds and the reported registry type matches the expected type. |
| `0x005890f1` | `int __cdecl CDXTexture__CpuHasMmxFeature(void)` | Uses CPUID leaf 1 and tests EDX bit 23 before returning a nonzero MMX-support flag. |

Wave678 read-back evidence verified `4` metadata rows, `4` tag rows, `71` xref rows, `148` instruction rows, and `4` clean decompile rows across `0x00588cc6 CDXTexture__ProjectPointToPlaneAndScale` through `0x0058926b CFastVB__InitDispatchTableByCpuFeature`. Post-Wave678 queue telemetry is `6098` total, `3839` commented, `2259` commentless, `1217` exact-undefined signatures, `478` `param_N`, strict clean-signature proxy `3789/6098 = 62.14%`, and next head `0x00589200 Catch@00589200`, later hardened by Wave679. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260521-071055_post_wave678_cdxtexture_dispatch_prelude_verified`.

Exact vector storage, plane-normal assumptions, registry policy/caller buffer contract, runtime Direct3D override behavior, CPU dispatch policy, OS feature gating, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave678 CDXTexture dispatch prelude`, `cdxtexture-dispatch-prelude-wave678`, `0x00588cc6 CDXTexture__ProjectPointToPlaneAndScale`, `0x0058926b CFastVB__InitDispatchTableByCpuFeature`, `0x00589200 Catch@00589200`.

## Wave677 CDXTexture Mapped/GDI Read-Back Note

Wave677 CDXTexture mapped/GDI saved seven adjacent CDXTexture mapped-file context and GDI cleanup helpers. Tag anchor: `cdxtexture-mapped-gdi-wave677`; the next queue head after this pass is `0x00588cc6 CDXTexture__ProjectPointToPlaneAndScale`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x0058864a` | `void __fastcall CDXTexture__InitMappedFileContext(void * mapped_file_context)` | Initializes mapped-file handle sentinels to `INVALID_HANDLE_VALUE`, then clears the mapped view pointer and byte count. |
| `0x0058865c` | `int __thiscall CDXTexture__OpenMappedFileReadOnly(void * this, void * path_or_wide_path, int path_is_wide, int unused_context)` | Opens a path read-only through `CreateFileA/W`, creates a read-only mapping, records file size, and maps a non-empty view. |
| `0x0058877d` | `int __thiscall CDXTexture__OpenOutputFileHandle(void * this, void * path_or_wide_path, int path_is_wide, int unused_context)` | Opens a path for write output through `CreateFileA/W` after the same observed path-encoding branch and stores the handle. |
| `0x00588855` | `int __fastcall CDXTexture__CloseMappedFileContext(void * mapped_file_context)` | Unmaps the view, clears byte count, closes mapping/file handles when valid, restores handle sentinels, and returns zero. |
| `0x00588896` | `void __fastcall CDXTexture__CloseHandleIfValid(void * mapped_file_context)` | Checks the first handle sentinel and delegates to `CDXTexture__CloseMappedFileContext` when the context is open. |
| `0x005888a1` | `void __fastcall CDXTexture__ZeroGdiBitmapRecord(void * gdi_bitmap_record)` | Clears three dwords in a GDI-style bitmap record used by texture preprocessor include context setup. |
| `0x005888ae` | `void __fastcall CDXTexture__DeleteGdiObjectIfSet(void * gdi_object_slot)` | Calls `DeleteObject` on the first slot when non-null. |

Wave677 read-back evidence verified `7` metadata rows, `7` tag rows, `15` xref rows, `623` instruction rows, and `7` clean decompile rows. Post-Wave677 queue telemetry is `6098` total, `3835` commented, `2263` commentless, `1217` exact-undefined signatures, `482` `param_N`, strict clean-signature proxy `3785/6098 = 62.07%`, and next head `0x00588cc6 CDXTexture__ProjectPointToPlaneAndScale`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260521-064643_post_wave677_cdxtexture_mapped_gdi_verified`.

Exact mapped-file context layout, path encoding policy, output mode contract, GDI object ownership, runtime texture decode/export behavior, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave677 CDXTexture mapped/GDI`, `cdxtexture-mapped-gdi-wave677`, `0x0058864a CDXTexture__InitMappedFileContext`, `0x005888ae CDXTexture__DeleteGdiObjectIfSet`, `0x00588cc6 CDXTexture__ProjectPointToPlaneAndScale`.

## Wave674 Texel Unpack Tail Read-Back Note

Wave674 texel unpack tail saved four CDXTexture-labelled unpackers alongside CFastVB profile/unpacker rows in [`FastVB.cpp`](../FastVB.cpp/_index.md) and three CTexture rows in [`texture.cpp`](../texture.cpp/_index.md). Tag anchor: `texel-unpack-tail-wave674`; the next queue head after this pass is `0x005869b0 CTexture__UnpackTexels_Bits16_16_16_ToFloat4`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x005861b4` | `void __thiscall CDXTexture__UnpackTexels_Signed2_10_10_10_ToFloat4(void * this, uint source_x, uint source_y, float * destination_vec4_array, int unused_context)` | Signed 2-10-10-10 unpacker sign-extends/scales three 10-bit lanes and scales the top 2-bit lane into alpha. |
| `0x00586305` | `void __thiscall CDXTexture__UnpackTexels_Signed16_16_16_16_ToFloat4(void * this, uint source_x, uint source_y, float * destination_vec4_array, int unused_context)` | Signed 16-16-16-16 unpacker sign-scales four 16-bit lanes into RGBA. |
| `0x00586609` | `void __thiscall CDXTexture__UnpackTexels_CallbackPerTexel_Stride2_SetRGBAOne(void * this, uint source_x, uint source_y, float * destination_vec4_array, int unused_context)` | Callback-dispatch stride-2 unpacker advances two bytes per texel, calls the indirect unpack dispatcher, then forces G/B/A to `1.0`. |
| `0x0058677b` | `void __thiscall CDXTexture__UnpackTexels_CallbackSingleTexel(void * this, uint source_x, uint source_y, float * destination_vec4_array, int unused_context)` | Single-callback unpacker forwards one texel through the indirect unpack dispatcher and applies the same key-color/post-process gates. |

Wave674 read-back evidence verified `25` metadata rows, `25` tag rows, `25` xref rows, `1125` instruction rows, and `25` clean decompile rows across `0x0058609e CFastVB__TexelUnpackProfile_005ea020__ctor` through `0x00586994 CFastVB__InitTexelUnpackVTable_005ea118`. Post-Wave674 queue telemetry is `6098` total, `3796` commented, `2302` commentless, `1217` exact-undefined signatures, `521` `param_N`, strict clean-signature proxy `3746/6098 = 61.43%`, and next head `0x005869b0 CTexture__UnpackTexels_Bits16_16_16_ToFloat4`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260521-052857_post_wave674_texel_unpack_tail_verified`.

Exact profile ABI, signed-normal/alpha contract, callback-table contract, lane-order enum contract, runtime texture output behavior, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave674 texel unpack tail`, `texel-unpack-tail-wave674`, `0x0058609e CFastVB__TexelUnpackProfile_005ea020__ctor`, `0x00586994 CFastVB__InitTexelUnpackVTable_005ea118`, `0x005869b0 CTexture__UnpackTexels_Bits16_16_16_ToFloat4`.

## Wave673 Texel Unpack Continuation Read-Back Note

Wave673 texel unpack continuation saved two CDXTexture-labelled signed-normal unpackers alongside CFastVB profile/unpacker rows in [`FastVB.cpp`](../FastVB.cpp/_index.md) and three CTexture rows in [`texture.cpp`](../texture.cpp/_index.md). Tag anchor: `texel-unpack-continuation-wave673`; the next queue head after this pass is `0x0058609e CFastVB__TexelUnpackProfile_005ea020__ctor`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x00585da3` | `void __thiscall CDXTexture__UnpackTexels_Signed5_5_A6_ToFloat4(void * this, uint source_x, uint source_y, float * destination_vec4_array, int unused_context)` | Signed 5-5 plus A6 unpacker advances one 16-bit word per texel, sign-extends/scales the low and next 5-bit lanes into R/G, fills Z=`1.0`, and scales the high 6 bits into alpha. |
| `0x00585e9f` | `void __thiscall CDXTexture__UnpackTexels_Signed8_8_A8_ToFloat4_RG(void * this, uint source_x, uint source_y, float * destination_vec4_array, int unused_context)` | Signed 8-8 plus A8 RG unpacker advances four bytes per texel, sign-scales byte0/byte1 into R/G, fills Z=`1.0`, and scales byte2 into alpha while byte3 remains unused in the current decompile. |

Wave673 read-back evidence verified `25` metadata rows, `25` tag rows, `67` xref rows, `1125` instruction rows, and `25` clean decompile rows across `0x0058577f CFastVB__TexelUnpackProfile_005e9f3c__ctor` through `0x00585fa3 CFastVB__UnpackTexels_Signed8_8_8_8_ToFloat4`. Post-Wave673 queue telemetry is `6098` total, `3771` commented, `2327` commentless, `1217` exact-undefined signatures, `546` `param_N`, strict clean-signature proxy `3721/6098 = 61.02%`, and next head `0x0058609e CFastVB__TexelUnpackProfile_005ea020__ctor`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260521-045554_post_wave673_texel_unpack_continuation_verified`.

Exact profile ABI, signed-normal/alpha contract, source-record contract, lane-order enum contract, runtime texture output behavior, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave673 texel unpack continuation`, `texel-unpack-continuation-wave673`, `0x0058577f CFastVB__TexelUnpackProfile_005e9f3c__ctor`, `0x00585fa3 CFastVB__UnpackTexels_Signed8_8_8_8_ToFloat4`, `0x0058609e CFastVB__TexelUnpackProfile_005ea020__ctor`.

## Wave672 Texel Unpack Head Read-Back Note

Wave672 texel unpack head saved three CDXTexture-labelled unpackers, plus adjacent CTexture/CFastVB/current-owner rows documented in [`texture.cpp`](../texture.cpp/_index.md), [`FastVB.cpp`](../FastVB.cpp/_index.md), and [`MeshCollisionVolume.cpp`](../MeshCollisionVolume.cpp/_index.md). Tag anchor: `texel-unpack-head-wave672`; the next queue head after this pass is `0x0058577f CFastVB__TexelUnpackProfile_005e9f3c__ctor`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x00585576` | `void __thiscall CDXTexture__UnpackTexels_Bits332ToFloat4(void * this, uint source_x, uint source_y, float * destination_vec4_array, int unused_context)` | 3-3-2 unpacker expands 3/3/2-bit RGB lanes with alpha `1.0`, then optionally runs key-color zeroing and post-process/gamma-or-square. |
| `0x0058562d` | `void __thiscall CDXTexture__UnpackTexels_A8ToFloat4_ZeroRGB(void * this, uint source_x, uint source_y, float * destination_vec4_array, int unused_context)` | A8 unpacker writes zero RGB and byte-scaled alpha through the shared source pointer/count/gate fields. |
| `0x005856b8` | `void __thiscall CDXTexture__UnpackTexels_Bits332A8ToFloat4(void * this, uint source_x, uint source_y, float * destination_vec4_array, int unused_context)` | 3-3-2 plus A8 unpacker expands the first byte as RGB and the second byte as alpha. |

Wave672 read-back evidence verified `16` metadata rows, `16` tag rows, `16` xref rows, `1616` instruction rows, and `16` clean decompile rows across `0x00584b5f CTexture__UnpackTexels_Bgr8ToFloat4` through `0x005856b8 CDXTexture__UnpackTexels_Bits332A8ToFloat4`. Post-Wave672 queue telemetry is `6098` total, `3746` commented, `2352` commentless, `1217` exact-undefined signatures, `571` `param_N`, strict clean-signature proxy `3696/6098 = 60.61%`, and next head `0x0058577f CFastVB__TexelUnpackProfile_005e9f3c__ctor`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260521-042809_post_wave672_texel_unpack_head_verified`.

Exact profile ABI, format-table contract, lane-order enum contracts, runtime texture output behavior, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave672 texel unpack head`, `texel-unpack-head-wave672`, `0x00584b5f CTexture__UnpackTexels_Bgr8ToFloat4`, `0x005856b8 CDXTexture__UnpackTexels_Bits332A8ToFloat4`, `0x0058577f CFastVB__TexelUnpackProfile_005e9f3c__ctor`.

## Wave671 Texel Callback/Raw Packers Read-Back Note

Wave671 texel callback/raw packers saved seven CDXTexture-labelled packers, plus one adjacent CTexture row documented in [`texture.cpp`](../texture.cpp/_index.md). Tag anchor: `texel-callback-raw-packers-wave671`; the next queue head after this pass is `0x00584b5f CTexture__UnpackTexels_Bgr8ToFloat4`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x00584724` | `void __thiscall CDXTexture__PackTexels_CallbackPerTexel_RepeatA(void * this, uint output_x, uint output_y, float * source_vec4_array, int unused_context)` | Repeat-A callback wrapper optionally normalizes source vec4 records, computes the output pointer from `+0x1058/+0x105c/+0x20`, and calls observed helper `0x005759c3` once per texel with selector `1`. |
| `0x00584786` | `void __thiscall CDXTexture__PackTexels_CallbackPerTexel_RepeatB(void * this, uint output_x, uint output_y, float * source_vec4_array, int unused_context)` | Repeat-B callback wrapper using the same output/count fields and observed helper `0x005759c3` with selector `2`. |
| `0x005847e9` | `void __thiscall CDXTexture__PackTexels_CallbackPerTexel_Once(void * this, uint output_x, uint output_y, float * source_vec4_array, int unused_context)` | Single-call callback wrapper that pushes byte count `count*4`, source pointer, and output pointer to observed helper `0x005759c3`. |
| `0x00584831` | `void __thiscall CDXTexture__PackTexels_CopyRaw32(void * this, uint output_x, uint output_y, void * source_texel_records, int unused_context)` | Raw-copy packer copying the first 4 bytes from each observed 16-byte source record. |
| `0x00584886` | `void __thiscall CDXTexture__PackTexels_CopyRaw64(void * this, uint output_x, uint output_y, void * source_texel_records, int unused_context)` | Raw-copy packer copying the first 8 bytes from each observed 16-byte source record. |
| `0x005848e3` | `void __thiscall CDXTexture__PackTexels_CopyRaw128(void * this, uint output_x, uint output_y, void * source_texel_records, int unused_context)` | Raw-copy packer copying `count*16` bytes from the source record stream using MOVSD.REP/tail-byte copy. |
| `0x00584936` | `void __thiscall CDXTexture__PackTexels_NoDither_A16L16(void * this, uint output_x, uint output_y, float * source_vec4_array, int unused_context)` | Currently named no-dither A16L16 packer; the current decompile still reads the shared `+0x34` dither-table term before writing high 16 source `+0xc` and low 16 weighted-RGB luminance. |

Wave671 read-back evidence verified `8` metadata rows, `8` tag rows, `9` xref rows, `840` instruction rows, and `8` clean decompile rows across `0x00584724 CDXTexture__PackTexels_CallbackPerTexel_RepeatA` through `0x00584a4c CTexture__PackTexels_NoDither_Bits16_16_16`. Post-Wave671 queue telemetry is `6098` total, `3730` commented, `2368` commentless, `1217` exact-undefined signatures, `587` `param_N`, strict clean-signature proxy `3680/6098 = 60.35%`, and next head `0x00584b5f CTexture__UnpackTexels_Bgr8ToFloat4`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260521-035844_post_wave671_texel_callback_raw_packers_verified`.

Exact callback ABI, selector contract, byte-count contract, source-record contract, exact no-dither naming rationale, luminance/alpha contract, lane-order contract, runtime texture output behavior, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave671 texel callback/raw packers`, `texel-callback-raw-packers-wave671`, `0x00584724 CDXTexture__PackTexels_CallbackPerTexel_RepeatA`, `0x00584a4c CTexture__PackTexels_NoDither_Bits16_16_16`, `0x00584b5f CTexture__UnpackTexels_Bgr8ToFloat4`.

## Wave669 Dither Packer Tail Read-Back Note

Wave669 dither packer tail saved eight CDXTexture-labelled dither-packer rows, plus four adjacent CFastVB/CTexture packers documented in [`FastVB.cpp`](../FastVB.cpp/_index.md) and [`texture.cpp`](../texture.cpp/_index.md). Tag anchor: `dither-packer-tail-wave669`; the next queue head after this pass is `0x00583c8e CTexture__PackTexels_Dither_Bits8_8`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x00582ef8` | `void __thiscall CDXTexture__PackTexels_Dither_Bits2_10_10_10(void * this, uint output_x, uint output_y, float * source_vec4_array, int unused_context)` | Dithered 32-bit 2-10-10-10-style output using observed 2-bit and 10-bit scale constants. |
| `0x00583041` | `void __thiscall CDXTexture__PackTexels_Dither_Bits8888(void * this, uint output_x, uint output_y, float * source_vec4_array, int unused_context)` | Dithered 32-bit 8-8-8-8-style output from four source vec4 lanes. |
| `0x0058318a` | `void __thiscall CDXTexture__PackTexels_Dither_Bits888(void * this, uint output_x, uint output_y, float * source_vec4_array, int unused_context)` | Dithered 24-bit 8-8-8-style packed output in a 32-bit store. |
| `0x005832af` | `void __thiscall CDXTexture__PackTexels_Dither_Bits1616(void * this, uint output_x, uint output_y, float * source_vec4_array, int unused_context)` | Dithered 16-16-style output from the first two source vec4 lanes. |
| `0x005833a6` | `void __thiscall CDXTexture__PackTexels_Dither_Bits2_10_10_10_Alt(void * this, uint output_x, uint output_y, float * source_vec4_array, int unused_context)` | Alternate 2-10-10-10-style source-lane order sharing the same callback/output context. |
| `0x005834ef` | `void __thiscall CDXTexture__PackTexels_Dither_Bits16_16_16_16(void * this, uint output_x, uint output_y, float * source_vec4_array, int unused_context)` | Dithered 16-16-16-16-style output, two 32-bit words per texel in the observed decompile. |
| `0x00583670` | `void __thiscall CDXTexture__PackTexels_Dither_PaletteIndexA8(void * this, uint output_x, uint output_y, float * source_vec4_array, int unused_context)` | Scans the observed 256-entry vec4 palette at `this+0x40` for nearest RGB distance, then writes palette-index plus dithered alpha. |
| `0x005837b7` | `void __thiscall CDXTexture__PackTexels_Dither_PaletteIndex8(void * this, uint output_x, uint output_y, float * source_vec4_array, int unused_context)` | Scans the observed 256-entry vec4 palette at `this+0x40` for nearest RGBA distance and writes one 8-bit palette index. |

Wave669 read-back evidence verified `12` metadata rows, `12` tag rows, `12` xref rows, `444` instruction rows, and `12` clean decompile rows across the dither-packer tail cluster from `0x00582ef8 CDXTexture__PackTexels_Dither_Bits2_10_10_10` through `0x00583ba4 CTexture__PackTexels_Dither_L16`. Queue after Wave669 is `6098` total, `3713` commented, `2385` commentless, `1217` exact-undefined signatures, `604` `param_N`, comment-backed proxy `3713/6098 = 60.89%`, strict clean-signature proxy `3663/6098 = 60.07%`, and next head `0x00583c8e CTexture__PackTexels_Dither_Bits8_8`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260521-030557_post_wave669_dither_packer_tail_verified`.

Exact dither table provenance, texel-pack callback ABI, channel-order enum contracts, palette metric/layout, runtime texture output behavior, BEA patching, and rebuild parity remain unproven.

## Wave668 Dither Packer Head Read-Back Note

Wave668 dither packer head hardened twelve decoded-texel post-process and dither-packer rows with the `dither-packer-head-wave668` and `wave668-readback-verified` tags. The tranche itself lives in the adjacent CFastVB/CTexture-labelled packer island: `0x0058210e CTexture__PostProcessDecodedTexels_GammaOrSquare` through `0x00582dd3 CTexture__PackTexels_Dither_Bits444`.

The post-Wave668 queue head is `0x00582ef8 CDXTexture__PackTexels_Dither_Bits2_10_10_10`, so the CDXTexture dither tail remains the next high-signal texture-family work. Wave668 made no renames, no function-boundary changes, no executable-byte changes, and no runtime texture-output claim.

Wave668 read-back evidence verified `12` metadata rows, `12` tag rows, `52` xref rows, `444` instruction rows, and `12` clean decompile rows. Queue after Wave668 is `6098` total, `3701` commented, `2397` commentless, `1217` exact-undefined signatures, `616` `param_N`, comment-backed proxy `3701/6098 = 60.69%`, strict clean-signature proxy `3651/6098 = 59.87%`, and next head `0x00582ef8 CDXTexture__PackTexels_Dither_Bits2_10_10_10`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260521-024019_post_wave668_dither_packer_head_verified`.

Exact dither table provenance, texel-pack callback ABI, channel-order enum contracts, gamma/curve identity, runtime texture output behavior, BEA patching, and rebuild parity remain unproven. Canonical row details live in [`FastVB.cpp`](../FastVB.cpp/_index.md) and [`texture.cpp`](../texture.cpp/_index.md).

## Wave667 Texel Profile Prep Read-Back Note

Wave667 texel-profile prep covered ten adjacent texel profile preparation rows after Wave666. Tag anchor: `texel-profile-prep-wave667`. Address anchors include `0x00581263 CFastVB__TexelUnpackProfile__dtor`, `0x00581e8c CDXTexture__NormalizeAndCopyVec4Array`, and next queue head `0x0058210e CTexture__PostProcessDecodedTexels_GammaOrSquare`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x005818b7` | `void __fastcall CDXTexture__PrepareDxtScaleAndQuantizedUV(void * texture_context)` | Checks observed DXT2/DXT3 FourCC values, stores a block scale at `+0x1074` and reciprocal at `+0x1078`, then quantizes float bounds at `+0x24/+0x28/+0x2c/+0x30` to observed scale grids. |
| `0x00581d49` | `void __fastcall CDXTexture__ProbeTexelProfileSample(void * texel_profile)` | Temporarily rewrites count, stride/sample pointer, source pointer, callback table, and mode fields to sample one vec4 at `+0x24`, optionally routes non-mode-1/non-mode-4 data through the domain converter, invokes vtable slots `+8` and `+4`, then restores saved fields. |
| `0x00581e8c` | `int __thiscall CDXTexture__NormalizeAndCopyVec4Array(void * this, float * source_vec4_array, int unused_context)` | Fills the scratch/output buffer at `+0x1054` from `source_vec4_array`, using either table-lookup or direct fast reciprocal-square-root normalization depending on `+0x14`; modes `1/4` normalize RGB and copy alpha, while other modes copy RGB and normalize alpha. |

The cross-owner CFastVB-labelled rows in this wave are documented in [`FastVB.cpp`](../FastVB.cpp/_index.md): `0x00581263 CFastVB__TexelUnpackProfile__dtor`, `0x00581279 CFastVB__ConvertTexelVectorDomain`, `0x0058183d CFastVB__TexelCodecProfile__dtor`, `0x005819b8 CFastVB__LookupCurveFromRsqrtScaledInput`, `0x00581a08 CFastVB__LookupCurveFromSquaredInput`, `0x00581cc0 CFastVB__TexelUnpackProfile__InitConversionScratch`, and `0x00581e1c CFastVB__TexelUnpackProfile__ZeroTexelsMatchingKeyColor`.

Wave667 read-back evidence: dry/apply/final dry reported `updated=0 skipped=10 renamed=0 would_rename=0 signature_updated=10 missing=0 bad=0`, then `updated=10 skipped=0 renamed=0 would_rename=0 signature_updated=10 missing=0 bad=0`, then `updated=0 skipped=10 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`. Post exports verified `10` metadata rows, `10` tag rows, `180` xref rows, `870` instruction rows, and `10` clean decompile rows. Queue after Wave667 is `6098` total, `3689` commented, `2409` commentless, `1217` exact-undefined signatures, `628` `param_N`, comment-backed proxy `3689/6098 = 60.50%`, strict clean-signature proxy `3639/6098 = 59.68%`, and next head `0x0058210e CTexture__PostProcessDecodedTexels_GammaOrSquare`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260521-021208_post_wave667_texel_profile_verified`.

Exact texel-profile/profile ABI, texel-domain enum, color-space meaning, DXT format contract, curve identity, callback contract, runtime texture conversion behavior, runtime transparency behavior, BEA patching, and rebuild parity remain unproven.

## Wave666 Texture Dual-Profile/Upload Read-Back Note

Wave666 texture dual-profile/upload covered ten adjacent dual-profile conversion and upload rows after Wave665. Tag anchor: `texture-dual-profile-wave666`. Address anchors include `0x0057fa10 CFastVB__BlendWeightTable_scalar_deleting_dtor`, `0x00580eef CFastVB__ShutdownActiveProfile_Thunk`, and next queue head `0x00581263 CFastVB__TexelUnpackProfile__dtor`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x0058083d` | `void __fastcall CDXTexture__ResetSurfaceCopyContext(void * surface_copy_context)` | Clears five consecutive dwords in the surface-copy/upload context at offsets `+0x00` through `+0x10`. |
| `0x00580850` | `int __stdcall CDXTexture__CopyLockedRectPitchAware(void * source_surface, void * destination_surface)` | Queries the source surface descriptor, locks source and destination rectangles through vtable slot `+0x34`, adjusts DXT-style row count for observed FourCC values DXT1-DXT5, copies the minimum source/destination pitch per row, advances each pitch independently, and unlocks both surfaces. |
| `0x0058092d` | `int __fastcall CDXTexture__FinalizeTextureUploadAndReleaseTemp(void * upload_context)` | Unlocks active temporary/destination surfaces, attempts a device vtable `+0x78` surface update with D3D9 debug mute toggled, falls back to `CDXTexture__CopyLockedRectPitchAware`, releases observed slots at `+0x04/+0x08/+0x0c/+0x10`, clears them, and returns zero. |
| `0x00580a00` | `int __fastcall CDXTexture__FinalizeTextureUploadAndReleaseTemp_Duplicate(void * upload_context)` | Duplicate/tail entry for the same texture-upload finalizer pattern. |

The cross-owner CFastVB-labelled rows in this wave are documented in [`FastVB.cpp`](../FastVB.cpp/_index.md): `0x0057fa10 CFastVB__BlendWeightTable_scalar_deleting_dtor`, `0x0057fa5c CFastVB__BlendDualProfileBoneWeights`, `0x00580120 CFastVB__RunDualProfileConversionStage`, `0x0058070e CFastVB__InitDualTexelConversionPipeline`, `0x005809de CFastVB__ShutdownActiveProfile`, and `0x00580eef CFastVB__ShutdownActiveProfile_Thunk`.

Wave666 read-back evidence: dry/apply/final dry reported `updated=0 skipped=10 renamed=0 would_rename=0 signature_updated=10 missing=0 bad=0`, then `updated=10 skipped=0 renamed=0 would_rename=0 signature_updated=8 missing=0 bad=0`, then `updated=0 skipped=10 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`. Post exports verified `10` metadata rows, `10` tag rows, `22` xref rows, `1060` instruction rows, and `10` clean decompile rows. Queue after Wave666 is `6098` total, `3679` commented, `2419` commentless, `1217` exact-undefined signatures, `638` `param_N`, comment-backed proxy `3679/6098 = 60.33%`, strict clean-signature proxy `3629/6098 = 59.51%`, and next head `0x00581263 CFastVB__TexelUnpackProfile__dtor`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260521-014950_post_wave666_texture_dual_profile_verified`.

Exact profile/layout identity, exact descriptor layout, flag enum naming, callback body semantics, COM/D3D interface contracts, UpdateSurface identity, runtime texture conversion behavior, runtime upload behavior, BEA patching, and rebuild parity remain unproven.

## Wave665 Texture Resample Surface/Volume Read-Back Note

Wave665 texture resample surface/volume covered nine adjacent texture copy, downsample, and resample rows after Wave664. Tag anchor: `texture-resample-wave665`. Address anchors include `0x0057e0c3 CDXTexture__ConvertSurfaceDirectCopyOrDxtCopy`, `0x0057f391 CDXTexture__ResampleVolumeTrilinear`, and next queue head `0x0057fa10 CFastVB__BlendWeightTable_scalar_deleting_dtor`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x0057e0c3` | `int __fastcall CDXTexture__ConvertSurfaceDirectCopyOrDxtCopy(void * texture_resample_context)` | Validates matching source/destination format, dimensions, depth, and row-byte fields from a two-surface texture context, delegates DXT block copying when appropriate, or copies rows after palette and dirty-flag checks. |
| `0x0057e4d3` | `int __fastcall CDXTexture__ResampleSurfaceNearestNeighbor(void * texture_resample_context)` | Handles mode byte `2` with source and destination vec4 row buffers, 16.16 stepping, and nearest-neighbor destination row writes. |
| `0x0057e6cc` | `int __fastcall CDXTexture__DownsampleSurface2x2_WithFastPaths(void * texture_resample_context)` | Handles mode byte `5` by validating 2D half-size dimensions, trimming odd source extents, trying packed-format fast paths including the Wave664 helpers, and falling back to a vec4 2x2 average. |
| `0x0057eadb` | `int __fastcall CDXTexture__DownsampleVolume2x2x2(void * texture_resample_context)` | Handles mode byte `5` for volumes by validating 3D half-size dimensions, trimming odd source extents, staging source vec4 row planes, and averaging observed 2x2x2 samples. |
| `0x0057f002` | `int __fastcall CDXTexture__ResampleSurfaceBilinear(void * texture_resample_context)` | Handles mode byte `3` for single-slice surfaces by building X/Y resample kernels, caching two source rows, bilinearly combining vec4 channels, and writing destination rows. |
| `0x0057f391` | `int __fastcall CDXTexture__ResampleVolumeTrilinear(void * texture_resample_context)` | Handles mode byte `3` for volumes by building X/Y/Z resample kernels, caching four source row planes, trilinearly combining vec4 channels, and writing destination volume rows. |

The cross-owner CFastVB-labelled rows in this wave are documented in [`FastVB.cpp`](../FastVB.cpp/_index.md): `0x0057e200 CFastVB__BlendEqualDimensionVolumeData`, `0x0057e2de CFastVB__BlendClampedVolumeData`, and `0x0057ef10 CFastVB__BuildResampleKernel1D`.

Wave665 read-back evidence: dry/apply/final dry reported `updated=0 skipped=9 renamed=0 would_rename=0 signature_updated=9 missing=0 bad=0`, then `updated=9 skipped=0 renamed=0 would_rename=0 signature_updated=9 missing=0 bad=0`, then `updated=0 skipped=9 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`. Post exports verified `9` metadata rows, `9` tag rows, `13` xref rows, `333` instruction rows, and `9` clean decompile rows. Queue after Wave665 is `6098` total, `3669` commented, `2429` commentless, `1217` exact-undefined signatures, `648` `param_N`, comment-backed proxy `3669/6098 = 60.17%`, strict clean-signature proxy `3619/6098 = 59.35%`, and next head `0x0057fa10 CFastVB__BlendWeightTable_scalar_deleting_dtor`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260521-012532_post_wave665_texture_resample_verified`.

Exact texture surface/context layout, palette contract, vtable contract, edge-mode naming, resample-kernel layout, CFastVB owner identity, runtime copy behavior, runtime resample/downsample quality, BEA patching, and rebuild parity remain unproven.

## Wave664 Texture Downsample Kernels Read-Back Note

Wave664 texture downsample kernels covered twelve adjacent downsample helpers reached from `0x0057e6cc CDXTexture__DownsampleSurface2x2_WithFastPaths`. Tag anchor: `texture-downsample-wave664`. Address anchors include `0x0057d216 CFastVB__DispatchMmxKernel_00657974`, `0x0057df84 CDXTexture__Average2x2Block_A4L4`, and next queue head `0x0057e0c3 CDXTexture__ConvertSurfaceDirectCopyOrDxtCopy`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x0057d216` | `void __fastcall CFastVB__DispatchMmxKernel_00657974(void * downsample_context)` | Cross-owner dispatch helper that reads source/destination surface pointers plus extent/stride fields from the two-slot downsample context and calls the CPU-selected MMX-style function pointer at `0x00657974`. |
| `0x0057d4ad` | `void __fastcall CFastVB__DispatchMmxKernel_00657978(void * downsample_context)` | Cross-owner dispatch helper with the same context shape, calling the CPU-selected MMX-style function pointer at `0x00657978`. |
| `0x0057d4db` | `int __fastcall CDXTexture__Average2x2Block_RGB565(void * downsample_context)` | Averages observed 2x2 packed 16-bit source texels into one RGB565-style destination texel using `0xf81f/0x07e0` masks and rounded sums. |
| `0x0057d62b` | `int __fastcall CDXTexture__Average2x2Block_RGB555(void * downsample_context)` | Averages observed 2x2 packed 16-bit source texels into one RGB555-style destination texel using `0x7c1f/0x03e0` masks and rounded sums. |
| `0x0057d74f` | `int __fastcall CDXTexture__Average2x2Block_ARGB1555(void * downsample_context)` | Averages observed 2x2 packed 16-bit source texels into one ARGB1555-style destination texel using `0x83e0/0x7c1f` masks and rounded sums. |
| `0x0057d89e` | `int __fastcall CDXTexture__Average2x2Block_A4R4G4B4(void * downsample_context)` | Averages observed 2x2 packed 16-bit source texels into one A4R4G4B4-style destination texel using `0xf0f0/0x0f0f` masks and rounded sums. |
| `0x0057d9f1` / `0x0057db30` / `0x0057dbcb` | Retained `CFastVB__Downsample2x1_*` signatures | Cross-owner retained-name helpers for R5G6B5-style packed bytes, L8 byte luminance, and A1R5G5B5-style packed words; canonical owner note is in [`FastVB.cpp`](../FastVB.cpp/_index.md). |
| `0x0057dd17` | `int __fastcall CDXTexture__Average2x2Block_RGB444(void * downsample_context)` | Averages observed 2x2 packed 16-bit source texels into one RGB444-style destination texel using `0x0f0f/0x00f0` masks and rounded sums. |
| `0x0057de38` | `int __fastcall CDXTexture__Average2x2Block_A8L8(void * downsample_context)` | Averages observed 2x2 packed 16-bit source texels into one A8L8-style destination texel by separately accumulating low and high byte lanes. |
| `0x0057df84` | `int __fastcall CDXTexture__Average2x2Block_A4L4(void * downsample_context)` | Averages observed 2x2 packed byte source samples into one A4L4-style destination byte using `0xf0/0x0f` masks and rounded sums. |

Wave664 read-back evidence: dry/apply/final dry reported `updated=0 skipped=12 renamed=0 would_rename=0 signature_updated=12 missing=0 bad=0`, then `updated=12 skipped=0 renamed=0 would_rename=0 signature_updated=12 missing=0 bad=0`, then `updated=0 skipped=12 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`. Post exports verified `12` metadata rows, `12` tag rows, `12` xref rows, `444` instruction rows, and `12` clean decompile rows. Queue after Wave664 is `6098` total, `3660` commented, `2438` commentless, `1217` exact-undefined signatures, `657` `param_N`, comment-backed proxy `3660/6098 = 60.02%`, strict clean-signature proxy `3610/6098 = 59.20%`, and next head `0x0057e0c3 CDXTexture__ConvertSurfaceDirectCopyOrDxtCopy`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260521-005813_post_wave664_texture_downsample_verified`.

Exact surface/context layout, CPU dispatch pointer identity, packed format contracts, retained CFastVB owner identity, runtime downsample behavior, runtime filter quality, BEA patching, and rebuild parity remain unproven.

## Wave663 Mapped Texture Resample Setup Read-Back Note

Wave663 mapped texture resample setup covered the next mapped texture output/resample setup bridge after Wave662. Tag anchor: `mapped-texture-resample-wave663`. Address anchors include `0x0057c7a4 CMeshCollisionVolume__LoadMappedTextureResourcesByMode`, `0x0057cca4 CFastVB__BuildResampleKernelBuckets`, and next queue head `0x0057d216 CFastVB__DispatchMmxKernel_00657974`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x0057c7a4` | `int __thiscall CMeshCollisionVolume__LoadMappedTextureResourcesByMode(void * this, void * mapped_resource_name_or_path, int output_mode, int open_mode_flags, int unused_arg3)` | Selects a format descriptor list by `output_mode`, converts the surface-node chain when the selected descriptor differs, opens a mapped output context, and dispatches BMP/JPEG/DDS-style writes for observed modes `0/1/4/6`. |
| `0x0057cc7b` | `double __stdcall Math__FloorFloatToDouble(float value)` | Cross-owner resample helper that casts a float to double and forwards to the floor-like CRT/helper at `0x0055dfe7`; canonical owner note is in [`Math.cpp`](../Math.cpp/_index.md). |
| `0x0057cc8e` | `void __fastcall CFastVB__ClearTripleDword(void * triple_dword)` | Cross-owner setup helper that zeroes three dwords for dual-profile conversion paths; canonical owner note is in [`FastVB.cpp`](../FastVB.cpp/_index.md). |
| `0x0057cca4` | `int * __stdcall CFastVB__BuildResampleKernelBuckets(uint output_count, int source_count, int clamp_edges)` | Cross-owner setup helper that allocates a variable-length resample bucket table, accumulates per-source weights, and records per-output bucket offsets for conversion callers. |

Wave663 read-back evidence: dry/apply/final dry reported `updated=0 skipped=4 renamed=0 would_rename=0 signature_updated=4 missing=0 bad=0`, then `updated=4 skipped=0 renamed=0 would_rename=0 signature_updated=4 missing=0 bad=0`, then `updated=0 skipped=4 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`. Post exports verified `4` metadata rows, `4` tag rows, `9` xref rows, `148` instruction rows, and `4` clean decompile rows. Queue after Wave663 is `6098` total, `3648` commented, `2450` commentless, `1217` exact-undefined signatures, `669` `param_N`, comment-backed proxy `3648/6098 = 59.82%`, strict clean-signature proxy `3598/6098 = 59.00%`, and next head `0x0057d216 CFastVB__DispatchMmxKernel_00657974`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260521-003649_post_wave663_mapped_texture_resample_verified`.

Exact mapped texture output mode enum, file/context layouts, resample kernel table layout, runtime texture export behavior, runtime resampling quality, BEA patching, and rebuild parity remain unproven.

## Wave662 CDXTexture Image Codec Read-Back Note

Wave662 CDXTexture image codec hardening covered 21 adjacent CDXTexture descriptor, surface-node, codec decode/encode, stream-write, and DXT copy rows without renames, boundary changes, or executable-byte changes:

Tag anchor: `cdxtexture-image-codec-wave662`. Address anchor: `0x00579b39 CDXTexture__LookupNamedFormatDescriptor` through `0x0057cf60 CDXTexture__CopyDxtBlockRegion`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x00579b39` | `int __stdcall CDXTexture__LookupNamedFormatDescriptor(void * format_name, uint required_flags, void * out_descriptor_or_null)` | Binary-searches the `0x005e9340` named format descriptor table, applies the requested flag mask, optionally copies the three-dword descriptor row, and returns D3D-style status codes. |
| `0x00579bd5` | `void __stdcall CDXTexture__SetD3D9DebugMute(int mute_enabled)` | Resolves `DebugSetMute` from `d3d9.dll` / `d3d9d.dll`, gates calls through cached config, and forwards the mute value when allowed. |
| `0x00579ca5` / `0x00579cbe` / `0x00579d17` / `0x00579d33` | Surface-node init/free/destructor/descriptor helpers | Clear observed surface-node fields, release owned buffers and child nodes, wrap scalar deletion, and copy descriptor identity plus extent/stride fields into the surface node. |
| `0x00579e08` / `0x0057ca3a` | BMP file/DIB memory decode helpers | Validate BMP file/DIB headers, palette data, masks, row bounds, and payload length before populating decoded pixel/palette buffers. |
| `0x0057a934` / `0x0057c28b` | BMP and DDS surface export helpers | Build BMP/DDS headers and stream optional palette data plus observed surface rows/blocks through `WriteFile` when enabled. |
| `0x0057af0a` / `0x0057b182` / `0x0057b6fa` / `0x0057b9ce` | JPEG, TGA, PPM, and PNG memory decode helpers | Validate codec headers, set up codec/decode contexts, handle palette/direct-color or transform paths, and populate decoded surface buffers. |
| `0x0057bf1f` | `int __thiscall CDXTexture__BuildDdsSurfaceNodeTree(void * this, void * dds_bytes, uint byte_count, void * unused_context)` | Validates DDS magic/header fields, resolves the format descriptor, derives cube/volume/mip counts, and builds a linked surface-node tree over payload spans. |
| `0x0057c57d` / `0x0057c5b2` / `0x0057c5dc` | Stream flush helpers and JPEG stream encoder | Flush a `WriteFile`-backed stream buffer and feed surface rows converted to RGB triples into the JPEG encoder path. |
| `0x0057cc53` / `0x0057cc5d` | Surface-pair init/release helpers | Clear and release two observed interface slots in a surface-pair/mapped-file context. |
| `0x0057cf60` | `int __fastcall CDXTexture__CopyDxtBlockRegion(void * copy_context)` | Validates DXT block alignment, chooses DXT1 8-byte or DXT2-5 16-byte blocks, and copies the requested block rectangle across row/depth strides. |

Wave662 read-back evidence: patched dry/apply/final dry reported `updated=0 skipped=21 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`, then `updated=21 skipped=0 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`, then `updated=0 skipped=21 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`. Post exports verified `21` metadata rows, `21` tag rows, `59` xref rows, `2793` instruction rows, and `21` clean decompile rows. Queue after Wave662 is `6098` total, `3644` commented, `2454` commentless, `1217` exact-undefined signatures, `673` `param_N`, comment-backed proxy `3644/6098 = 59.76%`, strict clean-signature proxy `3594/6098 = 58.94%`, and next head `0x0057c7a4 CMeshCollisionVolume__LoadMappedTextureResourcesByMode`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260521-001158_post_wave662_cdxtexture_image_codec_verified`.

Exact CDXTexture, surface-node, descriptor, stream-writer, COM/D3D, DDS, BMP, TGA, PPM, PNG, JPEG, and DXT copy-context layouts, runtime image fidelity, runtime upload/export behavior, BEA patching, and rebuild parity remain unproven.

## Wave659 Matrix Dispatch Correction Context

Wave659 matrix dispatch hardening corrected two stale `CDXTexture` dispatch labels in the matrix dispatch-table island and moved those rows under owner-neutral [`Math.cpp`](../Math.cpp/_index.md) evidence:

| Address | Saved name | Saved signature | Evidence |
|---------|------------|-----------------|----------|
| `0x00577239` | `Math__BuildTranslationMatrix4x4_Dispatch` | `void __stdcall Math__BuildTranslationMatrix4x4_Dispatch(void * out_matrix4x4, float translate_x, float translate_y, float translate_z)` | Runtime dispatch-table slot `0x00656f98`; paired source/default slot `0x006570b8` points to recovered `0x0057726d Math__BuildTranslationMatrix4x4`. |
| `0x00577267` | `Math__BuildTranslationMatrix4x4_Dispatch_Thunk` | `void __stdcall Math__BuildTranslationMatrix4x4_Dispatch_Thunk(void * out_matrix4x4, float translate_x, float translate_y, float translate_z)` | Pure jump thunk to runtime dispatch-table slot `0x00656f98`. |

Wave659 read-back evidence: dry/apply/final dry reported `updated=0 skipped=16 created=0 would_create=3 body_set=0 would_set_body=3 renamed=0 would_rename=5 signature_updated=13 missing=0 bad=0`, then `updated=16 skipped=0 created=3 would_create=0 body_set=3 would_set_body=0 renamed=5 would_rename=0 signature_updated=11 missing=0 bad=0`, then `updated=0 skipped=16 created=0 would_create=0 body_set=0 would_set_body=0 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`. Queue after Wave659 is `6096` total, `3602` commented, `2494` commentless, `1217` exact-undefined signatures, `711` `param_N`, comment-backed proxy `3602/6096 = 59.09%`, strict clean-signature proxy `3552/6096 = 58.27%`, and next head `0x005776a5 CTexture__DispatchPtr00656fd0_WithInit`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260521-221700_post_wave659_matrix_dispatch_verified`.

Exact vector/matrix storage contract, CPU feature replacement behavior, runtime math correctness, BEA patching, and rebuild parity remain unproven.

## Wave657 Texture Repeat / Mip / Decode Read-Back Note

Wave657 texture repeat/mip/decode hardening covered three adjacent texture-path rows without renames or boundary changes:

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x00574abb` | `void __stdcall CDXTexture__RepeatCallbackN(int unused_arg0, int unused_arg1, int repeat_count, void * callback_fn)` | Retained-name stdcall helper ignores the first two stack arguments in the current decompile and invokes `callback_fn` `repeat_count` times when the repeat count is positive; current xref comes from a retained CFastVB-labelled callback/weight-table row. |
| `0x00574e2b` | `uint __stdcall CDXTexture__GenerateMipChainBySurfaceCopy(void * surface_chain, int unused_context, uint start_level, uint mip_flags)` | Validates a surface-chain type through vfunc `+0x28`, derives mip flags when `mip_flags` is `0xffffffff`, walks mip levels/faces via vfunc `+0x34/+0x48`, copies or converts acquired surface pairs, releases surfaces, and returns D3D-style status codes. |
| `0x00575923` | `int __stdcall CDXTexture__DecodeMappedFileToTexture(void * decode_target, void * mapped_filename)` | Initializes mapped-file context, opens `mapped_filename` read-only, dispatches `CDXTexture__DecodeMappedMemoryEntry` on success, closes the handle/context, and returns decode status while the decompile still shows implicit `ESI`/`EAX`/`EDX` state. |

Wave657 read-back evidence: dry/apply/final dry reported `updated=0 skipped=3 renamed=0 would_rename=0 signature_updated=3 missing=0 bad=0`, then `updated=3 skipped=0 renamed=0 would_rename=0 signature_updated=3 missing=0 bad=0`, then `updated=0 skipped=3 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`. Post exports verified `3` metadata rows, `3` tag rows, `4` xref rows, `723` instruction rows, and `3` clean decompile rows. Queue after Wave657 is `6093` total, `3583` commented, `2510` commentless, `1217` exact-undefined signatures, `725` `param_N`, comment-backed proxy `3583/6093 = 58.81%`, strict clean-signature proxy `3533/6093 = 57.98%`, and next head `0x00575986 Math__IsFloatDiffOutsideTolerance`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260520-212214_post_wave657_texture_repeat_mip_decode_verified`.

Exact callback ABI, owner label provenance, D3D interface/type enum, cube/volume layout, file/path storage, runtime texture conversion behavior, runtime mip output, BEA patching, and rebuild parity remain unproven.

## Wave656 Texture Format / Upload Read-Back Note

Wave656 texture format/upload hardening covered eight adjacent texture-format selection and mapped-upload rows without renames or boundary changes:

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x00574270` | `int * __stdcall CDXTexture__FindFormatDescriptorById(int format_id)` | Walks descriptor rows from `DAT_005e6a68` to `PTR_DAT_00656f28` in 9-dword steps, returns the matching row, and falls back to `DAT_005e6a40`. |
| `0x00574296` | `uint __fastcall CFastVB__ComputeFormatMatchPenalty(void * requested_descriptor, void * candidate_descriptor)` | Rejects incompatible descriptor pairs through `DAT_005e7270`, then accumulates weighted mismatch penalties across five descriptor slots. |
| `0x0057430b` | `int __stdcall CDXTexture__SelectBestCompatibleFormat(void * format_id_list, int allow_mode_one_descriptor, void * requested_descriptor)` | Scans a zero-terminated format-id list, resolves descriptors, accepts exact matches first, and otherwise scores candidates with the penalty helper. |
| `0x0057437a` | `int __stdcall CFastVB__SelectBestFormatHandler(void * device_or_null, uint usage_flags, int resource_type, void * requested_descriptor)` | Mutes D3D debug output, optionally probes a device-like vtable, scores compatible rows, releases the local probe object, and restores debug output. |
| `0x00574476` | `int __stdcall CDXTexture__MapFormatTokenToInternalCode(int format_token)` | Maps `AL16` and `R16` FourCC-style tokens to internal codes `0x33` and `0x14`; other tokens return unchanged. |
| `0x00574577` | `int __fastcall CFastVB__ReturnInputInt(int value)` | Retained-name identity helper used as a texture profile/conversion-table callback target. |
| `0x0057457a` | `int __stdcall CDXTexture__LoadAndUploadMappedTexture_0057457a(void * target_ref, void * mode_flags, void * surface_ref, void * context_ref, void * fallback_ref)` | Builds a temporary surface/upload state, calls mapped-texture resource loading and upload helpers, and still shows implicit `EAX`/`ESI` state in the decompile. |
| `0x00574645` | `void __stdcall Platform__LoadAndUploadMappedTextureWrapper(void * target_ref, void * mode_flags, void * unused_surface_ref, void * context_ref, void * fallback_ref)` | Forwards selected arguments and a null final argument to the mapped-upload helper while leaving the third stack argument unused; screen-dump processing observes register side effects. |

Wave656 read-back evidence: dry/apply/final dry reported `updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=8 missing=0 bad=0`, then `updated=8 skipped=0 renamed=0 would_rename=0 signature_updated=8 missing=0 bad=0`, then `updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`. Post exports verified `8` metadata rows, `8` tag rows, `49` xref rows, `1768` instruction rows, and `8` clean decompile rows. Queue after Wave656 is `6093` total, `3580` commented, `2513` commentless, `1217` exact-undefined signatures, `728` `param_N`, comment-backed proxy `3580/6093 = 58.76%`, strict clean-signature proxy `3530/6093 = 57.94%`, and next head `0x00574abb CDXTexture__RepeatCallbackN`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260520-205422_post_wave656_texture_format_upload_verified`.

Exact texture descriptor schema, device interface identity, file/texture object ownership, runtime format selection/upload behavior, BEA patching, and rebuild parity remain unproven.

## Wave617 Static Read-Back Note

Wave617 hardened four CDXTexture head rows without renames or boundary changes:

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x00557300` | `int __thiscall CDXTexture__LoadTextureFromFile(void * this, int texture_slot)` | `CDXTexture__LoadTextureFromFile_Core` and `CDXTexture__Deserialize` pass ECX=this plus one stack texture-slot argument; RET `0x4` confirms the stack shape. |
| `0x005586e0` | `void __thiscall CDXTexture__DumpTextureToRGBA(void * this, char * output_path)` | `CDXTexture__DumpAllTexturesToTga` builds an output path, pushes it, and calls with ECX=texture; RET `0x4` confirms one explicit argument. |
| `0x00559410` | `void __thiscall CDXTexture__CreateMipmaps(void * this, void * chunk_reader, int texture_slot, int mip_count)` | `CDXTexture__Deserialize` calls with ECX=texture plus three stack args after a failed direct texture create; RET `0x0c` confirms the stack shape. |
| `0x00559be0` | `void * __cdecl CDXTexture__Deserialize(byte use_stream_payload, void * chunk_reader)` | Callers including `CResourceAccumulator__ReadResourceFile`, `CFEPGoodies__Deserialise`, `CDXBitmapFont__Deserialize`, and `CDXImposter__Deserialize` clean the two stack arguments after the call. |

Post-Wave617 queue telemetry is `6093` functions, `3176` commented, `2917` commentless, `1256` exact-undefined signatures, and `1056` `param_N` signatures. The next queue head is `0x0055a350 CDXTrees__CDXTrees`. This is saved static Ghidra evidence only; runtime texture loading/dumping/mipmap behavior, exact `CDXTexture`/`CTexture`/D3D/pixel-format/serialized layouts, BEA patching, and rebuild parity remain deferred.

## Wave571 Static Read-Back Note

Wave571 hardened `CDXTexture__IsResourceHandleValid` at `0x00528af0` as `bool __thiscall CDXTexture__IsResourceHandleValid(void * this)`. The helper is an ECX-only predicate over `this+0x0c`, returning whether that resource handle differs from `-1`; xrefs include `CDXTexture__LoadTextureFromFile` and `CVBufTexture__SetupSecondaryBlend`. This is saved static Ghidra evidence only; exact `CDXTexture` layout, runtime texture-loading behavior, source identity, BEA patching, and rebuild parity remain deferred.

## Recent Headless Semantic Promotions (2026-02-26)

| Address | Symbol | Purpose |
|---------|--------|---------|
| `0x0057ca3a` | `CDXTexture__DecodeBmpFromMemory` | Validates BMP memory headers and dispatches in-memory BMP decode path |
| `0x0057ca6a` | `CDXTexture__DecodeFromMemory_WithFallbackCodecs` | Tries multiple in-memory codecs and keeps first successful decode result |
| `0x00591340` | `CDXTexture__PumpDecoderStreamAndFinalize` | Pumps decoder stream callbacks/state machine and finalizes decode state |
| `0x0057d244` | `CDXTexture__Downsample2x2Average32` | Software 2x2 box filter over 32-bit pixels for mip/downscale fallback paths |
| `0x005818b7` | `CDXTexture__PrepareDxtScaleAndQuantizedUV` | Detects DXT2/DXT3 scale mode and quantizes UV-related fields to codec grid |
| `0x00582ef8` | `CDXTexture__PackTexels_Dither_Bits2_10_10_10` | Dithered texel packer for 2-10-10-10 packed output |
| `0x00583041` | `CDXTexture__PackTexels_Dither_Bits8888` | Dithered texel packer for 8-8-8-8 packed output |
| `0x0058318a` | `CDXTexture__PackTexels_Dither_Bits888` | Dithered texel packer for 8-8-8 packed output |
| `0x005832af` | `CDXTexture__PackTexels_Dither_Bits1616` | Dithered texel packer for 16-16 packed output |
| `0x005833a6` | `CDXTexture__PackTexels_Dither_Bits2_10_10_10_Alt` | Dithered texel packer for alternate 2-10-10-10 channel-order output |
| `0x005834ef` | `CDXTexture__PackTexels_Dither_Bits16_16_16_16` | Dithered texel packer for 16-16-16-16 packed output (two dwords per texel) |
| `0x00583670` | `CDXTexture__PackTexels_Dither_PaletteIndexA8` | Palette-distance quantizer writing palette-index plus 8-bit alpha |
| `0x005837b7` | `CDXTexture__PackTexels_Dither_PaletteIndex8` | Palette-distance quantizer writing 8-bit palette-index output |
| `0x00582244` | `CFastVB__PackTexels_Dither_Bits8_8_8_BGR` | Dithered texel packer writing B,G,R byte output |
| `0x00582355` | `CFastVB__PackTexels_Dither_Bits8_8_8_8_ARGB` | Dithered texel packer writing packed ARGB8888 output |
| `0x0058249e` | `CFastVB__PackTexels_Dither_Bits8_8_8_RGB` | Dithered texel packer writing R,G,B byte output |
| `0x005825c3` | `CFastVB__PackTexels_Dither_Bits5_6_5` | Dithered texel packer writing RGB565 output |
| `0x005826e8` | `CFastVB__PackTexels_Dither_Bits5_5_5` | Dithered texel packer writing RGB555 output |
| `0x0058280d` | `CFastVB__PackTexels_Dither_A1R5G5B5` | Dithered texel packer writing A1R5G5B5 output |
| `0x00582950` | `CFastVB__PackTexels_Dither_A4R4G4B4` | Dithered texel packer writing A4R4G4B4 output |
| `0x00583891` | `CFastVB__PackTexels_Dither_L8` | Dithered texel packer writing 8-bit luminance output |
| `0x00583979` | `CFastVB__PackTexels_Dither_A8L8` | Dithered texel packer writing 16-bit A8L8 output |
| `0x0056f260` | `CFastVB__ReleaseBufferAndResetTriplet_0056f260` | Releases owned buffer pointer and clears local span fields (`+0x04/+0x08/+0x0c`) |
| `0x0056f520` | `CFastVB__ReleaseBufferAndResetTriplet_0056f520` | Releases owned buffer pointer and clears local span fields (`+0x04/+0x08/+0x0c`) |
| `0x00573310` | `CFastVB__CountDwordsFromPointerSpan` | Returns dword count from pointer span (`(end - begin) >> 2`) with null guard |
| `0x005759c9` | `CFastVB__ConvertFloat32ArrayToFloat16` | Converts float32 source array into 16-bit half-float destination elements |
| `0x00575dc9` | `CFastVB__HermiteInterpolateVec3` | Cubic Hermite interpolation over four vec3 inputs at parameter `t` |
| `0x005759b6` | `CFastVB__DispatchIndirect_00657014` | Guarded indirect-dispatch thunk calling global function pointer `DAT_00657014` |
| `0x00575a58` | `CFastVB__DispatchIndirect_00657018` | Guarded indirect-dispatch thunk calling global function pointer `DAT_00657018` |
| `0x00575cae` | `CFastVB__DispatchIndirect_00656ff0_ReturnInt` | Guarded indirect-dispatch thunk forwarding args to `DAT_00656ff0` and returning int |
| `0x0057609c` | `CFastVB__DispatchIndirect_00657028` | Guarded indirect-dispatch thunk calling global function pointer `DAT_00657028` |
| `0x00576154` | `CFastVB__DispatchIndirect_00656f58` | Guarded indirect-dispatch thunk calling global function pointer `DAT_00656f58` |
| `0x00576698` | `CFastVB__DispatchIndirect_00656f38` | Guarded indirect-dispatch thunk calling global function pointer `DAT_00656f38` |
| `0x0057674a` | `CFastVB__DispatchIndirect_00657034` | Guarded indirect-dispatch thunk calling global function pointer `DAT_00657034` |
| `0x00574296` | `CFastVB__ComputeFormatMatchPenalty` | Computes weighted mismatch score between format candidates; returns `-1` when incompatible |
| `0x0057437a` | `CFastVB__SelectBestFormatHandler` | Scans format-handler table and selects best candidate using compatibility probes + penalty score |
| `0x005768f1` | `CFastVB__DispatchIndirect_00656f3c` | Guarded indirect-dispatch thunk calling global function pointer `DAT_00656f3c` |
| `0x00576b3a` | `CFastVB__DispatchIndirect_00656fc4` | Guarded indirect-dispatch thunk calling global function pointer `DAT_00656fc4` |
| `0x00576dfd` | `CFastVB__DispatchIndirect_00656f78` | Guarded indirect-dispatch thunk calling global function pointer `DAT_00656f78` |
| `0x005771af` | `CFastVB__DispatchIndirect_00656fb4` | Guarded indirect-dispatch thunk calling global function pointer `DAT_00656fb4` with 4 args |
| `0x005775b0` | `CFastVB__DispatchIndirect_00656fc8` | Guarded indirect-dispatch thunk calling global function pointer `DAT_00656fc8` |
| `0x005776d3` | `CFastVB__DispatchIndirect_00656fcc` | Guarded indirect-dispatch thunk calling global function pointer `DAT_00656fcc` |
| `0x005776e4` | `CFastVB__DispatchIndirect_00656fd4_ReturnInt` | Guarded indirect-dispatch thunk forwarding args to `DAT_00656fd4` and returning int |
| `0x0057798e` | `CFastVB__DispatchIndirect_00656fa4` | Guarded indirect-dispatch thunk calling global function pointer `DAT_00656fa4` with 3 args |
| `0x00577a0a` | `CFastVB__DispatchIndirect_00656f94` | Guarded indirect-dispatch thunk calling global function pointer `DAT_00656f94` with 4 args |
| `0x005784a9` | `CFastVB__DispatchIndirect_00657044` | Guarded indirect-dispatch thunk calling global function pointer `DAT_00657044` |
| `0x00579184` | `CFastVB__NormalizeQuaternionCopy` | Normalizes quaternion source (or zeroes near-zero input) and copies into destination |
| `0x00591050` | `CFastVB__ReleaseOwnedObjectAndReset` | Releases owned sub-object via vfunc(`+0x28`) and clears local state fields (`+0x04`, `+0x14`) |
| `0x00592b00` | `CFastVB__ParserContext_Shutdown` | Parser-context shutdown path performing virtual cleanup, release/reset helper, and terminal callback dispatch |
| `0x00592c50` | `CFastVB__ParserContext_Init` | Parser-context constructor/init path seeding callback table and default `"Bogus message code"` diagnostic string |
| `0x00599258` | `CFastVB__ComputeNodeSpanAndStride` | Recursively computes node span/stride aggregates across node-kind tree branches |
| `0x00599878` | `CFastVB__CloneNodeTreeWithAddRef` | Allocates and clones node tree while AddRef-copying child/interface references with failure cleanup |
| `0x00598a56` | `CFastVB__InitNodeType9` | Initializes node-type 9 record fields and binds vtable `0x005ef250` |
| `0x00598f82` | `CFastVB__NodeType9_scalar_deleting_dtor` | Scalar-deleting destructor for node-type 9 object (`vtable 0x005ef250`) |
| `0x00598b48` | `CFastVB__InitNodeType10` | Initializes node-type 10 record fields and binds vtable `0x005ef260` |
| `0x00598b81` | `CFastVB__NodeType10_dtor` | Destructor body for node-type 10 releasing owned children/resources then base cleanup |
| `0x00598fa4` | `CFastVB__NodeType10_scalar_deleting_dtor` | Scalar-deleting wrapper for node-type 10 destructor with optional free flag |
| `0x005988f5` | `CFastVB__CompareNodeValuesByTagAndPayload` | Typed payload comparator handling scalar/string/pointer payload forms by node tag |
| `0x00598873` | `CFastVB__CloneNodeChainWithAddRef` | Clones linked node chain and AddRef-copies referenced payload objects with failure rollback |
| `0x00598d6b` | `CFastVB__InitNodeType13` | Initializes node-type 13 storage defaults and binds vtable `0x005ef270` |
| `0x00599b13` | `CFastVB__SetParseErrorAndMarkStateDirty` | Emits parse diagnostic message and marks parser state/error flags dirty |
| `0x00599b69` | `CFastVB__NodeTreeHasBitFlag0x200` | Recursively walks node tree and returns whether payload bit `0x200` is present |
| `0x00584724` | `CDXTexture__PackTexels_CallbackPerTexel_RepeatA` | Counted callback-dispatch wrapper invoking per-texel conversion callback in repeat path A |
| `0x00584786` | `CDXTexture__PackTexels_CallbackPerTexel_RepeatB` | Counted callback-dispatch wrapper invoking per-texel conversion callback in repeat path B |
| `0x005847e9` | `CDXTexture__PackTexels_CallbackPerTexel_Once` | Single-call callback-dispatch wrapper invoking per-texel conversion callback |
| `0x00584831` | `CDXTexture__PackTexels_CopyRaw32` | Raw copy packer writing first 32 bits from each 16-byte source texel |
| `0x00584886` | `CDXTexture__PackTexels_CopyRaw64` | Raw copy packer writing first 64 bits from each 16-byte source texel |
| `0x005848e3` | `CDXTexture__PackTexels_CopyRaw128` | Raw copy packer writing full 128-bit source texel records |
| `0x00584936` | `CDXTexture__PackTexels_NoDither_A16L16` | Non-dither packer writing A16L16 packed output |
| `0x00585576` | `CDXTexture__UnpackTexels_Bits332ToFloat4` | Unpacks 8-bit 3-3-2 packed texels into float4 RGBA channels (alpha=1.0) |
| `0x0058562d` | `CDXTexture__UnpackTexels_A8ToFloat4_ZeroRGB` | Unpacks alpha-only 8-bit texels with RGB zeroed and alpha from source |
| `0x005856b8` | `CDXTexture__UnpackTexels_Bits332A8ToFloat4` | Unpacks paired 3-3-2 + 8-bit alpha texels into float4 RGBA channels |
| `0x00585da3` | `CDXTexture__UnpackTexels_Signed5_5_A6_ToFloat4` | Unpacks signed 5-5 plus alpha6 packed texels into float4 channels |
| `0x00585e9f` | `CDXTexture__UnpackTexels_Signed8_8_A8_ToFloat4_RG` | Unpacks signed 8-8 plus alpha8 texels into float4 RG lanes with scalar alpha |
| `0x005861b4` | `CDXTexture__UnpackTexels_Signed2_10_10_10_ToFloat4` | Unpacks signed 2-10-10-10 packed texels into float4 channels with sign expansion |
| `0x00586305` | `CDXTexture__UnpackTexels_Signed16_16_16_16_ToFloat4` | Unpacks signed 16-16-16-16 packed texels into float4 channels |
| `0x00586609` | `CDXTexture__UnpackTexels_CallbackPerTexel_Stride2_SetRGBAOne` | Callback wrapper for stride-2 records with post-write RGBA defaults |
| `0x0058677b` | `CDXTexture__UnpackTexels_CallbackSingleTexel` | Single-texel callback wrapper for helper-dispatched unpack conversion |
| `0x00581d49` | `CDXTexture__ProbeTexelProfileSample` | Probes profile callback behavior using temporary sample context swap |
| `0x0058864a` | `CDXTexture__InitMappedFileContext` | Initializes mapped-file context fields and decode-open bookkeeping |
| `0x0058865c` | `CDXTexture__OpenMappedFileReadOnly` | Opens mapped file read-only and binds map-view pointers for decode helpers |
| `0x00588cc6` | `CDXTexture__ProjectPointToPlaneAndScale` | Projects 3D point to plane-basis coordinates and scales output for texture-space math |
| `0x005890f1` | `CDXTexture__CpuHasMmxFeature` | CPUID helper returning MMX feature-bit availability |
| `0x00589116` | `CDXTexture__IsMmxEnabledBySystemConfig` | Registry/system-gated MMX enable probe with cached global result |
| `0x00589367` | `CTexture__ReleaseIncludeNodeTreeRecursive` | Recursively releases include-node interfaces and child chains |
| `0x005893d1` | `CTexture__FreeChildIncludeNodeChainRecursive` | Recursively frees child include-node chain through `+0x0c` links |
| `0x005893e9` | `CTexture__IncludeNodeChain_scalar_deleting_dtor` | Scalar-deleting destructor wrapper for include-node chain object |
| `0x00589438` | `CTexture__CleanupIncludeContextRecursive` | Recursive include-context teardown releasing mapped-file/resources and callbacks |
| `0x00589689` | `CTexture__FreeIncludeFileChainRecursive` | Recursively frees include-file chain through `+0x04` links |
| `0x00589cab` | `CTexture__HandleDirective_Include` | Preprocessor `#include` handler with nested-depth guard and source-open dispatch |
| `0x00589e73` | `CTexture__HandleDirective_Error` | Preprocessor `#error` handler with line-continuation folding and diagnostic emit |
| `0x0058b3c7` | `CTexture__ExecuteDirectiveParserAction` | Executes directive-parser reduction actions and preprocessor evaluation stack operations |
| `0x0058b812` | `CTexture__RunDirectiveParser` | Runs table-driven YACC-style directive parser loop and reduction dispatch |
| `0x0058bd25` | `CTexture__InitializePreprocessorStateFromMemorySpan` | Initializes preprocessor state from memory span and seeds base macro definitions |
| `0x0058bd87` | `CTexture__GetNextTokenWithPreprocessor` | Returns next token while applying preprocessor stack/include transitions and directive parsing |
| `0x0058c3fe` | `CTexture__SkipLineContinuationAndAdvance` | Scanner helper that skips escaped newline continuations and advances line counters |
| `0x0058d2ad` | `CTexture__ReadNextLexToken` | Core lexer/token reader that classifies next token and advances source/token metadata state |
| `0x0058c2b9` | `CTexture__AppendDiagnosticTextLine` | Appends formatted diagnostic text lines into the preprocessor/compiler message buffer |
| `0x0058c457` | `CTexture__ParseFloatingLiteral` | Parses float literal text (including exponent form) and optionally emits numeric value |
| `0x0058c5d3` | `CTexture__ParseIdentifierToken` | Parses identifier token text and stores/returns allocated token string |
| `0x0058c652` | `CTexture__ParseOperatorToken` | Parses one/two/three-char operator and punctuator tokens (`==`, `<=`, `>>=`, `##`, etc.) |
| `0x0058d18b` | `CTexture__ParseCharLiteralToken` | Parses single-quoted character literal token and validates closing quote |
| `0x0058d1ca` | `CTexture__ParseStringLiteralToken` | Parses quoted/include-style string token with escape handling and diagnostic checks |
| `0x0058d419` | `CTexture__ParseVertexSemanticUsageToken` | Parses vertex semantic usage token names (`POSITION/NORMAL/TEXCOORD/...`) and usage index |

---

## Function Details

### CDXTexture__LoadTextureFromFile (0x00557300)

**Signature:** `int __thiscall CDXTexture__LoadTextureFromFile(void * this, int texture_slot)` (Wave617)

**Purpose:** Loads a texture from the AYA resource archive system, supporting multiple texture formats and DXT compression.

**Key Behaviors:**
- Constructs resource paths like `data/resources/textures/%s_%d_%s` or `data/resources/dxtntextures/%s`
- Replaces backslashes with `%` in texture names for path construction
- Appends `.aya` extension to resource paths
- Supports texture format selection based on `DAT_009cc134` (32-bit textures flag)
- Uses `OID__AllocObject` to allocate memory (0x500000 bytes at line 0x1a2)
- Handles mip level shifting based on texture quality settings

**Texture Format Switch (at ECX+0x144):**

| Case | D3D Format Code | Format Name |
|------|-----------------|-------------|
| 0 | 0x00 | Unknown/Default |
| 1 | 0x19 | D3DFMT_A1R5G5B5 |
| 2 | 0x1a | D3DFMT_X1R5G5B5 |
| 3 | 0x16 | D3DFMT_A4R4G4B4 |
| 4 | 0x15 | D3DFMT_X4R4G4B4 |
| 5 | 0x17 | D3DFMT_R5G6B5 |
| 6 | 0x31545844 | DXT1 ('DXT1') |
| 7 | 0x32545844 | DXT2 ('DXT2') |
| 8 | 0x34545844 | DXT4 ('DXT4') |
| 9 | 0x3c | D3DFMT_A8 |
| 10 | 0x3f | D3DFMT_L8 |

**String References:**
- `s_mouse_tga_00640058` - Special case for mouse cursor texture
- `s_data_resources_textures_%s_%d_%s_006526e8` - Standard texture path format
- `s_data_resources_textures_mustbe_006526bc` - Required texture path format
- `s_data_resources_dxtntextures_%s_00652710` - DXT compressed texture path

**Called Functions:**
- `FUN_00528af0()` - Texture quality check
- `FUN_00547ec0()` - File open in AYA archive
- `DXMemBuffer__ReadBytes` (`0x00548570`) - Read file data
- `FUN_005758e6()` - Create DirectX texture surface
- `CChunker__CChunker()` / `CChunker__Destructor()` - Memory chunking

---

### CDXTexture__DumpTextureToRGBA (0x005586e0)

**Signature:** `void __thiscall CDXTexture__DumpTextureToRGBA(void * this, char * output_path)` (Wave617)

**Purpose:** Converts a texture to RGBA format for debugging/export purposes. Handles different source pixel formats.

**Key Behaviors:**
- Allocates output buffer: `width * height * 4` bytes (line 0x3a1)
- Reads texture surface data via vtable calls (offsets 0x44, 0x4c, 0x50)
- Converts pixels based on source format

**Pixel Format Conversion:**

| Format Code | Bits/Pixel | Conversion Logic |
|-------------|------------|------------------|
| 0x15, 0x16 | 32-bit | Direct byte extraction (R at byte 0, G at byte 1, B at byte 2) |
| 0x17 | 16-bit RGB565 | R = (val >> 11) << 3, G = (val >> 5) << 2, B = val << 3 |
| 0x19 | 16-bit ARGB1555 | R = (val >> 10) << 3, G = (val >> 5) << 3, B = val << 3 |

**Warning String:** `s_WARNING___Attempt_to_dump_textur_006528ac` - Displayed for unsupported formats

**Called Functions:**
- `OID__AllocObject()` - Allocate RGBA buffer
- `ImageIO__WriteTGA24()` - Write output data (24-bit TGA export)
- `OID__FreeObject()` - Free allocated memory

---

### CDXTexture__CreateMipmaps (0x00559410)

**Signature:** `void __thiscall CDXTexture__CreateMipmaps(void * this, void * chunk_reader, int texture_slot, int mip_count)` (Wave617)

**Purpose:** Generates a complete mipmap chain for a texture, with format conversion support.

**Key Behaviors:**
- Uses `GlobalMemoryStatus()` to check available system memory
- Reduces texture resolution if dimensions exceed `DAT_00888aac` (max width) or `DAT_00888ab0` (max height)
- Creates DirectX texture via `FUN_00513a10()`
- Handles format conversion between ARGB4444 and RGB565

**Debug String:** `s______________lose_res_texture____00652904` - Logged when reducing texture resolution

**Memory Allocations (via OID__AllocObject):**
- Line 0xb7a: Temporary buffer for ARGB4444 to RGB565 conversion
- Line 0xb92: Temporary buffer for format conversion (16-bit)
- Line 0xbbf: Standard mipmap buffer

**Format Conversion Cases:**
1. **ARGB4444 (format 4) to RGB1555 (format 2):** Converts 32-bit ARGB to 16-bit with alpha bit
2. **X4R4G4B4 (format 3) to RGB565 (format 5):** Converts to 16-bit without alpha
3. **Same format:** Direct memory copy with optional downsampling

**Downsampling Algorithm:**
- 2x2 box filter averaging for ARGB formats
- Each component: `(TL + TR + BL + BR) >> 2` with 0x3f3f3f3f mask to prevent overflow

---

### CDXTexture__Deserialize (0x00559be0)

**Signature:** `void * __cdecl CDXTexture__Deserialize(byte use_stream_payload, void * chunk_reader)` (Wave617)

**Purpose:** Main texture loading entry point that deserializes texture data from the AYA archive system.

**Key Behaviors:**
- Allocates 0x158 bytes (344 bytes) for CTexture object (line 0xc25)
- Calls `CTexture__ctor()` to initialize the texture object
- Iterates through all texture surfaces (`puVar3[0x4e]` = surface count)
- Tracks texture size distribution in histogram at `0x9cc058`

**Loading Paths:**
1. **Standard Load (param_1 == 0):** Calls `CDXTexture__LoadTextureFromFile()`
2. **Stream Load (param_1 != 0):** Creates texture directly via `FUN_00513a10()`, falls back to `CDXTexture__CreateMipmaps()` on failure

**Debug Logging:**
- `s_Textures__s_Deserialised___dx_dx_00652970` - Texture load success message
- `s_leaker__00652928` - Memory leak warning
- `s_Warning___Texture__s_in_resource_00652934` - Duplicate texture warning

**Texture Linked List:**
- `DAT_0083d9b0` - Head of global texture list
- Each texture links to next via offset 0x28 (`puVar3[0x28]`)
- Checks for duplicate textures with same name (offset 0x2a for some identifier)

**Exception Handling:**
- Uses structured exception handling with `ExceptionList`
- Unwind handler at `LAB_005d7ddc`

---

### CDXTexture__Deserialize_Unwind (0x005d7dc0)

**Signature:** `void CDXTexture__Deserialize_Unwind(void)`

**Purpose:** Exception unwinding handler for `CDXTexture__Deserialize`. Cleans up memory allocations on exception.

**Key Behaviors:**
- Calls `OID__FreeObject_Callback()` to free the allocated texture object
- Accesses stack frame via `unaff_EBP - 0x168` to get allocation pointer
- Same allocation parameters as Deserialize: type=2, file=DXTexture.cpp, line=0xc25

---

## Data Structures

### CTexture Layout (estimated from offsets)

| Offset | Size | Field | Description |
|--------|------|-------|-------------|
| 0x00 | 4 | vtable/flags | Virtual table or state flags |
| 0x04 | 4 | unknown | |
| 0x08 | 160 | name | Texture name string |
| 0xAC | 4 | width | Texture width |
| 0xB0 | 2 | height | Texture height |
| 0xB2 | 2 | mipShift | Mip level shift count |
| 0xB8 | 32 | surfaces[8] | Direct3D surface pointers |
| 0xA0 | 4 | next | Linked list pointer |
| 0xA4 | 4 | identifier | Texture identifier for duplicate check |
| 0x138 | 4 | surfaceCount | Number of surfaces (0x4E * 4) |
| 0x144 | 4 | format | Internal format enum |
| 0x148 | 4 | type | Texture type |
| 0x150 | 4 | flags | Texture flags |
| 0x154 | 1 | hasDXT | DXT compression flag |
| 0x155 | 1 | qualityFlags | Quality/filtering flags |
| 0x156 | 2 | mipCount | Number of mip levels |

**Total Size:** 0x158 bytes (344 bytes)

---

## Global Variables

| Address | Name | Purpose |
|---------|------|---------|
| `0x009cc058` | TextureSizeHistogram | Array tracking texture sizes (indexed by log2 of width) |
| `0x009cc0e4` | TextureQualitySetting1 | Texture quality level |
| `0x009cc0f4` | TextureQualitySetting2 | Alternative quality setting |
| `0x009cc104` | MipReductionLevel1 | Mip reduction factor |
| `0x009cc114` | MipReductionLevel2 | Alternative mip reduction |
| `0x009cc134` | Force32BitTextures | Flag to force 32-bit texture formats |
| `0x00663064` | UseDXTTextures | Flag to enable DXT compression |
| `0x00888aac` | MaxTextureWidth | Maximum allowed texture width |
| `0x00888ab0` | MaxTextureHeight | Maximum allowed texture height |
| `0x0083d9b0` | TextureListHead | Head of global texture linked list |

---

## Technical Notes

### DXT Compression Support
The engine supports DXT1, DXT2, and DXT4 compression formats (identified by FourCC codes). DXT textures are stored in a separate path (`dxtntextures/`) from regular textures.

### Texture Quality System
Multiple quality settings control texture resolution:
- `DAT_009cc0e4/0f4`: Primary quality settings (0-2)
- `DAT_009cc104/114`: Mip reduction levels
- Textures can be downscaled at load time to save VRAM

### Memory Management
All allocations go through `OID__AllocObject()` with tracking parameters:
- Type: 2 = texture data, 0x61/0x62 = temporary buffers
- Source file and line number for debugging

### Special Cases
- `mouse.tga` texture has special handling (forced to specific format)
- Textures starting with `*` are excluded from duplicate checking
- Frontend textures (`FE_BEA_title_nav_sym`) tracked for leak detection

---

## Semantic Wave75 Promotions (Headless 2026-02-26)

| Address | Symbol | Notes |
|---------|--------|-------|
| 0x0056c70a | CRT__InitLocaleDefaults | Initializes locale defaults from user LCID and seeds CRT locale state. |
| 0x0056c724 | CRT__ResolveLocaleCodePageToken | Resolves `ACP`/`OCP` or explicit codepage token strings into numeric codepage values. |
| 0x0056c78a | CRT__IsCodePageSupportedByLocaleMap | Checks codepage id against CRT locale support/exclusion map. |
| 0x0056c80b | CRT__IsWindowsNtPlatform | Returns true when running on NT-class Windows. |
| 0x0056c841 | CRT__GetLocaleInfoACompatFallback | Compatibility `GetLocaleInfoA` wrapper with CRT fallback table lookup. |
| 0x0056c981 | CRT__StrToLong | Wrapper entry for CRT signed integer parser (`strtol`-style behavior). |
| 0x0056d176 | CRT__IsFiniteDoubleWords | Bitwise finite check for IEEE-754 double word-pair representation. |
| 0x0056d18a | CRT__ClassifyDoubleWords | Classifies IEEE-754 double word-pair into CRT floating class codes. |
| 0x0056e0ec | CRT__UIntToAsciiBase | Converts unsigned integer to ASCII text in caller-selected radix. |
| 0x0056e148 | CRT__UIntToAsciiBase_ReturnBuffer | Wrapper around `CRT__UIntToAsciiBase` returning destination pointer. |

## Semantic Wave76 Promotions (Headless 2026-02-26)

| Address | Symbol | Notes |
|---------|--------|-------|
| 0x0056614c | CRT__SelectHeapStrategy | Chooses CRT heap strategy from OS/version checks and `__MSVCRT_HEAP_SELECT` environment parsing. |
| 0x00566294 | CRT__InitializeHeapSubsystem | Creates process heap, selects strategy, and dispatches heap-subsystem initialization path. |
| 0x005662f1 | CRT__InitSmallBlockHeap | Allocates and initializes small-block heap descriptor table and related globals. |
| 0x00566339 | CRT__FindSmallBlockHeapEntryForPtr | Scans small-block heap region records and returns the matching entry for a pointer range. |
| 0x00569449 | CRT__ControlFp | Applies floating-point control-word mask/update (`(old & ~mask) | (new & mask)`) and writes back state. |
| 0x0056aff4 | CRT__AllocOsHandleSlot | Allocates/initializes a lowio slot entry and returns its handle index. |
| 0x0056b117 | CRT__SetOsHandle | Stores OS handle into a lowio slot and updates std handle aliases for slots 0/1/2. |
| 0x0056b193 | CRT__FreeOsHandle | Releases lowio slot handle state and clears std handle aliases for slots 0/1/2. |
| 0x0056cbb4 | CRT__EnsureTzsetInitialized | One-time lock-gated wrapper that ensures timezone globals are initialized. |
| 0x0056cbe2 | CRT__Tzset | Populates timezone/daylight globals from `TZ` env string or Win32 `GetTimeZoneInformation` fallback. |
