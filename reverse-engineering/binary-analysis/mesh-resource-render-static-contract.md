# Mesh, resource, and render static contract

Status: active static map
Last updated: 2026-10-01 (complete texture activation match and trail name gate; bounded corrections retained)
Summary: specimen-bound rendering and collision contracts, with bounded corrections to arithmetic association, float stores and ordered admission.
Evidence: MEASURED — specimen instructions, whole-section/relocation matches and bounded native calculations and buffer comparisons; older slices were not reverified in this pass.
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

This contract consolidates the retained engine/frame, render-state, resource,
mesh geometry, and collision bridges used by asset tooling and rebuild planning.
Current corrected metadata is owned by the
[Ghidra guide](../ghidra/README.md) and `developer_state.json`'s selected live authority.
Static evidence does not by itself establish runtime rendering or layout parity.

## Trail renderer name gate — October 1

At `0x004c8ca7`, trail rendering (`0x004c8520`) calls the case-insensitive CRT
comparison at `0x00568390` for `Blue Trail Large`. This follows a separate,
case-sensitive fifth-index character check for uppercase `T`. The reconstructed
case-sensitive full-string comparison rejected names that retail accepts.

The lead freshly compiled the correction and reproduced its 32-byte gate with
all three references checked. A bounded native test executes only the admitted
gate and the CRT's locale-zero ASCII path, replacing RenderAll with a count stub.
Across 16,407 authored cases (all ASCII letter-case combinations plus rejection
controls), 8,191 old differences become zero, with no new differences.
`blue Trail large` passes; lowercase `t` at the quick-filter position still fails.
All 35 other callable sections and their references remain unchanged.

The complete trail renderer remains unmatched. Non-ASCII text, nonzero locale
and the real render flush remain untested; those are the next behavior falsifiers.
Private root evidence under the owner below: `trail-name-root-native/receipt.json`
and `font-render-reconnect-console-root-readback.json`.

## Trail basis normalization — October 1

The basis calculations inside `0x004c36b0` divide stored components by a live
x87 square-root magnitude at `0x004c398b`–`0x004c39a9` and
`0x004c3a74`–`0x004c3a92`. Assigning a newly constructed vector in the private
draft rounded the magnitude before division and retained a different component
intermediate. Existing in-place division restores the observed value boundaries.

The lead rebuilt the source and reproduced both frozen arithmetic corpora.
For 3,594 prepared float32 step vectors under PC24/53/64 nearest rounding,
1,636 prior XYZ/exception differences become zero. Extending to 14,412 cases
over all four rounding modes leaves twelve inherited signed-zero differences,
versus 7,490 before the change, with no new disagreements. Replacing the first
division with multiplication changes 12,046 expanded-corpus results.

The signed-zero counterexample remains explicit: at CW `037f`, step bits
`[80000000,3f800000,00000000]` produce side.Y `00000000` in retail and
`80000000` in both drafts. The complete function remains unmatched. These
isolated calculations do not establish step reachability, complete trail updates,
allocation, live control words or visible output; those remain useful falsifiers.

Private lead receipts under
`bea-decomp/.worktrees/codex-equiv-20260930/local-data/geometry-gate-resume-20261001/`:
`trail-native-root-expanded/receipt.json`,
`trail-native-root-replay/signed-zero-readback.json`, and
`trail-frontend-device-root-readback.json`. The lead compared regenerated fixtures
and admitted fragments with the frozen inputs and bound fresh compiled code to
the accepted object. Other callable sections retain their bytes and references.

## Texture constants and signed mipmap width — October 1

Projected texture activation (`0x005588f0`) reads scale constants with float bits
`3e9c18fa` at `0x005e59d0` and `bee38e39` at `0x005e59cc`, four uses each.
The former source's short decimal approximations differed. More precise literals
restore all eight references without changing the instruction section.

Mipmap construction loads source width at `0x0055964d`, saves it at
`0x00559667`, and halves it with arithmetic shifts at `0x0055994a` and
`0x00559b1c`. A signed source-width local reproduces those two instructions;
the unsigned draft emitted logical shifts. Only two compiled instruction bytes
change, with every relocation preserved. This proves the operation's signedness,
not that negative dimensions occur in admitted resources.

Mipmap construction remains unmatched. Texture activation now matches its complete
1,536-byte compiled section and all 89 relocations after restoring matrix lifetimes,
return paths and the near-plane getter's float value boundary. The product and
subtraction both read far/near at `0x0089cdd4`/`0x0089cdd0`, against the independently
consistent ENGINE base `0x0089c9a0`. This closes the previous structural draft's two
reversed references; all 44 other callable sections and their targets are preserved.
No resource decoding or graphics device ran. Private lead proofs under the owner
above: `startup-render-texture-root-readback.json` (earlier correction) and
`texture-activation-root-readback.json` (complete match). Resource/device behavior
remains the runtime falsifier.

## Projected-texture coordinate count — October 1

