# Rebuild Provenance

Status: active implementation boundary

`rebuild/` is a GPL-3.0-or-later, source- and reverse-engineering-informed
reconstruction. It is not a clean-room lane. The root MIT license does not
relicense this subtree or the pinned `references/Onslaught` source.

## Permitted evidence and inputs

- Stuart Gillam's pinned GPL source may be read, ported, and adapted with its
  license and attribution preserved.
- The Steam retail executable and Ghidra database establish released static
  identities and deltas from the reference source.
- Controlled copied-runtime observations establish measured behavior.
- Original design work, deterministic tests, public standards, and engine APIs
  may fill gaps that are clearly labelled provisional.
- Retail assets are user-supplied local inputs. The source tree retains exact
  hashes and bounded extraction/conversion recipes, while the materialized
  payloads remain ignored and outside source/release packages.

Do not import the retail executable, retail asset payloads or conversions,
decompiler output, user saves, raw runtime captures, or separately licensed
third-party code/media into this subtree.
Never describe synthetic or source-only behavior as observed Steam behavior.

## Authority

The reference source is implementation evidence, not automatic proof that the
Steam build is byte- or behavior-identical. When sources disagree, use this
order for the released PC game:

1. controlled retail runtime observation;
2. retail binary/static evidence;
3. pinned source implementation and vocabulary;
4. provisional reconstruction design.

Record a source or address only when it makes a current implementation decision
auditable. Generated inventories, human-review gates, and proof-plan chains are
not provenance.

## Current slice

The normal Godot entry path now belongs to a presentation-only frontend state
machine outside Core. It begins at click-to-start, then exposes the released
main-menu entries, a world-100-only level selector, the released loading image,
and one lifecycle seam that constructs, replaces, or disposes the existing
Level 100 session/world. The
startup FMV is absent: Steam's `-skipfmv` flag at
`CLIParams__ParseCommandLine` (`0x00423BC0`) skips that movie but still reaches
the click page. That page's Steam handlers at `0x0051B660`/`0x0051B6B0` accept
action `0x2C` and full-window mouse input; its render entry at `0x0051B840`
requests localized string index `0x77` (`Click to start`). Main-menu evidence is
the vtable at `0x005DBAE4`, input/action/render entries
`0x00462250`/`0x004623E0`/`0x00462D40`, and Stuart's `FrontEnd.cpp` and
`PCFrontend.cpp`. Level select uses Steam input/render entries
`0x004606B0`/`0x00460B40`; only released world 100 is exposed. The loading page
uses the exact image and `Loading...` text established by
`CConsole__RenderLoadingScreen` (`0x0042C810`). Twenty-one exact AYA textures,
three exact XAP PCM decodes, and twenty-three English strings decoded from the
supported shipped table are materialized to ignored frontend paths. This lane
emits move/select/back cue identities; it does not load or play those WAVs, so
the integrating audio owner remains singular.

Result ownership is deliberately split at the evidence boundary. Stuart's
`CGame::DeclareLevelWon`, `CGame::DeclareLevelLost`, and end-level render path
establish an in-game terminal overlay; Steam's later CFEPDebriefing vtable at
`0x005DB9C0` resolves to initializer `0x00456780`, input `0x004568A0`, process
`0x00456930`, and render `0x00456DD0`. This frontend implements neither visual
surface, and the HUD does not invent a replacement. The frontend consumes the
mission-owned
`Level100MissionSnapshot` only when its exact `Level100MissionTerminalState` is
ready, then retains only a terminal lifecycle handoff plus explicit retry and
Main Menu transitions. Shipped Level 100 script provides
`LevelLostString(LOSE_TUTORIAL_BROKE)`; Stuart's game system also identifies
generic player-death and water failures. Their three exact English strings are
materialized. The deterministic mission owns `Level100MissionOutcome` and
`Level100MissionFailureReason`; the frontend copies neither into a second
vocabulary. Exact `Mission Complete`, `Retry`, `Back`, and failure text remains
available to the separate result owner, but no terminal overlay, selected
default, summary compositor, rank/kill data, progression, save, or later
campaign selection is claimed here.

