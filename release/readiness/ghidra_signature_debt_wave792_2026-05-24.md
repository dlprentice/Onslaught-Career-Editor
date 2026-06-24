# Ghidra Signature Debt Wave792 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-24
Scope: `signature-debt-wave792`

Wave792 signature debt saved Ghidra comments, tags, and hardened signatures for eight Visual C++ CRT runtime helper rows: `0x0055e0c0 __aulldiv`, `0x0055e128 __ftol`, `0x0055e4d4 __fclose_lk`, `0x0055fcc0 __alldiv`, `0x00560289 __amsg_exit`, `0x005639d0 __allmul`, `0x00569ec0 __aullrem`, and `0x0056b840 ___free_lc_time`. The pass made no renames, no function-boundary changes, and no executable-byte changes.

Representative anchors:

| Address | Saved signature | Evidence |
| --- | --- | --- |
| `0x0055e0c0 __aulldiv` | `ulonglong __stdcall __aulldiv(uint dividend_low, uint dividend_high, uint divisor_low, uint divisor_high)` | Visual C++ library match; decompile/instructions implement unsigned 64-bit division and return with `ret 0x10`. |
| `0x0055e128 __ftol` | `longlong __cdecl __ftol(void)` | Visual C++ library match; decompile uses implicit ST0 and instruction evidence changes/restores FPU rounding state. |
| `0x0055e4d4 __fclose_lk` | `int __cdecl __fclose_lk(void * stream)` | Visual C++ 2003 library match; decompile flushes/frees/closes a CRT stream-like record and clears flags. |
| `0x0055fcc0 __alldiv` | `longlong __stdcall __alldiv(uint dividend_low, int dividend_high, uint divisor_low, int divisor_high)` | Visual C++ library match; decompile normalizes signs, divides, reapplies sign, and returns with `ret 0x10`. |
| `0x00560289 __amsg_exit` | `void __cdecl __amsg_exit(int runtime_error_code)` | Visual C++ 2003 library match; decompile reports the runtime error code and exits with `0xff`. |
| `0x005639d0 __allmul` | `longlong __stdcall __allmul(uint left_low, int left_high, uint right_low, int right_high)` | Visual C++ library match; decompile computes a 64-bit product returned in EDX:EAX. |
| `0x00569ec0 __aullrem` | `ulonglong __stdcall __aullrem(uint dividend_low, uint dividend_high, uint divisor_low, uint divisor_high)` | Visual C++ library match; decompile follows the high-divisor normalization path and returns the unsigned 64-bit remainder. |
| `0x0056b840 ___free_lc_time` | `void __cdecl ___free_lc_time(void * locale_time_block)` | Visual C++ library match; decompile null-checks a locale-time block and frees many pointer fields through `CRT__FreeBase`. |

Read-back evidence:

- Initial `ApplySignatureDebtWave792.java apply` saved the target metadata but exposed a script verifier mismatch for zero-parameter `__ftol`: Ghidra read back `longlong __cdecl __ftol(void)` while the first verifier expected `__ftol()`. That initial log is preserved as `apply-initial-readback-mismatch.log`.
- Corrected dry/read-back: `updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`.
- Corrected apply-mode read-back: `updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`.
- Post exports: 8 metadata rows, 8 tag rows, 104 xref rows, 296 instruction rows, and 8 decompile rows.
- Queue after Wave792: 6098 total, 5544 commented, 554 commentless, 21 exact-undefined signatures, 11 `param_N`, comment-backed proxy `5544/6098 = 90.92%`, strict clean-signature proxy `5512/6098 = 90.39%`.
- Earliest raw commentless row remains `0x0042f220 CSPtrSet__Clear`.
- The commentless high-signal queue remains empty.
- Verified backup: `G:\GhidraBackups\BEA_20260524-031629_post_wave792_crt_runtime_signature_debt_verified`, 19 files, 171281287 bytes, `DiffCount=0`.

What this proves:

- The eight target function rows exist in the saved Ghidra project.
- The saved signatures no longer contain `undefined` returns for seven rows and no longer contain `param_N` for `__amsg_exit`.
- The saved comments and tags include `signature-debt-wave792` and `wave792-readback-verified`.
- The observed bodies are static retail Ghidra evidence tied to decompile/instruction/xref exports and Visual C++ library-match names where present.

What remains unproven:

- Exact Visual C++ CRT source version identity.
- Runtime arithmetic, FPU, stream I/O, locale cleanup, and process-exit behavior.
- BEA patching behavior.
- Rebuild parity.
