# Rebuild determinism contract

Status: active — the contract a contributor breaks first
Last updated: 2026-09-19 (GDScript numerical and parsing foundations; existing behavior boundaries retained)
Evidence: SOURCE and bounded copied-runtime observation — constants and behaviors cited against
`references/Onslaught` (thing.h, eventmanager.cpp) and the tracked Core and
Headless sources named at the bottom; the retail 20 Hz step was MEASURED in
the 20 Hz migration evidence. Precision setup is static byte evidence; the
September 8 Plane control-word sample below is a separate runtime observation.
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
reduce its exponent range to float32. This bounded geometry model follows
device-creation intent. September 8 also measured PC24/RN at twenty-five
Plane/guide calls on the private WineD3D route described below; other sites
and rendering backends remain unmeasured.

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
rounding, cancellation, signed zero and retained exponent range. Those isolated
tests do not themselves sample the game or driver. These primitives are not yet
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

`RetailUnitEuler.Smooth` carries the finite PC24 angle update using retained
retail yaw/pitch/roll words. Nineteen cases match isolated execution of the
unchanged retail routine, including wrap boundaries, signed zero and subnormal
retained steps. `BuildBasis` follows its matrix arithmetic/store order using
managed double trig, matching thirty-one finite native outputs. General x87
transcendental equivalence and cross-host trig identity remain unestablished.
The Level100 mover now retains raw creation/Euler/drive/velocity state and
uses this update after Actor translation. Its living free-flight arithmetic
matched 32 consecutive copied-retail Moves across 352 grouped comparisons,
with observed guide inputs supplied explicitly. Move and clearance/avoidance
cadence use the existing scheduler with explicit PC24 routing arithmetic;
its mode, ordered pool and guide cache are included in schema 47. Aircraft
restore rejects the scheduler's legacy PC53 mode. Earlier formats remain
available for snapshots without this extension. Restoring raw Plane motion requires the matching guide and
event state; a millimeter pose cannot reconstruct them.

Spawned Planes additionally use schema 48 for the monitored spawning owner,
separate raw collision-ignore identity, attachment tag, exit selector/deadline
and explicit handoff to the existing normal-control approximation. Controller
listeners use negative actor IDs; existing positive Actor/Guide listener IDs
stay stable. Exit and pending Ready delivery restore without rerunning Init.
Omitting every exit record is rejected rather than silently selecting schema 47.
Scenes with no spawned Plane retain schema 47 bytes. The recorded 838-step
Headless fingerprint changed only because of the earlier exit-input definition
identity; its test compares every tick's canonical bytes after substituting
only the previous identity and recovers the previous complete trace.

The production script/weapon target bridge, missing avoidance candidate stream,
contact response, complete event/RNG order and effects remain partial. The
two unwritten native clearance-cache coordinates use the observed zero startup
allocation as an explicit deterministic seed. These boundaries preclude an
entire-trajectory or whole-game numerical parity claim.

A copied pristine game running through installed Proton Experimental Wine,
WineD3D and a private Xvfb display reached Level 100 with `-level 100`, without
desktop control. One constructor, twelve cache and twelve Plane Euler samples
read control word `0x007f`; the live constructor/Euler bodies matched pristine
bytes. The native oracle also reproduced eleven consecutive live Euler/basis
transitions. This is a bounded backend observation, not Steam-default, Windows,
cold-start acceptance or a whole-simulation precision claim. See the existing
[Unit function evidence](../reverse-engineering/binary-analysis/functions/CComplexThing.cpp.md).

## What Core may not do

The full GDScript migration preserves this boundary. Its deterministic modules
live under `OnslaughtRebuild.Godot/Core/` and use explicit preloads. They do not
become scene nodes or adopt Godot physics. Scalar arithmetic uses explicit
PC24 rounding, float32 stores and signed32 narrowing where the existing retail
contract requires them; built-in vector arithmetic is not a substitute.
Unsigned wide integers use exact base-32768 limbs. Invalid public inputs return
explicit failures in release builds, and mutation on failure follows the source
operation order. For example, a scaled RNG result overflow consumes its draw.

`npm run test:rebuild-gdscript` compares output bits, RNG state, wide-integer
results and binary bytes with the current C# reference and existing native
Euler fixtures. Raw signed-zero words are preserved explicitly: the initial
Godot 4.8 dev6 feasibility probe demonstrated that a compiled `-0.0` literal
could become positive zero and change the binary hash. These tests establish
the bounded numerical modules, not a complete GDScript simulation. A matching
C# result is regression evidence; retail contracts remain the parity authority.

