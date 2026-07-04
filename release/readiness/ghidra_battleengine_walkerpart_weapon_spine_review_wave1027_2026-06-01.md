# Ghidra BattleEngine WalkerPart Weapon Spine Review Wave1027

Status: complete read-only static review
Date: 2026-06-01
Scope: `battleengine-walkerpart-weapon-spine-review-wave1027`

Wave1027 re-read twelve `CBattleEngineWalkerPart` constructor/destructor, fire/charge, current-weapon, and HUD/accessor rows from the expanded Wave911 post-top-500 surface. The review made no mutation: no Ghidra mutation, no rename, no signature change, no comment/tag change, no function-boundary change, and no executable-byte change.

Primary targets:

| Address | Saved state | Fresh evidence |
| --- | --- | --- |
| `0x00412bc0 CBattleEngineWalkerPart__ctor` | `void * __thiscall CBattleEngineWalkerPart__ctor(void * this, void * mainPart)` | Called from `0x00404dd0 CBattleEngine__Init`; stores main part, initializes weapon/dash fields, calls `CBattleEngineWalkerPart__ResetConfiguration`, and registers `g_dash_*` variables. |
| `0x00412cf0 CBattleEngineWalkerPart__dtor_base` | `void __thiscall CBattleEngineWalkerPart__dtor_base(void * this)` | Called from `0x00405a40 CBattleEngine__dtor_base`; drains weapon entries and releases primary/augmented weapon pointers. |
| `0x00413cc0 CBattleEngineWalkerPart__FireWeapon` | `void __thiscall CBattleEngineWalkerPart__FireWeapon(void * this)` | Called from `0x00409f20 CGeneralVolume__Reset588AndDispatchModeSpecific_13CC0_or_11B90`; clears main-part `+0x588`, resolves current weapon through `0x00414030`, and dispatches `ProjectileBurst__SpawnFromPercentBucketFallback` when active. |
| `0x00413cf0 CBattleEngineWalkerPart__ChargeWeapon` | `void __thiscall CBattleEngineWalkerPart__ChargeWeapon(void * this)` | Called from `0x00409ef0 CGeneralVolume__DispatchModeSpecificReset_13CF0_or_11BF0`; resolves current weapon, checks charge/assigned-slot gates, calls `CWeapon__AdvanceChargeProgressIfAnySlotAssigned`, updates store heat/overheat lanes, and may dispatch projectile-burst fallback. |
| `0x00414030 CBattleEngineWalkerPart__GetCurrentWeapon` | `void * __thiscall CBattleEngineWalkerPart__GetCurrentWeapon(void * this)` | Fan-in from weapon accessors, movement, change-weapon, charge/fire, and BattleEngine wrapper rows; resolves primary/augmented/list weapon entries and may reset current index. |
| `0x004140d0 CBattleEngineWalkerPart__WeaponFired` | `int __thiscall CBattleEngineWalkerPart__WeaponFired(void * this, void * weapon)` | One explicit stack argument; called from `0x0040c2e0 CBattleEngine__CanSpawnBurstForResolvedEntry`; updates list, primary, and augmented weapon store value/heat/overheat paths. |
| `0x00414410 CBattleEngineWalkerPart__GetWeaponAmmoPercentage` | `float __thiscall CBattleEngineWalkerPart__GetWeaponAmmoPercentage(void * this)` | Called from `0x0040c3c0 CBattleEngine__GetWeaponAmmoPercentage`; resolves current weapon and computes/clamps store value against configuration capacity. |
| `0x00414470 CBattleEngineWalkerPart__GetWeaponAmmoCount` | `int __thiscall CBattleEngineWalkerPart__GetWeaponAmmoCount(void * this)` | Called from `0x0040c460 CBattleEngine__GetWeaponAmmoCount`; returns rounded non-heat store value. |
| `0x004144c0 CBattleEngineWalkerPart__IsEnergyWeapon` | `int __thiscall CBattleEngineWalkerPart__IsEnergyWeapon(void * this)` | Called from `0x0040c480 CBattleEngine__IsEnergyWeapon`; reads current weapon store heat flag at main-part `+0x55c`. |
| `0x004144f0 CBattleEngineWalkerPart__IsWeaponOverheated` | `int __thiscall CBattleEngineWalkerPart__IsWeaponOverheated(void * this)` | Called from `0x0040c3a0 CBattleEngine__IsWeaponOverheated`; reads current weapon overheat flag at main-part `+0x544`. |
| `0x00414520 CBattleEngineWalkerPart__GetWeaponCharge` | `float __thiscall CBattleEngineWalkerPart__GetWeaponCharge(void * this)` | Called from `0x0040c4a0 CBattleEngine__GetWeaponCharge`; returns current weapon charge/progress context from weapon `+0x60`. |
| `0x004145f0 CBattleEngineWalkerPart__GetCurrentWeaponZoomMode` | `int __thiscall CBattleEngineWalkerPart__GetCurrentWeaponZoomMode(void * this)` | Called from `0x00409f70 CBattleEngine__ChangeWeapon`; returns the selected weapon zoom-mode-like field used before/after slot switching. |

