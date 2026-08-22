using System;
using System.ComponentModel;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading.Tasks;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Automation;
using Microsoft.UI.Xaml.Controls;
using OnslaughtCareerEditor.WinUI.Helpers;
using OnslaughtCareerEditor.WinUI.Models;
using OnslaughtCareerEditor.AppCore;

namespace OnslaughtCareerEditor.WinUI.Pages
{
    public sealed partial class BinaryPatchesPage : Page
    {
        private static readonly string[] s_modernGraphicsKeys = { "extra_graphics_default_on", "ignore_cardid_tweak_overrides" };
        private static readonly string[] s_frontendColorPatchKeys =
        {
            "frontend_clear_screen_dark_red",
            "frontend_clear_screen_dark_green",
            "frontend_clear_screen_black",
        };
        private static readonly string[] s_freeCameraKeyboardQRemapPatchKeys =
        {
            "free_camera_keyboard_forward_q_hook",
            "free_camera_keyboard_backward_q_hook",
            "free_camera_keyboard_strafe_left_q_hook",
            "free_camera_keyboard_strafe_right_q_hook",
            "free_camera_keyboard_yaw_left_q_hook",
            "free_camera_keyboard_yaw_right_q_hook",
            "free_camera_keyboard_pitch_up_q_hook",
            "free_camera_keyboard_pitch_down_q_hook",
        };
        private const string LocalMultiplayerProbeLevelId = "850";
        private const int CopiedGameLivenessPollSeconds = 3;
        private const string CopiedGameEndedLaunchStatus =
            "The copied game is no longer running. It was closed from the game itself, not from here.";
        private const string CopiedGameEndedOperationLog =
            "The copied game closed on its own, so this page is ready again.\n" +
            "Your safe copy folder is untouched and still there. You can launch it again whenever you like.";
        private const int DefaultMouseSensitivityPresetIndex = 0;
        private const uint EnhancedCopyScreenShape = 1;
        private const int NoCreateMusicSwapPresetIndex = 0;
        private const int NoAdminLevelPresetIndex = 0;
        private static readonly float[] s_mouseLookSensitivityPresets =
        {
            GameProfileControlOptionsService.MinimumMouseLookSensitivity,
            GameProfileControlOptionsService.BalancedMouseLookSensitivity,
            GameProfileControlOptionsService.SharperMouseLookSensitivity,
            GameProfileControlOptionsService.FastMouseLookSensitivity,
        };
        private static readonly AdminLevelPreset[] s_adminLevelPresets =
        {
            new("100", PatchBenchLaunchPresetText.BuildAdminLevelPresetTrainingWorld100StatusMessage()),
            new("800", PatchBenchLaunchPresetText.BuildAdminLevelPresetFinalWorld800StatusMessage()),
            new("850", PatchBenchLaunchPresetText.BuildAdminLevelPresetLocalMultiplayerWorld850StatusMessage()),
            new("851", PatchBenchLaunchPresetText.BuildAdminLevelPresetLocalMultiplayerWorld851StatusMessage()),
        };
        private sealed record AdminLevelPreset(string LevelId, string StatusMessage);
        private enum LaunchPresetChoice
        {
            None,
            QuietCapture,
            ControlBaseline,
            ControlSharpened,
            ControlConfig2,
            ControlConfig3,
            ControlConfig4,
        }
        private static readonly LaunchPresetChoice[] s_namedLaunchPresetChoices =
        {
            LaunchPresetChoice.QuietCapture,
            LaunchPresetChoice.ControlBaseline,
            LaunchPresetChoice.ControlSharpened,
            LaunchPresetChoice.ControlConfig2,
            LaunchPresetChoice.ControlConfig3,
            LaunchPresetChoice.ControlConfig4,
        };

        private sealed record LaunchPresetSelection(
            bool SkipFmv,
            bool NoMusic,
            bool NoSound,
            bool ShowDebugTrace,
            string LevelId,
            int ControllerConfigurationIndex,
            bool PersistControllerConfig,
            bool SharpenMouseLook,
            int MouseSensitivityPresetIndex,
            bool InvertWalkerY,
            bool InvertFlightY,
            string StatusMessage);

        private readonly List<BinaryPatchItemModel> _allPatchItems;
        private readonly HashSet<string> _requiredCompatibilityKeys;
        private readonly List<BinaryPatchGroupModel> _patchGroups;
        private string? _verifiedSignature;
        private string? _lastCopiedProfileRoot;
        private string? _lastCopiedProfileContentSignature;
        private string? _lastCopiedProfileCreateMusicSwapPresetId;
        private GameProfileMusicReplacementResult? _lastMusicReplacementResult;
        private GameProfileManagedProcess? _managedCopiedProfileProcess;
        private readonly DispatcherTimer _copiedGameLivenessTimer;
        private bool _isPopulatingResolutionChoices;
        private bool _isCheckingCopiedGameLiveness;
        private bool _isLoadingSourcePath;
        private bool _isAwaitingCopiedProfileConfirmation;
        private bool _isPreparingCopiedProfile;
        private bool _isLaunchingCopiedProfile;
        private bool _isStoppingCopiedProfile;
        private bool _isStagingMusicReplacement;
        private bool _isRestoringMusicReplacement;
        private bool _isApplyingLaunchPreset;
        private LaunchPresetChoice _selectedLaunchPresetChoice = LaunchPresetChoice.None;

        public BinaryPatchesPage()
        {
            IReadOnlyList<string> defaultProfileKeys = BinaryPatchPlanBuilder.BuildSafeCopyProfilePatchKeys(BinaryPatchPlanBuilder.CompatibilityProfileId);
            _requiredCompatibilityKeys = defaultProfileKeys.ToHashSet(StringComparer.OrdinalIgnoreCase);

            _allPatchItems = BinaryPatchPlanBuilder.GetVisibleSpecs()
                .Select(spec => new BinaryPatchItemModel(spec)
                {
                    IsSelected = defaultProfileKeys.Contains(spec.Key, StringComparer.OrdinalIgnoreCase)
                })
                .ToList();
            EnsureRequiredCompatibilitySelected();
            _patchGroups = PatchBenchPatchGroups.Build(_allPatchItems);

            InitializeComponent();
            PatchBenchMusicTargetFileName.Text = "BEA_01(Master).ogg";
            PatchBenchAdminLevelPresetComboBox.SelectedIndex = NoAdminLevelPresetIndex;
            PatchBenchCopiedControllerConfigComboBox.SelectedIndex = 0;
            PatchBenchMouseSensitivityPresetComboBox.SelectedIndex = DefaultMouseSensitivityPresetIndex;
            PatchBenchCreateMusicSwapPresetComboBox.SelectedIndex = NoCreateMusicSwapPresetIndex;
            PatchGroupsItemsControl.ItemsSource = _patchGroups;
            InitializePatchLabInspector();
            InitializeResolutionChoices();
            ApplyProfileControlDefaults(BinaryPatchPlanBuilder.GetSafeCopyProfilePreset(BinaryPatchPlanBuilder.CompatibilityProfileId));

            OperationLogTextBox.Text =
                "Windowed & Mods patches and plays a copy of your game. Your installed game is left alone unless you choose to patch it, and that backs up your original first.\n" +
                "Ready.";
            LoadSourcePathFromConfig();
            RestoreTrackedSafeGameCopyProcess();
            UpdateControlState();

            // The copied game can end on its own - the player quits from the game's own
            // menu, or it crashes - and nothing tells this page about it. Poll instead, so
            // the page stops believing a copy is running the moment it is not.
            _copiedGameLivenessTimer = new DispatcherTimer
            {
                Interval = TimeSpan.FromSeconds(CopiedGameLivenessPollSeconds),
            };
            _copiedGameLivenessTimer.Tick += CopiedGameLivenessTimer_Tick;
            Loaded += BinaryPatchesPage_Loaded;
            Unloaded += BinaryPatchesPage_Unloaded;
        }

        private async void BinaryPatchesPage_Loaded(object sender, RoutedEventArgs e)
        {
            // Coming back to the page is the other moment a stale record shows up: the
            // copied game may have ended while the user was somewhere else in the app.
            RefreshCopiedGameLiveness();
            _copiedGameLivenessTimer.Start();

            // The set of copies can change from the CLI, from Explorer, or from another
            // window, so it is read on arrival rather than only after this page makes one.
            await RefreshSafeCopyManagerAsync();
        }

        private void BinaryPatchesPage_Unloaded(object sender, RoutedEventArgs e)
        {
            _copiedGameLivenessTimer.Stop();
        }

        private void CopiedGameLivenessTimer_Tick(object? sender, object e)
        {
            RefreshCopiedGameLiveness();
        }

        /// <summary>
        /// Forgets any tracked safe-copy process that is no longer running, and puts the
        /// page back into a usable state when the one this page launched has ended.
        ///
        /// Liveness itself is decided in AppCore, which requires the process id, its start
        /// time, and its main module path to all still match the managed record; a process
        /// id on its own is never enough because Windows recycles them. Nothing here closes
        /// a process, and the safe copy folder is never deleted.
        /// </summary>
        private void RefreshCopiedGameLiveness()
        {
            // A launch or stop already owns the record while it is in flight; let it finish.
            if (_isCheckingCopiedGameLiveness || _isLaunchingCopiedProfile || _isStoppingCopiedProfile)
            {
                return;
            }

            _isCheckingCopiedGameLiveness = true;
            try
            {
                IReadOnlyList<GameProfileRegisteredProcess> ended = App.SafeGameCopyProcesses.PruneDeadLeases();
                if (_managedCopiedProfileProcess is null ||
                    !ended.Any(row => row.Process.ProcessId == _managedCopiedProfileProcess.ProcessId))
                {
                    return;
                }

                _managedCopiedProfileProcess = null;

                // Re-enable the workflow and refresh the Launch/Stop buttons first:
                // UpdateControlState rewrites the launch status line itself, so the message
                // about the copied game ending has to be written after it, not before.
                UpdateControlState();
                PatchBenchCopiedProfileLaunchStatus.Text = CopiedGameEndedLaunchStatus;
                OperationLogTextBox.Text = CopiedGameEndedOperationLog;
                AppStatusService.SetStatus("Windowed & Mods: copied game is no longer running");
            }
            catch (Exception ex) when (IsUserFacingOperationException(ex))
            {
                OperationLogTextBox.Text = PatchBenchSafeCopyOutcomeText.DescribeCaughtFailure("check whether the copied game is still running");
            }
            finally
            {
                _isCheckingCopiedGameLiveness = false;
            }
        }

        private IEnumerable<BinaryPatchItemModel> AllItems => _allPatchItems;

        private IEnumerable<string> GetVisibleSelectedKeys()
        {
            return AllItems.Where(item => item.IsSelected).Select(item => item.Spec.Key);
        }

        private void SelectOnlyKeys(IEnumerable<string> keys)
        {
            var selected = keys.ToHashSet(StringComparer.OrdinalIgnoreCase);
            selected.UnionWith(_requiredCompatibilityKeys);
            foreach (BinaryPatchItemModel item in _allPatchItems)
            {
                item.IsSelected = selected.Contains(item.Spec.Key);
            }

            InvalidateVerification();
            UpdateControlState();
        }

        private void EnsureRequiredCompatibilitySelected()
        {
            foreach (BinaryPatchItemModel item in _allPatchItems)
            {
                if (_requiredCompatibilityKeys.Contains(item.Spec.Key))
                {
                    item.IsSelected = true;
                }
            }
        }

        private bool LoadSourcePathFromConfig()
        {
            string? gameDir = AppConfig.Load().GetGameDirOrDetect(persistDetection: true);
            if (string.IsNullOrWhiteSpace(gameDir))
            {
                return false;
            }

            string? candidate = ResolveGameExecutablePath(gameDir);
            if (!string.IsNullOrWhiteSpace(candidate))
            {
                SetSourceExecutablePath(candidate);
                return true;
            }

            return false;
        }

        private void InvalidateVerification()
        {
            _verifiedSignature = null;
        }

        private void UpdateControlState()
        {
            EnsureRequiredCompatibilitySelected();
            string exePath = (ExePathTextBox.Text ?? string.Empty).Trim();
            string sourcePath = (SourceExePathTextBox.Text ?? string.Empty).Trim();
            bool hasSourceExe = IsBattleEngineExecutableSourcePath(sourcePath) && File.Exists(sourcePath);
            bool hasWorkingCopy = IsUsableWorkingCopy(exePath);
            string[] visibleSelectedKeys = GetVisibleSelectedKeys().ToArray();
            bool hasSelected = visibleSelectedKeys.Length > 0;
            bool verifiedCurrent = string.Equals(
                _verifiedSignature,
                BinaryPatchPlanBuilder.BuildSelectionSignature(exePath, visibleSelectedKeys),
                StringComparison.Ordinal);

            CreateWorkingCopyButton.IsEnabled = hasSourceExe;
            VerifyButton.IsEnabled = hasWorkingCopy && hasSelected;
            ApplyButton.IsEnabled = hasWorkingCopy && hasSelected && verifiedCurrent;
            RestoreButton.IsEnabled = hasWorkingCopy && File.Exists(BinaryPatchEngine.BuildBackupPath(exePath));
            bool copiedProfileContentMatchesCurrent = IsCopiedProfileContentCurrent(sourcePath, visibleSelectedKeys);
            bool copiedProfileHasLaunchPlan = TryBuildCopiedProfileLaunchPlan(
                _lastCopiedProfileRoot,
                out GameProfileLaunchPlan? copiedProfileLaunchPlan,
                out string? copiedProfileLaunchError);
            bool hasLaunchableCopiedProfile =
                _managedCopiedProfileProcess is null &&
                !_isPreparingCopiedProfile &&
                !_isLaunchingCopiedProfile &&
                !_isStoppingCopiedProfile &&
                copiedProfileContentMatchesCurrent &&
                copiedProfileHasLaunchPlan;
            bool hasSafeCopyForMusic =
                _managedCopiedProfileProcess is null &&
                !_isPreparingCopiedProfile &&
                !_isLaunchingCopiedProfile &&
                !_isStoppingCopiedProfile &&
                !_isStagingMusicReplacement &&
                !_isRestoringMusicReplacement &&
                copiedProfileContentMatchesCurrent &&
                copiedProfileHasLaunchPlan;
            bool canRestoreMusicReplacement =
                _managedCopiedProfileProcess is null &&
                !_isPreparingCopiedProfile &&
                !_isLaunchingCopiedProfile &&
                !_isStoppingCopiedProfile &&
                !_isStagingMusicReplacement &&
                !_isRestoringMusicReplacement &&
                HasMusicReplacementManifest(_lastCopiedProfileRoot);
            bool hasActiveMusicReplacementManifest = canRestoreMusicReplacement;
            bool hasMusicReplacementInputs =
                !string.IsNullOrWhiteSpace(PatchBenchMusicTargetFileName.Text) &&
                !string.IsNullOrWhiteSpace(PatchBenchMusicReplacementPath.Text);
            bool hasCopiedTrackSwapInputs =
                PatchBenchMusicTargetTrackComboBox.SelectedItem is string targetTrack &&
                PatchBenchMusicReplacementTrackComboBox.SelectedItem is string replacementTrack &&
                !string.Equals(targetTrack, replacementTrack, StringComparison.OrdinalIgnoreCase);
            PatchBenchSafeCopySelectionReadinessState readiness = BuildSafeCopySelectionReadiness();

            PatchBenchPrepareCopiedProfileButton.IsEnabled = readiness.CanCreate;
            PatchBenchIncludeSavegamesOption.IsEnabled = PatchBenchPrepareCopiedProfileButton.IsEnabled;
            PatchBenchLevel100TextModOption.IsEnabled = PatchBenchPrepareCopiedProfileButton.IsEnabled;
            PatchBenchLevel100EarlyFlightModOption.IsEnabled = PatchBenchPrepareCopiedProfileButton.IsEnabled;
            PatchBenchTopCreateSafeCopyButton.IsEnabled = readiness.CanCreate;
            PatchBenchSafeCopySelectionReadiness.Text = readiness.Status;
            AutomationProperties.SetName(PatchBenchSafeCopySelectionReadiness, readiness.Status);
            uint? selectedControllerConfig = GetSelectedControllerConfigurationPreset();
            if (!selectedControllerConfig.HasValue && PatchBenchPersistControllerConfigOption.IsChecked == true)
            {
                PatchBenchPersistControllerConfigOption.IsChecked = false;
            }

            PatchBenchPersistControllerConfigOption.IsEnabled = PatchBenchPrepareCopiedProfileButton.IsEnabled && selectedControllerConfig.HasValue;
            PatchBenchAdminLevelPresetComboBox.IsEnabled = PatchBenchPrepareCopiedProfileButton.IsEnabled;
            PatchBenchMouseSensitivityPresetComboBox.IsEnabled = PatchBenchPrepareCopiedProfileButton.IsEnabled && PatchBenchSharpenMouseLookOption.IsChecked == true;
            PatchBenchInvertWalkerYOption.IsEnabled = PatchBenchPrepareCopiedProfileButton.IsEnabled;
            PatchBenchInvertFlightYOption.IsEnabled = PatchBenchPrepareCopiedProfileButton.IsEnabled;
            PatchBenchCreateMusicSwapPresetComboBox.IsEnabled = PatchBenchPrepareCopiedProfileButton.IsEnabled;

            UpdateInstalledGameState();
            PatchBenchLaunchCopiedProfileButton.IsEnabled = hasLaunchableCopiedProfile;
            PatchBenchTopPlaySafeCopyButton.IsEnabled = PatchBenchLaunchCopiedProfileButton.IsEnabled;
            PatchBenchStopCopiedProfileButton.IsEnabled = _managedCopiedProfileProcess is not null && !_isStoppingCopiedProfile;
            UpdateSafeCopyBusyState();
            PatchBenchMusicSwapBea02ForBea01PresetButton.IsEnabled = hasSafeCopyForMusic && !hasActiveMusicReplacementManifest;
            PatchBenchMusicSwapBea01ForBea02PresetButton.IsEnabled = hasSafeCopyForMusic && !hasActiveMusicReplacementManifest;
            PatchBenchMusicSwapBea02ForBea04PresetButton.IsEnabled = hasSafeCopyForMusic && !hasActiveMusicReplacementManifest;
            PatchBenchStageCopiedTrackSwapButton.IsEnabled = hasSafeCopyForMusic && !hasActiveMusicReplacementManifest && hasCopiedTrackSwapInputs;
            PatchBenchStageMusicReplacementButton.IsEnabled = hasSafeCopyForMusic && !hasActiveMusicReplacementManifest && hasMusicReplacementInputs;
            PatchBenchRestoreMusicReplacementButton.IsEnabled = canRestoreMusicReplacement;
            SourceExeSummaryTextBlock.Text = BuildSourceExecutableSummary(sourcePath);
            PatchBenchSafeCopySourceStatus.Text = BuildSafeCopySourceStatus(sourcePath);
            WorkingCopySummaryTextBlock.Text = BuildWorkingCopySummary(exePath);
            string? selectedProfileId = MatchSelectableSafeCopyProfileId(visibleSelectedKeys);
            bool isModernGraphicsOnly = SetEquals(
                visibleSelectedKeys,
                _requiredCompatibilityKeys.Concat(s_modernGraphicsKeys).ToArray());
            SafeCopyProfilePreset? selectedProfilePreset = string.IsNullOrWhiteSpace(selectedProfileId)
                ? null
                : BinaryPatchPlanBuilder.GetSafeCopyProfilePreset(selectedProfileId);
            var selectedProfileTextState = new PatchBenchSelectedProfileTextState(
                visibleSelectedKeys.Length,
                selectedProfilePreset,
                isModernGraphicsOnly);
            PatchBenchSelectedProfileStatus.Text = PatchBenchSelectedProfileText.BuildStatus(
                selectedProfileTextState);
            AutomationProperties.SetName(PatchBenchSelectedProfileStatus, PatchBenchSelectedProfileStatus.Text);
            PatchBenchProfileCatalogStatus.Text = BuildSafeCopyProfileCatalogStatus();
            PatchBenchSelectedProfileDetails.Text = PatchBenchSelectedProfileText.BuildDetails(
                selectedProfileTextState);
            PatchBenchPlayerModsSelectionStatus.Text = PatchBenchSelectedProfileText.BuildPlayerModsStatus(
                visibleSelectedKeys.Contains("version_overlay_use_patched_format_pointer", StringComparer.OrdinalIgnoreCase),
                visibleSelectedKeys.Contains("goodies_gallery_display_unlock", StringComparer.OrdinalIgnoreCase),
                PatchBenchLevel100TextModOption.IsChecked == true,
                PatchBenchLevel100EarlyFlightModOption.IsChecked == true);
            AutomationProperties.SetName(PatchBenchPlayerModsSelectionStatus, PatchBenchPlayerModsSelectionStatus.Text);
            PatchBenchLabSelectionStatus.Text = PatchBenchLabCreationInputText.BuildStatus(
                BuildLabCreationInputState());
            AutomationProperties.SetName(PatchBenchLabSelectionStatus, PatchBenchLabSelectionStatus.Text);
            UpdateChoiceVisualState(visibleSelectedKeys);
            UpdateLaunchPresetVisualState();

            SelectionSummaryTextBlock.Text =
                PatchBenchSelectedProfileText.BuildAdvancedCopySelectionSummary(selectedProfileTextState);

            WorkflowHintTextBlock.Text = !hasSourceExe
                ? "Select BEA.exe or BEA.exe.original.backup as a read-only source first."
                : !hasWorkingCopy
                    ? "Create a BEA.exe-only copy before verification or patching."
                : !hasSelected
                    ? "Choose at least one patch to continue."
                    : verifiedCurrent
                        ? "BEA.exe-only copy is verified and ready for patching."
                        : "Verify the BEA.exe-only copy after any file or selection change.";

            UpdateCopiedProfileLaunchReadiness(
                copiedProfileContentMatchesCurrent,
                copiedProfileHasLaunchPlan,
                copiedProfileLaunchPlan,
                copiedProfileLaunchError);
        }

