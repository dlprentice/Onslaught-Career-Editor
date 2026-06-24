## Summary
The Python app is a filesystem-first toolkit with two entry points: a monolithic CLI engine (`patcher.py`) and a PyQt6 GUI shell (`onslaught_explorer.py`) that composes tab modules.

Architecture is mostly 3-layer:
- Entry/UI: CLI argument router + GUI `MainWindow`.
- Domain/core: constants, BES parser/stats model, config discovery/persistence, binary EXE patch primitives.
- Data/filesystem: `.bes/.bea` binaries, `BEA.exe`, JSON config, media folders, and cache/backup files.

The strongest coupling is that GUI patch/analyze actions import and execute functions directly from `patcher.py` (`onslaught/gui/tabs/save_editor.py:1093`, `onslaught/gui/tabs/save_analyzer.py:381`), including `sys.path` mutation.

## File Map
### Entry Points
- `patcher.py:1584`
  - CLI command surface for patch/analyze/compare/goodie-list/config management.
  - Core mutation/read flows live in same file (`patch_file` at `patcher.py:580`, `analyze_file` at `patcher.py:1084`, `compare_files` at `patcher.py:934`, `list_goodies` at `patcher.py:1514`).
- `onslaught_explorer.py:17`
  - GUI bootstrap, applies Qt theme, constructs `MainWindow`, optional startup file load.

### Core Package (`onslaught/core`)
- `onslaught/core/constants.py`
  - Canonical layout offsets/counts/rank bits and app metadata.
- `onslaught/core/bes_file.py:90`
  - Structured parser/model (`BesFile`) with stats projection for analyzer/tree UI.
- `onslaught/core/config.py:96`
  - `AppConfig` dataclass + JSON persistence + game dir detection/save discovery.
- `onslaught/core/binary_patches.py:103`
  - Byte-verified `BEA.exe` patch/restore primitives, plus backup path policy.

### GUI Shell
- `onslaught/gui/main_window.py:26`
  - Top-level tab host and cross-tab policies (media overlap/background behavior, status/footer, menu actions).
  - Active top-level tabs: Saves, Media, Lore, Binary Patches, Settings (`onslaught/gui/main_window.py:84-111`).

### GUI Tabs (Mounted)
- `onslaught/gui/tabs/save_editor.py:24`
  - Patch UI for `.bes`; reused in configuration-only mode for `.bea` (`configuration_only=True`).
- `onslaught/gui/tabs/save_analyzer.py:21`
  - Analyze + compare UI for `.bes/.bea`.
- `onslaught/gui/tabs/audio_player.py:29`
  - OGG/WAV browser/player with game-dir integration.
- `onslaught/gui/tabs/video_player.py:39`
  - `.vid` browser/player; direct playback + ffmpeg conversion fallback/cache.
- `onslaught/gui/tabs/lore_browser.py:25`
  - Markdown docs browser rooted at `lore-book/BOOK.md`.
- `onslaught/gui/tabs/binary_patches.py:36`
  - GUI wrapper over `onslaught.core.binary_patches`.
- `onslaught/gui/tabs/settings.py:16`
  - Game directory + app preference editor.

### GUI Tabs (Present but Not Mounted)
- `onslaught/gui/tabs/goodie_viewer.py:48`
- `onslaught/gui/tabs/asset_browser.py:44`

### Shared GUI Widget
- `onslaught/gui/widgets/save_selector.py:88`
  - Reusable file selector with auto-detected saves, recent list, and game-dir dialog.

### Test Coverage Pointers
- `tests_pyqt/test_smoke.py` validates mounted tab set.
- `tests_pyqt/test_save_patch_regressions_unittest.py` and CLI tests validate key patcher invariants/guardrails.
- `tests_pyqt/test_binary_patches_unittest.py` validates EXE patch apply/restore behavior.

## Interfaces
### Tab Surfaces (Actual UI)
- Saves
  - `Save Editor` (`SaveEditorTab`)
  - `Save Analyzer` (`SaveAnalyzerTab`)
  - `Configuration Editor` (second `SaveEditorTab` instance in `.bea` mode)
- Media
  - `Audio Player`
  - `Video Player`
- Single tabs
  - `Lore`
  - `Binary Patches`
  - `Settings`

### Patch Flow (CLI + GUI)
1. CLI parses/validates mode and guardrails in `patcher.main` (`patcher.py:1584`), including in-place block and `.bea` career-section safety gate.
2. Option normalization builds rank/kill/settings/options-entry override structures (`patcher.py` main section and helper parsers).
3. `patch_file` validates file size/version, mutates selected sections, preserves kill meta high-byte, optionally copies options entries/tail, applies keybind overrides, then writes output (`patcher.py:580`).
4. GUI `SaveEditorTab._do_patch` collects form state, validates mode/path safety, translates UI overrides, then calls `patch_file` (`onslaught/gui/tabs/save_editor.py:1047`, call at `:1392`).

### Analyze/Compare Flow
- CLI analyze: `patcher.main -> analyze_file` (`patcher.py:1084`) for formatted textual report.
- CLI compare: `patcher.main -> compare_files` (`patcher.py:934`) for region-aware diff report.
- GUI analyze (`SaveAnalyzerTab._do_analyze`):
  - Structured summary via `BesFile.load(..., strict_version=False)` (`onslaught/gui/tabs/save_analyzer.py:376`).
  - Detailed text by importing `patcher.analyze_file` and capturing stdout (`:381-391`).
- GUI compare (`SaveAnalyzerTab._do_compare`): imports `patcher.compare_files` and captures stdout (`:423-432`).

### Config/Storage Model
- App config JSON:
  - Primary: `%APPDATA%/OnslaughtCareerEditor/config.json` on Windows or `~/.config/OnslaughtCareerEditor/config.json` on non-Windows (`onslaught/core/config.py:41-61`).
  - Legacy read/migrate path: `.../onslaught-career-editor/config.json` (`onslaught/core/config.py:64-149`).
  - Schema (camelCase on disk): game directory, recents, window state, tab index, media policy booleans.
- Save discovery:
  - Scans configured/detected game dir subfolders and extra Windows locations; de-duplicates and mtime-sorts (`onslaught/core/config.py:195-247`).
- Binary patch backup:
  - `BEA.exe.original.backup` adjacent to EXE (`onslaught/core/binary_patches.py:14`, `:58`).
- Video conversion cache:
  - `~/.cache/onslaught-career-editor/videos` (`onslaught/gui/tabs/video_player.py:119-123`).
- No DB/service layer; all persistence is local filesystem.

## Risks/Gaps
- GUI-to-CLI coupling is brittle: tabs modify `sys.path` and import `patcher.py` directly (`save_editor.py:1093`, `save_analyzer.py:381/423`).
- Analyzer summary currently duplicates the entire “Options” tree block, likely accidental copy-paste (`save_analyzer.py:211-252` and `:255-295`).
- `patcher.py` is a single large module mixing CLI, parsing, patch logic, and reporting; reuse exists but boundaries are weak for long-term maintainability.
- GUI analysis uses `strict_version=False` for `BesFile.load`; this improves tolerance but can surface partially invalid files as analyzable.
- `GoodieViewerTab` and `AssetBrowserTab` are implemented but unmounted; drift risk against mounted UX and tests.
- Media tabs rely on optional runtime dependencies (Qt Multimedia, ffmpeg) with warning-only degradation paths; behavior differs by machine setup.
- Automated tests cover key regressions and smoke paths, but there is limited end-to-end GUI interaction coverage for complex patch settings/keybind override flows.