Context evidence covered `0x0040a580 CBattleEngine__Morph`, `0x00413eb0 CBattleEngineWalkerPart__ChangeWeapon`, `0x004146b0 CBattleEngineWalkerPart__ResetConfiguration`, `0x005068f0 CWeapon__AdvanceChargeProgressIfAnySlotAssigned`, and `0x00506930 CWeapon__HandleFireBurstEvent`.

Evidence counts:

- Primary exports: 12 metadata rows, 12 tag rows, 39 xref rows, 704 body-instruction rows, and 12 decompile rows.
- Context exports: 5 metadata rows, 5 tag rows, 13 xref rows, 718 body-instruction rows, and 5 decompile rows.
- Queue closure remains `6238/6238 = 100.00%` with 0 commentless, 0 exact-undefined signatures, and 0 `param_N`.
- Wave911 focused re-audit progress after Wave1027: `600/1408 = 42.61%`; expanded static surface progress: `829/1493 = 55.53%`; Wave911 top-500 risk-ranked coverage remains `500/500 = 100.00%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260601-014543_post_wave1027_battleengine_walkerpart_weapon_spine_review_verified`, 19 files, 173968263 bytes, `DiffCount=0`, `HashDiffCount=0`.

What this proves:

- The saved WalkerPart weapon-spine names, signatures, comments, xrefs, instruction bodies, and decompiles remain internally coherent.
- `FireWeapon` and `ChargeWeapon` still route through `CBattleEngineWalkerPart__GetCurrentWeapon` and the projectile-burst fallback path while preserving their static source-parity boundary language.
- The HUD/accessor rows still bridge BattleEngine wrapper calls to current-weapon store, heat, overheat, charge, and zoom-mode state.
- The prior `+0x55c` heat / `+0x544` overheat distinction remains address-qualified for the WalkerPart rows.

What remains unproven:

- Runtime firing, charging, HUD, heat, overheat, or zoom behavior.
- Exact retail `CBattleEngine::WeaponFired` identity or `weapon_fire_breaks_stealth`.
- Exact source-body identity beyond static source/decompile parity.
- Concrete `CBattleEngineWalkerPart`, `CBattleEngine`, `CWeapon`, or configuration layouts.
- BEA patch behavior, gameplay outcomes, and rebuild parity.

Probe token anchor: Wave1027; battleengine-walkerpart-weapon-spine-review-wave1027; 0x00412bc0 CBattleEngineWalkerPart__ctor; 0x00413cc0 CBattleEngineWalkerPart__FireWeapon; 0x00413cf0 CBattleEngineWalkerPart__ChargeWeapon; 0x00414030 CBattleEngineWalkerPart__GetCurrentWeapon; 0x004140d0 CBattleEngineWalkerPart__WeaponFired; 0x004145f0 CBattleEngineWalkerPart__GetCurrentWeaponZoomMode; 600/1408 = 42.61%; 829/1493 = 55.53%; 500/500 = 100.00%; 6238/6238 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260601-014543_post_wave1027_battleengine_walkerpart_weapon_spine_review_verified; no mutation.
