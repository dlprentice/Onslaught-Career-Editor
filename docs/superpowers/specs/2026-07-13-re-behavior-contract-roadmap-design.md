# RE Behavior Contract Roadmap Design

Status: Chief-approved design with surgical stale-tooling correction
Date: 2026-07-13

## Goal

Turn accepted Steam-static findings and explicitly labeled Stuart-source
hypotheses into a prioritized, public-safe behavior-contract roadmap for the
RE-informed rebuild. The first slice must also provide one bounded
camera/movement/morph contract candidate that can guide First Flight without
promoting static evidence into measured retail behavior.

## Deliverables

The slice produces four integrated artifacts:

1. a roadmap ranking camera, movement/morph, controls, weapons, and
   mission-facing systems by player-visible First Flight value, evidence
   readiness, cost of the next decisive observation, and implementation risk;
2. an evidence-gap and stale-tooling closure plan that prefers simple bounded
   retail observations over another whole-binary pass or another morph-canary
   retry;
3. a versioned machine-readable camera/movement/morph contract candidate with
   a public explanation; and
4. a focused checker that validates the contract and forbids only the exact
   stale address/name/comment pairs proven superseded by the reviewed
   correction records.

## Evidence Model

Every material behavior row keeps these compartments separate:

- **Source hypothesis:** architecture, vocabulary, ordering, or ownership
  suggested by pinned Stuart source. It is never released-behavior authority.
- **Steam-static corroboration:** bounded ownership, call topology, data flow,
  or structure supported by the reviewed clean-Steam Ghidra evidence.
- **Copied-runtime measurement:** observed values or causal behavior from an
  authorized copied executable. A missing measurement remains explicitly
  missing.
- **Tolerances:** acceptance bands justified by measurement design. No numeric
  tolerance is invented from source or static constants.
- **Rebuild requirement:** what Core, Client, or a rendering adapter may consume
  after the contract reaches the required evidence state.
- **Nonclaims:** runtime, timing, handling, camera, presentation, gameplay,
  mission, animation, audio, parity, and completeness claims not established by
  the row.

The `6,411/6,411` result is metadata accounting only. The reviewed correction
wave is an input to this design, not whole-binary semantic or parity proof.

## Roadmap Ranking

The roadmap uses four priority bands:

- **P0 — First Flight control loop:** camera reference frame and follow
  response, directional movement response, grounded/airborne transition
  predicates, and morph request/result observables. These have the highest
  player-visible value and can be decomposed into simpler observations.
- **P1 — Input and weapon response:** held/edge action routing, weapon
  eligibility, projectile handoff, cooldown/charge observables, and mode-aware
  fire gating. Static anchors exist, but runtime causality and measured values
  remain separate.
- **P2 — Mission-facing progression:** objective/outcome transitions,
  flight-mode enablement, weapon availability, HUD messages, and scripted
  camera commands. Existing static command bridges make these good later
  contract consumers, but First Flight does not yet implement retail missions.
- **P3 — Presentation fidelity:** morph animation, camera shake, FOV, audio,
  effects, and asset-bound pose work. These are valuable but require separate
  presentation and asset evidence and must not block mechanical contracts.

Within each band, the roadmap ranks a bounded observation above a broad runtime
sampler, field sweep, or renewed whole-binary audit.

## Initial Contract Candidate

The candidate is a **camera-relative movement and morph-state observation
contract**, not a retail-constant contract. It connects three player-visible
questions:

1. Which frame defines forward/right movement input relative to the player and
   camera?
2. How do walker and jet movement paths respond to controlled input before,
   during, and after a transform request?
3. Which observable mode/state boundary may affect camera following without
   assuming a morph duration, animation, FOV, or source constant?

The candidate freezes only accepted static topology and an observation schema.
Its initial status is `candidate-static-runtime-required`. It cannot authorize
changes to retail-derived First Flight mechanics until copied-runtime evidence
fills the required measurement rows and an independent acceptance lane approves
the resulting tolerances.

The preferred next evidence is a sequence of independent, simpler copied-run
observations: camera reference-frame response, walker directional response,
jet directional response, then transform request/result correlation. The
three-role morph identity canary and Retry 13 remain off the critical path and
unauthorized.

## Surgical Stale-Tooling Closure

The current reviewed decisions explicitly classify both rows below as
`confirmed-apply`:

| Address | Forbidden stale owner | Accepted owner |
| --- | --- | --- |
| `0x00411630` | `CMonitor__IntegrateMovementAgainstTerrain` | `CBattleEngineJetPart__HandleGroundEffect` |
| `0x00411aa0` | `CMonitor__ComputeTerrainVelocityScalar` | `CBattleEngineJetPart__GetFriction` |

Closure is field- and address-scoped:

- mixed Java helpers keep unrelated accepted signature/comment operations;
- only exact stale target records for the two addresses are removed or made
  impossible to apply;
- historical read-only wave evidence remains tracked and is not rewritten into
  false present-tense authority;
- the regression reads the authoritative reviewed correction plan, confirms
  the two rows are `confirmed-apply`, and rejects active mutation source that
  pairs either address with its forbidden name or stale owner/caller comment;
- the regression also confirms unrelated accepted targets remain present in
  each mixed helper, preventing accidental broad retirement.

No package script is added or changed. The checker is invoked directly through
Python and may be proposed for package integration only by the owner of that
high-collision file.

## Files And Boundaries

Planned tracked changes are limited to:

- one roadmap/explanation under `roadmap/`;
- one versioned contract under `reverse-engineering/binary-analysis/`;
- one focused Python checker and its unit test under `tools/`;
- the two mixed Java apply helpers that contain the exact forbidden pairs; and
- this design plus the required implementation plan.

The slice does not edit `package.json`, `goal.md`, canonical state batons,
shared readiness/front-door documents, rebuild implementation, WinUI/AppCore,
runtime helpers, or proprietary/local payload paths. It performs no live
Ghidra, BEA, CDB, Godot, WinUI, or other native action.

## Validation And Acceptance

The first regression must fail against the current stale pairs before the Java
records change, then pass after the surgical edit. Focused acceptance includes:

- checker unit tests and direct contract validation;
- a forbidden-pair scan tied to the authoritative reviewed correction plan;
- proof that unrelated mixed-helper records remain;
- JSON parsing, `git diff --check`, current documentation command checks, and
  public-core link checks;
- hard-payload safety because the slice consumes RE evidence; and
- one normal and one adversarial Codex review plus sanitized normal and
  adversarial Cursor/Grok consults under one review envelope.

The worker reports recommended canonical state deltas to integration but does
not write canonical state. Commit and push occur only after the bounded slice
is green and review findings are resolved.
