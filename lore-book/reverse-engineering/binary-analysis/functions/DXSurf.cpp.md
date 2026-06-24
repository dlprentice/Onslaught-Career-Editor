# DXSurf.cpp Functions

> Source file: `C:\dev\ONSLAUGHT2\DXSurf.cpp`
> Debug path address: `0x006525a0`
> Last updated: 2026-05-20

## Current Status

Wave832 Texture/Surface Prelude (`texture-surface-prelude-wave832`, `wave832-readback-verified`) hardened the adjacent global texture/surface list unlink row `0x004f2790 CDXSurf__UnlinkNodeFromGlobalList` as `void __fastcall CDXSurf__UnlinkNodeFromGlobalList(void * texture_base)` and paired it with texture-base initialization evidence for `0x004f2710 CTextureBase__Init` as `void * __fastcall CTextureBase__Init(void * texture_base)`. These rows are important connective/static infrastructure for the shared list that ties texture-base construction to CDXSurf teardown.

Probe anchors: `Wave832 Texture/Surface Prelude`, `texture-surface-prelude-wave832`, `0x004f2710 CTextureBase__Init`, `void * __fastcall CTextureBase__Init(void * texture_base)`, `0x004f2790 CDXSurf__UnlinkNodeFromGlobalList`, `void __fastcall CDXSurf__UnlinkNodeFromGlobalList(void * texture_base)`, `DAT_0083d9b0`, `JCLTEX #%d`, `0x00556ce1`, `0x00556e70`, `5654/6098 = 92.72%`, `0x004f5b70 CParticleDescriptor__SetIndexedParam`, `G:\GhidraBackups\BEA_20260524-230834_post_wave832_texture_surface_prelude_verified`.

Static evidence: `CDXSurf__dtor` at `0x00556e70` and unwind rows `0x005d7d30`/`0x005d7d50` load `ECX` with `object+0x08` or null before calling/jumping to `CDXSurf__UnlinkNodeFromGlobalList`, correcting the stale cdecl stack-argument signature. The body walks `DAT_0083d9b0` through `node+0xa0` links, compares against `texture_base-0x08`, and unlinks by updating the previous node link or the global head. The paired init row uses `JCLTEX #%d` and `0x00556ce1` evidence in [`texture.cpp`](texture.cpp/_index.md). Post-Wave832 queue telemetry is `5654/6098 = 92.72%`, next raw head `0x004f5b70 CParticleDescriptor__SetIndexedParam`, and verified backup `G:\GhidraBackups\BEA_20260524-230834_post_wave832_texture_surface_prelude_verified`.

Wave1028 static re-audit (`cdx-render-resource-lifecycle-review-wave1028`) re-read `0x004f2790 CDXSurf__UnlinkNodeFromGlobalList` with context `0x004f2710 CTextureBase__Init` and no mutation. Fresh exports verified the same ECX-only global list unlink shape, `CDXSurf__dtor`/unwind caller set, and `DAT_0083d9b0` node walk while keeping runtime texture/surface teardown behavior and exact layout proof separate. Verified backup: `G:\GhidraBackups\BEA_20260601-021726_post_wave1028_cdx_render_resource_lifecycle_review_verified`.

Wave616 hardened the saved Ghidra metadata for the core `CDXSurf` cluster without renames or function-boundary changes. The pass covers the sprite wrapper, water-strip setup/teardown/render path, destructor pair, render-target cleanup, and setup helper. Read-back exports verified `15` context metadata rows plus `2` expected missing unbounded vtable targets, `15` tag rows plus the same misses, `169` xref rows, `1445` instruction rows, `15` decompile rows plus `2` misses, and `32` vtable-slot rows.

Queue telemetry after Wave616 is `6093` total functions, `3172` commented, `2921` commentless, `1260` exact-undefined signatures, and `1056` `param_N` signatures. Comment-backed proxy is `3172/6093 = 52.06%`; strict clean-signature proxy is `3127/6093 = 51.32%`. The verified Ghidra backup is `G:\GhidraBackups\BEA_20260520-020900_post_wave616_cdxsurf_core_verified` with `19` files, `161614727` bytes, and `DiffCount=0`.

