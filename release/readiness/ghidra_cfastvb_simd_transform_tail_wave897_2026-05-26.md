# Ghidra CFastVB SIMD Transform Tail Wave897 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-26
Scope: `cfastvb-simd-transform-tail-wave897`

Wave897 CFastVB SIMD transform tail saved comments/tags for nine raw commentless CFastVB SIMD transform and half-float conversion rows from `0x005a09f8 CFastVB__ConvertHalfToFloat8_SIMDKernel` through `0x005a289e CFastVB__ConvertHalfToFloat8_CheckSpecialCasesSIMD`. The pass preserved existing names and signature displays, made no renames, no function-boundary changes, and no executable-byte changes.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x005a09f8 CFastVB__ConvertHalfToFloat8_SIMDKernel` | Called by `0x005a0b22 CFastVB__ConvertHalfToFloatArray_SSE` at `0x005a0b53`; instruction evidence shows packed compare masks and `MULPS` scaling, while decompile remains hidden-register collapsed. |
| `0x005a1c55 CFastVB__DispatchOp_TransformVec4Batch_Alt_005a1c55` | DATA xref `0x00598365` from `CFastVB__InitDispatchTableVariant_0059822c`; uses `CFastVB__BroadcastMatrix4x4ToSIMDLanes` and scalar tail fallback `CFastVB__DispatchOp_TransformVec4ByMatrix4_005a3200`. |
| `0x005a1fe9 CFastVB__DispatchOp_TransformProjectVec4Batch_Alt_005a1fe9` | DATA xref `0x00598351`; projected Vec4 batch path with `RCPPS` reciprocal refinement and fallback thunk `CFastVB__DispatchIndirect_00656f54`. |
| `0x005a225f CFastVB__DispatchOp_TransformVec4Batch_Perspective_Alt_005a225f` | DATA xrefs `0x0059823e`, `0x00598383`, and `0x00598389`; perspective transform batch with scalar tail fallback `CFastVB__DispatchOp_TransformVec2ByMatrix4`. |
| `0x005a266d CFastVB__TransformProjectVec3ByMatrix4_Batch4` | DATA xref `0x0059836f`; processes four Vec3 inputs per loop, refines projected-W reciprocals, and falls back through `CFastVB__DispatchOp_TransformProjectVec3ByMatrix4_005a1786`. |
| `0x005a289e CFastVB__ConvertHalfToFloat8_CheckSpecialCasesSIMD` | Called by `0x005a298f CFastVB__ConvertHalfToFloatArray_SIMD` at `0x005a29c0`; checks eight half-float lanes against masks rooted at `0x0065e750`. |

Read-back evidence:

- `ApplyCFastVBSimdTransformTailWave897.java dry`: `updated=0 skipped=9 renamed=0 would_rename=0 missing=0 bad=0`
- `ApplyCFastVBSimdTransformTailWave897.java apply`: `updated=9 skipped=0 renamed=0 would_rename=0 missing=0 bad=0`
- `ApplyCFastVBSimdTransformTailWave897.java final dry`: `updated=0 skipped=9 renamed=0 would_rename=0 missing=0 bad=0`
- Post exports: 9 metadata rows, 9 tag rows, 11 xref rows, 1077 instruction rows, 9 decompile rows, and 10 context metadata rows.
- Queue after Wave897: 6113 total, 6097 commented, 16 commentless, 0 exact-undefined signatures, 0 `param_N`, strict/comment-backed proxy `6097/6113 = 99.74%`.
- Next raw commentless row: `0x005a9f44 CFastVB__DispatchOp_ComposeTransformAndProjectVec3_005a9f44`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260526-074111_post_wave897_cfastvb_simd_transform_tail_verified`, 19 files, 173214599 bytes, `DiffCount=0`.

What this proves:

- The nine target function rows exist in the saved Ghidra project.
- The saved names/signature displays are unchanged and clean.
- The saved comments and tags include `cfastvb-simd-transform-tail-wave897` and `wave897-readback-verified`.
- The observed SIMD transform and half-float bodies are static retail Ghidra evidence tied to xrefs, instruction exports, decompiles, and queue read-back.

What remains unproven:

- Exact dispatch-table slot schema and vector/matrix/stride layouts.
- Exact hidden XMM/MMX ABI and half-float special-case policy.
- Runtime math correctness or renderer behavior.
- BEA patching behavior.
- Rebuild parity.
