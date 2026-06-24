# WinUI Music Capture Source Correlation Adapter Readiness

Status: adapter/checker only
Date: 2026-06-22
Scope: `use-bea02-for-bea04` future audible-output proof adapter

This slice adds a fail-closed checker for sanitized future live capture-to-source correlation summaries. The adapter validates the `winui-safe-copy-music-capture-source-correlation.v1` artifact shape and emits the exact `sourceAudioCorrelation` object expected by the two-run audible-output harness, but it does not create a BEA launch, CDB attach, audio capture, source decode run, or audible playback claim.

Accepted public-safe summary:

- `schema=winui-safe-copy-music-capture-source-correlation.v1`
- `adapterVersion=capture-source-correlation-helper.v1`
- `captureSourceCorrelationAdapter=true`
- `presetId=use-bea02-for-bea04`
- `levelId=100`
- `target=BEA_04(Master).ogg`
- `replacement=BEA_02(Master).ogg`
- `method=windowed-spectral-fingerprint` or `bounded-fingerprint`
- `minimumAcceptedMargin>=0.15`
- `runtimeAudibleOutputProof=false`

Validation surface:

- `tools/winui_safe_copy_music_capture_source_correlation_check.py`
- `tools/winui_safe_copy_music_capture_source_correlation_check_test.py`
- `npm run test:winui-safe-copy-music-capture-source-correlation`

Fail-closed behavior:

- Rejects any `runtimeAudibleOutputProof` field in the adapter artifact.
- Rejects raw WAV/OGG/PCM/base64/sample/spectrogram/envelope payload keys.
- Rejects private source paths, private capture paths, local repo paths, Steam paths, and device identifiers.
- Rejects RMS-only, peak-only, non-silent-only, tied, non-finite, or out-of-range score evidence.
- Rejects weak active-window counts and margins below the accepted minimum.
- Rejects score matrices that contradict the declared clean-baseline or staged-positive best match.

Boundary:

- This is not runtime audible BEA playback.
- This is not standalone audible-output proof.
- This is not raw audio publication.
- This is not private path publication.
- This is not all music cues.
- This is not arbitrary external OGG compatibility.
- This is not gameplay parity.
- This is not rebuild parity.
