# Onslaught Rebuild

Status: active RE-informed original-code implementation
Last updated: 2026-07-12

This subtree turns the project's static and runtime research into executable
original code. It is deliberately separate from the WinUI toolkit:

- `OnslaughtRebuild.Core` owns deterministic simulation state;
- `OnslaughtRebuild.Client` converts real-time input into exact 30 Hz Core
  steps without owning simulation truth;
- `OnslaughtRebuild.Headless` replays a checked-in command tape and verifies a
  stable rolling trace hash plus final-state hash; and
- `OnslaughtRebuild.Godot` is the playable First Flight visual/input adapter.
  Default visuals are original procedural geometry and UI. Optional local-only
  local mesh preview can load ignored user-supplied assets from `local-lab/rebuild-godot/`
  (never committed; non-parity).

No Battle Engine Aquila installation, executable, save, media, or extracted
asset is required for the default synthetic path. First Flight is a small
playable prototype, not a replacement for the retail game.

The repository pins the .NET 10 SDK for the WinUI toolkit, while this rebuild
targets `net8.0` for Godot .NET compatibility. Install the .NET 8 SDK/runtime as
well; `dotnet --list-runtimes` must include `Microsoft.NETCore.App 8.x`.

## Play First Flight

From the repository root, either double-click
`rebuild\Launch First Flight.cmd` or run:

```powershell
npm run run:rebuild-godot
```

The first launch downloads the pinned official Godot 4.7 .NET Windows archive
(about 114 MB) into a per-user cache. The setup script verifies the archive
URL, byte length, SHA-256, runtime identity, and every extracted file against
`rebuild/toolchains/godot-4.7-stable-win-x64.json`. Later launches reuse that
verified cache. Use `pwsh rebuild/tools/Run-FirstFlight.ps1 -Offline` to require
cache-only operation.

First Flight starts in a resizable 1280x720 window with a supported minimum of
1200x675. Controls are:

| Input | Action |
| --- | --- |
| `W`, `A`, `S`, `D` | Move |
| `←`, `→` | Look left/right (body yaw; dual-accepted turn-p02 rate) |
| `Space` | Fire |
| `Q` | Toggle walker/jet mode |
| `R` | Reset the arena |
| `Esc` | Exit |

Destroy the three procedural sentries. The HUD reports mode, objective, energy,
shield, and hull. Look rate uses `WalkerLookYawRateMilliRadPerTick` (retail
Look/Left dual-accept); free-camera patch proofs are not Core authority.

## Optional user-supplied local mesh presentation

Ignored, user-extracted BYO assets can replace the synthetic Aquila stand-in
and ground plane without changing Core or Client simulation. This is a
trusted-local workflow for canonical retail inputs, not an untrusted-file
service, redistribution path, or parity/provenance proof.

```powershell
npm run init:rebuild-godot-assets
npm run export:local-bea-assets
# Convert selected exported FBX files to self-contained GLB or bounded OBJ.
# Put only the converted files in local-lab/rebuild-godot/staging/from-export,
# then select exactly one player mesh and one terrain mesh:
npm run bootstrap:rebuild-godot-assets -- -PlayerMesh aquila-player.glb -TerrainMesh ground-terrain.glb
npm run run:rebuild-godot:local
```

All generated/staged files stay under the ignored
`local-lab/rebuild-godot/` workspace (see `LOCAL_LAB_OVERLAY.md` and
`rebuild/local-assets.layout.json`). FBX may be staged but is never activated;
bootstrap reads converted files only from `staging/from-export` and fails on
missing or ambiguous roles. Runtime support is limited to self-contained GLB
with bounded core-glTF arrays/accessors/BIN ranges and a nonempty mesh primitive,
or bounded OBJ. Bootstrap writes both verified roles into one immutable
`versions/<content-id>/` generation and atomically publishes `manifest.json`
last; an interrupted generation remains unreferenced. Ordinary run and smoke
commands stay synthetic; the dedicated local command supplies the exact
`--local-assets` root. Failed or empty roles keep procedural geometry, and the
HUD describes a neutral user-supplied local mesh only after a nonempty renderable surface loads.
No retail-origin claim is made without a separately bound exporter receipt and
hash. Local assets are never simulation truth, redistribution material, or
parity evidence.

