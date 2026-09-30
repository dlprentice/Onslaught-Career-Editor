# Mesh, resource, and render static contract

Status: active static map
Last updated: 2026-09-30 (mesh-part loader match and distinct render-method setters)
Summary: named-mesh rendering uses a secondary interface pointer; collision calculations preserve float materialization and retail quirks; the mesh-part consumer distinguishes bone weights from fixed-width bone slots; an integer render-method store leaves acceptance unchanged. Retained engine/resource slices are historical leads.
Evidence: MEASURED — September 30 RTTI, vtable and instruction readback, whole-section byte matches for the named-mesh getter, mesh-part loader and render-method setters, and bounded original-code collision calculations; older slices were not reverified in this pass.
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

This contract consolidates the retained engine/frame, render-state, resource,
mesh geometry, and collision bridges used by asset tooling and rebuild planning.
Current corrected metadata is owned by the
[Ghidra guide](../ghidra/README.md) and `developer_state.json`'s selected live authority.
Static evidence does not by itself establish runtime rendering or layout parity.

## Serialized bone payload dimensions — September 30

The retail mesh-part reader at `0x004b27a0` supplies a consumer check for the extractor's
`BONW` and `BONS` formulas. The part is first read as a serialized object; its position count is
at `+0xac`, bone count at `+0xc0`, weight-array pointer at `+0xd4`, and slot-array pointer at
`+0xd8`. The following reads occur only with a positive bone count and the corresponding
non-null array pointer:

| Payload | Retail loop | Bytes requested |
| --- | --- | --- |
| Bone weights (`BONW` in the extractor) | `0x004b2ebd`–`0x004b2ee0`: one read per position, element size 4, count from `+0xc0` | `positions * bones * 4` |
| Bone slots (`BONS` in the extractor) | `0x004b2eff`–`0x004b2f1d`: one read per position, literal element size 4 and literal count 3 | `positions * 12` |

Both call `CChunkReader::Read` at `0x00423960`; its instructions at `0x00423961`–`0x00423965`
multiply the element size and count. The slot loop has **no bone-count multiplier**. Thus the
pinned extractor's `numPVert * 4 * numBones * 3` skip at `AyaModelImporter.cs:321` disagrees
with this consumer when the bone count is greater than one and positions are present. Its
weight formula agrees within these static limits. The private reconstruction already used the
retail dimensions before this recheck. A subsequent source-lifetime correction also makes the
entire loader match: its five independent chunk-read indices now have separate lexical scopes,
reproducing retail's reuse of dead argument homes. All 2528 compiled section bytes and every
relocation match, covering 2514 retail function bytes. The lead recompiled the helper's change and
reproduced it in the complete integrated build with all earlier matched identities retained.
Private receipts: `bea-decomp/.worktrees/codex-unitai-nearmiss-20260930/build/meshpart-load-stack-20260930/`
and `bea-decomp/build/source-interfaces-score-20260930.log`.

These are consumer/data-flow findings from the pristine specimen above, independently read
from its instructions on September 30. The reader advances chunks without comparing the
`BONW`/`BONS` FourCCs here; the marker names come from the extractor and their matching
position in the optional payload sequence. Neither tag was present in the earlier measured
CMSH census, which was not rerun. No new shipped asset, successful runtime load, bind/weight
interpretation, or safe malformed-input behavior is established. A hash-pinned resource with
these payloads remains the cheapest end-to-end falsifier; the comparison does not authorize
guessing data or silently enabling a new rebuild parser path. See the corrected
[extractor crosswalk](../source-code/aya-resource-extractor-source-audit.md).

## Render-method setters have different acceptance effects — September 30

The integer store at `0x00528b50` copies its stack argument to receiver `+0x0c` and returns
with four bytes of callee cleanup. It does not touch `+0x10`. The float setter at `0x00527d00`
instead converts its argument through x87, stores the resulting integer at `+0x0c`, and sets
the acceptance flag at `+0x10` to one (`0x00527d0f`). These are distinct operations even when
both receive zero.

Landscape's call at `0x0054565c` uses the integer store on `0x008aa920`; water's call at
`0x0055bacc` uses that same body on `0x009cc030`. The private reconstruction had incorrectly
selected the float setter for Landscape. It now uses an explicit integer setter, while the
console/CLI float setter remains unchanged. Both complete setter sections match retail.
`SetMethod` is a reconstruction name: folding shares the integer body with other setters and
does not establish its original source spelling or object-file home.

The texture-call recheck also consolidates fourteen declaration-only `GetAnimatedFrame` aliases
onto the existing `GetTexture` implementation at `0x00558690`. The checked callers pass the
returned pointer unchanged to texture binding; no second animation operation is established.
The whole integrated build preserves prior matched identities. Fresh instruction readback and
the before/after object comparison are in the private owner
`bea-decomp/.worktrees/codex-equiv-20260930/build/interface-bindings-20260930/`.
These findings correct source bindings and state writes, not a demonstrated Godot or GPU defect.
The cheapest runtime falsifier would observe `+0x10` across the Landscape fallback call and the
subsequent validation path; no new retail rendering run was performed.

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
behavior. That intermediate candidate was 624 compiled bytes; the following approach correction
supersedes it and retains all 27 contact-slice results. All 18 previously matched Geometry functions
remain exact.

