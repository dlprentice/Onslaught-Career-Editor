# Ghidra CRT SEH Tail Wave881 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-25
Scope: `crt-seh-tail-wave881`
Anchor: Wave881 CRT SEH tail

Wave881 saved Ghidra comments and tags for five adjacent CRT SEH/C++ exception runtime rows from `0x005602d2 CRT__SehDispatchWithScopeTable` through `0x0056080d CRT__CleanupCatchContext`. The pass verified existing signatures, made no renames, made no function-boundary changes, made no executable-byte changes, did not launch BEA, and did not touch the installed game.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x005602d2 CRT__SehDispatchWithScopeTable` | Checks frame magic `0x19930520`, exception flags mask `0x66`, C++ EH code `0xe06d7363`, computed handler pointers, `CRT__SehUnwindToTargetState`, and `CRT__SehLookupAndInvokeScopeHandler`; xrefs include `CRT__SehDispatchWithScopeTable_Thunk_0055d731`, `CRT__SehCallback_Call_005602d2`, and `CRT__SehFilterCppException`. |
| `0x0056036d CRT__SehLookupAndInvokeScopeHandler` | Validates current state, reads TLS catch-context fields through `CRT__GetOrInitThreadLocalRecord`, scans try-block ranges from `CRT__GetRangeOfTryBlocksForState`, checks handler descriptors through `CRT__TypeMatchForCatch`, and calls `CRT__SehUnwindAndResumeSearch` on a match. |
| `0x00560520 CRT__ValidateCatchHandlersForThrow` | Checks the TLS exception-translator slot at `+0x68`, calls `CRT__CallExceptionTranslator`, scans try-block handler descriptors, and calls `CRT__SehUnwindAndResumeSearch` for eligible handlers. |
| `0x005606c5 CRT__SehUnwindAndResumeSearch` | Calls `CRT__BuildCatchObject`, `CRT__SehRtlUnwindAndRestoreFrame`, `CRT__SehUnwindToTargetState`, `CRT__CallCatchBlock`, and `CRT__SehPopExceptionFrameAndJump` for matched-handler transfer. |
| `0x0056080d CRT__CleanupCatchContext` | Hidden `EBP`/`ESI`/`EDI` cleanup thunk that restores TLS catch-context fields `+0x6c` and `+0x70`, then conditionally calls `__abnormal_termination` and `CRT__DestroyCatchObject`. |

Read-back evidence:

- `ApplyCrtSehTailWave881.java dry`: `updated=0 skipped=5 renamed=0 would_rename=0 missing=0 bad=0`
- `ApplyCrtSehTailWave881.java apply`: `updated=5 skipped=0 renamed=0 would_rename=0 missing=0 bad=0`
- `ApplyCrtSehTailWave881.java final dry`: `updated=0 skipped=5 renamed=0 would_rename=0 missing=0 bad=0`
- Post exports: 5 metadata rows, 5 tag rows, 8 xref rows, 353 instruction rows, 5 decompile rows, 10 context metadata rows, and 10 context decompile rows.
- Queue after Wave881: 6113 total functions, 5929 commented, 184 commentless, 0 exact-undefined signatures, 0 `param_N`, strict static quality proxy `5929/6113 = 96.99%`.
- Next raw commentless row: `0x00561530 CRT__ReportMathErrorAndRestoreControlWord_00561530`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260525-235139_post_wave881_crt_seh_tail_verified`, 19 files, 172755847 bytes, `DiffCount=0`.

What this proves:

- The five target function rows exist in the saved Ghidra project.
- Their saved signatures match the existing clean signatures.
- Their saved comments and tags include `crt-seh-tail-wave881` and `wave881-readback-verified`.
- The observed behavior is static retail Ghidra evidence tied to metadata, xrefs, instructions, decompiles, context exports, and backup verification.

What remains unproven:

- Exact MSVC CRT version/source identity.
- Exact frame, throw-info, scope-table, catch-handler, and TLS metadata layouts.
- Runtime exception, unwind, translator, catch-object, and non-local jump behavior.
- BEA patching behavior.
- Rebuild parity.
