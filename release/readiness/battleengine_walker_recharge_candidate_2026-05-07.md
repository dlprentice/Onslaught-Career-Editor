# BattleEngine Walker Recharge Candidate - 2026-05-07

Status: public-safe bounded read-only retail-candidate evidence, not exact walker method identity or runtime proof

## Objective

Narrow the remaining source-only `walker_recharge` gap.

Source `CBattleEngineWalkerPart::Move()` recharges walker energy when the Battle Engine has been recently grounded, is not in the infinite-energy path, and is not cloaked. It uses `mGroundEnergyIncrease`, halves the rate when shields are not recharging, caps energy to the configured maximum, then mirrors shields to energy. This pass checks the strongest current retail helper for a source-compatible recharge cluster.

## Inputs

Fresh ignored Ghidra headless export:

```text
subagents/battleengine-walker-recharge-candidate/current/decompile/
```

The export reported targets `9`, dumped `9`, missing `0`, failed `0`. The candidate probe focuses on:

```text
0x00413760 CMonitor__ProcessTrackingAndSurfaceAlignment
```

The pass also used a read-only private local constant scan from the known Steam `BEA.exe` specimen for:

```text
0x005d85ec -> 0.5
0x005d8cb4 -> 0.30000001192092896
```

Raw decompile output, constant JSON, and generated probe JSON remain ignored/private under `subagents/`.

## Probe

Command:

```powershell
npm run test:battleengine-walker-recharge-candidate
```

Equivalent direct command:

```powershell
py -3 tools\battleengine_walker_recharge_candidate_probe.py --check
```

Result:

```text
BattleEngine walker recharge candidate probe
Status: pass
Source tokens: 8/8
Decompile tokens: 12/12
```

The probe checks:

- source `CBattleEngineWalkerPart::Move()` recent-ground recharge tokens
- source infinite-energy and cloaked exclusions
- source `mGroundEnergyIncrease`, half-rate recharge, max-energy cap, and shield/energy mirror tokens
- current decompile index row for `0x00413760 CMonitor__ProcessTrackingAndSurfaceAlignment`
- retail recent-ground gate using `DAT_00672fd0` and `_DAT_005d8cb4`
- two retail exclusion flags before recharge
- retail config-rate load from `config + 0x28`
- retail half-rate multiplier `_DAT_005d85ec`
- retail addition to the energy-like field at `+0xfc`
- retail cap against `config + 0x20`
- retail mirror from `+0xfc` into the adjacent shield-like field at `+0x100`
- line ordering for gate, add, cap, and mirror

## What This Proves

- Source `CBattleEngineWalkerPart::Move()` still contains recent-ground recharge, infinite-energy/cloak exclusions, ground-energy-increase addition, half-rate recharge after weapon use, max-energy cap, and shield/energy mirror tokens.
- Fresh read-only `CMonitor__ProcessTrackingAndSurfaceAlignment` decompile contains a source-compatible recent-ground gate, two exclusion flags, config-rate addition, half multiplier, max cap, and shield/energy mirror cluster.
- The read-only constant scan maps `_DAT_005d8cb4` to `0.3` and `_DAT_005d85ec` to `0.5` in `.rdata`.
- `walker_recharge` can now be tracked as a partial retail candidate, not a fully source-only gap.

## What This Does Not Prove

- Exact source-to-retail identity for `CBattleEngineWalkerPart::Move()`.
- Exact semantic names for the retail flags at offsets `0x160`, `0x4ac`, or the state at `param_1 + 0x14`.
- Runtime walker recharge behavior.
- Cloak energy gate, forced decloak, render flag, or weapon-fired stealth reset identity.
- Ghidra rename-map mutation.
- Rebuildable open-source gameplay implementation.

## Privacy / Release Safety

The committed report is public-safe. It does not include binaries, source excerpts, private absolute paths, screenshots, runtime captures, raw decompile bodies, private assets, or Ghidra mutation logs.

The raw decompile, generated constant scan, and generated JSON output remain ignored under `subagents/`.
