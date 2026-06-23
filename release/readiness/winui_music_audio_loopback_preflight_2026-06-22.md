# WinUI Music Audio Loopback Preflight

Status: private helper preflight
Date: 2026-06-22
Scope: bounded audio-output capture infrastructure for the future safe-copy music audible-output proof

This slice adds `tools/capture_audio_loopback.py`, an explicitly armed Windows WASAPI loopback helper. The helper writes artifacts only under an allowed output root, rejects Program Files/source-game overlap, records device and format metadata, and emits RMS/peak/non-silent metrics. The helper is private/release-excluded because it can capture system audio.

Machine-readable summary:

- `audioLoopbackBackendPreflight=true`
- `audioLoopbackCalibrationNonSilent=true`
- `runtimeAudibleOutputProof=false`

Preflight result:

| Field | Value |
| --- | --- |
| audioLoopbackBackendPreflight | true |
| audioLoopbackCalibrationNonSilent | true |
| runtimeAudibleOutputProof | false |
| Device | `Speaker (Realtek(R) Audio)` |
| Sample rate | `48000` |
| Channels | `2` |
| Requested duration | `700 ms` |
| Observed duration | `1752 ms` |
| Bytes recorded | `192000` |
| WAV bytes | `192058` |
| Sample count | `48000` |
| Peak absolute sample | `0.018935322761535645` |
| RMS | `0.009140619348333236` |
| Non-silent | true |

Validation:

```powershell
py -3 tools\capture_audio_loopback.py --self-test
npm run test:audio-loopback-capture-helper
npm run test:winui-safe-copy-music-audible-output-contract
```

Claim boundary:

- Proves this workstation can produce a bounded WASAPI loopback artifact and observe a short explicitly armed calibration tone.
- Preserves `runtimeAudibleOutputProof=false`.
- Does not prove current BEA audible playback, source-bound BEA music output, safe-copy music replacement output, clean same-level baseline difference, CDB/audio time correlation, arbitrary external OGG compatibility, all music cues, loop behavior, volume behavior, mixing/crossfade behavior, gameplay parity, rebuild parity, or no-noticeable-difference parity.

Next proof rung:

- Build or run a fail-closed two-run harness for `use-bea02-for-bea04` at level `100`: clean same-level baseline versus staged positive, both with exact-PID CDB selection/decode evidence and bounded audio-output capture.
