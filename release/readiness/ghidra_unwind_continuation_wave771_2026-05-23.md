# Ghidra Unwind Continuation Wave771 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-23
Scope: `unwind-continuation-wave771`

Wave771 unwind continuation saved Ghidra comments, tags, and `void __cdecl Unwind@...(void)` signatures for 25 compiler-generated SEH unwind cleanup callbacks from `0x005d5810 Unwind@005d5810` through `0x005d59e5 Unwind@005d59e5`. The pass made no renames, no function-boundary changes, and no executable-byte changes.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x005d5810 Unwind@005d5810` | DATA scope-table xref `0x0061e06c`; calls `CMonitor__Shutdown` on the monitor object at `*(EBP-0x10)`. |
| `0x005d5818 Unwind@005d5818` | DATA scope-table xref `0x0061e074`; calls `CGenericActiveReader__dtor` on the active-reader subobject at `(*(EBP-0x10))+0x0c`. |
| `0x005d5840 Unwind@005d5840` | DATA scope-table xref `0x0061e0a4`; calls `CWaveSoundRead__BaseConstructor` on `*(EBP-0x10)`; exact constructor/destructor role remains unproven. |
| `0x005d58a8 Unwind@005d58a8` | DATA scope-table xref `0x0061e124`; calls `CRT__EhVectorDestructorIterator_WithUnwind` for two 8-byte particle-list entries with `CParticleManager__RemoveFromGlobalList_Thunk`. |
| `0x005d5910 Unwind@005d5910` | DATA scope-table xref `0x0061e184`; calls `CParticleManager__RemoveFromGlobalList_Thunk` on stack-local node `EBP-0xa54`. |
| `0x005d5930 Unwind@005d5930` | DATA scope-table xref `0x0061e1ac`; calls `CLine__SetBaseVtable_00426360` on stack-local object `EBP-0x14c`. |
| `0x005d5970 Unwind@005d5970` | DATA scope-table xref `0x0061e1ec`; calls `CLine__SetBaseVtable_00426360` on stack-local object `EBP-0xc0`. |
| `0x005d5990 Unwind@005d5990` | DATA scope-table xref `0x0061e214`; calls `CSPtrSet__Clear` on `*(EBP-0x10)`. |
| `0x005d59e5 Unwind@005d59e5` | DATA scope-table xref `0x0061e254`; calls `CSPtrSet__Clear` on the subobject at `(*(EBP-0x10))+0x80`. |

Read-back evidence:

- `ApplyUnwindContinuationWave771.java dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave771.java apply`: `updated=25 skipped=0 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave771.java final dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 25 metadata rows, 25 tag rows, 25 xref rows, 2325 instruction rows, 25 decompile rows, and 9 helper metadata rows.
- Queue after Wave771: 6098 total, 5137 commented, 961 commentless, 438 exact-undefined signatures, 27 `param_N`, comment-backed proxy `5137/6098 = 84.24%`, strict clean-signature proxy `5079/6098 = 83.29%`.
- Earliest raw commentless row remains `0x0042f220 CSPtrSet__Clear`.
- Next commentless high-signal row is `0x005d59f3 Unwind@005d59f3`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260523-183606_post_wave771_unwind_continuation_verified`, 19 files, 169872263 bytes, `DiffCount=0`.

What this proves:

- The 25 target function rows exist in the saved Ghidra project.
- The saved signatures are `void __cdecl Unwind@...(void)` with no parameters.
- The saved comments and tags include `unwind-continuation-wave771` and `wave771-readback-verified`.
- The observed cleanup bodies are static retail Ghidra evidence tied to scope-table DATA xrefs, helper metadata, instruction exports, and decompile exports.

What remains unproven:

- Exact parent source-body identity.
- Runtime exception behavior.
- Runtime cleanup behavior.
- BEA patching behavior.
- Rebuild parity.
