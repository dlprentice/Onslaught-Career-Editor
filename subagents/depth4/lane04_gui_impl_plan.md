# Lane 04 C# GUI Implementation Plan (Depth4 Final Synthesis)

## Inputs
- Source fixcards: `subagents/depth3/lane04_gui_fixcards.md` (L4-C01..L4-C09).
- Supporting parity findings: `subagents/depth2/lane04_gui_parity_validation.md`.

## Scope (C# Only)
Included cards:
- L4-C01 (C# contract hardening only)
- L4-C02
- L4-C03
- L4-C06
- L4-C07
- L4-C08
- L4-C09 (C# side)

Explicitly out of C# implementation scope in this lane output:
- L4-C04 Python lazy-load work (`onslaught/gui/tabs/lore_browser.py`, `onslaught/gui/main_window.py`).
- L4-C05 Python Save Analyzer duplicate `Options` fix.

## Deterministic File Order
Apply changes in this exact order (lexicographic path order). If a file is new, create it at its position in this list:

1. `AssemblyInfo.cs`
2. `MainWindow.xaml`
3. `MainWindow.xaml.cs`
4. `OnslaughtCareerEditor.UiTests/MainWindowMenuTests.cs` (new)
5. `OnslaughtCareerEditor.UiTests/MainWindowStatusParityTests.cs` (new)
6. `OnslaughtCareerEditor.UiTests/MediaPolicyTransitionTests.cs` (new)
7. `OnslaughtCareerEditor.UiTests/OnslaughtCareerEditor.UiTests.csproj` (only if needed for test metadata)
8. `OnslaughtCareerEditor.UiTests/SaveEditorDefaultsTests.cs` (new)
9. `README.MD`
10. `Views/SaveAnalyzerView.xaml.cs`
11. `Views/SaveEditorView.xaml.cs`
12. `Views/SettingsView.xaml.cs`

## Per-File Implementation Tasks

### 1) `AssemblyInfo.cs`
- Add `InternalsVisibleTo("OnslaughtCareerEditor.UiTests")` only if required for minimal internal test seams from cards L4-C06/L4-C07.
- Keep surface area minimal; prefer read-only/internal getters over broad API exposure.

### 2) `MainWindow.xaml`
- Add top menu row (`File`, `Tools`, `Help`) for L4-C03.
- Add menu commands and names for:
  - `Open Save/Options File...`
  - `Analyze Save...`
  - `Compare Saves...`
  - `About`
- Ensure layout still preserves header + main tab + footer behavior.

### 3) `MainWindow.xaml.cs`
- Implement shared status formatter contract from L4-C02:
  - top-level: `"<Main> tab active"`
  - nested: `"<Main> -> <Sub> tab active"`
- Call formatter from both `MainTabControl_SelectionChanged` and `NestedTabControl_SelectionChanged`.
- Ensure startup/restored-tab path sets deterministic status text.
- Add menu handlers (L4-C03) and routing rules:
  - `.bea` -> Configuration/Save editor path handling
  - `.bes` -> Save editor path handling
  - Analyze -> Save Analyzer file load
  - Compare -> Save Analyzer compare flow + guidance status
  - About dialog
- If needed for L4-C07 tests, add minimal internal visibility hooks for media-policy transition state execution (no behavior change).
- Fold shared status strings/constants referenced by L4-C08 (avoid duplicate literals across window-level flows).

### 4) `OnslaughtCareerEditor.UiTests/MainWindowMenuTests.cs` (new)
- Verify menu presence and expected labels.
- Verify route behavior:
  - open `.bea` selects configuration-capable editing flow
  - open `.bes` selects save editing flow
- Verify Analyze/Compare actions route to Save Analyzer tab/subflow.

### 5) `OnslaughtCareerEditor.UiTests/MainWindowStatusParityTests.cs` (new)
- Assert nested status exact string contract:
  - `Saves -> Save Analyzer tab active`
  - `Media -> Video Player tab active`
- Assert top-level-only tab contract:
  - `Lore tab active`

### 6) `OnslaughtCareerEditor.UiTests/MediaPolicyTransitionTests.cs` (new)
- Add deterministic tests for:
  - `AllowBackgroundAudio`
  - `AllowBackgroundVideo`
  - `PreventAudioVideoOverlap`
- Verify stop/start interactions remain deterministic across main-tab and media-sub-tab transitions.

### 7) `OnslaughtCareerEditor.UiTests/OnslaughtCareerEditor.UiTests.csproj`
- Update only if a test dependency/metadata hook is needed for newly added UI tests.
- No speculative package churn.

### 8) `OnslaughtCareerEditor.UiTests/SaveEditorDefaultsTests.cs` (new)
- Add C# parity coverage from L4-C06:
  - Save mode defaults
  - Configuration mode defaults
  - Copy-source first-selection defaults:
    - Save mode: options entries unchecked, options tail unchecked
    - Config mode: options entries checked, options tail unchecked

### 9) `README.MD`
- Document GUI test prerequisites for L4-C09:
  - .NET 10 SDK
  - built app output path
  - interactive desktop session requirement for FlaUI
- Include deterministic GUI test commands section.

### 10) `Views/SaveAnalyzerView.xaml.cs`
- Add minimal `LoadFile(string path)` seam for menu-driven routing (L4-C03).
- Keep existing single `Options` summary behavior as parity reference (no duplication changes needed in C#).
- Align shared wording constants for L4-C08 where applicable.

### 11) `Views/SaveEditorView.xaml.cs`
- Keep existing in-place configuration behavior (L4-C01 source of truth).
- Extract/centralize key status and confirmation strings for deterministic assertions:
  - in-place block message
  - in-place config confirmation text
  - backup wording
- Add minimal `LoadFile(string path)` entry point for menu routing (L4-C03).
- Add small internal read-only seams only if required by `SaveEditorDefaultsTests`.

### 12) `Views/SettingsView.xaml.cs`
- Align status wording constants per L4-C08 canonical strings:
  - `Game directory not set - configure in Settings`
  - `Found <N> save/options file(s)`
  - `No save/options files found`

## Ordered Execution Plan

### Phase A (P0 behavior and contract)
1. `MainWindow.xaml`
2. `MainWindow.xaml.cs`
3. `Views/SaveEditorView.xaml.cs`
4. `Views/SaveAnalyzerView.xaml.cs`
5. `Views/SettingsView.xaml.cs`

### Phase B (P0/P1 automated coverage)
1. `AssemblyInfo.cs` (only if needed)
2. `OnslaughtCareerEditor.UiTests/SaveEditorDefaultsTests.cs`
3. `OnslaughtCareerEditor.UiTests/MainWindowStatusParityTests.cs`
4. `OnslaughtCareerEditor.UiTests/MainWindowMenuTests.cs`
5. `OnslaughtCareerEditor.UiTests/MediaPolicyTransitionTests.cs`
6. `OnslaughtCareerEditor.UiTests/OnslaughtCareerEditor.UiTests.csproj` (only if needed)

### Phase C (bootstrap docs)
1. `README.MD`

## Automated Validation (Deterministic Order)
Run in this order:

1. `dotnet build "Onslaught - Career Editor.sln"`
2. `dotnet test OnslaughtCareerEditor.UiTests/OnslaughtCareerEditor.UiTests.csproj --filter "FullyQualifiedName~SaveEditorDefaultsTests"`
3. `dotnet test OnslaughtCareerEditor.UiTests/OnslaughtCareerEditor.UiTests.csproj --filter "FullyQualifiedName~MainWindowStatusParityTests"`
4. `dotnet test OnslaughtCareerEditor.UiTests/OnslaughtCareerEditor.UiTests.csproj --filter "FullyQualifiedName~MainWindowMenuTests"`
5. `dotnet test OnslaughtCareerEditor.UiTests/OnslaughtCareerEditor.UiTests.csproj --filter "FullyQualifiedName~MediaPolicyTransitionTests"`
6. `dotnet test OnslaughtCareerEditor.UiTests/OnslaughtCareerEditor.UiTests.csproj --filter "FullyQualifiedName~SmokeTests"`

Pass criteria:
- All new tests pass.
- Existing smoke tests stay green.
- No regression in current Save patch regression suite when run in full UI test pass.

## Manual Validation Checklist
Run on an interactive Windows desktop session:

1. Status contract
- Switch to `Lore`: footer shows `Lore tab active`.
- Switch `Saves -> Save Analyzer`: footer shows `Saves -> Save Analyzer tab active`.
- Switch `Media -> Video Player`: footer shows `Media -> Video Player tab active`.

2. Menu routing parity
- `Open Save/Options File...` with `.bes` opens/selects Save editing workflow.
- `Open Save/Options File...` with `.bea` opens/selects configuration-oriented workflow.
- `Analyze Save...` routes to Save Analyzer and loads target file.
- `Compare Saves...` routes to compare-ready analyzer state.
- `About` opens successfully.

3. Configuration in-place safety behavior
- In Configuration mode with same input/output `.bea`, patching prompts for confirmation.
- On confirm, a timestamped `.bak` is created and output is replaced.
- In Save mode with same-path `.bes`, patch is blocked with in-place warning.

4. Media policy transitions
- With overlap prevention enabled, starting one media player stops the other.
- With background disallow toggles disabled, leaving Media tab stops disallowed playback paths.

5. Wording consistency
- Confirm canonical strings appear exactly for game-dir missing and save/options discovery counts.

## Risk Controls
- Keep behavioral changes minimal; avoid altering patch engine semantics.
- Prefer additive test seams and constants over refactors.
- If menu routing introduces ambiguity, default to extension-based deterministic routing (`.bea` vs `.bes`) and explicit status text.
