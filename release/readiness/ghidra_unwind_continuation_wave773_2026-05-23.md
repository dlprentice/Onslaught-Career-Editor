# Ghidra Unwind Continuation Wave773 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-23
Scope: `unwind-continuation-wave773`

Wave773 unwind continuation saved Ghidra comments, tags, and `void __cdecl Unwind@...(void)` signatures for 25 adjacent compiler-generated SEH unwind cleanup callbacks from `0x005d5b45 Unwind@005d5b45` through `0x005d5d8e Unwind@005d5d8e`. The pass made no renames, no function-boundary changes, and no executable-byte changes.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x005d5b45 Unwind@005d5b45` | DATA scope-table xref `0x0061e344`; `CSPtrSet__Clear` on `(*(EBP-0x10))+0x100`. |
| `0x005d5b70 Unwind@005d5b70` | DATA scope-table xref `0x0061e374`; `OID__FreeObject_Callback` on `*(EBP-0x1c)`. |
| `0x005d5bb0 Unwind@005d5bb0` | DATA scope-table xref `0x0061e3a4`; `CLine__SetBaseVtable_00426360` on the stack/object cell at `EBP+0x4`. |
| `0x005d5bd0 Unwind@005d5bd0` | DATA scope-table xref `0x0061e3cc`; `CDXMemBuffer__dtor_base` on the stack-local buffer at `EBP-0x308`. |
| `0x005d5c09 Unwind@005d5c09` | DATA scope-table xref `0x0061e3fc`; `CMonitor__Shutdown` on `*(EBP+0x4)`. |
| `0x005d5c87 Unwind@005d5c87` | DATA scope-table xref `0x0061e474`; `CSPtrSet__Clear` on `(*(EBP-0x38c4))+0x8`. |
| `0x005d5d8e Unwind@005d5d8e` | DATA scope-table xref `0x0061e524`; `CUnit__dtor_base_Thunk_004bfe00` on `*(EBP+0x4)`. |

Read-back evidence:

- `ApplyUnwindContinuationWave773.java dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave773.java apply`: `updated=25 skipped=0 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave773.java final dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 25 metadata rows, 25 tag rows, 25 xref rows, 3025 instruction rows, 25 decompile rows, and 6 helper metadata rows.
- Queue after Wave773: 6098 total, 5187 commented, 911 commentless, 388 exact-undefined signatures, 27 `param_N`, comment-backed proxy `5187/6098 = 85.06%`, strict clean-signature proxy `5129/6098 = 84.11%`.
- Earliest raw commentless row remains `0x0042f220 CSPtrSet__Clear`.
- Next commentless high-signal row is `0x005d5d96 Unwind@005d5d96`.
- Verified backup: `G:\GhidraBackups\BEA_20260523-192621_post_wave773_unwind_continuation_verified`, 19 files, 170068871 bytes, `DiffCount=0`.

What this proves:

- The 25 target function rows exist in the saved Ghidra project.
- The saved signatures are `void __cdecl Unwind@...(void)` with no parameters.
- The saved comments and tags include `unwind-continuation-wave773` and `wave773-readback-verified`.
- The observed cleanup bodies are static retail Ghidra evidence tied to scope-table DATA xrefs, helper metadata, and decompile/instruction exports.

What remains unproven:

- Exact parent source-body identity.
- Runtime exception behavior.
- Runtime cleanup behavior.
- BEA patching behavior.
- Rebuild parity.
