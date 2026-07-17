# BattleEngineConfigurations__GetConfiguration

> Address: `0x0040f2f0` | Source family: `references/Onslaught/BattleEngineConfigurations.cpp`

## Status

- Named in Ghidra: yes
- Saved signature: `void * __cdecl BattleEngineConfigurations__GetConfiguration(int configurationId)`
- Static authority: [Ghidra reference](../../GHIDRA-REFERENCE.md)
- Runtime behavior proof: not yet

## Summary

BattleEngine configuration lookup helper matching `UBattleEngineConfigurations::GetConfiguration(int)`: bounds-checks the supplied configuration id, selects a configuration name from the global table, asks the BattleEngine data manager for that named configuration, and falls back to the default configuration when the named lookup fails.

The current Ghidra correction supersedes the stale `CBattleEngine__GetWeaponProfileByIndex` label.

## Evidence

- Source anchor: `UBattleEngineConfigurations::GetConfiguration(int)` in `references/Onslaught/BattleEngineConfigurations.cpp`.
- Read-back tokens include global configuration count `0x00660250`, configuration-name table `0x00660200`, data-manager list root/current cursor context around `0x006602a0/0x006602a8`, and string compare against data entries at `+0xa8`.
- Saved signature models the function as a cdecl one-argument static helper returning an opaque configuration pointer.

## Boundaries

- Does not prove concrete `CBattleEngineData` layout or full data-manager structure typing.
- Does not prove runtime profile/configuration behavior.
- Does not mutate `BEA.exe`.
- Does not close rebuild parity.
