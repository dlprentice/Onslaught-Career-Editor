# BattleEngine Transform Special-Move Candidate - 2026-05-07

Status: public-safe bounded read-only retail-candidate evidence, not exact Morph identity or runtime proof

## Objective

Narrow the remaining source-only `transform_reject_special_moves` gap.

Source `CBattleEngine::Morph()` rejects morphing when the jet special-air-move path or walker special-walker-move path is active. This pass checks the strongest current retail transition helper for source-compatible early lockout gates before either transform branch runs.

## Inputs

Fresh ignored Ghidra headless export:

```text
subagents/battleengine-transform-special-move-candidate/current/decompile/
```

The export reported targets `1`, dumped `1`, missing `0`, failed `0` for:

```text
0x0040a580 CMonitor__UpdateFlightWalkerTransitionState
```

Raw decompile output remains ignored/private under `subagents/`.

## Probe

Command:

```powershell
npm run test:battleengine-transform-special-move-candidate
```

Equivalent direct command:

```powershell
py -3 tools\battleengine_transform_special_move_candidate_probe.py --check
```

Result:

```text
BattleEngine transform special-move candidate probe
Status: pass
Source tokens: 5/5
Retail tokens: 8/8
```

The probe checks:

- source `CBattleEngine::Morph()` special-move rejection tokens
- current decompile index row for `0x0040a580 CMonitor__UpdateFlightWalkerTransitionState`
- early retail `CGeneralVolume__IsStateMachineActive` and `CGeneralVolume__IsDashLockoutActive` gates
- fly-to-walk and walk-to-fly transition calls
- fly-to-walk and walk-to-fly animation strings
- line ordering proving both retail lockout gates occur before both transition branches

## What This Proves

- Source `CBattleEngine::Morph()` still rejects morphing during jet and walker special-move paths.
- Fresh read-only `CMonitor__UpdateFlightWalkerTransitionState` decompile contains early state-machine and dash-lockout gates before both transition branches.
- The same helper still contains the known fly-to-walk / walk-to-fly transition calls and animation strings from the Morph bridge evidence.
- `transform_reject_special_moves` can now be tracked as a partial retail candidate, not a fully source-only gap.

## What This Does Not Prove

- Exact source-to-retail identity for `GetIsDoingSpecialAirMove` or `GetIsDoingSpecialWalkerMove`.
- Exact full `CBattleEngine::Morph()` body identity.
- Correct final owner/name/signature for every retail helper involved.
- Runtime transform rejection during special moves.
- Ghidra rename-map mutation.
- Rebuildable open-source gameplay implementation.

## Privacy / Release Safety

The committed report is public-safe. It does not include binaries, source excerpts, private absolute paths, screenshots, runtime captures, raw decompile bodies, private assets, or Ghidra mutation logs.

The raw decompile and generated JSON output remain ignored under `subagents/`.
