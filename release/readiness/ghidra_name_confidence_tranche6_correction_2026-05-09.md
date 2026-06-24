# Ghidra Name-Confidence Tranche 6 Correction - 2026-05-09

Status: public-safe saved Ghidra name/comment correction evidence, not final identity or runtime proof

## Objective

Continue the full static Ghidra re-audit by consuming only the three tranche-6 targets that had enough caller/decompile context for conservative saved names.

This wave corrected `0x00411bf0`, `0x00412240`, and `0x00412420` in the saved Ghidra project. It deliberately leaves the five raw-boundary, owner-identity, and table-owner cases queued.

## Inputs

- Rename map: `subagents/ghidra-static-reaudit/name-confidence-tranche6-correction/current/rename_map_tranche6_corrections.txt`
- Comment TSV: `subagents/ghidra-static-reaudit/name-confidence-tranche6-correction/current/comments_after_rename.tsv`
- Metadata read-back: `subagents/ghidra-static-reaudit/name-confidence-tranche6-correction/current/metadata_readback.tsv`
- Decompile read-back index: `subagents/ghidra-static-reaudit/name-confidence-tranche6-correction/current/decompile_readback/index.tsv`
- Xref read-back: `subagents/ghidra-static-reaudit/name-confidence-tranche6-correction/current/xrefs_readback.tsv`
- Instruction read-back: `subagents/ghidra-static-reaudit/name-confidence-tranche6-correction/current/instructions_readback.tsv`
- Probe report: `subagents/ghidra-static-reaudit/name-confidence-tranche6-correction/current/name-confidence-tranche6-correction.json`
- Probe: `tools/ghidra_name_confidence_tranche6_correction_probe.py`
- Probe test: `tools/ghidra_name_confidence_tranche6_correction_probe_test.py`

## Commands

Mutation preflight and apply:

```powershell
py -3 tools\ghidra_rename_map_preflight.py subagents\ghidra-static-reaudit\name-confidence-tranche6-correction\current\rename_map_tranche6_corrections.txt
bash tools/run_ghidra_headless_postscript.sh GhidraBatchRename.java subagents/ghidra-static-reaudit/name-confidence-tranche6-correction/current/rename_map_tranche6_corrections.txt dry
bash tools/run_ghidra_headless_postscript.sh GhidraBatchRename.java subagents/ghidra-static-reaudit/name-confidence-tranche6-correction/current/rename_map_tranche6_corrections.txt apply
bash tools/run_ghidra_headless_postscript.sh GhidraApplyFunctionCommentsFromTsv.java subagents/ghidra-static-reaudit/name-confidence-tranche6-correction/current/comments_after_rename.tsv dry
bash tools/run_ghidra_headless_postscript.sh GhidraApplyFunctionCommentsFromTsv.java subagents/ghidra-static-reaudit/name-confidence-tranche6-correction/current/comments_after_rename.tsv apply
```

Read-back and validation:

```powershell
bash tools/run_ghidra_headless_postscript.sh ExportFunctionMetadataByAddress.java subagents/ghidra-static-reaudit/name-confidence-tranche6-correction/current/addresses.txt subagents/ghidra-static-reaudit/name-confidence-tranche6-correction/current/metadata_readback.tsv
bash tools/run_ghidra_headless_postscript.sh ExportFunctionsByAddressDecompile.java subagents/ghidra-static-reaudit/name-confidence-tranche6-correction/current/addresses.txt subagents/ghidra-static-reaudit/name-confidence-tranche6-correction/current/decompile_readback 220
bash tools/run_ghidra_headless_postscript.sh ExportXrefsForAddresses.java subagents/ghidra-static-reaudit/name-confidence-tranche6-correction/current/addresses.txt subagents/ghidra-static-reaudit/name-confidence-tranche6-correction/current/xrefs_readback.tsv
bash tools/run_ghidra_headless_postscript.sh ExportInstructionsAroundAddresses.java subagents/ghidra-static-reaudit/name-confidence-tranche6-correction/current/addresses.txt subagents/ghidra-static-reaudit/name-confidence-tranche6-correction/current/instructions_readback.tsv 0 28
bash tools/run_ghidra_headless_postscript.sh ExportFunctionQualitySnapshot.java subagents/ghidra-static-reaudit/queue/current/functions_quality.tsv
cmd.exe /c npm run test:ghidra-static-reaudit-queue
py -3 tools\ghidra_name_confidence_tranche6_correction_probe_test.py
py -3 tools\ghidra_name_confidence_tranche6_correction_probe.py --check
py -3 -m py_compile tools\ghidra_name_confidence_tranche6_correction_probe.py tools\ghidra_name_confidence_tranche6_correction_probe_test.py
cmd.exe /c npm run test:ghidra-name-confidence-tranche6-correction
```

## Result

```text
Ghidra name-confidence tranche 6 correction probe
Status: PASS
Targets: 3
Xref rows: 3
Uncertain owners: 4
Address-suffixed wrappers: 5
```

Saved correction summary:

| Address | Previous name | Saved name | Scope |
| --- | --- | --- | --- |
| `0x00411bf0` | `CEngine_Unk_0050a080__Wrapper_00411bf0` | `CGeneralVolume__DispatchMode3BurstProgressAndSpawn` | Mode-3 GeneralVolume burst-dispatch helper context. |
| `0x00412240` | `ROUND__Wrapper_00412240` | `CGeneralVolume__GetMode3CurrentEntryRoundedSlotValue` | Mode-3 current-entry rounded slot-value helper. |
| `0x00412420` | `CText_GetStringById__Wrapper_00412420` | `CGeneralVolume__GetMode3CurrentEntryDisplayString` | Mode-3 current-entry display-string helper. |

Still queued after this correction pass:

- `0x00402dd0` remains a shadow/heightfield corner-test raw-caller boundary question.
- `0x0040dda0` remains a UnitAI-like grid cooldown/stamp owner-identity question.
- `0x00412830` remains a cockpit disable/reselect raw-caller boundary question.
- `0x00413660` remained a scaled energy-drain raw jump-table/case boundary question at the end of this pass; the later GeneralVolume axis-correction note records that it was consumed as `CGeneralVolume__ApplyYawInputByWeaponClass`.
- `0x00418090` remains an opening-animation state callback table-owner question.

## What This Proves

- The three selected tranche-6 correction targets now have saved behavior-backed names in the Ghidra project.
- The three selected targets have saved proof-boundary comments.
- Metadata, decompile, xref, and instruction read-back still contain the checked context after mutation.
- The refreshed quality queue now reports `4` broad uncertain-owner names and `5` address-suffixed wrappers, while comments remain `368` and commentless functions remain `5495`.

## What This Does Not Prove

- This does not harden signatures, parameter names, local names, structures, or tags.
- This does not prove exact source method identity for the affected bodies.
- This does not prove weapon-fired stealth reset behavior, runtime behavior, gameplay correctness, or rebuild parity.
- This does not resolve the five remaining name-confidence queue deferrals.
- This does not patch, launch, or mutate `BEA.exe` or the installed game.

## Privacy / Release Safety

This report stores repo-relative artifact paths, public addresses, function names, counts, command summaries, and proof boundaries only. It does not include binaries, private absolute paths, source excerpts, decompiled source excerpts, runtime captures, screenshots, frame data, copied executables, copied saves, debugger logs, raw private proof JSON, or private game payloads.
