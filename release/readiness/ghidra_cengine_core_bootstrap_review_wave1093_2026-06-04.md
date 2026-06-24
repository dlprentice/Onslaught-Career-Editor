# Ghidra CEngine Core Bootstrap Review Wave1093

Status: complete read-only static review
Date: 2026-06-04
Scope: `cengine-core-bootstrap-review-wave1093`

Wave1093 re-read the saved CEngine constructor, lifecycle, resource bootstrap, viewpoint, mixer, and deserialize surface with fresh metadata, tag, xref, instruction, decompile, context, queue, and backup evidence. The review made no Ghidra rename, no signature change, no comment/tag mutation, no function-boundary change, no executable-byte change, no BEA launch, and no installed-game or runtime-file mutation.

Reviewed primary rows:

| Address | Saved row | Fresh static evidence |
| --- | --- | --- |
| `0x00449820 CEngine__ctor` | `void __fastcall CEngine__ctor(void * engine)` | Installs the engine vtable, seeds near/far clip constants, clears owned resource pointers, sets the render-landscape flag at `+0x4a8`, and initializes viewpoint-adjacent fields. |
| `0x00449890 CEngine__Shutdown` | `void __fastcall CEngine__Shutdown(void * engine)` | Releases screen effects, shadow/tree systems, gamut, landscape/camera/water/map texture/HUD texture resources, and trims VB/IB pool capacities. |
| `0x004499d0 CEngine__Init` | `int __fastcall CEngine__Init(void * engine)` | Registers `cg_renderlandscape`, `cg_drawpolybuckets`, and hit-effect cvars; allocates gamut/map texture/water/landscape/HUD/light resources; initializes screen effects/shadows/trees. |
| `0x00449d50 CEngine__InitResources` | `void __fastcall CEngine__InitResources(void * engine)` | Loads zoom textures, blob shadows, `hilight.tga`, `hiteffect.tga`, `cloak.tga`, and the landscape cloud-shadow texture. |
| `0x00449dc0 CEngine__LoadAllNamedMeshes` | `void __thiscall CEngine__LoadAllNamedMeshes(void * this, void * dataFile)` | Reads mesh names from the buffer, reports `Loading named meshes`, reuses entries by case-insensitive compare, and calls `CMesh__FindOrCreate` for new entries. |
| `0x00449ef0 CEngine__GetViewMatrixFromCamera` | `void __thiscall CEngine__GetViewMatrixFromCamera(void * this, void * camera, void * outViewMatrix)` | Uses two stack arguments, calls the camera orientation vfunc, builds/transposes view basis terms, and copies twelve dwords to the output matrix. |
| `0x0044a020 CEngine__SetViewpoint` | `void __thiscall CEngine__SetViewpoint(void * this, int viewpoint, void * camera, void * viewport, void * player)` | Uses four stack arguments, copies viewport state, stores the player pointer, destroys any prior camera wrapper, and allocates a `CInterpolatedCamera`. |
| `0x0044a0d0 CEngine__SelectViewpoint` | `void __thiscall CEngine__SelectViewpoint(void * this, int viewpoint)` | Writes current viewpoint at `+0x4ac`, copies selected viewport state, and calls `D3DDevice__SetViewport`. |
| `0x0044a110 CEngine__ResetPos` | `void __thiscall CEngine__ResetPos(void * this, int x, int y)` | Loads landscape pointer from `this+0x10` and forwards x/y reset coordinates to the landscape reset-position helper. |
| `0x0044a130 CEngine__InitDamageSystem` | `void __fastcall CEngine__InitDamageSystem(void * engine)` | Resets landscape damage tables, applies tree-shadow landscape damage stamps, updates current damage tracking, and resets the landscape wrapper. |
| `0x0044a1f0 CEngine__LoadMixers` | `void __thiscall CEngine__LoadMixers(void * this, int set)` | Loads the map texture array from `+0x49c`, calls `CMapTex__LoadMixerTextureSet` with set/6/0x100, and builds copied mixer levels. |
| `0x0044a6e0 CEngine__Deserialize` | `void __thiscall CEngine__Deserialize(void * this, void * chunkReader)` | Reads the `ENGN`/map-texture count through `CChunkReader`, deserializes map textures, then dispatches MAP deserialize/init context. |

Context rows include `0x00528f80 CD3DApplication__Init`, `0x005290a0 CD3DApplication__Create`, `0x0052af00 CD3DApplication__Initialize3DEnvironment`, `0x0052bb80 CD3DApplication__Reset3DEnvironment`, `0x0044a2a0 CEngine__SetKempyCube`, `0x0044a2c0 CEngine__SetWater`, `0x0044a2d0 CEngine__SetupLights`, `0x0044a610 CEngine__TrackBurstEventFromPreset`, `0x0044a1c0 CEngine__UpdatePos`, and `0x004902b0 CEngine__TrackBurstEventIfNearby`.

Evidence counts:

- Primary exports: `12` metadata rows, `12` tag rows, `25` xref rows, `785` function-body instruction rows, and `12` decompile rows.
- Context exports: `10` metadata rows, `10` tag rows, `17` xref rows, `1231` function-body instruction rows, and `10` decompile rows.
- Queue closure remains `6410/6410 = 100.00%`, with `0` commentless rows, `0` exact-undefined signatures, and `0` `param_N` signatures.
- Wave911 focused progress remains `812/1408 = 57.67%`.
- Expanded static surface progress remains `1560/1560 = 100.00%`.
- Wave911 top-500 risk-ranked coverage remains `500/500 = 100.00%`.
- Verified backup: `G:\GhidraBackups\BEA_20260604-155838_post_wave1093_cengine_core_bootstrap_review_verified`, 19 files, 175541127 bytes, `DiffCount=0`.

What this proves:

- The saved CEngine core bootstrap/viewpoint/resource function objects still exist in the loaded Ghidra database with coherent names, signatures, comments, tags, xrefs, instruction bodies, decompile output, and backup read-back.
- The prior CEngine source-compatible static treatment remains coherent after fresh Wave1093 re-audit exports.
- The review bridges CEngine bootstrap/resource/viewpoint rows back into the adjacent CD3DApplication shell context from Wave1092.

What remains separate proof:

- Runtime engine boot, device, resource, camera, landscape, lighting, damage, water, and mixer behavior.
- Exact CEngine, CDXEngine, landscape, water, map-texture, camera, D3D, and render-queue layouts beyond observed offsets.
- Exact source-body identity for all retail helper bodies.
- BEA patching behavior, gameplay outcomes, and rebuild parity.

Probe token anchor: Wave1093; cengine-core-bootstrap-review-wave1093; 0x00449820 CEngine__ctor; 0x004499d0 CEngine__Init; 0x00449dc0 CEngine__LoadAllNamedMeshes; 0x00449ef0 CEngine__GetViewMatrixFromCamera; 0x0044a020 CEngine__SetViewpoint; 0x0044a0d0 CEngine__SelectViewpoint; 0x0044a1f0 CEngine__LoadMixers; 0x0044a6e0 CEngine__Deserialize; 0x005290a0 CD3DApplication__Create; 0x0052af00 CD3DApplication__Initialize3DEnvironment; 1560/1560 = 100.00%; 812/1408 = 57.67%; 500/500 = 100.00%; 6410/6410 = 100.00%; G:\GhidraBackups\BEA_20260604-155838_post_wave1093_cengine_core_bootstrap_review_verified; no mutation.
