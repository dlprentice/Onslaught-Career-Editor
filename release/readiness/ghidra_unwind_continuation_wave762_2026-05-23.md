# Ghidra Unwind Continuation Wave762 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-23
Scope: `unwind-continuation-wave762`

Wave762 unwind continuation saved Ghidra comments, tags, and `void __cdecl Unwind@...(void)` signatures for 25 adjacent compiler-generated SEH unwind cleanup callbacks from `0x005d41e4 Unwind@005d41e4` through `0x005d445b Unwind@005d445b`. The pass made no renames, no function-boundary changes, and no executable-byte changes.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x005d41e4 Unwind@005d41e4` | DATA scope-table xref `0x0061ccdc`; calls `OID__FreeObject_Callback(*(EBP+0xc))` with ParticleSet.cpp debug path `0x00630fb0`, line token `0x10`, and allocation/type value `0x69`. |
| `0x005d4210 Unwind@005d4210` | DATA scope-table xref `0x0061ccec`; calls `OID__FreeObject_Callback(*(EBP+0xc))` with ParticleSet.cpp debug path `0x00630fb0`, line token `0x10`, and allocation/type value `0x6b`. |
| `0x005d4230 Unwind@005d4230` | DATA scope-table xref `0x0061cd14`; jumps to `CDXMemBuffer__dtor_base` on the stack-local buffer at `EBP-0x140`. |
| `0x005d4250 Unwind@005d4250` | DATA scope-table xref `0x0061cd3c`; jumps to `CMonitor__Shutdown_Thunk` on the monitor pointer at `*(EBP-0x18)`. |
| `0x005d4258 Unwind@005d4258` | DATA scope-table xref `0x0061cd44`; jumps to `CSPtrSet__Clear` on the embedded pointer set at `(*(EBP-0x18))+0x14`. |
| `0x005d4263 Unwind@005d4263` | DATA scope-table xref `0x0061cd4c`; calls `OID__FreeObject_Callback(*(EBP-0x14))` with PauseMenu.cpp debug path `0x006314dc`, line token `0x539`, and allocation/type value `0x80`. |
| `0x005d427f Unwind@005d427f` | DATA scope-table xref `0x0061cd54`; calls `OID__FreeObject_Callback(*(EBP+0x4))` with PauseMenu.cpp debug path `0x006314dc`, line token `0x558`, and allocation/type value `0x80`. |
| `0x005d43cf Unwind@005d43cf` | DATA scope-table xref `0x0061cdb4`; calls `OID__FreeObject_Callback(*(EBP+0x4))` with PauseMenu.cpp debug path `0x006314dc`, line token `0x593`, and allocation/type value `0x80`. |
| `0x005d445b Unwind@005d445b` | DATA scope-table xref `0x0061cddc`; calls `OID__FreeObject_Callback(*(EBP+0x4))` with PauseMenu.cpp debug path `0x006314dc`, line token `0x59a`, and allocation/type value `0x80`. |

Read-back evidence:

- `ApplyUnwindContinuationWave762.java dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave762.java apply`: `updated=25 skipped=0 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave762.java final dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 25 metadata rows, 25 tag rows, 25 xref rows, 2625 instruction rows, 25 decompile rows, and 5 helper metadata rows.
- Queue after Wave762: 6098 total, 4912 commented, 1186 commentless, 663 exact-undefined signatures, 27 `param_N`, comment-backed proxy `4912/6098 = 80.55%`, strict clean-signature proxy `4854/6098 = 79.60%`.
- Earliest raw commentless row remains `0x0042f220 CSPtrSet__Clear`.
- Next commentless high-signal row is `0x005d4477 Unwind@005d4477`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260523-143913_post_wave762_unwind_continuation_verified`, 19 files, 169085831 bytes, `DiffCount=0`.

What this proves:

- The 25 target function rows exist in the saved Ghidra project.
- The saved signatures are `void __cdecl Unwind@...(void)` with no parameters.
- The saved comments and tags include `unwind-continuation-wave762` and `wave762-readback-verified`.
- The observed cleanup bodies are static retail Ghidra evidence tied to scope-table DATA xrefs, debug-string dumps, helper metadata, and decompile/instruction exports.

What remains unproven:

- Exact parent source-body identity.
- Runtime exception behavior.
- Runtime cleanup behavior.
- BEA patching behavior.
- Rebuild parity.
