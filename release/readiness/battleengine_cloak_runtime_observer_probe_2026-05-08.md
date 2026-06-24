# BattleEngine Cloak Runtime Observer Probe - 2026-05-08

Status: public-safe copied-profile runtime observer probe, inconclusive for cloak activation

## Objective

Run the prepared cloak-latch observer against a copied, windowed `BEA.exe` profile before attempting another fire-while-cloaked proof.

The narrow gate was:

```text
Can the private CDB observer log a candidate latch activation before a weapon-fire input is sent?
```

## Safety Boundary

- The installed Steam game folder was treated as read-only source material.
- The runtime target was an ignored copied profile under `subagents/`.
- The copied executable was already windowed through the copied-profile patch path.
- Raw CDB logs, launch JSON, window scans, input logs, and parser JSON remained private under `subagents/`.
- The copied `BEA.exe` process and CDB process were stopped after the probe.
- No installed game file, original `BEA.exe`, original save/options file, Ghidra project, or public release artifact was mutated.

## Commands / Evidence Summary

| Step | Result | Public-safe summary |
| --- | --- | --- |
| Copied-profile launch | PASS | Launched the copied profile with `-skipfmv -level 710` from the ignored runtime root. |
| CDB attach, first observer | PASS/YELLOW | Attached CDB and installed the first one-breakpoint observer. The log recorded one helper entry event but no activation pair. The debugger also reported skipped commands after `gu`, so the observer shape was too fragile for final proof. |
| Parser, first observer | INCONCLUSIVE | `tools/cloak_runtime_observer_log_probe.py --require-activation` wrote a private summary with `EVENTS_WITHOUT_ACTIVATION`, `eventCount=1`, `pairCount=0`, and `activationPairCount=0`. |
| Observer correction | PASS | The command file was changed to explicit entry and return-path breakpoints at `0x0040d4d0`, `0x0040d4e8`, and `0x0040d528`, avoiding CDB step-out from an event handler. |
| CDB attach, corrected observer | PASS/YELLOW | Attached CDB with the corrected observer and sent two scoped `tap:TAB` inputs to the exact managed copied `BEA.exe` window. |
| Parser, corrected observer | INCONCLUSIVE | The corrected run wrote private summaries with `NO_LATCH_EVENTS`, `eventCount=0`, `pairCount=0`, and `activationPairCount=0`. |
| Stop/cleanup | PASS | The copied `BEA.exe` process and CDB process were stopped; a final process scan returned no `BEA` or `cdb` rows. |

## Finding

This probe strengthens the tooling but does not prove cloak activation.

It proves:

- copied-profile launch and debugger attach can be performed against the ignored runtime profile,
- the latch observer can be installed without touching the installed game,
- the parser can distinguish no events, events without activation, and activation-required failure,
- CDB `gu` inside a breakpoint command is fragile for this target and should not be used as final proof instrumentation,
- process cleanup worked after both observer attempts.

It does **not** prove:

- the player was cloaked in the tested runtime state,
- the tested `TAB` input is the correct active cloak input for this launch state,
- firing while cloaked breaks stealth,
- firing while cloaked preserves stealth,
- exact Steam retail identity for source `CBattleEngine::HandleCloak`, `Cloak`, `Decloak`, `Render`, or `WeaponFired`.

## Next Runtime Direction

Do not send the fire input until a prior observer or capture proves a cloak-active baseline.

Good next steps:

- verify the live level 710 control prompt and actual active cloak binding before attaching the observer,
- test the decoded `Special function` bindings (`RShift` for P1, `Tab` for P2 in the current options file) against the managed copied window,
- capture a visible pre-input state to confirm the game is in the expected player-control phase,
- consider a broader read-only state observer if the latch helper is not called from the current state,
- keep the explicit return-path breakpoint observer instead of the earlier `gu` step-out shape.

If a future observer run still has no latch events, the proof should remain blocked on runtime state/input setup rather than becoming a stealth behavior claim.

Follow-up status: `release/readiness/battleengine_cloak_input_binding_triage_2026-05-08.md` corrected the active input target to decoded `Special function` bindings `RShift` / `Tab`. `release/readiness/battleengine_cloak_binding_observer_probe_2026-05-08.md` then tested both decoded bindings against the copied profile. The observer logged helper entry/exit activity but still saw no activation transition, so cloak activation and fire-while-cloaked behavior remain unproven.

## Validation

Public-safe validation commands for the corrected tooling:

```powershell
py -3 -m py_compile tools\cloak_runtime_observer_log_probe.py
npm run test:cloak-runtime-observer-log
powershell -ExecutionPolicy Bypass -File .\tools\start_cdb_server.ps1 -CommandFile .\tools\runtime-probes\cloak-latch-observer.cdb.txt -PrintOnly
```

Runtime parser commands were run only against private ignored logs under `subagents/`; the activation-required parser intentionally failed the acceptance gate for this probe because activation was not observed.

## Privacy / Release Safety

This report is public-safe. It contains only repo-relative tool names, sanitized statuses, public addresses already used by the project, and explicit proof boundaries. It does not include private screenshots, copied saves, copied executables, raw captures, full local paths, raw CDB logs, or raw runtime proof JSON.