These higher-precision counterexamples are not established failures of ordinary gameplay. The earlier
[copied-retail observation](functions/CComplexThing.cpp.md#copied-retail-plane-observation-september-8)
records PC24/RN at 25 Plane/AirGuide calls on its WineD3D route; that retained observation was read,
not rerun here, and does not cover this collision site or other backends.

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

## Segment facing and approach — September 30

The same routine has two distinct dot products. At `0x00478cff`–`0x00478d2d`, the facing
test uses displacement differences retained in x87 while also storing float32 copies. At
`0x00478d3a`–`0x00478d54`, the threshold/division dot reloads those copies; the absolute-value
threshold comparison is at `0x00478d58`–`0x00478d5a`. Reusing one cached float dot or simply
splitting its tests does not preserve these two evaluation boundaries.

The corrected reconstruction evaluates facing separately, constructs the stored displacement, then
recomputes approach. The lead reproduced 57 finite ordinary-entry prefixes at declared PC24/53/64,
nearest rounding: all corrected outcomes, normal bits and admitted distance bits agree. The previous
candidate differs twice; a naive split-expression version differs eight times. With normal
`(0.6f,0.8f,0)` and Y displacement bits `0xbbcccccc`, the previous float store rounds the magnitude
up to the `0.005f` threshold at PC53/64 and admits a case retail rejects. With normal +Z,
start Z=1 and end Z=`-2^-24`, retaining the unrounded displacement for the second dot yields
distance `0x3f7fffff` instead of retail's `0x3f800000`, affecting comparison with a previous hit.

These runs stop at rejection or the first contact instruction. They do not validate the prism,
report publication or the whole function. Two controls refuse an undeclared read and input write;
declared input/report bytes and FPU control state are preserved. All other Geometry callable sections
and relocations are unchanged. The corrected body remains unmatched: 672 section bytes versus
1,014 retail body bytes. The earlier contact slices still agree in all 27 cases.

Private probe: `bea-decomp/.worktrees/codex-collision-nearmiss-20260930/build/geometry-approach-probe-v2-20260930.py`,
SHA-256 `c3d393e008a240aaaa533fe54c1b4859654887cd2230c35f0f3c836ac298bf84`.
Lead receipts: `bea-decomp/local-data/geometry-approach-root-20260930.json` and
`bea-decomp/local-data/geometry-contact-retained-root-20260930.json`.
The useful runtime falsifier remains observation of the actual caller's FPU state and admission path;
the earlier Plane/AirGuide PC24 observations do not settle this call site.

## Sphere and cylinder boundary checks — September 30

The lead independently reproduced complete invocations of sphere line admission (`0x004e4b90`)
and cylinder collision/line response (`0x0043fe20`, `0x00440510`) with actual byte-verified retail
helpers and no stubs. These are bounded emulator experiments over authored records, not a running
retail game or proof of function equivalence.

Sphere line admission has an open reconstruction defect. For radius 1, zero relative position and
segment `(1,1,0)` to `(-0.5,1,0)`, retail materializes the scaled displacement before addition
through its constructor call at `0x004e4cf7`. Its closest point is `(0,1,0)` and admission is true.
The candidate's earlier inlining retains closest-point X=`-2^-25` at PC53/64 and returns false.
Across 51 finite cases at PC24/53/64, twelve admissions differ; PC24 controls agree. Both entries
reject radial endpoint-only contact when the projection lies outside the segment. Named-temporary
and cast-only experiments did not reliably restore the boundary, so no forced source fix is retained.
Nine controls detect invalid execution/dependencies and a strict-versus-inclusive tangency mutant.
Degenerate outside/tangent division, nonfinite inputs, hardware exceptions and live FPU mode remain open.
The next source falsifier is recovery of the two retail constructor-call boundaries while retaining
the already-exact vector helpers and all earlier Sphere matches.

Cylinder's 55 sampled cases agree in defined outputs across two stack-fill patterns at declared
PC64/RN. They preserve behavior that should not be replaced with idealized collision geometry:

- Equality is admitted at the coarse radial/height tests (`0x0043fe71`–`0x0043fe96`).
- Response-enabled admission can reject a separating overlap that the coarse test accepts
  (`0x0043ffbf`–`0x0043ffd5`).
- The deep-overlap branch at `0x004403ec` moves both positions and sets stopped flags without
  writing the report normal. With unit cylinders, initial other X=1.5 and movement X=-0.25,
  the sampled other/own positions become 1.625/-0.125.
- Vertical branch selection at `0x0043ff1e`–`0x0043ff5c` uses signed initial Z; substituting
  absolute Z changes the branch.
- The line quadratic (`0x00440801`–`0x00440884`) uses the full 3D direction length. For unit
  radius/half-height and line `(-2,1,0)` to `(2,1,0)`, detailed response yields contact
  `(-0.76393199,1,0)`, rather than the ideal tangent point.

The cylinder probe executes seven exact helpers and detects nine negative controls. Six identified
integer-copy sites read uninitialized vector padding; these bytes are recorded and excluded from
defined-output comparisons. All other uninitialized stack reads refuse. Zero-length inputs may produce
nonfinite intermediates; no hardware-exception claim follows. Both large cylinder bodies remain
unmatched, with no demonstrated source defect in these samples. A useful next falsifier combines a
real caller's FPU word, detail flag, distinct volume/movement records and resulting contact state.

Private frozen probes are `bea-decomp/.worktrees/codex-career-nearmiss-20260930/build/sphere-line-review-20260930/probe.py`
(SHA-256 `f68e248f2d072172bfa0d5e15cc9046bf00f91ba80b644167181d8cb67fd3067`) and
`bea-decomp/.worktrees/codex-unitai-nearmiss-20260930/build/cylinder-boundaries-20260930/probe.py`
(SHA-256 `60339772c35dcb6ea86e28aef2014df2515476beac0d9c60e386ef6b48514936`).
Independent lead results are `bea-decomp/local-data/sphere-line-root-20260930/comparison.json`
and `bea-decomp/local-data/cylinder-boundaries-root-20260930/comparison.json`.

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
