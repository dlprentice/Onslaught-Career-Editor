# Ghidra CDXTexture Head Wave617

Status: ready
Date: 2026-05-20

## Scope

Wave617 hardened `4` CDXTexture rows at the current high-signal queue head:

- `0x00557300 CDXTexture__LoadTextureFromFile`
- `0x005586e0 CDXTexture__DumpTextureToRGBA`
- `0x00559410 CDXTexture__CreateMipmaps`
- `0x00559be0 CDXTexture__Deserialize`

The tranche is a saved-Ghidra signature/comment/tag pass with no renames and no function-boundary changes.

## What Changed

- Saved bounded signatures/comments/tags for the texture-file loader, debug TGA dump helper, mipmap stream fallback, and caller-cleaned texture resource deserializer.
- Documented `CDXTexture__LoadTextureFromFile` as an ECX=this plus one stack `texture_slot` helper that builds `data\\Resources` texture/dxtntexture `.aya` paths, loads a `CDXMemBuffer`, applies downscale-shift state, and dispatches `CDXTexture__DecodeMappedMemoryEntry`.
- Documented `CDXTexture__DumpTextureToRGBA` as an ECX=this plus one stack `output_path` helper called by `CDXTexture__DumpAllTexturesToTga`, converting observed 32-bit/16-bit source formats into a temporary RGBA buffer before `ImageIO__WriteTGA24`.
- Documented `CDXTexture__CreateMipmaps` as an ECX=this plus `chunk_reader`, `texture_slot`, and `mip_count` helper reached from `CDXTexture__Deserialize` after direct texture creation fails.
- Documented `CDXTexture__Deserialize` as a `__cdecl` caller-cleaned resource deserializer reached from the resource accumulator, Goodies, bitmap-font, and imposter deserialize paths.

## Evidence

- Apply script: `tools/ApplyCDXTextureHeadWave617.java`
- Focused probe: `tools/ghidra_cdxtexture_head_wave617_probe.py`
- Scratch evidence: `subagents/ghidra-static-reaudit/wave617-cdxtexture-head/`
- Dry: `updated=0 skipped=4 renamed=0 would_rename=0 missing=0 bad=0`
- Apply: `updated=4 skipped=0 renamed=0 would_rename=0 missing=0 bad=0`
- Final dry: `updated=0 skipped=4 renamed=0 would_rename=0 missing=0 bad=0`
- Read-back exports verified `16` context metadata rows, `16` tag rows, `57` xref rows, `592` instruction rows, `16` decompile rows, `32` vtable-slot rows, and `13` callsite-instruction targets.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260520-022015_post_wave617_cdxtexture_head_verified`
  - `sourceFileCount=19`
  - `destFileCount=19`
  - `sourceBytes=161614727`
  - `destBytes=161614727`
  - `DiffCount=0`

## Queue Delta

Post-Wave617 queue telemetry:

- Total functions: `6093`
- Commented functions: `3176`
- Commentless functions: `2917`
- Exact-undefined signatures: `1256`
- `param_N` signatures: `1056`
- Comment-backed proxy: `3176/6093 = 52.13%`
- Strict clean-signature proxy: `3131/6093 = 51.39%`
- Next queue head: `0x0055a350 CDXTrees__CDXTrees`

Delta from Wave616:

- `+4` commented rows
- `-4` commentless rows
- `-4` exact-undefined signatures
- `0` `param_N` signatures
- `+4` strict clean rows

## Limits

This is static retail Ghidra signature/comment/tag evidence only. Runtime texture loading, debug texture dumping, mipmap upload behavior, and resource ownership remain unproven. Exact `CDXTexture`, `CTexture`, D3D, pixel-format, and serialized texture layouts, concrete source identity, BEA patching, and rebuild parity remain deferred.
