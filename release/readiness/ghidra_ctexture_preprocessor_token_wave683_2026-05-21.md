# Ghidra CTexture Preprocessor Token Wave683 Readiness

Date: 2026-05-21

Wave683 CTexture preprocessor token saved static Ghidra metadata for thirteen adjacent CTexture preprocessor setup, directive action, token fetch, include-frame EOF, token-list storage, diagnostic text, and line-continuation rows.

Tag anchor: `ctexture-preprocessor-token-wave683`

Read-back anchors:

- `0x0058b1a0 CTexture__InitPreprocessorDefaultDefines`
- `0x0058c3fe CTexture__SkipLineContinuationAndAdvance`
- Next queue head: `0x0058c0e4 CFastVB__ResetConversionStatus`

## Evidence

- `ApplyCTexturePreprocessorTokenWave683.java` dry/apply/final-dry completed through headless Ghidra with `REPORT: Save succeeded`.
- Dry summary: `updated=0 skipped=13 renamed=0 would_rename=8 signature_updated=13 varargs=0 missing=0 bad=0`.
- Apply summary: `updated=13 skipped=0 renamed=8 would_rename=0 signature_updated=13 varargs=0 missing=0 bad=0`.
- Final dry summary: `updated=0 skipped=13 renamed=0 would_rename=0 signature_updated=0 varargs=0 missing=0 bad=0`.
- Post exports verified `13` metadata rows, `13` tag rows, `31` xref rows, `585` instruction rows, and `13` clean decompile rows.
- Pre-state evidence includes the same focused exports plus a `14313`-row wide instruction export for return-arity review.
- Verified backup: `G:\GhidraBackups\BEA_20260521-092456_post_wave683_ctexture_preprocessor_token_verified`, `19` files, `164531079` bytes, `DiffCount=0`.

## Queue Delta

Post-Wave683 queue telemetry:

- Total functions: `6098`
- Commented functions: `3891`
- Commentless functions: `2207`
- Exact-undefined signatures: `1216`
- `param_N` signatures: `430`
- Comment-backed proxy: `3891/6098 = 63.81%`
- Strict clean-signature proxy: `3841/6098 = 62.99%`

## Boundaries

This proves saved static Ghidra name/signature/comment/tag metadata only. Exact token enum, parser action enum, source/include context layouts, stream/provider sentinel contract, token-list field names, runtime macro expansion/preprocessor behavior, BEA patching, and rebuild parity remain unproven.
