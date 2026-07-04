# Ghidra Texel Unpack Tail Wave674 Readiness Note

Date: 2026-05-21

## Scope

Wave674 saved static Ghidra metadata for twenty-five adjacent texel unpack tail rows from `0x0058609e CFastVB__TexelUnpackProfile_005ea020__ctor` through `0x00586994 CFastVB__InitTexelUnpackVTable_005ea118`.

The pass used the `texel-unpack-tail-wave674` and `wave674-readback-verified` tags. It made no renames, no function-boundary changes, no executable-byte changes, and no runtime texture-output claim.

## Evidence

- Dry/apply/final dry summaries:
  - `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=25 missing=0 bad=0`
  - `updated=25 skipped=0 renamed=0 would_rename=0 signature_updated=25 missing=0 bad=0`
  - `updated=0 skipped=25 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`
- Post exports verified `25` metadata rows, `25` tag rows, `25` xref rows, `1125` instruction rows, and `25` clean decompile rows.
- Queue after Wave674: `6098` total, `3796` commented, `2302` commentless, `1217` exact-undefined signatures, `521` `param_N` signatures, strict clean-signature proxy `3746/6098 = 61.43%`.
- Next queue head: `0x005869b0 CTexture__UnpackTexels_Bits16_16_16_ToFloat4`.
- Verified Ghidra backup: `[maintainer-local-ghidra-backup-root]\BEA_20260521-052857_post_wave674_texel_unpack_tail_verified`, `19` files, `164236167` bytes, `DiffCount=0`.

## Boundaries

Wave674 proves saved static retail Ghidra name/signature/comment/tag evidence for the observed texel unpack tail tranche. Exact profile ABI, descriptor layout, callback-table contract, format-table contract, lane-order enum contract, runtime texture output behavior, BEA patching, and rebuild parity remain deferred.

Probe anchors: `Wave674 texel unpack tail`, `texel-unpack-tail-wave674`, `0x0058609e CFastVB__TexelUnpackProfile_005ea020__ctor`, `0x00586994 CFastVB__InitTexelUnpackVTable_005ea118`, `0x005869b0 CTexture__UnpackTexels_Bits16_16_16_ToFloat4`.
