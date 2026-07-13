# BattleEngine Helper Ghidra Read-Back Probe - 2026-05-06

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 live correction closeout:** Historical record; `0x00406560` → `CBattleEngine__HandleLocks` (was `CBattleEngine__UpdateAutoTargetSetAndFireProjectiles`). The original text below remains provenance rather than current semantic authority. It is superseded only where confirmed. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); final per-address decisions and exact before/after metadata are in `reverse-engineering/binary-analysis/ghidra-reviewed-correction-decisions-2026-07-13.jsonl` and `reverse-engineering/binary-analysis/ghidra-reviewed-correction-plan-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Status: public-safe evidence

Source branch: `wip/sandbox`

Source commit before this wave: `39475f879ade2ae9f99e1b42a5407f8a5d8e3934`

Evidence-report commit: `c9f75d5d454ca26ab5f711c8fce4f83d05229245`

Recorded at: 2026-05-06

## Scope

This proof adds a fresh read-only Ghidra read-back layer for four already named BattleEngine transform/target/combat helper functions.

It does not mutate `BEA.exe`, launch the game, apply a rename map, or interpret runtime gameplay state. It uses the existing headless decompile export path to read back named functions and then validates selected source-aligned token labels from ignored local decompile files.

## Private Evidence Policy

Ignored local evidence remains under `subagents/`. This report does not include decompiled source excerpts, binaries, private absolute paths, runtime captures, screenshots, frame data, Ghidra project files, or mutation logs.

Ignored evidence includes:

- `addresses.txt`
- `decompile/index.tsv`
- four decompile `.c` files
- `battleengine-helper-ghidra-readback.json`

The ignored JSON stores repo-relative ignored filenames, function names, public-safe addresses already present in tracked docs, token labels, and line numbers only.

## Functions Checked

| Address | Function | Result | Selected Evidence |
| --- | --- | --- | --- |
| `0x00406460` | `CBattleEngine__SwapPrimarySecondaryPartReadersForState` | PASS | Named state-gated reader-swap helper plus transform-state, reader-slot, reset, and influence-map tokens |
| `0x00406560` | `CBattleEngine__UpdateAutoTargetSetAndFireProjectiles` | PASS | Named auto-target/projectile helper plus indexed-entry, resolved-entry, nearest-target, projectile, and list-removal tokens |
| `0x00406da0` | `CBattleEngine__SelectNearestForwardTargetFromGlobalSet` | PASS | Named forward-target selection helper plus weapon-mode, target-mask, profile-field, and list-traversal tokens |
| `0x00407310` | `CBattleEngine__IsCurrentResolvedEntry` | PASS | Named current/resolved-entry comparator plus indexed-entry and fallback-resolution tokens |

## Commands Run

### Headless Decompile Export

Command:

```powershell
wsl bash -lc "cd <repo-root> && tools/run_ghidra_headless_postscript.sh ExportFunctionsByAddressDecompile.java subagents/battleengine-helper-ghidra-readback/2026-05-06/addresses.txt subagents/battleengine-helper-ghidra-readback/2026-05-06/decompile 90"
```

Result: PASS

Important output:

- Headless Ghidra opened the existing `BEA` project and processed `BEA.exe`.
- `ExportFunctionsByAddressDecompile.java` reported `targets=4 dumped=4 missing=0 failed=0`.
- The log included unrelated GhydraMCP module-manifest warnings before successful script execution.
- Headless reported `Save succeeded` for the processed file even though this script performs read/export work; this report does not treat that as a mutation proof.

### Read-Back Validation Probe

Command:

```powershell
npm run test:battleengine-helper-ghidra-readback
```

Result: PASS

Important output:

- 4/4 functions passed read-back validation.
- `CBattleEngine__SwapPrimarySecondaryPartReadersForState` contained selected state/reader-swap and influence-map tokens.
- `CBattleEngine__UpdateAutoTargetSetAndFireProjectiles` contained selected target-resolution and projectile emission call-chain tokens.
- `CBattleEngine__SelectNearestForwardTargetFromGlobalSet` contained selected profile/list traversal and target-mask tokens.
- `CBattleEngine__IsCurrentResolvedEntry` contained selected indexed-entry and fallback-resolution tokens.

## What Is Proven

- Fresh headless Ghidra read-back can export decompile output for four already named BattleEngine helper functions.
- The selected transform-state reader-swap helper has current decompile tokens supporting its existing state-gated naming.
- The selected target/projectile helper has current decompile tokens supporting target-resolution and projectile call-chain naming.
- The selected forward-target helper has current decompile tokens supporting list traversal and target filtering naming.
- The selected resolved-entry comparator has current decompile tokens supporting current/fallback entry comparison naming.
- The new `tools/battleengine_helper_ghidra_readback_probe.py` script provides a repeatable public-safe validation layer over ignored decompile exports.

## What Is Not Proven

- This does not prove Steam retail binary identity for every BattleEngine gameplay source anchor.
- This does not prove runtime damage, shield, transform, target-selection, or firing behavior in the running game.
- This does not apply or validate a Ghidra rename map.
- This does not mutate the Ghidra project intentionally, mutate `BEA.exe`, or launch the game.
- This does not prove a rebuildable open-source gameplay implementation.

## Release Posture

GREEN for selected BattleEngine helper Ghidra decompile read-back.

Remaining RE gaps are broader exact retail identity for every gameplay mechanics anchor, runtime gameplay-state interpretation, and rebuildable implementation parity.
