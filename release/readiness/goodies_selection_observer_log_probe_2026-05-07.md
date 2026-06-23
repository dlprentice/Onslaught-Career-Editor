# Goodies Selection Observer Log Probe - 2026-05-07

Status: public-safe parser/tooling evidence, not runtime proof

## Objective

Make future Goodies selection-observer CDB logs machine-checkable before running another copied-profile runtime pass.

The parser summarizes lines emitted by both prepared observer command files:

```text
tools/runtime-probes/goodies-selection-observer.cdb.txt
tools/runtime-probes/goodies-input-observer.cdb.txt
```

## What Changed

Added, then extended:

```text
tools/goodies_selection_observer_log_probe.py
tools/goodies_selection_observer_log_probe_test.py
tools/runtime-probes/goodies-input-observer.cdb.txt
```

The parser records:

- returned Goodie ids from `get_goodie_number`,
- whether the expected normal sequence `66, 67, 68, 69, 70, 74` appears,
- whether hidden ids `71`, `72`, or `73` appear,
- right-navigation and selected-load observer events,
- `CFEPGoodies__ButtonPressed` input-handler entry events,
- CDB "commands were skipped" warnings from hot breakpoints,
- multiple observer events printed on one physical CDB log line.

The original mapper observer remains useful when the goal is a broad rendered
wall-coordinate sample. The focused input observer avoids the global
`get_goodie_number` breakpoint and instead breaks after selected
`CFEPGoodies__ButtonPressed` call sites return, so the next runtime run can
separate input-handler evidence from render-loop sampling.

The repo gate is:

```powershell
npm run test:goodies-selection-observer-log
```

The test now also checks that `tools/runtime-probes/goodies-selection-observer.cdb.txt` still emits the parser's expected line prefixes for `get_goodie_number`, right-navigation probes, selected-load, and `StartLoadingGoody`, and that `tools/runtime-probes/goodies-input-observer.cdb.txt` avoids the hot global mapper breakpoint while emitting button-entry and after-call return labels.

## TDD Evidence

Red step:

```powershell
py -3 tools\goodies_selection_observer_log_probe_test.py
```

Result before implementation: FAIL, expected `ModuleNotFoundError` for the missing parser module.

Green step:

```powershell
py -3 tools\goodies_selection_observer_log_probe_test.py
```

Result after implementation: PASS, initially 2/2.

Focused input-observer extension:

```powershell
npm run test:goodies-selection-observer-log
```

Result after extension: PASS, 7/7 after the parser was corrected to consume every observer event occurrence on a line.

## Not Claimed

- This does not launch BEA.
- This does not attach CDB.
- This does not prove hidden/non-grid Goodies reachability or unreachability.
- This only prepares the future runtime proof to be checked from log evidence instead of screenshots alone.
- The input observer has not yet been run against the copied profile; it is a safer next probe shape for that future runtime pass.
