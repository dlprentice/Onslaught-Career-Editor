# Rebuild determinism contract

Status: active — the contract a contributor breaks first
Last updated: 2026-08-07
Evidence: SOURCE — constants and behaviors cited against
`references/Onslaught` (thing.h, eventmanager.cpp) and the tracked Core and
Headless sources named at the bottom; the retail 20 Hz step was MEASURED in
the 20 Hz migration evidence.
Summary: what "deterministic" means in this rebuild, what is enforced, and
what a contributor must do when a change legitimately moves the trace hash.

## The fixed step

`OnslaughtRebuild.Core` advances on a fixed 20 Hz step:

- `CLOCK_TICK = 0.05 s` / `GAME_FR = 20.0` — `SimulationConstants.cs`, derived
  from `references/Onslaught/thing.h:28-29` and `eventmanager.cpp:296`
  (`mTime = mFrameCount * CLOCK_TICK`).
- Retail floors every scheduled delay onto a whole 20 Hz boundary
  (`delay *= GAME_FR; delay = floorf(delay)`, `eventmanager.cpp:210-212`);
  the rebuild does the same.
- The prior 30 Hz step was migrated out in the 20 Hz work; constants that
  carry a tick-rate derivation are verbatim retail values where retail fixed
  them (e.g. the landing-thruster factor is retail's 0.975 exactly).

## What Core may not do

Core simulation truth must be independent of presentation and environment.
Core code does not call:

- presentation, filesystem, clock, process, network, or GPU APIs;
- anything that reads wall time, locale, environment, or thread scheduling.

Clients (the Godot renderer, the headless runner, tests) adapt Core state;
they never own simulation truth. `StateHasher` computes canonical SHA-256
state and trace hashes over ordered, versioned snapshots so a run is
comparable byte-for-byte across hosts.

## The tape and its bounds

The headless runner (`OnslaughtRebuild.Headless`) records input tapes and
replays them:

- `MaximumTapeBytes = 8 MiB`
- `MaximumReplaySteps = 100 000`
- A replay is run twice; the second run must reproduce the first run's hash,
  or the run fails with "Determinism failure: repeated replay produced
  different hashes."
- `--expect <hash>` requires the replay trace hash to equal the expected
  value exactly.

## What `--expect` means

An expected hash is the frozen fingerprint of one exact scenario at one exact
revision. It is owned by whoever pinned it (usually the test that asserts
it). A hash is a claim about the whole deterministic state machine: inputs,
constants, float/ordering policy, and the hash function itself.

## When a change legitimately moves the trace hash

Fixes that change simulation behavior (a retail constant corrected, a
physics law updated, a float-ordering change) legitimately move every trace
hash downstream. This is expected — but it must be deliberate and recorded:

1. Run the affected scenario(s) and capture the new hash.
2. Re-pin the expected hash in the owning test **in the same commit** as the
   behavior change, with a comment naming the behavior change.
3. Do not re-pin to hide a nondeterminism failure. If the replay produces
   different hashes across identical runs, that is a determinism defect, not
   a pin problem — stop and fix the divergence first.
4. If the change is visual-only or presentation-only, Core trace hashes must
   NOT move. A renderer change that moves Core hashes means the renderer
   leaked into Core state.

## Enforced by

- `Level100ColdStartTests` and the deterministic run fixtures (cold start,
  pointer-quantised, full-chain).
- `InteractiveSessionTests` (100 000-step bounds).
- `HeadlessApplicationTests` (8 MiB tape bound, replay determinism, `--expect`,
  and the pinned first-flight trace/state fingerprint owner).
- `StateHasher` canonical-format tests.

A contributor who touches `Simulation.cs`, `SimulationConstants.cs`,
`SimulationTypes.cs`, or anything in the tick/step path should expect the
cold-start and full-chain suites to be the first (and most sensitive) signal.
