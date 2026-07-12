# Transition/HUD Helper Ghidra Read-Back Probe - 2026-05-06

Status: public-safe evidence

> **Current name correction (2026-07-12):** the broad body described below at
> `0x004081c0` is now statically identified as `CBattleEngine__Move`, not
> `CMonitor__Process`. Historical token/xref evidence remains useful; the old
> owner name is superseded and runtime HUD behavior remains unproven.

Source branch: `wip/sandbox`

Source commit before this wave: `720082f5a7550b64de40dfbf37631675bdc08744`

Evidence-report commit: 8e447c94d3b5ac0b211209a0fdd9ae726f0a2b42

Recorded at: 2026-05-06

## Scope

This proof adds a fresh read-only Ghidra read-back layer for five transition/HUD helper functions reached from the transform/HUD string xref investigation.

It does not mutate `BEA.exe`, launch the game, apply a rename map, or interpret runtime gameplay state. It uses the existing headless decompile export path to read back named functions and then validates selected token labels from ignored local decompile files.

## Private Evidence Policy

Ignored local evidence remains under `subagents/`. This report does not include decompiled source excerpts, binaries, private absolute paths, runtime captures, screenshots, frame data, Ghidra project files, or mutation logs.

Ignored evidence includes:

- `addresses.txt`
- `decompile/index.tsv`
- five decompile `.c` files
- `transition-hud-helper-ghidra-readback.json`

The ignored JSON stores repo-relative ignored filenames, function names, public-safe addresses already present in tracked docs or xref evidence, token labels, and line numbers only.

## Functions Checked

| Address | Function | Result | Selected Evidence |
| --- | --- | --- | --- |
| `0x00424920` | `CGeneralVolume__BeginFlyToWalkTransition` | PASS | `flytowalk` animation string, animation-index lookup, transition fields, and state value 1 |
| `0x00424990` | `CGeneralVolume__BeginWalkToFlyTransition` | PASS | `walktofly` animation string, animation-index lookup, transition fields, and state value 2 |
| `0x0040eeb0` | `CBattleEngine__FinishedPlayingCurrentAnimation` | PASS | Both transition animation strings and `SharedUnitAnimation__PlayAnimationByNameIfPresent` |
| `0x0040a580` | `CBattleEngine__Morph` | PASS | Calls both transition helpers, both animation strings, animation playback, and `EVENT_MANAGER` |
| `0x004081c0` | `CMonitor__Process` | PASS | Calls the morph helper plus selected HUD-format, sound, and movement helpers |

## Commands Run

### Headless Decompile Export

Command:

```powershell
wsl bash -lc "cd <repo-root> && tools/run_ghidra_headless_postscript.sh ExportFunctionsByAddressDecompile.java subagents/transition-hud-helper-ghidra-readback/2026-05-06/addresses.txt subagents/transition-hud-helper-ghidra-readback/2026-05-06/decompile 90"
```

Result: PASS

Important output:

- Headless Ghidra opened the existing `BEA` project and processed `BEA.exe`.
- `ExportFunctionsByAddressDecompile.java` reported `targets=5 dumped=5 missing=0 failed=0`.
- The log included unrelated GhydraMCP module-manifest warnings before successful script execution.
- Headless reported `Save succeeded` for the processed file even though this script performs read/export work; this report does not treat that as a mutation proof.

### Read-Back Validation Probe

Command:

```powershell
npm run test:transition-hud-helper-ghidra-readback
```

Result: PASS

Important output:

- 5/5 functions passed read-back validation.
- `CGeneralVolume__BeginFlyToWalkTransition` and `CGeneralVolume__BeginWalkToFlyTransition` validate the current transition animation helper names.
- `CBattleEngine__FinishedPlayingCurrentAnimation` validates the current animation-completion helper checks both transition animation strings.
- `CBattleEngine__Morph` validates the current BattleEngine morph helper calls both transition helpers and animation strings.
- `CMonitor__Process` validates the current monitor process body calls the morph helper and selected HUD/sound/movement helpers.

Postscript 2026-05-14: Later Ghidra correction waves renamed `0x0040eeb0` from the broad `CUnit__FinishedPlayingCurrentAnimation` label to `CBattleEngine__FinishedPlayingCurrentAnimation`, renamed `0x0040a580` from the broad monitor transition-state label to `CBattleEngine__Morph`, and corrected the prior GillMHead-specific playback-helper label to `SharedUnitAnimation__PlayAnimationByNameIfPresent`. These updates refresh saved-name/token labels only; the original transition/HUD proof boundaries remain unchanged.

## What Is Proven

- Fresh headless Ghidra read-back can export decompile output for five transition/HUD helper functions reached from current transform/HUD string xrefs.
- The selected fly-to-walk and walk-to-fly helper functions have current decompile tokens supporting their transition helper names.
- The selected BattleEngine animation-completion helper has current decompile tokens supporting transition animation completion naming.
- The selected BattleEngine morph and Monitor process helpers have current decompile tokens supporting transform, HUD, sound, and movement linkage.
- The new `tools/transition_hud_helper_ghidra_readback_probe.py` script provides a repeatable public-safe validation layer over ignored decompile exports.

## What Is Not Proven

- This does not prove exact source-to-retail identity for source `CBattleEngine::Morph` / the transform-morph flow.
- This does not prove transform or HUD-warning runtime behavior in the running game.
- This does not apply or validate a Ghidra rename map.
- This does not mutate the Ghidra project intentionally, mutate `BEA.exe`, or launch the game.
- This does not prove a rebuildable open-source gameplay implementation.

## Release Posture

GREEN for selected transition/HUD helper Ghidra decompile read-back.

Remaining RE gaps are exact source-to-retail identity for full transform/damage/energy mechanics, runtime gameplay-state interpretation, and rebuildable implementation parity.
