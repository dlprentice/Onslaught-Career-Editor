# Summary
- The C# app is a single `net10.0-windows` executable with dual entry behavior: no args launches WPF GUI; any args invoke CLI (`Program.Main`: `Program.cs:32-45`, project startup object in `Onslaught - Career Editor.csproj:11`).
- `BesFilePatcher` is the shared core engine for patching, analysis, and compare used by both CLI and UI (`BesFilePatcher.cs:121`, `Program.cs:590-591`, `Program.cs:866`, `Views/SaveAnalyzerView.xaml.cs:143`, `Views/SaveEditorView.xaml.cs:984`).
- Active GUI shell is tab-based (`MainWindow.xaml:42-91`) with top-level surfaces: `Saves`, `Media`, `Lore`, `Binary Patches`, `Settings` (also asserted in UI smoke tests: `OnslaughtCareerEditor.UiTests/SmokeTests.cs:67-76`).
- Save editing is a shared surface (`SaveEditorView`) with mode switching: `Save` (`.bes`) vs `Configuration` (`.bea`) via wrapper `ConfigurationEditorView` (`Views/ConfigurationEditorView.xaml:10`, `Views/ConfigurationEditorView.xaml.cs:20`).
- Binary EXE patching is a separate in-app surface with hardcoded verified byte patches and backup/restore flow (`Views/BinaryPatchesView.xaml.cs:34-54`, `:194-355`).
- `GoodieViewerView` and `AssetBrowserView` exist in repo but are not wired into `MainWindow` tab tree (referenced only in their own files).

# File Map
| File | Role | Key Classes / Surfaces |
|---|---|---|
| `Onslaught - Career Editor.csproj` | App composition/runtime | WPF app, `Program` startup object, packages (`System.CommandLine`, `NAudio`, `LibVLCSharp`, `WebView2`) |
| `Program.cs` | Primary process entrypoint + CLI router | `Program.Main`, `RunGui`, `BuildRootCommand`, `ExecuteCli`, config command handlers |
| `App.xaml.cs` | GUI startup bootstrap | First-launch config/game-dir detection; creates `MainWindow` |
| `MainWindow.xaml` | Active top-level UI map | Tabs: Saves, Media, Lore, Binary Patches, Settings; nested Saves/Media sub-tabs |
| `MainWindow.xaml.cs` | Shell orchestration | Footer/status bus, tab persistence, lazy-load dispatch, media overlap policy |
| `AppConfig.cs` | Cross-surface configuration/service layer | Persisted config, game dir detection, save/options file discovery |
| `BesFilePatcher.cs` | Core domain engine | `PatchFile`, `AnalyzeSave`, `CompareFiles`, report formatting, keybind parse/format |
| `Views/SaveEditorView.xaml(.cs)` | Main save/config patch UI | Patch presets, section toggles, advanced mission/kill/settings/keybind overrides, options-copy flow |
| `Views/ConfigurationEditorView.xaml(.cs)` | Config-mode wrapper | Hosts `SaveEditorView`, forces `.bea` workflow |
| `Views/SaveAnalyzerView.xaml(.cs)` | Read-only analysis UI | Analyze, compare, summary TreeView, report copy |
| `Views/AudioPlayerView.xaml(.cs)` | Media surface: audio | Lazy-loaded scan/playback via NAudio + Vorbis |
| `Views/VideoPlayerView.xaml(.cs)` | Media surface: video | Lazy-loaded scan/playback via LibVLC |
| `Views/LoreBrowserView.xaml(.cs)` | Lore/docs browser | Lazy-loaded markdown + WebView2, tree/search/history |
| `Views/BinaryPatchesView.xaml(.cs)` | EXE binary patch UI | Patch verify/apply/restore with backup |
| `Views/SettingsView.xaml(.cs)` | Settings/admin UI | Game dir config, media behavior flags, save count/paths |
| `Views/ILazyLoadView.cs` | UI contract | `EnsureLoaded()` for deferred-heavy tabs |
| `Views/GoodieViewerView.*`, `Views/AssetBrowserView.*` | Dormant/unsurfaced views | Implemented but not mounted in active main tab shell |

