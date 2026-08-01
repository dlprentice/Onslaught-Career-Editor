using System;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Automation;
using Microsoft.UI.Xaml.Controls;
using OnslaughtCareerEditor.WinUI.Helpers;
using Onslaught___Career_Editor;

namespace OnslaughtCareerEditor.WinUI.Pages
{
    public sealed partial class HomePage : Page
    {
        private enum HomeGameFolderState
        {
            Unset,
            Invalid,
            Ready,
        }

        private const string ProfileManifestFileName = "onslaught-profile-manifest.json";

        private HomeQuickStartState _quickStart = HomeQuickStartState.Resolve(false, false, false, false);

        public HomePage()
        {
            InitializeComponent();
            RefreshSetupStatus();
            AppStatusService.SetStatus("Home: choose a task");
        }

        public void RefreshForNavigation()
        {
            RefreshSetupStatus();
        }

        /// <summary>
        /// Shows what the app already knows about this machine. Home used to be
        /// a static brochure even though the install path, save count, and
        /// media readiness were all computed elsewhere on every launch.
        /// </summary>
        private void RefreshSnapshot(string? gameDir, GameDirectoryInspection inspection)
        {
            bool ready = inspection.Status == GameDirectoryStatus.FullInstall;

            HomeSnapshotGameTextBlock.Text = ready && !string.IsNullOrWhiteSpace(gameDir)
                ? Path.GetFileName(gameDir.TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar))
                : "Not set yet";

            if (string.IsNullOrWhiteSpace(gameDir))
            {
                HomeSnapshotSavesTextBlock.Text = "—";
                HomeSnapshotMediaTextBlock.Text = "—";
                return;
            }

            try
            {
                int saveCount = AppConfig.FindSaveFiles(gameDir).Count;
                HomeSnapshotSavesTextBlock.Text = saveCount switch
                {
                    0 => "None yet",
                    1 => "1 file",
                    _ => $"{saveCount} files",
                };
            }
            catch (Exception)
            {
                HomeSnapshotSavesTextBlock.Text = "Unavailable";
            }

            HomeSnapshotMediaTextBlock.Text = ready ? "Ready to browse" : "Needs the full install";
        }

