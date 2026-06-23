# Ghidra CUnitAI Grid-Cooldown Rename - 2026-05-09

Status: PASS

Scope: public-safe summary of a saved Ghidra name/comment correction. Raw decompile exports, instruction windows, mutation logs, and generated JSON remain under ignored `subagents/` paths.

## What Changed

- `0x0040dda0` was corrected from `CUnitAI_Unk_0044c720__Wrapper_0040dda0` to `CUnitAI__RefreshGridCooldownFromOccupiedCells`.
- A proof-boundary comment was saved on the corrected function.
- The remaining name-confidence deferrals are now `0x00402dd0` and `0x00418090`.

## Evidence Summary

- Rename-map preflight accepted `1` row.
- Headless rename dry/apply saw the expected old name and saved the corrected name.
- Headless comment dry/apply saved the proof-boundary comment against the corrected name.
- Metadata, decompile, xref, instruction, and caller-decompile read-back verified the saved state.
- `py -3 tools\ghidra_unitai_grid_cooldown_rename_probe_test.py` returned PASS.
- `py -3 tools\ghidra_unitai_grid_cooldown_rename_probe.py --check` returned PASS.
- `cmd.exe /c npm run test:ghidra-unitai-grid-cooldown-rename` returned PASS.
- The refreshed queue reports `5865` total functions, `371` commented functions, `5494` commentless functions, `1` uncertain-owner name, `0` address-suffixed helper names, and `2` address-suffixed wrapper names.

## Interpretation

- The corrected body checks two `CSquadNormal__GetCellValueAtWorldXY` grids at the current world position.
- When either grid is active, the body refreshes the object `+0x2e8` timestamp to `DAT_00672fd0`.
- The checked caller `CExplosionInitThing__RenderObjectiveStatusPanel` passes the object at `param_1+0x50` and then reads the same `+0x2e8` timestamp for progress/UI math.
- This consumes the `0x0040dda0` rename candidate identified by the prior remaining-name-confidence review.

## Not Proven

- This does not harden signatures, parameter names, local names, tags, structures, or type information.
- This does not prove exact source identity or runtime behavior.
- This does not launch, patch, or mutate `BEA.exe` or the installed game.
- `0x00402dd0` still needs raw caller-boundary recovery, and `0x00418090` still needs DATA table-owner recovery.