The deterministic Core and command-tape/hash format are reconstruction-owned
infrastructure. The Godot Level 100 Opening Slice consumes the released
Federation walker, jet, and cockpit as exact 63-, 54-, and 21-part AYA
hierarchies, plus bounded static conversions of 24 Level 100 static-world mesh
types, four `pinesnow` variants, Target Tank, and Warehouse meshes. Static Steam
evidence separates three tree owners. `CRTTree` submits each exact pine mesh at
or inside the selected profile's horizontal mesh-quality distance and queues
its six-view imposter outside that boundary. The supported high-quality
`defaultoptions.bea` snapshot stores `70.0` at OptionsTail `+0x0C` (file
`0x26CA`), and manifest v7 owns that value. After the world and global-imposter
passes, `CDXTrees` submits one standing fast card selected by
`(tree_object_address >> 4) & 3` and a fifth-view horizontal card only when the
camera differs from sampled ground height by more than 20 units. A manifest
ordinal is not the retail selection input. The client preserves the close,
six-face far, always-on standing, and height-gated horizontal owners separately.
It does not infer Steam identity from its own heap. Manifest v7 instead pins an
explicit phase-0 ordinal cycle for deterministic reconstruction and validates
all 1,481 selected views with counts `371/370/370/370`. Steam's exact tree
allocation/view sequence and address-selector phase remain the precise
unresolved runtime boundary. Exact
source/output hashes live in the materializer and ignored generated manifest;
detailed card, atlas, and render-state evidence lives in the Level 100 asset note and
`reverse-engineering/binary-analysis/functions/DXTrees.cpp.md`.
The released Level 100 WRES
records now set the player start heading, all 33 visible base-world objects,
1,481 Steam-instantiated pines, trigger locations, and four Firing Range targets. The client
maps BEA `(X, Y, Z-down)` consistently to Godot `(X, -Z, -Y)` for terrain,
retained meshes, facilities, sky, light, camera, and Core-relative positions.
The supplied base-turret comparison resolves specifically to WRES type `8`
(`CUnitInitThing`), object `Turret 03`, definition `SAT Turret`, physics Unit
index `58`, mesh `ft_sam`, and released runtime class `CCannon`; it is not a
Target Tank. The authored transform is `(252.5, 261.25, -0.0)` with zero
yaw/pitch/roll. Stuart's `CThing::Init` clips the authored pivot through
`MAP.Collide` and then the water level, while Steam `CThing__Init` at
`0x004F34A0` dispatches the `CCannon` clip slot (`+0xB0`, true), samples HFLD
at `0x0047EB80`, then dispatches its underwater slot (`+0xC4`, false). HFLD
unit `-10485` gives terrain Z `-9.599889755249023`, above water in the released
Z-down relationship, so the initial retail transform is
`(252.5, 261.25, -9.599889755249023)` with identity orientation. The 16-part
mesh hierarchy is `base -> turretbase -> support -> barrel -> Emit01..08`, with
`Emit09..12` directly below `base`; its lower bound is
`-0.22822660952806473` relative to the pivot. The client now consumes the
manifest's existing definition and omits only the `SAT Turret` lower-bound lift,
preserving its authored below-pivot skirt without a per-instance offset. The
remaining static types keep their prior converted clearances and are not
claimed to share this released grounding relationship.
The loose mission scripts establish their order and 0.5-second event delays.
The retained `HFLD` uses the released loader's 64×64 tiled sample layout,
height scale, and complete 513×513 sample lattice. Core embeds the hash-verified
chunk and implements Steam's `0x0047EB80` 24.8 fixed-point signed interpolation
for hashed player-ground elevation. The released `MAPT`/`MMAP`, lighting-gradient,
30-owner `SSHD`, and base `DMKR` paths produce the initial 512×512 root landscape
texture. The materializer processes all 1,481 pine placements through the
released stamp rules and verifies the exact
RGB565 payload as SHA-256
`6EB202F450926097930BEDCA440F0163A1886572981E3C69B4EDF9289A68AE2B`.
The archive serializes seven `MAPT` sources; the single-player landscape calls
`CDXLandscape__CreateMipLevels` (`0x005447E0`) with five and selects mixer widths
`16/32/64/128/256`. Those sources, all variable-length `MMAP` records, the
lighting mask, sparse structure-shadow cells, and pine shadow descriptors are
retained in the 1,382,734-byte hierarchy payload with SHA-256
`541EACD0AA75FAE8BEFB8A3E1505EA52AE6B1F6C1367C15C65D7DD23B7CFE977`.
Level 100
selects exact 512×512 DXT1 `detail00`; the released terrain render path at
`0x00545590` supplies its two world-coordinate scales, offset, exact 256×256
DXT1 moving cloud-shadow stage, scroll rates, and observed modulation modes.
The macro compositor follows the released row-major tile, texel, weight, and
shade-mask addressing. `CHeightField__InitColorGradient` (`0x0047E8E0`) builds
the 64-entry coefficients; the load tail at `0x0047F932` doubles, clamps, and
masks them before `CLandscapeTexture__BlitTileRegionWithLightingMask` produces
RGB565 texels. Steam's 20-byte terrain vertices contain position plus repeated
landscape coordinates, but no normal or diffuse-color channel, so that prelit
macro owns base terrain illumination. An uninterrupted copied-runtime sample
measured the cloud offset advancing by `(0.01993, 0.00996)` cycles per wall-clock
second. Stage 0 wraps and plainly modulates the root texture, stage 1 plainly
modulates detail, and the cloud and rotated-detail stages use `MODULATE2X`.
Steam uses anisotropic root minification, but its five logical landscape levels
are separate one-level 512×512 cyclic caches rather than one hardware mip chain.
Their absolute-coordinate spans are `512/256/128/64/32`; cache ownership follows
the selected landscape tile rather than normalized mesh UVs.
The client preserves each retained mesh group's complete
six-slot `TEXR` assignment and directly decodes every AYA-wrapped texture
selected by its active passes. The PC
lighting setup at `CEngine::SetupLights` supplies packed ambient plus opposing
sun and anti-sun directions; its directional colors divide by 256, and the
base texture stage uses `MODULATE2X`. Five exact DXT1 cube-25
textures use the released face order and geometry. Steam runtime state confirms
Level 100's terrain capability flag and `MODULATE2X` state are both enabled, as
well as packed fog color `#D8D8FC`, density `0.0084`, and `D3DFOG_EXP` mode;
the shared Godot material applies that exponential path from camera-space depth
to terrain, static geometry, cockpit, targets, and water. Godot's
`OUTPUT_IS_SRGB` contract selects the final transfer so the GL Compatibility
renderer is not converted twice. Steam
`CMeshRenderer__RenderMeshWithLayerPasses` (`0x0054D530`) evaluates the slots in
order; `CDXMeshVB__Load` (`0x0054E160`) treats only `0xFFFFFFFF` as absent.
Controlled Level 100 runtime state enabled modes `0`, `1`, `2`, and `4` while
disabling modes `3` and `5`. `CVBufTexture__RenderModePass` establishes mode 1
as model-space `DOTPRODUCT3`, mode 2 as camera-space reflection coordinates with
the released half-scale/offset matrix, and mode 4 as the regular-UV alpha overlay
using the serialized `TEXB` offset and scale. For the Level 100 Tank Factory,
all four material groups own `Chrome3` in slot 2 at serialized strength
`0.19999998807907104`. Mode 2 is a separate draw which retains the active lit
stage-0 `MODULATE2X`; stage 1 multiplies its otherwise-opaque source alpha by
the byte-quantized `0x33FFFFFF` texture factor before
`SRCALPHA`/`INVSRCALPHA` framebuffer blending. It inherits the world's wrapping,
linear-mip, anisotropic stage-0 sampler and `-1` LOD bias. The client preserves
that encoded-channel, saturating equation rather than blending raw Chrome3 RGB.
Its special base path tests `CTexture +0xB4`, disables alpha test/blending, and uses
`BLENDTEXTUREALPHA`; parsing all 273 Level 100 `DXTX/CTEX` records identifies only
`meshtex\\A8_FB_hangermorebits_lit.tga` for that path. The client therefore blends
that texture over the lit current color while retaining normal alpha cutouts for
the other currently materialized base textures. The
runtime light vector `(-0.03407396, -0.9086333, 0.4162026)` matches normalized
negative Level 100 sun position. These active passes are shared by the current
static objects, targets, Aquila, jet, and cockpit; the visible-sun particle is
still absent. Water follows the released active fixed-function path: the exact
HFLD level and color, camera-following 25×25 grid, two caustic stages, authored
`reflection00` imagery sampled at the released absolute-world `1/256` transform,
the stage-3 disable before the main grid, shoreline-only wave passes, and two
exact `SURF` shoreline bands. Static
Steam evidence at `CWaterRenderSystem__RenderMainPass` (`0x0055B6C0`) establishes
the first-shoreline, grid, alpha-tested sun, and late additive-shoreline order.
The sun uses texture-factor color `#E8E8FF`, alpha reference `0xC0`, and a quad
whose center, half-width, and half-length are respectively `6`, `2`, and `8`
times camera height. The late shore pass uses `SRCALPHA`/`ONE`, no depth write,
and no fog. One uninterrupted copied-Steam sample measured the main phase at
`1` radian per second and both wave scrolls at `0.06` texture cycles per second;
the client advances those presentation phases from frame delta outside Core.
The animated half-scale reflection transform belongs to the optional advanced
path, which remained inactive in controlled Steam observation. Static analysis
of `CDXLandscape__UpdateLOD` (`0x00546B40`) and
`CLandscapeIB__CreateIndexBuffer` (`0x0048DF20`) establishes the complete
eight-step base, the 4/2/1-step grids and 16 edge-stitch index variants,
midpoint-error LOD score, camera-smoothed texture rings, and absolute cache
coordinates. It does not establish the exact stateful gamut-row
clipping or the exhaustion/reuse order of Steam's bounded `800/300/90` patch
pools; the client emits eight-step coverage for unselected tiles plus the
selected patches and leaves triangle clipping to Godot's renderer. Dynamic scene
reflection/refraction and pixel identity outside this bounded active pass are not
claimed.
Steep-slope sliding, structure collision
beyond the two observed facilities, targets, weapons, resources, jet/morph
handling, reverse-transform presentation, and unimplemented HUD behavior remain provisional unless
specific retained evidence says otherwise.

