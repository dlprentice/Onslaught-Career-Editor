# Ghidra Static Re-Audit Baseline - 2026-05-09

> **SUPERSEDED (2026-05-26):** Baseline counts here predate Wave900 closure. Current queue truth: **6113/6113** commented with clean signatures. See `ghidra_final_static_tail_wave900_2026-05-26.md` and `reverse-engineering/binary-analysis/static-reaudit-campaign.md`.

Status: superseded historical baseline; not current queue truth

## Objective

Start the broader static-binary refinement campaign by measuring current Ghidra database shape before changing names, signatures, comments, tags, or function boundaries.

The key correction is methodological: `100%` named coverage is not the same as `100%` correct naming. The next RE campaign should grade confidence and refine evidence-backed names in controlled tranches.

## Inputs

- Read-only all-function export: `subagents/ghidra-static-reaudit/current/functions_all.tsv`
- Baseline probe: `tools/ghidra_static_reaudit_baseline_probe.py`
- Baseline probe test: `tools/ghidra_static_reaudit_baseline_probe_test.py`

## Commands

Read-only Ghidra export:

```powershell
bash tools/run_ghidra_headless_postscript.sh ExportWeakFunctionList.java subagents/ghidra-static-reaudit/current/functions_all.tsv all
```

Probe validation:

```powershell
py -3 tools\ghidra_static_reaudit_baseline_probe_test.py
py -3 tools\ghidra_static_reaudit_baseline_probe.py --check
py -3 -m py_compile tools\ghidra_static_reaudit_baseline_probe.py tools\ghidra_static_reaudit_baseline_probe_test.py
cmd.exe /c npm run test:ghidra-static-reaudit-baseline
```

## Result

```text
Ghidra static re-audit baseline probe
Status: PASS
Total functions: 5862
Legacy weak names: 0
Uncertain owner names: 12
Address-suffixed helpers: 4
Address-suffixed wrappers: 26
Param signatures: 2563
Undefined signatures: 2086
Seed missing function objects: 0x00506930
```

Key read-only facts:

| Evidence | Current result |
| --- | --- |
| Current function object count | `5862` in the fresh headless export. |
| Legacy weak-name count | `0` for the legacy `FUN_`, `Auto_`, and `__Unk_` closure metric. |
| Broader review signals | Non-zero: `_Unk_`-style names, address-suffixed helper/wrapper names, `param_N` signatures, and `undefined` signatures. |
| First re-audit seed | Weapon/burst cluster: `0x00506010`, `0x005069f0`, `0x00506930`, and `0x005078b0`. |
| Boundary warning | `0x00506930` remains absent from the all-function export while other evidence points to it as a raw vtable slot-0 target. |

The ignored JSON report is written to `subagents/ghidra-static-reaudit/current/static-reaudit-baseline.json`.

## What This Proves

- The current Ghidra database can export a complete all-functions list through headless tooling.
- The current database has no legacy weak names by the old closure metric.
- Broader confidence signals are still non-zero, so the static RE work is not "done" just because every function has a name.
- The weapon/burst cluster has concrete seed targets for boundary and name-confidence re-audit.

## What This Does Not Prove

- This does not prove every current Ghidra name is correct.
- This does not mutate names, signatures, comments, tags, or function boundaries.
- This does not prove exact source-to-retail identity for any seed target.
- This does not prove runtime behavior.
- This does not replace future dry-run/apply/read-back mutation discipline.

## Campaign Direction

Future Ghidra update waves should follow this pattern:

1. Export a bounded function set with current names, signatures, decompile, xrefs, and instruction context.
2. Classify each target by evidence quality: source-parity, behavior-backed, owner-only, wrapper/thunk, boundary-risk, signature-risk, or runtime-only.
3. Prepare a small rename/signature/comment/tag tranche only when evidence supports it.
4. Dry-run where the tool supports it.
5. Apply headless changes in a small saved tranche.
6. Read back the changed functions and update public-safe docs/state with exact proof boundaries.

## Privacy / Release Safety

This report stores repo-relative filenames, public addresses, current function names/signatures, aggregate counts, example categories, command summaries, and proof boundaries only. It does not include binaries, private absolute paths, source excerpts, decompiled source excerpts, runtime captures, screenshots, copied executables, copied saves, debugger logs, or mutation logs beyond public-safe summaries.
