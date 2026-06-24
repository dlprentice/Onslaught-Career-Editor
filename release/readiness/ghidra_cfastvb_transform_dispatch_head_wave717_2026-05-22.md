# Ghidra CFastVB Transform Dispatch Head Wave717 Readiness Note

Date: 2026-05-22

Status: static Ghidra metadata saved and read back after corrected apply; no executable-byte change.

## Summary

Wave717 CFastVB transform dispatch head saved comments, tags, and selected signatures for fourteen adjacent SIMD transform-dispatch rows. Tag anchors are `cfastvb-transform-dispatch-head-wave717` and `wave717-readback-verified`.

The pass hardened six visible signatures/parameter names and left eight batch helpers comment/tag-only because the decompile still reports unknown calling convention, locked parameter storage, and hidden register context. The preserved first apply log recorded a read-back mismatch at `0x0059f6dd CFastVB__BroadcastMatrix4x4ToSIMDLanes` after Ghidra normalized the `__thiscall` receiver spelling; the corrected apply aligned to the saved explicit `this` parameter and the final dry run was idempotent.

| Address | Saved signature | Static evidence |
|---------|-----------------|-----------------|
| `0x0059f360 CFastVB__DispatchOp_TransformVec4_0059f360` | `int __stdcall CFastVB__DispatchOp_TransformVec4_0059f360(void * out_vec4, void * input_vec4, void * matrix4x4)` | Dispatch-table entry referenced by `CFastVB__InitDispatchTableVariant_005980be` and `_0059822c`; transforms a Vec4 through a 4x4 matrix and returns with `RET 0xc`. |
| `0x0059f3d9 CFastVB__DispatchOp_NormalizeVec4_0059f3d9` | `float * __stdcall CFastVB__DispatchOp_NormalizeVec4_0059f3d9(void * out_vec4, void * input_vec4)` | Dispatch-table entry; computes Vec4 length square, uses `rsqrtss` plus refinement, writes normalized components, and returns with `RET 0x8`. |
| `0x0059f473 CFastVB__DispatchOp_NormalizeVec4Scaled_0059f473` | `void __stdcall CFastVB__DispatchOp_NormalizeVec4Scaled_0059f473(void * out_vec4, void * input_vec4)` | Dispatch-table entry; normalizes a Vec4, applies scale constants from `0x0065e500`, and returns with `RET 0x8`. |
| `0x0059f4f1 CFastVB__DispatchOp_EulerToQuaternion_0059f4f1` | `void __stdcall CFastVB__DispatchOp_EulerToQuaternion_0059f4f1(void * out_quaternion_xyzw, float angle_x_radians, float angle_y_radians, float angle_z_radians)` | Dispatch-table entry; scales three Euler inputs, calls `CFastVB__SinCosApproxVec4_Paired`, writes four quaternion-style floats, and returns with `RET 0x10`. |
| `0x0059f5b3 CFastVB__BuildOrthonormalBasisFromCovariance` | `void __stdcall CFastVB__BuildOrthonormalBasisFromCovariance(void * out_quaternion_xyzw, void * matrix3x3_or_basis)` | Dispatch-adjacent helper; branches on matrix trace, chooses the maximum diagonal fallback when needed, and writes four quaternion-style output floats. |
| `0x0059f6dd CFastVB__BroadcastMatrix4x4ToSIMDLanes` | `void __thiscall CFastVB__BroadcastMatrix4x4ToSIMDLanes(void * this, void * simd_lane_matrix_out, void * matrix4x4)` | Shared batch helper; broadcasts each source 4x4 matrix scalar into four-wide lane blocks at offsets `0x00` through `0xfc`, with `RET 0x4`. |
| `0x0059f857 CFastVB__DispatchOp_TransformVec4Batch_0059f857` | `int CFastVB__DispatchOp_TransformVec4Batch_0059f857(void)` | Comment/tag-only; batch Vec4 matrix transform, four-record loop, matrix broadcast helper, scalar tail dispatch. |
| `0x0059fa5d CFastVB__DispatchOp_TransformVec4BatchW_0059fa5d` | `int CFastVB__DispatchOp_TransformVec4BatchW_0059fa5d(void)` | Comment/tag-only; batch Vec4W transform with hidden EBX/EDI context and dispatch-slot tail. |
| `0x0059fbeb CFastVB__DispatchOp_TransformProjectVec4Batch_0059fbeb` | `int CFastVB__DispatchOp_TransformProjectVec4Batch_0059fbeb(void)` | Comment/tag-only; projected Vec4 batch transform with reciprocal projection and hidden EBX/EDI context. |
| `0x0059fd51 CFastVB__DispatchOp_TransformVec4Batch_NoOffset_0059fd51` | `int CFastVB__DispatchOp_TransformVec4Batch_NoOffset_0059fd51(void)` | Comment/tag-only; no-offset Vec4 batch transform using broadcast matrix lanes. |
| `0x0059fe61 CFastVB__DispatchOp_TransformVec4Batch_Perspective_0059fe61` | `int CFastVB__DispatchOp_TransformVec4Batch_Perspective_0059fe61(void)` | Comment/tag-only; perspective-flavored Vec4 batch transform with scalar tail dispatch. |
| `0x005a009f CFastVB__DispatchOp_TransformVec3WBatch_005a009f` | `int CFastVB__DispatchOp_TransformVec3WBatch_005a009f(void)` | Comment/tag-only; batch Vec3W transform with W contribution and scalar tail dispatch. |
| `0x005a026f CFastVB__DispatchOp_TransformProjectVec3WBatch_005a026f` | `int CFastVB__DispatchOp_TransformProjectVec3WBatch_005a026f(void)` | Comment/tag-only; projected Vec3W batch transform with reciprocal projected components and scalar tail dispatch. |
| `0x005a04a0 CFastVB__DispatchOp_WeightedMatrixBlendBatch_005a04a0` | `int CFastVB__DispatchOp_WeightedMatrixBlendBatch_005a04a0(void)` | Comment/tag-only; weighted matrix/vector blend batch over a large stack-argument contract. |

