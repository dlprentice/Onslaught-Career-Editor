using System.IO;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using OnslaughtCareerEditor.WinUI.Helpers;
using Onslaught___Career_Editor;

namespace OnslaughtCareerEditor.WinUI.Pages
{
    public sealed partial class SettingsPage : Page
    {
        private bool _isLoadingSettings;

        public SettingsPage()
        {
            InitializeComponent();
            LoadSettings();
        }

        private void LoadSettings()
        {
            _isLoadingSettings = true;

            AppConfig config = AppConfig.Load();
            string? gameDir = config.GetGameDirOrDetect(persistDetection: true) ?? config.GameDirectory;

            RenderGameDirectory(gameDir);
            if (!string.IsNullOrWhiteSpace(gameDir))
            {
                ValidateGameDirectory(gameDir);
            }
            else
            {
                GameDirectoryStatusTextBlock.Text = "No game directory set. Click Browse or Auto-Detect.";
                GameDirectoryStatusTextBlock.Foreground = ThemeBrushes.Warning();
            }

            AllowBackgroundAudioToggle.IsOn = config.AllowBackgroundAudio;
            AllowBackgroundVideoToggle.IsOn = config.AllowBackgroundVideo;
            PreventOverlapToggle.IsOn = config.PreventAudioVideoOverlap;

            UpdateSaveFileInfo(gameDir);
            ConfigPathTextBlock.Text = AppConfig.GetConfigPath();

            _isLoadingSettings = false;
            AppStatusService.SetStatus("Settings: loaded shared configuration");
        }

        private void RenderGameDirectory(string? gameDir)
        {
            GameDirectoryInspection inspection = AppConfig.InspectGameDirectory(gameDir);
            bool isFullInstall = inspection.Status == GameDirectoryStatus.FullInstall;
            GameDirectoryTextBox.Text = gameDir ?? string.Empty;
            GameDirectorySummaryTextBlock.Text = string.IsNullOrWhiteSpace(gameDir)
                ? "Not configured"
                : BuildFolderSummary(gameDir, isFullInstall ? "Configured install" : "Saved folder needs review");
            GameDirectoryRoleTextBlock.Text = string.IsNullOrWhiteSpace(gameDir)
                ? "Choose your installed game folder. The app reads it to create playable copies; it does not edit that folder."
                : isFullInstall
                    ? "Read-only source material. Editing and patching workflows use copied files or app-managed working folders."
                    : "This saved folder is incomplete. Choose the full install before using automatic discovery, Media, or playable safe copies.";
        }

        private void ValidateGameDirectory(string path)
        {
            if (!Directory.Exists(path))
            {
                GameDirectoryStatusTextBlock.Text = "Directory does not exist.";
                GameDirectoryStatusTextBlock.Foreground = ThemeBrushes.Danger();
                return;
            }

            GameDirectoryInspection inspection = AppConfig.InspectGameDirectory(path);

            if (inspection.Status == GameDirectoryStatus.FullInstall)
            {
                GameDirectoryStatusTextBlock.Text = "Valid game directory detected (with executable and data).";
                GameDirectoryStatusTextBlock.Foreground = ThemeBrushes.Success();
            }
            else if (inspection.Status == GameDirectoryStatus.MediaOnly)
            {
                GameDirectoryStatusTextBlock.Text = "Partial game directory detected: media/data is present, but BEA.exe is missing. Choose the full install before using Media or playable safe copies.";
                GameDirectoryStatusTextBlock.Foreground = ThemeBrushes.Warning();
            }
            else if (inspection.Status == GameDirectoryStatus.ExecutableOnly)
            {
                GameDirectoryStatusTextBlock.Text = "Partial game directory detected: BEA.exe is present, but the data folder is missing. Choose the full game folder before using media or safe-copy workflows.";
                GameDirectoryStatusTextBlock.Foreground = ThemeBrushes.Warning();
            }
            else
            {
                GameDirectoryStatusTextBlock.Text = "Warning: this does not look like a full BEA installation yet.";
                GameDirectoryStatusTextBlock.Foreground = ThemeBrushes.Warning();
            }
        }