        private PatchBenchSafeCopySelectionReadinessState BuildSafeCopySelectionReadiness()
        {
            EnsureRequiredCompatibilitySelected();
            string[] visibleSelectedKeys = GetVisibleSelectedKeys().ToArray();
            string sourcePath = (SourceExePathTextBox.Text ?? string.Empty).Trim();
            bool hasSourceExecutable = IsBattleEngineExecutableSourcePath(sourcePath) && File.Exists(sourcePath);
            bool isBusy =
                _managedCopiedProfileProcess is not null ||
                _isPreparingCopiedProfile ||
                _isLaunchingCopiedProfile ||
                _isStoppingCopiedProfile ||
                _isStagingMusicReplacement ||
                _isRestoringMusicReplacement;
            string? validationError = BinaryPatchPlanBuilder.ValidateVisibleSelection(visibleSelectedKeys);
            int optionalPatchCount = visibleSelectedKeys.Count(key =>
                !_requiredCompatibilityKeys.Contains(key)) +
                (PatchBenchLevel100TextModOption.IsChecked == true ? 1 : 0) +
                (PatchBenchLevel100EarlyFlightModOption.IsChecked == true ? 1 : 0);

            return OnslaughtCareerEditor.WinUI.Helpers.PatchBenchSafeCopySelectionReadiness.Build(
                hasSourceExecutable,
                isBusy,
                validationError,
                optionalPatchCount);
        }

        private void UpdateChoiceVisualState(IReadOnlyCollection<string> selectedKeys)
        {
            string? profileId = MatchSelectableSafeCopyProfileId(selectedKeys);
            string? selectedMenuColorKey = selectedKeys.FirstOrDefault(IsFrontendColorPatchKey);
            PatchBenchMenuColorSelectionKind menuColorSelection = BuildMenuColorSelectionKind(selectedMenuColorKey);

            PatchBenchChoiceVisualState.ApplyPatchBenchChoiceStyles(
                new[]
                {
                    PatchBenchChoiceVisualState.Bind(PatchBenchWindowedPresetButton, "Reset to Enhanced Copy profile", "Selected: Enhanced Copy profile", string.Equals(profileId, BinaryPatchPlanBuilder.CompatibilityProfileId, StringComparison.OrdinalIgnoreCase)),
                    PatchBenchChoiceVisualState.Bind(PatchBenchStableDefaultsButton, "Legacy graphics-default recipe; Lab option, visible improvement is unproven", "Selected: legacy graphics-default Lab recipe; visible improvement is unproven", string.Equals(profileId, BinaryPatchPlanBuilder.RecommendedProfileId, StringComparison.OrdinalIgnoreCase)),
                    PatchBenchChoiceVisualState.Bind(PatchBenchEnhancedPreviewProfileButton, "Select retained legacy Enhanced Profile Preview Lab recipe", "Selected: retained legacy Enhanced Profile Preview Lab recipe", string.Equals(profileId, BinaryPatchPlanBuilder.EnhancedPreviewProfileId, StringComparison.OrdinalIgnoreCase)),
                    PatchBenchChoiceVisualState.Bind(PatchBenchClearSelectionButton, "Clear optional mods; safe copies still include Enhanced Copy", "Selected: no optional mod rows", SetEquals(selectedKeys, _requiredCompatibilityKeys)),
                    PatchBenchChoiceVisualState.Bind(PatchBenchModernGraphicsPresetButton, "Graphics flag rows only; adds the extra graphics flag rows", "Selected: graphics flag rows only", SetEquals(selectedKeys, _requiredCompatibilityKeys.Concat(s_modernGraphicsKeys).ToArray())),
                    PatchBenchChoiceVisualState.Bind(PatchBenchDebugCameraPreviewProfileButton, "Select experimental Debug Camera Preview Lab research recipe", "Selected: experimental Debug Camera Preview Lab research recipe", string.Equals(profileId, BinaryPatchPlanBuilder.DebugCameraPreviewProfileId, StringComparison.OrdinalIgnoreCase)),
                    PatchBenchChoiceVisualState.Bind(PatchBenchMenuColorRedButton, "Red margins for the frontend", "Selected: red frontend margins", string.Equals(selectedMenuColorKey, "frontend_clear_screen_dark_red", StringComparison.OrdinalIgnoreCase)),
                    PatchBenchChoiceVisualState.Bind(PatchBenchMenuColorGreenButton, "Green margins for the frontend", "Selected: green frontend margins", string.Equals(selectedMenuColorKey, "frontend_clear_screen_dark_green", StringComparison.OrdinalIgnoreCase)),
                    PatchBenchChoiceVisualState.Bind(PatchBenchMenuColorBlackButton, "Black margins for the frontend", "Selected: black frontend margins", string.Equals(selectedMenuColorKey, "frontend_clear_screen_black", StringComparison.OrdinalIgnoreCase)),
                    PatchBenchChoiceVisualState.Bind(PatchBenchMenuColorClearButton, "Clear margin color selection for the frontend", "Selected: no frontend margin color", selectedMenuColorKey is null),
                },
                Resources);
            PatchBenchMenuColorSelectionStatus.Text = PatchBenchMenuColorSelectionText.BuildStatus(menuColorSelection);
            AutomationProperties.SetName(PatchBenchMenuColorSelectionStatus, PatchBenchMenuColorSelectionStatus.Text);
        }

        private void UpdateLaunchPresetVisualState()
        {
            _selectedLaunchPresetChoice = ResolveMatchingLaunchPresetChoice();
            PatchBenchChoiceVisualState.ApplyPatchBenchChoiceStyles(
                new[]
                {
                    PatchBenchChoiceVisualState.Bind(PatchBenchQuietCaptureLaunchPresetButton, PatchBenchLaunchPresetText.BuildQuietCaptureChoiceState(_selectedLaunchPresetChoice == LaunchPresetChoice.QuietCapture)),
                    PatchBenchChoiceVisualState.Bind(PatchBenchControlBaselinePresetButton, PatchBenchLaunchPresetText.BuildControlBaselineChoiceState(_selectedLaunchPresetChoice == LaunchPresetChoice.ControlBaseline)),
                    PatchBenchChoiceVisualState.Bind(PatchBenchControlSharpenedPresetButton, PatchBenchLaunchPresetText.BuildControlSharpenedChoiceState(_selectedLaunchPresetChoice == LaunchPresetChoice.ControlSharpened)),
                    PatchBenchChoiceVisualState.Bind(PatchBenchControlConfig2PresetButton, PatchBenchLaunchPresetText.BuildControlConfig2ChoiceState(_selectedLaunchPresetChoice == LaunchPresetChoice.ControlConfig2)),
                    PatchBenchChoiceVisualState.Bind(PatchBenchControlConfig3PresetButton, PatchBenchLaunchPresetText.BuildControlConfig3ChoiceState(_selectedLaunchPresetChoice == LaunchPresetChoice.ControlConfig3)),
                    PatchBenchChoiceVisualState.Bind(PatchBenchControlConfig4PresetButton, PatchBenchLaunchPresetText.BuildControlConfig4ChoiceState(_selectedLaunchPresetChoice == LaunchPresetChoice.ControlConfig4)),
                },
                Resources);
        }

        private void ClearSelectedLaunchPresetChoiceForManualEdit()
        {
            if (_isApplyingLaunchPreset)
            {
                return;
            }

            _selectedLaunchPresetChoice = ResolveMatchingLaunchPresetChoice();
        }

        private LaunchPresetChoice ResolveMatchingLaunchPresetChoice()
        {
            foreach (LaunchPresetChoice choice in s_namedLaunchPresetChoices)
            {
                if (CurrentLaunchOptionsMatchPreset(choice))
                {
                    return choice;
                }
            }

            return LaunchPresetChoice.None;
        }

        private bool CurrentLaunchOptionsMatchPreset(LaunchPresetChoice choice)
        {
            return choice switch
            {
                LaunchPresetChoice.QuietCapture => CurrentLaunchOptionsMatch(
                    skipFmv: true,
                    noMusic: true,
                    noSound: false,
                    showDebugTrace: false,
                    levelId: string.Empty,
                    controllerConfigurationIndex: 0,
                    persistControllerConfig: false,
                    sharpenMouseLook: false,
                    mouseSensitivityPresetIndex: DefaultMouseSensitivityPresetIndex,
                    invertWalkerY: false,
                    invertFlightY: false),
                LaunchPresetChoice.ControlBaseline => CurrentLaunchOptionsMatch(
                    skipFmv: true,
                    noMusic: false,
                    noSound: false,
                    showDebugTrace: false,
                    levelId: string.Empty,
                    controllerConfigurationIndex: 1,
                    persistControllerConfig: true,
                    sharpenMouseLook: false,
                    mouseSensitivityPresetIndex: DefaultMouseSensitivityPresetIndex,
                    invertWalkerY: false,
                    invertFlightY: false),
                LaunchPresetChoice.ControlSharpened => CurrentLaunchOptionsMatch(
                    skipFmv: true,
                    noMusic: false,
                    noSound: false,
                    showDebugTrace: false,
                    levelId: string.Empty,
                    controllerConfigurationIndex: 1,
                    persistControllerConfig: true,
                    sharpenMouseLook: true,
                    mouseSensitivityPresetIndex: DefaultMouseSensitivityPresetIndex,
                    invertWalkerY: false,
                    invertFlightY: false),
                LaunchPresetChoice.ControlConfig2 => CurrentLaunchOptionsMatch(
                    skipFmv: true,
                    noMusic: false,
                    noSound: false,
                    showDebugTrace: false,
                    levelId: string.Empty,
                    controllerConfigurationIndex: 2,
                    persistControllerConfig: true,
                    sharpenMouseLook: false,
                    mouseSensitivityPresetIndex: DefaultMouseSensitivityPresetIndex,
                    invertWalkerY: false,
                    invertFlightY: false),
                LaunchPresetChoice.ControlConfig3 => CurrentLaunchOptionsMatch(
                    skipFmv: true,
                    noMusic: false,
                    noSound: false,
                    showDebugTrace: false,
                    levelId: string.Empty,
                    controllerConfigurationIndex: 3,
                    persistControllerConfig: true,
                    sharpenMouseLook: false,
                    mouseSensitivityPresetIndex: DefaultMouseSensitivityPresetIndex,
                    invertWalkerY: false,
                    invertFlightY: false),
                LaunchPresetChoice.ControlConfig4 => CurrentLaunchOptionsMatch(
                    skipFmv: true,
                    noMusic: false,
                    noSound: false,
                    showDebugTrace: false,
                    levelId: string.Empty,
                    controllerConfigurationIndex: 4,
                    persistControllerConfig: true,
                    sharpenMouseLook: false,
                    mouseSensitivityPresetIndex: DefaultMouseSensitivityPresetIndex,
                    invertWalkerY: false,
                    invertFlightY: false),
                _ => false,
            };
        }

        private bool CurrentLaunchOptionsMatch(
            bool skipFmv,
            bool noMusic,
            bool noSound,
            bool showDebugTrace,
            string levelId,
            int controllerConfigurationIndex,
            bool persistControllerConfig,
            bool sharpenMouseLook,
            int mouseSensitivityPresetIndex,
            bool invertWalkerY,
            bool invertFlightY)
        {
            return PatchBenchSkipFmvLaunchOption.IsChecked == skipFmv
                && PatchBenchNoMusicLaunchOption.IsChecked == noMusic
                && PatchBenchNoSoundLaunchOption.IsChecked == noSound
                && PatchBenchShowDebugTraceLaunchOption.IsChecked == showDebugTrace
                && string.Equals((PatchBenchLevelLaunchOption.Text ?? string.Empty).Trim(), levelId, StringComparison.Ordinal)
                && PatchBenchCopiedControllerConfigComboBox.SelectedIndex == controllerConfigurationIndex
                && PatchBenchPersistControllerConfigOption.IsChecked == persistControllerConfig
                && PatchBenchSharpenMouseLookOption.IsChecked == sharpenMouseLook
                && PatchBenchMouseSensitivityPresetComboBox.SelectedIndex == mouseSensitivityPresetIndex
                && PatchBenchInvertWalkerYOption.IsChecked == invertWalkerY
                && PatchBenchInvertFlightYOption.IsChecked == invertFlightY;
        }

        private bool IsLaunchPresetOwnedCheckBox(object sender)
        {
            return ReferenceEquals(sender, PatchBenchSkipFmvLaunchOption)
                || ReferenceEquals(sender, PatchBenchNoMusicLaunchOption)
                || ReferenceEquals(sender, PatchBenchNoSoundLaunchOption)
                || ReferenceEquals(sender, PatchBenchShowDebugTraceLaunchOption)
                || ReferenceEquals(sender, PatchBenchPersistControllerConfigOption)
                || ReferenceEquals(sender, PatchBenchSharpenMouseLookOption)
                || ReferenceEquals(sender, PatchBenchInvertWalkerYOption)
                || ReferenceEquals(sender, PatchBenchInvertFlightYOption);
        }

        private bool IsLaunchPresetOwnedTextBox(object sender)
        {
            return ReferenceEquals(sender, PatchBenchLevelLaunchOption);
        }

        private bool IsLaunchPresetOwnedComboBox(object sender)
        {
            return ReferenceEquals(sender, PatchBenchCopiedControllerConfigComboBox)
                || ReferenceEquals(sender, PatchBenchMouseSensitivityPresetComboBox);
        }

        private static PatchBenchMenuColorSelectionKind BuildMenuColorSelectionKind(string? selectedKey)
        {
            if (string.Equals(selectedKey, "frontend_clear_screen_dark_red", StringComparison.OrdinalIgnoreCase))
            {
                return PatchBenchMenuColorSelectionKind.Red;
            }

            if (string.Equals(selectedKey, "frontend_clear_screen_dark_green", StringComparison.OrdinalIgnoreCase))
            {
                return PatchBenchMenuColorSelectionKind.Green;
            }

            return string.Equals(selectedKey, "frontend_clear_screen_black", StringComparison.OrdinalIgnoreCase)
                ? PatchBenchMenuColorSelectionKind.Black
                : PatchBenchMenuColorSelectionKind.None;
        }


