# Ghidra Name-Confidence Deferral Correction - 2026-05-09

Status: public-safe saved Ghidra boundary/name correction evidence, not final identity or runtime proof

## Objective

Continue the full static Ghidra re-audit by revisiting one of the remaining name-confidence deferrals instead of treating the saved labels as final.

This wave recovered two raw function boundaries around the volume-entry group dispatch path and corrected one stale owner label. It deliberately keeps the remaining deferrals queued.

## Inputs

- Create-function map: `subagents/ghidra-static-reaudit/name-confidence-deferrals/current/create_function_targets.txt`
- Rename map: `subagents/ghidra-static-reaudit/name-confidence-deferrals/current/rename_map_corrections.txt`
- Comment TSV: `subagents/ghidra-static-reaudit/name-confidence-deferrals/current/comments_after_correction.tsv`
- Metadata read-back: `subagents/ghidra-static-reaudit/name-confidence-deferrals/current/metadata_readback.tsv`
- Decompile read-back index: `subagents/ghidra-static-reaudit/name-confidence-deferrals/current/decompile_readback/index.tsv`
- Xref read-back: `subagents/ghidra-static-reaudit/name-confidence-deferrals/current/xrefs_readback.tsv`
- Instruction read-back: `subagents/ghidra-static-reaudit/name-confidence-deferrals/current/instructions_readback.tsv`
- Probe report: `subagents/ghidra-static-reaudit/name-confidence-deferrals/current/name-confidence-deferral-correction.json`
- Probe: `tools/ghidra_name_confidence_deferral_correction_probe.py`
- Probe test: `tools/ghidra_name_confidence_deferral_correction_probe_test.py`

## Commands

Mutation preflight and apply:

```powershell
py -3 tools\ghidra_rename_map_preflight.py subagents\ghidra-static-reaudit\name-confidence-deferrals\current\rename_map_corrections.txt
bash tools/run_ghidra_headless_postscript.sh CreateFunctionsFromAddressList.java subagents/ghidra-static-reaudit/name-confidence-deferrals/current/create_function_targets.txt subagents/ghidra-static-reaudit/name-confidence-deferrals/current/create_function_dry.tsv dry
bash tools/run_ghidra_headless_postscript.sh CreateFunctionsFromAddressList.java subagents/ghidra-static-reaudit/name-confidence-deferrals/current/create_function_targets.txt subagents/ghidra-static-reaudit/name-confidence-deferrals/current/create_function_apply.tsv apply
bash tools/run_ghidra_headless_postscript.sh GhidraBatchRename.java subagents/ghidra-static-reaudit/name-confidence-deferrals/current/rename_map_corrections.txt dry
bash tools/run_ghidra_headless_postscript.sh GhidraBatchRename.java subagents/ghidra-static-reaudit/name-confidence-deferrals/current/rename_map_corrections.txt apply
bash tools/run_ghidra_headless_postscript.sh GhidraApplyFunctionCommentsFromTsv.java subagents/ghidra-static-reaudit/name-confidence-deferrals/current/comments_after_correction.tsv dry
bash tools/run_ghidra_headless_postscript.sh GhidraApplyFunctionCommentsFromTsv.java subagents/ghidra-static-reaudit/name-confidence-deferrals/current/comments_after_correction.tsv apply
```

Read-back and validation:

```powershell
bash tools/run_ghidra_headless_postscript.sh ExportFunctionMetadataByAddress.java subagents/ghidra-static-reaudit/name-confidence-deferrals/current/correction_readback_addresses.txt subagents/ghidra-static-reaudit/name-confidence-deferrals/current/metadata_readback.tsv
bash tools/run_ghidra_headless_postscript.sh ExportFunctionsByAddressDecompile.java subagents/ghidra-static-reaudit/name-confidence-deferrals/current/correction_readback_addresses.txt subagents/ghidra-static-reaudit/name-confidence-deferrals/current/decompile_readback 220
bash tools/run_ghidra_headless_postscript.sh ExportXrefsForAddresses.java subagents/ghidra-static-reaudit/name-confidence-deferrals/current/correction_readback_addresses.txt subagents/ghidra-static-reaudit/name-confidence-deferrals/current/xrefs_readback.tsv
bash tools/run_ghidra_headless_postscript.sh ExportInstructionsAroundAddresses.java subagents/ghidra-static-reaudit/name-confidence-deferrals/current/correction_readback_addresses.txt subagents/ghidra-static-reaudit/name-confidence-deferrals/current/instructions_readback.tsv 0 22
bash tools/run_ghidra_headless_postscript.sh ExportFunctionQualitySnapshot.java subagents/ghidra-static-reaudit/queue/current/functions_quality.tsv
cmd.exe /c npm run test:ghidra-static-reaudit-queue
py -3 tools\ghidra_name_confidence_deferral_correction_probe_test.py
py -3 tools\ghidra_name_confidence_deferral_correction_probe.py --check
py -3 -m py_compile tools\ghidra_name_confidence_deferral_correction_probe.py tools\ghidra_name_confidence_deferral_correction_probe_test.py
cmd.exe /c npm run test:ghidra-name-confidence-deferral-correction
```

## Result

```text
Ghidra name-confidence deferral correction probe
Status: PASS
Targets: 3
Created functions: 2
Corrected renames: 1
Total functions: 5865
Uncertain owners: 3
Address-suffixed wrappers: 4
```

Saved correction summary:

| Address | Previous state | Saved state | Scope |
| --- | --- | --- | --- |
| `0x0040dc30` | No function object at this raw table target | `CExplosionInitThing__EnableVolumeEntryGroupsByName` | Recovered dispatch stub that enables both GeneralVolume entry groups by name. |
| `0x0040dc60` | No function object at this raw table target | `CExplosionInitThing__DisableVolumeEntryGroupsByNameAndReselect` | Recovered dispatch stub that disables both GeneralVolume entry groups by name and reselects as needed. |
| `0x00412830` | `CCockpit_Unk_00411e70__Wrapper_00412830` | `CGeneralVolume__DisableLinkedEntriesByNameAndReselect` | Corrected stale cockpit owner label to the linked GeneralVolume disable/reselect helper used by `0x0040dc60`. |

Still queued after this correction pass:

- `0x00402dd0` remains a shadow/heightfield corner-test raw-caller boundary question.
- `0x0040dda0` remains a UnitAI-like grid cooldown/stamp owner-identity question.
- `0x00413660` remained a scaled energy-drain raw jump-table/case boundary question at the end of this pass; the later GeneralVolume axis-correction note records that it was consumed as `CGeneralVolume__ApplyYawInputByWeaponClass`.
- `0x00418090` remains an opening-animation state callback table-owner question.

## What This Proves

- The saved Ghidra project now has recovered function boundaries at `0x0040dc30` and `0x0040dc60`.
- The saved Ghidra name for `0x00412830` was corrected away from a stale `CCockpit` wrapper label to a GeneralVolume linked-entry disable/reselect helper.
- Metadata, decompile, xref, instruction-ownership, and queue read-back match the corrected state.
- The refreshed quality queue now reports `5865` total functions, `3` broad uncertain-owner names, `4` address-suffixed wrappers, `370` commented functions, and `5495` commentless functions.

## What This Does Not Prove

- This does not harden signatures, parameter names, local names, structures, or tags.
- This does not prove exact source method identity for the affected bodies.
- This does not prove runtime behavior, gameplay correctness, or rebuild parity.
- This does not resolve the remaining four name-confidence queue deferrals.
- This does not patch, launch, or mutate `BEA.exe` or the installed game.

## Privacy / Release Safety

This report stores repo-relative artifact paths, public addresses, function names, counts, command summaries, and proof boundaries only. It does not include binaries, private absolute paths, source excerpts, decompiled source excerpts, runtime captures, screenshots, frame data, copied executables, copied saves, debugger logs, raw private proof JSON, or private game payloads.
