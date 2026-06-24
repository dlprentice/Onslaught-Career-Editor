# WinUI Music Audible Output Materializer Readiness

Status: trusted materializer gate only
Date: 2026-06-23
Scope: `winui-safe-copy-music-audible-output-proof.v1` raw-to-sanitized builder

This slice adds `tools/winui_safe_copy_music_audible_output_materializer.py`,
which converts explicit private raw proof inputs into the sanitized two-run
audible-output proof schema and immediately validates the result with
`tools/winui_safe_copy_music_audible_output_two_run_harness_check.py`.

Accepted materializer inputs:

- clean/staged/mute `winui-safe-copy-live-runtime-smoke.v1` artifacts
- clean/staged timestamped CDB decode timeline sidecars generated or checked by
  `tools/winui_safe_copy_music_cdb_timeline_sidecar.py`, bound by live-artifact
  SHA-256, raw live CDB log SHA-256, and timestamped CDB evidence log SHA-256
  values, with timestamped raw CDB rows re-parsed by the materializer
- clean/mute source-music safety sidecars for source target/replacement hash
  unchanged facts
- ambient no-BEA process census sidecar bound to the ambient audio JSON and
  raw WAV SHA-256 values
- ambient/clean/staged/mute raw `audio-loopback-capture.v1` artifacts with
  helper-authored rawWavSha256 values
- sanitized capture-to-source correlation adapter artifact bound to clean/staged audio JSON and raw WAV SHA-256 values

Fail-closed checks:

- clean/staged launch arguments must include level `100` and must not include
  `-nomusic` or `-nosound`
- mute control must include `-nomusic` or `-nosound`
- clean must have no staged music replacement; staged must use
  `use-bea02-for-bea04`
- source executable, clean override, source save/options, and source music
  hashes must remain unchanged
- CDB logs must contain timestamped level, selection, async kick, Ogg open, and
  positive decoded PCM rows for `BEA_04(Master).ogg`
- each raw audio summary must point back to its own `outputJson`, and its raw
  WAV artifact must exist beside the JSON with matching byte count,
  helper-authored rawWavSha256, and independently rederived WAV sample statistics
- ambient no-BEA census must cover the full ambient capture window and bind to
  the ambient audio JSON plus raw WAV hashes
- capture-to-source correlation sidecar hashes must match the clean/staged
  audio JSON plus raw WAV hashes
- timestamped clean/staged audio capture windows must cover their CDB decode
  windows
- ambient and mute captures must stay below the non-silent threshold
- clean and staged captures must be non-silent
- all four captures must use the same sanitized endpoint and format
- calibration-tone captures are rejected
- final output must not publish raw WAV paths, JSON paths, CDB paths, source
  paths, copied-game paths, raw endpoint identifiers, local proof paths, or
  private runtime proof roots
- materialized output must stay inside the private raw input bundle

Validation:

- red: `py -3 tools\winui_safe_copy_music_audible_output_materializer_test.py`
  initially failed because the materializer module was absent
- red: `py -3 tools\winui_safe_copy_music_cdb_timeline_sidecar_test.py`
  caught omitted CLI arguments reporting the wrong missing-argument boundary
- green: `npm run test:winui-safe-copy-music-audible-output-materializer`
  including missing-WAV, stale-WAV-size, untimestamped-CDB, stale ambient-census,
  stale capture-source-correlation binding, ambient-census-window, and
  private-path-redaction/output-boundary negative cases
- green: `npm run test:winui-safe-copy-music-cdb-timeline-sidecar`
  validates the timestamped sidecar builder, raw/timestamped CDB log hash
  binding, and omitted-argument guard
- adjacent gates:
  - `npm run test:winui-safe-copy-music-audible-output-two-run-harness`
  - `npm run test:winui-safe-copy-music-capture-source-correlation`
  - `npm run test:audio-loopback-capture-helper`

Boundary:

- `runtimeAudibleOutputProof=false` remains the current project truth until a
  private live bundle is generated from real raw inputs and accepted by the
  materializer plus final checker.
- This is not a new BEA launch.
- This is not a new CDB attach.
- This is not a new audio capture.
- This is not current audible playback proof.
- This is not arbitrary external OGG compatibility.
- This is not all music cues.
- This is not loop behavior proof.
- This is not volume, mixing, or crossfade proof.
- This is not gameplay parity.
- This is not rebuild parity.
