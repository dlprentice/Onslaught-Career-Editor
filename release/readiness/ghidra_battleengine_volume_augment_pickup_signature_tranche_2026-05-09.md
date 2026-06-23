# Ghidra BattleEngine Volume / Augment / Pickup Signature Tranche - 2026-05-09

Status: public-safe saved-Ghidra name/signature evidence

## Summary

This wave reparsed six already named `0x0040dc30` to `0x0040dfb0` functions after fresh metadata, decompile, xref, and instruction read-back. Four saved owner labels were stale or too broad, and all six signatures/comments needed a stronger proof boundary.

A serial headless dry/apply pass saved corrected names, signatures, and comments. Fresh read-back plus a focused probe then verified the saved state.

## Corrected Targets

| Address | Previous state | Saved state after correction | Evidence boundary |
| --- | --- | --- | --- |
| `0x0040dc30` | `CExplosionInitThing__EnableVolumeEntryGroupsByName` | `void __thiscall CBattleEngine__EnableVolumeEntryGroupsByName(void * this, void * entryName)` | Dispatches BattleEngine volume-entry groups at `+0x578` and `+0x57c` by name. Runtime behavior and concrete layout remain unproven. |
| `0x0040dc60` | `CExplosionInitThing__DisableVolumeEntryGroupsByNameAndReselect` | `void __thiscall CBattleEngine__DisableVolumeEntryGroupsByNameAndReselect(void * this, void * entryName)` | Dispatches disable/reselect paths for the same BattleEngine volume-entry groups. Runtime behavior and concrete layout remain unproven. |
| `0x0040dcc0` | `CMonitor__ResetTransitionFlagAndUpdateIfState3_Thunk` | `void __thiscall CBattleEngine__ClearFlag58CAndMorphIfState3(void * this)` | Clears `+0x58c`, checks state `+0x260 == 3`, then tail-jumps to `CBattleEngine__Morph` only in that state. Runtime transform behavior remains unproven. |
| `0x0040dda0` | `CUnitAI__RefreshGridCooldownFromOccupiedCells` with stale parameter debt | `void __thiscall CUnitAI__RefreshGridCooldownFromOccupiedCells(void * this)` | Refreshes `+0x2e8` from current-world grid samples; owner/source identity remains provisional. |
| `0x0040de40` | `CMonitor__HandleTargetStateChangeAndHudPrompt` | `void __thiscall CBattleEngine__AugmentWeapon(void * this)` | Strong static bridge to Stuart `CBattleEngine::AugmentWeapon()` through selected weapon paths, aug timestamps, `MAX_AUG_VALUE` `10.0`, aug-active flag, and `hud_weapon_augmented`. Runtime augmented-weapon behavior remains unproven. |
| `0x0040dfb0` | `CGeneralVolume__SpawnPickupAndDispatch` with stale parameter debt | `void __thiscall CGeneralVolume__SpawnPickupAndDispatch(void * this)` | Resolves pickup name context, creates a pickup, initializes an influence/launch stack object, copies position fields, and dispatches the created pickup when available. Runtime pickup behavior remains unproven. |

## Validation

- Focused tests: `py -3 tools\ghidra_battleengine_volume_augment_pickup_signature_tranche_probe_test.py` passed `2/2`.
- Python compile: `py -3 -m py_compile tools\ghidra_battleengine_volume_augment_pickup_signature_tranche_probe.py tools\ghidra_battleengine_volume_augment_pickup_signature_tranche_probe_test.py` passed.
- Headless dry/apply: `updated=0 skipped=6 missing=0 bad=0`, then `updated=6 skipped=0 missing=0 bad=0`.
- Fresh metadata/decompile read-back: `6/6` targets.
- Fresh xref read-back: `8` rows.
- Fresh instruction read-back: `5406` rows.
- Focused probe: `cmd.exe /c npm run test:ghidra-battleengine-volume-augment-pickup-signature-tranche` passed with `6` targets, `4` corrected names, and `6` hardened signatures.

## Non-Claims

This is saved Ghidra name/signature/comment refinement only. It does not prove concrete BattleEngine, CUnitAI, GeneralVolume, pickup, volume-entry, or augmented-weapon layouts; exact source identity for every target; runtime augmented-weapon behavior; runtime pickup behavior; runtime transform behavior; exact retail `CBattleEngine::WeaponFired`; `weapon_fire_breaks_stealth`; BEA launch behavior; game patching; tags/local names/types; or rebuild parity.

## Privacy / Release Safety

This note includes repo-relative paths, public addresses, function names, aggregate counts, command summaries, and proof boundaries only. Raw decompile output, screenshots, frame data, copied saves, copied executables, private install paths, and generated JSON remain under ignored `subagents/`.
