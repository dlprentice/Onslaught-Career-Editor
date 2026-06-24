# Ghidra Unwind Continuation Wave755 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-23
Scope: `unwind-continuation-wave755`

Wave755 unwind continuation saved Ghidra comments, tags, and `void __cdecl Unwind@...(void)` signatures for 25 adjacent compiler-generated SEH unwind cleanup callbacks from `0x005d30a0 Unwind@005d30a0` through `0x005d3379 Unwind@005d3379`. The pass made no renames, no function-boundary changes, and no executable-byte changes.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x005d30a0 Unwind@005d30a0` | DATA scope-table xref `0x0061bde4`; calls `OID__FreeObject_Callback` on `*(EBP+0x4)` with InitThing.cpp debug path `0x0062d7b0`, line token `0x09`, and allocation/type value `0x2f`. |
| `0x005d30f8 Unwind@005d30f8` | DATA scope-table xref `0x0061be04`; same InitThing.cpp allocation-cleanup shape with allocation/type value `0x3f`. |
| `0x005d3120 Unwind@005d3120` | DATA scope-table xref `0x0061be2c`; jumps to `CUMTexture__dtor_base` with `ECX=*(EBP-0x10)`. |
| `0x005d31c0 Unwind@005d31c0` | DATA scope-table xref `0x0061bef4`; calls `OID__FreeObject_Callback` on `*(EBP-0x20)` with mapwho.cpp debug path `0x0062db88`, line token `0x45`, and allocation/type value `0x44`. |
| `0x005d3200 Unwind@005d3200` | DATA scope-table xref `0x0061bf44`; calls `OID__FreeObject_Callback` on `*(EBP+0x4)` with MCBuggy.cpp debug path `0x0062dc80`, line token `0x1b`, and allocation/type value `0x4e`. |
| `0x005d32a0 Unwind@005d32a0` | DATA scope-table xref `0x0061bfec`; calls `OID__FreeObject_Callback` on `*(EBP-0x160)` with MCMech.cpp debug path `0x0062df60`, line token `0x1b`, and allocation/type value `0x131`. |
| `0x005d3300 Unwind@005d3300` | DATA scope-table xref `0x0061c024`; jumps to `CLine__SetBaseVtable_00426360` with local `EBP-0x40`. |
| `0x005d3320 Unwind@005d3320` | DATA scope-table xref `0x0061c04c`; jumps to `CMCBuggy__ProfileEnd` with local `EBP-0x1b4`. |
| `0x005d3360 Unwind@005d3360` | DATA scope-table xref `0x0061c09c`; calls `OID__FreeObject_Callback` on `*(EBP-0x174)` with MCTentacle.cpp debug path `0x0062e06c`, line token `0x1b`, and allocation/type value `0x45`. |
| `0x005d3379 Unwind@005d3379` | DATA scope-table xref `0x0061c0a4`; same MCTentacle.cpp allocation-cleanup shape with allocation/type value `0x49`. |

Read-back evidence:

- `ApplyUnwindContinuationWave755.java dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave755.java apply`: `updated=25 skipped=0 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave755.java final dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 25 metadata rows, 25 tag rows, 25 xref rows, 925 instruction rows, 25 decompile rows, and 8 helper metadata rows.
- Queue after Wave755: 6098 total, 4737 commented, 1361 commentless, 838 exact-undefined signatures, 27 `param_N`, comment-backed proxy `4737/6098 = 77.68%`, strict clean-signature proxy `4679/6098 = 76.73%`.
- Earliest raw commentless row remains `0x0042f220 CSPtrSet__Clear`.
- Next commentless high-signal row is `0x005d3392 Unwind@005d3392`.
- Verified backup: `G:\GhidraBackups\BEA_20260523-105815_post_wave755_unwind_continuation_verified`, 19 files, 168364935 bytes, `DiffCount=0`.

What this proves:

- The 25 target function rows exist in the saved Ghidra project.
- The saved signatures are `void __cdecl Unwind@...(void)` with no parameters.
- The saved comments and tags include `unwind-continuation-wave755` and `wave755-readback-verified`.
- The observed cleanup bodies are static retail Ghidra evidence tied to scope-table DATA xrefs, debug-string dumps, helper metadata, and decompile/instruction exports.

What remains unproven:

- Exact parent source-body identity.
- Runtime exception behavior.
- Runtime cleanup behavior.
- BEA patching behavior.
- Rebuild parity.