        private void RefreshSetupStatus()
        {
            AppConfig config = AppConfig.Load();
            string? configuredPath = config.GameDirectory;
            string? gameDir = config.GetGameDirOrDetect(persistDetection: true);
            GameDirectoryInspection inspection = AppConfig.InspectGameDirectory(gameDir);
            RefreshSnapshot(gameDir, inspection);
            RefreshQuickStart(gameDir, inspection);
            HomeGameFolderState state = inspection.Status == GameDirectoryStatus.FullInstall
                ? HomeGameFolderState.Ready
                : string.IsNullOrWhiteSpace(configuredPath)
                    ? HomeGameFolderState.Unset
                    : HomeGameFolderState.Invalid;

            HomeSetupInfoBar.IsOpen = state != HomeGameFolderState.Ready;
            HomeSetupInfoBar.Severity = state == HomeGameFolderState.Invalid
                ? InfoBarSeverity.Warning
                : InfoBarSeverity.Informational;

            if (state == HomeGameFolderState.Unset)
            {
                // Deliberately terse: the quick-start card directly below makes
                // the invitation and offers to find the folder automatically.
                // This bar exists so keyboard and screen-reader users land on a
                // setup action on arrival, so it should not restate the card.
                HomeSetupInfoBar.Title = "Game folder not set";
                HomeSetupInfoBar.Message = "Save Lab still opens files you pick yourself.";
                HomeSetupActionButton.Content = "Choose game folder";
                AutomationProperties.SetName(HomeSetupActionButton, "Choose game folder");
                SetupTitleTextBlock.Text = "Setup not finished";
                SetupStatusTextBlock.Text = "Game folder not set. The app needs the full Battle Engine Aquila folder for Media and playable safe copies.";
                SetupGuidanceTextBlock.Text = "Save Lab still works with files you choose manually. Setting the folder also enables automatic save detection.";
                return;
            }

            if (state == HomeGameFolderState.Invalid)
            {
                HomeSetupInfoBar.Title = "Game folder needs a look";
                HomeSetupInfoBar.Message = "Save Lab still opens files you pick yourself.";
                HomeSetupActionButton.Content = "Review game folder";
                AutomationProperties.SetName(HomeSetupActionButton, "Review game folder");
                SetupTitleTextBlock.Text = "Setup needs attention";
                SetupStatusTextBlock.Text = "The saved game folder is missing or incomplete. Review it in Settings before using Media or playable safe copies.";
                SetupGuidanceTextBlock.Text = "Save Lab still works with files you choose manually; the installed game remains read-only.";
                return;
            }

            string folderName = string.IsNullOrWhiteSpace(gameDir)
                ? string.Empty
                : Path.GetFileName(gameDir.TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar));
            HomeSetupInfoBar.Title = "Game folder ready";
            HomeSetupInfoBar.Message = string.Empty;
            SetupTitleTextBlock.Text = "Setup";
            SetupStatusTextBlock.Text = string.IsNullOrWhiteSpace(folderName)
                ? "Game directory configured."
                : $"Game directory configured: {folderName}.";
            SetupGuidanceTextBlock.Text = "Windowed & Mods creates a safe game copy, patches only that copy, and plays only that copy without changing the Steam/game install.";
        }

        /// <summary>
        /// Rebuilds the quick-start card. There is exactly one sensible next
        /// action at any moment, and this decides which.
        /// </summary>
        private void RefreshQuickStart(string? gameDir, GameDirectoryInspection inspection)
        {
            bool running = App.SafeGameCopyProcesses.Snapshot().Count > 0;
            bool copyExists = false;
            try
            {
                string profilesRoot = AppConfig.GetGameProfilesDir();
                copyExists = Directory.Exists(profilesRoot) &&
                    Directory.EnumerateDirectories(profilesRoot)
                        .Any(directory => File.Exists(Path.Combine(directory, ProfileManifestFileName)));
            }
            catch (Exception)
            {
                // A missing or unreadable profiles folder simply means no copy yet.
            }

            _quickStart = HomeQuickStartState.Resolve(
                gameFolderSet: !string.IsNullOrWhiteSpace(gameDir),
                gameFolderComplete: inspection.Status == GameDirectoryStatus.FullInstall,
                safeCopyExists: copyExists,
                safeCopyRunning: running);

            HomeQuickStartTitleTextBlock.Text = _quickStart.Title;
            HomeQuickStartBodyTextBlock.Text = _quickStart.Body;
            HomeQuickStartPrimaryButton.Content = _quickStart.PrimaryActionLabel;
            AutomationProperties.SetName(HomeQuickStartPrimaryButton, _quickStart.PrimaryActionLabel);
            HomeQuickStartChooseFolderButton.Visibility = _quickStart.ShowsSecondaryChooseFolder
                ? Visibility.Visible
                : Visibility.Collapsed;
        }

        private void SetQuickStartBusy(bool busy, string? label)
        {
            HomeQuickStartProgressRing.IsActive = busy;
            HomeQuickStartPrimaryButton.IsEnabled = !busy;
            HomeQuickStartChooseFolderButton.IsEnabled = !busy;
            if (label is not null)
            {
                HomeQuickStartPrimaryButton.Content = label;
            }
        }

        private void ShowQuickStartNote(string? note)
        {
            HomeQuickStartNoteTextBlock.Text = note ?? string.Empty;
            HomeQuickStartNoteTextBlock.Visibility = string.IsNullOrWhiteSpace(note)
                ? Visibility.Collapsed
                : Visibility.Visible;
        }

        private async void HomeQuickStartPrimaryButton_Click(object sender, RoutedEventArgs e)
        {
            ShowQuickStartNote(null);

            switch (_quickStart.Stage)
            {
                case HomeQuickStartStage.FindGame:
                case HomeQuickStartStage.FixGame:
                    FindGameFolder();
                    return;

                case HomeQuickStartStage.Running:
                    App.MainWindowInstance?.NavigateToTag("binary");
                    return;

                case HomeQuickStartStage.MakeCopy:
                    await SetUpAndPlayAsync(createFirst: true);
                    return;

                default:
                    await SetUpAndPlayAsync(createFirst: false);
                    return;
            }
        }

        private void FindGameFolder()
        {
            string? detected = AppConfig.DetectGameDirectory();
            if (string.IsNullOrWhiteSpace(detected))
            {
                ShowQuickStartNote("Could not find the game automatically. Choose the folder you installed it into - the one holding BEA.exe.");
                AppStatusService.SetStatus("Home: game folder not found automatically");
                return;
            }

            AppConfig config = AppConfig.Load();
            if (!config.SetGameDir(detected))
            {
                ShowQuickStartNote("Found the game but could not save that location. Try choosing the folder yourself.");
                return;
            }

            AppConfigChangedService.NotifyChanged(config);
            App.MainWindowInstance?.RefreshFooter();
            ShowQuickStartNote($"Found it: {Path.GetFileName(detected.TrimEnd(Path.DirectorySeparatorChar))}.");
            AppStatusService.SetStatus("Home: found the game");
            RefreshSetupStatus();
        }

        private void HomeQuickStartChooseFolderButton_Click(object sender, RoutedEventArgs e)
        {
            App.MainWindowInstance?.NavigateToTag("settings");
        }

        /// <summary>
        /// The whole point of the card: from "I just installed this" to a
        /// running game without reading anything. Makes a playable copy if
        /// there is not one, then starts it.
        /// </summary>
        private async Task SetUpAndPlayAsync(bool createFirst)
        {
            try
            {
                string profilesRoot = AppConfig.GetGameProfilesDir();
                Directory.CreateDirectory(profilesRoot);
                string? profileRoot = null;

                if (createFirst)
                {
                    SetQuickStartBusy(true, HomeQuickStartState.WorkingLabel);
                    AppStatusService.SetStatus("Home: making your playable copy");

                    AppConfig config = AppConfig.Load();
                    string? source = config.GetGameDirOrDetect(persistDetection: true) ?? config.GameDirectory;
                    if (string.IsNullOrWhiteSpace(source))
                    {
                        ShowQuickStartNote("The game folder is not set any more. Choose it again.");
                        return;
                    }

                    string name = $"safe-game-copy-{DateTime.Now:yyyyMMdd-HHmmss}";
                    var options = new GameProfilePrepareOptions(
                        SourceGameRoot: source,
                        OutputRoot: profilesRoot,
                        ProfileName: name,
                        ApplyWindowedCompatibilityPatch: true,
                        AllowByteLayoutOnlyTarget: false,
                        LaunchArguments: BinaryPatchPlanBuilder
                            .GetSafeCopyProfilePreset(BinaryPatchPlanBuilder.CompatibilityProfileId)
                            .Modules
                            .SelectMany(module => module.LaunchArguments)
                            .ToArray(),
                        ProfilePresetId: BinaryPatchPlanBuilder.CompatibilityProfileId);

                    GameProfilePrepareResult prepared = await Task.Run(
                        () => GameProfilePreflightService.PrepareWindowedCompatibilityProfile(options));

                    if (prepared.PatchResult.Requested && !prepared.PatchResult.Success)
                    {
                        ShowQuickStartNote(prepared.PatchResult.Message);
                        AppStatusService.SetStatus("Home: could not prepare the copy");
                        return;
                    }

                    profileRoot = prepared.TargetGameRoot;
                }
                else
                {
                    profileRoot = Directory.EnumerateDirectories(profilesRoot)
                        .Where(directory => File.Exists(Path.Combine(directory, ProfileManifestFileName)))
                        .OrderByDescending(Directory.GetLastWriteTimeUtc)
                        .FirstOrDefault();

                    if (profileRoot is null)
                    {
                        ShowQuickStartNote("The playable copy is gone. Make a new one.");
                        RefreshSetupStatus();
                        return;
                    }
                }

                SetQuickStartBusy(true, HomeQuickStartState.LaunchingLabel);
                GameProfileLaunchPlan plan = GameProfilePreflightService.BuildLaunchPlan(profileRoot, null);
                GameProfileManagedProcess launched = GameProfileRuntimeService.LaunchCopiedProfile(
                    new GameProfileLaunchOptions(
                        ProfileRoot: plan.WorkingDirectory,
                        AppOwnedProfilesRoot: profilesRoot,
                        LaunchArguments: plan.Arguments));

                App.SafeGameCopyProcesses.Register(launched, profilesRoot);
                ShowQuickStartNote("The game is starting in its own copy. Your installed game is untouched.");
                AppStatusService.SetStatus("Home: started your copy of the game");
            }
            catch (Exception ex) when (ex is InvalidOperationException or IOException
                                        or UnauthorizedAccessException or DirectoryNotFoundException
                                        or System.ComponentModel.Win32Exception)
            {
                ShowQuickStartNote($"That did not work, and nothing was changed. {ex.Message}");
                AppStatusService.SetStatus("Home: setup did not finish");
            }
            finally
            {
                SetQuickStartBusy(false, null);
                RefreshSetupStatus();
            }
        }

        private void NavigateButton_Click(object sender, RoutedEventArgs e)
        {
            if (sender is Button { Tag: string tag })
            {
                App.MainWindowInstance?.NavigateToTag(tag);
            }
        }

        private void OpenConfigurationEditorButton_Click(object sender, RoutedEventArgs e)
        {
            App.MainWindowInstance?.NavigateToTag("saves", saveSubTab: 2);
        }
    }
}
