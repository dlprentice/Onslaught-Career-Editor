# Frontend Clear-Screen Color Patch

Status: cataloged copied-executable color preset family; red, green, and black each have title-screen plus one navigated-menu visual proof
Date: 2026-06-16

This note records the bounded evidence for the WinUI Windowed & Mods frontend clear-screen color presets. These patches change one DirectX frontend clear-screen color immediate in a copied `BEA.exe`. Only one color preset can be selected at a time because all presets patch the same file offset.

## Evidence

| Item | Value |
| --- | --- |
| Retail function | `0x00540f70 CDXFrontEnd__RenderStart` |
| Source anchor | `references/Onslaught/DXFrontend.cpp`, `CDXFrontEnd::RenderStart()` |
| Source behavior | `PLATFORM.ClearScreen(0x001f1f3f)` before forwarding to `CFrontEnd::RenderStart()` |
| File offset | `0x140F88` |
| VA | `0x00540F88` |
| Original bytes | `3F 1F 1F 00` (`0x001f1f3f`) |
| Dark red patched bytes | `1F 1F BF 00` (`0x00bf1f1f`) |
| Dark green patched bytes | `1F BF 1F 00` (`0x001fbf1f`) |
| Black patched bytes | `00 00 00 00` (`0x00000000`) |

The clean local `BEA.exe.original.backup` read-back at file offset `0x140F88` matched `3F 1F 1F 00`. Existing Ghidra/docs evidence identifies `0x00540f70` as `CDXFrontEnd__RenderStart`, reached by `CFrontEnd__Render`, resetting render state, clearing the screen, enabling render state `0x1b`, and forwarding into `CFrontEnd__RenderStart`.

Cataloged preset rows:

| Patch id | Runtime visual proof |
| --- | --- |
| `frontend_clear_screen_dark_red` | One local copied-game title-screen capture showed red clear-screen margins, and one later navigated Goodies-menu run showed red-family margins after scoped input. |
| `frontend_clear_screen_dark_green` | One local copied-game title-screen capture showed green clear-screen margins, and one later navigated Goodies-menu run showed green-family margins after scoped input. |
| `frontend_clear_screen_black` | One local copied-game title-screen capture showed black clear-screen margins, and one later navigated Goodies-menu run showed black-family margins after scoped input. |

WinUI Windowed & Mods exposes these rows both in the normal patch list and through Title-screen margin color quick picks: Red margins, Green margins, Black margins, and Clear margin color. The quick picks only select or clear the same mutually exclusive rows; they do not add a new patch format, a resource/theme system, or additional runtime proof.

Two early armed local safe-copy smokes on 2026-06-17 selected this patch with the windowed compatibility rows, launched a real copied `BEA.exe`, captured one exact process/window frame, stopped the managed process, and verified installed/source hashes were unchanged. The ignored proof summaries are `subagents/winui-safe-copy-live-runtime/20260617-040037/live-safe-copy-runtime-smoke.json` and `subagents/winui-safe-copy-live-runtime/20260617-040706/live-safe-copy-runtime-smoke.json`. Both captures showed the loading screen, so they proved safe copied launch/capture/stop with the patch selected, not visible red frontend/menu output.

A later armed local safe-copy smoke on 2026-06-17 used the multi-capture helper, selected `frontend_clear_screen_dark_red` with `resolution_gate` and `force_windowed`, launched a real copied `BEA.exe`, captured four exact process/window frames, stopped the managed process, and verified installed/source hashes were unchanged. The ignored proof summary is `subagents/winui-safe-copy-live-runtime/20260617-060348/live-safe-copy-runtime-smoke.json`. Frame 4 (`capture/safe-copy-frame-04.png`) reached the BEA title screen and showed red clear-screen margins, proving this copied-executable row can produce the expected visible frontend clear color in that local safe-copy run.

Two later armed local safe-copy smokes on 2026-06-17 selected `frontend_clear_screen_dark_green` and `frontend_clear_screen_black` separately with `resolution_gate` and `force_windowed`, launched real copied `BEA.exe` processes, captured five exact process/window frames each, stopped the managed processes, and verified installed/source executable and source save/options hashes were unchanged. The ignored proof summaries are `subagents/winui-safe-copy-live-runtime/20260617-112839/live-safe-copy-runtime-smoke.json` and `subagents/winui-safe-copy-live-runtime/20260617-113005/live-safe-copy-runtime-smoke.json`. In both runs, frame 5 (`capture/safe-copy-frame-05.png`) reached the BEA title screen and showed the selected green or black clear-screen margins.

An armed local safe-copy smoke on 2026-06-18 selected `frontend_clear_screen_dark_red` with `resolution_gate` and `force_windowed`, launched a real copied `BEA.exe`, focused the managed window, sent three scoped input sequences with 22 total actions, captured five exact process/window frames, stopped the managed process, and verified installed/source executable, clean override executable, source `defaultoptions.bea`, and source `savegames` hashes were unchanged. The ignored proof summary is `subagents/winui-safe-copy-live-runtime/frontend-color-red-menu-20260618-focus1/live-safe-copy-runtime-smoke.json`. `tools/winui_frontend_color_runtime_artifact_check.py` accepted the artifact with `captureCount=5`, `visualCaptureCount=5`, `matchingColorCaptureCount=5`, and `afterInputColorCaptureCount=3`. The title/pre-input frame matched the red immediate nearly exactly in the sampled margins; navigated frames were shaded by frontend rendering but retained dominant red-family margin pixels. `capture/safe-copy-after-input-03-frame.png` reached the Goodies menu, showing a red-margin frontend state beyond the title screen.

Two later armed local safe-copy smokes on 2026-06-18 repeated the same navigated Goodies-menu path for `frontend_clear_screen_dark_green` and `frontend_clear_screen_black` with `resolution_gate` and `force_windowed`. Each run launched a real copied `BEA.exe`, focused the managed window, sent three scoped input sequences with 22 total actions, captured five exact process/window frames, stopped the managed process, and verified installed/source executable, clean override executable, source `defaultoptions.bea`, and source `savegames` hashes were unchanged. The ignored proof summaries are `subagents/winui-safe-copy-live-runtime/frontend-color-green-menu-20260618-focus1/live-safe-copy-runtime-smoke.json` and `subagents/winui-safe-copy-live-runtime/frontend-color-black-menu-20260618-focus1/live-safe-copy-runtime-smoke.json`. `tools/winui_frontend_color_runtime_artifact_check.py` accepted each artifact with `captureCount=5`, `visualCaptureCount=5`, `matchingColorCaptureCount=5`, and `afterInputColorCaptureCount=3`. The representative `capture/safe-copy-after-input-03-frame.png` frames reached the Goodies menu with the selected green-family or black-family frontend margins.

## Boundary

This is a small executable color preset, not a menu-theme system. It should affect the frontend clear-screen background color path only. It does not replace textures, menu art, fonts, HUD colors, mission UI, or gameplay rendering colors.

Broader menu-state screenshots and repeat target-machine checks are still required before claiming every frontend/menu state uses a selected clear-screen color. The patch family remains copied-profile/app-owned only; the installed game and original executable must stay unchanged.
