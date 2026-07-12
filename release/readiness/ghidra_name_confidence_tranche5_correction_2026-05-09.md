# Ghidra Name-Confidence Tranche 5 Correction - 2026-05-09

> **Identity status update (2026-07-12):** `0x00412ad0` remains unresolved.
> Its historical Monitor surface-alignment label is not current owner or
> method proof. See the [current movement crosswalk](../../reverse-engineering/binary-analysis/battleengine-movement-static-crosswalk-2026-07-12.md).

Status: public-safe saved Ghidra name/comment correction evidence, not final identity or runtime proof

## Objective

Continue the full static Ghidra re-audit by reviewing the remaining name-confidence queue and saving only the clearest source/decompile/xref-backed corrections.

This wave first exported read-only metadata, decompile, xref, and instruction context for all `12` remaining name-confidence queue targets. It then saved four conservative corrections and left the other eight queued.

## Inputs

- Full tranche address list: `subagents/ghidra-static-reaudit/name-confidence-tranche5/current/addresses.txt`
- Full tranche read-only exports: `subagents/ghidra-static-reaudit/name-confidence-tranche5/current/`
- Rename map: `subagents/ghidra-static-reaudit/name-confidence-tranche5-correction/current/rename_map_tranche5_corrections.txt`
- Comment TSV: `subagents/ghidra-static-reaudit/name-confidence-tranche5-correction/current/comments_after_rename.tsv`
- Metadata read-back: `subagents/ghidra-static-reaudit/name-confidence-tranche5-correction/current/metadata_readback.tsv`
- Decompile read-back index: `subagents/ghidra-static-reaudit/name-confidence-tranche5-correction/current/decompile_readback/index.tsv`
- Xref read-back: `subagents/ghidra-static-reaudit/name-confidence-tranche5-correction/current/xrefs_readback.tsv`
- Instruction read-back: `subagents/ghidra-static-reaudit/name-confidence-tranche5-correction/current/instructions_readback.tsv`
- Probe report: `subagents/ghidra-static-reaudit/name-confidence-tranche5-correction/current/name-confidence-tranche5-correction.json`
- Probe: `tools/ghidra_name_confidence_tranche5_correction_probe.py`
- Probe test: `tools/ghidra_name_confidence_tranche5_correction_probe_test.py`

## Commands

Read-only tranche export:

```powershell
bash tools/run_ghidra_headless_postscript.sh ExportFunctionMetadataByAddress.java subagents/ghidra-static-reaudit/name-confidence-tranche5/current/addresses.txt subagents/ghidra-static-reaudit/name-confidence-tranche5/current/metadata.tsv
bash tools/run_ghidra_headless_postscript.sh ExportFunctionsByAddressDecompile.java subagents/ghidra-static-reaudit/name-confidence-tranche5/current/addresses.txt subagents/ghidra-static-reaudit/name-confidence-tranche5/current/decompile 180
bash tools/run_ghidra_headless_postscript.sh ExportXrefsForAddresses.java subagents/ghidra-static-reaudit/name-confidence-tranche5/current/addresses.txt subagents/ghidra-static-reaudit/name-confidence-tranche5/current/xrefs.tsv
bash tools/run_ghidra_headless_postscript.sh ExportInstructionsAroundAddresses.java subagents/ghidra-static-reaudit/name-confidence-tranche5/current/addresses.txt subagents/ghidra-static-reaudit/name-confidence-tranche5/current/instructions.tsv 0 24
```

Mutation preflight and apply:

```powershell
py -3 tools\ghidra_rename_map_preflight.py subagents\ghidra-static-reaudit\name-confidence-tranche5-correction\current\rename_map_tranche5_corrections.txt
bash tools/run_ghidra_headless_postscript.sh GhidraBatchRename.java subagents/ghidra-static-reaudit/name-confidence-tranche5-correction/current/rename_map_tranche5_corrections.txt dry
bash tools/run_ghidra_headless_postscript.sh GhidraBatchRename.java subagents/ghidra-static-reaudit/name-confidence-tranche5-correction/current/rename_map_tranche5_corrections.txt apply
bash tools/run_ghidra_headless_postscript.sh GhidraApplyFunctionCommentsFromTsv.java subagents/ghidra-static-reaudit/name-confidence-tranche5-correction/current/comments_after_rename.tsv dry
bash tools/run_ghidra_headless_postscript.sh GhidraApplyFunctionCommentsFromTsv.java subagents/ghidra-static-reaudit/name-confidence-tranche5-correction/current/comments_after_rename.tsv apply
```

Read-back and validation:

