using System;
using System.IO;
using System.Linq;
using System.Windows;
using System.Windows.Controls;

namespace Onslaught___Career_Editor.Views
{
    /// <summary>
    /// Settings tab - configures game directory and app preferences.
    /// </summary>
    public partial class SettingsView : UserControl
    {
        private bool _isLoadingSettings;

        public SettingsView()
        {
            InitializeComponent();
            LoadSettings();
        }

        private void LoadSettings()
        {
            _isLoadingSettings = true;
            var config = AppConfig.Load();
            string? gameDir = config.GetGameDir();

            if (!string.IsNullOrEmpty(gameDir))
            {
                GameDirTextBox.Text = gameDir;
                ValidateGameDir(gameDir);
            }
            else
            {
                GameDirStatus.Text = "No game directory set. Click Browse or Auto-Detect.";
            }

            UpdateSaveFileInfo();
            ConfigPathTextBlock.Text = $"Config file: {AppConfig.GetConfigPath()}";

            AllowBackgroundAudioCheckBox.IsChecked = config.AllowBackgroundAudio;
            AllowBackgroundVideoCheckBox.IsChecked = config.AllowBackgroundVideo;
            PreventAudioVideoOverlapCheckBox.IsChecked = config.PreventAudioVideoOverlap;
            _isLoadingSettings = false;
        }

        private void BrowseGameDir_Click(object sender, RoutedEventArgs e)
        {
            var dialog = new System.Windows.Forms.FolderBrowserDialog
            {
                Description = "Select Battle Engine Aquila game directory",
                ShowNewFolderButton = false
            };

            if (!string.IsNullOrEmpty(GameDirTextBox.Text) && Directory.Exists(GameDirTextBox.Text))
            {
                dialog.SelectedPath = GameDirTextBox.Text;
            }

            if (dialog.ShowDialog() == System.Windows.Forms.DialogResult.OK)
            {
                SetGameDir(dialog.SelectedPath);
            }
        }

        private void AutoDetectGameDir_Click(object sender, RoutedEventArgs e)
        {
            string? detected = AppConfig.DetectGameDirectory();
            if (!string.IsNullOrEmpty(detected))
            {
                SetGameDir(detected);
                MainWindow.SetStatus("Game directory auto-detected!");
            }
            else
            {
                MainWindow.SetStatus("Could not auto-detect game directory. Please browse manually.");
            }
        }

        private void SetGameDir(string path)
        {
            GameDirTextBox.Text = path;
            if (!Directory.Exists(path))
            {
                ValidateGameDir(path);
                MainWindow.SetStatus("Game directory path is invalid");
                return;
            }

            var config = AppConfig.Load();
            if (!config.SetGameDir(path))
            {
                MainWindow.SetStatus("Failed to save game directory setting");
                return;
            }

            ValidateGameDir(path);
            UpdateSaveFileInfo();
            MainWindow.RefreshFooter();
            MainWindow.SetStatus("Game directory updated");
        }

        private void ValidateGameDir(string path)
        {
            if (!Directory.Exists(path))
            {
                GameDirStatus.Text = "Directory does not exist";
                GameDirStatus.Foreground = System.Windows.Media.Brushes.Red;
                return;
            }

            // Check for expected game files/folders
            bool hasData = Directory.Exists(Path.Combine(path, "data"));
            bool hasVideo = Directory.Exists(Path.Combine(path, "data", "video"));
            bool hasMusic = Directory.Exists(Path.Combine(path, "data", "Music"));
            bool hasExe = File.Exists(Path.Combine(path, "BEA.exe")) ||
                          File.Exists(Path.Combine(path, "bea.exe"));

            if (hasData && (hasVideo || hasMusic))
            {
                GameDirStatus.Text = $"Valid game directory detected";
                if (hasExe) GameDirStatus.Text += " (with executable)";
                GameDirStatus.Foreground = System.Windows.Media.Brushes.Green;
            }
            else
            {
                GameDirStatus.Text = "Warning: This doesn't look like a BEA installation (missing data folder)";
                GameDirStatus.Foreground = System.Windows.Media.Brushes.Orange;
            }
        }

        private void UpdateSaveFileInfo()
        {
            var config = AppConfig.Load();
            string? gameDir = config.GetGameDir();

            if (string.IsNullOrEmpty(gameDir))
            {
                SaveDirLabel.Text = "Game directory not configured";
                SaveFileCount.Text = "";
                MainWindow.SetStatus("Set game directory to enable save file detection");
                return;
            }

            // Use centralized save file finder
            var saves = AppConfig.FindSaveFiles(gameDir);

            if (saves.Count > 0)
            {
                // Show the directory of the first save found
                string? firstDir = Path.GetDirectoryName(saves[0].Path);
                SaveDirLabel.Text = firstDir ?? "Unknown";
                SaveFileCount.Text = $"Found {saves.Count} save/options file(s)";
                MainWindow.SetStatus($"Found {saves.Count} save/options file(s)");
            }
            else
            {
                SaveDirLabel.Text = "No save/options files found";
                SaveFileCount.Text = "Create a save/options file in-game first, or check game directory";
                MainWindow.SetStatus("No save/options files found");
            }
        }

        private void MediaPreferenceChanged(object sender, RoutedEventArgs e)
        {
            if (_isLoadingSettings)
                return;

            var config = AppConfig.Load();
            config.AllowBackgroundAudio = AllowBackgroundAudioCheckBox.IsChecked == true;
            config.AllowBackgroundVideo = AllowBackgroundVideoCheckBox.IsChecked == true;
            config.PreventAudioVideoOverlap = PreventAudioVideoOverlapCheckBox.IsChecked == true;
            config.Save();
            if (Window.GetWindow(this) is MainWindow mainWindow)
            {
                mainWindow.ApplyMediaPolicyNow();
            }
            MainWindow.SetStatus("Media playback preferences updated");
        }
    }
}