Runtime water/render behavior remains unproven. Exact `CDXSurf`, `CVBuffer`, `CVBufTexture`, `CDXTexture`, render-state, D3D, and serialized wave-strip layouts, concrete source identity, BEA patching, and rebuild parity remain deferred.

## Class: CDXSurf

Vtable start: `0x005e59a0`.

Wave616 bounds only the slots below through static saved-Ghidra evidence. Slots after `0x1c` quickly run into non-CDXSurf-looking data and other tables; do not treat the 32-row peek as a complete CDXSurf vtable.

| Slot | Address | Pointer | Status |
| ---: | --- | --- | --- |
| `0x00` | `0x005e59a0` | `0x00556d70 CDXSurf__ScalarDeletingDestructor` | Bounded |
| `0x04` | `0x005e59a4` | `0x00557a90 CDXTexture__LoadTextureFromFile_Core` | Existing context row |
| `0x08` | `0x005e59a8` | `0x00557060 CTextureSequence__EnsureLoaded` | Existing context row |
| `0x0c` | `0x005e59ac` | `0x005572c0 CTextureSequence__ReleaseIfLoaded` | Existing context row |
| `0x10` | `0x005e59b0` | `0x00558600` | No Ghidra function boundary yet |
| `0x14` | `0x005e59b4` | `0x00556e90` | No Ghidra function boundary yet |
| `0x18` | `0x005e59b8` | `0x00556fc0 CDXSurf__SetupSurface` | Bounded |
| `0x1c` | `0x005e59bc` | `0x00405930 SharedVFunc__ReturnZero_00405930` | Shared inherited helper |

## Wave616 Function Map

