# Onslaught Rebuild

Status: early GPL reconstruction lane

This subtree is the replacement-engine effort for *Battle Engine Aquila*. It is
source- and RE-informed, not clean-room. The immediate target is a recognizable
Aquila handling slice followed by the opening portion of Level 100—not a larger
synthetic arena or another layer of readiness tooling.

## Ownership

- `OnslaughtRebuild.Core` owns deterministic simulation state and fixed 30 Hz
  stepping. It has no presentation, filesystem, clock, process, network, or GPU
  dependency.
- `OnslaughtRebuild.Client` adapts real-time input to exact Core steps.
- `OnslaughtRebuild.Headless` replays command tapes and verifies versioned final
  state and rolling trace hashes.
- `OnslaughtRebuild.Godot` renders Core snapshots and supplies player input.

The current Godot app is the **Level 100 Opening Slice**. It renders the
locally materialized released Federation Aquila; all 33 visible static objects
serialized by Level 100; all 1,481 pine placements instantiated by the Steam
world loader; the released active-path water grid and authored shoreline; three
training tanks; and the target Warehouse at their authored positions over the
released coarse Level 100 heightfield. Core owns the released player start heading, exact
Level 100 player-ground sampling, and the machine-observed objective and player
gates through the first Firing Range exercise. The walker is loaded directly
from its exact released AYA as a 63-part
hierarchy; its twenty animated leg-chain parts begin in the stable retail
Level 100 standing pose and follow the released `LegMotion` cycle as Core moves.
The jet, 24 static-world mesh types, four pine variants, and two target types
retain bounded static conversions and render with their complete active retail
material passes. Their lighting follows the released PC ambient, opposing
sun/anti-sun, and `MODULATE2X` path rather than approximate Godot PBR values. The
released macro terrain blend, repeating detail and moving cloud-shadow textures,
cube-25 sky, and exponential `CHFD` fog now replace the procedural ground/sky.
The shared fixed-function shader also owns the renderer-aware final color
transfer, so the Compatibility renderer does not apply the old double transfer.
The opening view uses the released Level
100 four-point exterior fly-in, then hands off to the released first-person
projection and exact walker cockpit at its runtime-selected `walk` pose. The HUD
remains hidden with the pan camera and appears at the control-camera handoff.
Twenty-three exact HUD textures and the released Font13PS atlas now compose the
bounded v3 crosshair, threat compass, lower-left scanner/weapon instrument,
lower-right battleline/portrait, active-objective markers, and conditional
message panel. The first seventeen released English tutorial messages through
the first exercise's Vulcan handoff now use their exact text, shipped voice
clips, and static Tatiana/technician portrait frames. Core follows the observed
power, objective, weapon-highlight, four-target, and Pulse Cannon activation
boundaries while keeping flight disabled. Independently repeated lowest-charge
Pulse Cannon runs now give all three training tanks their retail speed,
direct-hit damage, and four-hit deactivation. Two isolated Warehouse runs also
repeat one fixed center-aim twelve-hit path and the released Vulcan handoff.
Godot consumes the exact released round, impact, tank-destruction, sound, text,
and voice assets required by that path.
Core also reproduces only the observed circular walker
contact and tangent slide for the Control Tower and Tank Factory. Secondary
material passes, steep-slope and other actor/structure
collision response, mesh-part damage variation, weapon resources, the target
Warehouse's segment-specific damage/rubble, secondary debris/effects, moving
truck exercise, Vulcan firing, and most mission behavior remain provisional.

Retail asset payloads and converted copies are not repository source. The
bounded materializer verifies a supported user-provided installation and writes
the exact current slice to ignored paths. Expected source hashes and limitations
live with the [`Aquila`](OnslaughtRebuild.Godot/Assets/Aquila/README.md) and
[`Level 100`](OnslaughtRebuild.Godot/Assets/Level100/README.md) recipes.

## Run

Install .NET 8, then from the repository root run:

```powershell
npm run run:rebuild-godot
```