        private void PatchCheckBox_Changed(object sender, RoutedEventArgs e)
        {
            if (sender is CheckBox { IsChecked: true, DataContext: BinaryPatchItemModel changedItem } &&
                IsFrontendColorPatchKey(changedItem.Spec.Key))
            {
                foreach (BinaryPatchItemModel item in _allPatchItems)
                {
                    if (!string.Equals(item.Spec.Key, changedItem.Spec.Key, StringComparison.OrdinalIgnoreCase) &&
                        IsFrontendColorPatchKey(item.Spec.Key))
                    {
                        item.IsSelected = false;
                    }
                }
            }
            else if (sender is CheckBox { IsChecked: true, DataContext: BinaryPatchItemModel changedItemWithQRemap } &&
                IsFreeCameraKeyboardQRemapPatchKey(changedItemWithQRemap.Spec.Key))
            {
                foreach (BinaryPatchItemModel item in _allPatchItems)
                {
                    if (!string.Equals(item.Spec.Key, changedItemWithQRemap.Spec.Key, StringComparison.OrdinalIgnoreCase) &&
                        IsFreeCameraKeyboardQRemapPatchKey(item.Spec.Key))
                    {
                        item.IsSelected = false;
                    }
                }
            }

            EnsureRequiredCompatibilitySelected();
            InvalidateVerification();
            UpdateControlState();
        }

        private void WindowedPresetButton_Click(object sender, RoutedEventArgs e)
        {
            PatchBenchLevel100TextModOption.IsChecked = false;
            PatchBenchLevel100EarlyFlightModOption.IsChecked = false;
            ApplySafeCopyProfilePreset(BinaryPatchPlanBuilder.CompatibilityProfileId);
            AppStatusService.SetStatus("Windowed & Mods: Enhanced Copy profile selected");
        }

        private void ModernGraphicsPresetButton_Click(object sender, RoutedEventArgs e)
        {
            SelectOnlyKeys(s_modernGraphicsKeys);
            AppStatusService.SetStatus("Windowed & Mods: graphics flag rows selected");
        }

        private void StableDefaultsButton_Click(object sender, RoutedEventArgs e)
        {
            ApplySafeCopyProfilePreset(BinaryPatchPlanBuilder.RecommendedProfileId);
            AppStatusService.SetStatus("Windowed & Mods: Windowed + Graphics Defaults profile selected");
        }

        private void EnhancedPreviewPresetButton_Click(object sender, RoutedEventArgs e)
        {
            ApplySafeCopyProfilePreset(BinaryPatchPlanBuilder.EnhancedPreviewProfileId);
            AppStatusService.SetStatus("Windowed & Mods: Enhanced Profile Preview profile selected");
        }

        private void DebugCameraPreviewPresetButton_Click(object sender, RoutedEventArgs e)
        {
            ApplySafeCopyProfilePreset(BinaryPatchPlanBuilder.DebugCameraPreviewProfileId);
            AppStatusService.SetStatus("Windowed & Mods: Debug Camera Preview profile selected");
        }

        private void ApplySafeCopyProfilePreset(string profileId)
        {
            SafeCopyProfilePreset preset = BinaryPatchPlanBuilder.GetSafeCopyProfilePreset(profileId);
            SelectOnlyKeys(preset.PatchKeys);
            ApplyProfileControlDefaults(preset);
            RefreshCopiedProfileLaunchPlanPreview();
            UpdateControlState();
        }

        private void ApplyProfileControlDefaults(SafeCopyProfilePreset preset)
        {
            PatchBenchCopiedControllerConfigComboBox.SelectedIndex = preset.DefaultControllerConfiguration ?? 0;
            PatchBenchPersistControllerConfigOption.IsChecked = preset.DefaultPersistControllerConfigInOptions;
            PatchBenchSharpenMouseLookOption.IsChecked = preset.DefaultMouseLookSensitivity.HasValue;
            int mousePresetIndex = preset.DefaultMouseLookSensitivity.HasValue
                ? Array.FindIndex(s_mouseLookSensitivityPresets, value =>
                    Math.Abs(value - preset.DefaultMouseLookSensitivity.Value) < 0.0001f)
                : DefaultMouseSensitivityPresetIndex;
            PatchBenchMouseSensitivityPresetComboBox.SelectedIndex = mousePresetIndex >= 0
                ? mousePresetIndex
                : DefaultMouseSensitivityPresetIndex;
            PatchBenchInvertWalkerYOption.IsChecked = false;
            PatchBenchInvertFlightYOption.IsChecked = false;
        }

        private void ClearSelectionButton_Click(object sender, RoutedEventArgs e)
        {
            PatchBenchLevel100TextModOption.IsChecked = false;
            PatchBenchLevel100EarlyFlightModOption.IsChecked = false;
            SelectOnlyKeys(Array.Empty<string>());
            AppStatusService.SetStatus("Windowed & Mods: optional mods cleared");
        }

        private void MenuColorRedButton_Click(object sender, RoutedEventArgs e)
        {
            SelectFrontendColorPatch("frontend_clear_screen_dark_red", "red frontend margins selected");
        }

        private void MenuColorGreenButton_Click(object sender, RoutedEventArgs e)
        {
            SelectFrontendColorPatch("frontend_clear_screen_dark_green", "green frontend margins selected");
        }

        private void MenuColorBlackButton_Click(object sender, RoutedEventArgs e)
        {
            SelectFrontendColorPatch("frontend_clear_screen_black", "black frontend margins selected");
        }

        private void MenuColorClearButton_Click(object sender, RoutedEventArgs e)
        {
            SelectFrontendColorPatch(null, "frontend clear-screen color selection cleared");
        }

        private void SelectFrontendColorPatch(string? selectedKey, string statusMessage)
        {
            foreach (BinaryPatchItemModel item in _allPatchItems)
            {
                if (IsFrontendColorPatchKey(item.Spec.Key))
                {
                    item.IsSelected = selectedKey is not null &&
                        string.Equals(item.Spec.Key, selectedKey, StringComparison.OrdinalIgnoreCase);
                }
            }

            InvalidateVerification();
            UpdateControlState();
            AppStatusService.SetStatus($"Windowed & Mods: {statusMessage}");
        }

        private void AddVersionMarkerButton_Click(object sender, RoutedEventArgs e)
        {
            SetVisiblePatchRowSelected(
                "version_overlay_use_patched_format_pointer",
                isSelected: true,
                "PATCHED title marker row selected");
        }

        private void ClearVersionMarkerButton_Click(object sender, RoutedEventArgs e)
        {
            SetVisiblePatchRowSelected(
                "version_overlay_use_patched_format_pointer",
                isSelected: false,
                "PATCHED title marker row cleared");
        }

        private void AddGoodiesPreviewButton_Click(object sender, RoutedEventArgs e)
        {
            SetVisiblePatchRowSelected(
                "goodies_gallery_display_unlock",
                isSelected: true,
                "Goodies display preview row selected");
        }

        private void ClearGoodiesPreviewButton_Click(object sender, RoutedEventArgs e)
        {
            SetVisiblePatchRowSelected(
                "goodies_gallery_display_unlock",
                isSelected: false,
                "Goodies display preview row cleared");
        }

        private void SetVisiblePatchRowSelected(string key, bool isSelected, string statusMessage)
        {
            BinaryPatchItemModel? item = _allPatchItems.FirstOrDefault(item =>
                string.Equals(item.Spec.Key, key, StringComparison.OrdinalIgnoreCase));
            if (item is null)
            {
                OperationLogTextBox.Text = PatchBenchSafeCopyOutcomeText.PatchRowUnavailable;
                AppStatusService.SetStatus("Windowed & Mods: quick pick unavailable");
                return;
            }

            item.IsSelected = isSelected;
            InvalidateVerification();
            UpdateControlState();
            AppStatusService.SetStatus($"Windowed & Mods: {statusMessage}");
        }

        /// <summary>
        /// The Lab's patch row inspector: a read-only view of every catalog row with
        /// its exact bytes, evidence, and risk boundary. Staging routes through the
        /// page's existing selection model - the same checkboxes, validation, and
        /// guarded safe-copy apply path - so the inspector itself never writes.
        /// </summary>
        private PatchLabCatalog? _patchLabCatalog;
        private IReadOnlyList<PatchLabRowModel> _patchLabRows = Array.Empty<PatchLabRowModel>();

        private void InitializePatchLabInspector()
        {
            try
            {
                _patchLabCatalog = PatchSurfaceInspector.Load();
                _patchLabRows = _patchLabCatalog.Rows.Select(row => new PatchLabRowModel(row)).ToArray();
            }
            catch (Exception)
            {
                // The inspector is optional depth on top of the working patch bench;
                // a load failure must never take selection or safe copies down.
                _patchLabCatalog = null;
                _patchLabRows = Array.Empty<PatchLabRowModel>();
                PatchLabInspectorStatus.Text = "The patch catalog could not be inspected right now. Safe-copy patching still works normally.";
            }

            PatchLabInspectorSearchBox.TextChanged += PatchLabInspectorSearchBox_TextChanged;
            ApplyPatchLabFilter();
        }

        private void PatchLabInspectorSearchBox_TextChanged(object sender, TextChangedEventArgs e)
        {
            ApplyPatchLabFilter();
        }

        private void ApplyPatchLabFilter()
        {
            if (_patchLabCatalog is null)
            {
                PatchLabInspectorList.ItemsSource = Array.Empty<PatchLabRowModel>();
                return;
            }

            string query = PatchLabInspectorSearchBox.Text ?? string.Empty;
            IReadOnlyList<PatchLabRow> filtered = PatchSurfaceInspector.FilterRows(_patchLabCatalog.Rows, query);
            PatchLabRowModel[] models = _patchLabRows
                .Where(model => filtered.Any(row => string.Equals(row.Key, model.Key, StringComparison.OrdinalIgnoreCase)))
                .ToArray();

            PatchLabInspectorList.ItemsSource = models;

            int hiddenCount = models.Count(model => model.Row.IsHiddenCompanion);
            string countText = $"Inspecting {_patchLabRows.Count} patch rows ({_patchLabCatalog.TotalRegions} byte regions)";
            if (_patchLabCatalog.UsingFallback)
            {
                countText += "; catalog prose unavailable, showing compiled row facts";
            }

            if (query.Trim().Length == 0 && models.Length == _patchLabRows.Count)
            {
                PatchLabInspectorStatus.Text =
                    $"{countText}. {models.Length} shown, including {hiddenCount} hidden companion row{(hiddenCount == 1 ? "" : "s")} applied automatically with their visible rows.";
            }
            else if (models.Length == 0)
            {
                PatchLabInspectorStatus.Text =
                    "No patch row matches that filter. Try another word, or clear the filter.";
            }
            else
            {
                PatchLabInspectorStatus.Text =
                    $"{countText}. {models.Length} row{(models.Length == 1 ? "" : "s")} match{(models.Length == 1 ? "es" : "")} your filter.";
            }
        }

        private void PatchLabStageButton_Click(object sender, RoutedEventArgs e)
        {
            if (sender is not Button { DataContext: PatchLabRowModel model })
            {
                return;
            }

            SetVisiblePatchRowSelected(
                model.Key,
                isSelected: !IsPatchRowSelected(model.Key),
                statusMessage: IsPatchRowSelected(model.Key)
                    ? $"{model.Title} removed from the patch selection"
                    : $"{model.Title} staged into the patch selection");
        }

        private bool IsPatchRowSelected(string key)
        {
            return _allPatchItems.Any(item =>
                string.Equals(item.Spec.Key, key, StringComparison.OrdinalIgnoreCase) && item.IsSelected);
        }

        private void LocalMultiplayerProbeButton_Click(object sender, RoutedEventArgs e)
        {
            _selectedLaunchPresetChoice = LaunchPresetChoice.None;
            ApplyLaunchPreset(new LaunchPresetSelection(
                SkipFmv: true,
                NoMusic: false,
                NoSound: false,
                ShowDebugTrace: false,
                LevelId: LocalMultiplayerProbeLevelId,
                ControllerConfigurationIndex: 0,
                PersistControllerConfig: false,
                SharpenMouseLook: false,
                MouseSensitivityPresetIndex: DefaultMouseSensitivityPresetIndex,
                InvertWalkerY: false,
                InvertFlightY: false,
                StatusMessage: PatchBenchLaunchPresetText.BuildLocalMultiplayerProbeStatusMessage()));
            PatchBenchOnlinePrepActionStatus.Text = "Local split-screen launch preset selected. Next: create a safe copy, then play that safe copy. This is not Host/Join or online play.";
            OperationLogTextBox.Text = "Local split-screen preset selected: -skipfmv -level 850. Create safe copy next, then launch that safe copy. No listener, invitation, remote input, or Host/Join control is enabled.";
        }

        private void UpdateSafeCopyBusyState()
        {
            string? status = null;
            if (_isAwaitingCopiedProfileConfirmation)
            {
                status = "Waiting for safe copy confirmation.";
            }
            else if (_isPreparingCopiedProfile)
            {
                status = "Creating safe copy. This can take a few minutes for a full game folder.";
            }
            else if (_isLaunchingCopiedProfile)
            {
                status = "Starting safe copy.";
            }
            else if (_isStoppingCopiedProfile)
            {
                status = "Stopping safe copy.";
            }

            bool isBusy = status is not null;
            PatchBenchSafeCopyBusyPanel.Visibility = isBusy ? Visibility.Visible : Visibility.Collapsed;
            PatchBenchSafeCopyBusyRing.IsActive = isBusy;
            PatchBenchSafeCopyBusyStatus.Text = status ?? "Safe copy operation in progress.";
        }

        private void AdminLevelPresetComboBox_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            if (_isApplyingLaunchPreset)
                return;

            int selectedIndex = PatchBenchAdminLevelPresetComboBox.SelectedIndex;
            if (selectedIndex < NoAdminLevelPresetIndex)
                return;

            if (selectedIndex == NoAdminLevelPresetIndex)
            {
                bool hadLevelArgument = !string.IsNullOrEmpty(PatchBenchLevelLaunchOption.Text);
                if (!hadLevelArgument && _selectedLaunchPresetChoice == LaunchPresetChoice.None)
                {
                    return;
                }

                ClearSelectedLaunchPresetChoiceForManualEdit();
                PatchBenchLevelLaunchOption.Text = string.Empty;
                RefreshCopiedProfileLaunchPlanPreview();
                UpdateControlState();
                if (hadLevelArgument)
                {
                    AppStatusService.SetStatus("Windowed & Mods: admin level launch option cleared");
                }
                return;
            }

            int presetIndex = selectedIndex - 1;
            if (presetIndex < 0 || presetIndex >= s_adminLevelPresets.Length)
                return;

            AdminLevelPreset preset = s_adminLevelPresets[presetIndex];
            ClearSelectedLaunchPresetChoiceForManualEdit();
            PatchBenchLevelLaunchOption.Text = preset.LevelId;
            RefreshCopiedProfileLaunchPlanPreview();
            UpdateControlState();
            AppStatusService.SetStatus($"Windowed & Mods: {preset.StatusMessage}");
        }

        private void QuietCaptureLaunchPresetButton_Click(object sender, RoutedEventArgs e)
        {
            ApplyLaunchPreset(LaunchPresetChoice.QuietCapture, new LaunchPresetSelection(
                SkipFmv: true,
                NoMusic: true,
                NoSound: false,
                ShowDebugTrace: false,
                LevelId: string.Empty,
                ControllerConfigurationIndex: 0,
                PersistControllerConfig: false,
                SharpenMouseLook: false,
                MouseSensitivityPresetIndex: DefaultMouseSensitivityPresetIndex,
                InvertWalkerY: false,
                InvertFlightY: false,
                StatusMessage: PatchBenchLaunchPresetText.BuildQuietCaptureStatusMessage()));
        }

        private void ControlBaselinePresetButton_Click(object sender, RoutedEventArgs e)
        {
            ApplyLaunchPreset(LaunchPresetChoice.ControlBaseline, new LaunchPresetSelection(
                SkipFmv: true,
                NoMusic: false,
                NoSound: false,
                ShowDebugTrace: false,
                LevelId: string.Empty,
                ControllerConfigurationIndex: 1,
                PersistControllerConfig: true,
                SharpenMouseLook: false,
                MouseSensitivityPresetIndex: DefaultMouseSensitivityPresetIndex,
                InvertWalkerY: false,
                InvertFlightY: false,
                StatusMessage: PatchBenchLaunchPresetText.BuildControlBaselineStatusMessage()));
        }

        private void ControlSharpenedPresetButton_Click(object sender, RoutedEventArgs e)
        {
            ApplyLaunchPreset(LaunchPresetChoice.ControlSharpened, new LaunchPresetSelection(
                SkipFmv: true,
                NoMusic: false,
                NoSound: false,
                ShowDebugTrace: false,
                LevelId: string.Empty,
                ControllerConfigurationIndex: 1,
                PersistControllerConfig: true,
                SharpenMouseLook: true,
                MouseSensitivityPresetIndex: DefaultMouseSensitivityPresetIndex,
                InvertWalkerY: false,
                InvertFlightY: false,
                StatusMessage: PatchBenchLaunchPresetText.BuildControlSharpenedStatusMessage()));
        }

        private void ControlConfig2PresetButton_Click(object sender, RoutedEventArgs e)
        {
            ApplyLaunchPreset(LaunchPresetChoice.ControlConfig2, BuildPersistedControlDiagnosticPreset(
                controllerConfigurationIndex: 2,
                statusMessage: PatchBenchLaunchPresetText.BuildControlConfig2StatusMessage()));
        }

        private void ControlConfig3PresetButton_Click(object sender, RoutedEventArgs e)
        {
            ApplyLaunchPreset(LaunchPresetChoice.ControlConfig3, BuildPersistedControlDiagnosticPreset(
                controllerConfigurationIndex: 3,
                statusMessage: PatchBenchLaunchPresetText.BuildControlConfig3StatusMessage()));
        }

