# Ghidra Walker Dash / Surface Correction - 2026-05-10

> **Owner/name supersession (2026-07-12):** this file remains the historical
> record of what the saved Ghidra project held after this wave. Current
> read-only caller, object-layout, and source-order evidence identifies
> `0x00412900` as `CBattleEngineJetPart__AutoLevel`, not a Monitor helper.
> See the [current movement crosswalk](../../reverse-engineering/binary-analysis/battleengine-movement-static-crosswalk-2026-07-12.md).

## Scope

This note records a saved Ghidra correction tranche for the `0x004127a0` through `0x00413cf0` dash/surface cluster after fresh read-back showed a saved intermediate interpretation had over-promoted several functions to JetPart/WalkerPart names. This is public-safe static RE evidence only: no BEA launch, no debugger attach, no executable patching, no installed-game mutation, and no private decompile excerpts are included here.

## Corrected Targets

| Address | Saved name/signature after correction | Evidence boundary |
| --- | --- | --- |
| `0x004127a0` | `void __thiscall CGeneralVolume__EnableLinkedEntriesByName(void * this, char * entryName)` | Corrects a stale `CBattleEngineJetPart__EnableWeapon` label. Body walks linked entries, compares entry names, and sets entry flag `+0x9c`. |
| `0x00412900` | `int __thiscall CMonitor__CanUseTrackingUpdate(void * this)` | Corrects a stale `CBattleEngineJetPart__AutoLevel` label. Body checks monitor/main-part movement, velocity, energy, and local timer context. |
| `0x004129a0` | `int __thiscall LinkedObjectList__CountFlag9C(void * this)` | Corrects a stale JetPart active-weapon label. Body counts linked entries whose `+0x9c` flag is set. |
| `0x00412bc0` | `void * __thiscall CBattleEngineWalkerPart__ctor(void * this, void * mainPart)` | WalkerPart constructor context: stores main part, initializes dash/weapon fields, calls reset configuration, and registers `g_dash_*` variables. |
| `0x00412cf0` | `void __thiscall CBattleEngineWalkerPart__dtor_base(void * this)` | WalkerPart destructor-base context: drains owned weapon entries and clears primary/augmented weapon pointers. |
| `0x00412d80` | `void __thiscall CBattleEngineWalkerPart__Forward(void * this, float moveY)` | WalkerPart forward input helper with `ret 0x4` evidence. |
| `0x00412f70` | `void __thiscall CBattleEngineWalkerPart__Backward(void * this, float moveY)` | WalkerPart backward input helper with `ret 0x4` evidence. |
| `0x00413160` | `void __thiscall CBattleEngineWalkerPart__StrafeLeft(void * this, float moveX)` | WalkerPart strafe-left input helper with `ret 0x4` evidence. |
| `0x00413360` | `void __thiscall CBattleEngineWalkerPart__StrafeRight(void * this, float moveX)` | WalkerPart strafe-right input helper with `ret 0x4` evidence. |
| `0x004135d0` | `int __thiscall CBattleEngineWalkerPart__GetIsDoingSpecialWalkerMove(void * this)` | WalkerPart special-move predicate reads counter/state at `+0x44`. |
| `0x004135e0` | `void __thiscall CBattleEngineWalkerPart__ApplyWalkVelocityLimitAndSetMovementLatch(void * this)` | Corrects a stale `ActivateLandingJets` label. Body samples main-part velocity, applies scaled movement response, and sets main-part `+0x638`. |
| `0x00413760` | `void __thiscall CMonitor__ProcessTrackingAndSurfaceAlignment(void * this)` | Corrects a stale `CBattleEngineWalkerPart__Move` label. Body is monitor-owned tracking, surface-alignment, and movement-response processing. |
| `0x00413a70` | `int __thiscall CMonitor__ShouldUseSurfaceAlignmentPath(void * this)` | Corrects a stale `CBattleEngineWalkerPart__GoingIntoWater` label. Body samples static-shadow/height context for the monitor surface-alignment path. |
| `0x00413b90` | `void __thiscall CMonitor__ResolveSurfaceAlignmentIterative(void * this)` | Corrects stale `CCylinder` and `WalkerPart Slide` labels. Body iteratively samples heightfield normals and removes into-slope velocity components. |
| `0x00413cc0` | `void __thiscall CGeneralVolume__ResetState588AndRefreshCurrentEntry(void * this)` | Corrects a stale `CBattleEngineWalkerPart__FireWeapon` label. Body clears `+0x588`, resolves the current/fallback entry, and may dispatch projectile-burst fallback. |
| `0x00413cf0` | `void __thiscall CGeneralVolume__UpdateCurrentEntryProgressAndRefresh(void * this)` | Corrects a stale `CBattleEngineWalkerPart__ChargeWeapon` label. Body applies entry progress/charge/overheat-style gates and may dispatch projectile-burst fallback. |

## Evidence Summary

- Headless correction dry/apply saved `16` signatures/comments and corrected `9` stale saved names: dry `updated=0 skipped=16 renamed=0 missing=0 bad=0`; apply `updated=16 skipped=0 renamed=9 missing=0 bad=0`.
- Final metadata read-back found `16/16` targets with expected names, signatures, and proof-boundary comments.
- Final decompile read-back dumped `16/16` targets.
- Final xref read-back recorded `20` rows.
- Final instruction read-back recorded `592` rows and preserved the `ret 0x4` evidence for the five one-stack-argument helpers.
- Focused probe `cmd.exe /c npm run test:ghidra-walker-dash-surface-signature-correction` passed with `16` targets, `9` renamed targets, and `0` failures.
- The refreshed whole-database queue reports `5868` function objects, `580` commented functions, `5288` commentless functions, `2068` `undefined` signatures, and `2381` `param_N` signatures.

## Boundary

This tranche improves saved Ghidra names, signatures, and comments only. It does not prove concrete `CGeneralVolume`, linked-list, `CMonitor`, `CBattleEngineWalkerPart`, `CBattleEngine`, weapon, terrain, or heightfield layouts; tags; local variable names; structure types; runtime movement, dash, terrain, water, weapon-fire, cloak, or fire-while-cloaked behavior; BEA launch behavior; game patching; or rebuild parity. It does not close `weapon_fire_breaks_stealth`.
