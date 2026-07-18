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
heightfield. Core owns the released player start heading and the Target Zone 1
→ Firing Range objective handoff, including both scripts' 0.5-second event
delay. The four released meshes render with their exact retained layer-zero
textures. The Aquila uses the retained meshes' retail-unit scale and the
released third-person walker's pitch-zero framing. Secondary material passes,
terrain appearance and collision/response, combat targets, weapons, resources,
and most mission behavior remain provisional.

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
look—is part of the trace. Movement is projected relative to the body's
deterministic eight-way heading.

Repeated Level 100 retail observations now inform walker acceleration, equal
forward/strafe speed, frictional coast, and inertial body turning. Walker-to-jet
remains an explicit transition for 16 Core ticks before Jet mode commits;
repeated transform input, movement, turning, and fire are blocked during that
state. The presentation camera now uses the released third-person class's
pitch-zero walker geometry; clean retail Level 100 still starts in first-person
view, so this is not a claim that third-person is the mission default. Camera
pitch response and terrain clipping, eight-way movement projection,
jet-to-walker, transform animation, resource semantics, weapons, terrain
collision/response, AI, the remaining mission, audio, campaign, and networking
remain provisional or absent.

The client switches between deterministic static conversions of the released
walker and jet meshes and loads two released Level 100 facility meshes. The
retired synthetic arena boundary, flat plane, and placeholder structures are
gone. Godot renders the released 65×65 coarse heightfield and samples it for
presentation placement, but deterministic Core still has no terrain elevation
or collision. The client preserves the base material groups and decodes seven
exact AYA-wrapped DXT2 textures for the Aquila and two facilities. The shared
secondary `Chrome3` pass, terrain textures and sky, facility destruction, part
articulation, transform animation, retail HUD/cockpit, tutorial dialogue and
gates, and the full mission remain unimplemented; three synthetic combat targets
still exercise the older firing path and are not Level 100 parity.

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
