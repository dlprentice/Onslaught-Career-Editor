using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Threading;
using LibVLCSharp.Shared;

namespace Onslaught___Career_Editor.Views
{
    /// <summary>
    /// Video Player tab - plays game cutscenes and briefings.
    /// Uses LibVLC for native Bink video playback (no conversion needed).
    /// </summary>
    public partial class VideoPlayerView : UserControl, ILazyLoadView
    {
        private LibVLC? _libVLC;
        private MediaPlayer? _mediaPlayer;
        private DispatcherTimer? _positionTimer;
        private bool _isDraggingSlider;
        private bool _isUpdatingSliderFromTimer;
        private List<VideoFileItem> _allVideoFiles = new();
        private VideoFileItem? _currentFile;
        private bool _hasLoaded;
        private bool _isLoading;
        private CancellationTokenSource? _loadCts;

        // Cutscene names for human-readable display
        private static readonly Dictionary<string, string> CutsceneNames = new()
        {
            { "01", "Intro - Forseti Invasion" },
            { "02", "Mission Briefing 1" },
            { "03", "Battle Aftermath" },
            { "04", "Tatiana Introduction" },
            { "05", "Muspell Attack" },
            { "06", "Base Defense" },
            { "07", "Rescue Mission" },
            { "08", "Enemy Revealed" },
            { "09", "Counter Attack" },
            { "10", "Naval Battle" },
            { "11", "Air Support" },
            { "12", "Ground Assault" },
            { "13", "Enemy Base" },
            { "14", "Infiltration" },
            { "15", "Boss Battle" },
            { "16", "Victory" },
            { "17", "Plot Twist" },
            { "18", "New Orders" },
            { "19", "Allied Forces" },
            { "20", "Major Offensive" },
            { "21", "Desperate Times" },
            { "22", "Last Stand" },
            { "23", "Final Push" },
            { "24", "Enemy HQ" },
            { "25", "Confrontation" },
            { "26", "Sacrifice" },
            { "27", "Turning Point" },
            { "28", "Rally" },
            { "29", "Final Battle Prep" },
            { "30", "The End Begins" },
            { "31", "Ultimate Weapon" },
            { "32", "Climax" },
            { "33", "Ending/Credits" },
        };

        public VideoPlayerView()
        {
            InitializeComponent();
            UpdateVideoEmptyState();
            IsVisibleChanged += (_, _) =>
            {
                if (IsVisible)
                {
                    EnsureLoaded();
                }
            };
        }

        private void UserControl_Loaded(object sender, RoutedEventArgs e)
        {
            if (IsVisible)
            {
                EnsureLoaded();
            }
        }

        private void UserControl_Unloaded(object sender, RoutedEventArgs e)
        {
            var config = AppConfig.Load();
            if (config.AllowBackgroundVideo)
            {
                return;
            }

            // Clean up resources safely
            try
            {
                DisposePlayer();
            }
            catch
            {
                // Ignore cleanup errors
            }
        }

        // Friendly names for known main videos
        private static readonly Dictionary<string, string> MainVideoDescriptions = new()
        {
            { "OpeningFMV", "Opening Cinematic" },
            { "UsTheMovie", "Credits Video" },
            { "LTLogo", "Lost Toys Logo" },
            { "FEBack128", "Menu Background" },
            { "TWIMTBP_GefFX_640x480_Audio", "NVIDIA Logo" },
            { "gill_m_on_a_fork", "Easter Egg: Gill on a Fork!" },
        };

        public void EnsureLoaded()
        {
            if (_hasLoaded || _isLoading)
            {
                return;
            }

            if (!InitializePlayer())
            {
                return;
            }

            var config = AppConfig.Load();
            string? gameDir = config.GetGameDir() ?? AppConfig.DetectGameDirectory();
            if (string.IsNullOrEmpty(gameDir))
            {
                MainWindow.SetStatus("Video Player: Game directory not set");
                return;
            }

            if (string.IsNullOrEmpty(config.GetGameDir()))
            {
                config.SetGameDir(gameDir);
            }

            GameDirTextBox.Text = gameDir;
            LoadVideoFilesAsync(gameDir);
        }

