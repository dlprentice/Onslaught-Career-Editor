# BattleEngine Target-Acquisition Static Contract v1

Status: **accepted static contract; not runtime proof**

Schema: `battleengine-target-acquisition-static-contract.v1`

Slice: `M2.3-target-acquisition-static-contract`

This contract consolidates the player BattleEngine lock-acquisition path. It
uses pinned Onslaught commit
`5352a81cdb838b145a57f7febc5d9fc4b0129ebb` for source vocabulary while keeping
Steam-static evidence authoritative for the retail addresses and structure.

## Evidence classes

- `reviewed-retail-static`: accepted current identity or structure from the
  reviewed 2026-07-13 correction closeout.
- `saved-retail-structure`: address-bound structure whose saved semantic name
  is descriptive or dependent and not accepted as exact source identity.
- `pinned-source-hypothesis`: source vocabulary or behavior that still requires
  retail proof.
- `runtime-required`: causality, values, or gameplay semantics not established
  by static evidence.

## Address anchors

| Address | Current retail name | Source alignment | Boundary |
| --- | --- | --- | --- |
| `0x00406560` | `CBattleEngine__HandleLocks` | `CBattleEngine::HandleLocks` | Reviewed source-aligned retail-static identity. The old `CBattleEngine__UpdateAutoTargetSetAndFireProjectiles` interpretation is superseded. |
| `0x00406da0` | `CBattleEngine__SelectNearestForwardTargetFromGlobalSet` | `CBattleEngine::GetClosestLockableUnit` | Saved descriptive retail name; source name remains `hypothesis-only`. |
| `0x00406fc0` | `CBattleEngine__AddProjectile` | `CBattleEngine::StartLock` | Saved dependent name with superseded projectile semantics; exact source identity remains `hypothesis-only`. |

## Lock-path rows

1. `move-calls-handle-locks` — The sole reviewed caller is
   CBattleEngine__Move, which enters 0x00406560 with the BattleEngine pointer
   and no explicit stack arguments.
2. `active-part-weapon-selection` — The helper selects the current JetPart or
   WalkerPart weapon from the BattleEngine state before maintaining or
   acquiring locks.
3. `existing-lock-pruning` — The helper removes null, dying, or
   out-of-deflection entries from the tracked lock set at BattleEngine +0x294.
4. `maximum-lock-and-readiness-gates` — New acquisition is bounded by
   current-weapon fire readiness and maximum-lock gates; numeric thresholds and
   runtime timing remain unproven.
5. `direct-proximity-sequence-modes` — The body contains distinct direct,
   proximity, and sequence lock-mode paths without establishing their live
   selection or gameplay outcomes.
6. `lock-entry-creation-call-shape` — Four calls from HandleLocks pass a target,
   lock-time value, and direct-lock flag to 0x00406fc0; this is lock-entry
   creation structure, not projectile emission proof.

## Candidate-filter order

The saved `0x00406da0` body preserves this bounded structural order:

1. `global-candidate-set-traversal` — 0x00406da0 traverses the global candidate
   set rooted at DAT_008550d0.
2. `side-compatibility-gate` — Each candidate first passes an address-bound
   side/team compatibility helper.
3. `weapon-profile-eligibility-gate` — The candidate then passes the saved
   weapon/profile target-mask eligibility helper.
4. `distance-and-nearest-so-far-gate` — Squared distance from the
   caller-supplied origin is checked against a scaled range and the current
   nearest-so-far value.
5. `forward-deflection-gate` — A BattleEngine-relative normalized direction is
   compared with a cosine-derived deflection threshold.
6. `existing-lock-exclusion` — The candidate is excluded when it already
   appears in the tracked set at BattleEngine +0x294.
7. `candidate-return-or-null` — The helper returns the best retained candidate
   pointer or null when none survives.

These rows do not assert the exact C++ types or final semantic names of every
helper and field.

## Source hypotheses retained, not promoted

- `stealth-adjusted-effective-lock-range`
- `helper-00406da0-is-get-closest-lockable-unit`
- `helper-00406fc0-is-start-lock`

The source hypothesis is useful because its filter and call ordering closely
matches the saved retail bodies. It still does not turn a source expression or
method name into observed retail behavior.

## Accepted static claims

- the reviewed retail-static identity and bounded lock-maintenance phases of CBattleEngine__HandleLocks at 0x00406560
- the address-bound candidate-filter ordering retained by the saved 0x00406da0 helper body
- the target, lock-time, and direct-lock call shape of the saved 0x00406fc0 dependent helper

## Claim boundary

This contract establishes a bounded address-based static lock-maintenance and
candidate-filter map. It does not prove:

- `runtime target choice`
- `lock timing`
- `Core behavior`
- `exact helper source identity`
- `the retail semantic meaning of the source stealth expression`
- `projectile emission or weapon firing`
- `exact object or field layouts`
- `gameplay outcomes`
- `visual behavior`
- `rebuild parity`

No BEA launch, debugger attachment, Ghidra mutation, executable patching,
runtime observation, Core implementation, Godot implementation, visual proof,
or release action occurred.
