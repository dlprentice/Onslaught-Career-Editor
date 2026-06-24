# Lane 06 - Python GUI/CLI/Core Parity Audit

Date: 2026-03-05
Scope: Python GUI/CLI/core parity against the active C# app and canonical docs for active features only (`Save Editor`, `Save Analyzer`, `Configuration Editor`, `Binary Patches`, `Lore Browser`, `Media`, `Settings`, CLI/core semantics).

## Overall Assessment

- No high-severity Python core/save-format drift was found in the active feature set. The Python CLI flag surface and save/options semantics still line up with the C# CLI/core and canonical save docs (`Program.cs:101`, `patcher.py:1609`, `reverse-engineering/save-file/save-format.md:290`).
- The remaining issues are medium/low severity: Python GUI UX still lags behind the current WPF lane in a few places, one real shell-state parity gap remains, and PyQt regression coverage is still thin around the real action paths.

## Findings

### 1. Medium - Python Save Editor / Configuration Editor UX still lags behind the current WPF lane, but parity docs still read as closed

Python still uses raw text-entry affordances for the two areas WPF already hardened most:
- per-mission rank overrides are still a single freeform field (`1:S,2:A`) in `onslaught/gui/tabs/save_editor.py:183`
- per-category kill overrides are still plain line edits in `onslaught/gui/tabs/save_editor.py:190`

WPF now exposes the safer/friendlier surface the repo has been converging toward:
- explicit `Quick Unlock` / `Safe Edit` preset chooser in `Views/SaveEditorView.xaml:213`
- per-mission grid with `Node`, `Mission`, `Current Rank`, and `Rank Override` in `Views/SaveEditorView.xaml:284` and `Views/SaveEditorView.xaml:325`
- slider + textbox hybrid per-category overrides in `Views/SaveEditorView.xaml:348`
- explicit configuration-mode banner in `Views/SaveEditorView.xaml:26`

The parity roadmap still marks `Save Editor` as `COMPLETE` without calling out this remaining UX divergence: `roadmap/csharp-python-parity.md:15` and `roadmap/csharp-python-parity.md:90`.

Impact:
- Functional parity exists, but the Python lane still gives users more rope than the WPF lane and no longer matches the repo's current user-guidance direction.

### 2. Medium - Python shell does not persist nested Save/Media subtabs, unlike the current C# app

Current WPF persists both top-level and nested tab state:
- config schema includes `lastSaveSubTab` / `lastMediaSubTab` in `AppConfig.cs:63` and `AppConfig.cs:66`
- restore path uses them in `MainWindow.xaml.cs:38` and `MainWindow.xaml.cs:43`
- change handlers save them in `MainWindow.xaml.cs:128` and `MainWindow.xaml.cs:132`

Python only persists the top-level tab:
- config schema stops at `last_tab` in `onslaught/core/config.py:75` and `onslaught/core/config.py:105`
- restore logic only reapplies `last_tab` in `onslaught/gui/main_window.py:242`
- nested tab changes update status only; they do not persist subtab indexes in `onslaught/gui/main_window.py:327`
- close/save path writes only `last_tab` in `onslaught/gui/main_window.py:380`

Impact:
- After reopen, PyQt drops users back to the default nested subtab even though WPF preserves `Save Analyzer` / `Configuration Editor` and `Audio` / `Video` positions.
- This is a real active-surface parity gap, not just wording drift.

### 3. Medium - PyQt regression coverage does not exercise the real GUI Analyze/Patch action paths that import `patcher.py` at runtime

Two important GUI actions still depend on runtime imports from `patcher.py`:
- Save Analyzer imports `analyze_file` during the button path in `onslaught/gui/tabs/save_analyzer.py:390`
- Save Editor imports `patch_file` and related patch symbols during the patch path in `onslaught/gui/tabs/save_editor.py:1129` and `onslaught/gui/tabs/save_editor.py:1220`

Current Python tests do not cover those actual GUI action paths:
- `tests_pyqt/test_smoke.py:17` only covers shell presence and simple routing helpers
- `tests_pyqt/test_save_editor_defaults_unittest.py:1` covers defaults / enable-disable behavior, not actual patch execution
- CLI/core tests validate `patcher.py` directly, but not the PyQt button wiring

Impact:
- A refactor in `patcher.py` can break the Python GUI's Analyze/Patch buttons without tripping the current PyQt suite.

### 4. Medium - Python Binary Patches GUI contract is still untested even though the core engine is covered

The Python Binary Patches tab has real UI contract logic around:
- verify-before-apply gating in `onslaught/gui/tabs/binary_patches.py:279`
- selection validation / experimental-only rejection in `onslaught/gui/tabs/binary_patches.py:232`
- restore flow in `onslaught/gui/tabs/binary_patches.py:341`

But Python tests only cover the core patch engine, not the GUI tab behavior:
- `tests_pyqt/test_binary_patches_unittest.py:6` validates core apply/restore/report helpers only
- `tests_pyqt/test_smoke.py:17` only confirms the tab exists

Impact:
- The critical GUI safety contract for `Verify Selected -> Apply Selected -> Restore Backup` is not regression-tested on the Python side.

