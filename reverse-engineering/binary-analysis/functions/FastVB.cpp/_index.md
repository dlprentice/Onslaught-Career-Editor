# FastVB.cpp - Fast Vertex Buffer System

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 semantic revalidation:** `0x00578bad` comment correction; `0x00584724` comment correction; `0x0059be00` comment correction; `0x005a9637` comment correction. Older conflicting text below is superseded for these rows. Use the [closeout](../../ghidra-full-reaudit-closeout-2026-07-13.md); exact records are in `reverse-engineering/binary-analysis/ghidra-full-reaudit-corrections-2026-07-13.json` and `reverse-engineering/binary-analysis/ghidra-targeted-revalidation-corrections-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Wave1214 math/color/screen dispatch current-risk review (`wave1214-math-color-screen-dispatch-current-risk-review`) re-read the cross-owner transform dispatch callers around `CFastVB__BuildTransformMatrixWithOffsets` and the Math dispatch thunk `Math__BuildQuaternionRotationMatrix_Dispatch_Thunk`. The static callsite context keeps the FastVB transform-matrix bridge tied to CPU-selected math dispatch without changing any saved name, signature, comment, tag, function boundary, or executable byte. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260607-081942_post_wave1214_math_color_screen_dispatch_current_risk_review_verified`. Runtime CPU dispatch, exact FastVB/math layout, runtime render/math behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.

Wave1181 current-risk update: Wave1181 (`wave1181-cfastvb-residual-math-dispatch-trig-current-risk-review`) accounts for `21 CFastVB residual math/dispatch/trig current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator with fresh Ghidra export evidence. It is a read-only review with no mutation, no rename, no signature change, no comment change, no tag change, no function-boundary change, and no executable-byte change. Codex read-only consults used; Codex root final judgment kept the exact residual CFastVB slice. No Cursor/Composer was used. Static closure remains `6411/6411 = 100.00%` with static debt `0 / 0 / 0`; Wave1108 current focused accounting is now `750/1179 = 63.61%`; current risk candidates: 6166; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 429; focused threshold `15`; not Wave911 reconstruction. Fresh exports verified `40 xref rows` and `2013 instruction rows`. Static anchors include `CFastVB__HermiteInterpolateVec3`, `CFastVB__BuildTransformMatrixWithOffsets`, `CFastVB__SolveScalarEndpointPairFromSamples`, `CFastVB__DispatchOp_TransformVec2ArrayByMatrix4_WithTranslation_005a3a40`, `CFastVB__DispatchOp_BuildQuaternionFromMatrix3x3_Packed_005a4836`, `CFastVB__DispatchOp_SlotB0_005a4fee`, `CFastVB__FastTrigPairApprox_Scalar`, and `CFastVB__FastSinApprox_Scalar_005b8da0`; prior provenance spans Wave969, Wave970, Wave971, Wave737, Wave887, Wave888, and Wave701. Caveats preserved for rebuild-grade static contracts: hidden EBX, unreliable packed-register return, `0x005a4980 internal branch target`, exact dispatch-table schema, vector/matrix/quaternion concrete layouts, hidden ABI completeness, runtime math/render proof, exact source-body identity, BEA patching behavior, visual QA, gameplay outcomes, and rebuild parity remain separate proof. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260606-111618_post_wave1181_cfastvb_residual_current_risk_review_verified`. Static clean-room target: preserve rebuild-grade static contracts for a future clean-room implementation aiming at no noticeable difference. Probe token anchor: Wave1181; wave1181-cfastvb-residual-math-dispatch-trig-current-risk-review; 750/1179 = 63.61%; 21 CFastVB residual math/dispatch/trig current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 429; current risk candidates: 6166; fresh Ghidra export; read-only review; no mutation; no rename; no signature change; no comment change; no tag change; no function-boundary change; no executable-byte change; Codex read-only consults used; Codex root final judgment; no Cursor/Composer; residual CFastVB; hidden EBX; unreliable packed-register return; 0x005a4980 internal branch target; Wave969; Wave970; Wave971; Wave737; Wave887; Wave888; Wave701; 0 / 0 / 0; 6411/6411 = 100.00%; 40 xref rows; 2013 instruction rows; CFastVB__HermiteInterpolateVec3; CFastVB__BuildTransformMatrixWithOffsets; CFastVB__SolveScalarEndpointPairFromSamples; CFastVB__DispatchOp_TransformVec2ArrayByMatrix4_WithTranslation_005a3a40; CFastVB__DispatchOp_BuildQuaternionFromMatrix3x3_Packed_005a4836; CFastVB__DispatchOp_SlotB0_005a4fee; CFastVB__FastTrigPairApprox_Scalar; CFastVB__FastSinApprox_Scalar_005b8da0; [maintainer-local-ghidra-backup-root]\BEA_20260606-111618_post_wave1181_cfastvb_residual_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction; rebuild-grade static contracts; no noticeable difference.

Wave1173 current-risk update: Wave1173 (`wave1173-cfastvb-strip-candidate-current-risk-review`) accounts for `3 CFastVB strip-candidate current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator with fresh Ghidra export evidence. It is a read-only review with no mutation and Codex read-only consult spawned. Static anchors are `CFastVB__TriangleListContainsVertexTriplet_0056ff40`, `CFastVB__InsertStripCandidatesIntoBuffer_005708a0`, and `CFastVB__InitializeCandidateParentLinks_00570be0`. Static closure remains `6411/6411 = 100.00%` with static debt `0 / 0 / 0`; current focused candidates: 1178; live regenerated current focused candidates: 1178; Wave1108 current focused accounting is `675/1179 = 57.25%`; remaining active focused work: 504; current risk candidates: 6166; fresh Ghidra export; read-only review; no mutation; `3 xref rows`; `339 instruction rows`; verified backup `[maintainer-local-ghidra-backup-root]\BEA_20260606-073137_post_wave1173_cfastvb_strip_candidate_current_risk_review_verified`; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction. Runtime strip quality, concrete D3D index-buffer/render output, exact CFastVB/strip-candidate/span/triangle-record layouts, exact source-body identity, BEA patching behavior, visual QA, gameplay outcomes, and rebuild parity remain separate proof.

Wave1165 current-risk update: Wave1165 (`wave1165-cfastvb-dispatch-slot-tail-current-risk-review`) accounts for `21 CFastVB dispatch-slot tail current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator with fresh Ghidra export evidence. It is a read-only review with no mutation, no rename, no signature change, no comment/tag change, no function-boundary change, no executable-byte change, no BEA launch, no installed-game mutation, no save mutation, and no runtime-file mutation. Codex read-only consult used; Codex root made the final judgment. Static closure remains `6411/6411 = 100.00%` with static debt `0 / 0 / 0`; expanded post-100 static surface remains `1560/1560 = 100.00%`; Wave911 focused is historical-retired/non-reconstructable at `812/1408 = 57.67%`; Wave911 top-500 remains `500/500 = 100.00%`; Wave1108 current focused accounting is now `604/1179 = 51.23%`; current risk candidates: 6166; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 575; focused threshold `15`; not Wave911 reconstruction. Fresh exports verified `21 xref rows` and `1417 instruction rows`. Static anchors include `CFastVB__DispatchOp_SlotA4_005a77bc`, `CFastVB__DispatchOp_Slot10_005a923f`, `CFastVB__DispatchOp_SlotCC_005a9abe`, `CFastVB__DispatchOp_SlotC0_005aa8c5`, `CFastVB__DispatchOp_SlotD8_005aac0f`, and `CFastVB__DispatchOp_Slot58_005aaf4d`, all DATA-referenced from `CFastVB__InitDispatchOpsFromFeatureFlags`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260606-040830_post_wave1165_cfastvb_dispatch_slot_tail_current_risk_review_verified`. Runtime CPU dispatch/math/render behavior, exact dispatch-table slot schema, hidden MMX/SSE/register/stack ABI completeness, exact source-body identity, BEA patching behavior, visual QA, gameplay outcomes, and rebuild parity remain separate proof. Probe token anchor: Wave1165; wave1165-cfastvb-dispatch-slot-tail-current-risk-review; 604/1179 = 51.23%; 21 CFastVB dispatch-slot tail current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 575; current risk candidates: 6166; fresh Ghidra export; read-only review; no mutation; Codex read-only consult used; 0 / 0 / 0; 6411/6411 = 100.00%; 21 xref rows; 1417 instruction rows; CFastVB__DispatchOp_SlotA4_005a77bc; CFastVB__DispatchOp_Slot10_005a923f; CFastVB__DispatchOp_SlotCC_005a9abe; CFastVB__DispatchOp_SlotC0_005aa8c5; CFastVB__DispatchOp_SlotD8_005aac0f; CFastVB__DispatchOp_Slot58_005aaf4d; CFastVB__InitDispatchOpsFromFeatureFlags; [maintainer-local-ghidra-backup-root]\BEA_20260606-040830_post_wave1165_cfastvb_dispatch_slot_tail_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.

Wave1163 current-risk update: Wave1163 (`wave1163-texture-node-tree-inflate-huffman-current-risk-review`) accounts for `17 CFastVB/CTexture/CDXTexture current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator with fresh Ghidra export evidence. It is a read-only review with no mutation, no rename, no signature change, no comment/tag change, no function-boundary change, no executable-byte change, no BEA launch, no installed-game mutation, no save mutation, and no runtime-file mutation. Static closure remains `6411/6411 = 100.00%` with static debt `0 / 0 / 0`; expanded post-100 static surface remains `1560/1560 = 100.00%`; Wave911 focused is historical-retired/non-reconstructable at `812/1408 = 57.67%`; Wave911 top-500 remains `500/500 = 100.00%`; Wave1108 current focused accounting is now `564/1179 = 47.84%`; current risk candidates: 6166; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 615; focused threshold `15`; not Wave911 reconstruction. Fresh exports verified `68 xref rows` and `2779 instruction rows`. Static anchors include `CTexture__NodePayloadRecordCtor`, `CFastVB__NodeType9__ctor`, `CDXTexture__NodeType13__ctor`, `CDXTexture__RegisterSerializedChunk`, `CFastVB__AreNodeTreesCompatible`, `CFastVB__SelectBestNodeTreeMatch`, `CTexture__LoadDefaultHuffmanTables`, `CDXTexture__InflateStream_ProcessZlibState`, `CDXTexture__BuildInflateHuffmanTable`, and `CDXTexture__FlushEntropyBitWriter`. JPEG Huffman separate from inflate Huffman is an explicit static map boundary. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260606-025611_post_wave1163_texture_node_tree_inflate_huffman_current_risk_review_verified`. Runtime parser behavior, runtime texture decode behavior, runtime JPEG behavior, runtime inflate/decompression behavior, exact node-tree/payload/chunk/z_stream/Huffman-table/entropy-writer layouts, hidden ABI completeness, exact source-body identity, BEA patching behavior, visual QA, gameplay outcomes, and rebuild parity remain separate proof. Current system contract: `texture-resource-decode-static-contract.md`. Probe token anchor: Wave1163; wave1163-texture-node-tree-inflate-huffman-current-risk-review; 564/1179 = 47.84%; 17 CFastVB/CTexture/CDXTexture current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 615; current risk candidates: 6166; fresh Ghidra export; read-only review; no mutation; 0 / 0 / 0; 6411/6411 = 100.00%; 68 xref rows; 2779 instruction rows; CTexture__NodePayloadRecordCtor; CFastVB__NodeType9__ctor; CDXTexture__NodeType13__ctor; CDXTexture__RegisterSerializedChunk; CFastVB__AreNodeTreesCompatible; CFastVB__SelectBestNodeTreeMatch; CTexture__LoadDefaultHuffmanTables; CDXTexture__InflateStream_ProcessZlibState; CDXTexture__BuildInflateHuffmanTable; CDXTexture__FlushEntropyBitWriter; JPEG Huffman separate from inflate Huffman; [maintainer-local-ghidra-backup-root]\BEA_20260606-025611_post_wave1163_texture_node_tree_inflate_huffman_current_risk_review_verified; texture-resource-decode-static-contract.md; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.

**Source File:** `[maintainer-local-source-export-root]\FastVB.cpp`
**Debug String Address:** `0x0063fb24`
**Functions Found:** 5 (+ 2 exception unwind handlers)

## Overview

Wave1155 CFastVB Wave717-Wave722 current-risk supersession (`wave1155-cfastvb-wave717-722-current-risk-supersession`) accounts for 46 current-risk rows from Wave1108 as superseded by prior Wave717-Wave722 saved Ghidra read-back evidence. Representative anchors include `0x0059f360 CFastVB__DispatchOp_TransformVec4_0059f360`, `0x005a0b22 CFastVB__ConvertHalfToFloatArray_SSE`, `0x005a298f CFastVB__ConvertHalfToFloatArray_SIMD`, `0x005a47f2 CFastVB__DispatchOp_ExtractAxisAndOptionalAngle`, `0x005a62bf CFastVB__DispatchOp_InitIdentityMatrix4x4_005a62bf`, and `0x005ab00b CFastVB__DispatchOp_NormalizeQuaternionPacked_005ab00b`. It is no new Ghidra export and no mutation; Codex read-only consult used. Accounting source is `wave1108-current-risk-rank`: current risk candidates: 6166; current focused candidates: 1178; live regenerated current focused candidates: 1178; focused threshold `15`; current-risk denominator remains `1179`; progress moves to `424/1179 = 35.96%`; remaining active focused work: 755; this is not Wave911 reconstruction. Static Ghidra function-quality closure remains `6411/6411 = 100.00%`; commentless / undefined / `param_N` debt remains `0 / 0 / 0`. Prior evidence backups include `[maintainer-local-ghidra-backup-root]\BEA_20260522-021449_post_wave717_cfastvb_transform_dispatch_head_verified` and `[maintainer-local-ghidra-backup-root]\BEA_20260522-050258_post_wave722_cfastvb_packed_vec2_quaternion_tail_verified`; latest completed Ghidra review backup remains `[maintainer-local-ghidra-backup-root]\BEA_20260605-215410_post_wave1154_unitai_deploy_target_current_risk_review_verified`. Runtime math/render correctness, hidden ABI completeness, exact layouts, source identity, patching behavior, gameplay outcomes, visual QA, and rebuild parity remain separate proof.
> **Queue status (2026-05-26):** Ghidra export-contract closure **6113/6113** (Wave900: every function commented; clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

CFastVB is a fast vertex buffer class designed for rendering dynamic quads (sprites, particles, UI elements). It uses a dynamic vertex buffer with an associated index buffer for efficient batched quad rendering.

Wave1071 (`texel-unpack-head-mid-review-wave1071`) re-read the FastVB-owned portion of the Wave672/Wave673 texel-unpack head/middle table with no mutation, including `0x00584d78 CFastVB__UnpackTexels_Bits565ToFloat4`, `0x00584e32 CFastVB__UnpackTexels_Bits555ToFloat4_AlphaOne`, `0x00585072 CFastVB__UnpackTexels_Bits2_10_10_10_ToFloat4`, `0x0058577f CFastVB__TexelUnpackProfile_005e9f3c__ctor`, `0x00585bd3 CFastVB__TexelUnpackProfile_scalar_deleting_dtor`, and `0x00585fa3 CFastVB__UnpackTexels_Signed8_8_8_8_ToFloat4`. Fresh metadata/tags/xrefs/instructions/decompile evidence preserves DATA-slot texel profile coherence and constructor/destructor table context. Queue closure remains `6246/6246 = 100.00%`; expanded static surface progress advances to `1319/1560 = 84.55%`; verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260602-031627_post_wave1071_texel_unpack_head_mid_review_verified`. Runtime texture output behavior, runtime codec/FourCC behavior, exact profile/descriptor/layout identity, exact source identity, BEA patching, gameplay outcomes, and rebuild parity remain separate proof.

Wave1070 (`texel-unpack-tail-review-wave1070`) re-read five FastVB-owned texel profile, callback, L16A16, flush, and row-window codec rows with no mutation: `0x0058609e CFastVB__TexelUnpackProfile_005ea020__ctor`, `0x005866d2 CFastVB__UnpackTexels_CallbackPerTexel_Stride4_SetZAOne`, `0x005868d1 CFastVB__UnpackTexels_L16A16_ToFloat4`, `0x00586bb7 CFastVB__FlushPendingConvertedRows16`, and `0x00586f37 CFastVB__DecodeRowWindowToScratchPairs`. Fresh metadata/tags/xrefs/instructions/decompile evidence preserves the Wave674/Wave675 treatment, including DATA-slot context for the callbacks and direct callgraph context from `CFastVB__DecodeRowWindowToScratchPairs` to `CFastVB__FlushPendingConvertedRows16`. Queue closure remains `6246/6246 = 100.00%`; expanded static surface progress advances to `1278/1560 = 81.92%`; verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260602-022701_post_wave1070_texel_unpack_tail_review_verified`. Runtime texture output behavior, runtime codec/FourCC behavior, exact profile/descriptor/row-window layouts, exact source identity, BEA patching, gameplay outcomes, and rebuild parity remain separate proof.

Wave1057 math dispatch thunk review (`math-dispatch-thunk-review-wave1057`) re-read the adjacent math/CFastVB dispatch island with no mutation. CFastVB-side anchors include `0x0057798e CFastVB__BuildAxisAngleQuaternion_Dispatch` and the dispatch-table context `CFastVB__InitDispatchTableByCpuFeature`, `CFastVB__InitMathDispatchTable`, `CFastVB__InitDispatchTableVariant_005980be`, and `CFastVB__InitDispatchOpsFromFeatureFlags`; companion Math anchors include `0x005771af Math__BuildScaleMatrix4x4_Dispatch`, `0x005771dd Math__BuildScaleMatrix4x4`, `0x00577239 Math__BuildTranslationMatrix4x4_Dispatch`, `0x005775c3 Math__BuildQuaternionRotationMatrix`, `0x00577a3e Math__BuildQuaternionFromEulerAngles`, and `0x00577eaa Math__InterpolateVec4ByRatio`. Queue closure remains `6246/6246 = 100.00%`; Wave911 focused progress is `799/1408 = 56.75%`; expanded static surface progress is `1121/1509 = 74.29%`; top-500 coverage is `500/500 = 100.00%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260601-184232_post_wave1057_math_dispatch_thunk_review_verified`. Exact dispatch-table slot schema, exact vector/matrix/quaternion/ratio/lane-order/storage layouts, runtime CPU feature selection, runtime math/render correctness, exact source-body identity, BEA patching, gameplay outcomes, and rebuild parity remain separate proof. Probe token anchor: Wave1057; math-dispatch-thunk-review-wave1057; 0x005771af Math__BuildScaleMatrix4x4_Dispatch; 0x005771dd Math__BuildScaleMatrix4x4; 0x00577239 Math__BuildTranslationMatrix4x4_Dispatch; 0x005775c3 Math__BuildQuaternionRotationMatrix; 0x0057798e CFastVB__BuildAxisAngleQuaternion_Dispatch; 0x00577a3e Math__BuildQuaternionFromEulerAngles; 0x00577eaa Math__InterpolateVec4ByRatio; CFastVB__InitDispatchTableByCpuFeature; CFastVB__InitMathDispatchTable; CFastVB__InitDispatchTableVariant_005980be; CFastVB__InitDispatchOpsFromFeatureFlags; 799/1408 = 56.75%; 1121/1509 = 74.29%; 500/500 = 100.00%; 6246/6246 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260601-184232_post_wave1057_math_dispatch_thunk_review_verified; no mutation.

Wave1055 CFastVB residual dispatch review (`cfastvb-residual-dispatch-review-wave1055`) re-read twenty-six existing CFastVB vector, quaternion, matrix, and alternate batch dispatch helpers with no mutation. Representative anchors include `0x0059f360 CFastVB__DispatchOp_TransformVec4_0059f360`, `0x0059f3d9 CFastVB__DispatchOp_NormalizeVec4_0059f3d9`, `0x005a16b1 CFastVB__DispatchOp_TransformVec3ByMatrix4_005a16b1`, `0x005a225f CFastVB__DispatchOp_TransformVec4Batch_Perspective_Alt_005a225f`, `0x005a2ee9 CFastVB__DispatchOp_Determinant4x4_005a2ee9`, `0x005a3508 CFastVB__DispatchOp_BuildMatrix4FromQuaternionPair_005a3508`, and `0x005a3791 CFastVB__DispatchOp_BuildQuaternionFromMatrix3x3_005a3791`. Fresh primary exports verified `26` metadata rows, `26` tag rows, `50` xref rows, `2277` function-body instruction rows, and `26` decompile rows; context exports verified `12` metadata rows, `12` tag rows, `45` xref rows, `2263` instruction rows, and `12` decompile rows. Context anchors include `CFastVB__InitDispatchTableVariant_005980be`, `CFastVB__InitDispatchTableVariant_0059822c`, `CFastVB__InitDispatchOpsFromFeatureFlags`, `CFastVB__BroadcastMatrix4x4ToSIMDLanes`, `CFastVB__DispatchOp_WeightedMatrixBlendBatch_005a04a0`, `CFastVB__EvaluateCubicBasisVec3`, `CFastVB__DispatchOp_TransformVec4ArrayByMatrix4`, `CFastVB__DispatchOp_InterpolateQuaternionPairCore_005a4d98`, `CFastVB__DispatchOp_NormalizeQuaternionWithAcosFallback_005a5052`, `CFastVB__DispatchOp_ComposeTransformFromOptionalInputs_Core_005a647f`, `CFastVB__DispatchOp_InvertMatrix4x4_WithDeterminant_005a8f5d`, and `CFastVB__DispatchOp_MultiplyMatrix4x4_Packed_005a9d78`. Queue closure remains `6246/6246 = 100.00%`; Wave911 focused progress remains `769/1408 = 54.62%`; expanded static surface progress advances to `1091/1509 = 72.30%`; top-500 coverage remains `500/500 = 100.00%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260601-173102_post_wave1055_cfastvb_residual_dispatch_review_verified`, `19` files, `174656391` bytes, `DiffCount=0`, `HashDiffCount=0`. Exact dispatch-table slot schema, vector/matrix/quaternion/stride/lane-order layouts, hidden EBX/EDI/XMM/MMX/stack ABI completeness, runtime CPU feature selection, runtime math/render correctness, exact source-body identity, BEA patching, gameplay outcomes, and rebuild parity remain separate proof. Probe token anchor: Wave1055; cfastvb-residual-dispatch-review-wave1055; 0x0059f360 CFastVB__DispatchOp_TransformVec4_0059f360; 0x0059f3d9 CFastVB__DispatchOp_NormalizeVec4_0059f3d9; 0x005a16b1 CFastVB__DispatchOp_TransformVec3ByMatrix4_005a16b1; 0x005a225f CFastVB__DispatchOp_TransformVec4Batch_Perspective_Alt_005a225f; 0x005a2ee9 CFastVB__DispatchOp_Determinant4x4_005a2ee9; 0x005a3508 CFastVB__DispatchOp_BuildMatrix4FromQuaternionPair_005a3508; 0x005a3791 CFastVB__DispatchOp_BuildQuaternionFromMatrix3x3_005a3791; CFastVB__InitDispatchTableVariant_005980be; CFastVB__InitDispatchTableVariant_0059822c; CFastVB__BroadcastMatrix4x4ToSIMDLanes; 769/1408 = 54.62%; 1091/1509 = 72.30%; 500/500 = 100.00%; 6246/6246 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260601-173102_post_wave1055_cfastvb_residual_dispatch_review_verified; no mutation.

Wave1110 (`wave1110-cfastvb-wave1053-remainder-supersession`) accounts for 9 rows from the Wave1108 current focused candidates as superseded by Wave1053 (`cfastvb-stacklocked-transform-review-wave1053`) static read-back evidence. Covered anchors include `0x0059f857 CFastVB__DispatchOp_TransformVec4Batch_0059f857`, `0x0059fa5d CFastVB__DispatchOp_TransformVec4BatchW_0059fa5d`, `0x0059fbeb CFastVB__DispatchOp_TransformProjectVec4Batch_0059fbeb`, `0x0059fd51 CFastVB__DispatchOp_TransformVec4Batch_NoOffset_0059fd51`, `0x0059fe61 CFastVB__DispatchOp_TransformVec4Batch_Perspective_0059fe61`, `0x005a009f CFastVB__DispatchOp_TransformVec3WBatch_005a009f`, `0x005a026f CFastVB__DispatchOp_TransformProjectVec3WBatch_005a026f`, `0x005a04a0 CFastVB__DispatchOp_WeightedMatrixBlendBatch_005a04a0`, and `0x005a7617 CFastVB__DispatchOp_BuildRotationMatrixFromEulerAngles`. current focused candidates: 1179; supersession progress is `24/1179 = 2.04%`. This is no new Ghidra export and no mutation. Wave1053 backup: `[maintainer-local-ghidra-backup-root]\BEA_20260601-162015_post_wave1053_cfastvb_stacklocked_transform_review_verified`. Latest completed Ghidra backup remains `[maintainer-local-ghidra-backup-root]\BEA_20260604-200748_post_wave1100_cmeshpart_load_geometry_review_verified`.

Wave1109 (`wave1109-cfastvb-current-risk-head-supersession`) accounts for the first fifteen Wave1108 current focused candidates as superseded by Wave1053 static read-back evidence. Covered anchors include `0x005a0f50 CFastVB__EvaluateCubicBasisVec3`, `0x005a1002 CFastVB__EvaluateCubicBasisVec2`, `0x005a1087 CFastVB__EvaluateCubicBasisVec4`, `0x005a112c CFastVB__DispatchOp_CubicBlendVec3_005a112c`, `0x005a38c0 CFastVB__DispatchOp_TransformVec4ArrayByMatrix4`, `0x005a4ecf CFastVB__DispatchOp_BlendQuaternionTriple_005a4ecf`, `0x005a647f CFastVB__DispatchOp_ComposeTransformFromOptionalInputs_Core_005a647f`, and `0x005a7e09 CFastVB__DispatchOp_ComposeMatrixFromOptionalTransforms`. current focused candidates: 1179; supersession progress is `15/1179 = 1.27%`. This is no new Ghidra export and no mutation. Wave1053 backup: `[maintainer-local-ghidra-backup-root]\BEA_20260601-162015_post_wave1053_cfastvb_stacklocked_transform_review_verified`. Latest completed Ghidra backup remains `[maintainer-local-ghidra-backup-root]\BEA_20260604-200748_post_wave1100_cmeshpart_load_geometry_review_verified`.

Wave1053 CFastVB stack-locked transform review (`cfastvb-stacklocked-transform-review-wave1053`) re-read twenty-four existing transform, curve, quaternion, and optional-composition dispatch helpers with no mutation. Primary anchors include `0x0059f857 CFastVB__DispatchOp_TransformVec4Batch_0059f857`, `0x005a04a0 CFastVB__DispatchOp_WeightedMatrixBlendBatch_005a04a0`, `0x005a0f50 CFastVB__EvaluateCubicBasisVec3`, `0x005a13f7 CFastVB__DispatchOp_InterpolateVec3ByReciprocal_005a13f7`, `0x005a38c0 CFastVB__DispatchOp_TransformVec4ArrayByMatrix4`, `0x005a519e CFastVB__DispatchOp_BlendQuaternionSplineSegment_005a519e`, `0x005a647f CFastVB__DispatchOp_ComposeTransformFromOptionalInputs_Core_005a647f`, `0x005a7617 CFastVB__DispatchOp_BuildRotationMatrixFromEulerAngles`, and `0x005a7e09 CFastVB__DispatchOp_ComposeMatrixFromOptionalTransforms`. Fresh primary exports verified `24` metadata rows, `24` tag rows, `34` DATA xref rows, `4682` function-body instruction rows, and `24` decompile rows; context exports verified `12` metadata rows, `12` tag rows, `49` xref rows, `949` instruction rows, and `12` decompile rows. Incoming DATA refs still tie the targets to `CFastVB__InitDispatchTableVariant_005980be`, `CFastVB__InitDispatchTableVariant_0059822c`, or `CFastVB__InitDispatchOpsFromFeatureFlags`. Queue closure remains `6246/6246 = 100.00%`; Wave911 focused progress advances to `769/1408 = 54.62%`; expanded static surface progress advances to `1057/1509 = 70.05%`; top-500 coverage remains `500/500 = 100.00%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260601-162015_post_wave1053_cfastvb_stacklocked_transform_review_verified`. The old stack-locked `int ...(void)` signatures remain intentional bounded signatures where hidden stack/register ABI is still not represented exactly. Exact dispatch-table slot schema, vector/matrix/quaternion/stride/lane-order layouts, hidden EBX/EDI/XMM/MMX/stack ABI completeness, runtime CPU feature selection, runtime math/render correctness, exact source-body identity, BEA patching, gameplay outcomes, and rebuild parity remain separate proof. Probe token anchor: Wave1053; cfastvb-stacklocked-transform-review-wave1053; 0x0059f857 CFastVB__DispatchOp_TransformVec4Batch_0059f857; 0x005a04a0 CFastVB__DispatchOp_WeightedMatrixBlendBatch_005a04a0; 0x005a0f50 CFastVB__EvaluateCubicBasisVec3; 0x005a13f7 CFastVB__DispatchOp_InterpolateVec3ByReciprocal_005a13f7; 0x005a38c0 CFastVB__DispatchOp_TransformVec4ArrayByMatrix4; 0x005a519e CFastVB__DispatchOp_BlendQuaternionSplineSegment_005a519e; 0x005a647f CFastVB__DispatchOp_ComposeTransformFromOptionalInputs_Core_005a647f; 0x005a7617 CFastVB__DispatchOp_BuildRotationMatrixFromEulerAngles; 0x005a7e09 CFastVB__DispatchOp_ComposeMatrixFromOptionalTransforms; CFastVB__InitDispatchTableVariant_005980be; CFastVB__InitDispatchTableVariant_0059822c; CFastVB__InitDispatchOpsFromFeatureFlags; 769/1408 = 54.62%; 1057/1509 = 70.05%; 500/500 = 100.00%; 6246/6246 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260601-162015_post_wave1053_cfastvb_stacklocked_transform_review_verified; no mutation.

Wave1025 CFastVB node-tree review (`cfastvb-node-tree-review-wave1025`) re-read CFastVB/CDXTexture/CTexture parser node-tree, serialized-chunk, selector, and strip-selection residual rows with no mutation. It confirmed `0x0056ff40 CFastVB__TriangleListContainsVertexTriplet_0056ff40`, `0x00570be0 CFastVB__InitializeCandidateParentLinks_00570be0`, `0x00598a81 CFastVB__NodeType9__ctor`, `0x0059902a CDXTexture__RegisterSerializedChunk`, `0x00599d80 CFastVB__FlattenNodeTreeLeafByLinearIndex`, `0x0059a54d CFastVB__ScoreNodeTreeMatch`, and `0x0059a71a CFastVB__SelectBestNodeTreeMatch` without changing saved metadata. The selector remains a hidden-ECX/stack-ABI hub; call windows at `0x00599349` and `0x00599576` plus RET `0x20` support the current bounded treatment, not a forced prototype. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260601-004522_post_wave1025_cfastvb_node_tree_review_verified`. Runtime shader/parser/texture behavior, exact node-tree/payload/binding-chain/serialized-chunk layouts, exact source-body identity, BEA patching, and rebuild parity remain separate proof.

