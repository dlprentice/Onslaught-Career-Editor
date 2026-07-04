# Ghidra GeneralVolume Param Tail Wave475 Readiness

Date: 2026-05-17

## Scope

Wave475 saved bounded Ghidra signature/comment/tag corrections for:

- `0x00411b90` `CGeneralVolume__DispatchSelectedBurstPreset`
- `0x00411bf0` `CGeneralVolume__DispatchMode3BurstProgressAndSpawn`
- `0x00412240` `CGeneralVolume__GetMode3CurrentEntryRoundedSlotValue`
- `0x00412420` `CGeneralVolume__GetMode3CurrentEntryDisplayString`
- `0x00412830` `CGeneralVolume__DisableLinkedEntriesByNameAndReselect`
- `0x00413660` `CGeneralVolume__ApplyYawInputByWeaponClass`
- `0x004136e0` `CGeneralVolume__ApplyPitchInputByWeaponClass`

## Evidence

- Pre/post artifacts: `subagents/ghidra-static-reaudit/wave475-generalvolume-param-tail/`
- Apply script: `tools/ApplyGeneralVolumeParamTailWave475.java`
- Focused probe: `tools/ghidra_generalvolume_param_tail_wave475_probe.py`
- Probe test: `tools/ghidra_generalvolume_param_tail_wave475_probe_test.py`
- Function docs: `reverse-engineering/binary-analysis/functions/GeneralVolume.cpp/`

## Result

`ApplyGeneralVolumeParamTailWave475.java` reported:

- Dry: `updated=0 skipped=7 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`
- Apply: `updated=7 skipped=0 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`
- Verify dry: `updated=0 skipped=7 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`
- Save: `REPORT: Save succeeded`

Saved signatures:

```c
void __fastcall CGeneralVolume__DispatchSelectedBurstPreset(void * general_volume);
void __fastcall CGeneralVolume__DispatchMode3BurstProgressAndSpawn(void * general_volume);
int __fastcall CGeneralVolume__GetMode3CurrentEntryRoundedSlotValue(void * general_volume);
short * __fastcall CGeneralVolume__GetMode3CurrentEntryDisplayString(void * general_volume);
void __thiscall CGeneralVolume__DisableLinkedEntriesByNameAndReselect(void * this, char * entry_name);
void __thiscall CGeneralVolume__ApplyYawInputByWeaponClass(void * this, int axis_input);
void __thiscall CGeneralVolume__ApplyPitchInputByWeaponClass(void * this, int axis_input);
```

Read-back verified `7` metadata rows, `7` tag rows, `7` xref rows, `7` target decompile exports plus `index.tsv`, `623` instruction rows, `87` focused disassembly rows for `0x00412830`, `33` focused axis-caller rows, and focused probe status `PASS`.

## Boundary

This is static retail-binary evidence only. Runtime selected-weapon behavior, runtime HUD display behavior, runtime yaw/pitch control behavior, exact `CGeneralVolume`/entry/BattleEngine layouts, exact source identities, BEA launch behavior, game patching, and rebuild parity remain unproven.

## Queue Snapshot

Fresh queue after Wave475:

- Function objects: `6057`
- Functions with comments: `2152`
- Commentless functions: `3905`
- Undefined signatures: `1702`
- `param_N` signatures: `1557`
- Comment-backed proxy: `2152/6057 = 35.53%`
- Strict comment-plus-clean-signature proxy: `2096/6057 = 34.60%`

These percentages are telemetry only, not certification.

## Backup

Verified saved-project backup:

```text
[maintainer-local-ghidra-backup-root]\BEA_20260517-001036_post_wave475_generalvolume_param_tail_verified
SourceCount 19
BackupCount 19
BackupBytes 157223815
MissingCount 0
ExtraCount 0
HashDiffCount 0
```
