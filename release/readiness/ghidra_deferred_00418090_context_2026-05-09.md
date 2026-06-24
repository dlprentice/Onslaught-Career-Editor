# Ghidra Deferred 0x00418090 Context - 2026-05-09

Status: public-safe saved-Ghidra context evidence, not final owner/name/signature/runtime proof

Follow-up note: a later saved rename pass in the same campaign corrected this target to `OpeningAnimationStateCallback__StartOpeningIfPending` while keeping the unresolved table/owner/source/runtime caveats. This note remains the earlier comment-only context record.

## Objective

Resolve the deferred name-confidence tranche 2 target at `0x00418090` far enough to decide whether the current saved Ghidra project should receive a rename, a comment, or no mutation.

The result is intentionally conservative: `0x00418090` now has a saved proof-boundary comment, but its existing `FindAnimationIndex__Wrapper_00418090` name remains a weak wrapper-style label pending future owner/type/tag/signature work.

## Inputs

- Target: `0x00418090`
- Current saved name: `FindAnimationIndex__Wrapper_00418090`
- Raw evidence root: `subagents/ghidra-static-reaudit/deferred-00418090/current/`
- Probe: `tools/ghidra_deferred_00418090_context_probe.py`
- Probe test: `tools/ghidra_deferred_00418090_context_probe_test.py`

## Commands

Ghidra context and read-back:

```powershell
bash tools/run_ghidra_headless_postscript.sh ExportFunctionMetadataByAddress.java subagents/ghidra-static-reaudit/deferred-00418090/current/addresses.txt subagents/ghidra-static-reaudit/deferred-00418090/current/metadata.tsv
bash tools/run_ghidra_headless_postscript.sh ExportFunctionsByAddressDecompile.java subagents/ghidra-static-reaudit/deferred-00418090/current/addresses.txt subagents/ghidra-static-reaudit/deferred-00418090/current/decompile 80
bash tools/run_ghidra_headless_postscript.sh ExportXrefsForAddresses.java subagents/ghidra-static-reaudit/deferred-00418090/current/addresses.txt subagents/ghidra-static-reaudit/deferred-00418090/current/xrefs.tsv
bash tools/run_ghidra_headless_postscript.sh DumpPointerTable.java 0x005d9000 96 subagents/ghidra-static-reaudit/deferred-00418090/current/table_005d9000_96.tsv
bash tools/run_ghidra_headless_postscript.sh ResolveVtableTypeNames.java subagents/ghidra-static-reaudit/deferred-00418090/current/vtable_candidates.txt subagents/ghidra-static-reaudit/deferred-00418090/current/vtable_type_names.tsv
bash tools/run_ghidra_headless_postscript.sh ResolveVtableTypeNames.java subagents/ghidra-static-reaudit/deferred-00418090/current/vtable_candidates_9080.txt subagents/ghidra-static-reaudit/deferred-00418090/current/vtable_type_names_9080.tsv
bash tools/run_ghidra_headless_postscript.sh GhidraApplyFunctionCommentsFromTsv.java subagents/ghidra-static-reaudit/deferred-00418090/current/comments.tsv dry
bash tools/run_ghidra_headless_postscript.sh GhidraApplyFunctionCommentsFromTsv.java subagents/ghidra-static-reaudit/deferred-00418090/current/comments.tsv apply
bash tools/run_ghidra_headless_postscript.sh ExportFunctionMetadataByAddress.java subagents/ghidra-static-reaudit/deferred-00418090/current/addresses.txt subagents/ghidra-static-reaudit/deferred-00418090/current/metadata_readback.tsv
bash tools/run_ghidra_headless_postscript.sh ExportFunctionsByAddressDecompile.java subagents/ghidra-static-reaudit/deferred-00418090/current/addresses.txt subagents/ghidra-static-reaudit/deferred-00418090/current/decompile_readback 80
bash tools/run_ghidra_headless_postscript.sh ExportXrefsForAddresses.java subagents/ghidra-static-reaudit/deferred-00418090/current/addresses.txt subagents/ghidra-static-reaudit/deferred-00418090/current/xrefs_readback.tsv
```

Probe validation:

```powershell
py -3 tools\ghidra_deferred_00418090_context_probe_test.py
py -3 tools\ghidra_deferred_00418090_context_probe.py --check
py -3 -m py_compile tools\ghidra_deferred_00418090_context_probe.py tools\ghidra_deferred_00418090_context_probe_test.py
cmd.exe /c npm run test:ghidra-deferred-00418090-context
bash tools/run_ghidra_headless_postscript.sh ExportFunctionQualitySnapshot.java subagents/ghidra-static-reaudit/queue/current/functions_quality.tsv
cmd.exe /c npm run test:ghidra-static-reaudit-queue
```

Process note: an initial read-only decompile/xref export was accidentally started in parallel with another headless export and lock-failed. No Ghidra mutation was in that failed batch. The exports were rerun serially before the comment dry/apply and read-back steps above.

## Result

```text
Ghidra deferred 0x00418090 context probe
Status: PASS
Classification: deferred-opening-animation-context-commented-owner-unproven
Dry summary: {'applied': 0, 'skipped': 1, 'missing': 0, 'bad': 0}
Apply summary: {'applied': 1, 'skipped': 0, 'missing': 0, 'bad': 0}
Read-back: comment tokens present, decompile tokens present, mixed table slot xref present
```

Read-back summary:

- Metadata read-back found `0x00418090` with the expected current name and saved proof-boundary comment.
- Decompile read-back still carries the `opening` string token, `FindAnimationIndex` call, state field `+0x254`, timer field `+0x25c`, and animation-start vcall `+0xf0`.
- Xref read-back shows one DATA xref from table slot `0x005d9080`.
- Pointer/type context shows a mixed data/table region, including the `0x005d9080 -> 0x00418090` function pointer, nearby float-like entries at `0x005d9088` / `0x005d908c`, front-end and CByteSprite markers, nearby `CBuildingNamedMesh` RTTI for adjacent candidates, and no resolved class owner for the `0x005d9080` slot.
- Queue refresh after this pass: `5863` functions, `362` commented functions, `5501` commentless functions, `10` uncertain owner names, `4` address-suffixed helper names, and `18` address-suffixed wrapper names.

## What This Proves

- The deferred tranche-2 `0x00418090` body is better treated as an opening-animation state callback candidate than as a generic `FindAnimationIndex` wrapper.
- The saved Ghidra project now carries a proof-boundary comment for that evidence.
- The current evidence supports comment refinement only; table/owner context is not strong enough for a rename in this wave.

## What This Does Not Prove

- This does not rename `0x00418090`.
- This does not prove the current saved name is final or correct.
- This does not prove exact owner/table boundary, source method identity, signature, parameter names, local names, structures, data types, or tags.
- This does not prove runtime animation or opening-state behavior.
- This does not patch, launch, or mutate `BEA.exe` or the installed game.
- This does not complete the broader static re-audit queue.

## Privacy / Release Safety

This report stores repo-relative artifact paths, public addresses, function names, command summaries, counts, and proof boundaries only. It does not include binaries, private absolute paths, source excerpts, decompiled source excerpts, runtime captures, screenshots, frame data, copied executables, copied saves, debugger logs, raw private proof JSON, or private game payloads.