        private bool InitializePlayer()
        {
            if (_libVLC != null && _mediaPlayer != null)
            {
                return true;
            }

            try
            {
                // Initialize LibVLC with options to handle Bink video quirks
                Core.Initialize();
                _libVLC = new LibVLC(
                    "--avcodec-hw=none",            // Software decoding - more reliable for Bink
                    "--no-video-title-show",        // Don't overlay filename on video
                    "--file-caching=1000",          // Buffer for smoother playback
                    "--no-embedded-video",          // Disable taskbar thumbnail (fixes SetThumbNailClip error)
                    "--verbose=-1"                  // Suppress non-critical warnings
                );
                _mediaPlayer = new MediaPlayer(_libVLC);

                // Attach to VideoView
                VideoView.MediaPlayer = _mediaPlayer;

                // Set up event handlers
                _mediaPlayer.Playing += MediaPlayer_Playing;
                _mediaPlayer.Paused += MediaPlayer_Paused;
                _mediaPlayer.Stopped += MediaPlayer_Stopped;
                _mediaPlayer.EndReached += MediaPlayer_EndReached;
                _mediaPlayer.LengthChanged += MediaPlayer_LengthChanged;
                _mediaPlayer.EncounteredError += MediaPlayer_EncounteredError;

                // Set up position timer
                _positionTimer = new DispatcherTimer
                {
                    Interval = TimeSpan.FromMilliseconds(250)
                };
                _positionTimer.Tick += PositionTimer_Tick;

                // Initialize volume
                _mediaPlayer.Volume = (int)VolumeSlider.Value;

                return true;
            }
            catch (Exception ex)
            {
                MainWindow.SetStatus($"VLC initialization error: {ex.Message}");
                MessageBox.Show(
                    $"VLC initialization error:\n{ex.Message}\n\n" +
                    "Try rebuilding the app to restore LibVLC runtime files.",
                    "Video Player Error",
                    MessageBoxButton.OK,
                    MessageBoxImage.Error);
                return false;
            }
        }

        private void LoadVideoFilesAsync(string gameDir)
        {
            _loadCts?.Cancel();
            _loadCts = new CancellationTokenSource();
            var token = _loadCts.Token;

            _isLoading = true;
            MainWindow.SetStatus("Video Player: Loading video files...");

            Task.Run(() => BuildVideoCategories(gameDir, token), token)
                .ContinueWith(task =>
                {
                    _isLoading = false;

                    if (task.IsCanceled)
                    {
                        return;
                    }

                    if (task.Exception != null)
                    {
                        Dispatcher.Invoke(() => MainWindow.SetStatus("Video Player: Failed to load videos"));
                        return;
                    }

                    var result = task.Result;
                    Dispatcher.Invoke(() =>
                    {
                        _allVideoFiles = result.Files;
                        VideoTree.ItemsSource = result.Categories;
                        if (_currentFile != null && !_allVideoFiles.Any(f => string.Equals(f.FilePath, _currentFile.FilePath, StringComparison.OrdinalIgnoreCase)))
                        {
                            _currentFile = null;
                        }
                        if (_currentFile == null)
                        {
                            VideoTitleLabel.Text = "No video selected";
                            VideoPathLabel.Text = string.Empty;
                            PlayButton.IsEnabled = false;
                        }
                        UpdateVideoEmptyState();
                        _hasLoaded = true;
                        MainWindow.SetStatus($"Video Player: Loaded {_allVideoFiles.Count} video(s)");
                    });
                }, TaskScheduler.Default);
        }

