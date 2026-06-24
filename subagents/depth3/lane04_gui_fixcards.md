# Lane 04 GUI Parity Fix Cards

Source parity findings: `subagents/depth2/lane04_gui_parity_validation.md`.

## Parity Contract (Target)
- Top-level and nested tab flows must behave the same in C# WPF and Python PyQt.
- Save/Configuration Editor safety behavior must match (including in-place rules and confirmation wording intent).
- Main-window status wording should be deterministic and equivalent across both apps.
- GUI parity must be guarded by runnable tests on both stacks.

## Card Queue (Priority)
| Card | Priority | Theme |
|---|---|---|
| L4-C01 | P0 | Configuration in-place patch behavior parity |
| L4-C02 | P0 | Nested-tab status wording parity |
| L4-C03 | P1 | Global menu action parity |
| L4-C04 | P1 | Lore loading strategy parity (lazy-load) |
| L4-C05 | P0 | Python Save Analyzer duplicate Options section |
| L4-C06 | P0 | C# Save Editor defaults/copy-source regression coverage |
| L4-C07 | P1 | Media-policy transition regression coverage |
| L4-C08 | P1 | Cross-shell wording consistency pass |
| L4-C09 | P2 | Runnable GUI test bootstrap parity |

---

## L4-C01 (P0) - Configuration In-Place Patch Behavior Parity
**Finding**: C# allows safe in-place patching in Configuration mode (`.bea`) with backup; Python blocks all same-path patching.

### File-level actions
- C# (`no behavior change`, contract/test only)
  - `Views/SaveEditorView.xaml.cs`
    - Keep existing in-place configuration flow as parity source of truth.
    - Extract/centralize confirmation + backup message text into constants to stabilize cross-app wording/tests.
- Python
  - `onslaught/gui/tabs/save_editor.py`
    - Allow same-path patch only when `configuration_only=True` and both paths are options-like.
    - Add confirmation dialog before in-place patch.
    - Mirror C# safety pattern: patch to temp file, create timestamped `.bak`, replace target, cleanup temp.
    - Keep same-path hard-block in Save mode.
  - `onslaught/core` (if helper extracted)
    - Optional: add a small helper for timestamped backup-path generation to avoid duplicated path logic.

### Acceptance tests
1. Python automated: add `tests_pyqt/test_save_editor_configuration_inplace_unittest.py`.
2. Test case: config mode + same input/output `.bea` => patch allowed, `.bak` created, final file replaced.
3. Test case: save mode + same input/output `.bes` => blocked with in-place warning.
4. C# automated: add assertion coverage to UI regression suite that same-path config mode remains allowed while same-path save mode remains blocked.
5. Manual: from Configuration Editor, patch `defaultoptions.bea` in place and verify timestamped backup exists adjacent to target.

---

## L4-C02 (P0) - Nested-Tab Status Wording Parity
**Finding**: Python updates nested status text (`Main -> Sub tab active` equivalent), C# nested tab changes do not update status detail.

### File-level actions
- C#
  - `MainWindow.xaml.cs`
    - Add one shared formatter for status text:
      - top-level: `"<Main> tab active"`
      - nested: `"<Main> -> <Sub> tab active"`
    - Call formatter from both `MainTabControl_SelectionChanged` and `NestedTabControl_SelectionChanged`.
    - Ensure status is set correctly on startup after tab state restore.
- Python
  - `onslaught/gui/main_window.py`
    - Replace ad-hoc status text composition with the same formatter contract as C#.
    - Normalize arrow token to ASCII `->` for deterministic cross-framework assertions.

### Acceptance tests
1. C# automated: add `OnslaughtCareerEditor.UiTests/MainWindowStatusParityTests.cs`.
2. Assert switching to `Saves -> Save Analyzer` sets status exactly `Saves -> Save Analyzer tab active`.
3. Assert switching to `Media -> Video Player` sets status exactly `Media -> Video Player tab active`.
4. Python automated: add `tests_pyqt/test_main_window_status_unittest.py` with equivalent assertions.
5. Manual: click top-level-only tab (`Lore`) and verify status is `Lore tab active` (no sub-tab suffix).

---

## L4-C03 (P1) - Global Menu Action Parity
**Finding**: Python has `Open/Analyze/Compare/About` menu affordances; C# shell has no equivalent top-level menu.

