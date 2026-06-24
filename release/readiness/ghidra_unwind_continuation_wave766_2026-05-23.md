# Ghidra Unwind Continuation Wave766 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-23
Scope: `unwind-continuation-wave766`

Wave766 unwind continuation saved Ghidra comments, tags, and `void __cdecl Unwind@...(void)` signatures for 25 adjacent compiler-generated SEH unwind cleanup callbacks from `0x005d4bf0 Unwind@005d4bf0` through `0x005d4de9 Unwind@005d4de9`. The pass made no renames, no function-boundary changes, and no executable-byte changes.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x005d4bf0 Unwind@005d4bf0` | DATA scope-table xref `0x0061d45c`; calls `OID__FreeObject_Callback(*(EBP-0x10))` with SoundManager.cpp debug path `0x00632428`, line token `0x5a`, and allocation/type value `0x4a`. |
| `0x005d4c30 Unwind@005d4c30` | DATA scope-table xref `0x0061d4ac`; jumps to `CDXMemBuffer__dtor_base(EBP-0x140)`. |
| `0x005d4c50 Unwind@005d4c50` | DATA scope-table xref `0x0061d4d4`; jumps to `CGenericActiveReader__dtor(*(EBP-0x10))`. |
| `0x005d4c70 Unwind@005d4c70` | DATA scope-table xref `0x0061d4fc`; jumps to `CMonitor__Shutdown(*(EBP-0x10))`. |
| `0x005d4cf0 Unwind@005d4cf0` | DATA scope-table xref `0x0061d5ac`; calls `OID__FreeObject_Callback(*(EBP+0x8))` with SphereTrigger.cpp debug path `0x0063270c`, line token `0x53`, and allocation/type value `0x5b`. |
| `0x005d4d0e Unwind@005d4d0e` | DATA scope-table xref `0x0061d5bc`; calls `OID__FreeObject_Callback(*(EBP+0x4))` with monitor.h debug path `0x0062551c`, line token `0x18`, and allocation/type value `0x5e`. |
| `0x005d4d30 Unwind@005d4d30` | DATA scope-table xref `0x0061d5e4`; jumps to `CComplexThing__dtor_base_Thunk_004bff30(*(EBP-0x14))`. |
| `0x005d4d38 Unwind@005d4d38` | DATA scope-table xref `0x0061d5ec`; jumps to `CSPtrSet__Clear((*(EBP-0x14))+0xa4)`. |
| `0x005d4d62 Unwind@005d4d62` | DATA scope-table xref `0x0061d604`; jumps to `CDXLandscape__FreeObjectCallback((*(EBP-0x10))+0x10)`. |
| `0x005d4dd0 Unwind@005d4dd0` | DATA scope-table xref `0x0061d674`; calls `OID__FreeObject_Callback(*(EBP+0xc))` with SquadNormal.cpp debug path `0x0063283c`, line token `0x81`, and allocation/type value `0x0a`. |
| `0x005d4de9 Unwind@005d4de9` | DATA scope-table xref `0x0061d67c`; jumps to `CGenericActiveReader__dtor(*(EBP+0xc))`. |

Read-back evidence:

- `ApplyUnwindContinuationWave766.java dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave766.java apply`: `updated=25 skipped=0 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave766.java final dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 25 metadata rows, 25 tag rows, 25 xref rows, 925 instruction rows, 25 decompile rows, and 9 helper metadata rows.
- Queue after Wave766: 6098 total, 5012 commented, 1086 commentless, 563 exact-undefined signatures, 27 `param_N`, comment-backed proxy `5012/6098 = 82.19%`, strict clean-signature proxy `4954/6098 = 81.24%`.
- Earliest raw commentless row remains `0x0042f220 CSPtrSet__Clear`.
- Next commentless high-signal row is `0x005d4e00 Unwind@005d4e00`.
- Verified backup: `G:\GhidraBackups\BEA_20260523-161835_post_wave766_unwind_continuation_verified`, 19 files, 169413511 bytes, `DiffCount=0`.

What this proves:

- The 25 target function rows exist in the saved Ghidra project.
- The saved signatures are `void __cdecl Unwind@...(void)` with no parameters.
- The saved comments and tags include `unwind-continuation-wave766` and `wave766-readback-verified`.
- The observed cleanup bodies are static retail Ghidra evidence tied to scope-table DATA xrefs, debug-string dumps, helper metadata, and decompile/instruction exports.

What remains unproven:

- Exact parent source-body identity.
- Runtime exception behavior.
- Runtime cleanup behavior.
- BEA patching behavior.
- Rebuild parity.
