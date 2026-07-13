# Ghidra Deferred 0x00410c50 Correction - 2026-05-09

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 semantic revalidation:** Historical record; `0x004081c0` → `CBattleEngine__Move` (was `CMonitor__Process`); `0x00410c50` → `CBattleEngineJetPart__Move` (was `CMonitor__UpdateMovementTransitionAndEffects`); `0x00411630` → `CBattleEngineJetPart__HandleGroundEffect` (was `CMonitor__IntegrateMovementAgainstTerrain`); `0x00411aa0` → `CBattleEngineJetPart__GetFriction` (was `CMonitor__ComputeTerrainVelocityScalar`). The original text below remains provenance rather than current semantic authority. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); exact records are in `reverse-engineering/binary-analysis/ghidra-full-reaudit-corrections-2026-07-13.json` and `reverse-engineering/binary-analysis/ghidra-targeted-revalidation-corrections-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Status: historical saved Ghidra evidence; owner/name superseded 2026-07-12

> **Supersession:** read-only caller, constructor, object-layout, body-order,
> and source evidence now identifies `0x00410c50` as
> `CBattleEngineJetPart__Move`. The saved
> `CMonitor__UpdateMovementTransitionAndEffects` name remains in the live Ghidra
> project until a separately authorized mutation baton. See
> `reverse-engineering/binary-analysis/battleengine-movement-static-crosswalk-2026-07-12.md`.

## Objective

Consume the deferred complex body from the first Ghidra name-confidence tranche. The prior saved name, `OID_Unk_005078f0__Wrapper_00410c50`, described only one callee and hid a large Monitor-owned movement/update body.

This pass deliberately uses a conservative behavior-backed name, `CMonitor__UpdateMovementTransitionAndEffects`, and does not harden the function signature, parameter names, local names, tags, structures, or data types. No dedicated Monitor source file is present in `references/Onslaught`, so this is not a source-exact method identity claim.

## Inputs

- Rename map: `subagents/ghidra-static-reaudit/deferred-00410c50/current/rename_map.txt`
- Comment map: `subagents/ghidra-static-reaudit/deferred-00410c50/current/comments.tsv`
- Address lists: `subagents/ghidra-static-reaudit/deferred-00410c50/current/addresses.txt` and `readback_addresses.txt`
- Dry/apply logs: `subagents/ghidra-static-reaudit/deferred-00410c50/current/rename_*.log` and `comments_*.log`
- Metadata read-back: `subagents/ghidra-static-reaudit/deferred-00410c50/current/metadata_after.tsv`
- Xref read-back: `subagents/ghidra-static-reaudit/deferred-00410c50/current/xrefs_after.tsv`
- Decompile read-back: `subagents/ghidra-static-reaudit/deferred-00410c50/current/decompile_after/`
- Probe report: `subagents/ghidra-static-reaudit/deferred-00410c50/current/deferred-00410c50-correction.json`
- Probe: `tools/ghidra_deferred_00410c50_correction_probe.py`
- Probe test: `tools/ghidra_deferred_00410c50_correction_probe_test.py`

Raw logs, metadata exports, decompiles, xrefs, and probe JSON remain ignored under `subagents/`.

## Commands

- `py -3 tools\ghidra_rename_map_preflight.py subagents\ghidra-static-reaudit\deferred-00410c50\current\rename_map.txt`
- Direct `analyzeHeadless.bat` dry/apply runs for `GhidraBatchRename.java`.
- Direct `analyzeHeadless.bat` dry/apply runs for `GhidraApplyFunctionCommentsFromTsv.java`.
- Direct `analyzeHeadless.bat` read-back runs for metadata, xref, decompile, and quality-snapshot exports.
- `py -3 tools\ghidra_deferred_00410c50_correction_probe_test.py`
- `py -3 tools\ghidra_deferred_00410c50_correction_probe.py --check --json`
- `cmd.exe /c npm run test:ghidra-deferred-00410c50-correction`
- `cmd.exe /c npm run test:ghidra-static-reaudit-queue`

## Result

```text
Status: PASS
Classification: deferred-monitor-body-renamed-commented-signature-deferred
Rename dry/apply: applied=0 skipped=1 missing=0 bad=0; applied=1 skipped=0 missing=0 bad=0
Comment dry/apply: applied=0 skipped=1 missing=0 bad=0; applied=1 skipped=0 missing=0 bad=0
Read-back name: CMonitor__UpdateMovementTransitionAndEffects
Xref rows: 5
```

The refreshed queue reports:

```text
Total functions: 5863
Commentless functions: 5513
Undefined signatures: 2087
Param signatures: 2563
Uncertain owner names: 11
Address-suffixed helpers: 4
Address-suffixed wrappers: 20
```

## Corrected Function

| Address | Previous saved name | New saved name | Evidence basis |
| --- | --- | --- | --- |
| `0x00410c50` | `OID_Unk_005078f0__Wrapper_00410c50` | `CMonitor__UpdateMovementTransitionAndEffects` | Caller xref from `CMonitor__Process`, callee xrefs to `CMonitor__UpdateTrackedRenderPair`, `CMonitor__IntegrateMovementAgainstTerrain`, and `CMonitor__ComputeTerrainVelocityScalar`, plus decompile context showing transition, terrain/movement, impact-effect, and hostile-environment penalty behavior. |

## What This Proves

- The deferred `0x00410c50` body now has a saved conservative Monitor owner/behavior name in the Ghidra project.
- Metadata read-back confirms the expected new name and a proof-boundary comment.
- Xref read-back confirms `CMonitor__Process` calls the corrected target.
- Xref read-back confirms the corrected target calls selected Monitor movement helpers.
- The whole-database queue improved from `5514` to `5513` commentless functions and from `21` to `20` address-suffixed wrappers after this pass.

## What This Does Not Prove

- This does not prove exact source method identity; no dedicated Monitor source file is present in `references/Onslaught`.
- This does not change signatures, parameter names, local names, tags, structures, or data types.
- This does not prove runtime movement, transition, impact-effect, or hostile-environment behavior.
- This does not complete the broader Ghidra static re-audit queue.

## Follow-Up

The first name-confidence tranche has now had every initial action bucket consumed by later saved-Ghidra waves, but the static re-audit campaign is still broad. The next Ghidra work should pick a new queue slice or start a focused type/signature/tag pass with the same dry-run/read-back discipline.

## Privacy / Release Safety

This note stores repo-relative artifact paths, public addresses, function names, aggregate counts, command summaries, and proof boundaries only. It does not include binaries, private absolute paths, decompile excerpts, screenshots, runtime captures, copied executables, copied saves, raw private proof JSON, or private game payloads.
