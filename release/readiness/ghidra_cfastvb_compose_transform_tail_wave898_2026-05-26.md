# Ghidra CFastVB Compose Transform Tail Wave898 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-26
Scope: `cfastvb-compose-transform-tail-wave898`

Wave898 CFastVB compose transform tail saved comments/tags for three raw commentless CFastVB compose/project dispatch rows from `0x005a9f44 CFastVB__DispatchOp_ComposeTransformAndProjectVec3_005a9f44` through `0x005aa2f2 CFastVB__DispatchOp_ComposeTransformFromOptionalInputs_SIMD`. The pass preserved existing names and signature displays, made no renames, no function-boundary changes, and no executable-byte changes.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x005a9f44 CFastVB__DispatchOp_ComposeTransformAndProjectVec3_005a9f44` | DATA xref `0x005984ea` from `CFastVB__InitDispatchOpsFromFeatureFlags`; builds a 3-bit nullable matrix selector, uses jump table `0x005aa0ac`, composes through `CFastVB__DispatchOp_MultiplyMatrix4x4_Packed_005a9d78`, projects through `CFastVB__DispatchOp_TransformProjectVec3ByMatrix4_005a9ced`, and optionally remaps projected output through `EBP+0x10`. |
| `0x005aa0cc CFastVB__DispatchOp_ComposeTransformFromOptionalInputs_Scalar` | DATA xref `0x005984f1`; scalar optional-input path with jump table `0x005aa2d2`, matrix composition through `CFastVB__DispatchOp_MultiplyMatrix4x4_Packed_005a9d78`, inverse helper `CFastVB__DispatchOp_InvertMatrix4x4_Variant_005a9637`, optional vector remap, and projected Vec3 transform. |
| `0x005aa2f2 CFastVB__DispatchOp_ComposeTransformFromOptionalInputs_SIMD` | DATA xref `0x00598684`; SIMD optional-input path with jump table `0x005aa424`, identity initializer `CFastVB__DispatchOp_InitIdentityMatrix4x4_005a62bf`, packed matrix multiply, inverse helper `CFastVB__DispatchOp_InvertMatrix4x4_WithDeterminant_005a8f5d`, optional vector remap, and projected Vec3 transform. |

Read-back evidence:

- `ApplyCFastVBComposeTransformTailWave898.java dry`: `updated=0 skipped=3 renamed=0 would_rename=0 missing=0 bad=0`
- `ApplyCFastVBComposeTransformTailWave898.java apply`: `updated=3 skipped=0 renamed=0 would_rename=0 missing=0 bad=0`
- `ApplyCFastVBComposeTransformTailWave898.java final dry`: `updated=0 skipped=3 renamed=0 would_rename=0 missing=0 bad=0`
- Post exports: 3 metadata rows, 3 tag rows, 3 xref rows, 444 instruction rows, 3 decompile rows, and 8 context metadata rows.
- Queue after Wave898: 6113 total, 6100 commented, 13 commentless, 0 exact-undefined signatures, 0 `param_N`, strict/comment-backed proxy `6100/6113 = 99.79%`.
- Next raw commentless row: `0x005b7770 CDXTexture__ValidateJpegFrameAndComputeMcuLayout`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260526-080711_post_wave898_cfastvb_compose_transform_tail_verified`, 19 files, 173214599 bytes, `DiffCount=0`.

What this proves:

- The three target function rows exist in the saved Ghidra project.
- The saved names/signature displays are unchanged and clean.
- The saved comments and tags include `cfastvb-compose-transform-tail-wave898` and `wave898-readback-verified`.
- The observed CFastVB compose/project dispatch bodies are static retail Ghidra evidence tied to xrefs, instruction exports, decompiles, helper metadata, and queue read-back.

What remains unproven:

- Exact dispatch-table slot schema and optional-input layouts.
- Exact projected-output/vector remap semantics.
- SIMD-vs-scalar runtime selection policy beyond the observed registration xrefs.
- Runtime math correctness or renderer behavior.
- BEA patching behavior.
- Rebuild parity.
