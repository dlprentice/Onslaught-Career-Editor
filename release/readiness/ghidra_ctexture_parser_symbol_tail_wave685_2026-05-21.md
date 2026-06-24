# Ghidra CTexture Parser Symbol Tail Wave685 Readiness

Date: 2026-05-21

Wave685 CTexture parser symbol tail saved static Ghidra metadata for eight adjacent CTexture/CDXTexture parser-symbol, hash-table, semantic-value, yacc diagnostic, and shader semantic token rows.

Tag anchor: `ctexture-parser-symbol-tail-wave685`

Read-back anchors:

- `0x0058d419 CTexture__ParseVertexSemanticUsageToken`
- `0x0058d8c2 CTexture__ParseShaderSemanticToken`
- Next queue head: `0x0058e256 CTexture__ParseChannelMaskStrict`

## Evidence

- `ApplyCTextureParserSymbolTailWave685.java` dry/apply/final-dry completed through headless Ghidra with `REPORT: Save succeeded`.
- Dry summary: `updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=8 varargs=0 missing=0 bad=0`.
- Apply summary: `updated=8 skipped=0 renamed=0 would_rename=0 signature_updated=8 varargs=1 missing=0 bad=0`.
- Final dry summary: `updated=0 skipped=8 renamed=0 would_rename=0 signature_updated=0 varargs=0 missing=0 bad=0`.
- Post exports verified `8` metadata rows, `8` tag rows, `17` xref rows, `264` instruction rows, and `8` clean decompile rows.
- Pre-state evidence includes the same focused exports and candidate exports covering `15` adjacent CTexture/CDXTexture parser and constant-stream rows before the final eight-row tranche was selected.
- Verified backup: `G:\GhidraBackups\BEA_20260521-102431_post_wave685_ctexture_parser_symbol_tail_verified`, `19` files, `164662151` bytes, `DiffCount=0`.

## Queue Delta

Post-Wave685 queue telemetry:

- Total functions: `6098`
- Commented functions: `3919`
- Commentless functions: `2179`
- Exact-undefined signatures: `1216`
- `param_N` signatures: `402`
- Comment-backed proxy: `3919/6098 = 64.27%`
- Strict clean-signature proxy: `3869/6098 = 63.45%`

## Boundaries

This proves saved static Ghidra name/signature/comment/tag metadata only. Exact semantic enum ownership, symbol-node structure, yacc state layout, shader semantic table schema, runtime texture compiler behavior, BEA patching, and rebuild parity remain unproven.
