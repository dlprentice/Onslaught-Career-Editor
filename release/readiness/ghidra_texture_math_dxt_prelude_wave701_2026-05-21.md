# Ghidra Texture Math / DXT Prelude Wave701 Readiness

Date: 2026-05-21

Wave701 texture math / DXT prelude saved twelve adjacent texture math, dispatch-table, RGB565, alpha-block, endpoint-solver, and DXT selector rows with the `texture-math-dxt-prelude-wave701` and `wave701-readback-verified` tags.

Targets:

| Address | Saved signature |
| --- | --- |
| `0x005960c1` | `double __stdcall CDXTexture__FastReciprocalSqrtScalar(uint float_bits)` |
| `0x00596106` | `float * __stdcall CDXTexture__NormalizeVec3Fast(float * normalized_vec3_out, float * input_vec3)` |
| `0x005961d0` | `void __stdcall CDXTexture__MultiplyMatrix4x4_InPlaceSafe(float * matrix4x4_out, float * left_matrix4x4, float * right_matrix4x4)` |
| `0x005962b3` | `void __stdcall CDXTexture__MultiplyMatrix4x4_Safe(float * matrix4x4_out, float * left_matrix4x4, float * right_matrix4x4)` |
| `0x00596341` | `void __stdcall CFastVB__InitMathDispatchTable(void * math_dispatch_table)` |
| `0x00596386` | `void __fastcall CDXTexture__UnpackRgb565ToRgbaFloat(uint rgb565_word)`; output pointer is hidden in EAX |
| `0x005963d2` | `int __fastcall CDXTexture__NormalizeColorBlockByAlpha(void * rgba_float_block16)` |
| `0x00596450` | `int __fastcall CTexture__PremultiplyAlphaBlock16(void * premultiplied_rgba_out)`; source pointer is hidden in EAX |
| `0x00596480` | `uint __fastcall CFastVB__PackClampedRgbToR5G6B5(void * rgb_float_triplet)` |
| `0x00596589` | `void __stdcall CFastVB__SolveScalarEndpointPairFromSamples(float * endpoint_min_out, float * endpoint_max_out, float * scalar_samples16)`; endpoint mode is hidden in EBX |
| `0x005968a4` | `void __stdcall CFastVB__SolveVectorEndpointPairFromSamples(float * endpoint_min_rgb_out, float * endpoint_max_rgb_out, float * rgba_samples16, int endpoint_count)` |
| `0x00596e23` | `int __stdcall CFastVB__QuantizeScalarBlockIndices(void * dxt_color_block_out, float alpha_mode_weight)`; source block pointer is hidden in EAX |

Evidence:

- Dry/apply/final-dry summaries: `updated=0 skipped=12 renamed=0 would_rename=0 signature_updated=12 missing=0 bad=0`, then `updated=12 skipped=0 renamed=0 would_rename=0 signature_updated=12 missing=0 bad=0`, then `updated=0 skipped=12 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`.
- Post exports verified `12` metadata rows, `12` tag rows, `24` xref rows, `1068` instruction rows, and `12` clean decompile rows.
- Queue refresh PASS: `6098` total, `4045` commented, `2053` commentless, `1216` exact-undefined signatures, and `281` `param_N` signatures.
- Strict comment-plus-clean-signature proxy from the refreshed TSV is `3991/6098 = 65.45%`.
- Verified backup: `G:\GhidraBackups\BEA_20260521-172303_post_wave701_texture_math_dxt_prelude_verified`, `19` files, `165251975` bytes, `DiffCount=0`.

Scope boundary:

This is static saved-Ghidra metadata evidence only. Exact lookup-table provenance, numeric error bounds, vector/matrix layout conventions, dispatch-table schema, CPU feature replacement behavior, hidden EAX/EBX helper ABI, RGB565 color-space convention, DXT block schema, alpha-mode semantics, residual diffusion policy, runtime math correctness, runtime texture fidelity, runtime compression quality, BEA patching, and rebuild parity remain unproven.

Next queue head: `0x0059764a CDXTexture__DecodeDxt1ColorBlockToRgba`.

Probe anchors: `Wave701 texture math / DXT prelude`, `texture-math-dxt-prelude-wave701`, `0x005960c1 CDXTexture__FastReciprocalSqrtScalar`, `0x00596e23 CFastVB__QuantizeScalarBlockIndices`, `0x0059764a CDXTexture__DecodeDxt1ColorBlockToRgba`.