        private VideoLoadResult BuildVideoCategories(string gameDir, CancellationToken token)
        {
            var categories = new List<VideoCategory>();
            var allFiles = new List<VideoFileItem>();

            // Track already-added file paths to prevent duplicates (case-insensitive)
            var addedPaths = new HashSet<string>(StringComparer.OrdinalIgnoreCase);

            string videoDir = Path.Combine(gameDir, "data", "video");
            if (!Directory.Exists(videoDir))
            {
                return new VideoLoadResult(categories, allFiles);
            }

            // === Main Videos (ALL .vid files in root, excluding numbered cutscenes) ===
            var mainVideos = new VideoCategory { Name = "Main Videos" };
            foreach (string file in Directory.GetFiles(videoDir, "*.vid").OrderBy(f => f))
            {
                token.ThrowIfCancellationRequested();
                string baseName = Path.GetFileNameWithoutExtension(file);

                // Skip numbered cutscenes (they go in Cutscenes category)
                if (baseName.Length == 2 && int.TryParse(baseName, out _))
                    continue;

                // Skip briefings (they go in Briefings category)
                if (baseName.StartsWith("PC_") && baseName.EndsWith("_exact"))
                    continue;

                if (addedPaths.Add(file))
                {
                    string displayName = MainVideoDescriptions.GetValueOrDefault(baseName, baseName);
                    var item = CreateVideoItem(file, displayName);
                    mainVideos.Children.Add(item);
                    allFiles.Add(item);
                }
            }
            if (mainVideos.Children.Count > 0)
                categories.Add(mainVideos);

            // === Cutscenes - Check both root AND cutscenes/ subdirectory ===
            var cutscenes = new VideoCategory { Name = "Cutscenes" };

            // First check cutscenes/ subdirectory (Python's location)
            string cutsceneDir = Path.Combine(videoDir, "cutscenes");
            if (Directory.Exists(cutsceneDir))
            {
                foreach (string file in Directory.GetFiles(cutsceneDir, "*.vid")
                    .OrderBy(f =>
                    {
                        string stem = Path.GetFileNameWithoutExtension(f);
                        return int.TryParse(stem, out int num) ? num : 999;
                    }))
                {
                    token.ThrowIfCancellationRequested();
                    if (addedPaths.Add(file))
                    {
                        string num = Path.GetFileNameWithoutExtension(file);
                        string displayName = CutsceneNames.GetValueOrDefault(num, $"Cutscene {num}");
                        var item = CreateVideoItem(file, $"{num} - {displayName}");
                        cutscenes.Children.Add(item);
                        allFiles.Add(item);
                    }
                }
            }

            // Also check root directory for numbered cutscenes (fallback)
            foreach (string file in Directory.GetFiles(videoDir, "*.vid")
                .Where(f => {
                    string stem = Path.GetFileNameWithoutExtension(f);
                    return stem.Length == 2 && int.TryParse(stem, out _);
                })
                .OrderBy(f => int.Parse(Path.GetFileNameWithoutExtension(f))))
            {
                token.ThrowIfCancellationRequested();
                if (addedPaths.Add(file))
                {
                    string num = Path.GetFileNameWithoutExtension(file);
                    string displayName = CutsceneNames.GetValueOrDefault(num, $"Cutscene {num}");
                    var item = CreateVideoItem(file, $"{num} - {displayName}");
                    cutscenes.Children.Add(item);
                    allFiles.Add(item);
                }
            }

            if (cutscenes.Children.Count > 0)
                categories.Add(cutscenes);

            // === Briefings - Check both root AND briefings/ subdirectory, grouped by Episode ===
            var briefings = new VideoCategory { Name = "Mission Briefings" };
            var briefingsByEpisode = new Dictionary<string, List<(string file, string missionNum)>>();

            // Helper to process briefing files (with duplicate prevention)
            void ProcessBriefingFiles(IEnumerable<string> files)
            {
                foreach (string file in files)
                {
                    token.ThrowIfCancellationRequested();
                    // Skip if already added
                    if (!addedPaths.Add(file))
                        continue;

                    string fileName = Path.GetFileNameWithoutExtension(file);
                    if (!fileName.StartsWith("PC_") || !fileName.EndsWith("_exact"))
                    {
                        // Remove from addedPaths since we're not actually using this file
                        addedPaths.Remove(file);
                        continue;
                    }

                    string missionNum = fileName.Replace("PC_", "").Replace("_exact", "");
                    string episode = missionNum.Length > 0 ? missionNum[0].ToString() : "?";

                    if (!briefingsByEpisode.ContainsKey(episode))
                        briefingsByEpisode[episode] = new();
                    briefingsByEpisode[episode].Add((file, missionNum));
                }
            }

            // Check briefings/ subdirectory first (Python's location)
            string briefingDir = Path.Combine(videoDir, "briefings");
            if (Directory.Exists(briefingDir))
            {
                ProcessBriefingFiles(Directory.GetFiles(briefingDir, "*.vid"));
            }

            // Also check root directory (fallback)
            ProcessBriefingFiles(Directory.GetFiles(videoDir, "PC_*_exact.vid"));

            // Create episode sub-categories
            foreach (var episode in briefingsByEpisode.Keys.OrderBy(e => e))
            {
                token.ThrowIfCancellationRequested();
                var episodeCategory = new VideoCategory { Name = $"Episode {episode}" };
                foreach (var (file, missionNum) in briefingsByEpisode[episode].OrderBy(b => b.missionNum))
                {
                    token.ThrowIfCancellationRequested();
                    var item = CreateVideoItem(file, $"Mission {missionNum}");
                    episodeCategory.Children.Add(item);
                    allFiles.Add(item);
                }
                briefings.Children.Add(episodeCategory);
            }

            if (briefings.Children.Count > 0)
                categories.Add(briefings);

            return new VideoLoadResult(categories, allFiles);
        }

