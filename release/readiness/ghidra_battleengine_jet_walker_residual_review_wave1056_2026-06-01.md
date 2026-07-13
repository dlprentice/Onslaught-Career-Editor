# Ghidra BattleEngine Jet/Walker Residual Review Wave1056 Readiness Note

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 semantic revalidation:** Historical record; `0x00406560` → `CBattleEngine__HandleLocks` (was `CBattleEngine__UpdateAutoTargetSetAndFireProjectiles`). The original text below remains provenance rather than current semantic authority. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); exact records are in `reverse-engineering/binary-analysis/ghidra-full-reaudit-corrections-2026-07-13.json` and `reverse-engineering/binary-analysis/ghidra-targeted-revalidation-corrections-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Status: complete read-only static re-audit evidence
Date: 2026-06-01
Scope: `battleengine-jet-walker-residual-review-wave1056`

Wave1056 re-read six existing BattleEngine JetPart / WalkerPart residual helpers with source/decompile/xref parity and no mutation. The pass made no Ghidra mutation, no renames, no signature changes, no comment/tag changes, no function-boundary changes, and no executable-byte changes.

Primary target evidence:

| Address | Static read-back evidence |
| --- | --- |
| `0x004114d0 CBattleEngineJetPart__Gravity` | Source `CBattleEngineJetPart::Gravity` returns a small gravity factor when linked main-part energy is zero and otherwise returns `0.0`; decompile reads the main-part field through `this+0x18` and compares `+0xfc` against zero. |
| `0x00411500 CBattleEngineJetPart__HandleSkimming` | Source `CBattleEngineJetPart::HandleSkimming` low-altitude / high-speed skimming shape remains coherent; decompile samples terrain/water-style height context, damps velocity, applies damage, and calls `CBattleEngine__HostileEnvironment`. |
| `0x004145a0 CBattleEngineWalkerPart__GetWeaponName` | Called by `0x0040c550 CBattleEngine__GetWeaponName`; decompile resolves `CBattleEngineWalkerPart__GetCurrentWeapon`, then passes current weapon data language id `+0x3c` to `CText__GetStringById`. |
| `0x004145d0 CBattleEngineWalkerPart__GetWeaponPhysicsName` | Called by `0x0040c570 CBattleEngine__GetWeaponPhysicsName`; decompile returns the current weapon data name pointer through current weapon `+0xa4`. |
| `0x00414610 CBattleEngineWalkerPart__GetWeaponIconName` | Called by `0x0040c590 CBattleEngine__GetWeaponIconName`; decompile returns the current weapon icon-name-like field at current weapon data `+0x38`. |
| `0x00414630 CBattleEngineWalkerPart__CanWeaponFire` | Called by `0x00406560 CBattleEngine__UpdateAutoTargetSetAndFireProjectiles`; decompile checks active current weapon `+0x9c`, store `+0x52c`, heat `+0x55c`, overheat `+0x544`, and capacity `+0x4b0/+0x88`. |

Context anchors include `0x00409f70 CBattleEngine__ChangeWeapon`, `0x0040c2e0 CBattleEngine__CanSpawnBurstForResolvedEntry`, `0x0040c3c0 CBattleEngine__GetWeaponAmmoPercentage`, `0x0040c460 CBattleEngine__GetWeaponAmmoCount`, `0x0040c4a0 CBattleEngine__GetWeaponCharge`, `0x0040c550 CBattleEngine__GetWeaponName`, `0x0040c570 CBattleEngine__GetWeaponPhysicsName`, `0x0040c590 CBattleEngine__GetWeaponIconName`, `0x00410210 CBattleEngineJetPart__ctor`, `0x004102a0 CBattleEngineJetPart__dtor_base`, `0x00411e70 CBattleEngineJetPart__ChangeWeapon`, `0x00412610 CBattleEngineJetPart__GetCurrentWeapon`, `0x00413eb0 CBattleEngineWalkerPart__ChangeWeapon`, and `0x00414030 CBattleEngineWalkerPart__GetCurrentWeapon`.

Read-back evidence:

- Primary exports: `6` metadata rows, `6` tag rows, `7` xref rows, `157` function-body instruction rows, and `6` decompile rows.
- Context exports: `14` metadata rows, `14` tag rows, `48` xref rows, `1142` function-body instruction rows, and `14` decompile rows.
- Queue closure remains `6246/6246 = 100.00%`.
- Wave911 focused progress advances to `775/1408 = 55.04%`.
- Expanded static surface progress advances to `1097/1509 = 72.70%`.
- Wave911 top-500 coverage remains `500/500 = 100.00%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260601-180430_post_wave1056_battleengine_jet_walker_residual_review_verified`, `19` files, `174656391` bytes, `DiffCount=0`, `HashDiffCount=0`.

What this proves:

- The six target functions still exist in the saved Ghidra project with expected names, signatures, and bounded static comments.
- Incoming references still tie WalkerPart HUD/name/fire-gate helpers to the expected BattleEngine dispatch callers.
- Source snippets in `references/Onslaught/BattleEngineJetPart.cpp`, `references/Onslaught/BattleEngineWalkerPart.cpp`, and `references/Onslaught/BattleEngine.cpp` remain coherent with the exported decompile/xref evidence.
- No fresh evidence required a rename, signature rewrite, boundary recovery, or comment/tag mutation.

What remains unproven:

- Runtime flight, skimming, firing, HUD, localization, heat, overheat, zoom, stealth, or cloak behavior.
- Exact `CBattleEngine::WeaponFired` identity or `weapon_fire_breaks_stealth`.
- Concrete `CBattleEngine`, JetPart, WalkerPart, CWeapon, CWeaponData, CText, terrain/map, or store/heat layout completeness beyond observed offsets.
- Exact source-body identity, BEA patching behavior, gameplay outcomes, and rebuild parity.

Probe token anchor: Wave1056; battleengine-jet-walker-residual-review-wave1056; 0x004114d0 CBattleEngineJetPart__Gravity; 0x00411500 CBattleEngineJetPart__HandleSkimming; 0x004145a0 CBattleEngineWalkerPart__GetWeaponName; 0x004145d0 CBattleEngineWalkerPart__GetWeaponPhysicsName; 0x00414610 CBattleEngineWalkerPart__GetWeaponIconName; 0x00414630 CBattleEngineWalkerPart__CanWeaponFire; CBattleEngine__GetWeaponName; CBattleEngine__UpdateAutoTargetSetAndFireProjectiles; CText__GetStringById; CBattleEngine__HostileEnvironment; weapon_fire_breaks_stealth; 775/1408 = 55.04%; 1097/1509 = 72.70%; 500/500 = 100.00%; 6246/6246 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260601-180430_post_wave1056_battleengine_jet_walker_residual_review_verified; no mutation.
