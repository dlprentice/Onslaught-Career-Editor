# Mesh, resource, and render static contract

Status: active static map
Last updated: 2026-09-30 (named-mesh interface correction; older slices retained as history)
Summary: named-mesh rendering reads the mesh number through a secondary interface pointer; retained engine/resource slices are historical leads, not current completeness claims.
Evidence: MEASURED — September 30 RTTI, vtable and instruction readback plus a whole-section byte match for the named-mesh getter; older slices were not reverified in this pass.
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

This contract consolidates the retained engine/frame, render-state, resource,
mesh geometry, and collision bridges used by asset tooling and rebuild planning.
Current corrected metadata is owned by the
[Ghidra guide](../ghidra/README.md) and `developer_state.json`'s selected live authority.
Static evidence does not by itself establish runtime rendering or layout parity.

## Named-mesh render interface — September 30

The shared getter at `0x004183f0` reads `[ecx+0xd8]` and returns. ECX is the **secondary render
interface at complete-object offset +8**, so the read selects complete-object `+0xe0`. It is not a
read of the actor's `+0xd8` field. RTTI complete-object locators for named-mesh vtables `0x005dd578`
and `0x005d9094` both record offset 8; their zero-based slot 11 (`+0x2c`) contains this getter.
`CNamedMesh::Init` loads the initialization mesh number at `+0x64` and stores it at complete-object
`+0xe0` (`0x004bbcd8`–`0x004bbcdc`).

The caller path independently supports the adjustment: `0x004f35d7` forms the object-plus-eight
pointer passed to the render factory; `0x004dc4fa` retrieves the render object's stored interface
pointer and `0x004dc503` invokes its slot `+0x2c`. The private reconstruction's `GetRenderMesh`
override now reproduces the complete 16-byte compiled section (seven body bytes plus alignment).
The lead recompiled the affected objects and the full integrated build without losing earlier matches.
Private receipts: `bea-decomp/.worktrees/codex-equiv-20260930/build/namedmesh-secondary-this-evidence-20260930.json`
and `menu-namedmesh-readback-root-20260930.txt`; integrated checks are in
`bea-decomp/build/root-score-menu-namedmesh-20260930.log`.

Preserve the adjusted receiver when translating render dispatch or object layouts. This closes the
getter/receiver identity question; it does not demonstrate a current Godot defect, visible mesh selection,
animation correctness or scene parity. A useful runtime falsifier would observe the complete-object
pointer, interface pointer and selected mesh number together at a real render initialization boundary.

## Baseline Static System Slices

The following dated slices and backup paths are inherited records, not reverified recovery or semantic
completeness claims. Their historical function spellings may have been corrected by later audits.

| Slice | Contract role |
| --- | --- |
| Wave904 `texture-render-static-review-wave904` | Static-coherent texture/resource/decode/render baseline: texture lookup/lifetime, DirectX texture load/decode/upload, CFastVB dispatch/math/render, CVBufTexture/CVBuffer/CIBuffer render paths, render-state cache, render queue, mesh-renderer entry, and asset extraction counts. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260526-101300_post_wave904_texture_render_static_review_verified`. |
| Wave905 `mesh-motion-world-particle-static-review-wave905` | Static-coherent mesh/motion/world/particle baseline: thing/render initialization, CMesh/CMeshPart geometry and pose-cache rows, world occupancy and physics-manager lists, mesh collision, particle manager/set/descriptor rows, and mesh asset bridge counts. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260526-103409_post_wave905_mesh_motion_world_particle_static_review_verified`. |
| Waves1093-1100 | Historical focused rechecks covering engine bootstrap, frame render spine, state/matrix support, render queue, primitive collision, CMesh registry and CMeshPart load/geometry rows. Their reported closure coverage did not establish complete semantic understanding. |

## Engine And Frame Render Contract

Wave1093 re-read the CEngine constructor/lifecycle/resource/viewpoint/deserialize surface. Wave1094 then connected the game render loop to the CDXEngine frame render spine.

| Address | Static contract |
| --- | --- |
| `0x00449820 CEngine__ctor` | Installs engine vtable, seeds clip constants, clears owned resource pointers, and initializes viewpoint-adjacent state. |
| `0x004499d0 CEngine__Init` | Registers render/mesh cvars and allocates major render resources: gamut, map textures, water, landscape, HUD/light resources, screen effects, shadows, and trees. |
| `0x00449d50 CEngine__InitResources` | Loads zoom textures, blob shadows, highlight/hit/cloak textures, and landscape cloud-shadow texture resources. |
| `0x00449dc0 CEngine__LoadAllNamedMeshes` | Reads named mesh entries, reports `Loading named meshes`, reuses existing names by case-insensitive compare, and calls `CMesh__FindOrCreate` for new entries. |
| `0x00449ef0 CEngine__GetViewMatrixFromCamera` | Calls camera orientation vfunc, builds/transposes view basis terms, and copies the output view matrix block. |
| `0x0044a020 CEngine__SetViewpoint` | Stores per-view viewport/player/camera wrapper state and allocates a `CInterpolatedCamera`. |
| `0x0044a6e0 CEngine__Deserialize` | Reads `ENGN`/map-texture chunk data and dispatches map texture deserialize/init context. |
| `0x0046e460 CGame__Render` | Coordinates split-screen/fullscreen viewport setup, `CEngine__SetViewpoint`, `CDXEngine__PreRender`, repeated `CDXEngine__Render`, and `CDXEngine__PostRender`. |
| `0x0053e220 CDXEngine__PreRender` | Prepares per-frame engine/viewpoint state before per-view render loops. |
| `0x0053e2e0 CDXEngine__Render` | Drives per-view world rendering and reaches render queue, particle texture, water, Kempy cube, overlay, and fullscreen effect paths. |
| `0x0053ecc0 CDXEngine__PostRender` | Reaches HUD/viewpoint overlays including `0x00487d10 CHud__RenderBattleline`. |


## Claim boundaries

This map does not prove runtime texture pixels or GPU upload, mesh loading,
skinning, collision, culling, particles, water, exact object layouts, source-body
identity, native WinUI 3D rendering, in-game visual fidelity, patch behavior,
gameplay outcomes, or rebuild parity. Current extraction coverage is owned by
[the game-assets index](../game-assets/_index.md), not repeated here.
