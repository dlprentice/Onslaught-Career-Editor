# Ghidra Final Static Tail Wave900 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-26
Scope: `final-static-tail-wave900`

Wave900 final static tail saved comments/tags for the last seven raw commentless functions in the loaded Ghidra database. The pass preserved all existing names and signature displays, made no renames, no function-boundary changes, no executable-byte changes, and did not launch BEA.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x005d04e6 RtlUnwind` | One-instruction Windows import thunk through IAT slot `0x005d81e4`; called by `__global_unwind2` and `CRT__SehRtlUnwindAndRestoreFrame`. |
| `0x005d06f0 CRT__InitSehFrameNoop` | Compact CRT SEH-frame setup helper called by `CDXTexture__InitCpuVendorAndSimdFlags` at `0x005891cb`. |
| `0x005d08ad CRT__TmpFile_OpenUniqueBinaryStream` | CRT temporary binary stream opener called by `CDXTexture__InitHostIoCallbacks` at `0x005b1d51`; uses `DAT_009d3038`, open flags `0x8542`, permission `0x180`, and errno retry `0x11`. |
| `0x005d0a9f CRT__LongJmpProbe_NoOp` | `_longjmp`-adjacent SEH-shaped probe called at `0x005d05f0`; restores `FS:[0]` and returns with `RET 0x4`. |
| `0x005d0c0c GetCurrentProcessId` | One-instruction Windows import thunk through IAT slot `0x005d8144`; called by `init_namebuf` at `0x005d09c9`. |
| `0x005d0c7f CRT__LCMapStringW_AnsiCompat` | Frontend/save-name CRT locale compatibility helper called by `CFEPSaveGame__WideCharToLowerCompat` at `0x005d0a89`; probes `LCMapStringW`/`LCMapStringA` support through `DAT_009d304c`. |
| `0x005d5120 CTexture__FindTexture_Unwind` | texture.cpp unwind cleanup callback reached from scope-table DATA xref `0x0061d9cc`; calls `OID__FreeObject_Callback` on the stack allocation pointer at `EBP-0x210`. |

Read-back evidence:

- `ApplyFinalStaticTailWave900.java dry`: `updated=0 skipped=7 renamed=0 would_rename=0 missing=0 bad=0`
- `ApplyFinalStaticTailWave900.java apply`: `updated=7 skipped=0 renamed=0 would_rename=0 missing=0 bad=0`
- `ApplyFinalStaticTailWave900.java final dry`: `updated=0 skipped=7 renamed=0 would_rename=0 missing=0 bad=0`
- Post exports: 7 metadata rows, 7 tag rows, 8 xref rows, 304 instruction rows, and 7 decompile rows.
- Queue after Wave900: 6113 total, 6113 commented, 0 commentless, 0 exact-undefined signatures, 0 `param_N`, comment-backed proxy `6113/6113 = 100.00%`, strict clean-signature proxy `6113/6113 = 100.00%`.
- Commentless high-signal, signature, and name-confidence queues are empty.
- Verified backup: `G:\GhidraBackups\BEA_20260526-090248_post_wave900_final_static_tail_verified`, 19 files, 173247367 bytes, `DiffCount=0`.

What this proves:

- Every function object in the loaded Ghidra database has a non-empty function comment.
- Every function object in the current queue snapshot avoids exact `undefined` signatures and `param_N` parameter names.
- The seven Wave900 target rows exist in the saved Ghidra project with `final-static-tail-wave900` and `wave900-readback-verified` tags.
- The current static function-quality proxy is `6113/6113 = 100.00%`.

What remains unproven:

- That every current name, signature, comment, tag, or function boundary is correct.
- Exact MSVC CRT/source version identity.
- Exact Windows runtime behavior for import thunks, SEH, longjmp, locale mapping, process-id generation, temporary files, or exception cleanup.
- Exact parent source-body identity for `CTexture__FindTexture_Unwind`.
- Runtime BEA behavior, BEA patching behavior, and rebuild parity.
