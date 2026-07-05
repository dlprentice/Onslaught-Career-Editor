# WinUI v1.0.9 Action / Reaction Map

Status: source-derived release-readiness support note
Date: 2026-07-05
Scope: `OnslaughtCareerEditor.WinUI` primary app surface and the AppCore services reached by visible controls.

This note is for harder release questioning and code-flow orientation. It is not
a new release, runtime gameplay proof, visual parity proof, online proof,
installer/signing proof, or rebuild proof.

## Claim Boundaries

- v1.0.9 remains an unsigned portable Windows x64 ZIP release.
- The app ZIP includes app runtime/support files, `lore-book/`, and the 949-document `lore-pack/`.
- The app ZIP does not include Battle Engine Aquila game files, copied executables, saves, extracted media, full Ghidra databases, raw proof captures, or secrets.
- App workflows that need game material use the user's local install as input.
- Save/options editing writes selected output files, not in-place originals.
- Executable patching and playable launch flows are bounded to app-owned copies or app-owned BEA.exe-only working copies.
- Host/Join and player-ready online remain unavailable.

## Hard Questions And Straight Answers

Q: What is the first thing a normal user sees after extraction?
A: A friendly root folder with `Launch Onslaught Toolkit.cmd`, `README.MD`, `LICENSE`, `app/`, `lore-book/`, and `lore-pack/`. The DLL/EXE payload is under `app/`.

Q: Can the app start without the game installed?
A: Yes. The app can launch, show Home, read bundled Lore, and show configuration states. Game-aware flows such as Media browsing, safe-copy creation, asset catalog use, and real save/options edits need user-selected local inputs.

Q: Does the ZIP contain everything needed to run the app besides the game itself?
A: Yes, based on the v1.0.9 release probe and package shape. The root launcher targets the bundled app payload under `app/`. Windows remains the platform prerequisite.

Q: Is Lore still fully included?
A: Yes. v1.0.9 includes a generated offline Lore pack with 949 public-safe Markdown/TXT documents plus a short `lore-book/BOOK.md` entry point.

Q: What breaks if the user moves only the launcher out of the extracted folder?
A: The friendly launcher no longer has its expected sibling `app/` payload. The intended flow is extracting the full ZIP and running the launcher from the extracted root.

Q: Is the release signed or installer-grade?
A: No. It is an unsigned portable ZIP with a SHA-256 sidecar.

Q: Is SmartScreen/reputation solved?
A: No. The release does not claim signing, SmartScreen reputation, MSIX, Store, or installer trust.

Q: Is the original Steam/game folder ever patched by the app's normal patch flow?
A: The visible patch/launch flow is designed around copied files and app-owned safe-copy workspaces. The source game install is read-only input for creating safe copies.

Q: Which actions write to disk?
A: Settings save app config, Save Lab writes selected save/options output files, Windowed & Mods creates app-owned copies and safe game copies, material-package preparation writes an app-owned asset package, and safe-copy music staging writes within the safe copy.

Q: Which actions can start external processes?
A: Launch safe game copy starts copied `BEA.exe`; Stop copied game targets the managed process record after confirmation. Asset/Media open/show actions use shell/explorer. Lore open external uses the OS URI launcher.

Q: Does Media playback prove in-game media behavior?
A: No. It proves app-side media catalog/playback behavior only.

Q: Does safe-copy launch prove gameplay or patch behavior?
A: No. It proves guarded process start and managed process control only unless a separate runtime proof records more.

Q: Does selecting a patch row mutate anything?
A: No. Patch row selection only changes the pending plan and invalidates prior verification. Mutation happens only after create/verify/apply or safe-copy preparation flows.

Q: Does Verify mutate anything?
A: No. It checks selected patch rows against the app-owned working copy and records a verification signature for the current selection.

Q: Does Apply mutate the installed game?
A: No. Apply is bounded to the verified app-owned BEA.exe-only working copy.

Q: Does Prepare safe copy mutate the installed game?
A: No. It copies the selected game folder into the app-owned `GameProfiles` workspace, then patches or configures that copied profile.

Q: Does Stage music replacement mutate the installed game?
A: No. It stages bytes in the prepared safe copy and writes a manifest/backup there.

Q: Are online Host/Join controls hidden behind a technical toggle?
A: No player-ready Host/Join flow is enabled. Technical toggles reveal status/details/loaders only; they do not create a playable online session.

Q: What is the highest-risk user action?
A: Safe-copy creation/launch/stop, because it copies a full game folder, starts a copied executable, and can close or force-close that copied process. The app presents confirmation text and keeps the target within app-owned workspace boundaries.

