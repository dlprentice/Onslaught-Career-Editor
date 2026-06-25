# WinUI Music Loopback Wall-Clock Padding Hardening

Status: accepted helper/contract hardening; broad closeout green
Date: 2026-06-25
Scope: `winui-safe-copy-music-loopback-wall-clock-padding`

This slice hardens the audio loopback helper and materializer after the
`music-audible-live-20260624-144834` rejected replay showed a specific timing
failure: the CDB decode instant was about 44-46 seconds after capture start,
but the raw WAV data payload spanned only about 11-12 seconds.

Changes:

| Area | Result |
| --- | --- |
| Loopback helper | Inserts zero-silence padding for WASAPI loopback quiet gaps so WAV byte offsets preserve wall-clock capture duration. |
| Helper validation | Requires `capturedBytes + silencePaddingBytes == bytesRecorded`, enabled `wallClockPadding`, valid block alignment, positive byte rate, and raw data duration covering requested capture duration. |
| Materializer | Independently derives raw WAV data duration from canonical RIFF sample-rate/block-align/data-frame math, rejects forged byte-rate/block-align headers, rejects non-frame-aligned data, requires enabled `wallClockPadding` metadata, verifies `capturedBytes + silencePaddingBytes == bytesRecorded`, and rejects audio summaries whose timestamps outlast the actual WAV data span or whose data span does not cover the CDB decode window. |
| Diagnostic fixtures | Updated to use capture windows whose raw test WAV data spans match the claimed timestamps. |
| Contract checker | Requires the new wall-clock padding and raw-WAV duration/header-consistency guard flags/text while preserving `runtimeAudibleOutputProof=false`. |

Focused validation:

```powershell
py -3 -m py_compile tools\capture_audio_loopback.py tools\capture_audio_loopback_test.py tools\winui_safe_copy_music_audible_output_materializer.py tools\winui_safe_copy_music_audible_output_materializer_test.py
py -3 tools\capture_audio_loopback_test.py
py -3 tools\winui_safe_copy_music_audible_output_materializer_test.py
npm run test:audio-loopback-capture-helper
npm run test:winui-safe-copy-music-audible-output-materializer
npm run test:winui-safe-copy-music-decode-window-correlation-diagnostic
npm run test:winui-safe-copy-music-audible-output-contract
dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiProductLaneTests.PatchBench"
npm run test:winui-safe-copy-music-audible-output-live-bundle-executor
```

Broad closeout validation:

```powershell
npm run test:doc-commands
npm run test:md-links
npm run release:profile-check
npm run release:curated-check
npm run test:hard-payload-safety
npm run test:public-allowlist
npm run test:repo-hygiene
git diff --check
```

Adversarial hardening follow-up:

- forged low `byteRate` headers must not stretch a short WAV on paper
- `blockAlign` must equal `channels * bitsPerSample / 8`
- `byteRate` must equal `sampleRate * blockAlign`
- raw WAV `data` length must be block aligned
- materializer input must include enabled helper-authored `wallClockPadding`
  metadata and matching `capturedBytes`, `silencePaddingBytes`, and
  `dataBytesWritten` totals

Consult record:

- Adversarial review found the forged-header risk; fixed with canonical WAV
  header/data-frame validation.
- Specialist review found the materializer padding-metadata gap; fixed with
  wall-clock padding metadata requirements and regression tests.
- Docs/state audit found stale broad-validation state; state now separates
  previous v1.0.7 validation from active-slice validation until broad closeout
  is actually rerun.

Claim boundary:

- not runtime audible-output proof
- not accepted capture-source correlation
- not materializer input for the old rejected bundle
- not a new BEA launch
- not a CDB attach
- not source-bound audio replacement proof
- not all-cue, volume, loop, or mix proof
- not gameplay parity proof
- not online proof
- not rebuild parity proof
- no installed-game or original `BEA.exe` mutation

Next useful music proof step: run a new private live bundle only after this
helper hardening is present, then require the materializer and final checker to
accept the new raw bundle before changing `runtimeAudibleOutputProof=false`.
