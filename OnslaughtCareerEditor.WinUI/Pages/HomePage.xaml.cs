using System.IO;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Automation;
using Microsoft.UI.Xaml.Controls;
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

        private void RefreshSetupStatus()
        {
            AppConfig config = AppConfig.Load();
            string? configuredPath = config.GameDirectory;
            string? gameDir = config.GetGameDirOrDetect(persistDetection: true);
            GameDirectoryInspection inspection = AppConfig.InspectGameDirectory(gameDir);
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
                HomeSetupInfoBar.Title = "Choose your game folder";
                HomeSetupInfoBar.Message = "Set the installed game folder once to enable automatic save discovery, Media, and playable safe copies. Save Lab can still open files you choose manually.";
                HomeSetupActionButton.Content = "Choose game folder";
                AutomationProperties.SetName(HomeSetupActionButton, "Choose game folder");
                SetupTitleTextBlock.Text = "Setup not finished";
                SetupStatusTextBlock.Text = "Game folder not set. The app needs the full Battle Engine Aquila folder for Media and playable safe copies.";
                SetupGuidanceTextBlock.Text = "Save Lab still works with files you choose manually. Setting the folder also enables automatic save detection.";
                return;
            }

            if (state == HomeGameFolderState.Invalid)
            {
                HomeSetupInfoBar.Title = "Review your game folder";
                HomeSetupInfoBar.Message = "The saved folder is missing or incomplete. Choose the full Battle Engine Aquila install. Save Lab can still open files you choose manually.";
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
