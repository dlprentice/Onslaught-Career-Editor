# WinUI Music Source Audio Correlation Readiness

Status: private source-reference preflight
Date: 2026-06-22
Scope: `use-bea02-for-bea04` source-audio reference for future audible-output proof

This slice adds a private source-audio fingerprint/correlation helper for the shipped `BEA_04(Master).ogg` target and `BEA_02(Master).ogg` replacement used by the `use-bea02-for-bea04` copied-profile preset. The helper decodes the two source tracks through a pinned `NVorbis` path, emits redacted deterministic source-reference fingerprints and score summaries, and validates that the two source references are distinct enough for a future live capture-to-source comparison.

Accepted public-safe summary:

- `schema=winui-safe-copy-music-source-audio-correlation.v1`
- `sourceAudioReferenceFingerprint=true`
- `trackIds=BEA_02(Master).ogg, BEA_04(Master).ogg`
- `envelopeCorrelation=0.21995982677040438`
- `sourceDistinctMargin=0.7800401732295956`
- `minimumRequiredMargin=0.15`
- `sourceTracksDistinct=true`
- `runtimeAudibleOutputProof=false`

Validation surface:

- `tools/winui_safe_copy_music_source_audio_correlation_check.py`
- `tools/winui_safe_copy_music_source_audio_correlation_check_test.py`
- `npm run test:winui-safe-copy-music-source-audio-correlation`

Boundary:

- This is not runtime audible BEA playback.
- This is not loopback capture proof.
- This is not clean baseline capture proof.
- This is not staged positive capture proof.
- This is not all music cues.
- This is not arbitrary external OGG compatibility.
- This is not gameplay parity.
- This is not rebuild parity.
- Raw audio payloads, source file paths, private capture paths, and private proof roots remain excluded from public docs/release scope.
