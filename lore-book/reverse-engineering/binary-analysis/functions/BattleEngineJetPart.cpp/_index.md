# BattleEngineJetPart.cpp Function Mappings

> Functions from `references/Onslaught/BattleEngineJetPart.cpp` mapped to `BEA.exe`.

> **Queue status (2026-06-01):** Ghidra export-contract closure **6246/6246** (Wave1056: every current function object commented with clean-signature proxy; not evidence-grade semantics). Lines below that reference a "next raw commentless" row are **archival wave progress**, not open work.

## Overview

- **Functions Mapped:** 23
- **Status:** ACTIVE (source-parity signature correction)
- **Class:** `CBattleEngineJetPart`

## Function List

| Address | Name | Status | Link |
|---------|------|--------|------|
| 0x00410210 | CBattleEngineJetPart__ctor | NAMED/SIGNED | [CBattleEngineJetPart__ctor.md](CBattleEngineJetPart__ctor.md) |
| 0x004102a0 | CBattleEngineJetPart__dtor_base | NAMED/SIGNED | [CBattleEngineJetPart__dtor_base.md](CBattleEngineJetPart__dtor_base.md) |
| 0x00410310 | CBattleEngineJetPart__Thrust | NAMED/SIGNED | [CBattleEngineJetPart__Thrust.md](CBattleEngineJetPart__Thrust.md) |
| 0x00410490 | CBattleEngineJetPart__Turn | NAMED/SIGNED | [CBattleEngineJetPart__Turn.md](CBattleEngineJetPart__Turn.md) |
| 0x00410670 | CBattleEngineJetPart__Pitch | NAMED/SIGNED | [CBattleEngineJetPart__Pitch.md](CBattleEngineJetPart__Pitch.md) |
| 0x00410740 | CBattleEngineJetPart__YawLeft | NAMED/SIGNED | [CBattleEngineJetPart__YawLeft.md](CBattleEngineJetPart__YawLeft.md) |
| 0x004109d0 | CBattleEngineJetPart__YawRight | NAMED/SIGNED | [CBattleEngineJetPart__YawRight.md](CBattleEngineJetPart__YawRight.md) |
| 0x004114d0 | CBattleEngineJetPart__Gravity | NAMED/SIGNED | [CBattleEngineJetPart__Gravity.md](CBattleEngineJetPart__Gravity.md) |
| 0x00411500 | CBattleEngineJetPart__HandleSkimming | NAMED/SIGNED | [CBattleEngineJetPart__HandleSkimming.md](CBattleEngineJetPart__HandleSkimming.md) |
| 0x00411b70 | CBattleEngineJetPart__IsStateMachineActive | NAMED/SIGNED | Wave 306 |
| 0x00411e70 | CBattleEngineJetPart__ChangeWeapon | NAMED/SIGNED | Wave 306 |
| 0x00412000 | CBattleEngineJetPart__LoseWeaponCharge | NAMED/SIGNED | Wave 306 |
| 0x00412050 | CBattleEngineJetPart__WeaponFired | NAMED/SIGNED | Wave 306 |
| 0x004121b0 | CBattleEngineJetPart__GetWeaponAmmoPercentage | NAMED/SIGNED | Wave 306 |
| 0x004122b0 | CBattleEngineJetPart__IsEnergyWeapon | NAMED/SIGNED | Wave 308 |
| 0x00412310 | CBattleEngineJetPart__IsWeaponOverheated | NAMED/SIGNED | Wave 308 |
| 0x00412370 | CBattleEngineJetPart__GetWeaponCharge | NAMED/SIGNED | Wave 306 |
| 0x00412480 | CBattleEngineJetPart__GetWeaponPhysicsName | NAMED/SIGNED | Wave 306 |
| 0x004124d0 | CBattleEngineJetPart__GetCurrentWeaponNameField04 | NAMED/SIGNED | Wave 306 |
| 0x00412520 | CBattleEngineJetPart__GetWeaponIconName | NAMED/SIGNED | Wave 306 |
| 0x00412570 | CBattleEngineJetPart__CanWeaponFire | NAMED/SIGNED | Wave 306 |
| 0x00412610 | CBattleEngineJetPart__GetCurrentWeapon | NAMED/SIGNED | Wave 306 |
| 0x00412650 | CBattleEngineJetPart__ResetConfiguration | NAMED/SIGNED | [CBattleEngineJetPart__ResetConfiguration.md](CBattleEngineJetPart__ResetConfiguration.md) |

## Notes

