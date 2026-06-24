# Ghidra Unwind Continuation Wave749 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-22
Scope: `unwind-continuation-wave749`

Wave749 unwind continuation saved Ghidra comments, tags, and `void __cdecl Unwind@...(void)` signatures for 25 adjacent compiler-generated SEH unwind cleanup callbacks from `0x005d2250 Unwind@005d2250` through `0x005d24b0 Unwind@005d24b0`. The pass made no renames, no function-boundary changes, and no executable-byte changes.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x005d2250 Unwind@005d2250` | DATA scope-table xref `0x0061b10c`; calls `OID__FreeObject_Callback` for DiveBomber.cpp debug path `0x006289c0`, line `0x16`, allocation/type value `0x12`. |
| `0x005d22e0 Unwind@005d22e0` | DATA scope-table xref `0x0061b19c`; calls `OID__FreeObject_Callback` for Dropship.cpp debug path `0x00628a54`, line `0x1b`, allocation/type value `0x2c`. |
| `0x005d23a0 Unwind@005d23a0` | DATA scope-table xref `0x0061b244`; calls `OID__FreeObject_Callback` for engine.cpp debug path `0x00628b40`, line `0x36`, allocation/type value `0x87`. |
| `0x005d2470 Unwind@005d2470` | DATA scope-table xref `0x0061b2bc`; calls `CDXLandscape__DestroyResourceDescriptorArray_Thunk` on stack-local resource descriptors at `EBP-0x434`. |
| `0x005d24b0 Unwind@005d24b0` | DATA scope-table xref `0x0061b30c`; calls `CRT__EhVectorDestructorIterator_WithUnwind` over a vector at `(*(EBP-0x10))+0x30` with element size `0x10`, count `0x258`, and `CSPtrSet__Clear`. |

Read-back evidence:

- `ApplyUnwindContinuationWave749.java dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave749.java apply`: `updated=25 skipped=0 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave749.java final dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 25 metadata rows, 25 tag rows, 25 xref rows, 725 instruction rows, and 25 decompile rows.
- Queue after Wave749: 6098 total, 4587 commented, 1511 commentless, 988 exact-undefined signatures, 27 `param_N`, comment-backed proxy `4587/6098 = 75.22%`, strict clean-signature proxy `4529/6098 = 74.27%`.
- Earliest raw commentless row remains `0x0042f220 CSPtrSet__Clear`.
- Next commentless high-signal row is `0x005d24e0 Unwind@005d24e0`.
- Verified backup: `G:\GhidraBackups\BEA_20260522-190133_post_wave749_unwind_continuation_verified`, 19 files, 167807879 bytes, `DiffCount=0`.

What this proves:

- The 25 target function rows exist in the saved Ghidra project.
- The saved signatures are `void __cdecl Unwind@...(void)` with no parameters.
- The saved comments and tags include `unwind-continuation-wave749` and `wave749-readback-verified`.
- The observed cleanup bodies are static retail Ghidra evidence tied to scope-table DATA xrefs, debug-string dumps, and decompile/instruction exports.

What remains unproven:

- Exact parent source-body identity.
- Runtime exception behavior.
- Runtime cleanup behavior.
- BEA patching behavior.
- Rebuild parity.
