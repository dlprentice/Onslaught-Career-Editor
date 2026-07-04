# Ghidra Texture Repeat / Mip / Decode Wave657 Readiness Note

Status: complete
Date: 2026-05-20

## Scope

Wave657 texture repeat/mip/decode hardening covered three adjacent texture-path rows:

| Address | Saved signature |
| --- | --- |
| `0x00574abb` | `void __stdcall CDXTexture__RepeatCallbackN(int unused_arg0, int unused_arg1, int repeat_count, void * callback_fn)` |
| `0x00574e2b` | `uint __stdcall CDXTexture__GenerateMipChainBySurfaceCopy(void * surface_chain, int unused_context, uint start_level, uint mip_flags)` |
| `0x00575923` | `int __stdcall CDXTexture__DecodeMappedFileToTexture(void * decode_target, void * mapped_filename)` |

The pass added bounded comments/tags with the `texture-repeat-mip-decode-wave657` tag. It made no renames, no function-boundary changes, no executable-byte changes, no installed-game changes, and no runtime claims. The adjacent `0x00575986 Math__IsFloatDiffOutsideTolerance` and half-float conversion helpers were left for a later, separate math/CFastVB tranche.

## Evidence

- Pre-state exports: `subagents/ghidra-static-reaudit/wave657-texture-repeat-mip-decode/pre-metadata.tsv`, `pre-tags.tsv`, `pre-xrefs.tsv`, `pre-instructions.tsv`, and `decompile-pre/`.
- Apply script: `tools/ApplyTextureRepeatMipDecodeWave657.java`.
- Dry/apply/final dry:
  - Dry: `updated=0 skipped=3 renamed=0 would_rename=0 signature_updated=3 missing=0 bad=0`.
  - Apply: `updated=3 skipped=0 renamed=0 would_rename=0 signature_updated=3 missing=0 bad=0`.
  - Final dry: `updated=0 skipped=3 renamed=0 would_rename=0 signature_updated=0 missing=0 bad=0`.
- Post-state exports verified `3` metadata rows, `3` tag rows, `4` xref rows, `723` instruction rows, and `3` clean decompile rows.
- Queue refresh passed with `6093` total functions, `3583` commented, `2510` commentless, `1217` exact-undefined signatures, and `725` `param_N` signatures.
- Comment-backed proxy: `3583/6093 = 58.81%`.
- Strict clean-signature proxy: `3533/6093 = 57.98%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260520-212214_post_wave657_texture_repeat_mip_decode_verified` (`19` files, `163253127` bytes, `DiffCount=0`).
- Next high-signal queue head: `0x00575986 Math__IsFloatDiffOutsideTolerance`.

## Bounded Claim

This proves saved static retail Ghidra metadata for the three rows above: a retained-name callback repeat helper, a surface-copy mip-chain generator, and a mapped-file texture decode wrapper.

It does not prove exact callback ABI, exact owner label provenance, exact D3D interface/type enum, cube/volume layout, exact file/path storage, runtime texture conversion behavior, runtime mip output, BEA patching, or rebuild parity.