The exact walker AYA supplies 63 reciprocal parent/reference parts, 54 expanded
base-material surfaces, and the 100 usable frames in `LegMotion`. Steam
`CMCMech` does not replay those frames as one gait cycle: it precomputes each
leg's root-to-`Footbase` extension and chooses the closest frame independently
for the current planted-foot distance. The retained chains are legs
`18/21/22/23/24`, `28/30/31/32/33`, `46/51/52/53/54`, and
`3/8/9/10/11`, with Footbase parts `25`, `34`, `55`, and `12`.

One fresh no-input control and two uninterrupted copied-retail repetitions used
the same three-second idle, twelve-second forward hold, and fifteen-second rest
over the authored Level 100 slope. Both active runs repeated the exact start
`(288.6875, 243.25, -12.111499)` and end
`(270.926941, 275.010376, -12.886998)`, then settled all four phase/lift fields
to zero. Steam `CMCMech` establishes the consumed controller contract: body-local
foot offsets `(-0.957,1.078)`, `(0.937,1.089)`, `(-0.882,-1.527)`, and
`(0.937,-1.505)`; diagonal scheduling with at most two early swings; phase rate
`400` per second through `180`; `0.4` lift; and moving/stationary thresholds
`1.0`/`0.05`. Every planted foot repeated the exact HFLD height while the final
contacts spanned about `0.96` vertical units. Core consumes that fixed-step
controller subset and Godot directs each exact five-part chain toward its Core
contact. Retail keeps the Battle Engine body level at its 1.9-unit clearance;
exact toe-normal alignment, CMC sway, non-heightfield surfaces, and steep-slope
response remain outside this proof.

