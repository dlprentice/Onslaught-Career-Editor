# WinUI Music Capture-Source Correlation Builder

Status: producer/checker infrastructure only
Date: 2026-06-24
Scope: `winui-safe-copy-music-capture-source-correlation-builder`

This slice adds `tools/winui_safe_copy_music_capture_source_correlation_builder.py`
and `test:winui-safe-copy-music-capture-source-correlation-builder`.

The builder creates the `winui-safe-copy-music-capture-source-correlation.v1`
raw sidecar used by the future music audible-output materializer. It consumes
explicit clean/staged loopback audio JSON/WAV artifacts plus read-only source
music references for `BEA_04(Master).ogg` and `BEA_02(Master).ogg`, computes a
bounded windowed correlation, and writes a sanitized adapter artifact that the
existing capture-source correlation checker accepts.

What changed:

| Item | Evidence |
| --- | --- |
| Producer/checker | `tools/winui_safe_copy_music_capture_source_correlation_builder.py` |
| Test | `tools/winui_safe_copy_music_capture_source_correlation_builder_test.py` |
| Package script | `test:winui-safe-copy-music-capture-source-correlation-builder` |
| Contract update | `roadmap/music-audible-proof-contract.v1.json` now records `captureSourceCorrelationBuilder=true` while preserving `runtimeAudibleOutputProof=false`. |
| Gate update | `captureSourceCorrelation` now points at the tracked builder; this slice reduced the producer-gap count from two to one, and the later timestamped CDB log producer slice closed the last producer gap. |

The sidecar binds to the clean/staged audio JSON and raw WAV SHA-256 values and
keeps private source paths, raw audio samples, spectrograms, raw WAV paths, raw
JSON paths, and endpoint identifiers out of the sanitized output.

Claim boundary:

- `runtimeAudibleOutputProof=false`
- no BEA launch
- no CDB attach
- no audio capture
- no byte patch
- no installed-game mutation
- no original executable mutation
- no source/game mutation
- no all-cue audio proof
- no gameplay parity proof
- no online proof
- no rebuild parity proof

Representative focused validation:

```powershell
py -3 tools\winui_safe_copy_music_capture_source_correlation_builder_test.py
py -3 tools\winui_safe_copy_music_capture_source_correlation_builder.py --self-test
npm run test:winui-safe-copy-music-capture-source-correlation-builder
npm run test:winui-safe-copy-music-audible-output-live-bundle-gate
```

producer coverage is complete before the next private live audible-output
attempt. Actual ambient, clean, staged, mute, CDB timeline, source-safety,
audio, and capture-correlation sidecars are still required in the future private
raw bundle.
