# Ghidra Wave900 Through Wave1055 Recheck

Status: complete local static evidence gate
Date: 2026-06-01
Scope: `wave900-plus-through-wave1055-recheck`

This note extends the Wave900-plus static recheck boundary through Wave1055. Wave900 remains the loaded-Ghidra export-contract function-quality closure point; Wave1055 adds a read-only CFastVB residual dispatch review.

Wave1055 (`cfastvb-residual-dispatch-review-wave1055`) re-read twenty-six existing CFastVB vector/quaternion/matrix dispatch helpers: `0x0059f360 CFastVB__DispatchOp_TransformVec4_0059f360`, `0x0059f3d9 CFastVB__DispatchOp_NormalizeVec4_0059f3d9`, `0x0059f473 CFastVB__DispatchOp_NormalizeVec4Scaled_0059f473`, `0x0059f4f1 CFastVB__DispatchOp_EulerToQuaternion_0059f4f1`, `0x0059f5b3 CFastVB__BuildOrthonormalBasisFromCovariance`, `0x005a14a5 CFastVB__DispatchOp_BuildPlaneFromTriangle_005a14a5`, `0x005a15a5 CFastVB__DispatchOp_QuaternionToMatrix4_005a15a5`, `0x005a16b1 CFastVB__DispatchOp_TransformVec3ByMatrix4_005a16b1`, `0x005a1786 CFastVB__DispatchOp_TransformProjectVec3ByMatrix4_005a1786`, `0x005a1889 CFastVB__DispatchOp_NormalizeVec3_005a1889`, `0x005a1979 CFastVB__DispatchOp_NormalizeVec4_005a1979`, `0x005a1c55 CFastVB__DispatchOp_TransformVec4Batch_Alt_005a1c55`, `0x005a1e5b CFastVB__DispatchOp_TransformVec4BatchW_Alt_005a1e5b`, `0x005a1fe9 CFastVB__DispatchOp_TransformProjectVec4Batch_Alt_005a1fe9`, `0x005a214f CFastVB__DispatchOp_TransformVec4Batch_NoOffset_Alt_005a214f`, `0x005a225f CFastVB__DispatchOp_TransformVec4Batch_Perspective_Alt_005a225f`, `0x005a249d CFastVB__DispatchOp_TransformVec3WBatch_Alt_005a249d`, `0x005a2a61 CFastVB__DispatchOp_TransformVec2ByMatrix4`, `0x005a2ee9 CFastVB__DispatchOp_Determinant4x4_005a2ee9`, `0x005a2ff4 CFastVB__DispatchOp_BuildPlaneFromTriangle_Alt_005a2ff4`, `0x005a30f4 CFastVB__DispatchOp_QuaternionToMatrix4_Alt_005a30f4`, `0x005a3200 CFastVB__DispatchOp_TransformVec4ByMatrix4_005a3200`, `0x005a32d4 CFastVB__DispatchOp_MultiplyMatrix4x4_005a32d4`, `0x005a3508 CFastVB__DispatchOp_BuildMatrix4FromQuaternionPair_005a3508`, `0x005a36cf CFastVB__DispatchOp_BuildQuaternionFromEulerAngles_005a36cf`, and `0x005a3791 CFastVB__DispatchOp_BuildQuaternionFromMatrix3x3_005a3791`.

Fresh evidence:

- Primary exports: `26` metadata rows, `26` tag rows, `50` xref rows, `2277` function-body instruction rows, and `26` decompile rows.
- Context exports: `12` metadata rows, `12` tag rows, `45` xref rows, `2263` function-body instruction rows, and `12` decompile rows.
- Context anchors include `CFastVB__InitDispatchTableVariant_005980be`, `CFastVB__InitDispatchTableVariant_0059822c`, `CFastVB__InitDispatchOpsFromFeatureFlags`, `CFastVB__BroadcastMatrix4x4ToSIMDLanes`, `CFastVB__DispatchOp_WeightedMatrixBlendBatch_005a04a0`, `CFastVB__EvaluateCubicBasisVec3`, `CFastVB__DispatchOp_TransformVec4ArrayByMatrix4`, `CFastVB__DispatchOp_InterpolateQuaternionPairCore_005a4d98`, `CFastVB__DispatchOp_NormalizeQuaternionWithAcosFallback_005a5052`, `CFastVB__DispatchOp_ComposeTransformFromOptionalInputs_Core_005a647f`, `CFastVB__DispatchOp_InvertMatrix4x4_WithDeterminant_005a8f5d`, and `CFastVB__DispatchOp_MultiplyMatrix4x4_Packed_005a9d78`.
- Queue closure remains `6246/6246 = 100.00%`.
- Wave911 focused progress remains `769/1408 = 54.62%`.
- Expanded static surface progress advances to `1091/1509 = 72.30%`.
- Wave911 top-500 coverage remains `500/500 = 100.00%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260601-173102_post_wave1055_cfastvb_residual_dispatch_review_verified`, `19` files, `174656391` bytes, `DiffCount=0`, `HashDiffCount=0`.

Validation command:

```powershell
npm run test:ghidra-wave900-plus-through-wave1055-recheck
```

Boundary note: this aggregate gate is static documentation/evidence hygiene. Exact dispatch-table slot schema, vector/matrix/quaternion/stride/lane-order layouts, hidden EBX/EDI/XMM/MMX/stack ABI completeness, runtime CPU feature selection, runtime math/render correctness, exact source-body identity, BEA patching, gameplay outcomes, and rebuild parity remain separate proof.

Probe token anchor: Wave1055; cfastvb-residual-dispatch-review-wave1055; 0x0059f360 CFastVB__DispatchOp_TransformVec4_0059f360; 0x0059f3d9 CFastVB__DispatchOp_NormalizeVec4_0059f3d9; 0x005a16b1 CFastVB__DispatchOp_TransformVec3ByMatrix4_005a16b1; 0x005a225f CFastVB__DispatchOp_TransformVec4Batch_Perspective_Alt_005a225f; 0x005a2ee9 CFastVB__DispatchOp_Determinant4x4_005a2ee9; 0x005a3508 CFastVB__DispatchOp_BuildMatrix4FromQuaternionPair_005a3508; 0x005a3791 CFastVB__DispatchOp_BuildQuaternionFromMatrix3x3_005a3791; CFastVB__InitDispatchTableVariant_005980be; CFastVB__InitDispatchTableVariant_0059822c; CFastVB__BroadcastMatrix4x4ToSIMDLanes; 769/1408 = 54.62%; 1091/1509 = 72.30%; 500/500 = 100.00%; 6246/6246 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260601-173102_post_wave1055_cfastvb_residual_dispatch_review_verified; no mutation.
