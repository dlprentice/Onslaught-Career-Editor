# Ghidra Name-Confidence Tranche 3 - 2026-05-09

Status: public-safe read-only name-confidence classification, not a mutation or final identity proof

## Objective

Continue the saved Ghidra static re-audit by re-parsing the next small name-confidence queue slice after the deferred `0x00418090` context pass.

This pass deliberately treats current saved names as hypotheses. It checks whether the existing labels still match current decompile, xref, and instruction evidence before any rename/comment/tag/signature mutation wave.

## Inputs

- Seed queue rows: `subagents/ghidra-static-reaudit/name-confidence-tranche3/current/seed_names.json`
- Address list: `subagents/ghidra-static-reaudit/name-confidence-tranche3/current/addresses.txt`
- Read-only metadata export: `subagents/ghidra-static-reaudit/name-confidence-tranche3/current/metadata.tsv`
- Read-only decompile index: `subagents/ghidra-static-reaudit/name-confidence-tranche3/current/decompile/index.tsv`
- Read-only xref export: `subagents/ghidra-static-reaudit/name-confidence-tranche3/current/xrefs.tsv`
- Read-only instruction export: `subagents/ghidra-static-reaudit/name-confidence-tranche3/current/instructions.tsv`
- Tranche report: `subagents/ghidra-static-reaudit/name-confidence-tranche3/current/name-confidence-tranche3.json`
- Probe: `tools/ghidra_name_confidence_tranche3_probe.py`
- Probe test: `tools/ghidra_name_confidence_tranche3_probe_test.py`

## Commands

Read-only Ghidra exports:

```powershell
bash tools/run_ghidra_headless_postscript.sh ExportFunctionMetadataByAddress.java subagents/ghidra-static-reaudit/name-confidence-tranche3/current/addresses.txt subagents/ghidra-static-reaudit/name-confidence-tranche3/current/metadata.tsv
bash tools/run_ghidra_headless_postscript.sh ExportFunctionsByAddressDecompile.java subagents/ghidra-static-reaudit/name-confidence-tranche3/current/addresses.txt subagents/ghidra-static-reaudit/name-confidence-tranche3/current/decompile 100
bash tools/run_ghidra_headless_postscript.sh ExportXrefsForAddresses.java subagents/ghidra-static-reaudit/name-confidence-tranche3/current/addresses.txt subagents/ghidra-static-reaudit/name-confidence-tranche3/current/xrefs.tsv
bash tools/run_ghidra_headless_postscript.sh ExportInstructionsAroundAddresses.java subagents/ghidra-static-reaudit/name-confidence-tranche3/current/addresses.txt subagents/ghidra-static-reaudit/name-confidence-tranche3/current/instructions.tsv 0 16
```

Probe validation:

```powershell
py -3 tools\ghidra_name_confidence_tranche3_probe_test.py
py -3 tools\ghidra_name_confidence_tranche3_probe.py --check
py -3 -m py_compile tools\ghidra_name_confidence_tranche3_probe.py tools\ghidra_name_confidence_tranche3_probe_test.py
cmd.exe /c npm run test:ghidra-name-confidence-tranche3
```

## Result

```text
Ghidra name-confidence tranche 3 probe
Status: PASS
Targets: 6
Xref rows: 22
Instruction rows: 102
Action counts: {'renameCandidate': 5, 'ownerCorrectionCandidate': 1}
```

Classification summary:

| Address | Current name | Classification | Suggested action |
| --- | --- | --- | --- |
| `0x0050b010` | `CWorld__DispatchHelper_004bc480` | world occupancy-grid add wrapper | rename candidate |
| `0x0050b020` | `CWorld__DispatchHelper_004bc3e0` | world occupancy-grid remove wrapper | rename candidate |
| `0x0053f7d0` | `CWaypoint_Unk_004f7cd0__Wrapper_0053f7d0` | bitmap-font slot string init | owner-correction candidate |
| `0x0055e412` | `CRT__CallHelper_00564a0b_NoFlags` | texture-load fallback no-flags wrapper | rename candidate |
| `0x0055e45f` | `CRT__CallHelper_00564c09_WithAutoUnlock` | CRT open-file mode auto-unlock wrapper | rename candidate |
| `0x0056d21c` | `CRT__IsDigit_Wrapper_0056d21c` | ctype digit-mask return wrapper | rename candidate |

## What This Proves

- The third name-confidence queue tranche has read-only metadata, decompile, xref, and instruction context for all `6` selected targets.
- The two `CWorld__DispatchHelper_*` functions are thin wrappers into already named occupancy-grid add/remove helpers.
- `0x0053f7d0` is called by `PCPlatform__LoadFonts` and initializes a bitmap-font-like slot, so the current `CWaypoint` owner is likely stale.
- `0x0055e412` forwards to the resolved texture path/fallback loader with fixed no-flags behavior, making the current generic CRT helper label too weak.
- `0x0055e45f` is a CRT file-open wrapper whose callee is now resolved enough to improve the current address-helper name.
- `0x0056d21c` calls the char-type helper with digit mask `4`; instruction context shows the wrapper returns after the call with the callee result preserved.

## What This Does Not Prove

- This does not mutate Ghidra names, signatures, comments, tags, or function boundaries.
- This does not prove the suggested names or signatures are final.
- This does not prove exact source-to-retail identity.
- This does not prove runtime behavior.
- This does not patch, launch, or mutate `BEA.exe` or the installed game.

## Outcome

Future mutation should be selective:

- A small rename/correction wave can target the five rename candidates and the one owner-correction candidate after choosing conservative names and running the normal dry/apply/read-back gates.
- `0x0056d21c` should include signature review because the saved `void` signature is likely stale relative to the instruction-level return behavior.
- The broader static re-audit should continue treating saved names as reparsable hypotheses, not as completion proof.

## Privacy / Release Safety

This report stores repo-relative artifact paths, public addresses, function names, counts, classifications, caller names, command summaries, and proof boundaries only. It does not include binaries, private absolute paths, source excerpts, decompiled source excerpts, runtime captures, screenshots, frame data, copied executables, copied saves, debugger logs, raw private proof JSON, or private game payloads.
