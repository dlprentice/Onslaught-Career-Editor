# WinUI Safe-Copy Live Runtime Smoke Readiness Note

Status: validated bounded live launch/capture/stop smoke
Date: 2026-06-17

Scope: prove the guarded copied-game runtime lane can launch a real copied `BEA.exe`, capture one bounded screen-region frame at verified target-window bounds, and stop the managed process without mutating the installed game or original executable.

This smoke used the app-owned copied-game path rather than patching the Steam install. The local installed `BEA.exe` was non-clean, so the smoke used `BEA.exe.original.backup` as the clean executable source and copied it into the generated playable copied game folder as `BEA.exe`. The copied executable received only `resolution_gate` and `force_windowed`, then launched with `-skipfmv` from the copied working directory.

Measured evidence:

| Area | Result |
| --- | --- |
| Tool | `tools/winui_safe_copy_live_runtime_smoke.py --arm-live-bea "LAUNCH SAFE COPY BEA" --timeout-seconds 15` |
| Artifact | `subagents/winui-safe-copy-live-runtime/20260617-021055/live-safe-copy-runtime-smoke.json` |
| Captured frame | `subagents/winui-safe-copy-live-runtime/20260617-021055/capture/safe-copy-frame.png` |
| Copied game root | Local app-owned runtime proof root outside the repo; exact private path redacted from public-safe docs. |
| Source executable override | `BEA.exe.original.backup` |
| Installed `BEA.exe` hash before/after | Local non-clean installed hash unchanged; exact local hash kept in ignored proof artifact. |
| Clean backup hash before/after | `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` / unchanged |
| Patch keys | `resolution_gate`, `force_windowed` |
| Manifest patch state | `requested=true`, `success=true` |
| Launch observation | process id `51580`, observed alive, main window handle `0x370766`, not exited before stop |
| Capture observation | `game-window-capture-helper.v1`, status `captured`, verified process/window target bounds `656x539`, output PNG `533686` bytes |
| Stop observation | managed copied game process stopped; process no longer alive after stop |

Claim boundary:

- Proves copied-game preparation, copied-executable patching, live process launch observation, main-window-handle observation, one bounded screen-region capture at verified target bounds, managed stop, and unchanged installed-source hashes for this local run.
- Does not prove menu reach beyond the captured loading-window frame, rendering correctness, gameplay behavior, music playback, color/resource replacement, crash-free long session behavior, rebuild parity, or no-noticeable-difference parity.
- The capture helper records foreground-window metadata, but this note does not claim unoccluded pixels unless a focused visual review separately verifies the frame.
- Does not mutate installed `C:\Program Files (x86)\Steam\steamapps\common\Battle Engine Aquila\BEA.exe` or `BEA.exe.original.backup`.

Validation:

- Armed live smoke completed with exit code `0`.
- Manifest exists in the copied game root and reports `patchRequested=true`, `patchSuccess=true`, patch keys `resolution_gate,force_windowed`, and launch argument `-skipfmv`.
- Capture helper wrote `game-window-capture-helper.v1` JSON plus a bounded screen-region PNG for the verified process id/window handle bounds.
- `Get-Process` confirmed the launched process id was no longer alive after managed stop.
- Help/refusal checks for the tool passed before the armed run.

Next bounded proof:

- Superseded next-step status: the modern-graphics and staged-music copied-game launch/capture/stop smokes now exist as separate June 17 notes.
- Next useful proofs are menu/window reach, stayed-windowed behavior, runtime audio selection/decode/playback, and the first frontend color/background copied-target proof.
- Keep gameplay, rendering correctness, and rebuild claims separate until each has its own copied-target proof.
