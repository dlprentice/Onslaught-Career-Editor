# Ghidra Texture Dispatch/Interpolation Tail Wave887 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-26
Scope: `texture-dispatch-interpolation-tail-wave887`

Wave887 texture dispatch/interpolation tail saved comments/tags for 30 adjacent texture/math dispatch rows from `0x005759b6 CFastVB__DispatchIndirect_00657014` through `0x00576178 CTexture__DispatchPtr0065702c_NoInit`. Existing names and signature displays were preserved because Ghidra still reports locked/hidden parameter storage for these helpers. The pass made no renames, no function-boundary changes, no executable-byte changes, did not launch BEA, and did not touch the installed Steam game.

Representative anchors:

| Address / area | Evidence |
| --- | --- |
| `0x005759b6 CFastVB__DispatchIndirect_00657014` / `0x005759c3 CDXTexture__PackTexels_DispatchIndirect_005759c3` | CPU-feature initializer and no-init thunk for dispatch slot `0x00657014`; pack callbacks call the no-init thunk. |
| `0x00575a58 CFastVB__DispatchIndirect_00657018` / `0x00575a65 CDXTexture__UnpackTexels_DispatchIndirect_00575a65` | CPU-feature initializer and no-init thunk for dispatch slot `0x00657018`; unpack callbacks call the no-init thunk. |
| `0x00575b47 Math__InterpolateVec2Cubic` | Stack-locked scalar vec2 cubic/Hermite basis blend over four vec2 inputs, `RET 0x18`. |
| `0x00575dc9 CFastVB__HermiteInterpolateVec3` | Stack-locked scalar vec3 cubic/Hermite basis blend over four vec3 inputs, `RET 0x18`. |
| `0x00575cdd Math__InterpolateVec2ByUV` / `0x00575fa1 Math__InterpolateVec3ByUV` | UV interpolation helpers: base plus U and V direction deltas into output vectors, `RET 0x18`. |
| `0x00575d20` through `0x00575d99` | Dispatch slots `0x00656f30`, `0x00656f54`, `0x00656f44`, and `0x00656f4c`; callers include CFastVB transform batches, axis-angle math/quaternion builders, and texture dither packing. |
| `0x0057600b CVBufTexture__DispatchTextureTransformThunk` | No-init texture-transform thunk for slot `0x00656f34`; callers include `CVBufTexture__RenderDynamicUnitPass`, vertex-shader constant application, and `CVBufTexture__RenderModePass`. |
| `0x00576161 CFastVB__DispatchIndirectByGlobalTable` | No-init dispatch thunk for slot `0x00656f58`; callers include `CMeshRenderer__RenderMeshCore`, `CTexture__MapNormalizedUvToVolumeCoords`, `CFastVB__InterpolateDualProfileStreams`, and `CFastVB__MapVolumeCoordsToNormalizedUv`. |
| `0x00576167 CTexture__DispatchPtr0065702c_WithInit` / `0x00576178 CTexture__DispatchPtr0065702c_NoInit` | Optional transform-pass dispatch slot `0x0065702c`; callers include `CFastVB__ApplyOptionalTransformPasses_Minimal` and `CFastVB__ApplyOptionalTransformPasses`. |

Read-back evidence:

- `ApplyTextureDispatchInterpolationTailWave887.java dry`: `updated=0 skipped=30 renamed=0 would_rename=0 missing=0 bad=0`
- `ApplyTextureDispatchInterpolationTailWave887.java apply`: `updated=30 skipped=0 renamed=0 would_rename=0 missing=0 bad=0`
- `ApplyTextureDispatchInterpolationTailWave887.java final dry`: `updated=0 skipped=30 renamed=0 would_rename=0 missing=0 bad=0`
- Post exports: 30 metadata rows, 30 tag rows, 72 xref rows, 470 instruction rows, and 30 decompile rows.
- Queue after Wave887: 6113 total, 6008 commented, 105 commentless, 0 exact-undefined signatures, 0 `param_N`, comment-backed/strict proxy `6008/6113 = 98.28%`.
- Next raw commentless row: `0x0057617e CDXTexture__DispatchPtr00656f48_WithInit`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260526-030217_post_wave887_texture_dispatch_interpolation_tail_verified`, 19 files, 172952455 bytes, `DiffCount=0`.

What this proves:

- The 30 target function rows exist in the saved Ghidra project.
- The saved comments and tags include `texture-dispatch-interpolation-tail-wave887` and `wave887-readback-verified`.
- The observed bodies are static retail Ghidra evidence tied to dispatch slot pointers, xrefs, instruction exports, and decompile exports.

What remains unproven:

- Exact dispatch-table slot targets.
- Exact CPU feature policy.
- Exact source-body identity.
- Runtime texture/math/render behavior.
- BEA patching behavior.
- Rebuild parity.
