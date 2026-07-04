# DXKempyCube.cpp Functions

> Source File: DXKempyCube.cpp | Binary: BEA.exe
> Debug Path: 0x00650a88 (`[maintainer-local-source-export-root]\DXKempyCube.cpp`)

## Overview

DirectX environment cube map rendering. Implements skybox and environment reflection cube mapping for the game's rendering system. "Kempy" likely refers to a developer's name or internal codename.

**Status:** Wave600 extends the earlier Wave420 filename helper into the adjacent cube texture-slot cleanup, texture/VB setup, `SetKempyCube` wrapper, and render helper cluster. Wave1033 corrected stale texture-release helper wording for the release helper to `CTexture__DecrementRefCountFromNameField`. This is still static saved-Ghidra evidence only, not runtime cube-render proof or exact source-body identity.

## Debug Path Location

- **Address**: 0x00650a88
- **String**: `[maintainer-local-source-export-root]\DXKempyCube.cpp`

## Functions

| Address | Name | Purpose | Status |
|---------|------|---------|--------|
| `0x0048de30` | `CDXEngine__FormatCubeTextureFilename` | Formats one Kempy cube texture path from output buffer, cube index, and suffix index | Saved signature/comment in Wave420 |
| `0x00544040` | `CDXEngine__ClearKempyCubeTextureSlots` | Clears the five Kempy cube texture slots in the `engine+0x498` resource block | Saved signature/comment in Wave600 |
| `0x00544060` | `CDXEngine__ReleaseKempyCubeTexturesAndVertexBuffer` | Releases five texture refs through `CTexture__DecrementRefCountFromNameField(texture+8)` and global CVBuffer `0x008aa908` | Saved signature/comment in Wave600; stale helper wording corrected in Wave1033 |
| `0x005440a0` | `CDXEngine__InitKempyCubeTexturesAndVertexBuffer` | Calls the formatter in a five-iteration loop, loads the cube textures, and initializes static cube vertex-buffer data | Saved signature/comment in Wave600 |
| `0x005441a0` | `CDXEngine__InitKempyCubeResources` | `CEngine__SetKempyCube` wrapper around the texture/VB initializer | Saved signature/comment in Wave600 |
| `0x005441b0` | `CDXEngine__RenderKempyCubeFaces` | Render helper reached from `CDXEngine__Render`; loops the five texture slots and uses global CVBuffer `0x008aa908` | Saved signature/comment in Wave600 |

## Notes

- Referenced in the _index.md as having 5 functions (CDXKempyCube - environment cube mapping, skybox rendering)
- Part of the DX rendering subsystem
- Wave600 proves the nearby saved Ghidra metadata/xref/instruction evidence for the texture-slot lifecycle, setup, and render helpers, but runtime cube behavior and exact layouts remain unproven.
- Wave1033 (`cdxengine-render-resource-review-wave1033`) re-read `0x00544040 CDXEngine__ClearKempyCubeTextureSlots` as a primary target and `0x00544060 CDXEngine__ReleaseKempyCubeTexturesAndVertexBuffer` as corrected context, saved the `CTexture__DecrementRefCountFromNameField` wording at `0x00544060`, and marked it with `wave1033-readback-verified`. Probe token anchor: Wave1033; cdxengine-render-resource-review-wave1033; 0x0044a640 CDXEngine__SetOverlaySlotVisibilityByPlayerView; 0x0053d3a0 CDXEngine__ReleaseDefaultTextureAndMeshRefs; 0x00542a50 CDXEngine__BuildDirectionalSampleRing; 0x00544040 CDXEngine__ClearKempyCubeTextureSlots; 0x00544060 CDXEngine__ReleaseKempyCubeTexturesAndVertexBuffer; CTexture__DecrementRefCountFromNameField; supersedes older CHud__DecrementCounter9C wording; 635/1408 = 45.10%; 864/1493 = 57.87%; 500/500 = 100.00%; 6238/6238 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260601-051834_post_wave1033_cdxengine_render_resource_review_verified; two comment/tag corrections.
- Related to: DXLandscape.cpp, DXTexture.cpp

