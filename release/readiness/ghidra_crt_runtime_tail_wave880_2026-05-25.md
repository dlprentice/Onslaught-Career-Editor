# Ghidra CRT Runtime Tail Wave880 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-25
Scope: `crt-runtime-tail-wave880`

Wave880 CRT runtime tail saved comments/tags for ten adjacent CRT/runtime connector rows from `0x0055ecb1 CRT__UnlockHeapLock9_0055ecb1` through `0x0055fc35 CRT__IsFloat10Integral_0055fc35`. It corrected the stale `CDropship__FindSubstringW` owner label to `CRT__WcsStr`, verified and preserved existing clean signatures, made no function-boundary change, made no executable-byte change, did not launch BEA, and did not touch the installed game.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x0055ecb1 CRT__UnlockHeapLock9_0055ecb1` | Heap-allocation cleanup thunk; pushes lock index `9`, calls `CRT__UnlockByIndex`, and is called by `CRT__HeapAllocBase`. |
| `0x0055ed10 CRT__UnlockHeapLock9_0055ed10` | Second `CRT__HeapAllocBase` lock-index-9 cleanup thunk. |
| `0x0055f0ef CRT__UnlockHeapLock` | Free-path lock-index-9 release thunk called by `CRT__FreeBase`. |
| `0x0055f147 CRT__UnlockHeapLock_Alt` | Alternate `CRT__FreeBase` lock-index-9 release thunk. |
| `0x0055f16e fwrite` | Locks via `CRT__LockRouteByAddress`, calls `CRT__FWriteCore`, unlocks, and is called by TGA, save, options, and landscape texture-cache writers. |
| `0x0055f2a7 CRT__WcsStr` | Owner-corrected from `CDropship__FindSubstringW`; walks 16-bit haystack/needle strings. The only xref is `CMessageBox__SelectPortraitIndex`. |
| `0x0055f380 CRT__AcosClassifyAndDispatch` | Spills x87 `ST0` as a double, classifies exponent bits, and calls `CRT__AcosCoreWithFpuGuards`; xrefs include static-shadow ray/triangle math. |
| `0x0055f4d7 fread` | Locks via `CRT__LockRouteByAddress`, calls `CRT__FReadCore`, unlocks, and is called by startup, shader clone, Ogg Vorbis, and save-read paths. |
| `0x0055fa40 CRT__PowDispatch_ST0_ST1` | Spills two x87 doubles and calls decompile-limited `CRT__PowCoreWithFpuGuards`; xrefs include PNG gamma/decode and async music volume. |
| `0x0055fc35 CRT__IsFloat10Integral_0055fc35` | Pow-core x87 integral-test helper; two xrefs inside `CRT__PowCoreWithFpuGuards`. |

Read-back evidence:

- `ApplyCrtRuntimeTailWave880.java dry`: `updated=0 skipped=10 renamed=0 would_rename=1 missing=0 bad=0`
- `ApplyCrtRuntimeTailWave880.java apply`: `updated=10 skipped=0 renamed=1 would_rename=0 missing=0 bad=0`
- `ApplyCrtRuntimeTailWave880.java final dry`: `updated=0 skipped=10 renamed=0 would_rename=0 missing=0 bad=0`
- Post exports: 10 metadata rows, 10 tag rows, 35 xref rows, 114 instruction rows, 10 decompile rows, 10 context metadata rows, and 10 context decompile index rows with the expected `CRT__PowCoreWithFpuGuards` decompile-limit failure.
- Queue after Wave880: 6113 total, 5924 commented, 189 commentless, 0 exact-undefined signatures, 0 `param_N`, strict clean-signature proxy `5924/6113 = 96.91%`.
- Next raw commentless row: `0x005602d2 CRT__SehDispatchWithScopeTable`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260525-233022_post_wave880_crt_runtime_tail_verified`, 19 files, 172755847 bytes, `DiffCount=0`.

What this proves:

- The 10 target function rows exist in the saved Ghidra project.
- The saved comments and tags include `crt-runtime-tail-wave880` and `wave880-readback-verified`.
- `0x0055f2a7` has the saved owner-corrected name/signature `short * __cdecl CRT__WcsStr(short * haystack, short * needle)`.
- The observed bodies are static retail Ghidra evidence tied to xrefs, target decompiles/instructions, context metadata, and bounded existing CRT helper comments.

What remains unproven:

- Exact MSVC CRT helper identity/version.
- Exact CRT lock, stream, file I/O, wide-string, x87, and math exception semantics.
- Runtime heap/thread/file/save/audio/PNG/static-shadow/portrait behavior.
- BEA patching behavior.
- Rebuild parity.
