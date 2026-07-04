# Ghidra Unwind Continuation Wave750 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-22
Scope: `unwind-continuation-wave750`

Wave750 unwind continuation saved Ghidra comments, tags, and `void __cdecl Unwind@...(void)` signatures for 25 adjacent compiler-generated SEH unwind cleanup callbacks from `0x005d24e0 Unwind@005d24e0` through `0x005d270f Unwind@005d270f`. The pass made no renames, no function-boundary changes, and no executable-byte changes.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x005d24e0 Unwind@005d24e0` | DATA scope-table xref `0x0061b334`; calls `OID__FreeObject_Callback` for eventmanager.cpp debug path `0x00628d3c`, line `0x43`, allocation/type value `0x34`. |
| `0x005d2580 Unwind@005d2580` | DATA scope-table xref `0x0061b3ec`; calls `CDXLandscape__DestroyResourceDescriptorArray_Thunk` on stack-local descriptors at `EBP-0x434`. |
| `0x005d25e0 Unwind@005d25e0` | DATA scope-table xref `0x0061b464`; calls `OID__FreeObject_Callback` for FEPBEConfig.cpp debug path `0x00628fac`, line `0x80`, allocation/type value `0x18f`. |
| `0x005d2630 Unwind@005d2630` | DATA scope-table xref `0x0061b4b4`; calls `OID__FreeObject_Callback` for FEPDebriefing.cpp debug path `0x0062913c`, line `0x80`, allocation/type value `0x30`. |
| `0x005d26e0 Unwind@005d26e0` | DATA scope-table xref `0x0061b55c`; calls `CMonitor__Shutdown_Thunk` on the object pointer at `*(EBP-0x10)` in the FrontEnd.cpp-adjacent cleanup run. |
| `0x005d270f Unwind@005d270f` | DATA scope-table xref `0x0061b57c`; calls `CFEPMultiplayerStart__ClearSecondaryPlayerSet` on the subobject at `(*(EBP-0x10))+0x2ec`. |

Read-back evidence:

- `ApplyUnwindContinuationWave750.java dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave750.java apply`: `updated=25 skipped=0 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave750.java final dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 25 metadata rows, 25 tag rows, 25 xref rows, 725 instruction rows, and 25 decompile rows.
- Queue after Wave750: 6098 total, 4612 commented, 1486 commentless, 963 exact-undefined signatures, 27 `param_N`, comment-backed proxy `4612/6098 = 75.63%`, strict clean-signature proxy `4554/6098 = 74.68%`.
- Earliest raw commentless row remains `0x0042f220 CSPtrSet__Clear`.
- Next commentless high-signal row is `0x005d2730 Unwind@005d2730`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260522-193422_post_wave750_unwind_continuation_verified`, 19 files, 167906183 bytes, `DiffCount=0`.

What this proves:

- The 25 target function rows exist in the saved Ghidra project.
- The saved signatures are `void __cdecl Unwind@...(void)` with no parameters.
- The saved comments and tags include `unwind-continuation-wave750` and `wave750-readback-verified`.
- The observed cleanup bodies are static retail Ghidra evidence tied to scope-table DATA xrefs, debug-string dumps, helper metadata, and decompile/instruction exports.

What remains unproven:

- Exact parent source-body identity.
- Runtime exception behavior.
- Runtime cleanup behavior.
- BEA patching behavior.
- Rebuild parity.
