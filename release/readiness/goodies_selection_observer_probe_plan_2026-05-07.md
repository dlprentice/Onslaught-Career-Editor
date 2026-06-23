# Goodies Selection Observer Probe Plan - 2026-05-07

Status: public-safe runtime-observer setup, not executed runtime proof

## Objective

Prepare a read-only CDB observer for the next copied-profile Goodies wall runtime pass.

The prior runtime replay reached the Goodies wall but stalled at `Race Challenge 2`. Static/AppCore evidence now names the expected normal row sequence as `66, 67, 68, 69, 70, 74`. The next runtime pass should observe selected coordinates and returned Goodie ids directly instead of relying only on screenshot labels.

## What Changed

Added:

```text
tools/runtime-probes/goodies-selection-observer.cdb.txt
tools/runtime-probes/goodies-input-observer.cdb.txt
```

The command file installs read-only breakpoints at:

- `0x0045cb80` - `get_goodie_number`, logging `x`, `y`, and returned Goodie id.
- `0x0045cf2a` - right-navigation probe after clamp.
- `0x0045cf4c` - right-navigation backtrack scan.
- `0x0045d070` - selected-load gate.
- `0x0045c9f0` - `CFEPGoodies__StartLoadingGoody`.

The first copied-profile CDB run showed that the global `get_goodie_number`
breakpoint is extremely hot during Goodies wall rendering and can produce CDB
"commands were skipped" warnings when it uses `gu` inside the event handler.
Use the mapper observer when the question is broad coordinate-return sampling.
Use the focused input observer for navigation/selection proof:

```text
tools/runtime-probes/goodies-input-observer.cdb.txt
```

The focused observer avoids the global mapper breakpoint and instead logs:

- `CFEPGoodies__ButtonPressed` entry with the retail button id and current `mCX/mCY`.
- after-call return values for vertical scans, right clamp/backtrack, selected-state precheck, selected-load gate, post-load state check, and mark-selected-old.
- `CFEPGoodies__StartLoadingGoody` entry.

## Intended Use

Use this only against a copied-profile, windowed BEA runtime session:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\start_cdb_server.ps1 -CommandFile .\tools\runtime-probes\goodies-selection-observer.cdb.txt -PrintOnly
```

For a real run, omit `-PrintOnly` only after the copied profile is launched and ready. Keep the CDB log and raw runtime proof under ignored `subagents/`.

For copied-profile runtime proof, prefer exact PID attach after the managed window scan:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\start_cdb_server.ps1 -ProcessId <managed-bea-pid> -CommandFile .\tools\runtime-probes\goodies-selection-observer.cdb.txt
```

The helper now defaults to a local attached logger, refuses ambiguous process-name attach when multiple BEA processes are running, and fails if the debugger log is not created before the proof input starts. A missing CDB log is a setup/tooling failure, not Goodies behavior evidence.

For the next navigation-focused proof, prefer:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\start_cdb_server.ps1 -ProcessId <managed-bea-pid> -CommandFile .\tools\runtime-probes\goodies-input-observer.cdb.txt
```

## Expected Evidence

The useful runtime evidence is the logged sequence of:

- `get_goodie_number` coordinates,
- returned Goodie ids,
- right-navigation clamp/backtrack state,
- selected-load gate coordinates,
- `StartLoadingGoody` coordinates.

A GREEN runtime pass should either log the expected normal sequence `66, 67, 68, 69, 70, 74` or explain any runtime divergence from the static/AppCore invariant.

For the focused input observer, the useful evidence is button-entry events plus
after-call return values from the `CFEPGoodies__ButtonPressed` navigation and
selection call sites. This is the preferred next step because it avoids the
render-loop mapper flood observed in the first attached runtime log.

Parser prepared for that future log:

```powershell
py -3 tools\goodies_selection_observer_log_probe.py --log <private-cdb-log> --out <ignored-json> --check-normal-skip
```

Use `--check-normal-skip` only when the expected result is the ordinary wall path that skips 71-73. If a future run is deliberately hunting a hidden path, run without that flag and inspect `hiddenReturnIds`.

Harness guard:

```powershell
npm run test:goodies-selection-observer-log
```

This test keeps the parser sample cases and the CDB command-file output labels aligned before another live copied-profile run.

## Safety

- This file does not launch BEA.
- This file does not mutate BEA, saves, Ghidra, or runtime memory.
- This file does not patch the installed/original executable.
- Raw CDB logs remain private/ignored unless explicitly sanitized.