Wave1120 (`wave1120-mixed-score25-current-risk-review`) re-read `0x00599d80 CFastVB__FlattenNodeTreeLeafByLinearIndex` from the current-risk queue with a fresh read-only Ghidra export and no mutation. Fresh xrefs keep the helper tied to `CFastVB__ScoreNodeTreePairMismatchBits` and `CFastVB__AreNodeTreesCompatible`; decompile evidence still walks wrapper kinds `1`, `5`, `7`, and `10`, descends to leaf kind `8`, writes normalized leaf scratch fields, and returns `0` or `0x80004005`. Current focused accounting moves to `118/1179 = 10.01%`; verified backup `[maintainer-local-ghidra-backup-root]\BEA_20260605-025952_post_wave1120_mixed_score25_current_risk_review_verified`. Runtime FastVB parser/render behavior, exact node-tree/payload layout, source identity, BEA patching, gameplay outcomes, and rebuild parity remain separate proof.

Wave895 decode feature tail (`decode-feature-tail-wave895`, `wave895-readback-verified`) saved comments/tags for nine raw commentless CFastVB/CTexture/CDXTexture decode-feature rows. Probe token anchor: Wave895 decode feature tail; decode-feature-tail-wave895; 0x00598390 CFastVB__DetectCpuFeatureMask; 0x0059a71a CFastVB__SelectBestNodeTreeMatch; 0x0059b150 CTexture__InitDecodeLookupScratchTables; 0x0059b1d0 CTexture__InitializeDecodePipelineFromHeader; 0x0059b510 CDXTexture__ValidateJpegFrameAndBuildScanLayout; 0x0059b6f0 CTexture__BuildComponentPlaneLayoutTables; 0x0059b880 CTexture__EnsureComponentDecodeScratchBlocks; 0x0059be00 CDXTexture__CreateDecodeJobDescriptor; 0x0059be70 CDXTexture__AllocDecodeBlockAndLink; 0x0059c610 CFastVB__ReleaseOwnedObjectAndReset_Core; 6086/6113 = 99.56%; [maintainer-local-ghidra-backup-root]\BEA_20260526-064920_post_wave895_decode_feature_tail_verified. Static evidence ties the CFastVB-owned portion to CPUID feature-mask detection for `CFastVB__InitDispatchOpsFromFeatureFlags` and the Wave709-deferred `CFastVB__SelectBestNodeTreeMatch` selector reached from texture/shader parser validation and binding emission. Exact feature-bit names, SIMD dispatch semantics, node-tree layout, compatibility-score semantics, hidden register/stack ABI completeness, runtime parser/texture/JPEG/image decode behavior, BEA patching, and rebuild parity remain deferred.

Wave896 decode cleanup tail (`decode-cleanup-tail-wave896`, `wave896-readback-verified`) saved comments/tags for `0x0059c610 CFastVB__ReleaseOwnedObjectAndReset_Core`. Probe token anchor: Wave896 decode cleanup tail; decode-cleanup-tail-wave896; 0x0059c610 CFastVB__ReleaseOwnedObjectAndReset_Core; 0x0059ccb3 CDXTexture__FreeDecodeStateIfOwnerPresent; 0x005a09f8 CFastVB__ConvertHalfToFloat8_SIMDKernel; 6088/6113 = 99.59%; [maintainer-local-ghidra-backup-root]\BEA_20260526-071320_post_wave896_decode_cleanup_tail_verified. Static evidence ties the row to the `0x00591050 CFastVB__ReleaseOwnedObjectAndReset` tail-jump and `0x00592b00 CFastVB__ParserContext_Shutdown`; the body calls vfunc `+0x28` when `decode_state_header+0x04` is non-null, then clears fields `+0x04` and `+0x14`. Exact owner object layout, vtable method identity, runtime parser/decode cleanup behavior, BEA patching, and rebuild parity remain deferred.

Wave897 CFastVB SIMD transform tail (`cfastvb-simd-transform-tail-wave897`, `wave897-readback-verified`) saved comments/tags for nine raw commentless CFastVB SIMD transform and half-float conversion rows from `0x005a09f8 CFastVB__ConvertHalfToFloat8_SIMDKernel` through `0x005a289e CFastVB__ConvertHalfToFloat8_CheckSpecialCasesSIMD`. Probe token anchor: Wave897 CFastVB SIMD transform tail; cfastvb-simd-transform-tail-wave897; 0x005a09f8 CFastVB__ConvertHalfToFloat8_SIMDKernel; 0x005a1c55 CFastVB__DispatchOp_TransformVec4Batch_Alt_005a1c55; 0x005a266d CFastVB__TransformProjectVec3ByMatrix4_Batch4; 0x005a289e CFastVB__ConvertHalfToFloat8_CheckSpecialCasesSIMD; 0x005a9f44 CFastVB__DispatchOp_ComposeTransformAndProjectVec3_005a9f44; 6097/6113 = 99.74%; [maintainer-local-ghidra-backup-root]\BEA_20260526-074111_post_wave897_cfastvb_simd_transform_tail_verified. Static evidence ties the rows to `CFastVB__InitDispatchTableVariant_0059822c` DATA xrefs, `CFastVB__BroadcastMatrix4x4ToSIMDLanes`, scalar/fallback anchors from Waves 718/719/887, `RCPPS` projected-W refinement, and half-float masks rooted at `0x0065e750`. Exact dispatch-table slot schema, vector/matrix/stride layouts, hidden XMM/MMX ABI, half-float special-case policy, runtime math correctness, BEA patching, and rebuild parity remain deferred.

Wave898 CFastVB compose transform tail (`cfastvb-compose-transform-tail-wave898`, `wave898-readback-verified`) saved comments/tags for three raw commentless CFastVB compose/project dispatch rows: `0x005a9f44 CFastVB__DispatchOp_ComposeTransformAndProjectVec3_005a9f44`, `0x005aa0cc CFastVB__DispatchOp_ComposeTransformFromOptionalInputs_Scalar`, and `0x005aa2f2 CFastVB__DispatchOp_ComposeTransformFromOptionalInputs_SIMD`. Probe token anchor: Wave898 CFastVB compose transform tail; cfastvb-compose-transform-tail-wave898; 0x005a9f44 CFastVB__DispatchOp_ComposeTransformAndProjectVec3_005a9f44; 0x005aa0cc CFastVB__DispatchOp_ComposeTransformFromOptionalInputs_Scalar; 0x005aa2f2 CFastVB__DispatchOp_ComposeTransformFromOptionalInputs_SIMD; 0x005b7770 CDXTexture__ValidateJpegFrameAndComputeMcuLayout; 6100/6113 = 99.79%; [maintainer-local-ghidra-backup-root]\BEA_20260526-080711_post_wave898_cfastvb_compose_transform_tail_verified. Static evidence ties the rows to `CFastVB__InitDispatchOpsFromFeatureFlags` DATA xrefs, 3-bit nullable matrix selectors, jump tables `0x005aa0ac`, `0x005aa2d2`, and `0x005aa424`, `CFastVB__DispatchOp_MultiplyMatrix4x4_Packed_005a9d78`, inverse helpers `0x005a9637` and `0x005a8f5d`, identity helper `0x005a62bf`, optional vector/projected-output remaps, and `CFastVB__DispatchOp_TransformProjectVec3ByMatrix4_005a9ced`. Exact dispatch-table slot schema, optional-input layouts, projected-output/vector remap semantics, SIMD-vs-scalar runtime selection policy, runtime math correctness, BEA patching, and rebuild parity remain deferred.

Wave888 texture transform dispatch tail (`texture-transform-dispatch-tail-wave888`, `wave888-readback-verified`) saved comments/tags for CFastVB dispatch and transform rows in the texture transform island. Exact anchors include `0x0057770b CFastVB__BuildTransformMatrixWithOffsets`, `0x00578bad CFastVB__ApplyOptionalTransformPasses_Minimal`, `0x00578dad CFastVB__MapVolumeCoordsToNormalizedUv`, and `0x00578f53 CFastVB__ApplyOptionalTransformPasses`. Probe token anchor: `Wave888 texture transform dispatch tail`; `texture-transform-dispatch-tail-wave888`; `0x0057617e CDXTexture__DispatchPtr00656f48_WithInit`; `0x00576286 CDXTexture__DispatchPtr00656f68_WithInit`; `0x00576404 Math__InterpolateVec4Cubic`; `0x00576621 Math__InterpolateVec4ByUV`; `0x005768fe CFastVB__DispatchIndirect_00656f3c`; `0x0057770b CFastVB__BuildTransformMatrixWithOffsets`; `0x00578a20 CTexture__MapNormalizedUvToVolumeCoords`; `0x00578dad CFastVB__MapVolumeCoordsToNormalizedUv`; `0x00578f53 CFastVB__ApplyOptionalTransformPasses`; `0x00579273 CTexture__BuildTransformMatrixWithOptionalOffsets`; `0x00656f48`; `0x0065715c`; `0x00579a9a CVertexShader__CompileScriptWithDirectiveParser`; `6052/6113 = 99.00%`; `[maintainer-local-ghidra-backup-root]\BEA_20260526-033426_post_wave888_texture_transform_dispatch_tail_verified`. Exact dispatch-table slot targets, exact CPU feature policy, exact descriptor/matrix/vertex-shader/texture-transform layouts, runtime texture/math/render behavior, BEA patching, and rebuild parity remain deferred.

Wave887 texture dispatch/interpolation tail (`texture-dispatch-interpolation-tail-wave887`, `wave887-readback-verified`) saved comments/tags for CFastVB dispatch and interpolation rows in the texture/math dispatch island. Probe token anchor: `Wave887 texture dispatch/interpolation tail`; `texture-dispatch-interpolation-tail-wave887`; `0x005759b6 CFastVB__DispatchIndirect_00657014`; `0x005759c3 CDXTexture__PackTexels_DispatchIndirect_005759c3`; `0x00575b47 Math__InterpolateVec2Cubic`; `0x00575dc9 CFastVB__HermiteInterpolateVec3`; `0x0057600b CVBufTexture__DispatchTextureTransformThunk`; `0x00576161 CFastVB__DispatchIndirectByGlobalTable`; dispatch slots `0x00657014` and `0x00656f58`; `0x0057617e CDXTexture__DispatchPtr00656f48_WithInit`; `6008/6113 = 98.28%`; `[maintainer-local-ghidra-backup-root]\BEA_20260526-030217_post_wave887_texture_dispatch_interpolation_tail_verified`. Exact dispatch-table slot targets, exact CPU feature policy, runtime texture/math/render behavior, BEA patching, and rebuild parity remain deferred.

Wave889 texture codec surface prelude (`texture-codec-surface-prelude-wave889`, `wave889-readback-verified`) saved comments/tags for the texture codec, surface-node, mapped-resource, vertex-shader parser, and resample prelude tranche. Probe token anchor: Wave889 texture codec surface prelude; texture-codec-surface-prelude-wave889; 0x00579a9a CVertexShader__CompileScriptWithDirectiveParser; 0x00579b39 CDXTexture__LookupNamedFormatDescriptor; 0x00579e08 CDXTexture__DecodeBmpDibFromMemory; 0x0057ca6a CDXTexture__DecodeFromMemory_WithFallbackCodecs; 0x0057c7a4 CMeshCollisionVolume__LoadMappedTextureResourcesByMode; 0x0057cca4 CFastVB__BuildResampleKernelBuckets; 0x0057cf60 CDXTexture__CopyDxtBlockRegion; 0x0057d0ee CWaypointManager__BoxBlurPackedColorRows_Scalar; 6054/6113 = 99.03%; [maintainer-local-ghidra-backup-root]\BEA_20260526-040930_post_wave889_texture_codec_surface_prelude_verified. Static evidence ties the tranche to directive parsing, descriptor lookup, codec dispatch, surface-node cleanup, mapped texture export, resample bucket setup, and DXT block copying. Exact texture/codec/surface-node/mapped-file/descriptor/parser/resample table layouts, exact source-body identity, runtime texture decode/encode/export/resample/render behavior, BEA patching, and rebuild parity remain deferred.

Wave890 texture filter MMX dispatch (`texture-filter-mmx-dispatch-wave890`, `wave890-readback-verified`) saved comments/tags for the MMX dispatch continuation around the Wave664 downsample kernel rows. Probe token anchor: Wave890 texture filter MMX dispatch; texture-filter-mmx-dispatch-wave890; 0x0057d0ee CWaypointManager__BoxBlurPackedColorRows_Scalar; 0x0057d244 CDXTexture__Downsample2x2Average32; 0x0057d32e CWaypointManager__BoxBlurPackedColorRows_SIMD; 0x0057d446 CWaypointManager__InitMmxDispatchAndRun; 0x0057d47e CDXTexture__InitMmxDispatchAndRun; dispatch slots 0x00657974 and 0x00657978; 0x00580a05 CDXTexture__UploadSurfaceRegionWithFallback; 6059/6113 = 99.12%; [maintainer-local-ghidra-backup-root]\BEA_20260526-043655_post_wave890_texture_filter_mmx_dispatch_verified. Static evidence ties the tranche to CPU-selected dispatch slots, scalar and MMX/SIMD packed-color row filters, and the same two-slot downsample context used by `0x0057d216 CFastVB__DispatchMmxKernel_00657974` and `0x0057d4ad CFastVB__DispatchMmxKernel_00657978`. Exact owner/source identity, exact texture surface/context layout, hidden dispatch ABI, pointer-table ownership, runtime CPU selection/filtering/downsample behavior, BEA patching, and rebuild parity remain deferred.

Wave891 texture upload texel profile (`texture-upload-texel-profile-wave891`, `wave891-readback-verified`) saved comments/tags for `0x00581a4f CFastVB__TexelUnpackProfile__ctorFromDescriptor` and companion DXTexture upload/profile rows `0x00580a05 CDXTexture__UploadSurfaceRegionWithFallback` and `0x00580ef4 CDXTexture__CreateTexelCodecProfileFromSurfaceDesc`. Probe token anchor: Wave891 texture upload texel profile; texture-upload-texel-profile-wave891; 0x00580a05 CDXTexture__UploadSurfaceRegionWithFallback; 0x00580ef4 CDXTexture__CreateTexelCodecProfileFromSurfaceDesc; 0x00581a4f CFastVB__TexelUnpackProfile__ctorFromDescriptor; vtable slot 0x30; vtable slot 0x24; 0x005888bc CFastVB__InterpolateDualProfileStreams; 6062/6113 = 99.17%; [maintainer-local-ghidra-backup-root]\BEA_20260526-050306_post_wave891_texture_upload_texel_profile_head_verified. Static evidence ties the CFastVB row to broad constructor fan-in, base profile vtable `0x005e9ed0`, vector construction of `0x100` entries, lookup globals `DAT_00657980` and `DAT_00657a00`, key-color byte normalization, and format rows `0x28/0x29`. Exact texture surface/context layout, exact texel profile and descriptor layouts, exact Direct3D interface identity, runtime upload/lock/conversion/unpack/render behavior, BEA patching, and rebuild parity remain deferred.

Wave892 SIMD gate dual profile (`simd-gate-dual-profile-wave892`, `wave892-readback-verified`) saved comments/tags for `0x005888bc CFastVB__InterpolateDualProfileStreams` and companion DXTexture CPU/MMX rows `0x00589116 CDXTexture__IsMmxEnabledBySystemConfig` and `0x005891c6 CDXTexture__InitCpuVendorAndSimdFlags`. Probe token anchor: Wave892 SIMD gate dual profile; simd-gate-dual-profile-wave892; 0x005888bc CFastVB__InterpolateDualProfileStreams; 0x00589116 CDXTexture__IsMmxEnabledBySystemConfig; 0x005891c6 CDXTexture__InitCpuVendorAndSimdFlags; 0x00657164; DisableMMX; GenuineIntel; 0x0058aacf CTexture__HandleDirective_If; 6065/6113 = 99.21%; [maintainer-local-ghidra-backup-root]\BEA_20260526-052708_post_wave892_simd_gate_dual_profile_verified. Static evidence ties the CFastVB row to DATA dispatch slot `0x00657164`, `RET 0x30`, single-profile and multi-profile accumulation, `__ftol` phase reduction against `DAT_005e6a3c`, `CFastVB__DispatchIndirectByGlobalTable`, `CFastVB__DispatchIndirect_00656f48`, conditional payload-copy order, and output pointer/stride advancement. Exact stream/profile descriptor layout, hidden stack ABI, dispatch-slot ownership, interpolation math equivalence, runtime render behavior, BEA patching, and rebuild parity remain deferred.

### Key Characteristics

- **Vertex Size:** 0x1c (28 bytes) - likely position (12) + color (4) + UV (8) + normal/padding (4)
- **Observed Global Max Vertices:** static init writes `0x1388` (5000 vertices = 1250 quads) to the global CFastVB-style state at `DAT_00897aa4`
- **FVF / Vertex Shader Handle:** `0x144` is passed to `CVBuffer__CreateDynamic` and `CEngine__SetVertexShaderHandleRaw`; it is not the max-vertex count
- **Index Buffer:** shared static index buffer at `DAT_00897a90`; `CIBuffer__Create` receives index_count 0x1d4c (7500 indices)
- **Quad Indexing:** Uses 6 indices per quad (two triangles): [0,1,2,2,3,0] pattern

## Wave796 Final Signature Debt (2026-05-24)

Wave796 signature debt (`signature-debt-wave796`, `wave796-readback-verified`) saved the final CFastVB param-name hardening row: `0x005a7617 CFastVB__DispatchOp_BuildRotationMatrixFromEulerAngles` as `void __stdcall CFastVB__DispatchOp_BuildRotationMatrixFromEulerAngles(void * out_matrix4, int packed_angle_pair_low, int packed_angle_pair_high)`. The pass made no renames, no function-boundary changes, and no executable-byte changes; queue telemetry after the pass is 0 exact-undefined signatures, 0 param_N signatures, and strict clean-signature proxy `5544/6098 = 90.92%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260524-050846_post_wave796_final_param_signature_debt_verified`. Hidden packed-stack ABI details, packed angle layout, runtime CFastVB math correctness, BEA patching, and rebuild parity remain deferred.

## Wave854 CFastVB Render Immediate (2026-05-25)

Wave854 CFastVB render immediate static read-back (`cfastvb-render-immediate-wave854`, `wave854-readback-verified`) corrected `0x0051a6a0 CFastVB__RenderIndexedImmediate` to `0x0051a6a0 CFastVB__RenderTriangleStripImmediate` with saved signature `void __thiscall CFastVB__RenderTriangleStripImmediate(void * this)`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260525-104123_post_wave854_cfastvb_render_immediate_verified`. Queue after Wave854: `6098` total, `5755` commented, `343` commentless, strict proxy `5755/6098 = 94.38%`; next raw commentless row is `0x0051a970 CFEPCredits__TransitionNotification`.

| Address | Saved state | Static evidence |
| --- | --- | --- |
| `0x0051a6a0 CFastVB__RenderTriangleStripImmediate` | `void __thiscall CFastVB__RenderTriangleStripImmediate(void * this)` | Unlocks the CVBuffer at `this+0x00`, binds the vertex stream through Direct3D device vtable `+0x190` using stride `0x1c`, sets raw vertex shader/FVF handle `0x144`, calls device vtable `+0x144` with primitive type `5`, start vertex `this+0x06`, and primitive count `this+0x08-2`, then resets `this+0x06`/`this+0x08`. Xrefs are `CConsole__RenderLoadingScreen`, two `CRenderQueue__RenderAll` sites, and `CVBufTexture__DrawSpriteEx`. Unlike `CFastVB__Render`, this path does not bind shared CIBuffer `DAT_00897a90`. |

Exact CFastVB/global render-state layouts, exact Direct3D interface version or method identity beyond observed vtable slots, runtime render output, source identity, BEA patching, and rebuild parity remain deferred.

## Wave967 CFastVB Fast-Trig ABI Boundary Recovery (2026-05-28)

Wave967 CFastVB fast-trig ABI review (`cfastvb-fast-trig-abi-review-wave967`, `wave967-readback-verified`) recovered four previously non-function dispatch-table targets installed by `0x00598474 CFastVB__InitDispatchOpsFromFeatureFlags`. The pass created four function objects, saved names/signatures/comments/tags, made no executable-byte change, and did not launch BEA.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x005a4c67 CFastVB__DispatchOp_ComposeQuaternionFromFastTrigPairs_005a4c67` | `void __stdcall CFastVB__DispatchOp_ComposeQuaternionFromFastTrigPairs_005a4c67(void * out_quaternion_lanes, int packed_lane_arg2, int packed_lane_arg3, int packed_lane_arg4)` | DATA store at `0x00598537` into dispatch slot `+0x64`; post-`RET` boundary starts after `0x005a4c64`, calls `0x005b8ca0 CFastVB__FastTrigPairApprox_Scalar` at `0x005a4c89`, `0x005a4c9a`, and `0x005a4ca9`, writes two qword quaternion-like output lanes, and ends at `0x005a4d29 RET 0x10`. |
| `0x005a60ef CFastVB__DispatchOp_BuildRotationMatrixX_FastTrig_005a60ef` | `void __stdcall CFastVB__DispatchOp_BuildRotationMatrixX_FastTrig_005a60ef(void * out_matrix4x4, float angle_radians)` | DATA store at `0x0059855a` into dispatch slot `+0x78`; loads the second stack argument into `MM0`, calls `0x005b8ca0`, writes a 0x40-byte X-axis rotation-matrix-style output block, and ends at `0x005a614f RET 0x8`. |
| `0x005a6152 CFastVB__DispatchOp_BuildRotationMatrixY_FastTrig_005a6152` | `void __stdcall CFastVB__DispatchOp_BuildRotationMatrixY_FastTrig_005a6152(void * out_matrix4x4, float angle_radians)` | DATA store at `0x00598561` into dispatch slot `+0x7c`; loads the second stack argument into `MM0`, calls `0x005b8ca0`, writes a 0x40-byte Y-axis rotation-matrix-style output block, and ends at `0x005a61ad RET 0x8`. |
| `0x005a61b0 CFastVB__DispatchOp_BuildRotationMatrixZ_FastTrig_005a61b0` | `void __stdcall CFastVB__DispatchOp_BuildRotationMatrixZ_FastTrig_005a61b0(void * out_matrix4x4, float angle_radians)` | DATA store at `0x00598568` into dispatch slot `+0x80`; loads the second stack argument into `MM0`, calls `0x005b8ca0`, writes a 0x40-byte Z-axis rotation-matrix-style output block, and ends at `0x005a6206 RET 0x8`. |

Creation dry/apply/final-dry and a conservative signature-label correction dry/apply/final-dry passed. Final post exports verified `4` metadata rows, `4` tag rows, `4` xref rows, `131` body-instruction rows, and `4` decompile rows. Post-Wave967 queue telemetry is `6156` total functions, `6156` commented, `0` commentless, `0` exact-undefined signatures, and `0` `param_N`; export-contract closure remains `6156/6156 = 100.00%`. Wave911 focused re-audit progress is `344/1408 = 24.43%`; expanded static surface progress including the four recovered dispatch targets is `348/1412 = 24.65%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260528-160046_post_wave967_cfastvb_fast_trig_abi_review_verified`.

The broader `CFastVB__InitDispatchOpsFromFeatureFlags` dispatch table still contains additional no-function labels that should be reviewed in a later focused wave. Exact dispatch-table slot schema, packed lane order, vector/quaternion/matrix layouts, hidden MMX/register ABI, exact source identity, runtime CPU dispatch/math behavior, BEA patching, and rebuild parity remain deferred.

Probe anchors: `Wave967`, `cfastvb-fast-trig-abi-review-wave967`, `0x005a4c67 CFastVB__DispatchOp_ComposeQuaternionFromFastTrigPairs_005a4c67`, `0x005a60ef CFastVB__DispatchOp_BuildRotationMatrixX_FastTrig_005a60ef`, `0x005a6152 CFastVB__DispatchOp_BuildRotationMatrixY_FastTrig_005a6152`, `0x005a61b0 CFastVB__DispatchOp_BuildRotationMatrixZ_FastTrig_005a61b0`, `0x00598474 CFastVB__InitDispatchOpsFromFeatureFlags`, `0x005b8ca0 CFastVB__FastTrigPairApprox_Scalar`, `344/1408 = 24.43%`, `348/1412 = 24.65%`, `6156/6156 = 100.00%`, `[maintainer-local-ghidra-backup-root]\BEA_20260528-160046_post_wave967_cfastvb_fast_trig_abi_review_verified`, `function-boundary recovery`.

## Wave968 CFastVB Dispatch Continuation Boundary Recovery (2026-05-28)

Wave968 CFastVB dispatch continuation (`cfastvb-dispatch-continuation-wave968`, `wave968-readback-verified`) recovered five more previously non-function targets installed by `0x00598474 CFastVB__InitDispatchOpsFromFeatureFlags`. The pass created five function objects, saved names/signatures/comments/tags, made no executable-byte change, and did not launch BEA.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x005a6209 CFastVB__DispatchOp_BuildScaleMatrixFromThreeScalars_005a6209` | `void __stdcall CFastVB__DispatchOp_BuildScaleMatrixFromThreeScalars_005a6209(void * out_matrix4x4, float scale_x, float scale_y, float scale_z)` | DATA store at `0x00598572` into dispatch slot `+0x84`; starts after `0x005a6206 RET 0x8`, writes three stack scalar values into diagonal-like 0x40-byte matrix lanes with zero-fill and constant `0x005ef1c0`, runs `FEMMS`, and ends at `0x005a624d RET 0x10`. |
| `0x005ab06f CFastVB__DispatchOp_TransformPackedVec4ByMatrix4_005ab06f` | `void __stdcall CFastVB__DispatchOp_TransformPackedVec4ByMatrix4_005ab06f(void * out_vec4_lanes, void * in_vec4_lanes, void * matrix4x4)` | DATA store at `0x0059857c` into dispatch slot `+0x88`; starts after `0x005ab06c RET 0x8`, multiplies a packed four-float/qword input pair across matrix-like qword lanes, writes two output qwords, runs `FEMMS`, and ends at `0x005ab0ea RET 0xc` before `0x005ab0ed CDXTexture__EvalNodeOutputSizeUnits`. |
| `0x005a6250 CFastVB__DispatchOp_TransposeMatrix4x4_005a6250` | `void __stdcall CFastVB__DispatchOp_TransposeMatrix4x4_005a6250(void * out_matrix4x4, void * in_matrix4x4)` | DATA store at `0x0059859a` into dispatch slot `+0x94`; starts after `0x005a624d RET 0x10`, shuffles eight source qword lanes with `PUNPCKLDQ`/`PUNPCKHDQ`, writes a repacked 0x40-byte matrix-like output block, runs `FEMMS`, and ends at `0x005a62bc RET 0x8`. |
| `0x005a62f8 CFastVB__DispatchOp_BuildRotationMatrixFromQuaternionPacked_Scalar_005a62f8` | `void __stdcall CFastVB__DispatchOp_BuildRotationMatrixFromQuaternionPacked_Scalar_005a62f8(void * out_matrix4x4, void * in_quaternion_lanes)` | Default DATA store at `0x005985a4` into dispatch slot `+0x98`; starts after `0x005a62f7 RET`, expands packed quaternion-like qword input through `PFADD`/`PFMUL`/`PFSUBR` against `0x005ef100`, writes a 0x40-byte rotation-matrix-style output block, runs `FEMMS`, and ends at `0x005a63c7 RET 0x8`. |
| `0x005a63ca CFastVB__DispatchOp_BuildRotationMatrixFromQuaternionPacked_SIMD_005a63ca` | `void __stdcall CFastVB__DispatchOp_BuildRotationMatrixFromQuaternionPacked_SIMD_005a63ca(void * out_matrix4x4, void * in_quaternion_lanes)` | Feature-override DATA store at `0x00598692` for the same dispatch slot `+0x98` when feature bits `0x100` and `0x200` are both present; starts after `0x005a63c7 RET 0x8`, uses `PSWAPD`/`PFPNACC`/`PFACC`/`PFMUL`/`PFSUBR`, writes a 0x40-byte rotation-matrix-style output block, runs `FEMMS`, and ends at `0x005a647c RET 0x8` before `0x005a647f CFastVB__DispatchOp_ComposeTransformFromOptionalInputs_Core_005a647f`. |

Dry/apply/final-dry passed. Final post exports verified `5` metadata rows, `5` tag rows, `5` xref rows, `190` body-instruction rows, and `5` decompile rows. Post-Wave968 queue telemetry is `6161` total functions, `6161` commented, `0` commentless, `0` exact-undefined signatures, and `0` `param_N`; export-contract closure is `6161/6161 = 100.00%`. Wave911 focused re-audit progress remains `344/1408 = 24.43%`; expanded static surface progress including newly recovered dispatch targets is `353/1417 = 24.91%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260528-163203_post_wave968_cfastvb_dispatch_continuation_verified`.

Exact dispatch-table slot schema, packed lane order, vector/quaternion/matrix layouts, row/column convention, hidden MMX/register ABI, exact source identity, runtime CPU dispatch/math/render behavior, BEA patching, and rebuild parity remain separate proof.

Probe anchors: `Wave968`, `cfastvb-dispatch-continuation-wave968`, `0x005a6209 CFastVB__DispatchOp_BuildScaleMatrixFromThreeScalars_005a6209`, `0x005ab06f CFastVB__DispatchOp_TransformPackedVec4ByMatrix4_005ab06f`, `0x005a6250 CFastVB__DispatchOp_TransposeMatrix4x4_005a6250`, `0x005a62f8 CFastVB__DispatchOp_BuildRotationMatrixFromQuaternionPacked_Scalar_005a62f8`, `0x005a63ca CFastVB__DispatchOp_BuildRotationMatrixFromQuaternionPacked_SIMD_005a63ca`, `0x00598474 CFastVB__InitDispatchOpsFromFeatureFlags`, `344/1408 = 24.43%`, `353/1417 = 24.91%`, `6161/6161 = 100.00%`, `[maintainer-local-ghidra-backup-root]\BEA_20260528-163203_post_wave968_cfastvb_dispatch_continuation_verified`, `function-boundary recovery`.

## Wave969 CFastVB Array Dispatch Continuation Boundary Recovery (2026-05-28)

Wave969 CFastVB array dispatch continuation (`cfastvb-array-dispatch-continuation-wave969`, `wave969-readback-verified`) recovered five more previously non-function array-transform targets installed by `0x00598474 CFastVB__InitDispatchOpsFromFeatureFlags`. The pass created five function objects, saved stack-locked names/signatures/comments/tags, made no executable-byte change, and did not launch BEA.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x005a3a40 CFastVB__DispatchOp_TransformVec2ArrayByMatrix4_WithTranslation_005a3a40` | `int CFastVB__DispatchOp_TransformVec2ArrayByMatrix4_WithTranslation_005a3a40(void)` | DATA store at `0x005986cf` into dispatch slot `+0xec`; starts after `0x005a3980 RET 0x18`, falls back through scalar helper `0x005aa73b`, broadcasts matrix rows into XMM lanes, processes strided Vec2 inputs in batches, applies translation terms, writes transformed Vec4-style output lanes, and ends at `0x005a3c9c RET 0x18` before `0x005a3ca0`. |
| `0x005a3ca0 CFastVB__DispatchOp_TransformProjectVec2ArrayByMatrix4_005a3ca0` | `int CFastVB__DispatchOp_TransformProjectVec2ArrayByMatrix4_005a3ca0(void)` | DATA store at `0x005986d9` into dispatch slot `+0xf0`; starts after `0x005a3c9c RET 0x18`, falls back through scalar helper `0x005aa7c9`, applies matrix rows plus translation terms to strided Vec2 inputs, refines projected W with `RCPPS`/`SUBPS`/`MULPS`, writes projected Vec2 output lanes, and ends at `0x005a3ee2 RET 0x18` before `0x005a3f00`. |
| `0x005a3f00 CFastVB__DispatchOp_TransformVec2ArrayByMatrix4_NoTranslation_005a3f00` | `int CFastVB__DispatchOp_TransformVec2ArrayByMatrix4_NoTranslation_005a3f00(void)` | DATA store at `0x005986e3` into dispatch slot `+0xf4`; starts after `0x005a3ee2 RET 0x18`, falls back through scalar helper `0x005aa790`, batches strided Vec2 inputs across matrix row lanes without translation terms, writes transformed Vec2 output lanes, and ends at `0x005a40b3 RET 0x18` before `0x005a40c0 CFastVB__DispatchOp_TransformVec3ArrayByMatrix4_WithTranslation_005a40c0`. |
| `0x005a4160 CFastVB__DispatchOp_TransformProjectVec3ArrayByMatrix4_Alt_005a4160` | `int CFastVB__DispatchOp_TransformProjectVec3ArrayByMatrix4_Alt_005a4160(void)` | DATA store at `0x005986bb` into dispatch slot `+0xfc`; starts after `0x005a40c0 RET 0x18`, falls back through scalar helper `0x005a9f3f`, applies matrix rows plus translation terms to strided Vec3 inputs, refines projected W with `RCPPS`/`SUBPS`/`MULPS`, writes projected Vec3-style output lanes, and ends at `0x005a447a RET 0x18` before `0x005a4480`. |
| `0x005a4480 CFastVB__DispatchOp_TransformVec3ArrayByMatrix4_NoTranslation_005a4480` | `int CFastVB__DispatchOp_TransformVec3ArrayByMatrix4_NoTranslation_005a4480(void)` | DATA store at `0x005986c5` into dispatch slot `+0x100`; starts after `0x005a447a RET 0x18`, falls back through scalar helper `0x005a99f8`, batches strided Vec3 inputs across matrix row lanes without translation terms, writes transformed Vec3-style output lanes, and ends at `0x005a46f9 RET 0x18` before adjacent target `0x005a46fc`. |

