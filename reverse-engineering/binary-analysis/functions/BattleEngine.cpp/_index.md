# BattleEngine.cpp Function Mappings

> Functions from BattleEngine.cpp mapped to BEA.exe binary
> Source: references/Onslaught/BattleEngine.cpp (Stuart's code)
> Discovered: 2025-12-15 via Ghidra analysis

## Overview
- **Functions Mapped:** 3
- **Status:** NAMED in Ghidra
- **Class:** CBattleEngine

## Function List

| Address | Name | Status | Link |
|---------|------|--------|------|
| 0x00404dd0 | CBattleEngine__Init | NAMED | [View](CBattleEngine__Init.md) |
| 0x004063b0 | CBattleEngine__UpdateWeaponEffect | NAMED | [View](CBattleEngine__UpdateWeaponEffect.md) |
| 0x00406fc0 | CBattleEngine__AddProjectile | NAMED | [View](CBattleEngine__AddProjectile.md) |

## Related Runtime Helper Cluster (ChangeWeapon Path)

Recovered in headless semantic wave20 from the `CBattleEngine__ChangeWeapon` call-chain:

| Address | Name | Notes |
|---------|------|-------|
| 0x00411e70 | CCockpit__CycleToNextUsableWeapon | Iterates weapon list and advances to next valid candidate. |
| 0x004124d0 | CGeneralVolume__GetSelectedWeaponDef | Returns currently selected weapon-definition pointer from indexed set entry. |
| 0x004145f0 | CGeneralVolume__GetSelectedWeaponDef_CachedPath | Alternate selected-weapon accessor through cached-path helper. |
| 0x00412cf0 | CCockpit__DestroyWeaponSetAndOwnedNodes | Clears/destroys weapon-set container state and owned nodes. |

## Headless Semantic Wave108 Promotions (2026-02-26)

These entry-selection helpers are used by combat/runtime selection paths that resolve and validate active indexed entries.

| Address | Name | Notes |
|---------|------|-------|
| 0x00412610 | CBattleEngine__GetIndexedEntry | Returns the pointer for the currently selected indexed entry from the list container. |
| 0x00412570 | CBattleEngine__IsIndexedEntryUsable | Evaluates readiness gates for the selected indexed entry and returns boolean usable/not-usable state. |
| 0x00414630 | CBattleEngine__IsResolvedEntryUsable | Resolves current/fallback entry first, then applies readiness gates to return final usable state. |

## Headless Semantic Wave112 Promotion (2026-02-26)

| Address | Name | Notes |
|---------|------|-------|
| 0x004102a0 | CBattleEngine__DestroySPtrSetElementsAndClear | Iterates an SPtrSet-like container, destroys each element via virtual dtor call, then clears the set. |

## Headless Semantic Wave113 Promotion (2026-02-26)

| Address | Name | Notes |
|---------|------|-------|
| 0x00407310 | CBattleEngine__IsCurrentResolvedEntry | Returns true when the current resolved entry pointer matches the supplied entry pointer. |

## Headless Semantic Wave114 Promotions (2026-02-26)

| Address | Name | Notes |
|---------|------|-------|
| 0x00406460 | CBattleEngine__SwapPrimarySecondaryPartReadersForState | State-gated morph helper that swaps active reader/object pointers and reparents active part links between walker/jet paths. |
| 0x00406560 | CBattleEngine__UpdateAutoTargetSetAndFireProjectiles | Maintains/filters tracked target set and emits projectiles under resolved-entry, range, and forward-angle gates. |
| 0x00406da0 | CBattleEngine__SelectNearestForwardTargetFromGlobalSet | Selects nearest forward-facing in-range target from global candidate set, excluding entries already in current tracking set. |

## Related

- CBattleEngine is the core combat/physics system class
- Init sets up sound effects, mesh models, weapon systems, physics, collision
- UpdateWeaponEffect and AddProjectile manage active projectiles and weapon effects
- Source: `references/Onslaught/BattleEngine.cpp`
- Header: `references/Onslaught/BattleEngine.h`
- Parent: [../README.md](../README.md)
