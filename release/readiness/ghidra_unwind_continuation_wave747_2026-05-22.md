# Ghidra Unwind Continuation Wave747 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-22
Scope: `unwind-continuation-wave747`

Wave747 unwind continuation saved Ghidra comments, tags, and `void __cdecl Unwind@...(void)` signatures for 25 adjacent compiler-generated SEH unwind cleanup callbacks from `0x005d1cd9 Unwind@005d1cd9` through `0x005d1fc0 Unwind@005d1fc0`. The pass made no renames, no function-boundary changes, and no executable-byte changes.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x005d1cd9 Unwind@005d1cd9` | DATA scope-table xref `0x0061ab3c`; calls `CSPtrSet__Clear` on embedded object field `*(EBP-0x10)+0x4c`. |
| `0x005d1d20 Unwind@005d1d20` | DATA scope-table xref `0x0061ab94`; calls `OID__FreeObject_Callback` on `EBP-0x10` with WorldPhysicsManager.h debug path `0x00625850`, line `0xe`, memtype `0x94e`. |
| `0x005d1e80 Unwind@005d1e80` | DATA scope-table xref `0x0061acf4`; calls `OID__FreeObject_Callback` on `EBP-0x10` with WorldPhysicsManager.h debug path `0x00625850`, line `0x41`, memtype `0x97f`. |
| `0x005d1f20 Unwind@005d1f20` | DATA scope-table xref `0x0061ad94`; calls `CPhysicsUnitValue__dtor_base` on the pointer at `EBP-0x10`. |
| `0x005d1fc0 Unwind@005d1fc0` | DATA scope-table xref `0x0061ae5c`; calls `CComplexThing__dtor_base` on the pointer at `EBP-0x10`. |

Read-back evidence:

- `ApplyUnwindContinuationWave747.java dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave747.java apply`: `updated=25 skipped=0 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave747.java final dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 25 metadata rows, 25 tag rows, 25 xref rows, 575 instruction rows, and 25 decompile rows.
- Queue after Wave747: 6098 total, 4537 commented, 1561 commentless, 1038 exact-undefined signatures, 27 `param_N`, comment-backed proxy `4537/6098 = 74.40%`, strict clean-signature proxy `4479/6098 = 73.45%`.
- Earliest raw commentless row remains `0x0042f220 CSPtrSet__Clear`.
- Next commentless high-signal row is `0x005d1fc8 Unwind@005d1fc8`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260522-180520_post_wave747_unwind_continuation_verified`, 19 files, 167644039 bytes, `DiffCount=0`.

What this proves:

- The 25 target function rows exist in the saved Ghidra project.
- The saved signatures are `void __cdecl Unwind@...(void)` with no parameters.
- The saved comments and tags include `unwind-continuation-wave747` and `wave747-readback-verified`.
- The observed cleanup bodies are static retail Ghidra evidence tied to scope-table DATA xrefs, debug-string dumps, and decompile/instruction exports.

What remains unproven:

- Exact parent source-body identity.
- Runtime exception behavior.
- Runtime cleanup behavior.
- BEA patching behavior.
- Rebuild parity.
