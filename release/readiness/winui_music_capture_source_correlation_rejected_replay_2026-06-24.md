# WinUI Music Capture-Source Correlation Rejected Replay

Status: rejected local replay diagnostic
Date: 2026-06-24
Scope: `winui-safe-copy-music-capture-source-correlation-rejected-replay`

This slice replayed a maintainer-local nominal 60-second live-bundle attempt,
artifact ID
`music-audible-live-20260624-144834`, through
`tools/winui_safe_copy_music_capture_source_correlation_builder.py` after the
rejection-diagnostic hardening landed. The replay did not launch BEA, attach
CDB, capture audio, patch bytes, or mutate the installed game. It read the
existing private clean/staged audio sidecars plus read-only source music files
and produced a local-only rejected diagnostic sidecar validated by
`tools/winui_safe_copy_music_capture_source_correlation_check.py
--rejection-diagnostic`.

Result:

| Field | Value |
| --- | --- |
| Schema | `winui-safe-copy-music-capture-source-correlation-rejection.v1` |
| Rejection reason | `staged-positive-source-correlation-margin-too-weak` |
| Clean best match | `BEA_04(Master).ogg` |
| Staged best match | `BEA_04(Master).ogg` |
| Clean margin | `0.18338686002643562` |
| Staged margin | `-0.16189222398297243` |
| Minimum accepted margin | `0.15` |
| Staged target score | `0.862301545952873` |
| Staged replacement score | `0.7004093219699006` |
| `runtimeAudibleOutputProof` | `false` |

Guard tokens: `stagedPositiveBestMatch=BEA_04(Master).ogg`;
`runtimeAudibleOutputProof=false`.

Replay diagnostic guard tokens: `stagedFileLayoutProven=true`;
`exactPidDecodeTimelineProven=true`; `captureSourceCorrelationRejected=true`.

Replay diagnostic:

`tools/winui_safe_copy_music_rejected_replay_diagnostic_check.py` now validates
the same local bundle through a JSON-only diagnostic that ties the staged
live-smoke manifest, clean/staged CDB timeline sidecars, and rejected
capture-source sidecar together without reading raw WAVs, raw CDB logs, source
audio payloads, or copied executables.

| Field | Value |
| --- | --- |
| Schema | `winui-safe-copy-music-rejected-replay-diagnostic.v1` |
| `stagedFileLayoutProven` | `true` |
| `exactPidDecodeTimelineProven` | `true` |
| `captureSourceCorrelationRejected` | `true` |
| Clean/staged provenance | `cgame-restart-loop-direct` |
| Clean/staged row counts | `playSelectionRows=1`, `asyncKickRows=1`, `oggOpenRows=1`, `oggReadRows=1` |

Decode-window diagnostic:

`tools/winui_safe_copy_music_decode_window_correlation_diagnostic.py` now
validates a second JSON-only local sidecar over the same rejected bundle. It
asks whether the audio near the exact-PID CDB decode instant can be correlated
against a sliding source window without publishing raw WAVs, raw CDB logs,
source paths, or private proof roots.

| Field | Value |
| --- | --- |
| Schema | `winui-safe-copy-music-decode-window-correlation-diagnostic.v1` |
| Artifact-relative output | `raw/decode-window-correlation-diagnostic.json` |
| `decodeWindowInsideRawAudioCapture` | `false` |
| Clean decode offset / raw duration | `46208.935ms` / `11380.0ms` |
| Staged decode offset / raw duration | `44148.22ms` / `11880.0ms` |
| Skipped analysis rows | all rows skipped as `capture-window-out-of-range` |
| `stagedReplacementPreferredInDecodeWindow` | `false` (unavailable, not measured preference) |
| `runtimeAudibleOutputProof` | `false` |

Interpretation:

- The local sidecar proves the rejected correlation diagnosis is now
  machine-readable and validator-backed.
- The staged copied file layout is still proven: the copied target matched the
  replacement bytes, the backup matched the original bytes, and source music
  hashes were unchanged.
- The clean and staged exact-PID CDB timeline sidecars still prove level-100
  selection/decode windows through restart-loop direct provenance.
- The staged-positive capture still correlates more strongly with
  `BEA_04(Master).ogg` than with the staged replacement
  `BEA_02(Master).ogg`.
- The decode-window diagnostic could not evaluate the actual CDB decode
  instant because the raw WAV payload spans only about 11-12 seconds while the
  CDB decode instant is about 44-46 seconds after capture start. That narrows
  the next blocker to loopback capture data-span/duration/flush alignment
  rather than copied-file staging or another BEA patch guess.
- `stagedReplacementPreferredInDecodeWindow=false` means unavailable in this
  diagnostic, not measured source preference.
- The accepted `capture-source-correlation.json` adapter remains absent for
  this replay.

Claim boundary:

- not accepted capture-source correlation
- not materializer input
- not runtime audible-output proof
- not all-cue audio proof
- not gameplay parity proof
- not online proof
- not rebuild parity proof
- no private path publication
- no raw audio publication
- no source audio path publication
- no raw CDB log publication
- no screenshot or frame-dump publication

Focused validation:

```powershell
npm run test:winui-safe-copy-music-audible-output-contract
npm run test:winui-safe-copy-music-capture-source-correlation
npm run test:winui-safe-copy-music-capture-source-correlation-builder
npm run test:winui-safe-copy-music-decode-window-correlation-diagnostic
```

Maintainer-local replay commands may use private raw audio sidecars and source
music files from ignored overlays. Do not commit generated rejection sidecars,
raw WAVs, raw CDB logs, screenshots, frames, copied executables, or source audio
payloads.

Next useful music proof step: fix or replace the loopback capture helper path so
the raw WAV data span covers the CDB decode instant, then rerun the
decode-window/sliding-source diagnostic before attempting materialization.
