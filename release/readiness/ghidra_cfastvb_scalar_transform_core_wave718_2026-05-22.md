# Ghidra CFastVB Scalar Transform Core Wave718 Readiness Note

Status: passed
Date: 2026-05-22

Wave718 CFastVB scalar transform core saved seventeen adjacent CFastVB math/transform rows from `0x005a0b22 CFastVB__ConvertHalfToFloatArray_SSE` through `0x005a1a8e CFastVB__BuildMatrix4x4FromQuaternion` with the `cfastvb-scalar-transform-core-wave718` and `wave718-readback-verified` tags.

The pass hardened ten visible signatures/parameter names and left seven stack-locked cubic/interpolation helpers comment/tag-only:

| Address | Saved state | Evidence |
| --- | --- | --- |
| `0x005a0b22` | `int __stdcall CFastVB__ConvertHalfToFloatArray_SSE(float * out_float32, ushort * in_float16, uint element_count)` | Half-float conversion path referenced by `CFastVB__InitDispatchTableVariant_005980be`; processes eight inputs through `CFastVB__ConvertHalfToFloat8_SIMDKernel` when possible and tails scalar ushort inputs into float output slots. |
| `0x005a0df6` | `void __stdcall CFastVB__ComputeAdjugateVec4_PackedA(float * out_vec4, float * row_a_vec4, float * row_b_vec4, float * row_c_vec4)` | Reads three Vec4 rows, combines 3x3 minor products with sign-mask constants at `0x0065e600..0x0065e60c`, and returns with `RET 0x10`. |
| `0x005a0eb6` | `float * __stdcall CFastVB__NormalizeVec4_ReciprocalSqrt(float * out_vec4, float * input_vec4)` | Vec4 normalization with `rsqrtss` refinement; referenced by both CFastVB dispatch-table variants. |
| `0x005a0f50` through `0x005a13f7` | Comment/tag-only stack-locked cubic/interpolation helpers | `CFastVB__EvaluateCubicBasisVec3`, `Vec2`, `Vec4`, cubic blend Vec3/Vec4, derivative Vec2, and reciprocal-weighted interpolation retain current `int ... (void)` signatures because Ghidra still reports unknown calling convention and locked parameter storage. |
| `0x005a14a5` | `void __stdcall CFastVB__DispatchOp_BuildPlaneFromTriangle_005a14a5(float * out_plane_vec4, float * point_a_vec3, float * point_b_vec3, float * point_c_vec3)` | Cross-product normal construction, `rsqrtss` normalization, xyz normal, and sign-masked distance term. |
| `0x005a15a5` | `void __stdcall CFastVB__DispatchOp_QuaternionToMatrix4_005a15a5(float * out_matrix4x4, float * quaternion_xyzw)` | Quaternion normalization and sixteen matrix-float expansion. |
| `0x005a16b1` | `void __stdcall CFastVB__DispatchOp_TransformVec3ByMatrix4_005a16b1(float * out_vec3, float * input_vec3, float * matrix4x4)` | Scalar Vec3 transform used by dispatch tables and batch tails. |
| `0x005a1786` | `void __stdcall CFastVB__DispatchOp_TransformProjectVec3ByMatrix4_005a1786(float * out_projected_vec3, float * input_vec3, float * matrix4x4)` | Scalar projected Vec3 transform with reciprocal projection refinement. |
| `0x005a1889` | `void __stdcall CFastVB__DispatchOp_NormalizeVec3_005a1889(float * out_vec3, float * input_vec3)` | Tiny-length guard plus `rsqrtss` refinement for xyz. |
| `0x005a1979` | `void __stdcall CFastVB__DispatchOp_NormalizeVec4_005a1979(float * out_vec4, float * input_vec4)` | Tiny-length guard plus `rsqrtss` refinement for xyz and fourth-lane scaling. |
| `0x005a1a8e` | `void __stdcall CFastVB__BuildMatrix4x4FromQuaternion(float * out_matrix4x4, float * basis_matrix4x4, float * quaternion_xyzw)` | Quaternion normalization with lazy constants, basis-matrix row combination, and aligned/unaligned output paths. |

Validation:

- Dry/apply/final dry summaries: `updated=0 skipped=17 renamed=0 would_rename=0 signature_updated=10 comment_only_updated=7 missing=0 bad=0`; `updated=17 skipped=0 renamed=0 would_rename=0 signature_updated=10 comment_only_updated=7 missing=0 bad=0`; `updated=0 skipped=17 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`.
- Post exports verified `17` metadata rows, `17` tag rows, `33` xref rows, `1581` instruction rows, `4505` wide instruction rows, and `17` decompile rows, including the stack-locked anchor `0x005a0f50 CFastVB__EvaluateCubicBasisVec3`.
- Queue refresh passed: `6098` total, `4214` commented, `1884` commentless, `1216` exact-undefined signatures, `143` `param_N` signatures, strict clean-signature proxy `4157/6098 = 68.17%`.
- Current raw commentless head remains `0x0042f220 CSPtrSet__Clear`; current high-signal head is `0x005a298f CFastVB__ConvertHalfToFloatArray_SIMD`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260522-025058_post_wave718_cfastvb_scalar_transform_core_verified`, `19` files, `166267783` bytes, `DiffCount=0`.

Scope boundary: this is static saved-Ghidra metadata/decompile/instruction/xref evidence only. Exact dispatch-table slot schema, vector/matrix storage contract, stack-locked cubic helper ABI, source identity, runtime math correctness, BEA patching, and rebuild parity remain deferred.
