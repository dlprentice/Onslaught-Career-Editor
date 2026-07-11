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
using Onslaught___Career_Editor;

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
        private const string HighDetailTextureRamLimitMb = "256";
        private const int DefaultMouseSensitivityPresetIndex = 1;
        private const int NoCreateMusicSwapPresetIndex = 0;
        private const int NoAdminLevelPresetIndex = 0;
        private static readonly float[] s_mouseLookSensitivityPresets =
        {
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
            HighDetail,
            ControlBaseline,
            ControlSharpened,
            ControlConfig2,
            ControlConfig3,
            ControlConfig4,
        }

        private sealed record LaunchPresetSelection(
            bool SkipFmv,
            bool NoMusic,
            bool NoSound,
            bool HighDetail,
            bool NoStaticShadows,
            bool NoRumble,
            string LevelId,
            int ControllerConfigurationIndex,
            bool PersistControllerConfig,
            bool SharpenMouseLook,
            int MouseSensitivityPresetIndex,
            bool InvertWalkerY,
            bool InvertFlightY,
            string TextureRamLimitMb,
            string StatusMessage);

        private readonly List<BinaryPatchItemModel> _allPatchItems;
        private readonly List<BinaryPatchGroupModel> _patchGroups;
        private string? _verifiedSignature;
        private string? _lastCopiedProfileRoot;
        private string? _lastCopiedProfileContentSignature;
        private string? _lastCopiedProfileCreateMusicSwapPresetId;
        private GameProfileMusicReplacementResult? _lastMusicReplacementResult;
        private OnlineSecondHostReadinessArtifactSummary? _secondHostReadinessArtifactSummary;
        private OnlineLocalGamepadReadinessArtifactSummary? _localGamepadReadinessArtifactSummary;
        private OnlineDualSafeCopyTopologyArtifactSummary? _dualSafeCopyTopologyArtifactSummary;
        private GameProfileManagedProcess? _managedCopiedProfileProcess;
        private bool _isLoadingSourcePath;
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

            _allPatchItems = BinaryPatchPlanBuilder.GetVisibleSpecs()
                .Select(spec => new BinaryPatchItemModel(spec)
                {
                    IsSelected = defaultProfileKeys.Contains(spec.Key, StringComparer.OrdinalIgnoreCase)
                })
                .ToList();
            _patchGroups = PatchBenchPatchGroups.Build(_allPatchItems);

            InitializeComponent();
            PatchBenchMusicTargetFileName.Text = "BEA_01(Master).ogg";
            PatchBenchAdminLevelPresetComboBox.SelectedIndex = NoAdminLevelPresetIndex;
            PatchBenchConfigurationLaunchPresetComboBox.SelectedIndex = 0;
            PatchBenchMouseSensitivityPresetComboBox.SelectedIndex = DefaultMouseSensitivityPresetIndex;
            PatchBenchCreateMusicSwapPresetComboBox.SelectedIndex = NoCreateMusicSwapPresetIndex;
            PatchGroupsItemsControl.ItemsSource = _patchGroups;

            OperationLogTextBox.Text =
                "Windowed & Mods safely patches and plays a copy of your game. Your original Steam installation is left untouched.\n" +
                "Ready.";

            RenderOnlineMultiplayerReadiness();
            LoadSourcePathFromConfig();
            RestoreTrackedSafeGameCopyProcess();
            UpdateControlState();
        }

        private void RenderOnlineMultiplayerReadiness()
        {
            OnlineMultiplayerReadinessSummary summary = OnlineMultiplayerReadinessService.GetCurrentSummary(
                _secondHostReadinessArtifactSummary,
                _localGamepadReadinessArtifactSummary,
                _dualSafeCopyTopologyArtifactSummary);
            PatchBenchOnlineReadinessTextState text = PatchBenchOnlineReadinessText.Build(
                summary,
                _secondHostReadinessArtifactSummary,
                _localGamepadReadinessArtifactSummary,
                _dualSafeCopyTopologyArtifactSummary);

            PatchBenchOnlineReadinessHeadline.Text = text.Headline;
            PatchBenchOnlineReadinessSlots.Text = text.Slots;
            PatchBenchOnlineReadinessMetadataSlots.Text = text.MetadataSlots;
            PatchBenchOnlineTargetModel.Text = text.TargetModel;
            PatchBenchOnlineReadinessProofClass.Text = text.ProofClass;
            PatchBenchOnlineReadinessNextProof.Text = text.NextProof;
            PatchBenchOnlineReadinessGateDetails.Text = text.GateDetails;
            PatchBenchOnlineProofLadder.Text = text.ProofLadder;
            PatchBenchOnlineCompanionModelDetails.Text = text.CompanionModelDetails;
            PatchBenchOnlineSecondHostSetupChecklist.Text = text.SecondHostSetupChecklist;
            PatchBenchOnlineReadinessBlockedActions.Text = text.BlockedActions;
            PatchBenchOnlineReadinessBlockedReasons.Text = text.BlockedReasons;
            PatchBenchOnlineLiveAttemptStatus.Text = text.LiveAttemptStatus;
            PatchBenchOnlineLiveAttemptBlockers.Text = text.LiveAttemptBlockers;
            PatchBenchOnlineLiveAttemptCommands.Text = text.LiveAttemptCommands;
            PatchBenchOnlinePromotionLockStatus.Text = text.PromotionLockStatus;
            PatchBenchOnlineReadinessArtifactStatus.Text = text.SecondHostReadinessArtifactStatus;
            PatchBenchGamepadReadinessArtifactStatus.Text = text.GamepadReadinessArtifactStatus;
            PatchBenchDualSafeCopyTopologyArtifactStatus.Text = text.DualSafeCopyTopologyArtifactStatus;
            PatchBenchDualSafeCopyTopologyBoundary.Text = text.DualSafeCopyTopologyBoundary;
            PatchBenchDualSafeCopyTopologyNextProofs.Text = text.DualSafeCopyTopologyNextProofs;
            RenderOnlineTechnicalDetailsVisibility();
            RenderMaintainerArtifactToolsVisibility();
            RenderOnlineCompanionSessionReadiness(false, null, null);
        }

        private void RenderOnlineCompanionSessionReadiness(
            bool contentMatchesCurrentSelection,
            GameProfileLaunchPlan? launchPlan,
            string? launchPlanError)
        {
            OnlineCompanionSessionReadinessSummary summary = OnlineMultiplayerReadinessService.GetCompanionSessionReadiness(
                _lastCopiedProfileRoot,
                contentMatchesCurrentSelection,
                launchPlan,
                launchPlanError);
            PatchBenchOnlineCompanionSessionTextState text = PatchBenchOnlineReadinessText.BuildCompanionSession(summary);

            PatchBenchOnlinePrepActionStatus.Text = text.PrepActionStatus;
            PatchBenchOnlineCompanionSessionStatus.Text = text.SessionStatus;
            PatchBenchOnlineCompanionLaunchPlan.Text = text.LaunchPlan;
            PatchBenchOnlineCompanionNextProofs.Text = text.NextProofs;
            PatchBenchOnlineCompanionNonClaims.Text = text.NonClaims;
        }

        private void RenderMaintainerArtifactToolsVisibility()
        {
            bool visible = PatchBenchOnlineMaintainerArtifactToolsToggle.IsOn;
            PatchBenchMaintainerArtifactLoaderPanel.Visibility = visible ? Visibility.Visible : Visibility.Collapsed;
            PatchBenchMaintainerArtifactToolsStatus.Text = visible
                ? "Technical summary loaders are visible. Loading a summary still cannot enable Host/Join or prove online play."
                : "Technical summary loaders are hidden. Normal safe-copy play does not need summary files.";
        }

        private void RenderOnlineTechnicalDetailsVisibility()
        {
            bool visible = PatchBenchOnlineTechnicalDetailsToggle.IsOn;
            PatchBenchOnlineTechnicalDetailsExpander.Visibility = visible ? Visibility.Visible : Visibility.Collapsed;
        }

        private IEnumerable<BinaryPatchItemModel> AllItems => _allPatchItems;

        private IEnumerable<string> GetVisibleSelectedKeys()
        {
            return AllItems.Where(item => item.IsSelected).Select(item => item.Spec.Key);
        }

        private void SelectOnlyKeys(IEnumerable<string> keys)
        {
            var selected = keys.ToHashSet(StringComparer.OrdinalIgnoreCase);
            foreach (BinaryPatchItemModel item in _allPatchItems)
            {
                item.IsSelected = selected.Contains(item.Spec.Key);
            }

            InvalidateVerification();
            UpdateControlState();
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

            PatchBenchPrepareCopiedProfileButton.IsEnabled = hasSourceExe && !_isPreparingCopiedProfile && !_isLaunchingCopiedProfile && !_isStoppingCopiedProfile && _managedCopiedProfileProcess is null;
            PatchBenchIncludeSavegamesOption.IsEnabled = PatchBenchPrepareCopiedProfileButton.IsEnabled;
            PatchBenchTopCreateSafeCopyButton.IsEnabled = PatchBenchPrepareCopiedProfileButton.IsEnabled;
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
            bool isModernGraphicsOnly = SetEquals(visibleSelectedKeys, s_modernGraphicsKeys);
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
                        : "Verify the BEA.exe-only copy after any path or selection change.";

            UpdateCopiedProfileLaunchReadiness(
                copiedProfileContentMatchesCurrent,
                copiedProfileHasLaunchPlan,
                copiedProfileLaunchPlan,
                copiedProfileLaunchError);
            RenderOnlineCompanionSessionReadiness(
                copiedProfileContentMatchesCurrent,
                copiedProfileHasLaunchPlan ? copiedProfileLaunchPlan : null,
                copiedProfileLaunchError);
        }

        private void UpdateChoiceVisualState(IReadOnlyCollection<string> selectedKeys)
        {
            string? profileId = MatchSelectableSafeCopyProfileId(selectedKeys);
            string? selectedMenuColorKey = selectedKeys.FirstOrDefault(IsFrontendColorPatchKey);
            PatchBenchMenuColorSelectionKind menuColorSelection = BuildMenuColorSelectionKind(selectedMenuColorKey);

            PatchBenchChoiceVisualState.ApplyPatchBenchChoiceStyles(
                new[]
                {
                    PatchBenchChoiceVisualState.Bind(PatchBenchWindowedPresetButton, "Select Compatibility Copy profile", "Selected: Compatibility Copy profile", string.Equals(profileId, BinaryPatchPlanBuilder.CompatibilityProfileId, StringComparison.OrdinalIgnoreCase)),
                    PatchBenchChoiceVisualState.Bind(PatchBenchStableDefaultsButton, "Select Windowed and Graphics Defaults profile", "Selected: Windowed and Graphics Defaults profile", string.Equals(profileId, BinaryPatchPlanBuilder.RecommendedProfileId, StringComparison.OrdinalIgnoreCase)),
                    PatchBenchChoiceVisualState.Bind(PatchBenchEnhancedPreviewProfileButton, "Select Enhanced Profile Preview profile", "Selected: Enhanced Profile Preview profile", string.Equals(profileId, BinaryPatchPlanBuilder.EnhancedPreviewProfileId, StringComparison.OrdinalIgnoreCase)),
                    PatchBenchChoiceVisualState.Bind(PatchBenchClearSelectionButton, "Clear optional mod rows; safe copies still include required compatibility", "Selected: no optional mod rows", selectedKeys.Count == 0),
                    PatchBenchChoiceVisualState.Bind(PatchBenchModernGraphicsPresetButton, "Select extra graphics flag rows only", "Selected: graphics flag rows only", SetEquals(selectedKeys, s_modernGraphicsKeys)),
                    PatchBenchChoiceVisualState.Bind(PatchBenchDebugCameraPreviewProfileButton, "Select Debug Camera Preview profile", "Selected: Debug Camera Preview profile", string.Equals(profileId, BinaryPatchPlanBuilder.DebugCameraPreviewProfileId, StringComparison.OrdinalIgnoreCase)),
                    PatchBenchChoiceVisualState.Bind(PatchBenchMenuColorRedButton, "Select red menu background color", "Selected: red menu background color", string.Equals(selectedMenuColorKey, "frontend_clear_screen_dark_red", StringComparison.OrdinalIgnoreCase)),
                    PatchBenchChoiceVisualState.Bind(PatchBenchMenuColorGreenButton, "Select green menu background color", "Selected: green menu background color", string.Equals(selectedMenuColorKey, "frontend_clear_screen_dark_green", StringComparison.OrdinalIgnoreCase)),
                    PatchBenchChoiceVisualState.Bind(PatchBenchMenuColorBlackButton, "Select black menu background color", "Selected: black menu background color", string.Equals(selectedMenuColorKey, "frontend_clear_screen_black", StringComparison.OrdinalIgnoreCase)),
                    PatchBenchChoiceVisualState.Bind(PatchBenchMenuColorClearButton, "Clear menu background color selection", "Selected: no menu background color", selectedMenuColorKey is null),
                },
                Resources);
            PatchBenchMenuColorSelectionStatus.Text = PatchBenchMenuColorSelectionText.BuildStatus(menuColorSelection);
            AutomationProperties.SetName(PatchBenchMenuColorSelectionStatus, PatchBenchMenuColorSelectionStatus.Text);
        }

        private void UpdateLaunchPresetVisualState()
        {
            PatchBenchChoiceVisualState.ApplyPatchBenchChoiceStyles(
                new[]
                {
                    PatchBenchChoiceVisualState.Bind(PatchBenchQuietCaptureLaunchPresetButton, PatchBenchLaunchPresetText.BuildQuietCaptureChoiceState(_selectedLaunchPresetChoice == LaunchPresetChoice.QuietCapture)),
                    PatchBenchChoiceVisualState.Bind(PatchBenchHighDetailLaunchPresetButton, PatchBenchLaunchPresetText.BuildHighDetailChoiceState(_selectedLaunchPresetChoice == LaunchPresetChoice.HighDetail)),
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

            if (CurrentLaunchOptionsMatchSelectedPreset())
            {
                return;
            }

            _selectedLaunchPresetChoice = LaunchPresetChoice.None;
        }

        private bool CurrentLaunchOptionsMatchSelectedPreset()
        {
            return _selectedLaunchPresetChoice switch
            {
                LaunchPresetChoice.QuietCapture => CurrentLaunchOptionsMatch(
                    skipFmv: true,
                    noMusic: true,
                    noSound: false,
                    highDetail: false,
                    noStaticShadows: false,
                    noRumble: false,
                    levelId: string.Empty,
                    controllerConfigurationIndex: 0,
                    persistControllerConfig: false,
                    sharpenMouseLook: false,
                    mouseSensitivityPresetIndex: DefaultMouseSensitivityPresetIndex,
                    invertWalkerY: false,
                    invertFlightY: false,
                    textureRamLimitMb: string.Empty),
                LaunchPresetChoice.HighDetail => CurrentLaunchOptionsMatch(
                    skipFmv: true,
                    noMusic: false,
                    noSound: false,
                    highDetail: true,
                    noStaticShadows: false,
                    noRumble: false,
                    levelId: string.Empty,
                    controllerConfigurationIndex: 0,
                    persistControllerConfig: false,
                    sharpenMouseLook: false,
                    mouseSensitivityPresetIndex: DefaultMouseSensitivityPresetIndex,
                    invertWalkerY: false,
                    invertFlightY: false,
                    textureRamLimitMb: HighDetailTextureRamLimitMb),
                LaunchPresetChoice.ControlBaseline => CurrentLaunchOptionsMatch(
                    skipFmv: true,
                    noMusic: false,
                    noSound: false,
                    highDetail: false,
                    noStaticShadows: false,
                    noRumble: false,
                    levelId: string.Empty,
                    controllerConfigurationIndex: 1,
                    persistControllerConfig: false,
                    sharpenMouseLook: false,
                    mouseSensitivityPresetIndex: DefaultMouseSensitivityPresetIndex,
                    invertWalkerY: false,
                    invertFlightY: false,
                    textureRamLimitMb: string.Empty),
                LaunchPresetChoice.ControlSharpened => CurrentLaunchOptionsMatch(
                    skipFmv: true,
                    noMusic: false,
                    noSound: false,
                    highDetail: false,
                    noStaticShadows: false,
                    noRumble: false,
                    levelId: string.Empty,
                    controllerConfigurationIndex: 1,
                    persistControllerConfig: true,
                    sharpenMouseLook: true,
                    mouseSensitivityPresetIndex: DefaultMouseSensitivityPresetIndex,
                    invertWalkerY: false,
                    invertFlightY: false,
                    textureRamLimitMb: string.Empty),
                LaunchPresetChoice.ControlConfig2 => CurrentLaunchOptionsMatch(
                    skipFmv: true,
                    noMusic: false,
                    noSound: false,
                    highDetail: false,
                    noStaticShadows: false,
                    noRumble: false,
                    levelId: string.Empty,
                    controllerConfigurationIndex: 2,
                    persistControllerConfig: true,
                    sharpenMouseLook: false,
                    mouseSensitivityPresetIndex: DefaultMouseSensitivityPresetIndex,
                    invertWalkerY: false,
                    invertFlightY: false,
                    textureRamLimitMb: string.Empty),
                LaunchPresetChoice.ControlConfig3 => CurrentLaunchOptionsMatch(
                    skipFmv: true,
                    noMusic: false,
                    noSound: false,
                    highDetail: false,
                    noStaticShadows: false,
                    noRumble: false,
                    levelId: string.Empty,
                    controllerConfigurationIndex: 3,
                    persistControllerConfig: true,
                    sharpenMouseLook: false,
                    mouseSensitivityPresetIndex: DefaultMouseSensitivityPresetIndex,
                    invertWalkerY: false,
                    invertFlightY: false,
                    textureRamLimitMb: string.Empty),
                LaunchPresetChoice.ControlConfig4 => CurrentLaunchOptionsMatch(
                    skipFmv: true,
                    noMusic: false,
                    noSound: false,
                    highDetail: false,
                    noStaticShadows: false,
                    noRumble: false,
                    levelId: string.Empty,
                    controllerConfigurationIndex: 4,
                    persistControllerConfig: true,
                    sharpenMouseLook: false,
                    mouseSensitivityPresetIndex: DefaultMouseSensitivityPresetIndex,
                    invertWalkerY: false,
                    invertFlightY: false,
                    textureRamLimitMb: string.Empty),
                _ => false,
            };
        }

        private bool CurrentLaunchOptionsMatch(
            bool skipFmv,
            bool noMusic,
            bool noSound,
            bool highDetail,
            bool noStaticShadows,
            bool noRumble,
            string levelId,
            int controllerConfigurationIndex,
            bool persistControllerConfig,
            bool sharpenMouseLook,
            int mouseSensitivityPresetIndex,
            bool invertWalkerY,
            bool invertFlightY,
            string textureRamLimitMb)
        {
            return PatchBenchSkipFmvLaunchOption.IsChecked == skipFmv
                && PatchBenchNoMusicLaunchOption.IsChecked == noMusic
                && PatchBenchNoSoundLaunchOption.IsChecked == noSound
                && PatchBenchHighDetailLaunchOption.IsChecked == highDetail
                && PatchBenchNoStaticShadowsLaunchOption.IsChecked == noStaticShadows
                && PatchBenchNoRumbleLaunchOption.IsChecked == noRumble
                && string.Equals(PatchBenchLevelLaunchOption.Text ?? string.Empty, levelId, StringComparison.Ordinal)
                && PatchBenchConfigurationLaunchPresetComboBox.SelectedIndex == controllerConfigurationIndex
                && PatchBenchPersistControllerConfigOption.IsChecked == persistControllerConfig
                && PatchBenchSharpenMouseLookOption.IsChecked == sharpenMouseLook
                && PatchBenchMouseSensitivityPresetComboBox.SelectedIndex == mouseSensitivityPresetIndex
                && PatchBenchInvertWalkerYOption.IsChecked == invertWalkerY
                && PatchBenchInvertFlightYOption.IsChecked == invertFlightY
                && string.Equals(PatchBenchTextureRamLimitLaunchOption.Text ?? string.Empty, textureRamLimitMb, StringComparison.Ordinal);
        }

        private bool IsLaunchPresetOwnedCheckBox(object sender)
        {
            return ReferenceEquals(sender, PatchBenchSkipFmvLaunchOption)
                || ReferenceEquals(sender, PatchBenchNoMusicLaunchOption)
                || ReferenceEquals(sender, PatchBenchNoSoundLaunchOption)
                || ReferenceEquals(sender, PatchBenchHighDetailLaunchOption)
                || ReferenceEquals(sender, PatchBenchNoStaticShadowsLaunchOption)
                || ReferenceEquals(sender, PatchBenchNoRumbleLaunchOption)
                || ReferenceEquals(sender, PatchBenchShowDebugTraceLaunchOption)
                || ReferenceEquals(sender, PatchBenchPersistControllerConfigOption)
                || ReferenceEquals(sender, PatchBenchSharpenMouseLookOption)
                || ReferenceEquals(sender, PatchBenchInvertWalkerYOption)
                || ReferenceEquals(sender, PatchBenchInvertFlightYOption);
        }

        private bool IsLaunchPresetOwnedTextBox(object sender)
        {
            return ReferenceEquals(sender, PatchBenchLevelLaunchOption)
                || ReferenceEquals(sender, PatchBenchTextureRamLimitLaunchOption);
        }

        private bool IsLaunchPresetOwnedComboBox(object sender)
        {
            return ReferenceEquals(sender, PatchBenchConfigurationLaunchPresetComboBox)
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

            InvalidateVerification();
            UpdateControlState();
        }

        private void WindowedPresetButton_Click(object sender, RoutedEventArgs e)
        {
            SelectOnlyKeys(BinaryPatchPlanBuilder.BuildSafeCopyProfilePatchKeys(BinaryPatchPlanBuilder.CompatibilityProfileId));
            AppStatusService.SetStatus("Windowed & Mods: Compatibility Copy profile selected");
        }

        private void ModernGraphicsPresetButton_Click(object sender, RoutedEventArgs e)
        {
            SelectOnlyKeys(s_modernGraphicsKeys);
            AppStatusService.SetStatus("Windowed & Mods: graphics flag rows selected");
        }

        private void StableDefaultsButton_Click(object sender, RoutedEventArgs e)
        {
            SelectOnlyKeys(BinaryPatchPlanBuilder.BuildSafeCopyProfilePatchKeys(BinaryPatchPlanBuilder.RecommendedProfileId));
            AppStatusService.SetStatus("Windowed & Mods: Windowed + Graphics Defaults profile selected");
        }

        private void EnhancedPreviewPresetButton_Click(object sender, RoutedEventArgs e)
        {
            SafeCopyProfilePreset preset = BinaryPatchPlanBuilder.GetSafeCopyProfilePreset(BinaryPatchPlanBuilder.EnhancedPreviewProfileId);
            SelectOnlyKeys(preset.PatchKeys);
            PatchBenchConfigurationLaunchPresetComboBox.SelectedIndex = preset.DefaultControllerConfiguration ?? 0;
            PatchBenchPersistControllerConfigOption.IsChecked = preset.DefaultPersistControllerConfigInOptions;
            PatchBenchSharpenMouseLookOption.IsChecked = preset.DefaultSharpenMouseLook;
            PatchBenchMouseSensitivityPresetComboBox.SelectedIndex = DefaultMouseSensitivityPresetIndex;
            PatchBenchInvertWalkerYOption.IsChecked = false;
            PatchBenchInvertFlightYOption.IsChecked = false;
            RefreshCopiedProfileLaunchPlanPreview();
            UpdateControlState();
            AppStatusService.SetStatus("Windowed & Mods: Enhanced Profile Preview profile selected");
        }

        private void DebugCameraPreviewPresetButton_Click(object sender, RoutedEventArgs e)
        {
            SelectOnlyKeys(BinaryPatchPlanBuilder.BuildSafeCopyProfilePatchKeys(BinaryPatchPlanBuilder.DebugCameraPreviewProfileId));
            AppStatusService.SetStatus("Windowed & Mods: Debug Camera Preview profile selected");
        }

        private void ClearSelectionButton_Click(object sender, RoutedEventArgs e)
        {
            SelectOnlyKeys(BinaryPatchPlanBuilder.BuildSafeCopyProfilePatchKeys(BinaryPatchPlanBuilder.CustomProfileId));
            AppStatusService.SetStatus("Windowed & Mods: optional mod rows cleared");
        }

        private void MenuColorRedButton_Click(object sender, RoutedEventArgs e)
        {
            SelectFrontendColorPatch("frontend_clear_screen_dark_red", "red menu background selected");
        }

        private void MenuColorGreenButton_Click(object sender, RoutedEventArgs e)
        {
            SelectFrontendColorPatch("frontend_clear_screen_dark_green", "green menu background selected");
        }

        private void MenuColorBlackButton_Click(object sender, RoutedEventArgs e)
        {
            SelectFrontendColorPatch("frontend_clear_screen_black", "black menu background selected");
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
                OperationLogTextBox.Text = $"Patch row is not available: {key}";
                AppStatusService.SetStatus("Windowed & Mods: quick pick unavailable");
                return;
            }

            item.IsSelected = isSelected;
            InvalidateVerification();
            UpdateControlState();
            AppStatusService.SetStatus($"Windowed & Mods: {statusMessage}");
        }

        private void LocalMultiplayerProbeButton_Click(object sender, RoutedEventArgs e)
        {
            _selectedLaunchPresetChoice = LaunchPresetChoice.None;
            ApplyLaunchPreset(new LaunchPresetSelection(
                SkipFmv: true,
                NoMusic: false,
                NoSound: false,
                HighDetail: false,
                NoStaticShadows: false,
                NoRumble: false,
                LevelId: LocalMultiplayerProbeLevelId,
                ControllerConfigurationIndex: 0,
                PersistControllerConfig: false,
                SharpenMouseLook: false,
                MouseSensitivityPresetIndex: DefaultMouseSensitivityPresetIndex,
                InvertWalkerY: false,
                InvertFlightY: false,
                TextureRamLimitMb: string.Empty,
                StatusMessage: PatchBenchLaunchPresetText.BuildLocalMultiplayerProbeStatusMessage()));
            PatchBenchOnlinePrepActionStatus.Text = "Local split-screen launch preset selected. Next: create a safe copy, then play that safe copy. This is not Host/Join or online play.";
            OperationLogTextBox.Text = "Local split-screen preset selected: -skipfmv -level 850. Create safe copy next, then launch that safe copy. No listener, invitation, remote input, or Host/Join control is enabled.";
        }

        private void MaintainerArtifactToolsToggle_Toggled(object sender, RoutedEventArgs e)
        {
            RenderMaintainerArtifactToolsVisibility();
        }

        private void OnlineTechnicalDetailsToggle_Toggled(object sender, RoutedEventArgs e)
        {
            RenderOnlineTechnicalDetailsVisibility();
        }

        private void UpdateSafeCopyBusyState()
        {
            string? status = null;
            if (_isPreparingCopiedProfile)
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

        private async void LoadOnlineReadinessArtifactButton_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                if (App.MainWindowInstance is null)
                {
                    return;
                }

                string? path = await PickerInterop.PickFileAsync(App.MainWindowInstance, new[] { ".json" });
                if (string.IsNullOrWhiteSpace(path))
                {
                    return;
                }

                if (OnlineMultiplayerReadinessService.TryLoadSecondHostReadinessArtifact(
                        path,
                        out OnlineSecondHostReadinessArtifactSummary? artifact,
                        out string? error) &&
                    artifact is not null)
                {
                    _secondHostReadinessArtifactSummary = artifact;
                    RenderOnlineMultiplayerReadiness();
                    OperationLogTextBox.Text = PatchBenchOnlineReadinessText.FormatSecondHostReadinessArtifactStatus(artifact);
                    AppStatusService.SetStatus("Windowed & Mods: loaded redacted second-host readiness summary");
                    return;
                }

                PatchBenchOnlineReadinessArtifactStatus.Text = error ?? "Second-host readiness summary could not be loaded.";
                OperationLogTextBox.Text = PatchBenchOnlineReadinessArtifactStatus.Text;
                AppStatusService.SetStatus("Windowed & Mods: second-host readiness summary rejected");
            }
            catch (Exception ex) when (IsUserFacingOperationException(ex))
            {
                PatchBenchOnlineReadinessArtifactStatus.Text = "Readiness summary load failed.";
                OperationLogTextBox.Text = $"Could not load readiness summary: {ex.Message}";
                AppStatusService.SetStatus("Windowed & Mods: readiness summary load failed");
            }
        }

        private void ClearOnlineReadinessArtifactButton_Click(object sender, RoutedEventArgs e)
        {
            _secondHostReadinessArtifactSummary = null;
            RenderOnlineMultiplayerReadiness();
            OperationLogTextBox.Text = "Second-host readiness summary cleared. Host/Join remain unavailable.";
            AppStatusService.SetStatus("Windowed & Mods: second-host readiness summary cleared");
        }

        private async void LoadDualSafeCopyTopologyArtifactButton_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                if (App.MainWindowInstance is null)
                {
                    return;
                }

                string? path = await PickerInterop.PickFileAsync(App.MainWindowInstance, new[] { ".json" });
                if (string.IsNullOrWhiteSpace(path))
                {
                    return;
                }

                if (OnlineMultiplayerReadinessService.TryLoadDualSafeCopyTopologyArtifact(
                        path,
                        out OnlineDualSafeCopyTopologyArtifactSummary? artifact,
                        out string? error) &&
                    artifact is not null)
                {
                    _dualSafeCopyTopologyArtifactSummary = artifact;
                    RenderOnlineMultiplayerReadiness();
                    OperationLogTextBox.Text = PatchBenchOnlineReadinessText.FormatDualSafeCopyTopologyArtifactStatus(artifact);
                    AppStatusService.SetStatus("Windowed & Mods: loaded dual-safe-copy topology summary");
                    return;
                }

                PatchBenchDualSafeCopyTopologyArtifactStatus.Text = error ?? "Dual-safe-copy topology summary could not be loaded.";
                OperationLogTextBox.Text = PatchBenchDualSafeCopyTopologyArtifactStatus.Text;
                AppStatusService.SetStatus("Windowed & Mods: dual-safe-copy topology summary rejected");
            }
            catch (Exception ex) when (IsUserFacingOperationException(ex))
            {
                PatchBenchDualSafeCopyTopologyArtifactStatus.Text = "Topology summary load failed.";
                OperationLogTextBox.Text = $"Could not load topology summary: {ex.Message}";
                AppStatusService.SetStatus("Windowed & Mods: topology summary load failed");
            }
        }

        private void ClearDualSafeCopyTopologyArtifactButton_Click(object sender, RoutedEventArgs e)
        {
            _dualSafeCopyTopologyArtifactSummary = null;
            RenderOnlineMultiplayerReadiness();
            OperationLogTextBox.Text = "Dual-safe-copy topology summary cleared. Host/Join remain unavailable.";
            AppStatusService.SetStatus("Windowed & Mods: dual-safe-copy topology summary cleared");
        }

        private async void LoadGamepadReadinessArtifactButton_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                if (App.MainWindowInstance is null)
                {
                    return;
                }

                string? path = await PickerInterop.PickFileAsync(App.MainWindowInstance, new[] { ".json" });
                if (string.IsNullOrWhiteSpace(path))
                {
                    return;
                }

                if (OnlineMultiplayerReadinessService.TryLoadLocalGamepadReadinessArtifact(
                        path,
                        out OnlineLocalGamepadReadinessArtifactSummary? artifact,
                        out string? error) &&
                    artifact is not null)
                {
                    _localGamepadReadinessArtifactSummary = artifact;
                    RenderOnlineMultiplayerReadiness();
                    OperationLogTextBox.Text = PatchBenchOnlineReadinessText.FormatLocalGamepadReadinessArtifactStatus(artifact);
                    AppStatusService.SetStatus("Windowed & Mods: loaded local physical controller readiness summary");
                    return;
                }

                PatchBenchGamepadReadinessArtifactStatus.Text = error ?? "Local physical controller readiness summary could not be loaded.";
                OperationLogTextBox.Text = PatchBenchGamepadReadinessArtifactStatus.Text;
                AppStatusService.SetStatus("Windowed & Mods: local physical controller readiness summary rejected");
            }
            catch (Exception ex) when (IsUserFacingOperationException(ex))
            {
                PatchBenchGamepadReadinessArtifactStatus.Text = "Controller readiness summary load failed.";
                OperationLogTextBox.Text = $"Could not load controller readiness summary: {ex.Message}";
                AppStatusService.SetStatus("Windowed & Mods: controller readiness summary load failed");
            }
        }

        private void ClearGamepadReadinessArtifactButton_Click(object sender, RoutedEventArgs e)
        {
            _localGamepadReadinessArtifactSummary = null;
            RenderOnlineMultiplayerReadiness();
            OperationLogTextBox.Text = "Physical controller readiness summary cleared. Host/Join remain unavailable.";
            AppStatusService.SetStatus("Windowed & Mods: physical controller readiness summary cleared");
        }

        private void AdminLevelPresetComboBox_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            int selectedIndex = PatchBenchAdminLevelPresetComboBox.SelectedIndex;
            if (selectedIndex <= NoAdminLevelPresetIndex)
                return;

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
                HighDetail: false,
                NoStaticShadows: false,
                NoRumble: false,
                LevelId: string.Empty,
                ControllerConfigurationIndex: 0,
                PersistControllerConfig: false,
                SharpenMouseLook: false,
                MouseSensitivityPresetIndex: DefaultMouseSensitivityPresetIndex,
                InvertWalkerY: false,
                InvertFlightY: false,
                TextureRamLimitMb: string.Empty,
                StatusMessage: PatchBenchLaunchPresetText.BuildQuietCaptureStatusMessage()));
        }

        private void ControlBaselinePresetButton_Click(object sender, RoutedEventArgs e)
        {
            ApplyLaunchPreset(LaunchPresetChoice.ControlBaseline, new LaunchPresetSelection(
                SkipFmv: true,
                NoMusic: false,
                NoSound: false,
                HighDetail: false,
                NoStaticShadows: false,
                NoRumble: false,
                LevelId: string.Empty,
                ControllerConfigurationIndex: 1,
                PersistControllerConfig: false,
                SharpenMouseLook: false,
                MouseSensitivityPresetIndex: DefaultMouseSensitivityPresetIndex,
                InvertWalkerY: false,
                InvertFlightY: false,
                TextureRamLimitMb: string.Empty,
                StatusMessage: PatchBenchLaunchPresetText.BuildControlBaselineStatusMessage()));
        }

        private void ControlSharpenedPresetButton_Click(object sender, RoutedEventArgs e)
        {
            ApplyLaunchPreset(LaunchPresetChoice.ControlSharpened, new LaunchPresetSelection(
                SkipFmv: true,
                NoMusic: false,
                NoSound: false,
                HighDetail: false,
                NoStaticShadows: false,
                NoRumble: false,
                LevelId: string.Empty,
                ControllerConfigurationIndex: 1,
                PersistControllerConfig: true,
                SharpenMouseLook: true,
                MouseSensitivityPresetIndex: DefaultMouseSensitivityPresetIndex,
                InvertWalkerY: false,
                InvertFlightY: false,
                TextureRamLimitMb: string.Empty,
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
                HighDetail: false,
                NoStaticShadows: false,
                NoRumble: false,
                LevelId: string.Empty,
                ControllerConfigurationIndex: controllerConfigurationIndex,
                PersistControllerConfig: true,
                SharpenMouseLook: false,
                MouseSensitivityPresetIndex: DefaultMouseSensitivityPresetIndex,
                InvertWalkerY: false,
                InvertFlightY: false,
                TextureRamLimitMb: string.Empty,
                StatusMessage: statusMessage);
        }

        private void HighDetailLaunchPresetButton_Click(object sender, RoutedEventArgs e)
        {
            ApplyLaunchPreset(LaunchPresetChoice.HighDetail, new LaunchPresetSelection(
                SkipFmv: true,
                NoMusic: false,
                NoSound: false,
                HighDetail: true,
                NoStaticShadows: false,
                NoRumble: false,
                LevelId: string.Empty,
                ControllerConfigurationIndex: 0,
                PersistControllerConfig: false,
                SharpenMouseLook: false,
                MouseSensitivityPresetIndex: DefaultMouseSensitivityPresetIndex,
                InvertWalkerY: false,
                InvertFlightY: false,
                TextureRamLimitMb: HighDetailTextureRamLimitMb,
                StatusMessage: PatchBenchLaunchPresetText.BuildHighDetailStatusMessage()));
        }

        private void ClearLaunchOptionsButton_Click(object sender, RoutedEventArgs e)
        {
            _selectedLaunchPresetChoice = LaunchPresetChoice.None;
            ApplyLaunchPreset(new LaunchPresetSelection(
                SkipFmv: false,
                NoMusic: false,
                NoSound: false,
                HighDetail: false,
                NoStaticShadows: false,
                NoRumble: false,
                LevelId: string.Empty,
                ControllerConfigurationIndex: 0,
                PersistControllerConfig: false,
                SharpenMouseLook: false,
                MouseSensitivityPresetIndex: DefaultMouseSensitivityPresetIndex,
                InvertWalkerY: false,
                InvertFlightY: false,
                TextureRamLimitMb: string.Empty,
                StatusMessage: PatchBenchLaunchPresetText.BuildClearLaunchOptionsStatusMessage()));
        }

        private void ApplyLaunchPreset(LaunchPresetChoice selectedChoice, LaunchPresetSelection preset)
        {
            _selectedLaunchPresetChoice = selectedChoice;
            ApplyLaunchPreset(preset);
            UpdateLaunchPresetVisualState();
            _ = DispatcherQueue.TryEnqueue(() =>
            {
                _selectedLaunchPresetChoice = selectedChoice;
                UpdateLaunchPresetVisualState();
            });
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
                PatchBenchHighDetailLaunchOption.IsChecked = preset.HighDetail;
                PatchBenchNoStaticShadowsLaunchOption.IsChecked = preset.NoStaticShadows;
                PatchBenchNoRumbleLaunchOption.IsChecked = preset.NoRumble;
                PatchBenchShowDebugTraceLaunchOption.IsChecked = false;
                PatchBenchLevelLaunchOption.Text = preset.LevelId;
                PatchBenchConfigurationLaunchPresetComboBox.SelectedIndex = Math.Clamp(preset.ControllerConfigurationIndex, 0, 4);
                PatchBenchPersistControllerConfigOption.IsChecked = preset.PersistControllerConfig;
                PatchBenchSharpenMouseLookOption.IsChecked = preset.SharpenMouseLook;
                PatchBenchMouseSensitivityPresetComboBox.SelectedIndex = Math.Clamp(preset.MouseSensitivityPresetIndex, 0, s_mouseLookSensitivityPresets.Length - 1);
                PatchBenchInvertWalkerYOption.IsChecked = preset.InvertWalkerY;
                PatchBenchInvertFlightYOption.IsChecked = preset.InvertFlightY;
                PatchBenchTextureRamLimitLaunchOption.Text = preset.TextureRamLimitMb;
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
            if (IsLaunchPresetOwnedTextBox(sender))
            {
                ClearSelectedLaunchPresetChoiceForManualEdit();
            }

            RefreshCopiedProfileLaunchPlanPreview();
            UpdateControlState();
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
                OperationLogTextBox.Text = $"Could not browse for BEA.exe: {ex.Message}";
                AppStatusService.SetStatus("Windowed & Mods: browse failed");
            }
        }

        private void UseGameDirButton_Click(object sender, RoutedEventArgs e)
        {
            if (LoadSourcePathFromConfig())
            {
                AppStatusService.SetStatus("Windowed & Mods: loaded source path from shared settings");
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
            catch (Exception ex)
            {
                OperationLogTextBox.Text = $"Could not create BEA.exe-only copy: {ex.Message}";
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
                OperationLogTextBox.Text = "Create an app-owned BEA.exe-only copy before verification.";
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
                OperationLogTextBox.Text = "Create an app-owned BEA.exe-only copy before applying patches.";
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
                        "The selected verified catalog patches will be applied to the app-owned BEA.exe-only copy only. The original BEA.exe stays unchanged. Restore uses the first full-file backup snapshot, not a per-patch undo."))
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
                OperationLogTextBox.Text = $"Could not apply patches to BEA.exe-only copy: {ex.Message}";
                AppStatusService.SetStatus("Windowed & Mods: apply failed");
                UpdateControlState();
            }
        }

        private async void RestoreButton_Click(object sender, RoutedEventArgs e)
        {
            string exePath = (ExePathTextBox.Text ?? string.Empty).Trim();
            if (!IsUsableWorkingCopy(exePath))
            {
                OperationLogTextBox.Text = "Create an app-owned BEA.exe-only copy before restoring patch backups.";
                AppStatusService.SetStatus("Windowed & Mods: BEA.exe-only copy required");
                UpdateControlState();
                return;
            }

            if (!File.Exists(BinaryPatchEngine.BuildBackupPath(exePath)))
            {
                OperationLogTextBox.Text = "Backup file not found for the selected executable.";
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
                OperationLogTextBox.Text = $"Could not restore BEA.exe-only backup: {ex.Message}";
                AppStatusService.SetStatus("Windowed & Mods: restore failed");
                UpdateControlState();
            }
        }

        private async void PrepareCopiedProfileButton_Click(object sender, RoutedEventArgs e)
        {
            if (_isPreparingCopiedProfile)
            {
                OperationLogTextBox.Text = "Safe game copy preparation is already running.";
                AppStatusService.SetStatus("Windowed & Mods: safe copy preparation already running");
                return;
            }

            string sourcePath = (SourceExePathTextBox.Text ?? string.Empty).Trim();
            if (!IsBattleEngineExecutableSourcePath(sourcePath) || !File.Exists(sourcePath))
            {
                OperationLogTextBox.Text = "Select a valid source BEA.exe or BEA.exe.original.backup before preparing a safe game copy.";
                AppStatusService.SetStatus("Windowed & Mods: missing safe copy source");
                UpdateControlState();
                return;
            }

            string? sourceGameRoot = Path.GetDirectoryName(Path.GetFullPath(sourcePath));
            if (string.IsNullOrWhiteSpace(sourceGameRoot) || !Directory.Exists(sourceGameRoot))
            {
                OperationLogTextBox.Text = "The selected BEA.exe does not have a usable source game folder.";
                AppStatusService.SetStatus("Windowed & Mods: safe copy source folder missing");
                UpdateControlState();
                return;
            }

            bool includeSavegames = PatchBenchIncludeSavegamesOption.IsChecked == true;
            string[] selectedPatchKeys = GetVisibleSelectedKeys().ToArray();
            string? createMusicSwapPresetId = GetSelectedCreateMusicSwapPresetId();
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
                MusicSwapPresetId: createMusicSwapPresetId);

            if (!await ConfirmAsync(
                    "Create safe copy?",
                    $"The app will copy the selected game folder into its own safe workspace, then patch only that copied BEA.exe.\n\nSource folder:\n{sourceGameRoot}\n\nDestination root:\n{options.OutputRoot}\n\nThis can take a few minutes and may require several GB of free disk space. The Steam/game install stays unchanged."))
            {
                PatchBenchCopiedProfileSummary.Text = PatchBenchSafeCopyOutcomeText.BuildCanceledSummary();
                OperationLogTextBox.Text = PatchBenchSafeCopyOutcomeText.BuildCanceledOperationLog();
                AppStatusService.SetStatus("Windowed & Mods: safe copy creation canceled");
                return;
            }

            try
            {
                _isPreparingCopiedProfile = true;
                PatchBenchPrepareCopiedProfileButton.IsEnabled = false;
                PatchBenchLaunchCopiedProfileButton.IsEnabled = false;
                UpdateControlState();
                PatchBenchCopiedProfileSummary.Text = "Creating safe game copy. This can take a few minutes for a full game folder...";
                PatchBenchCopiedProfileLaunchPlan.Text = string.Empty;
                PatchBenchCopiedProfileLaunchStatus.Text = PatchBenchLaunchText.BuildBoundary("No safe copy launch attempted.");
                OperationLogTextBox.Text = "Preparing a safe game copy in the app-owned GameProfiles workspace. The selected Steam/game install stays unchanged.";
                AppStatusService.SetStatus("Windowed & Mods: preparing safe copy");

                GameProfilePrepareResult result = await Task.Run(() =>
                    GameProfilePreflightService.PrepareWindowedCompatibilityProfile(options));
                GameProfileControlOptionsResult? controlOptionsResult = null;
                uint? persistedControllerConfig = PatchBenchPersistControllerConfigOption.IsChecked == true
                    ? GetSelectedControllerConfigurationPreset()
                    : null;
                float? mouseLookSensitivity = GetSelectedMouseLookSensitivityPreset();
                bool invertWalkerY = PatchBenchInvertWalkerYOption.IsChecked == true;
                bool invertFlightY = PatchBenchInvertFlightYOption.IsChecked == true;
                if (mouseLookSensitivity.HasValue ||
                    persistedControllerConfig.HasValue ||
                    invertWalkerY ||
                    invertFlightY)
                {
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
                                InvertFlightP2Override: invertFlightY ? true : null)));
                }

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
                    LaunchModifierSummary: PatchBenchLaunchText.BuildModifierSummary(result.LaunchPlan.Arguments));
                PatchBenchCopiedProfileSummary.Text = PatchBenchSafeCopyOutcomeText.BuildPreparedSummary(outcomeText);
                PatchBenchCopiedProfileLaunchPlan.Text = result.LaunchPlan.CommandPreview;
                PatchBenchCopiedProfileLaunchStatus.Text =
                    PatchBenchLaunchText.BuildBoundary("Safe copy ready for a guarded launch attempt.");
                PatchBenchMusicReplacementStatus.Text = PatchBenchSafeCopyOutcomeText.BuildMusicReplacementStatus(outcomeText.MusicSwap);
                OperationLogTextBox.Text = PatchBenchSafeCopyOutcomeText.BuildPreparedOperationLog(outcomeText);
                AppStatusService.SetStatus("Windowed & Mods: safe copy ready");
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
                OperationLogTextBox.Text = $"Could not prepare safe game copy: {ex.Message}";
                AppStatusService.SetStatus("Windowed & Mods: safe copy preparation failed");
            }
            finally
            {
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
                        $"The app will launch BEA.exe from the safe game copy only.\n\nSafe copy: {plan.WorkingDirectory}\n{PatchBenchLaunchText.BuildModifierSummary(plan.Arguments)}\n\nThe Steam/game install stays unchanged. The game may take focus, switch display modes, fail to start, or exit. Any manual input after launch is not counted as automated proof."))
                {
                    AppStatusService.SetStatus("Windowed & Mods: safe copy launch canceled");
                    return;
                }

                PatchBenchCopiedProfileLaunchStatus.Text = "Launching safe copy...";
                OperationLogTextBox.Text = "Launching the safe game copy after manifest, hash, and patch verification.";
                AppStatusService.SetStatus("Windowed & Mods: launching safe copy");

                GameProfileManagedProcess launched = await Task.Run(() =>
                    GameProfileRuntimeService.LaunchCopiedProfile(
                        new GameProfileLaunchOptions(
                            ProfileRoot: plan.WorkingDirectory,
                            AppOwnedProfilesRoot: GetCopiedProfileWorkspaceRoot(),
                            LaunchArguments: BuildSelectedLaunchArguments())));

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
                OperationLogTextBox.Text = $"Could not launch safe copy: {ex.Message}";
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
                PatchBenchCopiedProfileLaunchStatus.Text = "No managed safe copy process is active.";
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
                OperationLogTextBox.Text = result.Message;
                AppStatusService.SetStatus(result.Success ? "Windowed & Mods: safe copy stopped" : "Windowed & Mods: safe copy stop failed");
            }
            catch (Exception ex) when (IsUserFacingOperationException(ex))
            {
                PatchBenchCopiedProfileLaunchStatus.Text = "Safe copy stop failed.";
                OperationLogTextBox.Text = $"Could not stop safe copy: {ex.Message}";
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
                OperationLogTextBox.Text = $"Could not stage safe-copy music preset: {ex.Message}";
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
                ? "Copying one safe-copy OGG track over another safe-copy OGG track. The original install stays unchanged."
                : "Staging one replacement OGG into the safe copy. The original install stays unchanged.";
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
                OperationLogTextBox.Text =
                    (copiedTrackSwap ? "Safe-copy track swap staged.\n" : "Copied music bytes staged.\n") +
                    $"Target: {result.TargetRelativePath}\n" +
                    $"Replacement source: {Path.GetFileName(replacementPath)}\n" +
                    $"Backup: {result.BackupRelativePath}\n" +
                    "Manifest written without absolute source paths.\n" +
                    "Original install remains unchanged; runtime audio playback is not proven.";
                AppStatusService.SetStatus(copiedTrackSwap ? "Windowed & Mods: safe-copy music swap staged" : "Windowed & Mods: music replacement staged");
            }
            catch (Exception ex) when (IsUserFacingOperationException(ex))
            {
                PatchBenchMusicReplacementStatus.Text = PatchBenchSafeCopyOutcomeText.BuildMusicStagingFailedStatus();
                OperationLogTextBox.Text = $"Could not stage copied music bytes: {ex.Message}";
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
                OperationLogTextBox.Text = result.Message;
                AppStatusService.SetStatus(result.Success ? "Windowed & Mods: music backup restored" : "Windowed & Mods: music restore failed");
            }
            catch (Exception ex) when (IsUserFacingOperationException(ex))
            {
                PatchBenchMusicReplacementStatus.Text = PatchBenchSafeCopyOutcomeText.BuildMusicRestoreFailedStatus();
                OperationLogTextBox.Text = $"Could not restore safe-copy music backup: {ex.Message}";
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
            return BuildSafeCopyContentSignature(
                sourcePath,
                includeSavegames,
                mouseLookSensitivity,
                persistedControllerConfig,
                invertWalkerY,
                invertFlightY,
                createMusicSwapPresetId,
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
            return $"source={normalizedSourcePath}|savegames={includeSavegames}|mouseLookSensitivity={mouseSensitivityToken}|persistedControllerConfig={persistedControllerConfigToken}|invertWalkerY={invertWalkerY}|invertFlightY={invertFlightY}|createMusicSwapPreset={createMusicSwapPresetToken}|effectivePatches={string.Join(",", normalizedPatchKeys)}";
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
                ? "BEA.exe in the app advanced patch workspace."
                : "Create an app-owned BEA.exe-only copy before verification or patching.";
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
                    result.InvertFlightP2);
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
            if (!App.SafeGameCopyProcesses.TryGetLatest(out GameProfileRegisteredProcess registered))
            {
                return;
            }

            _managedCopiedProfileProcess = registered.Process;
            _lastCopiedProfileRoot = registered.Process.WorkingDirectory;
            PatchBenchCopiedProfileSummary.Text = PatchBenchSafeCopyOutcomeText.BuildRestoredTrackedLaunchSummary();
            PatchBenchCopiedProfileReceipt.Text = PatchBenchSafeCopyOutcomeText.BuildRestoredTrackedLaunchReceipt();
            PatchBenchCopiedProfileLaunchStatus.Text = PatchBenchSafeCopyOutcomeText.BuildRestoredTrackedLaunchStatus();
            PatchBenchCopiedProfileLaunchPlan.Text =
                $"\"{registered.Process.ExecutablePath}\" {string.Join(" ", registered.Process.Arguments)}".TrimEnd();
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
            if (string.IsNullOrWhiteSpace(message) || string.IsNullOrWhiteSpace(exePath))
            {
                return message;
            }

            string backupPath = BinaryPatchEngine.BuildBackupPath(exePath);
            string formatted = message.Replace(backupPath, "BEA.exe-only backup snapshot", StringComparison.OrdinalIgnoreCase);
            return formatted.Replace(exePath, "app-owned BEA.exe-only copy", StringComparison.OrdinalIgnoreCase);
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

        private IReadOnlyList<string> BuildSelectedLaunchArguments()
        {
            var args = new List<string>();
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

            if (PatchBenchHighDetailLaunchOption.IsChecked == true)
            {
                args.Add("-hidetail");
            }

            if (PatchBenchNoStaticShadowsLaunchOption.IsChecked == true)
            {
                args.Add("-nostaticshadows");
            }

            if (PatchBenchNoRumbleLaunchOption.IsChecked == true)
            {
                args.Add("-norumble");
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

            uint? selectedControllerConfig = GetSelectedControllerConfigurationPreset();
            if (selectedControllerConfig.HasValue)
            {
                args.Add("-configuration");
                args.Add(selectedControllerConfig.Value.ToString(System.Globalization.CultureInfo.InvariantCulture));
            }

            string textureRamMb = (PatchBenchTextureRamLimitLaunchOption.Text ?? string.Empty).Trim();
            if (textureRamMb.Length > 0)
            {
                args.Add("-textureramlimit");
                if (int.TryParse(textureRamMb, out int megabytes))
                {
                    long bytes = (long)megabytes * 1024L * 1024L;
                    args.Add(bytes.ToString(System.Globalization.CultureInfo.InvariantCulture));
                }
                else
                {
                    args.Add(textureRamMb);
                }
            }

            return args;
        }

        private uint? GetSelectedControllerConfigurationPreset()
        {
            int configurationIndex = PatchBenchConfigurationLaunchPresetComboBox.SelectedIndex;
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
                error = ex.Message;
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
    }
}