        private void ControlConfig4PresetButton_Click(object sender, RoutedEventArgs e)
        {
            ApplyLaunchPreset(LaunchPresetChoice.ControlConfig4, BuildPersistedControlDiagnosticPreset(
                controllerConfigurationIndex: 4,
                statusMessage: PatchBenchLaunchPresetText.BuildControlConfig4StatusMessage()));
        }

        private static LaunchPresetSelection BuildPersistedControlDiagnosticPreset(int controllerConfigurationIndex, string statusMessage)
        {
            return new LaunchPresetSelection(
                SkipFmv: true,
                NoMusic: false,
                NoSound: false,
                ShowDebugTrace: false,
                LevelId: string.Empty,
                ControllerConfigurationIndex: controllerConfigurationIndex,
                PersistControllerConfig: true,
                SharpenMouseLook: false,
                MouseSensitivityPresetIndex: DefaultMouseSensitivityPresetIndex,
                InvertWalkerY: false,
                InvertFlightY: false,
                StatusMessage: statusMessage);
        }

        private void ClearLaunchOptionsButton_Click(object sender, RoutedEventArgs e)
        {
            _selectedLaunchPresetChoice = LaunchPresetChoice.None;
            ApplyLaunchPreset(new LaunchPresetSelection(
                SkipFmv: false,
                NoMusic: false,
                NoSound: false,
                ShowDebugTrace: false,
                LevelId: string.Empty,
                ControllerConfigurationIndex: 0,
                PersistControllerConfig: false,
                SharpenMouseLook: false,
                MouseSensitivityPresetIndex: DefaultMouseSensitivityPresetIndex,
                InvertWalkerY: false,
                InvertFlightY: false,
                StatusMessage: PatchBenchLaunchPresetText.BuildClearLaunchOptionsStatusMessage()));
        }

        private void ApplyLaunchPreset(LaunchPresetChoice selectedChoice, LaunchPresetSelection preset)
        {
            ApplyLaunchPreset(preset);
            _selectedLaunchPresetChoice = ResolveMatchingLaunchPresetChoice();
            UpdateLaunchPresetVisualState();

            // Every caller is a plain Click handler, so an escaping exception here would
            // take the whole app down over a preset button. Report the mismatch instead:
            // the controls are already whatever they are, and the highlighted preset above
            // now reflects that honestly.
            if (_selectedLaunchPresetChoice != selectedChoice)
            {
                OperationLogTextBox.Text =
                    "That launch preset did not fully apply, so no preset is shown as selected.\n" +
                    "The launch options below are still the ones that will be used. Set them yourself, or pick the preset again.";
                AppStatusService.SetStatus("Windowed & Mods: launch preset did not fully apply");
            }
        }

        private void ApplyLaunchPreset(LaunchPresetSelection preset)
        {
            bool wasApplyingLaunchPreset = _isApplyingLaunchPreset;
            _isApplyingLaunchPreset = true;
            try
            {
                PatchBenchSkipFmvLaunchOption.IsChecked = preset.SkipFmv;
                PatchBenchNoMusicLaunchOption.IsChecked = preset.NoMusic;
                PatchBenchNoSoundLaunchOption.IsChecked = preset.NoSound;
                PatchBenchShowDebugTraceLaunchOption.IsChecked = preset.ShowDebugTrace;
                PatchBenchLevelLaunchOption.Text = preset.LevelId;
                PatchBenchAdminLevelPresetComboBox.SelectedIndex = ResolveAdminLevelPresetIndex(preset.LevelId);
                PatchBenchCopiedControllerConfigComboBox.SelectedIndex = Math.Clamp(preset.ControllerConfigurationIndex, 0, 4);
                PatchBenchPersistControllerConfigOption.IsChecked = preset.PersistControllerConfig;
                PatchBenchSharpenMouseLookOption.IsChecked = preset.SharpenMouseLook;
                PatchBenchMouseSensitivityPresetComboBox.SelectedIndex = Math.Clamp(preset.MouseSensitivityPresetIndex, 0, s_mouseLookSensitivityPresets.Length - 1);
                PatchBenchInvertWalkerYOption.IsChecked = preset.InvertWalkerY;
                PatchBenchInvertFlightYOption.IsChecked = preset.InvertFlightY;
                RefreshCopiedProfileLaunchPlanPreview();
                UpdateControlState();
            }
            finally
            {
                _isApplyingLaunchPreset = wasApplyingLaunchPreset;
            }

            AppStatusService.SetStatus($"Windowed & Mods: {preset.StatusMessage}");
        }

        private void ExePathTextBox_TextChanged(object sender, TextChangedEventArgs e)
        {
            InvalidateVerification();
            UpdateControlState();
        }

        private void MusicReplacementInput_TextChanged(object sender, TextChangedEventArgs e)
        {
            UpdateControlState();
        }

        private void MusicTrackComboBox_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            if (PatchBenchMusicTargetTrackComboBox.SelectedItem is string targetTrack)
            {
                PatchBenchMusicTargetFileName.Text = targetTrack;
            }

            if (PatchBenchMusicReplacementTrackComboBox.SelectedItem is string replacementTrack &&
                !string.IsNullOrWhiteSpace(_lastCopiedProfileRoot))
            {
                PatchBenchMusicReplacementPath.Text = Path.Combine(_lastCopiedProfileRoot, "data", "Music", replacementTrack);
            }