        private VideoFileItem CreateVideoItem(string filePath, string displayName)
        {
            var info = new FileInfo(filePath);
            return new VideoFileItem
            {
                Name = displayName,
                FilePath = filePath,
                SizeText = FormatFileSize(info.Length)
            };
        }

        private void VideoTree_SelectedItemChanged(object sender, RoutedPropertyChangedEventArgs<object> e)
        {
            if (e.NewValue is VideoFileItem item)
            {
                _currentFile = item;
                VideoTitleLabel.Text = item.Name;
                VideoPathLabel.Text = item.FilePath;
                PlayButton.IsEnabled = true;
                UpdateVideoEmptyState();
                MainWindow.SetStatus($"Video Player: Selected {item.Name}");
            }
            else
            {
                _currentFile = null;
                VideoTitleLabel.Text = "No video selected";
                VideoPathLabel.Text = string.Empty;
                PlayButton.IsEnabled = false;
                UpdateVideoEmptyState();
            }
        }

        private void VideoTree_MouseDoubleClick(object sender, System.Windows.Input.MouseButtonEventArgs e)
        {
            // Double-click to play - only if a video file is selected (not a category)
            if (VideoTree.SelectedItem is VideoFileItem)
            {
                PlayButton_Click(sender, e);
            }
        }

        private void PlayButton_Click(object sender, RoutedEventArgs e)
        {
            if (_currentFile == null)
                return;

            if (!_hasLoaded)
            {
                EnsureLoaded();
            }

            if (_mediaPlayer == null || _libVLC == null)
            {
                if (!InitializePlayer())
                {
                    MainWindow.SetStatus("Video Player: Cannot play - player not initialized");
                    return;
                }
            }

            StopPlayback();

            try
            {
                var libVlc = _libVLC!;
                var player = _mediaPlayer!;
                using var media = new Media(libVlc, new Uri(_currentFile.FilePath));
                player.Play(media);
                UpdateVideoEmptyState();
                MainWindow.SetStatus($"Video Player: Playing {_currentFile.Name}");
                NotifyPlaybackStarted();
            }
            catch (Exception ex)
            {
                MainWindow.SetStatus($"Video Player: Playback error - {ex.Message}");
            }
        }

        private void PauseButton_Click(object sender, RoutedEventArgs e)
        {
            if (_mediaPlayer == null) return;

            if (_mediaPlayer.IsPlaying)
            {
                _mediaPlayer.Pause();
            }
            else
            {
                _mediaPlayer.Play();
                NotifyPlaybackStarted();
            }
        }

        private void StopButton_Click(object sender, RoutedEventArgs e)
        {
            StopPlayback();
            MainWindow.SetStatus("Video Player: Stopped");
        }

        /// <summary>
        /// Stops playback and resets UI state. Can be called publicly when switching tabs.
        /// </summary>
        public void StopPlayback()
        {
            _positionTimer?.Stop();
            _mediaPlayer?.Stop();

            PlayButton.IsEnabled = _currentFile != null;
            PauseButton.IsEnabled = false;
            PauseButton.Content = "Pause";
            StopButton.IsEnabled = false;
            ProgressSlider.IsEnabled = false;
            ProgressSlider.Value = 0;
            CurrentTimeLabel.Text = "0:00";
            UpdateVideoEmptyState();
        }

