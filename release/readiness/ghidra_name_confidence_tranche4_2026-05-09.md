# Ghidra Name-Confidence Tranche 4 - 2026-05-09

Status: public-safe read-only name-confidence classification, not a mutation or final identity proof

## Objective

Continue the saved Ghidra static re-audit by re-parsing the next small name-confidence queue slice after the tranche-3 saved correction pass.

This pass deliberately treats current saved names as hypotheses. It checks whether six already-commented `_Unk_` / address-suffixed wrapper labels still deserve future rename, owner-correction, or deferred review before any new saved Ghidra mutation wave.

## Inputs

- Address list: `subagents/ghidra-static-reaudit/name-confidence-tranche4/current/addresses.txt`
- Read-only metadata export: `subagents/ghidra-static-reaudit/name-confidence-tranche4/current/metadata.tsv`
- Read-only decompile index: `subagents/ghidra-static-reaudit/name-confidence-tranche4/current/decompile/index.tsv`
- Read-only xref export: `subagents/ghidra-static-reaudit/name-confidence-tranche4/current/xrefs.tsv`
- Read-only instruction export: `subagents/ghidra-static-reaudit/name-confidence-tranche4/current/instructions.tsv`
- Tranche report: `subagents/ghidra-static-reaudit/name-confidence-tranche4/current/name-confidence-tranche4.json`
- Probe: `tools/ghidra_name_confidence_tranche4_probe.py`
- Probe test: `tools/ghidra_name_confidence_tranche4_probe_test.py`

## Commands

Read-only Ghidra exports:

```powershell
bash tools/run_ghidra_headless_postscript.sh ExportFunctionMetadataByAddress.java subagents/ghidra-static-reaudit/name-confidence-tranche4/current/addresses.txt subagents/ghidra-static-reaudit/name-confidence-tranche4/current/metadata.tsv
bash tools/run_ghidra_headless_postscript.sh ExportFunctionsByAddressDecompile.java subagents/ghidra-static-reaudit/name-confidence-tranche4/current/addresses.txt subagents/ghidra-static-reaudit/name-confidence-tranche4/current/decompile 140
bash tools/run_ghidra_headless_postscript.sh ExportXrefsForAddresses.java subagents/ghidra-static-reaudit/name-confidence-tranche4/current/addresses.txt subagents/ghidra-static-reaudit/name-confidence-tranche4/current/xrefs.tsv
bash tools/run_ghidra_headless_postscript.sh ExportInstructionsAroundAddresses.java subagents/ghidra-static-reaudit/name-confidence-tranche4/current/addresses.txt subagents/ghidra-static-reaudit/name-confidence-tranche4/current/instructions.tsv 0 18
```

Probe validation:

```powershell
py -3 tools\ghidra_name_confidence_tranche4_probe_test.py
py -3 tools\ghidra_name_confidence_tranche4_probe.py --check
py -3 -m py_compile tools\ghidra_name_confidence_tranche4_probe.py tools\ghidra_name_confidence_tranche4_probe_test.py
cmd.exe /c npm run test:ghidra-name-confidence-tranche4
```

## Result

```text
Ghidra name-confidence tranche 4 probe
Status: PASS
Targets: 6
Xref rows: 17
Instruction rows: 114
Action counts: {'deferOwnerIdentity': 1, 'renameCandidate': 3, 'deferCallerOwnerReview': 1, 'ownerCorrectionCandidate': 1}
```

Classification summary:

| Address | Current name | Classification | Suggested action |
| --- | --- | --- | --- |
| `0x00402dd0` | `CHeightField_Unk_0047eb80__Wrapper_00402dd0` | shadow/heightfield corner test, owner deferred | defer owner identity |
| `0x00403ff0` | `CFastVB_Unk_0055db0a__Wrapper_00403ff0` | resource-descriptor array destroy wrapper | rename candidate |
| `0x0040dcc0` | `CGeneralVolume_Unk_0040a580__Wrapper_0040dcc0` | monitor transition-state wrapper | rename candidate |
| `0x0040dda0` | `CUnitAI_Unk_0044c720__Wrapper_0040dda0` | UnitAI grid cooldown/stamp, caller/owner review needed | defer caller/owner review |
| `0x00410670` | `CGeneralVolume_Unk_00409e60__Wrapper_00410670` | general-volume linked-object drain/update wrapper | rename candidate |
| `0x00411b90` | `CEngine_Unk_00506010__Wrapper_00411b90` | general-volume burst-list dispatch, owner correction | owner-correction candidate |

## What This Proves

- The fourth name-confidence queue tranche has read-only metadata, decompile, xref, and instruction context for all `6` selected targets.
- The saved proof-boundary comments remain present for each selected target.
- `0x00403ff0`, `0x0040dcc0`, and `0x00410670` have behavior-specific evidence that can support future conservative rename candidates.
- `0x00411b90` has caller/callee context pointing toward a CGeneralVolume burst-dispatch owner correction rather than the current CEngine/_Unk label.
- `0x00402dd0` and `0x0040dda0` should stay deferred until owner/caller context is improved.

## What This Does Not Prove

- This does not mutate Ghidra names, signatures, comments, tags, or function boundaries.
- This does not prove the candidate names, owners, or signatures are final.
- This does not prove exact source-to-retail identity.
- This does not prove runtime behavior.
- This does not patch, launch, or mutate `BEA.exe` or the installed game.

## Outcome

Future mutation should be selective:

- A small correction wave can target the three rename candidates and the one owner-correction candidate after choosing conservative names and running the normal preflight/dry/apply/read-back gates.
- The shadow/heightfield corner test and UnitAI grid cooldown/stamp body should remain queued until owner/caller evidence is stronger.
- The broader static re-audit should continue treating saved names as reparsable hypotheses, not as completion proof.

## Privacy / Release Safety

This report stores repo-relative artifact paths, public addresses, function names, counts, classifications, caller names, command summaries, and proof boundaries only. It does not include binaries, private absolute paths, source excerpts, decompiled source excerpts, runtime captures, screenshots, frame data, copied executables, copied saves, debugger logs, raw private proof JSON, or private game payloads.
