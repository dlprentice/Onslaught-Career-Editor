# Shield Live Measurement Readiness Design

Status: unattended maintainer-approved design
Date: 2026-07-14

## Goal

Make walker shield regeneration a first-class, receipt-bound measurement mode
without coupling resource-rate acceptance to walker motion, velocity, or a held
input. This slice prepares the existing two-attempt runner for shield evidence;
it does not launch Battle Engine Aquila, publish a retail contract, or authorize
a Core constant.

## Selected Approach

Add `shield` to the existing walker sampler's live measure-mode catalog and
route it through the established observer, receipt revalidation, foreground
guard, cleanup owner, and two-attempt lifecycle. Unlike forward, turn, strafe,
and jet-energy modes, shield collection owns no Q input. It records the normal
baseline/observation/release sample windows while the walker remains idle and
analyzes the paired `BattleEngine+0xFC` energy and `BattleEngine+0x100` shield
floats.

The private analysis accepts an attempt only when:

- the vehicle is the walker;
- at least five shield-update edges show positive regeneration;
- energy changes positively on the same sampled update edges often enough to
  establish correlation;
- the steady shield and energy rates agree within a bounded scaffold tolerance;
- all values and timestamps are finite and monotonic; and
- receipt identity, foreground ownership, observer-handle closure, process
  cleanup, copied-source immutability, and lab hygiene retain their existing
  fail-closed behavior.

The rate/correlation thresholds are sampler acceptance tolerances, not retail
constants and not deterministic-Core authority. The pair envelope remains a
`v0-scaffold` until two separately accepted copied-runtime attempts justify a
public v1 contract.

## Rejected Approaches

### Reuse the Q/forward hold path

Rejected because the current path proves a movement-control store and then
runs position/velocity acceptance. That would make a valid resource-rate trace
depend on unrelated motion and would actively move the walker during an idle
regeneration observation.

### Create a second shield-only runtime observer

Rejected because it would duplicate receipt identity, module binding,
foreground checks, deadlines, process ownership, cleanup, and private-root
enforcement already hardened in the walker measurement runner.

## Components

### Paired shield analysis

`tools/battleengine_shield_scaffold.py` consumes timestamped energy/shield
samples, computes update-edge rates, verifies positive paired regeneration, and
materializes a two-attempt provisional envelope. Synthetic fixtures cover
valid correlation, inactive energy, opposite direction, excessive rate spread,
non-monotonic timestamps, and unstable attempt pairs.

### Receipt-bound input-free collection

`tools/run_battleengine_walker_trajectory_measurement.py` adds the `shield`
mode, validates walker-only use, collects three guarded idle phases without
creating Q request markers, and emits a private shield metrics payload with an
explicit `none-idle-observation` input protocol. Other measure modes retain
their existing input and motion semantics.

### Catalog and command authority

The measure-mode catalog moves shield from the offline-only list into live
sampler wiring with status `sampler-wired; live dual-accept pending`.
`package.json` exposes the orchestrator test directly and a focused walker
measurement-contract composite; it does not expand the broad
`test:runtime-tooling-safety` aggregate.

## Verification Model

This slice makes no visual claim, so screenshots would be weaker evidence than
the underlying floats. Its unattended verification harness is deterministic
synthetic trace replay through the real scaffold and runner dispatch. Future
Godot or WinUI presentation changes must add native capture/comparison evidence
when their acceptance claim is visual.

Focused validation is:

- shield scaffold tests;
- walker sampler tests;
- measurement orchestrator tests;
- measure-mode catalog tests;
- the new focused package composite;
- Python compilation and `git diff --check`; and
- the repository's required normal/adversarial Codex and sanitized external
  review envelope before acceptance.

## Authority And Nonclaims

- No installed game or original `BEA.exe` access or mutation.
- No BEA launch, live memory read, debugger, input, screenshot, or runtime
  attempt during offline readiness work.
- A later live pair requires the complete action family, allowed/forbidden
  commands, resource lease, exact private proof-root policy, validation gates,
  cleanup/rollback, and expiration required by `goal.policy.md`.
- No third attempt.
- One failed attempt means no behavior contract.
- No shield rate, tick map, damage behavior, visual parity, retail parity,
  online capability, release, or Core constant is claimed by this design.
