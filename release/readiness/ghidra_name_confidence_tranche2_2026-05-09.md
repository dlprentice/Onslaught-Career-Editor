# Ghidra Name-Confidence Tranche 2 - 2026-05-09

Status: public-safe read-only name-confidence classification, not a mutation or final identity proof

## Objective

Continue the saved Ghidra static re-audit after the first tranche and its follow-up corrections by classifying the next commentless name-confidence queue slice.

This pass starts with the first `12` unconsumed commentless entries that still carry `_Unk_` owner fragments, address-suffixed wrapper labels, or both.

## Inputs

- Seed queue rows: `subagents/ghidra-static-reaudit/name-confidence-tranche2/current/seed_names.json`
- Address list: `subagents/ghidra-static-reaudit/name-confidence-tranche2/current/addresses.txt`
- Read-only decompile index: `subagents/ghidra-static-reaudit/name-confidence-tranche2/current/decompile/index.tsv`
- Read-only xref export: `subagents/ghidra-static-reaudit/name-confidence-tranche2/current/xrefs.tsv`
- Tranche report: `subagents/ghidra-static-reaudit/name-confidence-tranche2/current/name-confidence-tranche2.json`
- Probe: `tools/ghidra_name_confidence_tranche2_probe.py`
- Probe test: `tools/ghidra_name_confidence_tranche2_probe_test.py`

## Commands

Read-only Ghidra exports:

```powershell
bash tools/run_ghidra_headless_postscript.sh ExportFunctionsByAddressDecompile.java subagents/ghidra-static-reaudit/name-confidence-tranche2/current/addresses.txt subagents/ghidra-static-reaudit/name-confidence-tranche2/current/decompile 80
bash tools/run_ghidra_headless_postscript.sh ExportXrefsForAddresses.java subagents/ghidra-static-reaudit/name-confidence-tranche2/current/addresses.txt subagents/ghidra-static-reaudit/name-confidence-tranche2/current/xrefs.tsv
```

Probe validation:

```powershell
py -3 tools\ghidra_name_confidence_tranche2_probe_test.py
py -3 tools\ghidra_name_confidence_tranche2_probe.py --check
py -3 -m py_compile tools\ghidra_name_confidence_tranche2_probe.py tools\ghidra_name_confidence_tranche2_probe_test.py
cmd.exe /c npm run test:ghidra-name-confidence-tranche2
```

## Result

```text
Ghidra name-confidence tranche 2 probe
Status: PASS
Targets: 12
Xref rows: 19
Action counts: {'commentCandidate': 9, 'renameCandidate': 2, 'defer': 1}
```

Classification summary:

| Address | Current name | Classification | Suggested action |
| --- | --- | --- | --- |
| `0x00411bf0` | `CEngine_Unk_0050a080__Wrapper_00411bf0` | mode-specific burst dispatch helper | comment candidate |
| `0x00412240` | `ROUND__Wrapper_00412240` | selected-entry rounded slot value | comment candidate |
| `0x00412420` | `CText_GetStringById__Wrapper_00412420` | selected-entry display string | comment candidate |
| `0x00412650` | `CSPtrSet_Remove__Wrapper_00412650` | profile weapon-list rebuild | comment candidate |
| `0x00412830` | `CCockpit_Unk_00411e70__Wrapper_00412830` | cockpit disable matching weapon and reselect | comment candidate |
| `0x00412ad0` | `ABS__Wrapper_00412ad0` | monitor surface-alignment angle update | comment candidate |
| `0x00413660` | `CGeneralVolume_Unk_00409e60__Wrapper_00413660` | general-volume scaled energy drain | comment candidate |
| `0x004146b0` | `CSPtrSet_Remove__Wrapper_004146b0` | profile weapon and special-slot rebuild | comment candidate |
| `0x00414b30` | `CVBufTexture_Unk_0050a290__Wrapper_00414b30` | target-set timeout scan | rename candidate |
| `0x00418090` | `FindAnimationIndex__Wrapper_00418090` | opening animation state helper | defer |
| `0x004d3080` | `CGenericActiveReader_SetReader__Wrapper_004d3080` | game reader rebind and post-load toggle helper | comment candidate |
| `0x00505c30` | `stricmp__Wrapper_00505c30` | named-entry nearest-position lookup | rename candidate |

## What This Proves

- The second name-confidence queue tranche has read-only decompile context for all `12` selected targets.
- The xref export produced `19` rows for the selected targets.
- The tranche can be split into safer future work: `2` likely rename candidates, `9` comment candidates, and `1` deferred vtable/context-dependent body.
- The current `CVBufTexture_Unk_0050a290__Wrapper_00414b30` and `stricmp__Wrapper_00505c30` names are likely too weak for the observed behavior.
- The `0x00418090` opening-animation helper needs owner/vtable context before mutation.

## What This Does Not Prove

- This does not mutate Ghidra names, signatures, comments, tags, or function boundaries.
- This does not prove the suggested names or signatures are final.
- This does not prove exact source-to-retail identity.
- This does not prove runtime behavior.
- This does not patch, launch, or mutate `BEA.exe` or the installed game.

## Outcome

Future mutation should be selective:

- A small rename pass can target the `0x00414b30` target-set timeout scan and `0x00505c30` named-entry nearest-position lookup after choosing conservative names and running the normal dry/apply/read-back gates.
- A comment pass can annotate the nine behavior-classified but still owner/signature-provisional targets without overclaiming source identity.
- The `0x00418090` opening-animation state helper should remain deferred until vtable/owner context is recovered.

## Privacy / Release Safety

This report stores repo-relative artifact paths, public addresses, function names, counts, classifications, caller names, command summaries, and proof boundaries only. It does not include binaries, private absolute paths, source excerpts, decompiled source excerpts, runtime captures, screenshots, frame data, copied executables, copied saves, debugger logs, raw private proof JSON, or private game payloads.
