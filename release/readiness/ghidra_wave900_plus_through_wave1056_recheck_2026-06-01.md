# Ghidra Wave900 Through Wave1056 Recheck

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 semantic revalidation:** Historical record; `0x00406560` → `CBattleEngine__HandleLocks` (was `CBattleEngine__UpdateAutoTargetSetAndFireProjectiles`). The original text below remains provenance rather than current semantic authority. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); exact records are in `reverse-engineering/binary-analysis/ghidra-full-reaudit-corrections-2026-07-13.json` and `reverse-engineering/binary-analysis/ghidra-targeted-revalidation-corrections-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Status: complete local static evidence gate
Date: 2026-06-01
Scope: `wave900-plus-through-wave1056-recheck`

This note extends the Wave900-plus static recheck boundary through Wave1056. Wave900 remains the loaded-Ghidra export-contract function-quality closure point; Wave1056 adds a read-only BattleEngine JetPart / WalkerPart residual helper review.

Wave1056 (`battleengine-jet-walker-residual-review-wave1056`) re-read six existing BattleEngine JetPart / WalkerPart helpers with no mutation: `0x004114d0 CBattleEngineJetPart__Gravity`, `0x00411500 CBattleEngineJetPart__HandleSkimming`, `0x004145a0 CBattleEngineWalkerPart__GetWeaponName`, `0x004145d0 CBattleEngineWalkerPart__GetWeaponPhysicsName`, `0x00414610 CBattleEngineWalkerPart__GetWeaponIconName`, and `0x00414630 CBattleEngineWalkerPart__CanWeaponFire`.

Fresh evidence:

- Primary exports: `6` metadata rows, `6` tag rows, `7` xref rows, `157` function-body instruction rows, and `6` decompile rows.
- Context exports: `14` metadata rows, `14` tag rows, `48` xref rows, `1142` function-body instruction rows, and `14` decompile rows.
- Context anchors include `0x00409f70 CBattleEngine__ChangeWeapon`, `0x0040c2e0 CBattleEngine__CanSpawnBurstForResolvedEntry`, `0x0040c3c0 CBattleEngine__GetWeaponAmmoPercentage`, `0x0040c460 CBattleEngine__GetWeaponAmmoCount`, `0x0040c4a0 CBattleEngine__GetWeaponCharge`, `0x0040c550 CBattleEngine__GetWeaponName`, `0x0040c570 CBattleEngine__GetWeaponPhysicsName`, `0x0040c590 CBattleEngine__GetWeaponIconName`, `0x00410210 CBattleEngineJetPart__ctor`, `0x004102a0 CBattleEngineJetPart__dtor_base`, `0x00411e70 CBattleEngineJetPart__ChangeWeapon`, `0x00412610 CBattleEngineJetPart__GetCurrentWeapon`, `0x00413eb0 CBattleEngineWalkerPart__ChangeWeapon`, and `0x00414030 CBattleEngineWalkerPart__GetCurrentWeapon`.
- Source anchors include `references/Onslaught/BattleEngineJetPart.cpp`, `references/Onslaught/BattleEngineWalkerPart.cpp`, and `references/Onslaught/BattleEngine.cpp`.
- Queue closure remains `6246/6246 = 100.00%`.
- Wave911 focused progress advances to `775/1408 = 55.04%`.
- Expanded static surface progress advances to `1097/1509 = 72.70%`.
- Wave911 top-500 coverage remains `500/500 = 100.00%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260601-180430_post_wave1056_battleengine_jet_walker_residual_review_verified`, `19` files, `174656391` bytes, `DiffCount=0`, `HashDiffCount=0`.

Validation command:

```powershell
npm run test:ghidra-wave900-plus-through-wave1056-recheck
```

Boundary note: this aggregate gate is static documentation/evidence hygiene. Runtime flight, skimming, firing, HUD, localization, heat, overheat, zoom, stealth, cloak behavior, exact `CBattleEngine::WeaponFired` identity, `weapon_fire_breaks_stealth`, concrete layout completeness, exact source-body identity, BEA patching behavior, gameplay outcomes, and rebuild parity remain separate proof.

Probe token anchor: Wave1056; battleengine-jet-walker-residual-review-wave1056; 0x004114d0 CBattleEngineJetPart__Gravity; 0x00411500 CBattleEngineJetPart__HandleSkimming; 0x004145a0 CBattleEngineWalkerPart__GetWeaponName; 0x004145d0 CBattleEngineWalkerPart__GetWeaponPhysicsName; 0x00414610 CBattleEngineWalkerPart__GetWeaponIconName; 0x00414630 CBattleEngineWalkerPart__CanWeaponFire; CBattleEngine__GetWeaponName; CBattleEngine__UpdateAutoTargetSetAndFireProjectiles; CText__GetStringById; CBattleEngine__HostileEnvironment; weapon_fire_breaks_stealth; 775/1408 = 55.04%; 1097/1509 = 72.70%; 500/500 = 100.00%; 6246/6246 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260601-180430_post_wave1056_battleengine_jet_walker_residual_review_verified; no mutation.
