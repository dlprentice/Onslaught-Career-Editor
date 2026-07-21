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

The deterministic Core and command-tape/hash format are reconstruction-owned
infrastructure. The Godot Level 100 Opening Slice consumes the released
Federation walker's exact 63-part AYA hierarchy plus bounded static conversions
of the jet, 24 Level 100 static-world mesh types, four pine variants, Target
Tank, and Warehouse meshes; their exact source/output hashes live in the
materializer and ignored generated manifest. The released Level 100 WRES
records now set the player start heading, all 33 visible base-world objects,
1,481 Steam-instantiated pines, trigger locations, and four Firing Range targets. The client
maps BEA `(X, Y, Z-down)` consistently to Godot `(X, -Z, -Y)` for terrain,
retained meshes, facilities, sky, light, camera, and Core-relative positions.
The loose mission scripts establish their order and 0.5-second event delays.
The retained `HFLD` uses the released loader's 64×64 tiled sample layout,
height scale, and 65×65 coarse render sampling. Core embeds the hash-verified
chunk and implements Steam's `0x0047EB80` 24.8 fixed-point signed interpolation
for hashed player-ground elevation. Exact `MAPT`/`MMAP` inputs and
the released
`0x0047EFF0` blend path produce the 512×512 macro landscape texture. Level 100
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
second and confirmed mipmapping enabled with anisotropic macro minification and
the terrain capability and `MODULATE2X` paths.
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
the released half-scale/offset matrix and texture-strength alpha, and mode 4 as
the regular-UV alpha overlay using the serialized `TEXB` offset and scale. Its
special base path tests `CTexture +0xB4`, disables alpha test/blending, and uses
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
the shared wave `MULTIPLYADD`, and two exact `SURF` shoreline bands. Static
Steam evidence at `CWaterRenderSystem__RenderMainPass` (`0x0055B6C0`) establishes
the first-shoreline, grid, alpha-tested sun, and late additive-shoreline order.
The sun uses texture-factor color `#E8E8FF`, alpha reference `0xC0`, and a quad
whose center, half-width, and half-length are respectively `6`, `2`, and `8`
times camera height. The late shore pass uses `SRCALPHA`/`ONE`, no depth write,
and no fog. One uninterrupted copied-Steam sample measured the main phase at
`1` radian per second and both wave scrolls at `0.06` texture cycles per second;
the client advances those presentation phases from frame delta outside Core.
The animated half-scale reflection transform belongs to the optional advanced
path, which remained inactive in controlled Steam observation. Dynamic scene
reflection/refraction and pixel identity outside this bounded active pass are
not claimed.
Steep-slope sliding, structure collision
beyond the two observed facilities, targets, weapons, resources, jet/morph
presentation, and unimplemented HUD behavior remain provisional unless
specific retained evidence says otherwise.

The exact walker AYA supplies 63 reciprocal parent/reference parts, 54 expanded
base-material surfaces, and the 101-frame `LegMotion` table. At the authored
Level 100 start `(288.6875, 243.25)`, yaw `0.509829998`, one fresh app-owned
retail run in raw walker state `2` produced two identical complete pose-buffer
hashes 100 ms apart. The client retains only the resulting twenty local
leg-chain transforms and blends them toward the authored gait from deterministic
Core velocity. This proves the stable opening stance and consumes an authored
walk cycle; it does not reproduce the retail mech controller's per-frame
terrain-aware leg solving or prove arbitrary-terrain foot contact.

One clean Level 100 control and two fresh repeated copies establish the walker
translation and body-turn loop: equal forward/strafe acceleration, a 3.0-unit/s
cap, `0.7` per-retail-update coast, yaw-velocity accumulation, and `0.8`
retention. Core maps those 20 Hz responses into its fixed 30 Hz step. The same
control/repeat discipline maps raw states `2 → 1 → 3` to the explicit
16-tick walker-to-jet transition. Jet forward speed and energy drain retain
earlier bounded measurements.

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

