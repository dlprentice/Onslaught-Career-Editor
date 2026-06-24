# Ghidra Unwind Continuation Wave763 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-23
Scope: `unwind-continuation-wave763`

Wave763 unwind continuation saved Ghidra comments, tags, and `void __cdecl Unwind@...(void)` signatures for 25 adjacent compiler-generated SEH unwind cleanup callbacks from `0x005d4477 Unwind@005d4477` through `0x005d46c0 Unwind@005d46c0`. The pass made no renames, no function-boundary changes, and no executable-byte changes.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x005d4477 Unwind@005d4477` | DATA scope-table xref `0x0061cde4`; calls `OID__FreeObject_Callback(*(EBP+0x4))` with PauseMenu.cpp debug path `0x006314dc`, line token `0x59c`, and allocation/type value `0x80`. |
| `0x005d44af Unwind@005d44af` | DATA scope-table xref `0x0061cdf4`; calls `OID__FreeObject_Callback(*(EBP-0x14))` with PauseMenu.cpp debug path `0x006314dc`, line token `0x5aa`, and allocation/type value `0x80`. |
| `0x005d45a0 Unwind@005d45a0` | DATA scope-table xref `0x0061ce54`; jumps to `CMonitor__Shutdown_Thunk` on the monitor pointer at `*(EBP-0x10)`. |
| `0x005d45a8 Unwind@005d45a8` | DATA scope-table xref `0x0061ce5c`; jumps to `CSPtrSet__Clear` on the embedded pointer set at `(*(EBP-0x10))+0x14`. |
| `0x005d45e4 Unwind@005d45e4` | DATA scope-table xref `0x0061ce94`; jumps to `CMenuItemRangeVariant__Destructor` on the subobject at `(*(EBP+0x4))+0x0c`. |
| `0x005d45ef Unwind@005d45ef` | DATA scope-table xref `0x0061ce9c`; jumps to `CSPtrSet__Clear` on the embedded pointer set at `(*(EBP+0x4))+0x3c`. |
| `0x005d4670 Unwind@005d4670` | DATA scope-table xref `0x0061cf0c`; calls `OID__FreeObject_Callback(*(EBP+0x4))` with Plane.cpp debug path `0x00631630`, line token `0x13`, and allocation/type value `0x17`. |
| `0x005d469c Unwind@005d469c` | DATA scope-table xref `0x0061cf1c`; calls `OID__FreeObject_Callback(*(EBP+0x4))` with Plane.cpp debug path `0x00631630`, line token `0x2a`, and allocation/type value `0x10`. |
| `0x005d46c0 Unwind@005d46c0` | DATA scope-table xref `0x0061cf44`; jumps to `CMonitor__Shutdown` on the monitor pointer at `*(EBP-0x10)`. |

Read-back evidence:

- `ApplyUnwindContinuationWave763.java dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave763.java apply`: `updated=25 skipped=0 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave763.java final dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 25 metadata rows, 25 tag rows, 25 xref rows, 2625 instruction rows, 25 decompile rows, and 6 helper metadata rows.
- Queue after Wave763: 6098 total, 4937 commented, 1161 commentless, 638 exact-undefined signatures, 27 `param_N`, comment-backed proxy `4937/6098 = 80.96%`, strict clean-signature proxy `4879/6098 = 80.01%`.
- Earliest raw commentless row remains `0x0042f220 CSPtrSet__Clear`.
- Next commentless high-signal row is `0x005d46c8 Unwind@005d46c8`.
- Verified backup: `G:\GhidraBackups\BEA_20260523-150812_post_wave763_unwind_continuation_verified`, 19 files, 169118599 bytes, `DiffCount=0`.

What this proves:

- The 25 target function rows exist in the saved Ghidra project.
- The saved signatures are `void __cdecl Unwind@...(void)` with no parameters.
- The saved comments and tags include `unwind-continuation-wave763` and `wave763-readback-verified`.
- The observed cleanup bodies are static retail Ghidra evidence tied to scope-table DATA xrefs, debug-string dumps, helper metadata, and decompile/instruction exports.

What remains unproven:

- Exact parent source-body identity.
- Runtime exception behavior.
- Runtime cleanup behavior.
- BEA patching behavior.
- Rebuild parity.
