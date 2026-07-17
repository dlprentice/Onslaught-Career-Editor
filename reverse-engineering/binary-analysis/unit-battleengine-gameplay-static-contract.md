# Unit / BattleEngine / gameplay static contract

Status: bounded retail static map; not runtime gameplay proof
Last updated: 2026-07-16

This contract routes the retained Unit/BattleEngine evidence without repeating
the retired wave ledger. Function-level notes under [`functions/`](functions/)
remain the detailed evidence owners.

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
[`missionscript-iscript-static-contract.md`](missionscript-iscript-static-contract.md)
and the copied-corpus
[`../game-assets/mission-thing-usage.md`](../game-assets/mission-thing-usage.md).
Name matches and factory calls do not prove runtime object identity or spawn
outcomes.

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