Q: What is the highest-risk source action?
A: Any future loosening of path validation around patch targets, safe-copy roots, music staging, material packages, or process stop targeting.

Q: What should a reviewer audit next?
A: Generate a per-control matrix from XAML AutomationIds, event handlers, and code-behind effects, then compare it with the grouped map below.

## Mutation And Side-Effect Classes

| Class | Examples | Boundary |
| --- | --- | --- |
| Navigation/UI only | Shell nav, Home task cards, tabs, filters, preview background buttons | No disk or process effect except saved last-tab preferences where noted |
| Config write | Settings game directory/media toggles, Media tab preference, asset catalog path | App config only |
| Clipboard | Copy analyzer report, copy patch/output/package/export path | Clipboard only |
| User-selected output write | Save Editor patch, Game Options patch | Separate output file; in-place source patching blocked |
| App-owned copy mutation | BEA.exe-only working copy, safe copied game profile, safe-copy music staging | App config workspace only |
| Process launch/stop | Launch safe game copy, Stop copied game, open/show asset/media folder, open Lore external | Copied game process or OS shell/URI launcher |
| Read/preview | Media catalog, Lore pack, asset catalog, analyzer, Goodie save-state overlay | Read-only unless a paired export/package action is invoked |

## Top-Level Code Flow

1. App launch creates `MainWindow`.
2. `MainWindow` loads `AppConfig`, applies saved window size, builds page cache, refreshes footer, and navigates to saved or default tab.
3. `ShellNavigationView_SelectionChanged` calls `NavigateToTag`.
4. `NavigateToTag` swaps the cached page into `ContentFrame`, optionally selects a Save Lab subtab, and persists `LastTab`.
5. `ReviewSetupButton_Click` navigates to Settings and refreshes footer/status.
6. `AppWindow_Closing` warns first if a managed copied game process is still registered.
7. `MainWindow_Closed` stops managed safe-copy processes after allowed close and persists window size.

## Home

| Action | Handler | Reaction |
| --- | --- | --- |
| Task card buttons | `NavigateButton_Click` | Reads button `Tag` and navigates to the matching shell page. |
| Open configuration editor | `OpenConfigurationEditorButton_Click` | Navigates to Save Lab subtab 2, Game Options. |

## Settings

| Action | Handler | Reaction |
| --- | --- | --- |
| Browse game directory | `BrowseGameDirectoryButton_Click` | Folder picker, validates selected folder, saves app config if directory exists, notifies config listeners, refreshes footer. |
| Auto-detect game directory | `AutoDetectGameDirectoryButton_Click` | Uses configured detection, saves if found, otherwise reports no detection. |
| Media preference toggles | `MediaPreferenceChanged` | Saves `AllowBackgroundAudio`, `AllowBackgroundVideo`, and `PreventAudioVideoOverlap` to app config. |
| Reload | `ReloadButton_Click` | Reloads config, detected save/options summary, and status text. |

## Save Lab