### File-level actions
- C#
  - `MainWindow.xaml`
    - Add top menu row with `File`, `Tools`, `Help` and actions matching Python intent.
    - Name Save/Analyzer child controls so menu handlers can target them.
  - `MainWindow.xaml.cs`
    - Add handlers:
      - `Open Save/Options File...` -> route to Save Editor or Configuration Editor by extension.
      - `Analyze Save...` -> open file picker and route to Save Analyzer.
      - `Compare Saves...` -> switch to Save Analyzer with compare guidance status.
      - `About` dialog.
  - `Views/SaveEditorView.xaml.cs`
    - Add public/internal `LoadFile(string path)` helper for menu-driven routing.
  - `Views/SaveAnalyzerView.xaml.cs`
    - Add public/internal `LoadFile(string path)` helper for menu-driven routing.
- Python
  - `onslaught/gui/main_window.py`
    - Keep behavior; align labels/ellipsis text with C# menu wording.

### Acceptance tests
1. C# automated: extend `OnslaughtCareerEditor.UiTests/SmokeTests.cs` or new `MainWindowMenuTests.cs` to assert menu items exist.
2. C# automated: open action with `.bea` routes to Configuration Editor; `.bes` routes to Save Editor.
3. Python automated: add `tests_pyqt/test_main_window_menu_unittest.py` (dialog monkeypatch) asserting route/tab selection parity.
4. Manual: run both GUIs and confirm `File/Tools/Help` menu label set matches.

---

## L4-C04 (P1) - Lore Loading Strategy Parity (Lazy Load)
**Finding**: C# Lore tab lazy-loads on activation; Python eagerly loads in constructor.

### File-level actions
- C# (`no behavior change`, baseline)
  - `Views/LoreBrowserView.xaml.cs`
    - Keep `ILazyLoadView` contract and current deferred load behavior.
- Python
  - `onslaught/gui/tabs/lore_browser.py`
    - Remove eager `_load_lore_tree()` call from `__init__`.
    - Add `ensure_loaded()` idempotent method with `_has_loaded` guard.
  - `onslaught/gui/main_window.py`
    - On Lore tab activation, call `lore_browser_tab.ensure_loaded()`.

### Acceptance tests
1. Python automated: add `tests_pyqt/test_lore_browser_lazy_load_unittest.py`.
2. Assert Lore tab instance does not start loader before `ensure_loaded()`.
3. Assert first `ensure_loaded()` triggers load, second call is no-op.
4. Manual: startup should not show lore-loading activity until Lore tab is first opened.

---

## L4-C05 (P0) - Save Analyzer Options Duplication (Python)
**Finding**: Python summary tree adds the `Options` section twice; C# adds it once.

### File-level actions
- Python
  - `onslaught/gui/tabs/save_analyzer.py`
    - Remove duplicate `Options` block in `_populate_summary`.
    - Optional hardening: extract options-node builder into one helper to prevent re-duplication.
- C# (`no behavior change`, reference)
  - `Views/SaveAnalyzerView.xaml.cs`
    - Keep single `Options` section implementation as parity reference.

### Acceptance tests
1. Python automated: add `tests_pyqt/test_save_analyzer_summary_unittest.py`.
2. Assert exactly one top-level `Options` node after `_populate_summary`.
3. Assert options values remain present (volumes/invert/vibration/entries metadata).
4. Manual: analyze same file in both apps; summary tree section count and order are equivalent.

---

## L4-C06 (P0) - C# Save Editor Defaults/Copy-Source Regression Coverage
**Finding**: Python has explicit default-state tests; C# lacks equivalent GUI/default-state assertions.

### File-level actions
- C#
  - `OnslaughtCareerEditor.UiTests/SaveEditorDefaultsTests.cs` (new)
    - Add test coverage for Save mode defaults and Configuration mode defaults.
    - Add coverage for first copy-source selection defaults:
      - Save mode: entries/tail unchecked.
      - Configuration mode: entries checked, tail unchecked.
  - `Views/SaveEditorView.xaml.cs`
    - Expose minimal test seam if needed (internal read-only state helpers) rather than broad API.
  - `AssemblyInfo.cs` (if needed)
    - Add `InternalsVisibleTo("OnslaughtCareerEditor.UiTests")` only if test seam requires internals.
