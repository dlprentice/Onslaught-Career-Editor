# Ghidra Texture Transform Dispatch Tail Wave888 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-26
Scope: `texture-transform-dispatch-tail-wave888`

Wave888 texture transform dispatch tail saved comments/tags for forty-four adjacent texture, vertex-shader, CFastVB, and Math dispatch/transform rows from `0x0057617e CDXTexture__DispatchPtr00656f48_WithInit` through `0x00579273 CTexture__BuildTransformMatrixWithOptionalOffsets`. Existing names and signature displays were preserved because Ghidra still reports locked/hidden parameter storage. The pass made no renames, no function-boundary changes, no executable-byte changes, and did not launch BEA.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x0057617e CDXTexture__DispatchPtr00656f48_WithInit` | CPU-feature initializer thunk for slot `0x00656f48`; calls `CFastVB__InitDispatchTableByCpuFeature(1)` and tail-jumps through the slot. |
| `0x00576286 CDXTexture__DispatchPtr00656f68_WithInit` | CPU-feature initializer thunk with DATA xref `0x00656f68`; companion no-init thunk `0x00576297`. |
| `0x00576404 Math__InterpolateVec4Cubic` | Stack-locked scalar vec4 cubic interpolation body with DATA xref `0x00657120` and observed `RET 0x18`. |
| `0x00576621 Math__InterpolateVec4ByUV` | Stack-locked scalar vec4 UV interpolation body with DATA xref `0x00657128` and observed `RET 0x18`. |
| `0x005768fe CFastVB__DispatchIndirect_00656f3c` | Widely reused no-init transform/composition dispatch thunk for slot `0x00656f3c`; xrefs include vertex-shader, matrix-builder, UV/volume mapping, and optional transform-pass paths. |
| `0x0057770b CFastVB__BuildTransformMatrixWithOffsets` | Initializes matrix state, composes optional quaternion rotation, applies optional pivot subtraction/restoration, and adds optional translation; DATA xref `0x006570f4`; observed `RET 0x14`. |
| `0x005785c0 Math__TransformVec2ArrayToVec4Array` | Strided vec2 array to vec4 matrix transform; DATA xref `0x0065713c`; observed `RET 0x18`. |
| `0x005786c0 Math__TransformVec2ArrayByMatrixPerspective` | Strided vec2 perspective transform using `Math__IsFloatDiffOutsideTolerance`; DATA xref `0x00657140`; observed `RET 0x18`. |
| `0x00578a20 CTexture__MapNormalizedUvToVolumeCoords` | Optional transform flags plus normalized UV/Z to descriptor-bounds coordinate mapping; DATA xref `0x00657088`; observed `RET 0x18`. |
| `0x00578dad CFastVB__MapVolumeCoordsToNormalizedUv` | Inverse descriptor-bounds coordinate mapping back to normalized UV/Z; DATA xref `0x0065708c`; observed `RET 0x18`. |
| `0x00578f53 CFastVB__ApplyOptionalTransformPasses` | Full optional transform-pass helper; data xref `0x0065715c`; observed `RET 0x24`. |
| `0x00579273 CTexture__BuildTransformMatrixWithOptionalOffsets` | Texture transform matrix builder with optional quaternion rotations, pivot offsets, and translation offsets; DATA xref `0x006570ec`; observed `RET 0x1c`. |

Read-back evidence:

- `ApplyTextureTransformDispatchTailWave888.java dry`: `updated=0 skipped=44 renamed=0 would_rename=0 missing=0 bad=0`
- `ApplyTextureTransformDispatchTailWave888.java apply`: `updated=44 skipped=0 renamed=0 would_rename=0 missing=0 bad=0`
- `ApplyTextureTransformDispatchTailWave888.java final dry`: `updated=0 skipped=44 renamed=0 would_rename=0 missing=0 bad=0`
- Post exports: 44 metadata rows, 44 tag rows, 131 xref rows, 1581 instruction rows, and 44 decompile rows.
- Queue after Wave888: 6113 total, 6052 commented, 61 commentless, 0 exact-undefined signatures, 0 `param_N`, comment-backed and strict clean-signature proxy `6052/6113 = 99.00%`.
- Next raw commentless row: `0x00579a9a CVertexShader__CompileScriptWithDirectiveParser`.
- Commentless high-signal, signature, and name-confidence queues remain empty.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260526-033426_post_wave888_texture_transform_dispatch_tail_verified`, 19 files, 173116295 bytes, `DiffCount=0`.

What this proves:

- The 44 target function rows exist in the saved Ghidra project.
- The saved comments and tags include `texture-transform-dispatch-tail-wave888` and `wave888-readback-verified`.
- Existing names and signature displays were preserved after read-back checks.
- The observed dispatch thunks, interpolation helpers, array transform helpers, UV/volume mappers, and optional transform matrix helpers are static retail Ghidra evidence tied to xref, instruction, and decompile exports.

What remains unproven:

- Exact dispatch-table slot targets.
- Exact CPU feature policy.
- Exact descriptor, matrix, vertex-shader, and texture-transform layouts.
- Exact source-body identity.
- Runtime texture/math/render behavior.
- BEA patching behavior.
- Rebuild parity.
