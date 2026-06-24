# Wave1138 BattleEngine WalkerPart Current-Risk Review

Status: complete static read-only evidence
Date: 2026-06-05
Tag: `wave1138-battleengine-walkerpart-current-risk-review`

Wave1138 accounts for `5 rows` from the Wave1108 current focused continuity denominator as a BattleEngine WalkerPart weapon/ammo/heat current-risk cluster. It advances Wave1108 current focused accounting to `219/1179 = 18.58%` with current focused candidates: 1178, live regenerated current focused candidates: 1178, and remaining active focused work: 960.

Static closure remains `6410/6410 = 100.00%`; expanded post-100 static surface remains `1560/1560 = 100.00%`; Wave911 focused remains `812/1408 = 57.67%`; Wave911 top-500 risk-ranked remains `500/500 = 100.00%`; static debt remains `0 / 0 / 0`.

This was a fresh Ghidra export plus read-only review. It made no mutation: no rename, signature, comment, tag, function-boundary, executable-byte, BEA launch, installed-game, or runtime-file mutation.

## Primary Rows

| Address | Static read-back evidence |
| --- | --- |
| `0x00412cf0 CBattleEngineWalkerPart__dtor_base` | Called from `0x00405bbc CBattleEngine__dtor_base`; drains owned weapon entries through `CSPtrSet__Remove`, virtual destructor calls, and `CSPtrSet__Clear`. |
| `0x00414410 CBattleEngineWalkerPart__GetWeaponAmmoPercentage` | Called from `0x0040c43f CBattleEngine__GetWeaponAmmoPercentage`; calls `CBattleEngineWalkerPart__GetCurrentWeapon`, reads store `+0x52c`, divides by configuration `+0x4b0/+0x88`, and clamps to `1.0`. |
| `0x00414470 CBattleEngineWalkerPart__GetWeaponAmmoCount` | Called from `0x0040c46f CBattleEngine__GetWeaponAmmoCount`; calls `CBattleEngineWalkerPart__GetCurrentWeapon`, rejects heat-store rows via `+0x55c`, and rounds store `+0x52c`. |
| `0x004144c0 CBattleEngineWalkerPart__IsEnergyWeapon` | Called from `0x0040c48f CBattleEngine__IsEnergyWeapon`; calls `CBattleEngineWalkerPart__GetCurrentWeapon` and reads the current weapon-store heat/energy flag at main-part `+0x55c`. |
| `0x004144f0 CBattleEngineWalkerPart__IsWeaponOverheated` | Called from `0x0040c3af CBattleEngine__IsWeaponOverheated`; calls `CBattleEngineWalkerPart__GetCurrentWeapon` and reads the current weapon-store overheat flag at main-part `+0x544`. |

## Evidence Counts

| Export | Rows |
| --- | ---: |
| Primary metadata | 5 |
| Primary tags | 5 |
| Primary xrefs | 5 |
| Primary instructions | 125 |
| Primary decompile index | 5 |

Verified backup: `G:\GhidraBackups\BEA_20260605-130856_post_wave1138_battleengine_walkerpart_current_risk_review_verified`; `19` files, `175967111` bytes, `DiffCount=0`, `HashDiffCount=0`.

Previous completed Ghidra review backup: `G:\GhidraBackups\BEA_20260605-122130_post_wave1137_physics_script_weapon_bridge_review_verified`.

Probe token anchor: Wave1138; wave1138-battleengine-walkerpart-current-risk-review; 219/1179 = 18.58%; 5 rows; current focused candidates: 1178; live regenerated current focused candidates: 1178; remaining active focused work: 960; BattleEngine WalkerPart weapon/ammo/heat current-risk cluster; fresh Ghidra export; read-only review; no mutation; 0 / 0 / 0; 0x00412cf0 CBattleEngineWalkerPart__dtor_base; 0x00414410 CBattleEngineWalkerPart__GetWeaponAmmoPercentage; 0x00414470 CBattleEngineWalkerPart__GetWeaponAmmoCount; 0x004144c0 CBattleEngineWalkerPart__IsEnergyWeapon; 0x004144f0 CBattleEngineWalkerPart__IsWeaponOverheated; G:\GhidraBackups\BEA_20260605-130856_post_wave1138_battleengine_walkerpart_current_risk_review_verified; G:\GhidraBackups\BEA_20260605-122130_post_wave1137_physics_script_weapon_bridge_review_verified; wave1108-current-risk-rank; current-risk denominator; current risk candidates: 6165; focused threshold `15`; not Wave911 reconstruction.

## Boundary

This is static Ghidra evidence only. Runtime WalkerPart weapon behavior, runtime HUD ammo behavior, runtime heat/overheat behavior, exact `CBattleEngine`/WalkerPart/weapon-store/configuration layouts, `weapon_fire_breaks_stealth`, exact source-body identity, BEA patching, gameplay outcomes, visual QA, and rebuild parity remain separate proof.