Dry/apply/final-dry passed. Final post exports verified `5` metadata rows, `5` tag rows, `5` xref rows, `691` body-instruction rows, and `5` decompile rows. Post-Wave969 queue telemetry is `6166` total functions, `6166` commented, `0` commentless, `0` exact-undefined signatures, and `0` `param_N`; export-contract closure is `6166/6166 = 100.00%`. Wave911 focused re-audit progress remains `344/1408 = 24.43%`; expanded static surface progress including newly recovered dispatch targets is `358/1422 = 25.18%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260528-170703_post_wave969_cfastvb_array_dispatch_continuation_verified`.

Exact dispatch-table slot schema, vector/matrix layout, packed lane order, hidden SSE/register ABI, exact source identity, runtime CPU dispatch/math/render behavior, BEA patching, and rebuild parity remain separate proof. Adjacent target `0x005a46fc` was later recovered by Wave970.

Probe anchors: `Wave969`, `cfastvb-array-dispatch-continuation-wave969`, `0x005a3a40 CFastVB__DispatchOp_TransformVec2ArrayByMatrix4_WithTranslation_005a3a40`, `0x005a3ca0 CFastVB__DispatchOp_TransformProjectVec2ArrayByMatrix4_005a3ca0`, `0x005a3f00 CFastVB__DispatchOp_TransformVec2ArrayByMatrix4_NoTranslation_005a3f00`, `0x005a4160 CFastVB__DispatchOp_TransformProjectVec3ArrayByMatrix4_Alt_005a4160`, `0x005a4480 CFastVB__DispatchOp_TransformVec3ArrayByMatrix4_NoTranslation_005a4480`, `0x00598474 CFastVB__InitDispatchOpsFromFeatureFlags`, `344/1408 = 24.43%`, `358/1422 = 25.18%`, `6166/6166 = 100.00%`, `[maintainer-local-ghidra-backup-root]\BEA_20260528-170703_post_wave969_cfastvb_array_dispatch_continuation_verified`, `function-boundary recovery`.

## Wave970 CFastVB Axis Dispatch Continuation Boundary Recovery (2026-05-28)

Wave970 CFastVB axis dispatch continuation (`cfastvb-axis-dispatch-continuation-wave970`, `wave970-readback-verified`) recovered four more previously non-function axis/quaternion dispatch targets installed by `0x00598474 CFastVB__InitDispatchOpsFromFeatureFlags`. The pass created four function objects, saved stack-locked names/signatures/comments/tags, made no executable-byte change, and did not launch BEA.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x005a46fc CFastVB__DispatchOp_MultiplyQuaternionPair_Packed_005a46fc` | `int CFastVB__DispatchOp_MultiplyQuaternionPair_Packed_005a46fc(void)` | DATA store at `0x0059850d` into dispatch slot `+0x4c`; starts after `0x005a46f9 RET 0x18`, consumes two packed qword quaternion-like inputs from stack arguments, uses packed multiply/add/subtract lanes with sign masks at `0x005ef118`, writes two qword output lanes, runs `FEMMS`, and ends at `0x005a4792 RET 0x0c` before `0x005a4795`. |
| `0x005a4795 CFastVB__DispatchOp_NormalizeQuaternion_Packed_005a4795` | `int CFastVB__DispatchOp_NormalizeQuaternion_Packed_005a4795(void)` | DATA store at `0x00598514` into dispatch slot `+0x50`; starts after `0x005a4792 RET 0x0c`, computes packed length, gates against threshold `0x005ef170`, refines reciprocal square root with `PFRSQRT`/`PFRSQIT1`/`PFRCPIT2`, writes normalized qword output lanes, runs `FEMMS`, and ends at `0x005a47ef RET 0x08` before `0x005a47f2`. |
| `0x005a4836 CFastVB__DispatchOp_BuildQuaternionFromMatrix3x3_Packed_005a4836` | `int CFastVB__DispatchOp_BuildQuaternionFromMatrix3x3_Packed_005a4836(void)` | Default DATA store at `0x00598530` into dispatch slot `+0x60`; starts after `0x005a4833 RET 0x0c`, reads matrix-like diagonal/off-diagonal lanes, branches through internal target `0x005a4980`, normalizes with constant `0x005ef168`, writes quaternion-like qword output lanes, and ends through `RET 0x08` terminals at `0x005a4904`, `0x005a497d`, `0x005a49f1`, and `0x005a4a4f` before `0x005a4a52`. |
| `0x005a4a52 CFastVB__DispatchOp_BuildQuaternionFromMatrix3x3_FeatureOverride_005a4a52` | `int CFastVB__DispatchOp_BuildQuaternionFromMatrix3x3_FeatureOverride_005a4a52(void)` | Feature-override DATA store at `0x005986a6` into dispatch slot `+0x60` when feature bits `0x100` and `0x200` are present; starts after `0x005a4a4f RET 0x08`, mirrors the packed matrix3x3-to-quaternion branch shape with `PMOVMSKB`/`PFCMPGE` mask selection and reciprocal-square-root refinement, and ends before `0x005a4c67`. |

Dry/apply/final-dry passed. Final post exports verified `4` metadata rows, `4` tag rows, `4` xref rows, `342` body-instruction rows, and `4` decompile rows. Post-Wave970 queue telemetry is `6170` total functions, `6170` commented, `0` commentless, `0` exact-undefined signatures, and `0` `param_N`; export-contract closure is `6170/6170 = 100.00%`. Wave911 focused re-audit progress remains `344/1408 = 24.43%`; expanded static surface progress including newly recovered dispatch targets is `362/1426 = 25.39%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260528-174057_post_wave970_cfastvb_axis_dispatch_continuation_verified`.

Exact dispatch-table slot schema, vector/quaternion/matrix layout, packed lane order, row/column convention, hidden MMX/register ABI, exact source identity, runtime CPU dispatch/math/render behavior, BEA patching, and rebuild parity remain separate proof. `0x005a4980` is an internal branch target inside `0x005a4836`, not a separate dispatch-table function.

Probe anchors: `Wave970`, `cfastvb-axis-dispatch-continuation-wave970`, `0x005a46fc CFastVB__DispatchOp_MultiplyQuaternionPair_Packed_005a46fc`, `0x005a4795 CFastVB__DispatchOp_NormalizeQuaternion_Packed_005a4795`, `0x005a4836 CFastVB__DispatchOp_BuildQuaternionFromMatrix3x3_Packed_005a4836`, `0x005a4a52 CFastVB__DispatchOp_BuildQuaternionFromMatrix3x3_FeatureOverride_005a4a52`, `0x005a4980 internal branch target`, `0x00598474 CFastVB__InitDispatchOpsFromFeatureFlags`, `344/1408 = 24.43%`, `362/1426 = 25.39%`, `6170/6170 = 100.00%`, `[maintainer-local-ghidra-backup-root]\BEA_20260528-174057_post_wave970_cfastvb_axis_dispatch_continuation_verified`, `function-boundary recovery`.

## Wave971 CFastVB Dispatch-Slot Boundary Sweep (2026-05-28)

Wave971 CFastVB dispatch-slot boundary sweep (`cfastvb-dispatch-slot-boundary-sweep-wave971`, `wave971-readback-verified`) recovered twenty-eight remaining previously non-function dispatch-slot targets installed by `0x00598474 CFastVB__InitDispatchOpsFromFeatureFlags`. The pass created function objects, saved conservative stack-locked `int ...(void)` signatures plus comments/tags, made no executable-byte change, and did not launch BEA.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x005a4fee CFastVB__DispatchOp_SlotB0_005a4fee` | `int CFastVB__DispatchOp_SlotB0_005a4fee(void)` | DATA store at `0x005985e0` into dispatch slot `+0xb0`; starts after `0x005a4feb RET 0x18`; first observed terminal is `0x005a504f RET 0x8`. |
| `0x005a50f9 CFastVB__DispatchOp_SlotE0_005a50f9` | `int CFastVB__DispatchOp_SlotE0_005a50f9(void)` | DATA store at `0x00598630` into dispatch slot `+0xe0`; starts after `0x005a50f6 RET 0x8`; first observed terminal is `0x005a519b RET 0x8`. |
| `0x005a5bd7 CFastVB__DispatchOp_Slot0C_005a5bd7` | `int CFastVB__DispatchOp_Slot0C_005a5bd7(void)` | DATA store at `0x005984a4` into dispatch slot `+0x0c`; starts after `0x005a5bd4 RET 0x1c`; first observed terminal is `0x005a5e06 RET 0x0c`. |
| `0x005a77bc CFastVB__DispatchOp_SlotA4_005a77bc` | `int CFastVB__DispatchOp_SlotA4_005a77bc(void)` | DATA store at `0x005985c2` into dispatch slot `+0xa4`; starts after `0x005a77b9 RET 0x10`; first observed terminal is `0x005a7ced RET 0x14`. |
| `0x005a923f CFastVB__DispatchOp_Slot10_005a923f` | `int CFastVB__DispatchOp_Slot10_005a923f(void)` | DATA store at `0x00598658` into dispatch slot `+0x10`; starts after `0x005a923c RET 0x0c`; first observed terminal is `0x005a945f RET 0x0c`. |
| `0x005aa5c0 CFastVB__DispatchOp_SlotE4_005aa5c0` | `int CFastVB__DispatchOp_SlotE4_005aa5c0(void)` | DATA store at `0x00598673` into dispatch slot `+0xe4`; starts after `0x005aa5a7 RET 0x0c`; first observed terminal is `0x005aa738 RET 0x0c`. |
| `0x005aaadd CFastVB__DispatchOp_Slot40_005aaadd` | `int CFastVB__DispatchOp_Slot40_005aaadd(void)` | DATA store at `0x005984f8` into dispatch slot `+0x40`; starts after `0x005aaada RET 0x8`; first observed terminal is `0x005aac0c RET 0x10`. |
| `0x005aaf4d CFastVB__DispatchOp_Slot58_005aaf4d` | `int CFastVB__DispatchOp_Slot58_005aaf4d(void)` | DATA store at `0x00598522` into dispatch slot `+0x58`; starts after `0x005aaf4a RET 0x10`; first observed terminal is `0x005aafc5 RET 0x10`. |

Complete recovered target set: `0x005a4fee`, `0x005a50f9`, `0x005a5bd7`, `0x005a5e09`, `0x005a5ed8`, `0x005a5f28`, `0x005a6013`, `0x005a77bc`, `0x005a923f`, `0x005a996b`, `0x005a9987`, `0x005a9abe`, `0x005a9b2f`, `0x005a9c03`, `0x005aa5c0`, `0x005aa82d`, `0x005aa8c5`, `0x005aa90e`, `0x005aa951`, `0x005aa9fc`, `0x005aaa7e`, `0x005aaadd`, `0x005aac0f`, `0x005aac80`, `0x005aad48`, `0x005aae26`, `0x005aae69`, and `0x005aaf4d`.

Dry/apply/final-dry passed. Final post exports verified `28` metadata rows, `28` tag rows, `28` xref rows, `1821` body-instruction rows, and `28` decompile rows. Post-Wave971 queue telemetry is `6198` total functions, `6198` commented, `0` commentless, `0` exact-undefined signatures, and `0` `param_N`; export-contract closure is `6198/6198 = 100.00%`. Wave911 focused re-audit progress remains `344/1408 = 24.43%`; expanded static surface progress including newly recovered dispatch targets is `390/1454 = 26.82%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260528-181005_post_wave971_cfastvb_dispatch_slot_boundary_sweep_verified`.

Exact dispatch-table slot schema, vector/quaternion/matrix layout, packed lane order, hidden MMX/SSE/register ABI, exact source identity, runtime CPU dispatch/math/render behavior, BEA patching, and rebuild parity remain separate proof.

Probe anchors: `Wave971`, `cfastvb-dispatch-slot-boundary-sweep-wave971`, `0x005a4fee CFastVB__DispatchOp_SlotB0_005a4fee`, `0x005a77bc CFastVB__DispatchOp_SlotA4_005a77bc`, `0x005aaadd CFastVB__DispatchOp_Slot40_005aaadd`, `0x00598474 CFastVB__InitDispatchOpsFromFeatureFlags`, `390/1454 = 26.82%`, `6198/6198 = 100.00%`, `[maintainer-local-ghidra-backup-root]\BEA_20260528-181005_post_wave971_cfastvb_dispatch_slot_boundary_sweep_verified`, `function-boundary recovery`.

## Class Structure (CFastVB)

```cpp
struct CFastVB {
    /* 0x00 */ CVBuffer* pVertexBuffer;    // Pointer to vertex buffer
    /* 0x04 */ ushort   nWriteOffset;      // Current write position (vertex count)
    /* 0x06 */ ushort   nStartVertex;      // Start vertex for current batch (-1 if none)
    /* 0x08 */ int      nVertexCount;      // Number of vertices in current batch
    /* 0x0C */ int      nMaxVertices;      // Observed global state initializes this to 0x1388
};
```

## Functions

| Address | Name | Description |
|---------|------|-------------|
| `0x0051a270` | CFastVB__Create | Initialize fast vertex buffer |
| `0x0051a340` | CFastVB__Destroy | Release vertex buffer and static index buffer |
| `0x0051a380` | CFastVB__LockAligned | Lock vertex buffer (4-vertex aligned) |
| `0x0051a430` | CFastVB__Lock | Lock vertex buffer for writing |
| `0x0051a510` | CFastVB__Render | Flush pending vertices to GPU |
| `0x005d6820` | CFastVB__Create__Unwind | Exception handler for Create |
| `0x005d6840` | CFastVB__Render__Unwind | Exception handler for Render |

---

## Wave737 CFastVB Fast Trig Tail Read-Back Note

Wave737 CFastVB fast trig tail saved six adjacent fast trigonometric helper rows. Tag anchor: `cfastvb-fast-trig-tail-wave737`; the earliest raw commentless row after this pass remains `0x0042f220 CSPtrSet__Clear`, and the next commentless high-signal row is `0x005bb9b0 CDXTexture__InverseDct8x8_DequantAndStore_Scalar`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x005b81d0` | `void __stdcall CFastVB__SinCosApproxVec4_Paired(float * angle_vec4, float * out_sin_vec4, float * out_cos_vec4)` | RET `0xc` vec4 sine/cosine approximation helper called by `CFastVB__DispatchOp_EulerToQuaternion_0059f4f1`; reads four angle lanes and writes sine-like and cosine-like vec4 outputs. |
| `0x005b83b9` | `void __stdcall CFastVB__SinCosVec4Approx(float * angle_vec4, float * out_sin_vec4, float * out_cos_vec4)` | RET `0xc` vec4 sine/cosine approximation helper called by `CFastVB__DispatchOp_BuildQuaternionFromEulerAngles_005a36cf`; reads four angle lanes and writes sine-like and cosine-like vec4 outputs. |
| `0x005b85c0` | `int Math__Atan2ApproxPacked(void)` | Comment/tag-only packed atan2-style helper called by `CFastVB__DispatchOp_InterpolateQuaternionPairCore_005a4d98`; hidden `MM0`/`MM1` inputs and return register contract remain deferred. |
| `0x005b86c0` | `int CFastVB__FastAcosApprox_Scalar(void)` | Comment/tag-only fast acos-style helper called by axis-angle extraction, quaternion normalization fallback, and spline blending paths; hidden `MM0` ABI remains deferred. |

Wave1119 (`wave1119-mixed-score26-current-risk-review`) re-read `0x005b85c0 Math__Atan2ApproxPacked` and `0x005b86c0 CFastVB__FastAcosApprox_Scalar` with a fresh read-only Ghidra export and no mutation. Xrefs remain `0x005a4e3d` from `CFastVB__DispatchOp_InterpolateQuaternionPairCore_005a4d98` for the atan2-style helper and `0x005a481a`/`0x005a507e`/spline-blend callers for the fast-acos helper; decompile still shows hidden MM register inputs, packed polynomial/reciprocal operations, `DAT_0065ed98`/`DAT_0065ed9c` constants, and stale EAX-style returns intentionally retained until the packed register ABI is proven. Current focused accounting moves to `110/1179 = 9.33%`; verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260605-022812_post_wave1119_mixed_score26_current_risk_review_verified`. Runtime math behavior, exact packed lane layout, return register contract, source identity, BEA patching, and rebuild parity remain separate proof.
| `0x005b8ca0` | `uint CFastVB__FastTrigPairApprox_Scalar(void)` | Comment/tag-only fast trig-pair helper used by axis-angle quaternion, spline, and rotation-matrix dispatch paths; packed register return and adjacent no-function xref boundaries remain deferred. |
| `0x005b8da0` | `uint CFastVB__FastSinApprox_Scalar_005b8da0(void)` | Comment/tag-only fast sine-style helper used by quaternion interpolation, quaternion normalization fallback, and spline blending paths; packed register ABI remains deferred. |

Wave737 read-back evidence verified `6` metadata rows, `6` tag rows, `30` xref rows, `1686` instruction rows, `1110` xref-site instruction rows, `9` caller decompile rows, and `6` decompile rows. The pass hardened `2` visible signatures/parameter names, left `4` locked packed-MMX helpers comment/tag-only, made no renames, made no function-boundary changes, and made no executable-byte changes. Post-Wave737 queue telemetry is `6098` total, `4339` commented, `1759` commentless, `1216` exact-undefined signatures, `43` `param_N`, comment-backed proxy `4339/6098 = 71.15%`, strict clean-signature proxy `4281/6098 = 70.20%`, raw commentless head `0x0042f220 CSPtrSet__Clear`, and high-signal head `0x005bb9b0 CDXTexture__InverseDct8x8_DequantAndStore_Scalar`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260522-123343_post_wave737_cfastvb_fast_trig_tail_verified`.

Exact polynomial identity, packed register ABI, packed lane layout, floating-point accuracy, runtime math behavior, no-function caller boundaries, source identity, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave737 CFastVB fast trig tail`, `cfastvb-fast-trig-tail-wave737`, `0x005b81d0 CFastVB__SinCosApproxVec4_Paired`, `0x005b83b9 CFastVB__SinCosVec4Approx`, `0x005b85c0 Math__Atan2ApproxPacked`, `0x005b86c0 CFastVB__FastAcosApprox_Scalar`, `0x005b8ca0 CFastVB__FastTrigPairApprox_Scalar`, `0x005b8da0 CFastVB__FastSinApprox_Scalar_005b8da0`, `0x0042f220 CSPtrSet__Clear`, `0x005bb9b0 CDXTexture__InverseDct8x8_DequantAndStore_Scalar`.

---

## Wave722 CFastVB Packed Vec2/Quaternion Tail Read-Back Note

Wave722 CFastVB packed Vec2/quaternion tail saved five adjacent dispatch helpers. Tag anchor: `cfastvb-packed-vec2-quaternion-tail-wave722`; the earliest raw commentless row after this pass remains `0x0042f220 CSPtrSet__Clear`, and the next commentless high-signal row is `0x005ab0ed CDXTexture__EvalNodeOutputSizeUnits`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x005aa480` | `int __stdcall CFastVB__DispatchOp_ConvertPackedS16ToFloatPairBatch_005aa480(float * out_float_pairs, short * input_packed_s16_pairs, uint pair_count)` | Packed 16-bit pair conversion dispatch; loops over four-pair batches, falls back to `CFastVB__ConvertFloat16BufferToFloat32_00575a6b` for small/tail counts, writes float pairs, and returns the output pointer as an int-compatible value. |
| `0x005aa73b` | `int __stdcall CFastVB__DispatchOp_TransformVec2ByMatrix4_WithTranslation_005aa73b(float * out_vec4, float * input_vec2, float * matrix4x4)` | Vec2-by-matrix4 dispatch with translation; broadcasts x/y lanes, applies two matrix row pairs plus translation terms, and writes four output floats. |
| `0x005aa790` | `int __stdcall CFastVB__DispatchOp_TransformVec2ByMatrix4_NoTranslation_005aa790(float * out_vec2, float * input_vec2, float * matrix4x4)` | Vec2-by-matrix4 dispatch without translation; broadcasts x/y lanes, multiplies by matrix rows without translation terms, and writes two output floats. |
| `0x005aa7c9` | `int __stdcall CFastVB__DispatchOp_TransformProjectVec2ByMatrix4_005aa7c9(float * out_vec2, float * input_vec2, float * matrix4x4)` | Vec2 transform/project dispatch; applies matrix rows plus translation, derives a reciprocal from projected w, scales the output pair, and writes two output floats. |
| `0x005ab00b` | `void __stdcall CFastVB__DispatchOp_NormalizeQuaternionPacked_005ab00b(float * out_quaternion_xyzw, float * input_quaternion_xyzw)` | Packed quaternion normalization dispatch; accumulates squared xy and masked zw lanes, applies reciprocal-square-root refinement with a small-length compare mask, and writes four output quaternion floats. |

Wave722 read-back evidence verified `5` metadata rows, `5` tag rows, `10` xref rows, `1705` instruction rows, `2405` wide instruction rows, and `5` decompile rows. The pass hardened `5` visible signatures/parameter names, made no renames, made no function-boundary changes, and made no executable-byte changes. Post-Wave722 queue telemetry is `6098` total, `4253` commented, `1845` commentless, `1216` exact-undefined signatures, `113` `param_N`, comment-backed proxy `4253/6098 = 69.75%`, strict clean-signature proxy `4195/6098 = 68.79%`, raw commentless head `0x0042f220 CSPtrSet__Clear`, and high-signal head `0x005ab0ed CDXTexture__EvalNodeOutputSizeUnits`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260522-050258_post_wave722_cfastvb_packed_vec2_quaternion_tail_verified`.

Exact dispatch-table slot schema, packed vector/matrix/quaternion storage contract, source identity, runtime math correctness, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave722 CFastVB packed Vec2/quaternion tail`, `cfastvb-packed-vec2-quaternion-tail-wave722`, `0x005aa480 CFastVB__DispatchOp_ConvertPackedS16ToFloatPairBatch_005aa480`, `0x005aa73b CFastVB__DispatchOp_TransformVec2ByMatrix4_WithTranslation_005aa73b`, `0x005aa7c9 CFastVB__DispatchOp_TransformProjectVec2ByMatrix4_005aa7c9`, `0x005ab00b CFastVB__DispatchOp_NormalizeQuaternionPacked_005ab00b`, `0x0042f220 CSPtrSet__Clear`, `0x005ab0ed CDXTexture__EvalNodeOutputSizeUnits`.

---

## Wave721 CFastVB Matrix/Rotation Continuation Read-Back Note

Wave721 CFastVB matrix/rotation continuation saved twelve adjacent matrix, rotation, inverse, normalize, transform/project, and multiply helpers. Tag anchor: `cfastvb-matrix-rotation-continuation-wave721`; the earliest raw commentless row after this pass remains `0x0042f220 CSPtrSet__Clear`, and the next commentless high-signal row is `0x005aa480 CFastVB__DispatchOp_ConvertPackedS16ToFloatPairBatch_005aa480`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x005a62bf` | `void __cdecl CFastVB__DispatchOp_InitIdentityMatrix4x4_005a62bf(float * out_matrix4x4)` | Identity matrix4x4 initializer; writes one/zero lanes across a sixteen-float matrix and exits through `FastExitMediaState`. |
| `0x005a647f` | `int CFastVB__DispatchOp_ComposeTransformFromOptionalInputs_Core_005a647f(void)` | Comment/tag-only optional-transform composition core with output matrix, optional translation, quaternion/rotation, scale/basis, inverse pivot, and additive-offset-style inputs. |
| `0x005a7617` | `void __stdcall CFastVB__DispatchOp_BuildRotationMatrixFromEulerAngles(void * param_1, int param_2, int param_3)` | Comment/tag-only Euler-angle-to-matrix4 dispatch; custom stack-frame code scales packed angle inputs by the `0x005ef190` constant and calls the fast trig pair helper three times. |
| `0x005a7cf0` | `void __stdcall CFastVB__DispatchOp_BuildRotationMatrixFromAxisAngleVector(float * out_matrix4x4, float * axis_angle_vec3)` | Axis-angle-vector-to-matrix4 dispatch; normalizes through `CFastVB__DispatchOp_NormalizeVec3_Packed_005a9a5f`, calls the fast trig pair helper, and writes a sixteen-float rotation matrix. |
| `0x005a7e09` | `int CFastVB__DispatchOp_ComposeMatrixFromOptionalTransforms(void)` | Comment/tag-only optional transform matrix composition dispatch with nullable identity/scale/rotation/translation inputs, optional inverse-pivot, and additive-offset adjustments. |
| `0x005a8f5d` | `void __stdcall CFastVB__DispatchOp_InvertMatrix4x4_WithDeterminant_005a8f5d(float * out_inverse_matrix4x4, float * out_determinant_or_null, float * input_matrix4x4)` | Matrix4x4 inverse dispatch; computes cofactors and determinant, writes optional determinant output, skips inverse writes for zero determinant, and otherwise writes reciprocal-determinant-scaled inverse rows. |
| `0x005a9637` | `int __stdcall CFastVB__DispatchOp_InvertMatrix4x4_Variant_005a9637(float * out_inverse_matrix4x4, float * out_determinant_or_null, float * input_matrix4x4)` | Scalar matrix4x4 inverse variant; returns zero for zero determinant or the output pointer as an int-compatible value after writing the inverse matrix. |
| `0x005a99f8` | `int __stdcall CFastVB__DispatchOp_TransformVec3ByMatrix4_NoTranslation_005a99f8(float * out_vec3, float * input_vec3, float * matrix4x4)` | Vec3-by-matrix4 helper that omits translation terms, writes three output floats, and returns the output pointer as an int-compatible value. |
| `0x005a9a5f` | `void __stdcall CFastVB__DispatchOp_NormalizeVec3_Packed_005a9a5f(float * out_vec3, float * input_vec3)` | Packed Vec3 normalization helper with reciprocal-square-root refinement and a small-length mask. |
| `0x005a9ced` | `int __stdcall CFastVB__DispatchOp_TransformProjectVec3ByMatrix4_005a9ced(float * out_vec3, float * input_vec3, float * matrix4x4)` | Vec3 transform/project helper with matrix rows plus translation, reciprocal-w scaling, and three output floats. |
| `0x005a9d78` | `int __stdcall CFastVB__DispatchOp_MultiplyMatrix4x4_Packed_005a9d78(float * out_matrix4x4, float * left_matrix4x4, float * right_matrix4x4)` | Packed matrix4x4 multiply helper; reads four packed rows from the left matrix, multiplies them across right matrix columns, and writes sixteen output floats. |
| `0x005a9f3f` | `int __stdcall CFastVB__DispatchOp_TransformProjectVec3ByMatrix4_Alt_005a9f3f(float * out_vec3, float * input_vec3, float * matrix4x4)` | Alternate Vec3 transform/project dispatch with translation terms, reciprocal-w scaling, three output floats, and an int-compatible output-pointer return. |