`Core/strict_json.gd` preserves decimal lexemes and decoded UTF-16 units instead
of letting an engine dictionary discard duplicate members or round integers.
`Core/decimal_float64.gd` converts a validated decimal through an exact wide-
integer ratio and one nearest/even rounding, retaining signed zero, subnormals
and overflow. The pinned engine's `String.to_float()` changed 269 output words
in the initial varied-double/boundary comparison; the replacement passes the
unchanged C# words, plus exact normal/subnormal/overflow midpoint cases. The
strict parser checks grammar/depth and the tape's ordinal duplicate-name rule;
the future tape owner must still enforce its exact field set and schema.
JSON string tokens can retain an unpaired escaped surrogate until a caller
requests Unicode decoding, while duplicate-name admission validates each name
as the existing C# tape validator does. Embedded NUL uses raw units/bytes, since
native Godot string conversion would lose it. This is explicit representation,
not permission to normalize replay or save data.

The same exact-ratio converter now has a direct binary32 entry point.
`Core/invariant_number.gd` preserves the existing Int32/Single grammar,
trailing-NUL handling, signed zero, special values and invariant shortest
round-trip output. Decimal midpoint checks distinguish one binary32 rounding
from a binary64 intermediate. This helper does not apply locale-dependent
Godot formatting to authored particle values or options.

The resident chunk reader preserves short reads, partial live-size-word writes,
cursor/EOF ordering, unsigned accounting and signed32 narrowing. Its result
separates a retail short-read outcome from a terminal API failure; callers must
inspect both `ok` and `complete`. Synthetic managed-overflow and post-close
comparisons preserve existing C# behavior without claiming it as retail proof.

The GDScript event scheduler carries the same pool, ring, stable overflow order,
PC24/default clock paths and sparse snapshots. Synchronous callback results
require an explicit acknowledgement; a missing return or propagated failure
poisons the interrupted flush until reset. A handled nested-operation refusal
can be acknowledged, matching the C# caught-exception path. The differential
fixtures also retain typed-domain NaN and out-of-lane enum behavior, including
allocation/reuse mutation before an invalid ring index and the default mode's
valid alias at current buffer 48. These synthetic cases are current net8/Linux
regression boundaries, not evidence that retail gameplay generates those values.

The GDScript replay trace writer emits the unchanged schema-4 header, input
field widths and canonical-state length prefix. Trace serialization alone
admits the full managed field widths; gameplay still requires `SimInput`
validation by its owner. Failed entry construction leaves the current trace
unchanged. Repeated current-hash reads do not finish or reset a recording.

The GDScript command-tape codec preserves schema-v4 upgrade and schema-v5
serialization, field defaults, duplicate-member admission, exact canonical
JSON identity and reader cursor/failure ordering. Its record constructors
separate field-width admission from semantic validation, matching the existing
C# ownership. Nullable text remains nullable; embedded NUL and raw UTF-16 units
are retained until an explicit conversion. JSON encoding and BinaryWriter's
UTF-8 replacement rules remain distinct. The existing C# live runner still
owns full simulation/replay until that consumer is converted.