One clean Level 100 control and two fresh repeated copies establish the walker
translation and body-turn loop: equal forward/strafe acceleration, a 3.0-unit/s
cap, `0.7` per-retail-update coast, yaw-velocity accumulation, and `0.8`
retention. Core maps those 20 Hz responses into its fixed 30 Hz step. The same
control/repeat discipline maps raw states `2 → 1 → 3` to the explicit
16-tick walker-to-jet transition. Jet forward speed and energy drain retain
earlier bounded measurements.

A later clean control and two fresh copies with only the proven Level 100
early-flight byte change isolated the corresponding presentation. Transform was
bound through copied `defaultoptions.bea`; launches used only `-skipfmv -level
100`. The clean control delivered the same action but remained in walker state
`2` with no render, animation, cockpit, or camera change. Both modified runs
swapped the active render reader as state `1` began, committed state `3` after
540.045 and 549.598 ms, and retained one first-person camera pointer/vtable.
Steam `CBattleEngine::Morph` (`0x0040A580`) and the render-reader swap
(`0x00406460`) establish that the 54-part jet hierarchy owns the external
transition. `CBattleEngine::FinishedPlayingCurrentAnimation` (`0x0040EEB0`)
then changes its `walktofly` animation, virtual frames 25–50 at 20 Hz, to
looping `fly` frame 0 after 1.243 and 1.241 seconds. The 21-part cockpit begins
its independent `walktofly` path one step into its 26–50 table, displays frames
27–49, and selects `fly` frame 0 after 1.138 and 1.141 seconds. The same entry
starts exact XAP records 25 (`N_BE_engine_takeoff`) and 23
(`N_BE_engine_inflight`). Runtime copies, sampler output, and debugger helpers
were disposable; only the consumed hashes and timings are retained.

One no-input control and two uninterrupted fixed-yaw forward holds per facility
then establish the only retained structure contacts. The Control Tower repeated
a `2.5736`-unit centre separation while removing inward velocity and retaining
tangent motion; the Tank Factory settled at `8.4333` units and removed the
head-on velocity. Both held raw walker state `2`, the expected `0.15`-unit
released update speed before contact, and stable body yaw. Stuart's
`ECR_SLIDE` response and the released single-player `0.4` BattleEngine radius
support the interpretation. Core consumes rounded `2.574` and `8.434` contact
envelopes only; these are not general mesh bounds, arbitrary actor collision,
or facility-destruction behavior.

A fresh no-input Level 100 control and two repeated pointer, forward, coast, and
strafe runs also traversed a `6.232587`-radian
`CBattleEngineWalkerPart::UpdateWalkCycle` scalar. Static `CMCMech` analysis now
establishes that this separate scalar does not index every leg through
`LegMotion`; the retired renderer incorrectly conflated the two. The sampled
ground normal remained `(0, 0, -0.99999976)` on that earlier flat route.

A pair of fresh, uninterrupted, no-input app-owned Level 100 runs repeated the
same released opening-camera lifecycle. At event time `3.0`, Steam installed a
`CPanCamera` (`0x004198D0`, vtable `0x005D92A8`) with length `6.0`, not Stuart's
in-house `3.0` default. Both runs began at
`(283.807220, 251.978271, -16.411499)` and ended at
`(290.115509, 240.701736, -12.195276)` around the stationary Battle Engine at
`(288.6875, 243.25, -12.111499)`. Steam's `CPlayer__GotoPanView` at `0x004D2C10`
uses the released orientation with local points `(0,10,-4.3)`, `(5,0,1.3)`,
`(0,-9,-1.3)`, and `(0,-2.5,0)` through its order-three clamped quadratic
`CBSpline`. The camera changed to the first-person `CThingCamera` at event time
`8.95`; game state remained panning until `9.0`. `CPlayer__ReceiveButtonAction`
at `0x004D3110` rejects normal player actions below playing state. That establishes
the 180-tick camera-state boundary, but does not itself enable Level 100 input;
the later mission power gate is documented below. `CPanCamera::GetShowHUD` is
false; the control camera owns the HUD-visible handoff. Raw sampler output and
copied games were disposable and are not retained.

A clean copied Level 100 run starts player zero with current/preferred view `1`.
After that opening fly-in, five uninterrupted samples held the same active camera
pointer and first-person `CThingCamera` vtable `0x005DBB88`. The Battle Engine
position remained `(288.6875, 243.25, -12.111499)`, yaw remained `0.509829998`,
and the horizontal forward column remained `(-0.488029, 0.872827)`. The camera
position is the Battle Engine position, and the Steam 16:9/zoom-1 projection term
`0.5625` gives a 58.7155-degree vertical field of view. The cockpit pointer at
Battle Engine offset `0x528` selected animation index `1`; the exact `cockpit2.msh`
`CAMD` table identifies that as `walk`, authored hierarchy frame 25. Runtime
also reported the cockpit render flag enabled and no local position offset.
The retained 21-part cockpit loads its exact hierarchy as ten material-group
surfaces at that frame. Godot's camera child uses a bounded 6 cm depth and 1 cm
vertical presentation adjustment selected against the clean retail frame and
near-plane path; that adapter offset is not claimed as a retail model value.