| Action | Handler | Reaction |
| --- | --- | --- |
| Task cards / subtab buttons | `AnalyzeTaskButton_Click`, `EditSaveTaskButton_Click`, `ConfigureOptionsTaskButton_Click`, `SaveAnalyzerTabButton_Click`, `SaveEditorTabButton_Click`, `ConfigurationEditorTabButton_Click` | Selects the corresponding Save Lab subtab and persists last subtab. |
| Analyzer browse file | `BrowseFileButton_Click` | Picks `.bes`/`.bea`, fills path, runs analysis. |
| Analyzer detected file selection | `DetectedFilesComboBox_SelectionChanged` | Fills path and runs analysis. |
| Analyzer path edits | `FilePathTextBox_TextChanged`, `CompareFilePathTextBox_TextChanged` | Enables/disables Analyze, Compare, Copy Report. |
| Analyze | `AnalyzeButton_Click` | Calls `SaveAnalyzerService.AnalyzeFile`, updates metrics/tree/report/status. |
| Compare | `CompareButton_Click` | Calls `SaveAnalyzerService.CompareFiles`, updates comparison report or warning. |
| Verbose / mystery toggles | `DisplayOption_Toggled` | Re-runs analysis for current single-file document. |
| Copy report | `CopyReportButton_Click` | Copies report text to clipboard. |
| Clear analyzer | `ClearButton_Click` | Clears selected files and resets analyzer UI. |
| Save Editor detected/browse input | `EditorDetectedFilesComboBox_SelectionChanged`, `BrowseEditorInputButton_Click` | Selects source `.bes`, builds default output path, loads advanced snapshot. |
| Save Editor browse output | `BrowseEditorOutputButton_Click` | Chooses output folder and fills separate output path. |
| Save Editor path edits | `EditorPathTextBox_TextChanged` | Validates input, refreshes advanced snapshot, updates action state. |
| Save Editor preset/check boxes/toggles/number boxes | `EditorPatchPresetComboBox_SelectionChanged`, `EditorPatchSectionCheckBox_Changed`, `EditorKillsOnlyCheckBox_Changed`, `EditorQuickSettingSelectionChanged`, `EditorQuickSettingToggled`, `EditorGlobalKillNumberBox_ValueChanged` | Rebuilds pending patch request summary, enables patch only when valid. Kills-only temporarily disables other patch sections. |
| Advanced rank buttons | `EditorSetMissionRanksToDefaultButton_Click`, `EditorClearMissionRanksButton_Click` | Sets mission rank override rows or clears them back to keep. |
| Advanced rank/kill row changes | `EditorMissionRankOverrideComboBox_SelectionChanged`, `EditorCategoryKillOverrideCheckBox_Changed`, `EditorCategoryKillNumberBox_ValueChanged` | Updates pending advanced override validity. |
| Write patched save copy | `EditorPatchButton_Click` | Builds `SavePatchRequest`, confirms overwrite if needed, calls `SaveEditorService.PatchSave`, writes selected output file only. |
| Copy Save Editor output | `EditorCopyOutputButton_Click` | Copies output/status text to clipboard. |
| Game Options detected/browse input | `ConfigurationDetectedFilesComboBox_SelectionChanged`, `BrowseConfigurationInputButton_Click` | Selects `.bea`, builds default output path, loads options snapshot/keybind rows. |
| Game Options browse output | `BrowseConfigurationOutputButton_Click` | Chooses output folder and fills separate `.bea` output path. |
| Game Options copy-source browse/clear | `BrowseConfigurationCopySourceButton_Click`, `ClearConfigurationCopySourceButton_Click` | Selects or clears a source for copying options regions/keybinds. |
| Game Options toggles/selections/text/number edits | `ConfigurationOverrideToggle_Toggled`, `ConfigurationOptionSelectionChanged`, `ConfigurationNumberBox_ValueChanged`, `ConfigurationControllerConfigTextBox_TextChanged`, `ConfigurationKeybindTextBox_TextChanged`, `ConfigurationCopySourceTextBox_TextChanged`, `ConfigurationPathTextBox_TextChanged` | Rebuilds `ConfigurationPatchRequest`, validates output extension, copy source, controller values, keybind tokens, and in-place block. |
| Load keybinds | `LoadConfigurationKeybindsFromInputButton_Click`, `LoadConfigurationKeybindsFromCopySourceButton_Click` | Copies keybind override tokens from current input or selected copy source into editable rows. |
| Clear keybinds | `ClearConfigurationKeybindsButton_Click` | Clears keybind override fields. |
| Write options copy | `ConfigurationPatchButton_Click` | Confirms overwrite if needed, calls `ConfigurationEditorService.PatchConfiguration`, writes selected output `.bea` only. |
| Copy Game Options output | `ConfigurationCopyOutputButton_Click` | Copies output/status text to clipboard. |

## Windowed & Mods

