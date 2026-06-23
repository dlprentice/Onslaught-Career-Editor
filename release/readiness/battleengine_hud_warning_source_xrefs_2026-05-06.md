# BattleEngine HUD Warning Source/Xref Bridge Probe - 2026-05-06

Status: public-safe reverse-engineering evidence

Source branch: `wip/sandbox`

Source commit before this wave: `c7c88a3c580b7cda609b383fe5d03250adc85642`

Evidence-report commit: 8aba8b7c3b20eb9c86924e158b2fd039b3c63d8f

Recorded at: 2026-05-06

## Scope

This proof adds a narrow, public-safe bridge between Stuart source HUD warning sample anchors and existing retail string-xref evidence.

It does not launch the game, read or mutate `BEA.exe`, mutate Ghidra, export source excerpts, or interpret runtime gameplay state. It checks source tokens, tracked string-xref evidence, the transition/HUD helper read-back report, and the current `CMonitor__Process` function note.

## Private Evidence Policy

Ignored local evidence remains under `subagents/`. This report does not include source excerpts, binaries, private absolute paths, runtime captures, screenshots, frame data, Ghidra project files, or mutation logs.

Ignored evidence includes:

- `battleengine-hud-warning-source-xrefs.json`

The ignored JSON stores repo-relative filenames, token labels, line numbers, summaries, and pass/fail state only.

## Checks

| Check | Result | Selected Evidence |
| --- | --- | --- |
| Source low-armour HUD sample | PASS | Source tokens for `mLife <= low_life`, `mLowArmourStartTime`, `PlayHudSample("hud_armour_low")`, and the repeat timer |
| Source low-energy HUD sample | PASS | Source tokens for `mConfiguration->mEnergy / 4.0f`, `mEnergy <= low_energy`, `mLowEnergyStartTime`, `PlayHudSample("hud_energy_low")`, and the repeat timer |
| Retail string-xref report | PASS | Existing public-safe xref report links both HUD strings to `CMonitor__Process` |
| Transition/HUD helper read-back report | PASS | Existing read-back report records the current `CMonitor__Process` body with selected HUD/sound/physics helper tokens |
| `CMonitor__Process` function note | PASS | Function note records the source/string-xref bridge while keeping live HUD behavior unclaimed |

## Commands Run

Command:

```powershell
npm run test:battleengine-hud-warning-source-xrefs
```

Result: PASS

Important output:

- 5/5 checks passed.
- Source anchors for low-armour and low-energy HUD warning samples are present in `BattleEngine.cpp`.
- Existing retail string-xref evidence links `hud_armour_low` and `hud_energy_low` to the current `CMonitor__Process` family.
- The current function note keeps runtime HUD-warning behavior unclaimed.

## What Is Proven

- Stuart source contains low-armour and low-energy HUD warning sample anchors.
- Tracked retail string-xref evidence links the corresponding HUD strings to the current `CMonitor__Process` family.
- The current `CMonitor__Process` function note records this bridge while preserving runtime-proof boundaries.
- The new `tools/battleengine_hud_warning_source_xref_probe.py` script provides a repeatable public-safe validation layer over source tokens, tracked evidence, and docs.

## What Is Not Proven

- Live HUD warning sample playback in a running mission.
- Exact source-to-retail control-flow identity for the full BattleEngine process loop.
- Runtime gameplay-state interpretation.
- Ghidra rename-map mutation or read-back.
- Rebuildable open-source gameplay implementation.

## Release Posture

GREEN for a selected HUD-warning source/string-xref bridge.

Remaining RE gaps are exact source-to-retail identity for full transform/damage/energy mechanics, runtime gameplay-state interpretation, and rebuildable implementation parity.
