# Onslaught Rebuild

Status: active RE-informed original-code implementation
Last updated: 2026-07-11

This subtree turns the project's static and runtime research into executable
original code. It is deliberately separate from the WinUI toolkit:

- `OnslaughtRebuild.Core` owns deterministic simulation state;
- `OnslaughtRebuild.Headless` replays a checked-in command tape and verifies a
  stable rolling trace hash plus final-state hash; and
- the next bounded slice adds a Godot .NET visual client as a view/input
  adapter over the same Core API.

No Battle Engine Aquila installation, executable, save, media, or extracted
asset is required. The current slice is headless and testable but not yet the
interactive visual client.

The repository pins the .NET 10 SDK for the WinUI toolkit, while this rebuild
targets `net8.0` for Godot .NET compatibility. Install the .NET 8 SDK/runtime as
well; `dotnet --list-runtimes` must include `Microsoft.NETCore.App 8.x`.

## Run

From the repository root:

```powershell
npm run test:rebuild-core
npm run run:rebuild-headless
```

The normal headless command loads its packaged `first-flight.v1.json`, runs the
fixed-step simulation, prints a public-safe summary, and checks both hashes
against independent constants compiled into the headless host. An explicit
`--tape` requires an independently supplied `--expect` trace hash or an
explicit `--no-verify` hash-generation run.

## Current Contract

- 30 deterministic simulation ticks per second;
- integer positions, velocities, resources, cooldowns, and collisions;
- bounded arena movement;
- walker/jet mode changes with energy and shield differences;
- deterministic projectile/target interactions;
- reset behavior that preserves monotonic replay time; and
- canonical SHA-256 final-state hashing over ordered state fields; and
- a versioned rolling SHA-256 trace over every input slot and post-step state.

These are first-slice mechanics, not claims that retail values, timing,
handling, combat, mission behavior, or visuals match Battle Engine Aquila.

## Input And Tick Semantics

- Command-tape span ticks are zero-based input slots. After input slot `0` is
  stepped, the returned snapshot has `Tick == 1`; after a tape completes, the
  snapshot tick equals `durationTicks`.
- `Fire` is a held action and may remain active across a multi-tick span.
  `ToggleMode` and `Reset` are edge actions; command tapes require one-tick
  spans, and interactive clients must send them only on the press edge.
- Each fixed step validates input, increments the snapshot tick, gives `Reset`
  priority over every other action, decrements existing timers, applies a mode
  toggle, resolves movement/facing, updates resources, attempts fire, advances
  projectiles/collisions, and then returns the post-step snapshot.
- A projectile spawned by `Fire` advances once in that same step and reports
  one fewer lifetime tick. A walker-to-jet toggle pays the transform cost and
  the first jet drain in the same step. `Reset` combined with any other action
  restores dynamic state and ignores the other actions while preserving the
  monotonic tick.
- Normal built-in runs use independent headless golden constants. Explicit
  tapes require `--expect <trace-hash>` or `--no-verify`; a hash declared inside
  an explicit tape is metadata, not an independent trust source.
- Headless tape files are capped at 8 MiB before JSON parsing.
- One invocation is capped at 100,000 total simulation steps across repeats.

## License And Provenance

This subtree is GPL-3.0-or-later and RE-informed. Read
[PROVENANCE.md](PROVENANCE.md) before contributing. The strict clean-room path
is a separately staffed future process, not a label for this code.
