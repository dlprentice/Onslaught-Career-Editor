# WinUI Music Ambient No-BEA Census Producer

Status: producer/checker infrastructure only
Date: 2026-06-24
Scope: `winui-safe-copy-music-ambient-no-bea-census`

This slice adds `tools/winui_safe_copy_music_ambient_no_bea_census.py` and
`test:winui-safe-copy-music-ambient-no-bea-census`.

The producer builds the `winui-safe-copy-no-bea-process-census.v1` sidecar used
by the future music audible-output materializer. It validates an existing
ambient `audio-loopback-capture.v1` JSON/WAV artifact, verifies the helper
reported `rawWavSha256` matches the raw WAV, validates process samples cover the
ambient audio capture window, and rejects the sidecar if any observed process
image resolves to `BEA.exe`.

What changed:

| Item | Evidence |
| --- | --- |
| Producer/checker | `tools/winui_safe_copy_music_ambient_no_bea_census.py` |
| Test | `tools/winui_safe_copy_music_ambient_no_bea_census_test.py` |
| Package script | `test:winui-safe-copy-music-ambient-no-bea-census` |
| Gate update | `ambientCensus` now points at the tracked producer; this ambient slice reduced the producer-gap count from four to three, the later source-safety slice reduced the count to two, the later capture-source correlation builder slice reduced the count to one, and the later timestamped CDB log producer slice closed the last producer gap. |

Claim boundary:

- `runtimeAudibleOutputProof=false`
- no BEA launch
- no CDB attach
- no audio capture
- no source/game payload read
- no byte patch
- no installed-game mutation
- no original executable mutation
- no all-cue audio proof
- no gameplay parity proof
- no online proof
- no rebuild parity proof

Representative focused validation:

```powershell
py -3 tools\winui_safe_copy_music_ambient_no_bea_census_test.py
py -3 tools\winui_safe_copy_music_ambient_no_bea_census.py --self-test
npm run test:winui-safe-copy-music-ambient-no-bea-census
npm run test:winui-safe-copy-music-audible-output-live-bundle-gate
```

producer coverage is complete before the next private live audible-output
attempt. Actual ambient, clean, staged, mute, CDB timeline, source-safety,
audio, and capture-correlation sidecars are still required in the future private
raw bundle.
