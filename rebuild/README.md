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
released Federation Aquila, Control Tower, and Tank Factory geometry at their
authored horizontal opening positions over the released coarse Level 100
heightfield. Core owns the released player start heading, exact Level 100
player-ground sampling, and the Target Zone 1 → Firing Range objective handoff,
including both scripts' 0.5-second event
delay. The walker is loaded directly from its exact released AYA as a 63-part
hierarchy; its twenty animated leg-chain parts begin in the stable retail
Level 100 standing pose and follow the released `LegMotion` cycle as Core moves.
The jet and two facilities retain bounded static conversions. All four render
with their exact retained layer-zero textures. The released macro terrain
blend, repeating detail texture, cube-25 sky, fog, and environment light values
now replace the procedural ground/sky. The opening view uses the released Level
100 four-point exterior fly-in, then hands off to the released first-person
projection and exact walker cockpit at its runtime-selected `walk` pose. The HUD
remains hidden with the pan camera and appears at the control-camera handoff.
Twelve exact HUD textures
and the released Font13PS atlas replace the prototype panels for the bounded
crosshair, radar/radio frames, and current objective line. Secondary material
and moving cloud-shadow passes, steep-slope and actor collision response, combat targets,
weapons,
resources, and most mission
behavior remain provisional.

The project has permission to use, modify, and distribute the original game
assets. Exact source hashes and limitations live with the
[`Aquila`](OnslaughtRebuild.Godot/Assets/Aquila/README.md) and
[`Level 100`](OnslaughtRebuild.Godot/Assets/Level100/README.md) assets. Add
further assets only when a real implemented slice consumes them.

## Run

Install .NET 8, then from the repository root run:

```powershell
npm run run:rebuild-godot
```

The first run downloads the pinned official Godot 4.7 .NET Windows archive to a
per-user cache. The setup script verifies its URL, size, SHA-256, runtime
identity, and extracted tree from
`toolchains/godot-4.7-stable-win-x64.json`. Later runs reuse the verified cache.
Use `pwsh rebuild/tools/Run-FirstFlight.ps1 -Offline` to forbid downloads.

Controls:

| Input | Action |
| --- | --- |
| `W`, `A`, `S`, `D` | Move forward/back and strafe relative to body heading |
| `←`, `→` | Turn body left/right |
| `Space` | Fire the synthetic projectile |
| `Q` | Begin walker-to-jet transition; reverse transition remains provisional |
| `R` | Reset the slice |
| `Esc` | Exit |

## Current truth

Core currently provides integer positions, opening-objective state, resources,
cooldowns, projectile interactions, reset behavior, ordered snapshots, and
versioned SHA-256 state and trace hashes. Continuous body yaw and Level 100
objective state are part of the snapshot/hash, and every input axis—including
look—is part of the trace. Walker acceleration is projected through the body's
continuous deterministic yaw; jet movement and projectile aim still use the
older eight-way approximation.

Repeated Level 100 retail observations now inform walker acceleration, equal
forward/strafe speed, frictional coast, and inertial body turning. Walker-to-jet
remains an explicit transition for 16 Core ticks before Jet mode commits;
repeated transform input, movement, turning, and fire are blocked during that
state. The presentation camera now uses clean Level 100's released opening
lifecycle: four orientation-relative spline points around the exterior Aquila,
a six-second Steam pan, control-view handoff at 5.95 seconds, and then the
attached first-person view at the Aquila center of gravity with its horizontal
orientation column, 58.7155-degree vertical field of view, 0.1 near plane, and
authored frame-25 walker cockpit. Core mirrors the released playing-state
boundary by rejecting player input for the first 180 fixed ticks. Camera pitch response and
terrain clipping, jet movement and projectile heading,
jet-to-walker, transform animation, resource semantics, weapons, terrain
collision beyond grounded height following, AI, the remaining mission, audio,
campaign, and networking
remain provisional or absent.

The client switches between the released walker's exact part hierarchy and a
deterministic static conversion of the released jet, and loads two released
Level 100 facility meshes. The
retired synthetic arena boundary, flat plane, and placeholder structures are
gone. Godot renders the released 65×65 coarse heightfield and samples it for
static presentation placement, generates the released 512×512 macro blend from exact
`MAPT`/`MMAP` inputs, applies the exact Level 100 detail texture at both released
coordinate scales and modulation modes, and renders the five exact cube-25 sky
faces with `CHFD` fog and lighting values. Deterministic Core embeds the same
hash-verified HFLD, applies Steam's 24.8 fixed-point signed interpolation, and
hashes the player's ground elevation. Godot adapts that Core value for the
player rather than running an independent sampler. The client preserves the base material groups and decodes eight exact
AYA-wrapped mesh textures for the Aquila, cockpit, and two facilities. It also
uses twelve exact HUD textures, including the uncompressed released font atlas.
The shared secondary `Chrome3` pass, moving terrain cloud-shadow stage,
visible-sun particle, facility destruction, steep-slope sliding, actor/structure
collision, procedural foot placement/terrain IK,
transform animation, HUD contacts and state logic, radio portraits/video,
tutorial dialogue and gates, and the full mission remain unimplemented. Core's
three synthetic combat targets still exercise the older firing path, but the
Level 100 presentation no longer draws them or synthetic objective beacons as
retail scenery.

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
