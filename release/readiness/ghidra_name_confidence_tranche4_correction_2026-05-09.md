# Ghidra Name-Confidence Tranche 4 Correction - 2026-05-09

Status: public-safe saved Ghidra name/comment correction evidence, not final identity or runtime proof

## Objective

Consume only the four stronger correction candidates from the fourth name-confidence classification tranche and leave the two deferred targets untouched.

The selected targets were already reviewed read-only in `release/readiness/ghidra_name_confidence_tranche4_2026-05-09.md`. This follow-up saves conservative behavior-backed names and proof-boundary comments for the three rename candidates and the one owner-correction candidate.

## Inputs

- Rename map: `subagents/ghidra-static-reaudit/name-confidence-tranche4-correction/current/rename_map_tranche4_corrections.txt`
- Comment TSV: `subagents/ghidra-static-reaudit/name-confidence-tranche4-correction/current/comments_after_rename.tsv`
- Metadata read-back: `subagents/ghidra-static-reaudit/name-confidence-tranche4-correction/current/metadata_readback.tsv`
- Decompile read-back index: `subagents/ghidra-static-reaudit/name-confidence-tranche4-correction/current/decompile_readback/index.tsv`
- Xref read-back: `subagents/ghidra-static-reaudit/name-confidence-tranche4-correction/current/xrefs_readback.tsv`
- Instruction read-back: `subagents/ghidra-static-reaudit/name-confidence-tranche4-correction/current/instructions_readback.tsv`
- Probe report: `subagents/ghidra-static-reaudit/name-confidence-tranche4-correction/current/name-confidence-tranche4-correction.json`
- Probe: `tools/ghidra_name_confidence_tranche4_correction_probe.py`
- Probe test: `tools/ghidra_name_confidence_tranche4_correction_probe_test.py`

## Commands

Mutation preflight and apply:

```powershell
py -3 tools\ghidra_rename_map_preflight.py subagents\ghidra-static-reaudit\name-confidence-tranche4-correction\current\rename_map_tranche4_corrections.txt
bash tools/run_ghidra_headless_postscript.sh GhidraBatchRename.java subagents/ghidra-static-reaudit/name-confidence-tranche4-correction/current/rename_map_tranche4_corrections.txt dry
bash tools/run_ghidra_headless_postscript.sh GhidraBatchRename.java subagents/ghidra-static-reaudit/name-confidence-tranche4-correction/current/rename_map_tranche4_corrections.txt apply
bash tools/run_ghidra_headless_postscript.sh GhidraApplyFunctionCommentsFromTsv.java subagents/ghidra-static-reaudit/name-confidence-tranche4-correction/current/comments_after_rename.tsv dry
bash tools/run_ghidra_headless_postscript.sh GhidraApplyFunctionCommentsFromTsv.java subagents/ghidra-static-reaudit/name-confidence-tranche4-correction/current/comments_after_rename.tsv apply
```

Read-back and validation:

```powershell
bash tools/run_ghidra_headless_postscript.sh ExportFunctionMetadataByAddress.java subagents/ghidra-static-reaudit/name-confidence-tranche4-correction/current/addresses.txt subagents/ghidra-static-reaudit/name-confidence-tranche4-correction/current/metadata_readback.tsv
bash tools/run_ghidra_headless_postscript.sh ExportFunctionsByAddressDecompile.java subagents/ghidra-static-reaudit/name-confidence-tranche4-correction/current/addresses.txt subagents/ghidra-static-reaudit/name-confidence-tranche4-correction/current/decompile_readback 140
bash tools/run_ghidra_headless_postscript.sh ExportXrefsForAddresses.java subagents/ghidra-static-reaudit/name-confidence-tranche4-correction/current/addresses.txt subagents/ghidra-static-reaudit/name-confidence-tranche4-correction/current/xrefs_readback.tsv
bash tools/run_ghidra_headless_postscript.sh ExportInstructionsAroundAddresses.java subagents/ghidra-static-reaudit/name-confidence-tranche4-correction/current/addresses.txt subagents/ghidra-static-reaudit/name-confidence-tranche4-correction/current/instructions_readback.tsv 0 18
bash tools/run_ghidra_headless_postscript.sh ExportFunctionQualitySnapshot.java subagents/ghidra-static-reaudit/queue/current/functions_quality.tsv
cmd.exe /c npm run test:ghidra-static-reaudit-queue
py -3 tools\ghidra_name_confidence_tranche4_correction_probe_test.py
py -3 tools\ghidra_name_confidence_tranche4_correction_probe.py --check
py -3 -m py_compile tools\ghidra_name_confidence_tranche4_correction_probe.py tools\ghidra_name_confidence_tranche4_correction_probe_test.py
cmd.exe /c npm run test:ghidra-name-confidence-tranche4-correction
```

## Result

```text
Ghidra name-confidence tranche 4 correction probe
Status: PASS
Targets: 4
Xref rows: 15
Uncertain owners: 5
Address-suffixed wrappers: 12
```

Saved correction summary:

| Address | Previous name | Saved name | Scope |
| --- | --- | --- | --- |
| `0x00403ff0` | `CFastVB_Unk_0055db0a__Wrapper_00403ff0` | `CDXLandscape__DestroyResourceDescriptorArray_Thunk` | Resource-descriptor array destroy thunk. |
| `0x0040dcc0` | `CGeneralVolume_Unk_0040a580__Wrapper_0040dcc0` | `CMonitor__ResetTransitionFlagAndUpdateIfState3_Thunk` | Monitor transition-state flag reset and conditional update thunk. |
| `0x00410670` | `CGeneralVolume_Unk_00409e60__Wrapper_00410670` | `CGeneralVolume__DrainLinkedObjectFromVelocity` | General-volume linked-object velocity-scaled drain/update body. |
| `0x00411b90` | `CEngine_Unk_00506010__Wrapper_00411b90` | `CGeneralVolume__DispatchSelectedBurstPreset` | General-volume selected burst-preset dispatch body. |

Deferred from this correction pass:

- `0x00402dd0` remains a shadow/heightfield corner-test owner-identity question.
- `0x0040dda0` remains a UnitAI grid cooldown/stamp caller/owner review question.

## What This Proves

- The four selected tranche-4 correction targets now have saved behavior-backed names in the Ghidra project.
- The four selected targets have saved proof-boundary comments.
- Metadata, decompile, xref, and instruction read-back still contain the checked context after mutation.
- The refreshed quality queue now reports `5` uncertain-owner names and `12` address-suffixed wrappers, while comments remain `368` and commentless functions remain `5495`.

## What This Does Not Prove

- This does not harden signatures, parameter names, local names, structures, or tags.
- This does not prove exact source-to-retail identity.
- This does not prove runtime behavior.
- This does not prove `CWeapon::Fire`, `CBattleEngine::WeaponFired`, weapon-fired stealth reset, runtime cloak activation, or fire-while-cloaked behavior.
- This does not patch, launch, or mutate `BEA.exe` or the installed game.

## Privacy / Release Safety

This report stores repo-relative artifact paths, public addresses, function names, counts, command summaries, and proof boundaries only. It does not include binaries, private absolute paths, source excerpts, decompiled source excerpts, runtime captures, screenshots, frame data, copied executables, copied saves, debugger logs, raw private proof JSON, or private game payloads.
