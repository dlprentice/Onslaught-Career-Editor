# Ghidra Wave900 Through Wave1053 Recheck

Status: complete local static evidence gate
Date: 2026-06-01
Scope: `wave900-plus-through-wave1053-recheck`

This note extends the Wave900-plus static recheck boundary through Wave1053. Wave900 remains the loaded-Ghidra export-contract function-quality closure point; Wave1053 adds a focused read-only CFastVB stack-locked transform/curve/quaternion dispatch review with no mutation.

Wave1053 (`cfastvb-stacklocked-transform-review-wave1053`) re-read twenty-four existing CFastVB stack-locked/comment-only transform, curve, quaternion, and optional-composition dispatch helpers. Representative anchors: `0x0059f857 CFastVB__DispatchOp_TransformVec4Batch_0059f857`, `0x005a04a0 CFastVB__DispatchOp_WeightedMatrixBlendBatch_005a04a0`, `0x005a0f50 CFastVB__EvaluateCubicBasisVec3`, `0x005a13f7 CFastVB__DispatchOp_InterpolateVec3ByReciprocal_005a13f7`, `0x005a38c0 CFastVB__DispatchOp_TransformVec4ArrayByMatrix4`, `0x005a519e CFastVB__DispatchOp_BlendQuaternionSplineSegment_005a519e`, `0x005a647f CFastVB__DispatchOp_ComposeTransformFromOptionalInputs_Core_005a647f`, `0x005a7617 CFastVB__DispatchOp_BuildRotationMatrixFromEulerAngles`, and `0x005a7e09 CFastVB__DispatchOp_ComposeMatrixFromOptionalTransforms`.

Fresh evidence:

- Primary exports: `24` metadata rows, `24` tag rows, `34` DATA xref rows, `4682` function-body instruction rows, and `24` decompile rows.
- Context exports: `12` metadata rows, `12` tag rows, `49` xref rows, `949` function-body instruction rows, and `12` decompile rows.
- Incoming DATA refs still tie every target to `CFastVB__InitDispatchTableVariant_005980be`, `CFastVB__InitDispatchTableVariant_0059822c`, or `CFastVB__InitDispatchOpsFromFeatureFlags`.
- Queue closure remains `6246/6246 = 100.00%`.
- Wave911 focused progress advances to `769/1408 = 54.62%`.
- Expanded static surface progress advances to `1057/1509 = 70.05%`.
- Wave911 top-500 coverage remains `500/500 = 100.00%`.
- Verified backup: `G:\GhidraBackups\BEA_20260601-162015_post_wave1053_cfastvb_stacklocked_transform_review_verified`, `19` files, `174623623` bytes, `DiffCount=0`, `HashDiffCount=0`.

Validation command:

```powershell
npm run test:ghidra-wave900-plus-through-wave1053-recheck
```

Boundary note: this aggregate gate is static documentation/evidence hygiene. It does not prove exact dispatch-table slot schema, vector/matrix/quaternion/stride/lane-order layouts, hidden EBX/EDI/XMM/MMX/stack ABI completeness, runtime CPU feature selection, runtime math/render correctness, exact source-body identity, BEA patching, gameplay outcomes, or rebuild parity.

Probe token anchor: Wave1053; cfastvb-stacklocked-transform-review-wave1053; 0x0059f857 CFastVB__DispatchOp_TransformVec4Batch_0059f857; 0x005a04a0 CFastVB__DispatchOp_WeightedMatrixBlendBatch_005a04a0; 0x005a0f50 CFastVB__EvaluateCubicBasisVec3; 0x005a13f7 CFastVB__DispatchOp_InterpolateVec3ByReciprocal_005a13f7; 0x005a38c0 CFastVB__DispatchOp_TransformVec4ArrayByMatrix4; 0x005a519e CFastVB__DispatchOp_BlendQuaternionSplineSegment_005a519e; 0x005a647f CFastVB__DispatchOp_ComposeTransformFromOptionalInputs_Core_005a647f; 0x005a7617 CFastVB__DispatchOp_BuildRotationMatrixFromEulerAngles; 0x005a7e09 CFastVB__DispatchOp_ComposeMatrixFromOptionalTransforms; CFastVB__InitDispatchTableVariant_005980be; CFastVB__InitDispatchTableVariant_0059822c; CFastVB__InitDispatchOpsFromFeatureFlags; 769/1408 = 54.62%; 1057/1509 = 70.05%; 500/500 = 100.00%; 6246/6246 = 100.00%; G:\GhidraBackups\BEA_20260601-162015_post_wave1053_cfastvb_stacklocked_transform_review_verified; no mutation.