- Wave1056 (`battleengine-jet-walker-residual-review-wave1056`) re-read `0x004114d0 CBattleEngineJetPart__Gravity` and `0x00411500 CBattleEngineJetPart__HandleSkimming` with no mutation. `CBattleEngineJetPart__Gravity` remains source/decompile coherent with `CBattleEngineJetPart::Gravity`: it returns the small gravity factor when linked main-part energy is zero and otherwise returns `0.0`. `CBattleEngineJetPart__HandleSkimming` remains coherent with the low-altitude/high-speed skimming source path and decompile evidence that calls `CBattleEngine__HostileEnvironment`. The same Wave1056 pass covered WalkerPart accessors/fire gate and BattleEngine dispatch context. Fresh primary exports verified 6 metadata rows, 6 tag rows, 7 xref rows, 157 body-instruction rows, and 6 decompile rows; context exports verified 14 metadata rows, 14 tag rows, 48 xref rows, 1142 instruction rows, and 14 decompile rows. Queue closure remains `6246/6246 = 100.00%`; Wave911 focused progress advances to `775/1408 = 55.04%`; expanded static surface progress advances to `1097/1509 = 72.70%`; top-500 coverage remains `500/500 = 100.00%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260601-180430_post_wave1056_battleengine_jet_walker_residual_review_verified`. Runtime flight/skimming behavior, concrete terrain/map/BattleEngine/JetPart layouts, exact source-body identity, BEA patching, gameplay outcomes, and rebuild parity remain separate proof. Probe token anchor: Wave1056; battleengine-jet-walker-residual-review-wave1056; 0x004114d0 CBattleEngineJetPart__Gravity; 0x00411500 CBattleEngineJetPart__HandleSkimming; 0x004145a0 CBattleEngineWalkerPart__GetWeaponName; 0x004145d0 CBattleEngineWalkerPart__GetWeaponPhysicsName; 0x00414610 CBattleEngineWalkerPart__GetWeaponIconName; 0x00414630 CBattleEngineWalkerPart__CanWeaponFire; CBattleEngine__GetWeaponName; CBattleEngine__UpdateAutoTargetSetAndFireProjectiles; CText__GetStringById; CBattleEngine__HostileEnvironment; weapon_fire_breaks_stealth; 775/1408 = 55.04%; 1097/1509 = 72.70%; 500/500 = 100.00%; 6246/6246 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260601-180430_post_wave1056_battleengine_jet_walker_residual_review_verified; no mutation.
- Wave1029 (`battleengine-jetpart-weapon-status-review-wave1029`) re-read the JetPart weapon/status/accessor/reset spine with no mutation. Primary anchors were `0x00411e70 CBattleEngineJetPart__ChangeWeapon`, `0x00412050 CBattleEngineJetPart__WeaponFired`, `0x004122b0 CBattleEngineJetPart__IsEnergyWeapon`, `0x00412310 CBattleEngineJetPart__IsWeaponOverheated`, and `0x00412650 CBattleEngineJetPart__ResetConfiguration`, with all thirteen weapon rows from `0x00411e70` through `0x00412650` covered. Fresh exports verified 13 primary metadata rows, 13 tag rows, 19 xref rows, 790 body-instruction rows, 13 decompile rows, 11 context metadata rows, 11 context tag rows, 20 context xref rows, 1583 context body-instruction rows, and 11 context decompile rows. Queue closure remains `6238/6238 = 100.00%`; Wave911 focused progress is `618/1408 = 43.89%`; expanded static surface progress is `847/1493 = 56.73%`; top-500 coverage remains `500/500 = 100.00%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260601-025247_post_wave1029_battleengine_jetpart_weapon_status_review_verified`. Runtime firing, charging, HUD, audio, heat, overheat, zoom, stealth, cloak behavior, exact `CBattleEngine::WeaponFired` identity, `weapon_fire_breaks_stealth`, exact layouts, BEA patching, gameplay outcomes, and rebuild parity remain separate proof.
- Wave974 (`battleengine-jet-animation-review-wave974`) re-read `0x00410310 CBattleEngineJetPart__Thrust`, `0x00410490 CBattleEngineJetPart__Turn`, and `0x00410670 CBattleEngineJetPart__Pitch` while recovering the source-backed caller boundary `0x004d3110 CPlayer__ReceiveButtonAction`. Fresh xrefs now resolve Player input dispatch into JetPart turn/pitch/thrust/yaw helpers from `0x004d3110`; final post exports verified 7 metadata rows, 7 tag rows, 10 xref rows, 749 body-instruction rows, and 7 decompile rows. Wave911 focused re-audit progress is `356/1408 = 25.28%`; expanded static surface progress is `415/1467 = 28.29%`; export-contract closure is `6211/6211 = 100.00%`. Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260528-210511_post_wave974_battleengine_jet_animation_review_verified`. Exact `CPlayer`, `CController`, `CBattleEngine`, walker-part, and jet-part layouts, exact button enum names, runtime controller/input behavior, camera behavior, jet flight feel, animation behavior, BEA patching, and rebuild parity remain separate proof. Probe token anchor: Wave974; battleengine-jet-animation-review-wave974; 0x004d3110 CPlayer__ReceiveButtonAction; 0x00410310 CBattleEngineJetPart__Thrust; 0x00410490 CBattleEngineJetPart__Turn; 0x00410670 CBattleEngineJetPart__Pitch; 356/1408 = 25.28%; 415/1467 = 28.29%; 6211/6211 = 100.00%; [maintainer-local-ghidra-backup-root]\BEA_20260528-210511_post_wave974_battleengine_jet_animation_review_verified; function-boundary recovery.
- Wave948 read-only review (`battleengine-transition-effects-review-wave948`) refreshed BattleEngine transition/effects bridge evidence for `0x004124d0 CBattleEngineJetPart__GetCurrentWeaponNameField04` with context anchors `0x00409f70 CBattleEngine__ChangeWeapon`, `0x00411e70 CBattleEngineJetPart__ChangeWeapon`, `0x00412520 CBattleEngineJetPart__GetWeaponIconName`, `0x00412570 CBattleEngineJetPart__CanWeaponFire`, and `0x00412610 CBattleEngineJetPart__GetCurrentWeapon`. Fresh xrefs keep `0x004124d0` tied to `CBattleEngine__ChangeWeapon`; the decompile still returns selected weapon definition/context field `+0x04`, so no mutation or source-accessor rename was justified. Focused Wave911 re-audit progress after Wave948 is `247/1408 = 17.54%`; static export-contract closure remains `6150/6150 = 100.00%`; verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260528-073152_post_wave948_battleengine_transition_effects_review_verified`. Runtime weapon switching, HUD audio behavior, concrete layouts, BEA patching, and rebuild parity remain unproven.
- Wave925 read-only review (`battleengine-jetpart-movement-review-wave925`) refreshed metadata/tags/xrefs/instructions/decompile for `0x00410310 CBattleEngineJetPart__Thrust`, `0x00410490 CBattleEngineJetPart__Turn`, `0x00410670 CBattleEngineJetPart__Pitch`, `0x00410740 CBattleEngineJetPart__YawLeft`, `0x004109d0 CBattleEngineJetPart__YawRight`, and `0x00411b70 CBattleEngineJetPart__IsStateMachineActive`, plus BattleEngine context `0x00409e80 CBattleEngine__AutoZoomOut`. No mutation was needed. Focused Wave911 re-audit progress after Wave925 is `96/1408 = 6.82%`; static export-contract closure remains `6113/6113 = 100.00%`; verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260527-223000_post_wave925_battleengine_jetpart_movement_review_verified`. Runtime jet input, zoom, morph/controller dispatch, concrete layouts, BEA patching, and rebuild parity remain unproven.
- Wave304 saved nine `CBattleEngineJetPart` source-parity corrections: constructor, destructor-base, thrust, turn, pitch, yaw-left, yaw-right, gravity, and skimming/hostile-environment context.
- The wave supersedes stale `CBattleEngine`, `CGeneralVolume`, and `CMonitor` owner labels for those selected addresses.
- Three corrected bodies still have local decompiler artifacts (`0x00410490`, `0x00410670`, `0x00411500`), so local/type cleanup remains open even though owner/name/signature read-back is improved.
- Wave306 corrected thirteen stale owner labels in the JetPart weapon-helper cluster, including `ChangeWeapon`, `WeaponFired`, HUD/accessor helpers, `CanWeaponFire`, and `GetCurrentWeapon`.
- Wave306 keeps `CBattleEngineJetPart__WeaponFired` and `CBattleEngineJetPart__CanWeaponFire` bounded to static JetPart helper evidence only; exact retail `CBattleEngine::WeaponFired`, `weapon_fire_breaks_stealth`, and runtime fire-while-cloaked behavior remain unproven.
- Wave308 corrected the JetPart heat/energy helper swap: `0x004122b0` is the `+0x55c` energy-weapon predicate and `0x00412310` is the `+0x544` overheat-style predicate.
- Wave305 hardened `CBattleEngineJetPart__ResetConfiguration` from `void * param_1` register-parameter debt to a source-aligned `void * this` member signature.
- Wave262 saved `CBattleEngineJetPart__ResetConfiguration` after source/decompile/xref read-back: the checked body drains old jet-part weapons, creates profile-selected weapons, initializes them, and resets the current weapon index.
- Local names, structure types, tags, and runtime behavior remain deferred.

## Related

- Source: `references/Onslaught/BattleEngineJetPart.cpp`
- Parent: [../_index.md](../_index.md)
