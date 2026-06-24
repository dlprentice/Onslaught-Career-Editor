# Ghidra Math Dispatch Wave660 Readiness Note

Status: complete
Date: 2026-05-21

## Scope

Wave660 math dispatch continuation saved static Ghidra metadata for seventeen math/dispatch rows:

- `0x005776a5 CTexture__DispatchPtr00656fd0_WithInit`
- `0x0057798e CFastVB__BuildAxisAngleQuaternion_Dispatch`
- `0x005779ae CFastVB__BuildAxisAngleQuaternion`
- `0x00577a0a Math__BuildEulerRotationMatrix4x4_Dispatch`
- `0x00577a38 Math__BuildEulerRotationMatrix4x4_Dispatch_Thunk`
- `0x00577a3e Math__BuildEulerRotationMatrix4x4`
- `0x00577e80 Math__InterpolateVec4ByRatio_Dispatch`
- `0x00577ea4 Math__InterpolateVec4ByRatio_Dispatch_Thunk`
- `0x00577eaa Math__InterpolateVec4ByRatio`
- `0x00577f8d Math__BezierBlendVec4_Dispatch`
- `0x00577fb7 Math__BezierBlendVec4`
- `0x0057804e Math__BlendVec4DualWeights`
- `0x00578555 Math__TransformVec2ByMatrix4x4`
- `0x00578643 Math__TransformVec2ByMatrixPerspective`
- `0x00578758 Math__TransformVec2ByMatrixLinear`
- `0x005787e8 Math__NormalizeVec3`
- `0x00578885 Math__TransformVec3ByMatrixPerspective`

The pass created two missing function boundaries at `0x00577a3e` and `0x00577eaa`, renamed four stale dispatch rows, retained `0x005776a5` under its existing CTexture dispatch-slot label with a deferred argument/storage contract, and made no executable-byte changes.

## Evidence

- Ghidra dry run: `updated=0 skipped=17 created=0 would_create=2 body_set=0 would_set_body=2 renamed=0 would_rename=4 signature_updated=15 missing=0 bad=0`.
- Ghidra apply: `updated=17 skipped=0 created=2 would_create=0 body_set=2 would_set_body=0 renamed=4 would_rename=0 signature_updated=13 missing=0 bad=0`, with read-back `OK`/`OKCREATE` rows.
- Final Ghidra dry run: `updated=0 skipped=17 created=0 would_create=0 body_set=0 would_set_body=0 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`.
- Post exports verified `17` metadata rows, `17` tag rows, `31` xref rows, `833` instruction rows, `17` clean decompile rows, and two `71`-row dispatch-table snapshots.
- Queue after Wave660: `6098` total functions, `3619` commented, `2479` commentless, `1217` exact-undefined signatures, `698` `param_N` signatures, comment-backed proxy `3619/6098 = 59.35%`, strict clean-signature proxy `3569/6098 = 58.53%`.
- Verified backup: `G:\GhidraBackups\BEA_20260520-230154_post_wave660_math_dispatch_verified`, `19` files, `163318663` bytes, `DiffCount=0`.
- Next queue head: `0x00579184 CFastVB__NormalizeQuaternionCopy`.

## Boundaries

This is static retail Ghidra metadata evidence only. Exact vector/matrix storage contract, CPU feature replacement behavior, runtime math correctness, BEA patching, and rebuild parity remain deferred. The `math-dispatch-wave660` tag marks the saved static evidence set and does not certify runtime behavior.