## Wave600 CDXEngine Kempy Cube Resource/Render Cluster (2026-05-19)

Wave600 saved clean signatures/comments/tags for the adjacent Kempy cube cluster:

```text
void * __fastcall CDXEngine__ClearKempyCubeTextureSlots(void * kempy_cube_resources)
void __fastcall CDXEngine__ReleaseKempyCubeTexturesAndVertexBuffer(void * kempy_cube_resources)
void __thiscall CDXEngine__InitKempyCubeTexturesAndVertexBuffer(void * this, int cube_index)
void __thiscall CDXEngine__InitKempyCubeResources(void * this, int cube_index)
void __fastcall CDXEngine__RenderKempyCubeFaces(void * kempy_cube_resources)
```

`CEngine__Init` allocates a `0xa14` block at `engine+0x498` and calls `CDXEngine__ClearKempyCubeTextureSlots`, while `CEngine__Shutdown` calls `CDXEngine__ReleaseKempyCubeTexturesAndVertexBuffer` for the same block. `CEngine__SetKempyCube` calls `CDXEngine__InitKempyCubeResources`, which forwards one cube index to `CDXEngine__InitKempyCubeTexturesAndVertexBuffer` and returns with `RET 0x4`. `CDXEngine__Render` calls `CDXEngine__RenderKempyCubeFaces` with `engine+0x498`.

The texture/VB initializer formats five cube texture filenames through `CDXEngine__FormatCubeTextureFilename`, loads textures with `CTexture__FindTexture`, recreates global CVBuffer `0x008aa908`, creates a `20`-vertex/`20`-byte/FVF `0x102` buffer, copies `100` dwords from `0x006508f0`, and unlocks the buffer. The render helper copies matrix data from `0x008aa8d8`, binds `0x008aa908`, resolves animated frames through `CDXTexture__GetAnimatedFrame`, and issues the D3D draw path.

Read-back evidence: `ApplyCDXEngineKempyCubeWave600.java` dry/apply/final dry reported `updated=0 skipped=5 renamed=0 would_rename=2 missing=0 bad=0`, then `updated=5 skipped=0 renamed=2 would_rename=0 missing=0 bad=0`, then `updated=0 skipped=5 renamed=0 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`. Post exports verified `5` metadata rows, `5` tag rows, `5` xref rows, `1505` instruction rows, and `5` decompile rows.

Queue telemetry after the pass: `6093` total, `3079` commented, `3014` commentless, `1331` exact-undefined signatures, `1075` `param_N`, comment-backed proxy `3079/6093 = 50.53%`, strict clean-signature proxy `3034/6093 = 49.79%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260519-174509_post_wave600_cdxengine_kempy_cube_verified`, `19` files, `161188743` bytes, manifest hash `d86b1630787846993bbd52f40f4821e89ecc5f13e8fa0afddccbe4feb8725247`. Next queue head: `0x00544770 CDXLandscape__ReleaseOwnedResources`.

This is static saved-Ghidra evidence only. Runtime cube rendering, visible sky/reflection behavior, exact Kempy resource-block/texture/CVBuffer/vertex/render-state/matrix layouts, exact source identity, BEA patching, and rebuild parity remain unproven.

## Wave 420 Static Re-Audit Note (2026-05-14)

`CDXEngine__FormatCubeTextureFilename` is now saved as:

```text
void __cdecl CDXEngine__FormatCubeTextureFilename(char * out_path, int cube_index, int suffix_index)
```

Instruction read-back shows the helper masks `cube_index` to one byte, selects one of five suffix-string pointers by `suffix_index`, and calls `sprintf` with the `cube_%02d_%s.tga` format string. Runtime texture loading/render behavior remains unproven.

## Expected Functionality

- CDXKempyCube class
- Skybox rendering (6-face cube)
- Environment reflection mapping
- Cube map texture management

## TODO

1. [ ] Find xrefs to debug path string 0x00650a88
2. [ ] Analyze CDXKempyCube class
3. [ ] Document cube face rendering order
4. [ ] Map reflection coordinate system

---

*Stub created: 2025-12-16 - Pending xref discovery*
