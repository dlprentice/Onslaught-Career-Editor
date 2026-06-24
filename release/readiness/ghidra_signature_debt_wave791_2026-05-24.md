# Ghidra Signature Debt Wave791 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-24
Scope: `signature-debt-wave791`

Wave791 signature debt saved Ghidra comments, tags, and hardened signatures for ten adjacent Visual C++ CRT/SEH helper rows from `0x0055d6a0 CRT__SehPopExceptionFrameAndJump` through `0x0055da55 __NLG_Notify1`. The pass made no renames, no function-boundary changes, and no executable-byte changes.

Representative anchors:

| Address | Saved signature | Evidence |
| --- | --- | --- |
| `0x0055d6a0 CRT__SehPopExceptionFrameAndJump` | `void __stdcall CRT__SehPopExceptionFrameAndJump(void * continuation_target)` | Pops/restores SEH frame state and transfers through `continuation_target`; xref from `CRT__SehUnwindAndResumeSearch`. |
| `0x0055d6e2 CRT__SehRtlUnwindAndRestoreFrame` | `void __stdcall CRT__SehRtlUnwindAndRestoreFrame(void * target_frame, void * exception_record)` | Calls `RtlUnwind(target_frame, 0x0055d70a, exception_record, 0)`, clears flag bit `0x2`, and restores FS exception-list state. |
| `0x0055d896 CRT__SehFilterCppException` | `int __cdecl CRT__SehFilterCppException(void * exception_record, void * seh_frame, void * dispatcher_context)` | Checks `exception_record+4`, marks `seh_frame+0x24`, dispatches through the scope-table helper, and may call the Wave791 unwind/restore helper. |
| `0x0055d90b CRT__GetRangeOfTryBlocksForState` | `int __cdecl CRT__GetRangeOfTryBlocksForState(void * eh_func_info, int try_nesting_index, int current_state, int * out_low_try, int * out_high_try)` | Walks `0x14`-byte try-block records from `eh_func_info+0x10`, compares `current_state`, writes output range pointers, and returns the selected record pointer value. |
| `0x0055d988 __global_unwind2` | `void __cdecl __global_unwind2(void * target_frame)` | Visual C++ library match; decompile calls `RtlUnwind(target_frame, 0x0055d9a0, NULL, NULL)`. |
| `0x0055d9ca __local_unwind2` | `void __cdecl __local_unwind2(void * registration_frame, int stop_state)` | Visual C++ library match; decompile walks local unwind scope records until state `-1` or `stop_state`. |
| `0x0055da55 __NLG_Notify1` | `void __fastcall __NLG_Notify1(int nlg_destination)` | Visual C++ library match; stores `nlg_destination` plus implicit EAX/EBP values into CRT non-local-goto globals. |

Read-back evidence:

- `ApplySignatureDebtWave791.java dry`: `updated=0 skipped=10 renamed=0 would_rename=0 signature_updated=10 comment_only_updated=0 missing=0 bad=0`
- `ApplySignatureDebtWave791.java apply`: `updated=10 skipped=0 renamed=0 would_rename=0 signature_updated=10 comment_only_updated=0 missing=0 bad=0`
- `ApplySignatureDebtWave791.java final dry`: `updated=0 skipped=10 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 10 metadata rows, 10 tag rows, 18 xref rows, 1050 instruction rows, and 10 decompile rows.
- Queue after Wave791: 6098 total, 5544 commented, 554 commentless, 28 exact-undefined signatures, 12 `param_N`, comment-backed proxy `5544/6098 = 90.92%`, strict clean-signature proxy `5504/6098 = 90.26%`.
- Earliest raw commentless row remains `0x0042f220 CSPtrSet__Clear`.
- The commentless high-signal queue remains empty.
- Verified backup: `G:\GhidraBackups\BEA_20260524-025245_post_wave791_crt_seh_signature_debt_verified`, 19 files, 171215751 bytes, `DiffCount=0`.

What this proves:

- The ten target function rows exist in the saved Ghidra project.
- The saved signatures no longer contain `undefined` returns or `param_N` names.
- The saved comments and tags include `signature-debt-wave791` and `wave791-readback-verified`.
- The observed bodies are static retail Ghidra evidence tied to decompile/instruction/xref exports and Visual C++ library-match names where present.

What remains unproven:

- Exact Visual C++ CRT source version identity.
- Runtime exception behavior.
- Runtime unwind behavior.
- BEA patching behavior.
- Rebuild parity.