- Python (`existing baseline`)
  - `tests_pyqt/test_save_editor_defaults_unittest.py`
    - Keep as parity oracle; update only if wording/assert API changes.

### Acceptance tests
1. `dotnet test OnslaughtCareerEditor.UiTests/OnslaughtCareerEditor.UiTests.csproj --filter SaveEditorDefaultsTests`
2. Assert C# default states match existing Python assertions in `test_save_editor_defaults_unittest.py`.
3. Manual sanity: open both editors and confirm copy-source controls enable/disable and defaults match.

---

## L4-C07 (P1) - Media Policy Transition Regression Coverage
**Finding**: media-policy transition behavior exists in both apps, but no focused GUI tests validate transitions/status interactions.

### File-level actions
- C#
  - `OnslaughtCareerEditor.UiTests/MediaPolicyTransitionTests.cs` (new)
    - Add assertions around `AllowBackgroundAudio`, `AllowBackgroundVideo`, and overlap-prevention transitions.
  - `MainWindow.xaml.cs`
    - If needed for testability, add minimal internal hooks/readouts around media policy path execution (no behavior change).
- Python
  - `tests_pyqt/test_media_policy_unittest.py` (new)
    - Validate main-tab and media-sub-tab transitions call expected stop handlers based on config flags.
  - `onslaught/gui/main_window.py`
    - Optional tiny refactor to keep policy logic testable (single-purpose helper methods already present).

### Acceptance tests
1. C#: automated policy transition tests pass with deterministic stop behavior.
2. Python: equivalent policy transition tests pass.
3. Manual: with both players active and overlap prevention on, starting one stops the other in both apps.

---

## L4-C08 (P1) - Cross-Shell Wording Consistency Pass
**Finding**: multiple user-facing strings drift between C# and Python (status/footer/save-count wording).

### File-level actions
- C#
  - `MainWindow.xaml.cs`
  - `Views/SettingsView.xaml.cs`
  - `Views/SaveEditorView.xaml.cs`
  - `Views/SaveAnalyzerView.xaml.cs`
    - Centralize repeated status phrases in constants where practical.
- Python
  - `onslaught/gui/main_window.py`
  - `onslaught/gui/tabs/settings.py`
  - `onslaught/gui/tabs/save_editor.py`
  - `onslaught/gui/tabs/save_analyzer.py`
    - Align phrasing to C# contract for shared user-facing flows.

### Minimum canonical strings to align
- `Game directory not set - configure in Settings`
- `Found <N> save/options file(s)`
- `No save/options files found`
- `Output file must be different from input file` (with mode-specific suffix where needed)
- `... tab active` (format from L4-C02)

### Acceptance tests
1. Add lightweight string contract assertions:
   - C#: focused UI tests asserting status/footer text after known actions.
   - Python: unit tests asserting labels/status text after same actions.
2. Manual: side-by-side walkthrough of Settings + tab switching shows equivalent wording intent.

---

## L4-C09 (P2) - Runnable GUI Test Bootstrap Parity
**Finding**: in this lane pass, GUI suites could not run due missing runtime dependencies.

### File-level actions
- C#
  - `README.MD`
  - `OnslaughtCareerEditor.UiTests/OnslaughtCareerEditor.UiTests.csproj` (only if test prerequisites metadata is needed)
    - Document GUI-test prerequisites (interactive desktop session, build output path, .NET 10 SDK).
- Python
  - `README.MD`
  - `requirements.txt`
    - Ensure documented/test dependencies include `pytest`, `pytest-qt`, `PyQt6` for GUI tests.
- Optional helper scripts
  - `tools/` script(s) for one-command GUI test invocation per stack.

### Acceptance tests
1. Fresh machine bootstrap checklist can run both:
   - `dotnet test OnslaughtCareerEditor.UiTests/OnslaughtCareerEditor.UiTests.csproj`
   - `pytest -q tests_pyqt`
2. CI/manual logs include explicit skip reason only when GUI session is genuinely unavailable (not due missing packages).

---

## Suggested Implementation Order
1. L4-C05 (quick correctness fix), L4-C02 (status parity), L4-C01 (high-impact behavior parity).
2. L4-C06 + L4-C07 (lock regressions with tests).
3. L4-C03 + L4-C04 + L4-C08 (shell parity + wording cleanup).
4. L4-C09 (developer ergonomics/bootstrap hardening).
