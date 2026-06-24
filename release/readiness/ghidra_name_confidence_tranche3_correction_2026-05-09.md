# Ghidra Name-Confidence Tranche 3 Correction - 2026-05-09

Status: public-safe saved Ghidra rename/comment correction, not final identity or runtime proof

## Objective

Consume the six third-tranche name-confidence candidates with conservative saved Ghidra names and proof-boundary comments after the read-only classification pass showed the existing labels were stale or too weak.

This wave treats saved Ghidra names as reparsable hypotheses. It corrects labels only where the current decompile, xref, instruction, and caller context support a narrower behavior-backed name, and it preserves signature/type/tag/source/runtime caveats in the saved comments.

## Inputs

- Rename map: `subagents/ghidra-static-reaudit/name-confidence-tranche3-correction/current/rename_map_tranche3_corrections.txt`
- Comment TSV: `subagents/ghidra-static-reaudit/name-confidence-tranche3-correction/current/comments_after_rename.tsv`
- Read-back metadata: `subagents/ghidra-static-reaudit/name-confidence-tranche3-correction/current/metadata_readback.tsv`
- Read-back decompile index: `subagents/ghidra-static-reaudit/name-confidence-tranche3-correction/current/decompile_readback/index.tsv`
- Read-back xrefs: `subagents/ghidra-static-reaudit/name-confidence-tranche3-correction/current/xrefs_readback.tsv`
- Read-back instructions: `subagents/ghidra-static-reaudit/name-confidence-tranche3-correction/current/instructions_readback.tsv`
- Queue snapshot: `subagents/ghidra-static-reaudit/queue/current/static-reaudit-queue.json`
- Probe: `tools/ghidra_name_confidence_tranche3_correction_probe.py`
- Probe test: `tools/ghidra_name_confidence_tranche3_correction_probe_test.py`

## Commands

Preflight and mutation:

```powershell
py -3 tools\ghidra_rename_map_preflight.py subagents\ghidra-static-reaudit\name-confidence-tranche3-correction\current\rename_map_tranche3_corrections.txt
bash tools/run_ghidra_batch_rename_headless.sh subagents/ghidra-static-reaudit/name-confidence-tranche3-correction/current/rename_map_tranche3_corrections.txt dry
cmd.exe /c <analyzeHeadless.bat> <ghidra-project-root> BEA -process BEA.exe -noanalysis -scriptPath tools -postScript GhidraBatchRename.java subagents/ghidra-static-reaudit/name-confidence-tranche3-correction/current/rename_map_tranche3_corrections.txt dry
cmd.exe /c <analyzeHeadless.bat> <ghidra-project-root> BEA -process BEA.exe -noanalysis -scriptPath tools -postScript GhidraBatchRename.java subagents/ghidra-static-reaudit/name-confidence-tranche3-correction/current/rename_map_tranche3_corrections.txt apply
cmd.exe /c <analyzeHeadless.bat> <ghidra-project-root> BEA -process BEA.exe -noanalysis -scriptPath tools -postScript GhidraApplyFunctionCommentsFromTsv.java subagents/ghidra-static-reaudit/name-confidence-tranche3-correction/current/comments_after_rename.tsv dry
cmd.exe /c <analyzeHeadless.bat> <ghidra-project-root> BEA -process BEA.exe -noanalysis -scriptPath tools -postScript GhidraApplyFunctionCommentsFromTsv.java subagents/ghidra-static-reaudit/name-confidence-tranche3-correction/current/comments_after_rename.tsv apply
```

The bash rename wrapper failed before launching Ghidra because it expanded a Windows path into `C:\mnt\c\...`. The rename-map preflight had already passed, so the same dry/apply operation was rerun directly through `analyzeHeadless.bat`.

Read-back and validation:

```powershell
bash tools/run_ghidra_headless_postscript.sh ExportFunctionMetadataByAddress.java subagents/ghidra-static-reaudit/name-confidence-tranche3-correction/current/addresses.txt subagents/ghidra-static-reaudit/name-confidence-tranche3-correction/current/metadata_readback.tsv
bash tools/run_ghidra_headless_postscript.sh ExportFunctionsByAddressDecompile.java subagents/ghidra-static-reaudit/name-confidence-tranche3-correction/current/addresses.txt subagents/ghidra-static-reaudit/name-confidence-tranche3-correction/current/decompile_readback 120
bash tools/run_ghidra_headless_postscript.sh ExportXrefsForAddresses.java subagents/ghidra-static-reaudit/name-confidence-tranche3-correction/current/addresses.txt subagents/ghidra-static-reaudit/name-confidence-tranche3-correction/current/xrefs_readback.tsv
bash tools/run_ghidra_headless_postscript.sh ExportInstructionsAroundAddresses.java subagents/ghidra-static-reaudit/name-confidence-tranche3-correction/current/addresses.txt subagents/ghidra-static-reaudit/name-confidence-tranche3-correction/current/instructions_readback.tsv 0 16
bash tools/run_ghidra_headless_postscript.sh ExportFunctionQualitySnapshot.java subagents/ghidra-static-reaudit/queue/current/functions_quality.tsv
cmd.exe /c npm run test:ghidra-static-reaudit-queue
py -3 tools\ghidra_name_confidence_tranche3_correction_probe_test.py
py -3 tools\ghidra_name_confidence_tranche3_correction_probe.py --check
py -3 -m py_compile tools\ghidra_name_confidence_tranche3_correction_probe.py tools\ghidra_name_confidence_tranche3_correction_probe_test.py
cmd.exe /c npm run test:ghidra-name-confidence-tranche3-correction
```