The command first detects a lawfully obtained retail installation and
materializes 142 exact source/runtime files to ignored paths. For a custom
location, run
`pwsh rebuild/tools/Run-FirstFlight.ps1 -GameRoot "<game folder>"`. The first
run also downloads the pinned official Godot 4.7 .NET Windows archive to a
per-user cache. The setup script verifies its URL, size, SHA-256, runtime identity, and extracted tree from
`toolchains/godot-4.7-stable-win-x64.json`. Later runs reuse the verified cache.
Use `pwsh rebuild/tools/Run-FirstFlight.ps1 -Offline` to forbid downloads.

`npm run prepare:rebuild-assets` performs the same exact local materialization
without building or launching. Core, client, headless, and native smoke commands
use that same owner; no separate manual extraction path is required.

Controls:

| Input | Action |
| --- | --- |
| `W`, `A`, `S`, `D` | Move forward/back and strafe after the tutorial powers the Aquila |
| `←`, `→` | Turn body left/right after the same handoff |
| `↑`, `↓` | Aim the attached first-person view up/down |
| `Space` | Fire the Pulse Cannon after the Firing Range enables it |
| `R` | Reset the slice |
| `Esc` | Exit |

## Current truth

Core currently provides integer positions, opening tutorial/objective state,
reset behavior, ordered snapshots, and versioned SHA-256 state and trace hashes.
Resource and cooldown behavior remains provisional. The bounded three-training-
tank path uses the observed Pulse Cannon gate, continuous-yaw projectile heading,
retail speed, direct-hit damage, and objective removal. Continuous body yaw and
Level 100 objective state are part of the snapshot/hash, and every input axis—including
look—is part of the trace. Walker acceleration is projected through the body's
continuous deterministic yaw; only jet movement retains the older eight-way
approximation.

Repeated Level 100 retail observations now inform walker acceleration, equal
forward/strafe speed, frictional coast, and inertial body turning. Walker-to-jet
remains an explicit transition for 16 Core ticks before Jet mode commits;
repeated transform input, movement, turning, and fire are blocked during that
state, but clean Level 100 keeps the flight gate closed throughout the current
slice. The presentation camera now uses clean Level 100's released opening
lifecycle: four orientation-relative spline points around the exterior Aquila,
a six-second Steam pan, control-view handoff at 5.95 seconds, and then the
attached first-person view at the Aquila center of gravity with its horizontal
orientation and BattleEngine-owned vertical pitch, 58.7155-degree vertical
field of view, 0.1 near plane, and authored frame-25 walker cockpit. Core
mirrors the released playing-state
camera boundary at 180 fixed ticks, then keeps movement/look gated until the
mission powers the Aquila at tick 1000. Reaching the Firing Range temporarily
deactivates the player, then re-enables it with the Pulse Cannon; flight remains
disabled. Walker pitch uses the released 20 Hz `1/117`-radian input and `0.8`
retention translated to 30 Hz, with the two repeated absolute limits measured
on Level 100's authored start slope. Pulse Cannon rounds use the same yaw/pitch
direction as the crosshair camera and begin at the measured cockpit `Gun`
emitter. Terrain-relative pitch limiting, vertical target collision, auto-aim,
mouse response, terrain clipping,
jet movement,
jet-to-walker, transform animation, resource semantics, the rest of the weapon
model, target mesh-part damage,
secondary hit/destruction effects and debris, terrain collision
beyond grounded height following, AI, the mission
beyond the first four-target exercise and its weapon handoff,
campaign, and networking
remain provisional or absent.

