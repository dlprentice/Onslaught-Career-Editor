# Ghidra Vector Math Rename - 2026-05-09

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 live correction closeout:** Historical record; `0x00410c50` → `CBattleEngineJetPart__Move` (was `CMonitor__UpdateMovementTransitionAndEffects`). The original text below remains provenance rather than current semantic authority. It is superseded only where confirmed. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); final per-address decisions and exact before/after metadata are in `reverse-engineering/binary-analysis/ghidra-reviewed-correction-decisions-2026-07-13.jsonl` and `reverse-engineering/binary-analysis/ghidra-reviewed-correction-plan-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Status: public-safe saved Ghidra rename/read-back evidence, not final type or source-method proof

## Objective

Consume the two rename-ready vector math helpers from the first Ghidra name-confidence tranche and save conservative names in Ghidra after preflight, dry-run, apply, and read-back.

This wave deliberately targets only the two `SQRT__Wrapper_*` vector helpers. It does not broaden into the remaining comment, signature, or deferred complex-body queue.

## Inputs

- Rename map: `subagents/ghidra-static-reaudit/vector-math-rename/current/rename_map_vector_math.txt`
- Address list: `subagents/ghidra-static-reaudit/vector-math-rename/current/addresses.txt`
- Dry-run log: `subagents/ghidra-static-reaudit/vector-math-rename/current/rename_dry.log`
- Apply log: `subagents/ghidra-static-reaudit/vector-math-rename/current/rename_apply.log`
- Post-rename decompile index: `subagents/ghidra-static-reaudit/vector-math-rename/current/decompile_after/index.tsv`
- Post-rename xref export: `subagents/ghidra-static-reaudit/vector-math-rename/current/xrefs_after.tsv`
- Probe report: `subagents/ghidra-static-reaudit/vector-math-rename/current/vector-math-rename.json`
- Probe: `tools/ghidra_vector_math_rename_probe.py`
- Probe test: `tools/ghidra_vector_math_rename_probe_test.py`

## Commands

Preflight and mutation:

```powershell
py -3 tools\ghidra_rename_map_preflight.py subagents\ghidra-static-reaudit\vector-math-rename\current\rename_map_vector_math.txt
direct analyzeHeadless.bat GhidraBatchRename.java subagents\ghidra-static-reaudit\vector-math-rename\current\rename_map_vector_math.txt dry
direct analyzeHeadless.bat GhidraBatchRename.java subagents\ghidra-static-reaudit\vector-math-rename\current\rename_map_vector_math.txt apply
```

Read-back exports:

```powershell
direct analyzeHeadless.bat ExportFunctionsByAddressDecompile.java subagents\ghidra-static-reaudit\vector-math-rename\current\addresses.txt subagents\ghidra-static-reaudit\vector-math-rename\current\decompile_after 60
direct analyzeHeadless.bat ExportXrefsForAddresses.java subagents\ghidra-static-reaudit\vector-math-rename\current\addresses.txt subagents\ghidra-static-reaudit\vector-math-rename\current\xrefs_after.tsv
direct analyzeHeadless.bat ExportFunctionQualitySnapshot.java subagents\ghidra-static-reaudit\queue\current\functions_quality.tsv
```

Probe validation:

```powershell
py -3 tools\ghidra_vector_math_rename_probe_test.py
py -3 tools\ghidra_vector_math_rename_probe.py --check
py -3 tools\ghidra_static_reaudit_queue_probe.py --check
py -3 -m py_compile tools\ghidra_vector_math_rename_probe.py tools\ghidra_vector_math_rename_probe_test.py
cmd.exe /c npm run test:ghidra-vector-math-rename
```

## Result

```text
Ghidra vector math rename probe
Status: PASS
Classification: vector-math-helpers-renamed
Rename: 0x004026b0 SQRT__Wrapper_004026b0 -> Vec3__Magnitude
Rename: 0x00406d50 SQRT__Wrapper_00406d50 -> Vec3__NormalizeInPlace
Dry summary: {'applied': 0, 'skipped': 2, 'missing': 0, 'bad': 0}
Apply summary: {'applied': 2, 'skipped': 0, 'missing': 0, 'bad': 0}
Read-back: {'magnitudeRenamed': True, 'magnitudeXrefsUpdated': True, 'normalizeInPlaceRenamed': True, 'normalizeInPlaceXrefsUpdated': True}
Evidence: {'magnitudeShapePresent': True, 'normalizeInPlaceShapePresent': True}
```

The refreshed quality queue still has `5863` functions and `337` commented functions. The address-suffixed wrapper-name count dropped from `26` to `24` after these two renames.

## What This Proves

- The saved Ghidra project now names `0x004026b0` as `Vec3__Magnitude`.
- The saved Ghidra project now names `0x00406d50` as `Vec3__NormalizeInPlace`.
- Rename-map preflight, direct headless dry-run, direct headless apply, decompile read-back, xref read-back, and the focused probe all passed for this two-function tranche.
- The post-rename decompile shapes still match 3-float vector magnitude and in-place normalization behavior.
- The current whole-database quality queue reflects the removal of these two address-suffixed wrapper names.

## What This Does Not Prove

- This does not harden parameter types, return types, calling conventions, local names, structure types, or data types.
- This does not prove exact source `FVector` method identity.
- This does not add Ghidra tags or comments for the remaining queue.
- This does not mutate or run `BEA.exe`, patch the installed game, or prove runtime behavior.
- This does not complete the whole static re-audit campaign.

## Outcome

The first name-confidence tranche now has its two low-risk rename candidates consumed. The remaining tranche work is still open:

- six comment candidates,
- three signature candidates,
- and the deferred complex body at `0x00410c50`.

## Privacy / Release Safety

This report stores repo-relative artifact paths, public addresses, function names, command summaries, counts, and proof boundaries only. It does not include binaries, private absolute paths, source excerpts, decompiled source excerpts, runtime captures, screenshots, frame data, copied executables, copied saves, debugger logs, raw private proof JSON, or private game payloads.