        public bool IsPlaying => _mediaPlayer?.IsPlaying == true;

        public void DisposePlayer()
        {
            StopPlayback();
            _positionTimer?.Stop();

            if (_mediaPlayer != null)
            {
                VideoView.MediaPlayer = null; // Detach before disposing
                _mediaPlayer.Dispose();
                _mediaPlayer = null;
            }

            _libVLC?.Dispose();
            _libVLC = null;
            _hasLoaded = false;
        }

        private void NotifyPlaybackStarted()
        {
            if (Window.GetWindow(this) is MainWindow mainWindow)
            {
                mainWindow.HandleMediaPlaybackStarted(MediaPlaybackKind.Video);
            }
        }

        private void MediaPlayer_Playing(object? sender, EventArgs e)
        {
            // Use BeginInvoke to avoid potential deadlocks with VLC callbacks
            Dispatcher.BeginInvoke(() =>
            {
                PlayButton.IsEnabled = false;
                PauseButton.IsEnabled = true;
                PauseButton.Content = "Pause";
                StopButton.IsEnabled = true;
                ProgressSlider.IsEnabled = true;
                _positionTimer?.Start();
            });
        }

        private void MediaPlayer_Paused(object? sender, EventArgs e)
        {
            Dispatcher.BeginInvoke(() =>
            {
                _positionTimer?.Stop();
                PauseButton.Content = "Resume";
                MainWindow.SetStatus("Video Player: Paused");
            });
        }

        private void MediaPlayer_Stopped(object? sender, EventArgs e)
        {
            Dispatcher.BeginInvoke(() =>
            {
                _positionTimer?.Stop();
                PlayButton.IsEnabled = _currentFile != null;
                PauseButton.IsEnabled = false;
                PauseButton.Content = "Pause";
                StopButton.IsEnabled = false;
            });
        }

        private void MediaPlayer_EndReached(object? sender, EventArgs e)
        {
            // MUST use BeginInvoke (async) - using Invoke causes deadlock!
            // VLC callbacks block if we synchronously wait for UI thread
            Dispatcher.BeginInvoke(() =>
            {
                StopPlayback();
                MainWindow.SetStatus("Video Player: Playback finished");
            });
        }

        private void MediaPlayer_LengthChanged(object? sender, MediaPlayerLengthChangedEventArgs e)
        {
            Dispatcher.BeginInvoke(() =>
            {
                ProgressSlider.Maximum = e.Length / 1000.0; // Convert ms to seconds
                TotalTimeLabel.Text = FormatTime(TimeSpan.FromMilliseconds(e.Length));
            });
        }

        private void MediaPlayer_EncounteredError(object? sender, EventArgs e)
        {
            Dispatcher.BeginInvoke(() =>
            {
                MainWindow.SetStatus("Video Player: Playback error occurred");
            });
        }

        private void PositionTimer_Tick(object? sender, EventArgs e)
        {
            if (_mediaPlayer != null && !_isDraggingSlider && _mediaPlayer.IsPlaying)
            {
                _isUpdatingSliderFromTimer = true;
                try
                {
                    var position = _mediaPlayer.Time / 1000.0; // Convert ms to seconds
                    ProgressSlider.Value = position;
                    CurrentTimeLabel.Text = FormatTime(TimeSpan.FromMilliseconds(_mediaPlayer.Time));
                }
                finally
                {
                    _isUpdatingSliderFromTimer = false;
                }
            }
        }

        private void ProgressSlider_PreviewMouseDown(object sender, System.Windows.Input.MouseButtonEventArgs e)
        {
            _isDraggingSlider = true;
        }

        private void ProgressSlider_PreviewMouseUp(object sender, System.Windows.Input.MouseButtonEventArgs e)
        {
            _isDraggingSlider = false;
            if (_mediaPlayer != null)
            {
                _mediaPlayer.Time = (long)(ProgressSlider.Value * 1000); // Convert seconds to ms
            }
        }