A fresh no-input Level 100 control held
`(288.6875, 243.25, -12.111499)` with zero velocity and unchanged yaw, pitch,
and gait phase. Two fresh copies then repeated the same uninterrupted pointer,
forward, coast, and strafe sequence. Both active runs ended at the same sampled
position, yaw, and pitch and traversed a `6.232587`-radian gait-phase range.
Steam `CBattleEngineWalkerPart::UpdateWalkCycle` at `0x00412AD0` corroborates
the retained authored-cycle rule: dominant local forward velocity advances the
phase by `2.5`, dominant local strafe by `3.0`, with wrapping at `±π`. The
released mech controller's sampled ground normal remained
`(0, 0, -0.99999976)` throughout this short route. This establishes the current
gait phase and flat-route grounding, not the controller's arbitrary-slope foot
solving, body tilt, or steep-slope behavior.

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
The retained 21-part cockpit converts deterministically at that frame and loads
as two complete material-signature surfaces. Godot's camera child uses a bounded 6 cm
depth and 1 cm vertical presentation adjustment, selected against the clean
retail frame to account for its OBJ transform and near-plane path; that adapter
offset is not claimed as a retail model value.

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
pose and each static mesh from its exact lower bound.

Twenty-nine retained HUD textures are exact released files named by the Steam
binary. A clean copied-runtime frame and the released render paths establish
the bounded first-person composition now used by Godot: the generated central
threat compass and three v3 crosshair layers, lower-left scanner/weapon stack,
lower-right battleline or message portrait, and a message-only segmented panel.
`CHud__RenderObjectiveProgressGaugeAndHeadingNeedle` at
`0x004858D0`, `CHud__RenderBattleline` at `0x00487D10`,
`CMessageBox__RenderOverlay` at `0x004B8850`, and the `CDXCompass` render path
provide the retained edge offsets, 45/46/96/98/110/111.5-unit radii, rotations,
packed tints, and state ownership. `CMessageBox__RenderOverlay` supplies the
native 120-pixel bar pieces, bottom-centre anchors, five 15-pixel line offsets,
and 26-character wrap width. `CDXFont__CreateFromTexture` scans alpha above
`0x10` to derive each proportional glyph width. Exact 128×128 DXT2
`oo`/`ee`/`mm`/`aa` frames supply the four Tatiana and technician poses, while
`CMessageBox__RenderBattleLinePulseSprites` supplies their ordering and
8/12/40/40 selection weights. The client makes that selection deterministic at
its presentation cadence; exact retail RNG phase, audio-phoneme sync, other
portrait/video behavior, Steam's dynamic 16-bit ring texture, full multi-stage
mask render state, and the Level 100 influence map are not inferred.

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
records 35, 105, and 102 supply the retained 44.1 kHz mono fire, small-impact,
and medium-explosion PCM respectively. The record names, decoded lengths,
high-nibble-first IMA-ADPCM output, and retained hashes were independently
validated. A same-return CDB capture at released
`CBattleEngine__GetLaunchPosition` (`0x0040C990`) then resolved cockpit emitter
`Gun`, weapon index `1`, to `-0.005619` right, `+0.080066` forward, and
`+0.259300` up in the live BattleEngine basis. Core consumes the corresponding
rounded millimetre offset; the debugger stop supplied only that static return
value, never timing. Descriptor color ranges, mode-1 tank-smoke blend,
secondary emitters, debris, and wreck geometry remain absent.

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
occlusion, jet-to-walker, transform presentation, secondary Pulse Cannon
effects/resources, the remaining weapons, and flight
dynamics remain provisional.

A passing replay proves repeatability of the encoded state and input history.
A native smoke proves the current client starts; loads 58 Aquila, 111 static-world,
six target, and two cockpit material surfaces; instantiates all 1,481 pines and
the 625-vertex/1,152-triangle camera-following water grid plus 2,056 shoreline
triangles; decodes the exact locally materialized mesh, nine
Pulse/target-effect, twenty-nine HUD, five sky, and five water textures;
validates three PCM sound envelopes; and consumes the
retained heightfield, macro/detail/cloud-shadow terrain inputs, and Core-owned
ground elevation. Its deterministic
route reaches the first Firing Range exercise, renders the exact target models
and shipped objective markers, plays the fourteenth voice, removes Target Tank
1 after four bounded full hits with retained shot/impact/destruction
presentation, preserves the expected Core hash, and exits at
both supported viewports. It does not prove disabled or unreferenced material modes,
procedural leg solving, collision beyond the two observed facilities,
the separately proven Warehouse completion/Vulcan handoff, mesh-part damage,
secondary effects, complete environment
shading, the inactive optional advanced-water path or dynamic scene
reflection/refraction, the complete mission,
terrain-relative pitch/occlusion, full HUD behavior, or visual parity.
