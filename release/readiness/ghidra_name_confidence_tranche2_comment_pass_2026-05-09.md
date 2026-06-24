# Ghidra Name-Confidence Tranche 2 Comment Pass - 2026-05-09

Status: public-safe saved-Ghidra comment evidence, not final name/signature/runtime proof

## Objective

Consume the nine comment candidates from `release/readiness/ghidra_name_confidence_tranche2_2026-05-09.md` with the normal Ghidra mutation discipline: exact current-name guard, headless dry/apply, metadata/decompile/xref read-back, and a focused public-safe probe.

This pass deliberately adds comments instead of renaming. The current names remain evidence labels that can be corrected by later re-audit waves.

## Inputs

- Comment TSV: `subagents/ghidra-static-reaudit/name-confidence-tranche2-comment-pass/current/comments.tsv`
- Metadata read-back: `subagents/ghidra-static-reaudit/name-confidence-tranche2-comment-pass/current/metadata_after.tsv`
- Decompile read-back index: `subagents/ghidra-static-reaudit/name-confidence-tranche2-comment-pass/current/decompile_after/index.tsv`
- Xref read-back: `subagents/ghidra-static-reaudit/name-confidence-tranche2-comment-pass/current/xrefs_after.tsv`
- Probe: `tools/ghidra_name_confidence_tranche2_comment_pass_probe.py`
- Probe test: `tools/ghidra_name_confidence_tranche2_comment_pass_probe_test.py`

## Commands

Ghidra mutation/read-back:

```powershell
bash tools/run_ghidra_headless_postscript.sh GhidraApplyFunctionCommentsFromTsv.java subagents/ghidra-static-reaudit/name-confidence-tranche2-comment-pass/current/comments.tsv dry
bash tools/run_ghidra_headless_postscript.sh GhidraApplyFunctionCommentsFromTsv.java subagents/ghidra-static-reaudit/name-confidence-tranche2-comment-pass/current/comments.tsv apply
bash tools/run_ghidra_headless_postscript.sh ExportFunctionMetadataByAddress.java subagents/ghidra-static-reaudit/name-confidence-tranche2-comment-pass/current/addresses.txt subagents/ghidra-static-reaudit/name-confidence-tranche2-comment-pass/current/metadata_after.tsv
bash tools/run_ghidra_headless_postscript.sh ExportFunctionsByAddressDecompile.java subagents/ghidra-static-reaudit/name-confidence-tranche2-comment-pass/current/addresses.txt subagents/ghidra-static-reaudit/name-confidence-tranche2-comment-pass/current/decompile_after 80
bash tools/run_ghidra_headless_postscript.sh ExportXrefsForAddresses.java subagents/ghidra-static-reaudit/name-confidence-tranche2-comment-pass/current/addresses.txt subagents/ghidra-static-reaudit/name-confidence-tranche2-comment-pass/current/xrefs_after.tsv
```

Probe validation:

```powershell
py -3 tools\ghidra_name_confidence_tranche2_comment_pass_probe_test.py
py -3 tools\ghidra_name_confidence_tranche2_comment_pass_probe.py --check
py -3 -m py_compile tools\ghidra_name_confidence_tranche2_comment_pass_probe.py tools\ghidra_name_confidence_tranche2_comment_pass_probe_test.py
cmd.exe /c npm run test:ghidra-name-confidence-tranche2-comment-pass
```

## Result

```text
Ghidra name-confidence tranche 2 comment-pass probe
Status: PASS
Classification: tranche2-comment-candidates-commented
Targets: 9
Dry summary: {'applied': 0, 'skipped': 9, 'missing': 0, 'bad': 0}
Apply summary: {'applied': 9, 'skipped': 0, 'missing': 0, 'bad': 0}
All comments/context present: True
```

Read-back summary:

- Metadata read-back: `9/9` target functions found with expected current names and comment-boundary tokens.
- Decompile read-back: `9/9` target functions exported with expected behavior-context tokens.
- Xref read-back: `14` public-safe xref rows across the nine targets.
- Queue refresh after this pass: `5863` functions, `361` commented functions, `5502` commentless functions, `10` uncertain owner names, `4` address-suffixed helper names, and `18` address-suffixed wrapper names.

## Commented Targets

| Address | Current saved name | Comment scope |
| --- | --- | --- |
| `0x00411bf0` | `CEngine_Unk_0050a080__Wrapper_00411bf0` | Mode-specific burst dispatch helper evidence and provisional owner/runtime boundary. |
| `0x00412240` | `ROUND__Wrapper_00412240` | Selected-entry rounded slot value helper evidence, with generic ROUND-wrapper identity explicitly unproven. |
| `0x00412420` | `CText_GetStringById__Wrapper_00412420` | Selected-entry display string helper evidence and source/runtime caveat. |
| `0x00412650` | `CSPtrSet_Remove__Wrapper_00412650` | Profile weapon-list rebuild evidence, with exact jet/walker ownership deferred. |
| `0x00412830` | `CCockpit_Unk_00411e70__Wrapper_00412830` | Cockpit disable matching weapon and reselect evidence, with source/runtime caveat. |
| `0x00412ad0` | `ABS__Wrapper_00412ad0` | Monitor surface-alignment angle update evidence, with generic ABS-wrapper identity explicitly unproven. |
| `0x00413660` | `CGeneralVolume_Unk_00409e60__Wrapper_00413660` | General-volume scaled energy-drain evidence and method-boundary caveat. |
| `0x004146b0` | `CSPtrSet_Remove__Wrapper_004146b0` | Profile weapon and special-slot rebuild evidence, with exact owner/source identity deferred. |
| `0x004d3080` | `CGenericActiveReader_SetReader__Wrapper_004d3080` | Game reader rebind and post-load toggle helper evidence, with source/runtime caveat. |

## What This Proves

- The saved Ghidra project now carries proof-boundary comments for the nine second-tranche comment candidates.
- Clean dry/apply logs and metadata read-back confirm all nine comments landed against the expected current names.
- Decompile/xref read-back preserved the behavior and caller context used to justify comments instead of renames.

## What This Does Not Prove

- This does not rename any of the nine functions.
- This does not prove the current saved names are final or perfectly correct.
- This does not change signatures, parameter names, local names, tags, structures, or data types.
- This does not prove exact source-to-retail identity or final owner/class boundaries.
- This does not prove runtime behavior.
- This does not patch, launch, or mutate `BEA.exe` or the installed game.
- This does not complete the broader static re-audit queue.

## Privacy / Release Safety

This report stores repo-relative artifact paths, public addresses, function names, command summaries, counts, and proof boundaries only. It does not include binaries, private absolute paths, source excerpts, decompiled source excerpts, runtime captures, screenshots, frame data, copied executables, copied saves, debugger logs, raw private proof JSON, or private game payloads.
