# Ghidra Unwind Continuation Wave782 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-23
Scope: `unwind-continuation-wave782`

Wave782 unwind continuation saved Ghidra comments, tags, and `void __cdecl ... (void)` signatures for 25 adjacent compiler-generated SEH unwind cleanup callbacks from `0x005d7080 Unwind@005d7080` through `0x005d7278 Unwind@005d7278`. The pass made no renames, no function-boundary changes, and no executable-byte changes.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x005d7080 Unwind@005d7080` | DATA scope-table xref `0x0061f56c`; `OID__FreeObject_Callback` on `*(EBP-0x10)`. |
| `0x005d70f0 Unwind@005d70f0` | DATA scope-table xref `0x0061f5c4`; `OID__FreeObject_Callback` on `*(EBP+0x4)`. |
| `0x005d7109 Unwind@005d7109` | DATA scope-table xref `0x0061f5cc`; `CDataType__Destructor` on `*(EBP+0x4)`. |
| `0x005d7111 Unwind@005d7111` | DATA scope-table xref `0x0061f5d4`; `CGenericActiveReader__dtor` on `*(EBP-0x14)`. |
| `0x005d7180 Unwind@005d7180` | DATA scope-table xref `0x0061f624`; `OID__FreeObject_Callback` on `*(EBP-0x18)`. |
| `0x005d71e9 Unwind@005d71e9` | DATA scope-table xref `0x0061f66c`; `CDataType__Destructor` on `*(EBP-0x18)`. |
| `0x005d7241 Unwind@005d7241` | DATA scope-table xref `0x0061f6b4`; `CGenericActiveReader__dtor` on `*(EBP-0x14)`. |
| `0x005d7278 Unwind@005d7278` | DATA scope-table xref `0x0061f6cc`; `CDataType__Destructor` on `*(EBP-0x18)`. |

Read-back evidence:

- `ApplyUnwindContinuationWave782.java dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave782.java apply`: `updated=25 skipped=0 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave782.java final dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 25 metadata rows, 25 tag rows, 25 xref rows, 1225 instruction rows, 25 decompile rows, and 3 helper metadata rows.
- Queue after Wave782: 6098 total, 5412 commented, 686 commentless, 163 exact-undefined signatures, 27 `param_N`, comment-backed proxy `5412/6098 = 88.75%`, strict clean-signature proxy `5354/6098 = 87.80%`.
- Earliest raw commentless row remains `0x0042f220 CSPtrSet__Clear`.
- Next commentless high-signal row is `0x005d7280 Unwind@005d7280`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260523-224558_post_wave782_unwind_continuation_verified`, 19 files, 170822535 bytes, `DiffCount=0`.

What this proves:

- The 25 target function rows exist in the saved Ghidra project.
- The saved signatures are `void __cdecl ... (void)` with no parameters.
- The saved comments and tags include `unwind-continuation-wave782` and `wave782-readback-verified`.
- The observed cleanup bodies are static retail Ghidra evidence tied to scope-table DATA xrefs, helper metadata, and decompile/instruction exports.

What remains unproven:

- Exact parent source-body identity.
- Runtime exception behavior.
- Runtime cleanup behavior.
- BEA patching behavior.
- Rebuild parity.