# Interfaces
## Entrypoints
- **Process entry**: `Program.Main` selects GUI vs CLI (`Program.cs:32-45`).
- **GUI entry**: `RunGui` creates `App` and calls `app.Run()` (`Program.cs:50-57`); `App.OnStartup` creates `MainWindow` (`App.xaml.cs:11-42`).
- **CLI entry**: `BuildRootCommand().Invoke(args)` (`Program.cs:44`).

## Active Tab Surfaces
- **Saves**
  - `Save Editor` (`Views:SaveEditorView`) for `.bes` patching and advanced overrides (`MainWindow.xaml:53-55`).
  - `Save Analyzer` (`Views:SaveAnalyzerView`) for analysis/compare/reporting (`MainWindow.xaml:56-58`).
  - `Configuration Editor` (`Views:ConfigurationEditorView`) for `.bea` global options workflow (`MainWindow.xaml:59-61`).
- **Media**
  - `Audio Player` (`Views:AudioPlayerView`) and `Video Player` (`Views:VideoPlayerView`) (`MainWindow.xaml:70-75`).
- **Lore**
  - `Lore Browser` (`Views:LoreBrowserView`) markdown/webview surface (`MainWindow.xaml:79-81`).
- **Binary Patches**
  - `BinaryPatchesView` EXE byte patch surface (`MainWindow.xaml:83-85`).
- **Settings**
  - `SettingsView` configuration and playback policy (`MainWindow.xaml:87-89`).

## CLI Surface
- Flat root command (no subcommands), positional `input` + optional `output` (`Program.cs:88-96`, `:324-381`).
- Read-only modes:
  - `--analyze`, `--compare`, `--list-goodies` (`Program.cs:99-122`, `:553-616`, `:997-1102`).
- Patch modes/options:
  - Mission rank/kills toggles + per-level/per-category overrides (`Program.cs:123-185`, `:651-710`).
  - Career settings overrides (`Program.cs:186-225`, `:713-749`).
  - Options-copy and keybind override options (`Program.cs:231-308`, `:1134-1358`).
- Config/admin options:
  - `--list-saves`, `--set-game-dir`, `--show-config` (`Program.cs:311-321`, `:894-995`).
- Safety guards:
  - Input required, output required for patching, in-place write block, options-file career-section block unless explicit override (`Program.cs:532-539`, `:618-634`, `:777-788`).

## Patch Engines
- **Career/options patch engine**: `BesFilePatcher.PatchFile` (`BesFilePatcher.cs:354`).
  - Safety: strict size/version validation + no in-place writes.
  - Feature lanes: nodes/links/goodies/kills, per-level/per-category overrides, settings overrides, options-copy, options-entry/keybind overrides.
  - Analysis/compare/report interfaces: `AnalyzeSave`, `CompareFiles`, `FormatCompareReport`, `FormatAnalysisReport` (`BesFilePatcher.cs:1069`, `:1351`, `:1421`, `:1545`).
- **Binary EXE patch engine (UI-contained)**: `BinaryPatchesView`.
  - Patch specs are embedded (`Views/BinaryPatchesView.xaml.cs:34-54`).
  - `Verify -> Apply -> Restore` workflow with `.original.backup` path (`:95`, `:194-355`).

# Risks/Gaps
- Large code-behind concentration increases coupling and test burden: `SaveEditorView.xaml.cs` (~2053 lines), `LoreBrowserView.xaml.cs` (~1963 lines), `Program.cs` (~1443 lines), `BesFilePatcher.cs` (~1867 lines).
- Keybind parse/validation logic is duplicated in CLI and UI flows (`Program.ParseKeybindOverridesFromCli` vs `SaveEditorView.ParseKeybindOverrides`), which can drift.
- Binary patching is offset/signature specific to known `BEA.exe` bytes; there is no full-build hash/version gate before patch attempt.
- Dormant views (`AssetBrowserView`, `GoodieViewerView`) are implemented but unsurfaced, creating maintenance surface without active UI coverage.
- CLI is powerful but flat (single root with many options); discoverability and invalid option combinations are harder to manage than subcommand-based segmentation.
