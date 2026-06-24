# Ghidra CTexture Lexical Token Wave684 Readiness

Date: 2026-05-21

Wave684 CTexture lexical token saved static Ghidra metadata for twenty adjacent CFastVB, CDXTexture, and CTexture lexical-token, literal-parser, diagnostic, and sorted-key support rows.

Tag anchor: `ctexture-lexical-token-wave684`

Read-back anchors:

- `0x0058c0e4 CFastVB__ResetConversionStatus`
- `0x0058d2ad CTexture__ReadNextLexToken`
- Next queue head: `0x0058d419 CTexture__ParseVertexSemanticUsageToken`

## Evidence

- `ApplyCTextureLexicalTokenWave684.java` dry/apply/final-dry completed through headless Ghidra with `REPORT: Save succeeded`.
- Dry summary: `updated=0 skipped=20 renamed=0 would_rename=2 signature_updated=20 varargs=0 missing=0 bad=0`.
- Apply summary: `updated=20 skipped=0 renamed=2 would_rename=0 signature_updated=20 varargs=2 missing=0 bad=0`.
- Final dry summary: `updated=0 skipped=20 renamed=0 would_rename=0 signature_updated=0 varargs=0 missing=0 bad=0`.
- Post exports verified `20` metadata rows, `20` tag rows, `118` xref rows, `660` instruction rows, and `20` clean decompile rows.
- Pre-state evidence includes the same focused exports, a `2020`-row wide instruction export, and candidate exports covering `25` adjacent rows before the final twenty-row tranche was selected.
- Verified backup: `G:\GhidraBackups\BEA_20260521-095848_post_wave684_ctexture_lexical_token_verified`, `19` files, `164629383` bytes, `DiffCount=0`.

## Queue Delta

Post-Wave684 queue telemetry:

- Total functions: `6098`
- Commented functions: `3911`
- Commentless functions: `2187`
- Exact-undefined signatures: `1216`
- `param_N` signatures: `410`
- Comment-backed proxy: `3911/6098 = 64.14%`
- Strict clean-signature proxy: `3861/6098 = 63.32%`

## Boundaries

This proves saved static Ghidra name/signature/comment/tag metadata only. Exact token enum, diagnostic catalog, lexer state layout, format descriptor ABI, runtime texture compiler behavior, BEA patching, and rebuild parity remain unproven.
