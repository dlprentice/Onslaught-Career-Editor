# WinUI Music Audible Output Two-Run Harness Readiness

Status: acceptance checker only
Date: 2026-06-22
Scope: `use-bea02-for-bea04` level-100 audible-output proof target

This slice adds a fail-closed checker for the future `winui-safe-copy-music-audible-output-proof.v1` bundle and a public-safe plan scaffold for the next private live attempt. The follow-up hardening wires the mute-control live-smoke stage through bounded `--launch-nomusic` / `--launch-nosound` helper switches, records capture start/end timestamps from the loopback helper, and rejects hand-authored proof summaries that lack timestamp coverage, sanitized endpoint equality, or non-silent clean/staged output. It does not create a new BEA launch, CDB attach, audio capture, or audible playback claim.

Follow-up materializer gate: `release/readiness/winui_music_audible_output_materializer_2026-06-23.md` records the trusted raw-artifact-to-sanitized-proof builder that now prevents accepting a hand-authored final JSON blob as audible-output evidence.

Added checks:

- clean `BEA_04(Master).ogg` level-100 baseline and staged `BEA_02(Master).ogg` over copied `BEA_04(Master).ogg` positive run
- exact-PID CDB evidence for level `100`, selection `2`, async kick, Ogg open, and decoded PCM request on both compared runs
- source-safety gates for installed executable, override executable, source target music, source replacement music, preexisting BEA process state, and post-stop BEA process state
- no `-nomusic` or `-nosound` on the positive proof path
- timestamped clean/staged audio windows that cover their CDB decode windows
- same sanitized audio endpoint and format between clean/staged/ambient/mute runs
- ambient/no-BEA and mute-control negative controls
- non-silent clean baseline and staged-positive output
- raw device identifiers and private paths excluded from the sanitized proof
- source-audio correlation showing clean baseline prefers original `BEA_04(Master).ogg` and staged positive prefers replacement `BEA_02(Master).ogg`
- rejection of RMS-only, peak-only, non-silent-only, or clean-vs-positive-only evidence

Validation surface:

- `tools/winui_safe_copy_music_audible_output_two_run_harness_check.py`
- `tools/winui_safe_copy_music_audible_output_two_run_harness_check_test.py`
- `tools/run_winui_safe_copy_music_audible_output_two_run_harness.py`
- `tools/run_winui_safe_copy_music_audible_output_two_run_harness_test.py`
- `tools/winui_safe_copy_music_audible_output_materializer.py`
- `tools/winui_safe_copy_music_audible_output_materializer_test.py`
- `npm run test:winui-safe-copy-music-audible-output-two-run-harness`
- `npm run test:winui-safe-copy-music-audible-output-materializer`

Boundary:

- `runtimeAudibleOutputProof=false` remains the current accepted project truth.
- This is not current audible playback proof.
- This is not arbitrary external OGG compatibility.
- This is not all music cues.
- This is not loop behavior proof.
- This is not volume, mixing, or crossfade proof.
- This is not gameplay parity.
- This is not rebuild parity.
- This is not no-noticeable-difference parity.
- Raw WAV/audio, raw CDB logs, local proof paths, PIDs, HWNDs, device identifiers, screenshots, and private runtime proof bundles remain private/excluded evidence.
