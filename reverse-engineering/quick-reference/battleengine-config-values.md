Status: active quick reference
Last updated: 2026-04-29
Source: migrated from archived Codex Onslaught skills during the skill clean-slate pass.
Summary: BattleEngine default config and combat/movement constants.
# BattleEngine Default Configuration Values

Default values set in `CBattleEngineData::Initialise()`:

## Combat Stats

| Property | Default Value | Description |
|----------|---------------|-------------|
| `mLife` | 20.0 | Maximum health points |
| `mEnergy` | 2.5 | Maximum energy (also max shields in walker) |
| `mShieldEfficiency` | 90.0 | Percentage of damage absorbed by shields |
| `mStealth` | 0 | Stealth rating (reduces enemy lock range) |

## Velocity

| Property | Default Value | Description |
|----------|---------------|-------------|
| `mMaxAirVelocity` | 7.5 | Maximum jet mode speed |
| `mMinAirVelocity` | 5.0 | Minimum jet mode speed |
| `mGroundVelocity` | 4.0 | Walker mode movement speed |
| `mMaxWalkVelocity` | 0.15 | Maximum walker velocity |
| `mWalkFriction` | 0.9 | Walker movement friction |

## Turn Rates

| Property | Default Value | Description |
|----------|---------------|-------------|
| `mAirTurnRate` | 2.0 | Jet mode rotation speed |
| `mGroundTurnRate` | 1.5 | Walker mode rotation speed |

## Energy Costs

| Property | Default Value | Description |
|----------|---------------|-------------|
| `mGroundEnergyIncrease` | 0.01 | Energy regen per tick on ground |
| `mMinAirEnergyCost` | 0.1 | Energy drain at minimum thrust |
| `mMaxAirEnergyCost` | 0.3 | Energy drain at maximum thrust |
| `mMinTransformEnergy` | 1.0 | Energy required to transform to jet |
| `mRollEnergyCost` | 1.0 | Energy cost for barrel roll |
| `mLoopEnergyCost` | 1.0 | Energy cost for loop maneuver |

## Default Weapons

### Walker Mode
1. "Vulcan Cannon 1"
2. "Pulse Cannon Pod"

### Jet Mode
1. "Vulcan Cannon 1"
2. "Missile Pod"

### Special Weapons
| Property | Default Value |
|----------|---------------|
| `mPrimaryWeapon` | (empty) |
| `mAugWeapon` | (empty) |

## Weapon Stores

6 stores, each with:
- `mStoreHeat[n]` = false (ammo-based by default)
- `mStoreValue[n]` = 1000 (ammo/heat capacity)

## Assets

| Property | Default Value |
|----------|---------------|
| `mConfigurationName` | "Standard" |
| `mExplosion` | "Animated Explosion Emitter 2" |
| `mCockpit` | "cockpit2.msh" |
| `mLanguageName` | 1 |

## Constants

| Constant | Value | Description |
|----------|-------|-------------|
| `kCurrentBattleEngineDataFormat` | 12 | File format version |
| `kBattleEngineStores` | 6 | Number of weapon stores |
| `kMaxConfigurations` | 20 | Maximum configuration slots |

## Source-To-Retail Layout Candidate

`tools\battleengine_profile_layout_candidate_probe.py` validates the current source-to-retail profile layout candidate from Stuart source field order, x86 `GenericSPtrSet` shape, and existing read-only retail decompiles.

| Source field | Candidate retail profile offset | Current evidence |
| --- | ---: | --- |
| `mLife` | `+0x1c` | Retail profile apply copies profile `+0x1c` into the current life-like state. |
| `mEnergy` | `+0x20` | Retail profile apply and recharge paths consume profile `+0x20` as the max/current energy-like value. |
| `mGroundEnergyIncrease` | `+0x28` | Retail walker recharge path consumes profile `+0x28` as the recharge-like value. |
| `mMinTransformEnergy` | `+0x2c` | Retail cloak helper gates profile `+0x2c <= current energy`, matching the source transform/activation energy gate family. |
| `mStoreValue[0]` | `+0x88` | Retail per-slot readiness uses profile `+0x88 + slot * 4`. |
| `mStealth` | `+0xa0` | Source `Cloak()` gates on `mStealth > 0`; retail cloak helper gates on profile `+0xa0 > 0`. |
| `mLanguageName` | `+0xa4` | Source x86 layout places it immediately after `mStealth`. |
| `mConfigurationName` | `+0xa8` | Retail profile apply prints the profile name from `+0xa8`. |

This layout candidate does not prove all retail profile values or runtime cloak activation. It is strong enough to direct the next runtime wave toward selecting or identifying a profile with positive profile `+0xa0` before testing fire-while-cloaked behavior.

## Retail Profile Data Snapshot

`tools\battleengine_profile_data_probe.py` parses the local retail `data/battle engine configurations.dat` file read-only using the source loader order. On the current verified install it found six profiles and one positive-stealth profile:

| Profile | `mStealth` / profile `+0xa0` | Runtime implication |
| --- | ---: | --- |
| Racer | `0.0` | Not a cloak activation target. |
| Standard | `0.0` | Not a cloak activation target. |
| Sniper | `80.0` | Positive-stealth profile; next cloak runtime observer target. |
| Aquila Prototype | `0.0` | Not a cloak activation target. |
| Laser | `0.0` | Not a cloak activation target. |
| Blaster | `0.0` | Not a cloak activation target. |

This snapshot is derived evidence only. It does not prove that a runtime session has selected `Sniper`, and it does not prove cloak activation until the copied-profile observer sees the latch pass in a managed runtime run.

## Level 710 Configuration Evidence

`tools\battleengine_level_configuration_probe.py` inspects the local read-only
`data/Resources/710_res_PC.aya` level resource archive and the tracked
`Level710script.msl` evidence.

Derived findings:

- `WRES -> WRLD -> WDAT` identifies level `710`.
- `BSWD` has a structural `BattleEngineConfigurations` header table containing
  only `Sniper`.
- `RLWD` has a structural `BattleEngineConfigurations` header table containing
  `Standard`, `Sniper`, `Laser`, `Blaster`.
- `RLWD` references `Level710script`.
- `Level710script.msl` gates cloak tutorial text on
  `player.GetConfiguration() == "Sniper"`.

Read-only Ghidra headless export of `CWorld__LoadWorldHeader` and
`CWorld__SpawnInitialThings` shows that the header config table is loaded by
`BattleEngineConfigurations__Load`, then initial BattleEngine spawn records are
resolved against that table and written to `CBattleEngineInitThing +0x3bc`
(`mConfigurationId`). This is setup evidence only; it does not yet prove a
runtime transition into `Sniper`.

## Level Configuration Corpus Index

`tools\battleengine_level_configuration_index_probe.py` scans the local
read-only `data/Resources/*_res_PC.aya` numeric level corpus and parses the same
structural header tables.

Current derived findings:

- 66 numeric level resources expose at least one base-world or runtime-world
  configuration table.
- Base-world `Sniper` appears only in levels `710`, `720`, `731`, and `732`.
- Runtime-world tables include `Sniper` for levels `710`, `720`, `731`, `732`,
  `741`, `742`, `800`, `850`, `851`, `852`, `853`, `854`, `855`, `857`, `859`,
  `860`, `861`, `862`, `863`, `864`, `865`, and `866`.

This narrows the next copied-profile cloak observer target list. It does not
prove runtime configuration selection or cloak activation.
