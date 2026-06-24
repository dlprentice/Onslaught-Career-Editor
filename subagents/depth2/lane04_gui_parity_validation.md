# GUI Parity Validation (C# WPF vs Python PyQt)

## Scope
- Focused on active tabs and cross-tab behavior expectations in the current UI shell.
- Evidence sources: implementation code + test code + existing C# UI test artifact.
- Environment limitation during this pass: local execution of GUI suites was blocked (`dotnet` missing, `pytest` missing, `PyQt6` missing).

## Test Execution Reality (this pass)
- Could not run C# UI tests locally: `/bin/bash: dotnet: command not found`.
- Could not run PyQt tests locally: `/usr/bin/python3: No module named pytest`; `PyQt6 unavailable` when invoking unittest class setup.
- Used existing C# run artifact for executed evidence: `OnslaughtCareerEditor.UiTests/TestResults/ui-tests.trx:13`, `OnslaughtCareerEditor.UiTests/TestResults/ui-tests.trx:66`.

## Parity Matrix

### Matched
| Area | Status | Evidence (C#) | Evidence (Python) | Test Evidence |
|---|---|---|---|---|
| Top-level and nested active tabs are aligned (`Saves`, `Media`, `Lore`, `Binary Patches`, `Settings`; nested `Save Editor`, `Save Analyzer`, `Configuration Editor`, `Audio Player`, `Video Player`) | Matched | `MainWindow.xaml:42-91` | `onslaught/gui/main_window.py:70-111` | C# smoke assertion `OnslaughtCareerEditor.UiTests/SmokeTests.cs:67-76` (passed in artifact `.../ui-tests.trx:13`); Python smoke assertion `tests_pyqt/test_smoke.py:30-45` |
| Last-selected main tab is persisted/restored | Matched | Restore `MainWindow.xaml.cs:29-33`; persist `MainWindow.xaml.cs:93-95` | Restore `onslaught/gui/main_window.py:233-239`; persist `onslaught/gui/main_window.py:286-287`, `346-347` | Config schema parity: `AppConfig.cs:60-70` and `onslaught/core/config.py:75-79,105-109,129-133` |
| Cross-media policy controls exist and are enforced (background audio/video + overlap prevention) | Matched | Main-window policy handlers `MainWindow.xaml.cs:119-133,156-179`; settings writes + apply-now `Views/SettingsView.xaml.cs:169-178` | Main-window policy handlers `onslaught/gui/main_window.py:307-340`; settings writes + apply-now `onslaught/gui/tabs/settings.py:232-238` | Settings controls present on both: `Views/SettingsView.xaml:79-93`, `onslaught/gui/tabs/settings.py:98-108` |
| Binary Patches tab flow parity (verify selected, apply selected, restore backup; same patch intents) | Matched | `Views/BinaryPatchesView.xaml.cs:34-54,194-241,243-314` | `onslaught/gui/tabs/binary_patches.py:25-33,199-233,234-261` | Python binary patch regression tests exist: `tests_pyqt/test_binary_patches_unittest.py:22-79` |
| Save Analyzer supports analyze + compare workflows | Matched | Analyze/compare flow `Views/SaveAnalyzerView.xaml.cs:132-165,374-393` | Analyze/compare flow `onslaught/gui/tabs/save_analyzer.py:366-442` | UI smoke covers tab presence (`SmokeTests.cs`, `test_smoke.py`) |

### Missing
| Area | Status | Evidence (C#) | Evidence (Python) | Test Evidence |
|---|---|---|---|---|
| Automated GUI coverage for Save Editor configuration-mode defaults/copy-source defaulting | Missing on C# side | No equivalent UI default tests under `OnslaughtCareerEditor.UiTests/` (only `SmokeTests.cs`, `SavePatchRegressionTests.cs`) | Explicit tests exist | `tests_pyqt/test_save_editor_defaults_unittest.py:20-103` exercises these defaults |
| Automated coverage for main-window media-policy transitions and nested-tab status messaging | Missing on both | No C# test asserts these main-window status/policy transitions | No Python test asserts these transitions | Only tab-presence smoke covers shell (`SmokeTests.cs:18-77`, `test_smoke.py:15-45`) |
| Runnable GUI test environment in this lane | Missing in current environment | `dotnet` unavailable | `pytest`/`PyQt6` unavailable | Runtime errors observed during this pass |

### Divergent
| Area | Status | Evidence (C#) | Evidence (Python) | Impact |
|---|---|---|---|---|
| Configuration Editor in-place patching | Divergent | In-place allowed for configuration mode with confirmation + `.bak` backup: `Views/SaveEditorView.xaml.cs:915-949,977-996`; enable logic `Views/SaveEditorView.xaml.cs:1983-1994` | In-place always blocked: `onslaught/gui/tabs/save_editor.py:687-710,1071-1074` | Behavior mismatch for `.bea` workflows (C# supports safe in-place path; Python requires separate output path) |
| Nested-tab status detail text | Divergent | Main-tab handler sets top-level status (`"{tab} tab active"`), nested handler does not update status text: `MainWindow.xaml.cs:97-117` | Nested changes explicitly set `"Main → Sub"` detail: `onslaught/gui/main_window.py:290-300` | User-visible status differences when switching `Saves`/`Media` subtabs |
| Global menu actions (`Open`, `Analyze`, `Compare`, `About`) | Divergent (Python-only) | No main-window menu wiring in `MainWindow.xaml:19-123` / `MainWindow.xaml.cs` | Menu + handlers implemented: `onslaught/gui/main_window.py:121-156,174-231` | Additional entry paths exist only in Python shell |
| Lore tab loading strategy | Divergent | Explicit lazy-load contract (`ILazyLoadView` + defer until activation): `Views/LoreBrowserView.xaml.cs:23,69-70,90-98` | Eager load on tab construction (`_load_lore_tree()` in `__init__`): `onslaught/gui/tabs/lore_browser.py:42-44,146-169` | Different startup/perf behavior |
| Save Analyzer summary tree composition | Divergent | Single `Options` section build: `Views/SaveAnalyzerView.xaml.cs:199-225` | `Options` section added twice (duplicated block): `onslaught/gui/tabs/save_analyzer.py:211-252` and `254-295` | Python summary output includes duplicated section content |

## Bottom Line
- Core active-tab structure and major tab capabilities are aligned.
- Key behavior drifts are concentrated in: configuration in-place patch policy, status text behavior, menu affordances, lore loading timing, and Python Save Analyzer summary duplication.
- Coverage parity is not aligned; Python has stronger GUI default-state assertions for Save Editor configuration safety than C#.
