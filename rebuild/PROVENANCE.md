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
- The project has full permission to use, modify, and distribute the original
  game assets. Selected assets may enter the rebuild when an implemented slice
  consumes them and their provenance, credits, and third-party terms are clear.

Do not import the retail executable, decompiler output, user saves, raw runtime
captures, or separately licensed third-party code/media into this subtree.
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
of the jet, Control Tower, and Tank Factory meshes; their exact source/output
hashes live with the assets. The released Level 100
WRES placement records now set the player start heading, two nearby facility
placements, and the Target Zone 1 and Firing Range trigger locations. The client
maps BEA `(X, Y, Z-down)` consistently to Godot `(X, -Z, -Y)` for terrain,
retained meshes, facilities, sky, light, camera, and Core-relative positions.
The loose mission scripts establish their order and 0.5-second event delays.
The retained `HFLD` uses the released loader's 64×64 tiled sample layout,
height scale, and 65×65 coarse render sampling. Exact `MAPT`/`MMAP` inputs and the released
`0x0047EFF0` blend path produce the 512×512 macro landscape texture. The client
preserves each retained mesh group's layer-zero `TEXR` assignment and directly
decodes eight exact AYA-wrapped mesh textures. Five exact DXT1 cube-25
textures use the released face order and geometry; `CHFD` fog and light values
drive the Godot environment. The released renderer's later material
passes—including the shared layer-two `Chrome3` reference,
terrain-detail/cloud stages, and
visible-sun particle—are not guessed. Terrain collision/response, targets,
weapons, resources, jet/morph presentation, and unimplemented HUD behavior
remain provisional unless specific retained evidence says otherwise.

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

A clean copied Level 100 run starts player zero with current/preferred view `1`.
After the opening fly-in, five uninterrupted samples held the same active camera
pointer and first-person `CThingCamera` vtable `0x005DBB88`. The Battle Engine
position remained `(288.6875, 243.25, -12.111499)`, yaw remained `0.509829998`,
and the horizontal forward column remained `(-0.488029, 0.872827)`. The camera
position is the Battle Engine position, and the Steam 16:9/zoom-1 projection term
`0.5625` gives a 58.7155-degree vertical field of view. The cockpit pointer at
Battle Engine offset `0x528` selected animation index `1`; the exact `cockpit2.msh`
`CAMD` table identifies that as `walk`, authored hierarchy frame 25. Runtime
also reported the cockpit render flag enabled and no local position offset.
The retained 21-part cockpit converts deterministically at that frame and loads
as two layer-zero texture surfaces. Godot's camera child uses a bounded 6 cm
depth and 1 cm vertical presentation adjustment, selected against the clean
retail frame to account for its OBJ transform and near-plane path; that adapter
offset is not claimed as a retail model value.

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

Twelve retained HUD textures are exact released files named by the Steam
binary. A clean copied-runtime frame establishes the bounded first-person
composition now used by Godot: center crosshair/weapon layers, lower-left radar,
lower-right radio frame, and lower-center message treatment. The current
objective is rendered from the released Font13PS atlas. This does not establish
complete HUD state logic, contacts, radio portraits/video, weapon selection,
damage presentation, tutorial timing, or pixel parity.

These slices do not make the surrounding vehicle model retail-faithful.
Eight-way movement projection, terrain response, dash behavior, camera pitch and
occlusion, jet-to-walker, transform presentation, resources, weapons, and flight
dynamics remain provisional.

A passing replay proves repeatability of the encoded state and input history.
A native smoke proves the current client starts, loads the four exterior meshes
with 65 base-material surfaces (57 Aquila and eight facility), the two-surface
cockpit, eight mesh textures, twelve HUD textures, five sky textures, the
retained heightfield and exact macro terrain inputs, omits synthetic target and
objective-marker scenery, renders, advances, preserves the expected
deterministic Core hash, and exits. It does not prove secondary material or
terrain-detail passes, procedural leg solving, collision, complete environment
population, the complete mission, camera pitch/occlusion, full HUD behavior,
timing, or visual parity.
