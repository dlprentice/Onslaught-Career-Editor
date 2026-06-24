# WinUI Frontend Color Navigated Runtime Proof

Status: red, green, and black copied-game navigated-menu proofs accepted
Date: 2026-06-18

Scope: validate that the copied-executable frontend clear-screen color rows can survive real frontend navigation beyond the title screen in the safe-copy runtime harness.

Tracked outcome:

| Patch row | Runtime artifact | Checker result | Visual state |
| --- | --- | --- | --- |
| `frontend_clear_screen_dark_red` | `subagents/winui-safe-copy-live-runtime/frontend-color-red-menu-20260618-focus1/live-safe-copy-runtime-smoke.json` | `captureCount=5`, `visualCaptureCount=5`, `matchingColorCaptureCount=5`, `afterInputColorCaptureCount=3` | Representative after-input frame reached the Goodies menu with red-family margins. |
| `frontend_clear_screen_dark_green` | `subagents/winui-safe-copy-live-runtime/frontend-color-green-menu-20260618-focus1/live-safe-copy-runtime-smoke.json` | `captureCount=5`, `visualCaptureCount=5`, `matchingColorCaptureCount=5`, `afterInputColorCaptureCount=3` | Representative after-input frame reached the Goodies menu with green-family margins. |
| `frontend_clear_screen_black` | `subagents/winui-safe-copy-live-runtime/frontend-color-black-menu-20260618-focus1/live-safe-copy-runtime-smoke.json` | `captureCount=5`, `visualCaptureCount=5`, `matchingColorCaptureCount=5`, `afterInputColorCaptureCount=3` | Representative after-input frame reached the Goodies menu with black-family margins. |

For each row, the harness applied `resolution_gate`, `force_windowed`, and exactly one frontend color patch to the copied executable only; focused the managed copied `BEA.exe`; sent `3` scoped input sequences with `22` actions; captured `5` exact process/window frames; stopped the managed process; and verified installed/source executable, clean override executable, source `defaultoptions.bea`, and source `savegames` hashes stayed unchanged. No BEA process remained after managed stop.

Not claimed:

- No installed-game or original executable mutation.
- No full frontend theme system.
- No claim that every frontend/menu state on every target setup uses the selected clear-screen color.
- No texture replacement, menu art replacement, HUD color replacement, gameplay rendering color proof, visual parity, rebuild parity, or no-noticeable-difference proof.
- No Ghidra mutation or Ghidra backup; latest verified Ghidra review backup remains `G:\GhidraBackups\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified`.
