# Mesh, resource, and render static contract

Status: active static map
Last updated: 2026-09-30 (named-mesh interface and segment-contact rounding corrections)
Summary: named-mesh rendering uses a secondary interface pointer, and segment contact coordinates round after addition; retained engine/resource slices are historical leads, not current completeness claims.
Evidence: MEASURED — September 30 RTTI, vtable and instruction readback, the named-mesh getter's whole-section byte match, and bounded original-code contact calculations; older slices were not reverified in this pass.
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

## Segment contact precision — September 30

The segment/triangle routine at `0x00478c20` computes its contact coordinates at
`0x00478df9`–`0x00478e31`. For each coordinate, x87 multiplies the displacement by the stored
distance, adds the start coordinate, and only then stores float32. A reconstructed vector temporary
rounded the Y/Z products to float32 before adding the start; explicit component expressions now retain
the observed order and storage boundary. This is a demonstrated reconstruction error, not merely
different register allocation.

The lead independently reproduced a frozen original/old/corrected instruction-slice comparison:
27 finite cases across declared x87 precisions PC24, PC53 and PC64, with round-to-nearest-even.
The corrected results agree in all cases; the old code differs in six. With start `(1,-1,-1)`,
displacement `(-3,3,3)` and float32 distance `1/3`, retail and corrected Y/Z are `2^-25` at
PC53/64, while the old calculation produces zero. PC24 and zero/unit/half-distance controls agree;
adjacent float distances and mixed scales are also included.

Three ordinary-entry retail runs with triangle `(0,-10,-10)`, `(0,20,-10)`, `(0,-10,20)`,
segment `(1,-1,-1)` to `(-2,2,2)` and a null report reach the compared contact state. They stop
before prism admission. The slice comparison begins with an empty x87 stack and nonaliased finite
inputs. It neither determines the game's actual FPU control state nor validates denominator rounding,
normal construction, prism acceptance, report writes, special floating values or whole-function
behavior. The corrected candidate remains unmatched: 624 compiled bytes versus 1,014 retail body
bytes. All 18 previously matched Geometry functions remain exact.

Private evidence owner:
`bea-decomp/.worktrees/codex-collision-nearmiss-20260930/build/geometry-segment-contact-probe-20260930.py`
(SHA-256 `6739a2747f431a85c561f306adb9d353da7d91d57034cbd6a6fa4ebc5af8b771`), with
frozen old/corrected objects pinned in that script. The independent rerun is
`bea-decomp/local-data/geometry-contact-root-20260930.json`; focused compile results are
`bea-decomp/.worktrees/codex-equiv-20260930/build/geometry-contact-integrated-focused-20260930.log`.

Consumers should preserve the addition-before-store boundary instead of introducing a scaled-vector
temporary. A useful next falsifier is a controlled caller observation recording the FPU control word,
contact bits and subsequent prism decision together. This correction does not establish a Godot
collision defect, gameplay outcome or runtime parity.

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
