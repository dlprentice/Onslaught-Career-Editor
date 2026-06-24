# WinUI Safe-Copy Music Swap Level-100 Decode Proof

Status: complete bounded runtime proof
Date: 2026-06-19
Scope: `use-bea02-for-bea04` safe-copy shipped-track preset

This slice adds and validates the named shipped-track preset `use-bea02-for-bea04`, which stages copied `BEA_02(Master).ogg` bytes over copied `BEA_04(Master).ogg` in the generated safe-copy game folder only.

Fresh live proof:

| Field | Value |
| --- | --- |
| Preset | `use-bea02-for-bea04` |
| Target | `BEA_04(Master).ogg` |
| Replacement | `BEA_02(Master).ogg` |
| Level | `100` |
| CMusic selection | `2` |
| Capture count | `2` |
| Visual capture count | `2` |
| Async music kick count | `1` |
| Ogg open count | `1` |
| Ogg read count | `1` |
| Max decode request | `524288` |

The proof used `BEA.exe.original.backup` as the clean executable source; the backup matched the canonical Steam retail SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` before launch. The installed Steam executable, clean executable override, source music tracks, source saves/options, and source game folder remained unchanged. The generated copied game folder received only the safe-copy windowed patch pair and the copied music staging mutation.

Validation:

```powershell
npm run test:winui-safe-copy-music-swap-presets
npm run test:winui-safe-copy-music-swap-runtime-artifact-checker
npm run test:winui-safe-copy-music-selection-decode-artifact
npm run test:winui-safe-copy-music-swap-level100-decode-proof
npm run test:winui-safe-copy-live-runtime-smoke-helper
py -3 tools\winui_safe_copy_music_swap_level100_decode_proof_check.py <fresh private artifact>
py -3 tools\winui_safe_copy_music_swap_preset_artifact_check.py <fresh private artifact> --expected-preset-id use-bea02-for-bea04 --min-capture-count 2
py -3 tools\winui_safe_copy_music_selection_decode_artifact_check.py <fresh private artifact> --expected-target "BEA_04(Master).ogg" --expected-replacement "BEA_02(Master).ogg" --expected-level 100 --expected-selection 2 --min-capture-count 2 --require-ogg-decode
```

Claim boundary:

- Proves the named safe-copy shipped-track preset can stage `BEA_02(Master).ogg` over copied `BEA_04(Master).ogg`, launch a copied level-100 game, and observe the staged `BEA_04` path reaching async music stream kick plus Ogg open/read decode.
- Does not prove audible playback, loop behavior, volume, mixing, crossfade, all music cues, arbitrary external OGG compatibility, gameplay parity, rebuild parity, or no-noticeable-difference parity.
- Does not patch or mutate the installed Steam game folder or original executable.