| Action | Handler | Reaction |
| --- | --- | --- |
| Patch row checkbox changes | `PatchCheckBox_Changed` | Updates selected patch model, enforces mutually exclusive patch families, invalidates verification, refreshes controls. |
| Profile buttons | `WindowedPresetButton_Click`, `StableDefaultsButton_Click`, `ModernGraphicsPresetButton_Click`, `EnhancedPreviewPresetButton_Click`, `DebugCameraPreviewPresetButton_Click`, `ClearSelectionButton_Click` | Selects known patch key sets and resets/updates related launch/control options where applicable. No files mutate. |
| Menu color buttons | `MenuColorRedButton_Click`, `MenuColorGreenButton_Click`, `MenuColorBlackButton_Click`, `MenuColorClearButton_Click` | Selects at most one frontend color patch row or clears it. |
| Version / Goodies quick buttons | `AddVersionMarkerButton_Click`, `ClearVersionMarkerButton_Click`, `AddGoodiesPreviewButton_Click`, `ClearGoodiesPreviewButton_Click` | Toggles specific patch rows. |
| Local multiplayer probe | `LocalMultiplayerProbeButton_Click` | Fills launch arguments for local split-screen probe (`-skipfmv -level 850`) and status text. Does not enable Host/Join. |
| Technical detail toggles | `OnlineTechnicalDetailsToggle_Toggled`, `MaintainerArtifactToolsToggle_Toggled` | Shows/hides technical status/details or summary loader controls only. |
| Technical summary loaders | `LoadDualSafeCopyTopologyArtifactButton_Click`, `LoadOnlineReadinessArtifactButton_Click`, `LoadGamepadReadinessArtifactButton_Click` | Loads redacted JSON summary artifacts into readiness/status panels. No online action. |
| Technical summary clears | `ClearDualSafeCopyTopologyArtifactButton_Click`, `ClearOnlineReadinessArtifactButton_Click`, `ClearGamepadReadinessArtifactButton_Click` | Clears loaded summary state and re-renders locked online readiness. |
| Launch preset buttons | `QuietCaptureLaunchPresetButton_Click`, `HighDetailLaunchPresetButton_Click`, `ClearLaunchOptionsButton_Click`, `ControlBaselinePresetButton_Click`, `ControlSharpenedPresetButton_Click`, `ControlConfig2PresetButton_Click`, `ControlConfig3PresetButton_Click`, `ControlConfig4PresetButton_Click` | Fills allowed launch/options fields and refreshes safe-copy launch preview. |
| Launch option edits | `LaunchOptionCheckBox_Changed`, `LaunchOptionTextBox_TextChanged`, `LaunchOptionComboBox_SelectionChanged`, `AdminLevelPresetComboBox_SelectionChanged` | Clears preset ownership on manual edits, rebuilds launch preview, validates allowed argument shape. |
| Source executable browse/use settings | `BrowseButton_Click`, `UseGameDirButton_Click`, `SourceExePathTextBox_TextChanged` | Selects or derives source `BEA.exe`, clears stale copied launch state, invalidates verification. |
| Create BEA.exe-only copy | `CreateWorkingCopyButton_Click` | Validates source, creates app-owned copy under config `PatchBench`, refuses installed-game mutation. |
| Verify BEA.exe-only copy | `VerifyButton_Click` | Calls `BinaryPatchEngine.VerifyPatchTargetFile`; records verification signature for current selection. |
| Apply BEA.exe-only patches | `ApplyButton_Click` | Requires matching verification signature and confirmation, calls `BinaryPatchEngine.ApplyPatchesToFile` against app-owned copy only. |
| Restore BEA.exe-only copy | `RestoreButton_Click` | Requires backup and confirmation, restores app-owned copy from backup. |
| Prepare safe copy | `PrepareCopiedProfileButton_Click` | Confirms, copies selected game folder into app-owned `GameProfiles`, applies selected patch/profile options, writes receipt/manifest/status. |
| Launch safe game copy | `LaunchCopiedProfileButton_Click` | Confirms, validates launch plan, calls `GameProfileRuntimeService.LaunchCopiedProfile`, registers managed process. Process start only. |
| Stop copied game | `StopCopiedProfileButton_Click` | Confirms, then stops only the managed safe-copy process record through `App.SafeGameCopyProcesses`. |
| Music track combo/input edits | `MusicTrackComboBox_SelectionChanged`, `MusicReplacementInput_TextChanged` | Fills target/replacement values and refreshes enablement. |
| Stage copied-track swap / replacement | `StageCopiedTrackSwapButton_Click`, `StageMusicReplacementButton_Click`, `MusicSwapBea02ForBea01PresetButton_Click`, `MusicSwapBea01ForBea02PresetButton_Click`, `MusicSwapBea02ForBea04PresetButton_Click` | Stages OGG bytes inside prepared safe copy only, writes backup/manifest, blocks while copied game is running. |
| Restore music backup | `RestoreMusicReplacementButton_Click` | Restores staged music backup inside safe copy only, blocks while copied game is running. |

## Media

| Action | Handler | Reaction |
| --- | --- | --- |
| Browse game directory | `BrowseGameDirectoryButton_Click` | Folder picker, checks media-like game directory, saves app config, reloads catalog. |
| Reload library | `ReloadLibraryButton_Click` | Reloads media catalog from configured game directory. |
| Audio/Video tabs | `AudioTabButton_Click`, `VideoTabButton_Click` | Switches visible tab, persists last media subtab, applies audio/video overlap policy. |
| Search boxes | `AudioSearchTextBox_TextChanged`, `VideoSearchTextBox_TextChanged` | Filters audio/video trees. |
| Tree select/invoke | `AudioTreeView_SelectionChanged`, `AudioTreeView_ItemInvoked`, `VideoTreeView_SelectionChanged`, `VideoTreeView_ItemInvoked` | Selects media item and updates details. |
| Tree double-click | `AudioTreeView_DoubleTapped`, `VideoTreeView_DoubleTapped` | Starts selected audio/video playback. |
| Play/Pause/Stop | `AudioPlayButton_Click`, `AudioPauseButton_Click`, `AudioStopButton_Click`, `VideoPlayButton_Click`, `VideoPauseButton_Click`, `VideoStopButton_Click` | Controls app-side audio/video playback. |
| Volume sliders | `AudioVolumeSlider_ValueChanged`, `VideoVolumeSlider_ValueChanged` | Updates displayed volume and active player volume. |
| Progress sliders | audio/video pointer and value handlers | Tracks drag state and seeks active player to slider time. |
| Show in Explorer | `RevealVideoButton_Click` | Opens Explorer selecting the chosen video file. |