Read-back evidence verified `14` metadata rows, `14` tag rows, `32` xref rows, `1246` post-instruction rows, `3766` wide post-instruction rows, and `14` post-decompile rows.

Dry/apply/corrected/final dry reported:

- Dry: `updated=0 skipped=14 renamed=0 would_rename=0 signature_updated=6 comment_only_updated=8 missing=0 bad=0`.
- Preserved first apply: `updated=13 skipped=0 renamed=0 would_rename=0 signature_updated=5 comment_only_updated=8 missing=0 bad=1`, with `REPORT: Save succeeded`.
- Corrected dry: `updated=0 skipped=14 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`.
- Corrected apply: `updated=1 skipped=13 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`.
- Final dry: `updated=0 skipped=14 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`.

Post-Wave717 queue telemetry:

- `6098` total functions.
- `4197` commented.
- `1901` commentless.
- `1216` exact-undefined signatures.
- `153` `param_N` signatures.
- Comment-backed proxy: `4197/6098 = 68.83%`.
- Strict clean-signature proxy: `4140/6098 = 67.89%`.
- Delta from Wave716: `+14` commented, `-14` commentless, `0` exact-undefined, `-6` `param_N`, `+14` strict clean-signature rows.
- Raw commentless head: `0x0042f220 CSPtrSet__Clear`.
- Next commentless high-signal head: `0x005a0b22 CFastVB__ConvertHalfToFloatArray_SSE`.

Verified backup: `G:\GhidraBackups\BEA_20260522-021449_post_wave717_cfastvb_transform_dispatch_head_verified`, `19` files, `166235015` bytes, `DiffCount=0`.

## Boundaries

Wave717 proves static retail Ghidra metadata only. Exact dispatch-table slot schema, vector/matrix storage contract, batch helper hidden-register ABI, source identity, runtime math correctness, BEA patching, and rebuild parity remain unproven.

Probe anchors: `Wave717 CFastVB transform dispatch head`, `cfastvb-transform-dispatch-head-wave717`, `0x0059f360 CFastVB__DispatchOp_TransformVec4_0059f360`, `0x0059f6dd CFastVB__BroadcastMatrix4x4ToSIMDLanes`, `0x005a04a0 CFastVB__DispatchOp_WeightedMatrixBlendBatch_005a04a0`, `Ghidra thiscall normalization mismatch`, `0x005a0b22 CFastVB__ConvertHalfToFloatArray_SSE`, `0x0042f220 CSPtrSet__Clear`, `G:\GhidraBackups\BEA_20260522-021449_post_wave717_cfastvb_transform_dispatch_head_verified`.
