# Goodies Selection Observer Runtime Attempt - 2026-05-08

Status: YELLOW copied-profile runtime observer evidence; debugger attach helper hardened afterward

## Objective

Run the prepared Goodies selection observer against a copied-profile, windowed BEA session so the next Goodies wall proof can rely on CDB-selected Goodie ids instead of screenshots alone.

## Public-Safe Result

The first copied-profile launch, managed-window scan, scoped input sequence, and post-navigation capture completed against the copied runtime profile. That attempt did not create the expected debugger log, so no `get_goodie_number` or selected-load event sequence was parsed.

After helper hardening, a second copied-profile observer run created and parsed a CDB log. The parser produced:

```text
verdict: INCOMPLETE_SEQUENCE
coordinateSampleCount: 1017
navigationEventCount: 0
hiddenReturnIds: []
expectedNormalSequenceObserved: false
```

The observer saw rendered coordinate returns including `66`, `67`, and `68`, but did not observe `69`, `70`, or `74` in the parsed sample, and it did not observe right-navigation events. The post-navigation capture showed the Goodies wall at `Hawk Winter`, so this remains a YELLOW navigation/proof-state result rather than the desired normal-skip proof.

A parser rerun after the focused-input observer extension confirmed that the
log contains `1018` CDB "commands were skipped" warnings, `inputPathObserved:
false`, `buttonEventCount: 0`, and `navigationEventCount: 0`. That refines the
failure mode: the run sampled the hot rendered mapper path, but it did not
prove the input-handler path.

## Private Evidence Boundary

Raw runtime outputs remain ignored under:

```text
subagents/goodies-selection-observer-runtime-2026-05-08/
```

The private folder contains copied-profile launch records, managed-window scans, scoped input summaries, CDB attach output, post-navigation captures, CDB logs where available, and parser summaries. The successful-log attempt remains private because it includes raw runtime logs and screenshots.

Do not commit screenshots, raw frames, copied executables, private paths, or raw runtime proof JSON from that folder.

## Helper Hardening

`tools/start_cdb_server.ps1` now supports exact PID attach:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\start_cdb_server.ps1 -ProcessId <managed-bea-pid> -CommandFile .\tools\runtime-probes\goodies-selection-observer.cdb.txt
```

The helper now:

- uses CDB `-p <pid>` when `-ProcessId` is provided,
- rejects ambiguous process-name attach when multiple BEA processes are running,
- verifies the requested PID is the expected process name,
- rejects TCP server passwords containing punctuation before CDB is launched,
- defaults to local attached logging because current CDB exits before logging when `-server` is combined directly with a PID/name attach target,
- waits for the debugger log to exist before proof input should proceed,
- aborts and stops the CDB process if no log is created before the timeout.

A follow-up exact-PID rerun showed CDB exits before opening the log when the TCP server password contains punctuation such as a hyphen. Future copied-profile observer runs must use a simple password such as `goodiesobserver`.

Another attach diagnostic showed direct local `-p <pid>` attach can log and detach cleanly, while `-server ... -p <pid>` exits before opening the log in this WinDbg package. Future observer proof should use the default local attached logger unless a separate server/client attach path is proven.

## Not Claimed

- This does not prove hidden/non-grid Goodie reachability or unreachability.
- This does not prove the normal wall sequence `66, 67, 68, 69, 70, 74` by CDB log.
- This does not prove hidden/non-grid Goodies are impossible; it only records that the parsed observer run returned no `71`, `72`, or `73`.
- This does not prove in-game model-viewer playback.
- This does not mutate the installed game, the original `BEA.exe`, saves, or Ghidra.

## Next Runtime Step

Rerun or adjust the copied-profile Goodies observer with exact `-ProcessId` attach after `tools/list_game_windows.ps1` identifies the managed BEA window, then run:

```powershell
py -3 tools\goodies_selection_observer_log_probe.py --log <private-cdb-log> --out <ignored-json> --check-normal-skip
```

Prefer the focused input observer for the next navigation pass:

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\start_cdb_server.ps1 -ProcessId <managed-bea-pid> -CommandFile .\tools\runtime-probes\goodies-input-observer.cdb.txt
```

A GREEN observer pass should include a real CDB log and parser summary that observes the expected normal wall navigation sequence. The current attempt should remain YELLOW until that evidence exists.

Post-fix focused-observer pass: `release/readiness/goodies_input_observer_runtime_proof_2026-05-08.md` records the follow-up GREEN copied-profile input-path proof. It confirms the ordinary Goodies wall right-navigation sequence `66, 67, 68, 69, 70, 74` with no `71`, `72`, or `73` returns on that normal path.
