# Ghidra CEngine Lifecycle Resource Review Wave931 Readiness Note

Status: complete read-only static review
Date: 2026-05-27
Scope: `cengine-lifecycle-resource-review-wave931`

Wave931 re-reviewed six Wave911 focused CEngine lifecycle/resource candidates, plus five context helpers that anchor the CDXEngine wrapper and map-deserialize handoff. The review made no Ghidra mutation, no rename, no signature change, no function-boundary change, and no executable-byte change.

Primary targets:

| Address | Saved state | Fresh evidence |
| --- | --- | --- |
| `0x00449820 CEngine__ctor` | `void __fastcall CEngine__ctor(void * engine)` | Constructor installs `PTR_CEngine__Shutdown_005db270`, seeds near/far clip and viewpoint-adjacent fields, clears resource pointers including `+0x49c`, and sets the render-landscape flag at `+0x4a8`. |
| `0x00449890 CEngine__Shutdown` | `void __fastcall CEngine__Shutdown(void * engine)` | Xref from `0x0053d3e0 CDXEngine__Shutdown`; releases screen FX, shadows, trees, gamut, landscape/camera/water/map texture/HUD texture resources, calls `CMapTex__Reset` for the map-texture array, and trims VB/IB pool capacities. |
| `0x004499d0 CEngine__Init` | `int __fastcall CEngine__Init(void * engine)` | Xref from `0x0053d5f0 CDXEngine__Init`; registers hit-effect cvars plus `cg_renderlandscape` and `cg_drawpolybuckets`, allocates gamut/map texture/water/landscape/HUD/light resources, and initializes screen effects/shadows/trees. |
| `0x00449d50 CEngine__InitResources` | `void __fastcall CEngine__InitResources(void * engine)` | Xref from `0x0053d6d0 CDXEngine__InitResources`; calls zoom/blob-shadow resource setup, loads `hilight.tga`, `hiteffect.tga`, `cloak.tga`, and dispatches landscape cloud-shadow texture loading. |
| `0x00449dc0 CEngine__LoadAllNamedMeshes` | `void __thiscall CEngine__LoadAllNamedMeshes(void * this, void * dataFile)` | Xref from `0x0050b9c0 CWorld__LoadWorld`; uses one stack argument (`RET 0x4`), resets global named-mesh count, reports `Loading named meshes`, reads mesh names from the buffer, reuses existing entries via `stricmp`, and calls `CMesh__FindOrCreate` for new entries. |
| `0x0044a6e0 CEngine__Deserialize` | `void __thiscall CEngine__Deserialize(void * this, void * chunkReader)` | Xref from `0x004d7200 CResourceAccumulator__ReadResourceFile`; uses one stack argument (`RET 0x4`), reads the ENGN/map-texture count through `CChunkReader`, deserializes map textures through `this+0x49c`, then dispatches `CHeightField__DeserializeMapAndInitResources`. |

Context helpers:

| Address | Saved state | Fresh evidence |
| --- | --- | --- |
| `0x0044a020 CEngine__SetViewpoint` | `void __thiscall CEngine__SetViewpoint(void * this, int viewpoint, void * camera, void * viewport, void * player)` | Seven xrefs from `0x0046e460 CGame__Render`; copies viewport state, stores the player pointer, destroys any prior camera wrapper, and constructs `CInterpolatedCamera(camera)`. |
| `0x0044a1c0 CEngine__UpdatePos` | `void __thiscall CEngine__UpdatePos(void * this, void * camera)` | Xref from `0x0046eee0 CGame__MainLoop`; gates on render-landscape flag `+0x4a8`, reads landscape pointer `+0x10` and current viewpoint `+0x4ac`, and forwards to `CDXLandscape__SetTileData`. |
| `0x00491060 CHeightField__DeserializeMapAndInitResources` | `void __thiscall CHeightField__DeserializeMapAndInitResources(void * this, void * chunk_reader)` | Xref from `0x0044a6e0 CEngine__Deserialize`; reads map metadata, calls `CHeightField__Load`, initializes `CMixerMap`, and drives mixer/sky/water resource setup. |
| `0x0053d5f0 CDXEngine__Init` | `int __fastcall CDXEngine__Init(void * this)` | Xref from `0x0046c360 CGame__Init` and vtable DATA `0x005e4fc8`; wraps `CEngine__Init`, initializes CDXEngine render/resource fields, registers gamma/reflection controls, and initializes `CDXPatchManager`. |
| `0x0053d6d0 CDXEngine__InitResources` | `void __fastcall CDXEngine__InitResources(void * this)` | Xref from `0x0046e240 CGame__RunLevel` and vtable DATA `0x005e4fcc`; wraps `CEngine__InitResources`, loads `meshtex/default.tga`, `meshtex/outline.tga`, `meshtex/EdArrow.tga`, acquires `default.msh`, and caches `Sun_Sprite`. |

Evidence:

- Primary exports: 6 metadata rows, 6 tag rows, 10 xref rows, 555 instruction rows, and 6 decompile rows.
- Context exports: 5 metadata rows, 5 tag rows, 13 xref rows, 223 instruction rows, and 5 decompile rows.
- Source-reference context from Stuart's `engine.cpp` matches the broad constructor/init/resource/name-mesh/viewpoint/update/deserialize shape, while the loaded Steam Ghidra database remains authoritative for names, signatures, xrefs, and field offsets.
- Composer 2.5 adversarial consult agreed this is a read-only review wave with no mutation-grade correction.
- Wave911 focused re-audit progress after Wave931: `122/1408 = 8.66%`.
- Static export-contract closure remains `6113/6113 = 100.00%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260527-235851_post_wave931_cengine_lifecycle_resource_review_verified`, 19 files, 173247367 bytes, `DiffCount=0`.

What this proves:

- The saved names, signatures, tags, xrefs, instruction bodies, and decompiles for the six primary CEngine lifecycle/resource rows remain internally consistent with prior bounded claims.
- CDXEngine init/resource wrappers and the map-deserialize context still support the CEngine lifecycle/resource ownership model.
- The post-100 re-audit can treat this CEngine lifecycle/resource cluster as reviewed, source-compatible, and no-mutation for the static database.

What remains unproven:

- Runtime engine boot, shutdown, resource loading, render, or device behavior.
- Exact `CEngine`, `CDXEngine`, `CHeightField`, map-texture, mesh-table, or resource-object layouts beyond observed address-qualified offsets.
- Exact source-body identity or clean-room rebuild equivalence.
- Runtime texture, mesh, map, water, sky, shadow, camera, or viewport behavior.
- BEA patch behavior, gameplay outcomes, and rebuild parity.