        private void ProgressSlider_ValueChanged(object sender, RoutedPropertyChangedEventArgs<double> e)
        {
            if (_isDraggingSlider)
            {
                CurrentTimeLabel.Text = FormatTime(TimeSpan.FromSeconds(ProgressSlider.Value));
            }
            // Handle keyboard navigation (arrow keys, Page Up/Down, Home/End)
            // If value changed but not from mouse drag and not from timer update, it's keyboard input
            else if (!_isUpdatingSliderFromTimer && _mediaPlayer != null && ProgressSlider.IsEnabled)
            {
                CurrentTimeLabel.Text = FormatTime(TimeSpan.FromSeconds(ProgressSlider.Value));
                _mediaPlayer.Time = (long)(ProgressSlider.Value * 1000); // Convert seconds to ms
            }
        }

        private void VolumeSlider_ValueChanged(object sender, RoutedPropertyChangedEventArgs<double> e)
        {
            if (VideoVolumeLabel != null)
            {
                VideoVolumeLabel.Text = $"{(int)VolumeSlider.Value}%";
            }

            // Guard against event firing during XAML initialization
            if (_mediaPlayer == null) return;

            _mediaPlayer.Volume = (int)VolumeSlider.Value;
        }

        private void SearchTextBox_TextChanged(object sender, TextChangedEventArgs e)
        {
            string query = SearchTextBox.Text.Trim().ToLower();

            if (string.IsNullOrEmpty(query))
            {
                string? gameDir = GameDirTextBox.Text;
                if (!string.IsNullOrEmpty(gameDir))
                    LoadVideoFilesAsync(gameDir);
                return;
            }

            var filtered = _allVideoFiles.Where(f => f.Name.ToLower().Contains(query)).ToList();
            var category = new VideoCategory { Name = $"Search Results ({filtered.Count})" };
            category.Children.AddRange(filtered.Cast<object>());

            VideoTree.ItemsSource = new[] { category };
            MainWindow.SetStatus($"Video Player: Found {filtered.Count} video(s)");
        }

        private void BrowseGameDir_Click(object sender, RoutedEventArgs e)
        {
            var dialog = new System.Windows.Forms.FolderBrowserDialog
            {
                Description = "Select Battle Engine Aquila game directory",
                ShowNewFolderButton = false
            };

            if (dialog.ShowDialog() == System.Windows.Forms.DialogResult.OK)
            {
                GameDirTextBox.Text = dialog.SelectedPath;
                var config = AppConfig.Load();
                config.SetGameDir(dialog.SelectedPath);
                LoadVideoFilesAsync(dialog.SelectedPath);
            }
        }

        private void ReloadVideo_Click(object sender, RoutedEventArgs e)
        {
            string? gameDir = GameDirTextBox.Text;
            if (!string.IsNullOrEmpty(gameDir) && Directory.Exists(gameDir))
            {
                LoadVideoFilesAsync(gameDir);
            }
        }

        private void UpdateVideoEmptyState()
        {
            if (VideoEmptyStateOverlay == null || VideoEmptyStateText == null)
            {
                return;
            }

            if (_currentFile == null)
            {
                VideoEmptyStateText.Text = "Select a video from the library.";
                VideoEmptyStateOverlay.Visibility = Visibility.Visible;
                return;
            }

            VideoEmptyStateOverlay.Visibility = Visibility.Collapsed;
        }

        private static string FormatTime(TimeSpan time)
        {
            return $"{(int)time.TotalMinutes}:{time.Seconds:D2}";
        }

        private static string FormatFileSize(long bytes)
        {
            if (bytes < 1024) return $"{bytes} B";
            if (bytes < 1024 * 1024) return $"{bytes / 1024.0:F1} KB";
            return $"{bytes / (1024.0 * 1024.0):F1} MB";
        }
    }

    /// <summary>
    /// Represents a video file.
    /// </summary>
    public class VideoFileItem
    {
        public string Name { get; set; } = "";
        public string FilePath { get; set; } = "";
        public string SizeText { get; set; } = "";
    }

    /// <summary>
    /// Represents a category in the video tree.
    /// </summary>
    public class VideoCategory
    {
        public string Name { get; set; } = "";
        public List<object> Children { get; set; } = new();
    }

    internal sealed record VideoLoadResult(List<VideoCategory> Categories, List<VideoFileItem> Files);
}
