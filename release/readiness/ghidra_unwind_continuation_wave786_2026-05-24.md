# Ghidra Unwind Continuation Wave786 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-24
Scope: `unwind-continuation-wave786`

Wave786 unwind continuation saved Ghidra comments, tags, and `void __cdecl ... (void)` signatures for 25 adjacent compiler-generated SEH unwind cleanup callbacks from `0x005d7a96 Unwind@005d7a96` through `0x005d7d09 Unwind@005d7d09`. The pass made no renames, no function-boundary changes, and no executable-byte changes.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x005d7a96 Unwind@005d7a96` | DATA scope-table xref `0x0061fdf4`; `DebugTrace` on `(*(EBP-0x10))+0xae0 via ECX before jumping to the retail stub`. |
| `0x005d7ac0 Unwind@005d7ac0` | DATA scope-table xref `0x0061fe24`; `CMemoryManager__DeleteTagList` on `*(EBP-0x10)`. |
| `0x005d7b40 Unwind@005d7b40` | DATA scope-table xref `0x0061feb4`; `CDXMemBuffer__dtor_base` on `EBP-0x140`. |
| `0x005d7b60 Unwind@005d7b60` | DATA scope-table xref `0x0061fee4`; `CFrontEndPage__DeActiveNotification` on `the deactivating front-end page pointer`. |
| `0x005d7b80 Unwind@005d7b80` | DATA scope-table xref `0x0061ff0c`; `OID__FreeObject_Callback` on `*(EBP+0x4)`. |
| `0x005d7bf8 Unwind@005d7bf8` | DATA scope-table xref `0x0061ff54`; `CRT__EhVectorDestructorIterator_WithUnwind` on `the 0x20-element CGenericActiveReader array at (*(EBP-0x10))+0x0c`. |
| `0x005d7c28 Unwind@005d7c28` | DATA scope-table xref `0x0061ff84`; `CRT__EhVectorDestructorIterator_WithUnwind` on `the 0x20-element CGenericActiveReader array at (*(EBP-0x10))+0x0c`. |
| `0x005d7d09 Unwind@005d7d09` | DATA scope-table xref `0x00620054`; `OID__FreeObject_Callback` on `*(EBP-0x10)`. |

Read-back evidence:

- `ApplyUnwindContinuationWave786.java dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave786.java apply`: `updated=25 skipped=0 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave786.java final dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 25 metadata rows, 25 tag rows, 25 xref rows, 2125 instruction rows, 25 decompile rows, and 8 helper metadata rows.
- Queue after Wave786: 6098 total, 5512 commented, 586 commentless, 63 exact-undefined signatures, 27 `param_N`, comment-backed proxy `5512/6098 = 90.39%`, strict clean-signature proxy `5454/6098 = 89.44%`.
- Earliest raw commentless row remains `0x0042f220 CSPtrSet__Clear`.
- Next commentless high-signal row is `0x005d7d30 Unwind@005d7d30`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260524-005950_post_wave786_unwind_continuation_verified`, 19 files, 171150215 bytes, `DiffCount=0`.

What this proves:

- The 25 target function rows exist in the saved Ghidra project.
- The saved signatures are `void __cdecl ... (void)` with no parameters.
- The saved comments and tags include `unwind-continuation-wave786` and `wave786-readback-verified`.
- The observed cleanup bodies are static retail Ghidra evidence tied to scope-table DATA xrefs, helper metadata, and decompile/instruction exports.

What remains unproven:

- Exact parent source-body identity.
- Runtime exception behavior.
- Runtime cleanup behavior.
- BEA patching behavior.
- Rebuild parity.
