# WinUI Music CGame Caller Diagnostic

Status: bounded copied-runtime diagnostic accepted
Date: 2026-06-24
Scope: `winui-safe-copy-music-cgame-caller-diagnostic`

This slice adds a diagnostic CDB observer and checker for the unresolved
level-100 music proof gap. It does not accept audible output. It answers a
narrower question: when the final materializer misses the
`CGame__PlayMusicForCurrentLevel level=100` row, can the copied runtime still
show a level-100 music-selection call path inside the `CGame` restart-loop
region?

Added:

| Item | Evidence |
| --- | --- |
| CDB observer | `tools/runtime-probes/safe-copy-music-cgame-caller-diagnostic-observer.cdb.txt` |
| Checker | `tools/winui_safe_copy_music_cgame_caller_diagnostic_check.py` |
| Package script | `test:winui-safe-copy-music-cgame-caller-diagnostic` |
| Local ignored artifact | `music-cgame-diagnostic-20260624-131246/live-safe-copy-runtime-smoke.json` |

Accepted diagnostic result:

| Field | Value |
| --- | --- |
| Classification | `restart-loop-direct-level100-music-selection-observed` |
| `CGame__PlayMusicForCurrentLevel` rows | `0` |
| Level-100 `CMusic__PlaySelection` caller rows | `1` |
| Restart-loop direct rows | `1` |
| Direct return address | `0x0046e0bf` |
| Restart-loop range | `0x0046dc30..0x0046e240` |
| Async stream kick rows | `2` |
| Ogg open rows | `2` |
| Ogg decoded-PCM read rows | `1` |
| Max decode request | `524288` |
| `runtimeAudibleOutputProof` | `false` |

The observed caller row was:

```text
CMusic__PlaySelectionCaller ... caller=0046e0bf globalLevel=100 selection=2 ...
```

The return address `0x0046e0bf` is the instruction after the direct
`CALL 0x004bb8c0 CMusic__PlaySelection` inside
`CGame__RestartLoopRunLevel`, reached after the retail restart-loop level check
selects music id `2` for level `100`. The diagnostic therefore narrows the
previous failure: the missing wrapper-entry row is not enough to say level-100
music selection did not happen.

Claim boundary:

- no audible-output proof;
- no loopback/source-correlation acceptance;
- no all-cue, volume, mute, loop, or in-game mix proof;
- no gameplay parity proof;
- no online proof;
- no rebuild or no-noticeable-difference proof;
- no installed-game mutation;
- no original executable mutation;
- no Ghidra mutation.

Current interpretation:

- the materializer/timeline/final-checker contract now carries explicit
  `musicSelectionProvenance` values;
- the only accepted selector-provenance values are `cgame-wrapper` and
  `cgame-restart-loop-direct`;
- restart-loop direct provenance is accepted only when the timestamped CDB log
  and timeline sidecar agree on caller `0x0046e0bf`, level `100`, and selection
  `2`;
- this diagnostic by itself still does not accept audible output. A future
  private raw bundle must still pass audio, source-safety, capture-correlation,
  process-cleanup, materializer, and final-checker gates before
  `runtimeAudibleOutputProof` can become true.

Validation:

```powershell
py -3 -m py_compile tools\winui_safe_copy_music_cgame_caller_diagnostic_check.py
npm run test:winui-safe-copy-music-cgame-caller-diagnostic
py -3 tools\winui_safe_copy_music_cgame_caller_diagnostic_check.py "<ignored-artifact-root>\music-cgame-diagnostic-20260624-131246\live-safe-copy-runtime-smoke.json"
```
