# Ghidra Particle Texture Wave612

Status: ready
Date: 2026-05-20

## Scope

Wave612 saved signature/comment/tag hardening for the particle texture render and resource-lifecycle island:

- `0x0054f6e0 CDXEngine__ShutdownParticleSystemBundle`
- `0x0054f740 CDXEngine__ResetParticleSystemBundle`
- `0x0054f760 CDXEngine__SetParticleRenderStatePreset`
- `0x0054f7e0 CDXEngine__RenderParticleTexturePass`
- `0x0054fbc0 DXParticleTexture__GetOrCreate`
- `0x0054fd80 DXParticleTexture__ReleaseAll`
- `0x0054fde0 DXParticleTexture__RestoreAll`
- `0x0054fee0 DXParticleTexture__DestroyAll`
- `0x0054ff20 DXParticleTexture__RenderAll`
- `0x00550110 DXParticleTexture__Release`
- `0x00550180 DXParticleTexture__AddTriangleIndices`
- `0x005501b0 DXParticleTexture__GetIndexBuffer`
- `0x00550220 DXParticleTexture__Render`

The pass made no renames. The evidence is static retail Ghidra decompile, instruction, xref, callsite, and post-save tag read-back. Runtime particle output and rebuild parity remain unproven.

## What Changed

- The four engine-side particle helpers now carry explicit signatures for bundle shutdown/reset, the no-argument render-state preset, and the particle texture render pass.
- The global DXParticleTexture list helpers now carry cdecl signatures for get-or-create, release/restore/destroy all, and render all.
- The object methods now carry explicit thiscall receiver signatures for resource release, triangle-index append, index-buffer acquisition, and node render.
- `CParticleDescriptor__Load` callsite `0x004c57b9` proves the `DXParticleTexture__GetOrCreate(texture_path, texture_type)` ABI: two pushed args, `ADD ESP, 0x8`, returned node pointer stored at descriptor `+0x64`.
- `CDXEngine__RenderParticleTexturePass` callsite `0x0054f9ec` proves the global `DXParticleTexture__RenderAll` render walk after particle view/projection setup.
- `DXParticleTexture__DestroyAll` callsite `0x0054fefd` proves the per-node `DXParticleTexture__Release(this)` method before freeing each global-list node.
- `DXParticleTexture__AddTriangleIndices` now records the `RET 0x0c` ABI and 16-bit index writes through the node CVBufTexture at `+0x198`.

## Evidence

- Apply script: `tools/ApplyParticleTextureBundleWave612.java`
- Focused probe: `tools/ghidra_particle_texture_wave612_probe.py`
- Scratch evidence: `subagents/ghidra-static-reaudit/wave612-particle-texture-0054f6e0-00550220/`
- Initial clean dry: `updated=0 skipped=13 renamed=0 would_rename=0 missing=0 bad=0`
- Apply: `updated=13 skipped=0 renamed=0 would_rename=0 missing=0 bad=0`
- Final dry: `updated=0 skipped=13 renamed=0 would_rename=0 missing=0 bad=0`
- Read-back exports verified `13` metadata rows, `13` tag rows, `23` xref rows, `3393` instruction rows, `13` decompile rows, and `667` callsite instruction rows.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260519-234626_post_wave612_particle_texture_verified`
  - `sourceFileCount=19`
  - `destFileCount=19`
  - `sourceBytes=161581959`
  - `destBytes=161581959`
  - `DiffCount=0`

## Queue Delta

Post-Wave612 queue telemetry:

- Total functions: `6093`
- Commented functions: `3147`
- Commentless functions: `2946`
- Exact-undefined signatures: `1283`
- `param_N` signatures: `1056`
- Comment-backed proxy: `3147/6093 = 51.65%`
- Strict clean-signature proxy: `3102/6093 = 50.91%`
- Next queue head: `0x00550380 CDXPatch__Constructor`

Delta from Wave611:

- `+13` commented rows
- `-13` commentless rows
- `-9` exact-undefined signatures
- `-3` `param_N` signatures
- `+13` strict clean rows

## Limits

This is static retail evidence only. Exact particle bundle, DXParticleTexture, CParticleDescriptor, CTexture, CVBufTexture, shader/global, and render-state layouts remain partial; runtime particle output, concrete D3D device behavior, BEA patching, and rebuild parity remain unproven.