Texture activation `0x005588f0`, mode 3, pushes `0x104` at `0x00558e7c` before
calling `0x00513820` with stage zero and state `0x18` (`D3DTSS_TEXTURETRANSFORMFLAGS`).
The pinned DirectX 9 SDK header defines this as `D3DTTFF_COUNT4 | D3DTTFF_PROJECTED`.
The private reconstruction used COUNT3, emitting `0x103`; it now uses COUNT4.

For fixed-function texture processing, projected coordinates are divided by the last
selected component. Four versus three therefore selects a different projective divisor;
this API consequence is distinct from an observed image defect. See Microsoft's
[texture-coordinate processing contract](https://learn.microsoft.com/en-us/windows/win32/direct3d9/texture-coordinate-processing).
Active shader configuration and rendered results were not inspected here.

The lead freshly compiled both sources and isolated one changed instruction byte.
All 37 exact object controls, 88 target relocation records and 160 other object sections
remain unchanged. That intermediate activation draft was unmatched; the complete
match above supersedes that status. No D3D device,
graphics driver, game or Godot executed. A useful presentation falsifier is a mode-3
texture with different third/fourth transformed coordinates, observing the actual stage
state and projection under the retail shader configuration.

Private readback:
`bea-decomp/.worktrees/codex-equiv-20260930/local-data/texture-projection-root-20261001/state-readback.json`,
SHA-256 `367c39ffda7f2e79753c4985235422493bc423e29456d3dbf01a993c43db5aba`.
The receipt binds the pristine instructions and pinned `d3d9types.h` identity;
`readback.json` records the before/after object comparison.

## Trail-point count and arithmetic order — September 30

The body at `0x004c35d0`, reconstructed as `CPDTrail::AllocatePoints`, now matches its
complete 224-byte compiled section, including the call relocation to `0x004caed0` at
section offset `0x96`. Its retail function extent is 209 bytes. The saved Ghidra label
`CEngine__ConfigureParticleBurstForDistance` does not establish its owner or original
source name; this source correction has not changed the database.

For the segment-length path, retail subtracts the frame's previous position
(`+0x90/+0x94/+0x98`) from its current position (`+0/+4/+8`), combines the squared
components as `(dz*dz + dy*dy) + dx*dx`, takes the square root and divides by descriptor
`+0xa4`. The reconstruction had combined them as `(dz*dz + dx*dx) + dy*dy`.
The integer conversion at `0x004c363a` is x87 `FISTP` into a 64-bit temporary;
the following instructions use its low 32 bits and add three. Its rounding mode is
inherited from the x87 control word, not established by a C# cast or a floor operation.
The later allocation multiplies this count by 40. The experiment below executes the
arithmetic only, not that allocation or the point-initialization loop.

The lead reproduced a frozen native ELF32 probe of the unchanged, relocation-free
retail slice `[0x004c3602,0x004c363e)`, the old candidate and the corrected candidate.
It uses 140 finite float32 input cases at PC24, PC53 and PC64 with nearest-even and
toward-zero rounding: 840 executions per image. The old candidate differs in 36
calculated integers, twelve at each precision under nearest-even. No difference occurs
in the tested toward-zero cases. The corrected slice is byte-identical to retail and
agrees on every case.

One PC24/nearest-even witness uses current-position float bits
`[3f800000,39800001,39800001]`, previous position zero and segment length `2.0`.
Retail converts to zero while the old candidate converts to one; the unchanged following
addition therefore predicts three versus four points. This is a concrete consequence of
the arithmetic order under that selected mode, not a newly observed in-game trail.
The probe checks return, integer registers, stack canaries, preserved control word and
an empty x87 stack. Five simple finite controls per mode, a divide-to-multiply mutation
and truncated-input refusal also pass.

Private reproducer:
`bea-decomp/.worktrees/codex-career-nearmiss-20260930/build/trail-count-native-20260930/probe.py`
(SHA-256 `a58ee0b5fb6aed5405aea7d371c5957ae660fd5b17d8582b009f4ddcbc6f6ccb`).
Lead output: `bea-decomp/.worktrees/codex-equiv-20260930/build/trail-count-native-lead-20260930/result.json`
(SHA-256 `221566301ee483bc306dd5e8eecaab514eb6c6e946710657eb8a046b508cb7df`).
The full-section readback is in the adjacent `squad-trail-independent-readback-20260930.json`.
The actual game's control word, allocation outcome and visible trail remain unmeasured.
The cheapest runtime falsifier is to record the control word and these input fields at
this call on an experimental game copy, then compare its stored point count.

## Emitter and effect part pointers — September 30

The serialized emitter record's `+0x40` word is a presence marker, not its part index.
When nonzero, the reader consumes a separate index word and replaces the marker with
`mParts[index]` (`0x004ab275`–`0x004ab29d`). The older readers also store a selected part
pointer (`0x004a85ba`–`0x004a85c3`, `0x004a90ec`–`0x004a90f9`). At runtime both
emitter-part getters (`0x004aa5a0`, `0x004aa820`) return this pointer. Its consumers
dereference part fields, including the controller at `0x0044478c` and unit at `0x004f8927`.

CRTMesh's array at `+0x3c` retains these part pointers. Its distinct `+0x38` array holds
emitter ordinals, while `+0x40` holds numeric effect IDs. `FindEffect` (`0x004dd510`,
zero-based render slot 19) compares the supplied pointer with the `+0x3c` entries and returns
the first equal entry's index, or -1. It does not dereference the argument or exclude null
equality. The mesh-renderer and destructible-segment callers pass part pointers at
`0x004b6402`/`0x004b6405` and `0x00442ba4`/`0x00442ba5` respectively.

The private reconstruction now carries `CMeshPart*` across these getters and the virtual
interface, preserving all field offsets, allocation widths and slot positions. The pose call
at `0x004dd1cf` also binds to the existing `0x004b4de0` implementation with seven four-byte
arguments rather than a declaration-only alias. Its complete body remains unmatched;
`EvaluatePose` and `FindEmitterPart` are reconstruction names, not proven original spellings.

The lead inspected the pristine instructions above, reproduced all 378 previous exact
results in the affected twelve-object set and ran the full integrated score with no lost
matched addresses or relocation conflicts. Private receipts:
`bea-decomp/.worktrees/codex-equiv-20260930/build/emitter-pointer-20260930/`, its adjacent
before/after logs, and `bea-decomp/build/emitter-pointer-score-20260930.log`.
No new game run or Godot behavior was tested. A useful runtime falsifier would observe the
loaded part pointer, the effect array and the selected index together on an admitted mesh.

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

## Polygon side-normal magnitude — October 1

Within `CMeshPart::OptimizePolygons` at `0x004b31f0`, the neighbouring-face
normal's magnitude calculation at `0x004b3727`–`0x004b3745` adds Y² and Z²
before X², takes the square root, and stores float32. The former reconstruction
added X² and Y² first. This is a rounding distinction, even though the real-number
expressions are algebraically equivalent.

A source-local cross-product/normalization helper expresses the retail grouping
while retaining the existing extended intermediates and float store. The fresh
compiled target changes only six x87 operand bytes; its other section bytes and
all 33 relocation tuples remain unchanged. All 60 other callable sections retain
their bytes and relocation meaning. Simpler helper forms that removed the store
were rejected. The helper's original type/name is unknown, and shared vector math,
the outer normal and the edge-length calculation are unchanged.

The lead rebuilt the source, bound its fragment to the frozen candidate and
reproduced the existing 43,062 authored float32 XYZ cases under six explicit x87
precision/rounding settings. The old magnitude differs in 1,340 cases: 906 at
PC24/nearest and 434 at PC24/toward-zero. Corrected captured output agrees with
retail throughout, including the magnitude, retained XYZ, control/status/tag state
and stack canaries. Thirty-six exact controls pass; replacing square root with
absolute value changes 42,830 results as a negative control.

This executes only the 30-byte arithmetic slice with authored incoming x87
components. Cross-product reachability, normalized outputs, polygon-collapse
decisions, thresholds and the live game's control word remain unmeasured. The
complete function still does not match; its stack layout and edge-length square
association remain open. A useful next falsifier starts from admitted mesh
positions, observes the preceding cross product and follows normalization into
the curvature/collapse comparison with the caller precision recorded.

Private source/object readback:
`bea-decomp/.worktrees/codex-equiv-20260930/local-data/geometry-gate-resume-20261001/mesh-side-root-readback.json`.
The unchanged corpus, frozen before/after objects and lead replay are under
`bea-decomp/.worktrees/codex-resume-mesh-20261001/local-data/mesh-side-correction-20261001/`:
`correction-frozen/` and `root-corrected-replay-20261001/receipt.json`.

## Triangle travel-limit admission — October 1

The second projection path in `0x00478510` squares its distance and stores it as float32 at
`0x00478b21`, before calling the original `MagnitudeSq` at `0x00478b37`. That 32-byte helper at
`0x00477ba0` returns its x87 result without a caller-side float store. At `0x00478b3c`–`0x00478b45`,
retail continues only when the returned squared magnitude is ordered greater-or-equal to the stored
limit. Unordered comparisons take the rejection path.

The previous reconstruction squared the distance after the helper call, retaining excess precision,
and admitted unordered comparisons. A reconstructed inline predicate taking the squared limit by
reference, with `squaredLimit <= move.MagnitudeSq()`, restores the observed storage and branch
semantics under the pinned compiler. No independent helper entry or original source spelling is claimed.

The lead executed original, prior and corrected post-projection instruction fragments with the actual
byte-matched magnitude helper. Across 54 explicit PC24/53/64 cases, the prior candidate differs in
17 decisions: five finite boundaries and twelve NaN cases. The correction agrees on all decisions,
stored squared-limit bits and x87 status words. Projected-vector copies, stack canaries, control words
and empty x87 state also agree. The admitted set includes zero, adjacent values, decimal equality,
subnormal and large finite inputs, infinities and intentionally masked quiet/signaling NaNs. Inverting
the original branch changes every decision, providing a consequential negative control.

These cases start after projection with authored distance and movement; they do not prove ordinary
triangle-entry reachability or complete collision behavior. The full function remains unmatched, and
its stack layout, other inline boundaries and scheduling remain open. All other callable Geometry
sections and relocations are unchanged. The next falsifier is a complete original/candidate invocation
that reaches this gate from admitted triangle, sphere and motion inputs, with caller precision recorded.

Private source/object pins, fresh compilation and replay are in
`bea-decomp/.worktrees/codex-equiv-20260930/local-data/geometry-gate-resume-20261001/`:
`native-range-helper-replay.py NEW_OUTPUT`, `range-helper-positive/` and `corrected-gate-native/`.
The frozen previous candidate is retained under the earlier geometry-mask evidence owner. The original
specimen and earlier frozen experiment were read, not modified.

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

The September 30 sphere-line candidate had a reconstruction defect, corrected by the current exact body. For radius 1, zero relative position and
segment `(1,1,0)` to `(-0.5,1,0)`, retail materializes the scaled displacement before addition
through its constructor call at `0x004e4cf7`. Its closest point is `(0,1,0)` and admission is true.
The candidate's earlier inlining retains closest-point X=`-2^-25` at PC53/64 and returns false.
Across 51 finite cases at PC24/53/64, twelve admissions differ; PC24 controls agree. Both entries
reject radial endpoint-only contact when the projection lies outside the segment. Named-temporary
and cast-only experiments did not reliably restore the boundary, so no forced source fix is retained.
Nine controls detect invalid execution/dependencies and a strict-versus-inclusive tangency mutant.
Degenerate outside/tangent division, nonfinite inputs, hardware exceptions and live FPU mode remain open.
The October 1 fresh compile now matches all 480 section bytes, including all four relocations, for
`0x004e4b90` (479-byte retail body). The old draft and its rejected fixes remain historical evidence;
the constructor boundaries and earlier Sphere matches are preserved. Exact body matching does not
establish the caller's live precision or the runtime questions above.

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
nonfinite intermediates; no hardware-exception claim follows. This dated probe found no source defect
in its samples. The October 1 fresh check establishes that the line body `0x00440510` now matches all
1,456 section bytes and 21 relocations (1,442-byte retail body). The response remains unmatched;
the broader native experiment below exposes and corrects a radial-rounding defect.

Private frozen probes are `bea-decomp/.worktrees/codex-career-nearmiss-20260930/build/sphere-line-review-20260930/probe.py`
(SHA-256 `f68e248f2d072172bfa0d5e15cc9046bf00f91ba80b644167181d8cb67fd3067`) and
`bea-decomp/.worktrees/codex-unitai-nearmiss-20260930/build/cylinder-boundaries-20260930/probe.py`
(SHA-256 `60339772c35dcb6ea86e28aef2014df2515476beac0d9c60e386ef6b48514936`).
Independent lead results are `bea-decomp/local-data/sphere-line-root-20260930/comparison.json`
and `bea-decomp/local-data/cylinder-boundaries-root-20260930/comparison.json`.

## Sphere response arithmetic — October 1

The complete original `0x004e4e00` entry and freshly compiled reconstruction were executed natively
with five byte-verified retail vector helpers, explicit PC24/53/64 control words, and finite nonaliased
volume/movement records. The old candidate differed in final XYZ movement or position in 148 of 4,512
cases (77 deep-response and 71 shallow-threshold cases, all PC24). Return and stopped flags agreed;
the largest observed XYZ difference was approximately 0.02186.

Retail combines XY squared distance before adding Z squared at `0x004e4f2d` and `0x004e52ca`.
The old reconstruction's `MagnitudeSq()` emitted `(Y² + Z²) + X²`; using XY magnitude plus Z squared
restores the retail association, including the compiler-reused deep-contact distance. Fresh native
execution of the compiled correction removes all 148 observed differences with identical inputs and
retail outputs. PC53/64 continue to agree in these samples. After that first correction, the unmatched
1,552-byte section (1,537-byte retail body) retained 43 differing nonrelocation byte positions.
The expanded comparison below exposes a further relative-speed defect in that candidate.

The probe verifies nonvolatile registers, stack position/canaries, x87 stack/control-word preservation,
and unchanged volume/report inputs. Defined XYZ outputs, stopped flags and return are compared;
copied uninitialized vector padding is excluded. Three coarse-tangency controls change results, and
removing an admitted vector constructor fails. All 17 prior exact address/symbol pairs (15 unique
functions) and the 19 other callable bodies in the object remain unchanged.

These are bounded original-code comparisons, not equivalence, observed gameplay or evidence of the
caller's live control word. Nonfinite inputs, exceptional arithmetic and other rounding modes remain
outside these samples. The [startup precision contract](../contracts/render-platform/CD3DApplication__Initialize3DEnvironment__0052af00.md#precision-setup--october-1-instruction-recheck)
explains why PC24 deserves testing without claiming it has been measured at this caller.

Lead private owners in `bea-decomp/.worktrees/codex-equiv-20260930/local-data/` are
`sphere-root-20261001/` (baseline) and `sphere-correction-root-20261001/` (fresh compiled correction).
The latter's `native/receipt.json` SHA-256 is
`23a9ffe5a4509e9a1e02382aeda646596d19b05298c2885c7d0719527a610fb4`;
input SHA-256 is `45b993e1d8266cc3d73b6faffd1aabc9641da9c91a9bcda24fddc738803e0fd5`.
Whole-build readback preserves all earlier exact matches. The useful next falsifier is an unresolved
arithmetic block exercised at its actual caller's measured precision and contact state.

### Expanded relative-speed comparison

At `0x004e4fa3`, retail combines relative speed as `(X² + Z²) + Y²`; the earlier reconstruction
emits `(Z² + Y²) + X²`. Asymmetric small Y/Z velocity components expose the difference. The lead
reproduced 23,160 complete original/candidate calls with the same five retail vector helpers:
132 defined-output differences in the baseline, all PC24, and none in the corrected candidate.
Changing only the speed instruction block in a private diagnostic also removes all 132 differences;
that diagnostic is evidence of cause, not a patch to the preserved specimen.

The source uses the explicit speed association and the existing vector `Normalise` method. The shallow
normalization's 81-byte block agrees with retail after resolving constants; the deep zero/reciprocal tail
agrees over 68 bytes. The deep X/Y load order still differs. Its normalization substitution is not an
independently demonstrated deep-path fix: it preserves the tested behavior and compiler emission of an
already exact scale helper. The candidate remains unmatched, with a 1,536-byte section and different
frame/scheduling decisions. A larger raw byte-difference count does not erase the demonstrated speed fix.

The expanded fixtures cover the earlier controls, disparate-scale velocities, translated moving pairs,
and shallow/deep contacts under explicit PC24/53/64 nearest rounding. Return, defined XYZ positions and
velocities, stopped flags, untouched volumes/report, preserved registers, stack/canaries, x87 stack/control
word and exception flags are compared. Copied vector padding is excluded. A coarse-admission mutation
changes 21 results; removing an admitted constructor exits with the expected refusal. The lead verified
the original entry, its 15 alignment NOPs, all five helpers and the constant region against the specimen.
This remains finite, nonaliased authored-input evidence with one stack-fill pattern; live precision,
world reachability and general equivalence are not established.

Frozen inputs and replayer: `bea-decomp/.worktrees/codex-resume-collision-20261001/local-data/`
`collision-resume-20261001/replay-sphere.py --suite random --out NEW_OUTPUT`. Lead execution is in
`bea-decomp/.worktrees/codex-equiv-20260930/local-data/sphere-random-root-20261001/`;
the adjacent `geometry-gate-resume-20261001/sphere-original-readback.json` records the specimen readback.
The exact vector helpers are `0x00401ec0`, `0x0040d150`, `0x0041ad10`, `0x004404f0` and `0x00490900`.

## Cylinder response arithmetic — October 1

The original `0x0043fe20` entry and fresh compiled candidate were run natively on 77 finite authored
fixtures, each at explicit PC24/53/64 round-nearest settings and two stack fills: 462 cases. Seven
byte-verified retail helpers are admitted. These expand the earlier sampled cylinder states with
off-axis tangency, shallow/deep cutoff, translated origins and radial/vertical decision ties.

Retail stores Y squared before adding X squared at `0x0043ff2e..0x0043ff42` and reuses the stored
squares in deep normalization. The reconstructed `MagnitudeXY()` expression did not preserve those
rounding points. Using direct `sqrtf(X*X + Y*Y)` removes 76 of the 84 observed defined-output
differences. Inputs, original outputs and controls are identical between runs; the remaining eight
differences are unchanged. They concern translated-origin initial Z at PC53/64: retail stores Z at
`0x0043ff1a` before subtracting height, while the candidate retains excess precision. This remains
an explicit reconstruction defect, not an accepted approximation.

A broader depth-reordering draft initially agreed in 444 cases but failed additional moving-tie
fixtures: with X=`0.6f` minus two float ULPs, Y=`0.8f`, Z=`1.125f` and Z movement=`0.125f`, retail
returns true while that draft returns false at PC53/64. It was rejected. The retained correction
introduces no discrepancy in the expanded 462-case set and still leaves the full function unmatched:
1,664 section bytes versus the retail 1,731-byte body, with 29 relocations.

Checks cover return values, defined XYZ position/movement, stopped flags, report normals, preserved
inputs, nonvolatile registers, stack/canaries and x87 stack/control word. Copied vector padding is
excluded. Altered coarse admission changes 20 cases; changing the half-overlap constant changes 182;
removing an admitted dependency exits with the expected refusal. These are bounded original-code
comparisons, not gameplay observations, general equivalence or measurements of the live FPU state.
All 20 other retained callable sections and relocation destinations are unchanged; the line body
remains exact. The no-longer-emitted local Normalise copy is covered by its exact whole-build owner.

Lead private evidence is
`bea-decomp/.worktrees/codex-equiv-20260930/local-data/cylinder-correction-root-20261001/`:
`root-readback.json`, frozen sources/objects, inputs and outputs. The corrected native receipt
`accepted-native/receipt.json` has SHA-256
`b07ef298c8bc904b1ed557fbeb01c4ddd8b05a27388ef14c01fd41f47b00d554`.
The next numerical falsifier is the retained translated-origin Z witness; live caller precision,
nonfinite inputs, aliases and world contact reachability remain separate questions.

A subsequent explicit Z/Y-rounding draft is **rejected**, despite matching all
2,622 structured cases. The lead reproduced a separate frozen 24,000-case finite
set: the draft reduces disagreements from 692 to 288 but introduces 116 newly
failing cases. Retail's first position rewind rounds the X/Y products and retains
Z; the draft retains X instead. That concrete boundary is the next source question,
not permission to accept fewer total mismatches. Production source is unchanged.
Private readback: `bea-decomp/.worktrees/codex-equiv-20260930/local-data/cylinder-storage-root-20261001/independent-replay/readback.json`;
frozen input SHA-256 `985c49eaa0876659e0849eb5a3acbf60191c860cb2503b2865cee4b17b79010a`.

## Imposter quad coordinates and precision — October 1

The quad builder at `0x00542f90` receives texture coordinates from the frame record
at offsets `+00,+08,+04,+0c`; the caller's pushes at `0x00543845`–`0x0054386e`
establish the argument order `u0,v0,u1,v1`. The retail vertex stores establish:

| Corner position | Texture coordinates |
| --- | --- |
| `(position-right)-up` | `(u0,v0)` |
| `(position+right)-up` | `(u1,v0)` |
| `(position+right)+up` | `(u1,v1)` |
| `(position-right)+up` | `(u0,v1)` |

The former reconstruction reversed V on all four corners. The same corner order
and triangles (`i,i+1,i+2`, then `i+2,i+3,i`) rule out a compensating winding change.
Both buffer routes share these stores. A second defect rounded the first
`position-right` vector to float32 before subtracting up. Retail retains these
three intermediates on x87 at `0x00543069`–`0x00543090`; the other corners have
different constructor/materialization boundaries and must not all be flattened.

The lead reproduced 828 complete native i386 calls per version with four actual,
independently byte-matched helpers: vector construction, position assignment and
both buffer-pointer getters. Finite authored positions at PC24/53/64, two fills,
both buffer routes and three starting offsets produce 774 differences in the old
source, 288 after the UV correction alone, and zero after the precision correction.
The buffer offsets include an exact index-capacity boundary. A changed-sign control
differs in 474 cases. Missing-constructor, unlocked-buffer and vertex/index-resize
controls refuse execution rather than count partial runs as agreement.

A natural three-component aggregate with parenthesized values subsequently restores
the remaining instruction scheduling. The lead freshly reproduced all 880 compiled
section bytes and 20 relocations against the 866-byte retail body and its padding;
the final candidate also agrees in all 828 cases. All 25 prior exact controls and
29 other callable bodies/relocation targets remain intact. This identifies compiled
behavior, not the unique original source text.

The harness uses prelocked, adequately sized memory buffers. Real device locking,
resizing, error handling, arbitrary aliases/nonfinite inputs and actual rendering
remain outside its boundary. It checks buffer and input memory, ABI registers,
stack guards and x87 control/depth, not every memory access or all floating-status
semantics. A useful visual follow-up captures a known non-symmetric imposter frame
and its emitted vertices together; no such live observation is claimed here.

Private lead evidence:
`bea-decomp/.worktrees/codex-equiv-20260930/local-data/imposter-correction-root-20261001/`,
with `exact-readback.json`, `native-exact/receipt.json`, the pre-correction witnesses
and capacity refusal controls. No Ghidra state changed during this correction.

## Imposter orientation and centre offset — October 1

The per-imposter renderer `0x00543300` updates orientation after each of its first
four faces. At `0x00543878` it forms the current-orientation argument; after two
pushes, `0x00543888` forms the turn-matrix receiver. The actual matrix product
`0x0040d320` computes receiver times argument. Thus the operation is `turn * ori`,
whereas the former reconstruction used `ori * turn`. Matrix multiplication is not
commutative; this is a source error, not merely register allocation.

The lead freshly compiled the combined correction and reproduced 48 native cases
using the original turn-construction block, its exact trigonometric constants,
the original update and the complete byte-matched matrix helper. Eight finite
orientations at PC24/53/64 nearest and two stack fills distinguish the old source
in 36 cases; the corrected source agrees in every case. Identity and commuting
orientations remain controls. Inputs, stack guards, expected registers, control
word and empty x87 stack are checked; undefined matrix padding is excluded.

A separate first-row error combined the box-centre terms as `X+(Y+Z)`. Retail uses
`(X+Y)+Z` for each row (`0x0054342a`–`0x005434a7`). The corrected 125-byte block and
its constructor relocation equal retail exactly. With the actual vector constructor,
102 native finite fixtures expose twelve old cancellation differences, four at each
selected precision; the corrected block has none.

The full renderer remains unmatched: 1,424 compiled bytes against a 1,467-byte
retail body, with 25 relocations. All 26 earlier exact object controls and 29 other
callable sections/relocation destinations survive. These are isolated arithmetic
blocks with explicit state, not a full render, GPU or live-world observation.
A useful runtime falsifier captures one noncommuting incoming orientation and the
six resulting quad orientations on an experimental game copy; no such run occurred.

Private lead owner:
`bea-decomp/.worktrees/codex-equiv-20260930/local-data/imposter-render-root-20261001/`.
Rotation receipt SHA-256 `6a43f46e4bda0c1e011e200a36d7dce58815232356dc7a810e9dbbe8072cbc4d`;
offset receipt SHA-256 `9aeb7e86d28698f1f2c688995ce708c16d763b327b2b4cbde4eb71d1c78f7ac1`.
The adjacent `render-font-root-20261001/readback.json` binds the final source and
freshly compiled objects. Ghidra was not changed.

## Retained debug-arrow arithmetic and indices — October 1

The body at `0x0053df40`, reconstructed as `CDXEngine::RenderArrow`, retains the
first vertex sum's X component in x87 until the origin is added
(`0x0053e120`–`0x0053e149`). Its Y/Z components are rounded to float32 first.
The reconstructed forwarding format-setter wrappers consumed enough inline budget
to keep a vector constructor out of line and round X prematurely. Calling the actual
format setters directly removes that extra boundary without adding fake operations.

The lead freshly compiled and reproduced eighteen native finite cases with six
inputs at PC24/53/64 and nearest-even rounding. Six old X differences, three each at
PC53/64, become zero; Y/Z are unchanged. Adding only the premature X store/reload to
retail reproduces every old result. The baseline executes the actual vector
constructor. Explicit fragment-entry adapters, guard bytes, register/stack and x87
checks bound the result. Upstream normalization, providers, GPU drawing and live
control words are excluded. All thirty exact controls and 36 other callable sections
and relocation targets survive. The full 752-byte section remains unmatched against
the 734-byte retail body, with 188 differing positions and nineteen relocations.

A separate fresh static read finds three decoded direct calls, at `0x004e9fc9`,
`0x004ea110` and `0x004ea2f0`, all inside the squad-debug body `0x004e9f00`.
Its constructor installs vtable `0x005df0f4`, whose slot 52 points there.
The selected-squad dispatch at `0x00470681` precedes the developer-mode check;
PostRender reaches that dispatcher at `0x0053ef91`. This is real retained code,
but ordinary stock-player activation has not been established.

The retail six-word index array also leaves element 4 unwritten. Its other elements
are `[i0,i1,i2,i0,unknown,i3]` (`0x0053e1c3`–`0x0053e1f3`). Cached-buffer acquisition
at `0x00501280` does not initialize that caller stack slot. AddIndices copies all
twelve bytes (`0x00500b26`–`0x00500b2d`); Draw binds the buffer and forwards to the
indexed-draw wrapper (`0x00500f25`/`0x00500f38`). With initially empty buffers this
submits four vertices and two triangle-list primitives. Neither acquisition nor
submission establishes that the unwritten index is valid. The reconstruction
preserves this static behavior; no visible defect or device failure is claimed.

Private lead owner:
`bea-decomp/.worktrees/codex-equiv-20260930/local-data/arrow-root-20261001/`.
The native receipt `native-v08/receipt.json` has SHA-256
`a096ffd7f37c2361550ecc5cd7e3d59f745d33f4d26d041e0d25b10d5c158875`;
`readback.json` and `static-callers/` retain compiled and caller/buffer evidence.
A cheap future runtime falsifier watches the selected-squad pointer and these three
calls on an experimental game copy, then records the submitted index values.
No renderer ran and no Ghidra database changed.

## Inverse-trig callee identities — October 1

Fresh library-member and instruction comparison distinguishes intrinsic asin
`0x0055dcb0` from intrinsic acos `0x0055f380`; both consume an x87 argument.
Their conventional stack-argument entries are `0x0055dcc4` and `0x0055f394`.
The pinned VC6 LIBCMT `asin.obj` and `acos.obj` code sections each match their
203-byte retail span outside relocation fields. Their distinct arithmetic,
endpoint branches and linked operation-name strings establish which is which;
swapped-member comparisons fail 47/51 nonrelocation bytes. Library SHA-256:
`a541c95e5ffdd6d5573d1976f5e5d0038f2c4fb0bcb02975c68948bf1d6e452a`.

`CFeature::Move` calls asin at `0x0044cc84`, and Explosion initialization calls
it at `0x0044bb13`. Their reconstructed source wrongly called acos. The old
checker accepted Feature because its other instructions matched and the caller
inference consistently associated the wrong name with the asin address. Both
source calls are corrected; Feature passes the stricter complete-section check,
while Explosion remains unmatched. The shadow triangle routine's three calls
at `0x004ee852`, `0x004ee85f` and `0x004ee86e` really do use acos and are unchanged.

The checker and comparison resolver now enforce the four independently proved
entry identities before caller inference, stale annotations or section aliases.
This corrects a source/tooling defect; it does not prove visible toppling,
explosion orientation, shadow rendering or all other library identities.
Lead readback: `bea-decomp/.worktrees/codex-equiv-20260930/local-data/math-binding-root-20261001/readback.json`;
library comparison receipt SHA-256:
`a173dd413c384bacbed2215af09b8b2f9f43aab6384b0f2bd2c5a4d0bcd03e96`.

## Static-shadow plane admission — October 1

The triangle-ray body at `0x004ee410`, reconstructed as `CStaticShadow::RayHitsTriangle`,
accumulates its plane numerator as the existing D term plus Z, then Y, then X
(`0x004ee533`–`0x004ee549`). The reconstructed expression compiled as D plus Y,
then X, then Z. Successive updates to D restore the retail order without introducing
another float store, call or helper. Only six operand bytes change in the compiled
section; all 22 relocation identities and 33 other callable sections remain unchanged.
All 28 exact controls survive. The full 1,168-byte section remains unmatched, with
38 nonrelocation differences rather than 44; no new exact function is counted.

Fresh lead compilation and native i386 execution compare 650 authored finite
triangle/endpoint fixtures at PC24/53/64, 1,950 cases per image. Execution begins at
the actual function entry and stops at `0x004ee57d`, before intersection and angle
processing. A harness sentinel records arrival at that continuation; it is not the
function's final hit result. The old source differs in 472 parameter/intermediate
observations and 152 plane-admission decisions; the correction differs in none.
Decision differences are 120 at PC24 and sixteen each at PC53/64. Inverting the
denominator-threshold branch changes 1,269 decisions, demonstrating that the probe
observes rejection as well as admission. Input preservation, stack canaries,
nonvolatile registers and x87 control/stack state are checked.

One moderate finite witness starts exactly at a triangle vertex `(1,-0.75,0.3125)`.
Retail obtains a slightly negative segment parameter and rejects it; the old source
rounds to negative zero and admits it. This establishes an arithmetic boundary
consequence, not a visible shadow defect or the fixture's occurrence in retail levels.
The three later acos calls are correctly bound to `0x0055f380`, but no math helper or
angle calculation executes in this prefix experiment.

The subsequent complete native recheck executes all three actual acos calls and
their admitted finite-domain CRT helpers, including the precision-exception path.
It adds 75 inside/outside, edge, vertex, parallel and segment-limit controls to the
earlier cases. Across 2,025 complete entry-to-return cases, the old source differs
on 100 final BOOL results (84 at PC24, eight each at PC53/64); the correction differs
on none. All complete output records agree, including exception flags and guarded
input/ABI/x87 state. Inverting the final angle-test branch changes 913 results;
redirecting an acos call outside the admitted code refuses before any output.
No math function is replaced. The image-initial CRT flag at `0x009d08b4` remains
zero, an explicit fixture value rather than a measurement after live startup.

This closes the proposed complete-body falsifier only for these finite, nonaliased
fixtures and masked precision modes. Degenerate triangles, nonfinite/domain-error
paths, unmasked exceptions, arbitrary numeric equivalence and visible rendering
remain open. The complete section still differs at 38 positions. A useful next
runtime falsifier records an actual shadow ray, resulting BOOL and FPU/CRT state on
an experimental retail copy, then reproduces those inputs without modifying assets.

Private lead owner:
`bea-decomp/.worktrees/codex-equiv-20260930/local-data/staticshadow-root-20261001/`.
`readback.json` records the fresh compiled comparison; `native-plane/receipt.json`
has SHA-256 `9920a99d67783f330ad20c96fb7f2ee278a21e598f31b1a86969730516abd317`.
The complete-run receipt `full-native-v01/receipt.json` has SHA-256
`22e0e9e5164f1cbabc34d9d1e5434f9d255a2bbf6cc1300a79b8ba9fca22f69b`.
No Ghidra database or renderer was opened.

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
