# Ghidra Unwind Continuation Wave746 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-22
Scope: `unwind-continuation-wave746`

Wave746 unwind continuation saved Ghidra comments, tags, and `void __cdecl Unwind@...(void)` signatures for 25 adjacent compiler-generated SEH unwind cleanup callbacks from `0x005d1aa3 Unwind@005d1aa3` through `0x005d1cc0 Unwind@005d1cc0`. The pass made no renames, no function-boundary changes, and no executable-byte changes.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x005d1aa3 Unwind@005d1aa3` | DATA scope-table xref `0x0061a914`; calls `CGenericActiveReader__dtor` on embedded object field `*(EBP-0x10)+0x24`. |
| `0x005d1b26 Unwind@005d1b26` | DATA scope-table xref `0x0061a9ac`; calls `OID__FreeObject_Callback` on `EBP-0x14` with Controller.cpp debug path `0x00625538`, line `0x27`, memtype `0x3c7`. |
| `0x005d1b47 Unwind@005d1b47` | DATA scope-table xref `0x0061a9bc`; calls `OID__FreeObject_Callback` on `EBP-0x10` with monitor.h debug path `0x0062551c`, line `0x5e`, memtype `0x18`. |
| `0x005d1be0 Unwind@005d1be0` | DATA scope-table xref `0x0061aa4c`; calls `OID__FreeObject_Callback` on `EBP-0x10` with CPhysicsScript.cpp debug path `0x0062568c`, line `0x18`, memtype `0x10`. |
| `0x005d1c00 Unwind@005d1c00` | DATA scope-table xref `0x0061aa74`; calls `OID__FreeObject_Callback` on `EBP-0x10` with WorldPhysicsManager.h debug path `0x00625850`, line `0xf`, memtype `0x971`. |
| `0x005d1cc0 Unwind@005d1cc0` | DATA scope-table xref `0x0061ab34`; calls `OID__FreeObject_Callback` on `EBP-0x10` with WorldPhysicsManager.h debug path `0x00625850`, line `0x3c`, memtype `0x955`. |

Read-back evidence:

- `ApplyUnwindContinuationWave746.java dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave746.java apply`: `updated=25 skipped=0 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave746.java final dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 25 metadata rows, 25 tag rows, 25 xref rows, 575 instruction rows, and 25 decompile rows.
- Queue after Wave746: 6098 total, 4512 commented, 1586 commentless, 1063 exact-undefined signatures, 27 `param_N`, comment-backed proxy `4512/6098 = 73.99%`, strict clean-signature proxy `4454/6098 = 73.04%`.
- Earliest raw commentless row remains `0x0042f220 CSPtrSet__Clear`.
- Next commentless high-signal row is `0x005d1cd9 Unwind@005d1cd9`.
- Verified backup: `G:\GhidraBackups\BEA_20260522-173500_post_wave746_unwind_continuation_verified`, 19 files, 167578503 bytes, `DiffCount=0`.

What this proves:

- The 25 target function rows exist in the saved Ghidra project.
- The saved signatures are `void __cdecl Unwind@...(void)` with no parameters.
- The saved comments and tags include `unwind-continuation-wave746` and `wave746-readback-verified`.
- The observed cleanup bodies are static retail Ghidra evidence tied to scope-table DATA xrefs, debug-string dumps, and decompile/instruction exports.

What remains unproven:

- Exact parent source-body identity.
- Runtime exception behavior.
- Runtime cleanup behavior.
- BEA patching behavior.
- Rebuild parity.
