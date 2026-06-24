using System;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Threading;
using Onslaught___Career_Editor.Views;

namespace Onslaught___Career_Editor
{
    /// <summary>
    /// Main window with tabbed interface for Onslaught Toolkit.
    /// </summary>
    public partial class MainWindow : Window
    {
        private static MainWindow? _instance;

        public MainWindow()
        {
            InitializeComponent();
            _instance = this;

            var config = AppConfig.Load();

            // Restore window dimensions if saved
            if (config.WindowWidth > 0 && config.WindowHeight > 0)
            {
                Width = config.WindowWidth;
                Height = config.WindowHeight;
            }

            // Restore last tab from config
            if (config.LastTab >= 0 && config.LastTab < MainTabControl.Items.Count)
            {
                MainTabControl.SelectedIndex = config.LastTab;
            }

            if (config.LastSaveSubTab >= 0 && config.LastSaveSubTab < SavesTabControl.Items.Count)
            {
                SavesTabControl.SelectedIndex = config.LastSaveSubTab;
            }

            if (config.LastMediaSubTab >= 0 && config.LastMediaSubTab < MediaTabControl.Items.Count)
            {
                MediaTabControl.SelectedIndex = config.LastMediaSubTab;
            }

            UpdateFooter();

            // Trigger lazy loading for the initial tab after layout completes
            Dispatcher.BeginInvoke(() =>
            {
                if (MainTabControl.SelectedItem is TabItem tab)
                {
                    EnsureTabContentLoaded(tab.Content);
                    SetStatus(GetActiveTabStatusText());
                }
            }, DispatcherPriority.Loaded);
        }

        /// <summary>
        /// Set the status message in the footer from anywhere in the app
        /// </summary>
        public static void SetStatus(string message)
        {
            _instance?.Dispatcher.Invoke(() =>
            {
                if (_instance != null)
                {
                    _instance.StatusLabel.Text = message;
                }
            });
        }

        /// <summary>
        /// Refresh the footer (e.g. after settings change)
        /// </summary>
        public static void RefreshFooter()
        {
            _instance?.Dispatcher.Invoke(() =>
            {
                _instance?.UpdateFooter();
            });
        }

        private void UpdateFooter()
        {
            var config = AppConfig.Load();
            string? gameDir = config.GetGameDir();

            if (!string.IsNullOrEmpty(gameDir))
            {
                GameDirLabel.Text = NormalizeGameDirLabel(gameDir);
            }
            else
            {
                GameDirLabel.Text = "Not set - configure in Settings";
            }
        }

        private static string NormalizeGameDirLabel(string rawValue)
        {
            string value = rawValue.Trim();
            while (value.StartsWith("Game:", StringComparison.OrdinalIgnoreCase))
            {
                value = value[5..].Trim();
            }

            return value;
        }

        private void MainTabControl_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            // Only handle if this is the main tab control (not nested tab changes)
            if (e.Source == MainTabControl)
            {
                // Save selected tab to config
                var config = AppConfig.Load();
                config.LastTab = MainTabControl.SelectedIndex;
                config.Save();

                // Update footer status based on current tab
                if (MainTabControl.SelectedItem is TabItem tab)
                {
                    SetStatus(GetActiveTabStatusText());
                    EnsureTabContentLoaded(tab.Content);
                    ApplyMediaPolicyForMainTab(tab);
                }
            }
        }

        private void NestedTabControl_SelectionChanged(object sender, SelectionChangedEventArgs e)
        {
            if (e.Source is TabControl nestedControl && nestedControl.SelectedItem is TabItem tab)
            {
                var config = AppConfig.Load();
                if (nestedControl == SavesTabControl)
                {
                    config.LastSaveSubTab = SavesTabControl.SelectedIndex;
                }
                else if (nestedControl == MediaTabControl)
                {
                    config.LastMediaSubTab = MediaTabControl.SelectedIndex;
                }
                config.Save();

                EnsureTabContentLoaded(tab.Content);
                SetStatus(GetActiveTabStatusText());
                if (nestedControl == MediaTabControl)
                {
                    ApplyMediaPolicyForMediaSubTab(tab);
                }
            }
        }

        private string GetActiveTabStatusText()
        {
            if (MainTabControl.SelectedItem is not TabItem mainTab)
                return "Ready";

            string mainHeader = mainTab.Header?.ToString() ?? "Unknown";
            if (mainTab.Content is TabControl nested && nested.SelectedItem is TabItem nestedTab)
            {
                string nestedHeader = nestedTab.Header?.ToString() ?? "Unknown";
                return $"{nestedHeader} ready";
            }

            return $"{mainHeader} ready";
        }

        public void HandleMediaPlaybackStarted(MediaPlaybackKind kind)
        {
            var config = AppConfig.Load();
            if (!config.PreventAudioVideoOverlap)
                return;

            if (kind == MediaPlaybackKind.Audio)
            {
                VideoPlayerViewControl?.StopPlayback();
            }
            else
            {
                AudioPlayerViewControl?.StopPlayback();
            }
        }

        public void ApplyMediaPolicyNow()
        {
            if (MainTabControl.SelectedItem is TabItem mainTab)
            {
                ApplyMediaPolicyForMainTab(mainTab);
            }

            if (MediaTabControl.SelectedItem is TabItem mediaTab)
            {
                ApplyMediaPolicyForMediaSubTab(mediaTab);
            }

            var config = AppConfig.Load();
            if (config.PreventAudioVideoOverlap &&
                AudioPlayerViewControl?.IsPlaying == true &&
                VideoPlayerViewControl?.IsPlaying == true)
            {
                VideoPlayerViewControl.StopPlayback();
            }
        }

        private void ApplyMediaPolicyForMainTab(TabItem tab)
        {
            var config = AppConfig.Load();
            string header = tab.Header?.ToString() ?? "";
            if (!string.Equals(header, "Media", StringComparison.OrdinalIgnoreCase))
            {
                if (!config.AllowBackgroundAudio)
                    AudioPlayerViewControl?.StopPlayback();
                if (!config.AllowBackgroundVideo)
                    VideoPlayerViewControl?.StopPlayback();
            }
        }

        private void ApplyMediaPolicyForMediaSubTab(TabItem tab)
        {
            var config = AppConfig.Load();
            string header = tab.Header?.ToString() ?? "";

            if (!config.AllowBackgroundAudio && !string.Equals(header, "Audio Player", StringComparison.OrdinalIgnoreCase))
                AudioPlayerViewControl?.StopPlayback();

            if (!config.AllowBackgroundVideo && !string.Equals(header, "Video Player", StringComparison.OrdinalIgnoreCase))
                VideoPlayerViewControl?.StopPlayback();
        }

        private static void EnsureTabContentLoaded(object? content)
        {
            if (content is ILazyLoadView lazy)
            {
                lazy.EnsureLoaded();
                return;
            }

            if (content is TabControl nestedControl && nestedControl.SelectedItem is TabItem nestedTab)
            {
                EnsureTabContentLoaded(nestedTab.Content);
            }
        }

        private void Window_Closing(object sender, System.ComponentModel.CancelEventArgs e)
        {
            // Save window state
            var config = AppConfig.Load();
            config.WindowWidth = (int)ActualWidth;
            config.WindowHeight = (int)ActualHeight;
            config.Save();

            AudioPlayerViewControl?.StopPlayback();
            VideoPlayerViewControl?.DisposePlayer();
        }
    }
}
