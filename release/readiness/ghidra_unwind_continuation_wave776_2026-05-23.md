# Ghidra Unwind Continuation Wave776 Readiness Note

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 semantic revalidation:** Historical record; `0x004df520` → `CActor__dtor_base_Thunk` (was `CActor__dtor_base`). The original text below remains provenance rather than current semantic authority. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); exact records are in `reverse-engineering/binary-analysis/ghidra-full-reaudit-corrections-2026-07-13.json` and `reverse-engineering/binary-analysis/ghidra-targeted-revalidation-corrections-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Status: complete static read-back evidence
Date: 2026-05-23
Scope: `unwind-continuation-wave776`

Wave776 unwind continuation saved Ghidra comments, tags, and `void __cdecl Unwind@...(void)` signatures for 25 adjacent compiler-generated SEH unwind cleanup callbacks from `0x005d6150 Unwind@005d6150` through `0x005d635c Unwind@005d635c`. The pass made no renames, no function-boundary changes, and no executable-byte changes.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x005d6150 Unwind@005d6150` | DATA scope-table xref `0x0061e83c`; `CUnit__dtor_base` on `*(EBP-0x10)`. |
| `0x005d6158 Unwind@005d6158` | DATA scope-table xref `0x0061e844`; `CParticleManager__RemoveFromGlobalList_Thunk` on `(*(EBP-0x10))+0x250`. |
| `0x005d6166 Unwind@005d6166` | DATA scope-table xref `0x0061e84c`; `CSPtrSet__Clear` on `(*(EBP-0x10))+0x25c`. |
| `0x005d61b0 Unwind@005d61b0` | DATA scope-table xref `0x0061e8ac`; `OID__FreeObject_Callback` on `*(EBP+0x4)`. |
| `0x005d61c9 Unwind@005d61c9` | DATA scope-table xref `0x0061e8b4`; `CComplexThing__dtor_base_Thunk_004bff30` on `*(EBP+0x4)`. |
| `0x005d6290 Unwind@005d6290` | DATA scope-table xref `0x0061e964`; `CActor__dtor_base` on `*(EBP-0x10)`. |
| `0x005d62a6 Unwind@005d62a6` | DATA scope-table xref `0x0061e974`; `CGenericActiveReader__dtor` on `(*(EBP-0x10))+0xe8`. |
| `0x005d6309 Unwind@005d6309` | DATA scope-table xref `0x0061e9cc`; `CUnit__dtor_base` on `*(EBP+0x4)`. |
| `0x005d635c Unwind@005d635c` | DATA scope-table xref `0x0061e9fc`; `CGenericActiveReader__dtor` on `(*(EBP+0x4))+0x26c`. |

Read-back evidence:

- `ApplyUnwindContinuationWave776.java dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave776.java apply`: `updated=25 skipped=0 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave776.java final dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 25 metadata rows, 25 tag rows, 25 xref rows, 3025 instruction rows, 25 decompile rows, and 7 helper metadata rows.
- Queue after Wave776: 6098 total, 5262 commented, 836 commentless, 313 exact-undefined signatures, 27 `param_N`, comment-backed proxy `5262/6098 = 86.29%`, strict clean-signature proxy `5204/6098 = 85.34%`.
- Earliest raw commentless row remains `0x0042f220 CSPtrSet__Clear`.
- Next commentless high-signal row is `0x005d636a Unwind@005d636a`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260523-203857_post_wave776_unwind_continuation_verified`, 19 files, 170298247 bytes, `DiffCount=0`.

What this proves:

- The 25 target function rows exist in the saved Ghidra project.
- The saved signatures are `void __cdecl Unwind@...(void)` with no parameters.
- The saved comments and tags include `unwind-continuation-wave776` and `wave776-readback-verified`.
- The observed cleanup bodies are static retail Ghidra evidence tied to scope-table DATA xrefs, helper metadata, and decompile/instruction exports.

What remains unproven:

- Exact parent source-body identity.
- Runtime exception behavior.
- Runtime cleanup behavior.
- BEA patching behavior.
- Rebuild parity.
