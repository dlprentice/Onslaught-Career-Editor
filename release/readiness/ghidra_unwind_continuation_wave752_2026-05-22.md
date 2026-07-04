# Ghidra Unwind Continuation Wave752 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-22
Scope: `unwind-continuation-wave752`

Wave752 unwind continuation saved Ghidra comments, tags, and `void __cdecl Unwind@...(void)` signatures for 25 adjacent compiler-generated SEH unwind cleanup callbacks from `0x005d29f1 Unwind@005d29f1` through `0x005d2c40 Unwind@005d2c40`. The pass made no renames, no function-boundary changes, and no executable-byte changes.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x005d29f1 Unwind@005d29f1` | DATA scope-table xref `0x0061b7cc`; calls `OID__FreeObject_Callback` for game.cpp debug path `0x0062bba4`, line `0x27`, allocation/type value `0x11bf`, pointer `*(EBP-0x1c)`. |
| `0x005d2a20 Unwind@005d2a20` | DATA scope-table xref `0x0061b7f4`; calls `OID__FreeObject_Callback` for GillM.cpp debug path `0x0062c9e8`, line `0x1b`, allocation/type value `0x2d`, pointer `*(EBP-0x10)`. |
| `0x005d2a60 Unwind@005d2a60` | DATA scope-table xref `0x0061b844`; calls `CMonitor__Shutdown` on `*(EBP-0x10)` in the GillM.cpp-adjacent scope-table run. |
| `0x005d2ab0 Unwind@005d2ab0` | DATA scope-table xref `0x0061b8a4`; calls `OID__FreeObject_Callback` for GillMHead.cpp debug path `0x0062ca6c`, line `0x16`, allocation/type value `0x13`, pointer `*(EBP-0x10)`. |
| `0x005d2b00 Unwind@005d2b00` | DATA scope-table xref `0x0061b904`; calls `OID__FreeObject_Callback` for GroundAttackAircraft.cpp debug path `0x0062cadc`, line `0x1b`, allocation/type value `0x13`, pointer `*(EBP+0x4)`. |
| `0x005d2b2c Unwind@005d2b2c` | DATA scope-table xref `0x0061b914`; calls `CUnitAI__dtor_body_00415080` on `*(EBP+0x4)`. |
| `0x005d2bb0 Unwind@005d2bb0` | DATA scope-table xref `0x0061b9a4`; calls `OID__FreeObject_Callback` for GroundUnit.cpp debug path `0x0062cb0c`, line `0x10`, allocation/type value `0x23`, pointer `*(EBP+0x4)`. |
| `0x005d2c12 Unwind@005d2c12` | DATA scope-table xref `0x0061b9e4`; calls `OID__FreeObject_Callback` for GroundVehicle.cpp debug path `0x0062cb30`, line `0x16`, allocation/type value `0x25`, pointer `*(EBP+0x4)`. |
| `0x005d2c40 Unwind@005d2c40` | DATA scope-table xref `0x0061ba0c`; calls `CMonitor__Shutdown_Thunk` on `*(EBP-0x10)` in the GroundVehicle.cpp-adjacent scope-table run. |

Read-back evidence:

- `ApplyUnwindContinuationWave752.java dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave752.java apply`: `updated=25 skipped=0 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave752.java final dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 25 metadata rows, 25 tag rows, 25 xref rows, 725 instruction rows, and 25 decompile rows.
- Queue after Wave752: 6098 total, 4662 commented, 1436 commentless, 913 exact-undefined signatures, 27 `param_N`, comment-backed proxy `4662/6098 = 76.45%`, strict clean-signature proxy `4604/6098 = 75.50%`.
- Earliest raw commentless row remains `0x0042f220 CSPtrSet__Clear`.
- Next commentless high-signal row is `0x005d2c48 Unwind@005d2c48`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260522-212829_post_wave752_unwind_continuation_verified`, 19 files, 168102791 bytes, `DiffCount=0`.

What this proves:

- The 25 target function rows exist in the saved Ghidra project.
- The saved signatures are `void __cdecl Unwind@...(void)` with no parameters.
- The saved comments and tags include `unwind-continuation-wave752` and `wave752-readback-verified`.
- The observed cleanup bodies are static retail Ghidra evidence tied to scope-table DATA xrefs, debug-string dumps, helper metadata, and decompile/instruction exports.

What remains unproven:

- Exact parent source-body identity.
- Runtime exception behavior.
- Runtime cleanup behavior.
- BEA patching behavior.
- Rebuild parity.
