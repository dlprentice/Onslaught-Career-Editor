# Ghidra Remaining Name-Confidence Review - 2026-05-09

Status: PASS

Follow-up note: later saved mutation waves consumed all three reviewed targets. `0x0040dda0` is now `CUnitAI__RefreshGridCooldownFromOccupiedCells`, `0x00402dd0` is now `ShadowHeightfield__AnyBoundsCornerAboveSampledHeight` after caller-boundary recovery, and `0x00418090` is now `OpeningAnimationStateCallback__StartOpeningIfPending` while preserving unresolved table-owner caveats.

Scope: public-safe summary of a read-only Ghidra classification pass for the three remaining name-confidence targets. Raw decompile exports, instruction windows, xrefs, and generated JSON remain under ignored `subagents/` paths.

## What Changed

- Added a focused checked probe for the three remaining name-confidence targets.
- Reclassified `0x0040dda0` as a read-only rename candidate: `CUnitAI__RefreshGridCooldownFromOccupiedCells`.
- Kept `0x00402dd0` deferred behind raw caller-boundary recovery.
- Kept `0x00418090` deferred behind DATA table-owner recovery.
- No Ghidra name, comment, signature, tag, type, local, or boundary mutation was applied in this wave.

## Evidence Summary

- Headless metadata export found `3/3` targets.
- Headless decompile export dumped `3/3` targets.
- Headless xref export wrote `3` target rows.
- Headless instruction export wrote `99` target rows.
- Headless caller-context instruction export wrote `292` rows and preserved the expected missing-instruction DATA-slot context for `0x005d9080`.
- Headless caller metadata/decompile export covered the two supporting caller functions.
- `py -3 tools\ghidra_remaining_name_confidence_probe_test.py` returned PASS.
- `py -3 tools\ghidra_remaining_name_confidence_probe.py --check` returned PASS with action counts: `renameCandidate=1`, `deferRawCallerBoundary=1`, and `deferTableOwner=1`.
- `cmd.exe /c npm run test:ghidra-remaining-name-confidence` returned PASS.

## Interpretation

- `0x00402dd0` still has shadow/heightfield corner-test behavior, but the checked caller at `0x004478a3` remains outside a named function boundary. It should not be renamed until caller ownership is recovered.
- `0x0040dda0` now has stronger read-only caller/callee evidence: the callee refreshes a `+0x2e8` timestamp after checking two `CSquadNormal__GetCellValueAtWorldXY` grids, and the checked caller passes the object stored at `param_1+0x50` then immediately reads the same `+0x2e8` timestamp for UI/progress math.
- `0x00418090` still reads as an opening-animation state callback, but the only checked reference remains a DATA slot at `0x005d9080`; table/class ownership remains unresolved.

## Not Proven

- This does not mutate or save any new Ghidra name.
- The proposed `0x0040dda0` rename is not yet saved in Ghidra.
- This does not harden signatures, parameter names, locals, tags, structures, or table types.
- This does not prove exact source-to-retail identity or runtime behavior.
- This does not launch, patch, or mutate `BEA.exe` or the installed game.