### 5. Low - Python Binary Patches tab wording still understates the current executable-patch model

Python still frames the tab as display/windowed-only:
- group title `Display / Windowed Patches (Stable + Experimental)` in `onslaught/gui/tabs/binary_patches.py:105`
- generic backup note in `onslaught/gui/tabs/binary_patches.py:166`

That now lags the current WPF and release wording:
- WPF uses `Executable Patches (Stable + Experimental)` in `Views/BinaryPatchesView.xaml:52`
- WPF explicitly calls out extra-graphics/cardid coverage and the version watermark in `Views/BinaryPatchesView.xaml:64` and `Views/BinaryPatchesView.xaml:149`
- root README describes the stable patch set as widescreen + windowed + extra-graphics + cardid bypass in `README.MD:65`

Impact:
- No functional drift, but Python UI wording understates what the selected stable set actually does.

### 6. Low - Python Settings wording omits Binary Patches as a consumer of the configured game directory

Python settings copy currently says the game directory is used by `Audio Player, Video Player, and Save tools` in `onslaught/gui/tabs/settings.py:35`.

Current WPF/settings wording and release docs explicitly include binary patching:
- `Views/SettingsView.xaml:22` and `Views/SettingsView.xaml:29`
- `README.MD:65`

Impact:
- Visible wording drift only, but it is now inaccurate.

### 7. Low - Python Save Analyzer wording is still on the older terminology pass

Python still uses older labels:
- `Re-Analyze` button in `onslaught/gui/tabs/save_analyzer.py:62`
- `Dump Reserved/Unmapped Bytes` checkbox in `onslaught/gui/tabs/save_analyzer.py:79`

WPF has already moved to the newer wording and helper copy:
- `Analyze Again` in `Views/SaveAnalyzerView.xaml:84`
- `Raw reserved-byte dump (advanced)` in `Views/SaveAnalyzerView.xaml:108`
- auto-analysis explanation in `Views/SaveAnalyzerView.xaml:94`

Impact:
- Minor UX wording drift; behavior is aligned, copy is not.

### 8. Low - `roadmap/csharp-python-parity.md` is stale on Python video backend wording and overstates closure

The parity doc still describes Python video as `FFmpeg conversion if playback fails` versus C# `Uses VLC` in `roadmap/csharp-python-parity.md:31` and `roadmap/csharp-python-parity.md:38`.

Current code is more specific:
- Python uses `PyQt6.QtMultimedia` / `QVideoWidget` with optional ffmpeg conversion fallback in `onslaught/gui/tabs/video_player.py:26`, `onslaught/gui/tabs/video_player.py:137`, and `onslaught/gui/tabs/video_player.py:509`
- WPF uses LibVLC directly in `Views/VideoPlayerView.xaml:6`

The same doc also still treats multiple lanes as fully closed even though the active Python gaps above remain: `roadmap/csharp-python-parity.md:15`, `roadmap/csharp-python-parity.md:18`, and `roadmap/csharp-python-parity.md:19`.

Impact:
- Documentation drift only, but it matters because backend/runtime dependency expectations differ by stack and the parity status is too optimistic.

### 9. Low/Medium - Lore Browser remains under-tested on the Python side relative to its shipped surface

The Python lore browser has meaningful behavior around:
- lazy first-load in `onslaught/gui/tabs/lore_browser.py:45`
- threaded loading in `onslaught/gui/tabs/lore_browser.py:152`
- relative/external link routing in `onslaught/gui/tabs/lore_browser.py:284`
- search/filtering in `onslaught/gui/tabs/lore_browser.py:360`

The parity doc marks the lane complete in `roadmap/csharp-python-parity.md:14`, but there is no PyQt test that actually exercises lore load/search/link behavior; `tests_pyqt/test_smoke.py:17` stops at shell-level presence/routing.

Impact:
- Low immediate risk, but it is a real blind spot because Lore Browser is an active shipping tab and its behavior depends on filesystem markdown/link structure.

## No High-Severity Functional Drift Found

These areas looked aligned in this pass:
- CLI flag surface and save/options semantics: `Program.cs:101`, `patcher.py:1609`
- `.bes` vs `.bea` boot/runtime semantics reflected in both stacks and canonical docs: `BesFilePatcher.cs:1582`, `patcher.py:1160`, `reverse-engineering/save-file/save-format.md:290`
- Binary patch core catalog usage in Python includes the version watermark companion patches and the extra-graphics/cardid stable set: `onslaught/core/binary_patches.py:61`, `onslaught/gui/tabs/binary_patches.py:43`, and `onslaught/gui/tabs/binary_patches.py:210`

## Recommended Follow-Up Order

1. Update Python Save Editor UX to match the current WPF mission-rank / kill-override safety improvements.
2. Add nested Save/Media subtab persistence to Python config + main window.
3. Add PyQt regression coverage for Save Analyzer action import path, Save Editor patch action, Binary Patches tab contract, and Lore Browser interactions.
4. Sync Python Binary Patches / Settings / Save Analyzer wording to the current WPF and release language.
5. Refresh `roadmap/csharp-python-parity.md` so it reflects current real divergences instead of closed historical state.
