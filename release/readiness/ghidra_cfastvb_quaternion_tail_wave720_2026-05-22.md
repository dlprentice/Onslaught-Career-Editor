# Ghidra CFastVB Quaternion Tail Wave720 Readiness Note

Status: passed
Date: 2026-05-22

Wave720 CFastVB quaternion tail saved ten adjacent CFastVB vector/quaternion rows from `0x005a38c0 CFastVB__DispatchOp_TransformVec4ArrayByMatrix4` through `0x005a519e CFastVB__DispatchOp_BlendQuaternionSplineSegment_005a519e` with the `cfastvb-quaternion-tail-wave720` and `wave720-readback-verified` tags.

The pass hardened four visible signatures/parameter names and left six stack-locked helpers comment/tag-only:

| Address | Saved state | Evidence |
| --- | --- | --- |
| `0x005a38c0` | `int CFastVB__DispatchOp_TransformVec4ArrayByMatrix4(void)` | Comment/tag-only; stack-locked decompile shows strided Vec4 array output/input, matrix4x4 pointer, element count, four transformed output lanes per element, and return of the original output pointer. |
| `0x005a3980` | `int CFastVB__DispatchOp_TransformVec4ArrayByMatrix4_Alt_005a3980(void)` | Comment/tag-only alternate Vec4-array-by-matrix4 dispatch with the same strided output/input/matrix/count shape as `0x005a38c0`. |
| `0x005a40c0` | `int CFastVB__DispatchOp_TransformVec3ArrayByMatrix4_WithTranslation_005a40c0(void)` | Comment/tag-only; strided Vec3 source lanes are transformed through matrix rows plus translation terms into four output lanes. |
| `0x005a47f2` | `void __stdcall CFastVB__DispatchOp_ExtractAxisAndOptionalAngle(float * quaternion_xyzw, float * out_axis_vec3_or_null, float * out_angle_or_null)` | Axis/angle extraction dispatch; copies first three quaternion lanes to the optional axis output and optionally stores a fast-acos-derived angle scalar. |
| `0x005a4d2c` | `void __stdcall CFastVB__DispatchOp_BuildQuaternionFromAxisAngleVector_005a4d2c(float * out_quaternion_xyzw, float * axis_vec3, float angle_radians)` | Normalizes the axis vector through `CFastVB__DispatchOp_NormalizeVec3_Packed_005a9a5f`, scales angle input, calls the fast trig pair helper, and writes four quaternion lanes. |
| `0x005a4d98` | `void __stdcall CFastVB__DispatchOp_InterpolateQuaternionPairCore_005a4d98(float * out_quaternion_xyzw, float * from_quaternion_xyzw, float * to_quaternion_xyzw, float blend_ratio)` | Quaternion pair interpolation core with dot product, sign/short-path selection, reciprocal/trig angular branch, and blended output lanes. |
| `0x005a4ecf` | `int CFastVB__DispatchOp_BlendQuaternionTriple_005a4ecf(void)` | Comment/tag-only; stack-locked triple-blend helper interpolates one base quaternion toward two controls and then blends the intermediate quaternions. |
| `0x005a4f5c` | `int CFastVB__DispatchOp_BlendQuaternionControlPair_005a4f5c(void)` | Comment/tag-only; stack-locked control-pair helper interpolates two pairs and derives a smoothstep-like final blend ratio from `t` and `t*t`. |
| `0x005a5052` | `void __stdcall CFastVB__DispatchOp_NormalizeQuaternionWithAcosFallback_005a5052(float * out_quaternion_xyzw, float * input_quaternion_xyzw)` | Quaternion normalization/angle fallback dispatch with fast acos/sin paths, reciprocal refinement, scalar-lane masking, and output quaternion write. |
| `0x005a519e` | `int CFastVB__DispatchOp_BlendQuaternionSplineSegment_005a519e(void)` | Comment/tag-only large spline-segment helper; aligns quaternion signs by distance tests, normalizes/fallbacks through fast acos/sin paths, and writes two quaternion outputs. |

Validation:

- Dry/apply/final dry summaries: `updated=0 skipped=10 renamed=0 would_rename=0 signature_updated=4 comment_only_updated=6 missing=0 bad=0`; `updated=10 skipped=0 renamed=0 would_rename=0 signature_updated=4 comment_only_updated=6 missing=0 bad=0`; `updated=0 skipped=10 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`.
- Post exports verified `10` metadata rows, `10` tag rows, `16` xref rows, `1130` instruction rows, `3530` wide instruction rows, and `10` decompile rows.
- Queue refresh passed: `6098` total, `4236` commented, `1862` commentless, `1216` exact-undefined signatures, `127` `param_N` signatures, strict clean-signature proxy `4179/6098 = 68.53%`.
- Current raw commentless head remains `0x0042f220 CSPtrSet__Clear`; current high-signal head is `0x005a62bf CFastVB__DispatchOp_InitIdentityMatrix4x4_005a62bf`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260522-035533_post_wave720_cfastvb_quaternion_tail_verified`, `19` files, `166431623` bytes, `DiffCount=0`.

Scope boundary: this is static saved-Ghidra metadata/decompile/instruction/xref evidence only. Exact dispatch-table slot schema, vector/quaternion storage contract, source identity, runtime math correctness, BEA patching, and rebuild parity remain deferred.

Probe anchors: `Wave720 CFastVB quaternion tail`, `cfastvb-quaternion-tail-wave720`, `0x005a38c0 CFastVB__DispatchOp_TransformVec4ArrayByMatrix4`, `0x005a47f2 CFastVB__DispatchOp_ExtractAxisAndOptionalAngle`, `0x005a4d98 CFastVB__DispatchOp_InterpolateQuaternionPairCore_005a4d98`, `0x005a5052 CFastVB__DispatchOp_NormalizeQuaternionWithAcosFallback_005a5052`, `0x005a519e CFastVB__DispatchOp_BlendQuaternionSplineSegment_005a519e`, `0x0042f220 CSPtrSet__Clear`, `0x005a62bf CFastVB__DispatchOp_InitIdentityMatrix4x4_005a62bf`, `[maintainer-local-ghidra-backup-root]\BEA_20260522-035533_post_wave720_cfastvb_quaternion_tail_verified`.
