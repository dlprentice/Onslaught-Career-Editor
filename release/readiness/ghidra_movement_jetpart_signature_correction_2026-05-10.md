# Ghidra Movement / JetPart Signature Correction - 2026-05-10

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 semantic revalidation:** Historical record; `0x00411630` → `CBattleEngineJetPart__HandleGroundEffect` (was `CMonitor__IntegrateMovementAgainstTerrain`); `0x00411aa0` → `CBattleEngineJetPart__GetFriction` (was `CMonitor__ComputeTerrainVelocityScalar`); `0x00411b70` → `CBattleEngineJetPart__GetIsDoingSpecialAirMove` (was `CBattleEngineJetPart__IsStateMachineActive`). The original text below remains provenance rather than current semantic authority. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); exact records are in `reverse-engineering/binary-analysis/ghidra-full-reaudit-corrections-2026-07-13.json` and `reverse-engineering/binary-analysis/ghidra-targeted-revalidation-corrections-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

> **Owner/name supersession (2026-07-12):** this file remains the historical
> saved-name/read-back record. Current read-only caller, object-layout, and
> source-order evidence identifies `0x00411630` as
> `CBattleEngineJetPart__HandleGroundEffect`, `0x00411aa0` as
> `CBattleEngineJetPart__GetFriction`, and `0x00411b70` as
> `CBattleEngineJetPart__GetIsDoingSpecialAirMove`. See the
> [current movement crosswalk](../../reverse-engineering/binary-analysis/battleengine-movement-static-crosswalk-2026-07-12.md).

## Scope

This note records a saved Ghidra name/signature/comment correction tranche for movement, vector, and BattleEngine JetPart weapon helper functions. It is public-safe static RE evidence only: no BEA launch, no debugger attach, no executable patching, no installed-game mutation, and no private decompile excerpt is included here.

## Saved Targets

| Address | Saved name | Correction boundary |
| --- | --- | --- |
| `0x00411630` | `CMonitor__IntegrateMovementAgainstTerrain` | Hardened `void * this` signature and terrain/static-shadow movement comment. |
| `0x00411a60` | `Vec3__Cross` | Hardened `this`, `outCross`, and `rhs` vector signature with `ret 0x8` evidence. |
| `0x00411aa0` | `CMonitor__ComputeTerrainVelocityScalar` | Hardened `float` return and monitor receiver signature. |
| `0x00411b70` | `CBattleEngineJetPart__IsStateMachineActive` | Corrected stale `CGeneralVolume` owner label to JetPart state-machine context. |
| `0x00411e70` | `CBattleEngineJetPart__ChangeWeapon` | Corrected stale cockpit weapon-cycle label to JetPart weapon cycling context. |
| `0x00412000` | `CBattleEngineJetPart__LoseWeaponCharge` | Corrected stale monitor tracked-entry label to JetPart weapon-charge reset context. |
| `0x00412050` | `CBattleEngineJetPart__WeaponFired` | Corrected stale engine burst-quota label to JetPart weapon-fired bookkeeping context. |
| `0x004121b0` | `CBattleEngineJetPart__GetWeaponAmmoPercentage` | Corrected stale `CGeneralVolume` slot-ratio label to JetPart ammo percentage context. |
| `0x004122b0` | `CBattleEngineJetPart__IsWeaponOverheated` | Corrected stale `CGeneralVolume` slot-flag label to JetPart overheat flag context. |
| `0x00412310` | `CBattleEngineJetPart__IsEnergyWeapon` | Corrected stale `CGeneralVolume` slot-flag label to JetPart energy weapon context. |
| `0x00412370` | `CBattleEngineJetPart__GetWeaponCharge` | Corrected stale `CGeneralVolume` distance/progress label to JetPart weapon charge context. |
| `0x00412480` | `CBattleEngineJetPart__GetWeaponPhysicsName` | Corrected stale `CGeneralVolume` mode-id label to JetPart physics/name string context. |
| `0x004124d0` | `CBattleEngineJetPart__GetCurrentWeaponNameField04` | Corrected stale selected-weapon definition label to JetPart selected weapon field `+0x04`. |
| `0x00412520` | `CBattleEngineJetPart__GetWeaponIconName` | Corrected stale indexed-entry field label to JetPart icon-name string context. |
| `0x00412570` | `CBattleEngineJetPart__CanWeaponFire` | Corrected stale BattleEngine indexed-entry usability label to JetPart fire gate context. |
| `0x00412610` | `CBattleEngineJetPart__GetCurrentWeapon` | Corrected stale BattleEngine indexed-entry getter label to JetPart selected weapon pointer context. |

## Evidence Summary

- Headless rename dry/apply saved `13` owner/name corrections with dry `applied=0 skipped=13 missing=0 bad=0` and apply `applied=13 skipped=0 missing=0 bad=0`.
- Headless signature dry/apply saved `16` signatures/comments with dry `updated=0 skipped=16 missing=0 bad=0` and apply `updated=16 skipped=0 missing=0 bad=0`.
- Final metadata and decompile read-back found `16/16` targets.
- The focused probe reports `16` targets, `13` renamed targets, `0` stale name hits, `0` `param_N` signature hits, `0` comment overclaims, `16` xref evidence hits, `16` decompile evidence hits, and `2` return-evidence hits.
- The refreshed queue reports `5868` total functions, `564` commented functions, `5304` commentless functions, `2068` undefined signatures, and `2397` `param_N` signatures.

## Boundary

This tranche improves saved Ghidra names, signatures, and comments only. It does not prove concrete `CMonitor`, `Vec3`, `CBattleEngineJetPart`, `CBattleEngine`, weapon, or configuration layouts; local variable names; structure types; tags; runtime movement, weapon switching, weapon-fired, cloak, or fire-while-cloaked behavior; BEA launch behavior; game patching; or rebuild parity. It does not close `weapon_fire_breaks_stealth`.
