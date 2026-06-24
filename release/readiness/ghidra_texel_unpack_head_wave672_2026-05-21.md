# Ghidra Texel Unpack Head Wave672 Readiness Note

Date: 2026-05-21

## Scope

Wave672 saved static Ghidra metadata for sixteen adjacent texel unpacker rows from `0x00584b5f CTexture__UnpackTexels_Bgr8ToFloat4` through `0x005856b8 CDXTexture__UnpackTexels_Bits332A8ToFloat4`.

The pass used the `texel-unpack-head-wave672` and `wave672-readback-verified` tags. It made no renames, no function-boundary changes, no executable-byte changes, and no runtime texture-output claim.

## Evidence

- Dry/apply/final dry summaries:
  - `updated=0 skipped=16 renamed=0 would_rename=0 signature_updated=16 missing=0 bad=0`
  - `updated=16 skipped=0 renamed=0 would_rename=0 signature_updated=16 missing=0 bad=0`
  - `updated=0 skipped=16 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`
- Post exports verified `16` metadata rows, `16` tag rows, `16` xref rows, `1616` instruction rows, and `16` clean decompile rows.
- Queue after Wave672: `6098` total, `3746` commented, `2352` commentless, `1217` exact-undefined signatures, `571` `param_N` signatures, strict clean-signature proxy `3696/6098 = 60.61%`.
- Next queue head: `0x0058577f CFastVB__TexelUnpackProfile_005e9f3c__ctor`.
- Verified Ghidra backup: `G:\GhidraBackups\BEA_20260521-042809_post_wave672_texel_unpack_head_verified`, `19` files, `163941255` bytes, `DiffCount=0`.

## Boundaries

Wave672 proves saved static retail Ghidra name/signature/comment/tag evidence for the observed unpacker tranche. Exact profile ABI, format-table contract, current owner/layout identity for `0x0058546f`, lane-order enum contracts, runtime texture output behavior, BEA patching, and rebuild parity remain deferred.

Probe anchors: `Wave672 texel unpack head`, `texel-unpack-head-wave672`, `0x00584b5f CTexture__UnpackTexels_Bgr8ToFloat4`, `0x005856b8 CDXTexture__UnpackTexels_Bits332A8ToFloat4`, `0x0058577f CFastVB__TexelUnpackProfile_005e9f3c__ctor`.