        private void UpdateSaveFileInfo(string? gameDir)
        {
            if (string.IsNullOrWhiteSpace(gameDir))
            {
                SaveDirectoryTextBlock.Text = "Game directory not configured";
                SaveFileCountTextBlock.Text = "Set the game directory to enable save/options file detection.";
                return;
            }

            var saves = AppConfig.FindSaveFiles(gameDir);
            if (saves.Count == 0)
            {
                SaveDirectoryTextBlock.Text = "No save/options files found";
                SaveFileCountTextBlock.Text = "Create a save/options file in-game first, or verify the selected install path.";
                return;
            }

            string? firstDir = Path.GetDirectoryName(saves[0].Path);
            SaveDirectoryTextBlock.Text = BuildFolderSummary(firstDir, "Detected save folder");
            SaveFileCountTextBlock.Text = $"Found {saves.Count} save/options file(s). Open Save Lab to inspect or patch copies; full local paths stay out of this summary.";
        }

        private async void BrowseGameDirectoryButton_Click(object sender, RoutedEventArgs e)
        {
            if (App.MainWindowInstance is null)
            {
                return;
            }

            string? path = await PickerInterop.PickFolderAsync(App.MainWindowInstance);
            if (!string.IsNullOrWhiteSpace(path))
            {
                SetGameDirectory(path);
            }
        }

        private void AutoDetectGameDirectoryButton_Click(object sender, RoutedEventArgs e)
        {
            string? detected = AppConfig.DetectGameDirectory();
            if (string.IsNullOrWhiteSpace(detected))
            {
                AppStatusService.SetStatus("Settings: could not auto-detect the game directory");
                return;
            }

            SetGameDirectory(detected);
        }

        private void SetGameDirectory(string path)
        {
            RenderGameDirectory(path);
            ValidateGameDirectory(path);

            if (!Directory.Exists(path))
            {
                AppStatusService.SetStatus("Settings: game directory path is invalid");
                return;
            }

            AppConfig config = AppConfig.Load();
            if (!config.SetGameDir(path))
            {
                AppStatusService.SetStatus("Settings: failed to save game directory");
                return;
            }

            UpdateSaveFileInfo(path);
            AppConfigChangedService.NotifyChanged(config);
            App.MainWindowInstance?.RefreshFooter();
            AppStatusService.SetStatus(
                AppConfig.InspectGameDirectory(path).Status == GameDirectoryStatus.FullInstall
                    ? "Settings: game directory updated"
                    : "Settings: folder saved but the full game install is still required");
        }

        private void MediaPreferenceChanged(object sender, RoutedEventArgs e)
        {
            if (_isLoadingSettings)
            {
                return;
            }

            AppConfig config = AppConfig.Load();
            config.GameDirectory = string.IsNullOrWhiteSpace(GameDirectoryTextBox.Text) ? null : GameDirectoryTextBox.Text;
            config.AllowBackgroundAudio = AllowBackgroundAudioToggle.IsOn;
            config.AllowBackgroundVideo = AllowBackgroundVideoToggle.IsOn;
            config.PreventAudioVideoOverlap = PreventOverlapToggle.IsOn;

            if (!config.Save())
            {
                AppStatusService.SetStatus("Settings: failed to save media preferences");
                return;
            }

            AppConfigChangedService.NotifyChanged(config);
            App.MainWindowInstance?.RefreshFooter();
            AppStatusService.SetStatus("Settings: media preferences updated");
        }

        private void ReloadButton_Click(object sender, RoutedEventArgs e)
        {
            LoadSettings();
        }

        private static string BuildFolderSummary(string? path, string fallback)
        {
            if (string.IsNullOrWhiteSpace(path))
            {
                return fallback;
            }

            string trimmed = path.TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar);
            string name = Path.GetFileName(trimmed);
            return string.IsNullOrWhiteSpace(name) ? fallback : name;
        }
    }
}