Wave721 read-back evidence verified `12` metadata rows, `12` tag rows, `38` xref rows, `1356` instruction rows, `3420` wide instruction rows, and `12` decompile rows. The pass hardened `9` visible signatures/parameter names, left `3` stack-locked or packed-ABI helpers comment/tag-only, made no renames, made no function-boundary changes, and made no executable-byte changes. Post-Wave721 queue telemetry is `6098` total, `4248` commented, `1850` commentless, `1216` exact-undefined signatures, `118` `param_N`, comment-backed proxy `4248/6098 = 69.66%`, strict clean-signature proxy `4190/6098 = 68.71%`, raw commentless head `0x0042f220 CSPtrSet__Clear`, and high-signal head `0x005aa480 CFastVB__DispatchOp_ConvertPackedS16ToFloatPairBatch_005aa480`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260522-043029_post_wave721_cfastvb_matrix_rotation_continuation_verified`.

Exact dispatch-table slot schema, packed vector/matrix storage contract, source identity, runtime math correctness, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave721 CFastVB matrix/rotation continuation`, `cfastvb-matrix-rotation-continuation-wave721`, `0x005a62bf CFastVB__DispatchOp_InitIdentityMatrix4x4_005a62bf`, `0x005a7617 CFastVB__DispatchOp_BuildRotationMatrixFromEulerAngles`, `0x005a7cf0 CFastVB__DispatchOp_BuildRotationMatrixFromAxisAngleVector`, `0x005a8f5d CFastVB__DispatchOp_InvertMatrix4x4_WithDeterminant_005a8f5d`, `0x005a9d78 CFastVB__DispatchOp_MultiplyMatrix4x4_Packed_005a9d78`, `0x0042f220 CSPtrSet__Clear`, `0x005aa480 CFastVB__DispatchOp_ConvertPackedS16ToFloatPairBatch_005aa480`.

---

## Wave720 CFastVB Quaternion Tail Read-Back Note

Wave720 CFastVB quaternion tail saved ten adjacent vector/quaternion helpers. Tag anchor: `cfastvb-quaternion-tail-wave720`; the earliest raw commentless row after this pass remains `0x0042f220 CSPtrSet__Clear`, and the next commentless high-signal row is `0x005a62bf CFastVB__DispatchOp_InitIdentityMatrix4x4_005a62bf`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x005a38c0` | `int CFastVB__DispatchOp_TransformVec4ArrayByMatrix4(void)` | Comment/tag-only; stack-locked decompile shows strided Vec4 array output/input, matrix4x4 pointer, element count, and four transformed output lanes per element. |
| `0x005a3980` | `int CFastVB__DispatchOp_TransformVec4ArrayByMatrix4_Alt_005a3980(void)` | Comment/tag-only alternate Vec4-array-by-matrix4 dispatch with the same strided output/input/matrix/count shape. |
| `0x005a40c0` | `int CFastVB__DispatchOp_TransformVec3ArrayByMatrix4_WithTranslation_005a40c0(void)` | Comment/tag-only; strided Vec3 source lanes are transformed through matrix rows plus translation terms into four output lanes. |
| `0x005a47f2` | `void __stdcall CFastVB__DispatchOp_ExtractAxisAndOptionalAngle(float * quaternion_xyzw, float * out_axis_vec3_or_null, float * out_angle_or_null)` | Axis/angle extraction dispatch; copies first three quaternion lanes to the optional axis output and optionally stores a fast-acos-derived angle scalar. |
| `0x005a4d2c` | `void __stdcall CFastVB__DispatchOp_BuildQuaternionFromAxisAngleVector_005a4d2c(float * out_quaternion_xyzw, float * axis_vec3, float angle_radians)` | Normalizes the axis vector through `CFastVB__DispatchOp_NormalizeVec3_Packed_005a9a5f`, scales angle input, calls the fast trig pair helper, and writes four quaternion lanes. |
| `0x005a4d98` | `void __stdcall CFastVB__DispatchOp_InterpolateQuaternionPairCore_005a4d98(float * out_quaternion_xyzw, float * from_quaternion_xyzw, float * to_quaternion_xyzw, float blend_ratio)` | Quaternion pair interpolation core with dot product, sign/short-path selection, reciprocal/trig angular branch, and blended output lanes. |
| `0x005a4ecf` | `int CFastVB__DispatchOp_BlendQuaternionTriple_005a4ecf(void)` | Comment/tag-only; stack-locked triple-blend helper interpolates one base quaternion toward two controls and then blends the intermediates. |
| `0x005a4f5c` | `int CFastVB__DispatchOp_BlendQuaternionControlPair_005a4f5c(void)` | Comment/tag-only; stack-locked control-pair helper interpolates two pairs and derives a smoothstep-like final blend ratio from `t` and `t*t`. |
| `0x005a5052` | `void __stdcall CFastVB__DispatchOp_NormalizeQuaternionWithAcosFallback_005a5052(float * out_quaternion_xyzw, float * input_quaternion_xyzw)` | Quaternion normalization/angle fallback dispatch with fast acos/sin paths, reciprocal refinement, scalar-lane masking, and output quaternion write. |
| `0x005a519e` | `int CFastVB__DispatchOp_BlendQuaternionSplineSegment_005a519e(void)` | Comment/tag-only large spline-segment helper; aligns quaternion signs by distance tests, normalizes/fallbacks through fast acos/sin paths, and writes two quaternion outputs. |

Wave720 read-back evidence verified `10` metadata rows, `10` tag rows, `16` xref rows, `1130` instruction rows, `3530` wide instruction rows, and `10` decompile rows. The pass hardened `4` visible signatures/parameter names, left `6` stack-locked helpers comment/tag-only, made no renames, made no function-boundary changes, and made no executable-byte changes. Post-Wave720 queue telemetry is `6098` total, `4236` commented, `1862` commentless, `1216` exact-undefined signatures, `127` `param_N`, strict clean-signature proxy `4179/6098 = 68.53%`, raw commentless head `0x0042f220 CSPtrSet__Clear`, and high-signal head `0x005a62bf CFastVB__DispatchOp_InitIdentityMatrix4x4_005a62bf`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260522-035533_post_wave720_cfastvb_quaternion_tail_verified`.

Exact dispatch-table slot schema, vector/quaternion storage contract, source identity, runtime math correctness, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave720 CFastVB quaternion tail`, `cfastvb-quaternion-tail-wave720`, `0x005a38c0 CFastVB__DispatchOp_TransformVec4ArrayByMatrix4`, `0x005a47f2 CFastVB__DispatchOp_ExtractAxisAndOptionalAngle`, `0x005a4d98 CFastVB__DispatchOp_InterpolateQuaternionPairCore_005a4d98`, `0x005a5052 CFastVB__DispatchOp_NormalizeQuaternionWithAcosFallback_005a5052`, `0x005a519e CFastVB__DispatchOp_BlendQuaternionSplineSegment_005a519e`, `0x0042f220 CSPtrSet__Clear`, `0x005a62bf CFastVB__DispatchOp_InitIdentityMatrix4x4_005a62bf`.

---

## Wave719 CFastVB Matrix/Quaternion Core Read-Back Note

Wave719 CFastVB matrix/quaternion core saved twelve adjacent matrix/quaternion helpers. Tag anchor: `cfastvb-matrix-quaternion-core-wave719`; the earliest raw commentless row after this pass is `0x0042f220 CSPtrSet__Clear`, and the next commentless high-signal row is `0x005a47f2 CFastVB__DispatchOp_ExtractAxisAndOptionalAngle`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x005a298f` | `int __stdcall CFastVB__ConvertHalfToFloatArray_SIMD(float * out_float32, ushort * in_float16, uint element_count)` | SIMD half-float conversion referenced by `CFastVB__InitDispatchTableVariant_0059822c`; processes eight half-float inputs through `CFastVB__ConvertHalfToFloat8_CheckSpecialCasesSIMD` when possible. |
| `0x005a2a61` | `void __stdcall CFastVB__DispatchOp_TransformVec2ByMatrix4(float * out_vec4, float * input_vec4, float * matrix4x4)` | Scalar Vec2/Vec4-output transform dispatch referenced by both dispatch-table variants and perspective batch tails. |
| `0x005a2b2d` | `float * __stdcall CFastVB__InvertMatrix4x4_WithDeterminant(float * out_inverse_matrix4x4, float * out_determinant_or_null, float * input_matrix4x4)` | Matrix4x4 inverse helper with optional determinant output, zero-determinant null return, and reciprocal-determinant-scaled inverse output. |
| `0x005a2e29` | `void __stdcall CFastVB__ComputeAdjugateVec4_PackedB(float * out_vec4, float * row_a_vec4, float * row_b_vec4, float * row_c_vec4)` | Packed adjugate/cofactor Vec4 helper using sign masks from the `0x0065e7a0` constant block. |
| `0x005a2ee9` | `double __stdcall CFastVB__DispatchOp_Determinant4x4_005a2ee9(float * matrix4x4)` | 4x4 determinant dispatch; saved as Ghidra's current `double` return because the decompiler uses an x87-style scalar return model. |
| `0x005a2ff4` | `void __stdcall CFastVB__DispatchOp_BuildPlaneFromTriangle_Alt_005a2ff4(float * out_plane_vec4, float * point_a_vec3, float * point_b_vec3, float * point_c_vec3)` | Alternate plane-from-triangle helper with cross-product normal, `rsqrtss` refinement, and sign-masked distance term. |
| `0x005a30f4` | `void __stdcall CFastVB__DispatchOp_QuaternionToMatrix4_Alt_005a30f4(float * out_matrix4x4, float * quaternion_xyzw)` | Alternate quaternion-to-matrix4 helper expanding normalized quaternion lanes through the `0x0065e7e0..0x0065e85c` constant block. |
| `0x005a3200` | `void __stdcall CFastVB__DispatchOp_TransformVec4ByMatrix4_005a3200(float * out_vec4, float * input_vec4, float * matrix4x4)` | Scalar Vec4-by-matrix dispatch referenced by both dispatch-table variants and Vec4 batch tails. |
| `0x005a32d4` | `void __stdcall CFastVB__DispatchOp_MultiplyMatrix4x4_005a32d4(float * out_matrix4x4, float * left_matrix4x4, float * right_matrix4x4)` | Matrix4x4 multiply dispatch writing sixteen row/column dot-product floats. |
| `0x005a3508` | `void __stdcall CFastVB__DispatchOp_BuildMatrix4FromQuaternionPair_005a3508(float * out_matrix4x4, float * basis_quaternion_xyzw, float * rotation_quaternion_xyzw)` | Quaternion-pair-to-matrix dispatch combining a basis quaternion-like input with a normalized rotation quaternion. |
| `0x005a36cf` | `void __stdcall CFastVB__DispatchOp_BuildQuaternionFromEulerAngles_005a36cf(float * out_quaternion_xyzw, float angle_x_radians, float angle_y_radians, float angle_z_radians)` | Euler-angle-to-quaternion helper using `CFastVB__SinCosVec4Approx`. |
| `0x005a3791` | `void __stdcall CFastVB__DispatchOp_BuildQuaternionFromMatrix3x3_005a3791(float * out_quaternion_xyzw, float * matrix3x3)` | Matrix3x3-to-quaternion helper with trace-positive and largest-diagonal fallback branches plus axis-index table `0x005f4340`. |

Wave719 read-back evidence verified `12` metadata rows, `12` tag rows, `25` xref rows, `1116` instruction rows, `3180` wide instruction rows, and `12` decompile rows. The pass hardened `12` visible signatures/parameter names, made no renames, made no function-boundary changes, and made no executable-byte changes. Post-Wave719 queue telemetry is `6098` total, `4226` commented, `1872` commentless, `1216` exact-undefined signatures, `131` `param_N`, strict clean-signature proxy `4169/6098 = 68.37%`, raw commentless head `0x0042f220 CSPtrSet__Clear`, and high-signal head `0x005a47f2 CFastVB__DispatchOp_ExtractAxisAndOptionalAngle`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260522-032725_post_wave719_cfastvb_matrix_quaternion_core_verified`.

Exact dispatch-table slot schema, vector/matrix storage contract, source identity, runtime math correctness, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave719 CFastVB matrix/quaternion core`, `cfastvb-matrix-quaternion-core-wave719`, `0x005a298f CFastVB__ConvertHalfToFloatArray_SIMD`, `0x005a2b2d CFastVB__InvertMatrix4x4_WithDeterminant`, `0x005a3791 CFastVB__DispatchOp_BuildQuaternionFromMatrix3x3_005a3791`, `0x0042f220 CSPtrSet__Clear`, `0x005a47f2 CFastVB__DispatchOp_ExtractAxisAndOptionalAngle`.

---

## Wave718 CFastVB Scalar Transform Core Read-Back Note

Wave718 CFastVB scalar transform core saved seventeen adjacent scalar math/transform helpers. Tag anchor: `cfastvb-scalar-transform-core-wave718`; the earliest raw commentless row after this pass is `0x0042f220 CSPtrSet__Clear`, and the next commentless high-signal row was `0x005a298f CFastVB__ConvertHalfToFloatArray_SIMD`, later hardened by Wave719.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x005a0b22` | `int __stdcall CFastVB__ConvertHalfToFloatArray_SSE(float * out_float32, ushort * in_float16, uint element_count)` | Half-float conversion path referenced by `CFastVB__InitDispatchTableVariant_005980be`; processes eight inputs through `CFastVB__ConvertHalfToFloat8_SIMDKernel` when possible and tails scalar ushort inputs into float output slots. |
| `0x005a0df6` | `void __stdcall CFastVB__ComputeAdjugateVec4_PackedA(float * out_vec4, float * row_a_vec4, float * row_b_vec4, float * row_c_vec4)` | Reads three Vec4 rows, combines 3x3 minor products with sign-mask constants at `0x0065e600..0x0065e60c`, and returns with `RET 0x10`. |
| `0x005a0eb6` | `float * __stdcall CFastVB__NormalizeVec4_ReciprocalSqrt(float * out_vec4, float * input_vec4)` | Vec4 normalization with `rsqrtss` refinement; referenced by both CFastVB dispatch-table variants. |
| `0x005a0f50` | `int CFastVB__EvaluateCubicBasisVec3(void)` | Comment/tag-only; cubic basis Vec3 helper kept stack-locked because Ghidra still reports unknown calling convention and locked parameter storage. |
| `0x005a1002` | `int CFastVB__EvaluateCubicBasisVec2(void)` | Comment/tag-only; cubic basis Vec2 helper kept stack-locked. |
| `0x005a1087` | `int CFastVB__EvaluateCubicBasisVec4(void)` | Comment/tag-only; cubic basis Vec4 helper kept stack-locked. |
| `0x005a112c` | `int CFastVB__DispatchOp_CubicBlendVec3_005a112c(void)` | Comment/tag-only; cubic blend Vec3 helper kept stack-locked. |
| `0x005a11df` | `int CFastVB__DispatchOp_CubicBlendVec4_005a11df(void)` | Comment/tag-only; cubic blend Vec4 helper kept stack-locked. |
| `0x005a1279` | `int CFastVB__EvaluateCubicBasisDerivativeVec2(void)` | Comment/tag-only; cubic derivative Vec2 helper kept stack-locked. |
| `0x005a13f7` | `int CFastVB__DispatchOp_InterpolateVec3ByReciprocal_005a13f7(void)` | Comment/tag-only; reciprocal-weighted interpolation helper kept stack-locked. |
| `0x005a14a5` | `void __stdcall CFastVB__DispatchOp_BuildPlaneFromTriangle_005a14a5(float * out_plane_vec4, float * point_a_vec3, float * point_b_vec3, float * point_c_vec3)` | Cross-product normal construction, `rsqrtss` normalization, xyz normal, and sign-masked distance term. |
| `0x005a15a5` | `void __stdcall CFastVB__DispatchOp_QuaternionToMatrix4_005a15a5(float * out_matrix4x4, float * quaternion_xyzw)` | Quaternion normalization and sixteen matrix-float expansion. |
| `0x005a16b1` | `void __stdcall CFastVB__DispatchOp_TransformVec3ByMatrix4_005a16b1(float * out_vec3, float * input_vec3, float * matrix4x4)` | Scalar Vec3 transform used by dispatch tables and batch tails. |
| `0x005a1786` | `void __stdcall CFastVB__DispatchOp_TransformProjectVec3ByMatrix4_005a1786(float * out_projected_vec3, float * input_vec3, float * matrix4x4)` | Scalar projected Vec3 transform with reciprocal projection refinement. |
| `0x005a1889` | `void __stdcall CFastVB__DispatchOp_NormalizeVec3_005a1889(float * out_vec3, float * input_vec3)` | Tiny-length guard plus `rsqrtss` refinement for xyz. |
| `0x005a1979` | `void __stdcall CFastVB__DispatchOp_NormalizeVec4_005a1979(float * out_vec4, float * input_vec4)` | Tiny-length guard plus `rsqrtss` refinement for xyz and fourth-lane scaling. |
| `0x005a1a8e` | `void __stdcall CFastVB__BuildMatrix4x4FromQuaternion(float * out_matrix4x4, float * basis_matrix4x4, float * quaternion_xyzw)` | Quaternion normalization with lazy constants, basis-matrix row combination, and aligned/unaligned output paths. |

Wave718 read-back evidence verified `17` metadata rows, `17` tag rows, `33` xref rows, `1581` instruction rows, `4505` wide instruction rows, and `17` decompile rows. The pass hardened `10` visible signatures/parameter names, left `7` cubic/interpolation helpers comment/tag-only because stack parameter storage remains locked, made no renames, made no function-boundary changes, and made no executable-byte changes. Post-Wave718 queue telemetry is `6098` total, `4214` commented, `1884` commentless, `1216` exact-undefined signatures, `143` `param_N`, strict clean-signature proxy `4157/6098 = 68.17%`, raw commentless head `0x0042f220 CSPtrSet__Clear`, and high-signal head `0x005a298f CFastVB__ConvertHalfToFloatArray_SIMD`, later hardened by Wave719. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260522-025058_post_wave718_cfastvb_scalar_transform_core_verified`.

Exact dispatch-table slot schema, vector/matrix storage contract, stack-locked cubic helper ABI, source identity, runtime math correctness, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave718 CFastVB scalar transform core`, `cfastvb-scalar-transform-core-wave718`, `0x005a0b22 CFastVB__ConvertHalfToFloatArray_SSE`, `0x005a0f50 CFastVB__EvaluateCubicBasisVec3`, `0x005a1a8e CFastVB__BuildMatrix4x4FromQuaternion`, `0x0042f220 CSPtrSet__Clear`, `0x005a298f CFastVB__ConvertHalfToFloatArray_SIMD`.

---

## Wave717 CFastVB Transform Dispatch Head Read-Back Note

Wave717 CFastVB transform dispatch head saved fourteen adjacent SIMD transform-dispatch helpers. Tag anchor: `cfastvb-transform-dispatch-head-wave717`; the earliest raw commentless row after this pass is `0x0042f220 CSPtrSet__Clear`, and the next commentless high-signal row was `0x005a0b22 CFastVB__ConvertHalfToFloatArray_SSE`, later hardened by Wave718.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x0059f360` | `int __stdcall CFastVB__DispatchOp_TransformVec4_0059f360(void * out_vec4, void * input_vec4, void * matrix4x4)` | Dispatch-table entry referenced by `CFastVB__InitDispatchTableVariant_005980be` and `_0059822c`; transforms a Vec4 through a 4x4 matrix and returns with `RET 0xc`. |
| `0x0059f3d9` | `float * __stdcall CFastVB__DispatchOp_NormalizeVec4_0059f3d9(void * out_vec4, void * input_vec4)` | Computes Vec4 length square, uses `rsqrtss` plus refinement, writes normalized components, and returns with `RET 0x8`. |
| `0x0059f473` | `void __stdcall CFastVB__DispatchOp_NormalizeVec4Scaled_0059f473(void * out_vec4, void * input_vec4)` | Normalizes input, applies component scale constants from `0x0065e500`, and returns with `RET 0x8`. |
| `0x0059f4f1` | `void __stdcall CFastVB__DispatchOp_EulerToQuaternion_0059f4f1(void * out_quaternion_xyzw, float angle_x_radians, float angle_y_radians, float angle_z_radians)` | Scales three Euler inputs, calls `CFastVB__SinCosApproxVec4_Paired`, writes quaternion-style floats, and returns with `RET 0x10`. |
| `0x0059f5b3` | `void __stdcall CFastVB__BuildOrthonormalBasisFromCovariance(void * out_quaternion_xyzw, void * matrix3x3_or_basis)` | Branches on matrix trace, chooses the maximum diagonal fallback when needed, and writes four quaternion-style output floats. |
| `0x0059f6dd` | `void __thiscall CFastVB__BroadcastMatrix4x4ToSIMDLanes(void * this, void * simd_lane_matrix_out, void * matrix4x4)` | Shared batch helper broadcasts source 4x4 matrix scalars into four-wide SIMD lane blocks. The preserved first apply log records a `Ghidra thiscall normalization mismatch`; corrected apply and final dry read back cleanly. |
| `0x0059f857` | `int CFastVB__DispatchOp_TransformVec4Batch_0059f857(void)` | Comment/tag-only; batch Vec4 transform with matrix broadcast and scalar tail dispatch. |
| `0x0059fa5d` | `int CFastVB__DispatchOp_TransformVec4BatchW_0059fa5d(void)` | Comment/tag-only; batch Vec4W transform with hidden EBX/EDI context. |
| `0x0059fbeb` | `int CFastVB__DispatchOp_TransformProjectVec4Batch_0059fbeb(void)` | Comment/tag-only; projected Vec4 batch transform with reciprocal projection and hidden EBX/EDI context. |
| `0x0059fd51` | `int CFastVB__DispatchOp_TransformVec4Batch_NoOffset_0059fd51(void)` | Comment/tag-only; no-offset Vec4 batch transform using broadcast matrix lanes. |
| `0x0059fe61` | `int CFastVB__DispatchOp_TransformVec4Batch_Perspective_0059fe61(void)` | Comment/tag-only; perspective-flavored Vec4 batch transform with scalar tail dispatch. |
| `0x005a009f` | `int CFastVB__DispatchOp_TransformVec3WBatch_005a009f(void)` | Comment/tag-only; batch Vec3W transform with W contribution and scalar tail dispatch. |
| `0x005a026f` | `int CFastVB__DispatchOp_TransformProjectVec3WBatch_005a026f(void)` | Comment/tag-only; projected Vec3W batch transform with reciprocal projected components and scalar tail dispatch. |
| `0x005a04a0` | `int CFastVB__DispatchOp_WeightedMatrixBlendBatch_005a04a0(void)` | Comment/tag-only; weighted matrix/vector blend batch over a large stack-argument contract. |

Wave717 read-back evidence verified `14` metadata rows, `14` tag rows, `32` xref rows, `1246` instruction rows, `3766` wide instruction rows, and `14` decompile rows. The pass hardened `6` visible signatures/parameter names, left `8` batch helpers comment/tag-only because hidden register context or locked parameter storage remains visible, made no renames, made no function-boundary changes, and made no executable-byte changes. Post-Wave717 queue telemetry is `6098` total, `4197` commented, `1901` commentless, `1216` exact-undefined signatures, `153` `param_N`, strict clean-signature proxy `4140/6098 = 67.89%`, raw commentless head `0x0042f220 CSPtrSet__Clear`, and high-signal head `0x005a0b22 CFastVB__ConvertHalfToFloatArray_SSE`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260522-021449_post_wave717_cfastvb_transform_dispatch_head_verified`.

Exact dispatch-table slot schema, vector/matrix storage contract, batch helper hidden-register ABI, source identity, runtime math correctness, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave717 CFastVB transform dispatch head`, `cfastvb-transform-dispatch-head-wave717`, `0x0059f360 CFastVB__DispatchOp_TransformVec4_0059f360`, `0x0059f6dd CFastVB__BroadcastMatrix4x4ToSIMDLanes`, `0x005a04a0 CFastVB__DispatchOp_WeightedMatrixBlendBatch_005a04a0`, `Ghidra thiscall normalization mismatch`, `0x0042f220 CSPtrSet__Clear`, `0x005a0b22 CFastVB__ConvertHalfToFloatArray_SSE`.

---

## Wave709 Node-Tree Compatibility Read-Back Note

Wave709 node-tree compatibility saved six adjacent CFastVB node-tree compatibility/scoring helpers. Tag anchor: `node-tree-compatibility-wave709`; the earliest raw commentless row after this pass is `0x0042f220 CSPtrSet__Clear`, and the next commentless high-signal row is `0x0059aec0 CTexture__CanUseCompactDecodePath`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x00599d80` | `int __thiscall CFastVB__FlattenNodeTreeLeafByLinearIndex(void * this, void * node_tree, uint linear_leaf_index, void * out_leaf_scratch)` | Flattens wrapper/leaf trees by linear leaf index, writes normalized leaf scratch fields, and returns `0` or `0x80004005` for null/unknown paths. |
| `0x00599e48` | `int __stdcall CFastVB__ResolveCommonLeafFormat(void * left_leaf_scratch, void * right_leaf_scratch, void * out_common_format)` | Resolves matching or compatible leaf formats through observed compatibility tables at `0x005f2908/0x005f290c`. |
| `0x00599ffd` | `int __thiscall CFastVB__CompareNodePayloadBindingChain(void * this, void * left_payload, void * right_payload, void * right_binding_chain, int compare_flags)` | Compares payload descriptor/name context and linked binding records; `RET 0x10` keeps one unused cleaned argument as ABI context. |
| `0x0059a10a` | `int __thiscall CFastVB__ScoreNodeTreePairMismatchBits(void * this, void * left_node_tree, void * right_node_tree)` | Counts expanded leaves, flattens paired leaves, resolves common formats, and accumulates mismatch bits after removing a phantom third stack argument. |
| `0x0059a21f` | `int __thiscall CFastVB__AreNodeTreesCompatible(void * this, void * left_node_tree, void * right_node_tree, int relaxed_match)` | Corrects the prior `__stdcall` signature to `__thiscall`; handles null, scratch-expanded, relaxed, and structural-equality node-tree compatibility paths. |
| `0x0059a54d` | `int __thiscall CFastVB__ScoreNodeTreeMatch(void * this, void * source_payload, void * candidate_payload, void * candidate_binding_chain, int match_flags)` | Compares payload/binding context, applies match flag `0x10`, calls compatibility/mismatch-score helpers, and returns `-1` or an accumulated match score. |

Wave709 read-back evidence verified `6` metadata rows, `6` tag rows, `15` xref rows, `1590` instruction rows, and `6` clean decompile rows. The candidate context also exported `0x0059a71a CFastVB__SelectBestNodeTreeMatch` read-only; it remains deferred because hidden `in_ECX`, `unaff_EDI`, and `in_stack_*` ABI artifacts are still present. The pass hardened `6` signatures/parameter names, corrected `0x0059a21f` to `__thiscall`, removed phantom stack arguments from `0x00599d80`, `0x0059a10a`, and `0x0059a54d`, made no renames, made no function-boundary changes, and made no executable-byte changes. Post-Wave709 queue telemetry is `6098` total, `4117` commented, `1981` commentless, `1216` exact-undefined signatures, `218` `param_N`, strict clean-signature proxy `4063/6098 = 66.63%`, raw commentless head `0x0042f220 CSPtrSet__Clear`, and high-signal head `0x0059aec0 CTexture__CanUseCompactDecodePath`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260521-214637_post_wave709_node_tree_compatibility_verified`.

Exact node layout, compatibility rules, score-bit semantics, payload/binding layout, source identity, runtime parser behavior, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave709 node-tree compatibility`, `node-tree-compatibility-wave709`, `0x00599d80 CFastVB__FlattenNodeTreeLeafByLinearIndex`, `0x0059a54d CFastVB__ScoreNodeTreeMatch`, `0x0059a71a CFastVB__SelectBestNodeTreeMatch`, `0x0042f220 CSPtrSet__Clear`, `0x0059aec0 CTexture__CanUseCompactDecodePath`.

---

## Wave708 Node-Tree Predicates Read-Back Note

Wave708 node-tree predicates saved four adjacent CFastVB predicate/equality helpers. Tag anchor: `node-tree-predicates-wave708`; the earliest raw commentless row after this pass is `0x0042f220 CSPtrSet__Clear`, and the next commentless high-signal row is `0x00599d80 CFastVB__FlattenNodeTreeLeafByLinearIndex`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x00599b69` | `uint __thiscall CFastVB__NodeTreeHasBitFlag0x200(void * this, void * node_tree)` | Recursively walks wrapper kinds `1`, `5`, `7`, and `10`; leaf kind `8` returns `node +0x20 & 0x200`; unknown kinds emit the internal-error diagnostic. |
| `0x00599bd7` | `int __thiscall CFastVB__NodeTreeHasOnlyLeafType0to2(void * this, void * node_tree)` | Null trees pass; leaf kind `8` passes only when `node +0x10` is in `0..2`; unknown kinds emit the internal-error diagnostic. |
| `0x00599c49` | `int __thiscall CFastVB__CountNodeTreeExpandedLeafCount(void * this, void * node_tree)` | Counts expanded leaves by summing kind `1` children, unwrapping kinds `5`/`10`, multiplying kind `7` child count by `+0x14`, and using kind `8` fields `+0x1c * +0x18`. |
| `0x00599cd2` | `bool __stdcall CFastVB__AreNodeTreesStructurallyEqual(void * left_node_tree, void * right_node_tree)` | Recursively compares linked children, wrapper children, kind `7` repeat count `+0x14`, and kind `8` fields `+0x10/+0x14/+0x18/+0x1c`. |

Wave708 read-back evidence verified `4` metadata rows, `4` tag rows, `19` xref rows, `356` instruction rows, and `4` clean decompile rows. The pass hardened `4` signatures/parameter names, made no renames, made no function-boundary changes, and made no executable-byte changes. Post-Wave708 queue telemetry is `6098` total, `4111` commented, `1987` commentless, `1216` exact-undefined signatures, `224` `param_N`, strict clean-signature proxy `4057/6098 = 66.53%`, raw commentless head `0x0042f220 CSPtrSet__Clear`, and high-signal head `0x00599d80 CFastVB__FlattenNodeTreeLeafByLinearIndex`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260521-211737_post_wave708_node_tree_predicates_verified`.

Exact node layout, field/flag/type semantics, source identity, runtime parser behavior, BEA patching, and rebuild parity remain unproven. Later node-tree scorer/selector helpers beginning at `0x00599d80 CFastVB__FlattenNodeTreeLeafByLinearIndex` were left read-only for a future ABI-focused tranche.

Probe anchors: `Wave708 node-tree predicates`, `node-tree-predicates-wave708`, `0x00599b69 CFastVB__NodeTreeHasBitFlag0x200`, `0x00599cd2 CFastVB__AreNodeTreesStructurallyEqual`, `0x0042f220 CSPtrSet__Clear`, `0x00599d80 CFastVB__FlattenNodeTreeLeafByLinearIndex`.

---

## Wave707 Node-Tree Diagnostics Read-Back Note

Wave707 node-tree diagnostics saved three adjacent CFastVB diagnostic wrappers. Tag anchor: `node-tree-diagnostics-wave707`; the earliest raw commentless row after this pass is `0x0042f220 CSPtrSet__Clear`, and the next commentless high-signal row was `0x00599b69 CFastVB__NodeTreeHasBitFlag0x200`, later hardened by Wave708.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x00599a74` | `void __cdecl CFastVB__SelectBestNodeTreeMatch_ReportWarningAndSetFlag(void * match_context, void * source_location, int diagnostic_id, char * format)` | Formats caller varargs into a local buffer, appends via `CTexture__AppendDiagnosticMessage`, and sets `match_context +0x40`. |
| `0x00599ac8` | `void __cdecl CFastVB__SelectBestNodeTreeMatch_ReportWarning(void * match_context, void * source_location, int diagnostic_id, char * format)` | Formats caller varargs into a local buffer and appends via `CTexture__AppendDiagnosticMessageDedup` without a local flag write. |
| `0x00599b13` | `void __cdecl CFastVB__SetParseErrorAndMarkStateDirty(void * parser_context, void * source_location, int diagnostic_id, char * format)` | Formats caller varargs into a local buffer, appends via `CTexture__AppendDiagnosticMessage`, and sets `parser_context +0x40/+0x44`. |

