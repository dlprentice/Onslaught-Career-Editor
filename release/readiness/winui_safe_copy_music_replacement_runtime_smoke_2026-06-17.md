# WinUI Safe-Copy Music Replacement Runtime Smoke Readiness Note

Status: validated bounded live launch/capture/stop smoke with staged copied music replacement
Date: 2026-06-17

Scope: prove that a generated safe copied game folder can stage one copied `.ogg` replacement, launch the copied `BEA.exe`, capture one exact process/window frame, and stop the managed process without mutating the installed game, clean executable backup, source target track, or source replacement track.

This smoke used the app-owned copied-game path. The copied executable received `resolution_gate` and `force_windowed`; the generated safe-copy music lane staged shipped `BEA_02(Master).ogg` over the copied `data/Music/BEA_01(Master).ogg`, keeping the original copied track backup beside it. The launch used `-skipfmv`.

Measured evidence:

| Area | Result |
| --- | --- |
| Tool | `tools/winui_safe_copy_live_runtime_smoke.py --stage-music-replacement --arm-live-bea "LAUNCH SAFE COPY BEA" --timeout-seconds 15` |
| Artifact | `subagents/winui-safe-copy-live-runtime/20260617-023348/live-safe-copy-runtime-smoke.json` |
| Captured frame | `subagents/winui-safe-copy-live-runtime/20260617-023348/capture/safe-copy-frame.png` |
| Copied game root | Local app-owned runtime proof root outside the repo; exact private path redacted from public-safe docs. |
| Source executable override | `BEA.exe.original.backup` |
| Installed `BEA.exe` hash before/after | Local non-clean installed hash unchanged; exact local hash kept in ignored proof artifact. |
| Clean backup hash before/after | canonical clean Steam hash unchanged. |
| Patch keys | `resolution_gate`, `force_windowed` |
| Music source files | Source target and source replacement hashes unchanged; exact local hashes kept in ignored proof artifact. |
| Staged copied target | Copied `BEA_01(Master).ogg` now matches copied replacement bytes; copied backup matches original target bytes. |
| Launch observation | process id observed alive, main window handle observed, not exited before stop. |
| Capture observation | `game-window-capture-helper.v1`, status `captured`, exact process/window target, bounds `656x539`, output PNG `533921` bytes. |
| Stop observation | managed safe game copy process stopped; no `BEA` process remained after stop. |

Claim boundary:

- Proves safe-copy preparation, copied-executable patching, copied music-file replacement staging, source file non-mutation, live process launch observation, main-window-handle observation, one exact process/window frame capture, managed stop, and no leftover BEA process for this local run.
- Does not prove BEA decoded the replacement OGG, selected that track, played audible music, reached a menu/gameplay state beyond the captured loading-window frame, rendered correctly, applied color/resource replacement, or achieved rebuild/no-noticeable-difference parity.
- Does not mutate the installed game folder, installed `BEA.exe`, clean executable backup, source music target, or source replacement file.

Validation:

- Armed live smoke completed with exit code `0`.
- Music replacement manifest in the copied game root records package-relative paths and no absolute source paths.
- Capture helper wrote `game-window-capture-helper.v1` JSON plus a bounded still-frame PNG for the exact process id/window handle.
- `Get-Process` confirmed no `BEA` process remained after managed stop.

Next bounded proof:

- Superseded next-step status: UI-visible launch modifiers for safe copied game folders now exist and are allowlisted in AppCore.
- For actual audio proof, observe runtime audio selection/decode/playback separately rather than inferring it from copied file layout.
- Investigate the first frontend color/background mod path only after identifying a copied-target asset/byte path and a screenshotable success condition.
