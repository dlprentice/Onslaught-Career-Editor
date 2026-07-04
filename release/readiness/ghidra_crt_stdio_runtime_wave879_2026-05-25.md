# Ghidra CRT/Stdio Runtime Wave879 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-25
Scope: `crt-stdio-runtime-wave879`

Wave879 CRT/stdio runtime saved comments/tags for thirteen adjacent CRT/compiler-runtime rows from `0x0055dcb0 CRT__AcosDispatch_ST0` through `0x0055e607 WcsLen`, plus three context comment refreshes at `CRT__Acos`, `CRT__InitRuntimeFromStoredFrameGlobals`, and `CRT__InvokeFunctionPointerRange`. The pass corrected three stale owner labels, preserved existing clean signatures, made no function-boundary changes, made no executable-byte changes, did not launch BEA, and did not mutate the installed game.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x0055dcb0 CRT__AcosDispatch_ST0` | Renamed from stale `OID__AcosWrapper`; body marshals x87 ST0 into double words, calls `CRT__ExtractFiniteExponentMaskOrPassThrough`, then calls `CRT__Acos`; 41 broad world/gameplay/math xrefs. |
| `0x0055dd7b CRT__RunStaticInitRangesWithOptionalCallback` | Renamed from stale `CFastVB__RunStaticInitRangesWithOptionalCallback`; entry xref calls optional runtime-init callback pointer, then invokes two function-pointer ranges. |
| `0x0055de6f CRT__Lock_0x0D` / `0x0055de78 CRT__Unlock_0x0D` | Compact wrappers around `CRT__LockByIndex(0x0d)` and `CRT__UnlockByIndex(0x0d)`, used by CRT exit/shutdown paths. |
| `0x0055de9b sprintf` | Builds output descriptor with mode bits `0x42` and limit `0x7fffffff`, calls `CRT__FormatOutputToStream`, and has 304 xrefs across diagnostics/config/resource/game paths. |
| `0x0055def0 CRT__AllocaProbe` | Stack probe walks by `0x1000` pages toward the requested target and restores the return address on the adjusted stack; 40 compiler/runtime xrefs. |
| `0x0055e38c vsprintf` | Uses the same formatted-output descriptor pattern as `sprintf`, but forwards supplied varargs pointer directly to `CRT__FormatOutputToStream`. |
| `0x0055e3ea CRT__FpuIntrinsicDispatch2Thunk` | Renamed from stale `CPDSimpleSprite__FpuDispatchStub`; tail-calls `__cintrindisp2`; 44 broad math/renderer/gameplay/UI xrefs. |
| `0x0055e42a Win32__CaptureSystemTimeAsFileTimeTicks` | DATA xref `0x00622b18`; calls `GetSystemTimeAsFileTime` and combines FILETIME high/low words into global tick storage. |
| `0x0055e490 fopen`, `0x0055e4a3 fclose`, `0x0055e520 fprintf` | CRT file/stdio wrappers tied to console logs, resources, missions, textures, sound, save/load, and formatted logging paths. |
| `0x0055e607 WcsLen` | 16-bit wide-string length helper with 23 UI/text conversion xrefs. |

Read-back evidence:

- `ApplyCrtStdioRuntimeWave879.java dry`: `updated=0 skipped=16 renamed=0 would_rename=3 missing=0 bad=0`
- `ApplyCrtStdioRuntimeWave879.java apply`: `updated=16 skipped=0 renamed=3 would_rename=0 missing=0 bad=0`
- `ApplyCrtStdioRuntimeWave879.java final dry`: `updated=0 skipped=16 renamed=0 would_rename=0 missing=0 bad=0`
- Post exports: 13 metadata rows, 13 tag rows, 523 xref rows, 195 instruction rows, 13 decompile rows, 12 context metadata rows, and 12 context decompile rows.
- Queue after Wave879: 6113 total, 5914 commented, 199 commentless, 0 exact-undefined signatures, 0 `param_N`, comment-backed and strict clean-signature proxy `5914/6113 = 96.74%`.
- Next raw commentless row: `0x0055ecb1 CRT__UnlockHeapLock9_0055ecb1`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260525-225409_post_wave879_crt_stdio_runtime_verified`, 19 files, 172723079 bytes, `DiffCount=0`.

What this proves:

- The thirteen target function rows and three context rows exist in the saved Ghidra project with the saved comments and `crt-stdio-runtime-wave879` / `wave879-readback-verified` tags.
- The three stale owner labels were corrected to CRT/runtime names backed by body shape and xref breadth.
- Existing signatures remained clean and were read back after rename/comment/tag application.
- The observed behavior is static retail Ghidra decompile/xref/instruction evidence tied to CRT math dispatch, static init, locks, formatted output, stack probing, file I/O, time capture, and wide-string text helpers.
- These are high-importance CRT/stdio/runtime connector rows with low local evidence density, not low-importance filler.

What remains unproven:

- Exact MSVC helper identity/version and source-body identity.
- Full CRT startup/shutdown, stdio, file, locale, and FPU/intrinsic semantics.
- Runtime file I/O, logging, formatting, exception, stack-probe, FPU, or localization behavior.
- BEA patching behavior.
- Rebuild parity.
