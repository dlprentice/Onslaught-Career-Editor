# RE Behavior-Contract Roadmap — 2026-07-13

Status: prioritized public-safe roadmap; runtime observations remain separately authorized work

## Decision

Prioritize the smallest player-visible observations that can replace synthetic First Flight behavior safely. The current static review identifies useful owners and topology, but it does not establish camera reference frames, movement response, morph outcomes, values, tolerances, or causality. The `6411/6411` audit is metadata closure, not semantic parity.

The first candidate is [First Flight camera, movement, and morph contract](../reverse-engineering/binary-analysis/first-flight-camera-movement-morph-contract-candidate.v1.json). Its status is `candidate-static-runtime-required`; it authorizes no rebuild change.

## Priority

| Priority | Cluster | Player-visible value | Evidence readiness | Cheapest decisive next evidence | Main risk |
| --- | --- | --- | --- | --- | --- |
| P0 | Camera, movement, morph | Directly improves whether First Flight feels controllable and coherent. | Camera and movement owners have bounded static anchors; behavior and values are unmeasured. | Matched copied-runtime observations in this order: camera reference frame, walker direction, jet direction, then morph request/result correlation. | Freezing source or rebuild assumptions as retail behavior. |
| P1 | Controls, weapons | Makes input discoverable and combat feedback meaningful. | Candidate action routing and weapon/physics topology exist; exact input-to-effect causality is incomplete. | One action at a time: bind, deliver to the verified copied process, observe the intended player and one bounded weapon effect. | Confusing configured bindings, receipt delivery, and gameplay acceptance. |
| P2 | Mission-facing systems | Enables tutorial objectives and scripted progression to respond credibly. | Static command/effect candidates exist for flight mode, weapon availability, objectives, and camera pan. | Observe one low-ambiguity mission command and its externally visible state change before composing mission sequences. | Attributing encounter or tutorial state to the wrong command or actor. |
| P3 | Presentation | Improves polish after simulation-facing contracts are stable. | Static and asset references can suggest animation, audio, and effects, but the active exporter is not animation-complete. | Bounded visual/audio observations tied to already accepted state transitions. | Presentation evidence being mistaken for deterministic simulation truth or asset completeness. |

## P0 Executable Observation Order

1. `camera_reference_frame`: hold the same single input from two separated camera headings and compare normalized camera axes with actor displacement.
2. `walker_directional_response`: measure one directional response from a stable walker state without a morph request.
3. `jet_directional_response`: repeat for a stable jet state, separating ordinary flight from near-ground observations.
4. `morph_request_result_correlation`: only after the single-mode observations, correlate one transform request with success or rejection and the later movement mode.

This ordering reduces attribution ambiguity before any multi-event canary. The previous three-role morph canary is off the critical path. Retry 13 is not authorized; any later morph observation requires a new bounded design and explicit runtime authority.

## Evidence Compartments

Every accepted contract must keep these fields separate:

- `sourceHypothesis`: architecture, names, and expected control flow from the pinned Stuart source; never Steam behavior authority.
- `steamStaticCorroboration`: bounded released-code identity, ownership, and topology supported by reviewed static evidence.
- `copiedRuntimeMeasurement`: controlled, identity-bound observation of a copied executable; required for values, player-visible outcomes, timing, and causality.
- `tolerances`: acceptance envelopes derived from repeat measurements, never guessed from source or rebuild output.
- `rebuildRequirement`: the behavior an implementation must satisfy after the preceding evidence is accepted.
- `nonclaims`: nearby conclusions the evidence does not support.

The rebuild is an evidence consumer. Agreement with its current synthetic behavior cannot corroborate retail truth.

## Evidence Gaps

- Camera: the reference frame connecting view direction, input intent, and actor displacement is not measured; FOV, sensitivity, inversion, smoothing, and timing are also open.
- Walker: response direction, latency, acceleration, speed, turn behavior, terrain interaction, and walk-cycle presentation are open.
- Jet: response direction, latency, acceleration, speed, altitude effects, energy, stall, ground effect, and friction magnitudes are open.
- Morph: request success/rejection, transition timing, state labels, cost, cooldown, and effects on movement, shields, weapons, and missions are open.
- Controls: candidate action identities do not yet prove configured binding, exact player delivery, or gameplay acceptance.
- Weapons: static weapon/physics topology does not prove trigger gating, cadence, projectile behavior, damage, or feedback.
- Missions: static command-effect candidates do not prove runtime command dispatch, target identity, ordering, or visible outcome.

## Stale-Tooling Closure

The reviewed correction plan explicitly supersedes exactly two active address/name/comment pairs:

- `0x00411630` / `CMonitor__IntegrateMovementAgainstTerrain` → `CBattleEngineJetPart__HandleGroundEffect`
- `0x00411aa0` / `CMonitor__ComputeTerrainVelocityScalar` → `CBattleEngineJetPart__GetFriction`

Those exact stale records are removed from the two mixed Java apply helpers. Unrelated accepted operation records remain in both helpers, and historical read-only evidence remains intact. The focused guard binds the closure to one authoritative `confirmed-apply` row per address, rejects reintroduction of either forbidden pair/comment, and verifies the complete expected address/name operation inventory in each mixed helper. This is a syntactic regression guard; review of the bounded Java diff establishes that no control flow changed in this closure:

```powershell
py -3 -m unittest tools.re_behavior_contract_guard_test -v
py -3 tools/re_behavior_contract_guard.py --check
```

This is a surgical closure, not a broad invalidation of the helpers or the historical audit.

## Acceptance Boundary

Promote a candidate row only after its copied-runtime observation is accepted, repeat-derived tolerances are recorded, rebuild requirements are explicit, and nonclaims remain intact. Until then, static discoveries may improve observation design and naming but must not change player-visible rebuild behavior.

No live Ghidra, debugger, game, or native-client result was used or accepted as evidence for this roadmap. No installed-game file or original executable was mutated.
