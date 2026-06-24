# BattleEngine Profile Data - 2026-05-08

Status: public-safe derived read-only retail data evidence, not runtime activation proof

## Objective

Identify a concrete positive-stealth BattleEngine profile before running more copied-profile runtime cloak input.

The previous layout probe showed retail profile `+0xa0` is a strong source-compatible `CBattleEngineData::mStealth` candidate. This pass parses the installed retail profile data file read-only and asks which profile actually has positive stealth.

## Probe

Command:

```powershell
npm run test:battleengine-profile-data
```

Equivalent direct command:

```powershell
py -3 tools\battleengine_profile_data_probe.py --check
```

Result on the local read-only game install:

```text
BattleEngine profile data probe
Status: pass
Data path: data/battle engine configurations.dat
Profiles: 6
Positive stealth profiles:
- Sniper: 80.0
```

The probe writes only a derived JSON summary under ignored `subagents/battleengine-profile-data/current/`. It does not copy or commit the source data file.

## What This Proves

- The local retail `data/battle engine configurations.dat` parses as six `CBattleEngineData` entries with no trailing bytes using the source loader order.
- The six parsed profiles are `Racer`, `Standard`, `Sniper`, `Aquila Prototype`, `Laser`, and `Blaster`.
- `Sniper` is the only parsed profile with positive `mStealth` / profile `+0xa0`, with value `80.0`.
- The next copied-profile runtime cloak observer should select or verify the `Sniper` profile before attempting cloak activation again.

## Not Proven

- How the latest runtime selected the previous non-stealth profile.
- A runtime transition into the `Sniper` profile.
- Runtime cloak activation.
- Whether firing while cloaked breaks or preserves stealth.
- Any mutation of game files, Ghidra projects, copied profiles, or saves.
- Rebuildable gameplay implementation parity.

## Privacy / Release Safety

This report is public-safe. It contains only derived profile names and scalar values needed to document proof direction. It does not include raw binary bytes, the private source file, copied saves, copied executables, debugger logs, screenshots, private absolute paths, or runtime proof JSON.