## Lore

| Action | Handler | Reaction |
| --- | --- | --- |
| Page load | `LorePage_Loaded` | Loads Lore index from bundled/source pack and initial document. |
| Search | `SearchTextBox_TextChanged` | Debounced tree filter. |
| Refresh | `RefreshButton_Click` | Reloads Lore index while preserving current document when possible. |
| Tree select/invoke | `DocumentTree_SelectionChanged`, `DocumentTree_ItemInvoked` | Loads selected Lore document into WebView reader and history. |
| Back/Forward/Home | `BackButton_Click`, `ForwardButton_Click`, `HomeButton_Click` | Navigates internal Lore history/home document. |
| Toggle library | `ToggleLibraryButton_Click` | Opens/closes Lore document pane. |
| Open external | `OpenExternalButton_Click` | Opens current document/display URI through OS URI launcher. |

## Asset Library

| Action | Handler | Reaction |
| --- | --- | --- |
| Browse/load/change catalog | `BrowseCatalogButton_Click`, `LoadCatalogButton_Click`, `ChangeCatalogButton_Click` | Loads generated local asset catalog, persists catalog path, refreshes coverage/provenance/list; Change reopens chooser. |
| Asset tabs | `TexturesTabButton_Click`, `MeshesTabButton_Click`, `EmbeddedMeshesTabButton_Click`, `GoodiesTabButton_Click` | Switches list type and filter panels. |
| Goodies filters | `GoodiesAllFilterButton_Click`, `GoodiesWallFilterButton_Click`, `GoodiesHiddenFilterButton_Click`, `GoodiesModelsFilterButton_Click`, `GoodiesArtworkFilterButton_Click`, `GoodiesVideosFilterButton_Click` | Filters Goodies list and updates status/styles. |
| Search | `AssetSearchBox_TextChanged` | Filters current asset list. |
| List selection | `AssetItemsListView_SelectionChanged` | Shows texture, mesh, embedded mesh, or Goodie details/preview. |
| Goodie save-state browse/load/clear | `BrowseGoodieSaveStateButton_Click`, `LoadGoodieSaveStateButton_Click`, `ClearGoodieSaveStateButton_Click` | Reads selected `.bes` to overlay Goodie state; clear returns to catalog-only identity. |
| Model view buttons | `ModelViewFrontButton_Click`, `ModelViewSideButton_Click`, `ModelViewTopButton_Click`, `ModelViewIsoButton_Click` | Changes wireframe projection and redraws model preview. |
| Texture background buttons | `TexturePreviewNeutralButton_Click`, `TexturePreviewLightButton_Click`, `TexturePreviewDarkButton_Click` | Changes preview background only. |
| Open/copy selected export | `OpenExportButton_Click`, `CopyExportPathButton_Click` | Opens selected export through shell or copies path. |
| Open in Media | `OpenInMediaButton_Click` | Sends media handoff request and navigates to Media. |
| View linked texture | `ViewLinkedTextureButton_Click` | Selects linked texture row or previews sidecar texture. |
| Write local package | `PrepareMaterialPackageButton_Click` | Materializes/inspects an asset material import package under app-selected output root. |
| Open/copy material package | `OpenMaterialPackageButton_Click`, `CopyMaterialPackagePathButton_Click` | Opens material package folder or copies its path. |

## About

About is static in v1.0.9. Its constructor fills the version label from assembly metadata and sets status text. It has no page-local buttons, toggles, or click handlers.

## Reviewer Next Step

For the stricter "every individual control" audit, see the companion generated
matrix at `release/readiness/winui_control_action_matrix_v1_0_9_2026-07-05.tsv`,
with one row per XAML element:

`Page | AutomationId | visible label/content | control type | event | handler | handler source | effect class | write target | process target | safety boundary | test coverage`

The grouped map above covers every visible handler family found in the source
scan, but it intentionally groups repeated controls that share the same handler
and effect.