```powershell
bash tools/run_ghidra_headless_postscript.sh ExportFunctionMetadataByAddress.java subagents/ghidra-static-reaudit/name-confidence-tranche5-correction/current/addresses.txt subagents/ghidra-static-reaudit/name-confidence-tranche5-correction/current/metadata_readback.tsv
bash tools/run_ghidra_headless_postscript.sh ExportFunctionsByAddressDecompile.java subagents/ghidra-static-reaudit/name-confidence-tranche5-correction/current/addresses.txt subagents/ghidra-static-reaudit/name-confidence-tranche5-correction/current/decompile_readback 180
bash tools/run_ghidra_headless_postscript.sh ExportXrefsForAddresses.java subagents/ghidra-static-reaudit/name-confidence-tranche5-correction/current/addresses.txt subagents/ghidra-static-reaudit/name-confidence-tranche5-correction/current/xrefs_readback.tsv
bash tools/run_ghidra_headless_postscript.sh ExportInstructionsAroundAddresses.java subagents/ghidra-static-reaudit/name-confidence-tranche5-correction/current/addresses.txt subagents/ghidra-static-reaudit/name-confidence-tranche5-correction/current/instructions_readback.tsv 0 24
bash tools/run_ghidra_headless_postscript.sh ExportFunctionQualitySnapshot.java subagents/ghidra-static-reaudit/queue/current/functions_quality.tsv
cmd.exe /c npm run test:ghidra-static-reaudit-queue
py -3 tools\ghidra_name_confidence_tranche5_correction_probe_test.py
py -3 tools\ghidra_name_confidence_tranche5_correction_probe.py --check
py -3 -m py_compile tools\ghidra_name_confidence_tranche5_correction_probe.py tools\ghidra_name_confidence_tranche5_correction_probe_test.py
cmd.exe /c npm run test:ghidra-name-confidence-tranche5-correction
```

## Result

```text
Ghidra name-confidence tranche 5 correction probe
Status: PASS
Targets: 4
Xref rows: 9
Uncertain owners: 5
Address-suffixed wrappers: 8
```

Saved correction summary:

| Address | Previous name | Saved name | Scope |
| --- | --- | --- | --- |
| `0x00412650` | `CSPtrSet_Remove__Wrapper_00412650` | `CBattleEngineJetPart__ResetConfiguration` | Source-aligned jet-part weapon reset/configuration candidate. |
| `0x00412ad0` | `ABS__Wrapper_00412ad0` | `CMonitor__UpdateSurfaceAlignmentAngle` | Monitor surface-alignment angle update helper. |
| `0x004146b0` | `CSPtrSet_Remove__Wrapper_004146b0` | `CBattleEngineWalkerPart__ResetConfiguration` | Source-aligned walker-part weapon/primary/augmented reset/configuration candidate. |
| `0x004d3080` | `CGenericActiveReader_SetReader__Wrapper_004d3080` | `CPlayer__AssignBattleEngine` | Source-aligned player BattleEngine active-reader assignment candidate. |

Still queued after this correction pass:

- `0x00402dd0` remains a shadow/heightfield corner-test owner-identity question.
- `0x0040dda0` remains a UnitAI grid cooldown/stamp caller/owner review question.
- `0x00411bf0` remains a mode-specific burst-dispatch owner/name review question.
- `0x00412240` remains a selected-entry rounded slot-value helper review question.
- `0x00412420` remains a selected-entry display-string helper review question.
- `0x00412830` remains a weapon disable/reselect owner-boundary review question.
- `0x00413660` remained a general-volume scaled drain method-boundary review question at the end of this pass; the later GeneralVolume axis-correction note records that it was consumed as `CGeneralVolume__ApplyYawInputByWeaponClass`.
- `0x00418090` remains an opening-animation state callback table/owner review question.

## What This Proves

- The four selected tranche-5 correction targets now have saved source/decompile/xref-backed names in the Ghidra project.
- The four selected targets have saved proof-boundary comments.
- Metadata, decompile, xref, and instruction read-back still contain the checked context after mutation.
- The refreshed quality queue now reports `8` address-suffixed wrappers, while uncertain-owner names remain `5`, comments remain `368`, and commentless functions remain `5495`.

## What This Does Not Prove

- This does not harden signatures, parameter names, local names, structures, or tags.
- This does not prove every remaining wrapper or uncertain-owner name is wrong or right.
- This does not prove exact source-to-retail identity for every affected body.
- This does not prove runtime behavior, gameplay correctness, or rebuild parity.
- This does not patch, launch, or mutate `BEA.exe` or the installed game.

## Privacy / Release Safety

This report stores repo-relative artifact paths, public addresses, function names, counts, command summaries, and proof boundaries only. It does not include binaries, private absolute paths, source excerpts, decompiled source excerpts, runtime captures, screenshots, frame data, copied executables, copied saves, debugger logs, raw private proof JSON, or private game payloads.
