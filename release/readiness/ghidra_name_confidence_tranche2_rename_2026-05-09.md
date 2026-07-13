# Ghidra Name-Confidence Tranche 2 Rename Pass - 2026-05-09

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 live correction closeout:** Historical record; `0x00406560` → `CBattleEngine__HandleLocks` (was `CBattleEngine__UpdateAutoTargetSetAndFireProjectiles`). The original text below remains provenance rather than current semantic authority. It is superseded only where confirmed. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); final per-address decisions and exact before/after metadata are in `reverse-engineering/binary-analysis/ghidra-reviewed-correction-decisions-2026-07-13.jsonl` and `reverse-engineering/binary-analysis/ghidra-reviewed-correction-plan-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Status: public-safe saved-Ghidra correction evidence, not final type/signature/runtime proof

## Objective

Consume the two rename candidates from `release/readiness/ghidra_name_confidence_tranche2_2026-05-09.md` with the normal Ghidra mutation discipline: conservative names, rename-map preflight, headless dry/apply, proof-boundary comments, and read-back exports.

This pass updates only:

- `0x00414b30`: `CVBufTexture_Unk_0050a290__Wrapper_00414b30` -> `TargetSet__AnyUnitTargetTimeoutBeforeProfileLimit`
- `0x00505c30`: `stricmp__Wrapper_00505c30` -> `NamedEntryList__FindNearestChildByNameAndPosition`

## Inputs

- Rename map: `subagents/ghidra-static-reaudit/name-confidence-tranche2-rename/current/rename_map_tranche2_candidates.txt`
- Comment TSV: `subagents/ghidra-static-reaudit/name-confidence-tranche2-rename/current/comments_tranche2_candidates.tsv`
- Metadata read-back: `subagents/ghidra-static-reaudit/name-confidence-tranche2-rename/current/metadata_after.tsv`
- Decompile read-back index: `subagents/ghidra-static-reaudit/name-confidence-tranche2-rename/current/decompile_after/index.tsv`
- Xref read-back: `subagents/ghidra-static-reaudit/name-confidence-tranche2-rename/current/xrefs_after.tsv`
- Probe: `tools/ghidra_name_confidence_tranche2_rename_probe.py`
- Probe test: `tools/ghidra_name_confidence_tranche2_rename_probe_test.py`

## Commands

Ghidra mutation/read-back:

```powershell
py -3 tools\ghidra_rename_map_preflight.py subagents\ghidra-static-reaudit\name-confidence-tranche2-rename\current\rename_map_tranche2_candidates.txt
bash tools/run_ghidra_headless_postscript.sh GhidraBatchRename.java subagents/ghidra-static-reaudit/name-confidence-tranche2-rename/current/rename_map_tranche2_candidates.txt dry
bash tools/run_ghidra_headless_postscript.sh GhidraBatchRename.java subagents/ghidra-static-reaudit/name-confidence-tranche2-rename/current/rename_map_tranche2_candidates.txt apply
bash tools/run_ghidra_headless_postscript.sh GhidraApplyFunctionCommentsFromTsv.java subagents/ghidra-static-reaudit/name-confidence-tranche2-rename/current/comments_tranche2_candidates.tsv dry
bash tools/run_ghidra_headless_postscript.sh GhidraApplyFunctionCommentsFromTsv.java subagents/ghidra-static-reaudit/name-confidence-tranche2-rename/current/comments_tranche2_candidates.tsv apply
bash tools/run_ghidra_headless_postscript.sh ExportFunctionMetadataByAddress.java subagents/ghidra-static-reaudit/name-confidence-tranche2-rename/current/readback_addresses.txt subagents/ghidra-static-reaudit/name-confidence-tranche2-rename/current/metadata_after.tsv
bash tools/run_ghidra_headless_postscript.sh ExportFunctionsByAddressDecompile.java subagents/ghidra-static-reaudit/name-confidence-tranche2-rename/current/readback_addresses.txt subagents/ghidra-static-reaudit/name-confidence-tranche2-rename/current/decompile_after 80
bash tools/run_ghidra_headless_postscript.sh ExportXrefsForAddresses.java subagents/ghidra-static-reaudit/name-confidence-tranche2-rename/current/readback_addresses.txt subagents/ghidra-static-reaudit/name-confidence-tranche2-rename/current/xrefs_after.tsv
```

Probe validation:

```powershell
py -3 tools\ghidra_name_confidence_tranche2_rename_probe_test.py
py -3 tools\ghidra_name_confidence_tranche2_rename_probe.py --check
py -3 -m py_compile tools\ghidra_name_confidence_tranche2_rename_probe.py tools\ghidra_name_confidence_tranche2_rename_probe_test.py
cmd.exe /c npm run test:ghidra-name-confidence-tranche2-rename
```

## Result

```text
Ghidra name-confidence tranche 2 rename probe
Status: PASS
Classification: tranche2-rename-candidates-renamed-commented
Targets: 2
Rename: {'drySummary': {'applied': 0, 'skipped': 2, 'missing': 0, 'bad': 0}, 'applySummary': {'applied': 2, 'skipped': 0, 'missing': 0, 'bad': 0}}
Comments: {'drySummary': {'applied': 0, 'skipped': 2, 'missing': 0, 'bad': 0}, 'applySummary': {'applied': 2, 'skipped': 0, 'missing': 0, 'bad': 0}}
All names/comments/context present: True
```

Read-back summary:

| Address | New saved name | Evidence boundary |
| --- | --- | --- |
| `0x00414b30` | `TargetSet__AnyUnitTargetTimeoutBeforeProfileLimit` | Decompile context still calls `CUnit__IsTargetTimeoutBeforeProfileLimit`; xrefs remain from `CBattleEngine__UpdateAutoTargetSetAndFireProjectiles`. |
| `0x00505c30` | `NamedEntryList__FindNearestChildByNameAndPosition` | Decompile context still contains case-insensitive name matching and nearest-position math tokens; two checked xrefs remain no-function caller rows. |

## What This Proves

- The saved Ghidra project now carries behavior-backed names for the two tranche-2 rename candidates.
- Clean dry/apply logs and metadata read-back confirm both renames and proof-boundary comments landed.
- Decompile/xref read-back preserved the target-set timeout scan and named-entry nearest-position lookup evidence used to justify the names.

## What This Does Not Prove

- This does not change signatures, parameter names, local names, tags, structures, or data types.
- This does not prove exact source-to-retail identity or final owner/class boundaries.
- This does not prove runtime behavior.
- This does not patch, launch, or mutate `BEA.exe` or the installed game.
- This does not complete the broader static re-audit queue.

## Privacy / Release Safety

This report stores repo-relative artifact paths, public addresses, function names, command summaries, counts, and proof boundaries only. It does not include binaries, private absolute paths, source excerpts, decompiled source excerpts, runtime captures, screenshots, frame data, copied executables, copied saves, debugger logs, raw private proof JSON, or private game payloads.
