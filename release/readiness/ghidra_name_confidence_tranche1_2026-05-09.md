# Ghidra Name-Confidence Tranche 1 - 2026-05-09

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 live correction closeout:** Historical record; `0x0040f890` comment correction; `0x00410c50` → `CBattleEngineJetPart__Move` (was `CMonitor__UpdateMovementTransitionAndEffects`). The original text below remains provenance rather than current semantic authority. It is superseded only where confirmed. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); final per-address decisions and exact before/after metadata are in `reverse-engineering/binary-analysis/ghidra-reviewed-correction-decisions-2026-07-13.jsonl` and `reverse-engineering/binary-analysis/ghidra-reviewed-correction-plan-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

> **Owner/name supersession (2026-07-12):** this classification remains a
> historical queue record. Current static evidence identifies `0x00410c50` as
> `CBattleEngineJetPart__Move`, not a Monitor helper. See the
> [current movement crosswalk](../../reverse-engineering/binary-analysis/battleengine-movement-static-crosswalk-2026-07-12.md).

Status: public-safe read-only name-confidence classification, not a mutation or final identity proof

## Objective

Consume the first dozen entries from the whole-database static re-audit name-confidence queue and classify each target into the next safe action bucket before any rename/comment/signature mutation.

This pass starts with the queue entries that contain address-suffixed wrapper labels, `_Unk_` owner fragments, or both.

## Inputs

- Seed queue rows: `subagents/ghidra-static-reaudit/name-confidence-tranche1/current/seed_names.json`
- Address list: `subagents/ghidra-static-reaudit/name-confidence-tranche1/current/addresses.txt`
- Read-only decompile index: `subagents/ghidra-static-reaudit/name-confidence-tranche1/current/decompile/index.tsv`
- Read-only xref export: `subagents/ghidra-static-reaudit/name-confidence-tranche1/current/xrefs.tsv`
- Tranche report: `subagents/ghidra-static-reaudit/name-confidence-tranche1/current/name-confidence-tranche1.json`
- Probe: `tools/ghidra_name_confidence_tranche_probe.py`
- Probe test: `tools/ghidra_name_confidence_tranche_probe_test.py`

## Commands

Read-only Ghidra exports:

```powershell
bash tools/run_ghidra_headless_postscript.sh ExportFunctionsByAddressDecompile.java subagents/ghidra-static-reaudit/name-confidence-tranche1/current/addresses.txt subagents/ghidra-static-reaudit/name-confidence-tranche1/current/decompile 80
bash tools/run_ghidra_headless_postscript.sh ExportXrefsForAddresses.java subagents/ghidra-static-reaudit/name-confidence-tranche1/current/addresses.txt subagents/ghidra-static-reaudit/name-confidence-tranche1/current/xrefs.tsv
```

Probe validation:

```powershell
py -3 tools\ghidra_name_confidence_tranche_probe_test.py
py -3 tools\ghidra_name_confidence_tranche_probe.py --check
py -3 -m py_compile tools\ghidra_name_confidence_tranche_probe.py tools\ghidra_name_confidence_tranche_probe_test.py
cmd.exe /c npm run test:ghidra-name-confidence-tranche
```

## Result

```text
Ghidra name-confidence tranche probe
Status: PASS
Targets: 12
Xref rows: 122
Action counts: {'renameCandidate': 2, 'commentCandidate': 6, 'signatureCandidate': 3, 'defer': 1}
```

Classification summary:

| Address | Current name | Classification | Suggested action |
| --- | --- | --- | --- |
| `0x004026b0` | `SQRT__Wrapper_004026b0` | vector-length sqrt wrapper | rename candidate |
| `0x00402dd0` | `CHeightField_Unk_0047eb80__Wrapper_00402dd0` | heightfield/shadow corner test | comment candidate |
| `0x00403ff0` | `CFastVB_Unk_0055db0a__Wrapper_00403ff0` | resource-descriptor array destroy wrapper | comment candidate |
| `0x00406d50` | `SQRT__Wrapper_00406d50` | vector-normalize sqrt wrapper | rename candidate |
| `0x0040dcc0` | `CGeneralVolume_Unk_0040a580__Wrapper_0040dcc0` | transition-state wrapper | comment candidate |
| `0x0040dda0` | `CUnitAI_Unk_0044c720__Wrapper_0040dda0` | UnitAI grid cooldown wrapper | comment candidate |
| `0x0040e280` | `DXMemBuffer_ReadBytes__Wrapper_0040e280` | versioned DXMemBuffer reader | signature candidate |
| `0x0040f140` | `OID_FreeObject__Wrapper_0040f140` | global OID pool free wrapper | signature candidate |
| `0x0040f520` | `CSPtrSet_Init__Wrapper_0040f520` | paired CSPtrSet init wrapper | signature candidate |
| `0x00410670` | `CGeneralVolume_Unk_00409e60__Wrapper_00410670` | general-volume energy/drain wrapper | comment candidate |
| `0x00410c50` | `OID_Unk_005078f0__Wrapper_00410c50` | complex monitor movement/update body | defer |
| `0x00411b90` | `CEngine_Unk_00506010__Wrapper_00411b90` | burst-dispatch wrapper | comment candidate |

## Follow-Up Status

Later 2026-05-09 saved-Ghidra follow-up waves consumed the low-risk mutation buckets from this initial read-only classification:

- The two vector-math rename candidates were renamed to `Vec3__Magnitude` and `Vec3__NormalizeInPlace`.
- The six comment candidates received proof-boundary comments without renames or signature changes.
- The three original signature candidates were re-reviewed and corrected as rename/comment work, not signature hardening: `0x0040e280` became `CInitThing__LoadFromMemBuffer`, `0x0040f140` became `BattleEngineConfigurations__ShutDown`, and `0x0040f520` became `CBattleEngineData__ctor`.
- The adjacent BattleEngineData owner cluster found during that review was then corrected: `0x0040f590` became `CBattleEngineData__Initialise`, `0x0040f890` became `CBattleEngineData__Shutdown`, and `0x0040f980` became `CBattleEngineData__LoadFromMemBuffer`.
- The deferred `0x00410c50` body was then re-reviewed in a dedicated pass and conservatively corrected to `CMonitor__UpdateMovementTransitionAndEffects` with a proof-boundary comment; source-exact Monitor method identity and signature hardening remain deferred.

The original tranche's first-action buckets have now all been consumed by later saved-Ghidra waves, but this does not complete source identity, signature, type, tag, or runtime proof.

## What This Proves

- The first name-confidence queue tranche has read-only decompile context for all `12` selected targets.
- The xref export produced `122` rows for the selected targets.
- The tranche can be split into safer future work: `2` likely rename candidates, `6` comment candidates, `3` signature candidates, and `1` deferred complex body.
- The current `SQRT__Wrapper_*` names are likely too weak for the two vector math helpers.
- The large `0x00410c50` body was correctly held back from casual rename/signature mutation until a dedicated pass could prove a conservative Monitor owner/behavior label and preserve source/signature caveats.

## What This Does Not Prove

- This does not mutate Ghidra names, signatures, comments, tags, or function boundaries.
- This does not prove the suggested names or signatures are final.
- This does not prove exact source-to-retail identity.
- This does not prove runtime behavior.
- This does not patch, launch, or mutate `BEA.exe` or the installed game.

## Outcome

Future mutation should be selective:

- A small rename pass can target the two vector math helpers after choosing conservative names.
- A comment pass can annotate the six wrapper/provisional targets without overclaiming source identity.
- A signature pass can harden the three constructor/reader/free/init shapes only after parameter roles are reviewed.
- The first tranche is consumed for initial rename/comment/deferred-action purposes. Future mutation should move to a new queue slice or a focused signature/type/tag pass, with the same dry-run/read-back gates.

## Privacy / Release Safety

This report stores repo-relative artifact paths, public addresses, function names, counts, classifications, command summaries, and proof boundaries only. It does not include binaries, private absolute paths, source excerpts, decompiled source excerpts, runtime captures, screenshots, frame data, copied executables, copied saves, debugger logs, raw private proof JSON, or private game payloads.
