# Ghidra CFastVB Matrix/Quaternion Core Wave719 Readiness Note

Status: passed
Date: 2026-05-22

Wave719 CFastVB matrix/quaternion core saved twelve adjacent CFastVB math/transform rows from `0x005a298f CFastVB__ConvertHalfToFloatArray_SIMD` through `0x005a3791 CFastVB__DispatchOp_BuildQuaternionFromMatrix3x3_005a3791` with the `cfastvb-matrix-quaternion-core-wave719` and `wave719-readback-verified` tags.

The pass hardened twelve visible signatures/parameter names:

| Address | Saved state | Evidence |
| --- | --- | --- |
| `0x005a298f` | `int __stdcall CFastVB__ConvertHalfToFloatArray_SIMD(float * out_float32, ushort * in_float16, uint element_count)` | SIMD half-float conversion referenced by `CFastVB__InitDispatchTableVariant_0059822c`; processes eight inputs through `CFastVB__ConvertHalfToFloat8_CheckSpecialCasesSIMD` when possible and tails scalar ushort inputs into float output slots. |
| `0x005a2a61` | `void __stdcall CFastVB__DispatchOp_TransformVec2ByMatrix4(float * out_vec4, float * input_vec4, float * matrix4x4)` | Scalar transform dispatch referenced by both CFastVB dispatch-table variants and called by perspective batch tails; writes four transformed output floats. |
| `0x005a2b2d` | `float * __stdcall CFastVB__InvertMatrix4x4_WithDeterminant(float * out_inverse_matrix4x4, float * out_determinant_or_null, float * input_matrix4x4)` | Matrix4x4 inverse helper referenced by both dispatch-table variants; writes optional determinant, returns null on zero determinant, otherwise writes the reciprocal-determinant-scaled inverse. |
| `0x005a2e29` | `void __stdcall CFastVB__ComputeAdjugateVec4_PackedB(float * out_vec4, float * row_a_vec4, float * row_b_vec4, float * row_c_vec4)` | Packed adjugate/cofactor Vec4 helper using the `0x0065e7a0` constant block for sign masks. |
| `0x005a2ee9` | `double __stdcall CFastVB__DispatchOp_Determinant4x4_005a2ee9(float * matrix4x4)` | 4x4 determinant dispatch. Return type remains Ghidra's current `double` because the decompiler materializes the scalar float expression through the x87-style return model. |
| `0x005a2ff4` | `void __stdcall CFastVB__DispatchOp_BuildPlaneFromTriangle_Alt_005a2ff4(float * out_plane_vec4, float * point_a_vec3, float * point_b_vec3, float * point_c_vec3)` | Alternate plane-from-triangle dispatch; edge deltas, cross-product normal, `rsqrtss` refinement, xyz normal, and sign-masked distance term. |
| `0x005a30f4` | `void __stdcall CFastVB__DispatchOp_QuaternionToMatrix4_Alt_005a30f4(float * out_matrix4x4, float * quaternion_xyzw)` | Alternate quaternion-to-matrix4 dispatch using the `0x0065e7e0..0x0065e85c` constant block. |
| `0x005a3200` | `void __stdcall CFastVB__DispatchOp_TransformVec4ByMatrix4_005a3200(float * out_vec4, float * input_vec4, float * matrix4x4)` | Scalar Vec4-by-matrix dispatch referenced by both dispatch-table variants and by Vec4 batch tails. |
| `0x005a32d4` | `void __stdcall CFastVB__DispatchOp_MultiplyMatrix4x4_005a32d4(float * out_matrix4x4, float * left_matrix4x4, float * right_matrix4x4)` | Matrix4x4 multiply dispatch writing sixteen row/column dot-product output floats. |
| `0x005a3508` | `void __stdcall CFastVB__DispatchOp_BuildMatrix4FromQuaternionPair_005a3508(float * out_matrix4x4, float * basis_quaternion_xyzw, float * rotation_quaternion_xyzw)` | Quaternion-pair-to-matrix dispatch; combines a basis quaternion-like input with a normalized rotation quaternion and writes a 4x4 matrix. |
| `0x005a36cf` | `void __stdcall CFastVB__DispatchOp_BuildQuaternionFromEulerAngles_005a36cf(float * out_quaternion_xyzw, float angle_x_radians, float angle_y_radians, float angle_z_radians)` | Euler-angle-to-quaternion dispatch; calls `CFastVB__SinCosVec4Approx` and writes four quaternion floats. |
| `0x005a3791` | `void __stdcall CFastVB__DispatchOp_BuildQuaternionFromMatrix3x3_005a3791(float * out_quaternion_xyzw, float * matrix3x3)` | Matrix3x3-to-quaternion dispatch with trace-positive and largest-diagonal fallback branches plus axis-index table `0x005f4340`. |

Validation:

- Dry/apply/final dry summaries: `updated=0 skipped=12 renamed=0 would_rename=0 signature_updated=12 comment_only_updated=0 missing=0 bad=0`; `updated=12 skipped=0 renamed=0 would_rename=0 signature_updated=12 comment_only_updated=0 missing=0 bad=0`; `updated=0 skipped=12 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`.
- Post exports verified `12` metadata rows, `12` tag rows, `25` xref rows, `1116` instruction rows, `3180` wide instruction rows, and `12` decompile rows.
- Queue refresh passed: `6098` total, `4226` commented, `1872` commentless, `1216` exact-undefined signatures, `131` `param_N` signatures, strict clean-signature proxy `4169/6098 = 68.37%`.
- Current raw commentless head remains `0x0042f220 CSPtrSet__Clear`; current high-signal head is `0x005a47f2 CFastVB__DispatchOp_ExtractAxisAndOptionalAngle`.
- Verified backup: `G:\GhidraBackups\BEA_20260522-032725_post_wave719_cfastvb_matrix_quaternion_core_verified`, `19` files, `166366087` bytes, `DiffCount=0`.

Scope boundary: this is static saved-Ghidra metadata/decompile/instruction/xref evidence only. Exact dispatch-table slot schema, vector/matrix storage contract, source identity, runtime math correctness, BEA patching, and rebuild parity remain deferred.

Probe anchors: `Wave719 CFastVB matrix/quaternion core`, `cfastvb-matrix-quaternion-core-wave719`, `0x005a298f CFastVB__ConvertHalfToFloatArray_SIMD`, `0x005a2b2d CFastVB__InvertMatrix4x4_WithDeterminant`, `0x005a3791 CFastVB__DispatchOp_BuildQuaternionFromMatrix3x3_005a3791`, `0x0042f220 CSPtrSet__Clear`, `0x005a47f2 CFastVB__DispatchOp_ExtractAxisAndOptionalAngle`, `G:\GhidraBackups\BEA_20260522-032725_post_wave719_cfastvb_matrix_quaternion_core_verified`.
