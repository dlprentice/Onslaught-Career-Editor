# BattleEngine Level Configuration - 2026-05-08

Status: public-safe derived read-only level-resource evidence, not runtime activation proof

## Objective

Find a safer setup target for the next copied-profile cloak runtime observer by checking whether level 710 actually carries the Sniper Battle Engine configuration path.

The previous profile-data pass proved `Sniper` is the only retail Battle Engine profile with positive `mStealth` (`80.0`). This pass checks the local level 710 resource archive and the tracked mission script for Sniper-specific configuration evidence before any new runtime launch.

## Probe

Command:

```powershell
npm run test:battleengine-level-configuration
```

Equivalent direct command:

```powershell
py -3 tools\battleengine_level_configuration_probe.py --check
```

Result on the local read-only game install:

```text
BattleEngine level configuration probe
Status: pass
Level: 710
Resource: data/Resources/710_res_PC.aya
WDAT: {'levelNumber': 710, 'worldDataVersion': 8}
BSWD header configuration table: Sniper
RLWD header configuration table: Standard, Sniper, Laser, Blaster
BSWD configuration hits: Sniper
RLWD configuration table: Standard, Sniper, Laser, Blaster
RLWD all configuration-name hits: Standard, Sniper, Laser, Blaster, Sniper
```

The probe writes only a derived JSON summary under ignored `subagents/battleengine-level-configuration/current/`. It does not copy or commit the source archive.

## What This Proves

- The local read-only `data/Resources/710_res_PC.aya` archive inflates and contains `WRES -> WRLD` world data.
- `WDAT` identifies the resource as level `710`.
- The base-world header (`BSWD`) carries a structural `BattleEngineConfigurations` table containing only `Sniper`.
- The runtime-level header (`RLWD`) carries a structural `BattleEngineConfigurations` table containing `Standard`, `Sniper`, `Laser`, `Blaster`.
- `RLWD` also contains a second `Sniper` string from compiled mission-script constants.
- The runtime-level world data references `Level710script`.
- The tracked mission script gates cloak tutorial text on `player.GetConfiguration() == "Sniper"`.

## Loader Read-Back Bridge

Read-only Ghidra headless export was run against the current local project for:

- `0x0050d4c0` / `CWorld__LoadWorldHeader`
- `0x0050dcb0` / `CWorld__SpawnInitialThings`
- `0x0040f180` / `BattleEngineConfigurations__Load`
- `0x0040f260` / `BattleEngineConfigurations__Skip`

The ignored output lives under `subagents/battleengine-level-configuration/ghidra-world-helpers/`. It shows:

- `CWorld__LoadWorldHeader` reads the world header and delegates the length-prefixed Battle Engine configuration table to `BattleEngineConfigurations__Load` or `BattleEngineConfigurations__Skip`.
- `BattleEngineConfigurations__Load` stores up to 20 configuration-name pointers in the global config table at `0x00660200` with count at `0x00660250`.
- `CWorld__SpawnInitialThings` resolves an initial Battle Engine configuration string through that global table and writes the matched index to `CBattleEngineInitThing +0x3bc`, which corresponds to `mConfigurationId` immediately after the `CInitThing` base.

This closes the runtime init-object assignment gap for the initial-spawn configuration path. It does not prove that a managed runtime session reaches the `Sniper` profile; that still needs a copied-profile observer.

## Not Proven

- Any alternate per-unit serialized numeric configuration-id offset beyond the initial-spawn string-resolution path.
- A runtime transition into `Sniper` in the retail executable.
- Runtime cloak activation.
- Whether firing while cloaked breaks or preserves stealth.
- Any mutation of game files, Ghidra projects, copied profiles, saves, or runtime state.

## Next Runtime Implication

Level 710 remains the best first runtime setup target for cloak observation, but the next copied-profile observer should explicitly verify the active Battle Engine configuration before sending cloak input. If runtime memory still reports a zero-stealth profile on level 710, the follow-up should inspect the serialized `WRES` configuration ID or the level-loading path rather than guessing another input binding.

## Privacy / Release Safety

This report is public-safe. It contains only derived chunk names, configuration names, scalar resource metadata, and mission-script line-token evidence. It does not include raw resource bytes, copied saves, copied executables, debugger logs, screenshots, private absolute paths, or runtime proof JSON.
