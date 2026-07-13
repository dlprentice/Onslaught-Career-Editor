# Ghidra CTexture Include Context Wave680 Readiness Note

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 live correction closeout:** Historical record; `0x00589bd6` comment correction. The original text below remains provenance rather than current semantic authority. It is superseded only where confirmed. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); final per-address decisions and exact before/after metadata are in `reverse-engineering/binary-analysis/ghidra-reviewed-correction-decisions-2026-07-13.jsonl` and `reverse-engineering/binary-analysis/ghidra-reviewed-correction-plan-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Date: 2026-05-21

## Scope

Wave680 CTexture include context saved static Ghidra metadata for eighteen adjacent include/preprocessor-context rows from `0x00589367 CTexture__ReleaseIncludeNodeTreeRecursive` through `0x005898a4 CTexture__MapLexTokenToPreprocessorToken`.

The pass used the `ctexture-include-context-wave680` and `wave680-readback-verified` tags. It made no renames, no function-boundary changes, no executable-byte changes, and no runtime preprocessor claim. Sixteen rows received signature hardening; `0x005894a9 CTexture__OpenIncludeSourceAndInitBuffer` and `0x00589650 CTexture__InitBufferFromMemorySpan` kept their existing locked-storage signatures because Ghidra still reports unknown calling convention with locked parameter storage.

## Evidence

- Dry/apply/final dry summaries:
  - `updated=0 skipped=18 renamed=0 would_rename=0 signature_updated=16 missing=0 bad=0`
  - `updated=18 skipped=0 renamed=0 would_rename=0 signature_updated=16 missing=0 bad=0`
  - `updated=0 skipped=18 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`
- Post exports verified `18` metadata rows, `18` tag rows, `33` xref rows, `1458` instruction rows, and `18` clean decompile rows.
- Pre-context exports before mutation covered the same eighteen rows with `18` metadata rows, `18` tag rows, `33` xref rows, `1458` instruction rows, and `18` clean decompile rows.
- Queue after Wave680: `6098` total, `3859` commented, `2239` commentless, `1216` exact-undefined signatures, `462` `param_N` signatures, strict clean-signature proxy `3809/6098 = 62.46%`.
- Next queue head: `0x00589bd6 CTexture__ReportDirectiveParseError`.
- Verified Ghidra backup: `[maintainer-local-ghidra-backup-root]\BEA_20260521-080705_post_wave680_ctexture_include_context_verified`, `19` files, `164465543` bytes, `DiffCount=0`.

## Boundaries

Wave680 proves saved static retail Ghidra name/signature/comment/tag evidence for the observed include-node cleanup, preprocessor context setup/teardown, source-buffer initialization, directive-parser context setup/teardown, state-node push, source diagnostic getters, and lexical-token mapping rows. Exact node/context/parser layouts, provider ABI, token enum, path encoding policy, source-location/range semantics, runtime preprocessor behavior, BEA patching, and rebuild parity remain deferred.

Probe anchors: `Wave680 CTexture include context`, `ctexture-include-context-wave680`, `0x00589367 CTexture__ReleaseIncludeNodeTreeRecursive`, `0x005898a4 CTexture__MapLexTokenToPreprocessorToken`, `0x00589bd6 CTexture__ReportDirectiveParseError`.
