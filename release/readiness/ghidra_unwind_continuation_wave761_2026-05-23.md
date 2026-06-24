# Ghidra Unwind Continuation Wave761 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-23
Scope: `unwind-continuation-wave761`

Wave761 unwind continuation saved Ghidra comments, tags, and `void __cdecl Unwind@...(void)` signatures for 25 adjacent compiler-generated SEH unwind cleanup callbacks from `0x005d3f4b Unwind@005d3f4b` through `0x005d41ce Unwind@005d41ce`. The pass made no renames, no function-boundary changes, and no executable-byte changes.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x005d3f4b Unwind@005d3f4b` | DATA scope-table xref `0x0061cab4`; loads `ECX` from `*(EBP+0x4)` and jumps to `CComplexThing__dtor_base`. |
| `0x005d3f53 Unwind@005d3f53` | DATA scope-table xref `0x0061cabc`; calls `OID__FreeObject_Callback(*(EBP+0x4))` with oids.cpp debug path `0x00630c20`, line token `0x05`, and allocation/type value `0x48`. |
| `0x005d3f69 Unwind@005d3f69` | DATA scope-table xref `0x0061cac4`; loads `ECX` from `*(EBP+0x4)` and jumps to `CActor__dtor_base`. |
| `0x005d3f80 Unwind@005d3f80` | DATA scope-table xref `0x0061caec`; loads `ECX` from `*(EBP-0x10)` and jumps to `CActor__dtor_base`. |
| `0x005d3fe8 Unwind@005d3fe8` | DATA scope-table xref `0x0061cb6c`; jumps to `CParticleManager__RemoveFromGlobalList_Thunk` on object field `(*(EBP-0x10))+0x7c`. |
| `0x005d4040 Unwind@005d4040` | DATA scope-table xref `0x0061cbe4`; calls `OID__FreeObject_Callback(*(EBP-0xa4))` with ParticleDescriptor.cpp debug path `0x00630cd8`, line token `0x10`, and allocation/type value `0x7e9`. |
| `0x005d4070 Unwind@005d4070` | DATA scope-table xref `0x0061cc0c`; calls `OID__FreeObject_Callback(*(EBP-0x10))` with ParticleManager.cpp debug path `0x00630e60`, line token `0x10`, and allocation/type value `0x1a6`. |
| `0x005d4100 Unwind@005d4100` | DATA scope-table xref `0x0061cc84`; calls `OID__FreeObject_Callback(*(EBP+0xc))` with ParticleSet.cpp debug path `0x00630fb0`, line token `0x10`, and allocation/type value `0x5f`. |
| `0x005d4184 Unwind@005d4184` | DATA scope-table xref `0x0061ccb4`; loads `ECX` from `*(EBP+0xc)` and jumps to `CParticleSet__dtor_base`. |
| `0x005d41ce Unwind@005d41ce` | DATA scope-table xref `0x0061ccd4`; calls `OID__FreeObject_Callback(*(EBP+0xc))` with ParticleSet.cpp debug path `0x00630fb0`, line token `0x10`, and allocation/type value `0x68`. |

Read-back evidence:

- `ApplyUnwindContinuationWave761.java dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave761.java apply`: `updated=25 skipped=0 renamed=0 would_rename=0 signature_updated=25 comment_only_updated=0 missing=0 bad=0`
- `ApplyUnwindContinuationWave761.java final dry`: `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 25 metadata rows, 25 tag rows, 25 xref rows, 2625 instruction rows, 25 decompile rows, and 7 helper metadata rows.
- Queue after Wave761: 6098 total, 4887 commented, 1211 commentless, 688 exact-undefined signatures, 27 `param_N`, comment-backed proxy `4887/6098 = 80.14%`, strict clean-signature proxy `4829/6098 = 79.19%`.
- Earliest raw commentless row remains `0x0042f220 CSPtrSet__Clear`.
- Next commentless high-signal row is `0x005d41e4 Unwind@005d41e4`.
- Verified backup: `G:\GhidraBackups\BEA_20260523-140318_post_wave761_unwind_continuation_verified`, 19 files, 168954759 bytes, `DiffCount=0`.

What this proves:

- The 25 target function rows exist in the saved Ghidra project.
- The saved signatures are `void __cdecl Unwind@...(void)` with no parameters.
- The saved comments and tags include `unwind-continuation-wave761` and `wave761-readback-verified`.
- The observed cleanup bodies are static retail Ghidra evidence tied to scope-table DATA xrefs, debug-string dumps, helper metadata, and decompile/instruction exports.

What remains unproven:

- Exact parent source-body identity.
- Runtime exception behavior.
- Runtime cleanup behavior.
- BEA patching behavior.
- Rebuild parity.
