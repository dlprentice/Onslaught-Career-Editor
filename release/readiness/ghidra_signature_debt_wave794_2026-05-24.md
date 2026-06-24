# Ghidra Signature Debt Wave794 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-24
Scope: `signature-debt-wave794`

Wave794 signature debt saved parameter-hardened signatures/comments/tags for nine Visual C++ CRT/FPU helper rows. The pass made no renames, no function-boundary changes, and no executable-byte changes.

Representative anchors:

| Address | Saved signature | Static evidence |
| --- | --- | --- |
| `0x00561360 __trandisp1` | `void __fastcall __trandisp1(int dispatch_cookie, void * transition_table)` | Visual C++ one-operand transcendental dispatch helper; classifies hidden ST0/EBP FPU state and dispatches through the selected transition-table slot. |
| `0x005613c7 __trandisp2` | `void __fastcall __trandisp2(int dispatch_cookie, void * transition_table)` | Visual C++ two-operand transcendental dispatch helper; classifies hidden ST0/ST1/EBP FPU state and combines the two condition indexes through `DAT_0065374c`. |
| `0x00561547 __startOneArgErrorHandling` | `float10 __fastcall __startOneArgErrorHandling(float10 * __return_storage_ptr__, int dispatch_cookie, int error_context, ushort fpu_control_word, int error_slot0, int error_slot1, int error_slot2)` | Visual C++ one-argument floating-point error handler; spills hidden ST0, forwards the error context/control-word slots into `CRT__HandleFloatingPointException`, and restores the floating result. |
| `0x00562b03 __frnd` | `float10 __cdecl __frnd(float10 * __return_storage_ptr__, double input_value)` | Visual C++ round helper; returns `ROUND(input_value)` through the x87-style `float10` path. |
| `0x00563a10 __cintrindisp2` | `void __cdecl __cintrindisp2(void)` | Visual C++ two-operand intrinsic dispatch wrapper; calls `__trandisp2` and then `CRT__FpuIntDispatch2_Handle`. |
| `0x00563a4e __cintrindisp1` | `void __cdecl __cintrindisp1(void)` | Visual C++ one-operand intrinsic dispatch wrapper; calls `__trandisp1` and then `CRT__FpuIntDispatch2_Handle`. |
| `0x00563a8b __ctrandisp2` | `void __cdecl __ctrandisp2(uint left_mantissa_low, int left_packed_high, uint right_mantissa_low, int right_packed_high)` | Visual C++ two-operand transcendental wrapper; loads two packed floating operands through `__fload`, calls `__trandisp2`, and clears/handles FPU status. |
| `0x00563c0b __ctrandisp1` | `void __cdecl __ctrandisp1(uint mantissa_low, int packed_high)` | Visual C++ one-operand transcendental wrapper; loads one packed floating operand through `__fload`, calls `__trandisp1`, and clears/handles FPU status. |
| `0x00563c3e __fload` | `float10 __cdecl __fload(float10 * __return_storage_ptr__, uint mantissa_low, int packed_high)` | Visual C++ packed floating-load helper; handles the `0x7ff0` exponent case and otherwise converts packed high/low dwords through the double-to-`float10` path. |

Read-back evidence:

- `ApplySignatureDebtWave794.java dry`: `updated=0 skipped=9 renamed=0 would_rename=0 signature_updated=9 comment_only_updated=0 missing=0 bad=0`
- Initial `ApplySignatureDebtWave794.java apply` saved six rows and exposed a verifier/spec mismatch for the three `float10` return helpers: Ghidra renders a synthetic `float10 * __return_storage_ptr__` parameter on readback. The preserved log is `apply.log`.
- Corrected apply/read-back after the `float10` renderer fix: `updated=0 skipped=9 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Final dry: `updated=0 skipped=9 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 9 metadata rows, 9 tag rows, 19 xref rows, 405 instruction rows, and 9 decompile rows.
- Queue after Wave794: 6098 total, 5544 commented, 554 commentless, 4 exact-undefined signatures, 11 `param_N`, comment-backed proxy `5544/6098 = 90.92%`, strict clean-signature proxy `5529/6098 = 90.67%`.
- Earliest raw commentless row remains `0x0042f220 CSPtrSet__Clear`.
- The commentless high-signal queue remains empty; next signature-debt head is `0x004acde0 CMeshCollisionVolume__InitContactOutputRecord`.
- Verified backup: `G:\GhidraBackups\BEA_20260524-041355_post_wave794_crt_fpu_signature_debt_verified`, 19 files, 171314055 bytes, `DiffCount=0`.

What this proves:

- The nine target function rows exist in the saved Ghidra project.
- The saved signatures/comments/tags match the Wave794 post-export artifacts.
- The `signature-debt-wave794` and `wave794-readback-verified` tags are present on all nine targets.
- The observed bodies are static retail Ghidra evidence tied to Visual C++ library matches, instruction/decompile exports, and queue read-back.

What remains unproven:

- Exact Visual C++ CRT source version identity.
- Runtime FPU, transcendental, intrinsic, rounding, error-handling, packed-float, or x87 exception behavior.
- BEA patching behavior.
- Rebuild parity.
