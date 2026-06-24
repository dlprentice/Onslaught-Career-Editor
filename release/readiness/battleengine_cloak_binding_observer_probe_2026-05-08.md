# BattleEngine Cloak Binding Observer Probe - 2026-05-08

Status: public-safe copied-profile runtime observer probe, inconclusive for cloak activation

## Objective

Run one bounded copied-profile observer wave after correcting the active `Special function` input binding.

The narrow gate was:

```text
Do the decoded Special function bindings produce a candidate cloak latch activation before any weapon-fire input is sent?
```

## Safety Boundary

- The installed Steam game folder was treated as read-only source material.
- The runtime target was the ignored copied profile under `subagents/`.
- The copied executable had already been prepared for windowed control through the copied-profile patch path.
- Raw CDB logs, launch JSON, window scans, scoped-input logs, and parser JSON remained private under `subagents/`.
- No weapon-fire input was sent.
- The copied `BEA.exe` process and CDB process were stopped after the probe.
- No installed game file, original `BEA.exe`, original save/options file, Ghidra project, or public release artifact was mutated.

## Commands / Evidence Summary

| Step | Result | Public-safe summary |
| --- | --- | --- |
| Copied-profile launch | PASS | Launched the copied profile with `-skipfmv -level 710` from the ignored runtime root. |
| Window scan | PASS | Found one visible managed `BEA.exe` window for the copied process. |
| CDB attach | PASS | Attached x86 CDB with the explicit entry/return-path cloak latch observer. |
| Scoped `RSHIFT` input | SENT/YELLOW | Sent the decoded P1 `Special function` binding to the exact managed copied window. The observer logged entry/exit activity but no activation. |
| Scoped `TAB` input | SENT/YELLOW | Sent the decoded P2 `Special function` binding to the same managed copied window. The observer again logged entry/exit activity but no activation. |
| Parser hardening | PASS | `tools/cloak_runtime_observer_log_probe.py` now handles CDB checksum warning text and multiple observer events on one physical log line. |
| Parser result | INCONCLUSIVE | The private fixed summary reported `EVENTS_WITHOUT_ACTIVATION`, `eventCount=4`, `pairCount=2`, and `activationPairCount=0`. |
| Stop/cleanup | PASS | The copied `BEA.exe` process and CDB process were stopped; a final process scan returned no `BEA` or `cdb` rows. |

## Finding

This probe proves the corrected input binding reaches the candidate latch helper, but it still does not prove cloak activation.

It narrows the previous gap:

- `RShift` and `Tab` are better next-test inputs than backslash for the current profile.
- Both decoded inputs reached the observer path in the tested runtime state.
- Neither decoded input produced a latch-off to latch-on transition in the tested state.
- The stronger parser can now count CDB logs where warning text interrupts the first event and multiple events share one line.

It does **not** prove:

- the player was cloaked in the tested runtime state,
- the tested state was fully player-controllable,
- the candidate latch helper is the only cloak activation path,
- firing while cloaked breaks stealth,
- firing while cloaked preserves stealth,
- exact Steam retail identity for source `CBattleEngine::HandleCloak`, `Cloak`, `Decloak`, `Render`, or `WeaponFired`.

## Next Runtime Direction

Do not send the fire input until a prior observer or capture proves a cloak-active baseline.

Good next steps:

- capture or observe the level-control phase before input so the proof can distinguish wrong binding from wrong state,
- broaden the read-only observer to include the input dispatch / `Special function` handler path rather than only the downstream latch helper,
- consider testing a copied options profile with an intentionally simple `Special function` binding only if the byte-level setup is documented and preserved,
- keep raw logs and captures private and continue publishing only sanitized event counts and proof boundaries.

## Validation

Public-safe validation commands for this wave:

```powershell
py -3 tools\cloak_runtime_observer_log_probe.py --self-test
py -3 tools\cloak_runtime_observer_log_probe.py --log <private-log> --out <private-json> --require-activation
```

The activation-required parser intentionally returned non-zero for this probe because activation was not observed.

## Privacy / Release Safety

This report is public-safe. It contains only repo-relative tool names, sanitized statuses, public addresses already used by the project, event counts, and explicit proof boundaries. It does not include private screenshots, copied saves, copied executables, raw captures, full local paths, raw CDB logs, or raw runtime proof JSON.
