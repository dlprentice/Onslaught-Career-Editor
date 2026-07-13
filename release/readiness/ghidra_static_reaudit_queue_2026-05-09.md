# Ghidra Static Re-Audit Queue - 2026-05-09

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 semantic revalidation:** Historical record; `0x00410c50` → `CBattleEngineJetPart__Move` (was `CMonitor__UpdateMovementTransitionAndEffects`). The original text below remains provenance rather than current semantic authority. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); exact records are in `reverse-engineering/binary-analysis/ghidra-full-reaudit-corrections-2026-07-13.json` and `reverse-engineering/binary-analysis/ghidra-targeted-revalidation-corrections-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

> **SUPERSEDED (2026-05-26):** Queue counts in this note (`5863` functions, thousands commentless) are obsolete. Current closure is **6113/6113** (Wave900). Use `release/readiness/ghidra_final_static_tail_wave900_2026-05-26.md`, post-100 reviews **902–909**, and `reverse-engineering/binary-analysis/static-reaudit-campaign.md`.

Status: superseded historical queue snapshot; not current queue truth

## Objective

Move the static re-audit campaign from one-off cluster work toward a whole-database quality queue. This pass exports the current saved Ghidra function list with names, signatures, and function comments, then summarizes public-safe debt buckets for future refinement waves.

## Inputs

- Read-only function quality snapshot: `subagents/ghidra-static-reaudit/queue/current/functions_quality.tsv`
- Queue report: `subagents/ghidra-static-reaudit/queue/current/static-reaudit-queue.json`
- Ghidra export script: `tools/ExportFunctionQualitySnapshot.java`
- Probe: `tools/ghidra_static_reaudit_queue_probe.py`
- Probe test: `tools/ghidra_static_reaudit_queue_probe_test.py`

## Commands

Read-only Ghidra export:

```powershell
bash tools/run_ghidra_headless_postscript.sh ExportFunctionQualitySnapshot.java subagents/ghidra-static-reaudit/queue/current/functions_quality.tsv
```

Probe validation:

```powershell
py -3 tools\ghidra_static_reaudit_queue_probe_test.py
py -3 tools\ghidra_static_reaudit_queue_probe.py --check
py -3 -m py_compile tools\ghidra_static_reaudit_queue_probe.py tools\ghidra_static_reaudit_queue_probe_test.py
cmd.exe /c npm run test:ghidra-static-reaudit-queue
```

## Result

```text
Ghidra static re-audit queue probe
Status: PASS
Total functions: 5863
Commentless functions: 5513
Undefined signatures: 2087
Param signatures: 2563
Uncertain owner names: 11
Address-suffixed helpers: 4
Address-suffixed wrappers: 20
```

The export script reported `total_functions=5863` and `commented_functions=350`.

First follow-up note: after the vector-math rename tranche, the ignored queue snapshot reported `5863` functions and `337` commented functions, while the address-suffixed wrapper count moved to `24` instead of the original tranche's `26`.

Second follow-up note: after the name-confidence comment pass, the current ignored queue snapshot still reports `5863` functions and `24` address-suffixed wrappers, while commented functions increased to `343` and commentless functions dropped to `5520`.

Third follow-up note: after the signature-candidate correction pass, the current ignored queue snapshot reports `5863` functions, `346` commented functions, `5517` commentless functions, and `21` address-suffixed wrappers.

Fourth follow-up note: after the BattleEngineData owner correction pass, the current ignored queue snapshot reports `5863` functions, `349` commented functions, `5514` commentless functions, and `21` address-suffixed wrappers.

Fifth follow-up note: after the deferred `0x00410c50` Monitor-body correction pass, the current ignored queue snapshot reports `5863` functions, `350` commented functions, `5513` commentless functions, `11` uncertain owner names, and `20` address-suffixed wrappers.

Sixth follow-up note: after the opening-animation callback rename pass, the current ignored queue snapshot reports `5866` functions, `372` commented functions, `5494` commentless functions, `0` uncertain owner names, `0` address-suffixed helpers, and `0` address-suffixed wrappers.

Seventh follow-up note: after the CAtmospheric signature tranche, the current ignored queue snapshot reports `5866` functions, `376` commented functions, `5490` commentless functions, `2086` undefined signatures, `2564` `param_N` signatures, `0` uncertain owner names, `0` address-suffixed helpers, and `0` address-suffixed wrappers.

Eighth follow-up note: after the CMCMech/CRadar signature tranche, the current ignored queue snapshot reports `5866` functions, `378` commented functions, `5488` commentless functions, `2083` undefined signatures, `2564` `param_N` signatures, `0` uncertain owner names, `0` address-suffixed helpers, and `0` address-suffixed wrappers.

Ninth follow-up note: after the CBSpline/CByteSprite signature tranche, the current ignored queue snapshot reports `5866` functions, `384` commented functions, `5482` commentless functions, `2079` undefined signatures, `2564` `param_N` signatures, `0` uncertain owner names, `0` address-suffixed helpers, and `0` address-suffixed wrappers.

Tenth follow-up note: after the weapon/burst signature tranche, the current ignored queue snapshot reports `5866` functions, `384` commented functions, `5482` commentless functions, `2078` undefined signatures, `2563` `param_N` signatures, `0` uncertain owner names, `0` address-suffixed helpers, and `0` address-suffixed wrappers.

Eleventh follow-up note: after the vector/math signature tranche, the current ignored queue snapshot reports `5866` functions, `390` commented functions, `5476` commentless functions, `2078` undefined signatures, `2559` `param_N` signatures, `0` uncertain owner names, `0` address-suffixed helpers, and `0` address-suffixed wrappers.

Twelfth follow-up note: after the core-helper signature tranche, the current ignored queue snapshot reports `5866` functions, `396` commented functions, `5470` commentless functions, `2078` undefined signatures, `2553` `param_N` signatures, `0` uncertain owner names, `0` address-suffixed helpers, and `0` address-suffixed wrappers.

Thirteenth follow-up note: after the Actor/ComplexThing signature tranche, the current ignored queue snapshot reports `5866` functions, `407` commented functions, `5459` commentless functions, `2078` undefined signatures, `2542` `param_N` signatures, `0` uncertain owner names, `0` address-suffixed helpers, and `0` address-suffixed wrappers.

## What This Proves

- The current saved Ghidra database can export every function with name, signature, and function comment fields.
- The latest follow-up all-function count is `5866` after later boundary-recovery waves.
- Function comments are still sparse: the latest follow-up snapshot reports `407` functions with a non-empty function comment and `5459` commentless functions.
- The queue splits follow-up work into comment debt, signature debt, and name-confidence debt without publishing raw decompile text.
- The first two low-risk vector wrapper names have now been consumed by the vector-math rename follow-up, the first six comment candidates have now been consumed by the saved-comment follow-up, the first three signature-candidate wrapper labels have now been consumed by the saved correction follow-up, the adjacent BattleEngineData owner-label corrections have now been consumed by a dedicated follow-up, and the deferred `0x00410c50` Monitor-body correction has now been consumed by a dedicated follow-up; the remaining queue is still broad.
- The weapon/burst seed functions are present in the same all-function snapshot and can be tracked alongside the whole-database queue.
- Later follow-up snapshots supersede the original queue counts for current triage: the helper/wrapper/uncertain-owner tail is now zero, and the first CAtmospheric, CMCMech/CRadar, CBSpline/CByteSprite, weapon/burst, vector/math, core-helper, and Actor/ComplexThing signature/name correction targets have been hardened, while signature, comment, tag, type, local-name, structure, exact source-identity, and runtime-proof debt remain broad.

## What This Does Not Prove

- This does not prove any current name, signature, comment, tag, or boundary is correct.
- This does not mutate Ghidra names, signatures, comments, tags, or function boundaries.
- This does not add Ghidra tags; tag coverage remains future work.
- This does not prove exact source-to-retail identity or runtime behavior.
- This does not patch, launch, or mutate `BEA.exe` or the installed game.

## Outcome

The next static RE work should consume this queue instead of treating named coverage as completion. Small future tranches can now choose from:

- commentless high-signal functions,
- functions with `undefined` or `param_N` signatures,
- uncertain owner/helper/wrapper names,
- and active seed functions such as the weapon/burst cluster.

## Privacy / Release Safety

This report stores repo-relative artifact paths, aggregate counts, public addresses, function names, boolean quality flags, command summaries, and proof boundaries only. It does not include binaries, private absolute paths, source excerpts, decompiled source excerpts, runtime captures, screenshots, frame data, copied executables, copied saves, debugger logs, raw private proof JSON, or private game payloads.
