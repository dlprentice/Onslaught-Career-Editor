# Ghidra Signature Debt Wave795 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-24
Scope: `signature-debt-wave795`

Wave795 signature debt saved comments/tags/signatures for the final four exact-undefined signature rows in the current Ghidra queue. The pass made no renames, no function-boundary changes, and no executable-byte changes.

Representative anchors:

| Address | Saved signature | Static evidence |
| --- | --- | --- |
| `0x004acde0 CMeshCollisionVolume__InitContactOutputRecord` | `void CMeshCollisionVolume__InitContactOutputRecord(void)` | MeshCollisionVolume contact-output tail block reached by conditional jump from `CMeshCollisionVolume__VFunc_03_004ac6e0` at `0x004acd22`; uses hidden `EBX` as the output record and falls into a parent-style `RET 0x10` epilogue. |
| `0x0056a140 __allshl` | `longlong __fastcall __allshl(byte shift_count, int value_high)` | Visual Studio library-matched signed 64-bit left-shift helper; `shift_count` in `CL`, high dword in the rendered register parameter, low dword hidden in `EAX`, result in `EDX:EAX`. |
| `0x005d0648 __setjmp3` | `int __cdecl __setjmp3(void * jmp_buffer, int unwind_count, void * registration_record, int try_level_or_unwind_value)` | Visual Studio library-matched `__setjmp3`; stores frame/register state, magic `0x56433230`, FS exception-list state, optional registration/unwind fields, and up to six hidden stack dwords. |
| `0x005d06d0 __aullshr` | `ulonglong __fastcall __aullshr(byte shift_count, uint value_high)` | Visual Studio library-matched unsigned 64-bit logical right-shift helper; caller evidence comes from `CMeshCollisionVolume__UnpackTexels_Bits16_16_16_16_ToFloat4` at `0x005854f6`. |

Read-back evidence:

- `ApplySignatureDebtWave795.java dry`: `updated=0 skipped=4 renamed=0 would_rename=0 signature_updated=4 comment_only_updated=0 missing=0 bad=0`
- `ApplySignatureDebtWave795.java apply`: `updated=4 skipped=0 renamed=0 would_rename=0 signature_updated=4 comment_only_updated=0 missing=0 bad=0`, with `REPORT: Save succeeded`.
- `ApplySignatureDebtWave795.java final dry`: `updated=0 skipped=4 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 4 metadata rows, 4 tag rows, 8 xref rows, 180 instruction rows, and 4 decompile rows.
- Queue after Wave795: 6098 total, 5544 commented, 554 commentless, 0 exact-undefined signatures, 11 `param_N`, comment-backed proxy `5544/6098 = 90.92%`, strict clean-signature proxy `5533/6098 = 90.73%`.
- Earliest raw commentless row remains `0x0042f220 CSPtrSet__Clear`.
- The commentless high-signal queue remains empty; next signature-debt head is `0x004bbcd0 CNamedMesh__VFunc_09_004bbcd0`.
- Verified backup: `G:\GhidraBackups\BEA_20260524-043918_post_wave795_final_undefined_signature_debt_verified`, 19 files, 171314055 bytes, `DiffCount=0`.

What this proves:

- The four target function rows exist in the saved Ghidra project.
- The saved signatures/comments/tags match the Wave795 post-export artifacts.
- The `signature-debt-wave795` and `wave795-readback-verified` tags are present on all four targets.
- Current exact-undefined signature debt is zero in the refreshed queue snapshot.

What remains unproven:

- Exact source boundary for the MeshCollisionVolume tail block.
- Exact contact-record layout or hidden EBX/caller-frame ABI.
- Exact Visual Studio CRT source version identity.
- Runtime collision, `setjmp`/SEH, integer shift, or texture unpack behavior.
- BEA patching behavior.
- Rebuild parity.
