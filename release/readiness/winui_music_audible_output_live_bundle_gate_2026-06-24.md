# WinUI Music Audible-Output Live Bundle Gate

Status: complete proof-gate infrastructure
Date: 2026-06-24
Scope: `winui-safe-copy-music-audible-output-live-bundle-gate`

This slice adds a machine-checkable gate for the next private music audible-output live raw-bundle attempt. It does not launch BEA, attach CDB, capture audio, read private game/media payloads, mutate files, or claim audible runtime playback.

Added:

| Item | Evidence |
| --- | --- |
| Gate tool | `tools/winui_safe_copy_music_audible_output_live_bundle_gate.py` |
| Test | `tools/winui_safe_copy_music_audible_output_live_bundle_gate_test.py` |
| Package script | `test:winui-safe-copy-music-audible-output-live-bundle-gate` |
| Contract update | `roadmap/music-audible-proof-contract.v1.json` now records `liveRawBundleGate=true` and `timestampedCdbLogProducer=true` while preserving `runtimeAudibleOutputProof=false`. |

The gate records the 13 raw inputs the trusted materializer requires:

`cleanLive`, `stagedLive`, `muteLive`, `cleanTimeline`, `stagedTimeline`, `cleanSourceMusicSafety`, `muteSourceMusicSafety`, `ambientCensus`, `ambientAudio`, `cleanAudio`, `stagedAudio`, `muteAudio`, and `captureSourceCorrelation`.

The gate now records producer coverage as complete for the next private live
attempt after preflight. Its JSON output is path-redacted: it does not publish
private proof roots, source game paths, copied-game paths, raw CDB paths, or WAV
paths.

The timestamped CDB log raw inputs now have a tracked producer:
`tools/winui_safe_copy_music_timestamped_cdb_log_producer.py`. That producer
uses a trusted-tail observation ledger bound to an untimestamped raw CDB log by
SHA-256 and per-line hashes, writes a UTC timestamp-prefixed CDB evidence log,
and validates it against the existing timeline parser. It does not launch BEA,
attach CDB, spawn processes, capture audio, or make an audible-output claim.

The `ambientCensus` raw input now has a tracked producer:
`tools/winui_safe_copy_music_ambient_no_bea_census.py`. That producer only
builds/verifies the ambient no-BEA process census sidecar from an existing
ambient audio JSON/WAV artifact plus process samples that cover that ambient
capture window. It does not capture audio, launch BEA, or make an audible-output
claim.

The clean/mute source music safety raw inputs now have a tracked producer:
`tools/winui_safe_copy_music_source_music_safety_sidecar.py`. That producer
uses a before-run source music hash snapshot plus a post-run source-root hash
check to build `winui-safe-copy-source-music-safety.v1` sidecars bound to clean
or mute live artifacts. Actual clean and mute sidecars are still required in a
future private live bundle.

The capture-source correlation raw input now has a tracked producer:
`tools/winui_safe_copy_music_capture_source_correlation_builder.py`. That
producer builds a sanitized `winui-safe-copy-music-capture-source-correlation.v1`
adapter from explicit clean/staged audio JSON/WAV artifacts plus read-only
source music references. The actual capture-correlation sidecar is still
required in a future private live bundle.

The armed private executor for producing a future live raw bundle is tracked in
`tools/run_winui_safe_copy_music_audible_output_live_bundle.py` and guarded by
`test:winui-safe-copy-music-audible-output-live-bundle-executor`. It is not run
by this gate and does not change this note's no-launch/no-capture boundary.

Remaining future live-bundle raw evidence includes actual clean/staged
timestamped CDB logs, clean/staged timeline sidecars, clean/mute source-safety
sidecars, ambient census, ambient/clean/staged/mute audio captures, and
capture-correlation sidecars. producer coverage is complete, but those raw
artifacts have not been produced by this slice.

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
py -3 tools\winui_safe_copy_music_audible_output_live_bundle_gate_test.py
py -3 tools\winui_safe_copy_music_audible_output_live_bundle_gate.py --self-test
py -3 tools\winui_safe_copy_music_timestamped_cdb_log_producer_test.py
py -3 tools\winui_safe_copy_music_timestamped_cdb_log_producer.py --self-test
npm run test:winui-safe-copy-music-audible-output-live-bundle-gate
npm run test:winui-safe-copy-music-audible-output-live-bundle-executor
```

Next step: make a single private live attempt under the approved private runtime-proof root only if preconditions are clean, then feed its raw artifacts through the materializer and final checker before any audible-output claim.
