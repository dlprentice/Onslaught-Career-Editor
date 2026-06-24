# BattleEngine Level Configuration Index - 2026-05-08

Status: public-safe derived read-only level-resource evidence, not runtime activation proof

## Objective

Index the local numeric level-resource corpus for Battle Engine configuration tables so the next copied-profile runtime proof can choose setup targets from resource data instead of guessing from a single level.

## Probe

Command:

```powershell
npm run test:battleengine-level-configuration-index
```

Equivalent direct command:

```powershell
py -3 tools\battleengine_level_configuration_index_probe.py --check
```

Result on the local read-only game install:

```text
BattleEngine level configuration index probe
Status: pass
Resource root: data/Resources
Levels with configuration tables: 66
Base Sniper levels: 710, 720, 731, 732
Runtime Sniper table levels: 710, 720, 731, 732, 741, 742, 800, 850, 851, 852, 853, 854, 855, 857, 859, 860, 861, 862, 863, 864, 865, 866
```

The probe writes only a derived JSON summary under ignored `subagents/battleengine-level-configuration-index/current/`. It does not copy or commit source archives.

## What This Proves

- The local numeric `*_res_PC.aya` corpus can be scanned for `WRES -> WRLD` BattleEngine configuration tables.
- 66 numeric level resources expose at least one base-world or runtime-world configuration table.
- Base-world `Sniper` appears only in levels `710`, `720`, `731`, and `732` on this install.
- Runtime-world configuration tables include `Sniper` for levels `710`, `720`, `731`, `732`, `741`, `742`, `800`, `850`, `851`, `852`, `853`, `854`, `855`, `857`, `859`, `860`, `861`, `862`, `863`, `864`, `865`, and `866`.
- Base-world configuration distribution from the structural header tables:

| Base configuration | Levels |
| --- | --- |
| `Blaster` | `221`, `222`, `521`, `522`, `523`, `524`, `853`, `857`, `859`, `865`, `866`, `904`, `905` |
| `Laser` | `400`, `411`, `412`, `431`, `432`, `511` |
| `Paladin Prototype` | `100`, `110`, `860`, `863`, `901` |
| `Sniper` | `710`, `720`, `731`, `732` |
| `Standard` | `300`, `311`, `312`, `321`, `322`, `903` |

## Runtime Implication

Level `710` remains a good first cloak runtime target because it has base-world `Sniper` evidence and a Sniper-gated cloak tutorial script. If the next copied-profile observer still cannot observe activation there, levels `720`, `731`, and `732` are the next strongest static setup candidates before falling back to levels where `Sniper` appears only in the runtime table.

## Not Proven

- Runtime selection of any configuration in a managed `BEA.exe` process.
- Runtime cloak activation.
- Fire-while-cloaked behavior.
- Goodies unlock criteria or in-game Goodies model-viewer behavior.

## Privacy / Release Safety

This report is public-safe. It contains only derived level numbers, chunk/table names, and configuration names. It does not include raw resource bytes, copied saves, copied executables, debugger logs, screenshots, private absolute paths, or runtime proof JSON.
