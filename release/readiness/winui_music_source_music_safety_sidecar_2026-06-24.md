# WinUI Music Source-Music Safety Sidecar Producer

Status: producer/checker infrastructure only
Date: 2026-06-24
Scope: `winui-safe-copy-music-source-music-safety-sidecar`

This slice adds `tools/winui_safe_copy_music_source_music_safety_sidecar.py`
and `test:winui-safe-copy-music-source-music-safety-sidecar`.

The producer builds the `winui-safe-copy-source-music-safety.v1` sidecars used
by the future music audible-output materializer for the clean baseline and mute
control runs. It is a two-phase safety helper:

1. Write a before-run source music hash snapshot for `BEA_04(Master).ogg` and
   `BEA_02(Master).ogg`.
2. After the clean or mute live run, re-hash those source files, bind the
   unchanged result to the live artifact SHA-256, and write the sidecar.

What changed:

| Item | Evidence |
| --- | --- |
| Producer/checker | `tools/winui_safe_copy_music_source_music_safety_sidecar.py` |
| Test | `tools/winui_safe_copy_music_source_music_safety_sidecar_test.py` |
| Package script | `test:winui-safe-copy-music-source-music-safety-sidecar` |
| Gate update | `cleanSourceMusicSafety` and `muteSourceMusicSafety` now point at the tracked producer; the later capture-source correlation builder slice reduced the current unresolved producer-gap count to one. |

The sidecar exposes only hashes/counts and bounded booleans, including
`sourceTargetHashUnchanged` and `sourceReplacementHashUnchanged`; it does not
publish source paths.

Claim boundary:

- `runtimeAudibleOutputProof=false`
- no BEA launch
- no CDB attach
- no audio capture
- no byte patch
- no installed-game mutation
- no original executable mutation
- no all-cue audio proof
- no gameplay parity proof
- no online proof
- no rebuild parity proof

Representative focused validation:

```powershell
py -3 tools\winui_safe_copy_music_source_music_safety_sidecar_test.py
py -3 tools\winui_safe_copy_music_source_music_safety_sidecar.py --self-test
npm run test:winui-safe-copy-music-source-music-safety-sidecar
npm run test:winui-safe-copy-music-audible-output-live-bundle-gate
```

producer coverage is complete before the next private live audible-output
attempt. Actual ambient, clean, staged, mute, CDB timeline, source-safety,
audio, and capture-correlation sidecars are still required in the future private
raw bundle.
