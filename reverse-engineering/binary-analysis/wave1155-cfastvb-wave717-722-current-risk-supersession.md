# Wave1155 CFastVB Wave717-722 Current-Risk Supersession

Status: complete static supersession accounting
Last updated: 2026-06-05
Scope: `wave1155-cfastvb-wave717-722-current-risk-supersession`

Wave1155 accounts for 46 CFastVB score-20 rows from the Wave1108 current focused denominator as superseded by prior Wave717-Wave722 saved Ghidra read-back evidence. This is no new Ghidra export, no mutation, no rename, no signature change, no comment/tag change, no function-boundary change, no executable-byte change, no BEA launch, no installed-game mutation, no save mutation, and no runtime-file mutation.

## Accounting

| Track | Current |
| --- | ---: |
| Static Ghidra function-quality closure | `6411/6411 = 100.00%` |
| Commentless / exact-undefined / `param_N` debt | `0 / 0 / 0` |
| Expanded post-100 static surface | `1560/1560 = 100.00%` |
| Wave911 focused | `812/1408 = 57.67%`; historical-retired/non-reconstructable |
| Wave911 top-500 | `500/500 = 100.00%` |
| Wave1108 current focused accounting | `424/1179 = 35.96%` |
| Current risk candidates | 6166 |
| Current focused candidates | 1178 |
| Live regenerated current focused candidates | 1178 |
| Remaining active focused work | 755 |

## Superseded Rows

These rows were still present in the active Wave1108 current focused candidate list after Wave1154. Wave1155 excludes the 24 CFastVB rows already counted by Wave1109 and Wave1110.

| Prior wave | Address | Name |
| --- | --- | --- |
| Wave717 | `0x0059f360` | `CFastVB__DispatchOp_TransformVec4_0059f360` |
| Wave717 | `0x0059f3d9` | `CFastVB__DispatchOp_NormalizeVec4_0059f3d9` |
| Wave717 | `0x0059f473` | `CFastVB__DispatchOp_NormalizeVec4Scaled_0059f473` |
| Wave717 | `0x0059f4f1` | `CFastVB__DispatchOp_EulerToQuaternion_0059f4f1` |
| Wave717 | `0x0059f5b3` | `CFastVB__BuildOrthonormalBasisFromCovariance` |
| Wave717 | `0x0059f6dd` | `CFastVB__BroadcastMatrix4x4ToSIMDLanes` |
| Wave718 | `0x005a0b22` | `CFastVB__ConvertHalfToFloatArray_SSE` |
| Wave718 | `0x005a0df6` | `CFastVB__ComputeAdjugateVec4_PackedA` |
| Wave718 | `0x005a0eb6` | `CFastVB__NormalizeVec4_ReciprocalSqrt` |
| Wave718 | `0x005a14a5` | `CFastVB__DispatchOp_BuildPlaneFromTriangle_005a14a5` |
| Wave718 | `0x005a15a5` | `CFastVB__DispatchOp_QuaternionToMatrix4_005a15a5` |
| Wave718 | `0x005a16b1` | `CFastVB__DispatchOp_TransformVec3ByMatrix4_005a16b1` |
| Wave718 | `0x005a1786` | `CFastVB__DispatchOp_TransformProjectVec3ByMatrix4_005a1786` |
| Wave718 | `0x005a1889` | `CFastVB__DispatchOp_NormalizeVec3_005a1889` |
| Wave718 | `0x005a1979` | `CFastVB__DispatchOp_NormalizeVec4_005a1979` |
| Wave718 | `0x005a1a8e` | `CFastVB__BuildMatrix4x4FromQuaternion` |
| Wave719 | `0x005a298f` | `CFastVB__ConvertHalfToFloatArray_SIMD` |
| Wave719 | `0x005a2a61` | `CFastVB__DispatchOp_TransformVec2ByMatrix4` |
| Wave719 | `0x005a2b2d` | `CFastVB__InvertMatrix4x4_WithDeterminant` |
| Wave719 | `0x005a2e29` | `CFastVB__ComputeAdjugateVec4_PackedB` |
| Wave719 | `0x005a2ee9` | `CFastVB__DispatchOp_Determinant4x4_005a2ee9` |
| Wave719 | `0x005a2ff4` | `CFastVB__DispatchOp_BuildPlaneFromTriangle_Alt_005a2ff4` |
| Wave719 | `0x005a30f4` | `CFastVB__DispatchOp_QuaternionToMatrix4_Alt_005a30f4` |
| Wave719 | `0x005a3200` | `CFastVB__DispatchOp_TransformVec4ByMatrix4_005a3200` |
| Wave719 | `0x005a32d4` | `CFastVB__DispatchOp_MultiplyMatrix4x4_005a32d4` |
| Wave719 | `0x005a3508` | `CFastVB__DispatchOp_BuildMatrix4FromQuaternionPair_005a3508` |
| Wave719 | `0x005a36cf` | `CFastVB__DispatchOp_BuildQuaternionFromEulerAngles_005a36cf` |
| Wave719 | `0x005a3791` | `CFastVB__DispatchOp_BuildQuaternionFromMatrix3x3_005a3791` |
| Wave720 | `0x005a47f2` | `CFastVB__DispatchOp_ExtractAxisAndOptionalAngle` |
| Wave720 | `0x005a4d2c` | `CFastVB__DispatchOp_BuildQuaternionFromAxisAngleVector_005a4d2c` |
| Wave720 | `0x005a4d98` | `CFastVB__DispatchOp_InterpolateQuaternionPairCore_005a4d98` |
| Wave720 | `0x005a5052` | `CFastVB__DispatchOp_NormalizeQuaternionWithAcosFallback_005a5052` |
| Wave721 | `0x005a62bf` | `CFastVB__DispatchOp_InitIdentityMatrix4x4_005a62bf` |
| Wave721 | `0x005a7cf0` | `CFastVB__DispatchOp_BuildRotationMatrixFromAxisAngleVector` |
| Wave721 | `0x005a8f5d` | `CFastVB__DispatchOp_InvertMatrix4x4_WithDeterminant_005a8f5d` |
| Wave721 | `0x005a9637` | `CFastVB__DispatchOp_InvertMatrix4x4_Variant_005a9637` |
| Wave721 | `0x005a99f8` | `CFastVB__DispatchOp_TransformVec3ByMatrix4_NoTranslation_005a99f8` |
| Wave721 | `0x005a9a5f` | `CFastVB__DispatchOp_NormalizeVec3_Packed_005a9a5f` |
| Wave721 | `0x005a9ced` | `CFastVB__DispatchOp_TransformProjectVec3ByMatrix4_005a9ced` |
| Wave721 | `0x005a9d78` | `CFastVB__DispatchOp_MultiplyMatrix4x4_Packed_005a9d78` |
| Wave721 | `0x005a9f3f` | `CFastVB__DispatchOp_TransformProjectVec3ByMatrix4_Alt_005a9f3f` |
| Wave722 | `0x005aa480` | `CFastVB__DispatchOp_ConvertPackedS16ToFloatPairBatch_005aa480` |
| Wave722 | `0x005aa73b` | `CFastVB__DispatchOp_TransformVec2ByMatrix4_WithTranslation_005aa73b` |
| Wave722 | `0x005aa790` | `CFastVB__DispatchOp_TransformVec2ByMatrix4_NoTranslation_005aa790` |
| Wave722 | `0x005aa7c9` | `CFastVB__DispatchOp_TransformProjectVec2ByMatrix4_005aa7c9` |
| Wave722 | `0x005ab00b` | `CFastVB__DispatchOp_NormalizeQuaternionPacked_005ab00b` |

