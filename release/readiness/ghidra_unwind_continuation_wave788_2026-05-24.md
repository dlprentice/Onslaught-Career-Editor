# Ghidra Unwind Continuation Wave788 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-24
Scope: `unwind-continuation-wave788`

Wave788 unwind continuation saved Ghidra comments, tags, and `void __cdecl Unwind@...(void)` signatures for 7 adjacent compiler-generated SEH unwind cleanup callbacks from `0x005d7f20 Unwind@005d7f20` through `0x005d7f7e Unwind@005d7f7e`. The pass made no renames, no function-boundary changes, and no executable-byte changes.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x005d7f20 Unwind@005d7f20` | DATA scope-table xref `0x00620258`; `CFastVB__ReleaseBufferAndResetTriplet_0056f260` on `EBP-0x2c`. |
| `0x005d7f40 Unwind@005d7f40` | DATA scope-table xref `0x0062027c`; `CFastVB__ReleaseBufferAndResetTriplet_0056f260` on `EBP-0x1c`. |
| `0x005d7f48 Unwind@005d7f48` | DATA scope-table xref `0x00620284`; `OID__FreeObject_Callback` on `*(EBP-0x48)`. |
| `0x005d7f53 Unwind@005d7f53` | DATA scope-table xref `0x0062028c`; `CFastVB__ReleaseBufferAndResetTriplet_0056f260` on `EBP-0x2c`. |
| `0x005d7f5b Unwind@005d7f5b` | DATA scope-table xref `0x00620294`; `OID__FreeObject_Callback` on `*(EBP-0x48)`. |
| `0x005d7f70 Unwind@005d7f70` | DATA scope-table xref `0x006202b8`; `OID__FreeObject_Callback` on `*(EBP-0xdc)`. |
| `0x005d7f7e Unwind@005d7f7e` | DATA scope-table xref `0x006202c0`; `CTexture__DestroyNodeTreeAndStorage` on `EBP-0xb4`. |

Read-back evidence:

- `ApplyUnwindContinuationWave788.java dry`: `updated=0 skipped=7 renamed=0 would_rename=0 signature_updated=7 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave788.java apply`: `updated=7 skipped=0 renamed=0 would_rename=0 signature_updated=7 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave788.java final dry`: `updated=0 skipped=7 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 7 metadata rows, 7 tag rows, 7 xref rows, 214 instruction rows, 7 decompile rows, and 3 helper metadata rows.
- Queue after Wave788: 6098 total, 5544 commented, 554 commentless, 31 exact-undefined signatures, 27 `param_N`, comment-backed proxy `5544/6098 = 90.92%`, strict clean-signature proxy `5486/6098 = 89.96%`, raw commentless head `0x0042f220 CSPtrSet__Clear`, and the commentless high-signal queue is empty.
- Earliest raw commentless row remains `0x0042f220 CSPtrSet__Clear`.
- The commentless high-signal queue is empty after Wave788.
- Verified backup: `G:\GhidraBackups\BEA_20260524-014707_post_wave788_unwind_continuation_verified`, 19 files, 171215751 bytes, `DiffCount=0`.

What this proves:

- The 7 target function rows exist in the saved Ghidra project.
- The saved signatures are `void __cdecl Unwind@...(void)` with no parameters.
- The saved comments and tags include `unwind-continuation-wave788` and `wave788-readback-verified`.
- The observed cleanup bodies are static retail Ghidra evidence tied to scope-table DATA xrefs, helper metadata, and decompile/instruction exports.

What remains unproven:

- Exact parent source-body identity.
- Runtime exception behavior.
- Runtime cleanup behavior.
- BEA patching behavior.
- Rebuild parity.
