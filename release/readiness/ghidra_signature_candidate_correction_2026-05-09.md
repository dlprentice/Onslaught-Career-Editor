# Ghidra Signature-Candidate Correction - 2026-05-09

Status: public-safe saved Ghidra rename/comment evidence

## Objective

Revisit the three functions that the first name-confidence tranche classified as signature candidates and correct the weak wrapper names where source, decompile shape, and caller context agreed.

This pass deliberately did not harden signatures, parameter names, local names, tags, structures, or data types. The current decompiler storage still needs a dedicated type-model pass before those fields should be changed.

## Inputs

- Rename map: `subagents/ghidra-static-reaudit/signature-candidate-corrections/current/rename_map.txt`
- Comment map: `subagents/ghidra-static-reaudit/signature-candidate-corrections/current/comments.tsv`
- Address list: `subagents/ghidra-static-reaudit/signature-candidate-corrections/current/addresses.txt`
- Dry/apply logs: `subagents/ghidra-static-reaudit/signature-candidate-corrections/current/*_dry.log` and `*_apply.log`
- Metadata read-back: `subagents/ghidra-static-reaudit/signature-candidate-corrections/current/metadata_after.tsv`
- Probe report: `subagents/ghidra-static-reaudit/signature-candidate-corrections/current/signature-candidate-corrections.json`
- Probe: `tools/ghidra_signature_candidate_correction_probe.py`
- Probe test: `tools/ghidra_signature_candidate_correction_probe_test.py`

Raw logs, metadata exports, decompiles, xrefs, and probe JSON remain ignored under `subagents/`.

## Commands

- `py -3 tools\ghidra_rename_map_preflight.py subagents\ghidra-static-reaudit\signature-candidate-corrections\current\rename_map.txt`
- Direct `analyzeHeadless.bat` dry/apply runs for `GhidraBatchRename.java`.
- Direct `analyzeHeadless.bat` dry/apply runs for `GhidraApplyFunctionCommentsFromTsv.java`.
- Direct `analyzeHeadless.bat` read-back runs for metadata, decompile, xref, and quality-snapshot exports.
- `py -3 tools\ghidra_signature_candidate_correction_probe_test.py`
- `cmd.exe /c npm run test:ghidra-signature-candidate-correction`
- `cmd.exe /c npm run test:ghidra-static-reaudit-queue`

## Result

```text
Ghidra signature-candidate correction probe
Status: PASS
Classification: signature-candidates-renamed-commented-signatures-deferred
Targets: 3
Rename dry/apply: applied=0 skipped=3 missing=0 bad=0; applied=3 skipped=0 missing=0 bad=0
Comment dry/apply: applied=0 skipped=3 missing=0 bad=0; applied=3 skipped=0 missing=0 bad=0
All names/comments present: True
```

The refreshed queue reports:

```text
Total functions: 5863
Commentless functions: 5517
Undefined signatures: 2087
Param signatures: 2563
Uncertain owner names: 12
Address-suffixed helpers: 4
Address-suffixed wrappers: 21
```

## Corrected Functions

| Address | Previous saved name | New saved name | Evidence basis |
| --- | --- | --- | --- |
| `0x0040e280` | `DXMemBuffer_ReadBytes__Wrapper_0040e280` | `CInitThing__LoadFromMemBuffer` | Source `CInitThing::Load(short, CMEMBUFFER&)`, version-gated field reads, and caller `CSquadInitThing__VFunc_01_0048d8d0` reading squad fields after the base load. |
| `0x0040f140` | `OID_FreeObject__Wrapper_0040f140` | `BattleEngineConfigurations__ShutDown` | Source `UBattleEngineConfigurations::ShutDown`, global configuration count/table addresses `0x00660250` and `0x00660200`, and world teardown caller context. |
| `0x0040f520` | `CSPtrSet_Init__Wrapper_0040f520` | `CBattleEngineData__ctor` | Source `CBattleEngineData::CBattleEngineData()`, embedded set initialization at `+0x40/+0x50`, zeroed owned fields, and allocation-before-initialise/load caller context. |

## What This Proves

- Three weak wrapper labels from the first name-confidence tranche were corrected in the saved Ghidra project.
- Metadata read-back confirms the expected new names and proof-boundary comment tokens.
- The broader queue improved from `5520` to `5517` commentless functions and from `24` to `21` address-suffixed wrapper names after this pass.
- The first tranche's original "signature candidate" bucket was too coarse for these functions: the immediate correction was naming and evidence comments, not signature mutation.

## What This Does Not Prove

- This does not change signatures, parameter names, local names, tags, structures, or data types.
- This does not prove the current decompiler parameter storage is final.
- This does not prove runtime behavior.
- This does not complete the broader Ghidra static re-audit queue.

## Follow-Up

Follow-up completed later on 2026-05-09: `CBattleEngineDataManager__Init`, `CBattleEngineDataManager__Clear`, and `CBattleEngineDataManager__Load` were reviewed against source/decompile/xref evidence and corrected to `CBattleEngineData__Initialise`, `CBattleEngineData__Shutdown`, and `CBattleEngineData__LoadFromMemBuffer`. See `release/readiness/ghidra_battleengine_data_owner_correction_2026-05-09.md`.

The remaining owner-cluster debt is signature/type hardening, not another broad rename claim: `this`, `CMEMBUFFER&`, list/string fields, and structure offsets still need a dedicated type-model pass.

## Privacy / Release Safety

This note stores repo-relative artifact paths, public addresses, function names, aggregate counts, command summaries, and proof boundaries only. It does not include binaries, private absolute paths, decompile excerpts, screenshots, runtime captures, copied executables, copied saves, raw private proof JSON, or private game payloads.
