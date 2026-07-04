# Ghidra CTexture Directive Control Wave681 Readiness Note

Date: 2026-05-21

## Scope

Wave681 CTexture directive control saved static Ghidra metadata for ten adjacent directive diagnostics, source-location, conditional, and pragma rows from `0x00589bd6 CTexture__ReportDirectiveParseError` through `0x0058a1e3 CTexture__HandlePragma_Warning`.

The pass used the `ctexture-directive-control-wave681` and `wave681-readback-verified` tags. It made no renames, no function-boundary changes, no executable-byte changes, and no runtime preprocessor claim. All ten rows received signature hardening; `0x00589bd6 CTexture__ReportDirectiveParseError` was also marked as a cdecl varargs formatter because the decompile reads additional arguments from the caller stack.

## Evidence

- Dry/apply/final dry summaries:
  - `updated=0 skipped=10 renamed=0 would_rename=0 signature_updated=10 varargs=0 missing=0 bad=0`
  - `updated=10 skipped=0 renamed=0 would_rename=0 signature_updated=10 varargs=1 missing=0 bad=0`
  - `updated=0 skipped=10 renamed=0 would_rename=0 signature_updated=0 varargs=0 missing=0 bad=0`
- Post exports verified `10` metadata rows, `10` tag rows, `14` xref rows, `370` instruction rows, and `10` clean decompile rows.
- Pre-state exports before mutation covered the same ten rows with `10` metadata rows, `10` tag rows, `14` xref rows, `370` instruction rows, and `10` clean decompile rows.
- Queue after Wave681: `6098` total, `3869` commented, `2229` commentless, `1216` exact-undefined signatures, `452` `param_N` signatures, strict clean-signature proxy `3819/6098 = 62.63%`.
- Next queue head: `0x0058a578 CTexture__GetSymbolNameLength`.
- Verified Ghidra backup: `[maintainer-local-ghidra-backup-root]\BEA_20260521-083644_post_wave681_ctexture_directive_control_verified`, `19` files, `164465543` bytes, `DiffCount=0`.

## Boundaries

Wave681 proves saved static retail Ghidra name/signature/comment/tag evidence for observed CTexture directive diagnostics, source-location updates, `#include`, `#error`, conditional `#if`/`#elif`/`#else`/`#endif` state handling, and `#pragma pack_matrix` / `#pragma warning` handlers. Exact parser layout, diagnostic string catalog, token enum, conditional-frame layout, source-location semantics, pragma option mapping, runtime preprocessor behavior, BEA patching, and rebuild parity remain deferred.

Probe anchors: `Wave681 CTexture directive control`, `ctexture-directive-control-wave681`, `0x00589bd6 CTexture__ReportDirectiveParseError`, `0x0058a1e3 CTexture__HandlePragma_Warning`, `0x0058a578 CTexture__GetSymbolNameLength`.
