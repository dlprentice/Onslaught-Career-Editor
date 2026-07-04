# Ghidra CRT/FPU Runtime Tail Review Wave1041

Status: complete read-only static review
Date: 2026-06-01
Scope: `crt-fpu-runtime-tail-review-wave1041`

Wave1041 re-read four residual CRT/FPU runtime rows from the Wave911 risk-ranked continuation queue: `0x0055da76 CRT__InitRuntimeFromStoredFrameGlobals`, `0x0055e3ea CRT__FpuIntrinsicDispatch2Thunk`, `0x00562a89 CRT__SetErrnoForFpSourceKind`, and `0x00569cb8 CRT__FloatDispatchAmsgExitCode2Thunk`. The pass made no Ghidra mutation: no rename, no signature change, no comment/tag change, no function-boundary change, no executable-byte change, no BEA launch, and no runtime/game-file mutation.

Primary anchors:

| Address | Saved state confirmed by Wave1041 | Fresh instruction/decompile evidence |
| --- | --- | --- |
| `0x0055da76 CRT__InitRuntimeFromStoredFrameGlobals` | `void CRT__InitRuntimeFromStoredFrameGlobals(void)` with CRT runtime-init/FPU-control tags. | Calls `CRT__InitFloatConversionDispatchTable`, probes processor features through `CDXTexture__ProbeProcessorFeaturePresentOrFallback`, stores `EAX` into `DAT_009d08b8`, calls `CRT__InitFpuControlWord_0x10000_0x30000`, then `FNCLEX`/`RET`. |
| `0x0055e3ea CRT__FpuIntrinsicDispatch2Thunk` | `void __cdecl CRT__FpuIntrinsicDispatch2Thunk(void)` with broad math-xref and FPU dispatch tags. | Loads `EDX = 0x00653330` and jumps to `__cintrindisp2`; xrefs span renderer, gameplay, UI, and PDSimpleSprite expression/curve evaluation callers. |
| `0x00562a89 CRT__SetErrnoForFpSourceKind` | `void __cdecl CRT__SetErrnoForFpSourceKind(int sourceKind)` with CRT heap/FPU errno tags. | For `sourceKind == 1`, calls `CRT__GetErrnoThreadPtr_00567aa8` and writes `0x21`; for `sourceKind` 2 or 3, writes `0x22`; other values return unchanged. |
| `0x00569cb8 CRT__FloatDispatchAmsgExitCode2Thunk` | `void CRT__FloatDispatchAmsgExitCode2Thunk(void)` with CRT float-dispatch/default-abort tags. | Pushes runtime error code `2`, calls `__amsg_exit`, pops the stack slot, and returns; xrefs include computed calls from float formatting/input paths and DATA table pointers `0x00653658` through `0x0065366c`. |

Evidence counts:

- Fresh exports: `4` metadata rows, `4` tag rows, `63` xref rows, `24` body-instruction rows, and `4` decompile rows.
- Queue closure remains `6238/6238 = 100.00%` with `0` commentless, `0` exact-undefined signatures, and `0` `param_N`.
- Wave911 focused re-audit progress after Wave1041 remains `727/1408 = 51.63%`.
- Expanded static surface progress after Wave1041 advances to `960/1493 = 64.30%`.
- Wave911 top-500 risk-ranked coverage remains `500/500 = 100.00%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260601-090132_post_wave1041_crt_fpu_runtime_tail_review_verified`, `19` files, `174263175` bytes, `DiffCount=0`, `HashDiffCount=0`.

What this proves:

- The selected CRT/FPU rows still have coherent saved names, signatures, comments, tags, xrefs, instruction bodies, and decompile output.
- The saved comments still match fresh static evidence for startup/FPU init, intrinsic dispatch, errno mapping, and float-dispatch default abort behavior.
- The rows remain compiler/CRT support infrastructure rather than game-system behavior.

What remains unproven:

- Exact MSVC CRT helper/source identity.
- Exact float-dispatch table semantics, FPU control/status side effects, and processor feature policy.
- Runtime errno/error-report/exit behavior.
- BEA patching behavior, gameplay outcomes, and rebuild parity.

Probe token anchor: Wave1041; crt-fpu-runtime-tail-review-wave1041; 0x0055da76 CRT__InitRuntimeFromStoredFrameGlobals; 0x0055e3ea CRT__FpuIntrinsicDispatch2Thunk; 0x00562a89 CRT__SetErrnoForFpSourceKind; 0x00569cb8 CRT__FloatDispatchAmsgExitCode2Thunk; __cintrindisp2; __amsg_exit; DAT_009d08b8; 0x00653658; 727/1408 = 51.63%; 960/1493 = 64.30%; 500/500 = 100.00%; 6238/6238 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260601-090132_post_wave1041_crt_fpu_runtime_tail_review_verified; no mutation.
