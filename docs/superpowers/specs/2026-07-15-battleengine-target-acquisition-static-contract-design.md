# BattleEngine Target-Acquisition Static Contract Design

Status: implemented slice design; static evidence only

## Goal

Consolidate the current player BattleEngine lock-acquisition path into one
public-safe machine-readable contract. The contract must distinguish reviewed
Steam-static identity from saved-symbol structural evidence and pinned-source
hypotheses. It must reject the superseded interpretation of `0x00406560` as a
projectile helper and must not authorize runtime or rebuild behavior.

## Scope decision

The slice covers only the BattleEngine lock path rooted at
`CBattleEngine__HandleLocks`. It does not absorb the broader Unit/AI active-reader,
crosshair, auto-aim, squad-scoring, projectile, damage, or collision systems.

Three approaches were considered:

1. A broad targeting contract spanning player locks and Unit/AI readers. This
   would mix independently evidenced systems and create false closure.
2. A bounded player lock-acquisition contract. This is selected because the
   reviewed correction and saved helper bodies form a coherent static chain.
3. Documentation-only stale-name cleanup. This would not provide the requested
   machine-readable regression boundary.

## Evidence tiers

- `reviewed-retail-static`: accepted current Steam-static identity or structure
  from the 2026-07-13 correction closeout.
- `saved-retail-structure`: address-bound traversal, call shape, predicate, or
  ordering evidence whose saved semantic name is not independently accepted.
- `pinned-source-hypothesis`: vocabulary or behavior suggested by pinned
  Onslaught commit `5352a81cdb838b145a57f7febc5d9fc4b0129ebb`.
- `runtime-required`: behavior, numeric meaning, causality, or gameplay outcome
  that static evidence cannot establish.

## Contract anchors

- `0x00406560`: reviewed `CBattleEngine__HandleLocks` identity.
- `0x00406da0`: saved descriptive helper
  `CBattleEngine__SelectNearestForwardTargetFromGlobalSet`; source candidate
  `CBattleEngine::GetClosestLockableUnit` remains a hypothesis.
- `0x00406fc0`: saved dependent name `CBattleEngine__AddProjectile`; current
  static call shape is lock-entry creation and source candidate
  `CBattleEngine::StartLock`, without accepting exact source identity.

## Accepted static sequence

The checker fixes the retail-structure sequence to candidate-set traversal,
side compatibility, weapon/profile eligibility, distance and nearest-so-far
gates, forward-deflection gate, existing-lock exclusion, and candidate return.
The source-only stealth interpretation remains separate from the retail-static
predicate wording.

## Harness

A Python contract checker and focused unit suite validate schema closure,
canonical anchors and order, exact evidence-tier vocabulary, evidence paths,
false runtime/rebuild guards, exact v1 claim text, Markdown coverage, and the
reviewed correction record. The standalone contract checker can report an
absent source body without failing the retail-static contract; the named
combined gate requires the initialized source submodule, its exact Git revision,
and `BattleEngine.cpp` read from the committed object rather than the working
tree. Compatibility checks are updated so the old projectile interpretation
cannot pass merely because it remains in current authority prose.

This slice has no visual output or subjective presentation state. A screenshot
harness would add no evidence; the unattended acceptance surface is the
machine-readable static contract and its fail-closed regression suite.

## Non-claims

No BEA launch, debugger attachment, live memory read, input, Ghidra mutation,
executable patch, target-choice causality, lock timing, exact field layout,
Core implementation, Godot behavior, visual proof, gameplay parity, or release
is part of this slice.