            UpdateControlState();
        }

        private void LaunchOptionCheckBox_Changed(object sender, RoutedEventArgs e)
        {
            if (IsLaunchPresetOwnedCheckBox(sender))
            {
                ClearSelectedLaunchPresetChoiceForManualEdit();
            }

            RefreshCopiedProfileLaunchPlanPreview();
            UpdateControlState();
        }

        private void LaunchOptionTextBox_TextChanged(object sender, TextChangedEventArgs e)
        {
            if (!_isApplyingLaunchPreset && ReferenceEquals(sender, PatchBenchLevelLaunchOption))
            {
                SynchronizeAdminLevelPresetSelection(PatchBenchLevelLaunchOption.Text);
            }

            if (IsLaunchPresetOwnedTextBox(sender))
            {
                ClearSelectedLaunchPresetChoiceForManualEdit();
            }

            RefreshCopiedProfileLaunchPlanPreview();
            UpdateControlState();
        }

        private static int ResolveAdminLevelPresetIndex(string? levelId)
        {
            string normalizedLevelId = (levelId ?? string.Empty).Trim();
            for (int index = 0; index < s_adminLevelPresets.Length; index++)
            {
                if (string.Equals(s_adminLevelPresets[index].LevelId, normalizedLevelId, StringComparison.Ordinal))
                {
                    return index + 1;
                }
            }

            return NoAdminLevelPresetIndex;
        }

        private void SynchronizeAdminLevelPresetSelection(string? levelId)
        {
            int selectedIndex = ResolveAdminLevelPresetIndex(levelId);
            if (PatchBenchAdminLevelPresetComboBox.SelectedIndex == selectedIndex)
            {
                return;
            }

            bool wasApplyingLaunchPreset = _isApplyingLaunchPreset;
            _isApplyingLaunchPreset = true;
            try
            {
                PatchBenchAdminLevelPresetComboBox.SelectedIndex = selectedIndex;
            }
            finally
            {
                _isApplyingLaunchPreset = wasApplyingLaunchPreset;
            }
        }

        private void LaunchOptionComboBox_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            if (IsLaunchPresetOwnedComboBox(sender))
            {
                ClearSelectedLaunchPresetChoiceForManualEdit();
            }

            RefreshCopiedProfileLaunchPlanPreview();
            UpdateControlState();
        }

        private void SourceExePathTextBox_TextChanged(object sender, TextChangedEventArgs e)
        {

            if (!_isLoadingSourcePath)
            {
                ExePathTextBox.Text = string.Empty;
                ClearCopiedProfileLaunchState(clearManagedProcess: false);
            }

            InvalidateVerification();
            UpdateControlState();
        }

        private async void BrowseButton_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                if (App.MainWindowInstance is null)
                {
                    return;
                }

                string? path = await PickerInterop.PickFileAsync(App.MainWindowInstance, new[] { ".exe", "*" });
                if (!string.IsNullOrWhiteSpace(path))
                {
                    SetSourceExecutablePath(path);
                    AppStatusService.SetStatus("Windowed & Mods: source executable selected");
                }
            }
            catch (Exception ex) when (IsUserFacingOperationException(ex))
            {
                OperationLogTextBox.Text = PatchBenchSafeCopyOutcomeText.DescribeCaughtFailure("browse for BEA.exe");
                AppStatusService.SetStatus("Windowed & Mods: browse failed");
            }
        }

        private void UseGameDirButton_Click(object sender, RoutedEventArgs e)
        {
            if (LoadSourcePathFromConfig())
            {
                AppStatusService.SetStatus("Windowed & Mods: loaded BEA.exe from Settings");
                return;
            }

            OperationLogTextBox.Text = "No configured game folder with BEA.exe was found. Set the game folder in Settings or browse to BEA.exe.";
            AppStatusService.SetStatus("Windowed & Mods: no configured game folder found");
            UpdateControlState();
        }

        private void CreateWorkingCopyButton_Click(object sender, RoutedEventArgs e)
        {
            string sourcePath = (SourceExePathTextBox.Text ?? string.Empty).Trim();
            if (!IsBattleEngineExecutableSourcePath(sourcePath) || !File.Exists(sourcePath))
            {
                OperationLogTextBox.Text = "Select a valid source BEA.exe or BEA.exe.original.backup first.";
                AppStatusService.SetStatus("Windowed & Mods: missing source executable");
                UpdateControlState();
                return;
            }

            try
            {
                string validatedSourcePath = GameProfilePreflightService.ValidateExecutableSourceForWorkspaceCopy(sourcePath);
                string patchWorkspaceRoot = GetPatchWorkspaceRoot();
                string copyPath = GameProfilePreflightService.ValidateAppOwnedWorkspaceFileDestination(
                    BuildWorkingCopyPath(validatedSourcePath),
                    patchWorkspaceRoot,
                    "BEA.exe");
                Directory.CreateDirectory(Path.GetDirectoryName(copyPath)!);
                copyPath = GameProfilePreflightService.ValidateAppOwnedWorkspaceFileDestination(
                    copyPath,
                    patchWorkspaceRoot,
                    "BEA.exe");
                File.Copy(validatedSourcePath, copyPath, overwrite: false);
                ExePathTextBox.Text = copyPath;
                OperationLogTextBox.Text =
                    "BEA.exe-only copy created.\n" +
                    $"Source: {BuildSourceExecutableSummary(validatedSourcePath)}\n" +
                    $"Copy: {BuildWorkingCopySummary(copyPath)}\n" +
                    "Original executable stays unchanged. Verify the copy before applying patches.";
                AppStatusService.SetStatus("Windowed & Mods: BEA.exe-only copy ready");
            }
            catch (Exception)
            {
                OperationLogTextBox.Text = PatchBenchSafeCopyOutcomeText.DescribeCaughtFailure("create a BEA.exe-only copy");
                AppStatusService.SetStatus("Windowed & Mods: BEA.exe-only copy failed");
            }

            InvalidateVerification();
            UpdateControlState();
        }

        private void VerifyButton_Click(object sender, RoutedEventArgs e)
        {
            string exePath = (ExePathTextBox.Text ?? string.Empty).Trim();
            if (!IsUsableWorkingCopy(exePath))
            {
                OperationLogTextBox.Text = "Create a BEA.exe-only copy before verification.";
                AppStatusService.SetStatus("Windowed & Mods: BEA.exe-only copy required");
                UpdateControlState();
                return;
            }

            string? validationError = BinaryPatchPlanBuilder.ValidateVisibleSelection(GetVisibleSelectedKeys());
            if (!string.IsNullOrWhiteSpace(validationError))
            {
                OperationLogTextBox.Text = validationError;
                AppStatusService.SetStatus("Windowed & Mods: selection needs review");
                UpdateControlState();
                return;
            }

            var selected = BinaryPatchPlanBuilder.BuildSelectedSpecs(GetVisibleSelectedKeys());
            BinaryPatchTargetVerifyResult verify = BinaryPatchEngine.VerifyPatchTargetFile(BuildPatchTargetOptions(exePath), selected);

            OperationLogTextBox.Text = FormatPatchLogForUi(BinaryPatchEngine.RenderStateReport(exePath, verify.Rows.ToList(), verify.Message), exePath);
            _verifiedSignature = verify.Success
                ? BinaryPatchPlanBuilder.BuildSelectionSignature(exePath, GetVisibleSelectedKeys())
                : null;
            AppStatusService.SetStatus(verify.Success ? "Windowed & Mods: verification complete" : "Windowed & Mods: verification warning");
            UpdateControlState();
        }

        private async void ApplyButton_Click(object sender, RoutedEventArgs e)
        {
            string exePath = (ExePathTextBox.Text ?? string.Empty).Trim();
            if (!IsUsableWorkingCopy(exePath))
            {
                OperationLogTextBox.Text = "Create a BEA.exe-only copy before applying patches.";
                AppStatusService.SetStatus("Windowed & Mods: BEA.exe-only copy required");
                UpdateControlState();
                return;
            }

            string? currentSignature = BinaryPatchPlanBuilder.BuildSelectionSignature(exePath, GetVisibleSelectedKeys());
            if (!string.Equals(_verifiedSignature, currentSignature, StringComparison.Ordinal))
            {
                OperationLogTextBox.Text = "Verify the current selection before applying patches.";
                AppStatusService.SetStatus("Windowed & Mods: verify current selection first");
                UpdateControlState();
                return;
            }

            try
            {
                if (!await ConfirmAsync(
                        "Apply selected patches?",
                        "The selected verified catalog patches will be applied to the BEA.exe-only copy only. The original BEA.exe stays unchanged. Restore uses the first full-file backup snapshot, not a per-patch undo."))
                {
                    AppStatusService.SetStatus("Windowed & Mods: apply canceled");
                    return;
                }

                var selected = BinaryPatchPlanBuilder.BuildSelectedSpecs(GetVisibleSelectedKeys());
                var (success, message) = BinaryPatchEngine.ApplyPatchesToFile(BuildPatchTargetOptions(exePath), selected);
                OperationLogTextBox.Text = FormatPatchLogForUi(message, exePath);
                InvalidateVerification();
                AppStatusService.SetStatus(success ? "Windowed & Mods: apply complete" : "Windowed & Mods: apply aborted");
                UpdateControlState();
            }
            catch (Exception ex) when (IsUserFacingOperationException(ex))
            {
                OperationLogTextBox.Text = PatchBenchSafeCopyOutcomeText.DescribeCaughtFailure("apply patches to the BEA.exe-only copy");
                AppStatusService.SetStatus("Windowed & Mods: apply failed");
                UpdateControlState();
            }
        }

        private async void RestoreButton_Click(object sender, RoutedEventArgs e)
        {
            string exePath = (ExePathTextBox.Text ?? string.Empty).Trim();
            if (!IsUsableWorkingCopy(exePath))
            {
                OperationLogTextBox.Text = "Create a BEA.exe-only copy before restoring patch backups.";
                AppStatusService.SetStatus("Windowed & Mods: BEA.exe-only copy required");
                UpdateControlState();
                return;
            }

            if (!File.Exists(BinaryPatchEngine.BuildBackupPath(exePath)))
            {
                OperationLogTextBox.Text = BinaryPatchEngine.BackupFileMissing;
                AppStatusService.SetStatus("Windowed & Mods: backup not found");
                UpdateControlState();
                return;
            }

            try
            {
                if (!await ConfirmAsync(
                        "Restore backup?",
                        "The BEA.exe-only copy will be replaced with its original full-file backup snapshot. The retail executable stays unchanged."))
                {
                    AppStatusService.SetStatus("Windowed & Mods: restore canceled");
                    return;
                }

                var (success, message) = BinaryPatchEngine.RestoreFromBackup(BuildPatchTargetOptions(exePath));
                OperationLogTextBox.Text = FormatPatchLogForUi(message, exePath);
                InvalidateVerification();
                AppStatusService.SetStatus(success ? "Windowed & Mods: restore complete" : "Windowed & Mods: restore failed");
                UpdateControlState();
            }
            catch (Exception ex) when (IsUserFacingOperationException(ex))
            {
                OperationLogTextBox.Text = PatchBenchSafeCopyOutcomeText.DescribeCaughtFailure("restore the BEA.exe-only backup");
                AppStatusService.SetStatus("Windowed & Mods: restore failed");
                UpdateControlState();
            }
        }

        private async void PrepareCopiedProfileButton_Click(object sender, RoutedEventArgs e)
        {
            EnsureRequiredCompatibilitySelected();
            PatchBenchSafeCopySelectionReadinessState readiness = BuildSafeCopySelectionReadiness();
            if (!readiness.CanCreate)
            {
                PatchBenchSafeCopySelectionReadiness.Text = readiness.Status;
                AutomationProperties.SetName(PatchBenchSafeCopySelectionReadiness, readiness.Status);
                OperationLogTextBox.Text = readiness.Status;
                AppStatusService.SetStatus("Windowed & Mods: safe copy selection needs review");
                UpdateControlState();
                return;
            }

            if (_isPreparingCopiedProfile)
            {
                OperationLogTextBox.Text = "Safe game copy preparation is already running.";
                AppStatusService.SetStatus("Windowed & Mods: safe copy preparation already running");
                return;
            }

            _isPreparingCopiedProfile = true;
            _isAwaitingCopiedProfileConfirmation = true;
            try
            {
                UpdateControlState();
                string sourcePath = (SourceExePathTextBox.Text ?? string.Empty).Trim();
                if (!IsBattleEngineExecutableSourcePath(sourcePath) || !File.Exists(sourcePath))
                {
                    OperationLogTextBox.Text = "Select a valid source BEA.exe or BEA.exe.original.backup before preparing a safe game copy.";
                    AppStatusService.SetStatus("Windowed & Mods: missing safe copy source");
                    return;
                }

                string? sourceGameRoot = Path.GetDirectoryName(Path.GetFullPath(sourcePath));
                if (string.IsNullOrWhiteSpace(sourceGameRoot) || !Directory.Exists(sourceGameRoot))
                {
                    OperationLogTextBox.Text = PatchBenchSafeCopyOutcomeText.SourceGameFolderMissing;
                    AppStatusService.SetStatus("Windowed & Mods: safe copy source folder missing");
                    return;
                }

                bool includeSavegames = PatchBenchIncludeSavegamesOption.IsChecked == true;
                bool applyLevel100TextMod = PatchBenchLevel100TextModOption.IsChecked == true;
                bool applyLevel100EarlyFlightMod = PatchBenchLevel100EarlyFlightModOption.IsChecked == true;
                string[] selectedPatchKeys = GetVisibleSelectedKeys().ToArray();
                string? createMusicSwapPresetId = GetSelectedCreateMusicSwapPresetId();
                uint? persistedControllerConfig = PatchBenchPersistControllerConfigOption.IsChecked == true
                    ? GetSelectedControllerConfigurationPreset()
                    : null;
                float? mouseLookSensitivity = GetSelectedMouseLookSensitivityPreset();
                bool invertWalkerY = PatchBenchInvertWalkerYOption.IsChecked == true;
                bool invertFlightY = PatchBenchInvertFlightYOption.IsChecked == true;
                PatchBenchLabCreationInputState creationInputState = BuildLabCreationInputState();
                GameProfilePrepareOptions options = new(
                    SourceGameRoot: sourceGameRoot,
                    OutputRoot: GetCopiedProfileWorkspaceRoot(),
                    ProfileName: BuildCopiedProfileName(),
                    ExecutableOverridePath: sourcePath,
                    ApplyWindowedCompatibilityPatch: true,
                    AllowByteLayoutOnlyTarget: false,
                    IncludeSavegames: includeSavegames,
                    PatchKeys: selectedPatchKeys,
                    LaunchArguments: BuildSelectedLaunchArguments(),
                    ProfilePresetId: MatchSelectableSafeCopyProfileId(selectedPatchKeys),
                    MusicSwapPresetId: createMusicSwapPresetId,
                    ApplyLevel100TutorialTextMod: applyLevel100TextMod,
                    ApplyLevel100EarlyFlightMod: applyLevel100EarlyFlightMod);

                // Reading free space is not a gate and deliberately does not short-circuit the
                // confirmation: it goes into the dialog so the answer stays one decision. A drive
                // that will not report its free space says nothing here rather than blocking.
                string? spaceProblem = SafeCopyManagerText.DescribeSpaceProblem(
                    SafeCopyCatalogService.GetFreeSpaceBytesForNewCopy(),
                    SafeCopyCatalogService.MeasureDirectoryBytes(sourceGameRoot));
                string spaceSection = spaceProblem is null ? string.Empty : $"\n\n{spaceProblem}";

                if (!await ConfirmAsync(
                        "Create safe copy?",
                        PatchBenchSafeCopyOutcomeText.BuildCreateConfirmation(
                            sourceGameRoot,
                            options.OutputRoot,
                            PatchBenchLabCreationInputText.BuildConfirmationSection(creationInputState),
                            spaceSection)))
                {
                    PatchBenchCopiedProfileSummary.Text = PatchBenchSafeCopyOutcomeText.BuildCanceledSummary();
                    OperationLogTextBox.Text = PatchBenchSafeCopyOutcomeText.BuildCanceledOperationLog();
                    AppStatusService.SetStatus("Windowed & Mods: safe copy creation canceled");
                    return;
                }

                _isAwaitingCopiedProfileConfirmation = false;
                UpdateControlState();
                PatchBenchCopiedProfileSummary.Text = "Creating safe game copy. This can take a few minutes for a full game folder...";
                PatchBenchCopiedProfileLaunchPlan.Text = string.Empty;
                PatchBenchCopiedProfileLaunchStatus.Text = PatchBenchLaunchText.BuildBoundary("No safe copy launch attempted.");
                OperationLogTextBox.Text = "Preparing a safe game copy. The selected Steam/game install stays unchanged.";
                AppStatusService.SetStatus("Windowed & Mods: preparing safe copy");

                GameProfilePrepareResult result = await Task.Run(() =>
                    GameProfilePreflightService.PrepareWindowedCompatibilityProfile(options));
                GameProfileControlOptionsResult? controlOptionsResult = null;
                controlOptionsResult = await Task.Run(() =>
                    GameProfileControlOptionsService.ApplyToSafeCopy(
                        new GameProfileControlOptionsRequest(
                            ProfileRoot: result.TargetGameRoot,
                            AppOwnedProfilesRoot: GetCopiedProfileWorkspaceRoot(),
                            MouseSensitivityOverride: mouseLookSensitivity,
                            ControllerConfigP1Override: persistedControllerConfig,
                            ControllerConfigP2Override: persistedControllerConfig,
                            InvertWalkerP1Override: invertWalkerY ? true : null,
                            InvertWalkerP2Override: invertWalkerY ? true : null,
                            InvertFlightP1Override: invertFlightY ? true : null,
                            InvertFlightP2Override: invertFlightY ? true : null,
                            ScreenShapeOverride: EnhancedCopyScreenShape)));

                GameProfileMusicReplacementResult? createMusicSwapResult = result.MusicSwapResult;

                _lastCopiedProfileRoot = result.TargetGameRoot;
                _lastMusicReplacementResult = createMusicSwapResult;
                _lastCopiedProfileCreateMusicSwapPresetId = createMusicSwapPresetId;
                _managedCopiedProfileProcess = null;
                bool copiedSavegames = result.Entries.Any(entry =>
                    string.Equals(entry.Name, "savegames", StringComparison.OrdinalIgnoreCase));
                _lastCopiedProfileContentSignature = BuildSafeCopyContentSignature(
                    sourcePath,
                    includeSavegames,
                    mouseLookSensitivity,
                    persistedControllerConfig,
                    invertWalkerY,
                    invertFlightY,
                    createMusicSwapPresetId,
                    applyLevel100TextMod,
                    applyLevel100EarlyFlightMod,
                    result.PatchResult.PatchKeys);
                GameProfilePrepareReceipt receipt = GameProfilePreflightService.BuildPrepareReceipt(
                    result,
                    copiedSavegames,
                    controlOptionsResult);
                RenderSafeCopyReceipt(receipt);
                RefreshMusicTrackChoices();
                PatchBenchSafeCopyOutcomeTextState outcomeText = new PatchBenchSafeCopyOutcomeTextState(
                    CopiedSavegames: copiedSavegames,
                    ControlOptions: BuildSafeCopyControlOptionsTextState(controlOptionsResult),
                    MusicSwap: BuildSafeCopyMusicSwapTextState(createMusicSwapResult),
                    SafeCopyFolderName: Path.GetFileName(Path.TrimEndingDirectorySeparator(result.TargetGameRoot)),
                    FilesCopied: result.Entries.Count,
                    PatchDisplayList: BuildPatchDisplayList(result.PatchResult.PatchKeys),
                    LaunchModifierSummary: PatchBenchLaunchText.BuildModifierSummary(result.LaunchPlan.Arguments),
                    Level100TextModApplied: result.Level100TextModResult is not null,
                    Level100EarlyFlightModApplied: result.Level100EarlyFlightModResult is not null);
                PatchBenchCopiedProfileSummary.Text = PatchBenchSafeCopyOutcomeText.BuildPreparedSummary(outcomeText);
                PatchBenchCopiedProfileLaunchPlan.Text = result.LaunchPlan.CommandPreview;
                PatchBenchCopiedProfileLaunchStatus.Text =
                    PatchBenchLaunchText.BuildBoundary("Safe copy ready for a guarded launch attempt.");
                PatchBenchMusicReplacementStatus.Text = PatchBenchSafeCopyOutcomeText.BuildMusicReplacementStatus(outcomeText.MusicSwap);
                OperationLogTextBox.Text = PatchBenchSafeCopyOutcomeText.BuildPreparedOperationLog(outcomeText);

                AppStatusService.SetStatus("Windowed & Mods: safe copy ready");
                await RefreshSafeCopyManagerAsync();
            }
            catch (Exception ex) when (IsUserFacingOperationException(ex))
            {
                _lastCopiedProfileRoot = null;
                _lastCopiedProfileContentSignature = null;
                _lastCopiedProfileCreateMusicSwapPresetId = null;
                _lastMusicReplacementResult = null;
                ClearMusicTrackChoices();
                PatchBenchCopiedProfileSummary.Text = PatchBenchSafeCopyOutcomeText.BuildFailedSummary();
                PatchBenchCopiedProfileReceipt.Text = PatchBenchSafeCopyOutcomeText.BuildFailedReceipt();
                PatchBenchCopiedProfileLaunchPlan.Text = string.Empty;
                PatchBenchCopiedProfileLaunchStatus.Text = PatchBenchLaunchText.BuildBoundary("No safe copy launch attempted.");
                PatchBenchMusicReplacementStatus.Text = PatchBenchSafeCopyOutcomeText.BuildDefaultMusicReplacementStatus();
                OperationLogTextBox.Text = PatchBenchSafeCopyOutcomeText.DescribeCaughtFailure("prepare a safe game copy");
                AppStatusService.SetStatus("Windowed & Mods: safe copy preparation failed");
            }
            finally
            {
                _isAwaitingCopiedProfileConfirmation = false;
                _isPreparingCopiedProfile = false;
                UpdateControlState();
            }
        }

        private async void LaunchCopiedProfileButton_Click(object sender, RoutedEventArgs e)
        {
            if (_isLaunchingCopiedProfile)
            {
                OperationLogTextBox.Text = "Safe copy launch is already starting. Wait for it to finish before launching again.";
                AppStatusService.SetStatus("Windowed & Mods: safe copy launch already starting");
                UpdateControlState();
                return;
            }

            if (_managedCopiedProfileProcess is not null)
            {
                OperationLogTextBox.Text = "A safe copy process is already managed by this page. Stop it before launching another.";
                AppStatusService.SetStatus("Windowed & Mods: safe copy already running");
                UpdateControlState();
                return;
            }

            if (!TryBuildCopiedProfileLaunchPlan(_lastCopiedProfileRoot, out GameProfileLaunchPlan? plan, out string? validationError) || plan is null)
            {
                PatchBenchCopiedProfileLaunchStatus.Text = "Safe copy launch is not ready.";
                OperationLogTextBox.Text = validationError ?? "Prepare a safe game copy before launching.";
                AppStatusService.SetStatus("Windowed & Mods: safe copy launch not ready");
                UpdateControlState();
                return;
            }

            _isLaunchingCopiedProfile = true;
            PatchBenchLaunchCopiedProfileButton.IsEnabled = false;
            PatchBenchPrepareCopiedProfileButton.IsEnabled = false;
            UpdateControlState();

            try
            {
                if (!await ConfirmAsync(
                        "Launch safe game copy?",
                        PatchBenchLaunchText.BuildLaunchConfirmation(
                            plan.WorkingDirectory,
                            PatchBenchLaunchText.BuildModifierSummary(plan.Arguments))))
                {
                    AppStatusService.SetStatus("Windowed & Mods: safe copy launch canceled");
                    return;
                }

                PatchBenchCopiedProfileLaunchStatus.Text = "Launching safe copy...";
                OperationLogTextBox.Text = "Launching the safe game copy after manifest, hash, and patch verification.";
                AppStatusService.SetStatus("Windowed & Mods: launching safe copy");

                GameProfileManagedProcess launched = GameProfileRuntimeService.LaunchCopiedProfile(
                    new GameProfileLaunchOptions(
                        ProfileRoot: plan.WorkingDirectory,
                        AppOwnedProfilesRoot: GetCopiedProfileWorkspaceRoot(),
                        LaunchArguments: BuildSelectedLaunchArguments()));

                App.SafeGameCopyProcesses.Register(launched, GetCopiedProfileWorkspaceRoot());
                _managedCopiedProfileProcess = launched;
                PatchBenchCopiedProfileLaunchStatus.Text =
                    PatchBenchLaunchText.BuildBoundary($"Started safe copy process {launched.ProcessId}. This proves process start only.");
                OperationLogTextBox.Text =
                    "Safe copy launch attempt started.\n" +
                    $"Process id: {launched.ProcessId}\n" +
                    $"{PatchBenchLaunchText.BuildModifierSummary(launched.Arguments)}\n" +
                    "The original BEA.exe stays unchanged. Stop targets only this managed safe-copy process record.";
                AppStatusService.SetStatus("Windowed & Mods: safe copy launch started");
            }
            catch (Exception ex) when (IsUserFacingOperationException(ex))
            {
                PatchBenchCopiedProfileLaunchStatus.Text = "Safe copy launch failed.";
                OperationLogTextBox.Text = PatchBenchSafeCopyOutcomeText.DescribeCaughtFailure("launch the safe copy");
                AppStatusService.SetStatus("Windowed & Mods: safe copy launch failed");
            }
            finally
            {
                _isLaunchingCopiedProfile = false;
                UpdateControlState();
            }
        }

        private async void StopCopiedProfileButton_Click(object sender, RoutedEventArgs e)
        {
            if (_managedCopiedProfileProcess is null)
            {
                PatchBenchCopiedProfileLaunchStatus.Text = PatchBenchLaunchText.NoActiveCopiedGame;
                AppStatusService.SetStatus("Windowed & Mods: no safe copy process");
                UpdateControlState();
                return;
            }

            GameProfileManagedProcess process = _managedCopiedProfileProcess;
            if (!await ConfirmAsync(
                    "Stop copied game?",
                    "This closes only the copied BEA.exe process started from this page. Save progress first; Stop can close or force-close the copied game after a timeout. The installed game folder and safe-copy files stay unchanged.",
                    primaryButtonText: "Stop copied game",
                    closeButtonText: "Keep running"))
            {
                PatchBenchCopiedProfileLaunchStatus.Text = PatchBenchLaunchText.BuildBoundary("Safe copy is still running.");
                OperationLogTextBox.Text = "Safe copy stop canceled. The copied game process was left running.";
                AppStatusService.SetStatus("Windowed & Mods: safe copy stop canceled");
                UpdateControlState();
                return;
            }

            _isStoppingCopiedProfile = true;
            PatchBenchStopCopiedProfileButton.IsEnabled = false;
            PatchBenchCopiedProfileLaunchStatus.Text = "Stopping safe copy...";
            OperationLogTextBox.Text = "Stopping only the safe copy process started by this page. Save progress first. Stop can close or force-close the copied game after a timeout.";
            AppStatusService.SetStatus("Windowed & Mods: stopping safe copy");

            try
            {
                GameProfileStopResult result = await Task.Run(() =>
                    App.SafeGameCopyProcesses.Stop(process));

                if (result.Success)
                {
                    _managedCopiedProfileProcess = null;
                    if (string.IsNullOrWhiteSpace(_lastCopiedProfileRoot) &&
                        string.IsNullOrWhiteSpace(_lastCopiedProfileContentSignature))
                    {
                        PatchBenchCopiedProfileSummary.Text = "No safe game copy prepared in this session.";
                    }
                }

                PatchBenchCopiedProfileLaunchStatus.Text = result.Success
                    ? PatchBenchLaunchText.BuildBoundary("Managed safe copy process stopped.")
                    : "Managed safe copy process was not stopped.";
                OperationLogTextBox.Text = result.Success
                    ? PatchBenchLaunchText.BuildBoundary("Managed safe copy process stopped.")
                    : PatchBenchSafeCopyOutcomeText.DescribeCaughtFailure("stop the safe copy");
                AppStatusService.SetStatus(result.Success ? "Windowed & Mods: safe copy stopped" : "Windowed & Mods: safe copy stop failed");
            }
            catch (Exception ex) when (IsUserFacingOperationException(ex))
            {
                PatchBenchCopiedProfileLaunchStatus.Text = "Safe copy stop failed.";
                OperationLogTextBox.Text = PatchBenchSafeCopyOutcomeText.DescribeCaughtFailure("stop the safe copy");
                AppStatusService.SetStatus("Windowed & Mods: safe copy stop failed");
            }
            finally
            {
                _isStoppingCopiedProfile = false;
                UpdateControlState();
            }
        }

        private async void StageMusicReplacementButton_Click(object sender, RoutedEventArgs e)
        {
            string targetFileName = (PatchBenchMusicTargetFileName.Text ?? string.Empty).Trim();
            string replacementPath = (PatchBenchMusicReplacementPath.Text ?? string.Empty).Trim();
            await StageMusicReplacementAsync(targetFileName, replacementPath, copiedTrackSwap: false);
        }

        private async void StageCopiedTrackSwapButton_Click(object sender, RoutedEventArgs e)
        {
            if (PatchBenchMusicTargetTrackComboBox.SelectedItem is not string targetFileName ||
                PatchBenchMusicReplacementTrackComboBox.SelectedItem is not string replacementFileName ||
                string.IsNullOrWhiteSpace(_lastCopiedProfileRoot))
            {
                PatchBenchMusicReplacementStatus.Text = PatchBenchSafeCopyOutcomeText.BuildMusicSwapInputsMissingStatus();
                AppStatusService.SetStatus("Windowed & Mods: safe-copy music swap not ready");
                UpdateControlState();
                return;
            }

            string replacementPath = Path.Combine(_lastCopiedProfileRoot, "data", "Music", replacementFileName);
            await StageMusicReplacementAsync(targetFileName, replacementPath, copiedTrackSwap: true);
        }

        private async void MusicSwapBea02ForBea01PresetButton_Click(object sender, RoutedEventArgs e)
        {
            await StageMusicSwapPresetAsync(GameProfileMusicReplacementService.UseBea02ForBea01PresetId);
        }

        private async void MusicSwapBea01ForBea02PresetButton_Click(object sender, RoutedEventArgs e)
        {
            await StageMusicSwapPresetAsync(GameProfileMusicReplacementService.UseBea01ForBea02PresetId);
        }

        private async void MusicSwapBea02ForBea04PresetButton_Click(object sender, RoutedEventArgs e)
        {
            await StageMusicSwapPresetAsync(GameProfileMusicReplacementService.UseBea02ForBea04PresetId);
        }

        private async Task StageMusicSwapPresetAsync(string presetId)
        {
            if (string.IsNullOrWhiteSpace(_lastCopiedProfileRoot))
            {
                PatchBenchMusicReplacementStatus.Text = PatchBenchSafeCopyOutcomeText.BuildMusicPresetMissingSafeCopyStatus();
                AppStatusService.SetStatus("Windowed & Mods: music preset not ready");
                UpdateControlState();
                return;
            }

            try
            {
                GameProfileMusicSwapPreset preset = GameProfileMusicReplacementService.GetSafeCopyMusicSwapPreset(presetId);
                GameProfileMusicReplacementOptions options = GameProfileMusicReplacementService.BuildSafeCopyMusicSwapPresetOptions(
                    _lastCopiedProfileRoot,
                    GetCopiedProfileWorkspaceRoot(),
                    presetId);
                PatchBenchMusicTargetTrackComboBox.SelectedItem = preset.TargetMusicFileName;
                PatchBenchMusicReplacementTrackComboBox.SelectedItem = preset.ReplacementMusicFileName;
                PatchBenchMusicTargetFileName.Text = preset.TargetMusicFileName;
                PatchBenchMusicReplacementPath.Text = options.ReplacementOggPath;
                await StageMusicReplacementAsync(options.TargetMusicFileName, options.ReplacementOggPath, copiedTrackSwap: true);
            }
            catch (Exception ex) when (IsUserFacingOperationException(ex))
            {
                PatchBenchMusicReplacementStatus.Text = PatchBenchSafeCopyOutcomeText.BuildMusicPresetFailedStatus();
                OperationLogTextBox.Text = PatchBenchSafeCopyOutcomeText.DescribeCaughtFailure("stage the safe-copy music preset");
                AppStatusService.SetStatus("Windowed & Mods: music preset staging failed");
                UpdateControlState();
            }
        }

        private async Task StageMusicReplacementAsync(string targetFileName, string replacementPath, bool copiedTrackSwap)
        {
            if (_managedCopiedProfileProcess is not null)
            {
                PatchBenchMusicReplacementStatus.Text = PatchBenchSafeCopyOutcomeText.BuildMusicStagingBlockedStatus();
                AppStatusService.SetStatus("Windowed & Mods: stop safe copy before music staging");
                UpdateControlState();
                return;
            }

            if (!TryBuildCopiedProfileLaunchPlan(_lastCopiedProfileRoot, out _, out string? validationError))
            {
                PatchBenchMusicReplacementStatus.Text = PatchBenchSafeCopyOutcomeText.BuildMusicStagingMissingSafeCopyStatus();
                OperationLogTextBox.Text = validationError ?? "Prepare a safe game copy before staging copied music bytes.";
                AppStatusService.SetStatus("Windowed & Mods: music staging not ready");
                UpdateControlState();
                return;
            }

            _isStagingMusicReplacement = true;
            PatchBenchStageCopiedTrackSwapButton.IsEnabled = false;
            PatchBenchStageMusicReplacementButton.IsEnabled = false;
            PatchBenchRestoreMusicReplacementButton.IsEnabled = false;
            PatchBenchMusicReplacementStatus.Text = PatchBenchSafeCopyOutcomeText.BuildMusicStagingProgressStatus(copiedTrackSwap);
            OperationLogTextBox.Text = copiedTrackSwap
                ? "Copying one music file over another. The original install stays unchanged."
                : "Staging one replacement music file into the safe copy. The original install stays unchanged.";
                AppStatusService.SetStatus(copiedTrackSwap ? "Windowed & Mods: staging safe-copy music swap" : "Windowed & Mods: staging copied music bytes");

            try
            {
                GameProfileMusicReplacementResult result = await Task.Run(() =>
                    GameProfileMusicReplacementService.StageReplacement(
                        new GameProfileMusicReplacementOptions(
                            SafeGameRoot: _lastCopiedProfileRoot!,
                            AppOwnedProfilesRoot: GetCopiedProfileWorkspaceRoot(),
                            TargetMusicFileName: targetFileName,
                            ReplacementOggPath: replacementPath)));

                _lastMusicReplacementResult = result;
                PatchBenchMusicReplacementStatus.Text =
                    PatchBenchSafeCopyOutcomeText.BuildMusicStagedStatus(result.TargetMusicFileName, copiedTrackSwap);
                OperationLogTextBox.Text = PatchBenchSafeCopyOutcomeText.BuildMusicStagedOperationLog(
                    result.TargetMusicFileName,
                    replacementPath,
                    copiedTrackSwap);
                AppStatusService.SetStatus(copiedTrackSwap ? "Windowed & Mods: safe-copy music swap staged" : "Windowed & Mods: music replacement staged");
            }
            catch (Exception ex) when (IsUserFacingOperationException(ex))
            {
                PatchBenchMusicReplacementStatus.Text = PatchBenchSafeCopyOutcomeText.BuildMusicStagingFailedStatus();
                OperationLogTextBox.Text = PatchBenchSafeCopyOutcomeText.DescribeCaughtFailure("stage copied music bytes");
                AppStatusService.SetStatus("Windowed & Mods: copied music byte staging failed");
            }
            finally
            {
                _isStagingMusicReplacement = false;
                UpdateControlState();
            }
        }

        private async void RestoreMusicReplacementButton_Click(object sender, RoutedEventArgs e)
        {
            if (_managedCopiedProfileProcess is not null)
            {
                PatchBenchMusicReplacementStatus.Text = PatchBenchSafeCopyOutcomeText.BuildMusicRestoreBlockedStatus();
                AppStatusService.SetStatus("Windowed & Mods: stop safe copy before music restore");
                UpdateControlState();
                return;
            }

            if (string.IsNullOrWhiteSpace(_lastCopiedProfileRoot) ||
                !HasMusicReplacementManifest(_lastCopiedProfileRoot))
            {
                PatchBenchMusicReplacementStatus.Text = PatchBenchSafeCopyOutcomeText.BuildMusicRestoreMissingSafeCopyStatus();
                OperationLogTextBox.Text = "Prepare a safe game copy with staged copied music bytes before restoring music backup.";
                AppStatusService.SetStatus("Windowed & Mods: music restore not ready");
                UpdateControlState();
                return;
            }

            _isRestoringMusicReplacement = true;
            PatchBenchStageCopiedTrackSwapButton.IsEnabled = false;
            PatchBenchStageMusicReplacementButton.IsEnabled = false;
            PatchBenchRestoreMusicReplacementButton.IsEnabled = false;
            PatchBenchMusicReplacementStatus.Text = PatchBenchSafeCopyOutcomeText.BuildMusicRestoreProgressStatus();
            OperationLogTextBox.Text = "Restoring music from the safe copy backup. The original install stays unchanged.";
            AppStatusService.SetStatus("Windowed & Mods: restoring music backup");

            try
            {
                GameProfileMusicReplacementRestoreResult result = await Task.Run(() =>
                    GameProfileMusicReplacementService.RestoreReplacement(
                        new GameProfileMusicReplacementRestoreOptions(
                            SafeGameRoot: _lastCopiedProfileRoot!,
                            AppOwnedProfilesRoot: GetCopiedProfileWorkspaceRoot())));

                if (result.Success)
                {
                    _lastMusicReplacementResult = null;
                    if (!string.IsNullOrWhiteSpace(_lastCopiedProfileCreateMusicSwapPresetId))
                    {
                        _lastCopiedProfileContentSignature = null;
                        _lastCopiedProfileCreateMusicSwapPresetId = null;
                    }
                }

                PatchBenchMusicReplacementStatus.Text =
                    PatchBenchSafeCopyOutcomeText.BuildMusicRestoreResultStatus(result.TargetMusicFileName, result.Success);
                OperationLogTextBox.Text = PatchBenchSafeCopyOutcomeText.BuildMusicRestoreOperationLog(
                    result.TargetMusicFileName,
                    result.Success);
                AppStatusService.SetStatus(result.Success ? "Windowed & Mods: music backup restored" : "Windowed & Mods: music restore failed");

            }
            catch (Exception ex) when (IsUserFacingOperationException(ex))
            {
                PatchBenchMusicReplacementStatus.Text = PatchBenchSafeCopyOutcomeText.BuildMusicRestoreFailedStatus();
                OperationLogTextBox.Text = PatchBenchSafeCopyOutcomeText.DescribeCaughtFailure("restore the safe-copy music backup");
                AppStatusService.SetStatus("Windowed & Mods: music backup restore failed");
            }
            finally
            {
                _isRestoringMusicReplacement = false;
                UpdateControlState();
            }
        }

        private void SetSourceExecutablePath(string path)
        {
            _isLoadingSourcePath = true;
            SourceExePathTextBox.Text = path;
            _isLoadingSourcePath = false;
            ExePathTextBox.Text = string.Empty;
            ClearCopiedProfileLaunchState(clearManagedProcess: false);
        }

        private static string GetPatchWorkspaceRoot()
        {
            return Path.Combine(AppConfig.GetConfigDir(), "PatchBench");
        }

        private static string GetCopiedProfileWorkspaceRoot()
        {
            return AppConfig.GetGameProfilesDir();
        }

        private static BinaryPatchTargetOptions BuildPatchTargetOptions(string exePath)
        {
            return new BinaryPatchTargetOptions(
                ExePath: exePath,
                AllowedRoot: GetPatchWorkspaceRoot(),
                AllowByteLayoutOnlyTarget: false);
        }

        private static string BuildWorkingCopyPath(string sourcePath)
        {
            string stamp = DateTime.UtcNow.ToString("yyyyMMdd-HHmmss-fff");
            string uniqueSuffix = Guid.NewGuid().ToString("N")[..8];
            string fileName = string.Equals(Path.GetFileName(sourcePath), "bea.exe", StringComparison.OrdinalIgnoreCase)
                ? Path.GetFileName(sourcePath)
                : "BEA.exe";
            return Path.Combine(GetPatchWorkspaceRoot(), $"{stamp}-{uniqueSuffix}", fileName);
        }

        private static string BuildCopiedProfileName()
        {
            string stamp = DateTime.UtcNow.ToString("yyyyMMdd-HHmmss-fff");
            string uniqueSuffix = Guid.NewGuid().ToString("N")[..8];
            return $"safe-game-copy-{stamp}-{uniqueSuffix}";
        }

        private static bool HasMusicReplacementManifest(string? profileRoot)
        {
            return !string.IsNullOrWhiteSpace(profileRoot) &&
                File.Exists(Path.Combine(profileRoot, GameProfileMusicReplacementService.ManifestFileName));
        }

        private bool IsCopiedProfileContentCurrent(string sourcePath, IReadOnlyCollection<string> selectedKeys)
        {
            return !string.IsNullOrWhiteSpace(_lastCopiedProfileContentSignature) &&
                string.Equals(
                    _lastCopiedProfileContentSignature,
                    BuildCurrentSafeCopyContentSignature(sourcePath, selectedKeys),
                    StringComparison.Ordinal);
        }

        private string BuildCurrentSafeCopyContentSignature(string sourcePath, IReadOnlyCollection<string> selectedKeys)
        {
            var effectiveVisibleKeys = new HashSet<string>(selectedKeys, StringComparer.OrdinalIgnoreCase);
            foreach (string key in BinaryPatchPlanBuilder.BuildSafeCopyProfilePatchKeys(BinaryPatchPlanBuilder.CompatibilityProfileId))
            {
                effectiveVisibleKeys.Add(key);
            }

            string[] effectivePatchKeys = BinaryPatchPlanBuilder
                .BuildSelectedSpecs(effectiveVisibleKeys)
                .Select(spec => spec.Key)
                .ToArray();
            bool includeSavegames = PatchBenchIncludeSavegamesOption.IsChecked == true;
            float? mouseLookSensitivity = GetSelectedMouseLookSensitivityPreset();
            uint? persistedControllerConfig = PatchBenchPersistControllerConfigOption.IsChecked == true
                ? GetSelectedControllerConfigurationPreset()
                : null;
            bool invertWalkerY = PatchBenchInvertWalkerYOption.IsChecked == true;
            bool invertFlightY = PatchBenchInvertFlightYOption.IsChecked == true;
            string? createMusicSwapPresetId = GetSelectedCreateMusicSwapPresetId();
            bool applyLevel100TextMod = PatchBenchLevel100TextModOption.IsChecked == true;
            bool applyLevel100EarlyFlightMod = PatchBenchLevel100EarlyFlightModOption.IsChecked == true;
            return BuildSafeCopyContentSignature(
                sourcePath,
                includeSavegames,
                mouseLookSensitivity,
                persistedControllerConfig,
                invertWalkerY,
                invertFlightY,
                createMusicSwapPresetId,
                applyLevel100TextMod,
                applyLevel100EarlyFlightMod,
                effectivePatchKeys);
        }

        private static string BuildSafeCopyContentSignature(
            string sourcePath,
            bool includeSavegames,
            float? mouseLookSensitivity,
            uint? persistedControllerConfig,
            bool invertWalkerY,
            bool invertFlightY,
            string? createMusicSwapPresetId,
            bool applyLevel100TextMod,
            bool applyLevel100EarlyFlightMod,
            IEnumerable<string> effectivePatchKeys)
        {
            string normalizedSourcePath = string.IsNullOrWhiteSpace(sourcePath)
                ? string.Empty
                : Path.GetFullPath(sourcePath).TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar).ToUpperInvariant();
            string[] normalizedPatchKeys = effectivePatchKeys
                .Select(key => key.Trim())
                .Where(key => key.Length > 0)
                .Distinct(StringComparer.OrdinalIgnoreCase)
                .OrderBy(key => key, StringComparer.OrdinalIgnoreCase)
                .ToArray();
            string persistedControllerConfigToken = persistedControllerConfig.HasValue
                ? persistedControllerConfig.Value.ToString(System.Globalization.CultureInfo.InvariantCulture)
                : "none";
            string mouseSensitivityToken = mouseLookSensitivity.HasValue
                ? mouseLookSensitivity.Value.ToString("0.###", System.Globalization.CultureInfo.InvariantCulture)
                : "none";
            string createMusicSwapPresetToken = string.IsNullOrWhiteSpace(createMusicSwapPresetId)
                ? "none"
                : createMusicSwapPresetId.Trim();
            return $"source={normalizedSourcePath}|savegames={includeSavegames}|mouseLookSensitivity={mouseSensitivityToken}|persistedControllerConfig={persistedControllerConfigToken}|invertWalkerY={invertWalkerY}|invertFlightY={invertFlightY}|createMusicSwapPreset={createMusicSwapPresetToken}|level100TextMod={applyLevel100TextMod}|level100EarlyFlightMod={applyLevel100EarlyFlightMod}|effectivePatches={string.Join(",", normalizedPatchKeys)}";
        }

        private static string? ResolveGameExecutablePath(string gameDir)
        {
            string cleanBackup = Path.Combine(gameDir, "BEA.exe.original.backup");
            if (File.Exists(cleanBackup))
            {
                return cleanBackup;
            }

            string upper = Path.Combine(gameDir, "BEA.exe");
            if (File.Exists(upper))
            {
                return upper;
            }

            string lower = Path.Combine(gameDir, "bea.exe");
            return File.Exists(lower) ? lower : null;
        }

        private static bool IsBattleEngineExecutableSourcePath(string path)
        {
            string fileName = Path.GetFileName(path);
            return string.Equals(fileName, "BEA.exe", StringComparison.OrdinalIgnoreCase) ||
                string.Equals(fileName, "BEA.exe.original.backup", StringComparison.OrdinalIgnoreCase);
        }

        private static string BuildSourceExecutableSummary(string path)
        {
            if (string.IsNullOrWhiteSpace(path))
            {
                return "Select BEA.exe or BEA.exe.original.backup as read-only source.";
            }

            if (!IsBattleEngineExecutableSourcePath(path))
            {
                return "Selected file is not BEA.exe or BEA.exe.original.backup.";
            }

            string? folder = Path.GetFileName(Path.GetDirectoryName(path));
            if (string.Equals(Path.GetFileName(path), "BEA.exe.original.backup", StringComparison.OrdinalIgnoreCase))
            {
                return string.IsNullOrWhiteSpace(folder)
                    ? "Backup-named BEA.exe.original.backup selected as read-only source; patch preparation still verifies bytes."
                    : $"Backup-named BEA.exe.original.backup from {folder}; patch preparation still verifies bytes.";
            }

            return string.IsNullOrWhiteSpace(folder)
                ? "BEA.exe selected as read-only source."
                : $"BEA.exe from {folder}.";
        }

        private static string BuildSafeCopySourceStatus(string path)
        {
            if (string.IsNullOrWhiteSpace(path))
            {
                return "Installed game source: not set. Use Settings or browse a read-only BEA.exe source below.";
            }

            string summary = BuildSourceExecutableSummary(path);
            return IsBattleEngineExecutableSourcePath(path) && File.Exists(path)
                ? $"Installed game source ready for safe game copy: {summary}"
                : $"Installed game source not ready: {summary}";
        }

        private static string BuildSafeCopyProfileCatalogStatus()
        {
            string version = string.IsNullOrWhiteSpace(BinaryPatchPlanBuilder.SafeCopyProfileCatalogVersion)
                ? "unknown schema"
                : BinaryPatchPlanBuilder.SafeCopyProfileCatalogVersion;
            string hash = BinaryPatchPlanBuilder.SafeCopyProfileCatalogSha256;
            string hashSummary = string.IsNullOrWhiteSpace(hash)
                ? "no catalog hash"
                : $"catalog SHA-256 {hash[..Math.Min(12, hash.Length)]}";
            string source = BinaryPatchPlanBuilder.UsingFallbackSafeCopyProfileCatalog
                ? "fallback built-in presets are active"
                : "tracked profile catalog is active";

            return $"Profile catalog and preset source: {source}; {version}; {hashSummary}. Every profile still expands into byte-verified rows before safe-copy creation.";
        }

        private static string BuildWorkingCopySummary(string path)
        {
            if (string.IsNullOrWhiteSpace(path))
            {
                return "Create a copy before verifying or applying patches.";
            }

            return IsUsableWorkingCopy(path)
                ? "This is a BEA.exe-only copy."
                : "Create a BEA.exe-only copy before verification or patching.";
        }

        private string BuildPatchDisplayList(IEnumerable<string> patchKeys)
        {
            var byKey = BinaryPatchEngine.PatchSpecs.ToDictionary(spec => spec.Key, StringComparer.OrdinalIgnoreCase);
            var visibleByKey = _allPatchItems.ToDictionary(item => item.Spec.Key, StringComparer.OrdinalIgnoreCase);
            return string.Join(", ", patchKeys.Select(key =>
                visibleByKey.TryGetValue(key, out BinaryPatchItemModel? item)
                    ? item.DisplayName
                    : byKey.TryGetValue(key, out BinaryPatchSpec? spec)
                        ? BuildHiddenPatchDisplayName(spec)
                        : key));
        }

        private void RenderSafeCopyReceipt(GameProfilePrepareReceipt receipt)
        {
            PatchBenchCopiedProfileReceipt.Text = BuildSafeCopyReceiptText(receipt);
        }

        private static string BuildSafeCopyReceiptText(GameProfilePrepareReceipt receipt)
        {
            return PatchBenchSafeCopyReceiptText.Build(BuildSafeCopyReceiptTextState(receipt));
        }

        private static PatchBenchSafeCopyReceiptTextState BuildSafeCopyReceiptTextState(GameProfilePrepareReceipt receipt)
        {
            ArgumentNullException.ThrowIfNull(receipt);

            return new PatchBenchSafeCopyReceiptTextState(
                receipt.Headline,
                receipt.Lines.Select(line => new PatchBenchReceiptLineTextState(line.Label, line.Value)).ToArray(),
                receipt.IncludedChanges.ToArray(),
                BuildStillNotIncludedLimits(receipt.StillNotIncluded));
        }

        private static string[] BuildStillNotIncludedLimits(IReadOnlyList<string> stillNotIncluded)
        {
            string[] limits = stillNotIncluded.ToArray();
            string hostJoinBoundary = PatchBenchSafeCopyOutcomeText.HostJoinReceiptBoundary;
            return limits.Any(limit => IsCanonicalHostJoinBoundaryLimit(limit, hostJoinBoundary))
                ? limits
                : [.. limits, $"{hostJoinBoundary}."];
        }

        private static bool IsCanonicalHostJoinBoundaryLimit(string limit, string hostJoinBoundary)
        {
            return string.Equals(
                NormalizeReceiptBoundaryText(limit),
                NormalizeReceiptBoundaryText(hostJoinBoundary),
                StringComparison.OrdinalIgnoreCase);
        }

        private static string NormalizeReceiptBoundaryText(string value)
        {
            var builder = new StringBuilder(value.Length);
            bool pendingSpace = false;
            foreach (char current in value.Trim())
            {
                if (char.IsWhiteSpace(current))
                {
                    pendingSpace = true;
                    continue;
                }

                if (pendingSpace && builder.Length > 0)
                {
                    builder.Append(' ');
                }

                builder.Append(current);
                pendingSpace = false;
            }

            string normalized = builder.ToString();
            while (normalized.EndsWith(".", StringComparison.Ordinal))
            {
                normalized = normalized[..^1].TrimEnd();
            }

            return normalized;
        }

        private static string BuildHiddenPatchDisplayName(BinaryPatchSpec spec)
        {
            return spec.Key switch
            {
                "version_overlay_patched_format_cave_string" => "Version overlay support payload (auto-selected)",
                _ => spec.DisplayName,
            };
        }

        private static PatchBenchSafeCopyControlOptionsTextState? BuildSafeCopyControlOptionsTextState(GameProfileControlOptionsResult? result)
        {
            return result is null
                ? null
                : new PatchBenchSafeCopyControlOptionsTextState(
                    result.MouseSensitivity,
                    result.ControllerConfigP1,
                    result.ControllerConfigP2,
                    result.InvertWalkerP1,
                    result.InvertWalkerP2,
                    result.InvertFlightP1,
                    result.InvertFlightP2,
                    result.ScreenShape);
        }

        private static PatchBenchSafeCopyMusicSwapTextState? BuildSafeCopyMusicSwapTextState(GameProfileMusicReplacementResult? result)
        {
            return result is null
                ? null
                : new PatchBenchSafeCopyMusicSwapTextState(
                    result.TargetMusicFileName,
                    result.BackupRelativePath);
        }

        private void UpdateCopiedProfileLaunchReadiness(
            bool contentMatchesCurrent,
            bool hasLaunchPlan,
            GameProfileLaunchPlan? launchPlan,
            string? launchError)
        {
            if (string.IsNullOrWhiteSpace(_lastCopiedProfileRoot) ||
                _managedCopiedProfileProcess is not null ||
                _isPreparingCopiedProfile ||
                _isLaunchingCopiedProfile ||
                _isStoppingCopiedProfile)
            {

                return;
            }

            PatchBenchLaunchReadinessTextResult readinessText = PatchBenchLaunchText.BuildReadiness(
                new PatchBenchLaunchReadinessTextState(
                    contentMatchesCurrent,
                    hasLaunchPlan && launchPlan is not null,
                    launchPlan?.CommandPreview,
                    launchError));
            if (readinessText.SummaryText is not null)
            {
                PatchBenchCopiedProfileSummary.Text = readinessText.SummaryText;
            }

            PatchBenchCopiedProfileLaunchPlan.Text = readinessText.LaunchPlanText;
            PatchBenchCopiedProfileLaunchStatus.Text = readinessText.LaunchStatusText;
        }

        private void RestoreTrackedSafeGameCopyProcess()
        {
            // Leases are written to disk and survive app restarts, so the only honest
            // question is whether that process is still the one running right now.
            App.SafeGameCopyProcesses.PruneDeadLeases();
            if (!App.SafeGameCopyProcesses.TryResolveLiveManagedProcess(out GameProfileRegisteredProcess registered))
            {
                return;
            }

            _managedCopiedProfileProcess = registered.Process;
            _lastCopiedProfileRoot = registered.Process.WorkingDirectory;
            PatchBenchCopiedProfileSummary.Text = PatchBenchSafeCopyOutcomeText.BuildRestoredTrackedLaunchSummary();
            PatchBenchCopiedProfileReceipt.Text = PatchBenchSafeCopyOutcomeText.BuildRestoredTrackedLaunchReceipt();
            PatchBenchCopiedProfileLaunchStatus.Text = PatchBenchSafeCopyOutcomeText.BuildRestoredTrackedLaunchStatus();
            PatchBenchCopiedProfileLaunchPlan.Text =
                GameProfilePreflightService.BuildRedactedCommandPreview(registered.Process.Arguments);
        }

        private static bool SetEquals(IReadOnlyCollection<string> left, IReadOnlyCollection<string> right)
        {
            return left.Count == right.Count &&
                left.ToHashSet(StringComparer.OrdinalIgnoreCase).SetEquals(right);
        }

        private static string? MatchSelectableSafeCopyProfileId(IReadOnlyCollection<string> selectedKeys)
        {
            foreach (SafeCopyProfilePreset preset in BinaryPatchPlanBuilder.GetSafeCopyProfilePresets())
            {
                if (!preset.IsSelectable ||
                    string.Equals(preset.Id, BinaryPatchPlanBuilder.CustomProfileId, StringComparison.OrdinalIgnoreCase))
                {
                    continue;
                }

                if (SetEquals(selectedKeys, preset.PatchKeys))
                {
                    return preset.Id;
                }
            }

            return null;
        }

        private static string FormatPatchLogForUi(string message, string exePath)
        {
            string named = PatchBenchSafeCopyOutcomeText.DescribePatchLog(message);
            if (string.IsNullOrWhiteSpace(named) || string.IsNullOrWhiteSpace(exePath))
            {
                return named;
            }

            string backupPath = BinaryPatchEngine.BuildBackupPath(exePath);
            string formatted = named.Replace(backupPath, "BEA.exe-only backup snapshot", StringComparison.OrdinalIgnoreCase);
            return formatted.Replace(exePath, "BEA.exe-only copy", StringComparison.OrdinalIgnoreCase);
        }

        private static bool IsUsableWorkingCopy(string path)
        {
            return File.Exists(path) && IsInPatchWorkspace(path);
        }

        private void ClearCopiedProfileLaunchState(bool clearManagedProcess)
        {
            _lastCopiedProfileRoot = null;
            _lastCopiedProfileContentSignature = null;
            _lastCopiedProfileCreateMusicSwapPresetId = null;
            _lastMusicReplacementResult = null;
            if (clearManagedProcess)
            {
                _managedCopiedProfileProcess = null;
            }

            bool hasTrackedSafeCopyLaunch = _managedCopiedProfileProcess is not null;
            PatchBenchCopiedProfileSummary.Text = PatchBenchSafeCopyOutcomeText.BuildSourceChangedSummary(hasTrackedSafeCopyLaunch);
            PatchBenchCopiedProfileReceipt.Text = PatchBenchSafeCopyOutcomeText.BuildSourceChangedReceipt(hasTrackedSafeCopyLaunch);
            PatchBenchCopiedProfileLaunchPlan.Text = string.Empty;
            PatchBenchCopiedProfileLaunchStatus.Text = PatchBenchSafeCopyOutcomeText.BuildSourceChangedLaunchStatus(hasTrackedSafeCopyLaunch);
            PatchBenchMusicReplacementStatus.Text = PatchBenchSafeCopyOutcomeText.BuildDefaultMusicReplacementStatus();
            ClearMusicTrackChoices();
        }

        private void RefreshMusicTrackChoices()
        {
            ClearMusicTrackChoices();
            if (string.IsNullOrWhiteSpace(_lastCopiedProfileRoot))
            {
                return;
            }

            IReadOnlyList<string> tracks = GameProfileMusicReplacementService
                .ListSafeCopyMusicTracks(_lastCopiedProfileRoot, GetCopiedProfileWorkspaceRoot())
                .Select(track => track.FileName)
                .ToArray();
            if (tracks.Count == 0)
            {
                return;
            }

            PatchBenchMusicTargetTrackComboBox.ItemsSource = tracks;
            PatchBenchMusicReplacementTrackComboBox.ItemsSource = tracks;

            string target = tracks.FirstOrDefault(track => string.Equals(track, "BEA_01(Master).ogg", StringComparison.OrdinalIgnoreCase)) ?? tracks[0];
            string replacement = tracks.FirstOrDefault(track => !string.Equals(track, target, StringComparison.OrdinalIgnoreCase)) ?? target;
            PatchBenchMusicTargetTrackComboBox.SelectedItem = target;
            PatchBenchMusicReplacementTrackComboBox.SelectedItem = replacement;
            PatchBenchMusicTargetFileName.Text = target;
            PatchBenchMusicReplacementPath.Text = Path.Combine(_lastCopiedProfileRoot, "data", "Music", replacement);
        }

        private void ClearMusicTrackChoices()
        {
            PatchBenchMusicTargetTrackComboBox.ItemsSource = null;
            PatchBenchMusicReplacementTrackComboBox.ItemsSource = null;
            PatchBenchMusicTargetTrackComboBox.SelectedItem = null;
            PatchBenchMusicReplacementTrackComboBox.SelectedItem = null;
        }

        private PatchBenchLabCreationInputState BuildLabCreationInputState()
        {
            int optionalPatchCount = GetVisibleSelectedKeys()
                .Count(key => !_requiredCompatibilityKeys.Contains(key));
            int copiedOptionsCount =
                1 +
                (PatchBenchPersistControllerConfigOption.IsChecked == true ? 1 : 0) +
                (PatchBenchSharpenMouseLookOption.IsChecked == true ? 1 : 0) +
                (PatchBenchInvertWalkerYOption.IsChecked == true ? 1 : 0) +
                (PatchBenchInvertFlightYOption.IsChecked == true ? 1 : 0);

            return new PatchBenchLabCreationInputState(
                optionalPatchCount,
                CountSelectedLaunchModifiers(),
                copiedOptionsCount,
                GetSelectedCreateMusicSwapPresetId() is not null,
                PatchBenchLevel100TextModOption.IsChecked == true,
                PatchBenchLevel100EarlyFlightModOption.IsChecked == true);
        }

        private int CountSelectedLaunchModifiers()
        {
            int count = 0;
            count += PatchBenchSkipFmvLaunchOption.IsChecked == true ? 1 : 0;
            count += PatchBenchNoMusicLaunchOption.IsChecked == true ? 1 : 0;
            count += PatchBenchNoSoundLaunchOption.IsChecked == true ? 1 : 0;
            count += PatchBenchShowDebugTraceLaunchOption.IsChecked == true ? 1 : 0;
            count += string.IsNullOrWhiteSpace(PatchBenchLevelLaunchOption.Text) ? 0 : 1;
            return count;
        }

        /// <summary>
        /// Fills the screen-size picker. The measured size leads; the rest are
        /// offerable because the widescreen correction derives its aspect from
        /// the live screen rather than assuming 16:9, and each says plainly
        /// that nobody has played at it.
        /// </summary>
        private void InitializeResolutionChoices()
        {
            _isPopulatingResolutionChoices = true;
            try
            {
                PatchBenchResolutionComboBox.Items.Clear();
                foreach (DisplayResolutionPreset preset in DisplayResolutionPreset.Offered)
                {
                    PatchBenchResolutionComboBox.Items.Add(new ComboBoxItem
                    {
                        Content = preset.IsMeasured ? $"{preset.Label} (tested)" : preset.Label,
                        Tag = preset,
                    });
                }

                PatchBenchResolutionComboBox.SelectedIndex = 0;
            }
            finally
            {
                _isPopulatingResolutionChoices = false;
            }

            UpdateResolutionNote();
        }

        private DisplayResolutionPreset SelectedResolution =>
            PatchBenchResolutionComboBox?.SelectedItem is ComboBoxItem { Tag: DisplayResolutionPreset preset }
                ? preset
                : DisplayResolutionPreset.Measured;

        private void UpdateResolutionNote()
        {
            PatchBenchResolutionNoteTextBlock.Text = SelectedResolution.Describe();
        }

        private void ResolutionComboBox_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            if (_isPopulatingResolutionChoices)
            {
                return;
            }

            UpdateResolutionNote();
            AppStatusService.SetStatus($"Windowed & Mods: next safe copy runs at {SelectedResolution.Label}");
        }

        private IReadOnlyList<string> BuildSelectedLaunchArguments()
        {
            var args = BinaryPatchPlanBuilder
                .GetSafeCopyProfilePreset(BinaryPatchPlanBuilder.CompatibilityProfileId)
                .Modules
                .SelectMany(module => module.LaunchArguments)
                .ToList();
            if (PatchBenchSkipFmvLaunchOption.IsChecked == true)
            {
                args.Add("-skipfmv");
            }

            if (PatchBenchNoMusicLaunchOption.IsChecked == true)
            {
                args.Add("-nomusic");
            }

            if (PatchBenchNoSoundLaunchOption.IsChecked == true)
            {
                args.Add("-nosound");
            }

            if (PatchBenchShowDebugTraceLaunchOption.IsChecked == true)
            {
                args.Add("-showdebugtrace");
            }

            string levelId = (PatchBenchLevelLaunchOption.Text ?? string.Empty).Trim();
            if (levelId.Length > 0)
            {
                args.Add("-level");
                args.Add(levelId);
            }

            // Substitution, not an append: the compatibility profile always
            // contributes -res 1600 900, and two triples would leave the copied
            // game reading whichever its parser reached last.
            return SelectedResolution.ApplyTo(args);
        }

        private uint? GetSelectedControllerConfigurationPreset()
        {
            int configurationIndex = PatchBenchCopiedControllerConfigComboBox.SelectedIndex;
            return configurationIndex > 0
                ? (uint)configurationIndex
                : null;
        }

        private float? GetSelectedMouseLookSensitivityPreset()
        {
            if (PatchBenchSharpenMouseLookOption.IsChecked != true)
                return null;

            int sensitivityIndex = PatchBenchMouseSensitivityPresetComboBox.SelectedIndex;
            if (sensitivityIndex < 0 || sensitivityIndex >= s_mouseLookSensitivityPresets.Length)
                sensitivityIndex = DefaultMouseSensitivityPresetIndex;

            return s_mouseLookSensitivityPresets[sensitivityIndex];
        }

        private string? GetSelectedCreateMusicSwapPresetId()
        {
            return PatchBenchCreateMusicSwapPresetComboBox.SelectedIndex switch
            {
                1 => GameProfileMusicReplacementService.UseBea02ForBea01PresetId,
                2 => GameProfileMusicReplacementService.UseBea01ForBea02PresetId,
                3 => GameProfileMusicReplacementService.UseBea02ForBea04PresetId,
                _ => null,
            };
        }

        private void RefreshCopiedProfileLaunchPlanPreview()
        {
            if (string.IsNullOrWhiteSpace(_lastCopiedProfileRoot))
            {
                return;
            }

            bool contentMatchesCurrent = IsCopiedProfileContentCurrent(
                (SourceExePathTextBox.Text ?? string.Empty).Trim(),
                GetVisibleSelectedKeys().ToArray());
            GameProfileLaunchPlan? plan = null;
            string? error = null;
            bool hasLaunchPlan = contentMatchesCurrent &&
                TryBuildCopiedProfileLaunchPlan(_lastCopiedProfileRoot, out plan, out error) &&
                plan is not null;

            PatchBenchLaunchReadinessTextResult readinessText = PatchBenchLaunchText.BuildReadiness(
                new PatchBenchLaunchReadinessTextState(
                    contentMatchesCurrent,
                    hasLaunchPlan,
                    plan?.CommandPreview,
                    error));
            if (readinessText.SummaryText is not null)
            {
                PatchBenchCopiedProfileSummary.Text = readinessText.SummaryText;
            }

            PatchBenchCopiedProfileLaunchPlan.Text = readinessText.LaunchPlanText;
            PatchBenchCopiedProfileLaunchStatus.Text = readinessText.LaunchStatusText;
        }

        private static bool IsFrontendColorPatchKey(string key)
        {
            return s_frontendColorPatchKeys.Contains(key, StringComparer.OrdinalIgnoreCase);
        }

        private static bool IsFreeCameraKeyboardQRemapPatchKey(string key)
        {
            return s_freeCameraKeyboardQRemapPatchKeys.Contains(key, StringComparer.OrdinalIgnoreCase);
        }

        private bool TryBuildCopiedProfileLaunchPlan(string? profileRoot, out GameProfileLaunchPlan? plan, out string? error)
        {
            plan = null;
            error = null;
            if (string.IsNullOrWhiteSpace(profileRoot))
            {
                error = "Prepare a safe game copy before launching.";
                return false;
            }

            try
            {
                plan = GameProfilePreflightService.BuildLaunchPlan(profileRoot, BuildSelectedLaunchArguments());
                return true;
            }
            catch (Exception ex) when (IsUserFacingOperationException(ex))
            {
                error = PatchBenchSafeCopyOutcomeText.DescribeCaughtFailure("prepare that launch");
                return false;
            }
        }

        private static bool IsUserFacingOperationException(Exception ex)
        {
            return ex is IOException
                or UnauthorizedAccessException
                or InvalidOperationException
                or ArgumentException
                or NotSupportedException
                or Win32Exception
                or COMException;
        }

        private static bool IsInPatchWorkspace(string path)
        {
            if (string.IsNullOrWhiteSpace(path))
            {
                return false;
            }

            string root = Path.GetFullPath(GetPatchWorkspaceRoot())
                .TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar)
                + Path.DirectorySeparatorChar;

            string fullPath = Path.GetFullPath(path);
            return fullPath.StartsWith(root, StringComparison.OrdinalIgnoreCase);
        }

        private async System.Threading.Tasks.Task<bool> ConfirmAsync(
            string title,
            string body,
            string primaryButtonText = "Continue",
            string closeButtonText = "Cancel")
        {
            var dialog = new ContentDialog
            {
                Title = title,
                Content = new TextBlock
                {
                    Text = body,
                    TextWrapping = TextWrapping.WrapWholeWords
                },
                PrimaryButtonText = primaryButtonText,
                CloseButtonText = closeButtonText,
                DefaultButton = ContentDialogButton.Close,
                XamlRoot = XamlRoot
            };

            return await dialog.ShowAsync() == ContentDialogResult.Primary;
        }

        // ------------------------------------------------------- your safe copies

        private IReadOnlyList<SafeCopyOverview> _safeCopyManagerRows = Array.Empty<SafeCopyOverview>();

        /// <summary>
        /// Rebuild the list of copies on disk.
        ///
        /// Measuring a copy walks a whole game folder, so this runs off the UI thread. It is called
        /// on arrival and after anything that could have changed the set - never from
        /// <c>UpdateControlState</c>, which runs on every checkbox.
        /// </summary>
        private async System.Threading.Tasks.Task RefreshSafeCopyManagerAsync()
        {
            IReadOnlyList<SafeCopyOverview> copies;
            Models.SafeCopyManagerItem[] items;
            try
            {
                (copies, items) = await Task.Run(() =>
                {
                    IReadOnlyList<SafeCopyOverview> listed = SafeCopyCatalogService.List();
                    return (listed, listed.Select(copy => new Models.SafeCopyManagerItem(copy)).ToArray());
                });
            }
            catch (Exception ex) when (IsUserFacingOperationException(ex))
            {
                copies = Array.Empty<SafeCopyOverview>();
                items = Array.Empty<Models.SafeCopyManagerItem>();
            }

            _safeCopyManagerRows = copies;
            SafeCopyManagerList.ItemsSource = items;

            string total = SafeCopyManagerText.BuildTotalLine(copies);
            SafeCopyManagerTotal.Text = total;
            AutomationProperties.SetName(SafeCopyManagerTotal, total);
        }

        private void ShowSafeCopyManagerNote(string note)
        {
            SafeCopyManagerNote.Text = note;
            SafeCopyManagerNote.Visibility = Visibility.Visible;
        }

        private async void SafeCopyManagerRefreshButton_Click(object sender, RoutedEventArgs e)
        {
            await RefreshSafeCopyManagerAsync();
        }

        private static Models.SafeCopyManagerItem? GetRowFor(object sender)
        {
            return (sender as FrameworkElement)?.DataContext as Models.SafeCopyManagerItem;
        }

        private void SafeCopyManagerOpenFolderButton_Click(object sender, RoutedEventArgs e)
        {
            Models.SafeCopyManagerItem? row = GetRowFor(sender);
            if (row is null)
                return;

            // Reveal the executable rather than the folder: Explorer's /select opens the parent with
            // the item highlighted, which lands somebody inside the copy rather than beside it.
            ExplorerRevealService.TryReveal(Path.Combine(row.ProfileRoot, "BEA.exe"));
        }

        private void SafeCopyManagerLaunchButton_Click(object sender, RoutedEventArgs e)
        {
            Models.SafeCopyManagerItem? row = GetRowFor(sender);
            if (row is null)
                return;

            try
            {
                GameProfileManagedProcess process = GameProfileRuntimeService.LaunchCopiedProfile(
                    new GameProfileLaunchOptions(
                        ProfileRoot: row.ProfileRoot,
                        AppOwnedProfilesRoot: GetCopiedProfileWorkspaceRoot(),
                        LaunchArguments: BuildSelectedLaunchArguments()));

                App.SafeGameCopyProcesses.Register(process, GetCopiedProfileWorkspaceRoot());
                _managedCopiedProfileProcess = process;
                _lastCopiedProfileRoot = row.ProfileRoot;
                ShowSafeCopyManagerNote($"{row.DisplayName} is starting.");
                AppStatusService.SetStatus("Windowed & Mods: launched a safe copy");
                UpdateControlState();
            }
            catch (Exception ex) when (IsUserFacingOperationException(ex))
            {
                ShowSafeCopyManagerNote(SafeCopyManagerText.DescribeLaunchFailure(row.DisplayName));
                AppStatusService.SetStatus("Windowed & Mods: could not launch that copy");
            }
        }

        /// <summary>
        /// Delete one copy, and never take a career with it without asking.
        ///
        /// When careers are inside, this is deliberately not a yes/no question. Keeping them is the
        /// first and default answer, losing them is the second, and cancelling is the escape - a
        /// single "are you sure" with careers on the line would be a trap wearing a confirmation's
        /// clothes.
        /// </summary>
        private async void SafeCopyManagerDeleteButton_Click(object sender, RoutedEventArgs e)
        {
            Models.SafeCopyManagerItem? row = GetRowFor(sender);
            if (row is null || App.MainWindowInstance is null)
                return;

            SafeCopyOverview? overview = _safeCopyManagerRows.FirstOrDefault(copy =>
                string.Equals(copy.ProfileRoot, row.ProfileRoot, StringComparison.OrdinalIgnoreCase));
            if (overview is null)
                return;

            string profilesRoot = GetCopiedProfileWorkspaceRoot();
            SafeCopySaveInventory inventory;
            try
            {
                inventory = SafeCopySaveRescueService.Inventory(row.ProfileRoot, profilesRoot);
            }
            catch (Exception ex) when (IsUserFacingOperationException(ex))
            {
                ShowSafeCopyManagerNote(SafeCopyManagerText.CheckFailure);
                return;
            }

            if (!inventory.HasSaves)
            {
                if (!await ConfirmAsync(
                        SafeCopyManagerText.DeleteDialogTitle,
                        SafeCopyManagerText.BuildDeleteBody(row.DisplayName, row.SizeText),
                        SafeCopyManagerText.DeleteEverythingButtonText,
                        SafeCopyManagerText.CancelButtonText))
                {
                    return;
                }

                await DeleteSafeCopyAsync(row, profilesRoot, keepCareersIn: null);
                return;
            }

            var dialog = new ContentDialog
            {
                XamlRoot = XamlRoot,
                Title = SafeCopyManagerText.DeleteDialogTitle,
                Content = new TextBlock
                {
                    Text = SafeCopyManagerText.BuildDeleteWithCareersBody(inventory, row.SizeText),
                    TextWrapping = TextWrapping.WrapWholeWords,
                },
                PrimaryButtonText = SafeCopyManagerText.KeepCareersButtonText,
                SecondaryButtonText = SafeCopyManagerText.DeleteEverythingButtonText,
                CloseButtonText = SafeCopyManagerText.CancelButtonText,
                DefaultButton = ContentDialogButton.Primary,
            };

            ContentDialogResult answer = await dialog.ShowAsync();
            if (answer == ContentDialogResult.None)
                return;

            string? keepIn = null;
            if (answer == ContentDialogResult.Primary)
            {
                keepIn = await PickerInterop.PickFolderAsync(App.MainWindowInstance);
                if (string.IsNullOrWhiteSpace(keepIn))
                {
                    ShowSafeCopyManagerNote("Left the copy alone - no folder was chosen for the careers.");
                    return;
                }
            }

            await DeleteSafeCopyAsync(row, profilesRoot, keepIn);
        }

        private async System.Threading.Tasks.Task DeleteSafeCopyAsync(
            Models.SafeCopyManagerItem row,
            string profilesRoot,
            string? keepCareersIn)
        {
            try
            {
                if (keepCareersIn is not null)
                {
                    SafeCopyRemovalResult removal = await Task.Run(() =>
                        SafeCopySaveRescueService.RescueThenDelete(row.ProfileRoot, profilesRoot, keepCareersIn));

                    ShowSafeCopyManagerNote(
                        SafeCopyManagerText.DescribeRemovalOutcome(removal, row.DisplayName, row.SizeText));
                    AppStatusService.SetStatus(removal.Success
                        ? "Windowed & Mods: kept the careers and deleted the copy"
                        : "Windowed & Mods: the copy was not deleted");
                }
                else
                {
                    await Task.Run(() => GameProfilePreflightService.DeleteGeneratedProfile(
                        row.ProfileRoot,
                        profilesRoot,
                        SafeCopySaveDisposition.DiscardSaves));

                    ShowSafeCopyManagerNote(SafeCopyManagerText.BuildDeletedNote(row.DisplayName, row.SizeText));
                    AppStatusService.SetStatus("Windowed & Mods: deleted a safe copy");
                }
            }
            catch (Exception ex) when (IsUserFacingOperationException(ex))
            {
                ShowSafeCopyManagerNote(SafeCopyManagerText.DescribeDeleteFailure(row.DisplayName));
                AppStatusService.SetStatus("Windowed & Mods: the copy was not deleted");
            }

            if (string.Equals(_lastCopiedProfileRoot, row.ProfileRoot, StringComparison.OrdinalIgnoreCase) &&
                !Directory.Exists(row.ProfileRoot))
            {
                _lastCopiedProfileRoot = null;
            }

            await RefreshSafeCopyManagerAsync();
            UpdateControlState();
        }

        // ------------------------------------------ patching the game you installed

        /// <summary>
        /// The installed game's BEA.exe, if there is one configured or detected.
        ///
        /// Note this deliberately does NOT use <c>ResolveGameExecutablePath</c>, which prefers
        /// <c>BEA.exe.original.backup</c> when it exists. That preference is right for "give me
        /// clean bytes to copy from"; here the subject is the executable the player actually runs.
        /// </summary>
        private static string? GetInstalledGameExecutablePath()
        {
            try
            {
                string? gameDir = AppConfig.Load().GetGameDir() ?? AppConfig.DetectGameDirectory();
                if (string.IsNullOrWhiteSpace(gameDir))
                    return null;

                string exePath = Path.Combine(gameDir, "BEA.exe");
                return File.Exists(exePath) ? exePath : null;
            }
            catch (Exception ex) when (IsUserFacingOperationException(ex))
            {
                return null;
            }
        }

        private void UpdateInstalledGameState()
        {
            string? exePath = GetInstalledGameExecutablePath();
            InstalledGamePatchReadiness readiness = InstalledGamePatchText.DescribeReadiness(exePath);

            string status = InstalledGamePatchText.BuildStatusLine(readiness, exePath);
            PatchBenchInstalledGameStatus.Text = status;

            // The status line IS the accessible name here. Leaving the XAML placeholder in place
            // would announce "Installed game backup state" and tell a screen reader user nothing
            // about which state. Same treatment the safe-copy readiness line gets.
            AutomationProperties.SetName(PatchBenchInstalledGameStatus, status);
            PatchBenchInstalledGameBackupButton.IsEnabled = InstalledGamePatchText.CanBackUp(readiness);
            PatchBenchInstalledGamePatchButton.IsEnabled = InstalledGamePatchText.CanPatch(readiness);
            PatchBenchInstalledGameRestoreButton.IsEnabled = InstalledGamePatchText.CanRestore(readiness);
        }

        private void ShowInstalledGameNote(bool success, string message)
        {
            PatchBenchInstalledGameNote.Text = InstalledGamePatchText.BuildOutcomeNote(success, message);
            PatchBenchInstalledGameNote.Visibility = Visibility.Visible;
        }

        private void InstalledGameBackupButton_Click(object sender, RoutedEventArgs e)
        {
            string? exePath = GetInstalledGameExecutablePath();
            if (exePath is null)
                return;

            var (success, message, _) = BinaryPatchEngine.AuthorizeInstalledGameWrite(exePath);
            ShowInstalledGameNote(success, message);
            AppStatusService.SetStatus(success
                ? "Windowed & Mods: your original executable is backed up"
                : "Windowed & Mods: could not back up your game");
            UpdateInstalledGameState();
        }

        /// <summary>
        /// Patch the real install.
        ///
        /// Deliberately a separate handler from the safe-copy create rather than a branch inside
        /// it. The two ask different questions of the person pressing them, and the ordering
        /// contract the create handler is held to (revalidate, return, confirm, only then mutate)
        /// is easier to keep true when it is not sharing a body with this.
        /// </summary>
        private async void InstalledGamePatchButton_Click(object sender, RoutedEventArgs e)
        {
            string? exePath = GetInstalledGameExecutablePath();
            if (exePath is null)
                return;

            string[] selectedKeys = GetVisibleSelectedKeys().ToArray();
            IReadOnlyList<BinaryPatchSpec> selected = BinaryPatchEngine.PatchSpecs
                .Where(spec => selectedKeys.Contains(spec.Key, StringComparer.OrdinalIgnoreCase))
                .ToArray();
            if (selected.Count == 0)
            {
                ShowInstalledGameNote(false, "Choose at least one change first.");
                return;
            }

            if (!await ConfirmAsync(
                    InstalledGamePatchText.ConfirmPatchTitle,
                    InstalledGamePatchText.BuildPatchConfirmation(
                        exePath,
                        string.Join(", ", BuildPatchDisplayList(selectedKeys))),
                    InstalledGamePatchText.ConfirmPatchPrimaryButton,
                    InstalledGamePatchText.ConfirmCloseButton))
            {
                ShowInstalledGameNote(true, "Left your game alone.");
                return;
            }

            var (authorized, authorizationMessage, authorization) =
                BinaryPatchEngine.AuthorizeInstalledGameWrite(exePath);
            if (!authorized || authorization is null)
            {
                ShowInstalledGameNote(false, authorizationMessage);
                AppStatusService.SetStatus("Windowed & Mods: could not back up your game");
                UpdateInstalledGameState();
                return;
            }

            var target = new BinaryPatchTargetOptions(
                exePath,
                AllowedRoot: string.Empty,
                InstalledGame: authorization);

            (bool applied, string applyMessage) = await Task.Run(() =>
                BinaryPatchEngine.ApplyPatchesToFile(target, selected));

            OperationLogTextBox.Text = FormatPatchLogForUi(applyMessage, exePath);
            ShowInstalledGameNote(applied, applied
                ? $"{authorizationMessage} Your game is patched."
                : PatchBenchSafeCopyOutcomeText.DescribeInstalledWriteFailure(applyMessage));
            AppStatusService.SetStatus(applied
                ? "Windowed & Mods: your installed game is patched"
                : "Windowed & Mods: patching your game did not complete");
            UpdateInstalledGameState();
        }

        private async void InstalledGameRestoreButton_Click(object sender, RoutedEventArgs e)
        {
            string? exePath = GetInstalledGameExecutablePath();
            if (exePath is null)
                return;

            if (!await ConfirmAsync(
                    InstalledGamePatchText.ConfirmRestoreTitle,
                    InstalledGamePatchText.BuildRestoreConfirmation(exePath),
                    InstalledGamePatchText.ConfirmRestorePrimaryButton,
                    InstalledGamePatchText.ConfirmCloseButton))
            {
                ShowInstalledGameNote(true, "Left your game as it is.");
                return;
            }

            var (authorized, authorizationMessage, authorization) =
                BinaryPatchEngine.AuthorizeInstalledGameWrite(exePath);
            if (!authorized || authorization is null)
            {
                ShowInstalledGameNote(false, authorizationMessage);
                UpdateInstalledGameState();
                return;
            }

            (bool success, string message) = await Task.Run(() =>
                BinaryPatchEngine.RestoreFromBackup(new BinaryPatchTargetOptions(
                    exePath,
                    AllowedRoot: string.Empty,
                    InstalledGame: authorization)));

            OperationLogTextBox.Text = FormatPatchLogForUi(message, exePath);
            ShowInstalledGameNote(success, success
                ? "Your game is back the way it was."
                : PatchBenchSafeCopyOutcomeText.DescribeInstalledWriteFailure(message));
            AppStatusService.SetStatus(success
                ? "Windowed & Mods: your game is back the way it was"
                : "Windowed & Mods: could not put your game back");
            UpdateInstalledGameState();
        }
    }
}
