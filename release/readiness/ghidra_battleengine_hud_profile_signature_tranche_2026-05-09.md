# Ghidra BattleEngine HUD / Profile Signature Tranche - 2026-05-09

## Summary

This wave reparsed six saved Ghidra functions in the BattleEngine HUD/profile cluster that were still carrying caller-owned or mode-helper names. Fresh source comparison, metadata, decompile, xref, and instruction read-back showed these are better treated as BattleEngine weapon/configuration accessors. A serial headless dry/apply pass saved corrected names, signatures, and proof-boundary comments, followed by fresh read-back and a focused probe.

## Corrected Targets

| Address | Previous state | Saved state after correction | Evidence boundary |
| --- | --- | --- | --- |
| `0x0040c480` | `CExplosionInitThing__GetCurrentEntrySlotFlag_55C` | `int __thiscall CBattleEngine__IsWeaponOverheated(void * this)` | Source/caller bridge for the HUD overheat-style weapon flag; body routes to walker `+0x578` or jet `+0x57c` part paths and reaches current-entry `+0x55c` helpers. |
| `0x0040c4a0` | `CExplosionInitThing__GetCurrentEntryDistanceProgressRatioOrRacerDelta` | `float __thiscall CBattleEngine__GetWeaponCharge(void * this)` | Source/caller bridge for `CBattleEngine::GetWeaponCharge`; Racer path samples render/world position against terrain/water-style height, otherwise walker/jet charge helpers are used. |
| `0x0040c550` | `CExplosionInitThing__GetCurrentEntryDisplayString` | `short * __thiscall CBattleEngine__GetWeaponName(void * this)` | HUD status-panel caller and source bridge for the current weapon display string. |
| `0x0040c570` | `CGeneralVolume__DispatchModeSpecific_145D0_or_12480` | `char * __thiscall CBattleEngine__GetWeaponPhysicsName(void * this)` | `IScript__GetThingName` caller plus source bridge for the current weapon physics/name payload path. |
| `0x0040c590` | `CExplosionInitThing__GetCurrentEntryFieldA4_38` | `char * __thiscall CBattleEngine__GetWeaponIconName(void * this)` | HUD status-panel caller and source bridge for current weapon icon-name context. |
| `0x0040c650` | `CBattleEngine__ApplyWeaponProfileByIndex` | `void __thiscall CBattleEngine__UpdateConfiguration(void * this)` | Source bridge for configuration id resolution, energy/life update, jet/walker `ResetConfiguration`, six store heat/value refresh, and configuration-name log. |

## Validation

- Focused tests: `py -3 tools\ghidra_battleengine_hud_profile_signature_tranche_probe_test.py` passed `2/2`.
- Headless dry/apply: `updated=0 skipped=6 missing=0 bad=0`, then `updated=6 skipped=0 missing=0 bad=0`.
- Fresh metadata/decompile read-back: `6/6` targets.
- Fresh xref read-back: `8` rows.
- Fresh instruction read-back: `774` rows.
- Focused probe: `cmd.exe /c npm run test:ghidra-battleengine-hud-profile-signature-tranche` passes with `6` targets, `6` renamed targets, `6` signature-hardened targets, `0` `param_N` signature hits, `0` stale-token hits, and `0` overclaim hits.
- Refreshed queue after this tranche reported `5866` functions, `495` commented functions, `5371` commentless functions, `2076` undefined signatures, and `2456` `param_N` signatures.

## Non-Claims

This is saved Ghidra name/signature/comment refinement only. It does not prove concrete BattleEngine, part, active-entry, string, configuration, vtable, or HUD layouts; exact `CWeapon::Fire`; exact retail `CBattleEngine::WeaponFired`; `weapon_fire_breaks_stealth`; runtime weapon, HUD, script, configuration, fire, or cloak behavior; BEA launch behavior; game patching; or rebuild parity.
