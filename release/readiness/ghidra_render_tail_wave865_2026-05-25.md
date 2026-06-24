# Ghidra Render Tail Wave865 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-25
Scope: `render-tail-wave865`

Wave865 render tail saved comments, tags, and signatures for nine important render/cutscene/landscape/imposter/cache/memory connector rows from `0x0053df40 CDXEngine__RenderTexturedBeamQuad` through `0x00549310 CDXMemoryManager__LogDebugStats`. The pass made no renames, no function-boundary changes, and no executable-byte changes.

These rows are not low-importance tail code. They are low local-evidence-density but high connective/system-importance helpers: render quads, cutscene track-slot writes, frontend particle setup, landscape texture-cache generation, imposter billboard geometry, landscape reset/invalidation, developer cache building, and memory debug statistics. Treat this as saved static retail Ghidra metadata/decompile/xref evidence only, not runtime render/cutscene/cache behavior or rebuild proof.

Representative anchors:

| Address | Saved signature | Evidence |
| --- | --- | --- |
| `0x0053df40 CDXEngine__RenderTexturedBeamQuad` | `void __thiscall CDXEngine__RenderTexturedBeamQuad(void * this, float start_x, float start_y, float start_z, float start_w_or_pad, float end_x, float end_y, float end_z, float end_w_or_pad, int reserved_flags)` | Three no-boundary callsites `0x004e9fc9`, `0x004ea110`, and `0x004ea2f0`; global matrix seed `0x0089d640`; obtains a `CVBufTexture` from `this+0x4ec`; writes four beam vertices and six indices. |
| `0x0053f010 CCutscene__SetTrackSlotByFlag` | `void __thiscall CCutscene__SetTrackSlotByFlag(void * this, int track_slot, int use_primary_track)` | `CGame__LoadLevel`, `CCutscene__Start`, `CCutscene__Stop`, and `CCutscene__Update` callers pass two stack arguments; body writes `track_slot` to `this+0x4cc` or `this+0x4d0`. |
| `0x00540c30 CDXFrontEnd__SetupRenderMatricesAndProjection` | `void __cdecl CDXFrontEnd__SetupRenderMatricesAndProjection(void)` | `CDXFrontEnd__VFunc_07_00540fb0` caller; seeds matrices from `0x008a9788`, updates render-info/light matrix blocks, calls particle manager interpolation/update, device slot `+0xc4`, render state `0xf`, and `CDXEngine__RenderParticleTexturePass`. |
| `0x00541f50 CDXEngine__GenerateLandscapeCacheTileChunk` | `void __thiscall CDXEngine__GenerateLandscapeCacheTileChunk(void * this, int detail_shift, void * source_cache_info, void * source_pixels, int tile_x, int tile_y, int dest_x, int dest_y, int tile_count_x, int tile_count_y, int output_stride_pixels)` | Called by `CDXEngine__BuildLandscapeTextureCache`; samples source pixels, walks landscape rows through `this+0x20/0x28`, uses mask fields `this+0x10c4/0x10c8`, blends neighbor lanes, and writes ARGB cache pixels. |
| `0x00542f90 CDXImposter__BuildQuadGeometry` | `void __thiscall CDXImposter__BuildQuadGeometry(void * this, float * center_vec, float * right_vec, float * up_vec, float vertex_alpha, int reserved_14, float u0, float v0, float u1, float v1, int use_secondary_buffer)` | `CDXEngine__RenderImposterBillboardSet` caller; normalizes a cross product, selects `CVBufTexture` globals `0x008aa8b4` or `0x008aa8cc`, writes four billboard vertices and six indices. |
| `0x00544fb0 CDXLandscape__ResetWrapper` | `void __thiscall CDXLandscape__ResetWrapper(void * this, int reset_x, int reset_y)` | `CEngine__ResetPos` forwards two stack values and `engine+0x10`; wrapper ignores the stack values and calls `CDXLandscape__Reset(this)`. |
| `0x005473b0 CDXEngine__InvalidateLandscapeTilesAndPatchSlots` | `void __thiscall CDXEngine__InvalidateLandscapeTilesAndPatchSlots(void * this, int min_x, int min_y, int max_x, int max_y, int force_full_rebuild)` | `CStaticShadows__UpdateVisibility` and `CDXEngine__ApplyNavMapConsoleToggle_Thunk` callers; clamps a 64x64 tile range, marks patch-slot bytes with `0x80`, calls `CLandscapeTexture__UpdateTileRange`, and full-rebuild path resets patch managers/cache entries. |
| `0x00547860 CDXEngine__BuildLandscapeTextureCache` | `void __cdecl CDXEngine__BuildLandscapeTextureCache(void)` | No-argument developer/cache-builder path via wrapper `0x00544706`; logs `Building texture cache...`, writes `ps2data/LandscapeTextureCache` outputs, calls `CDXEngine__GenerateLandscapeCacheTileChunk`, `DXPalletizer__Palletize`, and memory frees. |
| `0x00549310 CDXMemoryManager__LogDebugStats` | `void __thiscall CDXMemoryManager__LogDebugStats(void * this)` | `CLTShell__RunFrontEndAndGameLoop` and `CLTShell__RunStressTestLevelLoop` call global memory manager `0x009c3df0`; logs separators, dispatches `CMemoryHeap__LogStats`, and formats heap peak/size lines. |

Read-back evidence:

- `ApplyRenderTailWave865.java dry`: `updated=0 skipped=9 renamed=0 would_rename=0 signature_updated=9 comment_only_updated=0 missing=0 bad=0`
- `ApplyRenderTailWave865.java apply`: `updated=9 skipped=0 renamed=0 would_rename=0 signature_updated=9 comment_only_updated=0 missing=0 bad=0`
- `ApplyRenderTailWave865.java final dry`: `updated=0 skipped=9 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: 9 metadata rows, 9 tag rows, 20 xref rows, 1542 function-body instruction rows, and 9 decompile rows.
- Queue after Wave865: 6105 total, 5819 commented, 286 commentless, 0 exact-undefined signatures, 0 `param_N`, comment-backed proxy `5819/6105 = 95.32%`, strict clean-signature proxy `5819/6105 = 95.32%`.
- Next raw commentless row: `0x00549570 CMeshRenderer__RenderMeshCore`.
- Verified backup: `G:\GhidraBackups\BEA_20260525-160100_post_wave865_render_tail_verified`, 19 files, 172329863 bytes, `DiffCount=0`.

What this proves:

- The nine target function rows exist in the saved Ghidra project.
- The saved comments and tags include `render-tail-wave865` and `wave865-readback-verified`.
- The saved signatures match the static caller stack shapes and observed calling conventions.
- The queue moved from 295 commentless rows after Wave864 to 286 after Wave865.

What remains unproven:

- Exact source identity and exact concrete layouts.
- Runtime rendering, cutscene, landscape-cache, imposter, or memory-debug behavior.
- BEA patching behavior.
- Rebuild parity.
