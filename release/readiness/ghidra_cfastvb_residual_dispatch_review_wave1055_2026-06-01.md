# Ghidra CFastVB Residual Dispatch Review Wave1055 Readiness Note

Status: complete read-only static re-audit evidence
Date: 2026-06-01
Scope: `cfastvb-residual-dispatch-review-wave1055`

Wave1055 re-read twenty-six existing CFastVB vector, quaternion, matrix, and alternate batch dispatch helpers from older Wave717, Wave718, Wave719, and Wave897 CFastVB math surfaces. The pass made no Ghidra mutation, no renames, no signature changes, no comment/tag changes, no function-boundary changes, and no executable-byte changes.

Primary target groups:

| Group | Addresses | Static read-back evidence |
| --- | --- | --- |
| Wave717 transform/normalization head | `0x0059f360`, `0x0059f3d9`, `0x0059f473`, `0x0059f4f1`, `0x0059f5b3` | DATA xrefs from `CFastVB__InitDispatchTableVariant_005980be` and/or `_0059822c`; saved comments/tags still describe Vec4 transform, Vec4 normalization/scaling, Euler-to-quaternion, and covariance/basis-to-quaternion evidence. |
| Wave718 scalar transform residual | `0x005a14a5`, `0x005a15a5`, `0x005a16b1`, `0x005a1786`, `0x005a1889`, `0x005a1979` | DATA xrefs from dispatch-table variants plus intra-family calls from batch tails; evidence covers plane-from-triangle, quaternion-to-matrix4, Vec3 transform/project, and Vec3/Vec4 normalization helpers. |
| Wave897 alternate SIMD batch tails | `0x005a1c55`, `0x005a1e5b`, `0x005a1fe9`, `0x005a214f`, `0x005a225f`, `0x005a249d` | DATA xrefs from `CFastVB__InitDispatchTableVariant_0059822c`; stack-locked decompile still shows hidden register/stack ABI artifacts around matrix broadcast and scalar tail calls. |
| Wave719 matrix/quaternion residual | `0x005a2a61`, `0x005a2ee9`, `0x005a2ff4`, `0x005a30f4`, `0x005a3200`, `0x005a32d4`, `0x005a3508`, `0x005a36cf`, `0x005a3791` | DATA xrefs from both dispatch-table variants plus batch-tail calls; evidence covers Vec2/Vec4 transforms, determinant, plane, quaternion/matrix conversion, matrix multiply, quaternion-pair matrix build, and Euler/matrix-to-quaternion helpers. |

Read-back evidence:

- Primary exports: `26` metadata rows, `26` tag rows, `50` xref rows, `2277` function-body instruction rows, and `26` decompile rows.
- Context exports: `12` metadata rows, `12` tag rows, `45` xref rows, `2263` function-body instruction rows, and `12` decompile rows.
- Context anchors include `CFastVB__InitDispatchTableVariant_005980be`, `CFastVB__InitDispatchTableVariant_0059822c`, `CFastVB__InitDispatchOpsFromFeatureFlags`, `CFastVB__BroadcastMatrix4x4ToSIMDLanes`, `CFastVB__DispatchOp_WeightedMatrixBlendBatch_005a04a0`, `CFastVB__EvaluateCubicBasisVec3`, `CFastVB__DispatchOp_TransformVec4ArrayByMatrix4`, `CFastVB__DispatchOp_InterpolateQuaternionPairCore_005a4d98`, `CFastVB__DispatchOp_NormalizeQuaternionWithAcosFallback_005a5052`, `CFastVB__DispatchOp_ComposeTransformFromOptionalInputs_Core_005a647f`, `CFastVB__DispatchOp_InvertMatrix4x4_WithDeterminant_005a8f5d`, and `CFastVB__DispatchOp_MultiplyMatrix4x4_Packed_005a9d78`.
- Queue closure remains `6246/6246 = 100.00%`.
- Wave911 focused progress remains `769/1408 = 54.62%`.
- Expanded static surface progress advances to `1091/1509 = 72.30%`.
- Wave911 top-500 coverage remains `500/500 = 100.00%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260601-173102_post_wave1055_cfastvb_residual_dispatch_review_verified`, `19` files, `174656391` bytes, `DiffCount=0`, `HashDiffCount=0`.

What this proves:

- The twenty-six target functions still exist in the saved Ghidra project with expected names, signatures, comments, and tags.
- Incoming references still tie the rows to the expected CFastVB dispatch-table initializer functions and intra-family CFastVB helper calls.
- The stack-locked / hidden-register rows remain intentionally bounded; fresh decompile did not justify forcing a new prototype.
- No fresh evidence required a rename, signature rewrite, boundary recovery, or comment/tag mutation.

What remains unproven:

- Exact dispatch-table slot schema.
- Exact vector, matrix, quaternion, stride, lane-order, or optional-input layouts.
- Hidden EBX/EDI/XMM/MMX/stack ABI completeness.
- Runtime CPU feature selection and runtime math/render correctness.
- Exact source-body identity.
- BEA patching behavior, gameplay outcomes, and rebuild parity.

Probe token anchor: Wave1055; cfastvb-residual-dispatch-review-wave1055; 0x0059f360 CFastVB__DispatchOp_TransformVec4_0059f360; 0x0059f3d9 CFastVB__DispatchOp_NormalizeVec4_0059f3d9; 0x005a16b1 CFastVB__DispatchOp_TransformVec3ByMatrix4_005a16b1; 0x005a225f CFastVB__DispatchOp_TransformVec4Batch_Perspective_Alt_005a225f; 0x005a2ee9 CFastVB__DispatchOp_Determinant4x4_005a2ee9; 0x005a3508 CFastVB__DispatchOp_BuildMatrix4FromQuaternionPair_005a3508; 0x005a3791 CFastVB__DispatchOp_BuildQuaternionFromMatrix3x3_005a3791; CFastVB__InitDispatchTableVariant_005980be; CFastVB__InitDispatchTableVariant_0059822c; CFastVB__BroadcastMatrix4x4ToSIMDLanes; 769/1408 = 54.62%; 1091/1509 = 72.30%; 500/500 = 100.00%; 6246/6246 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260601-173102_post_wave1055_cfastvb_residual_dispatch_review_verified; no mutation.
