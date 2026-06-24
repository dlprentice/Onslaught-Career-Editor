# Ghidra CRT Float Dispatch Amsg Exit Wave884 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-26
Scope: `crt-float-dispatch-amsg-exit-wave884`
Task anchor: Wave884 CRT float-dispatch amsg-exit

Wave884 corrected the stale `0x00569cb8 ControlsUI__AbortInvalidParameter` owner label to `CRT__FloatDispatchAmsgExitCode2Thunk`, saved the `void CRT__FloatDispatchAmsgExitCode2Thunk(void)` signature display, and added comments/tags. The pass made one rename, no function-boundary change, no executable-byte change, and did not launch BEA.

Evidence anchors:

| Address | Saved state | Evidence |
| --- | --- | --- |
| `0x00569cb8 CRT__FloatDispatchAmsgExitCode2Thunk` | `void CRT__FloatDispatchAmsgExitCode2Thunk(void)` plus comments/tags | Four-instruction body: `PUSH 0x2`, `CALL 0x00560289 __amsg_exit`, `POP ECX`, `RET`. |
| `0x00561834 CRT__FormatOutputToStream` | context only | Computed calls through `0x00653658`, `0x00653664`, and `0x0065365c`. |
| `0x00562cef CRT__InputFormatCore` | context only | Computed call through `0x00653660`. |
| `0x00565083 ControlsUI__FormatWideStringCore` | context only | Computed calls through `0x00653658`, `0x00653664`, and `0x0065365c`. |
| `0x0055da8d CRT__InitFloatConversionDispatchTable` | context only | Replaces default DATA table pointers `0x00653658` through `0x0065366c` with `__cfltcvt`, `__fassign`, `CRT__InsertDecimalSeparatorBeforeExponent`, and local float-format helpers. |

Read-back evidence:

- `ApplyCrtFloatDispatchAmsgExitWave884.java dry`: `updated=0 skipped=1 renamed=0 would_rename=1 missing=0 bad=0`
- `ApplyCrtFloatDispatchAmsgExitWave884.java apply`: `updated=1 skipped=0 renamed=1 would_rename=0 missing=0 bad=0`
- `ApplyCrtFloatDispatchAmsgExitWave884.java final dry`: `updated=0 skipped=1 renamed=0 would_rename=0 missing=0 bad=0`
- Post exports: 1 metadata row, 1 tag row, 13 xref rows, 4 instruction rows, 1 decompile row, 5 context metadata rows, and 5 context decompile rows.
- Queue after Wave884: 6113 total, 5967 commented, 146 commentless, 0 exact-undefined signatures, 0 `param_N`, strict proxy `5967/6113 = 97.61%`.
- Next raw commentless row: `0x005715b0 CFastVB__BuildStripBatchesFromIndexBuffer`.
- Verified backup: `G:\GhidraBackups\BEA_20260526-012542_post_wave884_crt_float_dispatch_amsg_exit_verified`, 19 files, 172788615 bytes, `DiffCount=0`.

What this proves:

- The saved Ghidra target row exists at `0x00569cb8`.
- The saved name/signature/comment/tags match the Wave884 bounded static evidence.
- The stale `ControlsUI__AbortInvalidParameter` function owner label no longer remains on the function row.
- The target is statically tied to CRT float-conversion dispatch default-abort table pointers and `__amsg_exit(2)`.

What remains unproven:

- Exact MSVC CRT helper/source identity.
- Exact float-dispatch table semantics.
- Runtime error/report/exit behavior.
- BEA patching behavior.
- Rebuild parity.