Wave707 read-back evidence verified `3` metadata rows, `3` tag rows, `9` xref rows, `267` instruction rows, and `3` clean decompile rows. The pass hardened `3` signatures/parameter names, made no renames, made no function-boundary changes, and made no executable-byte changes. Post-Wave707 queue telemetry is `6098` total, `4107` commented, `1991` commentless, `1216` exact-undefined signatures, `228` `param_N`, strict clean-signature proxy `4053/6098 = 66.46%`, raw commentless head `0x0042f220 CSPtrSet__Clear`, and high-signal head `0x00599b69 CFastVB__NodeTreeHasBitFlag0x200`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260521-204613_post_wave707_node_tree_diagnostics_verified`.

Exact context layout, varargs ABI, diagnostic id semantics, dedup key semantics, flag meanings, runtime parser behavior, source identity, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave707 node-tree diagnostics`, `node-tree-diagnostics-wave707`, `0x00599a74 CFastVB__SelectBestNodeTreeMatch_ReportWarningAndSetFlag`, `0x00599b13 CFastVB__SetParseErrorAndMarkStateDirty`, `0x0042f220 CSPtrSet__Clear`, `0x00599b69 CFastVB__NodeTreeHasBitFlag0x200`.

---

## Wave706 Node-Type Lifecycle CFastVB Companion Note

Wave706 node-type lifecycle saved two CFastVB-labelled rows in the same tranche as CTexture node-type lifecycle helpers documented in [`DXTexture.cpp`](../DXTexture.cpp/_index.md). Tag anchor: `node-type-lifecycle-wave706`; the earliest raw commentless row after this pass is `0x0042f220 CSPtrSet__Clear`, and the next commentless high-signal row was `0x00599a74 CFastVB__SelectBestNodeTreeMatch_ReportWarningAndSetFlag`, later hardened by Wave707.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x005997a5` | `void * __fastcall CFastVB__InitNodeType17(void * node_type17)` | Initializes node-type `0x11`, zeroes descriptor/resource slots, binds vtable `0x005ef374`, and returns the initialized pointer. |
| `0x00599878` | `void * __fastcall CFastVB__CloneNodeTreeWithAddRef(void * source_node_type17)` | Allocates and initializes a node-type `0x11` clone, copies descriptor fields, invokes vslot `+8` clone/add-ref hooks for optional resources, and destroys a partial clone on failure. |

Wave706 read-back evidence verified `9` metadata rows, `9` tag rows, `12` xref rows, `801` instruction rows, and `9` clean decompile rows across `0x005997a5 CFastVB__InitNodeType17` through `0x00599a58 CTexture__NodeType12_ScalarDeletingDtor`. The pass hardened `7` signatures/parameter names, left `2` locked-storage rows comment/tag-only, made no renames, made no function-boundary changes, and made no executable-byte changes. Post-Wave706 queue telemetry is `6098` total, `4104` commented, `1994` commentless, `1216` exact-undefined signatures, `231` `param_N`, strict clean-signature proxy `4050/6098 = 66.42%`, raw commentless head `0x0042f220 CSPtrSet__Clear`, and high-signal head `0x00599a74 CFastVB__SelectBestNodeTreeMatch_ReportWarningAndSetFlag`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260521-201902_post_wave706_node_type_lifecycle_verified`.

Exact node-type enum meanings, concrete field schema, hidden constructor ABI, child-resource ownership, reference-count semantics, runtime texture behavior, runtime vertex-buffer behavior, BEA patching, parser/source identity, and rebuild parity remain unproven.

Probe anchors: `Wave706 node-type lifecycle`, `node-type-lifecycle-wave706`, `0x005997a5 CFastVB__InitNodeType17`, `0x00599a58 CTexture__NodeType12_ScalarDeletingDtor`, `0x0042f220 CSPtrSet__Clear`, `0x00599a74 CFastVB__SelectBestNodeTreeMatch_ReportWarningAndSetFlag`.

---

## Wave705 Texture Serialized-Chunk Prelude CFastVB Companion Note

Wave705 texture serialized-chunk prelude saved one direct CFastVB row in the same tranche as CTexture/CDXTexture serialized-chunk and texture-binding helpers documented in [`DXTexture.cpp`](../DXTexture.cpp/_index.md). Tag anchor: `texture-serialized-chunk-prelude-wave705`; the earliest raw commentless row after this pass is `0x0042f220 CSPtrSet__Clear`, and the next commentless high-signal row is `0x005997a5 CFastVB__InitNodeType17`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x00599258` | `int __stdcall CFastVB__ComputeNodeSpanAndStride(void * node_tree, uint * out_span, uint * out_stride)` | Recursively computes span and stride for observed node kinds `8`, `7`, and `1`; kind `8` uses scalar-width or span/stride fields, kind `7` multiplies child stride by `+0x14`, and kind `1` walks a chained child tree while accumulating span and max stride. |

Wave705 read-back evidence verified `7` metadata rows, `7` tag rows, `29` xref rows, `847` instruction rows, and `7` clean decompile rows across `0x0059902a CDXTexture__RegisterSerializedChunk` through `0x005994c4 CDXTexture__ProcessTextureChunkAndEmitBindings`. The pass hardened `5` signatures/parameter names, left `2` locked-storage rows comment/tag-only, made no renames, made no function-boundary changes, and made no executable-byte changes. Post-Wave705 queue telemetry is `6098` total, `4095` commented, `2003` commentless, `1216` exact-undefined signatures, `238` `param_N`, strict clean-signature proxy `4041/6098 = 66.27%`, raw commentless head `0x0042f220 CSPtrSet__Clear`, and high-signal head `0x005997a5 CFastVB__InitNodeType17`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260521-194929_post_wave705_texture_serialized_chunk_prelude_verified`.

Exact chunk-builder layout, chunk/flag enums, record and binding schemas, node/declaration layouts, selected-node ABI, token enum, parser/source identity, runtime shader/texture behavior, runtime vertex-buffer behavior, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave705 texture serialized-chunk prelude`, `texture-serialized-chunk-prelude-wave705`, `0x0059902a CDXTexture__RegisterSerializedChunk`, `0x005994c4 CDXTexture__ProcessTextureChunkAndEmitBindings`, `0x0042f220 CSPtrSet__Clear`, `0x005997a5 CFastVB__InitNodeType17`.

---

## Wave704 Node-Type Constructors/Destructors CFastVB Companion Note

Wave704 node-type constructors/destructors saved ten CFastVB-labelled rows in the same tranche as CTexture/CDXTexture node-type and owned-list helpers documented in [`DXTexture.cpp`](../DXTexture.cpp/_index.md). Tag anchor: `node-type-constructors-wave704`; the earliest raw commentless row after this pass is `0x0042f220 CSPtrSet__Clear`, and the next commentless high-signal row is `0x00599161 CTexture__ComputeDebugChunkDwordCount`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x00598a56` | `void __fastcall CFastVB__InitNodeType9(void * node_type9)` | Initializes node-type-9 state with kind/class `8`, vtable `0x005ef250`, null links, zeroed payload fields, and default tag/value field `+0x14 = 9`. |
| `0x00598a81` | `int CFastVB__NodeType9__ctor(void)` | Hidden-ECX constructor copies five stack values into `+0x10..+0x20`; comment/tag-only because Ghidra reports locked storage. |
| `0x00598abd` | `void __fastcall CFastVB__NodeType9__dtor(void * node_type9)` | Restores node-type-9 vtable `0x005ef250` and releases the child/sibling chain through `CDXTexture__ReleaseNodePayloadChain`. |
| `0x00598b48` | `void __fastcall CFastVB__InitNodeType10(void * node_type10)` | Initializes node-type-10 state with kind/class `10`, vtable `0x005ef260`, null links, and zeroed owned/resource slots through `+0x38`. |
| `0x00598b81` | `void __fastcall CFastVB__NodeType10_dtor(void * node_type10)` | Releases owned pointers/resources at `+0x20/+0x24/+0x28/+0x2c/+0x30/+0x38`, then releases the base payload chain. |
| `0x00598d6b` | `void * __fastcall CFastVB__InitNodeType13(void * node_type13)` | Initializes node-type-13 state with kind/class `0xd`, vtable `0x005ef270`, zeroed storage through `+0x3c`, and `+0x10 = 3`. |
| `0x00598f60` | `void * __thiscall CFastVB__NodeType8_scalar_deleting_dtor(void * this, uint delete_flags)` | Node-type-8 scalar-deleting wrapper: resets vtable `0x005ef240`, releases the chain, and frees on delete bit 0. |
| `0x00598f82` | `void * __thiscall CFastVB__NodeType9_scalar_deleting_dtor(void * this, uint delete_flags)` | Node-type-9 scalar-deleting wrapper: resets vtable `0x005ef250`, releases the chain, and frees on delete bit 0. |
| `0x00598fa4` | `void * __thiscall CFastVB__NodeType10_scalar_deleting_dtor(void * this, uint delete_flags)` | Calls `CFastVB__NodeType10_dtor`, then frees on delete bit 0 and returns `this`. |
| `0x00598ff4` | `void __fastcall CTexture__FreeOwnedNodeListAndPayloads(void * owned_node_list)` | Drains owned-node records and conditionally frees payloads; included here because the tranche closes the CFastVB-labelled node-type rows before this owned-list tail. |

Wave704 read-back evidence verified `20` metadata rows, `20` tag rows, `45` xref rows, `2420` instruction rows, and `20` clean decompile rows across `0x005989c3 CTexture__NodeType8_InitDefaults` through `0x00598ff4 CTexture__FreeOwnedNodeListAndPayloads`. The pass hardened `17` signatures/parameter names, left `3` locked-storage rows comment/tag-only, made no renames, made no function-boundary changes, and made no executable-byte changes. Post-Wave704 queue telemetry is `6098` total, `4088` commented, `2010` commentless, `1216` exact-undefined signatures, `243` `param_N`, strict clean-signature proxy `4034/6098 = 66.15%`, raw commentless head `0x0042f220 CSPtrSet__Clear`, and high-signal head `0x00599161 CTexture__ComputeDebugChunkDwordCount`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260521-185425_post_wave704_node_type_constructors_verified`.

Exact node-type enum values, concrete node/owned-list/descriptor layouts, hidden calling-convention ABI, reference-count semantics, parser/source identity, runtime texture behavior, runtime vertex-buffer behavior, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave704 node-type constructors/destructors`, `node-type-constructors-wave704`, `0x005989c3 CTexture__NodeType8_InitDefaults`, `0x00598ff4 CTexture__FreeOwnedNodeListAndPayloads`, `0x0042f220 CSPtrSet__Clear`, `0x00599161 CTexture__ComputeDebugChunkDwordCount`.

---

## Wave703 Node Payload Head CFastVB Companion Note

Wave703 node payload head saved two CFastVB-labelled rows in the same node-payload tranche as CTexture/CDXTexture helpers documented in [`DXTexture.cpp`](../DXTexture.cpp/_index.md). Tag anchor: `ctexture-node-payload-head-wave703`; the next queue head after this pass is `0x005989c3 CTexture__NodeType8_InitDefaults`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x00598873` | `void * __fastcall CFastVB__CloneNodeChainWithAddRef(void * source_chain)` | Clones kind-1 wrapper nodes, copies `+0x10`, clones children through vslot `+0x8`, rolls back failed child clones with delete flag 1, and links cloned siblings through `+0xc`. |
| `0x005988f5` | `int __fastcall CFastVB__CompareNodeValuesByTagAndPayload(void * left_payload)` | Compares the ECX-held left payload with a hidden EAX-held right payload by tag, including scalar/pointer, inline-string, indirect-string, and double-like cases. |

Wave703 read-back evidence verified `12` metadata rows, `12` tag rows, `60` xref rows, `444` instruction rows, and `12` clean decompile rows across `0x00598702 CTexture__NodePayloadBaseCtor` through `0x005988f5 CFastVB__CompareNodeValuesByTagAndPayload`. The pass hardened `10` signatures/parameter names, left `2` locked-storage rows comment/tag-only, made no renames, made no function-boundary changes, and made no executable-byte changes. Post-Wave703 queue telemetry is `6098` total, `4068` commented, `2030` commentless, `1216` exact-undefined signatures, `260` `param_N`, strict clean-signature proxy `4014/6098 = 65.82%`, and next head `0x005989c3 CTexture__NodeType8_InitDefaults`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260521-182413_post_wave703_node_payload_head_verified`.

Exact node-payload struct layout, payload type enum, vtable contract, hidden-register comparator ABI, AddRef semantics, parser reduction behavior, runtime texture behavior, runtime vertex-buffer behavior, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave703 node payload head`, `ctexture-node-payload-head-wave703`, `0x00598702 CTexture__NodePayloadBaseCtor`, `0x005988f5 CFastVB__CompareNodeValuesByTagAndPayload`, `0x005989c3 CTexture__NodeType8_InitDefaults`.

---

## Wave702 DXT Codec / Dispatch CFastVB Companion Note

Wave702 DXT codec / dispatch saved five CFastVB-labelled rows in the same tranche as CDXTexture/CTexture DXT codec helpers documented in [`DXTexture.cpp`](../DXTexture.cpp/_index.md). Tag anchor: `dxt-codec-dispatch-wave702`; the next queue head after this pass is `0x00598702 CTexture__NodePayloadBaseCtor`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x00597a61` | `void __stdcall CFastVB__PackScalarBlock_4BitEndpoints(void * dxt3_block_out, float * rgba_float_block16)` | Packs explicit 4-bit alpha nibbles with residual diffusion, then quantizes the color selector block at `output+8`. |
| `0x00597b87` | `int __stdcall CFastVB__PackScalarBlock_InterpolatedEndpoints(void * dxt5_block_out, float * rgba_float_block16)` | Solves DXT5 alpha endpoints, builds selector remap tables, and packs selector bytes with residual diffusion. |
| `0x005980be` | `void __cdecl CFastVB__InitDispatchTableVariant_005980be(void * math_dispatch_table)` | Seeds one math dispatch-table variant with observed transform, matrix, quaternion, half-float, and batch helper pointers. |
| `0x0059822c` | `void __cdecl CFastVB__InitDispatchTableVariant_0059822c(void * math_dispatch_table)` | Seeds an alternate dispatch-table variant with alternate matrix/quaternion/batch helpers and SIMD half-float conversion slots. |
| `0x00598474` | `void __cdecl CFastVB__InitDispatchOpsFromFeatureFlags(void * math_dispatch_table)` | Queries `CFastVB__DetectCpuFeatureMask` and conditionally replaces dispatch slots for observed feature-mask bits. |

Wave702 read-back evidence verified `11` metadata rows, `11` tag rows, `17` xref rows, `1067` instruction rows, and `11` clean decompile rows across `0x0059764a CDXTexture__DecodeDxt1ColorBlockToRgba` through `0x00598474 CFastVB__InitDispatchOpsFromFeatureFlags`. The pass hardened `11` signatures/parameter names, made no renames, made no function-boundary changes, and made no executable-byte changes. Post-Wave702 queue telemetry is `6098` total, `4056` commented, `2042` commentless, `1216` exact-undefined signatures, `270` `param_N`, strict clean-signature proxy `4002/6098 = 65.63%`, and next head `0x00598702 CTexture__NodePayloadBaseCtor`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260521-175105_post_wave702_dxt_codec_dispatch_verified`.

Exact DXT block ABI, alpha selector ordering, residual diffusion policy, dispatch-table slot schema, CPU feature-bit names, runtime texture fidelity, runtime compression quality, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave702 DXT codec / dispatch`, `dxt-codec-dispatch-wave702`, `0x0059764a CDXTexture__DecodeDxt1ColorBlockToRgba`, `0x00598474 CFastVB__InitDispatchOpsFromFeatureFlags`, `0x00598702 CTexture__NodePayloadBaseCtor`.

---

## Wave701 Texture Math / DXT Prelude CFastVB Companion Note

Wave701 texture math / DXT prelude saved five CFastVB-labelled rows in the same tranche as CDXTexture/CTexture math and codec helpers documented in [`DXTexture.cpp`](../DXTexture.cpp/_index.md). Tag anchor: `texture-math-dxt-prelude-wave701`; the next queue head after this pass is `0x0059764a CDXTexture__DecodeDxt1ColorBlockToRgba`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x00596341` | `void __stdcall CFastVB__InitMathDispatchTable(void * math_dispatch_table)` | Seeds observed math dispatch-table slots with fixed helper labels and pointers to the Wave701 matrix/normalization helpers. |
| `0x00596480` | `uint __fastcall CFastVB__PackClampedRgbToR5G6B5(void * rgb_float_triplet)` | Clamps three float RGB lanes, rounds through 5-bit/6-bit scale constants, and packs an RGB565 endpoint word. |
| `0x00596589` | `void __stdcall CFastVB__SolveScalarEndpointPairFromSamples(float * endpoint_min_out, float * endpoint_max_out, float * scalar_samples16)` | Scans sixteen scalar samples, uses hidden EBX as endpoint-count/mode input, and iteratively refines scalar endpoints for up to eight passes. |
| `0x005968a4` | `void __stdcall CFastVB__SolveVectorEndpointPairFromSamples(float * endpoint_min_rgb_out, float * endpoint_max_rgb_out, float * rgba_samples16, int endpoint_count)` | Scans sixteen four-float sample rows, chooses an RGB bounding axis/order, and optionally refines RGB endpoints for endpoint counts 3 or 4. |
| `0x00596e23` | `int __stdcall CFastVB__QuantizeScalarBlockIndices(void * dxt_color_block_out, float alpha_mode_weight)` | Quantizes a hidden-EAX sixteen-pixel float RGBA block into endpoint and selector output, calls the vector endpoint solver, packs/unpacks RGB565 endpoints, and writes the 32-bit selector mask. |

Wave701 read-back evidence verified `12` metadata rows, `12` tag rows, `24` xref rows, `1068` instruction rows, and `12` clean decompile rows across `0x005960c1 CDXTexture__FastReciprocalSqrtScalar` through `0x00596e23 CFastVB__QuantizeScalarBlockIndices`. The pass hardened `12` visible signatures/parameter names, documented hidden EAX/EBX ABI gaps where present, made no renames, made no function-boundary changes, and made no executable-byte changes. Post-Wave701 queue telemetry is `6098` total, `4045` commented, `2053` commentless, `1216` exact-undefined signatures, `281` `param_N`, strict clean-signature proxy `3991/6098 = 65.45%`, and next head `0x0059764a CDXTexture__DecodeDxt1ColorBlockToRgba`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260521-172303_post_wave701_texture_math_dxt_prelude_verified`.

Exact lookup-table provenance, numeric error bounds, vector/matrix layout conventions, dispatch-table schema, CPU feature replacement behavior, hidden EAX/EBX helper ABI, RGB565 color-space convention, DXT block schema, alpha-mode semantics, residual diffusion policy, runtime math correctness, runtime texture fidelity, runtime compression quality, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave701 texture math / DXT prelude`, `texture-math-dxt-prelude-wave701`, `0x005960c1 CDXTexture__FastReciprocalSqrtScalar`, `0x00596e23 CFastVB__QuantizeScalarBlockIndices`, `0x0059764a CDXTexture__DecodeDxt1ColorBlockToRgba`.

---

## Wave693 CDXTexture Parser-Context Diagnostics Context Note

Wave693 CDXTexture parser-context diagnostics saved two CFastVB-labelled parser-context rows in the same tranche as six CDXTexture/CTexture diagnostic rows documented in [`DXTexture.cpp`](../DXTexture.cpp/_index.md). Tag anchor: `cdxtexture-parser-context-diagnostics-wave693`; the next queue head after this pass is `0x00592dc2 CDXTexture__CreatePngDecodeContext`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x00592b00` | `void __stdcall CFastVB__ParserContext_Shutdown(void * parser_context)` | Releases the parser-context owned object, invokes observed shutdown/final callback slots, calls `CRT__CExit(1)`, and dispatches the final stack-held callback record seeded by the init helper. |
| `0x00592c50` | `void __stdcall CFastVB__ParserContext_Init(void * parser_context)` | Seeds parser-context callback slots at observed offsets, clears state fields, installs the default bogus-message-code diagnostic text pointer, and records diagnostic id `0x7b`. |

Wave693 read-back evidence verified `8` metadata rows, `8` tag rows, `65` xref rows, `296` instruction rows, and `8` clean decompile rows across `0x00592b00 CFastVB__ParserContext_Shutdown` through `0x00592d9e CDXTexture__WarnPngChunkWithFormattedTag`. The pass hardened seven signatures, left the CDXTexture PNG chunk formatter comment/tag-only, made no renames, made no function-boundary changes, and made no executable-byte changes. Post-Wave693 queue telemetry is `6098` total, `3973` commented, `2125` commentless, `1216` exact-undefined signatures, `353` `param_N`, strict clean-signature proxy `3923/6098 = 64.33%`, and next head `0x00592dc2 CDXTexture__CreatePngDecodeContext`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260521-135916_post_wave693_cdxtexture_parser_context_diagnostics_verified`.

Exact parser-context layout, callback-table ABI, diagnostic table ownership, callback prototypes, runtime PNG/JPEG decode fidelity, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave693 CDXTexture parser-context diagnostics`, `cdxtexture-parser-context-diagnostics-wave693`, `0x00592b00 CFastVB__ParserContext_Shutdown`, `0x00592d9e CDXTexture__WarnPngChunkWithFormattedTag`, `0x00592dc2 CDXTexture__CreatePngDecodeContext`.

---

## Wave692 CDXTexture JPEG Marker Reader Context Note

Wave692 CDXTexture JPEG marker reader saved one CFastVB-labelled SOI helper in the marker-reader tranche documented in [`DXTexture.cpp`](../DXTexture.cpp/_index.md). Tag anchor: `cdxtexture-jpeg-marker-reader-wave692`; the next queue head after this pass was `0x00592b00 CFastVB__ParserContext_Shutdown`, later hardened by Wave693.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x00592530` | `int __stdcall CFastVB__JpegParser_ReadAndValidateSOI(void * jpeg_decode_state)` | Reads the first two buffered JPEG bytes, validates the SOI marker bytes `0xff/0xd8`, emits diagnostic id `0x35` on mismatch, advances the buffer cursor, records the marker byte at the observed decode-state slot, and returns decoder status. |

Wave692 read-back evidence verified the six-row marker-reader tranche from `0x00592380 CTexture__ReadJpegSegmentLengthAndEmitMarker` through `0x00592a80 CDXTexture__InitJpegMarkerReader`. The pass hardened six signatures, made no renames, made no function-boundary changes, and made no executable-byte changes. Post-Wave692 queue telemetry is `6098` total, `3965` commented, `2133` commentless, `1216` exact-undefined signatures, `360` `param_N`, strict clean-signature proxy `3915/6098 = 64.20%`, and next head `0x00592b00 CFastVB__ParserContext_Shutdown`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260521-132823_post_wave692_cdxtexture_jpeg_marker_reader_verified`.

Exact parser owner identity, SOI precondition contract, callback ABI, runtime decode fidelity, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave692 CDXTexture JPEG marker reader`, `cdxtexture-jpeg-marker-reader-wave692`, `0x00592380 CTexture__ReadJpegSegmentLengthAndEmitMarker`, `0x00592a80 CDXTexture__InitJpegMarkerReader`, `0x00592b00 CFastVB__ParserContext_Shutdown`.

---

## Wave679 CDXTexture Catch Bridge Context Note

Wave679 CDXTexture catch bridge did not mutate CFastVB-owned rows, but it closed the `0x00589200 Catch@00589200` queue head that Wave678 deliberately deferred beside `0x0058926b CFastVB__InitDispatchTableByCpuFeature`. The pass saved `0x00589200 Catch@00589200` and `0x0058920c CDXTexture__DetectCpuSimdFlags` with the `cdxtexture-catch-bridge-wave679` tag, leaving exact runtime exception and CPU dispatch behavior deferred. The next queue head after Wave679 is `0x00589367 CTexture__ReleaseIncludeNodeTreeRecursive`.

---

## Wave678 CDXTexture Dispatch Prelude Read-Back Note

Wave678 CDXTexture dispatch prelude saved the CFastVB dispatch-table initializer alongside three CDXTexture helpers documented in [`DXTexture.cpp`](../DXTexture.cpp/_index.md). Tag anchor: `cdxtexture-dispatch-prelude-wave678`; the next queue head after this pass was `0x00589200 Catch@00589200`, later hardened by Wave679.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x0058926b` | `int __stdcall CFastVB__InitDispatchTableByCpuFeature(int requested_mode)` | Resets or initializes the active dispatch table from the default table, applies observed Direct3D registry override checks, consults processor feature checks, selects a dispatch-table variant, and returns the recorded dispatch mode. |

Wave678 read-back evidence verified `4` metadata rows, `4` tag rows, `71` xref rows, `148` instruction rows, and `4` clean decompile rows across `0x00588cc6 CDXTexture__ProjectPointToPlaneAndScale` through `0x0058926b CFastVB__InitDispatchTableByCpuFeature`. Post-Wave678 queue telemetry is `6098` total, `3839` commented, `2259` commentless, `1217` exact-undefined signatures, `478` `param_N`, strict clean-signature proxy `3789/6098 = 62.14%`, and next head `0x00589200 Catch@00589200`, later hardened by Wave679. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260521-071055_post_wave678_cdxtexture_dispatch_prelude_verified`.

Exact mode enum, dispatch ABI, runtime CPU behavior, registry override behavior, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave678 CDXTexture dispatch prelude`, `cdxtexture-dispatch-prelude-wave678`, `0x00588cc6 CDXTexture__ProjectPointToPlaneAndScale`, `0x0058926b CFastVB__InitDispatchTableByCpuFeature`, `0x00589200 Catch@00589200`.

---

## Wave676 Texel Factory Tail Read-Back Note

Wave676 texel factory tail saved seven adjacent CFastVB profile constructor, destructor, and factory rows. Tag anchor: `texel-factory-tail-wave676`; the next queue head after this pass is `0x0058864a CDXTexture__InitMappedFileContext`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x00587dee` / `0x00587e06` / `0x00587e1e` | `void * __thiscall CFastVB__*005ea264/274/284*(void * this, void * format_descriptor)` | Profile-init and registry constructor thunks forward the descriptor to the `0x005ea138` unpack-profile registry initializer, bind observed vtables `0x005ea264`, `0x005ea274`, and `0x005ea284`, and return this. |
| `0x00587e36` / `0x00587e4e` | `void * __thiscall CFastVB__TexelCodecProfile_*__ctor(void * this, void * format_descriptor)` | Codec-profile constructors forward the descriptor through the FourCC codec initializer, bind observed vtables `0x005ea294` and `0x005ea2a4`, and are reached from factory DXT-style cases after 0x10f0-byte allocations. |
| `0x00587e66` | `void * __thiscall CFastVB__TexelCodecProfile_scalar_deleting_dtor(void * this, uint delete_flags)` | Scalar-deleting destructor calls the codec-profile destructor, optionally frees this when `delete_flags & 1` is set, and returns this. |
| `0x00587e82` | `void * __stdcall CFastVB__CreateTexelUnpackProfileByFormat(void * format_descriptor)` | Factory reads the format descriptor id at `+0x4`, dispatches numeric and FourCC-like cases, allocates 0x1074/0x10a4/0x10f0-byte profile objects, calls matching constructors, and invokes the observed setup callback when present. |

Wave676 read-back evidence verified `7` metadata rows, `7` tag rows, `13` xref rows, `623` instruction rows, and `7` clean decompile rows across `0x00587dee CFastVB__InitTexelUnpackVTable_005ea264` through `0x00587e82 CFastVB__CreateTexelUnpackProfileByFormat`. Post-Wave676 queue telemetry is `6098` total, `3828` commented, `2270` commentless, `1217` exact-undefined signatures, `489` `param_N`, strict clean-signature proxy `3778/6098 = 61.95%`, and next head `0x0058864a CDXTexture__InitMappedFileContext`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260521-062327_post_wave676_texel_factory_tail_verified`.

Exact format enum, descriptor ABI, FourCC semantics, DXT block ABI, setup callback contract, runtime texture output behavior, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave676 texel factory tail`, `texel-factory-tail-wave676`, `0x00587dee CFastVB__InitTexelUnpackVTable_005ea264`, `0x00587e82 CFastVB__CreateTexelUnpackProfileByFormat`, `0x0058864a CDXTexture__InitMappedFileContext`.

---

## Wave675 Texel Codec Continuation Read-Back Note

Wave675 texel codec continuation saved twenty-two CFastVB-labelled profile constructor, scratch row-window, codec profile, flush/decode/store/load, and destructor-like rows in the same tranche as three CTexture rows in [`texture.cpp`](../texture.cpp/_index.md). Tag anchor: `texel-codec-continuation-wave675`; the next queue head after this pass is `0x00587dee CFastVB__InitTexelUnpackVTable_005ea264`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x00586a55` / `0x00586b63` / `0x00586b7f` / `0x00586b9b` / `0x00586ec7` / `0x00586ee3` / `0x00586eff` / `0x00586f1b` / `0x00587303` / `0x00587322` / `0x0058733e` | `void * __thiscall CFastVB__*005ea128..005ea214*(void * this, void * format_descriptor)` | Profile constructor/init thunks forward the descriptor through the shared texel-unpack profile initializer and bind observed vtables. |
| `0x00586a71` / `0x00587dd6` | `void * __thiscall CFastVB__TexelUnpackProfileRegistry_*__ctor(void * this, void * format_descriptor)` | Registry constructors initialize or forward scratch row-window profile state for packed 16-bit/FourCC-style texel paths; `0x00587dd6 CFastVB__TexelUnpackProfileRegistry_005ea254__ctor` is the Wave675 tail anchor. |
| `0x00586bb7` | `int __fastcall CFastVB__FlushPendingConvertedRows16(void * profile)` | Flush helper writes pending converted two-pixel scratch rows back to the 16-bit source surface and clears the dirty flag. |
| `0x00586f37` | `int __thiscall CFastVB__DecodeRowWindowToScratchPairs(void * this, int row_index, uint column_index, uint decode_if_needed)` | Row-window decoder flushes stale dirty rows, selects a two-pixel row/column window, and expands packed RGBG/GBGR/YUY2/UYVY-style data into scratch float4 pairs. |
| `0x0058735a` / `0x005873f8` | `void __thiscall CFastVB__*DecodedBlock*Scratch(void * this, uint block_x, uint block_y, float * vec4_array, int unused_context)` | Store/load helpers copy vec4 blocks through scratch storage and apply the observed dirty-row or key-color/post-process gates. |
| `0x00587477` / `0x00587663` / `0x0058767b` / `0x00587693` | `void * __thiscall CFastVB__TexelCodecProfile*(void * this, void * format_descriptor)` | Codec profile constructors route FourCC/DXT cases to decode/encode callbacks, copy bounds, align block windows, and bind observed vtables. |
| `0x00587daf` | `void __fastcall CFastVB__TexelPackProfile_scalar_deleting_dtor(void * this)` | Destructor-like helper restores a registry vtable, flushes pending converted rows, frees scratch storage, and tail-calls the base profile destructor. |

