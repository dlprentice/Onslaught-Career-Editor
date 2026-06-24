# Ghidra Texel Factory Tail Wave676 Readiness Note

Date: 2026-05-21

## Scope

Wave676 saved static Ghidra metadata for seven adjacent CFastVB texel factory tail/profile rows from `0x00587dee CFastVB__InitTexelUnpackVTable_005ea264` through `0x00587e82 CFastVB__CreateTexelUnpackProfileByFormat`.

The pass used the `texel-factory-tail-wave676` and `wave676-readback-verified` tags. It made no renames, no function-boundary changes, no executable-byte changes, and no runtime texture-output claim.

## Evidence

- Dry/apply/final dry summaries:
  - `updated=0 skipped=7 renamed=0 would_rename=0 signature_updated=7 missing=0 bad=0`
  - `updated=7 skipped=0 renamed=0 would_rename=0 signature_updated=7 missing=0 bad=0`
  - `updated=0 skipped=7 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`
- Post exports verified `7` metadata rows, `7` tag rows, `13` xref rows, `623` instruction rows, and `7` clean decompile rows.
- Queue after Wave676: `6098` total, `3828` commented, `2270` commentless, `1217` exact-undefined signatures, `489` `param_N` signatures, strict clean-signature proxy `3778/6098 = 61.95%`.
- Next queue head: `0x0058864a CDXTexture__InitMappedFileContext`.
- Verified Ghidra backup: `G:\GhidraBackups\BEA_20260521-062327_post_wave676_texel_factory_tail_verified`, `19` files, `164334471` bytes, `DiffCount=0`.

## Boundaries

Wave676 proves saved static retail Ghidra name/signature/comment/tag evidence for the observed texel factory tail tranche. Exact format enum, descriptor ABI, FourCC semantics, DXT block ABI, setup callback contract, runtime texture output behavior, BEA patching, and rebuild parity remain deferred.

Probe anchors: `Wave676 texel factory tail`, `texel-factory-tail-wave676`, `0x00587dee CFastVB__InitTexelUnpackVTable_005ea264`, `0x00587e82 CFastVB__CreateTexelUnpackProfileByFormat`, `0x0058864a CDXTexture__InitMappedFileContext`.
