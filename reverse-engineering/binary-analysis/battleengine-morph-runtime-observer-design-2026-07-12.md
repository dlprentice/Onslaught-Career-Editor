# BattleEngine Morph Runtime Observer Design - 2026-07-12

Status: user-approved design; implementation and copied-runtime execution pending

## Decision

Use a three-stage progression:

1. prove process, module, player, input, BattleEngine, Morph, Move, and JetPart
   identity in a controlled Level 850 run;
2. measure raw morph-state transitions in fresh controlled Level 850 runs; and
3. corroborate the accepted behavior in the recognizable Level 100 tutorial.

This is deliberately narrower than a full movement sampler. The first run is
an identity-and-causality canary, not a behavior measurement. It must pass
before any retail-derived movement or transform behavior changes the rebuild.

The rejected alternatives were:

- sampling many candidate fields immediately, which could produce precise but
  misattributed results; and
- starting only in Level 100, where tutorial scripting, camera behavior, and
  encounter state make causal interpretation weaker.

## Evidence Hierarchy

The released Steam executable is the behavior target. Read-only Ghidra static
analysis and copied-runtime observations provide target evidence. Stuart's
in-house PC source supplies architecture, names, field hypotheses, and expected
control flow, but it does not decide Steam behavior. The AYA exporter supplies
format hypotheses and asset tooling. The rebuild is an evidence consumer and
cannot validate the retail executable by agreeing with itself.

The current implementation remains an RE-informed original-code rebuild, not a
strict clean-room or parity-complete implementation.

## Scope

The design covers:

- a fresh, app-owned, unpatched safe copy of the canonical Steam executable;
- exact process, module, window, specimen, and launch-receipt identity;
- one exact player-one (runtime slot P0) Transform action routed to the copied
  process;
- module-relative execution probes for the selected call chain;
- private raw capture plus a sanitized, hash-bound public summary; and
- deterministic cleanup and source-integrity verification.

It does not initially measure or claim:

- transition duration or retail simulation time;
- energy, shield, velocity, grounded, stall, or fire-eligibility semantics;
- camera, FOV, animation, audio, effects, handling, or mission parity;
- an exact ABI for every observed function or field; or
- whole-binary semantic completeness.

## Known Static Targets

Runtime addresses must be computed from the live `BEA.exe` module base and the
RVA. Preferred absolute addresses are documentation only and must not be used
as runtime identity.

| Static identity | Preferred VA | RVA from `0x00400000` | Canary role |
| --- | ---: | ---: | --- |
| `CPlayer__ReceiveButtonAction` | `0x004d3110` | `0x000d3110` | Observe player one/runtime P0 receiving raw Transform action `0x21`. |
| `CBattleEngine__Morph` | `0x0040a580` | `0x0000a580` | Confirm the same BattleEngine receives the transform request. |
| `CBattleEngine__Move` | `0x004081c0` | `0x000081c0` | Confirm the same BattleEngine reaches its movement owner. |
| `CBattleEngineJetPart__Move` | `0x00410c50` | `0x00010c50` | Confirm the JetPart belongs to that BattleEngine. |

The static object relations used as canary hypotheses are player one's
(runtime P0) BattleEngine at `CPlayer + 0x1c`, BattleEngine state at `+0x260`,
JetPart at BattleEngine `+0x57c`, and the JetPart main-part backpointer at
`+0x18`. A runtime pass may confirm pointer equality and raw values; it must not
silently promote field names or enum labels beyond the accepted evidence.

## Architecture

### 1. Safe-Copy Materializer

Reuse `GameProfilePreflightService` with
`ApplyWindowedCompatibilityPatch=false` and an empty patch set. The source and
copied executable must both match the canonical 2,506,752-byte specimen with
SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
before launch. The copy must be app-owned, newly materialized, and neither a
hardlink nor a reparse-point escape.

The copied profile binds player one `Actions/Transform` (`0x21`) to Q through
the existing control-options service. No installed-game file or original
`BEA.exe` is written. The controlled launch uses
`-skipfmv -level 850 -configuration 2`, matching the strongest existing
Level 850 input-to-state evidence while filtering only the Transform action.

### 2. Launch And Identity Guard

Reuse the managed runtime service and process registry. A private launch
receipt binds:

- executable path, size, and SHA-256;
- process ID and process start time;
- working directory and copied-profile manifest;
- top-level window handle; and
- live `BEA.exe` module base, size, and path.

Every debugger and input action must match that receipt. PID alone is not
sufficient. A missing or ambiguous window, reused PID, module-path mismatch,
hash mismatch, or unexpected second process fails closed before input.

### 3. Code-Identity Preflight

Before arming a probe, compare short live code regions at each module-relative
RVA with the corresponding bytes in the verified copied executable. Resolve
file bytes through parsed PE section mappings, not by treating an RVA as a file
offset, and account for any relocation entries before comparison. The raw bytes
remain private. Public evidence may record only the RVA, comparison result, and
cryptographic digest.

A mismatch stops the run. It is not repaired, waived, or treated as a different
build of the same target.

### 4. Exact Input And One-Shot CDB Canary

Use exact-PID and exact-window foreground input. Do not use broadcast input,
background `PostMessage`, or synthetic mutation of game memory.

The canary sequence is:

1. launch a fresh Level 850 controlled profile and resolve player one/runtime
   P0;
2. arm a hardware execution probe for `CPlayer__ReceiveButtonAction`;
3. send one Q tap to the exact owned window;
4. accept the input event only when the player pointer is player one/runtime P0
   and the raw action is `0x21`;
