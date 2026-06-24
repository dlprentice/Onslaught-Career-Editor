# WinUI Safe-Copy Music Swap Runtime Artifact Checker Readiness Note

Status: validated checker/helper slice
Date: 2026-06-17

Scope: make named copied-track music swap runtime artifacts checkable without claiming audio playback.

This slice adds a public-safe artifact checker for future live safe-copy runs that use a named music swap preset. The checker validates the generated `winui-safe-copy-live-runtime-smoke.v1` JSON boundary for `use-bea02-for-bea01` and `use-bea01-for-bea02`.

Tracked outcomes:

| Area | Result |
| --- | --- |
| Runtime helper wiring | `tools/winui_safe_copy_live_runtime_smoke.py` accepts `--music-swap-preset-id` / `ONSLAUGHT_LIVE_MUSIC_SWAP_PRESET_ID` and stages the selected preset through `GameProfileMusicReplacementService.BuildSafeCopyMusicSwapPresetOptions`. |
| Artifact checker | `tools/winui_safe_copy_music_swap_preset_artifact_check.py` validates preset id, target/replacement names, concrete before/after source executable and music hashes, backup/restore evidence, required windowed patch keys, launch/stop observations, and claim-boundary text. |
| Package script | `npm run test:winui-safe-copy-music-swap-runtime-artifact-checker` runs the checker self-test. A real runtime artifact is validated by passing its JSON path directly to `tools\winui_safe_copy_music_swap_preset_artifact_check.py`. |
| Safety boundary | The checker requires installed/source executable and music hashes to stay unchanged and treats the artifact as staging/source-safety proof only. |

Validation run:

- `py -3 tools\winui_safe_copy_music_swap_preset_artifact_check.py --self-test` - passed.
- `py -3 tools\winui_safe_copy_live_runtime_smoke_test.py` - passed, 4 tests.
- `npm run test:winui-safe-copy-music-swap-runtime-artifact-checker` - passed.
- `npm run test:winui-safe-copy-live-runtime-smoke-helper` - passed.

Not claimed:

- No live BEA launch was performed by this checker slice.
- No runtime audio playback, cue selection, Vorbis decode, volume, or audible-output proof.
- No installed-game mutation and no original `BEA.exe` mutation.
- No new executable patch row.
- No Enhanced Profile Preview default inclusion.
