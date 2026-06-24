# Ghidra Texture/TGA Wave513 Readiness

Status: static read-back complete
Date: 2026-05-17

## Scope

Wave513 saved name/signature/comment/tag hardening for 9 texture and TGA-adjacent helpers:

- `0x004f27f0` `CTexture__FindTexture`
- `0x004f29c0` `CTexture__InitDefaultTextureResourcesAndStatus`
- `0x004f2a30` `CTexture__ClearOut`
- `0x004f2b40` `CTexture__FreeLevelResources`
- `0x004f2c60` `CTGALoader__CTGALoader`
- `0x004f2c90` `CTGALoader__ScalarDeletingDestructor`
- `0x004f2cb0` `CTGALoader__Destructor`
- `0x004f2ce0` `CTGALoader__Load`
- `0x004f3110` `ImageIO__WriteTGA24`

The pass includes 2 renames: the CTGALoader scalar-deleting destructor and destructor body were normalized from stale lowercase destructor labels.

## Evidence

- Pre-state exports: `subagents/ghidra-static-reaudit/wave513-texture-tga-004f27f0/pre_*`.
- Caller/context exports: CMapTex, CDamage, CEngine screenshot, CDXTexture dump, and CImageLoader accessors under the same ignored evidence folder.
- Mutation script: `tools/ApplyTextureTgaWave513.java`.
- Dry run: `updated=0 skipped=9 renamed=0 would_rename=2 missing=0 bad=0`.
- Apply run: `updated=9 skipped=0 renamed=2 would_rename=0 missing=0 bad=0`.
- Verify dry run: `updated=0 skipped=9 renamed=0 would_rename=0 missing=0 bad=0`.
- Post read-back: `9` metadata rows, `9` tag rows, `267` xref rows, `2205` instruction rows, `9` decompile exports, and `16` CTGALoader vtable rows.
- Focused probe: `tools/ghidra_texture_tga_wave513_probe.py --check`.
- Queue refresh after Wave513: `6078` functions, `2400` commented, `3678` commentless, `1614` exact-undefined signatures, and `1431` `param_N` signatures.
- Current whole-project telemetry proxy: comment-backed `2400/6078 = 39.49%`; strict comment-plus-clean-signature proxy `2343/6078 = 38.55%`.
- Backup verified at `G:\GhidraBackups\BEA_20260517-193930_post_wave513_texture_tga_verified` with `19` files, `158403463` bytes, `MissingCount=0`, `ExtraCount=0`, and `HashDiffCount=0`.

## Claim Boundary

This is static Ghidra metadata evidence only. It improves texture-cache, texture-lifecycle, CTGALoader TGA decode, and 24-bit TGA writer readability. It does not prove runtime rendering behavior, runtime image loading, screenshot behavior, malformed-file behavior, exact CTexture/CTGALoader/CImageLoader class layouts, BEA launch behavior, game patching, or rebuild parity.