## Prior Evidence

Prior verified backups:

- Wave717: `G:\GhidraBackups\BEA_20260522-021449_post_wave717_cfastvb_transform_dispatch_head_verified`
- Wave718: `G:\GhidraBackups\BEA_20260522-025058_post_wave718_cfastvb_scalar_transform_core_verified`
- Wave719: `G:\GhidraBackups\BEA_20260522-032725_post_wave719_cfastvb_matrix_quaternion_core_verified`
- Wave720: `G:\GhidraBackups\BEA_20260522-035533_post_wave720_cfastvb_quaternion_tail_verified`
- Wave721: `G:\GhidraBackups\BEA_20260522-043029_post_wave721_cfastvb_matrix_rotation_continuation_verified`
- Wave722: `G:\GhidraBackups\BEA_20260522-050258_post_wave722_cfastvb_packed_vec2_quaternion_tail_verified`

Latest completed Ghidra review backup remains `G:\GhidraBackups\BEA_20260605-215410_post_wave1154_unitai_deploy_target_current_risk_review_verified`. Wave1155 did not perform a new Ghidra operation, so it has no new live-project backup.

Probe token anchor: Wave1155; wave1155-cfastvb-wave717-722-current-risk-supersession; 424/1179 = 35.96%; 46 current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 755; current risk candidates: 6166; CFastVB Wave717-Wave722 current-risk supersession; no new Ghidra export; no mutation; Codex read-only consult used; 0 / 0 / 0; 6411/6411 = 100.00%; CFastVB__DispatchOp_TransformVec4_0059f360; CFastVB__ConvertHalfToFloatArray_SSE; CFastVB__ConvertHalfToFloatArray_SIMD; CFastVB__DispatchOp_ExtractAxisAndOptionalAngle; CFastVB__DispatchOp_InitIdentityMatrix4x4_005a62bf; CFastVB__DispatchOp_NormalizeQuaternionPacked_005ab00b; G:\GhidraBackups\BEA_20260522-021449_post_wave717_cfastvb_transform_dispatch_head_verified; G:\GhidraBackups\BEA_20260522-050258_post_wave722_cfastvb_packed_vec2_quaternion_tail_verified; G:\GhidraBackups\BEA_20260605-215410_post_wave1154_unitai_deploy_target_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.

## Boundary

Wave1155 closes current-risk accounting for these 46 rows only. It does not prove runtime math/render correctness, hidden ABI completeness, exact vector/matrix/quaternion layouts, exact source-body identity, BEA patching behavior, gameplay outcomes, visual QA, or rebuild parity.
