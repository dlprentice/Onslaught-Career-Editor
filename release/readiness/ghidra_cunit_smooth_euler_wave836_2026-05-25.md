# Ghidra CUnit Smooth Euler Wave836 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-25
Scope: `cunit-smooth-euler-wave836`

Wave836 CUnit Smooth Euler saved a bounded signature/comment/tag correction for `0x004fa4b0 CUnit__SmoothEulerTowardTargetAndBuildMatrix`. This is important shared CUnit motion/orientation infrastructure with lower direct source-body evidence density, not low-importance code. The pass made no rename, no function-boundary change, and no executable-byte change.

| Address | Saved state | Evidence |
| --- | --- | --- |
| `0x004fa4b0 CUnit__SmoothEulerTowardTargetAndBuildMatrix` | `void __thiscall CUnit__SmoothEulerTowardTargetAndBuildMatrix(void * this, float * current_euler_xyz, float * target_euler_xyz, float * max_step_xyz, float * out_matrix3x4)` | Deep instruction export shows `RET 0x10` at `0x004fa7fc`; the direct caller stub at `0x00428c15-0x00428c21` pushes `EDX`, `ESI`, and two caller stack pointers before calling the target, then returns with `RET 0x10`. |
| DATA slot refs | 30 slot pointers to `0x004fa4b0` | DATA refs at `0x005d8af8`, `0x005d8fe8`, `0x005dd8bc`, `0x005dfacc`, `0x005dfe70`, `0x005e00c0`, `0x005e0310`, `0x005e0564`, `0x005e07b8`, `0x005e0a14`, `0x005e0c64`, `0x005e0ec0`, `0x005e1114`, `0x005e1370`, `0x005e15c4`, `0x005e1814`, `0x005e1a64`, `0x005e1cb8`, `0x005e1f0c`, `0x005e216c`, `0x005e23c0`, `0x005e2610`, `0x005e2860`, `0x005e2ab0`, `0x005e2d00`, `0x005e2f54`, `0x005e31a8`, `0x005e3408`, `0x005e3658`, and `0x005e38ac` all read back as pointers to this body. |
| Motion/orientation flow anchors | Static body evidence | Observed behavior calls vfunc +0x60 on the receiver for a frame-scale/time scalar, smooths current Euler `x/y/z` toward target Euler `x/y/z` using per-axis max-step input and constants at `0x005d85c0`, `0x005d85dc`, `0x005d85e0`, `0x005d85e4`, and `0x005d85e8`, wraps angle axes across the +/- pi-like boundary, computes sin/cos terms, and copies twelve floats into `out_matrix3x4`. |

Read-back evidence:

- `ApplyCUnitSmoothEulerWave836.java dry`: `updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0`
- `ApplyCUnitSmoothEulerWave836.java apply`: `READBACK_OK`, `updated=1 skipped=0 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0`
- `ApplyCUnitSmoothEulerWave836.java final dry`: `updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 1 metadata row, 1 tag row, 31 xref rows including 30 DATA slot refs, 141 instruction-window rows, 361 deep instruction rows, 55 xref-site instruction rows, 7 context metadata rows, 7 context decompile rows, and 1 decompile row.
- Queue after Wave836: 6098 total functions, 5658 commented, 440 commentless, 0 exact-undefined signatures, 0 `param_N`, comment-backed proxy `5658/6098 = 92.78%`, strict clean-signature proxy `5658/6098 = 92.78%`.
- Next raw commentless row: `0x004fc3a0 CSpawnerThng__SetCooldownState3`; commentless high-signal, signature, and name-confidence queues remain empty.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260525-010821_post_wave836_cunit_smooth_euler_verified`, 19 files, 171838343 bytes, `DiffCount=0`.

What this proves:

- The saved Ghidra row exists at `0x004fa4b0`.
- The saved signature, function comment, and tags include `cunit-smooth-euler-wave836` and `wave836-readback-verified`.
- The four explicit stack arguments are supported by `RET 0x10` and direct caller-stub push evidence.
- The observed Euler smoothing and matrix-build behavior is static retail Ghidra evidence tied to decompile, instruction, xref, context, and DATA-slot exports.

What remains unproven:

- Exact Unit.cpp source-body identity.
- Exact angle units.
- Exact matrix row/column convention.
- Concrete `CUnit` layout.
- Runtime motion/orientation behavior.
- BEA patching behavior.
- Rebuild parity.