`sha256_stream.gd` implements the unkeyed digest operations in
[FIPS 180-4 sections 4–6](https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.180-4.pdf).
It stores eight words and a partial block, so obtaining the current digest
copies bounded state. The pinned engine's
[HashingContext API](https://github.com/godotengine/godot/blob/8898c2b3d/doc/classes/HashingContext.xml)
only exposes a consuming `finish`; retaining all prior snapshot bytes to
rehash them would change the recording's memory contract. Differential checks
compare chunked and non-consuming reads with .NET and the native Godot digest,
including padding boundaries and detached source/result buffers. This is
content-identity support, not cryptographic-module certification or a claim
that the complete simulation has been converted.

`Core/state_hasher.gd` now serializes the complete existing schemas 42–48 from
detached snapshot facts. It preserves signed and unsigned widths, raw float
words, BinaryWriter string behavior, schema selection and each collection's
source order. Sorts with equal keys retain encounter order explicitly: Godot's
unstable sort cannot substitute for LINQ's stable ordering. Missing nullable
fields are refused rather than treated as null. The same raw-plane/base-state
admission happens before emitting an accepted checksum. Synthetic envelopes
exercise the serializer; acceptance by a serializer does not prove a valid
simulation restore. Its focused C# comparison covers 55 snapshot envelopes,
including the unchanged 40-step `SimulationTests` fingerprint and all seven
schemas. The live C# runner remains the caller until its own port is validated.

The native career and frontend owners retain source mutation order, including
partial changes before rejected operations, one-shot load requests and nullable
UTF-16 names. Career-name editing works on code units, not Unicode code points;
the differential gate checks all 65,536 glyph inputs. The read-only career codec
accepts the same 10,004-byte/versioned container and validates links before
nodes. Ranking words and all reserved/unknown bytes remain exact. Its malformed
input probes start from the existing tracked save in memory and never emit saves.

`Client/platform_input_edges.gd` retains key echo handling, read-once edges,
joystick byte state and counter wrap. These are host input facts; they do not
claim a new retail DirectInput scan-code mapping. `Core/camera_laws.gd` preserves
the movie-zoom cache's numerical float equality and explicit float stores.
`Core/engine_viewpoint.gd` keeps two slots, copied current viewport state and
schema-1 hashes. Neither introduces a scene/input owner or uses the separately
preserved unfinished camera draft.

The live world now uses those native camera owners through `Client/world_camera.gd`.
Its temporary bridge sends previous/current facts together and samples/binds in
one operation per rendered frame. It transports float32 words and raw UTF-16
identities explicitly; it owns no second camera state. The frontend likewise
uses the native session/path owners, with cached display projections and original
career-selection ordinals across the temporary boundary.

`Core/control_response.gd` retains the exact look table, checked Int32 minimum
failure and raw-axis float32 stores. `simulation_constants.gd` retains all 200
numeric constants, eight positions and foot phases from the comparison source.
`mission_timing.gd` keeps repeated float32 fade subtraction, Int32 wrap, pause
rounding and known message timing limits. Sharing those values with HUD does
not turn Inspector edits into simulation configuration. New scheduler boundary
checks also consume committed original-code evidence; see [PARITY.md](PARITY.md)
for the unresolved live precision context. Matching a managed implementation
does not resolve that retail question.

`Client/render_interpolation.gd` keeps explicit float stores and the source
quaternion operation order. Its checked native `acos`/`sin` path is not
replaced with Godot's quaternion interpolation shortcut. Target projection,
projectile position, tangent/frame construction and retained trail tails
compare with the current Client. The Int32-maximum trail-tail case is
source-derived and bounded; the original multi-billion-iteration loop was
not executed. These presentation checks do not change the simulation owner.

The live Options adapter preserves synchronous side effects at their original
action points: a pre-adjustment audio failure prevents the later mutation, while
a post-commit settings failure retains the committed value. Reentrant actions
keep separate effect contexts. Actual Godot-hosted checks exercise these cases
and the exact frontend font/FEBack outputs. That process reports `.NET 10.0.12`
while the project target remains `net8.0`; the target is not the executed CLR.
The native FEBack cast preserves this host's saturating overflow and NaN-to-zero
Int64 conversion. The Sun uses an explicit NaN-to-zero Int32 coordinate shim
before its native terrain sampler. These are current-renderer compatibility
edges, not evidence of retail nonfinite inputs or a changed simulation contract.

The native particle reader preserves raw UTF-16 fields, first-name lookup and
duplicate field order. Its Latin-1 encoder preserves all 65,536 unit mappings,
including the 295 legacy best-fit substitutions and two fallback bytes for a
surrogate pair. Invariant lowercase preserves U+0130; the pinned Godot and
.NET scalar maps otherwise match across the complete nonsurrogate range.
Effect plans retain traversal order, cyclic-reference omissions, provisional
selector allocation and the existing 256-instance reconstruction bound.
An emitter whose lifetime is Int32 maximum returns `NonTerminatingInput`
instead of entering the old wrapping loop. This documented refusal affects
none of the 338 emitters in the three pinned inputs; all other finite
schedules retain their original traversal, including omissions after the cap.

`Core/terrain.gd` checks supplied HFLD bytes against the existing world pins,
preserves metadata words and signed samples, and exposes one sampler for scalar
and batch consumers. Fixed-point interpolation truncates after each axis;
AirGuide's unusual X-edge shift remains distinct from the regular lattice.
Ground and gradient conversion retain checked widths, signed floor division
and away-from-zero rounding. LOD complexity retains integer midpoint division
and binary32 stores. The module has no filesystem or scene owner.

`Scenes/World/height_field.gd` owns production renderer smoothing, tile selection,
stitching, the FNV64 signature and mesh generation. Its y/x traversal explicitly
transposes the sampler's x-major complexity batch on admission. All emitted
vertex, UV, UV2 and index words compare against the retained C# renderer;
lazy caching reuses immutable tile geometry without skipping camera updates or
changing LOD decisions. The existing ArrayMesh is mutated in place and survives
release of the renderer when a scene still owns it.

`Client/terrain_compositor.gd` admits the existing hierarchy hash before decoding
and retains Int32 overflow, signed byte weights and arithmetic shifts, UInt32
blend masks, the Sun+Ambient lighting gradient and reverse pine-shadow order.
Terrain vertex diffuse remains a separate Sun+AntiSun calculation with explicit
binary32 stores. It writes the same RGB565 bytes, including the old flat-array
aliases and partial writes on destination failure. Unsupported texture levels
are refused before a potentially enormous shifted allocation; valid levels stay
0 through 4. This is a bounded invalid-input refusal, not a changed LOD decision.

The shared presentation binary32 store uses a single-precision Vector3 component
on the pinned official engine, with the former packed-array store retained as a
fallback for double-precision engines. Exact checks cover signed zero,
subnormals, ties, overflow and NaN payloads. This removes a temporary allocation
at each arithmetic store without replacing explicit rounding with float64 math.
Water retains its ordered float32 phases and float remainder behavior, including
no advance for nonpositive or nonfinite frame deltas. Native camera updates stay
in the original world presentation order, after terrain appearance.

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