A no-input control and two uninterrupted repetitions then bound attached-view
aim at the same authored start. `Look Up`, `Look Down`, and `Look Left` were
bound only through each copied `defaultoptions.bea`; launch used
`-skipfmv -level 100`. Raw state remained walker `2`, view remained `1`, and
position remained `(288.6875, 243.25, -12.111499)` during the aim phases. The
first vertical input changed pitch by `0.008547009` radians (`1/117`) and left
stored velocity `0.0068376074`; subsequent coast retained exactly `0.8`. Both
runs stabilized at pitch `+0.5321228`; their opposite endpoints were
`-1.0911411` and `-1.0912496`. This establishes absolute bounds on the Level
100 start slope, not the released terrain-normal rule elsewhere.

For a bounded shot witness, a disposable one-byte copied-archive setup changed
only the initial `Pulse Cannon Pod` call descriptor from `DisableWeapon` to
`EnableWeapon`. Two fresh runs produced player-owned `CRound` objects whose
unit directions were `(-0.226261, 0.404663, -0.886032)` and
`(-0.226194, 0.404543, -0.886105)` in Steam X/Y/Z axes. Their contemporaneous
BattleEngine yaw/pitch values predict
`(-sin(yaw)cos(pitch), cos(yaw)cos(pitch), sin(pitch))` with maximum component
error `0.00119`. Core consumes the 30 Hz time-equivalent pitch input `0.003938`,
retention `0.861774`, the bounded start-slope endpoints, and that three-axis
shot direction. Terrain-relative limits, mouse inversion, auto-aim, and vertical
target collision remain unimplemented. The setup patch,
copies, and raw samples were disposable.

The copied Steam options bind Movement Forward/Backward/Left/Right to both
`WASD` and the matching arrow keys, while Look Left/Right/Up/Down consume the
mouse axes. Steam `CController::DoMappings` at `0x0042DB40` maps each centered
cursor displacement as `clamp(sensitivity * pixels * 0.004333333, -1, 1)`;
`Input::UpdateCursorCenterWithWindowScale` at `0x0042DA00` retains `10/17` of
that displacement per 20 Hz update. Stuart's player and BattleEngine paths
corroborate that the resulting analogue axes add walker yaw at
`GroundTurnRate/75`, pitch at `1/117`, and then retain angular velocity by
`0.8`. One no-input control and two fresh uninterrupted copies configured only
through `defaultoptions.bea` repeated the same sensitivity-`1.5` pointer and
movement sequence without focus loss; both active runs produced the same
sampled yaw delta `-0.019985914`, pitch delta `-0.021745417`, and checkpoint
states. The Godot adapter consumes that bounded proportional mapping at its
30 Hz fixed step. Other sensitivity values, inversion, and jet mouse response
remain unproven.

Separately, a disposable expected-byte-only change to the player constructor's
preferred-view immediate
from `1` to `2` selected the released third-person vtable at `0x005D9230`; the
copy was restored and no retail patch is retained. The third-person constructor
at `0x00418EF0`, position path at `0x004191C0`, and orientation path at
`0x00419540` establish the previously inspected pitch-zero third-person
geometry: camera five units behind and 3.25 units above the 1.9-unit center of
gravity, looking six units ahead. Retained mesh bounds, the released
Level 100 ground/start relationship, and copied-runtime framing independently
agree on scale `1.0`; the client grounds the walker from its composed standing
pose. Static placement retains measured lower-bound metadata, but only the
`SAT Turret` currently has the type-specific released pivot-grounding correction
described above.

Fifty-four retained HUD textures and `Dial.raw` are exact released files named
by the Steam binary or the pinned Stuart weapon resource path. A clean
copied-runtime frame,
the complete Level 100 mission script, and the released render paths establish
the first-person composition now used by Godot: the central threat compass and
target layers, classified lower-left scanner/weapon stack, lower-right Level
100 influence map or message portrait, objective/world markers, and the
conditional segmented message panel.
`CHud__RenderObjectiveProgressGaugeAndHeadingNeedle` at
`0x004858D0`, `CHud__RenderBattleline` at `0x00487D10`,
`CMessageBox__RenderOverlay` at `0x004B8850`, and the `CDXCompass` render path
provide the retained edge offsets, 45/46-unit scanner north/contact radii, and
111.5/96/110/98-unit threat, damage, gauge-needle, and objective radii plus
rotations, packed tints, and state ownership.
`CDXCompass__BuildByteSpriteOverlayTexture` identifies `Dial.raw` frame zero as
the heading-rotated north treatment. `CDXCompass__BuildRingGeometry` supplies
the 50/40 segment counts and 31/27-percent thickness inputs. Level 100's version-1
BSWD supplies 13 translated radius-10 nodes and 22 exact links.
`CDXBattleLine__BuildMesh` establishes that the released interior is a
continuously triangulated terrain-extent mesh with inserted influence points
and relaxed edges, not a drawing of the BSWD links. Its dynamic influence
magnitudes and render mesh are not available from the current mission producer,
so Godot retains the typed state consumer but draws no inferred interior.

