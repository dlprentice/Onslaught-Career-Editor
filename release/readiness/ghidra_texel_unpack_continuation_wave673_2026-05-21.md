# Ghidra Texel Unpack Continuation Wave673 Readiness Note

Date: 2026-05-21

## Scope

Wave673 saved static Ghidra metadata for twenty-five adjacent texel unpack continuation rows from `0x0058577f CFastVB__TexelUnpackProfile_005e9f3c__ctor` through `0x00585fa3 CFastVB__UnpackTexels_Signed8_8_8_8_ToFloat4`.

The pass used the `texel-unpack-continuation-wave673` and `wave673-readback-verified` tags. It made no renames, no function-boundary changes, no executable-byte changes, and no runtime texture-output claim.

## Evidence

- Dry/apply/final dry summaries:
  - `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=25 missing=0 bad=0`
  - `updated=25 skipped=0 renamed=0 would_rename=0 signature_updated=25 missing=0 bad=0`
  - `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`
- Post exports verified `25` metadata rows, `25` tag rows, `67` xref rows, `1125` instruction rows, and `25` clean decompile rows.
- Queue after Wave673: `6098` total, `3771` commented, `2327` commentless, `1217` exact-undefined signatures, `546` `param_N` signatures, strict clean-signature proxy `3721/6098 = 61.02%`.
- Next queue head: `0x0058609e CFastVB__TexelUnpackProfile_005ea020__ctor`.
- Verified Ghidra backup: `G:\GhidraBackups\BEA_20260521-045554_post_wave673_texel_unpack_continuation_verified`, `19` files, `164072327` bytes, `DiffCount=0`.

## Boundaries

Wave673 proves saved static retail Ghidra name/signature/comment/tag evidence for the observed texel unpack continuation tranche. Exact profile ABI, descriptor layout, callback-table contract, format-table contract, lane-order enum contract, runtime texture output behavior, BEA patching, and rebuild parity remain deferred.

Probe anchors: `Wave673 texel unpack continuation`, `texel-unpack-continuation-wave673`, `0x0058577f CFastVB__TexelUnpackProfile_005e9f3c__ctor`, `0x00585fa3 CFastVB__UnpackTexels_Signed8_8_8_8_ToFloat4`, `0x0058609e CFastVB__TexelUnpackProfile_005ea020__ctor`.