Wave675 read-back evidence verified `25` metadata rows, `25` tag rows, `52` xref rows, `1125` instruction rows, and `25` clean decompile rows across `0x005869b0 CTexture__UnpackTexels_Bits16_16_16_ToFloat4` through `0x00587dd6 CFastVB__TexelUnpackProfileRegistry_005ea254__ctor`. Post-Wave675 queue telemetry is `6098` total, `3821` commented, `2277` commentless, `1217` exact-undefined signatures, `496` `param_N`, strict clean-signature proxy `3771/6098 = 61.84%`, and next head `0x00587dee CFastVB__InitTexelUnpackVTable_005ea264`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260521-055935_post_wave675_texel_codec_continuation_verified`.

Exact profile ABI, descriptor layout, FourCC semantics, DXT block ABI, quad-cache contract, runtime texture output behavior, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave675 texel codec continuation`, `texel-codec-continuation-wave675`, `0x005869b0 CTexture__UnpackTexels_Bits16_16_16_ToFloat4`, `0x00587dd6 CFastVB__TexelUnpackProfileRegistry_005ea254__ctor`, `0x00587dee CFastVB__InitTexelUnpackVTable_005ea264`.

---

## Wave674 Texel Unpack Tail Read-Back Note

Wave674 texel unpack tail saved sixteen CFastVB-labelled profile constructor/init thunks and two CFastVB-labelled unpackers in the same tranche as three CTexture rows in [`texture.cpp`](../texture.cpp/_index.md) and four CDXTexture rows in [`DXTexture.cpp`](../DXTexture.cpp/_index.md). Tag anchor: `texel-unpack-tail-wave674`; the next queue head after this pass is `0x005869b0 CTexture__UnpackTexels_Bits16_16_16_ToFloat4`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x0058609e` / `0x0058617c` / `0x00586198` | `void * __thiscall CFastVB__*005ea02x/34/44*(void * this, void * format_descriptor)` | Profile constructor/init thunks reached from `CFastVB__CreateTexelUnpackProfileByFormat` cases `0x22`, `0x23`, and `0x24`; each calls the descriptor ctor, binds its vtable, and returns this with `RET 0x4`. |
| `0x005862cd` / `0x005862e9` / `0x0058641c` | `void * __thiscall CFastVB__*005ea058/68/78*(void * this, void * format_descriptor)` | Adjacent profile constructor/init thunks for case/callsite evidence around `0x28`, `0x29`, and the next factory block, binding vtables `0x005ea058`, `0x005ea068`, and `0x005ea078`. |
| `0x00586519` / `0x00586535` / `0x00586551` / `0x005865ed` | `void * __thiscall CFastVB__TexelUnpackProfile_*__ctor(void * this, void * format_descriptor)` | Profile constructor thunks for cases `0x33`, `0x34`, `0x51`, and `0x3c`, binding vtables `0x005ea088`, `0x005ea098`, `0x005ea0a8`, and `0x005ea0b8`. |
| `0x0058669a` / `0x005866b6` / `0x0058675f` | `void * __thiscall CFastVB__InitTexelUnpackVTable_*(void * this, void * format_descriptor)` | Current-name-retained profile-init thunks for cases `0x3d`, `0x3e`, and `0x3f`, binding vtables `0x005ea0c8`, `0x005ea0d8`, and `0x005ea0e8`. |
| `0x005866d2` | `void __thiscall CFastVB__UnpackTexels_CallbackPerTexel_Stride4_SetZAOne(void * this, uint source_x, uint source_y, float * destination_vec4_array, int unused_context)` | Callback-dispatch stride-4 unpacker advances one dword per texel, calls the indirect unpack dispatcher, forces Z/A to `1.0`, then applies the observed key-color/post-process gates. |
| `0x005867d2` / `0x00586978` / `0x00586994` | `void * __thiscall CFastVB__*005ea0f8/108/118*(void * this, void * format_descriptor)` | Tail profile constructor/init thunks for cases `0x40`, `0x43`, and `0x6e`, binding vtables `0x005ea0f8`, `0x005ea108`, and `0x005ea118`. |
| `0x005868d1` | `void __thiscall CFastVB__UnpackTexels_L16A16_ToFloat4(void * this, uint source_x, uint source_y, float * destination_vec4_array, int unused_context)` | L16A16 unpacker copies 16-bit luminance into RGB and 16-bit alpha into A through the shared source/count/gate fields. |

Wave674 read-back evidence verified `25` metadata rows, `25` tag rows, `25` xref rows, `1125` instruction rows, and `25` clean decompile rows across `0x0058609e CFastVB__TexelUnpackProfile_005ea020__ctor` through `0x00586994 CFastVB__InitTexelUnpackVTable_005ea118`. Post-Wave674 queue telemetry is `6098` total, `3796` commented, `2302` commentless, `1217` exact-undefined signatures, `521` `param_N`, strict clean-signature proxy `3746/6098 = 61.43%`, and next head `0x005869b0 CTexture__UnpackTexels_Bits16_16_16_ToFloat4`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260521-052857_post_wave674_texel_unpack_tail_verified`.

Exact profile ABI, descriptor layout, callback-table contract, format-table contract, lane-order enum contracts, runtime texture output behavior, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave674 texel unpack tail`, `texel-unpack-tail-wave674`, `0x0058609e CFastVB__TexelUnpackProfile_005ea020__ctor`, `0x00586994 CFastVB__InitTexelUnpackVTable_005ea118`, `0x005869b0 CTexture__UnpackTexels_Bits16_16_16_ToFloat4`.

---

## Wave673 Texel Unpack Continuation Read-Back Note

Wave673 texel unpack continuation saved fourteen CFastVB-labelled texel-unpack profile constructor/init thunks, one shared profile scalar-deleting destructor, and five CFastVB-labelled unpackers in the same tranche as three CTexture rows in [`texture.cpp`](../texture.cpp/_index.md) and two CDXTexture rows in [`DXTexture.cpp`](../DXTexture.cpp/_index.md). Tag anchor: `texel-unpack-continuation-wave673`; the next queue head after this pass is `0x0058609e CFastVB__TexelUnpackProfile_005ea020__ctor`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x0058577f` | `void * __thiscall CFastVB__TexelUnpackProfile_005e9f3c__ctor(void * this, void * format_descriptor)` | Profile constructor thunk reached from `CFastVB__CreateTexelUnpackProfileByFormat` case `0x14`; calls the descriptor ctor, binds vtable `0x005e9f3c`, and returns this with `RET 0x4`. |
| `0x0058584f` | `void * __thiscall CFastVB__TexelUnpackProfile_005e9f4c__ctor(void * this, void * format_descriptor)` | Profile constructor thunk for case `0x15`, vtable `0x005e9f4c`. |
| `0x00585908` / `0x00585924` / `0x005859bc` | `void * __thiscall CFastVB__InitTexelUnpackVTable_*(void * this, void * format_descriptor)` | Current-name-retained profile-init thunks for cases `0x16`, `0x17`, and `0x18`, binding vtables `0x005e9f5c`, `0x005e9f6c`, and `0x005e9f7c`. |
| `0x005859d8` | `void __thiscall CFastVB__UnpackTexels_L8ToFloat4(void * this, uint source_x, uint source_y, float * destination_vec4_array, int unused_context)` | L8 unpacker copies byte-scaled luminance to RGB and forces alpha to `1.0` through the shared source/count/gate fields. |
| `0x00585a5f` / `0x00585b19` | `void * __thiscall CFastVB__TexelUnpackProfile_*__ctor(void * this, void * format_descriptor)` | Profile constructor thunks for cases `0x19` and `0x1a`, binding vtables `0x005e9f8c` and `0x005e9f9c`. |
| `0x00585a7b` | `void __thiscall CFastVB__UnpackTexels_L8A8ToFloat4(void * this, uint source_x, uint source_y, float * destination_vec4_array, int unused_context)` | L8A8 unpacker copies byte0-scaled luminance into RGB and byte1-scaled alpha into A. |
| `0x00585b35` | `void __thiscall CFastVB__UnpackTexels_A4L4ToFloat4(void * this, uint source_x, uint source_y, float * destination_vec4_array, int unused_context)` | A4L4 unpacker copies the low nibble into RGB luminance and the high nibble into alpha. |
| `0x00585bd3` | `void * __thiscall CFastVB__TexelUnpackProfile_scalar_deleting_dtor(void * this, byte flags)` | Shared scalar-deleting destructor wrapper calls the profile destructor and conditionally frees with `OID__FreeObject_Callback` when flags bit 0 is set. |
| `0x00585bef` / `0x00585c94` | `void * __thiscall CFastVB__InitTexelUnpackVTable_*(void * this, void * format_descriptor)` | Current-name-retained profile-init thunks for cases `0x1b` and `0x1c`, binding vtables `0x005e9fac` and `0x005e9fbc`. |
| `0x00585c0b` | `void __thiscall CFastVB__UnpackTexels_L16ToFloat4(void * this, uint source_x, uint source_y, float * destination_vec4_array, int unused_context)` | L16 unpacker copies 16-bit-scaled luminance into RGB and forces alpha to `1.0`. |
| `0x00585d6b` / `0x00585d87` / `0x00585e83` / `0x00585f6b` / `0x00585f87` | `void * __thiscall CFastVB__TexelUnpackProfile_*__ctor(void * this, void * format_descriptor)` | Profile constructor thunks for cases `0x1d` through `0x21`, binding vtables `0x005e9fd0`, `0x005e9fe0`, `0x005e9ff0`, `0x005ea000`, and `0x005ea010`. |
| `0x00585fa3` | `void __thiscall CFastVB__UnpackTexels_Signed8_8_8_8_ToFloat4(void * this, uint source_x, uint source_y, float * destination_vec4_array, int unused_context)` | Signed 8-8-8-8 unpacker sign-scales four byte lanes into RGBA and then applies the observed key-color/post-process gates. |

Wave673 read-back evidence verified `25` metadata rows, `25` tag rows, `67` xref rows, `1125` instruction rows, and `25` clean decompile rows across `0x0058577f CFastVB__TexelUnpackProfile_005e9f3c__ctor` through `0x00585fa3 CFastVB__UnpackTexels_Signed8_8_8_8_ToFloat4`. Post-Wave673 queue telemetry is `6098` total, `3771` commented, `2327` commentless, `1217` exact-undefined signatures, `546` `param_N`, strict clean-signature proxy `3721/6098 = 61.02%`, and next head `0x0058609e CFastVB__TexelUnpackProfile_005ea020__ctor`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260521-045554_post_wave673_texel_unpack_continuation_verified`.

Exact profile ABI, descriptor layout, callback-table contract, format-table contract, lane-order enum contracts, runtime texture output behavior, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave673 texel unpack continuation`, `texel-unpack-continuation-wave673`, `0x0058577f CFastVB__TexelUnpackProfile_005e9f3c__ctor`, `0x00585fa3 CFastVB__UnpackTexels_Signed8_8_8_8_ToFloat4`, `0x0058609e CFastVB__TexelUnpackProfile_005ea020__ctor`.

---

## Wave672 Texel Unpack Head Read-Back Note

Wave672 texel unpack head saved nine CFastVB-labelled unpackers in the same tranche as three CTexture rows in [`texture.cpp`](../texture.cpp/_index.md), one current-owner `CMeshCollisionVolume` row in [`MeshCollisionVolume.cpp`](../MeshCollisionVolume.cpp/_index.md), and three CDXTexture rows in [`DXTexture.cpp`](../DXTexture.cpp/_index.md). Tag anchor: `texel-unpack-head-wave672`; the next queue head after this pass is `0x0058577f CFastVB__TexelUnpackProfile_005e9f3c__ctor`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x00584d78` | `void __thiscall CFastVB__UnpackTexels_Bits565ToFloat4(void * this, uint source_x, uint source_y, float * destination_vec4_array, int unused_context)` | RGB565 unpacker expands 5/6/5-bit lanes to RGB and forces alpha to `1.0` through the shared source pointer/count/gate fields. |
| `0x00584e32` | `void __thiscall CFastVB__UnpackTexels_Bits555ToFloat4_AlphaOne(void * this, uint source_x, uint source_y, float * destination_vec4_array, int unused_context)` | 5-5-5 alpha-one unpacker expands three 5-bit color lanes and forces alpha to `1.0`. |
| `0x00584ee9` | `void __thiscall CFastVB__UnpackTexels_Bits1555ToFloat4(void * this, uint source_x, uint source_y, float * destination_vec4_array, int unused_context)` | 1-5-5-5 unpacker expands three 5-bit color lanes and the high-bit alpha lane. |
| `0x00584fae` | `void __thiscall CFastVB__UnpackTexels_Bits4444ToFloat4(void * this, uint source_x, uint source_y, float * destination_vec4_array, int unused_context)` | 4-4-4-4 unpacker expands four 4-bit lanes into float4 output rows. |
| `0x00585072` | `void __thiscall CFastVB__UnpackTexels_Bits2_10_10_10_ToFloat4(void * this, uint source_x, uint source_y, float * destination_vec4_array, int unused_context)` | 2-10-10-10 unpacker writes R/G/B from low/mid/high 10-bit fields and A from the top 2 bits. |
| `0x00585161` | `void __thiscall CFastVB__UnpackTexels_Bits8888ToFloat4(void * this, uint source_x, uint source_y, float * destination_vec4_array, int unused_context)` | 8-8-8-8 unpacker writes four byte lanes from the 32-bit source word. |
| `0x00585220` | `void __thiscall CFastVB__UnpackTexels_Bits888ToFloat4_AlphaOne(void * this, uint source_x, uint source_y, float * destination_vec4_array, int unused_context)` | 8-8-8 alpha-one unpacker writes three byte lanes and alpha `1.0`. |
| `0x005852d5` | `void __thiscall CFastVB__UnpackTexels_Bits16_16_ToFloat4_RG(void * this, uint source_x, uint source_y, float * destination_vec4_array, int unused_context)` | 16-16 RG unpacker writes two 16-bit lanes followed by B=`1.0` and A=`1.0`. |
| `0x00585380` | `void __thiscall CFastVB__UnpackTexels_Bits2_10_10_10_ToFloat4_Alt(void * this, uint source_x, uint source_y, float * destination_vec4_array, int unused_context)` | Alternate 2-10-10-10 unpacker writes R/G/B from high/mid/low 10-bit fields and A from the top 2 bits. |

Wave672 read-back evidence verified `16` metadata rows, `16` tag rows, `16` xref rows, `1616` instruction rows, and `16` clean decompile rows across `0x00584b5f CTexture__UnpackTexels_Bgr8ToFloat4` through `0x005856b8 CDXTexture__UnpackTexels_Bits332A8ToFloat4`. Post-Wave672 queue telemetry is `6098` total, `3746` commented, `2352` commentless, `1217` exact-undefined signatures, `571` `param_N`, strict clean-signature proxy `3696/6098 = 60.61%`, and next head `0x0058577f CFastVB__TexelUnpackProfile_005e9f3c__ctor`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260521-042809_post_wave672_texel_unpack_head_verified`.

Exact profile ABI, format-table contract, lane-order enum contracts, runtime texture output behavior, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave672 texel unpack head`, `texel-unpack-head-wave672`, `0x00584b5f CTexture__UnpackTexels_Bgr8ToFloat4`, `0x005856b8 CDXTexture__UnpackTexels_Bits332A8ToFloat4`, `0x0058577f CFastVB__TexelUnpackProfile_005e9f3c__ctor`.

---

## Wave670 Texel Packer Continuation Read-Back Note

Wave670 texel packer continuation saved three CFastVB-labelled packers in the same continuation tranche as six CTexture rows documented in [`texture.cpp`](../texture.cpp/_index.md). Tag anchor: `texel-packer-continuation-wave670`; the next queue head after this pass is `0x00584724 CDXTexture__PackTexels_CallbackPerTexel_RepeatA`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x00584144` | `void __thiscall CFastVB__PackTexels_NoDither_Bits16_16(void * this, uint output_x, uint output_y, float * source_vec4_array, int unused_context)` | Currently named no-dither 16-16 packer callback writes one 32-bit texel from two rounded 16-bit source lanes; the current decompile still reads the shared dither-table term at `+0x34` before rounding. |
| `0x0058423f` | `void __thiscall CFastVB__PackTexels_NoDither_Bits2_10_10_10(void * this, uint output_x, uint output_y, float * source_vec4_array, int unused_context)` | Currently named no-dither 2-10-10-10 packer callback writes one 32-bit texel from four rounded source lanes; the current decompile still reads the shared dither-table term at `+0x34` before rounding. |
| `0x0058439e` | `void __thiscall CFastVB__PackTexels_NoDither_Bits16_16_16_16(void * this, uint output_x, uint output_y, float * source_vec4_array, int unused_context)` | Currently named no-dither 16-16-16-16 packer callback writes two 32-bit words per texel from four rounded 16-bit source lanes; the current decompile still reads the shared dither-table term at `+0x34` before rounding. |

Wave670 read-back evidence verified `9` metadata rows, `9` tag rows, `9` xref rows, `729` instruction rows, and `9` clean decompile rows across `0x00583c8e CTexture__PackTexels_Dither_Bits8_8` through `0x0058463a CTexture__PackTexels_Dither_L16_Alt`. Post-Wave670 queue telemetry is `6098` total, `3722` commented, `2376` commentless, `1217` exact-undefined signatures, `595` `param_N`, strict clean-signature proxy `3672/6098 = 60.22%`, and next head `0x00584724 CDXTexture__PackTexels_CallbackPerTexel_RepeatA`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260521-033410_post_wave670_texel_packer_continuation_verified`.

Exact dither table provenance, exact no-dither naming rationale, texel-pack callback ABI, channel-order enum contracts, runtime texture output behavior, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave670 texel packer continuation`, `texel-packer-continuation-wave670`, `0x00583c8e CTexture__PackTexels_Dither_Bits8_8`, `0x0058463a CTexture__PackTexels_Dither_L16_Alt`, `0x00584724 CDXTexture__PackTexels_CallbackPerTexel_RepeatA`.

---

## Wave669 Dither Packer Tail Read-Back Note

Wave669 dither packer tail saved two CFastVB-labelled luminance packers alongside eight CDXTexture-labelled packers in [`DXTexture.cpp`](../DXTexture.cpp/_index.md) and two CTexture-labelled packers in [`texture.cpp`](../texture.cpp/_index.md). Tag anchor: `dither-packer-tail-wave669`; the next queue head after this pass is `0x00583c8e CTexture__PackTexels_Dither_Bits8_8`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x00583891` | `void __thiscall CFastVB__PackTexels_Dither_L8(void * this, uint output_x, uint output_y, float * source_vec4_array, int unused_context)` | Dithered luminance packer writes one 8-bit output from weighted RGB lanes using constants at `0x005e72dc/0x005e72e0/0x005e72e4`, the observed 8-bit scale, and the shared dither table. |
| `0x00583979` | `void __thiscall CFastVB__PackTexels_Dither_A8L8(void * this, uint output_x, uint output_y, float * source_vec4_array, int unused_context)` | Dithered A8L8-style packer writes a 16-bit word with dithered alpha in the high byte and weighted RGB luminance in the low byte. |

Wave669 read-back evidence verified `12` metadata rows, `12` tag rows, `12` xref rows, `444` instruction rows, and `12` clean decompile rows across `0x00582ef8 CDXTexture__PackTexels_Dither_Bits2_10_10_10` through `0x00583ba4 CTexture__PackTexels_Dither_L16`. Post-Wave669 queue telemetry is `6098` total, `3713` commented, `2385` commentless, `1217` exact-undefined signatures, `604` `param_N`, strict clean-signature proxy `3663/6098 = 60.07%`, and next head `0x00583c8e CTexture__PackTexels_Dither_Bits8_8`. Exact luminance contract, dither table provenance, texel-pack callback ABI, runtime texture output behavior, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave669 dither packer tail`, `dither-packer-tail-wave669`, `0x00582ef8 CDXTexture__PackTexels_Dither_Bits2_10_10_10`, `0x00583ba4 CTexture__PackTexels_Dither_L16`, `0x00583c8e CTexture__PackTexels_Dither_Bits8_8`.

---

## Wave668 Dither Packer Head Read-Back Note

Wave668 dither packer head saved seven CFastVB-labelled dither-packer rows alongside one `CTexture__PostProcessDecodedTexels_GammaOrSquare` row and four CTexture-labelled packers documented in [`texture.cpp`](../texture.cpp/_index.md). Tag anchor: `dither-packer-head-wave668`; the next queue head after this pass is `0x00582ef8 CDXTexture__PackTexels_Dither_Bits2_10_10_10`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x00582244` | `void __thiscall CFastVB__PackTexels_Dither_Bits8_8_8_BGR(void * this, uint output_x, uint output_y, float * source_vec4_array, int unused_context)` | Dithered callback at table slot `0x005e9f44`; writes B,G,R byte output through observed output pointer fields `+0x1058/+0x105c/+0x20`, count `+0x1060`, dither table `+0x34`, optional domain conversion `+0x1050`, and optional normalization `+0x10`. |
| `0x00582355` | `void __thiscall CFastVB__PackTexels_Dither_Bits8_8_8_8_ARGB(void * this, uint output_x, uint output_y, float * source_vec4_array, int unused_context)` | Dithered callback at table slot `0x005e9f54`; writes one ARGB8888-style dword from source vec4 lanes with the same shared stride/base/count/dither/conversion gates. |
| `0x0058249e` | `void __thiscall CFastVB__PackTexels_Dither_Bits8_8_8_RGB(void * this, uint output_x, uint output_y, float * source_vec4_array, int unused_context)` | Dithered callback at table slot `0x005e9f64`; writes 24-bit RGB byte output with the observed 8-bit scale and per-pixel dither term. |
| `0x005825c3` | `void __thiscall CFastVB__PackTexels_Dither_Bits5_6_5(void * this, uint output_x, uint output_y, float * source_vec4_array, int unused_context)` | Dithered callback at table slot `0x005e9f74`; writes 16-bit RGB565-style output using observed 5/6/5 scale constants. |
| `0x005826e8` | `void __thiscall CFastVB__PackTexels_Dither_Bits5_5_5(void * this, uint output_x, uint output_y, float * source_vec4_array, int unused_context)` | Dithered callback at table slot `0x005e9f84`; writes 16-bit RGB555-style output with observed 5-bit scale constants. |
| `0x0058280d` | `void __thiscall CFastVB__PackTexels_Dither_A1R5G5B5(void * this, uint output_x, uint output_y, float * source_vec4_array, int unused_context)` | Dithered callback at table slot `0x005e9f94`; derives one-bit alpha from source alpha plus the dither term and packs RGB with 5-bit scale constants. |
| `0x00582950` | `void __thiscall CFastVB__PackTexels_Dither_A4R4G4B4(void * this, uint output_x, uint output_y, float * source_vec4_array, int unused_context)` | Dithered callback at table slot `0x005e9fa4`; rounds alpha/RGB lanes with observed 4-bit scale constants and packs four nibbles. |

Wave668 read-back evidence verified `12` metadata rows, `12` tag rows, `52` xref rows, `444` instruction rows, and `12` clean decompile rows across the dither-packer head cluster from `0x0058210e CTexture__PostProcessDecodedTexels_GammaOrSquare` through `0x00582dd3 CTexture__PackTexels_Dither_Bits444`. Post-Wave668 queue telemetry is `6098` total, `3701` commented, `2397` commentless, `1217` exact-undefined signatures, `616` `param_N`, strict clean-signature proxy `3651/6098 = 59.87%`, and next head `0x00582ef8 CDXTexture__PackTexels_Dither_Bits2_10_10_10`. Exact dither table provenance, texel-pack callback ABI, channel-order enum contracts, runtime texture output behavior, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave668 dither packer head`, `dither-packer-head-wave668`, `0x0058210e CTexture__PostProcessDecodedTexels_GammaOrSquare`, `0x00582dd3 CTexture__PackTexels_Dither_Bits444`, `0x00582ef8 CDXTexture__PackTexels_Dither_Bits2_10_10_10`.

---

## Wave667 Texel Profile Prep Read-Back Note

Wave667 texel-profile prep saved seven CFastVB-labelled rows in the texel profile preparation cluster, alongside three `CDXTexture__*` rows documented in [`DXTexture.cpp`](../DXTexture.cpp/_index.md). Tag anchor: `texel-profile-prep-wave667`; the next queue head after this pass is `0x0058210e CTexture__PostProcessDecodedTexels_GammaOrSquare`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x00581263` | `void __fastcall CFastVB__TexelUnpackProfile__dtor(void * this)` | Resets the observed texel-unpack profile vtable and frees the vec4 scratch/output pointer at `+0x1054`. |
| `0x00581279` | `int __thiscall CFastVB__ConvertTexelVectorDomain(void * this, float * source_vec4_array, int unused_context)` | Converts count-controlled vec4 texels from `source_vec4_array` into the scratch/output buffer at `+0x1054` using source mode `+0x08`, target mode `+0x1050`, count `+0x1060`, observed scale/bias paths for modes `1-3`, and clamp-to-0..1 handling for mode `4`. |
| `0x0058183d` | `void __fastcall CFastVB__TexelCodecProfile__dtor(void * this)` | Resets the codec-profile vtable, frees per-cell allocations from the observed `+0x10ec` table across bounds `+0x10c8/+0x10cc` and `+0x10bc/+0x10c4`, frees `+0x10e4/+0x10ec`, then chains to `CFastVB__TexelUnpackProfile__dtor`. |
| `0x005819b8` | `double __stdcall CFastVB__LookupCurveFromRsqrtScaledInput(float sample_value)` | Uses a fast reciprocal-square-root-derived scaled index from `sample_value`, rounds to an observed table slot, handles negative rounded indices with the unsigned-adjust constant, and linearly interpolates the table rooted at `DAT_005e96d0`. |
| `0x00581a08` | `double __stdcall CFastVB__LookupCurveFromSquaredInput(float sample_value)` | Squares and scales `sample_value`, rounds to an observed table index, handles negative rounded indices with the same unsigned-adjust constant, and linearly interpolates the table rooted at `DAT_005e9ad0`. |
| `0x00581cc0` | `int __thiscall CFastVB__TexelUnpackProfile__InitConversionScratch(void * this, void * peer_profile, int unused_context)` | Compares mode fields, selects target conversion mode `+0x1050`, allocates count-based vec4 scratch/output storage at `+0x1054`, vector-constructs rows, returns the observed allocation failure code on null, and mirrors profile flag `+0x14` when both profiles have `+0x10` set. |
| `0x00581e1c` | `void __thiscall CFastVB__TexelUnpackProfile__ZeroTexelsMatchingKeyColor(void * this, float * texel_vec4_array, uint unused_context)` | Walks count-controlled vec4 texels and zeros all four channels when they exactly match the key vector stored at `+0x24/+0x28/+0x2c/+0x30`. |

Wave667 read-back evidence verified `10` metadata rows, `10` tag rows, `180` xref rows, `870` instruction rows, and `10` clean decompile rows across the texel-profile prep cluster. Post-Wave667 queue telemetry is `6098` total, `3689` commented, `2409` commentless, `1217` exact-undefined signatures, `628` `param_N`, strict clean-signature proxy `3639/6098 = 59.68%`, and next head `0x0058210e CTexture__PostProcessDecodedTexels_GammaOrSquare`. Exact texel-profile/profile ABI, texel-domain enum, color-space meaning, DXT format contract, curve identity, callback contract, runtime texture conversion behavior, runtime transparency behavior, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave667 texel-profile prep`, `texel-profile-prep-wave667`, `0x00581263 CFastVB__TexelUnpackProfile__dtor`, `0x00581e8c CDXTexture__NormalizeAndCopyVec4Array`, `0x0058210e CTexture__PostProcessDecodedTexels_GammaOrSquare`.

---

## Wave666 Texture Dual-Profile/Upload Read-Back Note