`CMessageBox__RenderOverlay` supplies the native 120-pixel bar pieces,
bottom-centre anchors, and five 15-pixel line offsets. `CDXFont__CreateFromTexture`
scans alpha above `0x10` to derive proportional glyph widths. The client uses
those released Font13PS metrics to wrap and paginate within the 232×76 text
rectangle and clips every glyph and shadow draw to that rectangle; it does not
use a fixed character-count estimate. Exact 128×128 DXT2 `oo`/`ee`/`mm`/`aa`
frames supply the four Tatiana, technician, and Kramer poses. The released
CircleMask is opaque at the square corners and transparent at its portrait
aperture, so the client first applies the released 0.75 portrait scale, then
multiplies every portrait's alpha by inverse mask alpha before normal alpha
composition. This is the retained mask operation that prevents the opaque black
source square from being rendered.

`CMessageBox__RenderBattleLinePulseSprites` supplies portrait ordering and
8/12/40/40 selection weights. Static evidence does not expose Steam's
process-global RNG seed/initial phase, and this owner does not establish phoneme
analysis. The HUD accepts read-only active-message/playback state from the
integrated audio owner. Page advancement follows actual playback position, and
the deterministic weighted portrait sample remains a presentation
reconstruction rather than a claim of Steam's exact RNG phase. A deterministic
ignored manifest is derived from exact
`LevelScript.msl`, Level 100 `English.txt`, global `text.stf`, and `english.dat`;
Godot verifies its hash and uses native signed ID/text/audio identities while
validating the ordered `PlayCharMessage` speaker/highlight identities. The
presentation projection drains the actual mission events and preserves their
speaker, message, highlight, and help order without feeding HUD timing back
into Core or using a C# fallback message catalog.
The Level 100 script and its
51 exact English audio references use
only Tatiana, the technician, and Kramer; there is no Level 100 video command or
Bink portrait asset.

The canonical mission snapshot supplies enabled weapon gates and HUD emphasis;
its ordered events supply message and help delivery. The canonical actor
registry supplies active objective identities and full three-dimensional poses.
The Godot projection retains those values for rendering and leaves selected
weapon, selection-panel state, weapon resources, classified contacts, threats,
damage flashes, target prediction, active-help lifetime, and influence values
absent until their mechanics owners exist. The HUD does not draw a parallel
terminal/result screen; mission outcome handoff remains owned by the frontend.
This is an ownership boundary, not a claim that every released HUD value or
render pass is complete.
Steam's exact dynamically written 16-bit ring pixels and exact portrait RNG
initial phase remain unproven.

One clean control and two fresh, uninterrupted app-owned Level 100 runs then
repeated the first eight message boundaries within one 50 ms retail sample.
With Core tick zero aligned to Steam's game-time-`3.0` pan start, their intervals
are HUD introduction `182..351`, threat circle `357..567`, scanner `573..756`,
message log `762..926`, technician `932..998`, movement `1004..1220`, Target
Zone 1 instruction `1226..1387`, and objective-scanner instruction `1393..1530`.
The Battle Engine power flag at offset `0x580` changed `0 → 1` at tick `1000`;
the released flight flag at `0x58C` and both initial weapon gates remained off.
At tick `1223`, the object uniquely identified at Target Zone 1's authored
position changed its `CThing` flags at offset `0x2C` from `0x0002` to `0x0022`,
setting objective bit `0x20`. Exact English strings decoded from `english.dat`
and the eight opening Ogg/Vorbis files drive the client.

Two fresh uninterrupted player-input runs then repeated the first objective
handoff. Target Zone 1's radius-5 volume remained active outside centre
distances `5.44` and `5.54`, then overlapped the released Battle Engine's
single-player `0.4` radius by distances `5.29` and `5.39`. Eleven 20 Hz updates
later, both runs changed Target Zone 1 flags `0x22 → 0x02`, Firing Range flags
`0x02 → 0x22`, and the active message to ID `4458134` in the same update. Steam
Battle Engine vtable slot 16 at `0x0040DF80` independently returns `0.4` outside
multiplayer. `CHud__RenderTacticalRadarContacts` at `0x00484C50` supplies the
objective path's yaw rotation, 46-unit clamp, and fixed `0xFFFFFF00` tint used
with the exact 16×16 DXT2 `CompassObjectiveMarker`. The ninth retained voice is
exact `tutorial_02.ogg`, 237871 samples at 44.1 kHz.

One clean control and three fresh uninterrupted runs then followed a
predeclared observer from the Firing Range objective through the first weapon
exercise. Steam's exact objective-list head at module RVA `0x455140` avoided a
broad heap scan. Every accepted run cleared the range objective, deactivated the
player, advanced through message IDs for `TUTORIAL_03`, `HUD_05`,
`TUTORIAL_PULSE_CANNON`, `TUTORIAL_OPEN_FIRE`, and
`TUTORIAL_PULSE_CANNON_2`, and added the same four `CThing` pointers as
objectives at Open Fire. One second later the player power gate changed `0 → 1`
and only the Pulse Cannon's active gate changed `0 → 1`. The copied `Fire`
binding changed Steam's live current-weapon state, proving delivery to player
one independently of the mission messages.

