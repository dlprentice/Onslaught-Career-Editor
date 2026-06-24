# Ghidra CTexture Macro Symbol Wave682 Readiness Note

Date: 2026-05-21

## Scope

Wave682 CTexture macro symbol saved static Ghidra metadata for nine adjacent macro-symbol, quoted-string, conditional-normalization, `#define`, generic `#pragma`, and `#ifdef`/`#ifndef` rows from `0x0058a578 CTexture__GetSymbolNameLength` through `0x0058aa69 CTexture__HandleDirective_IfdefIfndef`.

The pass used the `ctexture-macro-symbol-wave682` and `wave682-readback-verified` tags. It made no renames, no function-boundary changes, no executable-byte changes, and no runtime preprocessor claim. All nine rows received signature hardening; the macro-symbol helpers were corrected to model the observed ECX parser/table context where the instructions and `RET` arities support it.

## Evidence

- Dry/apply/final dry summaries:
  - `updated=0 skipped=9 renamed=0 would_rename=0 signature_updated=9 varargs=0 missing=0 bad=0`
  - `updated=9 skipped=0 renamed=0 would_rename=0 signature_updated=9 varargs=0 missing=0 bad=0`
  - `updated=0 skipped=9 renamed=0 would_rename=0 signature_updated=0 varargs=0 missing=0 bad=0`
- Post exports verified `9` metadata rows, `9` tag rows, `21` xref rows, `333` instruction rows, and `9` clean decompile rows.
- Pre-state exports before mutation covered the same nine rows with `9` metadata rows, `9` tag rows, `21` xref rows, `333` instruction rows, and `9` clean decompile rows. A wider pre-instruction export captured `3249` rows to verify the `RET` arities before mutation.
- Queue after Wave682: `6098` total, `3878` commented, `2220` commentless, `1216` exact-undefined signatures, `443` `param_N` signatures, strict clean-signature proxy `3828/6098 = 62.77%`.
- Next queue head: `0x0058b1a0 CTexture__InitPreprocessorDefaultDefines`.
- Verified Ghidra backup: `G:\GhidraBackups\BEA_20260521-085906_post_wave682_ctexture_macro_symbol_verified`, `19` files, `164498311` bytes, `DiffCount=0`.

## Boundaries

Wave682 proves saved static retail Ghidra name/signature/comment/tag evidence for observed CTexture macro-symbol list lookup/insert/remove paths, quote escaping, conditional expression normalization, `#define` macro capture, generic pragma dispatch, and simple `#ifdef`/`#ifndef` macro lookup handling. Exact macro node layout, bucket policy, token descriptor layout, expression-value convention, ifdef/ifndef polarity, runtime macro expansion/preprocessor behavior, BEA patching, and rebuild parity remain deferred.

Probe anchors: `Wave682 CTexture macro symbol`, `ctexture-macro-symbol-wave682`, `0x0058a578 CTexture__GetSymbolNameLength`, `0x0058aa69 CTexture__HandleDirective_IfdefIfndef`, `0x0058b1a0 CTexture__InitPreprocessorDefaultDefines`.
