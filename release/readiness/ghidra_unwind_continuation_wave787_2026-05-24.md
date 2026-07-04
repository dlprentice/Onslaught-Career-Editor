# Ghidra Unwind Continuation Wave787 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-24
Scope: `unwind-continuation-wave787`

Wave787 unwind continuation saved Ghidra comments, tags, and `void __cdecl ... (void)` signatures for 25 adjacent compiler-generated SEH unwind cleanup callbacks from `0x005d7d30 Unwind@005d7d30` through `0x005d7f18 Unwind@005d7f18`. The pass made no renames, no function-boundary changes, and no executable-byte changes.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x005d7d30 Unwind@005d7d30` | DATA scope-table xref `0x0062007c`; `CDXSurf__UnlinkNodeFromGlobalList` on `(*(EBP-0x10))+0x8`. |
| `0x005d7d50 Unwind@005d7d50` | DATA scope-table xref `0x006200ac`; `CDXSurf__UnlinkNodeFromGlobalList` on `conditional CDXSurf node pointer derived from (*(EBP-0x110))+0x8 or null at EBP-0x114`. |
| `0x005d7da0 Unwind@005d7da0` | DATA scope-table xref `0x006200dc`; `CDXMemBuffer__dtor_base` on `EBP-0x244`. |
| `0x005d7dc0 CDXTexture__Deserialize_Unwind` | DATA scope-table xref `0x00620104`; `OID__FreeObject_Callback` on `*(EBP-0x168) with DXTexture.cpp debug path 0x0065269c, line token 0xc25, and allocation/type value 0x2`. |
| `0x005d7df0 Unwind@005d7df0` | DATA scope-table xref `0x0062012c`; `OID__FreeObject_Callback` on `*(EBP-0xc8) with DXTrees.cpp debug path 0x006529b0, line token 0x5e, and allocation/type value 0x1f`. |
| `0x005d7e70 Unwind@005d7e70` | DATA scope-table xref `0x0062018c`; `CFastVB__ReleaseBufferAndResetTriplet_0056f260` on `EBP-0x3c`. |
| `0x005d7e98 Unwind@005d7e98` | DATA scope-table xref `0x006201b4`; `OID__FreeObject_Callback` on `*(EBP+0x10)`. |
| `0x005d7f18 Unwind@005d7f18` | DATA scope-table xref `0x00620250`; `CFastVB__ReleaseBufferAndResetTriplet_0056f260` on `EBP-0x3c`. |

Read-back evidence:

- `ApplyUnwindContinuationWave787.java dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave787.java apply`: `updated=25 skipped=0 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave787.java final dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 25 metadata rows, 25 tag rows, 25 xref rows, 925 instruction rows, 25 decompile rows, 6 helper metadata rows, and 2 debug-string dump rows.
- Queue after Wave787: 6098 total, 5537 commented, 561 commentless, 38 exact-undefined signatures, 27 `param_N`, comment-backed proxy `5537/6098 = 90.80%`, strict clean-signature proxy `5479/6098 = 89.85%`.
- Earliest raw commentless row remains `0x0042f220 CSPtrSet__Clear`.
- Next commentless high-signal row is `0x005d7f20 Unwind@005d7f20`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260524-012644_post_wave787_unwind_continuation_verified`, 19 files, 171182983 bytes, `DiffCount=0`.

What this proves:

- The 25 target function rows exist in the saved Ghidra project.
- The saved signatures are `void __cdecl ... (void)` with no parameters.
- The saved comments and tags include `unwind-continuation-wave787` and `wave787-readback-verified`.
- The observed cleanup bodies are static retail Ghidra evidence tied to scope-table DATA xrefs, helper metadata, and decompile/instruction exports.

What remains unproven:

- Exact parent source-body identity.
- Runtime exception behavior.
- Runtime cleanup behavior.
- BEA patching behavior.
- Rebuild parity.