The four pointers repeated bit-identical positions, yaws, and vtable identities
for three Target Tanks and one Warehouse; their exact values and retained asset
hashes live in the Level 100 asset README. The five new Ogg files supply exact
voice lengths. Core consumes the released script's explicit pauses and the
already demonstrated message post-roll/handoff, not variable wall-clock memory
scan latency. The exact overlap-to-event endpoint was not separately sampled,
so `FiringRange.msl`'s 0.5-second dispatch remains source-derived. This proves
the first Pulse Cannon exercise's gates, objectives, ordering, text, and audio,
but does not by itself prove completion, non-objective contacts, or pixel parity.

A no-fire control and fresh isolated copied-runtime runs then followed each of
the three Target Tank pointers, player-owned round list, and objective set. Four
releases at the first active charge bucket (`10`) created normal rounds with
definition speed `35` and exact movement magnitude `1.75` per 20 Hz update.
Each tank began at life `6` with no shield. Direct mesh hits repeated
`6 → 4.2 → 2.4 → 0.6 → -1.2`; each target set its destroyed bit and left the
objective set on shot four. One separate glancing mesh-part hit removed `1.0`.
`CUnit__ApplyDamage` (`0x004F9A90`) receives the mesh-part index and
`CUnit__MarkDestroyedAndCleanupLinks` (`0x004FD140`) owns the removal, so Core
does not generalize the unmeasured part multiplier. It consumes only the
three independently demonstrated direct-hit paths, the retained mesh bound,
and the nearest 30 Hz integer speed.
The speed-`35` physics record names `Mech Pulse Bolt Medium`; its released
five-entry particle descriptor references four unique texture archives: Blue
Spark 2, Blue Trail, Halo, and Energy Trail. Those exact archives and their
authored base dimensions supply the bounded projectile presentation. Exact
`data/ParticleSets/MainSet.par` (SHA-256
`A51FE4419B55E1AF132E31C6B3CD8133C937745D8F4AB691EB5A0D81017DED06`)
supplies the retained small-impact and medium tank-destruction primary
sprite layers, atlas ranges, scales, and lifetimes. Exact
`data/sounds/sounds_english_pc.xap` (SHA-256
`658C15E3BAB844D65DD3C07C4AC880F16F741C0EA116F48C603449BBD4DDA8B7`)
records 35, 106, and 102 supply the retained 44.1 kHz mono fire, small-impact,
and medium-explosion PCM respectively. The record names, decoded lengths,
high-nibble-first IMA-ADPCM output, and retained hashes were independently
validated. A same-return CDB capture at released
`CBattleEngine__GetLaunchPosition` (`0x0040C990`) then resolved cockpit emitter
`Gun`, weapon index `1`, to `-0.005619` right, `+0.080066` forward, and
`+0.259300` up in the live BattleEngine basis. Core consumes the corresponding
rounded millimetre offset; the debugger stop supplied only that static return
value, never timing. Descriptor color ranges, mode-1 tank-smoke blend,
secondary emitters, debris, and wreck geometry remain absent.

The complete-Level-100 audio retention extends that same decode contract
without extending current mission simulation. The accepted canonical Level 100
message table has 51 character-message identifiers; only those exact English
Ogg files are retained. Version-103 `sounds.sfx` resolves the exact PCM records
used by the bounded adapter and supplies their effect volume, pitch variance,
loop, and language fields. Stuart's `CSoundManager::PlayEffect`, `PauseAllSamples`,
`UnPauseAllSamples`, and `KillAllSamples` establish selection/randomization and
lifecycle architecture. Canonical Steam bodies at `0x00404DD0`
`CBattleEngine__Init`, `0x004081C0` `CBattleEngine__Move`, `0x00468770`
`CFrontEnd__PlaySound`, `0x0046FAE0`/`0x0046FB00` game unpause/pause, and
`0x004E1B20` `CSoundManager__UpdateStatus` independently retain the released
effect identities and pause boundary. The adapter consumes ordered numeric
`Level100MessageRequested` events from `FrameAdvanceResult`; it exposes event-
driven entry points for frontend, flight, actor, impact, and pause owners rather
than defining their state. Character-message clips queue by exact retained ID;
script waits and playback-duration gates remain deterministic mission state.
The PC `SetMasterVolume` tangent curve and externally supplied game-sound mix
are presentation-only adapter inputs, so audio applies but never advances a
failure fade or other ducking timeline.

Tracked Steam function summaries for `PauseMenu__Init` at `0x004CDE60`,
`CPauseMenu__Render` at `0x004D11D0`, input dispatch at `0x004D15D0`, action
dispatch at `0x004D0810`, and resume helper `0x004D06E0` identify the retained
Level 100 root, Retry/Quit confirmation, safe default to No, and back behavior.
The retained English table supplies the localized copy; three exact locally
materialized pause textures and the existing HUD fonts supply the asset inputs.
The current renderer's placement, fade gate, circle transition, colors, and hit
regions are bounded reconstruction presentation, not a claim of exact visual or
runtime parity.

