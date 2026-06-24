# BattleEngine Transform String Xref Probe - 2026-05-06

Status: public-safe evidence

Source branch: `wip/sandbox`

Source commit before this wave: `9dfa76407f99bfe63b5e1bc5e24134c1b97f67b4`

Evidence-report commit: `beb72644af9cce5b1fe718db2371cdb4023bd46d`

Recorded at: 2026-05-06

## Scope

This proof records a narrow read-only source-to-binary investigation for BattleEngine transform and HUD-warning strings.

The investigation scanned the local retail executable bytes read-only to locate selected ASCII string addresses, then used the existing headless Ghidra xref exporter to identify current referencing functions. It does not mutate `BEA.exe`, launch the game, apply a rename map, or interpret runtime gameplay state.

## Private Evidence Policy

Ignored local evidence remains under `subagents/`. This report does not include private absolute paths, raw binary bytes, decompiled source excerpts, runtime captures, screenshots, frame data, Ghidra project files, or mutation logs.

Ignored evidence includes:

- `string-addresses.txt`
- `string-xrefs.tsv`
- `battleengine-transform-string-xrefs.json`

The ignored JSON stores string labels, public-safe string addresses, xref counts, and function names only.

## Strings Checked

| String | Address | Result | Current Xref Functions |
| --- | --- | --- | --- |
| `flytowalk` | `0x006234bc` | PASS | `CGeneralVolume__BeginFlyToWalkTransition`, `CUnit__FinishedPlayingCurrentAnimation`, `CMonitor__UpdateFlightWalkerTransitionState` |
| `walktofly` | `0x006234b0` | PASS | `CGeneralVolume__BeginWalkToFlyTransition`, `CUnit__FinishedPlayingCurrentAnimation`, `CMonitor__UpdateFlightWalkerTransitionState` |
| `hud_armour_low` | `0x0062331c` | PASS | `CMonitor__Process` |
| `hud_energy_low` | `0x00623304` | PASS | `CMonitor__Process` |

## Commands Run

### Read-Only String Address Scan

Command:

```powershell
node <read-only local script that scans the local retail BEA.exe for selected ASCII strings and converts file offsets through the PE section table>
```

Result: PASS

Important output:

- `flytowalk` found at `0x006234bc`.
- `walktofly` found at `0x006234b0`.
- `hud_armour_low` found at `0x0062331c`.
- `hud_energy_low` found at `0x00623304`.
- No write operation was performed.

### Headless Xref Export

Command:

```powershell
wsl bash -lc "cd <repo-root> && tools/run_ghidra_headless_postscript.sh ExportXrefsForAddresses.java subagents/battleengine-transform-xrefs/2026-05-06/string-addresses.txt subagents/battleengine-transform-xrefs/2026-05-06/string-xrefs.tsv"
```

Result: PASS

Important output:

- Headless Ghidra opened the existing `BEA` project and processed `BEA.exe`.
- `ExportXrefsForAddresses.java` reported 10 output rows.
- The log included unrelated GhydraMCP module-manifest warnings before successful script execution.
- Headless reported `Save succeeded` for the processed file even though this script performs read/export work; this report does not treat that as a mutation proof.

### Xref Validation Probe

Command:

```powershell
npm run test:battleengine-transform-string-xrefs
```

Result: PASS

Important output:

- 4/4 strings passed xref validation.
- `flytowalk` and `walktofly` currently xref transition helpers in `CGeneralVolume`, `CUnit`, and `CMonitor`.
- `hud_armour_low` and `hud_energy_low` currently xref `CMonitor__Process`.

## What Is Proven

- The selected transform animation strings and HUD-warning strings are present in the current retail executable at the recorded addresses.
- Current Ghidra xrefs for `flytowalk` and `walktofly` point at transition helper functions, not at the source `CBattleEngine::Morph` body.
- Current Ghidra xrefs for `hud_armour_low` and `hud_energy_low` point at `CMonitor__Process`.
- The new `tools/battleengine_transform_string_xref_probe.py` script provides a repeatable public-safe validation layer over ignored xref exports.

## What Is Not Proven

- This does not prove exact source-to-retail identity for source `CBattleEngine::Morph` / the transform-morph flow.
- This does not prove transform or HUD-warning runtime behavior in the running game.
- This does not apply or validate a Ghidra rename map.
- This does not mutate the Ghidra project intentionally, mutate `BEA.exe`, or launch the game.
- This does not prove a rebuildable open-source gameplay implementation.

## Release Posture

GREEN for selected transform/HUD string xref read-back.

Remaining RE gaps are exact source-to-retail identity for full transform/damage/energy mechanics, runtime gameplay-state interpretation, and rebuildable implementation parity.
