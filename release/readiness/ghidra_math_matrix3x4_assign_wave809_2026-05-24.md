# Ghidra Math Matrix3x4 Assign Wave809 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-24
Scope: `math-matrix3x4-assign-wave809`

Wave809 math-matrix3x4 assign saved a one-row owner-neutral signature/comment/tag hardening for `0x004901e0 MathMatrix3x4__AssignFromEightScalars`. The pass retained the Wave126 name, made no renames, made no function-boundary changes, and made no executable-byte changes.

| Address | Saved state | Evidence |
| --- | --- | --- |
| `0x004901e0 MathMatrix3x4__AssignFromEightScalars` | `void __thiscall MathMatrix3x4__AssignFromEightScalars(void * this, float scalar_00, float scalar_14, float scalar_18, float scalar_1c, float scalar_20, float scalar_24, float scalar_28, float scalar_2c)` | Instruction evidence reads eight stack dwords/floats, writes `scalar_00` to `ECX+0x00`, writes `scalar_14` through `scalar_2c` to `ECX+0x14` through `ECX+0x2c`, and exits with `RET 0x20`. Sixteen observed callsites in `CEngine__SetupLights`, `CDXFrontEnd__SetupRenderMatricesAndProjection`, `CFEPBEConfig__Render`, `CRTTree__VFuncSlot02_BuildRenderOutputs`, `CFEPMultiplayerStart__Render`, and adjacent unmapped frontend callsites ignore `EAX` immediately after the call, supporting a `void` return. |

Read-back evidence:

- `ApplyMathMatrix3x4AssignWave809.java dry`: `updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0`
- `ApplyMathMatrix3x4AssignWave809.java apply`: `updated=1 skipped=0 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0`
- `ApplyMathMatrix3x4AssignWave809.java final dry`: `updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 1 metadata row, 1 tag row, 16 xref rows, 125 instruction rows, 1 decompile row, 432 post-callsite instruction rows, and 5 post-caller decompile rows.
- Queue after Wave809: 6098 total, 5584 commented, 514 commentless, 0 exact-undefined signatures, 0 `param_N`, comment-backed proxy `5584/6098 = 91.57%`, strict clean-signature proxy `5584/6098 = 91.57%`.
- Next raw commentless row: `0x0049bd50 CMCMech__UpdateBoneHierarchyRecursive`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260524-120255_post_wave809_math_matrix3x4_assign_verified`, 19 files, 171314055 bytes, `DiffCount=0`.

What this proves:

- The saved Ghidra function row exists at `0x004901e0`.
- The saved name remains `MathMatrix3x4__AssignFromEightScalars`.
- The saved signature is the `void __thiscall` eight-scalar form above.
- The saved comment and tags include `math-matrix3x4-assign-wave809` and `wave809-readback-verified`.
- The body is an owner-neutral matrix/scalar assignment helper in the retail binary.

What remains unproven:

- Exact `Mat3x4` or `FMatrix` storage contract.
- Meaning of skipped destination fields at `+0x04` through `+0x10`.
- Exact source identity.
- Runtime render/math behavior.
- BEA patching behavior.
- Rebuild parity.
