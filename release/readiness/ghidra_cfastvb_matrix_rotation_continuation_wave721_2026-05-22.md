# Ghidra CFastVB Matrix/Rotation Continuation Wave721 Readiness Note

Status: passed
Date: 2026-05-22

Wave721 CFastVB matrix/rotation continuation saved twelve adjacent CFastVB matrix, rotation, inverse, normalize, transform/project, and multiply rows from `0x005a62bf CFastVB__DispatchOp_InitIdentityMatrix4x4_005a62bf` through `0x005a9f3f CFastVB__DispatchOp_TransformProjectVec3ByMatrix4_Alt_005a9f3f` with the `cfastvb-matrix-rotation-continuation-wave721` and `wave721-readback-verified` tags.

The pass hardened nine visible signatures/parameter names and left three stack-locked or packed-ABI helpers comment/tag-only:

| Address | Saved state | Evidence |
| --- | --- | --- |
| `0x005a62bf` | `void __cdecl CFastVB__DispatchOp_InitIdentityMatrix4x4_005a62bf(float * out_matrix4x4)` | Identity matrix4x4 initializer; writes one/zero lanes across a sixteen-float matrix and exits through `FastExitMediaState`. |
| `0x005a647f` | `int CFastVB__DispatchOp_ComposeTransformFromOptionalInputs_Core_005a647f(void)` | Comment/tag-only; large optional-transform composition core with output matrix, optional translation, quaternion/rotation, scale/basis, inverse pivot, and additive-offset-style inputs. |
| `0x005a7617` | `void __stdcall CFastVB__DispatchOp_BuildRotationMatrixFromEulerAngles(void * param_1, int param_2, int param_3)` | Comment/tag-only Euler-angle-to-matrix4 dispatch; custom stack-frame code scales packed angle inputs by the `0x005ef190` constant and calls the fast trig pair helper three times. |
| `0x005a7cf0` | `void __stdcall CFastVB__DispatchOp_BuildRotationMatrixFromAxisAngleVector(float * out_matrix4x4, float * axis_angle_vec3)` | Axis-angle-vector-to-matrix4 dispatch; normalizes through `CFastVB__DispatchOp_NormalizeVec3_Packed_005a9a5f`, calls the fast trig pair helper, and writes a sixteen-float rotation matrix. |
| `0x005a7e09` | `int CFastVB__DispatchOp_ComposeMatrixFromOptionalTransforms(void)` | Comment/tag-only optional transform matrix composition dispatch with nullable identity/scale/rotation/translation inputs, optional inverse-pivot, and additive-offset adjustments. |
| `0x005a8f5d` | `void __stdcall CFastVB__DispatchOp_InvertMatrix4x4_WithDeterminant_005a8f5d(float * out_inverse_matrix4x4, float * out_determinant_or_null, float * input_matrix4x4)` | Matrix4x4 inverse dispatch; computes cofactors and determinant, writes optional determinant output, skips inverse writes for zero determinant, and otherwise writes reciprocal-determinant-scaled inverse rows. |
| `0x005a9637` | `int __stdcall CFastVB__DispatchOp_InvertMatrix4x4_Variant_005a9637(float * out_inverse_matrix4x4, float * out_determinant_or_null, float * input_matrix4x4)` | Scalar matrix4x4 inverse variant; returns zero for zero determinant or the output pointer as an int-compatible value after writing the inverse matrix. |
| `0x005a99f8` | `int __stdcall CFastVB__DispatchOp_TransformVec3ByMatrix4_NoTranslation_005a99f8(float * out_vec3, float * input_vec3, float * matrix4x4)` | Vec3-by-matrix4 helper that omits translation terms, writes three output floats, and returns the output pointer as an int-compatible value. |
| `0x005a9a5f` | `void __stdcall CFastVB__DispatchOp_NormalizeVec3_Packed_005a9a5f(float * out_vec3, float * input_vec3)` | Packed Vec3 normalization helper with reciprocal-square-root refinement and a small-length mask. |
| `0x005a9ced` | `int __stdcall CFastVB__DispatchOp_TransformProjectVec3ByMatrix4_005a9ced(float * out_vec3, float * input_vec3, float * matrix4x4)` | Vec3 transform/project helper with matrix rows plus translation, reciprocal-w scaling, and three output floats. |
| `0x005a9d78` | `int __stdcall CFastVB__DispatchOp_MultiplyMatrix4x4_Packed_005a9d78(float * out_matrix4x4, float * left_matrix4x4, float * right_matrix4x4)` | Packed matrix4x4 multiply helper; reads four packed left rows, multiplies across right matrix columns, and writes sixteen output floats. |
| `0x005a9f3f` | `int __stdcall CFastVB__DispatchOp_TransformProjectVec3ByMatrix4_Alt_005a9f3f(float * out_vec3, float * input_vec3, float * matrix4x4)` | Alternate Vec3 transform/project dispatch with translation terms, reciprocal-w scaling, three output floats, and an int-compatible output-pointer return. |

Validation:

- Dry/apply/final dry summaries: `updated=0 skipped=12 renamed=0 would_rename=0 signature_updated=9 comment_only_updated=3 missing=0 bad=0`; `updated=12 skipped=0 renamed=0 would_rename=0 signature_updated=8 comment_only_updated=3 missing=0 bad=0`; `updated=0 skipped=12 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`. The apply counter reported `signature_updated=8` because one visible pointer-type hardening was already datatype-equivalent at apply time; post metadata verifies nine cleaned visible signatures/parameter-name sets.
- Post exports verified `12` metadata rows, `12` tag rows, `38` xref rows, `1356` instruction rows, `3420` wide instruction rows, and `12` decompile rows.
- Queue refresh passed: `6098` total, `4248` commented, `1850` commentless, `1216` exact-undefined signatures, `118` `param_N` signatures, comment-backed proxy `4248/6098 = 69.66%`, strict clean-signature proxy `4190/6098 = 68.71%`.
- Current raw commentless head remains `0x0042f220 CSPtrSet__Clear`; current high-signal head is `0x005aa480 CFastVB__DispatchOp_ConvertPackedS16ToFloatPairBatch_005aa480`.
- Verified backup: `G:\GhidraBackups\BEA_20260522-043029_post_wave721_cfastvb_matrix_rotation_continuation_verified`, `19` files, `166464391` bytes, `DiffCount=0`.

Scope boundary: this is static saved-Ghidra metadata/decompile/instruction/xref evidence only. Exact dispatch-table slot schema, packed vector/matrix storage contract, source identity, runtime math correctness, BEA patching, and rebuild parity remain deferred.

Probe anchors: `Wave721 CFastVB matrix/rotation continuation`, `cfastvb-matrix-rotation-continuation-wave721`, `0x005a62bf CFastVB__DispatchOp_InitIdentityMatrix4x4_005a62bf`, `0x005a7617 CFastVB__DispatchOp_BuildRotationMatrixFromEulerAngles`, `0x005a7cf0 CFastVB__DispatchOp_BuildRotationMatrixFromAxisAngleVector`, `0x005a8f5d CFastVB__DispatchOp_InvertMatrix4x4_WithDeterminant_005a8f5d`, `0x005a9d78 CFastVB__DispatchOp_MultiplyMatrix4x4_Packed_005a9d78`, `0x0042f220 CSPtrSet__Clear`, `0x005aa480 CFastVB__DispatchOp_ConvertPackedS16ToFloatPairBatch_005aa480`, `G:\GhidraBackups\BEA_20260522-043029_post_wave721_cfastvb_matrix_rotation_continuation_verified`.
