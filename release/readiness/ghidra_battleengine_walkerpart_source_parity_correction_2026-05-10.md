# Ghidra BattleEngineWalkerPart Source-Parity Correction - 2026-05-10

## Summary

Wave 308 completed a saved Ghidra name/signature/comment correction tranche for `26` BattleEngine, JetPart, and WalkerPart source-parity targets.

The tranche supersedes the immediately previous intermediate interpretation for the selected `0x004135e0` through `0x00413cf0` WalkerPart-adjacent bodies after direct source/decompile/xref review showed those functions align with `CBattleEngineWalkerPart` methods. It also corrects the saved BattleEngine and JetPart heat/energy helper swaps around `+0x544` and `+0x55c`, and promotes the adjacent zoom helpers to `CBattleEngine__AutoZoomOut`, `CBattleEngine__ZoomOut`, and `CBattleEngine__ZoomIn`.

## Corrected Targets

- `0x00409e80` -> `CBattleEngine__AutoZoomOut`
- `0x00409e90` -> `CBattleEngine__ZoomOut`
- `0x00409ec0` -> `CBattleEngine__ZoomIn`
- `0x0040c3a0` -> `CBattleEngine__IsWeaponOverheated`
- `0x0040c480` -> `CBattleEngine__IsEnergyWeapon`
- `0x004122b0` -> `CBattleEngineJetPart__IsEnergyWeapon`
- `0x00412310` -> `CBattleEngineJetPart__IsWeaponOverheated`
- `0x004135e0` -> `CBattleEngineWalkerPart__ActivateLandingJets`
- `0x00413760` -> `CBattleEngineWalkerPart__Move`
- `0x00413a70` -> `CBattleEngineWalkerPart__GoingIntoWater`
- `0x00413b90` -> `CBattleEngineWalkerPart__Slide`
- `0x00413cc0` -> `CBattleEngineWalkerPart__FireWeapon`
- `0x00413cf0` -> `CBattleEngineWalkerPart__ChargeWeapon`
- `0x00413eb0` -> `CBattleEngineWalkerPart__ChangeWeapon`
- `0x00414030` -> `CBattleEngineWalkerPart__GetCurrentWeapon`
- `0x004140d0` -> `CBattleEngineWalkerPart__WeaponFired`
- `0x00414410` -> `CBattleEngineWalkerPart__GetWeaponAmmoPercentage`
- `0x00414470` -> `CBattleEngineWalkerPart__GetWeaponAmmoCount`
- `0x004144c0` -> `CBattleEngineWalkerPart__IsEnergyWeapon`
- `0x004144f0` -> `CBattleEngineWalkerPart__IsWeaponOverheated`
- `0x00414520` -> `CBattleEngineWalkerPart__GetWeaponCharge`
- `0x004145a0` -> `CBattleEngineWalkerPart__GetWeaponName`
- `0x004145d0` -> `CBattleEngineWalkerPart__GetWeaponPhysicsName`
- `0x004145f0` -> `CBattleEngineWalkerPart__GetCurrentWeaponZoomMode`
- `0x00414610` -> `CBattleEngineWalkerPart__GetWeaponIconName`
- `0x00414630` -> `CBattleEngineWalkerPart__CanWeaponFire`

## Validation

- Headless correction dry run: `updated=0 skipped=26 renamed=0 missing=0 bad=0`.
- Headless correction apply: `updated=26 skipped=0 renamed=3 missing=0 bad=0`.
- Metadata read-back: `26/26` targets found.
- Decompile read-back: `26/26` targets dumped.
- Xref read-back: `58` rows.
- Instruction read-back: `3302` rows.
- Focused probe: `PASS targets=26 renamed=3 failures=0`.
- Whole-database queue snapshot: `5868` functions, `593` commented functions, `5275` commentless functions, `2068` undefined signatures, and `2368` `param_N` signatures.

## Boundary

This is saved static Ghidra refinement only. It does not prove concrete `CBattleEngine`, `CBattleEngineJetPart`, `CBattleEngineWalkerPart`, weapon, terrain, water, zoom, heat, or energy layouts; tags/local names/types; runtime movement, landing-jets, water, slide, weapon, zoom, HUD, cloak, or fire-while-cloaked behavior; exact retail `CBattleEngine::WeaponFired`; `weapon_fire_breaks_stealth`; BEA launch behavior; game patching; or rebuild parity.

Raw read-back exports and generated proof JSON remain under ignored `subagents/`.
