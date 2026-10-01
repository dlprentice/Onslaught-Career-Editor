# Unit / BattleEngine / gameplay static contract

Status: bounded retail static map; not runtime gameplay proof
Last updated: 2026-10-01 (squad registration call and list-link writes rechecked)
Summary: retained gameplay evidence routing plus a fresh, bounded squad-registration correction.
Evidence: MEASURED — October 1 pristine instruction reads of squad registration and Add/Append; the other sections retain their July 16 evidence limits.
Specimen: pristine `BEA.exe.original.backup`, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

This contract routes the retained Unit/BattleEngine evidence without repeating
the retired wave ledger. Function-level notes under [`functions/`](functions/)
remain the detailed evidence owners.

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
