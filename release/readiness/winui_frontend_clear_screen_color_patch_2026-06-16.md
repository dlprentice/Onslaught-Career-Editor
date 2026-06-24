# WinUI Frontend Clear-Screen Color Patch Readiness Note

Status: catalog/UI wiring complete, launch/capture/stop proof and title-screen plus navigated-menu visual proof added for red, green, and black
Date: 2026-06-16

Scope: add the mutually exclusive `frontend_clear_screen_dark_red`, `frontend_clear_screen_dark_green`, and `frontend_clear_screen_black` opt-in copied-executable patches in WinUI Windowed & Mods.

Tracked outcomes:

| Area | Result |
| --- | --- |
| Source/static evidence | Stuart source `references/Onslaught/DXFrontend.cpp` shows `CDXFrontEnd::RenderStart()` calling `PLATFORM.ClearScreen(0x001f1f3f)`; existing Ghidra docs identify retail `0x00540f70 CDXFrontEnd__RenderStart` as the clear-screen frontend render-start path. |
| Byte evidence | Clean local `BEA.exe.original.backup` read-back at file offset `0x140F88` matched original bytes `3F 1F 1F 00`. |
| Catalog rows | `patches/catalog/patches.v2.json` adds `frontend_clear_screen_dark_red`, `frontend_clear_screen_dark_green`, and `frontend_clear_screen_black` with original bytes `3F 1F 1F 00`, patched bytes `1F 1F BF 00`, `1F BF 1F 00`, and `00 00 00 00`, target SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, and target size `2506752`. |
| Product boundary | The rows are visible alternatives, not layers, and are not part of the Windowed + graphics defaults preset. They patch copied/app-owned `BEA.exe` targets only and do not replace textures, menu art, fonts, HUD colors, or gameplay rendering colors. |
| WinUI quick picks | Windowed & Mods now has Title-screen margin color quick picks for Red margins, Green margins, Black margins, and Clear margin color. These buttons select or clear the same existing mutually exclusive catalog rows; they do not add new patch bytes or stronger runtime claims. |
| Test gate | Patch regression tests assert catalog/spec identity, offset, exact bytes, and mutual exclusion. WinUI source tests assert visible group/model wording and runtime-proof boundary text. |
| Live safe-copy smoke | Two early armed local runs on 2026-06-17 selected `frontend_clear_screen_dark_red` with `resolution_gate` and `force_windowed`, launched a real copied `BEA.exe`, captured one exact process/window frame, stopped the managed process, and verified installed/source hashes were unchanged. Ignored proof summaries: `subagents/winui-safe-copy-live-runtime/20260617-040037/live-safe-copy-runtime-smoke.json` and `subagents/winui-safe-copy-live-runtime/20260617-040706/live-safe-copy-runtime-smoke.json`. A later armed local red run used the multi-capture helper, captured four exact process/window frames, and reached the BEA title screen with red clear-screen margins in frame 4. Ignored proof summary: `subagents/winui-safe-copy-live-runtime/20260617-060348/live-safe-copy-runtime-smoke.json`; visible frame: `capture/safe-copy-frame-04.png`. Later green and black runs used the same safe-copy path, captured five frames each, verified installed/source executable and source save/options hashes unchanged, and reached the BEA title screen with green or black clear-screen margins in frame 5. Ignored proof summaries: `subagents/winui-safe-copy-live-runtime/20260617-112839/live-safe-copy-runtime-smoke.json` and `subagents/winui-safe-copy-live-runtime/20260617-113005/live-safe-copy-runtime-smoke.json`; visible frames: `capture/safe-copy-frame-05.png` in each run. |
| Navigated-menu smokes | Three armed local runs on 2026-06-18 selected `frontend_clear_screen_dark_red`, `frontend_clear_screen_dark_green`, and `frontend_clear_screen_black` separately with `resolution_gate` and `force_windowed`, launched real copied `BEA.exe` processes, focused the managed windows, sent three scoped input sequences with 22 actions per run, captured five exact process/window frames per run including three after-input frames, stopped the managed processes, and verified installed/source executable, clean override executable, source `defaultoptions.bea`, and source `savegames` hashes unchanged. `tools/winui_frontend_color_runtime_artifact_check.py` accepted each artifact with `captureCount=5`, `visualCaptureCount=5`, `matchingColorCaptureCount=5`, and `afterInputColorCaptureCount=3`. The proof summaries are ignored/private at `subagents/winui-safe-copy-live-runtime/frontend-color-red-menu-20260618-focus1/live-safe-copy-runtime-smoke.json`, `subagents/winui-safe-copy-live-runtime/frontend-color-green-menu-20260618-focus1/live-safe-copy-runtime-smoke.json`, and `subagents/winui-safe-copy-live-runtime/frontend-color-black-menu-20260618-focus1/live-safe-copy-runtime-smoke.json`; representative navigated frames `capture/safe-copy-after-input-03-frame.png` reached the Goodies menu with the selected color-family margins. |

Not claimed:

- No claim that every frontend/menu state uses the selected color on every target setup.
- No broader menu-navigation proof beyond one captured Goodies-menu path per color preset.
- No full menu-theme system.
- No texture/resource replacement.
- No installed-game or original executable mutation.
- No Ghidra mutation.
- No new Ghidra backup; latest verified Ghidra review backup remains `G:\GhidraBackups\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified`.
