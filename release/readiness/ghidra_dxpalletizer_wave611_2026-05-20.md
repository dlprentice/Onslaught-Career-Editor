# Ghidra DXPalletizer Wave611

Status: ready
Date: 2026-05-20

## Scope

Wave611 saved signature/comment/tag hardening for the DXPalletizer color-quantization and swizzle island:

- `0x0054e500 DXPalletizer__InsertColor`
- `0x0054e670 DXPalletizer__BuildPalette`
- `0x0054e6e0 DXPalletizer__AssignPaletteIndices`
- `0x0054e790 DXPalletizer__CollapseOctreeNode`
- `0x0054e950 DXPalletizer__FreeOctreeNode`
- `0x0054e9d0 DXPalletizer__Palletize`
- `0x0054ef70 DXPalletizer__FindNearestColor`
- `0x0054f090 DXPalletizer__SwizzleBlock`
- `0x0054f380 DXPalletizer__SwizzleTexture`

The pass made no renames. The evidence is static retail Ghidra decompile, instruction, xref, callsite, debug-path, and post-save tag read-back. Runtime texture output and rebuild parity remain unproven.

## What Changed

- The seven octree/palette helpers now carry explicit thiscall receiver signatures, including `DXPalletizer__Palletize(this, source_rgba, width, height, requested_palette_size, out_indices_ref, out_palette_ref, source_has_alpha, allocate_outputs, swizzle_output, preserve_alpha, expand_half_palette, copy_palette_tiles)`.
- The two texture swizzle helpers now carry cdecl stack-argument signatures: `DXPalletizer__SwizzleBlock(block_width, block_height, src_block, dst_block)` and `DXPalletizer__SwizzleTexture(width, height, src_indices, dst_swizzled)`.
- `CDXEngine__BuildLandscapeTextureCache` callsite `0x005479a6` proves the main DXPalletizer entry from the landscape texture-cache path.
- Internal callsites prove the octree helper family: insert `0x0054eb41`, palette build `0x0054ebc6`, assign indices `0x0054eb7a`/`0x0054eba3`, collapse `0x0054ebb8`, free `0x0054eefe`, nearest color `0x0054ec7c`, and swizzle `0x0054ecc0`.
- Swizzle evidence references table/data addresses `0x00651760`, `0x00651960`, `0x00651c60`, and `0x00651ce0`; palette expansion evidence references `DAT_006fbe44/DAT_006fbe54`.

## Evidence

- Apply script: `tools/ApplyDXPalletizerWave611.java`
- Focused probe: `tools/ghidra_dxpalletizer_wave611_probe.py`
- Scratch evidence: `subagents/ghidra-static-reaudit/wave611-dxpalletizer-0054e500-0054f380/`
- Initial clean dry: `updated=0 skipped=9 renamed=0 would_rename=0 missing=0 bad=0`
- Preserved correction log 1: `apply-initial-thiscall-mismatch.log` reported `updated=2 skipped=0 renamed=0 would_rename=0 missing=0 bad=7` after the first script omitted explicit thiscall receivers and Ghidra inserted `this` into saved signatures.
- Preserved correction log 2: `apply-corrected-this-pointer-mismatch.log` reported `updated=6 skipped=2 renamed=0 would_rename=0 missing=0 bad=1` after `DXPalletizer__FindNearestColor` read back its receiver as `void * this`.
- Final dry/apply after correction: `updated=0 skipped=9 renamed=0 would_rename=0 missing=0 bad=0`
- Read-back exports verified `9` metadata rows, `9` tag rows, `15` xref rows, `2349` instruction rows, `9` decompile rows, and `435` callsite instruction rows.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260519-231515_post_wave611_dxpalletizer_verified`
  - `sourceFileCount=19`
  - `destFileCount=19`
  - `sourceBytes=161549191`
  - `destBytes=161549191`
  - `DiffCount=0`

The mismatch logs are retained as evidence of read-back correction. The accepted final state is the idempotent final dry/apply pair plus the post-state exports.

## Queue Delta

Post-Wave611 queue telemetry:

- Total functions: `6093`
- Commented functions: `3134`
- Commentless functions: `2959`
- Exact-undefined signatures: `1292`
- `param_N` signatures: `1059`
- Comment-backed proxy: `3134/6093 = 51.44%`
- Strict clean-signature proxy: `3089/6093 = 50.70%`
- Next queue head: `0x0054f6e0 CDXEngine__ShutdownParticleSystemBundle`

Delta from Wave610:

- `+9` commented rows
- `-9` commentless rows
- `-9` exact-undefined signatures
- `0` `param_N` signatures
- `+9` strict clean rows

## Limits

This is static retail evidence only. Exact source identity, exact DXPalletizer workspace/octree-node/palette/swizzle layouts, exact console texture format identity, runtime texture output, BEA patching, and rebuild parity remain unproven.