| Address | Name | Saved signature | Evidence summary |
| --- | --- | --- | --- |
| `0x005563d0` | `CDXSurf__RenderSurface` | `void __cdecl CDXSurf__RenderSurface(float draw_x, float draw_y, float draw_z, void * texture_or_resource, float draw_width, float draw_height, float draw_depth, int color_a, int color_b, float scale_x, float scale_y)` | Heavy frontend/HUD/game sprite wrapper. Xrefs include `CConsole__RenderLoadingScreen`, frontend draw helpers, `CGame__DrawGameStuff`, `CGameInterface__Render`, `CFEPMain__Render`, and level/multiplayer frontend render paths. Body forwards to `CVBufTexture__DrawSpriteEx` with default UV bounds `0.0/1.0/0.0/1.0`. |
| `0x00556460` | `CDXSurf__Init` | `void __thiscall CDXSurf__Init(void * this)` | ECX-only initializer clears the strip-array pointer at `+0x00`, wave texture pointer at `+0x08`, secondary field at `+0x04`, and initialized flag at `+0x0c`. |
| `0x00556470` | `CDXSurf__LoadWavesTexture` | `void __thiscall CDXSurf__LoadWavesTexture(void * this)` | `CDXLandscape__Reset` callsite `0x005453ac`; resolves `mixers\\waves.tga` through `CTexture__FindTexture` with arguments `5,0,-1,1,1` and stores the pointer at `this+0x8`. |
| `0x00556490` | `CDXSurf__CreateSurfaceArray` | `void __thiscall CDXSurf__CreateSurfaceArray(void * this, void * chunk_reader)` | `CResourceAccumulator__ReadResourceFile` callsite `0x004d77f7`; gates on count above `7`, allocates `count*0x0c+4` from `DXSurf.cpp` line `0x38`, constructs 0x0c-byte strip entries with `CDXSurf__DestroyBuffers`, reads each strip count at `+0x8`, calls `CDXSurf__CreateSurfaceStrip`, then sets `this+0x0c`. |
| `0x005565b0` | `CDXSurf__DestroyBuffers` | `void __fastcall CDXSurf__DestroyBuffers(void * surface_strip)` | Vector cleanup callback used by create/destroy paths. Calls vtable slot `0` with delete flag `1` for two `CVBuffer` pointers at strip `+0x00` and `+0x04`. |
| `0x005565d0` | `CDXSurf__CreateSurfaceStrip` | `void __thiscall CDXSurf__CreateSurfaceStrip(void * this, void * chunk_reader)` | Called from `CDXSurf__CreateSurfaceArray` at `0x0055655f`. Allocates two `0x2c` `CVBuffer` objects from `DXSurf.cpp` lines `0xa8` and `0xab`, creates buffers with `count*2+2` vertices and shader `0x242`, reads strip positions, fills sine-offset wave vertices, handles `DAT_0082b4a4` UV ordering, writes `0x00ffffff` / `0xc0ffffff` / `0xff000000` colors, and unlocks both buffers. |
| `0x005569e0` | `CDXSurf__Destroy` | `void __thiscall CDXSurf__Destroy(void * this)` | `CDXLandscape__Shutdown` callsite `0x00544f8b`; clears initialized flag, destroys the strip array through `CDXLandscape__DestroyArrayWithCallback`, frees the count header, clears the array pointer, and releases the wave texture at `this+0x8` through `CTexture__DecrementRefCountFromNameField`. |
| `0x00556a30` | `CDXSurf__Render` | `void __thiscall CDXSurf__Render(void * this, byte validated_mode)` | `CWaterRenderSystem__RenderMainPass` callsites `0x0055bf37` and `0x0055d520`; validates shared water state when requested, sets projection depth bias index `4`, resolves the animated waves texture frame, binds render state, iterates strip entries, sets each stream source, draws D3D triangle strips through device vtable `+0x144`, marks accepted in validated mode, then resets depth bias. |
| `0x00556d70` | `CDXSurf__ScalarDeletingDestructor` | `void * __thiscall CDXSurf__ScalarDeletingDestructor(void * this, byte delete_flags)` | Vtable `0x005e59a0` slot `0`; calls `CDXSurf__dtor`, frees through `CDXMemoryManager__Free` when `delete_flags & 1`, and returns `this`. |
| `0x00556d90` | `CDXSurf__dtor` | `void __fastcall CDXSurf__dtor(void * this)` | Reached from the scalar-deleting destructor and a destructor thunk at `0x0053a140`. Installs vtable `0x005e59a0`, unlinks render-object lists, optionally reports nonzero texture refcounts through `Texture: %s refcount %d`, clears texture entries, runs base/device cleanup, and calls Wave832 `0x004f2790 CDXSurf__UnlinkNodeFromGlobalList` with `ECX=this+0x08` or null. The decompile still shows an `unaff_ESI` artifact. |
| `0x00556f80` | `CDXSurf__DestroyRenderTarget` | `void __thiscall CDXSurf__DestroyRenderTarget(void * this)` | `CFEPGoodies__FreeUpGoodyResources` callsite `0x0045cd7e`; releases resource pointer at `this+0x140`, destructs/frees a `CVBufTexture` when still present, clears `this+0x140`, and returns. |
| `0x00556fc0` | `CDXSurf__SetupSurface` | `bool __thiscall CDXSurf__SetupSurface(void * this, int setup_value, short format_word, int size_x, int size_y, byte setup_flags, int extra_config)` | Vtable `0x005e59a0` slot `+0x18` and `CDXBattleLine__Constructor` computed callsites; `RET 0x18`. Copies default surface name from `0x00662b2c` into `this+0x8`, stores setup fields at `+0xac/+0xb0/+0x13c/+0x144/+0x148/+0x14c/+0x150`, increments `this+0xa4`, invokes vtable slot `+0x04`, and returns true on nonnegative result. |

## Constants And Strings

| Address | Value / Role |
| --- | --- |
| `0x0065258c` | `mixers\\waves.tga` |
| `0x006525a0` | Source debug path pointer for `DXSurf.cpp` |
| `0x00652660` | `Texture: %s refcount %d` |
| `0x0082b4a4` | UV ordering/platform flag observed in strip creation |
| `0x00888a50` | D3D device pointer used by render path |
| `0x009cc1a0` | Render-mode/global flag used by render path |

## Deferred Work

- Recover or intentionally defer function boundaries for vtable pointer targets `0x00558600` and `0x00556e90`.
- Prove or reject exact source-body identity for the CDXSurf methods against retail behavior rather than debug-path proximity.
- Recover concrete `CDXSurf`, strip-entry, `CVBuffer`, `CVBufTexture`, `CDXTexture`, and render-state layouts.
- Prove runtime water rendering, Goodies render-target behavior, and D3D output through copied-profile runtime evidence.
- Keep BEA patching and rebuild parity out of scope until separate evidence exists.
