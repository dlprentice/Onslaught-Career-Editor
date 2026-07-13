# BattleEngine Mechanics Ghidra Read-Back Probe - 2026-05-06

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 semantic revalidation:** Historical record; `0x0049faa0` comment correction. The original text below remains provenance rather than current semantic authority. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); exact records are in `reverse-engineering/binary-analysis/ghidra-full-reaudit-corrections-2026-07-13.json` and `reverse-engineering/binary-analysis/ghidra-targeted-revalidation-corrections-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Status: public-safe evidence

Source branch: `wip/sandbox`

Source commit before this wave: `4e405987f827de958ea6685b040820e5dc8d0814`

Evidence-report commit: `61b660f01646f7feee2ba1e182e06dee6e82bc48`

Recorded at: 2026-05-06

## Scope

This proof adds a fresh read-only Ghidra read-back layer for five already named Unit/Mech mechanics-adjacent retail functions.

It does not mutate `BEA.exe`, launch the game, apply a rename map, or interpret runtime gameplay state. It uses the existing headless decompile export path to read back named functions and then validates selected source-aligned token labels from ignored local decompile files.

## Private Evidence Policy

Ignored local evidence remains under `subagents/`. This report does not include decompiled source excerpts, binaries, private absolute paths, runtime captures, screenshots, frame data, Ghidra project files, or mutation logs.

Ignored evidence includes:

- `addresses.txt`
- `decompile/index.tsv`
- five decompile `.c` files
- `battleengine-mechanics-ghidra-readback.json`

The ignored JSON stores repo-relative ignored filenames, function names, public-safe addresses already present in tracked docs, token labels, and line numbers only.

## Functions Checked

| Address | Function | Result | Selected Evidence |
| --- | --- | --- | --- |
| `0x004f9a90` | `CUnit__ApplyDamage` | PASS | Named damage handler signature plus cooldown, destructible segment, particle effect, weakpoint, and nexus tokens |
| `0x004f86d0` | `CUnit__Init` | PASS | Named Unit init signature plus weapon, spawner, character, active-reader, and Unit source-path tokens |
| `0x004fc4e0` | `CUnit__UpdateTransform` | PASS | Named transform function plus emitter lookup, matrix-basis multiplication, and Unit source-path tokens |
| `0x0049fa30` | `CMech__InitCockpit` | PASS | Named cockpit setup function plus cockpit object allocation, Mech AI constructor-like, and Mech source-path tokens |
| `0x0049faa0` | `CMech__InitTargeting` | PASS | Named targeting setup function plus guide object allocation, Mech guide constructor-like, and Mech source-path tokens |

## Commands Run

### Headless Decompile Export

Command:

```powershell
wsl bash -lc "cd <repo-root> && tools/run_ghidra_headless_postscript.sh ExportFunctionsByAddressDecompile.java subagents/battleengine-mechanics-ghidra-readback/2026-05-06/addresses.txt subagents/battleengine-mechanics-ghidra-readback/2026-05-06/decompile 90"
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
npm run test:battleengine-mechanics-ghidra-readback
```

Result: PASS

Important output:

- 5/5 functions passed read-back validation.
- `CUnit__ApplyDamage` contained selected cooldown, destructible-segment, particle-effect, weakpoint, and nexus tokens.
- `CUnit__Init` contained selected weapon, spawner, character, active-reader, and Unit source-path tokens.
- `CUnit__UpdateTransform` contained selected emitter, transform, and Unit source-path tokens.
- `CMech__InitCockpit` and `CMech__InitTargeting` contained selected allocation, constructor-like, and Mech source-path tokens.
- Three rows currently retain `undefined ... (void)` Ghidra signatures; the validation therefore claims function-name and body-token read-back for those rows, not recovered call-convention identity.

## What Is Proven

- Fresh headless Ghidra read-back can export decompile output for five already named Unit/Mech mechanics-adjacent retail functions.
- The selected `CUnit__ApplyDamage` retail function has current decompile tokens supporting the existing damage/segment/effect naming.
- The selected `CUnit__Init` retail function has current decompile tokens supporting Unit setup naming.
- The selected `CUnit__UpdateTransform` retail function has current decompile tokens supporting transform/emitter naming.
- The selected `CMech__InitCockpit` and `CMech__InitTargeting` retail functions have current decompile tokens supporting Mech cockpit/targeting setup naming.
- The new `tools/battleengine_mechanics_ghidra_readback_probe.py` script provides a repeatable public-safe validation layer over ignored decompile exports.

## What Is Not Proven

- This does not prove Steam retail binary identity for every BattleEngine gameplay source anchor.
- This does not prove damage, shield, transform, jet-energy, walker-recharge, or god-mode runtime behavior in the running game.
- This does not recover exact call conventions for the three rows whose current Ghidra signatures are still undefined.
- This does not apply or validate a Ghidra rename map.
- This does not mutate the Ghidra project intentionally, mutate `BEA.exe`, or launch the game.
- This does not prove a rebuildable open-source gameplay implementation.

## Release Posture

GREEN for selected Unit/Mech mechanics Ghidra decompile read-back.

Remaining RE gaps are broader exact retail identity for every gameplay mechanics anchor, runtime gameplay-state interpretation, and rebuildable implementation parity.
