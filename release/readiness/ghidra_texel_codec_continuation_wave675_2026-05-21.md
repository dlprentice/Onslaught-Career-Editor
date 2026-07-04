# Ghidra Texel Codec Continuation Wave675 Readiness Note

Date: 2026-05-21

## Scope

Wave675 saved static Ghidra metadata for twenty-five adjacent CTexture/CFastVB texel codec, scratch row-window, profile constructor, quad-cache read/write, and destructor-like rows from `0x005869b0 CTexture__UnpackTexels_Bits16_16_16_ToFloat4` through `0x00587dd6 CFastVB__TexelUnpackProfileRegistry_005ea254__ctor`.

The pass used the `texel-codec-continuation-wave675` and `wave675-readback-verified` tags. It made no renames, no function-boundary changes, no executable-byte changes, and no runtime texture-output claim.

## Evidence

- Dry/apply/final dry summaries:
  - `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=25 missing=0 bad=0`
  - `updated=25 skipped=0 renamed=0 would_rename=0 signature_updated=25 missing=0 bad=0`
  - `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`
- Post exports verified `25` metadata rows, `25` tag rows, `52` xref rows, `1125` instruction rows, and `25` clean decompile rows.
- Queue after Wave675: `6098` total, `3821` commented, `2277` commentless, `1217` exact-undefined signatures, `496` `param_N` signatures, strict clean-signature proxy `3771/6098 = 61.84%`.
- Next queue head: `0x00587dee CFastVB__InitTexelUnpackVTable_005ea264`.
- Verified Ghidra backup: `[maintainer-local-ghidra-backup-root]\BEA_20260521-055935_post_wave675_texel_codec_continuation_verified`, `19` files, `164301703` bytes, `DiffCount=0`.

## Boundaries

Wave675 proves saved static retail Ghidra name/signature/comment/tag evidence for the observed texel codec continuation tranche. Exact profile ABI, descriptor layout, FourCC semantics, DXT block ABI, quad-cache contract, runtime texture output behavior, BEA patching, and rebuild parity remain deferred.

Probe anchors: `Wave675 texel codec continuation`, `texel-codec-continuation-wave675`, `0x005869b0 CTexture__UnpackTexels_Bits16_16_16_ToFloat4`, `0x00587dd6 CFastVB__TexelUnpackProfileRegistry_005ea254__ctor`, `0x00587dee CFastVB__InitTexelUnpackVTable_005ea264`.