Stuart's source demonstrates the single paused-game flag, blocked event advance,
sample pause/unpause, and kill-then-Select level-exit boundary. The client owns
one `AuthenticMenu` pause reason: it advances zero Core steps, clears held and
pending input, pauses the existing gameplay-audio owner, and resumes only after
a neutral input sample. Continue resumes the same session; confirmed Retry and
Quit complete that existing audio boundary once before calling the existing
frontend lifecycle, whose teardown preserves the new Select cue. Message Log,
Briefing, and settings rows are visible but disabled because no canonical
integrated owner exists; no substitute subpage or settings state is inferred.

Stuart's Level 100 entry calls `PlaySelection(MUS_TUTORIAL)`. The playlist is
alphabetically ordered and `GetSong` is zero-based, so selection index `3`
resolves to exact `data/Music/BEA_04(Master).ogg` (SHA-256
`32D3E338964D74F50D0094536C585375F1E14AA2BAE6087487803F3529EAF360`).
Selection playback repeats that track at completion. Music has its own tangent-
curved option volume, remains outside `PauseAllSamples`, and is stopped by the
level-exit owner.

A shallow read-only parse of the supported copied `default physics.dat`
correlates the Level 100 unit, weapon-mode, and explosion assignments. It
establishes the Air Trainer's Forsetti flyby loop, the transport's bomber loop,
Target Drone's silent engine and silent missile-launch modes, Drone Vulcan's
`Blaster 2`, shared Forseti/Micro Missile medium-impact audio, target/truck
medium destruction, drone small-debris destruction,
facility medium-building destruction, Battle Engine huge destruction, and the
repair idle/charge/full triplet. No substitute sound is selected for a missing
assignment. The materializer verifies the decoded WAV envelopes, all 51 voice
Ogg hashes, and the tutorial-music Ogg hash; playback/mixing and stream lifetime
remain exclusively in the Godot adapter.

Static Steam and reference-source evidence establish that Warehouse damage is
forwarded through a 28-entry destructible-segment controller rather than the
root life field used by the tanks. Two fresh uninterrupted app-owned copies
isolated that objective by changing the compiled LevelScript target count from
`4` to `1` at the exact serialized integer byte; archive length and every other
payload byte remained unchanged. Each accepted run required an untouched
Warehouse immediately before the first explicit `Fire`, used only the first
active charge bucket (`10`), and removed the objective on exactly release 12.
Earlier hits distributed damage across the root and mesh segments; the final
hit flipped the controller threshold and cascaded the remaining intact parts.
Core therefore represents only an effective `12 × 1.8` direct-hit envelope and
the retained mesh's outward-rounded `8.240`-unit horizontal bound. It does not
claim the retail segment-selection, rubble, debris, pickup, or landscape-damage
behavior.

Both isolated runs then repeated the released zero-target continuation: player
power changed to `0`, `TUTORIAL_VULCAN_CANNON` played after the script's
one-second pause, and player power returned with Vulcan active and Pulse Cannon
inactive while three moving Target Truck objectives were added. The exact
voice granules and established 18-tick post-roll place the Core weapon handoff
at tick `269` after completion. The trucks had already advanced along their
`FollowWaypointWait` paths when sampled, so their changing positions are not
retained and the Vulcan exercise itself remains unimplemented.

These slices do not make the surrounding vehicle model retail-faithful.
Walker acceleration and the bounded projectile path now use the released
continuous yaw/pitch basis; the eight-way projection remains only in provisional jet
movement. Terrain
response beyond grounded height following, dash behavior, terrain-relative pitch and
occlusion, jet-to-walker simulation, exact backend attenuation, secondary Pulse Cannon
visuals, remaining weapon simulation, and flight
dynamics remain provisional.

A passing replay proves repeatability of the encoded state and input history.
A prior native smoke on the opening-slice base proved the client starts; loads
112 Aquila, 111 static-world,
six target, and ten cockpit material surfaces; instantiates all 1,481 pines and
the 625-vertex/1,152-triangle camera-following water grid plus 2,056 shoreline
triangles; decodes the exact locally materialized mesh, nine
Pulse/target-effect, twenty-nine then-retained HUD, five sky, and five water textures;
validates five PCM sound envelopes; and consumes the
retained heightfield, macro/detail/cloud-shadow terrain inputs, and Core-owned
ground elevation. Its deterministic route enters through the cold click page,
Main Menu, world-100 selection, and Loading before it reaches the first Firing
Range exercise, renders the exact target models and shipped objective markers,
resolves the fourteenth message, removes Target Tank
1 after four bounded full hits with retained shot/impact/destruction
presentation, preserves the expected Core hash, exercises focus/cursor release,
the mission terminal handoff, fresh retry, and return to the same Main Menu,
then exits.
The smoke produces no screenshot and proves no viewport or pixel parity. It
does not prove disabled or unreferenced material modes,
procedural leg solving, collision beyond the two observed facilities,
the separately proven Warehouse completion/Vulcan handoff, mesh-part damage,
secondary effects, complete environment
shading, the inactive optional advanced-water path or dynamic scene
reflection/refraction, the complete mission simulation, later HUD state
production, terrain-relative pitch/occlusion, exact dynamic ring pixels, exact
portrait RNG phase, or visual parity. This HUD milestone deliberately did not
launch Godot or retail; its additional assets and renderer paths are covered by
exact hash materialization, managed compilation, and deterministic Core tests,
not a new runtime visual-parity claim.