## Result

```text
Rename-map preflight: PASS; rows accepted 6; findings 0
Wrapper dry-run: failed before Ghidra launch due Windows path expansion
Direct rename dry-run: PASS; applied=0 skipped=6 missing=0 bad=0
Direct rename apply: PASS; applied=6 skipped=0 missing=0 bad=0
Comment dry-run: PASS; applied=0 skipped=6 missing=0 bad=0
Comment apply: PASS; applied=6 skipped=0 missing=0 bad=0
Metadata read-back: PASS; found 6/6
Decompile read-back: PASS; dumped 6/6
Xref read-back: PASS; rows 22
Instruction read-back: PASS; rows 102
Queue snapshot: PASS; total functions 5863; commented functions 368
Correction probe: PASS
```

Saved corrections:

| Address | Previous name | Saved name | Scope |
| --- | --- | --- | --- |
| `0x0050b010` | `CWorld__DispatchHelper_004bc480` | `CWorld__AddUnitToOccupancyGridAndRebuildShadows_Thunk` | Thin wrapper into the CWorld occupancy-grid add / shadow rebuild helper. |
| `0x0050b020` | `CWorld__DispatchHelper_004bc3e0` | `CWorld__RemoveUnitFromOccupancyGrid_Thunk` | Thin wrapper into the CWorld occupancy-grid removal helper. |
| `0x0053f7d0` | `CWaypoint_Unk_004f7cd0__Wrapper_0053f7d0` | `CDXBitmapFont__InitNamedFontSlot` | Bitmap-font slot initializer reached from `PCPlatform__LoadFonts`. |
| `0x0055e412` | `CRT__CallHelper_00564a0b_NoFlags` | `CDXTexture__LoadPathFallbackNoFlags_Thunk` | Texture path/fallback load wrapper with fixed no-flags behavior. Wave631 later corrected this stale texture label to `CRT__SpawnPathVarargsNoEnv_Thunk`. |
| `0x0055e45f` | `CRT__CallHelper_00564c09_WithAutoUnlock` | `CRT__OpenFileByModeString_AutoUnlock` | CRT file-open-by-mode wrapper with auto-unlock path. |
| `0x0056d21c` | `CRT__IsDigit_Wrapper_0056d21c` | `CRT__IsDigitCharTypeMask_Thunk` | Ctype digit-mask thunk; saved signature still needs review. |

Refreshed queue snapshot after the correction:

| Metric | Value |
| --- | ---: |
| Total functions | `5863` |
| Functions with comments | `368` |
| Commentless functions | `5495` |
| Undefined signatures | `2087` |
| `param_N` signatures | `2563` |
| Uncertain owner names | `9` |
| Address-suffixed helper names | `0` |
| Address-suffixed wrapper names | `16` |

## What This Proves

- The saved Ghidra project now has behavior-backed conservative names for all six third-tranche correction targets.
- The saved comments record proof boundaries for each correction and keep unresolved signature/type/tag/source/runtime claims open.
- Read-back metadata, decompile, xref, and instruction exports still contain the behavior/caller context that justified the corrections.
- The whole-database static re-audit queue advanced from `362` to `368` commented functions and from `5501` to `5495` commentless functions.

## What This Does Not Prove

- This does not harden signatures, parameters, local names, structures, data types, tags, or function boundaries.
- This does not prove exact source-to-retail identity.
- This does not prove runtime behavior.
- This does not certify the rest of the saved Ghidra database as correct.
- `CRT__IsDigitCharTypeMask_Thunk` still has a saved `void` signature that needs future review.
- This does not patch, launch, or mutate `BEA.exe` or the installed game.

## Outcome

This is a saved Ghidra quality improvement and a queue reduction, not completion of the static RE campaign. The next static re-audit wave should continue from the refreshed queue, prioritizing remaining uncertain-owner or wrapper names and then signature/type/tag hardening in small evidence-backed tranches.

## Privacy / Release Safety

This report stores repo-relative artifact paths, public addresses, function names, counts, command summaries, and proof boundaries only. It does not include binaries, private absolute asset paths, source excerpts, decompiled source excerpts, runtime captures, screenshots, frame data, copied executables, copied saves, debugger logs, raw private proof JSON, or private game payloads.