Wave666 texture dual-profile/upload saved six CFastVB-labelled rows in the texture conversion/profile-lifetime tail, alongside four `CDXTexture__*` upload rows documented in [`DXTexture.cpp`](../DXTexture.cpp/_index.md). Tag anchor: `texture-dual-profile-wave666`; the next queue head after this pass is `0x00581263 CFastVB__TexelUnpackProfile__dtor`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x0057fa10` | `int * __thiscall CFastVB__BlendWeightTable_scalar_deleting_dtor(void * this, uint delete_flags, int unused_context)` | Deleting-destructor wrapper for allocated blend-weight table storage; `delete_flags` bit `2` backs up to the count prefix and runs `CDXTexture__RepeatCallbackN` with the observed entry cleanup callback before optional base free, while bit `1` controls object/base freeing. |
| `0x0057fa5c` | `int __fastcall CFastVB__BlendDualProfileBoneWeights(void * dual_profile_context)` | Builds X/Y/Z resample bucket tables from profile extents at `+0x1060/+0x1064/+0x1068`, allocates vec4 scratch rows and 0xc-byte weight-table entries, reads source rows through vtable slot `+4`, applies weighted/clamped 4-float accumulation, and writes destination rows through vtable slot `+8`. |
| `0x00580120` | `int __fastcall CFastVB__RunDualProfileConversionStage(void * dual_profile_context)` | Validates source/destination depth fields at `+0x1068` are single-slice, builds X/Y resample bucket tables, allocates temporary vec4 rows, reads source rows through vtable slot `+4`, and writes destination rows through vtable slot `+8`. |
| `0x0058070e` | `int __thiscall CFastVB__InitDualTexelConversionPipeline(void * this, void * source_profile_descriptor, void * destination_profile_descriptor, int conversion_flags, uint unused_context)` | Initializes the two-profile conversion state, validates observed mode/flag bits, creates paired texel-unpack profiles, initializes conversion scratch, tries the direct copy/resample/downsample helpers through the dual-profile weighted stages, then releases both active profiles. |
| `0x005809de` | `int __fastcall CFastVB__ShutdownActiveProfile(void * active_profile_slot)` | Calls active profile vtable slot `+0x28`, then vtable slot `+0x08` if the pointer remains present, clears the slot, and returns zero. |
| `0x00580eef` | `int __fastcall CFastVB__ShutdownActiveProfile_Thunk(void * active_profile_slot)` | Thunk/alias entry to the same active-profile shutdown body. |

Wave666 read-back evidence verified `10` metadata rows, `10` tag rows, `22` xref rows, `1060` instruction rows, and `10` clean decompile rows across the texture dual-profile/upload tail. Post-Wave666 queue telemetry is `6098` total, `3679` commented, `2419` commentless, `1217` exact-undefined signatures, `638` `param_N`, strict clean-signature proxy `3629/6098 = 59.51%`, and next head `0x00581263 CFastVB__TexelUnpackProfile__dtor`. Exact profile/layout identity, exact descriptor layout, flag enum naming, callback body semantics, COM/D3D interface contracts, UpdateSurface identity, runtime texture conversion behavior, runtime upload behavior, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave666 texture dual-profile/upload`, `texture-dual-profile-wave666`, `0x0057fa10 CFastVB__BlendWeightTable_scalar_deleting_dtor`, `0x00580eef CFastVB__ShutdownActiveProfile_Thunk`, `0x00581263 CFastVB__TexelUnpackProfile__dtor`.

---

## Wave665 Texture Resample Surface/Volume Read-Back Note

Wave665 texture resample surface/volume saved three CFastVB-labelled helper rows in the texture copy/resample island, alongside six `CDXTexture__*` rows documented in [`DXTexture.cpp`](../DXTexture.cpp/_index.md). Tag anchor: `texture-resample-wave665`; the next queue head after this pass is `0x0057fa10 CFastVB__BlendWeightTable_scalar_deleting_dtor`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x0057e200` | `int __fastcall CFastVB__BlendEqualDimensionVolumeData(void * texture_resample_context)` | Validates equal source/destination width, height, and depth fields, then copies volume rows through source vtable read slot `+4` and destination vtable write slot `+8` using one vector-row scratch buffer. |
| `0x0057e2de` | `int __fastcall CFastVB__BlendClampedVolumeData(void * texture_resample_context)` | Handles mode byte `1` by sizing source/destination vector-row scratch buffers, copying overlapping source rows, and writing zero-filled destination rows for extents beyond the copied region. |
| `0x0057ef10` | `void * __stdcall CFastVB__BuildResampleKernel1D(int wrap_edges)` | Builds and returns an allocated one-dimensional resample-kernel table from source/destination counts held in caller registers; entries store low/high sample indices and bilinear weights while `wrap_edges` controls observed edge wrapping versus clamping. |

Wave665 read-back evidence verified `9` metadata rows, `9` tag rows, `13` xref rows, `333` instruction rows, and `9` clean decompile rows across the texture resample surface/volume island. Post-Wave665 queue telemetry is `6098` total, `3669` commented, `2429` commentless, `1217` exact-undefined signatures, `648` `param_N`, strict clean-signature proxy `3619/6098 = 59.35%`, and next head `0x0057fa10 CFastVB__BlendWeightTable_scalar_deleting_dtor`. Exact texture surface/context layout, palette contract, vtable contract, edge-mode naming, resample-kernel layout, CFastVB owner identity, runtime copy behavior, runtime resample/downsample quality, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave665 texture resample surface/volume`, `texture-resample-wave665`, `0x0057e0c3 CDXTexture__ConvertSurfaceDirectCopyOrDxtCopy`, `0x0057f391 CDXTexture__ResampleVolumeTrilinear`, `0x0057fa10 CFastVB__BlendWeightTable_scalar_deleting_dtor`.

---

## Wave664 Texture Downsample Kernels Read-Back Note

Wave664 texture downsample kernels saved five CFastVB-labelled helper rows in the texture downsample island, alongside seven `CDXTexture__Average2x2Block_*` rows documented in [`DXTexture.cpp`](../DXTexture.cpp/_index.md). Tag anchor: `texture-downsample-wave664`; the next queue head after this pass is `0x0057e0c3 CDXTexture__ConvertSurfaceDirectCopyOrDxtCopy`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x0057d216` | `void __fastcall CFastVB__DispatchMmxKernel_00657974(void * downsample_context)` | Reads source/destination surface pointers and extent/stride fields from the two-slot downsample context, then calls the CPU-selected MMX-style function pointer at `0x00657974`. |
| `0x0057d4ad` | `void __fastcall CFastVB__DispatchMmxKernel_00657978(void * downsample_context)` | Same observed context shape, calling the CPU-selected MMX-style function pointer at `0x00657978`. |
| `0x0057d9f1` | `int __fastcall CFastVB__Downsample2x1_R5G6B5(void * downsample_context)` | Retained-name byte-lane helper that reads paired source samples from adjacent rows and writes one packed output byte using `0xe3/0x1c` masks and rounded sums. |
| `0x0057db30` | `int __fastcall CFastVB__Downsample2x1_L8(void * downsample_context)` | Retained-name byte-luminance helper that averages observed 2x2 source bytes into one destination byte with a rounded `+2` bias. |
| `0x0057dbcb` | `int __fastcall CFastVB__Downsample2x1_A1R5G5B5(void * downsample_context)` | Retained-name helper that averages observed packed 16-bit source texels through `0xe3/0xff1c`-style masks and rounded sums before writing a destination word. |

Wave664 read-back evidence verified `12` metadata rows, `12` tag rows, `12` xref rows, `444` instruction rows, and `12` clean decompile rows across the texture downsample kernel island. Post-Wave664 queue telemetry is `6098` total, `3660` commented, `2438` commentless, `1217` exact-undefined signatures, `657` `param_N`, strict clean-signature proxy `3610/6098 = 59.20%`, and next head `0x0057e0c3 CDXTexture__ConvertSurfaceDirectCopyOrDxtCopy`. Exact surface/context layout, CPU dispatch pointer identity, packed format contracts, retained CFastVB owner identity, runtime downsample behavior, runtime filter quality, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave664 texture downsample kernels`, `texture-downsample-wave664`, `0x0057d216 CFastVB__DispatchMmxKernel_00657974`, `0x0057df84 CDXTexture__Average2x2Block_A4L4`, `0x0057e0c3 CDXTexture__ConvertSurfaceDirectCopyOrDxtCopy`.

---

## Wave663 Mapped Texture Resample Setup Read-Back Note

Wave663 mapped texture resample setup saved two CFastVB-labelled setup helpers in the mapped texture conversion bridge, alongside `0x0057c7a4 CMeshCollisionVolume__LoadMappedTextureResourcesByMode` and `0x0057cc7b Math__FloorFloatToDouble`. Tag anchor: `mapped-texture-resample-wave663`; the next queue head after this pass is `0x0057d216 CFastVB__DispatchMmxKernel_00657974`.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x0057cc8e` | `void __fastcall CFastVB__ClearTripleDword(void * triple_dword)` | Zeroes three consecutive dwords at offsets `0x00/0x04/0x08`; xrefs use it as callback/table data in dual-profile conversion paths. |
| `0x0057cca4` | `int * __stdcall CFastVB__BuildResampleKernelBuckets(uint output_count, int source_count, int clamp_edges)` | Allocates a variable-length resample bucket table, uses `Math__FloorFloatToDouble`, accumulates per-source weights, and records per-output bucket offsets. |

Wave663 read-back evidence verified `4` metadata rows, `4` tag rows, `9` xref rows, `148` instruction rows, and `4` clean decompile rows across the bridge. Post-Wave663 queue telemetry is `6098` total, `3648` commented, `2450` commentless, `1217` exact-undefined signatures, `669` `param_N`, strict clean-signature proxy `3598/6098 = 59.00%`, and next head `0x0057d216 CFastVB__DispatchMmxKernel_00657974`. Exact record ownership, callback ABI, resample kernel table layout, runtime texture export behavior, runtime resampling quality, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave663 mapped texture resample setup`, `mapped-texture-resample-wave663`, `0x0057c7a4 CMeshCollisionVolume__LoadMappedTextureResourcesByMode`, `0x0057cca4 CFastVB__BuildResampleKernelBuckets`, `0x0057d216 CFastVB__DispatchMmxKernel_00657974`.

---

## Wave563 Signature/Comment Hardening (2026-05-18)

Wave563 saved source-adjacent signatures, comments, and tags for the five retail CFastVB tail functions. No renames or boundary recovery were needed.

| Address | Saved signature | Evidence |
|---------|-----------------|----------|
| `0x0051a270` | `int __thiscall CFastVB__Create(void * this)` | Allocates a 0x2c `CVBuffer`, calls `CVBuffer__CreateDynamic(this+0x0c, 0x1c, 0x144)`, releases on negative result, and registers the buffer through `D3DBufferRegistry__MoveToFreeList`. |
| `0x0051a340` | `void __thiscall CFastVB__Destroy(void * this)` | Releases the instance vertex buffer and shared static index buffer `DAT_00897a90`, clearing both pointers. |
| `0x0051a380` | `ushort __thiscall CFastVB__LockAligned(void * this, void * * out_vertex_data, int vertex_count)` | `RET 0x8` proves two stack arguments; aligns the cursor to a 4-vertex boundary and locks `vertex_count * 0x1c` bytes with discard or no-overwrite flags. |
| `0x0051a430` | `ushort __thiscall CFastVB__Lock(void * this, void * * out_vertex_data, int vertex_count)` | `RET 0x8` proves two stack arguments; delegates to aligned lock when no batch is active and flushes through `CFastVB__Render` on overflow. |
| `0x0051a510` | `void __thiscall CFastVB__Render(void * this)` | Unlocks/binds the vertex buffer, lazily creates shared `CIBuffer` index_count 0x1d4c, fills the quad-index pattern, binds indices, sets handle `0x144`, draws indexed primitive type 4, and resets batch state. |

Static evidence also corrected the older max-vertex wording: `0x144` is FVF/vertex-shader-format evidence, while the observed global CFastVB-style state initializes `this+0x0c` to `0x1388`. This remains static retail/source evidence only; concrete layouts, D3D runtime behavior, BEA launch, patching, and rebuild parity are not proven by this wave.

---

## Wave650-Wave655 Strip Pipeline Hardening (2026-05-20, Wave885 addendum 2026-05-26)

The `CFastVB` owner prefix also appears on the retail triangle-strip pipeline reached from `CDXMeshVB__BuildStripBatchesAndEmitIndexBuffer`. The current checkout does not include `FastVB.cpp`, `DXMeshVB.cpp`, or `DXMeshVB.h`, so these rows are static retail Ghidra evidence only and are documented in more detail under [`DXMeshVB.cpp`](../DXMeshVB.cpp/_index.md).

Wave650 saved the strip setup, word-span, edge-record, and adjacency rows through `CFastVB__BuildTriangleAdjacency`. Wave651 saved the open-edge/next-triangle/seed-strip candidate-selection rows. Wave652 saved candidate merge/order and strip-index emission rows.

Wave885 CFastVB strip-batch builder returned to the central raw row in this same pipeline: `0x005715b0 CFastVB__BuildStripBatchesFromIndexBuffer`. The `cfastvb-strip-batch-builder-wave885` pass preserved the current signature display `int CFastVB__BuildStripBatchesFromIndexBuffer(void)` because Ghidra still reports locked/hidden parameter storage, while the saved comment records the observed ECX receiver context and `RET 0x18`. Static evidence ties the row to the only caller `CDXMeshVB__BuildStripBatchesAndEmitIndexBuffer`, 16-bit index-word span growth/copy, `CFastVB__BuildTriangleAdjacency`, `CFastVB__GenerateStripCandidatesFromAdjacency`, `CFastVB__MergeAndOrderStripBatches`, and cleanup of candidate, edge-bucket, overflow, and local spans. Queue after Wave885 is `6113` total, `5968` commented, `145` commentless, 0 exact-undefined signatures, 0 `param_N`, comment-backed proxy `5968/6113 = 97.63%`, strict clean-signature proxy `5968/6113 = 97.63%`, and next raw commentless row `0x00573d80 CTexture__InsertNodeIntoTree`; verified backup `[maintainer-local-ghidra-backup-root]\BEA_20260526-015531_post_wave885_cfastvb_strip_batch_builder_verified`. Exact CFastVB container/triangle/edge/candidate layouts, exact locked ABI, runtime strip quality, concrete D3D index-buffer behavior, BEA patching, and rebuild parity remain unproven.

Wave653 CFastVB vertex-cache/scoring hardening saved:

| Address | Name | Saved Signature | Evidence |
|---------|------|-----------------|----------|
| `0x005721f0` | `CFastVB__SeedVertexCacheFromTriangleRefs` | `void __stdcall CFastVB__SeedVertexCacheFromTriangleRefs(void * vertex_cache, void * strip_batch)` | Seeds vertex cache entries from each triangle reference in a strip batch. |
| `0x00572310` | `CFastVB__SeedVertexCacheFromTriangle` | `void __stdcall CFastVB__SeedVertexCacheFromTriangle(void * vertex_cache, void * triangle)` | Corrects stale `CDXTexture__InsertUniqueTripletAtFront` ownership; inserts a single triangle's vertex ids into the cache front when absent. |
| `0x005723c0` | `CFastVB__ComputeAverageVertexOverlapScore_005723c0` | `double __stdcall CFastVB__ComputeAverageVertexOverlapScore_005723c0(void * vertex_cache, void * strip_batch)` | Computes the average cached-vertex overlap score for a strip batch. |
| `0x00572490` | `CFastVB__CountTriangleVerticesInSet_00572490` | `int __stdcall CFastVB__CountTriangleVerticesInSet_00572490(void * vertex_cache, void * triangle)` | Counts how many triangle vertices are present in the current vertex cache. |
| `0x00572500` | `CFastVB__CountResolvedOppositeEdges` | `char __stdcall CFastVB__CountResolvedOppositeEdges(void * triangle, void * edge_buckets)` | Counts resolved opposite adjacency records for a triangle's three edges. |
| `0x00572570` | `CFastVB__ComputeAverageUnresolvedEdgesPerBatch` | `double __stdcall CFastVB__ComputeAverageUnresolvedEdgesPerBatch(void * candidate_bucket)` | Scores a candidate bucket by average unresolved edge count. |
| `0x005725e0` | `CFastVB__GenerateStripCandidatesFromAdjacency` | `void __thiscall CFastVB__GenerateStripCandidatesFromAdjacency(void * this, void * out_candidate_span, void * triangle_record_span, void * edge_buckets, int seed_bucket_limit, void * edi_context)` | Builds seed candidate buckets from adjacency, expands linked candidates, scores buckets, and initializes parent links into the output span. |

Wave653 read-back evidence: dry/apply/final dry reported `updated=0 skipped=7 renamed=0 would_rename=1 signature_updated=7 missing=0 bad=0`, then `updated=7 skipped=0 renamed=1 would_rename=0 signature_updated=7 missing=0 bad=0`, then `updated=0 skipped=7 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`. Post exports verified `7` metadata rows, `7` tag rows, `8` xref rows, `315` instruction rows, and `7` clean decompile rows. Queue after Wave653 is `6093` total, `3543` commented, `2550` commentless, `1217` exact-undefined signatures, `765` `param_N`, comment-backed proxy `3543/6093 = 58.15%`, strict clean-signature proxy `3491/6093 = 57.30%`, and next head `0x00572e40 CTexture__DestroyNodeTreeAndStorage`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260520-192250_post_wave653_cfastvb_vertex_cache_scoring_verified`.

Exact CFastVB/cache/span/batch/edge/triangle/candidate layouts, runtime strip quality, concrete D3D output, BEA patching, and rebuild parity remain unproven.

Wave654 CTexture/RB-tree helper hardening then hardened eight adjacent CTexture-labelled red-black-tree/list helpers that are also reached by the CFastVB tree routines in this strip-pipeline address band: `CTexture__DestroyNodeTreeAndStorage`, `CTexture__EraseNodeFromTree`, `CTexture__DestroySubtreeRecursive`, `CTexture__WalkNodeListUntilSentinel`, `CTexture__RotateTreeLeft`, `CTexture__InitTreeNodeParentAndKey`, `CTexture__TreeIteratorNext`, and `CTexture__TreeIteratorPrev`. The Wave654 queue after refresh is `6093` total, `3551` commented, `2542` commentless, `1217` exact-undefined signatures, `757` `param_N`, comment-backed proxy `3551/6093 = 58.28%`, strict clean-signature proxy `3501/6093 = 57.46%`, and next head `0x00572f00 CFastVB__InitDwordSpanBuilderState_00572f00`; verified backup `[maintainer-local-ghidra-backup-root]\BEA_20260520-195520_post_wave654_ctexture_tree_verified`. This is shared static Ghidra metadata evidence only; exact owner/template identity, concrete tree/node layouts, runtime texture/CFastVB behavior, BEA patching, and rebuild parity remain unproven.

Wave655 CFastVB span/tree utility hardening saved twenty-one adjacent helper rows at the next queue head:

| Address | Name | Saved Signature | Evidence |
|---------|------|-----------------|----------|
| `0x00572f00` | `CFastVB__InitDwordSpanBuilderState_00572f00` | `void __thiscall CFastVB__InitDwordSpanBuilderState_00572f00(void * this, void * source_flag, void * unused_context)` | Copies one byte from `source_flag`, clears span-builder slots at `+0x04/+0x08/+0x0c`, and ignores the trailing context argument. |
| `0x00572f20` | `CFastVB__AppendDwordRangeToSpanBuilder_00572f20` | `void __thiscall CFastVB__AppendDwordRangeToSpanBuilder_00572f20(void * this, void * dest_cursor, void * range_cursor, void * unused_context)` | Copies dwords from `range_cursor` to the builder current pointer and advances `this+0x08`. |
| `0x00572f50` | `CFastVB__CopyDwordRange` | `void __stdcall CFastVB__CopyDwordRange(void * range_start, void * range_end, void * dest_or_null)` | Copies a dword range when the destination is non-null. |
| `0x00572f80` | `CFastVB__GetWordCapacity` | `int __fastcall CFastVB__GetWordCapacity(void * span_state)` | Returns word-span capacity from begin/end pointers. |
| `0x00572fa0` | `CFastVB__InsertWordAndGrow` | `void * __thiscall CFastVB__InsertWordAndGrow(void * this, void * insert_at, void * value_ptr, void * unused_context)` | Inserts a word value, shifting in-place or allocating/growing the span as needed. |
| `0x00573140` | `CFastVB__CopyWordRange` | `void __stdcall CFastVB__CopyWordRange(void * range_start, void * range_end, void * dest_or_null)` | Copies a word range when the destination is non-null. |
| `0x00573170` | `CFastVB__InsertDwordAndGrow` | `void * __thiscall CFastVB__InsertDwordAndGrow(void * this, void * insert_at, void * value_ptr, void * unused_context)` | Inserts a dword value, shifting in-place or allocating/growing the span as needed. |
| `0x00573310` | `CFastVB__CountDwordsFromPointerSpan` | `int __fastcall CFastVB__CountDwordsFromPointerSpan(void * span_state)` | Counts dword elements as `(current - begin) / 4`. |
| `0x00573330` | `CFastVB__GetTreeRootNode_00573330` | `void __thiscall CFastVB__GetTreeRootNode_00573330(void * this, void * out_node_slot, void * unused_context)` | Writes the tree root node from the header at `this+0x04`. |
| `0x00573340` | `CFastVB__InsertNodeIntoRBTreeWithHint_00573340` | `void __thiscall CFastVB__InsertNodeIntoRBTreeWithHint_00573340(void * this, void * out_insert_result, void * key_ptr, void * unused_context)` | Searches/inserts a uint-key red-black-tree node through shared sentinel `DAT_009d0c44`. |
| `0x00573560` | `CFastVB__EraseNodeRangeFromRBTree_00573560` | `void __thiscall CFastVB__EraseNodeRangeFromRBTree_00573560(void * this, void * out_next_slot, void * first_node, void * last_node, void * unused_context)` | Clears a full sentinel-backed tree or erases an iterator range through the CTexture erase helper. |
| `0x00573630` | `RBTree__FindLowerBoundByUIntKey` | `void __thiscall RBTree__FindLowerBoundByUIntKey(void * this, void * out_node_slot, void * key_ptr, void * unused_context)` | Finds the first uint-key node not less than `key_ptr`. |
| `0x005736a0` | `MemCopyU16Elements` | `void __stdcall MemCopyU16Elements(void * dest_or_null, int element_count, void * value_ptr)` | Writes one repeated 16-bit value when the destination is non-null. |
| `0x005736d0` | `CFastVB__InsertDwordSpanFilled` | `void __thiscall CFastVB__InsertDwordSpanFilled(void * this, void * insert_at, int element_count, void * value_ptr, void * unused_context)` | Inserts repeated dword values, shifting or growing the span. |
| `0x00573d00` | `RBTree__InitUIntKeyTreeWithSharedSentinel` | `void __fastcall RBTree__InitUIntKeyTreeWithSharedSentinel(void * tree_state)` | Initializes a uint-key tree header using shared sentinel `DAT_009d0c44`. |
| `0x00573ff0` | `CFastVB__FillDwordSpanWithValue_00573ff0` | `void __stdcall CFastVB__FillDwordSpanWithValue_00573ff0(void * dest_or_null, int element_count, void * value_ptr)` | Writes one repeated dword value when the destination is non-null. |
| `0x00574020` | `CFastVB__RBTreeRotateLeft_00574020` | `void __thiscall CFastVB__RBTreeRotateLeft_00574020(void * this, void * pivot_node, void * unused_context)` | Performs red-black-tree left rotation during insert fixup. |
| `0x005741d0` | `CFastVB__CopyWordRange_Strict` | `void __cdecl CFastVB__CopyWordRange_Strict(void * range_start, void * range_end, void * dest)` | Unconditionally copies a word range. |
| `0x00574200` | `CFastVB__CopyDwordRange_Strict` | `void __cdecl CFastVB__CopyDwordRange_Strict(void * range_start, void * range_end, void * dest)` | Unconditionally copies a dword range. |
| `0x00574230` | `CFastVB__AssignDwordIfDestNotNull` | `void __cdecl CFastVB__AssignDwordIfDestNotNull(void * dest_or_null, void * source_value)` | Copies one dword when the destination is non-null. |
| `0x00574250` | `CFastVB__AssignWordIfDestNotNull` | `void __cdecl CFastVB__AssignWordIfDestNotNull(void * dest_or_null, void * source_value)` | Copies one word when the destination is non-null. |

Wave655 read-back evidence: dry/apply/final dry reported `updated=0 skipped=21 renamed=0 would_rename=0 signature_updated=21 missing=0 bad=0`, then `updated=21 skipped=0 renamed=0 would_rename=0 signature_updated=21 missing=0 bad=0`, then `updated=0 skipped=21 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`. Post exports verified `21` metadata rows, `21` tag rows, `117` xref rows, `1869` instruction rows, and `21` clean decompile rows. Queue after Wave655 is `6093` total, `3572` commented, `2521` commentless, `1217` exact-undefined signatures, `736` `param_N`, comment-backed proxy `3572/6093 = 58.62%`, strict clean-signature proxy `3522/6093 = 57.80%`, and next head `0x00574270 CDXTexture__FindFormatDescriptorById`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260520-202319_post_wave655_cfastvb_span_tree_verified`.

Exact CFastVB/span/vector/tree/layout identity, exact owner/template identity, concrete node/span layouts, runtime strip quality, runtime texture/CFastVB behavior, concrete D3D output, BEA patching, and rebuild parity remain unproven.

## Wave661 Quaternion Normalize Context

Wave661 quaternion/matrix correction hardened the next queue head, `0x00579184 CFastVB__NormalizeQuaternionCopy`, while the related matrix and Euler-to-quaternion rows are documented under [`Math.cpp`](../Math.cpp/_index.md):

| Address | Saved name | Saved signature | Evidence |
|---------|------------|-----------------|----------|
| `0x00579184` | `CFastVB__NormalizeQuaternionCopy` | `void __stdcall CFastVB__NormalizeQuaternionCopy(void * out_quaternion_xyzw, void * input_quaternion_xyzw)` | Source/default dispatch-table slot `0x00657070`; measures four quaternion lanes, copies already-normalized non-alias input, zeros near-zero length, or scales four lanes by reciprocal sqrt. |

The same `quaternion-matrix-wave661` pass corrected `0x00577a3e Math__BuildQuaternionFromEulerAngles`, moved two stale `CTexture` labels into owner-neutral math names, and made no executable-byte changes. Dry/apply/final dry reported `updated=0 skipped=7 renamed=0 would_rename=6 signature_updated=7 missing=0 bad=0`, then `updated=7 skipped=0 renamed=6 would_rename=0 signature_updated=6 missing=0 bad=0`, then `updated=0 skipped=7 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`. Queue after Wave661 is `6098` total, `3623` commented, `2475` commentless, `1217` exact-undefined signatures, `694` `param_N`, comment-backed proxy `3623/6098 = 59.41%`, strict clean-signature proxy `3573/6098 = 58.59%`, and next head `0x00579b39 CDXTexture__LookupNamedFormatDescriptor`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260520-234153_post_wave661_quaternion_matrix_verified`.

Exact quaternion convention, CPU feature replacement behavior, runtime math correctness, BEA patching, and rebuild parity remain unproven. The `quaternion-matrix-wave661` tag marks saved static Ghidra evidence only.

## Wave660 Quaternion Dispatch Context

Wave660 math dispatch continuation kept the quaternion axis-angle helpers under the retained `CFastVB` family while moving adjacent stale dispatch labels into the owner-neutral math dispatch island:

| Address | Saved name | Saved signature | Evidence |
|---------|------------|-----------------|----------|
| `0x0057798e` | `CFastVB__BuildAxisAngleQuaternion_Dispatch` | `float * __stdcall CFastVB__BuildAxisAngleQuaternion_Dispatch(void * out_quaternion_xyzw, void * axis_vec3, float angle_radians)` | Runtime dispatch-table slot `0x00656fa4`; corrected from stale `CFastVB__DispatchIndirect_00656fa4` and paired with concrete body `0x005779ae`. |
| `0x005779ae` | `CFastVB__BuildAxisAngleQuaternion` | `float * __stdcall CFastVB__BuildAxisAngleQuaternion(void * out_quaternion_xyzw, void * axis_vec3, float angle_radians)` | Source/default dispatch-table slot `0x006570c4`; uses `FSIN/FCOS` and writes quaternion lanes. |

Wave660 also records the adjacent math-dispatch rows in [`Math.cpp`](../Math.cpp/_index.md) and the retained `0x005776a5 CTexture__DispatchPtr00656fd0_WithInit` row in [`texture.cpp`](../texture.cpp/_index.md). Dry/apply/final dry reported `updated=0 skipped=17 created=0 would_create=2 body_set=0 would_set_body=2 renamed=0 would_rename=4 signature_updated=15 missing=0 bad=0`, then `updated=17 skipped=0 created=2 would_create=0 body_set=2 would_set_body=0 renamed=4 would_rename=0 signature_updated=13 missing=0 bad=0`, then `updated=0 skipped=17 created=0 would_create=0 body_set=0 would_set_body=0 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`. Queue after Wave660 is `6098` total, `3619` commented, `2479` commentless, `1217` exact-undefined signatures, `698` `param_N`, comment-backed proxy `3619/6098 = 59.35%`, strict clean-signature proxy `3569/6098 = 58.53%`, and next head `0x00579184 CFastVB__NormalizeQuaternionCopy`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260520-230154_post_wave660_math_dispatch_verified`.

Exact vector/matrix storage contract, CPU feature replacement behavior, runtime math correctness, BEA patching, and rebuild parity remain unproven. The `math-dispatch-wave660` tag marks saved static Ghidra evidence only.

## Wave659 Matrix Dispatch Correction Context

Wave659 matrix dispatch hardening corrected stale `CFastVB` dispatch labels in the matrix dispatch-table island and moved those rows under owner-neutral [`Math.cpp`](../Math.cpp/_index.md) evidence:

| Address | Saved name | Saved signature | Evidence |
|---------|------------|-----------------|----------|
| `0x005771af` | `Math__BuildScaleMatrix4x4_Dispatch` | `void __stdcall Math__BuildScaleMatrix4x4_Dispatch(void * out_matrix4x4, float scale_x, float scale_y, float scale_z)` | Runtime dispatch-table slot `0x00656fb4`; paired source/default slot `0x006570d4` points to recovered `0x005771dd Math__BuildScaleMatrix4x4`. |
| `0x005775b0` | `Math__BuildQuaternionRotationMatrix_Dispatch` | `void __stdcall Math__BuildQuaternionRotationMatrix_Dispatch(void * out_matrix4x4, void * quaternion_xyzw)` | Runtime dispatch-table slot `0x00656fc8`; paired source/default slot `0x006570e8` points to recovered `0x005775c3 Math__BuildQuaternionRotationMatrix`. |
| `0x005775bd` | `Math__BuildQuaternionRotationMatrix_Dispatch_Thunk` | `void __stdcall Math__BuildQuaternionRotationMatrix_Dispatch_Thunk(void * out_matrix4x4, void * quaternion_xyzw)` | Pure jump thunk to runtime dispatch-table slot `0x00656fc8`. |

