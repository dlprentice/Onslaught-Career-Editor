using System.IO;
using Microsoft.UI.Xaml;
using Microsoft.UI.Xaml.Controls;
using OnslaughtCareerEditor.WinUI.Helpers;
using OnslaughtCareerEditor.AppCore;

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
                ClearGameDirectoryIdentity();
                GameDirectoryStatusTextBlock.Text = "No game directory set. Click Browse or Auto-Detect.";
                GameDirectoryStatusTextBlock.Foreground = ThemeBrushes.Warning();
            }

            SelectThemeChoice(AppThemePreference.Normalize(config.AppTheme));
            AllowBackgroundAudioToggle.IsOn = config.AllowBackgroundAudio;
            AllowBackgroundVideoToggle.IsOn = config.AllowBackgroundVideo;
            PreventOverlapToggle.IsOn = config.PreventAudioVideoOverlap;
            AppearancePersistStatusTextBlock.Visibility = Visibility.Collapsed;
            MediaPersistStatusTextBlock.Visibility = Visibility.Collapsed;

            UpdateSaveFileInfo(gameDir);
            ConfigPathTextBlock.Text = GameDirectoryIdentityText.BuildConfigPathSummary(AppConfig.GetConfigPath());

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
                ? "Choose your installed game folder. The app reads it to create playable copies, and only changes it if you ask it to."
                : isFullInstall
                    ? "Source material. Editing and patching work on copies unless you choose to patch this install in Windowed & Mods."
                    : "This saved folder is incomplete. Choose the full install before using automatic discovery, Media, or playable safe copies.";
        }

        private void ValidateGameDirectory(string path)
        {
            ClearGameDirectoryIdentity();

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
                RenderGameDirectoryIdentity(path);
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

        private void RenderGameDirectoryIdentity(string gameDirectory)
        {
            string? exePath = AppConfig.TryGetGameExecutablePath(gameDirectory);
            RetailExecutableIdentity identity = BinaryPatchEngine.IdentifyRetailExecutable(exePath);
            string line = GameDirectoryIdentityText.ForSettings(identity);
            GameDirectoryIdentityTextBlock.Text = line;
            GameDirectoryIdentityTextBlock.Visibility = string.IsNullOrWhiteSpace(line)
                ? Visibility.Collapsed
                : Visibility.Visible;
            GameDirectoryStatusTextBlock.Foreground = GameDirectoryIdentityText.IsWarning(identity)
                ? ThemeBrushes.Warning()
                : ThemeBrushes.Success();
            GameDirectoryIdentityTextBlock.Foreground = GameDirectoryStatusTextBlock.Foreground;
        }

        private void ClearGameDirectoryIdentity()
        {
            GameDirectoryIdentityTextBlock.Text = string.Empty;
            GameDirectoryIdentityTextBlock.Visibility = Visibility.Collapsed;
        }

        /// <summary>
        /// Persist failed after the chosen folder was already drawn. Put the
        /// kept folder back so the page matches what is still on disk.
        /// </summary>
        private void RestoreKeptGameDirectory()
        {
            string? kept = AppConfig.Load().GameDirectory;
            RenderGameDirectory(kept);
            if (!string.IsNullOrWhiteSpace(kept))
            {
                ValidateGameDirectory(kept);
                return;
            }

            ClearGameDirectoryIdentity();
            GameDirectoryStatusTextBlock.Text = "No game directory set. Click Browse or Auto-Detect.";
            GameDirectoryStatusTextBlock.Foreground = ThemeBrushes.Warning();
        }

        private void RestoreKeptAppearance()
        {
            AppConfig kept = AppConfig.Load();
            string preference = AppThemePreference.Normalize(kept.AppTheme);
            _isLoadingSettings = true;
            try
            {
                SelectThemeChoice(preference);
            }
            finally
            {
                _isLoadingSettings = false;
            }

            App.MainWindowInstance?.ApplyThemePreference(preference);
            AppearancePersistStatusTextBlock.Text = GameDirectoryIdentityText.AppearancePersistFailed;
            AppearancePersistStatusTextBlock.Foreground = ThemeBrushes.Warning();
            AppearancePersistStatusTextBlock.Visibility = Visibility.Visible;
        }

        private void RestoreKeptMediaPreferences()
        {
            AppConfig kept = AppConfig.Load();
            _isLoadingSettings = true;
            try
            {
                AllowBackgroundAudioToggle.IsOn = kept.AllowBackgroundAudio;
                AllowBackgroundVideoToggle.IsOn = kept.AllowBackgroundVideo;
                PreventOverlapToggle.IsOn = kept.PreventAudioVideoOverlap;
            }
            finally
            {
                _isLoadingSettings = false;
            }

            MediaPersistStatusTextBlock.Text = GameDirectoryIdentityText.MediaPersistFailed;
            MediaPersistStatusTextBlock.Foreground = ThemeBrushes.Warning();
            MediaPersistStatusTextBlock.Visibility = Visibility.Visible;
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
                GameDirectoryStatusTextBlock.Text = GameDirectoryIdentityText.AutoDetectFailed;
                GameDirectoryStatusTextBlock.Foreground = ThemeBrushes.Warning();
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
                RestoreKeptGameDirectory();
                GameDirectoryStatusTextBlock.Text = GameDirectoryIdentityText.PersistFailed;
                GameDirectoryStatusTextBlock.Foreground = ThemeBrushes.Warning();
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

        private void SelectThemeChoice(string preference)
        {
            foreach (object item in AppThemeComboBox.Items)
            {
                if (item is ComboBoxItem { Tag: string tag } &&
                    string.Equals(tag, preference, StringComparison.OrdinalIgnoreCase))
                {
                    AppThemeComboBox.SelectedItem = item;
                    return;
                }
            }

            AppThemeComboBox.SelectedIndex = 0;
        }

        private void AppThemeChanged(object sender, SelectionChangedEventArgs e)
        {
            if (_isLoadingSettings)
            {
                return;
            }

            string preference = AppThemeComboBox.SelectedItem is ComboBoxItem { Tag: string tag }
                ? AppThemePreference.Normalize(tag)
                : AppThemePreference.Default;

            // Apply first so the change is visible immediately, then persist.
            App.MainWindowInstance?.ApplyThemePreference(preference);

            AppConfig config = AppConfig.Load();
            config.AppTheme = preference;
            if (!config.Save())
            {
                RestoreKeptAppearance();
                AppStatusService.SetStatus("Settings: failed to save the appearance choice");
                return;
            }

            AppearancePersistStatusTextBlock.Visibility = Visibility.Collapsed;
            AppConfigChangedService.NotifyChanged(config);
            AppStatusService.SetStatus($"Settings: appearance set to {AppThemePreference.DescribeChoice(preference)}");
        }

        private void MediaPreferenceChanged(object sender, RoutedEventArgs e)
        {
            if (_isLoadingSettings)
            {
                return;
            }

            // Changing a media preference must only write media preferences.
            // This used to also rewrite config.GameDirectory from the
            // read-only display textbox, so an unrelated toggle could push a
            // stale path back over the configured one - or clear it outright
            // whenever the textbox happened to be blank. The loaded config
            // already carries the persisted folder; leave it alone.
            AppConfig config = AppConfig.Load();
            config.AllowBackgroundAudio = AllowBackgroundAudioToggle.IsOn;
            config.AllowBackgroundVideo = AllowBackgroundVideoToggle.IsOn;
            config.PreventAudioVideoOverlap = PreventOverlapToggle.IsOn;

            if (!config.Save())
            {
                RestoreKeptMediaPreferences();
                AppStatusService.SetStatus("Settings: failed to save media preferences");
                return;
            }

            MediaPersistStatusTextBlock.Visibility = Visibility.Collapsed;
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