The client switches between the released walker's exact part hierarchy and a
deterministic static conversion of the released jet. It decodes Level 100's
version-50 base-world records into 33 visible static instances, 24 mesh types,
and 1,481 pines across four variants, while retaining the separate Target Tank
and Warehouse meshes. The
retired synthetic arena boundary, flat plane, and placeholder structures are
gone. Godot renders the released 65×65 coarse heightfield and samples it for
static presentation placement, generates the released 512×512 macro blend from exact
`MAPT`/`MMAP` inputs, applies the exact Level 100 detail texture at both released
coordinate scales, inserts the exact moving cloud-shadow stage with its released
scroll and modulation, and renders the five exact cube-25 sky
faces with `CHFD` fog and lighting values. Terrain, static objects, cockpit,
targets, and water share the released exponential fog color/density path. Static
objects use the released ambient plus opposing sun/anti-sun fixed-function
equation and stage-zero `MODULATE2X`; final color transfer follows Godot's active
renderer contract rather than converting Compatibility output twice.
Deterministic Core embeds the same
hash-verified HFLD, applies Steam's 24.8 fixed-point signed interpolation, and
hashes the player's ground elevation. Godot adapts that Core value for the
player rather than running an independent sampler. The client preserves each
active mesh group's six ordered retail texture slots and decodes the exact
AYA-wrapped textures selected by the Aquila, cockpit, static world, pines, and
range targets plus the four exact 64×64
textures named by the medium Pulse Bolt descriptor. It also uses twenty-three
exact HUD textures, including the three released v3 crosshair layers,
uncompressed font atlas, scanner/north sprites, battleline, portrait/noise
treatment, and objective marker. The observed player route uses Steam's
5.4-unit overlap and delayed dispatch to replace Target Zone 1 with the Firing
Range on that radar. A control and three repeated retail runs then establish the
Firing Range's five-message sequence, current-weapon highlight, four objective
targets, temporary player deactivation, and Pulse Cannon-only activation. The
client uses the exact seventeen retained English lines and voices through its
Vulcan handoff. A no-fire control and fresh isolated copied-runtime runs then
established the first charge bucket, definition speed `35`, `1.75`-unit released
update, life `6`, direct-hit damage `1.8`, and four-shot objective removal for
each of the three training tanks; one separate glancing hit removed `1.0`.
Two isolated Warehouse repetitions then required twelve normal hits along one
fixed center-aim attack line before terminal objective removal and the same
Pulse-to-Vulcan gate. Core deliberately implements only those demonstrated
paths. Godot removes each completed model and radar marker and presents retained
shot, hit, tank-destruction, text, voice, and primary particle layers.
Water reproduces the fixed-function path active on the supported Steam specimen:
its camera-following grid, Level 100 color, two caustic stages, authored
reflection image, sun stages, and both exact shoreline bands. This is not a
claim of dynamic scene reflection/refraction or the inactive optional advanced
water path. The visible-sun
particle, facility destruction,
steep-slope sliding,
actor/structure collision beyond the observed Control Tower and Tank Factory
contact envelopes, procedural foot placement/terrain IK,
transform animation, general HUD contacts and later state logic, Steam's
dynamic ring texture, full multi-stage mask state and Level 100 influence map,
animated radio portraits/video, Warehouse segment-specific health and breakup,
mesh-part damage variation, secondary particles/debris, the three moving trucks,
Vulcan ballistics, and the remainder of the mission remain
unimplemented. The old seeded synthetic targets are gone;
Core and Godot now share the four observed retail targets and shipped objective
marker without adding world-space beacons.

## Verify

Choose the smallest relevant command:

```powershell
npm run test:rebuild-core
npm run test:rebuild-client
npm run run:rebuild-headless
npm run test:rebuild-godot-smoke
```

The headless host loads the checked-in `first-flight.v1.json`, repeats it, and
fails if identical inputs diverge. It reports versioned state and trace hashes;
callers may supply `--expect <trace-hash>` when they own an external expected
result. Files are limited to 8 MiB and one invocation to 100,000 total steps.

The native smoke builds with the pinned engine, starts the real Godot window,
runs a bounded scripted input sequence, checks the final deterministic state,
captures a disposable frame for gross render inspection, and exits its owned
process. It is startup/render evidence, not retail comparison.

Read [PROVENANCE.md](PROVENANCE.md) before implementation work. Retail behavior
claims must point to the smallest relevant binary/source/runtime evidence; Core
agreement never re-proves retail.
