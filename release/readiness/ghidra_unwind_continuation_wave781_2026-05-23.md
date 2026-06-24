# Ghidra Unwind Continuation Wave781 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-23
Scope: `unwind-continuation-wave781`

Wave781 unwind continuation saved Ghidra comments, tags, and `void __cdecl ... (void)` signatures for 25 adjacent compiler-generated SEH unwind cleanup callbacks from `0x005d6d80 Unwind@005d6d80` through `0x005d7059 Unwind@005d7059`. The pass made no renames, no function-boundary changes, and no executable-byte changes.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x005d6d80 Unwind@005d6d80` | DATA scope-table xref `0x0061f364`; `OID__FreeObject_Callback` on `*(EBP-0x10)`. |
| `0x005d6db0 Unwind@005d6db0` | DATA scope-table xref `0x0061f38c`; `OID__FreeObject_Callback` on `*(EBP-0x30)`. |
| `0x005d6f10 Unwind@005d6f10` | DATA scope-table xref `0x0061f434`; `OID__FreeObject_Callback` on `*(EBP-0x20)`. |
| `0x005d6f59 Unwind@005d6f59` | DATA scope-table xref `0x0061f464`; `CDataType__Destructor` on `*(EBP+0x4)`. |
| `0x005d6f61 Unwind@005d6f61` | DATA scope-table xref `0x0061f46c`; `CGenericActiveReader__dtor` on `*(EBP-0x14)`. |
| `0x005d7020 Unwind@005d7020` | DATA scope-table xref `0x0061f514`; `CMonitor__Shutdown` on `*(EBP-0x10)`. |
| `0x005d7040 Unwind@005d7040` | DATA scope-table xref `0x0061f53c`; `OID__FreeObject_Callback` on `*(EBP-0x10)`. |
| `0x005d7059 Unwind@005d7059` | DATA scope-table xref `0x0061f544`; `OID__FreeObject_Callback` on `*(EBP-0x10)`. |

Read-back evidence:

- `ApplyUnwindContinuationWave781.java dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave781.java apply`: `updated=25 skipped=0 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave781.java final dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 25 metadata rows, 25 tag rows, 25 xref rows, 1225 instruction rows, 25 decompile rows, and 4 helper metadata rows.
- Queue after Wave781: 6098 total, 5387 commented, 711 commentless, 188 exact-undefined signatures, 27 `param_N`, comment-backed proxy `5387/6098 = 88.34%`, strict clean-signature proxy `5329/6098 = 87.39%`.
- Earliest raw commentless row remains `0x0042f220 CSPtrSet__Clear`.
- Next commentless high-signal row is `0x005d7080 Unwind@005d7080`.
- Verified backup: `G:\GhidraBackups\BEA_20260523-222816_post_wave781_unwind_continuation_verified`, 19 files, 170724231 bytes, `DiffCount=0`.

What this proves:

- The 25 target function rows exist in the saved Ghidra project.
- The saved signatures are `void __cdecl ... (void)` with no parameters.
- The saved comments and tags include `unwind-continuation-wave781` and `wave781-readback-verified`.
- The observed cleanup bodies are static retail Ghidra evidence tied to scope-table DATA xrefs, helper metadata, and decompile/instruction exports.

What remains unproven:

- Exact parent source-body identity.
- Runtime exception behavior.
- Runtime cleanup behavior.
- BEA patching behavior.
- Rebuild parity.
