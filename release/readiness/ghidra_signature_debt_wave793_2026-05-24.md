# Ghidra Signature Debt Wave793 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-24
Scope: `signature-debt-wave793`

Wave793 signature debt saved parameter-hardened signatures/comments/tags for eight Visual C++ CRT/runtime helper rows. The pass made no renames, no function-boundary changes, and no executable-byte changes.

Representative anchors:

| Address | Saved signature | Static evidence |
| --- | --- | --- |
| `0x0055f7a3 ___timet_from_ft` | `int __cdecl ___timet_from_ft(void * file_time)` | Visual C++ 2003 library match; decompile converts non-zero FILETIME through local/system time and `CRT__SystemTimeToUnixTimestampLocal`, else returns `-1`. |
| `0x00560ae0 __CallSettingFrame@12` | `void __stdcall __CallSettingFrame@12(int frame_arg0, int frame_arg1, int nlg_destination)` | Visual C++ non-local-goto setting-frame helper; notifies `__NLG_Notify1`, performs an indirect frame call, maps destination `0x100` to `2`, and notifies again. |
| `0x00561339 __seh_longjmp_unwind@4` | `void __stdcall __seh_longjmp_unwind@4(void * longjmp_registration)` | Visual C++ 1998/2003 SEH longjmp unwind helper; calls `__local_unwind2` using fields at `longjmp_registration+0x18` and `+0x1c`. |
| `0x005615d5 __fload_withFB` | `uint __fastcall __fload_withFB(int dispatch_cookie, void * floating_record)` | Visual C++ fastcall floating-load helper; reads high dword at `floating_record+4`, masks exponent bits, and preserves the high dword for `0x7ff` exponent cases. |
| `0x0056163b __math_exit` | `void __cdecl __math_exit(void)` | Visual C++ math-exit helper; checks FPU status/control state and calls `__startOneArgErrorHandling` only on the observed error path. |
| `0x0056d4c7 ___add_12` | `void __cdecl ___add_12(uint * accumulator, uint * addend)` | Visual C++ 2003 12-byte addition helper; adds three dwords with carry propagation through `CRT__UIntAddWithOverflowCheck`. |
| `0x0059ccce Memcpy` | `void * __thiscall Memcpy(void * this, void * destination, void * source, uint byte_count)` | Visual C++ 2003 C++ stream/memory-file `Memcpy` virtual helper; owner remains ambiguous between `CHtmlStream` and `CMemFile`; body copies dwords plus tail bytes and returns `destination`. |
| `0x005d0983 init_namebuf` | `void __cdecl init_namebuf(int temp_name_selector)` | Visual C++ 2003 temporary-name buffer initializer; selects one of two globals, normalizes a separator, writes `s`/`t`, appends process id in base `0x20`, and appends the suffix. |

Read-back evidence:

- `ApplySignatureDebtWave793.java dry`: `updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=8 comment_only_updated=0 missing=0 bad=0`
- Initial `ApplySignatureDebtWave793.java apply` saved seven rows and exposed a verifier/spec mismatch for `Memcpy`: Ghidra synthesized the implicit `this` parameter for `__thiscall`, while the first spec also supplied an explicit object parameter. The preserved log is `apply-initial-thiscall-mismatch.log`.
- Corrected dry after the `__thiscall` fix: `updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0`
- Corrected apply: `updated=1 skipped=7 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0`
- Final dry: `updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 8 metadata rows, 8 tag rows, 19 xref rows, 296 instruction rows, and 8 decompile rows.
- Queue after Wave793: 6098 total, 5544 commented, 554 commentless, 13 exact-undefined signatures, 11 `param_N`, comment-backed proxy `5544/6098 = 90.92%`, strict clean-signature proxy `5520/6098 = 90.52%`.
- Earliest raw commentless row remains `0x0042f220 CSPtrSet__Clear`.
- The commentless high-signal queue remains empty; next signature-debt head is `0x004acde0 CMeshCollisionVolume__InitContactOutputRecord`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260524-034246_post_wave793_crt_runtime_signature_debt_verified`, 19 files, 171281287 bytes, `DiffCount=0`.

What this proves:

- The eight target function rows exist in the saved Ghidra project.
- The saved signatures/comments/tags match the Wave793 post-export artifacts.
- The `signature-debt-wave793` and `wave793-readback-verified` tags are present on all eight targets.
- The observed bodies are static retail Ghidra evidence tied to Visual C++ library matches, instruction/decompile exports, and queue read-back.

What remains unproven:

- Exact Visual C++ CRT source version identity.
- Runtime time-conversion, SEH, FPU, math, arithmetic, stream, temporary-file, or exception behavior.
- BEA patching behavior.
- Rebuild parity.
