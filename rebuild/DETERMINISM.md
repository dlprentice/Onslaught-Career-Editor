# Rebuild determinism contract

Status: active — the contract a contributor breaks first
Last updated: 2026-09-08
Evidence: SOURCE — constants and behaviors cited against
`references/Onslaught` (thing.h, eventmanager.cpp) and the tracked Core and
Headless sources named at the bottom; the retail 20 Hz step was MEASURED in
the 20 Hz migration evidence. Precision setup below is direct static byte evidence.
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
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

## Retail geometry precision

The mesh-pose and passive sphere/bounds primitives use 24-significand-bit,
round-to-nearest-even operations with explicit float32 stores. `RetailFloat24`
retains a double carrier between operations: x87 precision control does not
reduce its exponent range to float32. This bounded geometry model is based on
device-creation intent; the live gameplay control word remains unmeasured.

Fresh September 8 inspection of pristine `BEA.exe.original.backup`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, found:

- Startup requests 53-bit precision through `0x00560cb1`, without changing
  rounding control. `[0x00560cb1,0x00560cc3)` hashes to
  `38dcf78aa3dab9d5e661a8e7fbaabcbab0399decb645b9d088bed196a65eef42`;
  the control-word mapper `[0x00569449,0x005695af)` hashes to
  `da7de6a1ae9b07904d40360b02191a2cdc51ff80da00eaabf02926bbc1ac8820`.
- The retail import is `d3d9.dll!Direct3DCreate9`. Enumerated device flags are
  `0x50`, `0x40`, `0x80` or `0x20`; device creation optionally adds `0x100`.
  The call at `0x0052b2d6` omits FPU preservation. Enumeration
  `[0x00529350,0x0052a6f2)` hashes to
  `a8374027bde940888504ac4b3a1a1a701baacc01629cbbce08ab83d560d3a8dc`;
  call setup `[0x0052b296,0x0052b2dd)` hashes to
  `5d1e6f9214f99860e35ec513fb9ba5dbdcb5a9907832448db1c4ff05341c3685`.
  Microsoft documents single-precision/RN initialization when preservation is
  omitted ([D3DCREATE](https://learn.microsoft.com/en-us/windows/win32/direct3d9/d3dcreate)).

Pinned `d3dapp.cpp:337–341` enables preservation only for `_DEBUG`, but that
source drop uses Direct3D 8; it does not establish the retail API or runtime.
Startup precision alone therefore cannot justify 53-bit gameplay arithmetic.
The focused Core tests and a separate native x87 PC24 probe distinguish root
rounding, cancellation, signed zero and retained exponent range. They do not
sample the game, driver or Proton control word. These primitives are not yet
connected to the spatial explosion scan; no whole-simulation precision claim
or replay fingerprint change follows from this correction.

Retail vectors map to Core as `Q(x,y,z) = (x,-z,y)`, apart from the position
datum. Both the materializer and raw Actor pose projection therefore convert
orientation by `Q * B * inverse(Q)`. The unsigned Y/Z swap was incorrect for
pitch and roll. Direct selection and sign-bit changes preserve signed zeros;
Core hashes those words, so even yaw-only definition identities change after
this correction. The quarter-turn offset and renderer checks in
`ThingActorBaseStateTests` and the materializer's `Level100FloatGeometryTests`
test coordinate consistency, not live retail Euler arithmetic or flight parity.

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

The headless runner (`OnslaughtRebuild.Headless`) reads and replays supplied
command tapes. `InteractiveSession` supplies the consumed input and resulting
snapshot to `CommandTapeRecorder`; `BuildObserved` freezes hashes measured during
that session without replaying it. The native Godot host writes a new tape at
exit when `--record-tape=/absolute/path.json` is set. A mostly idle native session
replayed twice on September 6; a substantial player walkthrough remains open in
`PROGRAM.md` P8. See [`README.md`](README.md) for recording commands.

- `MaximumTapeBytes = 8 MiB`
- `MaximumReplaySteps = 100 000`
- A replay runs twice by default (`--repeat` can select another count); each
  additional run must reproduce the first run's hash,
  or the run fails with "Determinism failure: repeated replay produced
  different hashes."
- `--expect <hash>` requires the replay trace hash to equal the expected
  value exactly. It does not suppress an embedded `expectedFinalStateHash`;
  both must match when the tape contains that value.

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
