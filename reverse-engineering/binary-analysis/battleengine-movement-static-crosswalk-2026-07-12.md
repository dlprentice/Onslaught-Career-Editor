# BattleEngine Movement Static Crosswalk - 2026-07-12

Status: high-confidence static owner/source mapping; runtime behavior and live Ghidra mutation remain pending

## Scope

This pass re-reviewed the BattleEngine movement/morph call chain against:

- the canonical clean Steam `BEA.exe` specimen, SHA-256
  `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`;
- read-only Ghidra 12.0.3 exports from a verified project backup;
- RTTI, vtable slots, callers, constructors, object offsets, and adjacent bodies;
- pinned Stuart source at
  `5352a81cdb838b145a57f7febc5d9fc4b0129ebb`; and
- the current synthetic rebuild implementation.

The Ghidra project was opened read-only. No saved name, signature, comment,
function boundary, executable byte, installed-game file, or original
`BEA.exe` was changed.

## Confidence Rubric

Each mapping is evaluated separately for owner/name, prototype/type, static
semantics, source provenance, and copied-runtime behavior. A clean comment or
signature is not semantic proof, and a source match is not runtime proof.

| Grade | Meaning |
| --- | --- |
| High static | Independent binary structure plus source-order/body agreement converge on the same identity. |
| Provisional | A useful candidate exists, but owner, exact method, or ABI evidence is incomplete. |
| Runtime pending | No accepted copied-runtime observation measures the behavior or constants. |

For the current slice, each evidence dimension is scored from 0 to 4:

- `0`: no accepted evidence;
- `1`: candidate or contextual clue;
- `2`: direct evidence with a material unresolved ambiguity;
- `3`: independent static signals converge, with runtime or final typing open;
- `4`: identity/provenance is directly anchored and independently
  triangulated at the stated evidence layer.

These are dimension scores, not a whole-binary completion percentage.

| Cluster | Owner/name | Prototype/type | Static semantics | Source provenance | Copied runtime |
| --- | ---: | ---: | ---: | ---: | ---: |
| `0x004081c0 CBattleEngine__Move` | 4 | 2 | 3 | 4 | 0 |
| `0x00410c50 CBattleEngineJetPart__Move` | 4 | 2 | 3 | 4 | 0 |
| `0x00411630` / `0x00411aa0` / `0x00411b70` / `0x00412900` helpers | 4 | 2 | 3 | 4 | 0 |
| `0x00412ad0` unresolved helper | 1 | 1 | 1 | 1 | 0 |

## Corrected Static Map

| Address | Prior saved name | Current static identity | Evidence | Confidence |
| --- | --- | --- | --- | --- |
| `0x004081c0` | `CMonitor__Process` | `CBattleEngine__Move` | `CBattleEngine` RTTI resolves the vtable at `0x005d89c4`; slot 66 at `0x005d8acc` points to this body. The same table contains known BattleEngine methods. The body reads BattleEngine state `+0x260`, WalkerPart `+0x578`, and JetPart `+0x57c`, dispatches both part movement paths, and reaches BattleEngine morph/aim/effect work plus the actor move base. | High static; prototype refinement and runtime pending |
| `0x00410c50` | `CMonitor__UpdateMovementTransitionAndEffects` | `CBattleEngineJetPart__Move` | Its sole checked call is from `CBattleEngine__Move` using the object at BattleEngine `+0x57c`. `CBattleEngine__Init` constructs the JetPart into that field, and the JetPart constructor stores the main BattleEngine backpointer at `+0x18`. Body order matches the source movement routine across emitter updates, energy cost, engine state, stall/morph, ground effect, flight velocity, auto-return, shield clearing, effects, and skimming. | High static; ABI labels and runtime values pending |
| `0x00411630` | `CMonitor__IntegrateMovementAgainstTerrain` | `CBattleEngineJetPart__HandleGroundEffect` | Called from JetPart Move; terrain/water height, near-ground acceleration, orientation response, and main-part backpointer usage match the source helper. | High static; runtime pending |
| `0x00411aa0` | `CMonitor__ComputeTerrainVelocityScalar` | `CBattleEngineJetPart__GetFriction` | Called from JetPart Move and returns the source-compatible terrain/velocity-gated friction scalar. | High static; runtime pending |
| `0x00411b70` | `CBattleEngineJetPart__IsStateMachineActive` | `CBattleEngineJetPart__GetIsDoingSpecialAirMove` | Returns true when the JetPart loop field or barrel-count field is active, exactly matching the source predicate. | High static; runtime pending |
| `0x00412900` | `CMonitor__CanUseTrackingUpdate` | `CBattleEngineJetPart__AutoLevel` | Uses the JetPart main-part pointer, on-ground and velocity virtuals, main-part energy, and local barrel-count field in the same decision sequence as source. | High static; caller name/prototype cleanup and runtime pending |
| `0x00412ad0` | `CMonitor__UpdateSurfaceAlignmentAngle` | unresolved helper before WalkerPart construction | The body is reached from WalkerPart movement context, but this pass did not establish an exact source method or owner strongly enough to rename it. | Provisional; keep unresolved |