5. derive the candidate BattleEngine pointer from that player object;
6. arm one-shot execution probes for Morph, BattleEngine Move, and JetPart Move;
7. require Morph and BattleEngine Move to receive that same BattleEngine;
8. require the JetPart backpointer to resolve to that same BattleEngine; and
9. record the normalized event order plus raw `BattleEngine + 0x260` values.

The probes are one-shot and pointer-gated. They must not log every frame. The
debugger stops perturb execution, so their timestamps cannot establish retail
timing.

### 5. Evidence Normalizer And Checker

Raw CDB output, addresses, PIDs, absolute paths, timestamps, and launch receipts
stay under an ignored local proof root. A deterministic materializer produces a
sanitized public-safe record containing:

- schema and tool versions;
- canonical specimen and command-template digests;
- module-relative RVAs and code-identity pass/fail results;
- normalized event names and order;
- pointer-equality booleans without pointer values;
- raw state dwords without semantic enum names;
- control/positive/repeat outcomes;
- before/after source and copy hashes; and
- cleanup results plus a digest binding the private raw capture.

The checker rejects missing stages, reordered events, identity mismatches,
unexpected writes, stale receipts, unbound raw evidence, failed cleanup, and
semantic claims outside the schema.

### 6. Cleanup Owner

A `finally` path releases every held key, detaches CDB, requests managed stop
only for the exact owned process identity, closes any owned process container,
and verifies that no owned BEA or CDB process remains. Unknown processes are
never terminated.

The installed source and copied executable are rehashed after the run. Any
source change is a hard failure. A copy change is also a hard failure because
this canary authorizes no executable or memory mutation.

## Stage Progression

### Stage A: Identity Canary

Run one bounded no-input control, one positive Q-transform canary, and one
positive repeat from a fresh copy and process. Acceptance proves only that the
owned player-one input causally reaches the expected
BattleEngine/Morph/Move/JetPart objects in the verified Steam specimen.

### Stage B: Controlled Raw-State Observation

Only after Stage A passes, add a separately tested exact-process read-only
sampler. It may query bounded raw state at a low rate without write access.
Retail simulation timing must first be identified independently; wall-clock
samples taken while CDB is stopping the process cannot define transform
duration.

Use at least one no-input control and three fresh positive runs before promoting
a raw transition sequence. Energy, shield, velocity, stall, grounded, and
eligibility fields remain separate hypotheses that require their own typed
correlation and controls.

### Stage C: Level 100 Corroboration

Repeat the accepted transform observation in the Level 100 tutorial. This stage
checks that the controlled result survives a recognizable mission context. It
does not use tutorial presentation or camera behavior to override the stronger
Level 850 causal evidence.

Only a public-safe behavior contract accepted after these stages may provide
measured constants, tolerances, and state rules to deterministic Core and the
Godot adapter.

## Runtime Authority

Before execution, the integration owner creates one ignored structured baton
that expires with this slice and names:

- action family: copied-runtime BattleEngine identity canary;
- allowed actions: unpatched AppCore safe-copy materialization, copied-profile
  control binding, managed launch/stop, exact-PID local CDB attach, read-only
  module/register/memory inspection, one-shot hardware execution probes,
  exact-window Q input, hashing, local materialization, and validation;
- forbidden actions: installed-game/original mutation, copied-executable or
  process-memory writes, remote debugging, broadcast/background input, unknown
  process termination, Ghidra mutation, raw-proof publication, and destructive
  proof cleanup;
- exclusive resources: `interactive-winui-desktop`, `bea-runtime`,
  `cdb-debugger`, and `local-proof-archive-write`;
- ignored proof-root policy, zero spend, validation gates, cleanup/rollback,
  and expiration.

The user's choice of this design authorizes preparation of that bounded baton;
the baton and leases, not historical proof plans, control the runtime action.

## Failure Handling And Stop Conditions

Stop before input when any specimen, module, process, path, start-time, window,
manifest, code-identity, lease, or authority check fails. Stop after cleanup
when an expected event is absent, ambiguous, or points to a different object.
Do not loosen a condition during the same run to obtain a pass.

An interrupted run is invalid evidence. Preserve its private diagnostics,
perform owned cleanup, then start from a fresh copy and process. User clicks or
keystrokes during the bounded input window invalidate that run even if the game
appears healthy.

## Validation And Acceptance

Implementation acceptance requires:

- focused tests for receipt identity, PID reuse, module-relative resolution,
  code comparison, event parsing, schema materialization, claim bounds, key-up
  cleanup, and owned-process cleanup;
- static checks proving no preferred absolute VA is used as a runtime address;
- a dry run that performs all preflight and cleanup without launching retail;
- the Stage A control, positive, and fresh-repeat matrix;
- before/after hashes for both source and copy;
- zero owned BEA/CDB processes after every terminal path;
- hard-payload, secret, docs, link, hygiene, and JSON gates; and
- normal/adversarial review of the implemented diff and sanitized result.

A green Stage A result increases runtime identity confidence for the selected
call chain. It does not increase gameplay, visual, handling, timing, or rebuild
parity confidence.

## User Interaction

The workflow is agent-operated. The user does not need to launch the game,
press Q, select a level, or close processes. During an announced native runtime
window, the user should leave mouse and keyboard input alone. If interference
is reported or detected, the run is discarded and repeated; it is not treated
as a mysterious product failure.
