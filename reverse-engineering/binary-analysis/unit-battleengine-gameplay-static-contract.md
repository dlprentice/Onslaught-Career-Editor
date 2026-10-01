# Unit / BattleEngine / gameplay static contract

Status: bounded retail static map; not runtime gameplay proof
Last updated: 2026-10-01 (dropship threshold and dive-bomber bank-sign arithmetic corrected)
Summary: retained gameplay routing plus specimen-bound aircraft arithmetic, provider, debris and squad-registration findings.
Evidence: MEASURED — October 1 whole-section/relocation match, bounded original-code arithmetic and squad instruction reads; the retained map sections keep their July 16 evidence limits.
Specimen: pristine `BEA.exe.original.backup`, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

This contract routes the retained Unit/BattleEngine evidence without repeating
the retired wave ledger. Function-level notes under [`functions/`](functions/)
remain the detailed evidence owners.

## Dropship landing-turn threshold — October 1

Move (`0x00447120`) compares its wrapped yaw difference against
`double(0.1f)`, approximately `0.10000000149011612`, stored at `0x005d8c38`.
The reconstructed double literal `0.1` was different. Correcting it to `0.1f`
preserves the compiled instruction sections of all 45 callables; only the
threshold reference at Move section offset `+0x51a` changes. All 44 other
callable graphs, 36 existing exact results and six vtables remain unchanged.

The lead freshly compiled both forms, independently read the constant, and
executed the original and candidate 111-byte fragments
`[0x004475dc,0x0044764b)`. These load the float32 headings, wrap their difference
and select the threshold branch. Seven constant references are bound to their
retail counterparts; only the old threshold payload differs. Among 87 authored
finite cases across PC24/53/64 nearest-rounding modes, the old form differs
from retail in twelve decisions: six each at PC53 and PC64, none at PC24.
The correction agrees in every admitted case. Inverting the branch reverses
all 87 decisions; register, stack and x87 guards also pass.

For example, at PC53 nearest, yaw `0.10000000149011612` and target
`4.656612873077393e-10` take the callback-side branch in retail and the
correction, but not the former source. The callback itself is not executed.
The fragments omit preceding Move branches, callbacks, the later speed block
and world state. Neither these inputs nor PC53/64 are measurements of live
game state. The full function remains unmatched, including the speed-sum
association and Z-square lifetime. The next falsifier is a full-function
comparison with admitted dependencies and separately observed live precision;
fragment agreement does not establish either.

Private root receipts under
`bea-decomp/.worktrees/codex-equiv-20260930/local-data/geometry-gate-resume-20261001/`:
`dropship-threshold-root/readback.json` and
`dropship-threshold-root/native-root-v1/receipt.json`.

## Dive-bomber bank sign — October 1

The guide at `0x00446840` chooses the bank sign from a dot product. Retail's
`[0x00446b64,0x00446b93)` fragment accumulates component products as `(Z+Y)+X`;
the former reconstruction used `(Y+X)+Z`. Cancellation can change the sign.
Binding the earlier destination height by const reference recovers the retail
operand order without a shared-header or compiler change.

The lead freshly compiled both versions and executed the original and candidate
47-byte fragments in 336 authored finite states. Before correction, 37 PC24,
21 PC53 and nine PC64 cases select the opposite sign. The corrected fragment
is byte-identical after its zero-constant relocation is independently bound,
and all admitted outputs agree. Reversing the branch flips every sign while
preserving the surviving heading; register, stack and x87 guards pass.

This experiment admits a clamped bank magnitude of `0.5`, finite orientation
and destination vectors, and explicit round-to-nearest control words. It does
not run the preceding callbacks, atan2/clamping, world queries or full update,
nor establish live reachability or the game's active control word. The full
guide remains unmatched. Nineteen other callable graphs, all 41 guide reference
identities and thirteen exact controls survive. Private root evidence under
`bea-decomp/.worktrees/codex-equiv-20260930/local-data/geometry-gate-resume-20261001/`:
`dive-bank-root/readback.json` and `dive-bank-root/native-bank/receipt.json`.

## Unit provider selection — October 1

Reconstructed `0x004fb840` matches its complete 1,104-byte section, 1,099-byte
body and all 27 relocations. Source-local spawner accessors and the selection
block after the active-weapon guard recover the initial iterator's stack
lifetime; the later outer iterator reuses that storage. Selection phases and
scoring remain in retail order. These source groupings are reconstructed,
not recovered original helper names.

The lead freshly compiled and bound every reference, preserving all 240 other
callable graphs across Unit and UnitAI and all nine vtables. The extra emitted
iterator was already globally exact. This settles the compiled method, not
live targeting or full Unit behavior. Other Unit/UnitAI misses remain open.
Private root `unit-provider-root/final-readback.json` under the owner below
contains the independent readback.

## Mech debris arithmetic — October 1

Retail's debris-velocity fragment `[0x004a000c,0x004a0059)` keeps the scaled Z
product on x87 until doubling and bias subtraction finish. The former vector
expression rounded that product to float first. Calling the existing vector
setter with the scaled components recovers the original materialization order.

The lead executed the original fragment and freshly compiled correction in
9,216 bounded integer/precision/rounding cases. The old version differs in
2,184 Z results; the correction agrees in XYZ and x87 status in all admitted
cases. A control inserting only the intermediate float store/reload reproduces
the former XYZ results. With all integer components `-99` and PC53 nearest,
the old Z bits are `bdd0a3d6`, versus retail/corrected `bdd0a3d7`.

