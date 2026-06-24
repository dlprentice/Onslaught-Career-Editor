# Ghidra CFastVB Packed Vec2 Quaternion Tail Wave722 Readiness Note

Status: passed
Date: 2026-05-22

Wave722 CFastVB packed Vec2/quaternion tail saved five adjacent CFastVB dispatch rows from `0x005aa480 CFastVB__DispatchOp_ConvertPackedS16ToFloatPairBatch_005aa480` through `0x005ab00b CFastVB__DispatchOp_NormalizeQuaternionPacked_005ab00b` with the `cfastvb-packed-vec2-quaternion-tail-wave722` and `wave722-readback-verified` tags.

The pass hardened five visible signatures/parameter names:

| Address | Saved state | Evidence |
| --- | --- | --- |
| `0x005aa480` | `int __stdcall CFastVB__DispatchOp_ConvertPackedS16ToFloatPairBatch_005aa480(float * out_float_pairs, short * input_packed_s16_pairs, uint pair_count)` | Packed 16-bit pair conversion dispatch referenced by `CFastVB__InitDispatchOpsFromFeatureFlags`; loops over four-pair batches, falls back to `CFastVB__ConvertFloat16BufferToFloat32_00575a6b` for small/tail counts, writes float pairs, and returns the output pointer as an int-compatible value. |
| `0x005aa73b` | `int __stdcall CFastVB__DispatchOp_TransformVec2ByMatrix4_WithTranslation_005aa73b(float * out_vec4, float * input_vec2, float * matrix4x4)` | Vec2-by-matrix4 dispatch with translation; broadcasts x/y lanes, applies two matrix row pairs plus translation terms, and writes four output floats. |
| `0x005aa790` | `int __stdcall CFastVB__DispatchOp_TransformVec2ByMatrix4_NoTranslation_005aa790(float * out_vec2, float * input_vec2, float * matrix4x4)` | Vec2-by-matrix4 dispatch without translation; broadcasts x/y lanes, multiplies by matrix rows without translation terms, and writes two output floats. |
| `0x005aa7c9` | `int __stdcall CFastVB__DispatchOp_TransformProjectVec2ByMatrix4_005aa7c9(float * out_vec2, float * input_vec2, float * matrix4x4)` | Vec2 transform/project dispatch; applies matrix rows plus translation, derives a reciprocal from projected w, scales the output pair, and writes two output floats. |
| `0x005ab00b` | `void __stdcall CFastVB__DispatchOp_NormalizeQuaternionPacked_005ab00b(float * out_quaternion_xyzw, float * input_quaternion_xyzw)` | Packed quaternion normalization dispatch; accumulates squared xy and masked zw lanes, applies reciprocal-square-root refinement with a small-length compare mask, and writes four output quaternion floats. |

Validation:

- Dry/apply/final dry summaries: `updated=0 skipped=5 renamed=0 would_rename=0 signature_updated=5 comment_only_updated=0 missing=0 bad=0`; `updated=5 skipped=0 renamed=0 would_rename=0 signature_updated=5 comment_only_updated=0 missing=0 bad=0`; `updated=0 skipped=5 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`.
- Post exports verified `5` metadata rows, `5` tag rows, `10` xref rows, `1705` instruction rows, `2405` wide instruction rows, and `5` decompile rows.
- Queue refresh passed: `6098` total, `4253` commented, `1845` commentless, `1216` exact-undefined signatures, `113` `param_N` signatures, comment-backed proxy `4253/6098 = 69.75%`, strict clean-signature proxy `4195/6098 = 68.79%`.
- Current raw commentless head remains `0x0042f220 CSPtrSet__Clear`; current high-signal head is `0x005ab0ed CDXTexture__EvalNodeOutputSizeUnits`.
- Verified backup: `G:\GhidraBackups\BEA_20260522-050258_post_wave722_cfastvb_packed_vec2_quaternion_tail_verified`, `19` files, `166497159` bytes, `DiffCount=0`.

Scope boundary: this is static saved-Ghidra metadata/decompile/instruction/xref evidence only. Exact dispatch-table slot schema, packed vector/matrix/quaternion storage contract, source identity, runtime math correctness, BEA patching, and rebuild parity remain deferred.

Probe anchors: `Wave722 CFastVB packed Vec2/quaternion tail`, `cfastvb-packed-vec2-quaternion-tail-wave722`, `0x005aa480 CFastVB__DispatchOp_ConvertPackedS16ToFloatPairBatch_005aa480`, `0x005aa73b CFastVB__DispatchOp_TransformVec2ByMatrix4_WithTranslation_005aa73b`, `0x005aa7c9 CFastVB__DispatchOp_TransformProjectVec2ByMatrix4_005aa7c9`, `0x005ab00b CFastVB__DispatchOp_NormalizeQuaternionPacked_005ab00b`, `0x0042f220 CSPtrSet__Clear`, `0x005ab0ed CDXTexture__EvalNodeOutputSizeUnits`, `G:\GhidraBackups\BEA_20260522-050258_post_wave722_cfastvb_packed_vec2_quaternion_tail_verified`.
