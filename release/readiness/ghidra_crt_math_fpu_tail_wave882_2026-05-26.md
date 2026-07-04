# Ghidra CRT Math/FPU Tail Wave882 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-26
Scope: `crt-math-fpu-tail-wave882`
Anchor: Wave882 CRT math/FPU tail
Exact anchors include `0x00562c76 CRT__GetFpuControlWord`.

Wave882 saved Ghidra comments and tags for fourteen adjacent CRT math/FPU/heap-lock runtime rows from `0x00561530 CRT__ReportMathErrorAndRestoreControlWord_00561530` through `0x00562c99 CRT__ReturnVoid`. The pass verified existing signatures, made no renames, made no function-boundary changes, made no executable-byte changes, did not launch BEA, and did not touch the installed game.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x00561530 CRT__ReportMathErrorAndRestoreControlWord_00561530` | Reached from `CRT__PowCoreWithFpuGuards` and `CRT__HandleFpuExceptionForMathOp`; saves EAX/caller stack double words and reaches `CRT__HandleFloatingPointException`. |
| `0x00561590 CRT__Exp2FromFpuCore_00561590` | x87 `FRNDINT` / `F2XM1` / `FSCALE` helper reached from pow core. |
| `0x005615a5 CRT__SetFpuControlWordMasked_005615a5` | Reads caller control word, preserves rounding bits `0x300`, ORs `0x7f`, and executes `FLDCW`; xrefs from acos/pow helpers. |
| `0x005615bc CRT__MapExponentFlagToClassCode_005615bc` | Tests exponent/classification bit `0x80000`, returns class code `7` or performs `FADD` against constant `0x005e5bf0` and returns `1`. |
| `0x005621b9` / `0x00562307` / `0x005623c7` / `0x00562442` | Four heap-lock cleanup thunks reduce to `CRT__UnlockByIndex(9)` from realloc/msize paths. |
| `0x0056249f CRT__HandleFloatingPointExceptionByFlags` | Calls `CRT__AdjustFloatingPointForFormatFlags`, `CRT__RaiseFloatingPointException`, `CRT__HandleFpStatusAndReturnDouble`, errno helpers, and `CRT__GetFpuControlWord`. |
| `0x00562537 CRT__RaiseFloatingPointException` | Builds an FPU exception record, maps status bits to NT exception codes `0xc000008f`, `0xc0000093`, `0xc0000091`, `0xc000008e`, and `0xc0000090`, calls `RaiseException`, then writes selected record bits back into the caller control word. |
| `0x00562c59` / `0x00562c67` / `0x00562c76` / `0x00562c99` | FPU status-word/control-word readback thunks and a return-only callback used by FPU exception/format-adjustment paths. |

Read-back evidence:

- `ApplyCrtMathFpuTailWave882.java dry`: `updated=0 skipped=14 renamed=0 would_rename=0 missing=0 bad=0`
- `ApplyCrtMathFpuTailWave882.java apply`: `updated=14 skipped=0 renamed=0 would_rename=0 missing=0 bad=0`
- `ApplyCrtMathFpuTailWave882.java final dry`: `updated=0 skipped=14 renamed=0 would_rename=0 missing=0 bad=0`
- Post exports: 14 metadata rows, 14 tag rows, 34 xref rows, 434 instruction rows, 14 decompile rows, 12 context metadata rows, and 12 context decompile index rows with the expected `CRT__PowCoreWithFpuGuards` context decompile-limit failure.
- Queue after Wave882: 6113 total functions, 5943 commented, 170 commentless, 0 exact-undefined signatures, 0 `param_N`, strict static quality proxy `5943/6113 = 97.22%`.
- Next raw commentless row: `0x00563ad3 CRT__FpuTransDispatch2_ClearStatusAndHandle`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260526-002800_post_wave882_crt_math_fpu_tail_verified`, 19 files, 172755847 bytes, `DiffCount=0`.

What this proves:

- The 14 target function rows exist in the saved Ghidra project.
- The saved comments and tags include `crt-math-fpu-tail-wave882` and `wave882-readback-verified`.
- Existing clean signatures were verified and preserved.
- The observed CRT math/FPU/heap-lock helper bodies are static retail Ghidra evidence tied to xrefs, instruction/decompile exports, and surrounding context metadata.

What remains unproven:

- Exact MSVC CRT helper/version identity.
- Exact FPU control/status/exception record layouts.
- Runtime floating-point exception behavior.
- Runtime heap-lock behavior.
- BEA patching behavior.
- Rebuild parity.
