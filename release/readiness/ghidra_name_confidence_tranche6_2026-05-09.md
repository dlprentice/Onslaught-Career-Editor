# Ghidra Name-Confidence Tranche 6 - 2026-05-09

Status: public-safe read-only name-confidence classification, not a mutation or final identity proof

## Objective

Continue the saved Ghidra static re-audit by re-parsing the eight name-confidence targets left after the tranche-5 correction wave.

This pass treats the current names as hypotheses. It checks whether each remaining `_Unk_` / address-suffixed wrapper label is ready for a small future mutation wave or should stay deferred until caller boundaries, owner identity, table ownership, signatures, types, or tags are stronger.

## Inputs

- Address list: `subagents/ghidra-static-reaudit/name-confidence-tranche6/current/addresses.txt`
- Read-only metadata export: `subagents/ghidra-static-reaudit/name-confidence-tranche6/current/metadata.tsv`
- Read-only decompile index: `subagents/ghidra-static-reaudit/name-confidence-tranche6/current/decompile/index.tsv`
- Read-only xref export: `subagents/ghidra-static-reaudit/name-confidence-tranche6/current/xrefs.tsv`
- Read-only instruction export: `subagents/ghidra-static-reaudit/name-confidence-tranche6/current/instructions.tsv`
- Caller decompile index: `subagents/ghidra-static-reaudit/name-confidence-tranche6/current/caller_decompile/index.tsv`
- Raw-callsite/table context export: `subagents/ghidra-static-reaudit/name-confidence-tranche6/current/xref_context_instructions.tsv`
- Tranche report: `subagents/ghidra-static-reaudit/name-confidence-tranche6/current/name-confidence-tranche6.json`
- Probe: `tools/ghidra_name_confidence_tranche6_probe.py`
- Probe test: `tools/ghidra_name_confidence_tranche6_probe_test.py`

## Commands

Read-only Ghidra exports:

```powershell
bash tools/run_ghidra_headless_postscript.sh ExportFunctionMetadataByAddress.java subagents/ghidra-static-reaudit/name-confidence-tranche6/current/addresses.txt subagents/ghidra-static-reaudit/name-confidence-tranche6/current/metadata.tsv
bash tools/run_ghidra_headless_postscript.sh ExportFunctionsByAddressDecompile.java subagents/ghidra-static-reaudit/name-confidence-tranche6/current/addresses.txt subagents/ghidra-static-reaudit/name-confidence-tranche6/current/decompile 220
bash tools/run_ghidra_headless_postscript.sh ExportXrefsForAddresses.java subagents/ghidra-static-reaudit/name-confidence-tranche6/current/addresses.txt subagents/ghidra-static-reaudit/name-confidence-tranche6/current/xrefs.tsv
bash tools/run_ghidra_headless_postscript.sh ExportInstructionsAroundAddresses.java subagents/ghidra-static-reaudit/name-confidence-tranche6/current/addresses.txt subagents/ghidra-static-reaudit/name-confidence-tranche6/current/instructions.tsv 0 28
bash tools/run_ghidra_headless_postscript.sh ExportFunctionsByAddressDecompile.java subagents/ghidra-static-reaudit/name-confidence-tranche6/current/caller_functions.txt subagents/ghidra-static-reaudit/name-confidence-tranche6/current/caller_decompile 160
bash tools/run_ghidra_headless_postscript.sh ExportInstructionsAroundAddresses.java subagents/ghidra-static-reaudit/name-confidence-tranche6/current/xref_context_addresses.txt subagents/ghidra-static-reaudit/name-confidence-tranche6/current/xref_context_instructions.tsv 8 16
```

Probe validation:

```powershell
py -3 tools\ghidra_name_confidence_tranche6_probe_test.py
py -3 tools\ghidra_name_confidence_tranche6_probe.py --check
py -3 -m py_compile tools\ghidra_name_confidence_tranche6_probe.py tools\ghidra_name_confidence_tranche6_probe_test.py
cmd.exe /c npm run test:ghidra-name-confidence-tranche6
```

## Result

```text
Ghidra name-confidence tranche 6 probe
Status: PASS
Targets: 8
Xref rows: 8
Instruction rows: 232
Action counts: {'deferRawCallerBoundary': 3, 'deferOwnerIdentity': 1, 'ownerCorrectionCandidate': 1, 'renameCandidate': 2, 'deferTableOwner': 1}
```

Classification summary:

| Address | Current name | Classification | Suggested action |
| --- | --- | --- | --- |
| `0x00402dd0` | `CHeightField_Unk_0047eb80__Wrapper_00402dd0` | shadow/heightfield corner test with raw caller boundary | defer raw caller boundary |
| `0x0040dda0` | `CUnitAI_Unk_0044c720__Wrapper_0040dda0` | UnitAI-like grid cooldown body with surprising caller context | defer owner identity |
| `0x00411bf0` | `CEngine_Unk_0050a080__Wrapper_00411bf0` | mode-3 GeneralVolume burst dispatch owner correction candidate | owner-correction candidate |
| `0x00412240` | `ROUND__Wrapper_00412240` | mode-3 current-entry rounded slot value helper | rename candidate |
| `0x00412420` | `CText_GetStringById__Wrapper_00412420` | mode-3 current-entry display string helper | rename candidate |
| `0x00412830` | `CCockpit_Unk_00411e70__Wrapper_00412830` | cockpit disable/reselect helper with raw caller stub | defer raw caller boundary |
| `0x00413660` | `CGeneralVolume_Unk_00409e60__Wrapper_00413660` | scaled energy-drain helper in raw jump-table/case context | defer raw caller boundary |
| `0x00418090` | `FindAnimationIndex__Wrapper_00418090` | opening-animation state callback with DATA table xref | defer table owner |

## What This Proves

- The eight remaining name-confidence targets have fresh read-only metadata, decompile, xref, instruction, caller, and raw-callsite/table context exports.
- `0x00412240` and `0x00412420` are stronger future rename candidates than their current generic wrapper names suggest.
- `0x00411bf0` is a stronger future owner-correction candidate than its current `CEngine_Unk_...` label suggests.
- `0x00402dd0`, `0x00412830`, and `0x00413660` should stay deferred until raw/no-function caller boundaries are recovered or explained.
- `0x0040dda0` should stay deferred until owner identity is stronger.
- `0x00418090` should stay deferred until table ownership and exact class context are stronger.

## What This Does Not Prove

- This does not mutate Ghidra names, signatures, comments, tags, or function boundaries.
- This does not prove any candidate name, owner, signature, tag, type, or boundary is final.
- This does not prove exact source-to-retail identity.
- This does not prove runtime behavior.
- This does not patch, launch, or mutate `BEA.exe` or the installed game.

## Outcome

The next safe mutation wave should be selective:

- Consider `0x00412240`, `0x00412420`, and `0x00411bf0` only after choosing conservative names and running normal rename preflight, dry/apply, and read-back gates.
- Keep the raw-caller, owner-identity, and table-owner cases queued for boundary/table/source-context work first.
- Continue treating saved Ghidra names as reparsable hypotheses, not as completion proof.

## Privacy / Release Safety

This report stores repo-relative artifact paths, public addresses, function names, counts, classifications, caller names, command summaries, and proof boundaries only. It does not include binaries, private absolute paths, source excerpts, decompiled source excerpts, runtime captures, screenshots, frame data, copied executables, copied saves, debugger logs, raw private proof JSON, or private game payloads.
