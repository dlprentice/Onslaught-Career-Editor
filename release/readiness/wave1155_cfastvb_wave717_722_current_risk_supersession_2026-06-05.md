# Wave1155 CFastVB Wave717-722 Current-Risk Supersession Readiness Note

Status: complete static supersession accounting
Date: 2026-06-05
Scope: `wave1155-cfastvb-wave717-722-current-risk-supersession`

Wave1155 accounts for 46 Wave1108 current focused CFastVB rows as superseded by prior Wave717-Wave722 saved Ghidra read-back evidence. This wave performs no new Ghidra export and no mutation.

Validation target: `npm run test:wave1155-cfastvb-wave717-722-current-risk-supersession`.

Accounting after Wave1155:

- Static Ghidra function-quality closure: `6411/6411 = 100.00%`.
- Static debt: `0 / 0 / 0` commentless / exact-undefined / `param_N`.
- Expanded post-100 static surface: `1560/1560 = 100.00%`.
- Wave911 focused: `812/1408 = 57.67%`, historical-retired/non-reconstructable.
- Wave911 top-500: `500/500 = 100.00%`.
- Wave1108 current focused accounting: `424/1179 = 35.96%`.
- Current risk candidates: 6166.
- Current focused candidates: 1178.
- Live regenerated current focused candidates: 1178.
- Remaining active focused work: 755.

Representative anchors:

| Prior wave | Representative covered row |
| --- | --- |
| Wave717 | `0x0059f360 CFastVB__DispatchOp_TransformVec4_0059f360`; `0x0059f6dd CFastVB__BroadcastMatrix4x4ToSIMDLanes` |
| Wave718 | `0x005a0b22 CFastVB__ConvertHalfToFloatArray_SSE`; `0x005a1a8e CFastVB__BuildMatrix4x4FromQuaternion` |
| Wave719 | `0x005a298f CFastVB__ConvertHalfToFloatArray_SIMD`; `0x005a3791 CFastVB__DispatchOp_BuildQuaternionFromMatrix3x3_005a3791` |
| Wave720 | `0x005a47f2 CFastVB__DispatchOp_ExtractAxisAndOptionalAngle`; `0x005a5052 CFastVB__DispatchOp_NormalizeQuaternionWithAcosFallback_005a5052` |
| Wave721 | `0x005a62bf CFastVB__DispatchOp_InitIdentityMatrix4x4_005a62bf`; `0x005a9d78 CFastVB__DispatchOp_MultiplyMatrix4x4_Packed_005a9d78` |
| Wave722 | `0x005aa480 CFastVB__DispatchOp_ConvertPackedS16ToFloatPairBatch_005aa480`; `0x005ab00b CFastVB__DispatchOp_NormalizeQuaternionPacked_005ab00b` |

Verified prior backups:

- `[maintainer-local-ghidra-backup-root]\BEA_20260522-021449_post_wave717_cfastvb_transform_dispatch_head_verified`
- `[maintainer-local-ghidra-backup-root]\BEA_20260522-025058_post_wave718_cfastvb_scalar_transform_core_verified`
- `[maintainer-local-ghidra-backup-root]\BEA_20260522-032725_post_wave719_cfastvb_matrix_quaternion_core_verified`
- `[maintainer-local-ghidra-backup-root]\BEA_20260522-035533_post_wave720_cfastvb_quaternion_tail_verified`
- `[maintainer-local-ghidra-backup-root]\BEA_20260522-043029_post_wave721_cfastvb_matrix_rotation_continuation_verified`
- `[maintainer-local-ghidra-backup-root]\BEA_20260522-050258_post_wave722_cfastvb_packed_vec2_quaternion_tail_verified`

Latest completed Ghidra review backup remains `[maintainer-local-ghidra-backup-root]\BEA_20260605-215410_post_wave1154_unitai_deploy_target_current_risk_review_verified`. Wave1155 has no new live-project backup because it performs no new Ghidra operation.

Probe token anchor: Wave1155; wave1155-cfastvb-wave717-722-current-risk-supersession; 424/1179 = 35.96%; 46 current-risk rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 755; current risk candidates: 6166; CFastVB Wave717-Wave722 current-risk supersession; no new Ghidra export; no mutation; Codex read-only consult used; 0 / 0 / 0; 6411/6411 = 100.00%; CFastVB__DispatchOp_TransformVec4_0059f360; CFastVB__ConvertHalfToFloatArray_SSE; CFastVB__ConvertHalfToFloatArray_SIMD; CFastVB__DispatchOp_ExtractAxisAndOptionalAngle; CFastVB__DispatchOp_InitIdentityMatrix4x4_005a62bf; CFastVB__DispatchOp_NormalizeQuaternionPacked_005ab00b; [maintainer-local-ghidra-backup-root]\BEA_20260522-021449_post_wave717_cfastvb_transform_dispatch_head_verified; [maintainer-local-ghidra-backup-root]\BEA_20260522-050258_post_wave722_cfastvb_packed_vec2_quaternion_tail_verified; [maintainer-local-ghidra-backup-root]\BEA_20260605-215410_post_wave1154_unitai_deploy_target_current_risk_review_verified; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction.

Boundary: this is static supersession accounting only. Runtime math/render correctness, hidden ABI completeness, exact vector/matrix/quaternion layouts, exact source-body identity, BEA patching behavior, gameplay outcomes, visual QA, and rebuild parity remain separate proof.
