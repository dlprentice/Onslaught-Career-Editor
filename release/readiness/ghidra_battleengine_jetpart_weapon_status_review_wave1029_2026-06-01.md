# Ghidra BattleEngine JetPart Weapon Status Review Wave1029

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 live correction closeout:** Historical record; `0x00406560` → `CBattleEngine__HandleLocks` (was `CBattleEngine__UpdateAutoTargetSetAndFireProjectiles`); `0x004081c0` → `CBattleEngine__Move` (was `CMonitor__Process`). The original text below remains provenance rather than current semantic authority. It is superseded only where confirmed. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); final per-address decisions and exact before/after metadata are in `reverse-engineering/binary-analysis/ghidra-reviewed-correction-decisions-2026-07-13.jsonl` and `reverse-engineering/binary-analysis/ghidra-reviewed-correction-plan-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Status: complete read-only static review
Date: 2026-06-01
Scope: `battleengine-jetpart-weapon-status-review-wave1029`

Wave1029 re-read thirteen `CBattleEngineJetPart` weapon/status/accessor/reset rows from the Wave911 residual surface. The review made no mutation: no Ghidra mutation, no rename, no signature change, no comment/tag change, no function-boundary change, and no executable-byte change.

Primary targets:

| Address | Saved state | Fresh evidence |
| --- | --- | --- |
| `0x00411e70 CBattleEngineJetPart__ChangeWeapon` | `void __thiscall CBattleEngineJetPart__ChangeWeapon(void * this)` | Xrefs from `CBattleEngine__ChangeWeapon` and `CGeneralVolume__DisableLinkedEntriesByNameAndReselect`; body counts weapons, selects the next active/usable weapon, clears slow movement, loses charge, and may auto-zoom when zoom mode changes. |
| `0x00412000 CBattleEngineJetPart__LoseWeaponCharge` | `void __thiscall CBattleEngineJetPart__LoseWeaponCharge(void * this)` | Xrefs from `CMonitor__Process`, `CBattleEngine__Morph`, and `CBattleEngine__AugmentWeapon`; selected JetPart weapon path clears weapon `+0x60` charge/progress. |
| `0x00412050 CBattleEngineJetPart__WeaponFired` | `int __thiscall CBattleEngineJetPart__WeaponFired(void * this, void * weapon)` | Xref from `CBattleEngine__CanSpawnBurstForResolvedEntry`; one stack argument (`ret 0x4`) and source/decompile evidence match JetPart quota, ammo, heat/overheat, and cooldown bookkeeping. |
| `0x004121b0 CBattleEngineJetPart__GetWeaponAmmoPercentage` | `float __thiscall CBattleEngineJetPart__GetWeaponAmmoPercentage(void * this)` | Xref from `CBattleEngine__GetWeaponAmmoPercentage`; divides selected weapon store value `+0x52c` by configuration capacity `+0x88` and clamps to `1.0`. |
| `0x004122b0 CBattleEngineJetPart__IsEnergyWeapon` | `int __thiscall CBattleEngineJetPart__IsEnergyWeapon(void * this)` | Xref from `CBattleEngine__IsEnergyWeapon`; returns selected weapon store heat/energy flag at battleEngine `+0x55c[store]`, preserving the Wave308 stale-label correction. |
| `0x00412310 CBattleEngineJetPart__IsWeaponOverheated` | `int __thiscall CBattleEngineJetPart__IsWeaponOverheated(void * this)` | Xref from `CBattleEngine__IsWeaponOverheated`; returns selected weapon store overheat flag at battleEngine `+0x544[store]`, preserving the Wave308 stale-label correction. |
| `0x00412370 CBattleEngineJetPart__GetWeaponCharge` | `float __thiscall CBattleEngineJetPart__GetWeaponCharge(void * this)` | Xref from `CBattleEngine__GetWeaponCharge`; divides weapon `+0x60` progress by the last valid definition threshold bucket. |
| `0x00412480 CBattleEngineJetPart__GetWeaponPhysicsName` | `char * __thiscall CBattleEngineJetPart__GetWeaponPhysicsName(void * this)` | Xref from `CBattleEngine__GetWeaponPhysicsName`; returns selected weapon definition/context field `+0x00`. |
| `0x004124d0 CBattleEngineJetPart__GetCurrentWeaponNameField04` | `char * __thiscall CBattleEngineJetPart__GetCurrentWeaponNameField04(void * this)` | Xref from `CBattleEngine__ChangeWeapon`; returns selected weapon definition/context field `+0x04` before HUD weapon-sample string matching. |
| `0x00412520 CBattleEngineJetPart__GetWeaponIconName` | `char * __thiscall CBattleEngineJetPart__GetWeaponIconName(void * this)` | Xref from `CBattleEngine__GetWeaponIconName`; returns selected weapon definition/context field `+0x38`. |
| `0x00412570 CBattleEngineJetPart__CanWeaponFire` | `int __thiscall CBattleEngineJetPart__CanWeaponFire(void * this)` | Xref from `CBattleEngine__UpdateAutoTargetSetAndFireProjectiles`; mirrors current-weapon ammo/heat/overheat gates. |
| `0x00412610 CBattleEngineJetPart__GetCurrentWeapon` | `void * __thiscall CBattleEngineJetPart__GetCurrentWeapon(void * this)` | Xrefs from projectile/targeting and state helpers; walks the selected index and returns the current JetPart weapon pointer. |
| `0x00412650 CBattleEngineJetPart__ResetConfiguration` | `void __thiscall CBattleEngineJetPart__ResetConfiguration(void * this)` | Xrefs from `CBattleEngine__UpdateConfiguration` and the JetPart constructor; drains the weapon set, deletes old weapons, walks config `+0x50`, creates/initializes weapons, appends them, and resets the current index. |

Context evidence covered `0x00409e80 CBattleEngine__AutoZoomOut`, `0x00409f70 CBattleEngine__ChangeWeapon`, `0x0040a580 CBattleEngine__Morph`, `0x00410210 CBattleEngineJetPart__ctor`, `0x004102a0 CBattleEngineJetPart__dtor_base`, `0x0040c2e0 CBattleEngine__CanSpawnBurstForResolvedEntry`, `0x00413eb0 CBattleEngineWalkerPart__ChangeWeapon`, `0x004140d0 CBattleEngineWalkerPart__WeaponFired`, `0x004146b0 CBattleEngineWalkerPart__ResetConfiguration`, `0x005068f0 CWeapon__AdvanceChargeProgressIfAnySlotAssigned`, and `0x00506930 CWeapon__HandleFireBurstEvent`.

Evidence counts:

- Primary exports: 13 metadata rows, 13 tag rows, 19 xref rows, 790 body-instruction rows, and 13 decompile rows.
- Context exports: 11 metadata rows, 11 tag rows, 20 xref rows, 1583 body-instruction rows, and 11 decompile rows.
- Queue closure remains `6238/6238 = 100.00%` with 0 commentless, 0 exact-undefined signatures, and 0 `param_N`.
- Wave911 focused re-audit progress after Wave1029: `618/1408 = 43.89%`; expanded static surface progress: `847/1493 = 56.73%`; Wave911 top-500 risk-ranked coverage remains `500/500 = 100.00%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260601-025247_post_wave1029_battleengine_jetpart_weapon_status_review_verified`, 19 files, 173968263 bytes, `DiffCount=0`, `HashDiffCount=0`.

What this proves:

- The saved JetPart weapon/status/accessor/reset rows remain internally coherent under fresh metadata/tag/xref/instruction/decompile exports.
- The Wave306/Wave308 JetPart owner, signature, energy/overheat, and accessor corrections remain supported by current caller/decompile evidence.
- The JetPart rows line up with BattleEngine caller wrappers, WalkerPart comparison rows, and CWeapon charge/burst context.

What remains unproven:

- Runtime firing, charging, HUD, audio, heat, overheat, zoom, stealth, or cloak behavior.
- Exact `CBattleEngine::WeaponFired` identity or `weapon_fire_breaks_stealth`.
- Exact `CBattleEngineJetPart`, `CBattleEngine`, or `CWeapon` layouts.
- Exact source-body identity beyond static source/decompile parity.
- BEA patch behavior, gameplay outcomes, and rebuild parity.

Probe token anchor: Wave1029; battleengine-jetpart-weapon-status-review-wave1029; 0x00411e70 CBattleEngineJetPart__ChangeWeapon; 0x00412050 CBattleEngineJetPart__WeaponFired; 0x004122b0 CBattleEngineJetPart__IsEnergyWeapon; 0x00412310 CBattleEngineJetPart__IsWeaponOverheated; 0x00412650 CBattleEngineJetPart__ResetConfiguration; 618/1408 = 43.89%; 847/1493 = 56.73%; 500/500 = 100.00%; 6238/6238 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260601-025247_post_wave1029_battleengine_jetpart_weapon_status_review_verified; no mutation.