The full `0x0049fdb0` function remains unmatched. PRNG calls, all combinations
of inputs, live control-word reachability and world effects were not exercised.
All nineteen exact controls and twenty other callable graphs survive. Private
root receipts are `mech-root-static-readback.json` and
`mech-velocity-root-native/receipt.json`, under
`bea-decomp/.worktrees/codex-equiv-20260930/local-data/geometry-gate-resume-20261001/`.

## Squad registration order — October 1

The lead freshly decoded squad initialization at `0x004e5e70`, the called
`Append` at `0x004e5b20`, and the different `Add` at `0x004e5a80`.

After the base initialization call at `0x004e61b4` and copying the position
snapshot, retail passes the squad pointer, sets ECX to `0x008550a0` at
`0x004e61d7`, and calls `Append` at `0x004e61dc`. This is the world's squad
registry, represented by `WORLD.GetSquadNB()` in the reconstructed source;
it is not the squad's member-unit list.

The distinction is visible in the list writes. `Append` clears the new node's
next pointer (`0x004e5b9e`), links an existing tail to it (`0x004e5bae`), and
replaces the tail (`0x004e5bb4`). `Add` instead sets the new node's next pointer
to the existing head (`0x004e5b00`) and replaces the head (`0x004e5b08`). Both
maintain the other endpoint when the resulting size is one. Thus prepending
is not an interchangeable reconstruction of this registration call for an
already nonempty registry.

The private draft used `Add`. The correction is the call to `Append`; it does
not settle the remaining initialization body, template expansion, script timing
or live squad behavior. This pass establishes static call identity and link
operations, not an observed change in retail gameplay or reconstruction parity.
Private decoded evidence is under
`bea-decomp/.worktrees/codex-equiv-20260930/local-data/geometry-gate-resume-20261001/`:
`squad-init-retail.asm`, `ptrset-add-retail.asm`, and `ptrset-append-retail.asm`.

## Unit lifecycle and damage

- `CUnit__VFunc08_InitAndAddToWorld` initializes a Unit, invokes its post-init
  virtual, and adds it to world occupancy/shadow structures.
- `CUnit__ApplyDamage` is the shared damage/lifetime anchor.
- `CUnit__ClearSpawnerSet`, `CUnit__ReleaseChildUnits`,
  `CUnit__ResetDeploymentGraphAndScheduleEvent`, and
  `CUnit__MarkDestroyedAndCleanupLinks` form the static cleanup path.
- Base/scalar-deleting destructor identities are retained in the function
  notes; they do not prove ownership of every concrete subclass field.

## BattleEngine movement, mode, and targeting

- [`functions/BattleEngine.cpp/CBattleEngine__Init.md`](functions/BattleEngine.cpp/CBattleEngine__Init.md)
  initializes walker/jet part groups and the active state.
- [`functions/BattleEngine.cpp/CBattleEngine__Move.md`](functions/BattleEngine.cpp/CBattleEngine__Move.md)
  is the shared movement/control handoff.
- `CBattleEngine__HandleLocks` maintains target locks and calls
  [`CBattleEngine__SelectNearestForwardTargetFromGlobalSet`](functions/BattleEngine.cpp/CBattleEngine__SelectNearestForwardTargetFromGlobalSet.md).
- [`CBattleEngine__SwapPrimarySecondaryPartReadersForState`](functions/BattleEngine.cpp/CBattleEngine__SwapPrimarySecondaryPartReadersForState.md)
  is the observed walker/jet reader swap boundary.
- `CBattleEngine__HandleEvent`, volume-group helpers, and morph/state helpers
  connect events and selection state; runtime input and morph behavior remain
  unproven.

## Walker, jet, weapon, and projectile handoff

Walker and jet parts have separate movement and weapon-state paths. Retained jet
evidence includes constructor/destructor, thrust, turn, pitch, yaw, gravity, and
configuration reset notes under
[`functions/BattleEngineJetPart.cpp/`](functions/BattleEngineJetPart.cpp/).

Static weapon/projectile anchors include `CWeapon__HandleFireBurstEvent`,
`ProjectileBurst__SpawnFromPercentBucketFallback`,
`ProjectileBurst__SpawnFromCurrentPreset`, `CRound__SpawnConfiguredProjectile`,
and `CRound__ArmProjectileAndSpawnTrailEffect`.
[`CBattleEngine__AddProjectile`](functions/BattleEngine.cpp/CBattleEngine__AddProjectile.md)
is the BattleEngine-facing handoff. These relationships do not prove exact
retail `CWeapon::Fire` identity, firing cadence, collision, damage, or stealth
interaction.

## AI, readers, and spawning

Static rows connect deploy/undeploy state, target-heading updates,
active-reader replacement, side compatibility, event dispatch, and animation
state. MissionScript `GetThingRef` / `SpawnThing` context is owned by
[`missionscript-iscript-static-contract.md`](missionscript-iscript-static-contract.md).
Source-corpus name matches and factory calls do not prove runtime object
identity or spawn outcomes.

## Collision and terrain handoff

Static projectile paths connect `CCollisionSeekingRound` setup/response/sweep
helpers to `CMeshCollisionVolume`, `CHLCollisionDetector`, and height-field
sampling. The evidence supports call relationships and observed flags, not
collision correctness, concrete record layouts, terrain response, or gameplay
outcomes.

## Claim boundary

This map supports scoped parser, patch-candidate, runtime-observation, and
rebuild planning. It does not prove runtime damage, AI, targeting, input,
movement, morph, weapons, spawning, projectile collision, cloak/stealth, HUD,
or terrain behavior; exact object/vtable layouts; exact source-body identities;
patch safety; gameplay outcomes; visual fidelity; or rebuild parity.