The export wrapper consumes the exact template
`references/AYAResourceExtractor/BoxWithTextures.fbx`. It preflights and holds
that file plus `AYAResourceExtractor.dll`, `DDSTextureUncompress.dll`, and
`Fbx.dll` before creating output. These are mutable trusted-local dependencies,
not cryptographically pinned provenance. The workflow is bounded to trusted
canonical retail input and process failure; it is not hostile-input sandboxing.

## Verify

From the repository root:

```powershell
npm run test:rebuild
npm run build:rebuild-godot
npm run test:rebuild-core
npm run run:rebuild-headless
```

The normal headless command loads its packaged `first-flight.v1.json`, runs the
fixed-step simulation, prints a public-safe summary, and checks both hashes
against independent constants compiled into the headless host. An explicit
`--tape` requires an independently supplied `--expect` trace hash or an
explicit `--no-verify` hash-generation run.

`npm run test:rebuild` is the ordinary deterministic contract gate. It runs
Core tests, interactive-adapter tests, hostile toolchain-manifest/extraction
and process-lifecycle tests, smoke-evidence validator tests, and focused local
asset manifest/mesh/workspace safety tests. It does not
invoke the Godot downloader or open a native window; normal .NET restore may
still use configured package sources when dependencies are not cached.
`npm run test:rebuild-godot-smoke` is the separate native acceptance smoke. It
builds with the pinned engine, runs the same scripted 120-tick session at
1280x720 and 1200x675, validates the exact final state hash plus heuristic
semantic HUD/player/sentry/world color anchors, exercises the Godot
focus-notification handler and neutral rearm contract synthetically, checks
owned-process cleanup, and writes ignored evidence under `local-proofs/`.
Those rendered-frame checks catch blank, misframed, and gross composition
regressions; they are not tamper-resistant or independent visual proof. The
handler probe is not proof that Windows delivered a real focus transition.

## Toolchain Boundary

Normal setup accepts only the tracked manifest at its fixed path and checks its
own SHA-256 before trusting any field. The per-user cache rejects reparse-point
paths, verifies all 82 files, holds every verified file against write/delete,
and retains the setup lock through restore, build, and engine execution.

This is corruption, substitution, and cooperating-process hardening for a
developer tool cache. It is not a security sandbox against another malicious
process already running as the same Windows user; that process shares the
account's filesystem and process authority. Do not elevate the cache or run
untrusted software beside the build.

## Current Contract

- 30 deterministic simulation ticks per second;
- integer positions, velocities, resources, cooldowns, and collisions;
- bounded arena movement;
- walker/jet mode changes with energy and shield differences;
- deterministic projectile/target interactions;
- reset behavior that preserves monotonic replay time;
- canonical SHA-256 final-state hashing over ordered state fields;
- a versioned rolling SHA-256 trace over every input slot and post-step state;
- a real-time adapter with exact rational 30 Hz accumulation, bounded catch-up,
  held-action sampling, one-tick quick-tap preservation, and press-edge
  latching for toggle/reset; and
- a Godot view that renders Core snapshots but cannot mutate Core state.

These are first-slice mechanics, not claims that retail values, timing,
handling, combat, mission behavior, or visuals match Battle Engine Aquila.

## Input And Tick Semantics

- Command-tape span ticks are zero-based input slots. After input slot `0` is
  stepped, the returned snapshot has `Tick == 1`; after a tape completes, the
  snapshot tick equals `durationTicks`.
- `Fire` is a held action and may remain active across a multi-tick span.
  `ToggleMode` and `Reset` are edge actions; command tapes require one-tick
  spans, and interactive clients must send them only on the press edge.
- Interactive quick taps for movement or fire are retained for one simulation
  tick even when press and release occur between ticks. Held and pulse input
  coalesce instead of producing duplicate actions. The Godot focus-notification
  handler releases all held and pending input and ignores new input until one
  neutral sample is observed.
- Real-time frame elapsed values are capped at 250 ms. Excess elapsed time is
  reported as dropped time instead of causing an unbounded catch-up spiral.
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
