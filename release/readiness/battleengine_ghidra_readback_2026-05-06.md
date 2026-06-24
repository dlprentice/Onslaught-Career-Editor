# BattleEngine Ghidra Read-Back Probe - 2026-05-06

Status: public-safe evidence

Source branch: `wip/sandbox`

Source commit before this wave: `b0e83034a888cde092fcfafd9ebf8626958db2c1`

Evidence-report commit: `3f744e82896ca91c5e616985616021eb4d88947d`

Recorded at: 2026-05-06

## Scope

This proof adds a narrow fresh Ghidra read-back layer for selected BattleEngine-related retail functions.

It does not mutate `BEA.exe`, launch the game, apply a rename map, or interpret runtime gameplay state. It uses the existing headless decompile export path to read back three already named functions and then validates a compact set of source-aligned token labels from ignored local decompile files.

## Private Evidence Policy

Ignored local evidence remains under `subagents/`. This report does not include decompiled source excerpts, binaries, private absolute paths, runtime captures, screenshots, frame data, Ghidra project files, or mutation logs.

Ignored evidence includes:

- `addresses.txt`
- `decompile/index.tsv`
- three decompile `.c` files
- `battleengine-ghidra-readback.json`

The ignored JSON stores repo-relative ignored filenames, function names, public-safe addresses already present in tracked docs, token labels, and line numbers only.

## Functions Checked

| Address | Function | Result | Selected Evidence |
| --- | --- | --- | --- |
| `0x0040f590` | `CBattleEngineData__Initialise` | PASS | Source-path ownership token, default loadout tokens, cockpit mesh token, and selected default float constants |
| `0x00404dd0` | `CBattleEngine__Init` | PASS | Source-path ownership token and selected BattleEngine init call-chain tokens |
| `0x004d28a0` | `CPlayer__Init` | PASS | Player init signature token and first-person-view initialization token |

## Commands Run

### Headless Decompile Export

Command:

```powershell
wsl bash -lc "cd <repo-root> && tools/run_ghidra_headless_postscript.sh ExportFunctionsByAddressDecompile.java subagents/battleengine-ghidra-readback/2026-05-06/addresses.txt subagents/battleengine-ghidra-readback/2026-05-06/decompile 90"
```

Result: PASS

Important output:

- Headless Ghidra opened the existing `BEA` project and processed `BEA.exe`.
- `ExportFunctionsByAddressDecompile.java` reported `targets=3 dumped=3 missing=0 failed=0`.
- The log included unrelated GhydraMCP module-manifest warnings before successful script execution.
- Headless reported `Save succeeded` for the processed file even though this script performs read/export work; this report does not treat that as a mutation proof.

### Read-Back Validation Probe

Command:

```powershell
py -3 tools\battleengine_ghidra_readback_probe.py --check --json
```

Result: PASS

Important output:

- 3/3 functions passed read-back validation.
- `CBattleEngineData__Initialise` contained selected loadout/config tokens, including Vulcan Cannon, Pulse Cannon Pod, Missile Pod, `cockpit2.msh`, `0x40200000`, `0x3e99999a`, `0x3f800000`, and `0x42b40000`.
- `CBattleEngine__Init` contained selected ownership/call-chain tokens.
- `CPlayer__Init` contained the expected first-person-view initialization call token.

## What Is Proven

- Fresh headless Ghidra read-back can export decompile output for selected already named BattleEngine-related retail functions.
- The selected `CBattleEngineData__Initialise` retail function has current decompile tokens that support the existing config-default/loadout mapping.
- The selected `CBattleEngine__Init` retail function has current decompile tokens that support BattleEngine ownership and init call-chain mapping.
- The selected `CPlayer__Init` retail function has current decompile tokens that support Player init naming.
- The new `tools/battleengine_ghidra_readback_probe.py` script provides a repeatable public-safe validation layer over ignored decompile exports.

## What Is Not Proven

- This does not prove Steam retail binary identity for every BattleEngine gameplay source anchor.
- This does not prove damage, shield, transform, jet-energy, walker-recharge, or god-mode runtime behavior in the running game.
- This does not apply or validate a Ghidra rename map.
- This does not mutate the Ghidra project intentionally, mutate `BEA.exe`, or launch the game.
- This does not prove a rebuildable open-source gameplay implementation.

## Release Posture

GREEN for selected BattleEngine-related Ghidra decompile read-back.

Remaining RE gaps are broader exact retail identity for individual gameplay mechanics anchors, runtime gameplay-state interpretation, and rebuildable implementation parity.
