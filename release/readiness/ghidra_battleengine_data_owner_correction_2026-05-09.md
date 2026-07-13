# Ghidra BattleEngineData Owner Correction - 2026-05-09

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 semantic revalidation:** Historical record; `0x0040f890` comment correction. The original text below remains provenance rather than current semantic authority. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); exact records are in `reverse-engineering/binary-analysis/ghidra-full-reaudit-corrections-2026-07-13.json` and `reverse-engineering/binary-analysis/ghidra-targeted-revalidation-corrections-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Status: public-safe saved Ghidra rename/comment evidence

## Objective

Correct the adjacent BattleEngineData owner cluster left open by the signature-candidate correction pass. The prior saved names used `CBattleEngineDataManager__*` for three instance-method bodies that source, decompile shape, and xref context now support as `CBattleEngineData` methods.

This pass deliberately did not harden signatures, parameter names, local names, tags, structures, or data types. The current decompiler storage still needs a dedicated type-model pass before those fields should be changed.

## Inputs

- Rename map: `subagents/ghidra-static-reaudit/battleengine-data-owner-correction/current/rename_map.txt`
- Comment map: `subagents/ghidra-static-reaudit/battleengine-data-owner-correction/current/comments.tsv`
- Address lists: `subagents/ghidra-static-reaudit/battleengine-data-owner-correction/current/addresses.txt` and `readback_addresses.txt`
- Dry/apply logs: `subagents/ghidra-static-reaudit/battleengine-data-owner-correction/current/*_dry.log` and `*_apply.log`
- Metadata read-back: `subagents/ghidra-static-reaudit/battleengine-data-owner-correction/current/metadata_after.tsv`
- Xref read-back: `subagents/ghidra-static-reaudit/battleengine-data-owner-correction/current/xrefs_after.tsv`
- Probe report: `subagents/ghidra-static-reaudit/battleengine-data-owner-correction/current/battleengine-data-owner-correction.json`
- Probe: `tools/ghidra_battleengine_data_owner_correction_probe.py`
- Probe test: `tools/ghidra_battleengine_data_owner_correction_probe_test.py`

Raw logs, metadata exports, decompiles, xrefs, and probe JSON remain ignored under `subagents/`.

## Commands

- `py -3 tools\ghidra_rename_map_preflight.py subagents\ghidra-static-reaudit\battleengine-data-owner-correction\current\rename_map.txt`
- Direct `analyzeHeadless.bat` dry/apply runs for `GhidraBatchRename.java`.
- Direct `analyzeHeadless.bat` dry/apply runs for `GhidraApplyFunctionCommentsFromTsv.java`.
- Direct `analyzeHeadless.bat` read-back runs for metadata, decompile, xref, and quality-snapshot exports.
- `py -3 tools\ghidra_battleengine_data_owner_correction_probe_test.py`
- `cmd.exe /c npm run test:ghidra-battleengine-data-owner-correction`
- `cmd.exe /c npm run test:ghidra-static-reaudit-queue`

## Result

```text
Ghidra BattleEngineData owner correction probe
Status: PASS
Classification: battleengine-data-owner-names-corrected
Targets: 3
Rename dry/apply: applied=0 skipped=3 missing=0 bad=0; applied=3 skipped=0 missing=0 bad=0
Comment dry/apply: applied=0 skipped=3 missing=0 bad=0; applied=3 skipped=0 missing=0 bad=0
All names/comments present: True
Load calls shutdown: True
```

The refreshed queue reports:

```text
Total functions: 5863
Commentless functions: 5514
Undefined signatures: 2087
Param signatures: 2563
Uncertain owner names: 12
Address-suffixed helpers: 4
Address-suffixed wrappers: 21
```

## Corrected Functions

| Address | Previous saved name | New saved name | Evidence basis |
| --- | --- | --- | --- |
| `0x0040f590` | `CBattleEngineDataManager__Init` | `CBattleEngineData__Initialise` | Source `CBattleEngineData::Initialise`, default strings including `Standard`, `Vulcan Cannon 1`, `Pulse Cannon Pod`, `Missile Pod`, `Animated Explosion Emitter 2`, and `cockpit2.msh`, plus reload caller context after construction. |
| `0x0040f890` | `CBattleEngineDataManager__Clear` | `CBattleEngineData__Shutdown` | Source `CBattleEngineData::Shutdown`, owned `mConfigurationName` cleanup, two weapon-list drains, owned string frees, and direct call from the renamed load body. |
| `0x0040f980` | `CBattleEngineDataManager__Load` | `CBattleEngineData__LoadFromMemBuffer` | Source `CBattleEngineData::Load(CMEMBUFFER&)`, initial shutdown call, versioned `DXMemBuffer__ReadBytes` flow, weapon-list append loops, store reads, optional string reads, and version fallback defaults. |

## What This Proves

- Three adjacent BattleEngineData lifecycle functions now have saved source-aligned owner names in the Ghidra project.
- Metadata read-back confirms the expected new names and proof-boundary comments.
- Xref read-back confirms the renamed `CBattleEngineData__LoadFromMemBuffer` body calls `CBattleEngineData__Shutdown`.
- The broader queue improved from `5517` to `5514` commentless functions after this pass.

## What This Does Not Prove

- This does not change signatures, parameter names, local names, tags, structures, or data types.
- This does not prove source-build identity beyond the checked source/decompile/xref alignment.
- This does not prove runtime behavior.
- This does not complete the broader Ghidra static re-audit queue.

## Follow-Up

The BattleEngineData lifecycle cluster is now better named, but the saved signatures still report undefined/fastcall-style decompiler storage. A future type-model pass should be separate from name correction and should only harden `this`, `CMEMBUFFER&`, list/string fields, and structure offsets after a focused preflight/read-back plan.

## Privacy / Release Safety

This note stores repo-relative artifact paths, public addresses, function names, aggregate counts, command summaries, and proof boundaries only. It does not include binaries, private absolute paths, decompile excerpts, screenshots, runtime captures, copied executables, copied saves, raw private proof JSON, or private game payloads.
