# WinUI Modern Graphics Live Runtime Smoke Readiness Note

Status: validated bounded live launch/capture/stop smoke
Date: 2026-06-17

Scope: prove the guarded safe-copy runtime lane can apply the stable modern-graphics patch rows to a copied `BEA.exe`, launch that copied executable, capture one exact process/window frame, and stop the managed process without mutating the installed game or original executable.

This smoke used the app-owned copied-game path rather than patching the Steam install. The local installed `BEA.exe` was non-clean, so the smoke used `BEA.exe.original.backup` as the clean executable source and copied it into the generated safe game folder as `BEA.exe`. The copied executable received the baseline windowed rows plus the stable modern-graphics rows, then launched with `-skipfmv` from the copied working directory.

Measured evidence:

| Area | Result |
| --- | --- |
| Tool | `tools/winui_safe_copy_live_runtime_smoke.py --include-modern-graphics --arm-live-bea "LAUNCH SAFE COPY BEA" --timeout-seconds 15` |
| Artifact | `subagents/winui-safe-copy-live-runtime/20260617-021941/live-safe-copy-runtime-smoke.json` |
| Captured frame | `subagents/winui-safe-copy-live-runtime/20260617-021941/capture/safe-copy-frame.png` |
| Copied game root | Local app-owned runtime proof root outside the repo; exact private path redacted from public-safe docs. |
| Source executable override | `BEA.exe.original.backup` |
| Installed `BEA.exe` hash before/after | Local non-clean installed hash unchanged; exact local hash kept in ignored proof artifact. |
| Clean backup hash before/after | `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` / unchanged |
| Patch keys | `resolution_gate`, `force_windowed`, `extra_graphics_default_on`, `ignore_cardid_tweak_overrides` |
| Manifest patch state | `requested=true`, `success=true` |
| Launch observation | process id `46496`, observed alive, main window handle `0x480b58`, not exited before stop |
| Capture observation | `game-window-capture-helper.v1`, status `captured`, exact process/window target, bounds `656x539`, output PNG `533711` bytes |
| Stop observation | managed safe game copy process stopped; process no longer alive after stop |

Claim boundary:

- Proves safe-copy preparation, copied-executable patching for the two stable modern-graphics rows, live process launch observation, main-window-handle observation, one exact process/window frame capture, managed stop, and unchanged installed-source hashes for this local run.
- Does not prove menu reach beyond the captured loading-window frame, rendering correctness, graphics-feature visual effect, gameplay behavior, music playback, color/resource replacement, crash-free long session behavior, rebuild parity, or no-noticeable-difference parity.
- Does not mutate installed `C:\Program Files (x86)\Steam\steamapps\common\Battle Engine Aquila\BEA.exe` or `BEA.exe.original.backup`.

Validation:

- Armed live smoke completed with exit code `0`.
- Manifest exists in the copied game root and reports `patchRequested=true`, `patchSuccess=true`, patch keys `resolution_gate,force_windowed,extra_graphics_default_on,ignore_cardid_tweak_overrides`, and launch argument `-skipfmv`.
- Capture helper wrote `game-window-capture-helper.v1` JSON plus a bounded still-frame PNG for the exact process id/window handle.
- `Get-Process` confirmed no `BEA` process remained after managed stop.
- Help/refusal checks for the tool passed before the armed run.

Next bounded proof:

- Promote safe-copy music replacement from staging to runtime proof only after a copied safe-game run shows the staged file can be decoded or selected.
- Investigate the first frontend color/background mod path as a copied-target proof before exposing it as a player-facing option.
