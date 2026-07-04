# Ghidra Decode Cleanup Tail Wave896 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-26
Scope: `decode-cleanup-tail-wave896`

Wave896 decode cleanup tail saved comments/tags for two raw commentless CFastVB/CDXTexture cleanup helpers: `0x0059c610 CFastVB__ReleaseOwnedObjectAndReset_Core` and `0x0059ccb3 CDXTexture__FreeDecodeStateIfOwnerPresent`. The pass preserved existing names and signature displays, made no renames, no function-boundary changes, and no executable-byte changes.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x0059c610 CFastVB__ReleaseOwnedObjectAndReset_Core` | Tail-jumped by `0x00591050 CFastVB__ReleaseOwnedObjectAndReset` and called by `0x00592b00 CFastVB__ParserContext_Shutdown`; body calls vfunc `+0x28` when `decode_state_header+0x04` is non-null, then clears fields `+0x04` and `+0x14`. |
| `0x0059ccb3 CDXTexture__FreeDecodeStateIfOwnerPresent` | Called by `0x00592dc2 CDXTexture__CreatePngDecodeContext`, nine `0x00593411 CDXTexture__ResetPngDecodeContext` callsites, and tail-jumped by `0x0059517e CDXTexture__FreeDecodeBufferIfPresent`; body requires both arguments to be non-null before `CRT__FreeBase(decode_buffer)`. |

Read-back evidence:

- `ApplyDecodeCleanupTailWave896.java dry`: `updated=0 skipped=2 renamed=0 would_rename=0 missing=0 bad=0`
- `ApplyDecodeCleanupTailWave896.java apply`: `updated=2 skipped=0 renamed=0 would_rename=0 missing=0 bad=0`
- `ApplyDecodeCleanupTailWave896.java final dry`: `updated=0 skipped=2 renamed=0 would_rename=0 missing=0 bad=0`
- Post exports: 2 metadata rows, 2 tag rows, 13 xref rows, 22 instruction rows, and 2 decompile rows.
- Queue after Wave896: 6113 total, 6088 commented, 25 commentless, 0 exact-undefined signatures, 0 `param_N`, strict/comment-backed proxy `6088/6113 = 99.59%`.
- Next raw commentless row: `0x005a09f8 CFastVB__ConvertHalfToFloat8_SIMDKernel`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260526-071320_post_wave896_decode_cleanup_tail_verified`, 19 files, 173214599 bytes, `DiffCount=0`.

What this proves:

- The two target function rows exist in the saved Ghidra project.
- The saved names/signature displays are unchanged and clean.
- The saved comments and tags include `decode-cleanup-tail-wave896` and `wave896-readback-verified`.
- The observed cleanup bodies are static retail Ghidra evidence tied to xrefs, instruction exports, decompiles, and queue read-back.

What remains unproven:

- Exact owner object, PNG/decode buffer, and decode-state layouts.
- Exact vtable method identity and allocation pairing.
- Runtime parser/decode/image cleanup behavior.
- BEA patching behavior.
- Rebuild parity.