`0x00411a60 Vec3__Cross` remains a shared math helper and is not reassigned to
JetPart ownership.

## Cross-Lane State

| Evidence layer | Current result | Authority boundary |
| --- | --- | --- |
| Stuart source | Names the BattleEngine/JetPart owners and candidate movement sequence. | Architecture and hypothesis only. |
| Steam static | Establishes the owner/method cluster above at high static confidence. | Does not measure runtime values or outcomes. |
| Steam copied runtime | No accepted morph/movement timeline for this slice yet. | Required before behavior constants are frozen. |
| AYA exporter/assets | Static model/texture export exists, but the pinned exporter does not preserve multipart animation or bones. | Sufficient for static stand-ins; insufficient for an authentic animated transform claim. |
| Rebuild | Core exposes mode, energy, shield, velocity, input, and deterministic tick state, but current values and transition behavior are synthetic. | Must consume a later accepted contract rather than source constants directly. |

The initial rebuild-facing observation fields are: mode/state, transform request
and rejection, transition start/end, energy, shield, velocity, grounded state,
stall state/start, movement eligibility, fire eligibility, and event timestamps.
Camera, FOV, animation frames, audio, and presentation remain separate lanes.

## Superseded Interpretations

- The Monitor owner/name at `0x004081c0` is wrong.
- The Monitor owner/name at `0x00410c50` and its selected child helpers is
  wrong.
- The May 7 jet energy/stall report used the broad BattleEngine Move body at
  `0x004081c0` as if it were the JetPart movement method. Its specific
  `+0x280` subtraction and counter interpretation is withdrawn. The actual
  static JetPart movement bridge is `0x00410c50`.
- Historical wave reports remain useful records of what was believed and
  changed at the time, but current docs must point through this correction.

## Meaning Of Previous Closure Metrics

The `6411/6411` Ghidra function-quality closure measured whether every current
function object had comment/signature metadata satisfying the export contract.
It did not prove all owners, method identities, layouts, or semantics. This
re-review found important semantic owner errors while that metric remained
green. Future quality reporting must keep metadata closure separate from
semantic confidence.

## Rebuild Consequence

The current First Flight rebuild uses synthetic instant mode switching, energy
cost/drain, shield behavior, and movement values. This crosswalk is enough to
choose the authentic subsystem and its observable fields, but not enough to
replace those values responsibly. The next evidence step is a copied-runtime
morph/movement observer that records successful and rejected transforms,
walker/jet return paths, state, energy, shield, velocity, and event timing.

Only after that observation is accepted should a public behavior contract set
constants, tolerances, and deterministic Core behavior. No gameplay, visual,
camera, handling, mission, animation, audio, or whole-game parity is claimed
here.
