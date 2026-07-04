# Ghidra CTexture Channel Constant Tail Wave686 Readiness

Date: 2026-05-21

Wave686 CTexture channel constant tail saved static Ghidra metadata for seven adjacent CTexture channel-mask, swizzle-mask, pending constant-stream, instruction operand-validation, and symbol-table finalization rows.

Tag anchor: `ctexture-channel-constant-tail-wave686`

Read-back anchors:

- `0x0058e256 CTexture__ParseChannelMaskStrict`
- `0x0058ecdb CTexture__FinalizeSymbolTablesIntoConstantStream`
- Next queue head: `0x0058eefb CTexture__ParseDebugChunkAndRelocateBindings`

## Evidence

- `ApplyCTextureChannelConstantTailWave686.java` dry/apply/final-dry completed through headless Ghidra with `REPORT: Save succeeded`.
- Dry summary: `updated=0 skipped=7 renamed=0 would_rename=0 signature_updated=7 varargs=0 missing=0 bad=0`.
- Apply summary: `updated=7 skipped=0 renamed=0 would_rename=0 signature_updated=7 varargs=0 missing=0 bad=0`.
- Final dry summary: `updated=0 skipped=7 renamed=0 would_rename=0 signature_updated=0 varargs=0 missing=0 bad=0`.
- Post exports verified `7` metadata rows, `7` tag rows, `13` xref rows, `511` instruction rows, and `7` clean decompile rows.
- Pre-state evidence includes the same focused exports and candidate exports covering `11` adjacent CTexture/CDXTexture channel, constant-stream, debug-chunk, destructor, release, and stream-write rows before the final seven-row tranche was selected.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260521-105415_post_wave686_ctexture_channel_constant_tail_verified`, `19` files, `164727687` bytes, `DiffCount=0`.

## Queue Delta

Post-Wave686 queue telemetry:

- Total functions: `6098`
- Commented functions: `3926`
- Commentless functions: `2172`
- Exact-undefined signatures: `1216`
- `param_N` signatures: `395`
- Comment-backed proxy: `3926/6098 = 64.38%`
- Strict clean-signature proxy: `3876/6098 = 63.56%`

## Boundaries

This proves saved static Ghidra name/signature/comment/tag metadata only. Exact channel-mask enum ownership, swizzle enum ownership, token-record layout, constant-stream format, shader ABI encoding, FINF/debug chunk schema, runtime texture compiler behavior, BEA patching, and rebuild parity remain unproven.
