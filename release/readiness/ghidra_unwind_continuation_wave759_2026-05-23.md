# Ghidra Unwind Continuation Wave759 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-23
Scope: `unwind-continuation-wave759`

Wave759 unwind continuation saved Ghidra comments, tags, and `void __cdecl Unwind@...(void)` signatures for 25 adjacent compiler-generated SEH unwind cleanup callbacks from `0x005d3bd0 Unwind@005d3bd0` through `0x005d3d7e Unwind@005d3d7e`. The pass made no renames, no function-boundary changes, and no executable-byte changes.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x005d3bd0 Unwind@005d3bd0` | DATA scope-table xref `0x0061c844`; jumps to `CMonitor__Shutdown_Thunk` on `*(EBP-0x10)`. |
| `0x005d3bf8 Unwind@005d3bf8` | DATA scope-table xref `0x0061c874`; jumps to `CSPtrSet__Clear` on the embedded set at `(*(EBP-0x10))+0x18`. |
| `0x005d3c10 Unwind@005d3c10` | DATA scope-table xref `0x0061c89c`; calls `OID__FreeObject_Callback` on `*(EBP-0x68)` with Mine.cpp debug path `0x006309a4`, line token `0x1b`, allocation/type value `0x1f`. |
| `0x005d3c30 Unwind@005d3c30` | DATA scope-table xref `0x0061c8c4`; calls `OID__FreeObject_Callback` on `*(EBP-0x50)` with Mine.cpp debug path `0x006309a4`, line token `0x10`, allocation/type value `0x58`. |
| `0x005d3c50 Unwind@005d3c50` | DATA scope-table xref `0x0061c8ec`; calls `OID__FreeObject_Callback` on `*(EBP-0x10)` with Missile.cpp debug path `0x006309c0`, line token `0x61`, allocation/type value `0x0b`. |
| `0x005d3c70 Unwind@005d3c70` | DATA scope-table xref `0x0061c914`; jumps to `CLine__SetBaseVtable_00426360` for stack-local `EBP-0x144`. |
| `0x005d3cb0 Unwind@005d3cb0` | DATA scope-table xref `0x0061c974`; calls `OID__FreeObject_Callback` on `*(EBP+0x4)` with oids.cpp debug path `0x00630c20`, line token `0x05`, allocation/type value `0x28`. |
| `0x005d3cc6 Unwind@005d3cc6` | DATA scope-table xref `0x0061c97c`; jumps to `CUnit__dtor_base` on `*(EBP+0x4)`. |
| `0x005d3d14 Unwind@005d3d14` | DATA scope-table xref `0x0061c9ac`; jumps to `CGenericActiveReader__dtor` on object field `(*(EBP+0x4))+0x4c8`. |
| `0x005d3d5a Unwind@005d3d5a` | DATA scope-table xref `0x0061c9d4`; jumps to `CParticleManager__RemoveFromGlobalList_Thunk` on object field `(*(EBP+0x4))+0x5f8`. |
| `0x005d3d68 Unwind@005d3d68` | DATA scope-table xref `0x0061c9dc`; calls `OID__FreeObject_Callback` on `*(EBP+0x4)` with oids.cpp debug path `0x00630c20`, line token `0x07`, allocation/type value `0x2b`. |
| `0x005d3d7e Unwind@005d3d7e` | DATA scope-table xref `0x0061c9e4`; calls `OID__FreeObject_Callback` on `*(EBP+0x4)` with oids.cpp debug path `0x00630c20`, line token `0x05`, allocation/type value `0x2d`. |

Read-back evidence:

- `ApplyUnwindContinuationWave759.java dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave759.java apply`: `updated=25 skipped=0 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave759.java final dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 25 metadata rows, 25 tag rows, 25 xref rows, 2625 instruction rows, 25 decompile rows, and 8 helper metadata rows.
- Queue after Wave759: 6098 total, 4837 commented, 1261 commentless, 738 exact-undefined signatures, 27 `param_N`, comment-backed proxy `4837/6098 = 79.32%`, strict clean-signature proxy `4779/6098 = 78.37%`.
- Earliest raw commentless row remains `0x0042f220 CSPtrSet__Clear`.
- Next commentless high-signal row is `0x005d3d94 Unwind@005d3d94`.
- Verified backup: `G:\GhidraBackups\BEA_20260523-130827_post_wave759_unwind_continuation_verified`, 19 files, 168790919 bytes, `DiffCount=0`.

What this proves:

- The 25 target function rows exist in the saved Ghidra project.
- The saved signatures are `void __cdecl Unwind@...(void)` with no parameters.
- The saved comments and tags include `unwind-continuation-wave759` and `wave759-readback-verified`.
- The observed cleanup bodies are static retail Ghidra evidence tied to scope-table DATA xrefs, debug-string dumps, helper metadata, and decompile/instruction exports.

What remains unproven:

- Exact parent source-body identity.
- Runtime exception behavior.
- Runtime cleanup behavior.
- BEA patching behavior.
- Rebuild parity.
