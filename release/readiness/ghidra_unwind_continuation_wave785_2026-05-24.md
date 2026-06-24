# Ghidra Unwind Continuation Wave785 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-24
Scope: `unwind-continuation-wave785`

Wave785 unwind continuation saved Ghidra comments, tags, and `void __cdecl ... (void)` signatures for 25 adjacent compiler-generated SEH unwind cleanup callbacks from `0x005d77c0 Unwind@005d77c0` through `0x005d7a88 Unwind@005d7a88`. The pass made no renames, no function-boundary changes, and no executable-byte changes.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x005d77c0 Unwind@005d77c0` | DATA scope-table xref `0x0061fb8c`; `CMonitor__Shutdown_Thunk` on `*(EBP-0x10)`. |
| `0x005d7800 Unwind@005d7800` | DATA scope-table xref `0x0061fbdc`; `OID__FreeObject_Callback` on `*(EBP-0x90)`. |
| `0x005d7868 Unwind@005d7868` | DATA scope-table xref `0x0061fc34`; `CGenericCamera__dtor` on `(*(EBP-0x10))+0x08`. |
| `0x005d7881 Unwind@005d7881` | DATA scope-table xref `0x0061fc44`; `CFEPMultiplayerStart__ClearJoinedPlayerSet` on `(*(EBP-0x10))+0x2bc`. |
| `0x005d7980 Unwind@005d7980` | DATA scope-table xref `0x0061fd24`; `CDXLandscape__ReleasePendingHudMarker` on `derived pointer (*(EBP-0x10))+0x08 or null staged in EBP-0x14`. |
| `0x005d7a60 Unwind@005d7a60` | DATA scope-table xref `0x0061fdbc`; `CDXLandscape__ReleaseSurfaces` on `EBP-0x14`. |
| `0x005d7a88 Unwind@005d7a88` | DATA scope-table xref `0x0061fdec`; `DebugTrace` on `(*(EBP-0x10))+0x214 via ECX before jumping to the retail stub`. |

Read-back evidence:

- `ApplyUnwindContinuationWave785.java dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave785.java apply`: `updated=25 skipped=0 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave785.java final dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 25 metadata rows, 25 tag rows, 25 xref rows, 2025 instruction rows, 25 decompile rows, and 11 helper metadata rows.
- Queue after Wave785: 6098 total, 5487 commented, 611 commentless, 88 exact-undefined signatures, 27 `param_N`, comment-backed proxy `5487/6098 = 89.98%`, strict clean-signature proxy `5429/6098 = 89.03%`.
- Earliest raw commentless row remains `0x0042f220 CSPtrSet__Clear`.
- Next commentless high-signal row is `0x005d7a96 Unwind@005d7a96`.
- Verified backup: `G:\GhidraBackups\BEA_20260524-003647_post_wave785_unwind_continuation_verified`, 19 files, 171051911 bytes, `DiffCount=0`.

What this proves:

- The 25 target function rows exist in the saved Ghidra project.
- The saved signatures are `void __cdecl ... (void)` with no parameters.
- The saved comments and tags include `unwind-continuation-wave785` and `wave785-readback-verified`.
- The observed cleanup bodies are static retail Ghidra evidence tied to scope-table DATA xrefs, helper metadata, and decompile/instruction exports.

What remains unproven:

- Exact parent source-body identity.
- Runtime exception behavior.
- Runtime cleanup behavior.
- BEA patching behavior.
- Rebuild parity.