Wave659 read-back evidence: dry/apply/final dry reported `updated=0 skipped=16 created=0 would_create=3 body_set=0 would_set_body=3 renamed=0 would_rename=5 signature_updated=13 missing=0 bad=0`, then `updated=16 skipped=0 created=3 would_create=0 body_set=3 would_set_body=0 renamed=5 would_rename=0 signature_updated=11 missing=0 bad=0`, then `updated=0 skipped=16 created=0 would_create=0 body_set=0 would_set_body=0 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`. Queue after Wave659 is `6096` total, `3602` commented, `2494` commentless, `1217` exact-undefined signatures, `711` `param_N`, comment-backed proxy `3602/6096 = 59.09%`, strict clean-signature proxy `3552/6096 = 58.27%`, and next head `0x005776a5 CTexture__DispatchPtr00656fd0_WithInit`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260521-221700_post_wave659_matrix_dispatch_verified`.

Exact vector/matrix storage contract, CPU feature replacement behavior, runtime math correctness, BEA patching, and rebuild parity remain unproven.

## Wave658 Half-Float Conversion Read-Back Note

Wave658 math/half-float hardening covered two retained `CFastVB` half-float array conversion helpers plus the companion math tolerance helper documented under [`Math.cpp`](../Math.cpp/_index.md):

| Address | Name | Saved Signature | Evidence |
|---------|------|-----------------|----------|
| `0x005759c9` | `CFastVB__ConvertFloat32ArrayToFloat16` | `void __stdcall CFastVB__ConvertFloat32ArrayToFloat16(void * half_dest, void * float32_source, uint element_count)` | Loops over `element_count` float32 inputs, converts sign/exponent/mantissa bits into 16-bit half-float-like outputs with rounding and saturation paths, and writes words to `half_dest`. |
| `0x00575a6b` | `CFastVB__ConvertFloat16BufferToFloat32_00575a6b` | `void * __stdcall CFastVB__ConvertFloat16BufferToFloat32_00575a6b(void * float32_dest, void * half_source, uint element_count)` | Loops over `element_count` 16-bit half-float-like inputs, expands zero/subnormal/normal encodings into 32-bit float bit patterns at `float32_dest`, and returns `float32_dest`. |

Wave658 read-back evidence: dry/apply/final dry reported `updated=0 skipped=3 renamed=0 would_rename=0 signature_updated=3 missing=0 bad=0`, then `updated=3 skipped=0 renamed=0 would_rename=0 signature_updated=3 missing=0 bad=0`, then `updated=0 skipped=3 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`. Post exports verified `3` metadata rows, `3` tag rows, `17` xref rows, `723` instruction rows, and `3` clean decompile rows. Queue after Wave658 is `6093` total, `3586` commented, `2507` commentless, `1217` exact-undefined signatures, `722` `param_N`, comment-backed proxy `3586/6093 = 58.85%`, strict clean-signature proxy `3536/6093 = 58.03%`, and next head `0x005771af CFastVB__DispatchIndirect_00656fb4`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260520-214232_post_wave658_math_half_float_verified`.

Exact IEEE-754 edge-case parity, dispatch-table ownership, runtime vertex/texture conversion behavior, BEA patching, and rebuild parity remain unproven.

## Wave656 Texture Format Scoring Context (2026-05-20)

Wave656 texture format/upload hardening covered the adjacent texture-format selection/upload island. Two rows carry the retained `CFastVB` owner prefix even though the xrefs sit in the `CDXTexture` decode/format-selection band:

| Address | Name | Saved Signature | Evidence |
|---------|------|-----------------|----------|
| `0x00574296` | `CFastVB__ComputeFormatMatchPenalty` | `uint __fastcall CFastVB__ComputeFormatMatchPenalty(void * requested_descriptor, void * candidate_descriptor)` | Uses the `DAT_005e7270` compatibility matrix and a weighted five-slot descriptor penalty score; returns `0xffffffff` for incompatible descriptor pairs. |
| `0x0057437a` | `CFastVB__SelectBestFormatHandler` | `int __stdcall CFastVB__SelectBestFormatHandler(void * device_or_null, uint usage_flags, int resource_type, void * requested_descriptor)` | Mutes/restores D3D debug output, optionally probes a device-like vtable for descriptor support, and selects the lowest-penalty compatible format id. |
| `0x00574577` | `CFastVB__ReturnInputInt` | `int __fastcall CFastVB__ReturnInputInt(int value)` | Retained-name identity helper reached from texture profile/conversion tables. |

The companion `CDXTexture` rows are documented under [`DXTexture.cpp`](../DXTexture.cpp/_index.md). Wave656 made no renames, no function-boundary changes, and no executable-byte changes. Queue after Wave656 is `6093` total, `3580` commented, `2513` commentless, `1217` exact-undefined signatures, `728` `param_N`, comment-backed proxy `3580/6093 = 58.76%`, strict clean-signature proxy `3530/6093 = 57.94%`, and next head `0x00574abb CDXTexture__RepeatCallbackN`; verified backup `[maintainer-local-ghidra-backup-root]\BEA_20260520-205422_post_wave656_texture_format_upload_verified`.

Exact descriptor schema, exact CFastVB owner/template identity, runtime D3D/device compatibility behavior, runtime texture upload behavior, BEA patching, and rebuild parity remain unproven.

---

## Recent Headless Semantic Promotions (2026-02-26)

| Address | Symbol | Description |
|---------|--------|-------------|
| `0x00584144` | `CFastVB__PackTexels_NoDither_Bits16_16` | Non-dither packer writing two 16-bit channels per texel into packed 32-bit output |
| `0x0058423f` | `CFastVB__PackTexels_NoDither_Bits2_10_10_10` | Non-dither packer writing 2-10-10-10 packed output from float texel channels |
| `0x0058439e` | `CFastVB__PackTexels_NoDither_Bits16_16_16_16` | Non-dither packer writing 16-16-16-16 packed output (two dwords per texel) |
| `0x00584d78` | `CFastVB__UnpackTexels_Bits565ToFloat4` | Unpacks 16-bit RGB565 packed texels into normalized float4 channels |
| `0x00584e32` | `CFastVB__UnpackTexels_Bits555ToFloat4_AlphaOne` | Unpacks 5-5-5 packed texels into float4 with forced alpha lane |
| `0x00584ee9` | `CFastVB__UnpackTexels_Bits1555ToFloat4` | Unpacks 1-5-5-5 packed texels into float4 including alpha-bit expansion |
| `0x00584fae` | `CFastVB__UnpackTexels_Bits4444ToFloat4` | Unpacks 4-4-4-4 packed texels into normalized float4 RGBA channels |
| `0x00585072` | `CFastVB__UnpackTexels_Bits2_10_10_10_ToFloat4` | Unpacks 2-10-10-10 packed texels into float4 channels with component scaling |
| `0x00585161` | `CFastVB__UnpackTexels_Bits8888ToFloat4` | Unpacks 8-8-8-8 packed texels into float4 RGBA channels |
| `0x00585220` | `CFastVB__UnpackTexels_Bits888ToFloat4_AlphaOne` | Unpacks 8-8-8 packed texels into float4 RGB with forced alpha=1.0 |
| `0x005852d5` | `CFastVB__UnpackTexels_Bits16_16_ToFloat4_RG` | Unpacks dual 16-bit channels into float4 RG lanes with default BA handling |
| `0x00585380` | `CFastVB__UnpackTexels_Bits2_10_10_10_ToFloat4_Alt` | Alternate channel-order unpacker for 2-10-10-10 packed texels |
| `0x005859d8` | `CFastVB__UnpackTexels_L8ToFloat4` | Unpacks 8-bit luminance texels into float4 with replicated RGB and alpha=1.0 |
| `0x00585a7b` | `CFastVB__UnpackTexels_L8A8ToFloat4` | Unpacks paired luminance/alpha bytes into float4 channels |
| `0x00585b35` | `CFastVB__UnpackTexels_A4L4ToFloat4` | Unpacks A4L4 texels into float4 RGBA channels |
| `0x00585c0b` | `CFastVB__UnpackTexels_L16ToFloat4` | Unpacks 16-bit luminance texels into float4 with replicated RGB and alpha=1.0 |
| `0x00585fa3` | `CFastVB__UnpackTexels_Signed8_8_8_8_ToFloat4` | Unpacks signed 8-8-8-8 packed texels into float4 channels |
| `0x005868d1` | `CFastVB__UnpackTexels_L16A16_ToFloat4` | Unpacks L16/A16 texels to float4 with replicated luminance and explicit alpha |
| `0x00585908` | `CFastVB__InitTexelUnpackVTable_005e9f5c` | Initializes texel-unpack profile object and binds vtable 0x005e9f5c |
| `0x00585924` | `CFastVB__InitTexelUnpackVTable_005e9f6c` | Initializes texel-unpack profile object and binds vtable 0x005e9f6c |
| `0x005859bc` | `CFastVB__InitTexelUnpackVTable_005e9f7c` | Initializes texel-unpack profile object and binds vtable 0x005e9f7c |
| `0x00585bd3` | `CFastVB__TexelUnpackProfile_scalar_deleting_dtor` | Scalar-deleting destructor for texel-unpack profile objects |
| `0x00585bef` | `CFastVB__InitTexelUnpackVTable_005e9fac` | Initializes texel-unpack profile object and binds vtable 0x005e9fac |
| `0x00585c94` | `CFastVB__InitTexelUnpackVTable_005e9fbc` | Initializes texel-unpack profile object and binds vtable 0x005e9fbc |
| `0x0058617c` | `CFastVB__InitTexelUnpackVTable_005ea034` | Initializes texel-unpack profile object and binds vtable 0x005ea034 |
| `0x005862e9` | `CFastVB__InitTexelUnpackVTable_005ea068` | Initializes texel-unpack profile object and binds vtable 0x005ea068 |
| `0x0058669a` | `CFastVB__InitTexelUnpackVTable_005ea0c8` | Initializes texel-unpack profile object and binds vtable 0x005ea0c8 |
| `0x005866b6` | `CFastVB__InitTexelUnpackVTable_005ea0d8` | Initializes texel-unpack profile object and binds vtable 0x005ea0d8 |
| `0x0058675f` | `CFastVB__InitTexelUnpackVTable_005ea0e8` | Initializes texel-unpack profile object and binds vtable 0x005ea0e8 |
| `0x00586994` | `CFastVB__InitTexelUnpackVTable_005ea118` | Initializes texel-unpack profile object and binds vtable 0x005ea118 |
| `0x00586ec7` | `CFastVB__InitTexelUnpackVTable_005ea198` | Initializes texel-unpack profile object and binds vtable 0x005ea198 |
| `0x00586bb7` | `CFastVB__FlushPendingConvertedRows16` | Flushes pending converted rows from float scratch to 16-bit destination pairs |
| `0x0058735a` | `CFastVB__StoreDecodedBlockToScratch` | Stores decoded texel block into scratch buffer |
| `0x005873f8` | `CFastVB__LoadDecodedBlockFromScratch` | Loads decoded texel block from scratch buffer |
| `0x00587daf` | `CFastVB__TexelPackProfile_scalar_deleting_dtor` | Scalar-deleting destructor for texel pack profile |
| `0x00587dee` | `CFastVB__InitTexelUnpackVTable_005ea264` | Initializes texel-unpack profile and binds vtable 0x005ea264 |
| `0x00587e06` | `CFastVB__InitTexelUnpackVTable_005ea274` | Initializes texel-unpack profile and binds vtable 0x005ea274 |
| `0x00587e66` | `CFastVB__TexelCodecProfile_scalar_deleting_dtor` | Scalar-deleting destructor for texel codec profile objects |
| `0x00587e82` | `CFastVB__CreateTexelUnpackProfileByFormat` | Factory creating texel unpack profile object by format id |
| `0x00580120` | `CFastVB__RunDualProfileConversionStage` | Runs dual-profile conversion stage with staging allocation and compatibility checks |
| `0x0058070e` | `CFastVB__InitDualTexelConversionPipeline` | Initializes paired unpack profiles and full conversion pipeline stages |
| `0x005809de` | `CFastVB__ShutdownActiveProfile` | Releases active profile via vtable callbacks and clears pointer |
| `0x00580eef` | `CFastVB__ShutdownActiveProfile_Thunk` | Alias thunk to active-profile shutdown path |
| `0x005866d2` | `CFastVB__UnpackTexels_CallbackPerTexel_Stride4_SetZAOne` | Callback wrapper for stride-4 records with post-write Z/A one-fill |
| `0x00591050` | `CFastVB__ReleaseOwnedObjectAndReset` | Releases owned sub-object via vfunc(`+0x28`) and clears local state fields (`+0x04`, `+0x14`) |
| `0x00592b00` | `CFastVB__ParserContext_Shutdown` | Parser-context shutdown path performing virtual cleanup, release/reset helper, and terminal callback dispatch |
| `0x00592c50` | `CFastVB__ParserContext_Init` | Parser-context constructor/init path seeding callback slots and default `"Bogus message code"` diagnostic string |
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
| `0x00592530` | `CFastVB__JpegParser_ReadAndValidateSOI` | Validates JPEG SOI marker and parser preconditions before frame decode |
| `0x005913b0` | `CFastVB__JpegParser_ResetFrameState` | Clears parser/frame accumulators and resets component-state fields |
| `0x00591720` | `CFastVB__JpegParser_ParseSOFComponents` | Parses SOF component descriptors with sampling/table selector fields |
| `0x00596589` | `CFastVB__SolveScalarEndpointPairFromSamples` | Solves scalar endpoint pair from sample spans for compression fit |
| `0x005968a4` | `CFastVB__SolveVectorEndpointPairFromSamples` | Solves weighted vector endpoint pair from sample set for fit path |
| `0x00596e23` | `CFastVB__QuantizeScalarBlockIndices` | Quantizes scalar samples into selector indices with iterative residual distribution |
| `0x00597a61` | `CFastVB__PackScalarBlock_4BitEndpoints` | Packs 16 scalar samples into 4-bit endpoint/index representation |
| `0x00597b87` | `CFastVB__PackScalarBlock_InterpolatedEndpoints` | Computes/interpolates scalar endpoints and emits per-sample selector indices |
| `0x0059c610` | `CFastVB__ReleaseOwnedObjectAndReset_Core` | Core release/reset helper for owned object pointer and local state fields |
| `0x0059c700` | `CFastVB__CopyBlockRows128Bytes` | Copies `param_3` rows of 128-byte block data between buffers |
| `0x0059a21f` | `CFastVB__AreNodeTreesCompatible` | Recursively compares node trees/types with exact-vs-compatible mode support |
| `0x0059a54d` | `CFastVB__ScoreNodeTreeMatch` | Computes compatibility score between requested/candidate node trees |
| `0x0059a71a` | `CFastVB__SelectBestNodeTreeMatch` | Selects best candidate node-tree match from rule lists by minimal score |
| `0x00598f60` | `CFastVB__NodeType8_scalar_deleting_dtor` | Scalar-deleting destructor wrapper for node-type-8 object (`vtable 0x005ef240`) |
| `0x005997a5` | `CFastVB__InitNodeType17` | Initializes node-type-17 storage and binds node vtable `0x005ef374` |
| `0x00598474` | `CFastVB__InitDispatchOpsFromFeatureFlags` | Initializes dispatch-operation table entries from active runtime feature flags |
| `0x0059f6dd` | `CFastVB__BroadcastMatrix4x4ToSIMDLanes` | Broadcasts matrix components into SIMD lane layout for downstream dispatch ops |
| `0x005a2a61` | `CFastVB__DispatchOp_TransformVec2ByMatrix4` | Dispatch operation transforming Vec2 coordinates through matrix-form parameters |
| `0x005aa0cc` | `CFastVB__DispatchOp_ComposeTransformFromOptionalInputs_Scalar` | Scalar composition dispatch path combining optional transform inputs into output state |
| `0x005aa2f2` | `CFastVB__DispatchOp_ComposeTransformFromOptionalInputs_SIMD` | SIMD composition dispatch path combining optional transform inputs into output state |
| `0x005a38c0` | `CFastVB__DispatchOp_TransformVec4ArrayByMatrix4` | Iterates input vectors and applies 4x4 matrix multiplication with configurable src/dst strides |
| `0x005a47f2` | `CFastVB__DispatchOp_ExtractAxisAndOptionalAngle` | Copies axis-vector components and optionally emits an angle-like scalar metric |
| `0x005a7617` | `CFastVB__DispatchOp_BuildRotationMatrixFromEulerAngles` | Computes trigonometric terms and writes a 4x4 rotation matrix-style output block |
| `0x005a7cf0` | `CFastVB__DispatchOp_BuildRotationMatrixFromAxisAngleVector` | Normalizes axis-angle vector input then emits a 4x4 rotation matrix-style output block |
| `0x005b3440` | `CFastVB__JpegEntropy_EncodeBlockZigZagHuffman` | Zig-zag block entropy encoder that emits run-length/value bits through JPEG-style bitstream helper |
| `0x005b35b0` | `CFastVB__JpegEntropy_WriteMarkerAndResetDcPredictors` | Emits marker bytes and resets per-component DC predictor/accumulator state |
| `0x005b86c0` | `CFastVB__FastAcosApprox_Scalar` | Scalar arccos-approximation kernel used by axis/angle extraction dispatch paths |
| `0x005b8ca0` | `CFastVB__FastTrigPairApprox_Scalar` | Scalar trigonometric pair approximation kernel used by rotation-matrix dispatch builders |
| `0x005a7e09` | `CFastVB__DispatchOp_ComposeMatrixFromOptionalTransforms` | Multi-branch dispatch path composing output matrix from optional transform inputs and basis blocks |
| `0x005ad590` | `CFastVB__JpegEntropy_CommitAndResetBlockState` | Commits entropy progress counters and resets per-block working state before next encode step |
| `0x0055f506` | `CRT__FReadCore` | Core CRT `fread` helper dispatching buffered read logic with item-size/count parameters |
| `0x0055f5ee` | `Win32__FindFirstFileWithMeta` | Wrapper around `FindFirstFile` path with metadata copyout into caller struct |
| `0x0055f6bb` | `Win32__FindNextFileWithMeta` | Wrapper around `FindNextFile` path with metadata copyout into caller struct |
| `0x0055fe26` | `CRT__LockRouteByAddress` | Routes lock/unlock path by encoded address class in CRT lock table |
| `0x0055fe55` | `CRT__LockRouteByIndex` | Routes lock/unlock path by lock-index mode and updates CRT lock bookkeeping |
| `0x0055f2e8` | `CRT__WcsCmp` | UTF-16 lexical compare returning {-1,0,1} ordering |
| `0x0055f783` | `Win32__FindCloseWithErrno` | Calls `FindClose`; maps failure into CRT errno path |
| `0x0055fe78` | `CRT__UnlockRouteByAddress` | Address-routed unlock companion to `CRT__LockRouteByAddress` |
| `0x0055fea7` | `CRT__UnlockRouteByIndex` | Index-routed unlock companion to `CRT__LockRouteByIndex` |
| `0x0055feec` | `CRT__FTellAdjusted` | Stream position helper with text-mode newline adjustment path |
| `0x0055eb3d` | `CRT__RoundToIntegerRespectingControlWord` | FPU control-word aware double rounding helper |
| `0x0055ec4a` | `CRT__HeapAllocBase` | CRT heap allocation base helper with small-block/HeapAlloc routing |
| `0x0055f085` | `CRT__FreeBase` | CRT heap free base helper with small-block/HeapFree routing |
| `0x0055f0ef` | `CRT__UnlockHeapLock` | Heap lock unlock wrapper for lock id 9 |
| `0x0055f147` | `CRT__UnlockHeapLock_Alt` | Alternate heap lock unlock wrapper for lock id 9 |
| `0x0055da8d` | `CRT__InitFloatConversionDispatchTable` | Initializes CRT float-conversion callback dispatch pointers |
| `0x0055dccd` | `CRT__Acos` | CRT arccos helper with FPU-control and error-path handling |
| `0x0055df28` | `CRT__OnexitTablePush` | Pushes callback pointer into CRT onexit table with growth fallback |
| `0x0055dfa6` | `CRT__RegisterOnexitFunction` | Front-end wrapper for CRT onexit registration |
| `0x0055e42a` | `Win32__CaptureSystemTimeAsFileTimeTicks` | Captures current system FILETIME into 64-bit global tick value |
| `0x0055d6a0` | `CRT__SehPopExceptionFrameAndJump` | Pops one exception-registration frame and tail-jumps to callback target |
| `0x0055d6db` | `CRT__SehLockUnlockAndJump` | Emits lock/unlock pair then tail-jumps to callback target |
| `0x0055d6e2` | `CRT__SehRtlUnwindAndRestoreFrame` | Calls `RtlUnwind`, clears unwind-state bit, and restores exception-list linkage |
| `0x0055d767` | `CRT__SehInvokeCallSettingFrame12` | Builds temporary exception frame and dispatches through `__CallSettingFrame_12` |
| `0x0055d7bb` | `CRT__SehCallback_Call_005602d2` | SEH callback shim that forwards control to `CRT__SehDispatchWithScopeTable` |
| `0x0055da5e` | `CRT__SehStoreFrameGlobals` | Stores frame/EAX context into CRT globals used by downstream runtime bridge helpers |
| `0x0055da76` | `CRT__InitRuntimeFromStoredFrameGlobals` | Runtime bridge init helper that seeds setup paths from stored frame globals |
| `0x0055db72` | `CRT__EhVectorDestructorIterator_IfNoException` | Invokes `eh_vector_destructor_iterator` only on no-exception guard path |
| `0x0055e412` | `CRT__SpawnPathVarargsNoEnv_Thunk` | Wave631 corrected the stale texture label; CRT spawn varargs/no-environment thunk |
| `0x0055e45f` | `CRT__OpenFileByModeString_AutoUnlock` | CRT file-open-by-mode wrapper that releases the stream lock via routed unlock |
| `0x005602d2` | `CRT__SehDispatchWithScopeTable` | Central SEH dispatch callback that validates scope table state before handler lookup/unwind routing |
| `0x0056036d` | `CRT__SehLookupAndInvokeScopeHandler` | Walks scope records, matches state windows, and invokes matching handler callback routes |
| `0x00560627` | `CRT__SehUnwindToTargetState` | Iteratively unwinds exception-state index toward target and executes cleanup callbacks |
| `0x005606c5` | `CRT__SehUnwindAndResumeSearch` | Performs unwind cleanup and resumes exception-search dispatch through continuation callback |
| `0x00560cb1` | `CRT__InitFpuControlWord_0x10000_0x30000` | Initializes runtime FPU control mask/value pair through helper `CTexture__Helper_0056947e` |
| `0x0055fc35` | `CRT__IsFloat10Integral_0055fc35` | Floating-point helper that gates integral-path handling by comparing rounded value against original input |
| `0x00561590` | `CRT__Exp2FromFpuCore_00561590` | FPU exponentiation core using `f2xm1` plus `fscale` sequence |
| `0x005615a5` | `CRT__SetFpuControlWordMasked_005615a5` | Applies masked FPU control-word update (`(arg & 0x300) | 0x7f`) and loads it via `FLDCW` |
| `0x005615bc` | `CRT__MapExponentFlagToClassCode_005615bc` | Maps exponent/status bit test (`0x80000`) into class code return values (`7` or `1`) |
| `0x00561618` | `CRT__ExtractFiniteExponentMaskOrPassThrough_00561618` | Returns finite exponent mask bits or pass-through bits for infinity/NaN patterns |
| `0x00560e28` | `CRT__FormatFloatScientificFromLongDouble` | Wrapper that converts long-double decomposition and dispatches to scientific-format core output builder |
| `0x00560e89` | `CRT__FormatFloatScientificCore` | Scientific float text emitter writing sign/mantissa plus exponent suffix (`e+000`) |
| `0x00560f4b` | `CRT__FormatFloatFixedFromLongDouble` | Wrapper that converts long-double decomposition and dispatches to fixed-format core output builder |
| `0x00560fa0` | `CRT__FormatFloatFixedCore` | Fixed float text emitter handling sign, decimal insertion, and precision/zero padding |
| `0x00561047` | `CRT__FormatFloatGeneral_SelectStyle` | `%g`-style selector that chooses scientific vs fixed emitter based on exponent range |
| `0x0055d731` | `CRT__SehDispatchWithScopeTable_Thunk_0055d731` | Thin thunk that directly forwards to `CRT__SehDispatchWithScopeTable` |
| `0x0055fa62` | `CRT__PowCore_0055fa62` | Disassembly-evidenced `pow` core path using `FYL2X` plus exp2 flow and extensive edge-case branches |
| `0x00561530` | `CRT__ReportMathErrorAndRestoreControlWord_00561530` | Calls math-error helper then restores saved control word before returning |
| `0x00560d2a` | `CRT__InsertDecimalSeparatorBeforeExponent_00560d2a` | Inserts locale decimal separator before exponent marker and shifts mantissa tail bytes |
| `0x0056004d` | `CDXTexture__AsciiToLowerInPlace` | Lowercases ASCII `A..Z` in-place on C-string buffers with lock-guarded fallback route |
| `0x00560b2c` | `CTexture__InitializeThreadLocalState` | Allocates/install TLS state record for texture runtime and seeds per-thread defaults |
| `0x00560b80` | `CTexture__InitializeThreadLocalRecordDefaults` | Initializes thread-local texture record defaults (`+0x50` dispatch pointer, `+0x14` flag) |
| `0x00561150` | `CTexture__InitializeGlobalCriticalSections` | Initializes four global texture/runtime critical sections used by lock routes |
| `0x005602ae` | `CDXTexture__ReportFatalAndExitProcess` | Runs fatal-report helper chain and terminates process via `ExitProcess(0xff)` |
| `0x00560bfa` | `CDXTexture__InvokeTlsCleanupCallbackAndFinalize` | Invokes optional TLS-context cleanup callback (`context+0x60`) then executes common finalize helper |
| `0x00560c5b` | `CDXTexture__InvokeGlobalCleanupCallbackAndFinalize` | Invokes global cleanup callback pointer when present, then executes shared finalize helper |
| `0x00560d01` | `CDXTexture__ProbeProcessorFeaturePresentOrFallback` | Dynamically probes `IsProcessorFeaturePresent`; falls back to helper gate when unavailable |
| `0x0055dd7b` | `CFastVB__RunStaticInitRangesWithOptionalCallback` | Runs optional callback then processes two static init-range tables through shared helper |
| `0x0055e183` | `CFastVB__DispatchLockedRoute_6533e0` | Locks route key `0x6533e0`, dispatches helper call, then unlocks |

---

## Function Details

### CFastVB__Create (0x0051a270)

**Purpose:** Creates and initializes a fast vertex buffer for dynamic quad rendering.

**Line Number:** 41 (0x29)

**Signature:**
```cpp
int __thiscall CFastVB::Create(CFastVB* this);
```

**Behavior:**
1. Early return if vertex buffer already exists (`*this != 0`)
2. Allocate CVBuffer object (0x2c bytes)
3. Call `CVBuffer__CreateDynamic` with max vertices from `this+0x0c`, vertex size `0x1c`, and FVF/format `0x144`
4. On success, call `D3DBufferRegistry__MoveToFreeList()` to register buffer
5. On failure, release buffer and return error code

**Returns:** HRESULT (0 = already exists, negative = error, positive = success)

---

### CFastVB__Destroy (0x0051a340)

**Purpose:** Releases the vertex buffer and the shared static index buffer.

**Signature:**
```cpp
void __thiscall CFastVB::Destroy(CFastVB* this);
```

**Behavior:**
1. If vertex buffer exists, call Release(1) via vtable and set to NULL
2. If static index buffer (`DAT_00897a90`) exists, release it and set to NULL

**Note:** The static index buffer is shared across all CFastVB instances - destroying one destroys for all.

---

### CFastVB__LockAligned (0x0051a380)

**Purpose:** Lock vertex buffer with 4-vertex alignment (for quad rendering).

**Signature:**
```cpp
ushort __thiscall CFastVB::LockAligned(CFastVB* this, void** ppData, int vertexCount);
```

**Behavior:**
1. Early return 0xFFFF if no vertex buffer
2. Align current write offset to multiple of 4: `offset = ((offset + 3) >> 2) << 2`
3. If buffer is empty or would overflow, reset to start with DISCARD flag (0x2800)
4. Otherwise use NOOVERWRITE flag (0x1800)
5. Call `CVBuffer::LockRange()` with calculated byte offsets
6. Update write offset and store start vertex

**Returns:** Start vertex index, or 0xFFFF on failure

---

### CFastVB__Lock (0x0051a430)

**Purpose:** Lock vertex buffer for writing (may flush if needed).

**Signature:**
```cpp
ushort __thiscall CFastVB::Lock(CFastVB* this, void** ppData, int vertexCount);
```

**Behavior:**
1. Return 0xFFFF if no vertex buffer
2. If start vertex is -1 (no current batch), delegate to LockAligned
3. If current batch is empty or would overflow:
   - Call `Render()` to flush pending vertices
   - Reset state and use DISCARD flag (0x2800)
4. Otherwise use NOOVERWRITE flag (0x1800) after unlocking
5. Lock the requested range and update vertex count

**Returns:** Start vertex index, or 0xFFFF on failure

---

### CFastVB__Render (0x0051a510)

**Purpose:** Flush all pending vertices to GPU as indexed triangles.

**Line Number:** 195 (0xC3)

**Signature:**
```cpp
void __thiscall CFastVB::Render(CFastVB* this);
```

**Behavior:**
1. Early return if no pending vertices (start vertex == -1)
2. Unlock vertex buffer
3. Set stream source to vertex buffer via D3D device vtable
4. Create static index buffer if not exists:
   - Allocate index buffer with index_count `0x1d4c` (7500 indices)
   - Fill with quad indices: [0,1,2,2,3,0], [4,5,6,6,7,4], ...
5. Set indices via D3D device
6. Call draw primitives: `FUN_00513c70(4, startVertex, vertexCount, indexCount, primitiveCount)`
7. Reset start vertex to -1 and vertex count to 0

**Index Pattern (per quad):**
```
Triangle 1: [i+0, i+1, i+2]
Triangle 2: [i+2, i+3, i+0]
```

---

## Global Data

| Address | Name | Type | Description |
|---------|------|------|-------------|
| `0x00897a90` | DAT_00897a90 | CIBuffer* | Shared static index buffer for quad rendering |
| `0x00888a50` | DAT_00888a50 | IDirect3DDevice8* | Direct3D device pointer |

## Lock Flags

| Value | Name | Description |
|-------|------|-------------|
| `0x1800` | D3DLOCK_NOOVERWRITE | Lock without overwriting (append mode) |
| `0x2800` | D3DLOCK_DISCARD | Discard contents (start fresh) |

## Usage Pattern

```cpp
// Typical usage for rendering quads
CFastVB fastVB;
fastVB.Create();

// Lock buffer for N vertices (N/4 quads)
void* pData;
ushort startVertex = fastVB.Lock(&pData, numVertices);
if (startVertex != 0xFFFF) {
    // Fill vertex data
    memcpy(pData, vertices, numVertices * 0x1c);
}

// Flush to GPU when batch complete
fastVB.Render();

// Cleanup
fastVB.Destroy();
```

## Cross-References

### Callers of CFastVB__Create
- `CDXFont__DrawTextScaled` at 0x00540057
- `CRenderQueue__RenderAll` at 0x0055294c
- `CVBufTexture__DrawSpriteEx` at 0x00556296

### Callers of CFastVB__Render
- `CDXCompass__Render` (called 4 times)
- `CFastVB__Lock` at 0x0051a490, 0x0051a4e2 (buffer full flush)
- `CDXFont__DrawTextScaled` at 0x00540613

## Related Systems

- **CVBuffer** - Underlying vertex buffer wrapper
- **CIBuffer** - Index buffer class (used for static quad indices)
- **Direct3D 8** - Native graphics API
